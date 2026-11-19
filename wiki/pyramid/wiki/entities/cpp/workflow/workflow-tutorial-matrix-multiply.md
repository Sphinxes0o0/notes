---
type: entity
tags: [C++异步框架, Matrix, 自定义计算, WFThreadTask]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 08: Matrix Multiply

## 概述
`tutorial-08-matrix_multiply` 展示如何创建自定义计算任务（CPU 密集型）。

## 定义计算任务
~~~cpp
namespace algorithm {
struct MMInput {
    Matrix a;
    Matrix b;
};

struct MMOutput {
    int error;
    size_t m, n, k;
    Matrix c;
};

void matrix_multiply(const MMInput *in, MMOutput *out) { ... }
}

using MMTask = WFThreadTask<algorithm::MMInput, algorithm::MMOutput>;
~~~

## 创建任务
~~~cpp
typedef WFThreadTaskFactory<MMInput, MMOutput> MMFactory;
MMTask *task = MMFactory::create_thread_task("matrix_multiply_task",
                                             matrix_multiply, callback);

MMInput *input = task->get_input();
input->a = {{1, 2, 3}, {4, 5, 6}};
input->b = {{7, 8}, {9, 10}, {11, 12}};
task->start();
~~~

## 带时限的计算任务
~~~cpp
MMTask *task = MMFactory::create_thread_task(
    seconds, nanoseconds, "queue_name", routine, callback);
// 超时后状态为 WFT_STATE_SYS_ERROR，error 为 ETIMEDOUT
~~~

## 算法与协议的对称性
- 自定义算法：提供 INPUT→OUTPUT 的 routine
- 自定义协议：提供 serialize/deserialize 接口

## 相关概念
- [[entities/cpp/workflow/workflow-compute-tasks]] — 计算任务总览
- [[entities/cpp/workflow/workflow-user-defined-protocol]] — 自定义协议