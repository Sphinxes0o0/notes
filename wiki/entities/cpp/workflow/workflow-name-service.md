---
type: entity
tags: [C++异步框架, 命名服务, 服务发现, DNS]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 命名服务

## 定义
命名服务将域名解析为具体地址，支持自定义解析策略。

## 架构
- `WFNSPolicy`：名称服务策略基类
- `WFNameService`：全局名称服务注册表
- `WFGlobal::get_name_service()` 获取全局实例

## 自定义策略
~~~cpp
class MyPolicy : public WFNSPolicy {
    WFRouterTask *create_router_task(...) override;
};
// 实现中可修改 params->uri.host
// 然后交给 dns_resolver 执行
~~~

## 注册
~~~cpp
WFNameService *ns = WFGlobal::get_name_service();
ns->add_policy("domain.name", new MyPolicy(...));
// 或设置默认策略
ns->set_default_policy(new MyPolicy(...));
~~~

## 应用
- hosts 文件风格解析
- 服务发现系统对接
- 自定义负载均衡策略

## 相关概念
- [[entities/cpp/workflow/workflow-dns]] — DNS
- [[entities/cpp/workflow/workflow-upstream]] — Upstream
