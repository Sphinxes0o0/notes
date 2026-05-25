---
type: entity
tags: [C++异步框架, 多选一, 任务选择]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Selector

## 定义
Selector 用于多选一场景：从多个异步分支中选择第一个成功完成的结果进行处理，丢弃其它结果。

## 关键要点
- **创建**：`WFTaskFactory::create_selector_task(candidates, callback)`
- **提交**：`selector->submit(msg)`，第一个非空消息被接受返回 1，后续返回 0
- **空消息**：`submit(NULL)` 表示分支失败，所有候选都提交 NULL 则状态为 `WFT_STATE_SYS_ERROR`
- **获取消息**：`selector->get_message()`
- **应用场景**：
  - 多下游冗余请求
  - Backup request
  - 并行计算中任一线程先完成

## 示例
~~~cpp
selector = WFTaskFactory::create_selector_task(3, [](WFSelectorTask *s) {
    void *msg = s->get_message();
    if (msg) printf("%s\n", (char *)msg);
    else printf("failed\n");
});
// 任意 HTTP 先完成则 submit 结果
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-conditional]] — 条件任务
