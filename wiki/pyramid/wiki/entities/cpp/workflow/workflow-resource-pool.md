---
type: entity
tags: [C++异步框架, 资源池, 消息队列, 并发控制]
created: 2026-05-25
updated: 2026-05-27
sources: [workflow-engine]
---

# Workflow Resource Pool

## 定义
资源池（WFResourcePool）和消息队列（WFMessageQueue）用于控制任务并发度，实现串行化、资源限流等场景。

## 资源池（WFResourcePool）
- **场景**：限制总并发度、串行化访问、任务完成后归还资源
- **创建**：`WFResourcePool(void *const *res, size_t n)` 或 `WFResourcePool(size_t n)`
- **获取**：`pool.get(task)` 将任务包装为 Conditional
- **归还**：`pool.post(res)` 在 callback 中归还
- **特性**：FILO（刚释放的资源优先复用），可派生为 FIFO
- **示例**：限制抓取并发度不超过 max_p
  ~~~cpp
  WFResourcePool pool(max_p);
  for (url : urls) {
      WFHttpTask *task = create_http_task(url, [](WFHttpTask *t){ pool.post(nullptr); });
      WFConditional *cond = pool.get(task);
      cond->start();
  }
  ~~~

## 消息队列（WFMessageQueue）
- **区别**：长度无限制、先进先出、无需先获取再归还
- **创建**：`WFMessageQueue()`
- **使用**：与资源池相同的 get/post 接口
- **适用**：生产者-消费者场景、任务调度

## 应用场景
- 网络通信并发度限制
- 跨 series 串行化访问
- 资源获取后必须归还（资源池）
- 消息传递无需归还（消息队列）

## 相关概念
- [[entities/cpp/workflow/workflow-conditional]] — Conditional 是资源池的基础
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型