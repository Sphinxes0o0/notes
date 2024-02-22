



进程间通信

（1）共享内存: 独立的开辟一段内存空间，进程1往内存中写数据，进程2从内存中读数据，如果有其他进程，则另开辟内存空间即可。

（2）消息队列：可以传递消息

（3）管道：可以用来传递消息，但是是单向的
	- 有名管道 (named pipe) ： 有名管道也是半双工的通信方式 

（4）互斥器：用来进程同步和互斥

（5）信号量：用来进程同步和互斥

（6）信号：用来进程同步和互斥

线程间通信

因为同一个进程中的线程是共享地址空间的，可以共享数据，因此线程间的通信方式个人认为就是处理线程间的同步和互斥，常用线程间通信的方式有以下几种：

（1）原子操作符集

（2）互斥锁

（3）信号量

（4）条件变量（Linux）

（5）读写锁（Linux）

crt1.o, crti.o, crtbegin.o, crtend.o, crtn.o 等目标文件和daemon.o（由我们自己的C程序文件产生）链接成一个执行文件。前面这5个目标文件的作用分别是启动、初始化、构造、析构和结束，它们通常会被自动链接到应用程序中。例如，应用程序的main()函数就是通过这些文件来调用的。如果不进行标准的链接的话（编译选项-nostdlib），我们就必须指明这些必要的目标文件，如果未指定，链接器就会提示找不到_start符号，并因此导致链接失败。且，将目标文件提供给编译器的次序也很重要，因为GNU链接器（编译器会自动调用该链接器进行目标文件的链接）只是个单次处理链接器。

 

Glibc有几个辅助程序运行的运行库 (C RunTime Library)，分别是/usr/lib/crt1.o、/usr/lib/crti.o和/usr/lib/crtn.o，其中crt1.o中包含程序的入口函数_start以及两个未定义的符号__libc_start_main和main，由_start负责调用__libc_start_main初始化libc，然后调用我们源代码中定义的main函数；另外，由于类似于全局静态对象这样的代码需要在main函数之前执行，crti.o和crtn.o负责辅助启动这些代码。另外，Gcc中同样也有crtbegin.o和crtend.o两个文件，这两个目标文件用于配合glibc来实现C++的全局构造和析构。


android bionic,这个C runtime library设计并不是功能特别强大,并且有些gnu glic中的函数没有实现,这是移植时会碰到的问题.而且,这个C runtime library也并没有采用crt0.o,crt1.o,crti.o crtn.o,crtbegin.o crtend.o,而是采用了android自己的crtbegin_dynamic.o, crtbegin_static.o 和crtend_android.o。crt1.o是crt0.o的后续演进版本,crt1.o中会非常重要的.init段和.fini段以及_start函数的入口..init段和.fini段实际上是靠crti.o以及crtn.o来实现的. init段是main函数之前的初始化工作代码, 比如全局变量的构造. fini段则负责main函数之后的清理工作.crti.o crtn.o是负责C的初始化,而C++则必须依赖crtbegin.o和crtend.o来帮助实现.
        So,在标准的linux平台下,link的顺序是:ld crt1.o crti.o [user_objects] [system_libraries] crtn.o
        而在android下,link的顺序是:arm-eabi-g++ crtbegin_dynamic.o [user_objects] [system_libraries]crtend_android.o
        所以这就是从另一个方面说明为什么不适合codesourcery之类编译来开发android底层东西的原因了,这里不包括BSP之类.

 

main()也是一个函数。

这是因为在编译连接时它将会作为crt0.s汇编程序的函数被调用。
crt0.s是一个桩（stub）程序，名称中的“crt”是“C run-time”的缩写。
该程序的目标文件将被链接在每个用户执行程序的开始部分，主要用于设置一些初始化全局变量。
通常使用gcc编译链接生成文件时，gcc会自动把该文件的代码作为第一个模块链接在可执行程序中。
在编译时使用显示详细信息选项“-v”就可以明显地看出这个链接操作过程。
因此在通常的编译过程中，我们无需特别指定stub模块crt0.o。

为了使用ELF格式的目标文件以及建立共享库模块文件，现在的编译器已经把crt0扩展成几个模块：
crt1.0、crti.o、crtbegin.o、crtend.o和crtn.o。

这些模块的链接顺序为crt1.o、crti.o、crtbegin.o（crtbeginS.o）、所有程序模块、crtend.o（crtendS.o）、crtn.o、库模块文件。gcc的配置文件specfile指定了这种链接顺序。
其中，crt1.o、crti.o和crtn.o由C库提供，是C程序的“启动”模块；crtbegin.o和crtend.o是C++语言的启动模块，由编译器gcc提供；
而crt1.o则与crt0.o的作用类似，主要用于在调用main()之前做一些初始化工作，全局符号_start就定义在这个模块中。
crtbegin.o和crtend.o主要用于C++语言，在.ctors和.dtors区中执行全局构造（constructor）和析构（destructor）函数。crtbeginS.o和crtendS.o的作用与前两者类似，但用于创建共享模块中。
crti.o用于在.init区中执行初始化函数init()。.init区中包含进程的初始化代码，即当程序开始执行时，系统会在调用main()之前先执行.init中的代码。
crtn.o则用于在.fini区中执行进程终止退出处理函数fini()函数，即当程序正常退出时（main()返回之后），系统会安排执行.fini中的代码。

## OpenOCD 

OpenOCD 探测目标所运行 OS 的原理是，它查询目标所运行的程序中有无 OS 所含有的变量符号，例如 FreeRTOS 有如下符号：

    pxCurrentTCB, pxReadyTasksLists, xDelayedTaskList1, xDelayedTaskList2, pxDelayedTaskList, pxOverowDelayedTaskList, xPendingReadyList, uxCurrentNumberOfTasks, uxTopUsedPriority.

如果这些符号都有，那就说明目标所运行的 OS 是 FreeRTOS。

但是 OpenOCD 是在硬件层的调试，它只是根据 gdb 的命令来读写内存和寄存器，如何能查询目标程序内的符号的呢？

下面是一个 OpenOCD 的启动日志，此时 gdb 还没有 attach 上来。

    Open On-Chip Debugger 0.9.0 (2016-10-26-15:30)
    Licensed under GNU GPL v2
    For bug reports, read
    http://openocd.org/doc/doxygen/bugs.html
    Info : JLink SWD mode enabled
    swd
    adapter speed: 10000 kHz
    adapter_nsrst_delay: 100
    adapter_nsrst_delay: 100
    none separate
    cortex_m reset_config sysresetreq
    jtag_init
    Info : J-Link V9 compiled Sep 1 2016 18:29:50
    Info : J-Link caps 0xb9ff7bbf
    Info : J-Link hw version 94000
    Info : J-Link hw type J-Link
    Info : J-Link max mem block 69920
    Info : J-Link configuration
    Info : USB-Address: 0x0
    Info : Kickstart power on JTAG-pin 19: 0xffffffff
    Info : Vref = 3.312 TCK = 0 TDI = 0 TDO = 0 TMS = 1 SRST = 1 TRST = 0
    Info : J-Link JTAG Interface ready
    Info : clock speed 10000 kHz
    Info : SWD IDCODE 0x2ba01477
    Info : stm32f4x.cpu: hardware has 6 breakpoints, 4 watchpoints
    Info : accepting 'gdb' connection on tcp/3333
    target state: halted
    target halted due to debug-request, current mode: Thread
    xPSR: 0x01000000 pc: 0x08000034 msp: 0x2000dd1c

可以看出，此时 OpenOCD 还探测不到目标所运行的 OS。

在 gdb attach 上以后，OpenOCD 日志如下：

    Info : device id = 0x10006431
    Info : flash size = 512kbytes
    Info : Auto-detected RTOS: FreeRTOS

可以看出，在 gdb attach 上以后，OpenOCD 才探测出目标所使用的 OS 是 FreeRTOS。

不难猜测，OpenOCD 应该是查询 gdb 所加载的 ELF 文件中的符号表来探测 OS 的。

那么 OpenOCD 如何能查询到 ELF 文件内的符号表呢？

原来 OpenOCD 可以向 gdb 发送查询符号命令 - qSymbol:sym_name，来查询 ELF 文件内的符号地址。

gdb 文档中关于此部分的说明如下：

    ‘qSymbol:sym_name’
    The target requests the value of symbol sym name (hex encoded). gdb may provide the value by using the ‘qSymbol:sym_value:sym_name’ message, described below.
    ‘qSymbol:sym_value:sym_name’
    Set the value of sym name to sym value.
    sym name (hex encoded) is the name of a symbol whose value the target has previously requested.
    sym value (hex) is the value for symbol sym name. If gdb cannot supply a value for sym name, then this eld will be empty.

用 wireshark 抓取 gdb attach 时的 gdb 和 OpenOCD 的通信包，其中有一段即是查询符号的部分：

    $qSymbol:5f74785f7468726561645f63757272656e745f707472
    $qSymbol::5f74785f7468726561645f63757272656e745f707472
    $qSymbol:757843757272656e744e756d6265724f665461736b73
    $qSymbol:20000b6c:757843757272656e744e756d6265724f665461736b73

OpenOCD 首先发出 qSymbol 命令，数据是 5f74785f7468726561645f63757272656e745f707472，转化成 ASCII 码是 _tx_thread_current_ptr，这是 ThreadX 的 symbol，因为我们的目标运行的是 FreeRTOS，所以 gdb 回复的 sym_value 是空的，代表没有这个符号。

然后 OpenOCD 查询 uxCurrentNumberOfTasks，gdb 回复中的 sym_value 的值是 20000b6c，即 uxCurrentNumberOfTasks 的地址。



