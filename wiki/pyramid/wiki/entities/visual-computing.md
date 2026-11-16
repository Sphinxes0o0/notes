---
type: entity
tags: [visual-computing, rendering, graphics, display, human-vision]
created: 2026-05-29
sources: [bookmark-visual-computing-foundations]
---

# Visual Computing

## 定义

视觉计算是跨越光学、模拟、数字和语义域的信号转换 — 研究人眼如何捕获光线、数字图像如何生成和显示。

## 关键要点

### 四大领域

1. **Human Vision**: 视觉感知、色彩空间、对比敏感度
2. **Rendering**: 光线追踪、光栅化、物理渲染 (PBR)
3. **Imaging**: 成像原理、传感器、计算摄影
4. **Display**: LCD、OLED、HDR 显示，颜色管理

### Rendering 管线

```
Scene → Geometry → Rasterization → Fragment → Display
         ↑                              ↓
      Transform              Lighting / Shading
```

### GPU 内存层级

纹理缓存是 GPU 特有的缓存层级，直接影响渲染性能 — 与 [[memory-hierarchy]] 中的 CPU 缓存原理相似。

### 与其他域的关系

- [[computer-architecture]] — GPU 架构 (CUDA cores, tensor cores)
- [[cache-memory-design]] — 纹理缓存设计
- 信号处理视角与 [[digital-signal-processing]] 相通

## 相关概念

- [[computer-architecture]] — CPU/GPU 架构
- [[memory-hierarchy]] — 缓存层级
- [[cache-memory-design]] — 缓存设计模式

## 来源详情

- [[bookmark-visual-computing-foundations]] — Foundations of Visual Computing 在线教材
