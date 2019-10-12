#!/usr/bin/env python
# coding: utf-8

import os, sys, json
try:
    from urllib2 import urlopen
    from urllib import unquote
    reload(sys)
    sys.setdefaultencoding('utf8')
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import unquote

#
def log(message):
    sys.stderr.write(message + '\n')

# Log HTTP payload
REQUEST_METHOD = os.getenv('REQUEST_METHOD')
if REQUEST_METHOD:
    log(REQUEST_METHOD + ' ' + os.environ['SCRIPT_NAME'] + '?' + os.environ['QUERY_STRING'] + '\n')

#
_appName = '小爱精灵'
_haUrl = None
def validateToken(queryString):
    global _appName
    global _haUrl
    parts = queryString.split('_')
    count = len(parts)
    if count > 2 and (parts[0] == 'http' or parts[0] == 'https'):
        i = 0
    elif count > 3 and (parts[1] == 'http' or parts[1] == 'https'):
        _appName = unquote(parts[0])
        i = 1
    else:
        return False

    _haUrl = parts[i] + '://' + parts[i+1] + ':' + parts[i+2] + '/api/%s'
    if count > i+3:
        _haUrl += '?api_password=' + parts[i+3]
    log('validateToken: ' + _appName + ', HAURL: ' + _haUrl)
    return True

#
def haCall(cmd, data=None):
    url = _haUrl % cmd
    method = 'POST' if data else 'GET'
    log('HA ' + method + ' ' + url)
    if data:
        log(data)
    if url.startswith('https'): # We need extra requests lib for HTTPS POST
        import requests
        result = requests.request(method, url, data=data, timeout=12).text
    else:
        result = urlopen(url, data=data, timeout=3).read()

    #log('HA RESPONSE: ' + result)
    return json.loads(result)

#
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
def handleState(entity_id, state, action):
    if action == '打开':
        service = 'cover/open_cover' if entity_id.startswith('cover') or entity_id == 'group.all_covers' else 'homeassistant/turn_on'
    elif action == '关闭':
        service = 'cover/close_cover' if entity_id.startswith('cover') or entity_id == 'group.all_covers' else 'homeassistant/turn_off'
    else:
        return '为' + (STATE_NAMES[state] if state in STATE_NAMES else state)

    data = '{"entity_id":"' + entity_id + '"}'
    result = haCall('services/' + service, data)
    return action + "成功" if type(result) is list else "不成功"

#
def handleStates(intent_name, query, states, group, names):
    for state in states:
        entity_id = state['entity_id']
        if entity_id.startswith('zone') or entity_id.startswith('automation') or group != entity_id.startswith('group'):
            continue

        attributes = state['attributes']
        friendly_name = attributes.get('friendly_name')
        if friendly_name is None:
            continue

        if names is not None:
            names.append(friendly_name)
        if query.startswith(friendly_name) or query.endswith(friendly_name):
            action = guessAction(entity_id, intent_name, query)
            return friendly_name + handleState(entity_id, state['state'], action)
    return None

#
def handleRequest(body):
    if not validateToken(os.environ['QUERY_STRING']):
        return (True, "需要配置服务端口类型哦")

    request = body['request']

    #
    if 'no_response' in request:
        return (False, '主人，您还在吗？')

    #
    request_type = request['type']
    if request_type == 2:
        return (True, "再见主人，" + _appName + "在这里等你哦！")

    #
    slot_info = body['request'].get('slot_info')
    intent_name = slot_info.get('intent_name') if slot_info is not None else None

    if intent_name == 'Mi_Welcome':
        return (False, "您好主人，我能为你做什么呢？")

    query = body['query']
    # 使用传入唤醒词截断
    if _appName != '小爱精灵':
        query = query.split(_appName)[-1]

    #
    states = haCall('states')
    names = [] if query == '导出词表' else None

    text = handleStates(intent_name, query, states, False, names)
    if text is not None:
        return (True, text)
    text = handleStates(intent_name, query, states, True, names)
    if text is not None:
        return (True, text)

    if names is not None:
        import locale
        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        return (True, ','.join(sorted(names, cmp=locale.strcoll)))

    return (False, _appName + "未找到设备，请再说一遍吧")

# Main process
try:
    if REQUEST_METHOD == 'POST':
        body = json.load(sys.stdin)
        log(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        # TEST only
        body = {
        }
    is_session_end, text = handleRequest(body)
except:
    import traceback
    log(traceback.format_exc())
    is_session_end, text = (True, "主人，程序出错啦！")

#
response = {
    'version': '1.0',
    'is_session_end': is_session_end,
    'response': {
        'open_mic': not is_session_end,
        'to_speak': {'type': 0,'text': text},
        #'to_display': {'type': 0,'text': text}
     },
}

# Process final result
result = json.dumps(response, indent=2, ensure_ascii=False)
if REQUEST_METHOD:
    log('RESPONSE ' + result)

    print('Content-Type: application/json\r\n')
    print(result)
