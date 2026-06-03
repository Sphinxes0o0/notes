# 布隆过滤器 (Bloom Filter)

## 概述

布隆过滤器是一种空间效率很高的随机数据结构，利用位数组简洁地表示集合，可判断元素是否属于该集合。

**核心特点：** 高效但存在假阳性（false positive），不适合"零错误"应用场合。

## 结构

- **初始化：** 位数组每一位都是0
- **插入：** 使用k个哈希函数对值x散列，取余后置对应位为1
- **查询：** 同样使用k个哈希函数，仅当所有位均为1时表示"可能存在"

## 数学结论

参数说明：
- **k** - 哈希函数个数
- **m** - 位数组容量
- **n** - 插入数据数量

关键公式：
1. 最优准确率：**k = ln2 × (m/n)**
2. 错误率不超过ε时：**m ≥ 1.44 × (m/n)**

## 实现（goleveldb）

```go
type bloomFilter int

func NewBloomFilter(bitsPerKey int) Filter {
    return bloomFilter(bitsPerKey)
}
```

k值计算（0.69 ≈ ln(2)）：
```go
k := uint8(f * 69 / 100)
```

核心逻辑使用**double hashing**技术生成哈希序列。

## 参考文献

- http://blog.csdn.net/jiaomeng/article/details/1495500
- https://en.wikipedia.org/wiki/Double_hashing

## 图片

- ![bloom1](https://leveldb-handbook.readthedocs.io/zh/latest/_images/bloom1.jpg)
- ![bloom2](https://leveldb-handbook.readthedocs.io/zh/latest/_images/bloom2.jpg)
- ![bloom3](https://leveldb-handbook.readthedocs.io/zh/latest/_images/bloom3.jpg)
