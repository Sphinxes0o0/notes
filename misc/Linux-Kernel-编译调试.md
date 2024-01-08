---
title: Linux Kernel 编译调试（Qemu + gdb）
date: 2021-11-24 22:03:26
tags:
    - Linux
    - gdb
---

## 编译环境

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

## 源码： 

https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.15.4.tar.xz


## 工具集
```bash
yay -S base-devel
```

## 编译步骤
```bash
make menuconfig # 内核配置， 可以默认配置

make -j$(nproc) # -j job 一般为线程数

......

arch/x86/tools/insn_sanity: Success: decoded and checked 1000000 random instructions with 0 errors (seed:0x6455b190)
Kernel: arch/x86/boot/bzImage is ready  (#1)

```
编好之后的产物为 `arch/x86/boot/bzImage`。

## rootfs 和文件系统简介

`rootfs`是基于内存的文件系统，所有操作都在内存中完成；也没有实际的存储设备，所以不需要设备驱动程序的参与。
基于以上原因，linux在启动阶段使用`rootfs`文件系统，当磁盘驱动程序和磁盘文件系统成功加载后，linux系统会将系统根目录从`rootfs`切换到磁盘文件系统。

大致的启动流程

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
　　　　　　　　　　　　　　　　　　　　static const struct qstr name = QSTR_INIT(“/”, 1);[1*]
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
正常来说，根文件系统至少包括以下目录：

* /etc/：存储重要的配置文件。

* /bin/：存储常用且开机时必须用到的执行文件。

* /sbin/：存储着开机过程中所需的系统执行文件。

* /lib/：存储/bin/及/sbin/的执行文件所需的链接库，以及Linux的内核模块。

* /dev/：存储设备文件。

> 以上列举出的目录必须存储在根文件系统上，缺一不可。

* /proc

这是一个空目录，常作为proc文件系统的挂接点，proc文件系统是个虚拟的文件系统，它没有实际的存储设备，里面的目录，文件都是由内核临时生成的，用来表示系统的运行状态，也可以操作其中的文件控制系统。

### 制作一个临时的rootfs
```bash
touch main.c
vim main.c
```

#### 代码

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

#### QEMU 启动
```bash
qemu-system-x86_64 \
> -kernel ./arch/x86/boot/bzImage \
> -initrd ./rootfs \
> -append "root=/dev/ram rdinit=hello_kernel" \
> -smp 2 \
> -s -S

```
这时的Qemu 会进入等待状态, 

#### GDB 启动
```
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

_target remote:1234_， gdb 连接上qemu,

_b start_kernel_， 设置断点： `start_kernel`

_c_， 继续执行：


##  VS Code 上面调试

需要安装好gdb插件
然后, 三个配置文件：

c_cpp_properties.json

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

launch.json

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [

        {
            "name": "(gdb) Launch",
            "type": "cppdbg",
            "request": "launch",
            "preLaunchTask": "qemu",
            "miDebuggerServerAddress":"127.0.0.1:1234",
            "program": "${workspaceFolder}/vmlinux",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${fileDirname}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        }
    ]
}
```

tasks.json
```json
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
      {
        "label": "qemu",
        "type": "shell",
        "command": "qemu-system-x86_64 -kernel ./arch/x86/boot/bzImage -initrd ./rootfs -append \"root=/dev/ram rdinit=hello_kernel\" -smp 2 -s -S",
        "presentation": {
          "echo": true,
          "clear": true,
          "group": "qemu"
        },
        "isBackground": true,
        "problemMatcher": [
          {
            "pattern": [
              {
                "regexp": ".",
                "file": 1,
                "location": 2,
                "message": 3
              }
            ],
            "background": {
              "activeOnStart": true,
              "beginsPattern": ".",
              "endsPattern": "."
            }
          }
        ]
      },
      {
        "label": "build",
        "type": "shell",
        "command": "make",
        "group": {
          "kind": "build",
          "isDefault": true
        },
        "presentation": {
          "echo": false,
          "group": "build"
        }
      }
    ]
  }
```


