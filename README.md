#  智能家居平台Home Assistant初探

#  ——Hass.io的配置、安装与使用





*注：本文档仅限宁理物联网工程校友群交流学习使用，不得随意转载或发布咯——物联网14101*



[Home Assistant](https://home-assistant.io/) 是一个基于 Python 3 开发的开源家庭自动化平台。可以跟踪和控制家庭中的所有设备，并实现自动化控制。不同于商业化的平台，Home Assistant 依托的是庞大的社群，目前支持 779 种不同组件，在 Github 上还有更多的定制组件，0.50 版本后，能够直接接入小米设备。它最大的优势在于丰富的自动化配置以及高度自由的定制化。

![](pic/1.gif)

[树莓派](https://www.raspberrypi.org/) 是由树莓派基金会研发的一种只有信用卡大小的单板机电脑，最初的设计目标是用较为廉价的硬件和开源软件为儿童提供一个计算机教育平台。但其优秀的扩展性和易于开发的特性，使其不仅仅用于儿童教育，更是成为了极客们的玩具。树莓派被开发出了千千万万种玩法，并且普通人也可以轻松实现。感兴趣的请深入阅读“少数派”的文章[树莓派入门指南](https://sspai.com/post/38542)。

经过众多版本的迭代以及社区成员的贡献，Home Assistant 支持大部分平台，包括 Docker、macOS、Linux、Windows 等。在树莓派上安装 Home Assistant 有多种方式，你可以选择在树莓派 Raspbian 系统下安装，也可以之间安装集成了 Home Assistant 的 Hassbian 操作系统。

我选择2017年发布的 Hass.io 集成系统，全可视化安装配置，基 [Docker](https://www.docker.com/) 和  [ResinOS](https://resinos.io/) 。



## 一、下载镜像文件与烧录：

1. 准备一张大于32G的TF卡，使用SDformatter进行格式化：

   ![](pic/1.1.png)

2. 在[Home Assistant官网](https://www.home-assistant.io/)选择合适的镜像文件进行**[下载](https://www.home-assistant.io/hassio/installation/)**;![](pic\1.2.png)

3. 烧录工具采用Etcher，可在**[官网](https://www.balena.io/etcher/)**进行下载：![](pic\1.3.png)

4. 将格式化后的SD卡接入PC端口后，打开Etcher软件，并选择下载下来的hassos_rpi3-2.11.img.gz镜像文件，进行烧录：
![](pic\1.4.png)

![](pic\1.5.png)

4. 烧录完成，开始进行网络的配置。



## 二、网络环境的配置：

​        **树莓派的网络连接，可以在插入TF卡后采取线直连的方式的方式。但在很多环境情况下，采用WiFi的方式使用起来更为便捷，但是配置的过程中就会遇到很多问题，相对要复杂得多：**

1. 在使用WiFi得情况下，利用读卡器将烧好程序得TF卡继续接如Window系统端口下（Mac无法读取），并在树莓派系统盘：Hassos-boot下创建文件夹:CONFIG/network，最终在该路径中创建文本文件“my-network”:![](pic/2.1.png)

2. 将网络配置的主要参数，写入该文本文件中并保存，具体设置可参考**[链接](https://github.com/home-assistant/hassos/blob/dev/Documentation/network.md)**:

   ```python
   [connection]
   id=hassos-network
   uuid=72111c67-4a5d-4d5c-925e-f8ee26efb3c3
   type=802-11-wireless
   
   [802-11-wireless]
   mode=infrastructure
   ssid=yuhan888888     # MY_SSID
   
   [802-11-wireless-security]
   auth-alg=open
   key-mgmt=wpa-psk
   psk=yuhan123456      # SSID_KEY
   
   [ipv4]
   method=auto
   
   [ipv6]
   addr-gen-mode=stable-privacy
   method=auto
   ```

3. 创建好网络配置的同时，如果能够保证该局域网在翻墙的代理状态下，进行后续的文件下载将会更加快捷，所以此次采用了ShadowSocket代理服务器进行网络的连接。当然，在非代理环境析也能够进行后续服务的配置下载，但是速度就可能会少微有些缓慢了：![](pic\2.2.png)

4. 网络配置完成后，即可直接进入IO，但是仍需系统的时间配置，才能使io进入下载环境。


## 三、HassIO系统配置：

**将插在读卡器上的系统TF卡安全退出后，插入树莓派，并连上鼠标与显示器，
