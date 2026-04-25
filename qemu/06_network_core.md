---
title: 网络核心架构
---

# 网络核心架构分析

## NetClientState

```c
// include/net/net.h
struct NetClientState {
    NetClientInfo *info;           // 驱动特定操作
    int link_down;                  // 链路状态标志
    QTAILQ_ENTRY(NetClientState) next; // 全局 net_clients 列表
    NetClientState *peer;           // 连接的对方
    NetQueue *incoming_queue;       // 数据包接收队列
    char *model;                    // 设备模型名称
    char *name;                     // 唯一标识符
    char info_str[256];            // 人类可读信息
    unsigned receive_disabled : 1; // 流控标志
    NetClientDestructor *destructor;
    unsigned int queue_index;       // 多队列索引
    unsigned rxfilter_notify_enabled:1;
    int vring_enable;
    int vnet_hdr_len;              // Virtio net 头长度
    bool is_netdev;                 // 是否为 netdev
    bool do_not_pad;                // 帧填充控制
    bool is_datapath;               // 数据路径部分
    QTAILQ_HEAD(, NetFilterState) filters; // 数据包过滤器
};
```

## NetClientInfo (驱动接口)

```c
typedef struct NetClientInfo {
    NetClientDriver type;           // 驱动类型
    size_t size;                    // 派生结构大小
    NetReceive *receive;           // 接收处理程序
    NetReceiveIOV *receive_iov;    // 向量接收处理程序
    NetCanReceive *can_receive;     // 轮询回调
    NetStart *start;               // 启动处理程序
    NetStop *stop;                 // 停止处理程序
    NetCleanup *cleanup;           // 清理处理程序
    LinkStatusChanged *link_status_changed;
    GetVHostNet *get_vhost_net;    // Vhost-net 集成
} NetClientInfo;
```

## NetQueue (数据包队列)

```c
// net/queue.c
struct NetQueue {
    void *opaque;                   // 所有者上下文
    uint32_t nq_maxlen;            // 最大队列深度 (默认 10000)
    uint32_t nq_count;              // 当前数据包数
    NetQueueDeliverFunc *deliver;   // 投递回调
    QTAILQ_HEAD(, NetPacket) packets; // 数据包列表
    unsigned delivering : 1;        // 重入投递标志
};
```

### 关键行为

- **流控**: `deliver` 返回 0 暂停投递
- **重入保护**: `delivering` 标志防止无限递归
- **向量 I/O**: `qemu_net_queue_send_iov()` 处理 iovec 数组

## 后端驱动

### TAP 后端

```c
// net/tap.c
typedef struct TAPState {
    NetClientState nc;
    int fd;                         // TAP 设备文件描述符
    char down_script[1024];
    char down_script_arg[128];
    bool using_vnet_hdr;            // Virtio net 头使用
    VHostNetState *vhost_net;       // 关联的 vhost-net
} TAPState;
```

### Socket 后端

```c
// net/socket.c
typedef struct NetSocketState {
    NetClientState nc;
    int listen_fd;                   // 监听 socket
    int fd;                          // 已连接 socket
    SocketReadState rs;              // 数据包重组状态
    struct sockaddr_in dgram_dst;    // UDP 目标
} NetSocketState;

// 模式: SOCK_STREAM (长度前缀), SOCK_DGRAM (UDP)
```

### Vhost-Net 后端

```c
// hw/net/vhost_net.c
// 封装内核 vhost-net 设备加速 virtio
vhost_net_init()                    // 创建 vhost_net 结构
vhost_net_start/stop()             // 控制设备状态
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `net/net.c` | NetClientState 核心 |
| `net/queue.c` | NetQueue 实现 |
| `net/tap.c` | TAP 后端 |
| `net/socket.c` | Socket 后端 |
| `hw/net/vhost_net.c` | Vhost-net 加速 |
