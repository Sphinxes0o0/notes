---
type: entity
tags: [C++异步框架, 排序, 算法工厂, 算法任务]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 07: sort_task 算法工厂

## 定义
展示如何使用内置算法工厂创建排序任务。

## 创建排序任务
~~~cpp
WFSortTask<int> *task;
if (use_parallel_sort)
    task = WFAlgoTaskFactory::create_psort_task("sort", array, end, callback);
else
    task = WFAlgoTaskFactory::create_sort_task("sort", array, end, callback);
task->start();
~~~

## 排序任务特点
- 模板参数：数组数据类型（如 `int`）
- 输入输出：`SortInput<T>` 和 `SortOutput<T>`（相同数组）
- 队列名：影响任务调度顺序

## 处理结果
~~~cpp
void callback(WFSortTask<int> *task) {
    SortInput<T> *input = task->get_input();
    // 升序完成后创建降序任务
    if (task->user_data == NULL) {
        auto cmp = [](int a1, int a2){ return a2 < a1; };
        reverse = WFAlgoTaskFactory::create_sort_task("sort", first, last, cmp, callback);
        series_of(task)->push_back(reverse);
    }
}
~~~

## 配置计算线程数
~~~cpp
struct WFGlobalSettings settings = GLOBAL_SETTINGS_DEFAULT;
settings.compute_threads = 16;
WORKFLOW_library_init(&settings);
~~~

## 并行排序算法
- 分块 + 二路归并，O(1) 空间
- 最多 128 线程，加速比小于线程数

## 相关概念
- [[entities/cpp/workflow/workflow-compute-tasks]] — 计算任务
- [[entities/cpp/workflow/workflow-go-task]] — Go Task