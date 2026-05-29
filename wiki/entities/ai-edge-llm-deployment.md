---
type: entity
tags: [llm, edge, mobile, storage, aios, deployment]
created: 2026-05-27
sources: [pdf-llm-edge-storage]
---

# Edge LLM Deployment & Storage Challenges

## Definition

Edge LLM deployment refers to running large language models on resource-constrained devices (smartphones, IoT sensors, automotive systems) where storage bandwidth, memory capacity, and power budget are severely limited compared to datacenter GPUs. Storage systems become the primary bottleneck.

## Key Concepts

### Device Categories

| 设备 | 存储介质 | 带宽 | 典型LLM |
|------|----------|------|---------|
| 高端手机 | NVMe/UFS 4.0 | ~4GB/s | 7B quantized |
| 中端手机 | UFS 3.1 | ~2GB/s | 3B quantized |
| 汽车SoC | eMMC/UFS | ~1GB/s | 7B quantized |
| IoT传感器 | SPI Flash | ~100MB/s | 1B quantized |

### AIOS Architecture

AI-integrated OS layers for edge AI:
- **Model Layer**: quantization, pruning, distillation
- **Runtime Layer**: inference scheduling, KVCache management
- **Storage Layer**: hierarchical caching, prefetching
- **Hardware Layer**: NPU/DSP integration

### Storage Optimization Strategies

| 策略 | 说明 | 效果 |
|------|------|------|
| **模型分片加载** | 按层/头加载，减少峰值内存 | -50% peak memory |
| **层级KVCache** | HBM→LPDDR→UFS三层分级 | +3x context length |
| **计算存储融合** | Near-storage computing，减少搬移 | -30% bandwidth |
| **INT4量化+压缩** | KVCache量化压缩 | -75% KVCache size |

### Challenges Summary

- Storage bandwidth >> compute capability (storage is bottleneck)
- Model size vs. device storage capacity
- Power budget: storage IO power vs. compute power
- Thermal management under sustained load

## Related Pages

- [[entities/cpp/cpp-llm-inference]] — LLM推理引擎通用架构
- [[entities/cpp/cpp-memory-management]] — 内存管理（KVCache层级）
- [[entities/linux/kernel/index#memory-management]] — Linux内存管理子系统
- [[entities/ai-mlir-compilation]] — 编译优化减少模型体积

## Source Details

- [[sources/pdf-llm-edge-storage]] — 端侧大模型部署：存储系统面临的挑战和优化实践