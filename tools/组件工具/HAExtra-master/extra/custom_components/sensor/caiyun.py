'''
Web: http://www.caiyunapp.com/map
Ref: http://wiki.swarma.net/index.php/%E5%BD%A9%E4%BA%91%E5%A4%A9%E6%B0%94API/v2
YAML Example:
sensor:
  - platform: caiyun
    #name: CaiYun
    #latitude: 30.000
    #longitude: 120.000
    #scan_interval: 1200
    monitored_conditions: # Optional
      - weather
      - temperature
      - humidity
      - cloud_rate
      - pressure
      - wind_direction
      - wind_speed
      - local_precipitation
      - nearest_precipitation
      - precipitation_distance
      - aqi
      - pm25
      - pm10
      - o3
      - co
      - no2
      - so2
'''

import asyncio
import json
import logging
import random
import time
import voluptuous as vol
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_LONGITUDE, CONF_LATITUDE, CONF_MONITORED_CONDITIONS,
    CONF_SCAN_INTERVAL)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1200)

USER_AGENT = 'ColorfulCloudsPro/3.2.2 (iPhone; iOS 11.3; Scale/3.00)'
DEVIEC_ID = '5F544F93-44F1-43C9-94B2-%012X' % random.randint(0, 0xffffffffffff)

WEATHER_ICONS = {
    'CLEAR_DAY': ('晴天', 'sunny'),
    'CLEAR_NIGHT': ('晴夜', 'night'),
    'PARTLY_CLOUDY_DAY': ('多云', 'partlycloudy'),
    'PARTLY_CLOUDY_NIGHT': ('多云', 'windy-variant'),
    'CLOUDY': ('阴', 'cloudy'),
    'RAIN': ('雨', 'rainy'),
    'SNOW': ('雪', 'snowy'),
    'WIND': ('风', 'windy'),
    'FOG': ('雾', 'fog'),
    'HAZE': ('霾', 'hail'),
    'SLEET': ('冻雨', 'snowy-rainy')
}

SENSOR_TYPES = {
    'weather': ('Weather', None, 'help-circle-outline'),
    'temperature': ('Temperature', '°C', 'thermometer'),
    'humidity': ('Humidity', '%', 'water-percent'),

    'cloud_rate': ('Cloud Rate', None, 'cloud-outline'),
    'pressure': ('Pressure', 'Pa', 'download'),
    'wind_direction': ('Wind Direction', None, 'weather-windy'),
    'wind_speed': ('Wind Speed', 'm/s', 'weather-windy'),

    'local_precipitation': ('Local Precipitation', None, 'weather-pouring'),
    'nearest_precipitation': ('Nearest Precipitation', None, 'mixcloud'),
    'precipitation_distance': ('Precipitation Distance', None, 'mixcloud'),

    'aqi': ('AQI', None, 'leaf'),
    'pm25': ('PM25', 'μg/m³', 'blur'),
    'pm10': ('PM10', 'μg/m³', 'blur-linear'),
    'o3': ('O3', None, 'blur-radial'),
    'co': ('CO', None, 'blur-radial'),
    'no2': ('NO2', None, 'blur-radial'),
    'so2': ('SO2', None, 'blur-radial')
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default='CaiYun'): cv.string,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_MONITORED_CONDITIONS,
                 default=['weather', 'temperature', 'humidity', 'pm25']):
    vol.All(cv.ensure_list, vol.Length(min=1), [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(seconds=1200)): (
        vol.All(cv.time_period, cv.positive_timedelta)),
})


async def async_setup_platform(hass, config, async_add_devices,
                               discovery_info=None):
    """Set up the Caiyun sensor."""
    name = config.get(CONF_NAME)
    longitude = str(config.get(CONF_LONGITUDE, hass.config.longitude))
    latitude = str(config.get(CONF_LATITUDE, hass.config.latitude))
    monitored_conditions = config[CONF_MONITORED_CONDITIONS]
    scan_interval = config.get(CONF_SCAN_INTERVAL)

    caiyun = CaiYunData(hass, longitude, latitude)
    await caiyun.update_data()

    sensors = []
    for type in monitored_conditions:
        sensors.append(CaiYunSensor(name, type, caiyun))
    async_add_devices(sensors)

    caiyun.sensors = sensors
    async_track_time_interval(hass, caiyun.async_update, scan_interval)


class CaiYunSensor(Entity):

    def __init__(self, name, type, caiyun):
        tname, unit, icon = SENSOR_TYPES[type]
        self._name = name + ' ' + tname
        self._type = type
        self._unit = unit
        self._icon = icon
        self._caiyun = caiyun

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._caiyun.data.get('dash_icon') if self._type == 'weather' else 'mdi:' + self._icon

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._type == 'temperature' or self._type == 'humidity':
            return self._type
        return None

    @property
    def available(self):
        return self._type in self._caiyun.data

    @property
    def state(self):
        return self._caiyun.data.get(self._type)

    @property
    def state_attributes(self):
        return self._caiyun.data if self._type == 'weather' else None

    @property
    def should_poll(self):  # pylint: disable=no-self-use
        """No polling needed."""
        return False


class CaiYunData:
    """Class for handling the data retrieval."""

    def __init__(self, hass, longitude, latitude):
        """Initialize the data object."""
        self._hass = hass
        self._longitude = longitude
        self._latitude = latitude
        self.data = {}

    async def async_update(self, time):
        """Update online data and update ha state."""
        old_data = self.data
        await self.update_data()

        tasks = []
        for sensor in self.sensors:
            if sensor.state != old_data.get(sensor._type):
                _LOGGER.info('%s: => %s', sensor.name, sensor.state)
                tasks.append(sensor.async_update_ha_state())

        if tasks:
            await asyncio.wait(tasks, loop=self._hass.loop)

    async def update_data(self):
        """Update online data."""
        data = {}

        try:
            headers = {'User-Agent': USER_AGENT,
                       'Accept': 'application/json',
                       'Accept-Language': 'zh-Hans-CN;q=1'}
            url = "http://api.caiyunapp.com/v2/UR8ASaplvIwavDfR/%s,%s/" \
                "weather?lang=zh_CN&tzshift=28800&timestamp=%d" \
                "&hourlysteps=384&dailysteps=16&alert=true&device_id=%s" % \
                (self._longitude, self._latitude, int(time.time()), DEVIEC_ID)
            _LOGGER.info('getWeatherData: %s', url)
            session = self._hass.helpers.aiohttp_client.async_get_clientsession()
            async with session.get(url, headers=headers) as response:
                json = await response.json()
            #_LOGGER.info('gotWeatherData: %s', json)
            result = json['result']['realtime']
            if result['status'] != 'ok':
                raise

            skycon = result['skycon']
            data['weather'], icon = WEATHER_ICONS[skycon]
            data['dash_icon'] = 'mdi:weather-' + icon

            data['temperature'] = round(result['temperature'])
            data['humidity'] = int(result['humidity'] * 100)

            data['aqi'] = int(result['aqi'])
            data['pm25'] = int(result['pm25'])

            data['cloud_rate'] = result['cloudrate']
            data['pressure'] = int(result['pres'])
            precipitation = result.get('precipitation')
            if precipitation:
                if 'nearest' in precipitation:
                    data['nearest_precipitation'] = precipitation['nearest'].get(
                        'intensity')
                    data['precipitation_distance'] = precipitation['nearest'].get(
                        'distance')
                if 'local' in precipitation:
                    data['local_precipitation'] = precipitation['local'].get(
                        'intensity')
            wind = result.get('wind')
            if wind:
                data['wind_direction'] = wind.get('direction')
                data['wind_speed'] = wind.get('speed')
            if 'pm10' in result:
                data['pm10'] = result['pm10']
            if 'o3' in result:
                data['o3'] = result['o3']
            if 'co' in result:
                data['co'] = result['co']
            if 'no2' in result:
                data['no2'] = result['no2']
            if 'so2' in result:
                data['so2'] = result['so2']
        except:
            import traceback
            _LOGGER.error('exception: %s', traceback.format_exc())

        self.data = data
