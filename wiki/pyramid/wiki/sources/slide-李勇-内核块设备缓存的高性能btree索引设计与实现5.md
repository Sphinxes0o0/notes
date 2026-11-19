---
type: source
source-type: slide
title: "李勇_内核块设备缓存的高性能Btree索引设计与实现5"
path: slides/李勇_内核块设备缓存的高性能Btree索引设计与实现5.pdf
source-md5: bf44582318d653342e99836ae12aefaa
size: 4672 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 李勇_内核块设备缓存的高性能Btree索引设计与实现5

> Ingested from `slides/李勇_内核块设备缓存的高性能Btree索引设计与实现5.pdf` via `lit parse` on 2026-06-04.
> Source file: 4.56 MB.

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

    Linux内核块设备缓存的
    高性能Btree索引设计与实现






Coly Li <colyli@fnnas .com>
        Bcache子系统maintainer
                 飞牛NAS内核架构师
                2025年12月13日

## Page 7

我是谁










 Linux内核bcache维护者，飞牛NAS内核架构师。
 曾作为第一位工程师加入并创建了淘宝Linux内核组（现阿里云Linux操作系统团队前身）

## Page 8

 以Bcache子系统为例

Bcache是Linux内核中的块设备缓存系统，可以在使用慢速机械硬盘存储数据的同时，将热数据缓
存在高速固态硬盘中，能够明显提高随机数据的访问性能。

      卸载

 Bcache        后端      可用的缓存模式
 虚拟设备        SSD        块设备     - 回写
      挂载                        - 写透
                                - 写绕过
                                - 不缓存
缓存系统中首先要有一个方法来确定数据对象是否已经被缓存。Linux内核中，目前性能最好的是
Bcache子系统使用的基于LSM(Log-Structured Merge-Tree)改进的Btree索引实现。

## Page 9

 Bcache对LSM-Tree的改进

Bcache对LSM-Tree的改进，主要考虑的场景是，
1，为了优化IO效率，单节点中索引key的数量大（超过1万个是常见的）
2，充分利用到CPU cacheline的性能特性

需要应对的挑战有，
1，对于Btree节点中的key的检索，不能用传统的线性查找。
2，要考虑到新key的插入，过期key的失效。
3，构建一个平衡二叉树（进行二分查找）并不总是能够成功的。
4，二分查找在内存中的前后跳跃对于CPU缓存并不友好。

接下来会介绍Bcache是如何组织了一个在存储和索引两方面都高效的Btree，来进行缓存数据查找。

## Page 10

 索引key的数据机构 bkey

Bcache定的key数据结构定义在drivers/md/bcache/bcache_ondisk.h中
                                           1）缓存副本数量（固定为单副本）
23 struct bkey {                           2）数据校验和标志位
24       __u64      high;                  3）数据是否为脏
25       __u64      low;                   4）数据大小
26       __u64      ptr[];   被缓存数据块对应在后端   5）后端磁盘设备编号
27 };                        （磁盘）设备上的LBA

                             被缓存数据块在高速缓存设备（固态硬盘）
                             上的LBA（ptr[0])和数据块校验和(ptr[n])
struct bkey数据结构直接存储在高速缓存设备的元数据bucket中，同时直接被读取到内存中建立
Btree节点进行索引。在Btree中用读IO请求的LBA检索bkey->low，来确定数据是否被缓存。
如果被缓存则根据ptr[0]指示的LBA从高速缓存设备上将已缓存数据读出返回给上层。

## Page 11

 写时复制的分配策略

Bcache中分配数据和元数据的基本单位都是bucket，通常大小为128KB – 1MB。
Btree节点在固态硬盘上和在内存中都是占用一个bucket的大小。

• 对于数据：新的缓存数据被追加写入到一个bucket中，直到这个bucket被写满再分配新的。
• 对于Btree节点：空间也是追加式的分配，除非该节点key数量过多（超过2/3桶空间）要被分裂。

当上层文件系统对某个已缓存的数据进行修改时，Bcache不会修改已经缓存的旧数据块，而是将新
的数据副本追加写入到某一个数据bucket中；同样会产生新的bkey并插入到对应btree节点的
unwritten bset中。

## Page 12

Btree节点的样子

    struct btree_node

    头部

    空闲空间


Bset头部

    struct bkey
Bcache的数据分配以bucket为单位，通常大小为128KB – 1MB。这也是一个Btree节点的大小。
一个Btree节点中包括多个Bset，一个Bset中包含多个Bkey。
这些数据结构以相同的格式既保存在存储介质上，也读取到内存中直接使用。

## Page 13

 一个Bset的样子

     struct bset


    头部

•   在一个Bset中的所有的Bkey都是严格增序。
•   内存中的Bset分为两类：written和unwritten
•   一旦某一个Bset被刷新到了高速块设备上，他就是written bset。
•   Bkey的插入和删除操作，只能在unwritten的bset上进行。

当一个bset很大时，常用的二分查找就会变慢。因此bcache为每一个bset创建了一个辅助查找树来
加速bset中特定key的查找。在Linux内核中这是Bcache的小创新，稍后会着重介绍。

## Page 14

当Btree节点中有多个Bset时
     unwritten bset

     头部

     空闲空间
     written bset

 头部

多个bset中可能会含有相同缓存数据的bkey，由于新的插入删除操作只能在最后的unwritten bset
中进行，因此后面（内存地址更大）的key总是优先于前面（内存地址更小）的key。这是处理被缓
存数据区域有重叠时的判定原则。
在整个Btree节点被从内存中回收前，Written bset也会一直保存在内存中。

## Page 15

    当Btree节点中有多个Bset时
    （续）
       written bset 0    written    bset  unwritten bset 0
        bset 1        头部

       written bset 0    written    written bset 0    空闲空间
        bset 1

  新的合并排序后的
written bset
  同一个btree节点中，当多个bkey之间存在重叠时，最后插入的bkey总是优先级最高的。

  对每一个Btree节点，最多在内存里有MAX_BSETS(3)个bset。如果正要被写入到固态硬盘中的bset
  已经达到MAX_BSETS个了，那么就先将内存中所有的三个bset先进行合并排序（最后插入的优先级
  最高），然后再将合并后的bset写入到固态硬盘上。

  然后内存里这个btree节点就只有一个written bset，当有新的key需要插入时就创建新的unwritten
  bset。

## Page 16

 Btree节点中的搜索

当要搜索一个bkey时，会从Btree的根节点搜索到某一个Btree节点。
Bcache的Btree只有一层中间节点，所以很快就会搜索到某一个叶子节点上。
当在一个叶子结点上检索到多个符合的bkey时，最后插入（内存地址最高）的那个胜出。


当Btree节点的Bset从固态硬盘读入到内存中时，同时会为它创建一个检索辅助树。
• 对于written set，这是一个二分查找树（节点结构精妙特殊）。
• 对于unwritten set，这就是一个简单的线性顺序表。

这个检索辅助树可以让Btree查找的速度大大提高，后面的内容会介绍bcache是如何做到的。

## Page 17

Written bset的二分辅助查找树

   二分辅助查找树的基本想法是
   • 一个bset中的多个bkey按照cache line的尺寸分组
   • 每个cache line组有一个起始bkey
   • 用每个cache line的起始bkey构造节点，来建立一个索引二叉树






    这个二分辅助查找树的优势是：
    •   查找过程是始终向前访问内存，因此可以充分发挥CPU
        cache的预取性能。
    •   每一个key代表了一个cache line的范围，可以将每一个节
        点迭代中覆盖的key的数量扩大8到16倍。

    特点是二分辅助查找树的节点结构和查找方法需要精妙的特
    殊设计。

## Page 18

   二分辅助查找树中的浮点格式key
二分辅助查找树中的key不是原先的bkey结构，而是转换成浮点数的格式（和浮点运算没有关系）：
•   这个key只是用来在二分辅助查找树中检索某一个cache line范围。
•   用浮点数格式可以将它压缩到4个字节，这样CPU cache里可以容纳更多，进行查找时访存操作
    就更少。
•   用浮点格式来进行key的比对，比用bkey 结构比对更快。

        244 struct bkey_float {
        245   unsigned int     exponent:BKEY_EXPONENT_BITS;
        246   unsigned int     m:BKEY_MID_BITS;
        247   unsigned int     mantissa:BKEY_MANTISSA_BITS;
        248 } __packed;

## Page 19

 二分辅助查找树中的浮点格式key （续1）

 由于是以cache line为范围查找，所以浮点格式key只要能区分不同的cache line即可

二分辅助查找树节点数据结构

struct bkey_float {
unsigned int       exponent:BKEY_EXPONENT_BITS;    边界
unsigned int       m:BKEY_MID_BITS;
unsigned int       mantissa:BKEY_MANTISSA_BITS;
 } __packed;

该数据结构被用来表示能够区分2个
相邻cache line的边界或者划分。

起始bkey在cacheline里的偏移量
（以8字节为单位,，这里是1）                                      前一个cache line中末尾bkey
 边界位置
     + 1 * 8 bytes                                   后一个cache line的起始bkey

## Page 20

 二分辅助查找树中的浮点格式key （续2）
 通过bkey来构造bkey_float：精读只要能区分开两个相邻的cache line位置即可。






 这些bkey的LBA的高位都相同



                                                  前一个cache line的末尾bkey

 末尾和起始key的内存地址的第一个                                后一个cache line的起始bkey
 不同的bit出现在第23位上      exponent: 23 （7位变量）
这么初始化一个bkey_float:   m: cacheline偏移量（这里是1）  用来表示这个相邻cache line的边界就足够了！
                     mantissa: 位24-64内容的低22位

## Page 21

二分辅助查找树中的浮点格式key （续3）

只要用构造的mantisa值在二分辅助查找树中进行查找即可。

例如把搜索的值s和上一页该二分辅助查找树中的这个节点（表示cache line边界）f进行比较。

        exponent: 23                        fbloat_mantissa(k, f)的运算本质就是根据上一页的计算，
f[n]    m: cacheline偏移量（这里是n）               返回mantissa对应的mantissa数值。
        mantissa: 位24-64的内容（低22位）

bset_search_tree()函数中的复杂行为的极简操作就是：

if (f->mantissa >= bfloat_mantissa(s, f))   则在cache line n中进行查找
else                                        则在cache line n-1中进行查找

如果f[n]是正好搜索命中的二分辅助查找树的节点，那接下来就可以到对应的cache line中进行检索。

## Page 22

   二分辅助查找树中的浮点格式key （续4）

当从二分辅助查找树中找到一个节点后，
•   该节点对应的cahce line范围也就可以通过f节点中的成员m决定（表示是当前bset中的第几
    个）。
•   然后在这个cache line内部直接做线性查找是最快的。
•   如果在这个cache line中找到匹配的bkey，那就是cache命中。
•   否则就是没有命中，需要从后端低速磁盘读取原始数据。










 在caheline范围内线性搜索
 速度比二分搜索更快

## Page 23

  write bset的搜索

• 因为所有的bkey插入删除操作都只能在write bset中进行，因此它的更新会很频繁。
• 这种情况下维护一个辅助搜索的二叉树性能代价是非常高的。
• 幸运的是write bset的尺寸通常都很小，因此直接用一个线性查找表来代替二分辅助查找树即可。

• 线性查找表的元素还是浮点数结构，只是按照线性表形式存储。
• 如果在线性查找表中匹配到对应的节点，仍然找到对应的cache line然后进行线性查找。

代价：每个内存中的Btree节点增加大约1%的额外内存。
收益：将bkey搜索的范围缩减为原先规模的1/8到1/16。

## Page 24

  Bcache的高性能Btree索引总结

Bkey的检索
• 已经在前面说明演示了。

Bkey的插入
• 插入到write bset的适当位置，保持被缓存数据LBA的严格增序。

Bkey删除
如果在write bset中：直接删除并更新bset。
如果在written bset中：在write bset中插入一个表示被缓存数据大小为0的bkey。

Bcache的日志机制会提供快速和异步的脏bkey刷新（这是另外一个复杂的故事）。

## Page 25

问答交流环节

## Page 26

THANKS

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/李勇_内核块设备缓存的高性能Btree索引设计与实现5.pdf]]`
