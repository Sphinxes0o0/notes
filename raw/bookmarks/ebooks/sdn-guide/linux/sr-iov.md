# SR-IOV

## 概述

SR-IOV (Single Root I/O Virtualization) 是使用x86通用硬件与虚拟机共享PCIe设备的标准，通过提供独立的内存空间、中断和DMA流来绕过VMM进行数据访问。

## 关键组件

- **PF (Physical Function)**: 包含完整PCIe功能，包括用于配置和管理的SR-IOV扩展能力
- **VF (Virtual Function)**: 轻量级PCIe功能，有自己的独占配置空间

## 图片

![SR-IOV图1](../images/14765271520676.png)
![SR-IOV图2](../images/14765293085020.jpg)
![SR-IOV图3](../images/14765293165898.jpg)
![SR-IOV图4](../images/14765293462966.jpg)
![SR-IOV图5](../images/1-2.png)
![SR-IOV图6](../images/2-2.png)
![SR-IOV图7](../images/3-2.png)

## 代码示例

```bash
modprobe -r igb
modprobe igb max_vfs=7
echo "options igb max_vfs=7" >>/etc/modprobe.d/igb.conf
```

## 优点

- 比直接分配更具可扩展性
- 通过IOMMU和功能隔离提高安全性
- 高包率、低CPU、低延迟

## 缺点

- 刚性：组合性问题
- 可扩展性有限（16 bit）
- 交换功能被迫放入硬件

## 参考文档

- Intel SR-IOV Configuration Guide
- OpenStack SR-IOV Passthrough for Networking
- Redhat OpenStack SR-IOV Configure
