# 自己连自己的TCP连接

**Source:** https://plantegg.github.io/2020/07/01/如何创建一个自己连自己的TCP连接/
**NIDS Relevance:** ★★★★☆ (隐蔽通道/evasion技术的直接参考)

## 核心内容

### 1. Self-Connecting TCP机制
源和目标相同的socket (`192.168.0.79:18082 -> 192.168.0.79:18082`)。
当`bind()`在`connect()`之前调用，且没有`listen()`时发生。

### 2. TCP Simultaneous Open
利用TCP simultaneous open特性 — socket在发送SYN后能接收SYN（而非预期的SYN+ACK）。
代码位置: `net/ipv4/tcp_input.c:5921`，内核明确处理此case："can be connect to self"。

### 3. 四元组唯一性 vs 端口唯一性
TCP连接要求唯一的`(src-ip, src-port, dest-ip, dest-port)`四元组，而非单个端口唯一。
同一端口如18089可出现多次（只要目标端口不同）。

### 4. Ephemeral Port Range误解
`/proc/sys/net/ipv4/ip_local_port_range` (默认10000-65535) 仅控制OS分配的ephemeral端口，不限制总连接数。

### 5. bind() vs connect()状态差异
- **bind()**: 内核只知道src_ip/src_port，无法检测四元组唯一性，端口冲突被强制执行
- **connect()**: 知道完整四元组，允许端口复用（只要四元组唯一）

### NIDS Relevance
1. **Detection Evasion**: 自连接可能绕过基于端口的签名规则（期望client/server端口不同）
2. **State Tracking Challenges**: Simultaneous open产生异常handshake（SYN交换而非SYN-SYN/ACK-SYN）
3. **Single-Socket Anomaly**: 正常连接需要两个socket；自连接一个socket作为两端
4. **Port Exhaustion**: 理解端口复用机制揭示了基于端口的连接限制常被高估

## 关联概念
-  — TCP状态机
-  — 连接跟踪
