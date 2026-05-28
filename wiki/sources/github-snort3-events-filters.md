---
type: source
source-type: github
title: "Snort3 — events/, host_tracker/, filters/"
author: "Snort Team (Cisco)"
date: 2026-05-27
size: medium
path: ~/workspace/github/snort3/src/events/ ~/workspace/github/snort3/src/host_tracker/ ~/workspace/github/snort3/src/filters/
summary: "Snort3 事件队列/主机追踪/过滤器框架源码分析：eventq memcap、host profiler (TCP/UDP/ICMP stats)、三层过滤架构 (detection/rate/event filter)"
---

# Snort3 — events/ host_tracker/ filters/

**Repo**: `snort3` (Cisco) | **Commit**: `72675d1ab` (master, 3.10.0.0 tag) | **Files**: 26 个源文件

---

## 源码结构

```
src/events/              (8 files)
src/host_tracker/        (14 files)
src/filters/             (14 files)
```

---

## 核心发现

### Event Queue — Memcap 机制

`SF_EVENTQ` 是预分配双向链表队列，`reserve_event` 槽实现优先级淘汰（不破坏节点即可比较）：

- `max_nodes` = memcap（最大节点数）
- `log_nodes` = 触发日志的阈值
- `fails` = 内存耗尽导致的丢弃计数
- 支持两种排序：`SNORT_EVENTQ_PRIORITY`（优先级序）vs `SNORT_EVENTQ_CONTENT_LEN`（内容长度序）

### Host Tracker — 分段缓存 + 自定义分配器

```
LruCacheSharedMemcap (atomic memcap tracking)
  └── HostCacheSegmented (XOR-hash 分段，减少锁竞争)
        └── HostCacheIp (per-segment LRU cache)
              └── CacheAlloc chain: CacheAlloc → HostCacheAllocIp → CacheInterface::update()
```

被驱逐的 `HostTracker` 不会直接析构，而是先调用 `remove_flows()` 清理关联流（`HTPurgatory` pattern）。

### Filter 三层架构

| 层级 | 文件 | 作用 |
|------|------|------|
| Detection Filter | `detection_filter.{h,cc}` | 规则匹配最后一步，决定是否生成事件 |
| Rate Filter | `sfrf.{h,cc}`, `rate_filter.{h,cc}` | 超阈值后替换动作 (alert→drop) |
| Event Filter | `sfthreshold.{h,cc}`, `sfthd.{h,cc}` | 控制事件是否记录日志 |

### Threshold 类型 (THD_TYPE)

- `LIMIT` — 记录前 N 个
- `THRESHOLD` — 每 N 个记录一次
- `BOTH` — N 个后记录一次，然后抑制
- `SUPPRESS` — 完全抑制
- `DETECT` — 仅跟踪，不记录

---

## 关键文件索引

| 文件 | 职责 |
|------|------|
| `events/sfeventq.{h,cc}` | 通用事件队列（memcap 预分配） |
| `events/event.{h,cc}` | Event 类（时间戳/gid/sid/priority/reference） |
| `events/event_queue.{h,cc}` | EventQueueConfig 配置结构 |
| `host_tracker/host_tracker.{h,cc}` | HostTracker 核心（MAC/proto/service/client/fingerprint） |
| `host_tracker/host_cache.{h,cc}` | LruCacheSharedMemcap 实现 |
| `host_tracker/host_cache_segmented.h` | 分段缓存（XOR hash 分发到 2^N 段） |
| `host_tracker/cache_allocator.{h,cc}` | STL 容器自定义分配器（memcap 回调链） |
| `filters/sfthd.{h,cc}` | Threshold 核心（THD_NODE / THD_IP_NODE） |
| `filters/sfrf.{h,cc}` | Rate filter 核心（状态机 FS_NEW→FS_OFF→FS_ON） |
| `filters/sfthreshold.{h,cc}` | Event filter 接口 |
| `filters/detection_filter.{h,cc}` | Detection filter（规则匹配最终关卡） |

---

## 相关页面

- [[entities/linux/snort3/snort3-events-filters]] — 概念详解
- [[entities/linux/snort3/snort3-framework]] — 框架总览
- [[entities/linux/snort3/snort3-flow]] — Flow/会话追踪
- [[entities/linux/snort3/snort3-actions]] — 动作系统
- [[entities/linux/snort3/snort3-ips-options]] — IPS 选项
