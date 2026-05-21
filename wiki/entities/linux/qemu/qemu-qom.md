---
type: entity
tags: [QEMU, 虚拟机, 对象模型]
created: 2026-05-20
sources: [notes-qemu]
---

# QOM (QEMU Object Model)

## 定义

QEMU 的核心对象模型系统，提供动态类型注册、继承、接口实现等面向对象特性，是 QEMU 模拟器架构的基础。

## 关键要点

- **类型系统**: `TypeInfo` → `TypeImpl` 静态注册，`type_register_static()` 完成注册
- **对象结构**: `Object` / `ObjectClass` 分离（实例/类），通过 `parent` 形成树结构
- **属性系统**: `object_property_add_*()` 系列添加属性，`object_property_get/set()` 访问
- **接口机制**: 通过 `INTERFACE` 宏实现接口类型，支持 `TYPE_DEVICE`, `TYPE_BUS`, `TYPE_MEMORY_REGION` 等
- **类层次**: Type → OBJECT_CLASS → TYPE_OBJECT / TYPE_DEVICE / TYPE_BUS / TYPE_MEMORY_REGION → ...

## 设计模式

1. **原型模式**: 对象通过 `object_new` 原型克隆
2. **工厂模式**: `type_create_object` 工厂方法
3. **注册表模式**: 全局 `type_table` 存储所有类型
4. **组合模式**: 对象通过 `parent` 形成树结构

## 相关概念

- [[entities/linux/qemu/qemu-memory]] — MemoryRegion 继承自 Object
- [[entities/linux/qemu/qemu-cpu]] — CPU 设备通过 QOM 管理
- [[entities/linux/qemu/qemu-block-layer]] — BlockDriverState 使用 QOM

## 来源详情

- [[sources/github-notes-qemu]]
