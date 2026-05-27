---
type: entity
tags: [C++异步框架, Sogou, 编译构建, xmake]
created: 2026-05-27
sources: [raw/workflow/xmake]
---

# Xmake 编译设计概念

## 定义

Sogou Workflow 使用 xmake 作为构建系统。本文记录编译、安装和模块裁剪的完整指南。

## 基本编译

~~~bash
# 编译 workflow 库
xmake

# 编译 test
xmake -g test
xmake run -g test

# 编译 tutorial
xmake -g tutorial

# 编译 benchmark
xmake -g benchmark
~~~

## 运行

~~~bash
xmake run -h    # 查看可运行的 target
xmake run -g tutorial -a tutorial-06-parallel_wget
~~~

## 安装

~~~bash
sudo xmake install
~~~

## 静态库 / 动态库切换

~~~bash
# 静态库
xmake f -k static && xmake -r

# 动态库
xmake f -k shared && xmake -r
~~~

## 模块裁剪

通过 `xmake f --help` 查看可裁剪的模块：

| 模块 | 选项 | 默认 |
|------|------|------|
| upstream | `--upstream=[y\|n]` | y |
| redis | `--redis=[y\|n]` | y |
| kafka | `--kafka=[y\|n]` | — |
| mysql | `--mysql=[y\|n]` | y |
| consul | `--consul=[y\|n]` | — |

**示例：** 编译不含 Redis 和 MySQL 的最小化版本：
~~~bash
xmake f --redis=n --kafka=y --mysql=n && xmake -r
~~~

## 相关页面

- [[workflow-build]] — Build 实体页
- [[workflow-tutorial-bugs]] — Tutorial 调试
