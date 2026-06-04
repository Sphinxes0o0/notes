---
type: source
source-type: book
title: "手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解"
path: books/手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解.pdf
source-md5: 5bdb1da53cbd35c29c354e6a77d28043
size: 19549 KB
category: book
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解

> Ingested from `books/手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解.pdf` via `lit parse` on 2026-06-04.
> Source file: 19.09 MB.

## Page 1

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 2

网络空间安全技术丛书

手机安全和可信应用开发指南：    TrustZone
与OP-TEE技术详解

帅峰云　黄腾　宋洋　编著

ISBN：978-7-111-60956-8

本书纸版由机械工业出版社于2018年出版，电子版
由华章分社（北京华章图文信息有限公司，北京奥
维博世图书发行有限公司）全球范围内制作与发
行。

版权所有，侵权必究

客服热线：+ 86-10-68995265

客服信箱：service@bbbvip.com

官方网址：www.hzmedia.com.cn

新浪微博 @华章数媒

微信公众号 华章电子书（微信号：hzebook）


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 3

           目录
推荐序
前言
致谢
第一篇　基础技术篇
第1章　可信执行环境
  1.1　系统存在的安全问题
  1.2 TEE如何保护数据安全
  1.3　现有TEE解决方案
   1.3.1　智能手机领域的TEE
   1.3.2　智能电视领域的TEE
   1.3.3   IoT领域及其他领域的TEE
  1.4　为什么选择OP-TEE
第2章　ARM的TrustZone技术
  2.1 TrustZone技术
   2.1.1　片上系统硬件框架
   2.1.2   ARMv7架构的TrustZone技术
   2.1.3   ARMv8架构的TrustZone技术
  2.2 ARM安全扩展组件
   2.2.1   AXI总线上安全状态位的扩展
   2.2.2   AXI-to-APB桥的作用
   2.2.3   TrustZone地址空间控制组件
   2.2.4   TrustZone内存适配器组件
   2.2.5   TrustZone保护控制器组件
   2.2.6   TrustZone中断控制器组件


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
           更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 4

2.2.7  Cache和MMU的扩展
2.3  TrustZone技术对资源隔离的实现
2.3.1　中断源的隔离
2.3.2　片上RAM和片上ROM的隔离
2.3.3　片外DRAM的隔离
2.3.4　外围设备的隔离
2.4　小结
第3章　ARM可信固件
3.1　为什么使用ATF
3.2   ATF的主要功能
3.3  ATF与TEE的关系
3.4　小结
第4章　OP-TEE运行环境的搭建及编译
4.1　获取OP-TEE代码并搭建运行环境
4.1.1  OP-TEE开发环境的搭建
4.1.2　获取OP-TEE的源代码
4.1.3　获取编译OP-TEE的toolchain
4.1.4　编译QEMU
4.1.5　运行OP-TEE
4.1.6　运行xtest和
optee_example_hello_world
4.2　运行CA和TA示例
4.2.1　示例代码的获取和集成
4.2.2　目录和文件创建
4.2.3   CA端代码的修改
4.2.4   TA端代码的修改

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 5

4.2.5   TA和CA在OP-TEE的集成
4.3  OP-TEE源代码结构
4.4  OP-TEE编译
4.4.1　编译目标的依赖关系
4.4.2   bios.bin镜像的生成过程
4.4.3   run-only目标的执行
4.5　小结
第二篇　系统集成篇
第5章　QEMU运行OP-TEE的启动过程
5.1  bios.bin的入口函数
5.2  OP-TEE镜像的加载和启动
5.3  Linux内核镜像的加载和启动
5.4  rootfs的挂载
5.5  OP-TEE驱动的启动
5.6  tee_supplicant的启动
5.7　小结
第6章　安全引导功能及ATF的启动过程
6.1　安全引导的作用
6.2　安全引导的原理
6.2.1   ARMv7安全引导的过程
6.2.2   ARMv8安全引导的过程
6.3   ATF的启动过程
6.3.1   ATF中bl1的启动
6.3.2   ATF中bl2的启动
6.3.3   ATF中bl31的启动
6.3.4   ATF中bl32的启动

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 6

   6.3.5   ATF启动过程小结
6.4　小结
   第7章　OP-TEE OS的启动过程
   7.1 OP-TEE镜像启动过程
   7.1.1   OP-TEE OS的入口函数
   7.1.2   OP-TEE的内核初始化过程
   7.1.3   OP-TEE服务项的启动
   7.1.4   OP-TEE驱动的挂载
   7.2 ARM64位与ARM32位OP-TEE启动过程的
   差异
   7.3　小结
   第8章　OP-TEE在REE侧的上层软件
   8.1 OP-TEE的软件框架
   8.2 REE侧libteec库提供的接口
   8.2.1   libteec库提供的接口说明
   8.2.2   CA调用libteec库中接口的流程
   8.3 REE侧的守护进程——tee_supplicant
   8.3.1   tee_supplicant编译生成和自启动
   8.3.2   tee_supplicant入口函数
   8.3.3   tee_supplicant存放RPC请求的结构体
   8.3.4   tee_supplicant中的无限循环
   8.3.5   tee_supplicant获取TA的RPC请求
   8.3.6   TA RPC请求的解析
   8.3.7   RPC请求的处理
   8.3.8　回复RPC请求
   8.4　各种RPC请求的处理

   https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
           更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 7

8.4.1　加载TA镜像
8.4.2　操作REE侧的文件系统
8.4.3　操作RPMB
8.4.4　分配共享内存
8.4.5　释放共享内存
8.4.6　记录程序执行效率
8.4.7　网络套接字操作
8.5　小结
第9章　REE侧OP-TEE的驱动
9.1 OP-TEE驱动模块的编译保存
9.2 REE侧OP-TEE驱动的加载
9.2.1　设备号和class的初始化
9.2.2  optee_driver_init函数
9.2.3　挂载驱动的probe操作
9.2.4　获取切换到Monitor模式或EL3的接口
9.2.5　驱动版本和API版本校验
9.2.6　判定OP-TEE是否预留共享内存空间
9.2.7　配置驱动与OP-TEE之间的共享内存
9.2.8　分配和设置tee0和teepriv0的设备信息
结构体变量
9.2.9  tee0和teepriv0设备的注册
9.2.10　请求队列的初始化
9.2.11　使能TEE中共享内存的缓存
9.2.12 OP-TEE驱动挂载的总结
9.3 REE侧用户空间对驱动的调用过程
9.4 OP-TEE驱动中重要的结构体变量

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 8

      9.4.1 OP-TEE驱动的file_operation结构体变
      量tee_fops
      9.4.2 tee0设备的tee_driver_ops结构体变量
      optee_ops
      9.4.3 teepriv0设备的操作结构体变量
      optee_supp_ops
      9.4.4　共享驱动缓存操作变量
      tee_shm_dma_buf_ops
    9.5 OP-TEE驱动与OP-TEE之间共享内存的注
    册和分配
    9.6 libteec库中的接口在驱动中的实现
      9.6.1 libteec库中的open操作
      9.6.2 libteec库中的release操作
      9.6.3 libteec执行get_version操作
      9.6.4 libteec库中的open session操作
      9.6.5 libteec库中的invoke操作
    9.7 tee_supplicant接口在驱动中的实现
      9.7.1　接收OP-TEE的RPC请求
      9.7.2　获取OP-TEE的RPC请求
      9.7.3 OP-TEE的RPC请求的返回
    9.8　小结
第三篇　OP-TEE内核篇
  第10章　ARM核安全态和非安全态间的切换
    10.1 ARMv7基本知识
      10.1.1 ARMv7运行模式扩展
      10.1.2　安全状态位扩展

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 9

10.1.3　重要寄存器
10.1.4　安全监控模式调用的汇编指令
10.2 Monitor模式下的处理过程
10.2.1   Monitor模式对安全监控模式调用的
处理
10.2.2　正常世界状态中触发安全监控模式
调用的处理过程
10.2.3　安全世界状态中触发安全监控模式
调用的处理过程
10.3 ARMv8基本知识
10.3.1   ARM核运行模式的新定义
10.3.2   ARMv8安全状态位扩展
10.3.3　寄存器资源
10.3.4　安全监控模式调用汇编指令
10.4 EL3的处理过程
10.4.1   ATF中EL3异常向量表的注册
10.4.2   EL3处理安全监控模式调用的流程
10.4.3　安全世界状态中触发安全监控模式
调用的处理过程
10.4.4　正常世界状态中触发安全监控模式
调用的处理过程
10.4.5   opteed_smc_handler函数
10.5　小结
第11章　OP-TEE对安全监控模式调用的处理
11.1 OP-TEE的线程向量表
11.2 ARMv7中Monitor模式对安全监控模式

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 10

 调用的处理
 11.3 ARMv8中EL3处理安全监控模式调用的
 实现
 11.4 OP-TEE对快速安全监控模式调用的处理
 11.5 OP-TEE对标准安全监控模式调用的处理
   11.5.1 OP-TEE对RPC请求返回操作的处理
   11.5.2 OP-TEE对libteec库触发的安全监控
   模式调用的处理
 11.6　小结
第12章　OP-TEE对中断的处理
 12.1　系统的中断处理
 12.2　中断控制器
   12.2.1 GIC寄存器
   12.2.2 ARMv7 SCR寄存器的设定
   12.2.3 ARMv8 SCR寄存器的设定
   12.2.4 GICv2架构
   12.2.5 GICv3架构
 12.3　异常向量表配置
   12.3.1 ARMv7中Monitor模式的异常向量表
   12.3.2 ARMv8中EL3阶段的异常向量表
   12.3.3 OP-TEE异常向量的配置
 12.4 OP-TEE的线程向量表
 12.5　全局handle变量的初始化
 12.6 ARMv7 Monitor对FIQ事件的处理
 12.7 ARMv8 EL3阶段对FIQ事件的处理
 12.8 OP-TEE对FIQ事件的处理

   https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 11

12.9 OP-TEE对IRQ事件的处理
12.10　小结
第13章　OP-TEE对TA操作的各种实现
13.1　创建会话在OP-TEE中的实现
13.1.1　静态TA的创建会话操作
13.1.2　动态TA的创建会话操作
13.2　调用TA命令操作在OP-TEE中的实现
13.2.1　静态TA的调用命令操作的实现
13.2.2　动态TA的调用命令操作实现
13.3　关闭会话操作在OP-TEE中的实现
13.3.1　静态TA的关闭会话操作
13.3.2　动态TA的关闭会话操作
13.4　小结
第14章　OP-TEE的内存和缓存管理
14.1　物理内存和缓存数据的硬件安全保护
14.1.1　内存设备安全区域的隔离
14.1.2 MMU和缓存中数据的安全隔离
14.2 ARM核对内存的访问
14.2.1 ARM核获取内存数据的过程
14.2.2　获取缓存数据的过程
14.2.3　缓存和TLB中条目的一致性
14.3 OP-TEE对内存区域的管理
14.3.1 OP-TEE中内存区域的类型
14.3.2　内存区域编译设置
14.4 MMU的初始化和映射页表
14.4.1 MMU的初始化入口函数

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 12

14.4.2　物理地址到虚拟地址表的建立
14.4.3   MMU转换页表的创建
14.4.4   MMU寄存器配置
14.5  OP-TEE内存安全权限检查
14.6　系统的共享内存
14.6.1　共享内存的配置
14.6.2   OP-TEE驱动与OP-TEE之间的共享
内存
14.6.3   OP-TEE内核空间与用户空间之间的
共享内存
14.7　数据是否需要写入Cache
14.8　小结
第15章　OP-TEE中的线程管理
15.1  OP-TEE中的线程
15.2　线程状态切换
15.2.1   Free态到Active态的实现
15.2.2   Active态到Suspend态的实现
15.2.3   Suspend态到Active态的实现
15.2.4   Active态到Free态的实现
15.3　线程运行时的资源
15.3.1　线程数据结构体
15.3.2   OP-TEE分配的内核栈
15.3.3　线程运行于用户空间的资源
15.3.4   tee_ta_session结构体
15.4　线程运行时资源的使用关系
15.5  OP-TEE中线程的调度

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 13

    15.6　线程的死锁
    15.6.1　死锁的原理
    15.6.2　防止死锁
    15.7　小结
    第16章　OP-TEE的系统调用
    16.1  OP-TEE系统调用的作用
    16.2  OP-TEE系统调用的实现
    16.2.1　系统调用的整体流程
    16.2.2　系统调用的定义
    16.2.3　系统调用表tee_sv_syacall_table
    16.3　小结
    第17章　OP-TEE的IPC机制
    17.1  IPC机制的作用
    17.2  IPC机制的原理
    17.3  IPC的实现
    17.3.1   TA调用其他TA的实现
    17.3.2   TA调用系统服务和安全驱动的实现
    17.3.3   TA对密码学系统服务的调用实现
    17.3.4　对SE功能模块进行操作的系统服务
    17.3.5　加载TA镜像的系统服务
    17.4　小结
第四篇　应用开发篇
    第18章　TA镜像的签名和加载
    18.1                                                 TA镜像文件的编译和签名
    18.1.1   TA镜像文件的编译
    18.1.2　对TA镜像文件的签名

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
                                 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 14

18.2 TA镜像的加载
18.2.1   REE侧获取TA镜像文件的内容
18.2.2　加载TA镜像的RPC请求
18.2.3   RPC请求的发送
18.2.4　读取TA镜像文件内容到共享内存
18.3 TA镜像合法性的验证
18.3.1　验证TA镜像合法性使用的RSA公钥
的产生和获取
18.3.2   TA镜像文件合法性的检查
18.4　加载TA镜像到OP-TEE的用户空间
18.5 TA运行上下文的初始化
18.6　小结
第19章　OP-TEE中的密码学算法
19.1　算法使用示例
19.1.1　示例代码获取和集成
19.1.2　板级编译文件的修改
19.1.3　通用编译文件的修改
19.1.4　编译运行
19.2 OP-TEE中的SHA算法
19.2.1   TA中使用SHA算法的实现
19.2.2   SHA算法实现接口说明
19.3 OP-TEE中的AES算法
19.3.1   TA中使用AES算法的实现
19.3.2   AES算法实现接口说明
19.4 OP-TEE中的RSA算法
19.4.1   TA中使用RSA算法的实现

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 15

19.4.2 RSA算法实现接口说明
19.5　小结
第20章　OP-TEE的安全存储
20.1　安全存储简介
20.2　安全存储使用示例
20.2.1　示例代码获取和集成
20.2.2　板级编译文件的修改
20.2.3　通用编译文件的修改
20.2.4　编译运行
20.3　安全存储功能使用的密钥
20.3.1　安全存储密钥
20.3.2　可信应用的存储密钥
20.3.3　文件加密密钥
20.4　安全文件、dirf.db文件的数据格式和操
作过程
20.4.1 dirf.db文件和安全文件的格式
20.4.2　安全存储功能中使用的重要结构体
20.4.3　安全存储中的文件节点组成
20.4.4　查询安全文件中的特定数据块
20.5　安全存储文件的创建
20.5.1　安全存储软件框架
20.5.2 dirf.db文件的创建
20.5.3　安全文件的创建
20.6　安全文件的打开操作
20.6.1　安全文件的打开
20.6.2　打开dirf.db文件并建立节点树

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 16

20.6.3　安全文件在/data/tee目录下的文件编
号
20.6.4　打开特定安全文件
20.7　安全文件的读写操作
20.7.1　安全文件中数据的读取
20.7.2　安全文件中数据的写入
20.8　安全文件中数据的加解密
20.8.1　各种类型数据的组成及作用
20.8.2　元数据的加密
20.8.3　数据块区域的加密策略
20.9　小结
第21章　可信应用及客户端应用的开发
21.1 TA及CA的基本概念
21.2 GP标准
21.3 GP标准对TA属性的定义
21.4 GP标准定义的接口
21.4.1   GP定义的客户端接口
21.4.2   GP定义的内部接口
21.5 TA和CA的实现
21.5.1　建立CA和TA的目录结构
21.5.2   CA代码的实现
21.5.3   TA代码的实现
21.6 TA和CA的集成
21.6.1   CA和TA的Makefile的修改
21.6.2   OP-TEE中comm.mk和xxx.mk文件的
修改

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 17

    21.7  TA和CA的调试
    21.8  TA和CA的使用
    21.9　小结
    第22章　安全驱动的开发
    22.1　安全设备的硬件安全隔离
    22.2  OP-TEE中安全驱动的框架
    22.2.1　系统服务层
    22.2.2　驱动层
    22.2.3　驱动文件在源代码中的位置
    22.3　安全驱动的开发过程和示例
    22.3.1　示例代码获取和集成
    22.3.2　驱动实现
    22.3.3　添加系统服务
    22.3.4　添加系统调用
    22.3.5　测试使用的TA和CA
    22.4　安全驱动示例的测试
    22.5　小结
    第23章　终端密钥在线下发系统
    23.1　密钥在线下发系统的框架
    23.2　密钥在线下发的数据包格式
    23.3　密钥在线下发系统示例
    23.3.1　示例代码获取和集成
    23.3.2　板级编译文件的修改
    23.3.3　通用编译文件的修改
    23.3.4　编译运行
    23.4　离线工具的使用

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 18

23.5　小结
第24章　基于OP-TEE的在线支付系统
24.1　在线支付系统的基本框架
24.2　可信通信通道
24.3　数据交互协议
24.3.1　数据头部区域
24.3.2　数据区域
24.3.3　电子签名区域
24.3.4　交互数据包的格式
24.4　在线支付系统示例的实现
24.4.1　第一次握手请求
24.4.2　第二次握手数据的解析
24.4.3　第三次握手请求
24.4.4　支付请求
24.4.5　支付反馈
24.5　示例的集成
24.5.1　示例代码的获取和集成
24.5.2　板级编译文件的修改
24.5.3　通用编译文件的修改
24.5.4　编译运行
24.5.5　示例支持的命令说明
24.5.6　服务器端工具
24.6　组包操作嵌入内核
24.7　支付系统与生物特征的结合
24.8　小结
第25章　TEE可信应用的使用领域

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 19

25.1　在线支付
25.2　数字版权保护
25.3　身份验证
25.4　其他领域
术语表










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 20

        推荐序

  近年来随着指纹支付的盛行，如支付宝、微信
支付等，可信执行环境（Trusted Execution
Environment，TEE）被广泛应用在手机、平板电脑
等移动终端设备中。尤其是近年来谷歌对系统安全
问题越来越重视，可信执行环境已成为谷歌提升系
统安全性的重要技术之一，包含为人熟知的
keymaster、gatekeeper等，未来在Android P上还会
引入基于TUI（Trusted User Interface）衍生的
Confirmation UI，这将会为使用者提供更好的安全
体验。

  可信执行环境是一个典型的软硬件协同合作的
概念，基于ARM的TrustZone技术为系统提供资源
的物理隔离，将系统执行环境区隔为安全区域和非
安全区域。开发者通过使用安全操作系统（secure
OS）提供的API开发更多的可信应用来实现特定的
安全功能。系统的安全是环环相扣的信任链，从设
备开机的安全引导到安全操作系统的安全性验证，
一直到软件开发者开发的软件安全性验证，每层相
扣，而可信执行环境为可信应用提供了一个基础且
可信任的执行环境。

  未来TEE的发展方向是多元的，TEE的应用也


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 21

会进入更多的产业，除了目前大热的指纹识别之
外，系统也会引入更多的生物识别技术，如虹膜与
人脸识别，从摄像头获取图像到识别演算的整个过
程都会在TEE中完成。此外TUI也是重要的方向之
一，使用者如何确认所见即所支付，确认的支付金
额或转账账号不会被别人攻击或修改，都是相当重
要的安全需求。除了移动终端设备之外，车载系统
和IoT设备也都有对应的安全需求，因此在可遇见
的未来，TEE将会被广泛应用到不同领域、不同的
电子设备中。

  此外，安全应用的开发者如何将安全应用广泛
部署到不同的设备中，以及如何安全升级它们也相
当重要。当发现了软件漏洞，如何第一时间更新安
全应用并避免版本回滚的攻击，是系统安全的一个
重要议题，目前商用TEE的生态、安全应用的签名
密钥都掌握在设备制造商手中，而安全应用的独立
在线下发和更新，将是未来的重要技术发展方向。

  机缘巧合，我认识峰云已经有相当久的时间
了，他对TEE的了解相当深入，也相当用心地完成
了该书，遇到有疑问与不理解的地方，他会想方设
法地找出答案，他的专业与用心深受大家的肯定与
赞赏。本书涵盖了TEE的硬件和软件知识，通过
OP-TEE开源项目的协助，读者可以通过理论与实
践的结合，深入理解TEE的原理、设计与应用。期


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 22

望通过本书的出版，能够让更多人了解与接触TEE
的相关知识，进而发现更多的应用场景，享受更多
的安全服务，让未来的生活在因为科技更方便的同
时，使用者的隐私与安全也能得到保护。

        邱国政（Koshi）

        Trustonic中国OEM经理










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 23

    前言

早在2014年，投资过Facebook、Skype、
   Twitter等的风投公司创始人安德森就说：“移动正
   在吞噬这个世界”（mobile is eating the world）。这
   毫不夸张，全球范围内移动设备的数量已经超过了
   世界人口的总和。在如今信息化技术高速发展的时
   代，人们的生活越来越离不开智能手机，越来越多
   的业务从原先复杂的流程演变到现在只需要简单地
   在手机上按几个按键。技术是一把双刃剑，总能给
   人带来难以想象的便利，但便利总是伴随着用户隐
   私的泄漏、身份认证的滥用等一系列的安全风险。
   据著名安全漏洞报告机构FreeBuf 2017年度移动应
   用程序安全漏洞与数据泄漏状况报告指出，多达
   88%的金融类App存在内存敏感数据泄漏问题，娱
   乐类移动应用程序更是安全漏洞的重灾区，社交类
   App被仿冒的概率比其他类别平均高出10倍以上。
   如何保障移动设备的安全，提高安全认证程序的可
   靠性，一直是近几年的热门话题。

    由嵌入式处理器最大的设计商ARM公司提出
   的硬件虚拟化扩展技术TrustZone，发展到现在已经
   有十余年的光景，如今已成为智能手机平台不可或
   缺的部分。从Android 7.0开始，谷歌就明确表示，
   Android设备上有关生物特征（指纹、虹膜等）识


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 24

别的方案一定要基于可信执行环境（Trust
Execution Environment，TEE）来实现。TEE就是基
于TrustZone技术建立的具有更高安全级别的可信执
行环境，运行在TEE环境下的应用称为可信应用程
序（Trusted Application，TA）。随着TEE可信应用
开发的API的普及，国内越来越多的手机厂商开始
集成TEE以及相关的可信应用。TEE环境的提供商
也越来越多，从先前国外的Trustonic TEE、高通
QSEE到现在国内的豆荚、华为、瓶钵等，可以说
TEE的技术开发门槛在降低，应用热度在提高。在
众多TEE产品方案中，有一个优秀的开源方案逐渐
进入人们的视野，那就是OP-TEE。OP-TEE（Open
Platform Trusted Execution Environment）由ST-
Ericsson创建，由STMicroelectronics维护，2014年
ARM的开源社区Linaro将OP-TEE方案开源。截至
目前，OP-TEE一直是Linaro社区在维护的核心安全
项目之一。目前看来，进入TEE领域最好的方式就
是学习成熟的OP-TEE方案。作者便是在学习OP-
TEE的过程中完成了本书，旨在为后继的入门者扫
除一些障碍。

本书组织结构

本书将采取由浅入深的方式介绍TrustZone技术
的原理、OP-TEE的整体架构及其主要功能模块的
原理，同时介绍如何基于OP-TEE进行可信应用、

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 25

客户端应用（Client Application，CA）、安全驱动
等功能的开发。

本书主要分为四篇，总计25章，各篇的主要内
容分别如下。

   ·第一篇，基础技术篇（第1章～第4章），包
含TrustZone技术的背景和实现原理、系统基本框架
以及OP-TEE环境的搭建。
   ·第二篇，系统集成篇（第5章～第9章），分
析OP-TEE在REE和TEE中各个组件的作用和联系，
对于有一定嵌入式以及Linux/Android开发经验的读
者，该篇实质上给将OP-TEE集成到基于
ARMv7/ARMv8处理器的开发平台打下基础。
·第三篇，OP-TEE内核篇（第10章～第17
章），包含OP-TEE内核的中断处理、线程管理和
通信等主要功能的实现原理，使读者对TEE OS的
架构设计有进一步认识。

  ·第四篇，应用开发篇（第18章～第25章），
介绍基于OP-TEE在加密、解密、安全存储等方面
的实际应用，以及如何开发基于OP-TEE的可信应
用程序。如果对OP-TEE有一定了解的读者希望通
过实践开发来了解TEE的工作原理，可以直接从应


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 26

用开发篇学习。

  OP-TEE的代码量远没有Linux内核大，但其涉
及的设计之复杂、模块之丰富也不是本书能完全涵
盖的。我们的初衷是希望通过本书对重要模块的代
码和流程进行分析，使读者对OP-TEE的架构有整
体的认识，之后看到其他部分也能做到举一反三。

  本书的主要代码均引用自GitHub上OP-TEE开
源项目的源代码（链接：https://github.com/OP-
TEE/optee_os），作者在翻译了一些代码英文注释
的基础上根据自己的理解对部分代码补充了更多的
注释。如果读者对书中代码的中文注释有疑问，可
参考上述链接中的原始代码和注释。另外，OP-
TEE也有详细的文档资料（https://github.com/OP-
TEE/optee_os/tree/master/documentation），强烈建
议英文基础好的读者结合本书和官方文档来学习。
如发现本书有纰漏和错误，或者需要改进之处，希
望读者不吝指出。

本书特色

  俗话说，基础打不牢，学问攀不高。本书采取
自下而上的方式从硬件的角度介绍了TrustZone技
术，并结合源代码逐步剖析了基于TrustZone技术的
OP-TEE实现。在技术深度上，本书从入门者的角


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 27

度出发由浅入深，从最基础的开发环境的搭建到最
终的OP-TEE OS的内部实现都进行了介绍；从内容
易读性上来讲，本书提供了基础的示例代码和各种
算法的使用示例，并给出了所有示例的源代码链接
及操作的实验步骤。相信读者通过边学习边实践的
方式阅读完本书后，能够掌握TrustZone技术的基础
原理和使用OP-TEE进行实际的应用开发。
 由于任何TEE方案的源代码都属于芯片厂商的
商业机密，外界无法一览各TEE方案的实现原理，
且TrustZone也是最近几年才被正式商用的，所以网
上的资料较少。本书是作者基于多年的工作积累并
对实际工作过程中遇见的问题进行整理后形成的。

本书读者对象

 ·手机、嵌入式系统和芯片开发者及技术支持
人员；

 ·手机和嵌入式系统安全与可信应用（支付系
统、多媒体及身份识别等）开发人员；

 ·相关专业安全技术研究者和大专院校学生；
 ·广大关心安全技术的爱好者。



 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 28

        致谢

  从萌生写本书的念头到最终完成初稿共花了一
年零三个月，一路走来历经波折，其间获得了许多
朋友和老师的帮助，感恩这一切。感谢他们曾经的
陪伴和咖啡，让我有勇气将本书写完。

  感谢邱国政（Koshi）的指导以及他为本书拟
定的大纲，感谢他在写作期间提供的耐心的释疑解
惑，并在初稿完成后挤出宝贵的时间审阅全稿，提
出建设性的修改意见。

  感谢段富刚师兄在写作初期的建议、支持和鼓
励，以及在后期审稿阶段给出的修改意见，因您一
语，才使我尝试将博文整理成书稿，使内容更加完
善和系统。

  感谢樊鹏对本书稿件的审阅及结合自身在NXP
车载芯片上集成OP-TEE的实际工作经验对本书提
供的宝贵建议。

  感恩家人在写作期间给予的理解和支持。感恩
沈雪亮和林先贤曾经的教导，感谢王佞姐平时的关
心，感谢黄诚、龚强强、徐贵友等好友在我撰写本
书期间给予的无私帮助和真切鼓励。


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 29

  感谢孟庆洋博士、黄冕博士、王子亮总监、尉
鲁飞师兄对本书内容的认可和推荐。感谢邓仰东老
师和朱捷编辑在审稿期间给予的非常有益的建议和
指导，让本书的内容更加丰富和严谨。

  感谢张星茹在我考研时提供的帮助，感恩大学
那么一帮人，十年友谊一直未变。

  感谢OP-TEE开源项目组的各位大牛，正是你
们的分享精神赋予了开发者涉足TrustZone这片神秘
领地和一探TEE具体实现原理的机会。

  最后仅以此书纪念自己曾经的三十年，感恩生
命中遇见的每一个人、大学同学（于洋、郭成飞、
吼哥、涛哥、胖胖、石头、王健等一帮兄弟）、研
究生同学（刘峰、孙登高、夏轩、刘智、陈耀
闯），以及所有的朋友，是你们的出现让我过去的
三十年不曾遗憾。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 30

第一篇　基础技术篇

第1章　可信执行环境
第2章　ARM的TrustZone技术

第3章　ARM可信固件
第4章　OP-TEE运行环境的搭建及编译










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 31

第1章　可信执行环境

1.1　系统存在的安全问题

  随着移动通信和互联网技术的飞速发展，智能
设备在各个领域扮演着越来越重要的角色。据统
计，在2017年，中国使用智能手机上网的用户数已
达6亿之多。此外，无人驾驶、物联网、网络电视
等也都与智能设备相关，或者本身就是智能设备，
它们都会用到操作系统。然而由于一些黑客能够破
解智能设备的root权限，进而盗取用户数据或其他
关键信息，造成用户数据的泄露或滥用。其次，如
果用户的车载系统被黑客获取控制权限，其人身安
全将无从保障。因此手机互联网领域、电视领域、
物联网领域以及车载领域的安全越来越显得重要。

  再者，智能设备上各种应用不断涌现，若开发
人员在开发这些应用时没有针对安全进行加固保
护，则黑客可能会利用这些应用本身固有的安全漏
洞获取智能设备操系统的root权限，轻松截获用户
的敏感数据。鉴于此，如何保障智能设备的安全变
得越来越重要。

  那么，如何消除甚至杜绝这类威胁呢？除了提
高系统被破解的难度之外，最好还要在系统中提供

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 32

一个相对可信赖的运行环境，使用户的关键数据或
应用在这个相对可信赖的环境中使用和运行。这样
一来，即便系统被攻破，入侵者也无法直接获取用
户的重要信息，用户的信息安全也就实现了，这就
是可信执行环境（Trusted Execution Environment，
TEE）的主要作用和理念。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 33

1.2 TEE如何保护数据安全

  为了给移动设备提供一个安全的运行环境，
ARM从ARMv6的架构开始引入了TrustZone技术。
TrustZone技术将中央处理器（Central Processing
Unit，CPU）的工作状态分为了正常世界状态
（Normal World Status，NWS）和安全世界状态
（Secure World Status，SWS）。支持TrustZone技
术的芯片提供了对外围硬件资源的硬件级别的保护
和安全隔离。当CPU处于正常世界状态时，任何应
用都无法访问安全硬件设备，也无法访问属于安全
世界状态下的内存、缓存（Cache）以及其他外围
安全硬件设备。

  TEE基于TrustZone技术提供可信运行环境，还
为开发人员提供了应用程序编程接口（Application
Programming Interface，API），以方便他们开发实
际应用程序。

  在整个系统的软件层面，一般的操作系统（如
Linux、Android、Windows等）以及应用运行在正
常世界状态中，TEE运行在安全世界状态中，正常
世界状态内的开发资源相对于安全世界状态较为丰
富，因此通常称运行在正常世界状态中的环境为丰
富执行环境（Rich Execution Environment，

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 34

REE），而可信任的操作系统以及上层的可信应用
（Trusted Application，TA）运行于安全世界状
态，运行在安全世界状态中的系统就是前文提到的
TEE。
  对CPU的工作状态区分之后，处于正常世界状
态中的Linux即使被root也无法访问安全世界状态中
的任何资源，包括操作安全设备、访问安全内存数
据、获取缓存数据等。这很像一个保险箱，不管保
险箱的外在环境是否安全，其内部的物件都有足够
的安全性。这是因为CPU在访问安全设备或者安全
内存地址空间时，芯片级别的安全扩展组件会去校
验CPU发送的访问请求的安全状态读写信号位
（Non-secure bit，NS bit）是0还是1，以此来判定
当前CPU发送的资源访问请求是安全请求还是非安
全请求。而处于非安全状态的CPU将访问指令发送
到系统总线上时，其访问请求的安全状态读写信号
位都会被强制设置成1，表示当前CPU的访问请求
为非安全请求。而非安全请求试图去访问安全资源
时会被安全扩展组件认为是非法访问的，于是就禁
止其访问安全资源，因此该CPU访问请求的返回结
果要么是访问失败，要么就是返回无效结果，这也
就实现了对系统资源硬件级别的安全隔离和保护。

  在真实环境中，可以将用户的敏感数据保存到
TEE中，并由可信应用（Trusted Application，TA）


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 35

使用重要算法和处理逻辑来完成对数据的处理。当
需要使用用户的敏感数据做身份验证时，则通过在
REE侧定义具体的请求编号（IDentity，ID）从TEE
侧获取验证结果。验证的整个过程中用户的敏感数
据始终处于TEE中，REE侧无法查看到任何TEE中
的数据。对于REE而言，TEE中的TA相当于一个黑
盒，只会接受有限且提前定义好的合法调用，而至
于这些合法调用到底是什么作用，会使用哪些数
据，做哪些操作在REE侧是无法知晓的。如果在
REE侧发送的调用请求是非法请求，TEE内的TA是
不会有任何的响应或是仅返回错误代码，并不会暴
露任何数据给REE侧。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 36

1.3　现有TEE解决方案

  TEE是一套完整的安全解决方案，主要包含正
常世界状态的客户端应用（Client Application，
CA）、安全世界状态的可信应用，可信硬件驱动
（Secure Driver，SD）以及可信内核系统（Trusted
Execution Environment Operation System，TEE
OS），其系统配置、内部逻辑、安全设备和安全资
源的划分是与CPU的集成电路（Integrated Circuit，
IC）设计紧密挂钩的，使用ARM架构设计的不同
CPU，TEE的配置完全不一样。国内外针对不同领
域的CPU也具有不同的TEE解决方案。
  国内外各种TEE解决方案一般都遵循
GP（Global Platform）规范进行开发并实现相同的
API。GP规范规定了TEE解决方案的架构以及供TA
开发使用的API原型，开发者可以使用这些规定的
API开发实际的TA并能使其正常运行于不同的TEE
解决方案中。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 37

1.3.1　智能手机领域的TEE

   智能手机领域的芯片厂商众多，国外有高通
（Qualcomm）、三星（Samsung）、LG，国内有
展讯、联发科（MediaTek）、威盛电子（VIA）、
华为海思（Hisilicon）等，目前手机厂商和芯片厂
商支持的TEE解决关系如图1-1所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 38

图1-1 TEE解决方案关系
各家TEE解决方案的内部操作系统的逻辑会不


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 39

一样，但都能提供GP规范规定的API，对于二级厂
商或TA开发人员来说接口都是统一的。这些TEE解
决方案在智能手机领域主要用于实现在线支付（如
微信支付、支付宝支付）、数字版权保护（DRM、
Winevine Level 1、China DRM）、用户数据安全保
护、安全存储、指纹识别、虹膜识别、人脸识别等
其他安全需求。这样可以降低用户手机在被非法
root之后带来的威胁。
  Google规定在Android M之后所有的Android设
备在使用指纹数据时都需要用TEE来进行保护，否
则无法通过Google的CTS认证授权，另外Android也
建议使用硬件Keymaster和gatekeeper来强化系统安
全性。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 40

1.3.2　智能电视领域的TEE

当前的智能电视领域大多是使用Android系统
来实现的，为保护二级厂商的视频源数据以及各厂
家用户会员权益不被盗取，需要使用TEE来实现数
字版权保护、会员鉴权、用户账号信息保护等安全
功能，而TEE方案一般都是由电视芯片厂商提供
的，且所有的TEE源代码都不对外公开，即使是二
级厂商也无法获取到TEE的源代码。在我国的智能
电视领域，智能电视芯片主要有两家：星辰半导体
（Mstar）和华为海思，两家厂商使用的TEE方案都
不一样。

                                        Mstar早期的TEE方案是在CPU的一个类似于单
片机的核上运行Nuttx系统作为TEE OS来实现TEE
方案的，但最新的Mstar芯片已经改用OP-TEE方案
来实现TEE解决方案。
华为海思的安全操作系统（Secure Operating
System，Secure OS）是按照GP规范自主研发的
TEE解决方案，其手机芯片和智能电视芯片都是使
用这个TEE方案。华为海思的TEE增加了权限校验
功能（类似于白名单机制），即在使用华为海思的
TEE方案提供的API实现特定安全功能的TA时，需
要将调用该TA对应的CA接口的进程或者服务的相

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 41

关信息提前注册到TEE后方能正常使用，否则会导
致调用失败。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 42

1.3.3 IoT领域及其他领域的TEE

    物联网（Internet of Thing，IoT）领域和车载
系统领域将会是未来TEE方案使用的另外一个重要
方向，大疆无人机已经使用TEE方案来保护无人机
用户的私人数据、航拍数据以及关键的飞控算法。
ARM的M系列也开始支持TrustZone技术，如何针
对资源受限的IoT设备实现TEE也是未来TEE的重要
发展方向之一。

            而在车载领域NXP芯片已经集成OP-TEE作为
TEE方案，MediaTek的车载芯片也已集成了
Trustonic的TEE方案，相信在车载系统领域TEE也
将渐渐普及。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 43

1.4　为什么选择OP-TEE

  本书主要是介绍OP-TEE的实现原理，OP-TEE
是由非营利的开源软件工程公司Linaro开发的，从
git上可以获取OP-TEE的所有源代码，且OP-TEE支
持的芯片也越来越多，相信未来OP-TEE将有可能
是TEE领域的Linux，并得到更加广泛的运用。
  OP-TEE是按照GP规范开发的，支持QEMU、
Hikey（Linaro推广的96Board系列平台之一，使用
Hisilicon处理器）以及其他通用的ARMv7/ARMv8
平台，开发环境搭建方便，便于开发者开发自有的
上层可信应用，且OP-TEE提供了完整的软件开发
工具包（Software Development Kit，SDK），方便
编译TA和CA。OP-TEE遵循GP规范，支持各种加
解密和电子签名验签算法以便实现DRM、在线支
付、指纹和虹膜识别功能。OP-TEE也支持在芯片
中集成第三方的硬件加解密算法。除此之外，在
IoT和车载芯片领域也大都使用OP-TEE作为TEE解
决方案。

  OP-TEE由Linaro组织负责维护，安全漏洞补丁
更新和代码迭代速度较快，系统的健壮性也越来越
好，所以利用OP-TEE来研究TrustZone技术的实现
并开发TA和CA将会是一个很好的选择。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 44

本书涉及的内核源代码使用的是OP-TEE 2.4版
本，书中所有的示例都在最新版本中测试通过。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 45

第2章　ARM的TrustZone技术

2.1 TrustZone技术

   为提高系统的安全性，ARM早在ARMv6架构
中就引入了TrustZone技术[1]，且在ARMv7和
ARMv8中得到增强，TrustZone技术能提供芯片级
别对硬件资源的保护和隔离，当前在手机芯片领域
已被广泛应用。

[1] TrustZone硬件需求文档：lcu14-
500armtrustedfirmware-140919105449-
phpapp02.pdf；TrustZone白皮书：PRD29-GENC-
009492C_TrustZone_security_whitepaper.pdf。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 46

    2.1.1　片上系统硬件框架

                                        一个完整的片上系统（System on Chip，SoC）
    由ARM核、系统总线、片上RAM、片上ROM以及
    其他外围设备组件构成。只有支持TrustZone技术的
    ARM核配合安全扩展组件，才能为整个系统提供芯
    片硬件级别的保护和隔离。如图2-1所示是一个支
    持TrustZone的SoC的硬件框图。

    支持TrustZone技术的ARM核在运行时将工作
    状态划分为两种：安全状态和非安全状态。当处理
    器核处于安全状态时只能运行TEE侧的代码，且具
    有REE侧地址空间的访问权限。当处理器核处于非
    安全状态时只能运行REE侧的代码，且只能通过事
    先定义好的客户端接口来获取TEE侧中特定的数据
    和调用特定的功能。

系统通过调用安全监控模式调用（secure
    monitor call，smc）指令实现ARM核的安全状态与
    非安全状态之间的切换。而ARM核对系统资源的访
    问请求是否合法，则由SoC上的安全组件通过判定
    ARM核发送到SoC系统总线上的访问请求中的安全
    状态读写信号位（Non-secure bit，NS bit）来决
    定。只有当ARM核处于安全状态（NS bit=0）时发
    送到系统总线上的读写操作才会被识别为安全读写

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 47

操作，对应TEE侧的数据资源才能被访问。反之，
当ARM核处于非安全状态（NS bit=1）时，ARM核
发送到系统总线上的读写操作请求会被作为非安全
读写操作，安全组件会根据对资源的访问权限配置
来决定是否响应该访问请求。这也是TrustZone技术
能实现对系统资源硬件级别的保护和隔离的根本原
因。










    图2-1 SoC硬件框





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 48

2.1.2 ARMv7架构的TrustZone技术

   ARMv7架构中使用了TrustZone技术的系统软
件层面的框图如图2-2所示。










      图2-2 ARMv7系统软件框架
   在ARMv7架构中CPU在运行时具有不同的特权
等级，分别是PL0（USR）、PL1（FIQ/IRQ、
SYS、ABT、SVC、UND和MON）以及
PL2（Hyp），即ARMv7架构在原有七种模式之上
扩展出了Monitor模式和Hyp模式。Hyp模式是ARM
核用于实现虚拟化技术的一种模式。系统只有在
Monitor模式下才能实现安全状态和非安全状态的切
换。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 49

  当系统在REE侧或者TEE侧运行时，系统执行
smc（安全监控模式调用）指令进入Monitor模式，
通过判定系统SCR寄存器中对应的值来确定请求来
源（REE/TEE）以及发送目标（REE/TEE），相关
寄存器中的值只有当系统处于安全态时才可以更
改，关于安全状态与非安全状态之间的切换过程，
在本书第10章中将进行详细介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 50

2.1.3 ARMv8架构的TrustZone技术

   在ARMv8架构中改用执行等级（Execution
Level，EL）EL0～EL3来定义ARM核的运行等级，
其中EL0～EL2等级分为安全态和非安全态。
ARMv8架构与ARMv7架构中ARM核运行权限的对
应关系如图2-3所示。








    图2-3 ARMv7/v8运行权限对比
    ARMv7和ARMv8架构下特权等级和工作模式
    的对应关系分别如表2-1所示。
    表2-1 ARMv7和ARMv8架构下各模式对应关系





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 51

   ARMv7架构中的PL0（USR）对应ARMv8架构
中的EL0，PL1（SVC/ABT/IRQ/FIQ/UND/SYS）对
应ARMv8架构中的EL1，ARMv7架构中的Hyp模式
对应ARMv8架构中的EL2，而ARMv7架构中的
Mon（Monitor）则对应于ARMv8架构中的EL3。

   ARMv8架构同样也是使用安全监控模式调用
指令使处理器进入EL3，在EL3中运行的代码负责
处理器安全状态和非安全状态的切换，其中关于
TEE和REE切换的处理方式与ARMv7架构中Monitor
模式下的处理方式类似，本书第10章将结合实际代
码进行详细分析。







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 52

2.2 ARM安全扩展组件

    TrustZone技术之所以能提高系统的安全性，是
因为对外部资源和内存资源的硬件隔离。这些硬件
隔离包括中断隔离、片上RAM和ROM的隔离、片
外RAM和ROM的隔离、外围设备的硬件隔离、外
部RAM和ROM的隔离等。实现硬件层面的各种隔
离，需要对整个系统的硬件和处理器核做出相应的
扩展。这些扩展包括：

    ·对处理器核的虚拟化，也就是将AMR处理器
的运行状态分为安全态和非安全态。

    ·对总线的扩展，增加安全位读写信号线。

    ·对内存管理单元（Memory Management
Unit，MMU）的扩展，增加页表的安全位。
    ·对缓存（Cache）的扩展，增加安全位。
    ·对其他外围组件进行了相应的扩展，提供安
全操作权限控制和安全操作信号。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 53

2.2.1 AXI总线上安全状态位的扩展

  为了支持TrustZone技术，控制处理器在不同状
态下对硬件资源访问的权限，ARM对先进可扩展接
口（Advanced eXtensible Interface，AXI）系统总线
进行了扩展。在原有AXI总线基础上对每一个读写
信道增加了一个额外的控制信号位，用来表示当前
的读写操作是安全操作还是非安全操作，该信号位
称为安全状态位（NS bit）或者非安全状态位
（Non-Secure bit）。

  ·AWPROT[1]：总线写事务——低位表示安全
写事务操作，高位表示非安全写事务操作。

  ·ARPROT[1]：总线读事务——低位表示安全
读事务操作，高位表示非安全读事务操作。

  当主设备通过总线发起读写操作时，从设备或
者外围资源同时也需要将对应的PROT控制信号发
送到总线上。总线或者从设备的解码逻辑必须能够
解析该PROT控制信号，以便保证安全设备在非安
全态下不被非法访问。所有的非安全主设备必须将
安全状态位置成高位，这样就能够保证非安全主设
备无法访问到安全从设备。如果一个非安全主设备
试图访问一个安全从设备，将会在总线或者从设备


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 54

上触发一个错误操作，至于该错误如何处理就依赖
于从设备的处理逻辑和总线的配置。通常这种非法
操作最终将产生一个SLVERR（slave error）或者
DECERR（decode error）。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 55

2.2.2 AXI-to-APB桥的作用

      TrustZone同样能够保护外围设备的安全，例如
中断控制、时钟、I/O设备，因此Trust-Zone架构还
能用来解决更加广泛的安全问题。比如一个安全中
断控制器和安全时钟允许一个非中断的安全任务来
监控系统，能够为DRM提供可靠的时钟，能够为用
户提供一个安全的输入设备从而保证用户密码数据
不会被恶意软件窃取。

          AMBA3规范包含了一个低门数、低带宽的外
设总线，被称作外设总线（Advanced Peripheral
Bus，APB），APB通过AXI-to-APB桥连接到系统
总线上。而APB总线并不具有安全状态位，为实现
APB外设与TrustZone技术相兼容，APB-to-AXI桥将
负责管理APB总线上设备的安全。APB-to-AXI桥会
拒绝不匹配的安全事务设置，并且不会将该事务请
求发送给外设。









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 56

2.2.3 TrustZone地址空间控制组件

    TrustZone地址空间控制组件（TrustZone
Address Space Controller，TZASC）[1]是AXI总线上
的一个主设备，TZASC能够将从设备全部的地址空
间分割成一系列的不同地址范围。在安全状态下，
通过编程TZASC能够将这一系列分割后的地址区域
设定成安全空间或者是非安全空间。被配置成安全
属性的区域将会拒绝非安全的访问请求。

             使用TZASC主要是将一个AXI从设备分割成几
个安全设备，例如off-Soc、DRAM等。ARM的动态
内存控制器（Dynamic Memory Controller，DMC）
并不支持安全和非安全分区的功能。如果将DMC接
到TZASC上，就能实现DRAM支持安全区域和非安
全区域访问的功能。需要注意的是，TZASC组件只
支持存储映射设备对安全和非安全区域的划分与扩
展，但不支持对块设备（如EMMC、NAND flash
等）的安全和非安全区域的划分与扩展。图2-4所
示为使用TZASC组件的例子。






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 57

        图2-4 TZASC组件示意
[1] TZASC文档：
DDI0431C_tzasc_tzc380_r0p1_trm.pdf。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 58

    2.2.4 TrustZone内存适配器组件

    TrustZone内存适配器组件（TrustZone Memory
    Adapter， TZMA）[1]允许对片上静态内存（on-SoC
    Static Memory）或者片上ROM进行安全区域和非安
    全区域的划分。TZMA支持最大2MB空间的片上静
    态RAM的划分，可以将2MB空间划分成两个部
    分，高地址部分为非安全区域，低地址部分为安全
    区域，两个区域必须按照4KB进行对齐。分区的具
    体大小通过TZMA的输入信号R0SIZE来控制，该信
    号来自TZPC的输出信号TZPCR0SIZE。即通过编程
    TZPC可以动态地配置片上静态RAM或者ROM的大
    小。使用TZMA组件的链接框图如图2-5所示。





    图2-5　使用TZMA组件的链接示意
[1] TZMA文档：
cycle_models_BP141_TZMA_User_Guide_v9_1_0_DUI1083A_en.pdf。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 59

2.2.5 TrustZone保护控制器组件

    TrustZone保护控制器组件（TrustZone
Protection Controller，TZPC）[1]是用来设定
TZPCDECPORT信号和TZPCR0SIZE等相关控制信
号的。这些信号用来告知APB-to-AXI对应的外设是
安全设备还是非安全设备，而TZPCR0SIZE信号用
来控制TZMA对片上RAM或片上ROM安全区域大
小的划分。TZPC包含三组通用寄存器
TZPCDECPROT[2：0]，每组通用寄存器可以产生8
种TZPCDECPROT信号，也就是TZPC最多可以将
24个外设设定成安全外设。TZPC组件还包含一个
TZPCROSIZE寄存器，该寄存器用来为TZMA提供
分区大小信息。TZPC组件的接口示意如图2-6所
示。

    当上电初始化时，TZPC的TZPCDECROT寄存
器中的位会被清零，同时TZPCR0SIZE寄存器会被
设置成0x200，表示接入到TZMA上的片上RAM或
者ROM的安全区域大小为2MB。通过修改TZPC的
寄存器配置的值可实现用户对资源的特定配置。
TZPC的使用例子如图2-7所示。




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 60

    图2-6 TZPC组件接口示意










        图2-7 TZPC使用示例
[1] TZPC文档（BP147）：
DTO0015_primecell_infrastructure_amba3_tzpc_bp147_to.pdf。






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 61

2.2.6 TrustZone中断控制器组件

   在支持TrustZone的SoC上，ARM添加了
TrustZone中断控制器（TrustZone Interrupt
Controller，TZIC）[1]。TZIC的作用是让处理器处
于非安全态时无法捕获到安全中断。TZIC是第一级
中断控制器，所有的中断源都需要接到TZIC上。
TZIC根据配置来判定产生的中断类型，然后决定是
将该中断信号先发送到非安全的向量中断控制器
（Vector Interrupt Controller，VIC）后以nIRQ信号
发送到处理器，还是以nTZICFIQ信号直接发送到
处理器。图2-8所示为TZIC在SoC中的使用示意。









    图2-8 TZIC在SoC中的使用示意
    通过对TZIC的相关寄存器进行编程，可对
    TZIC进行配置并设定每个接入到TZIC的中断源的

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 62

中断类型。TZIC具有众多寄存器，细节说明可以参
考相关ARM的文档。在TZIC中用来设置中断源类
型的寄存器为TZICIntSelect，如果TZICIntSelect中
的某一位被设置成1，则该相应的中断源请求会被
设置成快速中断请求（Fast Interrupt Request，
FIQ）。如果某一位被设置成0，则该中断源的中断
请求会被交给VIC进行处理。如果VIC的IntSelect将
获取到的中断源设置成FIQ，那么该中断源会被再
次反馈给TZIC进行处理。
[1] TZIC文档：
DTO0013B_tzic_sp890_r0p0_to.pdf。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 63

2.2.7 Cache和MMU的扩展

  在支持TrustZone的SoC上，会对MMU进行虚
拟化，使得寄存器TTBR0、TTBR1、TTBCR在安
全状态和非安全状态下是相互隔离的，因此两种状
态下的虚拟地址转换表是独立的。

  存放在MMU中的每一条页表描述符都会包含
一个安全状态位，用以表示被映射的内存是属于安
全内存还是非安全内存。虚拟化的MMU共享转换
监测缓冲区（Translation Lookaside Buffer，
TLB），同样TLB中的每一项也会打上安全状态位
标记，只不过该标记是用来表示该条转换是正常世
界状态转化的还是安全世界状态转化的。

  Cache也同样进行了扩展，Cache中的每一项都
会按照安全状态和非安全状态打上对应的标签，在
不同的状态下，处理器只能使用对应状态下的
Cache。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 64

2.3 TrustZone技术对资源隔离的实现

  ARM处理器核的虚拟化和资源隔离是
TrustZone实现安全需求的根本。支持TrustZone的
处理器核具有虚拟化，也即将一个物理核分成安全
状态和非安全状态。当处理器处于非安全状态时，
只能访问属于非安全的外设和内存，而不能访问安
全的资源；当处理器处于安全态时，处理器既可以
访问安全资源，也可以访问非安全的资源，只有当
处理器核为安全世界状态时才可能发出PROT的安
全访问信号。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 65

2.3.1　中断源的隔离

在原来的ARM芯片中，使用VIC来对外部中断
源进行控制和管理，支持TrustZone后，ARM提出
了TZIC组件，在芯片设计时，该组件作为一级中断
源控制器，控制所有的外部中断源，通过编程TZIC
组件的相关寄存器来设定哪个中断源为安全中断源
FIQ，而未被设定的中断源将会被传递给VIC进行
处理。一般情况下VIC会将接收到的中断源设定成
普通中断请求（Interrupt Request，IRQ），如果在
VIC中将接收到的中断源设定成FIQ，则该中断源
会被反馈给TZIC组件，TZIC组件会将安全中断源
送到安全世界状态中进行处理。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 66

2.3.2　片上RAM和片上ROM的隔离

  芯片内部存在小容量的RAM或者ROM，以供
芯片上电时运行芯片ROM或者存放芯片自身相关的
数据。TrustZone架构对该部分也进行了隔离操作。
隔离操作通过使用TZMA和TZPC组件来实现。

  TZMA用来将片上RAM或者ROM划分成安全
区域和非安全区域，安全区域的大小则由接入的
TZPCR0SIZE信号来决定。而TZPCR0SIZE的值可
以通过编程TZPC组件中的TZPCR0SIZE寄存器来实
现。

  当处理器核访问片上RAM或者ROM时，
TZMA会判定访问请求的PROT信号是安全操作还
是非安全操作，如果处理器发出的请求为非安全请
求而该请求又尝试去访问安全区域时，TZMA就会
认为该请求为非法请求。这样就能实现片上RAM和
ROM的隔离，达到非安全态的处理器核无法访问片
上安全区域的RAM和ROM。






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 67

2.3.3　片外DRAM的隔离

一个完整的系统必然会有片外RAM，对片外
RAM的隔离是通过TZASC组件实现的，ARM本身
的DMC可以将DRAM分割成不同的区域，这些区域
是没有安全和非安全分类。将DMC与TZASC相连
后再挂到总线上，通过对TZASC组件进行编程可以
将DRAM划分成安全区域和非安全区域。当主设备
访问DRAM时，除需要提供物理地址之外，还会发
送PROT信号。TZASC组件首先会判定主设备需要
访问的DARM地址是属于安全区域还是非安全区
域，然后再结合接收到的PROT信号来判定该次访
问是否有效。如果PROT信号为非安全访问操作，
且访问的DRAM地址属于安全区域，则TZASC就不
会响应这次访问操作，这样就能实现DRAM中安全
区域和非安全区域的隔离。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 68

2.3.4　外围设备的隔离

  其他外围设备都会挂载到APB总线上，然后通
过AXI-to-APB桥连接到AXI总线上，AXI-to-APB结
合TZPC组件的TZPCDECROT的值及访问请求的
PROT信号来判定该访问是否有效。当处理器需要
访问外围设备时，会将地址和PROT信号发送到
AXI总线上。

  AXI-to-APB桥会对接收到的请求进行解析，获
取需要访问的所需外围设备，然后通过查询
TZPCDECROT的值来判断外设的安全类型，再根
据PROT信号就能判定该请求的安全类型。如果该
请求是非安全请求，但需要访问的外围设备属于安
全设备，则AXI-to-APB会判定该访问无效。

  通过对TZPC中的TZPCDECROT寄存器进行编
程能够设置外设的安全类型，从而做到外设在硬件
层面的隔离。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 69

2.4　小结

  本章介绍了TrustZone的原理以及在ARMv7和
ARMv8架构下TrustZone技术实现的差异。
TrustZone对系统实现了硬件隔离，将系统资源划分
成安全和非安全两种类型，同时在系统总线上增加
安全读写信号位，通过读取安全读写信号位电平来
确定当前处理器的工作状态，从而判断是否具有该
资源的访问权限。因此，TrustZone从硬件级别实现
了对系统资源的保护。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 70

第3章　ARM可信固件

3.1　为什么使用ATF

  ARM可信任固件（ARM Trusted Firmware，
ATF）是由ARM官方提供的底层固件，该固件统一
了ARM底层接口标准，如电源状态控制接口
（Power Status Control Interface，PSCI）、安全启
动需求（Trusted Board Boot Requirements，
TBBR）、安全世界状态（SWS）与正常世界状态
（NWS）切换的安全监控模式调用（secure monitor
call，smc）操作等。ATF旨在将ARM底层的操作统
一使代码能够重用和便于移植。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 71

3.2 ATF的主要功能

    ATF的源代码共分为bl1、bl2、bl31、bl32、
bl33部分，其中bl1、bl2、bl31部分属于固定的固
件，bl32和bl33分别用于加载TEE OS和REE侧的镜
像。整个加载过程可配置成安全启动的方式，每一
个镜像文件在被加载之前都会验证镜像文件的电子
签名是否合法。

    ATF主要完成的功能如下：
    ·初始化安全世界状态运行环境、异常向量、
控制寄存器、中断控制器、配置平台的中断。

    ·初始化ARM通用中断控制器（General
Interrupt Controller，GIC）2.0版本和3.0版本的驱动
初始化。

    ·执行ARM系统IP的标准初始化操作以及安全
扩展组件的基本配置。

    ·安全监控模式调用（Secure Monitor Call，
smc）请求的逻辑处理代码（Monitor模式/EL3）。

    ·实现可信板级引导功能，对引导过程中加载


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 72

的镜像文件进行电子签名检查。

  ·支持自有固件的引导，开发者可根据具体需
求将自有固件添加到ATF的引导流程中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 73

3.3 ATF与TEE的关系

   为规范和简化TrustZone OS的集成，在ARMv8
架构中，ARM引入ATF作为底层固件并开放了源
码，用于完成系统中BootLoader、Linux内核、TEE
OS的加载和启动以及正常世界状态和安全世界状态
的切换。ATF将整个启动过程划分成不同的启动阶
段，由BLx来表示。例如，TEE OS的加载是由ATF
中的bl32来完成的，安全世界状态和正常世界状态
之间的切换是由bl31来完成的。在加载完TEE OS之
后，TEE OS需要返回一个处理函数的接口结构体
变量给bl31。当在REE侧触发安全监控模式调用指
令时，bl31通过查询该结构体变量就可知需要将安
全监控模式调用指令请求发送给TEE中的那个接口
并完成正常世界状态到安全世界状态的切换。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 74

3.4　小结

  在ARMv8架构中，如果系统需要支持TEE，则
几乎都必须使用由ARM提供的ATF作为底层固件。
关于ATF如何管理BootLoader、TEE OS、Linux内
核以及各个阶段镜像的加载过程和跳转过程，本书
第6章将结合实际代码详细分析。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 75

第4章　OP-TEE运行环境的搭建及编
译

  OP-TEE是开源的TEE解决方案，任何人都可
从github库中获取OP-TEE的源代码，本章主要包括
如何从github中获取OP-TEE的源代码、如何搭建运
行环境以及整个OP-TEE工程的编译过程。本书以
QEMU作为运行平台，Hikey或者其他平台的编译
和使用方式与QEMU平台类似。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 76

4.1　获取OP-TEE代码并搭建运行环境

   OP-TEE的开发环境推荐使用Linux进行搭建，
可在Windows系统中使用虚拟机创建一个Ubuntu系
统或者将计算机系统换成Ubuntu系统。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 77

4.1.1 OP-TEE开发环境的搭建

      OP-TEE的开发环境依赖于各种基本库，在
Ubuntu系统中直接运行如下指令就可安装OP-TEE
开发环境需要使用的各种依赖库。



$ sudo apt-get install android-tools-adb android-tools-fastboot autoconf \
    automake bc bison build-essential cscope curl device-tree-compiler \
    expect flex ftp-upload gdisk iasl libattr1-dev libc6:i386 libcap-dev \
    libfdt-dev libftdi-dev libglib2.0-dev libhidapi-dev libncurses5-dev \
    libpixman-1-dev libssl-dev libstdc++6:i386 libtool libz1:i386 make \
    mtools netcat python-crypto python-serial python-wand unzip uuid-dev \
    xdg-utils xterm xz-utils zlib1g-dev










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 78

4.1.2　获取OP-TEE的源代码

  在系统中创建用于存放OP-TEE的目录“open-
tee”，读者可以根据自己的喜好替换目录的名字，
创建完目录后就需要建立OP-TEE的repo（关于repo
或者git的使用，请读者自行查找资料了解），初始
化完repo后，使用repo sync指令就可从Github上获
取到OP-TEE的源代码，操作如下：

$ mkdir open-tee        //创建目录
$ cd open-tee           //切换到创建的目录
$ repo init -u https:   //github.com/OP-TEE/manifest.git -m default.xml --repo-url=git://codeaurora.org/tools/repo.git -b 2.6.0 //初始化repo
$repo sync              //开始获取OP-TEE源代码

    如果在执行repo sync时出现“remote：
Repository not found”的报错提示，则需要修改open-
tee/.repo目录下的manifest.xml文件，将该文件中所
有project域中的“.git”删除，也可通过如下指令进行
修改：

$sed -i "s/\.git//g"   .repo/manifest.xml

    修改完成之后，重新执行repo sync来获取OP-
TEE的代码。manifest.xml文件中包含的就是整个工
程所需的单独git仓库的链接[1]           。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 79

                         待代码同步完成后，为方便后续章节中各示例
代码的集成，需要使用如下指令将相关的代码回滚
到标签为3.0.0的版本。

$cd optee_client
$git checkout 3.0.0
$cd optee_test
$git checkout 3.0.0
$cd optee_benchmark
$git checkout 3.0.0
$cd optee_examples
$git checkout 3.0.0
$cd optee_os
$git checkout 3.0.0

[1] OP-TEE工程源代码链接：         https://github.com/OP-
TEE；OP-TEE内核代码链接：
https://github.com/OP-TEE/optee_os； OP-TEE client
端代码链接：    https://github.com/OP-
TEE/optee_client；  OP-TEE               test代码链接：
https://github.com/OP-TEE/optee_test；OP-TEE工程
使用的Linux                              Kernel代码链接：
https://github.com/linaroswg/linux；OP-TEE     中使用
的QEMU                                    软件源代码链接：
https://github.com/linaro-swg/qemu。







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 80

4.1.3　获取编译OP-TEE的toolchain

   OP-TEE工程的源代码下载完成后，下一步就
需要获取编译OP-TEE时使用的toolchain，切换到源
代码的build目录，执行如下指令：

  $ cd build //切换到build目录
  $ make -f toolchain.mk toolchains //下载toolchain

   查看toolchain.mk文件可知，执行make指令之
后，系统会去下载toolchains的tar包，包括32位和64
位的编译链接工具，下载完成后会进行解压操作。
执行完make后，可发现OP-TEE源代码的根目录下
会多出一个toolchains的目录，该目录中存放的就是
编译OP-TEE工程时使用的所有编译链接工具。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 81

4.1.4　编译QEMU

   OP-TEE源代码的build目录是用于编译整个工
程的编译目录，该目录包含各种平台的编译配置文
件。在QEMU平台运行时需选择qemu.mk文件进行
编译，具体操作如下：

  $ cd build //切换到build目录
  $ make -f qemu.mk all //编译工程

   当然，读者也可将qemu.mk文件链接成
Makefile，然后在build目录下直接执行make all就能
编译QEMU平台的工程。
   编译完成后将会在OP-TEE的根目录下生成一
个out目录，该目录中存放的就是使用QEMU方式运
行OP-TEE时需要的镜像和其他相关文件。

   如果在编译的过程中出现“ImportError：No
Module named wand.image”的报错提示，说明系统
没有安装Python的Wand包，此时在shell中运行如下
指令即可：

  $ pip install: Wand


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 82

4.1.5　运行OP-TEE

工程编译完成之后，如果要运行OP-TEE，则
需要进入build目录中执行make run-only语句，具体
操作如下：

$cd build                     //切换到build目录
$make -f qemu.mk run-only     //启动QEMU并运行OP-TEE

如果读者已将qemu.mk文件链接成了
Makefile，则直接在build目录中执行make run-only
即可。qemu.mk文件中的run-only目标首先会启动两
个分别属于安全世界状态和正常世界状态的
terminal，用于显示OP-TEE和Linux内核的日志数
据，然后加载OP-TEE镜像与Linux的镜像及其文件
系统。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 83

4.1.6　运行xtest和optee_example_hello_world

   通过使用make run-only启动OP-TEE后，可在
启动的正常世界状态对应的terminal中执行
Optee_example_hello_world或者xtest指令来检查OP-
TEE是否正常运行。

   Optee_example_hello_world是一个简单的CA编
译而成的二进制可执行文件，执行该可执行文件后
会调用OP-TEE中对应的TA，并执行一些简单的打
印操作，输出的日志信息可在安全世界状态的
terminal中查看。
   xtest是OP-TEE自带的一个测试使用的CA可执
行文件。该CA执行后将会调用TA中的各种功能，
包括检查基本算法接口、安全存储接口等。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 84

4.2　运行CA和TA示例

  OP-TEE中自带的TA和CA都保存在
optee_examples目录中，那么如何添加自己开发的
TA和CA程序到OP-TEE中并运行呢？本节将对此进
行介绍。为减少对编译方面的理解，本节将结合实
际的TA和CA示例介绍详细的操作步骤。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 85

4.2.1　示例代码的获取和集成

  本节所用示例的所有源代码可从gitHub上获
取，读者可使用如下指令获取到源代码，示例包中
有对应的补丁，读者直接合入补丁就可将该示例集
成到OP-TEE中，该示例的gitHub链接如下：

git clone https://github.com/shuaifengyun/optee_my_test.git

  获取到示例代码之后，切换到如下build目录
下，然后使用git apply命令合入补丁文件后就可将
该示例集成到OP-TEE，合入补丁的操作步骤如
下：

  1）将示例代码中的
optee_mytest_common_3.0.0.patch文件和
optee_mytest_qemu_3.0.0.patch文件复制到build目录
中。

  2）切换到build目录，使用如下命令合入补
丁：

git apply optee_mytest_common_3.0.0.patch
git apply optee_mytest_qemu_3.0.0.patch


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 86

   将补丁合入之后就可使用make-f qemu.mk all编
译整个工程，然后使用make-f qemu.mk run-only来
启动OP-TEE，在启动的正常世界状态的终端执行
my_test命令就能实现该示例的CA对TA的调用。示
例代码的运行效果如图4-1所示。










    图4-1 optee_my_test示例运行









    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 87

4.2.2　目录和文件创建

      从gitHub上获取到本章使用的示例代码后，
host存放的是CA的代码，ta目录存放的是TA部分的
代码。本章提供的示例代码的目录结构如下：


├── Android.mk
├── build_ta_mytest_qemu.sh
├── doc
│ ├── close_session_and_finalize_context.msc
│ ├── invoke_command.msc
│ ├── Makefile
│ └── open_session.msc
├── host
│ ├── main.c
│ ├── Makefile
│ └── my_test_ca.h
├── Makefile
├── optee_mytest_common_3.0.0.patch
├── optee_mytest_qemu_3.0.0.patch
├── README.md
└── ta
    ├── Android.mk
    ├── include
    │ ├── my_test_handle.h
    │ └── my_test_ta.h
    ├── Makefile
    ├── my_test.c
    ├── my_test_handle.c
    ├── sub.mk
    └── user_ta_header_defines.h


    目录中文件的作用说明如下：





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 88

  ·Android.mk文件：Android系统中编译整个TA
和CA时使用；
  ·build_ta_mytest_qemu.sh文件：单独编译TA和
CA使用的脚本文件；

  ·host/main.c文件：CA的源代码；
  ·host/Makefile文件：编译CA时使用的makefile
文件；

  ·host/my_test_ca.h文件：UUID、command ID
的宏定义；

  ·ta/Makefile文件：编译TA时使用的makefile文
件；

  ·ta/my_test.c文件：主要是存放TA部分代码的
入口处理函数，CA的command请求最终会被
TA_InvokeCommandEntryPoint函数处理；
  ·ta/my_test_handle.c文件：存放相应CA的
command请求的功能函数；

  ·ta/sub.mk文件：定义该TA中需要被编译的
source code；


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 89

   ·ta/user_ta_header_defines.h文件：定义UUID等
相关宏；

   ·ta/include/my_test_handle.h文件：定义了该TA
需要使用的类型；

   ·ta/include/my_test_ta.h文件：定义了UUID的宏
以及与CA对应的command ID宏；
   ·optee_mytest_common_3.0.0.patch文件：将该
TA和CA集成到OP-TEE时build/common.mk文件使
用的补丁文件；

   ·optee_mytest_qemu_3.0.0.patch文件：将该TA
和CA集成到OP-TEE时builld/qemu.mk文件使用的补
丁文件。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 90

4.2.3 CA端代码的修改

  若读者需添加新的功能，可按照GP规范调用
REE侧的相关接口，编辑完CA端的代码后就需要修
改host目录下的Makefile文件，将需要编译进CA的
文件添加到Makefile中，主要是修改host/Makefile文
件中的OBJS变量和BINARY变量，其中OBJS变量
存放的是需要编译到CA的目标文件或者库文件，
BINARY是编译完成后的可执行文件的名字。注
意，在CA的头文件中需要定义UUID和command ID
的宏，且定义的内容需要与TA中的UUID和
command ID一致，否则执行CA后将会导致调用失
败，关于UUID的值并没有特殊的要求，只需按照
其格式定义一个唯一的字符串即可。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 91

4.2.4 TA端代码的修改

  ta目录中存放的是该TA的源代码、makefile文
件和头文件，其中ta目录中必须存在一个
user_ta_header.h文件，该文件在编译TA镜像或者是
整个工程时会被使用到。在该文件中会定义UUID
的宏、该TA运行的堆栈空间的大小以及版本信
息。在TA的头文件中需要定义UUID的宏和
command ID，且必须与CA中定义的一样，否则CA
端将无法调用该TA中对应的操作。修改ta/Makefile
文件，将该文件中BINARY变量的值修改成与CA中
相同的UUID值。

  修改完成后运行build_ta_mytest_qemu.sh脚本
就能单独编译CA和TA，如果出现错误，则根据提
示进行修改，编译成功后会在ta目录中生成与UUID
值一样的elf文件，在host目录中将会生成与
host/Makefile文件中BINARY变量的值一样的文
件。







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 92

4.2.5 TA和CA在OP-TEE的集成

    单独编译TA和CA成功后，就需要将该TA和
CA集成到OP-TEE的工程中去，需要修改OP-TEE源
代码中build目录下的qemu.mk文件和common.mk文
件。

    在build/qemu.mk文件中增加该TA的目标和依
赖关系，以本示例为例，对build/qemu.mk文件的修
改如下。

    1）增加optee_my_test的编译目标内容：

############################################################################
# optee_my_test
############################################################################
Optee_mytest: optee_mytest-common
Optee_mytest-clean: optee_mytest-clean-common

    2）将optee_mytest目标和optee_mytest-clean-
common目标添加到all中：

all: bios-qemu qemu soc-term optee-examples optee_my_test
clean: bios-qemu-clean busybox-clean linux-clean optee-os-clean \
      optee-client-clean qemu-clean soc-term-clean check-clean \
      optee_my_test-clean \
      optee-examples-clean


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 93

      在build/common.mk文件中需要增加编译该TA
和CA的路径变量等信息，添加的内容如下。
      1）增加TA和CA的代码路径：


    OPTEE_MYTEST_PATH    ?= $(ROOT)/optee_my_test



    2）增加TA和CA的common目标：


    ############################################################################
    # optee_my_test
    ############################################################################
    OPTEE_MYTEST_COMMON_FLAGS ?= HOST_CROSS_COMPILE=$(CROSS_COMPILE_NS_USER)\
    TA_CROSS_COMPILE=$(CROSS_COMPILE_S_USER) \
    TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR) \
    TEEC_EXPORT=$(OPTEE_CLIENT_EXPORT)
    .PHONY: optee_my_test-common
    optee_my_test-common: optee-os optee-client
    $(MAKE) -C $(OPTEE_MYTEST_PATH) $(OPTEE_MYTEST_COMMON_FLAGS)
    OPTEE_MYTEST_CLEAN_COMMON_FLAGS ?= TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR)
    .PHONY: optee_my_test-clean-common
    optee_my_test-clean-common:
    $(MAKE) -C $(OPTEE_MYTEST_PATH) $(OPTEE_MYTEST_CLEAN_COMMON_FLAGS) clean



    3）将该TA和CA添加到filelist-tee-common目标
    的依赖关系中：



    filelist-tee-common: optee-client xtest optee-examples optee_my_test



    4）添加clean操作的依赖关系：




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 94

optee-os-clean-common: xtest-clean optee-examples-clean optee_my_test-clean



5）在filelist-tee-common中添加TA和CA镜像需
要被打包到文件系统中的操作：



@echo "#optee_mytest " >> $(fl)
@if [ -e $(OPTEE_MYTEST_PATH)/host/my_test ]; then \
  echo "file /bin/my_test" \
  "$(OPTEE_MYTEST_PATH)/host/my_test 755 0 0"     >> $(fl); \
  echo "file /lib/optee_armtz/9269fadd-99d5-4afb-a1dc-ee3e9c61b04c.ta" \
  "$(OPTEE_MYTEST_PATH)/ta/9269fadd-99d5-4afb-a1dc-ee3e9c61b04c.ta 444 0 0" \
  >> $(fl); \
fi










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 95

    4.3 OP-TEE源代码结构

        OP-TEE的源代码包含运行OP-TEE时需要的所
    有软件源代码，OP-TEE工程编译完成后，整个源
    代码的目录结构如下：


    ├── basicAlg_use
    ├── bios_qemu_tz_arm
    ├── build
    ├── busybox
    ├── gen_rootfs
    ├── linux
    ├── optee_benchmark
    ├── optee_client
    ├── optee_examples
    ├── optee_my_test
    ├── optee_os
    ├── optee_test
    ├── out
    ├── qemu
    ├── secStor_test
    ├── soc_term
    └── toolchains


      OP-TEE各子目录中的代码功能说明如下。

      （1）bios_qemu_tz_arm目录
      在QEMU平台中运行tz_arm的BIOS代码，启动
的最初阶段会被使用到，用来加载Linux内核镜
像、OP-TEE OS镜像、rootfs并启动Linux内核和



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 96

OP-TEE OS。
  （2）build目录

  OP-TEE工程的编译目录，包含各种mk文件和
相关配置文件，其中common.mk文件是工程的通用
mk文件，不同的CPU架构有不同的mk与之相对
应，编译工程时可使用make-f的方式指定编译哪个
板级的OP-TEE。
  （3）busybox目录
  busybox的源代码，编译生成制作rootfs所需要
的文件和目录。

  （4）gen_rootfs目录
  存放制作rootfs时使用的相关脚本和配置文
件。

  （5）linux目录

  Linux内核代码，在driver/tee目录下存放的是
OP-TEE在REE侧的驱动，任何在Linux用户空间调
用CA的接口都会经过OP-TEE的REE侧驱动处理之
后再转发到TEE侧。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 97

  （6）optee_benchmark目录
  OP-TEE运行的性能测试工具，只保存CA端的
代码，TA部分的代码保存在OP-TEE OS中，作为
静态TA集成到OP-TEE OS中。

  （7）optee_client目录
  包含CA程序调用的用户空间的接口库
（libteec）的源代码。其中tee_supplicant目录中的
代码会被编译成一个可执行文件，该可执行文件在
Linux启动时作为守护进程常驻在系统中，该守护
进程的主要作用是响应和处理来自TEE侧的RPC请
求，这些RPC请求包括：加载TA镜像、对文件系统
的操作、对SQL的操作、对EMMC RPMB的操作、
网络通信的socket操作等。
  （8）optee_examples目录

  示例代码，目录下包含OP-TEE提供的各种示
例的TA和CA的所有代码，启动后，在REE对应的
terminal中执行optee_example_hello_world命令后，
会调用optee_example_hello_world的TA的逻辑，TA
根据接收到的command ID在OP-TEE中执行对应的
操作。

  （9）optee_os目录

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 98

存放OP-TEE OS的源代码和相关文档，编译完
成之后，该目录将会生成OP-TEE的镜像文件。

（10）optee_test目录

opentee的测试程序xtest的源代码，主要用来测
试OP-TEE中提供的各种算法的逻辑并提供其他测
试功能。

（11）out目录
编译结果的输出目录（该目录编译完成之后才
会生成）。

（12）qemu目录
QEMU源代码，如果编译的是qemu.mk，编译
时将会使用到该目录。

（13）soc_term目录

在使用QEMU运行OP-TEE时，gnome-terminal
命令会启动终端，用于建立启动的两个terminal的
端口监听，方便OP-TEE OS的log和Linux的log分别
输出到对应的terminal中。
（14）toolchains目录

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 99

   编译时需要使用的编译工具链，在build目录下
执行make–f toolchai.mk toolchains后将会生成该目
录。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 100

4.4 OP-TEE编译

   整个OP-TEE工程的编译是一个庞大的过程，
牵扯到目标的依赖关系，本节以qemu.mk板级为
例，分析使用QEMU方式运行OP-TEE时的全部编
译过程和目标依赖关系。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 101

4.4.1　编译目标的依赖关系

  编译OP-TEE工程时各主要目标的依赖关系如
下：


all
   ├── bios-qemu
   │    ├── optee-os
   │    │ └── optee-os-common
   │    └── update_rootfs
   │      └── update_rootfs-common
   │           ├── busybox
   │           │    └── busybox-common
   │           │      └── linux
   │           │           └── linux-common
   │           │               └── linux-defconfig
   │           └── filelist-tee
   │               └── filelist-tee-common
   │                  ├── f1
   │                  │    └── filelist-tee.txt
   │                  ├── optee-client
   │                  │    ├── common
   │                  │    └── optee-client
   │                  └── xtest
   │                  │    ├── optee-client
   │                  │    └── xtest-common
   │                  │        └── optee-os
   │                  │           └──optee-os-common
   │                  └── optee-examples
   │                       └── build_socterm
   │                           └── helloworld-common
   │                                 ├──optee-client
   │                                 └──optee-os
   ├── benchmark-app
   ├── qemu
   │    └── build_qemu
   └── soc-term
   │    └── build_socterm



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 102

  └── optee-examples
  │    └── build_socterm
  │    └── helloworld-common
  │     ├──optee-client
  │     └──optee-os

  QEMU目标会切换到QEMU目录，并获取
QEMU的配置文件，然后执行make命令来编译
QEMU目标。

  soc-term目标会编译soc-term目录，生成一个
soc-term的可执行文件，用于启动两个terminal。
  bios-qemu目标依赖于update_rootfs和optee-os，
update_rootfs和optee-os编译完成之后会调用
biosqemu-comm宏定义的指令，该宏会编译
bios_qemu_tz_arm目录，该目录编译完成之后，会
生成启动时需要的bios镜像。
optee-os-common目标将编译optee_os目录，该
目录编译完成后将会生成tee.bin及其他的lib库文
件。

  busybox目标将编译linux目录和busybox目录，
生成Linux内核镜像文件和制作rootfs需要的相关文
件。

  filelist-tee目标将生成tee功能相关的文件和需要


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 103

被挂载到rootfs中的映射图，然后与系统的其他文
件的挂载映射关系一起保存到filelist-final.txt文件
中，用于生成filesystem.cpio.gz文件。

   update_rootfs-common目标依赖于busybox和
filelist-tee目标，上述两个目标编译完成之后，将会
切换到gen_rootfs目录中，调用gen_init_cpio命令生
成在启动时需要使用的filesystem.cpio.gz文件。

   Optee_examples目标包含OP-TEE提供的各种
TA部分和CA部分，编译完成之后，会生成对应的
TA镜像文件和CA的可执行文件。
   optee-client目标将对optee_client目录进行编
译，生成一系列的库文件和可执行文件，库文件提
供了OP-TEE在Linux端的接口，将被所有CA调用。
tee-supplicant目标将会编译生成一个tee_supplicant
的可执行文件，该可执行文件提供了optee_os访问
文件系统的RPC接口以及加载具体的TA镜像的功
能。

   xtest目标将会编译optee_test目录，生成在xtest
集合中会使用的TA镜像文件和xtest可执行文件。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 104

4.4.2 bios.bin镜像的生成过程

                                        bios.bin镜像是启动时会被使用到的主要镜像文
件，在执行make run-only指令使用QEMU方式启动
OP-TEE时，会借助qemu-system-arm命令来启动OP-
TEE和Linux kern，并挂载Linux的rootfs。在运行
qemu-system-arm命令时，其中有一个参数为“    -
bios” ，该参数就是告诉QEMU使用该参数之后所带
的bios.bin来启动整个系统。

                               bios.bin中会包含Linux kernel的镜像、OP-TEE
OS的镜像以及rootfs。该镜像文件是在bios-qemu的
目标中编译出来的。

    当bios-qemu目标的依赖目标都编译完成后，会
使用bios-qemu-common函数将Linux内核、OP-TEE
镜像、rootfs打包成bios.bin镜像文件。bios-qemu-
common函数定义在build/qemu.mk文件中，内容如
下：

define bios-qemu-common
    +$(MAKE) -C $(BIOS_QEMU_PATH) \
      CROSS_COMPILE=$(CROSS_COMPILE_NS_USER) \
      O=$(ROOT)/out/bios-qemu \
      BIOS_NSEC_BLOB=$(LINUX_PATH)/arch/arm/boot/zImage \
      BIOS_NSEC_ROOTFS=$(GEN_ROOTFS_PATH)/filesystem.cpio.gz \
      BIOS_SECURE_BLOB=$(OPTEE_OS_BIN) \
      PLATFORM_FLAVOR=virt

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 105

Endef

执行该函数时会带入相关的编译参数，编译由
变量BIOS_QEMU_PATH定义的目录
（bios_qemu_tz_arm目录），参数说明如下：

·CROSS_COMPILE：编译时使用的编译参
数，包括编译器、cflag等；

·O：编译结果的输出目录；
·BIO_NSEC_BLOB：定义该变量，指定Linux
内核镜像的名称和路径；

·BIOS_NSEC_ROOTFS：定义该变量，指定生
成的rootfs存在的目录和cpio格式文件名；
·BIOS_SECURE_BLOB：定义该变量，指定
OP-TEE OS镜像文件名；
·PLATFORM_FLAVOR：定义该变量，设定平
台变量。

编译bios_qemu_tz_arm目录时最终会将Linux内
核镜像、OP-TEE OS镜像、rootfs转换成.o文件，然
后再将这些转换后的.o文件与其他的.o文件一起链
接成biso.bin镜像文件。Linux内核镜像文件会被放

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 106

在bios.bin中名称为nsec_blob的section里。OP-TEE
os image将会被放在bios.bin中名称为secure_blob的
section里。rootfs image将会被放在bios.bin中名称为
nsec_rootfs的section里。
   上述将镜像文件转换成.o文件的操作是通过
OBJCOPY带--rename-section参数来实现的，具体的
内容可以在link.mk文件中找到。

   bios_qemu_tz_arm/bios/entry.s文件存放的就是
在启动系统时bios.bin的入口文件。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 107

4.4.3 run-only目标的执行

                       qemu.mk文件中的run-only目标是用来启动使用
QEMU方式运行OP-TEE的起始目标，在qemu.mk文
件中，run-only目标的定义如下：

.PHONY: run-only
run-only:
      $(call check-terminal)
      $(call run-help)
      $(call launch-terminal, 54320,"Normal World")
      $(call launch-terminal, 54321,"Secure World")
      $(call wait-for-ports, 54320,54321)
      $(QEMU_PATH)/arm-softmmu/qemu-system-arm \
      -nographic \
      -serial tcp:localhost:54320 -serial tcp:localhost:54321 \
      -s -S -machine virt -machine secure=on -cpu ARM核-a15 \
      -m 1057 \
      -bios $(ROOT)/out/bios-qemu/bios.bin \
      $(QEMU_EXTRA_ARGS)

      run-only目标的内容会调用各种函数，这些函
数会在相关的makefile文件中定义，下面是相关函
数的作用说明：

      $(call check-terminal)：

      check-terminal在QEMU的工程中不会被定义，
该语句不会被执行，但是在其他工程中会定义，具
体可查看build/common.mk文件。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 108

   $(call run-help)：
   run-help函数定义在build/commom.mk文件中，
主要用来打印出相关的启动帮助信息。

   $(call launch-terminal，54320，"Normal
World")：
   执行launch-terminal，54320，"Normal
World"指令，启动名字为Normal World的terminal，
其中launch-terminal在build/common.mk文件中定
义。

   $(call launch-terminal，54321，"Secure
World")：

   执行功能同上，只是在重定向时将端口换成了
54321，且启动的terminal名字为Secure World。
   $(call wait-for-ports，54320，54321)：
   调用wait-for-prots函数，该函数定义在
build/common.mk文件中，主要功能是检查上面启
动的两个terminal使用socket方式进行通信是否正
常。

   $(QEMU_PATH)/arm-softmmu/qemu-system-

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 109

arm：
   该指令就是调用qemu-system-arm指令，并设定
好QEMU启动的各种参数，然后开始启动Linux与
OP-TEE，该指令完全展开之后的内容如下：

  /home/icyshuai/devel/optee/build/../qemu/arm-softmmu/qemu-system-arm \
    -nographic \
    -serial tcp:localhost:54320 -serial tcp:localhost:54321 \
    -s -S -machine virt -machine secure=on -cpu ARM核-a15 \
    -m 1057 \
    -bios /home/icyshuai/devel/optee/build/../out/bios-qemu/bios.bin

   -nographic：不显示图形界面。
   -serial：将串口重定向到后面的参数部分。

   -S：使用C来控制启动（在QEMU的console界
面输入C之后才会正式启动系统）。
   -m：设定虚拟的内存大小。
   -bios：指定BIOS的文件（该image中会包含
OP-TEE、Linux、rootfs的镜像文件）。

1.launch-terminal函数
   launch-terminal函数的主要功能是用来启动


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 110

terminal。该函数定义在build/common.mk文件中，
具体内容如下：

define launch-terminal
@nc -z 127.0.0.1 $(1) || \
$(gnome-terminal) -t "$(2)" -x $(SOC_TERM_PATH)/soc_term $(1) &
endef

$(gnome-terminal)的定义也在common.mk文件
中，定义如下：

gnome-terminal := $(shell command -v gnome-terminal 2>/dev/null)

调用$(call launch-terminal，54320，    "Normal
World")等价于：

gnome-terminal -t "Normal World" -x $(SOC_TERM_PATH)/soc_term 54320

调用该函数的作用是启动一个名字为Normal
World的terminal，并且在terminal中执行soc_term
54320，soc_term就是在soc_term目录中编译出来的
可执行文件。执行soc_term 54320命令的主要作用
是将该terminal的输入和输出通过54320端口重定向
到标准输入和输出端口。

2.soc_term可执行文件

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 111

      soc_term可执行文件用来实现Linux和OP-TEE
的两个terminal输入和输出重定向到标准输入输出
端口，
        该可执行文件的源代码存放在soc_term目录
中。soc_term.c文件中的main函数定义如下：


    int main(int argc, char *argv[])
    {
     int listen_fd;
     char *port;
     bool have_handle_telnet_option = false;
     switch (argc) {
      case 2:
      port = argv[1];
      break;
      case 3:
      if (strcmp(argv[1], "-t") != 0)
          usage();
      have_handle_telnet_option = true;
      port = argv[2];
      break;
      default:
      usage();
     }
     save_current_termios();//获取当前terminal的信息（标准输入输出的terminal配置）
     listen_fd = get_listen_fd(port);//建立socket机制,并监听输入的端口号
     printf("listening on port %s\n", port);
     if (have_handle_telnet_option)   //判定是否使用telent
      printf("Handling telnet commands\n");
     /* 进入loop循环,完成端口监听和输入输出的重定向 */
     while (true) {
      int fd = accept_fd(listen_fd);      //开始接收建立的监听端口的信息
      handle_telnet = have_handle_telnet_option;
      handle_telnet_codes(-1,NULL, NULL); //为使用telent时不起作用
      warnx("accepted fd %d", fd);
      /*复制当前terminal的信息,并配置其他参数,然后调用tcsetattr函数来设定当前启动的terminal的信息*/
      set_tty_noncanonical();
      /*开始处理监听收到的数据,并根据对应的revent进行重定向操作,server_fd函数的注释见后续章节*/
      serve_fd(fd);
      /* 处理完成之后关闭该fd */
      if (close(fd))




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 112

 err(1, "close");
 fd = -1;
 /* 保存当前terminos的配置 */
 restore_termios();
}
}



server_fd函数用来接收受监控的端口的数据，
并执行重定向操作，代码内容和解释如下：



static void serve_fd(int fd)
{
 uint8_t buf[512];
 struct pollfd pfds[2];
 /* 设定pollfd参数,用于实现重定向操作 */
 memset(pfds, 0, sizeof(pfds));
 pfds[0].fd = STDIN_FILENO;
 pfds[0].events = POLLIN;
 pfds[1].fd = fd;
 pfds[1].events = POLLIN;
 while (true) {
 size_t n;
 /* 获取监听事件的pfds[0]和pfds[1]中定义的事件 */
 if (poll(pfds, 2, -1) == -1)
  err(1, "poll");
 /* 如果pfds[0]中的POLLIN时间触发（在该terminal的标准输入中有输入操作）,则进行读取操作 */
 if (pfds[0].revents & POLLIN) {
  //从该terminal的标准输入端口中读取输入的数据
  n = read(STDIN_FILENO, buf, sizeof(buf));
  if (n == -1)
   err(1, "read stdin");
  if (n == 0)
   errx(1, "read stdin EOF");
  /* 将读取到的数据写入到重定向的port捆绑的socket */
  if (!write_buf(fd, buf, n)) {
   warn("write_buf fd");
   break;
  }
 }
 /* 如果pfds[1]中的POLLIN时间触发（监测到该terminal的port捆绑的socket有输入流操作）,则读取监测的port对应的socket句柄中的数据 */




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 113

if (pfds[1].revents & POLLIN) {
 //读取与port捆绑的socket的句柄中的数据
 n = read(fd, buf, sizeof(buf));
 if (n == -1) {
  warn("read fd");
  break;
 }
 if (n == 0) {
  warnx("read fd EOF");
  break;
 }
 handle_telnet_codes(fd, buf, &n);
 /* 将读取到的数据写入到该terminal的标准输出 */
 if (!write_buf(STDOUT_FILENO, buf, n))
  err(1, "write_buf stdout");
}
}
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 114

4.5　小结

  本章主要介绍OP-TEE开发和运行环境的搭
建，并提供了一个demo，介绍如何开发自己的TA
和CA并让其成功运行在OP-TEE中。为方便读者理
解整个OP-TEE工程的实际执行流程，知道如何生
成启动OP-TEE时使用的各种镜像文件，本章特意
介绍了OP-TEE工程的编译过程以及编译过程中各
种目标的依赖关系，同时对编译过程中的重要函数
做了进一步的介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 115

第二篇　系统集成篇

第5章　QEMU运行OP-TEE的启动过程
第6章　安全引导功能及ATF的启动过程

第7章　OP-TEE OS的启动过程
第8章　OP-TEE在REE侧的上层软件
第9章　REE侧OP-TEE的驱动










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 116

第5章　QEMU运行OP-TEE的启动过
程

  使用QEMU的方式运行OP-TEE是通过在build
目录下执行make run-only来启动的，启动过程主要
是加载bios.bin文件，并从该镜像文件中分离出
Linux内核镜像和OP-TEE镜像以及rootfs镜像，并将
rootfs作为根文件系统挂到Linux系统中。本章将介
绍系统的启动过程，并详细介绍OP-TEE的启动流
程和相关的重要启动节点。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 117

5.1 bios.bin的入口函数

        使用QEMU运行OP-TEE时首先加载的是编译
生成的bios.bin镜像文件，而bios.bin镜像文件的入
口函数是在bios_qemu_tz_arm/bios/entry.S文件中定
义的，
    该文件的入口函数为_start，
    该文件的主要内
容如下：



.section .text.boot
//定义 _start函数,设定第一条指令跳转到reset函数执行
FUNC _start , :
     b   reset
     b   .   /* Undef */
     b   .   /* Syscall */
     b   .   /* Prefetch abort */
     b   .   /* Data abort */
     b   .   /* Reserved */
     b   .   /* IRQ */
     b   .   /* FIQ */
END_FUNC _start
/* reset 函数 */
LOCAL_FUNC reset , :
     read_sctlr r0
     orr r0, r0, #SCTLR_A
     write_sctlr r0
/* 设置中断向量表 */
     adr r0, _start
     write_vbar r0
     /* 重新设定bios在RAM中的地址 */
     mov r0, #0
     ldr r1, =__text_start
     ldr r2, =__data_end
     sub r2, r2, r1
//复制bios.bin文件中的__text_start到__data_end到地址为0的起始RAM中
bl   copy_blob
     /* 跳转到上面重新定位的bios在RAM中的地址 */




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 118

ldr ip, =new_loc
bx   ip
new_loc:
/* 重新设定中断向量 */
adr r0, _start
write_vbar r0
/* 清空BSS段的数据 */
ldr r0, =__bss_start
ldr r1, =__bss_end
sub r1, r1, r0
bl  zero_mem
/* 设定堆栈空间 */
ldr ip, =main_stack_top;
ldr sp, [ip]
push       {r0, r1, r2}
mov r0, sp
ldr ip, =main_init_sec    //获取main_init_sec函数地址
blx ip       //跳转到main_init_sec函数中执行,加载OP-TEE OS的image
pop {r0, r1, r2}
mov ip, r0      // OP-TEE OS的入口地址
mov r0, r1      /* argument (address of pagable part if != 0) */
blx ip       //跳转到OP-TEE OS的启动地址
/* 设置Normal World的栈 */
ldr ip, =main_stack_top;
ldr sp, [ip]
ldr ip, =main_init_ns     //获取main_init_ns函数的地址
bx   ip      //跳转到main_init_ns函数,加载Linux内核的image
END_FUNC reset
//复制函数
LOCAL_FUNC copy_blob , :
ldrb     r4, [r0], #1
strb     r4, [r1], #1
subs     r2, r2, #1
bne      copy_blob
bx       lr
END_FUNC copy_blob
//清空内存数据的函数
LOCAL_FUNC zero_mem , :
cmp      r1, #0
bxeq     lr
mov      r4, #0
strb     r4, [r0], #1
sub      r1, r1, #1
b        zero_mem
END_FUNC zero_mem




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 119

      main_init_sec函数用来将Linux内核镜像、OP-
TEE OS镜像、rootfs镜像文件加载到RAM的对应位
置，并且解析出OP-TEE OS的入口地址、Linux内
核的加载地址、rootfs在RAM中的地址和其他相关
信息。main_init_sec函数执行完成后会返回OP-TEE
OS的入口地址以及设备树（device tree，DT）的地
址，然后在汇编代码中通过调用blx指令进入OP-
TEE OS的启动。

OP-TEE启动完成后会重新进入entry.S文件中
继续执行，最终执行main_init_ns函数来启动Linux
内核，在main_init_sec函数中会设定Linux内核的入
口函数地址、DT的相关信息，main_init_ns函数会
使用这些信息来开始Linux内核的加载。
上述两个函数都定义在
bios_qemu_tz_arm/bios/main.c文件中。将各种镜像
文件复制到RAM的操作都是通过解析bios.bin镜像
的对应section来实现的，通过寻找特定的section来
确定各镜像文件在bios.bin文件中的位置。







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 120

5.2 OP-TEE镜像的加载和启动

     启动过程中entry.S文件通过汇编调用
main_init_sec函数将optee-os镜像、Linux镜像和
rootfs加载到RAM中，并定位DT的地址信息，以备
Linux和OP-TEE启动使用，这些操作是由
main_init_sec函数进行的，该函数定义在
bios_qemu_tz_arm/bios/main.c文件中，其内容如
下：


    void main_init_sec(struct sec_entry_arg *arg)
    {
     void *fdt;
     int r;
     //定义OP-TEE OS 镜像文件存放的起始地址
     const uint8_t *sblob_start = &__linker_secure_blob_start;
     //定义OP-TEE OS 镜像文件存放的末端地址
     const uint8_t *sblob_end = &__linker_secure_blob_end;
     struct optee_header hdr;  //存放OP-TEE OS image头的信息
     size_t pg_part_size;      //OP-TEE OS image除去初始化头部信息的大小
     uint32_t pg_part_dst;     //OP-TEE OS image除去初始化头部信息后在RAM中的起始地址
     msg_init();      //初始化uart
     /* 加载device tree 信息。在qemu工程中,并没有将device tree信息编译到Bios.bin中,而默认存放在DTB_START地址中 */
     fdt = open_fdt(DTB_START, &__linker_nsec_dtb_start,
         &__linker_nsec_dtb_end);
     r = fdt_pack(fdt);
     CHECK(r < 0);
     /* 判定OP-TEE OS image的大小是否大于image header的大小 */
     CHECK(((intptr_t)sblob_end - (intptr_t)sblob_start) <
     (ssize_t)sizeof(hdr));
     /* 将OP-TEE OS image header信息复制到hdr变量中 */
     copy_bios_image("secure header", (uint32_t)&hdr, sblob_start,
         sblob_start + sizeof(hdr));
     /* 校验OP-TEE OS image header中的magic和版本信息是否合法 */
     CHECK(hdr.magic != OPTEE_MAGIC || hdr.version != OPTEE_VERSION);



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 121

   msg("found secure header\n");
   sblob_start += sizeof(hdr); //将sblob_start的值后移到除去image header的位置
   CHECK(hdr.init_load_addr_hi != 0); //检查OP-TEE OS的初始化加载地址是否为零
   /* 获取OP-TEE OS除去 image header和ini操作部分代码后的大小 */
   pg_part_size = sblob_end - sblob_start - hdr.init_size;
   /* 确定存放OP-TEE OS除去image header和init操作部分代码后存放在RAM中的地址 */
   pg_part_dst = (size_t)TZ_RES_MEM_START + TZ_RES_MEM_SIZE - pg_part_size;
   /* 将存放OP-TEE OS除去image header和init操作部分后的内容复制到RAM中 */
   copy_bios_image("secure paged part",
        pg_part_dst, sblob_start + hdr.init_size, sblob_end);
   sblob_end -= pg_part_size; //重新计算sblo_end的地址,剔除page part
   //将pg_part_dst赋值给arg中的paged_part以备跳转执行OP-TEE OS使用
   arg->paged_part = pg_part_dst;
   //将hdr.init_load_addr_lo赋值给arg中的entry,该地址为op-TEE OS的入口地址
   arg->entry = hdr.init_load_addr_lo;
   /* 将OP-TEE OS的实际image复制到起始地址为hdr.init_load_addr_l的RAM地址中 */
   copy_bios_image("secure blob", hdr.init_load_addr_lo, sblob_start,
        sblob_end);
   //复制kernel image、rootfs到RAM,并复制device tree到对应地址,以备被kernel使用
   copy_ns_images();
   /* 将device tree的地址赋值给arg->fdt变量,以备OP-TEE OS启动使用 */
   arg->fdt = dtb_addr;
   msg("Initializing secure world\n");
}


     main_init_sec函数执行后将会返回一个
sec_entry_arg的变量，该变量包含启动OP-TEE OS
的入口地址、DT的地址以及paged_table的地址。
sec_entry_arg变量将会被entry.S文件用来启动OP-
TEE OS，entry.S会将OP-TEE OS的入口地址保存在
r0寄存器中，而paged_table部分的起始地址会被保
存在r1寄存器中，将r0赋值给ip，最终entry.S文件
通过执行blx ip指令进入OP-TEE OS的入口函数中去
执行OP-TEE OS的启动。当OP-TEE OS启动完成之
后，entry.S文件会调用main_init_ns函数来启动




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 122

Linux内核。待Linux内核启动完成之后，整个系统
也就启动完成。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 123

5.3 Linux内核镜像的加载和启动

   entry.S文件通过调用main_init_ns函数来完成对
Linux内核的启动，该函数会调用call_kernel函数来
完成Linux内核的启动，调用call_kernel函数时传入
的参数说明如下：

   kernel_entry：Linux内核在RAM中的入口地
址，该值在main_init_sec函数中通过调用
copy_ns_images函数来进行赋值。
   dtb_addr：DT存放的位置，该值在
main_init_sec函数中通过调用copy_ns_images函数来
进行赋值。

   rootfs_start：复制到RAM中的rootfs的起始地
址，该值在main_init_sec函数中被赋值。

   rootfs_end：复制到RAM中的rootfs的末端地
址，该值在main_init_sec函数中被赋值。

   call_kernel函数定义在
bios_qemu_tz_arm/bios/main.c文件中，该函数的内
容和相关注释如下：



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 124

    typedef void (*kernel_ep_func)(uint32_t a0, uint32_t a1, uint32_t a2);
    static void call_kernel(uint32_t entry, uint32_t dtb,
uint32_t initrd, uint32_t initrd_end)
    {
     /* 定义指向Linux内核入口地址的函数指针,并将函数指针的地址指向带入参数entry的位置 */
     kernel_ep_func ep = (kernel_ep_func)entry;
     void *fdt = (void *)dtb;  //定义device tree的地址并赋值
     const char cmdline[] = COMMAND_LINE;      //定义存放command line的变量并进行赋值
     int r;
     const uint32_t a0 = 0;
     /*MACH_VEXPRESS see linux/arch/arm/tools/mach-types*/
     const uint32_t a1 = 2272;
     /* 获取device tree的信息 */
     r = fdt_open_into(fdt, fdt, DTB_MAX_SIZE);
     CHECK(r < 0);
     /* 设置device tree中的相关节点、initrd的起始地址、initrd的末端地址、bootargs */
     setprop_cell(fdt, "/chosen", "linux,initrd-start", initrd);
     setprop_cell(fdt, "/chosen", "linux,initrd-end", initrd_end);
     setprop_string(fdt, "/chosen", "bootargs", cmdline);
     r = fdt_pack(fdt);
     CHECK(r < 0);
     /* 打印相关信息 */
     msg("kernel command line: \"%s\"\n", cmdline);
     msg("Entering kernel at 0x%x with r0=0x%x r1=0x%x r2=0x%x\n",
     (uintptr_t)ep, a0, a1, dtb);
     /* 带入device tree信息和其他相关参数,调用Linux内核的入口函数,进而执行Linux内核的启动 */
     ep(a0, a1, dtb);
    }



    ep的值是Linux内核的入口函数指针，
         所以最
    终调用ep(a0，a1，dtb)函数就能开始Linux内核的启
    动过程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 125

5.4 rootfs的挂载

   启动Linux系统时会加载rootfs，rootfs在启动
Linux系统之前会被拷贝到相应的内存地址中，系
统在启动Linux时会告知Linux内核rootfs在内存中的
地址，Linux内核启动时会到该地址中去获取rootfs
的内容，挂载起来作为Linux系统的根文件系统使
用。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 126

5.5 OP-TEE驱动的启动

              在OP-TEE工程中，OP-TEE在REE侧的驱动会
被编译到Linux内核镜像中，Linux系统在启动的过
程中会自动挂载OP-TEE的驱动，驱动挂载过程中
会创建/dev/tee0和/dev/teepriv0设备，其中/dev/tee0
设备将会被REE侧的用户空间的库（libteec）使
用，/dev/teepriv0设备将会被系统中的常驻进程
tee_supplicant使用，并且在OP-TEE驱动的挂载过程
中会建立正常世界状态与安全世界状态之间的共享
内存，用于OP-TEE驱动与OP-TEE之间的数据共
享，同时还会创建两个链表，分别用于保存来自
OP-TEE的RPC请求和发送RPC请求的处理结果给
OP-TEE。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 127

5.6 tee_supplicant的启动

    tee_supplicant是Linux系统中的常驻进程，该进
程用于接收和处理来自OP-TEE的RPC请求，并将
处理结果返回给OP-TEE。来自OP-TEE的RPC请求
主要包括socket操作、REE侧文件系统操作、加载
TA镜像文件、数据库操作、共享内存分配和注册
操作等。该进程在Linux系统启动过程中被自动创
建，在编译时，该进程的启动信息会被写入
到/etc/init.d文件中，而该进程的可执行文件则被保
存在文件系统的bin目录下。该进程中会使用一个
loop循环接收来自OP-TEE的远程过程调用
（Remote Procedure Call，RPC）请求，且每次获取
到来自OP-TEE的RPC请求后都会自动创建一个线
程，用于接收OP-TEE驱动队列中来自OP-TEE的
RPC请求，之所以这么做是因为时刻需要保证在
REE侧有一个线程来接收OP-TEE的请求，实现RPC
请求的并发处理。








https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 128

5.7　小结

  本章介绍了使用QEMU的方式运行OP-TEE的
启动过程，介绍了系统是如何启动的，在启动过程
中如何加载相应的镜像文件。即使在非QEMU方式
运行OP-TEE时，OP-TEE的驱动和tee_supplicant同
样会被挂载和启动，这属于运行OP-TEE不可或缺
的一部分。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 129

第6章　安全引导功能及ATF的启动过
程

  安全引导（Secure Boot）功能是指在系统的整
个启动过程中，使用链式验证电子签名的方式来验
证系统中重要镜像文件的可靠性，然后再加载镜像
文件的引导过程。安全引导功能可以保护二级厂商
系统的独立性和完整性。在ARMv8架构中ARM提
供了ARM可信固件（ATF）。Bootloader、Linux内
核、TEE OS的启动都由ATF来加载和引导。对于
ARMv8，Bootloader、Linux内核和TEE OS镜像文
件的验签工作都是在ATF中完成的。本章将介绍安
全引导功能的原理以及ATF的启动过程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 130

6.1　安全引导的作用

        安全引导可用于保证系统的完整性，防止系统
中重要镜像文件被破坏或替换。一般情况下，安全
引导需要保护系统的BootLoader镜像文件、TEE镜
像文件、Linux内核镜像文件、Recover镜像文件以
及在ARMv8中使用的ATF镜像文件。将TEE镜像文
件的加载操作加入安全引导功能中可阻止黑客通过
替换TEE镜像文件的方式来窃取被TEE保护的重要
资料。当前使用ARM芯片的系统中大部分使能了安
全引导功能，该功能对于用户的最直接感受就是，
当用户非法刷入其他厂商的ROM后手机无法正常启
动，这是因为非法刷机将导致系统中的重要镜像文
件被替换，系统在启动过程中对镜像文件的电子验
签失败，如果BootLoader验证失败，则系统在进入
BootLoader阶段之前就会挂死。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 131

6.2　安全引导的原理

  安全引导功能的原理就是采用链式验签的方式
启动系统，也就是在系统启动过程中，在加载下一
个阶段的镜像之前都会对需要被加载的镜像文件进
行电子验签，只有验签操作通过后，该镜像才能被
加载到内存中，然后系统才会跳转到下一个阶段继
续执行，整个验签链中的任何一环验签失败都会导
致系统挂死，系统启动过程中的第一级验签操作是
由ChipRom来完成的。只要芯片一出厂，用户就无
法修改固化在芯片中的这部分代码，因此无法通过
修改第一级验签结果来关闭安全引导功能。而且验
签操作使用的RSA公钥或者哈希值将会被保存在
OTP/efuse中，该区域中的数据一般只有ChipRom和
TEE能够读取且无法被修改。RSA公钥或者哈希值
将会在产品出厂之前被写入到OTP/efuse中，而且不
同厂商使用的密钥会不一样。

  在谷歌的安全引导功能白皮书中提出了安全引
导功能实现方案的设计建议。谷歌建议将镜像文件
的电子签名信息和验签使用的RSA公钥保存在电子
证书中，系统在启动的过程中首先会验证电子证书
的合法性，如果验证通过则需从电子证书中获取签
名信息和RSA公钥，然后再利用它们对镜像文件进
行验证。整个验证过程就是先验证证书，验证证书

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 132

通过后再去验证镜像文件的合法性。但是在实际实
现过程中，大多数芯片厂商是将签名信息与需要被
验签的镜像文件打包在一起，而RSA公钥则会被打
包到执行验证操作的镜像文件中。

  不同厂商可能会对镜像文件进行加密操作，使
保存在设备中的镜像文件都是以密文的形式存在。
在启动过程中，首先会验证密文镜像文件的合法性
然后再进行解密镜像文件的操作，这些都完成后才
会将明文的镜像文件加载到内存中然后再执行跳转
操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 133

6.2.1 ARMv7安全引导的过程

  对于安全引导功能的实现和验证过程各家芯片
公司的方案都不一样，这是由该芯片的启动流程以
及启动所需镜像文件来决定的，但都会遵循链式验
签启动的原则。ARMv7架构并没有使用ATF，系统
的启动流程与以前一样使用BootLoader来引导Linux
内核和TEE OS。安全引导的启动流程如图6-1所
示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 134

     图6-1　安全引导的启动流程

  系统启动过程使用链式验签的方式进行引导，
其中任何一环验签失败都会导致系统启动失败，为
防止通过替换ramdisk来修改根文件系统中的内容，
一般将ramdisk与Linux内核打包在同一个镜像文件
中，而且该镜像文件需要待验签通过后才可被使
用。签名信息一般是对镜像文件的内容进行哈希计
算获取摘要后再对该摘要使用RSA私钥进行电子签
名来获得，验证时同样会计算需要被引导的镜像文
件的摘要，然后使用该摘要、签名信息以及RSA公
钥进行RSA算法的验证。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 135

6.2.2 ARMv8安全引导的过程

   ARMv8架构之后ARM提供了ATF，
BootLoader、TEE镜像文件、Linux内核镜像文件、
recovery镜像文件都是由ATF来进行引导和加载而
不是由ChipRom来完成的。ChipRom只会去验证
ATF中bl1的合法性，后续引导过程同样也是按照链
式验签的方式进行，符合TBBR规范。读者可使用
git命令从gitHub上获取ATF的所有源代码[1]。在
ARMv8架构中整个安全引导的流程如图6-2所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 136

     图6-2 ARMv8的Secure Boot流程
   ARMv8架构中引入了ATF，同时在ATF中提供
了安全引导的功能，BootLoader镜像、Linux内核、
recovery镜像和TEE OS镜像文件的签名方式都由
ATF决定。当然开发者也可以对ATF进行定制化，
修改ATF中的验签过程，但是修改后的验签方案需
要符合TBBR规范。

[1] ATF的git仓库链接可参阅ATF源代码链接：
https://github.com/linaro-swg/arm-trusted-firmware。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 137

6.3 ATF的启动过程

   ATF的启动过程根据ARMv8的运行模式
（AArch32/AArch64）会有所不同，但基本一致。
在AArch32中是不会去加载bl31而是将EL3或者
Monitor模式的运行代码保存在bl32中执行。在
AArch64中，ATF的完整启动流程如图6-3所示。










    图6-3 AArch64模式的ATF启动流程
   在上述启动过程中，从一个镜像跳转到另外一
个镜像文件执行的方式各不相同，以下为镜像跳转


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 138

的过程和方式说明。

1.bl1跳转到bl2执行

  在bl1完成了将bl2镜像文件加载到RAM中的操
作、中断向量表的设定以及其他CPU相关设定后，
bl1_main函数会解析出bl2镜像文件的描述信息，获
取入口地址，并设定下一个阶段的cpu上下文。这
些操作完成之后，调用el3_exit函数来实现bl1到bl2
的跳转，进入bl2中开始执行。

2.bl2跳转到bl31执行
  在bl2中将会加载bl31、bl32、bl33的镜像文件
到对应权限的内存中，并将该三个镜像文件的描述
信息组成一个链表保存起来，以备bl31启动bl32和
bl33使用。在AArch64中，bl31为EL3的执行软件，
其运行时的主要功能是对安全监控模式调用
（smc）指令和中断处理，运行在ARM的Monitor模
式中。

  bl32一般为TEE OS镜像文件，本章以OP-TEE
为例进行说明。

  bl33为正常世界状态的镜像文件，例如uboot、
EKD2等。当前该部分为BootLoader部分的镜像文
件，再由BootLoader来启动Linux内核镜像。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 139

  从bl2跳转到bl31是通过带入bl31的入口点信息
作为参数，然后调用安全监控模式调用指令，触发
在bl1中设定的安全监控模式调用请求，该请求处理
完成后会将中央处理器的执行权限交给bl31，并跳
转到bl31中去执行。
3.bl31跳转到bl32执行

  在bl31中会执行runtime_service_inti函数，该函
数会调用注册到EL3中所有服务的初始化函数，其
中有一个服务项就是TEE服务，该服务项的初始化
函数会将TEE OS的初始化函数赋值给bl32_init变
量，当所有服务项执行完初始化后，在bl31中会调
用bl32_init执行的函数来跳转到TEE OS中并开始执
行TEE OS的启动。
4.bl31跳转到bl33执行
  当TEE-OS镜像启动完成后会触发一个ID为
TEESMC_OPTEED_RETURN_ENTRY_DONE的安
全监控模式调用，该调用是用来告知EL3 TEE OS
镜像已经完成了初始化，然后将CPU的状态恢复到
bl31_init的位置继续执行。

  bl31通过遍历在bl2中记录的所有镜像信息的链
表来找到需要执行的bl33的镜像。然后通过获取到


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 140

bl33镜像的信息，设定下一个阶段的CPU上下文，
退出el3后进入到bl33镜像中开始执行。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 141

6.3.1 ATF中bl1的启动

               系统上电之后首先会运行ChipRom，之后会跳
转到ATF的bl1中继续执行。bl1主要初始化CPU、
设定异常向量、将bl2的镜像加载到安全RAM中，
然后跳转到bl2中开始运行。bl1的主要代码存放在
bl1目录中，bl1的链接文件是bl1/bl1.ld.s文件，该文
件指定bl1的入口函数是bl1_entrypoint。AArch32的
该函数定义在bl1/aarch32/bl1_entrypoint.S文件中，
AArch64的该函数定义在
bl1/aarch64/bl1_entrypoint.S文件中。bl1的执行流程
如图6-4所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 142

    图6-4    bl1执行流程
    1.bl1_entrypoint函数说明

    bl1_entrypoint函数主要完成ARMv8架构中EL3
    执行环境的基础初始化、设定异常向量表、加载bl2
    的镜像文件到内存中并进行跳转到bl2继续执行。该
    函数的内容如下：



    func bl1_entrypoint
    /* EL3级别运行环境的初始化,该函数定义在include/common/aarch64/el3_common_macros.S文件中*/
el3_entrypoint_common    \
    _set_endian=1     \
    _warm_boot_mailbox=!PROGRAMMABLE_RESET_ADDRESS  \
    _secondary_cold_boot=!COLD_BOOT_SINGLE_CPU      \
    _init_memory=1      \




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 143

       _init_c_runtime=1        \
       _exception_vectors=bl1_exceptions
bl     bl1_early_platform_setup  //调用bl1_early_platform_setup函数完成底层初始化
bl     bl1_plat_arch_setup      //调用bl1_plat_arch_setup完成平台初始化
bl     bl1_main       //调用bl1_main函数,初始化验证模块,加载下一阶段的image到RAM中
b      el3_exit       //调用el3_exit函数,跳转到下一个image(bl2)
endfunc bl1_entrypoint



el3_entrypoint_common函数执行时带入的参数
包括大小端标识、属于冷启动还是重启操作、是否
是从核的启动、是否需要进行内存初始化、是否需
要建立C语言运行环境（栈初始化）、异常向量表
地址注册等。

2.el3_entrypoint_common功能说明

该函数以宏的方式被定义，
                      主要用来完成EL3
运行环境的设置和异常向量表的注册，代码内容和
注释如下：



.macro el3_entrypoint_common    \
       _set_endian, _warm_boot_mailbox, _secondary_cold_boot, \
       _init_memory, _init_c_runtime, _exception_vectors
/* 通过sctlr寄存器设定大小端 */
.if \_set_endian
       mrs x0, sctlr_el3
       bic x0, x0, #SCTLR_EE_BIT
       msr sctlr_el3, x0
       isb
.endif /* _set_endian */
/* 判定是否需要调用do_cold_boot流程 */
.if \_warm_boot_mailbox
       bl plat_get_my_entrypoint
       cbz x0, do_cold_boot




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 144

       br     x0
do_cold_boot:
.endif /* _warm_boot_mailbox */
bl     reset_handler     //执行reset handle操作
el3_arch_init_common \_exception_vectors //初始化异常向量
/* 判定当前CPU是否是主CPU,如果是则执行主CPU的初始化 */
.if \_secondary_cold_boot
       //获取当前core的编号,判定当前是主核还是从核
       bl     plat_is_my_cpu_primary
       //如果是主核则调用do_primary_cold_boot执行主核启动
       cbnz     w0, do_primary_cold_boot
       bl     plat_secondary_cold_boot_setup   //如果是从核则执行从核的启动
       bl     el3_panic
do_primary_cold_boot:
.endif /* _secondary_cold_boot */
/* 初始化memory */
.if \_init_memory
       bl     platform_mem_init     //初始化memory
.endif /* _init_memory */
/* 初始化C语言的运行环境 */
.if \_init_c_runtime
#ifdef IMAGE_BL31
       adr x0, __RW_START__        //获取内存RW的起始地址
       adr x1, __RW_END__      //获取内存RW的末端地址
       sub x1, x1, x0      //RW的长度
       bl     inv_dcache_range      //无效数据cache
#endif /* IMAGE_BL31 */
       ldr x0, =__BSS_START__     //将BSS段内存的起始地址存放在x0中
       ldr x1, =__BSS_SIZE__        //将BSS段内如的某段地址存放在x1中
       bl     zeromem      //请扩BSS段内存
#if USE_COHERENT_MEM
       ldr x0, =__COHERENT_RAM_START__
       ldr x1, =__COHERENT_RAM_UNALIGNED_SIZE__
       bl     zeromem
#endif
#ifdef IMAGE_BL1
       ldr x0, =__DATA_RAM_START__     //获取bl1的数据段存放到RAM中的起始地址
       ldr x1, =__DATA_ROM_START__     //获取bl1中数据段在ROM中的起始地址
       ldr x2, =__DATA_SIZE__     //获取bl1数据端的大小
       bl     memcpy16     //将bl1的数据段复制到RAM中
#endif
.endif /* _init_c_runtime */
msr spsel, #0
bl     plat_set_my_stack        //设定堆栈
#if STACK_PROTECTOR_ENABLED




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
              更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 145

    .if \_init_c_runtime
    bl    update_stack_protector_canary
    .endif /* _init_c_runtime */
    #endif
    .endm
    #endif /* __EL3_COMMON_MACROS_S__ */


     el3_entrypoint_common函数主要完成C语言运
行环境的搭建、异常向量表的注册、bl1镜像文件的
复制、CPU安全运行环境的设定等。

3.bl1_early_platform_setup函数
     bl1_early_platform_setup函数主要完成CPU中
ARM核的早期初始化，包括内存、页表、外部设备
以及ARM核状态的设定，其内容如下：


    void bl1_early_platform_setup(void)
    {
     /* 使能看门狗,初始化console,初始化memory */
     arm_bl1_early_platform_setup();
     plat_arm_interconnect_init();//初始化外部设备
     plat_arm_interconnect_enter_coherency();//使能外部设备
    }


4.bl_main函数
     bl_main函数主要完成bl2镜像文件的加载和bl2
运行环境的配置，如果使能了安全引导功能，则还
需要对bl2镜像文件执行验签操作。该函数定义




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 146

在/bl1/bl1_main.c文件中，主要内容和注释如下：


void bl1_main(void)
{
 unsigned int image_id;
 print_errata_status();
#if DEBUG
 u_register_t val;
/* 确保MMU和cache使能 */
#ifdef AARCH32
 val = read_sctlr();
#else
 val = read_sctlr_el3();
#endif
 assert(val & SCTLR_M_BIT);
 assert(val & SCTLR_C_BIT);
 assert(val & SCTLR_I_BIT);
 val = (read_ctr_el0() >> CTR_CWG_SHIFT) & CTR_CWG_MASK;
 if (val != 0)
     assert(CACHE_WRITEBACK_GRANULE == SIZE_FROM_LOG2_WORDS(val));
 else
     assert(CACHE_WRITEBACK_GRANULE <= MAX_CACHE_LINE_SIZE);
#endif
 bl1_arch_setup();      //设置bl2镜像运行时的EL级别
#if TRUSTED_BOARD_BOOT
 auth_mod_init();      //初始化image的验证模块
#endif /* TRUSTED_BOARD_BOOT */
 bl1_platform_setup();        //平台相关设置,主要是IO的设置
 //获取下一个阶段image的ID值。默认返回值为BL2_IMAGE_ID
 image_id = bl1_plat_get_next_image_id();
 if (image_id == BL2_IMAGE_ID)
     bl1_load_bl2();        //将bl2 image加载到安全RAM中
 else
     NOTICE("BL1-FWU: *******FWU Process Started*******\n");
 //获取bl2镜像的描述信息、包括名字、ID、entry point info等,并将这些信息保存到
//bl1_cpu_context的上下文中
 bl1_prepare_next_image(image_id);
 console_flush();      //刷新console
}









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 147

5.bl1_prepare_next_image函数
      bl1_prepare_next_image函数用来获取bl2镜像的
描述信息、bl2的入口地址信息、设定bl2的运行状
态，以备跳转时使用，其内容和解释如下：



    void bl1_prepare_next_image(unsigned int image_id)
    {
     unsigned int security_state;
     image_desc_t *image_desc;
     entry_point_info_t *next_bl_ep;
     /* 获取bl2 image的描述信息,主要包括入口地址、名字等信息 */
     image_desc = bl1_plat_get_image_desc(image_id);
     assert(image_desc);
     /* 获取image的入口地址信息 */
     next_bl_ep = &image_desc->ep_info;
     //获取bl2 image的安全状态（判定该image是属于安全态的image的还是非安全态的image）
     security_state = GET_SECURITY_STATE(next_bl_ep->h.attr);
     /* 设定用于存放CPU context的变量 */
     if (!cm_get_context(security_state))
      cm_set_context(&bl1_cpu_context[security_state], security_state);
     /* 为下个阶段的image准备好SPSR数据 */
     if (security_state == SECURE) {
      next_bl_ep->spsr = SPSR_64(MODE_EL1, MODE_SP_ELX,
DISABLE_ALL_EXCEPTIONS);
     } else {
      /* Use EL2 if supported else use EL1. */
      if (read_id_aa64pfr0_el1() &
       (ID_AA64PFR0_ELX_MASK << ID_AA64PFR0_EL2_SHIFT)) {
       next_bl_ep->spsr = SPSR_64(MODE_EL2, MODE_SP_ELX,
           DISABLE_ALL_EXCEPTIONS);
      } else {
       next_bl_ep->spsr = SPSR_64(MODE_EL1, MODE_SP_ELX,
           DISABLE_ALL_EXCEPTIONS);
      }
     }
     bl1_plat_set_ep_info(image_id, next_bl_ep);
     /* 使用获取到的bl2 image的entrypoint info数据来初始化cpu context */
     cm_init_my_context(next_bl_ep);
     /* 为进入到下个EL级别做准备 */




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 148

 cm_prepare_el3_exit(security_state);
 /* 设定image的执行状态 */
 image_desc->state = IMAGE_STATE_EXECUTED;
 /* 打印出bl2 image的入口信息 */
 print_entry_point_info(next_bl_ep);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 149

6.3.2 ATF中bl2的启动

   bl2镜像将为后续镜像的加载执行相关的初始
化操作，主要是内存、MMU、串口以及EL3软件运
行环境的设置，并且加载bl3x的镜像到内存中。通
过查看bl2.ld.S文件可发现，bl2镜像的入口函数是
bl2_entrypoint。该函数定义在
bl2/aarch64/bl2_entrypoint.S文件中。该阶段的执行
流程如图6-5所示。










    图6-5     bl2执行流程
    1.bl2_entrypoint函数
    bl2_entrypoint函数最终会触发安全监控模式调
    用（smc），通知bl1将CPU的控制权限转交给

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 150

bl31，然后执行bl31。该函数会执行平台相关的初
始化、获取存放bl3x镜像文件的结构体变量、解析
出bl31的入口地址等。该函数的主要内容和注释如
下：



func bl2_entrypoint
    mov x20, x1        //获取可用安全内存的起始地址
    adr x0, early_exceptions      //设定异常向量
    msr vbar_el1, x0        //将异常向量表地址写入到VBAR寄存器中
    isb
    msr daifclr, #DAIF_ABT_BIT     //使能SErrot中断
    /* 使能指令cache、栈顶地址以及数据访问权限对齐检查 */
    mov x1, #(SCTLR_I_BIT | SCTLR_A_BIT | SCTLR_SA_BIT)
    mrs x0, sctlr_el1
    orr x0, x0, x1
    msr sctlr_el1, x0
    isb
    /* 获取有效的RW内存以备bl2使用 */
    adr x0, __RW_START__              //获取RW内存的起始地址
    adr x1, __RW_END__                //获取RW内存的末端地址
    sub x1, x1, x0                    //计算出RW内存的大小
    bl     inv_dcache_range           //禁止数据cache
    ldr x0, =__BSS_START__            //获取bl2中BSS段的起始地址
    ldr x1, =__BSS_SIZE__             //获取bl2中BSS段的大小
    bl     zeromem                    //清空BSS段中的内容
    #if USE_COHERENT_MEM
    ldr x0, =__COHERENT_RAM_START__
    ldr x1, =__COHERENT_RAM_UNALIGNED_SIZE__
    bl     zeromem
    #endif
    bl     plat_set_my_stack          //初始化bl2运行的栈
    #if STACK_PROTECTOR_ENABLED
    bl     update_stack_protector_canary //更新栈保护区域数据
    #endif
    mov x0, x20
    bl     bl2_early_platform_setup   //设置平台相关
    bl     bl2_plat_arch_setup        //设置架构相关
    bl     bl2_main                   //跳转到BL2的主要函数执行,从该函数中跳转到bl31以及bl32或者bl33
    no_ret      plat_panic_handler
    endfunc bl2_entrypoint




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
           更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 151

     在bl2_entrypoint函数中，完成bl2运行栈的初始
化，配置完运行环境后，会调用bl2_main函数来完
成bl2对bl3x镜像的加载，而CPU控制权限的转移则
是通过触发安全监控模式调用（smc）来实现。
2.bl2_main函数
     bl2_main函数完成了bl2阶段的主要操作，包括
对下一个阶段镜像文件的解析、获取入口地址和镜
像文件大小等信息，然后对镜像文件进行验签和加
载操作。将bl31加载到内存中后会触发安全监控模
式调用（smc）将CPU权限转交给bl31。该函数的
主要内容和相关注释如下：


    void bl2_main(void)
    {
     entry_point_info_t *next_bl_ep_info;
     bl2_arch_setup(); //执行平台相关初始化
    #if TRUSTED_BOARD_BOOT
     /* Initialize authentication module */
     auth_mod_init(); //初始化image验证模块
    #endif /* TRUSTED_BOARD_BOOT */
     //加载bl3x image到RAM中并返回bl31的入口地址
     next_bl_ep_info = bl2_load_images();
    #ifdef AARCH32
     disable_mmu_icache_secure(); //禁止MMU的指令cache
    #endif /* AArch32 */
     console_flush(); //刷新console操作
     /* 调用smc指令,触发在bl1中设定的smc异常中断处理函数,跳转到bl31 */
     smc(BL1_SMC_RUN_IMAGE, (unsigned long)next_bl_ep_info, 0, 0, 0, 0,0, 0);
    }





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 152

3.bl2_load_images函数
      bl2_load_images函数完成将bl32和bl33的镜像
文件加载到内存中并返回bl31镜像的入口地址，最
终在bl2_main函数中通过触发安全监控模式调用
（smc）跳转到bl31，并将CPU控制权限交给bl31。
该函数的主要内容和注释如下：



    entry_point_info_t *bl2_load_images(void)
    {
     bl_params_t *bl2_to_next_bl_params;
     bl_load_info_t *bl2_load_info;
     const bl_load_info_node_t *bl2_node_info;
     int plat_setup_done = 0;
     int err;
     /* 获取bl3x image的加载和入口函数信息 */
     bl2_load_info = plat_get_bl_image_load_info();
     /* 检查返回的bl2_load_info中的信息是否正确 */
     assert(bl2_load_info);
     assert(bl2_load_info->head);
     assert(bl2_load_info->h.type == PARAM_BL_LOAD_INFO);
     assert(bl2_load_info->h.version >= VERSION_2);
     /* 将bl2_load_info中的head变量的值赋值为bl2_node_info,即将bl31 image的入口信息传递给bl2_node_info变量 */
     bl2_node_info = bl2_load_info->head;
     /* 进入loop循环 */
     while (bl2_node_info) {
     /* 在加载特定的bl3x image到RAM之前先确定是否需要进行平台的初始化 */
     if (bl2_node_info->image_info->h.attr & IMAGE_ATTRIB_PLAT_SETUP) {
      if (plat_setup_done) {
             WARN("BL2: Platform setup already done!!\n");
      } else {
             INFO("BL2: Doing platform setup\n");
             bl2_platform_setup();
             plat_setup_done = 1;
      }
     }
     /* 对bl3x image进行电子验签,如果通过则执行加载操作 */
     if (!(bl2_node_info->image_info->h.attr & IMAGE_ATTRIB_SKIP_LOADING)) {
      INFO("BL2: Loading image id %d\n", bl2_node_info->image_id);



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 153

   err = load_auth_image(bl2_node_info->image_id,
    bl2_node_info->image_info);
   if (err) {
    ERROR("BL2: Failed to load image (%i)\n", err);
    plat_error_handler(err);
   }
  } else {
   INFO("BL2: Skip loading image id %d\n", bl2_node_info->image_id);
  }
  /* 可以根据实际需要更改,通过给定image ID来更改image的加载信息 */
  err = bl2_plat_handle_post_image_load(bl2_node_info->image_id);
  if (err) {
   ERROR("BL2: Failure in post image load handling (%i)\n",err);
   plat_error_handler(err);
  }
  bl2_node_info = bl2_node_info->next_load_info;
 }
 /* 获取下一个执行的镜像的入口信息,并且将以后会被执行的镜像的入口信息组合成链表 ,通过判断image des中的ep_info.h.attr的值是否为（EXECUTABLE|EP_FIRST_EX）来确定接下来第一个被执行的image*/
 bl2_to_next_bl_params = plat_get_next_bl_params();
 assert(bl2_to_next_bl_params);
 assert(bl2_to_next_bl_params->head);
 assert(bl2_to_next_bl_params->h.type == PARAM_BL_PARAMS);
 assert(bl2_to_next_bl_params->h.version >= VERSION_2);
 plat_flush_next_bl_params();
 /* 返回下一个进入的镜像的入口信息,即bl31的入口信息 */
 return bl2_to_next_bl_params->head->ep_info;
}



4.bl3x镜像文件信息

ATF使用bl_mem_params_node_t结构体变量数
组bl_mem_params_desc_ptr来保存bl3x镜像文件的
信息。该结构体内容如下：



typedef struct bl_mem_params_node {
 unsigned int image_id;        //镜像文件的id值
 image_info_t image_info;        //镜像文件的信息
 entry_point_info_t ep_info;       //bl3x的入口地址信息




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 154

    unsigned int next_handoff_image_id; //写一个阶段bl3x的id值
    bl_load_info_node_t load_node_mem; //该镜像文件需要被保存在RAM中的信息
    bl_params_node_t params_node_mem; //该镜像文件启动时所需参数在RAM中的信息
  } bl_mem_params_node_t;

   在bl2_load_images函数中通过调用
plat_get_bl_image_load_info函数来获取bl3x镜像文
件的信息，ATF源代码中通过使用
REGISTER_BL_IMAGE_DESCS宏将事先定义好的
bl2_mem_params_descs变量中的数据保存到
bl_mem_params_desc_ptr数组中，而
bl2_mem_params_descs中保存的就是所有bl3x镜像
文件的基本信息，开发者可根据不同平台的实际情
况修改bl2_mem_params_descs变量中各镜像文件的
信息。

5.bl2到bl31的跳转
   在bl2_main函数中最终会调用
smc（BL1_SMC_RUN_IMAGE，（unsigned long）
next_bl_ep_info，0，0，0，0，0，0）来触发一个
类型为BL1_SMC_RUN_IMAGE的安全监控模式调
用。安全监控模式调用的处理接口在bl1阶段时被指
定，调用该函数时传入的command ID是
BL1_SMC_RUN_IMAGE，故执行该函数之后，系
统将跳转到中断处理函数（smc_handler64）继续执
行。该函数定义在bl1/aarch64/bl1_exception.S文件


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 155

中。该函数最终通过判定安全监控模式调用的类型
（在bl2中将会发送类型为BL1_SMC_RUN_IMAGE
的smc）查看当前的安全监控模式调用是否是用于
跳转，其内容如下：



    func smc_handler64
    /* 判定触发smc操作时带入的参数是否为跳转执行image的操作 */
    mov x30, #BL1_SMC_RUN_IMAGE      //将BL1_SMC_RUN_IMAGE的值保存到x30
    cmp x30, x0          //比较x30与x0的值
    //如果x30与x0不同,则认为是普通类型的异常,进入smc_handler进行处理
    b.ne     smc_handler
    mrs x30, scr_el3        //获取scr寄存器的值
    tst x30, #SCR_NS_BIT        //比较scr寄存器中的NS bit与SCR_NS_BIT是否相等
    //如果当前NS bit为非安全位,则证明不合法,产生异常
    b.ne     unexpected_sync_exception
    //获取offset和sp的值
    ldr x30, [sp, #CTX_EL3STATE_OFFSET + CTX_RUNTIME_SP]
    msr spsel,#0         //清空spsel中的值
    mov sp, x30          //保存x30的值到sp寄存器,用于返回
    mov x20, x1          //将x1中的数据保存到x20中
    mov x0, x20          //将x20的数据保存到x0中
    bl    bl1_print_next_bl_ep_info      //打印出bl3x镜像文件信息
    //传入参数和bl3x入口函数的PC指针
    ldp x0, x1, [x20, #ENTRY_POINT_INFO_PC_OFFSET]
    msr elr_el3, x0
    msr spsr_el3, x1
    ubfx     x0, x1, #MODE_EL_SHIFT, #2   //设定ARM核模式
    cmp x0, #MODE_EL3        //比较x0寄存器中的值是否为MODE_EL3
    b.ne     unexpected_sync_exception    //如果x0中不是MODE_EL3,则产生异常
    bl    disable_mmu_icache_el3        //禁止MMU的指令cache
    tlbi     alle3
    #if SPIN_ON_BL1_EXIT
    bl    print_debug_loop_message
    debug_loop:
    b     debug_loop
    #endif
    mov x0, x20
    bl    bl1_plat_prepare_exit/
    /* 设定返回参数 */
    ldp x6, x7, [x20, #(ENTRY_POINT_INFO_ARGS_OFFSET + 0x30)]




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 156

ldp x4, x5, [x20, #(ENTRY_POINT_INFO_ARGS_OFFSET + 0x20)]
ldp x2, x3, [x20, #(ENTRY_POINT_INFO_ARGS_OFFSET + 0x10)]
ldp x0, x1, [x20, #(ENTRY_POINT_INFO_ARGS_OFFSET + 0x0)]
eret //跳转到bl3x执行
endfunc smc_handler64



在此安全监控模式调用处理过程中会将ARM
核的状态切到EL3运行，即bl31是运行在EL3中的。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 157

6.3.3 ATF中bl31的启动

   在bl2中触发安全监控模式调用后会跳转到bl31
中执行，bl31最主要的作用是建立EL3运行态的软
件配置，在该阶段会完成各种类型的安全监控模式
调用ID的注册和对应的ARM核状态的切换，bl31运
行在EL3。bl31的执行流程如图6-6所示。










    图6-6     bl31执行流程
    1.bl31_entrypoint函数
    通过bl31.ld.S文件可知，bl31的入口函数是
    bl31_entrypoint。该函数的内容如下：

    func bl31_entrypoint

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 158

/*
el3初始化操作,该el3_entrypoint_common函数在上面已经介绍过,其中runtime_exceptions为el3 runtime software的异常向量表,内容定义在bl31/aarch64/runtime_exceptions.S文件中
*/
#if !RESET_TO_BL31
  mov x20, x0
  mov x21, x1
  el3_entrypoint_common           \
         _set_endian=0            \
         _warm_boot_mailbox=0     \
         _secondary_cold_boot=0   \
         _init_memory=0           \
         _init_c_runtime=1        \
         _exception_vectors=runtime_exceptions
  mov x0, x20
  mov x1, x21
#else
  el3_entrypoint_common           \
         _set_endian=1            \
         _warm_boot_mailbox=!PROGRAMMABLE_RESET_ADDRESS  \
         _secondary_cold_boot=!COLD_BOOT_SINGLE_CPU      \
         _init_memory=1           \
         _init_c_runtime=1        \
         _exception_vectors=runtime_exceptions
  mov x0, 0
  mov x1, 0
#endif /* RESET_TO_BL31 */
  bl     bl31_early_platform_setup          //平台架构相关的初始化设置
  bl     bl31_plat_arch_setup       //执行AArch初始化
  bl     bl31_main     //跳转到bl31_main函数,执行该阶段需要的主要操作
  adr x0, __DATA_START__            //获取REE镜像的DATA段的起始地址
  adr x1, __DATA_END__        //获取REE镜像的DATA段的末端地址
  sub x1, x1, x0     //计算镜像文件的大小
  bl     clean_dcache_range         //清空数据cache
  adr x0, __BSS_START__           //获取BSS段的起始地址
  adr x1, __BSS_END__      //获取BSS端的末端地址
  sub x1, x1, x0     //计算BSS段的长度
  bl     clean_dcache_range         //清空数据cache
  //执行完成将跳转到bl33中执行,即执行BootLoader
  b      el3_exit
endfunc bl31_entrypoint



2.bl31_main函数





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 159

    该函数主要完成必要的初始化操作，注册EL3
中各种安全监控模式调用的处理函数，以便在启动
完成后响应在REE侧和TEE侧产生的安全监控模式
调用。该函数的内容如下：


    void bl31_main(void)
    {
     bl31_platform_setup();    //初始化相关驱动、时钟等
     bl31_lib_init();      //用于执行bl31软件中相关全局变量的初始化
     /*初始化el3中的service,通过在编译时指定特定的section来确定哪些service会被作为el3 service*/
     runtime_svc_init();
     /* 如果注册了TEE OS支持,在调用完成run_service_init之后会使用TEE OS的入口函数初始化bl32_init变量,然后执行对应的init函数,以OP-TEE为例,bl32_init将会被初始化成opteed_init,到此将会执行opteed_init函数来进入OP-TEE OS的启动,当OP-TEE OS启动完后,将会产生一个TEESMC_OPTEED_RETURN_ENTRY_DONE的smc异常,通知bl31已经完成了OP-TEE的启动*/
     if (bl32_init) {
      INFO("BL31: Initializing BL32\n");
      (*bl32_init)();
     }
     //准备跳转到bl33,在执行runtime_service时会运行一个spd service,该service的初始化函数将会去执行bl32的镜像来完成TEE OS初始化
     bl31_prepare_next_image_entry();
     console_flush();
     bl31_plat_runtime_setup();
    }


    runtime_svc_init函数会将各种安全监控模式调
    用的处理函数的指针注册到EL3中，并通过service-
    >init函数来进行初始化，将TEE OS镜像的入口函数
    赋值给bl32_init，通过执行bl32_init指向的函数进入
    到TEE OS的启动过程。待TEE OS启动完成之后就
    会去查找bl33的镜像文件，即REE侧的镜像文件，
    开始进入REE侧镜像的启动。
    3.runtime_svc_init函数





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 160

       该函数主要用来建立安全监控模式调用处理函
数的索引表，
    并执行EL3中提供的服务项的初始化
操作，
获取TEE OS的入口地址并赋值给bl32_init变
量，
  以备启动TEE OS。而这些处理函数是通过
DECLARE_RT_SVC宏定义被编译到镜像文件的
rt_svc_descs段中的。


void runtime_svc_init(void)
{
 int rc = 0, index, start_idx, end_idx;
 /*判定rt_svc_descs段中service条数的是否超出MAX_RT_SVCS条*/
 assert((RT_SVC_DESCS_END >= RT_SVC_DESCS_START) &&
  (RT_SVC_DECS_NUM < MAX_RT_SVCS));
 if (RT_SVC_DECS_NUM == 0)
 return;
 /* 初始化 t_svc_descs_indices数组中的数据成-1,表示当前所有的service无效*/
 memset(rt_svc_descs_indices, -1, sizeof(rt_svc_descs_indices));
 /* 获取第一条EL3 service在RAM中的起始地址,通过获取RT_SVC_DESCS_START的值来确定,该值在链接文件中有定义 */
 rt_svc_descs = (rt_svc_desc_t *) RT_SVC_DESCS_START;
 /* 遍历整个rt_svc_des段,将其call type与rt_svc_descs_indices中的index建立对应关系 */
 for (index = 0; index < RT_SVC_DECS_NUM; index++) {
 rt_svc_desc_t *service = &rt_svc_descs[index];
 /* 判定在编译时注册的service是否有效 */
 rc = validate_rt_svc_desc(service);
 if (rc) {
  ERROR("Invalid runtime service descriptor %p\n",
      (void *) service);
  panic();
 }
 /* 执行当前service的init的操作 */
 if (service->init) {
  rc = service->init();
  if (rc) {
  ERROR("Error initializing runtime service %s\n",
      service->name);
      continue;
  }
 }
 /* 根据该service的call type以及start oen来确定唯一的index,并且将该service中支持的所有call type生成唯一的标识映射到同一个index中 */




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 161

     start_idx = get_unique_oen(rt_svc_descs[index].start_oen,
     service->call_type);
     assert(start_idx < MAX_RT_SVCS);
     end_idx = get_unique_oen(rt_svc_descs[index].end_oen,
     service->call_type);
     assert(end_idx < MAX_RT_SVCS);
     for (; start_idx <= end_idx; start_idx++)
     rt_svc_descs_indices[start_idx] = index;
    }
    }



4.DECLARE_RT_SVC

      该宏用来在编译时将EL3中的service编译进
rt_svc_descs段中。该宏定义如下：


    #define DECLARE_RT_SVC(_name, _start, _end, _type, _setup, _smch) \
     static const rt_svc_desc_t __svc_desc_ ## _name \
     __section("rt_svc_descs") __used = { \
    .start_oen = _start, \
    .end_oen = _end, \
    .call_type = _type, \
    .name = #_name, \
    .init = _setup, \
    .handle = _smch }



    该宏中的各种参数说明如下：

    ·start_oen：该service的起始内部编号；
    ·end.oen：该service的末尾编号；
    ·call_type：调用的smc的类型；




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 162

   ·name：该service的名字；
   ·init：该service在执行之前需要被执行的初始
化操作；

   ·handle：当触发了call type的调用时调用的处
理该请求的函数。

5.REE侧镜像文件的启动
   在bl31_main中启动完TEE OS之后通过调用
bl31_prepare_next_image_entry函数来获取下一个阶
段需要被加载的镜像文件，即REE侧的镜像文件，
并配置好REE侧镜像的运行环境。bl31_main执行完
成之后会跳转到bl31_entrypoint中继续执行，计算
出需要被加载的镜像文件的数据段大小和起始地址
并清空BSS端中的数据，从EL3进入到EL1-NS开始
执行REE侧的代码。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 163

6.3.4 ATF中bl32的启动

   bl31中的runtime_svc_init函数会初始化OP-TEE
对应的服务，通过调用该服务项的初始化函数来完
成OP-TEE的启动。对于OP-TEE的服务项会通过
DECLARE_RT_SVC宏在编译时被存放到rt_svc_des
段中。该段中的init成员会被初始化成opteed_setup
函数，由此开始进入到OP-TEE OS的启动。整个流
程如图6-7所示。







        图6-7 bl32执行流程
1.opteed_setup函数
   该函数是ATF启动OP-TEE的入口函数，该函
数会查找到OP-TEE镜像的信息、检查OP-TEE的入
口函数指针是否有效、设置OP-TEE运行的上下
文，然后调用OP-TEE的入口函数，开始执行OP-

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 164

TEE的启动。该函数的内容如下：


int32_t opteed_setup(void)
{
 entry_point_info_t *optee_ep_info;
 uint32_t linear_id;
 linear_id = plat_my_core_pos();      //获取当前core的ID
 /* 获取bl32(OP-TEE)镜像的描述信息 */
 optee_ep_info = bl31_plat_get_next_image_ep_info(SECURE);
 if (!optee_ep_info) {
  WARN("No OPTEE provided by BL2 boot loader, Booting device"
  " without OPTEE initialization. SMC's destined for OPTEE"
  " will return SMC_UNK\n");
  return 1;
 }
 /* 检查OP-TEE镜像指定的PC地址是否有效 */
 if (!optee_ep_info->pc)
  return 1;
 opteed_rw = OPTEE_AARCH64;
 /* 初始化OP-TEE运行时CPU的smc上下文 */
 opteed_init_optee_ep_state(optee_ep_info,
          opteed_rw,
          optee_ep_info->pc,
          &opteed_sp_context[linear_id]);
 /* 使用opteed_init初始化bl32_init变量,以备在bl31中调用 */
 bl31_register_bl32_init(&opteed_init);
 return 0;
}



2.opteed_init函数
该函数的地址会被赋值给bl32_init变量，
              在
bl31_main函数中会被调用，主要用来完成启动OP-
TEE的设置。该函数内容如下：


static int32_t opteed_init(void)




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 165

{
 uint32_t linear_id = plat_my_core_pos();
 //获取core的执行上下文变量
 optee_context_t *optee_ctx = &opteed_sp_context[linear_id];
 entry_point_info_t *optee_entry_point;
 uint64_t rc;
 /* 获取OPTEE image的信息 */
 optee_entry_point = bl31_plat_get_next_image_ep_info(SECURE);
 assert(optee_entry_point);
 /* 使用optee image的entry point信息初始化CPU的上下文 */
 cm_init_my_context(optee_entry_point);
 /* 开始设置CPU参数,最终会调用opteed_enter_sp函数执行跳转到OP-TEE的操作 */
 rc = opteed_synchronous_sp_entry(optee_ctx);
 assert(rc != 0);
 return rc;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 166

6.3.5 ATF启动过程小结

    ATF作为最底层固件，OP-TEE OS、
BootLoader、Linux内核的加载都是由ATF来完成
的，而且ATF实现了安全引导的功能。bl31运行于
EL3，待系统启动完成后，在REE侧或TEE侧触发
的安全监控模式调用（smc）都会进入bl31中被处
理。OP-TEE启动完成后会返回一个包含用于处理
各种类型的安全监控模式调用的函数指针结构体变
量，该变量会被添加到bl31的handle中，用于处理
REE侧触发的安全监控模式调用。bl2启动时通过触
发安全监控模式调用通知bl1将CPU控制权限交给
bl31，bl31通过解析特定段中是否存在OP-TEE的入
口函数指针来确定是否需要加载OP-TEE。OP-TEE
启动后会触发安全监控模式调用重新进入到bl31中
继续执行。bl31通过查询链表的方式获取下一个需
要被加载REE侧的镜像文件，并设定好REE侧运行
时CPU的状态和运行环境，然后退出EL3进入REE
侧镜像文件的启动，一般第一个REE侧镜像文件为
BootLoader，BootLoader会加载Linux内核。






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 167

6.4　小结

  本章主要介绍了安全引导的功能以及在
ARMv8架构中引入的ATF的启动过程。由于篇幅有
限，对于安全引导功能在ARMv7架构中的具体实现
没有进行介绍。各芯片厂商的实际实现方法也不一
样，但都会遵循链式验签的原则，笔者就曾经遇见
过一款芯片，在其安全引导功能的实现中共使用了
8个电子证书、9对RSA密钥对，该验证方案的过程
和逻辑相当复杂。而由于ARMv8中引入ATF，其已
完成了大部分的验签功能的开发，芯片厂商只需进
行相应的调整就能实现完整的安全引导功能。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 168

第7章　OP-TEE OS的启动过程

7.1 OP-TEE镜像启动过程

        在使用QEMU运行OP-TEE时，entry.S文件会调
用blx ip指令跳转到OP-TEE OS中，开始执行OP-
TEE OS的启动。如果系统支持ATF，则OP-TEE OS
镜像的加载由ATF来完成，OP-TEE属于ATF中的
bl32阶段，ATF的bl31阶段调用opteed_entry_sp函数
跳转到OP-TEE OS中执行OP-TEE OS的启动。32位
系统的OP-TEE与64位系统的OP-TEE的启动过程只
是底层的执行流程不一致，其他过程则大致相同。
本节将介绍ARM32位系统的启动过程以及ARM64
位系统OP-TEE的启动过程与ARM32位OP-TEE系统
的启动过程的差异。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 169

7.1.1 OP-TEE OS的入口函数

   OP-TEE镜像的入口函数是在编译OP-TEE OS
时通过链接文件来确定的，OP-TEE在编译时是按
照optee_os/core/arch/arm/kernel/kern.ld.S文件链接生
成OP-TEE OS的镜像文件，在kern.ld.S文件中通过
ENTRY宏来指定OP-TEE OS的入口函数，在OP-
TEE中指定的入口函数是_start，对于ARM32位系
统，该函数定义在
optee_os/core/arch/arm/generic_entry_a32.S文件中，
对于ARM64位系统而言，该函数定义在
optee_os/core/arch/arm generic_entry_a64.S文件中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 170

7.1.2 OP-TEE的内核初始化过程

   _start会调用reset函数进入OP-TEE OS的启动过
程。由于对称多处理（Symmetrical Multi-
Processing，SMP）架构的原因，在reset函数中会对
主核和从核进行不同的启动操作，分别调用
reset_primary函数和reset_secondary函数来完成。

1.reset入口函数执行内容
   reset函数是主核和从核启动的第一个函数，该
函数的执行流程如图7-1所示。










    图7-1 reset函数执行流程


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 171

      进入到reset函数后，系统会将_start的地址写入
VBAR寄存器作为中断向量表的起始地址使用，在
启动从核时，从核知道会到该地址去获取应该执行
代码来完成从核的启动。整个reset函数的内容和注
释如下：



    LOCAL_FUNC reset , :
    UNWIND(  .fnstart)
    UNWIND(  .cantunwind)
    bootargs_entry     //获取启动带入的参数,主要是启动地址、device tree地址等
    /* 使能对齐检查并禁用数据和指令缓存 */
    read_sctlr r0     //读取sctlr中的数据,获取当前CPU控制寄存器中的值
    #if defined(CFG_SCTLR_ALIGNMENT_CHECK)
    orr r0, r0, #SCTLR_A        //设定对齐校验
    #else
    bic r0, r0, #SCTLR_A
    #endif
    bic r0, r0, #SCTLR_C       //关闭数据cache
    bic r0, r0, #SCTLR_I       //关闭指令cache
    #if defined(CFG_HWSUPP_MEM_PERM_WXN) && defined(CFG_CORE_RWDATA_NOEXEC)
    orr r0, r0, #(SCTLR_WXN | SCTLR_UWXN)
    #endif
    write_sctlr r0     //将r0写入到sctlr中,用于关闭cache
    isb
    /* 早期ARM核安全监控模式态的特殊配置 */
    bl       plat_cpu_reset_early       //执行CPU早期初始化
    ldr r0, =_start      //设定r0寄存器的值为_start函数的地址
    write_vbar r0     //将_start函数的地址写入VBAR寄存器中,用于启动时使用
    #if defined(CFG_WITH_ARM_TRUSTED_FW)
    b        reset_primary     //支持ATF时跳转到reset_primary中执行
    #else
    bl       get_core_pos      //判定当前CPU CORE的编号
    cmp r0, #0      //将获得的CPU编号与0对比
    beq reset_primary      //如果当前core是主核,则使用reset_primary进行初始化
    b        reset_secondary        //如果当前core是从核,则使用reset_secondary进行初始化
    #endif
    UNWIND(  .fnend)
    END_FUNC reset






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 172

plat_cpu_reset_early函数将会设定SCR寄存器中
的安全标志位，用于标记当前CPU是处于安全世界
状态中，并且将_start地址写入VBAR寄存器，用于
在需要启动从核时系统能找到启动代码的入口地
址，reset_primary函数是主核启动代码的入口函
数，该函数将会启动主核的基本初始化、配置运行
环境，然后再开始执行唤醒从核的操作。对于从核
的唤醒操作，如果系统支持PSCI，从核的唤醒是在
REE OS启动时，发送PSCI给EL3或Monitor模式的
代码来启动从核；如果不使用PSCI，而是选择在
OP-TEE中使能CFG_SYNC_BOOT_CPU，则OP-
TEE会在主核启动结束后唤醒从核。
2.reset_primary函数的执行

本小节以CONFIG_BOOT_SYNC_CPU使能为
例，在使能PSCI系统中，不需要使能此宏。
reset_primary函数是OP-TEE对CPU主核进行初始化
操作的函数，该函数会初始化系统的MMU，并调
用generic_boot_init_primary函数完成OP-TEE运行环
境的建立，然后触发sev操作来唤醒从核，待所有
CPU核都启动完成之后，OP-TEE会触发安全监控
模式调用（smc），通知系统OP-TEE启动已完成并
将CPU的状态切换回到正常世界状态，该函数的执
行流程如图7-2所示。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 173

图7-2 reset_primary函数执行流程
reset_primary函数的主要代码内容如下：


LOCAL_FUNC reset_primary , :
UNWIND(  .fnstart)
UNWIND(  .cantunwind)
/* 清空BSS段 */
ldr r0, =__bss_start
ldr r1, =__bss_end
mov r2, #0
mov r3, #0
clear_bss:
stmia     r0!, {r2, r3}
cmp r0, r1
bls clear_bss
/* 初始化内存shadow区域,并设定权限 */
#ifdef CFG_CORE_SANITIZE_KADDRESS
ldr r0, =__asan_shadow_start
ldr r1, =__asan_shadow_end
mov r2, #ASAN_DATA_RED_ZONE
shadow_no_access:
str r2, [r0], #4




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 174

cmp r0, r1
bls shadow_no_access
/* 标记整个栈区域准备完成 */
ldr r2, =CFG_ASAN_SHADOW_OFFSET
ldr r0, =__nozi_stack_start
lsr r0, r0, #ASAN_BLOCK_SHIFT
add r0, r0, r2
ldr r1, =__nozi_stack_end
lsr r1, r1, #ASAN_BLOCK_SHIFT
add r1, r1, r2
mov r2, #0
shadow_stack_access_ok:
strb    r2, [r0], #1
cmp r0, r1
bls shadow_stack_access_ok
#endif
set_sp      //设定sp寄存器
bl     plat_cpu_reset_late //core的后期初始化,可根据具体情况执行特定操作
bl     console_init      //初始化log数据
inval_cache_vrange(__text_start, __end)   //在初始化阶段禁止数据cache
bl     core_init_mmu_map        //初始化MMU页表
bl     core_init_mmu_regs      //将MMU页表信息写入MMU的TTBRx寄存器中
bl     cpu_mmu_enable      //使能MMU
bl     cpu_mmu_enable_icache    //使能MMU的指令cache
bl     cpu_mmu_enable_dcache    //使能MMU的数据cache
mov r0, r4             /* 页表区域的地址 */
mov r1, r5             /* 非安全入口地址 */
mov r2, r6      /* 设备树地址 */
//带入paged_table、 Linux内核的地址、设备树信息进入OP-TEE系统运行环境的建立
bl     generic_boot_init_primary
mov r4, r0
flush_cache_vrange(__text_start, __end)   //刷新cache
cpu_is_ready      //设定CPU主核已经ready
flush_cpu_semaphores        //刷新信号量通知从核启动
wait_secondary     //等待从核启动完成
bl     thread_clr_boot_thread      //清空系统各thread的状态
#if defined(CFG_WITH_ARM_TRUSTED_FW)
mov r1, r4    //如果支持ATF,则将OP-TEE的handle返回给ATF
#else
mov r4, #0
mov r3, r6
mov r2, r7
mov r1, #0
#endif /* CFG_WITH_ARM_TRUSTED_FW */
mov r0, #TEESMC_OPTEED_RETURN_ENTRY_DONE  //设定返回给Normal World的值




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 175

    smc #0     //调用SMC操作切回到Normal World状态,OP-TEE启动结束
    b        . /* SMC should not return */
    UNWIND(  .fnend)
    END_FUNC reset_primary


3.generic_boot_init_primary函数内容

     generic_boot_init_primary函数是OP-TEE建立系
统运行环境的入口函数，该函数会进行建立线程运
行空间、初始化OP-TEE内核组件等操作。该函数
的执行流程如图7-3所示。










    图7-3     generic_boot_init_primary函数执行流程
    generic_boot_init_primary函数会调用




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 176

init_primary_helper函数来完成系统运行环境的建
立，如果系统支持ATF，则该函数会返回OP-TEE
的处理句柄，该处理句柄主要包含各种安全监控模
式调用的处理函数、安全世界状态（SWS）的中断
以及其他事件的处理函数，ATF中的bl31解析完安
全监控模式调用或中断请求后会在安全世界状态调
用该处理句柄来处理对应的事件。

     init_primary_helper函数的主要内容如下：


    static void init_primary_helper(unsigned long pageable_part,
                    unsigned long nsec_entry, unsigned long fdt)
    {
     thread_set_exceptions(THREAD_EXCP_ALL); //设置支持哪些异常处理
     init_vfp_sec();      //初始化浮点运算（根据实际需要考虑是否开启）
     //初始化各种memory,清空BSS段,分配TA运行时的memory
     init_runtime(pageable_part);
     /* 初始化TEE中支持的线程栈、异常处理、pagetable */
     thread_init_primary(generic_boot_get_handlers());
     //初始化每个CPU的monitor态的处理方式,如果支持ATF,则无需该操作
     thread_init_per_cpu();
     /* 如果系统不支持ATF,则需要配置在Linux内核中monitor的处理方式 */
     init_sec_mon(nsec_entry);
     /* 初始化device tree */
     init_fdt(fdt);
     /* 初始化中断控制器 */
     main_init_gic();
     /* 初始化非安全侧的浮点运算 */
     init_vfp_nsec();
     /* 初始化共享内存并执行存放在__initcall_start段的其他初始化函数 */
     if (init_teecore() != TEE_SUCCESS)
     panic();
     DMSG("Primary CPU switching to normal world boot\n");
    }






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 177

                           init_primary_helper函数最后会调用init_teecore
来完成OP-TEE内核的初始化，在init_teecore函数中
会设定共享内存、系统时间，然后再返回去执行
OP-TEE镜像文件中的_initcall段中的内容来启动系
统的服务以及安全驱动的挂载。

4.call_initcalls函数

  init_teecore函数通过调用call_initcalls来启动系
统的服务以及安全驱动的挂载，该函数的内容如
下：

static void call_initcalls(void)
{
  initcall_t *call;
  /* 遍历并执行_initcallx段中所有函数 */
  for (call = &__initcall_start; call < &__initcall_end; call++) {
   TEE_Result ret;
   ret = (*call)();
   if (ret != TEE_SUCCESS) {
    EMSG("Initial call 0x%08" PRIxVA " failed",
    (vaddr_t)call);
   }
  }
}

  在执行call_initcalls函数之前，系统已完成了
memory、CPU相关设置、中断控制器、共享内存、
线程堆栈设置、TA运行内存的分配等操作。
call_initcalls是通过遍历OP-TEE镜像文件的_initcall
段中从_initcall_start到_initcall_end之间的所有函数

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 178

来完成启动服务和驱动的挂载操作。

   OP-TEE镜像文件中_initcalls段的内容是通过使
用__define_initcall宏来告知编译器的，在编译时会
将使用该宏定义的函数保存到OP-TEE镜像文件的
_initcall段中。该宏定义如下：

  #define __define_initcall(level, fn) \
    static initcall_t __initcall_##fn __attribute__((used)) \
    __attribute__((__section__(".initcall" level))) = fn

   initcall_t：是一个函数指针类型(typedef
int(*initcall_t)(void))。
   __attribute__((__section__())：将fn对象放在一
个由括号中的名称指定的section中。

   ##：连接作用。

   例如，如果使用该宏如下：

  __define_initcall("1", init_operation)

则该宏的作用是声明一个名称为
__initcall_init_operation的函数指针，将该函数指针
初始化为init_operation，并在编译时将该函数的内


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 179

    容存放在名称为“.initcall1”的段中。
    core/arch/arm/kernel/kern.ld.S文件中存在如下内容：


    __initcall_start = .;
    KEEP(*(.initcall1))
    KEEP(*(.initcall2))
    KEEP(*(.initcall3))
    KEEP(*(.initcall4))
    __initcall_end = .;


      即在__initcall_start到__initcall_end之间保存的
是initcall1到initcall4之间的内容，而在整个OP-TEE
源代码的core/include/initcall.h文件中，
__define_initcall宏被使用的情况如下：


    #define __define_initcall(level, fn) \
    #define service_init(fn)          __define_initcall("1", fn)
    #define service_init_late(fn)     __define_initcall("2", fn)
    #define driver_init(fn)           __define_initcall("3", fn)
    #define driver_init_late(fn)      __define_initcall("4", fn)



      所以遍历执行从__initcall_start到__initcall_end
之间的内容就是启动OP-TEE的服务以及完整安全
驱动的挂载。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 180

7.1.3 OP-TEE服务项的启动

    OP-TEE服务项的启动分为：service_init以及
service_init_late，需要被启动的服务项通过使用这
两个宏，在编译时，相关服务的内容将会被保存到
initcall1和initcall2中。

1.service_init宏
    在OP-TEE使用中使用service_init宏定义的服务
项如下：

service_init(register_supplicant_user_ta);
service_init(verify_pseudo_tas_conformance);
service_init(tee_cryp_init);
service_init(tee_se_manager_init);

                        如果开发者有实际需求，可以将自己希望添加
的服务项功能按照相同的方式添加到系统中。在当
前的OP-TEE中默认是启动上述四个服务，分别定
义在以下文件：

register_supplicant_user_ta: core/arch/arm/kernel/ree_fs_ta.c
verify_pseudo_tas_conformance: core/arch/arm/kernel/pseudo_ta
tee_cryp_init: core/tee/tee_cryp_utl.c
tee_se_manager_init: core/tee/se/manager.c



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 181

     register_supplicant_user_ta部分：
     该操作主要是注册OP-TEE加载REE侧的TA镜
像时需要使用的操作接口，当REE侧执行open
session操作时，TEE侧会根据UUID的值在REE侧的
文件系统中查找该文件，然后通过RPC请求通知
tee_supplicant从REE的文件系统中读取与UUID对应
的TA镜像文件的内容并传递到TEE侧。

     verify_pseudo_tas_conformance部分：
     该函数主要是用来校验OP-TEE中静态TA的合
法性，需要检查OP-TEE OS中静态TA的UUID、函
数指针以及相关的flag。该段代码如下：


    static TEE_Result verify_pseudo_tas_conformance(void)
    {
     //获取存放psedo TAs的head info的段起始地址
     const struct pseudo_ta_head *start = &__start_ta_head_section;
     //获取存放psedo TAs的head info的段末尾地址
     const struct pseudo_ta_head *end = &__stop_ta_head_section;
     const struct pseudo_ta_head *pta;    //定义一个指向TA head的变量指针
     for (pta = start; pta < end; pta++) {
     const struct pseudo_ta_head *pta2;
     /* 检查psedo TAs的head info中包含的UUID信息是否有相同的 */
     for (pta2 = pta + 1; pta2 < end; pta2++)
     if (!memcmp(&pta->uuid, &pta2->uuid, sizeof(TEE_UUID)))
     goto err;
     /* 检查invoke函数指针是否为空和相关的flag是否合法 */
     if (!pta->name ||
     (pta->flags & PTA_MANDATORY_FLAGS) != PTA_MANDATORY_FLAGS ||
     pta->flags & ~PTA_ALLOWED_FLAGS ||
     !pta->invoke_command_entry_point)
     goto err;



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 182

     }
     return TEE_SUCCESS;
    err:
     DMSG("pseudo TA error at %p", (void *)pta);
     panic("pta");
    }



      OP-TEE OS镜像文件中的
__start_ta_head_section与__stop_ta_head_section之间
保存的是OP-TEE所有静态TA的内容，其值的定义
见core/arch/arm/kernel/kern.ld.S文件，
        分别表示
ta_head_section段的起始地址和末端地址。

      在编译OP-TEE的静态TA时，使用
pseudo_ta_register宏来告知编译器将静态TA的内容
保存到ta_head_section段中，该宏定义在
core/arch/arm/include/kernel/pseudo_ta.h文件中，内
容如下：



    #define pseudo_ta_register(...) static const struct pseudo_ta_head __head \
     __used __section("ta_head_section") = { __VA_ARGS__ }



    共有六个静态TA在OP-TEE编译时会被打包进
    OP-TEE的镜像文件中，分别如下：


    gprof: core/arch/arm/pta/gprof.c
    interrupt_tests.ta: core/arch/arm/pta/Iiterrupt_tests.c
    stats.ta: core/arch/arm/pta/stats.c
    se_api_self_tests.ta: core/arch/arm/pta/se_api_self_tests.c




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 183

socket: core/arch/arm/tee/pta_socket.c
invoke_tests.pta: core/arch/arm/pta/pta_invoke_test.c

tee_cryp_init部分：

该部分主要完成OP-TEE提供的密码学接口功
能的初始化操作，调用crypto_ops结构体中的init进
行初始化操作，该结构体变量定义在
core/lib/libtomcrypt/src/tee_ltc_provider.c文件中，变
量中定义了各种算法的操作函数指针。完成注册
后，TA就可以通过调用该变量中的对应函数指针
来实现OP-TEE中各种密码学算法接口的调用。
tee_se_manager_init部分：
该部分主要完成对SE模块的管理，为上层提供
对SE模块的操作接口。

2.service_init_late宏
service_init_late宏定义的内容将会在编译时被
链接到OP-TEE镜像文件的initcall2段中，OP-TEE中
使用该宏来定义OP-TEE中使用的密钥管理操作，
在core/tee/tee_fs_key_manager.c文件中，使用该宏
来将tee_fs_key_manager函数保存到initcall2段中，
在OP-TEE启动时被调用，用来生成或读取OP-TEE
在使用时会使用到的key，该函数内容如下：

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 184

static TEE_Result tee_fs_init_key_manager(void)
{
 int res = TEE_SUCCESS;
 struct tee_hw_unique_key huk;
 uint8_t chip_id[TEE_FS_KM_CHIP_ID_LENGTH];
 uint8_t message[sizeof(chip_id) + sizeof(string_for_ssk_gen)];
 /* 获取机器唯一的key作为salt值 */
 tee_otp_get_hw_unique_key(&huk);
 /* 获取chip ID值 */
 tee_otp_get_die_id(chip_id, sizeof(chip_id));
 /* 将unique key和chip id存放到message变量中 */
 memcpy(message, chip_id, sizeof(chip_id));
 memcpy(message + sizeof(chip_id), string_for_ssk_gen,
 sizeof(string_for_ssk_gen));
 /* 调用HMAC算法,以获取到的message作为参数传入来计算出一串字符串作为key存放到tee_fs_ssk变量中的key成员中 */
 res = do_hmac(tee_fs_ssk,key, sizeof(tee_fs_ssk.key),
 huk.data, sizeof(huk.data),
 message, sizeof(message));
 if (res == TEE_SUCCESS)
 tee_fs_ssk.is_init = 1;
 return res;
}



  这些key将会在使用安全存储功能时用到，         用
于生成加密、解密安全文件的FEK，
     其中
tee_otp_get_hw_unique_key函数可根据不同的平台
进行修改，只要保证读取到的值的唯一性且安全即
可，
  当前一般做法是读取一次性编程区域（One
Time Programmable，OTP）或efuse中的值，
     该值将
在芯片生产或者工厂整机生产时烧录到OTP中，
     当
然也有其他的实现方式。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 185

7.1.4 OP-TEE驱动的挂载

   安全设备在使用之前都需要执行一定的配置和
初始化，而该部分操作是在OP-TEE启动时执行
的。OP-TEE编译时通过使用driver_init宏和
driver_init_late宏来实现将安全设备驱动编译到OP-
TEE OS镜像文件中，使用这两个宏定义设备驱动
后，安全设备驱动的初始化操作将会被编译到OP-
TEE镜像文件的initcall3和initcall4段中，以Hikey为
例，其使用了driver_init宏来定义peripherals_init的
初始化操作，所以在使用hikey运行OP-TEE时会去
挂载外围安全设备并执行相关的初始化。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 186

7.2 ARM64位与ARM32位OP-TEE启动过
程的差异

    ARM32的OP-TEE与ARM64的OP-TEE启动过
程大致相同。ARM64的OP-TEE的_start函数定义在
generic_entry_a64.S文件中，而且该函数不像
ARM32位系统一样会进入reset中去执行OP-TEE启
动，而是直接在_start函数中就完成整个启动过程，
在进行初始化操作之前会注册一个异常向量表，该
异常向量表会在唤醒从核阶段被使用，当主核通知
唤醒从核时，从核会查找该异常向量表，然后命中
对应的处理函数并执行从核的启动操作。ARM64的
OP-TEE的启动过程与ARM32的OP-TEE的启动过程
几乎一样。ARM64位系统的_start函数内容说明如
下：

FUNC _start , :
    mov x19, x0       //保存paged_table的地址到x19中
    mov x20, x2       //保存device tree的地址到x20中
    adr x0, reset_vect_table  //获取异常向量表的地址
    msr vbar_el1, x0  //将异常向量表的地址写入VBAR寄存器中
    isb
    //设置系统控制寄存器,禁止cache等操作
mrs x0, sctlr_el1
    mov x1, #(SCTLR_I | SCTLR_A | SCTLR_SA)
    orr x0, x0, x1
    msr sctlr_el1, x0
    isb
//复制OP-TEE镜像中的init部分到内存中
copy_init:

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 187

ldp x3, x4, [x1], #16
stp x3, x4, [x0], #16
cmp x0, x2
b.lt  copy_init
msr daifclr, #DAIFBIT_ABT       //使能异常处理
adr x0, __text_start        //将__text_start的地址保存到x0中
adrp  x1, __end            //将_end的地址保存到x1中
add x1, x1, :lo12:__end
sub x1, x1, x0
bl     inv_dcache_range        //关闭数据cache
bl     console_init        //初始化console
bl     core_init_mmu_map        //初始化MMU的页表
bl     core_init_mmu_regs      //将MMU的页表信息写入TTBRx寄存器中
bl     cpu_mmu_enable      //使能MMU
bl     cpu_mmu_enable_icache    //使能MMU的指令cache
bl     cpu_mmu_enable_dcache    //使能MMU的数据cache
mov x0, x19            //将paged_table的地址保存到x0中
mov x1, #-1
mov x2, x20            //将device tree的地址保存到x2中
//使用device tree和paged_table作为参数开始OP-TEE的启动
bl     generic_boot_init_primary
mov x19, x0
adr x0, __text_start
add x1, x1, :lo12:__end
sub x1, x1, x0
bl     flush_dcache_range      //刷新数据cache
bl     thread_clr_boot_thread   //清空系统线程的状态
mov x1, x19
//将TEESMC_OPTEED_RETURN_ENTRY_DONE保存到x0
mov x0, #TEESMC_OPTEED_RETURN_ENTRY_DONE
smc #0   //调用SMC切换到normal world状态
b      . /* SMC不应该有返回操作 */
END_FUNC _start










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 188

7.3　小结

  本章介绍了OP-TEE的整个启动过程，包括
ARM32的OP-TEE与ARM64的OP-TEE启动过程之
间的差异。了解系统的启动过程，有助于理解OP-
TEE如何保证上层软件的安全，如何在系统级别添
加新的功能，以及安全驱动的挂载方式。关于OP-
TEE的MMU和内存管理的部分，将会在第14章详
细介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 189

第8章　OP-TEE在REE侧的上层软件

   OP-TEE在REE侧的上层软件包括libteec库和
tee_supplicant，libteec库提供CA程序运行时的基本
接口，tee_supplicant处理来自TEE侧的RPC请求。
libteec库和tee_supplicant属于REE侧用户空间的功
能，属于OP-TEE架构中的重要组成部分。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 190

8.1 OP-TEE的软件框架

    OP-TEE的软件分为REE侧部分和TEE侧部分，
分别包括CA、REE侧接口库（libteec）、常驻进程
（tee_supplicant）、OP-TEE驱动、OP-TEE OS、
TA等部分。使用OP-TEE来实现特定的安全功能需
要开发者根据实际需求开发特定的CA和TA程序并
集成到OP-TEE中。CA端负责在REE侧实现该新功
能在用户空间的对外接口，TA端的代码则是在OP-
TEE OS的用户空间负责实现具体的安全功能，例
如使用何种算法组合来对数据进行安全处理、对处
理后的数据的安全保存、解密加密数据等功能，如
图8-1所示为OP-TEE软件的整体框图。
    借助OP-TEE来实现特定安全需求时，一次完
整的功能调用一般是起源于CA，TA实现具体功能
并返回结果数据给CA。整个过程需要经过OP-TEE
的客户端接口、OP-TEE在Linux内核端的驱动、
Monitor模式/EL3下安全监控模式调用（smc）的处
理、OP-TEE OS的线程处理、OP-TEE中的TA程序
运行、OP-TEE端底层库或者硬件资源支持等几个
阶段。当TA执行完具体请求之后会按照原路径将
数据返回给CA。
                                            不同厂商对具体API的具体实现不一样，但是

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 191

其功能和对外接口都是遵循GP（Global Platform）
的规范来进行封装。例如笔者就发现海思和Mstar
在实现CA端的API的方案不相同，海思在添加TA
和CA时，在驱动层和TEE侧都会对调用TEE服务的
进程或者线程做权限检查，建立类似白名单机制，
在海思的TEE中添加TA和CA时必须注意将调用CA
端接口的进程注册到TEE中。
由于当前所有厂商的TEE方案都会遵循GP标
准，OP-TEE也遵循GP规范，本书中涉及的API的
实现以OP-TEE中的源代码为准。










图8-1 OP-TEE软件框架


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 192

8.2 REE侧libteec库提供的接口

                   CA使用libteec库中提供的接口来实现对TEE侧
TA中具体命令的调用。libteec库是OP-TEE提供给
用户在Linux用户空间使用的接口的实现，对于该
部分每家芯片厂商可能不一样，但对外的接口都遵
循GP规范中CA的接口进行定义。本章将以OP-TEE
的实现方法为例进行介绍。

    libteec库的所有源代码存放在
optee_client/libteec目录下，OP-TEE提供给Linux端
使用的接口源代码的实现存放在
optee_client/libteec/src/tee_client_api.c文件中。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 193

8.2.1 libteec库提供的接口说明

      libteec库提供给上层用户使用的API一共有10
个，都按照GP标准进行定义，使用这10个API能够
满足用户在Linux用户空间的需求，在系统中这部
分会被编译成libteec库，保存在REE侧的文件系统
中以备上层使用。上述10个函数的功能和实现说明
如下：

1.TEEC_InitializeContext

      函数原型：

TEEC_Result TEEC_InitializeContext(const char *name, TEEC_Context *ctx)

      函数作用描述：

      初始化一个TEEC_Context变量，该变量用于
CA和TEE之间建立联系。其中参数name用来定义
TEE的身份，如果该参数为NULL，则CA将会选择
默认的TEE方案来建立联系。该API必须是CA调用
的第一个libteec库的API，且该API不会触发TA的执
行。



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 194

    参数说明：

      name：指向TEE的名字，一般情况下该值设置
成NULL，使其选择默认的TEE方案进行连接。

    ctx：指向一个类型为TEEC_Context的变量的
    地址，
       该变量会用于CA与TA之间的连接和通信。

    函数返回值：

    TEEC_SUCCESS：
        初始化操作成功。

    其他返回值表示初始化失败。

    函数实现（在OP-TEE中的实现）如下：


    TEEC_Result TEEC_InitializeContext(const char *name, TEEC_Context *ctx)
    {
     char devname[PATH_MAX];
     int fd;
     size_t n;
     if (!ctx)
      return TEEC_ERROR_BAD_PARAMETERS;
     /* 调用teec_open_dev打开可用的TEE驱动文件,在打开的过程中会校验TEE的版本信息。如果检查合法,则会返回该驱动文件的句柄pd, 然后将fd赋值给ctx变量的fd成员 */
     for (n = 0; n < TEEC_MAX_DEV_SEQ; n++) {
      snprintf(devname, sizeof(devname), "/dev/tee%zu", n);
      fd = teec_open_dev(devname, name);
      if (fd >= 0) {
            ctx->fd = fd;
            return TEEC_SUCCESS;
      }
     }
     return TEEC_ERROR_ITEM_NOT_FOUND;
    }




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
            更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 195

2.TEEC_FinalizeContext

 函数原型：

void TEEC_FinalizeContext(TEEC_Context *ctx)

 函数作用描述：

 释放一个已经被初始化的类型为TEEC_Context
的变量，关闭CA与TEE之间的连接。在调用该函数
之前必须确保打开的session已经被关闭。

 参数说明：

 ctx：指向一个类型为TEEC_Context的变量，
该变量会用于CA与TA之间的连接和通信。

 函数返回值：

 无。

 函数实现（在OP-TEE中的实现）如下：

void TEEC_FinalizeContext(TEEC_Context *ctx)
{
 /* 调用close函数,释放掉tee驱动文件的描述符来完成资源释放 */


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 196

   if (ctx)
     close(ctx->fd);
  }

3.TEEC_OpenSession

   函数原型：

  TEEC_Result TEEC_OpenSession(TEEC_Context *ctx, TEEC_Session *session,const TEEC_UUID *destination,uint32_t connection_method, const
    void *connection_data,TEEC_Operation *operation, uint32_t *ret_origin)

   函数作用描述：

   打开一个CA与对应TA之间的一个session，该
session用于CA与对应TA之间的联系，CA需要连接
的TA是由UUID指定的。session具有不同的打开和
连接方式，根据不同的打开和连接方式CA可以在
执行打开session时传递数据给TA，以便TA对打开
操作进行权限检查。各种打开方式说明如下。

   TEEC_LOGIN_PUBLIC：不需要提供，即
connectionData的值必须为NULL。
   TEEC_LOGIN_USER：提示用户链接，
connectionData的值必须为NULL。

   TEEC_LOGIN_GROUP：CA以组的方式打开


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 197

session。connectionData的值必须指向一个类型为
uint32_t的数据，其包含某一组的特定信息。在TA
端将会对connectionData的数据进行检查，判定CA
是否真属于该组。

TEEC_LOGIN_APPLICATION：以application
的方式连接，connectionData的值必须为NULL。

TEEC_LOGIN_USER_APPLICATION：以用户
程序的方式连接，connectionData的值必须为
NULL。
TEEC_LOGIN_GROUP_APPLICATION：以组
应用程序的方式连接，其中connectionData需要指向
一个uint32_t类型的变量。在TA端将会对
connectionData的数据进行权限检查，查看连接是否
合法。

参数说明：

context：指向一个类型为TEEC_Context的变
量，该变量用于CA与TA之间的连接和通信，调用
TEEC_InitializeContext函数进行初始化；
session：存放session内存的变量；
destination：指向存放需要连接TA的UUID的值

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 198

的变量；

  connectionMethod：CA与TA的连接方式，详细
可参考函数描述中的说明；

  connectionData：指向需要在打开session时传递
给TA的数据；
  operation：指向TEEC_Operation结构体的变
量，变量中包含了一系列用于与TA进行交互使用
的buffer或者其他变量。如果在打开session时CA和
TA不需要交互数据，则可以将该变量指向NULL；
  returnOrigin：用于存放从TA端返回的结果的
变量。如果不需要返回值，则可以将该变量指向
NULL。

  函数返回值：

  TEEC_SUCCESS：初始化操作成功；
  其他返回值表示初始化失败。

  函数实现（在OP-TEE中的实现）如下：

 TEEC_Result TEEC_OpenSession(TEEC_Context *ctx, TEEC_Session *session,
      const TEEC_UUID *destination,
      uint32_t connection_method, const void *connection_data,

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 199

        TEEC_Operation *operation, uint32_t *ret_origin)
{
 /* 定义一个缓存,用于存放在执行open session需要传递给OP-TEE OS的数据和保存TA返回的数据 */
 uint64_t buf[(sizeof(struct tee_ioctl_open_session_arg) +
        TEEC_CONFIG_PAYLOAD_REF_COUNT *
          sizeof(struct tee_ioctl_param)) /
        sizeof(uint64_t)] = { 0 };
 /*定义buf_data,指向buf变量,用于将数据传递给OP-TEE驱动的ioctl函数来执行open session 操作*/
 struct tee_ioctl_buf_data buf_data;
 /* 定义参数,用于对初始化需要传递给TA的数据buffer */
 struct tee_ioctl_open_session_arg *arg;
 struct tee_ioctl_param *params;
 TEEC_Result res;
 uint32_t eorig;
 /* CA与TA之间的共享buffer */
 TEEC_SharedMemory shm[TEEC_CONFIG_PAYLOAD_REF_COUNT];
 int rc;
 (void)&connection_data;
 /* 参数检查 */
 if (!ctx || !session) {
  eorig = TEEC_ORIGIN_API;
  res = TEEC_ERROR_BAD_PARAMETERS;
  goto out;
 }
 /* 指针赋值 */
 buf_data.buf_ptr = (uintptr_t)buf;
 buf_data.buf_len = sizeof(buf);
 arg = (struct tee_ioctl_open_session_arg *)buf;
 arg->num_params = TEEC_CONFIG_PAYLOAD_REF_COUNT;
 params = (struct tee_ioctl_param *)(arg + 1);
 /* 将uuid的值填充到buffer中 */
 uuid_to_octets(arg->uuid, destination);
 arg->clnt_login = connection_method;
 /* 填充TEEC_Operation结构体变量 */
 res = teec_pre_process_operation(ctx, operation, params, shm);
 if (res != TEEC_SUCCESS) {
  eorig = TEEC_ORIGIN_API;
  goto out_free_temp_refs;
 }
 // 调用ioctl函数,执行TEE_IOC_OPEN_SESSION操作
 rc = ioctl(ctx->fd, TEE_IOC_OPEN_SESSION, &buf_data);
 if (rc) {
  EMSG("TEE_IOC_OPEN_SESSION failed");
  eorig = TEEC_ORIGIN_COMMS;
  res = ioctl_errno_to_res(errno);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 200

    goto out_free_temp_refs;
 }
 res = arg->ret;
 eorig = arg->ret_origin;
 if (res == TEEC_SUCCESS) {
    session->ctx = ctx;
    session->session_id = arg->session;
 }
 /* 解析出从TA中返回的数据 */
 teec_post_process_operation(operation, params, shm);
out_free_temp_refs:
 teec_free_temp_refs(operation, shm);
out:
 if (ret_origin)
    *ret_origin = eorig;
 return res;
}



4.TEEC_CloseSession

函数原型：



void TEEC_CloseSession(TEEC_Session *session)



函数作用描述：

关闭已经被初始化的CA与对应TA之间的
session，
    在调用该函数之前需要保证所有的
command已经执行完毕。如果session为NULL，则
不执行任何操作。

参数说明：





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 201

  session：指向已经初始化的session结构体变
量。

  函数返回值：

  无。

  函数实现（在OP-TEE中的实现）如下：


void TEEC_CloseSession(TEEC_Session *session)
{
 struct tee_ioctl_close_session_arg arg;
 if (!session)
  return;
 arg.session = session->session_id;
 /* 调用ioctl函数中的TEE_IOC_CLOSE_SESSION操作,通知TA执行close session */
 if (ioctl(session->ctx->fd, TEE_IOC_CLOSE_SESSION, &arg))
  EMSG("Failed to close session 0x%x", session->session_id);
}



5.TEEC_InvokeCommand

  函数原型：



TEEC_Result TEEC_InvokeCommand(TEEC_Session *session, uint32_t cmd_id, TEEC_Operation *operation, uint32_t *error_origin)



  函数作用描述：

  通过cmd_id和打开的session来通知session对应





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 202

的TA执行cmd_id指定的操作。

  参数说明：

  session：指向已经初始化的session结构体变
量；

  cmd_id：TA中定义的command的ID值，让CA
通知TA执行哪条command；
  operation：已经初始化的TEEC_Operation类型
的变量，该变量中包含CA与TA之间进行交互的
buffer、缓存的属性等信息；

  error_origin：调用TEEC_InvokeCommand函数
时，TA端的返回值。

  函数实现（在OP-TEE中的实现）如下：

TEEC_Result TEEC_InvokeCommand(TEEC_Session *session, uint32_t cmd_id,
  TEEC_Operation *operation, uint32_t *error_origin)
{
  /* 定义调用invokecommand函数时存放参数和共享内存的buffer */
  uint64_t buf[(sizeof(struct tee_ioctl_invoke_arg) +
  TEEC_CONFIG_PAYLOAD_REF_COUNT *
  sizeof(struct tee_ioctl_param)) /
  sizeof(uint64_t)] = { 0 };
  struct tee_ioctl_buf_data buf_data;
  struct tee_ioctl_invoke_arg *arg;
  struct tee_ioctl_param *params;
  TEEC_Result res;
  uint32_t eorig;

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 203

 TEEC_SharedMemory shm[TEEC_CONFIG_PAYLOAD_REF_COUNT];
 int rc;
 if (!session) {
    eorig = TEEC_ORIGIN_API;
    res = TEEC_ERROR_BAD_PARAMETERS;
    goto out;
 }
 /* 组合调用TA的command时需要使用的参数信息 */
 buf_data.buf_ptr = (uintptr_t)buf;
 buf_data.buf_len = sizeof(buf);
 arg = (struct tee_ioctl_invoke_arg *)buf;
 arg->num_params = TEEC_CONFIG_PAYLOAD_REF_COUNT;
 params = (struct tee_ioctl_param *)(arg + 1);
 arg->session = session->session_id;
 arg->func = cmd_id;
 if (operation) {
    teec_mutex_lock(&teec_mutex);
    operation->session = session;
    teec_mutex_unlock(&teec_mutex);
 }
 /* 填充operation中的params域,用于CA与TA之间的数据传输 */
 res = teec_pre_process_operation(session->ctx, operation, params, shm);
 if (res != TEEC_SUCCESS) {
    eorig = TEEC_ORIGIN_API;
    goto out_free_temp_refs;
 }
 /* 调用ioctl函数中的TEE_IOC_INVOKE操作 */
 rc = ioctl(session->ctx->fd, TEE_IOC_INVOKE, &buf_data);
 if (rc) {
    EMSG("TEE_IOC_INVOKE failed");
    eorig = TEEC_ORIGIN_COMMS;
    res = ioctl_errno_to_res(errno);
    goto out_free_temp_refs;
 }
 res = arg->ret;
 eorig = arg->ret_origin;
 /* 解析从TA中返回到params缓存中的数据 */
 teec_post_process_operation(operation, params, shm);
out_free_temp_refs:
 teec_free_temp_refs(operation, shm);
out:
 if (error_origin)
    *error_origin = eorig;
 return res;
}




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 204

6.TEEC_RequestCancellation

 函数原型：

void TEEC_RequestCancellation(TEEC_Operation *operation)

 函数作用描述：

 取消某个CA与TA之间的操作，该接口只能由
除执行TEEC_OpenSession和TEEC_InvokeCommand
的线程之外的其他线程进行调用，而TA端或者TEE
OS可以选择并不响应该请求。只有当operation中的
started域被设置成0之后，该操作方可有效。

 参数说明：

 operation：已经初始化的TEEC_Operation类型
的变量，该变量中包含CA与TA之间进行交互的
buffer、缓存的属性等信息。

 函数实现（在OP-TEE中的实现）如下：

void TEEC_RequestCancellation(TEEC_Operation *operation)
{
 struct tee_ioctl_cancel_arg arg;
 TEEC_Session *session;
 if (!operation)

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 205

 return;
 /* 获取session */
 teec_mutex_lock(&teec_mutex);
 session = operation->session;
 teec_mutex_unlock(&teec_mutex);
 if (!session)
 return;
 arg.session = session->session_id;
 arg.cancel_id = 0;
 /* 调用tee驱动中的ioctl执行TEE_IOC_CANCEL操作 */
 if (ioctl(session->ctx->fd, TEE_IOC_CANCEL, &arg))
 EMSG("TEE_IOC_CANCEL: %s", strerror(errno));
}



7.TEEC_RegisterShareMemory

函数原型：



TEEC_Result TEEC_RegisterSharedMemory(TEEC_Context *ctx, TEEC_SharedMemory *shm)



函数作用描述：

注册一块在CA端的内存作为CA与TA之间的共
享内存。shareMemory结构体中的三个成员如下：
buffer：指向作为共享内存的起始地址；
size：
 共享内存的大小；

flags：表示CA与TA之间的数据流方向。






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 206

参数说明：

ctx：指向一个类型为TEEC_Context的变量，
该变量必须已经被初始化；

shm：
    指向共享内存的结构体变量。

函数实现（在OP-TEE中的实现）如下：


TEEC_Result TEEC_RegisterSharedMemory(TEEC_Context *ctx, TEEC_SharedMemory *shm)
{
 int fd;
 size_t s;
 if (!ctx || !shm)
  return TEEC_ERROR_BAD_PARAMETERS;
 if (!shm->flags || (shm->flags & ~(TEEC_MEM_INPUT | TEEC_MEM_OUTPUT)))
  return TEEC_ERROR_BAD_PARAMETERS;
 s = shm->size;
 if (!s)
  s = 8;
 /* 调用ioctl函数,执行TEE_IOC_SHM_ALLOC操作 */
 fd = teec_shm_alloc(ctx->fd, s, &shm->id);
 if (fd < 0)
  return TEEC_ERROR_OUT_OF_MEMORY;
 /* 将注册到OP-TEE中的共享内存的对应fd映射到系统内存中,并存放到shm中的 shadow_buffer变量中 */
 shm->shadow_buffer = mmap(NULL, s, PROT_READ | PROT_WRITE, MAP_SHARED,
      fd, 0);
 close(fd);
 if (shm->shadow_buffer == (void *)MAP_FAILED) {
  shm->id = -1;
  return TEEC_ERROR_OUT_OF_MEMORY;
 }
 shm->alloced_size = s;
 shm->registered_fd = -1;
 return TEEC_SUCCESS;
}







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 207

8.TEEC_RegisterShareMemoryFileDescriptor

 函数原型：

TEEC_Result TEEC_RegisterSharedMemoryFileDescriptor(TEEC_Context *ctx, TEEC_SharedMemory *shm,int fd)

 函数作用描述：

 注册一个在CA与TA之间的共享文件，在CA端
会将文件的描述符fd传递给OP-TEE，其内容被存放
到shm中。

 参数说明：

 ctx：指向一个类型为TEEC_Context的变量，
该变量必须已经被初始化；

 shm：指向共享内存的结构体变量；

 fd：共享的文件的描述符号。
 函数实现（在OP-TEE中的实现）如下：

TEEC_Result TEEC_RegisterSharedMemoryFileDescriptor(TEEC_Context *ctx,
        TEEC_SharedMemory *shm,
        int fd)
{
 struct tee_ioctl_shm_register_fd_data data;


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 208

 int rfd;
 if (!ctx || !shm || fd < 0)
 return TEEC_ERROR_BAD_PARAMETERS;
 if (!shm->flags || (shm->flags & ~(TEEC_MEM_INPUT | TEEC_MEM_OUTPUT)))
 return TEEC_ERROR_BAD_PARAMETERS;
 /* 组合共享文件的结构体 */
 memset(&data, 0, sizeof(data));
 data.fd = fd;
 /* 调用ioctl函数由tee驱动来完成共享文件注册的其他操作 */
 rfd = ioctl(ctx->fd, TEE_IOC_SHM_REGISTER_FD, &data);
 if (rfd < 0)
 return TEEC_ERROR_BAD_PARAMETERS;
 /* 将返回值保存到shm变量中,以便后续使用 */
 shm->buffer = NULL;
 shm->shadow_buffer = NULL;
 shm->registered_fd = rfd;
 shm->id = data.id;
 shm->size = data.size;
 return TEEC_SUCCESS;
}



9.TEEC_AllocateSharedMemory

函数原型：



TEEC_Result TEEC_AllocateSharedMemory(TEEC_Context *ctx, TEEC_SharedMemory *shm)



函数作用描述：

分配一块共享内存，
         共享内存是由OP-TEE分
配的，
 OP-TEE分配了共享内存之后将会返回该内
存块的fd给CA，CA将fd映射到系统内存，
                   然后将
地址保存到shm中。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 209

参数说明：

ctx：指向一个类型为TEEC_Context的变量，
该变量必须已经被初始化；

shm：
    指向共享内存的结构体变量。

函数实现（在OP-TEE中的实现）如下：


TEEC_Result TEEC_AllocateSharedMemory(TEEC_Context *ctx, TEEC_SharedMemory *shm)
{
 int fd;
 size_t s;
 if (!ctx || !shm)
  return TEEC_ERROR_BAD_PARAMETERS;
 if (!shm->flags || (shm->flags & ~(TEEC_MEM_INPUT | TEEC_MEM_OUTPUT)))
  return TEEC_ERROR_BAD_PARAMETERS;
 s = shm->size;
 if (!s)
  s = 8;
 /* 通知OP-TEE进行共享内存的分配,返回fd */
 fd = teec_shm_alloc(ctx->fd, s, &shm->id);
 if (fd < 0)
  return TEEC_ERROR_OUT_OF_MEMORY;
 /* 将fd映射进系统内存,并将映射完成的地址存放到shm中 */
 shm->buffer = mmap(NULL, s, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
 close(fd);
 if (shm->buffer == (void *)MAP_FAILED) {
  shm->id = -1;
  return TEEC_ERROR_OUT_OF_MEMORY;
 }
 shm->shadow_buffer = NULL;
 shm->alloced_size = s;
 shm->registered_fd = -1;
 return TEEC_SUCCESS;
}







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 210

10.TEEC_ReleaseSharedMemory

函数原型：



void TEEC_ReleaseSharedMemory(TEEC_SharedMemory *shm)



函数作用描述：

释放已经被分配或者注册过的共享内存。

参数说明：

shm：
    指向共享内存的结构体变量。

函数实现（在OP-TEE中的实现）如下：


void TEEC_ReleaseSharedMemory(TEEC_SharedMemory *shm)
{
 if (!shm || shm->id == -1)
 return;
 /* 取消掉shm在系统内存中的地址映射 */
 if (shm->shadow_buffer)
 munmap(shm->shadow_buffer, shm->alloced_size);
 else if (shm->buffer)
 munmap(shm->buffer, shm->alloced_size);
 else if (shm->registered_fd >= 0)
 close(shm->registered_fd);
 /* 清空掉shm中的成员 */
 shm->id = -1;
 shm->shadow_buffer = NULL;
 shm->buffer = NULL;
 shm->registered_fd = -1;
}



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 211

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 212

8.2.2 CA调用libteec库中接口的流程

   CA在使用libteec库中的接口来实现调用TA的
操作时，一般过程是需要先建立context，然后建立
与需要调用的TA之间的session，再通过执行invoke
操作向TA发送command ID来实现具体的操作需
求，待TA中command ID的内容执行完成之后，如
果后续也不需要再次调用TA时，可以通过close
session和final context来释放资源，完全关闭该CA
与TA之间的联系。一次完整的操作过程如图8-2所
示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 213

图8-2 libteec库中接口调用过程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 214

8.3  REE侧的守护进程——tee_supplicant

tee_supplicant是常驻在Linux内核中的一个进
程，主要作用是使OP-TEE能够通过tee_supplicant来
访问REE侧的资源。例如加载存放在文件系统中的
TA镜像到TEE中，对REE侧数据库的操作，对
EMMC中RPMB分区的操作，提供socket通信等。
其源代码在optee_client/tee-supplicant目录中。编译
之后会生成一个名为tee_supplicant的可执行文件，
该可执行文件在REE启动时会作为一个后台守护程
序被自动启动。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 215

8.3.1 tee_supplicant编译生成和自启动

      tee_supplicant会在编译optee-client目标时被编
译生成一个可执行文件。tee_supplicant可执行文件
在Linux启动时会被作为后台程序启动。启动的动
作存放在build/init.d.optee文件中，其内容如下：


    #!/bin/sh
    #
    # /etc/init.d/optee
    #
    # Start/stop tee-supplicant (OP-TEE normal world daemon)
    #
    case "$1" in
    start)
    if [ -e /bin/tee-supplicant -a -e /dev/teepriv0 ]; then
                echo "Starting tee-supplicant..."
                tee-supplicant&  #将tee_supplicat以后台方式启动
                exit 0
          else
                echo "tee-supplicant or TEE device not found"
                exit 1
          fi
    ;;
      stop)
    killall tee-supplicant
          ;;
      status)
          cat /dev/teepriv0 2>&1 | grep -q "Device or resource busy" || not="not "
          echo "tee-supplicant is ${not}active"
          ;;
    Esac



    在编译时，
                init.d.optee文件将会被打包到根文




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
                更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 216

件系统中并以optee名字存放在/etc/init.d目录中，而
且会被链接到/etc/rc.d/S09_optee文件。这些操作是
在编译生成rootfs时进行的，详细情况可查看
build/common.mk文件中filelist-tee-common目标的内
容。系统启动tee_supplicant的过程如图8-3所示。









    图8-3 tee_supplicant启动过程










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 217

8.3.2 tee_supplicant入口函数

      tee_supplicant作为Linux中的一个守护进程，起
到处理RPC请求的服务器端的作用，
        通过类似于
C/S的方式，为OP-TEE提供对REE侧资源进行操作
的实现。该可执行文件的入口函数存放在
optee_client/tee-supplicant/src/tee_supplicant.c文件
中。其入口函数内容如下：



    int main(int argc, char *argv[])
    {
     struct thread_arg arg = { .fd = -1 };
     int e;
     /* 初始化互斥体 */
     e = pthread_mutex_init(&arg.mutex, NULL);
     if (e) {
      EMSG("pthread_mutex_init: %s", strerror(e));
     EMSG("terminating...");
     exit(EXIT_FAILURE);
     }
     /* 判定是否带有启动参数,如果带有启动参数,则打开对应的驱动文件,如果没有参数,则打开默认的驱动文件 */
     if (argc > 2)
      return usage();
     if (argc == 2) {
      arg.fd = open_dev(argv[1]);
      if (arg.fd < 0) {
           EMSG("failed to open \"%s\"", argv[1]);
           exit(EXIT_FAILURE);
      }
     } else {
      /*打开/dev/teepriv0设备,该设备为tee驱动设备文件,返回操作句柄*/
      arg.fd = get_dev_fd();
      if (arg.fd < 0) {
           EMSG("failed to find an OP-TEE supplicant device");
           exit(EXIT_FAILURE);




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
           更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 218

  }
 }
 if (tee_supp_fs_init() != 0) {
  EMSG("error tee_supp_fs_init");
  exit(EXIT_FAILURE);
 }
 if (sql_fs_init() != 0) {
  EMSG("sql_fs_init() failed ");
  exit(EXIT_FAILURE);
 }
 /* 调用process_one_request函数接收来自TEE的请求,并加以处理 */
 while (!arg.abort) {
  if (!process_one_request(&arg))
   arg.abort = true;
 }
 close(arg.fd);
 return EXIT_FAILURE;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 219

8.3.3 tee_supplicant存放RPC请求的结构体

      在tee_supplicant中用于接收和发送请求的数据
都存放在类型为tee_rpc_invoke的结构体变量中。该
结构体内容如下：



    union tee_rpc_invoke {
      uint64_t buf[(RPC_BUF_SIZE - 1) / sizeof(uint64_t) + 1];
      struct tee_iocl_supp_recv_arg recv;
      struct tee_iocl_supp_send_arg send;
    };



    RPC_BUF_SIZE的定义如下：


    #define RPC_BUF_SIZE (sizeof(struct tee_iocl_supp_send_arg) + \
      RPC_NUM_PARAMS * sizeof(struct tee_ioctl_param))



    tee_rpc_invoke结构体中的数据展开之后的组成
    如图8-4所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 220

图8-4 tee_rpc_invoke结构体格式










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 221

8.3.4 tee_supplicant中的无限循环

     tee_supplicant启动后最终会进入一个无限循
环，调用process_one_request函数来监控、接收、
处理、回复OP-TEE的请求。整个处理过程如图8-5
所示。










    图8-5 tee_supplicant处理RPC请求过程
                             process_one_request函数的内容和注释如下：

    static bool process_one_request(struct thread_arg *arg)
    {
    union tee_rpc_invoke request;
    size_t num_params;
    size_t num_meta;
    struct tee_ioctl_param *params;
    uint32_t func;
    uint32_t ret;


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 222

DMSG("looping");
memset(&request, 0, sizeof(request));
request.recv.num_params = RPC_NUM_PARAMS;
/* 组合tee_supplican等待TA请求的参数 */
params = (struct tee_ioctl_param *)(&request.send + 1);
params->attr = TEE_IOCTL_PARAM_ATTR_META;
/* 增加当前正在等待处理的tee_supplicant的数量 */
num_waiters_inc(arg);
/* 通过ioctl函数,将等待请求发送到tee驱动,在tee驱动中将会阻塞,直到有来自TA的请求才会返回 */
if (!read_request(arg->fd, &request))
return false;
/* 解析从TA发送的请求,分离出TA需要tee_supplicant执行的操作对应的ID和执行操作需要的参数 */
if (!find_params(&request, &func, &num_params, &ms, &num_meta))
return false;
/* 创建新的线程来等待接收来自TA的请求,将等待请求的数量减一 */
if (num_meta && !num_waiters_dec(arg) && !spawn_thread(arg))
return false;
/* 根据TA请求的ID来执行具体的handle */
switch (func) {
case RPC_CMD_LOAD_TA:
ret = load_ta(num_params, params);     //加载在文件系统的TA镜像
break;
case RPC_CMD_FS:
//处理操作文件系统的请求
ret = tee_supp_fs_process(num_params, params);
break;
case RPC_CMD_SQL_FS:
ret = sql_fs_process(num_params, params);      //处理操作数据库文件的请求
break;
case RPC_CMD_RPMB:
//处理对EMMC中rpmb分区的操作请求
ret = process_rpmb(num_params, params);
break;
case RPC_CMD_SHM_ALLOC:
//处理分配共享内存的请求
ret = process_alloc(arg->fd, num_params, params);
break;
case RPC_CMD_SHM_FREE:
ret = process_free(num_params, params);     //释放分配的共享内存的请求
break;
case RPC_CMD_GPROF:
ret = gprof_process(num_params, params);      //处理gprof请求
break;
case OPTEE_MSG_RPC_CMD_SOCKET:
ret = tee_socket_process(num_params, params);     //处理网络socket请求




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 223

  break;
  default:
  EMSG("Cmd [0x%" PRIx32 "] not supported", func);
  ret = TEEC_ERROR_NOT_SUPPORTED;
  break;
 }
 request.send.ret = ret;
 /* 回复处理后的数据给TA */
 return write_response(arg->fd, &request);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 224

8.3.5 tee_supplicant获取TA的RPC请求

      tee_supplicant通过read_request接收来自TA端的
请求。该函数会阻塞tee驱动层面，其内容如下：


    static bool read_request(int fd, union tee_rpc_invoke *request)
    {
     struct tee_ioctl_buf_data data;
     data.buf_ptr = (uintptr_t)request;
     data.buf_len = sizeof(*request);
     /* 将在tee_supplicant中设定的用于存放TA请求的buffer和属性的地址作为参数,然后调用ioctl函数进入到tee驱动中等待来自TA的请求 */
     if (ioctl(fd, TEE_IOC_SUPPL_RECV, &data)) {
      EMSG("TEE_IOC_SUPPL_RECV: %s", strerror(errno));
      return false;
     }
     return true;
    }



    在OP-TEE驱动中ioctl的
    TEE_IOC_SUPPL_RECV操作将会阻塞，直到接收
    到来自TA的请求。关于驱动部分将在后续章节详
    细介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 225

8.3.6 TA RPC请求的解析

      获取到来自TEE侧的RPC请求后，
tee_supplicant会调用find_params函数来解析该RPC
请求。该函数的内容和说明如下：



    static bool find_params(union tee_rpc_invoke *request, uint32_t *func,
       size_t *num_params, struct tee_ioctl_param **params,
       size_t *num_meta)
    {
     struct tee_ioctl_param *p;
     size_t n;
     p = (struct tee_ioctl_param *)(&request->recv + 1);
     /* 跳过属性为TEE_IOCTL_PARAM_ATTR_META的参数 */
     for (n = 0; n < request->recv.num_params; n++)
      if (!(p[n].attr & TEE_IOCTL_PARAM_ATTR_META))
       break;
     *func = request->recv.func; //记录TA请求的操作编号
     *num_params = request->recv.num_params - n; //确定TA真正的参数个数
     *params = p + n;   //将params指向TA发送过来的参数
     *num_meta = n;     //定位meta的起始位置
     /* 确保剩下的参数中没有属性为TEE_IOCTL_PARAM_ATTR_META的参数 */
     for (; n < request->recv.num_params; n++) {
      if (p[n].attr & TEE_IOCTL_PARAM_ATTR_META) {
       EMSG("Unexpected meta parameter");
       return false;
      }
     }
     return true;
    }










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 226

8.3.7 RPC请求的处理

      当解析完来自TA的RPC请求，获取到具体参数
后，在process_one_request函数中会根据请求的功
能ID来决定具体执行什么操作。这些操作包括：

      ·从文件系统中读取TA的镜像保存在共享内存
中；

      ·对文件系统中的节点进行读/写/打开/关闭/移
除等操作；

      ·执行RPMB（EMMC中的RPMB分区）相关操
作；

      ·分配共享内存；
      ·释放共享内存；
      ·处理gprof请求；

      ·执行网络socket请求。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 227

8.3.8　回复RPC请求

  当tee_supplicant解析出RPC请求的功能ID，并
根据该ID找到对应的处理函数，完成TEE请求操作
后，
  tee_supplicant通过调用write_response函数将处
理结果和数据返回给TA。该函数的内容和解释如
下：



static bool write_response(int fd, union tee_rpc_invoke *request)
{
 struct tee_ioctl_buf_data data;
 /* 将需要返回给TA的数据存放在buffer中 */
 data.buf_ptr = (uintptr_t)&request->send;
 data.buf_len = sizeof(struct tee_iocl_supp_send_arg) +
      sizeof(struct tee_ioctl_param) *
      request->send.num_params;
 /* 调用驱动中ioctl函数的TEE_IOC_SUPPL_SEND功能,将数据发送给TA */
 if (ioctl(fd, TEE_IOC_SUPPL_SEND, &data)) {
  EMSG("TEE_IOC_SUPPL_SEND: %s", strerror(errno));
  return false;
 }
 return true;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 228

8.4　各种RPC请求的处理

   tee_supplicant获取到远程过程调用（Remote
Procedure Call，RPC）请求后会解析出功能ID，然
后根据该ID值来命中tee_supplicant提供的具体操
作。当请求处理完成后会将处理结果和数据发送给
OP-TEE驱动，OP-TEE驱动最终会触发安全监控模
式调用（smc）将数据传递给OP-TEE。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 229

8.4.1　加载TA镜像

    请求加载TA镜像的功能ID为
RPC_CMD_LOAD_TA。执行该功能时，
tee_supplicant会到文件系统中将TA镜像的内容读取
到共享内存中。该操作是通过调用load_ta函数来实
现的，该函数定义在tee_supplicant.c文件中，在
REE侧加载TA镜像文件的整体流程如图8-6所示。






    图8-6 tee_supplicant处理加载TA的RPC请求过程
     load_ta函数的内容和注释说明如下：

    static uint32_t load_ta(size_t num_params, struct tee_ioctl_param *params)
    {
     int ta_found = 0;
     size_t size = 0;
     TEEC_UUID uuid;
     struct tee_ioctl_param_value *val_cmd;
     TEEC_SharedMemory shm_ta;
     memset(&shm_ta, 0, sizeof(shm_ta));
     /* 解析出需要加载的TA镜像的UUID以及配置将读取到的TA镜像的内容存放位置 */
     if (num_params != 2 || get_value(num_params, params, 0, &val_cmd) ||


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 230

      get_param(num_params, params, 1, &shm_ta))
      return TEEC_ERROR_BAD_PARAMETERS;
     /* 将UUID的值转换成TEEC_UUID格式 */
     uuid_from_octets(&uuid, (void *)val_cmd);
     /* 从ta_dir变量指定的目录中查找与UUID相符的TA镜像,并将其内容读取到共享内存中 */
     size = shm_ta.size;
     ta_found = TEECI_LoadSecureModule(ta_dir, &uuid, shm_ta.buffer, &size);
     if (ta_found != TA_BINARY_FOUND) {
      EMSG(" TA not found");
      return TEEC_ERROR_ITEM_NOT_FOUND;
     }
     /* 将读取到的TA镜像的大小填充到返回参数的size成员中 */
     params[1].u.memref.size = size;
     return TEEC_SUCCESS;
    }



      当load_ta执行完成并正确读取了TA镜像文件
的信息之后，最终会将读取到的数据通过调用
write_response函数，将数据发送给OP-TEE驱动，
由驱动来完成将数据发送给OP-TEE的操作。OP-
TEE会对接收到的TA镜像的合法性进行校验，主要
是验证TA镜像文件的电子签名是否合法。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 231

8.4.2　操作REE侧的文件系统

      当功能ID为RPC_CMD_FS时，tee_supplicant会
根据TA请求调用tee_supp_fs_process函数来完成对
文件系统的具体操作，包括常规的文件和目录的打
开、关闭、读取、写入、重命名、删除等。其内容
如下：



    TEEC_Result tee_supp_fs_process(size_t num_params,
      struct tee_ioctl_param *params)
    {
     /* 解析出params */
     if (num_params == 1 && tee_supp_param_is_memref(params)) {
      void *va = tee_supp_param_to_va(params);
      /* 如果num_params为1,且转换后va合法,则调用tee_supp_fs_process_primitive函数进行文件操作 */
      if (!va)
      return TEEC_ERROR_BAD_PARAMETERS;
      return tee_supp_fs_process_primitive(va, params->u.memref.size);
     }
     if (!num_params || !tee_supp_param_is_value(params))
      return TEEC_ERROR_BAD_PARAMETERS;
     /* 如果num_params参数不为1,则根据params中的value值来确定执行什么操作,并且根据params中的数据指定文件名 */
     switch (params->u.value.a) {
      case OPTEE_MRF_OPEN:
      return ree_fs_new_open(num_params, params);
      case OPTEE_MRF_CREATE:
      return ree_fs_new_create(num_params, params);
      case OPTEE_MRF_CLOSE:
             return ree_fs_new_close(num_params, params);
      case OPTEE_MRF_READ:
      return ree_fs_new_read(num_params, params);
      case OPTEE_MRF_WRITE:
             return ree_fs_new_write(num_params, params);
      case OPTEE_MRF_TRUNCATE:
      return ree_fs_new_truncate(num_params, params);
      case OPTEE_MRF_REMOVE:




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 232

     return ree_fs_new_remove(num_params, params);
     case OPTEE_MRF_RENAME:
     return ree_fs_new_rename(num_params, params);
     case OPTEE_MRF_OPENDIR:
     return ree_fs_new_opendir(num_params, params);
     case OPTEE_MRF_CLOSEDIR:
     return ree_fs_new_closedir(num_params, params);
     case OPTEE_MRF_READDIR:
     return ree_fs_new_readdir(num_params, params);
     default:
     return TEEC_ERROR_BAD_PARAMETERS;
    }
    }



      tee_supp_fs_process函数主要是对REE侧文件系
统进行操作。如果执行的是open、create操作则会
返回文件的操作句柄fd值给OP-TEE；如果是write
操作则会将需要写的内容写到具体的文件中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 233

8.4.3　操作RPMB

      当功能ID为RPC_CMD_RPMB时，
tee_supplicant会根据TA请求调用process_rpmb函数
来完成对EMMC中rmpb分区的操作。EMMC中的
RPMB分区，在读写过程中会执行验签和加解密的
操作。其内容如下：



    static uint32_t process_rpmb(size_t num_params, struct tee_ioctl_param *params)
     {
     TEEC_SharedMemory req;
     TEEC_SharedMemory rsp;
     /* 指定存放请求和返回数据的共享内存 */
     if (get_param(num_params, params, 0, &req) ||
      get_param(num_params, params, 1, &rsp))
      return TEEC_ERROR_BAD_PARAMETERS;
     /* 指定对rpmb分区的操作 */
     return rpmb_process_request(req.buffer, req.size, rsp.buffer, rsp.size);
    }










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 234

8.4.4　分配共享内存

当功能ID为RPC_CMD_SHM_ALLOC时，
tee_supplicant会根据TA请求调用process_alloc函数
来分配TA与tee_supplicant之间的共享内存。其内容
如下：



static uint32_t process_alloc(int fd, size_t num_params,
      struct tee_ioctl_param *params)
{
 struct tee_ioctl_shm_alloc_data data;
 struct tee_ioctl_param_value *val;
 struct tee_shm *shm;
 int shm_fd;
 memset(&data, 0, sizeof(data));
 /* 获取从TA发送到tee_supplicant的value */
 if (num_params != 1 || get_value(num_params, params, 0, &val))
  return TEEC_ERROR_BAD_PARAMETERS;
 /* 分配shm变量空间 */
 shm = calloc(1, sizeof(*shm));
 if (!shm)
  return TEEC_ERROR_OUT_OF_MEMORY;
 /* 调用tee驱动分配共享空间 */
 data.size = val->b;
 shm_fd = ioctl(fd, TEE_IOC_SHM_ALLOC, &data);
 if (shm_fd < 0) {
  free(shm);
  return TEEC_ERROR_OUT_OF_MEMORY;
 }
 /* 将分配好的共享内存的句柄映射到系统内存中 */
 shm->p = mmap(NULL, data.size, PROT_READ | PROT_WRITE, MAP_SHARED,
      shm_fd, 0);
 close(shm_fd);
 if (shm->p == (void *)MAP_FAILED) {
  free(shm);
  return TEEC_ERROR_OUT_OF_MEMORY;
 }



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 235

/* 记录分配好的共享内存数据 */
shm->id = data.id;
shm->size = data.size;
val->c = data.id;
/* 将分配的共享内存添加到共享内存链表中 */
push_tshm(shm);
return TEEC_SUCCESS;










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 236

8.4.5　释放共享内存

  当功能ID为RPC_CMD_SHM_FREE时，
tee_supplicant会根据TA请求调用process_free函数来
释放TA与tee_supplicant之间的共享内存。其内容如
下：



static uint32_t process_free(size_t num_params, struct tee_ioctl_param *params)
{
 struct tee_ioctl_param_value *val;
 struct tee_shm *shm;
 int id;
 /* 获取从TA传递到tee_supplicant的val数据 */
 if (num_params != 1 || get_value(num_params, params, 0, &val))
  return TEEC_ERROR_BAD_PARAMETERS;
 /* 获取需要被释放的共享内存的id值 */
 id = val->b;
 /* 从共享内存链表中删除指定的节点 */
 shm = pop_tshm(id);
 if (!shm)
  return TEEC_ERROR_BAD_PARAMETERS;
 /* 取消系统内存映射 */
 if (munmap(shm->p, shm->size) != 0) {
  EMSG("munmap(%p, %zu) failed - Error = %s",
      shm->p, shm->size, strerror(errno));
  free(shm);
  return TEEC_ERROR_BAD_PARAMETERS;
 }
 /* 执行free操作 */
 free(shm);
 return TEEC_SUCCESS;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 237

    8.4.6　记录程序执行效率

    当功能ID为RPC_CMD_GPROF时，
    tee_supplicant会根据TA请求调用gprof_process函数
    将某个特定的TA执行效率信息记录到文件系统
    中。其内容如下：



    TEEC_Result gprof_process(size_t num_params, struct tee_ioctl_param *params)
    {
     char vers[5] = "";
     char path[255];
     size_t bufsize;
     TEEC_UUID *u;
     int fd = -1;
     void *buf;
     int flags;
     int id;
     int st;
     int n;
     /* TA传递到tee_supplicant参数检查 */
     if (num_params != 3 ||
     (params[0].attr & TEE_IOCTL_PARAM_ATTR_TYPE_MASK) !=
     TEE_IOCTL_PARAM_ATTR_TYPE_VALUE_INOUT ||
     (params[1].attr & TEE_IOCTL_PARAM_ATTR_TYPE_MASK) !=
     TEE_IOCTL_PARAM_ATTR_TYPE_MEMREF_INPUT ||
     (params[2].attr & TEE_IOCTL_PARAM_ATTR_TYPE_MASK) !=
TEE_IOCTL_PARAM_ATTR_TYPE_MEMREF_INPUT)
         return TEEC_ERROR_BAD_PARAMETERS;
     /* 用于判定是否需要创建专门的文件记录执行效率信息 */
     id = params[0].u.value.a;
     if (params[1].u.memref.size != sizeof(TEEC_UUID))
         return TEEC_ERROR_BAD_PARAMETERS;
     /* 获取需要记录的TA的UUID值 */
     u = tee_supp_param_to_va(params + 1);
     if (!u)
         return TEEC_ERROR_BAD_PARAMETERS;
     /* 获取需要记录的信息 */



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 238

buf = tee_supp_param_to_va(params + 2);
if (!buf)
 return TEEC_ERROR_BAD_PARAMETERS;
bufsize = params[2].u.memref.size;
if (id < 0 || id > 100)
 return TEEC_ERROR_BAD_PARAMETERS;
flags = O_APPEND | O_WRONLY;
if (!id) {
 /* id == 0 means create file */
 flags |= O_CREAT | O_EXCL;
 id = 1;
}
/* 将buffer中的信息记录到/tmp/gmon-[uuid].out文件中 */
for (;;) {
 if (id > 1) {
  snprintf(vers, sizeof(vers), ".%d", id - 1);
 }
 n = snprintf(path, sizeof(path),
 "/tmp/gmon-"
 "%08x-%04x-%04x-%02x%02x%02x%02x%02x%02x%02x%02x"
 "%s.out",
 u->timeLow, u->timeMid, u->timeHiAndVersion,
 u->clockSeqAndNode[0], u->clockSeqAndNode[1],
 u->clockSeqAndNode[2], u->clockSeqAndNode[3],
 u->clockSeqAndNode[4], u->clockSeqAndNode[5],
 u->clockSeqAndNode[6], u->clockSeqAndNode[7],
 vers);
 if ((n < 0) || (n >= (int)sizeof(path)))
  break;
 fd = open(path, flags, 0600);
 if (fd >= 0) {
  do {
      st = write(fd, buf, bufsize);
  } while (st < 0 && errno == EINTR);
  close(fd);
  if (st < 0 || st != (int)bufsize)
      break;
  params[0].u.value.a = id;
  goto success;
 }
 if (errno != EEXIST)
  break;
 if (id++ == 100)
  break;
}




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 239

 return TEEC_ERROR_GENERIC;
 success:
 return TEEC_SUCCESS;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 240

8.4.7　网络套接字操作

当功能ID为
OPTEE_MSG_RPC_CMD_SOCKET时，
tee_supplicant会根据TA请求调用tee_socket_process
函数来完成网络套接字（socket）的相关操作，
    包
括网络套接字的建立、发送、接收和ioctl操作。其
内容如下：



TEEC_Result tee_socket_process(size_t num_params,
      struct tee_ioctl_param *params)
{
 if (!num_params || !tee_supp_param_is_value(params))
  return TEEC_ERROR_BAD_PARAMETERS;
 /* 根据value.a的值来判定执行什么操作,操作所需要的数据都从params中获取 */
 switch (params->u.value.a) {
  case OPTEE_MRC_SOCKET_OPEN:
  return tee_socket_open(num_params, params); //打开socket
  case OPTEE_MRC_SOCKET_CLOSE:
  return tee_socket_close(num_params, params); //关闭socket
  case OPTEE_MRC_SOCKET_CLOSE_ALL:
  return tee_socket_close_all(num_params, params); //关闭所有socket
  case OPTEE_MRC_SOCKET_SEND:
  return tee_socket_send(num_params, params); //通过socket发送数据
  case OPTEE_MRC_SOCKET_RECV:
  return tee_socket_recv(num_params, params); //通过socket接口数据
  case OPTEE_MRC_SOCKET_IOCTL:
  return tee_socket_ioctl(num_params, params); //socket的ioctl操作
  default:
  return TEEC_ERROR_BAD_PARAMETERS;
 }
}








https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 241

8.5　小结

  本章主要介绍了在REE侧libteec库及REE侧中
的常驻进程tee_supplicant的主要作用，用户可以使
用libteec库中的接口编写CA程序，通过对
tee_supplicant源代码的修改可以扩展TEE对REE侧
资源的特定操作和访问。libteec库中的接口遵循GP
规范的定义，有助于CA程序的通用性，使其兼容
不同的支持GP的TEE方案。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 242

第9章　REE侧OP-TEE的驱动

  OP-TEE驱动是REE侧与TEE侧之间进行交互的
重要通道，在REE侧的CA接口以及RPC请求的接收
和结果的返回最终都会被发送到驱动中，由驱动对
数据做进一步的处理。OP-TEE驱动通过解析传入
的参数，重新组合数据，将需要被传入到TEE侧的
数据载入到共享内存中，触发安全监控模式调用
（smc）进入到Monitor模式或EL3中将数据发送给
TEE。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 243

9.1 OP-TEE驱动模块的编译保存

      OP-TEE的驱动通过subsys_initcall和module_init
宏来告知系统在初始化阶段的什么时候去加载OP-
TEE驱动。subsys_initcall定义在linux/include/init.h
文件中，内容如下：



    #define __define_initcall(fn, id) \
    static initcall_t __initcall_##fn##id __used \
    __attribute__((__section__(".initcall" #id ".init"))) = fn;
    #define core_initcall(fn)            __define_initcall(fn, 1)
    #define core_initcall_sync(fn)       __define_initcall(fn, 1s)
    #define postcore_initcall(fn)        __define_initcall(fn, 2)
    #define postcore_initcall_sync(fn)   __define_initcall(fn, 2s)
    #define arch_initcall(fn)            __define_initcall(fn, 3)
    #define arch_initcall_sync(fn)       __define_initcall(fn, 3s)
    #define subsys_initcall(fn)          __define_initcall(fn, 4)
    #define subsys_initcall_sync(fn)     __define_initcall(fn, 4s)
    #define fs_initcall(fn)              __define_initcall(fn, 5)
    #define fs_initcall_sync(fn)         __define_initcall(fn, 5s)
    #define rootfs_initcall(fn)          __define_initcall(fn, rootfs)
    #define device_initcall(fn)          __define_initcall(fn, 6)
    #define device_initcall_sync(fn)     __define_initcall(fn, 6s)
    #define late_initcall(fn)            __define_initcall(fn, 7)
    #define late_initcall_sync(fn)       __define_initcall(fn, 7s)



      使用subsys_initcall宏定义的函数最终会被编译
到.initcall4.init段中，Linux系统在启动时会执行
initcallx.init段中的所有内容，而使用subsys_initcall
宏定义段的执行优先级为4。







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 244

   module_init的定义和相关扩展在
linux/include/linux/module.h文件和
linux/include/linux/init.h中，内容如下：

  #define device_initcall(fn) __define_initcall(fn, 6)
  #define __initcall(fn) device_initcall(fn)
  #define module_init(x) __initcall(x);

   由此可见，使用module_init宏构造的函数将会
在编译时被编译到initcall6.init段中，该段在Linux系
统启动过程中的优先等级为6。
   结合上述两点来看，在系统加载OP-TEE驱动
时，首先会执行OP-TEE驱动中使用subsys_init定义
的函数，然后再执行使用module_init定义的函数。
在OP-TEE驱动源代码中，使用subsys_init定义的函
数为tee_init，使用module_init定义的函数为
optee_driver_init。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 245

9.2 REE侧OP-TEE驱动的加载

    OP-TEE驱动是REE侧与TEE侧之间进行数据交
互的桥梁。tee_supplicant和libteec库中的接口最终
都会通过系统调用的方式陷入到Linux内核空间，
然后Linux内核根据传递的参数找到OP-TEE驱动，
并命中驱动的operation结构体中的具体处理函数来
完成实际的操作。对于OP-TEE驱动，一般会触发
安全监控模式调用（smc），并带参数进入到ARM
核的Monitor模式或EL3中，在Monitor模式或EL3中
执行正常世界状态（NWS）与安全世界状态
（SWS）之间的切换，待状态切换完成后，会将驱
动端带入的参数传递给OP-TEE中的线程进行进一
步的处理。OP-TEE驱动的源代码存放在
linux/drivers/tee目录中。
            OP-TEE驱动的加载过程分为两部分，第一部
分是创建class和分配设备号，第二部分是probe过
程。在正式介绍OP-TEE具体内容之前，首先需要
明白两个Linux内核中加载驱动的宏：
subsys_initcall和module_init。OP-TEE驱动的第一部
分是调用subsys_initcall宏来实现，而第二部分则是
调用module_init宏来实现。整个OP-TEE驱动的初始
化流程如图9-1所示。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 246

  OP-TEE驱动会创建两个设备，分别为/dev/tee0
和/dev/teepriv0，这两个设备分别被libteec库和
tee_supplicant使用，用于实现各自的功能，而驱动
与TEE侧之间的数据传递是通过共享内存的方式来
完成的，即在OP-TEE驱动挂载过程中会创建OP-
TEE与TEE之间的专用共享内存空间，在Linux的用
户空间需要发送到TEE的数据最终都会被保存在该
共享内存中，然后再切换ARM核的状态后，OP-
TEE从该共享内存中去获取数据。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 247

图9-1 OP-TEE驱动初始化流程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 248

9.2.1　设备号和class的初始化

tee_init函数定义在linux/drivers/tee/tee_core.c文
件中，
   主要完成class的创建和设备号的分配，
                                        其内
容如下：



static int __init tee_init(void)
{
 int rc;
 /* 分配OP-TEE驱动的class */
 tee_class = class_create(THIS_MODULE, "tee");
 if (IS_ERR(tee_class)) {
  pr_err("couldn't create class\n");
  return PTR_ERR(tee_class);
 }
 /* 分配OP-TEE的设备号 */
 rc = alloc_chrdev_region(&tee_devt, 0, TEE_NUM_DEVICES, "tee");
 if (rc) {
  pr_err("failed to allocate char dev region\n");
  class_destroy(tee_class);
  tee_class = NULL;
 }
 return rc;
}



分配好的设备号和class将会在驱动挂载过程中
执行probe操作时被使用。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 249

9.2.2 optee_driver_init函数

           Linux启动过程中会执行moudule_init宏定义的
函数，
    即在OP-TEE驱动的挂载过程中将会执行
optee_driver_init函数，
    该函数定义在
linux/drivers/tee/optee/core.c文件中，其内容如下：


static int __init optee_driver_init(void)
{
 struct device_node *fw_np;
 struct device_node *np;
 struct optee *optee;
 /* 从device tree中查找到firware的节点 */
 fw_np = of_find_node_by_name(NULL, "firmware");
 if (!fw_np)
    return -ENODEV;
 /* 匹配device tree中firmware节点下名称为linaro,optee-tz的节点 */
 np = of_find_matching_node(fw_np, optee_match);
 of_node_put(fw_np);
 if (!np)
    return -ENODEV;
 /* 使用查找到的节点执行OP-TEE驱动的probe操作 */
 optee = optee_probe(np);
 of_node_put(np);
 if (IS_ERR(optee))
 return PTR_ERR(optee);
 /* 保存初始化完成之后OP-TEE的设备信息到optee_svc中,以备在卸载时使用 */
 optee_svc = optee;
 return 0;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 250

9.2.3　挂载驱动的probe操作

      OP-TEE驱动在optee_driver_init函数中完成
probe操作。该函数首先会通过设备树找到OP-TEE
驱动的设备信息，然后将获取到的信息传递给
optee_probe函数执行probe操作。probe操作主要完
成版本的校验、获取OP-TEE驱动与TEE侧共享内存
的配置、建立共享内存的地址映射、添加安全监控
模式调用（smc）接口、分配/dev/tee0
和/dev/teepriv0设备、建立RPC请求队列等操作。
optee_probe函数内容如下：


    static struct optee *optee_probe(struct device_node *np)
    {
     optee_invoke_fn *invoke_fn;
     struct tee_shm_pool *pool;
     struct optee *optee = NULL;
     void *memremaped_shm = NULL;
     struct tee_device *teedev;
     u32 sec_caps;
     int rc;
     /* 获取在设备树中定义的OP-TEE驱动用于执行切换到monitor模式的接口 */
     invoke_fn = get_invoke_func(np);
     if (IS_ERR(invoke_fn))
      return (void *)invoke_fn;
     /* 调用到的secure world中,检查API版本信息是否匹配 */
     if (!optee_msg_api_uid_is_optee_api(invoke_fn)) {
      pr_warn("api uid mismatch\n");
      return ERR_PTR(-EINVAL);
     }
     /* 调用到secure world中,检查版本信息检查是否匹配 */
     if (!optee_msg_api_revision_is_compatible(invoke_fn)) {
      pr_warn("api revision mismatch\n");




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 251

 return ERR_PTR(-EINVAL);
}
/* 调用到secure world中,获取secure world是否预留了共享内存区域 */
if (!optee_msg_exchange_capabilities(invoke_fn, &sec_caps)) {
 pr_warn("capabilities mismatch\n");
 return ERR_PTR(-EINVAL);
}
/* 判定sercure world中是否预留了share memory,如果没有则报错 */
if (!(sec_caps & OPTEE_SMC_SEC_CAP_HAVE_RESERVED_SHM))
 return ERR_PTR(-EINVAL);
/* 配置secure world与驱动之间的共享内存,并进行地址映射,建立共享内存池 */
pool = optee_config_shm_memremap(invoke_fn, &memremaped_shm);
if (IS_ERR(pool))
 return (void *)pool;
/* 在kernel space内存空间中分配一块内存用于存放OP-TEE驱动的结构体变量 */
optee = kzalloc(sizeof(*optee), GFP_KERNEL);
if (!optee) {
 rc = -ENOMEM;
 goto err;
}
/* 将驱动中用于实现进入monitor模式的接口赋值到optee结构体中的invoke_fn成员中 */
optee->invoke_fn = invoke_fn;
/* 分配设备信息,填充被libteec使用的驱动文件信息到operation结构体变量中,并创建/dev/tee0文件,libteec将会使用该文件来使用op-tee驱动 */
teedev = tee_device_alloc(&optee_desc, NULL, pool, optee);
if (IS_ERR(teedev)) {
 rc = PTR_ERR(teedev);
 goto err;
}
optee->teedev = teedev;//libteec使用的驱动文件信息填充到optee中的teedev成员中
/* 分配设备信息,填充被tee_supplicant使用的驱动文件信息到operation结构体变量中,并创建/dev/teepriv0文件,tee_supplicant将会使用该文件来使用op-tee驱动 */
teedev = tee_device_alloc(&optee_supp_desc, NULL, pool, optee);
if (IS_ERR(teedev)) {
 rc = PTR_ERR(teedev);
 goto err;
}
//将tee_supplicant使用的驱动文件信息填充到optee中的supp_teedev成员中
optee->supp_teedev = teedev;
/* 将被libteec使用的设备信息注册到系统设备中 */
rc = tee_device_register(optee->teedev);
if (rc)
 goto err;
/* 将被tee_supplicant使用的设备信息注册到系统设备中 */
rc = tee_device_register(optee->supp_teedev);
if (rc)
 goto err;




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 252

 mutex_init(&optee->call_queue.mutex);
 INIT_LIST_HEAD(&optee->call_queue.waiters);
    /* 初始化RPC操作队列 */
 optee_wait_queue_init(&optee->wait_queue);
    /* 初始化被tee_supplicant用到的用于存放来自TA的请求的队列 */
 optee_supp_init(&optee->supp);
 /* 填充optee中的共享内存地址信息和共享内存池信息成员 */
 optee->memremaped_shm = memremaped_shm;
 optee->pool = pool;
 /* 使能共享内存的cache */
 optee_enable_shm_cache(optee);
 pr_info("initialized driver\n");
 return optee;
err:
 if (optee) {
    tee_device_unregister(optee->supp_teedev);
    tee_device_unregister(optee->teedev);
    kfree(optee);
 }
 if (pool)
    tee_shm_pool_free(pool);
 if (memremaped_shm)
    memunmap(memremaped_shm);
 return ERR_PTR(rc);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 253

9.2.4　获取切换到Monitor模式或EL3的接口

      正常世界状态与安全世界状态之间的切换是通
过在Monitor模式或EL3下设定SCR寄存器中的安全
状态位（NS bit）来实现的，OP-TEE驱动被上层调
用时，
        最终会通过触发安全监控模式调用（smc）
切换到Monitor模式或EL3，
        并通过共享内存的方式
将数据发送给安全世界状态来进行处理。而用户触
发安全监控模式调用的接口函数将在OP-TEE驱动
初始化时被填充到OP-TEE驱动的device info中，在
OP-TEE驱动中通过调用get_invoke_func函数来获取
该接口的指针。该函数的内容如下：



    static optee_invoke_fn *get_invoke_func(struct device_node *np)
    {
     const char *method;
     /* 获取op-tee驱动在device tree中的节点中的method属性的值 */
     if (of_property_read_string(np, "method", &method)) {
      pr_warn("missing \"method\" property\n");
      return ERR_PTR(-ENXIO);
     }
     /* 判定op-tee驱动是触发了SMC操作还是HVC操作。如果是SMC操作,则进入Monitor模式或EL3。如果是HVC操作,则进入ARM的Hypervisor */
     if (!strcmp("hvc", method))
      return optee_smccc_hvc;
     else if (!strcmp("smc", method))
      return optee_smccc_smc;
     pr_warn("invalid \"method\" property: %s\n", method);
     return ERR_PTR(-EINVAL);
    }








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 254

     执行安全监控模式调用指令会使ARM核进入
    EL3或Monitor模式。如果使用hvc，会是ARM核进
    入到EL2或者hyp模式，该模式主要用在使能虚拟机
    的系统上。这里以安全监控模式调用为例，实现系
    统状态切换的函数就是optee_smccc_smc，该函数内
    容如下：

    static void optee_smccc_smc(unsigned long a0, unsigned long a1,
         unsigned long a2, unsigned long a3,
         unsigned long a4, unsigned long a5,
         unsigned long a6, unsigned long a7,
         struct arm_smccc_res *res)
    {
     arm_smccc_smc(a0, a1, a2, a3, a4, a5, a6, a7, res);
    }

     即函数get_invoke_func执行完成之后会返回
    arm_smccc_smc函数的地址。arm_smccc_smc函数
    就是驱动用来将ARM核切换到Monitor模式或EL3的
    函数，该函数以汇编的方式编写，定义在
    linux/arch/arm/kernel/smccc-call.S文件中。如果是64
    位系统，则该函数定义在
    linux/arch/arm64/kernel/smccc-call.S目录中。本书以
    32位系统为例。该函数内容如下：

    /*SMCCC_SMC宏,触发smc*/
    .macro SMCCC_SMC
__SMC(0)
    .endm
    /*SMCCC_HVC宏,触发hvc用于ARM的虚拟化*/

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 255

.macro SMCCC_HVC
__HVC(0)
.endm
/* 定义SMCCC宏,其参数为instr */
.macro SMCCC instr
/* 将normal world中的寄存器入栈,保存现场 */
UNWIND(  .fnstart)
mov r12, sp
push       {r4-r7}
UNWIND(  .save  {r4-r7})
ldm      r12, {r4-r7}
\instr       /* 执行instr参数的内容,即执行smc切换 */
pop {r4-r7} /* 出栈操作,恢复现场 */
ldr r12, [sp, #(4 * 4)]
stm r12, {r0-r3}
bx       lr
UNWIND(  .fnend)
.endm
ENTRY(arm_smccc_smc)
SMCCC SMCCC_SMC
ENDPROC(arm_smccc_smc)










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 256

9.2.5　驱动版本和API版本校验

 OP-TEE驱动挂载过程中会校验驱动的版本以
及提供的API版本是否一致，该检查是通过触发快
速安全监控模式调用（fast smc）从OP-TEE中获取
到版本信息来实现的。快速安全监控模式调用与标
准安全监控模式调用（std smc）的不同之处就在于
第一个参数的BIT31的值不一样，这点将会在后续
章节中介绍。

                                           驱动加载过程中获取到REE侧与TEE侧之间进
行交互的接口函数（调用get_invoke_func函数返回
的函数地址）之后，OP-TEE驱动会对API的UID和
版本信息进行校验。上述操作是通过调用
optee_msg_api_uid_is_optee_api函数和
optee_msg_api_revision_is_compatible函数来实现
的。这两个函数的内容如下：

static bool optee_msg_api_uid_is_optee_api(optee_invoke_fn *invoke_fn)
{
 struct arm_smccc_res res;
 /* 调用执行smc操作的接口函数,带入的command ID为OPTEE_SMC_CALLS_UID */
 invoke_fn(OPTEE_SMC_CALLS_UID, 0, 0, 0, 0, 0, 0, 0, &res);
 /* 比较返回的UID的值与在驱动中定义的UID的值是否匹配 */
 if (res.a0 == OPTEE_MSG_UID_0 && res.a1 == OPTEE_MSG_UID_1 &&
 res.a2 == OPTEE_MSG_UID_2 && res.a3 == OPTEE_MSG_UID_3)
 return true;
 return false;
}

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 257

static bool optee_msg_api_revision_is_compatible(optee_invoke_fn *invoke_fn)
{
 union {
      struct arm_smccc_res smccc;
      struct optee_smc_calls_revision_result result;
} res;
/* 调用执行smc操作的接口函数,带入的command ID为OPTEE_SMC_CALLS_REVISION*/
invoke_fn(OPTEE_SMC_CALLS_REVISION, 0, 0, 0, 0, 0, 0, 0, &res.smccc);
/* 比较返回的版本信息的值与驱动中定义的版本值是否匹配 */
if (res.result.major == OPTEE_MSG_REVISION_MAJOR &&
 (int)res.result.minor >= OPTEE_MSG_REVISION_MINOR)
 return true;
return false;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 258

9.2.6　判定OP-TEE是否预留共享内存空间

      OP-TEE驱动与TEE之间需要进行数据的交
互，而进行数据交互则需要一定的共享内存来保存
OP-TEE和驱动之间共有的数据。所以在驱动初始
化时需要检查该共享内存空间是否被预留出来。通
过获取安全世界状态（SWS）中的相关变量的值并
判定该相关标识变量是否相等来判定安全世界状态
是否预留有共享内存空间。在OP-TEE OS启动过程
中，
      执行MMU初始化时会初始化该变量。在OP-
TEE驱动端通过调用
optee_msg_exchange_capabilities函数来获取该变量
的值，其内容如下：



    static bool optee_msg_exchange_capabilities(optee_invoke_fn *invoke_fn,
         u32 *sec_caps)
    {
     union {
     struct arm_smccc_res smccc;
     struct optee_smc_exchange_capabilities_result result;
     } res;
     u32 a1 = 0;
     if (!IS_ENABLED(CONFIG_SMP) || nr_cpu_ids == 1)
     a1 |= OPTEE_SMC_NSEC_CAP_UNIPROCESSOR;
    /* 调用smc操作接口,获取secure world中的变量 */
    invoke_fn(OPTEE_SMC_EXCHANGE_CAPABILITIES, a1, 0, 0, 0, 0, 0, 0,
     &res.smccc);
    if (res.result.status != OPTEE_SMC_RETURN_OK)
     return false;
    *sec_caps = res.result.capabilities; //将返回值中的变量赋值为sec_caps
    return true;
    }



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 259

  当驱动获取到sec_caps的值后会查看该值是否
为宏
OPTEE_SMC_SEC_CAP_HAVE_RESERVED_SHM
定义的值——BIT（0），如果该值不为——
BIT（0），则会报错，因为在安全世界状态都没有
预留共享内存空间，那OP-TEE驱动与安全世界状
态之间也就没法传输数据，所以有没有驱动也就没
有必要。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 260

    9.2.7　配置驱动与OP-TEE之间的共享内存

                               驱动与安全世界状态之间的数据交互是通过共
    享内存来完成的，在OP-TEE启动过程中会将作为
    共享内存的物理内存块预留出来，具体可查看OP-
    TEE启动代码中的core_init_mmu_map函数。OP-
    TEE驱动初始化阶段会将预留出来作为共享内存的
    物理内存配置成驱动的内存池，并通知OP-TEE OS
    执行相同的操作。配置完成后，安全世界状态就能
    从共享内存中获取到来自REE侧的数据。

OP-TEE驱动进行probe操作时，会调用到
    optee_config_shm_memremap函数来完成OP-TEE驱
    动和OP-TEE之间共享内存的配置。该函数定义在
    Linux/drivers/tee/optee/core.c文件中，其内容如下：

    static struct tee_shm_pool *optee_config_shm_memremap(optee_invoke_fn *invoke_fn, void **memremaped_shm)
    {
     union {
     struct arm_smccc_res smccc;
     struct optee_smc_get_shm_config_result result;
     } res;
     struct tee_shm_pool *pool;
     unsigned long vaddr;
     phys_addr_t paddr;
     size_t size;
     phys_addr_t begin;
     phys_addr_t end;
     void *va;
     struct tee_shm_pool_mem_info priv_info;


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 261

struct tee_shm_pool_mem_info dmabuf_info;
/* 调用smc类操作,通知OP-TEE OS返回被reserve出来的共享内存的物理地址和大小 */
invoke_fn(OPTEE_SMC_GET_SHM_CONFIG, 0, 0, 0, 0, 0, 0, 0, &res.smccc);
if (res.result.status != OPTEE_SMC_RETURN_OK) {
    pr_info("shm service not available\n");
    return ERR_PTR(-ENOENT);
}
/* 判定是否提供secure world中的cache */
if (res.result.settings != OPTEE_SMC_SHM_CACHED) {
    pr_err("only normal cached shared memory supported\n");
    return ERR_PTR(-EINVAL);
}
/* 将对齐操作之后的物理内存块的起始地址赋值给paddr,该块内存的大小赋值给size */
begin = roundup(res.result.start, PAGE_SIZE);
end = rounddown(res.result.start + res.result.size, PAGE_SIZE);
paddr = begin;
size = end - begin;
/* 判定作为共享内存的物理地址块的大小是否大于两个page大小,如果小于则报错,因为驱动配置用于dma操作和普通共享内存的大小分别为一个page大小*/
if (size < 2 * OPTEE_SHM_NUM_PRIV_PAGES * PAGE_SIZE) {
    pr_err("too small shared memory area\n");
    return ERR_PTR(-EINVAL);
}
// 将共享内存块的物理地址映射到系统内存中,得到映射完成的虚拟地址,存放在va变量中
va = memremap(paddr, size, MEMREMAP_WB);
if (!va) {
    pr_err("shared memory ioremap failed\n");
    return ERR_PTR(-EINVAL);
}
vaddr = (unsigned long)va;
/* 配置驱动私有内存空间的虚拟地址的启动地址、物理地址的起始地址以及大小、配置dma缓存的虚拟起始地址和物理地址以及大小。dmabuf与privbuf两个相邻,分别为一个page的大小 */
priv_info.vaddr = vaddr;
priv_info.paddr = paddr;
priv_info.size = OPTEE_SHM_NUM_PRIV_PAGES * PAGE_SIZE;
dmabuf_info.vaddr = vaddr + OPTEE_SHM_NUM_PRIV_PAGES * PAGE_SIZE;
dmabuf_info.paddr = paddr + OPTEE_SHM_NUM_PRIV_PAGES * PAGE_SIZE;
dmabuf_info.size = size - OPTEE_SHM_NUM_PRIV_PAGES * PAGE_SIZE;
/* 将驱动的私有buffer和dma buffer添加到内存池中,以便驱动在使用本身的alloc函数时能够从私有共享内存和dma buffer中分配内存来使用 */
pool = tee_shm_pool_alloc_res_mem(&priv_info, &dmabuf_info);
if (IS_ERR(pool)) {
    memunmap(va);
    goto out;
}
/* 将驱动与OP-TEE的共享内存赋值给memremaped_shm变量执行的地址 */
*memremaped_shm = va;
out:




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 262

return pool; //返回共享内存池的结构体
}



OP-TEE中预留出来的内存块作为驱动与OP-
TEE之间的共享内存使用。OP-TEE驱动会使用该块
内存来建立一个内存池，
                    以便驱动通过调用alloc函
数来完成共享内存的分配。共享内存池的建立是通
过调用tee_shm_pool_alloc_res_mem来实现的，其函
数内容如下：



struct tee_shm_pool *tee_shm_pool_alloc_res_mem(struct tee_shm_pool_mem_info
*priv_info, struct tee_shm_pool_mem_info *dmabuf_info)
{
 struct tee_shm_pool *pool = NULL;
 int ret;
 /* 从内核空间的memory中分配一块用于存放驱动内存池结构体变量的内存 */
 pool = kzalloc(sizeof(*pool), GFP_KERNEL);
 if (!pool) {
    ret = -ENOMEM;
    goto err;
 }
 /* 调用pool相关函数完成内存池的创建,设定alloc时的分配算法,并将私有共享内存的起始虚拟地址、起始物理地址以及大小信息保存到私有共享内存池中 */
 ret = pool_res_mem_mgr_init(&pool->private_mgr, priv_info,3);
 if (ret)
    goto err;
 /* 调用pool相关函数完成内存池的创建,设定alloc时的分配算法,并将dma共享内存的起始虚拟地址、起始物理地址以及大小信息保存到dma的共享内存池中 */
 ret = pool_res_mem_mgr_init(&pool->dma_buf_mgr, dmabuf_info, PAGE_SHIFT);
 if (ret)
    goto err;
 /* 设定销毁共享内存池的接口函数 */
 pool->destroy = pool_res_mem_destroy;
 return pool; //返回内存池结构体
err:
 if (ret == -ENOMEM)
 pr_err("%s: can't allocate memory for res_mem shared memory pool\n", __func__);
 if (pool && pool->private_mgr.private_data)
    gen_pool_destroy(pool->private_mgr.private_data);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 263

 kfree(pool);
 return ERR_PTR(ret);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 264

9.2.8　分配和设置tee0和teepriv0的设备信息结构体
变量

                                        在OP-TEE驱动进行probe操作时会分配和设置
两个tee_device结构体变量，分别用来表示被libteec
库和tee_supplicant使用的设备。分别通过执行
tee_device_alloc(&optee_desc，NULL，pool，    optee)
和tee_device_alloc(&optee_supp_desc，NULL，
pool，optee)来实现，主要是设置驱动被libteec库和
tee_supplicant使用时的设备具体操作和设备对应的
名称等信息。

                                         当libteec库调用文件操作函数执行打开、关闭
等操作/dev/tee0设备文件时，系统最终将调用到
optee_desc中具体的函数来实现对应操作。
                                     当tee_supplicant调用文件操作函数执行打开、
关闭等操作/dev/teepriv0设备文件时，系统最终将调
用到optee_supp_desc中具体的函数来实现对应操
作。

                                     上述配置操作都是通过调用tee_device_all函数
来实现的，该函数内容如下：

struct tee_device *tee_device_alloc(const struct tee_desc *teedesc,

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 265

struct device *dev, struct tee_shm_pool *pool, void *driver_data)
{
 struct tee_device *teedev;
 void *ret;
 int rc;
 int offs = 0;
 /* 参数检查 */
 if (!teedesc || !teedesc->name || !teedesc->ops ||
 !teedesc->ops->get_version || !teedesc->ops->open ||
 !teedesc->ops->release || !pool)
  return ERR_PTR(-EINVAL);
 /* 从内核空间中分配用于存放tee_device变量的内存 */
 teedev = kzalloc(sizeof(*teedev), GFP_KERNEL);
 if (!teedev) {
  ret = ERR_PTR(-ENOMEM);
  goto err;
 }
 /* 判定当前分配的设备结构体是提供给libteec还是tee_supplicant,如果该设备是分配给tee_supplicant,则将offs设置成16,offs将会在用于设置设备的id时被使用 */
 if (teedesc->flags & TEE_DESC_PRIVILEGED)
  offs = TEE_NUM_DEVICES / 2;
 /* 查找dev_mask中的从offs开始的第一个为0的bit位,然后将该值作为设备的id值 */
 spin_lock(&driver_lock);
 teedev->id = find_next_zero_bit(dev_mask, TEE_NUM_DEVICES, offs);
 if (teedev->id < TEE_NUM_DEVICES)
  set_bit(teedev->id, dev_mask);
 spin_unlock(&driver_lock);
 /* 判定设定的设备id是否超出最大数 */
 if (teedev->id >= TEE_NUM_DEVICES) {
  ret = ERR_PTR(-ENOMEM);
  goto err;
 }
 /* 组合出设备名,对于libteec来说,设备名为tee0。对于tee_supplicant来说,设备名为teepriv0 */
 snprintf(teedev->name, sizeof(teedev->name), "tee%s%d",
  teedesc->flags & TEE_DESC_PRIVILEGED ? "priv" : "",
  teedev->id - offs);
 /* 设定设备的class,tee_class在tee_init函数中被分配。设定执行设备release的操作函数和dev.parent */
 teedev->dev.class = tee_class;
 teedev->dev.release = tee_release_device;
 teedev->dev.parent = dev;
 /* 将设备的主设备号和设备ID组合后转化成dev_t类型 */
 teedev->dev.devt = MKDEV(MAJOR(tee_devt), teedev->id);
 /* 设置设备名,驱动被libteec使用时设备名为tee0,驱动被tee_supplicant使用时设备名为teepriv0 */
 rc = dev_set_name(&teedev->dev, "%s", teedev->name);
 if (rc) {
  ret = ERR_PTR(rc);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 266

    goto err_devt;
 }
 //设置驱动作为字符设备的操作函数接口,即指定该驱动在执行open、close、ioctl时的
 //函数接口
 cdev_init(&teedev->cdev, &tee_fops);
 teedev->cdev.owner = teedesc->owner;    //初始化字符设备的owner
 teedev->cdev.kobj.parent = &teedev->dev.kobj; //初始化kobj.parent成员
 /* 设置设备的私有数据 */
 dev_set_drvdata(&teedev->dev, driver_data);
 /* 初始化设备 */
 device_initialize(&teedev->dev);
 teedev->num_users = 1;  //标记该设备可以被使用
 init_completion(&teedev->c_no_users);
 mutex_init(&teedev->mutex);
 idr_init(&teedev->idr);
 /* 设定设备的desc成员,该成员包含设备最终执行具体操作的函数接口 */
 teedev->desc = teedesc;
 /* 设置设备的内存池,主要是驱动与secure world之间共享内存的私有共享内存和dma操作共享内存 */
 teedev->pool = pool;
 return teedev;
err_devt:
 unregister_chrdev_region(teedev->dev.devt, 1);
err:
 pr_err("could not register %s driver\n",
        teedesc->flags & TEE_DESC_PRIVILEGED ? "privileged" : "client");
 if (teedev && teedev->id < TEE_NUM_DEVICES) {
    spin_lock(&driver_lock);
    clear_bit(teedev->id, dev_mask);
    spin_unlock(&driver_lock);
 }
 kfree(teedev);
 return ret;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 267

9.2.9 tee0和teepriv0设备的注册

      完成版本的检查、OP-TEE与OP-TEE驱动之间
共享内存池配置、不同设备的配置之后，就需要将
这些配置好的设备注册到Linux系统中。对于被
libteec库和tee_supplicant使用的设备，分别通过调
用tee_device_register(optee->teedev)和
tee_device_register(optee->supp_teedev)来实现。其
中optee->teedev和optee->supp_teedev就是在上一章
中配置好的分别被libteec库和tee_supplicant使用的
设备结构体。调用tee_device_register函数来实现将
设备注册到系统的目的，该函数内容如下：



    int tee_device_register(struct tee_device *teedev)
    {
     int rc;
     /* 判定设备是否已经被注册过 */
     if (teedev->flags & TEE_DEVICE_FLAG_REGISTERED) {
      dev_err(&teedev->dev, "attempt to register twice\n");
      return -EINVAL;
     }
     /* 注册字符设备 */
     rc = cdev_add(&teedev->cdev, teedev->dev.devt, 1);
     if (rc) {
      dev_err(&teedev->dev,"unable to cdev_add() %s, major %d, minor %d, err=
    %d\n",teedev->name, MAJOR(teedev->dev.devt),
      MINOR(teedev->dev.devt), rc);
      return rc;
     }
     /* 将设备添加到Linux的设备模块中,在该步中将会在/dev目录下创建设备驱动文件节点,即对于被libteec使用的设备,在该步将创建/dev/tee0设备驱动文件。对于被tee_supplicant使用的设备,在该步将创建/dev/teepriv0设备文件 */
     rc = device_add(&teedev->dev);
     if (rc) {




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 268

  dev_err(&teedev->dev,
  "unable to device_add() %s, major %d, minor %d, err=%d\n",
  teedev->name, MAJOR(teedev->dev.devt),
  MINOR(teedev->dev.devt), rc);
  goto err_device_add;
 }
 /* 在/sys目录下创建设备的属性文件 */
 rc = sysfs_create_group(&teedev->dev.kobj, &tee_dev_group);
 if (rc) {
  dev_err(&teedev->dev,"failed to create sysfs attributes, err=%d\n", rc);
  goto err_sysfs_create_group;
 }
 /* 设定该设备已经被注册过 */
 teedev->flags |= TEE_DEVICE_FLAG_REGISTERED;
 return 0;
err_sysfs_create_group:
 device_del(&teedev->dev);
err_device_add:
 cdev_del(&teedev->cdev);
 return rc;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 269

9.2.10　请求队列的初始化

      OP-TEE驱动提供两个设备，分别是被libteec库
使用的/dev/tee0和被tee_supplicant使用
的/dev/teepriv0。为确保正常世界状态与安全世界状
态之间数据交互便利且能在正常世界状态进行异步
处理，
        OP-TEE驱动在挂载时会建立两个类似于消
息队列的队列，用于保存正常世界状态的请求数据
和安全世界状态的请求。optee_wait_queue_init用于
初始化/dev/tee0设备使用的队列，optee_supp_init用
于初始化/dev/teepriv0设备使用的队列。其代码分别
如下：



    void optee_wait_queue_init(struct optee_wait_queue *priv)
    {
     mutex_init(&priv->mu);
     INIT_LIST_HEAD(&priv->db);
    }
    void optee_supp_init(struct optee_supp *supp)
    {
     memset(supp, 0, sizeof(*supp));
     mutex_init(&supp->mutex);
     init_completion(&supp->reqs_c);
     idr_init(&supp->idr);
     INIT_LIST_HEAD(&supp->reqs);
     supp->req_id = -1;
    }










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 270

9.2.11　使能TEE中共享内存的缓存

  当一切执行完之后，
           最后就剩下通知OP-TEE
使能共享内存的缓存了，
           在OP-TEE驱动的挂载过
程中通过调用optee_enable_shm_cache函数来实现使
能共享内存Cache的操作。该函数内容如下：


void optee_enable_shm_cache(struct optee *optee)
{
 struct optee_call_waiter w;
 /* 确定secure world是否就绪*/
 optee_cq_wait_init(&optee->call_queue, &w);
 /* 进入loop循环,通知secure world执行相应操作,直到返回OK后跳出 */
 while (true) {
  struct arm_smccc_res res;
  /* 调用smc操作,通知secure world执行使能共享内存cache的操作 */
  optee->invoke_fn(OPTEE_SMC_ENABLE_SHM_CACHE, 0, 0, 0, 0, 0, 0,
  0, &res);
  if (res.a0 == OPTEE_SMC_RETURN_OK)
  break;
  optee_cq_wait_for_completion(&optee->call_queue, &w);
 }
 optee_cq_wait_final(&optee->call_queue, &w);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 271

9.2.12 OP-TEE驱动挂载的总结

  从OP-TEE驱动的挂载过程来看，OP-TEE驱动
会分别针对libteec库和tee_supplicant建立不同的设
备/dev/tee0和/dev/teepriv0。同时为两个设备中的des
配置各自独有的operation结构体变量，并建立类似
消息队列来存放正常世界状态与安全世界状态之间
的请求，这样libteec库和tee_supplicant使用OP-TEE
驱动时就能做到相对的独立。安全世界状态与OP-
TEE驱动之间使用共享内存进行数据交互。用于作
为共享内存的物理内存块在OP-TEE启动过程中进
行MMU初始化时需要被预留出来，在OP-TEE驱动
的挂载过程中需要将该内存块映射到系统内存中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 272

9.3 REE侧用户空间对驱动的调用过程

  在Linux用户空间对文件系统中的文件执行打
开、关闭、读写以及ioctl操作时，最终都会穿透到
Linux内核空间执行具体的操作。而从用户空间陷
入到内核空间是通过系统调用（systemcall）来实现
的（关于syscall的实现可自行查阅资料了解），进
入Linux内核空间后，系统会调用相应的驱动来获
取设备对应的file_operations变量，该结构体变量中
存放了对文件进行各种操作的具体函数指针。所以
从用户空间对文件进行操作时，其整个过程大致如
图9-2所示。
  调用libteec库中按照GP标准定义的API或
tee_supplicant执行具体操作时都会经历图9-2所示的
流程，所以在后续章节中该流程将不再反复赘述。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 273

图9-2 REE侧用户空间调用OP-TEE驱动的大致流
    程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 274

9.4 OP-TEE驱动中重要的结构体变量

  要了解OP-TEE驱动中具体进行了哪些操作，
首先需要了解在OP-TEE驱动中存在的四个重要的
结构体，libteec库和tee_supplicanty以及直接存储器
存储（Direct Memory Access，DMA）操作使用驱
动时会使用到这四个结构体，这四个结构体变量会
在驱动挂载时被注册到系统设备模块或该设备的自
由结构体中，以便被用户空间使用，而执行dma操
作时则会对共享内存进行注册。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 275

9.4.1 OP-TEE驱动的file_operation结构体变量
tee_fops

    OP-TEE驱动的file_operation结构体变量定义在
linux/drivers/tee/tee_core.c文件中。该变量中包含了
OP-TEE驱动文件的操作函数指针，其内容如下：


static const struct file_operations tee_fops = {
   .owner = THIS_MODULE, //驱动属于者
   .open = tee_open, //驱动文件open操作的具体实现的函数指针
   .release = tee_release, //驱动文件release操作的具体实现的函数指针
   .unlocked_ioctl = tee_ioctl, //驱动文件ioctl操作的具体实现的函数指针
   //驱动文件ioctl操作的具体实现的函数指针,用户空间为32位,而内核为64位时使用
   .compat_ioctl = tee_ioctl,
};


    当在用户空间调用open、release、ioctl函数操
作驱动文件时，就会调用到该结构体中的对应函数
去执行具体操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 276

9.4.2 tee0设备的tee_driver_ops结构体变量
optee_ops

    当用户空间调用libteec库中的接口时，操作的
是OP-TEE驱动的/dev/tee0设备，而optee_ops变量中
存放的就是针对/dev/tee0设备的具体操作函数的指
针。用户调用libteec库接口时，首先会调用到
tee_fops中的成员函数，tee_fops中的成员函数再去
调用optee_ops中对应的成员函数来完成对/dev/tee0
设备的实际操作。

    optee_ops变量定义在
linux/drivers/tee/optee/core.c文件中，其内容如下：

static struct tee_driver_ops optee_ops = {
      .get_version = optee_get_version,    //获取OP-TEE版本信息的接口函数
      //打开/dev/tee0设备的具体实现,初始化列表和互斥体,返回context
      .open = optee_open,
      //释放打开的/dev/tee0设备资源,并通知secure world关闭session
      .release = optee_release,
      .open_session = optee_open_session, //打开session,以便CA与TA进行交互
      //关闭已经打开的session,断开CA与TA之间的交互
      .close_session = optee_close_session,
      .invoke_func = optee_invoke_func,    //通过smc操作发送CA请求到对应TA
      .cancel_req = optee_cancel_req, //取消CA端已经发送的smc请求
};






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 277

9.4.3 teepriv0设备的操作结构体变量
optee_supp_ops

                      当tee_supplicant需要执行相关操作时，操作的
就是OP-TEE驱动的/dev/teepriv0设备，
optee_supp_ops变量中存放的就是针对/dev/teepriv0
设备的具体操作函数的指针。当tee_supplicant执行
相关操作时，首先会调用到tee_fops中的成员函
数，tee_fops中的成员函数会去调用optee_supp_ops
中对应的成员函数来完成对/dev/teepriv0设备的实际
操作。

    optee_supp_ops变量定义在
linux/drivers/tee/optee/core.c文件中，其内容如下：

static struct tee_driver_ops optee_supp_ops = {
      .get_version = optee_get_version, //获取OP-TEE的版本信息
      .open = optee_open, //打开/dev/teepriv0设备的具体实现
      //释放掉打开的/dev/teepriv0设备,并通知secure world关闭session
      .release = optee_release,
      .supp_recv = optee_supp_recv, //接收从OP-TEE发送给tee_supplicant的请求
      //执行完OP-TEE请求的操作后将结果和数据发送给OP-TEE
      .supp_send = optee_supp_send,
};






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 278

9.4.4　共享驱动缓存操作变量tee_shm_dma_buf_ops

    OP-TEE驱动也支持其他设备访问OP-TEE驱动
的共享缓存。该变量定义在
linux/drivers/tee/tee_shm.c文件中，当需要分配dma
缓存时就会调用该变量中对应的函数。其内容如
下：


    static struct dma_buf_ops tee_shm_dma_buf_ops = {
      .map_dma_buf = tee_shm_op_map_dma_buf, //暂未实现
      .unmap_dma_buf = tee_shm_op_unmap_dma_buf, //暂未实现
      .release = tee_shm_op_release, //释放掉指定的共享内存
      .kmap_atomic = tee_shm_op_kmap_atomic, //暂未实现
      .kmap = tee_shm_op_kmap, //暂未实现
      .mmap = tee_shm_op_mmap, //dma共享内存进行地址映射
    };










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 279

9.5 OP-TEE驱动与OP-TEE之间共享内存
的注册和分配

      当libteec库和tee_supplicant需要分配或注册与
安全世界状态之间的共享内存时，
        可通过调用OP-
TEE驱动的ioctl方法来实现，ioctl函数将调用
tee_ioctl_shm_alloc函数来实现具体的共享内存的分
配、注册共享内存的操作。该函数的内容如下：



    static int tee_ioctl_shm_alloc(struct tee_context *ctx,
         struct tee_ioctl_shm_alloc_data __user *udata)
    {
     long ret;
     struct tee_ioctl_shm_alloc_data data;
     struct tee_shm *shm;
     /* 将userspace传递的参数数据复制到kernel的buffer中 */
     if (copy_from_user(&data, udata, sizeof(data)))
        return -EFAULT;
     if (data.flags)
        return -EINVAL;
     /* 将共享内存的ID值设置成-1,以便分配好共享内存之后重新赋值 */
     data.id = -1;
     /* 调用tee_shm_all函数,从驱动与secure world之间的共享内存池中分配对应大小的内存,并设定对应的ID值 */
     shm = tee_shm_alloc(ctx, data.size, TEE_SHM_MAPPED | TEE_SHM_DMA_BUF);
     if (IS_ERR(shm))
         return PTR_ERR(shm);
     /* 设定需要返回给userspace的数据 */
     data.id = shm->id;
     data.flags = shm->flags;
     data.size = shm->size;
     /* 将需要返回的数据从Linux内核空间复制到用户空间 */
     if (copy_to_user(udata, &data, sizeof(data)))
         ret = -EFAULT;
     else
         ret = tee_shm_get_fd(shm);




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 280

   tee_shm_put(shm); //如果分配的是DMA的buffer,则要减少count值
   return ret;
 }

  从整个过程来看，如果在libteec库执行共享内
存的分配或注册操作时，驱动都会从OP-TEE驱动
与安全世界状态的共享内存池中分配一块内存，将
该分配好的内存的id值返回给libteec。在libteec库
中，如果是调用TEEC_AllocateSharedMemory函
数，则会对该共享内存的id值进行mmap操作，并将
所得的值赋给shm中的buffer成员。如果调用的是
TEEC_RegisterSharedMemory，则会将共享内存id
执行mmap操作后得到的值赋给shm中的
shadow_buffer成员。

  由此可见，libteec库中执行注册共享内存操作
时，并不是将用户空间的内存直接共享给安全世界
状态，而是将用户空间的内存与驱动中分配的一块
共享内存进行shadow操作，使两者实现一个类似映
射的关系。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 281

9.6 libteec库中的接口在驱动中的实现

  驱动挂载完成后，CA程序通过调用libteec库中
的接口调用OP-TEE驱动来穿透到OP-TEE中，然后
调用对应的TA程序。OP-TEE驱动在挂载完成后会
在/dev目录下分别创建两个设备节点，分别
为/dev/tee0和/dev/teepriv，对/dev/tee0设备进行相关
操作就能够穿透到OP-TEE中实现特定请求的发
送。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 282

9.6.1 libteec库中的open操作

      在libteec库中调用open函数打开/dev/tee0设备
时，
      最终会调用到tee_fops中的open成员指定的函
数指针——tee_open，
      该函数的内容如下：



static int tee_open(struct inode *inode, struct file *filp)
{
 struct tee_context *ctx;
 /* 调用container_of函数,获取设备的tee_device变量的内容。该变量对于/dev/tee0和/dev/teepriv0设备是不一样的,这点可以在驱动过载的过程中查阅*/
 ctx = teedev_open(container_of(inode->i_cdev, struct tee_device, cdev));
 if (IS_ERR(ctx))
    return PTR_ERR(ctx);
 filp->private_data = ctx;
 return 0;
}
static struct tee_context *teedev_open(struct tee_device *teedev)
{
 int rc;
 struct tee_context *ctx;
 /* 标记该设备的使用者加一 */
 if (!tee_device_get(teedev))
    return ERR_PTR(-EINVAL);
 /* 分配tee_context结构体变量空间 */
 ctx = kzalloc(sizeof(*ctx), GFP_KERNEL);
 if (!ctx) {
    rc = -ENOMEM;
    goto err;
 }
 /* 将tee_context结构体中的teedev变量赋值 */
 ctx->teedev = teedev;
 INIT_LIST_HEAD(&ctx->list_shm);
 /*调用设备des中的open执行设备级别的open操作*/
 rc = teedev->desc->ops->open(ctx);
 if (rc)
    goto err;
 return ctx;
err:



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 283

 kfree(ctx);
 tee_device_put(teedev);
 return ERR_PTR(rc);
}



对于设备级别（/dev/tee0和/dev/teepriv0），
 最
终会调用到optee_open函数，
 该函数内容如下：



static int optee_open(struct tee_context *ctx)
{
 struct optee_context_data *ctxdata;
 struct tee_device *teedev = ctx->teedev;
 struct optee *optee = tee_get_drvdata(teedev);
 /* 分配optee_context_data 结构体变量空间 */
 ctxdata = kzalloc(sizeof(*ctxdata), GFP_KERNEL);
 if (!ctxdata)
  return -ENOMEM;
 /* 通过teedev的值是否为 optee->supp_teedev来判定当前的open操作是打开/dev/tee0设备还是/dev/teepriv0设备,如果相等,则表示当前是打开/dev/teepriv0设备 */
 if (teedev == optee->supp_teedev) {
  bool busy = true; //标记/dev/teepriv0正在使用
  mutex_lock(&optee->supp.mutex);
  if (!optee->supp.ctx) {
   busy = false;
   optee->supp.ctx = ctx;
  }
  mutex_unlock(&optee->supp.mutex);
  if (busy) {
   kfree(ctxdata);
   return -EBUSY;
  }
 }
 /* 初始化互斥体和队列 */
 mutex_init(&ctxdata->mutex);
 INIT_LIST_HEAD(&ctxdata->sess_list);
 /* 赋值 */
 ctx->data = ctxdata;
 return 0;
}







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 284

9.6.2 libteec库中的release操作

      当libteec库和tee_supplicant打开了对应的设备
后，如果需要释放打开的设备，则可调用该设备的
release操作来实现，在用户空间调用该操作后，最
终会调用到OP-TEE驱动的release成员变量——
tee_release。该函数内容如下：


    static int tee_release(struct inode *inode, struct file *filp)
    {
     teedev_close_context(filp->private_data);
     return 0;
    }
    static void teedev_close_context(struct tee_context *ctx)
    {
     struct tee_shm *shm;
     /* 调用/dev/tee0或/dev/teepriv0设备的release操作函数 */
     ctx->teedev->desc->ops->release(ctx);
     mutex_lock(&ctx->teedev->mutex);
     /* 清空设备分配的共享内存,并将其指针指向NULL */
     list_for_each_entry(shm, &ctx->list_shm, link)
     shm->ctx = NULL;
     mutex_unlock(&ctx->teedev->mutex);
     //设备使用者数量减一。如果已经没有使用者,则将desc指向NULL
     tee_device_put(ctx->teedev);
     kfree(ctx);
    }


    ctx->teedev->desc->ops->release(ctx)；将会执行
    optee_release函数，其内容如下：







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 285

static void optee_release(struct tee_context *ctx)
{
 struct optee_context_data *ctxdata = ctx->data;
 struct tee_device *teedev = ctx->teedev;
 struct optee *optee = tee_get_drvdata(teedev);
 struct tee_shm *shm;
 struct optee_msg_arg *arg = NULL;
 phys_addr_t parg;
 struct optee_session *sess;
 struct optee_session *sess_tmp;
 if (!ctxdata)
  return;
 /* 分配驱动与secure world之间的共享内存 */
 shm = tee_shm_alloc(ctx, sizeof(struct optee_msg_arg), TEE_SHM_MAPPED);
 if (!IS_ERR(shm)) {
  arg = tee_shm_get_va(shm, 0); //获取共享内存的虚拟地址
  if (!IS_ERR(arg))
  //解析共享内存的虚拟地址得到物理地址,存放在parg中
  tee_shm_va2pa(shm, arg, &parg);
 }
 /*遍历存放使用该设备的所有session通知OP-TEE执行关闭session操作*/
 list_for_each_entry_safe(sess, sess_tmp, &ctxdata->sess_list,
       list_node) {
  list_del(&sess->list_node);
  if (!IS_ERR_OR_NULL(arg)) {
   memset(arg, 0, sizeof(*arg));
   arg->cmd = OPTEE_MSG_CMD_CLOSE_SESSION;
   arg->session = sess->session_id;
   optee_do_call_with_arg(ctx, parg);
  }
  kfree(sess);
 }
 kfree(ctxdata);
 /* 释放共享内存 */
 if (!IS_ERR(shm))
  tee_shm_free(shm);
 ctx->data = NULL;
 /* 如果是对/dev/teepriv0设备进行release操作,则指向optee_supp_release操作,释放该设备在使用时建立的各种队列 */
 if (teedev == optee->supp_teedev)
  optee_supp_release(&optee->supp);
}









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 286

9.6.3 libteec执行get_version操作

    在libteec库中获取OP-TEE的版本信息，会调
用/dev/tee0的TEE_IOC_VERSION类型的ioctl操
作，
    该操作最终会调用到tee_ioctl_version函数来完
成获取OP-TEE版本信息的操作，    该函数的内容和
注释如下：



static int tee_ioctl_version(struct tee_context *ctx,
 struct tee_ioctl_version_data __user *uvers)
{
 struct tee_ioctl_version_data vers;
 /* 调用设备的get_version操作 */
 ctx->teedev->desc->ops->get_version(ctx->teedev, &vers);
 /* 判定该操作是来自于tee_supplicant还是libteec */
 if (ctx->teedev->desc->flags & TEE_DESC_PRIVILEGED)
 vers.gen_caps |= TEE_GEN_CAP_PRIVILEGED;
 /* 将获取到的版本信息数据复制到userspace层面提供的buffer中 */
 if (copy_to_user(uvers, &vers, sizeof(vers)))
 return -EFAULT;
 return 0;
}



    设备的get_version函数内容如下：


static void optee_get_version(struct tee_device *teedev,
 struct tee_ioctl_version_data *vers)
{
 struct tee_ioctl_version_data v = {
 .impl_id = TEE_IMPL_ID_OPTEE,
 .impl_caps = TEE_OPTEE_CAP_TZ,
 .gen_caps = TEE_GEN_CAP_GP,




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 287

 };
 *vers = v;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 288

9.6.4 libteec库中的open session操作

   当用户调用libteec库中的TEEC_OpenSession接
口时会执行OP-TEE驱动中ioctl函数的
TEE_IOC_OPEN_SESSION分支去执行
tee_ioctl_open_session函数，该函数只会在打
开/dev/tee0设备后才能被使用。整个open session的
操作流程如图9-3所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 289

   图9-3 REE侧open session操作的执行流程
   调用过程中使用optee_do_call_with_arg函数来
完成驱动与OP-TEE之间的交互。该函数的内容和
说明如下：



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 290

u32 optee_do_call_with_arg(struct tee_context *ctx, phys_addr_t parg)
{
 struct optee *optee = tee_get_drvdata(ctx->teedev);
 struct optee_call_waiter w;
 struct optee_rpc_param param = { };
 u32 ret;
 /* 设定触发smc操作的第一个参数a0的值为OPTEE_SMC_CALL_WITH_ARG,通过OPTEE_SMC_CALL_WITH_ARG值可以知道,该函数将会执行std的smc操作 */
 param.a0 = OPTEE_SMC_CALL_WITH_ARG;
 reg_pair_from_64(&m.a1, &m.a2, parg);
 /* 初始化调用的等待队列 */
 optee_cq_wait_init(&optee->call_queue, &w);
 /*进入loop循环,触发smc操作并等待secure world的返回*/
 while (true) {
  struct arm_smccc_res res;
  /* 触发smc操作 */
  optee->invoke_fn(param.a0, param.a1, param.a2, param.a3,
       param.a4, param.a5, param.a6, param.a7,
       &res);
  /* 判定secure world是否超时,如果超时,完成一次调用,进入下一次循环直到secure world端完成open session请求 */
  if (res.a0 == OPTEE_SMC_RETURN_ETHREAD_LIMIT) {
   optee_cq_wait_for_completion(&optee->call_queue, &w);
  } else if (OPTEE_SMC_RETURN_IS_RPC(res.a0)) {
   /* 处理rpc操作 */
   param.a0 = res.a0;
   param.a1 = res.a1;
   param.a2 = res.a2;
   param.a3 = res.a3;
   optee_handle_rpc(ctx, &m);
  } else {
   /* 创建session完成之后跳出loop,并返回a0的值 */
   ret = res.a0;
   break;
  }
 }
 /* 执行等待队列最后完成操作 */
 optee_cq_wait_final(&optee->call_queue, &w);
 return ret;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 291

9.6.5 libteec库中的invoke操作

    当完成session的打开操作后，
    用户就可以调用
TEEC_InvokeCommand接口来调用对应的TA中特定
的操作了，
    TEEC_InvokeCommand函数最终会调用
驱动的tee_ioctl_invoke函数来完成具体的操作。该
函数内容如下：



static int tee_ioctl_invoke(struct tee_context *ctx,
     struct tee_ioctl_buf_data __user *ubuf)
{
 int rc;
 size_t n;
 struct tee_ioctl_buf_data buf;
 struct tee_ioctl_invoke_arg __user *uarg;
 struct tee_ioctl_invoke_arg arg;
 struct tee_ioctl_param __user *uparams = NULL;
 struct tee_param *params = NULL;
 /* 参数检查 */
 if (!ctx->teedev->desc->ops->invoke_func)
 return -EINVAL;
 /* 数据复制到kernel space */
 if (copy_from_user(&buf, ubuf, sizeof(buf)))
 return -EFAULT;
 if (buf.buf_len > TEE_MAX_ARG_SIZE ||
 buf.buf_len < sizeof(struct tee_ioctl_invoke_arg))
 return -EINVAL;
 uarg = u64_to_user_ptr(buf.buf_ptr);
 if (copy_from_user(&arg, uarg, sizeof(arg)))
 return -EFAULT;
 if (sizeof(arg) + TEE_IOCTL_PARAM_SIZE(arg.num_params) != buf.buf_len)
 return -EINVAL;
 /* 组合需要传递到secure world中的参数buffer */
 if (arg.num_params) {
 params = kcalloc(arg.num_params, sizeof(struct tee_param),
     GFP_KERNEL);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 292

        if (!params)
return -ENOMEM;
        uparams = uarg->params;
        rc = params_from_user(ctx, params, arg.num_params, uparams);
        if (rc)
            goto out;
     }
     /* 使用对应的session触发smc操作 */
     rc = ctx->teedev->desc->ops->invoke_func(ctx, &arg, params);
     if (rc)
        goto out;
     /* 检查和解析返回的数据,并将数据复制到userspace用户体用的buffser中 */
     if (put_user(arg.ret, &uarg->ret) ||
        put_user(arg.ret_origin, &uarg->ret_origin)) {
        rc = -EFAULT;
        goto out;
     }
     rc = params_to_user(uparams, arg.num_params, params);
    out:
     if (params) {
        /* Decrease ref count for all valid shared memory pointers */
        for (n = 0; n < arg.num_params; n++)
            if (tee_param_is_memref(params + n) &&
               params[n].u.memref.shm)
               tee_shm_put(params[n].u.memref.shm);
        kfree(params);
     }
     return rc;
    }










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 293

9.7 tee_supplicant接口在驱动中的实现

   tee_supplicant与OP-TEE之间的交互模式类似于
生产者与消费者的关系。完成上述需求的整个过程
包含驱动接收来自OP-TEE的请求、tee_supplicant从
驱动中获取OP-TEE的请求并处理、驱动返回请求
操作结果给OP-TEE三部分。其整个过程如图9-4所
示。










    图9-4 OP-TEE驱动处理RPC请求的过程


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 294

当libteec库调用驱动来与OP-TEE进行数据的交
互时，最终会调用optee_do_call_with_arg函数完成
安全监控模式调用（smc）的操作，该函数中有一
个无限循环，每次触发安全监控模式调用后会从安
全世界状态（SWS）中返回的参数res.a0中获取到
返回值，以此来判定当前从安全世界状态返回的数
据是要执行RPC操作还是直接返回到CA。如果是来
自OP-TEE的RPC请求，则会将请求存放到请求队
列req中，然后block住，直到tee_supplicant处理完请
求并将req->c标记为完成状态后才会进入下一个
loop，重新触发安全监控模式调用，将处理结果返
回给OP-TEE。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 295

9.7.1　接收OP-TEE的RPC请求

  当libteec库触发安全监控模式调用后，最终会
调用OP-TEE驱动的optee_do_call_with_arg函数，该
函数会进入到死循环，第一条语句会采用安全监控
模式调用，将用户空间的请求发送给OP-TEE，待
从OP-TEE中返回后，会对返回值进行判定。如果
返回的res.a0参数是需要驱动进行RPC操作，则该函
数会调用optee_handle_rpc函数，经过各种参数分析
和函数调用后，程序最后会调用
optee_supp_thrd_req函数将来自OP-TEE的请求存放
到tee_supplicant的请求队列中。该函数的内容如
下：

u32 optee_supp_thrd_req(struct tee_context *ctx, u32 func, size_t num_params,
  struct tee_param *param)
{
  struct optee *optee = tee_get_drvdata(ctx->teedev);
  struct optee_supp *supp = &optee->supp;
  struct optee_supp_req *req = kzalloc(sizeof(*req), GFP_KERNEL);
  bool interruptable;
  u32 ret;
  if (!req)
  return TEEC_ERROR_OUT_OF_MEMORY;
  /* 初始化该请求消息的c成员并配置请求数据 */
  init_completion(&req->c);
  req->func = func;
  req->num_params = num_params;
  req->param = param;
  /* 将接收到的请求添加到驱动的TEE请求消息队列中 */
  mutex_lock(&supp->mutex);
  list_add_tail(&req->link, &supp->reqs);

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 296

     mutex_unlock(&supp->mutex);
     /* 将supp->reqs_c置位,通知tee_supplicant的receve操作当前驱动中有一个来自TEE的请求 */
     complete(&supp->reqs_c);
     /* block在这里,通过判定req->c是否被置位来判定当前请求是否被处理完毕,而req->c的置位是由tee_supplicant的send调用来完成的,如果被置位,则进入while循环中进行返回值的设定并跳出while*/
     while (wait_for_completion_interruptible(&req->c)) {
      mutex_lock(&supp->mutex);
      interruptable = !supp->ctx;
      if (interruptable) {
       interruptable = !req->busy;
       if (!req->busy)
list_del(&req->link);
      }
      mutex_unlock(&supp->mutex);

      if (interruptable) {
       req->ret = TEEC_ERROR_COMMUNICATION;
       break;
      }
     }
     ret = req->ret;
     kfree(req);
     return ret;
    }



      当请求被处理完成后，函数返回处理后的数据
    到optee_do_call_with_arg函数中，
           并进入
    optee_do_call_with_arg函数while循环的下一次循
    环，
      将处理结果返回给OP-TEE。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 297

9.7.2　获取OP-TEE的RPC请求

      tee_supplicant会调用read_request函数从OP-
TEE驱动的请求队列中获取当前存在的来自OP-TEE
的请求。该函数最终会调用OP-TEE驱动中的
optee_supp_recv函数。该函数的内容如下：


    int optee_supp_recv(struct tee_context *ctx, u32 *func, u32 *num_params,
struct tee_param *param)
    {
     struct tee_device *teedev = ctx->teedev;
     struct optee *optee = tee_get_drvdata(teedev);
     struct optee_supp *supp = &optee->supp;
     struct optee_supp_req *req = NULL;
     int id;
     size_t num_meta;
     int rc;
     /* 对被用来存放TEE请求参数的数据的buffer进行检查 */
     rc = supp_check_recv_params(*num_params, param, &num_meta);
     if (rc)
      return rc;
     /* 进入到loop循环中,从驱动的请求消息队列中获取来自TEE中的请求,直到获取之后才会跳出该loop*/
     while (true) {
      mutex_lock(&supp->mutex);
      /* 尝试从驱动的请求消息队列中获取来自TEE的一条请求 */
      req = supp_pop_entry(supp, *num_params - num_meta, &id);
      mutex_unlock(&supp->mutex);
      /* 判定是否获取到请求。如果获取到,则跳出该loop */
      if (req) {
            if (IS_ERR(req))
            return PTR_ERR(req);
            break;
      }
     /* block在这里,直到在optee_supp_thrd_req函数中发送了complete(&supp->reqs_c)操作后才继续往下执行 */
     if (wait_for_completion_interruptible(&supp->reqs_c))
      return -ERESTARTSYS;
     }



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
            更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 298

 /* 设定参数进行异步处理请求的条件 */
 if (num_meta) {
  param->attr = TEE_IOCTL_PARAM_ATTR_TYPE_VALUE_INOUT |
      TEE_IOCTL_PARAM_ATTR_META;
  param->u.value.a = id;
  param->u.value.b = 0;
  param->u.value.c = 0;
 } else {
  mutex_lock(&supp->mutex);
  supp->req_id = id;
  mutex_unlock(&supp->mutex);
 }
 /* 解析参数,设定tee_supplicant将要执行的具体(加载TA、操作文件系统、操作EMMC的rpmb分区等)操作和相关参数 */
 *func = req->func;
 *num_params = req->num_params + num_meta;
 memcpy(param + num_meta, req->param,
  sizeof(struct tee_param) * req->num_params);
 return 0;
}



  从请求消息队列中获取到来自OP-TEE的请求
后，
  返回到tee_supplicant中继续执行。根据返回的
func值和参数执行OP-TEE要求在REE侧需要的操
作。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 299

9.7.3 OP-TEE的RPC请求的返回

     当tee_supplicant执行完OP-TEE请求的操作后，
会调用write_response函数将数据返回给OP-TEE。
而write_response函数最终会调用驱动的
optee_supp_send函数。该函数主要是通过调用
complete(&req->c)操作来完成对该请求的结构体成
员c的置位，通知optee_supp_thrd_req函数执行下一
步操作，
        返回到optee_do_call_with_arg函数中进入
该函数中的下一轮loop循环中，安全监控模式调用
将结果返回给OP-TEE。optee_supp_send函数的内
容如下：


    int optee_supp_send(struct tee_context *ctx, u32 ret, u32 num_params,
struct tee_param *param)
    {
     struct tee_device *teedev = ctx->teedev;
     struct optee *optee = tee_get_drvdata(teedev);
     struct optee_supp *supp = &optee->supp;
     struct optee_supp_req *req;
     size_t n;
     size_t num_meta;
     mutex_lock(&supp->mutex);
     /* 驱动中请求队列的pop操作 */
     req = supp_pop_req(supp, num_params, param, &num_meta);
     mutex_unlock(&supp->mutex);
     if (IS_ERR(req)) {
      /* 报错返回错误编号使REE侧的tee_supplicant进程重启 */
      return PTR_ERR(req);
     }
     /* 使用传入的参数,更新请求的参数区域,将需要返回给TEE侧的数据填入对应的位置 */
     for (n = 0; n < req->num_params; n++) {




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 300

  struct tee_param *p = req->param + n;
  switch (p->attr & TEE_IOCTL_PARAM_ATTR_TYPE_MASK) {
  case TEE_IOCTL_PARAM_ATTR_TYPE_VALUE_OUTPUT:
  case TEE_IOCTL_PARAM_ATTR_TYPE_VALUE_INOUT:
   p->u.value.a = param[n + num_meta].u.value.a;
   p->u.value.b = param[n + num_meta].u.value.b;
   p->u.value.c = param[n + num_meta].u.value.c;
   break;
  case TEE_IOCTL_PARAM_ATTR_TYPE_MEMREF_OUTPUT:
  case TEE_IOCTL_PARAM_ATTR_TYPE_MEMREF_INOUT:
   p->u.memref.size = param[n + num_meta].u.memref.size;
   break;
  default:
   break;
  }
 }
 req->ret = ret;
 // 通知optee_supp_thrd_req函数一个来自TEE侧的请求已经被处理完毕,可以继续往下执行
 complete(&req->c);
 return 0;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 301

9.8　小结

本章介绍了libteec库中的接口和tee_supplicant
的调用在驱动中的具体实现，libteec库中的接口主
要是发送REE侧的请求到OP-TEE，REE侧与OP-TE
之间的数据传递是通过共享内存的方式来实现的，
而该共享内存是在挂载驱动时被分配好的。

从tee_supplicant处理来自OP-TEE的请求过程来
看主要有三点。

·驱动在触发安全监控模式调用后会进入到loop
循环中，根据OP-TEE中的返回值来判定该返回是
来自OP-TEE的RPC请求还是CA请求的处理结果。
如果是RPC请求，也就是需要驱动或者
tee_supplicant执行相关操作，驱动将RPC请求保存
到OP-TEE驱动的请求消息队列中，然后等待直到
收到处理结果；

·tee_supplicant作为一个常驻进程存在于Linux
中，它会不停地尝试从驱动的请求消息队列中获取
来自OP-TEE的请求。如果请求消息队列中并没有
请求则会一直等待，直到拿到请求才返回，拿到请
求之后会对请求进行解析，然后根据请求ID执行具
体的操作；


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 302

   ·tee_supplicant处理完来自OP-TEE的请求后，
会调用send操作将处理结果存放到该消息队列的参
数区域，并使用complete函数通知OP-TEE驱动该请
求已经被处理完毕。OP-TEE驱动block住的地方可
以继续往下执行，通过安全监控模式调用将结果返
回给OP-TEE。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 303

第三篇　OP-TEE内核篇

第10章　ARM核安全态和非安全态间的切换
第11章　OP-TEE对安全监控模式调用的处理

第12章　OP-TEE对中断的处理
第13章　OP-TEE对TA操作的各种实现
第14章　OP-TEE的内存和缓存管理

第15章　OP-TEE中的线程管理
第16章　OP-TEE的系统调用
第17章　OP-TEE的IPC机制










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 304

第10章　ARM核安全态和非安全态间
的切换

10.1 ARMv7基本知识

  ARMv7架构的ARM核为支持TrustZone技术，
在ARM核原有七种运行模式的基础上扩展除了
Monitor模式，正常世界状态（NWS）与安全世界
状态（SWS）之间的切换就是由运行于Monitor模
式下的程序来完成的，为方便理解在ARMv7架构中
正常世界状态与安全世界状态之间的切换，本节将
介绍一些基础知识。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 305

10.1.1 ARMv7运行模式扩展

  在未支持TrustZone技术之前，ARM具有七种
运行模式，分别为：

  ·usr模式（用户模式）：正常程序运行时的模
式；

  ·fiq模式（快速中断模式）：当配置有快速中
断时，如果产生fiq事件，ARM核将会切换到该模
式；

  ·irq模式（用户模式）：中断模式，一般用于
通用中断处理，被ROS使用；

  ·svc模式（管理模式）：操作系统使用的保护
模式；

  ·sys模式（系统模式）：运行具有特权的操作
系统任务；

  ·abt模式（数据访问终止模式）：当数据或者
指令预取值时终止则会进入该模式；

  ·und模式（未定义指令模式）：当未定义指令


 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 306

执行时则会进入该模式。

  支持TrustZone技术后，ARM增加了Monitor模
式，Monitor模式起到进行安全世界状态与正常世界
状态之间切换的桥梁作用。所以在ARMv7架构的
ARM核中具有八种类型的运行模式和两种状态，每
种状态下具有自己独立的七种模式，Monitor模式是
共享的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 307

10.1.2　安全状态位扩展

 在支持TrustZone技术时，ARM在AXI系统总线
上增加了一个安全状态位（NS bit）（详细情况可
查阅ARM给出的TrustZone白皮书），而安全状态
位就是用来标识当前的数据、指令是属于安全世界
状态还是正常世界状态，安全状态位会被保存到scr
寄存器的第0位。当安全状态位等于1时，处理器处
于正常世界状态；当安全状态位等于0时，处理器
处于安全世界状态。

 除了对总线进行扩展之外，ARM对MMU和
Cache也同样进行了安全状态位的扩展，用于标记
MMU中存放的物理内存映射后的地址是属于安全
内存地址还是非安全地址，而对于Cache该位会被
用来标记当前的Cache是属于安全态的Cache还是非
安全态的Cache。当ARM核访问物理地址时，会对
该虚拟地址的安全状态位进行检查，而在访问物理
内存时安全扩展组件会对地址进行权限检查，该权
限检查操作属于硬件级别的检查，不受软件的控
制。关于安全地址的配置则是在IC设计时通过配置
安全组件的参数来设定的。





 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 308

10.1.3　重要寄存器

  执行两个世界之间的切换操作会使用到各种寄
存器的操作，这些寄存器的作用说明如下。

1.异常向量基地址寄存器
  异常向量基地址寄存器（Vector Base Address
Register，VBAR）将保存异常向量表的基地址，在
安全世界状态和正常世界状态都具有各自独有的
VBAR寄存器用于存放两种状态各自独有的异常向
量表的基地址。

2.Monitor模式的异常向量基地址寄存器

  Monitor模式的异常向量基地址寄存器
（Monitor Vector Base Address Register，MVBAR）
用于保存在Monitor模式下异常向量表的基地址，该
寄存器在安全世界状态和正常世界状态之间进行切
换时起到关键作用。

3.安全配置寄存器
  处理器在运行时，安全配置寄存器（Secure
Configuration Register，SCR）中会保存相关的标


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 309

志，其中用于标记处理器处于安全世界状态还是正
常世界状态的安全状态位（NS bit）就被保存在该
寄存器中。

4.栈指针寄存器

                                     栈指针寄存器（Stack Pointer，SP）用来存放
处理器使用的栈的偏移地址。

5.当前程序状态寄存器
                                 当前程序状态寄存器（Current Program Status
Register，CPSR）将保存处理器运行时的各种标志
位信息，包括标志域、状态域、扩展域和控制域。

6.程序保存状态寄存器
                                             当特定的异常中断发生时，程序保存状态寄存
器（Saved Program Status Register，SPSR）将保存
当前程序的cpsr寄存器中的内容，待异常中断退出
之后，处理器会使用spsr寄存器中的数据来恢复cpsr
寄存器中的数据。

7.链接寄存器

链接寄存器（Link Register，LR）一般用来保
存子程序的返回地址。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 310

10.1.4　安全监控模式调用的汇编指令

通过在程序中执行smc汇编指令可以让处理器
进入Monitor模式。如果该汇编指令执行成功，则处
理器就切换到了Monitor模式下，并且更新Monitor
模式下的重要寄存器，包括CPSR、SPSR、LR、
SCR等。该操作与ARM进入到IRQ、ABT等模式的
操作一样，采取的是产生异常来进行模式的切换。
当处理器进入到Monitor后，处理器就会去查询该模
式下的异常处理向量表的位置，而Monitor模式下具
有独立的异常向量表的基地址，该地址被保存在
MVBAR寄存器中。在ARMv8架构同样也是使用
smc指令切换到EL3阶段。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 311

10.2 Monitor模式下的处理过程

  在安全世界状态或者正常世界状态中执行smc
指令之后，处理器将会触发异常操作进入Monitor模
式，并从MVBAR寄存器中获取到Monitor模式的异
常中断向量表基地址，进而找到安全监控模式调用
操作的异常处理函数。在本书第12章中将详细介绍
Monitor模式的异常中断向量表基地址是如何保存到
MVBAR寄存器中的，此处不赘述。Monitor模式下
整个处理逻辑如图10-1所示。










    图10-1 Monitor模式处理smc请求的过程





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 312

10.2.1 Monitor模式对安全监控模式调用的处理

      在OP-TEE中，Monitor模式的异常中断向量表
定义在optee_os/core/arch/arm/sm/sm_a32.S文件中，
其内容如下：



    LOCAL_FUNC sm_vect_table , :
    UNWIND(  .fnstart)
    UNWIND(  .cantunwind)
    b        .      /* Reset */
    b        .      /* Undefined instruction */
    b        sm_smc_entry /* Secure monitor call */
    b        .      /* Prefetch abort */
    b        .      /* Data abort */
    b        .      /* Reserved */
    b        .      /* IRQ */
    b        sm_fiq_entry /* FIQ */
    UNWIND(  .fnend)
    END_FUNC sm_vect_table



    当系统调用smc指令后，
                    处理器将切换到
    Monitor模式，
             查找到异常中断向量表，
                                      并执行b
    sm_smc_entry指令来对安全监控模式调用进行处
    理。该函数定义在
    optee_os/core/arch/arm/sm/sm_a32.S文件中，其完整
    内容如下：



    LOCAL_FUNC sm_smc_entry , :
    UNWIND(  .fnstart)
    UNWIND(  .cantunwind)




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 313

//将当前模式的lr和spsr寄存器中的值分别存储在monitor模式的sp中
srsdb   sp!, #CPSR_MODE_MON
push    {r0-r7}      //将r0到r7中的值压入栈(sp)
clrex       //独占清除,可以将关系紧密的独占访问监控器返回为开放模式
read_scr r1        //获取当前scr寄存器中的值,并将值保存在r1寄存器中
//判定scr寄存器中值的NS位是否为1,如果是1,则将会改变CPSR中的条件标志位为0
tst r1, #SCR_NS
bne .smc_from_nsec //如果请求来自于Normal World,则跳转到smc_from_nsec进行执行
//将当前处于SWS中,Secure World的运行栈存放的运行栈存放在r0中
//所以将当前sp的值减去offset就可以得到Secure World的运行栈地址
//并将sp的值指向得到的Secure World的运行栈地址
sub sp, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0)
//将sp的值加上secure world context的长度保存在r0寄存器中
add r0, sp, #SM_CTX_SEC
//保存secure world中八种模式的主要寄存器的值,并将值存放到r0寄存器
//而r0寄存器已经指向了CPU栈的位置中以便实现secure context的保存
bl    sm_save_modes_regs
//将sp的值加上secure world context中r0存放的位置
add r8, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0)
ldm r8, {r0-r4}     //将r8寄存器中的值指向地址中的值依次赋给r0到r4
//    将FIQ指向完的值保存到r9寄存器中
mov_imm r9, TEESMC_OPTEED_RETURN_FIQ_DONE
cmp r0, r9        //对比r0寄存器和r9寄存器中的值
//如果r0与r9不相等则将sp加上non-secure context中的r0的值保存到r8寄存器中
addne   r8, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
//如果r0与r9不相等则将r1到r4寄存器中的值依次加载到r8指定的位置
stmne   r8, {r1-r4}
//将sp的值加上non-secure world context的长度保存到r0寄存器中
add r0, sp, #SM_CTX_NSEC
bl    sm_restore_modes_regs      //获取non-secure context的内容
//执行返回到Normal World的操作
.sm_ret_to_nsec:
//将sp的值加上normal world context中从起始位置到r8寄存器的偏移值
//然后将结果保存到r0寄存器中
add     r0, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R8)
ldm r0, {r8-r12}      //r0寄存器中值指向的地址中的值一次次赋给r8和r12寄存器
read_scr r0 //获取当前scr寄存器的值,并保存到r0寄存器中
orr r0, r0, #(SCR_NS | SCR_FIQ)         //将scr中的NS位和FIQ位置1
write_scr r0      //将修改后的r0的值写入scr寄存器
//将sp的值加上non-secure world context中从起始位置到r0寄存器的偏移值
//然后将结果保存到sp中
add sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
b     .sm_exit     //跳转到sm_exit函数继续执行
//指向切换到Secure World的操作
.smc_from_nsec:




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 314

//当前处于Normal world态,栈指针就是sp
//所以将当前sp的值减去offset就可以得到Normal World的运行栈地址
//并将sp的值指向得到的Normal World的运行栈地址
sub sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
bic r1, r1, #(SCR_NS | SCR_FIQ)  //清除r1寄存器中的NS位和FIQ位
write_scr r1           //将r1寄存器中的值写入scr寄存器
//将sp的值加上non-secure world context中r8存放的值
//然后将结果保存到r0寄存器中
add r0, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R8)
stm r0, {r8-r12}       //将r8到r12寄存器中的值保存到r0指向的地址位置
mov r0, sp      //将sp的值赋值给r0寄存器
//跳转到secure world中进行处理来自non-secure world的smc请求
bl     sm_from_nsec
cmp r0, #0      //对比返回值是否为零,即判断sm_form_nsec函数是否执行成功
beq .sm_ret_to_nsec    //如果执行成功,则执行返回到non-secure world的操作
//如果sm_from_nsec函数并未执行成功,
//则将sp的值加上secure world context中r8存放的位置
//然后将结果保存到sp中
add sp, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0)
//执行退出sm操作
.sm_exit:
pop {r0-r7}            //将栈中的r0到r7寄存器中的值进行出栈操作
rfefd       sp!        //使用sp寄存器中的数据执行返回操作
UNWIND( .fnend)
END_FUNC sm_smc_entry










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 315

10.2.2　正常世界状态中触发安全监控模式调用的
处理过程

  当在正常世界状态（NWS）触发安全监控模式
调用时，SCR寄存器中的安全状态位（NS bit）必
定为1，处理器进入Monitor模式后，异常向量表中
的sm_smc_entry处理函数会执行smc_from_nsec的分
支，正式进入对来自正常世界状态的安全监控模式
调用进行具体处理。整个执行过程的流程图如图
10-2所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 316

图10-2 Monitor模式处理非安全态的安全监控模式
    调用流程

         在整个处理过程中，当SCR寄存器中的安全状
态位被设定后，即表示处理器的状态已经处于安全
世界状态或者是正常世界状态。判定该安全监控模
式调用来自于正常世界状态后将会执行到
sm_smc_entry函数中的smc_from_nsec代码块。该代
码块的注释可参阅10.2.1节。

在该代码段中有重要的两条语句，将从
sm_smc_entry开始获取到的scr值保存到r1寄存器
中，并清空r1寄存器中的安全状态位和FIQ位来完
成设定处理器状态和使能FIQ，然后再将r1寄存器
重新载入到scr寄存器中来完成正常世界状态到安全
世界状态的切换。

当正常世界状态中的安全监控模式调用被OP-
TEE处理完毕后，处理器将调用sm_ret_to_nsec函数
重新回到正常世界状态。从安全世界状态切换到正
常世界状态是通过读取当前scr寄存器的值到r0寄存
器，将r0寄存器中的值的安全状态位和FIQ位设置
成1来实现将处理器切换回正常世界状态和屏蔽FIQ
的功能。再通过write_scr函数将修改后的r0寄存器
的值重新载入到scr寄存器中。



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 317

10.2.3　安全世界状态中触发安全监控模式调用的
处理过程

  当安全监控模式调用是在安全世界状态中触发
时，SCR寄存器中的安全状态位必定为0，处理器
会执行smc_ret_to_nsec分支，正式进入对来自正常
世界状态的安全监控模式调用的处理过程。整个执
行过程的流程图如图10-3所示。










    图10-3 Monitor模式处理安全态的安全监控模式调


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 318

        用流程

  在上述过程中，从安全世界状态切换到正常世
界状态的方法也是通过修改SCR寄存器中的安全状
态位来实现的。在执行切换之前需要保存安全世界
状态的上下文信息，并将当前处理器的上下文信息
恢复成正常世界状态的上下文信息。待正常世界状
态上下文信息恢复之后，再修改SCR寄存器的安全
状态位来实现切换。保存安全世界状态的上下文信
息和恢复正常世界状态的上下文信息的操作分别通
过执行sm_save_modes_regs和
sm_restore_modes_regs函数来实现。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 319

10.3 ARMv8基本知识

  ARMv8使用ATF来完成正常世界状态与安全世
界状态之间切换的过程。ARMv8的切换过程与
ARMv7大致一样，也是使用smc汇编指令来触发切
换动作，关于切换的软件则需要运行在EL3中，且
该部分的具体切换过程是在ATF中的bl31中实现
的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 320

10.3.1 ARM核运行模式的新定义

  在ARMv8架构中，ARM对ARM核的运行异常
等级进行了重新定义，将异常等级使用EL来表示，
其与ARMv7的对应关系如表10-1所示。

  表10-1 ARMv7与ARMv8运行模式对比表




    在ARMv8架构中EL和软件关系如图10-4所
    示。








    图10-4 ARMv8运行等级对应关系

      由此可见ARMv7与ARMv8的不同之处只是将


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 321

Monitor模式重新定义，将其定义成EL3，在ARMv8
中使用ATF固件，EL3中的软件对应的是ATF中的
bl31部分。即关于安全世界状态与正常世界状态之
间的切换和安全监控模式调用的处理都会在ATF的
bl31中完成。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 322

10.3.2 ARMv8安全状态位扩展

ARMv8中关于总线、MMU、Cache以及其他
安全组件的扩展与ARMv7中的完全一样。相关扩展
功能的说明可参见第10.1.2节。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 323

10.3.3　寄存器资源

  处理器共有AArch32模式（A32/T32指令集）
和AArch64模式（A64指令集）两种，不同的运行
模式下只能运行对应的指令集，其中A32/T32指令
集和ARMv7架构下的指令集基本相同，而A64指令
支持64位的虚拟寻址空间，A64中大多数指令同时
支持32位和64位参数。

  不同模式下使用的寄存器资源如表10-2所示。
   表10-2　不同模式下使用的寄存器资源







  安全世界状态与正常世界状态之间的切换过程
中使用的关键寄存器与ARMv7中完全一致，可参阅
10.1.3节。




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 324

10.3.4　安全监控模式调用汇编指令

  ARMv8中smc指令的作用与ARMv7中完全一
样，在ARMv8中，smc指令用来产生目标为EL3的
异常（异常类型为：Synchronous），只有EL1或更
高的特权等级才能调用smc指令。任何需要交给OP-
TEE OS完成的任务都需要首先发送相应的安全监
控模式调用，ATF再根据该调用的来源、ID号等来
决定交给OP-TEE OS中相应的处理函数。触发安全
监控模式调用的语法为：

 smc #imm16 /* imm4 会被处理器忽略,一般设置为#0 */

  安全监控模式调用可以分为SMC32调用规范
（参数采用32位寄存器）和SMC64调用规范（参数
采用64位寄存器）。这种模式独立于AArch32和
AArch64模式。在AArch32模式下，ATF规定只能
使用SMC32规范；在AArch64模式下，可以同时使
用SMC32/64两种调用规范。该规范的说明如表10-3
所示。

      表10-3 SMC32/64规范说明




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 325

   两种规范中参数的位数不同，但ID号都是使用
的32位。为避免不同安全监控模式调用定义的冲突
和混乱，ATF通过定义安全监控模式调用格式中不
同域的含义来决定安全监控模式调用的类型、服务
范围等（参考SMC Calling Convention PDD）。

   由图10-5可知，在SMC32规范中[1]，针对TEE
OS的快速安全监控模式调用（fast smc）的SMC ID
范围为0xB2000000～0xBF00FFFF；针对TEE OS的
标准安全监控模式调用（std smc）的SMC ID范围
为0x02000000～0x1FFFFFFF。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 326

        图10-5 SMC请求ID格式说明
[1] smc指令文档：
ARM_DEN0028B_SMC_Calling_Convention.pdf。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 327

10.4 EL3的处理过程

  为了简化不同ARMv8平台Trusted OS的移植，
ARM提供了在EL3运行的代码示例，称为ARM
Trusted Firmware（以下简称为ATF）。采用的BSD
许可证，因此目前各个TEE厂商都是在ATF基础上
做相应的定制。在ATF里面提供了各种相应的接口
标准，包含：

  ·Power State Coordination Interface（PSCI）：
用于CPU电源管理。
  ·Trusted Board Boot Requirement：描述可信任
的系统启动/加载镜像的流程。

  ·SMC Calling Convention：定义Secure Monitor
Call的请求格式。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 328

10.4.1 ATF中EL3异常向量表的注册

在ATF的bl31启动过程中，
    会调用函数
el3_entrypoint_common来初始化异常向量寄存器
（VBAR/MVBAR）。以下是
el3_entrypoint_common的部分实现，其中设定异常
向量的基地址为：


runtime_exceptions：
el3_entrypoint_common        \
     _init_sctlr=0           \
     _warm_boot_mailbox=0     \
     _secondary_cold_boot=0    \
     _init_memory=0           \
     _init_c_runtime=1         \
     _exception_vectors=runtime_exceptions    // 设置异常向量入口函数为runtime_exceptions
.macro el3_arch_init_common _exception_vectors
ldr     r0, =\_exception_vectors
stcopr r0, VBAR // 设置异常进入非Monitor/非Hyp模式下的异常向量基地址
stcopr        r0, MVBAR  // 设置异常进入Monitor模式下的异常向量基地址
Isb
     …
.endm



在runtime_exceptions中会设定不同异常向量的
入口函数，
     其中smc指令产生的异常属于
Synchronous异常，分别对应AArch64/32模式下的入
口为sync_exception_aarch64/32， 两者都调用同一个
处理函数handle_sync_exception。






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 329

10.4.2 EL3处理安全监控模式调用的流程

ARMv8调用smc指令产生安全监控模式调用
后，ARM核会切换到EL3中，然后读取MVBAR寄
存器中的异常向量表的基地址来获取异常向量表的
内容，并命中安全监控模式调用请求处理函数。对
于AArch32和AArch64结构，安全监控模式调用的
处理函数不同，但最终都会调用
handle_sync_exception函数来对安全监控模式调用
进行处理。进入handle_sync_exception函数后会对
触发安全监控模式调用的世界进行判定，并设定需
要切换到的那个世界的状态并恢复对应的CPU上下
文，再根据安全监控模式调用ID进入具体的分支，
并将ARM核的运行模式切换成EL1或者EL0，待安
全监控模式调用处理完毕后会再次触发安全监控模
式调用，触发异常重新进入EL3中继续运行余下流
程。整个过程如图10-6所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 330

图10-6 EL3处理安全监控模式调用的流程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 331

10.4.3　安全世界状态中触发安全监控模式调用的
处理过程

              在安全世界状态中触发安全监控模式调用后，
ARM核会进入EL3中，从MVBAR中获取异常向量
表的基地址，并找到安全监控模式调用的处理函
数，然后进入handle_sync_exception函数，再调用
opteed_smc_handler函数对该安全监控模式调用进行
处理，该函数中将判定该安全监控模式调用时SCR
寄存器中的安全状态位是否为安全值，然后再根据
SMC ID来决定是否需要恢复正常世界状态的运行
上下文，整体过程如图10-7所示。

           当OP-TEE处理完来自正常世界状态的安全监
控模式调用后会再次触发安全监控模式调用重新进
入EL3，再次调用EL3的安全监控模式调用处理函
数，调用opteed_smc_handler函数，根据SMC ID进
入不同的分支。一般情况下会进入
TEESMC_OPTEED_RETURN_CALL_DONE的分
支，在该分支中会保存安全世界状态的运行上下文
并恢复正常世界状态的运行上下文，然后调用
SMC_RET4返回到正常世界状态中继续运行。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 332

图10-7 EL3处理来自安全世界的安全监控模式调
    用的过程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 333

10.4.4　正常世界状态中触发安全监控模式调用的
处理过程

  在正常世界状态中调用smc指令触发安全监控
模式调用后，ARM核会进入EL3，即ATF中的
bl31，进入EL3后会从MVBAR寄存器中获取到EL3
的异常向量表，然后命中安全监控模式调用的处理
函数，最终调用opteed_smc_handler来处理该安全监
控模式调用，EL3处理正常世界状态中触发的安全
监控模式调用的整体流程如图10-8所示。

  在opteed_smc_handler函数中会调用
is_caller_non_secure来判定当前安全监控模式调用
是来自正常世界状态还是安全世界状态。如果异常
来自正常世界状态，则会保存正常世界状态的运行
上下文并恢复安全世界状态的运行上下文，然后根
据SMC ID将快速安全监控模式调用（fast smc）或
标准安全监控模式调用（stf smc）的处理函数注册
到运行上下文中，然后通过调用SMC_RET4进入
OP-TEE中对该安全监控模式调用做进一步处理。






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 334

图10-8 EL3处理来自非安全世界的安全监控模式
    调用的过程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 335

10.4.5 opteed_smc_handler函数

EL3中用于处理OP-TEE的安全监控模式调用是
通过调用opteed_smc_handler来实现的，
    该函数在
ATF启动时会被编译到rt_svc_descs段中。该函数的
内容如下：



uint64_t opteed_smc_handler(uint32_t smc_fid,
  uint64_t x1,
  uint64_t x2,
  uint64_t x3,
  uint64_t x4,
  void *cookie,   // 对应寄存器x5
  void *handle,   // 对应寄存器x6
  uint64_t flags)  // 寄存器x7(存放发送SMC请求时的安全状态)
{
 /* 取得对应cpu核的上下文 */
 cpu_context_t *ns_cpu_context;
 uint32_t linear_id = plat_my_core_pos();
 optee_context_t *optee_ctx = &opteed_sp_context[linear_id];
 uint64_t rc;
 /* 判定当前的smc是否是来自Normal World */
 if (is_caller_non_secure(flags)) {
 /* 保存Normal World的上下文 */
 cm_el1_sysregs_context_save(NON_SECURE);
 /* 检查保存的secure上下文与当前是否一致 */
 assert(&optee_ctx->cpu_ctx == cm_get_context(SECURE));
 /* 根据SMC类型跳转到相应el1的smc处理函数入口 */
 if (GET_SMC_TYPE(smc_fid) == SMC_TYPE_FAST) {
  cm_set_elr_el3(SECURE, (uint64_t)
  &optee_vectors->fast_smc_entry);
 } else {
  cm_set_elr_el3(SECURE, (uint64_t)
  &optee_vectors->yield_smc_entry);
 }
 /* 恢复EL1 Secure系统寄存器 */
 cm_el1_sysregs_context_restore(SECURE);



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 336

 cm_set_next_eret_context(SECURE);
 /* 恢复Secure上下文 */
 write_ctx_reg(get_gpregs_ctx(&optee_ctx->cpu_ctx),
  CTX_GPREG_X4,
  read_ctx_reg(get_gpregs_ctx(handle),
      CTX_GPREG_X4));
 write_ctx_reg(get_gpregs_ctx(&optee_ctx->cpu_ctx),
  CTX_GPREG_X5,
  read_ctx_reg(get_gpregs_ctx(handle),
      CTX_GPREG_X5));
 write_ctx_reg(get_gpregs_ctx(&optee_ctx->cpu_ctx),
  CTX_GPREG_X6,
  read_ctx_reg(get_gpregs_ctx(handle),
      CTX_GPREG_X6));
 /* Propagate hypervisor client ID */
 write_ctx_reg(get_gpregs_ctx(&optee_ctx->cpu_ctx),
  CTX_GPREG_X7,
  read_ctx_reg(get_gpregs_ctx(handle),
      CTX_GPREG_X7));
 /* 将smc ID以及参数填充到CPU的运行上下文中,并返回上下文的地址 */
 SMC_RET4(&optee_ctx->cpu_ctx, smc_fid, x1, x2, x3);
}
/* 这里从Trusted OS(EL1 Secure) 返回到EL3 */
switch (smc_fid) {
 /* optee 在冷启动后完成了初始化 */
 case TEESMC_OPTEED_RETURN_ENTRY_DONE:
 /* 设置optee上下文中的状态位为ON */
 if (optee_vectors) {
  set_optee_pstate(optee_ctx->state, OPTEE_PSTATE_ON);
  /* 注册psci电源管理下的optee处理函数 */
  psci_register_spd_pm_hook(&opteed_pm);
  /* 设置optee 安全中断处理函数 */
  flags = 0;
  set_interrupt_rm_flag(flags, NON_SECURE);
  rc = register_interrupt_type_handler(INTR_TYPE_S_EL1,
  opteed_sel1_interrupt_handler, flags);
  if (rc)
  panic();
 }
 /* optee os至此启动完成,恢复原来的C语言栈
 opteed_synchronous_sp_exit(optee_ctx, x1);
 /* 与PSCI控制相关的SMC请求返回ID 无特定行为 */
 case TEESMC_OPTEED_RETURN_ON_DONE:
 case TEESMC_OPTEED_RETURN_RESUME_DONE:
 case TEESMC_OPTEED_RETURN_OFF_DONE:




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 337

     case TEESMC_OPTEED_RETURN_SUSPEND_DONE:
     case TEESMC_OPTEED_RETURN_SYSTEM_OFF_DONE:
     case TEESMC_OPTEED_RETURN_SYSTEM_RESET_DONE:
     opteed_synchronous_sp_exit(optee_ctx, x1);
     /* EL1 Secure 之前SMC请求对应的返回 */
     case TEESMC_OPTEED_RETURN_CALL_DONE:
     /* 验证返回来自Secure */
     assert(handle == cm_get_context(SECURE));
     cm_el1_sysregs_context_save(SECURE);
     /* 恢复Normal World上下文前检查是否有效 */
     ns_cpu_context = cm_get_context(NON_SECURE);
     assert(ns_cpu_context);
     /* 恢复Normal World上下文 */
     cm_el1_sysregs_context_restore(NON_SECURE);
     cm_set_next_eret_context(NON_SECURE);
     /* 返回到Normal World 这里不再继续执行 */
     SMC_RET4(ns_cpu_context, x1, x2, x3, x4);
     /* Trusted OS收到安全中断处理完毕后也通过SMC请求返回到这里 */
     case TEESMC_OPTEED_RETURN_FIQ_DONE:
     /* 与前一个case基本一样,这里不再继续执行 */
     default:
     panic();
    }
    }



      opteed_smc_handler函数是ATF用于处理OP-
TEE产生的安全监控模式调用的处理函数，该函数
会对具体的安全监控模式调用类型进行处理。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 338

10.5　小结

  ARMv7架构中对安全监控模式调用的处理是
在Monitor模式下进行的，Monitor模式具有独立的
代码。而在ARMv8架构中，对安全监控模式调用的
处理则是在ATF的bl31中实现的，在ATF中ARM为
兼容不同厂商的TEE方案，提供了集成接口，只要
按照一定规范就可以将TEE方案对安全监控模式调
用的最终处理逻辑和接口添加到ATF的bl31中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 339

第11章　OP-TEE对安全监控模式调用
的处理

  来自正常世界状态（NWS）的安全监控模式调
用（smc）最终都会使用OP-TEE提供的处理接口进
行处理，而该处理接口中的内容在OP-TEE启动过
程中会被初始化。ARM官方将安全监控模式调用的
类型分为两个大类：快速安全监控模式调用（fast
smc）和标准安全监控模式调用（std smc），使用
不同的SMC ID来表示，关于SMC ID的含义和设
置，可参阅10.3.4节。ARMv7或者ARMv8中都使用
smc汇编指令来使ARM核陷入Monitor模式或者EL3
阶段，Monitor模式或者EL3判定安全状态位（NS
bit）后会设置对应的运行上下文，然后退出
Monitor模式或者EL3阶段，再跳转到OP-TEE中使
用特定的处理接口作进一步处理。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 340

11.1 OP-TEE的线程向量表

  OP-TEE中会定义一个线程向量表——
thread_vector_table，该线程向量表会被Monitor模式
或者EL3使用。在ARMv7架构中，Monitor模式的处
理代码将会使用该变量来进行安全监控模式调用的
最终处理，在ARMv8架构中，该线程向量表的地址
会在OP-TEE启动过程中返回给ATF中的bl31，当
EL3接收到FIQ、smc或者其他事件时，将会使用该
线程向量表中的具体函数来对事件进行最终的处
理，关于线程向量表和全局处理变量的内容可参阅
第12章。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 341

11.2 ARMv7中Monitor模式对安全监控模
式调用的处理

  当在正常世界状态或者安全世界状态中触发了
安全监控模式调用后，在ARMv7架构中ARM核会
切换到Monitor模式，且从MVBAR寄存器中获取到
异常向量表的基地址，然后查找到对安全监控模式
调用的处理函数——sm_smc_entry，使用该函数来
完成对安全监控模式调用的处理。在处理过程中会
判定该安全监控模式调用来自正常世界状态还是安
全世界状态，如果触发该安全监控模式调用是正常
世界状态，则会调用smc_from_nsec函数进行处
理，然后再根据SMC ID判定该安全监控模式调用
的类型做进一步处理。在Monitor模式中对安全监控
模式调用的处理过程如图11-1所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 342

 图11-1 ARMv7中Monitor模式对安全监控模式调
        用的处理流程

   ARMv7架构通过Monitor模式来实现正常世界
状态到安全世界状态之间的切换，并根据不同的
SMC ID来判定当前安全监控模式调用是快速安全
监控模式调用（fast smc）还是标准安全监控模式
调用（std smc），然后通过查找线程向量表进入到
fast smc和std smc的处理函数，在各自的处理函数
中最终会调用OP-TEE中的全局handler变量中对应


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 343

的函数指针来实现对该安全监控模式调用的具体处
理。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 344

11.3            ARMv8中EL3处理安全监控模式调用
的实现

          ARMv8架构使用ATF中的bl31来实现安全世界
状态与正常世界状态之间的切换，以及安全监控模
式调用的第一步处理，bl31运行于EL3，所有的安
全监控模式调用在ARMv8架构中都会在EL3先被处
理，然后根据不同的TEE方案使用对应的接口进行
安全监控模式调用的分发，在分发之前，bl31会设
定好ARM核安全状态，保存当前CPU的运行上下文
并恢复将要切换到的ARM核状态对应的运行上下
文。关于EL3中如何实现正常世界状态与安全世界
状态的切换以及如何跳转到OP-TEE中运行，可参
阅10.3节。从EL3进入OP-TEE是通过调用OP-TEE
在初始化阶段提供的线程向量表来实现的，即EL3
在设定CPU运行上下文时会根据SMC ID来判定是
进入到vector_std_smc_entry还是
vector_fast_smc_entry，在EL3中对安全监控模式调
用（smc）的处理流程如图11-2所示。







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 345

图11-2 ARMv8中EL3处理安全监控模式调用的流
    程









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 346

11.4 OP-TEE对快速安全监控模式调用的
处理

   快速安全监控模式调用（fast smc）一般会在
驱动挂载过程中，或需要获取OP-TEE OS版本信
息、共享内存配置、Cache信息时被调用。OP-TEE
不会使用建立线程的方式对fast smc进行处理，而
是在OP-TEE的内核空间调用tee_entry_fast函数对安
全监控模式调用（smc）进行处理，并通过再次产
生安全监控模式调用（smc）的方式返回最终的处
理结果。在OP-TEE中对fast smc的处理过程如图11-
3所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 347

图11-3                                       OP-TEE处理快速安全监控模式调用的流程
fast smc被处理完成后会重新触发安全监控模
式调用，对于ARMv7而言，触发该安全监控模式调
用的作用是让ARM核重新进入Monitor模式，最终
将结果返回给正常世界状态。对于ARMv8而言，触
发该安全监控模式调用的作用是让ARM核重新进入
EL3，即bl31中。在bl31中最终会调用
opteed_smc_handler函数对该安全监控模式调用进行
处理，根据该SMC的ID号进入
TEESMC_OPTEED_RETURN_CALL_DONE分支，
执行保存安全世界状态上下文、恢复正常世界状态
上下文，并将返回的数据填充到正常世界状态上下

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 348

文中，
   然后调用exit_el3退出EL3返回到正常世界状
态中继续执行。tee_entry_fast中的内容如下，
   用户
可以根据实际的需求增加。处理函数源码如下：



void tee_entry_fast(struct thread_smc_args *args)
{
 switch (args->a0) {
 /* Generic functions */
 /* 获取API被调用的次数,可以根据实际需求实现 */
 case OPTEE_SMC_CALLS_COUNT:
 tee_entry_get_api_call_count(args);
 break;
 /* 获取OP-TEE API的UID值 */
 case OPTEE_SMC_CALLS_UID:
 tee_entry_get_api_uuid(args);
 break;
 /* 获取OP-TEE中API的版本信息 */
 case OPTEE_SMC_CALLS_REVISION:
 tee_entry_get_api_revision(args);
 break;
 /* 获取OP-TEE OS的UID值 */
 case OPTEE_SMC_CALL_GET_OS_UUID:
 tee_entry_get_os_uuid(args);
 break;
 /* 获取OS的版本信息 */
 case OPTEE_SMC_CALL_GET_OS_REVISION:
 tee_entry_get_os_revision(args);
 break;
 /* 获取OP-TEE与驱动之间的共享内存配置信息 */
 case OPTEE_SMC_GET_SHM_CONFIG:
 tee_entry_get_shm_config(args);
 break;
 /* 获取I2CC的互斥体信息 */
 case OPTEE_SMC_L2CC_MUTEX:
 tee_entry_fastcall_l2cc_mutex(args);
 break;
 /* OP-TEE的capabilities信息 */
 case OPTEE_SMC_EXCHANGE_CAPABILITIES:
 tee_entry_exchange_capabilities(args);
 break;
 /* 关闭OP-TEE与驱动共享内存的cache */




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 349

 case OPTEE_SMC_DISABLE_SHM_CACHE:
  tee_entry_disable_shm_cache(args);
  break;
 /* 使能OP-TEE与驱动之间共享内存的cache */
 case OPTEE_SMC_ENABLE_SHM_CACHE:
  tee_entry_enable_shm_cache(args);
  break;
 /* 进入启动的第二阶段，启动其他ARM核 */
 case OPTEE_SMC_BOOT_SECONDARY:
  tee_entry_boot_secondary(args);
  break;
 default:
  args->a0 = OPTEE_SMC_RETURN_UNKNOWN_FUNCTION;
  break;
 }
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 350

11.5             OP-TEE对标准安全监控模式调用的
处理

             当OP-TEE驱动中触发标准安全监控模式调用
（std smc）时，ARMv7架构的ARM核会进入
Monitor模式，然后使用线程向量表中的
vector_std_smc_entry来处理该请求，ARMv8架构的
核则进入EL3，处理过程最终同样也会调用OP-TEE
中定义的线程向量表中的vector_std_smc_entry来对
该请求进行处理。关于在Monitor模式或EL3阶段如
何进入vector_std_smc_entry可参阅第10.2.1节和
10.4.1节。在Monitor模式或EL3都是根据a0参数中
的bit[31]来判定是快速安全监控模式调用（fast
smc）还是标准安全监控模式调用。如果bit[31]的
值是0，则会进入标准安全监控模式调用的处理逻
辑。vector_std_smc_entry函数的执行流程如图11-4
所示。









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 351

图11-4 OP-TEE处理标准安全监控模式调用请求的
     流程

 AArch32和AArch64中vector_std_smc_entry的
实现不一样，但都会调用thread_handler_std_smc函
数来处理标准的安全监控模式调用。
thread_handler_std_smc的内容和解释如下：

void thread_handle_std_smc(struct thread_smc_args *args)
{
 /* 检查堆栈 */
 thread_check_canaries();

 if (args->a0 == OPTEE_SMC_CALL_RETURN_FROM_RPC)
 //处理由tee_supplican回复的RPC请求处理结果


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 352

 thread_resume_from_rpc(args);
 else
 //处理来自Libteec的请求,主要包括open session, close session, invoke等
 thread_alloc_and_run(args);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 353

11.5.1 OP-TEE对RPC请求返回操作的处理

远程处理请求（Remote Procedure Call，RPC）
是指OP-TEE需要REE侧协助完成对REE侧资源进行
操作的请求。当OP-TEE需要操作REE侧的资源
时，OP-TEE会发送RPC类型的安全监控模式调
用，REE侧收到来自OP-TEE的RPC请求后，REE侧
根据RPC请求的ID进行处理并将处理结果返回给
OP-TEE，关于在REE侧如何获取和处理RPC请求可
参阅本书第8章。待REE侧处理完成后，会将处理
结果放在OP-TEE驱动设备teepriv0的返回队列中，
然后在驱动中触发安全监控模式调用将结果发送到
OP-TEE中。OP-TEE驱动产生的安全监控模式调用
请求是标准类型的SMC，最终在OP-TEE中会调用
thread_resume_from_rpc函数对该请求进行处理。
RPC请求的处理过程如图11-5所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 354

图11-5 OP-TEE处理RPC请求返回的数据处理流程
  OP-TEE在发送RPC请求时会带入发送该请求
的线程的ID，该ID将会在接收RPC结果时被用于恢
复该线程继续执行。关于RPC操作在OP-TEE中的
处理过程将会在第18.2节中详细介绍。






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 355

11.5.2 OP-TEE对libteec库触发的安全监控模式调
用的处理

 libteec库提供给上层使用的所有接口被调用之
后就有可能需要OP-TEE进行对应的操作。libteec库
提供的接口会将请求发送给OP-TEE驱动，由tee0设
备来发起标准的安全监控模式调用（std smc），在
ARMv7中，这些请求首先会被Monitor模式下的程
序处理，在ARMv8中会被ATF中的bl31处理，通过
命中OP-TEE提供的线程异常向量表中对应的
handler，进入OP-TEE的处理阶段。由libteec库的调
用触发的标准安全监控模式调用OP-TEE最终会调
用thread_alloc_and_run，创建一个线程来对该请求
进行专门的处理。而且在处理过程中可能会产生
OP-TEE与REE侧之间的RPC请求。
thread_alloc_and_run函数的内容和相关注释如下：

static void thread_alloc_and_run(struct thread_smc_args *args)
{
       size_t n;
       /* 获取当前CPU的ID,并返回该ARM核的对应结构体 */
       struct thread_core_local *l = thread_get_core_local();
       bool found_thread = false;
       /* 判定是否有线程正在占用CPU */
       assert(l->curr_thread == -1);
       /* 锁定线程状态 */
       lock_global();
       /* 查找系统中哪个线程空间当前可用 */
       for (n = 0; n < CFG_NUM_THREADS; n++) {


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 356

        if (threads[n].state == THREAD_STATE_FREE) {
        threads[n].state = THREAD_STATE_ACTIVE;
        found_thread = true;
        break;
        }
    }
    /* 解锁 */
    unlock_global();
    /* 初步设定返回给REE侧驱动的结果为OPTEE_SMC_RETURN_ETHREAD_LIMIT,返回的数据在后续处理中会被更改 */
    if (!found_thread) {
        args->a0 = OPTEE_SMC_RETURN_ETHREAD_LIMIT;
        return;
    }
    /* 记录当前ARM核使用了哪个线程空间来执行操作 */
    l->curr_thread = n;
    /* 设置选中的线程空间的flag为0*/
    threads[n].flags = 0;
    /*并对该线程中使用的pc、cpsr等相关寄存器进行设置,并且将参数传递到线程context的reg.ro~reg.r7中 */
    init_regs(threads + n, args);
    /* 保存hypervisor客户端的ID值 */
    threads[n].hyp_clnt_id = args->a7;
    /* 保存vfp相关数据 */
    thread_lazy_save_ns_vfp();
    /* 调用thread_resume函数,开始执行已经被初始化的线程 */
    thread_resume(&threads[n].regs);
}



1.新线程的创建

      thread_alloc_and_run会建立一个线程，并通过
init_regs函数进行初始化。该线程的运行上下文指
定该线程的入口函数以及运行时的参数。初始化完
成后，
        调用thread_resume启动该线程。线程运行上
下文的配置和初始化是在init_regs函数中实现，内
容如下：







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 357

    static void init_regs(struct thread_ctx *thread,
     struct thread_smc_args *args)
    {
     //指定该线程上下文中PC指针的地址,当该resume回来之后就会开始执行regs.pc指向的函数
     thread->regs.pc = (uint32_t)thread_std_smc_entry;
     /* 设定cpsr寄存器的值,屏蔽外部中断,进入SVC模式 */
     thread->regs.cpsr = read_cpsr() & ARM32_CPSR_E;
     thread->regs.cpsr |= CPSR_MODE_SVC | CPSR_A |
     (THREAD_EXCP_FOREIGN_INTR << ARM32_CPSR_F_SHIFT);
     if (thread->regs.pc & 1)
     thread->regs.cpsr |= CPSR_T;
     thread->regs.svc_sp = thread->stack_va_end;      //重新定位栈地址
     /*运行时传入的参数 */
     thread->regs.r0 = args->a0;
     thread->regs.r1 = args->a1;
     thread->regs.r2 = args->a2;
     thread->regs.r3 = args->a3;
     thread->regs.r4 = args->a4;
     thread->regs.r5 = args->a5;
     thread->regs.r6 = args->a6;
     thread->regs.r7 = args->a7;
    }



      创建线程的过程中会指定新的线程运行时的起
始PC指针，然后调用thread_resume函数启动该线
程，
      进入到pc指针指定的函数中继续执行。

2.线程恢复的实现
      通过init_regs配置完线程的运行上下文之后，
通过调用thread_resume函数来唤醒该线程，
        让其进
入到执行状态。thread_resume函数使用汇编来实
现，主要是保存一些寄存器状态、指定线程运行在
什么模式，该函数内容如下：






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 358

    FUNC thread_resume , :
    UNWIND(  .fnstart)
    UNWIND(  .cantunwind)
    add r12, r0, #(13 * 4)    /* 保存r0~r12寄存器的值 */
    cps #CPSR_MODE_SYS        //进入sys模式
    ldm r12!, {sp, lr}
    cps #CPSR_MODE_SVC        //进入svc模式
    ldm r12!, {r1, sp, lr}
    msr spsr_fsxc, r1
    cps #CPSR_MODE_SVC        //进入svc模式
    ldm r12, {r1, r2}
    push         {r1, r2}     //出栈操作
    ldm r0, {r0-r12}          //将参数存放到r0~r12中
    rfefd        sp!      //跳转到线程的pc指针处执行并返回
    UNWIND(  .fnend)
    END_FUNC thread_resume



3.线程的入口函数

      init_regs的regs.pc中已经指定了该线程被恢复
回来后pc指针的值为thread_std_smc_entry。当线程
被恢复后就会去执行该函数，进入到处理由调用
libteec库中的接口引起的安全监控模式调用（smc）
的过程，该入口函数使用汇编实现，内容如下：



    FUNC thread_std_smc_entry , :
    UNWIND(  .fnstart)
    UNWIND(  .cantunwind)
    push {r0-r7}         //入栈操作,将r0~r7的数据入栈
    mov r0, sp      //将r0执行栈地址作为参数传递给__thread_std_smc_entry
    bl       __thread_std_smc_entry  //正式对标准smc进行处理
    pop {r4-r7}          //出栈操作
    add sp, #(4 * 4)
    cpsid    aif         //关闭中断
    bl       thread_get_tmp_sp       //获取堆栈
    mov sp, r0      //将r0的值存放到sp中
    bl       thread_state_free       //释放thread




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 359

ldr r0, =TEESMC_OPTEED_RETURN_CALL_DONE //设置返回到normal的r0寄存器的值
mov r1, r4
mov r2, r5
mov r3, r6
mov r4, r7
smc #0     //调用smc,切回到normal world
b        . /* SMC 不需要返回 */
UNWIND(  .fnend)
END_FUNC thread_std_smc_entry

进入线程后会使用__thread_std_smc_entry函数
进行处理，在该函数中会调用在OP-TEE启动过程
中初始化的全局handler指针函数来处理标准的安全
监控模式调用（std smc），处理完成后该线程资源
将会被释放，线程编号将会被重新设定成可用状态
等待下次调用。

4.对安全监控模式调用中各种命令进行处理
在__thread_std_smc_entry函数中最终会调用
thread_std_smc_handler_ptr来对请求进行正式的处
理，而thread_std_smc_handler_ptr在OP-TEE启动的
过程中执行init_handlers函数时被初始化为handlers-
>std_smc。handlers->std_smc的实现根据不同的板
级可能有所不同，但一般会将该函数的名字设置成
tee_entry_std，关于thread_std_smc_handler_ptr函数
指针变量的赋值可参阅12.4节。tee_entry_std函数的
内容和注释如下：



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 360

void tee_entry_std(struct thread_smc_args *smc_args)
{
 paddr_t parg;
 struct optee_msg_arg *arg = NULL; /* fix gcc warning */
 uint32_t num_params;
 /* 判定a0是否合法 */
 if (smc_args->a0 != OPTEE_SMC_CALL_WITH_ARG) {
  EMSG("Unknown SMC 0x%" PRIx64, (uint64_t)smc_args->a0);
  DMSG("Expected 0x%x\n", OPTEE_SMC_CALL_WITH_ARG);
  smc_args->a0 = OPTEE_SMC_RETURN_EBADCMD;
  return;
 }
 /* 判定传入参数起始地址是否属于non-secure memory中,因为驱动与OP-TEE之间使用共享内存来共享数据,而共享内存属于非安全内存 */
 parg = (uint64_t)smc_args->a1 << 32 | smc_args->a2;
 if (!tee_pbuf_is_non_sec(parg, sizeof(struct optee_msg_arg)) ||
  !ALIGNMENT_IS_OK(parg, struct optee_msg_arg) ||
  !(arg = phys_to_virt(parg, MEM_AREA_NSEC_SHM))) {
  EMSG("Bad arg address 0x%" PRIxPA, parg);
  smc_args->a0 = OPTEE_SMC_RETURN_EBADADDR;
  return;
 }
 /* 检查所有参数是否存放在non-secure memory中 */
 num_params = arg->num_params;
 if (!tee_pbuf_is_non_sec(parg, OPTEE_MSG_GET_ARG_SIZE(num_params))) {
  EMSG("Bad arg address 0x%" PRIxPA, parg);
  smc_args->a0 = OPTEE_SMC_RETURN_EBADADDR;
  return;
 }
 thread_set_foreign_intr(true);    //使能中断
 /* 根据参数的cmd成员来判定来自libteec的请求是要求OP-TEE进行什么操作 */
 switch (arg->cmd) {
 /* 执行打开session操作 */
 case OPTEE_MSG_CMD_OPEN_SESSION:
  entry_open_session(smc_args, arg, num_params);
  break;
 /* 执行关闭session的操作 */
 case OPTEE_MSG_CMD_CLOSE_SESSION:
  entry_close_session(smc_args, arg, num_params);
  break;
 /* 请求特定TA执行特定的command */
 case OPTEE_MSG_CMD_INVOKE_COMMAND:
  entry_invoke_command(smc_args, arg, num_params);
  break;
 /* 请求取消掉某个session的command */
 case OPTEE_MSG_CMD_CANCEL:




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 361

  entry_cancel(smc_args, arg, num_params);
  break;
 default:
  EMSG("Unknown cmd 0x%x\n", arg->cmd);
  smc_args->a0 = OPTEE_SMC_RETURN_EBADCMD;
 }
}

 在tee_entry_std函数中会根据在OP-TEE中填入
的cmd值执行不同的分类操作，主要包括打开TA与
CA之间的session操作，关闭session操作，CA请求
invoke操作，取消invoke操作中特定的cmd操作等，
开发者也可以根据实际需求对该部分进行扩展，但
是必须保证在REE侧和TEE侧的修改一致。在执行
打开session的操作时，根据调用的TA是属于静态
TA还是动态TA可能会触发RPC请求，当TA image
存放在文件系统中时，在打开session时OP-TEE就
会触发RPC请求，请求tee_supplicant从文件系统中
读取TA image的内容，并将内容传递给OP-TEE，
然后经过对image的校验判定完成TA image的加载
操作后才执行open session查找并将该session添加到
OP-TEE的全局session的队列中，以便在执行invoke
时查询session队列找到对应的session。







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 362

11.6　小结

   本章介绍了OP-TEE中处理快速安全监控模式
调用（fast smc）和标准安全监控模式调用（std
smc）的详细过程以及由RPC请求和调用libteec库中
的接口产生的std smc的处理过程，而对于libteec库
产生的std smc进入到tee_entry_std处理之后会根据
command ID进行不同的操作，即Open session、
close session、invoke command等。open session是
invoke command操作的前提，在open session操作中
会根据TA的UUID来进行运行上下文的配置，并根
据是动态TA还是静态TA配置不同的operation，关
于各invoke command的操作将会在第13章中详细介
绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 363

第12章　OP-TEE对中断的处理

   一个完整的系统都会存在中断，ARMv7架构
扩展出了Monitor模式而ARMv8使用EL的方式对
ARM异常运行模式进行了重新定义，分为
EL0~EL3。在ARMv8架构系统中，OP-TEE运行于
安全侧的EL1，bl31运行于EL3。系统运行过程中任
何阶段都有可能会产生外部中断。本章将主要介绍
FIQ事件和IRQ事件在OP-TEE、ARMv7架构中的
Monitor模式、ARMv8架构中的EL3的处理过程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 364

12.1　系统的中断处理

  ARM核处于安全世界状态（SWS）和正常世
界状态（NWS）都具有独立的VBAR寄存器和中断
向量表。而当ARM核处于Monitor模式或者EL3时，
ARM核将具有独立的中断向量表和MVBAR寄存
器。想实现各种中断在三种状态下被处理的统一性
和正确性，就需要确保各种状态下中断向量表以及
GIC的正确配置。ARM的指导手册中建议在TEE中
使用FIQ，在ROS中使用IRQ，即TEE侧会处理由中
断引起的FIQ事件，而Linux内核端将会处理中断引
起的IRQ事件。而由于ATF的使用，Monitor状态或
者EL3下中断的处理代码将会在ATF中实现。
  针对ARM核，中断与ARM核每种状态的关系
图如图12-1所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 365

   图12-1 ARMv7架构对中断的处理示意
   系统中的中断主要被分为Native Interrupt和
Foreign Interrupt事件，FIQ会被TEE侧处理，IRQ会
被REE侧处理，如果在Monitor模式或EL3阶段产生
了中断，则处于Monitor模式或者EL3的软件会使用
MVBAR寄存器中保存的异常向量表中的处理函数
对FIQ或者IRQ事件进行处理。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 366

12.2　中断控制器

中断控制器（General Interruption Controller，
GIC）模块是CPU的外设之一，它的作用是接收来
自其他外设的中断引脚输入，然后根据中断触发模
式、中断类型优先级等设置来控制发送不同的中断
信号到CPU。ARM对GIC的架构也在不断改进，已
经从GICv1发展到现在的GICv4版本。目前主要使
用的是GICv2和GICv3架构。本书将介绍在支持TEE
安全扩展的ARM处理器平台上这两个版本的中断控
制器是如何工作的。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 367

12.2.1 GIC寄存器

                                            GIC模块中的寄存器主要分为中断控制分发寄
存器（缩写为GICD）以及CPU接口寄存器（缩写
为GICC）两部分。GICD接收所有的中断源，然后
根据中断的优先级来判定是否响应中断，以及是否
将该中断信号转发到对应的CPU。GICC和各个
ARM核相连。当收到来自GICD的中断信号时，由
GICC来决定是否将中断请求发送给ARM核。

                                            支持安全扩展的GIC模块将中断分为了两组：
Group0中断和Group1中断。对于ARMv7架构，
Group0为安全中断，Group1为非安全中断。对于
ARMv8架构，Group0为安全中断且有最高的优先
级，而Group1又分安全中断（Group1 Secure，
G1S）和非安全中断（Group1 NonSecure，
G1NS）。GIC会根据中断所在的Group安全类型及
当前ARM核运行模式来决定是发送FIQ还是IRQ信
号到ARM核。根据GIC版本的不同其决定方式也不
同。关于这点将在接下来的章节分开介绍。另外，
当ARM核收到FIQ/IRQ信号后会进入哪种模式是由
SCR寄存器来决定的。
ARMv8架构中，OP-TEE根据中断要求触发的
模式将中断类型分为三类，其定义如下：

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 368

#define INTR_TYPE_S_EL1 0 // 该中断应该由Secure EL1处理
#define INTR_TYPE_EL3 1 // 该中断应该由EL3处理
#define INTR_TYPE_NS 2 // 该中断应该由Normal World 处理


     不同版本的GIC对于以上三种类型的中断将会
产生不同的IRQ或FIQ事件，故需要先根据GIC版本
来确定上述三种类型的中断所产生的是IRQ还是
FIQ事件，然后再设定SCR寄存器中SCR.FIQ和
SCR.IRQ位来决定该中断是否会触发ARM核进入
EL3阶段。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 369

12.2.2 ARMv7 SCR寄存器的设定

      ARMv7架构中，SCR寄存器中的值是在
optee_os/core/arch/arm/sm/sm_a32.S文件被设定，其
内容如下：



    .sm_ret_to_nsec:
    //回到Normal World之前设定SCR.NS位
    add             r0, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R8)
    ldm             r0, {r8-r12}
    //设定SCR.NS下FIQ为1, FIQ中断会进入Monitor模式
    read_scr r0
    orr             r0, r0, #(SCR_NS | SCR_FIQ)
    write_scr r0
    add             sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
    b               .sm_exit
    .smc_from_nsec:
    //进入Secure World
    sub             sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
    /* 设定SCR.FIQ位为0,FIQ中断会直接通过VBAR进入EL1S FIQ异常向量 */
    bic             r1, r1, #(SCR_NS | SCR_FIQ)
    write_scr r1
    add             r0, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R8)
    stm             r0, {r8-r12}
    mov             r0, sp
    bl              sm_from_nsec
    cmp             r0, #0
    beq             .sm_ret_to_nsec
    add             sp, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0)










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 370

12.2.3 ARMv8 SCR寄存器的设定

      首先ATF在bl31/interrupt_mgmt.h下分别定义了
Secure EL1、NonSecure以及EL3模式下Group0和
Group1中断的路由模式。


    /* 以下分别定义了在EL3/SEL1/NS模式下中断的路由模式,定义名称格式如下
    * RM:   Routing Model
    * SEL1: Secure EL1 Mode(optee os)
    * NS:   Non Secure Mode
    * 0:    Routing Model 0
    * 1:    Routing Model 1
    * 值对应SCR寄存器中的bit[2:0],定义如下
    * bit[0]: SCR.NS (0: Secure, 1: Non Secure)
    * bit[1]: SCR.IRQ (0: enter IRQ mode 1: enter EL3 monitor)
    * bit[2]: SCR.FIQ (0: enter FIQ mode 1: enter EL3 monitor)
    */
    /* 从NS进入EL3.并在安全态的EL1进行处理 */
    #define INTR_SEL1_VALID_RM0      0x2
    /* 从NS或者安全态进入EL3 */
    #define INTR_SEL1_VALID_RM1      0x3
    /* 从NS进入EL1/EL2并转切到安全态的EL1 */
    #define INTR_NS_VALID_RM0      0x0
    /* 从NS到EL1/EL2或从安全态进入EL3
    #define INTR_NS_VALID_RM1      0x1
    /* 从NS进入EL3，并进入安全态的EL1，最终进入EL3 */
    #define INTR_EL3_VALID_RM0     0x2
    /* 从NS或安全态进入EL3 */
    #define INTR_EL3_VALID_RM1     0x3
    /* 默认模式转移路径 */
    #define INTR_DEFAULT_RM      0x0



    为兼容GICv2和GICv3平台，                在初始化CPU时
    将IRQ和FIQ位同时设置为1，               设置相关代码如下：




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
            更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 371

void css_cpu_standby(plat_local_state_t cpu_state)
{
 unsigned int scr;
 assert(cpu_state == ARM_LOCAL_STATE_RET);
 scr = read_scr_el3();
 /*对于非安全中断,如果当前CPU运行在EL3,对于GICv3平台非安全Group1中断会触发FIQ中断,而对于 GICv2平台Group1中断会触发IRQ中断,这里同时将FIQ和IRQ位设置成1所以GICv2/v3平台的非安全中断都会进入EL3 */
 write_scr_el3(scr | SCR_IRQ_BIT | SCR_FIQ_BIT);
 isb();
 dsb();
 //等待非安全中断触发
 wfi();
 //恢复SCR寄存器的原始值
 write_scr_el3(scr);
}



CPU初始化过程中会调用
register_interrupt_type_handler来设定Secure EL1下
的SCR寄存器，
 其内容如下：



case TEESMC_OPTEED_RETURN_ENTRY_DONE:
 assert(optee_vectors == NULL);
 optee_vectors = (optee_vectors_t *) x1;
 if (optee_vectors) {
set_optee_pstate(optee_ctx->state, OPTEE_PSTATE_ON);
//OP-TEE 初始化成功,安装psci处理函数
psci_register_spd_pm_hook(&opteed_pm);
//设置flag为ON_SECURE定义为1
flags = 0;
set_interrupt_rm_flag(flags, NON_SECURE);
//设定进入Secure EL1状态时SCR应使用的值
rc = register_interrupt_type_handler(INTR_TYPE_S_EL1,
opteed_sel1_interrupt_handler, flags);
if (rc)
panic();



register_interrypt_type_handler函数会调用




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 372

set_routing_model来定义三种不同目标的中断在EL3
和EL1的SCR寄存器的值，
该函数内容如下：



int32_t set_routing_model(uint32_t type, uint32_t flags)
{
 int32_t rc;
 rc = validate_interrupt_type(type);
 if (rc)
 return rc;
 /* 检查将要设定的SCR的值是否是之前interrupt_mgmt.h中预定义的有效值 */
 rc = validate_routing_model(type, flags);
 if (rc)
 return rc;
 /* 结构体变量intr_type_descs用来描述安全/正常模式下SCR的设定 */
 intr_type_descs[type].flags = flags;
 /* 设置在CPU安全模式下(SCR.NS=0)的SCR.IRQ、SCR.FIQ位 */
 set_scr_el3_from_rm(type, flags, SECURE);
 /* 设置在CPU正常模式下(SCR.NS=1)的SCR.IRQ、SCR.FIQ位 */
 set_scr_el3_from_rm(type, flags, NON_SECURE);
 return 0;
}



set_scr_el3_from_rm函数实现如下：


static void set_scr_el3_from_rm(uint32_t type, uint32_t interrupt_type_flags,
 uint32_t security_state)
{
 uint32_t flag, bit_pos;
 /*
 * 这里根据security_state状态来获取对应SCR要设定的值
 * 如果之前调用的是set_interrupt_rm_flag(flags, NON_SECURE)
 * 1. security_state == SECUREflag = (0xb10 >> SECURE) & 0xb1 = 0
 * 2. security_state == NONSECURE: flag = (0xb10 >> NONSECURE) & 0xb1 = 1
 * 如果之前调用的是set_interrupt_rm_flag(flags, SECURE) 同理
 * 1. security_state == SECURE: flag = 1
 * 2. security_state == NONSECURE: flag = 0
 */
 flag = get_interrupt_rm_flag(interrupt_type_flags, security_state);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 373

 /* 这个函数根据GIC的版本决定设定SCR寄存器中FIQ/IRQ位 */
 bit_pos = plat_interrupt_type_to_line(type, security_state);
 intr_type_descs[type].scr_el3[security_state] = flag << bit_pos;
 /* 如果当前上下文有效则可以在这里直接更新scr_el3否则将要设定的SCR的值保存在
 * intr_type_descs中,之后通过get_scr_els3_from_routing_model()函数来获取并
 * 写入SCR寄存器中
 */
 if (cm_get_context(security_state))
 cm_write_scr_el3_bit(security_state, bit_pos, flag);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 374

12.2.4 GICv2架构

     GICv2设定Group0为安全中断，Group1为非安
全中断。中断号属于哪个Group是由其在
GICD_IGROUPRn寄存器中的值来决定的。当GIC
接收到中断信号后，如果中断属于Group0则发送
IRQ信号到目标CPU，中断属于Group1则发送FIQ
信号到目标CPU。

     plat_interrupt_type_to_line（type，
security_state）在GICv2下的实现如下：


    uint32_t plat_interrupt_type_to_line(uint32_t type,
         uint32_t security_state)
    {
     assert(type == INTR_TYPE_S_EL1 ||
     type == INTR_TYPE_EL3 ||
     type == INTR_TYPE_NS);
     /* NonSecure中断发IRQ信号,设置SCR.IRQ = 1*/
     if (type == INTR_TYPE_NS)
       return __builtin_ctz(SCR_IRQ_BIT);
     /*
     * 两种情况
     * (1) FIQ disabled: 安全中断(Group0)会产生IRQ中断信号设置SCR.IRQ=1
     * (2) FIQ enabled:  安全中断(Group1)会产生FIQ中断信号设置SCR.FIQ=1
     */
     return ((gicv2_is_fiq_enabled()) ? __builtin_ctz(SCR_FIQ_BIT) :
         __builtin_ctz(SCR_IRQ_BIT));
    }








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 375

12.2.5 GICv3架构

与GICv2相比GICv3的主要改进有以下几点：

在软件中断（SGI）方面新增了中断目标路由
模式（affinity routing），SGI中断能支持更大范围
的CPU ID。
GICv3对Group1的中断类型进行了进一步的细
分。Group0中断和GICv2一样为安全中断（以下用
G0S表示）且拥有最高的优先级，而Group1中断又
分为Group1非安全中断（以下用G1NS表示）和
Group1安全中断（以下用G1S表示）。
GIC的CPU接口寄存器（GICC）不再需要地址
映射，可以直接通过系统寄存器访问。

在IRQ/FIQ都使能的情况下，属于Group0的中
断始终会触发FIQ信号，而属于Group1的中断则根
据CPU当前工作模式和中断类型（secure/non-
secure）分别触发FIQ或者IRQ信号。表12-1为EL3
在AArch64模式下GICv3对不同中断的处理。
表12-1  EL3在AArch64模式下中断的处理方式



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 376

      通过表12-1可知，当处理器接收的中断类型
（secure/non secure）和当前处理器工作模式
（secure/non-secure）不一致时，GIC会发送FIQ中
断信号否则会发出IRQ中断信号。

      plat_interrupt_type_to_line（type，
security_state）在GICv3下的内容如下：


    uint32_t plat_interrupt_type_to_line(uint32_t type,
         uint32_t security_state)
    {
     assert(type == INTR_TYPE_S_EL1 ||
     type == INTR_TYPE_EL3 ||
     type == INTR_TYPE_NS);
     assert(sec_state_is_valid(security_state));
     assert(IS_IN_EL3());
     switch (type) {
     case INTR_TYPE_S_EL1:
     /*
     * 当安全中断G1S在S-EL1发生IRQ中断,设置SCR.IRQ=1
     * 当安全中断G1S在NS发生FIQ中断,设置SCR.FIQ=1
     */
     if (security_state == SECURE)
              return __builtin_ctz(SCR_IRQ_BIT);
     else
              return __builtin_ctz(SCR_FIQ_BIT);
     case INTR_TYPE_NS:
     /*
     * 当非安全中断G1NS在NS发生IRQ中断,设置SCR.IRQ=1
     * 当非安全中断在S-EL1发生FIQ中断,设置SCR.FIQ=1
     */




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 377

  if (security_state == SECURE)
  return __builtin_ctz(SCR_FIQ_BIT);
  else
  return __builtin_ctz(SCR_IRQ_BIT);
 default:
  assert(0);
 case INTR_TYPE_EL3:
  /*无论在S-EL1还是在NS-EL1,目标为EL3的中断都是FIQ*/
  return __builtin_ctz(SCR_FIQ_BIT);
 }
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 378

12.3　异常向量表配置

  REE侧、TEE侧以及Monitor模式或EL3都可接
收中断信号。在系统中存在两个VBAR寄存器和一
个MVBAR寄存器，REE侧的VBAR寄存器中存放
的是Linux内核的异常向量表基地址，OP-TEE中的
VBAR寄存器存放的是OP-TEE系统的中断向量表基
地址，而Monitor或者EL3的MVBAR存放的是
Monitor模式或EL3运行时的中断向量表基地址，即
在Monitor或者EL3阶段是可以接收外部中断信号
的。本节将介绍OP-TEE中断的配置和Monitor或
EL3阶段中断的配置。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 379

12.3.1    ARMv7中Monitor模式的异常向量表

  ARMv7架构在ARM扩展出了Monitor模式，
Monitor模式属于安全世界状态，用于实现ARM核
安全世界状态与正常世界状态之间的切换，且该模
式具有独立的中断向量表。使用MVBAR寄存器来
保存该运行模式的中断向量表的基地址。在OP-
TEE初始化过程中会调用sm_init函数来初始化
Monitor模式的配置，并将Monitor模式的中断向量
基地址写入到MVBAR寄存器中，该函数内容如
下：

FUNC sm_init , :
UNWIND(   .fnstart)
       mrs r1, cpsr //设置Monitor模式使用的栈
       cps #CPSR_MODE_MON
       sub sp, r0, #(SM_CTX_SIZE - SM_CTX_NSEC)
       msr cpsr, r1
       ldr r0, =sm_vect_table    //将Monitor模式的异常向量表地址保存到r0寄存器中
       write_mvbar r0     //将Monitor模式的异常向量表基地址写入MVBAR寄存器中
       bx lr      //返回
END_FUNC sm_init

  sm_init函数中写入MVBAR寄存器中的值即是
Monitor模式下的异常向量表的基地址——
sm_vect_table，该向量表的内容如下：

LOCAL_FUNC sm_vect_table , :


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 380

UNWIND(  .fnstart)
UNWIND(  .cantunwind)
b        .              /* 重启操作 */
b        .              /* 未定义指令操作 */
b        sm_smc_entry   /* smc异常处理函数 */
b        .              /* 执行时的abort操作 */
b        .              /* 数据abort操作 */
b        .              /* 预留 */
b        .              /* IRQ事件 */
b        sm_fiq_entry   /* FIQ中断处理入口函数 */
UNWIND(  .fnend)
END_FUNC sm_vect_table



从上述异常向量表中可知，
                        当在Monitor模式
下接收到FIQ中断时，系统将会调用sm_fiq_entry函
数对该FIQ中断进行处理。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 381

12.3.2 ARMv8中EL3阶段的异常向量表

  ARMv8使用ATF中的bl31作为EL3阶段的代
码，
         其作用与ARMv7中Monitor模式下运行的代码
作用一致。在ATF的启动过程中，bl31通过调用
el3_entrypoint_common函数来进行EL3运行环境的
初始化，
      在初始化过程中会执行EL3阶段异常向量
表的初始化，
      EL3的异常向量表的基地址为
runtime_exception_vectors。EL3异常向量表的内容
如下：



vector_base runtime_exceptions
/*在EL3阶段不接收同步异常,如果产生当作错误处理 */
vector_entry sync_exception_sp_el0
no_ret  report_unhandled_exception
check_vector_size sync_exception_sp_el0
vector_entry irq_sp_el0
no_ret  report_unhandled_interrupt
check_vector_size irq_sp_el0
vector_entry fiq_sp_el0
no_ret  report_unhandled_interrupt
check_vector_size fiq_sp_el0
vector_entry serror_sp_el0
no_ret  report_unhandled_exception
check_vector_size serror_sp_el0
vector_entry sync_exception_sp_elx
no_ret  report_unhandled_exception
check_vector_size sync_exception_sp_elx
vector_entry irq_sp_elx
no_ret  report_unhandled_interrupt
check_vector_size irq_sp_elx
vector_entry fiq_sp_elx
no_ret  report_unhandled_interrupt
check_vector_size fiq_sp_elx




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 382

vector_entry serror_sp_elx
no_ret report_unhandled_exception
check_vector_size serror_sp_elx
/* AArch64的同步异常处理,smc异常将进入该向量中进行处理 */
vector_entry sync_exception_aarch64
handle_sync_exception
check_vector_size sync_exception_aarch64
/* AArch64的同步异常处理,IRQ事件将进入该向量中进行处理 */
vector_entry irq_aarch64
handle_interrupt_exception irq_aarch64
check_vector_size irq_aarch64
/* AArch64的同步异常处理,FIQ事件将进入该向量中进行处理 */
vector_entry fiq_aarch64
handle_interrupt_exception fiq_aarch64
check_vector_size fiq_aarch64
vector_entry serror_aarch64
no_ret report_unhandled_exception
check_vector_size serror_aarch64
/* AArch32的同步异常处理,smc异常将进入该向量中进行处理 */
vector_entry sync_exception_aarch32
handle_sync_exception
check_vector_size sync_exception_aarch32
/* AArch64的同步异常处理,IRQ事件将进入该向量中进行处理 */
vector_entry irq_aarch32
handle_interrupt_exception irq_aarch32
check_vector_size irq_aarch32
/* AArch64的同步异常处理,FIQ事件将进入该向量中进行处理 */
vector_entry fiq_aarch32
handle_interrupt_exception fiq_aarch32
check_vector_size fiq_aarch32
vector_entry serror_aarch32
no_ret report_unhandled_exception
check_vector_size serror_aarch32



从异常向量表来看，
    ARMv8架构中不管是
AArch32还是AArch64，当在EL3阶段产生了FIQ事
件或者IRQ事件后，bl31将会调用
handle_interrupt_exception宏来处理，
    该宏使用的参
数就是产生的异常的标签。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 383

12.3.3 OP-TEE异常向量的配置

在初始化阶段，OP-TEE异常向量的加载和配
置会通过执行thread_init_vbar函数来实现，从初始
化起始到配置异常向量表的整个调用过程如图12-2
所示。










图12-2   OP-TEE的异常向量表配置流程
thread_init_vbar函数在AArch32位系统中的定
义如下：

FUNC thread_init_vbar , :
UNWIND( .fnstart)


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 384

/* 设置VBAR寄存器的值 */
ldr r0, =thread_vect_table
write_vbar r0
bx       lr
UNWIND(  .fnend)
END_FUNC thread_init_vbar
KEEP_PAGER thread_init_vbar



thread_init_vbar函数在AArch64位系统中的定
义如下：



FUNC thread_init_vbar , :
adr x0, thread_vect_table    //获取OP-TEE异常向量表的基地址
msr vbar_el1, x0      //将OP-TEE的异常向量表的基地址写入到VBAR寄存器中
ret
END_FUNC thread_init_vbar
KEEP_PAGER thread_init_vbar //thread_init_vbar函数保存到__keep_meta_vars_pager段中


OP-TEE的AArch32中断向量表内容如下：


LOCAL_FUNC thread_vect_table , :
UNWIND(  .fnstart)
UNWIND(  .cantunwind)
b        .      /* Reset */
b        thread_und_handler        /* 异常指令处理函数 */
b        thread_svc_handler        /* 用于系统调用 */
b        thread_pabort_handler     /* abort异常处理函数 */
b        thread_dabort_handler     /* 数据abort异常处理 */
b        .      /* Reserved */
b        thread_irq_handler        /* IRQ事件处理函数 */
b        thread_fiq_handler        /* FIQ事件处理函数 */
UNWIND(  .fnend)
END_FUNC thread_vect_table








https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 385

OP-TEE的AArch64中断向量表内容如下：


LOCAL_FUNC thread_vect_table , :
.align         7
sync_el1_sp0:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b     el1_sync_abort
check_vector_size sync_el1_sp0
.align         7
irq_el1_sp0:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b     elx_irq
check_vector_size irq_el1_sp0
.align         7
fiq_el1_sp0:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b     elx_fiq
check_vector_size fiq_el1_sp0
.align         7
SErrorSP0:
b     SErrorSP0
check_vector_size SErrorSP0
.align         7
SynchronousExceptionSPx:
b   SynchronousExceptionSPx
check_vector_size SynchronousExceptionSPx
.align         7
IrqSPx:
b     IrqSPx
check_vector_size IrqSPx
.align         7
FiqSPx:
b     FiqSPx
check_vector_size FiqSPx
.align         7
SErrorSPx:
b     SErrorSPx
check_vector_size SErrorSPx
.align         7
el0_sync_a64:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
mrs          x2, esr_el1
mrs          x3, sp_el0



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 386

lsr          x2, x2, #ESR_EC_SHIFT
cmp          x2, #ESR_EC_AARCH64_SVC
b.eq         el0_svc
b    el0_sync_abort
check_vector_size el0_sync_a64
.align        7
el0_irq_a64:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b    elx_irq
check_vector_size el0_irq_a64
.align        7
el0_fiq_a64:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b    elx_fiq
check_vector_size el0_fiq_a64
.align        7
SErrorA64:
b    SErrorA64
check_vector_size SErrorA64
.align        7
el0_sync_a32:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
mrs x2, esr_el1
mrs x3, sp_el0
lsr x2, x2, #ESR_EC_SHIFT
cmp x2, #ESR_EC_AARCH32_SVC
b.eq     el0_svc
b    el0_sync_abort
check_vector_size el0_sync_a32
.align        7
el0_irq_a32:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b    elx_irq
check_vector_size el0_irq_a32
.align        7
el0_fiq_a32:
store_xregs sp, THREAD_CORE_LOCAL_X0, 0, 3
b    elx_fiq
check_vector_size el0_fiq_a32
.align        7
SErrorA32:
b    SErrorA32
check_vector_size SErrorA32
END_FUNC thread_vect_table





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 387

  当系统处于OP-TEE中时，系统会到VBAR寄存
器中获取OP-TEE的异常向量表基地址，然后根据
异常类型获取到FIQ或IRQ事件的处理函数，并对
不同的事件进行处理。针对不同的事件会调用线程
向量表thread_vector_table变量中对应的处理函数来
完成对该异常事件的处理。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 388

12.4 OP-TEE的线程向量表

     在OP-TEE中会定义一个用于保存各种事件处
理函数的线程向量表，该线程向量表中的成员是
OP-TEE对fast smc、std smc、FIQ事件、CPU关闭
和打开以及系统关机和重启事件的处理函数，该变
量的内容如下：


    FUNC thread_vector_table , :
    UNWIND(  .fnstart)
    UNWIND(  .cantunwind)
    b        vector_std_smc_entry     //处理标准smc异常
    b        vector_fast_smc_entry    //处理快速smc异常
    b        vector_cpu_off_entry      //关闭CPU操作
    b        vector_cpu_resume_entry   //恢复CPU操作
    b        vector_cpu_suspend_entry  // CPU待机操作
    b        vector_fiq_entry          // FIQ事件处理
    b        vector_system_off_entry    //系统关机操作
    b        vector_system_reset_entry  //重启系统操作
    UNWIND(  .fnend)
    END_FUNC thread_vector_table


     ARMv8架构中，该线程向量表的地址会被返
回给bl31，以备EL3接收到安全监控模式调用或FIQ
事件时可使用该变量中的处理函数对请求和异常事
件进行进一步的处理。在ARMv7架构中，该变量会
被Monitor模式下运行的程序使用，用于处理安全监
控模式调用和FIQ事件。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 389

12.5　全局handle变量的初始化

   ARMv8架构中会将thread_vector_table的地址返
回给ATF的bl31，用于处理安全监控模式调用、FIQ
事件以及CPU和系统的相关操作，而在ARMv7中则
会被Monitor模式的异常向量表使用。通过对该
thread_vector_table的基地址进行偏移计算来获得安
全监控模式调用、FIQ事件以及CPU和系统的相关
处理函数的实际地址，然后调用获得的地址指向的
函数来处理上述事件。

     thread_vector_table变量中的函数都是使用汇编
来实现的，当异常事件发生时会调用各自对应的处
理函数对事件进行处理，处理函数的名字类似于
thread_xxx_xxx_handler_ptr。这些变量都是函数指
针，在OP-TEE启动时，通过调用init_handlers函数
来实现对这些全局函数指针变量进行赋值，执行过
程如图12-3所示。









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 390

    图12-3　全局handle变量初始化过程
    init_handlers函数的内容如下：


static void init_handlers(const struct thread_handlers *handlers)
{
    thread_std_smc_handler_ptr = handlers->std_smc;
    thread_fast_smc_handler_ptr = handlers->fast_smc;
    thread_nintr_handler_ptr = handlers->nintr;
    thread_cpu_on_handler_ptr = handlers->cpu_on;
    thread_cpu_off_handler_ptr = handlers->cpu_off;
    thread_cpu_suspend_handler_ptr = handlers->cpu_suspend;
    thread_cpu_resume_handler_ptr = handlers->cpu_resume;
    thread_system_off_handler_ptr = handlers->system_off;
    thread_system_reset_handler_ptr = handlers->system_reset;
}



    而调用init_handlers函数时传入的参数——
    handlers的内容如下：




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 391

    static const struct thread_handlers handlers = {
      .std_smc = tee_entry_std,
      .fast_smc = tee_entry_fast,
      .nintr = main_fiq,
      .cpu_on = cpu_on_handler,
      .cpu_off = pm_do_nothing,
      .cpu_suspend = pm_do_nothing,
      .cpu_resume = pm_do_nothing,
      .system_off = pm_do_nothing,
      .system_reset = pm_do_nothing,
    };



      当在ARMv7或ARMv8中产生了FIQ事件后，
        将
会调用main_fiq函数来处理FIQ事件。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 392

12.6 ARMv7 Monitor对FIQ事件的处理

   当在Monitor模式下出现了FIQ事件时，系统会
从MVBAR寄存器中获取到异常向量表的基地址，
并查找到FIQ事件的处理函数——sm_fiq_entry。该
函数即为Monitor模式下对FIQ事件的处理函数，
Monitor模式下对FIQ的处理过程如图12-4所示。










    图12-4   ARMv7中Monitor模式对FIQ事件的处理流
        程

    sm_fiq_entry函数内容如下：

    LOCAL_FUNC sm_fiq_entry , :
    UNWIND( .fnstart)

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 393

UNWIND( .cantunwind)
sub lr, lr, #4     //记录返回地址
srsdb  sp!, #CPSR_MODE_MON     //保存sp
push {r0-r7}      //将寄存器r0~r7压入栈
clrex        //清空状态
/* 将栈指针切换到Secure World使用的栈 */
sub sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
read_scr r1      //读取SCR寄存器
bic r1, r1, #(SCR_NS | SCR_FIQ)  //清空NS位和FIQ事件位
write_scr r1      //将修改后的值重新写入SCR寄存器
add r0, sp, #SM_CTX_NSEC      //获取Normal World的栈地址
bl      sm_save_modes_regs  //保存Normal World的运行上下文
stm r0!, {r8-r12}
/* 获取FIQ事件处理函数的入口地址 */
ldr r0, =(thread_vector_table + THREAD_VECTOR_TABLE_FIQ_ENTRY)
str r0, [sp, #(SM_CTX_SEC + SM_SEC_CTX_MON_LR)]
/* 保存Secure World的运行上下文,并进行FIQ事件的处理 */
add r0, sp, #SM_CTX_SEC
bl     sm_restore_modes_regs
add sp, sp, #(SM_CTX_SEC + SM_SEC_CTX_MON_LR)  //获取SP
rfefd       sp!      //使用SP中的内容返回
UNWIND( .fnend)
END_FUNC sm_fiq_entry



通过调用ldr r0，=
(thread_vector_table+THREAD_VECTOR_TABLE_FIQ_ENTRY)
的值获取到FIQ事件在thread_vector_table向量表中
的地址，
    然后调用该函数来处理FIQ事件。在
ARMv7架构中将会调用vector_fiq_entry函数来处理
FIQ事件。该函数的内容如下：


LOCAL_FUNC vector_fiq_entry , :
UNWIND(  .fnstart)
UNWIND(  .cantunwind)
/* 安全监控模式接收到一个FIQ并获取控制权 */
bl       thread_check_canaries
ldr lr, =thread_nintr_handler_ptr //获取thread_nintr_handler_ptr的地址




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 394

ldr       lr, [lr]
blx       lr      //跳转到thread_nintr_handler_ptr中执行,完成后返回
mov r1, r0      //将返回值保存到rl
ldr r0, =TEESMC_OPTEED_RETURN_FIQ_DONE
smc #0        //触发smc异常切换到Monitor模式
b        .
UNWIND(  .fnend)
END_FUNC vector_fiq_entry



  在上一节中介绍了handle的初始化，
              其中
thread_nintr_handler_ptr会被初始化成main_fiq的地
址，
  故在Monitor模式下产生的FIQ事件最终会被发
送到OP-TEE中，然后调用main_fiq函数来进行处
理。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
          更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 395

12.7 ARMv8 EL3阶段对FIQ事件的处理

     ARMv8架构中通过查看EL3的异常向量可知，
在EL3阶段是通过调用handle_interrupt_exception宏
对FIQ事件进行处理的，最终该宏会将FIQ事件转发
给OP-TEE，由OP-TEE来完成对FIQ事件的处理，
并指定OP-TEE提供的线程向量表中的fiq_entry作为
处理该事件的入口函数。在EL3中对FIQ事件的处
理过程如图12-5所示。
     handle_interrupt_exception宏的内容和解释如
下：


    handle_interrupt_exception宏的内容和解释如下：
    .macro handle_interrupt_exception label
    /* 使能Serror中断*/
    msr daifclr, #DAIF_ABT_BIT
    str x30, [sp, #CTX_GPREGS_OFFSET + CTX_GPREG_LR]
    bl     save_gp_registers
    /* 保存EL3系统寄存器以备从中断返回时使用 */
    mrs x0, spsr_el3
    mrs x1, elr_el3
    stp x0, x1, [sp, #CTX_EL3STATE_OFFSET + CTX_SPSR_EL3]
    /* 切换到运行栈 */
    ldr x2, [sp, #CTX_EL3STATE_OFFSET + CTX_RUNTIME_SP]
    mov x20, sp
    msr spsel, #0
    mov sp, x2
    /* 判定中断是否有效 */
    bl     plat_ic_get_pending_interrupt_type //判定当前中断是否有效
    cmp x0, #INTR_TYPE_INVAL  //对比plat_ic_get_pending_interrupt_type返回值
    b.eq interrupt_exit_\label //如果当前中断是无效中断,则进入到interrupt_exit
    /* 获取当前中断类型对应的中断处理函数 */



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 396

bl get_interrupt_type_handler  //根据中断类型找到对应的中断处理函数地址
//判定返回值,如果为x0为0证明没有找到handle跳出处理
cbz x0, interrupt_exit_\label
mov x21, x0      //将找到的handle地址赋值给x21
mov x0, #INTR_ID_UNAVAILABLE   //初始化x0的值
/* 设定安全态flag作为参数 */
mrs x2, scr_el3      //将SCR寄出去的值读取到x2中
ubfx      x1, x2, #0, #1      //设定安全态flag
mov x2, x20      //将栈信息地址保存在x2中
mov x3, xzr
blr x21        //跳转到当前中断对应的中断处理函数中对该中断进行处理
interrupt_exit_\label:
b  el3_exit        //退出EL3
.endm










图12-5 ARMv8中EL3对FIQ事件的处理流程
中断处理过程会调用get_interrupt_type_handler
函数来获取FIQ的handler，
    该函数的内容如下：



interrupt_type_handler_t get_interrupt_type_handler(uint32_t type)



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 397

    {
     /* 判定type值是否有效 */
     if (validate_interrupt_type(type))
     return NULL;
     /* 返回保存在intr_type_descs数组变量中type的handler */
     return intr_type_descs[type].handler;
    }



      intr_type_descs变量会在ATF启动过程中通过调
用register_interrupt_type_handler函数来进行赋值，
不同的平台调用该中断注册函数的参数可能不同，
对于OP-TEE而言其调用代码如下：


    rc = register_interrupt_type_handler(INTR_TYPE_S_EL1,opteed_sel1_interrupt_handler,flags)



    在EL3中产生FIQ之后将会调用
    opteed_sel1_interrupt_handler函数来对该FIQ事件进
    行处理。该函数内容如下：



    static uint64_t opteed_sel1_interrupt_handler(uint32_t id,
                        uint32_t flags,
                        void *handle,
                        void *cookie)
    {
     uint32_t linear_id;
     optee_context_t *optee_ctx;
     /* 检查产生中断时的安全态 */
     assert(get_interrupt_src_ss(flags) == NON_SECURE);
     /* 检查传入的上下文 */
     assert(handle == cm_get_context(NON_SECURE));
     /* 保存Normal World的运行上下文 */
     cm_el1_sysregs_context_save(NON_SECURE);
     /* 获取OP-TEE的运行上下文 */
     linear_id = plat_my_core_pos();



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 398

 optee_ctx = &opteed_sp_context[linear_id];
 assert(&optee_ctx->cpu_ctx == cm_get_context(SECURE));
 /* 设置在OP-TEE中处理FIQ事件的入口函数 */
 cm_set_elr_el3(SECURE, (uint64_t)&optee_vectors->fiq_entry);
 cm_el1_sysregs_context_restore(SECURE); //恢复OP-TEE的运行上下文
 cm_set_next_eret_context(SECURE);
 //返回设定好的OP-TEE上下文的运行地址
 SMC_RET1(&optee_ctx->cpu_ctx, read_elr_el3());
}


当调用opteed_sel1_interrupt_handler函数并返回
CPU运行上下文的地址后，
handler_interrupt_exception函数会执行b el3_exit退
出EL3，使用获取到的CPU运行上下文进入OP-TEE
中对FIQ事件进行处理。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 399

12.8 OP-TEE对FIQ事件的处理

   OP-TEE启动时会调用thread_init_vbar函数来完
成安全世界状态（SWS）的中断向量表的初始化，
且在GIC中配置FIQ在安全世界状态时才有效。所
以在安全世界状态中产生了FIQ事件时，CPU将直
接通过VBAR寄存器查找到中断向量表的基地址，
并命中FIQ的处理函数。整个处理过程如图12-6所
示。









    图12-6 OP-TEE处理FIQ事件的流程
   GICv3会调用foreign_intr_handler函数，而对于
GICv2则会调用native_intr_handler。对于AArch32将
会调用thread_nintr_handler_ptr对FIQ事件进行处
理，而对于AArch64则会调用elx_fiq对FIQ事件进行
处理。以GICv2和AArch32为例，native_intr_hanler

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 400

    函数的内容如下：


    .macro native_intr_handler mode:req
    sub      lr, lr, #4
    .ifc     \mode\(),fiq
    push     {r0-r3, r8-r12, lr}
    .else
    push     {r0-r3, lr}
    .endif
    bl     thread_check_canaries        //检查栈空间是否被破坏
    ldr lr, =thread_nintr_handler_ptr   //加载FIQ处理函数的地址到lr寄存器中
    ldr lr, [lr]
    blx lr   //跳转到thread_nintr_handler_ptr函数执行
    .ifc     \mode\(),fiq
    pop {r0-r3, r8-r12, lr}
    .else
    pop {r0-r3, lr}
    .endif
    movs     pc, lr
    .endm



      在OP-TEE中产生的FIQ事件与在Monitor或EL3
中产生的FIQ事件一样，都使用main_fiq函数对FIQ
事件进行处理。main_fiq函数需要根据不同的板级
需求以及FIQ事件类型进行实际的编写和处理。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 401

12.9 OP-TEE对IRQ事件的处理

  IRQ事件的处理一般会用在REE侧。但当ARM
核处于安全世界状态时，系统产生了IRQ事件，而
该事件又不能被暴力的作为无用事件而轻易丢弃，
系统还是需要响应并执行相关操作的。针对该情况
的处理方式和逻辑如图12-7所示。










    图12-7 OP-TEE对IRQ事件的处理过程

    在系统初始化时，系统会调用thread_init_vbar


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 402

函数来初始化安全世界状态的中断向量表并将中断
向量的基地址保存到VBAR寄存器中。当系统在
ARM核处于安全世界状态中产生IRQ事件时，
        系统
通过VBAR寄存器获取到中断向量表的基地址，然
后查找到IRQ对应的中断处理函数——
thread_irq_handler，使用该函数处理IRQ事件，整
个处理过程的流程如图12-8所示。
      在GICV2且为AArch32时，
        将调用
foreign_intr_handler宏处理IRQ事件，
        该宏的内容如
下：



.macro foreign_intr_handler mode:req
    .ifc     \mode\(),irq     //判定传入的参数是irq还是fiq
    cpsid    f
    .endif
    sub lr, lr, #4
    push     {lr}
    push     {r12}
    .ifc     \mode\(),fiq
    bl  thread_save_state_fiq
    .else
    bl  thread_save_state     //保存当前状态
    .endif
    mov r0, #THREAD_FLAGS_EXIT_ON_FOREIGN_INTR
    mrs r1, spsr
    pop {r12}
    pop {r2}
    blx thread_state_suspend      //挂起当前系统中线程
    mov r4, r0
    mov r0, sp
    cps #CPSR_MODE_SVC      //切换到SVC模式
    mov sp, r0  //保存栈信息

    ldr r0, =TEESMC_OPTEED_RETURN_CALL_DONE
    ldr r1, =OPTEE_SMC_RETURN_RPC_FOREIGN_INTR



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 403

    mov r2, #0
    mov r3, #0
    smc #0 //调用smc触发smc事件,将CPU状态切换到Monitor执行进一步的处理
    b        .
  .endm










    图12-8 OP-TEE处理IRQ事件的流程
   OP-TEE接收到IRQ事件后，ARMv7架构中会
通过切换到Monitor模式将该IRQ事件发送到REE侧
进行处理，ARMv8架构中IRQ中断事件会通过切换
到EL3将该IRQ事件发送到REE侧进行处理。
   OP-TEE接收IRQ事件后会触发安全监控模式调
用（smc），在ARMv7中将会进入安全监控模式调
用（smc）的处理过程，即进入sm_smc_entry函数
中进行处理，该函数的内容和介绍如下：


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 404

LOCAL_FUNC sm_smc_entry , :
UNWIND(  .fnstart)
UNWIND(  .cantunwind)
srsdb    sp!, #CPSR_MODE_MON
push {r0-r7}         //将r0~r7入栈
clrex        /* 清空状态 */
read_scr r1 //读取SCR寄存器中的值到r1寄存器中
tst r1, #SCR_NS //判定SCR寄存器中的NS位为0
bne .smc_from_nsec   //如果NS不为0,则表示该smc来自正常世界状态
sub sp, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0) //获取安全世界状态的上下文栈
/* 保存安全世界状态的上下文 */
add r0, sp, #SM_CTX_SEC
bl       sm_save_modes_regs
/* 配置好传递到正常世界状态的参数 */
add r8, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0)
ldm r8, {r0-r4}
mov_imm           r9, TEESMC_OPTEED_RETURN_FIQ_DONE
cmp r0, r9
addne             r8, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
stmne             r8, {r1-r4}
/* 加载正常世界状态的上下文 */
add r0, sp, #SM_CTX_NSEC
bl       sm_restore_modes_regs
/* 返回到非安全世界状态 */
.sm_ret_to_nsec:
add      r0, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R8)
ldm r0, {r8-r12}
/* 更新 SCR */
read_scr r0
orr r0, r0, #(SCR_NS | SCR_FIQ) /* Set NS and FIQ bit in SCR */
write_scr r0
add sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
b        .sm_exit    //退出smc操作,切换到正常世界状态
.smc_from_nsec:
sub sp, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R0)
bic r1, r1, #(SCR_NS | SCR_FIQ) /* 清空SCR寄存器中的NS位和FIQ位 */
write_scr r1
add r0, sp, #(SM_CTX_NSEC + SM_NSEC_CTX_R8)
stm r0, {r8-r12}
mov r0, sp
bl       sm_from_nsec
cmp r0, #0
beq .sm_ret_to_nsec
add sp, sp, #(SM_CTX_SEC + SM_SEC_CTX_R0)




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 405

.sm_exit:
    pop {r0-r7}
rfefd       sp!
UNWIND( .fnend)
END_FUNC sm_smc_entry

当Monitor模式将IRQ事件传递到正常世界状态
后，Linux将根据具体得到的参数执行对该IRQ事件
的具体处理。完成对IRQ事件的处理后，会触发安
全监控模式调用重新切回到Monitor态，然后恢复安
全世界状态中被中断的线程的状态继续执行。对于
ARMv8，该部分的处理逻辑类似，在此不再赘述，
详细部分可查看ATF中bl31部分的代码。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 406

12.10　小结

ARMv7架构中安全世界状态包含Monitor模式
和OP-TEE，而在ARMv8架构中安全世界状态则包
含EL3阶段和OP-TEE。Monitor模式或EL3阶段对
FIQ的处理都是通过调用OP-TEE在初始化时赋值的
处理函数来实现的。对于ARMv7，该处理函数的指
针最终会被Monitor模式下运行的代码用来处理FIQ
中断事件，而对于ARMv8，该处理函数的地址会被
返回给ATF的bl31，当在EL3中接收到FIQ事件时，
EL3会使用该处理函数来处理该FIQ事件。FIQ的处
理都是通过调用OP-TEE中的main_fiq函数来完成
的，由于CPU和板级配置不同，该函数的实现也各
不相同。在OP-TEE中接收到IRQ事件时，  OP-TEE
会将IRQ中断事件转发给Monitor模式或EL3进行处
理，Monitor模式或者EL3最终会将IRQ事件发送到
REE侧，REE侧处理完该IRQ事件后会触发安全监
控模式调用恢复到安全世界状态中继续执行。








https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 407

第13章　OP-TEE对TA操作的各种实现

  当在REE侧执行CA时，OP-TEE中的
tee_entry_std函数会根据CA调用libteec库文件中不
同的接口而采取不同的处理方式，这些操作包括打
开会话、关闭会话、调用TA中的命令、取消对TA
中命令的调用。OP-TEE中存在动态和静态两种
TA，本章将详细介绍OP-TEE对这两种TA操作的具
体实现。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 408

13.1　创建会话在OP-TEE中的实现

                                           会话是CA调用TA中具体命令的基础，如果CA
与TA之间没有建立会话，CA就无法调用TA中的任
何命令。在CA中通过调用libteec库文件中的
TEEC_OpenSession函数来建议CA与特定TA之间的
会话，该函数执行时会调用OP-TEE驱动中的
optee_open_session函数发送标准安全监控模式调用
（std smc）请求，通知OP-TEE开始执行创建会话
的操作。该标准安全监控模式调用会被Monitor模式
（ARMv7）或者EL3阶段（ARMv8）处理后转发给
OP-TEE，OP-TEE调用entry_open_session函数来完
成创建会话的操作。在OP-TEE中一次完整的创建
会话操作的流程如图13-1所示。
                                         OP-TEE支持动态TA和静态TA。静态TA镜像
将与OP-TEE镜像编译在同一个镜像文件中，因此
静态TA镜像会存放在OP-TEE镜像的特定区段中，
静态TA在OP-TEE启动时会被加载到属性为
MEM_AREA_TA_RAM的安全内存中。动态TA则
是将TA镜像文件保存到文件系统中，在创建会话
时OP-TEE通过发送RPC请求将动态TA镜像加载到
OP-TEE的安全内存中。创建会话在OP-TEE中的操
作是根据TA对应的UUID值找到对应的TA镜像，读
取TA镜像文件的头部数据，并将相关数据保存到

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 409

tee_ta_ctx结构体变量中，然后将填充好的tee_ta_ctx
结构体变量保存到tee_ctxes链表中，以便后期CA执
行调用TA命令操作时可通过查找tee_ctxes链表来获
取对应的会话。最后根据会话的内容进入到指定的
TA，根据需要被调用的命令的ID执行特定的操
作。关于TA镜像的加载过程将会在后续章节中详
解介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 410

图13-1 OP-TEE中创建会话操作的实现流程







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 411

13.1.1　静态TA的创建会话操作

  静态TA是与OP-TEE OS镜像编译在一起的，
在OP-TEE的启动阶段，静态TA镜像的内容会被加
载到OP-TEE的安全内存中，且在启动过程中会调
用verify_pseudo_tas_conformance函数对所有的静态
TA镜像的内容进行检查。

  调用创建会话操作后，OP-TEE首先会在已经
被创建的会话链表中查找是否有匹配的会话存在。
如果找到则将该会话的ID直接返回给REE侧，如果
没有找到则会根据UUID去静态TA的段中进行查
找，然后将找到的静态TA的相关信息填充到
tee_ta_ctx结构体变量中，再将该变量添加到全局的
tee_ctxes链表中，并调用静态TA的
enter_open_session函数执行创建会话操作。静态TA
创建会话的操作全过程如图13-2所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 412

    图13-2　静态TA的创建会话操作流程
1.根据UUID找到对应静态TA

  如果CA调用的是静态TA，OP-TEE会到存放静
态TA的ta_head区域通过遍历的方式，对比内存中
静态TA区域中TA的UUID与需要调用的TA的UUID
值是否相等找到需要被调用的静态TA，这些操作

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 413

是通过调用tee_ta_init_pseudo_ta_session函数来实现
的。查找到需要被调用的静态TA后，
                        该函数会将
pseudo_ta_ops变量的地址赋值到TA的上下文中，
    该
函数的内容如下：



TEE_Result tee_ta_init_pseudo_ta_session(const TEE_UUID *uuid,
        struct tee_ta_session *s)
{
 struct pseudo_ta_ctx *stc = NULL;
 struct tee_ta_ctx *ctx;
 const struct pseudo_ta_head *ta;
 DMSG(" Lookup for pseudo TA %pUl", (void *)uuid);

 /* 获取静态TA的head的起始地址 */
 ta = &__start_ta_head_section;
 /* 进入到loop循环,遍历整个段,根据UUID是否匹配来判定在静态TA的head段中是否有相应的TA */
 while (true) {
  if (ta >= &__stop_ta_head_section)
      return TEE_ERROR_ITEM_NOT_FOUND;
  if (memcmp(&ta->uuid, uuid, sizeof(TEE_UUID)) == 0)
      break;
  ta++;
 }
 /* 分配存放pseudo_ta_ctx结构体变量的内存空间 */
 stc = calloc(1, sizeof(struct pseudo_ta_ctx));
 if (!stc)
  return TEE_ERROR_OUT_OF_MEMORY;
 ctx = &stc->ctx;
 /* 填充数据,组合ctx变量*/
 ctx->ref_count = 1;
 s->ctx = ctx;
 ctx->flags = ta->flags;
 stc->pseudo_ta = ta;        //设定ta context的内容
 ctx->uuid = ta->uuid;       //设定该context中的UUID为找到的静态TA的UUID
 ctx->ops = &pseudo_ta_ops;      //执行该context的operation变量
 //将context插入到全局context链表中
 TAILQ_INSERT_TAIL(&tee_ctxes, ctx, link);
 DMSG("   %s : %pUl", stc->pseudo_ta->name, (void *)&ctx->uuid);
 return TEE_SUCCESS;
}




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 414

 __start_ta_head_section到
__stop_ta_head_section区域之间保存的是所有静态
TA的ta_head数据。在编译各静态TA时，通过使用
pseudo_ta_register宏将各静态TA的ta_head数据保存
到ta_head_section段中，该段的起始地址是
__start_ta_head_section，结束地址是
__stop_ta_head_section。
2.pseudo_ta_ops变量
 OP-TEE对所有静态TA的操作接口都保存在
pseudo_ta_ops变量中，该变量的enter_open_session
成员的值为pseudo_ta_enter_open_session，该函数
指针会检查具体TA中的相关函数是否有效并执行
相应的操作，该函数的内容和注释如下：

static TEE_Result pseudo_ta_enter_open_session(struct tee_ta_session *s, struct tee_ta_param *param, TEE_ErrorOrigin *eo)
{
 TEE_Result res = TEE_SUCCESS;
 struct pseudo_ta_ctx *stc = to_pseudo_ta_ctx(s->ctx); //获取TA的上下文
 TEE_Param tee_param[TEE_NUM_PARAMS];
 tee_ta_push_current_session(s);
 *eo = TEE_ORIGIN_TRUSTED_APP;
 /* 检查该静态TA中是否存在create_entry_point接口,如果有则执行 */
 if ((s->ctx->ref_count == 1) && stc->pseudo_ta->create_entry_point) {
  res = stc->pseudo_ta->create_entry_point();
  if (res != TEE_SUCCESS)
  goto out;
 }
 /* 检查该静态TA中是否存在open_session_entry_point接口 */
 if (stc->pseudo_ta->open_session_entry_point) {


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 415

        res = copy_in_param(s, param, tee_param); //复制传入的参数
        if (res != TEE_SUCCESS) {
         *eo = TEE_ORIGIN_TEE;
         goto out;
        }
        /* 执行具体TA的open_session_entry_point操作 */
        res = stc->pseudo_ta->open_session_entry_point(param->types,
                  tee_param,
                  &s->user_ctx);
        update_out_param(tee_param, param); //更新返回数据
     }
    out:
     tee_ta_pop_current_session(); //更新会话链表
     return res;
    }



    3.pseudo_ta_register宏

    在编译过程中，
           该宏将静态TA的ta_head数据
    保存到ta_head_section段中，该宏的定义如下：


    #define pseudo_ta_register(...) static const struct pseudo_ta_head __head \
         __used __section("ta_head_section") = { __VA_ARGS__ }



    一个静态TA的ta_head数据中保存了该静态TA
    的UUID、name、flags，以及初始化该TA操作接口
    的函数指针。
          以提供网络socket服务的静态TA为
    例，使用该宏时的内容如下：



pseudo_ta_register(.uuid = PTA_SOCKET_UUID, .name = "socket",
        .flags = PTA_DEFAULT_FLAGS,
        .open_session_entry_point = pta_socket_open_session,
        .close_session_entry_point = pta_socket_close_session,




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 416

.invoke_command_entry_point = pta_socket_invoke_command);



在该示例中定义了网络socket服务静态TA提供
的创建会话、关闭会话、调用命令的操作实现。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 417

13.1.2　动态TA的创建会话操作

动态的TA镜像存放在REE侧的文件系统中。
CA在执行动态TA的创建会话操作时，OP-TEE会根
据UUID值借助RPC机制让tee_supplicant将动态TA
镜像加载到OP-TEE的内存中，并获取加载到内存
中的动态TA的相关信息，将这些信息填充到
tee_ta_ctx结构体变量中，然后再将该变量添加到全
局的tee_ctxes链表中，以便后续CA端调用该TA中
的命令操作时，可直接根据会话ID值从链表中找到
对应的会话。加载动态TA镜像到OP-TEE中是通过
调用tee_ta_init_user_ta_session函数来实现的，该函
数会调用ta_load函数发送RPC请求从REE侧的文件
系统中加载动态TA镜像到OP-TEE中。在将TA镜像
的内容写入到OP-TEE的内存中之前，OP-TEE会对
该TA镜像中的内容进行电子验签，以确保该TA镜
像的合法性。动态TA的创建会话操作整体过程如
图13-3所示。

          动态TA运行在OP-TEE的用户空间，创建会话
操作最终会切换到用户态，调用到具体动态TA的
创建会话接口函数TA_OpenSessionEntryPoint。
1.动态TA的加载


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 418

      动态TA的镜像文件被保存在REE侧的文件系统
中。在第一次执行创建会话操作时首先需要将REE
侧的动态TA镜像文件加载到OP-TEE中，并初始化
该TA的运行上下文。这些操作是通过调用
tee_ta_init_user_ta_session函数来实现的，
        该函数内
容和注释如下：



    TEE_Result tee_ta_init_user_ta_session(const TEE_UUID *uuid,
     struct tee_ta_session *s)
    {
     TEE_Result res;
     /* 判定用于加载动态TA镜像所用的操作函数指针变量是否存在 */
     if (!user_ta_store)
return TEE_ERROR_ITEM_NOT_FOUND;
     DMSG("Load user TA %pUl", (void *)uuid);
     /* 开始调用ta_load函数正式加载动态静态TA文件 */
     res = ta_load(uuid, user_ta_store, &s->ctx);
     /* 判定加载结果 */
     if (res == TEE_SUCCESS)
     s->ctx->ops = &user_ta_ops;  //赋值该context的operation
     return res;
    }



    关于动态TA加载过程和原理将在后续章节中
    详细介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 419

      图13-3　动态TA的创建会话操作流程

    user_ta_ops变量用于保存在OP-TEE内核空间中
操作动态TA的接口函数的指针，其内容如下：


    static const struct tee_ta_ops user_ta_ops __rodata_unpaged = {
    // 对动态TA的创建会话操作接口
    .enter_open_session = user_ta_enter_open_session,
    .enter_invoke_cmd = user_ta_enter_invoke_cmd, // 对动态TA的调命令操作接口
    // 对动态TA的关闭会话操作接口



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 420

      .enter_close_session = user_ta_enter_close_session,
      .dump_state = user_ta_dump_state, // 对动态TA的dump出状态的操作接口
      .destroy = user_ta_ctx_destroy, // 销毁TA运行上下文的操作接口
      .get_instance_id = user_ta_get_instance_id, // 获取动态TA实体ID的接口
    };

当动态TA被加载到OP-TEE中后，OP-TEE会调
    用user_ta_ops中的enter_open_session成员变量所指
    向的函数进一步处理CA创建会话的请求。

    2.OP-TEE内核空间对创建会话的处理
      在创建CA与动态TA的会话过程中，
    tee_ta_open_session函数会调用ctx->ops-
    >enter_open_session接口，其对应的是user_ta_ops变
    量中的enter_open_session成员所指向的函数，该成
    员的值指向user_ta_enter_open_session函数。
    user_ta_enter_open_session通过调用user_ta_enter函
    数来处理创建会话的操作，建立内存映射后会进入
    OP-TEE的用户空间去执行，user_ta_enter函数的内
    容和注释如下：

    static TEE_Result user_ta_enter(TEE_ErrorOrigin *err,
      struct tee_ta_session *session,
      enum utee_entry_func func, uint32_t cmd,
      struct tee_ta_param *param)
    {
      TEE_Result res;
      struct utee_params *usr_params;
      uaddr_t usr_stack;
      struct user_ta_ctx *utc = to_user_ta_ctx(session->ctx);


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 421

 TEE_ErrorOrigin serr = TEE_ORIGIN_TEE;
 struct tee_ta_session *s __maybe_unused;
 void *param_va[TEE_NUM_PARAMS] = { NULL };
 if (!(utc->ctx.flags & TA_FLAG_EXEC_DDR))
  panic("TA does not exec in DDR");
 /* 建立参数的用户空间地址映射 */
 res = tee_mmu_map_param(utc, param, param_va);
 if (res != TEE_SUCCESS)
  goto cleanup_return;
 tee_ta_push_current_session(session);
 /* 将用户参数保存在栈顶 */
 usr_stack = (uaddr_t)utc->mmu->regions[0].va + utc->mobj_stack->size;
 usr_stack -= ROUNDUP(sizeof(struct utee_params), STACK_ALIGNMENT);
 usr_params = (struct utee_params *)usr_stack;
 init_utee_param(usr_params, param, param_va);
 /* 切换到用户空间开始执行entry_func指向的函数的cmd分支 */
 res = thread_enter_user_mode(func, tee_svc_kaddr_to_uref(session),
               (vaddr_t)usr_params, cmd, usr_stack,
               utc->entry_func, utc->is_32bit,
               &utc->ctx.panicked, &utc->ctx.panic_code);
 clear_vfp_state(utc);
 serr = TEE_ORIGIN_TRUSTED_APP;
 if (utc->ctx.panicked) {
  DMSG("tee_user_ta_enter: TA panicked with code 0x%x\n",
  utc->ctx.panic_code);
  serr = TEE_ORIGIN_TEE;
  res = TEE_ERROR_TARGET_DEAD;
 }
 /* 复制用户空间返回的数据到param中 */
 update_from_utee_param(param, usr_params);
 s = tee_ta_pop_current_session();
 assert(s == session);
cleanup_return:
 session->cancel = false;
 *err = serr;
 return res;
}



3.切换到用户空间的实现

调用thread_enter_user_mode函数会进入到OP-




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 422

TEE的用户空间。调用该函数时会指定切换到用户
空间后的起始运行函数的地址。在OP-TEE中该值
被设置成ta_head->entry.ptr64，entry.prt64在
user_ta_header.c文件中被赋值为__utee_entry，即当
切换到用户空间后，系统将会执行__utee_entry函
数，那如何实现从OP-TEE的内核态切换到OP-TEE
的用户态呢？OP-TEE中是通过调用
__thread_enter_user_mode函数来实现的，该函数在
AArch32中的内容如下：


FUNC __thread_enter_user_mode , :
UNWIND(.fnstart)
UNWIND(.cantunwind)
   push {r4-r12,lr} //将r4~r12和lr寄存器中的值入栈
    ldr    r4, [sp, #(10 * 0x4)]     /* 将用户态的栈地址保存到r4中 */
    ldr    r5, [sp, #(11 * 0x4)]     /* 将切换到用户态的入口函数地址保存在r5中 */
    ldr    r6, [sp, #(12 * 0x4)]     /* 将传入的spsr数据保存在r6中 */
    msr    spsr_cxsf, r6 /* 将r6中保存的新的spsr的值填入spsr寄存器 */
    cps #CPSR_MODE_SYS //进入SYS模式
    mov r6, sp        //将sp的值保存到r6中
    mov    sp, r4      //将用户态的栈地址保存到sp中
    cps #CPSR_MODE_SVC //进入svc模式
    push   {r6,r7}     //将r6和r7入栈
    mov    lr, #0      //将lr寄存器中的值设置成0,表示无需返回
    movs   pc, r5      //重新设定pc指针指向入口函数
    UNWIND(.fnend)
    END_FUNC __thread_enter_user_mode


     切换到用户态后，系统将执行pc指针指向的函
数，该函数会被赋值成entry.prt64的值，在用户空
间调用__utee_entry继续执行。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
           更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 423

4.用户空间的entry_open_session函数
      当系统切换到OP-TEE的用户态后，会进入
__utee_entry函数执行，该函数中会根据命令ID调用
用户空间中的entry_open_session函数来执行特定TA
中的创建会话接口的内容，该函数的内容和注释如
下：



    static TEE_Result entry_open_session(unsigned long session_id,
     struct utee_params *up)
    {
     TEE_Result res;
     struct ta_session *session;
     uint32_t param_types;
     TEE_Param params[TEE_NUM_PARAMS];
     /* 将该具体TA的session添加到ta_session链表中 */
     res = ta_header_add_session(session_id);
     if (res != TEE_SUCCESS)
     return res;
     /* 根据session id从ta_session链表中获取该session的内容 */
     session = ta_header_get_session(session_id);
     if (!session)
     return TEE_ERROR_BAD_STATE;
     /* 获取从内核空间传递上来的参数 */
     __utee_to_param(params, &param_types, up);
     /* 保存参数的内容到全局变量中 */
     ta_header_save_params(param_types, params);
     /* 调用具体TA中定义的TA_OpenSessionEntryPoint函数 */
     res = TA_OpenSessionEntryPoint(param_types, params,
         &session->session_ctx);
     /* 参数返回 */
     __utee_from_param(up, param_types, params);
     /* 如果执行不成功则删除该session */
     if (res != TEE_SUCCESS)
     ta_header_remove_session(session_id);
     return res;
    }






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 424

待执行完具体的动态TA中的
TA_OpenSessionEntryPoint函数后，动态TA的创建
会话操作也就完成，在CA端可使用返回的会话ID
通过调用命令的接口来调用该动态TA中的具体命
令去执行特定的操作。

5.用户空间返回到内核空间

待entry_open_session执行完并返回到
__utee_entry后，__utee_entry函数将会调用
utee_return函数，通过系统调用的方式返回到OP-
TEE的内核空间。该返回操作最终会调用
syscall_sys_return函数来实现。从用户空间切换回
到内核空间的过程如图13-4所示。
                                 thread_unwind_user_mode函数主要是将寄存器
的状态恢复到切换到用户空间之前的状态，该函数
的内容如下：

FUNC thread_unwind_user_mode , :
UNWIND(.fnstart)
UNWIND(.cantunwind)
ldr        ip, [sp, #(15 * 0x4)]
str r1, [ip]
ldr        ip, [sp, #(16 * 0x4)]
str r2, [ip]
/* 恢复切换之前的寄存器状态 */
pop {r4,r7}
cps #CPSR_MODE_SYS
mov sp, r4
cps #CPSR_MODE_SVC

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 425

/* 将pc指针以及寄存器的值出栈,下一条执行就会跳转到切换之前的位置*/
pop {r4-r12,pc}
UNWIND(.fnend)
END_FUNC thread_unwind_user_mode










图13-4 OP-TEE中用户空间进入内核空间的流程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 426

13.2　调用TA命令操作在OP-TEE中的实现

REE侧的CA执行创建会话操作成功后，CA就
可使用获取到的会话ID和命令ID调用
TEEC_InvokeCommand接口来让TA执行特定的命
令。在CA中调用TEEC_InvokeCommand接口时，
该函数会将会话ID、命令ID，以及需要传递给TA
的参数信息通过ioctl的系统调用发送到OP-TEE的驱
动中，OP-TEE驱动会调用optee_invoke_func函数将
需要传递给TA的参数信息保存在共享内存中，并
触发安全监控模式调用（smc）切换到Monitor模式
（ARMv7）或EL3（ARMv8）中进行安全世界状态
的处理。调用TA命令触发的安全监控模式调用最
终会被作为标准安全监控模式调用进行解析，并建
立一个专门的线程进入thread_std_smc_entry函数去
执行，线程运行到tee_entry_std函数时会对安全监
控模式调用（smc）进行判定，并进入调用TA命令
的分支。调用TA命令的操作在OP-TEE中的执行流
程如图13-5所示。







https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 427

  图13-5 OP-TEE中调用TA命令操作的实现流程
      根据会话ID获取到已经创建的会话内容后，
OP-TEE会调用tee_ta_invoke_command函数开始对
调用TA命令的操作请求进行处理，
        该函数的内容
如下：



    TEE_Result tee_ta_invoke_command(TEE_ErrorOrigin *err,
     struct tee_ta_session *sess,
     const TEE_Identity *clnt_id,
     uint32_t cancel_req_to, uint32_t cmd,
     struct tee_ta_param *param)
    {
     TEE_Result res;




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 428

 /* 参数检查 */
 if (check_client(sess, clnt_id) != TEE_SUCCESS)
  return TEE_ERROR_BAD_PARAMETERS;
 if (!check_params(sess, param))
  return TEE_ERROR_BAD_PARAMETERS;
 if (sess->ctx->panicked) {
  DMSG("   Panicked !");
  *err = TEE_ORIGIN_TEE;
  return TEE_ERROR_TARGET_DEAD;
 }
 /* 设定会话的状态 */
 tee_ta_set_busy(sess->ctx);
 /* 设定调用超时限制 */
 set_invoke_timeout(sess, cancel_req_to);
 /* 进入OP-TEE的用户空间运行 */
 res = sess->ctx->ops->enter_invoke_cmd(sess, cmd, param, err);
 if (sess->ctx->panicked) {
  *err = TEE_ORIGIN_TEE;
  res = TEE_ERROR_TARGET_DEAD;
 }
 /* 清空会话的运行状态 */
 tee_ta_clear_busy(sess->ctx);
 if (res != TEE_SUCCESS)
  DMSG("    => Error: %x of %d\n", res, *err);
 return res;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 429

13.2.1　静态TA的调用命令操作的实现

  静态的TA运行于OP-TEE的内核空间。TEE通
过从CA传来的会话ID获取需要被调用的静态TA的
上下文，然后从上下文中获取该静态TA提供的
invoke_command_entry_point接口。
invoke_command_entry_point对应的函数会根据不同
的命令ID执行相应的操作，并将执行结果返回给
CA。静态TA的调用命令操作的整个操作过程如图
13-6所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 430

      图13-6　静态TA的调用命令操作实现流程
      在对静态的TA执行创建会话操作时会将该TA
的运行上下文中的ctx->ops变量赋值成
pseudo_ta_ops，故调用ss->ctx->ops-
>enter_invoke_cmd就会调用
pseudo_ta_enter_invoke_cmd函数。该函数的内容和
注释如下：



    static TEE_Result pseudo_ta_enter_invoke_cmd(struct tee_ta_session *s,
        uint32_t cmd, struct tee_ta_param *param,
        TEE_ErrorOrigin *eo)
    {
     TEE_Result res;
     //获取该静态TA的上下文
     struct pseudo_ta_ctx *stc = to_pseudo_ta_ctx(s->ctx);
     TEE_Param tee_param[TEE_NUM_PARAMS];
     tee_ta_push_current_session(s); //设定该静态TA的栈空间被使用
     res = copy_in_param(s, param, tee_param); //复制从REE发送过来的参数内容
     /* 判定复制是否成功 */
     if (res != TEE_SUCCESS) {
        *eo = TEE_ORIGIN_TEE;
        goto out;
     }
     *eo = TEE_ORIGIN_TRUSTED_APP;
     /* 调用该静态TA提供的invoke_command函数,根据不同的command ID执行特定的操作 */
     res = stc->pseudo_ta->invoke_command_entry_point(s->user_ctx, cmd,
                    param->types,
                    tee_param);
     /* 更新输出结果到buffer中 */
     update_out_param(tee_param, param);
    out:
     tee_ta_pop_current_session();//设定该静态TA栈空间可用
     return res;
    }







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 431

13.2.2　动态TA的调用命令操作实现

                                       动态TA运行在OP-TEE的用户空间，OP-TEE通
过从CA传来的会话ID找到对应动态TA，并获取该
动态TA的运行上下文，然后调用sess->ctx->ops成
员中的调用命令的方法，即
user_ta_enter_invoke_cmd函数。这是因为在创建CA
与该动态TA的会话时，sess->ctx->ops被赋值成
user_ta_ops，该变量中的enter_invoke_cmd成员指向
的就是user_ta_enter_invoke_cmd函数。
user_ta_enter_invoke_cmd函数会执行运行空间的切
换操作，关于如何从OP-TEE的内核空间进入OP-
TEE的用户空间，可参阅13.1.2节“用户空间的
entry_open_session函数”部分。动态TA的调用命令
的整个操作过程如图13-7所示。

 当系统运行于OP-TEE的用户空间后，会调用
用户空间的entry_invoke_command函数执行调用命
令的操作。用户空间的entry_invoke_command函数
定义在optee_os/lib/libutee/arch/arm/user_ta_entry.c文
件中，该函数内容如下：

static TEE_Result entry_invoke_command(unsigned long session_id,
 struct utee_params *up, unsigned long cmd_id)
{
 TEE_Result res;

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 432

 uint32_t param_types;
 TEE_Param params[TEE_NUM_PARAMS];
 struct ta_session *session = ta_header_get_session(session_id);
 if (!session)
 return TEE_ERROR_BAD_STATE;
 /* 检查传入到用户空间的参数是否合法 */
 __utee_to_param(params, ?m_types, up);
 ta_header_save_params(param_types, params);
 /* 调用TA的TA_InvokeCommandEntryPoint函数 */
 res = TA_InvokeCommandEntryPoint(session->session_ctx, cmd_id,
     param_types, params);
 __utee_from_param(up, param_types, params);
 return res;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 433

图13-7　动态TA的Invoke Command操作的实现流
        程

  OP-TEE调用用户空间的entry_invoke_command
函数时，创建的线程就已进入到TA镜像的上下文
中运行了，当调用TA_InvokeCommandEntryPoint函
数时就会去执行TA镜像中定义的
TA_InvokeCommandEntryPoint函数，该函数具体会
执行什么操作就由具体的TA决定，一般是根据命
令id执行定义好的操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 434

13.3　关闭会话操作在OP-TEE中的实现

 CA端通过调用libteec库文件中关闭会话的接口
通知OP-TEE执行关闭会话的操作。该操作的作用
是让OP-TEE释放建立的会话的相关资源，并将该
会话从全局的会话链表中删除。OP-TEE实现关闭
会话操作的流程如图13-8所示。

             实现关闭会话的操作过程中，在将会话从全局
会话队列tee_open_session链表删除之前，需要先执
行TA中的关闭会话接口中的操作，这是因为TA可
能在创建会话时分配了一些资源，如果在释放这些
资源之前就将该会话从链表中移除，这些分配的资
源将无法被释放，这样会造成内存泄漏或者其他问
题。tee_ta_close_session函数是执行关闭会话的主
要函数，大多数资源的释放操作都是在该函数中完
成的，该函数的内容如下：










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 435

 图13-8 OP-TEE中关闭会话操作的实现流程

TEE_Result tee_ta_close_session(struct tee_ta_session *csess,
             struct tee_ta_session_head *open_sessions,
             const TEE_Identity *clnt_id)
{
 struct tee_ta_session *sess;
 struct tee_ta_ctx *ctx;
 bool keep_alive;
 DMSG("tee_ta_close_session(0x%" PRIxVA ")", (vaddr_t)csess);
 if (!csess)
  return TEE_ERROR_ITEM_NOT_FOUND;
 /* 获取需要被关闭的会话的内容 */
 sess = tee_ta_get_session((vaddr_t)csess, true, open_sessions);
 if (!sess) {
  EMSG("session 0x%" PRIxVA " to be removed is not found",
      (vaddr_t)csess);
  return TEE_ERROR_ITEM_NOT_FOUND;
 }
 /* 检查CA端是否还存在调用 */
 if (check_client(sess, clnt_id) != TEE_SUCCESS) {
  tee_ta_put_session(sess);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 436

  return TEE_ERROR_BAD_PARAMETERS; /* intentional generic error */
 }
 ctx = sess->ctx;
 tee_ta_set_busy(ctx);     //设定当前会话正在被使用
 /* 调用会话对应的TA中的关闭会话操作 */
 if (!ctx->panicked) {
  set_invoke_timeout(sess, TEE_TIMEOUT_INFINITE);
  ctx->ops->enter_close_session(sess);
 }
 /* 将该会话从全局打开的会话链表中删除 */
 tee_ta_unlink_session(sess, open_sessions);
 free(sess);      //释放掉会话占用的内存空间
 tee_ta_clear_busy(ctx);   //清空flag
 mutex_lock(&tee_ta_mutex);
 if (ctx->ref_count <= 0)
  panic();

 ctx->ref_count--;
 keep_alive = (ctx->flags & TA_FLAG_INSTANCE_KEEP_ALIVE) &&
      (ctx->flags & TA_FLAG_SINGLE_INSTANCE);
 if (!ctx->ref_count && !keep_alive) {
  DMSG("     ... Destroy TA ctx");
  TAILQ_REMOVE(&tee_ctxes, ctx, link);
  mutex_unlock(&tee_ta_mutex);
  condvar_destroy(&ctx->busy_cv);
  pgt_flush_ctx(ctx);
  ctx->ops->destroy(ctx);
 } else
  mutex_unlock(&tee_ta_mutex);
 return TEE_SUCCESS;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 437

13.3.1　静态TA的关闭会话操作

   关闭与静态TA的会话操作时，OP-TEE会调用
ctx->ops->enter_close_session来执行具体TA的关闭
会话操作。其调用的是
pseudo_ta_enter_close_session函数，该函数会调用
具体静态TA提供的close_session_entry_ponit和
destroy_entry_point指定的接口来释放掉该TA占用
的系统资源。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 438

13.3.2　动态TA的关闭会话操作

  关闭动态TA的会话操作时，OP-TEE会调用
ctx->ops->enter_close_session来执行具体TA的关闭
会话操作，其调用的是user_ta_enter_close_session
函数，该函数的执行过程中会切换到OP-TEE的用
户空间，调用具体动态TA中的
TA_CloseSessionEntryPoint函数，完成动态TA在用
户空间资源的释放，其整体的调用流程类似于动态
TA的创建会话操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 439

13.4　小结

本章介绍了CA端调用libteec库文件中的接口执
行创建会话、关闭会话、调用命令操作时在OP-
TEE中的具体实现和流程。静态TA运行于OP-TEE
的内核空间，动态TA运行于OP-TEE的用户空间。
两种TA在OP-TEE中实现上述操作各有不同，静态
TA的所有操作都在内核空间中完成，动态TA的所
有操作则需要分别在内核空间和用户空间中完成。
关于如何从OP-TEE的内核空间切换到OP-TEE的用
户空间运行在本章中也进行了详细的介绍。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 440

第14章　OP-TEE的内存和缓存管理

  OP-TEE运行于安全内存中，REE侧无法访问
到安全内存和安全缓存（Cache）中的任何数据。
本章将详细介绍OP-TEE中的安全内存以及实现原
理。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 441

14.1　物理内存和缓存数据的硬件安全保护

  ARM核运行时所需的数据主要来自于硬件内
存设备和Cache。支持TrustZone技术后，ARM核运
行态分为安全世界状态（SWA）和正常世界状态
（NWS）。当ARM核处于正常世界状态时，ARM
核无权访问硬件内存设备的安全区域和Cache中的
安全数据。为实现数据的安全隔离，ARM使用
TZASC来保障正常世界状态无法访问到硬件内存设
备的安全区域，对Cache和MMU的扩展保障正常世
界状态无法获取到Cache中的安全数据。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 442

14.1.1　内存设备安全区域的隔离

                                       借助TrustZone技术搭建的TEE方案之所以能够
保障系统的安全是由于TrustZone技术对ARM核和
总线进行了安全扩展，并提供了安全组件（IP）来
实现对系统资源硬件层面的隔离，包括对中断、内
存、片上SRAM、外设等都能实现硬件级别的隔
离。只有当ARM核处于安全世界状态时才有权限访
问安全资源，如果ARM核在正常世界状态中试图去
访问安全资源，会触发数据访问异常
（Segmentation Fault）。对于不同的系统资源，
ARM提供了不同的安全组件来实现对资源的硬件隔
离。对于系统内存（DRAM），ARM使用TZASC
组件来实现内存中安全区域和非安全区域的硬件级
别的安全隔离，DRAM通过TZASC组件挂接到系统
总线上。图14-1所示为DRAM通过TZASC接入到系
统中的框图。

TZASC组件（tzc_380/tzc_400）可将DRAM的
地址空间划分成几个区域，每个区域可以被配置成
安全内存区域或非安全内存区域。当ARM核需要访
问物理内存时，除了会将需要访问的物理内存的地
址发送到系统总线上之外还会发送PROT信号（安
全读写信号），对应于总线上的安全状态位（NS
bit）。只有当ARM核处于安全世界状态时，安全

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 443

状态位才可能是0，即安全读写操作。由于DRAM
是通过TZASC挂接到总线上的，所以读写操作的物
理地址信息和PROT信号最终会被发送到TZASC
中，TZASC计算出ARM需要读写的物理内存地址
区域，再结合该读写请求的安全状态位的值来判定
该读写操作请求是否合法，如果需要被读写的物理
内存地址在系统启动时被设置成安全区域，而该读
写操作又是ARM核在正常世界状态时发起的，则
TZASC会判定该读写操作失败并返回错误。





   图14-1 DRAM与TZASC的连接示意

  内存区域的划分是在系统启动时通过配置
TZASC组件（tzc_400/tzc_380）中的寄存器来实现
的。在ATF中使用的是tzc_400，一般将区域0配置
成安全内存区域，用于EL3程序的运行，区域1配置
成安全内存用于TEE OS和TA的运行，其他区域配
置成非安全区域用于REE侧程序的运行。开发者也
可根据实际需求修改对内存区域的安全属性的设
定。




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 444

14.1.2 MMU和缓存中数据的安全隔离

  TZASC能够提供物理内存硬件级别的安全保
护，但ARM核访问数据时首先会到Cache中去查找
内容，如果在Cache中有需要被访问的地址的条
目，则会直接使用找到的条目中的内容作为访问的
结果，只有当在Cache中找不到与需要访问的内存
地址匹配的条目时才会从内存中去读取数据。

  支持TrustZone技术的ARM核对MMU进行了扩
展，MMU在安全世界状态和正常世界状态中具有
各自独立的TTBR0、TTBR1和TTBCR，对这些
MMU寄存器的虚拟化确保正常世界状态和安全世
界状态具有完全独立的MMU地址映射表。因此在
正常世界状态和安全世界状态中，虚拟地址
（Virtual Address，VA）到物理地址（Physical
Address，PA）的转化是独立分开的。但MMU中的
TLB是共用的，只不过对TLB中的每一项扩展了一
个安全状态位（NS bit），用来表示该条转化曾经
是正常世界状态触发的还是安全世界状态触发的。
Cache也有相同的扩展，当ARM核产生访问请求
时，将需要被访问虚拟地址经过MMU转换成物理
地址，并将物理地址值和当前ARM核是处于正常世
界状态还是安全世界状态的标志位NSTID传递给
Cache。Cache根据物理地址和NSTID来判定将哪一

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 445

个条目的数据发送到AXI上返回给ARM核。图14-2
所示为内存在正常世界状态和安全世界状态中的结
构框图。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 446

图14-2　内存在SWS和NWS的状态










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 447

14.2 ARM核对内存的访问

  系统启动完成后，系统运行于内存中，ARM
核处理的数据都来自于内存，即在系统运行过程
中，ARM核会从内存中获取数据。支持TrustZone
技术的ARM核在访问内存的过程中对安全世界状态
和正常世界状态进行了不同的处理。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 448

14.2.1 ARM核获取内存数据的过程

     当ARM核需要从内存中获取数据时，将需要
访问的内存的虚拟地址（VA）传递给MMU，
MMU会到TLB中查找是否存在该虚拟地址对应的
物理地址（PA），若没有对应的转换条目，MMU
将会使用虚拟地址和页表进行虚拟地址到物理地址
的转换操作，并将获取到的虚拟地址与物理地址的
转换条目存放到TLB中以便下次再次访问时直接使
用。完成虚拟地址到物理地址的转换后，MMU会
将物理地址发送到Cache中进行匹配操作。如果
Cache命中，Cache则会直接将命中的物理地址的数
据返回给ARM核。如果在Cache中并未命中，则会
将请求发送到AXI总线上，从内存硬件中读取物理
地址对应的数据，然后将数据返回给ARM核，并将
结果同步到Cache中。整个访问过程如图14-3所
示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 449

图14-3 ARM核访问内存过程流程








https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 450

14.2.2　获取缓存数据的过程

ARM核支持TrustZone后，对MMU、TLB、
Cache都做了相应的扩展，MMU的页表中增加了一
个安全状态位用来表示该地址映射是安全内存还是
非安全内存的映射。对TLB中的虚拟地址和物理地
址部分也都做了扩展，虚拟地址部分增加了NSTID
位，物理地址部分增加了安全状态位，用于表示该
虚拟地址和物理地址是安全内存还是非安全内存。
对Cache的扩展也增加了安全状态位，用于表示该
条Cache是ARM核在安全世界状态时访问产生的还
是在正常世界状态时访问产生的，ARM核获取
Cache中数据的处理过程如图14-4所示。

ARM核会将需要访问的虚拟地址和非安全页
表ID（non-secure table Identifier，NSTID）发送给
MMU，MMU查找TLB，如果命中则将命中的
VA+NSTID对应的PA+NS传递给Cache，Cache根据
物理地址和安全状态位在Cache条目中进行匹配操
作。若在Cache中存在与PA+NS对应的条目，则将
该条目中的数据返回给ARM核。如果在TLB中并未
找到与VA+NSTID对应的转换关系，则执行虚拟地
址到物理地址的转换（pagetable walk），并将获取
到的物理地址和虚拟地址作为一个新的条目同步到
TLB中，如果当前ARM核处于正常世界状态，则新

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 451

增该条目包含物理地址的安全状态位会被强制写成
1。TLB中存放的正常世界状态转换条目的内容映
射关系如图14-5所示。










     图14-4 Cache与TLB访问关系

   图14-5 TLB中虚拟地址与物理地址对照

  当ARM核为安全世界状态时，若在TLB中并未
有匹配的条目，MMU将进行虚拟地址到物理地址


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 452

的转换（pagetable walk），最终将得到的转换信息
同步到TLB中，缓存到TLB中条目的物理地址部分
的安全状态位是1还是0，则是由该内存是属于安全
内存还是非安全内存决定的。虚拟地址部分的
NSTID位标记该内存是安全内存还是非安全内存，
NSTID为1表示该内存为非安全内存，物理地址部
分的安全状态位会被设置成1。NSTID为0表示该内
存为安全内存，则物理地址部分的安全状态位会被
设置成0。完成同步操作后，将PA+NS位发送到
Cache中，如果在整个Cache中命中该条目，则直接
返回对应的数据给ARM核，如果未命中则到内存设
备中的物理地址位置去读取数据，并将数据返回给
ARM核后同步到Cache中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 453

14.2.3　缓存和TLB中条目的一致性

支持TrustZone技术的芯片中的Cache和TLB是
共享的。正常世界状态只能访问非安全内存，安全
世界状态是可以访问安全和非安全内存。当ARM核
处于正常世界状态时，处理器在访问内存时会忽略
掉安全状态位，只会去查找TLB中虚拟地址部分的
NSTID位为1的条目来获取对应的物理地址，然后
使用得到的物理地址在Cache中查找安全状态位为1
的条目。TLB中虚拟地址部分的NSTID位为1的所
有条目对应的物理地址部分的安全状态位会被强制
写成1。

当ARM核处于安全世界状态时，ARM核在访
问内存时并不会忽略掉安全状态位，即当ARM核处
于安全世界状态时会去查找TLB中虚拟地址部分的
NSTID为0的所有条目，若匹配到条目，则会将对
应条目中的物理地址和安全状态位部分传递给
Cache，而传递的安全状态位可能为1也可能为0。
缓存在MMU的TLB中条目的NSTID位的值不
是由产生该条目时ARM核的状态决定的，而是由该
地址在MMU中是被配置成安全内存还是非安全内
存决定的。ARM核处于安全世界状态时，访问安全
内存时产生的虚拟地址与物理地址的转换条目缓存

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 454

到TLB时，NSTID位为0且NS也为0，而当安全世界
状态访问非安全内存时，产生的虚拟地址与物理地
址的转换条目被缓存到TLB中时，NSTID位为1且
NS也为1。
  要理解这一点最好的例子是对共享内存数据的
读写，所有的共享内存都属于非安全内存。如果
ARM核需要获取共享内存中地址A的数据，且该地
址的虚拟地址与物理地址的转换条目已经被缓存到
TLB中，同时Cache也缓存了该地址的数据条目。
保存在TLB中的该地址的转换条目关系如图14-6所
示。


   图14-6 TLB中共享内存的映射条目关系
  而保存在Cache中的数据条目关系如图14-7所
示。


    图14-7 Cache中共享内存的条目

  当在正常世界状态修改了地址A中的数据后，
安全世界状态需要到Cache的非安全条目中查找
A_PA对应的条目，这样才能保证TLB中保存的条


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 455

目的安全状态位与Cache中保存的条目统一，所以
在OP-TEE建立MMU页表时需要将共享内存的内存
映射表中的NSTID位设置成1。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 456

14.3 OP-TEE对内存区域的管理

   支持TrustZone的ARM核对MMU进行了安全扩
展，ARM核在安全世界状态和正常世界状态中具有
各自的TTBR0、TTBR1、TTBCR，故在OP-TEE中
可以使用安全世界状态的TTBR0、TTBR1、
TTBCR来建立OP-TEE的内存映射表。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 457

14.3.1 OP-TEE中内存区域的类型

    OP-TEE会将内存划分成不同的区域，每个区
域包含内存区域类型、物理地址、虚拟地址、大
小、属性信息。OP-TEE使用tee_mmap_region结构
体类型的数组变量static_memory_map来表示，该结
构体的定义如下，OP-TEE划分的内存区域将会被
保存到static_memory_map数组中：


    struct tee_mmap_region {
      unsigned int type;           //内存区域类型
      unsigned int region_size;    //内存区域大小
      paddr_t pa;             //内存区域的起始物理地址
      vaddr_t va;             //内存区域的起始虚拟地址
      size_t size;                //内存区域的大小
      uint32_t attr;              //内存区域的属性
    };


    内存区域具有不同的类型，使用枚举类型
teecore_memtypes来表示类型的值，其定义和说明
如下：


    enum teecore_memtypes {
      MEM_AREA_END = 0,        //预留值,表示内存区域表的末尾
      MEM_AREA_TEE_RAM,        //OP-TEE OS使用的内存区域
      MEM_AREA_TEE_RAM_RX,         //OP-TEE内核私有内存区域具有只读和可执行权限
      MEM_AREA_TEE_RAM_RO,    //OP-TEE内核私有内存区域具有只读权限
      MEM_AREA_TEE_RAM_RW,    //OP-TEE内核私有内存区域具有读写权限
      MEM_AREA_TEE_COHERENT,    //OP-TEE内核一致性内存区域,预留给OP-TEE使用
      MEM_AREA_TA_RAM,        //动态TA加载和运行区域



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 458

      MEM_AREA_NSEC_SHM,      //OP-TEE与REE侧之间的非安全共享内存区域
      MEM_AREA_RAM_NSEC,     //用于保存数据的非安全内存区域
      MEM_AREA_RAM_SEC,       //用于保存数据的安全内存区域
      MEM_AREA_IO_NSEC,      //非安全硬件寄存器地址映射区域
      MEM_AREA_IO_SEC,        //安全硬件寄存器地址映射区域
      MEM_AREA_RES_VASPACE,   //预留的虚拟内存区域
      MEM_AREA_SHM_VASPACE,   //共享缓存的虚拟内存区域
      MEM_AREA_TA_VASPACE,    //TA虚拟地址区域
      MEM_AREA_SDP_MEM,       //特殊数据路径内存区域
      MEM_AREA_MAXTYPE        //无效内存区域类型值
    };


    每一种类型的内存区域具有不同的属性和作
用，每种类型的内存区域的属性和作用以及是否属
于安全内存的关系如下表14-1所示。

    表14-1 OP-TEE中内存区域划分的属性表










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 459

    14.3.2　内存区域编译设置

    OP-TEE支持SRAM和DRAM。在OP-TEE编译
    时分别使用三个区段来保存每个内存区域的信息，
    并提供不同的宏接口将不同的内存区域的信息注册
    到不同的区段中，
        其对应关系如表14-2所示。

    表14-2　内存区段编译设置




    这三个宏的接口说明如下：


/* 用于告诉编译器在编译时将输入的信息按照core_mmu_phys_mem结构体变量保存到_section指定的section中 */
#define __register_memory2(_name, _type, _addr, _size, _section, _id) \
    static const struct core_mmu_phys_mem __phys_mem_ ## _id \
        __used __section(_section) = \
        { .name = _name, .type = _type, .addr = _addr, .size = _size }
/* 设置section的名字 */
#define __register_memory1(name, type, addr, size, section, id) \
        __register_memory2(name, type, addr, size, #section, id)
/* 将定义的各内存区域信息保存到phys_mem_map_section段中 */
#define register_phys_mem(type, addr, size) \
        __register_memory1(#addr, (type), (addr), (size), \
        phys_mem_map_section, __COUNTER__)
/* 将定义的各内存区域信息保存到phys_sdp_mem_section段中 */
#define register_sdp_mem(addr, size) \
        __register_memory1(#addr, MEM_AREA_SDP_MEM, (addr), (size), \
        phys_sdp_mem_section, __COUNTER__)
/* 将定义的各内存区域信息保存到phys_nsec_ddr_section段中 */
#define register_nsec_ddr(addr, size) \




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 460

    __register_memory1(#addr, MEM_AREA_RAM_NSEC, (addr), (size), \
    phys_nsec_ddr_section, __COUNTER__)


     用户也可自行定义新的区段或并不按照这种方
式进行配置，
        只要在建立MMU映射表时能获得各
类型的内存区域信息即可。

     OP-TEE通过两个struct memaccess_area变量来
指定系统中的安全内存空间和非安全内存空间。在
建立MMU的内存映射表之前会对这两个区域范围
进行检查，并检查各种类型的内存区域是否按照其
配置的属性定义在安全内存还是非安全内存中。这
两个变量如下：


    /* 安全内存的整体区域,指定其起始地址和大小 */
    static struct memaccess_area secure_only[] = {
    #ifdef TZSRAM_BASE
    MEMACCESS_AREA(TZSRAM_BASE, TZSRAM_SIZE),
    #endif
    MEMACCESS_AREA(TZDRAM_BASE, TZDRAM_SIZE),
    };
    /* 非安全内存的整体区域,指定其起始地址和大小 */
    static struct memaccess_area nsec_shared[] = {
      MEMACCESS_AREA(CFG_SHMEM_START, CFG_SHMEM_SIZE),
    };










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 461

14.4 MMU的初始化和映射页表

  OP-TEE使用MMU来管理内存空间，建立物理
地址到虚拟地址的映射关系，其包括对物理内存空
间的地址映射、外部设备IO接口和寄存器的地址映
射。建立完整的地址映射关系后，OP-TEE就可直
接使用虚拟地址来访问物理内存中的数据或对外部
设备和寄存器进行读写操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 462

14.4.1 MMU的初始化入口函数

      MMU的初始化入口函数是
core_init_mmu_map，启动OP-TEE的过程中会调用
该函数，该函数主要完成各种内存区域物理地址与
虚拟地址之间的映射关系的建立，并生成一级转换
页表。在执行过程中还会对配置好的各种内存区域
是否属于安全内存进行检查。该函数的内容和注释
如下：



    void core_init_mmu_map(void)
    {
     struct tee_mmap_region *map;
     size_t n;
     /* 检查规定的安全内存空间与非安全内存空间之间是否存在重叠 */
     for (n = 0; n < ARRAY_SIZE(secure_only); n++) {
      if (pbuf_intersects(nsec_shared, secure_only[n].paddr,
          secure_only[n].size))
      panic("Invalid memory access config: sec/nsec");
     }
     /* 建立各种类型内存区域中物理地址与虚拟地址之间的映射关系 */
     if (!mem_map_inited)
      init_mem_map(static_memory_map, ARRAY_SIZE(static_memory_map));
     /* 检查各种类型的内存区域是否按照其属性设置配置在安全内存空间还是非安全内存空间 */
     map = static_memory_map;
     while (!core_mmap_is_end_of_table(map)) {
      switch (map->type) {
    /* 检查MEM_AREA_TEE_RAM、MEM_AREA_TEE_RAM_RX、MEM_AREA_TEE_RAM_RO、MEM_AREA_TEE_RAM_RW类型的内存区域是否在安全内存空间 */
      case MEM_AREA_TEE_RAM:
      case MEM_AREA_TEE_RAM_RX:
      case MEM_AREA_TEE_RAM_RO:
      case MEM_AREA_TEE_RAM_RW://确保这四个空间在secure_only中
      if (!pbuf_is_inside(secure_only, map->pa, map->size))
          panic("TEE_RAM can't fit in secure_only");
      break;



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 463

  /* 检查MEM_AREA_TA_RAM类型的内存区域是否在安全内存空间 */
  case MEM_AREA_TA_RAM:
   if (!pbuf_is_inside(secure_only, map->pa, map->size))
       panic("TA_RAM can't fit in secure_only");
   break;
  /* 检查MEM_AREA_NSEC_SHM类型的内存区域是否在非安全内存空间 */
  case MEM_AREA_NSEC_SHM:
   if (!pbuf_is_inside(nsec_shared, map->pa, map->size))
       panic("NS_SHM can't fit in nsec_shared");
   break;
  case MEM_AREA_IO_SEC:
  case MEM_AREA_IO_NSEC:
  case MEM_AREA_RAM_SEC:
  case MEM_AREA_RAM_NSEC:
  case MEM_AREA_RES_VASPACE:
  case MEM_AREA_SHM_VASPACE:
   break;
  default:
   EMSG("Uhandled memtype %d", map->type);
   panic();
  }
  map++;
 }
 /* 建立内存映射的转换页表 */
 core_init_mmu_tables(static_memory_map);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 464

14.4.2　物理地址到虚拟地址表的建立

      要使用虚拟地址来访问具体的物理地址就需要
建立虚拟地址与物理地址之间的映射关系。OP-
TEE默认将这种映射关系设置成一一映射，而对于
预留出来的虚拟地址空间则会按照其在
static_memory_map变量中的索引位置和预留的虚拟
空间的大小进行配置，预留虚拟地址空间的默认映
射的物理起始地址为0。OP-TEE通过调用
init_mem_map函数来实现映射关系的建立，该函数
的内容如下：



    static void init_mem_map(struct tee_mmap_region *memory_map, size_t num_elems)
    {
     const struct core_mmu_phys_mem *mem;
     struct tee_mmap_region *map;
     size_t last = 0;
     size_t __maybe_unused count = 0;
     vaddr_t va;
     vaddr_t __maybe_unused end;
     bool __maybe_unused va_is_secure = true; /* any init value fits */

     /* 将使用register_phys_mem定义的内存块区域按照type的值由小到大的
     方式依次排列到static_memory_map数组中*/
     for (mem = &__start_phys_mem_map_section;
     mem < &__end_phys_mem_map_section; mem++) {
     //从phys_mem_map_section段中获取一个定义好的内存区域信息
     struct core_mmu_phys_mem m = *mem;
     if (!m.size)
     continue;
     assert(m.addr || !core_mmu_type_to_attr(m.type));
     /* 如果定义的内存区域类型为MEM_AREA_IO_NSEC或MEM_AREA_IO_SEC,则按照页对齐的原则调整其地址和大小 */
     if (m.type == MEM_AREA_IO_NSEC || m.type == MEM_AREA_IO_SEC) {




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 465

       m.addr = ROUNDDOWN(m.addr, CORE_MMU_PGDIR_SIZE);
       m.size = ROUNDUP(m.size + (mem->addr - m.addr),
              CORE_MMU_PGDIR_SIZE);
      }
      /* 将phys_mem_map_section段中定义的所有类型内存区域信息填充到static_memory_map数组中 */
      add_phys_mem(memory_map, num_elems, &m, &last);
}
#ifdef CFG_SECURE_DATA_PATH
/* 检查SDP内存空间地址是否与DRAM/SRAM的内存空间地址有重叠,如果重叠则产生panic */
verify_special_mem_areas(memory_map, num_elems,
          &__start_phys_sdp_mem_section,
          &__end_phys_sdp_mem_section, "SDP");
/* 检查SDP内存空间地址是否与非安全的DDR地址空间地址有重叠,如果重叠则产生panic */
check_sdp_intersection_with_nsec_ddr();
#endif
/* 检查非安全的DDR地址空间与DRAM/SRAM的地址空间是否有重叠,如果重叠则产生panic */
verify_special_mem_areas(memory_map, num_elems,
          &__start_phys_nsec_ddr_section,
          &__end_phys_nsec_ddr_section, "NSEC DDR");
/* 预留出一段MEM_AREA_RES_VASPACE类型的内存空间,并将该类型的内存空间信息插入到static_memory_map数组末尾 */
add_va_space(memory_map, num_elems, MEM_AREA_RES_VASPACE,
       RES_VASPACE_SIZE, &last);
/* 预留出一段MEM_AREA_SHM_VASPACE类型的内存空间,并将该类型的内存空间信息插入到static_memory_map数组末尾 */
add_va_space(memory_map, num_elems, MEM_AREA_SHM_VASPACE,
       RES_VASPACE_SIZE, &last);
/* 设定static_memory_map数组中有效区域的尾端 */
memory_map[last].type = MEM_AREA_END;
/* 分配每个内存区域的region_size的值,用于表示该内存区域的块大小,如果static_memory_map中元素的size大于1M,则设置region_size为1M,表示该区域是按照1M对齐的,如果size的大小小于1M则设置region_size为4K,表示该区域按照4K对齐 */
for (map = memory_map; !core_mmap_is_end_of_table(map); map++) {
      paddr_t mask = map->pa | map->size;
      if (!(mask & CORE_MMU_PGDIR_MASK))
       map->region_size = CORE_MMU_PGDIR_SIZE;
      else if (!(mask & SMALL_PAGE_MASK))
       map->region_size = SMALL_PAGE_SIZE;
      else
       panic("Impossible memory alignment");
#ifdef CFG_WITH_PAGER
      if (map_is_tee_ram(map))
       map->region_size = SMALL_PAGE_SIZE;
#endif
}
/* 调整static_memory_map中各区域的位置,按照region_size由小到大的原则进行排列 */
qsort(memory_map, last, sizeof(struct tee_mmap_region),
      cmp_mmap_by_bigger_region_size);
#if !defined(CFG_WITH_LPAE)




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 466

for (count = 0, map = memory_map; map_is_pgdir(map); count++, map++)
      ;
/* 调整static_memory_map中各区域的位置,按照non-secure->secure由小到大的原则进行排列*/
qsort(memory_map + count, last - count, sizeof(struct tee_mmap_region),
      cmp_mmap_by_secure_attr);
#endif
va = (vaddr_t)~0UL;      //初始化VA的地址为~0UL
end = 0;//初始化虚拟地址的end为0
/* 建立map_is_flat_mapped内存中的虚拟地址到物理地址的映射关系 */
for (map = memory_map; !core_mmap_is_end_of_table(map); map++) {
      if (!map_is_flat_mapped(map))
       continue;
      /* 设定attr的值,决定映射属于flat的内存区域是否为安全内存区域、读写执行权限以及对该区域操作获取的结果是否需要同步到cache中*/
      map->attr = core_mmu_type_to_attr(map->type);
      map->va = map->pa;//使物理地址与虚拟地址一一对应
      /* 完成一次内存区域物理地址与虚拟地址的映射之后虚拟地址空间的起始地址 */
      va = MIN(va, ROUNDDOWN(map->va, map->region_size));
      /*完成一次内存区域物理地址与虚拟地址的映射之后虚拟地址空间的末端地址*/
      end = MAX(end, ROUNDUP(map->va + map->size, map->region_size));
}
assert(va >= CFG_TEE_RAM_START);
assert(end <= CFG_TEE_RAM_START + CFG_TEE_RAM_VA_SIZE);
/* 判定虚拟地址与物理地址映射完成后,OP-TEE的内核空间是否处于最高的1G空间之内,并建立预留出来的虚拟地址空间的虚拟起始地址和映射关系 */
if (core_mmu_place_tee_ram_at_top(va)) {
      for (map = memory_map; !core_mmap_is_end_of_table(map); map++) {
       if (map_is_flat_mapped(map))
        continue;
#if !defined(CFG_WITH_LPAE)
       if (va_is_secure != map_is_secure(map)) {
        va_is_secure = !va_is_secure;
        va = ROUNDDOWN(va, CORE_MMU_PGDIR_SIZE);
       }
#endif
       map->attr = core_mmu_type_to_attr(map->type);
       va -= map->size;
       va = ROUNDDOWN(va, map->region_size);
#if !defined(CFG_WITH_LPAE)
       va = ROUNDDOWN(va, CORE_MMU_PGDIR_SIZE);
#endif
       map->va = va;
      }
} else {
      va = ROUNDUP(va + CFG_TEE_RAM_VA_SIZE, CORE_MMU_PGDIR_SIZE);
      for (map = memory_map; !core_mmap_is_end_of_table(map); map++) {
       if (map_is_flat_mapped(map))




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 467

           continue;
    #if !defined(CFG_WITH_LPAE)
          if (va_is_secure != map_is_secure(map)) {
           va_is_secure = !va_is_secure;
           va = ROUNDUP(va, CORE_MMU_PGDIR_SIZE);
          }
    #endif
          map->attr = core_mmu_type_to_attr(map->type);
          va = ROUNDUP(va, map->region_size);
    #if !defined(CFG_WITH_LPAE)
          /* Mapping does not yet support sharing L2 tables */
          va = ROUNDUP(va, CORE_MMU_PGDIR_SIZE);
    #endif
          map->va = va;
          va += map->size;
         }
     }
     /* 按照各类型的内存区域的虚拟起始地址从小到大的原则重新排列static_memory_map数组中的元素 */
     qsort(memory_map, last, sizeof(struct tee_mmap_region),
         cmp_mmap_by_lower_va);
     /* 打印出映射完成之后的类型内存区域的映射关系的内容 */
     dump_mmap_table(memory_map);
    }



      从各区段中读取定义的各类型的内存区域信息
并建立其虚拟地址与物理地址之间的映射关系后，
下一步就可使用整理后的static_memory_map数组中
的信息生成转换页表。在QEMU中建立的各类型内
存区域的物理地址与虚拟地址之间的关系如图14-8
所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
          更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 468

图14-8 QEMU平台各类型区域地址映射










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 469

14.4.3 MMU转换页表的创建

      程序运行时一般使用的是虚拟地址，从虚拟地
址到物理地址的转换过程是由MMU通过查找转换
页表来完成的，
        关于MMU的工作原理在此就不再
赘述。在OP-TEE中转换页表是通过调用
core_init_mmu_tables函数使用static_memory_map数
组中的元素来生成的，生成的虚拟地址与物理地址
的转换页表将会被保存在特定的区域中，以备配置
MMU时被使用，在编译OP-TEE时就会定义保存转
换页表的地址，生成转换页表的函数内容如下：



    void core_init_mmu_tables(struct tee_mmap_region *mm)
    {
     paddr_t max_pa = 0;
     uint64_t max_va = 0;
     size_t n;
     /* 根据static_memory_map中各类型内存区域的物理末端地址和区域大小,计算获得生成转换页表的虚拟起始地址和虚拟末端地址 */
     for (n = 0; !core_mmap_is_end_of_table(mm + n); n++) {
      paddr_t pa_end;
      vaddr_t va_end;
      debug_print(" %010" PRIxVA " %010" PRIxPA " %10zx %x",
          mm[n].va, mm[n].pa, mm[n].size, mm[n].attr);
      if (!IS_PAGE_ALIGNED(mm[n].pa) || !IS_PAGE_ALIGNED(mm[n].size))
panic("unaligned region");
      pa_end = mm[n].pa + mm[n].size - 1;
      va_end = mm[n].va + mm[n].size - 1;
      if (pa_end > max_pa)
          max_pa = pa_end;
      if (va_end > max_va)
          max_va = va_end;
     }
     /* 清空用于保存转换页表的变量 */




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 470

 memset(l1_xlation_table[0], 0, NUM_L1_ENTRIES * XLAT_ENTRY_SIZE);
 /* 生成转换页表 */
 init_xlation_table(mm, 0, l1_xlation_table[0], 1);
 /* 为CPU中每个ARM核配置相同的转换页表 */
 for (n = 1; n < CFG_TEE_CORE_NB_CORE; n++)
  memcpy(l1_xlation_table[n], l1_xlation_table[0],
   XLAT_ENTRY_SIZE * NUM_L1_ENTRIES);
 for (n = 1; n < NUM_L1_ENTRIES; n++) {
  if (!l1_xlation_table[0][n]) {
   user_va_idx = n;
   break;
  }
 }
 assert(user_va_idx != -1);
 /* 获取tcr的物理地址位 */
 tcr_ps_bits = calc_physical_addr_size_bits(max_pa);
 COMPILE_TIME_ASSERT(CFG_LPAE_ADDR_SPACE_SIZE > 0);
 assert(max_va < CFG_LPAE_ADDR_SPACE_SIZE);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 471

14.4.4 MMU寄存器配置

     MMU在使能之前需要将转换页表的基地址写
入MMU的TTBR0/TTBR1寄存器中，并配置MMU
的TTBCR寄存器。MMU进行虚拟地址到物理地址
转换时会从TTBRx寄存中获取到转换页表的基地
址，然后使用需要转换的虚拟地址通过查表的方式
获取到该虚拟地址对应的物理地址。对MMU寄存
器的配置是在OP-TEE启动时通过调用
core_init_mmu_regs函数来实现的，AArch32和
AArch64的寄存器不同，但在配置MMU寄存器时其
原理是一样的，在AArch32中该函数的实现如下：


    void core_init_mmu_regs(void)
    {
     uint32_t ttbcr = TTBCR_EAE;
     uint32_t mair;
     paddr_t ttbr0;
     /* 获取当前ARM核的MMU的转换页表基地址 */
     ttbr0 = virt_to_phys(l1_xlation_table[get_core_pos()]);
     /* 配置MMU主要属性 */
     mair = MAIR_ATTR_SET(ATTR_DEVICE, ATTR_DEVICE_INDEX);
     mair |= MAIR_ATTR_SET(ATTR_IWBWA_OWBWA_NTR, ATTR_IWBWA_OWBWA_NTR_INDEX);
     write_mair0(mair);
     /* 配置TTBCR寄存器的值,用于控制MMU功能的各种限制 */
     ttbcr |= TTBCR_XRGNX_WBWA << TTBCR_IRGN0_SHIFT;
     ttbcr |= TTBCR_XRGNX_WBWA << TTBCR_ORGN0_SHIFT;
     ttbcr |= TTBCR_SHX_ISH << TTBCR_SH0_SHIFT;
     /* 禁止使用TTBR1 */
     ttbcr |= TTBCR_EPD1;
     /* 将MMU的配置信息数据写入到TTBCR寄存器中 */
     write_ttbcr(ttbcr);



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 472

     /* 将转换页表的基地址写入到TTBR0寄存器中 */
     write_ttbr0_64bit(ttbr0);
     /* 向TTBR1寄存器中写入0,不适用二级转换页表 */
     write_ttbr1_64bit(0);
    }


    待MMU的相关寄存器配置完成并使能MMU功
能后，就可通过虚拟地址来访问物理地址中的数
据。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 473

14.5 OP-TEE内存安全权限检查

  TZASC能够提供ARM核访问物理内存时的安
全检查，在系统运行过程中OP-TEE也提供了对操
作地址的安全检查的宏，用于检查访问的地址是否
属于安全内存空间。这些宏的定义如下：

/* 判定buf指向的物理地址是否属于非安全内存 */
#define tee_pbuf_is_non_sec(buf, len) \
            core_pbuf_is(CORE_MEM_NON_SEC, (paddr_t)(buf), (len))
/* 判定buf指向的物理地址是否属于安全内存 */
#define tee_pbuf_is_sec(buf, len) \
    core_pbuf_is(CORE_MEM_SEC, (paddr_t)(buf), (len))
/* 判定buf指向的虚拟地址是否属于非安全内存 */
#define tee_vbuf_is_non_sec(buf, len) \
             core_vbuf_is(CORE_MEM_NON_SEC, (void *)(buf), (len))
/* 判定buf指向的虚拟地址是否属于安全内存 */
#define tee_vbuf_is_sec(buf, len) \
    core_vbuf_is(CORE_MEM_SEC, (void *)(buf), (len))

                               OP-TEE中定义了两个struct memaccess_area类
型的变量，分别为secure_only和nsec_shared。
secure_only规定了OP-TEE中安全内存的物理地址范
围，nsec_shared规定了OP-TEE中非安全内存的物
理地址范围。如果需要检查某个虚拟地址是否为安
全地址，首先会将该地址通过MMU转换成物理地
址再进行安全权限检查。最终对权限的检查是通过
调用core_pbuf_is来完成的，该函数的内容和解释如
下：

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 474

    bool core_pbuf_is(uint32_t attr, paddr_t pbuf, size_t len)
    {
     struct tee_mmap_region *map;
     if (len == 0)
      return true;
     /* 通过attr来判定指定的buf是否处于安全区域还是非安全区域 */
     switch (attr) {
     case CORE_MEM_SEC:
      return pbuf_is_inside(secure_only, pbuf, len);
     case CORE_MEM_NON_SEC:
      return pbuf_is_inside(nsec_shared, pbuf, len) ||
      pbuf_is_nsec_ddr(pbuf, len);
     case CORE_MEM_TEE_RAM:
      return core_is_buffer_inside(pbuf, len, CFG_TEE_RAM_START,
          CFG_TEE_RAM_PH_SIZE);
     case CORE_MEM_TA_RAM:
      return core_is_buffer_inside(pbuf, len, CFG_TA_RAM_START,
CFG_TA_RAM_SIZE);
     case CORE_MEM_NSEC_SHM:
      return core_is_buffer_inside(pbuf, len, CFG_SHMEM_START,
CFG_SHMEM_SIZE);
     case CORE_MEM_SDP_MEM:
      return pbuf_is_sdp_mem(pbuf, len);
     case CORE_MEM_CACHED:
      map = find_map_by_pa(pbuf);
      if (map == NULL || !pbuf_inside_map_area(pbuf, len, map))
      return false;
      return map->attr >> TEE_MATTR_CACHE_SHIFT ==
          TEE_MATTR_CACHE_CACHED;
     default:
      return false;
     }
    }



      REE侧与OP-TEE之间的共享内存和OP-TEE内
核空间与用户空间之间的安全权限检查是通过调用
两个共享内存各自的match接口完成的。ARM核访
问时对内存区域的读写、执行权限的检查则是由
MMU来完成的。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 475

14.6　系统的共享内存

  共享内存分为REE侧与OP-TEE侧之间的共享
内存和OP-TEE内核空间与用户空间之间的共享内
存。前者用于OP-TEE侧驱动与OP-TEE之间的数据
交互，后者用于OP-TEE内核空间与OP-TEE用户空
间之间的数据交互。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 476

14.6.1　共享内存的配置

      上述两个共享内存区域具有不同的安全设定。
REE侧与OP-TEE之间的共享内存属于非安全内存
区域，
        OP-TEE内核空间与用户空间之间的共享内
存属于安全内存区域。OP-TEE在启动的过程通过
调用default_mobj_init函数划分出上述两个共享内存
区域并配置在OP-TEE中操作上述两个共享内存区
域的操作接口。default_mobj_init函数使用
driver_init_late宏进行封装，在OP-TEE启动过程中
执行Initcall段的内容时就会调用driver_init_late函数
进行上述两个共享内存区域的划分和初始化，该函
数的内容和注释如下：



    static TEE_Result default_mobj_init(void)
    {
     /* 设定default_nsec_shm_paddr指向的地址区域的属性,并将操作接口mobj_phys_ops填充到该mobj中的mobj.ops中 */
     shm_mobj = mobj_phys_alloc(default_nsec_shm_paddr,
                   default_nsec_shm_size, SHM_CACHE_ATTRS,
                   CORE_MEM_NSEC_SHM);
     if (!shm_mobj)
     panic("Failed to register shared memory");
     /* 设定tee_mm_sec_ddr.lo指向的地址区域的属性,并将操作接口mobj_phys_ops填充到该mobj 中的mobj.ops中 */
     mobj_sec_ddr = mobj_phys_alloc(tee_mm_sec_ddr.lo,
                        tee_mm_sec_ddr.hi - tee_mm_sec_ddr.lo,
                        SHM_CACHE_ATTRS, CORE_MEM_TA_RAM);
     if (!mobj_sec_ddr)
     panic("Failed to register secure ta ram");
    #ifdef CFG_SECURE_DATA_PATH
     sdp_mem_mobjs = core_sdp_mem_create_mobjs();
     if (!sdp_mem_mobjs)
     panic("Failed to register SDP memory");



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 477

  #endif
    return TEE_SUCCESS;
  }

    default_nsec_shm_paddr指向的区域是OP-TEE
驱动与OP-TEE之间的共享内存区域，属于非安全
内存。tee_mm_sec_ddr.lo则为OP-TEE内核空间与
OP-TEE用户空间之间的共享内存的起始地址，
tee_mm_sec_ddr指定的内存区域属于安全内存。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 478

14.6.2 OP-TEE驱动与OP-TEE之间的共享内存

                                     当CA调用或OP-TEE产生RPC请求时，产生的
数据交互是通过使用OP-TEE驱动与OP-TEE之间的
共享内存来完成的，该内存区域是OP-TEE驱动与
OP-TEE OS之间的共享内存，属于非安全内存。
OP-TEE中的default_nsec_shm_paddr变量指向的地
址就是OP-TEE驱动与OP-TEE之间的共享内存的起
始地址。default_mobj_init函数会设定该内存区域的
属性并设定操作该区域的接口。在OP-TEE启动过
程中，default_mobj_init会使用teecore_init_pub_ram
函数来对default_nsec_shm_paddr变量进行赋值，指
定该共享内存的物理起始地址和区域的大小，该函
数的内容如下：

void teecore_init_pub_ram(void)
{
       vaddr_t s;
       vaddr_t e;
       /* 获取MEM_AREA_NSEC_SHM类型的内存区域的起始虚拟地址和末端虚拟地址 */
       core_mmu_get_mem_by_type(MEM_AREA_NSEC_SHM, &s, &e);
       /* 结果检查 */
       if (s >= e || s & SMALL_PAGE_MASK || e & SMALL_PAGE_MASK)
           panic("invalid PUB RAM");
       /* 判定MEM_AREA_NSEC_SHM的内存区域是否为非安全内存,如果为安全内存则产生panic */
       if (!tee_vbuf_is_non_sec(s, e - s))
           panic("PUB RAM is not non-secure");
#ifdef CFG_PL310
       tee_l2cc_store_mutex_boot_pa(virt_to_phys((void *)s));
       s += sizeof(uint32_t);
       s = ROUNDUP(s, SMALL_PAGE_SIZE);


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 479

    #endif
      /* 将MEM_AREA_NSEC_SHM类型的内存区域的起始虚拟地址转化成物理地址赋值给default_nsec_shm_paddr */
      default_nsec_shm_paddr = virt_to_phys((void *)s);
      /* 计算该共享内存的大小 */
      default_nsec_shm_size = e - s;
    }

OP-TEE驱动会在加载的过程中通过发送命令
    为OPTEE_SMC_GET_SHM_CONFIG的快速安全监
    控模式调用（fast smc）请求获取
    default_nsec_shm_paddr和default_nsec_shm_size的
    值，然后使用该地址区域作为OP-TEE驱动的私有
    空间，用于OP-TEE区域与OP-TEE之间的数据交
    互。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 480

14.6.3 OP-TEE内核空间与用户空间之间的共享内
存

     内核空间与用户空间的共享内存在加载动态
TA和动态TA与OP-TEE内核之间传递数据时被使
用。tee_mm_sec_ddr.lo指定的地址区域是该共享内
存区域的起始地址，属于安全内存。
tee_mm_sec_ddr变量在OP-TEE启动时通过调用
teecore_init_ta_ram函数进行初始化，该函数的内容
如下：


    void teecore_init_ta_ram(void)
    {
     vaddr_t s;
     vaddr_t e;
     paddr_t ps;
     paddr_t pe;
     /* 获取MEM_AREA_TA_RAM类型的内存区域的起始虚拟地址和结束虚拟地址 */
     core_mmu_get_mem_by_type(MEM_AREA_TA_RAM, &s, &e);
     ps = virt_to_phys((void *)s);                   //将虚拟地址转换成物理地址
     pe = virt_to_phys((void *)(e - 1)) + 1;         //将虚拟地址转换成物理地址
     /* 检查结果 */
     if (!ps || (ps & CORE_MMU_USER_CODE_MASK) ||
     !pe || (pe & CORE_MMU_USER_CODE_MASK))
     panic("invalid TA RAM");
     /* 判定MEM_AREA_TA_RAM类型的内存区域是否为安全内存区域 */
     if (!tee_pbuf_is_sec(ps, pe - ps))
     panic("TA RAM is not secure");
     /* 判定tee_mm_sec_ddr的值是否为空 */
     if (!tee_mm_is_empty(&tee_mm_sec_ddr))
     panic("TA RAM pool is not empty");
     tee_mm_final(&tee_mm_sec_ddr);    //清空tee_mm_sec_ddr变量的值
     /* 完成tee_mm_sec_ddr变量的赋值,其中tee_mm_sec_ddr.lo是起始地址,tee_mm_sec_ddr.hi是末端地址 */
     tee_mm_init(&tee_mm_sec_ddr, ps, pe, CORE_MMU_USER_CODE_SHIFT,



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 481

TEE_MM_POOL_NO_FLAGS);
}

 当CA调用动态TA时，OP-TEE最终会将动态
TA加载到该区域，同时该TA也运行于该区域，即
OP-TEE的用户空间。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 482

14.7　数据是否需要写入Cache

      OP-TEE在MMU建立虚拟地址与物理地址之间
的映射关系时，
        会调用core_mmu_type_to_attr函数
来完成对各类型的内存区域的属性进行配置，在设
定内存区域的属性时会指定各类型的内存区域在被
访问时获取的数据是否需要同步到Cache中，该函
数的内容如下：



    uint32_t core_mmu_type_to_attr(enum teecore_memtypes t)
    {
     const uint32_t attr = TEE_MATTR_VALID_BLOCK | TEE_MATTR_GLOBAL;
     const uint32_t cached = TEE_MATTR_CACHE_CACHED << TEE_MATTR_CACHE_SHIFT;
     const uint32_t noncache = TEE_MATTR_CACHE_NONCACHE <<
         TEE_MATTR_CACHE_SHIFT;
     switch (t) {
     case MEM_AREA_TEE_RAM:
     return attr | TEE_MATTR_SECURE | TEE_MATTR_PRWX | cached;
     case MEM_AREA_TEE_RAM_RX:
     return attr | TEE_MATTR_SECURE | TEE_MATTR_PRX | cached;
     case MEM_AREA_TEE_RAM_RO:
     return attr | TEE_MATTR_SECURE | TEE_MATTR_PR | cached;
     case MEM_AREA_TEE_RAM_RW:
     return attr | TEE_MATTR_SECURE | TEE_MATTR_PRW | cached;
     case MEM_AREA_TA_RAM:
     return attr | TEE_MATTR_SECURE | TEE_MATTR_PRW | cached;
     case MEM_AREA_NSEC_SHM:
     return attr | TEE_MATTR_PRW | cached;
     case MEM_AREA_IO_NSEC:
     return attr | TEE_MATTR_PRW | noncache;
     case MEM_AREA_IO_SEC:
     return attr | TEE_MATTR_SECURE | TEE_MATTR_PRW | noncache;
     case MEM_AREA_RAM_NSEC:
     return attr | TEE_MATTR_PRW | cached;
     case MEM_AREA_RAM_SEC:




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 483

  return attr | TEE_MATTR_SECURE | TEE_MATTR_PRW | cached;
 case MEM_AREA_RES_VASPACE:
 case MEM_AREA_SHM_VASPACE:
  return 0;
 default:
     panic("invalid type");
 }
}



该函数配置每种类型内存区域的attr的值时，
如果添加了标志cached，则表示该类型的内存区域
的数据在被访问时需要将数据同步到Cache中， 并
在Cache保存的该条目中设定安全状态位的值， 安
全状态位的值由数据属于安全数据还是非安全数据
决定。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 484

14.8　小结

  本章介绍了OP-TEE中对内存的管理，并介绍
了ARM核访问物理内存设备时如何保障安全区域的
安全，介绍了安全世界状态与正常世界状态之间的
共享内存以及OP-TEE内核空间和用户空间的共享
内存的内容。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 485

第15章　OP-TEE中的线程管理

  OP-TEE中使用线程的方式来管理当前系统中
需要运行的任务。当TA被调用时，OP-TEE都会使
用一个线程空间来运行执行流程，待调用完成后，
该线程的状态将会被重置，以备后续被再次调用。
本章将详细介绍OP-TEE中线程管理的相关内容。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 486

15.1 OP-TEE中的线程

                     OP-TEE中的每一个线程作为一个任务的运行
载体。OP-TEE中定义了一个线程的数组，线程数
组中的每一个元素都表示一个单独的线程空间。该
数组定义在optee_os/core/arch/arm/kernel/thread.c文
件中，其内容如下：

struct thread_ctx threads[CFG_NUM_THREADS];

                     OP-TEE中并没有线程的创建一说，可通过修
改CFG_NUM_THREADS来控制OP-TEE中支持的
线程的最大个数。当CA端触发了安全监控模式调
用（smc）时，OP-TEE会从该数组中找寻到可用的
线程元素作为一个任务。如果REE侧触发的安全监
控模式调用（smc）是由RPC引起的，OP-TEE会直
接使用参数中的线程ID值找到对应的线程上下文，
然后执行恢复操作继续执行该线程，该线程ID的值
是OP-TEE发起RPC请求时的线程ID。

                     由于OP-TEE支持多核处理安全监控模式调用
（smc）（即CPU中的每一个核都可以用来处理安
全监控模式调用），故在OP-TEE中还存在另外一
个数组变量：


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 487

 static struct thread_core_local thread_core_local[CFG_TEE_CORE_NB_CORE]

  OP-TEE的线程数组是共用，即CPU中的所有
核共用线程数组。thread_core_local数组中的每一个
元素表示一个核的相关信息，元素中的
tmp_stack_va_end用于指定每个ARM核的栈空间，
curr_thread用于表示当前核使用的是哪个线程空
间。

  当CA触发安全监控模式调用（smc）来调用
TA中的命令时，OP-TEE会使用一个线程来完成对
该安全监控模式调用（smc）的处理。而如果CA调
用的是动态的TA，则该线程最终需要切到用户空
间去执行，而在进入到用户空间之前会重新设定该
线程的栈空间地址。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 488

    15.2　线程状态切换

      OP-TEE中的每个线程都具有三种状态，OP-
    TEE通过判定每个线程的状态来决定该线程是否可
    用。OP-TEE中线程的三种状态及含义如表15-1所
    示。

      表15-1 OP-TEE中线程的状态表



  OP-TEE使用枚举变量thread_state来表示当前
线程的状态，枚举中的值就是表15-1中的“表示状态
的值”一栏中的内容。线程状态之间的切换关系如
图15-1所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 489

       图15-1　线程状态切换
  线程状态的切换是通过设定线程的status成员
变量来实现，在OP-TEE对状态的切换操作进行了
封装，切换是使用汇编来实现的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 490

15.2.1 Free态到Active态的实现

OP-TEE启动时所有的线程都处于Free态（可用
状态）。
    当CA调用TA时就会从线程数组中找到一
个可用的线程空间用于运行该调用的任务。通过调
用thread_alloc_and_run函数可将Free态的线程设置
成Active态，
    该函数的内容如下：



static void thread_alloc_and_run(struct thread_smc_args *args)
{
 size_t n;
 struct thread_core_local *l = thread_get_core_local();//获取当前核的信息
 bool found_thread = false;
 assert(l->curr_thread == -1);
 /* 自旋锁锁定操作 */
 lock_global();
 /* 从全局的线程数组中查找可用的元素,即第一个状态为THREAD_STATE_FREE的元素并将找到的线程的状态设置成THREAD_STATE_ACTIVE */
 for (n = 0; n < CFG_NUM_THREADS; n++) {
  if (threads[n].state == THREAD_STATE_FREE) {
   threads[n].state = THREAD_STATE_ACTIVE;
   found_thread = true;
   break;
  }
 }
 /* 自旋锁解锁 */
 unlock_global();
 /* 判定是否找到可用的线程空间 */
 if (!found_thread) {
  args->a0 = OPTEE_SMC_RETURN_ETHREAD_LIMIT;
  return;
 }
 /* 将当前核的curr_thread变量设置成找到线程的索引值 */
 l->curr_thread = n;
 /* 清空找到线程的flag */
 threads[n].flags = 0;
 /* 设定该线程的入口函数、栈空间、sp以及入口函数的参数 */




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 491

 init_regs(threads + n, args);
 /* 虚拟化调用的ID*/
 threads[n].hyp_clnt_id = args->a7;
 thread_lazy_save_ns_vfp();
 /* 恢复该线程*/
 thread_resume(&threads[n].regs);
}



thread_resume函数执行完成后，
 该线程就处于
active状态并开始从指定的入口函数开始执行。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 492

15.2.2 Active态到Suspend态的实现

    当线程需要发送RPC请求时，首先需要将线程
挂起，然后触发RPC类型的安全监控模式调用
（smc）。当RPC请求返回时，直接使用该线程的
ID执行恢复操作继续执行就可接收RPC请求返回的
数据。OP-TEE处理FIQ中断时，需要使用线程来运
行中断的具体处理过程。OP-TEE会直接使用当前
ARM核运行的线程作为处理中断的线程使用，待中
断处理完毕后再返回到线程挂起之前的状态继续执
行。在OP-TEE中带参数调用thread_state_suspend函
数来实现对某个线程的挂起操作，该函数的内容如
下：


    int thread_state_suspend(uint32_t flags, uint32_t cpsr, vaddr_t pc)
    {
     struct thread_core_local *l = thread_get_core_local(); //获取当前ARM核的信息
     int ct = l->curr_thread;     //获取当前ARM核上运行的线程的ID
     assert(ct != -1);
     /* 检查当前线程的空间是否被破坏 */
     thread_check_canaries();
     /* 释放该线程无效的内核栈空间 */
     release_unused_kernel_stack(threads + ct, cpsr);
     /* 判定该挂起操作是否来自于用户空间,如果是则需要更新用session的时间 */
     if (is_from_user(cpsr)) {
      thread_user_save_vfp();
      tee_ta_update_session_utime_suspend();
      tee_ta_gprof_sample_pc(pc);
     }
     thread_lazy_restore_ns_vfp();
     /* 自旋锁锁定操作 */
     lock_global();



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 493

 assert(threads[ct].state == THREAD_STATE_ACTIVE);
 threads[ct].flags |= flags;     //设定该线程恢复回来时的flag
 threads[ct].regs.cpsr = cpsr;   //设定该线程恢复回来时的cpsr寄存器中的值
 threads[ct].regs.pc = pc;       //设定该线程恢复回来时的入口函数
 threads[ct].state = THREAD_STATE_SUSPENDED;//设定该线程的状态为挂起状态
 /* 如果线程有用户空间的内存映射,则还需要保存该线程的user map并清空ttbr */
 threads[ct].have_user_map = core_mmu_user_mapping_is_active();
 if (threads[ct].have_user_map) {
  core_mmu_get_user_map(&threads[ct].user_map);
  core_mmu_set_user_map(NULL);
 }
 /* 设定当前ARM核中的curr_thread的值为-1,即表示当前ARM核中并没有线程在运行 */
 l->curr_thread = -1;
 /* 自旋锁解锁操作 */
 unlock_global();
 return ct;
}



当thread_state_suspend函数执行完毕后，
                                 会触
发安全监控模式调用进行正常世界状态（NWS）和
安全世界状态（SWS）的切换，从安全世界状态切
换到正常世界状态。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 494

15.2.3 Suspend态到Active态的实现

  调用thread_resume函数可将挂起的线程切换到
运行状态，该函数在OP-TEE接收RPC请求返回的
数据时被调用。该函数的实现在前面章节中已有介
绍，在此就不再赘述。其原理就是恢复该线程在挂
起之前所有寄存器的值。PC的值作为线程恢复时程
序运行的入口地址。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 495

15.2.4 Active态到Free态的实现

  当线程处理完所有操作后就需要将线程重置，
释放掉分配的系统资源，并将该线程重新设置成
Free态以便被其他任务使用。这些操作是通过调用
thread_state_free函数来实现的，
    该函数的内容如
下：



void thread_state_free(void)
{
 struct thread_core_local *l = thread_get_core_local(); //获取当前ARM核的信息
 int ct = l->curr_thread;            //获取当前ARM核上运行的线程的ID
 assert(ct != -1);
 assert(TAILQ_EMPTY(&threads[ct].mutexes));
 thread_lazy_restore_ns_vfp();
 /* 释放掉该线程的栈空间 */
 tee_pager_release_phys(
 (void *)(threads[ct].stack_va_end - STACK_THREAD_SIZE),
 STACK_THREAD_SIZE);
 /* 自旋锁锁定操作 */
 lock_global();
 assert(threads[ct].state == THREAD_STATE_ACTIVE);
 threads[ct].state = THREAD_STATE_FREE; //将该线程的state成员设置成free
 threads[ct].flags = 0;       //清空该线程的flag
 l->curr_thread = -1;         //将当前ARM核中运行的线程的ID设置成-1
 /* 自旋锁解锁 */
 unlock_global();
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 496

15.3　线程运行时的资源

  线程在运行过程中需要很多资源的支持，其中
最重要的资源就是栈空间。当调用动态TA时，线
程会切换到用户空间运行，OP-TEE为每个线程指
定了内核空间栈，即OP-TEE中的所有线程都具有
独立的内核栈，如果线程需要进入到用户空间，也
会具有独立的用户空间栈。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 497

15.3.1　线程数据结构体

     OP-TEE使用thread_ctx结构体变量来表示每个
线程的基本信息，该结构体的定义如下：


    struct thread_ctx {
      struct thread_ctx_regs regs;      //用于保存线程运行时的所有寄存器的值
      enum thread_state state;          //用于标记线程的状态
      vaddr_t stack_va_end;             //线程的内核栈的栈底地址
      uint32_t hyp_clnt_id;             //虚拟化时client端的调用ID（在OP-TEE中未使用）
      uint32_t flags;                   //用于表示该线程是用于RPC请求还是中断的处理
      struct core_mmu_user_map user_map; //保存该线程的用户空间的内存映射信息
      bool have_user_map;               //标记当前线程是否有用户空间的内容映射
    #ifdef ARM64
      vaddr_t kern_sp;
    #endif
    #ifdef CFG_WITH_VFP
      struct thread_vfp_state vfp_state;
    #endif
      void *rpc_arg;                     //指向发送RPC请求时分配的共享内存的虚拟地址
      uint64_t rpc_carg;                 //发送RPC请求时cookie的地址
      struct mobj *rpc_mobj;             //发送RPC请求时分配的共享内存空间信息
      struct mutex_head mutexes;         //线程中互斥体链表的头
      struct thread_specific_data tsd;   //线程的特定数据,包含session、ta_contex等信息
    };


     线程执行挂起时会将cpsr、spsr、pc以及其他寄
存器的值保存到线程的regs变量中，以备在恢复线
程时直接通过regs中的数据恢复到挂起之前的状
态。stack_va_end是线程在内核态的栈底地址，当
线程切换到用户空间时需要重新设置栈空间。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 498

15.3.2 OP-TEE分配的内核栈

如果OP-TEE不支持PAGER，则会建立三个栈
空间，这三个栈空间的作用和说明如表15-2所列。

    表15-2 OP-TEE中的栈空间列表



这三个栈使用DECLARE_STACK来进行定
义，在编译时会被保存到.nozi_stack段中，其定义
在thread.c文件中，内容如下：

#define DECLARE_STACK(name, num_stacks, stack_size, linkage) \
linkage uint32_t name[num_stacks] \
      [ROUNDUP(stack_size + STACK_CANARY_SIZE, STACK_ALIGNMENT) / \
      sizeof(uint32_t)] \
      __attribute__((section(".nozi_stack"), \
      aligned(STACK_ALIGNMENT)))
DECLARE_STACK(stack_tmp, CFG_TEE_CORE_NB_CORE, STACK_TMP_SIZE, static);
DECLARE_STACK(stack_abt, CFG_TEE_CORE_NB_CORE, STACK_ABT_SIZE, static);
#ifndef CFG_WITH_PAGER
DECLARE_STACK(stack_thread, CFG_NUM_THREADS, STACK_THREAD_SIZE, static);
#endif

每个线程都具有独立的内核栈空间，该栈空间
是从nozi_stack中划分出来的。OP-TEE启动时会调


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 499

用init_thread_stacks函数为OP-TEE支持的每个线程
指定内核栈空间，并将该栈的地址赋值给线程结构
体中的stack_va_end成员，其内容如下：


    bool thread_init_stack(uint32_t thread_id, vaddr_t sp)
    {
     if (thread_id >= CFG_NUM_THREADS)
      return false;
     //将传入的地址sp赋值给线程中的stac_va_end成员
     threads[thread_id].stack_va_end = sp;
     return true;
    }
    static void init_thread_stacks(void)
    {
     size_t n;
     /* 使用stack_thread指定的区域为每个线程指定内核栈空间 */
     for (n = 0; n < CFG_NUM_THREADS; n++) {
      if (!thread_init_stack(n, GET_STACK(stack_thread[n])))
      panic("thread_init_stack failed");
     }
    }










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 500

15.3.3　线程运行于用户空间的资源

     CA触发安全监控模式调用（smc）时，OP-
TEE都会使用一个线程来完成具体操作。如果调用
的是动态TA，则该线程最终会切换到OP-TEE的用
户空间，调用具体TA的接口来完成处理。OP-TEE
使用user_ta_ctx结构体变量保存该调用在用户空间
的所有信息，其中就包括了线程在用户空间运行时
的栈信息，该结构体的内容和注释如下：


    struct user_ta_ctx {
    uaddr_t entry_func;        //线程进入到用户空间时的入口函数,即每个动态TA的__utee函数
    uaddr_t exidx_start;        // TA panic时使用的栈的起始地址
    size_t exidx_size;        //处理Panic时使用的栈的大小
    //表示该TA是32位的还是64位的,true表示32位, false表示64位
    bool is_32bit;
    //用于保存由该TA打开的与其他TA之间的session链表头
    struct tee_ta_session_head open_sessions;
    //用于保存由该TA创建的crypt操作的链表头
    struct tee_cryp_state_head cryp_states;
    struct tee_obj_head objects; //用于保存由该TA创建的object信息的链表头
    //用于保存由该TA创建的存储enum信息的链表头
    struct tee_storage_enum_head storage_enums;
    struct mobj *mobj_code;      //保存在MEM_AREA_TA_RAM内存区域的TA代码的起始地址
    struct mobj *mobj_stack;     //TA用户空间运行时的栈地址
    uint32_t load_addr;        //加载到MEM_AREA_TA_RAM内存区域的TA代码的起始地址的虚拟地址
    uint32_t context;        //处理的context的ID
    struct tee_mmu_info *mmu;    //动态TA的MMU信息(ddr only)
    void *ta_time_offs;        //TA使用的时间信息
    struct tee_pager_area_head *areas;
    #if defined(CFG_SE_API)
    struct tee_se_service *se_service;
    #endif
    #if defined(CFG_WITH_VFP)
    struct thread_user_vfp_state vfp;



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 501

#endif
  //该TA运行时的context信息,在opensession时会被加入到tee_ctxes链表中
  struct tee_ta_ctx ctx;
};

  只有当CA调用的是动态TA时才会创建该结构
体变量。创建该变量时，entry_func会被初始化成
该TA镜像的ta_head段中的entry.ptr64的值，该值在
编译生成TA镜像时被设定成__utee_entry。

       用户空间中使用的栈空间是从tee_mm_sec_ddr
内存池中分配出来的，该内存池属于
MEM_AREA_TA_RAM内存区域，该区域是由OP-
TEE分配，用于运行TA镜像。
  用户空间使用的堆空间是在user_ta_header.c文
件中定义的ta_heap数组变量，其大小由
TA_DATA_SIZE宏决定。该宏定义在每个TA的
user_ta_header.h文件中，ta_heap会被编译到TA镜像
文件的BSS段中，加载TA镜像到OP-TEE的过程中
会使用malloc_add_pool函数将ta_heap作为该TA的
堆空间添加到内存池中，在TA中需要使用类似于
malloc的函数分配一块内存空间时就会从该内存池
中分配所需要的内存。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 502

15.3.4 tee_ta_session结构体

     CA调用创建会话操作时会创建一个会话建立
CA与特定TA之间的通道。会话是tee_ta_session的
结构体变量，创建好的变量会被添加到OP-TEE用
于保存当前系统中已经被创建的会话的链表
tee_open_sessions中。待下次CA调用时，只要提供
会话ID就可从tee_open_session链表中查找到对应的
会话实体，进行调用TA命令的操作。添加到该链
表中的是tee_ta_session结构体变量，该结构体的定
义如下：


    struct tee_ta_session {
      TAILQ_ENTRY(tee_ta_session) link;
      TAILQ_ENTRY(tee_ta_session) link_tsd;
      //TA的运行上下文,如果该TA为动态TA,则该值即是user_ta_ctx中的ctx成员
      struct tee_ta_ctx *ctx;
      TEE_Identity clnt_id;       // CA调用的ID信息,包含CA调用是的login方式和UUID值
      bool cancel;                //表示需要取消调用TA命令
      bool cancel_mask;           //需要取消的调用TA命令对应命令ID的操作
      TEE_Time cancel_time;       //取消调用命令操作的时间
      void *user_ctx;             //用户空间的user_ta_contex
      uint32_t ref_count;         //记录当前该会话被引用的次数
      struct condvar refc_cv;     //等待ref_count变成0,即表示当前会话未被引用
      struct condvar lock_cv;
      int lock_thread;            //记录当前那个thread获取了该会话的锁
      bool unlink;                //表示当前会话是否被锁定
    #if defined(CFG_TA_GPROF_SUPPORT)
      struct sample_buf *sbuf; /* Profiling data (PC sampling) */
    #endif
    };





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 503

     每个tee_ta_session变量会包含指向TA运行上下
文的指针，TA的运行上下文使用tee_ta_ctx结构体
来表示，其内容和定义如下：


    struct tee_ta_ctx {
      TEE_UUID uuid; //该TA的UUID
      const struct tee_ta_ops *ops; //提供操作TA的接口函数
      uint32_t flags; // ta_head中规定该TA的flag
      TAILQ_ENTRY(tee_ta_ctx) link;
      uint32_t panicked; // TA是否panic了,true表示该TA已经panic了
      uint32_t panic_code; //用于处理TA panic请求的代码地址
      uint32_t ref_count; // TA被引用的次数
      bool busy; //当前会话是否正在被使用
      struct condvar busy_cv; //cv值
    };


     如果CA与TA之间的会话已经创建完成，CA调
用时会从tee_open_sessions链表中通过UUID的值找
到需要被调用的会话，然后使用该会话的内容来操
作TA。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 504

15.4　线程运行时资源的使用关系

  使用线程来处理CA对TA的调用请求时都会使
用到上一节中的所有资源。如果调用的是动态
TA，还会使用到该TA的user_ta_ctx的内容，线程的
运行与上述资源的关系如图15-2所示。










    图15-2　线程与系统资源的关系
    线程切换到用户空间之前，使用thread_ctx实体

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 505

中的stack_va_end作为该线程运行时的内核栈空
间，并且通过UUID从tee_open_session链表中查找
到需要被调用的TA的tee_ta_session实体。该实体会
保存TA的操作上下文信息，该上下文信息是在CA
调用创建会话操作时被分配和初始化的。保存在
user_ta_ctx的tee_ta_ctx结构体成员中，通过
tee_ta_ctx实体就能够找到在用户空间使用的
user_ta_ctx的内容。user_ta_ctx实体中会指定线程在
用户空间使用的用户空间栈地址。这些结构体之间
的包含关系如图15-3所示。










    图15-3 TA相关结构体关系



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 506

15.5 OP-TEE中线程的调度

  OP-TEE支持SMP，即支持多核来处理安全监
控模式调用，但任何时候一个核上同时只会有一个
线程在运行。CPU中的所有核共享OP-TEE的线程
数组，即如果某个线程被一个核挂起了，待需要被
恢复继续运行时，任何CPU的核都可以通过线程ID
继续运行该线程。

  OP-TEE中的线程调度并不像Linux一样采取时
间片轮转的方式进行。在OP-TEE中，一个线程分
配到ARM核运行之后，其将独占该核的使用权。除
非线程主动挂起或正常世界状态的中断触发状态切
换。待线程执行完后会释放掉调用该线程时分配的
资源，并将线程空间重置成Free状态，释放掉占使
用的ARM核的控制权限。

  如果线程在执行过程中主动执行挂起操作，则
线程会保存当前线程的资源，并将线程的状态设置
成挂起态，然后通过指定当前ARM核的
thread_core_local结构体变量中的curr_thread交出
ARM核的控制权限。待线程被挂起后，若有实际需
求时，CPU中的任何一个核都可以使用该线程的ID
来唤醒该线程继续执行。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 507

15.6　线程的死锁

  死锁对于任何一个系统来说都是很严重的问
题，轻则会导致线程被杀死而无法完成任务，重则
可能会引起看门狗超时导致系统重启。这对于任何
一个系统来说都是不可接受的。故避免死锁现象对
于系统的稳定性来说至关重要。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 508

15.6.1　死锁的原理

  死锁即一个线程占用了资源A，同时需要获取
到资源B之后才会释放资源A，而另一个线程占用
了资源B，而且只有获取到资源A之后才会释放资
源B，这样导致线程one和线程two都无法正确地获
取到资源继续执行，更加直观的解释如图15-4所
示。










    图15-4　死锁原理







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 509

15.6.2　防止死锁

  死锁一般出现在对互斥体或自旋锁的使用过程
中，尤其是一个线程需要获取多个互斥体或者自旋
锁的情况下。有效地防止死锁现象的做法是，如果
一个线程需要使用多个互斥体或者自旋锁来完成一
些操作时，其他的线程在使用这些互斥体或者自旋
锁时需要按照同样的顺序来获得，即在使用互斥体
或者自旋锁时统一按照相同的顺序进行。而且最好
互斥体和自旋锁的锁住和解锁动作在同一个函数中
完成。这点在编写TA程序使用互斥体或者自旋锁
时需要格外注意。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 510

15.7　小结

  本章介绍了OP-TEE中线程的相关信息和状态
切换的实现。注意CPU中的所有核共享OP-TEE的
线程数组，当执行动态TA时，线程进入到用户空
间之后会使用新的堆栈空间，在某种意义上可以理
解成各个TA之间是相互隔离的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 511

第16章　OP-TEE的系统调用

16.1 OP-TEE系统调用的作用

              OP-TEE运行时分为用户空间和内核空间，以
此来保证OP-TEE运行时用户空间和内核空间的相
互独立。TA程序、OP-TEE提供的一些外部库、各
种算法的对外接口都存在于用户空间，而OP-TEE
的线程管理、TA管理、内存管理等都运行于内核
空间。用户空间的程序无法直接访问到内核空间的
资源和内存，如果用户空间的程序需要访问内核空
间的资源可以通过OP-TEE的系统调用（System
Call）的来实现。
OP-TEE按照GP规范定义的大部分接口都是给
OP-TEE中的TA使用的。GP统一定义了高级加密标
准（Advanced Encryption Standard，ASE）、
RSA、安全散列算法（Secure Hash Algorithm，
SHA）、哈希消息论证码（Hash-based Message
Authentication Code，HMAC）、基于密码的密钥
导出算法（Password-Based Key Derivation
Function，PBKDF2）等算法的调用接口，该部分在
OP-TEE编译时会被编译成libutee.a库文件。TA可通
过调用该库中的相关接口来完成对数据的加解密以


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 512

及签名和验签等操作。如果板级具有硬件密码学引
擎实现，调用这些算法接口后最终会使用底层驱动
引擎来完成密码学的相关操作。密码学引擎驱动是
处于内核空间的，这也就衍生出了OP-TEE的系统
调用的需求。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 513

16.2 OP-TEE系统调用的实现

   OP-TEE用户空间的接口一般定义成
utee_xxx_xxx的形式，而其对应的系统调用则为
syscall_xxx_xxx。即在OP-TEE的用户空间调用
utee_xxx_xxx函数，OP-TEE最终会调用
syscall_xxx_xxx来实现处理，可参考Linux中系统调
用的概念。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 514

    16.2.1　系统调用的整体流程

    OP-TEE的系统调用是通过让ARM核进入svc模
    式来使系统陷入内核态中，然后根据系统调用ID来
    命中系统调用的内核实现，整个系统调用的过程如
    图16-1所示。










     图16-1 OP-TEE中系统调用流程
  OP-TEE系统调用的关键点是通过svc从OP-TEE
用户空间切换到OP-TEE的内核空间。使用切换时
带入的系统调用ID，在OP-TEE的系统调用数组中
找到对应的函数并执行，完成系统调用后切换ARM
核的模式返回到用户空间。


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 515

    16.2.2　系统调用的定义

    一个系统调用的定义是在用户空间通过
    UTEE_SYSCALL宏来实现的。在OP-TEE中，
        所有
    的utee_xxx类的接口都使用该宏定义在
    utee_syscalls_asm.S文件中，该宏使用汇编实现，内
    容如下：



    .macro UTEE_SYSCALL name, scn, num_args
    FUNC \name , :
         push     {r5-r7,lr}      //保存r5~r7和lr
         mov      r7, #(\scn)     //将scn的值保存到r7中,scn为syscall的index
    /* 检查参数个数,并根据num_args 的值来配置参数个数和参数在sp中的位置 */
    .if \num_args > TEE_SVC_MAX_ARGS
    .error "Too many arguments for syscall"
    .endif
         .if \num_args <= 4
         @ No arguments passed on stack
         mov      r6, #0
         .else
         @ Tell number of arguments passed on the stack
         mov      r6, #(\num_args - 4)
         @ Point just before the push (4 registers) above on the first argument
         add      r5, sp, #(4 * 4)
         .endif
         svc #0       //触发类svc中断
         pop      {r5-r7,pc}      //svc处理完成之后返回继续执行
    END_FUNC \name
    .endm



该宏相当于实现了utee_xxx的函数，
                                  在使用该
    宏时，
参数中name相当于是utee_xxx，              scn是系统调





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 516

用的索引号，numargs是参数个数。若numargs的值
小于或等于4则表示不需要传递额外数据给系统调
用。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 517

16.2.3　系统调用表tee_sv_syacall_table

  OP-TEE的内核空间中定义了一个系统调用的
数组表——tee_svc_syscall_table，该数组中包含了
当前OP-TEE中支持的所有系统调用在内核空间的
实现，该数组定义在
optee_os/core/arch/arm/tee/arch_svc.c文件中。由于
该数组较大，在此就不贴出。在用户空间中触发
svc后，会调用tee_svc_handler函数，该函数会使用
在用户空间传入的scn值从tee_svc_syscall_table中查
找到系统调用的实现，tee_svc_syscall_table[scn]内
容所指向的函数即为系统调用在OP-TEE内核空间
的具体实现。

  tee_svc_handler会调用tee_svc_do_call来执行
tee_svc_syscall_table[scn]中定义的函数。在执行
tee_svc_syscall_table[scn]之前会保存相关寄存器，
以便执行完系统调用后恢复到执行系统调用之前的
用户空间的状态，而且还需要将用户空间中带入的
数据复制到内核空间供tee_svc_syscall_table[scn]中
的函数使用。






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 518

16.3　小结

  系统调用主要是给用户空间的接口提供对内核
空间接口的调用，使用户空间可以访问到内核空间
的资源。例如在使用安全存储功能时，对object的
所有操作最终都是在内核空间完成的，包括安全文
件查找、文件树建立、RPC请求发送等。所以理解
OP-TEE中系统调用的实现，对理解OP-TEE在用户
空间提供的接口的具体实现有很大帮助。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 519

第17章　OP-TEE的IPC机制

  进程间通信（Inter-Process Communication，
IPC）机制是指系统中进程或线程之间的通信机
制，用于实现线程与线程之间进行通信、数据交互
等功能。Linux具有多种方式能够实现进程或线程
之间的通信和数据共享，例如：消息队列、信号
量、共享内存等。而在OP-TEE中并未提供如此丰
富的IPC方法，本章将介绍OP-TEE中的IPC机制。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 520

17.1 IPC机制的作用

  动态TA是以线程的方式运行于OP-TEE的用户
空间，OP-TEE的IPC机制用于实现各线程之间的相
互调用、线程调用安全驱动、线程调用OP-TEE内
核空间的服务。OP-TEE中并未有类似消息队列、
信号量等专门用于线程间通信的机制，但OP-TEE
提供动态TA调用其他TA或安全驱动的方法和接
口，从而实现OP-TEE中各线程间的通信。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 521

17.2 IPC机制的原理

OP-TEE中的IPC机制主要是为满足OP-TEE用
户空间运行的线程调用其他线程、静态TA、安全
驱动的需求。其原理的核心是利用系统调用来访问
其他线程或者安全驱动。当线程需要调用其他线程
或者安全驱动时，首先会通过系统调用陷入到OP-
TEE的内核态，然后执行类似CA调用TA的操作，
建立会话并通过调用命令的方式让其他TA来完成
相应的操作。线程调用安全驱动时，同样是通过调
用系统调用陷入到OP-TEE的内核态，然后调用服
务或安全驱动提供给OP-TEE内核空间的接口来完
成TA对安全驱动和服务的调用。关于OP-TEE中系
统调用的实现和定义方式可参考本书第16章。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 522

17.3 IPC的实现

  OP-TEE的IPC机制是通过系统调用陷入到内核
中来实现的。调用其他TA的操作有专门的接口，
而访问安全驱动和OP-TEE的服务则是通过在内核
态中调用服务提供的内核级接口来实现的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 523

17.3.1 TA调用其他TA的实现

  一个TA调用其他TA时，OP-TEE通过建立两者
间的会话，并调用命令来实现。GP规范定义了如表
17-1中的三个接口，这些接口可在OP-TEE的用户空
间被调用。

   表17-1 TA调用其他TA使用的接口列表



  当一个TA需要调用其他的TA时，首先需要使
用TEE_OpenTASession创建两个TA之间的会话，再
使用TEE_InvokeTACommand调用到已经建立的会
话的TA中的具体操作，待不再需要调用其他TA
时，则调用TEE_InvokeTACommand函数关闭会话
来断开两个TA间的联系。
1.TEE_OpenTASession的实现

  TEE_OpenTASession的实现与CA中创建与TA
的会话的过程大致相同，但TEE_OpenTASession是
通过系统调用的方式来触发OP-TEE分配线程并创
建会话，而CA则是通过触发安全监控模式调用

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 524

（smc）来让OP-TEE分配线程并创建会话。
TEE_OpenTASession操作的整体流程如图17-1所
示。

  函数执行到tee_ta_open_session后，
    其操作与在
CA创建会话的操作完全一致，
syscall_open_ta_session函数的说明如下：


TEE_Result syscall_open_ta_session(const TEE_UUID *dest,
  unsigned long cancel_req_to,
  struct utee_params *usr_param, uint32_t *ta_sess,
  uint32_t *ret_orig)
{
 TEE_Result res;
 uint32_t ret_o = TEE_ORIGIN_TEE;
 struct tee_ta_session *s = NULL;
 struct tee_ta_session *sess;
 struct mobj *mobj_param = NULL;
 TEE_UUID *uuid = malloc(sizeof(TEE_UUID));
 struct tee_ta_param *param = malloc(sizeof(struct tee_ta_param));
 TEE_Identity *clnt_id = malloc(sizeof(TEE_Identity));
 void *tmp_buf_va[TEE_NUM_PARAMS];
 struct user_ta_ctx *utc;
 /* 参数合法性检查 */
 if (uuid == NULL || param == NULL || clnt_id == NULL) {
  res = TEE_ERROR_OUT_OF_MEMORY;
     goto out_free_only;
 }
 /* 清空分配的param变量中的数据 */
 memset(param, 0, sizeof(struct tee_ta_param));
 /* 获取当前TA的会话信息 */
 res = tee_ta_get_current_session(&sess);
 if (res != TEE_SUCCESS)
     goto out_free_only;
 utc = to_user_ta_ctx(sess->ctx);
 /* 将用户空间传递的UUID值复制到内核空间中 */
 res = tee_svc_copy_from_user(uuid, dest, sizeof(TEE_UUID));
 if (res != TEE_SUCCESS)
     goto function_exit;



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 525

 /* 设定login方式并设定clnt_id->uuid的值,即让当前TA认为是client端*/
 clnt_id->login = TEE_LOGIN_TRUSTED_APP;
 memcpy(&clnt_id->uuid, &sess->ctx->uuid, sizeof(TEE_UUID));
 /* 复制用户空间传递的参数数据到内核空间 */
 res = tee_svc_copy_param(sess, NULL, usr_param, param, tmp_buf_va,
      &mobj_param);
 if (res != TEE_SUCCESS)
  goto function_exit;
 /* 执行创建会话操作*/
 res = tee_ta_open_session(&ret_o, &s, &utc->open_sessions, uuid,
      clnt_id, cancel_req_to, param);
 if (res != TEE_SUCCESS)
  goto function_exit;
 /* 更新param的内容 */
 res = tee_svc_update_out_param(sess, s, param, tmp_buf_va, usr_param);
function_exit:
 if (mobj_param) {
  mutex_lock(&tee_ta_mutex);
  mobj_free(mobj_param);
  mutex_unlock(&tee_ta_mutex);
 }
 if (res == TEE_SUCCESS)
  tee_svc_copy_kaddr_to_uref(ta_sess, s);//将获得的会话的ID值复制到用户空间
 //复制执行函数的返回值到用户空间
 tee_svc_copy_to_user(ret_orig, &ret_o, sizeof(ret_o));
out_free_only:
 free(param);
 free(uuid);
 free(clnt_id);
 return res;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 526

  图17-1 TEE_OpenTASession操作实现的流程
   关于tee_ta_open_session函数的执行过程可参阅

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 527

    本书第13章。
    2.TEE_InvokeTACommand的实现

      调用TEE_InvokeTACommands时带入命令ID的
    值就能调用TA中具体的命令，其过程与CA的命令
    调用操作几乎一致，该接口的执行流程如图17-2所
    示。










  图17-2 TEE_InvokeTACommands操作流程
  Syscall_invoke_ta_command的内容和说明如

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 528

下：



TEE_Result syscall_invoke_ta_command(unsigned long ta_sess,
         unsigned long cancel_req_to, unsigned long cmd_id,
         struct utee_params *usr_param, uint32_t *ret_orig)
{
 TEE_Result res;
 TEE_Result res2;
 uint32_t ret_o = TEE_ORIGIN_TEE;
 struct tee_ta_param param = { 0 };
 TEE_Identity clnt_id;
 struct tee_ta_session *sess;
 struct tee_ta_session *called_sess;
 struct mobj *mobj_param = NULL;
 void *tmp_buf_va[TEE_NUM_PARAMS];
 struct user_ta_ctx *utc;
 /* 获取当前的TA的session信息 */
 res = tee_ta_get_current_session(&sess);
 if (res != TEE_SUCCESS)
 return res;
 utc = to_user_ta_ctx(sess->ctx);
 /* 根据session ID从保存已经open的session链表中找到对应的session */
 called_sess = tee_ta_get_session(
             (vaddr_t)tee_svc_uref_to_kaddr(ta_sess), true,
 &utc->open_sessions);
 if (!called_sess)
 return TEE_ERROR_BAD_PARAMETERS;
 /* 设定clnt_id的内容,将调用者作为client端处理 */
 clnt_id.login = TEE_LOGIN_TRUSTED_APP;
 memcpy(&clnt_id.uuid, &sess->ctx->uuid, sizeof(TEE_UUID));
 /* 复制从用户空间传入的参数 */
 res = tee_svc_copy_param(sess, called_sess, usr_param, &param,
 tmp_buf_va, &mobj_param);
 if (res != TEE_SUCCESS)
     goto function_exit;
 /* 开始调用找到的session中的invoke command,根据command ID执行指定的操作 */
 res = tee_ta_invoke_command(&ret_o, called_sess, &clnt_id,
     cancel_req_to, cmd_id, &param);
 /* 更新执行结果到输出参数 */
 res2 = tee_svc_update_out_param(sess, called_sess, &param, tmp_buf_va,
     usr_param);
 if (res2 != TEE_SUCCESS) {





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 529

  ret_o = TEE_ORIGIN_TEE;
  res = res2;
 }

function_exit:
 tee_ta_put_session(called_sess);
 if (mobj_param) {
  mutex_lock(&tee_ta_mutex);
  mobj_free(mobj_param);
  mutex_unlock(&tee_ta_mutex);
 }
 if (ret_orig)
  tee_svc_copy_to_user(ret_orig, &ret_o, sizeof(ret_o));
 return res;
}



关于tee_ta_invoke_command函数的执行过程可
参阅第13章。
3.TEE_CloseTASession的实现
TEE_CloseTASession接口用于断开TA与其他
TA之间的连接，其过程与CA的关闭会话操作几乎
一致，
   该接口的执行流程如图17-3所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 530

        图17-3 TEE_CloseTASession操作流程
      调用TEE_CloseTASession接口时会产生系统调
用，系统会执行关闭会话的操作，
syscall_close_ta_session函数的内容和说明如下：


    TEE_Result syscall_close_ta_session(unsigned long ta_sess)
    {
     TEE_Result res;
     struct tee_ta_session *sess;
     TEE_Identity clnt_id;
     struct tee_ta_session *s = tee_svc_uref_to_kaddr(ta_sess);
     struct user_ta_ctx *utc;
     /* 获取当前TA的session信息 */
     res = tee_ta_get_current_session(&sess);
     if (res != TEE_SUCCESS)
     return res;
     utc = to_user_ta_ctx(sess->ctx);



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 531

 /* 设定clnt_id信息 */
 clnt_id.login = TEE_LOGIN_TRUSTED_APP;
 memcpy(&clnt_id.uuid, &sess->ctx->uuid, sizeof(TEE_UUID));
 /* 将需要被关闭的session从保存已经Open的session链表中移除 */
 return tee_ta_close_session(s, &utc->open_sessions, &clnt_id);
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 532

17.3.2 TA调用系统服务和安全驱动的实现

                                             动态TA实现具体功能时需要调用到安全驱动
或系统底层的资源。例如密码学操作、加载TA镜
像文件操作、对SE模块的操作等。这些资源提供的
接口都处于OP-TEE的内核空间，当用户空间的TA
需要使用这些资源来实现具体功能时，则需要让
TA的调用操作通过系统调用的方式进入到内核空
间，然后再调用特定的接口。

1.OP-TEE中服务和安全驱动的构成框架
OP-TEE使用系统服务的方式统一管理各功能
模块，安全驱动的操作接口会接入到系统服务中，
系统服务是在OP-TEE启动过程中执行initcall段中的
内容时被启动，service_init的启动等级设置为1，而
driver_init的启动等级设置成3。故在OP-TEE的启动
过程中，首先会启动使用service_init宏定义的功能
函数，再初始化安全驱动。各系统服务、安全驱动
和上层的TA之间的关系如图17-4所示。
OP-TEE中的系统服务提供了类似框架层的功
能，安全驱动初始化时会将驱动的操作接口注册到
对应的系统服务。TA可使用的只是各系统服务提
供的接口，如果系统服务并不需要给上层TA使

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 533

用，则不会暴露对应的接口给TA。当前的OP-TEE
中提供了如下三个重要的系统服务：

  ·密码学操作的系统服务；

  ·对SE功能模块进行操作的系统服务；
  ·提供加载TA镜像操作的系统服务；










    图17-4　动态TA与系统服务的关系

2.TA对系统服务接口的调用实现
  动态TA通过系统调用的方式进入到内核态，
然后在内核态调用各系统服务提供的接口。系统服
务为OP-TEE用户态程序提供的接口定义在类似于
tee_api_xxx.c的文件中，这些文件根据不同的功能


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 534

模块定义了用户空间需要使用的密码学操作接口、
SE操作接口等。这些接口的调用过程大致相同，如
图17-5所示。










    图17-5　动态TA调用驱动流程


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 535

  用户态的TA通过系统调用陷入OP-TEE内核空
间，然后在对应的系统调用中使用系统服务提供的
接口或变量来完成对安全驱动或其他资源的操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 536

17.3.3 TA对密码学系统服务的调用实现

      TA需要实现计算摘要、产生随机数、加解
密、签名验签等操作时就会调用到密码学系统服务
提供的接口。OP-TEE的内核空间中有一个变量
——crypto_ops，该变量中保存了各种密码学算法
的调用接口，其内容如下：



    const struct crypto_ops crypto_ops = {
    .name = "LibTomCrypt provider",      //该系统服务的名字
    //crypto service的初始化函数,在启动过程中将会执行crypto_ops.init指定的函数
    .init = tee_ltc_init,
    /* hash类算法的接口,用于计算摘要 */
    #if defined(_CFG_CRYPTO_WITH_HASH)
    .hash = {
          .get_ctx_size = hash_get_ctx_size,
          .init = hash_init,
          .update = hash_update,
          .final = hash_final,
    },
    #endif
    /* 对称加解密算法的接口用于对称加解密 */
    #if defined(_CFG_CRYPTO_WITH_CIPHER)
    .cipher = {
          .final = cipher_final,
          .get_block_size = cipher_get_block_size,
          .get_ctx_size = cipher_get_ctx_size,
          .init = cipher_init,
          .update = cipher_update,
    },
    #endif
    /* MAC类算法接口 */
    #if defined(_CFG_CRYPTO_WITH_MAC)
    .mac = {
          .get_ctx_size = mac_get_ctx_size,
          .init = mac_init,




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
          更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 537

      .update = mac_update,
      .final = mac_final,
    },
#endif
/* 对称验证加解密算法接口 */
#if defined(_CFG_CRYPTO_WITH_AUTHENC)
.authenc = {
      .dec_final = authenc_dec_final,
      .enc_final = authenc_enc_final,
      .final = authenc_final,
      .get_ctx_size = authenc_get_ctx_size,
      .init = authenc_init,
      .update_aad = authenc_update_aad,
      .update_payload = authenc_update_payload,
    },
#endif
/* 非对称算法（RSA）加解密,签名验签操作接口 */
#if defined(_CFG_CRYPTO_WITH_ACIPHER)
.acipher = {
#if defined(CFG_CRYPTO_RSA)
      .alloc_rsa_keypair = alloc_rsa_keypair,
      .alloc_rsa_public_key = alloc_rsa_public_key,
      .free_rsa_public_key = free_rsa_public_key,
      .gen_rsa_key = gen_rsa_key,
      .rsaes_decrypt = rsaes_decrypt,
      .rsaes_encrypt = rsaes_encrypt,
      .rsanopad_decrypt = rsanopad_decrypt,
      .rsanopad_encrypt = rsanopad_encrypt,
      .rsassa_sign = rsassa_sign,
      .rsassa_verify = rsassa_verify,
#endif
/* 生成key的接口 */
#if defined(CFG_CRYPTO_DH)
      .alloc_dh_keypair = alloc_dh_keypair,
      .gen_dh_key = gen_dh_key,
      .dh_shared_secret = do_dh_shared_secret,
#endif
/* DSA算法接口 */
#if defined(CFG_CRYPTO_DSA)
      .alloc_dsa_keypair = alloc_dsa_keypair,
      .alloc_dsa_public_key = alloc_dsa_public_key,
      .gen_dsa_key = gen_dsa_key,
      .dsa_sign = dsa_sign,
      .dsa_verify = dsa_verify,
#endif




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 538

    /* ECC算法接口 */
    #if defined(CFG_CRYPTO_ECC)
          /* ECDSA and ECDH */
          .alloc_ecc_keypair = alloc_ecc_keypair,
          .alloc_ecc_public_key = alloc_ecc_public_key,
          .gen_ecc_key = gen_ecc_key,
          .free_ecc_public_key = free_ecc_public_key,

          /* ECDSA only */
          .ecc_sign = ecc_sign,
          .ecc_verify = ecc_verify,
          /* ECDH only */
          .ecc_shared_secret = do_ecc_shared_secret,
    #endif
      },
    /* 大整数操作接口 */
      .bignum = {
          .allocate = bn_allocate,
          .num_bytes = num_bytes,
          .num_bits = num_bits,
          .compare = compare,
          .bn2bin = bn2bin,
          .bin2bn = bin2bn,
          .copy = copy,
          .free = bn_free,
          .clear = bn_clear
      },
    #endif /* _CFG_CRYPTO_WITH_ACIPHER */
    /* 随机系列算法接口 */
      .prng = {
          .add_entropy = prng_add_entropy,
          .read = prng_read,
      }
    };



1.crypto service的初始化
      OP-TEE在启动时会调用crypto_ops.init指定的
函数初始化整个密码学系统服务，即调用
tee_ltc_init函数来初始化密码学系统服务，该函数




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
          更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 539

将各种密码学算法的操作接口都注册到特定的变量
中，
  这些变量与对应算法的关系如表17-2所示。
表17-2 OP-TEE密码学系统服务变量与接口关系列
    表





启动密码学系统服务时，会调用
tee_ltc_reg_algs函数将对应算法的操作接口注册到
相关变量中，该函数内容如下：



static void tee_ltc_reg_algs(void)
{
#if defined(CFG_CRYPTO_AES)
 register_cipher(&aes_desc);      //注册AES算法的操作接口到cipher_descriptor中
#endif
#if defined(CFG_CRYPTO_DES)
 register_cipher(&des_desc);      //注册DES算法的操作接口到cipher_descriptor中
 register_cipher(&des3_desc);     //注册DES3算法的操作接口到cipher_descriptor中
#endif
#if defined(CFG_CRYPTO_MD5)
 register_hash(&md5_desc);        //注册MD5算法的操作接口到hash_descriptor中
#endif
#if defined(CFG_CRYPTO_SHA1)
 register_hash(&sha1_desc);       //注册SHA1算法的操作接口到hash_descriptor中
#endif
#if defined(CFG_CRYPTO_SHA224)
 register_hash(&sha224_desc);     //注册SHA224算法的操作接口到hash_descriptor中
#endif
#if defined(CFG_CRYPTO_SHA256)
 register_hash(&sha256_desc);     //注册SHA256算法的操作接口到hash_descriptor中
#endif




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 540

#if defined(CFG_CRYPTO_SHA384)
  register_hash(&sha384_desc);     //注册SHA384算法的操作接口到hash_descriptor中
#endif
#if defined(CFG_CRYPTO_SHA512)
  register_hash(&sha512_desc);     //注册SHA512算法的操作接口到hash_descriptor中
#endif
//注册prng算法的操作接口到prng_descriptor中
#if defined(CFG_WITH_SOFTWARE_PRNG)
#if defined(_CFG_CRYPTO_WITH_FORTUNA_PRNG)
 register_prng(&fortuna_desc);
#else
 register_prng(&rc4_desc);
#endif
#else
 register_prng(&prng_mpa_desc);
#endif
}


  注册过程就是将具体密码学算法的operation变
量保存到对应的数组变量元素中。密码学系统服务
初始化完成后，内核空间通过调用
crypto_ops.xxx.xxx的方式可调用到各种密码学算法
的具体实现。

2.TA调用具体算法的实现
调用crypto_ops中的接口时，会根据需要被调
用密码学算法的名称从数组变量中找到对应的元
素，然后使用元素中保存的算法操作接口来完成密
码学操作。如果芯片集成了硬件加解密引擎，加密
算法的实现，则可使用硬件cipher驱动提供的接口
来完成。本节以调用SHA1算法为例介绍其实现过
程。



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 541

  在TA中如果需要使用SHA1算法计算数据的摘
要，则需要调用TEE_DigestUpdate接口来实现，该
函数的完整执行过程如图17-6所示。










  图17-6 TEE_DigestUpdate操作的实现流程

  其他算法接口的调用过程与图17-6类似，只是
不同的算法类型查找的数组变量会有所不同，但是
执行流程大致相同。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 542

17.3.4　对SE功能模块进行操作的系统服务

  在OP-TEE内核空间调用类似tee_se_reader_xxx
的接口会调用到OP-TEE的SE系统服务，用于操作
具体的SE模块。若需要在TA中操作SE模块，可将
tee_se_reader_xxx类型的接口重新封装成系统调
用，然后在TA中调用封装的接口就能实现TA对SE
模块的操作。在OP-TEE中要使用具体的SE模块需
要初始化SE功能模块的系统服务，并挂载具体SE
模块的驱动。

                                          SE模块的系统服务是通过在OP-TEE启动过程
中调用tee_se_manager_init函数来实现的，该函数只
会初始化该系统服务的上下文空间，函数内容如
下：

static TEE_Result tee_se_manager_init(void)
{
  //定义SE service的上下文变量
  struct tee_se_manager_ctx *ctx = &se_manager_ctx;
  context_init(ctx);  //初始化该上下文变量的内容
  return TEE_SUCCESS;
}

  SE系统服务的上下文变量初始化完成后，就需
要挂载具体的SE模块驱动，将SE的操作接口注册
到上下文中。驱动的挂载和注册过程如图17-7所

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 543

    示。










  图17-7 SE模块驱动将接口注册到SE Manager
        Service的流程

   调用tee_se_reader_xxx类接口操作SE模块时会
获取SE系统服务的上下文——se_manager_ctx，然
后根据实际操作需求调用pcsc_passthru_reader_ops
变量中对应接口。pcsc_passthru_reader_ops变量中
的接口会根据需要操作的proxy编号找到具体的
proxy，然后调用该proxy中对应的接口完成整个操
作。





    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 544

17.3.5　加载TA镜像的系统服务

  当CA调用libteec库中用于创建与某个动态TA
的会话时，会从REE侧的文件系统中加载TA镜像文
件到OP-TEE，加载TA镜像的过程就会使用到该系
统服务提供的接口函数。

  本书第13章详细介绍了OP-TEE创建会话的实
现过程。OP-TEE会使用tee_ta_init_user_ta_session
函数来完成加载TA镜像并初始化会话的操作。加
载TA镜像文件时，会使用user_ta_store变量中的接
口发送RPC请求，通知tee_supplicant对REE侧文件
系统中的TA镜像文件执行打开、读取、获取TA镜
像文件大小、关闭TA镜像文件的操作。
user_ta_store变量在该系统服务启动时被赋值，具
体函数内容如下：

static const struct user_ta_store_ops ops = {
  .open = ta_open,          //发送RPC请求使tee_supplicant打开TA镜像文件
  .get_size = ta_get_size,  //发送RPC请求,获取TA镜像文件的大小
  .read = ta_read,          //发送RPC请求读取TA镜像的内容
  .close = ta_close,        //发送RPC请求关闭打开的TA镜像文件
};
/* OP-TEE启动时被调用,使用service_init宏将该函数编译到initcall段中 */
static TEE_Result register_supplicant_user_ta(void)
{
  return tee_ta_register_ta_store(&ops);
}
/* 将user_ta_store变量的地址赋值成ops */
TEE_Result tee_ta_register_ta_store(const struct user_ta_store_ops *ops)


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 545

{
 user_ta_store = ops;
 return TEE_SUCCESS;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 546

17.4　小结

  本章介绍了OP-TEE中各种系统服务以及TA调
用另外一个TA的原理和实现。每个TA具有独立的
运行空间，OP-TEE中的一个TA调用另一个TA执行
特定操作的过程是OP-TEE中的一种IPC的方式。
OP-TEE中各种系统服务起到类似框架层的作用，
安全驱动或其他子模块提供的操作接口会接入到对
应的系统服务中。系统服务通过接口变量或其他方
式将操作接口暴露给OP-TEE的内核空间，用户空
间的TA通过系统调用的方式在OP-TEE内核空间调
用这些接口，从而实现TA对安全驱动或其他模块
的资源操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 547

第四篇　应用开发篇

第18章　TA镜像的签名和加载
第19章　OP-TEE中的密码学算法

第20章　OP-TEE的安全存储
第21章　可信应用及客户端应用的开发
第22章　安全驱动的开发

第23章　终端密钥在线下发系统
第24章　基于OP-TEE的在线支付系统
第25章　TEE可信应用的使用领域










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 548

第18章　TA镜像的签名和加载

  使用OP-TEE实现特定功能需求则需要开发一
个特定的TA，TA调用GP规范定义的接口实现该功
能需求。TA镜像文件会被保存在REE侧的文件系统
中并以动态TA的方式运行于OP-TEE中，当用户需
要调用该TA的功能时，通过在CA中调用libteec库
中的接口，完成创建会话的操作，将REE侧文件系
统中的TA镜像文件加载到OP-TEE的用户空间运
行。为防止该TA镜像文件被篡改或被破坏，在加
载TA镜像文件的过程中会对该TA镜像文件的合法
性进行检查，只有校验通过的TA镜像文件才允许
运行于OP-TEE的用户空间。编译TA镜像文件过程
中会对TA镜像文件做电子签名操作。本章将详细
介绍TA镜像文件的编译、签名，以及加载过程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 549

18.1 TA镜像文件的编译和签名

  TA镜像文件在OP-TEE工程编译过程中生成，
也可通过单独调用TA目录下的脚本来进行编译，
但前提是OP-TEE工程被完整编译过。编译过程会
先生成原始的TA镜像文件，然后使用签名脚本对
该文件进行电子签名，并最终生成.ta文件，即最终
会被加载到OP-TEE中的TA镜像文件。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 550

18.1.1 TA镜像文件的编译

      对某个TA源代码目录中的Makefile文件执行
make指令可触发编译生成TA镜像文件的操作，该
Makefile文件将会包含optee_os/ta/mk/ta_dev_kit.mk
文件，该文件中会定义各种目标依赖关系和
Object，编译完目标和object后，编译器将会按照
optee_os/ta/arch/arm/link.mk文件中的依赖关系将目
标和object链接成xxx.ta文件，其中xxx是该TA
UUID的值。link.mk中的链接依赖关系如下：


    $(link-script-pp): $(link-script) $(MAKEFILE_LIST)
    @$(cmd-echo-silent) '  CPP $@'
    $(q)mkdir -p $(dir $@)
    $(q)$(CPP$(sm)) -Wp,-P,-MT,$@,-MD,$(link-script-dep) \
    $(link-script-cppflags-$(sm)) $< > $@
    $(link-out-dir)/$(binary).elf: $(objs) $(libdeps) $(link-script-pp)
    @$(cmd-echo-silent) '  LD  $@'
    $(q)$(LD$(sm)) $(ldargs-$(binary).elf) -o $@
    $(link-out-dir)/$(binary).dmp: $(link-out-dir)/$(binary).elf
    @$(cmd-echo-silent) '  OBJDUMP $@'
    $(q)$(OBJDUMP$(sm)) -l -x -d $< > $@
    $(link-out-dir)/$(binary).stripped.elf: $(link-out-dir)/$(binary).elf
    @$(cmd-echo-silent) '  OBJCOPY $@'
    $(q)$(OBJCOPY$(sm)) --strip-unneeded $< $@
    $(link-out-dir)/$(binary).ta: $(link-out-dir)/$(binary).stripped.elf \
        $(TA_SIGN_KEY)
    @echo ' SIGN $@'
    $(q)$(SIGN) --key $(TA_SIGN_KEY) --in $< --out $@



    $(link-out-dir)/$(binary).stripped.elf目标会删除




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 551

TA镜像文件中的调试信息。在原始TA镜像文件的
头部有一个ta_head段，该段中存放该TA的基本信
息以及被调用到的入口地址，该段的内容将会在加
载TA镜像到OP-TEE时和调用TA执行特定命令时被
使用到。存放在该段中的内容定义在
optee_os/ta/arch/arm/user_ta_header.c文件中，其内
容如下：


    const struct ta_head ta_head __section(".ta_head") = {
      .uuid = TA_UUID,  //TA的UUID值
      .stack_size = TA_STACK_SIZE + TA_FRAMEWORK_STACK_SIZE, //TA运行栈大小
      //该TA运行flag表示该TA将运行在用户空间
      .flags = TA_FLAG_USER_MODE | TA_FLAGS,
    #ifdef __ILP32__
      .entry.ptr32 = {  .lo = (uint32_t)__utee_entry },
    #else
      .entry.ptr64 = (uint64_t)__utee_entry, //定义该TA的入口函数
    #endif
    };


    对于该段中的entry.ptr64成员的作用，读者可
    参阅13.1节。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 552

    18.1.2　对TA镜像文件的签名

    生成原始的TA镜像文件后，
        编译系统会对该
    镜像文件进行签名生成最终的xxx.ta文件，
        该文件
    会被保存在REE侧的文件系统中。对原始TA镜像文
    件的签名操作是使用optee_os/scripts/sign.py文件来
    实现，
使用的私钥是optee_os/keys目录下的
    RSA2048密钥（default_ta.pem）。  当该TA需要被正
    式发布时，
                      应该使用OEM厂商自有的私钥替换掉该
    密钥。sign.py文件的内容如下：


    #!/usr/bin/env python
    #解析输入参数的函数
    def get_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--key', required=True, help='Name of key file')
    parser.add_argument('--in', required=True, dest='inf', \
    help='Name of in file')
    parser.add_argument('--out', required=True, help='Name of out file')
    return parser.parse_args()
    #脚本的入口函数
    def main():
    #导入各种依赖的python库
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    import struct
    #解析输入参数
    args = get_args()
    #打开输入的RSA key并读取该key的内容存放到key变量中
    f = open(args.key, 'rb')
    key = RSA.importKey(f.read())
    f.close()




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 553

#打开原始的TA镜像文件并读取该文件中的内容保存到img变量中
f = open(args.inf, 'rb')
img = f.read()
f.close()
#创建文件RSA签名结构体和sha256运算结构体
signer = PKCS1_v1_5.new(key)
h = SHA256.new()
digest_len = h.digest_size     #设定SHA256计算的输出结果长度
sig_len = len(signer.sign(h))  #设定签名长度
img_size = len(img)      #获取原始进行文件内容的长度
magic = 0x4f545348      # magic值
img_type = 0      # TA类型代号
algo = 0x70004830      # TEE_ALG_RSASSA_PKCS1_V1_5_SHA256（TA中验签对应的算法ID）
#将magic、img_type、img_size、algo、digese等信息按照一定的格式转成后存放在shdr变量中
shdr = struct.pack('<IIIIHH', \
magic, img_type, img_size, algo, digest_len, sig_len)
#将shdr变量和TA原始镜像文件的内容填充到SH256结构体数据区域中
h.update(shdr)
h.update(img)
#对h的摘要使用输入的私钥做RSA2048签名生成signature
sig = signer.sign(h)
#将shdr、shdr+img的SHA结果、signature、原始TA镜像文件内容写入到输出文件
f = open(args.out, 'wb')
f.write(shdr)
f.write(h.digest())
f.write(sig)
f.write(img)
f.close()
if __name__ == "__main__":
main()



签名完成后的TA镜像文件中的内容如图18-1所
示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 554

      图18-1 TA镜像文件格式
  签名后的TA镜像文件在被加载到OP-TEE内存
中之前，会使用签名信息对该TA镜像文件进行合
法性检查。TA镜像文件的ta_head段中的内容将会
在创建会话操作时被使用，主要告知系统如何调用
TA镜像中的创建会话、调用命令、关闭会话等操
作。




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 555

18.2 TA镜像的加载

  当CA第一次调用libteec库中的创建会话操作
时，如果被调用的TA是动态TA，则会触发OP-TEE
加载该动态TA镜像文件的操作。在加载过程中，
OP-TEE会发送PRC请求通知tee_supplicant从文件系
统中将UUID对应的TA镜像文件传递到OP-TEE，
OP-TEE会对接收到的数据进行验证操作，如果验
证通过则将相关段中的内容保存到OP-TEE用户空
间分配的TA内存中。加载TA镜像的整体流程如图
18-2所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 556

图18-2 OP-TEE加载动态TA镜像文件的流程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 557

18.2.1 REE侧获取TA镜像文件的内容

      OP-TEE通过调用rpc_load函数发送PRC请求，
将TA镜像文件的内容从REE侧加载到OP-TEE的共
享内存中。该函数会触发两次RPC请求，
        第一次
RPC请求用于获取TA镜像文件的大小，第二次RPC
请求是将TA镜像文件加载到OP-TEE的共享内存
中。触发第二次RPC请求之前，OP-TEE会在用户
空间先分配与TA镜像文件的大小相等的共享内存
区域，
        该区域用于存放TA镜像文件的内容。
rpc_load函数的内容如下：


    static TEE_Result rpc_load(const TEE_UUID *uuid, struct shdr **ta,
     uint64_t *cookie_ta, size_t *ta_size,
     struct mobj **mobj)
    {
     TEE_Result res;
     struct optee_msg_param params[2];
     uint64_t cta = 0;
     /* 输入参数检查 */
     if (!uuid || !ta || !cookie_ta || !mobj || !ta_size)
     return TEE_ERROR_BAD_PARAMETERS;
     /* 组合第一次RPC请求的参数,带入需要被加载的TA的UUID值,获取TA镜像文件的大小 */
     memset(params, 0, sizeof(params));
     params[0].attr = OPTEE_MSG_ATTR_TYPE_VALUE_INPUT;
     tee_uuid_to_octets((void *)&params[0].u.value, uuid);
     params[1].attr = OPTEE_MSG_ATTR_TYPE_TMEM_OUTPUT;
     params[1].u.tmem.buf_ptr = 0;
     params[1].u.tmem.size = 0;
     params[1].u.tmem.shm_ref = 0;
     /* 触发第一次RPC请求将返回TA镜像文件的大小 */
     res = thread_rpc_cmd(OPTEE_MSG_RPC_CMD_LOAD_TA, 2, params);
     if (res != TEE_SUCCESS)




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 558

     return res;
     /* 分配大小与TA镜像文件大小相当的共享内存 */
     *mobj = thread_rpc_alloc_payload(params[1].u.tmem.size, &cta);
     if (!*mobj)
     return TEE_ERROR_OUT_OF_MEMORY;
     /* 获取分配的共享内存的虚拟地址被保存在*ta中 */
     *ta = mobj_get_va(*mobj, 0);
     /* 检查虚拟地址是否有效 */
     assert(*ta);
     *cookie_ta = cta;
     *ta_size = params[1].u.tmem.size;
     /* 组合第二次RPC请求的参数 */
     params[0].attr = OPTEE_MSG_ATTR_TYPE_VALUE_INPUT;
     tee_uuid_to_octets((void *)&params[0].u.value, uuid);
     msg_param_init_memparam(params + 1, *mobj, 0, params[1].u.tmem.size,
         cta, MSG_PARAM_MEM_DIR_OUT);
     /* 触发第二次RPC请求,TA镜像文件的内容将会被读取到刚刚分配的共享内存中 */
     res = thread_rpc_cmd(OPTEE_MSG_RPC_CMD_LOAD_TA, 2, params);
     if (res != TEE_SUCCESS)
     thread_rpc_free_payload(cta, *mobj);
     return res;
    }



      对TA镜像文件内容的合法性检查，将TA加载
到OP-TEE用户空间TA的内存操作都是在共享内存
中完成的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 559

18.2.2　加载TA镜像的RPC请求

      加载TA过程中，ta_open函数会调用rpc_load函
数，
      该函数会调用thread_rpc_cmd来发送
OPTEE_MSG_RPC_CMD_LOAD_TA的RPC请求，
rpc_load函数会组合该类请求的相关数据结构变
量，
      然后通过调用thread_rpc函数向REE发送RPC请
求。thread_rpc_cmd函数的内容和介绍如下：


    uint32_t thread_rpc_cmd(uint32_t cmd, size_t num_params,
     struct optee_msg_param *params)
    {
     uint32_t rpc_args[THREAD_RPC_NUM_ARGS] = { OPTEE_SMC_RETURN_RPC_CMD };
     struct optee_msg_arg *arg;
     uint64_t carg;
     size_t n;
     struct optee_msg_param *arg_params;
     if (cmd != OPTEE_MSG_RPC_CMD_WAIT_QUEUE)
     plat_prng_add_jitter_entropy_norpc();

     /* 获取需要通过RPC机制发送到REE侧的参数内容 */
     if (!get_rpc_arg(cmd, num_params, &arg, &carg, &arg_params))
     return TEE_ERROR_OUT_OF_MEMORY;

     /* 复制操作 */
     memcpy(arg_params, params, sizeof(*params) * num_params);

     /* 转换成64位,以便兼容64位系统 */
     reg_pair_from_64(carg, rpc_args + 1, rpc_args + 2);
     /* 发送RPC请求,触发smc和挂起当前线程 */
     thread_rpc(rpc_args);
     for (n = 0; n < num_params; n++) {
     switch (params[n].attr & OPTEE_MSG_ATTR_TYPE_MASK) {
     case OPTEE_MSG_ATTR_TYPE_VALUE_OUTPUT:
     case OPTEE_MSG_ATTR_TYPE_VALUE_INOUT:




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 560

      case OPTEE_MSG_ATTR_TYPE_RMEM_OUTPUT:
      case OPTEE_MSG_ATTR_TYPE_RMEM_INOUT:
      case OPTEE_MSG_ATTR_TYPE_TMEM_OUTPUT:
      case OPTEE_MSG_ATTR_TYPE_TMEM_INOUT:
       params[n] = arg_params[n];
       break;
      default:
       break;
      }
     }
     return arg->ret;
    }



      在整个TA的加载过程中会发送两次RPC请求，
第一次是用于获取TA镜像文件的大小，第二次RPC
请求是通知tee_supplicant将TA镜像文件的内容加载
到OP-TEE提供的共享内存中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 561

18.2.3 RPC请求的发送

  RPC请求的发送是通过触发安全监控模式调用
（smc）来实现的，
    在触发安全监控模式调用
（smc）之前会将当前的线程挂起，
    并保存该线程
的运行上下文。该函数以汇编的形式实现内容如
下：



FUNC thread_rpc , :
UNWIND(.fnstart)
push         {r4-r5, lr}
UNWIND(.save  {r4-r5, lr})
push         {r0}
UNWIND(.save  {r0})
bl     thread_save_state       //保存状态
mov r4, r0                     /* 保存CPSR寄存器的值 */
bl     thread_get_tmp_sp       //获取tmp栈空间
ldr r5, [sp]
cps #CPSR_MODE_SVC             /* 切换到SVC模式 */
mov sp, r0                     /* 切换到tmp栈空间*/
mov r0, #THREAD_FLAGS_COPY_ARGS_ON_RETURN
mov r1, r4                     /* 回复CPSR寄存器的内容 */
ldr r2, =.thread_rpc_return    //thred_rpc_return为当前线程恢复回来之后的PC的值
bl    thread_state_suspend     //挂起当前线程
mov r4, r0
ldr r0, =TEESMC_OPTEED_RETURN_CALL_DONE
ldm r5, {r1-r3}
smc #0                         //触发smc操作,切回到REE侧
b     .
.thread_rpc_return:
pop {r12}
stm r12, {r0-r5}
pop {r4-r5, pc}
UNWIND(.fnend)
END_FUNC thread_rpc





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
             更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 562

  当REE处理完RPC请求后，会发送标准安全监
控模式调用（std smc）重新进入到OP-TEE中，OP-
TEE根据返回的安全监控模式调用（smc）的类型
判定当前的安全监控模式调用（smc）是RPC的返
回还是普通的安全监控模式调用（smc）。如果该
安全监控模式调用（smc）是返回RPC请求的处理
结果，则会进入到thread_resume_from_rpc分支恢复
之前被挂起的线程。在thread_rpc函数中已经指定了
恢复该线程之后程序执行的入口函数——
thread_rpc_return，到此一次完整的RPC请求也就被
处理完毕。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 563

18.2.4　读取TA镜像文件内容到共享内存

   rpc_load函数发起第二次RPC请求时才会将TA
镜像文件的内容读取到OP-TEE提供的共享内存
中，共享内存的分配是在rpc_load函数中调用
thread_rpc_alloc_payload函数来实现的。分配的共
享内存的地址将会被保存到ta_handle变量的nw_ta
成员中，读取到的TA镜像文件的内容将会被加载
到OP-TEE用户空间TA运行的内存中，代码内容解
释见16.2.1节。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 564

18.3 TA镜像合法性的验证

  当TA镜像文件被加载到共享内存后，OP-TEE
会对获取到的数据进行合法性检查。检查TA镜像
文件中的哈希（hash）值、magic值、flag值等是否
一致，并对镜像文件中的电子签名部分做验证。整
个验证过程如18-3所示。










    图18-3 TA镜像文件验证过程流程







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 565

    18.3.1　验证TA镜像合法性使用的RSA公钥的产生
    和获取

编译整个工程时会生成一个ta_pub_key.c文
    件，该文件中存放的是RSA公钥，用于验证TA镜像
    文件合法性。该文件是在编译gensrcs-y目标中的
    ta_pub_key成员时生成的，该部分的内容定义在
    optee_os/core/sub.mk文件中，其内容如下：

    subdirs-y += kernel
    subdirs-y += tee
    subdirs-y += drivers
    ifeq ($(CFG_WITH_USER_TA)-$(CFG_REE_FS_TA),y-y)
    gensrcs-y += ta_pub_key
    produce-ta_pub_key = ta_pub_key.c
    depends-ta_pub_key = $(TA_SIGN_KEY)
    recipe-ta_pub_key = scripts/pem_to_pub_c.py --prefix ta_pub_key \
    --key $(TA_SIGN_KEY) --out $(sub-dir-out)/ta_pub_key.c
    cleanfiles += $(sub-dir-out)/ta_pub_key.c
    endif

    编译ta_pub_key目标时会调用recipe-ta_pub_key
    命令来生成ta_pub_key.c文件，该文件被保存在
    optee_os/out/arm/core/目录中。recipe-ta_pub_key命
    令调用pem_to_pub_c.py文件解析optee_os/keys目录
    中的RSA密钥来获取RSA公钥，并将该公钥保存到
    ta_pub_key.c文件中。pem_to_pub_c.py脚本的内容
    如下：


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 566

#输入参数解析函数
def get_args():
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', required=True, \
help='Prefix for the public key exponent and modulus in c file')
parser.add_argument('--out', required=True, \
help='Name of c file for the public key')
parser.add_argument('--key', required=True, help='Name of key file')
return parser.parse_args()
#生成ta_pub_key.c文件的主要函数
def main():
import array
from Crypto.PublicKey import RSA
from Crypto.Util.number import long_to_bytes
#解析输入参数
args = get_args();
#打开输入的pem格式的RSA key并读取内容
f = open(args.key, 'r')
key = RSA.importKey(f.read())
f.close
#创建ta_pub_key.c文件
f = open(args.out, 'w')
#将include语句的内容写入到ta_pub_key.c文件中
f.write("#include <stdint.h>\n");
f.write("#include <stddef.h>\n\n");
#写入ta_pub_key_exponent变量的内容和值
f.write("const uint32_t " + args.prefix + "_exponent = " +
str(key.publickey().e) + ";\n\n")
#写入ta_pub_key_modulus变量的内容和值
f.write("const uint8_t " + args.prefix + "_modulus[] = {\n")
i = 0;
for x in array.array("B", long_to_bytes(key.publickey().n)):
f.write("0x" + '{0:02x}'.format(x) + ",")
i = i + 1;
if i % 8 == 0:
    f.write("\n");
else:
    f.write(" ");
f.write("};\n");
#写入ta_pub_key_modulus_size变量的值
f.write("const size_t " + args.prefix + "_modulus_size = sizeof(" + \
args.prefix + "_modulus);\n")
f.close()




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 567

    if __name__ == "__main__":
    main()


     生成的ta_pub_key.c文件中将定义三个全局变
量并赋值，这三个变量就是RSA公钥的内容，作用
和内容分别为：


    ta_pub_key_exponent         //RSA公钥中的E值
    ta_pub_key_modulus          //RSA公钥中的N值
    ta_pub_key_modulus_size     //RSA key的长度,在OP-TEE中该值为256,也即表示该RSA key为RSA 2048


    这三个变量作为全局变量被使用，在对TA镜
    像文件的签名信息进行验签操作时被使用到。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 568

18.3.2 TA镜像文件合法性的检查

      对TA镜像文件内容合法性的检查是通过调用
check_shdr函数来实现的，该函数除了会对TA镜像
文件中的签名信息进行验签操作外，
        还会校验TA
镜像文件的shdr部分，check_shdr代码内容如下：


    static TEE_Result check_shdr(struct shdr *shdr)
    {
     struct rsa_public_key key;
     TEE_Result res;
     //将全局变量ta_pub_key_exponent转成RSA公钥的E值
     uint32_t e = TEE_U32_TO_BIG_ENDIAN(ta_pub_key_exponent);
     size_t hash_size;
     /* 校验shdr中的magic值和img_type值 */
     if (shdr->magic != SHDR_MAGIC || shdr->img_type != SHDR_TA)
     return TEE_ERROR_SECURITY;
     /* 检查shdr中的algo成员指定的算法类型是否合法 */
     if (TEE_ALG_GET_MAIN_ALG(shdr->algo) != TEE_MAIN_ALGO_RSA)
     return TEE_ERROR_SECURITY;
     /* 获取验签操作时需要使用的摘要的大小 */
     res = tee_hash_get_digest_size(TEE_DIGEST_HASH_TO_ALGO(shdr->algo),
&hash_size);
     if (res != TEE_SUCCESS)
     return res;
     /* 检查shdr中的hash_size是否正确 */
     if (hash_size != shdr->hash_size)
     return TEE_ERROR_SECURITY;
     /* 检查OP-TEE中提供的算法接口crypto_ops中的成员是否有效 */
     if (!crypto_ops.acipher.alloc_rsa_public_key ||
     !crypto_ops.acipher.free_rsa_public_key ||
     !crypto_ops.acipher.rsassa_verify ||
     !crypto_ops.bignum.bin2bn)
     return TEE_ERROR_NOT_SUPPORTED;
     /* 分配RSA公钥在算法接口中的存储空间 */
     res = crypto_ops.acipher.alloc_rsa_public_key(&key, shdr->sig_size);
     if (res != TEE_SUCCESS)



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 569

        return res;
     /* 将RSA公钥中的E值转换成大整数*/
     res = crypto_ops.bignum.bin2bn((uint8_t *)&e, sizeof(e), key.e);
     if (res != TEE_SUCCESS)
        goto out;
     /* 将ta_pub_key_modulus变量的值作为RSA公钥中的N值,并转换成大整数*/
     res = crypto_ops.bignum.bin2bn(ta_pub_key_modulus,
            ta_pub_key_modulus_size, key.n);
     if (res != TEE_SUCCESS)
        goto out;
     /* 使用TA镜像文件中的摘要部分和签名信息部分做RSA的验签操作 */
     res = crypto_ops.acipher.rsassa_verify(shdr->algo, &key, -1,
        SHDR_GET_HASH(shdr), shdr->hash_size,
        SHDR_GET_SIG(shdr), shdr->sig_size);
    out:
     crypto_ops.acipher.free_rsa_public_key(&key);
     if (res != TEE_SUCCESS)
        return TEE_ERROR_SECURITY;
     return TEE_SUCCESS;
    }



      校验TA镜像签名时使用的RSA公钥是由
ta_public_key.c文件中的ta_pub_key_exponent和
ta_pub_key_modulus变量的值组成。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 570

18.4　加载TA镜像到OP-TEE的用户空间

  待共享内存中的TA镜像文件校验通过后，OP-
TEE就会将共享内存中的TA的内容复制到OP-TEE
用户空间的TA内存区域，并初始化该TA运行于用
户空间时的上下文。这些操作通过调用load_elf函数
来实现。整个TA镜像文件加载到OP-TEE用户空间
的过程如图18-4所示。










  图18-4　加载TA镜像文件到用户空间的流程
  TA镜像文件的TA原始文件是ELF格式，在加
载前需要先解析该ELF格式文件，获取该ELF文件


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 571

中哪些段在运行时是必需的、需要保存在什么位
置，从而决定用户空间中该TA运行时需要的内存
大小和堆栈空间大小。解析完后再将ELF格式的必
要段的内容复制到为该TA分配的OP-TEE用户空间
内存中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 572

18.5 TA运行上下文的初始化

      TA镜像的内容从共享内存复制到OP-TEE用户
空间内存区域后会返回到ta_load函数继续执行，
        执
行初始化该TA运行上下文的操作，
        并将该上下文
添加到OP-TEE的TA运行上下文队列中。ta_load的
内容如下：



    static TEE_Result ta_load(const TEE_UUID *uuid,
                const struct user_ta_store_ops *ta_store,
                struct tee_ta_ctx **ta_ctx)
    {
     TEE_Result res;
     uint32_t mandatory_flags = TA_FLAG_USER_MODE | TA_FLAG_EXEC_DDR;
     uint32_t optional_flags = mandatory_flags | TA_FLAG_SINGLE_INSTANCE |
      TA_FLAG_MULTI_SESSION | TA_FLAG_SECURE_DATA_PATH |
      TA_FLAG_INSTANCE_KEEP_ALIVE | TA_FLAG_CACHE_MAINTENANCE;
     struct user_ta_ctx *utc = NULL;
     struct ta_head *ta_head;
     struct user_ta_store_handle *ta_handle = NULL;
     /* 从REE侧获取TA镜像文件 */
     res = ta_store->open(uuid, &ta_handle);
     if (res != TEE_SUCCESS)
      return res;
     /* 分配内存用于保存该TA的运行上下文信息 */
     utc = calloc(1, sizeof(struct user_ta_ctx));
     if (!utc) {
      res = TEE_ERROR_OUT_OF_MEMORY;
      goto error_return;
     }
     /*初始化必要队列*/
     TAILQ_INIT(&utc->open_sessions);
     TAILQ_INIT(&utc->cryp_states);
     TAILQ_INIT(&utc->objects);
     TAILQ_INIT(&utc->storage_enums);
     /* 将共享内存中的TA镜像文件复制到OP-TEE用户空间TA的内存中 */




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 573

res = load_elf(utc, ta_store, ta_handle);
if (res != TEE_SUCCESS)
 goto error_return;
/* 获取该TA被加载到OP-TEE用户空间的虚拟地址 */
utc->load_addr = tee_mmu_get_load_addr(&utc->ctx);
/* 设定ta_head部分指向该TA在用户空间的起始地址 */
ta_head = (struct ta_head *)(vaddr_t)utc->load_addr;
/* 对比该TA的ta_head中的UUID值与请求加载的TA的UUID值是否一致 */
if (memcmp(&ta_head->uuid, uuid, sizeof(TEE_UUID)) != 0) {
 res = TEE_ERROR_SECURITY;
 goto error_return;
}
/* 校验该TA中ta_head中flag的设定是否合法 */
if ((ta_head->flags & optional_flags) != ta_head->flags ||
 (ta_head->flags & mandatory_flags) != mandatory_flags) {
 EMSG("TA flag issue: flags=%x optional=%x mandatory=%x",
         ta_head->flags, optional_flags, mandatory_flags);
 res = TEE_ERROR_BAD_FORMAT;
 goto error_return;
}
/* 设定TA运行上下文中的相关成员 */
DMSG("ELF load address 0x%x", utc->load_addr);
utc->ctx.flags = ta_head->flags;
utc->ctx.uuid = ta_head->uuid;
utc->entry_func = ta_head->entry.ptr64;
utc->ctx.ref_count = 1;
/* 初始化该TA的内存保护机制 */
condvar_init(&utc->ctx.busy_cv);
/* 将该运行上下文插入到全局的可用TA上下文队列中 */
TAILQ_INSERT_TAIL(&tee_ctxes, &utc->ctx, link);
*ta_ctx = &utc->ctx;
tee_mmu_set_ctx(NULL);
ta_store->close(ta_handle);
return TEE_SUCCESS;
error_return:
ta_store->close(ta_handle);
tee_mmu_set_ctx(NULL);
if (utc) {
 pgt_flush_ctx(&utc->ctx);
 tee_pager_rem_uta_areas(utc);
 tee_mmu_final(utc);
 mobj_free(utc->mobj_code);
 mobj_free(utc->mobj_stack);
 free(utc);
}




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 574

return res;
}

 待ta_load执行完后，加载TA镜像到OP-TEE的
操作也就全部完成。在CA中执行的创建会话操作
会得到该TA的会话ID，用于REE侧的CA对该TA执
行调用命令的操作。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 575

18.6　小结

  本章节主要介绍OP-TEE在执行创建会话操作
时加载动态TA的全过程，OP-TEE通过发送RPC请
求通知REE侧的tee_supplicant将文件系统中的TA镜
像文件加载到OP-TEE分配的共享内存中，然后对
共享内存中的数据进行合法性检查，并将必要段的
内容复制到分配的OP-TEE用户空间。本章节同时
也介绍了对TA镜像文件进行合法性检查时使用的
密钥的生成以及TA镜像文件的签名和验签过程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 576

第19章　OP-TEE中的密码学算法

  OP-TEE根据GP规范实现了常用的加解密、签
名验签和计算摘要的密码学算法的基础框架。如果
芯片厂商需使用硬件的密码学引擎来实现这些算
法，则只需替换掉对应的底层算法实现接口即可。
对于上层用户而言无需修改任何代码，只需按照GP
规范，调用对应的接口组合即可实现对数据的加解
密、摘要计算和数据的签名验签操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 577

19.1　算法使用示例

OP-TEE根据GP规范支持当前主流的基本算
法，包括RAS、AES、HMAC、SHA、RANDOM
等。本章将介绍在OP-TEE中添加一个TA和CA来调
用上述算法的GP接口，实现对数据的加密、解密、
签名、验签、计算哈希值等操作。

    在xtest中也有上述算法的接口调用示例，但比
较零散，并不适合开发者直接引用。例如在xtest
中，如果要对数据进行AES加密操作，在xtest中可
能需要在TA和CA之间多次传递数据来才可完成。
而正常的用户希望能达到的效果是在CA中带入需
要被处理的数据，调用接口就能够对数据完成AES
加密操作。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 578

19.1.1　示例代码获取和集成

   本章提供的示例代码中的TA实现了在OP-TEE
中完整调用GP接口实现上述算法。代码已经上传到
GitHub上，使用如下指令可以下载：

 git clone https://GitHub.com/shuaifengyun/basicAlg_use.git

   下载完代码后，将该TA和CA集成到OP-TEE
中，并需要修改OP-TEE源代码build目录下的
qemu.mk（开发者板级对应的mk文件）和
common.mk文件。修改完成后，整体编译OP-
TEE，然后就能使用该份示例代码来使用OP-TEE中
提供的基本算法的操作。

   获取到示例代码之后，切换到如下build目录
下，然后使用git apply命令合入补丁文件后就可将
该示例集成到OP-TEE，合入补丁的操作步骤如
下：

   1）将示例代码中的
basicAlg_common_3.0.0.patch文件和
basicAlg_qemu_3.0.0.patch文件复制到build目录中。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 579

   2）切换到build目录，使用如下命令合入补
丁：

  git apply basicAlg_common_3.0.0.patch
  git apply basicAlg_qemu_3.0.0.patch

   合入补丁之后就可使用make-f qemu.mk all编译
整个工程，然后使用make-f qemu.mk run-only来启
动OP-TEE，在启动的正常世界状态的终端执行
basicAlgUse相关命令就能实现该示例的CA对TA的
调用。示例代码的运行效果如图19-1所示。










    图19-1 basicAlg示例运行效果



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 580

19.1.2　板级编译文件的修改

                                将该示例的TA和CA添加到OP-TEE中，则需要
修改读者开发环境对应的mk文件。以使用QEMU方
式运行OP-TEE为例，需要修改qemu.mk文件，添加
该示例代码的编译目标，修改步骤如下：

1）添加basicAlg_use的编译目标：

############################################################################
# basic algorithm use
############################################################################
basicAlg_use: basicAlg_use-common
basicAlg_use-clean: basicAlg_use-clean-common

2）将basicAlg_use和basicAlg_use-clean添加到
全局的all和clean目标依赖关系中：

all: bios-qemu qemu soc-term optee-examples basicAlg_use
clean: bios-qemu-clean busybox-clean linux-clean optee-os-clean \
optee-client-clean qemu-clean soc-term-clean check-clean \
optee-examples-clean basicAlg_use-clean

添加部分的主要作用是定义basicAlg_use目标
并建立该编译目标与all的依赖关系——在编译整个
OP-TEE工程时会被使用到。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 581

19.1.3　通用编译文件的修改

修改完板级编译的mk文件后，
                       还需修改
build/common.mk文件。修改的内容主要是将
basicAlg_use的编译目标集成到系统编译中， 需要
修改的内容如下：

1）定义basicAlg_use路径变量。


BASIC_ALG_USE_PATH    ?= $(ROOT)/basicAlg_use



2）添加basicAlg_use的目标依赖，修改filelist-
tee-common目标的依赖关系如下：


filelist-tee-common: optee-client xtest optee-examples basicAlg_use



3）增加TA和CA的common目标：


############################################################################
# basicAlg use
###########################################################################
OPTEE_BASICALG_COMMON_FLAGS ?= HOST_CROSS_COMPILE=$(CROSS_COMPILE_NS_USER)\
TA_CROSS_COMPILE=$(CROSS_COMPILE_S_USER) \
TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR) \
TEEC_EXPORT=$(OPTEE_CLIENT_EXPORT)
.PHONY: basicAlg_use-common
basicAlg_use-common: optee-os optee-client




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 582

    $(MAKE) -C $(BASIC_ALG_USE_PATH) $(OPTEE_BASICALG_COMMON_FLAGS)
    OPTEE_BASICALG_CLEAN_COMMON_FLAGS ?= TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR)
    .PHONY: basicAlg_use-clean-common
    basicAlg_use-clean-common:
    $(MAKE) -C $(BASIC_ALG_USE_PATH) $(OPTEE_BASICALG_CLEAN_COMMON_FLAGS) clean



    4）添加clean操作的依赖关系。


    optee-os-clean-common: xtest-clean optee-examples-clean basicAlg_use-clean



    5）在filelist-tee-common中添加TA和CA镜像需
    要被打包到文件系统中的操作：



    @echo "#basic alg use" >> $(fl)
    @if [ -e $(BASIC_ALG_USE_PATH)/host/basicAlgUse ]; then \
      echo "file /bin/basicAlgUse" \
"$(BASIC_ALG_USE_PATH)/host/basicAlgUse 755 0 0" >> $(fl); \
      echo "file /lib/optee_armtz/ebb6f4b5-7e33-4ad2-9802-e64f2a7cc20c.ta" \
      "$(BASIC_ALG_USE_PATH)/ta/ebb6f4b5-7e33-4ad2-9802-e64f2a7cc20c.ta 444 0 0" >> $(fl); \
    fi










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 583

19.1.4　编译运行

   修改完毕后，进入到build目录中运行make-f
qemu.mk all指令编译整个工程。关于如何使用
basicAlg_use的CA可执行文件，请参阅basicAlg_use
目录中的README.md一文。

   编译完成后，在build目录下执行make-f
qemu.mk run-only开始启动QEMU+OP-TEE的运行
环境，系统启动后在REE终端直接运行
REAMME.md中的指令，就可调用该TA来执行相关
的算法。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 584

19.2 OP-TEE中的SHA算法

             SHA算法主要用于计算数据的摘要，该算法的
特点是具有不可逆性，外界不可能通过摘要的值计
算出原始数据的内容。SHA算法主要包括SHA1、
SHA256、SHA244、SHA384、SHA512。OP-TEE
使用同一套接口来实现这些算法，只是在调用各接
口函数时输入的参数有所不同，各SHA算法执行后
输出的数据长度和算法ID如表19-1所示。
表19-1         SHA算法执行后输出的数据长度和算法ID










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 585

19.2.1 TA中使用SHA算法的实现

  GP规范定义了一类用于在TEE侧计算摘要的接
口函数，一次完整的摘要计算需要在TA中带参数
依次调用如下函数：

 TEE_AllocateOperation
 TEE_DigestUpdate
 TEE_DigestDoFinal

  TEE_AllocateOperation函数会分配一个算法操
作句柄，用于规定当前操作是计算摘要操作还是加
解密操作或签名验签操作。TEE_DigestUpdate用于
将需要计算摘要的数据填充到操作句柄的数据区域
中。TEE_DigestDoFinal用于触发最终的计算摘要操
作。上述三个接口函数最终都会通过系统调用陷入
OP-TEE内核空间，在OP-TEE内核空间调用密码学
系统服务提供的接口完成摘要的计算。在调用
TEE_AllocateOperation函数时需要带入算法ID和模
式。







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 586

19.2.2 SHA算法实现接口说明

 TA依次调用在19.2.1节提到的三个接口函数就
能完成使用SHA算法计算数据的摘要。关于使用示
例请参考19.1节。现对上述三个接口的作用和参数
做如下说明：

1.TEE_AllocateOperation

 函数原型：

 TEE_Result TEE_AllocateOperation(TEE_OperationHandle *operation, uint32_t algorithm, nt32_t mode,uint32_t maxKeySize)

 函数作用描述：

 分配一个进行密码操作的操作句柄，并设定算
法类型和模式。

 参数说明：

 operation：指向所创建的密码学操作句柄地址
的指针变量，后续操作需要使用该指针变量进行数
据填充和摘要计算；

 algorithm：算法类型，使用时填入需要调用的

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 587

算法ID；
mode：操作模式，使用SHA算法时该值必须填
入TEE_MODE_DIGEST；

maxKeySize：key的最大长度，以bit为单位，
在使用SHA算法时该值为0。
函数返回值：

TEEC_SUCCESS：初始化操作成功；

TEE_ERROR_OUT_OF_MEMORY：内存空间
不足；

TEE_ERROR_NOT_SUPPORTED：mode、
algorithm或者maxKeySize参数不匹配。

2.TEE_DigestUpdate

函数原型：

void TEE_DigestUpdate(TEE_OperationHandle operation,const void *chunk,
int32_t chunkSize)

函数作用描述：


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 588

  将需要进行摘要计算的数据添加到密码学操作
句柄的数据区域中。

  参数说明：

  operation：指向创建好的密码学操作句柄；
  chunk：需要填入的数据的起始地址；
  chunkSize：填入的数据的长度。

  函数返回值：

  无。

3.TEE_DigestDoFinal

  函数原型：

 TEE_Result TEE_DigestDoFinal(TEE_OperationHandle operation, const void *chunk, uint32_t chunkLen, void *hash, uint32_t *hashLen)

  函数作用描述：

  对已经填入的数据进行哈希计算得到数据的摘
要。

  参数说明：

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 589

operation：指向创建好的密码学操作句柄；
chunk：最后需要被填入的数据块地址；

chunkLen：数据块最后的长度；
hash：存放摘要的地址；
hashLen：摘要的长度。

函数返回值：

TEEC_SUCCESS：初始化操作成功；
TEE_ERROR_SHORT_BUFFER：hash参数给
定的buffer长度不够。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 590

19.3 OP-TEE中的AES算法

AES算法是对称加解密算法，使用时需要利用
AES密钥和初始化向量IV来加解密数据。解密操作
时必须使用相同的AES密钥和IV值，否则解密出来
的数据是不正确的。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 591

19.3.1 TA中使用AES算法的实现

      GP规范中定义了一类用于在TEE侧使用AES算
法对数据进行加解密的接口函数，完成一次完整的
AES加解密需要在TA中带参数依次调用如下函数：


    TEE_AllocateOperation
    TEE_AllocateTransientObject
    TEE_InitRefAttribute
    TEE_PopulateTransientObject
    TEE_SetOperationKey
    TEE_CipherInit
    TEE_CipherUpdate
    TEE_CipherDoFinal



    这些接口的名称以及作用如表19-2所示。
    表19-2 AES算法接口说明










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 592

  在执行AES操作之前，需要将AES密钥作为一
个object填充到操作句柄中，然后填充数据进行初
始化，再执行加解密操作，至于是加密还是解密操
作由句柄的mode参数决定。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 593

19.3.2 AES算法实现接口说明

  在TA中依次调用19.3.1节介绍的8个接口函数
就能实现完整的AES算法的加解密操作。示例代码
请参考19.1节。现对上述8个接口的作用和参数说明
如下。

1.TEE_AllocateOperation

  参阅19.2.2节中的说明。对于AES操作，算法
ID为AES各种类型的算法ID值。mode指定是加密还
是解密，TEE_MODE_ENCRYPT表示执行AES加密
操作，TEE_MODE_DECRYPT表示执行AES解密操
作。

2.TEE_AllocateTransientObject

  函数原型：

TEE_Result TEE_AllocateTransientObject(TEE_ObjectType objectType, uint32_t maxKeySize, TEE_ObjectHandle *object)

  函数作用描述：

  分配一个未初始化的临时object空间。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 594

  参数说明：

  objectType：需要分配的临时object的类型；

  maxKeySize：该类型object的密钥长度的最大
值；

  object：指向分配的临时object空间变量的地
址。

  函数返回值：

  TEEC_SUCCESS：分配操作成功；
  TEE_ERROR_OUT_OF_MEMORY：剩余内存
空间不足以分配该object；
  TEE_ERROR_NOT_SUPPORTED：密钥的大
小与需要分配的object的类型不匹配。

3.TEE_InitRefAttribute

  函数原型：

void TEE_InitRefAttribute(TEE_Attribute *attr, uint32_t attributeID, const void *buffer, nt32_t length)




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 595

函数作用描述：

使用buffer中的数据初始化某个属性变量。

参数说明：

attr：指向需要被初始化的属性变量；
attributeID：属性ID，对于AES算法，该值为
TEE_ATTR_SECRET_VALUE；

buffer：需要被填充到该属性变量中的数据；
length：buffer变量中数据的长度；
hashLen：摘要的长度。

函数返回值：

无。

4.TEE_PopulateTransientObject

函数原型：

TEE_Result TEE_PopulateTransientObject(TEE_ObjectHandle object,const TEE_Attribute *ttrs, uint32_t attrCount)



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 596

函数作用描述：

将属性变量赋值到object中。

参数说明：

object：指向需要被赋值的object变量；
attrs：指向属性变量；

attrCount：指定需要被赋值到object中的属性变
量的个数。

函数返回值：

TEEC_SUCCESS：分配操作成功；

TEE_ERROR_BAD_PARAMETERS：输入参
数不合法。

5.TEE_SetOperationKey

函数原型：

TEE_Result TEE_SetOperationKey(TEE_OperationHandle operation,
TEE_ObjectHandle key)



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 597

  函数作用描述：

  将存放密钥的object中的相关内容保存到操作
句柄中。

  参数说明：

  operation：指向操作句柄；
  key：指向存放密钥信息的object变量。

  函数返回值：

  TEEC_SUCCESS：分配操作成功；
  TEE_ERROR_CORRUPT_OBJECT：保存密钥
的object损坏；

  TEE_ERROR_STORAGE_NOT_AVAILABLE：
object试图存放在操作句柄当中不可用的保存区
域。

6.TEE_CipherInit

  函数原型：

void TEE_CipherInit(TEE_OperationHandle operation, const void *IV, uint32_t IVLen)


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 598

函数作用描述：

使用初始化向量初始化对称加密操作。

参数说明：

operation：指向操作句柄；
IV：AES操作时的初始化向量；

IVLen：初始化向量的长度。

函数返回值：

无。

7.TEE_CipherUpdate

函数原型：

TEE_Result TEE_CipherUpdate(TEE_OperationHandle operation, const void *srcData, uint32_t srcLen, void *destData, uint32_t *destLen)

函数作用描述：

开始使用AES算法解密或者解密数据。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 599

参数说明：

operation：指向操作句柄；

srcData：需要被加密或解密的数据；
srcLen：需要被加密或者解密的数据长度；
destData：保存执行解密或加密操作后的数据
的地址；

destLen：记录输出数据长度变量的地址。

函数返回值：

TEEC_SUCCESS：分配操作成功；

TEE_ERROR_SHORT_BUFFER：用于保存输
出数据的buffer长度不够。

8.TEE_CipherDoFinal

函数原型：

TEE_Result TEE_CipherDoFinal(TEE_OperationHandle operation,
const void *srcData, uint32_t srcLen,void *destData, uint32_t *destLen)



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 600

 函数作用描述：

 完成加解密操作。

 参数说明：

 operation：指向操作句柄；
 srcData：剩下的需要被加解密的数据；

 srcLen：需要被加密或者解密的数据长度；
 destData：保存执行解密或加密操作后的数据
的地址；

 destLen：记录输出数据长度变量的地址。

 函数返回值：

 TEEC_SUCCESS：分配操作成功；
 TEE_ERROR_SHORT_BUFFER：用于保存输
出数据的buffer长度不够。






 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 601

19.4 OP-TEE中的RSA算法

  RSA算法是非对称算法，RSA算法支持加密、
解密、签名、验签操作，执行上述操作时需要使用
RSA私钥或者RSA公钥，操作与密钥类型的对应关
系如表19-3所示。
   表19-3 RSA算法操作与密钥类型关系










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 602

19.4.1 TA中使用RSA算法的实现

GP规范中定义了一类用于在TEE侧使用RSA算
法对数据进行加解密以及签名验签操作的接口函
数，完成一次完整的RSA加解密需要在TA中带参数
调用如下函数：

TEE_AllocateOperation
TEE_AllocateTransientObject
TEE_PopulateTransientObject
TEE_SetOperationKey
TEE_AsymmetricEncrypt
TEE_AsymmetricDecrypt
TEE_AsymmetricSignDigest
TEE_AsymmetricVerifyDigest

这些接口的名称以及作用如表19-4所示。
    表19-4 RSA算法接口名称与作用






在执行RSA操作之前需要将密钥作为一个


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 603

object填充到操作句柄中，然后使用对应的函数实
现RSA的加密、解密、签名、验签操作。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 604

19.4.2 RSA算法实现接口说明

1.TEE_AllocateOperation

参阅19.2.1节中的说明，对于RSA操作，算法
ID可查阅GP规范文档。对于mode参数，如果mode
值为TEE_MODE_ENCRYPT，则执行加密操作，
如果mode值为TEE_MODE_DECRYPT，则执行解
密操作，如果mode值为TEE_MODE_SIGN，则执
行签名操作，如果mode值为
TEE_MODE_VERIFY，则执行验签操作。

2.TEE_AllocateTransientObject

              请参阅19.3.2节中的说明。

3.TEE_PopulateTransientObject

              请参考19.3.2节中的说明。

4.TEE_SetOperationKey

              请参考19.3.2节中的说明。

5.TEE_AsymmetricEncrypt


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 605

  函数原型：

 TEE_Result TEE_AsymmetricEncrypt(TEE_OperationHandle operation, const TEE_Attribute *params, uint32_t paramCount, const void *srcData,uint32_t srcLen, void *destData, uint32_t *destLen)

  函数作用描述：

  执行非对称算法的加密操作。

  参数说明：

  operation：指向操作句柄；
  params：可选参数，一般为NULL；
  paramCount：可选参数，一般为0；

  srcData：指向需要进行加密操作的原始数据的
地址；

  srcLen：需要被加密的数据的长度；
  destData：保存执行加密操作后的数据的地
址；

  destLen：记录输出数据长度变量的地址。

  函数返回值：

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 606

TEEC_SUCCESS：加密操作成功；
TEE_ERROR_SHORT_BUFFER：用于保存输
出数据的buffer长度不够；

TEE_ERROR_BAD_PARAMETERS：输入参
数不合法。

6.TEE_AsymmetricDecrypt

函数原型：

TEE_Result TEE_AsymmetricDecrypt(TEE_OperationHandle operation, const TEE_Attribute *params, uint32_t paramCount, const void *srcData,uint32_t srcLen, void *destData,uint32_t *destLen)

函数作用描述：

执行非对称算法的解密操作。

参数说明：

operation：指向操作句柄；
params：可选参数，一般为NULL；

paramCount：可选参数，一般为0；
srcData：指向需要进行解密操作的密文数据的

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 607

地址；

  srcLen：需要被解密的数据的长度；

  destData：保存执行解密操作后的数据的地
址；

  destLen：记录输出数据长度变量的地址。

  函数返回值：

  TEEC_SUCCESS：解密操作成功；
  TEE_ERROR_SHORT_BUFFER：用于保存输
出数据的buffer长度不够；
  TEE_ERROR_BAD_PARAMETERS：输入参
数不合法。

7.TEE_AsymmetricSignDigest

  函数原型：

 TEE_Result TEE_AsymmetricSignDigest(TEE_OperationHandle operation, const TEE_Attribute *params,uint32_t paramCount, const void *digest, uint32_t digestLen, void *signature,uint32_t *signatureLen)

  函数作用描述：


 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 608

执行非对称算法的签名操作。

参数说明：

operation：指向操作句柄；
params：可选参数，一般为NULL；
paramCount：可选参数，一般为0；

digest：需要被签名的数据的摘要；
digestLen：摘要的长度；
signature：保存执行签名操作后获取的数据的
地址；

signatureLen：记录输出数据长度变量的地址。

函数返回值：

TEEC_SUCCESS：签名操作成功；

TEE_ERROR_SHORT_BUFFER：用于保存输
出数据的buffer长度不够。

8.TEE_AsymmetricVerifyDigest


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 609

函数原型：

TEE_ResultTEE_AsymmetricVerifyDigest(TEE_OperationHandle operation,
const TEE_Attribute *params,
uint32_t paramCount, const void *digest,
uint32_t digestLen, const void *signature,
uint32_t signatureLen)

函数作用描述：

执行非对称算法的验签操作。

参数说明：

operation：指向操作句柄；
params：可选参数，一般为NULL；
paramCount：可选参数，一般为0；

digest：需要被验签的数据的摘要；
digestLen：摘要的长度；
signature：签名信息；

signatureLen：签名信息的长度。



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 610

函数返回值：

TEEC_SUCCESS：验签操作成功；

TEE_ERROR_SIGNATURE_INVALID：验签
失败。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 611

19.5　小结

  本章介绍了在OP-TEE中RSA、AES、SHA基
本算法的使用、相关参数的说明以及相关接口的说
明，由于篇幅有限，而GP规范中定义的接口有很
多，所以读者可参阅GP规范中定义的算法接口编写
其他算法的实现，例如HMAC、PBKDF2、DES、
ECDSA，以及大整数计算等。使用各种算法的共同
点是首先分配操作句柄，使用object来建立密钥处
理句柄，将使用的密钥保存在object中，而object会
通过Populate的方式传递到操作句柄中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 612

第20章　OP-TEE的安全存储

20.1　安全存储简介

 OP-TEE的安全存储功能是OP-TEE为用户提供
的安全存储机制。用户可使用安全存储功能来保存
敏感数据、密钥等信息。使用OP-TEE安全存储功
能保存数据时，OP-TEE会对需要被保存的数据进
行加密，且每次更新安全文件时所用的加密密钥都
会使用随机数重新生成，用户只要调用GP标准中定
义的安全存储相关接口就能使用OP-TEE的安全存
储功能对私有数据进行保护。需要被保护的数据被
OP-TEE加密后会被保存到REE侧的文件系统、
EMMC的RPMB分区或数据库中，至于具体需要将
加密后的数据保存到哪里则由芯片提供商决定。也
可通过打开对应的宏开关，使能对应的保存方式来
满足用户的实际需求。安全存储功能可提供一个安
全的存储环境，安全文件中数据的加解密过程都在
OP-TEE中完成，且加解密密钥的生成也是在OP-
TEE中进行的，这样就能保证数据的安全性。
 不同的TA程序在使用安全存储功能时会生成
不同的加密密钥，且在更新安全文件的内容时会重
新使用随机数生成加密使用的初始化向量IV值。在


 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 613

REE则保存的安全文件不再像以前一样使用TA的
UUID作为存放路径，而是使用了类似文件映射表
的方式。在创建安全文件时会创建一个dirf.db文
件，该文件保存了安全存储功能管理的所有安全文
件的信息，且该文件中的所有数据也是被加密保存
的，加密该文件使用的密钥是在创建该文件时通过
随机数的方式生成。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 614

20.2　安全存储使用示例

  安全存储功能的实现主要是通过对
PersistentObject进行操作来完成，将需要被保存的
数据填充到PersistentObject的相应位置，并调用对
应的接口就能实现对安全文件的创建、打开、读
取、写入、重命名、删除等操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 615

20.2.1　示例代码获取和集成

                                    本书提供了根据GP标准定义的接口，使用OP-
TEE安全存储功能对数据进行保护的示例TA和CA
代码，读者可使用如下指令从GitHub中获取代码：

git clone https://GitHub.com/shuaifengyun/secStor_test.git

  下载完代码后就需要将该TA和CA集成到OP-
TEE中，需修改OP-TEE源代码build目录下的
qemu.mk（开发者板级对应的mk文件）和
common.mk文件。然后编译整体OP-TEE后就能够
使用该示例代码来使用安全存储功能保存数据。

           获取到示例代码之后，切换到如下build目录
下，然后使用git apply命令合入补丁文件后就可完
成将该示例集成到OP-TEE，合入补丁的操作步骤
如下：

  1）将示例代码中的
secStorTest_common_3.0.0.patch文件和
secStorTest_qemu_3.0.0.patch文件复制到build目录
中。



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 616

   2）切换到build目录，使用如下命令合入补
丁：

  git apply secStorTest_common_3.0.0.patch
  git apply secStorTest_qemu_3.0.0.patch

   将补丁合入完成之后就可使用make-f qemu.mk
all编译整个工程，然后使用make-f qemu.mk run-
only来启动OP-TEE，在启动的正常世界状态的终端
执行secStorTest命令就能实现该示例的CA对TA的
调用。示例代码的运行效果如图20-1所示。










    图20-1 secStorTest示例运行



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 617

20.2.2　板级编译文件的修改

                               将该示例的TA和CA添加到OP-TEE中需要修改
读者开发环境对应的mk文件。以使用QEMU方式运
行OP-TEE为例，则需要修改qemu.mk文件添加该示
例代码的编译目标，修改步骤如下：

1）添加secStorTest的编译目标：

############################################################################
# secure storage test
############################################################################
secStorTest: secStorTest-common
secStorTest-clean: secStorTest-clean-common

2）将secStorTest和secStorTest-clean添加到全
局的all和clean目标依赖关系中：

all: bios-qemu qemu soc-term optee-examples secStorTest
clean: bios-qemu-clean busybox-clean linux-clean optee-os-clean \
optee-client-clean qemu-clean soc-term-clean check-clean \
optee-examples-clean secStorTest-clean

                             添加部分的主要作用是定义secStorTest目标并
建立该编译目标与all的依赖关系，在编译整个OP-
TEE工程时会被使用到。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 618

20.2.3　通用编译文件的修改

修改完板级编译的mk文件后，
                     还需修改
build/common.mk文件。修改的内容主要是将
secStorTest的编译目标集成到系统编译中，
    需要修
改的内容如下：

1）定义secStorTest路径变量。


SEC_STORAGE_TEST_PATH ?= $(ROOT)/secStor_test



2）添加secStorTest的目标依赖，修改filelist-
tee-common目标的依赖关系如下：


filelist-tee-common: optee-client xtest optee-examples secStorTest



3）增加TA和CA的common目标：


############################################################################
# secure storage test
###########################################################################
SEC_STORAGE_COMMON_FLAGS ?=    HOST_CROSS_COMPILE=$(CROSS_COMPILE_NS_USER)\
TA_CROSS_COMPILE=$(CROSS_COMPILE_S_USER) \
TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR) \
TEEC_EXPORT=$(OPTEE_CLIENT_EXPORT)
.PHONY: secStorTest-common
secStorTest-common: optee-os optee-client




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 619

$(MAKE) -C $(SEC_STORAGE_TEST_PATH) $(SEC_STORAGE_COMMON_FLAGS)
SEC_STORAGE_CLEAN_COMMON_FLAGS?= TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR)
.PHONY: secStorTest-clean-common
secStorTest-clean-common:
$(MAKE) -C $(SEC_STORAGE_TEST_PATH) $(SEC_STORAGE_CLEAN_COMMON_FLAGS) clean



4）添加clean操作的依赖关系。


optee-os-clean-common: xtest-clean optee-examples-clean secStorTest-clean



5）在filelist-tee-common中添加TA和CA镜像需
要被打包到文件系统中的操作：



@echo "# Secure storage test " >> $(fl)
@if [ -e $( SEC_STORAGE_TEST_PATH)/host/secStorTest ]; then \
  echo "file /bin/secStorTest" \
  "$(SEC_STORAGE_TEST_PATH)/host/secStorTest 755 0 0"     >> $(fl); \
  echo "file /lib/optee_armtz/59e4d3d3-0199-4f74-b94d-53d3daa57d73.ta" \
  "$(SEC_STORAGE_TEST_PATH)/ta/59e4d3d3-0199-4f74-b94d-53d3daa57d73.ta
  444 0 0” >> $(fl); \
fi










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 620

20.2.4　编译运行

   修改完编译相关文件后，在build目录下执行
make指令编译整个OP-TEE工程。编译完成后，启
动系统就可以在REE侧终端使用secStorTest命令来
测试安全存储功能。测试命令执行完成后，在REE
侧文件系统的/data/tee目录下将会出现dirf.db文件和
该TA对应的安全存储文件，该安全存储文件名是
以数字的方式保存在/data/tee目录中的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 621

20.3　安全存储功能使用的密钥

  OP-TEE中使用安全存储功能保存的数据都是
使用AES算法进行加密的，加密后的文件被保存在
文件系统或RPMB分区。使用AES算法进行数据加
密或解密时需提供密钥和初始化向量IV值。每个
TA在使用安全存储功能保存数据时都会生成一个
随机数作为IV值，使用FEK的值作为AES的密钥。
FEK的值是OP-TEE对相关数据执行HMAC操作后
生成的。FEK值的生成涉及SSK和TSK，本章节将
介绍这些密钥的使用和生成过程。相关密钥的关系
和生成方式如图20-2所示。










   图20-2　安全存储功能中各密钥的关系

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 622

20.3.1　安全存储密钥

 安全存储密钥（Secure Storage Key，SSK）在
每台设备中的值都不同。OP-TEE启动时会使用芯
片ID和HUK经HMAC算法计算来获得该值，并将
SSK的值保存在结构体变量tee_fs_ssk的密钥成员
中，以备生成其他密钥使用。工厂生产时会将HUK
写入到OTP/efuse中，且正常世界状态无法读取到
HUK的值，而芯片ID在芯片出厂后就会被写入到芯
片中。

 OP-TEE启动过程中会执行
tee_fs_init_key_manager函数，该函数使用
SSK=HMAC(HUK，message)的方式来生成SSK。
该函数的内容如下：

static TEE_Result tee_fs_init_key_manager(void)
{
 int res = TEE_SUCCESS;
 struct tee_hw_unique_key huk;
 uint8_t chip_id[TEE_FS_KM_CHIP_ID_LENGTH];
 uint8_t message[sizeof(chip_id) + sizeof(string_for_ssk_gen)];
 /* SSK的产生:
 *   SSK = HMAC(HUK, message)
 *   message := concatenate(chip_id, static string)
 * */
 /* 获取HUK的值（该接口的实现与平台有关,不同的芯片具有不同读取HUK值的方式） */
 tee_otp_get_hw_unique_key(&huk);


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 623

 /* 获取芯片ID的值（不同的芯片具有不同的读取芯片ID值的方式）*/
 tee_otp_get_die_id(chip_id, sizeof(chip_id));

 /* 将chip id + string_for_ssk_gen连接后的值保存到message中,string_for_ssk_gen是一个静态的字符串,该值被写死在代码中 */
 memcpy(message, chip_id, sizeof(chip_id));
 memcpy(message + sizeof(chip_id), string_for_ssk_gen,
    sizeof(string_for_ssk_gen));

 /* 使用huk的值对message的内容做HMAC运算,将获取到的数据作为SSK保存到tee_fs_ssk 变量的key成员中 */
 res = do_hmac(tee_fs_ssk.key, sizeof(tee_fs_ssk.key),
    huk.data, sizeof(huk.data),
    message, sizeof(message));
 /* 标记ssk已经生产 */
 if (res == TEE_SUCCESS)
    tee_fs_ssk.is_init = 1;
 return res;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 624

20.3.2　可信应用的存储密钥

   可信应用的存储密钥（Trusted Applicant
Storage Key，TSK）是生成FEK时使用到的密钥。
TSK是使用SSK作为密钥对TA的UUID经HMAC计
算获得，类似于HMAC(SSK，UUID)的方式生成
TSK。在调用tee_fs_fek_crypt函数时会计算TSK的
值。TSK最终会被用来生成FEK，FEK会在使用安
全存储功能保存数据时被用来加密数据。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 625

    20.3.3　文件加密密钥

文件加密密钥（File Encryption Key，FEK）是
    安全存储功能用于对数据进行加密时使用的AES密
    钥，该密钥在生成文件时会使用PRNG算法随机产
    生，产生的FEK会使用TSK进行加密，然后保存到
    head.enc_fek变量中。TA在每次使用安全存储功能
    创建一个安全文件时就会生成一个随机数作为
    FEK，即每个TA中的每个安全文件都有一个FEK用
    于加密对应文件中的数据。关于FEK的产生可简单
    理解为如下公式，使用的初始化向量IV值为0：

     AES_CBC（in_key，TSK）
     OP-TEE通过调用tee_fs_fek_crypt函数来生成一
    个FEK，该函数代码如下：

    TEE_Result tee_fs_fek_crypt(const TEE_UUID *uuid, TEE_OperationMode mode,
     const uint8_t *in_key, size_t size,
     uint8_t *out_key)
    {
     TEE_Result res;
     uint8_t *ctx = NULL;
     size_t ctx_size;
     uint8_t tsk[TEE_FS_KM_TSK_SIZE];
     uint8_t dst_key[size];
     /* 检查输入的用于生成FEK的随机数in_key和用于存放生成的out_key地址是否合法 */
     if (!in_key || !out_key)
     return TEE_ERROR_BAD_PARAMETERS;

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 626

/* 检查in_key长度 */
if (size != TEE_FS_KM_FEK_SIZE)
     return TEE_ERROR_BAD_PARAMETERS;
/* 判定SSK是否已经被初始化 */
if (tee_fs_ssk.is_init == 0)
     return TEE_ERROR_GENERIC;
/* 如果调用时参数uuid不为0,则调用HMAC算法生成TSK。如果UUID的值为0,则默认生成TSK使用的原始数据为0 */
if (uuid) {
     res = do_hmac(tsk, sizeof(tsk), tee_fs_ssk.key,
         TEE_FS_KM_SSK_SIZE, uuid, sizeof(*uuid));
     if (res != TEE_SUCCESS)
     return res;
} else {
     uint8_t dummy[1] = { 0 };
     res = do_hmac(tsk, sizeof(tsk), tee_fs_ssk.key,
         TEE_FS_KM_SSK_SIZE, dummy, sizeof(dummy));
     if (res != TEE_SUCCESS)
     return res;
}
/* 获取调用AEC_CBC操作需要的context的大小 */
res = crypto_ops.cipher.get_ctx_size(TEE_FS_KM_ENC_FEK_ALG, &ctx_size);
if (res != TEE_SUCCESS)
     return res;

/* 分配一份进行AES_CBC操作时需要的context空间 */
ctx = malloc(ctx_size);
if (!ctx)
     return TEE_ERROR_OUT_OF_MEMORY;
/* 使用TSK作为进行AES_CBC计算使用的key,而IV值默认为0 */
res = crypto_ops.cipher.init(ctx, TEE_FS_KM_ENC_FEK_ALG, mode, tsk,
         sizeof(tsk), NULL, 0, NULL, 0);
if (res != TEE_SUCCESS)
     goto exit;
/* 将输入的in_key填充到context中,做完AES_CBC操作之后,输出的数据将会被保存到dst_key中 */
res = crypto_ops.cipher.update(ctx, TEE_FS_KM_ENC_FEK_ALG,
     mode, true, in_key, size, dst_key);
if (res != TEE_SUCCESS)
     goto exit;
/* 执行AES_CBC的加密运算,生成FEK */
crypto_ops.cipher.final(ctx, TEE_FS_KM_ENC_FEK_ALG);
/* 将生成的FEK的值复制到输出参数中 */
memcpy(out_key, dst_key, sizeof(dst_key));

exit:
free(ctx);




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 627

return res;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 628

20.4　安全文件、dirf.db文件的数据格式和
操作过程

 OP-TEE的安全存储功能可满足用户保存敏感
数据的需求，需要被保存的数据会被加密保存到文
件系统或RPMB分区中。当选择将数据保存到文件
系统中时，默认情况下，加密后的数据会被保存
在/data/tee目录中。安全存储功能使用二叉树的方
式来保存加密后的文件。

          当第一次使用安全存储功能创建用于保存敏感
数据的安全文件时，OP-TEE将会在/data/tee目录中
生成两个文件：dirf.db文件和以数字命名的文件。
dirf.db文件保存的是整个安全存储功能管理的所有
文件的目录信息和节点信息。当用户使用某个已经
存在的安全文件时，OP-TEE首先会读取dirf.db文件
中的相关内容，然后根据需要操作的安全文件名字
的哈希值在dirf.db文件中找到对应的文件编号，最
终按照这个编号实现对文件的打开、关闭、写入、
读出、重命名、裁剪等操作。

 保存在/data/tee目录以数字命名的文件是被安
全存储保护的用户文件。该文件保存的是加密之后
的用户数据，加密使用的密钥则是对应的FEK。


 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 629

20.4.1 dirf.db文件和安全文件的格式

  使用安全存储功能生成的文件都会使用相同的
格式被保存，而且dirf.db文件与安全文件的格式也
相同。安全文件中的内容分为三个区域，分别用于
保存文件头、结点、数据，文件的内容，其格式如
图20-3所示。










    图20-3 dirf.db文件的格式

    安全文件将整个空间划分成相等大小的物理


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 630

块，每个物理块的大小为4KB，其中文件头部分存
放的是tee_fs_htree_image结构体的内容，该结构体
定义如下：


    struct tee_fs_htree_image {
      //加密iv+enc_fek时使用的iv值,每次保存head时会使用随机数更新
      uint8_t iv[TEE_FS_HTREE_IV_SIZE];
      uint8_t tag[TEE_FS_HTREE_TAG_SIZE];      //加密iv+Enc_fek生成的数据的tag部分
      uint8_t enc_fek[TEE_FS_HTREE_FEK_SIZE];  //使用TSK加密一个安全文件的fek生成的
      //加密iv+Enc_fek生成的数据的imeta部分
      uint8_t imeta[sizeof(struct tee_fs_htree_imeta)];
      uint32_t counter; //用于计算在保存tee_fs_htree_image时是存到ver0还是ver1
    };


    节点部分存放的是tee_fs_htree_node_image结
构体的内容，在保存数据到每个物理块之前都会使
用FEK和对应的IV值对需要被保存的数据进行加
密，而在打开读取文件时则会首先从文件头中读取
enc_fek的值，然后使用TSK做解密操作来获取
FEK，最后从需要被解密的物理块对应的节点中获
取到IV值。tee_fs_htree_node_image的结构体的定
义如下：


    struct tee_fs_htree_node_image {
      //保存节点的哈希值,用于在操作文件时找到该文件的head
      uint8_t hash[TEE_FS_HTREE_HASH_SIZE];
      //加密安全文件数据区域中某一个块时使用的iv值,块数据的每次写入都会使用随机数更新
      uint8_t iv[TEE_FS_HTREE_IV_SIZE];
      uint8_t tag[TEE_FS_HTREE_TAG_SIZE]; //加密安全数据区域中一个块数据时生成的tag
      uint16_t flags;        //用于计算使用块中的那个ver
    };




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 631

    数据块中保存的是密文数据，该密文数据是使
用该文件对应的FEK和块对应的IV值对需要被保存
的数据进行加密操作来生成。

    dirf.db文件的数据块区域保存的是所有使用安
全存储功能保存的文件的相关信息，在安全存储功
能中使用dirfile_entry结构体来表示每个安全文件的
基本信息，该结构体定义如下：


    struct dirfile_entry {
      TEE_UUID uuid; //创建该安全文件的TA的UUID
      uint8_t oid[TEE_OBJECT_ID_MAX_LEN]; //安全文件的名字（使用安全存储操作时的名字）
      uint32_t oidlen;//文件名字的长度
//data/tee目录下安全文件的root node的哈希值
      uint8_t hash[TEE_FS_HTREE_HASH_SIZE];
      uint32_t file_number; //保存在/data/tee目录下的文件编号
    };










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 632

20.4.2　安全存储功能中使用的重要结构体

  在整个安全存储功能的操作过程中，存在一些
很重要的结构体，这些结构体用于记录或保存所有
安全文件和dirf.db文件的操作信息，这些结构体的
关系框图如图20-4所示。










 图20-4　安全存储功能实现时各结构体的关系

  相关重要结构体作用说明如下：

  ·tee_fs_htree_node_image：用于保存文件的节
点信息，通过节点可找到对应文件的头部或数据块

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 633

信息；

 ·tee_fs_htree_image：用于保存安全文件的头部
数据，从头部数据中可获取安全文件的加密密钥和
加密头部时使用的IV值；

 ·tee_fs_fd：安全存储操作时使用的重要结构
体，存放对文件操作时使用的fd、dir、TA的UUID
等信息。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 634

20.4.3　安全存储中的文件节点组成

  在安全存储中，dirf.db文件和安全文件都是使
用二叉树的方式来保存文件编号或数据块。dirf.db
文件的数据块区域保存的是dirfile_entry结构体变量
（密文保存），dirf.db文件中的节点区域保存的是
与保存的数据块相对应的节点信息。通过查找
dirf.db文件中的tee_fs_htree_node_image就能找到对
应的dirfile_entry数据块的数据。在安全文件中同样
也存在这样的对应关系，只不过数据块中保存的不
再是dirfile_entry，而是实际需要被保存的数据。二
叉树的保存方式如图20-5所示，第一个节点作为
dirf.db文件或安全文件的根节点使用。










    图20-5　安全存储功能中的二叉树节点


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 635

20.4.4　查询安全文件中的特定数据块

  使用安全存储对已经保存的安全文件执行读写
等操作时，都会先打开dirf.db文件，读取dirf.db文
件中的数据区域。获取到安全存储中保存的所有文
件的dirfile_entry信息，然后对比dirfile_entry中uuid
和obj_id与需要被操作的安全文件的uuid和obj_id是
否匹配，如果匹配则获取对应的文件编号。该文件
编号就是保存在/data/tee目录下需要被操作的安全
文件。

                    查询到安全文件的文件编号后，通过计算需要
读取的数据在安全文件中的位置来确定块编号，然
后通过该块对应的节点ID获得该块的IV值，使用保
存在安全文件头中的FEK和获得的块的IV值对块内
容进行加/解密操作。最后将处理后的数据写入块中
或返回给用户。整个过程的大致流程如图20-6所
示。

  整个操作过程中，节点ID与块编号的对应关系
是：节点ID=块编号+1，而选取的是块中的哪个ver
则与节点ID的ver值相同。





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 636

图20-6　安全存储查找操作文件的流程










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 637

20.5　安全存储文件的创建

   使用安全存储时首先需要创建并初始化该安全
文件。如果在创建安全文件之前，/data/tee目录下
没有dirf.db文件，则会先创建dirf.db文件并进行初
始化。创建的dirf.db文件和安全文件具有相同的格
式。所有对/data/tee目录下的文件进行的操作都是
通过TEE侧发送RPC请求通知tee_supplicant来完成
的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 638

20.5.1　安全存储软件框架

  在OP-TEE中调用GP标准接口使用安全存储功
能时，对文件的读写操作最终是由REE侧来完成
的。OP-TEE无法直接操作REE侧的文件系统，故
需通过发送RPC请求的方式通知tee_supplicant来完
成对文件系统的操作，整个安全存储功能的软件框
图如图20-7所示。

  在TA中调用GP的接口最终会通过系统调用的
方式陷入OP-TEE的内核空间，根据实际操作需求
组装RPC请求需要的参数，并触发安全监控模式调
用（smc）将RPC请求发送给tee_supplicant。
tee_supplicant会解析出RPC请求的参数，并根据参
数的定义对/data/tee目录下的文件进行具体操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 639

图20-7　安全存储与tee_supplicant的关系










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 640

20.5.2 dirf.db文件的创建

   使用安全存储功能时，如果/data/tee目录下没
有dirf.db文件，首先会创建dirf.db文件。OP-TEE在
执行get_dirh函数时，get_dirh函数会判定在/data/tee
目录下是否有dirf.db文件，如果没有则会先创建
dirf.db文件。该文件的创建过程如图20-8所示。










      图20-8 get_dirh函数的实现流程
   get_dirh函数在执行安全文件的打开、创建、
写入操作时都会被调用。该函数的内容只会被执行


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 641

一次，以后再调用该函数将不再执行任何实际操
作，这是因为在dirf.db文件打开后会设定相应的标
志，在get_dirh函数中会对该标志进行判定以便确
定是否需要执行打开dirf.db文件的操作。
  在创建dirf.db文件过程中会产生一个随机数作
为FEK，且在调用update_root函数时会产生另外一
个随机数作为加密FEK的IV值并保存到head.iv中。
每次文件的更新时，该IV值都会被新的随机数替
代。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 642

20.5.3　安全文件的创建

在TA中调用TEE_CreatePersistentObject接口时
会创建安全文件。在创建安全文件时会初始化安全
文件的数据区域（初始化数据已加密）。整个安全
文件的创建过程如图20-9所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 643

  图20-9 TEE_CreatePersistentObject函数流程

   安全文件创建完成之后，会将初始化数据加密
后写入到安全文件中，然后更新整个安全文件的
tee_fs_htree_node_image区域以及保存在文件头的
tee_fs_htree_image区域，到此安全文件创建就已完
毕。为后续能够通过dirf.db文件找到该安全文件，
则还需要更新dirf.db文件的内容，主要是更新
dirf.db文件数据区域中的dirfile_entry数据。


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 644

20.6　安全文件的打开操作

  获取安全文件的操作句柄是对文件中的内容进
行读写操作的基础，本节将详细介绍安全文件的打
开过程。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 645

20.6.1　安全文件的打开

   使用安全存储功能时，在TA中调用
TEE_OpenPersistentObject函数来打开某个特定的安
全文件。该函数将会调用utee_storage_obj_open函数
进入OP-TEE的内核空间执行打开操作。打开安全
文件的操作过程如图20-10所示。










    图20-10 TEE_OpenPersistentObject函数流程


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 646

20.6.2　打开dirf.db文件并建立节点树

   打开某个特定的安全文件之前，首先需要从
dirf.db文件中找到该安全文件对应的文件编号。打
开dirf.db文件是通过调用get_dirh函数来实现的，打
开dirf.db文件的执行流程如图20-11所示。










      图20-11 get_dirh函数流程
      dirf.db文件的创建及安全文件节点树的建立是
    通过调用get_dirh函数来实现的，该函数的内容如
    下：

    static TEE_Result get_dirh(struct tee_fs_dirfile_dirh **dirh)
    {


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 647

     if (!ree_fs_dirh_refcount) {
      TEE_Result res;

      assert(!ree_fs_dirh);
      /* 执行打开dirf.db文件 */
      res = tee_fs_dirfile_open(&ree_dirf_ops, &ree_fs_dirh);
      if (res)
      return res;
     }
     assert(ree_fs_dirh);
     ree_fs_dirh_refcount++;//标记difr.db文件已经被打开
     *dirh = ree_fs_dirh; //将打开的dirf.db文件的相关信息返回
     return TEE_SUCCESS;
    }



      tee_fs_dirfile_open函数会调用
ree_fs_open_primitive来打开dirf.db文件。该函数会
调用tee_fs_rpc_open_dfh函数通知tee_supplicant打
开/data/tee/dirf.db文件并返回该文件的fd值，
        然后
tee_fs_rpc_open_dfh函数会调用tee_fs_htree_open函
数读取dirf.db文件中最新的文件头部数据，
        通过解
密获得dirf.db文件加解密使用的FEK，并建立dirf.db
文件的节点树。tee_fs_htree_open函数内容如下：


    TEE_Result tee_fs_htree_open(bool create, uint8_t *hash, const TEE_UUID *uuid,
             const struct tee_fs_htree_storage *stor,
             void *stor_aux, struct tee_fs_htree **ht_ret)
    {
     TEE_Result res;
     struct tee_fs_htree *ht = calloc(1, sizeof(*ht));
     if (!ht)
      return TEE_ERROR_OUT_OF_MEMORY;
     /* 填充tee_fs_htree结构体变量 */
     ht->uuid = uuid;
     ht->stor = stor;
     ht->stor_aux = stor_aux;




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 648

     /* 判定是执行打开还是创建文件操作 */
     if (create) {
         const struct tee_fs_htree_image dummy_head = { .counter = 0 };
         res = crypto_ops.prng.read(ht->fek, sizeof(ht->fek));
         if (res != TEE_SUCCESS)
         goto out;
         res = tee_fs_fek_crypt(ht->uuid, TEE_MODE_ENCRYPT, ht->fek,
             sizeof(ht->fek), ht->head.enc_fek);
         if (res != TEE_SUCCESS)
         goto out;
         res = init_root_node(ht);
         if (res != TEE_SUCCESS)
goto out;
         ht->dirty = true;
         res = tee_fs_htree_sync_to_storage(&ht, hash);
         if (res != TEE_SUCCESS)
         goto out;
         res = rpc_write_head(ht, 0, &dummy_head);
     } else {
         /* 当在打开dirf.db文件时调用函数,init_head_form_data函数将会读取dirf.db文件最开始的tee_fs_htree_image结构体,并选用其中一个最新的head,记录下该head的idx值（0/1）并调用rpc_read_node获取dirf.db文件中的root node */
         res = init_head_from_data(ht, hash);
         if (res != TEE_SUCCESS)
         goto out;
         /* 解密出root node的内容并校验*/
         res = verify_root(ht);
         if (res != TEE_SUCCESS)
         goto out;

         /* 读取dirf.db文件中的所有node信息建立dirf.db文件的节点树 */
         res = init_tree_from_data(ht);
         if (res != TEE_SUCCESS)
         goto out;
         // 通过计算各节点内容的哈希值,并与保存的hash进行比较来校验整个节点的树是否合法
         res = verify_tree(ht);
     }
    out:
     if (res == TEE_SUCCESS)
         *ht_ret = ht;
     else
         tee_fs_htree_close(&ht);
     return res;
    }








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
         更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 649

20.6.3　安全文件在/data/tee目录下的文件编号

   打开dirf.db文件并建立了文件节点树后，通过
读取dirf.db文件的数据区域中安全文件对应的
dirfile_entry来找到该安全文件的存储编号。整个过
程是通过调用tee_fs_dirfile_find函数来实现的，查
找的过程如图20-12所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 650

     图20-12 tee_fs_dirfile_find函数流程
   dirf.db文件的数据区域保存的是加密之后的
dirf_entry数据。该数据使用dirf.db文件的FEK和该
份数据块对应的节点ID中的IV进行加密，在读取过
程中也需要使用对应的数据和操作才能获取到明文
的dirf_entry数据。通过检查读取到的dirf_entry数据
中的uuid、obj_id与需要打开的安全文件是否一致

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
        更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 651

来判定dirf_entry是否正确。如果匹配，则正确的那
个dirf_entry数据中的file_number成员就是安全文件
在/data/tee目录下的文件编号。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 652

20.6.4　打开特定安全文件

  得到安全文件编号后就可打开该文件，读取该
安全文件的头部分，获取根节点信息，并建立该安
全文件的节点树，然后就可开始对该安全文件进行
读写操作。打开安全文件也是通过调用
ree_fs_open_primitive函数来实现的。注意安全文件
中的节点ID与数据区域中的块编号的对应关系。解
密数据区域中的某个块中的密文数据需要使用到对
应的节点ID中的IV值，对应的FEK，该FEK被加密
保存在安全文件的头部，在打开安全文件时会被保
存到ht->fek变量中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 653

20.7　安全文件的读写操作

   TA对安全文件进行读写操作是通过调用
TEE_ReadObjectData和TEE_WriteObjectData函数来
实现的。这两个函数的执行最终会进入OP-TEE的
内核空间中。在OP-TEE内核空间调用对应的读写
接口syscall_storage_obj_read和
syscall_storage_obj_write函数来完成对安全文件中
数据的读写操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 654

20.7.1　安全文件中数据的读取

      在TA中调用读取接口后，OP-TEE内核空间将
会调用syscall_storage_obj_read函数对安全文件中的
数据进行读取操作。该函数的执行过程中与打开操
作一样，
        首先会获取TA的会话ID和运行上下文并
检查权限。然后调用ree_fs_read函数来实现读取数
据的操作。该函数内容如下：



    static TEE_Result ree_fs_read(struct tee_file_handle *fh, size_t pos,
         void *buf, size_t *len)
    {
     TEE_Result res;
     /* 传入的post是要读取的数据在安全文件中数据区域中的起始位置,可以通过object的seek函数改变buf为读取到的数据存放的地址 */
     mutex_lock(&ree_fs_mutex);        //互斥的lock操作
     res = ree_fs_read_primitive(fh, pos, buf, len); //进入读取操作函数
     mutex_unlock(&ree_fs_mutex);        //互斥的unlock操作
     return res;
    }

    static TEE_Result ree_fs_read_primitive(struct tee_file_handle *fh, size_t pos,
         void *buf, size_t *len)
    {
     TEE_Result res;
     int start_block_num;
     int end_block_num;
     size_t remain_bytes;
     uint8_t *data_ptr = buf;
     uint8_t *block = NULL;
     struct tee_fs_fd *fdp = (struct tee_fs_fd *)fh;
     struct tee_fs_htree_meta *meta = tee_fs_htree_get_meta(fdp->ht);
     /* 判定需要读取的长度是否被满足 */
     remain_bytes = *len;
     if ((pos + remain_bytes) < remain_bytes || pos > meta->length)
     remain_bytes = 0;




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 655

 else if (pos + remain_bytes > meta->length)
     remain_bytes = meta->length - pos;
 *len = remain_bytes;
 if (!remain_bytes) {
     res = TEE_SUCCESS;
     goto exit;
 }
 /* 计算出读取位置数据安全文件数据区域中的block,并根据需要读取的数据长度计算出需要读取的数据尾部在哪个block */
 start_block_num = pos_to_block_num(pos);
 end_block_num = pos_to_block_num(pos + remain_bytes - 1);
 /* 分配buffer保存读取的block数据 */
 block = malloc(BLOCK_SIZE);
 if (!block) {
     res = TEE_ERROR_OUT_OF_MEMORY;
     goto exit;
 }
 /* 使用while循环开始读取数据,当查出en_block_num时表示读取操作完成 */
 while (start_block_num <= end_block_num) {
     /* 计算出需要读取的文件在该block中的offset */
     size_t offset = pos % BLOCK_SIZE;
     /* 计算需要读取的长度 */
     size_t size_to_read = MIN(remain_bytes, (size_t)BLOCK_SIZE);
     if (size_to_read + offset > BLOCK_SIZE)
         size_to_read = BLOCK_SIZE - offset;
     /* 读取block number编号为start_block_number的数据块的数据,在tee_fs_htree_read_block函数中将会根据start_block_number找到该block对应的node,获取到该block加解密使用的IV,然后使用IV和该文件FEK解密从安全文件中读取的数据获得明文的数据 */
     res = tee_fs_htree_read_block(&fdp->ht, start_block_num, block);
     if (res != TEE_SUCCESS)
     goto exit;
     /* 按照offset和size_to_read复制读出的明文数据到buffer中 */
     memcpy(data_ptr, block + offset, size_to_read);
     /* 计算偏移 */
     data_ptr += size_to_read;
     remain_bytes -= size_to_read;
     pos += size_to_read;
     start_block_num++;
 }
 res = TEE_SUCCESS;
exit:
 free(block);
 return res;
}









https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 656

20.7.2　安全文件中数据的写入

      TA调用写入接口后在OP-TEE内核空间将会调
用syscall_storage_obj_write函数来实现对安全文件
中的数据进行写入操作。该函数的执行过程与打开
安全文件的操作一样，
        首先会获取TA的会话ID和
运行上下文并检查权限。然后调用ree_fs_write函数
来实现读取数据操作。该函数内容如下：



    static TEE_Result ree_fs_write(struct tee_file_handle *fh, size_t pos,
         const void *buf, size_t len)
    {
     TEE_Result res;
     struct tee_fs_dirfile_dirh *dirh = NULL;
     struct tee_fs_fd *fdp = (struct tee_fs_fd *)fh;
     mutex_lock(&ree_fs_mutex);
     /* dirf.db文件操作,由于已经在open中执行过,故不会重复打开dirf.db文件 */
     res = get_dirh(&dirh);
     if (res)
        goto out;
     /* 将数据写入安全文件中,写入之前会对数据进行加密操作,执行时首先会将牵扯到的block中的数据全部读出,然后将需要被写入的数据替换掉对应的区域,然后再调用tee_fs_htree_write_block函数将数据进行加密操作后写入安全文件中 */
     res = ree_fs_write_primitive(fh, pos, buf, len);
     if (res)
        goto out;
     /* 更新整个安全文件的node tree信息和head部分的数据 */
     res = tee_fs_htree_sync_to_storage(&fdp->ht, fdp->dfh.hash);
     if (res)
        goto out;
     /* 更新dirf.db文件中该安全文件对应的dirfile_entry结构体数据 */
     res = tee_fs_dirfile_update_hash(dirh, &fdp->dfh);
     if (res)
        goto out;
     /* 更新相关哈希值 */
     res = tee_fs_dirfile_commit_writes(dirh);
    out:




    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 657

 put_dirh(dirh);
 mutex_unlock(&ree_fs_mutex);
 return res;
}










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 658

20.8　安全文件中数据的加解密

  安全存储中的安全文件和dirf.db文件中的数据
内容都是按照一定的格式保存的，主要由三部分组
成：tee_fs_htree_image、tee_fs_htree_node_image和
数据区域块。tee_fs_htree_image和
tee_fs_htree_node_image结构体中保存的是安全文件
操作时使用到的重要数据的密文数据，
tee_fs_htree_image区域中的数据是对元数据经加密
重要数据后生成的。而数据区域块和
tee_fs_htree_node_image中的数据则是对数据块数据
经加密后获得的。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 659

20.8.1　各种类型数据的组成及作用

   tee_fs_htree_image主要保存加密头部的IV值、
加密安全文件的FEK使用的enc_fek以及加密之后生
成的tag、imeta及标记两个tee_fs_htree_image哪个为
最新的counter值。

   tee_fs_htree_node_image保存节点的哈希值、
加密数据块区域使用的IV值、标记使用哪个data
block的ver的flag值以及加密需要被保存的数据时生
成的tag数据。
   数据块区域保存的是需要被保存的数据的密文
数据。

   tee_fs_htree_image中的imeta是按照元数据的方
式经加密对应的数据获得，
tee_fs_htree_node_imaget中的tag跟数据块中的数据
则是按照数据块加密策略经加密后获得。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 660

20.8.2　元数据的加密

  tee_fs_htree_image区域中的数据是按照元数据
方式经加密生成的，该加密过程如图20-13所示。










      图20-13　元数据的加密过程

  上述加密操作过程中相关元素说明如下：

  FEK：安全文件和dirf.db文件在执行加密操作
时使用的密钥，该值在文件创建时使用随机数的方
式生成。对已经创建好的文件进行操作时，该值会

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 661

从tee_fs_htree_image的enc_fek成员中使用TSK解密
获得；

   TSK：使用SSK和UUID执行HMAC计算得到；

   AES_ECB：将FEK使用TSK经AES的ECB模式
加密操作后生成enc_fek；
   Encrypted FEK：使用TSK加密FEK得到，保存
在tee_fs_htree_image的enc_fek中，最终会被写入安
全文件或者dirf.db文件头的头部中；
   Meta IV：使用安全存储创建文件或将
tee_fs_htree_image写入文件中都会被随机生成，最
终会被写入安全文件或dirf.db文件头的头部中；

   Meta Data：/data/tee目录下每个文件中存放的
tee_fs_htree_node_image的个数相关的数据；
   AES_GCM：将enc_fek+meta iv+meta data使用
FEK和meta IV进行AES的GCM模式加密操作生成
tag和Encryption Meta Data数据；
   Tag：加密enc_fek+meta iv+meta data时生成的
tag值，数据会被保存在tee_fs_htree_image中的tag成
员中；


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 662

    Encryptoed Meta Data：加密enc_fek+meta
iv+meta data时生成的imeta值，数据会被保存在
tee_fs_htree_image中的imeta成员中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 663

    20.8.3　数据块区域的加密策略

    数据块区域和tee_fs_htree_node_image中的数
    据是按照数据块区域的加密策略经加密明文数据生
    成的，数据块区域加密策略的加密过程如图20-14
    所示。










  图20-14　数据块区域中数据的加密过程

  上述加密操作过程中相关元素说明如下：

  Encrypted FEK：使用TSK加密FEK得到，保存

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 664

在tee_fs_htree_image的enc_fek中，最终会被写入安
全文件或者dirf.db文件头的头部中；
   TSK：使用SSK和UUID执行HMAC计算得到；

   AES_ECB：将Encrypted FEK使用TSK进行
ECB模式的AES解密操作生成FEK；
   FEK：解密Encrypted FEK之后生成的FEK，用
于加密需要被保存的数据块；

   Block IV：每次加密数据区域中每个数据块是
都会随机生成，然后被保存到
tee_fs_htree_node_image变量的IV成员中；

   Block Data：将需要被保存的数据更新到对应
的数据块区域，然后重新加密后生成新的数据块的
密文数据；

   AES_GCM：将Block IV+Block data使用FEK和
块IV进行GCM模式的AES加密操作生成tag和
Encryption Block Data数据；
   Tag：加密Block IV+Block data时生成的tag
值，数据会被保存在tee_fs_htree_node_image中的
tag成员中；


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 665

    Encryption Block Data：加密Block IV+Block
data时生成的Encryption Block Data值，数据会被保
存在文件中数据区域对应的block中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 666

20.9　小结

  安全存储功能是OP-TEE中的一个重要功能，
为用户提供一个安全存取数据的方式。由于每次在
对安全文件进行写入操作时都会使用随机数重新生
成加密时使用的IV值，且加密时使用的密钥也在创
建安全文件时使用随机数生成，并被加密保存到安
全文件的头部中，所以很难非法获取到安全存储中
保存的明文数据。本章节介绍了OP-TEE中安全存
储功能的实现原理、软件代码执行流程以及其加密
密钥的生成和文件内容的加密过程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 667

第21章　可信应用及客户端应用的开
发

  TA的全称是Trust Application，即可信任应用
程序。CA的全称是Client Applicant，即客户端应用
程序。TA运行在OP-TEE的用户空间，CA运行在
REE侧。CA执行时代入特定的UUID和命令ID参数
就能实现请求特定TA执行特定操作的需求，并将
执行结果返回给CA。通过CA对TA的调用可实现在
REE侧对安全设备和安全资源的操作。普通用户无
法知道TA的具体实现，例如操作使用了什么算
法、操作了哪些资源、获取了哪些数据等，这也就
确保了相关资源和数据的安全。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 668

21.1 TA及CA的基本概念

  GP规范定义了CA调用TA的所有接口以及相关
结构体和变量类型，同时也定义了TEE侧用户空间
的所有接口和相关结构体和变量类型。如果TEE方
案提供方是遵循GP规范实现了规范中定义的接口，
上层应用开发者按照GP规范开发的CA和TA就能正
常运行于各家TEE平台中。CA与TA有一些基本的
概念，这些部分组成了TA与CA之间进行交互的基
本条件，这些基本概念的说明如下。

1.TEE Contexts

  TEE上下文（TEE Contexts）用于表示CA与
TEE之间的抽象连接，即通过TEE上下文可将REE
侧的操作请求发送到TEE侧。需注意的是，在执行
打开CA与TA之间的会话之前必须先获取到TEE上
下文。一般该值是打开REE侧的TEE驱动设备时返
回的句柄，如果在REE侧支持多个TEE驱动，则在
调用TEEC_InitializeContext时可指定具体的驱动设
备名来获得特定的TEE上下文。

2.Session

  会话（Session）是CA与特定TA之间的抽象连

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 669

接。只有建立了CA与TA之间的会话后，CA才可调
用TA中的命令来执行特定的操作。调用
TEEC_OpenSession函数后，TEE会将建立的会话内
容返回给CA，一个会话包含TEE上下文和会话ID
值。

3.Commands

  命令（Commands）是CA与TA之间通过会话
进行具体操作的基础。在交互过程中，CA通过指
定命令ID通知TA执行与命令ID匹配的操作。至于
TA中执行什么操作则完全由TA开发者决定，命令
ID只是CA与TA约定的某个特殊操作的ID值。

4.Share Memroy

  共享内存（Share Memroy）被用于CA与TEE之
间进行数据交互，CA可通过注册或分配的方式通
知TEE注册或分配CA与TA之间的共享内存，CA和
TEE对该块共享内存都具有指定的读写权限。

5.Memory References
  Memroy Reference是CA与TEE之间一段固定范
围的共享内存，Memory Reference可指定一个完整
的共享内存块，也可指定共享内存块中的特定区
域。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 670

6.UUID

UUID是一个TA的身份标识ID。当CA需要调
用某个TA时，TEE侧通过UUID来决定要加载和运
行哪个TA镜像。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 671

21.2   GP标准

       GP标准的全称是GlobalPlatform，该标准对
TEE的框架和安全需求做出了明确的规定[1]，    并对
REE侧提供的接口函数、数据类型和数据结构体也
做出了明确的定义，并对TEE侧提供给TA开发者使
用的接口函数、数据类型、数据结构体做出了明确
的规定和定义。关于GP规范与TEE相关的文档，读
者可到如下链接中自行查阅和下载：

       https://www.globalplatform.org/mediaguidetee.asp

            对CA和TA的开发者而言，需要仔细阅读GP对
REE侧和TEE侧各种接口函数和数据结构体的定
义，只有熟悉了接口函数以及数据结构体的定义后
才能正确使用这些接口来开发特定的CA和TA。

[1]        GP规范系统架构文档：
GPD_TEE_SystemArch_v1.0.pdf。








https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 672

21.3 GP标准对TA属性的定义

  TA的属性定义了该TA的运行方式、链接方
式、堆栈大小、版本等信息。在GP标准中对一个
TA所需要具有的属性进行了严格的定义和说明，
这些属性的名称、作用、值的内容说明如表21-1所
示。

      表21-1 TA个属性说明表








    OP-TEE中TA的扩展属性如表21-2所示。

    表21-2 OP-TEE对TA属性的扩展列表


  需要被设定的TA属性都在TA源代码的

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 673

user_ta_headr_defines.h文件中被定义，gpd.ta.appID
的值通常被设置成该文件中TA_UUID的值。
gpd.ta.singleInstance、gpd.ta.multiSession、
gpd.ta.instanceKeepAlive的值通过在该文件中定义
TF_FLAGS的值来确定。gpd.ta.dataSize的值由该文
件中定义TA_DATA_SIZE的值来确定。
gpd.ta.stackSize的值由该文件中定义
TA_STACK_SIZE的值来确定。在OP-TEE中
gpd.ta.version和gpd.ta.description的值使用默认值。
gp.ta.description和gp.ta.version的值由
TA_CURRENT_TA_EXT_PROPERTIES宏定义来确
定。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 674

21.4 GP标准定义的接口

  GP标准中对REE侧和TEE侧提供给CA和TA调
用的接口都做出了明确的定义，包括接口函数的函
数名、作用、参数说明、返回值等。GP官方网站中
名称为TEE_Client_API_Specification-Vx.x_c.pdf的
文档给出了这些接口的详细说明，根据发布版本的
不同，定义的接口可能也会有所不同。TEE侧定义
的接口函数属于内部接口，详细内容查阅GP提供的
名称为
GPD_TEE_Internal_Core_API_Specification_vx.x.pdf
的文档。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 675

21.4.1 GP定义的客户端接口

  GP定义的客户端接口包括9个函数和1个宏[1]，
使用这9个接口函数和宏就可满足CA的开发，只是
CA需要配合TA一起使用，双方定义的UUID的值和
命令ID的值需保持一致，这9个函数和宏的名称和
作用如表21-3所示。

  表21-3　客户端函数和宏的作用说明列表








  上述9个函数的函数原型、作用、参数说明、
返回值的说明在本书8.2节中已进行了详细的介绍。
这部分接口的实现会被编译到libteec库文件中，最
终会被CA调用。
[1] GP规范CA中API说明文档：
TEE_Client_API_Specification-V1.0_c.pdf。


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 676

21.4.2 GP定义的内部接口

  GP定义的内部接口是供TEE侧的TA或其他功
能模块使用[1]。大致可以分为Framwork层API、对
数据和密钥操作的API、密码学操作API、时钟
API、大整数算法API。由于API较多，故在本书中
就不对每个API进行一一说明，只给出各API的作用
和名称。

1.Framwork层接口
  Framwork层API是TEE用户空间实现对内存、
TA属性等资源进行操作的API，该类API的说明如
下表21-4所示。
     表21-4 Framwork层API说明列表










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 677

2.对数据和密钥操作的API
  GP规定了特定的操作接口，用于TEE实现对各
种数据流和密钥的操作。在使用安全存储、加解密
等操作时都需使用该部分的接口。对数据流的操作
是以object的方式完成的，对密钥的操作则是使用

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 678

attr的方式来完成的。该部分API名称以及作用关系
如表21-5所示。
  表21-5　对数据和密钥操作的API说明列表










    3.密码学操作接口


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 679

TEE最重要的功能之一是提供了各种密码学算
法的实现，并确保这些算法运行于安全环境中。GP
定义了各种密码学的操作接口，这些API的名称和
作用说明如表21-6所示。
表21-6　密码学操作API说明列表










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 680

4.时间操作接口

GP对在TEE中操作系统时间的接口也作出了明
确的规定，这部分接口的函数名称和作用说明如表
21-7所示。
表21-7　时间操作接口说明列表





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 681

5.大整数算法接口

  TEE中会提供对大整数的操作接口，GP规范对
该部分的接口进行了定义，由于篇幅有限，这部分
的内容就不详细列出。这部分的接口主要包括对大
整数的初始化、加减乘除、转换、对比、获取具体
的位、模幂运算等，详细内容可参阅GP的文档。

[1] GP规范TA中API说明文档：
GlobalPlatform_Trusted_User_Interface_API_v1.0.pdf。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 682

21.5 TA和CA的实现

  第4章中提供了一个完整的CA和TA的示例，本
节将详细介绍如何完成CA和TA源代码的实现。本
节中并不涉及TA中的特定操作的实现，只是介绍
如何搭建CA和TA的整体框架和设定相关的参数，
关于TA中的特定操作由读者根据自身的实际需求
进行开发。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 683

21.5.1　建立CA和TA的目录结构

开始CA和TA源代码的开发前首先需要在OP-
TEE源代码中创建CA和TA的目录结构。在OP-TEE
源代码的根目录下创建CA和TA的目录结构和相应
的文件，具体的目录结构体可参阅第4章中提供的
示例，关于各子目录中Makefile文件的内容可参考
示例中对应Makefile。

              秉承功能模块化的理念，建议在创建TA中的
源代码文件时分为三个部分。第一个部分为TA的
入口调用文件，该TA中TA_xxxEntryPoint接口的实
现将保存在该文件中。第二部分为TA的处理文
件，该文件中的内容是调用
TA_InvokeCommandEntryPoint函数时switch case中
各case中的具体实现。第三部分为TA具体操作的实
现，建议将不同的功能实现保存在不同的文件中，
这样从代码阅读或调试时便于理解。

建立完目录结构和相关文件后，需将OP-TEE
中的user_header_defines.h文件保存到TA的源代码
中。通过修改该文件中的内容可实现对该TA属性
的设定。



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 684

21.5.2 CA代码的实现

                                            在CA源代码中调用GP规范中定义的客户端的
接口就可实现对TA的调用。在CA中调用客户端接
口的顺序依次如下。

1.TEEC_InitializeContext

初始化CA与TEE之间的上下文，打开TEE驱动
设备，得到一个TEEC_context。

2.TEEC_OpenSession

调用时代入TA的UUID，建立CA与指定TA之
间的会话。

3.TEEC_PARAM_TYPES

配置需要发送到TA的参数的属性，可将参数
设定为input属性和output属性。

4.TEEC_InvokeCommand

代入会话ID、命令ID、包含参数内容的
operation变量，开始发送请求给TEE来调用TA中的
特定操作。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 685

5.TEEC_CloseSession

  调用完成后关闭CA与TA之间的会话。

6.TEEC_FinalizeContext

  关闭CA与TEE之间的连接。
  在编写CA代码时需注意，在关闭上下文之前
不要重复调用TEEC_InitializeContext函数，否则会
报错，且如果在没有调用TEEC_CloseSession函数
之前重复执行打开会话的操作可能会导致TEE中的
空间不足。CA中的UUID和命令ID的定义一定要保
证与TA中的命令ID和UUID的定义一致。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 686

21.5.3 TA代码的实现

  TA代码需实现具体功能的所有操作，TA被
TEE调用的各种操作的入口函数就是在表21-4部分
的API。所以需要在TA中实现这些API，最重要的
是对TA_InvokeCommand-EntryPoint函数的实现。
该函数需要定义各种命令ID对应的操作，至于每个
命令ID需要实现什么功能就由开发者决定，但该命
令ID的定义需要与CA中的命令ID的定义保持一
致。

  TA属性的设定可通过修改
user_ta_head_defines.h文件来实现，主要需修改如
下的宏定义：

  ·TA_UUID：该TA的UUID值；
  ·TA_FLAGS：TA的访问属性，具体内容请参
阅21.3节和GP规范；

  ·TA_STACK_SIZE：指定该TA运行时栈空间
的大小；

  ·TA_DATA_SIZE：指定该TA运行时堆空间的
大小；


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 687

  ·TA_CURRENT_TA_EXT_PROPERTIES：该
TA的扩展属性，主要包括TA名字、版本等。
  关于TA代码的开发可以参考示例中TA部分的
源代码。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 688

21.6 TA和CA的集成

编辑完TA和CA的源代码后，需修改源代码中
的Makefile文件和OP-TEE工程源代码中对应的板级
mk文件和common.mk文件。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 689

21.6.1 CA和TA的Makefile的修改

   需将CA所有源代码文件对应的目标文件添加
到CA的Makefile文件中的OBJS目标中，并修改all
目标的内容，将BINARY变量的值修改成开发者指
定的值，并修改CFLAGS变量，将CA包含的头文件
路径添加到cflag中。

   对于TA部分则需修改ta目录下的Makefile文件
和sub.mk文件。将ta/Makefile文件中的BINARY变
量修改成UUID的值，将TA所有源代码文件的名称
添加到ta/sub.mk文件中的srcs-y变量中，同时修改
该文件中的global-incdirs-y变量，将TA的头文件目
录添加到全局头文件路径中。对于srcs-y和global-
incdirs-y变量的名字，开发者也可将其修改成srcs-
$(XXX)和global-incdirs-$(XXX)的形式，然后通过
在optee_os/mk/config.mk文件中定义XXX？=n或者
是XXX？=y来控制在编译OP-TEE整个工程时是否
需要编译该TA。







    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 690

21.6.2 OP-TEE中comm.mk和xxx.mk文件的修改

  若需要将该TA和CA集成到OP-TEE系统中，则
需修改build/xxx.mk文件和build/common.mk文件。
对xxx.mk文件的修改主要是将该TA和CA的编译集
成到系统的编译目标当中，而对common.mk文件的
修改则是指定编译TA和CA的具体依赖关系和编译
路径，以及编译结果的保存路径和CA的编译结果
是否需要集成到REE的文件系统中等。关于如何修
改commom.mk和xxx.mk文件可参考19.1节。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 691

21.7 TA和CA的调试

  调试一个TA和CA程序时最主要的手段就是在
报错的地方打印。在开发TA和CA的过程中会牵扯
到程序编译、应用层、内核层、驱动层的问题。

  关于程序编译的问题只需要根据编译报错的日
志进行修改即可，若对编译过程不熟悉可在编译系
统中添加打印的方式跟踪整个编译过程，然后定位
编译报错的位置后进行对应的修改，一般都是函数
和变量的定义问题以及相关选项的设置问题。

  对于应用层的调试，最实用的方法就是在出错
的地方添加打印信息，将错误时的数据打印出来然
后结合实际的代码逻辑进行代码的调整和修改。为
方便形成自己的调试风格，建议读者建立一套自己
的调试打印模块，将系统提供的打印接口与自己的
打印模块进行对接之后就可以很好地进行调试。

  OP-TEE的内核层面的调试主要是各种密码学
算法的报错调试。为确定在哪一步操作地方出现了
错误，读者可以在代码中添加对应的打印信息，然
后根据打印的信息进行对应的修改。关于AES和
RSA算法部分，注意输入数据的长度对齐问题，至
于加解密出来的数据是否正确，读者可使用openssl


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 692

提供的接口进行实现后对两者的结果进行对比验
证。

  驱动层面则需要接口J-TAG或者Trace32等工具
来进行调试，但到了该级别的调试就比较复杂，首
先是调试环境以及调试工具的使用，但使用该方法
更容易定位问题。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 693

21.8 TA和CA的使用

  整个CA可被编译成库文件供上层使用也可编
译成可执行文件作为服务或指令在REE侧被使用。
  当CA被编译成库文件后，使用该库文件时需
为使用者提供对应的头文件。头文件中需要声明该
库文件暴露给上层用户调用的API原型，在Android
系统中也可将CA实现的接口以JNI的方式进行封装
供APP使用。
  当CA需要被编译成可执行文件时，需要添加
main函数，在main函数中调用CA实现的接口来完
成具体的操作。第4章提供的示例中就是将CA部分
编译成可执行文件，系统启动后，在REE侧的终端
中输入可执行文件的名字来让CA调用TA完成具体
的操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 694

21.9　小结

       本章介绍了开发CA和TA的基本过程以及如何
修改CA和TA的Makefile，同时也介绍了如何将CA
和TA的编译集成到OP-TEE工程的整个编译系统
中。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 695

第22章　安全驱动的开发

  支持TruztZone技术的芯片可将某个特定外部设
备配置成安全设备，使其只能被处于安全世界状态
（SWS）的ARM核访问。如果要在OP-TEE中使用
安全设备，需要在OP-TEE OS中集成该安全设备的
驱动程序，TA或OP-TEE OS可使用该安全驱动提
供的接口来使用该安全设备。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 696

22.1　安全设备的硬件安全隔离

  系统的外部设备一般是通过APB总线挂接到
AXI总线上的，APB总线不支持ARM核对设备访问
时进行安全检查的功能，故如果要将某个外部设备
配置成安全设备，则需在SOC中添加TZPC组件和
AXI-to-APB桥。TZPC组件负责将某个特定外部设
备配置成安全设备，并为该安全设备提供额外的安
全信号，AXI-to-APB桥使用TZPC配置给该外部设
备的安全信号来校验ARM核发送的访问请求中的安
全状态位（NS bit）是否与之匹配，如果TZPC给外
部设备提供的信号为安全信号而ARM核的访问请求
是在正常世界状态（NWS）发起的，则AXI-to-
APB总线会判定访问失败，从而实现系统对该外部
设备的安全隔离。

  TZPC组件主要有两个作用，一是为TZMA提
供安全区域大小配置信号，用于TZMA来配置片上
SRAM、ROM安全区域的大小，另外一个作用是接
入到AXI-to-APB总线上，为外部设备提供安全信
号，将某个外部设备配置成安全设备。TZPC组件
的信号连接图如图22-1所示。
  TZPCR0SIZE信号线将被连接到TZMA组件
上，用于TZMA配置片上SRAM、ROM安全区域的

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
       更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 697

大小，TZPCDECPROTx信号线将连接到AXI-to-
APB桥上，用于配置某个外设是否为安全设备。
TZPC最多支持将24个外部设备设定为安全设备，
且需将TZPC组件的寄存器地址设定在安全地址范
围内。TZPC提供了18个寄存器，这些寄存器用于
配置安全信号。这些寄存器的相关信息如表22-1所
示。

  通过配置TZPC组件寄存器的值可设定特定的
安全信号的输出组合，用于将外部设备设定成安全
设备。TZPC的基地址并不固定，但需确保TZPC的
基地址是在安全地址区域中的。










    图22-1 TZPC外部管脚示意

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 698

表22-1 TZPC组件的寄存器信息列表










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 699

22.2 OP-TEE中安全驱动的框架

OP-TEE中的安全驱动是OP-TEE操作安全设备
的载体。TA通过调用某个安全驱动的接口就可实
现对特定安全设备的操作。安全驱动在OP-TEE中
的软件框架如图22-2所示。

     系统服务层并非必需的，主要是为方便管理和
上层使用。例如OP-TEE提供了各种各样的密码学
算法，每一种算法的实现可通过不同的硬件引擎来
完成。为统一管理，可将这些硬件引擎驱动提供的
操作接口统一集成到一个系统服务中，而上层用户
只需调用系统服务暴露的接口就可实现对硬件引擎
的调用。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 700

图22-2 OP-TEE中各软件层框架










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 701

22.2.1　系统服务层

  系统服务层在OP-TEE启动过程中由initcall段的
代码进行初始化和启动，一个系统服务的初始化函
数则是通过使用service_init宏来进行定义并在编译
时链接到OP-TEE的镜像文件中。在编译OP-TEE
时，该初始化函数将被保存到OP-TEE镜像文件的
initcall段中。至于系统服务的初始化函数所要执行
的内容则由开发者自行决定，一般是在系统服务的
初始化函数中进行该服务的配置、状态量的初始化
以及系统服务提供给上层调用的操作接口变量的初
始化，系统服务提供的结构体变量会包含用于实现
具体功能的函数指针变量，这些函数指针变量指向
的函数就是安全驱动提供给TA调用的操作接口。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 702

22.2.2　驱动层

  OP-TEE启动过程中会执行各安全驱动的初始
化，驱动的初始化函数是在OP-TEE执行initcall段中
的内容时被调用的，在OP-TEE中通过使用
driver_init宏来告诉编译器，在编译时将driver_init
宏传入的函数作为某个驱动的入口函数保存在镜像
文件的initcall段中。安全驱动的初始化主要用来完
成安全设备的寄存器的配置以及私有数据的初始
化。如果某个安全驱动需要系统服务的配合，则还
需要将驱动提供的操作接口连接到系统服务中的操
作接口变量中。若该驱动不需以系统服务的方式向
上层提供操作接口，则不用将对应接口暴露给系统
服务，而是由TA通过系统调用的方式直接调用安
全驱动的接口来操作安全设备。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 703

22.2.3　驱动文件在源代码中的位置

  安全驱动需要被编译到OP-TEE镜像文件中，
OP-TEE中有专门的目录来存放驱动和系统服务的
源代码。将驱动编译到OP-TEE镜像文件之前还需
修改对应的sub.mk文件，OP-TEE中保存驱动和系
统服务源代码的目录对应关系如表22-2所示。

表22-2　安全驱动和系统服务源代码对应的目录列
        表










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 704

22.3　安全驱动的开发过程和示例

  在OP-TEE中，若需要使用系统服务的方式为
上层TA提供操作接口，则一个完整的安全驱动需
要实现TA接口部分、系统调用部分、系统服务部
分、驱动实现部分。本节将结合实际的示例介绍这
四部分的开发流程。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 705

22.3.1　示例代码获取和集成

本示例中的驱动只实现了对内存的读写操作，
并提供了测试使用的TA和CA。读者可使用如下指
令从GitHub上获取到示例源代码：

git clone https://GitHub.com/shuaifengyun/opentee_driver.git

下载完代码后就需要将该TA和CA集成到OP-
TEE中，需修改OP-TEE源代码build目录下的
qemu.mk（开发者板级对应的mk文件）和
common.mk文件，同时也需要将安全驱动集成到
OP-TEE的内核中。然后编译整体OP-TEE后就能够
使用该份示例代码来验证本书提供的安全驱动示例
是否运行正常。

获取到示例代码后将opentee_driver/my_test目
录全部复制到op-tee的根目录下，再切换到根目录
的build目录中，然后使用git apply命令合入补丁文
件后就可完成测试使用的TA和CA集成到OP-TEE，
合入全部补丁的操作步骤如下：

1）将示例代码中的
my_test_common_3.0.0.patch文件和


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 706

my_test_qemu_3.0.0.patch文件复制到build目录中，
将0001-Integrate-secure-driver-test-into-op-tee.patch
文件复制到optee_os目录中。
   2）切换到build目录，使用如下命令合入补
丁：

  git apply my_test_common_3.0.0.patch
  git apply my_test_qemu_3.0.0.patch

   3）切换到optee_os目录，使用如下命令合入安
全驱动在内核中的补丁：

  git am 0001-Integrate-secure-driver-test-into-op-tee.patch

   将补丁合入完成后就可使用make-f qemu.mk all
编译整个工程，然后使用make-f qemu.mk run-only
来启动OP-TEE，在启动的正常世界状态的终端执
行secStorTest命令就能实现该示例的CA对TA的调
用。示例代码的运行效果如图22-3所示。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 707

图22-3　安全驱动示例运行










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 708

22.3.2　驱动实现

   开发一个安全驱动时，需要在
optee_os/core/drivers目录中建立该安全驱动的源文
件，在源文件中实现驱动的初始化函数、操作设备
的接口函数（read、write、ioctl），具体的接口函
数由开发者自行定义。若该驱动需要在系统启动过
程中执行一些初始化操作则可使用driver_init宏进行
定义，编译完成后需要被执行的内容将会被保存到
镜像文件的initcall段中，这些使用driver_init宏定义
的内容将在OP-TEE启动时被调用。

   示例源代码中的driver_test.c文件需要放在
optee_os/core/drivers目录中，然后修改
optee_os/core/drivers目录下的sub.mk文件，将
driver_test.c文件添加编译系统中。在sub.mk文件中
添加如下内容：

 srcs-y += driver_test.c

   若需要使用宏的方式来控制该驱动的编译，可
将添加到sub.mk的内容修改成“srcs-
$(CFG_XXX)+=driver_test.c”，然后在
optee_os/mk/config.mk文件中定义CFG_XXX变量，


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 709

通过将CFG_XXX变量赋值成y或n来控制该驱动是
否需要被编译进系统。

   该驱动对应的头文件driver_test.h文件需保存到
optee_os/core/inlcude/drivers目录中，该文件中声明
了该驱动暴露给外界调用的接口和相关结构体。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 710

22.3.3　添加系统服务

                       系统服务的添加不是必需的，为方便对底层驱
动的管理和对外部设备的扩展，可将安全驱动的接
口接入到某个系统服务中，通过系统服务向外界暴
露调用接口，以便上层TA可以使用该安全驱动。
在本示例中建立的系统服务的源代码为tee_test.c文
件，需将该文件保存到optee_os/core/tee目录中，同
时将tee_test.h文件保存到optee_os/core/include/tee目
录中，然后修改optee_os/core/tee目录中的sub.mk文
件，添加“srcs-y+=tee_test.c”，将tee_test.c集成到编
译系统中。也可使用宏来控制该系统服务的编译，
其实现方法与上一节相同。

 在tee_test.c文件中使用service_init宏来定义该
系统服务的初始化函数（tee_test_init），该初始化
函数将会被编译到OP-TEE的初始化段中，       OP-TEE
启动时将会执行服务段中包含的函数，调用
tee_test_init函数初始化该系统服务。








 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 711

22.3.4　添加系统调用

上层的TA运行于OP-TEE的用户空间，如果上
层的TA需要调用安全驱动，则需通过调用系统调
用接口的方式来调用安全驱动提供的操作接口。若
要在TA中使用本示例中的安全驱动，则还需在OP-
TEE中增加该驱动对应的系统调用。包括用户空间
接口的定义和内核空间接口的定义，关于OP-TEE
中系统调用的实现原理可参阅第16章。

1.用户空间代码的修改
修改
optee_os/lib/libutee/arch/arm/utee_syscalls_asm.S文
件，添加如下内容：

UTEE_SYSCALL utee_testDriver_write, TEE_SCN_TESTDRIVER_WRITE, 3
UTEE_SYSCALL utee_testDriver_read, TEE_SCN_TESTDRIVER_READ, 3
UTEE_SYSCALL utee_testDriver_dump, TEE_SCN_TESTDRIVER_DUMP, 2

                   utee_testDriver_xxx是在TA中调用该驱动时使
用的函数，TEE_SCN_TESTDRIVER_XXX是该系
统调用对应的索引值。上层TA调用
utee_testDriver_xxx函数后会进入OP-TEE的内核空
间，系统通过查找TEE_SCN_TESTDRIVER_XXX


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 712

对应的接口来找到该功能在OP-TEE内核中的实
现。最后的数字表示调用该接口时需要代入的参数
的个数。

  修改optee_os/lib/libutee/include/utee_syscalls.h
文件，添加如下内容，申明上述三个函数接口。在
TA的源代码中包含该头文件后就可调用这三个接
口来对该安全驱动进行调用。

TEE_Result utee_testDriver_write(void *buf, size_t blen, size_t offset);
TEE_Result utee_testDriver_read(void *buf, size_t blen, size_t offset);
TEE_Result utee_testDriver_dump(void *buf, size_t blen);

  修改
optee_os/lib/libutee/include/tee_syscall_numbers.h文
件，添加上述三个系统调用接口的索引值，并修改
TEE_SCN_MAX的值，需要修改和添加的内容如
下：

#define TEE_SCN_TESTDRIVER_WRITE      71
#define TEE_SCN_TESTDRIVER_READ     72
#define TEE_SCN_TESTDRIVER_DUMP     73
#define TEE_SCN_MAX        73

2.内核空间代码的修改
  修改optee_os/core/arch/arm/tee/arch_svc.c文件


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 713

中系统调用数组变量tee_svc_syscall_table的内容，
将上述系统调用对应的内核层接口添加到该数组
中，并包含申明这三个接口的头文件，在该文件中
添加的内容如下：

SYSCALL_ENTRY(syscall_testDriver_write),
SYSCALL_ENTRY(syscall_testDriver_read),
SYSCALL_ENTRY(syscall_testDriver_dump),
#include <tee/tee_test.h>

上述三个函数的具体实现在tee_test.c文件中，
读者可自行查阅这三个接口函数的实现。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 714

22.3.5　测试使用的TA和CA

                           将该示例的测试TA和CA添加到OP-TEE中需要
修改读者开发环境对应的mk文件中。以使用QEMU
方式运行OP-TEE为例，则需要修改qemu.mk文件添
加该示例代码的编译目标，修改步骤如下：

1）添加my_test的编译目标：

############################################################################
# secure driver test TA--my_test
############################################################################
my_test: my_test-common
my_test-clean: my_test-clean-common

2）将my_test和my_test-clean添加到全局的all
和clean目标依赖关系中：

all: bios-qemu qemu soc-term optee-examples my_test
clean: bios-qemu-clean busybox-clean linux-clean optee-os-clean \
optee-client-clean qemu-clean soc-term-clean check-clean \
optee-examples-clean my_test-clean

添加部分的主要作用是定义my_test目标并建立
该编译目标与all的依赖关系，在编译整个OP-TEE
工程时会被使用到。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 715

修改完板级编译的mk文件后，
                 还需修改
build/common.mk文件。修改的内容主要是将
my_test的编译目标集成到系统编译中，需要修改的
内容如下：

1）定义my_test路径变量：


MY_TEST_PATH ?= $(ROOT)/my_test



2）添加my_test的目标依赖，修改filelist-tee-
common目标的依赖关系如下：


filelist-tee-common: optee-client xtest optee-examples my_test



3）增加TA和CA的common目标：


############################################################################
# my_test
###########################################################################
MY_TEST_COMMON_FLAGS ?= HOST_CROSS_COMPILE=$(CROSS_COMPILE_NS_USER)\
TA_CROSS_COMPILE=$(CROSS_COMPILE_S_USER) \
TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR) \
TEEC_EXPORT=$(OPTEE_CLIENT_EXPORT)

.PHONY: my_test-common
my_test-common: optee-os optee-client
$(MAKE) -C $(MY_TEST_PATH) $(MY_TEST_COMMON_FLAGS)
MY_TEST_CLEAN_COMMON_FLAGS ?= TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR)
.PHONY: my_test-clean-common
my_test-clean-common:
$(MAKE) -C $(MY_TEST_PATH) $(MY_TEST_CLEAN_COMMON_FLAGS) clean




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 716

4）添加clean操作的依赖关系：


optee-os-clean-common: xtest-clean optee-examples-clean my_test-clean



5）在filelist-tee-common中添加TA和CA镜像需
要被打包到文件系统中的操作：



@echo “#secure driver test TA “ >> $(fl)
@if [ -e $(MY_TEST_PATH)/host/my_test ]; then \
  echo "file /bin/my_test" \
  "$(MY_TEST_PATH)/host/my_test 755 0 0" >> $(fl); \
  echo "file /lib/optee_armtz/9269fadd-99d5-4afb-a1dc-ee3e9c61b04c.ta" \
  "$(MY_TEST_PATH)/ta/9269fadd-99d5-4afb-a1dc-ee3e9c61b04c.ta 444 0 0" \
  >> $(fl); \
fi










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 717

22.4　安全驱动示例的测试

  完成所有修改之后，编译整个OP-TEE工程然
后运行。在OP-TEE的启动日志中能看见示例中的
系统服务和驱动启动的日志，启动的日志如图22-4
所示。




    图22-4　安全驱动示例启动日志

系统启动后，在REE侧的终端中输入对应的指
令就可通过TA调用到该示例的安全驱动，指令说
明如下。

1.向驱动中写入数据

my_test writeDev [offset] [len]

offset：表示需将数据写入驱动提供的buffer中
的偏移位置。

len：表示需要写入驱动中数据的长度。

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 718

  写入驱动中的数据在CA源代码中被设定，读
者可通过修改CA源代码中g_WriteData变量中的值
将不同的内容写入该安全驱动中。

2.读取驱动中的数据

my_test readDev [offset] [len]

  offset：表示从驱动中buffer的哪个位置开始读
取。

  len：表示需要从驱动中读取的内容长度。

3.打印出驱动中的数据

my_test dumpDev [len]

  len：表示需要打印的数据的长度。

  用于测试添加的模拟安全驱动的TA和CA运行
的效果如图22-5所示。






https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 719

图22-5 TA和CA运行的效果










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 720

22.5　小结

  本章介绍了OP-TEE中安全设备驱动的开发以
及实现安全设备的安全隔离的原理。当需要在系统
中增加安全设备时，除了需在OP-TEE中开发该设
备对应的安全驱动之外，还需修改TZPC的配置为
该设备提供安全信号。TA通过调用系统调用接口
的方式陷入OP-TEE的内核空间来使用驱动，如需
对多个安全设备进行统一管理，则可添加一个系统
服务，将各安全驱动提供的接口集成到该系统服务
中，使该系统服务封装接口暴露给上层使用。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 721

第23章　终端密钥在线下发系统

  在终端设备实际使用过程中，终端设备与服务
器端可能会存在通信的情况，为确保通信过程中数
据的安全，一般会对通信数据进行加密操作。而在
终端设备生产过程中，由于产品的生产批次和后续
安全功能的扩展，通信所需要的密钥并不一定会在
产品出厂之前就预置到终端设备中，此时就可使用
TEE来构建终端密钥的在线下发系统来确保密钥被
安全分发到特定的终端设备中，后期就可使用下发
的密钥实现终端设备与服务器端进行密文通信。本
章将介绍使用OP-TEE搭建的一种密钥在线下发系
统。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 722

23.1　密钥在线下发系统的框架

  将下发的密文密钥包发送到OP-TEE中，由OP-
TEE来完成对密文数据包的解密以及密钥的保存就
能确保下发的密钥的安全性，如果在使用该密钥时
也将相关加密操作放在OP-TEE中，这样可以确保
密钥在任何时候都不被暴露在REE侧，这样可以构
建一个安全的通信密文环境。整个终端密钥在线下
发系统的框架图如图23-1所示。









     图23-1　密钥在线下发系统框
  密钥在线下发系统在REE侧会运行一个常驻进
程用于接收服务器端发送的密文密钥数据包，该进
程在接收到数据包后直接调用下发系统的CA接
口，将数据发送给OP-TEE中密钥下发系统的TA，


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 723

该TA会按照约定的数据格式和密钥解析并解密下
发的数据包，从而获得明文的密钥，然后调用OP-
TEE的安全存储功能保存该密钥，在使用时同样也
通过该TA来获取该密钥。当然读者也可以借助自
己的实际环境将密钥保存到希望保存的地方，但最
好采取密文的形式保存该密钥。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 724

23.2　密钥在线下发的数据包格式

  密钥下发系统的数据包是以密文的形式被发送
到终端设备，为确保数据的完整性和合法性，最后
会对密钥数据包的内容使用RSA算法进行电子签
名，数据包的格式如图23-2所示。










       图23-2　数据包格式

  整个数据包分为密文数据区域和哈希区域，密
文数据部分包含需要下发的数据经对称加密处理之
后数据，而哈希区域则是使用SHA256算法计算的
密文区域的哈希值。由于设备厂商在生产设备时会
收集每台终端设备的相关硬件信息，所以可使用这
些硬件信息作为因子用于生成加密使用的密钥。下


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 725

发的密钥是通过盐值、密码和重复数经过PBKDF算
法计算获得的。

  密文数据区域中包含的信息说明如下：

  ·KeyType：需要被下发的密钥类型，读者可以
根据自己实际需求进行定义，用于分发不通过类型
的密钥；

  ·MagicNum：数据包的魔术数，用于校验；
  ·DataLength：整个数据包中有效数据的长度；

  ·Count：用于生成密钥时使用的重复数；
  ·SaltData：存放用于生成密钥时使用的盐值；
  ·Length of salt dat：盐值的数据长度；

  ·Password Data：存放用于生成密钥时使用的
密码；

  ·Length of password data：密码的数据长度；
  ·Reservet：预留的区域；

  ·HASH：下发的数据明文数据的哈希值，用于


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 726

校验明文数据的完整性。

  整个密文会使用AES128算法的CBC模式进行
加密。由于在OP-TEE中AES128的CBC模式采取的
是无填充的方式进行加密操作，故需要明文数据的
长度为八个字节的倍数。

  哈希数据区域保存的是密文数据区域的哈希
值，在OP-TEE中可使用该值来判定终端接收到的
数据包是否完整。

  最后使用BASE64算法对密文数据区域和哈希
数据区域的数据进行转换，最终生成的数据就是被
下发到终端设备的数据包。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 727

23.3　密钥在线下发系统示例

  本书提供的密钥在线下发系统示例代码中包含
了测试使用的CA和TA的源代码以及用于生成下发
的数据包的离线工具。读者可通过修改离线工具中
定义的盐值和密码来获取不同的下发数据包，读者
可将获取到的数据包内容填充到CA代码中的
g_Message变量来验证数据的可用性。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 728

23.3.1　示例代码获取和集成

  本书提供了根据GP标准定义的接口，使用OP-
TEE安全存储功能对数据进行保护的示例TA和CA
代码，读者可使用如下指令从GitHub中获取代码：

 git clone https://GitHub.com/shuaifengyun/save_key.git

  下载完代码后就需要将该TA和CA集成到OP-
TEE中，需修改OP-TEE源代码build目录下的
qemu.mk（开发者板级对应的mk文件）和
common.mk文件。然后编译整体OP-TEE后就能使
用在线下发系统的功能。

  获取到示例代码之后，切换到如下build目录
下，然后使用git apply命令合入补丁文件后就可完
成将该示例集成到OP-TEE，合入补丁的操作步骤
如下：

  1）将示例代码中的
save_key_common_3.0.0.patch文件和
save_key_qemu_3.0.0.patch文件复制到build目录
中。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 729

  2）切换到build目录，使用如下命令合入补
丁：

git apply save_key_common_3.0.0.patch
git apply save_key_qemu_3.0.0.patch

  将补丁合入完成之后就可使用make-f qemu.mk
all编译整个工程，然后使用make-f qemu.mk run-
only来启动OP-TEE，在启动的正常世界状态
（NWD）的终端执行saveKey save命令就能使CA中
的数据包数据通过OP-TEE进行解密和保存。示例
代码的运行效果如图23-3所示。










图23-3 save_key示例运行



https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 730

23.3.2　板级编译文件的修改

                            将该示例的TA和CA添加到OP-TEE中需要修改
读者开发环境对应的mk文件。以使用QEMU方式运
行OP-TEE为例，则需要修改qemu.mk文件添加该示
例代码的编译目标，修改步骤如下：

1）添加secStorTest的编译目标：

############################################################################
# save key TA
############################################################################
save_key: save_key-common
save_key-clean: save_key-clean-common

2）将secStorTest和secStorTest-clean添加到全
局的all和clean目标依赖关系中：

all: bios-qemu qemu soc-term optee-examples save_key
clean: bios-qemu-clean busybox-clean linux-clean optee-os-clean \
optee-client-clean qemu-clean soc-term-clean check-clean \
optee-examples-clean save_key-clean

添加部分的主要作用是定义save_key目标并建
立该编译目标与all的依赖关系，在编译整个OP-
TEE工程时会被使用到。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 731

23.3.3　通用编译文件的修改

修改完板级编译的mk文件后，
                  还需修改
build/common.mk文件。修改的内容主要是将
save_key的编译目标集成到系统编译中，需要修改
的内容如下：

1）定义save_key路径变量：


SAVE_KEY_PATH    ?= $(ROOT)/save_key



2）添加save_key的目标依赖，修改filelist-tee-
common目标的依赖关系如下：


filelist-tee-common: optee-client xtest optee-examples save_key



3）增加TA和CA的common目标：


############################################################################
# save key demo
###########################################################################
SAVE_KEY_COMMON_FLAGS ?= HOST_CROSS_COMPILE=$(CROSS_COMPILE_NS_USER)\
TA_CROSS_COMPILE=$(CROSS_COMPILE_S_USER) \
TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR) \
TEEC_EXPORT=$(OPTEE_CLIENT_EXPORT)
.PHONY: save_key-common
save_key-common: optee-os optee-client




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 732

$(MAKE) -C $(SAVE_KEY_PATH) $(SAVE_KEY_COMMON_FLAGS)
SAVE_KEY_CLEAN_COMMON_FLAGS ?= TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR)
.PHONY: save_key-clean-common
save_key-clean-common:
$(MAKE) -C $(SAVE_KEY_PATH) \
$(SAVE_KEY_CLEAN_COMMON_FLAGS) clean



4）添加clean操作的依赖关系：


optee-os-clean-common: xtest-clean optee-examples-clean save_key-clean



5）在filelist-tee-common中添加TA和CA镜像需
要被打包到文件系统中的操作：



@echo "# Secure storage test " >> $(fl)
@if [ -e $( SAVE_KEY_PATH)/host/saveKey ]; then \
  echo "file /bin/saveKey" \
  "$(SAVE_KEY_PATH)/host/saveKey 755 0 0"     >> $(fl); \
  echo "file /lib/optee_armtz/fe93c771-c349-492e-89ce-218f4eb6ffa9.ta" \
  "$(SAVE_KEY_PATH)/ta/fe93c771-c349-492e-89ce-218f4eb6ffa9.ta
  444 0 0" >> $(fl); \
Fi










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 733

23.3.4　编译运行

  修改完编译相关文件后，在build目录下执行
make指令编译整个OP-TEE工程。编译完成后，启
动系统就可以在REE侧终端使用saveKey save命令
来测试TA是否能正常地解析密文数据包。TA最后
会使用明文中的盐值、密码和重复数借助PBKDF算
法生成密钥，生成的密钥最终使用OP-TEE的安全
存储系统进行保存。

  在REE侧的终端中运行saveKey get命令可以在
TA中获取到保存的密钥。根据实际的需求可使用
该密钥对数据进行加密和解密操作，且建议在使用
该密钥时，所有的处理过程都需要在OP-TEE中，
以免密钥被暴露到REE侧。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 734

23.4　离线工具的使用

  Save_key/offlineTool目录中存放的是离线工具
的源代码，读者可以直接执行make指令编译该离线
工具，编译完成后最终会生成一个名为cryptoLinux
的可执行文件，在Linux环境中直接执行该文件就
可获取到合法的在线下发数，该执行文件的执行结
果如图23-4所示。
  执行该命令后会在界面中输出经过BASE64处
理后的密文内容及该数据包对应的下发的密钥内
容。读者可根据自己实际需求对代码进行修改以便
达到自身实际需求的目的。










    图23-4　离线工具运行



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 735

23.5　小结

  本章给出了一个使用OP-TEE实现密钥在线下
发的系统示例，使用该框架可实现密钥的密文在线
下发功能，在下发过程中，所有数据都是以密文的
形式存在的，密文生成的算法及加密使用的密钥都
只有OP-TEE知道，在REE侧无法知晓数据的解
密、加密以及保存方式。读者可根据自身实际需求
修改密文组包的格式以及加密算法的类型和密钥的
生成规则搭建自己的在线密钥下发系统，例如可将
组包数据最后的哈希操作换成RSA算法签名，这样
可确保下发数据的完整性和合法性。关于下发的密
钥是如何产生的，读者亦可根据实际需求进行修
改。

  在使用下发的密钥时不可将密钥暴露到REE
侧，这就需将使用密钥对数据进行密码学处理的操
作也集成到该TA中，这样可以确保密钥的下发、
保存、使用都处于一个隔离的安全状态。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 736

第24章　基于OP-TEE的在线支付系统

  基于安全考虑，支付系统的最终结算由支付服
务提供商与银行完成支付结算，而终端设备只为支
付系统的服务器提供支付凭据，让支付系统的服务
器端触发支付操作完成与银行间的账务清算。而终
端设备的支付凭据就在整个在线支付过程中起到了
至关重要的作用。如何确保支付凭据安全且可信的
发送到服务器端并被服务器验证通过就尤为重要。
本章将简要介绍在线支付系统中，终端设备中的
TEE是如何确保数据安全且可信地被支付系统的服
务器端使用。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 737

24.1　在线支付系统的基本框架

  在线支付系统的支付凭据是由终端产生，该支
付凭据包含了产生支付操作所需要的所有信息，支
付凭据的组包和加密都是由TEE内核或者运行于
TEE中的TA来完成的，至于采取何种方式则需要支
付厂商与终端设备厂商协商解决。一个简单的在线
支付系统的大致框架如图24-1所示。










       图24-1　在线支付框

  在线支付系统的服务器端与银行之间的数据交
互协议是由支付厂商与银行之间制定的，而支付系
统的服务器端与终端设备之间的数据交互协议则是
由支付服务提供商自行定义。一般情况下支付系统

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
      更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 738

提供商会为终端设备提供从应用层到系统层面的支
付应用程序、库文件和可执行文件，这些软件能够
搭建一个完整的支付请求交互通道。终端设备普遍
支持TEE，支付厂商可将数据的组包操作和加密操
作都放到TEE中来完成，这样可将交互数据的组包
和加密部分与REE侧的系统相互隔离。根据是否在
终端设备中预置了密钥在TEE中完成终端设备与支
付系统服务器端之间交互数据的组包和加密可大致
分为预置密钥的组包方式和未预置密钥的组包方
式。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 739

24.2　可信通信通道

  可信通信通道是指设备终端与支付服务器之间
的通信链路是安全可信的，即设备终端发出去的支
付相关数据只有支付服务器才能正确地解析。可信
通信通道的建立可以仿照SSL协议来进行建立，
SSL协议主要用于网络通信，通过设备终端与支付
服务器之间的握手通信来建立两者之间进行密文通
信使用的加密密钥。图24-2所示为SLL通信协议的
简图。










    图24-2 SSL通信协议简图

    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 740

  在确定可信通信通道之前，设备终端与服务器
端需要经过三次握手来协商通信时使用的加密密
钥。设备终端向服务器第一次发送握手请求时会生
成一个随机数A，服务器端会认证该请求的可信
性，如果认证通过，服务器会生成一个随机数B，
然后将该随机数发送给设备终端。设备终端获取到
来自服务器的返回数据之后会进行一系列的可信认
证，待认证通过之后会生成一个随机数C，并将该
随机数发送给服务器完成整个握手操作。然后客户
端和服务器端使用相同的算法结合上述三个随机数
生成两者之间进行数据通信的加密密钥。

  为防止中间人攻击，在终端设备和服务器建立
可信通信通道时，终端设备和服务器需要具有数据
的唯一性和可信鉴定机制。这一点可通过在设备生
产时提前将认证密钥预置到设备中或在应用程序安
装或注册时分发密钥到设备来实现。为确保终端设
备与服务器之间的相互隐私，这组密钥一般使用的
是非堆成算法密钥，其中私钥保存在终端设备中，
而公钥则由服务器来保存。

  在线支付程序安装或者注册时，支付服务器可
给设备下发一对RSA密钥的公钥，该公钥最终会被
保存到OP-TEE中。在建立可信通信信道时，终端
设备可用该公钥加密握手数据请求。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 741

24.3　数据交互协议

  数据交互协议是指终端设备与支付服务器之间
进行数据交互时双方发送的数据需按照一定的格式
进行组合。组合的数据需要包含数据的用途、内
容、发送方、数字签名，且以密文的形式进行传
输。在本章节提供的示例中，数据交互协议的内容
包括数据头部区域、数据区域电子签名区域。数据
头部区域和数据区域的内容在发送之前需要使用密
码学算法进行处理，以便数据在传输过程中都是以
密文的形式存在。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 742

   24.3.1　数据头部区域

       数据头部区域包含通信协议的版本信息、数据
   发送方、数据接收方以及预留区域，以便后续扩展
   使用。关于数据头部区域的数据格式定义如表24-1
   所示。

      表24-1　数据头部区域定义列表






  数据头部区域包含的版本信息可以进行扩展使
用，其可用于规定通信时使用的电子签名算法类
型。解析数据是获取到版本信息后就可以确定认证
数据唯一性时使用的算法配置信息。









    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 743

24.3.2　数据区域

  数据区域中包含的内容是设备终端与服务器之
间进行交互式传输的数据内容，关于数据区域中包
含了哪些数据内容则由支付服务提供商自行决定。
但该区域中一般都会包含该份数据的用途、数据长
度等信息。数据区域的数据格式定义如表24-2所
示。

     表24-2　数据区域定义列表






  数据区域中的数据是设备终端与服务器端需要
进行相关操作的依据，用于产生支付凭据、合法的
支付请求以及支付结果的反馈等。支付厂商可以根
据自身的实际需求定义该部分的内容。








    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 744

24.3.3　电子签名区域

  电子签名区域用于验证接收到的数据的完整性
和唯一性，一般使用RSA算法来实现，当然支付厂
商也可以根据实际的需求使用电子证书加RSA签名
的方式来实现。本章提供的示例代码中直接使用
RSA2048算法来实现，其内容定义如表24-3所示。

     表24-3　电子签名区域列表


  在建立可信通信通道过程中，第一次握手时不
会带电子签名，如果设备终端没有在生产时将RSA
公钥发布给支付厂商，则在第一次握手时会将设备
终端的一把RSA公钥发送给服务器端。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 745

24.3.4　交互数据包的格式

  一个完整数据包需要包含数据包头、数据区
域、电子签名区域。一般在完成通信握手操作之后
使用对称加密算法对数据包头和数据区域进行加
密。一份完整的数据包的组合方式如图24-3所示。










     图24-3　数据组包格式示意

  由于在数据通信过程中并不会在设备终端中固
定加密密钥。故在仿照SSL通信协议协商加密密钥
的过程中传输的数据一般使用非对称加密的方式对
握手操作时的数据进行加密处理。这样可以确保终
端设备与服务器端握手操作时数据的安全性。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 746

24.4　在线支付系统示例的实现

  在线支付系统示例仿照SSL协议，终端设备与
支付服务器采取三次握手的方式完成可信通信信道
的建立。在握手过程中终端设备和支付服务器会将
一把RSA公钥发送给彼此，RSA公钥用于加密握手
数据。每次握手操作的握手数据包中都会包含一个
随机数，待握手操作完成后，支付服务器和终端设
备会使用握手过程中的三个随机数使用PBKDF2算
法生成后期设备终端与支付服务器之间进行数据交
互时使用的AES加密密钥。本节将详细介绍示例中
各操作的实现。

  在第一次握手时会使用到RSA的公钥对数据包
进行加密。该密钥可通过在线下发的方式，在安装
或注册支付应用程序时下发给终端设备。第二次握
手时使用的RSA公钥即可在第一次握手请求时告知
服务器端，亦可在终端设备生产时提前将该RSA私
钥预置到设备中，同时将RSA公钥告知服务器。关
于设备终端的RSA密钥对可在使用时调用OP-TEE
的接口产生亦可提前生成好然后预置到设备中。






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 747

24.4.1　第一次握手请求

  在支付应用程序安装到终端设备或者用户登录
时，支付服务器会向终端设备下发一把RSA公钥。
为方便后续说明，将该RSA公钥称为
RSA_PUBLIC_SERVER。终端设备发起第一次握
手请求时，在TA中就会使用该公钥加密握手请求
数据，按照通信协议规定，第一次握手请求的明文
数据内容如图24-4所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 748

图24-4　第一次握手请求的明文数据内容示例





https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 749

  整个数据包按照256个字节进行对齐，组包后
的明文数据会使用RSA_PUBLIC_SERVER公钥进
行加密，并将密文数据返回给CA，然后将密文数
据通过网络发送支付服务器。数据的组包、RSA加
密模式、填充数据都在TA中完成，读者可根据实
际需求自行修改协议中的内容，可添加时间戳信
息、魔术数等身份标识数据，这些信息可被服务器
用于对数据合法性的验证。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 750

24.4.2　第二次握手数据的解析

  第一次握手请求时，设备终端会将一把RSA的
公钥RSA_PUBLIC_CLIENT打包到握手请求数据包
中，服务器接收到数据包后使用对应的RSA私钥解
密开数据包，然后解析获取到设备终端的RSA公
钥，该公钥会被用于加密第二次握手数据。

  第二次握手数据是由服务器端组包完成的。该
数据的明文内容如图24-5所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 751

    图24-5　第二次握手数据内容示意

  第二次握手数据明文组包完成后会使用
RSA_PUBLIC_CLIENT进行加密，最后使用服务器
的RSA私钥对密文数据进行RSA电子签名操作，第
二组数据包中的数据区域中会包含第二个随机数


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 752

B。终端设备接收到该数据后会调用CA接口，将数
据包发送给TA，然后TA按照协议内容对数据包进
行电子签名验证、数据解析、数据验证，最终获取
到第二个随机数B，并将该随机数保存到OP-TEE
中。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 753

24.4.3　第三次握手请求

第三次握手请求会将第三个随机数C发送给服
务器端，按照协议内容组包的第三次明文数据内容
如图24-6所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 754

图24-6　第三次握手请求数据示意
第三次握手请求使用设备终端的RSA私钥进行
签名，其中会包含第三个随机数C。明文数据会使
用RSA_PUBLIC_SERVER进行加密。待数据组包
完成之后，TA会使用获取和生成的三个随机数A、
B、C使用PBKDF2算法生成数据交互使用的AES密
钥，并将最终生成的AES密钥保存在OP-TEE中。
待此操作完成后，TA会将第三次握手请求数据包
返回给CA，CA以网络通信的方式将数据发送给服
务器端。

        待服务器端接收到第三次握手请求后，服务器
同样也会使用PBKDF2算法节后三个随机数生成
AES密钥并保存起来，用于后续数据交互时明文数
据的加密操作。到此终端设备与服务器端之间可信
通信信道已经建立。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 755

24.4.4　支付请求

  支付请求命令会生成一个通知支付服务器与银
行产生清算操作的支付凭据的数据包。该数据包使
用握手时生成的AES密钥进行加密，然后使用设备
终端的RSA私钥进行电子签名，以确保数据包的完
整性和唯一性。支付请求的数据包内容示意图如图
24-7所示。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 756

     图24-7　支付请求数据示意

  支付请求时设备终端发送给支付服务器的支付
凭据，在组包之前需要被发起支付请求的操作者进
行相关的身份验证，例如支付密码、指纹验证、短
信验证等方式。待身份验证通过后，CA会向OP-
TEE发送该命令，让TA生成合法的支付请求数据
包。明文支付请求数据会使用握手时生成的AES密
钥进行加密，服务器接收到该数据包后会对数据包


    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 757

进行电子签名验证、解密、解析、支付请求合法性
验证等操作。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 758

24.4.5　支付反馈

  支付请求完成之后，服务器端会向设备终端发
送支付反馈数据包，该数据包包含直接结果和其他
相关的信息，用于将最终的支付结果反馈给用户。
该数据包的内容示意图如图24-8所示。

  设备终端接收到支付反馈数据包后会通过调用
CA将该数据发送给TA，TA接收到数据后会对数据
包进行电子签名验证、AES解密、合法性验证，然
后解析出支付结果，并将最终的支付结果信息返回
给CA。支付应用可从CA的返回数据中获取支付结
果并显示给用户。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 759

图24-8　支付反馈数据示意










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 760

24.5　示例的集成

  终端设备与支付服务器端之间的交互数据是按
照事先约定的通信协议格式进行组包和发送的，为
提高数据的安全性、唯一性、完整性、可信性，将
数据的组包、加密、签名操作都放在TA中来实
现，REE侧只负责数据的接收和发送。整个系统在
TEE侧的实现如图24-9所示，本节将介绍如何将示
例代码集成到OP-TEE中。










    图24-9　在线支付系统框架示意






    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 761

24.5.1　示例代码的获取和集成

  本书提供了根据GP标准定义的接口，使用OP-
TEE实现的一个简单在线支付的示例TA和CA代
码，读者可使用如下指令从GitHub中获取代码：

 git clone https://GitHub.com/shuaifengyun/onLinePay.git

  下载完代码后就需要将该TA和CA集成到OP-
TEE中，需修改OP-TEE源代码build目录下的
qemu.mk（开发者板级对应的mk文件）和
common.mk文件。然后编译整体OP-TEE后就能使
用在线下发系统的功能。

  获取到示例代码之后，切换到如下build目录
下，然后使用git apply命令合入补丁文件后就可完
成将该示例集成到OP-TEE，合入补丁的操作步骤
如下：

  1）将示例代码中的
onLinePay_common_3.0.0.patch文件和
onLinePay_qemu_3.0.0.patch文件复制到build目录
中。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 762

  2）切换到build目录，使用如下命令合入补
丁：

git apply onLinePay_common_3.0.0.patch
git apply onLinePay_qemu_3.0.0.patch

  3）切换到optee_os目录，使用如下指令合入开
启OP-TEE的dump功能：

git apply lib_libutils_ext_trace.patch

  将补丁合入完成之后就可使用make-f qemu.mk
all编译整个工程，然后使用make-f qemu.mk run-
only来启动OP-TEE，在启动的正常世界状态的终端
执行相关的命令就能实现在线支付的握手请求、支
付请求、支付完成的相关操作。示例代码的运行效
果如图24-10所示。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 763

图24-10 save_key示例运行










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 764

24.5.2　板级编译文件的修改

                             将该示例的TA和CA添加到OP-TEE中需要修改
读者开发环境对应的mk文件。以使用QEMU方式运
行OP-TEE为例，则需要修改qemu.mk文件添加该示
例代码的编译目标，修改步骤如下：

1）添加onLinePay的编译目标：

############################################################################
# On Line Pay System
############################################################################
onLinePay: onLinePay-common
onLinePay-clean: onLinePay-clean-common

2）将onLinePay和onLinePay-clean添加到全局
的all和clean目标依赖关系中：

all: bios-qemu qemu soc-term optee-examples onLinePay
clean: bios-qemu-clean busybox-clean linux-clean optee-os-clean \
optee-client-clean qemu-clean soc-term-clean check-clean \
optee-examples-clean
optee-examples-clean onLinePay-clean

添加部分的主要作用是定义onLinePay目标并
建立该编译目标与all的依赖关系，在编译整个OP-
TEE工程时会被使用到。


https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 765

24.5.3　通用编译文件的修改

修改完板级编译的mk文件后，
                   还需修改
build/common.mk文件。修改的内容主要是将
onLinePay的编译目标集成到系统编译中，
    需要修
改的内容如下：

1）定义onLinePay路径变量：


ON_LINE_PAY_PATH    ?= $(ROOT)/onLinePay



2）添加onLinePay的目标依赖，修改filelist-tee-
common目标的依赖关系如下：


filelist-tee-common: optee-client xtest optee-examples onLinePay



3）增加TA和CA的common目标：


###############################################################################
# on line pay test case
###############################################################################
ON_LINE_PAY_COMMON_FLAGS ?= HOST_CROSS_COMPILE=$(CROSS_COMPILE_NS_USER)\
TA_CROSS_COMPILE=$(CROSS_COMPILE_S_USER) \
TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR) \
TEEC_EXPORT=$(OPTEE_CLIENT_EXPORT)
.PHONY: onLinePay-common
onLinePay-common: optee-os optee-client




https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 766

$(MAKE) -C $(ON_LINE_PAY_PATH) $(ON_LINE_PAY_COMMON_FLAGS)
ON_LINE_PAY_CLEAN_COMMON_FLAGS ?= TA_DEV_KIT_DIR=$(OPTEE_OS_TA_DEV_KIT_DIR)
.PHONY: onLinePay-clean-common
onLinePay-clean-common:
$(MAKE) -C $(ON_LINE_PAY_PATH) \
$(ON_LINE_PAY_CLEAN_COMMON_FLAGS) clean



4）添加clean操作的依赖关系：


optee-os-clean-common: xtest-clean optee-examples-clean onLinePay-clean



5）在filelist-tee-common中添加TA和CA镜像需
要被打包到文件系统中的操作：



@echo "#on line pay TA " >> $(fl)
@if [ -e $(ON_LINE_PAY_PATH)/host/onLinePay ]; then \
  echo "file /bin/onLinePay" \
  "$(ON_LINE_PAY_PATH)/host/onLinePay 755 0 0" >> $(fl); \
  echo "file /lib/optee_armtz/abb6f4b6-8e33-4ad2-9805-e64f2c7cc70c.ta" \
  "$(ON_LINE_PAY_PATH)/ta/abb6f4b6-8e33-4ad2-9805-e64f2c7cc70c.ta \
  444 0 0" >> $(fl); \
fi










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
  更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 767

24.5.4　编译运行

  修改完编译相关文件后，在build目录下执行
make指令编译整个OP-TEE工程。编译完成后，启
动系统就可以在REE侧终端使用相关的命令来触发
整个在线支付系统过程中需要的基本操作。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 768

24.5.5　示例支持的命令说明

  示例总共支持五个命令，更加详细的信息可参
阅示例代码中的README.md文件，其在CA侧的命
令说明如下：

  onLinePay hsone：让OP-TEE中的TA按照通信
协议的规定打包第一次握手请求的数据包，其中包
括第一个随机数和终端设备需要发送给服务器端的
RSA公钥内容。
  onLinePay hstwo：将服务器端发送的第二次握
手的数据发送到OP-TEE进行解密、验证并解析，
获取到服务器端发送给终端设备的第二个随机数。

  onLinePay hsthree：让OP-TEE中的TA按照通信
协议打包第三次握手请求的数据包，其中包含第三
个随机数，最后将上述三个随机数通过PBKDF2算
法进行融合生成终端设备与服务器端进行数据交互
时的AES密钥，从而完成可信通信通道的建立。

  onLinePay payreq：让OP-TEE中的TA按照通信
协议打包支付请求的数据包，其中包含了需要发送
给服务器端用于实现支付认证的相关信息。



    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 769

  onLinePay payover：将服务器端发送的支付操
作反馈数据包发送到OP-TEE中进行解密、验证并
解析，获取最终的支付结果。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 770

24.5.6　服务器端工具

  在示例代码包中有一个server_tools的目录，该
目录中存放的是在服务器端用于验证来自于OP-
TEE数据及生成下发数据包的工具，读者可使用该
工具进行数据的验证、下发数据的打包等，同时读
者也可根据自身具体的需求进行扩展。关于该工具
的使用可参阅该目录中的README.md。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 771

24.6　组包操作嵌入内核

       若支付厂商想提高支付系统与终端设备的强制
绑定，则可将打包操作完全嵌入到OP-TEE的内核
中，在TA调用系统调用接口的方式来完成数据包
的打包和解析操作，也即是芯片厂商需按照支付系
统的通信协议将相关操作嵌入到内容中，该种实现
方式的支付系统在OP-TEE中的框架图如图24-11所
示。










 图24-11　未预置密钥的组包方式示意



 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 772

  采取该种方式完成数据打包时就需要读者将打
包操作移植到OP-TEE中，可以在OP-TEE的内容中
建立一个虚拟的服务，然后通过服务的方式将操作
接口暴露到系统调用中，而最终打包操作时可看作
是一个虚拟的安全驱动，将操作接口暴露给虚拟服
务就可实现将操作嵌入到OP-TEE内容的开发。关
于具体的实现，读者可参考第22章中关于安全驱动
的开发部分。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 773

24.7　支付系统与生物特征的结合

  生物特征数据一般都会用于终端设备使用者身
份合法性的鉴定，如果在执行支付操作时嵌入使用
者生物特征的匹配检查就能实现支付系统与使用者
生物特征数据的结合。即在触发支付操作之前需要
使用者提供生物特征数据，例如指纹、虹膜、人脸
扫描等。只有当生物特征数据验证通过之后才能触
发支付操作，如果生物特征数据匹配失败则取消支
付操作。

  如要实现生物特征数据与支付系统的强制绑
定，可在开通支付系统之前要求用户录入生物特征
数据，并将该数据传递到服务器端，由服务器端来
完成使用者身份的论证，但该方式往往会牵扯到侵
犯用户隐私的问题，故当前一般将生物特征数据的
鉴定放在终端设备中来完成。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 774

24.8　小结

   本章介绍了TEE如何实现在线支付功能的安全
问题，根据终端设备是否预置密钥提供了使用OP-
TEE搭建安全支付功能的两个示例，读者可以根据
自己的实际需求修改相关的代码内容来实现自由的
系统，当然关于支付系统的解决方案也非一定的。
读者也可根据自己的实际设计实现不一样的在线支
付方案，但为确保终端设备的安全性，强烈建议将
密码学操作、组包操作、鉴权操作、数据保存等操
作都放在OP-TEE中完成，只将处理之后的数据返
回给REE侧的应用程序。这样可实现支付数据全程
都与REE侧相互隔离，即使REE侧的系统被破坏也
不会造成关键数据的泄密。










 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 775

第25章　TEE可信应用的使用领域

  随着互联网经济的飞速发展，移动设备用户的
数据安全性越来越重要，有些数据直接关系到用户
的经济利益。本章将简要介绍TEE方案的实际应用
场景，在实际使用过程中TEE能为数据提供硬件级
别的保护。由于篇幅有限，对于实际使用的技术细
节就不作详细的介绍。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 776

25.1　在线支付

                                              国内手机的在线支付功能越来越普遍，如何保
证在线支付过程中数据的安全性和支付密钥的安全
越来越重要，尤其是在使用指纹识别进行支付时，
谷歌在Android 7.0之后已强制要求手机设备厂商需
要将用户的指纹数据保存在TEE中，国内的在线支
付系统主要是支付宝和微信支付，在使用指纹支付
时都使用TEE来保护相关数据的安全。
                                             在线支付的验证过程可放到TEE中运行，但由
于种种原因支付宝和微信支付的支付验证过程都使
用软件方案来实现，而并没有运行于TEE中，但是
验证过程中使用的关键数据大多是被保存在TEE中
的，且这些数据的保存也是经TEE加密保存的。

                                              每一台手机在工厂生产过程中都会使用微信提
供的工具生成一对RSA密钥，公钥将会被上传到微
信的服务器中，生成密钥的操作是由TEE来完成，
而且在使用微信时，相关数据的组包、签名都由
TEE来完成。微信的在线支付功能在使用时会使用
到系统中的keystore模块、keymaster模块、TEE驱
动、运行于TEE中的在线支付TA、指纹TA模块。
整个过程中所有数据的加密、签名以及生成密钥的
过程都是在TEE环境中完成的，这也就能保证在线

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
 更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 777

支付操作的安全。










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 778

25.2　数字版权保护

                                              数字版权保护（DRM）是用于对视频资源进
行版权保护的解决方案，目前DRM的方案有很多
种，例如ChinaDRM、Marlin、WideWine等。TEE
用于对视频码流版权的验证和视频资源的解密，并
提供安全的播放环境（Secure Video Path，SVP）。
当设备需要播放受DRM保护的视频资源时，首先需
要对视频码流进行版权验证，待视屏码流被验证通
过后，系统再从服务器端获取到加密的视频资源，
然后将密文的视频资源交由TEE使用密钥进行解
密，解密后的明文视频资源将会被保存到安全内存
中，当多媒体单元要播放该视频资源时，多媒体单
元可以从SVP中获取到解码后的视频数据。

                                           ChinaDRM是我国自有的DRM方案[1]，当前全
套方案已应用在腾讯视频源平台，相信以后肯定会
接入越来越多的视频源平台，ChinaDRM的框架如
图25-1所示。
 在ChinaDRM的方案中，TEE主要用于验证和
解密视屏资源并提供安全内存的功能。TEE中会运
行一个ChinaDRM的TA，该TA将完成对视频资源
的版权认证和解密操作，解密使用的算法策略则由
ChinaDRM厂商以库文件的方式提供给应用厂商，

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
     更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 779

应用厂商将该算法策略集成到TA中。
[1] ChinaDRM网站：
http://www.unitend.com/product?cid=16。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 780

25.3　身份验证

                                              对设备使用者的身份验证主要使用密码和生物
特征数据来进行判定，最终的验证结果是由转换后
的数据与保存数据的对比结果是否一致来决定。根
据生物特征数据进行判定是目前最安全的方式，生
物传感器主要用于采集用户的生物特征数据，例如
指纹数据和虹膜数据。谷歌在Android 7.0之后已强
制要求设备厂商使用TEE来保存用户的生物特征数
据。对于系统软件中的指纹识别模块，谷歌在
Android系统已提供了统一的标准接口。设备厂商
只需将指纹传感器配置成安全设备，并在TEE中添
加对应的TA就可实现使用TEE对指纹数据进行安全
保护。

  由于指纹传感器被设置成安全设备，故只有
TEE才可以获取到指纹识别传感器的数据。指纹数
据的采集操作是由运行于TEE中的TA来完成的，该
TA会调用指纹识别传感器厂商提供的第三方库来
完成数据的采集。将指纹识别对应的CA接口与
Android在REE侧提供的标准接口进行对接就能实现
指纹识别相关的认证操作，包括指纹解锁、指纹支
付等功能。这些功能的实现需要TEE厂商、支付平
台、芯片厂商以及在线支付厂商四方共同开发完
成。

 https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
   更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 781

25.4　其他领域

  TEE的使用也越来越普及，大疆的无人机已使
用TEE来保护飞控系统中的关键数据以及航拍数据
的安全。互联网电视领域也在TEE中集成DRM的功
能用于保护视频资源的安全，智能电视厂商亦可使
用TEE来搭建自有的会员鉴权系统，使关键的会员
鉴权算法运行于TEE中，而鉴权时使用的鉴权密钥
会被TEE保护以确保关键信息的安全。在无人驾驶
领域，车载芯片也集成了TEE方案，用于保护系统
关键数据、系统控制单元以及网络数据传输的安
全。










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 782

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 783

图25-1 ChinaDRM框架










https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 784

        术语表

  本书使用了各种专业的术语，为了方便读者理
解，下表列出了本书涉及的相关缩略语：










    https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
    更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 785

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Page 786

https://homeofpdf.com https://homeofpdf.com https://homeofpdf.com
更多电子书资料请搜索「书行万里」：http://www.gpdf.net

## Related pages

- 

## Source

- Local path: `[[books/手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解.pdf]]`
