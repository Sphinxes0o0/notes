---
title: C++ 内存序 (memory_order) 源码示例
description: std::atomic memory_order_relaxed / acquire / release / seq_cst 的演示
---

# memory_order 源码示例

本目录收录 C++ 内存序（memory order）的演示代码，验证不同 `std::memory_order` 在多线程场景下的可见性与重排约束。

## 文件清单

| 文件 | 内容 |
|------|------|
| `mem_order_demo.cc` | 各种 memory_order 的对比演示 |
| `msg_pass.cc` | acquire-release 消息传递模式 |

## 编译与运行

```bash
g++ -std=c++17 -pthread mem_order_demo.cc -o mem_order_demo
./mem_order_demo
```

## 进一步阅读

- [cppreference: std::memory_order](https://en.cppreference.com/w/cpp/atomic/memory_order)
