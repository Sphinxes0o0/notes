---
type: source
created: 2026-05-22
sources: [notes-ccpp]
source-type: github
tags: [c, cpp, programming]
title: "Sphinx's C/C++ Technical Notes"
author: "Sphinx"
date: 2026-05-22
size: medium
path: raw/notes/ccpp/
summary: "C/C++ 技术笔记：序列化技术（JSON/XML/Protobuf/Boost/MessagePack）、智能指针深度分析、堆栈对象创建策略、移动语义与完美转发"
---

# C/C++ 技术笔记

## 核心内容

本来源包含 4 个 C/C++ 技术笔记文件，涵盖以下主题：

### 序列化技术
- **JSON**：nlohmann/json header-only 库使用、RapidJSON 高性能 SAX/DOM 解析
- **XML**：TinyXML-2 轻量级 XML 解析/生成
- **Protocol Buffers**：Google 高效二进制序列化，.proto 定义、跨语言支持
- **Boost.Serialization**：非入侵式序列化，支持文本/二进制/XML 归档
- **MessagePack**：介于 JSON 和 Protobuf 之间的二进制格式
- 序列化方案对比（JSON/XML/Protobuf/MessagePack/FlatBuffers/Thrift/ASN.1）
- 版本控制与兼容性、性能优化、安全性考虑

### 智能指针
- RAII 原则与原理
- unique_ptr 独占所有权、移动语义
- shared_ptr 引用计数机制、线程安全、循环引用
- weak_ptr 解决循环引用、lock() 方法
- 自定义删除器、make_shared vs new 对比
- 智能指针实现原理（控制块、原子引用计数）
- 智能指针 vs 裸指针（安全性、性能对比）

### 对象创建策略
- 限制对象只能在堆上创建（私有析构函数、protected 构造函数 + 静态工厂）
- 限制对象只能在栈上创建（私有 operator new/delete）

### 移动语义与完美转发
- 左值/右值/右值引用
- std::move 原理与实现
- std::forward 完美转发
- 通用引用（universal reference）
- STL 中的移动语义应用

## 关键引用

> "序列化就是将对象实例的状态转换为可保持或传输的格式的过程。与序列化相对的是反序列化，它根据流重构对象。"

> "RAII 核心思想：将资源的获取与对象的初始化绑定在一起，资源的释放与对象的销毁绑定在一起。"

## 相关页面
- [[entities/cpp/cpp-serialization]]
- [[entities/cpp/cpp-object-lifetime]]
- [[entities/cpp/smart-pointers]]
- [[entities/cpp/move-semantics]]
- [[entities/cpp/raii]]
