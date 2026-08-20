---
title: "术语对照表（TERMS.md）"
description: "本书翻译中使用的关键术语对照。**首次出现时**采用\"中文（English）\"格式，后续章节内沿用英文术语不再重复中文。"
---
# 术语对照表（TERMS.md）

本书翻译中使用的关键术语对照。**首次出现时**采用"中文（English）"格式，后续章节内沿用英文术语不再重复中文。

> 规则：专有项目名、协议名、组件名、API 名、CLI 命令、配置字段、证书 / 加密术语**一律保留英文**。
> 仅对"概念类别"提供中文译名，方便母语阅读。

## 项目 / 协议 / 标准

| 中文 | English | 说明 |
|---|---|---|
| SPIFFE | SPIFFE | Secure Production Identity Framework For Everyone，工作负载身份标准 |
| SPIRE | SPIRE | SPIFFE Runtime Environment，SPIFFE 的参考实现 |
| 零信任 | Zero Trust | 整体安全模型，封面 Zero the Turtle 即此意 |
| 云原生计算基金会 | CNCF | Cloud Native Computing Foundation |
| TLS | TLS | Transport Layer Security，传输层安全 |
| mTLS | mTLS | mutual TLS，双向 TLS |
| X.509 | X.509 | 证书标准 |
| JWT | JWT | JSON Web Token |
| JWKS | JWKS | JSON Web Key Set |
| JWS | JWS | JSON Web Signature |
| JWE | JWE | JSON Web Encryption |
| OIDC | OIDC | OpenID Connect |
| OAuth | OAuth | OAuth 授权框架 |
| PKI | PKI | Public Key Infrastructure，公钥基础设施 |
| WIMSE | WIMSE | Workload Identity in Multi System Environments，IETF 工作组 |

## 核心 SPIFFE / SPIRE 概念

| 中文 | English | 说明 |
|---|---|---|
| 工作负载 | Workload | 通常指一个运行中的服务进程；是 SPIFFE 标识的发放对象 |
| 工作负载身份 | Workload Identity | 赋予工作负载的加密身份 |
| 信任域 | Trust Domain | Trust Domain，共享同一套信任根的边界，写作 `spiffe://trust-domain/...` |
| SPIFFE ID | SPIFFE ID | 工作负载的标准化 URI 形式标识 |
| SVID | SVID | SPIFFE Verifiable Identity Document，工作负载的"身份证"；有 X.509-SVID 和 JWT-SVID 两种形态 |
| 信任包 / 信任束 | Trust Bundle | 一个 Trust Domain 内的所有可信 CA 证书集合 |
| SPIFFE 联邦 | SPIFFE Federation | 跨 Trust Domain 建立信任，交换 Trust Bundle |
| 节点证明 | Node Attestation | Node Attestation，对运行 SPIRE Agent 的节点（机器/VM/容器宿主）做身份证明 |
| 工作负载证明 | Workload Attestation | Workload Attestation，对工作负载进程做身份证明（拿到 SVID 前最后一步） |
| 节点代理 | SPIRE Agent | 部署在工作负载节点上的代理服务 |
| 控制平面 / 服务端 | SPIRE Server | 集中式签发 SVID 的服务 |
| 注册条目 | Registration Entry | 父 SPIFFE ID（parent ID）与子 SPIFFE ID（spiffe_id）、选择器（selectors）的对应关系 |
| 选择器 | Selector | 描述工作负载属性的 key/value 对，例如 `k8s:ns:foo` |
| 调用方身份 | Caller Identity | 发起请求一方的 SPIFFE ID |
| 身份文件 | Identity Document | 证明身份的具体文档（SVID 是一种身份文件） |
| 身份签发机构 | Identity Issuer | 签发 SVID 的实体，典型为 SPIRE Server |
| 身份消费者 / 依赖方 | Identity Consumer / Relying Party | 验证并使用对端 SVID 的服务 |
| 根 CA | Root CA | 信任根，签发中间 CA |
| 中间 CA | Intermediate CA | 签发终端实体 SVID 的中间证书签发者 |
| 下层 | Downstream | 服务调用链中"被调用"的一端 |
| 上游 | Upstream | 服务调用链中"调用他人"的一端 |

## 部署 / 运维

| 中文 | English | 说明 |
|---|---|---|
| 数据存储 | Data Store | SPIRE Server 持久化元数据的后端（SQLite / MySQL / Postgres） |
| 联邦网关 | Federation Gateway | SPIRE 内置的跨 Trust Domain 联邦网关 |
| 部署模型 | Deployment Model | 文中特指 SPIRE Server / Agent 拓扑，含独立、副本、分片（Sharding） |
| 节点升级器 | Node Resolver / Updater | 节点侧的插件 |
| 凭证桶 | Bucket of Creds | 形象说法，泛指 SPIFFE 提供的各种可验证身份材料 |
| 一次性密码 | OTP | One-Time Password |
| 凭据轮换 | Credential Rotation | 周期性更换 SVID / 私钥的过程 |
| 启动引导 | Bootstrap | 节点或集群初始化阶段 |

## 授权 / 访问控制

| 中文 | English | 说明 |
|---|---|---|
| 认证 | Authentication (AuthN) | 验证"你是谁" |
| 授权 | Authorization (AuthZ) | 决定"你能做什么" |
| 访问控制 | Access Control | 决定资源是否可被访问的整体机制 |
| 策略 | Policy | 描述"谁能做什么"的规则 |
| 策略执行点 | PEP | Policy Enforcement Point |
| 策略决策点 | PDP | Policy Decision Point |
| 策略信息点 | PIP | Policy Information Point |
| RBAC | RBAC | Role-Based Access Control，基于角色的访问控制 |
| ABAC | ABAC | Attribute-Based Access Control，基于属性的访问控制 |

## 网络 / 基础设施

| 中文 | English | 说明 |
|---|---|---|
| 边界 / 外围防线 | Perimeter | 传统基于网络边界的防护模型 |
| 服务网格 | Service Mesh | 常见有 Istio / Linkerd |
| 覆盖网络 | Overlay Network | 在既有网络之上构建的逻辑网络 |
| 微服务 | Microservice | 分布式系统中的小型自治服务 |
| 虚拟私有云 | VPC | Virtual Private Cloud |
| 命名空间 | Namespace | 特指 Kubernetes Namespace 时写作 k8s Namespace |

## 威胁与攻击

| 中文 | English | 说明 |
|---|---|---|
| 威胁模型 | Threat Model | 描述系统面临的威胁及应对假设 |
| 网络钓鱼 | Phishing | 通过伪装骗取凭证 |
| 蠕虫 | Worm | 自我复制的恶意程序 |
| 秘密 | Secret | 任何用于证明身份的字符串或密钥材料 |
| 秘密管理 | Secrets Management | 集中化管理和分发 Secret |
| 横向移动 | Lateral Movement | 攻击者在内网横向扩散 |
| 信任根 | Root of Trust | 整个信任链最底层的可信锚点 |
| "底部的乌龟" | Bottom Turtle | 书名典故：层层秘密背后那一只"不再需要保护"的乌龟 = Root of Trust |

## 常见产品 / 项目名（仅作引用，保留英文）

SPIFFE、SPIRE、Istio、Linkerd、Envoy、Consul Connect、HashiCorp Vault、AWS IAM、Azure AD、Active Directory、Kerberos、OpenSSL、Cloud Foundry、Kubernetes、Helm、Terraform、Ansible、Jenkins、Prometheus、Grafana、Open Policy Agent (OPA)、JWT.io、Teleport、Square SPIFFE Federation、Uber、ByteDance、Pinterest、Anthem、Cohesity、HPE、VMware、Netflix、Doc.ai、IBM、Slack、Stripe、Cloudflare、Twistlock、Palo Alto、Prisma Cloud、CNCF、SIG-Security、SIG-Auth。

---

**维护说明**：随着翻译推进，如发现遗漏的术语，在此表追加；不在表内的新术语由译者按上下文首次出现时给出中文译名。
