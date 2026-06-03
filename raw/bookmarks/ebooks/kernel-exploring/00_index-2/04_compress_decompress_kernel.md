# 内核压缩与解压

内核编译后是ELF文件，需要加载到内存并跳转执行。本文探讨内核如何找到加载地址及建立虚拟地址映射。

## 从piggy.S开始

piggy.S包含压缩内核数据，通过`.incbin`指令嵌入压缩文件。定义了压缩前后大小：input_len=9993406字节，output_len=37640768字节。

## 解压缩内核

内核进入保护模式后，首先计算解压缩目标地址。通过CONFIG_PHYSICAL_START确定物理地址为16MB。

移动压缩内核到安全位置（内存末端），然后执行原地解压。extract_kernel返回解压后内核入口点。

验证发现入口地址为0x1000000，正是startup_64函数所在位置。

## 链接与加载

vmlinux是ELF格式，包含5个LOAD段。链接脚本vmlinux.lds.S定义虚拟地址从0xffffffff80000000开始（高端2G内核空间）。

通过parse_elf解析program header，将各段加载到指定物理地址：Text段加载到0x1000000，VirtAddr为0xffffffff81000000。

代码展示了内核解压流程：通过压缩内核→解压→按ELF段加载→跳转执行完整路径。