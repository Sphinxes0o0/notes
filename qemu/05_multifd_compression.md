---
title: Multifd 和压缩
---

# Multifd 和压缩分析

## Multifd 通道

```c
// migration/multifd.c
struct MultiFDPacket_t {
    uint32_t magic;                 // 0x11223344 验证
    uint32_t version;               // 协议版本
    uint32_t flags;                // 压缩方法 + 同步标志
    uint32_t packet_num;           // 全局序列号
    uint32_t pages;                 // 页数
    uint32_t size;                  // 数据大小
    uint64_t normal[4096];          // 正常页
    uint32_t zero[1024];            // 零页
};

// 512KB 默认包大小
```

### 压缩标志

```c
MULTIFD_FLAG_NOCOMP      // 无压缩
MULTIFD_FLAG_ZLIB        // zlib 压缩
MULTIFD_FLAG_ZSTD        // zstd 压缩
MULTIFD_FLAG_QPL         // QPL 压缩
MULTIFD_FLAG_UADK        // UADK 压缩
MULTIFD_FLAG_QATZIP      // QATzip 压缩
```

### 通道同步

```c
MULTIFD_SYNC_NONE        // 不同步
MULTIFD_SYNC_LOCAL       // 本地同步
MULTIFD_SYNC_ALL         // 全同步

// 基于信号量的主线程和工作线程协调
pending_job / pending_sync // 每通道标志
```

## 压缩方法

```c
// migration/multifd-*.c
struct MultiFDMethods {
    const char *name;

    int (*send_setup)(MultiFDSendParams *p);
    int (*send_cleanup)(MultiFDSendParams *p, int err);
    int (*send_prepare)(MultiFDSendParams *p);

    int (*recv_setup)(MultiFDRecvParams *p);
    int (*recv_cleanup)(MultiFDRecvParams *p, int err);
    int (*recv)(MultiFDRecvParams *p);
};
```

### 零页检测

```c
multifd_send_zero_page_detect()    // 发送前标记零页
multifd_recv_zero_page_process()   // 接收端处理零页
```

## RDMA 迁移

```c
// migration/rdma.h (编译时可选 CONFIG_RDMA)

rdma_connect_outgoing()           // 建立 RDMA 连接
rdma_connect_incoming()            // 接收 RDMA 连接
rdma_control_save_page()           // 直接内存传输

RAM_CONTROL_SETUP/ROUND/FINISH   // 控制操作
RAM_SAVE_CONTROL_DELAYED          // 异步操作返回码
```

### 集成

```c
// 通过 ram_save_target_page() 检查拦截
// 返回 RAM_SAVE_CONTROL_DELAYED 表示异步处理
// 通过返回路径完成
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `multifd.c` | Multifd 协议 |
| `multifd-zlib.c` | zlib 压缩 |
| `multifd-zstd.c` | zstd 压缩 |
| `rdma.h` | RDMA 接口 |
