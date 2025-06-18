# AOSP 编译& 基本入门

源码目录：
```bash
Android源码根目录	    描述
abi		            应用程序二进制接口
art	                全新的ART运行环境
bionic	            系统C库
bootable	        启动引导相关代码
build	            存放系统编译规则及generic等基础开发包配置
cts	Android         兼容性测试套件标准
dalvik dalvik	    虚拟机
developers	        开发者目录
development	        应用程序开发相关
device	            设备相关配置
docs	            参考文档目录
external	        开源模组相关文件
frameworks	        应用程序框架，Android系统核心部分，由Java和C++编写
hardware	        主要是硬件抽象层的代码
libcore	            核心库相关文件
libnativehelper	    动态库，实现JNI库的基础
ndk	                NDK相关代码，帮助开发人员在应用程序中嵌入C/C++代码
out	                编译完成后代码输出在此目录
packages	        应用程序包
pdk	                Plug Development Kit 的缩写，本地开发套件
platform_testing	平台测试
prebuilts	        x86和arm架构下预编译的一些资源
sdk	                sdk和模拟器
system	            底层文件系统库、应用和组件
toolchain	        工具链文件
tools	            工具文件
Makefile	        全局Makefile文件，用来定义编译规则

```



## 编译

```bash

sudo pacman -S aosp-devel # 自动安装源码编译所依赖的库

source build/envsetup.sh

make clobber

lunch 41

make -j10

emulator

```

```bash

# 内存不够有时，开启swap文件

dd if=/dev/zero of=./swapfile bs=4M count=5120


```


> mmm：编译指定目录下的模块，不编译它所依赖的其它模块。
> mma：编译当前目录下的模块及其依赖项。
> mmma：编译指定路径下所有模块，并且包含依赖。



## 源码概览

网络
Android 10 包含以下网络模块：

网络组件模块，用于提供通用 IP 服务、网络连接监控和强制登录门户检测。
网络堆栈权限配置模块，定义了一种可让模块执行网络相关任务的权限。
网络组件模块
网络组件模块可以确保 Android 能够适应不断完善的网络标准，并支持与新实现进行互操作。例如，通过针对强制门户检测和登录代码的更新，Android 能够及时了解不断变化的强制门户模型；通过针对高级政策防火墙 (APF) 的更新，Android 能够在新型数据包普及的同时节省 WLAN 耗电量。

Android 10 中的变化
网络组件模块包含以下组件。

IP 服务。IpClient（以前称为 IpManager）组件负责处理 IP 层配置和维护。在 Android 9 中，它被蓝牙等组件用于进程间处理，被 WLAN 等组件用于进程内处理。DhcpClient 组件从 DHCP 服务器获取 IP 地址，以便将它们分配给接口。
NetworkMonitor。NetworkMonitor 组件会在连接到新网络或出现网络故障时、检测强制门户时以及验证网络时测试互联网可达性。
强制门户登录应用。强制门户登录应用是一款预安装应用，负责管理强制门户的登录操作。从 Android 5.0 开始，此应用一直是一款独立应用，但它会与 NetworkMonitor 交互，以将一些用户选项转发到系统。
在使用网络组件模块的设备上，系统会将上述服务重构为其他进程，并使用稳定的 AIDL 接口进行访问。重构路径如下表所示。

IP 服务重构路径
Android 9 及更低版本	在 frameworks/base/services/net/java/android/net/ 中：
apf
dhcp
ip
netlink
util（部分）
Android 10 及更高版本	packages/modules/NetworkStack
强制门户登录重构路径
Android 9 及更低版本	在 frameworks/base/ 中：
core/java/android/net/captiveportal/
services/core/java/com/android/server/connectivity/NetworkMonitor.java
packages/CaptivePortalLogin/*（其中 * 表示通配符）
Android 10 及更高版本	packages/modules/CaptivePortalLogin（以及一些其他共享位置）
格式和依赖项
网络组件模块以三个 APK 的形式提供：一个用于 IP 服务，一个用于强制门户登录，一个用于网络堆栈权限配置。

网络组件模块依赖于以下各项：

系统服务器中的特权 @hide 方法（如 IConnectivityManager.aidl 中的此类方法）。这些 API 带有 @SystemApi 注释并受到适当保护，这样一来，该模块可以访问它们，但其他特权应用（如使用新签名权限的应用）则不能。
INetd.aidl 中定义的指向 netd 的 Binder IPC。此接口已转换为稳定的 AIDL，并且需要进行符合性测试。
网络堆栈权限配置模块
网络堆栈权限配置模块不包含任何代码，而是定义了一种供网络堆栈模块和强制门户登录模块使用的权限。系统允许已获得此权限的模块在设备上执行相关的网络配置任务。



网络堆栈配置工具
Android 操作系统中包含标准的 Linux 网络实用程序，如 ifconfig、ip 和 ip6tables。这些实用程序位于系统映像中，并支持对整个 Linux 网络堆栈进行配置。在搭载 Android 7.x 及更低版本的设备上，供应商代码可以直接调用此类二进制文件，这会导致出现以下问题：

由于网络实用程序在系统映像中更新，因此无法提供稳定的实现。
网络实用程序的范围非常广泛，因此难以在保证行为可预测的同时不断改进系统映像。
在搭载 Android 8.0 及更高版本的设备上，供应商分区会在系统分区接收更新时保持不变。为了实现这一点，Android 8.0 不仅提供了定义稳定的版本化接口的功能，同时还使用了 SELinux 限制，以便在供应商映像与系统映像之间保持已知的良好相互依赖关系。

供应商可以使用平台提供的网络配置实用程序来配置 Linux 网络堆栈，但这些实用程序并未包含 HIDL 接口封装容器。为了定义此类接口，Android 8.0 中纳入了 netutils-wrapper-1.0 工具。

Netutils 封装容器
netutils 封装容器实用程序提供了一部分不受系统分区更新影响的 Linux 网络堆栈配置。Android 8.0 包含 1.0 版本的封装容器，借助它，您可以传递与所封装的实用程序（安装在系统分区的 /system/bin 中）相同的参数，如下所示：


u:object_r:system_file:s0           /system/bin/ip-wrapper-1.0 -> netutils-wrapper-1.0
u:object_r:system_file:s0           /system/bin/ip6tables-wrapper-1.0 -> netutils-wrapper-1.0
u:object_r:system_file:s0           /system/bin/iptables-wrapper-1.0 -> netutils-wrapper-1.0
u:object_r:system_file:s0           /system/bin/ndc-wrapper-1.0 -> netutils-wrapper-1.0
u:object_r:netutils_wrapper_exec:s0 /system/bin/netutils-wrapper-1.0
u:object_r:system_file:s0           /system/bin/tc-wrapper-1.0 -> netutils-wrapper-1.0
这些符号链接显示了 netutils 封装容器中封装的网络实用程序，其中包括：

ip
iptables
ip6tables
ndc
tc
如需在 Android 8.0 及更高版本中使用这些实用程序，供应商实现必须遵循以下规则：

供应商进程不得直接执行 /system/bin/netutils-wrapper-1.0，否则会导致错误。
由 netutils-wrapper-1.0 封装的所有实用程序必须使用其符号链接启动。例如，将以前执行该操作的供应商代码 (/system/bin/ip <FOO> <BAR>) 更改为 /system/bin/ip-wrapper-1.0 <FOO> <BAR>。
平台 SELinux 政策禁止在未进行域转换的情况下执行封装容器。此规则不得更改，并会在 Android 兼容性测试套件 (CTS) 中进行测试。
平台 SELinux 政策还禁止直接从供应商进程执行实用程序（例如，/system/bin/ip <FOO> <BAR>）。此规则不得更改，并会在 CTS 中进行测试。
需要启动封装容器的所有供应商网域（进程）必须在 SELinux 政策中添加以下网域转换规则：domain_auto_trans(VENDOR-DOMAIN-NAME, netutils_wrapper_exec, netutils_wrapper)。
注意：如需详细了解 Android 8.0 及更高版本中的 SELinux，请参阅在 Android 8.0 及更高版本中自定义 SEPolicy。
Netutils 封装容器过滤器
封装的实用程序几乎可用于配置 Linux 网络堆栈的任何方面。不过，为了确保可以维护稳定的接口并允许对系统分区进行更新，只能执行某些命令行参数组合；其他命令将被拒绝。

供应商接口和链
封装容器有一个概念称为“供应商接口”。供应商接口通常是指由供应商代码管理的接口，例如移动数据网络接口。通常，其他类型的接口（如 Wi-Fi）由 HAL 和框架管理。封装容器按名称识别供应商接口（使用正则表达式），并允许供应商代码对其执行多种操作。目前，供应商接口包括：

名称结尾是“oem”后跟一个数字的接口，如 oem0 或 r_oem1234。
由当前的 SOC 和 OEM 实现使用的接口，如 rmnet_data[0-9]。
通常由框架管理的接口的名称（如 wlan0）一律不是供应商接口。

封装容器还有一个类似的概念，即“供应商链”。供应商链在 iptables 命令中使用，也按名称识别。目前，供应商链包括：

以 oem_ 开头的链。
由当前的 SOC 和 OEM 实现使用的链，例如以 nm_ 或 qcom_ 开头的链。
允许执行的命令
下面列出了当前允许执行的命令。系统通过一组正则表达式对执行的命令行实施限制。如需了解详情，请参阅 system/netd/netutils_wrappers/NetUtilsWrapper-1.0.cpp。

ip
ip 命令用于配置 IP 地址、路由、IPsec 加密以及多种其他网络参数。封装容器允许执行以下命令：

从供应商管理的接口添加和移除 IP 地址。
配置 IPsec 加密。
iptables/ip6tables
iptables 和 ip6tables 命令用于配置防火墙、数据包修改、NAT 及其他对单个数据包的处理操作。封装容器允许执行以下命令：

添加和删除供应商链。
在引用进入 (-i) 或离开 (-o) 供应商接口的数据包的任何链中添加和删除规则。
从其他任何链中的任意一点跳转到某个供应商链。
ndc
ndc 用于与在 Android 设备上执行大部分网络配置的 netd 守护程序通信。封装容器允许执行以下命令：

创建和销毁 OEM 网络 (oemXX)。
向 OEM 网络添加由供应商管理的接口。
向 OEM 网络添加路由。
在全局范围内和供应商接口上启用或停用 IP 转发。
tc
tc 命令用于配置供应商接口上的流量队列和调整。

====


Android 以太网调用流程

NiceDream
0.064
2017.06.08 09:22:29
字数 81
阅读 3,604
frameworks\base\core\java\android\net\EthernetManager.java

public boolean setEthernetEnabled(boolean enabled) {
        Log.d(TAG,enabled ? "turn on Ethernet" : "turn off Ethernet");
        try {
            return mService.setEthernetEnabled(enabled);
        } catch (RemoteException e) {
            return false;
        }
    }
frameworks\opt\net\ethernet\java\com\android\server\ethernet\EthernetService.java

EthernetServiceImpl.java

public boolean setEthernetEnabled(boolean enable) {
        //enforceChangePermission();
        Log.i(TAG,"setEthernetEnabled() : enable="+enable);
        if ( enable ) {
           return mTracker.setInterfaceUp();
        } else {
           return mTracker.setInterfaceDown(); 
        }
    }
EthernetNetworkFactory.java

public boolean setInterfaceUp() {
       try {
           if(!TextUtils.isEmpty(mIface)) {
               mNMService.setInterfaceUp(mIface);
               sendEthIfaceStateChangedBroadcast(EthernetManager.ETHER_IFACE_STATE_UP);
               return true;
           }
           else
              Log.e(TAG,"mIface is null");
        }catch (Exception e) {
            Log.e(TAG, "Error downing interface " + mIface + ": " + e);
        }
      return false;
    }
\frameworks\base\services\core\java\com\android\server\NetworkManagementService.java

    public void setInterfaceUp(String iface) {
        mContext.enforceCallingOrSelfPermission(CONNECTIVITY_INTERNAL, TAG);
        final InterfaceConfiguration ifcg = getInterfaceConfig(iface);
        ifcg.setInterfaceUp();
        setInterfaceConfig(iface, ifcg);
    }
    
    
    public void setInterfaceConfig(String iface, InterfaceConfiguration cfg) {
        mContext.enforceCallingOrSelfPermission(CONNECTIVITY_INTERNAL, TAG);
        LinkAddress linkAddr = cfg.getLinkAddress();
        if (linkAddr == null || linkAddr.getAddress() == null) {
            throw new IllegalStateException("Null LinkAddress given");
        }

        final Command cmd = new Command("interface", "setcfg", iface,
                linkAddr.getAddress().getHostAddress(),
                linkAddr.getPrefixLength());
        for (String flag : cfg.getFlags()) {
            cmd.appendArg(flag);
        }

        try {
            mConnector.execute(cmd);
        } catch (NativeDaemonConnectorException e) {
            throw e.rethrowAsParcelableException();
        }
    }    
system\netd\server\CommandListener.cpp

CommandListener::InterfaceCmd::InterfaceCmd() :
                 NetdCommand("interface") {
}

int CommandListener::InterfaceCmd::runCommand(SocketClient *cli,
                                                      int argc, char **argv) {
   
        else if (!strcmp(argv[1], "setcfg")) {
            // arglist: iface [addr prefixLength] flags
            if (argc < 4) {
                cli->sendMsg(ResponseCode::CommandSyntaxError, "Missing argument", false);
                return 0;
            }
            ALOGD("Setting iface cfg");

            struct in_addr addr;
            int index = 5;

            ifc_init();

            if (!inet_aton(argv[3], &addr)) {
                // Handle flags only case
                index = 3;
            } else {
                if (ifc_set_addr(argv[2], addr.s_addr)) {
                    cli->sendMsg(ResponseCode::OperationFailed, "Failed to set address", true);
                    ifc_close();
                    return 0;
                }

                // Set prefix length on a non zero address
                if (addr.s_addr != 0 && ifc_set_prefixLength(argv[2], atoi(argv[4]))) {
                   cli->sendMsg(ResponseCode::OperationFailed, "Failed to set prefixLength", true);
                   ifc_close();
                   return 0;
               }
            }

            /* Process flags */
            for (int i = index; i < argc; i++) {
                char *flag = argv[i];
                if (!strcmp(flag, "up")) {
                    ALOGD("Trying to bring up %s", argv[2]);
                    if (ifc_up(argv[2])) {
                        ALOGE("Error upping interface");
                        cli->sendMsg(ResponseCode::OperationFailed, "Failed to up interface", true);
                        ifc_close();
                        return 0;
                    }
                } else if (!strcmp(flag, "down")) {
                    ALOGD("Trying to bring down %s", argv[2]);
                    if (ifc_down(argv[2])) {
                        ALOGE("Error downing interface");
                        cli->sendMsg(ResponseCode::OperationFailed, "Failed to down interface", true);
                        ifc_close();
                        return 0;
                    }
                } else if (!strcmp(flag, "broadcast")) {
                    // currently ignored
                } else if (!strcmp(flag, "multicast")) {
                    // currently ignored
                } else if (!strcmp(flag, "running")) {
                    // currently ignored
                } else if (!strcmp(flag, "loopback")) {
                    // currently ignored
                } else if (!strcmp(flag, "point-to-point")) {
                    // currently ignored
                } else {
                    cli->sendMsg(ResponseCode::CommandParameterError, "Flag unsupported", false);
                    ifc_close();
                    return 0;
                }
            }

            cli->sendMsg(ResponseCode::CommandOkay, "Interface configuration set", false);
            ifc_close();
            return 0;

    }
    return 0;
}
system\core\libnetutils\ifc_utils.c
发送命令到内核；

int ifc_up(const char *name)
{
    int ret = ifc_set_flags(name, IFF_UP, 0);
    if (DBG) printerr("ifc_up(%s) = %d", name, ret);
    return ret;
}

static int ifc_set_flags(const char *name, unsigned set, unsigned clr)
{
    struct ifreq ifr;
    ifc_init_ifr(name, &ifr);

    if(ioctl(ifc_ctl_sock, SIOCGIFFLAGS, &ifr) < 0) return -1;
    ifr.ifr_flags = (ifr.ifr_flags & (~clr)) | set;
    return ioctl(ifc_ctl_sock, SIOCSIFFLAGS, &ifr);
}

