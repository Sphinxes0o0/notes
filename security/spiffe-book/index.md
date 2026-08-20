---
title: SPIFFE 翻译
---

# 扉页与前言（Frontmatter）

> 原书：扉页、版权页、致谢、About the book、About Zero the Turtle（p.1–5）
> 翻译策略：保留所有原作者署名、出版社、ISBN、CC BY 4.0 协议等版权信息；简介部分按"技术直译 + 段落重排"。

---

## 版权页

**Solving the Bottom Turtle — a SPIFFE Way to Establish Trust in Your Infrastructure via Universal Identity**

**作者**：Daniel Feldman、Emily Fox、Evan Gilman、Ian Haken、Frederick Kautz、Umair Khan、Max Lambrecht、Brandon Lum、Agustín Martínez Fayó、Eli Nesterov、Andres Vega、Michael Wardrop。**2020**。

**协议**：本作品采用 **Creative Commons Attribution 4.0 International License（CC BY 4.0）** 许可。

> 您可以自由地：
> - 共享——以任何媒介或格式复制、转发本作品
> - 修改——为任何目的（包括商业目的）修改本作品
>
> **唯一条件**：注明出处——您必须给出适当的署名、提供指向本协议的链接、指出是否做了修改。**您可以以任何合理的方式这样做，但不能以任何方式暗示许可方认可您或您的使用**。
>
> 完整协议文本：[CC BY 4.0 协议全文](https://creativecommons.org/licenses/by/4.0/legalcode)。

- **版本**：第一版，2020
- **ISBN**：978-0-578-77737-5
- **URL**：[thebottomturtle.io](https://thebottomturtle.io)

**本书使用 Book Sprints 方法学（[booksprints.net](https://www.booksprints.net)）制作**。**其内容由作者在为期两周的高强度在线协作中撰写**。

> **Hewlett Packard Enterprise（HPE）** 赞助了 Book Sprint，作为对开源社区的贡献。

---

## 致谢

| 角色 | 姓名 |
|---|---|
| Book Sprints 引导 | Barbara Rühling |
| 文字编辑 | Raewyn Whyte、Christine Davis |
| HTML 书籍设计 | Manuel Vazquez |
| 插画与封面设计 | Henrik Van Leeuwen |
| 字体 | Work Sans（Wei Huang 设计）、Iosevka（ Belleve Invis 设计） |

### 作者简介

| 姓名 | 职位 |
|---|---|
| **Daniel Feldman** | Hewlett Packard Enterprise 首席软件工程师 |
| **Emily Fox** | 云原生计算基金会（CNCF）安全特别兴趣小组（SIG-Security）联合主席 |
| **Evan Gilman** | VMware 资深工程师 |
| **Ian Haken** | Netflix 高级安全软件工程师 |
| **Frederick Kautz** | Doc.ai 边缘基础设施负责人 |
| **Umair Khan** | Hewlett Packard Enterprise 高级产品营销经理 |
| **Max Lambrecht** | Hewlett Packard Enterprise 高级软件工程师 |
| **Brandon Lum** | IBM 高级软件工程师 |
| **Agustín Martínez Fayó** | Hewlett Packard Enterprise 首席软件工程师 |
| **Eli Nesterov** | ByteDance 安全工程经理 |
| **Andres Vega** | VMware 产品线经理 |
| **Michael Wardrop** | Cohesity 资深工程师 |

---

## 关于本书

**本书介绍用于服务身份的 SPIFFE 标准、以及 SPIFFE 的参考实现 SPIRE**。**这些项目在现代、异构的基础设施之上提供统一的身份控制平面**。**两个项目都是开源的，都是 CNCF 的一部分**。

**当组织发展自己的应用架构、充分利用新的基础设施技术时，它们的安全模型也必须演化**。**软件已经从"一台机器上的单体"成长为"几十甚至几百个紧耦合的微服务"——这些微服务可能分散在公有云或私有数据中心的数千台虚拟机上**。**在这样的新基础设施世界中，SPIFFE 和 SPIRE 帮助系统保持安全**。

**本书致力于把 SPIFFE 和 SPIRE 顶尖专家的经验沉淀下来，让你能深入理解"身份"问题、以及如何解决它**。**有了这些项目，开发者和运维可以使用新的基础设施技术构建软件——同时让安全团队从那些昂贵、耗时的人工安全流程中抽身**。

---

## 关于 Zero the Turtle

> 图：本书封面上的 Zero the Turtle（见 `assets/pages/page-001.png`）。

**访问控制、秘密管理、身份——它们彼此依赖**。**大规模地管理秘密需要有效的访问控制**；**实现访问控制需要身份**；**证明身份需要拥有一个秘密**。**保护一个秘密需要想出办法去保护另一个秘密，而那个秘密又需要被保护——如此往复**。

这让人想起那个著名的轶事：一位女士打断一位哲学家的讲座，告诉他世界是站在一只乌龟的背上的。当哲学家问她"那只乌龟又站在什么上"时，她说："**一路向下，都是乌龟！**"。**找到那只"底部的乌龟"——所有其他安全都建立其上的那个坚实基础——就是 SPIFFE 和 SPIRE 项目的目标**。

**Zero the Turtle**——本书封面上的那只乌龟——**就是那只底部的乌龟**。**Zero 代表了数据中心与云中安全的基础**。**Zero 是可信的、愉快地支撑着所有其他乌龟**。

**SPIFFE 和 SPIRE 是帮助你为自己的组织找到"底部乌龟"的项目**。**有了本书中的工具，我们也希望你能为 Zero the Turtle 找到一个家**。

---

**目录**

- **第 1 章　SPIFFE 的历史与动机**
- **第 2 章　收益**
- **第 3 章　身份背后的通用概念**
- **第 4 章　SPIFFE 与 SPIRE 概念入门**
- **第 5 章　动手之前**
- **第 6 章　设计一个 SPIRE 部署**
- **第 7 章　与外部集成**
- **第 8 章　用 SPIFFE 身份驱动授权**
- **第 9 章　与其他安全技术的对比**
- **第 10 章　从业者故事**
- **附录 A　术语表（Glossary）**
- **附录 B　注释（Notes）**
- **附录 C　后记（Epilogue）**
- **术语对照表**
