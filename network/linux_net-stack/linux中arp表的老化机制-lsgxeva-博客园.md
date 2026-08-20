---
title: "Linux 中 arp 表的老化机制"
description: "arp 表老化 = **定时器 + 事件驱动** 双轨. 调优本质是调整 `gc_stale_time` 和 GC 阈值适配网络规模."
---
# Linux 中 arp 表的老化机制

> 来源: [cnblogs.com/lsgxeva](https://www.cnblogs.com/lsgxeva/p/13749751.html)
> 原文: 4.4KB, 落本地 (源: juejin.im/post/6844904166545080334)

## 核心问题

- 设备维护的 arp 表 与 内核 arp 表 需同步
- 设备 arp 模块需要"老化时间"功能, 这依靠 **内核 arp 表老化**
- 网络设备 → 上层 arp 模块 通过钩子通知变化

## 内核 arp 表维护机制

### 老化触发

1. **时间到期**: arp 条目带 timeout (默认 60s, 可调 `net.ipv4.neigh.default.gc_stale_time`)
2. **主动探测**: 内核定期发 ARP request 验证可达性
3. **新包更新**: 收到新 ARP reply 时刷新时间戳

### 数据结构

```c
struct neighbour {
    struct hh_cache  *hh;             // L2 头缓存
    struct net_device *dev;           // 关联网卡
    unsigned char     ha[ETH_ALEN];   // 硬件地址 (MAC)
    __u32             hash;           // 哈希桶
    atomic_t          refcnt;
    // ...
};
```

### 关键路径

```
arp_rcv() (收到 ARP 包)
  → arp_process()
    → NEIGH_EVENT_REACHABLE  /  NEIGH_EVENT_STALE
      → neigh_release() / neigh_refresh()

arp_timer() (定时器)
  → neigh_periodic_work() (gc_stale_time 到期)
    → neigh_invalidate() (标记 stale)
      → 下次访问 → 重新 resolve
```

## 调优点

| 场景 | 参数 | 说明 |
|---|---|---|
| 高频 arp 表更新环境 | `net.ipv4.neigh.default.base_reachable_time_ms` | 缩短到 30s |
| 大量主机 (广播域大) | `gc_thresh1/2/3` | 调大 GC 阈值 |
| 频繁 arp miss | `unres_qlen_bytes` | 调大队列 |

## 关键 takeaway

arp 表老化 = **定时器 + 事件驱动** 双轨. 调优本质是调整 `gc_stale_time` 和 GC 阈值适配网络规模.

---
*原文 4.4KB 较精简, 主参考 [juejin 转载](https://juejin.im/post/6844904166545080334) 含完整代码段 (neighbour 结构, neigh_ops 回调, gc 算法详解).*
