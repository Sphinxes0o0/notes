---
title: c_memory
date: 2022-01-03 23:20:06
tags:
    - Linux
    - C
    - Memory
    - Notes
---

## 内存分区
* 栈区（stack）:

  栈又称堆栈，是用户存放程序临时创建的局部变量,
  存放函数形参和局部变量（auto类型），由编译器自动分配和释放。

  在函数被调用时，其参数也会被压入发起调用的进程栈中，并且待到调用结束后，函数的返回值也会被存放回栈中。

  由于栈的先进先出(FIFO)特点，所以栈特别方便用来保存/恢复调用现场。


* 堆区（heap）:

  堆是用于存放进程运行中被动态分配的内存段，它的大小并不固定，可动态扩张或缩减。
  该区由程序员申请后使用，需要手动释放否则会造成内存泄漏。
  如果程序员没有手动释放，那么程序结束时可能由OS回收。

* 全局/静态存储区：

  存放全局变量和静态变量（包括静态全局变量与静态局部变量），初始化的全局变量和静态局部变量放在一块，未初始化的放在另一块。

* 文字常量区：

  常量在统一运行被创建，常量区的内存是只读的，程序结束后由系统释放。

* 程序代码区：

  存放程序的二进制代码，内存由系统管理

## 可执行分段
一个程序本质上都是由 bss段、data段、text段三个组成的。

- `text`

  这部分区域的大小在程序运行前就已经确定，并且内存区域通常属于只读(某些架构也允许代码段为可写，即允许修改程序)。
  在代码段中，也有可能包含一些只读的常数变量，例如字符串常量等

- `date`

  存放在编译阶段（而非运行时）就能确定的数据，可读可写, 是指用来存放程序中已初始化的全局变量的一块内存区域。
  也就是通常所说的静态存储区，赋了初值的全局变量和静态变量存放在这个区域，常量也存在这个区域.
  数据段属于静态内存分配.

- `bss`
  bss段（bss segment）通常是指用来存放程序中未初始化的全局变量的一块内存区域。
  bss是英文Block Started by Symbol的简称。
  bss段属于静态内存分配。
  已经定义但没赋初值的全局变量和静态变量存放在这个区域。

> `text` 段在内存中被映射为只读，但 `date` 段与 `bss` 段是可写的.


![m](../../resources/imgs/cc/memory.gif)


> 代码段，数据段，堆栈段是cpu级别的概念，五大分区属于语言级别的概念

## 动态内存分配

### 堆内存分配机制

C 语言中，动态内存分配主要通过 `malloc`、`calloc`、`realloc` 和 `free` 四个函数完成。这些函数位于标准库 `stdlib.h` 中。

```c
#include <stdlib.h>

// malloc - 分配指定字节大小的内存，不初始化
void* malloc(size_t size);

// calloc - 分配 num 个大小为 size 的元素，并初始化为 0
void* calloc(size_t num, size_t size);

// realloc - 重新调整已分配内存的大小
void* realloc(void* ptr, size_t new_size);

// free - 释放之前分配的内存
void free(void* ptr);
```

### 内存分配示例

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    // 使用 malloc 分配内存
    int* arr = (int*)malloc(10 * sizeof(int));
    if (arr == NULL) {
        // 内存分配失败
        return -1;
    }

    // 使用 malloc 分配的内存不会被初始化，需要手动初始化
    for (int i = 0; i < 10; i++) {
        arr[i] = i;
    }

    // 使用 calloc 分配内存，会被初始化为 0
    int* arr2 = (int*)calloc(10, sizeof(int));

    // 重新分配内存
    int* arr3 = (int*)realloc(arr, 20 * sizeof(int));
    if (arr3 != NULL) {
        arr = arr3;  // 更新指针
    }

    // 释放内存
    free(arr);
    free(arr2);
    free(arr3);

    return 0;
}
```

### 内存分配的实现原理

在 Linux 系统中，动态内存分配通常通过 `brk()` 或 `mmap()` 系统调用实现：

- **`brk()` 系统调用**：调整堆的大小。当请求的内存较小时（通常小于 128KB），glibc 的内存分配器会使用 `brk()` 来扩展堆。
- **`mmap()` 系统调用**：直接映射匿名内存区域。当请求的内存较大时，分配器会使用 `mmap()` 创建独立的内存映射。

glibc 实现了多层分配器：
1. **ptmalloc2**：默认的分配器，将内存分为 chunk 进行管理
2. **tcmalloc**：Google 开发的分配器，提供更好的多线程性能
3. **jemalloc**：FreeBSD 使用的分配器，减少碎片化

### 常见的内存分配错误

| 错误类型 | 描述 | 后果 |
|---------|------|------|
| 内存泄漏 | 分配后未释放 | 内存消耗持续增长 |
| 双重释放 | 对同一内存块释放两次 | 未定义行为，可能崩溃 |
| 释放后使用 | 访问已释放的内存 | 未定义行为，数据损坏 |
| 缓冲区溢出 | 写入超出分配范围 | 破坏相邻内存 |
| 空指针解引用 | 对 NULL 进行操作 | 程序崩溃 |

```c
// 内存泄漏示例
void memory_leak() {
    int* ptr = (int*)malloc(sizeof(int) * 100);
    // 忘记 free(ptr) 就返回
    return;  // ptr 指向的内存泄漏
}

// 双重释放示例
void double_free() {
    int* ptr = (int*)malloc(sizeof(int));
    free(ptr);
    free(ptr);  // 错误：对同一指针释放两次
}

// 释放后使用示例
void use_after_free() {
    int* ptr = (int*)malloc(sizeof(int));
    *ptr = 42;
    free(ptr);
    printf("%d\n", *ptr);  // 错误：访问已释放的内存
}
```

## 内存对齐

### 什么是内存对齐

内存对齐是指数据在内存中的起始地址必须是某个值 N 的倍数。N 称为对齐系数，通常是 2、4、8 或 16 字节。

为什么需要内存对齐：
1. **硬件限制**：大多数 CPU 要求数据按特定边界访问，否则可能触发硬件异常或性能下降
2. **性能考虑**：对齐的数据访问比非对齐访问快数倍
3. **跨平台兼容**：不同平台的对齐要求可能不同

### 对齐规则

基本类型的对齐值等于其大小：

| 类型 | 大小 | 对齐要求 |
|------|------|---------|
| char | 1 字节 | 1 字节 |
| short | 2 字节 | 2 字节 |
| int | 4 字节 | 4 字节 |
| long | 8 字节（64位） | 8 字节 |
| float | 4 字节 | 4 字节 |
| double | 8 字节 | 8 字节（32位系统可能为 4 字节） |
| 指针 | 8 字节（64位） | 8 字节 |

结构体的对齐要求是其所有成员的最大对齐值。

### 结构体对齐示例

```c
#include <stdio.h>

// 未使用 #pragma pack 的结构体
struct Unpacked {
    char a;    // 偏移 0
    int b;     // 偏移 4-7（需要 3 字节填充）
    char c;    // 偏移 8
};             // 总大小：12 字节（不是 6 字节）

// 使用 #pragma pack(1) 强制 1 字节对齐
#pragma pack(push, 1)
struct Packed {
    char a;    // 偏移 0
    int b;     // 偏移 1-4
    char c;    // 偏移 5
};             // 总大小：6 字节
#pragma pack(pop)

int main() {
    printf("Unpacked size: %zu\n", sizeof(struct Unpacked));  // 12
    printf("Packed size: %zu\n", sizeof(struct Packed));      // 6
    return 0;
}
```

### aligned 属性

GCC 和 Clang 支持 `__attribute__((aligned(N)))` 来指定对齐方式：

```c
#include <stdio.h>

struct Aligned16 {
    int x;
} __attribute__((aligned(16)));  // 整个结构体按 16 字节对齐

struct Aligned32 {
    double a;
    char b;
} __attribute__((aligned(32)));

int main() {
    printf("Aligned16 size: %zu, align: %zu\n",
           sizeof(struct Aligned16), __alignof__(struct Aligned16));
    printf("Aligned32 size: %zu, align: %zu\n",
           sizeof(struct Aligned32), __alignof__(struct Aligned32));
    return 0;
}
```

## 栈内存管理

### 栈帧结构

函数调用时，会在栈上创建一个栈帧（stack frame），包含以下内容：

```
高地址
+------------------+
|    参数 N        |  ← 函数参数（从右向左压栈）
|    ...           |
|    参数 2        |
|    参数 1        |
+------------------+
|   返回地址       |  ← 调用指令的下一条地址
+------------------+
|   保存的 ebp     |  ← 上一个函数的栈帧基址
+------------------+
|   局部变量 1     |  ← 函数局部变量
|   局部变量 2     |
|   ...            |
|   局部变量 N     |
+------------------+
|   临时变量/寄存器|
+------------------+
低地址
```

### 栈溢出

栈溢出（stack overflow）发生在栈空间耗尽时，常见原因：

1. **递归调用过深**：没有正确的基准情况或递归深度过大
2. **大数组分配**：在栈上分配过大的局部变量
3. **不合理的链式调用**：深层函数调用链

```c
// 栈溢出示例 - 递归没有终止条件
int infinite_recursion(int n) {
    return infinite_recursion(n + 1);  // 栈溢出
}

// 大数组导致栈溢出
void large_array() {
    int arr[1000000];  // 4MB，栈可能无法容纳
}

// 安全的替代方案 - 使用静态数组
static int safe_arr[1000000];  // 位于 data 段，不占用栈空间

// 或者使用堆分配
void safe_allocation() {
    int* arr = (int*)malloc(sizeof(int) * 1000000);
    if (arr) {
        // 安全使用
        free(arr);
    }
}
```

### 寄存器与栈帧

x86-64 架构中，栈帧相关的主要寄存器：

| 寄存器 | 用途 |
|--------|------|
| rsp | 栈顶指针（Stack Pointer） |
| rbp | 栈帧基指针（Base Pointer） |
| return address | 返回地址，紧邻栈帧 |

GCC 提供了 `__builtin_frame_address()` 和 `__builtin_return_address()` 内建函数来获取栈帧信息。

## 内存屏障与优化

### 编译器优化与内存 reorder

现代编译器会对代码进行优化，可能改变内存访问的顺序。处理器也会采用指令重排来提升性能。

```c
// 示例：编译器可能改变内存访问顺序
int flag = 0;
int value = 0;

void writer() {
    value = 42;      // 可能被编译器重排到 flag = 1 之后
    flag = 1;
}

void reader() {
    if (flag == 1) {
        // value 可能还未被写入
        printf("value = %d\n", value);
    }
}
```

### 内存屏障类型

| 屏障类型 | 说明 |
|---------|------|
| `__asm__ __volatile__("" ::: "memory")` | GCC 内存屏障 |
| `std::atomic_thread_fence(std::memory_order_seq_cst)` | C++11 原子屏障 |
| `MMIO_WRITE_BARRIER_64()` | 设备内存操作屏障 |

### volatile 关键字

`volatile` 告诉编译器不要优化对该变量的访问：

```c
volatile int* device_reg = (volatile int*)0x40021000;

// 每次访问都会实际执行，不会被优化掉
int value = *device_reg;

// 适合设备寄存器、共享内存等多线程场景
```

注意：`volatile` 不提供跨线程同步，不适合替代适当的同步机制。

## 常见内存检测工具

### Valgrind

```bash
# 检测内存泄漏和非法访问
valgrind --leak-check=full ./program

# 检测未初始化内存使用
valgrind --track-origins=yes ./program

# 检测内存操作错误
valgrind --tool=memcheck ./program
```

### AddressSanitizer (ASan)

编译时添加 `-fsanitize=address` 标志：

```bash
gcc -fsanitize=address -g program.c -o program
```

ASan 可以检测：
- 堆/栈/全局缓冲区溢出
- 释放后使用（use-after-free）
- 返回后使用（use-after-return）
- 重复释放

### 堆分析工具

| 工具 | 用途 |
|------|------|
| mtrace | GNU 内存分配追踪 |
| dmalloc | Debug memory allocator |
| Electric Fence | 缓冲区溢出检测 |
| Massif | 堆 profiling 工具（Valgrind 的一部分）|
