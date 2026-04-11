---
title: linux_ipc
date: 2022-03-21 23:41:11
tags: Linux, C
---
# 进程间通信： IPC

> key: processes , communication

* 进程是一个独立的资源分配单元:
    - 不同进程（这里所说的进程通常指的是用户进程）之间的资源是独立的，没有关联，不能在一个进程中直接访问另一个进程的资源,进程不是孤立的，
    - 不同的进程需要进行信息的交互和状态的传递等，因此需要进程间通信( IPC：Inter Processes Communication )。

* 进程间通信的目的：
    - 数据传输：一个进程需要将它的数据发送给另一个进程。
    - 通知事件：一个进程需要向另一个或一组进程发送消息，通知它（它们）发生了某种事件（如进程终止时要通知父进程）。
    - 资源共享：多个进程之间共享同样的资源。为了做到这一点，需要内核提供互斥和同步机制。
    - 进程控制：有些进程希望完全控制另一个进程的执行（如 Debug 进程），此时控制进程希望能够拦截另一个进程的所有陷入和异常，并能够及时知道它的状态改变。

* 具体方式
    - 同一主机：
        - Unix
            - 匿名管道
            - 具名管道
        - POSIX / System V
            - 消息队列
            - 共享内存
            - 信号量
    - 网络：
        - sokcet

## 管道

`ls | ws -l`： 
shell 创建了2个进程来分别执行 `ls` 和 `wc`:

```bash
---------------             -----------------                 -----------------
|    stdout   |             |  管道          |                 | stdin         |
| ls          |   ------>   | 字节流， 单向   |  ------>        |            wc |
|       fd  1 |             |               |                 | fd 0          |
---------------             -----------------                 -----------------
                      管道写入端            管道读取端  
      
```

特点：
* 内存中维护的缓冲器
    - 大小有限
    - 不同OS实现不用
* 具有文件的读.写操作，没有文件的实体(具名管道有文件实体)
* 一个管道是一个字节流，没有消息边界的概念，可以读取任意大小的数据
* 读取顺序和写入顺序完全一致
* 单向传递，半双工
* 一次性操作: 读取完之后就释放对应的内存
* 匿名管道仅在具有共同公共祖先的进程之间使用
* 数据结构: 环形队列(逻辑上)

### 具名管道
由于匿名管道，只能用于亲缘关系之间的进程通信，具名管道(FIFO)， 解决了这个局限。

* 具有文件实体， 但是实际数据在内核缓冲区中
* 通过名字，可以进程间通信

#### 有名管道的注意事项：
1. 一个为只读而打开一个管道的进程会阻塞，直到另外一个进程为只写打开管道
2. 一个为只写而打开一个管道的进程会阻塞，直到另外一个进程为只读打开管道

读管道：
- 管道中有数据，read返回实际读到的字节数
- 管道中无数据：
	- 管道写端被全部关闭，read返回0，（相当于读到文件末尾）
	- 写端没有全部被关闭，read阻塞等待

写管道：
- 管道读端被全部关闭，进行异常终止（收到一个SIGPIPE信号）
- 管道读端没有全部关闭：
	- 管道已经满了，write会阻塞
	- 管道没有满，write将数据写入，并返回实际写入的字节数。

### Linux 实现
pipe 属于 Linux 文件系统中的一种类型：

```c
static struct file_system_type pipe_fs_type = {
	.name		= "pipefs",
	.init_fs_context = pipefs_init_fs_context,
	.kill_sb	= kill_anon_super,
};
```

在`sysctl`中的属性如下：
```c

static struct ctl_table fs_pipe_sysctls[] = {
	{
		.procname	= "pipe-max-size",
		.data		= &pipe_max_size, 
		.maxlen		= sizeof(pipe_max_size),
		.mode		= 0644,
		.proc_handler	= proc_dopipe_max_size,
	},
	{
		.procname	= "pipe-user-pages-hard",
		.data		= &pipe_user_pages_hard,
		.maxlen		= sizeof(pipe_user_pages_hard),
		.mode		= 0644,
		.proc_handler	= proc_doulongvec_minmax,
	},
	{
		.procname	= "pipe-user-pages-soft",
		.data		= &pipe_user_pages_soft,
		.maxlen		= sizeof(pipe_user_pages_soft),
		.mode		= 0644,
		.proc_handler	= proc_doulongvec_minmax,
	},
	{ }
};
```

* pipe-max-size
    - 1048576
    - `/proc/sys/fs/pipe-max-size`

在 Linux 的实现中，每一个管道至少需要有2段buffer, 一个里面要读取的数据，一个留个即将写入的数据;

实际数据结构：

```c
struct pipe_buffer {
	struct page *page;
	unsigned int offset, len;
	const struct pipe_buf_operations *ops;
	unsigned int flags;
	unsigned long private;
};
```

### 管道的读写特点：

使用管道时，需要注意以下几种特殊的情况（假设都是阻塞I/O操作）:  
1. 所有的指向管道写端的文件描述符都关闭了（管道写端引用计数为0），有进程从管道的读端
读数据，那么管道中剩余的数据被读取以后，再次read会返回0，就像读到文件末尾一样。

2. 如果有指向管道写端的文件描述符没有关闭（管道的写端引用计数大于0），而持有管道写端的进程
也没有往管道中写数据，这个时候有进程从管道中读取数据，那么管道中剩余的数据被读取后，
再次read会阻塞，直到管道中有数据可以读了才读取数据并返回。

3. 如果所有指向管道读端的文件描述符都关闭了（管道的读端引用计数为0），这个时候有进程
向管道中写数据，那么该进程会收到一个信号SIGPIPE, 通常会导致进程异常终止。

4. 如果有指向管道读端的文件描述符没有关闭（管道的读端引用计数大于0），而持有管道读端的进程
也没有从管道中读数据，这时有进程向管道中写数据，那么在管道被写满的时候再次write会阻塞，
直到管道中有空位置才能再次写入数据并返回。


总结：
- 读管道：
    - 有数据，read返回实际读到的字节数。
    - 无数据：
        写端被全部关闭，read返回0（相当于读到文件的末尾）
        写端没有完全关闭，read阻塞等待

- 写管道：
    - 全部被关闭，进程异常终止（进程收到SIGPIPE信号）
    - 没有全部关闭：
        管道已满，write阻塞
        管道没有满，write将数据写入，并返回实际写入的字节数

## 内存映射 Memory-Mapped

将磁盘文件的数据映射到内存， 用户通过修改内存就能修改磁盘文件

使用内存映射实现进程间通信：

1. 有关系的进程（父子进程）
    - 还没有子进程的时候
        - 通过唯一的父进程，先创建内存映射区
    - 有了内存映射区以后，创建子进程
    - 父子进程共享创建的内存映射区
	- 匿名映射(没有文件实体)

2. 没有关系的进程间通信
    - 准备一个大小不是0的磁盘文件
    - 进程1 通过磁盘文件创建内存映射区
        - 得到一个操作这块内存的指针
    - 进程2 通过磁盘文件创建内存映射区
        - 得到一个操作这块内存的指针
    - 使用内存映射区通信

> 注意：内存映射区通信，是非阻塞。

### Linux 调用函数

```c
void *mmap(void *addr, size_t length, int prot, int flags,int fd, off_t offset);
```

- 功能：
将一个文件或者设备的数据映射到内存中

- 参数：
	- void *addr: NULL, 由内核指定

	- length : 要映射的数据的长度，这个值不能为0。建议使用文件的长度。
		获取文件的长度：
		- stat() 
		- lseek()

	- prot : 对申请的内存映射区的操作权限
		- PROT_EXEC ：可执行的权限
		- PROT_READ ：读权限
		- PROT_WRITE ：写权限
		- PROT_NONE ：没有权限

		要操作映射内存，必须要有读的权限。
		PROT_READ、PROT_READ|PROT_WRITE

	- flags :
		- MAP_SHARED : 映射区的数据会自动和磁盘文件进行同步，进程间通信，必须要设置这个选项
		- MAP_PRIVATE ：不同步，内存映射区的数据改变了，对原来的文件不会修改，会重新创建一个新的

	- fd: 需要映射的那个文件的文件描述符
		- 通过open得到，open的是一个磁盘文件
		- 注意：文件的大小不能为0，open指定的权限不能和prot参数有冲突。
			prot: PROT_READ                open:只读/读写 
			prot: PROT_READ | PROT_WRITE   open:读写

	- offset：偏移量，一般不用。必须指定的是4k的整数倍，0表示不便宜。

- 返回值：返回创建的内存的首地址  
	失败返回 `MAP_FAILED`，`(void *) -1`

```c
int munmap(void *addr, size_t length);
```
- 功能：释放内存映射
- 参数：
	- addr : 要释放的内存的首地址
	- length : 要释放的内存的大小，要和mmap函数中的length参数的值一样。

### Q&A

1. 如果对mmap的返回值(ptr)做++操作(ptr++), munmap是否能够成功?  
```c
void * ptr = mmap(...);
ptr++;  //可以对其进行++操作
munmap(ptr, len);   // 错误,要保存地址
```

2. 如果open时 `O_RDONLY`, mmap时prot参数指定 `PROT_READ | PROT_WRITE` 会怎样?

	错误，返回MAP_FAILED
	open()函数中的权限建议和prot参数的权限保持一致。

3. 如果文件偏移量为1000会怎样?

	偏移量必须是4K的整数倍，返回MAP_FAILED

4. mmap什么情况下会调用失败?
    - 第二个参数：length = 0
    - 第三个参数：prot
        - 只指定了写权限
        - prot `PROT_READ | PROT_WRITE`  
          第5个参数fd 通过open函数时指定的` O_RDONLY / O_WRONLY`

5. 可以open的时候O_CREAT一个新文件来创建映射区吗?
    - 可以的，但是创建的文件的大小如果为0的话，肯定不行
    - 可以对新的文件进行扩展
        - lseek()
        - truncate()

6. mmap后关闭文件描述符，对mmap映射有没有影响？
	```c
	int fd = open("XXX");
	mmap(,,,,fd,0);
	close(fd); 
	```
	映射区还存在，创建映射区的fd被关闭，没有任何影响。

7. 对ptr越界操作会怎样？
	```c
	void * ptr = mmap(NULL, 100,,,,,);
	```
	4K;  
	越界操作操作的是非法的内存 -> 段错误


## 信号

Linux 进程间通信的最古老的方式之一，是事件发生时对进程的通知机制，有时也称之为软件中断，
它是在软件层次上对中断机制的一种模拟，是一种异步通信的方式。

信号可以导致一个正在运行的进程被另一个正在运行的异步进程中断，转而处理某一个突发事件。

发往进程的诸多信号，通常都是源于内核。引发内核为进程产生信号的各类事件如下：

- 对于前台进程，用户可以通过输入特殊的终端字符来给它发送信号。比如输入Ctrl+C 
通常会给进程发送一个中断信号。

- 硬件发生异常，即硬件检测到一个错误条件并通知内核，随即再由内核发送相应信号给
相关进程。比如执行一条异常的机器语言指令，诸如被 0 除，或者引用了无法访问的
内存区域。

- 系统状态变化，比如 alarm 定时器到期将引起 SIGALRM 信号，进程执行的 CPU 
时间超限，或者该进程的某个子进程退出。

- 运行 kill 命令或调用 kill 函数。

使用信号的两个主要目的是：

- 让进程知道已经发生了一个特定的事情。

- 强迫进程执行它自己代码中的信号处理程序。

- 信号的特点：
	- 简单
	- 不能携带大量信息
	- 满足某个特定条件才发送
	- 优先级比较高

- 查看系统定义的信号列表：kill –l

### 信号的 5 种默认处理动作
- 查看信号的详细信息：man 7 signal

- 信号的 5 中默认处理动作
	- Term 终止进程
	- Ign 当前进程忽略掉这个信号
	- Core 终止进程，并生成一个Core文件
	- Stop 暂停当前进程
	- Cont 继续执行当前被暂停的进程

- 信号的几种状态：
	- 产生
	- 未决
	- 递达

- SIGKILL 和 SIGSTOP 信号不能被捕捉、阻塞或者忽略，只能执行默认动作。

### 信号相关的函数
- int kill(pid_t pid, int sig);
- int raise(int sig);
- void abort(void);
- unsigned int alarm(unsigned int seconds);
- int setitimer(int which, const struct itimerval *new_val, struct itimerval *old_value);
- sighandler_t signal(int signum, sighandler_t handler);
- int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);

### 信号集
- 许多信号相关的系统调用都需要能表示一组不同的信号，多个信号可使用一个称之为
信号集的数据结构来表示，其系统数据类型为 sigset_t。 

- 在 PCB 中有两个非常重要的信号集。一个称之为 “阻塞信号集” ，另一个称之为“未决信号集” 。
这两个信号集都是内核使用位图机制来实现的。但操作系统不允许我们直接对这两个信号集进行位操作。
而需自定义另外一个集合，借助信号集操作函数来对 PCB 中的这两个信号集进行修改。

- 信号的 “未决” 是一种状态，指的是从信号的产生到信号被处理前的这一段时间。

- 信号的 “阻塞” 是一个开关动作，指的是阻止信号被处理，但不是阻止信号产生。

- 信号的阻塞就是让系统暂时保留信号留待以后发送。由于另外有办法让系统忽略信号，
所以一般情况下信号的阻塞只是暂时的，只是为了防止信号打断敏感的操作。

#### 相关函数

- int sigemptyset(sigset_t *set);
- int sigfillset(sigset_t *set);
- int sigaddset(sigset_t *set, int signum);
- int sigdelset(sigset_t *set, int signum);
- int sigismember(const sigset_t *set, int signum);
- int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);
- int sigpending(sigset_t *set);

### MAN 7 signal

```bash
 Signal numbering for standard signals
       The numeric value for each signal is given in the table below.  As shown in the table, many
       signals  have different numeric values on different architectures.  The first numeric value
       in each table row shows the signal number on x86, ARM, and most  other  architectures;  the
       second  value is for Alpha and SPARC; the third is for MIPS; and the last is for PARISC.  A
       dash (-) denotes that a signal is absent on the corresponding architecture.

       Signal        x86/ARM     Alpha/   MIPS   PARISC   Notes
                   most others   SPARC
       ─────────────────────────────────────────────────────────────────
       SIGHUP           1           1       1       1
       SIGINT           2           2       2       2
       SIGQUIT          3           3       3       3
       SIGILL           4           4       4       4
       SIGTRAP          5           5       5       5
       SIGABRT          6           6       6       6
       SIGIOT           6           6       6       6
       SIGBUS           7          10      10      10
       SIGEMT           -           7       7      -
       SIGFPE           8           8       8       8
       SIGKILL          9           9       9       9
       SIGUSR1         10          30      16      16
       SIGSEGV         11          11      11      11
       SIGUSR2         12          31      17      17
       SIGPIPE         13          13      13      13
       SIGALRM         14          14      14      14
       SIGTERM         15          15      15      15
       SIGSTKFLT       16          -       -        7
       SIGCHLD         17          20      18      18
       SIGCLD           -          -       18      -
       SIGCONT         18          19      25      26
       SIGSTOP         19          17      23      24
       SIGTSTP         20          18      24      25
       SIGTTIN         21          21      26      27
       SIGTTOU         22          22      27      28
       SIGURG          23          16      21      29
       SIGXCPU         24          24      30      12
       SIGXFSZ         25          25      31      30
       SIGVTALRM       26          26      28      20
       SIGPROF         27          27      29      21
       SIGWINCH        28          28      20      23
       SIGIO           29          23      22      22
       SIGPOLL                                            Same as SIGIO
       SIGPWR          30         29/-     19      19
       SIGINFO          -         29/-     -       -
       SIGLOST          -         -/29     -       -
       SIGSYS          31          12      12      31
       SIGUNUSED       31          -       -       31

 Note the following:

       *  Where defined, SIGUNUSED is synonymous with SIGSYS.  Since glibc 2.26, SIGUNUSED  is  no
          longer defined on any architecture.

       *  Signal 29 is SIGINFO/SIGPWR (synonyms for the same value) on Alpha but SIGLOST on SPARC.


```
