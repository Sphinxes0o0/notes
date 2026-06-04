# AF_XDP技术详解

**Source:** https://rexrock.github.io/post/af_xdp1/
**NIDS Relevance:** ★★★★★ (零拷贝内联NIDS的核心技术)

## 核心内容

### AF_XDP架构
- 利用`bpf_redirect_map()`将packet直接重定向到用户态内存
- 使用`BPF_MAP_TYPE_XSKMAP`关联queue ID和socket fd
- **零拷贝**: RX和TX共享同一UMEM，无需在用户态和内核间复制packet

### UMEM内存模型
UMEM将内存划分为固定大小的chunk，四个ring管理packet流：
- **FILL RING**: 用户→内核缓冲供给
- **COMPLETION RING**: 内核→用户发送完成确认
- **RX RING**: 入向packet
- **TX RING**: 出向packet

用户通过`mmap()`访问这些ring，通过`getsockopt()`获取kernel结构体偏移。

### XDP Program Hook
```c
if (bpf_map_lookup_elem(&xsks_map, &index))
    return bpf_redirect_map(&xsks_map, index, 0);
```
XDP程序检查queue是否有绑定的AF_XDP socket，有则重定向。

### 驱动支持
需要驱动级XDP支持`XDP_REDIRECT`功能。已用于：OVS、DPDK、Cilium。

### NIDS Relevance
- 用户态直接访问packet，最小延迟
- 适合inline NIDS应用（全packet可见性）
- 对比DPDK: AF_XDP不需要专用大页，API更简单
- 对比XDP-only: AF_XDP支持完整TX path，方便做主动响应（如reset连接）

## 关键引用
> "RX和TX可以共享同一UMEM，因此不必在RX和TX之间复制数据包"

## 关联概念
-  — DPDK是另一种kernel bypass方案
-  — XDP/eBPF基础
- NIDS架构: AF_XDP → Snort3 inline detection
