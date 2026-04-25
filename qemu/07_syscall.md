---
title: 系统调用模拟
---

# 系统调用模拟分析

## CPULoop 结构

```c
// linux-user/i386/cpu_loop.c
void cpu_loop(CPUX86State *env)
{
    CPUState *cs = env_cpu(env);
    for(;;) {
        cpu_exec_start(cs);
        trapnr = cpu_exec(cs);        // 通过 TCG 执行 guest 代码
        cpu_exec_end(cs);
        qemu_process_cpu_events(cs);

        switch(trapnr) {
        case 0x80:                    // x86 syscall via int $0x80
        case EXCP_SYSCALL:            // x86-64 syscall 指令
            get_task_state(cs)->orig_ax = env->regs[R_EAX];
            ret = do_syscall(env, env->regs[R_EAX], ...);
            break;
        case EXCP_INTERRUPT:
            break;                    // 信号待处理 - 尽快处理
        }
        process_pending_signals(env); // 投递任何待处理信号
    }
}
```

## 系统调用分派机制

### 入口点

```c
// linux-user/syscall.c
abi_long do_syscall(CPUArchState *cpu_env, int num, abi_long arg1, ... arg8)
{
    // 1. 插件系统调用过滤
    if (send_through_syscall_filters(cpu, num, ...)) {
        return filtered_result;
    }
    // 2. 分派到 do_syscall1()
    return do_syscall1(cpu_env, num, arg1, ... arg8);
}
```

### 主分派

```c
// linux-user/syscall.c
static abi_long do_syscall1(CPUArchState *cpu_env, int num, ...) {
    switch(num) {
    case TARGET_NR_exit:
        preexit_cleanup(cpu_env, arg1);
        _exit(arg1);

    case TARGET_NR_read:
        // lock_user(VERIFY_WRITE, ...) 获取 guest 缓冲区
        // safe_read() 从 host fd 读取
        // fd_trans_host_to_target_data() 转换
        // unlock_user() 返回

    case TARGET_NR_write:
        // 类似模式用 VERIFY_READ 和 safe_write()

    case TARGET_NR_brk:
        return do_brk(arg1);

    // ... 400+ 更多 syscall
    }
}
```

## 目标结构映射

### Guest 地址转换

```c
g2h()                               // guest 虚拟地址转 host 指针
h2g()                               // host 地址转 guest 地址
lock_user(type, guest_addr, len, copy) // 验证并映射 guest 内存
unlock_user()                       // 必要时写回，释放临时映射
```

### 目标结构

```c
// 目标结构定义在每架构头文件中
struct target_sigaction
struct target_sigset_t
struct target_siginfo_t
struct target_stat
struct target_timeval
// 布局匹配 guest ABI；复制时进行字节交换
```

### 系统调用参数处理

```c
// 基于宏的类型安全 get_user/put_user
put_user_ual(x, gaddr)            // 放置 abi_ulong
get_user_u32(x, gaddr)            // 获取 uint32_t

// 结构复制的 lock_user_struct
lock_user_struct(VERIFY_WRITE, host_ptr, guest_addr, copy)
```

## 关键设计模式

1. **错误处理**: 返回 `-TARGET_E*` (负的 guest errno 值)
2. **安全系统调用**: 使用 `safe_read()`/`safe_write()` 包装器
3. **FD 转换**: `fd_trans_*` 函数转换 guest/host 文件描述符
4. **内存验证**: `access_ok()` 检查 guest 虚拟地址
5. **系统调用重启**: 信号在系统调用期间到达时返回 `-QEMU_ERESTARTSYS`

## 关键文件

| 文件 | 功能 |
|------|------|
| `linux-user/main.c` | 入口点和初始化 |
| `linux-user/syscall.c` | 系统调用模拟核心 |
| `linux-user/cpu_loop.c` | 架构特定 CPU 循环 |
| `accel/tcg/user-exec.c` | 用户模式帮助函数 |
