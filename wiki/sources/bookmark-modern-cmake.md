---
type: source
source-type: bookmark
title: "Modern CMake 教程 (中文版)"
author: "The packtworkshops & Henry Schreiner; 译者: modern-cmake-cn"
date: 2024
size: medium
path: raw/github/modern-cmake-cn/Modern-CMake-zh_CN
summary: "系统化 Modern CMake 3.1+ 教程，从安装到高级包管理，纠正网上散乱的 CMake 错误用法，是 C++ 构建工程的权威指南。"
tags: [cpp, cmake, build-system, professional-engineering]
---

# Modern CMake 教程 (中文版)

## Overview

Modern CMake 教程中文版，系统化覆盖 CMake 从入门到高级主题。与网上散乱的 Stack Overflow 答案不同，本教程提供一致、现代化的 CMake 3.1+ 最佳实践。

> "It aims to address the problems with bad examples and 'best practices' found everywhere on the internet."

## Core Content

### Topics by Level

**基础：**
- CMake 安装与运行
- `CMakeLists.txt` 基本语法
- 变量与缓存
- 条件与循环
- 函数与宏

**进阶：**
- C++11/14/17/20/23 支持
- 检测编译器特性 (`check_cxx_compiler_flag`)
- 查找包 (`find_package`)
- 子项目 (add_subdirectory)
- 导出与安装 (export, install)

**高级包管理：**
- CUDA 支持
- OpenMP
- Boost
- MPI
- ROOT / Minuit2

**工具集成：**
- IDE 集成 (Visual Studio, CLion, Xcode)
- GoogleTest 集成
- Catch2 集成
- 调试技巧

### Key CMake Best Practices

- **目标导向**: `target_include_directories`, `target_compile_options` 优先于全局设置
- **现代特性**: CMP0054, CMP0068 等策略
- **版本感知**: `cmake_minimum_required()` 在文件顶部
- **避免全局**: 不使用 `include_directories()` 等全局命令
- **R路径**: 正确处理 macOS `@rpath`

## 相关页面

### Entity 页面
- [[entities/cpp/modern/c17-11-ecosystem]] — C++17 生态系统（含 CMake）
- [[entities/cpp/cpp-high-performance]] — C++ 高性能（与构建优化相关）

### Source 页面
- [[sources/cpp-modern-skills]] — Modern C++ Skills（含 c17-11-ecosystem）
