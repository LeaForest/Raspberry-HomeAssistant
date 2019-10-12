![](pic\主页.png)



# 一、什么是Home Assistant:

可以方便地连接外部设备（智能设备、摄像头、邮件、云服务等），并可按需手动或自动化地将设备联动的平台空间。

## 特性标签：

**开源 **、识别和直连近千外部设备（小米系列、Apple Siri、亚马逊音响、谷歌、飞利浦系列等）

安全、可靠、响应快

每**两周**一次版本更新     基于**Python**

## 系统体系：

​       **Hass组成:**       →| 内核（core）.工作机制：状态、时间、服务

​                                →| 组件（component）.逻辑程序. 交互基础：近千种不同组件



​        **内核**类似于大脑，并不与感官、运动器官**直接**相连，而是通过类似“神经系统”的**组件**，**间接**地与外界相连，比如：light.hue组件负责与飞利浦HUE智能灯的互动（感知与设置其当前状态）；

​                           camera.mjpeg组件负责获得摄像头的标准MJPEG视频流；

​                           ensor.yr组件负责与yr.no云服务通讯，获得天气信息；

​        **组件**之间的交互，由**Hass内核**中的工作机制（状态、时间、服务）来进行协调，**部分**组件不与外界相连，仅获取内部信息状态，再运行逻辑规则。

​         **操作系统**类似于整个生命系统，**Hass**为神经系统，**内核**为大脑，**组件**为大脑周围的神经元，**Python**环境为血液循环系统。



## 外围系统：

* Hass.io

  主要**应用于树莓派**。负责管理你的设备中一些应用(称为Add-ons)，包括安装、升级。 支持的add-ons(应用)包括：Duck_DNS（一个动态IP域名解析服务）、Let’s Encrypt（自动管理你的ssl数字证书）、Mosquitto MQTT broker（一个MQTT代理服务实现）、SSH_Server、Samba（共享文件夹服务）、DHCP_Server、Snips.ai（一个本地运行的语音识别应用）、等等。

* Hassbian

  是在树莓派上专门用于安装HA系统的定制操作系统，不提供升级管理服务。

* AppDaemon

  基于HomeAssistant的API，为用户提供与HomeAssistant互动的python环境，一般用于编写自动化规则程序。

* HADashboard

  HaDashboard是一个模块化、可换肤的HomeAssistant前端仪表面板，可用于大屏幕显示。基于AppDaemon（必须安装AppDaemon才能安装HaDashboard）。

* ......



# 二、HomeAssistant配置：

## Yaml：配置文件格式

Yaml文件由**“块”**组成    →|序列块：由短横杠**“ - ”**开始

​                                       →|映射块 ：形式为“key: value”

​                                                      →|两者间通过空格缩进表达关系，形成整个yaml文件                               

【**格式规则**】

1. 在“#”右边的文字用于注释，不起实际作用。
2. 冒号（:）左边的字符串代表配置项的名称，冒号右边是配置项的值。
3. 若冒号右边为空，那么下一行开始所有比这行缩进 (左边多两个空格) 的都是这个配置项的值。
4. 如果配置项的值以减号（-）开始，代表这个配置项有若干个并列的值（也可能仅并列一个），每个都是以相同缩进的减号开始。
5. 冒号和减号后面要加一个空格，缩进(两个空格)符必需是空格（不能是tab）

**例1： 一个输入选择（input select）组件**

```yaml
input_select:
  threat:
    name: Threat level
    # 选择项是一个序列
    options:
     - 0
     - 1
     - 2
     - 3
    initial: 0
```

红色框代表一个映射块，绿色框代表一个序列块:

![](pic\例图.png)

**例2：包含了两个MQTT设备的sensor组件**

```yaml
sensor:
  - platform: mqtt
    state_topic: sensor/topic
  - platform: mqtt
    state_topic: sensor2/topic
```

![](pic\图例2.png)



## 进行基础信息配置：

初次运行时，HomeAssistant会根据IP地址确定你的位置信息，然后根据位置信息选择合适的度量衡单位和时区，这些基础信息配置在homeassistant域中。

```yaml
homeassistant:
  latitude: 32.87336
  longitude: 117.22743
  elevation: 430
  unit_system: metric
  time_zone: America/Los_Angeles
  name: Home
```

参见：https://www.hachina.io/docs/336.html



## 基础配置

若HomeAssistant在启动时没找到配置文件（一般是在第一次启动的时候），会自动创建一个配置文件（其中包含通过IP推测的经纬度、时区信息，http访问，自动发现设备、sun实体、天气预报等配置内容）

参见：https://www.hachina.io/docs/331.html



## HTTP配置：

http组件为HomeAssistant Web前端提供文件和数据服务，是HomeAssistant对外提供API服务的基础。

```yaml
# configuration.yaml http配置样例
http:
  api_password: abc54321  # 设置前端访问密码为abc54321
  server_port: 12345      # http对外的服务端口号为12345
  ssl_certificate: /etc/letsencrypt/live/hass.example.com/fullchain.pem
  ssl_key: /etc/letsencrypt/live/hass.example.com/privkey.pem
  cors_allowed_origins:
    - https://google.com
    - https://home-assistant.io
  use_x_forwarded_for: True

# 这些地址来的访问不需要密码
  trusted_networks:
    - 127.0.0.1
    - ::1
    - 192.168.0.0/24
    - 2001:DB8:ABCD::/48
  ip_ban_enabled: True
  login_attempts_threshold: 5
```

参见;https://www.hachina.io/docs/338.html



## 添加设备：

[组件](https://www.hachina.io/docs/472.html)是HomeAssistant连接外部设备的逻辑程序，有一些组件下又区分[平台](https://www.hachina.io/docs/474.html)，比如light（灯）组件下有飞利浦的hue平台、小米的yeelight平台（作为灯，它们的控制逻辑框架一样，但它们与设备的通讯协议不同）。
组件和平台类似于设备的驱动程序；配置文件告诉hass加载哪些组件和平台，以及相应的配置参数。

手工配置参见：https://www.hachina.io/docs/339.html



## 组：

配置多个设备后，采用**组（group）**来组织这些设备，进行界面优化和简化操作。

```yaml
# 组配置的示例
# groups.yaml文件（在configuration.yaml中，配置“group: !include groups.yaml”）
outside_weather:
  name: 室外环境      # 组的friendly_name
  entities: sun.sun, sensor.hachina_temperature, sensor.hachina_humidity, sensor.hachina_pm25, sensor.weather_temperature, sensor.weather_humidity, sensor.weather_precipitation, sensor.weather_pressure, sensor. # 组内的实体
  
# *************************************************************************
# 组中包含的实体，可以在组名冒号后直接用逗号分隔书写；也可以在entities属性中用列表书写；也可以在entities属性后，用逗号分隔书写。

environment_in_office: sensor.temperature_158d0001a1f8f1, sensor.humidity_158d0001a1f8f1, sensor.illumination_34ce0091d350, sensor.pressure_158d0001a1f8f1, binary_sensor.door_window_sensor_158d0001aac1b4, binary_sensor.water_leak_sensor_158d0001bc185d
 
environment_in_plant:
  name: 花盆环境
  entities:
    - sensor.office_flower_moisture
    - sensor.office_flower_temperature
    - sensor.office_flower_light_intensity
    - sensor.office_flower_conductivity
    - sensor.office_flower_battery
 
coin_market:
  name: 电子货币
  entities: sensor.bitcoin, sensor.exchange_rate_1_btc, sensor.ethereum, sensor.ripple
# *************************************************************************

tab_plant:          # 增加此组的页签
  view: yes         # 组的属性“view”控制组是否以TAB页形式展现，缺省值为false。
  name: 花盆环境     # 组中配置的属性“name”是组的friendly_name，仅用于显示。
  icon: mdi:flower  # 组中的属性“icon”用于组在作为TAB页显示时的页签。
  entities: group.environment_in_plant
 
tab_outside:
  view: yes
  name: 室外环境
  icon: mdi:image-filter-hdr
  entities: camera.camera1, group.outside_weather
 
tab_coinmarket:
  view: yes
  name: 电子货币
  icon: mdi:currency-btc
  entities: group.coin_market
```

![](pic\组图.png)

- 组还有一个属性“control”：当组中所有实体都是开关或者灯的时候，HomeAssistant就会在组上自动加上一个on/off的开关（控制所有组成员）；如果你想隐藏这个开关，就将此属性设置为“hidden”。
- 缺省情况下，所有组都会出现在HOME页签中。如果你想改变HOME页签的显示内容，定义一个default_view组就可以覆盖HOME页签的内容。

参见：https://www.hachina.io/docs/340.html



## 子配置文件：

当configuration.yaml越来越大的时候，可以通过“!include”方法，在主配置文件中包含子配置文件。从而拆分成若干文件，方便阅读和编辑。

```yaml
group: !include groups.yaml
automation: !include automations.yaml
script: !include scripts.yaml
light: !include devices/lights.yaml
sensor: !include devices/sensors.yaml
```

使用子配置文件时，需要注意主配置文件与子配置文件内容的匹配。配置文件中就不需要出现“light”和“sensor”这两个域的名字了：

```yaml
# 文件sensors.yaml的内容，不出现“sensor:”
- platform: mqtt
  name: "Room Humidity"
  state_topic: "room/humidity"
- platform: mqtt
  name: "Door Motion"
  state_topic: "door/motion"
  ...
```

格式参见：https://www.hachina.io/docs/341.html



## 调试配置文件：

终端命令行下，输入以下的命令，可以对配置文件进行调试：

- `hass --script check_config`
  检查配置文件是否有错误
- `hass --script check_config --files`
  检查加载了哪些配置文件（包括[include的子文件](https://www.hachina.io/docs/341.html)和[secret文件](https://www.hachina.io/docs/2368.html)）
- `hass --script check_config --info sensor`
  显示某个组件（比如这条命令中的sensor）的配置信息
- `hass --script check_config --info all`
  显示所有组件的配置信息
- `hass --script check_config --help`
  获得关于配置调试命令的完整帮助信息



# 核心机制

 **状态、事件、服务，这三个机制是HomeAssistant核心运行机制。**

- 每个[**实体**](https://www.hachina.io/docs/468.html)（entity，比如一盏灯、一个开关）有一个**状态（state）**，比如“on”、“off”等；每个实体除了状态（state）之外可以有若干个[**属性**](https://www.hachina.io/docs/469.html)（attributes），比如颜色值。
- **事件（event）**是激发/监听机制。事件代表当前发生了什么，比如“state_changed”（状态改变了）事件。激发一个事件，监听者监听到后，执行相应的动作。
- **服务（service）**是注册/调用机制。注册的服务就可以被调用，每个服务代表一个功能，比如“switch.turn_on”（打开开关）。
- **组件（component）**是运行在核心机制上的功能模块，HomeAssistant中组件数量会不断增加。组件可以读、写状态，注册、调用服务，激发、监听事件。也可以与外界互动，获取汇率、执行开灯动作、从温湿度传感器上读取温度等。当组件具有对状态、事件、服务的完全操控能力时，就能设计出自动化（automation组件）的引擎，就能对外提供http（http组件）的服务。

![](pic\核心架构.png)



## 实体、状态与属性：

**外部的设备在HomeAssistant中体现为实体：**一个具体的物理设备可能对应一个或多个实体，比如一个手机摄像头设备，在系统中除了对应摄像头这个实体外，还对应各种开关实体，比如闪光灯开关、前后摄像头切换开关等，如下图。

![](pic\实体.png)

**实体**也可能并不是一个物理存在的设备，比如说汇率、天气状况信息等。在HomeAssistant中，对实体并没有任何前提限定。在组件（component）中可以随意地增加实体，定义它的状态，设置它的属性。

在HomeAssistant的WEB前端中，可以点击开发者工具栏的对应位置，查看当前系统中的所有实体，以及其对应的状态和属性。

实体的标识是**实体ID**，由**域ID**和**对象ID**两部分组成，例如“light.kitchen_ceiling”表示的是在“light”这个域下的“kitchen_ceiling”这盏灯。

每个实体，都对应一个当前**状态（state）**，状态是这个实体的最重要的性质。比如一个智能开关，状态值一般是“on”或者“off”。在程序或者WEB前端中改写某个实体的状态，并不会对实际的设备产生作用，因为修改的只是系统数据库中的数据。

一个实体，除了状态之外，还存在零个或多个**属性（attributes）**。实体的属性，是为了更好的描述这个实体。比如一个比特币行情实体“sensor.exchange_rate_1_btc”，它的状态是当前的交易价格，它的属性包含了价格的计量单位、价格数据来源等信息。



一个实体的属性是由若干个**“属性名称:属性值”**组成的数据结构（IT专业人士将其称为dictionary，字典）。在HomeAssistant中，一个实体的属性通过**JSON格式表达**，比如HomeAssistant中内置的太阳（sun）组件构建的“sun.sun”实体的属性值为：

```yaml
{
  "next_dawn": "2017-09-30T21:23:48+00:00",# 下一个太阳初升的时间（国际标准时间）
  "next_dusk": "2017-09-30T10:05:48+00:00",
  "next_midnight": "2017-09-30T15:44:08+00:00",
  "azimuth": 264.15,
  "next_rising": "2017-09-30T21:47:57+00:00",
  "friendly_name": "Sun",
  "elevation": 3.89,
  "next_noon": "2017-10-01T03:44:10+00:00",
  "next_setting": "2017-09-30T09:41:40+00:00"
}
```

HomeAssistant中，有一些预定义的属性名称，对应的属性值用于这个实体在前端展现时的效果：

![](C:\Users\nicdo\Desktop\预订属性.png)

## 事件（event）:

**事件总线**是Home Assistant中最核心的机制。组件程序可以在事件总线上触发事件，也可以在事件总线上监听事件（当监听到事件发生时执行相应动作）。

一条被触发的**事件**，包含事件**类型、触发时间、事件附加信息**等信息。事件类型代表是什么事件；触发时间是指事件被触发的时间；事件附加信息是一些{KEY:VALUE}格式的信息（专业人士称其为**字典结构数据**）.

```yaml
{
'entity_id': 'light.reading_room',   # “状态变化的实体ID”
'old_state':                         # 变化前的状态属性以及这个状态被设置的时间
'new_state':                         # 变化后的状态属性以及新状态被设置的时间
}
```

为了方便不同组件之间交互（一个组件会监听其他组件程序触发的事件），HomeAssistant预定义了一些事件类型和对应的事件附加信息：

- 事件homeassistant_start
  homeassistant_start事件当所有组件被初始化后被触发。

- 事件homeassistant_stop
  homeassistant_stop当Home Assistant关闭时被触发。当这个事件发生时，各个组件应当关闭各种打开的连接（网络和文件），释放资源。

- 事件state_changed
  事件state_changed当实体（entity）状态改变时被触发。state_changed事件附加信息中包含旧的状态和新的状态。其包含的信息为：

| 字段      | 描述                                                        |
| --------- | ---------------------------------------------------------- |
| entity_id | 状态改变的实体（entity）的ID。如：light.kitchen            |
| old_state | 状态改变之前的状态。如果是一个新的实体，忽略此字段。       |
| new_state | 状态改变之后的新状态。如果实体从状态机中移除，忽略此字段。 |

- 事件time_changed

  事件time_changed被计时器每秒钟触发，其中包含当前时间的信息。

| 字段 | 描述                          |
| ---- | ----------------------------- |
| Now  | 当前的UTC时间（世界标准时间） |

- 事件service_registered

  事件service_registered当一个新的服务被注册时触发。其包含的信息：

| 字段    | 描述                          |
| ------- | ----------------------------- |
| domain  | 服务所在的域，如：light       |
| service | 可以被调用的服务，如：turn_on |

- 事件call_service

  触发call_service事件用于调用一个服务。

| 字段            | 描述                                                      |
| --------------- | --------------------------------------------------------- |
| domain          | 服务所在的域，如：light                                   |
| service         | 要被调用的服务，如：turn_on                               |
| service_data    | 被组织成字典格式的服务调用参数。如：{ ‘brightness’: 120 } |
| service_call_id | 唯一的调用id，字符串格式。如：23123-4                     |

- 事件service_executed

  事件service_executed由服务处理程序触发，表示调用的服务已经被执行。

| 字段            | 描述                                                  |
| --------------- | ----------------------------------------------------- |
| service_call_id | 服务被调用时输入的唯一调用id，字符串格式。如：23123-4 |

- 事件platform_discovered

  事件platform_discovered当自动发现组件（用于网络自动探测发现新的设备）发现一个新平台（platform）时被触发。

| 字段       | 描述                                                         |
| ---------- | ------------------------------------------------------------ |
| service    | 被发现的服务                                                 |
| discovered | 发现的信息，字典（dictionary）格式，如：{ “host”: “192.168.1.10”, “port”: 8889} |
| platform   | 发现的平台，如“xiaomi”                                       |

- 事件component_loaded

  事件component_loaded当一个新的组件（component）加载和初始化完成后被触发。

| 字段      | 描述                          |
| --------- | ----------------------------- |
| component | 被初始化的组件的域。如：light |



##  服务（service）

组件可以在HomeAssistant某一个域（domain）中以服务名（字符串）标识注册一个服务，然后可以调用任意的已注册的服务，**服务**表示组件对外公布的一个功能，如“switch.turn_on”表示打开开关这个功能。调用时，一般会传入数据，传入的数据为JSON格式的字典类型数据，例如，调用“switch”域中注册的服务“turn_off”，可以传入以下参数来告诉这个服务要关闭是哪个开关：{"entity_id":"switch.living_room"}

服务在内核中的实现是基于事件机制的。



## 组件（component）

**组件**是HA中不断被扩展的**程序模块**。大多数情况与HA核心交互（读、写状态，注册、调用服务，触发、监听事件），另方面与外部设备交互，将内核数据与外界有效对应。还有部分组件不与外部设备交互，仅完成核心中状态、事件、服务间逻辑规则的运行 -- **自动化组件（automation）**。



- 温度传感器组件（核心交互）
  一个温度传感器组件定时与温度传感器通讯，获得温度信息，写入对应实体的状态中。
- 智能灯组件（外界交互）
  智能灯组件在系统中注册开关灯的服务，当服务被调用时，组件程序与智能灯通讯，完成对应动作。同时，会定期查询智能灯的开关状态，将此信息写入对应实体的状态中。
- 系统中的automation组件（逻辑规则运行）
  HomeAssistant自带的automation组件，根据配置文件中的trigger信息，监听对应事件；根据配置文件中condition信息，判断对应实体状态是否符合条件；根据配置文件中action信息，调用对应的服务。



## 平台（playform）

有些组件，比如灯（light），会涵盖不同品牌灯的控制（比如小米智能灯、PHILIPS智能灯）。这种组件的逻辑分成两个部分，通用的智能灯的逻辑部分，以及品牌相关的智能灯的逻辑部分；后者被称为**平台（platform）**。



## 域（domain）

通常意义下，**组件的名称就是域**。其概念常用于三种情况：

- 实体名称的形式为“<DOMAIN.OBJECT_ID>”，例如“light.bedroom”中，”light”就是域。
- 服务是被发布在一个具体的域中的（服务的注册与调用需要指定域，如服务：“switch.turn_on”的域为switch）。
- 配置文件的基本格式是< 域:此域下的对应配置信息 >的列表（也可能表达为< 域 OBJECTID:此实体的对应配置信息 > ）。例如下面的配置文件信息中，sensor和switch就是域的名字:

```yaml
sensor:
  - platform: mqtt
    state_topic: "home/bedroom/temperature"
    name: "MQTT Sensor 1"
  - platform: mqtt
    state_topic: "home/kitchen/temperature"
    name: "MQTT Sensor 2"
  - platform: rest
    resource: http://IP_ADDRESS/ENDPOINT
switch:
  - platform: vera
```

- 配置文件加载过程中，根据其中的域，加载对应名字的组件程序。
- 每一个组件程序都会定义一个与它文件名相同的域（DOMAIN）。
- 在这个组件程序中维护状态的实体，使用这个域（DOMAIN）作为标识前缀。
- 在这个组件程序中注册的服务，定义在这个域（DOMAIN）中。A组件中注册的服务都在域A中。



## 自动化组件（atomation）

HA中的自动化由自动化组件实现，该组件读取配置文件中自动化规则的配置，根据配置信息监听相关事件，当事件发生时，判断规则中的条件是否满足，是就执行配置的动作。

自动化规则由三部分组成：trigger（触发器）、condition（条件）、action（动作）。例：

-  trigger：当Alice回到家时
- condition：如果太阳已经下山了
- action：打开客厅的灯

**trigger**触发一个自动化规则开始运行。trigger是对要监听的事件的描述。在这个例子中，trigger是Alice回家这件事，在HomeAssistant中可以通过监听state_changed事件，发现Alice的状态由“not_home”转变为“home”启动。

**condition**在规则中不是必须的。它判断当前的状态值，当满足条件时，规则继续后续执行

**action**在规则中trigger经常混淆：：trigger判断的是一种变化，而condition判断的是变化的结果，例如，trigger可以是灯的状态由关闭变为打开，trigger判断的是一种变化，而condition判断当前灯的状态是打开状态。

```yaml
# configuration.yaml文件中自动化组件配置样例
automation:
#在太阳下山前一小时，如果有人在家；或者有人在16:00-23:00之间回到家，就打开起居室的灯
  - alias: 'Rule 1 Light on in the evening'
    trigger:
      - platform: sun
        event: sunset
        offset: '-01:00:00'
      - platform: state
        entity_id: group.all_devices
        to: 'home'
    condition:
      - condition: state
        entity_id: group.all_devices
        state: 'home'
      - condition: time
        after: '16:00:00'
        before: '23:00:00'
    action:
      service: homeassistant.turn_on
      entity_id: group.living_room
 
#当所有人离开家的时候，关闭所有灯
  - alias: 'Rule 2 - Away Mode'
    trigger:
      platform: state
      entity_id: group.all_devices
      to: 'not_home'
    action:
      service: light.turn_off
      entity_id: group.all_lights
 
# 如果Paulus在20:00之后离开家，就发送通知
  - alias: 'Leave Home notification'
    trigger:
      platform: zone
      event: leave
      zone: zone.home
      entity_id: device_tracker.paulus
    condition:
      condition: time
      after: '20:00'
    action:
      service: notify.notify
      data:
        message: 'Paulus left the house'
```



## 自动化

在系统的自动化（automation）组件中，可以设置若干条自动化规则。trigger触发器、condition条件、action动作。“触发器”触发这条规则开始执行，程序判断“条件”是否满足，若满足，则执行“动作”（“条件”部分如果没有，则直接执行“动作”）。

```yaml
# configuration.yaml文件中自动化组件配置样例
automation:
  #当所有人离开家的时候，关闭所有灯
  - alias: 'Rule - Away Mode'
    trigger:
      platform: state
      entity_id: group.all_devices
      to: 'not_home'
    action:
      service: light.turn_off
      entity_id: group.all_lights
 
  # 如果Paulus在20:00之后离开家，就发送通知
  - alias: 'Leave Home notification'
    trigger:
      platform: zone
      event: leave
      zone: zone.home
      entity_id: device_tracker.paulus
    condition:
      condition: time
      after: '20:00'
    action:
      service: notify.notify
      data:
        message: 'Paulus left the house'
```



### 触发器

触发器在一条规则中是必须有的，当被触发时，这条规则启动进入后续执行。自动化规则中的触发器存在不同的类型（time，event，state，numeric_state等）。在配置文件中，不同类型的触发器以“platform:”（平台）字段标识。不同类型的触发器，需要配置的信息是不一样的。

每一条自动化规则，由三个部分组成，触发器、条件、动作。触发器在一条规则中是必须有的，当被触发时，这条规则启动进入后续执行。

自动化规则中的触发器存在不同的类型（time，event，state，numeric_state等）。在配置文件中，不同类型的触发器以“platform:”（平台）字段标识。不同类型的触发器，需要配置的信息是不一样的。

- 时间（time）触发器

  时间触发器在指定的时间触发规则，可以是某个时刻，也可以是某个指定的分钟（小时、秒），或者每隔多少时间。

  ```yaml
  automation 1:
    trigger:
      platform: time  # （平台）字段标识不同类型的触发器  
      minutes: 5 # 在每个小时的05分钟触发，比如……9:05，10:05，11:05……
      seconds: 00
   
  automation 2:
    trigger:
      platform: time
      at: '15:32:00'   # 在每天的15:32:00触发
   
  automation 3:
    trigger:
      platform: time
      minutes: '/5'    # 当分钟数能被5整除时（也就是每隔5分钟）触发
      seconds: 00
  ```

- 事件（event）触发器

  事件是HomeAssistant运行的核心机制。事件触发器根据事件类型和事件附加信息进行触发；当配置中未设置事件附加信息时，此类事件发生时，不管事件附加信息是什么，此规则都会被触发。

  ```yaml
  automation:
    trigger:
      platform: event
      event_type: MY_CUSTOM_EVENT
      # 可选，表示仅当事件附件信息中的mood为happy时触发
      event_data:
        mood: happy
  ```

* 太阳（sun）触发器
    根据太阳的升起或降落进行触发。触发时间是升起（降落）的当时，也可以是升起（降落）前或者后多少时间。

```YAML
automation:
  trigger:
    platform: sun
    # event的可选值是“sunset”和“sunrise”
    event: sunset
    # 可选，此处代表太阳下山前45分钟触发
    offset: '-00:45:00'
```

* MQTT触发器
  在MQTT的broker上，当某一主题上发布了新的消息时触发。当不指定消息内容时，收到这个主题上的任何新的消息都会引起触发。

```yaml
automation:
  trigger:
    platform: mqtt
    topic: living_room/switch/ac
    # 可选。表示当在“living_room/switch/ac”上收到“on”时触发；如果不设置这行，那么在这个主题上收到任何消息都触发。
    payload: 'on
```

* 具体参见https://www.hachina.io/docs/449.html......

### 条件（condition）

**“条件”**在一条规则中不一定存在：当存在时，“触发”后只有“条件”满足时才会执行”动作”；当不存在时，”触发”后直接执行”动作”。

与触发器类似，自动化规则中的条件有不同的类型；在配置文件中，不同类型的条件以“condition”字段标识。不同类型的条件，需要配置的信息内容也是不一样的。

* 时间（time）条件
  时间条件判断当前是否在某个时刻之前或之后，也可以判断在一个星期中的哪一天。

  ```yaml
condition:
  # 在周一、周三、周五的15:00到20:00之间
  condition: time
  after: '15:00:00'
  before: '20:00:00'
  weekday:
    - mon
    - wed
    - fri
  ```

* 状态（state）条件
  判断一个实体的状态是否是特定的值。

  ```yaml
condition:
  # 判断实体device_tracker.paulus的状态是否是“not_home”
  condition: state
  entity_id: device_tracker.paulus
  state: not_home
  ```

* 太阳（sun）条件
  判断太阳的状况是否满足条件。太阳的状况可以是：太阳升起（下山）以前（以后）——其中，在太阳升起（下山）的时间点上可以加上偏移值。

  ```yaml
condition:
  # 在太阳下山前一小时之后（如果太阳在19:23下山，此处就是在18:23之后为true）
  condition: sun
  after: sunset
  # 可选值
  after_offset: "-1:00:00"
  ```

* 区域（zone）条件
  区域条件用于判断是否一个实体在某个区域中，仅支持在device_tracker域中基于GPS坐标报告的实体（例如，device_tracker组件中的[OwnTracks](https://www.hachina.io/docs/3085.html)和[iCloud](https://www.hachina.io/docs/3100.html)平台支持此特性）。

  ```yaml
condition:
  # 判断实体device_tracker.paulus是否在区域zone.home中
  condition: zone
  entity_id: device_tracker.paulus
  zone: zone.home
  ```

* 模板（template）条件
  模板条件判断是否一个模板的输出是true

   ```yaml
  condition:
    # 判断实体device_tracker.iphone的battery属性值是否大于50 
    condition: template
    value_template: '{{ states.device_tracker.iphone.attributes.battery > 50 }}'
   ```

* 组合条件
  多个条件可以按照or（或者）、and（并且）关系进行组合，形成一条综合判断。

  ```yaml
#当device_tracker.paulus的状态是home，并且（sensor.weather_precip的状态是rain或者sensor.temperature的温度低于20）时，条件满足
condition:
  condition: and
  conditions:
    - condition: state
      entity_id: 'device_tracker.paulus'
      state: 'home'
    - condition: or
      conditions:
        - condition: state
          entity_id: sensor.weather_precip
          state: 'rain'
        - condition: numeric_state
          entity_id: 'sensor.temperature'
          below: '20
  ```

### 动作

**“动作”**是在“触发器”被触发，并且“条件”满足的情况下，要执行的内容。

动作表现为一段**脚本（script）**，脚本可以包含调用一个服务、判断一个条件、触发一个事件等内容。

```yaml
automation 1:
  trigger:
    platform: sun
    event: sunset
  action:
  # 调用服务，打开灯light.kitchen和light.living_room ，并调节到特定的颜色和亮度
    service: light.turn_on
    entity_id:
      - light.kitchen
      - light.living_room
    data:
      brightness: 150
      rgb_color: [255, 0, 0]
 
automation 2:
  trigger:
    platform: sun
    event: sunset
    offset: -00:30
  action:
  # 间隔35分钟，调用服务，发送两条特定的通知
    - service: notify.notify
      data:
        message: Beautiful sunset!
    - delay: 0:35
    - service: notify.notify
      data:
        message: Oh wow you really missed something great.
 
automation 3:
- alias: 'Enciende Despacho'
  trigger:
    platform: state
    entity_id: sensor.mini_despacho
    to: 'ON'
  action:
  # 发送消息后，判断条件是否成立，若成立，则执行后续动作
    - service: notify.notify
      data:
        message: Testing conditional actions
    - condition: or
      conditions:
        - condition: template
          value_template: '{{ states.sun.sun.attributes.elevation < 4 }}'
        - condition: template
          value_template: '{{ states.sensor.sensorluz_7_0.state < 10 }}'
    - service: scene.turn_on
      entity_id: scene.DespiertaDespacho
```

### 自动化中的模板

在自动化规则中，触发器（trigger）和条件（condition）都有模板（template）类型，在动作（action）脚本中，也可以包含模板。



## 安装（Windows平台）：

1、python3.7环境下：

```
pip3 install home assistant
```

2、启动：

```
hass
```

再通过浏览器打开本地服务：http://localhost:8123

或是通过命令直接打开浏览器：

```
hass --open-ui
```

安装教程：https://www.hachina.io/docs/353.html

![](C:/Users/nicdo/Desktop/HomeAssistant/2.Home%20Assistant%E6%A6%82%E8%A7%88/pic/%E7%99%BB%E9%99%86.png)



