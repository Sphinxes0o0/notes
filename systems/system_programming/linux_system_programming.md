# Linux 系统编程综合指南

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

## 存储器金字塔结构

《Computer Systems: A Programmer's Perspective》 中的 Chapter 6 The Memory Hierarchy 详细介绍了计算机系统中的内存层次结构。

受限于存储介质的存取速率和成本，现代计算机的存储结构呈现为金字塔型。越往塔顶，存取效率越高、但成本也越高，所以容量也就越小。
得益于程序访问的局部性原理，这种节省成本的做法也能取得不俗的运行效率。从存储器的层次结构以及计算机对数据的处理方式来看，上层一般作为下层的Cache层来使用（广义上的Cache）。
比如寄存器缓存CPU Cache的数据，CPU Cache L1~L3层视具体实现彼此缓存或直接缓存内存的数据，而内存往往缓存来自本地磁盘的数据。

## Linux 中的I/O buffering

当程序调用各类文件操作函数后，用户数据（User Data）到达磁盘（Disk）的流程如图所示。
图中描述了Linux下文件操作函数的层级关系和内存缓存层的存在位置。
中间的黑色实线是用户态和内核态的分界线。

从上往下分析这张图，首先是C语言stdio库定义的相关文件操作函数，这些都是用户态实现的跨平台封装函数。
stdio中实现的文件操作函数有自己的stdio buffer，这是在用户态实现的缓存。此处使用缓存的原因很简单——系统调用总是昂贵的。
如果用户代码以较小的size不断的读或写文件的话，stdio库将多次的读或者写操作通过buffer进行聚合可以提高程序运行效率。stdio库同时也支持`fflush(3)`函数来主动的刷新buffer，主动的调用底层的系统调用立即更新buffer里的数据。
特别地，`setbuf(3)`函数可以对stdio库的用户态buffer进行设置，甚至取消buffer的使用。

系统调用的`read(2)`/`write(2)`和真实的磁盘读写之间也存在一层buffer，这里用术语Kernel buffer cache来指代这一层缓存。
在Linux下，文件的缓存习惯性的称之为Page Cache，而更低一级的设备的缓存称之为Buffer Cache。
这两个概念很容易混淆，这里简单的介绍下概念上的区别：
- **Page Cache**：用于缓存文件的内容，和文件系统比较相关。文件的内容需要映射到实际的物理磁盘，这种映射关系由文件系统来完成；
- **Buffer Cache**：用于缓存存储设备块（比如磁盘扇区）的数据，而不关心是否有文件系统的存在（文件系统的元数据缓存在Buffer Cache中）。

### Linux 内核IO栈全貌

从系统调用的接口再往下，Linux下的IO栈大致有三个层次：

- **文件系统层**：以 `write(2)` 为例，内核拷贝了`write(2)`参数指定的用户态数据到文件系统Cache中，并适时向下层同步
- **块层**：管理块设备的IO队列，对IO请求进行合并、排序
- **设备层**：通过DMA与内存直接交互，完成数据和具体设备之间的交互

Linux 中一些常见的 `buffered io`, `mmap`, `Direct IO` 在系统中的位置：

```
 +-----------------------------------------------+
 |  Application                                  |
 +-------+----------------+-----------------+----+
         |                |                 |     
Buffered |                |                 |     
IO       |                |  mmap           |     
         v                |                 |     
 +-------+---------+      |           Direct|     
 |                 |      |           IO    |     
 |File System      |      |                 |     
 +-------+---------+      |                 |     
         |                |                 |     
         v                |                 |     
 +-------+----------------+-----+           |     
 |  Page System                 |           |     
 +-------------+----------------+           |     
               |                            |     
               v                            |     
 +-------------+----------------------------+----+
 |          Block IO Layer                       |
 +-------------+----------------------------+----+
               |                            |     
               v                            v     
 +-------------+----------------------------+----+
 |        Device & Disk etc......                |
 +-----------------------------------------------+
```

### Buffered IO 读取文件的过程

传统的Buffered IO使用`read(2)`读取文件的过程：
假设要去读一个冷文件（Cache中不存在），`open(2)`打开文件后内核建立了一系列的数据结构，接下来调用`read(2)`，到达文件系统这一层，发现Page Cache中不存在该位置的磁盘映射，
然后创建相应的Page Cache并和相关的扇区关联。
然后请求继续到达块设备层，在IO队列里排队，接受一系列的调度后到达设备驱动层，此时一般使用DMA方式读取相应的磁盘扇区到Cache中，然后`read(2)`拷贝数据到用户提供的用户态buffer中去（`read(2)`的参数指定的）。

### 整个过程的数据拷贝次数

从磁盘到Page Cache算第一次的话，从Page Cache到用户态buffer就是第二次了。

- **mmap(2)做了什么？**  
`mmap(2)`直接把Page Cache映射到了用户态的地址空间里，所以`mmap(2)`的方式读文件是没有第二次拷贝过程的。

- **Direct IO做了什么？**  
这个机制更直接，让用户态和块IO层直接对接，直接放弃Page Cache，从磁盘直接和用户态拷贝数据。

  - **好处是什么？**写操作直接映射进程的buffer到磁盘扇区，以DMA的方式传输数据，减少了原本需要到Page Cache层的一次拷贝，提升了写的效率。对于读而言，第一次肯定也是快于传统的方式的，但是之后的读就不如传统方式了（当然也可以在用户态自己做Cache，有些商用数据库就是这么做的）。

除了传统的Buffered IO可以比较自由的用偏移+长度的方式读写文件之外，`mmap(2)`和Direct IO均有数据按页对齐的要求，Direct IO还限制读写必须是底层存储设备块大小的整数倍（甚至Linux 2.4还要求是文件系统逻辑块的整数倍）。
所以接口越来越底层，换来表面上的效率提升的背后，需要在应用程序这一层做更多的事情。

## Page Cache 的同步

一般意义上Cache的同步方式有两种，即Write Through（写穿）和Write back（写回）。
从名字上就能看出这两种方式都是从写操作的不同处理方式引出的概念（纯读的话就不存在Cache一致性了）。
对应到Linux的Page Cache上，所谓Write Through就是指`write(2)`操作将数据拷贝到Page Cache后立即和下层进行同步的写操作，完成下层的更新后才返回。
而Write back正好相反，指的是写完Page Cache就可以返回了。Page Cache到下层的更新操作是异步进行的。

Linux下Buffered IO默认使用的是Write back机制，即文件操作的写只写到Page Cache就返回，之后Page Cache到磁盘的更新操作是异步进行的。
Page Cache中被修改的内存页称之为脏页（Dirty Page），脏页在特定的时候被内核的writeback线程（在较新的内核中替代了之前的pdflush线程）写入磁盘，写入的时机和条件如下：

- 当空闲内存低于一个特定的阈值时，内核必须将脏页写回磁盘，以便释放内存。
- 当脏页在内存中驻留时间超过一个特定的阈值时，内核必须将超时的脏页写回磁盘。
- 用户进程调用`sync(2)`、`fsync(2)`、`fdatasync(2)`系统调用时，内核会执行相应的写回操作。

刷新策略由以下几个参数决定（数值单位均为1/100秒）：

```bash
# writeback每隔5秒执行一次
$ sysctl vm.dirty_writeback_centisecs
vm.dirty_writeback_centisecs = 500

# 内存中驻留30秒以上的脏数据将由writeback在下一次执行时写入磁盘
$ sysctl vm.dirty_expire_centisecs
vm.dirty_expire_centisecs = 3000

# 若脏页占总物理内存10％以上，则触发writeback把脏数据写回磁盘
$ sysctl vm.dirty_background_ratio
vm.dirty_background_ratio = 10

# 当脏页占总物理内存20%以上时，进程会被阻塞直到writeback完成
$ sysctl vm.dirty_ratio
vm.dirty_ratio = 20
```

## 文件操作与锁

当多个进程/线程对同一个文件发生写操作的时候会发生什么？如果写的是文件的同一个位置呢？
这个问题讨论起来有点复杂了。首先`write(2)`调用不是原子操作，不要被TLPI的中文版5.2章节的第一句话误导了（英文版也是有歧义的，作者在这里给出了勘误信息）。
当多个`write(2)`操作对一个文件的同一部分发起写操作的时候，情况实际上和多个线程访问共享的变量没有什么区别。按照不同的逻辑执行流，会有很多种可能的结果。
也许大多数情况下符合预期，但是本质上这样的代码是不可靠的。

特别的，文件操作中有两个操作是内核保证原子的。分别是`open(2)`调用的`O_CREAT`和`O_APPEND`这两个flag属性。
前者是文件不存在就创建，后者是每次写文件时把文件游标移动到文件最后追加写（NFS等文件系统不保证这个flag）。
有意思的问题来了，以`O_APPEND`方式打开的文件`write(2)`操作是不是原子的？文件游标的移动和调用写操作是原子的，但是写操作本身的数据写入过程不是原子的。

### 文件锁的类型

Linux下的文件锁有两种，分别是`flock(2)`的方式和`fcntl(2)`的方式，前者源于BSD，后者源于System V，各有限制和应用场景：

#### flock(2) - BSD风格文件锁
- **特点**：简单易用，锁定整个文件
- **锁的类型**：共享锁（LOCK_SH）和排它锁（LOCK_EX）
- **作用域**：只在本地文件系统有效，NFS等网络文件系统不支持
- **继承性**：子进程不继承父进程的锁

#### fcntl(2) - POSIX文件锁
- **特点**：功能更强大，可以锁定文件的特定区域
- **锁的类型**：读锁（F_RDLCK）和写锁（F_WRLCK）
- **作用域**：支持网络文件系统
- **继承性**：子进程继承父进程的锁
- **死锁检测**：内核提供基本的死锁检测

### 现代I/O技术补充

随着硬件发展，Linux内核也引入了一些新的I/O技术：

#### io_uring
- **特点**：异步I/O接口，减少系统调用开销
- **优势**：高性能，特别适合高并发场景
- **应用**：现代数据库和高性能服务器

#### 多队列块层 (Multi-Queue Block Layer)
- **特点**：利用多核CPU并行处理I/O请求
- **优势**：显著提升SSD等高速存储设备的性能

# 网络IO模型

网络IO模型主要用于描述如何处理输入和输出操作，特别是在涉及网络通信时的数据传输方式。传统上，有五种主要的网络IO模型，它们分别是：

## 1. 阻塞IO（Blocking IO）

在这个模型中，应用程序执行一个IO操作（例如，读取网络数据），该调用会阻塞，直到操作完成。在数据从网络到达并且被复制到应用程序缓冲区之前，应用程序不会继续执行。大部分传统的网络应用使用阻塞IO模型。
```
应用程序                   内核  
    |--- read() ----------->|  
    |                       |  
    |<---- 数据可用 ---------|  
    |                       |  
    |<---- read() 完成 -----|  
```
当客户端请求到达时，服务器执行一个阻塞的read()调用，等待客户端发送请求数据。
在这个过程中，服务器不能做任何其他事情。

## 2. 非阻塞IO（Non-blocking IO）

非阻塞IO模型允许应用程序发出IO操作后立即返回，即使操作尚未完成。如果数据尚未准备好，调用会返回一个错误码，通常是EWOULDBLOCK或EAGAIN。应用程序可以继续做其他工作，但它必须定期轮询IO操作，以确定数据是否已准备好。
```
应用程序                   内核
    |                       |
    |---- read() ---------->|
    |<--- EWOULDBLOCK ------|
    |                       |
    |       ... (等待)       |
    |---- read() ---------->|
    |<--- EWOULDBLOCK ------|
    |                       |
    |       ... (等待)      |
    |---- read() ---------->|
    |<----- 数据可用 --------|
    |                       |
 ```
一个使用非阻塞套接字的网络应用程序，它在读取数据时不断轮询。
如果read()调用发现没有数据可读，它会立即返回EWOULDBLOCK。
应用程序可以在轮询期间执行其他任务。

## 3. IO复用（IO Multiplexing）

IO复用使用select或poll系统调用，允许应用程序监视多个IO流（文件描述符）的就绪状态。应用程序在一个单独的阻塞调用中等待多个IO操作中的任何一个完成。当select或poll调用返回时，应用程序可以执行IO操作，而无需担心阻塞，因为已知至少有一个IO操作是准备好的。
```
应用程序                   内核
    |                      |
    |--- select() -------->|
    |                      |
    |                      |--- 等待多个
    |                      |    文件描述符
    |<--- 有描述符就绪 -----|
    |                      |
    |--- read() ---------->|
    |<---- 数据可用 --------|
    |                      |
```
服务器使用select()调用来监视多个连接。
当有客户端发送数据时，select()会返回，服务器就知道可以从哪个套接字读取数据而不会阻塞。

## 4. 信号驱动IO（Signal-driven IO）

信号驱动IO允许应用程序为一个IO操作安装一个信号处理器，然后继续执行，而不是等待IO完成。当数据准备好可以进行IO操作时，应用程序会收到一个SIGIO信号，然后可以处理IO操作而不会被阻塞。
```
应用程序                   内核
    |                      |
    |--- sigaction() ----->|
    |                      |
    |--- read() ---------->|
    |                      |
    |                       --- 等待数据 ---
    |                      |
    |<----- SIGIO ---------|
    |                      |
    |--- read() ---------->|
    |<---- 数据可用 --------|
    |                      |
```
应用程序使用sigaction()设置一个信号处理程序来处理SIGIO，然后继续执行，
当数据到达并准备好被读取时，内核发送SIGIO信号，应用程序响应信号并读取数据。

## 5. 异步IO（Asynchronous IO）

在异步IO模型中，应用程序发起一个IO操作后可以立即开始执行其他任务。与信号驱动IO不同，异步IO的操作会在整个操作完成后通知应用程序。应用程序不需要在IO完成后立即处理数据，因为操作系统会在后台处理所有的IO操作。
```
应用程序                   内核
    |                      |
    |--- aio_read() ------>|
    |                      |
    |                       --- 执行读操作 ---
    |                      |
    |                      |--- 读操作完成
    |<---- 通知完成 --------|
    |                      |
```
应用程序发起一个aio_read()操作，并立即继续执行其他代码。
当读操作实际完成时，应用程序会收到一个通知，这可能是通过信号或其他异步通知机制。

# Reactor & Proactor 模型

## Reactor模型

Reactor模型是基于事件驱动机制的，它使用非阻塞I/O操作。
在这个模型中，主要有一个Reactor（或者事件循环），它负责监听和分发事件。
事件通常是I/O操作，比如读或写操作准备就绪可以进行处理。
当Reactor检测到一个或多个I/O事件的时候，它会相应地通知相关的处理程序（Handlers）来处理这些事件。

Reactor模型的ASCII流程图如下：

```
[ 应用程序 ]       [ Reactor ]        [ Handlers ]
    |                  |                   |
    | 注册处理程序      |                   |
    |----------------->|                   |
    |                  |                   |
    |                  | 监听事件           |
    |                  |<------------------>|
    |                  |                   |
    |                  | 事件就绪           |
    |                  |------------------>|
    |                  |                   |-> 处理事件
    |                  |                   |
    |                  |<------------------|
```

### 处理流程

1. 应用程序启动并注册需要处理的事件及其对应的处理程序到Reactor。
2. Reactor负责监听事件，它通常是一个无限循环，等待事件的发生（如，使用select, poll, 或epoll）。
3. 当一个事件就绪（比如，一个socket可读），Reactor就将事件分发给之前注册的对应处理程序。
4. 处理程序执行非阻塞操作来处理事件（例如，读取数据、处理数据、发送响应等）。

### 组件

首先来回想一下普通函数调用的机制：  
程序调用某函数，函数执行，程序等待，函数将结果和控制权返回给程序，程序继续处理。

和普通函数调用的不同之处在于：  
应用程序不是主动的调用某个 API 完成处理，而是恰恰相反，Reactor 逆置了事件处理流程，应用程序需要提供相应的接口并注册到 Reactor 上，如果相应的时间发生，Reactor 将主动调用应用程序注册的接口，这些接口又称为"回调函数"。

Reactor 模型有三个重要的组件：
* 多路复用器：由操作系统提供，在 linux 上一般是 select, poll, epoll 等系统调用。
* 事件分发器：将多路复用器中返回的就绪事件分到对应的处理函数中。
* 事件处理器：负责处理特定事件的处理函数。

具体流程如下：
1. 注册读就绪事件和相应的事件处理器；
2. 事件分离器等待事件；
3. 事件到来，激活分离器，分离器调用事件对应的处理器；
4. 事件处理器完成实际的读操作，处理读到的数据，注册新的事件，然后返还控制权。

### Reactor优缺点

Reactor 模式是编写高性能网络服务器的必备技术之一，它具有如下的优点：
* 响应快，不必为单个同步时间所阻塞，虽然 Reactor 本身依然是同步的；
* 编程相对简单，可以最大程度的避免复杂的多线程及同步问题，并且避免了多线程/进程的切换开销；
* 可扩展性，可以方便的通过增加 Reactor 实例个数来充分利用 CPU 资源；
* 可复用性，reactor 框架本身与具体事件处理逻辑无关，具有很高的复用性；

Reactor 模型开发效率上比起直接使用 IO 复用要高，它通常是单线程的，设计目标是希望单线程使用一颗 CPU 的全部资源，但也有附带优点，即每个事件处理中很多时候可以不考虑共享资源的互斥访问。
可是缺点也是明显的，现在的硬件发展，已经不再遵循摩尔定律，CPU 的频率受制于材料的限制不再有大的提升，而改为是从核数的增加上提升能力，当程序需要使用多核资源时，Reactor 模型就会悲剧。

## Proactor模型

Proactor模型是异步I/O（AIO）操作的模型。
在这个模型中，应用程序会发起一个异步I/O操作，并立即返回，继续执行其他任务。
当I/O操作实际完成时，操作系统会通知应用程序，这时应用程序会调用相应的完成处理程序（Completion Handler）来处理I/O操作的结果。

Proactor模型的ASCII流程图如下：

```
[ 应用程序 ]       [ OS/AIO Subsystem ]       [ Completion Handlers ]
     |                       |                             |
     | 发起异步I/O操作        |                             |
     |---------------------->|                             |
     |                       |                             |
     |                       | 完成I/O操作                  |
     |                       |---------------------------->|
     |                       |                             |-> 处理完成的I/O
     |                       |                             |
     |<----------------------|                             |
     | 通知I/O完成            |                             |
```

### 处理流程

具体流程如下：
1. 处理器发起异步操作，并关注 I/O 完成事件
2. 事件分离器等待操作完成事件
3. 分离器等待过程中，内核并行执行实际的 I/O 操作，并将结果数据存入用户自定义缓冲区，最后通知事件分离器读操作完成
4. I/O 完成后，通过事件分离器呼唤处理器
5. 事件处理器处理用户自定义缓冲区中的数据

从上面的处理流程，可以发现 proactor 模型最大的特点就是使用异步 I/O。
所有的 I/O 操作都交由系统提供的异步 I/O 接口去执行。工作线程仅仅负责业务逻辑。

在 Proactor 中，用户函数启动一个异步的文件操作。同时将这个操作注册到多路复用器上。
多路复用器并不关心文件是否可读或可写而是关心这个异步读操作是否完成。
异步操作是操作系统完成，用户程序不需要关心。多路复用器等待直到有完成通知到来。
当操作系统完成了读文件操作——将读到的数据复制到了用户先前提供的缓冲区之后，通知多路复用器相关操作已完成。多路复用器再调用相应的处理程序，处理数据。

Proactor 增加了编程的复杂度，但给工作线程带来了更高的效率。Proactor 可以在系统态将读写优化，利用 I/O 并行能力，提供一个高性能单线程模型。
在 windows 上，由于没有 epoll 这样的机制，因此提供了 IOCP 来支持高并发， 由于操作系统做了较好的优化，windows 较常采用 Proactor 的模型利用完成端口来实现服务器。
在 linux 上，2.6 内核出现了 aio 接口，但 aio 实际效果并不理想，它的出现，主要是解决 poll 性能不佳的问题，但实际上经过测试，epoll 的性能高于 poll+aio，并且 aio 不能处理 accept，因此 linux 主要还是以 Reactor 模型为主。

在不使用操作系统提供的异步 I/O 接口的情况下，还可以使用 Reactor 来模拟 Proactor，差别是：

使用异步接口可以利用系统提供的读写并行能力，而在模拟的情况下，这需要在用户态实现。具体的做法只需要这样：
1. 注册读事件（同时再提供一段缓冲区）
2. 事件分离器等待可读事件
3. 事件到来，激活分离器，分离器（立即读数据，写缓冲区）调用事件处理器
4. 事件处理器处理数据，删除事件(需要再用异步接口注册)

Boost.asio 库采用的即为 Proactor 模型。不过 Boost.asio 库在 Linux 平台采用epoll 实现的 Reactor 来模拟 Proactor，并且另外开了一个线程来完成读写调度。

#### 同步 I/O 模拟 Proactor 模型

流程如下：
1. 主线程往 epoll 内核事件表中注册 socket 上的读就绪事件。
2. 主线程调用 epoll_wait 等待 socket 上有数据可读。
3. 当 socket 上有数据可读时，epoll_wait 通知主线程。主线程从 socket 循环读取数据，直到没有更多数据可读，然后将读取到的数据封装成一个请求对象并插入请求队列。
4. 睡眠在请求队列上的某个工作线程被唤醒，它获得请求对象并处理客户请求，然后往 epoll 内核事件表中注册 socket 上的写就绪事件。
5. 主线程调用 epoll_wait 等待 socket 可写。
6. 当 socket 可写时，epoll_wait 通知主线程。主线程往 socket 上写入服务器处理客户请求的结果。

## 对比

两个模式的相同点，都是对某个 IO 事件的事件通知(即告诉某个模块，这个 IO 操作可以进行或已经完成)。
在结构上两者也有相同点：demultiplexor 负责提交 IO 操作(异步)、查询设备是否可操作(同步)，然后当条件满足时，就回调注册处理函数。

不同点在于，异步情况下(Proactor)，当回调注册的处理函数时，表示 IO 操作已经完成；
同步情况下(Reactor)，回调注册的处理函数时，表示 IO 设备可以进行某个操作(can read or can write)，注册的处理函数这个时候开始提交操作。

这两个模型的关键差异在于：

* Reactor：应用程序负责在操作就绪时进行实际的I/O操作（即，Reactor通知你"可以读取或写入数据了"，然后你去执行那个操作）。

* Proactor：应用程序只需启动操作和处理结果，实际的I/O操作是由操作系统异步完成的（即，Proactor告诉你"读取或写入操作已经完成了"，然后你处理这个结果）。

# 线程编程

## 线程概述

与进程（process）类似，线程（thread）是允许应用程序并发执行多个任务的一种机制。一个进程可以包含多个线程。
同一个程序中的所有线程均会独立执行相同程序，且共享同一份全局内存区域，其中包括初始化数据段、未初始化数据段，以及堆内存段。（传统意义上的 UNIX 进程只是多线程程序的一个特例，该进程只包含一个线程）

- 进程是 CPU 分配资源的最小单位，线程是操作系统调度执行的最小单位。
- 线程是轻量级的进程（LWP：Light Weight Process），`在 Linux 环境下线程的本质仍是进程`。
- 查看指定进程的 LWP 号：ps –Lf pid

### 线程和进程区别

- 进程间的信息难以共享。由于除去只读代码段外，父子进程并未共享内存，因此必须采用一些进程间通信方式，在进程间进行信息交换。

- 调用 fork() 来创建进程的代价相对较高，即便利用写时复制技术，仍然需要复制诸如内存页表和文件描述符表之类的多种进程属性，这意味着 fork() 调用在时间上的开销依然不菲。

- 线程之间能够方便、快速地共享信息。只需将数据复制到共享（全局或堆）变量中即可。

- 创建线程比创建进程通常要快 10 倍甚至更多。线程间是共享虚拟地址空间的，无需采用写时复制来复制内存，也无需复制页表。

### 线程之间共享和非共享资源

- 共享资源
    - 进程 ID 和父进程 ID
    - 进程组 ID 和会话 ID
    - 用户 ID 和 用户组 ID
    - 文件描述符表
    - 信号处置
    - 文件系统的相关信息：文件权限掩码（umask）、当前工作目录
    - 虚拟地址空间（除栈、.text） 

- 非共享资源
    - 线程 ID
    - 信号掩码
    - 线程特有数据
    - error 变量
    - 实时调度策略和优先级
    - 栈，本地变量和函数的调用链接信息

## NPTL

当 Linux 最初开发时，在内核中并不能真正支持线程。

但是它的确可以通过 clone() 系统调用将进程作为可调度的实体。这个调用创建了调用进程（calling process）的一个拷贝，这个拷贝与调用进程共享相同的地址空间。LinuxThreads 项目使用这个调用来完成在用户空间模拟对线程的支持。
不幸的是，这种方法有一些缺点，尤其是在信号处理、调度和进程间同步等方面都存在问题。另外，这个线程模型也不符合 POSIX 的要求。

- 要改进 LinuxThreads，需要内核的支持，并且重写线程库。有两个相互竞争的项目开始来满足这些要求。一个包括 IBM 的开发人员的团队开展了 NGPT（Next-Generation POSIX Threads）项目。同时，Red Hat 的一些开发人员开展了 NPTL 项目。NGPT 在 2003 年中期被放弃了，把这个领域完全留给了 NPTL。

- NPTL，或称为 Native POSIX Thread Library，是 Linux 线程的一个新实现，它克服了 LinuxThreads 的缺点，同时也符合 POSIX 的需求。与 LinuxThreads 相比，它在性能和稳定性方面都提供了重大的改进。

- 查看当前 pthread 库版本：getconf GNU_LIBPTHREAD_VERSION

## 线程创建函数

- int pthread_create(pthread_t *thread, const pthread_attr_t *attr, void *(*start_routine) (void *), void *arg);
- pthread_t pthread_self(void);
- int pthread_equal(pthread_t t1, pthread_t t2);
- void pthread_exit(void *retval);
- int pthread_join(pthread_t thread, void **retval);
- int pthread_detach(pthread_t thread);
- int pthread_cancel(pthread_t thread);

### 线程属性函数

* 线程属性类型 pthread_attr_t
* int pthread_attr_init(pthread_attr_t *attr);
* int pthread_attr_destroy(pthread_attr_t *attr);
* int pthread_attr_getdetachstate(const pthread_attr_t *attr, int *detachstate);
* int pthread_attr_setdetachstate(pthread_attr_t *attr, int detachstate);

## 线程同步

即当有一个线程在对内存进行操作时，其他线程都不可以对这个内存地址进行操作，直到该线程完成操作，其他线程才能对该内存地址进行操作，而其他线程则处于等待状态。

> 线程的主要优势在于，能够通过全局变量来共享信息。不过，这种便捷的共享是有代价的：必须确保多个线程不会同时修改同一变量，或者某一线程不会读取正在由其他线程修改的变量。

> 临界区是指访问某一共享资源的代码片段，并且这段代码的执行应为原子操作，也就是同时访问同一共享资源的其他线程不应终断该片段的执行。

### 互斥量

为避免线程更新共享变量时出现问题，可以使用互斥量（mutex 是 mutual exclusion的缩写）来确保同时仅有一个线程可以访问某项共享资源。可以使用互斥量来保证对任意共享资源的原子访问。

* 互斥量有两种状态：
    - 已锁定（locked）
    - 未锁定（unlocked）。
    任何时候，至多只有一个线程可以锁定该互斥量。试图对已经锁定的某一互斥量再次加锁，将可能阻塞线程或者报错失败，具体取决于加锁时使用的方法。

* 一旦线程锁定互斥量，随即成为该互斥量的所有者，只有所有者才能给互斥量解锁。一般情况下，对每一共享资源（可能由多个相关变量组成）会使用不同的互斥量，每一线程在访问同一资源时将采用如下协议：
    - 针对共享资源锁定互斥量
    - 访问共享资源
    - 对互斥量解锁

### 死锁

- 有时，一个线程需要同时访问两个或更多不同的共享资源，而每个资源又都由不同的互斥量管理。当超过一个线程加锁同一组互斥量时，就有可能发生死锁。

- 两个或两个以上的进程在执行过程中，因争夺共享资源而造成的一种互相等待的现象，若无外力作用，它们都将无法推进下去。此时称系统处于死锁状态或统产生了死锁。

- 死锁的几种场景：
    - 忘记释放锁
    - 重复加锁
    - 多线程多锁，抢占锁资源

#### 互斥量相关操作函数

- 互斥量的类型 pthread_mutex_t
- int pthread_mutex_init(pthread_mutex_t *restrict mutex, const pthread_mutexattr_t *restrict attr);
- int pthread_mutex_destroy(pthread_mutex_t *mutex);
- int pthread_mutex_lock(pthread_mutex_t *mutex);
- int pthread_mutex_trylock(pthread_mutex_t *mutex);
- int pthread_mutex_unlock(pthread_mutex_t *mutex);

### 读写锁

- 当有一个线程已经持有互斥锁时，互斥锁将所有试图进入临界区的线程都阻塞住。但是考虑一种情形，当前持有互斥锁的线程只是要读访问共享资源，而同时有其它几个线程也想读取这个共享资源，但是由于互斥锁的排它性，所有其它线程都无法获取锁，也就无法读访问共享资源了，但是实际上多个线程同时读访问共享资源并不会导致问题。
- 在对数据的读写操作中，更多的是读操作，写操作较少，例如对数据库数据的读写应用。为了满足当前能够允许多个读出，但只允许一个写入的需求，线程提供了读写锁来实现。
- 读写锁的特点：
    - 如果有其它线程读数据，则允许其它线程执行读操作，但不允许写操作。
    - 如果有其它线程写数据，则其它线程都不允许读、写操作。
    - 写是独占的，写的优先级高。

#### 读写锁相关操作函数

- 读写锁的类型 pthread_rwlock_t
- int pthread_rwlock_init(pthread_rwlock_t *restrict rwlock, const pthread_rwlockattr_t *restrict attr);
- int pthread_rwlock_destroy(pthread_rwlock_t *rwlock);
- int pthread_rwlock_rdlock(pthread_rwlock_t *rwlock);
- int pthread_rwlock_tryrdlock(pthread_rwlock_t *rwlock);
- int pthread_rwlock_wrlock(pthread_rwlock_t *rwlock);
- int pthread_rwlock_trywrlock(pthread_rwlock_t *rwlock);
- int pthread_rwlock_unlock(pthread_rwlock_t *rwlock);

### 信号量

- 信号量的类型 sem_t
- int sem_init(sem_t *sem, int pshared, unsigned int value);
- int sem_destroy(sem_t *sem);
- int sem_wait(sem_t *sem);
- int sem_trywait(sem_t *sem);
- int sem_timedwait(sem_t *sem, const struct timespec *abs_timeout);
- int sem_post(sem_t *sem);
- int sem_getvalue(sem_t *sem, int *sval);

### RCU

RCU锁是读写锁的扩展版本，简单来说就是支持多读多写同时加锁，但是对于多写同时加锁，还是存在一些技术挑战的。

RCU锁翻译为 `Read Copy Update Lock`:
- Copy ：写者在访问临界区时，写者将先拷贝一个临界区副本，然后对副本进行修改；
- Update ：RCU机制将在在适当时机使用一个回调函数把指向原来临界区的指针重新指向新的被修改的临界区，锁机制中的垃圾收集器负责回调函数的调用。

> 更新时机：没有CPU再去操作这段被RCU保护的临界区后，这段临界区即可回收了，此时回调函数即被调用。

从实现逻辑来看，RCU锁在多个写者之间的同步开销还是比较大的，涉及到多份数据拷贝，回调函数等，因此这种锁机制的使用范围比较窄，适用于读多写少的情况，如网络路由表的查询更新、设备状态表更新等，在业务开发中使用不是很多。

### 条件变量

条件变量是用来等待线程而不是上锁的，通常和互斥锁一起使用。
互斥锁的一个明显的特点就是某些业务场景中无法借助系统来唤醒，仍然需要业务代码使用while来判断，这样效率本质上比较低。
而条件变量通过允许线程阻塞和等待另一个线程发送信号来弥补互斥锁的不足，所以互斥锁和条件变量通常一起使用，来让条件变量异步唤醒阻塞的线程。

- 条件变量的类型 pthread_cond_t
- int pthread_cond_init(pthread_cond_t *restrict cond, const pthread_condattr_t *restrict attr);
- int pthread_cond_destroy(pthread_cond_t *cond);
- int pthread_cond_wait(pthread_cond_t *restrict cond, pthread_mutex_t *restrict mutex);
- int pthread_cond_timedwait(pthread_cond_t *restrict cond, pthread_mutex_t *restrict mutex, const struct timespec *restrict abstime);
- int pthread_cond_signal(pthread_cond_t *cond);
- int pthread_cond_broadcast(pthread_cond_t *cond);

### 自旋锁 Spin Lock

自旋锁的主要特征是使用者在想要获得临界区执行权限时，如果临界区已经被加锁，那么自旋锁并不会阻塞睡眠，等待系统来主动唤醒，而是原地忙轮询资源是否被释放加锁;
自旋锁有它的优点就是避免了系统的唤醒，自己来执行轮询，如果在临界区的资源代码非常短且是原子的，那么使用起来是非常方便的，避免了各种上下文切换，开销非常小，因此在内核的一些数据结构中自旋锁被广泛的使用。

### 可重入锁和不可重入锁

- 递归锁recursive mutex 可重入锁(reentrant mutex)
- 非递归锁non-recursive mutex 不可重入锁(non-reentrant mutex)

### 生产/消费者模型实例

```C
#include <stdio.h>
#include <pthread.h>
#define MAX 5

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t notfull = PTHREAD_COND_INITIALIZER;  //是否队满
pthread_cond_t notempty = PTHREAD_COND_INITIALIZER; //是否队空
int top = 0;
int bottom = 0;

void* produce(void* arg)
{
    int i;
    for ( i = 0; i < MAX*2; i++)
    {
        pthread_mutex_lock(&mutex);
        while ((top+1)%MAX == bottom)
        {
            printf("full! producer is waiting\n");
            //等待队不满
            pthread_cond_wait(notfull, &mutex);
        }
        top = (top+1) % MAX;
        //发出队非空的消息
        pthread_cond_signal(notempty);
        pthread_mutex_unlock(&mutex);
    }
    return (void*)1;
}
void* consume(void* arg)
{
    int i;
    for ( i = 0; i < MAX*2; i++)
    {
        pthread_mutex_lock(&mutex);
        while ( top%MAX == bottom)
        {
            printf("empty! consumer is waiting\n");
            //等待队不空
            pthread_cond_wait(notempty, &mutex);
        }
        bottom = (bottom+1) % MAX;
        //发出队不满的消息
        pthread_cond_signal(notfull);
        pthread_mutex_unlock(&mutex);
    }
    return (void*)2;
}
int main(int argc, char *argv[])
{
    pthread_t thid1;
    pthread_t thid2;
    pthread_t thid3;
    pthread_t thid4;

    int ret1;
    int ret2;
    int ret3;
    int ret4;

    pthread_create(&thid1, NULL, produce, NULL);
    pthread_create(&thid2, NULL, consume, NULL);
    pthread_create(&thid3, NULL, produce, NULL);
    pthread_create(&thid4, NULL, consume, NULL);

    pthread_join(thid1, (void**)&ret1);
    pthread_join(thid2, (void**)&ret2);
    pthread_join(thid3, (void**)&ret3);
    pthread_join(thid4, (void**)&ret4);
    return 0;
}
```

## 总结

Linux的I/O子系统和线程编程是一个复杂而精妙的系统，通过多层缓存和异步机制来平衡性能和一致性。理解这些机制对于编写高性能应用程序至关重要：

1. **选择合适的I/O方式**：根据应用场景选择Buffered I/O、mmap或Direct I/O
2. **合理使用缓存**：理解Page Cache的工作机制，避免不必要的同步操作
3. **注意并发安全**：使用适当的文件锁机制保证数据一致性
4. **选择合适的I/O模型**：根据并发需求选择阻塞、非阻塞、I/O复用、信号驱动或异步I/O
5. **正确使用线程同步机制**：合理使用互斥量、读写锁、信号量等同步原语
6. **关注新技术**：如io_uring等新技术可以显著提升I/O性能

深入理解这些概念有助于开发者写出更高效、更可靠的系统级程序。
