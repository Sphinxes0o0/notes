---
title: elf简介
date: 2022-01-15 18:03:28
tags:
    - linux
    - c
    - elf
---

## 回顾

程序的转换处理过程:

1. C代码 hello.c:

```C
#include <stdio.h>

int main() {
    printf("hello!");
}
```
2. 预处理

```bash
$ gcc -E hello.c -o hello.i
```
预处理器会展开头文件、宏定义等，生成 `.i` 文件。
3. 汇编
```bash
$ gcc -S hello.c -o hello.s
```
生成汇编代码 `.s` 文件。关键部分：
```asm
.globl	main
main:
	pushq	%rbp
	movq	%rsp, %rbp
	leaq	.LC0(%rip), %rax
	movq	%rax, %rdi
	call	printf@PLT
	movl	$0, %eax
	popq	%rbp
	ret
```

4. 机器码

```bash
gcc -C hello.s
```
* file 查看
    ```bash
    hello.o: ELF 64-bit LSB relocatable, x86-64, version 1 (SYSV), not stripped
    ```

* objdump 查看
  ```bash
    hello.o:     file format elf64-x86-64
    hello.o
  ```

* nm 查看
  ```bash
                     U _GLOBAL_OFFSET_TABLE_
    0000000000000000 T main
                     U printf
  ```

* readelf
```bash
$ readelf -h hello.o     # 查看ELF头信息
$ readelf -S hello.o     # 查看Section headers
$ readelf -s hello.o     # 查看符号表
```
关键sections：`.text`(代码), `.data`(初始化数据), `.bss`(未初始化数据), `.rodata`(只读数据)

5. 链接
```bash
gcc hello.o -o hello
```

* file 查看

```bash
hello: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=92f33896a3687559674a0d0f204f68984bfd8ee3, for GNU/Linux 4.4.0, not stripped
```
* readelf (可执行文件)：
    ```bash
    $ readelf -h hello       # 显示type为DYN (PIE executable)
    $ readelf -l hello       # 显示Program headers
    $ readelf -d hello       # 显示动态链接信息
    ```
* nm (符号表)
    ```bash
    $ nm hello                   # 显示符号和地址
    $ nm -D hello               # 显示动态符号
    ```
    关键符号：`T main`(全局函数), `U printf`(未定义符号，需要动态链接)

## 格式简介

> ELF： executable and linkable format

一种用于可执行文件、目标代码、共享库和核心转储（`core dump`）的标准文件格式。
首次发布于一个名为 `System V Release 4（SVR4）`的 `Unix` 操作系统版本中关于应用二进制接口（ABI）的规范中，并且此后不久发布于工具接口标准（Tool Interface Standard），随后很快被不同 `Unix` 发行商所接受。1999 年，这种格式被 `86open` 项目选为 `x86` 架构处理器上的 `Unix` 和 类 Unix 系统的标准二进制文件格式。

按照设计，ELF 格式灵活性高、可扩展，并且跨平台。比如它支持不同的字节序和地址范围，所以它不会不兼容某一特别的 CPU 或指令架构。这也使得 ELF 格式能够被运行于众多不同平台的各种操作系统所广泛采纳。

每个 ELF 文件都由一个 ELF 首部和紧跟其后的文件数据部分组成。数据部分可以包含：

* 程序头表（Program header table）：
  描述 0 个或多个内存段信息
  > 内存段中包含了用于某个 ELF 文件运行时执行所需的信息，而片段中包含了用于链接和重定位的重要数据。
    整个文件中的任何一个字节至多只能属于一个片段，也就是说可能存在不属于任何片段的孤立字节。
* 分段头表（Section header table）：
  描述 0 段或多段链接与重定位需要的数据
* 程序头表与分段头表引用的数据，比如 `.text`, `.data`

程序表中包含指向其他分段的索引， 分段表中也是如此：

```text
----------------------------
|     ELF  header           |
|---------------------------|
|   Program header table    |-------|
|---------------------------|       |
|          .text            |<------|-------|
|---------------------------|       |       |
|          .rodata          |<------|-------|
|---------------------------|       |       |
|           ......          |<------|-------|
|---------------------------|       |       |
|           .data           |<------|-------|
|---------------------------|               |
|  Section header table     |---------------|
|---------------------------|
```

* `Linux-IA32` 下的 ELF 存储和对应到Linux 内核中的情况

```text
  0====>-----------------------------  ---|             --------------------------------------              
        |     ELF  header           |     |             |      Kernel Virtual           |  /| 1GB
        |                           |     |             |                               |   |/  
        |---------------------------|     |             |-------------------------------|<===== 0xC000 00000  
        |   Program header table    |     |             |     User Stack  (dynamic)     |  <-- 栈 
        |                           |     |             |                               |
        |---------------------------|     |             |-------------------------------|<===== %esp
        |          .init            |     | \           |            /|\                |
        |---------------------------|     |  \          |             |                 |
        |          .text            |     |   \         |            \|/                |
        |---------------------------|     |    \        |-------------------------------|
        |          .rodata          |     |     \       |        dynamic libs           | <-- 共享库区域
        |---------------------------|  ---|      |      |-------------------------------|
        |           .data           | ---|       |      |           /|\                 |
        |---------------------------|    |\      |      |            |                  |
        |           .bss            | ---| \     |      |            |                  |
        |---------------------------|       \    |      |-------------------------------|<===== brk
        |           .symtab         |       |    |      |          heap                 | <-- 堆： 由程序主动申请释放(malloc, new)
        |---------------------------|       |     \     |-------------------------------|
        |           .debug          |       |      ---->|        .data ,  .bss          | <-- 读写数据段
        |---------------------------|        \          |-------------------------------|             
        |           .line           |         \---->    |       .init, .text, .rodata   | <-- 只读代码段
        |---------------------------|                   |-------------------------------|<===== 0x0804 8000
        |           .data           |                   |                               |
        |---------------------------|                   |         not used yet          |
        |           .strtab         |                   |                               |
        |---------------------------|                   |-------------------------------|<===== 0 
                ELF 文件(磁盘)                               Linux 虚拟空间
```

#### sections

* header
    包括：我们字节标识信息， 文件类型(.O, exec, .so), 机器类型(IA-32, IA-64, Power-32)

* `.text`
  编译后的代码部分

* `.rodata`
  只读数据

* `.data`
  已初始化的全局变量

* `.bss`
  block started by symbol
  为初始化的全局变量, 仅仅作为占位符, 不占据任何实际磁盘空间。
  > 区分初始化和非初始化是为了提供空间效率

  因为C语言中已经规定: 未初始化的全局变量和局部静态变量的默认值为零。
  所以，将为初始化的变量和已经初始化的变量分开成两个段：
  * `.data` 中存放具体的初始值, 仅占有一定的磁盘空间
  * `.bss` 中仅说明变量将来执行时占用几个字节即可, 几乎不占用磁盘空间， 提高了执行效率

* '.symtab`
  存放函数名和全局变量(符号表)信息

* `.rel.text` & `.rel.data`
  `.text` & `.data`的重定位信息, 用于重新修改代码段中的指令的地址信 & 对被模块使用或定义的全局变量进行重定位的信息。
  在`.o`文件里面是需要的， 而实际的可执行文件里面已经重定位过了， 所以就不存在了。

* `.debug`
  调试符号表

* `strtab`
  包含`symtab` 和 `debug` 中符号和节名

#### 代码对应ELF

```cpp
#include <stdio.h>

int y = 100;                   // .data
int x;                         // .bss

void print() {
    printf("hello!");         // .text
}


int main() {                 // .text
    static int a = 1;        // .data
    static int b;            // .bss
    int c = 200, d;           
    print();
}


```
#### elf.h

通过 `man elf` 就可以获取elf 介绍的详细信息

* elf header

```c
#define EI_NIDENT 16

typedef struct {
    unsigned char e_ident[EI_NIDENT];
    uint16_t      e_type;
    uint16_t      e_machine;
    uint32_t      e_version;
    ElfN_Addr     e_entry;
    ElfN_Off      e_phoff;
    ElfN_Off      e_shoff;
    uint32_t      e_flags;
    uint16_t      e_ehsize;
    uint16_t      e_phentsize;
    uint16_t      e_phnum;
    uint16_t      e_shentsize;
    uint16_t      e_shnum;
    uint16_t      e_shstrndx;
} ElfN_Ehdr;

# N = 32 or 64
```
* Program header (Phdr)

```c
// 32
typedef struct {
    uint32_t   p_type;
    Elf32_Off  p_offset;
    Elf32_Addr p_vaddr;
    Elf32_Addr p_paddr;
    uint32_t   p_filesz;
    uint32_t   p_memsz;
    uint32_t   p_flags;
    uint32_t   p_align;
} Elf32_Phdr;

// 64
typedef struct {
    uint32_t   p_type;
    uint32_t   p_flags;
    Elf64_Off  p_offset;
    Elf64_Addr p_vaddr;
    Elf64_Addr p_paddr;
    uint64_t   p_filesz;
    uint64_t   p_memsz;
    uint64_t   p_align;
} Elf64_Phdr;

```

* Section header (Shdr)
```c
typedef struct {
    uint32_t   sh_name;
    uint32_t   sh_type;
    uint32_t   sh_flags;
    Elf32_Addr sh_addr;
    Elf32_Off  sh_offset;
    uint32_t   sh_size;
    uint32_t   sh_link;
    uint32_t   sh_info;
    uint32_t   sh_addralign;
    uint32_t   sh_entsize;
} Elf32_Shdr;

typedef struct {
    uint32_t   sh_name;
    uint32_t   sh_type;
    uint64_t   sh_flags;
    Elf64_Addr sh_addr;
    Elf64_Off  sh_offset;
    uint64_t   sh_size;
    uint32_t   sh_link;
    uint32_t   sh_info;
    uint64_t   sh_addralign;
    uint64_t   sh_entsize;
} Elf64_Shdr;

```
*  String and symbol tables
```c
typedef struct {
    uint32_t      st_name;
    Elf32_Addr    st_value;
    uint32_t      st_size;
    unsigned char st_info;
    unsigned char st_other;
    uint16_t      st_shndx;
} Elf32_Sym;

typedef struct {
    uint32_t      st_name;
    unsigned char st_info;
    unsigned char st_other;
    uint16_t      st_shndx;
    Elf64_Addr    st_value;
    uint64_t      st_size;
} Elf64_Sym;

```

### 常用的工具

`GNU Binutils` 是用来处理许多格式的目标文件(包括elf文件)一整套的编程语言工具程序，包括：

* readelf
  显示elf文件

* objdump
  显示elf和object格式文件，解码elf文件中高级语言语句所对应的机器语言语句段落，汇编语言语句段落

* nm
  显示elf文件中变量名和地址 

* strings
  打印文件中的可打印字符的字符串。
  在开发软件的时候，各种文本/ASCII 信息会被添加到其中，比如打印信息、调试信息、帮助信息、错误等。只要这些信息都存在于二进制文件中，就可以用 `strings` 命令将其转储到屏幕上。

* ldd 
  打印共享对象依赖关系。
  对动态链接的二进制文件运行该命令会显示出所有依赖库和它们的路径。


