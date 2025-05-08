# QNX 资源管理器

> Reading notes from : https://github.com/xtang2010/articles

## What is  ?

资源管理器顾名思义就是管理“资源”的服务器，这里问题是，到底什么是“资源”呢？
在QNX 上，“资源”可以是一个硬件(硬件资源管理器其实就是我们常说的硬件驱动)，
“资源”也可以是一种服务，比如TCPIP 网络服务，或者ntfs 文件系统服务；
“资源”甚至可以是一个文件(或者目录).

Unix 的基本思想，就是“把驱动当成文件”，那资源管理器就非常有用了。
所以/dev/ser1 是一个管理串口的资源管理器，而/dev/random 则是一个提供随机数的资源管理器。
甚至传统Unix 里那些mount point，像是根目录 /，或者用户目录 /home 在QNX 里也可以是一个个资源管理器。

## 框架

QNX 提供的资源管理器框架：
- iofunc (iomsg) : 提供所有POSIX对文件可以进行的io操作
    - sys/iofuncs.h
    - sys/iomsg.h

- remgr : 提供了登记路径名， 接收数据然后分发给iofunc 执行

- dispatch : 识别不同的处理函数， 如消息传递， 脉冲， 信号等

- thread pool : 提供线程池管理，配置实现多个线程进行资源管理


### iofunc (iomsg)
QNX 总结了总共34 个对文件操作，基本上POSIX 对文件的处理，都可以通过这34 个操作进行。
而资源管理器的iofunc 层，其实也就是准备回调函数，通过响应这些操作请求，来提供服务。

根据回调参数的性质不同， 分成了两种回调函数：

- "connect" type
    - open
    - unlink
    - rename
    - mknod
    - readlink
    - link
    - unblock
    - mount

- "IO" type
    - read
    - write
    - close_ocb
    - stat
    - notify
    - devctl
    - unblock
    - chmod
    - pathconf
    - lseek
    - chown
    - utime
    - openfd
    - fdinfo
    - lock
    - space
    - shutdown
    - mmap
    - msg
    - umount
    - close_dup
    - lock_ocb
    - unlock_ocb
    - sync
    - power

### resmgr

resmgr 层是那个“循环按收信息并调用iofunc”的那一层。几个重要的函数差不多就是这样:

```c
    resmgr_attach(....) 
    ctp = resmgr_context_alloc() 
    for (;;) { 
        ctp = resmgr_block(ctp); 
        resmgr_handler(ctp) 
    }
```

### dispatch 层 

虽然大多数情况下，用 `iofunc` 层+ `resmgr` 层已经可以构建一个完整的资源管理器了，但是有时候资源管理
器需要同时处理别的消息，这时就需要 `dispatch` `层了。dispatch` 可以处理其他形态的信息，除了可以用 
`resmgr_attch()` 来挂接 `resmgr` 和 `iofunc` 以外，还可以做这些 (sys/dispatch.h)： 


```c
int message_attach(dispatch_t *dpp, message_attr_t *attr, int low, int high, 
                  int (*func)(message_context_t *ctp, int code, unsigned flags, void *handle), 
                  void *handle); 
```


有时候资源管理器在使用标准的 iomsg 以外，还想要定义自己的消息类型，那就会用到这个 `message_attach()`.
这个函数意思是说，如果收到一个消息，它的消息类型在 low 和 high 之间的话，那就回调 func 来处理。 

当然，要保证 low/high 不会与 iomsg 重叠，不然就会有歧义。在 iomsg.h 里已经定义了所有的 iomsg 在 
`_IO_BASE` 和 `_IO_MAX` 之间，所以只要保证 `low > _IO_MAX` 就可以了。  

```c
int pulse_attach(dispatch_t *dpp, int flags, int code, 
                int (*func)(message_context_t *ctp, int code, unsigned flags, void *handle), 
                void *handle); 
```

有许多管理硬件资源的管理器（驱动程序），除了提供iomsg 消息，来对应客户端的io 请求以外，也会很
常见需要接收“脉冲”来处理中断 (InterruptAttachEvent)。这时，用 `pulse_attach()` 就可以把指定的脉冲号
(code)，绑定到回调函数 func 上。 

```c
int select_attach(void *dpp, select_attr_t *attr, int fd, unsigned flags, 
                int (*func)(select_context_t *ctp, int fd, unsigned flags, void *handle), 
                void *handle); 
```

很多资源管理器，在处理客户端请求时，还需要向别的资源管理器发送一些请求。
而很多时候这些请求可能不能立即返回结果，通常情况下，可以用 select() 来处理，但第一我们无法使用会阻塞的select()，
因为我们是一个资源管理器的服务函数，如果被阻塞无法返回，就意味着我们无法处理客户端请求了；
第二我们也无法用 select() 轮询，因为我们一旦返回，就会进入 等待客户端消息的阻塞状态，没有新消息来时，
不会退出阻塞状态，也就没有机会再去轮询 select()了。 

当然，可以自设一个时钟，每隔一定时间就给自己发一个脉冲，等于自己把自己叫醒，然后再轮询 select()，但这样就无端增加了许多系统开销。 
select_attach() 就是为了这个目的设的，针对一个特定的 fd, 这里的 unsigned flags，决定了你想要 select() 的事件（Read? Write? Except?)。
这意思是说，如果对于 fd, 我选择的 flags 事件发生了的话，调用func回调函数。


### thread pool
上面这些用 while (1) 来循环处理消息的资源管理器，明显都是“单线程”资源管理器，一共只有一个线程来处理客户端请求。 
对于一些需要频繁处理客户请求的资源管理器，自然会想到用“多线程”资源管理器。
基本就是用几个线程来执行上面的 while(1)循环。 

线程池（Thread Pool）就是用来实现这个的。使用起来也比较简单，先配置 poot_attr，然后创建并启动线
程池。

```c
memset(&pool_attr, 0x00, sizeof pool_attr); 
if(!(pool_attr.handle = dpp = dispatch_create())) { 
    perror("dispatch_create"); 
    return EXIT_FAILURE; 
} 
pool_attr.context_alloc = dispatch_context_alloc; 
pool_attr.block_func    = dispatch_block; 
pool_attr.handler_func  = dispatch_handler; 
pool_attr.context_free  = dispatch_context_free; 
pool_attr.lo_water      = 2; 
pool_attr.hi_water      = 5; 
pool_attr.increment     = 2; 
pool_attr.maximum       = 10; 
  
tpp = thread_pool_create( &pool_attr, POOL_FLAG_EXIT_SELF) 
thread_pool_start( tpp ); 
```

pool_attr 前面几个回调函数都比较简单，后面的 lo_water, hi_water, increment, maximum 简要说明一下。 
maxmimum 是最多池里可以建多少线程， 
hi_water 是最多这些线程可以等待任务 
lo_water 是至少应该有多少线程需要在等待任务 
increment 则是一次递增的线程数。

