---
type: entity
tags: [cpp, stl, iterators]
created: 2026-05-21
sources: [sources/pdf-cpp-effective-stl]
---

# STL Iterators

## 定义

迭代器是 STL 中访问容器元素的抽象机制，模拟指针的行为，提供了一种统一的方式遍历不同容器类型的数据。

## 关键要点

### 迭代器类别

| 类别 | 能力 | 示例 |
|------|------|------|
| Input Iterator | 读，单向前进 | istream_iterator |
| Output Iterator | 写，单向前进 | ostream_iterator |
| Forward Iterator | 读写，前进多次 | forward_list |
| Bidirectional Iterator | 读写，双向移动 | list, set, map |
| Random Access Iterator | 任意跳转 | vector, string, deque |
| Contiguous Iterator (C++17) | 相邻内存 | vector, string, array |

### 迭代器适配器

- **reverse_iterator** — 逆向遍历，base() 转换为正向
- **insert iterator**: `back_inserter`, `front_inserter`, `inserter`
- **stream iterator**: `istream_iterator`, `ostream_iterator`
- **move iterator** (C++11) — 移动而非复制

### istreambuf_iterator vs streambuf_iterator

```cpp
// istreambuf_iterator<char> 跳过流缓冲区的格式化层
istreambuf_iterator<char> i(cin), end;
string s(i, end);  // 直接读取字符，不跳过空白

// istream_iterator<char> 使用流格式化
istream_iterator<char> i(cin), end;
string s(i, end);  // 跳过空白字符
```

### 迭代器失效

**vector**: 插入导致所有迭代器失效；删除导致被删点之后的迭代器失效
**deque**: 插入中间导致所有迭代器失效；首尾操作不影响其他迭代器
**list/set/map**: 只有被删除元素的迭代器失效
**string**: 同 vector

### 迭代器算数

```cpp
advance(it, n);          // 前进 n 步（对 Bidirectional 需注意方向）
distance(it1, it2);     // 两迭代器距离（需同容器）
iter_swap(it1, it2);    // 交换两个迭代器指向的值
```

## Effective STL 要点 (Items 11-15)

- Item 11: 理解 selectone vs selectmany
- Item 12: 当心 64 位系统的 iterator 语义
- Item 13: 用 iterator base 代替 const_iterator
- Item 14: 用 reverse_iterator 的 base 构造
- Item 15: 用 istreambuf_iterator 代替字符输入算法

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — 容器提供迭代器接口
- [[entities/cpp/cpp-stl-algorithms]] — 算法通过迭代器操作
- [[entities/cpp/cpp-stl-functors]] — 迭代器常与函数对象配合
- [[entities/cpp/cpp-stl-string]] — string 容器支持迭代器
