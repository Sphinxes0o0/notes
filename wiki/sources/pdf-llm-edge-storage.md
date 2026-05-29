---
type: source
source-type: pdf
title: 端侧大模型部署：存储系统面临的挑战和优化实践
author: 王骁
date: 2024
size: small
path: raw/PDFs/slides/王骁_端侧大模型部署：存储系统面临的挑战和优化实践.pdf
summary: 王骁：端侧LLM部署的存储系统挑战，AIOS架构，端侧存储优化实践
tags: [llm, edge-inference, storage, aios, mobile, ai-slides]
created: 2024
---
# 端侧大模型部署：存储系统面临的挑战和优化实践

## 核心内容

**Author:** 王骁 | 2024

### 目录

01. 端侧大模型发展
02. AIOS架构
03. 存储系统挑战和优化实践
04. 未来展望

### 端侧大模型趋势

- **手机/PC**：Apple CoreML/Google ML Kit
- **汽车**：车载AI助手，本地推理
- **IoT**：传感器数据本地处理
- **隐私敏感场景**：数据不出端

### 端侧存储系统挑战

| 挑战 | 说明 |
|------|------|
| 模型体积 | 7B模型 ~14GB权重，量化后 ~4GB |
| KVCache | 长上下文端侧存储带宽受限 |
| 存储介质差异 | UFS/eMMC vs NVMe，性能差10x |
| 功耗 | 存储IO功耗 vs 计算功耗平衡 |
| 热管理 | 端侧设备散热能力有限 |

### AIOS 存储优化策略

- **模型分片加载**：按层/按注意力头加载，减少峰值内存
- **层级KVCache**：HBM → LPDDR → UFS三层分级存储
- **计算存储融合**：Near-storage computing，减少数据搬移
- **模型量化+压缩**：INT4/INT8量化 + KVCache压缩

## 相关页面
- [[entities/cpp/cpp-llm-inference]] — C++ LLM推理优化
- [[entities/cpp/cpp-memory-management]] — 内存管理
- [[cpp-index]] — Modern C++ 模块索引
- [[entities/linux/kernel/index#memory-management]] — Linux内存管理（存储相关）