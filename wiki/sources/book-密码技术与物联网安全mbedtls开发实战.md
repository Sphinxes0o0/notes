---
type: source
source-type: book
title: "密码技术与物联网安全mbedtls开发实战"
path: books/密码技术与物联网安全mbedtls开发实战.pdf
source-md5: 24203e6da3d8bf4b9dfa916559a535fe
size: 26820 KB
category: book
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 密码技术与物联网安全mbedtls开发实战

> Ingested from `books/密码技术与物联网安全mbedtls开发实战.pdf` via `lit parse` on 2026-06-04.
> Source file: 26.19 MB.

## Page 1

_(no text content on this page)_

## Page 2

物联网核心技术丛书

密码技术与物联网安全：mbedtls开发实战

徐凯 崔红鹏 编著

ISBN：978-7-111-62001-3

本书纸版由机械工业出版社于2019年出版，电子版由华章分社（北京
华章图文信息有限公司，北京奥维博世图书发行有限公司）全球范围
内制作与发行。

版权所有，侵权必究

客服热线：+ 86-10-68995265

客服信箱：service@bbbvip.com

官方网址：www.hzmedia.com.cn

新浪微博 @华章数媒

微信公众号 华章电子书（微信号：hzebook）










2

## Page 3

      目录

     推荐序一
     推荐序二
前言
 第1章 物联网安全概述
1.1  本章主要内容
1.2  物联网安全基础
  1.2.1  物联网安全与互联网安全
  1.2.2  物联网安全与密码学
1.3  密码学安全常识
  1.3.1       柯克霍夫原则
  1.3.2  Alice和Bob
  1.3.3  Eve和Mallory
1.4  mbedtls简介
  1.4.1       密码学工具箱
  1.4.2  TLS/DTLS协议
  1.4.3  X.509证书
1.5  OpenSSL简介
  1.5.1  源代码安装
  1.5.2  命令行工具简介
  1.5.3  摘要命令dgst
  1.5.4  对称加密命令enc

      3

## Page 4

1.5.5 SSL命令s  _server
1.6  本章小结
第2章  mbedtls入门
2.1  本章主要内容
2.2  mbedtls体系结构
2.3  Linux  mbedtls安装
2.3.1 安装CMake
2.3.2 使用CMake安装mbedtls
2.4  Linux  mbedtls示例
2.4.1 Base64示例
2.4.2 遍历mbedtls安全套件
2.5  Zephyr OS简介
2.6      Zephyr开发环境搭建
2.7      Zephyr硬件平台选择
2.7.1 资源介绍
2.7.2 Ubuntu中安装STLink工具
2.8      Zephyr应用示例开发
2.8.1 编写CMakeLists.txt
2.8.2 编写prj.conf
2.8.3 编写main.c
2.8.4 编译与运行
2.9  Zephyr mbedtls示例
2.9.1 Base64示例

    4

## Page 5

2.9.2  大数运算示例
2.10  本章小结
  第3章 数论基础知识
3.1   本章主要内容
3.2   素数
3.3   模运算
3.3.1  模数
3.3.2  同余
3.3.3  模算术运算
3.3.4  模逆运算
3.3.5  模重复平方
3.4   群
3.4.1     群的基本概念
3.4.2  循环群
3.4.3  子群
3.5   域
3.5.1     域的基本概念
3.5.2     有限域和素域
3.5.3  扩展域GF(2m)
3.5.4  GF(2m)加法和减法
3.5.5  GF(2m)乘法
3.5.6  GF(2m)逆操作
3.6   欧拉函数

    5

## Page 6

3.7  欧拉定理
3.8  费马小定理
3.9  离散对数
3.9.1       模算术–指数
3.9.2       模算术–对数
3.9.3  离散对数问题
3.10 本章小结
第4章  单向散列函数
4.1  本章主要内容
4.2  单向散列函数原理
4.2.1        单向散列函数性质
4.2.2        单向散列函数应用
4.3  单向散列函数的实现方法
4.3.1  MD算法家族
4.3.2  SHA算法家族
4.4  SHA256详细描述
4.4.1  预处理
4.4.2    哈希计算
4.4.3    具体示例
4.5  mbedtls单向散列应用工具

4.5.1  hello

4.5.2  generic_sum
4.6  mbedtls SHA256示例

    6

## Page 7

4.6.1   示例描述
4.6.2   示例代码
4.6.3   代码说明
4.6.4  编译与运行
4.7  本章小结
第5章  对称加密算法
5.1  本章主要内容
5.2  对称加密算法原理
5.3  分组密码模式
5.3.1  ECB（电子密码本）模式
5.3.2  CBC（密码分组链接）模式
5.3.3  CTR（计数器）模式
5.4  PKCS7填充方案
5.5  AES算法概述
5.6  AES算法详细说明
5.6.1   字节替换
5.6.2  行移位
5.6.3  列混合
5.6.4       轮密钥加法
5.6.5       轮密钥生成
5.7  AES算法动手实践
5.8  mbedtls对称加密应用工具

5.8.1  aescrypto2

    7

## Page 8

    5.8.2   crypt_and_hash
    5.9  mbedtls AES示例
    5.9.1   示例描述
    5.9.2   示例代码
    5.9.3   代码说明
    5.9.4   编译与运行
    5.10 本章小结
     第6章 消息认证码
    6.1  本章主要内容
    6.2  消息认证码原理
    6.3  消息认证码实现方法
    6.3.1   单向散列算法实现
    6.3.2   分组密码实现
    6.3.3   认证加密算法实现
    6.4  HMAC算法
    6.5  CBC-MAC和CMAC

    6.5.1   CBC-MAC

    6.5.2   CMAC
    6.6  认证加密CCM
    6.6.1   输入数据格式化
    6.6.2   认证和加密
    6.7  认证加密GCM

    6.7.1   GHASH

8

## Page 9

    6.7.2     GCTR
    6.7.3     认证和加密
    6.8   mbedtls HMAC示例
    6.8.1     示例代码
    6.8.2     代码说明
    6.8.3     编译与运行
    6.9   mbedtls GCM示例
    6.9.1     示例代码
    6.9.2     代码说明
    6.9.3     编译与运行
    6.10  本章小结
      第7章 伪随机数生成器
    7.1     本章主要内容
    7.2   随机数概述
    7.3     随机数生成器
    7.3.1     真随机数生成器
    7.3.2     伪随机数生成器
    7.4   CTR _DRBG算法
    7.4.1     参数情况
    7.4.2     生成过程
    7.5   mbedtls随机数应用工具

    7.5.1     gen_entropy

    7.5.2     gen_random_ctr_drbg

9

## Page 10

7.5.3   gen_random_havege
7.6  mbedtls CTR_DRBG示例
7.6.1   示例代码
7.6.2   代码说明
7.6.3   编译与执行
7.7  mbedtls大素数生成示例
7.7.1   示例代码
7.7.2   代码说明
7.7.3   编译与执行
7.8  mbedtls自定义熵源接口
7.9  本章小结
第8章  RSA算法
8.1  本章主要内容
8.2  RSA算法原理
8.3  RSA算法详细说明
8.4  RSA加速技术
8.4.1   中国剩余数定理
8.4.2   动手实践
8.4.3   性能对比
8.5   RSA填充方法

8.5.1   PKCS1-V1_5

8.5.2   OAEP
8.6  mbedtls RSA应用工具

            10

## Page 11

8.6.1   rsa_genkey

8.6.2   rsa_encrypt

8.6.3   rsa_decrypt
8.7   mbedtls RSA加解密示例
8.7.1   示例代码
8.7.2   代码说明
8.7.3   编译与执行
8.8   本章小结
  第9章      DH密钥协商
9.1  本章主要内容
9.2      DH密钥协商数学基础
9.3      DH密钥协商详细说明
9.3.1   DH共享参数
9.3.2   DH密钥协商
9.3.3   DH具体实践
9.3.4   DH密钥协商安全性分析
9.4   常用共享参数
9.5   mbedtls DH应用工具

9.5.1   dh_genprime

9.5.2   dh_server

9.5.3   dh_client
9.6   mbedtls DH示例
9.6.1   示例代码

            11

## Page 12

9.6.2   代码说明
9.6.3   编译与执行
9.7    本章小结
  第10章 ECDH密钥协商
10.1     本章主要内容
10.2     椭圆曲线定义
10.2.1      实数域上的椭圆曲线
10.2.2      有限域上的椭圆曲线
10.3   椭圆曲线上群操作
10.3.1   群操作几何描述
10.3.2   群操作代数描述
10.3.3   群操作动手实践
10.4   椭圆曲线离散对数问题
10.5   常用有限域上的椭圆曲线
10.6   ECDH密钥协商
10.6.1  ECDH共享参数
10.6.2  密钥协商过程
10.6.3     动手实践
10.7   mbedtls椭圆曲线模块
10.8   mbedtls ECDH示例
10.8.1     示例代码
10.8.2     代码说明
10.8.3  编译与执行

    12

## Page 13

10.9  本章小结
第11章  数字签名RSA、DSA和ECDSA
11.1         本章主要内容
11.2         数字签名原理
11.3        RSA数字签名
11.3.1   RSA数字签名详细说明
11.3.2   RSA数字签名动手实践
11.3.3   RSA签名填充方法
11.4        DSA数字签名
11.4.1   DSA数字签名详细说明
11.4.2   DSA签名动手实践
11.5  ECDSA数字签名
11.5.1   ECDSA数字签名详细说明
11.5.2   ECDSA动手实践
11.6  mbedtls数字签名应用工具

11.6.1   rsa_genkey

11.6.2   rsa_sign

11.6.3   rsa_verify
11.7  mbedtls RSA签名示例
11.7.1   示例代码
11.7.2   代码说明
11.7.3   编译与执行
11.8  mbedtls ECDSA示例

             13

## Page 14

11.8.1   示例代码
11.8.2   代码说明
11.8.3   编译与执行
11.9   本章小结
  第12章    数字证书X.509
12.1         本章主要内容
12.2         数字证书原理
12.3   X.509证书标准
12.3.1   证书结构
12.3.2   证书名称
12.3.3   证书实例
12.4   mbedtls X.509应用工具

12.4.1   cert_req

12.4.2   req_app

12.4.3   cert_write

12.4.4   cert_app
12.5   mbedtls X.509示例
12.5.1   示例代码
12.5.2   代码说明
12.5.3   编译与执行
12.6   本章小结
  第13章 mbedtls移植与性能分析
13.1   本章主要内容

             14

## Page 15

    13.2 mbedtls移植
    13.2.1   时间相关
    13.2.2   网络相关
    13.2.3   内存分配相关
    13.3 mbedtls算法性能说明
    13.3.1   单向散列函数
    13.3.2   AES算法
    13.3.3   AES-GCM和AES-CCM
    13.3.4   伪随机数生成器

    13.3.5   RSA
    13.3.6   DHE和ECDHE

    13.3.7   ECDSA
    13.3.8   ECC内存优化
    13.4 本章小结
    第14章 TLS
    14.1 本章主要内容
    14.2 TLS原理
    14.2.1   TLS设计目标
    14.2.2   TLS框架说明
    14.3 TLS密码套件
    14.4 TLS记录层协议
    14.5 密码规格变更协议
    14.6 警报协议

15

## Page 16

14.7  握手协议
14.7.1      握手协议概述
14.7.2      完整握手过程
14.7.3    会话恢复
14.8   TLS密钥交换
14.8.1   密钥交换算法对比
14.8.2   ECDHE密钥交换
14.8.3   ECDH与ECDHE的区别
14.9   TLS密钥计算
14.9.1   伪随机数生成函数
14.9.2   主密钥计算
14.9.3  KeyBlock计算
14.9.4      密钥计算示例
14.10 对称加密
14.10.1   分组加密
14.10.2   认证加密
14.10.3  对称加密示例
14.10.4  对称加密结果长度对比
14.11 mbedtls TLS应用工具
14.11.1  基础示例说明
14.11.2  启动ssl_server2
14.11.3  抓取网络数据
14.11.4  启动ssl_client2

    16

## Page 17

14.11.5  分析网络数据
14.12  构建TLS服务器
14.12.1  生成证书
14.12.2  编写HTML页面
14.12.3  启动s _server
14.12.4   验证服务器
14.13  构建TLS客户端
14.13.1   配置文件
14.13.2   示例代码
14.13.3   代码说明
14.13.4   编译与执行
14.14  本章小结
 第15章  DTLS
15.1   本章主要内容
15.2   DTLS概述
15.3   DTLS与TLS区别
15.3.1   记录层协议变化
15.3.2   握手协议变化
15.4   PSK密钥交换

15.4.1   PSK Identity
15.4.2   密钥交换详细过程
15.4.3   PSK与X.509证书传输开销比较
15.5   DTLS对称加密变化

             17

## Page 18

15.6   mbedtls DTLS应用工具
15.6.1  基础示例说明
15.6.2  启动ssl  _server2
15.6.3  抓取网络数据
15.6.4  启动ssl  _client2
15.6.5  分析网络数据
15.7    构建DTLS服务器
15.8    构建DTLS客户端
15.8.1     配置文件
15.8.2     示例代码
15.8.3     代码说明
15.8.4  编译与执行
15.9   本章小结
  第16章 CoAPs
16.1   本章主要内容
16.2   CoAPs原理
16.3   CoAPs安全说明
16.4   构建CoAPs服务器
16.4.1  服务器代码
16.4.2  代码说明
16.4.3  pom.xml文件
16.4.4  构建与执行
16.5   构建CoAPs客户端

    18

## Page 19

  16.5.1  示例代码
  16.5.2  代码说明
  16.5.3  编译与执行
16.6 本章小结
参考文献










  19

## Page 20

       推荐序一

    物联网已经成为在云计算、大数据、AI之后的又一个重要的基础
    技术，吸引了众多的产业链上下游参与者，在全球范围内呈现迅猛发
    展的态势。物联网在智能生活、智慧城市、智能制造、物流管理、健
    康医疗等众多的领域已经有多样化的应用场景和业务落地。物联网应
    用的普及和物联网技术的成熟将推动世界进入万物互联的新时代，数
    以百亿计的设备会接入网络，拥有百万亿连接的数字化物联世界即将
    到来。

物联网IoT的核心理念是把物理世界中的物体联接上网络和云
    端，通过对物的模型化抽象来提升对物的认知，通过对物的数据化分
    析来提升物的智能，从而实现物理世界的最终数字化。作为坚信这一
    理念的践行者，阿里云IoT以解决产业数字化转型升级中的痛点为出
    发点，通过全面搭建IoT基础设施，打造使能平台，完善生态系统，
    推动物联网向智能网发展。阿里云IoT已经构建了云管边端一体化的
    安全的物联网体系，在云侧推出了物联网平台和开发者平台，在管侧
    发布了国内首个LoRa城域物联网并试运营，在边缘侧发布了边缘计
    算产品，在端侧提供了适用于不同设备的物联网开源操作系统，建设
    了物联网标准化联盟，为众多的物联网芯片商、开发者、应用方案商
    等各种参与方搭建了开放的物联网市场，通过整合场景化的生态应
    用，为智能生活、智能工业、智慧城市等各行业提供数字化物联的基
    础设施，助力于物理世界的数字化。


    20

## Page 21

  数字化的物联网世界，离不开物联网安全技术的应用。随着物联
网终端设备的规模不断增大，随之而来的威胁也越来越大，各种物联
网安全事件层出不穷。针对物联网设备的攻击，如漏洞利用、数据泄
露、恶意软件、大规模DDoS攻击等造成了大量的资产损失或品牌影
响。因此，保障物联网的安全显得至关重要并且刻不容缓。从物联网
安全的角度，需要结合多种多样、多种维度的安全技术，如设备的身
份安全，设备跟云端的安全接入，各种数据链路的安全通信协议，云
端安全防护，设备运营监控等。通过对这些安全技术的广泛应用，构
建从设备、边缘、网络到云服务间的安全全链路防护体系，为数字化
的物联世界提供可靠的安全基础保障。

  本书的两位作者，正是构建安全的数字化物联网世界的践行先锋
和布道者。本书的诞生，最初是从解决实际的设备安全连接问题出
发，通过对基础密码技术的深入研究，在总结安全开发实践经验的基
础上，形成了物联网安全的重要知识积累。在数字化物联世界的理念
下，对物联网安全有着积极思考的两位作者进行了勇敢的尝试，最终
把这些内容和知识归结成书，实属不易，令人赞叹！本书的内容既涵
盖了密码学的基础数论知识，涉及大量安全密码算法和技术原理，又
包含了安全连接协议，mbedtls软件框架和安全开发实用工具，还提
供了大量的工程实践案例和指导建议。对物联网安全有兴趣的读者，
可以从本书了解到物联网安全的基础知识和应用技术；物联网安全的
开发者，也可以通过本书提供的工程移植样例以及示例代码，提升对
物联网安全协议和基础安全算法的理解；物联网设计架构师，可以通


    21

## Page 22

过本书提供的参考解析和性能分析，获得先验性的实践经验和安全指
导。正如作者在书中所言，传播知识比学习知识更有价值。真诚地希
望本书的推出，能够为物联网安全开发者赋能，让广大的物联网从业
者受益，为构建安全的数字化物联世界贡献知识与力量。

        阿里云智能IoT事业部 总经理 库伟

        2019年2月










    22

## Page 23

        推荐序二

  伴随着传感器、遥感、移动互联、大数据、云计算等技术的不断
发展，物联网在各行业得到了广泛应用。2016年，国家“十三五”规划
中指出：要积极推进云计算和物联网发展，推进物联网感知设施规划
布局，发展物联网开环应用。这显示了国家非常重视物联网基础设施
的建设和推广。

  在物联网应用高速发展的同时，物联网安全将面临严峻的挑战。
大量物联网设备将直接暴露在网络上，如果有部分设备存在安全隐
患，那么攻击者可以通过丰富的攻击手段获取用户隐私，影响用户的
财产安全甚至人身安全。在一些大规模的物联网系统中，存在安全漏
洞的主机可能会被恶意代码感染成为僵尸主机，变成僵尸网络的一部
分，对互联网上的业务造成严重影响。

  物联网安全问题主要包括设备安全、网络安全和应用安全，解决
物联网安全问题需要分步走，其中设备安全更多的是解决物理攻击造
成的影响。设备面临的物理攻击手段主要包括：版图攻击、计时攻
击、能量分析攻击、电磁攻击和故障攻击。清华大学硬件安全和密码
设备实验室在可重构计算和芯片安全领域深耕多年，形成了完善的芯
片安全解决方案，在物理攻击防护方面有丰富的知识积累，在此基础
上实现了多种主流国密和商密密码学算法，并提供了完善的密钥管理
机制和可信计算服务，可以适用于各类安全应用系统进行高速、安全



    23

## Page 24

的密码运算。

  本书两位作者的写作初衷是解决设备安全连接问题，让设备更安
全的连接网络，为推动物联网系统的网络安全和应用安全贡献力量。
本书是一本理论结合实践的物联网安全书籍，按照数论基础知识、密
码学算法、TLS/DTLS协议、物联网安全协议CoAPs的结构展开。密
码学算法部分除了理论知识，还提供了相关工具和mbedtls示例代
码，可以帮助读者更好地学习理解。本书中对密码学中较为重要的算
法进行详细描述，如认证加密算法GCM/CCM和椭圆曲线算法。在
TLS/DTLS协议相关章节中，对协议实现进行详细描述，并使用网络
抓包数据作为示例样本，按照密钥交换、密钥计算、对称加密的结构
进行展开，详细描述每个过程的具体流程。在物联网安全协议CoAPs
章节中，详细描述了物联网安全协议CoAPs的实现方法，可以在占用
较少资源的情况下为物联网设备提供安全连接服务。为了对开发者有
一定的指导意义，本书提供了丰富的示例，所有示例均基于嵌入式硬
件平台实现，示例中更加关注硬件资源的消耗情况。

  本书的两位作者作为物联网安全的探索者和实践者，为构建安全
稳定的物联网系统提供了重要的知识积累，对于物联网开发者或爱好
者而言，本书可以提供实践经验和安全指导，值得一读。

      清华大学硬件安全和密码设备实验室主任 刘雷波教授






    24

## Page 25

    前言

为何写作本书

    2015年，我和本书的另一位作者崔红鹏同在无锡物联网产业研究
院从事无线传感网方面的开发工作。那年，物联网概念虽然已被炒作
多年，但无论是技术路线还是开发手段都还处于摸索阶段。2015年，
共享单车才刚刚出现，NBIoT还在协议制定阶段，云计算也没有迎来
爆发式增长。当时工作室采购了一套带网络接口的STM32F4开发
板，我们想利用这块开发板进行一次HTTPS实验：把STM32F4开发
板作为HTTPS服务器，用浏览器作为HTTPS客户端，通过浏览器访
问开发板提供的HTTPS服务。我们想将这个嵌入式HTTPS实验作为
学习物联网安全的第一步。但万事开头难，我们始终没有完成这个嵌
入式HTTPS实验，冗长的调试信息和复杂的握手过程使我们不知所
措。在排错过程中，我们查阅了大量的资料，发现了一个又一个新名
词或概念，例如SSL、TLS、RSA加密、数字签名和椭圆曲线等，这
些密码学基础知识让我们一头雾水。除了一个又一个新名词或概念之
外，我们还了解到“RSA已经被破解了”或“哈希算法SHA1已经被破
解”这些网络传言，这些真真假假的网络传言让我们在排错过程中束
手束脚，生怕使用了不安全的算法。经过几天的努力，我们把问题总
结为“TLS握手过程的证书校验出现了问题”。由于大量基础知识的缺
失，我们并没有完成这次HTTPS实验。虽然嵌入式HTTPS实验并没


25

## Page 26

有成功，但是我们还是总结了以下经验教训：

1）相对于资源受限制的物联网终端而言，HTTPS协议非常复
杂，运行时也需要消耗大量资源。我们也开始思考是不是存在更合适
的物联网终端的安全连接方案。

2）HTTPS涉及TLS协议和密码学基础知识，这些内容都需要花
时间和精力系统学习。

3）该实验通过PolarSSL开源组件实现SSL/TLS，而SSL/TLS正是
HTTPS的安全传输层。如果要熟练掌握嵌入式HTTPS，首先需要掌
握PolarSSL。2015年，Polar更名为mbedtls，开启了物联网安全应用
的新篇章。

              当时我们还有另外一个共识：要想让物联网设备安全地联网，应
该分为两步——第一，让物联网设备方便地连接网络；第二，让物联
网设备安全地连接网络。

         为了完成“两步走”的第一步，我在2016年到2017年间编写了国内
第一本关于物联网专用协议CoAP的图书——《IoT开发实战：CoAP
卷》，这本书解决了物联网设备方便连接网络的问题。CoAP好比互
联网应用中的HTTP，而互联网应用不仅有HTTP，还有HTTPS，我想
物联网应用中也应该有CoAPs。2017年到2018年间，三大运营商——
中国电信、中国移动和中国联通在国内大力推进NBIoT网络建设，市
面上出现了各种各样的NBIoT模组。2018年3月底，阿里巴巴宣布物


26

## Page 27

    联网成为继电商、金融、物流和云计算之后的第5条“主赛道”，从
    此，物联网进入了“云连物”时代。NBIoT和云计算的脱颖而出极大地
    推动了物联网的发展，当百万亿连接不再是遥不可及的梦想时，物联
    网应用不再满足于“方便”，同时对“安全”也提出了更高的要求。

       在这种大背景下，2017年6月，我找到了本书的另一位作者崔红
    鹏，此时他已经在清华大学无锡应用技术研究院从事安全芯片的开发
    工作。我表示希望结合mbedtls写一本详细描述物联网连接安全的图
    书，我们很快达成了共识并付诸实践。我已经有编写技术图书的经
    验，我本以为上一次的成功经验可以使这次图书编写变成一次“愉快
    的写作之旅”，但是没过多久我就发现自己错了。物联网连接安全涉
    及大量密码学知识，而密码学又涉及很多数学基础知识，例如初等数
    论和抽象数学等。数学基础知识的缺失使得图书的编写过程举步维
    艰，我们花费大量的时间学习各种数论公式，甚至还研究公式或定理
    的证明过程。大学毕业之后很少有系统地学习数学理论知识的机会，
    这次特殊的自主学习经历让我们深刻体会到了数学的力量，那些经典
    的公式居然在几百年之后依然发挥着巨大的作用。


目标读者

  本书适合物联网工程师、嵌入式工程师和Web开发工程师阅读。

  ·对于物联网工程师而言，通过本书可以系统地学习物联网安全
连接的基础知识。本书借助深入浅出的示例讲解密码学算法，这些算


    27

## Page 28

法是构成物联网连接安全的利器。

  ·对于嵌入式工程师而言，本书详细讲解了mbedtls不同模块的使
用方法，这些使用方法可以帮助你构建物联网安全应用。本书还分析
各种安全算法的性能，这些分析结果将帮助你在实际项目中做出正确
的选择。

  ·对于Web开发工程师而言，通过本书可以从设备角度了解物联
网连接安全的限制条件，在这些限制条件下，物联网设备不能直接使
用互联网应用中常见的安全套件。

  总而言之，本书试图消除物联网工程师、嵌入式工程师与Web开
发工程师之间的知识鸿沟，在物联网连接安全方面达成共识。

如何阅读本书


  本书主要内容分为三部分。

  第一部分：第1~3章。第一部分是全书的基础。第1章主要讲解密
码学安全常识、mbedtls和OpenSSL相关基础知识。本书虽然以
mbedtls为核心，但在多个章节中使用了OpenSSL工具，所以在第1章
的后面部分将详细讲解OpenSSL的安装和使用方法。第2章介绍
mbedtls的安装和使用方法，由于本书的大多数硬件示例均基于Zephyr
构建，所以第2章还介绍了Zephyr的构建过程和使用方法。第3章讲解
数论基础知识，包括素数、模运算、群、域和有限域等概念，这些数


    28

## Page 29

论知识是密码学算法的基础。

  第二部分：第4~12章。第二部分主要讲解密码学6种主要密码技
术——单向散列函数、对称加密算法、消息认证码、随机数、公钥密
码和数字签名。第二部分还介绍了多种密码技术，分别是SHA256、
AES、HMAC、GCM、CCM、CTR_DRBG、RSA、DH、ECDH、
DSA、ECDSA和X.509，每章均包括原理说明和mbedtls示例代码，试
图通过理论结合实践的方式向读者展现mbedtls的全貌，其中椭圆曲
线相关的ECDH和ECDSA涉及较多数学知识，是本书较难理解的内
容。

  第三部分：第13~16章。第三部分主要包括mbedtls移植与性能分
析、TLS/DTLS/CoAPs等内容。mbedtls性能分析部分将比较各种安全
算法，这些分析结果可以帮助读者在实际项目中做出正确选择。第三
部分还介绍了TLS和DTLS协议，虽然TLS协议异常复杂且仍在不断发
展，但它是物联网连接安全的核心协议。第14章详细介绍TLS协议，
包括TLS握手协议、密钥交换、密钥计算和对称加密等，这些是本书
最复杂的内容。为了讲解CoAPs，第15章还介绍了DTLS协议，重点
介绍了DTLS协议与TLS协议之间的联系与区别。最后一章介绍了
CoAPs，CoAPs可被理解为CoAP协议与DTLS协议的结合，它将成为
物联网连接安全的主流协议。

相关资料



29

## Page 30

    本书提供多个基础示例，这些示例代码可以帮助读者更好地了解
    mbedtls。

    示例代码仓库网址为：https://github.com/iotwuxi/iot_security。

    勘误与支持


    由于作者水平有限，书中难免有错误之处，恳请读者批评指正。
    如果读者在阅读过程中发现任何问题，可通过邮件与本书的两位作者
    取得联系。

    徐凯的邮箱：xukai19871105@126.com

    崔红鹏的邮箱：xianrenqiu90@126.com

    徐凯的致谢


  感谢机械工业出版社华章公司的编辑，没有他们的策划与鼓励就
不会有这本书。

  感谢阿里巴巴阿里云IoT无锡团队的汪亮（画安）和罗日健（悠
仔），感谢他们营造了一个具有创新精神的工作环境，这种氛围激励
我不断前进；感谢一起并肩战斗的小伙伴们，他们是黄浩（先道）、
赵峰（新安）、林达（靖明）、龙超（瞻龙）、吴叶俊（安悟）、庞
海亮（胖亮）、谢娟（无鱼）、刘愿（毕险）、李迪晞（平休）、彭



    30

## Page 31

    微（师尘）、三帖（张云）；感谢阿里云IoT的两位师兄李锟（怀
    明）和杨骁（羽升）；感谢崔杨（懿侬），是他让我明白“传播知识
    比学习知识更有价值”。

      感谢我的导师江南大学君远学院院长张秋菊教授，感谢您帮助我
    开启物联网世界的大门。

      感谢我的妻子左文娟一如既往地支持我写作，感谢家人的默默付
    出与包容。


    崔红鹏的致谢


  感谢微纳电子实验室的朱敏、吴有余、张继璠和龚雪，是他们为
实验室创造了良好的工作环境和学习氛围。感谢实验室与我一起工作
的同事，他们是：杨锦江、王宇峰、孙进军、徐翔、张扣、姚俊、张
沛、李植、章俊、李康、胡永鑫、赵新成、赵启义、徐健、郭唯、贾
德存、蒋广隶。

  感谢妈妈和老婆的默默付出，是她们让我有充足的时间和精力完
成写作。在此祝家人健康快乐。










    31

## Page 32

        第1章 物联网安全概述

1.1 本章主要内容

  本章将介绍物联网安全相关基础知识。物联网安全和互联网安全
既有联系又有区别，本章开始部分将简单介绍两者的区别与联系。物
联网安全离不开密码技术，6种主要的密码技术是本书讨论的重点内
容。本章还简单介绍了mbedtls，它是本书涉及的主要安全组件，
mbedtls的具体使用方法将在其他章逐步展开。为了更好地理解密码
学基础知识，本章还介绍了OpenSSL，它是互联网安全方面的“瑞士
军刀”。










    32

## Page 33

    1.2   物联网安全基础

    1.2.1 物联网安全与互联网安全


  当前，我们生活在一个互联网的世界中，互联网应用非常普及，
并对我们的生活方式产生了深远影响。现在，我们依赖智能手机和个
人电脑进行通信、购买商品和支付账单等活动，智能手机和个人电脑
已经深入我们工作和生活的方方面面。互联网应用的繁荣离不开各种
各样的互联网协议，这些功能各异的互联网协议帮助智能手机和个人
电脑与远程服务器交换数据，这些被传输的数据可能是一张图片、一
段视频，也有可能是一个支付密码。在互联网世界中，人们在分享图
片和视频的同时，账号和密码的安全可能并没有得到足够的重视。人
们在最初设计互联网时并没有过多地考虑安全，像HTTP这样的核心
互联网协议本质上也是不安全的。

  随着互联网技术与应用的不断发展，互联网安全变得越来越重
要。现在所有连接到互联网的智能手机和个人电脑都依赖传输层安全
协议（Transport Layer Security，TLS），HTTP协议与安全传输层协
议结合形成了全新的安全协议——HTTPS。2015年左右，国内业界发
起了一场“全站HTTPS”运动，没过多久国内大多数知名网站都提供了
HTTPS服务，人们可以更加放心地使用网络购物和电子支付。但
HTTPS协议比非安全的HTTP协议更加复杂，它需要消耗更多的计算



    33

## Page 34

资源和内存资源。

  互联网应用的蓬勃发展也促进了物联网应用的发展。近些年，出
现了各种各样的物联网终端，这些物联网终端可以提供远程控制、场
景联动和环境感知等功能。相比智能手机和个人电脑，物联网终端属
于典型的受限制设备，这类设备往往无法提供充足的计算能力和内存
空间，然而物联网应用的安全同样重要。那么，这些设备是否可以像
智能手机一样使用HTTPS协议呢？本书其他章将介绍物联网如何借鉴
互联网安全的成功经验，让终端设备可以像HTTPS那样安全地连接网
络。

  物联网安全与互联网安全既有交集又有差异，由于互联网安全发
展较早，体系也更加成熟，所以物联网安全应借鉴互联网安全的成功
经验，把TLS和HTTPS这样成熟的技术“移植”到受限制终端中。










    34

## Page 35

1.2.2 物联网安全与密码学

            互联网安全离不开密码学，物联网安全也同样离不开密码学，也
就是说，密码学是互联网安全与物联网安全的基础。互联网安全更关
注算法的安全强度，而物联网安全更关注算法的执行效率。密码学是
应用数学的一个分支，密码学本身属于研究范畴，并不能直接用于工
程实践，但是密码学提供的6种主要密码技术却是工程应用的“利
器”，它们是单向散列函数、对称加密算法、消息认证码算法、公钥
密码算法、数字签名算法和伪随机数生成器。为了满足不同的安全需
求，可以将不同的密码技术进行排列组合。然而，密码技术还是不能
直接使用的，所以国内外各种组织根据密码学工具的原理定义了各种
标准，这些标准依赖密码学工具所提供的算法，把“公式”转化为“文
档”。例如，单向散列函数包括MD5标准和SHA1标准，对称加密算法
包括AES128、AES192和AES256等。为了实现物联网终端与服务器
的安全通信，还需要把这些标准规范像搭积木一样整合在一起，所
以，除了这些密码技术标准规范以外，还需要安全“框架”的支持。著
名的安全框架包括TLS和DTLS等，这些安全“框架”定义了密码技术
工具的组合方式和使用顺序。但TLS和DTLS这些框架依然处于“文
档”层面，还需要通过代码实现TLS和DTLS所规定的内容。市面上有
很多TLS/DTLS实现工具包，知名的工具包包括OpenSSL、wolfssl和
mbedtls，其中OpenSSL常用于互联网应用，而mbedtls用于物联网应
用。通过这些工具包最终才可以组成各种各样的物联网安全应用。物

    35

## Page 36

联网安全与密码技术的关系如图1-1所示。










36

## Page 37

图1-1 物联网安全与密码技术之间的关系










37

## Page 38

1.3 密码学安全常识

    在系统讲解物联网安全应用之前，先介绍一个原则和4个人物。
一个原则是柯克霍夫（Kerckhoffs）原则，4个人物分别是Alice、
Bob、Eve与Mallory。










38

## Page 39

1.3.1 柯克霍夫原则

  柯克霍夫原则（也称柯克霍夫假说）是奥古斯特·柯克霍夫
（Auguste Kerckhoffs）于19世纪提出的密码理论，具体内容如下：

  即使除密钥外的整个系统的一切都是公开的，这个密码体制也必
须是安全的。即使攻击者知道系统中的加密算法和解密算法，此系统
也必须是安全的。

  柯克霍夫原则认为，“一个安全保护系统的安全性不在于它的算
法对于对手来说是保密的，而是应在于它所选择的密钥对于对手来说
是保密的”。柯克霍夫原则告诉我们，系统的安全性依赖于密钥的安
全性，而不依赖于算法的保密性。在大多数民用场合，算法应公开并
接受公众的检验。

  《图解密码技术》[1]一书指出了以下几点密码学安全常识：

  ·不要使用保密的密码算法。

  ·使用低强度密码比不进行任何加密更加危险。

  ·任何密码算法总有被破解的一天。

  ·密码只是信息安全的一部分。

[1] 结城浩：图解密码技术[M].北京：人民邮电出版社，2015.

        39

## Page 40

1.3.2 Alice和Bob

   为了方便描述物联网安全应用场景，本书依然沿用密码学中的两
个重要人物Alice和Bob，通过Alice和Bob说明各种不同的应用场景。
Alice和Bob只是信息交互的参与者，在物联网领域，Alice和Bob可能
只是两个物联网终端的简称。Alice和Bob总是在不安全的通道中传递
信息，并试图通过各种各样的密码技术工具保证信息的安全性。本书
中，Alice使用一个女孩头像，而Bob使用一个男孩头像，如图1-2所
示。Alice和Bob都非常善良，绝不会伪造或篡改消息。










    图1-2 Alice和Bob










    40

## Page 41

1.3.3 Eve和Mallory

由于Alice和Bob的信息交互是在不安全的通道中传输的，所以交
互信息可能被窃听或攻击。在传统密码学经典教材中，窃听者一般被
称为Eve，主动攻击者被称为Mallory。Alice、Bob、Mallory和Eve的
关系如图1-3所示。










图1-3 Alice、Bob、Mallory和Eve的关系









41

## Page 42

1.4 mbedtls简介

     mbedtls使开发人员可以非常轻松地在嵌入式产品中加入物联网
安全功能。相比于OpenSSL这样的工具，mbedtls小巧灵活且易于使
用。mbedtls具有多种多样的配置选项，这些配置选项可以帮助开发
人员根据实际情况灵活地裁剪代码，降低对具体硬件平台的资源消
耗。mbedtls提供的安全加密组件相对独立，开发者可以通过单个配
置文件把单个功能加入应用中。另外，它还包括一个完整的抽象层实
现，通过这个抽象层可提高代码的复用程度，降低开发难度。除了这
些强大的功能之外，mbedtls还包括众多经过精心设计的测试用例，
这些测试用例保证了mbedtls的稳定性和可靠性。总之，mbedtls足够
小巧灵活，完全可以做到“开箱即用”。

    从功能角度来看，mbedtls主要分为以下3个部分：

    1）密码学工具箱实现。

    2）X.509证书处理实现。

    3）TLS/DTLS协议实现。









    42

## Page 43

1.4.1 密码学工具箱

  mbedtls的密码学工具箱部分具有针对对称加密算法、单向散列
（又称消息摘要）和公钥加密的抽象层实现。另外，mbedtls还包含
多个基于标准的随机数生成器和一个可自定义的熵池。所有的安全算
法均以独立模块存在，任何一个模块都可以与其他模块解耦。这种轻
耦合的设计方法便于用户对mbedtls进行裁剪，用户可以直接根据需
求选取相应的头文件和源代码文件，并将其放入项目中。

1.对称加密算法

  对称加密抽象层提供了对称加密和解密功能。它针对不同算法支
持不同的加密模式，主要包括电子密码本（ECB）、密码块链接
（CBC）、计数器模式（CTR）和密码反馈（CFB）等模式。mbedtls
不仅提供AES、Blowfish和Camellia等最常用的算法，还提供DES和
RC4等老旧或已弃用的算法。

2.单向散列与消息认证码算法

  mbedtls针对单向散列算法提供了消息摘要抽象层，可提供单向
散列功能和消息认证码功能（HMAC）。mbedtls不仅为SHA256、
SHA512和RIPEMD-160等最常用的算法提供支持，还支持MD2、
MD4、MD5和SHA1等老旧或已弃用的算法。


    43

## Page 44

3.公钥算法与数字签名

  公钥加密算法可搭配RSA算法或椭圆曲线算法，mbedtls在这些
算法的基础上提供公钥算法抽象层。mbedtls公钥算法部分还提供多
种密钥协商算法，例如Diffie-Hellman密钥协商算法（DH）和椭圆曲
线密钥协商算法（ECDH）。另外，它也提供多种数字签名方法，例
如RSA签名和椭圆曲线数字签名（ECDSA）。

4.随机数生成器

  关于随机数生成器，mbedtls不但提供了熵池，还提供了符合
CTR-DRBG与HMAC-DRBG标准的随机数生成器。mbedtls的熵池具
有很强的灵活性，熵池既可从标准源收集也可以由应用程序提供。










    44

## Page 45

1.4.2 TLS/DTLS协议

   mbedtls提供TLS/DTLS客户端和服务器功能。mbedtls为当前所有
的SSL和TLS/DTLS标准提供客户端和服务器端支持，这些标准包括
SSL 3版本、TLS 1.0版本、TLS 1.1版本和TLS 1.2版本。mbedtls还支
持大多数标准化协议扩展，如服务器名称指示（SNI）和会话票证。
mbedtls支持常用的密钥交换方法和130多种不同的标准化密码套件。










    45

## Page 46

1.4.3 X.509证书

SSL/TLS身份验证和一些其他协议都依赖X.509证书处理功能。
mbedtls为X.509证书提供以下支持：

·X.509证书解析

·X.509证书吊销列表解析

·X.509（RSA/ECDSA）私钥解析

·X.509证书验证

另外，mbedtls还可以签发或创建证书，例如：

·X.509证书生成

·X.509（RSA/ECDSA）私钥生成

·X.509证书请求解析

·X.509证书请求生成










46

## Page 47

1.5 OpenSSL简介

  OpenSSL是包含安全套接字层和传输层安全协议的开源软件库，
它几乎成为安全领域的事实标准，大部分的服务器和客户端都使用
OpenSSL，一些硬件加密算法的实现通常也需要使用OpenSSL的命令
行工具进行验证。OpenSSL在本书中将作为辅助工具对密码学算法以
及TLS/DTLS协议进行验证。本节剩余部分将描述OpenSSL的安装过
程及多种命令行工具的使用方法。










    47

## Page 48

1.5.1 源代码安装

虽然大多数发行版Linux系统中已经默认安装了OpenSSL，但为
了统一环境，本节将描述如何在Ubuntu系统中以源码方式安装
OpenSSL的指定版本。本节以OpenSSL 1.1.1版本为准。OpenSSL安装
过程如下：




# 克隆OpenSSL代码到本地
$ git clone https://github.com/openssl/openssl
# 切换到 1.1.1 分支
$ git checkout OpenSSL _1
# 配置工程，指定安装路径
$ ./config
# 编译
$ make
# 安装
$ sudo make install
$ sudo ldconfig



安装成功后可以通过openssl version命令验证安装是否成功。



# 查看安装版本
$ openssl version
OpenSSL 1.1.1 11 Sep 2018










48

## Page 49

1.5.2 命令行工具简介

      OpenSSL命令行工具分为3部分，分别为标准命令、摘要命令和
加密命令。可以通过help命令查看OpenSSL支持的所有命令。



    $ openssl help
    # 输出内容
    Standard commands
    asn1parse        ca            ciphers        cms
    crl              crl2pkcs7     dgst           dhparam
    dsa              dsaparam      ec             ecparam
    # 省略部分输出
    Message Digest commands (see the `dgst' command for more details)
    blake2b512       blake2s256    gost           md4
    md5              mdc2          rmd160         sha1
    sha224           sha256        sha3-224       sha3-256
    sha3-384         sha3-512      sha384         sha512
    # 省略部分输出
    Cipher commands (see the `enc' command for more details)
    aes-128-cbc     aes-128-ecb     aes-192-cbc    aes-192-ecb
    aes-256-cbc     aes-256-ecb     aria-128-cbc   aria-128-cfb
    aria-128-cfb1   aria-128-cfb8   aria-128-ctr   aria-128-ecb
    # 省略部分输出










                                    49

## Page 50

1.5.3 摘要命令dgst

通过openssl dgst-help可以查看dgst命令的参数信息，也可以使用
man dgst命令查看具体的使用方法。以下代码使用SHA256算法对字
符串“abc”计算消息摘要。


# 准备测试样本，并写入file.txt文件中
$ echo -n abc > file.txt
# 计算消息摘要
$ openssl dgst -sha256 -hex file.txt
SHA256(file.txt)= ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad










50

## Page 51

1.5.4 对称加密命令enc

     目前OpenSSL版本支持多种对称加密算法，示例中将使用AES-
128-CBC算法对明文“CBC has been the most commonly used mode of
operation.”进行加密，加密过程默认使用PKCS#7进行填充，密钥
为“06a9214036b8a15b512e03d534120006”，初始化向量IV
为“3dafba429d9eb430b422da802c9fac41”。加解密过程如下，openssl
enc命令描述如表1-1所示。



    # 准备测试样本
    $ echo -n CBC has been the most commonly used mode of operation. > file.txt
    # 执行AES-128-CBC加密
    $ openssl enc -aes-128-cbc -e -in file.txt -out file.enc -K 06a9214036b8a15b512e03d534120006 -iv 3dafba429d9eb430b422da802c9fac41
    # 查看加密结果
    $ hexdump -C file.enc
    00000000 4d df 90 12 d7 b3 89 87 45 a1 ed 98 60 eb 0f a2 |M.......E...`...|
    00000010 fd 2b bd 80 d2 71 90 d7 2a 2f 24 0c 8f 37 2a 27 |.+...q..*/$..7*'|
    00000020 63 74 62 96 dd c2 bf ce 7c 25 2b 6c d7 dd 4b a8 |ctb.....|%+l..K.|
    00000030 57 7e 09 6d bd 80 24 c8 b4 c5 a1 16 0c a2 d3 f9 |W~.m..$.........|
    00000040
    # 执行AES-128-CBC解密
    $ openssl enc -aes-128-cbc -d -in file.enc -out file.dec -K 06a9214036b8a15b512e03d534120006 -iv 3dafba429d9eb430b422da802c9fac41
    # 查看解密结果
    $ cat file.dec
    CBC has been the most commonly used mode of operation.



    表1-1 openssl enc命令参数描述










    51

## Page 52

1.5.5 SSL命令s_server

s_server是OpenSSL提供的SSL工具，该工具可用来搭建
TLS/DTLS服务器，用于测试和调试TLS/DTLS客户端。s_server命令
行参数很多，如表1-2所示。可以通过openssl s_server-help进行查看，
同样也可以通过man s_server进行查看。

    表1-2    openssl s_server命令参数描述









$ man s_server
# 输出内容
NAME
openssl-s_server, s_server - SSL/TLS server program
SYNOPSIS
openssl s_server [-help] [-port +int] [-accept val] [-unix val] [-4] [-6]
[-unlink] [-context val] [-verify int] [-Verify int] [-cert infile]
[-nameopt val] [-naccept +int] [-serverinfo val] [-certform PEM|DER]
[-key infile] [-keyform format] [-pass val] [-dcert infile]
[-dcertform PEM|DER] [-dkey infile] [-dkeyform PEM|DER] [-dpass val]
[-nbio_test] [-crlf] [-debug] [-msg] [-msgfile outfile] [-state]
// 省略部分内容

本节将通过一个示例说明s_server工具使用方法，示例中将使用
命令行工具s_server搭建一个TLS服务器，然后使用浏览器连接该TLS
服务器。

1.搭建TLS服务器

    52

## Page 53

# 进入证书及HTML文件所在路径
$ cd 14_tls/tls_server
# 运行TLS 服务器，等待客户端连接
$ openssl s_server --state -cert srv_cert.pem -key srv_privkey.pem -CAfile ca_cert.pem -port 443 -cipher ECDHE-ECDSA-AES256-GCM-SHA384 -WWW ./



2.浏览器访问

打开火狐浏览器，在网址栏输入https://localhost/index.html。由于
服务器使用的是自签名证书，需要将证书添加到信任列表才能继续访
问，依次单击【高级】【添加例外】【确认安全例外】即可，添加例
外过程如图1-4所示。










53

## Page 54

图1-4 添加例外

完成上述设置后，看到如图1-5所示页面，则表示HTTPS服务器
访问成功。










图1-5 服务器访问成功

连接成功后，服务器控制台会输出握手过程。



SSL_accept:before SSL initialization
SSL_accept:before SSL initialization
SSL_accept:SSLv3/TLS read client hello
SSL_accept:SSLv3/TLS write server hello
SSL_accept:SSLv3/TLS write certificate


54

## Page 55

SSL_accept:SSLv3/TLS write key exchange
SSL_accept:SSLv3/TLS write server done
SSL_accept:SSLv3/TLS write server done
SSL_accept:SSLv3/TLS read client key exchange
SSL_accept:SSLv3/TLS read change cipher spec
SSL_accept:SSLv3/TLS read finished
SSL_accept:SSLv3/TLS write session ticket
SSL_accept:SSLv3/TLS write change cipher spec
SSL_accept:SSLv3/TLS write finished
FILE:index.html










55

## Page 56

1.6 本章小结

  物联网安全需要借鉴互联网安全的成熟经验，但绝不能生搬硬
套。从柯克霍夫原则可知，密码系统的安全取决于密钥的安全而不是
算法的安全，对于一般应用来说选择一个保密的算法往往得不偿失。
密码学涉及非常多的数学知识，个人或公司一般很难独立开发新的密
码学算法，建议在物联网安全应用中选择已有的安全算法。本章简单
介绍了mbedtls和OpenSSL，OpenSSL是后续章的辅助工具，而
mbedtls是后续章的主要安全工具。










    56

## Page 57

    第2章   mbedtls入门

2.1 本章主要内容

      本章将首先介绍如何在Linux平台通过CMake工具安装mbedtls。
CMake是一种近几年较为流行的C/C++应用程序构建工具，比
Makefile脚本CMake工具简单且易学。mbedtls提供多个实用的命令行
工具，例如SSL客户端与服务端工具、X.509证书生成工具等。除了
这些工具之外，mbedtls还包括多个动态或静态链接库——mbedtls、
mbedx509和mbedcrypto，通过这些扩展库可实现各种各样的物联网安
全功能。虽然在Linux平台使用mbedtls已经具有足够的代表性，但本
章还将介绍如何在Zephyr平台使用mbedtls。Zephyr是由Linux软件基
金会主持开发的新一代物联网操作系统，Zephyr已经支持多种嵌入式
平台，并包含了网络与安全套件，mbedtls就是Zephyr操作系统支持的
安全套件。在Zephyr操作系统的帮助下，基于mbedtls的物联网安全应
用可以运行于大多数嵌入式平台上。










57

## Page 58

2.2 mbedtls体系结构

  mbedtls是一款采用Apache 2.0许可证协议开源软件加密库，使用
标准C语言编写，采用独立的模块化设计，以大大降低模块之间的耦
合。从功能上来看，mbedtls主要包括密码学算法、X.509证书、
TLS/DTLS协议3个组成部分。mbedtls非常适合于嵌入式系统，在嵌
入式系统中可作为OpenSSL的替代者。相比OpenSSL，mbedtls代码更
加简洁，API简单、直观且易于理解。除此之外，mbedtls采用模块化
设计，使用宏定义的方式将平台依赖代码进行隔离，若用户将
mbedtls移植到新的平台运行，只需修改相关宏定义并添加平台依赖
相关的代码即可。mbedtls体系结构如图2-1所示。本章剩余部分将介
绍mbedtls的安装方法，以及如何构建mbedtls应用。










    58

## Page 59

图2-1 mbedtls体系结构










59

## Page 60

2.3 Linux mbedtls安装

                        本节将介绍如何在Linux平台安装mbedtls。在mbedtls官方代码仓
库中介绍了至少4种不同的安装方法：yotta、Make、CMake和
Microsoft Visual Studio（Visual Studio 6或Visual Studio 2010）。本节
主要介绍CMake安装方法，相较于其他方法，CMake构建工具更加简
单易用。CMake工具是一个跨平台的安装（编译）工具，使用简单的
脚本语句来描述编译与安装过程。CMake不能直接输出可执行文件，
但是它能够输出各种各样的makefile脚本，然后再通过makefile脚本构
建可执行文件。CMake的结构化文档名为CMakeLists.txt，一个CMake
工程中总包含一个CMakeLists.txt。










60

## Page 61

    2.3.1 安装CMake

          在Linux正确构建mbedtls开发环境之前，需要在Linux中安装合适
    版本的CMake工具。在Debian/Ubuntu系统中可通过apt-get工具从中心
    软件仓库中获取并安装CMake。在控制台中输入以下指令便可完成
    CMake的安装。



    $ sudo apt-get update
    $ sudo apt-get install cmake



     但中心软件仓库中的CMake版本一般较低，可能无法满足需求。
若遇到版本问题时可前往CMake官网下载合适版本。下面以v3.8.2版
本为例，说明如何安装较新版本的CMake工具。本节把CMake工具安
装至{用户目录}/opt/cmake路径下，为了能够正确使用CMake工具，
还需要把CMake工具的具体安装路径写入环境变量中。安装CMake的
具体过程如下：




    # 新建CMake安装文件夹
    $ mkdir –p $HOME/opt/cmake && cd $HOME/opt/cmake
    # 通过wget指令获取cmake-v3.8.2版本安装包
    $ wget https://cmake.org/files/v3.8/cmake-3.8.2-Linux-x86_64.sh
    # 执行CMake安装过程
    $ yes | sh cmake-3.8.2-Linux-x86_64.sh | cat
    # 在.bashrc文件最后增加一行
    $ echo "export PATH=$PWD/cmake-3.8.2-Linux-x86_64/bin:\$PATH" >> $HOME/.bashrc
    # 环境变量生效
    $ source ~/.bashrc



            CMake工具安装完成之后，可通过查看当前版本编号的方式验证
    该工具是否正确安装。在控制台中输入“cmake–version”命令即可验证


    61

## Page 62

当前版本编号。如果CMake安装正确，可获得类似以下输出：



# 查看cmake版本信息
$ cmake –version
# 输出内容
cmake version 3.8.2
CMake suite maintained and supported by Kitware (kitware.com/cmake).










62

## Page 63

2.3.2 使用CMake安装mbedtls

  完成CMake工具安装之后可从GitHub获取mbedtls的最新源代
码。与其他优秀的开源软件一样，mbedtls同样托管于GitHub
——https://github.com/ARMmbed/mbedtls.git。截至目前，mbedtls已经
推出多个版本，本书以mbedtls-2.12.0版本为例说明mbedtls的安装过
程。

1.获取mbedtls源代码

  本节中mbedtls的源代码将被克隆至{用户目录}/repo/mbedtls文件
夹。

# 新建repo文件夹
$ mkdir -p ~/repo
# 克隆mbedtls源代码
$ git clone https://github.com/ARMmbed/mbedtls.git

2.切换到某个发布分支

  由于mbedtls仍处于持续更新阶段，已知Bug被修复，新的特性与
功能被不断添加到master分支中，建议在实际使用时以某个发布版本
为主。本节以mbedtls-2.12.0分支为例，通过checkout命令切换至
mbedtls-2.12.0分支。

$ git checkout -b mbedtls-2.12.0 origin/mbedtls-2.12.0


63

## Page 64

  通过checkout命令可检验出本地或远程分支，以上指令将检验出
远程仓库名为mbedtls-2.12.0分支，并在本地也创建一个同名分支
mbedtls-2.12.0。

3.重要文件与目录说明

 mbedtls源代码中包含多个重要文件或目录，其中README.md文
档详细描述了mbedtls的安装步骤，programs目录包含了多组示例代码
和应用工具。mbedtls源代码中各文件或目录的主要功能如表2-1所
示。

    表2-1     mbedtls重要文件与目录










4.编译并安装mbedtls

  完成分支切换之后，再通过cmake命令生成makefile脚本，并通
过make install命令安装mbedlts。

# 进入mbedlts源代码目录
$ cd $HOME/repo/mbedtls
# 生成makefile文件，启用生成动态链接库选项
$ cmake -DUSE_SHARED_MBEDTLS_LIBRARY=On .

    64

## Page 65

      # 编译并安装
      $ make
      $ sudo make install
      $ sudo ldconfig

   1）-DUSE_SHARED_MBEDTLS_LIBRARY=On参数用于配置动
态链接库选项，把USE_SHARED_MBEDTLS_LIBRARY设置为On
时，最终将编译获得mbedtls、mbedx509和mbedcrypto扩展库。默认
情况下这些扩展库将被安装至/usr/local/lib目录中。

   2）使用cmake命令时，请不要忘记cmake指令最后的“.”，该“.”用
于指定CMakeLists.txt的位置。观察mbedtls源代码目录可以发现，
CMakeLists.txt文件位于mbedtls源代码根目录下。

      3）执行make install命令之后，多个mbedtls工具将会被安装
    到/usr/local/bin/目录中，这些工具包括：hello、dh_client、
    dh_server、rsa_sign和rsa_verify等。

    5.设置环境变量

      在用户目录.bashrc文件末尾增加MBEDTLS_BASE参数，修改完
    成后在控制台执行source$HOME/.bashrc，该指令可使新增的环境变
    量立即生效。

      $ echo "export MBEDTLS_BASE=<mbedtls 源代码仓库安装路径>" >> $HOME/.bashrc
      $ source $HOME/.bashrc

    6.必要的验证工作


      65

## Page 66

    安装完成之后可使用某个mbedtls工具验证其是否安装成功。在
    控制台中输入hello将获得以下输出。



    $ hello
    MD5('Hello, world!') = 6cd3556deb0da54bca060b4c39479839




      mbedtls自带的hello工具只是一个验证性工具，该工具把字符
串“Hello,world!”输入到MD5算法中，并把计算结果输出到控制台
中。MD5算法是一种常见的单向散列算法，除了MD5算法之外，
mbedtls还支持SHA系列单向散列算法。hello工具的具体实现可参考
{mbedtls代码仓库}\programs\hash目录中的hello.c。由于篇幅限制，代
码清单2-1中的hello.c内容略有删减。

      代码清单2-1 hello.c



    #include <stdio.h>
    #include "mbedtls/config.h"
    #include "mbedtls/md5.h"
    #define mbedtls_printf  printf
    int main( void )
    {
     int i;
     unsigned char digest[16];
     char str[] = "Hello, world!";
     mbedtls_printf( "\n MD5('%s') = ", str );
     mbedtls_md5( (unsigned char *) str, 13, digest );
     for( i = 0; i < 16; i++ )
     mbedtls_printf( "%02x", digest[i] );
     mbedtls_printf( "\n" );
     return( 0 );
    }



    hello工具使用CMake工具构建。在hello.c同级目录中包含一个
    CMakeLists.txt文件，CMakeLists.txt文件的主要内容如下：



    add_executable(hello hello.c)
    target_link_libraries(hello mbedtls)


     66

## Page 67

   在CMake构建规则中，add_executable函数用于指定可执行文件
名称，并添加相应的源文件，此处可执行文件名为hello，相应的源文
件为hello.c。另外，target_link_libraries函数用于添加相应的库文件，
此处库文件为libmbedtls.so。










    67

## Page 68

2.4 Linux mbedtls示例

  本节将通过两个示例说明如何在Linux平台构建mbedtls编写示
例。第1个示例通过一个Base64示例说明如何使用CMake工具构建
mbedtls应用。第2个示例将遍历mbedtls的所支持的安全套件，除了遍
历安全套件之外，该示例还将通过修改mbedtls配置文件的方法，裁
剪不必要的安全套件。

  注意：由于篇幅限制，示例代码中只给出部分内容，具体示例代
码可在本书代码仓库中查看，本章示例位于02_start/linux文件夹下。










    68

## Page 69

2.4.1 Base64示例

  Base64算法是一种基于64个字符的编码算法，它是一种以任意8
位字节序列组合的描述形式，这种描述形式不易被人直接识别。
Base64算法是一种可以把非ASCII编码数据转化为ASCII编码数据的
方法。经过Base64编码之后的数据长度会比原始数据长度增加1/3。
除此之外Base64编码算法还包括填充规则，编码之后的输出结果总是
4字节的整数倍。与Base64编码算法类似的算法还有Base32编码算法
和Base16编码算法，这些算法的详细说明可参考标准文件“RFC 4648
The Base16，Base32，and Base64 Data Encodings”。在该标准文件
中，给出了3组Base64编码与解码样本数据，这些样本数据如表2-2所
示。

        表2-2 Base64编码与解码样本数据










  虽然经过Base64编码之后的结果不能被直接识别，但是Base64并
不是一种加密/解密算法，Base64仅仅是一种编码算法，它输出的结
果并没有任何“保密性”。mbedtls中也包括Base64的具体实现，下面通

        69

## Page 70

过一个示例说明如何在Linux平台编写一个简单的mbedtls示例。

1.示例代码

      示例的测试样本来自rfc3548，被编码的数据为一个字符数组，
编码的结果为字符串形式的“FPucA9l+”。在输入数据中0xfb、0x9c、
0xd9和0x7e并不能通过ASCII编码表示，但是输出结果却可通过
ASCII编码表示。Base64示例如代码清单2-2所示。

      代码清单2-2 Base64示例代码



    #include <stdio.h>
    #include <string.h>
    #include <stdint.h>
    #include "mbedtls/base64.h"
    #define mbedtls_printf     printf
    // 省略部分中间代码
    int main(void)
    {
     size_t len;
     uint8_t rst[512];
     len = sizeof(msg);
     dump_buf("\n base64 message: ", msg, len);
     mbedtls_base64_encode(rst, sizeof(rst), &len, msg, len);
     mbedtls_printf(" base64 encode : %s\n", rst);
     mbedtls_base64_decode(rst, sizeof(rst), &len, rst, len);
     dump_buf(" base64 decode : ", rst, len);
     printf("\n");
     return 0;
    }



    示例中所使用接口的具体描述如表2-3所示。

     表2-3 Base64示例相关接口描述








     70

## Page 71

2.编写CMakeLists.txt

为了在Linux平台上构建一个可执行程序，还需要编写一个
CMakeLists.txt文件，具体内容如代码清单2-3所示。

代码清单2-3     CMakeLists.txt文件

cmake_minimum_required(VERSION 3.8.2)①
project("Base64")②
include_directories(./ $ENV{MBEDTLS_BASE}/include)③
aux_source_directory($ENV{MBEDTLS_BASE}/library MBEDTLS_SOURCES)④
set(SOURCES ⑤
    ${CMAKE_CURRENT_LIST_DIR}/base64.c
    ${MBEDTLS_SOURCES})
add_executable(base64 ${SOURCES})⑥

1）设置CMake最低版本限制；

2）设置CMake工程名称为Base64；

3）通过include_directories函数指定mbedtls头文件路径，此处
mbedtls头文件路径位于环境变量$ENV{MBEDTLS_BASE}中；

4）添加mbedtls源文件到MBEDTLS_SOURCES变量中，此处通
过aux_source               _directory函数找出mbedtls library中所有C文件，并把这
些C文件路径输出至MBEDTLS_SOURCES变量中；

5）通过set函数定义一个名为SOURCES的变量，该变量包含所
有mbedtls源文件以及示例代码base64.c；

6）定义可执行文件名为base64，该可执行文件依赖SOURCES变


    71

## Page 72

量。

3.编译与执行

  编译与执行过程如下：




# 进入示例所在路径
$ cd 02_start/linux/base64
# 新建一个build文件夹，用于保存临时文件
$ mkdir –p build & cd build
# 生成makefile文件
$ cmake ..
$ make
# 执行示例
$  ./base64
   base64 message: 14 fb 9c 03 d9 7e
   base64 encode : FPucA9l+
   base64 decode : 14 fb 9c 03 d9 7e




   从输出的结果可以看出，一组不能被ASCII编码的数据被转化为
可以完全被ASCII编码的字符串“FPucA9l+”。










   72

## Page 73

    2.4.2 遍历mbedtls安全套件

   虽然Base64示例相对简单，但是已经展现了使用mbedtls构建应
用的基本步骤。经过一个简单的示例之后，我们适当提高难度实现一
个更为复杂的示例，在这个示例中将遍历mbedtls所支持的安全套
件。mbedtls支持很多常用的安全套件，但对于物联网嵌入式终端来
说，过多的安全套件将会占用更多的资源，另外有些安全套件由于种
种历史原因也不会在物联网领域流行。mbedtls可通过配置文件裁剪
一些不必要的安全套件，这样可大大缩小mbedtls所占用的代码空
间。在mbedtls中可通过mbedtls_ssl_list_ciphersuites函数遍历所有用于
TLS/DTLS通信的安全套件。

   例如，TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384安
全套件如图2-2所示。该密码套件具体含义如下：

    ·密钥协商算法ECDHE

    ·身份认证算法ECDSA

    ·对称加密算法AES_256

    ·消息认证算法GCM

    ·伪随机数算法SHA384



    73

## Page 74

        图2-2 安全套件名称构成方式

    虽然安全套件名称不能表示所有参数，但是可以指示其中的重要
    参数。当前已经有超过300种安全套件被官方定义，可访问IANA的
    TLS官方页面[1]获得完整列表。

    1.示例代码

    遍历mbedtls安全套件的代码，如代码清单2-4所示。

    代码清单2-4 遍历mbedtls安全套件示例



    #include <stdio.h>
    #include "mbedtls/ssl.h"
    int main( void )
    {
     int index = 1;
     const int *list;
     const char *name;
     mbedtls_printf("\n Available Ciphersuite:\n\n");
     list = mbedtls_ssl_list_ciphersuites();①
     for(; *list; list++) {
      name = mbedtls_ssl_get_ciphersuite_name(*list);②
      mbedtls_printf(" [%03d] %s\n", index++, name);
     }
     mbedtls_printf("\n");
     return 0;
    }



     1）mbedtls _ciphersuites将返回全局数组
        _ssl_list
supported_ciphersuites，该数组定义了所有被mbedtls支持的安全套


      74

## Page 75

    件；

      2）获得安全套件名称，例如TLS-ECDHE-ECDSA-WITH-AES-
    256-GCM-SHA384或TLS-ECDHE-RSA-WITH-AES-256-GCM-
    SHA384。

    2.编写CMakeLists.txt

为了在Linux平台上构建一个可执行程序，还需要编写一个
    CMakeLists.txt文件，这个CMakeLists.txt构建文件与上一个Base64示
    例的构建文件非常相似，只是可执行文件名称和依赖C文件名称发生
    了变化，具体内容如代码清单2-5所示。

      代码清单2-5 CMakeLists.txt文件


    cmake_minimum_required(VERSION 3.8.2)①
    project("Ciphersuite-list")②
    include_directories(./ $ENV{MBEDTLS_BASE}/include)③
    aux_source_directory($ENV{MBEDTLS_BASE}/library MBEDTLS_SOURCES)④
    set(SOURCES⑤
    ${CMAKE_CURRENT_LIST_DIR}/ciphersuite-list.c
    ${MBEDTLS_SOURCES})
    add_executable(ciphersuite-list ${SOURCES})⑥

    1）设置CMake最低版本限制；

    2）设置CMake工程名称为Ciphersuite-list；

    3）设置mbedtls头文件路径；

    4）添加mbedtls源文件输出到MBEDTLS_SOURCES变量中；



    75

## Page 76

    5）通过set函数定义一个名为SOURCES的变量，该变量包含
    mbedtls源文件以及示例代码ciphersuite-list.c；

    6）定义可执行文件名为ciphersuite-list，该可执行文件依赖
    SOURCES变量。

    3.编译与执行

    行编译与执行过程如下：




    # 进入示例所在路径
    $ cd 02_start/linux/ciphersuite-list
    # 新建一个build文件夹，用于保存临时文件
    $ mkdir –p build & cd build
    # 生成makefile文件
    $ cmake ..
    $ make
    # 执行示例
    $  ./ciphersuite-list
       Available Ciphersuite:
       [001] TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384
       [002] TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
       [003] TLS-DHE-RSA-WITH-AES-256-GCM-SHA384
       [004] TLS-ECDHE-ECDSA-WITH-AES-256-CCM
       [005] TLS-DHE-RSA-WITH-AES-256-CCM
       [006] TLS-ECDHE-ECDSA-WITH-AES-256-CBC-SHA384
       [007] TLS-ECDHE-RSA-WITH-AES-256-CBC-SHA384
       [008] TLS-DHE-RSA-WITH-AES-256-CBC-SHA256
       [009] TLS-ECDHE-ECDSA-WITH-AES-256-CBC-SHA
       [010] TLS-ECDHE-RSA-WITH-AES-256-CBC-SHA
       // 省略部分内容
       [125] TLS-PSK-WITH-AES-128-CBC-SHA256
       [126] TLS-PSK-WITH-AES-128-CBC-SHA
       [127] TLS-PSK-WITH-CAMELLIA-128-GCM-SHA256
       [128] TLS-PSK-WITH-CAMELLIA-128-CBC-SHA256
       [129] TLS-PSK-WITH-AES-128-CCM-8
       [130] TLS-PSK-WITH-3DES-EDE-CBC-SHA




      从输出结果可以看出，默认配置下的mbedtls支持130种安全套
件。虽然mbedtls所支持的安全套件仅是IANA组织规定的一部分，但
是在嵌入式物联网应用中，这些安全套件还是显得有些“臃肿”。



       76

## Page 77

4.替换mbedtls配置文件

     mbedtls可通过修改配置文件的方式进行裁剪，默认的配置文件
位于{mbedtls代码仓库}/include/mbedtls/config.h文件中。虽然config.h
文件中对于每一个参数均有详细的辅助说明，但是参数之间存在一定
的依赖关系，所以从头编写一个配置文件往往需要不少实践经验。
mbedtls提供了几种参考配置，这些参考配置详见configs文件夹。此
处会使用config-mini-tls1_1.h文件作为配置文件，配置文件中启用了
        _ENABLED宏定义，从后面的执
MBEDTLS_KEY_EXCHANGE_RSA
行结果可以看出，列表中只保留了与RSA密钥协商相关的密码套件。
config-mini-tls1_1.h的具体内容如代码清单2-6所示，该文件中相关配
置含义和使用方法将在后续的章中逐个分析。

     代码清单2-6 config-mini-tls1_1.h



    #ifndef MBEDTLS_CONFIG_H
    #define MBEDTLS_CONFIG_H
    /* System support */
    #define MBEDTLS_HAVE_ASM
    #define MBEDTLS_HAVE_TIME
    /* mbed TLS feature support */
    #define MBEDTLS_CIPHER_MODE_CBC
    #define MBEDTLS_PKCS1_V15
    #define MBEDTLS_KEY_EXCHANGE_RSA_ENABLED
    #define MBEDTLS_SSL_PROTO_TLS1_1
    /* mbedtls组件 */
    #define MBEDTLS_AES_C
    #define MBEDTLS_ASN1_PARSE_C
    #define MBEDTLS_ASN1_WRITE_C
    // 省略部分内容




    5.再次编译执行

    在编译过程中，通过CFLAG参数指定配置文件查找路径和自定

        77

## Page 78

    义配置文件，本示例中配置文件位于{mbedtls代码仓库}/configs目录
    中，配置文件宏定义DMBEDTLS  _FILE被赋值为<config-
        _CONFIG
        _1.h>。
    mini-tls1



    # 进入示例所在路径
    $ cd 02_start/linux/ciphersuite-list
    # 进入build目录，删除编译文件
    $ cd build && rm -rf *
    # 生成makefile文件
    $ CFLAGS="-I$MBEDTLS_BASE/configs -DMBEDTLS_CONFIG_FILE='<config-mini-tls1_1.h>'"
    cmake ..
    $ make
    # 执行示例
    $  ./ciphersuite-list
       Available Ciphersuite:
       [001]TLS-RSA-WITH-AES-256-CBC-SHA256
       [002]TLS-RSA-WITH-AES-256-CBC-SHA
       [003]TLS-RSA-WITH-AES-128-CBC-SHA256
       [004]TLS-RSA-WITH-AES-128-CBC-SHA
       [005]TLS-RSA-WITH-3DES-EDE-CBC-SHA




     再次执行之后我们将发现，ciphersuite-list的输出内容产生了明显
变化，此时mbedtls支持的安全套件仅有5个。mbedtls的模块化设计使
用户可以根据实际需要裁剪安全组件，以达到最优配置。

[1] IANA TLS安全套件完整列表网址为：

https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-

parameters-4










       78

## Page 79

2.5 Zephyr OS简介

   Zephyr OS[1]是由Linux基金会托管的开源协作项目，其目标是构
建一个针对资源受限设备的小型、可裁剪的实时操作系统
（RTOS）。Zephyr OS系统架构如图2-3所示。










    79

## Page 80

图2-3 Zephyr OS系统架构

Zephyr OS采用模块化设计，支持多种主流硬件架构，如ARC架
构、ARM架构、X86架构等，开发人员可以很容易地根据需求定制一
个最优的解决方案。除此之外，Zephyr OS相比其他开源物联网系统
具有很多优点，如表2-4所示。

表2-4     Zephyr OS优点


80

## Page 81

[1] Zephyr官网为：https://www.zephyrproject.org。










81

## Page 82

2.6 Zephyr开发环境搭建

本节以Ubuntu 1604 Desktop为例，说明如何在Linux环境下构建
Zephyr开发环境。构建Zephyr开发环境前，需在Ubuntu中正确安装
Python3和CMake等工具。构建Zephyr开发环境的步骤较多，详细内
容可参考Zephyr OS入门手册。

1.安装依赖包

    为了搭建Zephyr开发环境，需要在Ubuntu中安装必要的依赖包。



# 更新软件源
$ sudo apt-get update
$ sudo apt-get upgrade
# 安装依赖包
$ sudo apt-get install --no-install-recommends git cmake ninja-build gperf \
ccache doxygen dfu-util device-tree-compiler \
python3-ply python3-pip python3-setuptools python3-wheel xz-utils file \
make gcc-multilib autoconf automake libtool librsvg2-bin \
texlive-latex-base texlive-latex-extra latexmk texlive-fonts-recommended




2.获取Zephyr源代码

    把Zephyr代码克隆到用户目录中，再切换到zephyr-v1.13.0分支，
本书所有章节的示例均基于该分支。




$ mkdir -p repo
$ cd repo
$ git clone https://github.com/zephyrproject-rtos/zephyr
$ git checkout zephyr-v1.13.0




3.安装必要的Python3依赖工具

82

## Page 83

    # 进入zephyr源代码目录
    $ cd zephyr
    # 通过pip3工具安装其他依赖项
    $ pip3 install --user -r scripts/requirements.txt




    4.安装Zephyr SDK

Zephyr SDK包括相关硬平台所依赖的编译、下载和调试等工
    具。本文中使用的SDK版本为0.9.3。安装过程中控制台将出现Zephyr
    SDK安装路径的提示，建议把Zephyr SDK安装到{用户目
    录}\opt\zephyr-sdk文件夹中。



    # 通过wget下载Zephyr SDK
    $ wget https://github.com/zephyrproject-rtos/meta-zephyr-sdk/releases/download/0.9.3/zephyr-sdk-0.9.3-setup.run
    # 安装Zephyr SDK
    $ chmod +x zephyr-sdk-0.9.3-setup.run
    $  ./zephyr-sdk-0.9.3-setup.run
    # 输出内容
    Verifying archive integrity... All good.
    Uncompressing SDK for Zephyr 100%
    Enter target directory for SDK (default: /opt/zephyr-sdk/): {用户目录}/opt/zephyr-sdk
    Installing SDK to {用户目录}/opt/zephyr-sdk
    The directory {用户目录}/opt/zephyr-sdk/sysroots will be removed!
      [*] Installing x86 tools...
      [*] Installing arm tools...
      [*] Installing arc tools...
      [*] Installing iamcu tools...
      [*] Installing mips tools...
      [*] Installing nios2 tools...
      [*] Installing xtensa tools...
      [*] Installing riscv32 tools...
      [*] Installing additional host tools...
    Success installing SDK. SDK is ready to be used.




    5.设置环境变量

      在用户目录中的.bashrc文件末尾增加
          _VARIANT、ZEPHYR
    ZEPHYR_TOOLCHAIN      _SDK_INSTALL_DIR
    和ZEPHYR_BASE等参数。修改完成后在控制台执行



      83

## Page 84

    source$HOME/.bashrc，该指令可使新增的环境变量立即生效。



$ echo "export ZEPHYR_TOOLCHAIN_VARIANT=zephyr" >> $HOME/.bashrc
$ echo "export ZEPHYR_SDK_INSTALL_DIR=<zephyr-sdk 安装路径>" >> $HOME/.bashrc
$ echo "export ZEPHYR_BASE=<zephyr 源代码仓库安装路径>" >> $HOME/.bashrc
$ source $HOME/.bashrc










    84

## Page 85

2.7 Zephyr硬件平台选择

   Zephyr操作系统支持多款ARM平台，本书与Zephyr有关的
mbedtls示例均运行在Nucleo F429ZI平台。相较于Linux平台，在类似
Nucleo F429ZI这样的嵌入式平台上运行mbedtls应用时需要考虑更多
的限制，这些限制包括mbedtls应用所需的内存和栈空间等，这些额
外的消耗将限制mbedlts的发挥空间。










    85

## Page 86

2.7.1 资源介绍

   Nucleo F429ZI是一款基于ARM Cortex-M4内核的STM32F4系列
开发板，板载MCU为STM32F429ZI，STM32F429ZI主频可达
180MHz，并具有2MB内部Flash和256KB RAM，还具有以太网和真
随机数生成器等功能。真随机数生成器是物联网应用的关键部分。
Zephyr提供的标准驱动中包括熵源（entropy）驱动，并可通过
sys_rand32_get获得一个4字节大小的真随机数。在下一节的随机数示
例中，将使用STM32F429ZI的真随机数生成器生成4字节随机数。该
开发板主要资源情况如表2-5所示，外观如图2-4所示。

        表2-5 Nucleo F429ZI板载资源情况










    86

## Page 87

图2-4 Nucleo STM32F429ZI开发板外观










87

## Page 88

2.7.2 Ubuntu中安装STLink工具

    为了把编译得到的固件下载至Nucleo F429ZI开发板中，需要在
Ubuntu中正确安装STLink工具。具体的安装步骤如下：


    # 安装依赖库
    $ sudo apt-get install libusb-1.0
    # 克隆STLink工具
    $ git clone https://github.com/texane/stlink
    # 编译
    $ make release
    # 安装
    $ cd Release
    $ sudo make install


    安装STLink工具后，若Ubuntu主机与Nucleo STM32F429ZI板载
的STLink相连，STLink工具将会在Ubuntu主机中虚拟一个串口设
备，该串口设备的名称为ttyACM0或ttyACM1。Zephyr平台Nucleo
STM32F429ZI相关示例中，控制台输出内容将会重定向到ttyACM0设
备中，波特率为115200。调试Zephyr示例时，可借助minicom工具查
看STM32F429ZI的输出日志。










    88

## Page 89

2.8 Zephyr应用示例开发

                            完成Zephyr开发环境的构建工作之后，本节通过一个随机数示例
说明开发Zephyr应用的基本步骤。随机数是物联网应用的重要组成部
分，公钥密码、数字签名和TLS/DTLS部分均与随机数相关。Zephyr
应用示例结构如下：

# 进入示例路径
$ cd 02_start/zephyr/random
# 查看示例文件结构
$ tree -L 2├── CMakeLists.txt├── prj.conf └── src└── main.c

                                      随机数示例相关文件及其描述如表2-6所示。

    表2-6  Zephyr随机数示例相关文件描述










89

## Page 90

2.8.1 编写CMakeLists.txt

    此处CMakeLists.txt文件是一个非常好用的Zephyr模板文件，只需
简单的修改便可适配其他的Zephyr应用。该文件的具体内容如下：

  cmake_minimum_required(VERSION 3.8.2)
  include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)
  project(NONE)
  FILE(GLOB app_sources src/*.c)
  target_sources(app PRIVATE ${app_sources})

    在CMakeLists.txt文件中，通过include指令引入一个构建脚本
boilerplate.cmake。为了能够正确地找到boilerplate.cmake脚本，
CMake构建脚本通过环境变量中的ZEPHYR_BASE变量获取Zephyr源
代码的安装路径，只有ZEPHYR_BASE环境变量设置正确才可以顺利
载入boilerplate.cmake脚本。再通过FILE命令把src文件夹中的所有C文
件复制到CMake内部变量app_sources中。最后，通过target_sources指
令引入依赖的C文件，构建名为app的可执行固件。boilerplate.cmake
较为复杂，它包含了很多CMake技巧，但其具体内容已经超出了本书
的讨论范围。










    90

## Page 91

2.8.2 编写prj.conf

   每个Zephyr应用都包含一个conf配置文件，可通过该配置文件启
用或禁用某些系统功能。为了启用随机数驱动和控制台打印功能，需
要在prj.conf文件中设置CONFIG_ENTROPY_GENERATOR和
CONFIG_STDOUT_CONSOLE。本节中的prj.conf具体内容如下：


    CONFIG_ENTROPY_GENERATOR=y
    CONFIG_STDOUT_CONSOLE=y










    91

## Page 92

2.8.3 编写main.c

随机数应用示例使用sys     _get接口获取随机数，该接口位
    _rand32
于random/rand32.h头文件中。示例代码会以1秒为周期，获取并生成4
字节随机数，如代码清单2-7所示。

代码清单2-7 main.c用于生成4字节随机数



#include <zephyr.h>
#include <random/rand32.h>
#include <stdio.h>
void main(void)
{
 printf("\n %s board random:\n", CONFIG_BOARD);
 while (1) {
  printf(" 0x%08x\n", sys_rand32_get());
  k_sleep(1000);
 }
}










  92

## Page 93

2.8.4 编译与运行

    在使用cmake指令时，需通过-DBOARD参数指定硬件平台，本
书中所有的示例均可以运行在native_posix平台和nucleo_f429zi平台，
前者比较适合作为应用示例快速实现和验证的开发环境，而后者则为
实际的嵌入式硬件平台，需要更加关注内存资源的使用情况。下面分
别对两种硬件平台的编译与执行过程进行介绍。

1.native_posix平台


    # 进入示例代码文件夹
    $ cd 02_start/zephyr/random
    # 新建一个build文件夹，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成native_posix平台makefile文件
    $ cmake -DBOARD=native_posix ..
    # 编译与执行
    $ make && make run
    native_posix board random:
    0x098a2adf
    0x698f8e7b
    0x324be164
    0x3218c6a9
    0x11c8915c
    0x13127769
    # 省略之后内容


2.nucleo_f429zi平台

    与native_posix平台不同的是，nucleo_f429zi平台示例编译完成后
需要通过make flash命令将生成的固件下载至目标板中。应用程序将
运行结果输出至串口控制台，所以应用程序下载至开发板运行之前，
需新建终端并通过minicom工具打开指定串口。操作指令如下：


    93

## Page 94

# 请根据实际情况修改串口名称
sudo minicom -b 115200 -D /dev/ttyACM0



编译与运行过程如下：




# 进入示例代码文件夹
$ cd 02_start/zephyr/random
# 新建一个build文件夹，用于存放临时文件
$ mkdir -p build && cd build
# 通过cmake指令生成nucleo_f429zi平台makefile文件
$ cmake -DBOARD=nucleo_f429zi ..
# 编译
$ make
# 执行下载
$ make flash
# 串口控制台输出
nucleo_f429zi board random:
0x098a2adf
0x698f8e7b
0x324be164
0x3218c6a9
0x11c8915c
# 省略之后内容










94

## Page 95

2.9 Zephyr mbedtls示例

   上一节已经说明了如何构建Zephyr应用，本节将在此基础上增加
mbedtls相关的内容。在2.8节介绍了编写CMakeLists.txt和prj.conf的方
法，这些方法在本节依然适用。与前面的示例不同，为了构建
mbedtls相关示例，本节将修改prj.conf文件，并在该文件中增加
mbedtls的编译选项。另外本节还将增加一个名为mbedtls_config.h的
mbedtls配置文件。本节示例中的CMakeLists.txt、prj.conf和
mbedtls_config.h文件都是不错的模板文件，后续章的示例都将以这些
文件为基础。










    95

## Page 96

2.9.1  Base64示例

让我们再次回到mbedtls的讨论中，之前的Zephyr示例中并没有
mbedtls部分的内容，下面通过一个Base64示例说明如何在Zephyr环境
下中使用mbedtls。与大多数Zephyr示例相似，此处包括
CMakeLists.txt、prj.conf和src/main.c，除此之外还包括
mbedtls_config.h配置文件。该示例目录结构如下，各文件描述如表2-
7所示。

# 进入示例路径
$ cd 02_start/zephyr/base64
# 查看示例结构
$ tree -L 2├── CMakeLists.txt├── prj.conf└── src
├── main.c
└── mbedtls_config.h

    表2-7     Zephyr应用示例相关文件描述






1.示例代码

代码清单2-8与之前的Linux平台实现代码几乎相同，示例描述及
接口描述在这里不做重复介绍。

代码清单2-8 main.c Base64编码与解码



96

## Page 97

#include <zephyr.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "mbedtls/base64.h"
#include "mbedtls/platform.h"
// 省略部分中间代码
int main(void)
{
 size_t len;
 uint8_t rst[512];
 mbedtls_platform_set_printf(printf);
 len = sizeof(msg);
 dump_buf("\n base64 message: ", msg, len);
 mbedtls_base64_encode(rst, sizeof(rst), &len, msg, len);
 mbedtls_printf(" base64 encode : %s\n", rst);
 mbedtls_base64_decode(rst, sizeof(rst), &len, rst, len);
 dump_buf(" base64 decode : ", rst, len);
 printf("\n");
 return 0;
}




2.编写mbedtls
     _config.h

该示例中增加一个名为mbedtls_config.h的mbedtls配置文件，该
文件是一个典型的模板文件，在其他示例中将被反复使用。该模板文
件可分为以下3部分。

·Zephyr系统支持：保证mbedtls在Zephyr操作系统中正确运行，
该部分一般保持不变，本书的其他示例也将沿用该部分定义；

·mbedtls组件：此处增加了Base64支持，建议按需增加；

·mbedtls配置文件检查：一般情况下需引入
 _config.h，用于检查mbedtls配置参数之间的依赖关系，
mbedtls/check
见代码清单2-9。该部分一般保持不变。

代码清单2-9     mbedtls_config.h



 97

## Page 98

    #define MBEDTLS_PLATFORM_C
    #define MBEDTLS_PLATFORM_MEMORY
    #define MBEDTLS_MEMORY_BUFFER_ALLOC_C
    #define MBEDTLS_PLATFORM_NO_STD_FUNCTIONS
    #define MBEDTLS_PLATFORM_EXIT_ALT
    #define MBEDTLS_NO_PLATFORM_ENTROPY
    #define MBEDTLS_NO_DEFAULT_ENTROPY_SOURCES
    #define MBEDTLS_PLATFORM_PRINTF_ALT
    #define MBEDTLS_BASE64_C


   1）MBEDTLS_PLATFORM_C启用平台抽象接口，使能该参数
后，用户可重新定义calloc/free等接口。

   2）MBEDTLS_PLATFORM_MEMORY启用内存分配接口，使能
该参数后用户可以自己实现calloc/free接口，并通过宏定义替换或通
过接口设置方式进行替换。

   3）MBEDTLS_MEMORY_BUFFER_ALLOC_C启用mbedtls自带
的内存分配接口，该参数适用于那些没有动态内存分配功能的嵌入式
平台。

   4）MBEDTLS_PLATFORM_NO_STD_FUNCTIONS不使用标准
库函数，如calloc/free等接口。

   5）MBEDTLS_PLATFORM_EXIT_ALT使能exit接口替换，使能
后允许平台设置exit接口。

   6）MBEDTLS_NO_PLATFORM_ENTROPY不使用内置的熵源，
开启该宏定义后需要通过接口添加自定义熵源接口。

   7）MBEDTLS_NO_DEFAULT_ENTROPY_SOURCES取消默认
熵源功能，用户可通过接口添加自定义熵源接口。

        98

## Page 99

   8）MBEDTLS_PLATFORM_PRINTF_ALT使能printf接口替换，
    使能后允许用户使用mbedtls        _platform_set_printf接口设置自定义printf
    函数。

    9）MBEDTLS    _BASE64    _C启用Base64功能。

    3.编写prj.conf

          为了在Zephyr应用中集成mbedtls，需要在prj.conf配置文件中启
    用CONFIG_MBEDTLS和CONFIG  _MBEDTLS_BUILTIN。默认情况
    下，Zephyr使用的mbedtls配置文件为{zephyr代码仓
    库}/ext/lib/crypto/mbedtls/configs config-mini-tls1_2.h，此处示例使用
    了自定义的配置文件mbedtls_config.h，所以还需要在prj.conf中定义
    CONFIG_MBEDTLS_CFG    _FILE为mbedtls_config.h。此处的prj.conf文
    件也是一个典型的模板文件，其他章的示例将会在此模板文件上进行
    修改。

    CONFIG_STDOUT_CONSOLE=y
    CONFIG_MBEDTLS=y
    CONFIG_MBEDTLS_BUILTIN=y
    CONFIG_MBEDTLS_CFG_FILE="mbedtls_config.h"

    4.编写CMakeLists.txt文件

   CMakeLists.txt和之前的构建文件大致相同，由于启用了
mbedtls，并指定了自定义的mbedtls配置文件，所以还需要通过
CMake的target_include_directories指令引入mbedtls配置文件所在的路


                            99

## Page 100

    径，否则在编译过程中将提示无法找到mbedtls_config.h。



    cmake_minimum_required(VERSION 3.8.2)
    include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)
    project(NONE)
    if (CONFIG_MBEDTLS)
    target_include_directories(mbedTLS INTERFACE ${PROJECT_SOURCE_DIR}/src)
    endif()
    target_sources(app PRIVATE src/main.c)



5.编译与运行

     基础示例默认会运行在necluo_f429zi平台，若需要运行在仿真平
台只需将-DBOARD参数指定为native_posix即可，具体过程可回顾
2.8.4节。编译过程完成时控制台将输出Flash和RAM的消耗情况，此
时Base64示例仅消耗STM32F429ZI约14KB Flash空间和约4KB RAM
空间。在后续章的示例中，我们还将关注mbedtls应用的Flash和RAM
消耗情况。

     应用程序将把运行结果输出至串口控制台，所以应用程序下载至
开发板运行之前需新建终端，并通过minicom工具打开指定串口。操
作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



    编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 02_start/zephyr/base64
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..


    100

## Page 101

# 编译并查看资源消耗情况
$ make
Memory region    Used Size Region Size %age Used
         FLASH:  14400 B     2 MB   0.69%
           CCM:     0 GB    64 KB   0.00%
          SRAM:   4356 B   256 KB   1.66%
      IDT_LIST:    200 B     2 KB   9.77%
# 下载到开发板运行
$ make flash
# 串口控制台输出
base64 message: 14 fb 9c 03 d9 7e
base64 encode : FPucA9l+
base64 decode : 14 fb 9c 03 d9 7e










                 101

## Page 102

2.9.2 大数运算示例

  完成Base64示例之后，本节继续在Zephyr平台运行一个大数运算
示例。大数运算是密码学中常用的计算手段之一，是公钥密码和数字
签名算法的基础。所谓大数运算，就是运算过程的参数或结果超过了
计算机编程语言中基本数据类型所表示的范围，例如C语言中64位无
符号整数的表示范围为0~18446744073709551615。虽然64位无符号整
数的表示范围已经很大，但在密码学范畴这种类型的整数依然不能满
足需求。mbedtls支持大数运算，大数运算的具体实现详见{mbedtls代
码仓库}/library/bignum.c。下面通过大数乘法运算、大数模指数运算
和大数模逆运算这3个示例说明bignum相关接口的使用方法。在本示
例中共有A、E和N三组参数参与运算，先计算一组大数乘法
X=A*E，再计算一组大数模指数运算X=A^E mod，最后计算一组大
数模逆运算。本节示例相关参数和计算结果如图2-5所示。

  与本章其他示例相似，本节示例也包括main.c、
mbedtls_config.h、prj.conf和CMakeLists.txt等文件。

1.示例代码

  在示例代码中的大数运算中，大数乘法运算、大数模指数运算与
实数域中的概念非常相似，但是模逆运算和实数域中的倒数运算存在
很大差异。在实数域中，2与0.5的乘积为1，则称2的倒数为0.5，在有


    102

## Page 103

限域（此处的模逆运算）中，2 X 8 mod 17=1，则称2关于模17的逆元
为8。总之，实数域中倒数的概念与乘积为1有关，而有限域中逆元的
概念与余数为1有关。示例代码如代码清单2-10所示。










    103

## Page 104

图2-5 大数运算示例

代码清单2-10 bignum示例代码



#include <zephyr.h>
#include <string.h>
#include <stdio.h>
#include "mbedtls/bignum.h"
#include "mbedtls/platform.h"
static void dump_buf(char *buf, size_t len)
{
 for (int i = 0; i < len; i++) {
  mbedtls_printf("%c%s", buf[i], (i + 1) % 32 ? "" : "\n\t");
 }
 mbedtls_printf("\n");
}


 104

## Page 105

    int main(void)
    {
     size_t olen;
     char buf[256];
     mbedtls_mpi A, E, N, X;
     mbedtls_platform_set_printf(printf);
     mbedtls_mpi_init(&A);
     mbedtls_mpi_init(&E);
     mbedtls_mpi_init(&N);
     mbedtls_mpi_init(&X);
     mbedtls_mpi_read_string(&A, 16,
"EFE021C2645FD1DC586E69184AF4A31E" \
"D5F53E93B5F123FA41680867BA110131" \
"944FE7952E2517337780CB0DB80E61AA" \
"E7C8DDC6C5C6AADEB34EB38A2F40D5E6" );
     mbedtls_mpi_read_string(&E, 16,
"B2E7EFD37075B9F03FF989C7C5051C20" \
"34D2A323810251127E7BF8625A4F49A5" \
"F3E27F4DA8BD59C47D6DAABA4C8127BD" \
"5B5C25763222FEFCCFC38B832366C29E" );
     mbedtls_mpi_read_string(&N, 16,
"0066A198186C18C10B2F5ED9B522752A" \
"9830B69916E535C8F047518A889A43A5" \
"94B6BED27A168D31D4A52F88925AA8F5" );
     mbedtls_mpi_mul_mpi(&X, &A, &N);
     mbedtls_mpi_write_string(&X, 16, buf, 256, &olen);
     mbedtls_printf("\n X = A * N = \n\t");
     dump_buf(buf, olen);
     mbedtls_mpi_exp_mod(&X, &A, &E, &N, NULL);
     mbedtls_mpi_write_string(&X, 16, buf, 256, &olen);
     mbedtls_printf("\n X = A^E mode N = \n\t");
     dump_buf(buf, olen);
     mbedtls_mpi_inv_mod( &X, &A, &N);
     mbedtls_mpi_write_string(&X, 16, buf, 256, &olen);
     mbedtls_printf("\n X = A^-1 mod N = \n\t");
     dump_buf(buf, olen);
     mbedtls_mpi_free(&A);
     mbedtls_mpi_free(&E);
     mbedtls_mpi_free(&N);
     mbedtls_mpi_free(&X);
     return 0;
    }



    示例代码中相关接口描述如表2-8所示。

     表2-8 大数运算示例相关接口描述










     105

## Page 106

2.编写mbedtls_config.h

   为了使mbedtls支持大数运算，需要在配置文件中增加
MBEDTLS_BIGNUM_C定义。mbedtls_config.h的其他部分与上一节
介绍的模板文件相同。

3.编写prj.conf

   由于大数运算需要消耗更大的栈空间，建议把
MAIN_STACK_SIZE设置为4096字节或更大值，默认情况下
MAIN_STACK_SIZE的大小为仅1024字节。另外大数运算过程中还会
使用动态内存分配接口，可以在配置文件中定义mbedtls栈大小，示
例中将mbedtls的堆大小设置为4096字节。prj.conf配置文件内容如
下：


    CONFIG_STDOUT_CONSOLE=y
    CONFIG_MAIN_STACK_SIZE=4096
    CONFIG_MBEDTLS=y
    CONFIG_MBEDTLS_BUILTIN=y
    CONFIG_MBEDTLS_ENABLE_HEAP=y
    CONFIG_MBEDTLS_HEAP_SIZE=4096
    CONFIG_MBEDTLS_CFG_FILE="mbedtls_config.h"


    4.编写CMakeLists.txt

    CMakeLists.txt文件内容与上一节完全相同。

    5.编译与运行




    106

## Page 107

      基础示例默认会运行在necluo_f429zi平台，若需要运行在仿真平
台只需将-DBOARD参数指定为native_posix即可，具体过程可回顾
2.8.4节。编译过程完成后，控制台将输出Flash空间和RAM空间的消
耗情况。由于增加了mbedtls自定义栈空间，栈空间占4KB，另外还增
加了4KB的Zephyr主线程栈空间，所以大数运算的内存消耗增加至
11KB左右，约占STM32F429ZI整个RAM空间的4.4%。

      应用程序将把运行结果输出至串口控制台，所以应用程序下载至
开发板运行之前需新建终端，并通过minicom工具打开指定串口。操
作指令如下：




    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



    编译与运行过程如下：




    # 进入示例代码文件夹
    $ cd 02_start/zephyr/bignum
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region    Used Size Region Size %age Used
                 FLASH:     22760 B    2 MB    1.09%
                   CCM:     0 GB      64 KB    0.00%
                  SRAM:     11548 B  256 KB    4.41%
          IDT_LIST:         200 B      2 KB    9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    X = A * N =
          602AB7ECA597A3D6B56FF9829A5E8B85
          9E857EA95A03512E2BAE7391688D264A
          A5663B0341DB9CCFD2C4C5F421FEC814
          8001B72E848A38CAE1C65F78E56ABDEF
          E12D3C039B8A02D6BE593F0BBBDA56F1
          ECF677152EF804370C1A305CAF3B5BF1
          30879B56C61DE584A0F53A2447A51E
    X = A^E mode N =
          36E139AEA55215609D2816998ED020BB



                            107

## Page 108

BD96C37890F65171D948E9BC7CBAA4D9
325D24D6A3C12710F10A09FA08AB87
X = A^-1 mod N =
3A0AAEDD7E784FC07D8F9EC6E3BFD5C3
DBA76456363A10869622EAC2DD84ECC5
B8A74DAC4D09E03B5E0BE779F2DF61










108

## Page 109

2.10 本章小结

   本章介绍了Linux和Zephyr环境下开发mbedtls应用的一般步骤。
本章通过一个Base64示例说明开发mbedtls应用的具体步骤，这些步
骤包括源代码编写、CMake构建脚本编写和编译与执行等。无论开发
Linux应用还是开发Zephyr应用，CMake都是一种重要的构建工具。
在遍历mbedtls安全套件示例中，我们可通过修改mbedtls配置文件的
方式对其进行裁剪。相较于Linux平台，为了在Zephyr中启用mbedtls
组件，还需要在配置文件prj.conf中增加CONFIG_MBEDTLS和
CONFIG_MBEDTLS_BUILTIN选项。本章还引入了一个nucleo_f429zi
平台的硬件随机数示例，硬件随机数生成器是物联网安全应用的基
础。

   请务必注意本章中提到的3个模板文件——CMakeLists.txt、
prj.conf和mbedtls_conf.h，这些模板文件经过简单的修改之后便可适
用于其他章节的示例。但由于篇幅关系，这些模板文件中的通用内容
将不再重复介绍。










    109

## Page 110

    第3章 数论基础知识

3.1 本章主要内容

   数论在密码学中有着非常广泛的应用。为了更好地理解密码学基
础知识，本章将讲解与本书相关的数论基础知识。若读者已经熟练掌
握了这些数论基础知识，可略过本章内容。表3-1罗列了本书所涉及
的相关数论基础知识及相应的简要描述。

    表3-1 数论基础知识及简要描述










110

## Page 111

3.2 素数

定义3-1

  设整数n≠0，±1，若除了因数±1和±n之外，n没有其他的因数，
那么称n为素数（或质数或不可约数），否则n为合数。

  例如，整数2、3、7都是素数，而4、6、10、15、32都是合数。
素数，又称质数或不可约数。素数的概念虽然简单，但是人类从未停
止过有关素数的研究。若一个整数小于100，通过简单的运算就可判
断该整数是否为素数，例如24=2×2×2×3，所以24为一个合数；而
59=1×59，所以59为一个素数。

  素数还有一个显著特点：若给定两个素数p和q，计算乘积n=p·q
较为容易；但给定一个整数n，求解其两个素因数却非常困难。这便
是公钥加密RSA算法的基础。例如：

  p=20000000000000002559，q=80000000000000001239

  n=p·q=1600000000000000229500000000000003170601

  表3-2罗列了前100个素数。

        表3-2 前100个素数





    111

## Page 112

  判断素数的方法包括平凡除法（厄拉托赛师筛选法）、费马检
验、Miller-Rabin检验等。这些素数检测方法可参考《信息安全数学
基础（第2版）》一书。










    112

## Page 113

3.3 模运算

    本节将介绍同余符号、模加法运算、模乘法运算、模逆运算和模
重复平方运算。阅读本节需注意以下两点：

 1）同余符号“≡”和恒等于符号“≡”在外观上完全相同，但是表达
的含义却完全不同。

   2）模运算中也有“倒数”概念，但模运算中倒数的计算方法和整
数倒数的计算方法完全不同，例如整数3的倒数为1/3，但是整数3关
于模8的倒数却为3。

    模运算是密码学的基础，无论是对称加密、公钥加密还是数字签
名，均与模运算有关。










113

## Page 114

3.3.1 模数

定义3-2

若a是整数，n是正整数，则a模n是a除以n所得到的余数，整数n
叫作模数。

例3-1

1 mod 7=1中，模数为7，余数为1；

9 mod 6=3中，模数为6，余数为3；

-4 mod 8=2中，模数为8，余数为2。










114

## Page 115

3.3.2 同余

定义3-3

给定一个正整数m，如果两个整数a、b，a-b能被m整除，记作
a≡b mod m，叫作a和b模m同余。

例3-2

8≡1 mod 7，15≡1 mod 7，22≡1 mod 7，29≡1 mod 7

同余概念和同余符号由德国数学家高斯引入，同余符号“≡”和恒
等于符号“≡”在外观上完全相同，但表达的含义却完全不同。由示例
可以得出，模运算和同余符号可用于表达余数，例如8除以7商1余1，
22除以7商3余1，8和27这两个整数除以7的余数均为1。在之前的数学
知识中一般讨论商的关系，而在数论中一般讨论余数的关系。8、
15、22、29与模7的关系还可以采用以下写法：

8≡15≡22≡29≡1 mod 7

在多数计算机语言中，模运算常使用“%”表示，常用的计算语
言，如C、Python和Java均使用“%”作为运算符。相比于15≡1 mod 7，
15%7=1这样的写法似乎更容易理解。但高斯引入的同余符号表达更
加简洁，该符号将在后续章中被频繁使用。



115

## Page 116

3.3.3 模算术运算

通过模数的定义可以知道，模n运算会将所有整数结果限定到
{0,1,2…,n-1}的集合内，而普通算术的加、减和乘运算同样可以“平
移”到集合内，叫作模算术运算。模算术运算具有以下性质：

((a mod n)+(b mod n))mod n=(a+b)mod n

((a mod n)-(b mod n))mod n=(a-b)mod n

((a mod n)×(b mod n))mod n=(a×b)mod n

例3-3

假设a=3，b=5，n=8，验证模算术运算性质：

第一步：验证加法性质

((13 mod 8)+(15 mod 8))mod 8  12 mod 8=4

(13+15)mod 8  28 mod 8=4

第二步：验证减法性质

((13 mod 8)-(15 mod 8))mod 8  -2 mod 8=4

(13-15)mod 8  -2 mod 8=4



116

## Page 117

第三步：验证乘法性质

((13 mod 8)×(15 mod 8))mod 8  35 mod 8=3

(13×15)mod 8       195 mod 8=3










117

## Page 118

3.3.4 模逆运算

  和普通加法运算一样，模运算中对于每个整数也存在加法逆元，
或称为负数。在模运算中整数a的加法逆元b是使得(a+b)mod n=0成立
的值。同样，每个整数也存在乘法逆元，或称为倒数。在模运算中整
数a的乘法逆元b满足(a·b)≡1 mod n。

  表3-3为模8的加法计算结果，表3-4为模8的乘法计算结果。由于
加法运算和乘法运算的交换性，从表3-3或表3-4可以看出，模加法和
模乘法的计算结果均关于主对角线对称。关于模8的加法逆元可以通
过浏览表3-3中值为0的项获得，例如3的加法逆元为5；而乘法逆元可
以通过浏览表3-4中值为1的项获得，例如3的乘法逆元为3。

        表3-3 关于模8的加法运算










    表3-4 关于模8的乘法运算



    118

## Page 119

  关于模8的乘法逆元结果可以看出，整数1、3和5存在关于模8的
乘法逆元，而整数2、4和6不存在关于模8的乘法逆元，如表3-5所
示。实际上，只有当a和m互为质数，也就是说gcd(a,m)=1时，才存在
一个整数b且满足a·b≡1 mod m。此处3和8互为质数，5和8互为质数，
而4和8并不存在互为质数的关系。

     表3-5 关于模8的加法逆元和乘法逆元结果汇总




  模乘法逆元可使用扩展欧几里得算法计算得到，具体算法可参考
《深入浅出密码学——常用加密技术原理与应用》6.3.1节欧几里得算
法和6.3.2节扩展的欧几里得算法。代码清单3-1是扩展欧几里得算法
计算模乘法逆元的python脚本，可通过命令行输入参数计算得到模乘
法逆元。该文件名称为eea.py，位于本书代码仓库scripts目录下。

  代码清单3-1 计算模乘法逆元脚本eea.py


    119

## Page 120

import sys
n = int(sys.argv[1])
p = int(sys.argv[2])
def extended_euclid_algorithm(n, p):
s, old_s = 0, 1
t, old_t = 1, 0
r, old_r = p, n
while r != 0:
quotient = old_r // r
old_r, r = r, old_r - quotient * r
old_s, s = s, old_s - quotient * s
old_t, t = t, old_t - quotient * t
return old_r, old_s, old_t
def inverse_of(n, p):
gcd, x, y = extended_euclid_algorithm(n, p)
assert (n * x + p * y) % p == gcd
if gcd != 1:
raise ValueError(
          '{} has no multiplicative inverse '
          'modulo {}'.format(n, p))
else:
return x % p
print(n, "^ -1 mod", p, "=", inverse_of(n, p))



计算7 mod 23的乘法逆元的代码如下：



$ cd scripts
$ python3 eea.py 7 23
# 输出
7 ^ -1 mod 23 = 10










          120

## Page 121

3.3.5 模重复平方

模算术运算中经常会计算大整数的幂运算，例如对于大整数m和
大整数n，计算bnmod m，通常可对b递归进行n-1次幂运算：

bn≡(bn-1(mod m))·b(mod m)

这样递归计算的效率通常较低，在实际应用中可通过模重复平方
算法提高计算效率。下面通过一个具体示例说明模重复平方算法。

例3-4

通过计算137mod 15来验证模算术运算中的幂运算。若按照一般
的计算顺序，先计算137=62748517，然后再计算62748517 mod
15=7，在这种情况下需要7次乘法运算和一次模运算。本示例先把137
分解为137=134×132×131，然后依次计算131、132和134。

第一步：计算131mod 15

13    1≡13 mod 15

第二步：计算132mod 15

13    2≡169≡4 mod 15

第三步：计算134mod 15


121

## Page 122

134mod 15的结果可由132≡4 mod 15间接获取，通过这种方法可
大大减少计算量。

134≡(132)2≡(4)2≡16≡1 mod 15

第四步：计算137=134×132×131mod 15

137≡134×132×131≡1×4×13≡52≡7 mod 15

这种不直接计算137而通过中间结果计算137mod 15的方法称为模
重复平方算法，通过这种方法可以降低计算复杂度，缩短计算时间。










122

## Page 123

3.4   群

3.4.1 群的基本概念

    群是密码学中非常重要的概念。群是一个定义了二元运算的集
合，使集合上的两个元素运算得到第3个元素。这些运算方法需要遵
守特定的规则。

定义3-4

    群指的是一个元素集合G以及联合G内两个元素的操作·的集合，
如果一个群的元素是有限的，则称该群为有限群；群中元素的个数称
为群的阶，表示为|G|；如果群的元素是无限的，则称该群为无限
群。

    群具有以下属性。

    ·封闭性：如果a和b属于G，则a·b也属于G。

    ·结合律：即对G中任意元素a、b、c，都有a·(b·c)=(a·b)·c成立。

    ·单位元：G中存在一个元素e，对于G中任意元素a，都有
a·e=e·a=a成立。

    ·逆元：对于G中任意元素a，G中都存在一个元素a，使得


    123

## Page 124

    a·a=a·a=e成立。

    ·交换性：对于G中任意的元素a、b，都有a·b=b·a成立，则称G为
    阿贝尔群。

    例3-5

   构造一个集合 ，该集合由i={0,1,…,m-1}组成，且集合中的元
素满足gcd(i,m)=1。例如当m=9时， ={1,2,4,5,7,8}。在 中定义一个
群操作a·b mod 9，把群操作结果记录至表3-6中。

        表3-6    群操作a·b mod 9计算结果










    通过观察表3-6可以获得以下结论。

    ·封闭性：a和b均属于集合 ，而a·b mod 9的结果也属于集合
    ，例如当a=4，b=8时，a·b mod 9的计算结果为5，a=4，b=8和群操作
    结果5均属于集合 。

        124

## Page 125

   ·结合性：a、b、c均属于集合 ，则a·(b·c)=(a·b)·c，例如当
a=2，b=4，c=5时，2·(4·5)=(2·4)·5≡40≡4 mod 9。

   ·单位元： 中存在元素e，使得a·e=e·a=a，单位元e=1。

   ·逆元：对于集合 中的每一个元素，都存在一个逆元。例如2关
于模9的逆元为5，7关于模9的逆元为4。

   ·交换性：a·b mod 9和b·a mod 9的结果相同，例如当a=7，b=2
时，a·b mod 9和b·a mod 9的计算结果均为5。由于符合交换性，所以
 为阿贝尔群。










    125

## Page 126

3.4.2 循环群

定义3-5

 在群中定义求幂运算为重复的群运算，如a3=a·a·a，单位元为
a0=e，并且a-n=(a)n，其中a是a在群中的逆元，如果群G中的每一个元
素都是群中一个固定元素a的幂ak（k是整数），则称G是循环群，a是
生成元或本原元。

定义3-6

 设群的单位元为e，群内元素a的阶记作ord(a)，用来表示满足以

下条件的最小正整数k：  。

 例3-6

 下面通过一个具体示例说明循环群的概念。示例中需要计算群
中a=3的阶，此处计算3kmod 7，其中k={1,2,3,4,5,6,7,8}，各计算结果
记录如表3-7所示。

     表3-7    计算群 中a=3的阶






 从表3-7的计算结果可以看出，当指数为6时计算结果为1。3kmod

 126

## Page 127

7的计算结果在集合{3,2,6,4,5,1}中不断循环，3kmod 7的计算结果的
个数为6。由循环群的定义可知，当生成元为3时，群 的阶为6，记
作ord(3)=6。该循环群可表示为： ={3,2,6,4,5,1}。

  通过例3-6可得到，通过生成元3可获得循环群 内的所有元素，
 的阶和循环群内的元素个数相同。

定理3-1

  对每个素数p，（ ,·）都是一个阿贝尔有限循环群。

  例3-6中 ={3,2,6,4,5,1}便是一个阿贝尔有限循环群。










    127

## Page 128

3.4.3 子群

子群是循环群的一个子集。为了防止针对离散对数问题的攻击，
通常会选择循环群中阶为素数的子群构建离散对数问题，而不是直接
使用循环群本身。

定义3-7

设H是群G的一个子集合，如果对于群G的结合法，H成为一个
群，那么H就叫作群G的子群。

子群作为群的子集，它本身也是群，为了验证群H是群G的一个
子群，需要验证H是否满足群定义中的所有属性。

定理3-2

假设G是一个循环群，则G内每个满足ord(a)=s的元素a，都是拥
有s个元素的循环子群的生成元。

定理3-2说明循环群内的每个元素都是其子群的生成元，而且生
成的子群也是循环群。

例3-7

假设循环群G= ={3,2,6,4,5,1}，选择循环群G中的元素4作为生
成元，通过生成元4构成一个子群H，子群H各元素计算过程如下：

    128

## Page 129

    41≡4 mod 7，42≡2 mod 7，43≡1 mod 7

    所以，子群H={1,2,4}，子群H中的所有元素都属于循环群G，且
子群H也是一个循环群。循环群G和子群H的关系如图3-1所示。










    图3-1 循环群G和子群H










    129

## Page 130

3.5 域

    介绍完群的概念之后，我们再来讨论密码学中的另一个常用概念
——域。










130

## Page 131

3.5.1 域的基本概念

域在群的基础上增加了新的规则。域是有两个二元运算的集合，
这两个二元运算分别为加法和乘法。

定义3-8

域F是包含加法与乘法运算的集合，且对于域F内的任意元素满
足以下性质：

·F中的所有元素形成了一个加法交换群，群操作为“+”，单位元
为0；

·F中除0以外的所有元素构成了一个乘法交换群，群操作为“·”，
单位元为1；

·当两种运算混合使用时，分配律仍然成立，即对域F内的任意元
素a，b，c都满足a(b+c)=(ab)+(ac)。

简单说，域就是一个集合，我们可以在域上进行加法、减法、乘
法和除法而不脱离该集合。

例3-8

实数集合R是一个域，加法群的单位元为0，集合内每个元素a的
加法逆元为-a，乘法群的单位元为1，集合内每个非零元素a的乘法逆

    131

## Page 132

元为 。

实数集合R符合域的定义，但是整数集合并不符合域的定义，例
如整数2的倒数为0.5，0.5不属于整数集合，整数的倒数不在整数集合
中，所以整数集合肯定不符合域的定义。










132

## Page 133

3.5.2 有限域和素域

  由于无限域在密码学中并没有特殊用途，所以我们还需要缩小讨
论范围。当域中包含有限个元素时，这种域被称为有限域或伽罗瓦
域。域中包含的元素个数称为域的阶。有限域的阶必须是pn，其中p
为素数，n为正整数。阶为pn的有限域通常记作GF(pn)，GF表示伽罗
瓦域（Galois Field）。

  域中的两种操作分别为模整数加法和模整数乘法。为了在素域中
进行算术运算，需要遵守以下规则：

  ·加法和乘法均通过模p实现；

  ·域内任意元素a的加法逆元可以通过a+(-a)=0 mod p计算得到；

  ·域内任意非零元素a的乘法逆元可以通过a·a-1=1计算得到。

  此处需要关注一种特殊情况，当n=1时的有限域GF(p)，这种特殊
的有限域又被称为素域。GF(p)与GF(pn)有着不同的结构，这两种不
同的域的关系如图3-2所示。










    133

## Page 134

        图3-2 域的类型

  本节先来讨论当p=7时有限域GF(7)的结构。表3-8为有限域GF(7)
的加法运算结果，表3-9为有限域GF(7)的乘法运算结果，表3-10为域
内元素的加法逆元和乘法逆元结果。从计算结果中可以看出，有限域
GF(7)满足域的两个基本条件——存在加法逆元和乘法逆元。与表3-3
和表3-4模8运算结果不同，集合Z8={1,2,3,4,5,6,7}通过模8算术运算并
不能构成域，Z8中存在非零元素没有乘法逆元的情况，例如整数4不
存在关于模8的乘法逆元。

        表3-8 有限域GF（7）加法运算










    134

## Page 135

表3-9 有限域GF（7）乘法运算










表3-10 有限域GF（7）加法逆元和乘法逆元




135

## Page 136

  经过有限域GF(7)的讨论之后，我们熟悉了有限域的基本性质。
接着我们把讨论范围继续缩小，讨论当p=2的情况，也就是素域
GF(2)。素域GF(2)是有限域中最简单的域，但却是非常重要的一个有
限域。表3-11为GF(2)加法运算结果和乘法运算结果，从该表可以看
出，GF(7)加法运算等价于异或（XOR）运算，而乘法运算等价于逻
辑与（AND）运算。有限域GF(2)加法逆元和乘法逆元如表3-12所
示。有限域GF(2)在高级加密标准AES算法中至关重要。

      表3-11 有限域GF（2）加法运算和乘法运算








    表3-12 有限域GF（2）加法逆元和乘法逆元










    136

## Page 137

3.5.3 扩展域GF(2m)

     通过有限域的定义可知，有限域的阶必须是pn，其中p为素数，n
为正整数。上面一节描述了当阶为素数时（即n=1）的有限域GF(p)，
有限域GF(p)可满足域定义中的所有条件。本节将讨论n＞1的有限域
GF(p n)，并重点讲解高级加密标准AES算法所使用的扩展域GF(28)。

     密码学中所有算法都在整数集上进行运算。扩展域GF(28)的阶为
28，也就是说扩展域GF(28)中包含256个元素。计算机1字节为8个比
特，扩展域GF(28)中的每一个元素都可以用1字节表示，这也是高级
         8
加密标准AES算法选择扩展域GF(2 )的主要原因。但由于扩展域
GF(2 8)的阶不是素数，有限域内的加法和乘法运算就不能用整数加法
模28和乘法模28表示。为了在扩展域GF(28)内定义运算并使其构成一
个域，扩展域内将使用一种多项式运算来代替算术运算。

     在扩展域GF(28)中，域中元素f(x)使用多项式表示，其中系数ai为
域GF(2)中的元素，多项式最大次数为7。

     f(x)=a7x7+…+a1x+a0

     下面几个节将介绍扩展域加法、减法、乘法和逆操作，其中扩展
域加法是AES算法中的轮密钥加法层的核心操作，扩展域乘法是AES
算法中列混合过程的核心操作，扩展域逆操作是AES算法S盒变化的
核心操作。

         137

## Page 138

    3.5.4 GF(2m)加法和减法

    在扩展域加法和减法运算中，多项式系数的加法和减法操作均在
    域GF(2)中完成。

    定义3-9 扩展域加法和减法

    假设A(x)，B(x)∈GF(2m)，两个元素之和的计算方法为：





    两个元素之差的计算方法为：






   从定义3-9可以看出，扩展域中的加法操作和减法操作完全相
同。加法操作和减法操作可以看作相同位置系数之间的异或操作。下
面通过一个具体示例来说明扩展域加法和减法。

   例3-9 扩展域GF（28）上的加法和减法示例

   计算C(x)=A(x)+B(x)，其中A(x)=x7+x5+x3+1，B(x)=x3+x2+1。计
算过程如下：



    138

## Page 139

   示例中的A(x)按位表示为10101001，B(x)按位表示为00001101，
通过异或运算可得C(x)=A(x)+B(x)=0xA9^0x0D=0xA4。扩展域中多项
式加法运算和减法运算可理解为“相同项抵消，不同项保留”。










    139

## Page 140

3.5.5  GF(2m)乘法

扩展域的乘法操作也在域GF(2)中完成。

定义3-10 计算C(x)=A(x)·B(x)

C(x)=A(x)·B(x)=(am-1xm-1+…+a0)·(bm-1xm-1+…+b0)

C'(x)=c'2m-2x2m-2+…+c0

其中，

c'0=a0b0mod2

…

c'2m-2=am-1bm-1mod 2

计算过程若出现多项式次数大于7的情况，需要对计算结果进行
约简。约简时将两个多项式相乘结果除以一个不可约多项式P(x)，只
保留得到的余数。AES算法中使用的不可约多项式为
P(x)=x8+x4+x3+x+1。

定义3-11 扩展域乘法

假设A(x)，B(x)∈GF(2m)，且P(x)为一个不可约多项式，两个元
素之积的计算方法为：

    140

## Page 141

    C(x)≡A(x)·B(x)mod P(x)

    例3-10 扩展域GF（28）上的乘法示例

    计算C(x)=A(x)·B(x)，其中A(x)=x7+x5+x3+1，B(x)=x3+x2+1










    所以C'(x)=x10+x9+x8+x6+x2+1。由于计算结果中多项式次数大于
7，还需要对C'(x)运算结果进行约简。我们可以通过“竖式除法”的方
式约简C'(x)。具体运算过程如下：










    141

## Page 142

 除了“竖式除法”外，还可以分别约简x8、x9和x10，再计算
x10+x9+x8+x6+x2+1，约简C'(x)。

 P(x)-x 8=(x8+x4+x3+x+1)-x8

 x 8≡x4+x3+x+1 mod P(x)

 x 9=x8 ·x≡x 5+x4+x2+x mod P(x)

 x 10=x9 ·x≡x 6+x5+x3+x2mod P(x)

 所以：

 x 10+x9+x8+x6+x2+1

≡((x6+x5+x3+x2)+(x5+x4+x2+x)+(x4+x3+x+1))+x6+x2+1


 142

## Page 143

≡x2mod P(x)










143

## Page 144

3.5.6 GF(2m)逆操作

扩展域中任何一个非零元素a的逆元b可以通过a·b≡1 mod P(x)计
算得到，其中P(x)为不可约多项式。

对于GF(28)这样的小型域而言，可直接通过预计算得到乘法逆元
表，使用时直接通过查表即可得到某个元素的乘法逆元。除了查表法
之外，还可以通过扩展欧几里得算法计算乘法逆元。表3-13为扩展域
GF(28)中的乘法逆元表。

    表3-13     GF（28）乘法逆元表










例3-11 计算x7+x6+x的乘法逆元

x7+x6+x=(11000010)2=(C2)hex

    144

## Page 145

x7+x6+x的乘法逆元可在表3-13的第C行第2列获得。该表第C行第
2列的值为2F。

(2F)hex=(00101111)2=x5+x3+x2+x+1

所以，x7+x6+x的乘法逆元为x5+x3+x2+x+1。










145

## Page 146

3.6 欧拉函数

定义3-12

    若m是一个正整数，则从1到m中与m互素的整数的个数，记作
φ(m)，通常叫作欧拉（Euler）函数。

    两个数互素也就是它们最大公约数为1，gcd(a,b)=1表示a和b互
素。

    例3-12 计算φ(6)

    当m=6时，计算小于m并且与m互素的正整数的个数。从表3-14
的结果可以看出，只有整数1和5与6互为素数，所以φ(6)=2。

        表3-14   φ(6)计算过程



    例3-13 计算φ(7)

    当m=7时，计算小于m并且与m互素的正整数的个数。从表3-15
的结果可以看出，整数1到6均与7互为素数，所以φ(7)=6。

        表3-15   φ(7)计算过程





    146

## Page 147

   很明显，对于素数p而言，φ(p)=p-1。而当存在两个不相等的素
数p和q，假设n=pq，则有φ(n)=φ(p·q)=φ(p)·φ(q)=(p-1)·(q-1)。

   例3-14 计算φ(15)

   当m=15时，计算小于m并且与m互素的正整数个数。从表3-16的
结果可以看出，整数1、2、4、7、8、11、13和15都与15互为素数，
与15互为素数的个数为8，所以φ(15)=φ(3)×φ(5)=2×4=8。

        表3-16 φ(15)计算过程










    147

## Page 148

3.7 欧拉定理

定理3-3

    设m是大于1的整数，如果a和m互为素数，则aφ(m)≡1(mod m)。

    例3-15

    当m=7，a=2，计算gcm(7,2)=1，φ(7)=6，26≡1(mod 7)










    148

## Page 149

3.8 费马小定理

    费马小定理在公钥密码学和素性检测中有着广泛应用。

定理3-4

    设p是一个素数，则对任意整数a，有ap≡a(mod p)

    当a和p互素时，此定理也可以表示为ap-1≡1(mod p)。从上述公式
中可以看出，费马小定理是欧拉定理的一个特例。

    例3-16

    当p=11，a=2时，211-1≡210≡1024≡1(mod 11)

    费马小定理还可以用于约简指数。

    例3-17 求4103mod 11

    因为整数15和4互为素数，根据费马小定理可知，410≡1 mod 11。

4103≡(410)10(43)≡43≡9 mod 11，所以4103≡9 mod 11。

    可见，通过费马小定理可以约简指数，而不用直接计算4103。







    149

## Page 150

3.9 离散对数

    离散对数是部分公钥算法的理论基础，这些公钥算法包括DH密
钥交换算法与数字签名算法等。










150

## Page 151

3.9.1 模算术–指数

定义3-13

设m是大于1的整数，a是与m互素的正整数，则使am≡1 mod n成
立的最小正整数m叫作a对模n的指数，记作ordm(a)。

如果a对模n的指数是φ(n)，则称a为模n的本原根。本原根的重要
之处在于其模n的幂运算结果各不相同，并且均与n互素。表3-17为所
有小于17的正整数a模17的整数幂，从该表的结果可以看出，每行的
计算结果都有周期性，其中3，5，6，7，10，11，12，14为本原根，
使得a16≡1 mod 17。

    表3-17     模17的整数幂










151

## Page 152

3.9.2 模算术–对数

   对于正实数而言，指数函数的逆函数为对数函数，模运算中也有
类似于对数的概念。对于正实数而言，以x为底y的对数可以表示为
     ，对于本原根为a的素数p，对a进行模p的幂运算可以产生1到
p-1个整数，因此对于任何整数b和素数p的本原根a，都存在唯一的指
数i，使得b≡aimod p成立，其中0≤i≤(p-1)，指数i称为模p下以a为底b
的离散对数，记为d loga,p(b)。一些密码学图书也把指数i称为指标，
记为inda,p(b)。以3为底模17的整数幂如表3-18所示。

        表3-18 以3为底模17的整数幂



    有了指数表和对数表，我们可以通过查表法快速计算逆元。以3
    为底模17的离散对数如表3-19所示。

    表3-19 以3为底模17的离散对数



例3-18 计算7关于模17的乘法逆元

通过对数表可知log3,17(7)=11，也就是311≡7 mod 17。

因为316≡311·35≡1 mod 17，所以311关于模17的逆元为35mod 17。


    152

## Page 153

查阅指数表可得35≡5 mod 17，所以7关于模17的乘法逆元为5，
也就是5·7≡1 mod 17。










153

## Page 154

3.9.3 离散对数问题

对给定的a，x和p，通过y=axmod p计算出y很容易，但是给定y，
a和p计算x却非常困难。离散对数的计算难度与RSA中大整数质因数
分解的难度相同，目前并没有找到有效的方法计算出模为素数的离散
对数问题。

例3-19

p=20000000000000002559是一个素数，假定生成元a=11，给定整
数x=20030428，可以快速计算

y≡a   x≡1134889584997235257 mod p

但是已知y求解x却异常困难。










154

## Page 155

3.10 本章小结

  本章介绍了很多数论的基础知识，虽然这些基础知识较为枯燥难
懂，但是这些理论知识可帮助读者理解后续章的密码技术相关算法，
本章中的多个示例也可以帮助读者掌握这些数论知识。

  本章介绍的素数是密码学的基础，虽然很多人都知道素数，但是
数学家们依然在探索素数的奥秘。本章还介绍了模运算，在之前的初
等数学中我们更关心“商”，而在模运算中我们只关心“余数”。模运算
中也有倒数的概念，但是模运算中的倒数的计算方法和之前初等数学
中的计算方法完全不同。另外本章还介绍了群和域的概念。在3.4节
中，不但介绍了循环群和子群，还引出了群的阶与生成元的概念，这
些概念在后续密码学章节中将会被反复使用。3.5节重点说明了有限
域和素域的概念，为了给高级加密标准AES算法做必要的理论铺垫，
此节还详细介绍了有限域GF(2m)中的加法、减法、乘法和求逆运算。
接着本章介绍了密码学中几个基础函数或定理——欧拉函数、欧拉定
理和费马小定理。费马小定理是欧拉定理的一个特例，费马小定理在
公钥算法和数字签名理论证明中有重要的应用，另外费马小定理还可
以用于快速求解逆元。本章最后介绍了离散对数问题，离散对数问题
是DH密钥交换算法和数字签名算法的基础。







    155

## Page 156

        第4章 单向散列函数

4.1 本章主要内容

  单向散列函数又称安全散列函数或哈希函数，可以根据消息的内
容计算出散列值。散列值又称为消息摘要或摘要，可用于检查消息的
完整性。消息的散列值或摘要就像消息的“指纹”，这种“指纹”长度固
定且不随消息长度的改变而改变。这种固定长度的“指纹”非常简单易
用，所以单向散列函数是密码学工具箱中较为容易理解的部分。在密
码学的发展历程中出现了多种单向散列算法，例如MD4/5系列和SHA
系列等。由于种种原因，MD4/5系列算法已经退出历史舞台，而SHA
系列算法在物联网安全领域较为常用，所以本章将重点介绍SHA256
算法。

  除了介绍SHA256算法之外，本章还将通过几个应用工具介绍
mbedtls中单向散列模块的使用方法。mbedtls提供一个名为
generic_sum的单向散列计算工具，该工具可以计算任意输入文件的
消息摘要。最后本章将通过一个示例介绍单向散列模块的具体使用方
法。









    156

## Page 157

4.2 单向散列函数原理

    单向散列函数是一类满足密码学算法安全属性的特殊散列函数。
输入数据通常称为消息，输出数据通常称为消息摘要或简称为摘要，
可以用来检测消息的完整性。

    本章先通过一个示例介绍单向散列函数的应用场景：假想场景中
Alice需要传送一个文件给Bob，Bob需要知道文件在传输过程中是否
发生了篡改或者传输错误，具体过程如图4-1所示。

    1）Alice准备好待传输文件；

    2）Alice使用单向散列函数计算出文件的消息摘要；

    3）Alice将文件和消息摘要一起发送给Bob；

    4）Bob收到文件后使用相同的单向散列函数计算出文件的消息
摘要；

    5）Bob对比接收到的消息摘要是否与计算得到的消息摘要一
致。









    157

## Page 158

图4-1 单向散列函数应用场景










158

## Page 159

4.2.1 单向散列函数性质

单向散列函数为消息产生了一个“指纹”，为了能够实现对消息的
完整性进行检测，单向散列函数需要满足的性质如表4-1所示。其中
单向散列函数描述为h(x)。

          表4-1 单向散列函数性质










159

## Page 160

    4.2.2 单向散列函数应用


  基于单向散列函数的性质，单向散列函数可以应用在消息认证
码、数字签名、随机数生成器和一次性口令等密码技术中。也可以作
为普通散列函数独立使用，例如用于索引哈希表中的数据、指纹识
别、检测重复数据或唯一标识文件，以及用于校验和检测意外的数据
损坏。下面分别介绍单向散列函数的具体应用。

1.消息完整性检测

  单向散列函数的一个重要应用是对消息的完整性进行检测，例如
可以通过比较传输前后消息（或文件）的摘要值来检测是否发生篡
改。这样大多数数字签名算法只需要确认消息摘要的真实性即可，验
证消息摘要的真实性等同于验证消息本身的真实性。

2.伪随机数生成器

  单向散列函数可以用来构造伪随机数生成算法，它可以用于由单
个密钥派生出多个新的密钥，例如TLS1.2协议中的PRF函数。

3.消息认证码

  在密码学中，消息认证码可以用于检测消息传输过程中的错误、
篡改和伪装，其实现过程依赖于单向散列函数。消息认证码中除了单


    160

## Page 161

向散列函数外还加入了共享密钥，该密钥由发送者和接收者共享，因
此消息认证码不但可以检测消息在传输过程中是否发生了错误或篡
改，还可以对发送者的身份进行认证。

4.数字签名

           由于数字签名的计算过程比较耗时，在对消息计算签名之前，通
常会使用单向散列函数对消息计算消息摘要，然后对消息摘要进行签
名。

5.一次性口令

  单向散列函数可构造一次性口令（one-time password）。服务器
通常使用一次性口令来认证客户端的合法性，客户端使用单向散列函
数计算出令牌和同步资源（例如时间或计数值）的消息摘要，客户端
再把消息摘要发送给服务器进行认证。










161

## Page 162

4.3 单向散列函数的实现方法

    单向散列函数有很多种实现方法，较为常用的实现方法包括
MD4、MD5、SHA-256、SHA-384/512等。本节将介绍MD算法家族
和SHA算法家族。










162

## Page 163

4.3.1 MD算法家族

MD4算法是单向散列函数中较早提出的一个版本，MD5和SHA
算法家族均基于MD4的基本原理设计实现。

·MD4：由Rivest设计的单向散列函数，能够产生128比特的散列
值，其散列碰撞已被攻破。

·MD5：由Rivest设计的单向散列函数，能够产生128比特的散列
值，其抗碰撞性已被攻破。










163

## Page 164

4.3.2 SHA算法家族

  SHA算法的全称为安全散列算法（Secure Hash Algorithms），由
美国国家标准与技术研究所（NIST）制定，该系列算法是美国联邦
信息处理标准（FIPS）的一部分。

  ·SHA0是1993年发布的单向散列算法，可以产生160比特的消息
摘要，是SHA家族的第一个成员。由于未公开的“重大缺陷”，在出版
后不久就被撤销，并被修改后的版本SHA1所取代。

  ·SHA1是一种能够产生160比特消息摘要的单向散列函数，由美
国国家安全局（NSA）设计，作为数字签名算法的一部分。由于
SHA1中存在缺陷，2010年后，大多数安全应用中不再推荐SHA1算
法。

  ·SHA2是由美国国家安全局设计的单向散列函数，包括
SHA256、SHA384和SHA512，其消息摘要长度分别是256比特、384
比特和512比特。

  ·SHA3于2012年被选中，支持与SHA2相同的消息摘要长度，其
内部结构与SHA系列的其他算法并不相同。

  MD算法家族与SHA算法家族的参数对照如表4-2所示。

        表4-2 单向散列函数参数对照

        164

## Page 165

165

## Page 166

4.4 SHA256详细描述

  单向散列函数中的典型实现是SHA256算法，大部分单向散列函
数的构造方法与其类似，详细了解其实现过程对理解密码学相关应用
会有很大帮助。本节将对SHA256的计算过程进行详细描述，部分内
容参考自NIST FIPS 180-4[1]标准规范。算法的输入为小于264比特长
度的任意消息，分组长度为512比特，经过哈希计算得到长度为256比
特的消息摘要。算法框图如图4-2所示，其中H(0)为初始摘要值，k为
常量。










    图4-2 SHA256算法框图

    单向散列函数的计算过程可以分为两个阶段，分别为预处理和哈


    166

## Page 167

希计算。计算过程涉及一些变换操作，这些变换操作如下：










以上计算过程中涉及的运算符描述如表4-3所示。

表4-3 运算符描述





[1]    NIST  FIPS    180-4：Secure        Hash

Standard:http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf










167

## Page 168

4.4.1 预处理

  预处理阶段会对消息进行填充，使消息长度达到512比特的整数
倍，填充完成后会将消息分割为若干个分组。为了方便后续的哈希计
算，还需要对初始摘要值进行初始化，并准备SHA256常量。

1.消息填充

  填充的目的是为了确保消息长度达到512比特的整数倍。假设有
一个长度为L比特的消息，为了让消息的长度达到512比特的整数
倍，会将一个比特1、K个比特0和长度L的二进制表示（64比特）追
加到消息后面。其中K可以表示为：

  K≡512-64-1-L≡448-(L+1)mod 512

  下面通过一个简单示例来描述消息填充的过程。给定一个由3个8
位ASCII字符组成的消息“abc”，首先在末尾加入一个比特1，然后在
后面加入k比特0。消息的最后64比特需要填入消息的原始长度，对
于“abc”而言，其原始长度为24比特，这样可以计算出K的长度为423
比特（K≡512-64-1-24=423 mod 512）。填充后的消息为：




    2.消息分割


    168

## Page 169

  完成消息的填充后，会将其分解为N个512比特的分组
M(1)~M(N)，分组长度512比特可以用16个32比特表示，第1个32比特
可以表示为 ，依此类推到 。




3.设置初始摘要值

  在消息摘要计算之前，必须设置初始的散列值H(0)，初始值的大
小和数量取决于消息摘要的长度。对于SHA256算法，初始的散列值
H(0)将包含以下8个32比特的数值，十六进制表示如下：










    169

## Page 170

    4.准备常量

    SHA256计算过程中需要用到一系列的常量字，表示为
        ，十六进制表示如下（从左到右）：




428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5
d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174
e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da
983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967
27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85
a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070
19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a 5b9cca4f 682e6ff3
748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2










    170

## Page 171

    4.4.2 哈希计算

    预处理阶段完成后可以正式开始哈希计算。哈希计算过程分为4
    个步骤，分别为消息调度、初始化工作寄存器、更新工作寄存器和计
    算消息摘要，本节会对每个步骤进行详细描述。计算过程中N为分组
    个数，i为计算次数（1≤i≤N）。

    1.消息调度

    预处理阶段会用16个32比特（  ）来表示每个消息分
    组，消息调度过程使用这16个32比特作为输入。消息调度过程表达式
    如下：





  从计算过程中可以看出，当0≤t≤15时，Wt的值等于消息分组中的
对应值，当16≤t≤63时，Wt的值由前4个值计算得到。消息调度计算过
程如图4-3所示。










    171

## Page 172

图4-3     消息调度计算过程

2.初始化工作寄存器

消息调度完成后会对8个32比特工作寄存器（a,b,c,d,e,f,g,h）进行
初始化，当i=1时，8个工作寄存器的值等于预处理阶段设置的初始摘
要值H(0)。初始化工作寄存器过程表达式如下：







3.更新工作寄存器

初始化工作寄存器后，需要通过计算对8个工作寄存器进行更
新，更新过程分为64轮（0≤t≤63），每一轮处理256位的消息分组。
该过程的变化步骤如下：



172

## Page 173

更新工作寄存器的每一轮的变化过程如图4-4所示。










173

## Page 174

    图4-4 更新工作寄存器示意图

4.计算消息摘要

完成更新工作寄存器后，可通过8个工作寄存器的值计算出中间
摘要值 。更新过程表达式如下：





每次处理完单个消息分组后，新的摘要值将替换旧的摘要值，最
后一个摘要值H(N)作为最终的摘要值输出。







174

## Page 175

4.4.3 具体示例

下面给出NIST所提供的SHA256示例[1]，示例中使用“abc”作为消
息，其计算过程如下（由于篇幅限制，只截取了部分输出结果）。

·消息填充










·初始摘要值










175

## Page 176

    ·更新工作寄存器，前两轮和后两轮




    a b c d e f g h
6A09E667 BB67AE85 3C6EF372 A54FF53A 510E527F 9B05688C 1F83D9AB 5BE0CD19
5D6AEBCD 6A09E667 BB67AE85 3C6EF372 FA2A4622 510E527F 9B05688C 1F83D9AB
// 省略中间过程
D39A2165 04D24D6C B85E2CE9 B6AE8FFF FB121210 948D25B6 961F4894 B21BAD3D
506E3058 D39A2165 04D24D6C B85E2CE9 5EF50F24 FB121210 948D25B6 961F4894




    ·计算消息摘要










    176

## Page 177

    最终摘要值为：


   BA7816BF 8F01CFEA 414140DE 5DAE2223 B00361A3 96177A9C B410FF61 F20015AD

[1] NIST SHA256示例网址如下：

https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-

Guidelines/documents/examples/SHA256.pdf










    177

## Page 178

4.5 mbedtls单向散列应用工具

      mbedtls为各个模块提供了应用工具，应用工具主要展示了模块
接口的使用方法。mbedtls单向散列模块提供了两个示例应用程序，
分别为hello和generic_sum，下面分别介绍示例应用工具的使用方
法。










178

## Page 179

4.5.1  hello

                     hello通常作为mbedtls安装是否成功的验证工具，应用工具使用
MD5算法计算“Hello,world!”的消息摘要，并打印到终端。hello应用
工具的使用方法如下：

# 执行hello指令
$ hello
MD5('Hello, world!') = 6cd3556deb0da54bca060b4c39479839










179

## Page 180

4.5.2 generic_sum

  generic_sum是一个对文件计算消息摘要的工具，分为打印模式
和校验模式。打印模式用于计算文件的消息摘要值，校验模式用于验
证消息摘要的正确性。generic_sum应用工具的参数描述如表4-4所
示。

    表4-4     generic_sum参数描述










  generic_sum应用工具的使用方法如下：

# 准备测试文件
$ echo -n "abc" > msg.txt
# 使用SHA256算法计算消息摘要
$ generic_sum SHA256 msg.txt
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad msg.txt










180

## Page 181

4.6 mbedtls SHA256示例

    mbedtls提供了单向散列模块（Hashing），可以生成固定长度的
消息摘要来检测数据是否被篡改。模块中的每种算法均以独立子模块
的形式存在，可以在编译时选择是否开启。除了独立子模块接口外，
mbedtls还提供了md通用接口。md通用接口形式一般为
mbedtls_md_xx，位于{mbedtls代码仓库}/include/mbedtls/md.h文件
中，用户使用时可以根据需求灵活选择具体算法和接口形式。
mbedtls单向散列模块中也包含消息认证功能（HMAC），可以与对
称加密模块结合使用，用来检测消息的完整性。mbedtls所支持的单
向散列算法如表4-5所示。本节主要介绍单向散列相关内容，HMAC
部分在第6章进行讲解。

    表4-5  mbedtls所支持的单向散列算法










181

## Page 182

4.6.1 示例描述

  本节基础示例用于展示如何使用mbedtls md通用接口计算消息摘
要。示例代码参考自mbedtls示例代码，在mbedtls示例代码的基础上
增加或修改了部分内容。本章示例均基于Zephyr系统构建，借助
Zephyr系统良好的适配性，本章示例不但可运行于Linux平台，也可
运行于STM32F429等硬件平台。为了正确运行示例代码，需要在
mbedtls_config.h配置文件中增加相关宏定义，宏定义描述如表4-6所
示。

        表4-6 mbedtls_config.h宏定义描述








  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书代码仓库。本章示例位于04_hash文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本章示例，其他应用请根据实
际情况修改。








    182

## Page 183

4.6.2 示例代码

代码清单4-1将使用md通用接口，以消息“abc”作为测试样本，使
用SHA256算法计算消息摘要，SHA256的分组长度为64字节，输出32
字节的消息摘要。

代码清单4-1 单向散列函数示例



#include <zephyr.h>
#include <stdio.h>
#include <string.h>
#include "mbedtls/md.h"
#include "mbedtls/platform.h"
static void dump_buf(char *info, uint8_t *buf, uint32_t len)
{
 mbedtls_printf("%s", info);
 for (int i = 0; i < len; i++) {
 mbedtls_printf("%s%02X%s", i % 16 == 0 ? "\n\t":" ",
           buf[i], i == len - 1 ? "\n":"");
 }
 mbedtls_printf("\n");
}
int main(void)
{
 uint8_t digest[32];
 char *msg = "abc";
 mbedtls_md_context_t ctx;
 const mbedtls_md_info_t *info;
 mbedtls_platform_set_printf(printf);
 mbedtls_md_init(&ctx);
 info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
 mbedtls_md_setup(&ctx, info, 0);
 mbedtls_printf("\n md info setup, name: %s, digest size: %d\n",
     mbedtls_md_get_name(info), mbedtls_md_get_size(info));
 mbedtls_md_starts(&ctx);
 mbedtls_md_update(&ctx, msg, strlen(msg));
 mbedtls_md_finish(&ctx, digest);
 dump_buf("\n md sha-256 digest:", digest, sizeof(digest));
 mbedtls_md_free(&ctx);
 return 0;
}



示例中所使用的接口描述如表4-7所示。

 表4-7 单向散列函数示例相关接口描述

     183

## Page 184

184

## Page 185

4.6.3 代码说明

单向散列函数示例如图4-5所示。










    图4-5 单向散列函数示例简图

1.准备测试样本

  测试样本来自NIST提供的SHA256示例，试样本内容如表4-8所
示。

    表4-8 单向散列函数测试样本






185

## Page 186

2.选择算法并分配内部结构

    示例代码中使用SHA256作为单向散列算法，通过算法类型可以
得到md信息结构体指针，md信息结构体名称为mbedtls_md_info_t，
位于{mbedtls代码仓库}include/mbedtls/md_internal.h文件中，该结构
体是对单向散列算法的抽象，结构体中包含了单向散列算法中必要的
参数及接口。


    struct mbedtls_md_info_t
    {
      mbedtls_md_type_t type;
      const char * name;
      int size;
      int block_size;
      int (*starts_func)( void *ctx );
      int (*update_func)( void *ctx, const unsigned char *input, size_t ilen );
      int (*finish_func)( void *ctx, unsigned char *output );
      int (*digest_func)( const unsigned char *input,
                  size_t ilen, unsigned char *output );
      void * (*ctx_alloc_func)( void );
      void (*ctx_free_func)( void *ctx );
      void (*clone_func)( void *dst, const void *src );
      int (*process_func)( void *ctx, const unsigned char *input );
    };


    得到具体算法的信息结构体指针后，通过mbedtls_md_setup接口
完成内部赋值操作，设置完成后便可以使用md通用接口计算消息摘
要。

3.计算消息摘要

    计算消息摘要过程一般以“start_update_finish”的形式展开。md启
动接口为mbedtls_md_starts，该接口需要输入md结构体，内部会对8
个工作寄存器进行初始化。mbedtls_md_starts接口原型如下：



      186

## Page 187

    int mbedtls_md_starts( mbedtls_md_context_t *ctx );

   md更新接口为mbedtls_md_update，该接口需要输入md结构体、
消息和消息长度。内部处理时会按照分组长度进行更新计算。如果消
息长度不是分组长度的整数倍，则剩余部分将先保存在md内部结构
    体中。换句话说，mbedtls_md             _update可以被调用多次，应用程序可
    以随时通过mbedtls_md_update填入消息。mbedtls    _md_update接口原
    型如下：

    int mbedtls_md_update( mbedtls_md_context_t *ctx,
        const unsigned char *input, size_t ilen );

   md完成接口为mbedtls_md_finish，该接口需输入md结构体，本
示例将输出长度为32字节的摘要值。mbedtls_md_finish接口原型如
下：

    int mbedtls_md_finish( mbedtls_md_context_t *ctx,
        unsigned char *output);

   总之，mbedtls_md_starts接口只需调用一次，而
mbedtls_md_update接口可调用多次，最后通过mbedtls_md_finish接口
获得期望结果。










    187

## Page 188

4.6.4 编译与运行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     示例中开启了md通用接口和SHA256算法，从编译结果可以看
出，本示例共消耗约5KB RAM空间，约17KB FLASH空间。编译与
运行过程如下：




    # 进入示例代码文件夹
    $ cd 04_hash
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region         Used Size Region Size %age Used
             FLASH:        17636 B     2 MB         0.84%
               CCM:           0 GB    64 KB         0.00%
              SRAM:         5404 B   256 KB         2.06%
          IDT_LIST:          200 B     2 KB         9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    md info setup, name: SHA256, digest size: 32
    md sha-256 digest:
          BA 78 16 BF 8F 01 CF EA 41 41 40 DE 5D AE 22 23
          B0 03 61 A3 96 17 7A 9C B4 10 FF 61 F2 00 15 AD









          188

## Page 189

4.7 本章小结

   本章介绍了单向散列函数的性质、应用和实现方法。单向散列函
数的计算结果称为消息摘要，消息摘要不随消息长度的变化而变化，
例如MD5的消息摘要长度为128位，SHA256的消息摘要长度为256
位。本章还简单介绍了单向散列算法的发展历史，通过这些发展可以
发现单项散列算法并不是牢不可破的，建议在实际使用中以SHA256
为主。除了介绍原理之外，本章还介绍了mbedtls单向散列模块的使
用方法，mbedtls可通过修改配置文件的方式裁剪单向散列模块。使
用单向散列模块时，一般以“start_update_finish”的形式展开，
mbedtls_md_start完成初始化工作，mbedtls_md_start在应用程序中仅
需调用一次，而mbedtls_md_update可被多次调用，也就是说可以在
应用程序的任意位置插入消息内容，最后通过mbedtls_md_finish获得
消息摘要。单向散列函数和其他密码技术息息相关，它是物联网安全
应用的重要组成部分。










    189

## Page 190

        第5章 对称加密算法

5.1 本章主要内容

  本章将重点介绍高级加密标准AES算法。AES算法是当前比较流
行的对称加密算法，其接口简单，使用方便，非常适合物联网安全应
用。在介绍AES算法之前，本章先介绍3种分组密码模式：ECB、
CBC和CTR。除了分组密码模式之外，本章还将介绍PKCS#7填充方
法。AES算法虽然接口简单，使用方便，但其实现原理却非常复杂，
其实现过程大致可分为字节替换、行移位、列混合、轮密钥加法和轮
密钥生成等阶段。本章的实例部分将介绍两个mbedtls应用工具：
aescrypto和crypt_and_hash。除了工具介绍之外，本章最后还包括一
个使用mbedtls cipher通用接口实现AES加密和解密的示例。










    190

## Page 191

5.2 对称加密算法原理

  对称加密算法是一种使用相同的密钥加密明文和解密密文的密码
算法，通信双方持有相同的密钥，该密钥被称为共享密钥或对称密
钥。第三方窃听到密文后，由于没有密钥则无法还原明文。这里先通
过一个假想示例来说明对称加密算法的应用场景。假想场景中，
Alice和Bob都持有一个共享密钥。Alice需要发送某消息给Bob，为了
保证消息的安全性，Alice将使用对称密钥对消息进行加密，并将密
文发送给Bob。被加密的消息称为明文，而加密的结果称为密文。
Bob收到密文后使用对称密钥对密文进行解密从而得到消息。如图5-1
所示为对称加密算法的简化模型。










    191

## Page 192

        图5-1 对称加密算法简化模型

  市面上有多种对称加密算法，例如AES、DES和3DES，这些对
称加密算法都能满足图5-1中所描述的使用场景，但是这些对称加密
算法单次只能处理一个固定长度的分组数据，例如AES算法单次只能
加密或解密128位数据，而实际场景中被AES加密或解密的消息长度
并不是128位的整数倍。为了解决这种矛盾，下面两节将介绍分组密
码模式和消息填充方法。








    192

## Page 193

5.3 分组密码模式

  分组密码只能加密或解密固定长度的数据，如果需要加密的明文
长度超出了分组长度，就需要对明文进行分组处理，然后对各分组进
行加密或解密处理。不同的分组密码模式有不同的计算过程，安全性
也存在差异。本节将介绍几种常用的模式，分别为ECB模式、CBC模
式和CTR模式。










    193

## Page 194

5.3.1 ECB（电子密码本）模式

  电子密码本（Electronic Codebook）模式是最简单的分组加密模
式，该模式将明文进行分组加密，加密结果为密文分组。ECB模式非
常简单，但是由于它存在明显的缺点，所以在实际项目中往往被禁止
使用。ECB模式中明文和密文存在一一对应关系，一个明文总是对应
一个长度相等的密文，这种对应关系可以理解为一张巨大的“明文—
密文”对应表。ECB模式下加密和解密过程如图5-2所示。ECB模式虽
然非常简单，但它却是理解分组加密模式的“窗口”。










    194

## Page 195

图5-2 ECB模式加密和解密过程










195

## Page 196

5.3.2 CBC（密码分组链接）模式

  在密码分组链接（Cipher Block Chaining）模式中，每一组明文
在加密前都与前面的密文分组进行异或操作。由于第一个明文分组前
面没有密文分组，所以需要准备一个与密文分组长度相等的比特序列
来代替密文分组，这个比特序列被称作初始化向量（Initialization
Vector），通常简写为IV。CBC模式是一种常用的分组加密模式，其
加密和解密过程如图5-3所示。

  若Alice和Bob在通信时使用CBC分组密码模式，那么除了具有相
同的对称密钥之外，还需要具有相同的初始化向量。若每次Alice和
Bob通信时使用不同的初始化向量，那么即使被加密的消息完全相
同，加密得到的密文也不会相同。这样第三方窃听者就无法获得明文
和密文的对应关系。

  一般情况下可使用伪随机数生成器派生初始化向量IV，初始化向
量IV绝不能被预测，但加密方可以通过某种明文方式把初始化向量
IV传递至解密方。










    196

## Page 197

图5-3 CBC模式加密和解密过程










197

## Page 198

5.3.3 CTR（计数器）模式

  CTR（计数器）模式由NIST作为标准提出，NIST SP800-38A中
包含CTR规范的详细描述。CTR模式使用与分组长度相同的计数值参
与运算，典型的实现方法是通过对逐次累加的计数器进行加密来生成
密钥流，通过加密计数器得到的密钥流与明文分组进行异或运算，得
到密文分组。CTR模式的加密和解密过程如图5-4所示。

  若明文长度不是分组长度的整数倍，假设最后一个明文分组N的
长度为L位，那么最后一个明文分组N只需与计数器N加密结果的左侧
L位异或，获得的密文分组N的长度也是N位。这种算法结构使得CTR
模式不需要对明文进行填充。最后一个明文分组的处理过程如图5-5
所示。

  与ECB模式和CBC模式相比，CTR模式具有很多优点，主要体现
在软件效率、随机访问特性和简单性等方面。










    198

## Page 199

图5-4 CTR模式加密和解密过程



199

## Page 200

        图5-5 最后一个明文分组处理过程

  ·软件效率：CTR模式能够支持并行计算，因此可以充分利用支
持并行计算的各类处理器，通过并行计算大大提高对称加密算法的效
率，减少计算时间。

  ·随机访问特性：在CBC模式中，当前密文分组的解密过程依赖
于前一个密文分组。一旦前一个密文分组遭到破坏，那么之后所有密
文分组都将无法正确解密。而在CTR模式中不存在这种情况，即使有
一个密文分组受到破坏也会不影响其他密文分组的解密过程。

  ·简单性：不同于ECB模式和CBC模式，CTR模式仅需要加密算

        200

## Page 201

法而不需要解密算法，这点在加密过程和解密过程不同时尤为重要。
而且，CTR模式不需要对明文进行填充处理。










201

## Page 202

5.4 PKCS7填充方案

  部分分组密码模式中要求输入明文长度为分组密码长度的整数
倍，例如ECB和CBC模式。当待加密明文长度不是分组密码长度的整
数倍时，通常需要对明文进行填充。在实际应用中，常用的填充方案
是PKCS7。PKCS7填充方法非常简单，以AES-CBC算法为例，分组
长度为16字节，若待加密明文为28字节，则需要在明文末尾填充4字
节04，使其达到分组长度的整数倍；若待加密数据恰好为16字节，需
要在明文后面额外填充16字节，并将其全部填充为16，如图5-6所
示。










    图5-6 PKCS7填充方式

    在应用PKCS7填充方案时，当明文长度为分组长度的整数倍时，


    202

## Page 203

    若使用CBC分组加密模式，其最终密文长度将增加一个分组长度，例
    如分组长度为16字节，明文长度为32字节，那么经过PKCS7填充之
    后，明文长度变为32+16=48字节，最终密文长度为48字节，而不是
    明文填充之前的32字节。若没有这样的填充规则，当明文的最后1字
    节为01时，解密方将无法判断被解密之后的明文是否经过填充操作；
    而额外增加一个分组长度作为填充，很好地解决了这种容易被混淆的
    问题。这种容易被混淆的问题如图5-7所示。










        图5-7 PKCS7填充规则

  注意：TLS/DTLS协议中也可使用CBC模式加密明文，但是
TLS/DTLS协议中规定的填充方式与PKCS7填充方案不同。







    203

## Page 204

5.5 AES算法概述

  下面让我们开始本章的重点内容——AES算法。AES算法是由美
国国家标准技术研究所在2001年发布的高级加密标准。AES算法是一
个对称分组加密算法，其固定分组大小为128位（16字节），密钥长
度为128、192或256位。密钥长度用于指定将明文转换为密文所需的
变化轮数。当密钥长度为128位时，轮数为10；当密钥长度为192为
时，轮数为12；当密钥长度为256位时，轮数为14。AES输入和输出
参数情况如图5-8所示。










        图5-8 AES算法输入输出参数情况

  AES算法执行加密过程时，将消息分成若干个16字节的消息分
组，第一个16字节明文首先经过密钥加法层，与轮密钥进行异或操
作。除最后一轮外，其他每轮操作包括字节替换层、行移位层、列混
合层、轮密钥加法层。AES算法加密和解密执行过程如图5-9所示。

        204

## Page 205

图5-9 AES算法加密和解密过程




205

## Page 206

5.6 AES算法详细说明

  本节将对AES算法进行详细描述，部分内容参考了NIST FIPS
197[1]。AES算法的计算过程运行在一个4×4的字节矩阵上，该矩阵又
称为“状态”（State）。AES算法的所有运算均按字节进行，加减乘除
运算均在扩展域GF(28)内完成，这部分内容可以回顾第3章相关内
容。若有16字节输入内容（a0~a15），那么这些输入字节的状态如图
5-10所示。










        图5-10 AES状态矩阵输入内容

           同样，密钥字节也通过矩阵方式描述，其行数固定为4，列数由
    密钥长度决定。128位密钥的列数为4；192位密钥的列数为6；256位
    密钥的列数为8。若密钥的长度为128位（K0~K15），那么该密钥如
    图5-11所示。




    206

## Page 207

       图5-11   AES状态矩阵密钥内容
[1]    NIST    FIPS       197：

https://csrc.nist.gov/csrc/media/publications/fips/197/final/documents/fips-

197.pdf










207

## Page 208

5.6.1 字节替换

  在图5-9中，每轮的第一层总是字节替换，字节替换将输入的16
字节通过S盒进行替换，S盒的输入和输出都为8位，这样每个输入字
节Xi都会被替换成另一个字节Yi。字节替换过程如图5-12所示。

  S盒是AES算法中唯一的非线性实现，解密过程需要完成S盒的逆
转，所以S盒代换被设计成双向映射，即28=256个可能的输入元素都
与输出元素一一对应。在软件实现中，S盒计算通常通过查表法实
现，如表5-1所示。










    图5-12  字节替换过程
    表5-1 AES算法的S盒






    208

## Page 209

若输入字节为0xE2，取表中第E行第2列，替换后的字节为
0x98，字节替换示例如图5-13所示。










图5-13 字节替换示例




209

## Page 210

5.6.2 行移位

行移位变换将矩阵的第2行向右移动3字节，将第3行向右移动2字
节，将第4行向右移动1字节，第1行保持不变。行移位的目的是增加
AES算法的扩散属性。行移位原理如图5-14所示，行移位示例如图5-
15所示。










图5-14 行移位原理










图5-15 行移位示例





210

## Page 211

5.6.3 列混合

  列混合是一个线性变换的过程，使得每个输入字节对4个输出字
节造成影响，变换后的状态矩阵中的每个元素是固定矩阵中的一行和
输入矩阵一列对应元素的乘积之和，其中的加法和乘法都是在扩展域
GF(28)内完成的。列混合原理如图5-16所示，列混合示例如图5-17所
示。










图5-16 列混合原理










211

## Page 212

图5-17 列混合示例










212

## Page 213

5.6.4 轮密钥加法

状态矩阵中的每一字节都与该轮密钥做异或运算，而每个轮密钥
由轮密钥生成算法计算得到。轮密钥加法原理如图5-18所示，轮密钥
加法示例如图5-19所示。










图5-18 轮密钥加法原理







213

## Page 214

图5-19 轮密钥加法示例










214

## Page 215

5.6.5 轮密钥生成

  原始输入密钥将被扩展为n个轮密钥，轮密钥的个数等于轮数加
1。对于长度为128位的密钥而言，轮数为10则轮密钥的个数为11。
AES算法的轮密钥通过递归计算得到，也就是说通过轮密钥ni-1可计
算得到轮密钥ni。轮密钥生成过程按字计算，轮密钥存储在一个由字
组成的数组W中，每个轮密钥的长度等于原始密钥长度，如128位、
192位或256位。假设密钥长度为128位，则轮密钥个数为11，轮密钥
将存储在数组W[0]~W[43]中、轮密钥的生成过程如图5-20所示，其中
K0~K15为原始密钥。










    215

## Page 216

  图5-20     AES轮密钥生成

  首先将原始密钥按字转换到W[0]~W[3]中，其他轮密钥的计算方
法如下，其中i为轮密钥个数，j为1、2、3。

  ·最左侧数组元素：W[4i]=W[4(i-1)]+g(W[4i-1])

  ·其他3个数组元素：W[4i+j]=W[4i+j-1]+W[4(i-4)+j]

  在计算最左侧元素时使用到了函数g。函数g先将4字节输入执行
行移位操作，再执行S盒替换操作，最后将首字节与轮密钥常量
RCON在有限域相加。轮密钥常量为有限域GF(28)中的一组元素，
mbedtls中轮密钥常量定义如下：

static const uint32_t RCON[10] =
{
  0x00000001, 0x00000002, 0x00000004, 0x00000008,
  0x00000010, 0x00000020, 0x00000040, 0x00000080,
  0x0000001B, 0x00000036
};

  函数g中通过S盒替换可增加轮密钥生成中的非线性，消除AES算
法对称性，以抵抗某些分组密码的攻击。










  216

## Page 217

    5.7 AES算法动手实践

        下面给出NIST FIPS 197中提供的一个AES-ECB-128算法示例，
    示例中所使用的明文、密钥和密文的十六进制表示如表5-2所示。

        表5-2 AES-ECB-128算法示例




   示例中密钥长度为128比特，轮数为10轮，轮开始、字节替换、
行移位、列混合、轮密钥及最终输出情况如表5-3所示。

        表5-3 AES-ECB-128算法示例










    217

## Page 218

218

## Page 219

    5.8 mbedtls对称加密应用工具

  mbedtls为各个模块提供了相应的应用工具，应用工具主要展示
了模块接口的使用方法。mbedtls对称密码模块包括两个示例应用工
具，分别为aescrypt2和crypto_and_hash。下面分别介绍这两个应用工
具的使用方法。










    219

## Page 220

5.8.1 aescrypto2

     aescrypto2应用工具用于演示如何通过mbedtls AES功能对文件内
容进行加密或解密，aescrypto2的实现代码详见{mbedtls代码仓
库}/programs/aes/aescrypt2.c。aescrypto2相关参数描述如表5-4所示。



    $ aescrypt2
    aescrypt2 <mode> <input filename> <output filename> <key>
    <mode>: 0 = encrypt, 1 = decrypt
    example: aescrypt2 0 file file.aes hex:E76B2413958B00E193



    表5-4 aescrypto2参数描述






     aescrypto2使用AES-128-ECB模式对输入文件进行加解密操作，
并通过HMAC算法产生消息认证码，加解密结果和消息认证码将会被
输出到指令文件中。该工具主要用于限制mbedtls AES相关接口的使
用方法，但该示例工具并没有太多的实际意义。aescrypto2具体使用
方法如下：




    # 准备测试样本
    $ echo -n "hello world!" > file
    # 使用aescrypt2 对文件进行加密并认证
    $ aescrypt2 0 file file.aes hex:E76B2413958B00E193
    # 通过hexdump工具查看输出文件
    $ hexdump -C file.aes
    00000000 7f 3d 9c fa 23 4f 4e 1c c1 07 04 15 e8 73 a2 ac |.=..#ON......s..|
    00000010 53 76 0f 49 6f 56 f7 1e 95 71 39 95 71 e0 bf db |Sv.IoV...q9.q...|
    00000020 cd 93 b2 c8 ac db b9 c4 df 12 41 4b 42 73 27 c2 |..........AKBs'.|
    00000030 ae ae 38 5b ae a8 2f c9 8b e9 05 57 f4 86 3b 31 |..8[../....W..;1|
    00000040



    220

## Page 221

    分析aescrypto2的实现代码可以发现，aescrypto2.c中仅调用了
AES模块的相关原生接口，例如mbedtls_aes_init、
mbedtls_aes_setkey_enc和mbedtls_aes_setkey_dec。通过aescrypto2.c，
读者可以快速熟悉mbedtls AES模块原生接口的使用方法，但在实际
应用中依然推荐使用cpiher通用接口。










    221

## Page 222

5.8.2 crypt_and_hash

     crypt_and_hash应用工具用于演示如何使用cipher通用接口和md
通用接口。crypt_and_hash应用工具可指定对称加密算法和单向散列
算法，该工具可对输入文件进行加密并计算消息摘要，最终把输出结
果保存在指定的文件中。crypt_and_hash的实现代码详见{mbedtls代码
仓库}/programs/aes/crypt_and_hash.c。crypt_and_hash的应用工具相关
参数描述如表5-5所示。


    $ crypt_and_hash
    crypt_and_hash <mode> <input filename> <output filename> <cipher> <mbedtls_md> <key>
    <mode>: 0 = encrypt, 1 = decrypt
    example: crypt_and_hash 0 file file.aes AES-128-CBC SHA1 hex:E76B2413958B00E193

        表5-5     crypt_and    _hash参数描述








    crypt_and_hash应用工具具体使用方法如下：

    # 准备测试样本
    $ echo -n "hello world!" > file
    # 使用aescrypt2 对文件进行加密并认证
    $ crypt_and_hash 0 file file.aes AES-128-CBC SHA256 hex:E76B2413958B00E193
    # 通过hexdump工具查看输出文件
    $ hexdump -C file.aes
    00000000 7f 3d 9c fa 23 4f 4e 1c c1 07 04 15 e8 73 a2 ac |.=..#ON......s..|
    00000010 9d cd 06 21 5d c7 97 70 b0 27 18 87 2e 36 08 e1 |...!]..p.'...6..|
    00000020 51 59 2c 15 3e 70 93 0a f7 ff 1d b5 dd f5 ba a1 |QY,.>p..........|
    00000030 5a 0e 2e 4c b5 51 54 35 4b dd 4e 9e 3b 86 05 be |Z..L.QT5K.N.;...|


    222

## Page 223

5.9 mbedtls AES示例

   本节将介绍使用AES CBC模式和AES CTR模块加密消息。
mbedtls提供了对称密码模块（cipher），对称密码模块中的各种算法
都可以作为子模块独立存在，可在编译时选择开启或关闭。除了子模
块的独立接口外，mbedtls还提供了相应的cipher通用接口，接口形式
一般为mbedtls_cipher_xxx，这些接口定义详见{mbedtls代码仓
库}/include/mbedtls/cipher.h文件，用户使用时可根据需要灵活选择相
关算法和接口形式。mbedtls对称加密算法模块所支持的对称加密算
法及相应分组加密模式如表5-6所示。

        表5-6 mbedtls对称加密算法










    223

## Page 224

5.9.1 示例描述

   本节基础示例用于展示mbedtls cipher通用接口的使用方法。示例
代码参考自mbedtls示例代码，在mbedtls示例代码的基础上增加或修
改了部分内容。本章示例均基于Zephyr系统构建，借助Zephyr系统良
好的适配性，本章示例不但可运行于Linux平台，也可运行于
STM32F429等硬件平台。为了正确运行示例代码，需要在
mbedtls_config.h配置文件中增加相关宏定义，如表5-7所示。

       表5-7 mbedtls_config.h配置文件宏定义描述









   注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书代码仓库。本章示例位于05_aes文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本章示例，其他应用请根据实
际情况修改。








    224

## Page 225

5.9.2 示例代码

      示例代码（见代码清单5-1）将使用cipher通用接口完成消息加密
操作。和md通用接口的使用方法类似，首先通过算法类型获取对应
的算法信息结构体指针，然后通过配置接口设置算法计算过程中的中
间函数，最后完成消息的加解密操作。在mbedtls配置文件中可以指
定填充方式，示例中开启了PKCS7填充方案。CBC模式时，54字节的
明文加密后将获得64字节的密文；CTR模式时，密文长度和明文长度
相同。示例中相关接口描述如表5-8所示。

      代码清单5-1 对称加密算法示例



    #include <zephyr.h>
    #include <string.h>
    #include <stdio.h>
    #include "mbedtls/cipher.h"
    #include "mbedtls/platform.h"
    char *ptx = "CBC has been the most commonly used mode of operation.";
    uint8_t key[16] =
    {
      0x06, 0xa9, 0x21, 0x40, 0x36, 0xb8, 0xa1, 0x5b,
      0x51, 0x2e, 0x03, 0xd5, 0x34, 0x12, 0x00, 0x06
    };
    uint8_t iv[16] =
    {
      0x3d, 0xaf, 0xba, 0x42, 0x9d, 0x9e, 0xb4, 0x30,
      0xb4, 0x22, 0xda, 0x80, 0x2c, 0x9f, 0xac, 0x41
    };
    static void dump_buf(char *info, uint8_t *buf, uint32_t len)
    {
      mbedtls_printf("%s", info);
      for (int i = 0; i < len; i++) {
      mbedtls_printf("%s%02X%s", i % 16 == 0 ? "\n\t":" ",
          buf[i], i == len - 1 ? "\n":"");
      }
      mbedtls_printf("\n");
    }
    int cipher(int type)
    {
      size_t len;
      int olen = 0;
      uint8_t buf[64];
      mbedtls_cipher_context_t ctx;


      225

## Page 226

 const mbedtls_cipher_info_t *info;
 mbedtls_platform_set_printf(printf);
 mbedtls_cipher_init(&ctx);
 info = mbedtls_cipher_info_from_type(type);
 mbedtls_cipher_setup(&ctx, info);
 mbedtls_printf("\n cipher info setup, name: %s, block size: %d\n",
              mbedtls_cipher_get_name(&ctx),
              mbedtls_cipher_get_block_size(&ctx));
 mbedtls_cipher_setkey(&ctx, key, sizeof(key)*8, MBEDTLS_ENCRYPT);
 mbedtls_cipher_set_iv(&ctx, iv, sizeof(iv));
 mbedtls_cipher_update(&ctx, ptx, strlen(ptx), buf, &len);
 olen += len;
 mbedtls_cipher_finish(&ctx, buf + len, &len);
 olen += len;
 dump_buf("\n cipher aes encrypt:", buf, olen);
 mbedtls_cipher_free(&ctx);
 return 0;
}
int main(void)
{
 cipher(MBEDTLS_CIPHER_AES_128_CBC);
 cipher(MBEDTLS_CIPHER_AES_128_CTR);
 return 0;
}



 表5-8 对称加密算法示例相关接口描述










              226

## Page 227

5.9.3 代码说明

对称加密算法示例如图5-21所示。










图5-21 对称加密算法示例简图

1.准备测试样本

示例测试样本如表5-9所示。

    表5-9 对称加密算法测试样本









227

## Page 228

2.选择算法并分配内部结构

     示例代码中选择AES_128_CBC和AES_128_CTR作为对称加密模
式，通过算法类型可以得到cipher信息结构体指针，cipher信息结构体
名称为mbedtls_cipher_info_t，位于{mbedtls代码仓
库}/include/mbedtls/cipher.h文件中，该结构体中包含了对称密码算法
中必要的参数及接口。


    typedef struct {
    mbedtls_cipher_type_t type;
    mbedtls_cipher_mode_t mode;
    unsigned int key_bitlen;
    const char * name;
    unsigned int iv_size;
    int flags;
    unsigned int block_size;
    const mbedtls_cipher_base_t *base;
    } mbedtls_cipher_info_t;


     得到cipher信息结构体指针后，通过mbedtls_cipher_setup接口完
成内部赋值操作，设置完成后便可使用cipher通用接口执行加密或解
密操作。

    3.对称加密过程


    228

## Page 229

    与第4章的示例类似，对称加密算法示例中同样
以“starts_update_finish”的形式展开，不同的是cipher通用接口中使用
设置密钥和初始化向量接口替代了“starts”接口。对于AES算法来说，
密钥长度为128、192、256比特，初始化向量长度为16字节。

    cipher更新接口为mbedtls_cipher_update，该接口需要输入cipher
结构体、消息以及消息长度，输出密文和密文长度。内部处理时会按
照分组长度进行更新计算，如果消息长度不是密文分组的整数倍，剩
余部分将保存在内部结构体中。mbedtls_cipher_update接口原型如
下：

  int mbedtls_cipher_update( mbedtls_cipher_context_t *ctx,
        const unsigned char *input, size_t ilen,
        unsigned char *output, size_t *olen );

    cipher完成接口为mbedtls_cipher_finish，该接口需要输入cipher结
构体，输出密文和密文长度，该接口对cipher更新过程中的剩余消息
进行处理。mbedtls_cipher_finish接口原型如下：

  int mbedtls_cipher_finish( mbedtls_cipher_context_t *ctx,
        unsigned char *output, size_t *olen );

    总之，mbedtls_cipher_update可调用多次，而
mbedtls_cipher_finish仅需调用一次。







    229

## Page 230

5.9.4 编译与运行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



    本节示例中开启了cipher通用接口以及AES算法，为了减少RAM
    开销，配置文件中还开启了MBEDTLS    _TABLES宏定
    _AES_ROM
    义。从编译结果可以看出，本示例共消耗了约5KB RAM空间，约
    28KB FLASH空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 05_aes
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region         Used Size Region Size %age Used
                 FLASH:    28148 B     2 MB         1.34%
                   CCM:       0 GB    64 KB         0.00%
                  SRAM:     5440 B   256 KB         2.08%
          IDT_LIST:          200 B     2 KB         9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    cipher info setup, name: AES-128-CBC, block size: 16
    cipher aes encrypt:
          4D DF 90 12 D7 B3 89 87 45 A1 ED 98 60 EB 0F A2
          FD 2B BD 80 D2 71 90 D7 2A 2F 24 0C 8F 37 2A 27
          63 74 62 96 DD C2 BF CE 7C 25 2B 6C D7 DD 4B A8
          57 7E 09 6D BD 80 24 C8 B4 C5 A1 16 0C A2 D3 F9
    cipher info setup, name: AES-128-CTR, block size: 16

              230

## Page 231

cipher aes encrypt:
C4 1A 1D B1 56 C0 9B 59 E8 25 D9 5B 72 FD 97 BE
F7 06 BA C1 B8 4F F5 4E 72 88 2D 17 0B DB 53 0A
9B 0A FD 86 41 65 73 06 6B C1 F0 52 18 FC 1D 57
9D F4 81 F7 08 CB


通过运行结果可以看出：

·AES_CBC模式和AES_CTR模式的分组长度都是16字节，两者并
没有区别。

·AES_CBC模式把54字节明文加密为64字节明文，而AES_CTR模
式的加密结果仍为54字节，明文长度和密文长度相同。










231

## Page 232

5.10 本章小结

本章主要介绍高级对称加密算法AES。在介绍AES算法之前，我
们介绍了多种分组密码模式。在实际应用中建议使用CBC模式和CTR
模式。在CBC模式中，通信双方除了具有相同的共享密钥之外，还需
要具有相同的初始化向量IV。分组密码只能处理消息长度为分组长度
整数倍的情况，若无法满足这种限制条件，则需要采用某种填充方
式。PKCS7是一种常用的填充方式，在这种填充方式中，如果消息长
度为分组长度的整数倍，那么填充之后将会增加一个额外的分组长
度。而CTR模式没有填充过程，明文长度和密文长度相同。mbedtls
中可通过原生mbedtls_aes接口或mbedlts_cipher接口实现消息的加密
或解密操作，在实际应用中推荐使用mbedlts_cipher接口。










232

## Page 233

    第6章   消息认证码

6.1 本章主要内容

         本章将详细介绍消息认证码的原理、应用和实现方法。消息认证
码可帮助接收者判断消息是否被第三方篡改。消息认证码的使用方法
容易与数字证书、单向散列函数产生混淆。单向散列函数是实现消息
认证码的常见方法，该类方法统称为HMAC，常见的消息认证码算法
有HMAC-SHA1和HMAC-SHA256等。另外，使用分组加密算法也可
构造消息认证码算法，例如CMAC、GCM和CCM。本章示例部分将
使用mbedtls HMAC和GCM接口计算消息认证码，通过这些示例可以
帮助读者快速熟悉HMAC和GCM的使用方法。










233

## Page 234

6.2 消息认证码原理

  消息认证码（Message Authentication Code）可用来检查消息的完
整性和真实性。消息认证码算法的输入为任意长度的消息和发送者与
接收者之间的共享密钥，消息认证码的输出为固定长度的数据，该输
出数据常被简称为MAC值、Tag或T。

  首先通过一个示例介绍消息认证码的使用场景。假想场景中
Alice需要传输某文件至Bob，Bob收到后需要判断该文件在传输过程
中是否被篡改或者发生了传输错误，除此之外Bob还需判断消息是否
真的来源于Alice。Alice和Bob传输与判断文件可靠性的过程如图6-1
所示。

  1）在传输开始之前，Alice和Bob已经具备相同的共享密钥；

  2）Alice使用密钥对文件进行计算并得到消息认证码；

  3）Alice将消息认证码和文件一起发送至Bob；

  4）Bob使用共享密钥对接收文件计算得到消息认证码；

  5）Bob对比接收到的消息认证码和生成的消息认证码是否一
致，若一致则表示文件未被篡改且来自于Alice。






    234

## Page 235

        图6-1 消息认证码应用场景

  消息认证码的使用方法容易与单向散列函数产生混淆，消息认证
码和单向散列函数都可以输出固定长度的数据，均可用于验证数据的
完整性。但单向散列函数只有一个输入参数，也就是消息本身；而消
息认证码却有两个输入参数，一个是消息本身，另一个是发送与接收
方之间的共享密钥。相较于单向散列函数，消息认证码不但可以确认
消息的完整性，还可以确认消息发送者是否持有相同的共享密钥。单
向散列函数与消息认证码的区别如图6-2所示。







    235

## Page 236

图6-2 单向散列函数与消息认证码的区别










236

## Page 237

6.3 消息认证码实现方法

  消息认证码可以由其他密码技术构造，例如单向散列函数和分组
加密算法等。下面介绍几种消息认证码的实现方法：单向散列函数实
现、分组密码实现和认证加密算法。










237

## Page 238

6.3.1 单向散列算法实现

  使用单向散列函数可实现消息认证码算法，这类方法常统称为
HMAC，与SHA1算法结合成为HMAC-SHA1，与SHA256算法结合成
为HMAC-SHA256，与MD5算法结合成为HMAC-MD5等。单向散列
函数可检查消息的完整性，但无法验证消息来源的可靠性，所以单向
散列算法不能直接应用于消息认证码算法。在HMAC算法中，共享密
钥并没有长度限制，输入消息也没有长度限制，但HMAC算法的输出
结果的长度是固定的。










    238

## Page 239

6.3.2 分组密码实现

  分组密码中的CBC模式也可实现消息认证码算法，典型实现方法
为CBC-MAC。分组密码的密钥可作为消息认证码中的共享密钥，对
消息进行加密处理后将最后一个分组加密的结果作为消息认证码。由
于CBC模式的最后一个分组加密结果由整个消息和密钥的决定，所以
这种方法也可保证消息的完整性和真实性。但实际应用中该算法存在
某些安全隐患。

  CMAC也是基于分组密码的消息认证码算法，CMAC算法通过共
享密钥派生出两个中间密钥K1和K2，其算法的安全性要高于CBC-
MAC算法。










    239

## Page 240

    6.3.3 认证加密算法实现


  认证加密算法是在通信过程中提供数据机密性和完整性的密码算
法，可以看作对称加密算法和消息认证码的结合。认证加密算法的典
型实现包括GCM算法和CCM算法，相比单向散列算法和分组密码实
现的消息认证算法，认证加密算法的应用更广泛。










    240

## Page 241

6.4 HMAC算法

  在消息认证码算法中，HMAC算法最为典型，本节将对HMAC算
法进行详细介绍，部分内容参考自NIST FIPS 198-1[1]。HMAC算法基
于单向散列函数实现，其构造过程可以由任意一种单向散列函数实
现，安全强度取决于单向散列函数的安全性。

  HMAC算法计算过程大致可分为密钥计算、密钥与ipad异或、与
消息组合、计算第1次散列值、密钥与opad异或、与散列值组合、计
算第2次散列值等步骤，详细过程如图6-3所示。










    图6-3 HMAC计算过程

        241

## Page 242

  在HMAC算法中，首先对密钥（K0）进行计算（步骤1-3），密
钥计算分为3种情况：

  1）如果密钥长度等于单向散列算法（H）的分组长度，则不对
密钥做任何处理；

  2）如果密钥长度小于分组长度，则需要在末尾填充0，直到其长
度达到单向散列函数的分组长度为止；

  3）如果密钥长度大于分组长度，则需要使用单向散列算法计算
密钥的消息摘要，将其作为HMAC算法的密钥。

  计算后的密钥分别与内部填充（ipad）和外部填充（opad）进行
异或操作（步骤4和步骤7），为后续的内部哈希计算和外部哈希计算
做准备。内部填充ipad和外部填充opad如下所示：

ipad = 0011 0110, 0011 0110, …, 0011 0110
opad = 0101 1100, 0101 1100, …, 0101 1100

                                     密钥与内部填充进行异或操作，将其结果与消息进行组合（步骤
5），将步骤5的输出作为内部单向散列计算的输入，计算获得消息摘
要（步骤6）。密钥与外部填充进行异或操作，将其结果与步骤6的输
出进行组合（步骤8），将步骤8的输出作为外部单向散列计算的输入
（步骤9），计算得到的结果为消息认证码。上述过程的伪代码如
下：

MAC(text) = HMAC(K, text) = H((K0 ⊕ opad )||H((K0 ⊕ ipad)||text))

    242

## Page 243

    从上述计算过程可以看出，HMAC需要计算两次单向散列函数。
消息本身在内部单向散列计算中仅执行计算一次，外部单向散列计算
的输入仅为两部分，其中一部分为密钥与外部填充opad进行异或操作
后结果，另一部分为内部单向散列计算得到的消息摘要，因此HMAC
的计算开销较低。

[1] NIST FIPS 198-1：

http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.198-1.pdf










    243

## Page 244

6.5 CBC-MAC和CMAC

   本节将介绍两种基于分组密码模式的消息认证码实现算法：
CBC-MAC和CMAC。CBC-MAC是数据认证算法（Data
Authentication Algorithm）的扩展实现。数字认证算法简称DDA算
法，它在FIPS PUB 113标准规范中定义。由于DDA算法存在安全隐
患，目前已被废弃。










    244

## Page 245

6.5.1 CBC-MAC

  CBC-MAC可以使用经过安全验证的分组密码算法，如AES算
法。但CBC-MAC在使用时需要满足一些限制条件，它仅能处理固定
长度的消息。CBC-MAC计算过程如图6-4所示。










    图6-4 CBC-MAC计算过程

       通过图6-4可以发现，CBC-MAC算法的期望结果不是所有的密文
    分组而是最后一个密文分组。CBC-MAC算法中使用全零分组作为初
    始化向量，如果消息的长度不是分组长度的整数倍，则需要在最后一
    个分组填充0直到其长度达到分组长度。对于非固定长度的消息，该
    算法存在一定的安全隐患，假设给定一个消息分组M，可以通过
    CBC-MAC计算得到消息认证码T，由于算法的特性攻击者可以很容
    易计算出两个消息分组M'=M||(M^T)的消息认证码，其结果还是T。
    虽然在合理的安全准则下CBC-MAC是安全的，但这种限制条件在实
    际应用中会带来一些影响。为了解决该问题，人们在CBC-MAC的基

        245

## Page 246

础上设计了CMAC算法，CMAC算法通过两个子密钥参与运算，从而
解决了上述问题。










246

## Page 247

6.5.2 CMAC

CMAC与CBC-MAC相比具有更高的安全性，为了解决非固定长
度消息的安全性问题，CMAC会通过密钥扩展出两个子密钥，子密钥
会在最后一个消息分组加密前参与运算。NIST 800-38B中详细描述了
CMAC规范。CMAC的计算过程主要分为3部分，分别为子密钥生
成、生成消息认证码和验证消息认证码。

1.子密钥生成

两个子密钥K1和K2的长度为对应算法的分组长度，例如AES算法
分组长度为16字节。子密钥的生成过程如下：

1）将一个全0分组进行加密，得到密文L。

2）将L左移一位并判断L的最左边一位是否为0，如果不为0则需
要与不可约多项式Rb进行异或运算。

3）将K1左移一位并判断K1的最左边一位是否为0，如果不为0则
需要与不可约多项式Rb进行异或运算。

其中Rb为不可约多项式，其中下标b为分组长度，当分组长度为
64时，其不可约多项式R64可以表示为：x64+x4+x3+x+1，当分组长度
为128时，R128可以表示为：x128+x7+x2+1，有限域的计算在GF(2b)内
完成。

    247

## Page 248

2.生成消息认证码

  当消息长度为分组长度b的N倍时，N为正整数，消息被格式化为
M1~MN。对于AES算法而言，分组长度b为16字节，密钥长度为128
位、192位或256位。子密钥K1会参与最后一组明文数据的运算。当消
息长度为分组长度整数倍时，CMAC计算过程如图6-5所示。










   图6-5 CMAC计算过程（消息长度为分组长度整数倍）

  当消长度不是分组长度的整数倍时，需要在最后一个分组的低位
填充一个比特1和若干比特0，直到最后一个明文分组的长度达到分组
长度，子密钥K2将参与最后一个明文分组的运算。当消息长度不是分
组长度整数倍时，CMAC计算过程如图6-6所示。







    248

## Page 249

图6-6 CMAC计算过程消息长度不是分组长度整数倍










249

## Page 250

6.6 认证加密CCM

  CCM模式由NIST作为标准提出，NIST SP800-38C包括CCM规范
的详细描述，CCM算法计算过程需要使用CBC-MAC算法和CTR模
式，加密和认证时CCM的输入包括明文P、一次性整数
N（Nonce）、相关数据A以及密钥K，输出密文C和认证码T。解密和
验证时CCM的输入包括密文C、认证码T、一次性整数N、相关数据A
以及密钥K，输出明文P，并返回认证是否成功。CCM模式中各参数
的长度信息如表6-1所示。

        表6-1 CCM模式中各参数长度说明










    250

## Page 251

    6.6.1 输入数据格式化

    1.控制信息和Nonce

    格式化函数用于将一次性整数N、相关数据A以及明文P格式化为
    B0~BN的消息分组，其中B0分组中包含了一次性整数N以及相关数据
    A和明文P的长度信息。B0的数据格式如表6-2所示。

        表6-2     B0数据格式


  其中q表示明文P的长度信息所占的字节数，假设N的长度为8，
则q=16-1-8=7，这样B0分组的1~8字节为N，9~15字节为明文P的长度
Q。

  B0中Flags信息的第7比特保留，第6比特用于指示是否包含相关
数据，第3~5比特用于表示消息认证码的长度，第0~2比特用于表示明
文的长度信息所占的字节数。B0中Flags数据格式如表6-3所示。

        表6-3 B0中Flags数据格式



    假设16字节的B0如下：

    01101110 00010011 11010100 10100011 01011101 01110001 10100101 00000000

        251

## Page 252

00000000 00000000 00000000 00000000 00000000 00000000 01000100 00000001

B0中包含的信息如下：

·包含相关数据，第6位为0b1；

·消息认证码的长度为12，(t-2)/2=0b101；

·明文长度信息所占的字节数为7，q-1=0b110；

·由于q=7，所以一次性整数N的长度为8字节，内容为：

0001001111010100101000110101110101110001101001010000000000000000

·由于q=7，所以明文的长度Q为17409。

000000000000000000000000000000000000000000100010000000001

B0编码过程示例如图6-7所示。









图6-7 B0编码过程示例

2.相关数据


252

## Page 253

  有相关数据A时需要对相关数据进行格式化，格式化过程与相关
数据的长度a有关：

  ·当0<a<216-28，将2字节的长度信息填充到相关数据的头部；

  ·当216-28≤a<232，将0xff、0xfe和4字节长度信息填充到相关数据
头部；

  ·当232≤a<264，将0xff、0xff和8字节长度信息填充到相关数据头
部。

  例如，相关数据长度为216，则填充的数据如下：

 11111111 11111110 00000000 00000001 00000000 00000000

  填充后，如果相关数据的长度不是分组长度的整数倍，则需要在
最后一个分组数据末尾填充0，直到其长度达到分组长度。

3.明文

  由于认证过程中使用的算法为CBC-MAC，所以同样需要对明文
进行填充，如果明文数据的长度不是分组长度的整数倍，则需要在最
后一个分组数据的末尾填充0，直到其长度达到分组长度。

4.计数值

  CTR模式需要对计数值进行加密，每个计数值的长度为分组长度


    253

## Page 254

16字节。Ctri数据格式如表6-4所示。

表6-4 Ctri数据格式



可以发现，Ctri的结构与前面描述的控制信息结构类似，其中i为
每个分组数据的索引，Ctri中的Flags信息的第6、7比特保留，第3~5
比特为0，第0~2比特用于表示明文的长度信息所占的字节数。Ctri中
Flags数据格式如表6-5所示。

表6-5 Ctri中Flags数据格式










254

## Page 255

6.6.2 认证和加密

  CCM认证过程是对格式化后的数据进行CBC-MAC运算，输出得
到长度为t的消息认证码Tag，然后使用Ctr0作为计数值对Tag进行
AES-CTR加密，输出作为最终的消息认证码T。对明文的加密过程同
样使用计数器模式，不同的是计数值从Ctr1开始，该过程无需对明文
进行填充。完成上述操作后，将密文和消息认证码作为最终的输出结
果。CCM模式加密和认证过程如图6-8所示。

  从算法结构来看，CCM算法相对复杂，需要对明文进行两次加
密处理，第1次使用CBC-MAC计算消息认证码，第2次使用CTR模式
加密明文。但由于加密和认证过程可以同时进行，并且加密过程中所
使用的CTR模式也可并行计算，这些特点使该算法在有相应的硬件支
持时性能提高显著。










    255

## Page 256

图6-8 CCM模式加密和认证过程










256

## Page 257

6.7 认证加密GCM

  GCM模式由NIST作为标准提出，NIST SP800-38D中包含GCM规
范的详细描述，GCM算法的计算过程中需要使用GHASH算法和
GCTR算法。GCM与CCM类似，加密和认证时，GCM的输入包括明
文P、初始化向量(IV)、相关数据A以及密钥K，输出密文C和认证码
T。解密和验证时CCM的输入包括密文C、认证码T、初始化向量
(IV)、相关数据A以及密钥K，输出明文P，并返回认证是否成功。
GCM模式中各参数的长度说明如表6-6所示。

  对比表6-1和表6-6可以发现，GCM的消息认证码长度只能为16字
节，而CCM模式的消息认证码长度最小为4字节，最大为16字节。

        表6-6 GCM模式中各参数长度说明










    257

## Page 258

6.7.1 GHASH

     GHASH的结构和CBC-MAC结构类似，不同的是将分组加密算法
替换为扩展域GF(2128)上的乘法运算，表示为·H。GHASH的计算过程
如图6-9所示。










    图6-9 GHASH计算过程

GHASHH(X)

需要项：H，哈希计算的子密钥

输入项：位串X，长度为128字节的m倍，m为正整数

输出项：GHASH计算结果，长度为16字节

计算过程：

·输入位串为X1 ||X2||...||Xm；


258

## Page 259

·令Y0为128比特的0，表示为0128；

·For i=1,…,m,Yi=(Yi-1⊕Xi)·H；

·返回Ym。










259

## Page 260

 6.7.2 GCTR

 GCTR是计数值每次增加1的CTR模式，其中ICB为初始计数块，
 长度为分组长度，其最右侧32比特作为计数值，逐次累加。输入位串
 X，输出长度与X相同的密文Y，GCTR计算过程如图6-10所示。

 GCTRK(ICB,X)

 需要项：分组密码算法，分组长度为128字节

 输入项：初始计数块ICB，位串X

 输出项：位串Y，长度和位串X相同

 计算过程：

 ·判断位串X是否为空，如果为空则返回空位串Y；

 ·计算n，位串X的长度为len(X)，n为大于等于len(X)/128的最小正
 整数；

·输入位串X=X1||X2||Xm-1||Xm，其中X1~Xm-1为128比特；

 ·令CB1=ICB；

 ·For i=2 to n，计算CBi=inc32(CBi-1)，inc32(S)表示对S的最右侧32
 比特加1，并对232取模运算；

     260

## Page 261

·For i=1 to n-1，计算Yi=Xi⊕CIPHK(CBi)；

·计算Ym=Xm⊕

·令Y=Y1||Y2||…||Ym；

·返回Y。










图6-10 GCTR计算过程










261

## Page 262

6.7.3 认证和加密

   GCM首先需要使用GCTR算法对明文进行加密，得到密文C。加
密使用的初始计数块IBC由IV编码得到，表示为J0，加密后得到密文
C。认证过程的输入为相关数据A和密文C，如果相关数据或密文的最
后一个分组的长度不是分组长度，则需要使用0进行填充，直到其长
度达到分组长度。图6-11填充数据分别表示为0v和0u，最后再加上64
比特的相关数据长度和64比特的密文长度作为GHASH算法的输入。

  GHASH算法的哈希子密钥H为加密密钥K对全0分组（0128）的加
密结果。将GHASH的计算结果使用GCTR算法进行加密，根据实际
需要的消息认证码长度（t）输出得到消息认证码T。GCM加密与认
证过程如图6-11所示。

  GCM算法和CCM算法均基于CTR模式实现，由于CTR模式无需
对消息进行填充，并且可以并行计算，使得基于CTR的认证加密方案
成为当前最为高效的工作模式。因为GCM和CCM模式的高效性和安
全性，它们在很多安全协议以及应用协议中得到广泛应用，例如
TLS1.3版本中，只保留了基于GCM/CCM模式的认证加密算法。









262

## Page 263

图6-11 GCM模式加密与认证过程










263

## Page 264

6.8 mbedtls HMAC示例

   本节基础示例用于展示mbedtls md通用接口计算消息认证码的方
法。示例参考自mbedtls示例代码，在mbedtls示例代码的基础上增加
或修改了部分内容。本章示例均基于Zephyr系统构建，借助Zephyr系
统良好的适配性，本章示例不但可运行于Linux平台，也可运行于
STM32F429等硬件平台。为了实现示例代码，需在mbedtls_config.h配
置文件中增加相关宏定义，宏定义描述如表6-7所示。

       表6-7 mbedtls_config.h配置文件宏定义描述





   注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书代码仓库。本章示例位于06_mac/hmac文件夹中。另外
mbedtls_config.h中所启用的配置仅限于本章示例，其他应用请根据实
际情况修改。










    264

## Page 265

6.8.1 示例代码

  代码清单6-1中将使用md通用接口，以消息“what do ya want for
nothing?”作为测试样本，使用HMAC算法计算并打印消息认证码，单
向散列算法使用SHA256，分组长度为64字节，消息认证码为32字
节。

  代码清单6-1 HMAC示例代码



#include <zephyr.h>
#include <stdio.h>
#include <string.h>
#include "mbedtls/md.h"
#include "mbedtls/platform.h"
static void dump_buf(char *info, uint8_t *buf, uint32_t len)
{
 mbedtls_printf("%s", info);
 for (int i = 0; i < len; i++) {
   mbedtls_printf("%s%02X%s", i % 16 == 0 ? "\n\t":" ",
                buf[i], i == len - 1 ? "\n":"");
 }
 mbedtls_printf("\n");
}
int main(void)
{
 uint8_t mac[32];
 char *sec"Jefe";
 char *msg = "what do ya want for nothing?";
 mbedtls_md_context_t ctx;
 const mbedtls_md_info_t *info;
 mbedtls_platform_set_printf(printf);
 mbedtls_md_init(&ctx);
 info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
 mbedtls_md_setup(&ctx, info, 1);
 mbedtls_printf("\n md info setup, name: %s, digest size: %d\n",
     mbedtls_md_get_name(info), mbedtls_md_get_size(info));
 mbedtls_md_hmac_starts(&ctx, secret, strlen(secret));
 mbedtls_md_hmac_update(&ctx, msg, strlen(msg));
 mbedtls_md_hmac_finish(&ctx, mac);
 dump_buf("\n md hmac-sha-256 mac:", mac, sizeof(mac));
 mbedtls_md_free(&ctx);
 return 0;
}



  示例中相关接口描述如表6-8所示。

 265

## Page 266

表6-8 HMAC示例接口描述










266

## Page 267

6.8.2 代码说明

HMAC示例简图如图6-12所示。










图6-12 HMAC示例简图

1.准备测试样本

测试样本来自rfc4231[1]，测试样本内容如表6-9所示。

    表6-9 HMAC测试样本内容








267

## Page 268

2.选择算法并分配内部结构

    示例代码中使用HMAC-SHA256作为消息认证算法，通过算法类
型可以得到md信息结构体指针，md信息结构体名称为
mbedtls_md_info_t，位于{mbedtls代码仓
库}include/mbedtls/md_internal.h文件中，该结构体是对单向散列算法
的抽象，结构体中包含了单向散列算法中必需的参数及接口。


    struct mbedtls_md_info_t
    {
      mbedtls_md_type_t type;
      const char * name;
      int size;
      int block_size;
      int (*starts_func)( void *ctx );
      int (*update_func)( void *ctx, const unsigned char *input, size_t ilen );
      int (*finish_func)( void *ctx, unsigned char *output );
      int (*digest_func)( const unsigned char *input,
          size_t ilen, unsigned char *output );
      void * (*ctx_alloc_func)( void );
      void (*ctx_free_func)( void *ctx );
      void (*clone_func)( void *dst, const void *src );
      int (*process_func)( void *ctx, const unsigned char *input );
    };


    得到md信息结构体指针后，通过mbedtls_md_setup接口完成内部
赋值操作，设置完成后便可以使用md通用接口开始消息认证码的计
算。

3.计算消息认证码

    HMAC消息认证码的计算过程一般以“start_update_finish”的形式
展开。hmac启动接口为mbedtls_md_hmac_starts，该接口需要输入md
结构体、密钥及密钥长度。当密钥长度大于分组长度时，将对密钥计



      268

## Page 269

    算消息摘要；当密钥长度等于分组长度时，不做任何处理；当密钥长

    度小于分组长度时，会在末尾填充0，直到其达到分组长度。
    mbedtls_md_hmac_starts接口原型如下：

    int mbedtls_md_hmac_starts( mbedtls_md_context_t *ctx,
        const unsigned char *key, size_t keylen );


   hmac更新接口为mbedtls_md_hmac_update，该接口需要输入md
结构体、消息和消息长度。接口内部会按照分组长度进行更新计算，
如果消息长度不是分组长度对齐，则剩余部分会保存在内部结构体
中，在hmac完成接口被调用时进行处理。mbedtls_md_hmac_update接
口原型如下：


    int mbedtls_md_hmac_update( mbedtls_md_context_t *ctx,
        const unsigned char *input, size_t ilen );


   hmac完成接口为mbedtls_md_hmac_finish，该接口需要输入md结
构体，输出长度为32字节的消息认证码。mbedtls_md_hmac_finish接
口原型如下：


    int mbedtls_md_hmac_finish( mbedtls_md_context_t *ctx, unsigned char *output);

    [1] rfc4231：https://tools.ietf.org/rfc/rfc4231.txt










    269

## Page 270

6.8.3 编译与运行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     本示例中开启了md通用接口以及SHA256算法，从编译结果可以
看出，示例代码共消耗约5KB RAM空间，约18KB FLASH空间。编
译与运行过程如下：




    # 进入示例代码文件夹
    $ cd 06_mac/hmac
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region         Used Size Region Size %age Used
              FLASH:       17952 B     2 MB         0.86%
                CCM:          0 GB    64 KB         0.00%
               SRAM:        4892 B   256 KB         1.87%
           IDT_LIST:         200 B     2 KB         9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    md info setup, name: SHA256, digest size: 32
    md hmac-sha-256 mac:
          5B DC C1 46 BF 60 75 4E 6A 04 24 26 08 95 75 C7
          5A 00 3F 08 9D 27 39 83 9D EC 58 B9 64 EC 38 43




    通过运行结果可以看出，HMAC的消息认证码长度与内部单向散

          270

## Page 271

列算法的消息摘要长度相等，本节示例中单向散列函数为SHA256，
其消息摘要长度为32字节，所以HMAC-SHA256的消息认证码长度也
为32字节。










    271

## Page 272

6.9 mbedtls GCM示例

   本节基础示例用于展示如何使用mbedtls cipher通用接口完成
GCM认证加密操作。示例代码参考自mbedtls示例代码，在mbedtls示
例代码的基础上增加或修改了部分内容。本章示例均基于Zephyr系统
构建，借助Zephyr系统良好的适配性，本章示例不但可运行于Linux
平台，也可运行于STM32F429等硬件平台。为了实现示例代码，需
要在mbedtls_config.h配置文件中增加相关宏定义，宏定义描述如表6-
10所示。

       表6-10 mbedtls_config.h配置文件宏定义描述






   注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书代码仓库。本章示例位于06_mac/gcm文件夹中。另外
mbedtls_config.h中所启用的配置仅限于本章示例，其他应用请根据实
际情况修改。










    272

## Page 273

6.9.1 示例代码

      代码清单6-2将使用cipher通用接口完成数据的认证加密和认证解
密操作，认证加密接口会输出密文及消息认证码，消息认证码的长度
不超过16字节，而认证解密接口则只输出明文，认证结果需要通过返
回值进行判断。示例中相关接口描述如表6-11所示。

      代码清单6-2 GCM示例代码



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/cipher.h"
    #include "mbedtls/platform.h"
    // 省略部分测试数据
    static void dump_buf(char *info, uint8_t *buf, uint32_t len)
    {
     mbedtls_printf("%s", info);
     for (int i = 0; i < len; i++) {
     mbedtls_printf("%s%02X%s", i % 16 == 0 ? "\n\t":" ",
                       buf[i], i == len - 1 ? "\n":"");
     }
     mbedtls_printf("\n");
    }
    int main(void)
    {
     int ret;
     size_t len;
     uint8_t buf[16], tag_buf[16];
     mbedtls_cipher_context_t ctx;
     const mbedtls_cipher_info_t *info;
     mbedtls_platform_set_printf(printf);
     mbedtls_cipher_init(&ctx);
     info = mbedtls_cipher_info_from_type(MBEDTLS_CIPHER_AES_128_GCM);
     mbedtls_cipher_setup(&ctx, info);
     mbedtls_printf("\n cipher info setup, name: %s, block size: %d\n",
                       mbedtls_cipher_get_name(&ctx),
                       mbedtls_cipher_get_block_size(&ctx));
     mbedtls_cipher_setkey(&ctx, key, sizeof(key)*8, MBEDTLS_ENCRYPT);
     mbedtls_cipher_auth_encrypt(&ctx, iv, sizeof(iv), add, sizeof(add),
                           pt, sizeof(pt), buf, &len, tag_buf, 16);
     dump_buf("\n cipher gcm auth encrypt:", buf, 16);
     dump_buf("\n cipher gcm auth tag:", tag_buf, 16);
     mbedtls_cipher_setkey(&ctx, key, sizeof(key)*8, MBEDTLS_DECRYPT);
     mbedtls_cipher_auth_decrypt(&ctx, iv, sizeof(iv), add, sizeof(add),
                           ct, sizeof(ct), buf, &len, tag, 16);
     dump_buf(" cipher gcm auth decrypt:", buf, 16);
     mbedtls_cipher_free(&ctx);
     return(0);


                       273

## Page 274

}

 表6-11 GCM示例接口描述










274

## Page 275

6.9.2 代码说明

GCM示例简图如图6-13所示。










  图6-13   GCM示例简图

1.准备示例测试样本

  示例测试样本来自NIST gcmtestvectors[1]，样本内容如表6-12所
示。

  表6-12   GCM示例测试样本





275

## Page 276

2.选择算法并分配内部结构

   示例代码中选择AES_128_GCM作为认证加密算法，和md通用接
口的过程类似，通过算法类型可以得到cipher信息结构体指针，cipher
信息结构体名称为mbedtls_cipher_info_t，该结构体详细描述位于
include/mbedtls/cipher.h文件中。得到cipher信息结构体指针后，再通
过mbedtls_cipher_setup接口完成内部赋值操作，接着使用cipher通用
接口开始认证加密和解密操作。

3.认证加密

   认证加密前首先需要完成密钥的设置，密钥设置接口为
mbedtls_cipher_setkey，该接口需要输入cipher结构体、密钥以及密钥
用途。认证加密时密钥用途为MBEDTLS_ENCRYPT。

   完成密钥设置后可以开始认证加密操作，认证加密接口为

        276

## Page 277

mbedtls_cipher_auth_encrypt，该接口需要输入cipher结构体、初始化
向量、相关数据、认证数据、消息和消息认证码，输出得到密文和消
息认证码。mbedtls_cipher_auth_encrypt接口原型如下：


    int mbedtls_cipher_auth_encrypt( mbedtls_cipher_context_t *ctx,
    const unsigned char *iv, size_t iv_len,
    const unsigned char *ad, size_t ad_len,
    const unsigned char *input, size_t ilen,
    unsigned char *output, size_t *olen,
    unsigned char *tag, size_t tag_len );


4.认证解密

     认证解密前同样需要完成密钥的设置，和认证加密不同的是，认
证解密时密钥用途为MBEDTLS_DECRYPT。

     完成密钥设置后可以开始认证解密操作，认证解密接口为
mbedtls_cipher_auth_decrypt，该接口需要输入cipher结构体、初始化
向量、认证数据、相关数据、消息和消息认证码，输出得到密文和消
息认证码。mbedtls_cipher_auth_decrypt接口原型如下：


    int mbedtls_cipher_auth_decrypt( mbedtls_cipher_context_t *ctx,
           const unsigned char *iv, size_t iv_len,
           const unsigned char *ad, size_t ad_len,
           const unsigned char *input, size_t ilen,
           unsigned char *output, size_t *olen,
           const unsigned char *tag, size_t tag_len );

    [1]    NIST        gcmtestvectors：

    http://csrc.nist.gov/groups/STM/cavp/documents/mac/gcmtestvectors.zip






           277

## Page 278

6.9.3 编译与运行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



    本示例中开启了cipher通用接口和AES算法，为了节省RAM消
    耗，配置文件中还开启了MBEDTLS  _TABLES宏定义，
    _AES_ROM
    从编译结果可以看出，本示例共消耗约5KB RAM空间，约30KB
    FLASH空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 06_mac/gcm
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region        Used Size Region Size %age Used
             FLASH:        29280 B     2 MB        1.40%
               CCM:           0 GB    64 KB        0.00%
              SRAM:         5496 B   256 KB        2.10%
          IDT_LIST:          200 B     2 KB        9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    cipher info setup, name: AES-128-GCM, block size: 16
    cipher gcm auth encrypt:
         93 FE 7D 9E 9B FD 10 34 8A 56 06 E5 CA FA 73 54
    cipher gcm auth tag:
    00 32 A1 DC 85 F1 C9 78 69 25 A2 E7 1D 82 72 DD
    cipher gcm auth decrypt:
         C3 B3 C4 1F 11 3A 31 B7 3D 9A 5C D4 32 10 30 69

        278

## Page 279

   从输出示例输出结果可以看出，运行结果与样本数据完全相同。
与CBC模式不同，GCM模式不仅输出密文还可以输出消息认证码。
CCM模式与GCM模式的使用方法非常相似，只需将设置模式改为
MBEDTLS_CIPHER_AES_128_CCM即可。CCM模式的具体使用方法
将在第16章展开介绍。










    279

## Page 280

6.10 本章小结

        消息认证码可保证消息的完整性和消息来源的可靠性。消息认证
码的使用场景容易与单向散列算法产生混淆，消息认证码包含两个输
入参数——共享密钥和消息，而单向散列函数仅包含一个输入参数
——消息。本章介绍了多种消息认证码算法的实现方法——单向散列
算法、分组密码和认证加密算法。单向散列算法是实现消息认证码常
用手段，这类方法常被称为HMAC算法，HMAC算法可以与SHA1或
SHA256结合。HMAC算法对共享密钥没有长度要求，对输入消息也
没有长度要求，而算法的输出结果长度固定，该长度由单向散列算法
决定。本章还介绍了CCM模式和GCM模式，与HMAC算法不同，
CCM模式和GCM模式不但可计算消息认证码，还包括加密和解密过
程。CCM模式与GCM模式均不包含明文填充过程。CCM模式的消息
认证码长度可以为4、6、8、10、12、14和16字节，而GCM模式的消
息认证码长度不应超过16字节。










280

## Page 281

        第7章 伪随机数生成器

7.1 本章主要内容

  随机数和伪随机数生成器是物联网安全应用中最为重要的部分。
本章将介绍随机数的基本概念和常见用途，例如随机数在密码技术中
可用于生成密钥等敏感数据。除了基本概念之外，本章还将介绍真随
机数生成器和伪随机数生成器，真随机数生成器一般来自于物理设
备，伪随机数生成器可分为“种子”（又称熵源）和内部结构两部分。
虽然真随机数生成器的随机性更好，但是其生成速度较慢，不利于实
际使用。所以在实际应用中，往往使用真随机数作为“种子”，再通过
伪随机数生成指定长度的随机序列。到目前为止，存在多种伪随机数
生成算法，本章将重点介绍CTR_DRBG方法，该方法使用分组密码
模式产生随机数序列。

  本章mbedtls随机数应用工具部分介绍3种应用工具，分别为
gen_entropy、gen_random_ctr_drbg和gen_random_havege。在示例代
码部分，通过随机数生成示例和素数生成示例说明mbedtls随机数模
块的使用方法。伪随机数生成器看似简单，但它却是后续RSA、
ECDSA、TLS、DTLS和CoAPs相关章节中的重要组成部分。







    281

## Page 282

7.2 随机数概述

  随机数是一组不能被预测的数字或比特序列，不同的应用程序中
有不同的方法来产生随机数据。生活中比较经典的方法包括掷骰子、
抛硬币、扑克牌、占卜等。

  很多人认为随机数和物联网安全并没有太大关系，但实际上随机
数在物联网安全应用中扮演着极为重要的角色。随机数往往用于生成
密钥，从另一个角度来说密钥就是随机数，如果随机数可以被攻击者
预测到，那么无论密码算法的强度如何，攻击者在获知密钥的情况下
可以对系统发起各种各样的攻击。密码学应用中有很多算法都需要使
用随机数，主要包括：

  ·生成盐，用于基于口令的密码。

  ·生成密钥，用于对称加密和消息认证码。

  ·生成一次性整数Nonce，用于防止重放攻击。

  ·生成初始化向量，用于分组加密的CBC模式。










    282

## Page 283

7.3 随机数生成器

   产生随机数的方式有很多种，用来生成随机数的发生器叫作随机
数生成器，随机数生成器通常分为真随机数生成器（TRNG）和伪随
机数生成器（PRNG）。由于真随机数生成器生成速度通常较慢，而
伪随机数生成器生成速度则较快，在实际应用中通常将真随机数生成
器作为熵源使用，为伪随机数生成器提供种子，这样的随机数系统在
保证安全性的同时也提供了足够的速度保障。真随机数生成器、熵池
和伪随机数生成器之间的关系如图7-1所示。




图7-1 真随机数生成器、熵池和伪随机数生成器之间的关系










283

## Page 284

7.3.1 真随机数生成器


                   真随机数生成器是从物理过程生成随机数的设备，通常基于微观
现象，例如热噪声、光电效应和其他量子现象。真随机数生成器生成
随机数的速度依赖于物理现象的采集速度，在大多数Linux发行版
中，可使用伪设备文件/dev/random获取随机数。当熵池为空时，该伪
设备文件生成随机数将发生阻塞，直到系统从环境中收集到足够的熵
时才会退出这种阻塞状态。由于这种阻塞行为，当应用程序通
过/dev/random批量读取随机数时往往需要消耗大量的时间。使
用/dev/random产生1KB随机数的操作过程如下，指令的详细说明如表
7-1所示。

# 使用/dev/random产生1KB 随机数
$ dd count=1 ibs=1024 if=/dev/random >/dev/null
# 输出如下
0+1 records in
0+1 records out
7 bytes copied, 0.000454096 s, 15.4 kB/s

    表7-1     dd指令说明








             伪设备文件/dev/random产生随机数的数量有限，当熵池中没有足
                 够的随机数并且非空时熵池中的随机数会立即返回至用户，当熵池为


284

## Page 285

空时则会发生阻塞。以上示例中试图获取1024字节随机数，
但/dev/random只返回7字节随机数，生成速度为每秒15.4KB。

    Linux系统中还有另一个伪随机数生成器/dev/urandom，不同
于/dev/random，该伪设备文件工作过程中不产生阻塞，产生随机数的
速度更快，但其输出结果的随机性不佳。使用/dev/urandom产生1KB
随机数的操作过程如下：


    # 使用/dev/urandom产生1KB 随机数
    $ dd count=1 ibs=1024 if=/dev/urandom >/dev/null
    # 输出如下
    1+0 records in
    2+0 records out
    1024 bytes (1.0 kB, 1.0 KiB) copied, 0.000605166 s, 1.7 MB/s


    通过运行情况可以看出，/dev/urandom成功生成1024字节随机
数，而且生成速度也达到每秒1.7MB。从/dev/random和/dev/urandom
的运行结果可以看出，相较于真随机数生成器，伪随机数生成器运行
速度更快。










    285

## Page 286

7.3.2 伪随机数生成器

  伪随机数生成器也称为确定性随机数生成器（DRBG），它是一
种用于产生近似随机数序列的算法。伪随机数生成器会使用一组被称
为“种子”的初始值作为输入，伪随机数生成器的内部结构被称为内部
状态，内部状态会根据种子进行初始化，并计算出随机数序列。如图
7-2所示为伪随机数生成器的结构。










        图7-2 伪随机数生成器的结构

  ·种子：种子是一串较短随机的比特序列，用于初始化伪随机数
生成器的内部状态，用户可以根据种子生成随机数序列。

  ·内部状态：指随机数生成器对内存数据的管理方法，当用户输
入种子并要求随机数生成器产生随机数时，随机数生成器会使用种子


    286

## Page 287

对内部状态进行初始化，并对内存中的数据进行计算，计算完成后输
出随机数供用户使用。为了响应下一个获取随机数的请求，还需要改
变内部状态。

  从上述过程可以看出，伪随机数生成器生成的序列并不真正随
机，它完全由一组相对较小的初始值确定，而该初始值被称为伪随机
数生成器的种子或熵源。伪随机数生成器的优势在于生成随机数的速
度更快。由于真随机数生成的过程受速度限制，在实际使用中通常采
用真随机数和伪随机数混合的方法，使用真随机数作为“种子”，通过
伪随机数生成器来生成随机数序列。而为了保证安全性，在生成一定
数量随机数后，需要使用真随机数对“种子”进行更新。










    287

## Page 288

7.4    CTR_DRBG算法

       NIST SP 800-90A[1]规范中描述了3种产生随机数的方法，分别为
Hash                       _DRBG、HMAC_DRBG和CTR_DRBG，其中Hash_DRBG使用
单向散列算法作为随机数生成器基础算法；HMAC_DRBG使用消息
认证码算法作为随机数生成器基础算法；而CTR_DRBG则使用分组
密码算法的计数器模式作为随机数生成器的基础算法。本节将重点介
绍CTR_DRBG方式实现的随机数生成器。

[1]       NIST    SP                                     800-90A：
http://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-
90Ar1.pdf










       288

## Page 289

7.4.1 参数情况

  CTR_DRBG是实现伪随机数生成器的一种典型算法，它使用分
组密码算法作为基础算法并工作在计数模式（CTR）。若使用3DES
算法，输入和输出分组长度为64比特；若使用AES算法，输入和输出
分组长度为128比特。初始计数值和算法的分组长度相等，以AES算
法为例，CTR_DRBG计算过程中参数情况如表7-2所示。

        表7-2 AES算法CTR_DRBG参数情况










    289

## Page 290

7.4.2 生成过程

CTR   _DRBG可理解为一个AES加密过程，而加密结果为期望随
机数序列。图7-3描述了CTR_DRBG生成随机数的计算过程。其整体
流程如下：

1）将密钥和初始计数值作为种子对内部状态进行初始化；

2）计数器值加1；

3）使用密钥加密计数器值；

4）将密文作为伪随机数输出；

5）根据伪随机数需求数量重复2）~4）步；

6）输出随机数序列。










290

## Page 291

图7-3 CTR    _DRBG计算过程

  如果攻击者试图预测下一个随机序列，那么他必须知晓计数器的
当前值。然而此时的随机数序列相当于密文，要破解计数器的值就相
当于破解对称加密算法，这是一项较为困难的工作。所以攻击者往往
无法预测下一个随机数序列。










291

## Page 292

    7.5 mbedtls随机数应用工具

   mbedtls为各个模块提供了应用工具，应用工具主要展示了模块
接口的使用方法。mbedtls随机数模块提供了3个示例应用程序，分别
为gen_entropy、gen_random_ctr_drbg和gen_random_havege。下面分
别介绍这些应用工具的使用方法。










    292

## Page 293

    7.5.1 gen_entropy

_entropy可以用于生成足够的熵供随机数模块使用，产生的熵
    gen
    将写入指定文件中。gen
       _entropy具体使用方法如下：



    # 生成熵并写入指定文件
    $ gen_entropy entropy.txt
    # 控制台输出
    Generating 48kb of data in file 'entropy.txt'... 100.0% done
    # 查看熵
    $ hexdump -C -n 64 entropy.txt
    00000000 37 a8 08 30 df 11 76 a1 58 39 e4 7b 1a 2d 23 51 |7..0..v.X9.{.-#Q|
    00000010 31 92 7c f8 ee 57 73 82 d6 cf e9 45 6b 5c 87 1b |1.|..Ws....Ek\..|
    00000020 3a d2 f1 fb a9 67 a7 ae b0 e5 54 7b 60 ff 5d a4 |:....g....T{`.].|
    00000030 4d e9 a6 00 fb ae 06 fd c4 fe ed 96 d8 3b c5 db |M............;..|
    00000040










    293

## Page 294

7.5.2 gen_random  _drbg
        _ctr

    gen_random_ctr_drbg使用CTR_DRBG方法生成伪随机数序列，
CTR _DRBG使用AES-256作为随机数生成器基础算法，该工具产生的
伪随机数将写入指定文件中。gen      _drbg具体使用方法如
        _random_ctr
下：




# 生成随机数并写入指定文件
$ gen_random_ctr_drbg random.ctr
# 控制台输出
Failed to open seedfile. Generating one.
Generating 768kb of data in file 'random.ctr'... 100.0% done
# 查看随机数
$ hexdump -C -n 64 random.ctr
00000000 38 46 7d 54 a5 79 d4 ec da 53 f5 2e 12 14 ad 2b |8F}T.y...S.....+|
00000010 3a a0 5b 44 88 4f 7b 1a 72 fd 95 d0 0d 11 f7 21 |:.[D.O{.r......!|
00000020 99 5d 39 e8 92 8f 79 f6 8d 8a fc 87 30 0a c9 16 |.]9...y.....0...|
00000030 cd 31 e7 cd 85 f6 c6 c2 a1 ed e0 ee 08 91 2d cc |.1............-.|
00000040










    294

## Page 295

7.5.3 gen_random_havege

gen_random_havege使用HAVEGE方法生成伪随机数序列，
HAVEGE（Hardware Volatile Entropy Gathering and Expansion）使用
硬件时钟源作为随机数生成器，该工具产生的随机数会写入指定文件
中。具体使用方法如下：




# 生成随机数并写入指定文件
$ gen_random_havege random.havege
# 控制台输出
enerating 768kb of data in file 'random.havege'... 100.0% done
# 查看随机数
$ hexdump -C -n 64 random.havege
00000000 b0 d9 bb 23 18 09 69 36 dc 02 2f f7 8d 57 26 83 |...#..i6../..W&.|
00000010 74 61 00 f6 af d1 11 97 c4 c5 67 99 3f a9 02 59 |ta........g.?..Y|
00000020 6a 73 bf 79 d9 ac ef 77 4c c0 ec 4b 11 b0 f8 2f |js.y...wL..K.../|
00000030 20 63 91 41 a9 ae ba 0a 44 45 ac 69 59 99 d0 e5 | c.A....DE.iY...|
00000040




  注意：mbedtls默认配置中并没有开启HAVEGE，若使用
gen_random_havege工具，需在{mbedtls代码仓
库}/include/mbedtls/config.h文件中增加MBEDTLS    _C设
    _HAVEGE
置。










295

## Page 296

7.6 mbedtls CTR_DRBG示例

  本节基础示例用于展示如何使用mbedtls CTR_DRBG接口生成随
机数。随机数在mbedtls应用中极为重要，很多算法应用都依赖于随
机数。本节首先将介绍随机数生成器的配置方法和随机数的获取方
法，随机数生成器的配置与获取操作将在后续章中反复出现。示例代
码参考自mbedtls示例代码，在mbedtls示例代码的基础上增加或修改
了部分内容。本节示例均基于Zephyr系统构建，借助Zephyr系统良好
的适配性，本节示例不但可运行于Linux平台，也可运行于
STM32F429等硬件平台。为了正确运行示例代码，需要在
mbedtls_config.h配置文件中增加相关宏定义，宏定义描述如表7-3所
示。

       表7-3 mbedtls_config.h配置文件宏定义描述









  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本章示例位于07_rng/gen_random文件夹
中。另外，mbedtls_config.h中所启用的配置仅限于本章示例，其他应
用请根据实际情况修改。

    296

## Page 297

    7.6.1 示例代码


   示例代码中首先需要对熵源接口进行配置，在配置熵源时需指定
熵源强度属性。mbedtls中定义了两种熵源强度属性：

   ·MBEDTLS_ENTROPY_SOURCE_WEAK表示弱熵源，系统时钟
一般被定义为弱熵源。

   ·MBEDTLS_ENTROPY_SOURCE_STRONG表示强熵源，硬件真
随机数生成器一般被定义为强熵源。

   mbedtls中熵源可以来自于单个熵源，也可以来自于多个熵源，
但至少要存在一个强熵源。完成熵源配置后再通过自定义字符串对种
子进行初始化，最后通过mbedtls随机数接口生成指定长度的随机
数。生成随机数示例相关代码如代码清单7-1所示。生成随机数示例
相关接口描述如表7-4所示。

   代码清单7-1 生成随机数示例


    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/platform.h"
    // 省略部分中间代码
    static int entropy_source(void *data, uint8_t *output, size_t len, size_t *olen)
    {
     uint32_t seed;
     seed = sys_rand32_get();
     if (len > sizeof(seed)) {
len = sizeof(seed);
     }
     memcpy(output, &seed, len);

297

## Page 298

    *olen = len;
    return 0;
}
int main(void)
{
    uint8_t random[64];
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    const uint8_t *pers = "CTR_DRBG";
    mbedtls_platform_set_printf(printf);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
        MBEDTLS_ENTROPY_MAX_GATHER,
        MBEDTLS_ENTROPY_SOURCE_STRONG);
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
        (const unsigned char *) pers, strlen(pers));
    mbedtls_printf("\n . setup rng ... ok\n");
    mbedtls_ctr_drbg_random(&ctr_drbg, random, sizeof(random));
    dump_buf("\n . generate 64 byte random data ... ok", random, sizeof(random));
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return 0;
}



    表7-4 生成随机数示例相关接口描述










    298

## Page 299

7.6.2 代码说明

生成随机数示例简图如图7-4所示。










     图7-4     生成随机数示例简图

1.熵源接口

 本示例中，mbedtls随机数模块通过自定义熵源接口获取熵源，
此处熵源接口名为entropy_source。在Zephyr操作系统中，可使用
sys_rand32_get()来获取4字节随机数。自定义熵源接口如代码清单7-2
所示。

 代码清单7-2     熵源接口

static int entropy_source(void *data, uint8_t *output, size_t len, size_t *olen)
{
 uint32_t seed;
 seed = sys_rand32_get();
 if (len > sizeof(seed)){

     299

## Page 300

len = sizeof(seed);
    }
     memcpy(output, &seed, len);
     *olen = len;
     return 0;
    }


   在Zephyr相关配置文件中已经使能
CONFIG_ENTROPY_GENERATOR选型，若Zephyr系统构建于
STM32F429平台，那么在构建过程中将会加入entropy_stm32.c。在
entropy_stm32.c中有从硬件系统中获取熵源的关键函数
entropy_stm32_rng_get_entropy()，在该关键函数中通过STM32底层硬
件接口LL_RNG_ReadRandData32()获取32位随机数。

2.添加熵源并更新种子

   通过mbedtls_entropy_add_source接口可以添加熵源并配置其属
性，该接口需要输入熵源结构体、熵源接口、熵源接口参数、熵源可
用阈值及熵源类型。当熵源中随机数数量达到阈值时熵源才可以被使
用。熵源类型分为MBEDTLS_ENTROPY_SOURCE_STRONG和
MBEDTSL_ENTROPY_SOURCE_WEAK两种，为了系统的安全性，
系统中至少需要一个MBEDTLS_ENTROPY_SOURCE_STRONG类型
的熵源。mbedtls_entropy_add_source接口原型如下：


    int mbedtls_entropy_add_source( mbedtls_entropy_context *ctx,
    mbedtls_entropy_f_source_ptr f_source, void *p_source,
    size_t threshold, int strong );


   添加熵源接口后还需通过个性化字符串更新种子，
mbedtls_ctr_drbg_seed接口需要输入随机数结构体、熵源回调接口、

        300

## Page 301

熵源结构体、个性化字符串及个性化字符串长度。本示例中个性化字
符串为CTR_DRBG，在实际应用中可使用其他任意值。
mbedtls_ctr_drbg_seed接口原型如下：


    int mbedtls_ctr_drbg_seed( mbedtls_ctr_drbg_context *ctx,
    int (*f_entropy)(void *, unsigned char *, size_t),
    void *p_entropy,
    const unsigned char *custom,
    size_t len );


3.生成随机数

   完成配置工作后可以通过mbedtls_ctr_drbg_random接口获取随机
数序列，mbedtls_ctr_drbg_random接口需输入随机数结构体、期望输
出随机数序列缓冲区和期望获取随机数序列长度。随机数长度必须小
于MBEDTLS_CTR_DRBG_MAX_REQUEST，
MBEDTLS_CTR_DRBG_MAX_REQUES默认为1024字节，本示例中
期望获取64字节随机数序列，该值远小于默认值1024。
mbedtls_ctr_drbg_random接口原型如下：


    int mbedtls_ctr_drbg_random( void *p_rng,
    unsigned char *output, size_t output_len );










    301

## Page 302

7.6.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



    示例中开启了熵源模块、CTR_DRBG模块、AES算法和SHA256
    算法，为了节省RAM空间，配置文件中还开启了
    _TABLES宏定义，从编译结果可以看出本示
    MBEDTLS_AES_ROM
    例共消耗了约8KB RAM空间和约30KB FLASH空间。编译与运行过
    程如下：




    # 进入示例代码文件夹
    $ cd 07_random/gen_random
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region    Used Size Region Size %age Used
             FLASH:        30524 B     2 MB    1.46%
               CCM:           0 GB    64 KB    0.00%
              SRAM:         8504 B   256 KB    3.24%
          IDT_LIST:          200 B     2 KB    9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    . setup rng done.
    . generate 64 byte random data done.
28 A5 7D 2B 80 C5 40 65 DE 63 38 BD 3B 3C CC 6F
10 71 EA A5 81 56 74 9D BF 22 4C A8 A5 F0 15 4E


    302

## Page 303

2F B2 BA B3 95 52 80 F3 97 B8 73 12 DF 3C B2 7C
DB FB DE FB 59 31 E8 B0 93 FD 7C 63 84 E6 E6 7C










303

## Page 304

7.7 mbedtls大素数生成示例

  mbedtls中很多功能都依赖随机数模块，例如密钥生成、素数生
成和素性检测等，在这些功能实现过程中，随机数接口通常作为参数
进行传递。本示例将借助随机数模块生成一个512比特序列。因为生
成素数长度较大，所以本示例运行的时间较长，有可能需要几分钟。
示例代码参考自mbedtls示例代码，在mbedtls示例代码的基础上增加
或修改了部分内容。本节示例均基于Zephyr系统构建，借助Zephyr系
统良好的适配性，本节示例不但可运行于Linux平台，也可运行于
STM32F429等硬件平台。为了正确运行示例代码，需要在
mbedtls_config.h配置文件中增加相关宏定义，宏定义描述如表7-5所
示。

       表7-5 mbedtls_config.h配置文件宏定义描述










  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本节示例位于07_rng/gen_prime文件夹中。

        304

## Page 305

另外，mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请
根据实际情况修改。










305

## Page 306

    7.7.1 示例代码

    示例代码中首先初始化两个大数结构体P和Q，其中P为运行结
    果，Q=(P-1)/2用于素性检测，然后调用素数生成接口生成指定长度
    的大素数，素数生成接口需指定随机数生成接口，生成大素数示例如
    代码清单7-3所示。

    代码清单7-3   生成大素数示例



#include <zephyr.h>
#include <stdio.h>
#include <string.h>
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/bignum.h"
#include "mbedtls/platform.h"
// 省略部分中间代码
int main(void)
{
    uint8_t prime[64];
    mbedtls_mpi P, Q;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    const uint8_t *pers = "CTR_DRBG";
    mbedtls_platform_set_printf(printf);
    mbedtls_mpi_init(&P);
    mbedtls_mpi_init(&Q);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
        MBEDTLS_ENTROPY_MAX_GATHER,
        MBEDTLS_ENTROPY_SOURCE_STRONG);
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
        (const unsigned char *) pers, strlen(pers));
    mbedtls_printf("\n . setup rng ... ok\n");
    mbedtls_printf("\n ! Generating large primes may take minutes!\n");
    mbedtls_mpi_gen_prime(&P, sizeof(prime)*8, 1,
        mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_mpi_sub_int(&Q, &P, 1);
    mbedtls_mpi_div_int(&Q, NULL, &Q, 2);
    mbedtls_mpi_is_prime(&Q, mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_printf("\n . Verifying that Q = (P-1)/2 is prime ... ok\n");
    mbedtls_mpi_write_binary(&P, prime, sizeof(prime));
    dump_buf("\n . generate 512 bit prime data ... ok", prime, sizeof(prime));
    mbedtls_mpi_free(&P);
    mbedtls_mpi_free(&Q);
    mbedtls_entropy_free(&entropy);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    return 0;


    306

## Page 307

}

 示例中所使用接口的具体描述如表7-6所示。

 表7-6 生成大素数相关接口描述










307

## Page 308

7.7.2 代码说明

生成大素数示例简图如图7-5所示。










    图7-5 大素数示例简图

1.随机数配置

    大素数生成过程需要使用随机数接口，首先需要完成随机数的配
置工作，该过程包括熵源接口添加、熵源属性设置及通过个性化字符
串更新种子。伪随机数生成器配置过程的详细描述可回顾7.6.2节。

    308

## Page 309

2.生成素数

    完成随机数的配置工作后，可以调用mbedtls_mpi_gen_prime接口
生成指定长度的素数，该接口需输入素数结构体、生成素数的长度、
生成素数标志、随机数生成接口和随机数结构体，素数会被保存在素
数结构体中。其中素数长度按位表示，素数标志为1时则(P-1)/2也为
素数。mbedtls_mpi_gen_prime接口原型如下：


    int mbedtls_mpi_gen_prime( mbedtls_mpi *X, size_t nbits, int dh_flag,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng );


3.验证素数

    验证素数P的素性可简化为验证(P-1)/2的素性，通过这种方式可
提高效率。mbedtls中使用Miller-Rabin算法进行素性检测，该算法是
典型的大数素性测试算法。示例中首先通过mbedtls_mpi_sub_int接口
和mbedtls_mpi_div_int接口计算Q=(P-1)/2，最后通过
mbedtls_mpi_is_prime接口完成大数Q的素性检测。

4.打印素数

    素数检测通过后，可使用mbedtls_mpi_write_binary接口将大数结
构体中的内容写入数组中，最后将数组内容打印到终端。







    309

## Page 310

7.7.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     本示例中在生成随机数示例的基础上增加了大数计算模块，
RAM及FLASH的消耗也相应增加，从编译结果可以看出，本示例共
消耗约11KB RAM空间及约39KB FLASH空间。编译与运行过程如
下：




    # 进入示例代码文件夹
    $ cd 07_random/gen_prime
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region       Used Size Region Size %age Used
             FLASH:         38728 B       2 MB    1.85%
               CCM:         0 GB         64 KB    0.00%
              SRAM:         11576 B     256 KB    4.42%
          IDT_LIST:         200 B         2 KB    9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    . setup rng ...    ok
    ! Generating large primes may take minutes!
    . Verifying that Q = (P-1)/2 is prime ...     ok
    . generate 512 bit prime data     ... ok
    DE 41 1D 39 E1 72 2B 80 3E C4 3C A7 98 1E 54 7F
    18 EC 19 D7 1D 8B 84 2B E7 62 E4 02 10 35 30 B6
    84 25 41 62 69 F0 98 E9 D7 64 36 2D 7A 59 D5 F9


                            310

## Page 311

B1 48 84 99 EB 0D 4F 55 40 86 F5 27 2D 18 4E F7










311

## Page 312

7.8 mbedtls自定义熵源接口

    以上示例均通过mbedtls_entropy_add_source()增加熵源接口。在
mbedtls中还可以通过使能MBEDTLS_ENTROPY_HARDWARE_ALT
宏定义的方式启用mbedtls_hardware_poll接口，可在
mbedtls_hardware_poll中获取来自于硬件的真随机数。在STM32F4系
列中，mbedtls_hardware_poll的实现如代码清单7-4所示。

    代码清单7-4 mbedtls_hardware_poll实现


    int mbedtls_hardware_poll(void *data, unsigned char *output,
           size_t len, size_t *olen )
    {
     uint32_t index;
     uint32_t random_value;
     for (index = 0; index < len/4; index++)
     {
      if (HAL_RNG_GenerateRandomNumber(&RngHandle, &random_value) == HAL_OK)
      {
       *olen += 4;
       memcpy(&(output[index * 4]), &random_value, 4);
      }
     }
     return 0;
    }










       312

## Page 313

7.9 本章小结

  随机数是物联网应用的重要组成部分，它可用于生成各种密钥或
初始化向量。随机数生成器分为真随机数生成器和伪随机数生成器，
由于真随机数生成器产生随机序列的速度较慢，所以一般采用真随机
数作为伪随机数生成器的“种子”。伪随机数生成器可通过单向散列、
消息认证码和分组加密算法实现。其中CTR_DRBG是一种常用的伪
随机数生成算法，它使用AES-256作为生成器的基础算法。

  mbedtls随机数模块的实际应用中必须包含一种强属性熵源，这
种熵源一般来自于硬件设备，本章示例所使用的熵源来自于
STM32F4芯片中的真随机数随机数生成器。通过
mbedtls_entropy_add_source接口可增加熵源，最终构建可用的随机数
模块。










    313

## Page 314

        第8章 RSA算法

8.1 本章主要内容

   RSA算法是一种常用的公钥密码算法，不但可用于公钥加密，也
可用于数字签名。本章将首先介绍RSA算法的基本原理。与对称加密
中共享密钥不同，RSA加密过程和解密过程使用不同的密钥。RSA密
钥分为公钥和私钥两部分，在RSA公钥加密部分，公钥通常用于加密
消息，而私钥用于解密消息。

   除了介绍基本原理之外，本章还将介绍RSA加速技术和填充方
法。RSA加速技术部分将重点介绍中国剩余数定理；RSA填充方法部
分将详细介绍PKCS1-V1.5填充方法和OAEP填充方法。RSA公钥密码
的实际应用离不开加速技术和填充方法。

   在mbedtls RSA应用工具部分介绍3个与RSA密切相关的应用工
具：rsa_genkey、rsa_encrypt和rsa_decrypt。通过这些工具可以快速熟
悉RSA公钥加密运行原理。在mbedtls基础示例部分，将介绍
mbedtls_rsa_gen_key、mbedtls_rsa_pkcs1_encrypt和
mbedtls_rsa_pkcs1_decrypt等接口。








    314

## Page 315

8.2 RSA算法原理

       RSA算法是一种常用的公钥密码算法，它是使用最为广泛的非对
称密码方案。RSA算法基于大整数质因数分解难题构建，计算两个大
素数（质数）的乘积较为容易，但反过来对乘积进行因式分解则非常
困难。RSA算法的诞生开辟了一个新的密码学分支，但是RSA算法的
本意并不是为了取代对称密码。RSA算法在计算过程中存在较多模幂
运算，计算速度比对称加密算法要慢很多，并不适用于对大量数据进
行加密或解密操作。RSA算法在实际中常用于加密或解密小数据片
段，例如密钥配送等应用。另外RSA算法也可用于构建数字签名算
法。本节将详细描述RSA算法的计算过程和加速方法，数字签名部分
将在第11章进行介绍。

下面通过Alice和Bob说明RSA算法的应用场景。假想场景中Alice
需要发送消息给Bob，此处将对称密钥作为消息，该对称密钥将用于
后续安全通信。具体流程如图8-1所示。










315

## Page 316

      图8-1 RSA算法密钥对生成、加密和解密过程

  1）Bob生成符合RSA算法标准的密钥对，密钥对包含公钥和私
钥；

  2）Bob将公钥发送至Alice，私钥则自己保存；

  3）Alice使用Bob的公钥加密明文，此处的明文为对称密钥，
Alice将密文发送至Bob；

  4）Bob使用私钥解密密文后得到明文，此时Bob得到了后续对称
加密过程所使用的对称密钥；

  5）Alice和Bob通过RSA算法完成对称密钥的配送工作。



    316

## Page 317

  注意：在TLS1.2协议握手阶段也与图8-1过程类似，客户端（相
当于Alice）产生一个48字节的预备主密钥，预备主密钥是主密钥的
组成部分之一。客户端使用服务器（相当于Bob）的RSA公钥加密48
字节预备主密钥，最后将加密结果发送至服务器。TLS1.2协议仍然允
许使用RSA算法进行密钥协商，但由于RSA算法没有前向安全性，所
以并不推荐在物联网安全应用中使用图8-1类似的密钥交换方法。另
外，在最新版的TLS1.3协议中，已经禁止用RSA作为密钥协商算法。










    317

## Page 318

8.3 RSA算法详细说明

  本节将继续沿用上一节中的假想场景介绍RSA算法的计算过程。
RSA算法的计算过程包括密钥对生成、RSA加密和RSA解密。假想场
景中Bob首先生成密钥对，密钥对包括公钥和私钥，Bob通过某种途
径把公钥发送给Alice；Alice需要发送消息至Bob，发送时使用来自
Bob的公钥对消息进行加密；Bob使用自身保留的私钥对密文进行解
密。RSA算法的整体过程如表8-1所示。

        表8-1 RSA算法整体过程










    1.RSA密钥对生成

      RSA算法的密钥对生成过程需要使用两个大素数。密钥对生成过
    程如下：

    1）选择两个大素数p和q（p≠q），大素数一般来自于随机数，先
    使用随机数生成器生成一个大整数，再判断该大整数是否为素数；



    318

## Page 319

  2）计算n=p×q，n是公钥和私钥的模数，通常以比特表示，例如
1024比特、2048比特；

  3）计算L=1005319.png(n)=(p-1)(q-1)，1005314.png(n)为欧拉函
数；

  4）选择e，e需要同时满足1＜e＜L和gcd(e,L)=1，也就是说e和L
互素，e的常见选择有3、17和65537，它们都是素数并可加快模幂运
算速度；

  5）计算d，需要通过e计算得到，d需要同时满足1＜d＜L和d·e≡1
mod L，d是e关于模L的乘法逆元，由于e和L互为素数，所以e关于模
L的乘法逆元总是存在的。

  通过上面的步骤可以得到表8-2中几个关键参数。

    表8-2     RSA算法关键参数










  注意：在RSA算法中，公钥和私钥并不是一个数，而是一个“结

  319

## Page 320

构”，RSA的公钥包括n和e两部分，RSA的私钥至少包括n和d两部
分。

2.RSA加密

  Alice获得Bob的公钥后，可使用公钥对明文进行加密操作，从而
得到密文c。最后将密文发送给Bob。加密过程表达式如下：

  c≡memod n

3.RSA解密

  Bob收到密文后，可使用私钥对密文c进行解密操作，从而得到
明文m。解密过程表达式如下：

  m≡cdmod n

  下面通过一个具体示例说明RSA算法的计算过程。首先Bob通过
密钥生成算法计算得到公钥(33,3)和私钥(33,7)。Bob将公钥发送至
Alice，私钥则自己保留不对外公开。

  1）选择两个素数，p=11，q=3；

  2）计算模数n，n=p×q=11×3=33；

  3）计算L，L=1005295.png(n)=(p-1)(q-1)=20；

  4）选择e，e=3，满足条件gcd(3,L)=1；

      320

## Page 321

5）计算d，通过d·e≡1 mod L可以得到d·3≡1 mod 20，取d=7可满
足条件1＜d＜L；

6）得到公钥(n,e)=(33,3)，得到私钥(n,d)=(33,8)。

Alice获得Bob公钥后，将消息m=7使用Bob公钥进行加密操作，
最后将密文发送至Bob。加密过程如下：

c≡me=73≡343≡13 mod 33

Bob收到密文后，使用私钥对密文执行解密操作，从而得到明文
m=7。解密过程如下。

m≡cd≡137≡62748517≡7 mod 33










321

## Page 322

8.4 RSA加速技术

    从以上示例中可以看出，RSA加解密过程中存在大量的模幂运
算，这将导致其计算效率很低。RSA公钥操作过程通常可以使用短公
开指数的方法进行快速计算，常用的e为3、17和65537（0x01001）。

        RSA私钥操作可以通过中国剩余定理（CRT）进行加速执行，该
加速过程依赖于一个重要的数论原理：对一个较大模数进行操作等价
于对该模数的质因数操作。通过中国剩余定理可以把私密指数d和模
数n转换为两个较小的数，并将其变换到CRT域内进行计算，计算完
成后再变换回原问题域。

         本节将描述RSA私钥解密操作中使用中国剩余定理进行加速的详
细过程，解密过程包括3个部分，分别为密文变换到CRT域、在CRT
域内进行指数运算和变换回问题域。










322

## Page 323

    8.4.1 中国剩余数定理

    1.将密文变换到CRT域

       假设私钥为(d,n)，明文为m，密文为c，解密过程表达式为
    m≡cdmod n。首先将密文c分解为模上公共模数n的两个因子p和q，并
    得到CRT域内的模表示。






2.在CRT域内进行指数运算

  在CRT域内计算出明文m模表示，首先将私密指数d变换到CRT
域，然后计算出CRT域内的m模。具体计算过程如下：










    3.变换回问题域



    323

## Page 324

  最后从CRT域内的m模表示(mp,mq)中得到最终的结果m。首先计
算CRT系数，然后将CRT域内的m模变换回问题域。具体计算过程如
下：









  该计算过程中第2步中的模幂运算最为耗时。与直接计算相比，
使用中国剩余定理并没有减少乘法计算次数，但是通过将n分解为p和
q，使得每次乘法操作涉及的整数长度都变为原来的1/2，所以如果不
考虑中国剩余定理本身的计算开销，可以提升4倍左右的计算效率。










    324

## Page 325

8.4.2 动手实践

下面通过一个具体示例说明中国剩余定理的计算过程。该示例只
是为了描述RSA使用中国剩余定理完成解密的过程，并没有实际加速
效果。参数情况及计算过程如下：

通过中国剩余数定理加速计算m≡cdmod n，其中，

p=3;q=11;n=33;e=3;d=7;m=7;c=13

1）将密文变化到CRT域。






2）在CRT域内进行指数运算。










3）变换到问题域。



325

## Page 326

4）计算得到明文m=7。










326

## Page 327

8.4.3 性能对比

     mbedtls提供了性能测试工具，该工具可查看指定算法性能，应
用工具的实现代码位于{mbedtls代码仓库}/programs/test/benchmark.c
文件。性能对比在Linux虚拟机环境下完成，测试虚拟机主频为
2.5GHz，内核数量为1。

     在mbedtls配置文件中，可通过MBEDTLS_RSA_NO_CRT宏定义
打开或关闭CRT加速，默认情况下mbedtls已经开启了CRT加速。通过
benchmark应用工具查看RSA算法使用或禁用CRT加速的性能差异。



       # 关闭CRT加速
    $ benchmark rsa
    RSA-2048      :  12415 public/s
    RSA-2048      :    98 private/s
    RSA-4096      :   3622 public/s
    RSA-4096      :    15 private/s
       # 启用CRT加速
    $ benchmark rsa
    RSA-2048      :  12189 public/s
    RSA-2048      :   261 private/s
    RSA-4096      :   3595 public/s
    RSA-4096      :    48 private/s



     通过对比结果可以发现，使用CRT加速后私钥解密性能有明显提
升，而CRT对公钥加密的影响并不大。以RSA-2048私钥解密操作为
例，未开启CRT加速的情况下私钥解密速度为每秒98次，开启CRT加
速后解密速度提升至每秒261次。CRT加速对mbedtls RSA加密和解密
的影响如图8-2所示。





                     327

## Page 328

图8-2 CRT加速对mbedtls RSA加密和解密的影响










328

## Page 329

8.5 RSA填充方法

  在上述示例中已经说明了RSA算法的计算过程。示例中的RSA计
算过程较为简单，若直接使用将存在一定的安全隐患。RSA加密结果
总是确定的，也就是说给定一个公钥，特定的明文总是可以得到对应
的密文。攻击者可以从密文中获得明文的一些统计信息。

  实际中RSA算法通常需要包含填充方案，通过填充动作把随机性
注入明文中，这样在公钥和明文相同的情况下，密文也不会相同，从
而避免了攻击者从密文中获得统计信息。常用的RSA填充方案有两
种：RSAES-OAEP和RSAES-PKCS1-v1_5。本节将对两种RSA填充方
案做详细说明。










    329

## Page 330

8.5.1 PKCS1-V1_5

  PKCS1-V1_5是一种早期RSA填充方案，目前已经不推荐在新应
用中使用。其填充过程各字段表示如图8-3所示。










        图8-3 PKCS1-V1_5填充字段描述

  填充字段中有3字节的固定长度，包括2字节0x00，用于指示填充
开始和结束，1字节0x02用于指示算法类型。假设消息长度为mlen，
模数n长度为K，则PS字段长度为K-3-mlen，最小长度为8字节。公钥
加密操作中需要使用随机数完成PS字段的填充，完成PS字段的填充
后将消息拼接在用于指示填充结束的0x00之后。需要注意的是，消息
长度mlen最大为K-11，需预留至少11字节用于填充。





    330

## Page 331

8.5.2 OAEP

新版本PKCS#1标准中推荐使用OAEP填充方法，该方法在实现
过程中引入单向散列函数和与消息相关联的标签。填充过程中使用的
参数或运算如表8-3所示。

    表8-3  OAEP填充过程使用的参数或运算










1）生成一个长度为K-mlen-2hlen-2的全零字节的填充字符串PS，
这里PS的长度可能为0；

2）计算LHash=Hash(L)，长度为hlen；

3）将LHash、PS、一个固定字节0x01和消息拼接在一起形成数
据块DB，其长度为K-hlen-1，该过程具体表达式为：

DB=LHash||PS||0x01||M

4）生成长度为hlen的随机字符串seed；



331

## Page 332

5）计算dbMask=MGF(seed,k-hlen-1)；

6）计算maskedDB=DB xor dbMask；

7）计算seedMask=MGF(maskedDB,hlen)；

8）计算maskedSeed=seed xor seedMask；

9）将一个固定字节0x00、maskedSeed和maskedDB连接起来，构
成填充后的消息EM，长度为K字节，其表达式为：

EM=0x00||maskedSeed||maskedDB










332

## Page 333

8.6 mbedtls RSA应用工具

  mbedtls为各个模块提供了应用工具，应用工具主要用于展示模
块接口的使用方法。mbedtls公钥算法模块提供了多个应用工具，与
RSA加解密相关的应用工具有3个，分别为rsa_genkey、rsa_encrypt和
rsa_decryp。下面通过一个具体场景介绍应用工具的使用方法，假想
场景中使用RSA算法生成密钥对，使用公钥对“Hello,world!”进行加
密，最后再通过私钥对密文进行解密。










    333

## Page 334

    8.6.1 rsa_genkey

    rsa   _genkey可以用来生成rsa密钥对，默认生成2048比特长度的密
    钥。公钥保存在rsa_pub.txt文件中，私钥保存在rsa_priv.txt文件中。具
    体过程如下：


    $ rsa_genkey
    . Seeding the random number generator... ok
    . Generating the RSA key [ 2048-bit ]... ok
    . Exporting the public key in rsa_pub.txt....  ok
    . Exporting the private key in rsa_priv.txt... ok


     rsa_gengkey将生成密钥对，其中公钥部分内容将保存到
rsa_pub.txt文件中，而私钥部分内容将保存到rsa_priv.txt文件中。

     rsa_pub.txt中包括公钥参数N和E，其中E采用短公开指数
65537(0x01001)。rsa_pub.txt的具体内容如下：


    $ cat rsa_pub.txt
    # 输出内容
    N = B949D4F8F22671828BB6C7406DA06515F05B232FA3A832F3553320BCA03A0C2DCA3FA231FD578D9EC2AE4B1630FE5129BD2BBA671B90F458A06E49F14CD27079424D960A224D3F033AF384AAFE05EC4C83F732E5FFAD756E5872D73A7601B70247A5F0F6C33D5B50BCA26C4A5F652BBAAF84ED583586521235E6FE49BD4B94109951D2AD4AAFFA42899E2BFA1DB227022C66E93EF2EF6972B38480DC01094CA14790BBE432715AF16776FE977A8BE7CCA354F16F6B314D9C6F46034EC3A7E3EA31AFA628490CD796D434FFF348B17B001EE4B95A8BE8A27EEEC507E69B967616F7544DB58C9F39596A965DE852AA2A75F4BDB641E9A7BBD21DC45A3FEC865EFD
    E = 010001


        rsa_priv.txt中不但包括公钥参数N和E，还包括私钥参数D、P、
    Q、DP、DQ和QP，其中DP、DQ和DQ用于加速解密过程。
    rsa _priv.txt的具体内容如下，

        $ cat rsa_priv.txt
        # 输出内容
        N = B949D4F8F22671828BB6C7406DA06515F05B232FA3A832F3553320BCA03A0C2DCA3FA231FD578D9EC2AE4B1630FE5129BD2BBA671B90F458A06E49F14CD27079424D960A224D3F033AF384AAFE05EC4C83F732E5FFAD756E5872D73A7601B70247A5F0F6C33D5B50BCA26C4A5F652BBAAF84ED583586521235E6FE49BD4B94109951D2AD4AAFFA42899E2BFA1DB227022C66E93EF2EF6972B38480DC01094CA14790BBE432715AF16776FE977A8BE7CCA354F16F6B314D9C6F46034EC3A7E3EA31AFA628490CD796D434FFF348B17B001EE4B95A8BE8A27EEEC507E69B967616F7544DB58C9F39596A965DE852AA2A75F4BDB641E9A7BBD21DC45A3FEC865EFD
        E = 010001
        D = 07C019887AEDE0BC4A867AB9D73169090C8F6E095AC47907C9FDE42B55086DE4A71BC24D15011F360F83FAE012C1E5E3391125DAEA419B4C4469ADEE1F532E2139AF6FCC920D69200421EB8ABB80194244C2DCFE2C93B4E0736805036256F0061DB91DE5DF2F7C8259619C90AA8230DCBE3AC6881F5FB44F24076586456F6E8CB0BFF9853711C40E05E51B5BD09DC1FCB69D0D0D6266727B14EFF9513DD09BF512F58D64B7430E3D83F7AB765242CD342B5AE5BFD42A5E49646A6D315698DB9CC5998805B17884F65F655A7D3A5F2883C4687D94C8F47588C80F4B35176A6FCEC99C1C2556452F3C63D1E1BEE936D65BC1775A0DEF6E6DE3040AC508FF640001
        P = FEF9CDE5D239330D9F4058B9591A6EE4E507BBDC01B3273AD7B0A891EC1FBD5F10F20E037BF8993668913688C026CBF661473042089BA0B6252E5B67BE6CC3315BF7873BFFC2F98CA00B555C2787F8AB84D32EC055EB3DFD270D49D226F3200F6C2D6686FED40A25EBAAF6F15F7E626CA133315C4BEFE42183DA7A43CDEC2201

            334

## Page 335

Q = BA085DF1C007AB55DAA2708D589DF366AF8CA7EDF35E2B2A376EE71E15BC51F71BBA898E98DBDA947077C3C33C8805C505E0541908FA8D2BC3C2569DF3584E83ED890716BB030A785D670003BFE1850BACD893D260F49196EC51561336EC5FA0901C678B76E590AC3CD6F5D50E06F71C050E6C7F208C43A1FA3EB1506020C4FD
DP = F48C912F90FEAD79AE39201FBD573DEF29BFCE2D4830153B39AE452F97E225562DC18B314A50F85A17D6D7103803BDF23400FC47094C82CAD0447304C0BE3E447429A7BA23275503CC68B2592DCD1AF31EF511CD055B17DC5AFD42C55DF827D2C2F594757BA9D185E74FD583520CBCC7E5A05D02620ED6A652795474FDE73201
DQ = 0D25403630029AB9D35C3D25CFC84185D50BD465FD177F6759496DED734DBE60FEC59CA8C5E66B38A805DE80724B8E54D0C87C48D49897D72ADB15B1CD9B44D90FB4EA1A5216B1EBB575ECCB5708C195049EBD3B557C92B91E73D4E840AE4D4794475D8DBE561476074A8D4E83D23C2DEFB1883B277AA1E0D5450ED486266AA5
QP = BB52BBBE9C9219656C128A7DDCECEBEE841ADB0D63A19F7545B7EC8F3A23EF8AEB72E34D8EF8065D9A8BB33D5C2796AF9001BB94CC24CF5318BBEF192A33B3776765710FD464B9DA330445DC2A0BF518FB9F7DD24F875C65E3EB53CA5AE76AFFD3DBADE74D66B660A78C000F9C0609DBD5B61224321A6881A64716C7362959EC

从rsa_gengkey的运行结果可以看出：

·RSA密钥参数d的值远大于参数e，所以在指数运算中，RSA加
密过程c≡memod n的运算量远小于RSA解密过程m≡cdmod n。

·对于物联网设备而言，RSA的密钥对结构较为复杂，密钥长度
较长，RSA密钥对需要消耗更多的存储资源和传输资源。










335

## Page 336

    8.6.2 rsa_encrypt

    rsa   _encrypt可以使用RSA公钥对输入数据进行加密操作，输入数
    据不能超过100字节，加密结果默认保存在result-enc.txt文件中。具体
    过程如下：



    $ rsa_encrypt 'Hello, World!'
    # 输出内容
    . Seeding the random number generator...
    . Reading public key from rsa_pub.txt
    . Generating the RSA encrypted value
    . Done (created "result-enc.txt")




      由于mbedtls默认配置中已经启用了PKCS1V1_5填充规则，所以
两次运行rsa_encrypt加密相同的消息时将获得不同的密文，但这种不
同并不会影响解密操作。result-enc.txt的具体内容如下：



    $ result-enc.txt
    # 输出内容
    3E 4E 64 0E E9 5D 84 6E BC B9 38 73 39 D1 EB 1F
    24 7A D5 B0 DF 9F D2 DA 2B 12 0A 15 B3 95 D5 BA
    D3 2D 8E 24 B9 54 72 97 40 AD 07 72 5D CC 7A DC
    6F CC 54 81 A7 F0 89 02 C8 06 2A 58 65 BB A5 F2
    BF 00 47 B5 97 E9 FD B6 16 88 B4 F7 60 E7 50 BD
    7B 5C A3 85 14 88 62 8F 45 A2 52 7C 07 92 5B 2F
    4E 61 76 D0 72 86 F8 92 10 00 A8 47 C7 B1 C4 6F
    D1 A3 B2 3D 65 3E CE 64 4F 31 78 DD 5D 07 1D 2E
    00 71 7B E8 0D 6B 27 42 1A 28 9A A5 89 01 0A 87
    79 BB 1E 7B 75 C6 84 0B 5E F6 90 0B 8F D5 7E F5
    8E 6B D4 6E D6 5D 01 83 43 D4 2C FE F3 D2 34 73
    A1 24 EB 31 EE 46 C0 B3 5B 92 66 62 F9 30 A6 5C
    50 14 BC 26 D9 2C 5E 83 51 E1 26 84 C4 CD FC 78
    91 93 20 68 11 1E D5 6F AB 86 3A 62 00 25 E8 4E
    B9 F5 B4 C3 90 55 71 CD 79 DE 6B 8C 0D 18 D1 9A
    FE 53 9A A3 D9 A9 6A 27 72 FE EC 5F B7 11 86 62




    从RSA加密结果可以看出，明文“Hello,World!”的长度为12，而
    密文长度为256，密文长度远大于明文长度。


    336

## Page 337

8.6.3 rsa_decrypt

     rsa_decrypt可使用RSA私钥对加密文件进行解密，解密结果将打
印至终端。该工具使用时不需要传入任何参数。具体过程如下：



    $ rsa_decrypt
    # 输出内容
    . Seeding the random number generator...
    . Reading private key from rsa_priv.txt
    . Decrypting the encrypted data
    . OK
    The decrypted result is: 'Hello, World!'










    337

## Page 338

8.7 mbedtls RSA加解密示例

  本节基础示例将介绍mbedtls RSA私钥加密与公钥解密过程，填
充方法为OAEP。示例中通过RSA私钥加密明文字符
串“Hello,World”，再通过RSA公钥解密密文，最后还原明文字符
串“Hello,World!”。由于RSA加密过程涉及填充操作，所以本节示例
中还使用了伪随机数生成器模块。示例代码参考自mbedtls示例代
码，在mbedtls示例代码的基础上增加或修改了部分内容。本节示例
均基于Zephyr系统构建，借助Zephyr系统良好的适配性，本节示例不
但可运行于Linux平台，也可运行于STM32F429等硬件平台。为了正
确运行示例代码，需要在mbedtls_config.h配置文件中增加相关宏定
义。宏定义描述如表8-4所示。

       表8-4 mbedtls_config.h配置文件宏定义描述










  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本节示例位于08_rsa文件夹中。另外，

        338

## Page 339

mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。










339

## Page 340

8.7.1 示例代码

      示例代码大致可分为密钥对生成、RSA加密和RSA解密这3个阶
段。RSA生成密钥过程中需要使用伪随机数生成器产生大整数p和q，
并对大整数p和q进行素性检测。RSA密钥对生成过程较为缓慢，有时
运算时间长达几分钟。生成密钥对时需指定密钥长度（位表示）和公
开指数，示例中选择较为常用的短公开指数65537（0x01001），生成
密钥对后通过RSA加密接口完成明文的加密操作。最后，通过RSA解
密接口对密文进行解密，然后对比解密后的结果和明文是否一致。
RSA加解密示例代码如代码清单8-1所示，示例代码中使用的RSA相
关接口如表8-5所示。

      代码清单8-1 RSA加解密示例



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/rsa.h"
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/platform.h"
    // 省略部分中间代码
    int main(void)
    {
     size_t olen = 0;
     uint8_t out[2048/8];
     mbedtls_rsa_context ctx;
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     const char *pers = "simple_rsa";
     const char *msg = "Hello, World!";
     mbedtls_platform_set_printf(printf);
     mbedtls_platform_set_snprintf(snprintf);
     mbedtls_entropy_init(&entropy);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_rsa_init(&ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
                             MBEDTLS_ENTROPY_MAX_GATHER,
                             MBEDTLS_ENTROPY_SOURCE_STRONG);


                             340

## Page 341

 mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
     (const uint8_t *) pers, strlen(pers));
 mbedtls_printf("\n . setup rng ... ok\n");
 mbedtls_printf("\n ! RSA Generating large primes may take minutes! \n");
 mbedtls_rsa_gen_key(&ctx, mbedtls_ctr_drbg_random,
                                 &ctr_drbg, 2048, 65537);
 mbedtls_printf("\n 1. RSA generate key ... ok\n");
 dump_rsa_key(&ctx);
 mbedtls_rsa_pkcs1_encrypt(&ctx, mbedtls_ctr_drbg_random,
     &ctr_drbg, MBEDTLS_RSA_PUBLIC, strlen(msg), msg, out);
 dump_buf("\n 2. RSA encryption ... ok", out, sizeof(out));
 mbedtls_rsa_pkcs1_decrypt(&ctx, mbedtls_ctr_drbg_random, &ctr_drbg,
     MBEDTLS_RSA_PRIVATE, &olen, out, out, sizeof(out));
 out[olen] = 0;
 mbedtls_printf("\n 3. RSA decryption ... ok\n     %s\n", out);
 memcmp(out, msg, olen);
 mbedtls_printf("\n 4. RSA Compare results and plaintext ... ok\n");
 mbedtls_ctr_drbg_free(&ctr_drbg);
 mbedtls_entropy_free(&entropy);
 mbedtls_rsa_free(&ctx);
 return 0;
}



 表8-5 RSA加解密示例接口描述










 341

## Page 342

8.7.2 代码说明

RSA加解密示例简图如图8-4所示。










    图8-4 RSA加解密示例简图

1.配置随机数

 由于RSA生成密钥对过程需要使用伪随机数生成器，首先需要完
成伪随机数的配置工作，该过程包括熵源接口添加、熵源属性设置及
通过个性化字符串更新种子等步骤。伪随机数生成器配置过程的详细

    342

## Page 343

    描述可回顾7.6.2节。

    2.RSA密钥初始化

    mbedtls RSA密钥结构为mbedtls _context结构体，结构体中保
        _rsa
    存了RSA密钥详细信息，这些详细信息不但包括公钥和私钥信息，还
    包括RSA算法加速相关信息。mbedtls   _context的具体结构如下：
        _rsa



    typedef struct
    {
     int ver;        /*!< Always 0.*/
     size_t len;        /*!< The size of \p N in Bytes. */
     mbedtls_mpi N;       /*!< The public modulus. */
     mbedtls_mpi E;       /*!< The public exponent. */
     mbedtls_mpi D;       /*!< The private exponent. */
     mbedtls_mpi P;       /*!< The first prime factor. */
     mbedtls_mpi Q;       /*!< The second prime factor. */
     mbedtls_mpi DP;     /*!< <code>D % (P - 1)</code>. */
     mbedtls_mpi DQ;     /*!< <code>D % (Q - 1)</code>. */
     mbedtls_mpi QP;     /*!< <code>1 / (Q % P)</code>. */
     int padding;        /*!< Selects padding mode:
                          #MBEDTLS_RSA_PKCS_V15 for 1.5 padding and
                          #MBEDTLS_RSA_PKCS_V21 for OAEP or PSS. */
    } mbedtls_rsa_context;



     RSA密钥初始化时通过参数MBEDTLS _V21指定填
        _RSA_PKCS
充方案为OAEP，同时指定单向散列函数算法，示例使用SHA256算
法作为单向散列算法。由于OAEP填充方法中将使用随机数对消息进
行填充，所以在加密过程中即使使用相同的密钥对明文进行加密，每
次得到的密文也不相同。




    mbedtls_rsa_init(&ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);




    3.RSA生成密钥



                          343

## Page 344

    RSA生成密钥接口为mbedtls_rsa_gen_key，该函数需要输入RSA
结构体、随机数生成接口、随机数结构体、模数位长度以及公开指
数，密钥信息将保存至RSA结构体中。示例中RSA模数的长度为2048
比特，公开指数为65537（0x01001）。mbedtls_rsa_gen_key接口原型
如下：


    int mbedtls_rsa_gen_key( mbedtls_rsa_context *ctx,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng,
    unsigned int nbits, int exponent );


                   由于RSA密钥生成过程计算量较大，生成时间较长，嵌入式终端
    中需要谨慎使用软件算法生成RSA密钥对。

    4.RSA加密

    RSA加密接口为mbedtls_rsa_pkcs1_encrypt，该函数需要输入RSA
结构体、随机数生成接口、随机数结构体、工作模式、消息长度和消
息，该函数的输出为密文。工作模式mode中
    MBEDTLS_RSA_PUBLIC表示公钥操作，MBEDTLS_RSA_PRIVATE
    表示私钥操作，此处使用公钥对消息进行加密。
    mbedtls_rsa_pkcs1_encrypt接口原型如下：


    int mbedtls_rsa_pkcs1_encrypt( mbedtls_rsa_context *ctx,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng,
    int mode, size_t ilen,
    const unsigned char *input,
    unsigned char *output );




    344

## Page 345

    5.RSA解密

     RSA解密接口为mbedtls_rsa_pkcs1_decrypt，该函数要输入RSA结
构体、伪随机数生成接口、伪随机数结构体、工作模式、密文以及输
出数组的最大长度，该函数输出为明文及明文长度。示例中使用RSA
私钥对密文进行解密。mbedtls_rsa_pkcs1_decrypt接口原型如下：

    int mbedtls_rsa_pkcs1_decrypt( mbedtls_rsa_context *ctx,
           int (*f_rng)(void *, unsigned char *, size_t),
           void *p_rng,
           int mode, size_t *olen,
           const unsigned char *input,
           unsigned char *output,
           size_t output_max_len );










           345

## Page 346

8.7.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     由于RSA算法依赖其他mbedtls算法模块，例如伪随机数生成器
和单向散列函数等，再加上RSA算法计算过程涉及大数运算以及较大
的密钥尺寸等因素，使得RSA示例中RAM和FLASH的消耗要远大于
前面几章中的示例。本示例共消耗约45KB FLASH空间和约32KB
RAM空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 08_rsa
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region   Used Size Region Size %age Used
             FLASH:      45068 B      2 MB    2.15%
               CCM:         0 GB     64 KB    0.00%
              SRAM:      32060 B    256 KB   12.23%
          IDT_LIST:         200 B     2 KB    9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    . setup rng ...    ok
    ! RSA Generating large primes may take minutes!
    1. RSA generate key ... ok
    +++++++++++++++++ rsa keypair +++++++++++++++++


                         346

## Page 347

N: E0E9960BF595B5F6C6251A3955CAC95F7CCC79F6060DBABFEEA94932E788A21A0B4755AFDDABBC50903FB916EC1FAB1EFB6724255C473B8558FFF6F14616B160148394
E: 010001
D: 10B7B6C6CE205755851B93916E1BBEA571AF4E8EC79B145083E58D62A7EC735ACAE5288203FB69E9F5C43C211A0D588E3053005023F074DA253D66C0E9B1721F197C9A
// 省略部分输出
+++++++++++++++++ rsa keypair +++++++++++++++++
2. RSA encryption ... ok
4B 93 F9 3A 6E E7 73 52 19 00 51 FD FD A7 B3 10
1E 56 65 BD EB 3A 7F F0 B7 1E E2 81 5B C6 C5 D8
61 44 89 DF B7 A3 D4 E2 A9 FA 5B C4 58 20 E1 C6
11 96 0C F2 55 12 72 C5 F6 CC D8 FB 52 0D 69 58
61 7B 03 48 01 E9 38 CB EA 97 19 DA EA A7 C9 3A
60 07 C7 26 A6 5C 4F 19 2D 21 DF A5 35 11 50 FC
6E 18 B2 AB 94 58 BB FF 79 11 79 EC 66 FA C0 8E
36 BE 56 6A E3 71 BE E0 4C 57 CB 77 3D DC 73 77
26 B4 B6 0F F8 94 80 BB A4 02 95 04 0A 47 41 89
7C 4A 4E E6 CF 9A A1 66 63 4A 5B FE 8E 3F 1F CC
88 D5 48 DE F2 2C 06 34 73 A3 1A AF 10 63 A5 98
CE 2A E6 7D A3 D3 F2 C7 F3 54 6B 3E CE F7 25 AB
CF 2F D9 03 91 3C 04 70 C1 3F B9 9A EA 84 65 9A
99 31 3C C4 A5 E9 8E 7D AD B3 D0 7D 6C 01 74 6B
58 6F 58 52 25 A7 AA 33 0B 93 1A FF 3C 09 42 1F
AC ED 8F 83 8E FA 0F 07 55 6F 54 BB 5E 77 A9 BB
3. RSA decryption ... ok
Hello, World!
4. RSA Compare results and plaintext ... ok










347

## Page 348

8.8 本章小结

  RSA算法是一种常用的公钥密码算法。RSA密钥分为公钥和私钥
两部分，通常RSA公钥用于加密而RSA私钥用于解密，公钥可以公
开，而私钥需要绝对保密。在实际应用中，RSA算法离不开RSA加速
技术和填充方法。由于在RSA填充过程需要使用随机数，所以在明文
和公钥完全相同的情况下，密文也并不相同。通过mbedtls RSA应用
工具和mbedtls基础示例部分可以发现，RSA密钥对组成复杂且长度
较长。虽然RSA算法较为成熟，但并不一定适合于物联网应用。










    348

## Page 349

        第9章 DH密钥协商

9.1 本章主要内容

  本章将介绍DH（Diffie-Hellman）密钥协商算法。上一章已经介
绍了基于大整数质因数分解问题的RSA算法，RSA算法的出现在一定
程度上解决了密钥配送的问题，但实际应用中也可以使用DH密钥协
商算法解决密钥配送问题。因为DH密钥协商算法基于离散对数问
题，本章先介绍离散对数问题的定义，再详细介绍DH密钥协商算法
的实现步骤。除了具体步骤之外，本章还将分析DH密钥协商算法的
安全性。

  在mbedtls部分将先介绍3种与DH密钥协商相关的工具：
dh_genprime、dh_server和dh_client。最后通过示例代码说明如何通过
mbedtls相关接口完成DH密钥协商。










    349

## Page 350

9.2 DH密钥协商数学基础

  DH密钥协商算法基于离散对数问题，在密码学中通常使用基于
有限循环群的离散对数问题进行构建。关于循环群和离散对数问题的
讨论可以回顾第3章有关内容。基于有限循环群的离散对数问题定义
如下。

定义9-1

  给定一个阶为p-1的有限循环群 ，循环群内的一个生成元a和另
一个元素b，离散对数问题是确定满足ax≡b mod p的整数x(0＜x＜p)的
值。

  由于a是一个生成元，可以通过指数运算生成群内的所有元素，
所以x肯定存在。如果已知生成元a和整数x，通过ax≡b mod p计算循
环群内的元素b非常容易，而反过来通过生成元a和循环群内的一个元
素b计算x却非常困难。










    350

## Page 351

9.3 DH密钥协商详细说明

  DH是一种密钥协商算法，由Whitfield Diffie和Martin Hellman在
1976年提出，算法允许通信双方在不安全通道交换共享参数，从而协
商出一个会话密钥。该算法的安全性基于离散对数求解困难问题
（Discrete Logarithm Problem，DLP）。推广到Diffie-Hellman的离散
对数问题的定义如下。

定义9-2

  给定一个阶为n的有限循环群G，循环群内的生成元为a，群内的
两个元素A=ax和B=ay，Diffie-Hellman离散对数问题是计算出群元素
axy。

  下面通过一个假想场景说明DH密钥协商算法。假想场景中Alice
和Bob借助DH密钥协商算法完成会话密钥的协商。密钥协商分为两
个阶段：DH共享参数和DH密钥协商。DH密钥协商过程如图9-1所
示。










    351

## Page 352

图9-1 DH密钥协商过程










352

## Page 353

9.3.1 DH共享参数

Alice和Bob在有限循环群 中选择相同的大素数p和生成元a作为
共享参数。具体过程如下：

1）选择大素数p；

2）在有限循环群中选择生成元a(1≤a≤p)。










353

## Page 354

    9.3.2 DH密钥协商

        在密钥协商阶段，Alice和Bob选择随机密钥作为私密参数，然后
    进行模幂运算得到公开参数进行交换，通过交换最终得到的公开参数
    和私密参数计算出会话密钥。具体过程如下：

        1）Alice选择一个随机密钥x(1≤x≤p-1)，计算A≡axmod p并发送给
    Bob；

        2）Bob选择一个随机密钥y(1≤y≤p-1)，计算B≡aymod p并发送给
    Alice；

        3）Bob收到A并计算得到共享密钥k≡Aymod p→(ax)ymod
    p→a xymod p；

   4）Alice收到B并计算得到共享密钥k≡Bymod p→(ay)xmod
p→axymod p。










        354

## Page 355

9.3.3 DH具体实践

下面通过一个具体示例说明DH密钥协商过程。

1.Alice和Bob确认共享参数

Alice和Bob确认共享参数，其中a=5，p=97，该共享参数构成的
一个阶为96的循环群。该循环群内的所有元素如表9-1所示。

    表9-1     循环群元素










355

## Page 356

2.Alice生成随机密钥x

Alice生成随机密钥x=36，通过查表可得A≡ax≡536≡50 mod 97。
Alice将A=50发送至Bob。

3.Bob生成随机数密钥y

Bob生成随机数密钥y=58，通过查表可得B≡ay≡558≡44 mod 97。
Bob将B=44发送给Alice。

4.Alice计算共享密钥



356

## Page 357

 k≡(B)x≡4436mod 97，使用模重复平方算法计算4436mod 97，如表
9-2所示。

      表9-2 模重复平方算法计算4436mod 97









    5.Bob计算共享密钥

     k≡(A)y≡5058mod 97，使用模重复平方算法计算5058mod 97，如表
    9-3所示。

        表9-3   模重复平方算法计算5058mod 97








    6.Alice和Bob获得共享密钥

    最后Alice和Bob获得相同的密钥k=75。





    357

## Page 358

9.3.4 DH密钥协商安全性分析

   假设Eve窃听Alice与Bob之间的DH密钥协商过程，Eve可以在这
条非安全通道上获得一些信息，如图9-2所示。但这些信息并不能让
Eve很容易地推算出Alice和Bob之间的共享密钥。Alice、Bob和Eve在
一次DH密钥协商过程中掌握的信息内容如表9-4所示。










    图9-2 Eve窃听Alice和Bob DH密钥协商过程
    表9-4   Alice、Bob和Eve掌握信息内容





    358

## Page 359

  经过上述过程后，Alice和Bob可以计算得到共享密钥k，而Eve可
能无法推算出共享密钥k。Eve可以截获到参数p、α、A和B，他可以
用穷举法计算5x≡50 mod 97和5y≡44 mod 97。但若模数p很大时，这种
穷举法往往并不可信。若Eve可以快速求解离散对数问题，那么就能
够从已截获的上述信息中解出x或y，最终推算出共享密钥k。遗憾的
是，目前世界上暂没有快速求解离散对数的方法，因此当所选的域参
数足够大时，x和y很难通过计算得到。为了提供DH密钥协商的安全
性，大素数p的长度应与RSA的模数n的长度相同，实际应用中大素数
p的长度不应小于2048比特。










    359

## Page 360

        图9-3 DH密钥协商中间人攻击

   DH密钥协商算法并不会对公钥发送者的身份进行认证，因此无
法阻止主动攻击者。在如图9-3所示场景中，Mallory侵入了Alice和
Bob的非安全传输通道，当Alice和Bob进行DH密钥协商时，Mallory
冒充了Alice或Bob。当Alice想要和Bob交换密钥时，实际上却与
Mallory交换了共享密钥K1，与此同时Bob与Mallory交换了共享密钥
K2。Alice获得了共享密钥K1，认为Bob也获得了相同的密钥，但此时
Bob却获得了共享密钥K2。也就是说Mallory截获了Alice的公钥，替
换为自己的公钥，并将其发送给Bob；同样Mallory也截获Bob的公
钥，替换为自己的公钥，并将其发送给Alice。这样Eve就可以轻松地

        360

## Page 361

对Alice与Bob之间发送的任何消息进行解密。Mallory可以更改消息，
用自己的密钥对消息重新加密，然后将消息发送给接收者。解决身份
认证的问题可以加入ECDSA或RSA数字签名，该部分内容将在第11
章进行介绍。










    361

## Page 362

9.4 常用共享参数

      上一节中使用的素数p很小，无法在真实环境中使用。另外若使
用不安全的算法产生的大素数p，DH密钥协商过程也会存在一定的安
全隐患。在《RFC-7919 Negotiated Finite Field Diffie-Hellman
Ephemeral Parameters for Transport Layer Security(TLS)》规范中定义
了5组安全的DH共享参数，建议用户在实际应用中从规范中进行选
择。下面将介绍其中的两组大素数p和生成元a。

1.2048-bit MODP Group

      生成元a=2，大素数p如下：




    FFFFFFFF FFFFFFFF ADF85458 A2BB4A9A AFDC5620 273D3CF1
    D8B9C583 CE2D3695 A9E13641 146433FB CC939DCE 249B3EF9
    7D2FE363 630C75D8 F681B202 AEC4617A D3DF1ED5 D5FD6561
    2433F51F 5F066ED0 85636555 3DED1AF3 B557135E 7F57C935
    984F0C70 E0E68B77 E2A689DA F3EFE872 1DF158A1 36ADE735
    30ACCA4F 483A797A BC0AB182 B324FB61 D108A94B B2C8E3FB
    B96ADAB7 60D7F468 1D4F42A3 DE394DF4 AE56EDE7 6372BB19
    0B07A7C8 EE0A6D70 9E02FCE1 CDF7E2EC C03404CD 28342F61
    9172FE9C E98583FF 8E4F1232 EEF28183 C3FE3B1B 4C6FAD73
    3BB5FCBC 2EC22005 C58EF183 7D1683B2 C6F34A26 C1B2EFFA
    886B4238 61285C97 FFFFFFFF FFFFFFFF





    2.3072-bit MODP Group

    生成元a=2，大素数p如下：




    FFFFFFFF FFFFFFFF ADF85458 A2BB4A9A AFDC5620 273D3CF1
    D8B9C583 CE2D3695 A9E13641 146433FB CC939DCE 249B3EF9
    7D2FE363 630C75D8 F681B202 AEC4617A D3DF1ED5 D5FD6561
    2433F51F 5F066ED0 85636555 3DED1AF3 B557135E 7F57C935
    984F0C70 E0E68B77 E2A689DA F3EFE872 1DF158A1 36ADE735



    362

## Page 363

30ACCA4F 483A797A BC0AB182 B324FB61 D108A94B B2C8E3FB
B96ADAB7 60D7F468 1D4F42A3 DE394DF4 AE56EDE7 6372BB19
0B07A7C8 EE0A6D70 9E02FCE1 CDF7E2EC C03404CD 28342F61
9172FE9C E98583FF 8E4F1232 EEF28183 C3FE3B1B 4C6FAD73
3BB5FCBC 2EC22005 C58EF183 7D1683B2 C6F34A26 C1B2EFFA
886B4238 611FCFDC DE355B3B 6519035B BC34F4DE F99C0238
61B46FC9 D6E6C907 7AD91D26 91F7F7EE 598CB0FA C186D91C
AEFE1309 85139270 B4130C93 BC437944 F4FD4452 E2D74DD3
64F2E21E 71F54BFF 5CAE82AB 9C9DF69E E86D2BC5 22363A0D
ABC52197 9B0DEADA 1DBF9A42 D5C4484E 0ABCD06B FA53DDEF
3C1B20EE 3FD59D7C 25E41D2B 66C62E37 FFFFFFFF FFFFFFFF










363

## Page 364

9.5 mbedtls DH应用工具

  mbedtls为各个模块提供了应用工具，应用工具主要用于演示模
块接口的使用方法。mbedtls DH密钥协商模块提供了3个应用工具：
dh_genprime、dh_client和dh_server。下面通过一个具体场景介绍应用
工具的使用方法。示例场景中客户端和服务器基于DH算法模块完成
密钥协商，详细过程如图9-4所示。










    364

## Page 365

图9-4 服务器和客户端通过DH密钥协商获得共享密钥









365

## Page 366

9.5.1 dh_genprime

    _genprime可生成DH密钥协商参数，这些参数包括大素数P和
dh
生成元G，可以通过参数指定大素数的长度，默认为2048比特。DH
密钥协商参数将保存在dh_prime.txt文件中。由于在该过程中需要生
成随机数并进行素性检测，可能会导致其运行时间较长。生成DH密
钥协商参数具体过程如下：




# 生成共享参数
$ dh_genprime
# 输出内容
! Generating large primes may take minutes!
. Seeding the random number generator... ok
. Generating the modulus, please wait... ok
. Verifying that Q = (P-1)/2 is prime... ok
. Exporting the value in dh_prime.txt... ok
# 查看共享参数
$ cat dh_prime.txt
# 输出内容
P = D8B863C9514D994668AB11B9D91B55D3334E4A14214FA3E23786AB7E6598864BC52D70099C7E2AD3BCC83C3A20362278367C5FC80F7115229C552E
04318978B873AF1D6EED2394233AE33BEF4771C4179BC35B815040D8C1690D9E7EFC1E36147A48454E6EDBB5F00557F4719A4D06AC1D4AECC79D0B3372D347BDEE19F3F07EB24357D87EF496F6FF2C9E1EE2075BE4D74EBE2A794605AA06FECB50FB1A9594F53F0954B26CCC29723039749748EC3FD3555BFDD9B30FF1B540C25D477D406D679CB697931F4C1EF135F8BF9AF42B85850D01EFF31C1B5C7C2EB42F92379F367D7280265B5594B8C89F89AD4A91254F38DDA22D8B577E20D8F9716736C5F3D3
G = 04










366

## Page 367

9.5.2 dh_server


密钥协商过程中服务器会对密钥协商参数进行签名操作，客户端
进行验签，所以需要使用rsa_genkey工具生成RSA密钥对，私钥保存
于rsa_priv.txt文件中，公钥保存于rsa_pub.txt文件中。

# 生成RSA密钥对文件
$ rsa_genkey
# 输出内容
. Seeding the random number generator... ok
. Generating the RSA key [ 2048-bit ]... ok
. Exporting the public key in rsa_pub.txt....  ok
. Exporting the private key in rsa_priv.txt... ok
# 查看密钥对
$ ls
rsa_priv.txt rsa_pub.txt

dh  _server将完成以下工作：

1）从rsa_priv.txt中读取RSA私钥，从dh_prime.txt中读取DH密钥
协商共享参数；

2）绑定本地11999端口并等待客户端连接；

3）计算服务器DH公钥，DH公钥经过单向散列之后使用RSA私
钥签名，将服务器DH公钥和签名值合并后发送至客户端；

4）接收客户端DH公钥，计算共享密钥，该共享密钥将作为对称
加密阶段的密钥；

5）使用对称加密算法加密“==Hello there!==”，并把加密结果发


367

## Page 368

送至客户端。



# 启动dh服务器
$ dh_server
# 输出内容
. Seeding the random number generator
. Reading private key from rsa_priv.txt
. Reading DH parameters from dh_prime.txt
. Waiting for a remote connection
# 当有dh客户端发起连接后输出情况
. Sending the server's DH parameters
. Receiving the client's public value
. Shared secret: 071c59b4d6cba2c36ffade81e9ecb163...
. Encrypting and sending the ciphertext










368

## Page 369

9.5.3 dh_client

dh    _client将完成以下工作：

1）从rsa_pub.txt中读取RSA公钥，从dh_prime.txt中读取DH密钥
协商共享参数；

2）连接服务器11999端口；

3）接收服务器DH公钥和签名，计算服务器DH公钥散列值，使
用RSA公钥验证签名合法性；

4）发送客户端DH公钥，计算共享密钥，该共享密钥将作为对称
加密阶段的密钥；

5）接收来自服务器的密文，使用共享密钥解密。


# 启动 dh 客户端
$ dh_client
# 输出内容
. Seeding the random number generator
. Reading public key from rsa_pub.txt
. Connecting to tcp/localhost/11999
. Receiving the server's DH parameters
. Verifying the server's RSA signature
. Sending own public value to server
. Shared secret: 071c59b4d6cba2c36ffade81e9ecb163...
. Receiving and decrypting the ciphertext
. Plaintext is "==Hello there!=="









369

## Page 370

9.6 mbedtls DH示例

  本节示例将模拟服务器和客户端进行DH密钥协商，服务器和客
户端分别生成DH公开参数。由于模拟环境中服务器和客户端并没有
发生网络通信，所以双方会通过共享内存的方式交换DH公开参数，
最后分别计算得到共享密钥。出于性能方面的考虑，mbedtls DH密钥
协商过程中并不会对大素数P进行素性检测，建议用户在实际应用中
使用规范文档中所提供的几组DH共享参数。示例代码参考自mbedtls
示例代码，在mbedtls示例代码的基础上增加或修改了部分内容。本
节示例均基于Zephyr系统构建，借助Zephyr系统良好的适配性，本节
示例不但可运行于Linux平台，也可运行于STM32F429等硬件平台。
为了正确运行示例代码，需要在mbedtls_config.h配置文件中增加相关
宏定义。宏定义描述如表9-5所示。

       表9-5 mbedtls_config.h配置文件宏定义描述










  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本节示例位于09_dh文件夹中。另外，

        370

## Page 371

mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。










371

## Page 372

9.6.1 示例代码

      示例代码用于演示如何使用mbedtls接口完成DH密钥协商，主要
包括随机数配置、生成共享参数、生成公开参数、读取公开参数和生
成共享密钥几个部分。由于大素数生成过程比较耗时，生成公开参数
部分使用RFC 7919中提供的标准数据作为测试样本。示例代码如代
码清单9-1所示，示例中相关接口描述如表9-6所示。

      代码清单9-1 dh密钥协商示例



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/dhm.h"
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/platform.h"
    // 省略部分中间代码
    int main(void)
    {
     size_t n = 0;
     const char *pers = "simple_dh";
     uint8_t cli_pub[256], cli_secret[256];
     uint8_t srv_pub[256], srv_secret[256];
     mbedtls_platform_set_printf(printf);
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     mbedtls_dhm_context dhm_cli, dhm_srv;
     mbedtls_dhm_init(&dhm_cli);
     mbedtls_dhm_init(&dhm_srv);
     mbedtls_entropy_init(&entropy);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
         MBEDTLS_ENTROPY_MAX_GATHER, MBEDTLS_ENTROPY_SOURCE_STRONG);
     mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
         (const unsigned char *) pers, strlen(pers));
     mbedtls_printf("\n     . setup rng ... ok\n\n");
    mbedtls_mpi_read_string(&dhm_srv.P, 16, T_P);
    mbedtls_mpi_read_string(&dhm_srv.G, 10, GENERATOR);
    dhm_srv.len = mbedtls_mpi_size(&dhm_srv.P);
    mbedtls_mpi_read_string(&dhm_cli.P, 16, T_P);
    mbedtls_mpi_read_string(&dhm_cli.G, 10, GENERATOR);
    dhm_cli.len = mbedtls_mpi_size(&dhm_cli.P);
    mbedtls_printf(" 1. dh generate 2048 bit prime(G, P) ... ok\n");
    mbedtls_dhm_make_public(&dhm_srv, 256, srv_pub, sizeof(srv_pub),
        mbedtls_ctr_drbg_random, &ctr_drbg);
    dump_buf(" 2. dh server generate public parameter:", srv_pub, sizeof(srv_pub));


     372

## Page 373

 mbedtls_dhm_make_public(&dhm_cli, 256, cli_pub, sizeof(cli_pub),
     mbedtls_ctr_drbg_random, &ctr_drbg);
 dump_buf(" 3. dh client generate public parameter:", cli_pub, sizeof(cli_pub));
 mbedtls_dhm_read_public(&dhm_srv, cli_pub, sizeof(cli_pub));
 mbedtls_printf(" 4. dh server read public ... ok\n");
 mbedtls_dhm_read_public(&dhm_cli, srv_pub, sizeof(srv_pub));
 mbedtls_printf(" 5. dh client read public ... ok\n");
 mbedtls_dhm_calc_secret(&dhm_srv, srv_secret, sizeof(srv_secret),
     &n, mbedtls_ctr_drbg_random, &ctr_drbg);
 dump_buf(" 6. dh server generate secret:", srv_secret, sizeof(srv_secret));
 mbedtls_dhm_calc_secret(&dhm_cli, cli_secret, sizeof(cli_secret),
     &n, mbedtls_ctr_drbg_random, &ctr_drbg);
 dump_buf(" 7. dh client generate secret:", cli_secret, sizeof(cli_secret));
 memcmp(cli_secret, srv_secret, sizeof(srv_secret));
 mbedtls_printf(" 8. dh checking secrets ... ok\n\n");
 mbedtls_dhm_free(&dhm_cli);
 mbedtls_dhm_free(&dhm_srv);
 mbedtls_entropy_free(&entropy);
 mbedtls_ctr_drbg_free(&ctr_drbg);
 return 0;
}



 表9-6 dh密钥协商相关接口描述










 373

## Page 374

9.6.2 代码说明

dh密钥协商示例简图如图9-5所示。










图9-5 dh密钥协商示例简图

1.配置随机数

dh生成公开参数并计算共享密钥过程中需要使用随机数接口，首

    374

## Page 375

先需要完成随机数的配置工作，该过程包括熵源接口添加、熵源属性
设置及通过个性化字符串更新种子。伪随机数生成器配置过程的详细
描述可回顾7.6.2节。

2.生成共享参数

    共享参数包括大素数P和生成元G，该过程通常需要花费一定时
间。示例将从预先准备好的向量中进行导入，该向量来自rfc7919，
导入过程可以使用mbedtls_mpi_read_string接口。具体内容如下：


    The 2048-bit group has registry value 256 and is calculated from the
    following formula:
    The modulus is:
    p = 2^2048 - 2^1984 + {[2^1918 * e] + 560316 } * 2^64 - 1
    The hexadecimal representation of p is:
    FFFFFFFF FFFFFFFF ADF85458 A2BB4A9A AFDC5620 273D3CF1
    D8B9C583 CE2D3695 A9E13641 146433FB CC939DCE 249B3EF9
    7D2FE363 630C75D8 F681B202 AEC4617A D3DF1ED5 D5FD6561
    2433F51F 5F066ED0 85636555 3DED1AF3 B557135E 7F57C935
    984F0C70 E0E68B77 E2A689DA F3EFE872 1DF158A1 36ADE735
    30ACCA4F 483A797A BC0AB182 B324FB61 D108A94B B2C8E3FB
    B96ADAB7 60D7F468 1D4F42A3 DE394DF4 AE56EDE7 6372BB19
    0B07A7C8 EE0A6D70 9E02FCE1 CDF7E2EC C03404CD 28342F61
    9172FE9C E98583FF 8E4F1232 EEF28183 C3FE3B1B 4C6FAD73
    3BB5FCBC 2EC22005 C58EF183 7D1683B2 C6F34A26 C1B2EFFA
    886B4238 61285C97 FFFFFFFF FFFFFFFF
    The generator is: g = 2


3.生成公开参数

    导入了共享参数G和P以后，可以生成公开参数GX或GY。生成公
开参数的接口为mbedtls_dhm_make_public，接口内部会完成私钥X或
Y的生成，并导出公开参数GX或GY。该接口输入参数为dhm结构体、
私钥长度、用于存放公开参数的数组长度、随机数接口及随机数结构
体，输出得到公开参数。mbedtls_dhm_make_public接口原型如下：


    375

## Page 376

int mbedtls_dhm_make_public( mbedtls_dhm_context *ctx, int x_size,
    unsigned char *output, size_t olen,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng );


4.读取公开参数

     示例中为了构建dh密钥协商过程，需要读取对方的公开参数，读
取公开参数的接口为mbedtls_dhm_read_public，需要输入dhm结构
体、对方的公开参数和对方公开参数长度，读取成功后会保存到自己
的dhm结构体中。mbedtls_dhm_read_public接口原型如下：


    int mbedtls_dhm_read_public( mbedtls_dhm_context *ctx,
    const unsigned char *input, size_t ilen );


5.生成共享密钥

     通过上面的过程已经具备生成共享密钥的条件，生成共享密钥接
口为mbedtls_dhm_calc_secret，需要输入dhm结构体、用于存放共享
密钥的数组长度、随机数接口及随机数结构体，输出得到共享密钥和
共享密钥长度。mbedtls_dhm_calc_secret接口原型如下：


    int mbedtls_dhm_calc_secret( mbedtls_dhm_context *ctx,
    unsigned char *output, size_t output_size, size_t *olen,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng );









    376

## Page 377

9.6.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     由于示例中DH密钥协商过程并没有涉及网络通信，而是使用共
享内存的方式交换公开参数，所以本示例中RAM消耗情况与第8章相
差不大。在没有开启网络协议栈的情况下，27K左右的RAM消耗对于
物联网终端设备来说是一个不小的“负担”。本示例共消耗约40KB
FLASH空间和约27KB RAM空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 09_dh
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region       Used Size Region Size %age Used
             FLASH:      40028 B          2 MB    1.91%
               CCM:       0 GB           64 KB    0.00%
              SRAM:      26936 B        256 KB   10.28%
          IDT_LIST:       200 B           2 KB    9.77%
    $ make flash
    . setup rng ...    ok
    1. dh generate 2048 bit prime(G, P) ... ok
    2. dh server generate public parameter:
    BD 7D 10 99 17 45 D0 37 4F EF 0C C6 C8 8A BF 23
    58 E7 1C 90 B7 F6 D2 37 5F 02 1C D2 21 7B 95 23
    # server输出的公开参数长度为2048位(256字节)，此处省略部分内容


                         377

## Page 378

3. dh client generate public parameter:
1D 73 63 0A EF CD 06 AE CE 45 3E FB 4B 0C A6 24
85 96 0F 5E A8 A8 C1 DE 94 71 35 FE DD 3A FA 87
# client输出的公开参数长度为2048位(256字节)，此处省略部分内容
4. dh server read public ...  ok
5. dh client read public ...  ok
6. dh server generate secret:
72 C4 4B E9 CC CE CF BE 9F C4 F0 6C D7 18 62 67
9E D1 B4 7A 08 62 26 0C 68 C8 4E 06 DE BC C1 B3
# server计算获得共享密钥长度为2048位(256字节)，此处省略部分内容
7. dh client generate secret:
72 C4 4B E9 CC CE CF BE 9F C4 F0 6C D7 18 62 67
9E D1 B4 7A 08 62 26 0C 68 C8 4E 06 DE BC C1 B3
# client计算获得共享密钥长度为2048位(256字节)，此处省略部分内容
8. dh checking secrets ... ok




从控制台的输出内容可以看出：

1）模拟服务器和客户端输出的DH公钥为2048比特（256字
节），两者的公开参数并不相同。

2）模拟服务器和客户端计算出相同的共享密钥，共享密钥的长
度也为2048比特（256字节）。










                              378

## Page 379

9.7 本章小结

  本章介绍了DH密钥协商算法，DH密钥协商算法基于离散对数问
题构建。与RSA算法不同，DH算法只能应用于密钥协商，不能应用
于身份认证和数据加解密。DH算法也不能抵抗主动攻击者，在TLS
协议中DH算法不能独立存在，需要与RSA签名算法或ECDSA算法结
合。DH算法的强度依赖于大素数p，建议长度为2048比特或3072比
特。由于DH密钥的尺寸较大，在物联网应用中并没有传输效率优
势，建议在物联网应用中用ECDH算法代替DH算法。










    379

## Page 380

    第10章   ECDH密钥协商

10.1 本章主要内容

                本章将介绍ECDH密钥协商过程。ECDH密钥协商算法基于椭圆
曲线密码系统（ECC），使用较短的密钥长度可提供与RSA或DH算
法同等的安全等级，密钥长度为160~256比特的椭圆曲线算法与密钥
长度为1024~3072比特的非ECC算法安全强度相同。本章将介绍椭圆
曲线的一些基础知识，这些基础知识包括椭圆曲线的定义、实数域上
的椭圆曲线和有限域上的椭圆曲线。为了在椭圆曲线上构造离散对数
问题，本章还介绍了椭圆曲线上的群操作，椭圆曲线上的群操作可分
为相同点相加和不同点相加，虽然椭圆曲线上的群加法操作使
用“+”符号，但是群加法操作并不是简单的坐标点相加。本章将尽量
避免涉及复杂的数学运算，而是通过示例说明如何将循环群应用到椭
圆曲线密码体制中。本章将介绍两种常用的椭圆曲线——secp256r1
和secp384r1，并通过mbedtls ECDH应用工具和mbedtls ECDH示例说
明ECDH密钥交换的具体过程。










380

## Page 381

10.2 椭圆曲线定义

                在过去很长的时间中，椭圆曲线并没有引起数学家们的重视，直
到1985年才由德国数学家格哈德·费赖第一次创造性地提出：如果费
马大定理有整数解，则必定存在一条与之对应的椭圆曲线。格哈德·
费赖的观点打开了使用椭圆曲线证明费马大定理的大门，引起了人们
对椭圆曲线研究的重视。同年，Neal Koblitz和Victor Miller分别独立
提出椭圆曲线在密码学中的应用，提出了椭圆曲线密码系统。椭圆曲
线密码系统简称为ECC，它具有密钥尺寸短、安全性高等特点，是近
几年密码学应用领域的研究热点。

                椭圆曲线被描述为一个二元方程解的集合，本节将分别介绍实数
域上的椭圆曲线和有限域上的椭圆曲线。










381

## Page 382

10.2.1 实数域上的椭圆曲线

实数域上的椭圆曲线定义如下。

定义10-1 实数域上的椭圆曲线

假设a,b∈R，其满足4a3+27b2≠0，方程

y2=x3+ax+b

的所有解(x,y)∈R×R，连同一个无穷远点σ组成的集合E。

椭圆曲线有多种表示形式，它们都有各自的用途。但关于椭圆曲
线的各种性质已经超出了本书的讨论范围，本节仅给出椭圆曲线的3
个简单特质。

·椭圆曲线的形状并不是椭圆。

·椭圆曲线是一条光滑的曲线。

·椭圆曲线关于X轴对称。

如图10-1所示为一条实数域上的椭圆曲线y2=x3-7x+10，如图10-2
所示也是一条实数域上的椭圆曲线y2=x3-4x。虽然两个椭圆曲线在外
形上存在差异，但这两条曲线都符合前文提到的3个特质。




382

## Page 383

图10-1 椭圆曲线y2=x3-7x+10










383

## Page 384

图10-2 椭圆曲线y2=x3-4x










384

## Page 385

10.2.2 有限域上的椭圆曲线

 实数域上的椭圆曲线并不适合构建密码体制。为了把椭圆曲线上
的点离散化，需要把椭圆曲线定义到有限域上。椭圆曲线中最常用的
有限域便是素域GF(p)，有限域及素域相关知识请回顾第3章相关内
容。下面给出有限域中椭圆曲线的定义。

定义10-2 有限域上的椭圆曲线

 假设p＞3且p为素数，a,b∈Zp且满足4a3+27b2≠0，Zp上的同余方
程

 y2≡x3+ax+b mod p

 的所有解(x,y)∈Zp×Zp，连同一个无穷远点σ构成的集合E。

 定义在有限域中的椭圆曲线其变量和系数均来自集合Zp={1,2,
…,p-2,p-1}，例如当p=23，其变量x和系数a、b的取值范围为
{0,1,2...,21,22}。此处的椭圆曲线通过模p运算把计算结果缩小到一个
可知的范围中。如图10-3所示为有限域中的椭圆曲线y2≡x3+2x+2 mod
17。观察图10-3可以发现，有限域中的椭圆曲线由一系列的离散点组
成，其形状和实数域中的椭圆曲线完全不同。






 385

## Page 386

图10-3 椭圆曲线y2≡x3+2x+2 mod 17

该有限域Z17上的椭圆曲线共有19个点（包含无穷远点），这些
离散点的具体坐标如表10-1所示。

表10-1 椭圆曲线方程y2≡x3+2x+2 mod 17（不包括无穷远点）








386

## Page 387

10.3 椭圆曲线上群操作

   在上一节中，已经把椭圆曲线方程y2≡x3+2x+2mod17上的所有离
散点构成一个具有19个元素的集合。为了在椭圆曲线上构建离散对数
问题，除了需要一个有限个数的集合之外，还需要在该集合上定义一
种合适的“加法”操作。加法操作可理解为通过椭圆曲线上的两个已知
点计算得到第3个点。假设使用加法符号“+”表示群操作，两点相加得
到第3个点可以如下表示。

定义10-3 椭圆曲线上的群操作

   P+Q=R

   (x1,y1)+(x2,y2)=(x3,y3)

   此处的群操作虽然使用加法符号替代，但是运算过程并不是简单
的坐标点相加，例如P=(1,2)和Q=(3,4)，R≠(4,6)。本节从两个角度讨
论椭圆曲线中的群操作：几何角度和代数角度。










    387

## Page 388

10.3.1 群操作几何描述

  为了方便讨论椭圆曲线群操作原理，本节先在实数域讨论椭圆曲
线的群操作。此处群操作可分为不同点相加和相同点相加。假设椭圆
曲线为y2=x3-7x+10，已知椭圆曲线上的P=(1,2)和Q=(3,4)。

1.不同点相加

  通过已知点P=(1,2)和点Q=(3,4)，计算R=P+Q。几何计算方法如
下：

  1）画一条经过点P和点Q的直线，该直线与椭圆曲线交于第3
点；

  2）将上一步获得的第3点关于X轴映射，得到的映射点便是群操
作结果R=(-3,2)。

  如图10-4所示为实数域上不同点相加的具体步骤。

2.相同点相加

  通过已知点Q=(1,2)，计算R=Q+Q。几何计算方法如下：

  1）画一条经过Q的切线，与椭圆曲线交于第2点；

  2）将上一步获得的第2点关于X轴映射，得到的映射点便是群操

      388

## Page 389

作结果R=(-1,-4)。

如图10-5所示为实数域上相同点相加的具体步骤。










图10-4 实数域上不同点相加










389

## Page 390

        图10-5 实数域上相同点相加

  根据第3章的相关内容，群具有封闭性、结合律、单位元、逆元
和交换律。椭圆曲线群操作的运算结果也在椭圆曲线上，因此符合群
定义中的封闭性；除此之外，椭圆曲线群操作也满足结合律和交换
性。根据上述方法计算无穷远点σ与椭圆曲线上一点P相加可以表示
为：

  P+σ=P

  无穷远点σ可以理解为Y正半轴或负半轴的无穷远处，还可以更


    390

## Page 391

简单地理解为普通加法中的“零点”，在群定义中称为单位元或中性
元。点P与无穷远点σ相交得到的点为P'，被称为点P的逆元，它满足
P+(-P)=σ。










    391

## Page 392

    10.3.2 群操作代数描述

    根据前面的几何描述很容易推导出实数域中椭圆曲线群操作的代
数描述。已知点P(x1,y1)和点Q(x2,y2)，计算R(x3,y3)=P(x1,y1)+Q(x2,y2)
的代数描述如下：

    公式10-1 实数域中椭圆曲线群操作

    x3=s 2 -x1-x2

    y3=s(x1-x3)-y1

    其中，








    前面的讨论均基于实数域，实数域对于构建密码学体制并没有太
大帮助，我们还需要把代数计算过程推广到有限域。相较于实数域中
的椭圆曲线，有限域中的椭圆曲线增加了模运算，并且参数和系数都
属于集合Zp。下面给出有限域上椭圆曲线群操作代数描述。

公式10-2 有限域中椭圆曲线群操作


    392

## Page 393

x3=s2-x1-x2 mod p

y3=s(x1-x3)-y1 mod p

其中，









当相同点相加时，s表示经过点P的切线斜率；不同点相加时，s
表示经过点P和点Q的直线的斜率。










393

## Page 394

10.3.3 群操作动手实践

下面通过一个具体示例说明有限域中椭圆曲线群加法操作。

1.不同点群操作

已知某椭圆曲线在有限域Z17上的曲线方程y2≡x3+2x+2mod17，在
该椭圆曲线上选取点P(10,6)和点Q(3,16)，计算R=P+Q。

1）计算斜率s。




2）分别计算x3和y3。

x3≡s2-x1-x2≡1-10-3≡-12≡5mod17

y3≡s(x1-x3)-y1≡1·(10-5)-6≡-1≡16mod17

所以群操作的结果为R(5,16)=P(10,6)+Q(3,16)。

该示例也可通过几何法计算R=P+Q，相比于代数解法，几何解法
更容易理解。详细过程如图10-6所示。

1）绘制离散点。

绘制有限域上的椭圆曲线y2≡x3+2x+2mod17上的所有离散点。

    394

## Page 395

2）绘制经过点P和点Q的直线。

在代数法中我们已经计算得到经过点P和点Q的直线斜率为1，经
过点P画一条与X轴夹角为45度的斜直线。由于这条直线无法与点Q相
交，所以把点Q向右平移17个单元格获得扩展点M。这条斜直线经过
椭圆曲线上的一个离散点N(5,1)；

3）找出对称映射点。

经过点N(5,1)画一条垂直于X轴的直线，该直线经过椭圆曲线上
的一个离散点R(5,16)，所以群操作的结果为
R(5,16)=P(10,6)+Q(3,16)。










395

## Page 396

    图10-6 不同点群操作

2.相同点群操作

  已知某椭圆曲线在有限域Z11上的曲线方程y2≡x3+2x+2mod11，在
该椭圆曲线上选取点P(1,4)，计算R=2P。

有限域Z11上的椭圆曲线y2≡x3+2x+2mod11共有8个点，分别是
(1,4)，(1,7)，(2,5)，(2,6)，(5,4)，(5,7)，(9,1)和(9,10)，如图10-7所
示。



396

## Page 397

图10-7 相同点群操作

1）计算斜率s。





计算斜率s时需要计算整数8关于模11的乘法逆元，该乘法逆元的
计算结果为7，也就是8-1≡7mod11。

2）计算x3和y3。

    397

## Page 398

x3≡s2-x1-x2≡22-1-1≡2mod11

y3≡s(x1-x3)-y1≡2(1-2)-4≡-6≡5mod11

所以R=2P=(1,4)+(1,4)=(2,5)，通过图10-7可确认点R也位于椭圆
曲线上。










398

## Page 399

10.4 椭圆曲线离散对数问题

  为了构建基于椭圆曲线的离散对数密码系统，除了定义椭圆曲线
群操作之外，还需要找到一个关于椭圆曲线的循环群。

  假设在有限域Z11上的椭圆曲线方程为y2=x3+2x+2mod11，选取
P=(1,4)作为起始点，分别计算2P、3P...nP，计算结果如表10-2所示。

  表10-2中各元素正好构成了一个阶为9的循环群。也就是说以
P(1,4)作为生成元，通过群运算可生成循环群内的所有元素。

     表10-2 椭圆曲线方程y2=x3+2x+2mod11所有点










    借助椭圆曲线循环群和椭圆曲线的基础知识，可以进一步构建椭
    圆曲线构建离散对数问题。椭圆曲线离散对数问题（ECDLP）定义
    如下。

    定义10-4 椭圆曲线离散对数问题ECDLP


    399

## Page 400

    给定一个椭圆曲线E，考虑生成元P和另一个元素T。则DL问题
    是找到整数d，满足：





  定义10-4中E为有限域上的椭圆曲线，P为椭圆曲线上的一个生成
元，d为私钥（通常为整数），T为公钥（椭圆曲线上的某点
(xT,yT)）。已知点P、计算dP的过程有时又被称为标量乘法。但这种
描述往往具有误导性，因为计算dP时并不是简单的坐标相乘。

  已知点P，计算dP相对容易，而通过点P和点T计算d却很困难。
下面通过一个具体示例说明椭圆曲线离散对数问题的计算过程。

  已知椭圆曲线方程为y2=x3+2x+2mod11，点P=(1,4)，d=2019，计
算椭圆曲线点T=dP。

  通过表10-2可知循环群的阶为9，也就是说循环群内个元素的循
环周期为9，所以T=2019P=3P，通过表10-2可知T=3P=(9,10)。已知点
P和d（相当于私钥）很容易计算得到点T（相当于公钥），但是通过
点P和点T却很难确定d，d有很多种可能结果，例如3、12、21和30
等。为了方便理解，可以将点P看作起点，通过在椭圆曲线上的各离
散点间不断跳跃，直到终点T（公钥）为止，跳跃到终点T所需的次
数为d（私钥）。从点P跳跃到点8P的过程如图10-8所示。




    400

## Page 401

图10-8 点P到点8P跳跃过程










401

## Page 402

10.5 常用有限域上的椭圆曲线

为了清晰地解释椭圆曲线密码系统的原理，之前节均使用了参数
较为简单的椭圆曲线，但在实际应用中的椭圆曲线参数往往比较复
杂。椭圆曲线的详细介绍可参考《SEC 1:Elliptic Curve
Cryptography,Version 2.0》[1]，常用的椭圆曲线可参考《SEC
2:Recommended Elliptic Curve Domain Parameteres,Version 2.0》[2]。在
以上两份文档中，椭圆曲线一般由以下参数组成：

T=(p,a,b,G,n,h)

通过模数P和两个系数a、b，可构成椭圆曲线方程：

y    2=x3+ax+b mod p

G(Gx,Gy           )为椭圆曲线群的生成元，椭圆曲线群的生成元G本质为
一个坐标点；n为一个素数，用于表示椭圆曲线群的阶，也就是椭圆
曲线群元素的个数；整数h为余因数。椭圆曲线参数的具体描述如表
10-3所示。

    表10-3     椭圆曲线参数说明








402

## Page 403

      关于椭圆曲线群的生成元G包含Gx和Gy两个参数，该标准规范中
定义了两种表述方式——压缩模式和非压缩模式，非压缩模式以04开
始，而压缩模式以03开始。实际应用中一般使用非压缩模式。

      随着椭圆曲线密码系统的不断发展，市面上出现了各种各样的椭
圆曲线。根据《RFC4492 Elliptic Curve Cryptography(ECC)Cipher
Suites for Transport Layer Security(TLS)》[3]中的相关描述，Transport
Layer Security可支持以下椭圆曲线：



    enum {
    sect163k1 (1), sect163r1 (2), sect163r2 (3),
    sect193r1 (4), sect193r2 (5), sect233k1 (6),
    sect233r1 (7), sect239k1 (8), sect283k1 (9),
    sect283r1 (10), sect409k1 (11), sect409r1 (12),
    sect571k1 (13), sect571r1 (14), secp160k1 (15),
    secp160r1 (16), secp160r2 (17), secp192k1 (18),
    secp192r1 (19), secp224k1 (20), secp224r1 (21),
    secp256k1 (22), secp256r1 (23), secp384r1 (24),
    secp521r1 (25),
    reserved (0xFE00..0xFEFF),
    arbitrary_explicit_prime_curves(0xFF01),
    arbitrary_explicit_char2_curves(0xFF02),
    (0xFFFF)
    } NamedCurve;



      在RFC4492中椭圆曲线的定义由两部分组成：名称和编号。例
如，“secp256r1(23)”表示该椭圆曲线的名称为“secp256r1”
        ，而该椭圆
曲线的编号为23。椭圆曲线的名称与编号由IANA（互联网数字分配
机构）负责协调、定义与维护，通过这些预定义名称与编号可规范椭
圆曲线的应用。下面介绍两个常用的椭圆曲线：secp256r1和
secp384r1。

1.椭圆曲线secp256r1



    403

## Page 404

     大素数p，p的长度为256比特（32字节），p=2224(232-
1)+2192+296-1。


    p = FFFFFFFF 00000001 00000000 00000000 00000000 FFFFFFFF FFFFFFFF FFFFFFFF


    椭圆曲线方程E：y2≡x3+ax+b mod p。


    a = FFFFFFFF 00000001 00000000 00000000 00000000 FFFFFFFF FFFFFFFF FFFFFFFC
    b = 5AC635D8 AA3A93E7 B3EBBD55 769886BC 651D06B0 CC53B0F6 3BCE3C3E 27D2604B


  生成元G(Gx,Gy)。

Gx = 6B17D1F2 E12C4247 F8BCE6E5 63A440F2 77037D81 2DEB33A0 F4A13945 D898C296
Gy = 4FE342E2 FE1A7F9B 8EE7EB4A 7C0F9E16 2BCE3357 6B315ECE CBB64068 37BF51F5


    椭圆曲线的阶n。


    n = FFFFFFFF 00000000 FFFFFFFF FFFFFFFF BCE6FAAD A7179E84 F3B9CAC2 FC632551


    2.椭圆曲线secp384r1

     大素数p，p的长度为384比特（48字节），p=2384-2128-296+232-
1。


    p = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF
    FFFFFFFE FFFFFFFF 00000000 00000000 FFFFFFFF


    椭圆曲线方程E：y2≡x3+ax+b mod p。


    a = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF
    FFFFFFFE FFFFFFFF 00000000 00000000 FFFFFFFC

    404

## Page 405

b = B3312FA7 E23EE7E4 988E056B E3F82D19 181D9C6E FE814112 0314088F
5013875A C656398D 8A2ED19D 2A85C8ED D3EC2AEF


生成元G(Gx,Gy)。

Gx = AA87CA22 BE8B0537 8EB1C71E F320AD74 6E1D3B62 8BA79B98
     59F741E0 82542A38 5502F25D BF55296C 3A545E38 72760AB7
Gy = 3617DE4A 96262C6F 5D9E98BF 9292DC29 F8F41DBD 289A147C
     E9DA3113 B5F0B8C0 0A60B1CE 1D7E819D 7A431D7C 90EA0E5F


椭圆曲线的阶n。


    n = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF C7634D81
        F4372DDF 581A0DB2 48B0A77A ECEC196A CCC52973

[1]     《SEC  1:Elliptic  Curve      Cryptography,Version      2.0》：

http://www.secg.org/sec1-v2.pdf
[2]    《SEC 2:Recommended Elliptic Curve Domain Parameteres,Version
2.0》：http://www.secg.org/sec2-v2.pdf

[3] https://tools.ietf.org/html/rfc4492










        405

## Page 406

10.6 ECDH密钥协商

  与第9章中DH密钥协商类似，可根据椭圆曲线离散对数问题实现
基于椭圆曲线的密钥协商算法，通常称为椭圆曲线Diffie-Helllman或
简称ECDH。本节将介绍ECDH密钥协商算法的具体工作方式。假想
场景中通信双方分别为Alice和Bob，密钥协商过程主要分为两个阶
段：共享椭圆曲线参数和密钥协商。ECDH密钥协商过程如图10-9所
示。










    图10-9 ECDH密钥协商过程










    406

## Page 407

10.6.1 ECDH共享参数

Alice和Bob在进行密钥交换之前，两者需要达成一些“共识”。进
行ECDH密钥协商之前，Alice和Bob必须选择相同的椭圆曲线方程、
大素数p和生成元G。

1）选择相同的大素数p；

2）选择椭圆曲线方程E：y2=x3+ax+b mod p；

3）选择相同的生成元G(Gx,Gy)。

在真实场景中，Alice和Bob将会使用secp256r1或secp384r1这些被
推荐的椭圆曲线。由于这些椭圆曲线已经被相关组织标准化，所以
Alice和Bob一旦确认在ECDH过程中使用secp256r1或secp384r1，那么
双方就可以很容易地确认大素数P、椭圆曲线方程和生成元。










407

## Page 408

10.6.2 密钥协商过程

在ECDH密钥协商阶段，Alice和Bob选择随机数作为私密参数，
这个随机数可理解为私钥；并通过椭圆曲线标量乘法得到公开参数，
这个公开参数可理解为公钥；双方通过交换得到的公开参数和自身私
密参数计算出会话密钥。具体过程如下：

1）Alice选择一个比椭圆曲线的阶小的随机数dA作为私密参数，
该私密参数可理解为Alice的私钥，计算QA=dAG=(xA,yA)，并把QA发
送给Bob；

2）Bob选择一个比椭圆曲线的阶小的随机数QB作为私密参数，
该私密参数可理解为Bob的私钥，计算QB=dBG=(xB,yB)，并把QB送给
Alice；

3）Bob收到QA后计算得到共享密钥KB=dBQA=dB(dAG)；

4）Alice收到QB并计算得到共享密钥KA=dAQB=dA(dBG)。

由于椭圆曲线群符合群的结合律，也就是说dB(dAG)=dA(dBG)=
(xQ,yQ)，所以Alice和Bob将获得相同的共享密钥KA=KB。此时KA或
KB均为一个坐标点，共享密钥可以是xQ和yQ两部分，也可以是xQ单
一部分。若共享椭圆曲线为secp256r1，则xQ和yQ的长度均为256比特
（32字节）；若共享椭圆曲线方程为secp384r1，则xQ和yQ的长度均


408

## Page 409

为384比特（48字节）。










409

## Page 410

10.6.3 动手实践

下面通过一个具体示例来说明ECDH密钥协商的过程。由于椭圆
曲线secp256r1或secp384r1参数均非常复杂，所以此处选择一个较为
简单的椭圆曲线方程说明问题。椭圆曲线方程如下：

y2=x3+2x+2 mod 11

生成元为G(1,4)，椭圆曲线群的阶为9，椭圆曲线群的所有元素
如表10-2所示。

1）Alice选择一个随机数dA=3作为私密参数，计算QA=3G=
(9,10)，并把QA发送给Bob；

2）Bob选择一个随机数dB=5作为私密参数，计算QB=5G=(5,7)，
并把QB发送给Alice；

3）Bob收到QA，并计算得到共享密钥KB=5QA=5(9,10)=(9,1)；

4）Alice收到QB，并计算得到共享密钥KA=3QB=3(5,7)=(9,1)。

经过ECDH密钥协商，Alice和Bob获得了相同的共享密钥(9,1)。
本示例中共享密钥包括X坐标和Y坐标两部分，实际应用中共享密钥
也可以只取X坐标部分，通过这个共享密钥可派生出会话密钥。需要
注意的是，ECDH并不能解决认证问题，也就是说Alice无法确认获得


410

## Page 411

的公钥是否来自Bob。椭圆曲线除了应用于密钥协商之外，还可以应
用于数字签名。










411

## Page 412

10.7 mbedtls椭圆曲线模块

mbedtls提供了椭圆曲线算法，包括椭圆曲线基础运算、椭圆曲
线定义、椭圆曲线密钥协商算法和椭圆曲线数字签名算法。椭圆曲线
相关实现如表10-4所示。

    表10-4    mbedtls椭圆曲线相关实现










由于嵌入式运行环境的各种限制，mbedtls并不能也没有必要完
整地支持RFC449中规定的所有椭圆曲线，mbedtls所支持的椭圆曲线
可通过MBEDTLS    _{椭圆曲线名称}_ENABLE宏定义使能或
_ECP_DP
关闭。这些宏定义如下：




#define MBEDTLS_ECP_DP_SECP192R1_ENABLED
#define MBEDTLS_ECP_DP_SECP224R1_ENABLED
#define MBEDTLS_ECP_DP_SECP256R1_ENABLED
#define MBEDTLS_ECP_DP_SECP384R1_ENABLED
#define MBEDTLS_ECP_DP_SECP521R1_ENABLED
#define MBEDTLS_ECP_DP_SECP192K1_ENABLED
#define MBEDTLS_ECP_DP_SECP224K1_ENABLED
#define MBEDTLS_ECP_DP_SECP256K1_ENABLED
#define MBEDTLS_ECP_DP_BP256R1_ENABLED
#define MBEDTLS_ECP_DP_BP384R1_ENABLED
#define MBEDTLS_ECP_DP_BP512R1_ENABLED
#define MBEDTLS_ECP_DP_CURVE25519_ENABLED


412

## Page 413

#define MBEDTLS_ECP_DP_CURVE448_ENABLED



在ecp_curves.c中包含各种椭圆曲线的定义，例如secp256r1（代
码清单10-1）和secp384r1（代码清单10-2）。

代码清单10-1 椭圆曲线secp256r1



/*
* Domain parameters for secp256r1
*/
#if defined(MBEDTLS_ECP_DP_SECP256R1_ENABLED)
static const mbedtls_mpi_uint secp256r1_p[] = {
  BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
  BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00 ),
  BYTES_TO_T_UINT_8( 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ),
  BYTES_TO_T_UINT_8( 0x01, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF ),
};
static const mbedtls_mpi_uint secp256r1_b[] = {
  BYTES_TO_T_UINT_8( 0x4B, 0x60, 0xD2, 0x27, 0x3E, 0x3C, 0xCE, 0x3B ),
  BYTES_TO_T_UINT_8( 0xF6, 0xB0, 0x53, 0xCC, 0xB0, 0x06, 0x1D, 0x65 ),
  BYTES_TO_T_UINT_8( 0xBC, 0x86, 0x98, 0x76, 0x55, 0xBD, 0xEB, 0xB3 ),
  BYTES_TO_T_UINT_8( 0xE7, 0x93, 0x3A, 0xAA, 0xD8, 0x35, 0xC6, 0x5A ),
};
static const mbedtls_mpi_uint secp256r1_gx[] = {
  BYTES_TO_T_UINT_8( 0x96, 0xC2, 0x98, 0xD8, 0x45, 0x39, 0xA1, 0xF4 ),
  BYTES_TO_T_UINT_8( 0xA0, 0x33, 0xEB, 0x2D, 0x81, 0x7D, 0x03, 0x77 ),
  BYTES_TO_T_UINT_8( 0xF2, 0x40, 0xA4, 0x63, 0xE5, 0xE6, 0xBC, 0xF8 ),
  BYTES_TO_T_UINT_8( 0x47, 0x42, 0x2C, 0xE1, 0xF2, 0xD1, 0x17, 0x6B ),
};
static const mbedtls_mpi_uint secp256r1_gy[] = {
  BYTES_TO_T_UINT_8( 0xF5, 0x51, 0xBF, 0x37, 0x68, 0x40, 0xB6, 0xCB ),
  BYTES_TO_T_UINT_8( 0xCE, 0x5E, 0x31, 0x6B, 0x57, 0x33, 0xCE, 0x2B ),
  BYTES_TO_T_UINT_8( 0x16, 0x9E, 0x0F, 0x7C, 0x4A, 0xEB, 0xE7, 0x8E ),
  BYTES_TO_T_UINT_8( 0x9B, 0x7F, 0x1A, 0xFE, 0xE2, 0x42, 0xE3, 0x4F ),
};
static const mbedtls_mpi_uint secp256r1_n[] = {
  BYTES_TO_T_UINT_8( 0x51, 0x25, 0x63, 0xFC, 0xC2, 0xCA, 0xB9, 0xF3 ),
  BYTES_TO_T_UINT_8( 0x84, 0x9E, 0x17, 0xA7, 0xAD, 0xFA, 0xE6, 0xBC ),
  BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
  BYTES_TO_T_UINT_8( 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF ),
};
#endif /* MBEDTLS_ECP_DP_SECP256R1_ENABLED */



代码清单10-2 椭圆曲线secp384r1



/*
* Domain parameters for secp384r1
*/
#if defined(MBEDTLS_ECP_DP_SECP384R1_ENABLED)
static const mbedtls_mpi_uint secp384r1_p[] = {
  BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00 ),
  BYTES_TO_T_UINT_8( 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF ),


  413

## Page 414

    BYTES_TO_T_UINT_8( 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
    BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
    BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
    BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
};
static const mbedtls_mpi_uint secp384r1_b[] = {
    BYTES_TO_T_UINT_8( 0xEF, 0x2A, 0xEC, 0xD3, 0xED, 0xC8, 0x85, 0x2A ),
    BYTES_TO_T_UINT_8( 0x9D, 0xD1, 0x2E, 0x8A, 0x8D, 0x39, 0x56, 0xC6 ),
    BYTES_TO_T_UINT_8( 0x5A, 0x87, 0x13, 0x50, 0x8F, 0x08, 0x14, 0x03 ),
    BYTES_TO_T_UINT_8( 0x12, 0x41, 0x81, 0xFE, 0x6E, 0x9C, 0x1D, 0x18 ),
    BYTES_TO_T_UINT_8( 0x19, 0x2D, 0xF8, 0xE3, 0x6B, 0x05, 0x8E, 0x98 ),
    BYTES_TO_T_UINT_8( 0xE4, 0xE7, 0x3E, 0xE2, 0xA7, 0x2F, 0x31, 0xB3 ),
};
static const mbedtls_mpi_uint secp384r1_gx[] = {
    BYTES_TO_T_UINT_8( 0xB7, 0x0A, 0x76, 0x72, 0x38, 0x5E, 0x54, 0x3A ),
    BYTES_TO_T_UINT_8( 0x6C, 0x29, 0x55, 0xBF, 0x5D, 0xF2, 0x02, 0x55 ),
    BYTES_TO_T_UINT_8( 0x38, 0x2A, 0x54, 0x82, 0xE0, 0x41, 0xF7, 0x59 ),
    BYTES_TO_T_UINT_8( 0x98, 0x9B, 0xA7, 0x8B, 0x62, 0x3B, 0x1D, 0x6E ),
    BYTES_TO_T_UINT_8( 0x74, 0xAD, 0x20, 0xF3, 0x1E, 0xC7, 0xB1, 0x8E ),
    BYTES_TO_T_UINT_8( 0x37, 0x05, 0x8B, 0xBE, 0x22, 0xCA, 0x87, 0xAA ),
};
static const mbedtls_mpi_uint secp384r1_gy[] = {
    BYTES_TO_T_UINT_8( 0x5F, 0x0E, 0xEA, 0x90, 0x7C, 0x1D, 0x43, 0x7A ),
    BYTES_TO_T_UINT_8( 0x9D, 0x81, 0x7E, 0x1D, 0xCE, 0xB1, 0x60, 0x0A ),
    BYTES_TO_T_UINT_8( 0xC0, 0xB8, 0xF0, 0xB5, 0x13, 0x31, 0xDA, 0xE9 ),
    BYTES_TO_T_UINT_8( 0x7C, 0x14, 0x9A, 0x28, 0xBD, 0x1D, 0xF4, 0xF8 ),
    BYTES_TO_T_UINT_8( 0x29, 0xDC, 0x92, 0x92, 0xBF, 0x98, 0x9E, 0x5D ),
    BYTES_TO_T_UINT_8( 0x6F, 0x2C, 0x26, 0x96, 0x4A, 0xDE, 0x17, 0x36 ),
};
static const mbedtls_mpi_uint secp384r1_n[] = {
    BYTES_TO_T_UINT_8( 0x73, 0x29, 0xC5, 0xCC, 0x6A, 0x19, 0xEC, 0xEC ),
    BYTES_TO_T_UINT_8( 0x7A, 0xA7, 0xB0, 0x48, 0xB2, 0x0D, 0x1A, 0x58 ),
    BYTES_TO_T_UINT_8( 0xDF, 0x2D, 0x37, 0xF4, 0x81, 0x4D, 0x63, 0xC7 ),
    BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
    BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
    BYTES_TO_T_UINT_8( 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ),
};
#endif /* MBEDTLS_ECP_DP_SECP384R1_ENABLED */



      在代码清单10-1和代码清单10-2中，大素数p、椭圆曲线参数a与
b、生成元坐标Gx与Gy、椭圆曲线的阶均使用小端格式，所以数值出
现的顺序与10.5.1节和10.5.2节并不相同，但是数值大小完全相同。










    414

## Page 415

10.8 mbedtls ECDH示例

  本节基础示例模拟客户端和服务器进行ECDH密钥协商，模拟的
客户端和服务器并没有发生网络通信，而在程序中通过共享内存的方
式交换公开参数。示例代码参考自mbedtls示例代码，在mbedtls示例
代码的基础上增加或修改了部分内容。本节示例均基于Zephyr系统构
建，借助Zephyr系统良好的适配性，本节示例不但可运行于Linux平
台，也可运行于STM32F429等硬件平台。为了正确运行示例代码，
需要在mbedtls_config.h配置文件中增加相关宏定义。宏定义描述如表
10-5所示。

      表10-5 mbedtls_config.h配置文件宏定义描述










  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本节示例位于11_ecdh文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。


    415

## Page 416

    10.8.1 示例代码


      示例代码可以分为配置随机数、生成公开参数、生成共享密钥和
比对共享密钥几个部分，示例代码中qA、qB为公钥，dA、dB为私
钥，zA、zB为共享密钥。选用secp256r1作为曲线来生成公开参数，
生成公开参数后，通过对方的公开参数和自己的私钥完成共享密钥的
计算，最后比对共享密钥是否一致。ECDH密钥协商示例代码如代码
清单10-3所示，示例代码相关接口描述如表10-6所示。

      代码清单10-3 ECDH密钥协商示例



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/ecdh.h"
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/platform.h"
    // 省略部分中间代码
    int main(void)
    {
     size_t olen;
     char buf[65];
     mbedtls_ecp_group grp;
     mbedtls_mpi cli_secret, srv_secret;
     mbedtls_mpi cli_pri, srv_pri;
     mbedtls_ecp_point cli_pub, srv_pub;
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     uint8_t *pers = "simple_ecdh";
     mbedtls_platform_set_printf(printf);
     mbedtls_mpi_init(&cli_pri);
     mbedtls_mpi_init(&srv_pri);
     mbedtls_mpi_init(&cli_secret);
     mbedtls_mpi_init(&srv_secret);
     mbedtls_ecp_group_init(&grp);
     mbedtls_ecp_point_init(&cli_pub);
     mbedtls_ecp_point_init(&srv_pub);
     mbedtls_entropy_init(&entropy);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
         MBEDTLS_ENTROPY_MAX_GATHER, MBEDTLS_ENTROPY_SOURCE_STRONG);
     mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                               (const uint8_t *) pers, strlen(pers));
     mbedtls_printf("\n . setup rng  ... ok\n");

         416

## Page 417

    mbedtls_ecp_group_load(&grp, MBEDTLS_ECP_DP_SECP256R1);
    mbedtls_printf("\n . select ecp group SECP256R1 ... ok\n");
    mbedtls_ecdh_gen_public(&grp, &cli_pri, &cli_pub,
        mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_ecp_point_write_binary(&grp, &cli_pub,
        MBEDTLS_ECP_PF_UNCOMPRESSED, &olen, buf, sizeof(buf));
    dump_buf(" 1. ecdh client generate public parameter:", buf, olen);
    mbedtls_ecdh_gen_public(&grp, &srv_pri, &srv_pub,
        mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_ecp_point_write_binary(&grp, &srv_pub,
        MBEDTLS_ECP_PF_UNCOMPRESSED, &olen, buf, sizeof(buf));
    dump_buf(" 2. ecdh server generate public parameter:", buf, olen);
    mbedtls_ecdh_compute_shared(&grp, &cli_secret, &srv_pub, &cli_pri,
        mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_mpi_write_binary(&cli_secret, buf, mbedtls_mpi_size(&cli_secret));
    dump_buf(" 3. ecdh client generate secret:",
        buf, mbedtls_mpi_size(&cli_secret));
    mbedtls_ecdh_compute_shared(&grp, &srv_secret, &cli_pub, &srv_pri,
        mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_mpi_write_binary(&srv_secret, buf, mbedtls_mpi_size(&srv_secret));
    dump_buf(" 4. ecdh server generate secret:",
        buf, mbedtls_mpi_size(&srv_secret));
    mbedtls_mpi_cmp_mpi(&cli_secret, &srv_secret);
    mbedtls_printf(" 5. ecdh checking secrets ... ok\n");
    mbedtls_mpi_free(&cli_pri);
    mbedtls_mpi_free(&srv_pri);
    mbedtls_mpi_free(&cli_secret);
    mbedtls_mpi_free(&srv_secret);
    mbedtls_ecp_group_free(&grp);
    mbedtls_ecp_point_free(&cli_pub);
    mbedtls_ecp_point_free(&srv_pub);
    mbedtls_entropy_free(&entropy);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    return 0;
}



    表10-6 ECDH密钥协商相关接口描述










    417

## Page 418

10.8.2 代码说明

ECDH密钥协商示例简图如图10-10所示。










418

## Page 419

图10-10 ECDH密钥协商示例简图


419

## Page 420

    1.配置随机数

    ECDH生成公开参数以及计算共享密钥过程中需要使用伪随机数
    接口，首先需要完成随机数的配置工作，该过程包括熵源接口添加、
    熵源属性设置及通过个性化字符串更新种子。伪随机数生成器配置过
    程的详细描述可回顾7.6.2节。

    2.选择椭圆曲线参数

    首先需要通过mbedtls_ecp_group_load接口选择曲线参数，使用
    时需要输入椭圆曲线结构体以及椭圆曲线id。示例选择椭圆曲线
    secp256r1，mbedtls中椭圆曲线参数定义在mbedtls/library/ecp_curves.c
    文件中。

    3.生成公开参数

   有了椭圆曲线参数后，可以生成公开参数。生成公开参数的接口
为mbedtls_ecdh_gen_public，该接口需要输入椭圆曲线结构体、随机
数接口以及随机数结构体，输出得到私密参数d和公开参数Q。
mbedtls_ecdh_gen_public接口原型如下：

    int mbedtls_ecdh_gen_public( mbedtls_ecp_group *grp,
                  mbedtls_mpi *d, mbedtls_ecp_point *Q,
              int (*f_rng)(void *, unsigned char *, size_t),
              void *p_rng );

    4.生成共享密钥


              420

## Page 421

    通过上面的过程已经具备生成共享密钥的条件，生成共享密钥接
口为mbedtls_ecdh_compute_shared，该接口需要输入椭圆曲线结构
体、对方的公开参数、自身私密参数、伪随机数接口及伪随机数结构
体。输出为共享密钥，共享密钥仅包含X坐标。
mbedtls_ecdh_compute_shared接口原型如下：


int mbedtls_ecdh_compute_shared( mbedtls_ecp_group *grp, mbedtls_mpi *z,
    const mbedtls_ecp_point *Q, const mbedtls_mpi *d,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng );










    421

## Page 422

10.8.3 编译与执行

      本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



    本示例共消耗约43KB FLASH空间和约15KB RAM空间。编译与
    运行过程如下：




    # 进入示例代码文件夹
    $ cd 10_ecdh
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region      Used Size Region Size %age Used
             FLASH:        42940 B      2 MB     2.05%
               CCM:    0 GB           64 KB     0.00%
              SRAM:        15676 B    256 KB     5.98%
          IDT_LIST:          200 B      2 KB     9.77%
    $ make flash
    . setup rng    ... ok
    . select ecp group SECP256R1 ...  ok
    1. ecdh client generate public parameter:
    04 18 66 03 B8 81 CE 88 FA AE 11 D3 FC 05 40 63
    24 36 F7 3A 98 98 72 E9 17 53 2C 3B BD CC E1 60
    2A 2B 1C 23 FE F4 23 66 EE F4 B0 E1 9C FF 95 DD
    3A 52 84 6F 97 B5 01 63 AA CC 4B 7E 10 B4 8D 85
    60
    2. ecdh server generate public parameter:
    04 68 9B 3C 78 7C D6 99 04 66 F0 44 C1 AC 23 AE
    37 A8 1E 89 5A 34 A7 9C 78 8F F3 D3 23 B0 0F DE
    53 24 77 9A 57 DF 57 CC 18 E4 67 7E 2D 99 67 B1
    09 91 90 28 9D 84 DB DC C5 BE A1 13 12 C4 FB 92
    50



    422

## Page 423

3. ecdh client generate secret:
D1 C9 8F 94 53 AD 3A 1E 46 AE FD BC 7E BA 21 57
42 B5 58 A0 34 50 82 E9 C7 08 B6 1F 29 9F DB BF
4. ecdh server generate secret:
D1 C9 8F 94 53 AD 3A 1E 46 AE FD BC 7E BA 21 57
42 B5 58 A0 34 50 82 E9 C7 08 B6 1F 29 9F DB BF
5. ecdh checking secrets ... ok




从示例代码的输出可以看出：

1）模拟服务器和客户端均生成了不同的椭圆曲线公钥；

2）模拟服务器和客户端的椭圆曲线公钥均采用非压缩模式，从
控制台的输出可以看出，两者的公钥均以“04”开头，而“04”表示非压
缩模式；

3）双方采用的椭圆曲线同为secp256r1，所以生成的椭圆曲线公
钥长度同为65字节，该65字节包括1字节压缩提示，32字节X坐标和
32字节Y坐标；

4）最终双方获得完全相同的共享密钥，共享密钥仅包括X坐标
点，所以长度为32字节。










423

## Page 424

10.9 本章小结

             本章介绍了实数域和有限域上的椭圆曲线方程。在密码系统中，
实数域中的椭圆曲线方程并没有太多的实际作用，而有限域上的椭圆
曲线方程可获得有限集合。椭圆曲线群除了包含所有该椭圆曲线上的
离散点之外，还包括一个特殊的无穷远点，该无穷远点相当于普通运
算中的“零点”。椭圆曲线的阶等同于群内元素的个数，也就是所有离
散点加上无穷远点。本章介绍了两种群加法操作：相同点加法和不同
点加法，椭圆曲线中的群加法操作并不是简单的坐标点相加。在实际
应用中推荐使用椭圆曲线secp256r1和secp384r1。进行ECDH密钥协商
之前，密钥交换双方必须使用相同的椭圆曲线方程、大素数P和生成
元G。在ECDH交换过程中各自生成的随机数作为私钥，而椭圆曲线
标量乘法获得的结果dG作为公钥，经过密钥协商之后双方将获得相
同的会话密钥。










424

## Page 425

   第11章 数字签名RSA、DSA和ECDSA

11.1 本章主要内容

  数字签名可以识别消息是否被篡改，并验证消息的可靠性，也可
以防止否认。它与消息认证码的最大不同在于，数字签名算法可以防
止否认，因为私钥只有签名者持有，而消息认证码中的密钥由双方共
享。本章理论知识部分将介绍3种数字签名方法——RSA、DSA和
ECDSA，mbedtls部分将介绍3个与RSA数字签名有关的工具——
rsa_genkey、rsa_sign和rsa_verify。mbedtls实现了多种数字签名算
法，本章示例部分将重点介绍RSA数字签名和ECDSA数字签名。










    425

## Page 426

11.2 数字签名原理

  数字签名类似于现实世界中的盖章和签字，它具有以下四大特
征：

  ·可验证性——接收者可以验证发送者签名的真实性和有效性；

  ·不可伪造性——除签名者之外，任何人不可伪造签名；

  ·不可否认性——发送方不能否认自己所发送的签名；

  ·数据完整性——能够提供对所签消息的完整性检验。

  这里先通过一个示例介绍数字签名的应用场景。假想场景中
Alice为买家，Bob为商家，Alice需要从商家预订一台笔记本电脑，为
了防止Alice发送的合同被其他人篡改，也为了防止Alice否认预订合
同，Alice需要使用某种数字签名算法对合同进行签名。具体过程如
图11-1所示。










  426

## Page 427

图11-1 数字签名应用场景

1）Alice通过密钥生成算法生成密钥对；

2）Alice将公钥发送给Bob，私钥自己保留；

3）Alice使用单向数列函数计算出合同的摘要值；

4）Alice使用私钥对消息摘要值进行签名；

5）Alice将合同和签名值分别发送至Bob；

6）Bob使用单向散列函数计算出合同的消息摘要值；

    427

## Page 428

  7）Bob使用Alice的公钥对签名进行验证，若验证通过则说明合
同内容完整且来自于Alice。

  从本应用场景中可以看出，虽然数字签名的工作模式与消息认证
码较为相似，但不同的是数字签名可防止否认。消息认证码使用的密
钥为对称密钥，如果基于消息认证码完成消息的认证过程，一旦
Alice否认曾经向Bob发送过预订合同，那么Bob将无法对Alice进行指
控。而数字签名算法中私钥只有Alice持有，其他人无法对签名进行
伪造，这一特点也使得Alice无法对这一过程进行否认。

  市面上有多种数字签名实现算法，本章将介绍RSA数字签名算
法、DSA算法和ECDSA算法。










    428

## Page 429

11.3 RSA数字签名

RSA数字签名算法基于RSA密钥系统实现，在第8章中已经详细
介绍了RSA算法。RSA数字签名过程与RSA加解密过程较为相似，但
公钥和私钥的使用方法却存在明显区别。

为了方便描述RSA数字签名过程，此处依然借助假想场景加以说
明，在假想场景中：

1）Alice通过RSA密钥生成算法生成密钥对；

2）Alice将公钥发送给Bob，私钥自己保留；

3）Alice使用RSA私钥对消息进行加密操作，并将消息和签名结
果分别发送给Bob；

4）Bob使用RSA公钥对签名进行解密操作，判断解密结果和消
息是否一致。

此处Alice使用私钥对消息执行加密操作，该加密操作可理解为
对消息进行数字签名，该私钥可称为签名密钥；Bob收到消息之后使
用Alice的公钥执行解密操作，该解密操作可理解为对消息执行数字
签名验证，该公钥可称为验证密钥。总之，在RSA数字签名中，私钥
用于加密消息，公钥用于解密消息；而在RSA加密中，公钥用于加密
消息，而私钥用于解密消息。无论如何，公钥总是可以公开的，而私


429

## Page 430

钥却不能泄露。










430

## Page 431

    11.3.1 RSA数字签名详细说明

    1.RSA密钥对生成

      密钥对的生成过程与第8章RSA加解密算法中所描述的过程完全
    一致，此处不重复描述。通过密钥对生成算法得到的参数如表11-1所
    示。

        表11-1 RSA密钥参数说明










2.RSA签名

  RSA数字签名和RSA加密过程恰好相反，签名过程使用私钥对数
据执行加密操作，RSA数字签名表达式如下，其中s为签名结果，m
为消息（消息可以是明文也可以是消息摘要）。



    431

## Page 432

s≡mdmod n

3.RSA验证签名

同样，验证签名过程使用公钥对签名数据进行解密，RSA验证签
名表达式如下，其中s为签名结果，m'为解密结果。验证签名过程判
断m'≡mmod n，成立则为有效签名，不成立则签名无效。

m'≡semod n

通过第8章的学习可以发现，由于参数e的值远小于参数d，所以
RSA验证签名的计算量小于RSA签名，也就说RSA验证签名速度快于
签名速度。










432

## Page 433

11.3.2 RSA数字签名动手实践

此处假定：公钥（n,e）=（33,3）、私钥（n,d）=（33,7），消息
m=7；

1）Alice使用私钥加密消息。

Alice使用私钥（33,7）对消息进行签名，签名结果为s=28。计算
过程如下：

s≡mdmodn→s≡77≡823543≡28mod33→s=28

2）Bob使用公钥对签名进行验证。

Bob使用公钥（33,3）对签名进行验证，验证结果m'=7，因此签
名有效。计算过程如下：

m'≡s   emodn→m'≡283≡21952≡7mod33→m'=7










433

## Page 434

    11.3.3 RSA签名填充方法

         在实际应用中，RSA签名算法通常还需包含填充方法。RSA填充
    方法非常重要，它的好坏将直接影响RSA签名的安全性。与RSA加解
    密部分类似，RSA数字签名算法也包括两种填充方案：PKCS1-v1_5
    和PSS。

    1.PKCS1-v1_5

      与RSA加密过程中的填充方法类似，PKCS1-v1_5填充过程各字
    段如图11-2所示。










        图11-2 PKCS1-v1_5填充字段描述

   填充字段中有3字节的固定长度，包括2字节0x00，用于指示填充
开始和结束，1字节0x01用于指示算法类型。假设消息长度为mlen，


    434

## Page 435

模数n长度为K，则PS字段长度为K-3-mlen，最小长度为8字节。签名
操作中需要使用固定字节0xff完成PS字段的填充，字段T中包含消息
摘要算法信息和消息摘要值，使用DER格式进行编码。需要注意的
是，消息长度mlen的最大长度为K-11，需要预留至少11字节用于填
充。

2.PSS

  新版本PKCS#1标准中推荐使用PSS填充方法，填充过程中将会
引入随机字符串，相比PKCS1-v1_5填充方法，该填充方法更加安
全。PSS填充过程涉及的参数如表11-2所示。

    表11-2 PSS填充过程参数说明







具体过程如下：

1）生成随机字符串salt，长度为slen；

2）计算MHash=Hash（M），长度为hlen；

3）计算emlen=emBits/8（向上取整），填充后消息长度需要满
足条件：emlen<hlen+slen+2；



435

## Page 436

4）将8个0、MHash和salt拼接为M'，该过程的表达式如下：

M' = （0x）00 00 00 00 00 00 00 00 || MHash || salt;

5）计算H=Hash（M'），长度为hlen；

6）生成固定字符串PS，由emlen-slen-hlen-2个0组成；

7）将PS、一个固定字节0x01和salt拼接在一起形成数据块DB，
其长度为emlen-hlen-1，该过程的表达式为：

DB = PS || 0x01 || salt

8）计算dbMask=MGF（H,emLen-hLen-1）；

9）计算maskedDB=DB xor dbMask；

10）将maskedDB最左8emLen-emBits位设为0；

11）将maskedDB、H和一个固定字节0xbc拼接在一起，构成填
充后的字符串EM，具体表达式如下：

EM = maskedDB || H || 0xbc










436

## Page 437

11.4 DSA数字签名

  DSA算法是数字签名标准规范DSS（Digital Signature Standard）
的一部分，该规范由美国国家标准与技术研究所制定并发布。DSS最
初于1991年提出，最新版为FIPS PUB 186-4，于2013年发布。与RSA
算法不同，DSA算法只能提供数字签名功能，而不能用于加密或密钥
交换。










    437

## Page 438

11.4.1 DSA数字签名详细说明

1.DSA密钥对生成

DSA密钥对的生成过程如下：

1）生成一个大素数p，满足条件2L-1<p<2L；

2）找到p-1的一个素除数q，满足条件2N-1<q<2N；

3）在循环群GF(p)中，找到子群的生成元g，使得ord(g)=q，即阶
为q；

4）选择一个随机数x，满足条件0<x<q；

5）计算y≡gxmod p；

6）得到私钥(x)，公钥(p,q,g,y)。

DSA密钥对生成过程中素数p的位长度为L，而素数q的位长度为
N位。DSS规范中指定了L、N与签名长度的关系，它们之间的对应关
系如表11-3所示。

表11-3  DSS规范中L、N和签名长度的对应关系（单位：比特）






438

## Page 439

当L为1024比特、N为160比特时，素数p为1024比特，素数q为
160比特，在这种情况下，签名结果的长度为320比特。

2.DSA签名

DSA签名结果包括两部分，r和s。签名过程中需使用单向散列函
数，单向散列函数表示为HASH()。假设消息为M，N为160比特时签
名结果的长度为320比特。DSA签名过程如下：

1）选择一个随机数k，满足条件0<k<q；

2）计算r≡(gkmod p)mod q；

3）计算z=HASH(M)；

4）计算s≡(k-1(z+xr))mod q；

5）得到签名(r,s)。

3.DSA验证签名

DSA验证签名过程需要使用签名者的公钥，公钥可通过可信机构
（如CA）或面对面的方式获得，在实际应用中通常会使用数字证书
作为公钥传递手段。关于数字证书会在第12章进行详细描述。验证签

    439

## Page 440

名之前需要检查签名者公钥、消息以及签名信息(r,s)。DSA验证签名
过程如下：

1）检测签名(r,s)的合法性，即0<r<q,0<s<q，满足条件则继续进
行，否则验证失败；

2）计算w≡s-1mod q；

3）计算z=HASH(M)；

4）u1=(zw)mod q；

5）u2≡(rw)mod q；

6）v≡((gu1yu2)mod p)mod q；

7）若v≡r mod p，则签名验证通过，否则签名验证失败。










440

## Page 441

11.4.2 DSA签名动手实践

  下面通过一个具体示例说明DSA算法的计算过程。示例中Alice
发送消息M给Bob，消息通过DSA算法进行签名，假设M的消息摘要
值为HASH（M）=13，Alice通过DSA密钥生成方法计算得到公钥和
私钥，并将公钥发送给Bob，私钥由Alice自己保管。示例中选择大素
数p=23，q=11，子群生成元g=4。循环子群如表11-4所示。

        表11-4 循环子群








    Alice生成密钥对的过程如下：

    1）选择素数p=23；

    2）选择q=11；

    3）选择生成元g=4；

    4）选择随机数x=5；

    5）计算y≡45≡12mod 59→y=12；



    441

## Page 442

6）公钥为（p,q,g,y）（23,11,4,12），私钥为（x）（5）。

Alice使用私钥对消息M执行DSA签名计算，得到签名结果，并将
签名结果和消息一起发送给Bob。DSA签名的具体过程如下：

1）选择随机数k=7；

2）计算r≡(gkmod p)mod q→r≡(47 mod 23)mod 11→r=8；

3）计算z=HASH(M)=13；

4）计算s≡(k-1(z+xr))mod q→s≡(7-1(13+5·8))mod 11→s=6；

5）得到签名(r,s)(8,6)。

Bob收到消息和签名结果后，使用Alice的公钥对消息签名进行验
证。DSA验证签名的具体过程如下：

1）检测签名(r,s)的合法性，0<8<p,0<6<q；

2）计算w≡s-1mod q→w≡6-1mod 11→w=2；

3）计算z=HASH(M)=13；

4）u1≡(zw)mod q→u1≡(13·2)mod 11→u1=4；

5）u2≡(rw)mod q→u2≡(8·2)mod 11→u2=5；

6）v≡((gu1yu2))mod p)mod q→v≡((44·125))mod 23)mod 11→v=8；


442

## Page 443

7）v≡r mod p→8≡8 mod 23，签名有效。










443

## Page 444

11.5 ECDSA数字签名

  ECDSA算法基于椭圆曲线离散对数问题，使用较短的密钥长度
便可提供与RSA签名算法或DSA算法等同的安全等级，密钥长度为
160~256位的椭圆曲线算法与密钥长度为1024~3072位的非椭圆曲线算
法安全性相同。椭圆曲线的基础知识可以回顾第10章的内容。
ECDSA数字签名算法和DSA算法在概念上有紧密联系，但其计算过
程是在椭圆曲线群上完成的，所以计算过程相差较大。ECDSA算法
与DSA算法相似，该算法只能提供数字签名功能，而不能用于加密或
密钥交换。










    444

## Page 445

11.5.1 ECDSA数字签名详细说明

1.ECDSA生成密钥对

ECDSA密钥生成依赖于椭圆曲线参数，在软件实现中通常在现
有的椭圆曲线参数中进行选择，常用的椭圆曲线包括secp256r1、
secp384r1等。椭圆曲线参数包括{p,a,b,G,n,h}，下面再来回顾一下椭
圆曲线参数的具体描述，如表11-5所示。

    表11-5   椭圆曲线参数说明








  ECDSA算法生成密钥的过程如下：

  1）选择椭圆曲线E：y2≡x3+ax+b mod p、生成元G和循环群的阶
n；

  2）选择一个随机数d，满足条件0<d<n；

  3）计算Q=d·G；

  4）得到私钥(d)，公钥(p,a,b,G,n,Q)。


  445

## Page 446

2.ECDSA生成签名

ECDSA的签名结果由两部分构成：r和s。其中r和s的长度与n相
同，例如在secp256r1曲线中，n的长度为256比特，r和s也分别为256
比特，不使用任何编码方式的情况下签名总长度为512比特。假设消
息为M，单向散列函数为HASH()。使用ECDSA对消息进行签名的计
算过程如下：

1）选择一个随机数k，满足条件0<k<n；

2）计算R=k·G；

3）计算z=HASH(M)；

4）设置r=xR，xR为点R的横坐标；

5）计算s≡(z+d·r)k-1mod n；

6）得到签名(r,s)。

3.ECDSA验证签名

在验证签名之前需确保已经得到签名者的公钥、消息以及签名信
息(r,s)。验证签名的过程如下：

1）计算w≡s-1mod n；

2）计算z=HASH(M)；

    446

## Page 447

3）计算u1≡(wz)mod n；

4）计算u2≡(wr)mod n；

5）计算P=u1·g+u2·Q；

6）如果xP≡r mod n，则签名有效，否则签名无效，其中xP为点P
的横坐标。










447

## Page 448

11.5.2 ECDSA动手实践

下面通过一个具体示例完成ECDSA算法计算过程的描述。为了
便于计算，示例中选择了较小的椭圆曲线参数。示例中Alice发送消
息M给Bob，消息通过ECDSA算法进行签名，假设M的消息摘要值
HASH(M)=26。Alice通过ECDSA密钥对生成方法计算出公钥和私
钥，并将公钥发送给Bob，私钥由Alice自己保管。ECDSA生成密钥
对的具体过程如下：

1）选择椭圆曲线E：y2≡x3+2x+2 mod 17，生成元为G=(5,1)，循
环群的阶n=19。

当确定椭圆曲线方程和生成元之后，可先计算该椭圆曲线上的所
有点，具体坐标如表11-6所示。

    表11-6 椭圆曲线方程E上的所有点






2）选择一个随机数d=7；

3）计算Q=d·G=7·(5,1)=(0,6)；

4）得到私钥(7)，公钥(17，2，2，(5，1)，19，(0，6))。


448

## Page 449

Alice使用私钥对消息M进行ECDSA签名计算，得到签名结果，
并将签名结果和消息一起发送给Bob。ECDSA签名的具体过程如下：

1）选择一个随机数k=10；

2）计算R=k·G=10·(5,1)=(7,11)；

3）计算z=HASH(M)=26；

4）设置r=xR mod n→r=7；

5）计算s≡(z+dr)k-1mod n→s≡(26+7·7)10-1mod 19→s=17；

6）得到签名(7,17)。

Bob收到签名结果和消息后，使用得到的公钥对消息签名进行验
证。ECDSA验证签名的具体过程如下：

1）计算w≡s-1mod n→w≡17-1mod 19→w=9；

2）计算z=HASH(M)=26；

3）计算u1≡(wz)mod n→u1≡(9·26)mod 19→u1=6；

4）计算u2≡(wr)mod n→u2≡(9·7)mod 19→u2=6；

5）计算P=u1·g+u2·Q=6·(5,1)+6·(0,6)=(7,11)；

6）xP≡r mod n→7≡7 mod 19，签名有效。


449

## Page 450

11.6 mbedtls数字签名应用工具

   mbedtls为各个模块提供了应用工具，应用工具主要展示模块接
口使用方法。mbedtls数字签名算法模块提供了多个应用工具，本节
将主要介绍rsa_genkey、rsa_sign和rsa_verify的使用方法。下面通过一
个假想场景介绍应用工具的使用方法，假想场景中使用RSA算法生成
密钥对，使用私钥对“Hello,world!”生成签名，最后通过公钥对签名进
行验证。










    450

## Page 451

11.6.1 rsa_genkey

rsa_genkey可以用来生成rsa密钥对，默认生成2048比特长度的密
钥，公钥保存在rsa_pub.txt文件中，私钥保存在rsa_priv.txt文件中。具
体过程如下：


# 生成rsa密钥对
$ rsa_genkey
# 输出
. Seeding the random number generator... ok
. Generating the RSA key [ 2048-bit ]... ok
. Exporting the public key in rsa_pub.txt....  ok
. Exporting the private key in rsa_priv.txt... ok


rsa_genkey工具在第8章RSA算法中介绍过。rsa_gengkey工具生成
的密钥保存在rsa_pub.txt和rsa_priv.txt中。










451

## Page 452

    11.6.2 rsa_sign

        rsa_sign可以使用RSA私钥对消息进行签名，使用rsa_sign工具
    对“Hello,World!”字符串生成签名，签名结果默认保存在
        _world.txt.sig文件中。具体过程如下：
    hello



    # 生成消息
    $ echo -n "Hello, World!" > hello_world.txt
    $ hexdump -C hello.txt
    00000000 48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21 |Hello, World!|
    # 生成签名
    $ rsa_sign hello_world.txt
    # 输出
    . Reading private key from rsa_priv.txt
    . Checking the private key
    . Generating the RSA/SHA-256 signature
    . Done (created "hello_world.txt.sig")



      工具中默认为PKCS1v1_5填充方法，与RSA加密填充过程不同，
RSA签名不会使用随机数进行填充，所以使用相同的私钥进行签名，
每次的签名结果均相同。RSA-2048签名结果的长度为256字节。



    # 查看签名结果
    $ cat hello_world.txt.sig
    08 62 B1 4A 3B FC 7B 2B 41 6C A7 DB BD 13 D6 48
    D2 82 71 AB 7E C0 C6 42 62 60 8F 24 1A 16 0A 57
    73 58 D2 D4 1E 23 20 A0 A9 F7 82 0D 72 4C 9C 87
    20 D0 B9 D9 4C BD 30 EC 6D 8C FE B5 2C 08 39 3F
    34 23 C2 F3 6E 45 0E 1E 76 AD 7F 26 73 B0 F4 6C
    F0 B7 17 4C C3 DE 6B 6E 84 61 9B 45 0F 6B EB 80
    05 9D 2E B2 D2 C7 91 23 4E 53 5F 9E 99 8F 02 5B
    EF 7B 35 D0 A6 8B 20 A9 8E 4D DD E0 31 9F 7F 3A
    9B 57 0D EA CE B9 81 DD 4F 91 7E 59 66 99 E5 96
    F3 BB F9 99 9F 5A 77 6F C1 5D A4 EC B8 33 FE 73
    33 B8 07 6D 11 73 BE 9D 79 F4 EF 07 A2 83 18 73
    55 62 02 01 1E 6E 2C A6 92 EF 33 7D 32 A0 3D 24
    E4 E1 09 CE 5D F9 71 AA 22 35 BC 89 A1 AE BB 1C
    8D E7 24 F3 81 71 47 A7 C2 2D 30 EE E5 71 56 02
    5B D9 29 A9 FF BD 09 95 4D 95 40 C3 82 5C 25 2C
    34 A2 51 96 24 6B B8 E0 24 31 48 12 F6 38 43 96







    452

## Page 453

11.6.3 rsa_verify

    rsa_verify可以通过公钥对签名进行验证，使用rsa_verify工具对
hello_world.txt文件验证签名，验证过程中会自动根据输入文件名加
载hello_world.txt.sig签名结果。具体过程如下：


    # 验证签名
    $ rsa_verify hello_world.txt
    # 输出
    . Reading public key from rsa_pub.txt
    . Verifying the RSA/SHA-256 signature
    . OK (the signature is valid)










    453

## Page 454

11.7 mbedtls RSA签名示例

   本节基础示例将展示如何使用mbedtls RSA接口对消息计算签
名。示例代码参考自mbedtls示例代码，在mbedtls示例代码的基础上
增加或修改了部分内容。本节示例均基于Zephyr系统构建，借助
Zephyr系统良好的适配性，示例不但可运行于Linux平台，也可运行
于STM32F429等硬件平台。为了实现示例代码，需要在
mbedtls_config.h配置文件中增加相关宏定义，宏定义描述如表11-7所
示。

      表11-7 mbedtls_config.h配置文件的宏定义描述










   注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本节示例位于11_dsa/rsa_sign文件夹中。另
外，mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根
据实际情况修改。



    454

## Page 455

11.7.1 示例代码

      RSA生成密钥过程中需要使用随机数模块产生随机数，并对随机
数进行素性检测，因此可能会占用几分钟甚至更长的时间。生成密钥
对的过程中需要指定密钥长度（位表示）和公开指数，示例中选择较
为常用的短公开指数65537（0x01001），生成密钥后使用RSA签名接
口对消息进行签名操作，签名操作需指定单向散列函数。生成签名后
使用RSA签名验证接口对签名和消息进行验证。RSA数字签名示例如
代码清单11-1所示。

      代码清单11-1 RSA数字签名示例



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/rsa.h"
    #include "mbedtls/platform.h"
    // 省略部分内容
    int main(void)
    {
     uint8_t msg[100];
     uint8_t sig[2048/8];
     uint8_t *pers = "simple_rsa_sign";
     mbedtls_platform_set_printf(printf);
     mbedtls_platform_set_snprintf(snprintf);
     mbedtls_rsa_context ctx;
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     mbedtls_entropy_init(&entropy);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_rsa_init(&ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
         MBEDTLS_ENTROPY_MAX_GATHER, MBEDTLS_ENTROPY_SOURCE_STRONG);
     mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
         (const uint8_t *) pers, strlen(pers));
     mbedtls_printf("\n     . setup rng ... ok\n\n");
     mbedtls_printf(" ! RSA Generating large primes may take minutes! \n");
     mbedtls_rsa_gen_key(&ctx, mbedtls_ctr_drbg_random,
         &ctr_drbg, 2048, 65537);
     mbedtls_printf(" 1. rsa generate keypair ...    ok\n");
     dump_rsa_key(&ctx);


     455

## Page 456

 mbedtls_rsa_pkcs1_sign(&ctx, mbedtls_ctr_drbg_random, &ctr_drbg,
                                MBEDTLS_RSA_PRIVATE, MBEDTLS_MD_SHA256,
                                sizeof(msg), msg, sig);
 dump_buf(" 2. rsa generate signature:", sig, sizeof(sig));
 mbedtls_rsa_pkcs1_verify(&ctx, mbedtls_ctr_drbg_random, &ctr_drbg,
                                  MBEDTLS_RSA_PUBLIC, MBEDTLS_MD_SHA256,
                                  sizeof(msg), msg, sig);
 mbedtls_printf(" 3. rsa verify signature ... ok\n\n");
 mbedtls_rsa_free(&ctx);
 mbedtls_ctr_drbg_free(&ctr_drbg);
 mbedtls_entropy_free(&entropy);
 return 0;
}



示例代码相关接口描述如表11-8所示。

 表11-8 RSA数字签名示例相关接口描述










                                456

## Page 457

11.7.2 代码说明

RSA签名示例简图如图11-3所示。










图11-3 RSA签名示例简图

1.配置随机数



457

## Page 458

   由于RSA生成密钥对过程需要使用伪随机数接口，首先需要完成
伪随机数的配置工作，该过程包括熵源接口添加、熵源属性设置及通
过个性化字符串更新种子等步骤。伪随机数生成器配置过程的详细描
述可回顾7.6.2节。

2.RSA密钥初始化

   初始化时通过参数MBEDTLS_RSA_PKCS_V21指定填充方案为
PSS，需要指定单向散列函数算法ID，示例中将使用SHA256算法作
为单向散列算法。由于PSS填充方法将使用随机数对消息进行填充，
所以在签名过程中即使使用相同的密钥对明文进行签名，每次得到的
签名结果也不相同。

  mbedtls_rsa_init(&ctx, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);


    3.RSA生成密钥

   RSA生成密钥对接口为mbedtls_rsa_gen_key，该函数需要输入
RSA结构体、随机数生成接口、随机数结构体、模数的位长度以及公
开指数，密钥对会保存在RSA结构体中。示例中输入模数的位长度为
2048，公开指数为65537。mbedtls_rsa_gen_key接口原型如下：

    int mbedtls_rsa_gen_key( mbedtls_rsa_context *ctx,
             int (*f_rng)(void *, unsigned char *, size_t),
             void *p_rng,
             unsigned int nbits, int exponent );




             458

## Page 459

4.RSA生成签名

    RSA生成签名接口为mbedtls_rsa_pkcs1_sign，该函数需输入RSA
结构体、随机数生成接口、随机数结构体、密钥类型、单向散列函数
类型、消息摘要长度和消息摘要，输出得到签名结果。

    由于示例中使用PSS填充方法，填充时需要使用随机数进行填
充，接口中需要指定随机数生成接口和随机数结构体。输入参数中密
钥类型包括公钥（MBEDTLS_RSA_PUBLIC）和私钥
（MBEDTLS_RSA_PRIVATE）。示例中选择私钥进行签名操作，单
向散列函数为SHA256算法。mbedtls_rsa_pkcs1_sign结构体原型如
下：


    int mbedtls_rsa_pkcs1_sign( mbedtls_rsa_context *ctx,
    int (*f_rng)(void *, unsigned char *, size_t),
    void *p_rng,
    int mode,
    mbedtls_md_type_t md_alg,
    unsigned int hashlen,
    const unsigned char *hash,
    unsigned char *sig );


    5.RSA验证签名

    RSA验证签名接口为mbedtls_rsa_pkcs1_verify，该函数需要输入
RSA结构体、随机数生成接口、随机数结构体、密钥类型、单向散列
函数类型、消息摘要长度、消息摘要和签名。若返回值为0则表示验
证成功。mbedtls_rsa_pkcs1_verify接口原型如下：

    int mbedtls_rsa_pkcs1_verify( mbedtls_rsa_context *ctx,
        int (*f_rng)(void *, unsigned char *, size_t),

        459

## Page 460

void *p_rng,
int mode,
mbedtls_md_type_t md_alg,
unsigned int hashlen,
const unsigned char *hash,
const unsigned char *sig );










460

## Page 461

11.7.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     本示例中RSA签名长度为256字节，RSA签名示例与第8章RSA加
解密示例所消耗的RAM空间和Flash空间几乎相同。示例共消耗约
45KB Flash空间和约32KB RAM空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 11_dsa/rsa_sign
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region   Used Size Region Size %age Used
             FLASH:      45076 B      2 MB    2.15%
               CCM:       0 GB       64 KB    0.00%
              SRAM:      32060 B    256 KB   12.23%
          IDT_LIST:       200 B       2 KB    9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    . setup rng ...    ok
    ! RSA Generating large primes may take minutes!
    1. rsa generate keypair ...   ok
    +++++++++++++++++ rsa keypair +++++++++++++++++
    N: BF278713147331F0537D734303C518486F2B6DF1AE2859549D8FEFE986E469433E03ABACD4B641730924DEADD83ADC4B4678888208C207D80A65BF2327DCA10670E2E1
    E: 010001
    D: 5BBBA1E03FA79A770CF1FE8ED1EFD35BEB71A984DA4185C10C0E07A18778F4A4EECD3F25253D43826B88748E73DEA75A3E7AD873A2B54EA3583604B85FC84AC4370741
    // 省略部分输出
    +++++++++++++++++ rsa keypair +++++++++++++++++



                         461

## Page 462

2. rsa generate signature:
10 3D 54 69 EC 91 B0 13 3D 04 C2 6C CD 31 EE BF
F7 02 7C C7 18 B5 99 DA CF D6 38 D1 E7 D7 CB 4F
EA F1 EC A4 2F 64 5B 6B BA 2D B6 5C 09 DC 21 06
0A A2 85 DD 3E CB 03 B1 BC 5B 53 21 DD 73 FB 96
34 20 D0 C7 79 57 5A 9B BF 27 41 D3 74 20 61 16
4A A1 C7 07 89 5E E0 35 5D 7E 4A 31 41 7F CD 5F
B9 AD AB 64 B4 D7 59 0A 92 74 F3 A6 29 18 28 BD
80 90 50 83 31 72 64 80 27 E3 10 A8 EA 3F 58 AB
7F 3F BE 15 80 44 41 C0 D9 71 E0 C8 4B 32 8D 56
02 FA 6A E5 E7 06 AD 9B 31 6A BE 99 CC 5A 29 A8
E9 8E B2 F4 B6 B9 49 43 12 BF ED 03 1F C9 28 D4
4E 12 C6 2D 61 4F 4D DC 60 46 14 39 3A 3A BE C1
EF ED A8 A5 FD 36 8F 4A 95 30 E8 69 00 E5 02 15
C4 A0 AA 44 44 77 77 3F 3A A3 32 9D 55 5D DF 2A
BF 2D E3 73 DA 09 6C 5C 8E 8C 1B BF 8D 2D F3 6E
2E 97 2C D8 3D 77 80 D8 88 AE 11 1F B8 81 AE 80
3. rsa verify signature ... ok










462

## Page 463

11.8 mbedtls ECDSA示例

  本节基础示例将展示如何使用mbedtls ECDSA接口对消息计算签
名。示例代码参考自mbedtls示例代码，在mbedtls示例代码的基础上
增加或修改了部分内容。本节示例均基于Zephyr系统构建，借助
Zephyr系统良好的适配性，示例不但可运行于Linux平台，也可运行
于STM32F429等硬件平台。为了实现示例代码，需要在
mbedtls_config.h配置文件中增加相关宏定义，宏定义描述如表11-9所
示。

      表11-9 mbedtls_config.h配置文件宏定义描述










  注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详
见本书GitHub代码仓库。本节示例位于11_dsa/ecdsa文件夹中。另外
mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。


    463

## Page 464

    11.8.1 示例代码


      示例代码中首先完成随机数的配置工作，然后计算消息的消息摘
要。示例中使用SHA256作为单向散列函数，选择secp256r1作为椭圆
曲线参数生成密钥对，生成密钥对后通过ECDSA签名接口对消息摘
要进行签名，最后通过ECDSA验证签名接口对签名和消息摘要进行
验证。ECDSA示例代码如代码清单11-2所示，示例代码相关接口描
述如表11-10所示。

      代码清单11-2 ECDSA算法示例



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/entropy.h"
    #include "mbedtls/ctr_drbg.h"
    #include "mbedtls/md.h"
    #include "mbedtls/ecdsa.h"
    #include "mbedtls/platform.h"
    // 省略部分内容
    int main(void)
    {
     char buf[97];
     uint8_t hash[32], msg[100];
     uint8_t *pers = "simple_ecdsa";
     size_t rlen, slen, qlen, dlen;
     memset(msg, 0x12, sizeof(msg));
     mbedtls_platform_set_printf(printf);
     mbedtls_mpi r, s;
     mbedtls_ecdsa_context ctx;
     mbedtls_md_context_t md_ctx;
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     mbedtls_mpi_init(&r);
     mbedtls_mpi_init(&s);
     mbedtls_ecdsa_init(&ctx);
     mbedtls_entropy_init(&entropy);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
         MBEDTLS_ENTROPY_MAX_GATHER, MBEDTLS_ENTROPY_SOURCE_STRONG);
     mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
         (const uint8_t *) pers, strlen(pers));
     mbedtls_printf("\n  . setup rng ... ok\n\n");
     mbedtls_md_init(&md_ctx);
     mbedtls_md(mbedtls_md_info_from_type(MBEDTLS_MD_SHA256),


     464

## Page 465

        msg, sizeof(msg), hash);
    mbedtls_printf(" 1. hash msg ... ok\n");
    mbedtls_ecdsa_genkey(&ctx, MBEDTLS_ECP_DP_SECP256R1,
        mbedtls_ctr_drbg_random, &ctr_drbg);
    mbedtls_ecp_point_write_binary(&ctx.grp, &ctx.Q,
        MBEDTLS_ECP_PF_UNCOMPRESSED, &qlen, buf, sizeof(buf));
    dlen = mbedtls_mpi_size(&ctx.d);
    mbedtls_mpi_write_binary(&ctx.d, buf + qlen, dlen);
    dump_buf(" 2. ecdsa generate keypair:", buf, qlen + dlen);
    mbedtls_ecdsa_sign(&ctx.grp, &r, &s, &ctx.d,
        hash, sizeof(hash), mbedtls_ctr_drbg_random, &ctr_drbg);
    rlen = mbedtls_mpi_size(&r);
    slen = mbedtls_mpi_size(&s);
    mbedtls_mpi_write_binary(&r, buf, rlen);
    mbedtls_mpi_write_binary(&s, buf + rlen, slen);
    dump_buf(" 3. ecdsa generate signature:", buf, rlen + slen);
    mbedtls_ecdsa_verify(&ctx.grp, hash, sizeof(hash), &ctx.Q, &r, &s);
    mbedtls_printf(" 4. ecdsa verify signature ... ok\n\n");
    mbedtls_mpi_free(&r);
    mbedtls_mpi_free(&s);
    mbedtls_md_free(&md_ctx);
    mbedtls_ecdsa_free(&ctx);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    return 0;
}



    表11-10 ECDSA算法示例相关接口描述










    465

## Page 466

11.8.2 代码说明

ECDSA签名示例简图如图11-4所示。










    图11-4 ECDSA签名示例简图

1.配置随机数

ECDSA生成密钥过程依赖伪随机数生成接口，首先需要完成伪
随机数模块的配置工作，该过程包括熵源接口添加、熵源属性设置


466

## Page 467

等。伪随机数生成器配置过程的详细描述可回顾7.6.2节。

2.计算消息摘要

  示例中在计算ECDSA签名之前使用SHA256算法对消息计算消息
摘要，md通用接口的使用过程可以回顾4.6节基础示例部分，这里不
详细描述。

3.ECDSA生成密钥

  ECDSA生成密钥对接口为mbedtls_ecdsa_genkey，该函数需要输
入ECDSA结构体、椭圆曲线id、随机数生成接口、随机数结构体，密
钥会保存在ECDSA结构体中。示例中选择椭圆曲线secp256r1，
mbedtls中椭圆曲线参数定义在mbedtls/library/ecp_curves.c文件中。
mbedtls_rsa_gen_key接口原型如下：

 int mbedtls_ecdsa_genkey( mbedtls_ecdsa_context *ctx, mbedtls_ecp_group_id gid,
        int (*f_rng)(void *, unsigned char *, size_t), void *p_rng );

4.ECDSA生成签名

  ECDSA生成签名接口为mbedtls_ecdsa_sign，该函数需要输入椭
圆曲线结构体、私钥、消息、消息长度、随机数生成接口和随机数结
构体，输出得到签名结果r和s。

  由于椭圆曲线为secp256r1，可以确定签名结果r和s的长度分别为


    467

## Page 468

256比特。由于签名结果计算过程中需要使用随机数，所以使用相同
的密钥对相同的消息进行签名，每次的签名结果并不相同。
mbedtls_ecdsa_sign结构体原型如下：


int mbedtls_ecdsa_sign( mbedtls_ecp_group *grp, mbedtls_mpi *r, mbedtls_mpi *s,
        const mbedtls_mpi *d, const unsigned char *buf, size_t blen,
        int (*f_rng)(void *, unsigned char *, size_t), void *p_rng );


5.ECDSA验证签名

    ECDSA验证签名接口为mbedtls_ecdsa_verify，该函数需要输入椭
圆曲线结构体、消息、消息长度、公钥、签名结果r和s，返回值为0
则表示验证成功。mbedtls_ecdsa_verify接口原型如下：


    int mbedtls_ecdsa_verify( mbedtls_ecp_group *grp,
    const unsigned char *buf, size_t blen,
    const mbedtls_ecp_point *Q,
    const mbedtls_mpi *r, const mbedtls_mpi *s);










    468

## Page 469

11.8.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数修改为native_posix即可，编译过程中可关注
RAM及Flash的消耗情况。应用程序将把运行结果输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     由于示例中选择的椭圆曲线为secp256r1，所以ECDSA的签名r和
s的长度分别为256比特，共64字节。和RSA签名示例相比，ECDSA
算法所消耗的RAM空间和Flash空间更少，示例共消耗44KB Flash空
间和16KB RAM空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 11_dsa/ecdsa
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region   Used Size Region Size %age Used
             FLASH:     44180 B       2 MB    2.11%
               CCM:       0 GB       64 KB    0.00%
              SRAM:     15676 B     256 KB    5.98%
          IDT_LIST:       200 B       2 KB    9.77%
    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    . setup rng ...  ok
    1. hash msg ...  ok
    2. ecdsa generate keypair:
    04 BF 99 30 5D 99 56 D1 0A B4 25 9F 13 57 D8 BB
    45 49 89 CE 50 6B 46 2C 25 BF 05 16 EA 91 30 5D
    06 D7 36 AD BC FE EC A9 7E 18 1F F2 48 DC BC FE
    F4 44 D2 CC 35 45 24 3C C1 C2 DB 11 F5 95 45 1C


                        469

## Page 470

55 C5 83 9B A5 4B E5 6F 31 9B 52 40 BC DD ED 48
E7 3D D1 C8 E9 86 35 4A 3E 27 2E 40 E0 8B 8E B6
9E
3. ecdsa generate signature:
87 9E 59 05 6C D8 3D CB BE 74 48 4E 7E 06 EE 36
22 0F 73 C7 E8 80 0F 76 FE 66 35 36 9E 53 A8 3D
23 91 6A 4D EB C4 1C 6B D2 61 EA DD B9 B1 CA 9E
E1 27 5C 38 69 90 08 14 FD 86 A5 60 F1 56 36 79
4. ecdsa verify signature ... ok










470

## Page 471

11.9 本章小结

   本章介绍了3种数字签名算法——RSA数字签名、DSA数字签名
和ECDSA数字签名。结合之前内容可以看出，RSA算法即可用于公
钥加密，也可用于数字签名。RSA算法用于数字签名时，私钥用于生
成签名，公钥用于验证签名。DSA算法与RSA算法不同，它只能作为
数字签名算法使用，不能用于公钥加密或密钥交换。ECDSA算法和
DSA算法都依赖于单向散列函数。ECDSA算法与DSA算法有紧密的
联系，在相同的安全等级下，ECDSA算法具有密钥短、执行效率高
等特点，更适合物联网安全应用。










471

## Page 472

                第12章 数字证书X.509

12.1 本章主要内容

数字证书又称公钥证书或身份证书，是互联网或物联网安全的重
要组成部分。本章将重点介绍X.509证书标准，包括X.509证书的结
构，并通过一个示例说明证书的细节。在mbedtls X.509应用工具部
分，本章将介绍4种mbedtls X.509应用工具，分别为cert_req、
req_app、cert_write和cert_app，并使用4种工具生成自签名证书和服
务器证书。本章最后将通过一个mbedtls X.509示例介绍mbedtls数字证
书模块，并提供相关接口的详解描述，主要包括
mbedtls_x509_crt_parse、mbedtls_x509_crt_parse和
mbedtls_x509_crt  _verify等接口。










                472

## Page 473

12.2 数字证书原理

  有了公钥算法和数字签名算法后，通信变得越来越安全，但在公
钥分发上仍然存在一些问题，如果攻击者将公钥替换掉，则很容易对
系统发起攻击。而数字证书则可以很好地解决公钥分发的问题。在密
码技术中数字证书也被称为公钥证书或身份证书，它是用来证实公钥
持有者身份的电子文件。证书中包主要含公钥的相关信息、用户身份
信息及来自发行者的数字签名。

  下面通过一个示例说明证书的应用场景。假想场景中Alice需要
向Bob发送消息，Bob会将公钥发送给Alice，Alice使用公钥对消息进
行加密，Bob使用私钥进行解密。为了防止攻击者攻击，Bob使用数
字证书来完成公钥的分发。整个过程如图12-1所示。

  1）Bob生成密钥对，密钥对包括Bob公钥和私钥；

  2）Bob使用公钥生成证书签名请求（CSR），并将其发送给证书
认证机构（CA）；

  3）证书认证机构CA根据Bob的证书签名请求生成Bob证书，证
书中主要包含Bob的公钥和CA的数字签名；

  4）Bob将证书发送给Alice；

  5）Alice从CA获取根证书，并使用CA证书中的CA公钥对Bob证


    473

## Page 474

书中CA的签名进行验证，从而判断Bob证书的真实性；

  6）验证通过后，Alice从Bob的证书中提取Bob公钥；

  7）Alice使用Bob的公钥将明文加密并发送至Bob；

  8）Bob收到密文后使用私钥解密得到明文。










        图12-1 数字证书的应用场景

  在数字证书使用流程介绍中出现了两份证书——Bob证书和CA证
书。通过图12-1可以看出，Bob的证书由证书认证机构签发，一般情
况下Bob不能自己给自己签发证书。Bob并不是权威机构，若Bob给自
己签发证书，那么该证书就失去了“公信力”。但是CA证书却是一


    474

## Page 475

份“自签发”证书，也就是说数字证书机构使用自身的私钥对自身的公
钥进行签名。换句话说CA不但作为Alice和Bob的“裁判”，也当了自
己的“裁判”。所以数字证书机构的私钥保密性异常重要，一旦CA的
私钥泄密那么将产生巨大的影响。










    475

## Page 476

12.3 X.509证书标准

  X.509基于ASN.1标准，由国际电信联盟的标准化部门（ITU-T）
定义，它是数字证书的一种标准格式。X.509证书包含公钥、标识信
息（主机名、组织或个人）、证书颁发机构签名或自签名等信息。










    476

## Page 477

12.3.1 证书结构

X.509证书结构主要由12个字段构成，各字段详细描述如表12-1
所示。本节部分内容参考自《RFC 5280 Internet X.509 Public Key

Infrastructure Certificate and Certificate Revocation
List(CRL)Profile》。[1]

    表12-1     X.509证书字段










[1] https://tools.ietf.org/html/rfc5280










477

## Page 478

    12.3.2 证书名称

    在“发行商名称Issuer”和“证书主体名称Subject”字段中还包括多
    种可分辨名称，常用分辨名称如表12-2所示。例如GlobalSign根证书
    的可分辨名称如下：

    C = BE, O = GlobalSign nv-sa, CN = GlobalSign Organization Validation CA - SHA256 - G2

    阿里云网官证书的可分辨名称如下：

    C = CN, ST = ZheJiang, L = HangZhou, O = "Alibaba (China) Technology Co., Ltd.", CN = *.aliyun.com

        表12-2  常用分辨名称









  另外，证书扩展选项部分一般还包括证书持有者可选名称
（Subject Alternative Name）。持有者名称（Common Name）用于将
证书公钥信息和域名信息绑定在一起。但是在实际使用中发现，仅使
用持有者名称不够灵活，持有者名称只能与一个IP主机名进行绑定，
无法同时处理多个身份信息。证书持有者可选名称用于替换持有者名
称，它通过DNS名称、IP地址和URI将多个身份绑定在一起。例如，


    478

## Page 479

aliyun.com证书中持有可选名称包括以下内容：




X509v3 Subject Alternative Name:
DNS:*.aliyun.com, DNS:manager.channel.aliyun.com, DNS:market.tianchi.aliyun.com, DNS:*.ace.aliyun.com, DNS:*.alibabacloud.com, DNS:*.alicdn.com,
# 省略部分内容



一般情况下，客户端在执行证书验证过程时，将先检查证书持有
者可选名称，再检查持有者名称。










479

## Page 480

12.3.3 证书实例

  由于证书的结构复杂，为了更直观地展现证书结构，本节将通过
一个真实的证书说明X.509证书结构。

1.获取证书

  本节X.509证书来自于www.aliyun.com，可以从浏览器中获取
PEM格式的证书。以火狐浏览器为例，获取PEM证书的步骤如下：

  1）在火狐浏览器地址栏中输入www.aliyun.com，单击地址栏
的“安全锁”图标，在弹出的对话框中选择【更多信息】，如图12-2所
示。










图12-2 查看证书更多信息



480

## Page 481

2）在“页面信息”页面中选择【查看证书】，具体操作如图12-3
所示。

3）在“证书查看器”中单击【导出】按钮，并把证书另存
为“aliyuncom.crt”，如图12-4所示。










图12-3 选择查看证书










481

## Page 482

    图12-4     导出X.509证书

2.解析证书

                             aliyuncom.crt为文本类型文件，可使用记事本等工具直接查看。
aliyuncom.crt采用PEM编码格式，这种编码格式以“-----BEGIN
CERTIFICATE-----”开头，并以“-----END CERTIFICATE-----”结尾。

-----BEGIN CERTIFICATE-----
MIIJzzCCCLegAwIBAgIMcRG9pAknpfT64DClMA0GCSqGSIb3DQEBCwUAMGYxCzAJ

    482

## Page 483

BgNVBAYTAkJFMRkwFwYDVQQKExBHbG9iYWxTaWduIG52LXNhMTwwOgYDVQQDEzNH
bG9iYWxTaWduIE9yZ2FuaXphdGlvbiBWYWxpZGF0aW9uIENBIC0gU0hBMjU2IC0g
# 省略部分内容
6SH7/4J+PYwayJ9Z4TakhcgOHZbIve6eUXeE50RTqwFAf2eZx4yOfjt5sbdZ04lT
QamsflJijtOmMx5WFWtgDhXULtkQxV9fVf0j+zEkdxhPN4aChdblfvcG5J1ZQjGm
DmNwvbAmJqj/vFcEAwq8AT9vzG+eIgmtcDqCdOH30KlaASUPgri1Gr1aDke3twm9
TCNcZJ/4qLQPby8csEUtqLrRmQ==
-----END CERTIFICATE-----




    此处借助OpenSSL证书解析工具查看证书详细信息。控制台中输
    入以下内容：




    $ openssl x509 -text -in aliyuncom.crt –noout



      该指令中各参数解释如下。

      ·X509：证书解析工具；

      ·-text：以文本形式打印内容；

      ·-in aliyuncom.crt：输入的X.509证书名为aliyuncom.crt；

      ·-noout：不输出编码之后的X.509证书，该参数可减少打印内
    容。

      控制台输出内容如下：




    Certificate:
    Data:
    Version: 3 (0x2)
    Serial Number:
         71:11:bd:a4:09:27:a5:f4:fa:e0:30:a5
      Signature Algorithm: sha256WithRSAEncryption
    Issuer: C = BE, O = GlobalSign nv-sa, CN = GlobalSign Organization
             Validation CA - SHA256 - G2
    Validity
         Not Before: Apr 18 02:12:02 2018 GMT
         Not After : Mar 29 05:41:07 2019 GMT
    Subject: C = CN, ST = ZheJiang, L = HangZhou, O = "Alibaba (China)
             Technology Co., Ltd.", CN = *.aliyun.com
    Subject Public Key Info:


         483

## Page 484

    Public Key Algorithm: id-ecPublicKey
    Public-Key: (256 bit)
    pub:
               04:e0:cc:0e:64:3f:6c:1b:ca:cc:19:62:2a:2e:ec:
               44:19:49:e8:6f:e5:fd:dd:7e:ed:4e:73:bc:fb:81:
               54:a3:22:b5:ae:98:b1:50:75:c2:4a:5e:a3:cd:e0:
               e5:61:2f:d8:fb:1f:3e:b1:c8:18:0d:08:49:5b:4c:
               08:d7:52:5f:50
    ASN1 OID: prime256v1
    NIST CURVE: P-256
    X509v3 extensions:
    X509v3 Basic Constraints:
    CA:FALSE
    X509v3 Subject Alternative Name:
    DNS:*.aliyun.com
    Signature Algorithm: sha256WithRSAEncryption
    55:39:85:21:bb:84:3f:5e:22:91:31:ef:bf:47:50:5b:f4:8c:
    ce:33:71:cd:7f:b7:62:58:17:2f:7a:80:2d:52:a6:40:cb:3d:
    b5:1d:68:c5:4c:cf:87:1a:87:60:72:76:92:d8:47:19:ac:0e:
    # 省略部分内容
    74:e1:f7:d0:a9:5a:01:25:0f:82:b8:b5:1a:bd:5a:0e:47:b7:
    b7:09:bd:4c:23:5c:64:9f:f8:a8:b4:0f:6f:2f:1c:b0:45:2d:
    a8:ba:d1:99





3.公钥信息

      X.509证书的核心内容为公钥信息及签名信息。通过公钥信息可
以看出该证书的公钥采用椭圆曲线密钥算法，椭圆曲线为
prime256v1。公钥长度为256位（32字节），两个椭圆曲线坐标点合
计64字节。公钥结构中还包括一个压缩模式提示字节，此处为0x04，
表示非压缩模式。证书公钥信息如下：




    Public Key Algorithm: id-ecPublicKey
    Public-Key: (256 bit)
    pub:
    04:e0:cc:0e:64:3f:6c:1b:ca:cc:19:62:2a:2e:ec:
    44:19:49:e8:6f:e5:fd:dd:7e:ed:4e:73:bc:fb:81:
    54:a3:22:b5:ae:98:b1:50:75:c2:4a:5e:a3:cd:e0:
    e5:61:2f:d8:fb:1f:3e:b1:c8:18:0d:08:49:5b:4c:
    08:d7:52:5f:50
    ASN1 OID: prime256v1
    NIST CURVE: P-256





    4.签名信息



               484

## Page 485

    该证书由GlobalSign Domain Validation CA-SHA256-G2签发，签
    名算法为sha256WithRSAEncryption。签名内容如下：

    Signature Algorithm: sha256WithRSAEncryption
    55:39:85:21:bb:84:3f:5e:22:91:31:ef:bf:47:50:5b:f4:8c:
    ce:33:71:cd:7f:b7:62:58:17:2f:7a:80:2d:52:a6:40:cb:3d:
    b5:1d:68:c5:4c:cf:87:1a:87:60:72:76:92:d8:47:19:ac:0e:
    # 省略部分内容
    bc:57:04:03:0a:bc:01:3f:6f:cc:6f:9e:22:09:ad:70:3a:82:
    74:e1:f7:d0:a9:5a:01:25:0f:82:b8:b5:1a:bd:5a:0e:47:b7:
    b7:09:bd:4c:23:5c:64:9f:f8:a8:b4:0f:6f:2f:1c:b0:45:2d:
    a8:ba:d1:99

    示例证书中包含椭圆曲线公钥，椭圆曲线公钥的签名算法为
    sha256WithRSA，RSA密钥长度为2048比特。而GlobalSign Domain
    Validation CA-SHA256-G2的公钥签名算法为sha1WithRSA，RSA密钥
    长度为2048比特。GlobalSign Domain Validation CA-SHA256–G证书
    由根证书GlobalSign Root CA签发。各证书公钥算法与签名算法之间
    的关系如图12-5所示。










        图12-5 各证书公钥算法与签名算法之间的关系

    从关系图中可以看出，为了验证aliyun.com的服务器证书，客户
端需要同时支持SHA1和SHA256两种单向散列算法，同时也要支持


    485

## Page 486

    RSA算法和ECDSA算法。以mbedtls为例，其配置文件中至少需要包
    含以下配置选项：


    #define MBEDTLS_ECP_DP_SECP256R1_ENABLED
    #define MBEDTLS_ECP_C
    #define MBEDTLS_RSA_C
    #define MBEDTLS_SHA1_C
    #define MBEDTLS_SHA256_C


5.证书大小

    在互联网应用中并不会过多考虑X.509证书的大小，但对于内存
受限的物联网终端来说，过大的证书尺寸将是一个不可被忽视的问
题。在上述示例中，浏览器与aliyun.com服务器建立TLS连接时，
aliyum.com将向浏览器返回2份证书：中间CA证书GlobalSign Domain
Validation CA-SHA256–G和服务器证书*.aliyun.com。其中DER格式
的中间CA证书的大小为1133字节，而DER格式的服务器证书的大小
为2943字节，两份证书合计大小为4076字节。










    486

## Page 487

12.4 mbedtls X.509应用工具

   mbedtls为各个模块提供了应用工具，应用工具主要展示模块接
口的使用方法。mbedtls数字证书模块提供了4个示例应用工具——
cert_req、req_app、cert_write和cert_app。下面通过一个假想场景介绍
这些应用工具的使用方法，使用流程如图12-6所示。

   假想场景中包含两个角色——CA和Bob。CA通过gen_key工具生
成密钥对，然后使用cert_write工具生成一份自签名证书，该证书为假
想场景中的根证书。Bob通过cert_req生成证书请求，CA根据证书请
求中的内容通过cert_write颁发证书至Bob。










    487

## Page 488

图12-6 Bob申请证书流程










488

## Page 489

12.4.1 cert_req

   cert_req工具可用于生成证书签名请求（CSR），默认为PEM格
式。cert_req工具参数描述如表12-3所示。

    表12-3     cert_req参数描述










下面使用cert_req应用工具生成Bob证书请求，生成证书请求之前
需使用密钥生成工具生成密钥对。生成证书请求的具体过程如下：



# 生成椭圆曲线密钥对
$ gen_key type=ec ec_curve=secp256r1 filename=bob_privkey.pem format=pem
# 生成证书签名请求
$ cert_req filename=bob_privkey.pem subject_name=CN=Bob,O=security,C=china output_file=bob_cert.req
. Seeding the random number generator... ok
. Checking subject name... ok
. Loading the private key ... ok
. Writing the certificate request ... ok




489

## Page 490

证书请求过程说明如下：

1）使用ECC算法生成密钥对，曲线参数为secp256r1，密钥对以
PEM格式保存在名为bob_privkey.pem的文件中；

2）证书使用者名称中可分辨名称填
入“CN=Bob,O=security,C=china”；

3）Bob的证书请求保存在bob_cert.req文件中。










490

## Page 491

12.4.2 req_app

      req_app工具可用于解析证书签名请求文件，可通过参数指定文
件名称，解析结果将打印至终端。req_app工具使用方法如下：



    # 解析证书签名请求
    $ req_app filename=bob_cert.req
    # 输出内容
    . Loading the CSR ... ok
    . CSR information    ...
    CSR version        : 1
    subject name : CN=Bob, O=security, C=china
    signed using : ECDSA with SHA256
    EC key size     : 256 bits




    也可以使用OpenSSL req工具查看bob
    _cert.req，该工具功能更加
    强大，是req_app工具的有力补充。具体指令如下：



    $ openssl req -in bob_cert.req -text –noout
    # 输出内容
    Certificate Request:
    Data:
          Version: 1 (0x0)
          Subject: CN = Bob, O = security, C = china
          Subject Public Key Info:
          Public Key Algorithm: id-ecPublicKey
          Public-Key: (256 bit)
          pub:
                     04:79:c3:81:95:04:96:20:ce:ed:18:7d:8b:d7:a1:
                     ca:bd:14:63:1b:f4:55:05:ed:f4:5d:a4:32:1f:dc:
                     f3:b1:52:ce:d1:de:03:2f:c6:44:11:f2:22:18:4c:
                     cd:9d:b9:73:ed:63:a5:04:a2:44:00:c8:60:2f:a1:
                     49:09:c2:4a:f3
          ASN1 OID: prime256v1
          NIST CURVE: P-256
          Attributes:
          a0:00
    Signature Algorithm: ecdsa-with-SHA256
          30:45:02:20:63:11:a8:6c:64:b8:5c:da:43:bc:8f:da:b7:9b:
          95:71:a3:a6:e9:cf:78:4f:17:dc:41:f1:0c:03:e1:eb:42:c9:
          02:21:00:d2:4d:1e:1e:b6:54:3c:d9:b6:68:7a:1f:bd:49:41:
          48:5e:16:44:3f:e5:d5:da:7d:4e:0a:b4:b7:8b:15:46:d1










                     491

## Page 492

12.4.3 cert_write

   cert_write工具可以用于生成证书，默认输出格式为PEM格式。
cert_write工具参数描述如表12-4所示。

    表12-4     cert_write参数描述










492

## Page 493

生成Bob用户证书之前需要先生成CA根证书，然后通过CA根证


493

## Page 494

书生成Bob用户证书。生成过程如下：

1.通过cert_write生成根证书




# 生成CA椭圆曲线密钥对
$ gen_key type=ec ec_curve=secp256r1 filename=ca_privkey.pem format=pem
# 生成CA根证书
$ cert_write selfsign=1 issuer_name=CN=CA,O=security,C=china output_file=ca_cert.pem not_before=20180101000000 not_after=20220101000000 is_ca=1
# 输出内容
. Seeding the random number generator... ok
. Reading serial number... ok
. Loading the issuer key ... ok
. Setting certificate values ... ok
. Adding the Basic Constraints extension ... ok
. Adding the Subject Key Identifier ... ok
. Adding the Authority Key Identifier ... ok
. Writing the certificate... ok




自签名证书生成过程说明如下：

1）使用ECC算法生成密钥对，曲线参数为secp256r1，密钥对以
PEM格式保存在名为ca_privkey.pem的文件中；

2）默认发行者私钥为ca_privkey.pem，cert_write工具中省略了
_key参数；
issuer

3）证书发行者名称中可分辨名称填
入“CN=CA,O=security,C=china”，该可分辨名称为假想值，并没有实
际意义；

4）通过参数“selfsign=1”和“is_ca=1”生成自签名根证书；

5）根证书以PEM格式保存在名为“ca_cert.pem”的文件中。




494

## Page 495

2.通过cert_write生成Bob用户证书




# 生成Bob用户证书
$ cert_write request_file=bob_cert.req issuer_name=CN=CA,O=security,C=china output_file=bob_cert.pem not_before=20180101000000 not_after=20220101000000
# 输出内容
. Seeding the random number generator... ok
. Reading serial number... ok
. Loading the certificate request ... ok
. Loading the issuer key ... ok
. Setting certificate values ... ok
. Adding the Basic Constraints extension ... ok
. Adding the Subject Key Identifier ... ok
. Adding the Authority Key Identifier ... ok
. Writing the certificate... ok




生成Bob用户证书过程说明如下：

1）证书请求文件为bob_cert.req；

2）发行商名称中可分辨名称为“CN=CA,O=security,C=china”；

3）Bob用户证书以PEM格式保存在“bob_cert.pem”文件中。










495

## Page 496

12.4.4 cert_app

   cert_app相当于OpenSSL X.509工具。cert_app工具可用于解析证
书文件，可通过参数指定本地文件名称或远程服务器地址，解析结果
将打印至终端。cert_app工具参数描述如表12-5所示。

    表12-5     cert_app参数描述










  下面使用证书解析工具cert_app分别对CA根证书和Bob用户证书
进行解析，可以从解析后的输出中查看证书的基本信息。解析过程如
下。

1.通过cert_app查看根证书信息




# 解析CA根证书
$ cert_app mode=file filename=ca_cert.pem
# 输出内容
. Loading the CA root certificate ... ok (1 skipped)
. Loading the certificate(s) ... ok
. Peer certificate information     ...
cert. version   : 3
serial number   : 01
issuer name     : CN=CA, O=security, C=china
subject name    : CN=CA, O=security, C=china
issued on       : 2019-01-01 00:00:00
expires on      : 2022-01-01 00:00:00


                496

## Page 497

    signed using   : ECDSA with SHA256
    EC key size    : 256 bits
    basic constraints : CA=true





    2.通过cert_app查看Bob用户证书




    # 解析Bob用户证书
    $ cert_app mode=file filename=bob_cert.pem
    # 输出内容
    . Loading the CA root certificate ... ok (1 skipped)
    . Loading the certificate(s) ... ok
    . Peer certificate information     ...
    cert. version   : 3
    serial number   : 01
    issuer name     : CN=CA, O=security, C=china
    subject name    : CN=Bob, O=security, C=china
    issued on       : 2019-01-01 00:00:00
    expires on      : 2022-01-01 00:00:00
    signed using    : ECDSA with SHA256
    EC key size     : 256 bits
    basic constraints : CA=false





3.通过cert_app查看远程服务器证书

      cert_app工具除了可以解析本地证书之外，还可以解析远程服务
器证书。下面的示例中，通过cert_app工具解析aliyun.com证书，此处
可通过server
        _name指定域名并通过server_port指定端口号。首先
aliyun.com网站在端口443上提供https访问能力，cert_app工具作为客
户端，它将试图与aliyun.com服务主机建立TLS连接。在TLS握手过程
中aliyun.com服务器将把服务器证书传输至客户端，cert_req工具将证
书信息打印至控制台。



    $ cert_app mode=ssl server_name=aliyun.com server_port=443
    # 输出内容
    . Loading the CA root certificate ... ok (0 skipped)
    . Seeding the random number generator... ok
    . SSL connection to tcp/aliyun.com/443... ok
    . Peer certificate information ...
    cert. version   : 3
    serial number   : 71:11:BD:A4:09:27:A5:F4:FA:E0:30:A5
    issuer name     : C=BE, O=GlobalSign nv-sa, CN=GlobalSign



                    497

## Page 498

               Organization Validation CA - SHA256 - G2
subject name   : C=CN, ST=ZheJiang, L=HangZhou,
               O=Alibaba (China) Technology Co., Ltd., CN=*.aliyun.com
issued on      : 2018-04-18 02:12:02
expires on     : 2019-03-29 05:41:07
signed using   : RSA with SHA-256
EC key size    : 256 bits
basic constraints : CA=false
subject alt name : *.aliyun.com, (省略部分内容)










               498

## Page 499

12.5 mbedtls X.509示例

   本节基础示例用于展示如何使用mbedtls x.509接口完成证书解析
与证书验证操作。示例代码参考自mbedtls示例代码，在mbedtls示例
代码的基础上增加或修改了部分内容。本节示例均基于Zephyr系统构
建，借助Zephyr系统良好的适配性，本节示例不但可运行于Linux平
台，也可运行于STM32F429等硬件平台。为了正确运行示例代码，
需要在mbedtls_config.h配置文件中增加相关宏定义。宏定义描述如表
12-6所示。

       表12-6 mbedtls_config.h配置文件宏定义描述










    注意：由于篇幅限制，示例代码中只给出部分函数，完整代码详


    499

## Page 500

见本书GitHub代码仓库。本节示例位于12_cert文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。










    500

## Page 501

12.5.1 示例代码

    示例中使用PEM格式证书作为测试样本，以数组形式存放于内存
中，数组内容包括根证书和用户证书，通过mbedtls证书解析接口可
将证书解析到对应的结构体中。通过mbedtls证书验证接口检查证书
是否有效，验证过程中将使用根证书对用户证书进行验证，调用证书
验证接口时可指定回调函数，示例中将在回调函数中打印证书信息。
证书解析与验证流程简图如图12-7所示。










图12-7 证书解析与验证流程简图

证书示例代码如代码清单12-1所示。


501

## Page 502

    代码清单12-1 证书示例



    #include <zephyr.h>
    #include <stdio.h>
    #include <string.h>
    #include "mbedtls/x509_crt.h"
    #include "mbedtls/platform.h"
    #include "certs.h"
    static int my_verify(void *data, mbedtls_x509_crt *crt,
                                 int depth, uint32_t *flags)
    {
     ((void) data);
     char buf[1024];
     int mbedtls_x509_crt_info(buf, sizeof(buf) - 1, "     ", crt);
     mbedtls_printf("  . Verify requested for (Depth %d) ... ok\n", depth);
    for( int = 0; i < ret; i++) {
        mbedtls_printf("%c", buf[i]);
    }
    if ((*flags) != 0) {
        mbedtls_x509_crt_verify_info(buf, sizeof(buf), " ! ", *flags);
        for(int i = 0; i < ret; i++) {
        mbedtls_printf("%c", buf[i]);
        }
    }
    mbedtls_printf("\n");
    return(0);
}
int main(void)
{
    uint32_t flags = 0;
    mbedtls_x509_crt cert, cacert;
    mbedtls_platform_set_printf(printf);
    mbedtls_platform_set_snprintf(snprintf);
    mbedtls_x509_crt_init(&cert);
    mbedtls_x509_crt_init(&cacert);
    mbedtls_x509_crt_parse(&cert, bob_cert, sizeof(bob_cert));
    mbedtls_x509_crt_parse(&cacert, ca_cert, sizeof(ca_cert));
    mbedtls_printf("\n . Loading the certificate(s) ... ok\n\n");
    mbedtls_x509_crt_verify(&cert, &cacert, NULL, NULL, &flags, my_verify, NULL);
    mbedtls_x509_crt_free(&cert);
    mbedtls_x509_crt_free(&cacert);
    return 0;
}



    示例代码相关接口描述如表12-7所示

     表12-7 证书示例相关接口描述








     502

## Page 503

503

## Page 504

    12.5.2 代码说明

    1.加载证书

    示例中通过mbedtls X.509应用工具生成根证书和用户证书，生成
    过程可回顾12.4节。CA根证书以及Bob用户证书如下：



    // CA根证书
    const char ca_cert[] =
    "-----BEGIN CERTIFICATE-----\r\n"
    "MIIBojCCAUegAwIBAgIBATAMBggqhkjOPQQDAgUAMDAxCzAJBgNVBAMTAkNBMREw\r\n"
    "DwYDVQQKEwhzZWN1cml0eTEOMAwGA1UEBhMFY2hpbmEwHhcNMTkwMTAxMDAwMDAw\r\n"
    # 省略部分内容
    "DAYIKoZIzj0EAwIFAANHADBEAiAbJOzzfku6aEDQFc+uRKx5TZQ2e1VcvlHTfEda\r\n"
    "gQYQpgIgciJa/mdVjuILgIILPN5lV4iqgTdgYWEShNOL5woxMHw=\r\n"
    "-----END CERTIFICATE-----\r\n";
    // Bob用户证书
    const char bob_cert[] =
    "-----BEGIN CERTIFICATE-----\r\n"
    "MIIBojCCAUWgAwIBAgIBATAMBggqhkjOPQQDAgUAMDAxCzAJBgNVBAMTAkNBMREw\r\n"
    "DwYDVQQKEwhzZWN1cml0eTEOMAwGA1UEBhMFY2hpbmEwHhcNMTkwMTAxMDAwMDAw\r\n"
    # 省略部分内容
    "CCqGSM49BAMCBQADSQAwRgIhAMxdo4TuxZondcIOZrTfiLbZNLltYASALPXsQ+Bd\r\n"
    "lVuGAiEAjz/sl5hAYQ8Qamtl5Cqz1OydvZxsQDPUHmIZ35vljyM=\r\n"
    "-----END CERTIFICATE-----\r\n";



     证书解析接口为mbedtls_x509_crt_parse，该函数需输入X.509证
书结构体、证书和证书长度，解析结果将会保存到X.509证书结构体
中。mbedtls_x509_crt_parse接口原型如下：



    int mbedtls_x509_crt_parse( mbedtls_x509_crt *chain,
    const unsigned char *buf, size_t buflen );




    2.认证回调接口

    在认证用户证书之前需要编写认证回调接口，证书认证完成后会


    504

## Page 505

    调用该回调接口，示例中将在回调接口中打印证书信息。




    static int my_verify(void *data, mbedtls_x509_crt *crt,
int depth, uint32_t *flags)
    {
     ((void) data);
     char buf[1024];
     int mbedtls_x509_crt_info(buf, sizeof(buf) - 1, " ", crt);
    mbedtls_printf(" . Verify requested for (Depth %d) ... ok\n", depth);
    for(uint32_t i = 0; i < ret; i++) {
        mbedtls_printf("%c", buf[i]);
    }
    if ((*flags) != 0) {
        mbedtls_x509_crt_verify_info(buf, sizeof(buf), " ! ", *flags);
        for(uint32_t i = 0; i < ret; i++) {
        mbedtls_printf("%c", buf[i]);
        }
    }
    mbedtls_printf("\n");
    return(0);
}



      在回调接口中会对证书信息进行解析并打印，证书信息获取接口
为mbedtls_x509_crt_info。该函数需要输入存放证书解析信息的数组
长度、打印前缀、X.509证书结构体，输出得到证书解析信息。
mbedtls_x509_crt_info接口原型如下：



    int mbedtls_x509_crt_info( char *buf, size_t size, const char *prefix,
     const mbedtls_x509_crt *crt );



      当证书认证失败时，可以通过mbedtls_x509_crt_verify_info接口
获取证书认证信息。该接口和mbedtls_x509_crt_info接口类似，需要
输入存放证书解析信息的数组长度、打印前缀、认证结果标志，输出
得到证书认证信息。mbedtls_x509_crt_verify_info接口原型如下：



    int mbedtls_x509_crt_verify_info( char *buf, size_t size,
     const char *prefix, uint32_t flags );








     505

## Page 506

    3.证书认证

     证书认证接口为mbedtls_x509_crt_verify，该接口需要输入用户
证书结构体、根证书结构体、期望服务器名称、认证结果标志、认证
回调接口和认证回调接口的参数。当返回值为0并且认证结果标志为0
时，则表示认证成功，否则认证失败。认证失败后可通过认证回调函
    数查看具体失败原因。mbedtls_x509_crt_verify接口原型如下：

    int mbedtls_x509_crt_verify( mbedtls_x509_crt *crt,
          mbedtls_x509_crt *trust_ca,
          mbedtls_x509_crl *ca_crl,
          const char *cn, uint32_t *flags,
          int (*f_vrfy)(void *, mbedtls_x509_crt *, int, uint32_t *),
          void *p_vrfy );










          506

## Page 507

12.5.3 编译与执行

     本示例默认运行于necluo_f429zi平台。若需要运行在仿真平台，
只需将-DBOARD参数改为native_posix即可，编译过程中可本示例关
注RAM及Flash的消耗情况。应用程序将把运行结束输出至串口控制
台，所以应用程序下载至开发板运行之前需新建终端，并通过
minicom工具打开指定串口。操作指令如下：



    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     证书解析相关接口对RAM空间以及FLASH空间的消耗并不大，
但在实际应用中，使用RSA作为签名算法的X.509证书大小通常在
1KB以上，并且证书链中的证书所使用的签名算法有可能存在不同，
这就使得客户端需要支持多种签名算法才可能完成证书的验证工作。
因此在嵌入式客户端中加入证书认证功能前，需要对资源消耗情况进
行综合评估。本示例中共消耗约47KB FLASH空间和约18KB RAM空
间。编译与运行过程如下：




    # 进入示例代码文件夹
    $ cd 12_cert
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region   Used Size Region Size %age Used
             FLASH:     47456 B       2 MB    2.26%
               CCM:       0 GB       64 KB    0.00%
              SRAM:     17720 B     256 KB    6.76%
          IDT_LIST:       200 B       2 KB    9.77%
    # 下载到开发板运行


                        507

## Page 508

$ make flash
# 串口控制台输出
. Loading the certificate(s) ...  ok
. Verify requested for (Depth 1)  ... ok
cert. version   : 3
serial number   : 01
issuer name     : CN=CA, O=security, C=china
subject name    : CN=CA, O=security, C=china
issued on       : 2019-01-01 00:00:00
expires on      : 2022-01-01 00:00:00
signed using    : ECDSA with SHA256
EC key size     : 256 bits
basic constraints : CA=true
. Verify requested for (Depth 0)  ... ok
cert. version   : 3
serial number   : 01
issuer name     : CN=CA, O=security, C=china
subject name    : CN=Bob, O=security, C=china
issued on       : 2018-01-01 00:00:00
expires on      : 2022-01-01 00:00:00
signed using    : ECDSA with SHA256
EC key size     : 256 bits
basic constraints : CA=false










                                  508

## Page 509

12.6 本章小结

  本章介绍了X.509数字证书标准。X.509数字证书标准内容较多，
可借助OpenSSL x509工具查看证书的详细内容。本章通过一个假想
场景介绍了CA根证书的生成过程，也介绍了用户证书请求、用户证
书生成等过程。CA根证书是一份特殊证书，数字认证机构CA使用自
身的私钥对自身的公钥签名，CA证书也可称为“自签发证书”。而Bob
的证书由CA通过CA私钥签发，Bob本身不能给自己签发证书。

  X.509证书在互联网领域取得了广泛的应用，但是多数X.509证
书“尺寸”较大，对于物联网设备来说，处理X.509证书需要消耗更多
的内存资源和传输资源。就目前的实际情况而言，X.509证书可能不
适用于物联网应用。










    509

## Page 510

      第13章 mbedtls移植与性能分析

13.1 本章主要内容

  本章主要内容包括mbedtls的移植步骤及相关算法的性能分析。
mbedtls采用严格的组件化开发方式，独立性强且对平台的依赖性较
低。mbedtls移植过程大概可分为时间部分、网络部分和内存分配部
分等。mbedtls支持多种安全算法，但是不同的密码算法存在性能差
异，这些性能差异表现在执行速度和内存消耗方面。本章将分析单向
散列函数、AES-CBC、认证加密GCM、认证加密CCM、RSA、
DH、ECDH和ECDSA等算法的性能。最后还将分析椭圆曲线算法优
化选项对执行速度与内存消耗的影响。










    510

## Page 511

13.2 mbedtls移植

    mbedtls可以非常方便地移植到不同的操作系统和硬件平台中。
mbedtls使用标准C语言开发，在设计与实现过程中mbedtls的各个组件
尽量保证结构上的独立，努力减少对平台的依赖性，所以mbedtls只
需经过少量的修改便可移植到不同的平台。

    默认情况下，mbedtls运行于Linux平台或Windows平台。为了把
mbedtls移植到其他平台需要禁止以下宏定义：


    MBEDTLS_NET_C
    MBEDTLS_FS_IO
    MBEDTLS_HAVE_TIME_DATE
    MBEDTLS_HAVE_TIME










    511

## Page 512

    13.2.1 时间相关

    mbedtls提供定时模块组件timing，但是该组件只能运行于Linux
    或Windows环境。由于mbedtls DTLS组件依赖定时功能，若需要在其
    他平台启用DTLS，在关闭MBEDTLS  _C宏定义的基础上还
        _TIMING
需要通过mbedtls_ssl_set_timer_cb()函数定义定时模块回调函数。
mbedtls_ssl_set_timer_cb()函数原型如下：



    void mbedtls_ssl_set_timer_cb( mbedtls_ssl_context *ssl,
    void *p_timer,
    mbedtls_ssl_set_timer_t *f_set_timer,
    mbedtls_ssl_get_timer_t *f_get_timer );



      在Zephyr平台中可通过k _32()函数获得系统“滴
        _uptime_get
答”值。当mbedtls调用设置定时器回调函数时，定时器回调函数把系
统“滴答”值记录至snapshot变量中；当mbedtls调用获取定时回调函数
时，获取定时器回调函数再次读取系统“滴答”值，并与之前记录的
snapshot变量比较以判断是否超时。时间部分示例代码如下：



    struct dtls_timing_context
    {
      uint32_t snapshot;
      uint32_t int_ms;
      uint32_t fin_ms;
    };
    static struct dtls_timing_context timer;
    void dtls_timing_set_delay(void *data, uint32_t int_ms, uint32_t fin_ms)
    {
      struct dtls_timing_context *ctx = (struct dtls_timing_context *)data;
      ctx->int_ms = int_ms;
      ctx->fin_ms = fin_ms;
      if (fin_ms != 0) {
       ctx->snapshot = k_uptime_get_32();
      }
    }
    int dtls_timing_get_delay(void *data)
    {


      512

## Page 513

 struct dtls_timing_context *ctx = (struct dtls_timing_context *)data;
 unsigned long elapsed_ms;
 if (ctx->fin_ms == 0) {
  return -1;
 }
 elapsed_ms = k_uptime_get_32() - ctx->snapshot;
 if (elapsed_ms >= ctx->fin_ms)
  return 2;
 if (elapsed_ms >= ctx->int_ms)
  return 1;
 return 0;
}
int main()
{
 // 设置定时器回调
 mbedtls_ssl_set_timer_cb(&ssl, &timer,
     dtls_timing_set_delay, dtls_timing_get_delay);
}










 513

## Page 514

13.2.2 网络相关

      mbedtls仅提供可在Linux或Windows平台运行的BSD套接字，这
些实现位于{mbedtls代码仓库}/library/net_sockets.c文件中。若需要在
其他平台使用TLS或DTLS客户端功能，则至少需要实现以下接口：



    void mbedtls_net_init( mbedtls_net_context *ctx );
    int mbedtls_net_connect( mbedtls_net_context *ctx, const char *host,
    const char *port, int proto );
    int mbedtls_net_recv( void *ctx, unsigned char *buf, size_t len );
    int mbedtls_net_send( void *ctx, const unsigned char *buf, size_t len );
    int mbedtls_net_recv_timeout( void *ctx, unsigned char *buf, size_t len,
    uint32_t timeout );
    void mbedtls_net_free( mbedtls_net_context *ctx );



    若物联网安全应用还包括TLS或DTLS服务功能，则还应实现以
    下接口：




    int mbedtls_net_bind( mbedtls_net_context *ctx, const char *bind_ip,
    const char *port, int proto );
    int mbedtls_net_accept( mbedtls_net_context *bind_ctx,
    mbedtls_net_context *client_ctx,
    void *client_ip, size_t buf_size, size_t *ip_len );
    int mbedtls_net_poll( mbedtls_net_context *ctx, uint32_t rw, uint32_t timeout );



    实现以上接口是一个较为复杂的过程，幸运的是大多数开源组件
    也会提供兼容BSD标准的套接字接口，例如LWIP和Zephyr Socket组
    件。在这种兼容前提下可参考mbedtls中net_sockets实现，经过适当修
    改之后也可应用于其他平台。以下为Zephyr平台下mbedtls
        _net_recv()
    与mbedtls _send()实现。
        _net



    int mbedtls_net_recv( void *ctx, unsigned char *buf, size_t len )
    {
     int ret;

        514

## Page 515

     int fd = ((mbedtls_net_context *) ctx)->fd;
     if( fd < 0 )
     return( MBEDTLS_ERR_NET_INVALID_CONTEXT );
     (int) recv( fd, buf, len, 0);
     return( ret );
    }
    int mbedtls_net_send( void *ctx, const unsigned char *buf, size_t len )
    {
     int ret;
     int fd = ((mbedtls_net_context *) ctx)->fd;
     if( fd < 0 )
     return( MBEDTLS_ERR_NET_INVALID_CONTEXT );
     (int) send( fd, buf, len, 0);
    return( ret );
    }



      除了实现网络接口之外，还需要通过mbedtls_ssl_set_bio()函数指
定网络发送和网络接收函数。该函数的原型如下：




    void mbedtls_ssl_set_bio( mbedtls_ssl_context *ssl,
    void *p_bio,
    mbedtls_ssl_send_t *f_send,
    mbedtls_ssl_recv_t *f_recv,
    mbedtls_ssl_recv_timeout_t *f_recv_timeout);










     515

## Page 516

    13.2.3 内存分配相关

    mbedtls中各组件均依赖内存分配功能，mbedtls至少支持3种内存
    分配策略：C语言标准库、内部静态方法和自定义方法。

    1.标准C库

    默认情况下mbedtls将使用C语言标准库中calloc()和free()方法。
    使用标准C语言库的方法在Windows或Linux应用中较为常见，这两种
    平台中不易出现内存分配失败的情况。但是在其他嵌入式平台中（如
    STM32F4），由于内存与平台的限制，不易发现内存分配失败的情
    况，运行过程也无法合理统计堆栈空间的使用情况。在嵌入式平台
    中，推荐使用内部静态方法或自定义方法。

    2.内部静态方法

    所谓内部静态方法是启用mbedtls中memory_buffer_alloc组件，该
    组件提供一种可以在静态全局数组中分配内存的方法。通过定义以下
    两个宏定义便可开启memory_buffer_alloc组件。

    #define MBEDTLS_PLATFORM_MEMORY
    #define MBEDTLS_MEMORY_BUFFER_ALLOC_C

   使用memory_buffer_alloc组件前需要声明一个全局数组，然后调
用mbedtls_memory_buffer_alloc_init完成该组件的初始化工作。示例

        516

## Page 517

    代码如下：



    // 声明一个静态全局数组
    #if defined(MBEDTLS_MEMORY_BUFFER_ALLOC_C)
    #include "mbedtls/memory_buffer_alloc.h"
    static unsigned char heap[2048];
    #endif
    int main(void) {
    #if defined(MBEDTLS_MEMORY_BUFFER_ALLOC_C)
        mbedtls_memory_buffer_alloc_init(heap, sizeof(heap));
    #endif
     // 省略若干代码
    }




    3.自定义内存分配方法

      mbedtls还支持自定义calloc()和free()方法。若要启用自定义内存
分配方法需要在配置文件中增加MBEDTLS
        _PLATFORM_MEMORY
宏定义，并通过mbedtls_platform_set_calloc_free()函数指定自定义内
存分配方法。

    以FreeRTOS操作系统为例，FreeRTOS操作系统中内存分配函数
    为pvPortMalloc()和vPortFree()，通过这两个函数可以自定义适用于
    mbedtls的calloc()和free()方法。示例代码如下：



    #include "FreeRTOS.h"
    #include "task.h"
    void *platform_calloc(size_t n, size_t size)
    {
     void *ptr = NULL;
     ptr = pvPortMalloc(n * size);
     if (ptr != NULL) {
         memset(ptr, 0x00, n * size);
     }
     return ptr;
    }
    void platform_free(void* ptr)
    {
     vPortFree(ptr);
    }






     517

## Page 518

     再通过mbedtls_platform_set_calloc_free()完成初始化工作。示例
代码如下：




    void main(void)
    {
     mbedtls_platform_set_calloc_free(platform_calloc, platform_free);
     // 省略部分代码
    }










     518

## Page 519

13.3 mbedtls算法性能说明

               在实际物联网安全应用中，由于嵌入式硬件平台的限制及项目对
物联网安全的具体需求，开发工程师必须根据实际情况选择合适的安
全算法。物联网安全应用既不能盲目追求算法的安全等级，也不能忽
视算法性能对系统带来的影响，为了选择合适的安全算法我们需要对
算法性能有所了解。本节将重点讨论mbedtls所支持的物联网安全算
法的各项性能。

         本节依然选择Nucleo F429ZI平台来验证这些物联网安全算法。
在之前章的示例中均使用了Nucleo F429ZI平台，Nucleo F429ZI是一
款基于ARM Cortex-M4内核的STM32F4系列开发板，板载MCU为
STM32F429ZI，STM32F429ZI主频可达180MHz，并且具有256KB
RAM空间和一个真随机数生成器。

               如果从时间角度来说，算法的复杂程度和运算时间成正比，越复
杂的算法需要的运算时间越多。如果从CPU机器周期的角度来说，越
复杂的算法需要消耗越多的CPU机器周期。本节性能分析结果多以
CPU机器周期作为参考。









519

## Page 520

13.3.1 单向散列函数

                     一般情况下物联网安全应用均包括单向散列函数，单向散列函数
不但是消息认证码HMAC算法的必要组成部分，也是伪随机数生成器
的依赖算法之一。在当前的物联网安全应用中，不建议继续使用MD
系列算法（例如MD4算法和MD5算法），而推荐使用SHA1系列算
法，例如SHA1、SHA256和SHA512等。

                   同时使用3种不同的单向散列算法计算一个1000字节缓冲区的消
息摘要值。在验证程序中，mbedtls_sha1            _ret对应SHA1算法，
mbedtls_sha256_ret对应SHA256算法，mbedtls_sha512_ret对应
SHA512算法。在相同主频条件下，SHA1算法速度为46机器周期/
秒，而SHA256算法和SHA512算法的速度分别为89机器周期/秒和249
机器周期/s。3种不同的单向散列算法的对比结果如图13-1所示。由于
在一些较为严格的场景中SHA1算法已经被禁止使用，例如TLS1.2协
议，综合考虑3种算法的效率和安全性，建议在条件允许的情况下优
先使用SHA256算法。










520

## Page 521

图13-1 SHA系列算法性能对比










521

## Page 522

13.3.2 AES算法

AES算法是最常用的对称加密算法，AES算法明文分组长度为
128比特（16字节），密钥长度可以为128比特、192比特和256比特。
根据密钥的长度，AES算法被称为AES-128，AES-192和AES-256。
AES算法的执行过程包括多轮密钥加法，其中AES-128算法的轮数为
10轮，AES-192算法的轮数为12轮，而AES-256算法的轮数为14轮。
从安全角度来说，轮数越多算法强度越高安全性也越好，但是计算量
也越大。此处以CBC模式为例，分别加密1000字节测试明文样本，并
计算算法所消耗的机器周期。测试程序通过mbedtls_aes_crypt_cbc函
数加密测试明文样本。AES算法的性能测试结果如图13-2所示。

        从图中可以看出，AES-128算法的计算速度为128机器周期/秒，
而AES-192算法的计算速度为145机器周期/秒，AES-256算法的计算
速度为163机器周期/秒。AES算法的轮数越多，消耗的机器周期越
多，计算速度越慢，3种算法对安全系统的整体性能影响不大，可以
在实际项目开发中灵活使用3种算法。










522

## Page 523

图13-2 AES算法密钥长度性能对比










523

## Page 524

13.3.3 AES-GCM和AES-CCM

AES-CBC模式仅包括加密和解密过程，并不包括计算消息认证
码过程，而AES-GCM模式和AES-CCM模式是两种典型的认证加密算
法，认证加密算法不但包括加密和解密过程，还包括计算消息认证码
过程。mbedtls既支持AES-GCM模式也支持AES-CCM模式，在测试
条件下，同时使用AES-GCM模式和AES-CCM模式处理1000字节测试
明文样本，两种模式的消息认证码的长度均为16字节，
mbedtls_gcm_crypt_and_tag函数对应AES-GCM模式，而
mbedtls_ccm_encrypt_and_tag函数对应AES-CCM模式。两种模式的性
能测试结果如图13-3所示。

              从图中的结果可以看出，AES-GCM和AES-CCM性能相似，例如
AES-GCM-256的计算速度为399机器周期/秒，而AES-CCM-256的计
算速度为369机器周期/秒。在相同密钥长度情况下，AES-CCM模式
的性能要略优于AES-GCM模式。两种不同模式所消耗的机器周期与
密钥长度成正比，密钥长度越长消耗的机器周期越多。

            在实际项目中可以灵活选择GCM或CCM模式，两种效率相差不
大，AES-CCM模式略好于AES-GCM模式。







524

## Page 525

图13-3 AES-GCM模式和AES-CCM模式性能对比










525

## Page 526

13.3.4 伪随机数生成器

  伪随机数生成器是物联网安全应用的重要组成部分，本节将比较
CTR_DRBG算法和HMAC_DRBG算法的性能。CTR_DRBG算法通过
AES-CTR模式生成随机数序列，而HMAC_DRBG算法则依赖HMAC
算法。根据随机数据单向散列算法的不同，又可以分为HMAC-SHA1
算法和HMAC-SHA256算法。

  在测试条件下，CTR_DRBG算法和HMAC_DRBG算法的熵源均
来自于STM32F4的硬件真随机数生成器，在CTR_DRBG算法中通过
mbedtls_ctr_drbg_random函数获得伪随机数序列，在HMAC_DRBG算
法中通过mbedtls_hmac_drbg_random函数获得伪随机数序列。
CTR_DRBG算法和HMAC_DRBG算法的性能对比结果如图13-4所
示。

  从对比结果可以看出，CTR_DRBG算法生成伪随机数序列的速
度明显快于HMAC_DRBG算法。CTR_DRBG算法的生成速度可达
1150KB/秒，这种速度完全可以满足物联网安全应用。建议在实际应
用中优先选择CTR_DRBG算法。









    526

## Page 527

图13-4 CTR_DRBG算法和HMAC_DRBG算法的性能对比










    527

## Page 528

13.3.5 RSA

  RSA算法是常用的非对称加密算法，但其计算过程较慢，资源消
耗较多，对于受限制的物联网设备来说是一个不小的负担。在测试条
件下，分别使用RSA-2048算法处理1024字节测试样本。在测试程序
中，mbedtls_rsa_public函数对应RSA公钥操作，而mbedtls_rsa_private
函数对应RSA私钥操作。RSA公钥操作和私操作的性能对比如表13-1
所示。

      表13-1 RSA公钥操作和私钥操作性能对比




  从表中可以看出，RSA算法需要消耗较多的内存资源，例如公钥
操作需要消耗4K多字节，而私钥操作需要消耗8K多字节。RSA公钥
执行过程和私钥执行过程计算速度差异较大，公钥加密操作明显快于
私钥加密操作。在RSA数字签名应用中，私钥操作对应签名操作，而
公钥操作对应验证签名操作，所以RSA验证签名的速度明显优于生成
签名的速度。换句话说，RSA适用于需要反复验证签名的场合，而不
是需要频繁签名的场合。







    528

## Page 529

13.3.6 DHE和ECDHE

   下面我们再来比较两种密钥交换算法——DHE和ECDHE。在测
试条件下，使用DHE算法或ECDHE算法生成两组密钥对，然后再通
过两组公钥计算共享密钥。在DHE算法测试程序中，通过
mbedtls_dhm_make_public函数生成密钥对，该函数共调用两次，再
通过mbedtls_dhm_calc_secret函数生成共享密钥；在ECDEH算法测试
程序中，通过mbedtls_ecdh_make_public函数生成密钥对，该函数共
调用两次，再通过mbedtls_ecdh_calc_secret函数生成共享密钥。

   在相同密钥长度条件下，椭圆曲线相关算法的安全强度明显优于
DH或RSA算法。根据密码学的相关经验，椭圆曲线相关算法的密钥
长度与DH算法的密钥长度之间的对应关系如表13-2所示。

   测试程序选择4种相似的密钥交换算法，如表13-3所示。其中，
DH算法的密钥长度分别为2048位和3072位，而ECDH算法选择了两
条不同的椭圆曲线——secp256r1和secp384r1。从表13-2的经验数据可
以看出，256位的椭圆曲线的安全强度优于2048位的DH算法，同时
384位的椭圆曲线算法也优于3072位的DH算法。4种不同算法的对比
结果如表13-3所示。

    表13-2 椭圆曲线算法密钥长度与DH算法密钥长度对比




    529

## Page 530

表13-3 4种不同的密钥交换算法性能对比结果










        从表13-3的结果可以看出，ECDH算法性能要明显优于DH算法。
DHE-2048算法的执行平均速度为0.20次/秒，也就是说完成一次握手
所消耗的时间约为5秒，这对于物联网设备来说的确是一个“漫长”的
过程。而ECDHE-secp256r1算法的执行平均速度为2.30次/秒，也就说
完成一次握手所消耗的时间约为430ms，执行速度约为DHE-2048算法
的十几倍。另外，两种密钥分配算法均需要消耗大量的内存，而效率
最高的ECDHE-secp256r1也需要消耗约5K字节的内存空间。

所以从性能与安全角度出发，推荐在物联网应用中使用ECDH算


530

## Page 531

法，椭圆曲线推荐使用secp256r1。










531

## Page 532

13.3.7 ECDSA

   ECDSA是一种常用的基于椭圆曲线的数字签名算法，在ECDSA
系列算法中常用的椭圆曲线包括secp521r1、secp384r1、secp256r1、
secp224r1和secp192r1等。一般情况下，椭圆曲线的位数越多，签名
或验证签名的速度越慢，消耗的内存也越多。在测试条件下，通过
ECDSA算法对1024字节的测试样本数据进行签名，再使用相同的
ECDSA算法验证签名，测试程序将记录签名或验证签名速度，并统
计内存消耗情况。在测试程序中，通过mbedtls_ecdsa_write_signature
函数执行签名操作，签名过程中使用SHA256作为单向散列算法；签
名完成后再通过mbedtls_ecdsa_read_signature函数读取并验证签名结
果。签名和验证签名的性能对比如表13-4所示。

        表13-4 ECDSA签名和验证签名性能对比










   从表13-4的数据可以看出，相同椭圆曲线下，签名速度明显快于
验证签名速度，例如当椭圆曲线为secp256r1时签名的速度为7.53次/
秒，而验证签名的速度仅为2.20次/秒。另外椭圆曲线的位数越多，签


    532

## Page 533

名和验证签名的速度也越慢。它们之间的速度差异如图13-5所示。在
一定的安全要求下，推荐使用secp256r1和secp384r1这两条椭圆曲
线。










    图13-5 ECDSA签名和验证签名性能对比










    533

## Page 534

    13.3.8 ECC内存优化

    mbedtls中椭圆曲线算法的性能还与宏定义
    MBEDTLS_ECP_WINDOW_SIZE、
    MBEDTLS_ECP_FIXED_POINT_OPTIM和
    MBEDTLS_ECP_NIST_OPTIM有关。这些宏定义决定了椭圆曲线的
    计算效率和内存消耗。在之前的ECDSA和ECDH性能测试中，更关心
    计算效率而未关心内存消耗，例如基于secp256r1椭圆曲线的ECDSA
    签名算法，内存消耗为4448字节，而基于secp384r1椭圆曲线的
    ECDSA签名算法，内存消耗达到了10740字节。

           在前面几节ECDSA和ECDH性能测试中，椭圆曲线性能优化的宏
    定义如代码清单13-1所示。

    代码清单13-1 最优性能


    #define MBEDTLS_ECP_WINDOW_SIZE    6
    #define MBEDTLS_ECP_FIXED_POINT_OPTIM 1
    #define MBEDTLS_ECP_NIST_OPTIM


   其中：

   ·MBEDTLS_ECP_WINDOW_SIZE椭圆曲线算法中“点乘”操作消
耗最多的计算量，为了提高计算效率，mbedtls可以通过预先计算多
组中间结果并把这些中间结果保存在内存中。换句话说，中间结果越
多，“点乘”操作越快，内存消耗也越多。但如果未开启

        534

## Page 535

MBEDTLS_ECP_FIXED_POINT_OPTIM，这些中间结果将在使用后
被抛弃。

   ·MBEDTLS_ECP_FIXED_POINT_OPTIM把椭圆曲线算法中
的“点乘”中间结果保留在内存中。该宏定义需要配合
MBEDTLS_ECP_WINDOW_SIZE使用。

   ·MBEDTLS_ECP_NIST_OPTIM模除运算优化选项，mbedtls参考
《FIPS PUB 186-4 Digital Signature Standard（DSS）》附录D.2中相关
算法加快模除运算。

   MBEDTLS_ECP_WINDOW_SIZE对椭圆曲线的计算效率和内存
消耗有不小的影响。以secp256r1椭圆曲线为例，在保持
MBEDTLS_ECP_FIXED_POINT_OPTIM关闭的情况下，ECDHE算法
的执行速度如图13-6所示，而ECDHE算法的内存消耗情况如图13-7所
示。

   从上述两图可以看出，MBEDTLS_ECP_WINDOW_SIZE取值越
大ECDHE算法的执行速度越快，但提升空间较小；但随着
MBEDTLS_ECP_WINDOW_SIZE取值的增加，ECDHE算法所消耗的
内存越来越多。例如当MBEDTLS_ECP_WINDOW_SIZE取值为2时，
内存消耗为1376字节；而当MBEDTLS_ECP_WINDOW_SIZE取值为6
时，内存消耗增加至2360字节。内存增加幅度较大但执行速度提升效
果较低。




    535

## Page 536

为了尽可能降低内存消耗，建议减小
MBEDTLS_ECP_WINDOW_SIZE设置大小，并关闭
MBEDTLS_ECP_FIXED_POINT_OPTIM，仅保留
MBEDTLS_ECP_NIST_OPTIM优化选项。config-suite-b中推荐配置如
代码清单13-2所示。










图13-6 ECDHE算法执行速度










536

## Page 537

    图13-7 ECDHE算法内存消耗

    代码清单13-2 推荐配置



    #define MBEDTLS_ECP_WINDOW_SIZE    2
    #define MBEDTLS_ECP_FIXED_POINT_OPTIM 0
    #define MBEDTLS_ECP_NIST_OPTIM



     以椭圆曲线secp256r1为例，在最优性能配置条件下椭圆曲线相
关算法的速度与内存消耗如表13-5所示。

表13-5 最优性能配置条件下椭圆曲线相关算法速度与内存消耗情况








    537

## Page 538

  同样以椭圆曲线secp256r1为例，在推荐配置条件下椭圆曲线相
关算法的速度与内存消耗如表13-6所示。

 表13-6 推荐配置条件下椭圆曲线相关算法速度与内存消耗情况





  从表13-5和表13-6可以看出，推荐配置条件下椭圆曲线的性能有
所下降，但是内存消耗也明显减少。两种不同配置条件下内存消耗对
比如图13-8所示。










    图13-8 最优配置与推荐配置情况下内存消耗对比


    538

## Page 539

   根据上面的分析，建议把MBEDTLS_ECP_WINDOW_SIZE设置
为2，关闭MBEDTLS_ECP_FIXED_POINT_OPTIM优化选项，并打开
MBEDTLS_ECP_NIST_OPTIM优化选项。采用这种推荐配置可保持
计算速度和内存消耗之间的平衡。










    539

## Page 540

    13.4 本章小结

  本章介绍了mbedtls移植和性能分析两部分内容。若需要在其他
平台使用mbedtls网络功能，需要关闭MBEDTLS_NET_C选项。若在
其他平台启用DTLS功能，需要重新定义时钟模块，并使用
    mbedtls_ssl_set_timer_cb()完成时钟模块初始化操作。mbedtls支持多
    种内存分配方法，建议使用内部静态方法或自定义内存分配方法，不
    建议使用标准C库中的calloc()和free()。

    本章还分析多种安全算法的性能。单向散列函数推荐使用
    SHA256算法。AES系列算法的执行速度与密钥长度成正比，性能相
    差不大，可根据系统安全需求灵活选择。AES_GCM与AES_CCM性
    能差异较小。伪随机数生成器算法CTR_DRBG性能优异，建议在实
    际应用中优先选择。RSA算法消耗资源较多且RSA密钥系统存在诸多
    安全隐患，不建议把RSA算法用于密钥交换，RSA算法可用于数字签
    名。对于物联网设备而言，RSA算法更适合验证签名较多的场合。
    ECDH算法的性能优于DH算法，建议优先选择ECDH算法。ECDSA
    算法中，执行速度和内存消耗与椭圆曲线的位数成正比，建议选择
    secp256r1或secp384r1，相较于其他曲线这两条曲线可保持安全需
    求、执行速度与内存消耗之间的平衡。最后，mbedtls还提供椭圆曲
    线优化选项，建议与config-suite-b中的配置保持一致。





    540

## Page 541

        第14章 TLS

14.1 本章主要内容

  TLS（Transport Layer Security）是一种为计算机网络提供通信安
全的加密协议，TLS协议常用于承载HTTP协议，HTTPS协议可简单
理解为HTTP+TLS。一次完整的TLS通信一般可分为密钥交换、密钥
计算和对称加密3个阶段。本章将介绍TLS密码套件，密码套件包括
TLS通信过程中很多关键信息，例如密钥交换算法、对称加密算法和
消息认证码计算方法等。TLS协议可分为记录层协议和4个子协议，4
个子协议包括密码规格变更协议、警报协议、握手协议和应用数据协
议。其中握手协议是TLS协议中最为复杂且最为精密的部分，本章将
通过示例分析握手协议。密钥交换部分，本章将重点介绍ECDHE-
ECDSA密钥协商算法。密钥计算部分，本章将介绍伪随机数生成函
数、主密钥计算和KeyBlock计算等内容。对称加密部分，本章将介绍
分组加密和认证加密两部分内容，其中分组加密还包括
mac_then_encrypt和encrypt_then_mac两个子部分。

  mbedtls TLS应用工具部分将重点介绍ssl_server2和ssl_client2，通
过这两个应用工具可以进行各种各样的TLS试验。最后通过TLS客户
端示例说明mbedtls TLS相关接口的使用方法。





    541

## Page 542

14.2 TLS原理

  TLS是一种通过计算机网络提供通信安全的加密协议，该协议在
Web浏览器、电子邮件、即时消息和语音（VoIP）等应用程序中得到
了广泛的应用。

  TLS协议由互联网工程任务组（IETF）在1999年首次定义。TLS
协议基于SSL3.0协议，SSL协议由网景（Netspace）公司于1994年设
计，并在自家Web浏览器Netscape Navigator上进行了实现。TLS协议
与SSL协议在细节上存在不少差别，但一般情况下我们总是把TLS和
SSL协议作为一个整体对待。TLS 1.2是目前广泛使用的TLS协议版
本，该版本的详细内容可参考《RFC 5246 The Transport Layer
Security（TLS）Protocol Version 1.2》。

  HTTP协议常被用于在Web浏览器和网站服务器之间传递数据，
但HTTP协议总以明文方式发送内容，不提供任数据加密功能。如果
攻击者截取了Web浏览器和网站服务器之间的传输报文，就可以直接
获取报文中的敏感信息，因此HTTP协议不适合传输敏感内容，比如
信用卡号、密码等。为了解决HTTP协议无法传输敏感内容这一问
题，HTTPS（Hyper Text Transfer Protocol over Secure Socket Layer）
应运而生。HTTPS协议通过TLS协议加密传输报文，实现Web浏览器
与网站服务器之间的安全通道。HTTP、HTTPS和TLS之间的关系如
图14-1所示。


    542

## Page 543

        图14-1 HTTP、HTTPS与TLS的关系

   当Bob通过Web浏览器登录GitHub服务器时，Bob需要向GitHub
网站提供用户名和密码等敏感数据。若使用HTTP协议进行传输，
Bob的用户名和密码将作为明文进行传输，这样窃听者将有可能得到
Bob的用户名和密码。若使用TLS作为通信加密协议，在此之上承载
HTTP协议，通过这两种协议的叠加，Bob的敏感数据将会得到保
护，从而防止这些数据被窃听。当Bob通过HTTPS访问github.com
时，URL不再以“http://”开头，而以“https://”开头。一般情况下，当
Bob使用https访问某网站时，浏览器的地址栏前将出现一个“安全
锁”，该“安全锁”提醒用户：Web浏览器已经与网站建立了安全通
道。Bob通过HTTPS登录github.com的大致流程如图14-2所示。





    543

## Page 544

图14-2 HTTPS访问网站流程示意图










544

## Page 545

14.2.1 TLS设计目标

  TLS协议的设计目标主要包括密码学安全、互操作性、可拓展性
和高效率。

  ·密码学安全：TLS协议可以为通信双方建立安全可靠的连接，
主要技术手段包括消息加密、消息完整性验证和身份认证等。

  ·互操作性：开发人员可以独立开发和使用TLS的应用程序，使
得通信双方可以在互不了解彼此代码的情况下成功地交换密码参数。

  ·可拓展性：TLS提供一种密码通信框架，可以替换一些存在安
全隐患的算法，并将经过验证的新算法集成到TLS通信框架中。

  ·高效率：加密算法属于CPU密集型运算，尤其是公钥密码算
法。出于该原因，TLS协议加入了一个可选的会话缓存功能，会话缓
存功能可以减少建立连接过程的握手次数。










    545

## Page 546

14.2.2 TLS框架说明

  TLS是一种加密通信框架，它几乎使用到了本书第3~12章所提到
的所有密码技术。TLS加密通信过程大致可分为3个阶段：

  ·密钥交换阶段：伪随机数生成算法、ECDH、ECDSA、RSA和
DH。另外X.509证书也是密钥交换阶段的重要组成部分。

  ·密钥计算阶段：HMAC算法，例如HMAC-SHA256或HMAC-
SHA512。

  ·对称加密阶段：AES系列算法和HMAC算法，AES算法包括
AES-CBC、AES-GCM和AES-CCM，HMAC算法包括HMAC-SHA256
和HMAC-SHA512。

  TLS协议框架和涉及的密码技术如图14-3所示。










    546

## Page 547

图14-3 TLS协议中使用的密码技术










547

## Page 548

14.3 TLS密码套件

   TLS协议通信框架使密码算法可以像零件一样进行组合或替换。
虽然这种方式很灵活，但在实际通信过程中，双方需要具有相同密码
运算能力才能完成密钥协商和消息加解密等操作。为了保证TLS协议
整体的兼容性，IANA组织规定了多种密码套件（The Cipher
Suite），通信双方可以使用约定好的密码套件进行加密通信。密码套
件通常由密钥协商算法、身份认证算法、对称加密算法、消息认证码
（MAC）和伪随机数算法组成，如图14-4所示。







    图14-4 密码套件构成

    下面列举几种常见的密码套件。

    1.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384

    通信双方协商采用
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384作为密码套
    件，该密码套件的具体含义如下：

    ·密钥协商算法ECDHE


    548

## Page 549

    ·身份认证算法ECDSA

    ·对称加密算法AES_256

    ·消息认证算法GCM

    ·伪随机数算法HMAC-SHA384

    2.TLS_PSK_WITH_AES_128_CBC_SHA256

   通信双方协商采用TLS_PSK_WITH_AES_128_CBC_SHA256作
为密码套件，该密码套件的具体含义如下：

    ·密钥协商算法PSK

    ·身份认证算法无

    ·对称加密算法AES_128_CBC

    ·消息认证算法HMAC-SHA256

    ·伪随机数算法HMAC-SHA256

    3.TLS_RSA_WITH_AES_128_CBC_SHA256

   通信双方协商采用TLS_RSA_WITH_AES_128_CBC_SHA256作
为密码套件，该密码套件的具体含义如下：

    ·密钥协商算法RSA

        549

## Page 550

·身份认证算法RSA

·对称加密算法AES_128_CBC

·消息认证算法HMAC-SHA256

·伪随机数算法HMAC-SHA256

4.TLS_DHE_RSA_WITH_AES_128_CBC_SHA256

通信双方协商采用
TLS_DHE_RSA_WITH_AES_128_CBC _SHA256作为密码套件，该密
码套件的具体含义如下：

·密钥协商算法DHE

·身份认证算法RSA

·对称加密算法AES_128_CBC

·消息认证算法HMAC-SHA256

·伪随机数算法HMAC-SHA256










550

## Page 551

14.4 TLS记录层协议

   TLS协议位于TCP传输协议之上，通过提供消息机密性、消息完
整性和身份认证等方法来保障通信安全。TLS协议一般可分为两层，
底层为TLS记录协议，上层为4个子协议，分别是握手协议、密码规
格变更协议、警告协议和应用数据协议。其中握手协议是子协议中最
为复杂的一部分。TLS分层结构如图14-5所示。










        图14-5     TLS分层结构

    每一条TLS记录层协议均包含一个较短的首部，该首部中包含子
    协议类型、TLS版本号和负载长度等信息。TLS记录层协议包括以下
    字段：

    struct {
    uint8 major;
    uint8 minor;
    } ProtocolVersion;
    enum {
    change_cipher_spec(20), alert(21), handshake(22),

        551

## Page 552

application_data(23),(255)
} ContentType;
struct {
ContentType type;
ProtocolVersion version;
uint16 length;
opaque fragment[TLSPlaintext.length];
} TLSPlaintext;


  其中，

  ·type：记录子层协议类型，包括应用数据协议和3个握手子协
议。

  ·version：TLS版本，本章中描述的协议版本为TLS 1.2版本
（{0x03,0x03}）。

  ·length：TLS负载数据长度，负载数据长度不应超过214字节。

  ·fragment：TLS负载数据。

  TLS记录层协议的具体结构如图14-6所示。










  552

## Page 553

图14-6 TLS记录层协议










553

## Page 554

    14.5 密码规格变更协议

      密码规格变更ChangeCipherSpec消息是TLS记录协议的一个子协
    议，它用于通知接收方，将使用协商后密码套件对后续数据报文进行
    加密。其结构示意如图14-7所示。ChangeCipherSpec的具体结构如
    下：

    struct {
        enum { change_cipher_spec(1),(255)} type;
    } ChangeCipherSpec;










        图14-7 密码规格变更协议

   需要注意的是，如果在通信期间发生了重新握手
（rehandshake），通信双方可能需要继续使用旧的密码规范发送数


    554

## Page 555

据。如果密码规格发生了变更，则需要使用新的密码规格发送数据。

发送ChangeCipherSpec的一方不确定另一方是否完成了主密钥的计
算，所以在一个小的时间窗口内接收方必须接收并缓存数据。在实际
情况中，对于现代计算机的计算能力而言，这个时间窗口通常会非常
小。










    555

## Page 556

    14.6 警报协议

TLS警报协议是一种很简单的通知机制，用于将通信异常告之对
    端。TLS警报协议由两部分组成，分别为警报等级和警报描述。

    struct {
         AlertLevel level;
         AlertDescription description;
    } Alert;

警告等级分为警告（warning）和致命错误（fatal）。当警报等级
    为fatal时，会立即终止连接。表14-1为TLS警报协议结构的具体描
    述，其中阴影部分的警告等级为fatal。

表14-1 警告协议结构描述










         556

## Page 557

557

## Page 558

14.7 握手协议

  握手协议是TLS协议中最复杂的部分，但也是最精密的部分。在
握手过程中，通信需要进行密码套件协商并完成身份认证。根据实际
情况的不同，整个过程需要交换6~10条消息，根据客户端和服务器端
的不同设置，交换过程可能出现各种各样的变换。本节将重点分析两
种流程——完整握手流程和会话恢复流程。










    558

## Page 559

    14.7.1 握手协议概述

    与TLS记录层相似，握手协议中可包括握手子协议类型和握手应
    用数据长度两部分。具体结构如下：




    struct {
    HandshakeType msg_type;
    uint24 length;
    select (HandshakeType) {
            case hello_request:       HelloRequest;
            case client_hello:        ClientHello;
            case server_hello:        ServerHello;
            case certificate:         Certificate;
            case server_key_exchange: ServerKeyExchange;
            case certificate_request: CertificateRequest;
            case server_hello_done:   ServerHelloDone;
            case certificate_verify: CertificateVerify;
            case client_key_exchange: ClientKeyExchange;
            case finished:            Finished;
    } body;
    } Handshake;
    enum {
    hello_request(0), client_hello(1), server_hello(2),
    certificate(11), server_key_exchange (12),
    certificate_request(13), server_hello_done(14),
    certificate_verify(15), client_key_exchange(16),
    finished(20), (255)
    } HandshakeType;



      TLS记录协议与握手子协议的关系如图14-8所示。需要注意的
是，TLS记录层首部中包含length字段，该字段用于指示TLS负载数据
长度；而握手子协议中也包含length字段，该字段用于指示握手子协
议中负载数据的长度，两者并不相同。










                                      559

## Page 560

图14-8 TLS记录协议与握手子协议的关系










560

## Page 561

    14.7.2 完整握手过程


   握手协议主要用于密钥交换和身份认证，下面通过一个完整的握
手流程说明TLS握手协议。由于握手过程较为复杂，本节将借助
mbedtls ssl_server2工具和ssl_client2工具构建TLS握手过程，密码套件
为TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384，该过程会
进行双向认证。握手过程中使用Wireshark进行抓包，本节会使用该
抓包文件作为样本对握手过程进行分析。握手协议的整体过程如图
14-9所示。










    561

## Page 562

    图14-9     TLS握手过程

1.ClientHello

客户端第一次连接到服务器时需要发送ClientHello消息，
ClientHello消息中包含TLS版本信息、随机数、客户端所支持的密码
套件等参数。以下样本中可看到ClientHello消息部分关键字段。

Handshake Protocol: Client Hello
Handshake Type: Client Hello (1)
Length: 135

    562

## Page 563

Version: TLS 1.2 (0x0303)
Random: 5b1738ea8529f5bfdb89072425313a1c85329e9c99dfd82e...
Session ID Length: 0
Cipher Suites Length: 4
Cipher Suites (2 suites)
Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (0xc02c)
Cipher Suite: TLS_EMPTY_RENEGOTIATION_INFO_SCSV (0x00ff)
Compression Methods Length: 1
Compression Methods (1 method)
Extensions Length: 90
Extension: server_name (len=14)
Extension: signature_algorithms (len=22)
Extension: supported_groups (len=24)
Extension: ec_point_formats (len=2)
Extension: encrypt_then_mac (len=0)
Extension: SessionTicket TLS (len=0)




·Version：版本编号，客户端所支持的TLS最高版本。

·Random：随机数序列，随机数序列由4字节时间戳和28字节安
全随机数组成，该部分总长为32字节。在握手时客户端和服务器都会
提供随机数。该随机数一般由随机数生成器生成，这些随机数在身份
认证中起着举足轻重的作用，它可以防止重放攻击。

·Session ID：会话ID，客户端首次建立连接时该字段一般为空，
为空时表示客户端并不希望恢复某个已经存在的会话。在后续的连接
过程中，该字段将会保存会话的唯一标识符。服务器可以借助该会话
ID在服务器缓存中找到对应的会话状态。

·Cipher Suites：密码套件，客户端与服务器建立连接时，将向服
务器提供自身所支持的密码套件。此处密码套件为
                       _SHA384，该套件的编
TLS_ECDHE_ECDSA_WITH_AES_256_GCM
号为0xc02c。

·Extension：扩展选项，扩展选项以扩展块的形式出现在


563

## Page 564

ClientHello或ServerHello消息结尾，扩展块由多个扩展项堆叠组成，
每个扩展项包括2字节扩展标识符和扩展数据。扩展选项容易被人忽
略，但它也是密钥交换过程的重要组成部分。例如，ECDH密钥协商
时，需要通过扩展选项说明客户端所支持的椭圆曲线和签名方法。此
时客户端支持以下多种扩展选项。

    ·server_name：客户端期望访问的虚拟主机名称。

    ·signature_algorithms：客户端通知服务器自身支持的签名算法
和单向散列函数，TLS1.2协议中支持的签名算法包括RSA和
ECDSA，支持的单向散列函数包括SHA1、SHA256和SHA512等。

    ·supported_groups：客户端通知服务器自身支持的椭圆曲线列
表。

    ·ec_point_formats：客户端通知服务器自身支持的椭圆曲线坐
标点类型，一般选择非压缩模式。

    ·encrypt_then_mac：客户端期望服务器使用先加密后计算消息
认证码模式，默认情况下TLS1.2版本采用先计算消息认证码后加密模
式。

    ·SessionTicket：客户端支持无状态会话恢复。

2.ServerHello

   当服务器收到客户端发送的ClientHello后，将返回一个

        564

## Page 565

    ServerHello消息。以下示例样本中可看到ServerHello消息的部分关键
    字段。




    Handshake Protocol: Server Hello
    Handshake Type: Server Hello (2)
    Length: 59
    Version: TLS 1.2 (0x0303)
    Random: 5b1738ea0c2e565bf2282c8a9c6ea40ff74d177f4f8dc769...
    Session ID Length: 0
    Cipher Suite: TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (0xc02c)
    Compression Method: null (0)
    Extensions Length: 19
    Extension: renegotiation_info (len=1)
    Extension: extended_master_secret (len=0)
    Extension: SessionTicket TLS (len=0)
    Extension: ec_point_formats (len=2)



      ServerHello消息的字段描述与ClientHello类似，主要包括以下两
个。

      ·Random：随机数序列，服务器向客户端提供32字节随机数序
列。

      ·Cipher Suites：协商之后的密码套件。

3.Certificate

      当客户端需要对服务器的身份进行验证时，服务器端发送
Certificate消息。该消息中包含证书清单，证书清单是一组X.509 v3证
书列表。证书列表包含服务器证书、中间证书和根证书。通常情况下
服务器并不会发送根证书，这就需要客户端提前导入根证书。由于样
本所使用的测试客户端中已经固化了根证书，握手消息中只包含一个
550字节的服务器证书并不包括根证书。通过Certificate消息，客户端


    565

## Page 566

将获得服务器的公钥，并通过根证书中的公钥验证服务器公钥的合法
性。




Handshake Protocol: Certificate
Handshake Type: Certificate (11)
Length: 553
Certificates Length: 550
Certificates (550 bytes)
        Certificate Length: 547
Certificate: 3082021f308201a5a003020102020109300a06082a8648ce...
signedCertificate
           version: v3 (2)
           serialNumber: 9
           signature (ecdsa-with-SHA256)
           issuer: rdnSequence (0)
           validity
           subject: rdnSequence (0)
           subjectPublicKeyInfo
           extensions: 3 items
algorithmIdentifier (ecdsa-with-SHA256)
           Algorithm Id: 1.2.840.10045.4.3.2 (ecdsa-with-SHA256)
Padding: 0
encrypted: 30650231009a2c5cd7a6dba2e5640df0b94eddd761d61331...





4.ServerKeyExchange

  ServerKeyExchange可携带密钥交换过程的额外数据。某些场景
下，服务器并不会发送ServerKeyExchange消息，以椭圆曲线密钥交
换算法为例：

  ·若密钥协商采用ECDH，客户端将使用证书中的服务器公钥，服
务器不发送ServerKeyExchange。

·若密钥协商采用ECDHE，服务器将通过ServerKeyExchange消息
告之客户端临时ECDH公钥，并使用服务器私钥对该临时公钥进行签
名。

  下面的示例样本中可以看到ServerKeyExchange消息的关键字

               566

## Page 567

段。


Handshake Protocol: Server Key Exchange
Handshake Type: Server Key Exchange (12)
Length: 144
EC Diffie-Hellman Server Params
Curve Type: named_curve (0x03)
Named Curve: secp256r1 (0x0017)
Pubkey Length: 65
Pubkey: 04d06dc0e8aa471d0693be1a3ae6e47f3c6b39d99077ce3e...
Signature Algorithm: ecdsa_sha512 (0x0603)
          Signature Hash Algorithm Hash: SHA512 (6)
          Signature Hash Algorithm Signature: ECDSA (3)
Signature Length: 71
Signature: 3045022078678b2e143b9355f2f2ab65fe239f757a1fee62...

示例样本中，服务器通过ServerKeyExchange给出临时椭圆曲线
公钥，该公钥使用的椭圆曲线为secp256r1，公钥包括X坐标、Y坐标
和压缩提示，合计65字节。该公钥使用SHA512算法计算单向散列
值，接着使用椭圆曲线secp256r1计算得到签名值（r，s），签名值均
为32字节。最后签名结果还需经过了ASN.1编码，该样本中ASN.1编
码后为71字节。

5.CertificateRequest

当服务器端需要对客户端的身份进行验证时，服务器发送
CertificateRequest消息，消息中包括以下信息：

·服务器可理解的证书类型清单（certificate_types）

·服务器可理解的签名算法清单
（supported_signature_algorithms）

·服务器可理解的认证机构清单（certificate_authorities）

              567

## Page 568

    Handshake Protocol: Certificate Request
    Handshake Type: Certificate Request (13)
    Length: 211
    Certificate types count: 2
    Certificate types (2 types)
    Certificate type: RSA Sign (1)
    Certificate type: ECDSA Sign (64)
    Signature Hash Algorithms Length: 12
    Signature Hash Algorithms (6 algorithms)
    Signature Algorithm: rsa_pkcs1_sha384 (0x0501)
    Signature Hash Algorithm Hash: SHA384 (5)
    Signature Hash Algorithm Signature: RSA (1)
    # 省略部分内容
    Distinguished Names Length: 192
    Distinguished Names (192 bytes)
    Distinguished Name: (id-at-commonName=PolarSSL Test CA,
        id-at-organizationName=PolarSSL,id-at-countryName=NL)
    RDNSequence item: 1 item (id-at-countryName=NL)
    RDNSequence item: 1 item (id-at-organizationName=PolarSSL)
    RDNSequence item: 1 item (id-at-commonName=PolarSSL Test CA)
    # 省略部分内容



      从示例样本中可以看到，服务器可解析的证书类型为RSA签名证
书或ECDSA签名证书。服务器可解析的签名算法有6种，其中一种为
        _sha384。服务器可理解的认证机构为PolarSSL Test CA，该
rsa_pkcs1
机构并没有权威性，仅用于mbedtls示例或测试程序中。

6.ServerHelloDone

      服务器已经将所有预计的握手消息发送完毕。




    Handshake Protocol: Server Hello Done
    Handshake Type: Server Hello Done (14)
    Length: 0





7.Certificate

      当客户端收到服务器的CertificateRequest消息后，客户端将会发
送Certificate消息，消息中包含客户端证书清单，该过程与服务器证


    568

## Page 569

    书消息类似。从示例样本中可以看到，客户端证书使用RSA-SHA256
    算法进行签名，长度为905字节。




    Handshake Protocol: Certificate
    Handshake Type: Certificate (11)
    Length: 911
    Certificates Length: 908
    Certificates (908 bytes)
    Certificate Length: 905
    Certificate: 308203853082026da003020102020104300d06092a864886...
    signedCertificate
    algorithmIdentifier (sha256WithRSAEncryption)
    Padding: 0
    encrypted: 2ef23bbf3a36f707a4af14a2f2881bd701df6a12410a262e...





8.ClientKeyExchange

     ClientKeyExchange主要用于传递客户端公钥，结合之前的服务器
证书或ServerKeyExchange，客户端和服务器可同时计算出预备主密
钥。以下样本中可看到ClientKeyExchang消息的部分关键字段，样本
数据客户端公钥长度为65字节（包括1字节压缩提示）。




    Handshake Protocol: Client Key Exchange
    Handshake Type: Client Key Exchange (16)
    Length: 66
    EC Diffie-Hellman Client Params
    Pubkey Length: 65
    Pubkey: 0455c12e67da191767f53046b280a6aa5212940a9b634f1d...





    9.CertificateVerify

    客户端发送CertificateVerify消息，该消息用来证明客户端持有证
    书私钥。消息中将对主密钥和以上握手过程中的所有消息计算消息摘
    要，并使用客户端私钥签名后发送至服务器。示例样本中将使用
    CertificateRequest消息中所包含的rsa _sha384算法计算签名，签
        _pkcs1

        569

## Page 570

    名长度为256字节。



    Handshake Protocol: Certificate Verify
    Handshake Type: Certificate Verify (15)
    Length: 260
    Signature Algorithm: rsa_pkcs1_sha384 (0x0501)
    Signature Hash Algorithm Hash: SHA384 (5)
    Signature Hash Algorithm Signature: RSA (1)
    Signature length: 256
    Signature: 48606a37a0d2b56315e1e7c02e592643acdce24556d1ea24...




    10.ChangeCipherSpec

    客户端发送ChangeCipherSpec消息，表示客户端期望变更密码套
    件。实际上ChangeCipherSpec消息并不是握手协议的一部分，在
    TLS1.3中已将此过程移除。



    TLSv1.2 Record Layer: Change Cipher Spec Protocol: Change Cipher Spec
    Content Type: Change Cipher Spec (20)
    Version: TLS 1.2 (0x0303)
    Length: 1
    Change Cipher Spec Message




11.Finished

      客户端发送Finished消息，表示握手过程已经完成。客户端会向
服务器发送一段验证数据，用于确认客户端和服务器协商出的密码参
数是否一致，在TLS1.2中该验证数据的长度默认为12字节。

      该过程中客户端会使用单向散列函数对以上所有握手消息计算消
息摘要，将主密钥、标签数据及握手消息的消息摘要作为输入，通过
PRF函数派生出12字节的随机数。主密钥的计算及PRF函数会在后续
章节进行描述。PRF计算验证数据表达式如下：

        570

## Page 571

    verify_data = PRF(master_secret, finished_label, Hash(handshake_messages))


    示例样本中使用
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384作为密码套
件，12字节验证数据将使用GCM算法加密认证后发送至服务器。加
密前会在12字节的验证数据头部加入1字节消息类型（20）和3字节消
息长度（000012），这样负载中包含8字节nonce显示部分、16字节密
文和16字节TAG，共40字节。由于该过程会被加密，所以示例样本中
将显示为Encrypted Handshake Message。


    TLSv1.2 Record Layer: Handshake Protocol: Encrypted Handshake Message
    Content Type: Handshake (22)
    Version: TLS 1.2 (0x0303)
    Length: 40
    Handshake Protocol: Encrypted Handshake Message


    12.ChangeCipherSpec

      服务器发送ChangeCipherSpec消息，表示服务器期望切换密码套
    件。


    TLSv1.2 Record Layer: Change Cipher Spec Protocol: Change Cipher Spec
    Content Type: Change Cipher Spec (20)
    Version: TLS 1.2 (0x0303)
    Length: 1
    Change Cipher Spec Message


    13.Finished

      服务器发送Finished消息，表示握手过程已经完成。该过程与客



    571

## Page 572

    户端Finished过程相同，这里不重复描述。




    TLSv1.2 Record Layer: Handshake Protocol: Encrypted Handshake Message
    Content Type: Handshake (22)
    Version: TLS 1.2 (0x0303)
    Length: 40
    Handshake Protocol: Encrypted Handshake Message





14.Application Data

      完成以上握手过程后，服务器和客户端已经拥有后续安全通信所
需要的所有安全参数，如对称密钥和初始化向量IV等，可以通过对称
加密算法和消息认证算法完成后续消息的加密和认证操作。




    TLSv1.2 Record Layer: Application Data Protocol: Application Data
    Content Type: Application Data (23)
    Version: TLS 1.2 (0x0303)
    Length: 58
    Encrypted Application Data: 000000000000000148cf11728ca38ee204aa...










    572

## Page 573

14.7.3 会话恢复

  完整的握手过程非常复杂，为了降低TLS连接时的开销，TLS协
议引入了一个可选的会话缓存功能。如果客户端希望恢复之前的某次
会话，可以将会话ID放入ClientHello消息中，服务器如果同样愿意恢
复会话，则将相同的ID放入ServerHello消息中返回至客户端，然后使
用之前协商的主密钥生成新的会话密钥，再发送密码规格变更协议切
换到加密模式，最后发送Finished消息。客户端收到Finished后进行相
同的操作，完成握手过程。通过缓存会话ID的方法可减少握手过程中
的交互次数。会话恢复过程如图14-10所示。










        图14-10 会话恢复过程

  除了缓存会话ID方式之外，恢复客户端与服务器端会话还可以使
用会话票据（session ticket），会话票据的原理与HTTP Cookie原理非


    573

## Page 574

常相似。服务器把会话相关信息加密之后发送至客户端，客户端将缓
存该会话票据，并在下一次建立会话时发送至服务器。若服务器可以
解密并验证该会话票据，则同意客户端恢复会话。与会话ID相比，会
话票据更适合分布式服务器。










    574

## Page 575

    14.8 TLS密钥交换

    通过密钥交换可获得预备主密钥（pre master secret），预备主密
    钥是主密钥（master secret）的重要组成部分。TLS支持多种密钥交换
    算法，可以支持多种证书类型、公钥算法和密钥生成协议。这些密钥
    协商算法如表14-2所示。

            表14-2 常用密钥协商算法说明










  ·RSA：RSA算法作为一种密钥交换实现标准得到了广泛的支
持，但是它也受到了各种各样的攻击。此外，被认为安全的RSA密钥
至少为2048比特，这大大增加了物联网终端的网络开销。

  ·DH（E）_RSA：（临时）DH密钥协商算法也是一种较为完备


    575

## Page 576

的密钥交换算法，它能够支持前向安全，但是执行速度较慢。
DH（E）算法一般与RSA算法配合使用，DH（E）算法完成密钥交
换，而RSA算法完成身份认证。与RSA算法相似，安全的DH密钥长
度至少为2048比特，这也给物联网终端带来不小的网络开销。

  ·ECDH（E）_ECDSA：ECDH和ECDSA均基于椭圆曲线算法，
ECDH和ECDSA支持前向安全，而且执行速度快。相对于RSA算法和
DH算法，椭圆曲线算法中密钥尺寸较小，所需要的传输开销也更
小，适合物联网应用。










    576

## Page 577

14.8.1 密钥交换算法对比

不同的密钥交换算法也会产生不同的网络传输开销，下面以握手
过程中的ClientKeyChange说明各种密钥交换算法所产生的网络传输
开销，具体内容如表14-3所示。

    表14-3 各种密钥协商算法传输开销










577

## Page 578

14.8.2  ECDHE密钥交换

                                             若要进行ECDHE密钥交换，客户端与服务器必须协商使用相同
的椭圆曲线和签名算法。密码套件的信息并不足以表达椭圆曲线和签
名算法的所有信息，例如
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384，通过该密码
套件，服务器和客户端只能明确采用ECDHE进行密钥交换，并使用
ECDSA进行签名，但是双方并不知道使用哪条椭圆曲线，也无法明
确在计算ECDSA签名时使用哪种单向散列算法。

1.ClientHello扩展选项

为了顺利完成ECDH密钥协商过程，必须借助ClientHello中的扩
展选项。这些扩展选项包括signature_algorithms、supported_groups和
ec_point_formats。

（1）signature    _algorithm

客户端通知服务器自身支持的签名算法和单向散列算法，TLS1.2
协议中支持的签名算法包括RSA和ECDSA，支持的单向散列函数包
括SHA1、SHA256和SHA512等。

enum {
none(0), md5(1), sha1(2), sha224(3), sha256(4), sha384(5),
sha512(6), (255)
} HashAlgorithm;
enum { anonymous(0), rsa(1), dsa(2), ecdsa(3), (255) } SignatureAlgorithm;
struct {

    578

## Page 579

    HashAlgorithm hash;
    SignatureAlgorithm signature;
    } SignatureAndHashAlgorithm;
    SignatureAndHashAlgorithm supported_signature_algorithms<2..2^16-2>;



      常用单向散列算法和签名算法均被编号，例如SHA256编号为4，
SHA512编号为6，ECDSA编号为3。在以下Wireshark抓包数据中，客
户端支持两种组合方式：

      ·单向散列算法为SHA256，签名算法为ECDSA

      ·单向散列算法为SHA224，签名算法为ECDSA



    Extension: signature_algorithms (len=6)
    Type: signature_algorithms (13)
    Length: 6
    Signature Hash Algorithms Length: 4
    Signature Hash Algorithms (2 algorithms)
    Signature Algorithm: (0x0403)
    Signature Hash Algorithm Hash: SHA256 (4)
    Signature Hash Algorithm Signature: ECDSA (3)
    Signature Algorithm: (0x0303)
    Signature Hash Algorithm Hash: SHA224 (3)
    Signature Hash Algorithm Signature: ECDSA (3)




    （2）supported
        _groups

    客户端通知服务器自身支持的椭圆曲线列表。在以下Wireshark
    网络抓包数据中，客户端支持两种椭圆曲线——secp384r1和
    secp256r1。



Extension: supported_groups (len=6)
    Type: supported_groups (10)
    Length: 6
    Supported Groups List Length: 4
    Supported Groups (2 groups)
    Supported Group: secp384r1 (0x0018)
    Supported Group: secp256r1 (0x0017)








    579

## Page 580

    （3）ec
        _point_formats

    客户端通知服务器自身支持的椭圆曲线坐标点类型，一般选择非
    压缩模式。




Extension: ec_point_formats (len=2)
    Type: ec_point_formats (11)
    Length: 2
    EC point formats Length: 1
    Elliptic curves point formats (1)
    EC point format: uncompressed (0)




2.服务器提供公钥

      服务器可通过ServerKeyExchange提供临时公钥，
ServerKeyExchange中包括曲线名称，公钥长度、公钥主体和公钥签
名4部分。在以下Wireshark网络抓包数据中，椭圆曲线为secp256r1，
临时公钥长度为65字节（包括1字节压缩模式）。



    EC Diffie-Hellman Server Params
    Curve Type: named_curve (0x03)
    Named Curve: secp256r1 (0x0017)
    Pubkey Length: 65
    Pubkey: 04d06dc0e8aa471d0693be1a3ae6e47f3c6b39d99077ce3e...
    Signature Algorithm: ecdsa_sha512 (0x0603)
    Signature Hash Algorithm Hash: SHA512 (6)
    Signature Hash Algorithm Signature: ECDSA (3)
    Signature Length: 71
    Signature: 3045022078678b2e143b9355f2f2ab65fe239f757a1fee62...




      临时公钥将使用服务器私钥对其进行签名，此时单向散列算法为
SHA512，被签名消息包括ClientHello中的随机数、ServerHello中的随
机数和ServerKeyExchange中的相关信息。



    struct {
    ECParameters curve_params;


    580

## Page 581

    ECPoint      public;
    } ServerECDHParams;
    struct {
            ServerECDHParams   params;
            Signature          signed_params;
    } ServerKeyExchange;
    SHA(ClientHello.random + ServerHello.random + ServerKeyExchange.params);




      ECDSA签名的结果还需进行ASN.1编码，其中签ECDSA签名结
果r和s均为INTEGER类型，而r和s的组合作为SEQUENCE类型。若
ECDSA的签名结果为64字节，那么经过ASN.1编码的最终长度为
70~72字节。ServerHelloExchange生成过程如图14-11所示。




Ecdsa-Sig-Value ::= SEQUENCE {
     r     INTEGER,
     s      INTEGER
    }










                               581

## Page 582

图14-11   ServerHelloExchange生成过程

3.客户端提供公钥

客户端在ClientKeyExchange中提供客户端公钥，与
ServerKeyExchange不同，ClientKeyExchange中仅包括客户端临时公
钥而不包括临时公钥签名。以下Wireshark网络抓包数据可反映
ClientKeyExchange消息的所有细节。


Handshake Protocol: Client Key Exchange
Handshake Type: Client Key Exchange (16)
Length: 66
EC Diffie-Hellman Client Params
Pubkey Length: 65
Pubkey: 0455c12e67da191767f53046b280a6aa5212940a9b634f1d...





582

## Page 583

4.预备主密钥

     通过ServerKeyExchange和ClientKeyExchange可完成ECDH密钥协
商，即获得ECDH共享参数。服务器提供的ECDH公钥如下：



    # ECDH: X坐标
    d0 6d c0 e8 aa 47 1d 06 93 be 1a 3a e6 e4 7f 3c
    6b 39 d9 90 77 ce 3e ae d8 6e 47 32 5b 21 73 52
    # ECDH: Y坐标
    01 20 5b 3b 55 9b 1a e7 02 53 f6 f3 32 35 ba e8
    38 de f9 3d 2d f8 72 65 4b 0e 1e 76 4c f9 06 63




    客户端提供的ECDH公钥如下：



    # ECDH: X坐标
    55 c1 2e 67 da 19 17 67 f5 30 46 b2 80 a6 aa 52
    12 94 0a 9b 63 4f 1d 58 21 dc 15 50 da cd 7d 43
    # ECDH: Y坐标
    91 83 82 87 72 25 2d 32 e0 21 2a 2b 21 63 f9 ad
    ef d9 ce bf f4 fd c8 d4 17 32 13 5b fd 17 a3 43




    预备主密钥为ECDH共享参数的X坐标，上述握手过程可获得预
    备主密钥如下：




    f2 52 de 01 3a bc 49 36 d2 d5 ad 71 a7 77 ec 71
    3a 6f 6e e8 e0 49 ec b3 1a 05 5d 33 97 89 49 30










    583

## Page 584

14.8.3 ECDH与ECDHE的区别

  ECDH密钥协商与ECDHE密钥协商算法非常相似，ECDH密钥协
商过程中，服务器将提供服务器证书中的ECDH公钥；而ECDHE密钥
协商过程中，服务器将增加一个ServerKeyExchange握手过程，在
ServerKeyExchange握手报文中包含服务器临时公钥，该临时公钥与
服务器证书中的固定公钥并不相同。换句话说，若使用ECDH密钥协
商，服务器每次握手过程都使用相同的ECDH公钥；而使用ECDHE密
钥交换时，服务器每次都提供不同的ECDH公钥。










    584

## Page 585

14.9 TLS密钥计算

  完成密钥协商之后可通过预备主密钥（pre master secret）获得主
密钥（master secret），再通过主密钥派生出对称加密阶段所使用的3
组密钥参数。这3组密钥参数分别为：

  ·客户端和服务器计算消息认证码时所需的密钥MAC Key

  ·客户端和服务器进行对称加密操作时所需的密钥Enc Key

  ·客户端和服务器进行对称加密操作时所需的初始化向量IV

  从预备主密钥到3组关键参数的操作过程如图14-12所示。其中客
户端和服务器随机数来自于握手过程，而预备主密钥（pre master
secret）来自于客户端与服务器的协商结果。

  注意：其中MAC Key和初始化向量IV应根据TLS版本和对称加密
模式按需生成。例如，使用AEAD算法(GCM或CCM)时，并不需要生
成MAC_Key；再如TLS1.1或TLS1.2版本中，对称加密操作时所需的
初始化向量IV由TLS记录层显式提供。初始化向量应保持足够的随机
性且不能被预测，它与主密钥无关。








    585

## Page 586

图14-12 TLS密钥操作过程说明










586

## Page 587

    14.9.1    伪随机数生成函数

    为了将主密钥进行扩展，TLS协议中定义了伪随机数生成函数
    （PRF），该伪随机数生成函数基于SHA256或更高强度的单向散列
    算法，可根据主密钥派生出其他密钥参数。PRF函数实现过程依赖于
    一个名为P_hash的数据扩展函数，P_hash函数使用密钥和种子作为输
    入，可获得任意长度的输出内容。其表达式如下：

    P_hash(secret, seed)= HMAC_hash(secret, A(1) + seed) +
HMAC_hash(secret, A(2) + seed) +
HMAC_hash(secret, A(3) + seed) +     ...

    此处“+”表示字符串拼接过程，其中的A（i）的定义如下：

    A(0)= seed
    A(1)= HMAC_hash(secret, A(0))
    A(i)= HMAC_hash(secret, A(i-1))

    P_hash函数的计算过程如图14-13所示。










              587

## Page 588

    图14-13   P_hash计算过程

假设P_hash函数使用HMAC-SHA256算法，单向散列函数
SHA256算法的输出长度为32字节，那么单次运行P_hash函数可输出
32字节伪随机数。若期望得到80字节的伪随机数，可以通过定义
A（3）使得P_hash函数重复运行3次，从而得到96字节的输出数据，
然后丢弃最后16字节数据。

                   PRF函数的实现基于P_hash函数，其中label为标识标签，其表达
式如下：

PRF(secret, label, seed)= P_hash(secret, label + seed)

    588

## Page 589

14.9.2 主密钥计算

主密钥（master secret）是由预备主密钥（pre master secret）和随
机数生成，使用上文提到的PRF算法进行推算，其计算过程如下：

master_secret = PRF (pre_master_secret, "master secret",
           ClientHello.random + ServerHello.random)
           [0..47];

此处“+”号表示字符拼接，其中：

·master_secret为主密钥，长度固定为48字节。

·pre_master_secret为预备主密钥，预备主密钥的生成方法及长度
由密钥协商算法决定。

·ClientHello.random为ClientHello握手过程中客户端发送到服务器
的32字节随机数。

·ServerHello.random为ServerHello握手过程中服务器发送到客户
端的32字节随机数。

主密钥的长度为固定的48字节，预备主密钥的生成方法及长度由
密钥协商算法决定，其计算过程依赖于密钥协商算法。

·若密钥协商算法为RSA算法，预备主密钥的长度为48字节。

·若密钥协商算法是DH算法，预备主密钥的长度由DH公钥参数

               589

## Page 590

决定，一般为2048比特（256字节）或3072比特（384字节）。

  ·若密钥协商算法为ECDH算法，预备主密钥的长度由椭圆曲线参
数决定：若椭圆曲线为secp256r1，则预备主密钥长度为32字节；若
椭圆曲线为secp384r1，则预备主密钥的长度为48字节。

  ·若密钥协商算法为PSK（预分享密钥），那么预备主密钥的长
度与PSK的长度相关。










    590

## Page 591

14.9.3 KeyBlock计算

通过主密钥可以完成KeyBlock的计算，其计算表达式如下：


key_block = PRF(master_secret,
"key expansion",
SecurityParameters.server_random +
SecurityParameters.client_random);


其中：

·key_block为最终输出结果；

·master_secret为主密钥；

·“key expansion”为扩展标签；

·SecurityParameters.server_random为客户端收到来自服务器的32
字节随机数；

·SecurityParameters.client_random为服务器收到来自客户端的32
字节随机数。

key_block将派生出客户端和服务器MAC Key（按需生成）、客
户端和服务器Enc Key，以及客户端与服务器初始化向量IV（按需生
成）。


client_write_MAC_key[SecurityParameters.mac_key_length]
server_write_MAC_key[SecurityParameters.mac_key_length]
client_write_key[SecurityParameters.enc_key_length]

591

## Page 592

    server_write_key[SecurityParameters.enc_key_length]
    client_write_IV[SecurityParameters.fixed_iv_length]
    server_write_IV[SecurityParameters.fixed_iv_length]


    enc_key_length和fixed_iv_length与对称加密算法的关系如表14-4
所示，mac_key_length与HMAC算法的关系如表14-5所示。

       表14-4 enc_key_length和fixed_iv_length与算法的关系







    表14-5 mac_key_length与算法的关系




    若TLS密码套件为TLS-ECDH-ECDSA-AES-128-SHA256，那么
MAC Key长度为32字节，Enc Key长度为16字节，IV长度为16字节；
若TLS密码套件为TLS-ECDH-ECDSA-AES-256-SHA384，那么MAC
Key长度为64字节，Enc Key长度为32字节，IV长度为16字节；若TLS
密码套件为TLS-ECDH-ECDSA-AES-128-GCM，那么MAC Key长度
为0字节，Enc Key长度为16字节，IV长度为4字节。










    592

## Page 593

    14.9.4 密钥计算示例

    本节将通过示例描述密钥计算过程。假设密码套件为TLS-
    ECDH-ECDSA-WITH-AES-128-CBC-SHA256，椭圆曲线为
    secp256r1。

    1.主密钥计算

    经过ECDH密钥协商之后，客户端和服务器将获得一个共享密
钥，该共享密钥包括X坐标和Y坐标，而pre_master_key为ECDH共享
密钥的X坐标，所以pre_master_key的长度为32字节。具体内容如
下：


    40 1b e1 29 b9 dc c3 c3 03 f8 91 00 87 d2 00 9c
    ed 2c 18 8d 92 3a c5 4e 42 e9 ee 22 d2 18 f3 00


    主密钥可通过pre_master_secret、客户端随机数和服务器随机数
经过PRF伪随机数算法计算获得，最终客户端和服务器将获得长度为
48字节的主密钥master_secret。


    # master_secret计算过程
    master_secret = PRF(pre_master_secret, "master secret",
    ClientHello.random + ServerHello.random)
    [0..47];
    # master_secret 计算结果
    dc 6b 4d b1 83 29 88 c2 24 dc 88 40 af c4 87 24
    65 8c 07 cd 51 3c 38 f9 d5 03 0c 5d 5a e8 e9 b7
    06 32 53 31 19 60 d0 e7 3e d1 ed 5b d8 18 92 cc





    593

## Page 594

2.KeyBlock计算

默认情况下，客户端和服务器端会生成一个256字节长度的
key_block数组。



# key_bock计算方法
key_block = PRF(SecurityParameters.master_secret,
        "key expansion",
        SecurityParameters.server_random +
        SecurityParameters.client_random);
# 生成内容
fd 94 2f 73 24 4a 57 8e fb 56 c8 4f fd 34 7a 4b
32 1d 73 ef b9 cd 8e 04 c6 80 5a eb b3 c5 10 20
8c 51 3b c1 c7 22 74 26 60 63 db f8 39 e3 a8 da
# 省略部分内容
16 bc 46 7e 2d ec 9d a7 c6 d3 4a 94 a7 36 d6 97
fa e0 d2 7b 18 f3 74 85 c1 59 bd ec 0e da e7 c5
af 59 2a 88 00 aa 5a f6 fc aa 53 6f 61 5f fa 95




此时TLS密码套件为TLS-ECDH-ECDSA-WITH-AES-128-CBC-
SHA256，那么key_block数组将会被依次分割为：

·客户端32字节MAC Key

·服务器32字节MAC Key

·客户端16字节Enc Key

·服务器16字节Enc Key

·客户端16字节初始化向量IV（生成但未使用）

·服务器16字节初始化向量IV（生成但未使用）





        594

## Page 595

14.10 对称加密

  TLS协议可使用多种方法加密应用数据，目前应用最广泛的加密
算法为AES算法。TLS至少支持3种类型加密算法，分别是序列加
密、分组加密和认证加密。本节将重点介绍分组加密和认证加密。










    595

## Page 596

14.10.1 分组加密

   分组加密模式不但与密钥协商过程所获得的3组密钥参数有关，
还与以下内容有关：

   ·序列号，该序列号的长度为8字节，由客户端和服务器在TLS会
话过程中各自保存；

   ·TLS记录首部，包括记录子协议类型（type）、TLS版本
（version）、记录层长度指示（length）；

   ·填充，确保加密前数据长度是分组长度的整数倍，如AES算法
的分组长度为16字节；

   ·初始化向量IV，生成一个长度与对称加密算法分组长度相同且
不可预期的初始化向量，该向量IV将与密文一同被发送。

   分组加密模式中加密和认证部分有两种组合方式，分别为
mac_then_encrypt和encrypt_then_mac。mac_then_encrypt表示先计算
消息认证码后加密，mac_then_encrypt由RFC5246规定，它是TLS默认
的分组加密模式。虽然这种模式被广泛应用，但是也带来不少问题。
而encrypt_then_mac表示先加密后计算消息认证码，encrypt_then_mac
由RFC7366定义。这种补充模式通过ClientHello握手协议中增加扩展
选项encrypt_then_mac方式实现，使用该模式前客户端和服务器需通


    596

## Page 597

过协商确定，否则依然使用mac_then_encrypt这种传统模式。

    1.mac_then_encrypt

   在mac_then_encrypt模式中，消息认证码由序列号、TLS记录首
部和明文计算得到。具体计算过程如下：

    MAC(MAC_write_key, seq_num +
              TLSCipherText.type +
              TLSCipherText.version +
              TLSCipherText.length +
              TLSCipherText.fragment);

    其中，“+”表示字符串拼接操作。

    ·MAC表示消息认证码计算方法，计算消息认证码方法由TLS密
    码套件决定，例如HMAC-SHA256或HMAC-SHA512；

    ·MAC_write_key由主密钥派生得到；

    ·seq_num表示序列号；

    ·type表示TLS握手子协议类型；

    ·length表示密文长度；

    ·fragment表示密文整体。

    被加密的应用数据由初始化向量IV、密文、消息认证码、填充和
    填充长度组成。具体结构如下：


              597

## Page 598

struct {
opaque IV[SecurityParameters.record_iv_length];
block-ciphered struct {
        opaque content[TLSCipherText.length];
        opaque MAC[SecurityParameters.mac_length];
        uint8 padding[GenericBlockCipher.padding_length];
        uint8 padding_length;
};
} GenericBlockCipher;




其中：

·IV表示初始化向量，是一个长度与分组长度相同的随机数序
列，该随机数序列不能被预测，一般情况下，可通过伪随机数生成器
获得该向量，向量的长度一般为16字节；

·content表示主要内容，也就是密文；

·MAC表示消息认证码，一般情况下消息认证码的长度为32字节
或64字节；

·padding表示填充；

·padding_length表示填充长度。

计算消息认证码和加密的整体过程如图14-14所示。










        598

## Page 599

      图14-14     mac_then_encrypt整体过程

    2.encrypt_then_mac

      encrypt_then_mac模式与之前的模式稍有不同，具体计算方法如
    下：


MAC(MAC_write_key, seq_num +
    TLSCipherText.type +
    TLSCipherText.version +
    TLSCipherText.length +
    IV +
    ENC(content + padding + padding_length));


    其中“+”表示字符串拼接操作。

    ·MAC表示消息认证码计算方法，计算消息认证码方法由TLS密
    码套件决定，例如HMAC-SHA256或HMAC-SHA512；

    ·MAC_write_key由主密钥派生得到；



    599

## Page 600

    ·seq_num表示序列号；

    ·type表示TLS握手子协议类型；

    ·length表示密文长度；

    ·IV表示不可预测的初始化向量；

    ·ENC（content+padding+padding_length）表示密文整体，密文由
    明文经过填充操作之后加密获得。

    encrypt_then_mac和加密的整体过程如图14-15所示。










        图14-15 encrypt_then_mac整体过程

    3.填充过程

   无论是mac_then_encrypt还是encrypt_then_mac模式都包含填充操
作，TLS协议规定的填充操作分为填充内容和填充长度指示两部分。


    600

## Page 601

以encrypt_then_mac为例，若分组长度为16字节，明文长度为34字
节，加上填充长度域后总长度为35字节，需填充13字节至48字节才可
满足分组长度整数倍的要求。此时填充内容为13字节“13”，填充长度
域内容为“13”。填充过程如图14-16所示。








        图14-16 分组加密填充过程

  TLS填充过程与PKCS7标准并不相同，PKCS7标准中并没有专门
的填充长度域，而TLS填充过程中最后1字节总是填充长度域。若按
照PKCS7标准进行填充操作，应填充14字节“14”。










    601

## Page 602

14.10.2 认证加密


认证加密将加密过程和验证完整性过程合二为一，它的全名为使
用关联数据的认证加密（authenticated encryption with associated
data，AEAD）。常见的AEAD算法包括AES-CCM和AES-GCM，
AEAD算法不需要填充。相比于分组加密模式，认证加密模式的结构
要简单一些。被加密的应用数据的具体结构如下：

struct {
opaque nonce_explicit[SecurityParameters.record_iv_length];
aead-ciphered struct {
    opaque content[TLSCipherText.length];
};
} GenericAEADCipher;

其中：

·nonce  _explicit为一次性整数，该部分与被加密的数据一同被发
送，一般情况下该值与序列号seq_num相等；

·content为被加密的内容，包括密文和消息认证码。

密文由一次性整数、明文和附加数据计算得到。计算公式如下：

TLSCipherText.fragment = AEAD-Encrypt(write_key, nonce, plaintext, additional_data)

其中：

·write  _key表示对称加密密钥，该密钥来自于Key Block。

    602

## Page 603

·nonce为一次性整数，该一次性整数分为两部分，一部分为4字
节salt和8字节nonce_explicit。4字节salt取自Key Block初始化向量IV部
分；8字节nonce_explicit一般为序列号seq_num。

struct {
opaque salt[4];
opaque nonce_explicit[8];
} GCMNonce;

·additional_data为附加数据，一般由序列号、TLS记录子协议类
型、TLS版本信息和密文长度拼接而成。例如，序列号为00 00 00 00
00 00 00 01（HEX格式），TLS记录子协议类型为23（0x17），密文
长度为34，那么附加数据为“00 00 00 00 00 00 00 01 17 03 03 00 22”，
共13字节。

additional_data = seq_num + TLSCipherText.type +
    TLSCipherText.version + TLSCipherText.length;

认证加密的整体流程如图14-17所示。










603

## Page 604

图14-17     认证加密整体流程

GCM模式中，消息认证码的长度为固定的16字节，而CCM模式
中，消息认证码的长度可以为8字节或16字节，也就是说CCM模式的
消息认证码长度可能更短。










604

## Page 605

    14.10.3 对称加密示例

    假设客户端将向服务器发送HTTP请求，请求内容为34字节（包
    括3处回车换行）。具体内容如下：

    GET / HTTP/1.0\r\n
    Extra-header:\r\n
    \r\n


1.AES-CBC mac_then_encrypt

  若客户端与服务器协商使用“先计算消息认证码后加密”方式，密
码套件为TLS-ECDHE-ECDSA-WITH-AES-128-CBC-SHA256。根据
TLS协议CBC分组加密的具体过程，可分为计算消息认证码、明文填
充和对称加密3步，该过程与“先加密后计算消息认证码”不同。

  1）使用HMAC-SHA256计算消息认证码，消息认证码的长度为
32字节；

  2）此时明文的长度为34字节，消息认证码的长度为32字节，合
计66字节，由于分组长度为16字节，需填充14字节，使总长度为80字
节；

  3）使用AES128-CBC模式对填充后的密文进行加密；

  4）加上16字节初始化向量，最终结果为96字节。


    605

## Page 606

2.AES-CBC encrypt_then_mac

客户端与服务器协商使用“先加密后计算消息认证码”方式，密码
套件为TLS-ECDHE-ECDSA-WITH-AES-128-CBC-SHA256。根据TLS
协议CBC分组加密的具体过程，可分为明文填充、对称加密和计算消
息认证码3步。

1）此时明文长度为34字节，又由于分组长度为16字节，所以需
填充14字节，填充后总长度为48字节；

2）使用AES128-CBC模式对填充后的明文进行加密，加密结果
的长度为48字节；

3）最后使用HMAC-SHA256计算消息认证码，消息认证码的长
度为32字节；密文长度为48字节，消息认证码长度为32字节，初始化
向量IV为16字节，合计96字节。

3.AES-GCM

客户端与服务器协商使用密码套件为TLS-ECDHE-ECDSA-
WITH-AES-128-GCM-SHA256，根据TLS协议GCM分组加密的具体
过程，大致可分为组装附加数据、加密并计算消息认证码两个阶段。

·一次性整数显示部分为8字节；

·密文与明文的长度保持一致，同为34字节；


606

## Page 607

·消息认证码的长度为16字节；

·合计58字节。

4.AES-CCM模式

客户端与服务器协商使用密码套件为TLS-ECDHE-ECDSA-
WITH-AES-CCM-8，根据TLS协议CCM分组加密的具体过程，大致
可分为组装附加数据、加密并计算消息认证两个阶段。

·一次性整数显示部分为8字节；

·密文与明文的长度保持一致，同为34字节；

·消息认证码的长度为8字节；

·合计50字节。










607

## Page 608

14.10.4 对称加密结果长度对比

  同样长度的明文经过不同的加密操作后可获得不同长度的密文，
此处的密文包括消息认证码。无论采用mac_then_encrypt模式还是
encrypt_then_mac模式，AES-CBC模式把34字节明文加密为80字节密
文（包括消息认证码），而AES-GCM由于不存在填充操作，把34字
节明文加密为58字节密文（包括消息认证码）。一般情况下，AES-
GCM模式和AES-CCM模式的消息认证码长度均为16字节，但是CCM
模式可以把消息认证码的长度减小为8字节，这样就把34字节明文加
密为50字节密文（包括消息认证码）。对称加密模式结果长度对比如
表14-6所示。

        表14-6 对称加密模式结果长度对比






  通过表146可以看出，AES-GCM/CCM模式比AES-CBC模式具有
更小的传输消耗。AES-GCM/CCM模式更适合物联网应用。另外，
AES-CCM模式具有更短的消息认证码，可获得最高的传输效率。







    608

## Page 609

14.11 mbedtls TLS应用工具

    本节将重点介绍ssl_client2和ssl_server2工具的使用方法。
ssl_server2是一个综合性TLS服务器示例应用工具，该工具的实现代
码为{mbedtls代码仓库}/programs/ssl/ssl_server2.c。ssl_server2支持多
种密码套件，可以通过命令行参数指定根证书文件、PSK或强制密码
套件等。ssl_client2是与ssl_server2相对应的TLS客户端工具，该工具
的实现代码为{mbedtls代码仓库}/programs/ssl/ssl_client.c。ssl_client2
和ssl_server2参数较为相似，这些参数的具体说明如表14-7所示。

        表14-7 ssl_client2和ssl_server2主要参数说明










    609

## Page 610

610

## Page 611

611

## Page 612

14.11.1 基础示例说明

  下面通过一个基础示例说明ssl_server2和ssl_client2工具的使用方
法。

  1）新建第1个控制台，在控制台中启动TLS服务器；

  2）打开第2个控制台，在控制器中通过tcpdump工具抓取网络分
组数据，并保存为pcap文件，被抓取的网络数据可通过Wireshark进行
进一步分析；

  3）打开第3个控制台，在控制台中启动TLS客户端；

  4）TLS客户端与TLS服务器端完成握手之后，TLS客户端将向
TLS服务器发送一个HTTP GET请求，TLS服务器将返回经过协商的
密码套件信息；

  5）TLS客户端和服务器端运行时，将在控制台输出TLS协议版
本、证书信息以及密码套件等信息。

  ssl_client2和ssl_server2基础示例流程如图14-18所示。









    612

## Page 613

图14-18 ssl_client2和ssl_server2基础示例流程










    613

## Page 614

14.11.2 启动ssl
    _server2

新建第1个控制台，在控制台中启动TLS服务器，等待客户端连
接，并通过控制台查看输出。




$ ssl_server2
# 输出内容
. Seeding the random number generator... ok
. Loading the CA root certificate ... ok (0 skipped)
. Loading the server cert. and key... ok
. Bind on tcp://*:4433/ ...  ok
. Setting up the SSL/TLS structure... ok
. Waiting for a remote connection ...
# 当有TLS连接后，输出情况
. Performing the SSL/TLS handshake... ok
[ Protocol is TLSv1.2 ]
[ Ciphersuite is TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384 ]
[ Record expansion is 29 ]
[ Maximum fragment length is 16384 ]
. Verifying peer X.509 certificate... failed
! Certificate verification was skipped
< Read from client: 34 bytes read
GET / HTTP/1.0
Extra-header:
> Write to client: 152 bytes written in 1 fragments
HTTP/1.0 200 OK
Content-Type: text/html
<h2>mbed TLS Test Server</h2>
<p>Successful connection using: TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384</p>
. Closing the connection... done










614

## Page 615

14.11.3 抓取网络数据

新建第2个控制台，通过tcpdump工具抓取网络数据。通过-i参数
指定网卡为loopback，通过-w指定将抓包结果保存到tls.pcap文件中。

$ sudo tcpdump –i lo –w tls.pcap tcp port 4433










615

## Page 616

        启动ssl
    14.11.4    _client2

    新建第3个控制台，在控制台中启动TLS客户端，并强制客户端
    密钥套件为TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384。



    $ ssl_client2 force_ciphersuite=TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384
    # 输出内容
    . Seeding the random number generator... ok
    . Loading the CA root certificate ... ok (0 skipped)
    . Loading the client cert. and key... ok
    . Connecting to tcp/localhost/4433... ok
    . Setting up the SSL/TLS structure... ok
    . Performing the SSL/TLS handshake... ok
    [ Protocol is TLSv1.2 ]
    [ Ciphersuite is TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384 ]
    [ Record expansion is 29 ]
[ Maximum fragment length is 16384 ]
    . Verifying peer X.509 certificate... ok
    . Peer certificate information    ...
    cert. version          : 3
    serial number          : 09
    issuer name            : C=NL, O=PolarSSL, CN=Polarssl Test EC CA
    subject name           : C=NL, O=PolarSSL, CN=localhost
    issued on              : 2013-09-24 15:52:04
    expires on             : 2023-09-22 15:52:04
    signed using           : ECDSA with SHA256
    EC key size            : 256 bits
    basic constraints : CA=false
    > Write to server: 34 bytes written in 1 fragments
    GET / HTTP/1.0
    Extra-header:
    < Read from server: 152 bytes read
    HTTP/1.0 200 OK
    Content-Type: text/html
    <h2>mbed TLS Test Server</h2>
    <p>Successful connection using: TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384</p>
    . Closing the connection... done










                           616

## Page 617

14.11.5 分析网络数据

   停止tcpdump工具，通过Wireshark打开网络分析数据，在
Wireshark过滤条件中输入“ssl”。通过Wireshark可展现TLS客户端与
TLS服务器端握手的详细过程，如图14-19所示。










       图14-19 通过Wireshark展现TLS网络分组数据

   由于ssl_server2和ssl_client2的默认通信端口号为4433，而TLS默
认端口号为443，两者存在区别。若Wireshark使用默认TLS配置，那
么Wireshark将认为在4433端口的网络通信报文为普通TCP报文。为了
更好地展现TLS协议细节，建议把4433端口加入Wireshark默认端口号
中。在编辑菜单栏中选择【首选项】，在“首选项”设置界面左侧协议


    617

## Page 618

列表中选中【HTTP】，在HTTP设置界面中把4433端口增加到
SSL/TLS默认端口中。Wireshark首选项修改过程如图14-20所示。










618

## Page 619

图14-20 增加4433端口到SSL/TLS默认端口中










619

## Page 620

14.12 构建TLS服务器

   本节将描述如何使用OpenSSL s_server工具构建TLS服务器、
s_server是一个综合性TLS/DTLS服务程序，可通过man s_server查看
s_server的使用方法，也可回顾第1章中有关OpenSSL简介。TLS服务
器的构建过程主要分为生成证书、编写HTML页面和启动s_server三
部分。

   注意：为了便于读者使用，本书已经在域名为iotwuxi.org服务中
部署了TLS服务，该服务的端口号为442。后续TLS客户端示例中默认
与该服务器进行连接，本节主要描述TLS服务器的构建过程。需要注
意的是，本节TLS服务器的部署方式仅用于TLS客户端的测试，实际
应用中并不建议该部署方式。










    620

## Page 621

14.12.1 生成证书

  真实业务场景中，服务器证书一般由具有权威性的CA机构签
发，在某些测试场景中也可使用自签名证书。本节将构建一个名为
iotwuxi-Root-CA虚拟CA机构，通过这个虚拟CA为iotwuxi.org签发服
务器证书。证书的签发可以使用OpenSSL或mbedtls所提供的命令行工
具完成。本节将使用mbedtls提供的命令行工具完成证书的签发，最
终生成文件如表14-8所示的。

        表14-8 服务器相关文件说明










1.参数选择

  生成根证书及服务器证书前，需要详细了解嵌入式TLS客户端所
支持的单向散列算法及签名算法，以避免嵌入式客户端由于算法缺失
而无法完成服务器证书的验证。另外，考虑到嵌入式客户端RAM和
Flash空间有限，本节将选择ECDSA签名算法，该签名算法比RSA签
名算法所生成的证书尺寸小。所以证书签发过程所选择的密钥对类型


    621

## Page 622

为椭圆曲线，单向散列算法算法为SHA-256，签名算法为ECDSA，
椭圆曲线参数为secp256r1。

2.生成根证书

   在签发服务器证书之前，首先完成根证书的签发，根证书由上面
提到的iotwuxi-Root-CA虚拟机构签发。在生成根证书之前，需要生成
根证书所对应的密钥对文件（ca_privkey.pem），生成过程如下：

  $ gen_key type=ec ec_curve=secp256r1 filename=ca_privkey.pem format=pem

   完成密钥对生成后可生成自签名根证书，生成过程如下：

  $ cert_write selfsign=1 issuer_key=ca_privkey.pem md=SHA256
  issuer_name=CN="iotwuxi-Root-CA",O="iotwuxi",C=CN output_file=ca_cert.pem
  not_before=20180101000000 not_after=20231231115959 is_ca=1 serial=16011


    3.导出根证书

   在客户端建立TLS连接前，需要将CA根证书安全导入TLS客户端
中。为了减少TLS客户端的RAM或FLASH空间消耗，本节将PEM格
式的证书文件转换为DEM格式，并将其写入名为ca_cert_der[]的数组
中，该数组将保存在名为ca_cert.h的头文件中，以便TLS客户端使
用。

    $ pem2der filename=ca_cert.pem output_file=ca_cert.der
    $ xxd -g 1 -i -u ca_cert.der >> "ca_cert.h"



    622

## Page 623

4.生成服务器证书

  生成服务器证书过程与生成CA根证书过程类似，首先需要生成
服务器密钥对文件（srv_privkey.pem），其中公钥会被写入服务器证
书中，私钥由服务器保管。服务器密钥对生成过程如下：

$ gen_key type=ec ec_curve="secp256r1" filename=srv_privkey.pem format=pem

  与CA根证书生成过程稍有不同，在服务器证书生成前需生成服
务器证书签名请求（srv_cert.req）。服务器证书签名请求生成过程如
下：

$ cert_req filename=srv_privkey.pem output_file=srv_cert.req
subject_name=CN="iotwuxi.org",O="iotwuxi",C=CN

  最后，通过服务器证书签名请求完成服务器证书的签发，得到名
为srv_cert.pem的服务器证书。服务器证书生成过程如下：

$ cert_write request_file=srv_cert.req md=SHA256 issuer_key=ca_privkey.pem
issuer_name=CN="iotwuxi-Root-CA",O="iotwuxi",C=CN output_file=srv_cert.pem
not_before=20180101000000 not_after=20191231115959 serial=16012

  注意：为了便于使用，代码仓库中提供了用mbedtls工具编写的
证书生成的脚本，脚本文件为scripts/cert.sh。该脚本会自动生成CA根
证书和服务器证书，并将CA根证书以DER格式导出到数组文件中，
生成文件会保存在certs文件夹下。读者在实际使用中可根据实际情况
修改脚本头部的参数，如组织、CA机构名称以及椭圆曲线参数等。



623

## Page 624

14.12.2 编写HTML页面

TLS服务器除了提供TLS服务外，还将提供一个名为index.html页
面。index.html页面如下：



<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>TLS Server</title>
</head>
<body>
<h1>This is TLS Server</h1>
</body>
</html>










624

## Page 625

14.12.3 启动s
    _server

完成上述准备工作后可使用OpenSSL s_server工具启动TLS服务
器。TLS服务器选择ECDHE-ECDSA-AES256-GCM-SHA384作为密码
套件，并通过参数指定端口号、证书位置等信息。启动过程如下：


$ openssl s_server --state -cert srv_cert.pem -key srv_privkey.pem
-CAfile ca_cert.pem -port 442 -cipher ECDHE-ECDSA-AES256-GCM-SHA384 -WWW ./
# 输出内容
Using default temp DH parameters
ACCEPT










625

## Page 626

    14.12.4 验证服务器

    完成TLS服务器部署后，可通过OpenSSL s_client工具验证TLS服
    务部署是否成功，iotwuxi.org对应的CA根证书位于14_tls文件夹下。
    TLS服务器验证过程如下：



    $ cd 14_tls
    $ openssl s_client --connect iotwuxi.org:442 -CAfile ca_cert.pem
    # 输出内容
    CONNECTED(00000005)
    depth=1 CN = iotwuxi-Root-CA, O = iotwuxi, C = CN
    verify return:1
    depth=0 CN = iotwuxi.org, O = iotwuxi, C = CN
    verify return:1
    ---
    Certificate chain
    0 s:CN = iotwuxi.org, O = iotwuxi, C = CN
      i:CN = iotwuxi-Root-CA, O = iotwuxi, C = CN
    1 s:CN = iotwuxi-Root-CA, O = iotwuxi, C = CN
      i:CN = iotwuxi-Root-CA, O = iotwuxi, C = CN
    ---
    # 省略服务器证书内容
    subject=CN = iotwuxi.org, O = iotwuxi, C = CN
    issuer=CN = iotwuxi-Root-CA, O = iotwuxi, C = CN
    ---
    # 省略部分内容
    New, TLSv1.2, Cipher is ECDHE-ECDSA-AES256-GCM-SHA384
    Server public key is 256 bit
    Secure Renegotiation IS supported
    Compression: NONE
    Expansion: NONE
    No ALPN negotiated
    SSL-Session:
       Protocol : TLSv1.2
       Cipher   : ECDHE-ECDSA-AES256-GCM-SHA384
       # 省略部分输出内容
    ---




      从输出信息中可以看到服务器证书及密码套件等信息。后续章节
将介绍使用nucleo_f429平台作为TLS客户端的方法，并详细描述
mbedtls相关配置及mbedtls TLS相关接口的使用方法。





       626

## Page 627

14.13 构建TLS客户端

  本节基础示例将介绍如何在嵌入式终端中实现TLS客户端。示例
中访问的TLS服务器部署于阿里云主机中，该服务器的域名为
iotwuxi.org，IP地址为139.196.187.107，TLS服务端口号为442。为了
完成对服务器身份的认证，TLS客户端代码中存放了用于验证服务器
证书的CA根证书。在TLS握手成功后，TLS客户端将发送GET请求来
获取一个简单的HTML页面。TLS示例工作流程如图14-21所示。

  示例代码中将使用TLS-ECDHE-ECDSA-AES256-GCM-SHA384
作为密码套件，握手过程中会对服务器身份进行认证，服务器证书认
证失败则会终止握手过程。TLS示例握手过程如图14-22所示。










    图14-21 TLS示例工作流程






    627

## Page 628

    图14-22 TLS示例握手过程

           注意：由于篇幅限制，示例代码中只给出部分函数，完整代码见
本书GitHub代码仓库。本节示例位于14_tls文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。










628

## Page 629

14.13.1 配置文件

示例代码所使用的mbedtls配置文件参考自NSA Suite B规范，配
置文件中对RAM空间消耗及FLASH空间消耗进行了优化，配置文件
中的宏定义描述如表14-9所示。

    表14-9 suite-b.h配置文件宏定义描述










629

## Page 630

630

## Page 631

14.13.2 示例代码

      TLS示例中将对服务器身份进行认证，当服务器证书验证失败时
则终止握手过程。为了完成对服务器证书的验证，需要完成根证书的
配置，并通过mbedtls_ssl_set_hostname接口正确设置hostname（示例
中为iotwuxi.org）。完成证书相关的配置后，还需要通过
mbedtls_ssl_set_bio接口设置发送和接收处理函数。TLS示例代码如代
码清单14-1所示。

      代码清单14-1 TLS示例



    // 省略头文件及中间代码
    #define SERVER_PORT      "iotwuxi.org"
    #define SERVER_PORT      "442"
    #define HOSTNAME         "iotwuxi.org"
    #define GET_REQUEST      "GET /index.html HTTP/1.0\r\n\r\n"
    int main(void)
    {
     int ret, len = 0;
     uint8_t buf[256];
     const char *pers = "tls_client";
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     mbedtls_platform_set_printf(printf);
     mbedtls_platform_set_snprintf(snprintf);
     mbedtls_x509_crt ca;
     mbedtls_net_context ctx;
     mbedtls_ssl_context ssl;
     mbedtls_ssl_config conf;
     mbedtls_net_init(&ctx);
     mbedtls_ssl_init(&ssl);
     mbedtls_ssl_config_init(&conf);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_x509_crt_init(&ca);
     mbedtls_printf("\n tls client use %s board.\n", CONFIG_BOARD);
     mbedtls_printf("\n  . Seeding the random number generator ... ");
     mbedtls_entropy_init(&entropy);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
         MBEDTLS_ENTROPY_MAX_GATHER, MBEDTLS_ENTROPY_SOURCE_STRONG);
     mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                                 (const uint8_t *)pers, strlen(pers));
     mbedtls_printf(" ok\n  . Setting up the SSL/TLS structure ... ");
     mbedtls_ssl_config_defaults(&conf, MBEDTLS_SSL_IS_CLIENT,
         MBEDTLS_SSL_TRANSPORT_STREAM, MBEDTLS_SSL_PRESET_DEFAULT);
     mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);


                             631

## Page 632

    mbedtls_x509_crt_parse_der(&ca, ca_cert_der, ca_cert_der_len);
    mbedtls_ssl_conf_ca_chain(&conf, &ca, NULL);
    mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    mbedtls_ssl_setup(&ssl, &conf);
    mbedtls_ssl_set_hostname(&ssl, HOSTNAME);
    mbedtls_printf(" ok\n . Connecting to %s:%s...", SERVER_ADDR, SERVER_PORT);
    mbedtls_net_connect( &ctx, SERVER_ADDR, SERVER_PORT, MBEDTLS_NET_PROTO_TCP );
    mbedtls_ssl_set_bio( &ssl, &ctx, mbedtls_net_send, mbedtls_net_recv, NULL );
    mbedtls_printf(" ok\n . Performing the SSL/TLS handshake ...");
    while ((ret = mbedtls_ssl_handshake(&ssl)) != 0)
    {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE)
        {
        mbedtls_printf(" failed\n ! -0x%x\n\n", -ret);
        goto cleanup;
        }
    }
    mbedtls_printf(" ok\n > Write to server:");
    mbedtls_ssl_write(&ssl, (const uint8_t *)GET_REQUEST, strlen(GET_REQUEST));
    len = ret;
    mbedtls_printf( " %d bytes written\n\n%s\n\n", len, GET_REQUEST);
    mbedtls_printf(" > Read from server:");
    len = sizeof(buf) - 1;
    memset(buf, 0x00, sizeof(buf));
    do {
        mbedtls_ssl_read(&ssl, buf, len);
    } while (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE);
    len = ret;
    mbedtls_printf( " %d bytes read\n\n\n%s\n\n", len, buf);
    mbedtls_ssl_close_notify(&ssl);
    mbedtls_printf(" ok\n . Closing the connection ... done\n");
cleanup:
    mbedtls_net_free(&ctx);
    mbedtls_ssl_free(&ssl);
    mbedtls_ssl_config_free(&conf);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    mbedtls_x509_crt_free(&ca);
    return 0;
}



    示例代码相关接口描述如表14-10所示

    表14-10 TLS示例代码相关接口描述










    632

## Page 633

633

## Page 634

    14.13.3    代码说明

    1.配置随机数

    TLS握手过程中需要使用随机数接口，首先需要完成伪随机数的
    配置工作，该过程包括熵源接口添加、熵源属性设置及通过个性化字
    符串更新种子。伪随机数生成器配置过程的详细描述可回顾7.6.2节。

    2.配置SSL选项

    （1）配置默认选项

   为了完成TLS握手，首先需要通过mbedtls_ssl_config_defaults接
口完成SSL默认选项的配置，该函数需要输入mbedtls_ssl_config结构
体、终端类型、传输协议，以及是否预设配置选项，配置信息保存在
mbedtls_ssl_config结构体中。其中终端类型分为
    MBEDTLS_SSL_IS_CLIENT和MBEDTLS_SSL_IS           _SERVER两种，客
    户端为MBEDTLS _SSL_IS                  _CLIENT。传输协议分为TCP和UDP两
种，其中MBEDTLS_SSL_TRANSPORT_STREAM对应TLS协议，而
    MBEDTLS_SSL_TRANSPORT                _DATAGRAM对应DTLS协议。预设置
    配置选项可设置一些默认的配置参数，如版本号、密码套件等。
    mbedtls_ssl_config接口原型如下：

    int mbedtls_ssl_config_defaults( mbedtls_ssl_config *conf,
                    int endpoint, int transport, int preset );

        634

## Page 635

    （2）配置证书选项

    示例代码中会对服务器证书进行验证，因此需要完成证书相关的
    配置工作。首先通过mbedtls  _x509_crt_parse        _der将根证书解析至证书
结构体中，解析成功后将根证书添加到mbedtls_ssl_config结构体中，
最后通过mbedtls_ssl_conf_authmode配置认证方式。认证方式分为3
种，描述如下：

    ·MBEDTLS_SSL_VERIFY_NONE，不对证书进行验证；

    ·MBEDTLS_SSL_VERIFY               _OPTIONAL，对证书进行验证，即使
    证书验证失败，也继续完成握手操作；

    ·MBEDTLS_SSL_VERIFY               _REQUIRED，对证书进行验证，而且
    要求证书必须通过验证，否则将终止握手过程。

    示例代码中选择最为严格的是
    MBEDTLS_SSL_VERIFY_REQUIRED，它意味着一旦证书认证失
    败，则立即终止握手过程。

    （3）添加配置到SSL结构体

   完成上述配置工作后，通过mbedtls_ssl_setup接口将配置选项添
    加到mbedtls_ssl_context结构体中，最后通过mbedtls_ssl_set_hostname
    接口设置服务器的hostname。证书验证阶段会对服务器证书中的持有
    者名称（Common Name）或支持者可选名称（Subject Alternative

        635

## Page 636

Name）字段进行验证，示例中使用的hostname为“iotwuxi.org”。

3.连接服务器

     完成SSL相关配置后可尝试与TLS服务器建立连接，该服务器部
署在域名为iotwuxi.org的服务器上。mbedtls提供的接口为
mbedtls_net_connect，该函数需要输入mbedtls_net_context结构体、服
务器域名或IP地址、服务器端口号及协议类型。mbedtls_net_connect
接口原型如下：


    int mbedtls_net_connect( mbedtls_net_context *ctx,
    const char *host, const char *port, int proto );


     连接成功后，需要通过mbedtls_ssl_set_bio接口设置发送和接收
回调函数，当有发送和接收事件时，mbedtls内部会完成接口调用，
该函数需要输入mbedtls_ssl_context结构体、mbedtls_net_context结构
体、发送回调函数、接收回调函数及接收超时时间。
mbedtls_ssl_set_bio接口原型如下：


    void mbedtls_ssl_set_bio( mbedtls_ssl_context *ssl,
    void *p_bio,
    mbedtls_ssl_send_t *f_send,
    mbedtls_ssl_recv_t *f_recv,
    mbedtls_ssl_recv_timeout_t *f_recv_timeout );


    4.执行SSL握手

    在完成SSL选项配置并成功连接到服务器后，只需要调用
    mbedtls_ssl_handshake接口即可完成SSL握手过程。该接口内部实现

        636

## Page 637

了SSL握手状态机，内部会根据不同消息进行状态切换，直到握手成
功。SSL握手过程中的不同状态定义在mbedtls_ssl_states枚举中，该
枚举位于include/mbedtls/ssl.h文件中。



    /*
     * SSL state machine
     */
    typedef enum
    {
       MBEDTLS_SSL_HELLO_REQUEST,
       MBEDTLS_SSL_CLIENT_HELLO,
       MBEDTLS_SSL_SERVER_HELLO,
       MBEDTLS_SSL_SERVER_CERTIFICATE,
       MBEDTLS_SSL_SERVER_KEY_EXCHANGE,
       MBEDTLS_SSL_CERTIFICATE_REQUEST,
       MBEDTLS_SSL_SERVER_HELLO_DONE,
       MBEDTLS_SSL_CLIENT_CERTIFICATE,
       MBEDTLS_SSL_CLIENT_KEY_EXCHANGE,
       MBEDTLS_SSL_CERTIFICATE_VERIFY,
       MBEDTLS_SSL_CLIENT_CHANGE_CIPHER_SPEC,
       MBEDTLS_SSL_CLIENT_FINISHED,
       MBEDTLS_SSL_SERVER_CHANGE_CIPHER_SPEC,
       MBEDTLS_SSL_SERVER_FINISHED,
       MBEDTLS_SSL_FLUSH_BUFFERS,
       MBEDTLS_SSL_HANDSHAKE_WRAPUP,
       MBEDTLS_SSL_HANDSHAKE_OVER,
       MBEDTLS_SSL_SERVER_NEW_SESSION_TICKET,
       MBEDTLS_SSL_SERVER_HELLO_VERIFY_REQUEST_SENT,
    }
    mbedtls_ssl_states;




5.发送消息

      完成SSL握手后，TLS客户端将向服务器发送GET请求来获取
index.hmtl页面。发送接口为mbedtls _write，该接口需要输入
        _ssl
mbedtls_ssl_context结构体、待发送消息和消息长度。需要注意的
是，该接口并不保证一次性发送所有消息，当返回值小于输入的消息
长度时，需要继续调用该接口发送剩余部分，直到将所有消息发送完
成。mbedtls_ssl_write接口原型如下：



    int mbedtls_ssl_write( mbedtls_ssl_context *ssl,
       const unsigned char *buf, size_t len );

       637

## Page 638

    6.读取消息

    TLS服务器在收到GET请求后将返回一个简单的index.html页面。
TLS客户端可以通过mbedtls_ssl_read接口读取ssl消息，该接口需要输
入mbedtls_ssl_context结构体、存放读取消息的缓冲区和缓冲区长
    度，返回值为实际读取的消息长度。mbedtls_ssl        _read接口原型如下：

    int mbedtls_ssl_read( mbedtls_ssl_context *ssl,
        const unsigned char *buf, size_t len );

    7.关闭连接

    完成SSL通信后，通过mbedtls_ssl_close_notify接口关闭连接。










    638

## Page 639

14.13.4 编译与执行

     本节示例默认运行于necluo_f429zi平台，示例代码中客户端地
址、网关地址定义在prj_nucleo_f429zi.conf配置文件中，可根据实际
情况进行修改。IP地址相关配置宏定义如下：



    # necluo_f429zi开发板IP地址
    CONFIG_NET_CONFIG_MY_IPV4_ADDR="{本机IP地址}"
    # 网关IP地址
    CONFIG_NET_CONFIG_MY_IPV4_GW="{本机IP地址}"



     应用程序将把运行结束输出至串口控制台，所以应用程序下载至
开发板运行之前需新建终端，并通过minicom工具打开指定串口。操
作指令如下：




    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     在TLS示例中，需要开启STM32的网卡驱动及网络协议栈，因此
消耗的RAM和FLASH空间会有所增加，示例中共消耗约137KB
FLASH空间和约57KB RAM空间。编译与运行过程如下：



    # 进入示例代码文件夹
    $ cd 14_tls
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region     Used Size Region Size %age Used
             FLASH:       137652 B     2 MB     6.56%
               CCM:           0 GB    64 KB     0.00%
              SRAM:        57392 B   256 KB    21.89%
          IDT_LIST:          216 B     2 KB    10.55%



    639

## Page 640

    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    tls client use nucleo_f429zi board.
    . Seeding the random number generator   ... ok
    . Setting up the SSL/TLS structure  ... ok
    . Connecting to iotwuxi.org:442...  ok
    . Performing the SSL/TLS handshake  ... ok
    > Write to server: 28 bytes written
    GET /index.html HTTP/1.0
    > Read from server: 198 bytes read
    HTTP/1.0 200 ok
    Content-type: text/html
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>TLS Server</title>
    </head>
    <body>
      <h1>This is TLS Server</h1>
    </body>
    </html>
    ok
    . Closing the connection ... done



        在TLS客户端示例中，总共消耗约57K RAM，这些RAM消耗主
    要来自Zephyr网络组件、STM32网络驱动等部分，主要消耗如表14-
    11所示。

        表14-11 TLS示例RAM主要消耗分析






      由于TLS功能依赖Zephyr网络组件和STM32网络驱动，所以约
37K RAM为网络功能的固定开销，占总RAM消耗的65.35%。另外，
mbedtls堆空间和Zephyr主线程栈空间的大小由Zephyr配置文件定义。



    # mbedtls 堆空间大小
    CONFIG_MBEDTLS_HEAP_SIZE=10240
    # Zephyr 主线程栈空间
    CONFIG_MAIN_STACK_SIZE=4096



    640

## Page 641

   mbedtls堆空间太小将导致mbedtls内存分配失败，而Zephyr主线
程栈空间太小，将导致Zephyr任务切换失败。总之，对于TLS示例而
言，37K RAM为固定开销，14KRAM为浮动开销。










    641

## Page 642

14.14 本章小结

  本章是本书中最为复杂的部分。本章重点介绍了TLS记录层协议
和握手子协议。TLS记录层协议包括版本号和长度等信息，每个TLS
报文均包含一个记录头。TLS握手子协议非常复杂，本章结合
ECDHE_ECDSA密钥协商算法说明了如何通过握手过程生成预备主
密钥。在ECDHE_ECDSA密钥交换过程中，预备主密钥的各部分分
别来自于ClientHelllo、ServerHello、ServerKeyExchange和
ClientKeyExchange。预备主密钥的长度与椭圆曲线的位长度有关，例
如椭圆曲线为secp256r1时，预备主密钥的长度为32字节。
ECDHE_ECDSA密钥交换算法要求客户端和服务器均生成一个ECDH
临时公钥，而ECDH_ECDSA密钥交换算法仅要求客户端生成临时公
钥，而服务器将复用证书中的公钥。对称加密部分介绍了3种不同的
加密模式：mac_then_encrypt、encrypt_then_mac和AEAD。物联网应
用推荐使用AEAD模式，该模式负载更短且运算速度更快。

  除了协议内容之外，本章还介绍了ssl_client2工具，该工具是学
习TLS协议的利器，该工具配合Withireshark使用，可快速掌握TLS协
议。








    642

## Page 643

    第15章   DTLS

15.1 本章主要内容

DTLS是Datagram Transport Layer Security的简称，它是运行于
UDP协议之上的安全通信协议。DTLS大部分内容与TLS类似，只有
少部分内容与TLS存在差异。本章将介绍DTLS记录层协议和握手子
协议的变化，这些变化可帮助DTLS克服报文乱序和报文丢失等问
题。另外，本章还介绍PSK密钥交换，在TLS协议中，密钥交换多以
X.509证书为基础，但在物联网应用中，为了节约传输开销，也可以
使用PSK方法进行密钥交换。在mbedtls DTLS应用工具部分将介绍如
何使用ssl_server2和ssl_client2工具测试DTLS通信。最后，通过DTLS
客户端示例说明mbedtls DTLS相关接口的使用方法。










643

## Page 644

15.2 DTLS概述

  DTLS协议是运行在UDP之上的安全通信协议，DTLS协议保留了
TLS协议的设计风格，针对UDP在不可靠传输方面的问题增加了新的
特性。DTLS协议分层结构与TLS类似，如图15-1所示。










    图15-1 DTLS分层结构










    644

## Page 645

15.3 DTLS与TLS区别

  TLS协议依赖TCP提供的可靠传输特性，而DTLS协议依赖的传
输层协议UDP并不能提供这种可靠性服务。相较于TCP协议，UDP协
议没有建立连接过程，也无法自动发送应答报文。DTLS协议需要通
过某些手段解决报文乱序和报文丢失等问题。DTLS协议主要通过以
下方法来解决上述问题：

  ·禁止流密码，避免记录层报文前后关联；

  ·在记录层增加计数值和序列号字段，用于排序和数据认证；

  ·在握手子协议中加入重传机制，防止握手过程中报文丢失；

  ·在握手子协议中加入序列号，保证握手报文的顺序正确；

  ·DTLS握手协议中增加偏移量（fragment_offset）和帧长度
（fragment_length）字段，报文长度大于1500字节后将会产生报文分
片，通过这两个字段可将分片报文进行还原；

  ·DTLS维护一个位图窗口（bitmap window），用于检测重复的报
文。








  645

## Page 646

15.3.1  记录层协议变化

DTLS记录层协议大部分字段和TLS记录层协议相似，但DTLS记
录层协议增加了计数值和序列号字段，这两个字段可解决报文乱序和
报文丢失等问题。DTLS记录层具体格式如下：

struct {
ContentType type;
ProtocolVersion version;
uint16 epoch;             // 新增部分
uint48 sequence_number;   // 新增部分
uint16 length;
opaque fragment[DTLSPlaintext.length];
} DTLSPlaintext;

其中：

·type，报文类型；

·version，DTLS版本，本章中DTLS协议的版本为
DTLS1.2（{0xFE,0xFD}）；

·epoch，独立计数值，占2字节，初始值为0，每次密码规格变更
（ChangeCipherSpec）后该计数值递增，该计数值主要用于区分重协
商过程中具有相同序列号的报文；

·sequence_number，记录层序列号，占6字节，每次密码规格变更
（ChangeCipherSpec）后置0。

TLS协议中也有序列号，但在TLS协议中序列号由客户端和服务

                          646

## Page 647

器各自保存，而在DTLS协议中序列号由“隐式”变为“显式”，该字段
直接出现在DTLS记录层协议中。记录层中的序列号可以帮助DTLS协
议解决报文乱序到达和报文丢失等问题。










    647

## Page 648

15.3.2 握手协议变化

   DTLS握手子协议和TLS握手子协议非常相似，但DTLS有一些变
化，这些变化包括以下内容。

1.防止DDoS攻击

   握手子协议类型中加入HelloVerifyRequest，服务器接收到
ClientHello消息后将为请求连接的IP地址分配一个cookie，并把这个
cookie包含在HelloVerifyRequest消息中；客户端接收到
HelloVerifyRequest消息后，需重新发送带有cookie的ClientHello消
息。如果服务器在短时间内连续收到某个IP的重复报文则会将其丢
弃。在握手协议类型中加入HelloVerifyRequest消息字段，可以有效地
防止DDoS攻击，交互过程如图15-2所示。










    648

## Page 649

    图15-2 DTLS cookie交换过程

    DTLS握手子协议中增加了hello_verify_request报文，该报文的类
    型编号为3。



    enum {
    hello_verify_request(3),
    } HandshakeType;



    _verify_request报文的具体结构如下：
    hello



    struct {
    ProtocolVersion server_version;
    opaque cookie<0..2^8-1>;
    } HelloVerifyRequest;




    ClientHello报文中也增加了新的字段。



    struct {
    ProtocolVersion client_version;
    Random random;
    SessionID session_id;
    opaque cookie<0..2^8-1>; // 新增字段
    CipherSuite cipher_suites<2..2^16-1>;
    CompressionMethod compression_methods<1..2^8-1>;
    } ClientHello;




      以下示例样本中可以观察到Cookie交换完整过程，示例样本中省
略了部分握手信息。从样本中可以看出，客户端发送的第1个
ClientHello报文中并没有Cookie；服务器收到第1个ClientHello后通过
     _verify_request报文把服务器生成的Cookie发送至客户端；客户
hello
端收到Cookie后重新发送ClientHello报文，而此时的ClientHello报文
中包含Cookie。在本例中Cookie的长度为32字节。



    649

## Page 650

    Handshake Protocol: Client Hello
    Handshake Type: Client Hello (1)
    Length: 136
    Message Sequence: 0
    Fragment Offset: 0
    Fragment Length: 136
    Version: DTLS 1.2 (0xfefd)
    Random: 5b2858ec9460ea998b3c064541ab17d956b794e208f172d3...
    Session ID Length: 0
    Cookie Length: 0
    # 省略部分信息
    Handshake Protocol: Hello Verify Request
    Handshake Type: Hello Verify Request (3)
    Length: 35
    Message Sequence: 0
    Fragment Offset: 0
    Fragment Length: 35
    Version: DTLS 1.2 (0xfefd)
    Cookie Length: 32
    Cookie: 5b2858ec0c9afcab52ce8a122fd4e79bab1a76c0c5f8bab7...
    Handshake Protocol: Client Hello
    Handshake Type: Client Hello (1)
    Length: 168
    Message Sequence: 1
    Fragment Offset: 0
    Fragment Length: 168
    Version: DTLS 1.2 (0xfefd)
    Random: 5b2858ec9460ea998b3c064541ab17d956b794e208f172d3...
    Session ID Length: 0
    Cookie Length: 32
    Cookie: 5b2858ec0c9afcab52ce8a122fd4e79bab1a76c0c5f8bab7...
    # 省略部分信息




    2.握手协议格式

握手子协议中增加message_seq序列号字段。双方发送第1个报文
    的message_seq序列号为0，每发送一条报文后message_seq序列号增加
    1。如果发生消息重传，则使用相同的message_seq序列号。握手协议
    格式的具体内容如下：




    struct {
    HandshakeType msg_type;
    uint24 length;
    uint16 message_seq;             // 新增字段
    uint24 fragment_offset;         // 新增字段
    uint24 fragment_length;         // 新增字段
    select (HandshakeType) {
            case hello_request: HelloRequest;
            case client_hello: ClientHello;
            case hello_verify_request: HelloVerifyRequest; // 新类型
            case server_hello: ServerHello;
            // 省略部分内容



            650

## Page 651

    } body;
} Handshake;

     message_seq序列号的使用方法如图15-3所示。










        图15-3     DTLS握手消息序列号

    3.超时和重传

    DTLS握手协议中增加超时和重传机制，用于防止报文丢失。协
    议中将握手过程划分成不同的阶段，每个阶段中可能包含多个协议类
    型，但应该将其视为一个整体以达到超时重传的目的。交互过程按阶
    段划分情况如图15-4所示。


    651

## Page 652

    图15-4 DTLS握手消息的阶段划分

  DTLS使用一个简单的超时和重传机制，状态机中包括4种状态，
分别为准备、发送、等待和完成。握手过程总是由客户端发起
（ClientHello），所以客户端的起始状态为准备状态，服务器的起始
状态为等待状态。超时和重传的状态机如图15-5所示。

  ·准备状态，客户端从准备状态开始，缓存下一阶段握手消息并
进入发送状态。

  ·发送状态，发送握手消息并设置超时重传时间，进入等待状
态。

    652

## Page 653

·等待状态，接收到握手消息、到达超时重传时间或接收到重传
消息中的一种情况成立时，都会离开等待状态。如果接收到握手消
息，会判断是否为最后一个阶段的握手消息，如果是则进入完成状
态，如果不是则进入准备状态。

      ·完成状态，接收到重传消息、服务器发送HelloRequest或客户端
接收到HelloRequest中的一种情况成立时，都会离开完成状态。第1种
情况如果接收到重传消息，会重新发送最后一个阶段的握手消息。第
2种情况通常发生在服务器需要重新握手时，服务器会发送
HelloRequest消息，并进入准备状态。第3种情况中客户端在接收到
HelloRequest消息后，会发送ClientHello消息，并进入准备状态。










653

## Page 654

图15-5 DTLS超时重传状态机










654

## Page 655

15.4 PSK密钥交换

在第14章已经详细介绍了ECDH（E）_ECDSA密钥交换方法，
但是这类密钥交换方法依赖X.509证书，客户端需要通过服务器证书
中的公钥和公钥签名判断服务器的真实性。在第14章的示例中
mbedtls的默认自签名证书的长度约为500字节，这种证书的“尺寸”对
于互联网应用来说毫无压力，但对于物联网终端来说却是一个挑战。
为了尽可能地减少传输开销，物联网终端也可以使用PSK密钥交换方
法。PSK是Pre-Shared Key的简称，只有客户端和服务器都具备相同
的PSK时才可以建立（D）TLS通信。PSK密钥交换详细内容可参考
《RFC4279 Pre-Shared Key Ciphersuites for Transport Layer
Security（TLS）》，该文档不仅适用于TLS也适用于DTLS。










655

## Page 656

15.4.1 PSK Identity

   PSK密钥交换方法涉及另一个重要概念：PSK Identity。PSK
Identity和PSK与用户名和登录口令的概念非常接近，PSK Identity相
当于用户名，而PSK相当于登录口令。例如某物联网终端的PSK
Identity为IoTNode.A5D6，该物联网终端的PSK为
E456B90AC84DC6（Hex格式）。一般情况下，PSK Identity可使用物
联网终端自身的固定信息，例如出厂编号、CPUID、SIM卡信息或通
信模组内部信息等，PSK Identity常用字符串形式表示；而PSK一般采
用Hex格式表示。

   对于物联网终端而言，不同终端的PSK Identity和PSK应各不相
同。服务器将保存终端的PSK Identity和PSK的列表。当客户端与服务
器进行握手时，客户端将告之服务器自身的PSK Identity，服务器根
据客户端的PSK Identity，从存储列表中找出相应PSK。客户端和服务
器通过相同的PSK生成预备主密钥。










    656

## Page 657

15.4.2 密钥交换详细过程

PSK密钥交换过程大致可分为确认PSK密码套件、客户端提供
PSK Identity和预备主密钥计算3个步骤。客户端与服务器交换过程如
图15-6所示。










    图15-6     PSK密钥交换过程

1.客户端与服务器确认密码套件

客户端与服务器通过ClientHello和ServerHello确认采用PSK密码
套件。ClientHello报文示例内容如下：

Handshake Protocol: Client Hello
Handshake Type: Client Hello (1)
Length: 168
Message Sequence: 1

    657

## Page 658

Fragment Offset: 0
Fragment Length: 168
Version: DTLS 1.2 (0xfefd)
Random: 5b7793764fe745bb006c6fa4a4c0c79e60eb8331cd52edda...
Session ID Length: 0
Cookie Length: 32
Cookie: 5b77937676ab075f6b34be61162155d351fc8da235439da3...
Cipher Suites Length: 4
Cipher Suites (2 suites)
Cipher Suite: TLS_PSK_WITH_AES_128_CCM_8 (0xc0a8)
Cipher Suite: TLS_EMPTY_RENEGOTIATION_INFO_SCSV (0x00ff)
[省略部分内容]




ServerHello报文示例内容如下：




Handshake Protocol: Server Hello
Handshake Type: Server Hello (2)
Length: 59
Message Sequence: 1
Fragment Offset: 0
Fragment Length: 59
Version: DTLS 1.2 (0xfefd)
Random: 5b779376a4b51d18eb40e8c8d003591a4aa9001c80e31831...
Session ID Length: 0
Cipher Suite: TLS_PSK_WITH_AES_128_CCM_8 (0xc0a8)
Compression Method: null (0)
[省略部分内容]




从ClientHello和ServerHello报文可以看出，客户端和服务器经过
协商之后确认了密码套件，经过确认的密码套件为
    _8。同时客户端和服务器均提供了
TLS_PSK_WITH_AES_128_CCM
32字节随机数，具体内容如下：



# 客户端随机数
5b 77 93 76 4f e7 45 bb 00 6c 6f a4 a4 c0 c7 9e
60 eb 83 31 cd 52 ed da 71 ac 90 1b db dc 9f 38
# 服务器随机数
5b 77 93 76 a4 b5 1d 18 eb 40 e8 c8 d0 03 59 1a
4a a9 00 1c 80 e3 18 31 1a 83 82 b5 31 18 0a 24





2.客户端提供PSK Identity

客户端在ClientKeyExchange中提供PSK Identity，这样服务器便


658

## Page 659

可在已经存储的列表中找到客户端对应的PSK。ClientKeyExchange报
文示例内容如下：

Handshake Protocol: Client Key Exchange
  Handshake Type: Client Key Exchange (16)
  Length: 13
  Message Sequence: 2
  Fragment Offset: 0
  Fragment Length: 13
  PSK Client Params
  Identity Length: 11
  Identity: 496f544e6f64652e413544

  此处Identity长度为11字节，Identity经过Hex编码之后
为“496f544e6f64652e413544”，字符串形式为“IoTNode.A5D6”。

3.预备主密钥计算

  预备主密钥的组成方法如下：

  1）如果PSK的长度为N字节，先使用一个16位无符号整数表示长
度；

  2）在长度指示后追加N字节0x00；

  3）再用一个uint16整数表示长度；

  4）最后为N字节PSK本身。

  预备主密钥的具体组装方法如图15-7所示。






  659

## Page 660

        图15-7 预备主密钥生成规则

   此处PSK为E456B90AC84DC6（Hex格式），经过上述处理之后
预备主密钥的长度为18字节。具体内容如下：

  # 预备主密钥
  00 07 00 00 00 00 00 00 00 00 07 e4 56 b9 0a c8 4d c6

   一般情况下，客户端中PSK固定不变，也就是预备主密钥不会发
生变化，但由于主密钥生成时使用了ClientHello和ServerHello报文中
的随机数，所以主密钥肯定发生变化，如图15-8所示。










    图15-8 主密钥生成过程






    660

## Page 661

15.4.3 PSK与X.509证书传输开销比较

   下面我们比较PSK与X.509证书传输开销。DTLS-PSK情景中，
PSK Identity为IoTNode.A5D6，PSK为496f544e6f64652e413544（Hex
格式）；DTLS-X.509情景中，证书为mbedtls默认证书，密钥交换算
法为ECDHE_ECDSA。两种情况中列举的握手协议长度均来自于
DTLS记录层协议中的长度字段。

        表15-1 PSK与X.509证书传输开销比较










   从表15-1可以看出，PSK方式可以节约更多的传输资源，在握手
过程中可以减少Certificate和ServerKeyExchange报文，而Certificate报
文往往是握手协议中最“重”的报文。在这样的测试情况下，
Certificate报文中仅包含一份证书，而在实际情况中需要包含两份甚
至多份证书，这对物联网设备是一个较为沉重的负担。从传输消耗的
角度来说，PSK方式更适合物联网设备。




    661

## Page 662

15.5 DTLS对称加密变化

  DTLS协议中对称加密部分与TLS协议中的对称加密几乎相同，
但也存在一些细节差异。若对称加密部分采用GCM或CCM模式，与
加解密操作相关的一次性整数显式部分就由epoch和seq_num两部分组
成。TLS协议中一次性整数显式部分的长度为8字节，而DTLS协议
中，epoch的长度为2字节，seq_num的长度为6字节，组成后的一次性
整数显式部分的长度也为8字节。GCM或CCM模式下一次性整数显式
部分的组成方法如图15-9所示。










    图15-9 GCM或CCM模式下一次性整数显式部分的组成方法






    662

## Page 663

15.6 mbedtls DTLS应用工具

   第14章已经介绍过ssl_server2和ssl_client2工具，这两个工具不但
能用于TLS测试，也可用于DTLS测试。下面回顾一下ssl_server2和
ssl_client2工具的参数情况，表15-2中整理了DTLS PSK密钥交换应用
相关的参数。

        表15-2 ssl_server2和ssl_client2 DTLS应用参数










    663

## Page 664

15.6.1 基础示例说明

本节以PSK密钥交换为例，说明如何通过ssl_server2和ssl_client2
测试DTLS应用。操作过程如下：

1）裁剪并重新编译mbedlts；

2）新建第1个控制台，在控制台中启动DTLS服务器；

3）打开第2个控制台，在控制台中通过tcpdump工具抓取网络分
组数据，并保存为pcap文件，被抓取的网络数据可通过Wireshark进行
进一步分析；

4）打开第3个控制台，在控制台中启动DTLS客户端；

5）DTLS客户端与DTLS服务器端完成握手协议之后，DTLS客户
端将向TLS服务器发送一个GET请求，DTLS服务器将返回经过协商
的密码套件信息；

6）DTLS客户端和服务器端运行时，将在控制台输出DTLS协议
版本和密码套件等信息。

以上过程如图15-10所示。






664

## Page 665

图15-10 DTLS基础示例过程










665

## Page 666

    15.6.2 启动ssl
        _server2

    新建第1个控制台，在控制器中启动DTLS服务器，等待客户端连
    接并通过控制台查看输出。




    $ ssl_server2 psk_identity=IoTNode.A5D6 psk=E456B90AC84DC6 dtls=1
    force_ciphersuite=TLS-PSK-WITH-AES-128-CCM-8
    . Seeding the random number generator... ok
    . Loading the CA root certificate ... ok (0 skipped)
    . Loading the server cert. and key... ok
    . Bind on udp://*:4433/ ...  ok
    . Setting up the SSL/TLS structure... ok
    . Waiting for a remote connection ...
    # 当有DTLS连接后，输出信息如下：
    . Performing the SSL/TLS handshake... hello verification requested
    . Waiting for a remote connection ... ok
    . Performing the SSL/TLS handshake... ok
    [ Protocol is DTLSv1.2 ]
    [ Ciphersuite is TLS-PSK-WITH-AES-128-CCM-8 ]
    [ Record expansion is 29 ]
[ Maximum fragment length is 16384 ]
    . Verifying peer X.509 certificate... ok
    < Read from client: 34 bytes read
    GET / HTTP/1.0
    Extra-header:
    > Write to client: 139 bytes written in 1 fragments
    HTTP/1.0 200 OK
    Content-Type: text/html
    <h2>mbed TLS Test Server</h2>
    <p>Successful connection using: TLS-PSK-WITH-AES-128-CCM-8</p>
    . Closing the connection... done










    666

## Page 667

15.6.3 抓取网络数据

               新建第2个控制台，通过tcpdump工具抓取网络分组数据。此处通
过-i参数指定网卡为loopback，通过-w指定将抓包结果保存到dtls.pcap
文件中。

$ sudo tcpdump –i lo –w dtls.pcap udp port 4433










667

## Page 668

        启动ssl
    15.6.4    _client2

    新建第3个控制台，在控制台中启动DTLS客户端，并强制客户端
    密钥套件为TLS-PSK-WITH-AES-128-CCM-8。



    $ ssl_client2 force_ciphersuite=TLS-PSK-WITH-AES-128-CCM-8 psk_identity=IoTNode.A5D6 psk=E456B90AC84DC6 dtls=1 force_ciphersuite=TLS-PSK-WITH-AES-128-CCM-8
    . Seeding the random number generator... ok
    . Loading the CA root certificate ... ok (0 skipped)
    . Loading the client cert. and key... ok
    . Connecting to udp/localhost/4433... ok
    . Setting up the SSL/TLS structure... ok
    . Performing the SSL/TLS handshake... ok
    [ Protocol is DTLSv1.2 ]
    [ Ciphersuite is TLS-PSK-WITH-AES-128-CCM-8 ]
    [ Record expansion is 29 ]
[ Maximum fragment length is 16384 ]
    . Verifying peer X.509 certificate... ok
    > Write to server: 34 bytes written in 1 fragments
    GET / HTTP/1.0
    Extra-header:
    < Read from server: 139 bytes read
    HTTP/1.0 200 OK
    Content-Type: text/html
    <h2>mbed TLS Test Server</h2>
    <p>Successful connection using: TLS-PSK-WITH-AES-256-CCM-8</p>
    . Closing the connection... done










    668

## Page 669

15.6.5 分析网络数据

   停止tcpdump工具，通过Wireshark打开网络分析数据。在
Wireshark过滤条件中输入“dtls”。通过Wireshark可展现DTLS客户端
与DTLS服务器端握手的详细过程，如图15-11所示。










    图15-11 通过Wireshark展现DTLS网络分组数据









    669

## Page 670

15.7  构建DTLS服务器

  本节将描述如何使用OpenSSL s_server工具构建DTLS服务器，
DTLS服务器将使用PSK-AES128-CCM8（TLS-PSK-WITH-AES-128-
CCM-8）作为密码套件。相比TLS构建过程，DTLS的构建过程较为
简单，只需要通过命令行指定psk相关参数即可。启动DTLS服务过程
如下：

$ openssl s_server -state -nocert -dtls1_2 -port 4432 -cipher PSK-AES128-CCM8 -psk_hint Client_identity -psk 000102030405060708090a0b0c0d0e0f
# 输出
Using default temp DH parameters
ACCEPT

  注意：为了便于读者使用，本书已经在域名为iotwuxi.org服务器
已经部署了DTLS服务，该服务的端口号为4432。在后续DTLS客户端
示例中默认会与该服务器进行连接。本节描述的DTLS服务器的部署
方式仅用于DTLS客户端的测试，实际应用场景中并不推荐该部署方
式。










670

## Page 671

15.8 构建DTLS客户端

  本节示例将介绍如何在嵌入式终端中实现DTLS客户端。示例代
码中所访问的DTLS服务器部署于阿里云主机中，该云主机的域名为
iotwuxi.org，IP地址为139.196.187.107，DTLS服务端口号为4432。
DTLS握手成功后，客户端会向服务器发送“Echo this”的消息，服务
器接收到消息后直接将消息返回。DTLS客户端与DTLS服务器的交互
过程如图15-12所示。










        图15-12 DTLS-PSK示例交互过程

  与第14章示例不同，DTLS示例将使用预共享密钥（PSK）协商
方案，DLTS握手过程中省去了X.509证书传输过程，使握手过程中的
负载长度明显减少，所消耗的RAM空间也相应减少，因此PSK密钥
协商方案更加适合于物联网终端。PSK密钥协商过程如图15-13所
示。


    671

## Page 672

    图15-13 DTLS PSK协商方式握手过程

           注意：由于篇幅限制，示例代码中只给出部分函数，完整代码见
本书GitHub代码仓库。本节示例位于15_dtls文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。










672

## Page 673

15.8.1 配置文件

DTLS示例中配置文件参考自config-ccm-psk-tls1_2.h，该文件是
mbedtls所提供的配置文件中最精简的一个。DTLS示例中
mbedtls_config.h配置文件相关宏定义描述如表15-3所示。

    表15-3 DTLS示例配置文件宏定义描述










673

## Page 674

15.8.2 示例代码

      DTLS示例和TLS示例稍有区别，由于DTLS协议中加入了超时和
重传机制，而超时和重传机制的实现依赖于定时回调函数，所以示例
中增加了定时回调相关接口。设置定时器和获取定时器接口分别为
        _delay和dtls _delay，通过
dtls_timing_set _timing_get
mbedtls_ssl_set_timer_cb接口完成定时回调接口的注册，当握手过程
中发生超时和重传时将会调用注册的定时回调函数。除了定时回调函
数接口外，其余内容和TLS示例基本一致。DTLS示例代码如代码清
单15-1所示，示例代码相关接口描述如表15-4所示。

      代码清单15-1 DTLS示例



    // 省略头文件及中间代码
    #define SERVER_PORT      "4432"
    #define SERVER_ADDR      "iotwuxi.org"
    #define MESSAGE          "Echo this\r\n"
    int main(void)
    {
     int ret, len = 0;
     unsigned char buf[256];
     const char *pers = "dtls_client";
     mbedtls_entropy_context entropy;
     mbedtls_ctr_drbg_context ctr_drbg;
     mbedtls_platform_set_printf(printf);
     mbedtls_ssl_context ssl;
     mbedtls_ssl_config conf;
     mbedtls_net_context ctx;
     mbedtls_net_init(&ctx);
     mbedtls_ssl_init(&ssl);
     mbedtls_ssl_config_init(&conf);
     mbedtls_ctr_drbg_init(&ctr_drbg);
     mbedtls_printf("\n    . Seeding the random number generator...");
     mbedtls_entropy_init(&entropy);
     mbedtls_entropy_add_source(&entropy, entropy_source, NULL,
         MBEDTLS_ENTROPY_MAX_GATHER, MBEDTLS_ENTROPY_SOURCE_STRONG);
     mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
         (const uint8_t *)pers, strlen(pers));
     mbedtls_printf(" ok\n  . Setting up the SSL/TLS structure...");
     mbedtls_ssl_config_defaults(&conf, MBEDTLS_SSL_IS_CLIENT,
         MBEDTLS_SSL_TRANSPORT_DATAGRAM, MBEDTLS_SSL_PRESET_DEFAULT);


                             674

## Page 675

 mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);
 mbedtls_ssl_conf_psk(&conf, psk, sizeof(psk),
           (const uint8_t *)psk_id, strlen((char*)psk_id));
 mbedtls_ssl_setup(&ssl, &conf);
 mbedtls_printf(" ok\n  . Connecting to %s:%s...", SERVER_ADDR, SERVER_PORT);
 mbedtls_net_connect(&ctx, SERVER_ADDR, SERVER_PORT, MBEDTLS_NET_PROTO_UDP);
 mbedtls_ssl_set_timer_cb(&ssl, &timer,
           dtls_timing_set_delay, dtls_timing_get_delay);
 mbedtls_ssl_set_bio(&ssl, &ctx, mbedtls_net_send, mbedtls_net_recv, NULL);
 mbedtls_printf(" ok\n  . Performing the SSL/TLS handshake...");
 while ((ret = mbedtls_ssl_handshake(&ssl)) != 0)
 {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE)
        {
         mbedtls_printf(" failed\n ! -0x%x\n\n", -ret);
         goto cleanup;
        }
 }
 mbedtls_printf(" ok\n > Write to server:");
 do {
        mbedtls_ssl_write(&ssl, (const uint8_t *)MESSAGE, strlen(MESSAGE));
 } while (ret == MBEDTLS_ERR_SSL_WANT_READ ||
         ret == MBEDTLS_ERR_SSL_WANT_WRITE);
 len = ret;
 mbedtls_printf( " %d bytes written\n\n%s\n\n", len, MESSAGE);
 mbedtls_printf(" > Read from server:");
 len = sizeof(buf) - 1;
 memset(buf, 0x00, sizeof(buf));
 do {
        mbedtls_ssl_read(&ssl, buf, len);
 } while (ret == MBEDTLS_ERR_SSL_WANT_READ ||
         ret == MBEDTLS_ERR_SSL_WANT_WRITE);
 len = ret;
 mbedtls_printf( " %d bytes read\n\n\n%s\n\n", len, buf);
 mbedtls_ssl_close_notify(&ssl);
 mbedtls_printf(" . Closing the connection  ... done\n");
cleanup:
 mbedtls_net_free(&ctx);
 mbedtls_ssl_free(&ssl);
 mbedtls_ssl_config_free(&conf);
 mbedtls_ctr_drbg_free(&ctr_drbg);
 mbedtls_entropy_free(&entropy);
 return 0;
}



         表15-4 DTLS示例相关接口描述










         675

## Page 676

676

## Page 677

15.8.3     代码说明

1.配置随机数

DTLS握手过程中需要使用随机数接口，首先需要完成随机数的
配置工作，该过程包括熵源接口添加、熵源属性设置及通过个性化字
符串更新种子。伪随机数生成器配置过程的详细描述可回顾7.6.2节。

2.配置SSL选项

（1）配置默认选项

为了完成DTLS握手过程，首先需要通过
mbedtls_ssl_config_defaults接口完成SSL默认选项的配置，该函数需
要输入mbedtls _ssl     _config结构体、终端类型、传输协议，以及是否预
设配置选项，配置信息保存在mbedtls    _ssl  _config结构体中。其中，终
端类型分为MBEDTLS  _SSL_IS_CLIENT和
MBEDTLS_SSL_IS _SERVER两种，客户端为
MBEDTLS_SSL_IS _CLIENT。传输协议分为TCP和UDP两种，其中
MBEDTLS_SSL_TRANSPORT_STREAM对应TLS协议，而
MBEDTLS_SSL_TRANSPORT_DATAGRAM对应DTLS协议。预设置
选项可设置一些默认的参数，如版本号、密码套件等。
mbedtls_ssl_config接口原型如下：



677

## Page 678

    int mbedtls_ssl_config_defaults( mbedtls_ssl_config *conf,
    int endpoint, int transport, int preset );


     （2）配置PSK选项

     示例代码中会使用预共享密钥（PSK）协商方案，因此需要完成
PSK相关的配置工作，通过mbedtls_ssl_conf_psk接口可以将预共享密
钥参数添加到mbedtls_ssl_config结构体中，该函数需要输入
mbedtls_ssl_config结构体、预共享密钥、预共享密钥长度、预共享密
钥身份信息和预共享密钥身份信息长度。示例中所使用的预共享密钥
参数如下：


    const uint8_t psk[] = {
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
      0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    const char psk_id[] = "Client_identity";


    mbedtls_ssl_conf_psk接口原型如下：


    int mbedtls_ssl_conf_psk( mbedtls_ssl_config *conf,
    const unsigned char *psk, size_t psk_len,
    const unsigned char *psk_identity, size_t psk_identity_len );


     （3）添加配置到SSL结构体

     完成上述配置工作后，通过mbedtls_ssl_setup接口将配置选项添
加到mbedtls_ssl_context结构体中，该函数需要输入
mbedtls_ssl_context结构体和mbedtls_ssl_config结构体，配置参数被保
存到mbedtls_ssl_context结构体中。mbedtls_ssl_setup接口原型如下：


    int mbedtls_ssl_setup( mbedtls_ssl_context *ssl,

      678

## Page 679

    const mbedtls_ssl_config *conf );


3.连接服务器

     完成SSL相关配置后，可以尝试与DTLS服务器建立连接，DTLS
服务器部署在域名为iotwuxi.org的阿里云主机上。mbedtls提供的连接
接口为mbedtls_net_connect，该函数需要输入mbedtls_net_context结构
体、服务器域名或IP地址、服务器端口号及协议类型。
mbedtls_net_connect接口原型如下：


    int mbedtls_net_connect( mbedtls_net_context *ctx,
    const char *host, const char *port, int proto );


     DTLS协议相比TLS协议增加了超时和重传机制，所以在使用
DTLS建立握手之前需要通过mbedtls_ssl_set_timer_cb接口设置定时器
回调函数，该函数需要输入mbedtls_ssl_context结构体、
mbedtls_net_context结构体、设置定时器回调函数和获取定时器回调
函数。该接口原型如下：


   void mbedtls_ssl_set_timer_cb( mbedtls_ssl_context *ssl,
        void *p_timer,
        mbedtls_ssl_set_timer_t *f_set_timer,
        mbedtls_ssl_get_timer_t *f_get_timer );

     最后，通过mbedtls_ssl_set_bio接口设置发送和接收回调函数，
当有发送和接收事件时，mbedtls内部会完成接口调用，该函数需要
输入mbedtls_ssl_context结构体、mbedtls_net_context结构体、发送回
调函数、接收回调函数及接收超时时间。mbedtls_ssl_set_bio接口原


    679

## Page 680

    型如下：


    void mbedtls_ssl_set_bio( mbedtls_ssl_context *ssl,
    void *p_bio,
    mbedtls_ssl_send_t *f_send,
    mbedtls_ssl_recv_t *f_recv,
    mbedtls_ssl_recv_timeout_t *f_recv_timeout );


4.执行SSL握手

     在完成SSL选项配置并与DTLS服务器建立连接后，只需要调用
mbedtls_ssl_handshake接口即可完成SSL握手过程。该接口内部实现
了SSL握手状态机，内部会根据不同消息进行状态切换，直到握手成
功。SSL握手过程中的不同状态定义在mbedtls_ssl_states枚举中，该
枚举在include/mbedtls/ssl.h文件中。

5.发送消息

     完成DTLS握手后，DTLS客户端将会向服务器发送一条“Echo
this”的消息。发送接口为mbedtls_ssl_write，该接口需要输入
mbedtls_ssl_context结构体、待发送消息和消息长度。需要注意的
是，该接口并不保证一次性发送所有消息，当返回值小于输入的消息
长度时，需要继续调用该接口发送剩余部分，直到将所有消息发送完
成。mbedtls_ssl_write接口原型如下：


    int mbedtls_ssl_write( mbedtls_ssl_context *ssl,
    const unsigned char *buf, size_t len );





    680

## Page 681

    6.读取消息

   DTLS服务器在收到客户端的消息后，将返回“Echo this”的消息
到客户端。客户端可以通过mbedtls_ssl_read接口进行读取，该接口需
要输入mbedtls_ssl_context结构体、存放读取消息的缓冲区和缓冲区
长度，返回值为实际读取的消息长度。mbedtls_ssl_read接口原型如
下：

    int mbedtls_ssl_read( mbedtls_ssl_context *ssl,
        const unsigned char *buf, size_t len );

    7.关闭连接

   完成SSL通信后，通过mbedtls_ssl_close_notify接口关闭连接。










    681

## Page 682

    15.8.4 编译与执行

    本示例默认运行于necluo_f429zi平台。示例中客户端地址、网关
    地址定义在prj_nucleo_f429zi.conf配置文件中，可根据实际情况进行
    修改。IP地址配置宏定义如下：



    # necluo_f429zi开发板IP地址
    CONFIG_NET_CONFIG_MY_IPV4_ADDR="{本机IP地址}"
    # 网关IP地址
    CONFIG_NET_CONFIG_MY_IPV4_GW="{本机IP地址}"



     运行过程中，应用程序将把运行结果输出至串口控制台，所以应
用程序下载至开发板运行之前需新建终端，并通过minicom工具打开
指定串口。操作指令如下：




    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     相比TLS示例，DTLS示例的RAM和FLASH消耗有所减少，
DTLS示例共消耗约105KB FLASH空间和约49KB RAM空间。编译与
运行过程如下：




    # 进入示例代码文件夹
    $ cd 15_dtls
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region     Used Size Region Size %age Used
             FLASH:       104692 B     2 MB     4.99%
               CCM:           0 GB    64 KB     0.00%
              SRAM:        48720 B   256 KB    18.59%
          IDT_LIST:          216 B     2 KB    10.55%



    682

## Page 683

    # 下载到开发板运行
    $ make flash
    # 串口控制台输出
    . Seeding the random number generator... ok
    . Setting up the SSL/TLS structure... ok
    . Connecting to iotwuxi.org:4432... ok
    . Performing the SSL/TLS handshake... ok
    > Write to server: 11 bytes written
    Echo this
    > Read from server: 11 bytes read
    Echo this
    . Closing the connection ... done



    TLS示例共消耗57KB RAM，而DTLS示例共消耗49KB RAM，
    DTLS示例的内存消耗主要来自于Zephyr Net组件和STM32网络驱动
    等部分，主要消耗如表15-5所示。

    表15-5 DTLS RAM主要消耗






      DTLS示例中“固定”消耗部分与TLS示例同为37KB，而“浮动”消
耗部分由14KB降为6KB。相比TLS，DTLS可使用更小的mbedtls堆空
间和Zephyr主线程栈空间。本示例中，两个空间的大小定义如下：



    CONFIG_MBEDTLS_HEAP_SIZE=4096
    CONFIG_MAIN_STACK_SIZE=2048










    683

## Page 684

15.9 本章小结

   本章介绍了DTLS协议。DTLS协议与TLS协议大致相同但也存在
细节差异。在ClientHello报文中，DTLS协议加入了Cookie机制，通过
Cookie机制可以防止DDoS攻击。另外，DTLS协议中加入了多个序列
号——DTLS记录层中加入了2字节epoch和6字节sequence number；握
手子协议中也加入了2字节message_seq。DTLS协议通过这种改进，
克服UDP传输中报文乱序到达和报文丢失等问题。对于物联网应用来
说，也可以使用PSK密钥交换方法，相较于X.509证书PSK密钥交换
可节约传输开销，更适合内存受限制设备。mbedtls工具部分，
ssl_server2和ssl_client2工具通过dtls=1参数也可应用于DTLS测试。










    684

## Page 685

        第16章 CoAPs

16.1 本章主要内容

  本章将介绍CoAPs原理和实现。CoAP是专门为物联网设备而设
计的应用层协议，CoAP本身没有安全机制，CoAP需借助TLS或
DTLS才可以实现安全通信。被加密后的CoAP协议一般称为CoAPs，
本章将介绍CoAPs实现中的3种安全模式：PSK、Raw Public Key和
X.509证书。本章将使用Java Californium框架实现一个CoAPs服务
器，并使用mbedtls构建一个CoAPs客户端，CoAP客户端与服务器通
过PSK模式完成DTLS握手。










    685

## Page 686

16.2 CoAPs原理

CoAP是为受限制设备专门设计的物联网应用层协议，核心部分
由《RFC The Constrained Application Protocol（CoAP）》定义，在核
心协议中规定CoAP使用UDP作为传输层协议。另外《RFC8323
CoAP（Constrained Application Protocol）over TCP,TLS,and
WebSockets》还为CoAP增加了其他的传输方式，也就是说CoAP不但
可以使用UDP作为传输层协议，也可以使用TCP作为传输层协议。为
了表示区别，当使用TCP作为传输层协议时一般称为CoAP over
TCP。

                       CoAP协议与HTTP协议类似，它本身没有提供任何的安全机制，
CoAP请求响应均使用明文传输。为了解决安全问题，HTTP协议使用
TLS作为安全传输协议。与HTTP情况相似，CoAP可以选择DTLS作
为安全传输协议。使用安全传输协议的CoAP协议一般被称为CoAPs
协议。另外，CoAP over TCP也可使用TLS作为安全传输层协议。
CoAPs与DTLS、TLS的关系如图16-1所示。










686

## Page 687

图16-1 CoAPs与DTLS、TLS之间的关系










687

## Page 688

16.3 CoAPs安全说明

        CoAPs支持3种安全模式：PSK、Raw Public Key和X.509。下面
将简单介绍这3种安全模式。

                  ·PSK模式：该模式是3种模式中最为简单的一种，CoAP核心协
议中规定终端节点必须支持TLS_PSK_WITH_AES_128_CCM         _8安全
套件。

  ·Raw Public Key模式：该模式由《RFC7250 Using Raw Public
Keys in Transport Layer Security（TLS）and Datagram Transport Layer
Security（DTLS）》定义。在X.509证书模式下，握手过程中将交换
证书，一般情况下服务器将把证书发送至客户端，证书中不但包括公
钥还包括公钥签名。但在Raw Public Key模式下，服务器并不会传递
证书，而只把公钥发送至客户端。在Raw Public Key模式下公钥仅经
过ASN.1编码便发送至客户端，经过编码后公钥尺寸远小于X.509证
书，传输效率较高。但最新版的mbedtls并未支持Raw Public Key模
式。

  ·X.509证书：该模式是3种模式中最为常用的一种，CoAP核心协
议规定终端节点必须支持
TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8安全套件。另外CoAP
核心协议推荐的椭圆曲线为secp256r1，推荐的单向散列算法为
SHA256。

    688

## Page 689

16.4 构建CoAPs服务器

   本节通过Java Californium框架构建一个CoAPs服务器。
Californium框架是Eclipse IoT项目的一部分，该框架包括CoAP客户端
和服务器实现，支持的安全模式包括PSK、Raw Public Key和X.509证
书。本节将构建一个具有PSK安全模式的CoAPs服务，PSK Identity默
认为“identity”,PSK为字符串形式“password”。CoAPs服务器中包括两
个资源——secure和time，这两个资源仅支持GET方法。

   本节示例使用Maven工具构建Java应用，示例代码包括两个主要
文件：CoAPsPSKServer.java和pom.xml。其中CoAPsPSKServer.java包
括CoAPs服务器实现代码，而pom.xml为一个Maven构建脚本，其作
用与CMake工具中的CMakeLists.txt类似。

   CoARs客户端与CoAPs服务器框架如图16-2所示。










    689

## Page 690

图16-2 CoAPs客户端与CoAPs服务器

注意：为了便于读者测试CoAPs服务，本节已经在域名为
iotwuxi.org服务器内部署了CoAPs测试服务，该服务端口号为5682。
在后续CoAPs客户端示例中，默认将与该服务器进行连接。本节主要
说明构建与部署CoAPs服务器的方法。










690

## Page 691

16.4.1 服务器代码

由于篇幅限制，代码清单16-1中只给出部分函数，完整代码见本
书GitHub代码仓库。本节示例位于16_coaps/javacf-src文件夹中。

代码清单16-1 CoAPs服务器实现




import java.net.InetSocketAddress;
import java.util.Date;
import java.util.logging.Level;
import org.eclipse.californium.core.CaliforniumLogger;
import org.eclipse.californium.scandium.dtls.pskstore.InMemoryPskStore;
// 省略部分代码
public class CoAPsPSKServer
{
 static {
  CaliforniumLogger.initialize();
  CaliforniumLogger.setLevel(Level.CONFIG);
  ScandiumLogger.initialize();
  ScandiumLogger.setLevel(Level.FINER);
 }
 public static final int DTLS_PORT = 5682;
 public static void main( String[] args )
 {
  CoapServer server = new CoapServer();
  server.add(new CoapResource("secure") {
         @Override
         public void handleGET(CoapExchange exchange) {
          exchange.respond(ResponseCode.CONTENT, "Hello Security!");
         }
  });
  server.add(new CoapResource("time") {
         @Override
         public void handleGET(CoapExchange exchange) {
          Date date = new Date();
          exchange.respond(ResponseCode.CONTENT,
             new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(date));
         }
  });
  // Pre-shared secrets
  InMemoryPskStore pskStore = new InMemoryPskStore();
  pskStore.setKey("identity", "password".getBytes());
  DtlsConnectorConfig.Builder config =
          new DtlsConnectorConfig.Builder(new InetSocketAddress(DTLS_PORT));
  config.setSupportedCipherSuites(
          new CipherSuite[]{CipherSuite.TLS_PSK_WITH_AES_128_CCM_8,
          CipherSuite.TLS_PSK_WITH_AES_128_CBC_SHA256});
  config.setPskStore(pskStore);
  DTLSConnector connector = new DTLSConnector(config.build());
  server.addEndpoint(
          new CoapEndpoint(connector, NetworkConfig.getStandard()));
  server.start();



          691

## Page 692

System.out.println("Secure CoAP PSK Server listening on port:" + DTLS_PORT);
}
}










692

## Page 693

    16.4.2 代码说明

    1）配置CoAPs服务端口号，示例代码中将其指定为5682。


    public static final int DTLS_PORT = 5682;


   2）为CoAPs服务增加两组资源，其中secure资源支持GET方法，
可返回一个固定字符串“Hello Security!”，time资源也支持GET方法，
可返回当前服务器时间，返回格式为“yyyy-MM-dd HH:mm:ss”。


    CoapServer server = new CoapServer();
    server.add(new CoapResource("secure") {
       // 省略部分代码
    });
    server.add(new CoapResource("time") {
       // 省略部分代码
    });


    3）定义PSK_Identity和PSK，本示例中PSK_Identity
    为“identity”，PSK为“password”。


    InMemoryPskStore pskStore = new InMemoryPskStore();
    pskStore.setKey("identity", "password".getBytes());


    4）定义服务器支持的密码套件，此处服务器支持两种密码套件
    TLS_PSK_WITH_AES_128_CCM_8和
    TLS_PSK_WITH_AES_128_CBC_SHA256，16.3节已经指出
    TLS_PSK_WITH_AES_128_CCM_8为必选密码套件，所有的CoAPs
    服务器均需要支持该密码套件。


    693

## Page 694

config.setSupportedCipherSuites(
new CipherSuite[]{CipherSuite.TLS_PSK_WITH_AES_128_CCM_8,
CipherSuite.TLS_PSK_WITH_AES_128_CBC_SHA256});



5）构造一个DTLS连接实例，并将一个CoapEndpoint实例加入
server中，最后通过server.start()启动CoAPs服务器。



DTLSConnector connector = new DTLSConnector(config.build());
server.addEndpoint(
new CoapEndpoint(connector, NetworkConfig.getStandard()));
server.start();










694

## Page 695

16.4.3 pom.xml文件

      为了正确使用Java Californium框架，需要在POM文件中引入
californium-core和scandium。此处californium-core的版本编号为2.0.0-
M2，而scandium的版本编号同样为2.0.0-M2。



    <dependencies>
    <dependency>
    <groupId>org.eclipse.californium</groupId>
    <artifactId>californium-core</artifactId>
    <version>2.0.0-M2</version>
    </dependency>
    <dependency>
    <groupId>org.eclipse.californium</groupId>
    <artifactId>scandium</artifactId>
    <version>2.0.0-M2</version>
    </dependency>
    </dependencies>



    在POM文件中自定义一个名为assembly.mainClass的变量，该变
    量指向CoAPsPSKServer。



    <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <!--定义一个mainclass变量-->
    <assembly.mainClass>org.iotwuxi.embedded.CoAPsPSKServer</assembly.mainClass>
    </properties>



      为了将工程打包为一个可执行的Jar文件,还需要在POM中引入
maven-assembly-plugin组件。打包过程中需要指定mainClass，此处直
接引用上文定义的变量${assembly.mainClass}。



    <plugins>
    <plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-assembly-plugin</artifactId>
    <configuration>


    695

## Page 696

          <appendAssemblyId>false</appendAssemblyId>
          <archive>
          <manifest>
          <addClasspath>true</addClasspath>
          <mainClass>${assembly.mainClass}</mainClass>
          <addDefaultImplementationEntries>
              true
          </addDefaultImplementationEntries>
          </manifest>
          </archive>
          <descriptorRefs>
          <descriptorRef>jar-with-dependencies</descriptorRef>
          </descriptorRefs>
</configuration>
<executions>
          <execution>
          <id>make-assembly</id>
          <phase>package</phase>
          <goals>
          <goal>single</goal>
          </goals>
          </execution>
</executions>
</plugin>
</plugins>










          696

## Page 697

16.4.4 构建与执行

       完成CoAPsPSKServer.java和pom.xml文件之后，可使用mvn命令
构建可执行Jar文件。在控制台中输入以下指令：

$ mvn clean package

                  打包工作完成之后，将在pom.xml文件同级目录中生成一个名为
target的文件夹，该文件夹中包含名为coaps-psk-server-1.0-
SNAPSHOT.jar的目标Jar文件。进入target文件夹后，可通过Java指令
启动CoAPs服务器。在控制台中输入以下指令：

$ java -jar coaps-psk-server-1.0-SNAPSHOT.jar
// 省略部分输出信息
Secure CoAP PSK Server is listening on port: 5682

  CoAPs服务器将绑定本地所有网卡，并在5682端口提供相应的服
务。










697

## Page 698

16.5 构建CoAPs客户端

                第15章示例中通过OpenSSL工具构建了一个DTLS服务器，服务
器和客户端通过PSK方式建立DTLS连接。客户端与服务器完成DTLS
握手之后，服务器直接返回客户端所请求的内容，两者并没有对请求
和响应内容做过多的处理。而在CoAPs应用中，客户端向服务器发送
的请求内容必须符合CoAP协议规范，而服务器返回的响应内容也必
须符合CoAP协议规范。虽然CoAPs应用与DTLS示例请求响应内容不
同，但是两者却具有相同的握手过程。DTLS应用与CoAPs应用的关
系如图16-3所示。

              由于CoAPs应用与DTLS应用握手过程相同，所以mbedtls的相关
配置参数也几乎相同，由于篇幅限制本节不再一一列举。示例代码中
所访问的CoAPs服务器部署于阿里云主机中，该云主机的域名为
iotwuxi.org，IP地址为139.196.187.107，CoAPs服务端口号为5682。
在DTLS握手成功后，CoAPs客户端会向服务器发送请求获取当前时
间。










698

## Page 699

    图16-3 DTLS应用与CoAP应用之间的关系

           注意：由于篇幅限制，示例代码中只给出部分函数，完整代码见
本书GitHub代码仓库。本节示例位于16_coaps文件夹中。另外，
mbedtls_config.h中所启用的配置仅限于本节示例，其他应用请根据实
际情况修改。










699

## Page 700

16.5.1 示例代码

      示例代码中省略了握手过程，这部分代码与第15章基本一致。另
外，客户端代码中还使用了Zephyr用于管理网络数据包的相关接口，
如net _reserve、net _alloc和net _frag_add等接口，示例
      _pkt_get _buf _pkt
中将使用上述接口申请一个128字节的缓冲区，用于发送和接收coap
数据。CoAPs客户端示例代码如代码清单16-2所示。

      代码清单16-2 CoAPs客户端实现



    // 省略头文件应用
    #define SERVER_PORT  "5682"
    #define SERVER_ADDR   "iotwuxi.org"
    const char psk_id[] = "identity\0";
    const uint8_t psk[] = "password\0";
    const char *const uri_path = "time";
    void main(void)
    {
     // 省略握手过程及网络缓冲区分配代码
     coap_packet_init(&request, pkt, 1, COAP_TYPE_CON, 8,
         coap_next_token(), COAP_METHOD_GET, coap_next_id());
     coap_packet_append_option(&request,
                             COAP_OPTION_URI_PATH, uri_path, strlen(uri_path));
     mbedtls_printf(" ok\n > Write to server ...");
     mbedtls_ssl_write(&ssl, frag->data, frag->len);
     mbedtls_printf(" ok\n > Read from server ...");
     response = frag->data + NET_UDPH_LEN;
     ret = mbedtls_ssl_read(&ssl, response, COAP_BUF_SIZE - 1);
     frag->len = ret + NET_UDPH_LEN;
     coap_packet_parse(&cpkt, pkt, NULL, 0);
     mbedtls_printf(" ok\n > Parse coap packet ...");
     len = COAP_BUF_SIZE - 1;
     frag = coap_packet_get_payload(&cpkt, &offset, &len);
     mbedtls_printf(" ok\n\n   . [COAP] Response Code: %d\n",
                         coap_header_get_code(&cpkt));
     mbedtls_printf("    . [COAP] Response Message id: %d\n",
                         coap_header_get_id(&cpkt));
     mbedtls_printf("    . [COAP] Response Payload: %s\n", frag->data + offset);
     mbedtls_ssl_close_notify(&ssl);
     mbedtls_net_free(&ctx);
     mbedtls_ssl_free(&ssl);
     mbedtls_ssl_config_free(&conf);
     mbedtls_ctr_drbg_free(&ctr_drbg);
     mbedtls_entropy_free(&entropy);
    }




                         700

## Page 701

    16.5.2 代码说明

      1）设置PSK_Identity和PSK，此处设置应与服务器配置保持一
    致。


    const char psk_id[] = "identity\0";
    const uint8_t psk[] = "password\0";

            2）构造CoAP请求。coap_packet_init()函数可以指定CoAP请求中
    的报文类型、Token、请求方法和报文编号。其中报文类型为CON，
    请求方法为GET。一个CON报文必须对应一个ACK报文，若客户端
    没有在指定时间内收到ACK报文将触发重传机制。Token长度为8，
    Token值来自于Zephyr随机数获取函数sys    _rand32_get()。完成CoAP请
    求初始化工作后，再通过coap_packet    _append_option()函数把请求路
    由“time”加入到CoAP选项中。


    const char *const uri_path = "time";
    coap_packet_init(&request, pkt, 1, COAP_TYPE_CON, 8,
     coap_next_token(), COAP_METHOD_GET, coap_next_id());
    for (p = uri_path; p && *p; p++) {
     coap_packet_append_option(&request,
     COAP_OPTION_URI_PATH, *p, strlen(*p));
    }


     3）通过mbedtls_ssl_write()发送CoAP请求，mbedtls将把明文形式
的CoAP请求加密之后发送至CoAPs服务器。


    mbedtls_ssl_write(&ssl, frag->data, frag->len);



    701

## Page 702

     4）通过mbedtls_ssl_read()获取CoAP响应，并通过
coap_packet_parse()函数解析CoAP响应。


    mbedtls_ssl_read(&ssl, response, COAP_BUF_SIZE - 1);
    coap_packet_parse(&cpkt, pkt, NULL, 0);


     5）通过coap_packet_get_payload()函数获取payload，将主要信息
打印至控制台。


    frag = coap_packet_get_payload(&cpkt, &offset, &len);










    702

## Page 703

    16.5.3 编译与执行

    本示例默认运行于necluo_f429zi平台。示例中客户端地址和网关
    地址定义在prj_nucleo_f429zi.conf配置文件中，可根据实际情况进行
    修改。IP地址配置宏定义如下：



    # necluo_f429zi开发板IP地址
    CONFIG_NET_CONFIG_MY_IPV4_ADDR="{本机IP地址}"
    # 网关IP地址
    CONFIG_NET_CONFIG_MY_IPV4_GW="{本机IP地址}"



     运行过程中，应用程序将把运行结果输出至串口控制台，所以应
用程序下载至开发板运行前，需要新建终端并通过minicom工具打开
指定串口。操作指令如下：




    # 请根据实际情况修改串口名称
    $ sudo minicom -b 115200 -D /dev/ttyACM0



     COAPs示例中RAM空间和FLASH空间的消耗情况与DTLS示例相
差不多，示例中共消耗约107KB FLASH空间和约49KB RAM空间。
编译与运行过程如下：




    # 进入示例代码文件夹
    $ cd 16_coaps
    # 新建一个build目录，用于存放临时文件
    $ mkdir -p build && cd build
    # 通过cmake指令生成nucleo_f429zi平台makefile文件
    $ cmake -DBOARD=nucleo_f429zi ..
    # 编译并查看资源消耗情况
    $ make
    Memory region     Used Size Region Size %age Used
             FLASH:       107480 B     2 MB     5.13%
               CCM:           0 GB    64 KB     0.00%
              SRAM:        49008 B   256 KB    18.70%
          IDT_LIST:          216 B     2 KB    10.55%



    703

## Page 704

# 下载到开发板运行
$ make flash
# 串口控制台输出
. Seeding the random number generator ... ok
. Setting up the SSL/TLS structure ... ok
. Connecting to iotwuxi.org:5682 ...  ok
. Performing the SSL/TLS handshake ... ok
> Set coap packet ...  ok
> Write to server ...  ok
> Read from server ...  ok
> Parse coap packet ... ok
. [COAP] Response Code: 69
. [COAP] Response Message id: 1
. [COAP] Response Payload: 2018-09-24 14:19:29










                       704

## Page 705

16.6 本章小结

   通过本章的示例可以发现，mbedtls提供的TLS/DTLS组件是其他
物联网应用层协议的基础。CoAP是一种专门为物联网设备设计的应
用层协议，协议本身并没有提供安全机制，需要借助TLS/DTLS构建
安全通道，而mbedtls可以为CoAP这样的应用层协议提供TLS/DTLS
功能，通过mbedtls_ssl_handshake()完成握手过程之后，再使用
mbedtls_ssl_write()发送CoAP报文，或使用mbedtls_ssl_read()接收
CoAP报文。

   mbedtls面向物联网终端设备设计，在占用较少资源的情况下为
物联网设备提供安全连接服务。mbedtls加速了TLS/DTLS在受限制设
备中的应用，简化了嵌入式加密与解密应用的开发与移植工作，有助
于物联网安全应用的发展。










    705

## Page 706

        参考文献

   [1] 结城浩.图解密码技术[M].北京：人民邮电出版社，2015.

   [2] 彭长根.现代密码学趣味之旅[M].北京：金城出版社，2015.

   [3] Ivan Ristic.HTTPS权威指南：在服务器和Web应用上部署
SSL TLS和PKI[M].杨洋，等译.北京：人民邮电出版，2016.

   [4] Christof Paar，Jan Pelzl.深入浅出密码学——常用加密技术
原理与应用[M].马小婷，译.北京：清华大学出版，2012.

   [5] 杨波.现代密码学[M].4版.北京：清华大学出版社，2017.

   [6] Kenneth H Rosen.初等数论及其应用[M].2版.夏鸿刚，译.北
京：机械工业出版社，2016.

   [7] 陈恭亮.信息安全数学基础[M].2版.北京：清华大学出版社，
2017.

   [8] Douglas R Stinson.密码学原理与实践[M].3版.冯登国，等译.
北京：电子工业出版社，2015.

   [9] William Stallings.网络安全基础应用与标准[M].5版.白国强，
等译.北京：清华大学出版社，2014.

   [10] William Stallings.密码编码学与网络安全——原理与实践

        706

## Page 707

[M].7版.王后珍，等译.北京：电子工业出版社，2017.

 [11]  张明德，刘伟.PKI/CA与数字证书技术大全[M].北京：电子
工业出版社，2015.

 [12]  梁栋.Java加密与解密的艺术[M].北京：机械工业出版社，
2014.

 [13]  Nitesh Dhanjani.物联网设备安全[M].林林，等译.北京：机
械工业出版社，2017.

 [14]  刘健皓，王奥博.智能硬件安全[M].北京：电子工业出版
社，2016.

 [15]  张之津，李胜广，薛艺泽.智能卡安全与设计[M].北京：清
华大学出版社，2010.

 [16]  徐凯.IoT开发实战CoAP卷[M].北京：机械工业出版社，
2017.










707

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[books/密码技术与物联网安全mbedtls开发实战.pdf]]`
