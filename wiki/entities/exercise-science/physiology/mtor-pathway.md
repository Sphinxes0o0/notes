---
type: entity
tags: [exercise-science, protein-synthesis, cell-signaling]
created: 2026-05-20
sources: [relay-neuron-physiology]
---

# mTOR Pathway (mTOR 信号通路)

## Definition

哺乳动物雷帕霉素靶蛋白 (mTOR) 是 PI3K 相关激酶家族成员，是蛋白质合成的主要调控因子，作为细胞生长的中央枢纽整合营养、能量和生长因子信号。

## Structure

| 复合物 | 组成 | 功能 |
|-------|------|-----|
| mTORC1 | mTOR + Raptor + mLST8 | 蛋白质合成调控（核心） |
| mTORC2 | mTOR + Rictor + mLST8 | 细胞存活、代谢 |

## Activation Cascade

```
氨基酸 (亮氨酸) → mTORC1 → S6K1 → 蛋白质合成
                        ↓
                  4E-BP1 磷酸化
                        ↓
                  eIF4E 释放 → 翻译启动
```

## Key Findings

- **亮氨酸核心作用**: ~2-3g/餐 达到最大 [[entities/exercise-science/physiology/mps-muscle-protein-synthesis]] 刺激
- **运动后时间进程**:
  - 运动后 1-4 小时: mTOR、S6K1、4E-BP1 磷酸化增加
  - 运动后 24-48 小时: MPS 持续升高
  - 运动后 72 小时: 恢复至基线
- **阻力训练 vs 有氧训练**:
  - 阻力训练: 显著激活 mTORC1 (Ser2448, S6K1 Thr389)
  - 有氧训练: 激活 AMPK，抑制 mTORC1
  - 这一差异是 [[entities/exercise-science/physiology/concurrent-training]] 协调效应的核心机制

## Anabolic Resistance

老年人或特定人群对合成代谢刺激响应减弱：
- mTOR 通路信号下调
- [[entities/exercise-science/physiology/satellite-cells]] 活性降低
- 肌肉蛋白分解 (MPB) 增加
- 需要更高蛋白质剂量或亮氨酸富集

## Related

- [[entities/exercise-science/physiology/mps-muscle-protein-synthesis]]
- [[entities/exercise-science/physiology/muscle-hypertrophy]]
- [[entities/exercise-science/physiology/concurrent-training]]
