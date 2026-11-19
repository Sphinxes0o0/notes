---
type: entity
tags: [SDN, 网络, OpenFlow, 控制平面, 数据平面]
created: 2026-05-28
sources: [bookmark-sdn-guide]
---

# SDN架构 (Software Defined Networking)

## 定义

SDN是一种新的网络设计理念，实现**控制与转发分离**、**集中控制**和**开放API**。

## 关键要点

### 三层架构 (ONF定义)
- **应用层**: 各种业务应用
- **控制层**: 数据平面资源编排、维护网络拓扑和状态信息
- **数据层**: 数据处理、转发和状态收集

### 三个基本特征
1. **控制与转发分离**: 转发平面由受控转发设备组成，业务逻辑由控制面控制应用所控制
2. **开放API**: 通过南向API(控制器→转发设备)和北向API(应用↔控制器)实现无缝集成
3. **集中控制**: 逻辑集中的控制平面获得全局信息，全局调配和优化

### SDN优势
- 灵活性: 动态调整网络设备配置，无需人工配置每台设备
- 硬件简化: 白牌交换机等，只关注数据处理和转发，与业务特性解耦
- 自动化: 网络部署和运维自动化、故障诊断

### 发展历程
- 2006: Martin Casado博士提出SANE
- 2007: Ethane项目(SDN和OpenFlow前身)
- 2008: OpenFlow论文发表，NOX开源控制器
- 2009: SDN入选MIT科技评论"未来十大突破性技术"
- 2011: ONF成立，第一届ONS
- 2012: Google B4，VMware收购Nicira
- 2013: OpenDaylight项目诞生
- 2014: ONOS、P4诞生
- 2015: SD-WAN成为第二个成熟SDN应用市场

## 南向接口 vs 北向接口
- **南向接口**: 控制器到转发设备，OpenFlow是第一个开放标准
- **北向接口**: 应用到控制器，REST API为主

## 相关概念
- [[openflow]] — OpenFlow协议（第一个开放的南向接口）
- [[linux-ebpf-xdp]] — XDP（eBPF可编程数据面）
- [[load-balancing]] — 负载均衡（SDN核心功能之一）
- [[linux-net-stack-overview]] — Linux网络协议栈（数据平面）

## 来源详情
- [[bookmark-sdn-guide]] — SDN网络指南
