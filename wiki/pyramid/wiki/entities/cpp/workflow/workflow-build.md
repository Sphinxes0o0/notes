---
type: entity
tags: [C++异步框架, 编译, xmake, 构建]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 编译与构建

## 定义
Workflow 使用 xmake 作为构建系统，支持库裁剪、静态/动态库切换、安装等。

## 基本命令

### 编译
~~~bash
xmake                          # 编译库
xmake -g test                  # 编译测试
xmake run -g test              # 运行测试
xmake -g tutorial              # 编译教程
xmake -g benchmark             # 编译 benchmark
xmake run tutorial-06-parallel_wget  # 运行示例
sudo xmake install             # 安装库
~~~

### 库类型切换
~~~bash
xmake f -k static              # 编译静态库
xmake f -k shared              # 编译动态库
xmake -r                       # 重新构建
~~~

## 模块裁剪

### 可选模块
| 选项 | 说明 | 默认 |
|------|------|------|
| --redis | Redis 客户端 | y |
| --kafka | Kafka 客户端 | - |
| --mysql | MySQL 客户端 | y |
| --upstream | Upstream 组件 | y |
| --consul | Consul 组件 | - |

### 编译示例
~~~bash
xmake f --redis=n --kafka=y --mysql=n
xmake -r
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-config]] — 全局配置