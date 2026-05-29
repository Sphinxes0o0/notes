---
type: entity
tags: [embedded-rust, pac, peripheral-access, svd2rust, register, bare-metal]
created: 2026-05-29
sources: [bookmark-rust-embedded-drivers]
---

# Embedded Rust PAC

## 定义

PAC (Peripheral Access Crate) 是嵌入式芯片的寄存器级抽象，通过 SVD（System View Description）文件自动生成（svd2rust），提供对芯片所有外设寄存器的类型安全读写能力。

## 关键要点

- **SVD 文件**: 芯片厂商提供的 XML 描述文件，包含外设地址、中断向量、寄存器字段
- **svd2rust**: 自动生成 `pac` crate，将 SVD 转换为 Rust 结构体
  - 每个外设一个结构体（如 `peripherals.SPI1`）
  - 每个寄存器一个字段（如 `spi1.cr1`）
  - 寄存器字段类型安全（`u8`/`u16`/`u32`，位域枚举）
- **volatile 读写**: 寄存器读写通过 `volatile::Volatile` 包装，防止编译器优化
- **寄存器命名**: 直接对应芯片参考手册（RM030、RM043 等）
- **PAC vs HAL**: PAC 是"你怎么写 C 寄存器操作"，HAL 是"你怎么写嵌入式 Python"
- **与 no_std 的关系**: PAC 本身无任何 std 依赖，可在纯裸机环境使用

## 使用模式

```rust
// 直接写寄存器
let rcc = &peripherals.RCC;
rcc.apb1enr.modify(|_, w| w.tim2en(true));

let tim2 = peripherals.TIM2;
tim2.cr1.write(|w| w.cen().enabled());
tim2.egr.write(|w| w.ug().update());
```

## 相关概念

- [[embedded-rust-hal]] — HAL trait 的实现内部调用 PAC 寄存器操作
- [[embedded-rust-rtic]] — RTIC 运行时通过 PAC 操作 NVIC 中断控制器
- [[rust-language]] — Rust 的 const generics 和类型系统使 PAC 寄存器访问类型安全
- [[armv8-architecture]] — PAC 生成背后是 ARM 架构的外设寄存器映射
