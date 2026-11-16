---
type: entity
tags: [OpenFlow, SDN, 南向接口, 流表, 网络协议]
created: 2026-05-28
sources: [bookmark-sdn-guide]
---

# OpenFlow

## 定义

2008年Nick McKeown提出的第一个开放的南向接口协议，实现SDN架构中的控制与转发分离。

## 关键要点

### OpenFlow交换机组件
- **OpenFlow通道**: 与控制器的通信通道(TLS或TCP)
- **流表** (Flow Table): 数据包匹配和动作执行
- **端口** (Port): 物理端口、逻辑端口、保留端口
- **组表** (Group Table): 组播/多路径转发
- **Meter表**: 计量/速率限制

### 流条目结构
每个流条目包含:
- **匹配域** (Match Fields): 输入端口、包头(TCP/UDP/IP/MAC)、元数据
- **优先级** (Priority): 越高越先匹配
- **指令集** (Instructions): 执行动作或修改流水线
- **计数器** (Counters): 匹配统计
- **计时器** (Timers): 超时管理
- **Cookie**: 控制器设置的模糊标识

### 三种消息类型
1. **Controller-to-Switch**: 初始化和管理消息
   - FeaturesRequest/Reply, Configuration, PacketOut, FlowMod
2. **Asynchronous**: 交换机发起的异步事件通知
   - PacketIn, FlowRemoved, PortStatus, Error
3. **Symmetric**: 无需许可的消息
   - Hello, EchoRequest/Reply, Error

### 与SDN架构关系
- 是SDN架构中**控制层↔数据层**通信的标准南向接口
- 驱动转发平面可编程化

## 版本演进
- OpenFlow 1.0: 单流表
- OpenFlow 1.1: 多流表、组表、Meter表
- OpenFlow 1.3+: Meter表、多控制器
- OpenFlow 1.4: 流条目的bundle消息

## 相关概念
- [[sdn-architecture]] — SDN整体架构
- [[linux-ebpf-xdp]] — XDP（另一种可编程数据面方案）
- [[load-balancing]] — 负载均衡（OpenFlow应用场景）

## 来源详情
- [[bookmark-sdn-guide]] — SDN网络指南
- OpenFlow规范: https://www.opennetworking.org/technical-communities/areas/specification
