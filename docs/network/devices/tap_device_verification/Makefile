# TAP Device Kernel Module Makefile

obj-m := tap_device.o

# 获取当前内核版本
KVERSION := $(shell uname -r)

# 内核构建目录
KDIR := /lib/modules/$(KVERSION)/build

# 当前目录
PWD := $(shell pwd)

# 编译目标
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# 清理目标
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f *.o *.ko *.mod.c *.mod *.symvers *.order

# 安装模块
install:
	sudo insmod tap_device.ko

# 卸载模块
uninstall:
	sudo rmmod tap_device

# 查看模块信息
info:
	modinfo tap_device.ko

# 查看内核日志
dmesg:
	dmesg | tail -20

# 完整测试流程
test: all install
	@echo "=== TAP device module loaded ==="
	lsmod | grep tap_device
	@echo "=== Device files created ==="
	ls -l /dev/tap*
	@echo "=== Network interfaces ==="
	ip link show | grep tap

# 验证编译
verify: all
	@echo "=== Module compilation successful ==="
	file tap_device.ko
	@echo "=== Module information ==="
	modinfo tap_device.ko

.PHONY: all clean install uninstall info dmesg test verify 