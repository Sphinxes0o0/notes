---
title: 'someip-01: code'
date: 2021-12-21 18:07:15
tags:
    - someip
    - vSOMEIP
---

# vSOMEIP 01:  source code

source code reading

## Start from CMakeLists.txt

### Dependencies

* C++11, gcc > 5.2
* Boost > 1.55

### Configuration

#### DCMAKE_INSTALL_PREFIX
安装位置
```bash
cmake -DCMAKE_INSTALL_PREFIX:PATH=$YOUR_PATH ..
```

#### DBASE_PATH
创建local sockets 位置, 默认为 `/tmp/vsomeip*`

```bash
cmake -DBASE_PATH=<YOUR BASE PATH> ..
```

#### DUNICAST_ADDRESS
组播 address

```bash
cmake -DUNICAST_ADDRESS=<YOUR IP ADDRESS> ..
```


#### DDIAGNOSIS_ADDRESS
诊断 address

默认为`0x01`

```bash
cmake -DDIAGNOSIS_ADDRESS=<YOUR DIAGNOSIS ADDRESS> ..
```

#### DDEFAULT_CONFIGURATION_FOLDER
配置文件目录

```bash
cmake -DDEFAULT_CONFIGURATION_FOLDER=<DEFAULT CONFIGURATION FOLDER> ..
```

默认为 `/etc/vsomeip`

#### DDEFAULT_CONFIGURATION_FILE

```bash
cmake -DDEFAULT_CONFIGURATION_FILE=<DEFAULT CONFIGURATION FILE> ..
```

默认为 `/etc/vsomeip.json`

#### DENABLE_SIGNAL_HANDLING

开启 signal handling

```bash
cmake -DENABLE_SIGNAL_HANDLING=1 ..
```

#### DROUTING_READY_MESSAGE

自定义 完成 ip routing 后的通知消息

```bash
cmake -DROUTING_READY_MESSAGE=<YOUR MESSAGE> ..
```

#### VSOMEIP_APPLICATION_NAME

通过环境变量 定义启动的程序名字

```bash
export VSOMEIP_APPLICATION_NAME=my_vsomeip_client \
export VSOMEIP_CONFIGURATION=my_settings.json \
./my_vsomeip_application
```


#### json 配置

* unicast

    The IP address of the host system.

* netmask

    The netmask to specify the subnet of the host system.

* device

    If specified, IP endpoints will be bound to this device.


* diagnosis

    The diagnosis address (byte) that will be used to build client identifiers. The
    diagnosis address is assigned to the most significant byte in all client
    identifiers if not specified otherwise (for example through a predefined client
    ID).

* diagnosis_mask

    The diagnosis mask (2 byte) is used to control the maximum amount of allowed
    concurrent vsomeip clients on an ECU and the start value of the client IDs.

    The default value is `0xFF00` meaning the most significant byte of the client ID 
    is reserved for the diagnosis address and 
    the client IDs will start with the diagnosis address as specified.

    The maximum number of clients is 255 as the Hamming weight of the inverted mask
    is 8 (2^8 = 256 - 1 (for the routing manager) = 255). The resulting client ID
    range with a diagnosis address of for example 0x45 would be 0x4501 to 0x45ff.

* network

    Network identifier used to support multiple routing managers on one host. This
    setting changes the name of the shared memory segment in `/dev/shm` and the name
    of the unix domain sockets in `/tmp/`. Defaults to `vsomeip` meaning the shared
    memory will be named `/dev/shm/vsomeip` and the unix domain sockets will be
    named `/tmp/vsomeip-$CLIENTID`

* __logging__

* level
    - trace
    - debug
    - info
    - warning
    - error
    - fatal

    6个等级
    


* console
    - true
    - false

    log 输出到console的开启/关闭

* file
    - enable
        - true
        - false
    - path

    log 输出到console的开启/关闭  
    path: The absolute path of the log file

* memory_log_interval  
    Configures interval in seconds in which the routing manager logs its used
    memory. Setting a value greater than zero enables the logging.

* status_log_interval
    Configures interval in seconds in which the routing manager logs its internal
    status.
    Setting a value greater than zero enables the logging.


* __Tracing__

    - enable

    - sd_enable

    - channels
        - name
        - id

* __Applications__

    - name
    - id
    - max_dispatchers
    - max_dispatch_time
    - threads
    - io_thread_nice
    - request_debounce_time









### Source Code Arch
```bash
├── config
├── documentation
├── examples
│   ├── hello_world
│   └── routingmanagerd
├── implementation ---> 具体的代码实现逻辑
│   ├── compat     ---> vSOMEIP 兼容
│   │   ├── message
│   │   │   ├── include
│   │   │   └── src
│   │   └── runtime
│   │       ├── include
│   │       └── src
│   ├── configuration   ---> 配置
│   │   ├── include
│   │   └── src
│   ├── e2e_protection
│   ├── endpoints       ---> 具有vSOMEIP功能的进程
│   │   ├── include
│   │   └── src
│   ├── helper          ---> boost版本兼容
│   │   ├── 1.55
│   │   ├── 1.66
│   │   ├── 1.70
│   │   └── 1.74
│   ├── logger
│   │   ├── include
│   │   └── src
│   ├── message
│   │   ├── include
│   │   └── src
│   ├── plugin
│   │   ├── include
│   │   └── src
│   ├── routing      ---> 每个系统中只能有一个vSomeIP服务被配置成Routing
│   │   ├── include
│   │   └── src
│   ├── runtime       ---> 管理公共资源和获取runtime属性
│   │   ├── include
│   │   └── src
│   ├── security
│   │   ├── include
│   │   └── src
│   ├── service_discovery
│   │   ├── include
│   │   └── src
│   ├── tracing
│   │   ├── include
│   │   └── src
│   └── utility
│       ├── include
│       └── src
├── interface
│   ├── compat
│   │   └── vsomeip
│   │       ├── internal
│   │       └── plugins
│   └── vsomeip
│       ├── internal
│       └── plugins
├── test
└── tools
```

* Configuration lib
    - implementation
        - configuration

* Base (Core) lib
    - implementation
        - __endpoingts__
        - __message__
        - __routing__
        - __runtime__
        - __service_discovery__


