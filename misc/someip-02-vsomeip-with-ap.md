---
title: 'someip-01: vsomeip with ap'
date: 2021-12-22 18:10:05
tags:
    - someip
    - vSOMEIP
---
## vector autosar someip与vsomeip对接经验总结

someip是现代车辆通信的主流通信协议知一

虽然someip协议已经基本成熟，但有多个实现版本，现在使用较多的主要有
* vector autosar 的someip版本
* vsomeip；

这两个版本在理论上是可以相互兼容正常通信的，但在实际使用过程中，仍然发现了一些问题；

### 在同一个局域网内，两方无法相互发现；

原理：运行的someip应用需要借助于各自的someipd服务来彼此发现对方；

而someipsd实现的someip sd协议是借助于udp的广播来发布或收集网络中的其他someip应用的相关信息的；

所以要想两方能够彼此发现，首先要将someip sd的服务设置为同一广播地址以及服务端口号；

这个信息可以在vsomeip程序加载的vsomeip-tcp-server.jason等配置文件中进行修改；

理想情况下，将两方的配置修改成一样就可以正常发现彼此；

 

### 将someip sd的广播地址以及服务端口号配置成一样，双方仍然是无法发现彼此；

这个首先要借助网络工具来抓包进行确认，是否可以在网络上抓取到相应的udp数据包，来检查是不是由于网络设置的原因造成的；

如果抓包工具可以确认在网络上有影响的udp广播包；

那么就要对someip的版本号配置进行确认；

在使用vsomeip 2.10版本时发现，vsomeip 代码中的默认主版本号信息为0x00;而vector autasar的someip版本号信息不特意更改的话是0x01;

由于双方版本号不一致，虽然彼此可以收到对方发出的sd udp广播包，但在软件中彼此仍然无法相互识别。并且在vsomeip中会频繁输出warning信息；

将双方的版本号信息设置为一致时，就相互就可以识别了；

 

### sd 广播地址服务端口号以及版本号都配置成一致；但彼此仍然无法发现；

这个就需要排查网络设置问题；

(1)双方是否可以彼此ping通；

(2)路由表以及gateway是否配置正确；

我就遇到双方可以ping通，但由于路由表以及gateway信息缺失使得双方无法彼此发现的问题；

 

### 双方可以彼此发现，但客户端一订阅或者发送request底层tcp链接就断开的情况；

这个问题，也是由于服务版本号的问题（interface version）;

由于某些特殊的原因，将autosar someip的主版本号设置为255可以与vsomeip 的0版本号相互发现；

但是当进行交互时，在代码中会对interface version配置进行验证。如果双方的interface version不一致，那么就会出现一通信底层tcp的链接就会断开情况；

这个需要注意检查；

 
### 当vsomeip作为服务器,autosar someip作为客户端。vsomeip发送的event,autosar someip的客户端无法接收到的情况；

首先要对someip传输类型进行确认（使用的是tcp或者udp）;

假如使用tcp进行传输；则需要将vsomeip 配置文件中event配置添加is_reliable为true的字段；

否则autasar someip tcp的客户端无法正常接收；