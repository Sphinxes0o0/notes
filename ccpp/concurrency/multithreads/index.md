---
title: 多线程 atexit 行为示例
description: 多线程程序中 atexit / destructor 触发顺序的演示
---

# 多线程 atexit

本目录收录多线程程序中 `atexit()` 注册的清理函数、以及线程局部析构顺序的演示代码。

## 文件清单

| 文件 | 内容 |
|------|------|
| `multithread_atexit.c` | 基础多线程 + atexit 示例 |
| `multithread_atexit_advanced.c` | 进阶：线程局部存储 + atexit 顺序 |

## 编译与运行

```bash
gcc -std=c11 -pthread multithread_atexit.c -o multithread_atexit
./multithread_atexit
```
