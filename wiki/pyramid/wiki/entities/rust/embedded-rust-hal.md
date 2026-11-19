---
type: entity
tags: [embedded-rust, hal, embedded-hal, gpio, i2c, spi, uart, esp32]
created: 2026-05-29
sources: [bookmark-rust-embedded-drivers]
---

# Embedded Rust HAL

## 定义

HAL (Hardware Abstraction Layer) 在嵌入式 Rust 中指 `embedded-hal` crate 提供的一组 trait 接口，抽象 GPIO、I2C、SPI、UART、定时器、PWM 等外设，使驱动代码与具体芯片解耦。

## 关键要点

- **embedded-hal trait**: 异步/阻塞双模式，支持 `embedded-hal 1.x`（async trait）和 `embedded-hal 0.x`（blocking trait）
  - `InputPin` / `OutputPin` / `toggle_pin`（GPIO）
  - `I2c`（SMBus 协议）、`Spi`（全双工）
  - `Serial`（UART）、`Timer`、`Pwm`
- **实际芯片 HAL**: 每个芯片（STM32、ESP32、NRF52）实现 embedded-hal trait
  - ESP32: `esp-hal` crate
  - STM32: `stm32f4xx-hal` / `stm32h7xx-hal`
- **解耦设计**: 驱动编写者依赖 trait 而非具体芯片，实现者提供具体芯片的 impl
- **零成本抽象**: trait 对零静态调度，编译器内联后无额外开销
- **与 std 的区别**: 无堆分配、无文件系统、无网络栈，只保留嵌入式必需 trait

## 常见 trait

| Trait | 方法 | 用途 |
|-------|------|------|
| `InputPin` | `is_high()`, `is_low()` | 数字输入 |
| `OutputPin` | `set_high()`, `set_low()`, `toggle()` | 数字输出 |
| `I2c` | `write()`, `read()`, `write_read()` | I2C 通信 |
| `Spi` | `transfer()`, `send()` | SPI 通信 |
| `Serial` | `read()`, `write()` | UART 通信 |

## 相关概念

- [[embedded-rust-pac]] — PAC 是寄存器级直接访问，HAL 是 trait 抽象层，HAL 底层依赖 PAC
- [[embedded-rust-rtic]] — RTIC 调度器依赖 HAL 定时器和 GPIO 实现中断驱动任务
- [[embedded-rust-drivers]] — 驱动（DHT22、MAX7219）使用 HAL I2C/SPI 通信
- [[rust-language]] — Rust trait 系统是 HAL 的语言基础
