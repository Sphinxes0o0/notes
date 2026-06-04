---
type: source
source-type: slide
title: "王骁_端侧大模型部署：存储系统面临的挑战和优化实践"
path: slides/王骁_端侧大模型部署：存储系统面临的挑战和优化实践.pdf
source-md5: efb9c834a1f0f65d0451cb9f8a5291f5
size: 6445 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 王骁_端侧大模型部署：存储系统面临的挑战和优化实践

> Ingested from `slides/王骁_端侧大模型部署：存储系统面临的挑战和优化实践.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.29 MB.

## Page 1

_(no text content on this page)_

## Page 2

_(no text content on this page)_

## Page 3

_(no text content on this page)_

## Page 4

_(no text content on this page)_

## Page 5

_(no text content on this page)_

## Page 6

端侧大模型部署：存储系统面临的挑
 战和优化实践

 王骁 vivo存储系统专家

## Page 7

目 录 CONTENTS
    01：端侧大模型发展
    02：AIOS架构
    03：存储系统挑战和优化实践
    04：未来展望

## Page 8

_(no text content on this page)_

## Page 9

智能命名&总结    小V电话助手
    Blue
小v记忆       LM  小V语音对话
    蓝心大模型
    小V写作       蓝心小V


离线消除    定制美颜

## Page 10

AI普惠全球vivo手机用户

## Page 11

_(no text content on this page)_

## Page 12

_(no text content on this page)_

## Page 13

   蓝 心 个 人 智 能 框 架

实时感知  个人记忆  自主规划  可控执行

## Page 14

系统架构

                      业务&交互
    语音        实体按键              双指长按          ……
        统
        系统应用                      三方应用
                      AI Agent框架
    意图理解              记忆管理                任务规划     全
                                                   链
                                                   路
                      模型引擎                         个
                                                   人
    模型管理              端云协同                高效推理     隐
                                                   私
                                                   数
                      内核                           据
                              文件系统                 安
    资源调度        内存管理          Block IO    度量       全

                      硬件
    CPU/GPU/NPU    DRAM/PIM   UFS/ZUFS    sensors


                                                   14

## Page 15

_(no text content on this page)_

## Page 16

挑战1：模型加载耗时长，3B模型接近2G文件加载耗时达10s




 dmabuf A    dmabuf B    输入输出buf

 模型文件A              模型文件B

     模型文件A

                    模型文件B




 10.147s 完成加载

## Page 17

mmap+memcy访问大模型文件，因为文件不在pagecache，
需要通过缺页来完成每个page的读取

## Page 18

  read + 并行，从10s下降到2s，仍然不满足1s需求





  dmabuf A    dmabuf B    输入输出buf









读模型文件
  A



  读模型文件B



  2s内全部读完

## Page 19

 挑战2：内存申请耗时波动大（ 1~4s ），占用3.5GB+

可用内存在4GB情况下，申请2GB dmabuf耗时约1.94S；可用内存在2GB情况下，申请2GB dmabuf耗时约4S+


             申请2GB dmabuf内存耗时

  memfree/MB available/GB 耗时/S    申请速率GB/S
  300        4GB          1.94     1.03
  300        3GB          2.11     0.99
  300        2GB          4.14    0.518

## Page 20

   挑战3：随机数据占比高，影响推理速度

   PocketPal 使用AI Model：Phi4-O2-K
   推理阶段加载耗时超过1.4s，总数据量500MB，4K占比23.93%



            >=64k,    4k,
            12.48%  23.93%

   64k,…        8k,
                6.72%
                     16k,
 32k,                9.65%
19.35%

## Page 21

挑战4：带宽仍有30GB/s+的差距，存储功耗占比超过50%

## Page 22

  存储系统原生方案机制和不足

原生的dma-buf内存的文件读写，数据要先从存储器读取到cache缓存，再从缓存拷贝到用户实际内存空间，需要
两次数据copy和两份内存占用，读写大文件效率低




  两份内存占用，内存占用3GB+
  一次CPU拷贝，算力消耗

## Page 23

 探索1：DMA-BUF介绍和用户态无法支持 Direct IO 的原因

DMA-BUF这个框架解决CPU和各种不同外设驱
动之间buffer共享的问题。但是DMA-BUF的内
存PFNMAP特性限制导致Direct IO无法使用。

      VM_PFNMAP










  23

## Page 24

探索1： DMA-BUF 机制缺陷： DMA-BUF申请后才能发起 IO

## Page 25

    探索1：vivo的解决方案，模型加载速度提升50%+

•   在内核态读取文件,struct page可管理
•   读取完再export dma-buf,避免并发竞争
•   内存申请和文件读取在生产-消费者模式下
    并行,提高效率

## Page 26

探索1： udmabuf 方案










26

## Page 27

探索1：vivo 对 udmabuf 的提交

• pre-fault加速mmap page的获取
• 修复udmabuf size超过2G创建失败问题（buddy
 alloc导致）
• vmap等适配HVO，避免用page struct，而是使用pfn
• 对于create过程的代码简化和性能提升
• google后续将在安卓上开启udmabuf





 提交链接：
 https://lore.kernel.org/all/20240918025238.2957823-1-link@vivo.com/
                                                                    27

## Page 28

探索2： EROFS文件系统对 direct I/O 的支持

为什么要求数据块在磁盘上对齐？IO对齐要求源自存储设备：如 UFS存储设备最小传输单位是4KB。

## Page 29

     探索2： EROFS文件系统怎么支持 Direct I/O ？

l  EROFS：block大小对齐不是问题
  Ø  当不是block大小对齐时，EROFS实现先读取到临时page
     中，再从临时page解压到user buffer中
l  buffer 地址和buffer大小：需要page大小对齐
   Ø EROFS当前是以page为单位进行读取的
l  性能思考
  Ø 顺序读大部分情况下是就地I/O（inplace I/O）和就地解
     压（inplace decompression），不需要临时page

## Page 30

  探索2： Buffer I/O和Direct I/O的folio读取对比

l buffer I/O读取时，vfs读取过程中调用 readahead / read_folio 读取folio后，会等待各个folio的完成，所
 以 readahead / read_folio 对filio的完成处理比较简单（直接unlock folio即可）；
l direct I/O读取相比buffer I/O，folio读取的处理更复杂：
  Ø 每笔direct I/O请求需要管理各个folio并等其完成，一般会增加结构体进行管理——影响并发
  Ø 并发增加考虑：direct I/O和buffer I/O并发、多线程direct I/O的并发

## Page 31

探索2： EROFS Direct I/O并发设计演进










 https://lore.kernel.org/linux-erofs/20250922124304.489419-1-guochunhai@vivo.com/T/#u

## Page 32

探索2：结果：模型加载耗时小于1s，性能提升54%


      buffer I/O    direct I/O    提升比例
        (MiB/s)       (MiB/s)
 低内存场景   2350          3633       54%
 普通场景    2629          3648       38%
 降低比例    10.6%         0.4%

## Page 33

  探索3： Uncached buffer IO机制：阅后即焚

Direct I/O 要求严格的内存对齐和大小限制，对开
发者要求较高，限制了其使用范围。
为了能够使用 Buffer I/O 的便利性，同时又让
Buffer I/O 不占用 page cache，Jens Axboe 提出
了 Uncached buffered I/O。

## Page 34

探索3： Uncached buffer io 读文件实现原理










34

## Page 35

探索3： Uncached buffer I/O 读场景 kswapd 负载降为 0

## Page 36

探索3： Uncached buffer I/O 读速度波动由 150MB/s 降到
50MB/s

## Page 37

 探索3： Uncached buffer IO的思考

Uncached buffer I/O 写为了能尽快释放 page cache 占用内存，其会在数据写入 page cache 后主动触发
一次回写，这种方法类似于 sync 操作，进而会导致写性能降低。
但是在 Jens Axboe 的测试环境，即磁盘性能非常好的环境下 UBIO 写性能会有提升，但是在绝大部分场景
下磁盘的性能是低于内存的，故 UBIO 写会导致写性能降低。
是否有更优方案来解决 UBIO 写性能降低的问题？




    f2fs 适配 Uncached buffer IO 读、写提交：
    https://lore.kernel.org/all/20250828121131.3694154-1-hanqi@vivo.com/
    Jens Axboe 环境写性能：
    https://git.kernel.org/pub/scm/linux/kernel/git/akpm/mm.git/commit/?h=mmnew&id=
    d47c670061b5f9481ce494cd6c45078be301620e

## Page 38

   探索4：基于Zone的分类存储，提升随机读性能30%

 1、文件系统识别AI个人数据，基于ZonedUFS的分类数据存储，将随机性能转换为顺序性能
 2、基于zone映射，nand数据全部缓存命中，对于部分随机数据也大幅提升读性能

 文件系统
数据分类管理

          ZonedUFS
          FTL                  基于zone映射
   坏块管理   zone 映射     错误处理     随机读性能提升30%
   zone1  zone2  zone3  AI     AI数据集中存储在特定区域，
                               提升数据检索和加载速率

## Page 39

    探索5：并行内存回收，提升回收速度15%


    Kswapd单线程，匿名页和文件页串行回收，速度慢

    kswapd




        4K    4K  4K  4K
    Inactive  Apage Apage Apage Apage Apage
    Anon LRU


4K 4K 4K 4K
    Inactive Fpage
    File LRU Fpage Fpage Fpage Fpage

## Page 40

_(no text content on this page)_

## Page 41

   以存算一体为代表新硬件将深刻影响存储系统变革，突破
   的关键在存储的高效管理和PIM/GPU/NPU的有序协同





        3D DRAM + NPU  LPDDR PIM (@LP6)  LPW
    方案     外挂加速芯片     主存(带计算能力)     定制存储芯片(无计
        算功能)
主要特点 协处理器方式，降 接口不变，存储带计算；可 新接口，数据带宽增
           低Soc负载        以降低CPU/NPU的负载  加

    带宽     1TB/s       500G/s        200GB/s

    标准化    当前无相关标准     26年             26年
    成本        高                低         中
    成熟度      26年       27年             27年

## Page 42

Thank You

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/王骁_端侧大模型部署：存储系统面临的挑战和优化实践.pdf]]`
