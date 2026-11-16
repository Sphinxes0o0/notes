---
type: entity
tags: [C++异步框架, 命名服务, DNS, 自定义策略]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 15: Name Service

## 概述
`tutorial-15-name_service` 展示如何自定义命名服务策略。

## 需求场景
- 通过文本文件指定域名 → IP 的映射
- 文件格式与 `/etc/hosts` 兼容
- 支持域名指向其他域名

## 实现命名策略
~~~cpp
class MyNSPolicy : public WFNSPolicy {
public:
    WFRouterTask *create_router_task(
        const struct WFNSParams *params,
        router_callback_t callback) override {
        // 从文件读取映射
        std::string dest = read_from_file(params->uri.host);
        if (!dest.empty()) {
            free(params->uri.host);
            params->uri.host = strdup(dest.c_str());
        }
        // 交给 DNS resolver 执行
        return WFGlobal::get_dns_resolver()->create_router_task(
            params, std::move(callback));
    }
};
~~~

## 注册策略
~~~cpp
MyNSPolicy *policy = new MyNSPolicy(filename);
WFNameService *ns = WFGlobal::get_name_service();
ns->add_policy(name, policy);  // 为特定域名添加策略
// 或
ns->set_default_policy(policy);  // 全局默认策略

// 清理
ns->del_policy(name);
delete policy;
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-dns]] — DNS 详细
- [[entities/cpp/workflow/workflow-upstream]] — Upstream