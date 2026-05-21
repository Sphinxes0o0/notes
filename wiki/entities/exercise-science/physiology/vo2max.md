---
type: entity
tags: [exercise-science, endurance, cardio-vascular]
created: 2026-05-20
sources: [github-relay-neuron-exercise-physiology]
---

# VO2max (最大摄氧量)

## Definition

人体在剧烈运动时利用氧气的最大能力，单位 ml/kg/min，是衡量心肺功能的黄金标准指标。

## Key Formula

```
VO2max = 心输出量 (CO) × 动静脉氧差
       = (心率 × 每搏输出量) × (动脉氧含量 - 静脉氧含量)
```

## Benchmarks

| 人群 | 平均值 | 范围 |
|-----|-------|------|
| 久坐男性 | 35-40 | 25-50 |
| 活跃男性 | 45-50 | 35-60 |
| 精英男性跑者 | 70-85 | 60-95 |
| 久坐女性 | 25-30 | 20-40 |
| 精英女性跑者 | 55-70 | 50-80 |

## Running Performance Prediction

```
马拉松时间 (分钟) ≈ 4800 / (VO2max - 30)
```

- VO2max 与 5K 成绩: r = 0.75-0.85
- VO2max 与 10K 成绩: r = 0.78-0.88
- VO2max 与马拉松: r = 0.65-0.75

## Training to Improve VO2max

**最有效方法: HIIT (高强度间歇训练)**

| 方案 | 强度 | 时间 | 重复 | 恢复 |
|-----|------|-----|------|-----|
| 4×4 训练 | 95-100% 最大心率 | 4 分钟 | 4 次 | 3 分钟 |
| 10-20-30 | 全力/低强度交替 | 30+20+30 秒 | 3-4 次 | 2 分钟 |
| 坡度重复 | VO2max 强度 | 3-5 分钟 | 4-6 次 | 恢复跑 |

**周跑量影响**:
- < 30km: 维持水平
- 30-60km: 缓慢提高
- 60-100km: 显著提高
- > 100km: 边际效益递减

## Age-Related Decline

- 30 岁后每年下降 0.5-1%
- 长期跑步者下降速度减慢约 50%
- 持续训练是维持关键

## Detraining

| 停训时间 | VO2max 变化 |
|---------|-----------|
| 1 周 | -4-6% |
| 2 周 | -8-10% |
| 4 周 | -15-20% |
| 8 周+ | -20-25% |

## Related

- [[entities/exercise-science/physiology/lactate-threshold]]
- [[entities/exercise-science/physiology/concurrent-training]]
- [[entities/exercise-science/physiology/fatigue-recovery]]
## Related Concepts

- [[entities/exercise-science/running/ultra-endurance]] — 超耐力运动对VO2max的长期适应
- [[entities/exercise-science/health/exercise-disease]] — 心肺功能与疾病预防高度相关
