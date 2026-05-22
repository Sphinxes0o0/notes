---
type: entity
tags: [exercise-science, technology, running-power-meter, Stryd, training, FTP]
created: 2026-05-22
sources: [relay-neuron-technology]
---

# 跑步功率计 (Running Power Meter)

## 定义

跑步功率计是测量跑步过程中实际能量消耗的设备，通过足底压力/加速度传感器或运动算法估算实时功率输出，为跑者提供客观、可量化的训练强度指标。

## 关键要点

- **功率定义**: 功率(W) = 力(N) × 速度(m/s)，跑步功率由水平推进力、垂直提升力、腿部摆动消耗共同构成
- **代表产品**: Stryd（鞋垫式）、Garmin Running Power（手腕算法估算）、跑步机内置功率
- **技术演进**: 2015-2019起步 → 2020-2022发展 → 2023-2026 Garmin原生支持+实时功率普及
- **核心优势**: 客观量化强度、不受环境影响（坡度/风阻/温度）、实时反馈

## 功率区间体系

**功能性阈值功率 (FTP)**:
- 定义: 60分钟最大平均功率
- 测试方法: 30分钟计时赛 × 0.95

**功率区间划分**:
| 区间 | 名称 | FTP% | 训练目的 |
|-----|------|------|---------|
| Z1 | 恢复 | <55% | 主动恢复 |
| Z2 | 轻松 | 55-75% | 有氧基础 |
| Z3 | 马拉松 | 75-85% | 耐力 |
| Z4 | 阈值 | 85-95% | 乳酸阈值 |
| Z5 | 间歇 | 95-120% | 无氧能力 |
| Z6 | 重复 | 120-150% | 速度 |
| Z7 | 冲刺 | >150% | 爆发力 |

## Stryd技术规格

| 型号 | 重量 | 电池 | 防水 | 特点 |
|-----|------|-----|------|-----|
| Stryd Original | 9g | 可更换 | IP67 | 第一代 |
| Stryd 2019 | 7.6g | 可更换 | IP67 | 双轴加速度 |
| Stryd 2022 | 6.5g | 内置锂电 | IP68 | 第三代传感 |
| Stryd Race | 8g | 可更换 | IP67 | 竞赛专用 |

**计算模型**: `Power = f(加速度, 速度, 坡度, 体重)`

## 功率训练优势

- **配速 vs 功率**: 配速受环境影响大（坡度/风阻/温度）；功率反映实际努力程度
- **标准化**: 不同地形条件下相同功率=相同努力程度
- **训练精确性**: 相同功率不同地形表现不同，帮助识别有氧/无氧状态

## 环境影响因素

| 条件 | 配速影响 | 功率影响 |
|-----|---------|---------|
| 高温 | 显著下降 | 下降较少 |
| 高海拔 | 下降 | 下降 |
| 大风 | 下降 | 水平推进变化 |
| 低气压 | 下降 | 下降 |

## 科学证据

- **可靠性**: 日间变异系数 2.1-4.7%；单位间可靠性 ICC=0.97-0.99
- **有效性**: 与代谢功率相关性 r=0.82-0.89；与摄氧量相关性 r=0.78-0.86
- **比赛策略**: 均匀功率分配表现最佳；负分段策略功率略高；爆胎策略表现下降

## 相关概念

- [[entities/exercise-science/technology/wearable-devices]] — 可穿戴设备
- [[entities/exercise-science/technology/hrv-training]] — HRV训练监控
- [[entities/exercise-science/running/running-economy]] — 跑步经济性
- [[entities/exercise-science/physiology/lactate-threshold]] — 乳酸阈值
- [[entities/exercise-science/training/training-methods]] — 训练方法
- [[entities/exercise-science/biomechanics/gait-analysis]] — 步态分析

## 来源详情

- [[sources/relay-neuron-technology]] — 跑步功率计研究 (2020-2026)
