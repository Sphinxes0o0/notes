# C++ 综合指南

## 目录
1. [C++ 基础概念](#c-基础概念)
2. [编译与链接](#编译与链接) 
3. [内存管理](#内存管理)
4. [存储类与变量](#存储类与变量)
5. [现代C++特性](#现代c特性)
6. [STL 核心概念](#stl-核心概念)
7. [STL 容器详解](#stl-容器详解)

---

## C++ 基础概念

### 编译与链接

编译过程分为四个过程：
* **编译**
  * 编译预处理
  * 编译
  * 优化
* **汇编**
* **链接**

**编译预处理**：处理以 `#` 开头的指令；

**编译、优化**：将源码 `.cpp` 文件翻译成 `.s` 汇编代码；

**汇编**：将汇编代码 `.s` 翻译成机器指令 `.o` 文件；

**链接**：汇编程序生成的目标文件，即 `.o` 文件，并不会立即执行，因为可能会出现：`.cpp` 文件中的函数引用了另一个 `.cpp` 文件中定义的符号或者调用了某个库文件中的函数。那链接的目的就是将这些文件对应的目标文件连接成一个整体，从而生成可执行的程序文件。

![cpp_overview_00](../../../resources/imgs/cc/cpp_overview_00.png)

#### 链接分为两种：

**静态链接**：  
代码从其所在的静态链接库中拷贝到最终的可执行程序中，在该程序被执行时，这些代码会被装入到该进程的虚拟地址空间中。

**动态链接**：  
代码被放到动态链接库或共享对象的某个目标文件中，链接程序只是在最终的可执行程序中记录了共享对象的名字等一些信息。
在程序执行时，动态链接库的全部内容会被映射到运行时相应进行的虚拟地址的空间。

#### 二者的优缺点：

**静态链接**： 
![static](../../../resources/imgs/cc/cpp_overview_01_static.png) 
浪费空间，每个可执行程序都会有目标文件的一个副本，这样如果目标文件进行了更新操作，
就需要重新进行编译链接生成可执行程序（更新困难）；优点就是执行的时候运行速度快，因为可执行程序具备了程序运行的所有内容。

**动态链接**：
![dyn](../../../resources/imgs/cc/cpp_overview_01_dyna.png)

节省内存、更新方便，但是动态链接是在程序运行时，每次执行都需要链接，相比静态链接会有一定的性能损失。

---

## 内存管理

C++ 内存分区：栈、堆、全局/静态存储区、常量存储区、代码区。

* **栈**：
   存放函数的局部变量、函数参数、返回地址等，由编译器自动分配和释放。

* **堆**：
   动态申请的内存空间，就是由 malloc 分配的内存块，由程序员控制它的分配和释放，如果程序执行结束还没有释放，操作系统会自动回收。

* **全局区/静态存储区（.bss 段和 .data 段）**：
   存放全局变量和静态变量，程序运行结束操作系统自动释放，在 C 语言中，未初始化的放在 .bss 段中，初始化的放在 .data 段中，C++ 中不再区分了。

* **常量存储区（.data 段）**：
存放的是常量，不允许修改，程序运行结束自动释放。

* **代码区（.text 段）**：
   存放代码，不允许修改，但可以执行。编译后的二进制文件存放在这里。

> 从操作系统的本身来讲，以上存储区在内存中的分布是如下形式(从低地址到高地址)：`.text 段` --> `.data 段` --> `.bss 段` --> `堆` --> `unused` --> `栈` --> `env`

```cpp
#include <iostream>
using namespace std;

/*
说明：C++ 中不再区分初始化和未初始化的全局变量、静态变量的存储区，如果非要区分下述程序标注在了括号中
*/

int g_var = 0; // g_var 在全局区（.data 段）
char *gp_var;  // gp_var 在全局区（.bss 段）

int main()
{
    int var;                    // var 在栈区
    char *p_var;                // p_var 在栈区
    char arr[] = "abc";         // arr 为数组变量，存储在栈区；"abc"为字符串常量，存储在常量区
    char *p_var1 = "123456";    // p_var1 在栈区；"123456"为字符串常量，存储在常量区
    static int s_var = 0;       // s_var 为静态变量，存在静态存储区（.data 段）
    p_var = (char *)malloc(10); // 分配得来的 10 个字节的区域在堆区
    free(p_var);
    return 0;
}
```

### 栈和堆的区别

**申请方式**：
栈是系统`自动分配`，堆是程序员`主动申请`。

**申请后系统响应**：
分配栈空间，如果剩余空间大于申请空间则分配成功，否则分配失败栈溢出；申请堆空间，堆在内存中呈现的方式类似于链表（记录空闲地址空间的链表），在链表上寻找第一个大于申请空间的节点分配给程序，将该节点从链表中删除，大多数系统中该块空间的首地址存放的是本次分配空间的大小，便于释放，将该块空间上的剩余空间再次连接在空闲链表上。

栈在内存中是连续的一块空间（向低地址扩展）最大容量是系统预定好的，堆在内存中的空间（向高地址扩展）是不连续的。

**申请效率**：
栈是有系统自动分配，申请效率高，但程序员无法控制；堆是由程序员主动申请，效率低，使用起来方便但是容易产生碎片。

**存放的内容**：
栈中存放的是局部变量，函数的参数；堆中存放的内容由程序员控制。

---

## 存储类与变量

### C++ 中的左值（Lvalues）和右值（Rvalues）

* **左值（lvalue）**：
 指向内存位置的表达式被称为左值（lvalue）表达式。左值可以出现在赋值号的左边或右边。

* **右值（rvalue）**：
 术语右值（rvalue）指的是存储在内存中某些地址的数值。右值是不能对其进行赋值的表达式，也就是说，右值可以出现在赋值号的右边，但不能出现在赋值号的左边。

### C++ 存储类

存储类定义 C++ 程序中变量/函数的范围（可见性）和生命周期。这些说明符放置在它们所修饰的类型之前。下面列出 C++ 程序中可用的存储类：

* auto
* register
* static
* extern
* mutable

#### static 

`static` 存储类指示编译器在程序的生命周期内保持局部变量的存在，而不需要在每次它进入和离开作用域时进行创建和销毁。因此，使用 `static` 修饰局部变量可以在函数调用之间保持局部变量的值。

`static` 修饰符也可以应用于全局变量。当 `static` 修饰全局变量时，会使变量的作用域限制在声明它的文件内。

在 C++ 中，当 `static` 用在类数据成员上时，会导致仅有一个该成员的副本被类的所有对象共享。

### 变量的区别

全局变量、局部变量、静态全局变量、静态局部变量的区别:

#### 从作用域看：

* **全局变量**：
  具有全局作用域。全局变量只需在一个源文件中定义，就可以作用于所有的源文件。当然，其他不包含全局变量定义的源文件需要用 extern 关键字再次声明这个全局变量。

* **静态全局变量**：
  具有文件作用域。它与全局变量的区别在于如果程序包含多个文件的话，它作用于定义它的文件里，不能作用到其它文件里，即被 static 关键字修饰过的变量具有文件作用域。

* **局部变量**：
  具有局部作用域。它是自动对象（auto），在程序运行期间不是一直存在，而是只在函数执行期间存在，函数的一次调用执行结束后，变量被撤销，其所占用的内存也被收回。

* **静态局部变量**：
  具有局部作用域。它只被初始化一次，自从第一次被初始化直到程序运行结束都一直存在，它和全局变量的区别在于全局变量对所有的函数都是可见的，而静态局部变量只对定义自己的函数体始终可见。

---

## 现代C++特性

验证环境：
```
> clang --version
clang version 13.0.1
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/bin
```

### 被弃用的特性

- **`char *`** - 不再允许字符串字面值常量赋值给一个 char *。如果需要用字符串字面值常量赋值和初始化一个 char *，应该使用 const char * 或者 auto。

- **`unexpected_handler`、`set_unexpected()` --> `noexcept`** - `noexcept` 是 C++11 为了替代 `throw()` 而提出的一个新的关键字

- **`auto_ptr`  --> `unique_ptr`**

- **`register`** 关键字被弃用，可以使用但不再具备任何实际含义

- **`bool` 类型的 `++` 操作被弃用**

### 新增的特性

#### nullptr

`nullptr` 出现的目的是为了替代 `NULL`。在某种意义上来说，传统 C++ 会把 `NULL`、`0` 视为同一种东西，这取决于编译器如何定义 `NULL`。

```cpp
#include <iostream>
#include <type_traits>

void foo(char *);
void foo(int);

int main() {
    if (std::is_same<decltype(NULL), decltype(0)>::value)
        std::cout << "NULL == 0" << std::endl;
    if (std::is_same<decltype(NULL), decltype((void*)0)>::value)
        std::cout << "NULL == (void *)0" << std::endl;
    if (std::is_same<decltype(NULL), std::nullptr_t>::value)
        std::cout << "NULL == nullptr" << std::endl;

    foo(0);          // 调用 foo(int)
    // foo(NULL);    // 该行不能通过编译
    foo(nullptr);    // 调用 foo(char*)
    return 0;
}
```

#### constexpr

`constexpr` 让用户显式的声明函数或对象构造函数在编译期会成为常量表达式。从 C++14 开始，constexpr 函数可以在内部使用局部变量、循环和分支等简单语句。

#### auto

`auto` 在很早以前就已经进入了 C++，但是他始终作为一个存储类型的指示符存在，与 `register` 并存。使用 `auto` 进行类型推导的一个最为常见而且显著的例子就是迭代器。

```cpp
// 在 C++11 之前
for(vector<int>::const_iterator it = vec.cbegin(); itr != vec.cend(); ++it)

// 而有了 auto 之后可以：
for (auto it = list.begin(); it != list.end(); ++it) {
    vec.push_back(*it);
}
```

#### 初始化列表

C++11 首先把初始化列表的概念绑定到了类型上，并将其称之为 `std::initializer_list`，允许构造函数或其他函数像参数一样使用初始化列表。

```cpp
#include <initializer_list>
#include <vector>
class MagicFoo {
public:
    std::vector<int> vec;
    MagicFoo(std::initializer_list<int> list) {
        for (auto it = list.begin(); it != list.end(); ++it)
            vec.push_back(*it);
    }
};
int main() {
    MagicFoo magicFoo = {1, 2, 3, 4, 5};
    return 0;
}
```

#### 变长参数模板

```cpp
template<typename... Ts> class Magic;

// 递归模板函数
template<typename T0>
void printf1(T0 value) {
    std::cout << value << std::endl;
}
template<typename T, typename... Ts>
void printf1(T value, Ts... args) {
    std::cout << value << std::endl;
    printf1(args...);
}
```

---

## STL 核心概念

### 六大组件

- **容器 container**：
	`vector`, `list`, `deque`, `set`, `map`;
	`class template`
	
- **算法 algorithms**：
	`sort`, `search`, `copy`, `erase`
	`function template`
	
- **迭代器 iterators**：
	泛型指针,
	将 `operator*`, `operator->`, `operator++`, `operator--` 
	等指针相关操作予以重载的 `class template`

- **仿函数 functors**：
	行为类似函数, 重载了` operator()` 的 `class` 或 `class template`

- **适配器 adapters**： 
	修饰容器，仿函数，迭代器接口

- **分配器 allocators**：
	内存分配和管理

大部分的情况下 Container 通过 Allocator 获取内存空间， 
Algorithm 通过 Iterator 存取 Container 中的内容， 
Functor 实现 Algorithm 的不同变化策略， 
Adapter 修饰 Functor

### Allocators

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

STL 定义了5个全局函数：

* construct()
* destroy()
* uninitialized_copy() - 将内存配置和对象的构造行为分开
* uninitialized_fill()
* uninitialized_fill_n()

### 迭代器 & traits

抽象的设计概念: 
提供一种方法, 使之能够顺序的访问容器内的各个元素，而无需暴露聚合物的内部表述方式。

可以看作是一种行为类似指针的对象, 而指针的各种行为中最常见也最重要的便是`dereference`和
成员访问`member access`， 所以迭代器大部分的工作是对 `operator*` 和 `operator->`进行重载.

#### 萃取

```cpp
template <class T>
struct iterator_traits {
	typedef typename I::value_type value_type;
}
```

迭代器常用类型：

* **iterator_category** - 迭代器类别
* **value_type** - 对象类型
* **difference_type** - 表示两个迭代器之间的距离/容器的最大容量
* **pointer** - 指针类型
* **reference** - 引用类型

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

---

## STL 容器详解

### 容器对比表

|        容器        |    底层数据结构   |                         时间复杂度                        | 有无序 | 可不可重复 |                                     其他                                       |
|:------------------:|:-----------------:|:---------------------------------------------------------:|:------:|:----------:|:----------------------------------------------------------------------------:|
| array              | 数组              | 随机读改 O(1)                                             | 无序   | 可重复     | 支持随机访问                                                                 |
| vector             | 数组              | 随机读改、尾部插入、尾部删除 O(1) 头部插入、头部删除 O(n) | 无序   | 可重复     | 支持随机访问                                                                    |
| deque              | 双端队列          | 头尾插入、头尾删除 O(1)                                   | 无序   | 可重复     | 一个中央控制器 + 多个缓冲区，支持首尾快速增删，支持随机访问                       |
| forward_list       | 单向链表          | 插入、删除 O(1)                                           | 无序   | 可重复     | 不支持随机访问                                                               |
| list               | 双向链表          | 插入、删除 O(1)                                           | 无序   | 可重复     | 不支持随机访问                                                               |
| stack              | deque / list      | 顶部插入、顶部删除 O(1)                                   | 无序   | 可重复     | deque 或 list 封闭头端开口，不用 vector 的原因应该是容量大小有限制，扩容耗时     |
| queue              | deque / list      | 尾部插入、头部删除 O(1)                                   | 无序   | 可重复     | deque 或 list 封闭头端开口，不用 vector 的原因应该是容量大小有限制，扩容耗时     |
| priority_queue     | vector + max-heap | 插入、删除 O(log2n)                                       | 有序   | 可重复     | vector容器+heap处理规则                                                      |
| set                | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 不可重复   |                                                                              |
| multiset           | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 可重复     |                                                                              |
| map                | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 不可重复   |                                                                              |
| multimap           | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 可重复     |                                                                              |
| unordered_set      | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 不可重复   |                                                                              |
| unordered_multiset | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 可重复     |                                                                              |
| unordered_map      | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 不可重复   |                                                                              |
| unordered_multimap | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 可重复     |                                                                              |

### array

#### 函数一览

|             方法             |     分类   |                                      含义                                       |
|:----------------------------:|:---------:|:------------------------------------------------------------------------------:|
| begin                        | iterators |  返回指向数组容器中第一个元素的迭代器                                               |
| end                          | iterators |  返回指向数组容器中最后一个元素之后的理论元素的迭代器                                 |
| rbegin                       | iterators |  返回指向数组容器中最后一个元素的反向迭代器                                          |
| rend                         | iterators |  返回一个反向迭代器，指向数组中第一个元素之前的理论元素                               |
| cbegin                       | iterators |  返回指向数组容器中第一个元素的常量迭代器(const_iterator)                          |
| cend                         | iterators |  返回指向数组容器中最后一个元素之后的理论元素的常量迭代器(const_iterator)           |
| crbegin                      | iterators |  返回指向数组容器中最后一个元素的常量反向迭代器(const_reverse_iterator)            |
| crend                        | iterators |  返回指向数组中第一个元素之前的理论元素的常量反向迭代器(const_reverse_iterator)     |
| size                         | capacity  |  返回数组容器中元素的数量                                                          |
| max_size                     | capacity  |  返回数组容器可容纳的最大元素数                                                    |
| empty                        | capacity  |  返回一个布尔值，指示数组容器是否为空                                               |
| operator[]                   | element access |  返回容器中第 n(参数)个位置的元素的引用                                      |
| at                           | element access |  返回容器中第 n(参数)个位置的元素的引用                                      |
| front                        | element access |  返回对容器中第一个元素的引用                                                 |
| back                         | element access |  返回对容器中最后一个元素的引用                                               |
| data                         | element access |  返回指向容器中第一个元素的指针                                               |
| fill                         | element access |  用 val(参数)填充数组所有元素                                                |
| swap                         | element access |  通过 x (参数)的内容交换数组的内容                                            |

#### 源码实现

```cpp
Class template std::array
namespace std
{
    template<class T, size_t N>
    struct array
    {
        // types
        using value_type             = T;
        using pointer                = T*;
        using const_pointer          = const T*;
        using reference              = T&;
        using const_reference        = const T&;
        using size_type              = size_t;
        using difference_type        = ptrdiff_t;
        using iterator               = /* implementation-defined */;
        using const_iterator         = /* implementation-defined */;
        using reverse_iterator       = std::reverse_iterator<iterator>;
        using const_reverse_iterator = std::reverse_iterator<const_iterator>;
 
        // no explicit construct/copy/destroy for aggregate type
 
        constexpr void fill(const T& u);
        constexpr void swap(array&) noexcept(is_nothrow_swappable_v<T>);
 
        // iterators
        constexpr iterator               begin() noexcept;
        constexpr const_iterator         begin() const noexcept;
        constexpr iterator               end() noexcept;
        constexpr const_iterator         end() const noexcept;
 
        constexpr reverse_iterator       rbegin() noexcept;
        constexpr const_reverse_iterator rbegin() const noexcept;
        constexpr reverse_iterator       rend() noexcept;
        constexpr const_reverse_iterator rend() const noexcept;
 
        constexpr const_iterator         cbegin() const noexcept;
        constexpr const_iterator         cend() const noexcept;
        constexpr const_reverse_iterator crbegin() const noexcept;
        constexpr const_reverse_iterator crend() const noexcept;
 
        // capacity
        [[nodiscard]] constexpr bool empty() const noexcept;
        constexpr size_type size() const noexcept;
        constexpr size_type max_size() const noexcept;
 
        // element access
        constexpr reference       operator[](size_type n);
        constexpr const_reference operator[](size_type n) const;
        constexpr reference       at(size_type n);
        constexpr const_reference at(size_type n) const;
        constexpr reference       front();
        constexpr const_reference front() const;
        constexpr reference       back();
        constexpr const_reference back() const;
 
        constexpr T*       data() noexcept;
        constexpr const T* data() const noexcept;
    };
 
    template<class T, class... U>
        array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```

---

## 总结

本文档涵盖了C++从基础概念到现代特性，从内存管理到STL容器的全面知识。无论是初学者还是有经验的开发者，都可以在这里找到需要的C++相关信息。

主要内容包括：
- C++编译链接过程
- 内存管理和存储类
- 现代C++11/14/17新特性 
- STL六大组件详解
- 常用容器的实现和特性

通过系统学习这些内容，可以建立完整的C++知识体系。
