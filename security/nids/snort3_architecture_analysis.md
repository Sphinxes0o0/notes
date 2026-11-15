---
title: "Snort 3 源码架构分析文档"
search: false
description: "Snort 3 是下一代 Snort IPS（入侵预防系统），是一个用 C++ 编写的开源网络入侵检测/预防系统。与 Snort 2.x 相比，Snort 3 采用了全新的架构设计，主要特性包括："
---
# Snort 3 源码架构分析文档

## 目录
1. [概述](#概述)
2. [整体架构](#整体架构)
3. [核心组件](#核心组件)
4. [数据包处理流程](#数据包处理流程)
5. [插件系统](#插件系统)
6. [检测系统](#检测系统)
7. [关键数据结构](#关键数据结构)
8. [模块详解](#模块详解)

---

本文按原有章节顺序拆为 28 篇。正文、代码与原章节编号保留；旧章节链接会跳转至对应分篇。

也可从 [数据包处理流水线与模块分析](./snort3/) 按模块阅读。

## 分篇目录

1. [架构与数据包流程](./snort3/01-architecture)：概述 — 模块详解
2. [数据结构与插件开发](./snort3/02-core-details)：总结 — 附录B：编解码器架构
3. [附录 C–L](./snort3/03-appendices-c-l)：附录C：事件和日志系统 — 附录L：流分割器 (Stream Splitter)
4. [附录 M–Z](./snort3/04-appendices-m-z)：附录M：正则表达式卸载 — 附录Z：核心流程时序图
5. [附录 AA–AN](./snort3/05-appendices-aa-an)：附录AA：Actions系统详解 — 附录AN：Port Scan检测器
6. [附录 AO–BH](./snort3/06-appendices-ao-bh)：附录AO：PerfMonitor性能监控 — 附录BH：Protocol IDs协议ID
7. [附录 BI–BY](./snort3/07-appendices-bi-by)：附录BI：BitFlags位标志操作 — 附录BY：PubSub事件系统
8. [附录 BZ–CQ](./snort3/08-appendices-bz-cq)：附录BZ：配置系统详解 — 附录CQ：DAta AcQuisition (DAQ)
9. [附录 CR–DK](./snort3/09-appendices-cr-dk)：附录CR：流重组细节 — 附录DK： IRC检测器
10. [附录 DL–EE](./snort3/10-appendices-dl-ee)：附录DL： SNMP检测器 — 附录EE： 线程局部存储
11. [附录 EF–EW](./snort3/11-appendices-ef-ew)：附录EF： 对象池 — 附录EW： 规则语法
12. [附录 EX–FH](./snort3/12-appendices-ex-fh)：附录EX： HiSF检测器 — 附录FH： MQTT检测器
13. [附录 FI–FX](./snort3/13-appendices-fi-fx)：附录FI： AMP检测器（自适应消息协议） — 附录FX： 性能计数器
14. [附录 FY–GK](./snort3/14-appendices-fy-gk)：附录FY： 云原生支持 — 附录GK： 持续集成
15. [附录 GL–GV](./snort3/15-appendices-gl-gv)：附录GL： 持续部署 — 附录GV： Elastic Stack集成
16. [附录 GW–HG](./snort3/16-appendices-gw-hg)：附录GW： 日志格式详解 — 附录HG： 字符串处理
17. [附录 HH–HQ](./snort3/17-appendices-hh-hq)：附录HH： 位操作工具 — 附录HQ： 信号处理
18. [附录 HR–ID](./snort3/18-appendices-hr-id)：附录HR： 进程管理 — 附录ID： 许可证和版权
19. [附录 IE–IN](./snort3/19-appendices-ie-in)：附录IE： 贡献指南 — 附录IN： 网络编程接口
20. [附录 IO–IY](./snort3/20-appendices-io-iy)：附录IO： 定时器实现 — 附录IY： 日志记录系统
21. [附录 IZ–JL](./snort3/21-appendices-iz-jl)：附录IZ： 审计系统 — 附录JL： 框架接口详解
22. [附录 JM–JX](./snort3/22-appendices-jm-jx)：附录JM： 核心数据结构 — 附录JX： 统计系统
23. [附录 JY–KJ](./snort3/23-appendices-jy-kj)：附录JY： 日志系统 — 附录KJ： 其他重要模块
24. [附录 KK–LB](./snort3/24-appendices-kk-lb)：附录KK： 配置文件详解 — 附录LB： 规则选项类型
25. [附录 LC–LW](./snort3/25-appendices-lc-lw)：附录LC： 配置参数 — 附录LW： 结束
26. [Codec、TCP 重组与流管理](./snort3/26-codecs-tcp-and-flow)：附录LX：Codec模块详细分析 — 附录ML：Flow管理详细分析
27. [Inspector、协议与规则解析](./snort3/27-inspectors-and-rules)：附录MM：IpsAction和响应处理详细分析 — 附录NC：规则解析系统
28. [协议检测与参考索引](./snort3/28-protocols-and-reference)：附录MS：SIP检测模块详细分析 — 附录MJ：文档更新记录

## 完整章节索引

### [架构与数据包流程](./snort3/01-architecture)

- <span id="概述"></span>[概述](/security/nids/snort3/01-architecture#%E6%A6%82%E8%BF%B0)
- <span id="整体架构"></span>[整体架构](/security/nids/snort3/01-architecture#%E6%95%B4%E4%BD%93%E6%9E%B6%E6%9E%84)
- <span id="核心组件"></span>[核心组件](/security/nids/snort3/01-architecture#%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6)
- <span id="数据包处理流程"></span>[数据包处理流程](/security/nids/snort3/01-architecture#%E6%95%B0%E6%8D%AE%E5%8C%85%E5%A4%84%E7%90%86%E6%B5%81%E7%A8%8B)
- <span id="插件系统"></span>[插件系统](/security/nids/snort3/01-architecture#%E6%8F%92%E4%BB%B6%E7%B3%BB%E7%BB%9F)
- <span id="检测系统"></span>[检测系统](/security/nids/snort3/01-architecture#%E6%A3%80%E6%B5%8B%E7%B3%BB%E7%BB%9F)
- <span id="关键数据结构"></span>[关键数据结构](/security/nids/snort3/01-architecture#%E5%85%B3%E9%94%AE%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
- <span id="模块详解"></span>[模块详解](/security/nids/snort3/01-architecture#%E6%A8%A1%E5%9D%97%E8%AF%A6%E8%A7%A3)

### [数据结构与插件开发](./snort3/02-core-details)

- <span id="总结"></span>[总结](/security/nids/snort3/02-core-details#%E6%80%BB%E7%BB%93)
- <span id="附录-关键数据结构详解"></span>[附录：关键数据结构详解](/security/nids/snort3/02-core-details#%E9%99%84%E5%BD%95-%E5%85%B3%E9%94%AE%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E8%AF%A6%E8%A7%A3)
- <span id="tcp流跟踪架构详解"></span>[TCP流跟踪架构详解](/security/nids/snort3/02-core-details#tcp%E6%B5%81%E8%B7%9F%E8%B8%AA%E6%9E%B6%E6%9E%84%E8%AF%A6%E8%A7%A3)
- <span id="规则匹配深度解析"></span>[规则匹配深度解析](/security/nids/snort3/02-core-details#%E8%A7%84%E5%88%99%E5%8C%B9%E9%85%8D%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90)
- <span id="插件开发指南"></span>[插件开发指南](/security/nids/snort3/02-core-details#%E6%8F%92%E4%BB%B6%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97)
- <span id="总结-1"></span>[总结](/security/nids/snort3/02-core-details#%E6%80%BB%E7%BB%93-1)
- <span id="附录b-编解码器架构"></span>[附录B：编解码器架构](/security/nids/snort3/02-core-details#%E9%99%84%E5%BD%95b-%E7%BC%96%E8%A7%A3%E7%A0%81%E5%99%A8%E6%9E%B6%E6%9E%84)

### [附录 C–L](./snort3/03-appendices-c-l)

- <span id="附录c-事件和日志系统"></span>[附录C：事件和日志系统](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95c-%E4%BA%8B%E4%BB%B6%E5%92%8C%E6%97%A5%E5%BF%97%E7%B3%BB%E7%BB%9F)
- <span id="附录d-配置系统架构"></span>[附录D：配置系统架构](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95d-%E9%85%8D%E7%BD%AE%E7%B3%BB%E7%BB%9F%E6%9E%B6%E6%9E%84)
- <span id="附录e-关键类层次结构"></span>[附录E：关键类层次结构](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95e-%E5%85%B3%E9%94%AE%E7%B1%BB%E5%B1%82%E6%AC%A1%E7%BB%93%E6%9E%84)
- <span id="附录f-binder和wizard机制"></span>[附录F：Binder和Wizard机制](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95f-binder%E5%92%8Cwizard%E6%9C%BA%E5%88%B6)
- <span id="附录g-快速模式匹配-mpse-深度解析"></span>[附录G：快速模式匹配 (MPSE) 深度解析](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95g-%E5%BF%AB%E9%80%9F%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D-mpse-%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90)
- <span id="附录h-检测选项类型"></span>[附录H：检测选项类型](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95h-%E6%A3%80%E6%B5%8B%E9%80%89%E9%A1%B9%E7%B1%BB%E5%9E%8B)
- <span id="附录i-pub-sub事件系统"></span>[附录I：Pub/Sub事件系统](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95i-pub-sub%E4%BA%8B%E4%BB%B6%E7%B3%BB%E7%BB%9F)
- <span id="附录j-snort配置系统"></span>[附录J：Snort配置系统](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95j-snort%E9%85%8D%E7%BD%AE%E7%B3%BB%E7%BB%9F)
- <span id="附录k-daq数据获取接口"></span>[附录K：DAQ数据获取接口](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95k-daq%E6%95%B0%E6%8D%AE%E8%8E%B7%E5%8F%96%E6%8E%A5%E5%8F%A3)
- <span id="附录l-流分割器-stream-splitter"></span>[附录L：流分割器 (Stream Splitter)](/security/nids/snort3/03-appendices-c-l#%E9%99%84%E5%BD%95l-%E6%B5%81%E5%88%86%E5%89%B2%E5%99%A8-stream-splitter)

### [附录 M–Z](./snort3/04-appendices-m-z)

- <span id="附录m-正则表达式卸载"></span>[附录M：正则表达式卸载](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95m-%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E5%8D%B8%E8%BD%BD)
- <span id="附录n-文件处理和mime"></span>[附录N：文件处理和MIME](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95n-%E6%96%87%E4%BB%B6%E5%A4%84%E7%90%86%E5%92%8Cmime)
- <span id="附录o-主循环和处理流程"></span>[附录O：主循环和处理流程](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95o-%E4%B8%BB%E5%BE%AA%E7%8E%AF%E5%92%8C%E5%A4%84%E7%90%86%E6%B5%81%E7%A8%8B)
- <span id="附录p-内存管理和对象池"></span>[附录P：内存管理和对象池](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95p-%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E5%92%8C%E5%AF%B9%E8%B1%A1%E6%B1%A0)
- <span id="附录q-多线程和线程本地存储"></span>[附录Q：多线程和线程本地存储](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95q-%E5%A4%9A%E7%BA%BF%E7%A8%8B%E5%92%8C%E7%BA%BF%E7%A8%8B%E6%9C%AC%E5%9C%B0%E5%AD%98%E5%82%A8)
- <span id="附录r-ha高可用性"></span>[附录R：HA高可用性](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95r-ha%E9%AB%98%E5%8F%AF%E7%94%A8%E6%80%A7)
- <span id="附录s-追踪和调试"></span>[附录S：追踪和调试](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95s-%E8%BF%BD%E8%B8%AA%E5%92%8C%E8%B0%83%E8%AF%95)
- <span id="附录t-时间处理"></span>[附录T：时间处理](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95t-%E6%97%B6%E9%97%B4%E5%A4%84%E7%90%86)
- <span id="附录u-搜索引擎比较"></span>[附录U：搜索引擎比较](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95u-%E6%90%9C%E7%B4%A2%E5%BC%95%E6%93%8E%E6%AF%94%E8%BE%83)
- <span id="附录v-常见规则选项详解"></span>[附录V：常见规则选项详解](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95v-%E5%B8%B8%E8%A7%81%E8%A7%84%E5%88%99%E9%80%89%E9%A1%B9%E8%AF%A6%E8%A7%A3)
- <span id="附录w-开发示例"></span>[附录W：开发示例](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95w-%E5%BC%80%E5%8F%91%E7%A4%BA%E4%BE%8B)
- <span id="文档总结"></span>[文档总结](/security/nids/snort3/04-appendices-m-z#%E6%96%87%E6%A1%A3%E6%80%BB%E7%BB%93)
- <span id="附录x-检测引擎深度解析"></span>[附录X：检测引擎深度解析](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95x-%E6%A3%80%E6%B5%8B%E5%BC%95%E6%93%8E%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90)
- <span id="附录y-规则编译详解"></span>[附录Y：规则编译详解](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95y-%E8%A7%84%E5%88%99%E7%BC%96%E8%AF%91%E8%AF%A6%E8%A7%A3)
- <span id="附录z-核心流程时序图"></span>[附录Z：核心流程时序图](/security/nids/snort3/04-appendices-m-z#%E9%99%84%E5%BD%95z-%E6%A0%B8%E5%BF%83%E6%B5%81%E7%A8%8B%E6%97%B6%E5%BA%8F%E5%9B%BE)

### [附录 AA–AN](./snort3/05-appendices-aa-an)

- <span id="附录aa-actions系统详解"></span>[附录AA：Actions系统详解](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95aa-actions%E7%B3%BB%E7%BB%9F%E8%AF%A6%E8%A7%A3)
- <span id="附录ab-latency延迟管理"></span>[附录AB：Latency延迟管理](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ab-latency%E5%BB%B6%E8%BF%9F%E7%AE%A1%E7%90%86)
- <span id="附录ac-dns检测器详解"></span>[附录AC：DNS检测器详解](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ac-dns%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录ad-smtp检测器"></span>[附录AD：SMTP检测器](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ad-smtp%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录ae-ftp-telnet检测器"></span>[附录AE：FTP/Telnet检测器](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ae-ftp-telnet%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录af-active响应"></span>[附录AF：Active响应](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95af-active%E5%93%8D%E5%BA%94)
- <span id="附录ag-文件处理详解"></span>[附录AG：文件处理详解](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ag-%E6%96%87%E4%BB%B6%E5%A4%84%E7%90%86%E8%AF%A6%E8%A7%A3)
- <span id="附录ah-filter过滤器详解"></span>[附录AH：Filter过滤器详解](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ah-filter%E8%BF%87%E6%BB%A4%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录ai-snort协议id"></span>[附录AI：Snort协议ID](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ai-snort%E5%8D%8F%E8%AE%AEid)
- <span id="附录aj-主要源目录详解"></span>[附录AJ：主要源目录详解](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95aj-%E4%B8%BB%E8%A6%81%E6%BA%90%E7%9B%AE%E5%BD%95%E8%AF%A6%E8%A7%A3)
- <span id="附录ak-常用配置示例"></span>[附录AK：常用配置示例](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95ak-%E5%B8%B8%E7%94%A8%E9%85%8D%E7%BD%AE%E7%A4%BA%E4%BE%8B)
- <span id="附录al-调试和问题排查"></span>[附录AL：调试和问题排查](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95al-%E8%B0%83%E8%AF%95%E5%92%8C%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5)
- <span id="附录am-术语表"></span>[附录AM：术语表](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95am-%E6%9C%AF%E8%AF%AD%E8%A1%A8)
- <span id="附录an-port-scan检测器"></span>[附录AN：Port Scan检测器](/security/nids/snort3/05-appendices-aa-an#%E9%99%84%E5%BD%95an-port-scan%E6%A3%80%E6%B5%8B%E5%99%A8)

### [附录 AO–BH](./snort3/06-appendices-ao-bh)

- <span id="附录ao-perfmonitor性能监控"></span>[附录AO：PerfMonitor性能监控](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95ao-perfmonitor%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7)
- <span id="附录ap-stream-udp处理"></span>[附录AP：Stream UDP处理](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95ap-stream-udp%E5%A4%84%E7%90%86)
- <span id="附录aq-normalizer规范化器"></span>[附录AQ：Normalizer规范化器](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95aq-normalizer%E8%A7%84%E8%8C%83%E5%8C%96%E5%99%A8)
- <span id="附录ar-service-map和classifier"></span>[附录AR：Service Map和Classifier](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95ar-service-map%E5%92%8Cclassifier)
- <span id="附录as-eventqueue事件队列"></span>[附录AS：EventQueue事件队列](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95as-eventqueue%E4%BA%8B%E4%BB%B6%E9%98%9F%E5%88%97)
- <span id="附录at-config-dump配置输出"></span>[附录AT：Config Dump配置输出](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95at-config-dump%E9%85%8D%E7%BD%AE%E8%BE%93%E5%87%BA)
- <span id="附录au-target-based目标基础"></span>[附录AU：Target Based目标基础](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95au-target-based%E7%9B%AE%E6%A0%87%E5%9F%BA%E7%A1%80)
- <span id="附录av-packetmanager数据包管理"></span>[附录AV：PacketManager数据包管理](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95av-packetmanager%E6%95%B0%E6%8D%AE%E5%8C%85%E7%AE%A1%E7%90%86)
- <span id="附录aw-prox模块"></span>[附录AW：Prox模块](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95aw-prox%E6%A8%A1%E5%9D%97)
- <span id="附录ax-ip碎片重组"></span>[附录AX：IP碎片重组](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95ax-ip%E7%A2%8E%E7%89%87%E9%87%8D%E7%BB%84)
- <span id="附录ay-正则表达式pcre"></span>[附录AY：正则表达式PCRE](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95ay-%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8Fpcre)
- <span id="附录az-sfrt检索表"></span>[附录AZ：Sfrt检索表](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95az-sfrt%E6%A3%80%E7%B4%A2%E8%A1%A8)
- <span id="附录ba-host-tracker主机追踪"></span>[附录BA：Host Tracker主机追踪](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95ba-host-tracker%E4%B8%BB%E6%9C%BA%E8%BF%BD%E8%B8%AA)
- <span id="附录bb-pubsub事件详解"></span>[附录BB：PubSub事件详解](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95bb-pubsub%E4%BA%8B%E4%BB%B6%E8%AF%A6%E8%A7%A3)
- <span id="附录bc-mpsemanager搜索引擎管理"></span>[附录BC：MpseManager搜索引擎管理](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95bc-mpsemanager%E6%90%9C%E7%B4%A2%E5%BC%95%E6%93%8E%E7%AE%A1%E7%90%86)
- <span id="附录bd-stream-splitter详解"></span>[附录BD：Stream Splitter详解](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95bd-stream-splitter%E8%AF%A6%E8%A7%A3)
- <span id="附录be-detection模块配置"></span>[附录BE：Detection模块配置](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95be-detection%E6%A8%A1%E5%9D%97%E9%85%8D%E7%BD%AE)
- <span id="附录bf-actions模块详解"></span>[附录BF：Actions模块详解](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95bf-actions%E6%A8%A1%E5%9D%97%E8%AF%A6%E8%A7%A3)
- <span id="附录bg-inspector类型详解"></span>[附录BG：Inspector类型详解](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95bg-inspector%E7%B1%BB%E5%9E%8B%E8%AF%A6%E8%A7%A3)
- <span id="附录bh-protocol-ids协议id"></span>[附录BH：Protocol IDs协议ID](/security/nids/snort3/06-appendices-ao-bh#%E9%99%84%E5%BD%95bh-protocol-ids%E5%8D%8F%E8%AE%AEid)

### [附录 BI–BY](./snort3/07-appendices-bi-by)

- <span id="附录bi-bitflags位标志操作"></span>[附录BI：BitFlags位标志操作](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bi-bitflags%E4%BD%8D%E6%A0%87%E5%BF%97%E6%93%8D%E4%BD%9C)
- <span id="附录bj-hash模块"></span>[附录BJ：Hash模块](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bj-hash%E6%A8%A1%E5%9D%97)
- <span id="附录bk-smtp检测器"></span>[附录BK：SMTP检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bk-smtp%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bl-ftp-telnet检测器"></span>[附录BL：FTP/Telnet检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bl-ftp-telnet%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bm-dns检测器"></span>[附录BM：DNS检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bm-dns%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bn-ssl-tls检测器"></span>[附录BN：SSL/TLS检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bn-ssl-tls%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bo-sip检测器"></span>[附录BO：SIP检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bo-sip%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bp-pop3-imap检测器"></span>[附录BP：POP3/IMAP检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bp-pop3-imap%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bq-ssh检测器"></span>[附录BQ：SSH检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bq-ssh%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录br-dnp3检测器"></span>[附录BR：DNP3检测器](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95br-dnp3%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录bs-base64编码处理"></span>[附录BS：Base64编码处理](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bs-base64%E7%BC%96%E7%A0%81%E5%A4%84%E7%90%86)
- <span id="附录bt-packet结构深度解析"></span>[附录BT：Packet结构深度解析](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bt-packet%E7%BB%93%E6%9E%84%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90)
- <span id="附录bu-flow数据结构深度解析"></span>[附录BU：Flow数据结构深度解析](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bu-flow%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90)
- <span id="附录bv-ipsaction系统详解"></span>[附录BV： IpsAction系统详解](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bv-ipsaction%E7%B3%BB%E7%BB%9F%E8%AF%A6%E8%A7%A3)
- <span id="附录bw-detectionengine深度解析"></span>[附录BW：DetectionEngine深度解析](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bw-detectionengine%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90)
- <span id="附录bx-module系统详解"></span>[附录BX：Module系统详解](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95bx-module%E7%B3%BB%E7%BB%9F%E8%AF%A6%E8%A7%A3)
- <span id="附录by-pubsub事件系统"></span>[附录BY：PubSub事件系统](/security/nids/snort3/07-appendices-bi-by#%E9%99%84%E5%BD%95by-pubsub%E4%BA%8B%E4%BB%B6%E7%B3%BB%E7%BB%9F)

### [附录 BZ–CQ](./snort3/08-appendices-bz-cq)

- <span id="附录bz-配置系统详解"></span>[附录BZ：配置系统详解](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95bz-%E9%85%8D%E7%BD%AE%E7%B3%BB%E7%BB%9F%E8%AF%A6%E8%A7%A3)
- <span id="附录ca-网络接口定义"></span>[附录CA：网络接口定义](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95ca-%E7%BD%91%E7%BB%9C%E6%8E%A5%E5%8F%A3%E5%AE%9A%E4%B9%89)
- <span id="附录cb-时间处理"></span>[附录CB：时间处理](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cb-%E6%97%B6%E9%97%B4%E5%A4%84%E7%90%86)
- <span id="附录cc-内存管理"></span>[附录CC：内存管理](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cc-%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86)
- <span id="附录cd-原子操作"></span>[附录CD：原子操作](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cd-%E5%8E%9F%E5%AD%90%E6%93%8D%E4%BD%9C)
- <span id="附录ce-正则表达式引擎"></span>[附录CE：正则表达式引擎](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95ce-%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E5%BC%95%E6%93%8E)
- <span id="附录cf-文件系统处理"></span>[附录CF：文件系统处理](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cf-%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E5%A4%84%E7%90%86)
- <span id="附录cg-缓冲区管理"></span>[附录CG：缓冲区管理](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cg-%E7%BC%93%E5%86%B2%E5%8C%BA%E7%AE%A1%E7%90%86)
- <span id="附录ch-性能分析"></span>[附录CH：性能分析](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95ch-%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90)
- <span id="附录ci-追踪系统"></span>[附录CI：追踪系统](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95ci-%E8%BF%BD%E8%B8%AA%E7%B3%BB%E7%BB%9F)
- <span id="附录cj-主循环流程"></span>[附录CJ：主循环流程](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cj-%E4%B8%BB%E5%BE%AA%E7%8E%AF%E6%B5%81%E7%A8%8B)
- <span id="附录ck-规则选项数据结构"></span>[附录CK：规则选项数据结构](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95ck-%E8%A7%84%E5%88%99%E9%80%89%E9%A1%B9%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
- <span id="附录cl-codec系统"></span>[附录CL：Codec系统](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cl-codec%E7%B3%BB%E7%BB%9F)
- <span id="附录cm-日志系统"></span>[附录CM：日志系统](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cm-%E6%97%A5%E5%BF%97%E7%B3%BB%E7%BB%9F)
- <span id="附录cn-过滤器系统"></span>[附录CN：过滤器系统](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cn-%E8%BF%87%E6%BB%A4%E5%99%A8%E7%B3%BB%E7%BB%9F)
- <span id="附录co-网络地址处理"></span>[附录CO：网络地址处理](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95co-%E7%BD%91%E7%BB%9C%E5%9C%B0%E5%9D%80%E5%A4%84%E7%90%86)
- <span id="附录cp-端口处理"></span>[附录CP：端口处理](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cp-%E7%AB%AF%E5%8F%A3%E5%A4%84%E7%90%86)
- <span id="附录cq-data-acquisition-daq"></span>[附录CQ：DAta AcQuisition (DAQ)](/security/nids/snort3/08-appendices-bz-cq#%E9%99%84%E5%BD%95cq-data-acquisition-daq)

### [附录 CR–DK](./snort3/09-appendices-cr-dk)

- <span id="附录cr-流重组细节"></span>[附录CR：流重组细节](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cr-%E6%B5%81%E9%87%8D%E7%BB%84%E7%BB%86%E8%8A%82)
- <span id="附录cs-协议字段"></span>[附录CS：协议字段](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cs-%E5%8D%8F%E8%AE%AE%E5%AD%97%E6%AE%B5)
- <span id="附录ct-tcp跟踪状态机"></span>[附录CT：TCP跟踪状态机](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95ct-tcp%E8%B7%9F%E8%B8%AA%E7%8A%B6%E6%80%81%E6%9C%BA)
- <span id="附录cu-内存对齐处理"></span>[附录CU：内存对齐处理](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cu-%E5%86%85%E5%AD%98%E5%AF%B9%E9%BD%90%E5%A4%84%E7%90%86)
- <span id="附录cv-配置加载"></span>[附录CV：配置加载](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cv-%E9%85%8D%E7%BD%AE%E5%8A%A0%E8%BD%BD)
- <span id="附录cw-插件api"></span>[附录CW：插件API](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cw-%E6%8F%92%E4%BB%B6api)
- <span id="附录cx-搜索算法"></span>[附录CX：搜索算法](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cx-%E6%90%9C%E7%B4%A2%E7%AE%97%E6%B3%95)
- <span id="附录cy-协议相关错误处理"></span>[附录CY：协议相关错误处理](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cy-%E5%8D%8F%E8%AE%AE%E7%9B%B8%E5%85%B3%E9%94%99%E8%AF%AF%E5%A4%84%E7%90%86)
- <span id="附录cz-配置示例"></span>[附录CZ：配置示例](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95cz-%E9%85%8D%E7%BD%AE%E7%A4%BA%E4%BE%8B)
- <span id="附录da-调试技巧"></span>[附录DA：调试技巧](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95da-%E8%B0%83%E8%AF%95%E6%8A%80%E5%B7%A7)
- <span id="附录db-测试框架"></span>[附录DB：测试框架](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95db-%E6%B5%8B%E8%AF%95%E6%A1%86%E6%9E%B6)
- <span id="附录dc-性能优化建议"></span>[附录DC：性能优化建议](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95dc-%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E5%BB%BA%E8%AE%AE)
- <span id="附录dd-命令参考"></span>[附录DD：命令参考](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95dd-%E5%91%BD%E4%BB%A4%E5%8F%82%E8%80%83)
- <span id="附录de-术语表"></span>[附录DE：术语表](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95de-%E6%9C%AF%E8%AF%AD%E8%A1%A8)
- <span id="附录df-arp协议检测器"></span>[附录DF： ARP协议检测器](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95df-arp%E5%8D%8F%E8%AE%AE%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dg-gtp检测器-gprs隧道协议"></span>[附录DG： GTP检测器（GPRS隧道协议）](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95dg-gtp%E6%A3%80%E6%B5%8B%E5%99%A8-gprs%E9%9A%A7%E9%81%93%E5%8D%8F%E8%AE%AE)
- <span id="附录dh-diameter协议检测器"></span>[附录DH： Diameter协议检测器](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95dh-diameter%E5%8D%8F%E8%AE%AE%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录di-radius协议检测器"></span>[附录DI： Radius协议检测器](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95di-radius%E5%8D%8F%E8%AE%AE%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dj-dhcp检测器"></span>[附录DJ： DHCP检测器](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95dj-dhcp%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dk-irc检测器"></span>[附录DK： IRC检测器](/security/nids/snort3/09-appendices-cr-dk#%E9%99%84%E5%BD%95dk-irc%E6%A3%80%E6%B5%8B%E5%99%A8)

### [附录 DL–EE](./snort3/10-appendices-dl-ee)

- <span id="附录dl-snmp检测器"></span>[附录DL： SNMP检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dl-snmp%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dm-ssh检测器"></span>[附录DM： SSH检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dm-ssh%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dn-smb检测器"></span>[附录DN： SMB检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dn-smb%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录do-dcerpc检测器"></span>[附录DO： DCERPC检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95do-dcerpc%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dp-pop3检测器详解"></span>[附录DP： POP3检测器详解](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dp-pop3%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录dq-imap检测器详解"></span>[附录DQ： IMAP检测器详解](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dq-imap%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录dr-rdp检测器"></span>[附录DR： RDP检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dr-rdp%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录ds-kerberos检测器"></span>[附录DS： Kerberos检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95ds-kerberos%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dt-netbios检测器"></span>[附录DT： NetBIOS检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dt-netbios%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录du-uucp检测器"></span>[附录DU： UUCP检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95du-uucp%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dv-quake检测器"></span>[附录DV： Quake检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dv-quake%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dw-teamspeak检测器"></span>[附录DW： Teamspeak检测器](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dw-teamspeak%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录dx-dns检测器详解"></span>[附录DX： DNS检测器详解](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dx-dns%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录dy-模块引用关系图"></span>[附录DY： 模块引用关系图](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dy-%E6%A8%A1%E5%9D%97%E5%BC%95%E7%94%A8%E5%85%B3%E7%B3%BB%E5%9B%BE)
- <span id="附录dz-关键类层次结构"></span>[附录DZ： 关键类层次结构](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95dz-%E5%85%B3%E9%94%AE%E7%B1%BB%E5%B1%82%E6%AC%A1%E7%BB%93%E6%9E%84)
- <span id="附录ea-规则选项链"></span>[附录EA： 规则选项链](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95ea-%E8%A7%84%E5%88%99%E9%80%89%E9%A1%B9%E9%93%BE)
- <span id="附录eb-编码和解码流程"></span>[附录EB： 编码和解码流程](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95eb-%E7%BC%96%E7%A0%81%E5%92%8C%E8%A7%A3%E7%A0%81%E6%B5%81%E7%A8%8B)
- <span id="附录ec-模式匹配流程"></span>[附录EC： 模式匹配流程](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95ec-%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D%E6%B5%81%E7%A8%8B)
- <span id="附录ed-内存布局"></span>[附录ED： 内存布局](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95ed-%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80)
- <span id="附录ee-线程局部存储"></span>[附录EE： 线程局部存储](/security/nids/snort3/10-appendices-dl-ee#%E9%99%84%E5%BD%95ee-%E7%BA%BF%E7%A8%8B%E5%B1%80%E9%83%A8%E5%AD%98%E5%82%A8)

### [附录 EF–EW](./snort3/11-appendices-ef-ew)

- <span id="附录ef-对象池"></span>[附录EF： 对象池](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ef-%E5%AF%B9%E8%B1%A1%E6%B1%A0)
- <span id="附录eg-事件日志系统"></span>[附录EG： 事件日志系统](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95eg-%E4%BA%8B%E4%BB%B6%E6%97%A5%E5%BF%97%E7%B3%BB%E7%BB%9F)
- <span id="附录eh-延迟监控"></span>[附录EH： 延迟监控](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95eh-%E5%BB%B6%E8%BF%9F%E7%9B%91%E6%8E%A7)
- <span id="附录ei-配置合并"></span>[附录EI： 配置合并](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ei-%E9%85%8D%E7%BD%AE%E5%90%88%E5%B9%B6)
- <span id="附录ej-数据流图"></span>[附录EJ： 数据流图](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ej-%E6%95%B0%E6%8D%AE%E6%B5%81%E5%9B%BE)
- <span id="附录ek-时序图-tcp会话建立"></span>[附录EK： 时序图 - TCP会话建立](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ek-%E6%97%B6%E5%BA%8F%E5%9B%BE-tcp%E4%BC%9A%E8%AF%9D%E5%BB%BA%E7%AB%8B)
- <span id="附录el-流重组时序"></span>[附录EL： 流重组时序](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95el-%E6%B5%81%E9%87%8D%E7%BB%84%E6%97%B6%E5%BA%8F)
- <span id="附录em-规则匹配时序"></span>[附录EM： 规则匹配时序](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95em-%E8%A7%84%E5%88%99%E5%8C%B9%E9%85%8D%E6%97%B6%E5%BA%8F)
- <span id="附录en-插件生命周期"></span>[附录EN： 插件生命周期](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95en-%E6%8F%92%E4%BB%B6%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F)
- <span id="附录eo-消息类型注册"></span>[附录EO： 消息类型注册](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95eo-%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E6%B3%A8%E5%86%8C)
- <span id="附录ep-错误处理"></span>[附录EP： 错误处理](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ep-%E9%94%99%E8%AF%AF%E5%A4%84%E7%90%86)
- <span id="附录eq-统计信息"></span>[附录EQ： 统计信息](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95eq-%E7%BB%9F%E8%AE%A1%E4%BF%A1%E6%81%AF)
- <span id="附录er-配置验证"></span>[附录ER： 配置验证](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95er-%E9%85%8D%E7%BD%AE%E9%AA%8C%E8%AF%81)
- <span id="附录es-性能分析工具"></span>[附录ES： 性能分析工具](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95es-%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90%E5%B7%A5%E5%85%B7)
- <span id="附录et-编译配置"></span>[附录ET： 编译配置](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95et-%E7%BC%96%E8%AF%91%E9%85%8D%E7%BD%AE)
- <span id="附录eu-调试技术"></span>[附录EU： 调试技术](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95eu-%E8%B0%83%E8%AF%95%E6%8A%80%E6%9C%AF)
- <span id="附录ev-常用命令选项"></span>[附录EV： 常用命令选项](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ev-%E5%B8%B8%E7%94%A8%E5%91%BD%E4%BB%A4%E9%80%89%E9%A1%B9)
- <span id="附录ew-规则语法"></span>[附录EW： 规则语法](/security/nids/snort3/11-appendices-ef-ew#%E9%99%84%E5%BD%95ew-%E8%A7%84%E5%88%99%E8%AF%AD%E6%B3%95)

### [附录 EX–FH](./snort3/12-appendices-ex-fh)

- <span id="附录ex-hisf检测器"></span>[附录EX： HiSF检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95ex-hisf%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录ey-iec-61850检测器"></span>[附录EY： IEC 61850检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95ey-iec-61850%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录ez-modbus检测器"></span>[附录EZ： Modbus检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95ez-modbus%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录fa-dnp3检测器详解"></span>[附录FA： DNP3检测器详解](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fa-dnp3%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录fb-gtp检测器详解"></span>[附录FB： GTP检测器详解](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fb-gtp%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录fc-sip检测器详解"></span>[附录FC： SIP检测器详解](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fc-sip%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录fd-rpc检测器"></span>[附录FD： RPC检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fd-rpc%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录fe-smb检测器详解"></span>[附录FE： SMB检测器详解](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fe-smb%E6%A3%80%E6%B5%8B%E5%99%A8%E8%AF%A6%E8%A7%A3)
- <span id="附录ff-http-2检测器"></span>[附录FF： HTTP/2检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95ff-http-2%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录fg-websocket检测器"></span>[附录FG： WebSocket检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fg-websocket%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录fh-mqtt检测器"></span>[附录FH： MQTT检测器](/security/nids/snort3/12-appendices-ex-fh#%E9%99%84%E5%BD%95fh-mqtt%E6%A3%80%E6%B5%8B%E5%99%A8)

### [附录 FI–FX](./snort3/13-appendices-fi-fx)

- <span id="附录fi-amp检测器-自适应消息协议"></span>[附录FI： AMP检测器（自适应消息协议）](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fi-amp%E6%A3%80%E6%B5%8B%E5%99%A8-%E8%87%AA%E9%80%82%E5%BA%94%E6%B6%88%E6%81%AF%E5%8D%8F%E8%AE%AE)
- <span id="附录fj-cip检测器-通用工业协议"></span>[附录FJ： CIP检测器（通用工业协议）](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fj-cip%E6%A3%80%E6%B5%8B%E5%99%A8-%E9%80%9A%E7%94%A8%E5%B7%A5%E4%B8%9A%E5%8D%8F%E8%AE%AE)
- <span id="附录fk-s7comm检测器-s7通信"></span>[附录FK： S7Comm检测器（S7通信）](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fk-s7comm%E6%A3%80%E6%B5%8B%E5%99%A8-s7%E9%80%9A%E4%BF%A1)
- <span id="附录fl-enip检测器-ethernet-ip"></span>[附录FL： ENIP检测器（EtherNet/IP）](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fl-enip%E6%A3%80%E6%B5%8B%E5%99%A8-ethernet-ip)
- <span id="附录fm-http代理检测器"></span>[附录FM： Http代理检测器](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fm-http%E4%BB%A3%E7%90%86%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录fn-检测性能分析"></span>[附录FN： 检测性能分析](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fn-%E6%A3%80%E6%B5%8B%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90)
- <span id="附录fo-内存分析"></span>[附录FO： 内存分析](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fo-%E5%86%85%E5%AD%98%E5%88%86%E6%9E%90)
- <span id="附录fp-协议解析器框架"></span>[附录FP： 协议解析器框架](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fp-%E5%8D%8F%E8%AE%AE%E8%A7%A3%E6%9E%90%E5%99%A8%E6%A1%86%E6%9E%B6)
- <span id="附录fq-防火墙集成"></span>[附录FQ： 防火墙集成](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fq-%E9%98%B2%E7%81%AB%E5%A2%99%E9%9B%86%E6%88%90)
- <span id="附录fr-策略管理"></span>[附录FR： 策略管理](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fr-%E7%AD%96%E7%95%A5%E7%AE%A1%E7%90%86)
- <span id="附录fs-威胁情报集成"></span>[附录FS： 威胁情报集成](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fs-%E5%A8%81%E8%83%81%E6%83%85%E6%8A%A5%E9%9B%86%E6%88%90)
- <span id="附录ft-文件签名库"></span>[附录FT： 文件签名库](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95ft-%E6%96%87%E4%BB%B6%E7%AD%BE%E5%90%8D%E5%BA%93)
- <span id="附录fu-安全特性"></span>[附录FU： 安全特性](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fu-%E5%AE%89%E5%85%A8%E7%89%B9%E6%80%A7)
- <span id="附录fv-模式匹配优化"></span>[附录FV： 模式匹配优化](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fv-%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D%E4%BC%98%E5%8C%96)
- <span id="附录fw-加密流量检测"></span>[附录FW： 加密流量检测](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fw-%E5%8A%A0%E5%AF%86%E6%B5%81%E9%87%8F%E6%A3%80%E6%B5%8B)
- <span id="附录fx-性能计数器"></span>[附录FX： 性能计数器](/security/nids/snort3/13-appendices-fi-fx#%E9%99%84%E5%BD%95fx-%E6%80%A7%E8%83%BD%E8%AE%A1%E6%95%B0%E5%99%A8)

### [附录 FY–GK](./snort3/14-appendices-fy-gk)

- <span id="附录fy-云原生支持"></span>[附录FY： 云原生支持](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95fy-%E4%BA%91%E5%8E%9F%E7%94%9F%E6%94%AF%E6%8C%81)
- <span id="附录fz-分布式追踪"></span>[附录FZ： 分布式追踪](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95fz-%E5%88%86%E5%B8%83%E5%BC%8F%E8%BF%BD%E8%B8%AA)
- <span id="附录ga-机器学习集成"></span>[附录GA： 机器学习集成](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95ga-%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E9%9B%86%E6%88%90)
- <span id="附录gb-自动化响应"></span>[附录GB： 自动化响应](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gb-%E8%87%AA%E5%8A%A8%E5%8C%96%E5%93%8D%E5%BA%94)
- <span id="附录gc-合规性检查"></span>[附录GC： 合规性检查](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gc-%E5%90%88%E8%A7%84%E6%80%A7%E6%A3%80%E6%9F%A5)
- <span id="附录gd-ipv6支持"></span>[附录GD： IPv6支持](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gd-ipv6%E6%94%AF%E6%8C%81)
- <span id="附录ge-隧道协议"></span>[附录GE： 隧道协议](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95ge-%E9%9A%A7%E9%81%93%E5%8D%8F%E8%AE%AE)
- <span id="附录gf-gtp-u检测器"></span>[附录GF： GTP-U检测器](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gf-gtp-u%E6%A3%80%E6%B5%8B%E5%99%A8)
- <span id="附录gg-数据丢失防护"></span>[附录GG： 数据丢失防护](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gg-%E6%95%B0%E6%8D%AE%E4%B8%A2%E5%A4%B1%E9%98%B2%E6%8A%A4)
- <span id="附录gh-蜜罐集成"></span>[附录GH： 蜜罐集成](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gh-%E8%9C%9C%E7%BD%90%E9%9B%86%E6%88%90)
- <span id="附录gi-攻击指标"></span>[附录GI： 攻击指标](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gi-%E6%94%BB%E5%87%BB%E6%8C%87%E6%A0%87)
- <span id="附录gj-威胁建模"></span>[附录GJ： 威胁建模](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gj-%E5%A8%81%E8%83%81%E5%BB%BA%E6%A8%A1)
- <span id="附录gk-持续集成"></span>[附录GK： 持续集成](/security/nids/snort3/14-appendices-fy-gk#%E9%99%84%E5%BD%95gk-%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90)

### [附录 GL–GV](./snort3/15-appendices-gl-gv)

- <span id="附录gl-持续部署"></span>[附录GL： 持续部署](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gl-%E6%8C%81%E7%BB%AD%E9%83%A8%E7%BD%B2)
- <span id="附录gm-监控和可观测性"></span>[附录GM： 监控和可观测性](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gm-%E7%9B%91%E6%8E%A7%E5%92%8C%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7)
- <span id="附录gn-安全更新机制"></span>[附录GN： 安全更新机制](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gn-%E5%AE%89%E5%85%A8%E6%9B%B4%E6%96%B0%E6%9C%BA%E5%88%B6)
- <span id="附录go-api网关集成"></span>[附录GO： API网关集成](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95go-api%E7%BD%91%E5%85%B3%E9%9B%86%E6%88%90)
- <span id="附录gp-grpc接口"></span>[附录GP： gRPC接口](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gp-grpc%E6%8E%A5%E5%8F%A3)
- <span id="附录gq-插件开发指南"></span>[附录GQ： 插件开发指南](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gq-%E6%8F%92%E4%BB%B6%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97)
- <span id="附录gr-性能调优指南"></span>[附录GR： 性能调优指南](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gr-%E6%80%A7%E8%83%BD%E8%B0%83%E4%BC%98%E6%8C%87%E5%8D%97)
- <span id="附录gs-故障排查矩阵"></span>[附录GS： 故障排查矩阵](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gs-%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E7%9F%A9%E9%98%B5)
- <span id="附录gt-安全加固"></span>[附录GT： 安全加固](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gt-%E5%AE%89%E5%85%A8%E5%8A%A0%E5%9B%BA)
- <span id="附录gu-haproxy集成"></span>[附录GU： HAProxy集成](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gu-haproxy%E9%9B%86%E6%88%90)
- <span id="附录gv-elastic-stack集成"></span>[附录GV： Elastic Stack集成](/security/nids/snort3/15-appendices-gl-gv#%E9%99%84%E5%BD%95gv-elastic-stack%E9%9B%86%E6%88%90)

### [附录 GW–HG](./snort3/16-appendices-gw-hg)

- <span id="附录gw-日志格式详解"></span>[附录GW： 日志格式详解](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95gw-%E6%97%A5%E5%BF%97%E6%A0%BC%E5%BC%8F%E8%AF%A6%E8%A7%A3)
- <span id="附录gx-协议分析器实现"></span>[附录GX： 协议分析器实现](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95gx-%E5%8D%8F%E8%AE%AE%E5%88%86%E6%9E%90%E5%99%A8%E5%AE%9E%E7%8E%B0)
- <span id="附录gy-流量生成器"></span>[附录GY： 流量生成器](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95gy-%E6%B5%81%E9%87%8F%E7%94%9F%E6%88%90%E5%99%A8)
- <span id="附录gz-基准测试"></span>[附录GZ： 基准测试](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95gz-%E5%9F%BA%E5%87%86%E6%B5%8B%E8%AF%95)
- <span id="附录ha-协议逆向工程"></span>[附录HA： 协议逆向工程](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95ha-%E5%8D%8F%E8%AE%AE%E9%80%86%E5%90%91%E5%B7%A5%E7%A8%8B)
- <span id="附录hb-加密算法实现"></span>[附录HB： 加密算法实现](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95hb-%E5%8A%A0%E5%AF%86%E7%AE%97%E6%B3%95%E5%AE%9E%E7%8E%B0)
- <span id="附录hc-正则表达式引擎"></span>[附录HC： 正则表达式引擎](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95hc-%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E5%BC%95%E6%93%8E)
- <span id="附录hd-数据结构实现"></span>[附录HD： 数据结构实现](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95hd-%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E5%AE%9E%E7%8E%B0)
- <span id="附录he-时间处理"></span>[附录HE： 时间处理](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95he-%E6%97%B6%E9%97%B4%E5%A4%84%E7%90%86)
- <span id="附录hf-网络工具函数"></span>[附录HF： 网络工具函数](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95hf-%E7%BD%91%E7%BB%9C%E5%B7%A5%E5%85%B7%E5%87%BD%E6%95%B0)
- <span id="附录hg-字符串处理"></span>[附录HG： 字符串处理](/security/nids/snort3/16-appendices-gw-hg#%E9%99%84%E5%BD%95hg-%E5%AD%97%E7%AC%A6%E4%B8%B2%E5%A4%84%E7%90%86)

### [附录 HH–HQ](./snort3/17-appendices-hh-hq)

- <span id="附录hh-位操作工具"></span>[附录HH： 位操作工具](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hh-%E4%BD%8D%E6%93%8D%E4%BD%9C%E5%B7%A5%E5%85%B7)
- <span id="附录hi-文件操作"></span>[附录HI： 文件操作](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hi-%E6%96%87%E4%BB%B6%E6%93%8D%E4%BD%9C)
- <span id="附录hj-并发工具"></span>[附录HJ： 并发工具](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hj-%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7)
- <span id="附录hk-错误处理"></span>[附录HK： 错误处理](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hk-%E9%94%99%E8%AF%AF%E5%A4%84%E7%90%86)
- <span id="附录hl-日志系统"></span>[附录HL： 日志系统](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hl-%E6%97%A5%E5%BF%97%E7%B3%BB%E7%BB%9F)
- <span id="附录hm-配置解析器"></span>[附录HM： 配置解析器](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hm-%E9%85%8D%E7%BD%AE%E8%A7%A3%E6%9E%90%E5%99%A8)
- <span id="附录hn-事件驱动框架"></span>[附录HN： 事件驱动框架](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hn-%E4%BA%8B%E4%BB%B6%E9%A9%B1%E5%8A%A8%E6%A1%86%E6%9E%B6)
- <span id="附录ho-状态机框架"></span>[附录HO： 状态机框架](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95ho-%E7%8A%B6%E6%80%81%E6%9C%BA%E6%A1%86%E6%9E%B6)
- <span id="附录hp-观察者模式"></span>[附录HP： 观察者模式](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hp-%E8%A7%82%E5%AF%9F%E8%80%85%E6%A8%A1%E5%BC%8F)
- <span id="附录hq-信号处理"></span>[附录HQ： 信号处理](/security/nids/snort3/17-appendices-hh-hq#%E9%99%84%E5%BD%95hq-%E4%BF%A1%E5%8F%B7%E5%A4%84%E7%90%86)

### [附录 HR–ID](./snort3/18-appendices-hr-id)

- <span id="附录hr-进程管理"></span>[附录HR： 进程管理](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hr-%E8%BF%9B%E7%A8%8B%E7%AE%A1%E7%90%86)
- <span id="附录hs-crc校验"></span>[附录HS： CRC校验](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hs-crc%E6%A0%A1%E9%AA%8C)
- <span id="附录ht-完整类图参考"></span>[附录HT： 完整类图参考](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95ht-%E5%AE%8C%E6%95%B4%E7%B1%BB%E5%9B%BE%E5%8F%82%E8%80%83)
- <span id="附录hu-关键数据结构映射"></span>[附录HU： 关键数据结构映射](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hu-%E5%85%B3%E9%94%AE%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E6%98%A0%E5%B0%84)
- <span id="附录hv-内存布局详解"></span>[附录HV： 内存布局详解](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hv-%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80%E8%AF%A6%E8%A7%A3)
- <span id="附录hw-函数调用序列"></span>[附录HW： 函数调用序列](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hw-%E5%87%BD%E6%95%B0%E8%B0%83%E7%94%A8%E5%BA%8F%E5%88%97)
- <span id="附录hx-配置模式参考"></span>[附录HX： 配置模式参考](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hx-%E9%85%8D%E7%BD%AE%E6%A8%A1%E5%BC%8F%E5%8F%82%E8%80%83)
- <span id="附录hy-错误消息参考"></span>[附录HY： 错误消息参考](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hy-%E9%94%99%E8%AF%AF%E6%B6%88%E6%81%AF%E5%8F%82%E8%80%83)
- <span id="附录hz-api参考速查"></span>[附录HZ： API参考速查](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95hz-api%E5%8F%82%E8%80%83%E9%80%9F%E6%9F%A5)
- <span id="附录ia-术语表续"></span>[附录IA： 术语表续](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95ia-%E6%9C%AF%E8%AF%AD%E8%A1%A8%E7%BB%AD)
- <span id="附录ib-参考资源"></span>[附录IB： 参考资源](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95ib-%E5%8F%82%E8%80%83%E8%B5%84%E6%BA%90)
- <span id="附录ic-版本历史"></span>[附录IC： 版本历史](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95ic-%E7%89%88%E6%9C%AC%E5%8E%86%E5%8F%B2)
- <span id="附录id-许可证和版权"></span>[附录ID： 许可证和版权](/security/nids/snort3/18-appendices-hr-id#%E9%99%84%E5%BD%95id-%E8%AE%B8%E5%8F%AF%E8%AF%81%E5%92%8C%E7%89%88%E6%9D%83)

### [附录 IE–IN](./snort3/19-appendices-ie-in)

- <span id="附录ie-贡献指南"></span>[附录IE： 贡献指南](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95ie-%E8%B4%A1%E7%8C%AE%E6%8C%87%E5%8D%97)
- <span id="附录if-快速命令参考"></span>[附录IF： 快速命令参考](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95if-%E5%BF%AB%E9%80%9F%E5%91%BD%E4%BB%A4%E5%8F%82%E8%80%83)
- <span id="附录ig-诊断工具"></span>[附录IG： 诊断工具](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95ig-%E8%AF%8A%E6%96%AD%E5%B7%A5%E5%85%B7)
- <span id="附录ih-安全建议"></span>[附录IH： 安全建议](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95ih-%E5%AE%89%E5%85%A8%E5%BB%BA%E8%AE%AE)
- <span id="附录ii-总结"></span>[附录II： 总结](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95ii-%E6%80%BB%E7%BB%93)
- <span id="附录ij-设计模式应用"></span>[附录IJ： 设计模式应用](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95ij-%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F%E5%BA%94%E7%94%A8)
- <span id="附录ik-并发模型详解"></span>[附录IK： 并发模型详解](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95ik-%E5%B9%B6%E5%8F%91%E6%A8%A1%E5%9E%8B%E8%AF%A6%E8%A7%A3)
- <span id="附录il-内存管理细节"></span>[附录IL： 内存管理细节](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95il-%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E7%BB%86%E8%8A%82)
- <span id="附录im-性能分析工具"></span>[附录IM： 性能分析工具](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95im-%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90%E5%B7%A5%E5%85%B7)
- <span id="附录in-网络编程接口"></span>[附录IN： 网络编程接口](/security/nids/snort3/19-appendices-ie-in#%E9%99%84%E5%BD%95in-%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%E6%8E%A5%E5%8F%A3)

### [附录 IO–IY](./snort3/20-appendices-io-iy)

- <span id="附录io-定时器实现"></span>[附录IO： 定时器实现](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95io-%E5%AE%9A%E6%97%B6%E5%99%A8%E5%AE%9E%E7%8E%B0)
- <span id="附录ip-缓存实现"></span>[附录IP： 缓存实现](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95ip-%E7%BC%93%E5%AD%98%E5%AE%9E%E7%8E%B0)
- <span id="附录iq-序列化框架"></span>[附录IQ： 序列化框架](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95iq-%E5%BA%8F%E5%88%97%E5%8C%96%E6%A1%86%E6%9E%B6)
- <span id="附录ir-插件接口定义"></span>[附录IR： 插件接口定义](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95ir-%E6%8F%92%E4%BB%B6%E6%8E%A5%E5%8F%A3%E5%AE%9A%E4%B9%89)
- <span id="附录is-单元测试框架"></span>[附录IS： 单元测试框架](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95is-%E5%8D%95%E5%85%83%E6%B5%8B%E8%AF%95%E6%A1%86%E6%9E%B6)
- <span id="附录it-基准测试框架"></span>[附录IT： 基准测试框架](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95it-%E5%9F%BA%E5%87%86%E6%B5%8B%E8%AF%95%E6%A1%86%E6%9E%B6)
- <span id="附录iu-集成测试"></span>[附录IU： 集成测试](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95iu-%E9%9B%86%E6%88%90%E6%B5%8B%E8%AF%95)
- <span id="附录iv-压力测试"></span>[附录IV： 压力测试](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95iv-%E5%8E%8B%E5%8A%9B%E6%B5%8B%E8%AF%95)
- <span id="附录iw-模糊测试"></span>[附录IW： 模糊测试](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95iw-%E6%A8%A1%E7%B3%8A%E6%B5%8B%E8%AF%95)
- <span id="附录ix-配置验证"></span>[附录IX： 配置验证](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95ix-%E9%85%8D%E7%BD%AE%E9%AA%8C%E8%AF%81)
- <span id="附录iy-日志记录系统"></span>[附录IY： 日志记录系统](/security/nids/snort3/20-appendices-io-iy#%E9%99%84%E5%BD%95iy-%E6%97%A5%E5%BF%97%E8%AE%B0%E5%BD%95%E7%B3%BB%E7%BB%9F)

### [附录 IZ–JL](./snort3/21-appendices-iz-jl)

- <span id="附录iz-审计系统"></span>[附录IZ： 审计系统](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95iz-%E5%AE%A1%E8%AE%A1%E7%B3%BB%E7%BB%9F)
- <span id="附录ja-命令行完整参考"></span>[附录JA： 命令行完整参考](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95ja-%E5%91%BD%E4%BB%A4%E8%A1%8C%E5%AE%8C%E6%95%B4%E5%8F%82%E8%80%83)
- <span id="附录jb-环境变量"></span>[附录JB： 环境变量](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jb-%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F)
- <span id="附录jc-配置文件模板"></span>[附录JC： 配置文件模板](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jc-%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E6%A8%A1%E6%9D%BF)
- <span id="附录jd-告警格式详解"></span>[附录JD： 告警格式详解](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jd-%E5%91%8A%E8%AD%A6%E6%A0%BC%E5%BC%8F%E8%AF%A6%E8%A7%A3)
- <span id="附录je-日志rotate配置"></span>[附录JE： 日志rotate配置](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95je-%E6%97%A5%E5%BF%97rotate%E9%85%8D%E7%BD%AE)
- <span id="附录jf-系统服务配置"></span>[附录JF： 系统服务配置](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jf-%E7%B3%BB%E7%BB%9F%E6%9C%8D%E5%8A%A1%E9%85%8D%E7%BD%AE)
- <span id="附录jg-性能监控"></span>[附录JG： 性能监控](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jg-%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7)
- <span id="附录jh-备份和恢复"></span>[附录JH： 备份和恢复](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jh-%E5%A4%87%E4%BB%BD%E5%92%8C%E6%81%A2%E5%A4%8D)
- <span id="附录ji-集群配置"></span>[附录JI： 集群配置](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95ji-%E9%9B%86%E7%BE%A4%E9%85%8D%E7%BD%AE)
- <span id="附录jj-最终检查清单"></span>[附录JJ： 最终检查清单](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jj-%E6%9C%80%E7%BB%88%E6%A3%80%E6%9F%A5%E6%B8%85%E5%8D%95)
- <span id="附录jk-总结"></span>[附录JK： 总结](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jk-%E6%80%BB%E7%BB%93)
- <span id="附录jl-框架接口详解"></span>[附录JL： 框架接口详解](/security/nids/snort3/21-appendices-iz-jl#%E9%99%84%E5%BD%95jl-%E6%A1%86%E6%9E%B6%E6%8E%A5%E5%8F%A3%E8%AF%A6%E8%A7%A3)

### [附录 JM–JX](./snort3/22-appendices-jm-jx)

- <span id="附录jm-核心数据结构"></span>[附录JM： 核心数据结构](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jm-%E6%A0%B8%E5%BF%83%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
- <span id="附录jn-检测引擎核心"></span>[附录JN： 检测引擎核心](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jn-%E6%A3%80%E6%B5%8B%E5%BC%95%E6%93%8E%E6%A0%B8%E5%BF%83)
- <span id="附录jo-选项评估"></span>[附录JO： 选项评估](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jo-%E9%80%89%E9%A1%B9%E8%AF%84%E4%BC%B0)
- <span id="附录jp-规则编译"></span>[附录JP： 规则编译](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jp-%E8%A7%84%E5%88%99%E7%BC%96%E8%AF%91)
- <span id="附录jq-事件系统"></span>[附录JQ： 事件系统](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jq-%E4%BA%8B%E4%BB%B6%E7%B3%BB%E7%BB%9F)
- <span id="附录jr-stream模块"></span>[附录JR： Stream模块](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jr-stream%E6%A8%A1%E5%9D%97)
- <span id="附录js-协议辅助"></span>[附录JS： 协议辅助](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95js-%E5%8D%8F%E8%AE%AE%E8%BE%85%E5%8A%A9)
- <span id="附录jt-辅助工具"></span>[附录JT： 辅助工具](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jt-%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7)
- <span id="附录ju-主程序流程"></span>[附录JU： 主程序流程](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95ju-%E4%B8%BB%E7%A8%8B%E5%BA%8F%E6%B5%81%E7%A8%8B)
- <span id="附录jv-daq接口"></span>[附录JV： DAQ接口](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jv-daq%E6%8E%A5%E5%8F%A3)
- <span id="附录jw-插件api"></span>[附录JW： 插件API](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jw-%E6%8F%92%E4%BB%B6api)
- <span id="附录jx-统计系统"></span>[附录JX： 统计系统](/security/nids/snort3/22-appendices-jm-jx#%E9%99%84%E5%BD%95jx-%E7%BB%9F%E8%AE%A1%E7%B3%BB%E7%BB%9F)

### [附录 JY–KJ](./snort3/23-appendices-jy-kj)

- <span id="附录jy-日志系统"></span>[附录JY： 日志系统](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95jy-%E6%97%A5%E5%BF%97%E7%B3%BB%E7%BB%9F)
- <span id="附录jz-过滤器"></span>[附录JZ： 过滤器](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95jz-%E8%BF%87%E6%BB%A4%E5%99%A8)
- <span id="附录ka-整理完成"></span>[附录KA： 整理完成](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95ka-%E6%95%B4%E7%90%86%E5%AE%8C%E6%88%90)
- <span id="附录kb-源文件组织"></span>[附录KB： 源文件组织](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kb-%E6%BA%90%E6%96%87%E4%BB%B6%E7%BB%84%E7%BB%87)
- <span id="附录kc-头文件依赖关系"></span>[附录KC： 头文件依赖关系](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kc-%E5%A4%B4%E6%96%87%E4%BB%B6%E4%BE%9D%E8%B5%96%E5%85%B3%E7%B3%BB)
- <span id="附录kd-编译系统"></span>[附录KD： 编译系统](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kd-%E7%BC%96%E8%AF%91%E7%B3%BB%E7%BB%9F)
- <span id="附录ke-宏定义参考"></span>[附录KE： 宏定义参考](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95ke-%E5%AE%8F%E5%AE%9A%E4%B9%89%E5%8F%82%E8%80%83)
- <span id="附录kf-常量定义"></span>[附录KF： 常量定义](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kf-%E5%B8%B8%E9%87%8F%E5%AE%9A%E4%B9%89)
- <span id="附录kg-错误码"></span>[附录KG： 错误码](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kg-%E9%94%99%E8%AF%AF%E7%A0%81)
- <span id="附录kh-完整api速查"></span>[附录KH： 完整API速查](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kh-%E5%AE%8C%E6%95%B4api%E9%80%9F%E6%9F%A5)
- <span id="附录ki-版本信息"></span>[附录KI： 版本信息](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95ki-%E7%89%88%E6%9C%AC%E4%BF%A1%E6%81%AF)
- <span id="附录kj-其他重要模块"></span>[附录KJ： 其他重要模块](/security/nids/snort3/23-appendices-jy-kj#%E9%99%84%E5%BD%95kj-%E5%85%B6%E4%BB%96%E9%87%8D%E8%A6%81%E6%A8%A1%E5%9D%97)

### [附录 KK–LB](./snort3/24-appendices-kk-lb)

- <span id="附录kk-配置文件详解"></span>[附录KK： 配置文件详解](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kk-%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E8%AF%A6%E8%A7%A3)
- <span id="附录kl-性能调优参数"></span>[附录KL： 性能调优参数](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kl-%E6%80%A7%E8%83%BD%E8%B0%83%E4%BC%98%E5%8F%82%E6%95%B0)
- <span id="附录km-安全加固清单"></span>[附录KM： 安全加固清单](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95km-%E5%AE%89%E5%85%A8%E5%8A%A0%E5%9B%BA%E6%B8%85%E5%8D%95)
- <span id="附录kn-故障排查指南"></span>[附录KN： 故障排查指南](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kn-%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E6%8C%87%E5%8D%97)
- <span id="附录ko-参考资料"></span>[附录KO： 参考资料](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95ko-%E5%8F%82%E8%80%83%E8%B5%84%E6%96%99)
- <span id="附录kp-协议处理器映射"></span>[附录KP： 协议处理器映射](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kp-%E5%8D%8F%E8%AE%AE%E5%A4%84%E7%90%86%E5%99%A8%E6%98%A0%E5%B0%84)
- <span id="附录kq-事件处理"></span>[附录KQ： 事件处理](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kq-%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86)
- <span id="附录kr-属性表"></span>[附录KR： 属性表](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kr-%E5%B1%9E%E6%80%A7%E8%A1%A8)
- <span id="附录ks-规则动作系统"></span>[附录KS： 规则动作系统](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95ks-%E8%A7%84%E5%88%99%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F)
- <span id="附录kt-规范化策略"></span>[附录KT： 规范化策略](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kt-%E8%A7%84%E8%8C%83%E5%8C%96%E7%AD%96%E7%95%A5)
- <span id="附录ku-协议识别"></span>[附录KU： 协议识别](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95ku-%E5%8D%8F%E8%AE%AE%E8%AF%86%E5%88%AB)
- <span id="附录kv-检测选项链"></span>[附录KV： 检测选项链](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kv-%E6%A3%80%E6%B5%8B%E9%80%89%E9%A1%B9%E9%93%BE)
- <span id="附录kw-正则表达式处理"></span>[附录KW： 正则表达式处理](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kw-%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E5%A4%84%E7%90%86)
- <span id="附录kx-快速模式匹配"></span>[附录KX： 快速模式匹配](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kx-%E5%BF%AB%E9%80%9F%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D)
- <span id="附录ky-分片重组"></span>[附录KY： 分片重组](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95ky-%E5%88%86%E7%89%87%E9%87%8D%E7%BB%84)
- <span id="附录kz-日志格式"></span>[附录KZ： 日志格式](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95kz-%E6%97%A5%E5%BF%97%E6%A0%BC%E5%BC%8F)
- <span id="附录la-端口列表处理"></span>[附录LA： 端口列表处理](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95la-%E7%AB%AF%E5%8F%A3%E5%88%97%E8%A1%A8%E5%A4%84%E7%90%86)
- <span id="附录lb-规则选项类型"></span>[附录LB： 规则选项类型](/security/nids/snort3/24-appendices-kk-lb#%E9%99%84%E5%BD%95lb-%E8%A7%84%E5%88%99%E9%80%89%E9%A1%B9%E7%B1%BB%E5%9E%8B)

### [附录 LC–LW](./snort3/25-appendices-lc-lw)

- <span id="附录lc-配置参数"></span>[附录LC： 配置参数](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lc-%E9%85%8D%E7%BD%AE%E5%8F%82%E6%95%B0)
- <span id="附录ld-主循环处理"></span>[附录LD： 主循环处理](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95ld-%E4%B8%BB%E5%BE%AA%E7%8E%AF%E5%A4%84%E7%90%86)
- <span id="附录le-内存管理"></span>[附录LE： 内存管理](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95le-%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86)
- <span id="附录lf-时间管理"></span>[附录LF： 时间管理](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lf-%E6%97%B6%E9%97%B4%E7%AE%A1%E7%90%86)
- <span id="附录lg-追踪调试"></span>[附录LG： 追踪调试](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lg-%E8%BF%BD%E8%B8%AA%E8%B0%83%E8%AF%95)
- <span id="附录lh-数据结构"></span>[附录LH： 数据结构](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lh-%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
- <span id="附录li-互斥锁"></span>[附录LI： 互斥锁](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95li-%E4%BA%92%E6%96%A5%E9%94%81)
- <span id="附录lj-原子操作"></span>[附录LJ： 原子操作](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lj-%E5%8E%9F%E5%AD%90%E6%93%8D%E4%BD%9C)
- <span id="附录lk-日志宏"></span>[附录LK： 日志宏](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lk-%E6%97%A5%E5%BF%97%E5%AE%8F)
- <span id="附录ll-插件注册"></span>[附录LL： 插件注册](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95ll-%E6%8F%92%E4%BB%B6%E6%B3%A8%E5%86%8C)
- <span id="附录lm-辅助工具函数"></span>[附录LM： 辅助工具函数](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lm-%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7%E5%87%BD%E6%95%B0)
- <span id="附录ln-结束标记"></span>[附录LN： 结束标记](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95ln-%E7%BB%93%E6%9D%9F%E6%A0%87%E8%AE%B0)
- <span id="附录lo-异常处理"></span>[附录LO： 异常处理](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lo-%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86)
- <span id="附录lp-配置参数表"></span>[附录LP： 配置参数表](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lp-%E9%85%8D%E7%BD%AE%E5%8F%82%E6%95%B0%E8%A1%A8)
- <span id="附录lq-数据流图"></span>[附录LQ： 数据流图](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lq-%E6%95%B0%E6%8D%AE%E6%B5%81%E5%9B%BE)
- <span id="附录lr-类继承关系"></span>[附录LR： 类继承关系](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lr-%E7%B1%BB%E7%BB%A7%E6%89%BF%E5%85%B3%E7%B3%BB)
- <span id="附录ls-宏定义索引"></span>[附录LS： 宏定义索引](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95ls-%E5%AE%8F%E5%AE%9A%E4%B9%89%E7%B4%A2%E5%BC%95)
- <span id="附录lt-版本兼容性"></span>[附录LT： 版本兼容性](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lt-%E7%89%88%E6%9C%AC%E5%85%BC%E5%AE%B9%E6%80%A7)
- <span id="附录lu-索引"></span>[附录LU： 索引](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lu-%E7%B4%A2%E5%BC%95)
- <span id="附录lv-总结"></span>[附录LV： 总结](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lv-%E6%80%BB%E7%BB%93)
- <span id="附录lw-结束"></span>[附录LW： 结束](/security/nids/snort3/25-appendices-lc-lw#%E9%99%84%E5%BD%95lw-%E7%BB%93%E6%9D%9F)

### [Codec、TCP 重组与流管理](./snort3/26-codecs-tcp-and-flow)

- <span id="附录lx-codec模块详细分析"></span>[附录LX：Codec模块详细分析](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95lx-codec%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录ly-tcp重组详细分析"></span>[附录LY：TCP重组详细分析](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95ly-tcp%E9%87%8D%E7%BB%84%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录lz-模式匹配算法详细分析"></span>[附录LZ：模式匹配算法详细分析](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95lz-%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D%E7%AE%97%E6%B3%95%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录ma-port-scan检测模块详细分析"></span>[附录MA：Port Scan检测模块详细分析](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95ma-port-scan%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mb-资源管理与性能优化"></span>[附录MB：资源管理与性能优化](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95mb-%E8%B5%84%E6%BA%90%E7%AE%A1%E7%90%86%E4%B8%8E%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96)
- <span id="附录mc-附录索引"></span>[附录MC：附录索引](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95mc-%E9%99%84%E5%BD%95%E7%B4%A2%E5%BC%95)
- <span id="附录md-文档更新记录"></span>[附录MD：文档更新记录](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95md-%E6%96%87%E6%A1%A3%E6%9B%B4%E6%96%B0%E8%AE%B0%E5%BD%95)
- <span id="附录mk-stream-tcp模块详细分析"></span>[附录MK：Stream TCP模块详细分析](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95mk-stream-tcp%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录ml-flow管理详细分析"></span>[附录ML：Flow管理详细分析](/security/nids/snort3/26-codecs-tcp-and-flow#%E9%99%84%E5%BD%95ml-flow%E7%AE%A1%E7%90%86%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)

### [Inspector、协议与规则解析](./snort3/27-inspectors-and-rules)

- <span id="附录mm-ipsaction和响应处理详细分析"></span>[附录MM：IpsAction和响应处理详细分析](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95mm-ipsaction%E5%92%8C%E5%93%8D%E5%BA%94%E5%A4%84%E7%90%86%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mn-daq接口详细分析"></span>[附录MN：DAQ接口详细分析](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95mn-daq%E6%8E%A5%E5%8F%A3%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录me-http-inspect模块详细分析"></span>[附录ME：HTTP Inspect模块详细分析](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95me-http-inspect%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mf-dns检测模块详细分析"></span>[附录MF：DNS检测模块详细分析](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95mf-dns%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mg-ssl-tls检测模块详细分析"></span>[附录MG：SSL/TLS检测模块详细分析](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95mg-ssl-tls%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mh-binder和wizard服务检测"></span>[附录MH：Binder和Wizard服务检测](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95mh-binder%E5%92%8Cwizard%E6%9C%8D%E5%8A%A1%E6%A3%80%E6%B5%8B)
- <span id="附录mz-stream-udp-icmp和ip分片重组"></span>[附录MZ：Stream UDP/ICMP和IP分片重组](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95mz-stream-udp-icmp%E5%92%8Cip%E5%88%86%E7%89%87%E9%87%8D%E7%BB%84)
- <span id="附录na-packet数据结构和codec框架"></span>[附录NA：Packet数据结构和Codec框架](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95na-packet%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E5%92%8Ccodec%E6%A1%86%E6%9E%B6)
- <span id="附录nb-appid应用识别模块"></span>[附录NB：AppId应用识别模块](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95nb-appid%E5%BA%94%E7%94%A8%E8%AF%86%E5%88%AB%E6%A8%A1%E5%9D%97)
- <span id="附录nc-规则解析系统"></span>[附录NC：规则解析系统](/security/nids/snort3/27-inspectors-and-rules#%E9%99%84%E5%BD%95nc-%E8%A7%84%E5%88%99%E8%A7%A3%E6%9E%90%E7%B3%BB%E7%BB%9F)

### [协议检测与参考索引](./snort3/28-protocols-and-reference)

- <span id="附录ms-sip检测模块详细分析"></span>[附录MS：SIP检测模块详细分析](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95ms-sip%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mt-网络inspector模块详细分析"></span>[附录MT：网络Inspector模块详细分析](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mt-%E7%BD%91%E7%BB%9Cinspector%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mu-分类阈值和检测系统"></span>[附录MU：分类阈值和检测系统](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mu-%E5%88%86%E7%B1%BB%E9%98%88%E5%80%BC%E5%92%8C%E6%A3%80%E6%B5%8B%E7%B3%BB%E7%BB%9F)
- <span id="附录mv-主线程和启动系统"></span>[附录MV：主线程和启动系统](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mv-%E4%B8%BB%E7%BA%BF%E7%A8%8B%E5%92%8C%E5%90%AF%E5%8A%A8%E7%B3%BB%E7%BB%9F)
- <span id="附录mw-alerter日志系统"></span>[附录MW：alerter日志系统](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mw-alerter%E6%97%A5%E5%BF%97%E7%B3%BB%E7%BB%9F)
- <span id="附录mx-inspector框架"></span>[附录MX：Inspector框架](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mx-inspector%E6%A1%86%E6%9E%B6)
- <span id="附录my-pubsub事件系统"></span>[附录MY：PUBSUB事件系统](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95my-pubsub%E4%BA%8B%E4%BB%B6%E7%B3%BB%E7%BB%9F)
- <span id="附录mo-dce-rpc检测模块详细分析"></span>[附录MO：DCE/RPC检测模块详细分析](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mo-dce-rpc%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mp-smtp检测模块详细分析"></span>[附录MP：SMTP检测模块详细分析](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mp-smtp%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mq-ftp-telnet检测模块详细分析"></span>[附录MQ：FTP/Telnet检测模块详细分析](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mq-ftp-telnet%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mr-ssh-pop-imap检测模块详细分析"></span>[附录MR：SSH/POP/IMAP检测模块详细分析](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mr-ssh-pop-imap%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90)
- <span id="附录mi-附录索引"></span>[附录MI：附录索引](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mi-%E9%99%84%E5%BD%95%E7%B4%A2%E5%BC%95)
- <span id="附录mj-文档更新记录"></span>[附录MJ：文档更新记录](/security/nids/snort3/28-protocols-and-reference#%E9%99%84%E5%BD%95mj-%E6%96%87%E6%A1%A3%E6%9B%B4%E6%96%B0%E8%AE%B0%E5%BD%95)


<script setup>
import LegacyAnchorRedirect from '../../.vitepress/components/LegacyAnchorRedirect.vue'
import targets from './snort3/legacy-anchors.json'
</script>

<LegacyAnchorRedirect :targets="targets" />
