---
title: "附录 B　注释（Notes）"
---
# 附录 B　注释（Notes）

> 原书：*Notes*（p.190–191）
> 翻译策略：保留原书脚注序号、引用和链接。中文按"直译 + 段落重排"。

## 1. History and Motivation for SPIFFE

1. *Building Microservices*，O'Reilly Media, Inc.，2015。
2. *Turtles All the Way Down: Storing Secrets in the Cloud and the Data Center*，Daniel Somerfield，AppSecUSA 2015，[AppSecUSA 2015 议程](https://appsecusa2015.sched.com/event/621130a7c1090d129134ab6fb1c3cba4)。

## 2. Benefits

3. X.509 原本是 X.500 电信标准的一部分——X.500 提出了一种全球目录，用户可以按名字查找人或服务器的数据并拿到他们的证书。**X.500 的其他部分都没有得到广泛采用**。
4. 更多信息参见 [RFC 5280 PDF](https://www.rfc-editor.org/rfc/pdfrfc/rfc5280.txt.pdf)。
5. 一项叫做 **X.509 Name Constraints** 的较新扩展（参考 [RFC 5280 §Name Constraints](https://tools.ietf.org/html/rfc5280%23page-40)）允许对 CA 加上限制——它们不能为外部组织签发证书——**但它还没有被广泛采用**。
6. 服务如何与 CA 进行安全通信？**由于 CA 自己的证书是众所周知的，任何人都能与之建立安全连接**。
7. 想对 CRL 做一个入门介绍、并了解一些潜在问题，请参考 Ronald Rivest 的 *"Can we eliminate certificate revocation lists?"*（[Rivest: Can we eliminate CRLs?](https://people.csail.mit.edu/rivest/pubs/Riv98b.pdf)）。
8. **身份本身并不授予授权**；**真正起作用的是"与该身份相关联的特定属性"（保存在一个单独的存储里）**——允许决策点或执行点判断该实体是否被授权访问。

## 3. Introduction to SPIFFE and SPIRE concepts

9. **这个 API 不要求认证是一个重要的差异**——**它正是让我们能解决"底部的乌龟"问题的关键**。**SPIFFE 实现仍然负责"对 API 调用方做正向识别"**，
10. 与身份一起提供的信息可能包括：中间 CA 证书、用于证明身份的私钥、以及用于验证 SVID 的公钥。
11. 身份本身同时包含"信任域"和"名字"两个部分。**名字部分有时会被单独叫做"身份"，但它必须和信任域一起才完整——否则不唯一**。

## 4. Before You Start

12. 关于"采纳行为者"的一份优秀阅读材料：*Technology Adoption Curve: Traits of Adopters at Each Stage of the Lifecycle*（[Technology Adoption Curve](https://academy.whatfix.com/technology-adoption-curve)）。

## 5. Designing a SPIRE Deployment

13. **集群（cluster）由多台配置相同的 server 组成**。
