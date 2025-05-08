## ConnectivityService

ConnectivityService（简称CS）是Android系统中的网络连接大管家，所有类型（如WiFi、Telephony、Ethernet等）的网络都需要注册关联到CS并提供链路请求接口。
CS主要提供了以下几个方面的功能：

* 网络有效性检测（NetworkMonitor）
* 网络评分与选择（NetworkFactory、NetworkAgent、NetworkAgentInfo）
* 网口、路由、DNS等参数配置（netd）
* 向系统及三方提供网络申请接口（ConnectivityManager）


### NetworkFactory
系统中的网络工厂，也是CS向链路网络请求的统一接口。Android系统启动之初，数据和WiFi就通过WifiNetworkFactory和TelephonyNetworkFactory将自己注册到CS中，方便CS迅速响应网络请求。

NetworkFactory继承自Handler，并通过AsyncChannel（对Messenger的一种包装，维护了连接的状态，本质上使用Messenger）建立了CS和WifiStateMachine之间的单向通信


### NetworkAgent

链路网络的代理，是CS和链路网络管理者（如WifiStateMachine）之间的信使，在L2连接成功后创建。通过NetworkAgent，WifiStateMachine可以向CS：

* 更新网络状态 NetworkInfo（断开、连接中、已连接等）
* 更新链路配置 LinkProperties（本机网口、IP、DNS、路由信息等）
* 更新网络能力 NetworkCapabilities（信号强度、是否收费等）

CS可以向WifiStateMachine：

* 更新网络有效性（即NetworkMonitor的网络检测结果）
* 禁止自动连接
* 由于网络不可上网等原因主动断开网络

因此，NetworkAgent提供了CS和WifiStateMachine之间双向通信的能力。原理类似NetworkFactory，也是使用了AsyncChannel和Messenger。

CS和WifiStateMachine通过NetworkAgent进行双向通信


### NetworkMonitor
在链路网络注册到CS，并且所有网络配置信息都已经向netd完成了配置，此时就会开始进行网络诊断，具体诊断的任务交给NetworkMonitor。

NetworkMonitor也是一个状态机

|	|		|
| -- 	| --		|
| State	| Description	|
| DefaultState	    |	初始状态。接收CS网络诊断命令消息后触发诊断；接收用户登录网络消息    |
| MaybeNotifyState	    |	通知用户登录。接收诊断后发送的"CMD_LAUNCH_CAPTIVE_PORTAL_APP"消息，startActivity显示登录页面    |
| EvaluatingState	    |	诊断状态。进入时发送"CMD_REEVALUATE"消息，接收 “CMD_REEVALUATE” 消息并执行网络诊断过程    |
| CaptivePortalState	    |	登录状态。进入时发送"CMD_LAUNCH_CAPTIVE_PORTAL_APP"消息显示登录页面，发送10分钟延迟的"CMD_CAPTIVE_PORTAL_RECHECK"消息进行再次诊断    |
| ValidatedState       	    |	已验证状态。进入时发送"EVENT_NETWORK_TESTED"通知CS网络诊断完成。    |
| EvaluatingPrivateDnsState |	私密DNS验证状态。Android Pie验证私密DNS推出。    |


### NetworkPolicyManagerService
NetworkPolicyManagerService（简称NPMS）是Android系统的网络策略管理者。NPMS会监听网络属性变化（是否收费，metered）、应用前后台、系统电量状态（省电模式）、设备休眠状态（Doze），在这些状态发生改变时，为不同名单内的网络消费者配置不同的网络策略。


### NetworkPolicyManagerService
NetworkPolicyManagerService（简称NPMS）是Android系统的网络策略管理者。NPMS会监听网络属性变化（是否收费，metered）、应用前后台、系统电量状态（省电模式）、设备休眠状态（Doze），在这些状态发生改变时，为不同名单内的网络消费者配置不同的网络策略。

网络策略的基本目的：

* 在收费网络的情况下省流量
* 最大可能性的省电
* 防止危险流量进入

网络策略中几个重要的名单：

* mUidFirewallStandbyRules	
黑名单，针对前后台应用。此名单中的APP默认REJECT，可配置ALLOW。

* mUidFirewallDozableRules	
白名单，针对Doze。此名单中的APP在Doze情况下默认ALLOW。

* mUidFirewallPowerSaveRules	
白名单，针对省电模式（由Battery服务提供）。此名单中的APP在省电模式下默认ALLOW，但在Doze情况下仍然REJECT

NPMS对网络策略进行统一管理和记录，并配合netd和iptables/ip6tables工具，达到网络限制的目的。


### NetworkManagementService
Android SystemServer不具备直接配置和操作网络的能力，所有的网络参数（网口、IP、DNS、Router等）配置，
网络策略执行都需要通过netd这个native进程来实际执行或者传递给Kernel来执行。

而NetworkManagementService（简称NMS）就是SystemServer中其他服务连接netd的桥梁。

NMS和netd之间通信的方式有两种：Binder 和 Socket。
为什么不全使用Binder？原因在于Android老版本上像 vold、netd 这种native进程和SystemServer通信的方式都是使用的Socket，目前高版本上也在慢慢的Binder化，提升调用速度。

### netd
为了保障各个功能的正常运行，Android系统中有非常多的守护进程（Daemon）。
为了保证系统起来后各项功能都已经ready，这些daemon进程跟随系统的启动而启动，而且一般比system_server进程先启动。

init.svc.netd进程由init进程启动

如存储相关的vold、电话相关的rild、以及网络相关netd等

netd作为Android系统的网络守护者，主要有以下方面的职能：

* 处理接收来自Kernel的UEvent消息（包含网络接口、带宽、路由等信息），并传递给Framework

* 提供防火墙设置、网络地址转换（NAT）、带宽控制、网络设备绑定（Tether）等接口

* 管理和缓存DNS信息，为系统和应用提供域名解析服务



----
当前网络信息以及网络检测
adb shell dumpsys connectivity

来查看当前的网络策略
adb shell dumpsys netpolicy


查看NMS和netd之前通过socket传递的信息记录
db shell dumpsys network_management


### 注网
WiFi、Data、Ethernet等类型链路网络注册到CS，
并将Interface、IP、DNS、Router等网络属性设置到netd中的过程称为Android系统的注网过程。

WifiStateMachine和CS之间是通过WifiNetworkAgent使用AsyncChannel来进行双向通信的.

Android系统网络注册过程很复杂，涉及到的模块也非常多。主要可以分为以下几个步骤：


### 网络有效性检测
每种类型的链路网络在L2连接上并注册到CS中时，CS都会为其匹配一个NetworkMonitor，用于进行网络有效性检测。
NetworkMonitor将检测结果反馈给CS，CS会根据结果进行以下过程：

* 标记和提示用户网络有效性状态
* 提示用户进入网络二次登录操作（针对Portal类型网络，如机场WiFi）
* 为网络进行评分，并进行网络切换，提供最优网络

触发网络有效性检测的时机：

* 链路连接上并且Interface/IP/Router/DNS等配置成功后触发检测
* 网络检测不通过时延时触发检测
* Portal类型网络登录后触发检测
* 三方APP通过CS的reportNetworkConnectivity接口反馈网络有效性触发检测

#### 网络有效性检测的原理：

* DNS验证：
使用"Network.getAllByName(host)"进行DNS解析，成功则验证通过，抛出"UnknownHostException"异常则说明验证失败。

* HTTP验证：
使用HttpURLConnection访问generate_204网站（访问成功会返回204的response code），
该网站一般使用Google提供的"http://connectivitycheck.gstatic.com/generate_204"，各大手机厂商也会进行定制，防止被墙导致诊断失误。
HTTP验证会有3种结果，根据response code确定：

* code=204：
返回值由generate_204网站返回，网络验证通过

* 200<=code<=399：
返回值由路由器网关返回，一般会携带redirect url，网络需要登录

* code不在上述范围内：无法上网

* 抛出"IOException"，无法上网

## 网络策略/防火墙

为了达到省电/省流量/拦截等目的，Android系统会在多种场景下（Doze、Powersave、前后台等）根据配置进行网络流量限制。

### Netfilter和iptables
Android基于Linux内核，而Linux则使用Netfilter这个"钩子"在内核的IP协议栈中去hook各个阶段的数据包，
根据预先制定的包过滤规则，定义哪些数据包可以接收，哪些数据包需要丢弃或者拒绝。

#### iptables/ip6tables：

iptables/ip6tables是用户层的一个工具，用户层使用iptables/ip6tables通过socket的系统调用方式（setsockopt、getsockopt）获取和修改Netfilter需要的包过滤规则，
是用户层和内核层Netfilter之间交互的工具。（iptables用于IPv4，ip6tables用于IPv6）

Netfilter和iptables是Linux网络防火墙中重要的组成部分。

![netfilter](./imgs/netfilter.png)

收到的每个数据包都从（1）进来，经过路由判决，如果是发送给本机的就经过（2），然后往协议栈的上层继续传递；
否则，如果该数据包的目的地不是本机，那么就经过（3），然后顺着（5）将该包转发出去。

Netfilter在 `PRE_ROUTING`、`LOCAL_IN`、`LOCAL_OUT`、`FORWARD``、POST_ROUTING` 这5个阶段分别设置回调函数（hook函数），
对每一个进出的数据包进行检测。

Q：为什么不只在PRE_ROUTING和POST_ROUTING这两个入口和出口设置数据包检测？

A：一方面，这两个阶段处于网络层（IP层）协议栈中，这时候不会拆解TCP/UDP等传输层协议的头部信息，
如果需要对更上层协议内容（如端口等）进行过滤，在这两个阶段显然不行；
另一方面，这两个阶段协议栈不知道这个数据包是需要转发给谁，是转发到下一跳还是传递给上层协议栈，
如果是需要传递给上层应用，就更不知道需要传递给哪个应用了。
但这些信息在LOCAL_IN和LOCAL_OUT这两个阶段是明确的（明确了传输层协议类型、源IP/目的IP、源端口/目的端口，确定了一条连接），
这样过滤应用的报文就成为了可能。

#### Netfilter主要有3个模块和3张表：

##### 包过滤子模块：
对应filter表，能够对数据包进行过滤，DROP/REJECT/RETURN/ACCEPT

##### NAT子模块：
对应nat表，能够实现网络地址转换

##### 数据报修改和跟踪模块：
对应mangle表，能够对数据包打上或者判断mark标记，也可以修改数据报中的其它内容（如IP协议头部的tos等）。

应用层通过iptables工具修改filter、nat和mangle这三张表来控制Netfilter的行为。

> iptables和Netfilter交互方式：
> iptables的源码在/external/iptables目录下，编译完成后，iptables在系统中是一个可执行的bin文件，位于/system/bin目录下

iptables和Netfilter通信使用的是sockopt的系统调用方式，通过setsockopt和getsockopt在参数中传递对应命令值来进行修改和查询

![](./imgs/iptables_tcpip.png)


Google、各大ODM及手机厂商都会配置很多包过滤规则来进行定制化，因此iptables的操作会很频繁，每次fork都会占用比较大的时间资源；
并且为了保证并发访问修改内核的ip tables规则时的安全性，iptables中其实是有文件锁（#define XT_LOCK_NAME "/system/etc/xtables.lock"）存在的，
这样就又存在排队等待。这个过程比较耗时甚至可能还会引起上层的系统watchdog。

Google在Android O上做了优化：netd中fork出一个iptables-restore进程并且保持它的存活，
每次需要时都通过socket的方式将命令发送给该子进程，并且在执行连续执行命令时做了优化，尽可能保证一次查询一次修改。
大大优化了效率。

### 评分机制
CS中注册的网络可能不只一种，同时，CS也能够向Data和WiFi提供的NetworkFactory请求链路网络。
多种网络共存时，就存在优先选择的问题，CS通过分数统计的方式来进行网络择优。评分的影响因素有：

* 链路网络存在初始分数：WiFi默认为60分，Data默认为50分

* 链路网络根据信号衰减rssi更新初始分数

* 用户强行选择的网络（不可上网但用户主动连接）默认100分

* 网络是否可以上网，不可上网则减去40分


## DNS 解析器

### Android 10 中的变化
在搭载 Android 9 及更低版本的设备上，DNS 解析器代码分布在 Bionic 和 netd 上。

DNS 查找操作集中在 netd 守护程序中，以便进行系统级缓存，而应用在 Bionic 中调用函数（例如 getaddrinfo）。

查询会通过 UNIX 套接字发送到 `/dev/socket/dnsproxyd`，再到 netd 守护程序，该守护程序会解析请求并再次调用 getaddrinfo 用于发出 DNS 查找请求，
然后它会缓存结果以供其他应用使用。

DNS 解析器实现主要包含在 `bionic/libc/dns/` 中，部分包含在 `system/netd/server/dns` 中。

Android 10 将 DNS 解析器代码移至 `system/netd/resolv`,，将其转换为 C++，然后对代码进行了翻新和重构。
由于应用兼容性方面的原因，Bionic 中的代码继续存在，但系统不会再调用它们。以下源文件路径受到重构的影响：


* bionic/libc/dns
* system/netd/client
* system/netd/server/dns
* system/netd/server/DnsProxyListener.*
* system/netd/resolv


DNS 解析器模块以 APEX 文件的形式提供，并由 netd 动态链接；
但是 netd 不是依赖项，因为模块直接提供本地套接字 `/dev/socket/dnsproxyd`。

解析器配置的 Binder 端点已从 netd 移至解析器，这意味着，系统服务可以直接调用解析器模块，无需通过 netd。

DNS 解析器模块依赖于 libc (Bionic) 并静态链接其依赖项；不需要使用其他库。


## 网络
Android 10 包含以下网络模块：

* 网络组件模块
用于提供通用 IP 服务、网络连接监控和强制登录门户检测。

* 网络堆栈权限配置模块
定义了一种可让模块执行网络相关任务的权限。

网络组件模块以三个 APK 的形式提供：
一个用于 IP 服务，一个用于强制门户登录，一个用于网络堆栈权限配置。

### 网络组件模块
网络组件模块可以确保 Android 能够适应不断完善的网络标准，并支持与新实现进行互操作。例如，通过针对强制门户检测和登录代码的更新，Android 能够及时了解不断变化的强制门户模型；通过针对高级政策防火墙 (APF) 的更新，Android 能够在新型数据包普及的同时节省 WLAN 耗电量。

Android 10 中的变化
网络组件模块包含以下组件。

#### IP 服务
IpClient（以前称为 IpManager）组件负责处理 IP 层配置和维护。
在 Android 9 中，它被蓝牙等组件用于进程间处理，被 WLAN 等组件用于进程内处理。DhcpClient 组件从 DHCP 服务器获取 IP 地址，以便将它们分配给接口。

#### NetworkMonitor
NetworkMonitor 组件会在连接到新网络或出现网络故障时、检测强制门户时以及验证网络时测试互联网可达性。

#### 强制门户登录应用
强制门户登录应用是一款预安装应用，负责管理强制门户的登录操作。
从 Android 5.0 开始，此应用一直是一款独立应用，但它会与 NetworkMonitor 交互，以将一些用户选项转发到系统。

在使用网络组件模块的设备上，系统会将上述服务重构为其他进程，并使用稳定的 AIDL 接口进行访问。重构路径如下表所示。

### IP 服务重构路径
* Android 9 及更低版本	
在 `frameworks/base/services/net/java/android/net/` 中：
* apf
* dhcp
* ip
* netlink
* util（部分）

* Android 10 及更高版本	
`packages/modules/NetworkStack`






----

几种可能导致无法上网的原因：

* WiFi网络未验证（portal网络），访问时路由器会重定向到二次登录网址
* 运营商服务器或代理服务器问题，无法连接到外网
* DNS服务器问题，导致DNS解析失败
* 系统时间不正常，导致证书失效，SSL/TLS握手失败，HTTPS无法上网
* TCP连接长时间无数据收发，达到NAT超时时间，网络运营商切断TCP连接，导致长连接失效（push心跳间隔应小于NAT超时时间）

* 应用进入了后台且在mUidFirewallStandbyRules黑名单中，数据包被DROP
* 系统进入省电模式且应用不在mUidFirewallPowerSaveRules白名单中，数据包被DROP
* 系统进入Doze且应用不在mUidFirewallDozableRules白名单中，数据包被DROP

