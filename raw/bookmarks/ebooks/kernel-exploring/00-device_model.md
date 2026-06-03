# 设备模型

内核除了管理内存，其很大一部分工作就是管理设备了。如果大家看一眼代码就可以发现drivers目录驱动的代码量估计占一半以上。

现在我们就来看看内核是如何管理这么庞大数量的设备的，其中有三个比较重要的概念：

* 总线
* 驱动
* 设备

## 总线

第一个我想说的是总线bus，因为接着我们就可以看到总线连接着驱动和设备，是整个设备模型的纽带。

[总线](/kernel-exploring/00-device_model/01-bus.md)

## 驱动

驱动和设备部分前后，先聊聊驱动。

[驱动](/kernel-exploring/00-device_model/02-driver.md)

## 设备

终于要看到设备了。

[设备](/kernel-exploring/00-device_model/03-device.md)

## 如何关联设备和驱动

在上面小节的描述中，我们跳过了一个非常总要的环节，那就是驱动和设备是如何关联到一起的。

[绑定](/kernel-exploring/00-device_model/04-bind.md)