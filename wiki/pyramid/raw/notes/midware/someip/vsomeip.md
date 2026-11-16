
# vSOMEIP 入门

## 简介和概述

### 什么是 vSOMEIP

vSOMEIP 是 GENIVI 项目中的一个 SOME/IP 开源实现，基于 Mozilla Public License v2.0 协议开源，由 BMW 贡献。

vSOMEIP 提供了两个动态库：
* **SOME/IP协议的实现库** `libvsomeip.so`
* **用于服务发现的库** `libvsomeip-sd.so`

### 主要特性

* 支持设备之间的 SOME/IP 通讯
* 支持设备本地的进程间通讯（通过 unix socket 完成）
* 基于 boost.asio 的异步 IO 库实现
* 通过 Routing Manager 统一管理服务发现和外部通讯 socket
* 支持 JSON 配置文件进行配置管理

### 通讯架构

vSOMEIP 应用通过一个 **Routing Manager** 与其他设备进行通讯：
- Routing Manager 统一负责服务发现以及外部通讯 socket 的管理
- 一个设备上的多个 vSOMEIP 应用共用一个 Routing Manager
- 默认第一个启动的 vSOMEIP 应用负责启动 Routing Manager
- 其他应用通过 proxy 与 Routing Manager 进行通讯

vSOMEIP 应用可以通过 JSON 文件来进行配置，配置项包含：自身IP，应用名字，负责启动 Routing Manager 的应用，应用日志，服务发现的广播地址，广播间隔等。

### 内容目录

1. 源码结构
2. 环境和编译
3. 核心模块
4. 实现细节
5. 配置管理
6. 高级主题



```bash
-----------------------           -----------------------
|  upper applications |   <---->  |  someip-service     |  
|                     |           |                     |  
-----------------------           -----------------------
       |       /|\                   / /\ 
      \|/       |                  \/ /
--------------------------------------
|  COMMON-API   |  COMMONAPI         |  ---> commonapi-core-generator-<platform>-<arch>
|  (gen-code)   |  common part (.so) |
--------------------------------------
|  COMMON-SOMEIP RT                  |  ---> commonapi-someip-generator-<platform>-<arch>
--------------------------------------
       |       /|\ 
      \|/       |
---------------------
|    vsomeip         |
---------------------
|    TCP/IP          |
---------------------

```

### 代码分层结构

vSOMEIP 的代码主要分成如下四大部分：

* **daemon** - 守护进程
* **implementation** - 具体实现
* **interface** - 接口定义
  - runtime
  - application
  - message
  - payload
* **tool & examples** - 工具和示例

---

## 1. 源码结构

```bash
yshi10@dev:~/someip_space/vsomeip$ tree . -L 1
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
├── tools                --> someip_ctrl 工具
├── vsomeip3Config.cmake.in            --|
├── vsomeip3ConfigVersion.cmake.in       |
├── vsomeip3.pc.in                       |
├── vsomeipConfig.cmake.in               | ==> cmake 配置
├── vsomeipConfigVersion.cmake.in        |
├── vsomeip.pc.in                        |
└── vsomeip.xml                        --|
```

> 代码实现都在 `implementation` 下

### implementation


![arch](../../resources/imgs/tcpip/someip/00_overview_source_arch.png)

#### `impelemention`:
```bash
yshi10@dev:~/someip_space/vsomeip/implementation$ tree . -L 1
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
yshi10@dev:~$ lsb_release -a
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 21.10
Release:	21.10
Codename:	impish
```

> 实测 18.04, 20.04, 20.10 都没有问题, 官方推荐12.04 及以上, 最新的21.10 上 boost v1.71 与 最新的 glibc v2.34 不兼容, 同步了 boost v1.78 的变更解决这个问题

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

  __必需支持 C++11__ 

* boost 1.71 (1.55 ~ 1.74)

  1.71 刚好和 DoIP boost版本保持一致
  - repo:(master branch) 

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

```bash
cd vsomeip-3.1.20/
mkdir build;cd build;

# 默认配置
cmake ..

##  自定义的CMake配置

#### DCMAKE_INSTALL_PREFIX
安装位置
```bash
cmake -DCMAKE_INSTALL_PREFIX:PATH=$YOUR_PATH ..
```

#### DBASE_PATH
创建 local sockets 位置，默认为 `/tmp/vsomeip*`
```bash
cmake -DBASE_PATH=<YOUR BASE PATH> ..
```

#### DUNICAST_ADDRESS
组播 address
```bash
cmake -DUNICAST_ADDRESS=<YOUR IP ADDRESS> ..
```

#### DDIAGNOSIS_ADDRESS
诊断 address，默认为 `0x01`
```bash
cmake -DDIAGNOSIS_ADDRESS=<YOUR DIAGNOSIS ADDRESS> ..
```

#### DDEFAULT_CONFIGURATION_FOLDER
配置文件目录，默认为 `/etc/vsomeip`
```bash
cmake -DDEFAULT_CONFIGURATION_FOLDER=<DEFAULT CONFIGURATION FOLDER> ..
```

#### DDEFAULT_CONFIGURATION_FILE
默认配置文件，默认为 `/etc/vsomeip.json`
```bash
cmake -DDEFAULT_CONFIGURATION_FILE=<DEFAULT CONFIGURATION FILE> ..
```

#### DENABLE_SIGNAL_HANDLING
开启 signal handling
```bash
cmake -DENABLE_SIGNAL_HANDLING=1 ..
```

#### DROUTING_READY_MESSAGE
自定义完成 IP routing 后的通知消息
```bash
cmake -DROUTING_READY_MESSAGE=<YOUR MESSAGE> ..
```

#### VSOMEIP_APPLICATION_NAME
通过环境变量定义启动的程序名字
```bash
export VSOMEIP_APPLICATION_NAME=my_vsomeip_client \
export VSOMEIP_CONFIGURATION=my_settings.json \
./my_vsomeip_application
```

```bash
make

sudo make install

# tool: vsomeip_ctrl
make vsomeip_ctrl
```

## 3. 核心模块

vSOMEIP 整体设计是 模块化,设计了插件机制,自上而下来看可以简化为以下:

```bash
------------------------------
| Application                 |
------------------------------
       |       /|\ 
      \|/       |
------------------------------
| runtime       |            |
----------------|     SD     |
| application   | -----------|
----------------|     CFG    |
| messgae       | ---------  |
----------------|   Plugin   |
|  payload      |            |
------------------------------
```

### examples

__client__ 
```cpp
static vsomeip::service_t service_id = 0x1111;
static vsomeip::instance_t service_instance_id = 0x2222;
static vsomeip::method_t service_method_id = 0x3333;

class hello_world_client {
public:
    // Get the vSomeIP runtime and
    // create a application via the runtime, we could pass the application name
    // here otherwise the name supplied via the VSOMEIP_APPLICATION_NAME
    // environment variable is used
    hello_world_client() :
                    rtm_(vsomeip::runtime::get()),
                    app_(rtm_->create_application())
    {
    }

    bool init(){
        // init the application
        if (!app_->init()) {
            LOG_ERR ("Couldn't initialize application");
            return false;
        }

        // register a state handler to get called back after registration at the
        // runtime was successful
        app_->register_state_handler(
                std::bind(&hello_world_client::on_state_cbk, this,
                        std::placeholders::_1));

        // register a callback for responses from the service
        app_->register_message_handler(vsomeip::ANY_SERVICE,
                service_instance_id, vsomeip::ANY_METHOD,
                std::bind(&hello_world_client::on_message_cbk, this,
                        std::placeholders::_1));

        // register a callback which is called as soon as the service is available
        app_->register_availability_handler(service_id, service_instance_id,
                std::bind(&hello_world_client::on_availability_cbk, this,
                        std::placeholders::_1, std::placeholders::_2,
                        std::placeholders::_3));
        return true;
    }

    void start()
    {
        // start the application and wait for the on_event callback to be called
        // this method only returns when app_->stop() is called
        app_->start();
    }

    void on_state_cbk(vsomeip::state_type_e _state)
    {
        if(_state == vsomeip::state_type_e::ST_REGISTERED)
        {
            // we are registered at the runtime now we can request the service
            // and wait for the on_availability callback to be called
            app_->request_service(service_id, service_instance_id);
        }
    }

    void on_availability_cbk(vsomeip::service_t _service,
            vsomeip::instance_t _instance, bool _is_available)
    {
        // Check if the available service is the the hello world service
        if(service_id == _service && service_instance_id == _instance
                && _is_available)
        {
            // The service is available then we send the request
            // Create a new request
            std::shared_ptr<vsomeip::message> rq = rtm_->create_request();
            // Set the hello world service as target of the request
            rq->set_service(service_id);
            rq->set_instance(service_instance_id);
            rq->set_method(service_method_id);

            // Create a payload which will be sent to the service
            std::shared_ptr<vsomeip::payload> pl = rtm_->create_payload();
            std::string str("World");
            std::vector<vsomeip::byte_t> pl_data(std::begin(str), std::end(str));

            pl->set_data(pl_data);
            rq->set_payload(pl);
            // Send the request to the service. Response will be delivered to the
            // registered message handler
            LOG_INF("Sending: %s", str.c_str());
            app_->send(rq);
        }
    }

    void on_message_cbk(const std::shared_ptr<vsomeip::message> &_response)
    {
        if(service_id == _response->get_service()
                && service_instance_id == _response->get_instance()
                && vsomeip::message_type_e::MT_RESPONSE
                        == _response->get_message_type()
                && vsomeip::return_code_e::E_OK == _response->get_return_code())
        {
            // Get the payload and print it
            std::shared_ptr<vsomeip::payload> pl = _response->get_payload();
            std::string resp = std::string(
                    reinterpret_cast<const char*>(pl->get_data()), 0,
                    pl->get_length());
            LOG_INF("Received: %s", resp.c_str());
            stop();
        }
    }

    void stop()
    {
        // unregister the state handler
        app_->unregister_state_handler();
        // unregister the message handler
        app_->unregister_message_handler(vsomeip::ANY_SERVICE,
                service_instance_id, vsomeip::ANY_METHOD);
        // alternatively unregister all registered handlers at once
        app_->clear_all_handler();
        // release the service
        app_->release_service(service_id, service_instance_id);
        // shutdown the application
        app_->stop();
    }

private:
    std::shared_ptr<vsomeip::runtime> rtm_;
    std::shared_ptr<vsomeip::application> app_;
};

```

__server__
```cpp
static vsomeip::service_t service_id = 0x1111;
static vsomeip::instance_t service_instance_id = 0x2222;
static vsomeip::method_t service_method_id = 0x3333;

class hello_world_service {
public:
    // Get the vSomeIP runtime and
    // create a application via the runtime, we could pass the application name
    // here otherwise the name supplied via the VSOMEIP_APPLICATION_NAME
    // environment variable is used
    hello_world_service() :
                    rtm_(vsomeip::runtime::get()),
                    app_(rtm_->create_application()),
                    stop_(false),
                    stop_thread_(std::bind(&hello_world_service::stop, this))
    {
    }

    ~hello_world_service()
    {
        stop_thread_.join();
    }

    bool init()
    {
        // init the application
        if (!app_->init()) {
            LOG_ERR("Couldn't initialize application");
            return false;
        }

        // register a message handler callback for messages sent to our service
        app_->register_message_handler(service_id, service_instance_id,
                service_method_id,
                std::bind(&hello_world_service::on_message_cbk, this,
                        std::placeholders::_1));

        // register a state handler to get called back after registration at the
        // runtime was successful
        app_->register_state_handler(
                std::bind(&hello_world_service::on_state_cbk, this,
                        std::placeholders::_1));
        return true;
    }

    void start()
    {
        // start the application and wait for the on_event callback to be called
        // this method only returns when app_->stop() is called
        app_->start();
    }

    void stop()
    {
        std::unique_lock<std::mutex> its_lock(mutex_);
        while(!stop_) {
            condition_.wait(its_lock);
        }
        std::this_thread::sleep_for(std::chrono::seconds(5));
        // Stop offering the service
        app_->stop_offer_service(service_id, service_instance_id);
        // unregister the state handler
        app_->unregister_state_handler();
        // unregister the message handler
        app_->unregister_message_handler(service_id, service_instance_id,
                service_method_id);
        // shutdown the application
        app_->stop();
    }

    void terminate() {
        std::lock_guard<std::mutex> its_lock(mutex_);
        stop_ = true;
        condition_.notify_one();
    }

    void on_state_cbk(vsomeip::state_type_e _state)
    {
        if(_state == vsomeip::state_type_e::ST_REGISTERED)
        {
            // we are registered at the runtime and can offer our service
            app_->offer_service(service_id, service_instance_id);
        }
    }

    void on_message_cbk(const std::shared_ptr<vsomeip::message> &_request)
    {
        // Create a response based upon the request
        std::shared_ptr<vsomeip::message> resp = rtm_->create_response(_request);

        // Construct string to send back
        std::string str("Hello ");
        str.append(
                reinterpret_cast<const char*>(_request->get_payload()->get_data()),
                0, _request->get_payload()->get_length());

        // Create a payload which will be sent back to the client
        std::shared_ptr<vsomeip::payload> resp_pl = rtm_->create_payload();
        std::vector<vsomeip::byte_t> pl_data(str.begin(), str.end());
        resp_pl->set_data(pl_data);
        resp->set_payload(resp_pl);

        // Send the response back
        app_->send(resp);
        // we have finished
        terminate();
    }

private:
    std::shared_ptr<vsomeip::runtime> rtm_;
    std::shared_ptr<vsomeip::application> app_;
    bool stop_;
    std::mutex mutex_;
    std::condition_variable condition_;
    std::thread stop_thread_;
};

```


```
### Plugin 系统

#### Plugin 管理

vSOMEIP 允许 Application 加载一到多个 Plugin。
当 Application 的状态发生变化时，这个变化会被通知到 Plugin。
在通知的时候会附带 Application 的名称，用于 Plugin 进行区别对待。

Application 的状态有三种，分别为：
* **Initialized** - 初始化完成
* **Started** - 已启动  
* **Stopped** - 已停止

#### Plugin 功能函数

装卸载插件, 加载库和导入符号表

* get_plugin
* load_plugin
* load_library
* load_symbol
* add_plugin
* unload_plugin


### __runtime__

![runtime](../../resources/imgs/tcpip/someip/vsomeip_source_runtime.png)

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


### __application__

__最核心的一个部分__

每个客户端都存在且仅存在一份。  
`Application` 可以通过 `Runtime` 的接口来实例化。  
管理着vSomeIP客户端的生命周期和生命周期内的所有通讯。  

管理的资源:

- plugin
- configuration
- routing
- endpoint
- security
- connector

#### 函数实现:

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


### __message & payload__

![msg_arch](../../resources/imgs/tcpip/someip/vsomeip_source_messages_arch.png)

#### Message 类型

无论是 Request、Response 还是 Notification，本质上都是一种 Message。

从某种意义上来说，Message 可以分成两类：
- **通用 Message** - 普通的业务消息
- **服务发现相关的 Message** - SD 相关消息

#### 功能说明

Message & Payload 模块与其他模块之间的交互，主要负责：
- `set/get` 相关的属性(session, payload, id...)
- (反)序列化功能

Message 类提供了编串和解串功能，用于进行数据通讯，本质上它封装了 SOME/IP 的消息头。
所以，它还提供了一系列方法来设置或者读取详细的消息头信息。

#### Payload

Message 的主体。也就是排除消息头之后剩下的部分。

#### 实现文件

由以下 `.cpp` 文件实现功能:

* message_base_impl.cpp
* message_header_impl.cpp
* message_impl.cpp
* payload_impl.cpp

### __endpoint__

![ep](../../resources/imgs/tcpip/someip/vsomeip_endpoint.png)

#### Endpoint 分类

每个具有 vSOMEIP 功能的进程都是一个 Endpoint。
Endpoint 分成六大类：

##### Client Endpoints
- **local-client** - 本地客户端
- **udp-client** - UDP 客户端
- **tcp-client** - TCP 客户端

##### Server Endpoints
- **local-server** - 本地服务端
- **udp-server** - UDP 服务端
- **tcp-server** - TCP 服务端

#### 实现结构

按功能分成如下:

##### Client 实现
base: client_endpoint_impl.cpp
- remote (udp/tcp): udp/tcp_client_endpoint_impl.cpp
- local(Unix Domain): local_client_endpoint_impl.cpp

##### Server 实现
base: server_endpoint_impl.cpp
- remote (udp/tcp): udp/tcp_server_endpoint_impl.cpp
- local(Unix Domain): server_client_endpoint_impl.cpp

#### 以`local_client_endpoint_impl` 为例子

`endpoint` 是所有vsomeip通讯实例的基础.

> `endpoint`的生命周期其实就是一个“连接”的生命周期。

* start

code: 

```cpp
void local_client_endpoint_impl::start() {
    connect();
}
```

`start()`函数中会根据`endpoint`的类型创建一个socket链接, 并且开始触发第一次消息接收。
如果在连接建立起来之前，就已经有消息被放入队列中了。那么，在连接成功之后，会将队列中缓存的消息逐一发出。也就是说，vsomeip对于服务端和客户端启动的先后顺序没有强制要求.

> 在实际 connect() 中 对 socket连接都开启了 `reuse_address`

* connect

1. open socket (set asio::socket_base::reuse_address(true))

2. state = CONNECTING

3.  connect

4. call connect_cbk() (async)

* send

插入数据到一个`buffer`中, 然后设置标志位(判断当前`queue`大小) `void client_endpoint_impl<Protocol>::queue_train` 调用`send_queued()`

> 这里的`queue`数据类型: deque<std::shared_ptr<std::vector<uint8_t> > >

* send_queued

通过 `asio::async_write()` 将数据写入socket然后调用`client_endpoint_impl::send_cbk`


* receive

具体实现如下: 
```cpp
void local_client_endpoint_impl::receive() {
    std::lock_guard<std::mutex> its_lock(socket_mutex_);
    if (socket_->is_open()) {
        socket_->async_receive(
            boost::asio::buffer(recv_buffer_),
            strand_.wrap(
                std::bind(
                    &local_client_endpoint_impl::receive_cbk,
                    std::dynamic_pointer_cast<
                        local_client_endpoint_impl
                    >(shared_from_this()),
                    std::placeholders::_1,
                    std::placeholders::_2
                )
            )
        );
    }
}
```
通过asio的 `async_receive()`接受 `receive_cbk()`的方式,接受数据.

* restart

```cpp
# 设置如下属性
state_ = cei_state_e::CONNECTING;
sending_blocked_ = false;
was_not_connected_ = true;
reconnect_counter_ = 0;

# 调用如下函数
queue_.clear();
shutdown_and_close_socket_unlocked(true);
start_connect_timer();
```

* stop

```cpp
# 1. reset CONNECT_TIMEOUT
connect_timer_.cancel(ec);
connect_timeout_ = VSOMEIP_DEFAULT_CONNECT_TIMEOUT;

# 2. check socket open or not
# if open go to 3 else go to 4
is_open = socket_->is_open();

# 3. check queue empty or not
# 3.1 if empty, go to 4
# 3.2 else 
std::this_thread::sleep_for(std::chrono::milliseconds(10));
times_slept++;

# 4 shutdown
shutdown_and_close_socket(false);

```

##### manager

manager 的本质是 __增删查__

* 增
  - create_local_server
  - create_remote_client
  - create_client_endpoint
  - add_remote_service_info

* 删
  - remove_instance
  - remove_instance_multicast
  - release_port


* 查
  - find_instance
  - find_instance_multicast
  - find_remote_client
  - on_connect
  - on_disconnect

* helper
  - log_client_states
  - log_server_states
  - on_error
  - print_status
  - is_remote_service_known


##### netlink

监控了如下消息:
* RTMGRP_LINK
* RTMGRP_IPV4_IFADDR
* RTMGRP_IPV6_IFADDR 
* RTMGRP_IPV4_ROUTE 
* RTMGRP_IPV6_ROUTE 
* RTMGRP_IPV4_MROUTE
* RTMGRP_IPV6_MROUTE


##### TP
  - tp.cpp
  - tp_message.cpp
  - tp_reassembler.cpp

* tp.cpp

定义最大的分片

```cpp
const std::uint16_t tp::tp_max_segment_length_ = 1392;
```

分片函数:
```cpp
tp_split_messages_t tp::tp_split_message(const std::uint8_t * const _data, std::uint32_t _size)
```







>TODO
---
### __routing__

#### Routing 概述

每个系统中只能有一个 vSOMEIP 服务被配置成 Routing。

如果没有特别的设定，那么系统中被运行的第一个具备 vSOMEIP 功能的程序会被作为 Routing Manager。

#### Routing 组件

* event
* eventgroupinfo
* remote_subscription
* serviceinfo
* manager

#### Routing 生命周期

##### 初始化
![](../../resources/imgs/tcpip/someip/vsomeip_source_routing_init.png)

##### 启动过程
![](../../resources/imgs/tcpip/someip/vsomeip_source_routing_start.png)


### __service discovery__

#### 服务发现理论基础

##### 基本流程

服务发现机制包含三个核心流程：

* **Register** - 服务启动时候进行注册
* **Query** - 查询已注册服务信息  
* **Healthy Check** - 确认服务状态是否健康

整个过程很简单。大致就是在服务启动的时候，先去进行注册，并且定时反馈本身功能是否正常。由服务发现机制统一负责维护一份正确或者可用的服务清单。因此，服务本身需要能随时接受查询，反馈调用方服务所要的信息。

##### 注册模式

###### 自主注册模式
自主注册模式，由服务(client)本身来维护。每个服务启动后，需要到统一的服务注册中心进行注册登记，服务正常终止后，也可以到注册中心移除自身的注册记录。在服务执行过程中，通过不断的发送心跳信息，来通知注册中心，本服务运行正常。注册中心只要超过一定的时间没有收到心跳消息，就可以将这个服务状态判断为异常，进而移除该服务的注册记录。

###### 第三方注册模式  
这个模式与自主注册相比，区别是健康检查的动作不是由服务本身(client)来负责，而是由第三方服务来确认。因为有时候服务自身发送心跳信息的方式并不精确，因为可能服务本身已经存在故障，某些接口功能不可用，但仍然可以不断的发送心跳信息，导致注册中心没有发觉该服务已经异常，从而源源不断的将流量打到已经异常的服务上来。所以，确认服务是否正常运转的健康检查机制，就不能只依靠心跳，必须通过其它第三方的验证，不断的从外部来确认服务本身的健康状态。

##### 发现模式

服务发现机制主要包括三个角色：

* **服务提供者** - 服务启动时将服务信息注册到注册中心，服务退出时将注册中心的服务信息删除掉
* **服务消费者** - 从服务注册表获取服务提供者的最新网络位置等服务信息，维护与服务提供者之间的通信  
* **注册中心** - 服务提供者和服务消费者之间的桥梁

###### 客户端发现模式
首先要进行的是到服务注册中心获取服务列表，然后再根据调用端本地的负载均衡策略，进行服务调用：

1. 服务提供者向注册中心进行注册，提交自己的相关信息 (register)
2. 服务消费者定期从注册中心获取服务提供者列表 (keep alive)  
3. 服务消费者通过自身的负载均衡算法，在服务提供者列表里面选择一个合适的服务提供者，进行访问

###### 服务端发现模式
1. 服务提供者向注册中心进行服务注册
2. 注册中心提供负载均衡功能
3. 服务消费者去请求注册中心，由注册中心根据服务提供列表的健康情况，选择合适的服务提供者供服务消费者调用

> 本质区别在于，客户端是否保存服务列表信息

##### 实现方案对比

###### 文件方式 (SOME/IP 采用)
以文件的形式实现服务发现，这是一个比较简单的方案。其基本原理就是将服务提供者的信息(ip:port)写入文件中，服务消费者加载该文件，获取服务提供者的信息，根据一定的策略，进行访问。

**特点：**
* **优点** - 实现简单，去中心化
* **缺点** - 需要服务消费者去定时操作，如果某一个文件推送失败，那么就会造成异常现象

> **SOME/IP 就是通过文件的方式实现服务发现**

###### 其他第三方实现
* **zookeeper** - 分布式协调服务
* **redis** - 内存数据库方案  
* **etcd** - 分布式键值存储

#### vSOMEIP 服务发现实现

##### 初始化流程
```mermaid
graph TD;
    service_discovery_impl == init -.- 
    parse_confguration -.->
    service_discovery_imple;
```

##### 启动过程
```mermaid
graph TD;

service_discovery_impl
 == start 
 -.-> create_service_discovery_endpoint 
 -.-> create_server_endpoint 
 == join_sd_multicast
--> endpoint
```

---

## 配置管理

### JSON 配置详解

vSOMEIP 应用可以通过 JSON 文件来进行详细配置，主要配置项包含以下内容：

#### 网络配置

##### unicast
主机系统的 IP 地址。

##### netmask  
指定主机系统子网的网络掩码。

##### device
如果指定，IP endpoints 将绑定到此设备。

#### 诊断配置

##### diagnosis
用于构建客户端标识符的诊断地址（字节）。诊断地址被分配给所有客户端标识符的最高有效字节（除非另有指定，例如通过预定义的客户端 ID）。

##### diagnosis_mask
诊断掩码（2字节）用于控制 ECU 上允许的并发 vSOMEIP 客户端的最大数量和客户端 ID 的起始值。

默认值是 `0xFF00`，意味着客户端 ID 的最高有效字节保留给诊断地址，客户端 ID 将从指定的诊断地址开始。

客户端的最大数量是 255，因为反转掩码的汉明权重是 8（2^8 = 256 - 1（用于路由管理器）= 255）。例如，诊断地址为 0x45 的结果客户端 ID 范围将是 0x4501 到 0x45ff。

##### network
网络标识符，用于支持一台主机上的多个路由管理器。此设置更改 `/dev/shm` 中共享内存段的名称和 `/tmp/` 中 Unix 域套接字的名称。默认为 `vsomeip`，意味着共享内存将命名为 `/dev/shm/vsomeip`，Unix 域套接字将命名为 `/tmp/vsomeip-$CLIENTID`。

#### 日志配置 (logging)

##### level  
日志级别，支持 6 个等级：
- `trace` - 跟踪级别
- `debug` - 调试级别  
- `info` - 信息级别
- `warning` - 警告级别
- `error` - 错误级别
- `fatal` - 致命错误级别

##### console
控制日志输出到控制台的开启/关闭：
- `true` - 启用控制台输出
- `false` - 禁用控制台输出

##### file
文件日志配置：
- `enable` - 启用/禁用文件日志输出
  - `true` - 启用
  - `false` - 禁用
- `path` - 日志文件的绝对路径

##### memory_log_interval
配置路由管理器记录其使用内存的间隔（秒）。设置大于零的值将启用日志记录。

##### status_log_interval  
配置路由管理器记录其内部状态的间隔（秒）。设置大于零的值将启用日志记录。

#### 跟踪配置 (Tracing)

##### enable
启用/禁用跟踪功能。

##### sd_enable
启用/禁用服务发现跟踪。

##### channels
跟踪通道配置：
- `name` - 通道名称
- `id` - 通道标识符

#### 应用配置 (Applications)

##### name
应用程序名称。

##### id  
应用程序标识符。

##### max_dispatchers
最大调度器数量。

##### max_dispatch_time
最大调度时间。

##### threads
线程数量。

##### io_thread_nice
IO 线程优先级。

##### request_debounce_time
请求防抖时间。

### 配置示例

```json
{
    "unicast": "192.168.1.100",
    "netmask": "255.255.255.0",
    "diagnosis": "0x01",
    "diagnosis_mask": "0xFF00",
    "logging": {
        "level": "info",
        "console": "true",
        "file": {
            "enable": "true",
            "path": "/var/log/vsomeip.log"
        },
        "memory_log_interval": 10,
        "status_log_interval": 60
    },
    "tracing": {
        "enable": "true",
        "sd_enable": "true",
        "channels": [
            {
                "name": "service_discovery",
                "id": "SD"
            }
        ]
    },
    "applications": [
        {
            "name": "my_service",
            "id": "0x1234",
            "max_dispatchers": 2,
            "max_dispatch_time": 100,
            "threads": 1,
            "io_thread_nice": 0,
            "request_debounce_time": 10
        }
    ]
}
```

---

## 高级主题

### Daemon 架构

#### Daemon 概述

daemon 的主体就是一个 `vsomeip::application`

![](../../resources/imgs/tcpip/someip/vsomeip_source_daemon.png)

#### Daemon vs Application

Application 创建了一个 `routing_manager_impl` 的实例。
如果这不是 Daemon，而是一个通常的 Application，那么它会转而创建 `routing_manager_proxy` 的实例，并与找到的 Routing Manager 建立连接。

### Tools & Examples

一些简易的 Application，用于进行一些消息发送接收的测试工作。

---

## 参考资料

* [vSOMEIP Blog Reference](https://blog.zeerd.com/vsomeip-1st/)
* [GENIVI Project](https://www.genivi.org/)
* [SOME/IP Protocol Documentation](https://some-ip.com/)

---

*文档最后更新: 2021-12-20*



