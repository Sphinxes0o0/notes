# OpenBMC KVM/虚拟介质深度分析

## 目录

1. [概述](#1-概述)
2. [phosphor-virtualmedia 虚拟介质服务](#2-phosphor-virtualmedia-虚拟介质服务)
3. [phosphor-kvm KVM 会话管理](#3-phosphor-kvm-kvm-会话管理)
4. [HTML5 KVM Web 客户端](#4-html5-kvm-web-客户端)
5. [Markdown 图像编码与 KVM 流传输](#5-markdown-图像编码与-kvm-流传输)
6. [会话生命周期管理](#6-会话生命周期管理)
7. [与主机通信机制](#7-与主机通信机制)
8. [知识点关联表格](#8-知识点关联表格)

---

## 1. 概述

### 1.1 OpenBMC 简介

OpenBMC 是 Linux 基金会托管的开源项目，旨在为基板管理控制器（BMC）构建完整的 Linux 固件堆栈。BMC 是服务器主板上的专用微控制器，负责远程管理和监控硬件状态。OpenBMC 广泛应用于数据中心服务器、存储设备、网络设备等基础设施硬件的管理。

### 1.2 KVM/虚拟介质子系统架构

KVM（Keyboard, Video, Mouse）和虚拟介质（Virtual Media）是 OpenBMC 系统中两个紧密协作的远程管理组件：

| 组件 | 功能 | 协议/技术 |
|------|------|----------|
| **phosphor-virtualmedia** | CD/DVD/USB 存储介质重定向 | NBD, USB Gadget, D-Bus |
| **phosphor-kvm** | 键盘/视频/鼠标会话管理 | VNC/RFB, WebSocket |
| **bmcweb** | Web 服务器，统一接口 | HTTPS, Redfish, WebSocket |
| **phosphor-webui** | HTML5 Web 客户端 | JavaScript, HTML5 Canvas |

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐     │
│  │   Virtual Media UI  │    │        KVM Client          │     │
│  │   (HTML5 File UI)   │    │   (HTML5 Canvas + VNC)     │     │
│  └──────────┬──────────┘    └──────────────┬──────────────┘     │
│             │          WebSocket/HTTPS      │                    │
└─────────────┼──────────────────────────────┼────────────────────┘
              │                              │
┌─────────────┼──────────────────────────────┼────────────────────┐
│             ▼                              ▼                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                      BMCWeb                              │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │    │
│  │  │   Redfish   │  │   KVM RFB   │  │  D-Bus Event   │  │    │
│  │  │   API       │  │  WebSocket  │  │   WebSocket    │  │    │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│             │                              │                     │
│  ┌─────────┴──────────────┐    ┌────────┴───────────────┐     │
│  │  phosphor-virtualmedia  │    │     obmc-ikvm          │     │
│  │  (D-Bus Service)        │    │  (VNC Server)          │     │
│  └─────────┬──────────────┘    └────────┬───────────────┘     │
│            │                              │                     │
└────────────┼──────────────────────────────┼─────────────────────┘
             │                              │
    ┌────────┴────────┐           ┌─────────┴──────────┐
    │   NBD Client   │           │   USB Gadget      │
    │   (nbdkit)     │           │   (/dev/hidgX)    │
    └────────┬────────┘           └─────────┬──────────┘
             │                              │
    ┌────────┴────────┐           ┌─────────┴──────────┐
    │  /dev/nbdX     │           │    USB Device      │
    │  (Block Device) │           │    (to HOST)       │
    └─────────────────┘           └────────────────────┘
```

---

## 2. phosphor-virtualmedia 虚拟介质服务

### 2.1 服务概述

phosphor-virtualmedia 是 OpenBMC 中的虚拟介质服务，负责将远程 ISO/IMG 磁盘映像文件重定向到服务器主机。远程驱动器在主机中呈现为 USB 存储设备，支持只读（RO）和读写（RW）两种模式。该功能允许管理员远程安装操作系统、访问介质文件，甚至可以在裸机系统上进行操作系统安装。

### 2.2 工作模式

虚拟介质服务支持两种工作模式：

#### 2.2.1 代理模式（Proxy Mode）

代理模式允许浏览器 JavaScript/WebSocket 直接与 BMC 上的 HTTPS 端点通信，并升级为 WSS（WebSocket Secure）用于 NBD 服务器命令交互。这种模式下，数据流直接从前端浏览器流向 BMC，减少了延迟。

```
Web Browser → JavaScript/WebSocket → BMCWeb (HTTPS/WSS) → VirtualMedia Service
```

#### 2.2.2 传统模式（Legacy Mode）

传统模式通过 Redfish VirtualMedia API 发起连接，BMC 进程连接到外部 CIFS/HTTPS 映像服务器。这种模式需要预先配置外部存储服务器地址。

```
Browser → Redfish API → BMCWeb → VirtualMedia Service → NBDkit → CIFS/HTTPS Server
```

### 2.3 核心组件与数据流

#### 2.3.1 核心技术栈

| 组件 | 技术 | 功能 |
|------|------|------|
| **NBD (Network Block Device)** | TCP 协议 | 远程块设备访问，将数据拉取到本地 /dev/nbdXX |
| **USB Gadget** | Linux Kernel USB OTG | 模拟 USB 大容量存储设备到主机 |
| **NBDkit** | NBD 服务器 | 通过 HTTPS/CIFS 协议提供磁盘映像 |
| **D-Bus** | IPC 机制 | 服务间通信与异步操作 |

#### 2.3.2 数据流架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Web Browser │────▶│   BMCWeb    │────▶│VirtualMedia │────▶│  NBD Client │
│  (HTTPS)    │     │   (HTTPS)   │     │  (D-Bus)    │     │  (UNIX Sock)│
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│    HOST     │◀────│ USB Gadget  │◀────│  /dev/nbdX  │◀───────────┤
│  (Server)   │     │ /dev/hidgX │     │  (Block Dev)│            │
└─────────────┘     └─────────────┘     └─────────────┘            │
                                                                    │
                                                         ┌──────────┴──────────┐
                                                         │      NBDkit         │
                                                         │  (CIFS/HTTPS)       │
                                                         └──────────┬──────────┘
                                                                    │
                                                         ┌──────────┴──────────┐
                                                         │  Remote Storage     │
                                                         │  (ISO/IMG File)     │
                                                         └─────────────────────┘
```

### 2.4 D-Bus 接口定义

VirtualMedia 服务通过 D-Bus 与其他组件通信，主要接口包括：

#### 2.4.1 服务名称与对象路径

```
Service Name: xyz.openbmc_project.VirtualMedia
Object Path:  /xyz/openbmc_project/VirtualMedia/device/{instance}
```

#### 2.4.2 核心接口方法

| 方法 | 参数 | 返回值 | 描述 |
|------|------|--------|------|
| `Mount` | `string imageUri, string mountType, boolean readOnly` | `void` | 挂载远程映像 |
| `Unmount` | `void` | `void` | 卸载虚拟介质 |
| `GetStatus` | `void` | `string status` | 获取挂载状态 |
| `SetAuthMethod` | `string method, string credentials` | `void` | 设置认证方法 |

#### 2.4.3 D-Bus 信号

| 信号 | 参数 | 描述 |
|------|------|------|
| `StatusChanged` | `string oldStatus, string newStatus` | 状态变更通知 |
| `MountCompleted` | `boolean success, string message` | 挂载完成通知 |
| `ProgressUpdate` | `uint32 percentage` | 传输进度更新 |

### 2.5 NBD 协议交互

NBD（Network Block Device）是一种基于 TCP 的远程块设备访问协议。在虚拟介质场景中：

1. **客户端连接**：NBD Client 通过 UNIX 域socket连接到 NBDkit
2. **握手过程**：NBD 协议握手交换导出名称和选项
3. **块传输**：通过 TCP 连接传输块数据
4. **设备映射**：映射到本地 /dev/nbdX 设备节点

```cpp
// NBD Client 关键数据结构
struct nbd_request {
    uint32_t magic;      // NBD_REQUEST_MAGIC
    uint16_t flags;      // NBD_CMD_HAS_FLAGS
    uint16_t type;       // 命令类型
    uint64_t handle;     // 请求句柄
    uint64_t offset;     // 偏移量
    uint32_t length;     // 数据长度
};
```

### 2.6 USB Gadget 配置

USB Gadget 子系统在 BMC 端模拟 USB 大容量存储设备：

```bash
# USB Gadget 设备节点
/dev/hidg0  # 键盘 HID 设备
/dev/hidg1  # 鼠标 HID 设备
/dev/hidg2  # 虚拟 CD/DVD
```

关键配置参数：
- **驱动模式**：FunctionFS（FunctionFS 模式支持多接口复合设备）
- **HID 描述符**：定义设备的 VID/PID 和接口描述符
- **传输模式**：Bulk-Only 传输（USB Mass Storage 规范）

---

## 3. phosphor-kvm KVM 会话管理

### 3.1 obmc-ikvm 概述

obmc-ikvm 是 OpenBMC 中的 KVM 会话管理守护进程，负责捕获视频流和处理键盘鼠标输入。它与 bmcweb 协作，通过 WebSocket 向 Web 客户端提供完整的远程 KVM 功能。

### 3.2 核心类架构

obmc-ikvm 源代码实现了五个核心类：

```cpp
namespace ikvm {
    // 参数解析类：读取和解析命令行参数
    class Args {
    public:
        Args(int argc, char* argv[]);
        std::string getDevice() const;      // 获取视频设备
        int getPort() const;                 // 获取监听端口
        bool getVerbose() const;             // 获取详细模式
    };

    // 输入处理类：虚拟键盘/鼠标输入
    class Input {
    public:
        void sendKeyEvent(uint32_t key, bool pressed);
        void sendPointerEvent(int x, int y, uint8_t buttons);
    };

    // 视频传输类：视频捕获和发送
    class Video {
    public:
        int initDevice(const std::string& device);
        void captureFrame();
        void sendFrame();
    };

    // 服务器类：会话调度和协调
    class Server {
    public:
        void acceptConnection();
        void processEvents();
    };

    // 管理类：主控制器，协调所有类
    class Manager {
    private:
        Args args;
        Input input;
        Video video;
        Server server;
        bool continueExecuting;
        bool serverDone;
        bool videoDone;
    public:
        Manager(const Args& args);
        void run();
    };
}
```

### 3.3 视频流子系统

#### 3.3.1 V4L2 框架

视频捕获基于 Linux V4L2（Video4Linux2）框架：

```bash
# 视频设备节点
/dev/video0  # 捕获设备
```

关键 V4L2 操作：

| 操作 | 描述 |
|------|------|
| `V4L2_BUF_TYPE_VIDEO_CAPTURE` | 视频捕获类型 |
| `V4L2_MEMORY_MMAP` | 内存映射缓冲区模式 |
| `VIDIOC_DQBUF` | 出队已捕获的缓冲区 |
| `VIDIOC_QBUF` | 入队空闲缓冲区 |
| `VIDIOC_STREAMON` | 启动视频流 |

#### 3.3.2 帧捕获流程

```cpp
// 视频捕获主循环
void Manager::run() {
    // 初始化视频设备
    video.initDevice(args.getDevice());

    // 启动视频传输线程
    std::thread videoThread([this]() {
        while (continueExecuting) {
            video.captureFrame();
            video.sendFrame();
        }
    });

    // 事件处理线程（键盘/鼠标）
    std::thread eventThread([this]() {
        while (continueExecuting) {
            server.processEvents();
        }
    });

    videoThread.join();
    eventThread.join();
}
```

### 3.4 键盘鼠标输入处理

#### 3.4.1 USB HID 模拟

obmc-ikvm 通过 USB Gadget 模拟 USB HID（Human Interface Device）设备：

```bash
# HID 设备节点
/dev/hidg0  # 键盘设备
/dev/hidg1  # 鼠标设备
```

HID 报告描述符定义了输入数据格式：

```cpp
// 键盘 HID 报告格式
struct hid_keyboard_report {
    uint8_t modifiers;     // 修饰键（Shift, Ctrl, Alt等）
    uint8_t reserved;     // 保留字段
    uint8_t keycodes[6];  // 最多6个同时按下的键
};

// 鼠标 HID 报告格式
struct hid_mouse_report {
    uint8_t buttons;      // 按钮状态
    int8_t  x_delta;      // X 方向移动增量
    int8_t  y_delta;      // Y 方向移动增量
    int8_t  wheel_delta;   // 滚轮增量
};
```

#### 3.4.2 LibVNCServer 集成

使用 LibVNCServer 库处理 RFB/VNC 协议事件：

```cpp
#include <rfb/rfb.h>
#include <rfb/keysym.h>

// 键盘事件处理
void keyEvent(rfbBool down, rfbKeySym keySym, rfbClientPtr cl) {
    uint32_t keyCode = keysym2keycode(keySym);
    input.sendKeyEvent(keyCode, down);
}

// 指针事件处理
void pointerEvent(int x, int y, int buttonMask, rfbClientPtr cl) {
    uint8_t buttons = 0;
    if (buttonMask & 1) buttons |= MOUSE_BUTTON_LEFT;
    if (buttonMask & 2) buttons |= MOUSE_BUTTON_RIGHT;
    if (buttonMask & 4) buttons |= MOUSE_BUTTON_MIDDLE;
    input.sendPointerEvent(x, y, buttons);
}

// 设置 RFB 回调
rfbScreenInfoPtr server = rfbGetScreen(&argc, argv, width, height, 8, 3, bytesPerPixel);
server->kbdAddEvent = keyEvent;
server->ptrAddEvent = pointerEvent;
```

### 3.5 通信协议

#### 3.5.1 TCP Socket 通信

obmc-ikvm 与 bmcweb 之间使用原生 TCP Socket 通信：

| 组件 | 角色 | 端口 |
|------|------|------|
| obmc-ikvm | VNC Server | 5900 |
| bmcweb | VNC Client | 动态分配 |

#### 3.5.2 协议数据流

```
bmcweb (Client)                              obmc-ikvm (Server)
     │                                              │
     │────────── TCP Connection (Port 5900) ───────▶│
     │                                              │
     │◀─────── VNC Protocol Handshake ─────────────│
     │        (ProtocolVersion, Security)           │
     │                                              │
     │──────── Init: Framebuffer size ────────────▶│
     │◀─────── FramebufferUpdate ──────────────────│
     │        (Video frames)                        │
     │                                              │
     │──────── KeyEvent (keyboard) ────────────────▶│
     │──────── PointerEvent (mouse) ────────────────▶│
     │        (Input events)                         │
     │                                              │
     │◀──────── FramebufferUpdate ─────────────────│
     │        (Updated video)                        │
     │                                              │
```

### 3.6 会话同步机制

Manager 类使用线程同步原语管理视频和事件处理线程：

```cpp
// 线程同步状态
bool serverDone;   // 服务器线程完成标志
bool videoDone;    // 视频线程完成标志

// 同步函数
void setVideoDone(bool done) { videoDone = done; }
void waitServer() { while (!serverDone) { /* wait */ } }
void waitVideo() { while (!videoDone) { /* wait */ } }

// 帧计数器（用于检测分辨率变化）
int frameCounter;
```

---

## 4. HTML5 KVM Web 客户端

### 4.1 bmcweb KVM 实现

bmcweb 是 OpenBMC 的统一 Web 服务器，实现了基于 WebSocket 的 RFB（Remote Framebuffer）协议，用于与 webui-vue 配合提供完整的 KVM 功能。

#### 4.1.1 KVM RFB 协议实现

```javascript
// bmcweb KVM WebSocket 端点
const kvmEndpoint = "wss://{bmc_ip}/kvm/{session_id}";
```

bmcweb 将 RFB 协议封装为 WebSocket 消息流：

| RFB 消息类型 | WebSocket 帧 | 描述 |
|-------------|-------------|------|
| FramebufferUpdate | Binary Frame | 视频帧数据 |
| KeyEvent | Binary Frame | 键盘事件 |
| PointerEvent | Binary Frame | 鼠标事件 |
| ClientCutText | Binary Frame | 剪贴板文本 |

### 4.2 Web 客户端架构

#### 4.2.1 前端组件

```javascript
// HTML5 KVM 客户端核心组件
class KVMClient {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.websocket = null;
        this.rfbState = {
            version: null,
            security: null,
            encodings: ['RAW', 'ZLIB', 'HEXTILE', 'RRE']
        };
    }

    connect(sessionId) {
        const url = `wss://${location.host}/kvm/${sessionId}`;
        this.websocket = new WebSocket(url, ['rfb']);
        this.websocket.binaryType = 'arraybuffer';

        this.websocket.onopen = () => this.onConnect();
        this.websocket.onmessage = (e) => this.onMessage(e);
        this.websocket.onclose = () => this.onDisconnect();
    }

    // 处理视频帧更新
    handleFramebufferUpdate(data) {
        const rect = this.readRect(data);
        const pixels = this.decodePixels(rect.encoding, data);
        this.ctx.putImageData(pixels, rect.x, rect.y);
    }

    // 发送键盘事件
    sendKeyEvent(key, pressed) {
        const msg = this.buildKeyEventMsg(key, pressed);
        this.websocket.send(msg);
    }

    // 发送鼠标事件
    sendPointerEvent(x, y, buttons) {
        const msg = this.buildPointerEventMsg(x, y, buttons);
        this.websocket.send(msg);
    }
}
```

#### 4.2.2 Canvas 渲染

HTML5 Canvas 用于实时渲染视频帧：

```javascript
// Canvas 配置
const canvas = document.getElementById('kvm-canvas');
canvas.width = 1920;  // 最大分辨率
canvas.height = 1080;

// 渲染循环
function renderLoop() {
    requestAnimationFrame(renderLoop);
    // 双缓冲渲染逻辑
}
```

### 4.3 认证与安全

bmcweb 实现了多层安全机制：

| 安全层 | 机制 | 描述 |
|--------|------|------|
| 传输层 | HTTPS/WSS | TLS 加密传输 |
| 认证 | Cookie/Token | 基于会话的认证 |
| 授权 | PAM | Linux PAM 认证后端 |
| CSRF | Token | 跨站请求伪造防护 |

```javascript
// 认证流程
async function authenticate(username, password) {
    const response = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
        credentials: 'include'
    });
    return response.ok;
}
```

### 4.4 会话管理

Web 客户端通过 sessionId 标识 KVM 会话：

```javascript
// 会话状态
const sessionState = {
    id: null,
    status: 'disconnected', // connecting, connected, disconnecting
    server: null,
    startedAt: null,
    lastActivity: null
};

// 会话建立
async function startSession() {
    const response = await fetch('/api/kvm/sessions', {
        method: 'POST',
        credentials: 'include'
    });
    const data = await response.json();
    sessionState.id = data.sessionId;
    kvmClient.connect(data.sessionId);
}

// 会话终止
async function terminateSession() {
    await fetch(`/api/kvm/sessions/${sessionState.id}`, {
        method: 'DELETE',
        credentials: 'include'
    });
    sessionState.id = null;
}
```

---

## 5. Markdown 图像编码与 KVM 流传输

### 5.1 KVM 流编码概述

KVM 视频流在传输过程中需要高效的编码方式来减少带宽占用。OpenBMC 支持多种编码方案，从原始像素到压缩格式。

### 5.2 支持的 RFB 编码类型

| 编码类型 | 编号 | 描述 | 适用场景 |
|---------|------|------|---------|
| RAW | 0 | 原始像素数据 | 低延迟本地连接 |
| ZLIB | 6 | zlib 压缩 | 中等带宽 |
| HEXTILE | 5 | 16x16 瓦片压缩 | 互联网连接 |
| RRE | 2 | Rise-and-Run-Length | 已废弃 |
| Tight | 7 | JPEG/PNG 压缩 | 高压缩比 |
| TightPNG | 7 | PNG 压缩 | 无损压缩 |

### 5.3 帧数据格式

#### 5.3.1 FramebufferUpdate 消息格式

```
+----------+-------------+------------+----------------+
| 0 (类型) | 0 (填充)    | 2 (数量)   | 后续数据        |
+----------+-------------+------------+----------------+
| u8       | u8          | u16        | 变长           |
```

矩形数据格式：

```
+------+------+--------+--------+--------+-------------+
| X    | Y    | Width  | Height | Coding | Data        |
+------+------+--------+--------+--------+-------------+
| u16  | u16  | u16    | u16    | u32    | 变长        |
```

### 5.4 Base64 编码在 Markdown 中的应用

在某些管理界面和日志中，KVM 帧可能需要以 Base64 编码形式嵌入 Markdown 文档：

#### 5.4.1 图像内联格式

```markdown
![KVM Session Snapshot](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==)
```

#### 5.4.2 Base64 编码流程

```
原始帧数据 → PNG 编码 → Base64 编码 → Markdown 嵌入
```

### 5.5 流传输优化

#### 5.5.1 带宽自适应

```javascript
// 编码选择策略
function selectEncoding(bandwidth) {
    if (bandwidth > 10 * 1024 * 1024) { // > 10 Mbps
        return 'RAW';
    } else if (bandwidth > 1 * 1024 * 1024) { // > 1 Mbps
        return 'HEXTILE';
    } else {
        return 'TIGHT';
    }
}
```

#### 5.5.2 帧率控制

```javascript
// 动态帧率调整
const frameController = {
    targetFPS: 30,
    actualFPS: 0,
    frameHistory: [],

    adjust() {
        if (this.actualFPS < this.targetFPS * 0.8) {
            // 降低帧率以保证实时性
            this.targetFPS = Math.max(5, this.targetFPS * 0.8);
        }
    }
};
```

---

## 6. 会话生命周期管理

### 6.1 会话状态机

KVM/虚拟介质会话遵循标准的状态机模型：

```
                    ┌──────────────────┐
                    │    IDLE          │
                    │  (初始状态)       │
                    └────────┬─────────┘
                             │ startSession()
                             ▼
                    ┌──────────────────┐
                    │  CONNECTING      │
                    │  (连接中)        │
                    └────────┬─────────┘
                             │ onConnected()
                             ▼
                    ┌──────────────────┐
          ┌────────▶│   ACTIVE         │◀────────┐
          │         │  (会话活跃)      │         │
          │         └────────┬─────────┘         │
          │                  │                  │
          │         pauseSession()              │ resumeSession()
          │                  │                  │
          │                  ▼                  │
          │         ┌──────────────────┐        │
          │         │   SUSPENDED      │────────┘
          │         │  (会话暂停)      │
          │         └────────┬─────────┘
          │                  │
          │                  │ terminateSession()
          │                  ▼
          │         ┌──────────────────┐
          └─────────│  TERMINATING     │
                    │  (终止中)        │
                    └────────┬─────────┘
                             │ onTerminated()
                             ▼
                    ┌──────────────────┐
                    │    CLOSED        │
                    │  (已关闭)        │
                    └──────────────────┘
```

### 6.2 会话建立流程

#### 6.2.1 KVM 会话建立

```
1. Web Client                      2. BMCWeb                      3. obmc-ikvm
      │                                │                              │
      │── POST /api/kvm/sessions ─────▶│                              │
      │                                │── Create Session ───────────▶│
      │                                │◀── Session Created ──────────│
      │◀── {sessionId, wsUrl} ─────────│                              │
      │                                │                              │
      │── WSS connect (wsUrl) ────────▶│                              │
      │                                │── Proxy to Port 5900 ────────▶│
      │                                │◀── VNC Handshake ────────────│
      │◀── WebSocket Binary Stream ────│                              │
      │                                │                              │
      │── FramebufferRequest ─────────▶│                              │
      │                                │── FramebufferUpdate ─────────▶│
      │◀── Video Frame ────────────────│◀── Encoded Frame ─────────────│
      │                                │                              │
```

#### 6.2.2 虚拟介质会话建立

```
1. Web Client                   2. BMCWeb                   3. VirtualMedia
      │                              │                            │
      │── GET /redfish/v1/Managers ──▶│                            │
      │◀── Manager Collection ────────│                            │
      │                              │                            │
      │── POST /VirtualMedia/Mount    │                            │
      │   {Image: "https://...",      │                            │
      │    ReadOnly: true}            │                            │
      │──────────────────────────────▶│── D-Bus Mount() ─────────▶│
      │                              │◀── Mount Started ──────────│
      │◀── 202 Accepted ─────────────│                            │
      │                              │                            │
      │── GET /VirtualMedia/{id}     │                            │
      │◀── {Status: "Mounted"} ───────│                            │
```

### 6.3 会话保持机制

#### 6.3.1 心跳检测

```javascript
// WebSocket 心跳
const heartbeat = {
    interval: 30000,  // 30秒
    timer: null,

    start() {
        this.timer = setInterval(() => {
            if (this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({type: 'ping'}));
            }
        }, this.interval);
    },

    stop() {
        if (this.timer) clearInterval(this.timer);
    }
};
```

#### 6.3.2 自动重连

```javascript
class ReconnectionManager {
    constructor(maxAttempts = 5, baseDelay = 1000) {
        this.maxAttempts = maxAttempts;
        this.baseDelay = baseDelay;
        this.attempts = 0;
    }

    shouldRetry() {
        return this.attempts < this.maxAttempts;
    }

    getDelay() {
        // 指数退避
        return this.baseDelay * Math.pow(2, this.attempts);
    }

    recordFailure() {
        this.attempts++;
    }

    recordSuccess() {
        this.attempts = 0;
    }
}
```

### 6.4 会话终止流程

#### 6.4.1 主动终止

```javascript
async function terminateSession() {
    // 1. 通知服务器
    await fetch(`/api/kvm/sessions/${sessionId}`, {
        method: 'DELETE'
    });

    // 2. 关闭 WebSocket
    if (kvmClient.websocket) {
        kvmClient.websocket.close(1000, 'Client initiated');
    }

    // 3. 释放资源
    kvmClient.release();
}
```

#### 6.4.2 被动终止（超时）

服务端超时配置：

```xml
<!-- Session timeout 配置 -->
<session>
    <timeout>300</timeout>  <!-- 5分钟空闲超时 -->
    <maxLifetime>3600</maxLifetime>  <!-- 1小时最大生命周期 -->
</session>
```

### 6.5 超时配置

| 超时类型 | D-Bus | Redfish | 描述 |
|---------|-------|---------|------|
| 挂载操作 | 25s | 60s | 异步挂载/卸载超时 |
| 会话空闲 | - | 300s | 空闲会话超时 |
| 会话最大生命周期 | - | 3600s | 会话最大存活时间 |
| WebSocket Ping | 30s | - | 心跳间隔 |

---

## 7. 与主机通信机制

### 7.1 Socket/D-Bus 接口概述

OpenBMC 中 KVM/虚拟介质与主机（HOST）的通信涉及多种 IPC 机制：

| IPC 类型 | 用途 | 位置 |
|---------|------|------|
| D-Bus | 服务间通信 | BMC 内部 |
| UNIX Socket | NBD 客户端连接 | /var/run/nbd.sock |
| TCP Socket | VNC 协议 | Port 5900 |
| USB Gadget | 设备模拟 | /dev/hidg*, /dev/bus/usb/* |
| /dev/nbdX | 块设备 | 块设备接口 |

### 7.2 D-Bus 通信架构

```
┌─────────────────────────────────────────────────────────────┐
│                     BMC System                               │
│                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │  phosphor-  │     │   bmcweb    │     │  obmc-ikvm  │   │
│  │  virtualmedia│◀───▶│  (D-Bus    │     │  (D-Bus     │   │
│  │             │     │   Client)   │     │   Client)   │   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘   │
│         │                   │                   │          │
│         └───────────────────┴───────────────────┘          │
│                           │                                 │
│                    ┌──────┴──────┐                         │
│                    │  D-Bus Bus   │                         │
│                    │  (System Bus) │                         │
│                    └─────────────┘                         │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                      │
┌────────┴────────┐                  ┌──────────┴──────────┐
│   NBD Client   │                  │   USB Subsystem   │
│  (nbdkit)      │                  │   (Gadget Driver) │
└────────┬────────┘                  └──────────┬──────────┘
         │                                      │
┌────────┴────────┐                  ┌──────────┴──────────┐
│   /dev/nbdX     │                  │    USB Device      │
│                 │                  │   (to HOST)        │
└─────────────────┘                  └────────────────────┘
```

### 7.3 NBD Socket 连接

NBD 客户端通过 UNIX 域 socket 连接 NBDkit 服务器：

```bash
# NBD socket 路径
/var/run/nbd-client.sock
/var/run/nbd-server.sock
```

### 7.4 USB 设备模拟

#### 7.4.1 USB Gadget 配置

```bash
# 列出可用的 USB Gadget 配置
ls /configfs/usb_gadget/

# 创建虚拟 CD/DVD Gadget
mkdir -p /configfs/usb_gadget/g1/functions/mass_storage.usb0

# 配置 Gadget 参数
echo "1" > /configfs/usb_gadget/g1/functions/mass_storage.usb0/lun.0/cdrom
echo "0" > /configfs/usb_gadget/g1/functions/mass_storage.usb0/lun.0/ro
echo "/dev/nbd0" > /configfs/usb_gadget/g1/functions/mass_storage.usb0/lun.0/file

# 启用 Gadget
echo "g1" > /configfs/usb_gadget/g1/UDC
```

#### 7.4.2 HID 设备配置

```bash
# 创建 HID Gadget
mkdir -p /configfs/usb_gadget/g1/functions/hid.usb0

# 配置键盘 HID
echo "/dev/hidg0" > /configfs/usb_gadget/g1/functions/hid.usb0/galaxy
```

### 7.5 主机端视图

当虚拟介质挂载成功时，主机端会看到一个 USB 大容量存储设备：

```
$ lsusb
Bus 001 Device 002: ID 0000:0000 Virtual USB Device

$ dmesg
[  123.456789] usb 1-1: new USB device, idVendor=0000, idProduct=0000
[  123.456790] usb 1-1: New USB device found, idVendor=0000, idProduct=0000
[  123.456791] usb 1-1: Product: Virtual USB CD-ROM
[  123.456792] usb 1-1: Manufacturer: OpenBMC Virtual Media
```

### 7.6 通信接口汇总

| 接口类型 | 端点 | 协议 | 方向 | 用途 |
|---------|------|------|------|------|
| D-Bus | System Bus | D-Bus | 双向 | BMC 内部 IPC |
| WebSocket | /kvm/{id} | RFB/VNC | 双向 | KVM 会话 |
| WebSocket | /vm/{id} | 自定义 | 双向 | 虚拟介质状态 |
| HTTPS | /redfish/v1/* | Redfish | 请求/响应 | REST API |
| UNIX Socket | /var/run/nbd.sock | NBD | 双向 | 块设备传输 |
| USB Device | /dev/bus/usb/* | USB | 主机可见 | 设备模拟 |
| HID | /dev/hidg* | HID | 输出到主机 | 输入模拟 |

---

## 8. 知识点关联表格

### 8.1 组件关联表

| 源组件 | 目标组件 | 协议/接口 | 描述 |
|--------|---------|-----------|------|
| Web Browser | BMCWeb | HTTPS/WSS | Web 访问入口 |
| BMCWeb | phosphor-virtualmedia | D-Bus | 虚拟介质控制 |
| BMCWeb | obmc-ikvm | TCP:5900 | KVM 视频流代理 |
| phosphor-virtualmedia | NBDkit | UNIX Socket | 块设备请求 |
| NBDkit | Remote Storage | HTTPS/CIFS | 远程映像访问 |
| phosphor-virtualmedia | USB Gadget | /dev/nbdX | 块设备到 USB |
| obmc-ikvm | V4L2 | /dev/video0 | 视频捕获 |
| obmc-ikvm | USB Gadget | /dev/hidg* | 键盘鼠标输入 |
| USB Gadget | HOST | USB | 主机设备模拟 |

### 8.2 协议层级表

| 层级 | 协议 | 封装 | 传输层 |
|------|------|------|--------|
| 应用层 | Redfish API | JSON/HTTP | TCP |
| 应用层 | RFB/VNC | 二进制/WebSocket | TCP |
| 应用层 | D-Bus | D-Bus Message | UNIX Socket |
| 传输层 | NBD | NBD Protocol | TCP |
| 传输层 | USB | USB 2.0 | USB |
| 物理层 | Ethernet | IP | Copper/Fiber |

### 8.3 核心文件表

| 组件 | 关键文件/路径 | 功能 |
|------|-------------|------|
| phosphor-virtualmedia | /usr/bin/phosphor-virtualmedia | 主服务进程 |
| phosphor-virtualmedia | /etc/systemd/system/virtualmedia.service | 服务配置 |
| obmc-ikvm | /usr/bin/obmc-ikvm | KVM 主程序 |
| obmc-ikvm | /etc/systemd/system/ikvm.service | 服务配置 |
| bmcweb | /usr/bin/bmcweb | Web 服务器 |
| bmcweb | /etc/systemd/system/bmcweb.service | 服务配置 |
| USB Gadget | /configfs/usb_gadget/ | Gadget 配置 |
| V4L2 | /dev/video0 | 视频设备节点 |
| HID | /dev/hidg* | HID 设备节点 |
| NBD | /dev/nbd* | NBD 设备节点 |

### 8.4 知识点矩阵

| 功能 | phosphor-virtualmedia | phosphor-kvm | bmcweb | 知识点分类 |
|------|----------------------|--------------|--------|-----------|
| ISO 挂载 | ✓ | - | - | 虚拟介质 |
| USB 重定向 | ✓ | - | - | 虚拟介质 |
| 视频捕获 | - | ✓ | - | KVM |
| 键盘输入 | - | ✓ | - | KVM |
| 鼠标输入 | - | ✓ | - | KVM |
| WebSocket 代理 | - | - | ✓ | 基础设施 |
| Redfish API | - | - | ✓ | 基础设施 |
| D-Bus IPC | ✓ | ✓ | ✓ | 基础设施 |
| VNC/RFB | - | ✓ | ✓ | 协议 |
| NBD 协议 | ✓ | - | - | 协议 |
| USB Gadget | ✓ | ✓ | - | 驱动 |
| V4L2 | - | ✓ | - | 驱动 |

### 8.5 安全机制表

| 安全机制 | 实现位置 | 描述 |
|---------|---------|------|
| TLS 加密 | BMCWeb | HTTPS/WSS 传输加密 |
| 会话认证 | BMCWeb | Cookie/Token 认证 |
| PAM 授权 | BMCWeb | Linux PAM 后端认证 |
| CSRF 防护 | BMCWeb | Token-based CSRF 保护 |
| 权限控制 | D-Bus | D-Bus 策略控制 |
| 资源限制 | systemd | Cgroup 资源限制 |

---

## 参考资源

- [OpenBMC 官方项目](https://www.openbmc.org/)
- [phosphor-virtualmedia 源码](https://github.com/openbmc/phosphor-virtualmedia)
- [phosphor-kvm (obmc-ikvm) 源码](https://github.com/openbmc/phosphor-kvm)
- [bmcweb Web 服务器](https://github.com/openbmc/bmcweb)
- [phosphor-webui](https://github.com/openbmc/phosphor-webui)
- [RFB/VNC 协议规范](https://github.com/rfbproto/rfbproto)
- [NBD 协议规范](https://nbd.sourceforge.io/)
- [Linux USB Gadget API](https://www.kernel.org/doc/html/latest/usb/gadget/index.html)
- [V4L2 开发者文档](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/)

---

*文档生成日期：2026-04-27*
*OpenBMC 版本：2.10+*
