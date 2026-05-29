---
type: entity
tags: [linux-kernel, networking, skbuff, memory-management, scatter-gather, clone]
created: 2026-05-22
sources: [notes-net-deep]
---

# SKB (sk_buff) Deep Dive — 套接字缓冲区深度分析

## 定义

sk_buff（Socket Buffer）是 Linux 内核网络子系统中最核心的数据包容器，承载从设备驱动到应用层之间所有协议层的数据传递。通过精心设计的 head/data/tail/end 四指针布局和分散/聚集 I/O（Scatter-Gather），SKB 在保证零拷贝的同时支持高效的协议头操作。

## 关键要点

### 核心结构：四指针布局

```
head                    data                            tail                end
  |                       |                               |                   |
  v                       v                               v                   v
  +-----------------------+-------------------------------+-------------------+
  |      headroom         |        data area              |    tailroom      |
  |   (预留空间, push)    |    (实际网络数据)              |   (预留空间, put) |
  +-----------------------+-------------------------------+-------------------+
                          |<- skb_headlen(skb) -->|
                          |<- len -------------->|<- data_len (分页数据) -->|
                          |<----------- truesize (含 skb 本体) ------------>|
                                                                         
  end 之后附着 struct skb_shared_info:
    ├─ nr_frags, frags[]     (页面片段, 分散/聚集)
    ├─ frag_list              (SKB 片段链表, 用于 GSO fraglist)
    ├─ dataref                (数据引用计数, 16位分割)
    └─ gso_size / gso_segs    (GSO 信息)
```

**关键指针操作**：
- `skb_put(skb, len)`：在 tail 后添加数据（写入载荷）
- `skb_push(skb, len)`：在 data 前添加数据（写入协议头）
- `skb_pull(skb, len)`：从 data 移除数据（解析协议头后移动 data 指针）
- `skb_reserve(skb, len)`：预留 headroom（data 和 tail 均增加，用于后续 push 协议头）

### 分散/聚集 I/O（Scatter-Gather）

SKB 支持三种数据存储方式，共同构成 skb->len：

| 区域 | 指针 | 描述 |
|------|------|------|
| 线性区 | `skb->data` ~ `skb->tail` | 主数据区，包含所有协议头 |
| 页面片段 | `skb_shared_info->frags[]` | `skb_frag_t` 数组，每项指向 page + offset + len |
| 片段链表 | `skb_shared_info->frag_list` | 完整的子 SKB 链表，用于 GSO fraglist |

`skb_headlen(skb)` = skb->len - skb->data_len（线性部分）。
`skb_is_nonlinear(skb)` = skb->data_len > 0。

### 内存分配路径

| 函数 | 用途 | 分配来源 |
|------|------|----------|
| `__alloc_skb()` | 通用分配 | kmem_cache (skbuff_cache/fclone_cache) + kmalloc |
| `__netdev_alloc_skb()` | 设备驱动接收 | page_frag_cache（中包）或 kmalloc（小/大包） |
| `napi_alloc_skb()` | NAPI 上下文 | per-CPU NAPI cache |

**分配标志**：
- `SKB_ALLOC_FCLONE`：从 fclone cache 分配（预分配 skb1+skb2 对，加速克隆）
- `SKB_ALLOC_RX`：接收路径（可触发 PFMEMALLOC）
- `SKB_ALLOC_NAPI`：仅使用 NAPI per-CPU cache（不 fallback）

### 克隆 vs 复制

| 操作 | 函数 | 数据 | 元数据 | 适用场景 |
|------|------|------|--------|----------|
| 快速克隆 | `skb_clone()` | **共享**（dataref++） | 新 SKB | 多消费者（tcpdump + 协议栈） |
| 完全复制 | `skb_copy()` | **独立复制**（包括分页数据） | 新 SKB | 需要修改数据 |
| 部分复制 | `pskb_copy()` | 线性区独立，分页数据共享 | 新 SKB | 需修改协议头但保留载荷 |

**fclone 优化**：`struct sk_buff_fclones` 包含 skb1 + skb2 对。首次 `skb_clone()` 时直接使用预分配的 skb2，无需 kmem_cache_alloc，减少锁竞争。

### dataref 引用计数

`skb_shared_info->dataref` 是 32 位原子变量，分为两半：
- **低 16 位**：总引用数（cloned SKB 的数量）
- **高 16 位**：仅 payload（无 header）的引用数

`skb_data_unref()` 在释放时根据 `skb->cloned` 和 `skb->nohdr` 标志选择递减 bias（1 或 (1<<16)+1），确保最后一个消费者释放数据。

### Linearize 过程

`skb_linearize()` → `__pskb_pull_tail()` 将非线性 SKB 的分页数据拷贝到线性区：
1. 检查 tailroom 是否充足，不足则 `pskb_expand_head()` 重新分配
2. `skb_copy_bits()` 将分页数据拷贝入线性区尾部
3. 释放已合并的 frags
4. 更新 `skb->tail`、`skb->data_len`

### pskb_expand_head() 重分配

当需要更多 headroom/tailroom 时（如添加隧道封装头），分配新缓冲区：
1. 分配 `osize + nhead + ntail` 新缓冲区
2. `memcpy` 复制原有数据和 skb_shared_info
3. 若为克隆 SKB，需先 orphan frags（独立持有分页数据）
4. 更新 head/data/tail/end 指针偏移量
5. 重置 cloned=0, dataref=1

### 释放路径

```
kfree_skb() / consume_skb()
  → __kfree_skb()
    → skb_release_all()
      → skb_release_head_state()  // dst_drop, destructor (tcp_wfree/sock_wfree), nf_reset_ct
      → skb_release_data()
        → skb_data_unref()        // 检查 dataref
        → __skb_frag_unref() × N  // 释放页面片段引用
        → kfree_skb_list(frag_list)
        → skb_free_head()        // kfree 或 page_frag 回收
    → kfree_skbmem()
      → SKB_FCLONE_ORIG/CLONE 处理：refcount_dec_and_test(fclone_ref)
      → kmem_cache_free(skbuff_cache 或 skbuff_fclone_cache)
```

### Destructor 机制

SKB 在释放时通过 destructor 回调通知所属 socket 更新内存记账：
- `sock_wfree`：通用 socket 写释放，更新 sk_wmem_alloc
- `tcp_wfree`：TCP 专用，更新 sk_wmem_alloc 并可能触发发送窗口更新
- `xsk_destruct_skb`：AF_XDP socket 释放

## 源码关键位置

| 文件 | 行号 | 内容 |
|------|------|------|
| `include/linux/skbuff.h` | 885 | `struct sk_buff` |
| `include/linux/skbuff.h` | 593 | `struct skb_shared_info` |
| `include/linux/skbuff.h` | 361 | `skb_frag_t` |
| `net/core/skbuff.c` | 672 | `__alloc_skb()` |
| `net/core/skbuff.c` | 759 | `__netdev_alloc_skb()` |
| `net/core/skbuff.c` | 2098 | `skb_clone()` |
| `net/core/skbuff.c` | 1608 | `__skb_clone()` |
| `net/core/skbuff.c` | 2178 | `skb_copy()` |
| `net/core/skbuff.c` | 1102 | `skb_release_data()` |
| `net/core/skbuff.c` | 2866 | `__pskb_pull_tail()` |
| `net/core/skbuff.c` | 2294 | `pskb_expand_head()` |

## 相关概念

- [[entities/linux/kernel/net]] — 网络子系统整体架构，SKB 在其中的位置
- [[entities/linux/network/linux-network-protocols]] — 协议层使用 SKB 进行数据传递
- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径中的 SKB 操作
- [[entities/linux/kernel/netfilter]] — Netfilter 通过 SKB 承载数据包

## 来源详情

- [[sources/notes-net-deep]] — net_skbuff.md + net_deep_dive_r1.md §2
