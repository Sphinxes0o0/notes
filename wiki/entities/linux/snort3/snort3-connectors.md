---
type: entity
tags: [snort3, inter-process-communication, data-export]
created: 2026-05-27
sources: [github-snort3-actions-connectors]
---

# Snort3 Connectors

## 定义

Connector 提供 Snort3 数据包处理线程之间的带外通信，用于高可用性（HA）伙伴通信、侧信道数据传输、以及与外部进程的数据导出。

## 框架架构

### 基类层次 (`framework/connector.h`)

```cpp
class Connector {
public:
    enum Direction { CONN_UNDEFINED, CONN_RECEIVE, CONN_TRANSMIT, CONN_DUPLEX };
    virtual bool transmit_message(const ConnectorMsg&, const ID& = null) = 0;
    virtual ConnectorMsg receive_message(bool block) = 0;
    virtual bool flush();
};

class ConnectorMsg {
    const uint8_t* data;
    uint32_t length;
    bool owns;
    // Move-only, owns memory when pass_ownership=true
};
```

### 插件 API 结构

```cpp
struct ConnectorApi {
    BaseApi base;
    unsigned flags;
    ConnectorFunc pinit, pterm;          // 进程级 init/cleanup
    ConnectorThreadInitFunc tinit;       // 线程局部初始化
    ConnectorThreadTermFunc tterm;       // 线程清理
    ConnectorNewFunc ctor;               // 实例构造
    ConnectorDelFunc dtor;               // 实例析构
};
```

## Connector 类型

| 类型 | 路径 | 方向 | 用途 |
|------|------|------|------|
| `file_connector` | `connectors/file_connector/` | TX/RX | 文件读写（调试/离线分析） |
| `tcp_connector` | `connectors/tcp_connector/` | TX/RX | TCP socket 通信 |
| `unixdomain_connector` | `connectors/unixdomain_connector/` | TX/RX | Unix Domain Socket |
| `std_connector` | `connectors/std_connector/` | TX/RX | stdout/stdin（stdio） |

## 数据格式

所有 connector 使用统一的消息头格式：

```cpp
// 通用消息头
class __attribute__((__packed__)) ConnectorMsgHdr {
    uint8_t version;           // 格式版本
    uint16_t connector_msg_length;  // 消息长度
};
```

### 版本号

| Connector | 版本常量 |
|-----------|----------|
| TCP | `TCP_FORMAT_VERSION = 1` |
| File | `FILE_FORMAT_VERSION = 1` |
| Unix Domain | `UNIXDOMAIN_FORMAT_VERSION = 1` |

## file_connector

基于文件的点对点 connector，用于实例间通信。

```cpp
class FileConnector : public Connector {
    std::fstream file;
    bool transmit_message(const ConnectorMsg&, const ID&) override;
    ConnectorMsg receive_message(bool) override;
    bool flush() override;
};
```

### 特性

- **传输模式**：二进制或文本格式（`text_format` 配置）
- **文件命名**：`{connector_name}_{instance}_transmit` / `_receive`
- **二进制格式**：头 + 数据；文本格式：纯文本行

### 初始化

```cpp
static Connector* file_connector_tinit(const ConnectorConfig& config) {
    if (direction == CONN_TRANSMIT)
        return file_connector_tinit_transmit(filename, fconf);
    else if (direction == CONN_RECEIVE)
        return file_connector_tinit_receive(filename, fconf);
}
```

## tcp_connector

基于 TCP socket 的 connector，支持异步接收。

```cpp
class TcpConnector : public Connector {
    int sock_fd;
    std::thread* receive_thread;
    Ring<ConnectorMsg*>* receive_ring;  // 无锁环形缓冲区
    void start_receive_thread();
    void receive_processing_thread();
};
```

### 特性

- **异步接收**：可选 `async_receive` 模式，后台线程 + Ring buffer
- **poll() 驱动**：使用 `poll()` 系统调用等待 socket 事件
- **Setup 模式**：
  - `CALL` — 主动连接（client）
  - `ANSWER` — 监听接受（server）

### 接收流程

```cpp
void TcpConnector::receive_processing_thread() {
    while (run_thread.load()) {
        process_receive();  // poll() + read_message()
    }
}

ConnectorMsg* TcpConnector::read_message() {
    // 读取 3 字节头 (version + length)
    // 再读取 payload
    return new ConnectorMsg(data, length, true);
}
```

## unixdomain_connector

基于 Unix Domain Socket 的 connector，支持自动重连。

```cpp
class UnixDomainConnector : public Connector {
    int sock_fd;
    std::thread* receive_thread;
    Ring<ConnectorMsg*>* receive_ring;
    UnixDomainConnectorUpdateHandler update_handler;
    UnixDomainConnectorReconnectHelper* reconnect_helper;
};

class UnixDomainConnectorListener {
    void start_accepting_connections(handler, config);
};

class UnixDomainConnectorReconnectHelper {
    void connect(const char* path, size_t idx);
    void reconnect(size_t idx);
};
```

### 特性

- **自动重连**：连接断开后可配置重试（`conn_retries`, `retry_interval`）
- **非阻塞连接**：`connect()` 后用 `select()` 等待完成
- **多路径支持**：基于 `instance_id` 选择不同 socket 路径
- **异步接收**：后台线程 + Ring buffer

### 重连机制

```cpp
void UnixDomainConnector::process_receive() {
    if (pfds[0].revents & (POLLHUP|POLLERR|POLLNVAL)) {
        run_thread.store(false);
        close(sock_fd);
        sock_fd = -1;
        if (reconnect_helper)
            reconnect_helper->reconnect(instance_id);  // 触发重连
        else
            start_retry_thread(cfg, instance_id);
    }
}
```

## std_connector

基于标准输入输出的 connector，用于管道集成。

```cpp
class StdConnector : public Connector {
    bool buffered;
    TextLog* text_log;
    Ring2::Writer writer;
    StdConnectorBuffer& buffer;
};
```

### 特性

- **输出模式**：`stdout`（默认）、文件重定向
- **缓冲模式**：可选 `buffer_size` 启用 Ring2 缓冲
- **统计**：消息收发计数、发送阻塞计数

### 传输实现

```cpp
bool StdConnector::internal_transmit_message(const ConnectorMsg& msg) {
    if (!buffered)
        return TextLog_Print(text_log, "%.*s\n", msg.get_length(), msg.get_data());
    // 否则写入 Ring2
}
```

## 数据导出 Pipeline

```
Snort Detection Engine
    ↓ (IPS Action fires)
Action Queue (per-flow)
    ↓
ConnectorManager
    ↓
Connector (TX) ──socket/file/pipe──> External Process
    ↑
    └── tcp_connector / unixdomain_connector / std_connector / file_connector
```

## 插件注册

```cpp
// connectors.cc
void load_connectors() {
    PluginManager::load_plugins(file_connector);
    PluginManager::load_plugins(tcp_connector);
    PluginManager::load_plugins(std_connector);
    PluginManager::load_plugins(unixdomain_connector);
}
```

## 相关概念

- [[snort3-actions]] — 使用 connector 导出数据的 IPS 动作
- [[snort3-pig]] — 插件加载和生命周期
- [[ring-helpers]] — 无锁环形缓冲区实现
