# The Annotated STL Sources

## Overview

### 六大组件

- 容器 container :
	`vector`, `list`, `deque`, `set`, `map`;
	`class template`
	
- 算法 algorithms
	`sort`, `search`, `copy`, `erase`
	`function template`
	
- 迭代器 iterators
	泛型指针,
	将 `operator*`, `operator->`, `operator++`, `operator--` 
	等指针相关操作予以重载的 `class template`

- 仿函数 functors
	行为类似函数, 重载了` operator()` 的 `class` 或 `class template`

- 适配器 adapters 
	修饰容器，仿函数，迭代器接口

- 分配器 allocators
	内存分配和管理


主流的实现有一个家：
- libc++: llvm project
- libstdc++: GNU gcc

大部分的情况下 Container 通过 Allocator 获取内存空间， 
Algorithm 通过 Iterator 存取 Container 中的内容， 
Functor 实现 Algorithm 的不同变化策略， 
Adapter 修饰 Functor

## Allocators

必要接口：
```
allocator::value_type
allocator::pointer
allocator::const_pointer
allocator::reference
allocator::const_reference
allocator::size_type
allocator::difference_type
```

### STL 定义了5个全局函数

> POD

* construct()
* destroy()

#### uninitialized_copy()
将内存配置和对象的构造行为分开
 - 萃取类型
	- is_POD
		- copy

* uninitialized_fill()
* uninitialized_fill_n()


## iterators & traits

抽象的设计概念: 
提供一种方法, 使之能够顺序的访问容器内的各个元素，而无需暴露聚合物的内部表述方式。

可以看作是一种行为类似指针的对象, 而指针的各种行为中最常见也最重要的便是`dereference`和
成员访问`member access`， 所以迭代器大部分的工作是对 `operator*` 和 `operator->`进行重载.

迭代器需要所指对象的具体类型, 参数可以依靠`template 参数推导机制`获得， 但是无法推导
函数的返回值。

因此，迭代器大部分都是`class type`，可以显式声明(typename T);
如果不是的话，就必须对范化进行特化处理， 既偏特化 `partial specialization`.

### 萃取

```cpp
tempalte <class T>
struct iterator_traits {
	typedef typename I::value_type value_type;
}
```

迭代器常用类型：

* iterator_category

* value_type: 对象类型

* difference_type: 表示两个迭代器之间的距离/容器的最大容量

* pointer

* reference
	从迭代器是否可以改变所指对象的内容来看, 可以分为：
	- constant iterators: 对右值操作
	- mutable iterators: 对左值操作


迭代器的分类：
* input iterator
* output iterator
* forward iterator
* bidirectional iterator
* random access iterator

```
input IT                   output IT
	\						/
		\                /
			\		/
			Forward IT
				|
			Bidireactional IT
				|
			RandomAccess IT
```

















● 最近未使用置换（NRU）

出现未命中现象时，置换最近一个周期未使用的数据。

● 先入先出置换（FIFO)

出现未命中现象时，置换最早进入的数据。

● 最近最少使用置换（LRU)

出现未命中现象时，置换未使用时间最长的数据。