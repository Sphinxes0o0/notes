# OpenFlow

## OpenFlow原理

OpenFlow是第一个开放的南向接口协议，由Nick McKeown在2008年提出，实现SDN架构中的控制与转发分离。

### OpenFlow交换机

组件包括：
- OpenFlow通道（与控制器的通信通道）
- 流表（flow table）
- 端口（物理、逻辑、保留端口）
- 组表（group table）
- Meter表（计量/速率限制）

### 流表

每个流条目包含：
- 匹配域（match fields: input port, packet header, metadata）
- 优先级（priority）
- 指令集（instructions）
- 计数器（counters）
- 计时器（timers）
- Cookie

### OpenFlow通道

三种消息类型：
1. **controller-to-switch:** 初始化和管理消息
2. **asynchronous:** 交换机发起的事件通知
3. **symmetric:** 无需许可的消息（Hello, Echo, Error）

通信通常使用TLS或直接TCP。

## 图片

![OpenFlow图](images/openflow.png)
![Flow图](images/flow.png)
![Match图](images/item.png)
![匹配图](images/match.png)
![指令图](images/instruction.png)
![Meter图](images/meter.png)

## 参考

- [OpenFlow Official Site](https://www.opennetworking.org/sdn-resources/openflow)
- [OpenFlow Specification](https://www.opennetworking.org/technical-communities/areas/specification)
