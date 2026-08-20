---
title: "Snort3 连接器与侧信道 (Connectors & Side Channel)"
description: "连接器和侧信道模块提供了Snort3与外部系统之间的通信机制,支持高可用性伙伴通信、数据包处理线程间的带外通信等场景。"
---
# Snort3 连接器与侧信道 (Connectors & Side Channel)

连接器和侧信道模块提供了Snort3与外部系统之间的通信机制,支持高可用性伙伴通信、数据包处理线程间的带外通信等场景。

## 1. 概述

**代码规模**:
- `connectors/`: 约 6,151 行代码
- `side_channel/`: 约 1,537 行代码

**模块列表**:

| 模块 | 描述 |
|------|------|
| `connectors/` | 连接器框架与实现 |
| `tcp_connector/` | TCP连接器 |
| `file_connector/` | 文件连接器 |
| `unixdomain_connector/` | Unix Domain Socket连接器 |
| `side_channel/` | 侧信道框架 |

## 2. 连接器框架 (Connector Framework)

### 2.1 基类: Connector

连接器是Snort3中用于线程间或进程间通信的抽象接口。

```cpp
class SO_PUBLIC Connector
{
public:
    enum Direction
    {
        CONN_UNDEFINED,
        CONN_RECEIVE,
        CONN_TRANSMIT,
        CONN_DUPLEX
    };

    using ID = std::variant<const char*, int>;

    Connector(const ConnectorConfig& config) : config(config) { }
    virtual ~Connector() = default;

    virtual const ID get_id(const char*) const { return null; }

    virtual ConnectorMsg allocate_connector_message(uint32_t length)
    {
        const uint8_t* data = new uint8_t[length];
        return ConnectorMsg(data, length, true);
    }

    virtual bool transmit_message(const ConnectorMsg&, const ID& = null) = 0;
    virtual bool transmit_message(const ConnectorMsg&&, const ID& = null) = 0;
    virtual ConnectorMsg receive_message(bool block) = 0;
    virtual bool flush() { return true; }
    virtual void reinit() { }

protected:
    const ConnectorConfig& config;
    static constexpr ID null {nullptr};
};
```

### 2.2 ConnectorMsg 消息类

```cpp
class ConnectorMsg
{
public:
    ConnectorMsg() = default;

    ConnectorMsg(const uint8_t* data, uint32_t length,
        bool pass_ownership = false, uint32_t content_offset = 0) :
        data(data), content(const_cast<uint8_t*>(data) + content_offset),
        length(length), owns(pass_ownership)
    { }

    ~ConnectorMsg()
    { if (owns) delete[] data; }

    // 移动语义支持
    ConnectorMsg(ConnectorMsg&& other) :
        data(other.data), content(other.content), length(other.length), owns(other.owns)
    { other.owns = false; }

    const uint8_t* get_data() const { return data; }
    uint8_t* get_content() const { return content; }
    uint32_t get_length() const { return length; }

private:
    const uint8_t* data = nullptr;
    uint8_t* content = nullptr;
    uint32_t length = 0;
    bool owns = false;
};
```

## 3. TCP 连接器 (TcpConnector)

TCP连接器通过TCP Socket与其他Snort实例或外部系统通信。

### 3.1 TcpConnector 类

```cpp
class TcpConnector : public snort::Connector
{
public:
    TcpConnector(const TcpConnectorConfig&, int sock_fd);
    ~TcpConnector() override;

    bool transmit_message(const snort::ConnectorMsg&, const ID& = null) override;
    bool transmit_message(const snort::ConnectorMsg&&, const ID& = null) override;
    snort::ConnectorMsg receive_message(bool) override;

    void process_receive();

    int sock_fd;

private:
    typedef Ring<snort::ConnectorMsg*> ReceiveRing;

    void start_receive_thread();
    void stop_receive_thread();
    void receive_processing_thread();
    snort::ConnectorMsg* read_message();
    bool internal_transmit_message(const snort::ConnectorMsg&);

    std::atomic<bool> run_thread;
    std::thread* receive_thread;
    ReceiveRing* receive_ring;
};
```

### 3.2 消息格式

```cpp
class __attribute__((__packed__)) TcpConnectorMsgHdr
{
public:
    TcpConnectorMsgHdr() : version(0), connector_msg_length(0) { }
    TcpConnectorMsgHdr(uint32_t length)
    { version = TCP_FORMAT_VERSION; connector_msg_length = length; }

    uint8_t version;
    uint16_t connector_msg_length;
};
```

### 3.3 关键实现

```cpp
bool TcpConnector::transmit_message(const snort::ConnectorMsg& msg, const ID& id)
{
    TcpConnectorMsgHdr hdr(msg.get_length());

    // 发送头部
    ssize_t n = send(sock_fd, &hdr, sizeof(hdr), 0);
    if (n != sizeof(hdr))
        return false;

    // 发送数据
    n = send(sock_fd, msg.get_data(), msg.get_length(), 0);
    return (n == (ssize_t)msg.get_length());
}

snort::ConnectorMsg TcpConnector::receive_message(bool block)
{
    // 从接收环形缓冲区获取消息
    ReceiveRing* ring = receive_ring;
    if (!ring)
        return snort::ConnectorMsg();

    // 如果block则等待直到有数据
    return ring->get(block ? -1 : 0);
}
```

## 4. 文件连接器 (FileConnector)

文件连接器通过文件系统进行消息传递,适用于进程间不需要实时通信的场景。

### 4.1 FileConnector 类

```cpp
class FileConnector : public snort::Connector
{
public:
    FileConnector(const FileConnectorConfig& conf) : Connector(conf), cfg(conf) {}

    bool transmit_message(const snort::ConnectorMsg&, const ID& = null) override;
    bool transmit_message(const snort::ConnectorMsg&&, const ID& = null) override;
    snort::ConnectorMsg receive_message(bool) override;

    bool flush() override
    { file.flush(); return file.good(); }

    std::fstream file;

private:
    bool internal_transmit_message(const snort::ConnectorMsg&);
    snort::ConnectorMsg receive_message_binary();

    const FileConnectorConfig& cfg;
};
```

### 4.2 文件消息格式

```cpp
class __attribute__((__packed__)) FileConnectorMsgHdr
{
public:
    FileConnectorMsgHdr(uint32_t length)
    { version = FILE_FORMAT_VERSION; connector_msg_length = length; }

    uint16_t version;
    uint32_t connector_msg_length;
};
```

## 5. Unix Domain Socket 连接器

Unix Domain Socket连接器提供本地进程间的高速通信。

### 5.1 UnixDomainConnector 类

```cpp
class UnixDomainConnector : public snort::Connector
{
public:
    UnixDomainConnector(const UnixDomainConnectorConfig&, int sock_fd);
    ~UnixDomainConnector() override;

    bool transmit_message(const snort::ConnectorMsg&, const ID& = null) override;
    bool transmit_message(const snort::ConnectorMsg&&, const ID& = null) override;
    snort::ConnectorMsg receive_message(bool) override;

private:
    // ...
    int sock_fd;
    std::thread* receive_thread;
    std::atomic<bool> run_thread;
};
```

## 6. 侧信道框架 (Side Channel)

侧信道提供了一种带外通信机制,用于Snort与外部系统(如高可用性伙伴)之间的消息传递。

### 6.1 SideChannel 类

```cpp
class SideChannel
{
public:
    SideChannel(ScMsgFormat);

    void register_receive_handler(const SCProcessMsgFunc& handler);
    void unregister_receive_handler();

    bool process(int max_messages);
    SCMessage* alloc_transmit_message(uint32_t content_length);
    bool discard_message(SCMessage* msg) const;
    bool transmit_message(SCMessage* msg) const;
    void set_default_port(SCPort port);
    snort::Connector::Direction get_direction();

    snort::Connector* connector_receive = nullptr;
    snort::Connector* connector_transmit = nullptr;

private:
    SCMsgHdr get_header();

    SCSequence sequence = 0;
    SCPort default_port = 0;
    SCProcessMsgFunc receive_handler = nullptr;
    ScMsgFormat msg_format;
};
```

### 6.2 消息格式

```cpp
struct __attribute__((__packed__)) SCMsgHdr
{
    uint16_t port = 0;
    uint16_t sequence = 0;
    uint32_t time_u_seconds = 0;
    uint64_t time_seconds = 0;
};

enum ScMsgFormat : uint8_t
{
    BINARY,
    TEXT
};

struct SCMessage
{
    SCMessage(const SideChannel* sc, const snort::Connector* conn,
        snort::ConnectorMsg&& cmsg) :
        sc(sc), connector(conn), cmsg(std::move(cmsg))
    {}

    const SideChannel* sc;
    const snort::Connector* connector;
    const snort::ConnectorMsg cmsg;
    uint8_t* content = nullptr;
    uint32_t content_length = 0;
};

typedef std::function<void(SCMessage*)> SCProcessMsgFunc;
```

### 6.3 SideChannelManager

```cpp
class SideChannelManager
{
public:
    // 实例化新的SideChannel配置
    static void instantiate(const SCConnectors* connectors,
        const PortBitSet* ports, ScMsgFormat fmt);

    // 主线程,配置前初始化
    static void pre_config_init();

    // 每个数据包线程启动时调用
    static void thread_init();

    // 每个数据包线程关闭时调用
    static void thread_term();

    // 总体关闭
    static void term();

    // 获取指定端口关联的SideChannel对象
    static SideChannel* get_side_channel(SCPort);

private:
    SideChannelManager() = delete;
};
```

### 6.4 核心函数实现

```cpp
bool SideChannel::process(int max_messages)
{
    int messages_processed = 0;

    while (messages_processed < max_messages || max_messages == DISPATCH_ALL_RECEIVE)
    {
        // 从连接器接收消息
        snort::ConnectorMsg msg = connector_receive->receive_message(false);

        if (msg.get_length() == 0)
            break;

        // 创建SCMessage并调用处理函数
        SCMessage* sc_msg = new SCMessage(this, connector_receive,
            std::move(msg));

        if (receive_handler)
            receive_handler(sc_msg);

        delete sc_msg;
        messages_processed++;
    }

    return (messages_processed > 0);
}

SCMessage* SideChannel::alloc_transmit_message(uint32_t content_length)
{
    // 分配包含头部和内容的传输消息
    uint32_t total_length = sizeof(SCMsgHdr) + content_length;
    snort::ConnectorMsg msg = connector_transmit->allocate_connector_message(
        total_length);

    return new SCMessage(this, connector_transmit, std::move(msg));
}
```

## 7. 文件清单与行数

### Connectors 模块

| 文件 | 行数 | 描述 |
|------|------|------|
| `connectors.h` | 25 | 连接器头文件 |
| `connectors.cc` | 42 | 连接器实现 |
| `tcp_connector/tcp_connector.h` | 79 | TCP连接器头文件 |
| `tcp_connector/tcp_connector.cc` | 12739 | TCP连接器实现 |
| `tcp_connector/tcp_connector_config.h` | ~50 | TCP配置 |
| `tcp_connector/tcp_connector_module.cc` | ~200 | TCP模块 |
| `file_connector/file_connector.h` | 68 | 文件连接器头文件 |
| `file_connector/file_connector.cc` | 6281 | 文件连接器实现 |
| `file_connector/file_connector_config.h` | ~50 | 文件配置 |
| `unixdomain_connector/unixdomain_connector.h` | ~141 | Unix域连接器 |
| `unixdomain_connector/unixdomain_connector.cc` | 775 | Unix域实现 |

### Side Channel 模块

| 文件 | 行数 | 描述 |
|------|------|------|
| `side_channel.h` | 120 | SideChannel头文件 |
| `side_channel.cc` | 339 | SideChannel实现 |
| `side_channel_format.h` | 33 | 消息格式头文件 |
| `side_channel_format.cc` | 317 | 消息格式实现 |
| `side_channel_module.h` | 65 | 模块头文件 |
| `side_channel_module.cc` | 151 | 模块实现 |

## 8. 架构关系

```
┌─────────────────────────────────────────────────────────────┐
│                  Snort 3 核心引擎                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Side Channel Framework                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  SideChannelManager                                    │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│  │  │SideChannel│ │SideChannel│ │SideChannel│ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Connector 抽象层                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ TcpConnector │ │FileConnector │ │UnixConnector │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │TCP Socket│   │   File   │   │ Unix Domain│
        │  Network │   │  System  │   │   Socket  │
        └──────────┘   └──────────┘   └──────────┘
```

## 9. 使用场景

### 9.1 高可用性 (High Availability)

Side Channel用于HA伙伴之间的状态同步:

```cpp
// 注册接收处理函数
void on_ha_message(SCMessage* msg)
{
    // 处理来自HA伙伴的消息
    // 更新Snort状态
}

side_channel->register_receive_handler(on_ha_message);

// 发送消息给HA伙伴
SCMessage* tx_msg = side_channel->alloc_transmit_message(len);
memcpy(tx_msg->content, data, len);
side_channel->transmit_message(tx_msg);
```

### 9.2 进程间通信

文件连接器用于不需要实时性的场景:

```cpp
FileConnectorConfig config;
config.path = "/var/log/snort/connector.out";
config.format = FILE_FORMAT_VERSION;

FileConnector fc(config);

// 发送消息
ConnectorMsg msg(data, length);
fc.transmit_message(msg);
fc.flush();
```

### 9.3 实时数据传输

TCP连接器用于实时场景:

```cpp
TcpConnectorConfig config;
config.address = "192.168.1.100";
config.port = 5555;

TcpConnector tc(config, sock_fd);

// 接收消息
ConnectorMsg msg = tc.receive_message(true);
```

## 10. 总结

连接器和侧信道模块提供了Snort3灵活的通信机制:

1. **Connector抽象层** - 统一的接口支持多种传输方式
2. **TcpConnector** - 基于TCP的网络通信
3. **FileConnector** - 基于文件系统的持久化通信
4. **UnixDomainConnector** - 本地高速Socket通信
5. **SideChannel** - 带外通信框架,支持HA和数据共享

这些组件使得Snort3能够与其他Snort实例、外部系统或高可用性伙伴进行可靠的消息传递。
