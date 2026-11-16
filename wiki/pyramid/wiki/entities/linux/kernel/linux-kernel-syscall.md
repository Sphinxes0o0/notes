---
type: entity
tags: [linux-kernel, system-call, syscall, syscall-table, x86_64, entry-point]
created: 2026-05-28
sources: [ebook-linux-insides]
---

# System Call (系统调用) 机制

## 定义

系统调用是用户空间程序请求内核服务的唯一合法接口。Linux 通过 `syscall` 指令触发从用户态到内核态的特权切换，是 OS 的核心 ABI。x86_64 架构下系统调用通过 MSR 寄存器配置入口点。

## 关键要点

### 系统调用表 (sys_call_table)

```c
// arch/x86/entry/syscall_64.c
asmlinkage const sys_call_ptr_t sys_call_table[__NR_syscall_max+1] = {
    [0 ... __NR_syscall_max] = &sys_ni_syscall,  // 未实现 = -ENOSYS
    #include <asm/syscalls_64.h>
};
```

- **大小**: `__NR_syscall_max + 1` (322 in kernel 4.2)
- **生成方式**: `syscalltbl.sh` 脚本从 `syscall_64.tbl` 生成
- **类型**: `typedef void (*sys_call_ptr_t)(void);`

**x86_64 系统调用号 (部分):**
| 号 | 函数 |
|----|------|
| 0 | sys_read |
| 1 | sys_write |
| 2 | sys_open |
| 3 | sys_close |
| 5 | sys_newfstat |

### 入口初始化 (syscall_init)

在 `trap_init()` → `cpu_init()` → `syscall_init()` 中完成：

```c
// arch/x86/kernel/cpu/common.c
wrmsrl(MSR_STAR,   ((u64)__USER32_CS)<<48 | ((u64)__KERNEL_CS)<<32);
wrmsrl(MSR_LSTAR,  entry_SYSCALL_64);        // 核心入口
wrmsrl(MSR_CSTAR,  entry_SYSCALL_compat);     // 32位兼容模式
wrmsrl(MSR_SYSCALL_MASK, X86_EFLAGS_TF|X86_EFLAGS_DF|...);
```

**MSR 寄存器:**
- `IA32_STAR`: 用户/内核代码段选择符
- `IA32_LSTAR`: 64位 syscall 入口 (`entry_SYSCALL_64`)
- `IA32_CSTAR`: 兼容模式入口
- `IA32_SYSCALL_MASK`: 中断标志屏蔽

### entry_SYSCALL_64 入口处理

用户程序执行 `syscall` 指令时，CPU 自动跳转到 `entry_SYSCALL_64`：

```asm
# arch/x86/entry/entry_64.S
ENTRY(entry_SYSCALL_64)
    SWAPGS_UNSAFE_STACK              # 交换 GS 与 MSR_KERNEL_GS_BASE

    movq    %rsp, PER_CPU_VAR(rsp_scratch)
    movq    PER_CPU_VAR(cpu_current_top_of_stack), %rsp

    pushq   $__USER_DS
    pushq   PER_CPU_VAR(rsp_scratch)
    pushq   %r11                      # RFLAGS
    pushq   $__USER_CS
    pushq   %rcx                      # RIP (返回地址)
    pushq   %rax                      # syscall number

    ENABLE_INTERRUPTS(CLBR_NONE)

    # 检查 syscall 跟踪 (_TIF_WORK_SYSCALL_ENTRY)
    testl   $_TIF_WORK_SYSCALL_ENTRY, ...
    jnz     tracesys

    # 验证 syscall 号
    cmpq    $__NR_syscall_max, %rax
    ja      1f

    # 分发到 sys_call_table[rax]
    movq    %r10, %rcx               # 第四参数 (r10 → rcx for C ABI)
    call    *sys_call_table(, %rax, 8)
```

**寄存器约定 (x86_64 C ABI):**
| 寄存器 | 用途 |
|--------|------|
| rax | syscall 号 / 返回值 |
| rcx | 返回地址 (被 syscall 覆盖) |
| rdi | 第1参数 |
| rsi | 第2参数 |
| rdx | 第3参数 |
| r10 | 第4参数 (替代 r8) |
| r8 | 第5参数 |
| r9 | 第6参数 |

### 退出系统调用

```asm
    # 从 handler 返回后
    movq    %rax, RAX(%rsp)          # 保存返回值

    LOCKDEP_SYS_EXIT

    RESTORE_C_REGS_EXCEPT_RCX_R11

    movq    RIP(%rsp), %rcx          # 恢复返回地址
    movq    EFLAGS(%rsp), %r11       # 恢复标志位
    movq    RSP(%rsp), %rsp          # 恢复栈指针

    USERGS_SYSRET64                   # swapgs + sysretq
```

### SWAPGS 机制

`SWAPGS` 交换 GS 寄存器和 `MSR_KERNEL_GS_BASE`：
```c
#define SWAPGS_UNSAFE_STACK    swapgs
```

- 用户态: GS 指向用户数据结构
- 内核态: GS 指向 per-CPU `irq_stack_union`
- `swapgs` 快速切换 GS 基址，无需内存访问

### vsyscall 和 vDSO

- **vsyscall**: 早期机制，固定地址，存在安全风险
- **vDSO**: 动态链接到用户空间，无安全风险，部分 syscall (如 `gettimeofday`) 直接在内核页表执行

## 相关概念

- [[entities/linux/kernel/linux-kernel-vfs-core]] — VFS 层 socket/file 接口 (syscall 的应用层)
- [[entities/linux/kernel/net]] — 网络 syscall (socket, bind, connect)
- [[entities/linux/kernel/linux-kernel-smp]] — per-CPU 变量 (rsp_scratch, irq_stack_union)
- [[entities/linux/kernel/linux-kernel-time-core]] — 时钟相关 syscall (clock_gettime)

## 来源详情

- [[sources/ebook-linux-insides]] — SysCall 章节 (27-syscall-2, 29-syscall-4)
- [[bookmark-linux-inside]] — Linux Inside bookmark
