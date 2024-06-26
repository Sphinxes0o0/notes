# Proc目录说明

```bash
proc文件系统是一个伪文件系统，它只存在内存当中。
/proc/buddyinfo   每个内存区中的每个order有多少块可用，和内存碎片问题有关
/proc/cmdline     启动时传递给kernel的参数信息
/proc/cpuinfo     cpu的信息
/proc/crypto      内核使用的所有已安装的加密密码及细节
/proc/devices     已经加载的设备并分类
/proc/dma         已注册使用的ISA DMA频道列表
/proc/execdomains Linux内核当前支持的execution domains
/proc/fb          帧缓冲设备列表，包括数量和控制它的驱动
/proc/filesystems 内核当前支持的文件系统类型
/proc/interrupts  x86架构中的每个IRQ中断数
/proc/iomem       每个物理设备当前在系统内存中的映射
/proc/ioports     一个设备的输入输出所使用的注册端口范围
/proc/kcore       代表系统的物理内存，存储为核心文件格式，里边显示的是字节数，等于RAM大小加上4kb
/proc/kmsg        记录内核生成的信息，可以通过/sbin/klogd或/bin/dmesg来处理
/proc/loadavg     根据过去一段时间内CPU和IO的状态得出的负载状态，与uptime命令有关
/proc/locks       内核锁住的文件列表
/proc/mdstat      多硬盘，RAID配置信息(md=multiple disks)
/proc/meminfo     RAM使用的相关信息
/proc/misc        其他的主要设备(设备号为10)上注册的驱动
/proc/modules     所有加载到内核的模块列表
/proc/mounts      系统中使用的所有挂载
/proc/mtrr        系统使用的Memory Type Range Registers (MTRRs)
/proc/partitions  分区中的块分配信息
/proc/pci         系统中的PCI设备列表
/proc/slabinfo    系统中所有活动的 slab 缓存信息
/proc/stat        所有的CPU活动信息
/proc/sysrq-trigger 使用echo命令来写这个文件的时候，远程root用户可以执行大多数的系统请求关键命令，就好像在本地终端执行一样。要写入这个文件，需要把/proc/sys/kernel/sysrq不能设置为0。这个文件对root也是不可读的
/proc/uptime      系统已经运行了多久
/proc/swaps       交换空间的使用情况
/proc/version     Linux内核版本和gcc版本
/proc/bus         系统总线(Bus)信息，例如pci/usb等
/proc/driver      驱动信息
/proc/fs          文件系统信息
/proc/ide         ide设备信息
/proc/irq         中断请求设备信息
/proc/net         网卡设备信息
/proc/scsi        scsi设备信息
/proc/tty         tty设备信息
/proc/net/dev     显示网络适配器及统计信息
/proc/vmstat      虚拟内存统计信息
/proc/vmcore      内核panic时的内存映像
/proc/diskstats   取得磁盘信息
/proc/schedstat   kernel调度器的统计信息
/proc/zoneinfo    显示内存空间的统计信息，对分析虚拟内存行为很有用
#### 以下是/proc目录中进程N的信息
/proc/N           pid为N的进程信息
/proc/N/cmdline   进程启动命令
/proc/N/cwd       链接到进程当前工作目录
/proc/N/environ   进程环境变量列表
/proc/N/exe       链接到进程的执行命令文件
/proc/N/fd        包含进程相关的所有的文件描述符
/proc/N/maps      与进程相关的内存映射信息
/proc/N/mem       指代进程持有的内存，不可读
/proc/N/root      链接到进程的根目录
/proc/N/stat      进程的状态
/proc/N/statm     进程使用的内存的状态
/proc/N/status    进程状态信息，比stat/statm更具可读性
/proc/self        链接到当前正在运行的进程
```
