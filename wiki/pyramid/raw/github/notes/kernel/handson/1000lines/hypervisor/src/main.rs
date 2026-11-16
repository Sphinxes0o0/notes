#![no_std]
#![no_main]

use core::arch::asm;
use core::panic::PanicInfo;

extern crate alloc;

#[macro_use]
mod print;

mod trap;
mod allocator;

#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.boot")]
pub extern "C" fn boot() -> ! {
    // 添加调试信息，确认进入boot函数
    unsafe {
        // 使用特定的指令序列作为标记
        asm!(
            "li t0, 0xB007",        // Load immediate 0xB007 into t0 (BOOT marker)
            "li t1, 0xB007",        // Load immediate 0xB007 into t1 (BOOT marker)
            "la sp, __stack_top",   // Load __stack_top address into sp
            "li t2, 0x1111",        // Load immediate 0x1111 into t2 (before jump marker)
            "j {main}",             // Jump to main
            main = sym main,        // Resolve main symbol
            options(noreturn)       // Tell the compiler that this function does not return
        );
    }
}

#[panic_handler]
pub fn panic_handler(info: &PanicInfo) -> ! {
    println!("panic: {}", info);
    loop {
        unsafe {
            core::arch::asm!("wfi"); // Wait for an interrupt (idle loop)
        }
    }
}

unsafe extern "C" {
    static mut __bss: u8;
    static mut __bss_end: u8;
    static mut __heap: u8;
    static mut __heap_end: u8;
}

fn main() -> ! {
    // Fill the BSS section with zeros.
    unsafe {
        let bss_start = &raw mut __bss;
        let bss_size = (&raw mut __bss_end as usize) - (&raw mut __bss as usize);

        core::ptr::write_bytes(bss_start, 0, bss_size);
        asm!("csrw stvec, {}", in(reg) trap::trap_handler as usize);
        asm!("unimp"); // Illegal instruction here!
    }

    println!("\nBooting hypervisor...");
    allocator::GLOBAL_ALLOCATOR.init(&raw mut __heap, &raw mut __heap_end);

    let mut v = alloc::vec::Vec::new();
    v.push('a');
    v.push('b');
    v.push('c');
    println!("v = {:?}", v);

    loop {
        unsafe {
            asm!("wfi");
        }
    }
}