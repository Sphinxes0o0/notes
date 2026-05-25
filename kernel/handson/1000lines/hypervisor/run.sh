#!/bin/bash
set -xue

# QEMU file path
QEMU=qemu-system-riscv64

RUSTFLAGS="-C link-arg=-Thypervisor.ld -C linker=rust-lld" \
  cargo build --bin hypervisor --target riscv64gc-unknown-none-elf

cp target/riscv64gc-unknown-none-elf/debug/hypervisor hypervisor.elf

# Start QEMU
$QEMU -machine virt \
    -bios default \
    -nographic \
    -cpu rv64 \
    -smp 1 \
    -m 128M \
    -d cpu_reset,unimp,guest_errors,int -D qemu.log \
    -serial mon:stdio \
    -monitor telnet:localhost:1234,server,nowait \
    --no-reboot \
    -kernel hypervisor.elf 
