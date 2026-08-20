---
title: "第 4 章　SPIFFE 与 SPIRE 概念入门"
description: "**Secure Production Identity Framework For Everyone（SPIFFE）** 是一组用于**软件身份**的开放标准。为了以\"组织无关、平台无关\"的方式获得可互操作的软件身份，SPIFFE 定义了一组接口和文档，用来以**完全自动化的方式**获取并验证加密身份。"
---
# 第 4 章　SPIFFE 与 SPIRE 概念入门

> 原书：*Chapter 4. Introduction to SPIFFE and SPIRE concepts*（p.52–77）
> 翻译策略：技术直译 + 段落重排；专有项目名、协议名、API 名、CLI 命令、配置字段、证书/加密术语一律保留英文；首次出现的关键概念以"中文（English）"形式给出，后续沿用英文。术语对照见 **`TERMS.md`**。

## 章节导言

> 本章在第 3 章的基础上，介绍 SPIFFE 这一标准本身。它会解释 SPIRE 实现的各个组件、以及它们如何组合起来。最后会讨论威胁模型，以及某个组件被入侵时会发生什么。

## 什么是 SPIFFE？

**Secure Production Identity Framework For Everyone（SPIFFE）** 是一组用于**软件身份**的开放标准。为了以"组织无关、平台无关"的方式获得可互操作的软件身份，SPIFFE 定义了一组接口和文档，用来以**完全自动化的方式**获取并验证加密身份。

SPIFFE 包含五个部分：

> 图 4.1　SPIFFE 的五个组成部分（见 `assets/pages/page-053.png`）。

- **SPIFFE ID**——如何表示一个软件服务的名字（即身份）。
- **SPIFFE Verifiable Identity Document（SVID）**——一种"密码学可验证的文档"，用来向对端证明服务的身份。
- **SPIFFE Workload API**——一种简单的"节点本地"API，让服务能获取自己的身份，**且不需要任何身份认证**。
- **SPIFFE Trust Bundle**——一种格式，用于表示"某个 SPIFFE 签发机构当前正在使用的公钥集合"。
- **SPIFFE Federation**——一种简单机制，用来在不同的 Trust Domain 之间共享 Trust Bundle。

### SPIFFE 不是什么

SPIFFE 的设计目标是**标识**服务器、服务、以及其他通过计算机网络进行通信的**非人类**实体。这些场景的共性是：身份必须**可自动签发**（无人在回路中）。虽然把 SPIFFE 用于标识人或野生动物物种是可能的，但项目特意把这些用例排除在范围之外。除了机器人和机器外，没有做其他的特殊考虑。

SPIFFE 把身份和相关的信息下发给服务、同时管理这些身份的生命周期。但它的角色仅限于"提供方"——它**不直接消费**所下发的身份。如何使用 SPIFFE 身份，是服务自身的责任。围绕"使用 SPIFFE 身份"有很多解决方案，可以启用认证层——比如端到端加密通信、服务对服务的授权与访问控制——但这些功能同样**不在 SPIFFE 项目的范围之内**，SPIFFE 不会直接解决它们。

### SPIFFE ID

**SPIFFE ID** 是一个字符串，充当服务的唯一名字。它被建模成一个 URI，由几部分组成：URI 的 scheme `spiffe://`、**信任域（Trust Domain）**的名字（作为 URI 的 host 段），以及具体工作负载的名字或身份（作为 URI 的 path 段）。

一个简单的 SPIFFE ID 可以长这样：

```
spiffe://example.com/myservice
```

> 图 4.2　一个 SPIFFE ID 及其组成（见 `assets/pages/page-054.png`）。

**SPIFFE ID 的第一个组件是 `spiffe://` URI scheme。** 虽然看似平淡，但加上它是个重要的细节：它把 SPIFFE ID 与 URL 或其他网络定位符区分开。

**第二个组件是 Trust Domain 名字**（`example.com`）。有些情况下，整个组织只有一个 Trust Domain；也有些时候需要多个 Trust Domain。Trust Domain 的语义本章稍后会展开。

**最后一个组件是工作负载自身的"名字部分"**，用 URI path 表示。**这部分 SPIFFE ID 的具体格式和组成是各站点自定义的**。组织可以自由选择最合理的命名方案。比如，可以选择同时反映"组织位置"与"工作负载用途"的命名方案：

```
spiffe://example.com/bizops/hr/taxrun/withholding
```

需要强调的是：**SPIFFE ID 的首要目的**是以一种"人机皆易消费"的方式灵活地表达工作负载身份。**要克制"试图在 SPIFFE ID 的格式里塞进过多含义"的冲动**。比如，试图把"后续要单独作为授权元数据使用的属性"硬编码进 SPIFFE ID，会带来互操作性和灵活性上的挑战。建议用一份**独立的数据库**（参考 [en.wiktionary.org/wiki/lookaside](https://en.wiktionary.org/wiki/lookaside)）来维护这些关系。

### SPIFFE Trust Domain

SPIFFE 规范引入了 **Trust Domain** 的概念。Trust Domain 用来**管理组织内部和组织之间的管理与安全边界**。每一个 SPIFFE ID 都内嵌了它所属的 Trust Domain 名字，如上所述。

具体来说，**一个 Trust Domain 是 SPIFFE ID 命名空间的一部分，在这一部分上"某组特定的公钥"被视为权威**。由于不同 Trust Domain 有不同的签发机构，**一个 Trust Domain 被攻破并不意味着另一个也被攻破**。这是一项重要的属性，它让"彼此并不完全信任"的双方能安全通信——比如 staging 和 production 之间，或者两家公司之间。

跨多个 Trust Domain 验证 SPIFFE 身份的能力，叫做 **SPIFFE Federation**，本章稍后会介绍。

### SPIFFE Verifiable Identity Document（SVID）

**SVID** 是一份"密码学可验证的身份文档"，用于向对端证明服务的身份。SVID 包含**一个** SPIFFE ID，并由代表该服务所在 Trust Domain 的"签发机构"签名。

SPIFFE 没有选择"发明一种新的文档类型、让所有软件去学着支持它"，而是**复用那些已经被广泛使用、且广为理解的文档类型**。在撰写本书时，SPIFFE 规范定义了两种可用作 SVID 的身份文档类型：**X.509** 和 **JWT**。

#### X509-SVID

**X509-SVID** 把 SPIFFE 身份编码到一张标准的 X.509 证书里（参考 [tools.ietf.org/html/rfc5280](https://tools.ietf.org/html/rfc5280)）。对应的 SPIFFE ID 被设为证书的 **SAN（Subject Alternative Name）扩展字段**中的 URI 类型。一张 X509-SVID 上只允许设置**一个** URI SAN 字段，但证书可以包含任意数量的其他类型 SAN 字段，包括 DNS SAN。

X509-SVID 是**被推荐在一切可能场景下使用**的形态，因为它比 JWT-SVID 拥有更好的安全属性。具体来说：与 TLS 一起使用时，X.509 证书不能被中间人录制并重放。

X509-SVID 的使用可能有额外要求，详情参见规范的 X509-SVID 部分（[github.com/spiffe/spiffe/blob/master/standards/...](https://github.com/spiffe/spiffe/blob/master/standards/X509-SVID.md)）。

#### JWT-SVID

**JWT-SVID** 把 SPIFFE 身份编码到一个标准 JWT 中（参考 [tools.ietf.org/html/rfc7519](https://tools.ietf.org/html/rfc7519)）——具体来说是一个 **JWS**（参考 [tools.ietf.org/html/rfc7515](https://tools.ietf.org/html/rfc7515)）。JWT-SVID 在应用层作为**持有者令牌（bearer token）**用于向对端证明身份。**与 X509-SVID 不同，JWT-SVID 存在一类名为"重放攻击"的威胁**（参考 [en.wikipedia.org/wiki/Replay_attack](https://en.wikipedia.org/wiki/Replay_attack)）——攻击者获取 token 后可以复用。

SPIFFE 强制要求三种机制来缓解这种威胁：

1. JWT-SVID **只能通过安全信道传输**。
2. 必须设置 `aud` 声明，**严格字符串匹配**到 token 的目标接收方。
3. 所有 JWT-SVID 必须包含**过期时间**，限制被盗 token 的有效窗口。

> **关键洞察**：即便有这些缓解措施，**JWT-SVID 仍然从根本上易受重放攻击**，必须谨慎使用、小心处理。但它们是 SPIFFE 规范集中重要的一部分——因为它们让 SPIFFE 身份认证能用于"无法建立端到端通信信道"的场景。

JWT-SVID 的使用可能有额外要求，详情参见规范的 JWT-SVID 部分（[github.com/spiffe/spiffe/blob/master/standards/...](https://github.com/spiffe/spiffe/blob/master/standards/JWT-SVID.md)）。

### SPIFFE Trust Bundle

**SPIFFE Trust Bundle** 是一份包含 Trust Domain 公钥的文档。每种 SVID 类型都有自己特定的表示形式（例如，X509-SVID 对应的是**代表那些公钥的 CA 证书**）。**每个 SPIFFE Trust Domain 都有一个与之关联的 Trust Bundle**，这份 bundle 里的材料被用来验证声称属于该 Trust Domain 的 SVID。

由于 Trust Bundle 不含任何秘密（只有公钥），可以安全地对外公开。但**它必须以一种安全的方式被分发**，以防内容被未授权篡改——也就是说，**保密性非必需，但完整性必需**。

SPIFFE bundle 用 **JWK Set（JWKS 文档）**格式化，与现有身份认证技术（比如 OpenID Connect，参考 [openid.net/connect](https://openid.net/connect/)）兼容。JWKS 是一种灵活、被广泛采用的格式，可表示各种类型的加密密钥和文档——这为"未来可能定义新的 SVID 格式"提供了前向兼容的能力。

### SPIFFE Federation

很多时候，你希望让位于**不同 Trust Domain** 的服务之间能安全通信。多数情况下，你并不能把所有服务都塞进同一个 Trust Domain。一个常见的例子是两家不同的公司需要相互通信；另一个例子是同一组织内需要建立安全边界——比如"不太可信的云环境"和"高度可信的本地服务"之间。

要做到这一点，**每个服务都必须持有对端所在 Trust Domain 的 bundle**。因此，SPIFFE Trust Domain 必须把自己的 bundle 内容暴露或共享出去，让"位于其它 Trust Domain 的服务"能验证"本 Trust Domain 的身份"。用来共享 Trust Domain bundle 内容的机制叫做 **bundle endpoint**。

Bundle endpoint 是一类简单的、受 TLS 保护的 HTTP 服务。希望与远端 Trust Domain 联邦的运维人员，需要在他们的 SPIFFE 实现里配置"远端 Trust Domain 的名字 + bundle endpoint 的 URL"，让 bundle 内容可以被定期拉取。

> 图 4.3　通过联邦连接两个不同 Trust Domain 的企业架构示意。**每个 SPIRE Server 只能为自己的 Trust Domain 签发 SVID**（见 `assets/pages/page-059.png`）。

### SPIFFE Workload API

**SPIFFE Workload API** 是一种**本地的、非网络的** API，工作负载用它来获取自己的当前身份文档、Trust Bundle 以及相关信息。**关键在于：这个 API 不需要认证**，不要求工作负载预先拥有任何凭证。

把这一能力以"本地 API"的形式提供，让 SPIFFE 实现可以**玩出各种花样**——用各种办法识别调用方，而无需直接认证（例如借助操作系统提供的能力）。Workload API 暴露为一个 gRPC server，使用**双向流（bi-directional stream）**，允许需要时把更新推送给工作负载。

Workload API 不要求调用方工作负载"了解自己的身份"或"调用 API 时拥有任何凭证"。这避免了"在工作负载旁边部署任何认证类秘密"的需求。

> 图 4.4　Workload API 提供信息与能力，让工作负载能利用 SPIFFE 身份（见 `assets/pages/page-060.png`）。

Workload API 把 SVID 与 Trust Bundle 投递给工作负载，并在必要时进行轮换。

## 什么是 SPIRE？

**SPIFFE Runtime Environment（SPIRE）** 是一套**生产就绪**的、SPIFFE 规范的完整开源实现。

> 图 4.5　SPIRE Agent 暴露 SPIFFE Workload API，并与 SPIRE Server 协作把身份签发给"调用 Agent 的"工作负载（见 `assets/pages/page-063.png`）。

SPIRE（以及 SPIFFE）项目由 **CNCF**（Cloud Native Computing Foundation，云原生计算基金会）托管。**CNCF** 由众多头部基础设施技术公司创立，为云原生社区的开源项目提供中立的主场。

SPIRE 有两个主要组件：**Server** 和 **Agent**。**Server** 负责认证 Agent、签发 SVID；**Agent** 负责对外提供 SPIFFE Workload API。两个组件都采用**插件化（plugin-oriented）**的架构编写，可以很方便地扩展以适配各种配置与平台。

### SPIRE 架构

SPIRE 的架构由两个关键组件组成：**SPIRE Server** 和 **SPIRE Agent**。

#### SPIRE Server

**SPIRE Server** 负责在 SPIFFE Trust Domain 内**管理并签发所有身份**。它使用一个**数据存储（Data Store）**来保存关于它的 Agent 和工作负载的信息等。**SPIRE Server 通过"注册条目（registration entry）"了解自己管理的工作负载**——"注册条目"是用于把 SPIFFE ID 赋给节点和工作负载的灵活规则。

Server 既可以通过 **API** 管理，也可以通过 **CLI 命令**管理。需要特别注意的是：**因为 Server 持有 SVID 签名密钥，它是关键的安全组件**。在决定其部署位置时需要特别考虑。本书稍后会展开讨论。

#### 数据存储

**SPIRE Server 使用一个数据存储**，记录当前的注册条目以及它所签发 SVID 的状态。当前支持多种 SQL 数据库。SPIRE 内置 **SQLite**——一种进程内嵌入式数据库——用于开发与测试。

#### Upstream Authorities

一个 Trust Domain 内的所有 SVID 都被 SPIRE Server 签名。默认情况下，SPIRE Server 会**生成一份自签名证书**（用自己随机生成的私钥签的证书）来签发 SVID，除非配置了一个叫做 **Upstream Certificate Authorities** 的插件接口。该接口允许 SPIRE 从**别的 CA**获取它的签名证书。

很多简单场景下，使用自签名证书是够用的。但对更大的部署，**借助既有 CA 和 X.509 证书的层次结构**来让多个 SPIRE Server（以及其它会生成 X.509 证书的软件）协同工作，是更可取的做法。

在某些组织里，**upstream CA** 可能是组织用于其他用途的"中央 CA"。当你的环境里使用多种不同的证书、并希望它们在整个基础设施范围内都被信任时，这就很有用。

#### SPIRE Agent

**SPIRE Agent 只有一个职能**——但这个职能非常关键——**提供 Workload API**。在完成这件事的过程中，它要解决若干关联问题：确定工作负载的身份、调用 Workload API、以及安全地"自报家门"给 SPIRE Server。**所有重活都由 Agent 干**。

> 注：原文 "securely introducing itself to the SPIRE Server"，"introducing" 译为"自报家门"略口语化，更正式可译为"安全地向 SPIRE Server 完成自我证明"。这里保留口语化版本以贴合原文语气。

> 图 4.6　SPIRE 支持的关键插件接口。Server 端有 Node Attestor、KeyManager、Upstream Authority 三类插件；Agent 端有 Node Attestor 和 Workload Attestor 两类插件（见 `assets/pages/page-064.png`）。

Agent 不像 SPIRE Server 那样需要主动管理。它虽然需要一份配置文件，但**关于本地 Trust Domain 和可能调用它的工作负载的信息，直接由 SPIRE Server 推过来**。当你在某个 Trust Domain 中定义新工作负载时，**只需在 SPIRE Server 中创建或更新记录**，关于新工作负载的信息就会自动下发到对应的 Agent。

#### 插件架构

SPIRE 是以**一组插件**的形式构建的，这样可以很方便地扩展以容纳新的 Node Attestor、Workload Attestor、Upstream Authority。

#### SVID 管理

SPIRE Agent 用它在 Node Attestation 阶段获得的身份，去 SPIRE Server 完成认证，然后为它被授权管理的工作负载获取 SVID。由于 SVID 是**有期限**的，Agent 还负责按需续期 SVID、并把更新传达给相关工作负载。Trust Bundle 也会轮换，Agent 负责跟踪这些更新并传达给工作负载。Agent 在内存中维护所有这些信息的缓存——**即便 SPIRE Server 宕机，SVID 也能被提供**；同时也保证 Workload API 的响应足够快，无需在每次被调用时都回源到 Server。

### 证明（Attestation）

**证明（Attestation）**是一个**发现并断言**"关于工作负载及其环境的信息"的过程。换句话说，**它是用可获得的信息作为证据、以确定性方式证明工作负载身份的过程**。

SPIRE 中有两种证明：**Node Attestation** 和 **Workload Attestation**。**Node Attestation** 断言"描述节点"的那类属性（例如属于哪个 AWS Auto Scaling Group，或位于哪个 Azure region）；**Workload Attestation** 断言"描述工作负载"的属性（例如它所运行的 Kubernetes Service Account，或磁盘上 binary 的路径）。这些属性在 SPIRE 中的表示叫做 **selector**。

SPIRE 开箱支持几十种 selector 类型，而且还在增长。截至本书撰写时，Node Attestor 已经支持：裸金属、Kubernetes、Amazon Web Services、Google Cloud Platform、Azure 等。Workload Attestor 已经支持：Docker、Kubernetes、Unix 等。

此外，SPIRE 的**可插拔架构**允许运维轻松扩展系统，按需支持额外的 selector 类型。

#### Node Attestation

**Node Attestation 发生在 Agent 第一次启动时**。Node Attestation 中，Agent 联系 SPIRE Server，双方进入一个交换过程——**Server 目标是确定地把 Agent 所在节点、以及与之相关的所有 selector 都识别出来**。要做到这一点，Agent 端和 Server 端都会跑一个**特定平台**的插件。举例来说，在 AWS 场景下：

- **Agent 端插件**收集"只有该节点能拿到"的 AWS 信息（一份由 AWS 密钥签名的 document），并把它传给 Server。
- **Server 端插件**校验 AWS 签名、并继续调用 AWS API 来核验该声明的准确性，同时收集关于该节点的额外 selector。

> 图 4.7　运行在 AWS 上的节点的 Node Attestation（见 `assets/pages/page-066.png`）。
>
> 1. Agent 通过调用 AWS API 收集节点身份的证据。
> 2. Agent 把这份身份证据发给 Server。
> 3. Server 通过回调 AWS API 验证第 2 步拿到的证据，然后为 Agent 创建一份 SPIFFE ID。

**Node Attestation 成功**后，会把身份签发给该 Agent。**之后 Agent 用该身份与 Server 进行所有通信**。

#### Workload Attestation

**Workload Attestation** 是**确定工作负载身份**的过程——该身份最终会作为身份文档被签发并下发。**每次工作负载调用、与 SPIFFE Workload API 建立连接时（也就是工作负载对 API 的每一次 RPC），都会发生证明**。后续流程由 **SPIRE Agent 上的一组插件**驱动。

> 图 4.8　Workload Attestation（见 `assets/pages/page-068.png`）。
>
> 1. 工作负载调用 Workload API 请求一份 SVID。
> 2. Agent 查询节点的 kernel，拿到调用进程的属性。
> 3. Agent 拿到被发现的 selector。
> 4. Agent 通过比对"已发现的 selector"与"注册条目"，确定工作负载的身份，把正确的 SVID 返回给工作负载。

当 Agent 收到来自调用方工作负载的新连接时，Agent 会**利用操作系统的能力**，确定"是哪个进程打开了新连接"。**用到的操作系统能力取决于 Agent 跑在哪个 OS 上**。在 Linux 上，Agent 会做一次系统调用，拿到**进程 ID、用户 ID、以及调用本 socket 的远端系统的全局唯一标识**。在 BSD 和 Windows 上，请求的 kernel 元数据会不同。Agent 会把"调用方工作负载的 ID"提供给各 Attestor 插件。从那里开始，证明流程会**通过这些插件扇出**，提供关于调用方的额外进程信息，并以 selector 的形式返回给 Agent。

**每个 Attestor 插件负责"自省调用方"，并生成描述它的一组 selector**。例如：

- 一个插件可能看 kernel 层细节，生成诸如"该进程以哪个 user、哪个 group 跑"这类 selector；
- 另一个插件可能与 Kubernetes 通信，生成诸如"该进程跑在哪个 namespace、哪个 service account"这类 selector；
- 第三个插件可能与 Docker daemon 通信，生成诸如 Docker image ID、Docker labels、container env vars 这类 selector。

> **关键洞察**：如果某个 selector 的值可以由工作负载自己操纵，那么这个 selector 天然就不安全——这是 Workload Attestation 设计上一个至关重要的细节。

#### 注册条目（Registration Entry）

要让 SPIRE 签发工作负载身份，必须先告诉它"自己的环境里有哪些预期/被允许的工作负载"：哪些工作负载应该跑在哪里、它们的 SPIFFE ID 应该是什么、大致形态如何。**SPIRE 通过"注册条目"来学习这些信息**——注册条目是用 SPIRE API 创建和管理的对象，里面就装着上述信息。

> 图 4.9　注册条目的三大核心属性（见 `assets/pages/page-069.png`）。

每个注册条目有三个核心属性：

1. **Parent ID**——告诉 SPIRE"这个特定工作负载应该跑在哪里"（延伸开来，就是"哪些 Agent 有权代表它去申请 SVID"）。
2. **SPIFFE ID**——当我们看到这个工作负载时，应该签给它哪份 SPIFFE ID。
3. **Selector**——SPIRE 需要某种信息来识别工作负载，这正是从证明中拿到的 selector。

**注册条目把 SPIFFE ID 绑定到"它要代表的"节点和工作负载上**。一个注册条目可以描述**一组节点**或**一个工作负载**；后者通常通过 Parent ID 引用前者。

#### Node 条目

**描述节点（或一组节点）的注册条目**使用由 Node Attestation 生成的 selector 来分配 SPIFFE ID——这些 ID 在后续注册工作负载时可以被引用。**一个节点可以被证明为"匹配多个 Node 条目"的一组 selector**，让它能参与多个分组。**这在决定"某个工作负载被允许跑在哪里"这件事上提供了极大的灵活性**。

SPIRE 自带多种开箱即用的 Node Attestor，每种都生成平台相关的 selector。**虽然 SPIRE Server 一次可以加载多个 Node Attestor 插件，但 SPIRE Agent 一次只能加载一个**。可用 Node selector 的一些例子：

- 在 **Google Cloud Platform（GCP）**上……
- 在 **Kubernetes** 上，是节点所属 Kubernetes 集群的名字
- 在 **Amazon Web Services（AWS）**上，是节点的 AWS Security Group

**Node 条目把 Parent ID 设为 SPIRE Server 的 SPIFFE ID**——因为执行证明、并断言"该节点确实匹配条目所定义 selector"的是 Server。

#### Workload 条目

**描述工作负载的注册条目**使用由 Workload Attestation 生成的 selector，当某些条件被满足时，为工作负载分配 SPIFFE ID。**当 Parent ID 和 selector 条件都满足时，工作负载才能拿到 SPIFFE ID**。

**Workload 条目的 Parent ID 描述"这个工作负载被授权跑在哪里"**。其值是某个节点或某组节点的 SPIFFE ID。**跑在这些节点上的 SPIRE Agent 会拿到这条 Workload 条目的副本**，里面包括"在为该条目签发 SVID 之前必须证明"的 selector。

当一个工作负载调用 Agent 时，Agent 执行 Workload Attestation，**把"已发现的 selector"与"条目中定义的 selector"做交叉比对**。如果工作负载持有"已定义 selector 的全部集合"，那么条件就满足——给该工作负载签发一份带有所定义 SPIFFE ID 的 SVID。

与 Node Attestation 不同，**SPIRE Agent 一次可以加载多个 Workload Attestor 插件**。这允许在 Workload 条目里"混搭"多种 selector。例如，一个 Workload 条目可以要求工作负载处于"某个 Kubernetes 命名空间、其 Docker 镜像上带某个特定 label、且某个特定 SHA 校验和匹配"。

## SPIFFE / SPIRE 应用概念 · 威胁模型

**SPIFFE / SPIRE 面临的具体威胁集合是因场景而异的**。理解 SPIFFE / SPIRE 的一般威胁模型是重要的——它能帮你判断"自己的具体需求是否可以被满足"，以及"哪里还需要进一步加固"。

本节会描述 SPIFFE 和 SPIRE 的**安全边界**以及**系统中每个组件被入侵的影响**。本书稍后会覆盖**不同 SPIRE 部署模型带来的具体安全考量**。

### 假设

SPIFFE 和 SPIRE 旨在成为**分布式身份与认证的基石**——这种身份与认证与云原生（参考 [github.com/cncf/toc/blob/master/DEFINITION.md](https://github.com/cncf/toc/blob/master/DEFINITION.md)）设计架构一致。SPIRE 支持 **Linux 和 BSD 系列**（包括 macOS）。**目前不支持 Windows**，不过在该方向上已有一些早期原型。

> 图 4.10　威胁模型中纳入考虑的组件（见 `assets/pages/page-073.png`）。

SPIRE 遵循**零信任网络（zero trust networking）**安全模型，**假设网络通信是有敌意的、或已被完全攻破**。**同时假设 SPIRE 组件运行所在硬件、及其运维人员是可信的**。如果硬件植入物（hardware implant）或内部威胁被纳入威胁模型，则需要**围绕 SPIRE Server 的物理部署位置、其配置参数的安全性做更细致的考量**。

根据所选的"节点和工作负载证明"方式，可能还会**隐含信任第三方平台或软件**。**借助多种独立机制去断言信任，能提供更强的信任断言**。举例来说：使用 AWS 或 GCP 的 Node Attestation 隐含了"假定计算平台是可信的"；使用 Kubernetes 做 Workload Attestation 隐含了"假定 Kubernetes 部署是可信的"。由于证明的达成方式多种多样、且 SPIRE 架构完全可插拔，这些流程的安全性（以及相关假设）**不在本评估范围内**。它们应该按**具体场景**逐一评估。

> 图 4.11　SPIFFE / SPIRE 的安全边界（见 `assets/pages/page-074.png`）。

### 安全边界

**安全边界（security boundary）** 在形式上被理解为**两个不同信任水平区域的交线**。

SPIFFE / SPIRE 定义了**三个主要的安全边界**：

1. **工作负载与 Agent 之间**；
2. **Agent 与 Server 之间**；
3. **不同 Trust Domain 的 Server 之间**。

在这个模型中，**工作负载是完全不可信的**，其他 Trust Domain 里的 Server 也是如此；并且如前所述，**网络通信永远是完完全全不可信的**。

#### 工作负载 | Agent 边界

随着我们在系统中移动、跨越这些边界，信任水平**逐步提升**。从工作负载开始，我们跨越一条安全边界到达 Agent。**通常期望（虽然不是强制的）**在工作负载和 Agent 之间存在**超越 SPIRE 设计本身**的安全机制——例如借助 Linux user 权限、容器化等。

**Agent 不信任工作负载给出任何形式的输入**。Agent 关于"工作负载身份"的所有断言，都通过**带外（out-of-band）**的检查完成。在 Workload Attestation 语境下，这是一个重要细节——**任何值可以被工作负载自己操纵的 selector，本质上都是不安全的**。

#### Agent | Server 边界

下一条边界存在于 **Agent 和 Server 之间**。**Agent 比工作负载更可信、但比 Server 更不可信**。SPIRE 的一个明确设计目标是：**它必须能在节点被攻破的情况下存活**。既然工作负载完全不可信，我们距离"节点被攻破"这种状态可能只有一次、两次攻击的距离。**Agent 有能力代表工作负载创建并管理身份**，但同时必须**按照最小权限原则，把每个 Agent 的能力限制在"完成它任务所必需"的最小范围**。

为缓解"节点（及 Agent）被攻破"的影响，**SPIRE 要求掌握"某个特定工作负载被授权跑在哪里"（以 Parent ID 的形式）**。**Agent 必须先证明它对某条注册条目的所有权，才能为它申请身份**。这样一来，**被攻破的 Agent 也无法获取任意身份**——它们**只能**为"本来就该跑在这个节点上的"工作负载获取身份。

值得注意：**SPIRE Server 与 SPIRE Agent 之间的通信**可以在不同时机使用 TLS 或 mTLS——这取决于**该节点是否已经完成证明**，或**该 Agent 是否已经拥有合法 SVID、并能用它进行 mTLS**。一旦到了后一种情况，**Server 和 Agent 之间的所有通信都是安全的**。

#### Server | Server 边界

最后一条边界存在于**不同 Trust Domain 的 Server 之间**。**SPIRE Server 仅被信任在自己直接管理的 Trust Domain 内签发 SVID**。当 SPIRE Server 之间相互联邦、交换公钥信息时，它们所收到的密钥**仍然被限制在"它们来自的那个" Trust Domain 范围内**。与 Web PKI 不同，**SPIFFE 不会简单地把所有公钥一股脑塞进一个混合的袋子里**。结果是：**某个外部 Trust Domain 被攻破，并不会让攻击者能在本地 Trust Domain 内签发 SVID**。

需要指出：**SPIRE Server 之间没有"多方共防"的保护**。**Trust Domain 内的每个 SPIRE Server 都拥有能签发 SVID 的签名密钥**。**Server 之间的安全边界仅限于"不同 Trust Domain 的 Server 之间"**，**并不适用于"同一 Trust Domain 内的 Server"**。

### 组件被攻破的影响

虽然工作负载始终被认为是"被攻破的"，但通常期望 Agent 一般不是。**如果 Agent 被攻破，攻击者将能访问"该 Agent 被授权管理的所有身份"**。在"一个工作负载对应一个 Agent"的部署中，这事不必太担心；在"一个 Agent 管理多个工作负载"的部署中，这一点必须理解清楚。

Agent 在被某条注册条目"作为 parent 引用"时，就获得了管理该身份的能力。**鉴于此，**把注册条目的 Parent ID 范围**尽量收紧**是好的实践。

一旦 Server 被攻破，可以预期攻击者**将在该 Trust Domain 内签发任意身份**。**SPIRE Server 毫无疑问是整个系统最敏感的组件**。对 Server 的管理与部署位置需要格外小心。例如，**SPIRE 之所以能应对节点被攻破的场景，前提是工作负载不可信；但如果 SPIRE Server 跑在与这些不可信工作负载同一台宿主上，那么 Server 就享受不到"Agent/Server 安全边界"曾经提供的保护**。因此，**强烈建议把 SPIRE Server 部署在与"它要管理的不可信工作负载"不同的硬件上**。

### Agent 注意事项

**SPIRE 通过把 Agent 的权限限制在"它直接被授权管理的身份"上来应对节点被攻破的场景**——但**如果攻击者能攻破多个 Agent，甚至所有 Agent**呢？情况会糟糕得多。

**SPIRE Agent 之间没有任何通信通路**，这显著限制了"Agent 之间横向移动"的可能性。这是一个重要的设计决策，目的是缓解"Agent 漏洞可能带来的影响"。**但要理解，某些配置或部署选择可能会部分、甚至完全破坏这种缓解**。举例来说，SPIRE Agent 支持暴露一个 **Prometheus metrics 端点**；**如果所有 Agent 都暴露该端点、且该端点存在漏洞，那么横向移动就会变得轻而易举**——除非你部署了充分的网络层控制。**鉴于此，强烈不建议把 SPIRE Agent 暴露给入站网络连接**。

---

下一章：**第 5 章　动手之前**
