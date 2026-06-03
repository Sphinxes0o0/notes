# XDP (eXpress Data Path)

## 概述

XDP通过在数据包进入网络协议栈之前处理，提供高性能可编程数据路径，显著提升性能。

## 关键特性

- 在网络协议栈之前处理数据包
- 无锁设计
- 批量I/O操作
- 基于轮询的操作
- 直接队列访问
- 无需分配sk_buff
- 支持网络卸载
- DDIO
- 快速XDP程序执行无循环
- 数据包转向

## 与DPDK比较

XDP相对DPDK的优势：
- 无需第三方代码库或许可证
- 支持基于轮询和中断驱动的网络
- 无需大页分配
- 无需专用CPU
- 无需新的安全网络模型

## 图片

![XDP数据包处理图](xdp-packet-processing-1024x560.png)

## 示例 (GitHub链接)

- Linux kernel BPF samples
- prototype-kernel samples
- libbpf

## 限制

- 无qdisc缓存队列；当TX设备慢时直接丢弃数据包
- XDP程序是专用的，缺乏通用网络协议栈能力

## 参考文档

多个来自NetDev会议的PDF和视频资源
