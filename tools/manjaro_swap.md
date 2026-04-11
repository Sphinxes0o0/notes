---
title: manjaro_swap
date: 2021-12-16 17:04:07
tags:
    - Linux
categories:
    - Linux编程
---


> 起因： 编译AOSP源码， 提示最小内存为 16gb


本机环境：
```bash
 ████████  ████████  ████████     young@dev
 ████████  ████████  ████████     young@dev
 ████████  ████████  ████████     Uptime: 3h 52m
                                  Shell: bash 5.1.12
 ████████  ████████  ████████     DE: GNOME 41.2
 ████████  ████████  ████████     GTK Theme: Matcha-light-sea [GTK2/3]
                                  Icon Theme: Papirus-Adapta-Maia
 ████████  ████████  ████████     CPU: AMD Ryzen 7 5700G with Radeon Graphics @ 16x 3.8GHz
 ██████████████████  ████████     GPU: AMD/ATI
 ████████  ████████  ████████     Kernel: x86_64 Linux 5.15.7-1-MANJARO
 ██████████████████  ████████     Resolution: 2560x1440
 ████████  ████████  ████████     WM Theme: 
 ██████████████████  ████████     Disk: 383G / 946G (43%)
 ██████████████████  ████████     RAM: 3558MiB / 15448MiB
 ████████  ████████  ████████     Packages: 1375
                                  OS: Manjaro 21.2.0 Qonos
 ████████  ████████  ████████     Font: Noto Sans 12
 ████████  ████████  ████████     WM: Mutter
```

## 配置及安装相应软件
```bash
sudo yay -Syyu

yay -S lineageos-devel

```

## 建立交换文件

使用dd去创建一个由你自己指定大小的交换文件。例如，创建一个 20 GiB 的交换文件:
```bash
sudo dd if=/dev/zero of=/swapfile bs=1G count=20 status=progress
```

为交换文件设置权限（交换文件全局可读是一个巨大的本地漏洞）：

```bash
sudo chmod 600 /swapfile
```

创建正确大小的文件后，将其格式化用来作为交换文件：

```bash
sudo mkswap /swapfile
```

启用交换文件：

```bash
sudo swapon /swapfile
```

最后，编辑 /etc/fstab，在为交换文件添加一个条目：

```bash
/swapfile none swap defaults 0 0
```











