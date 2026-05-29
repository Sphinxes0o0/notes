---
type: source
source-type: bookmark
title: "Rust Embedded Drivers (RED) Book"
author: "ImplFerris"
date: 2024
url: https://red.implrust.com/
github: https://github.com/ImplFerris/red-book
license:
  code: MIT, Apache 2.0
  prose: CC-BY-SA v4.0
summary: "通过实战项目（DHT22、MAX7219 LED、RTC）学习嵌入式 Rust 驱动开发，涵盖 HAL、PAC、RTIC 等核心概念"
tags: [embedded-rust, drivers, esp32, hal, pac, rtic, no-std]
---

# Rust Embedded Drivers (RED) Book

## 核心内容

- **no_std 嵌入式开发**: 无标准库依赖的 Rust 裸机编程
- **HAL (Hardware Abstraction Layer)**: `embedded-hal` 统一硬件抽象（GPIO、I2C、SPI、UART、定时器）
- **PAC (Peripheral Access Crate)**: 寄存器级编程，自动生成自 svd2rust
- **RTIC (Real-Time Interrupt-driven Concurrency)**: 任务调度、资源管理、优先级中断
- **驱动开发实战**: DHT22 温湿度传感器、MAX7219 LED 驱动、DS1307/DS3231 RTC

## 章节结构

| # | 章节 | 内容 |
|---|------|------|
| 1 | Introduction | 开发环境、ESP32、工具链 |
| 2 | DHT22 | 单总线协议、时序解析、温湿度驱动 |
| 3 | MAX7219 | SPI 驱动、LED 矩阵、7 段显示 |
| 4 | Embedded Graphics | embedded-graphics 库、DrawTarget trait |
| 5 | RTC (DS1307/DS3231) | I2C 通信、RTC HAL traits、NVRAM |

## 关键技术点

- **单总线 (DHT22)**: 单 GPIO 时序驱动，低速传感器协议，bit-banging 实现
- **SPI (MAX7219)**: 全双工串行协议，8位寄存器寻址，多路复用 LED 控制
- **I2C (RTC)**: 时钟/日历芯片，BCD 编码，NVRAM，square wave 输出
- **embedded-graphics**: 跨设备图形库，支持多种显示驱动，统一 DrawTarget trait
- **RTC HAL**: 抽象 RTC trait，支持 DS1307/DS3231 多种芯片

## 相关页面

- [[embedded-rust-hal]] — embedded-hal trait 系统，GPIO/I2C/SPI 抽象
- [[embedded-rust-pac]] — PAC 寄存器编程，svd2rust 自动生成
- [[embedded-rust-rtic]] — RTIC 实时并发，任务优先级，资源共享
- [[embedded-rust-drivers]] — 驱动开发模式，DHT22/MAX7219/RTC 实战
- [[rust-language]] — Rust 语言基础（所有权、生命周期、trait）
- [[armv8-architecture]] — ESP32 基于 ARM Cortex-M（参考）
