# LLM Wiki — 待办与进度

> 本文件追踪 ingest 进度。Hermes 按优先级自动分配 Claude Code 执行，无需反复确认。

---

## ✅ 已完成

| 批次 | 内容 | 新增 |
|------|------|------|
| Phase 1-5 | notes 内核/网络/C++ | 127→185 pages |
| eBPF | 10 PDFs | 185→214 pages |
| C++ | 7 PDFs | 214→220 pages |
| 拆分 | relay-neuron → atlas | 220→~95 pages |
| D | safeOS lwIP Core (27 docs) | +27 entities |
| E | safeOS lwIP 扩展/sel4 (19 docs) | +19 entities |
| F | safeOS LWFW 防火墙 (25 docs) | +25 entities |
| Synth | safeos-lwip-deep-analysis.md | 1513 行 |
| Synth | safeos-source-analysis.md | 1324 行 |
| **合计** | **281 wiki pages** | |

## 📋 待办（按优先级）

### P1 — safeOS 剩余文档
- [ ] 架构类: architecture_notes, plan, NSv_analysis, network_implementation (6 docs)
- [ ] memory/safeos_vdf_nids.md (1 doc)

### P2 — safeOS vdf & soa
- [ ] vdf: VDF seL4 虚拟化框架（需先 rsync 远程文档）
- [ ] soa: SOA 服务化架构（需先 rsync 远程文档）

### P3 — Modern-Cpp-Skills（待同步）
- [ ] rsync 远程 ~/github/Modern-Cpp-Skills/ → raw/
- [ ] C++17 现代技能 (~15 docs)
- [ ] C++ 大师级技能 (~15 docs)

### P4 — workflow 异步引擎（待同步）
- [ ] rsync 远程 ~/github/workflow/docs/ → raw/
- [ ] workflow 核心 (~20 docs)
- [ ] workflow 教程 (~15 docs)

### P5 — 高价值 PDFs
- [ ] 密码学/安全 (商用密码、mbedTLS、PTPsec、Isovalent)
- [ ] MLIR/编译器
- [ ] 体系结构
- [ ] C++ 剩余 slides
- [ ] 高性能服务器

### P6 — 低优先级 PDFs
- [ ] 其余书籍/论文/slides (~70 PDFs)

---

## 🔍 Lint 任务

| ID | 任务 | 触发条件 |
|----|------|----------|
| L-1 | lint_wiki.py | 每次 batch ingest 后 |
| L-2 | 内容准确度审计 | 每 3-5 batch 后 |

---

*Last updated: 2026-05-25*
