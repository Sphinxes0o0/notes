---
type: index
tags: [C++异步框架, Sogou, 模块索引]
created: 2026-05-25
---

# Workflow Engine 模块索引

> Sogou C++ Workflow 异步引擎文档索引页

## 架构核心

### 任务模型
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-async-model]] | 异步任务模型总览 |
| [[entities/cpp/workflow/workflow-go-task]] | Go Task 计算任务 |
| [[entities/cpp/workflow/workflow-counter]] | Counter 计数器 |
| [[entities/cpp/workflow/workflow-timer]] | Timer 定时器 |
| [[entities/cpp/workflow/workflow-selector]] | Selector 多选一 |
| [[entities/cpp/workflow/workflow-conditional]] | Conditional 条件任务 |
| [[entities/cpp/workflow/workflow-module-task]] | Module 模块封装 |
| [[entities/cpp/workflow/workflow-graph-task]] | Graph DAG 图任务 |
| [[entities/cpp/workflow/workflow-resource-pool]] | Resource Pool 资源池 |

### 基础设施
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-config]] | 全局配置 |
| [[entities/cpp/workflow/workflow-error-handling]] | 错误处理 |
| [[entities/cpp/workflow/workflow-exit-handling]] | 程序退出 |
| [[entities/cpp/workflow/workflow-timeout]] | 超时机制 |
| [[entities/cpp/workflow/workflow-connection-context]] | 连接上下文 |

### 网络与协议
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-dns]] | DNS 解析与缓存 |
| [[entities/cpp/workflow/workflow-upstream]] | Upstream 负载均衡 |
| [[entities/cpp/workflow/workflow-service-governance]] | 服务治理 |
| [[entities/cpp/workflow/workflow-tlv-message]] | TLV 消息格式 |
| [[entities/cpp/workflow/workflow-user-defined-protocol]] | 自定义协议 |
| [[entities/cpp/workflow/workflow-name-service]] | 命名服务 |

### 调试与工具
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-benchmark]] | 性能测试 |
| [[entities/cpp/workflow/workflow-known-bugs]] | 已知问题 |
| [[entities/cpp/workflow/workflow-build]] | 编译与构建 |

## 教程

### 基础入门
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-tut-wget]] | wget 第一个 HTTP 任务 |
| [[entities/cpp/workflow/workflow-tut-redis-cli]] | redis_cli Redis 客户端 |
| [[entities/cpp/workflow/workflow-tut-wget-to-redis]] | wget_to_redis 任务链 |
| [[entities/cpp/workflow/workflow-tut-http-echo-server]] | http_echo_server HTTP 服务器 |
| [[entities/cpp/workflow/workflow-tut-http-proxy]] | http_proxy HTTP 代理 |

### 并行与计算
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-tut-parallel-wget]] | parallel_wget 并行抓取 |
| [[entities/cpp/workflow/workflow-tut-sort-task]] | sort_task 算法工厂 |
| [[entities/cpp/workflow/workflow-tut-matrix-multiply]] | matrix_multiply 自定义计算 |
| [[entities/cpp/workflow/workflow-tut-http-file-server]] | http_file_server 异步文件 IO |

### 高级协议
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-user-defined-protocol]] | 自定义协议 |
| [[entities/cpp/workflow/workflow-tut-mysql-cli]] | mysql_cli MySQL 客户端 |
| [[entities/cpp/workflow/workflow-tut-dns-cli]] | dns_cli DNS 客户端 |
| [[entities/cpp/workflow/workflow-tut-name-service]] | name_service 自定义命名服务 |
| [[entities/cpp/workflow/workflow-tut-redis-subscriber]] | redis_subscriber Redis 订阅 |
| [[entities/cpp/workflow/workflow-tut-dns-server]] | dns_server DNS 服务器 |

### 客户端
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-network-client]] | HTTP/Redis/MySQL/Kafka/DNS 客户端 |
| [[entities/cpp/workflow/workflow-redis-features]] | Redis 订阅模式 |

### 服务器
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-http-server]] | HTTP Server 教程 |
| [[entities/cpp/workflow/workflow-dns-server]] | DNS Server |

### 高级
| Entity | 主题 |
|--------|------|
| [[entities/cpp/workflow/workflow-parallel-tasks]] | Series/Parallel 并行任务 |
| [[entities/cpp/workflow/workflow-compute-tasks]] | 计算任务与算法工厂 |

## 源文档

| Source | 说明 |
|--------|------|
| [[sources/workflow-engine]] | Sogou Workflow 文档汇总 |

## 核心概念

```
┌─────────────────────────────────────────────────────────┐
│                    Workflow 异步模型                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Series    │  │  Parallel   │  │    Graph    │    │
│  │  (串行链)   │  │  (并行组)   │  │  (DAG图)    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │            │
│  ┌──────┴────────────────┴────────────────┴──────┐    │
│  │              任务类型                           │    │
│  │  ┌─────┐ ┌─────┐ ┌──────┐ ┌──────┐ ┌─────┐   │    │
│  │  │HTTP │ │Redis│ │MySQL │ │Kafka │ │ DNS │   │    │
│  │  │Task │ │Task │ │ Task │ │ Task │ │Task │   │    │
│  │  └─────┘ └─────┘ └──────┘ └──────┘ └─────┘   │    │
│  │  ┌─────┐ ┌─────┐ ┌──────┐ ┌──────┐ ┌─────┐   │    │
│  │  │ Go  │ │Sort │ │ Timer│ │Counter│ │File │   │    │
│  │  │Task │ │Task │ │      │ │      │ │ IO  │   │    │
│  │  └─────┘ └─────┘ └──────┘ └──────┘ └─────┘   │    │
│  └──────────────────────────────────────────────┘    │
│                                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │                 服务治理                        │    │
│  │  Upstream │ DNS │ 熔断 │ 负载均衡 │ 主备      │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 关键特性

- **13+ 协议支持**：HTTP、Redis、MySQL、Kafka、DNS、TLV、自定义
- **高性能**：500K QPS，优于 nginx
- **服务治理**：Upstream、熔断、负载均衡
- **异步 IO**：Linux aio、epoll/kqueue
- **线程池**：默认 CPU 核数
