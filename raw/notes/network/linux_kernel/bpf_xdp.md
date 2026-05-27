# BPF/XDP 钩子

## 1. 模块架构

### 1.1 功能概述

XDP (Express Data Path) 是 Linux 网络栈的高性能入口点，在内核早期处理网络包。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `kernel/bpf/devmap.c` | XDP 设备映射 |
| `net/core/filter.c` | BPF 过滤器 |
| `include/net/xdp.h` | XDP 定义 |

## 2. XDP 架构

### 2.1 XDP 处理阶段

```
packet arrival
    |
    +-> NIC driver (DMA to ring buffer)
    |
    +-> XDP (before skb allocation)
    |       |
    |       +-> XDP_PASS (继续正常处理)
    |       +-> XDP_DROP (丢弃包)
    |       +-> XDP_TX (发送回同一网卡)
    |       +-> XDP_REDIRECT (重定向到其他接口或 AF_XDP)
    |
    +-> skb allocation (如果没有被 XDP 处理)
    |
    +-> netif_receive_skb()
```

### 2.2 XDP 优点

```
1. 在 skb 分配前处理 - 节省内存分配
2. 在 IRQ 上下文中处理 - 极低延迟
3. 直接访问 DMA 缓冲区 - 零拷贝
4. 可编程 - 灵活的数据平面
```

## 3. BPF_PROG_TYPE_XDP

### 3.1 注册 XDP 程序

```c
// net/core/dev.c
int dev_change_xdp_fd(struct net_device *dev, int fd)
{
    struct bpf_prog *prog;

    // 获取 BPF 程序
    prog = bpf_prog_get(fd);
    if (IS_ERR(prog))
        return PTR_ERR(prog);

    // 检查程序类型
    if (prog->type != BPF_PROG_TYPE_XDP)
        return -EINVAL;

    // 附加到设备
    return dev_xdp_attach(dev, prog);
}
```

### 3.2 XDP 程序结构

```c
// XDP 程序示例
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

SEC("xdp")
int xdp_parser(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_DROP;

    if (eth->h_proto == htons(ETH_P_IP)) {
        struct iphdr *ip = data + sizeof(*eth);
        if ((void *)(ip + 1) > data_end)
            return XDP_DROP;

        // 处理 IPv4
    }

    return XDP_PASS;
}
```

## 4. XDP 辅助函数

### 4.1 数据访问

```c
// 获取数据包数据
void *xdp_data(struct xdp_md *ctx)
{
    return (void *)(long)ctx->data;
}

void *xdp_data_end(struct xdp_md *ctx)
{
    return (void *)(long)ctx->data_end;
}

// 获取协议头
struct ethhdr *bpf_hdr_pointer(struct xdp_md *ctx)
{
    return (struct ethhdr *)xdp_data(ctx);
}
```

### 4.2 动作

```c
// XDP 返回码
#define XDP_PASS     0   // 传递到网络栈
#define XDP_DROP     1   // 丢弃
#define XDP_TX       2   // 发送回网卡
#define XDP_REDIRECT 3   // 重定向
```

### 4.3 重定向

```c
// 重定向到其他设备
int bpf_redirect(int ifindex, u64 flags)
{
    struct net_device *dev = dev_get_by_index(net, ifindex);
    return bpf_redirect_map(dev_map, ifindex, flags);
}

// 重定向到 AF_XDP socket
int bpf_redirect_map(void *map, int key, u64 flags)
{
    // 使用 map 存储目标信息
}
```

## 5. XDP 设备映射

### 5.1 struct bpf_map

```c
// kernel/bpf/syscall.c
struct bpf_map {
    enum bpf_map_type map_type;
    __u32 key_size;
    __u32 value_size;
    __u32 max_entries;

    struct bpf_map_ops *ops;
    void *map;
};
```

### 5.2 devmap

```c
// kernel/bpf/devmap.c
struct bpf_dtab {
    struct bpf_map map;
    struct net_device ** devs;
};

// 查找设备
struct net_device *dev_map_lookup(struct bpf_dtab *dtab, int key)
{
    return dtab->devs[key];
}
```

## 6. 使用示例

### 6.1 ip 命令

```bash
# 加载 XDP 程序
ip link set eth0 xdp obj xdp_drop.o sec xdp

# 查看 XDP 状态
ip link show eth0

# 卸载 XDP
ip link set eth0 xdp off
```

### 6.2 iproute2

```bash
# 编译 BPF 程序
clang -target bpf -O2 -c xdp.c

# 加载
ip link set eth0 xdp obj xdp.o

# 多程序附加
ip link set eth0 xdp obj xdp_percpu.o
```

## 7. 性能

### 7.1 基准测试

```
传统方式 (skb): ~60 cycles/packet
XDP:            ~10 cycles/packet
XDP + redirect: ~20 cycles/packet
```

### 7.2 使用场景

```
1. DDoS 防护 - 在早期丢弃恶意流量
2. 负载均衡 - XDP 作为负载均衡器
3. 包过滤 - 高速包处理
4. 统计收集 - 低开销流量监控
```
