---
type: entity
tags: [C++异步框架, 自定义计算任务, 线程任务]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 08: matrix_multiply 自定义计算任务

## 定义
展示如何实现自定义 CPU 计算任务（WFThreadTask）。

## 定义计算任务
~~~cpp
struct MMInput {
    Matrix a;
    Matrix b;
};
struct MMOutput {
    int error;
    Matrix c;
};
void matrix_multiply(const MMInput *in, MMOutput *out) { ... }

using MMTask = WFThreadTask<MMInput, MMOutput>;
MMTask *task = WFThreadTaskFactory<MMInput, MMOutput>::create_thread_task(
    "matrix_multiply_task", matrix_multiply, callback);
~~~

## 关键要点
- INPUT 和 OUTPUT 是两个模板参数
- routine 是从 INPUT 到 OUTPUT 的转换函数
- `task->get_input()` 和 `task->get_output()` 获取数据
- 计算任务失败时状态为 SUCCESS（算法是纯函数）

## 带运行时间限制
~~~cpp
task = create_thread_task(seconds, nanoseconds, queue_name, routine, callback);
// 超时状态：WFT_STATE_SYS_ERROR，错误码：ETIMEDOUT
// 注意：框架不会中断执行中的函数
~~~

## 算法与协议的对称性
- 自定义算法：提供 routine 函数
- 自定义协议：提供 encode/append 函数
- 算法和协议都非常纯粹，不知道 task、series 等的存在

## 相关概念
- [[entities/cpp/workflow/workflow-compute-tasks]] — 计算任务
- [[entities/cpp/workflow/workflow-user-defined-protocol]] — 自定义协议