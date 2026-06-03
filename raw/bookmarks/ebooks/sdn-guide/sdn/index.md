# SDN网络

SDN（Software Defined Network）是一种新的网络设计理念，即控制与转发分离、集中控制并且开放API。一般称控制器开放的API为北向接口，而控制器与底层网络之间的接口为南向接口。

## SDN架构

ONF (Open Networking Foundation)将SDN架构分为三层：
- 应用层：包括各种不同的业务应用
- 控制层：负责数据平面资源的编排、维护网络拓扑和状态信息等
- 数据层：负责数据处理、转发和状态收集

![SDN架构图](images/sdn-architecture.png)

## SDN的基本特征

SDN具有三个基本特征：
1. **控制与转发分离**：转发平面由受控转发的设备组成，转发方式以及业务逻辑由运行在分离出去的控制面上的控制应用所控制。
2. **开放API**：通过开放的南向和北向API，能够实现应用和网络的无缝集成。
3. **集中控制**：逻辑上集中的控制平面能够获得网络资源的全局信息并根据业务需求进行全局调配和优化。

## SDN优势

- 灵活性：动态调整网络设备的配置，再也不需要人工去配置每台设备
- 网络硬件简化（如白牌交换机等），只需要关注数据的处理和转发，与业务特性解耦
- 网络的自动化部署和运维、故障诊断

## SDN发展历程

- **2006年**：Martin Casado博士提出SANE，打开了集中控制解决安全问题的大门
- **2007年**：Ethane项目诞生（SDN架构和OpenFlow的前身）
- **2008年**：网络领域学者联合发表OpenFlow论文，发布第一个开源SDN控制器NOX
- **2009年**：SDN入选麻省理工科技评论的 "未来十大突破性技术"
- **2011年**：开放网络基金会ONF诞生，第一届开放网络峰会ONS成功举办
- **2012年**：Google发布B4，VMWare天价收购Nicira
- **2013年**：OpenDaylight项目诞生
- **2014年**：ONOS、P4等诞生
- **2015年**：SD-WAN成为第二个成熟的SDN应用市场
- **2017年**：鹏博士正式发布运行国内首个运营商级SD-WAN

## SDN技能图谱

![SDN技能图谱](images/Open_SDN_skill_map_ch_v2_0.jpg)

## 参考文档

- https://www.opennetworking.org/index.php
- 漫谈SDN大历史 (http://www.sdnlab.com/18601.html)
- SDN Reading List (https://www.opennetworking.org/sdn-resources/sdn-reading-list)
