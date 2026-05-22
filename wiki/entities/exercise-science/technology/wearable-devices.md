---
type: entity
tags: [exercise-science, technology, wearable-devices, running, monitoring]
created: 2026-05-22
sources: [relay-neuron-technology]
---

# 可穿戴设备 (Wearable Devices)

## 定义

可穿戴设备是集成了传感器技术的便携式电子设备，能够在运动过程中实时监测跑者的生理和运动数据，为训练优化和健康管理提供数据支持。

## 关键要点

- **主要类型**: GPS手表（Garmin/Apple Watch/Polar）、心率带（Polar H10/Wahoo TICKR）、运动手环、智能跑鞋、血氧监测设备
- **核心技术**: 双频GPS（2020+）、光学心率PPG、多频段卫星定位（2024+）
- **数据指标**: 配速、距离、心率区间、步频、触地时间、垂直振幅、HRV、跑步功率
- **技术演进**: 2020-2022双频GPS普及 → 2023-2024 AI算法优化+实时HRV → 2025-2026 无创血糖监测开始应用

## 核心数据指标

**基础跑步指标**:
| 指标 | 定义 | 优化目标 |
|------|------|---------|
| 步频 (Cadence) | 每分钟步数 | 170-180 spm |
| 步幅 (Stride Length) | 每步距离 | 效率最大化 |
| 触地时间 (Ground Contact) | 单脚触地时长 | <200ms |
| 垂直振幅 (Vertical Oscillation) | 身体上下起伏 | <6% 身高 |

**生理指标**: 静息心率、最大心率、心率区间分布、心率恢复(HRR)、VO2max估算

## GPS技术发展

| 阶段 | 精度 | 特点 |
|------|------|------|
| 单频GPS (早期) | ±5-10米 | 容易受树木/建筑物干扰 |
| 双频多星GPS (2020+) | ±2-3米 | 支持GPS/GLONASS/北斗/Galileo |
| 多频段GPS (2024+) | ±1-2米 | L1+L5双频段，隧道内保持轨迹 |

## 光学心率准确性

| 条件 | 准确率 |
|------|--------|
| 静止时 | 95-98% |
| 低强度运动 | 90-95% |
| 高强度运动 | 80-88% |
| 间歇训练 | 75-85% |

**建议**: 高强度训练仍建议使用心率带

## 科学研究证据

- **VO2max估算**: Garmin Firstbeat算法 r=0.87-0.92，与实验室测试高度相关
- **损伤预防**: 步态对称性分析、触地时间变化预警、垂直振幅异常提示

## 相关概念

- [[entities/exercise-science/technology/hrv-training]] — HRV监测与训练指导
- [[entities/exercise-science/technology/running-power-meter]] — 跑步功率计
- [[entities/exercise-science/physiology/vo2max]] — 最大摄氧量
- [[entities/exercise-science/running/running-economy]] — 跑步经济性
- [[entities/exercise-science/physiology/lactate-threshold]] — 乳酸阈值
- [[entities/exercise-science/training/training-methods]] — 训练方法

## 来源详情

- [[sources/relay-neuron-technology]] — 可穿戴设备与跑步数据 (2020-2026)
