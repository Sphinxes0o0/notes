---
type: source
source-type: pdf-book
title: STL源码剖析
author: 侯捷
date: 2002
size: large
path: raw/PDFs/books/STL源码剖析简体中文完整版(清晰扫描带目录).pdf
pages: 437
summary: 侯捷 STL 源码剖析：SGI STL 5（GCC 2.95.3）完整注释版，逐行解析 STL六大组件（容器/迭代器/算法/仿函数/适配器/配置器）的底层实现，含 GCC STL 源码全文。
created: 2002
tags: []
---
# STL源码剖析

## Metadata
- **Author:** 侯捷
- **Pages:** 437（含完整 GCC STL 源码）
- **Topic:** C++ Standard Library implementation
- **Edition:** 简体中文完整版（带目录）
- **STL 版本:** SGI STL 5 (GCC 2.95.3)

## Core Content

侯捷老师经典著作，以 SGI STL 5 为蓝本，逐组件、逐行解析 STL 六大组件的底层实现。书中附完整 GCC STL 源码（437页），是理解标准库内部机制的权威参考。

### 1. 空间配置器 (Allocator)

**两级配置器 (Default Allocator):**
- 第一级 (`__malloc_alloc_template`): 直接用 `malloc()`/`free()`，处理大块内存；含 oom_malloc 处理机制
- 第二级 (`__default_alloc_template`): 内存池 (Memory Pool) 实现
  - Free-list 数组（16个桶，8字节对齐）：128B/256B/512B/1KB/2KB/4KB/8KB/16KB
  - 区块切分：从内存池索取 chunk，满足后填充 free-list
  - 区块回收：归还 free-list，避免碎片
- 嵌入式指针 (Embedded Pointers)：在空闲区块中复用存储 next 指针，零额外开销
- 线程安全：__default_alloc_template 含 static 锁（多线程考虑）

**配置/释放流程：**
- `allocate()` → 检查 size > 128B？走第一级 / 走第二级 free-list
- `deallocate()` → 区块回归 free-list（不归还系统）
- 重新填充：free-list 为空 → chunkalloc() 从堆索取 2×n 个区块

### 2. 迭代器 (Iterator) 与 Trait 技法

**Iterator Traits:**
- 萃取迭代器型别：value_type、difference_type、pointer、reference、iterator_category
- `__type_traits`（SGI 扩展）：trivial constructor/destructor/copy assignment

**迭代器实现：**
- `__iterator_traits.h`: 将迭代器型别"向后委托"给容器的 iterator
- `advance()` / `distance()` 重载实现（random-access / bidirectional / forward / input / output）
- 迭代器配接：`reverse_iterator`、`istream_iterator`、`ostream_iterator`

**Iterator Adapters:**
- `reverse_iterator`: base() 返回 ++current，current = base()-1
- `insert_iterator` / `front_insert_iterator` / `back_insert_iterator`
- `ostream_iterator` / `istream_iterator`

### 3. 序列式容器 (Sequence Containers)

**Vector:**
- 三指针结构：`start` / `finish` / `end_of_storage`
- `insert_aux()`: 中间插入触发重新配置（2×容量）；尾部插入 amortized O(1)
- `erase()`: 后续元素前移，不缩减容量
- 与 string 共用 `vector<bool>` 特化（含 proxy class）

**List:**
- 环形双向链表：node 节点作为哨兵，end() 即 node
- `sort()`: 归并排序（O(N log N)，in-place）
- `merge()`: 合并两个有序 list
- 不依赖 STL algorithms 的 random-access

**Deque:**
- 中控器 Map（指针数组）+ 多个缓冲区（chunk）
- `map[i]` 索引 buffer，`start`/`finish` 含 offset 计算
- `push_back()` / `push_front()`: 缓冲区满 → 新建 buffer，map 扩充（2倍）
- 迭代器跳跃：跨 buffer 边界处理
- 无连续性（与 vector 对比），但支持 random access

**Stack / Queue:**
- 默认底层容器：deque（也可指定 list）
- 无 iterator（不符合 Container 完整要求）
- queue 默认 deque；stack 默认 deque，可选 vector/list

**Priority Queue:**
- 大根堆 (max-heap)：vector 作为完全二叉树存储
- `make_heap()` / `push_heap()` / `pop_heap()` / `sort_heap()`
- Heap 算法实现：percolate-up / percolate-down（下沉）

**Bitset / Vector<bool>:**
- `bitset<N>`: 静态位数组，`operator[]` 返回 reference proxy
- `vector<bool>` 特化：`bool` 用 1 bit 存储，proxy reference 模拟真实引用

### 4. 关联式容器 (Associative Containers)

**RB-tree (红黑树):**
- 5个着色规则（根黑/红节点子黑/路径等黑）
- 左旋/右旋/插入修正（3种 case）/ 删除修正（4种 case）
- `insert_equal()` / `insert_unique()` 区分重复键值处理
- `iterator` = 中序遍历（in-order successor/prev）
- `lower_bound()` / `upper_bound()` 实现

**Map / Set:**
- 默认 less<F>（调用 `operator<`）
- `pair<const Key, T>` 作为 value_type
- `map<K,V>::operator[]`: 调用 `insert()`，value 默认构造

**Multimap / Multiset:**
- `insert_equal()`（允许重复键）
- 无 `operator[]`（语义不明）

**Hash Table (SGI 扩展):**
- 桶数组 + 链表解决冲突
- 负载因子 (load factor) = 元素数 / 桶数
- `max_load_factor` / `rehash()` / `reserve()` 控制
- 质数buckets数组：`stl_hash_fun.h`（int/double/char*/string/指针等特化）
- 可配置 bucket_count、hash_function、equal_key

**Hash Set / Map:**
- 底层 hash table（rebind trick 实现不同 value_type）
- `unordered_set` / `unordered_map` 的前身（SGI STL）

### 5. 算法 (Algorithms)

**Algorithm 文件结构：**
- `stl_algobase.h`: `min`/`max`/`iter_swap`/`copy`/`swap`/`fill`/`find`/`search` 等基础算法
- `stl_algo.h`: 高阶算法（sort/merge/binary_search/heap/partition/permutation）

**copy 算法：**
- `InputIterator` 版本：逐元素赋值（泛化版本）
- `trivially_copyable` 特化：直接 `memmove`（编译器原语检测）
- `copy_backward`: 从后向前复制，避免 overlap 问题

**sort 算法（introsort）：**
- Introsort = Introspective sort：快速排序 + 堆排序 + 插入排序混合
  - 分区深度 > 1.5 × log₂N → 切换堆排序
  - 子区间 ≤ 16 元素 → 切换插入排序
- `nth_element()`: 线性时间找第 N 大（小）元素
- `stable_sort()`: 归并排序（自然归并 + 额外空间）

**Heap 算法:**
- `make_heap()`: linear-time 构建（从 N/2 向上渗透）
- `push_heap()`: percolate-up（O(log N)）
- `pop_heap()`: swap root & last，然后 percolate-down（O(log N)）

**其他重要算法:**
- `unique()` / `unique_copy()`: 相邻重复元素移除（需先排序）
- `rotate()`: 两段数据对调（gcd 分组交换算法）
- `next_permutation()` / `prev_permutation()`: 全排列
- `partition()` / `stable_partition()`: 划分
- `lower_bound()` / `upper_bound()`: 有序区间二分查找

### 6. 仿函数 (Functor / Function Object)

**STL 定义的仿函数分类：**
- 算术类：`plus<T>`、`minus<T>`、`negate<T>`、`multiplies<T>`、`divides<T>`、`modulus<T>`
- 关系类：`equal_to<T>`、`not_equal_to<T>`、`greater<T>`、`less<T>`、`greater_equal<T>`、`less_equal<T>`
- 逻辑类：`logical_and<T>`、`logical_or<T>`、`logical_not<T>`
- 身份/选择/绑定：`identity<T>`、`select1st`、`select2nd`、`project1st`、`project2nd`、`pointer_to_unary_function`、`bind1st`/`bind2nd`

**适配器 (Adapter):**
- 函数适配器：`not1`/`not2`（否定一元/二元断言）
- `binder1st`/`binder2nd`: 绑定第一/第二参数
- `mem_fun`/`mem_fun_ref`: 成员函数适配器
- `ptr_fun`: 普通函数指针适配

**Adaptable Function:**
- `unary_function` / `binary_function`：继承这两个基类使仿函数可被 not1/bind1st 等适配器识别（空基类优化 EBO）

### 7. 配接器 (Adapter)

**容器配接器:**
- `stack` / `queue`: 默认 deque，开放 `c` protected 成员
- `priority_queue`: 默认 vector + heap 算法

**迭代器配接器:**
- `reverse_iterator`: `base()`、`operator*()` 偏移
- `insert_iterator`: `operator=` 调用容器的 `insert(pos, value)`
- `ostream_iterator`: `operator=` 输出并加分隔符

**函数配接器:**
- `pointer_to_unary_function` / `pointer_to_binary_function`
- `mem_fun_t` / `mem_fun_ref_t` 族
- `binder1st_t` / `binder2nd_t`

## Key Implementation Insights

### G++ 2.95.3 STL Extensions
- `hash_*` 系列仿函数（未进入 C++98 标准，后成为 C++11 unordered_* 基础）
- `slist`：单向链表（GCC 扩展）
- `rope`：字符串数据结构（基于平衡树）
- `bit_vector`：`vector<bool>` 的前身

### 内存分配时机
- Vector: capacity 增长策略——1.5×（某些版本）或 2×（SGI）
- List/Slist: 节点单独配置（不适用内存池）
- Deque: 缓冲区默认 512 字节，map 初始 8 个指针

### 技术细节
- `construct()` / `destroy()`: 对象构造与析构（placement new + explicit destructor call）
- `uninitialized_copy()` / `uninitialized_fill()`: 未初始化内存批量构造
- `temp_value()`: 临时对象避免多次构造（move 语义前身）
- `value_type()`: 萃取迭代器指向的类型

## Related Pages

- [[sources/pdf-book-cpp-templates-complete-guide]] — C++ Templates 2nd（模板元编程基础）
- [[sources/pdf-book-effective-stl]] — Effective STL（STL 使用最佳实践）
- [[sources/pdf-book-ds-algos-cpp]] — 数据结构与算法 C++ 实现
- [[sources/pdf-book-modern-cpp]] — Modern C++ books
- [[entities/cpp/cpp-stl-iterators]] — STL Iterators
- [[entities/cpp/smart-pointers]] — Smart pointers
- [[entities/cpp/raii]] — RAII idiom
- [[cpp-index]] — Modern C++ index
- [[sys-prog-index]] — System programming
