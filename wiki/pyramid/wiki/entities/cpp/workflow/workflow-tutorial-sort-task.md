---
type: entity
tags: [C++异步框架, Sort, 算法工厂, 并行排序]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 07: Sort Task

## 概述
`tutorial-07-sort_task` 展示如何使用 Workflow 的内置算法工厂创建排序任务。

## 创建排序任务
~~~cpp
// 普通排序
WFSortTask<int> *task = WFAlgoTaskFactory::create_sort_task(
    "sort", array, end, callback);

// 并行排序（加 "p" 参数）
WFSortTask<int> *task = WFAlgoTaskFactory::create_psort_task(
    "sort", array, end, callback);
~~~

## 处理结果
~~~cpp
void callback(WFSortTask<int> *task) {
    SortInput<int> *input = task->get_input();
    int *first = input->first;
    int *last = input->last;

    // 创建降序排序
    auto cmp = [](int a, int a2){ return a2 < a; };
    WFSortTask<int> *reverse = WFAlgoTaskFactory::create_sort_task(
        "sort", first, last, cmp, callback);
    series_of(task)->push_back(reverse);
}
~~~

## 计算线程配置
~~~cpp
struct WFGlobalSettings settings = GLOBAL_SETTINGS_DEFAULT;
settings.compute_threads = 16;
WORKFLOW_library_init(&settings);
~~~

## 队列名
- 不同队列名的任务公平调度
- 同队列内按提交顺序执行
- 推荐：每种计算任务用独立队列名

## 相关概念
- [[entities/cpp/workflow/workflow-compute-tasks]] — 计算任务总览
- [[entities/cpp/workflow/workflow-async-model]] — 异步模型