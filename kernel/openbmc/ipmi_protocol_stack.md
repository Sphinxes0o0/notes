# OpenBMC IPMI 协议栈深度分析

## 概述

IPMI（Intelligent Platform Management Interface，智能平台管理接口）是一种开放标准的硬件管理接口规范，广泛应用于服务器和嵌入式系统。OpenBMC 作为开源的 BMC（Baseboard Management Controller）固件栈，实现了完整的 IPMI 协议栈，包括命令处理、FRU 数据管理、SEL 事件日志和传感器读取等功能。

本文档基于 Linux 内核 IPMI 子系统实现（`drivers/char/ipmi/`）和 OpenBMC 开源组件，对 IPMI 协议栈进行深度技术分析。

---

## 一、IPMI 命令帧格式

### 1.1 基本消息格式

IPMI 消息分为请求（Request）和响应（Response）两种类型，采用 NetFn/LUN + CMD + Data 的基本结构。

**请求消息格式：**

```
+-----------+-----+------+
| NetFn/LUN | Cmd | Data |
+-----------+-----+------+
  1 byte    1 byte N bytes
```

**响应消息格式：**

```
+-----------+-----+------+------+
| NetFn/LUN | Cmd | CC   | Data |
+-----------+-----+------+------+
  1 byte    1 byte 1 byte N bytes
```

响应消息相比请求消息增加了 CC（Completion Code，完成码）字段，位于 CMD 之后。

### 1.2 NetFn 字段定义

NetFn（Network Function）占用 6 位，与 LUN（Logical Unit Number）共用一个字节，格式为 `NNNNNNLL`：

| NetFn 值 | 功能域 | 请求 NetFn | 响应 NetFn |
|----------|--------|------------|------------|
| 0x04 | 传感器/事件 (Sensor/Event) | 0x04 | 0x05 |
| 0x06 | 应用 (Application) | 0x06 | 0x07 |
| 0x08 | 固件 (Firmware) | 0x08 | 0x09 |
| 0x0A | 存储 (Storage) | 0x0A | 0x0B |
| 0x0C | 传输 (Transport) | 0x0C | 0x0D |
| 0x0E | 群组 (Group) | 0x0E | 0x0F |
| 0x2C | 关闭/重启 (Shutdown/Restart) | 0x2C | 0x2D |

**关键 NetFn 命令定义**（参见 `include/uapi/linux/ipmi_msgdefs.h`）：

```c
#define IPMI_NETFN_SENSOR_EVENT_REQUEST    0x04
#define IPMI_NETFN_SENSOR_EVENT_RESPONSE   0x05
#define IPMI_NETFN_APP_REQUEST             0x06
#define IPMI_NETFN_APP_RESPONSE            0x07
#define IPMI_NETFN_STORAGE_REQUEST         0x0a
#define IPMI_NETFN_STORAGE_RESPONSE        0x0b
#define IPMI_NETFN_FIRMWARE_REQUEST        0x08
#define IPMI_NETFN_FIRMWARE_RESPONSE      0x09
```

### 1.3 完成码（Completion Code）

完成码位于响应消息的 CMD 之后，用于表示命令执行结果：

| 完成码 | 名称 | 说明 |
|--------|------|------|
| 0x00 | NO_ERROR | 命令成功执行 |
| 0xC0 | NODE_BUSY_ERR | BMC 节点忙 |
| 0xC1 | INVALID_COMMAND_ERR | 无效命令 |
| 0xC3 | TIMEOUT_ERR | 命令超时 |
| 0xC6 | ERR_MSG_TRUNCATED | 消息被截断 |
| 0xC7 | REQ_LEN_INVALID_ERR | 请求长度无效 |
| 0xC8 | REQ_LEN_EXCEEDED_ERR | 请求长度超限 |
| 0xD5 | NOT_IN_MY_STATE_ERR | 状态不匹配 |
| 0xFF | ERR_UNSPECIFIED | 未指定错误 |

### 1.4 校验和问题

IPMI 协议涉及两种校验和计算：

**消息校验和格式：**

```
原始消息: [Addr] [NetFn/LUN] [Checksum1] [Cmd] [Data...] [Checksum2]
                    ^ RS LUN             ^请求方校验          ^响应方校验
```

- **Checksum1**：对 `[Addr] + [NetFn/LUN]` 进行校验
- **Checksum2**：对 `[Cmd] + [Data...]` 进行校验

校验和算法：取 8 位二补数（`256 - (sum & 0xFF)`）

---

## 二、KCS 接口驱动分析

### 2.1 KCS 协议概述

KCS（Keyboard Controller Style）是 IPMI 最常用的系统接口形式，通过 I/O 端口或内存映射 I/O 与 BMC 通信。KCS 接口使用三个 I/O 端口：

| 端口偏移 | 名称 | 方向 | 说明 |
|----------|------|------|------|
| 0 | Data | 双向 | 数据寄存器 |
| 1 | Command/Status | 双向 | 命令/状态寄存器 |
| 2 | flags (可选) | 只读 | 标志寄存器 |

### 2.2 KCS 状态机

KCS 接口采用状态机机制（`ipmi_kcs_sm.c`），核心状态定义如下：

```c
enum kcs_states {
    KCS_IDLE,           // 接口空闲
    KCS_START_OP,       // 开始操作
    KCS_WAIT_WRITE_START,   // 等待写入开始
    KCS_WAIT_WRITE,     // 等待写入
    KCS_WAIT_WRITE_END, // 等待写入结束
    KCS_WAIT_READ,      // 等待读取
    KCS_ERROR0,         // 错误处理阶段0
    KCS_ERROR1,         // 错误处理阶段1
    KCS_ERROR2,         // 错误处理阶段2
    KCS_ERROR3,         // 错误处理阶段3
    KCS_HOSED           // 接口故障
};
```

### 2.3 KCS 控制码

KCS 接口定义的控制码：

| 控制码 | 名称 | 说明 |
|--------|------|------|
| 0x60 | GET_STATUS_ABORT | 中止当前操作 |
| 0x61 | WRITE_START | 开始写入 |
| 0x62 | WRITE_END | 结束写入 |
| 0x68 | READ_BYTE | 读取字节 |

### 2.4 KCS 状态寄存器

KCS 状态寄存器各位定义：

```c
// 状态寄存器位字段
#define GET_STATUS_STATE(status) (((status) >> 6) & 0x03)
#define KCS_IDLE_STATE  0  // 空闲状态
#define KCS_READ_STATE  1  // 读取状态
#define KCS_WRITE_STATE 2  // 写入状态
#define KCS_ERROR_STATE 3  // 错误状态
#define GET_STATUS_ATN(status)  ((status) & 0x04)  // ATTN 标志
#define GET_STATUS_IBF(status)  ((status) & 0x02)  // 输入缓冲区满
#define GET_STATUS_OBF(status)  ((status) & 0x01)  // 输出缓冲区满
```

### 2.5 KCS 数据结构

```c
struct si_sm_data {
    enum kcs_states  state;
    struct si_sm_io *io;
    unsigned char    write_data[MAX_KCS_WRITE_SIZE];  // 写缓冲区
    int              write_pos;    // 写位置
    int              write_count;  // 写计数
    int              orig_write_count;
    unsigned char    read_data[MAX_KCS_READ_SIZE];    // 读缓冲区
    int              read_pos;     // 读位置
    int              truncated;    // 截断标志
    unsigned int     error_retries;
    long             ibf_timeout;  // IBF 超时
    long             obf_timeout;  // OBF 超时
    unsigned long    error0_timeout;
};
```

---

## 三、SMIC 接口驱动分析

### 3.1 SMIC 协议概述

SMIC（System Management Interface Chip）是另一种 IPMI 系统接口，与 KCS 类似但状态机略有不同。SMIC 使用三个 I/O 端口：

| 端口偏移 | 名称 | 说明 |
|----------|------|------|
| 0 | Data | 数据寄存器 |
| 1 | Status | 状态寄存器 |
| 2 | Flags | 标志寄存器 |

### 3.2 SMIC 状态机

SMIC 接口状态定义（`ipmi_smic_sm.c`）：

```c
enum smic_states {
    SMIC_IDLE,         // 空闲状态
    SMIC_START_OP,     // 开始操作
    SMIC_OP_OK,       // 操作成功
    SMIC_WRITE_START,  // 开始写入
    SMIC_WRITE_NEXT,  // 继续写入
    SMIC_WRITE_END,   // 写入结束
    SMIC_WRITE2READ,  // 写转读
    SMIC_READ_START,  // 开始读取
    SMIC_READ_NEXT,   // 继续读取
    SMIC_READ_END,    // 读取结束
    SMIC_HOSED        // 接口故障
};
```

### 3.3 SMIC 标志寄存器

SMIC 标志寄存器位定义：

```c
#define SMIC_RX_DATA_READY   0x80  // 接收数据就绪
#define SMIC_TX_DATA_READY   0x40  // 发送数据就绪
#define SMIC_SMI             0x10  // SMI 标志
#define SMIC_EVM_DATA_AVAIL  0x08  // 事件数据可用
#define SMIC_SMS_DATA_AVAIL  0x04  // SMS 数据可用
#define SMIC_FLAG_BSY        0x01  // 忙标志
```

### 3.4 SMIC 错误码

```c
#define EC_NO_ERROR         0x00  // 无错误
#define EC_ABORTED          0x01  // 操作中止
#define EC_ILLEGAL_CONTROL  0x02  // 非法控制码
#define EC_NO_RESPONSE      0x03  // 无响应
#define EC_ILLEGAL_COMMAND  0x04  // 非法命令
#define EC_BUFFER_FULL      0x05  // 缓冲区满
```

---

## 四、Linux 内核 IPMI 架构

### 4.1 层级架构

Linux 内核 IPMI 子系统采用分层架构：

```
+-------------------+
|   用户空间应用    |
+-------------------+
        |
        v
+-------------------+
|  IPMI 字符设备    |  (ipmi_devintf.c)
|  /dev/ipmi0       |
+-------------------+
        |
        v
+-------------------+
|  消息处理器       |  (ipmi_msghandler.c)
|  消息路由/分发    |
+-------------------+
        |
        v
+-------------------+
|  SMI 接口层       |  (ipmi_si_intf.c)
|  策略/定时器管理  |
+-------------------+
        |
        v
+-------------------+
|  状态机层         |  (ipmi_kcs_sm.c, ipmi_smic_sm.c, ipmi_bt_sm.c)
|  KCS/SMIC/BT     |
+-------------------+
        |
        v
+-------------------+
|  硬件抽象层       |  (ipmi_si_port_io.c, ipmi_si_mem_io.c)
+-------------------+
```

### 4.2 核心数据结构

**SMI 信息结构体**（`ipmi_si_intf.c`）：

```c
struct smi_info {
    int                    si_num;
    struct ipmi_smi       *intf;
    struct si_sm_data     *si_sm;         // 状态机数据
    const struct si_sm_handlers *handlers;
    spinlock_t             si_lock;
    struct ipmi_smi_msg   *waiting_msg;   // 等待中的消息
    struct ipmi_smi_msg   *curr_msg;      // 当前消息
    enum si_intf_state    si_state;       // 接口状态
    struct si_sm_io       io;             // I/O 抽象
    unsigned char          msg_flags;      // 消息标志
    bool                   has_event_buffer;
    atomic_t               req_events;
    struct timer_list      si_timer;       // 定时器
    struct ipmi_device_id  device_id;      // 设备 ID
    atomic_t               stats[SI_NUM_STATS];
};
```

**SMI 消息结构体**（`include/linux/ipmi_smi.h`）：

```c
struct ipmi_smi_msg {
    struct list_head link;
    enum ipmi_smi_msg_type type;
    long msgid;
    struct ipmi_recv_msg *recv_msg;
    int           data_size;
    unsigned char data[IPMI_MAX_MSG_LENGTH];
    int           rsp_size;
    unsigned char rsp[IPMI_MAX_MSG_LENGTH];
    void (*done)(struct ipmi_smi_msg *msg);
};
```

### 4.3 IPMI 用户消息结构

用户空间消息格式（`include/uapi/linux/ipmi.h`）：

```c
struct ipmi_msg {
    unsigned char  netfn;     // Network Function
    unsigned char  cmd;       // Command
    unsigned short data_len;  // 数据长度
    unsigned char  __user *data;
};

struct ipmi_req {
    unsigned char __user *addr;
    unsigned int  addr_len;
    long    msgid;
    struct ipmi_msg msg;
};

struct ipmi_recv {
    int     recv_type;  // 接收类型
    unsigned char __user *addr;
    unsigned int  addr_len;
    long    msgid;
    struct ipmi_msg msg;
};
```

---

## 五、OpenBMC ipmid 守护进程

### 5.1 概述

ipmid 是 OpenBMC 中的 IPMI 守护进程，负责接收和处理来自系统的 IPMI 命令。OpenBMC 的 ipmid 实现位于用户空间，通过 D-Bus 与其他系统服务交互。

### 5.2 架构特点

OpenBMC ipmid 的设计特点：

1. **D-Bus 集成**：ipmid 通过 D-Bus 与phosphor-logging、phosphor-dbus-interfaces 等服务通信
2. **handler 注册机制**：支持动态注册命令处理器
3. **NetFn/CMD 分派**：根据 NetFn 和 CMD 分派到对应的 handler

### 5.3 命令处理流程

```
IPMI 请求 (KCS/SMIC)
       |
       v
  ipmid 守护进程
       |
       v
   解析 NetFn/CMD
       |
       v
   查找对应 Handler
       |
       v
   执行命令处理
       |
       v
   访问系统资源 (D-Bus)
       |
       v
   返回响应数据
```

---

## 六、FRU 解析器 (ipmi-fru-parser)

### 6.1 FRU 概述

FRU（Field Replaceable Unit，可现场更换单元）是 IPMI 规范中用于存储硬件设备信息的标准格式。FRU 数据通常存储在 EEPROM 或 NVRAM 中，包含以下信息：

- 产品信息（制造商、型号、序列号）
- 板卡信息（PCB 版本、序列号）
- 区域映射（多区域结构）

### 6.2 FRU 存储格式

FRU 数据采用多区域结构：

```
+--------+--------+--------+--------+--------+
| Header | Inter | Chassis| Board  | Product|
|  内部   |  内部  |  Info  |  Info  |  Info  |
+--------+--------+--------+--------+--------+
  1-8B     0-7B   0-256B  0-256B  0-256B
```

### 6.3 FRU 头部格式

```c
struct fru_header {
    uint8_t  format_version;  // 格式版本 (0x01)
    uint8_t  internal_offset; // 内部使用区域偏移
    uint8_t  chassis_offset; // 机箱区域偏移
    uint8_t  board_offset;    // 板卡区域偏移
    uint8_t  product_offset;  // 产品区域偏移
    uint8_t  pad;             // 填充
    uint8_t  checksum;        // 头部校验和
};
```

### 6.4 FRU 区域类型

| 区域类型 | 内容 | 典型大小 |
|----------|------|----------|
| Internal Use | 厂商内部数据 | 0-7B |
| Chassis Info | 机箱信息 | 0-256B |
| Board Info | 板卡信息 | 0-256B |
| Product Info | 产品信息 | 0-256B |
| Multi-Record | 多记录区域 | 可变 |

---

## 七、SEL 事件日志 (ipmi-sel)

### 7.1 SEL 概述

SEL（System Event Log，系统事件日志）是 IPMI 规范中用于记录系统硬件事件的日志存储机制。SEL 存储在 BMC 的持久存储中，可通过 IPMI 命令访问。

### 7.2 SEL 记录格式

每条 SEL 记录包含 16 字节：

```c
struct sel_record {
    uint16_t record_id;        // 记录 ID
    uint8_t  record_type;     // 记录类型
    uint32_t timestamp;        // 时间戳
    uint16_t generator_id;    // 生成器 ID
    uint8_t  evm_revision;    // 事件格式版本
    uint8_t  sensor_type;     // 传感器类型
    uint8_t  sensor_number;   // 传感器编号
    uint8_t  event_direction; // 事件方向
    uint8_t  event_data[3];   // 事件数据
};
```

### 7.3 SEL 管理命令

| 命令 | NetFn/Cmd | 说明 |
|------|-----------|------|
| Get SEL Info | 0x0A/0x40 | 获取 SEL 信息 |
| Get SEL Allocation Info | 0x0A/0x41 | 获取分配信息 |
| Read SEL Entry | 0x0A/0x43 | 读取 SEL 条目 |
| Add SEL Entry | 0x0A/0x44 | 添加 SEL 条目 |
| Clear SEL | 0x0A/0x47 | 清空 SEL |
| Get SEL Time | 0x0A/0x48 | 获取 SEL 时间 |
| Set SEL Time | 0x0A/0x49 | 设置 SEL 时间 |

### 7.4 OpenBMC ipmi-sel 实现

OpenBMC 的 ipmi-sel 服务特点：

1. **D-Bus 集成**：SEL 条目通过 D-Bus 暴露
2. **日志持久化**：SEL 数据存储在文件系统中
3. **事件转发**：支持将 SEL 事件转发到系统日志

---

## 八、传感器读取 (ipmi-sensor/SDR)

### 8.1 SDR 概述

SDR（Sensor Data Repository，传感器数据仓库）是 IPMI 中存储传感器元数据的机制。SDR 记录了每个传感器的详细信息，包括类型、阈值、操作特性等。

### 8.2 SDR 记录类型

| 类型 | 说明 |
|------|------|
| Full Sensor | 完整传感器记录 (0x01) |
| Compact Sensor | 紧凑传感器记录 (0x02) |
| Event-only Sensor | 仅事件传感器 (0x03) |
| Entity Association | 实体关联 (0x08) |
| Device Relative Entity | 设备相对实体 (0x09) |
| Generic Device Locator | 通用设备定位器 (0x10) |
| fru Device Locator | FRU 设备定位器 (0x11) |
| IPMB Device Locator | IPMB 设备定位器 (0x12) |
| IPMB Extension | IPMB 扩展 (0x13) |

### 8.3 SDR 命令

| 命令 | NetFn/Cmd | 说明 |
|------|-----------|------|
| Get SDR Repository Info | 0x0A/0x20 | 获取 SDR 信息 |
| Get SDR Allocation Info | 0x0A/0x21 | 获取分配信息 |
| Reserve SDR Repository | 0x0A/0x22 | 预约 SDR |
| Get SDR | 0x0A/0x23 | 读取 SDR 条目 |

### 8.4 传感器命令

| 命令 | NetFn/Cmd | 说明 |
|------|-----------|------|
| Get Sensor Reading | 0x04/0x2D | 读取传感器值 |
| Get Sensor Thresholds | 0x04/0x27 | 获取阈值 |
| Set Sensor Thresholds | 0x04/0x26 | 设置阈值 |
| Get Sensor Event Enable | 0x04/0x29 | 获取事件使能 |
| Set Sensor Event Enable | 0x04/0x28 | 设置事件使能 |

---

## 九、消息处理流程详解

### 9.1 消息发送流程

```
用户空间调用 ioctl(IPMICTL_SEND_COMMAND)
        |
        v
ipmi_ioctl() 消息验证
        |
        v
ipmi_send_request() 添加到发送队列
        |
        v
start_new_msg() 分配消息 ID
        |
        v
check_msg_timeout() 启动超时计时器
        |
        v
do_send() 调用 SMI sender
        |
        v
si_sm_transition() 状态机推进
        |
        v
write_status() / write_data() I/O 操作
```

### 9.2 消息接收流程

```
硬件中断或轮询触发
        |
        v
si_sm_event() 状态机事件处理
        |
        v
read_status() / read_data() 读取数据
        |
        v
handle_new_recv_msgs() 处理新消息
        |
        v
deliver_recv_msg() 消息分发
        |
        v
ipmi_smi_msg_received() 递送到上层
        |
        v
handle_one_recv_msg() 处理单条消息
        |
        v
deliver_response() 或 deliver_local() 分派响应
```

### 9.3 状态机事件处理

```c
enum si_sm_result {
    SI_SM_CALL_WITHOUT_DELAY, // 立即再次调用
    SI_SM_CALL_WITH_DELAY,    // 延迟后调用
    SI_SM_CALL_WITH_TICK_DELAY, // 延迟至少一个 tick
    SI_SM_TRANSACTION_COMPLETE, // 事务完成
    SI_SM_IDLE,               // 空闲状态
    SI_SM_HOSED,               // 硬件故障
    SI_SM_ATTN                 // ATTN 标志
};
```

---

## 十、接口检测与初始化

### 10.1 接口类型检测

Linux 内核 IPMI 驱动支持的接口类型：

```c
const char *const si_to_str[] = { "invalid", "kcs", "smic", "bt", NULL };

enum si_type {
    SI_KCS,
    SI_SMIC,
    SI_BT,
    SI_TYPE_COUNT
};
```

### 10.2 PCI/平台设备检测

IPMI 接口可以通过多种方式检测：

1. **PCI 检测**：通过 PCI 配置空间枚举
2. **ACPI 检测**：通过 ACPI _IFT 表
3. **SMBIOS 检测**：通过 Type 42 条目
4. **DMI 检测**：通过 DMI 匹配表
5. **命令行参数**：通过 modprobe 或启动参数

### 10.3 接口初始化序列

```
ipmi_si_probe()
        |
        v
try_smi_init()
        |
        v
setup_ports() 或 setup_mem() I/O 资源分配
        |
        v
smi_info->handlers->init_data() 初始化状态机
        |
        v
start_ipmi_engine() 启动消息处理引擎
        |
        v
ipmi_add_smi() 向消息处理器注册
```

---

## 十一、知识点关联表

### 11.1 协议层次关联

| 层次 | 组件 | 文件 | 功能 |
|------|------|------|------|
| 用户接口 | 字符设备 | ipmi_devintf.c | /dev/ipmi0 设备访问 |
| 消息路由 | 消息处理器 | ipmi_msghandler.c | 命令/响应分发 |
| SMI 接口 | 接口管理 | ipmi_si_intf.c | 策略/定时器 |
| 状态机 | KCS 驱动 | ipmi_kcs_sm.c | KCS 协议实现 |
| 状态机 | SMIC 驱动 | ipmi_smic_sm.c | SMIC 协议实现 |
| 状态机 | BT 驱动 | ipmi_bt_sm.c | BT 协议实现 |
| I/O 抽象 | 端口 I/O | ipmi_si_port_io.c | x86 I/O 端口 |
| I/O 抽象 | 内存 I/O | ipmi_si_mem_io.c | 内存映射 I/O |

### 11.2 NetFn 与功能对应

| NetFn | 功能域 | 主要命令 | 数据结构 |
|-------|--------|----------|----------|
| 0x04/0x05 | 传感器/事件 | Get Sensor Reading, Set Event Enable | sensor_type |
| 0x06/0x07 | 应用 | Get Device ID, Cold Reset, Get MSG Flags | ipmi_device_id |
| 0x08/0x09 | 固件 | Get Firmware Version, BMC Ready | - |
| 0x0A/0x0B | 存储 | Get SEL Info, Add SEL Entry, Get SDR Info | sel_record, sdr_record |
| 0x0C/0x0D | 传输 | Get LAN Config, Set LAN Config | lan_config |
| 0x2C/0x2D | 关机/重启 | Graceful Shutdown | - |

### 11.3 接口类型特征

| 特性 | KCS | SMIC | BT |
|------|-----|------|-----|
| I/O 端口数 | 2 | 3 | 2-3 |
| 最大消息长度 | 256B | 80B | 256B |
| 状态机复杂度 | 中等 | 较高 | 高 |
| 中断支持 | 可选 | 可选 | 必需 |
| 厂商支持 | Intel, Nuvoton | HP | Intel |

### 11.4 内核-用户空间接口

| IOCTL | 功能 | 数据结构 |
|-------|------|----------|
| IPMICTL_SEND_COMMAND | 发送命令 | ipmi_req |
| IPMICTL_RECEIVE_MSG | 接收消息 | ipmi_recv |
| IPMICTL_REGISTER_FOR_CMD | 注册命令监听 | ipmi_cmdspec |
| IPMICTL_SET_GETS_EVENTS | 设置事件接收 | int |
| IPMICTL_SET_TIMING_PARMS | 设置时序参数 | ipmi_timing_parms |

### 11.5 OpenBMC 组件映射

| OpenBMC 组件 | 功能 | 替代内核组件 |
|--------------|------|--------------|
| ipmid | IPMI 命令处理 | ipmi_msghandler.c |
| ipmi-fru-parser | FRU 解析 | 用户空间实现 |
| ipmi-sel | SEL 日志管理 | ipmi_msghandler.c |
| phosphor-logging | 事件日志 | journald |
| phosphor-dbus-interfaces | D-Bus 接口 | kernel netlink |

---

## 十二、扩展阅读

### 12.1 相关规范文档

- IPMI v2.0 规范 (Document Revision 1.1)
- Intelligent Platform Management Interface Specification v1.5
- IPMI Platform Management FRU Information Storage Definition v1.0
- Sensor Data Record (SDR) Repository Specification v1.0

### 12.2 内核源码位置

```
drivers/char/ipmi/
├── ipmi_si_intf.c      # SMI 接口管理
├── ipmi_kcs_sm.c       # KCS 状态机
├── ipmi_smic_sm.c      # SMIC 状态机
├── ipmi_bt_sm.c        # BT 状态机
├── ipmi_msghandler.c   # 消息处理
├── ipmi_devintf.c      # 字符设备接口
├── ipmi_ssif.c         # SSIF 接口 (SMBus)
├── ipmi_ipmb.c         # IPMB 协议
└── ipmi_si_sm.h        # 状态机接口定义
```

### 12.3 关键头文件

```
include/uapi/linux/ipmi.h         # 用户空间 API
include/uapi/linux/ipmi_msgdefs.h # 消息定义
include/linux/ipmi_smi.h          # SMI 接口定义
include/linux/ipmi.h              # 内核 API
```

---

*文档版本: 1.0*
*分析基于: Linux Kernel IPMI 子系统 + OpenBMC 开源组件*
