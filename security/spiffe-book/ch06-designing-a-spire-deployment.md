---
title: "第 6 章　设计一个 SPIRE 部署"
description: "你的 SPIRE 部署设计应当满足团队和组织的**技术需求**。它也应当**纳入对可用性、可靠性、安全性、扩展性、性能的要求**。这份设计将作为你部署工作的基础。"
---
# 第 6 章　设计一个 SPIRE 部署

> 原书：*Chapter 6. Designing a SPIRE Deployment*（p.104–132）
> 翻译策略：技术直译 + 段落重排；专有项目名、协议名、API 名、CLI 命令、配置字段、证书/加密术语一律保留英文；首次出现的关键概念以"中文（English）"形式给出，后续沿用英文。术语对照见 **`TERMS.md`**。

## 章节导言

> 本章介绍 SPIRE 部署的组件、可用的部署模型，以及在部署 SPIRE 时需要纳入考量的性能与安全考量。

你的 SPIRE 部署设计应当满足团队和组织的**技术需求**。它也应当**纳入对可用性、可靠性、安全性、扩展性、性能的要求**。这份设计将作为你部署工作的基础。

## 你的身份命名方案

回想前几章——**SPIFFE ID 是一个结构化字符串，代表一个工作负载的身份名**（如第 4 章所见）。**工作负载标识段**（URI 的 path 段）追加在**信任域名**（URI 的 host 段）之后，可以被**组合**起来以传达"服务归属"——比如它跑在哪个平台、谁拥有它、它的预期用途，或其他约定。它被有意设计为**灵活、可定制**。

**你的命名方案可以是分层的，就像文件系统路径那样**。话虽如此，**为了减少歧义，命名方案不应以结尾的斜杠（`/`）结束**。下面你会看到三种不同约定的若干样例，**你也可以自创**。

### 直接标识服务

你可能会觉得有用——**直接从"应用视角的功能"和"它在软件生命周期中运行的环境"来标识一个服务**。例如，管理员可以规定：**任何跑在某个特定环境中的进程，都应该能以某个特定身份出示自己**。比如：

```
spiffe://staging.example.com/payments/mysql
```

或者：

```
spiffe://staging.example.com/payments/web-fe
```

上面这两个 SPIFFE ID 分别对应**支付服务的两个不同组件**——一个 MySQL 数据库服务、一个 web 前端——它们都跑在 staging 环境。**`staging` 代表环境，`payments` 代表高层服务**。

> **关键洞察**：前面两个与后面两个例子都是示意性、**而非规范性**的。**实现者应该权衡自己的选项，决定自己偏好的做法**。

### 标识服务所有者

通常，**更上层的编排器和平台有自己的身份概念**（比如 Kubernetes service account、AWS/GCP service account），**把 SPIFFE 身份直接映射到那些身份上**会很有用。比如：

```
spiffe://k8s-workload-cluster.example.com/ns/staging/sa/default
```

在这个例子里，**Trust Domain `example.com` 的管理员在跑一个 Kubernetes 集群 `k8s-workload-cluster.example.com`**，它有一个 `staging` 命名空间，里面有一个叫 `default` 的 service account（SA）。

### 不透明的 SPIFFE 身份

**SPIFFE path 也可以是不透明的**，然后**元数据保存在一份二级数据库中**——通过查询它来获取与该 SPIFFE 标识符关联的任何元数据。例如：

```
spiffe://example.com/9eebccd2-12bf-40a6-b262-65fe0487d4
```

## SPIRE 部署模型

我们将概述在生产中运行 SPIRE 的**最常见的三种方式**。这并不意味着我们想限制可选方案——**只是出于本书篇幅考虑，我们把范围限定在这些"运行 SPIRE Server 的常见方式"上**。**我们将只关注 Server 端的部署架构**，**因为通常每个节点只装一个 Agent**。

### "多少个"问题：大 Trust Domain vs 小 Trust Domain

**Trust Domain 的数量预期相对固定，只是偶尔回顾一下，不应随时间漂移太多**。**而一个给定 Trust Domain 内的节点数、以及工作负载数，会因负载和增长而频繁波动**。

**到底走"集中到一个根信任、一个大 Trust Domain"还是"分散隔离成多个 Trust Domain"，由多种因素决定**。**本章的安全考量一节会讨论 Trust Domain 在隔离方面的应用**。**选择多个小 Trust Domain 而非一个大 Trust Domain 还有其他一些原因**，比如提升多租户的可用性与隔离。**管理域边界、工作负载数量、可用性要求、云厂商数量、认证要求**这些变量都会影响决策。

举例来说，你可能选择为**每一个独立的管理边界**单独搞一个 Trust Domain——让组织里那些可能有不同开发实践的各个组之间保持自治。

> 表 6.1　Trust Domain 规模决策表（参考 `assets/pages/page-107.png`）
>
> | | 单 Trust Domain | 嵌套 | 联邦 |
> |---|---|---|---|
> | **部署规模** | 大 | 非常大 | 大 |
> | **跨 region** | 否 | 是 | 是 |
> | **跨云** | 否 | 是 | 是 |

### 一一对应：单 Trust Domain 里的单个 SPIRE 集群

**对单 Trust Domain 来说，以高可用配置部署的单个 SPIRE Server 是最好的起点**。

> 图 6.1　单 Trust Domain（见 `assets/pages/page-108.png`）。

但当你的 SPIRE Server 单点部署要服务**跨 region、跨平台、跨云厂商**的 Trust Domain 时，**当 SPIRE Agent 依赖一个地理上遥远的 SPIRE Server 时，可能出现扩展性问题**。**如果单一部署必须横跨多个环境，那么在单 Trust Domain 下"用共享数据存储"的解决方案就是配置成嵌套拓扑的 SPIRE Server**。

### 嵌套 SPIRE

**SPIRE Server 的嵌套拓扑**让你能把 **SPIRE Agent 与 SPIRE Server 之间的通信距离**压到最短。

> 图 6.2　嵌套 SPIRE 拓扑（见 `assets/pages/page-109.png`）。

在嵌套拓扑中，**顶层 SPIRE Server 持有根证书和密钥**，**下层 Server 向顶层申请一张中间签名证书**，作为下层 Server 的 X.509 签名机构。**如果顶层挂了，下层 Server 仍能继续运行——为拓扑提供韧性**。

**嵌套拓扑非常适合多云部署**。**由于能混搭 Node Attestor**，**下层 Server 可以驻留在不同云厂商环境中，为那里的工作负载和 Agent 提供身份**。

> 图 6.3　一种企业架构示意：1 个上游 SPIRE Server + 2 个嵌套 SPIRE Server。**两个嵌套 SPIRE Server 各自可以有独立的配置（对 AWS 和 Azure 相关），且任一方失效都不影响另一方**（见 `assets/pages/page-110.png`）。

> **关键洞察**：虽然嵌套 SPIRE 是提升 SPIRE 部署灵活性和扩展性的理想方式，**但它不提供任何额外安全性**。由于 X.509 没有任何办法限制"中间证书签发机构"的权力，**每个 SPIRE Server 都可以签发任何证书**。**即使你的 upstream CA 是放在公司地下室混凝土掩体里的加固服务器——一旦你的 SPIRE Server 被攻破，你的整个网络都可能陷入风险**。**因此，要保证每个 SPIRE Server 自身的安全**。

### 联邦 SPIRE

**部署可能需要多个信任根**——也许是因为组织有不同的部门、各自的管理员，**或者他们有相互独立的 staging 与 production 环境、偶尔需要通信**。

另一个用例是**组织之间的 SPIFFE 互操作**，比如云厂商与它的客户之间。

> 图 6.4　SPIRE Server 使用联邦 Trust Domain（见 `assets/pages/page-111.png`）。

**这些"多个 Trust Domain 与互操作"用例都要求一个良定义的、可互操作的方法——让一个 Trust Domain 中的工作负载能认证另一个 Trust Domain 中的工作负载**。在联邦 SPIRE 中，**不同 Trust Domain 之间的信任**是这样建立的：先认证对方 bundle endpoint 的身份，再通过这条已认证的 endpoint 拉取对方 Trust Domain 的 bundle。

### 独立 SPIRE Server

**运行 SPIRE 最简单的方式**是部署在专用服务器上，**尤其当只有一个 Trust Domain，且工作负载数量不多时**。在那种情况下，你可以**把数据存储共置在同一节点上**（用 SQLite 或 MySQL 当数据库），**简化部署**。但**采用共置部署模型时，记得考虑数据库的复制或备份**。**如果这个节点丢了，你可以快速在另一台节点上跑起 SPIRE Server，但你所有的 Agent 与工作负载需要重新证明才能拿到新身份——如果你把数据库也一起丢了**。

> 图 6.5　单个专用 SPIRE Server（见 `assets/pages/page-112.png`）。

### 避免单点故障

**简洁带来的好处总是有代价的**。**如果只有一台 SPIRE Server、它又丢了，那一切就都没了——一切都要重建**。**系统的可用性可以通过部署多台 Server 来提升**。**仍然会有一份共享的数据存储、安全的连通性、以及数据复制**。**我们会在本章稍后讨论这些决策带来的不同安全影响**。

**要对 SPIRE Server 做水平扩展**，就把同一 Trust Domain 内的所有 Server 都配置为读写同一份共享数据存储。**数据存储是 SPIRE Server 持久化动态配置信息（比如注册条目、身份映射策略）的地方**。**SQLite 与 SPIRE Server 绑定打包，是默认的数据存储**。

> 图 6.6　在 HA 上跑多个 SPIRE Server 实例（见 `assets/pages/page-113.png`）。

## 数据存储建模

在做数据存储设计时，**你主要的关注点应当是冗余与高可用**。你需要决定**每个 SPIRE Server 集群是各自拥有专属的数据存储，还是所有集群共享一份**。

**数据库选型可能会受到整个系统可用性要求、运维团队能力的影响**。比如，**如果运维团队有 MySQL 的支持与扩展经验，那就应该把它作为首选**。

### 每个集群一份专属数据存储

**多份数据存储让系统的每个专属部分拥有更高的独立性**。比如，AWS 和 GCP 云上的 SPIRE 集群可以各自拥有独立的数据存储，**或者 AWS 上的每个 VPC 都可以有一份专属的数据存储**。**这种选择的优势是：如果一个 region 或云厂商挂了，其他 region 或云厂商上跑的 SPIRE 部署不受影响**。

**每集群一份数据存储的缺点**在重大故障时最明显。**如果某个 region 里的 SPIRE 数据存储（进而所有 SPIRE Server）挂了，就只能去恢复那份本地数据存储、或者把 Agent 切到同一 Trust Domain 内的另一套 SPIRE Server 集群上**——假设这个 Trust Domain 跨 region。

**如果不得不把 Agent 切到新集群，必须做特殊的考量**——**新集群不会知道"另一套 SPIRE 集群已经签发出去的身份"，也不知道那套集群里的注册条目**。**Agent 必须向新集群重新证明**，**注册条目要么从备份恢复、要么重新构建**。

> 图 6.7　如果需要把一个集群里的所有 Agent 迁移到另一个集群，会发生什么？（见 `assets/pages/page-114.png`）

### 共享数据存储

**共享数据存储解决了上面"每集群一份数据存储"带来的问题**。**然而，它可能让设计与运维更复杂——并要依赖其他系统来检测宕机、在故障时更新 DNS 记录**。**而且这种设计仍然要求为每个 SPIRE 可用域（按 region 或数据中心）部署数据库基础设施部件**。**请查阅 SPIRE 文档获取更多细节**（参考 [github.com/spiffe/spire/blob/master/doc/plugin_...](https://github.com/spiffe/spire/blob/master/doc/plugin_server_datastore_sql.md)）。

> 图 6.8　两套集群使用 Global 数据存储方案（见 `assets/pages/page-115.png`）。

## 故障管理

**当基础设施宕机发生时，主要的关切点是：如何继续为需要 SVID 才能正常工作的那些工作负载签发 SVID**。**SPIRE Agent 的内存 SVID 缓存被设计为抵御短期宕机的第一道防线**。

**SPIRE Agent 会周期性地从 SPIRE Server 拉取"被授权签发"的 SVID**——提前准备好，等工作负载需要时就能下发给它们。**这个过程在工作负载实际请求 SVID 之前就已经完成**。

### 性能与可靠性

**SVID 缓存带来两个好处：性能与可靠性**。**当工作负载请求自己的 SVID 时，Agent 不必再向 SPIRE Server 发起请求、等它签发——因为它早就在本地缓存好了——这避免了去 SPIRE Server 的往返**。**另外，如果工作负载请求 SVID 时 SPIRE Server 不可用，也不会影响 SVID 签发，因为 Agent 早就缓存好了**。

**我们需要区分 X509-SVID 与 JWT-SVID**。**JWT-SVID 不能提前签发**，**因为 Agent 不知道工作负载需要的 JWT-SVID 的具体 audience（受众）**——**Agent 只预缓存 X509-SVID**。**不过，SPIRE Agent 确实会维护一份"已签发 JWT-SVID"的缓存**，**只要缓存里的 JWT-SVID 仍然有效，它就能签发 JWT-SVID 给工作负载——不必联系 SPIRE Server**。

### TTL

**SVID 有一个重要属性是它的 TTL（time-to-live）**。**当缓存中的 SVID 剩余寿命不到 TTL 的一半时，SPIRE Agent 会为它续期**。**这告诉我们：SPIRE 在"对底层基础设施能否按时下发 SVID"这件事上是持保守态度的**。**同时也提示了 SVID TTL 在抵御宕机韧性中所扮演的角色**。

**更长的 TTL 给你更多时间修复和恢复任何基础设施宕机**——但**TTL 的选择要在安全与可用性之间做权衡**。**长 TTL 会给修复宕机留出充裕时间，但代价是让 SVID（以及相关密钥）暴露在更长时间里**。**短 TTL 缩小了恶意行为者利用被攻破 SVID 的时间窗口，但要求你对宕机的反应更快**。**可惜，没有一个"万能"的 TTL 能通吃所有部署**。**你必须在"留出多长的窗口来应对宕机"和"愿意让已签发的 SVID 暴露多久"之间做权衡**。

## 在 Kubernetes 中运行 SPIRE

本节讲述在 Kubernetes 中运行 SPIRE 的细节。**Kubernetes 是一个容器编排器，可以在多种云厂商上、也可以在物理硬件上管理软件部署与可用性**。**SPIRE 提供了多种不同形式的 Kubernetes 集成**。

### Kubernetes 中的 SPIRE Agent

**Kubernetes 包含 DaemonSet 的概念**——一个自动部署在所有节点上的容器，每个节点跑一份。**这是跑 SPIRE Agent 的完美方式——因为一个节点必须有一个 Agent**。

**新的 Kubernetes 节点上线时，调度器会自动为它们拉起新的 SPIRE Agent**。**首先，每个 Agent 需要一份 bootstrap trust bundle**。**最简单的方式是通过 Kubernetes ConfigMap 把它分发出去**。

**Agent 一旦拿到 bootstrap trust bundle，就要去 Server 证明自己的身份**。**Kubernetes 提供了两类认证 token**：

1. **Service Account Tokens（SATs）**
2. **Projected Service Account Tokens（PSATs）**

**Service Account Tokens 对安全来说并不理想**——因为它们**永远有效、且作用域无限制**。**Projected Service Account Tokens 安全得多**——但它们**要求较新版本的 Kubernetes、并开启一个特殊 feature flag**。**SPIRE 同时支持 SAT 和 PSAT 来做节点证明**。

### Kubernetes 中的 SPIRE Server

**SPIRE Server 与 Kubernetes 的交互有两种方式**。**首先，每当 trust bundle 变化时，它要把 trust bundle 写到一份 Kubernetes ConfigMap**。**其次，Agent 上线时，它需要用 TokenReview API 来校验它们的 SAT 或 PSAT token**。**这两件事都通过 SPIRE 插件来配置，要求有相应的 Kubernetes API 权限**。

**SPIRE Server 可以完全跑在 Kubernetes 里、与工作负载并置**。**但出于安全考虑，更可取的做法是把它跑在独立的 Kubernetes 集群或独立硬件上**。**这样一来，如果主集群被攻破，SPIRE 私钥就不会有风险**。

> 图 6.9　SPIRE Server 与工作负载跑在同一集群（见 `assets/pages/page-118.png`）。

> 图 6.10　出于安全考虑，SPIRE Server 跑在独立的集群（见 `assets/pages/page-119.png`）。

### Kubernetes 工作负载证明

**SPIRE Agent 内置一个 Kubernetes Workload Attestor 插件**。**这个插件先通过系统调用识别工作负载的 PID**。**然后它通过本地调用 Kubelet 来识别工作负载的 pod 名、image 及其他特征**。**这些特征可以用作注册条目中的 selector**。

### Kubernetes 自动注册条目

**一个叫做 Kubernetes Workload Registrar 的 SPIRE 扩展**可以**自动创建 Node 和 Workload 注册条目**——**在 Kubernetes API Server 和 SPIRE Server 之间充当桥梁**。**它支持多种识别运行中 pod 的方式**，**并且对它创建的条目有一定的灵活性**。

### 增加 side-car

**对那些还没改造去使用 Workload API 的工作负载**（参见第 7 章 Integration with Others 的 Native SPIFFE support 一节），**Kubernetes 让添加 side-car 变得很简单**。**一个 side-car 可以是 SPIFFE 感知的代理，比如 Envoy**。**另一种选择是 SPIRE 配套开发的一个叫做 "SPIFFE Helper" 的 side-car**——**它监控 Workload API，并在 SVID 变化时重新配置工作负载**。

> 图 6.11　k8s 集群中与 side-car 容器一起部署的工作负载（见 `assets/pages/page-120.png`）。

## SPIRE 性能考量

**当连接到 Server 的 SPIRE Agent 数量增长时，也会给 Server、数据存储、以及网络本身带来更多负载**。**多种因素会影响负载**，**包括每个节点的节点数和工作负载数、以及你轮换密钥的频率**。**在嵌套 SPIRE 模型下使用 JWT-SVID，**公钥需要保持同步**——这会增加 Agent 与 Server 之间需要传输的数据量**。

**我们不打算给出具体的性能要求或建议**——比如"每个 Agent 的工作负载数"或"每个 Server 的 Agent 数"——**因为所有这些数据 a) 取决于硬件和网络特征，b) 变化很快**。**举个例，最近一次发布就把数据性能提升了 30%**。

如你在前几章所学，**SPIRE Agent 会持续与 Server 通信，以获取任何新变化**——比如新工作负载的 SVID、或 trust bundle 的更新。**每次同步都会涉及多个数据存储操作**。**默认情况下，同步周期是 5 秒；如果它对系统造成的压力太大，你可以把它调高**。

**很短的 SVID TTL 能缓解安全风险**，**但如果你用非常短的 TTL，要做好准备——SPIRE Server 上的负载会增加，因为签发操作量与轮换频率成正比**。

另一个影响系统性能的关键因素是**每个节点上的工作负载数**。**如果你给系统中所有节点都加一个新工作负载，**那会突然产生一个尖峰，给整个系统带来负载**。

**如果你的系统重度依赖 JWT-SVID，请记住：JWT-SVID 不会在 Agent 端被提前生成，**必须按需签名**。**这会给 SPIRE Server 和 Agent 带来额外负载，并在过载时增加延迟**。

## 证明（Attestor）插件

**SPIRE 为节点证明和工作负载证明都提供了多种证明插件**。**用哪个证明插件，取决于证明的需求、以及底层基础设施/平台所能提供的支持**。

> 图 6.12　Node Attestor 架构与流程（见 `assets/pages/page-123.png`）。

**对工作负载证明来说，这在很大程度上取决于被编排的工作负载类型**。**比如，用 Kubernetes 集群时，Kubernetes 工作负载证明插件就是合适的**；**同理 OpenStack 平台就用 OpenStack Attestor**。

**对节点证明来说，重要的是确定安全与合规上的要求**。**有时会有"对工作负载做地理围栏"的要求**。**在这种场景下，使用能断言地理信息的云厂商的 Node Attestor，就能提供这些保证**。

**在强监管行业，可能要求使用基于硬件的证明**。**这些机制通常依赖底层基础设施提供支持**，比如 API 或硬件模块（Trusted Platform Module / TPM）。**这可以包括对系统软件状态的度量**——固件、内核版本、内核模块、乃至文件系统内容。

### 为不同云平台设计证明

**在云环境下，针对云厂商提供的元数据校验节点身份，被视为一种最佳实践**。**SPIRE 通过为你的云专门设计的自定义 Node Attestor，提供了一种简单的方式**。**大多数云厂商会分配一个 API，可用于识别 API 调用方**。

**针对 Amazon Web Services（AWS）、Azure、Google Cloud Platform（GCP）的 Node Attestor 和 Resolver 都已就绪**。**云环境下的 Node Attestor 是特定于该云的**。**Attestor 的目的是在给跑在该节点上的 SPIRE Agent 签发身份之前对节点进行证明**。

**身份一旦建立，SPIRE Server 上可能安装有 Resolver 插件——它允许基于节点的元数据创建额外的 selector**。**可用的元数据是云特定的**。

> **关键洞察**：另一个极端是，**如果云厂商没有提供对节点进行证明的能力，则可以用 join token 来 bootstrap**。**不过，这能提供的保证非常有限——具体取决于整个 join token 的产生与使用流程**。

## 注册条目的管理

**SPIRE Server 支持两种添加注册条目的方式**：**通过命令行接口**，或**通过 Registration API**（**只允许管理员访问**）。**SPIRE 需要注册条目才能工作**。**一种选择是让管理员手动创建它们**。

> 图 6.13　工作负载的手动注册（见 `assets/pages/page-124.png`）。

**在大型部署或基础设施快速增长时，手工流程撑不住**。**而且任何手工流程都容易出错、可能无法跟踪所有变更**。

> 图 6.14　用与"Workload Orchestrator"通信的 "Identity Operator" 自动创建工作负载注册条目的例子（见 `assets/pages/page-125.png`）。

**用自动化流程通过 SPIRE API 创建注册条目，对那些有大量注册条目的部署来说是更好的选择**。

## 把安全考量与威胁建模纳入设计

**你做的任何设计与架构决策，都会影响整个系统、甚至与之交互的其他系统的威胁模型**。

**下面是一些重要的安全考量、以及在设计阶段需要纳入的安全含义**。

### PKI 设计

**你的 PKI 是什么结构、你如何定义 Trust Domain 来建立安全边界、你的私钥放在哪里、轮换频率**——这些是**在这个阶段你需要问自己的关键问题**。

> 图 6.15　一个 SPIRE 部署示例：3 个 Trust Domain，每个使用不同的企业 CA，每个都使用同一个根 CA。**每一层证书都有更短的 TTL**（见 `assets/pages/page-126.png`）。

**每个组织会有不同的证书层次**——**因为每个组织有不同的需求**。**上面的图示代表的是一种可能的证书层次**。

### TTL、撤销与续期

**在做 PKI 时，证书过期、重新签发与撤销的问题总会被提起**。**几个考量会影响这里的决策**：

- **文档过期/重新签发的性能开销**——**能容忍多少性能开销**。**TTL 越短，性能开销越大**。
- **文档下发延迟**——**TTL 必须长于身份文档预期的下发延迟**，**以确保服务在认证自身时不会有空档**。
- **PKI 生态成熟度**——**有没有撤销机制？这些机制是否被维护并保持最新？**
- **组织的风险偏好**——**如果不启用撤销，当身份被攻破并被发现后，可接受的有效时间是多长**。
- **对象的预期寿命**——**基于对象的预期寿命，TTL 不应该设得太长**。

### 爆炸半径

**在 PKI 设计阶段，非常重要的一点是考虑：某个组件被攻破会如何影响其余的基础设施**。**比如，如果你的 SPIRE Server 把密钥放在内存里、且该 Server 被攻破，那么所有下游 SVID 就都需要被吊销和重新签发**。**为了最小化这种攻击的影响，你可以把 SPIRE 基础设施设计成针对不同网络段、VPC、或云厂商的多个 Trust Domain**。

### 私钥保密

**重要的是把密钥放在哪里**。**如你可能已经学过的，SPIRE 有一个 Key Manager 的概念，负责管理 CA 密钥**。**如果你打算把 SPIRE Server 作为 PKI 中的根，你可能想要持久化你的根密钥**——**但把它存在磁盘上不是一个好主意**。

**存放 SPIRE 密钥的一种方案**——**软件或硬件的 Key Management Service（KMS）**。**有作为 KMS 的独立产品、也有各大云厂商提供的内建服务**。

**另一种与现有 PKI 集成的可能设计策略**——**使用 SPIRE 的 Upstream Authority 插件接口**。**在这种情况下，SPIRE Server 通过"与一个现有 PKI 通信"（使用某个支持的插件）来签自己的中间 CA 证书**。

### SPIRE 数据存储的安全考量

**在第 4 章我们故意把 SPIRE Server 的数据存储从威胁模型中拿掉**。**数据存储是 SPIRE Server 持久化动态配置（比如注册条目、身份映射策略）的地方——这些动态配置是从 SPIRE Server API 写入的**。**SPIRE Server 数据存储支持多种数据库系统**。**数据存储被攻破会允许攻击者向任意节点注册工作负载、还可能包括节点本身**。**攻击者还能向 trust bundle 里加密钥、并切入下游基础设施的信任链**。

**攻击者的另一个可能的攻击面是**——**对数据库或 SPIRE Server 与数据库之间的连接做拒绝服务攻击**——**这会演变成对整个基础设施的拒绝服务**。

**在为产环境中的 SPIRE Server 基础设施设计任何数据库时，你大概率不会采用"数据库进程与 Server 共置在同一 host 上"的模型**。**虽然"对数据库的访问受限、且与 Server 共置"能显著缩小攻击面，但在产环境中它非常难以扩展**。

> 图 6.16　出于可用性与性能的考虑，SPIRE Server 数据存储通常通过远程网络连接跑在别处——**但这带来了一个安全挑战**（见 `assets/pages/page-129.png`）。

**出于可用性与性能的考虑，SPIRE 数据存储通常会是一份网络可达的数据库**。**但你应该考虑以下几点**：

- **如果这是一份与其他服务共享的数据库，谁还能访问它、谁在管理它**？
- **SPIRE Server 如何向数据库做认证**？
- **数据库连接是否支持 TLS 保护的安全通信**？

**这些都是必须考虑的相关问题——因为 SPIRE Server 与数据库的连接方式在很大程度上决定了整个部署的安全性**。**在使用 TLS 和基于密码的认证时，SPIRE Server 部署应当依赖一个秘密管理工具或 KMS 来保护数据安全**。

**在某些部署中，你可能需要再加一层更底层的 meta-PKI 基础设施**——**它能让你保护与 SPIRE Server 所有低层依赖之间的通信**，**包括你的配置管理或部署软件**。

### SPIRE Agent 的配置与 trust bundle

**在你的环境中如何分发和部署 SPIRE 生态的组件、以及它的配置**，**可能会对威胁模型和整个系统的安全模型产生严重后果**。**它是 SPIRE、也是你所有安全系统的低层依赖**——**所以这里我们只聚焦于 SPIFFE 和 SPIRE 特有的内容**。

#### Trust bundle

**有多种方式可以下发 Agent 的 bootstrap trust bundle**。**这是 Agent 启动时用于认证 SPIRE Server 的 trust bundle**。**如果攻击者能向初始 trust bundle 加密钥、并执行中间人攻击，那么对工作负载来说它也会执行同样的攻击——因为它们从受感染的 Agent 那里收到 SVID 和 trust bundle**。

#### 配置

**SPIRE Agent 的配置也需要保持安全**。**如果攻击者能修改这份配置文件，他们就能把它指向一个被攻破的 SPIRE Server，进而控制 Agent**。

#### 节点证明插件的影响

**通过多种独立机制断言信任，可以得到更强的信任断言**。**你选择的 Node Attestation 可能会显著影响你 SPIRE 部署的安全性、并将它的信任根转移到另一个系统**。**在决定使用哪种 Attestation 时，你应该把它纳入你的威胁模型，并在每次有变化时回顾一遍**。

**举例来说，任何其他"基于所有权证明（proof-of-possession）"的 Attestation 都会把信任根转移——所以你要确保"作为你更低层依赖的那个系统"满足你组织的安全和可用性标准**。

**当使用 join token 来设计一个 Attestation 模型时，**仔细评估"添加和使用 token 的运维流程"——**无论是运维人员手动操作，还是由配置系统自动完成**。

#### 遥测与健康检查

**SPIRE Server 和 Agent 都支持健康检查和多种类型的遥测**。**可能不那么明显的是——启用或错误配置健康检查与遥测，可能会扩大 SPIRE 基础设施的攻击面**。**SPIFFE 和 SPIRE 的威胁模型假设 Agent 只在本地 Unix socket 上暴露 Workload API 接口**。**模型没有考虑"配置错误（或故意配置成）健康检查服务不在 localhost 上监听"——这可能让 Agent 暴露在 DoS、RCE、内存泄露等潜在攻击之下**。**在选择遥测集成模型时也要做类似的小心——**因为某些遥测插件（比如 Prometheus）可能会暴露额外的端口**。

---

下一章：**第 7 章　与外部集成**
