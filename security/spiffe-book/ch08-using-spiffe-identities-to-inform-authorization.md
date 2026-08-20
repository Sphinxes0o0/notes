---
title: "第 8 章　用 SPIFFE 身份驱动授权"
description: "**SPIFFE 聚焦于\"为软件签发可互操作的、安全的加密身份\"——但如本书之前所述，它不直接解决\"使用或消费这些身份\"的问题**。"
---
# 第 8 章　用 SPIFFE 身份驱动授权

> 原书：*Chapter 8. Using SPIFFE Identities to Inform Authorization*（p.146–158）
> 翻译策略：技术直译 + 段落重排；专有项目名、协议名、API 名、CLI 命令、配置字段、证书/加密术语一律保留英文；首次出现的关键概念以"中文（English）"形式给出，后续沿用英文。术语对照见 **`TERMS.md`**。

## 章节导言

> 本章解释如何用 SPIFFE 身份来实现授权策略。

## 在 SPIFFE 之上构建授权

**SPIFFE 聚焦于"为软件签发可互操作的、安全的加密身份"——但如本书之前所述，它不直接解决"使用或消费这些身份"的问题**。

**SPIFFE 经常作为一个强授权系统的基石，SPIFFE ID 本身在这一图景中扮演了重要角色**。**本节我们讨论用 SPIFFE 来构建授权的若干选项**。

## 认证 vs 授权（AuthN vs AuthZ）

**一旦工作负载拥有了一个安全的加密身份，它就可以向其他服务证明自己的身份**。**向外部服务证明身份叫做认证（authentication）**。**认证之后，该服务就可以选择允许哪些动作**。**这个过程叫做授权（authorization）**。

**在一些系统中，任何能认证的实体也就被授权了**。**由于 SPIFFE 在服务启动时会自动为它签发身份，所以非常重要的一点是要清楚理解：并不是每一个能认证自身的实体都应该被授权**。

## 授权类型

**授权的建模方式有很多**。**最简单的方案是：为每个资源附带一份"已授权身份"的白名单**。**然而，当我们继续探索时，会发现这种"白名单"方式在面对"生态的规模与复杂度"时存在一些局限**。**我们将看两种更复杂的模型——RBAC（基于角色的访问控制）和 ABAC（基于属性的访问控制）**。

### 白名单

**在小型生态中、或者刚开始用 SPIFFE / SPIRE 时，有时最好的办法是保持简单**。**举例来说，如果你的生态里只有十几个身份，每个资源（即服务、数据库）的访问都可以通过维护一份"拥有访问权的身份"列表来管理**：

```bash
ghostunnel server --allow-uri spiffe://example.com/blog/web
```

**这里，ghostunnel server 显式地仅基于客户端身份授权访问**。

**这种模型的优点是容易理解**。**只要你的身份数量有限、且不变，那么在资源上定义和更新访问控制是很容易的**。**然而，可扩展性会成为障碍**。**如果一个组织有几百、几千个身份，维护白名单很快就会变得不可管理**。**比如，每加一个新服务，都可能要求运维团队去更新许多白名单**。

### 基于角色的访问控制（RBAC）

**在 RBAC 中，服务被分配到角色，然后基于角色来指定访问控制**。**这样一来，当新服务被加入时，只需要去编辑相对小的一组角色**。

**虽然可以把服务的角色编码进它的 SPIFFE ID，但这通常是一种糟糕的做法——因为 SPIFFE ID 是静态的，而它所被分配的角色可能不得不变**。**更佳的做法是：使用一个外部的、SPIFFE ID 到角色的映射**。

### 基于属性的访问控制（ABAC）

**ABAC 是一种"基于与服务关联的属性来做出授权决策"的模型**。**与 RBAC 一起，ABAC 可以成为强化授权策略的强力工具**。**举例来说，为满足法律要求，可能有必要把对数据库的访问限制在"来自某个特定 region 的服务"**。**region 信息可以作为 ABAC 模型中的一项属性——用于授权、并被编码进 SPIFFE ID 方案**。

## 为授权设计 SPIFFE ID 方案

**SPIFFE 规范没有指定或限制你可以或应该在 SPIFFE ID 中编码什么信息**。**你唯一需要注意的限制来自：SAN 扩展的最大长度、以及允许使用的字符**。

### 警告

> **在把授权元数据编码进你组织的 SPIFFE ID 格式时，请格外小心**。**下面的例子只是为了演示怎么做，因为我们不想在这里引入额外的授权概念**。

### SPIFFE 方案示例

**要在 SPIFFE 身份子串上做授权决策，我们必须定义身份的每一部分代表什么**。**你可以按位置顺序来设计你的方案，把信息编码到顺序中**。**在这种情况下，第一部分可能代表 region，第二部分代表环境，以此类推**。

下面是方案与身份的一个示例：

```
spiffe://trust.domain.org/<region>/<dev,stage,prod>/<organization>/<workload name>
```

> 图 8.1　SPIFFE ID 的组成以及某组织中各部分可能的含义（见 `assets/pages/page-150.png`）。

> 图 8.2　另一种潜在 SPIFFE ID 方案的示意（见 `assets/pages/page-151.png`）。

**身份方案不仅可以采取"一连串固定字段"的形态，也可以根据组织需要采取更复杂的结构**。**一个常见的例子是：跨不同编排系统的工作负载身份**。**举例来说，Kubernetes 和 OpenShift 的工作负载命名约定是不同的**。**下图以示例形式展示了这一点**。**你可能注意到：字段不仅引用不同的属性和对象，而且 SPIFFE ID 的结构也依赖于上下文**。**消费者可以通过观察身份的前缀来区分方案的结构**。**例如，**一个以 `spiffe://trust.domain.org/Kubernetes/…` 为前缀的身份会按下方图中的方案结构被解析为 Kubernetes 身份**。

### 变更方案

**组织几乎一定会变化，身份方案的需求也会随之变化**。**这可能是因为组织架构重组、或者技术栈迁移**。**几年后你的环境会变成什么样，可能很难预测**。**因此，在设计 SPIFFE ID 方案时，**去考虑未来可能的变化、以及这些变化会如何影响"基于 SPIFFE 身份的其他系统"是至关重要的**。**你应该思考如何把向后兼容与向前兼容纳入方案设计**。**如我们之前提到的，对"有序"方案来说，你只需要在 SPIFFE ID 末尾添加新实体；**但如果你需要往中间插入东西呢**？

**一种方法是基于 key-value 对的方案，另一种方法是我们都很熟悉的东西——版本号**。

#### 基于 key-value 对的方案

**我们注意到上面的方案设计都是有序的**——**通过看身份的前缀、并确定如何评估其后缀来评估这个方案**。**然而，**由于这种有序性，向方案中新增字段是困难的**。**key-value 对按其本性是无序的，这是一种不用大改就能向身份方案中扩展字段的方法**。**举例来说，你可以用 key-value 对加上一个已知分隔符——比如冒号 `:` 字符**。**在这种情况下，上面的身份可以被编码为下面的样子**：

```
spiffe://trust.domain.org/environment:dev/region:us/organization:zero/name:turtle
```

**由于身份的消费者会把它处理为一组 key-value 对，**更多的 key 可以被加入而无需改变方案的底层结构**。**也存在一种可能性：SPIFFE 在未来支持把 key-value 对纳入 SVID**。

> **关键洞察**：**一如既往，结构化与非结构化数据类型之间的权衡是需要考虑的**。

#### 版本号

**一种可能的解决方案是：把版本号纳入方案**。**版本可以是第一项，也是方案中最关键的部分**。**其他系统需要在处理 SPIFFE ID 数据时遵循"版本与编码实体之间的映射"**。

```
spiffe://trust.domain.org/v1/region/environment/organization/workload
```

**v1 方案**：
- 0 = version
- 1 = region
- 2 = environment
- 3 = organization
- 4 = workload

```
spiffe://trust.domain.org/v2/region/datacenter/environment/organization/workload
```

**v2 方案**：
- 0 = version
- 1 = region
- 2 = datacenter
- 3 = environment
- 4 = organization
- 5 = workload

**在 SPIFFE 中，单个工作负载可以拥有多个身份**。**然而，由工作负载自己决定使用哪个身份**。**为了保持授权简单，最佳做法是：先给每个工作负载一个身份，按需再增加**。

## 授权示例：HashiCorp Vault

**我们用一个工作负载可能希望与之通信的服务（HashiCorp Vault）作为例子过一遍**。**我们会分别看一个 RBAC 和一个 ABAC 的例子，**并讨论一些在用 SPIFFE / SPIRE 做授权时会遇到的坑和考量**。

**Vault 是一个秘密仓库**：**管理员可以用它安全地存储服务可能需要的密码、API key、私钥等秘密**。**由于许多组织即使在用 SPIFFE 提供安全身份之后，仍然需要安全地存储秘密——用 SPIFFE 访问 Vault 是一个常见诉求**。

```
spiffe://example.org/<region>/<dev,stage,prod>/<organization>/<workload name>
```

### 为 SPIFFE 身份配置 Vault

**Vault 在处理客户端请求时承担认证与授权两类任务**。**像其他许多管理资源（这里指 secret）的应用一样，它有一个可插拔接口，能接入多种身份认证与授权机制**。

**在 Vault 中，这通过 TLS Certificate Auth Method（参考 [www.vaultproject.io/api/auth/cert](https://www.vaultproject.io/api/auth/cert)）或 JWT/OIDC Auth Method（参考 [www.vaultproject.io/api-docs/auth/jwt](https://www.vaultproject.io/api-docs/auth/jwt)）实现——**这些可以被配置为识别并验证 SPIFFE 生成的 JWT 和 X509-SVID**。

**要让 Vault 启用 SPIFFE 身份，需要把这些可插拔接口配上 trust bundle——以便它能认证 SVID**。

**这就搞定了认证，但我们还需要配置它来执行授权**。**要做到这一点，需要为 Vault 部署一套授权规则——让它决定哪些身份可以访问秘密**。

### 一个 SPIFFE RBAC 示例

**在下面的例子中，我们假设使用 X509-SVID**。**Vault 允许创建规则，这些规则可以表达"哪些身份可以访问哪些秘密"**。**这通常包括：创建一组访问权限、以及创建一条把这些权限与访问绑定的规则**。

**例如，一条简单的 RBAC 策略**：

```json
{
  "display_name": "medical-access-role",
  "allowed_common_names": [
    "spiffe://example.org/eu-de/prod/medical/data-proc-1",
    "spiffe://example.org/eu-de/prod/medical/data-proc-2"
  ],
  "token_policies": "medical-use",
}
```

**这条规则编码的语义是**：**如果一个客户端的身份是 `spiffe://example.org/eu-de/prod/medical/data-proc-1` 或 `spiffe://example.org/eu-de/prod/medical/data-proc-2`，它就能获得一组权限（"medical-use"），进而获得对医疗数据的访问**。

**在这个场景下，我们让这两个身份能够访问这个 secret**。**Vault 负责把两个不同的 SPIFFE ID 映射到同一套访问控制策略——这让它更接近 RBAC、而不是简单的白名单**。

### 一个 SPIFFE ABAC 示例

**在某些情况下，按属性（而不是按角色）来设计授权策略更简单**。**通常当存在多组不同的属性、且每一组都可能单独命中策略，**而要造出足够多的唯一角色来匹配每种情况又很困难时，就需要这么做**。

**沿着上面那个例子，我们可以创建一条策略，授权具有某个 SPIFFE ID 前缀的工作负载**：

```json
{
  ...
  "display_name": "medical-access-role",
  "allowed_common_names": [
    "spiffe://example.org/eu/prod/medical/batch-job*"
  ],
  "token_policies": "medical-use",
}
```

**这条策略声明**：**所有以 `spiffe://example.org/eu/prod/medical/batch-job` 为前缀的工作负载都被授权访问该 secret**。**这可能是有用的——因为批处理作业是临时性的，可能会被赋予一个随机分配的后缀**。

**另一个例子是下面这样的策略**：

```json
{
  ...
  "display_name": "medical-access-role",
  "allowed_common_names": [
    "spiffe://example.org/eu-*/prod/medical/data-proc"
  ],
  "token_policies": "medical-use",
}
```

**这条策略想要达到的效果是**：**只有"任意 EU 数据中心里的 data-proc 工作负载"才能访问这个医疗 secret**。**因此，如果一个新工作负载在 EU 内的某个新数据中心启动，任何 data-proc 工作负载都将被授权访问医疗 secret**。

### Open Policy Agent

**Open Policy Agent（OPA）** 是 **CNCF（Cloud Native Computing Foundation）** 的一个项目，用于执行高级授权。**它使用一种叫做 Rego 的领域特定语言，高效地评估传入请求的属性、并确定它应当被允许访问哪些资源**。**使用 Rego，可以设计出精细的授权策略与规则——包括 ABAC 与 RBAC**。**它还能把"与 SPIFFE 无关的"连接属性考虑进来，比如传入请求的 user ID**。**Rego 策略存储在文本文件中，**因此可以通过 CI 系统集中维护和部署，**甚至能进行单元测试**。

下面是一个示例——它把"对某个数据库服务的访问"编码为"只有某个 SPIFFE ID 才被允许"：

```rego
# allow Backend service to access DB service
allow {
  http_request.path == "/good/db"
  http_request.method == "GET"
  svc_spiffe_id == "spiffe://domain.test/eu-du/backend-server"
}
```

**如果需要更精细的授权策略，OPA 是一个很好的选择**。**Envoy 代理同时集成了 SPIRE 和 OPA，所以无需修改服务代码就能立即上手**。**要了解更多关于"使用 OPA 做授权"的细节，请查阅 OPA 文档**。

## 小结

**授权本身就是一个庞大而复杂的话题，远超本书的范围**。**然而，与"和身份打交道的生态"中许多其他方面一样，理解身份与授权（以及更广泛的策略）的关系很有用**。

**本章我们介绍了多种用 SPIFFE 身份思考授权的方式，以及与身份相关的若干设计考量**。**这会帮助你更好地去设计你的身份方案——以满足组织在授权与策略上的需求**。

---

下一章：**第 9 章　与其他安全技术的对比**
