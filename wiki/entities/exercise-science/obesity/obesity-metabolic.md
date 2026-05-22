---
type: entity
tags: [exercise-science, obesity, metabolic, T2DM, insulin-resistance, IL7, Treg, RBP4, VAI]
created: 2026-05-22
sources: [relay-neuron-obesity-literature]
---

# Obesity & Metabolic/Endocrine System — 肥胖与代谢内分泌系统

## Definition

肥胖是2型糖尿病（T2DM）最强的可改变风险因素。内脏脂肪通过脂肪因子失衡（RBP4↑、脂联素↓）、慢性炎症（IL-7/Treg轴失调）和脂毒性，驱动胰岛素抵抗→β细胞衰竭→T2DM的完整链条。**VAI（内脏脂肪指数）每增加1个单位，T2DM风险增加43%（OR=1.43）。**

## Pharmacological Treatment Landscape

Nature Medicine (2025, IF~58.7) — 系统综述+网络荟萃分析，纳入56项RCT：

| 药物 | 12个月减重效果 | 心血管获益 |
|------|--------------|----------|
| **Tirzepatide（GIP/GLP-1双靶点）** | ~15-20% | 心衰住院↓ |
| **Semaglutide（GLP-1）** | ~10-15% | MACE显著降低 |
| Liraglutide（GLP-1）| ~5-10% | 心血管保护信号 |
| Orlistat（脂肪酶抑制剂）| ~5-10% | 证据有限 |

## VAI and T2DM Risk

Scientific Reports (2024, NHANES 2007-2018, n=11,214)：

> **VAI每增加1个单位，T2DM风险增加43%（OR=1.43, 95%CI: 1.35-1.50）**

关键洞察：**即使BMI正常，高VAI仍增加T2DM风险**——这解释了"代谢性肥胖"（TOFI: thin outside, fat inside）人群的特殊风险。

| 比较维度 | VAI | BMI |
|---------|-----|-----|
| 反映脂肪分布 | ✅（含WC）| ❌ |
| 反映血脂异常 | ✅（含TG、HDL）| ❌ |
| 代谢健康综合评估 | ✅ | ❌ |
| 识别"代谢性肥胖" | ✅ | ❌ |

## Novel Adipokine: RBP4

Endocrine (2024, IF~3.2) — 新型脂肪因子视黄醇结合蛋白4：

| RBP4的作用 | 结果 |
|-----------|------|
| 诱导骨骼肌胰岛素抵抗 | GLUT4转位↓→葡萄糖摄取↓ |
| 促进肝脏胰岛素抵抗 | 糖异生↑ |
| 损害β细胞功能 | β细胞凋亡↑ + 胰岛素分泌↓ |
| 诱导β细胞炎症 | 炎症小体激活 |

RBP4将**维生素A代谢与葡萄糖代谢**联系在一起，是未来治疗新靶点。减重和运动可降低RBP4水平。

## Immunological Mechanism: IL-7/Treg Axis

日本京都大学 (2025, Journal of Immunology, IF~4.4)：

```
IL-7 → 维持内脏脂肪中调节性T细胞（Treg）存活
        ↓
Treg数量稳定 → 脂肪组织局部抗炎（抑制M1巨噬细胞）
        ↓
胰岛素敏感性改善 → 血糖降低
```

**突破性发现**：**单次IL-7注射**即可使小鼠高血糖状态得到**长时间抑制**（数周）。这为T2DM的免疫疗法提供了全新思路——IL-7或将成为新型治疗靶点。

## Disease Continuum

```
肥胖
  │
  ├─→ 脂肪细胞功能障碍
  │       │
  │       ├─→ RBP4分泌↑ → 胰岛素抵抗（肝脏+骨骼肌）
  │       └─→ Treg减少（IL-7↓）→ 炎症↑
  │               │
  │               ↓
  └────────────────→ β细胞功能损害 → T2DM
```

## Related Entities

- [[entities/exercise-science/obesity/obesity-overview]] — VAT内分泌功能、脂肪因子网络、VAI综合指标
- [[entities/exercise-science/obesity/obesity-kidney]] — VAI同样预测CKD风险（+12%/每翻倍）
- [[entities/exercise-science/obesity/obesity-liver]] — 胰岛素抵抗是MASLD和T2DM的共享机制
- [[entities/exercise-science/supplements/curcumin/curcumin-diabetes]] — 姜黄素：GSK-3β↓, IAPP↓, β-cell protection（RCT n=272）
- [[entities/exercise-science/supplements/coq10/coq10-overview]] — CoQ10：线粒体功能改善胰岛素敏感性

## Source Details

- [[sources/relay-neuron-obesity-literature]] — 4篇代谢文献：Nature Medicine (2025), Journal of Immunology (2025), Endocrine (2024), Scientific Reports (2024)
