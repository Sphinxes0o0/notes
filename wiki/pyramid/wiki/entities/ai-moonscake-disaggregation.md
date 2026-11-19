---
type: entity
tags: [llm, inference, mooncake, kv-cache, disaggregated]
created: 2026-05-27
sources: [pdf-mooncake]
---

# Mooncake KVCache Disaggregation

## Definition

Mooncake is a production LLM inference architecture that decouples Prefill and Decode nodes, using a distributed KVCache pool to enable elastic scaling and "storage for computation" trade-offs. Proposed by Ke Yang (Approaching.AI / Mooncake core contributor) at the 2024 C++ Summit China.

## Key Concepts

### Storage-for-Computation Trade-off

- GPU HBM bandwidth (2TB/s) >> network bandwidth (100-400Gbps)
- Storing KVCache in pooled storage and fetching it over the network is cheaper than keeping it in GPU memory
- Enables Prefill and Decode to scale independently

### KVCache Pool Architecture

```
Multi-tier KVCache Pool
┌─────────────────────────────────┐
│  HBM (GPU)  │ LPDDR (Host) │ NVMe│
│  hot data   │ warm data    │ cold│
└─────────────────────────────────┘
         ↑ cross-node network
    Prefill ←→ KVCache Pool ←→ Decode
```

### Disaggregation Benefits

- **Independent scaling**: add Decode nodes without adding Prefill nodes
- **Better GPU utilization**: compute and memory resources not competing
- **Elasticity**: KVCache nodes scale separately based on context length distribution

## Related Pages

- [[entities/ai-rtp-llm-inference]] — RTP-LLM (compare: same MoE/speculative themes)
- [[entities/cpp/cpp-llm-inference]] — C++ inference framework patterns
- [[entities/ai-mlir-compilation]] — MLIR-based inference compilation

## Source Details

- [[sources/pdf-mooncake]]