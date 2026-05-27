---
type: source
source-type: pdf
title: "统一算力，释放智能：FlagScale在FlagOS生态中的演进"
author: "熬玉龙"
date: 2024
size: small
path: raw/PDFs/slides/熬玉龙_统一算力，释放智能：FlagScale在FlagOS生态中的演进.pdf
summary: "熬玉龙：FlagScale大模型训练推理框架，FlagCX统一通信库，FlagOS多AI芯片统一软件栈"
tags: [llm, training, inference, flag-scale, distributed, ai-slides]
---

# 统一算力，释放智能：FlagScale在FlagOS生态中的演进

## 核心内容

**Author:** 熬玉龙 | 2024

### FlagOS 统一软件栈

```
各种AI芯片  →  统一支持  ←  各种大模型
                      ↑
                深度学习框架
              (PyTorch, PaddlePaddle, etc)
```

### FlagOS 已支持模型

**语言模型**：DeepSeek、Qwen、Seed-oss、GPT-oss、Step、Grok、Llama等
**多模态模型**：智源EMU、面壁CPM、Qwen-VL系列、ERNIE4.5、Llava系列
**具身智能模型**：智源RoboBrain、Pai-0

### FlagScale 核心组件

1. **FlagScale大模型训推框架**：统一的训练+推理框架
2. **FlagCX统一通信库**：跨芯片通信抽象（ NCCL兼容接口）
3. **自动化迁移**：自动化跨芯片模型转换
4. **跨芯片协同**：多异构芯片联合推理

### FlagCX 设计

- 抽象通信原语：AllReduce/Broadcast/ReduceScatter
- 后端插件：支持NVIDIA/AMD/国产AI芯片
- 拓扑感知：NUMA/PCIe/NVLink跨节点

## 相关页面
- [[entities/cpp/cpp-llm-inference]] — C++ LLM推理优化
- [[entities/ai-mlir-compilation]] — AI编译器基础设施
- [[entities/cpp/cpp-high-performance]] — C++高性能计算
- [[cpp-index]] — Modern C++ 模块索引