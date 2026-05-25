#!/bin/bash
set -xue

# clang 路径和编译器标志
CC=/opt/homebrew/opt/llvm/bin/clang  # Ubuntu 用户：使用 CC=clang
OBJCOPY=/opt/homebrew/opt/llvm/bin/llvm-objcopy
CFLAGS="-std=c11 -O2 -g3 -Wall -Wextra \
       --target=riscv32-unknown-elf -mcmodel=medany \
       -fno-stack-protector -ffreestanding -nostdlib"

# Build the shell (application)
$CC $CFLAGS -fuse-ld=lld -Wl,-Tuser.ld -Wl,-Map=shell.map \
    -o shell.elf shell.c user.c common.c

$OBJCOPY --set-section-flags .bss=alloc,contents -O binary shell.elf shell.bin
$OBJCOPY -Ibinary -Oelf32-littleriscv shell.bin shell.bin.o

# 构建内核，添加链接器兼容性选项
$CC $CFLAGS -fuse-ld=lld -Wl,-Tkernel.ld \
    -Wl,-Map=kernel.map \
    -Wl,--gc-sections -Wl,--no-relax \
    -o kernel.elf \
    kernel.c common.c shell.bin.o

# QEMU 文件路径
QEMU=qemu-system-riscv32

(cd disk && tar cf ../disk.tar --format=ustar *.txt)

# 启动 QEMU，启用 monitor 并通过 telnet 访问
# 可以通过 telnet localhost 1234 连接到 monitor
$QEMU \
    -machine virt \
    -bios default \
    -nographic \
    -serial stdio \
    -monitor telnet:localhost:1234,server,nowait \
    --no-reboot \
    -d unimp,guest_errors,int,cpu_reset -D qemu.log \
    -drive id=drive0,file=disk.tar,format=raw,if=none \
    -device virtio-blk-device,drive=drive0,bus=virtio-mmio-bus.0 \
    -kernel kernel.elf