# ONOS

## 概述

ONOS (Open Network Operating System) 是面向服务提供商和企业骨干网络的开源SDN网络操作系统。设计目标包括可靠性、性能和灵活性。

## 架构

### 系统分层

包含分层架构图，显示不同组件及其关系。

### 组件和服务

- **Modularity**: ONOS由功能模块组成，每个模块提供特定服务，具有组件生命周期管理
- **Openness**: 提供开放的北向和南向API用于应用开发和南向插件
- **Abstraction**: 统一的网络资源和元素模型使第三方SDN应用程序能够互操作
- **Simplicity**: 屏蔽复杂的分布式机制，只暴露业务接口

### ONOS集群

- 分布式架构，多个实例
- 对称设计，每个实例运行相同软件
- **容错和弹性扩展**: 节点故障时集群保持运行，支持动态添加节点
- **位置透明**: 客户端可以与任何实例交互
- **集群通信**: Gossip协议用于弱一致性，Raft算法用于强一致性

通过集群机制实现高可靠性。

## 图片

![ONOS图](images/onos.png)
![ONOS子系统图](images/onos-subsystem.png)
![ONOS通信图](images/onos-communication.png)

## 参考

- ONOS Website: http://onosproject.org/
- ONOS Wiki: https://wiki.onosproject.org
- Huawei ONOS Architecture Analysis
- SDNLab articles on ONOS
