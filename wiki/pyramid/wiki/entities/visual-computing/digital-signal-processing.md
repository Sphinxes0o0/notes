---
type: entity
tags: [dsp, signal-processing, mathematics, audio, image, fft]
created:2026-06-08
sources: [bookmark-visual-computing-foundations]
---

# Digital Signal Processing (DSP)

## 定义

数字信号处理（DSP）是对离散时间信号（采样序列）进行分析、变换、滤波、压缩的理论与技术体系。DSP 是音频/图像/视频处理、通信系统（调制解调）、雷达/声呐、生物医学信号、控制系统等领域的基础。核心数学工具包括离散傅里叶变换（DFT）、Z变换、卷积、滤波器设计。

##关键要点

- **采样定理（Nyquist-Shannon）**：采样率 ≥2× 信号最高频率，避免混叠（aliasing）
- **DFT/FFT**：O(N log N)快速傅里叶变换，是频谱分析的核心
- **Z变换**：离散信号的拉普拉斯变换，分析系统极零点
- **滤波器**：FIR（线性相位，稳定）/ IIR（反馈结构，高效）
- **窗函数**：Hamming、Hann、Blackman抑制频谱泄漏

##核心概念

- **采样与量化**：连续信号 →离散信号（时间/幅度双量化）
- **卷积定理**：时域卷积 ↔频域乘积
- **快速卷积**：重叠保留/重叠相加法
- **多采样率**：上采样（插值）/下采样（抽取）+抗混叠滤波
- **自适应滤波**：LMS、NLMS、RLS 算法
- **实时DSP**：TI C6000 系列、ARM Cortex-M DSP扩展

## 相关页面

- [[entities/visual-computing]] — 可视计算总览
- [[entities/parallel-computing]] — DSP 中常用并行架构
- [[sources/bookmark-visual-computing-foundations]] — 可视计算基础资源
