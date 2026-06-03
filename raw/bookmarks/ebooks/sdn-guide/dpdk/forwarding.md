# DPDK报文转发模型

## 核心内容

本文档介绍DPDK报文转发框架，主要包括三种转发模型：

1. **基本网络包处理流程**：Packet input → Pre-processing → Classification → Queuing → Scheduling → Accelerator → Egress → Output

2. **DPDK Run to Completion模型**：每个物理核处理报文完整生命周期，线程绑定到特定核上

3. **DPDK Pipeline模型**：不同功能模块（解析、查表、修改、发送）组成处理引擎，通过输入输出连接

## 关键算法

- **精确匹配**：使用CRC32和J hash进行哈希签名，解决冲突
- **LPM最长前缀匹配**：小于24位前缀一次访存，大于24位需两次访存
- **ACL库**：支持N元组匹配规则

## 图片

![转发模型图1](../images/14779992425286.jpg)
![转发模型图2](../images/14779998291041.jpg)
![转发模型图3](../images/14779998372971.jpg)
![转发模型图4](../images/14779998722257.jpg)
![转发模型图5](../images/14779998808151.jpg)
![转发模型图6](../images/14780002108908.jpg)
![转发模型图7](../images/14780002930693.jpg)
![转发模型图8](../images/14780007087819.jpg)
![转发模型图9](../images/14780007458818.jpg)

## 技术要点

DPDK pipeline由三大部分组成，支持Packet I/O、Flow classification、Firewall、Routing、Metering等功能模块。Packet distributor API用于包分发处理。
