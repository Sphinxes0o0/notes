# Linux 内核开发入门

## 目录
1. [开发环境准备](#开发环境准备)
2. [内核编译](#内核编译)
3. [rootfs和文件系统](#rootfs和文件系统)
4. [内核调试](#内核调试)
5. [驱动开发工具](#驱动开发工具)
6. [系统启动过程](#系统启动过程)

## 开发环境准备

### 编译环境

```bash
 ██████████████████  ████████     4soos@dev
 ██████████████████  ████████     OS: Manjaro 21.2.0 Qonos
 ██████████████████  ████████     Kernel: x86_64 Linux 5.10.79-1-MANJARO
 ██████████████████  ████████     Uptime: 19m
 ████████            ████████     Packages: 1324
 ████████  ████████  ████████     Shell: bash 5.1.8
 ████████  ████████  ████████     Resolution: 2560x1440
 ████████  ████████  ████████     DE: GNOME 41.1
 ████████  ████████  ████████     WM: Mutter
 ████████  ████████  ████████     WM Theme: 
 ████████  ████████  ████████     GTK Theme: Matcha-dark-pueril [GTK2/3]
 ████████  ████████  ████████     Icon Theme: Papirus-Adapta-Maia
 ████████  ████████  ████████     Font: Noto Sans 12
 ████████  ████████  ████████     Disk: 150G / 946G (17%)
                                  CPU: AMD Ryzen 7 5700G with Radeon Graphics @ 16x 3.8GHz
                                  GPU: AMD RENOIR (DRM 3.40.0, 5.10.79-1-MANJARO, LLVM 13.0.0)
                                  RAM: 2030MiB / 15453MiB
```

### 源码获取

https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.15.4.tar.xz

### 工具集安装
```bash
yay -S base-devel
```

## 内核编译

### 编译步骤
```bash
make menuconfig # 内核配置， 可以默认配置
make -j$(nproc) # -j job 一般为线程数

......

arch/x86/tools/insn_sanity: Success: decoded and checked 1000000 random instructions with 0 errors (seed:0x6455b190)
Kernel: arch/x86/boot/bzImage is ready  (#1)
```
编好之后的产物为 `arch/x86/boot/bzImage`。

## rootfs和文件系统

### 简介

`rootfs`是基于内存的文件系统，所有操作都在内存中完成；也没有实际的存储设备，所以不需要设备驱动程序的参与。
基于以上原因，linux在启动阶段使用`rootfs`文件系统，当磁盘驱动程序和磁盘文件系统成功加载后，linux系统会将系统根目录从`rootfs`切换到磁盘文件系统。

### 启动流程

```
start_kernel
　　vfs_caches_init
　　　　mnt_init
　　　　　　init_rootfs注册rootfs文件系统
　　　　　　init_mount_tree 挂载rootfs文件系统
　　　　　　　　vfs_kern_mount
　　　　　　　　　　mount_fs
　　　　　　　　　　　　type->mount其实是rootfs_mount
　　　　　　　　　　　　　　mount_nodev
　　　　　　　　　　　　　　　　fill_super 其实是ramfs_fill_super
　　　　　　　　　　　　　　　　　　inode = ramfs_get_inode(sb, NULL, S_IFDIR | fsi->mount_opts.mode, 0);
　　　　　　　　　　　　　　　　　　sb->s_root = d_make_root(inode);
　　　　　　　　　　　　　　　　　　　　static const struct qstr name = QSTR_INIT("/", 1);[1*]
　　　　　　　　　　　　　　　　　　　　__d_alloc(root_inode->i_sb, &name);
　　　　　　　　　…
　　　　　　　　　　mnt->mnt.mnt_root = root;[2*]
　　　　　　　　　　mnt->mnt.mnt_sb = root->d_sb;[3*]
　　　　　　　　　　mnt->mnt_mountpoint = mnt->mnt.mnt_root;[4*]
　　　　　　　　　　mnt->mnt_parent = mnt;[5*]
root.mnt = mnt;
　　　　　　　　root.dentry = mnt->mnt_root;
　　　　　　　　mnt->mnt_flags |= MNT_LOCKED;
　　　　　　　　set_fs_pwd(current->fs, &root);
　　　　　　　　set_fs_root(current->fs, &root);
　　…
　　rest_init
　　kernel_thread(kernel_init, NULL, CLONE_FS);
```

### 根文件系统结构

正常来说，根文件系统至少包括以下目录：

* `/etc/`：存储重要的配置文件。
* `/bin/`：存储常用且开机时必须用到的执行文件。
* `/sbin/`：存储着开机过程中所需的系统执行文件。
* `/lib/`：存储/bin/及/sbin/的执行文件所需的链接库，以及Linux的内核模块。
* `/dev/`：存储设备文件。

> 以上列举出的目录必须存储在根文件系统上，缺一不可。

* `/proc`：这是一个空目录，常作为proc文件系统的挂接点，proc文件系统是个虚拟的文件系统，它没有实际的存储设备，里面的目录，文件都是由内核临时生成的，用来表示系统的运行状态，也可以操作其中的文件控制系统。

### 制作临时rootfs

#### 示例代码

```bash
touch main.c
vim main.c
```

```c
#include <stdio.h>

int main()
{
    printf("hello world!");
    printf("hello world!");
    printf("hello world!");
    printf("hello world!");
    fflush(stdout);
    while(1) {
        printf("linux-5.14 > \n");
    };
    return 0;
}
```

#### 生成rootfs

```bash
gcc --static -o hello_kernel main.c
echo hello_kernel | cpio -o --format=newc > rootfs
```

## 内核调试

### QEMU 启动
```bash
qemu-system-x86_64 \
> -kernel ./arch/x86/boot/bzImage \
> -initrd ./rootfs \
> -append "root=/dev/ram rdinit=hello_kernel" \
> -smp 2 \
> -s -S
```
这时的Qemu 会进入等待状态。

### GDB 调试
```bash
gdb ./vmlinux
......
Type "apropos word" to search for commands related to "word"...
Reading symbols from ./vmlinux...
(gdb) target remote:1234
Remote debugging using :1234
0x000000000000fff0 in exception_stacks ()
(gdb) b start_kernel
Breakpoint 1 at 0xfff0
(gdb) c
Continuing.
```

* `target remote:1234`：gdb 连接上qemu
* `b start_kernel`：设置断点： `start_kernel`
* `c`：继续执行

### VS Code 调试配置

需要安装好gdb插件，然后配置三个文件：

#### c_cpp_properties.json

```json
{
    "configurations": [
        {
            "name": "Linux kernel",
            "cStandard": "c11",
            "intelliSenseMode": "linux-clang-x64",
            "compileCommands": "${}/compile_commands.json"
        }
    ],
    "version": 4
}
```

## 驱动开发工具

### 常见工具&命令

#### 系统调试工具
- **dmesg**：查看内核启动的log
- **add2line**：将地址转换成文件名或行号对，以便调试程序
- **ar**：从文件中创建、修改、扩展文件
- **gasp**：汇编宏处理器

#### 目标文件分析工具
- **nm**：从目标文件列举所有变量
- **objcopy**：使用GNU BSD库把目标文件的内容从一种文件格式复制到另一种格式的目标文件中
- **objdump**：显示目标文件信息可发编译二进制文件，也可以对对象文件进行反汇编，并查看机器代码
- **readelf**：显示elf文件信息
- **ranlib**：生成索引以加快对归档文件的访问，并将其保存到这个归档文件中
- **size**：列出目标模块或文件的代码尺寸
- **strings**：打印可打印的目标代码符号（至少4个字符）
- **strip**：放弃所有符号连接，一般应用程序最终都要strip处理
- **C++filt**：链接器ld通过该命令可过滤C++符号和JAVA符号，防止重载函数冲突
- **gprof**：显示程序调用段的各种数据

#### 模块管理工具
- **insmod**：将指定的模块加载到内核中。.ko 是内核模块文件的扩展名
- **rmmod**：用于从内核中卸载指定的模块

#### 符号表分析
- **nm**：显示二进制目标文件的符号表
```bash
-A：每个符号前显示文件名；
-D：显示动态符号；
-g：仅显示外部符号；
-r：反序显示符号表。
```

#### 依赖关系分析
- **ldd**
```bash
-v：详细信息模式，打印所有相关信息；
-u：打印未使用的直接依赖；
-d：执行重定位和报告任何丢失的对象；
-r：执行数据对象和函数的重定位，并且报告任何丢失的对象和函数；
```

#### 进程管理
- **ps**：查看进程信息，如查看僵尸进程
```bash
ps -A -ostat,pid,cmd |grep -iE '^z'
# -A 显示所有任务 -o 按照指定格式输出 grep -iE 显示z开头的行，不区分大小写
```

#### 文件查找
- **find**

用法：
```bash
find [-path ..] [expression]

-name     按照文件名
-iname    按照文件名 忽略大小写
-perm     按照文件权限
-user     按照文件拥有者
-group    按照文件所属的组
-mtime -n +n 按照文件的更改时间来查找文件， -n：n天以内，+n：n天以前
-type     查找某一类型：文件类型有：普通文件(f)，目录(d)，字符设备文件(c)，块设备文件(b)，符号链接文件(l)，套接字文件(s)，管道文件(p)
-size n   查找文件长度为n块（一块等于512字节）的文件，带有c时表示文件长度以字节计。 
-mount    不跨越文件系统
-follow   遇到符号链接文件，就跟踪至链接所指向的文件
-path     匹配文件路径或者文件
-exec     执行后续命令操作
-a        and 与操作
-o        or  或操作
-not      not 非操作
```

经典使用方法：
```bash
# 查找/run中所有的socket文件
find /run -type s
# 搜索/dev中所有包含tty的文件
find /dev -name "*tty*"
# 搜索/dev中大小大于10字节，名称包含bus的文件
find /dev -size +10c -name "*bus*"
# 或操作，搜索debug开头的文件或者.rst的文件
find -name 'debug*' -o -name '*.rst'
# 与操作，搜索debug开头的文件同时是.rst的文件
find -name 'debug*' -a -name '*.rst'
# 找出文件大小大于10000块的文件，并复制到当前目录
find -size +100000 -exec cp {} . \;
```

#### 设备信息
- **lsusb**：显示系统中的USB总线信息

#### 文件系统分析
- **lsof**：列出当前系统打开的文件
```bash
$ lsof
COMMAND    PID      USER   FD      TYPE     DEVICE     SIZE       NODE      NAME
```

字段说明：
* **COMMAND**：进程的名称
* **PID**：进程标识符
* **USER**：进程所有者
* **FD**：文件描述符，应用程序通过文件描述符识别该文件。如cwd、txt、mem等
* **TYPE**：文件类型，REG(文件) DIR(目录) CHR(字符) BLK(块设备) FIFO(管道) UNIX(UNIX 域套接字) IPv4(IP套接字)
* **DEVICE**：指定磁盘的名称
* **SIZE**：文件大小
* **NODE**：文件inode，每个文件都有一个唯一的inode
* **NAME**：文件名称

#### 文本搜索
- **grep**

```bash
-i 忽略大小写
-v 反向选择，即显示不包含匹配文本的所有行
-c 统计匹配的行数
-n 输出行号
-r 递归搜索
```

## 系统启动过程

Linux 系统的启动过程可以分为以下几个阶段：

1. **系统上电**：系统通电，硬件初始化。

2. **BootROM**：
   * 处理器内部的只读存储器（ROM）包含初始启动代码。
   * 执行 BootROM 代码，初始化基本硬件。
   * 查找和加载引导加载程序（如 U-Boot）。

3. **U-Boot**：
   * U-Boot 是一个常用的开源引导加载程序。
   * 负责更多的硬件初始化，如内存、外设等。
   * 提供引导菜单和环境配置。
   * 加载 Linux 内核到内存，并将控制权移交给内核。

4. **Kernel 加载**：
   * Linux 内核开始执行，进一步初始化硬件。
   * 挂载根文件系统（Root Filesystem）。

5. **init**：
   * 内核启动后，运行第一个用户空间进程，通常是 init。
   * init 进程读取配置文件（如 /etc/inittab 或 systemd 配置）并启动系统服务。

---

> 本文档整合了Linux内核编译、调试和驱动开发的基础知识，为内核开发提供完整的指导。 