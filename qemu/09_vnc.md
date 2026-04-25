---
title: VNC 服务器架构
---

# VNC 服务器架构分析

## 核心数据结构

### VncDisplay

```c
// ui/vnc.h
struct VncDisplay {
    QTAILQ(VncState) clients;        // 连接的客户端
    QTAILQ(VDnsSocket) listeners;    // TCP/WebSocket 监听器
    DisplaySurface *ds;               // 显示表面
   pixman: server, guest surfaces   // 服务器/访客 pixman 表面
    VncTlsCreds *tls_creds;        // TLS 凭证
    VncSASL *sasl;                  // SASL 状态
};
```

### VncState

```c
// ui/vnc.h
struct VncState {
    VncDisplay *vd;                  // 父 VncDisplay
    QIOChannel *sioc;               // Socket I/O 通道
    QIOChannel *ioc;                // 底层 I/O 通道
    uint32_t dirty[VNC_MAX_HEIGHT][VNC_DIRTY_BITS]; // 脏位图
    VncEncoding enc;                // 编码类型
    VncOutputBuffer output;         // 输出缓冲区
    VncInputBuffer input;           // 输入缓冲区
    // ... 编码特定状态
};
```

## 帧缓冲区更新流程

### 脏位图跟踪

```c
// ui/vnc.h
#define VNC_DIRTY_PIXELS_PER_BIT 16  // 每位 16 像素
#define VNC_MAX_WIDTH 5120
#define VNC_MAX_HEIGHT 2160

// 访客表面更新通过 vnc_dpy_update() → vnc_set_area_dirty() 标记
```

### 更新循环

```
vnc_refresh()
  → 1. vnc_refresh_server_surface()  // 比较访客 vs 服务器表面，复制差异
  → 2. For each client: vnc_update_client()  // 用脏矩形构建 VncJob
  → 3. vnc_job_push()               // 排队到后台工作线程
```

## RFB 协议实现

### 协议版本协商

```c
// 支持 RFB 3.3, 3.4, 3.5, 3.7, 3.8
// v3.4/3.5 规范化为 v3.3 兼容性
```

### 消息类型

```c
// Client → Server
SetPixelFormat(0), SetEncodings(2), FBUpdateRequest(3),
KeyEvent(4), PointerEvent(5), CutText(6)

// Server → Client
FBUpdate(0), SetColourMap(1), Bell(2), CutText(3)
```

### 认证

```c
// 支持: None, VNC password, TLS, VeNCrypt (with SASL/X509), SASL
```

## Tight 编码

### 子编码类型

```c
FILL (0x08)          // 纯色矩形
JPEG (0x09)          // JPEG 压缩
PNG (0x0A)           // PNG 压缩
BASIC+ZLIB (0x03)   // Zlib 压缩带可选过滤器
BASIC+FILTER (0x04) // 带显式过滤器
```

### 梯度过滤器

```c
// 使用 left + upper - upperleft 预测像素值
// 对预测差异编码以获得更好的压缩
```

## ZRLE 编码

### 组合 RLE + 调色板

```c
// 选择: Raw, Plain RLE, Palette RLE, 或 Packed Palette
// 估计每种方法的字节数并选择最小的
```

### 基于瓦片处理

```c
#define VNC_ZRLE_TILE_WIDTH 64
#define VNC_ZRLE_TILE_HEIGHT 64
// 在 64x64 瓦片中处理帧缓冲区
```

## 后台工作线程

```c
// ui/vnc-jobs.c
struct VncJobQueue {
    VncJob *jobs;                    // 作业队列
    QemuMutex mutex;                 // 互斥锁
    QemuCond cond;                   // 条件变量
    QemuThread thread;               // 工作线程
};
```

### 线程循环

```c
vnc_worker_thread_loop()
  → 等待条件变量
  → 创建 VncState 本地副本进行编码 (与主线程解耦)
  → 使用适当编码方案编码矩形
  → 复制结果到 jobs_buffer，调度底部处理
```

## 关键设计模式

1. **双缓冲**: 服务器表面 vs 访客表面以高效脏跟踪
2. **生产者-消费者**: 主线程产生作业，工作线程编码
3. **自适应刷新**: 基于脏区域和更新频率动态调整
4. **节流**: 输出缓冲区大小限制防止客户端过载
5. **编码抽象**: `VncSendFramebufferUpdate` 函数指针分派

## 关键文件

| 文件 | 功能 |
|------|------|
| `ui/vnc.c` | 核心实现 |
| `ui/vnc.h` | 数据结构和常量 |
| `ui/vnc-enc-tight.c` | Tight 编码 |
| `ui/vnc-enc-zrle.c` | ZRLE 编码 |
| `ui/vnc-jobs.c` | 后台工作线程 |
