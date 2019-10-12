import json
import logging

from homeassistant.components.http import HomeAssistantView
from homeassistant.const import HTTP_BAD_REQUEST
from homeassistant.auth.const import ACCESS_TOKEN_EXPIRATION
import homeassistant.auth.models as models
from typing import Optional
from datetime import timedelta
from homeassistant.helpers.state import AsyncTrackStates

_LOGGER = logging.getLogger(__name__)

MAIN = 'miai'
DOMAIN = 'miai'
EXPIRE_HOURS = 168  # 7天过期
_hass = None


async def async_create_refresh_token(
        user: models.User, client_id: Optional[str] = None,
        client_name: Optional[str] = None,
        client_icon: Optional[str] = None,
        token_type: str = models.TOKEN_TYPE_NORMAL,
        access_token_expiration: timedelta = ACCESS_TOKEN_EXPIRATION) \
        -> models.RefreshToken:
    if access_token_expiration == ACCESS_TOKEN_EXPIRATION:
        access_token_expiration = timedelta(hours=EXPIRE_HOURS)
    _LOGGER.info('Access token expiration: %d hours', EXPIRE_HOURS)
    """Create a new token for a user."""
    kwargs = {
        'user': user,
        'client_id': client_id,
        'token_type': token_type,
        'access_token_expiration': access_token_expiration
    }  # type: Dict[str, Any]
    if client_name:
        kwargs['client_name'] = client_name
    if client_icon:
        kwargs['client_icon'] = client_icon

    refresh_token = models.RefreshToken(**kwargs)
    user.refresh_tokens[refresh_token.id] = refresh_token

    _hass.auth._store._async_schedule_save()
    return refresh_token


async def async_setup(hass, config):
    global _hass
    _hass = hass
    hass.auth._store.async_create_refresh_token = async_create_refresh_token
    hass.http.register_view(MiAiView)
    return True


class MiAiView(HomeAssistantView):
    """View to handle Configuration requests."""

    url = '/miai'
    name = 'miai'
    requires_auth = False

    async def post(self, request):
        """Update state of entity."""
        try:
            data = await request.json()
            from homeassistant.components.http import KEY_REAL_IP
            response = await handleRequest(data, str(request[KEY_REAL_IP]))
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
            response = makeResponse("主人，程序出错啦！")
        return self.json(response)


#
_appName = '我家'


def guessAction(entity_id, intent_name, query):
    if not entity_id.startswith('sensor') and not entity_id.startswith('binary_sensor') and not entity_id.startswith('device_tracker'):
        # 使用小米意图识别或做意图识别
        if intent_name == 'open' or query.startswith('打开') or query.startswith('开') or query.endswith('打开'):
            return '打开'
        elif intent_name == 'close' or query.startswith('关') or query.endswith('关掉') or query.endswith('关闭') or query.endswith('关上'):
            return '关闭'
    return '查询'


#
STATE_NAMES = {
    'on': '开启状态',
    'off': '关闭状态',

    'home': '在家',
    'not_home': '离家',

    'cool': '制冷模式',
    'heat': '制热模式',
    'auto': '自动模式',
    'dry': '除湿模式',
    'fan': '送风模式',

    'open': '打开状态',
    'opening': '正在打开',
    'closed': '闭合状态',
    'closing': '正在闭合',

    'unavailable': '不可用',
}

#


async def handleState(entity_id, state, action):
    cover = entity_id.startswith('cover') or entity_id == 'group.all_covers'
    domain = 'cover' if cover else 'homeassistant'
    #domain = entity_id[:entity_id.find('.')]
    if action == '打开':
        service = 'open_cover' if cover else 'turn_on'
    elif action == '关闭':
        service = 'close_cover' if cover else 'turn_off'
    else:
        return '为' + (STATE_NAMES[state] if state in STATE_NAMES else state)

    data = {'entity_id': entity_id}
    with AsyncTrackStates(_hass) as changed_states:
        result = await _hass.services.async_call(domain, service, data, True)

    return action + ("成功" if result else "不成功")

#


async def handleStates(intent_name, query, states, group, names):
    for state in states:
        entity_id = state.entity_id
        if entity_id.startswith('zone') or entity_id.startswith('automation') or group != entity_id.startswith('group'):
            continue

        attributes = state.attributes
        friendly_name = attributes.get('friendly_name')
        if friendly_name is None:
            continue

        if names is not None:
            names.append(friendly_name)
        if query.startswith(friendly_name) or query.endswith(friendly_name):
            action = guessAction(entity_id, intent_name, query)
            return friendly_name + await handleState(entity_id, state.state, action)
    return None

#


def makeResponse(text, open_mic=False):
    return {
        'version': '1.0',
        'is_session_end': not open_mic,
        'response': {
            'open_mic': open_mic,
            'to_speak': {'type': 0, 'text': text},
            # 'to_display': {'type': 0,'text': text}
        }
    }

#


async def handleRequest(data, real_ip):
    _LOGGER.info("Handle Request %s: %s", real_ip, data)
    if not real_ip.startswith('124.251'):
        return makeResponse("未经访问许可")

    request = data['request']

    #
    if 'no_response' in request:
        return makeResponse('主人，您还在吗？', True)

    #
    request_type = request['type']
    if request_type == 2:
        return makeResponse("再见主人，" + _appName + "在这里等你哦！")

    #
    slot_info = data['request'].get('slot_info')
    intent_name = slot_info.get(
        'intent_name') if slot_info is not None else None

    if intent_name == 'Mi_Welcome':
        return makeResponse("您好主人，我能为你做什么呢？", True)

    query = data['query']
    # 使用传入唤醒词截断
    if _appName != '小爱精灵':
        query = query.split(_appName)[-1]

    #
    states = _hass.states.async_all()
    names = [] if query == '导出词表' else None

    text = await handleStates(intent_name, query, states, False, names)
    if text is not None:
        return makeResponse(text)
    text = await handleStates(intent_name, query, states, True, names)
    if text is not None:
        return makeResponse(text)

    if names is not None:
        import locale
        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        return makeResponse(','.join(sorted(names, cmp=locale.strcoll)))

    return makeResponse(_appName + "未找到设备，请再说一遍吧", True)
