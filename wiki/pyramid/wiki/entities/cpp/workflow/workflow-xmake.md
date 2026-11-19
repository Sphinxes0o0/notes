---
type: entity
tags: [C++异步框架, 编译, xmake, 构建]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow xmake 编译

## 基本编译
~~~bash
xmake                      # 编译 workflow 库
xmake -g test              # 编译测试
xmake run -g test          # 运行测试
xmake -g tutorial          # 编译教程
xmake -g benchmark         # 编译性能测试
sudo xmake install         # 安装
~~~

## 静态/动态库切换
~~~bash
xmake f -k static && xmake -r   # 静态库
xmake f -k shared && xmake -r   # 动态库
~~~

## 模块裁剪
~~~bash
xmake f --help  # 查看可裁剪模块
xmake f --redis=n --kafka=y --mysql=n
xmake -r
~~~

## 可裁剪模块
- `--upstream` — Upstream 组件
- `--consul` — Consul 组件
- `--redis` — Redis 协议（默认 y）
- `--kafka` — Kafka 协议
- `--mysql` — MySQL 协议（默认 y）

## 运行教程
~~~bash
xmake run tutorial-06-parallel_wget
~~~