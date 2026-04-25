---
title: 信号处理
---

# 信号处理分析

## 信号转换表

```c
// linux-user/signal.c
static uint8_t host_to_target_signal_table[_NSIG];
static uint8_t target_to_host_signal_table[TARGET_NSIG + 1];

int host_to_target_signal(int sig) {
    if (sig < 1 || sig >= _NSIG) return sig;
    return host_to_target_signal_table[sig];
}
```

### 初始化

```c
signal_table_init()
// 默认: SIGRTMIN+2 到 SIGRTMAX 映射到 TARGET_SIGRTMIN
// 保留 2 个 host RT 信号供内部使用
```

## Host 信号处理程序

```c
// linux-user/signal.c
static void host_signal_handler(int host_signum, siginfo_t *info, void *puc)
{
    // 1. 获取目标信号号
    guest_sig = host_to_target_signal(host_signum);

    // 2. 同步信号特殊处理
    if (info->si_code > 0) {
        switch(host_signum) {
        case SIGSEGV:
            host_sigsegv_handler(cpu, info, uc);
        case SIGBUS:
            host_sigbus_handler(...);
        }
    }

    // 3. 转换 siginfo 到目标格式
    host_to_target_siginfo_noswap(&tinfo, info);

    // 4. 排队等待投递
    ts->sigtab[guest_sig - 1].info = tinfo;
    ts->sigtab[guest_sig - 1].pending = guest_sig;
    ts->signal_pending = 1;

    // 5. 退出 CPU 执行以投递信号
    cpu->exception_index = EXCP_INTERRUPT;
    cpu_loop_exit_restore(cpu, pc);
}
```

## Siginfo 转换

```c
// linux-user/signal.c
void host_to_target_siginfo(target_siginfo_t *tinfo, const siginfo_t *info)
{
    // si_code 在上部 16 位编码信号类型
    // 处理: SI_USER/SI_TKILL, SIGCHLD, SIGIO, SIGQUEUE 源
    // 转换 si_pid, si_uid, si_status, si_addr, si_band, si_fd
}
```

## 信号帧构建

```c
// 架构特定的 setup_frame()/setup_rt_frame()
// 在 guest 栈上创建 sigframe，包含:
// - target_ucontext
// - target_siginfo
// - 保存的 guest 寄存器状态
// - 信号处理程序地址
// - 返回地址
```

## 异步信号处理

### 信号排队

```c
// linux-user/signal.c
void queue_signal(CPUArchState *env, int sig, int si_type, target_siginfo_t *info)
{
    ts->sync_signal.info = *info;
    ts->sync_signal.pending = sig;
    qatomic_set(&ts->signal_pending, 1);
}
```

### 处理循环

```c
void process_pending_signals(CPUArchState *cpu_env)
{
    while (qatomic_read(&ts->signal_pending)) {
        // 处理期间阻塞所有信号
        sigfillset(&set);
        sigprocmask(SIG_SETMASK, &set, 0);

    restart_scan:
        // 首先: 处理同步信号 (来自 queue_signal)
        if (ts->sync_signal.pending) {
            handle_pending_signal(cpu_env, sig, &ts->sync_signal);
            goto restart_scan;
        }

        // 其次: 处理来自 sigtab[] 的异步信号
        for (sig = 1; sig <= TARGET_NSIG; sig++) {
            if (ts->sigtab[sig-1].pending && ...) {
                handle_pending_signal(cpu_env, sig, &ts->sigtab[sig-1]);
                goto restart_scan;
            }
        }
    }
}
```

## TaskState 信号字段

```c
struct TaskState {
    struct emulated_sigtable sync_signal;        // 同步异常信号
    struct emulated_sigtable sigtab[TARGET_NSIG]; // 排队的异步信号
    sigset_t signal_mask;                       // Guest 信号掩码
    sigset_t sigsuspend_mask;                   // sigsuspend() 掩码
    int in_sigsuspend;                          // 在 sigsuspend 系统调用中
    int signal_pending;                         // 至少一个信号待处理
    struct target_sigaltstack sigaltstack_used; // 备用栈
};
```

## 待处理信号类型

1. **同步信号** - QEMU 强制用于 CPU 异常 (页错误, 除法错误)
2. **异步信号** - 从 host 信号排队，来自 guest 系统调用 (kill, rt_sigqueueinfo)

## 关键设计模式

1. **两阶段投递**: Host 信号被捕获，转换，排队；然后在安全点投递
2. **Siginfo 保留**: si_code, si_addr, si_pid 等信息通过转换保留
3. **SA_SIGINFO 支持**: 请求时将完整 siginfo 传递给 guest 处理程序
4. **同步信号取消阻塞**: Linux 要求同步信号不能被阻塞 (强制执行)
5. **核心转储处理**: `dump_core_and_abort()` 用于未处理的致命信号
6. **安全系统调用倒带**: `rewind_if_in_safe_syscall()` 从安全系统调用恢复 PC

## 关键文件

| 文件 | 功能 |
|------|------|
| `linux-user/signal.c` | 核心信号处理 |
| `linux-user/signal-common.h` | 公共信号基础设施 |
| `accel/tcg/user-exec.c` | 用户模式帮助函数 |
