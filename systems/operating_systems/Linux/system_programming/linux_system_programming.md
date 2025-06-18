---
title: linux_system_programming
date: 2021-11-20 19:22:00
tags:
    - Linux
    - C
categories:
    - Linux编程
---

## 系统调用
在深入系统调用的运作方式之前，务必关注以下几点。
* 系统调用将处理器从用户态切换到核心态，以便 CPU 访问受到保护的内核内存。

* 系统调用的组成是固定的，每个系统调用都由一个唯一的数字来标识。
（程序通过名称来标识系统调用，对这一编号方案往往一无所知。）

* 每个系统调用可辅之以一套参数，对用户空间（亦即进程的虚拟地址空间）与内核空
间之间（相互）传递的信息加以规范。

从编程角度来看，系统调用与 C 语言函数的调用很相似。然而，在执行系统调用时，其
幕后会历经诸多步骤。为说明这点，下面以一个具体的硬件平台—x86-32 为例，按事件发
生的顺序对这些步骤加以分析。
1． 应用程序通过调用 C 语言函数库中的外壳（wrapper）函数，来发起系统调用。

2． 对系统调用中断处理例程（稍后介绍）来说，外壳函数必须保证所有的系统调用参数可用。
通过堆栈，这些参数传入外壳函数，但内核却希望将这些参数置入特定寄存器。
因此，外壳函数会将上述参数复制到寄存器。

3． 由于所有系统调用进入内核的方式相同，内核需要设法区分每个系统调用。为此，外壳函
数会将系统调用编号复制到一个特殊的 CPU 寄存器（%eax）中。

4． 外壳函数执行一条中断机器指令（int 0x80），引发处理器从用户态切换到核心态，并执行
系统中断 0x80 (十进制数 128)的中断矢量所指向的代码。

5． 为响应中断 0x80，内核会调用 system_call()例程（位于汇编文件 arch/i386/entry.S 中）来
处理这次中断，具体如下。
    a）在内核栈中保存寄存器值（参见 6.5 节）。 他
    b）审核系统调用编号的有效性。
    c）以系统调用编号对存放所有调用服务例程的列表（内核变量 sys_call_table）进行索引，
    发现并调用相应的系统调用服务例程。若系统调用服务例程带有参数，那么将首先检查参数的有效性。
    例如，会检查地址指向用户空间的内存位置是否有效。随后，该服务例程会执行必要的任务，这可能涉及对特定参数中指定地址处的值进行修改，以及在用户内存和内核内存间传递数据（比如，在 I/O 操作中）。
    最后，该服务例程会将结果状态返回给 system_call()例程。
    d）从内核栈中恢复各寄存器值，并将系统调用返回值置于栈中。
    e）返回至外壳函数，同时将处理器切换回用户态。

6． 若系统调用服务例程的返回值表明调用有误，外壳函数会使用该值来设置全局变量 errno
（参见 3.4 节）。然后，外壳函数会返回到调用程序，并同时返回一个整型值，以表明系统
调用是否成功。

![execve](imgs/linux_system_exec_steps.png)


## 文件I/O

所有执行 I/O 操作的系统调用都以文件描述符，一个非负整数（通常是小整数），来指代打开的文件。
文件描述符用以表示所有类型的已打开文件，包括管道（pipe）、FIFO、socket、终端、
设备和普通文件。针对每个进程，文件描述符都自成一套。

大多数程序都能够使用 3 种标准的文件描述符：

| 描述符 | 用途       | POSIX         | stdio  |
| ----- | --------- | ------------- | ------ |
| 0     | 标准输入    | STDIN_FILENO  | stdin  |
| 1     | 标准输出    | STDOUT_FILENO | stdout |
| 2     | 标准错误    | STDERR_FILENO | stderr |

> 程序中指代这些文件描述符时，可以使用数字（0、1、2）表示，但最好是采用<unistd.h>
所定义的 POSIX 标准名称。

### IO 操作的主要系统调用函数

#### open()
```c
fd = open(pathname, flags, mode)
```
函数打开 `pathname` 所标识的文件，并返回文件描
述符，用以在后续函数调用中指代打开的文件。如果文件不存在，`open()`函数可以
创建之，这取决于对位掩码参数 `flags` `的设置。flags` 参数还可指定文件的打开方式：只
`读、只写亦或是读写方式。mode` 参数则指定了由 `open()`调用创建文件的访问权限，
如果 `open()` 函数并未创建文件，那么可以忽略或省略 `mode` 参数。

```C
// open existing file for reading
fd = open("start.up", O_RDONLY);
if (fd == -1)
    printf("can't open");

// open new or existing file or reading and writing, truncating to zero
// bytes; file permissions read+write for owner, nothing for all others
fd = open("myfile", O_RDWR | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR );
if (fd == -1)
    printf("can't open");

fd = open("w.log", O_WRONLY|O_CREAT|O_TRUNC|O_APPEND, S_IRUSR|S_IWUSR);

if (fd == -1)
    printf("can't open");

```

SUSv3 规定，如果调用 open()成功，必须保证其返回值为进程未用文件描述符中数值最小者。
可以利用该特性以特定文件描述符打开某一文件。

```C
if (close(STDIN_FILENO) == -1)
    print("close");

fd = open(pathname, O_RDONLY);
if (fd == -1)
    print("open");

```


#### read()
```C
numread = read(fd, buffer, count)
```
调用从 `fd` 所指代的打开文件中读取至多 `count` 字节的数据，并存储到 `buffer` 中。
`read()`调用的返回值为实际读取到的字节数。如果再无字节可读（例如：读到文件结尾符 `EOF` 时），则返回值为 0。

#### write()
```C
numwritten = write(fd, buffer, count)
```
调用从 `buffer` 中读取多达 `count` 字节的数据写入由
`fd` 所指代的已打开文件中。`write()`调用的返回值为实际写入文件中的字节数，且有可
能小于 `count。`

#### close()
```C
status = close(fd)
```
在所有输入/输出操作完成后，调用 `close()`，释放文件描述符 `fd` 以及与之相关的内核资源。


> 使用IO 小例子(src/fileio/copy)： 
> ```C
>$ clang copy.c error_functions.c get_num.c -o copy
>$ ./copy newfile oldfile
> ```



# Others (补充)

## libc & glibc
`libc` 是 `ANSI C` 的函数库, `glibc` 是 `GNU C` 的函数库。


`ANSI C` 函数库是基本的 C 语言函数库，包含了 C 语言最基本的库函数。这个库可以根据头文件划分为 15 个部分，其中包括： 

* `<ctype.h>`：包含用来测试某个特征字符的函数的函数原型，以及用来转换大小写字母的函数原型；
* `<errno.h>`：定义用来报告错误条件的宏；
* `<float.h>`：包含系统的浮点数大小限制；
* `<math.h>`：包含数学库函数的函数原型；
* `<stddef.h>`：包含执行某些计算 C 所用的常见的函数定义；
* `<stdio.h>`：包含标准输入输出库函数的函数原型，以及他们所用的信息；
* `<stdlib.h>`：包含数字转换到文本，以及文本转换到数字的函数原型，还有内存分配、随机数字以及其他实用函数的函数原型；
* `<string.h>`：包含字符串处理函数的函数原型；
* `<time.h>`：包含时间和日期操作的函数原型和类型；
* `<stdarg.h>`：包含函数原型和宏，用于处理未知数值和类型的函数的参数列表；
* `<signal.h>`：包含函数原型和宏，用于处理程序执行期间可能出现的各种条件；
* `<setjmp.h>`：包含可以绕过一般函数调用并返回序列的函数的原型，即非局部跳转；
* `<locale.h>`：包含函数原型和其他信息，使程序可以针对所运行的地区进行修改。
 地区的表示方法可以使计算机系统处理不同的数据表达约定，如全世界的日期、时间、美元数和大数字；
* `<assert.h>`：包含宏和信息，用于进行诊断，帮助程序调试。

`glibc`是linux下面c标准库的实现，即`GNU C Library`。
`glibc`本身是GNU旗下的C标准库，后来逐渐成为了Linux的标准c库，而Linux下原来的标准c库`Linux libc`逐渐不再被维护。
Linux下面的标准c库不仅有这一个，如`uclibc`、`klibc`，以及上面被提到的`Linux libc`，但是glibc无疑是用得最多的。
`glibc`在/lib目录下的.so文件为libc.so.6。


