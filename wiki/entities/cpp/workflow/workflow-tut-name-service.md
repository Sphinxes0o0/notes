---
type: entity
tags: [C++异步框架, 命名服务, 自定义策略]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 15: name_service 自定义命名服务

## 定义
通过自定义 WFNSPolicy 实现名称服务策略，将域名解析为自定义地址。

## 自定义策略
~~~cpp
class MyNSPolicy : public WFNSPolicy {
    WFRouterTask *create_router_task(const WFNSParams *params,
                                     router_callback_t callback) override {
        // 读取 hosts 文件风格的配置文件
        // 修改 params->uri.host
        // 交给全局 dns resolver 执行
        return WFGlobal::get_dns_resolver()->create_router_task(
            params, std::move(callback));
    }
};
~~~

## 注册策略
~~~cpp
WFNameService *ns = WFGlobal::get_name_service();
ns->add_policy("domain.name", new MyPolicy(filename));

// 设置默认策略（所有域名）
ns->set_default_policy(new MyPolicy(...));
// 恢复默认
ns->set_default_policy(WFGlobal::get_dns_resolver());
~~~

## 配置文件格式
~~~bash
127.0.0.1 www.myhost.com
192.168.10.10 host1
www.sogou.com sogou  # 指向 www.sogou.com
~~~

## 应用场景
- hosts 文件风格解析
- 服务发现系统对接
- 测试环境地址映射

## 相关概念
- [[entities/cpp/workflow/workflow-dns]] — DNS
- [[entities/cpp/workflow/workflow-upstream]] — Upstream