---
type: index
source-type: "web"
title: "WoWoTech Linux Kernel Block Index"
url: "http://www.wowotech.net/comm/2353.html"
summary: "WoWoTech 内核块设备索引页: block layer 架构、bio 合并、request 调度、multi-queue、blk-mq."
tags: [linux-kernel, block, io, wowotech]
created: "2026-06-08"
---
# WoWoTech Linux Kernel Block Index

## 来源信息

- **Author**: WoWoTech (lihaijian)
- **URL**: http://www.wowotech.net/comm/2353.html
- **Language**: 中文
- **Topic**: Linux block layer

## 核心内容

- Block layer 整体架构 (bio, request, queue)
- Generic block layer 与 blk-mq (multi-queue)
- IO 调度器 (cfq, deadline, noop) 与 mq-deadline, bfq, kyber
- bio 合并策略 (front/back merge)
- plug/unplug 模型与 polling
- Block device driver 模板 (request-based vs bio-based)

## 相关页面
- [[entities/linux/kernel/block/linux-kernel-block-core]]
- [[entities/linux/kernel/sched/linux-kernel-sched-core]]
- [[entities/linux/ebpf/ebpf-overview]]
- [[entities/linux/process-management-model]]
