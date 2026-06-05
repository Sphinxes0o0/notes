---
title: C++ future / promise / async 源码示例
description: std::future、std::promise、std::shared_future、std::async、std::packaged_task 的示例代码
---

# future / promise / async 源码示例

本目录收录 C++ `<future>` 头文件相关并发原语的示例代码。

## 文件清单

| 文件 | 内容 |
|------|------|
| `aysnc.cc` | `std::async` 用法示例 |
| `future.cc` | `std::future` 基础用法 |
| `promise.cc` | `std::promise` 与 `std::future` 配合 |
| `shared_future.cc` | `std::shared_future` 多消费者场景 |
| `task.cc` | `std::packaged_task` 包装可调用对象 |

## 编译与运行

```bash
# 示例：编译 future.cc
g++ -std=c++17 -pthread future.cc -o future
./future
```
