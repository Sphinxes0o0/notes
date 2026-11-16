---
type: entity
tags: [embedded-rust, drivers, dht22, max7219, rtc, i2c, spi, embedded-graphics]
created: 2026-05-29
sources: [bookmark-rust-embedded-drivers]
---

# Embedded Rust Drivers

## 定义

嵌入式 Rust 驱动开发是通过 HAL trait 接口和 PAC 寄存器操作，为真实硬件设备（DHT22 传感器、MAX7219 LED 驱动、DS1307/DS3231 RTC）编写无 std 依赖的驱动程序。

## 关键要点

- **DHT22 温湿度传感器**:
  - 单总线协议（single-wire），半双工时序
  - 主机拉低 ≥1ms → DHT22 响应 80μs 低 → 80μs 高 → 数据位
  - 40bit 数据（16bit 湿度 + 16bit 温度 + 8bit 校验和）
  - 使用 esp-idf-hal GPIO bit-banging 实现时序
- **MAX7219 LED 驱动**:
  - SPI 协议，8 位寄存器地址 + 数据
  - 寄存器：No-op / Digit0-7 / Decode-Mode / Intensity / Scan-Limit / Shutdown
  - 支持 8×8 LED 点阵和 7 段数码管
  - `embedded-graphics` crate 提供统一绘图接口（DrawTarget trait）
- **RTC 芯片 DS1307 / DS3231**:
  - I2C 协议，从地址 0x68（DS1307）/ 0x68（DS3231）
  - BCD 编码时钟/日历寄存器
  - 支持 NVRAM 读写、方波输出（SQW）、涓流充电（DS1307）
  - DS3231 精度更高（±2ppm），集成温度传感器
- **RTC HAL trait**: `embedded-rtc` crate 定义 `Rtc` trait，统一不同芯片实现
  - `Datetime` / `Control` / `SquareWave` / `Nvram` traits

## 驱动开发模式

1. 读取芯片 datasheet 和 register map
2. 定义寄存器地址常量和位域
3. 实现初始化函数（配置外设）
4. 实现读写操作（I2C/SPI/GPIO 时序）
5. 封装错误类型（`enum` 类型安全）
6. 编写单元测试（mock HAL 行为）

## 相关概念

- [[embedded-rust-hal]] — 驱动使用 HAL I2C/SPI trait 与芯片通信
- [[embedded-rust-pac]] — HAL 底层通过 PAC 操作寄存器
- [[embedded-rust-rtic]] — 驱动可在 RTIC 任务中调用，定时读取传感器
- [[rust-language]] — Rust 的类型系统和错误处理（`Result<(), Error>`）是驱动可靠性的保障
