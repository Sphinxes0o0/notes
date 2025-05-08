---
title: vSOMEIP source reading
date: 2022-01-06 02:06:23
tags:
    - CPP
    - SOMEIP
    - sources
    - notes
---

# VSOMEIP 源码学习分享 之 手摸手编译安装过源码


Content
---

1. 源码结构

2. 环境和编译

3. 核心内容  

  3.1 模块  

  3.2 配置



## 1. 源码结构

```bash
dev@dev:~/someip_space/vsomeip$ tree . -L 1
.
├── Android.bp
├── AUTHORS
├── CHANGES
├── CMakeLists.txt
├── config               --> 示例配置文件
├── documentation        --> 使用文档
├── examples             --> Demo
├── exportmap.gcc        --> 控制动态库的函数导出
├── implementation       --> 逻辑代码实现
├── interface            --> 代码接口设计
├── LICENSE
├── LICENSE_boost
├── README.md
├── test                 --> 测试代码
├── tools                --> some_ctrl 工具
├── vsomeip3Config.cmake.in            --|
├── vsomeip3ConfigVersion.cmake.in       |
├── vsomeip3.pc.in                       |
├── vsomeipConfig.cmake.in               | ==> cmake 配置
├── vsomeipConfigVersion.cmake.in        |
├── vsomeip.pc.in                        |
└── vsomeip.xml                        --|
```

> 核心代码都在 implementation

### implementation


![arch](../imgs/00_overview_source_arch.png)

```bash
dev@dev:~/someip_space/vsomeip/implementation$ tree . -L 1
.
├── compat                 --> 3.x 和 2.x 兼容层
├── configuration          --> 配置模块: 配置读取,加载; 插件配置
├── e2e_protection         --> e2e模块
├── endpoints              --> client/server, tcp/udp, TP endpoint 实现
├── helper                 --> boost 兼容层
├── logger                 --> logger
├── message                --> message, payload, (反)序列化 实现
├── plugin                 --> 插件模块: 插件管理
├── routing                --> 路由模块 
├── runtime                --> 运行时: 管理 APP , runtime 资源
├── security               --> 安全模块: policy, credentials 
├── service_discovery      --> 服务发现: 
                                    发现注册模块, 
                                    IPv4/IPv6 Options, 
                                    负载均衡, 
                                    远程订阅
├── tracing                --> tracing: 配置 dlt-daemon
└── utility                --> 通用工具
```



## 2. 环境和编译

### 环境

OS环境:

```bash
lsb_release -a
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 21.04
Release:	21.04
Codename:	hirsute
```

> 实测 18.04 也没有问题, 官方推荐14.04 及以上

#### 工具

* CMake

> ref : https://apt.kitware.com/

```bash
# For Ubuntu Bionic Beaver (18.04) and newer:
sudo apt-get update
sudo apt-get install gpg wget

# For Ubuntu Xenial Xerus (16.04):
sudo apt-get update
sudo apt-get install apt-transport-https wget

# Obtain a copy of our signing key:
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null

# Add the repository to your sources list and update

# For Ubuntu Focal Fossa (20.04):
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ focal main' | sudo tee /etc/apt/sources.list.d/kitware.list >/dev/null

sudo apt-get update

# For Ubuntu Bionic Beaver (18.04):
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ bionic main' | sudo tee /etc/apt/sources.list.d/kitware.list >/dev/null

sudo apt-get update


# For Ubuntu Xenial Xerus (16.04):
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ xenial main' | sudo tee /etc/apt/sources.list.d/kitware.list >/dev/null

sudo apt-get update

# Install the kitware-archive-keyring package to ensure that your keyring stays up to date as we rotate our keys:
sudo rm /usr/share/keyrings/kitware-archive-keyring.gpg
sudo apt-get install kitware-archive-keyring

# install cmake
sudo apt-get install cmake

```

* g++ / clang++

  需要支持 C++11 , 因为使用了很多 C++11 的特性, 如 `std::bind`

* boost 1.71

  1.71 刚好和 DoIP boost版本保持一致
  - repo, (master branch) 

    ```bash
    Ethernet/boost_1_71_0
    ```

##### 可选
```bash
# 编译文档

sudo apt install -y asciidoc source-highlight doxygen graphviz

# pkg-config 配合make install
# Return metainformation about installed libraries

sudo apt install -y pkg-config
```

### 编译&安装

``` bash
cd vsomeip-3.1.20/
mkdir build;cd build;

# 默认配置
cmake ..

##  自定义
# install path
cmake -DCMAKE_INSTALL_PREFIX:PATH=$YOUR_PATH ..
# ip addr
cmake -DUNICAST_ADDRESS=<YOUR IP ADDRESS> ..
# diagnosis addr
cmake -DDIAGNOSIS_ADDRESS=<YOUR DIAGNOSIS ADDRESS> ..
# configuration folder
cmake -DDEFAULT_CONFIGURATION_FOLDER=<DEFAULT CONFIGURATION FOLDER> ..
# default configuration file
cmake -DDEFAULT_CONFIGURATION_FILE=<DEFAULT CONFIGURATION FILE> ..
# signal handling
cmake -DENABLE_SIGNAL_HANDLING=1 ..

make

sudo make install

# tool: vsomeip_ctrl
make vsomeip_ctrl
```

## 3. 核心内容

### 3.1 模块
自上而下来看可以划分为以下:

* runtime

* application

* messgae

* payload


#### __runtime__

![runtime](../imgs/vSOMEIP_source_runtime.png)

上图为runtime 类在代码中与其他类的关系.

这个类主要用于创建和管理其他所有公共资源和获取runtime属性。
管理的资源包括:

- application

- message

- payload

主要的功能函数:

* get
  - `runtime`
  - `application`

* set/get_property:
  - `map<string, string>`

* create_xxx
  - `application`
  - `message`
  - `request`
  - `response`
  - `notification`
  - `payload`

* remove_application


#### __application__

__最核心的一个部分__

每个客户端都存在且仅存在一份。  
Application可以通过Runtime的接口来实例化。  
管理着vSomeIP客户端的生命周期和生命周期内的所有通讯。

管理的资源:

- plugin
- configuration
- routing
- endpoint
- security
- connector

##### 函数实现:

自身状态管理:
- init
- start
- stop
- process
- is_available 
- are_available 
- is_routing

属性:
- get_name
- get_client
- get_diagnosis
- get_security_mode
- get_offered_services_async 
- get_sd_acceptance_required
- set_routing_state
- set_sd_acceptance_required 
- set_sd_acceptance_required

handler 类(调用client 传入的函数):

- register_state_handler
- unregister_state_handler

- register_message_handler 
- unregister_message_handler 

- register_availability_handler
- unregister_availability_handler 

- register_subscription_handler 
- register_async_subscription_handler
- register_subscription_status_handler 
- unregister_subscription_status_handler
- unregister_subscription_handler 

- register_routing_ready_handler 
- register_routing_state_handler 

- clear_all_handler 

- register_sd_acceptance_handler 

- register_reboot_notification_handler 

- set_watchdog_handler 


消息服务类:
- update_service_configuration 
- update_security_policy_configuration
- remove_security_policy_configuration 

- offer_service 
- stop_offer_service

- offer_event 
- stop_offer_event

- request_service 
- release_service

- request_event 
- release_event 

- subscribe
- unsubscribe

- send 
- notify 
- notify_one 


#### __messgae & payload__

![msg_arch](../imgs/vSOMEIP_source_messages_arch.png)

message & payload 模块与其他模块之间的交互;
主要负责 `set/get` 相关的属性(session, payload, id...), (反)序列化功能.

由以下 `.cpp` 文件实现功能:

* message_base_impl.cpp
* message_header_impl.cpp
* message_impl.cpp
* payload_impl.cpp

