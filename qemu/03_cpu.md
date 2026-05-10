---
title: CPU 执行
---

# QEMU CPU 执行架构分析

## cpu_exec 流程

```c
// accel/tcg/cpu-exec.c
int cpu_exec(CPUState *cpu)
{
    CPUClass *cc = CPU_GET_CLASS(cpu);
    int ret;

    // 主循环
    for (;;) {
        // 检查停止请求
        if (cpu->stopped) {
            break;
        }

        // 处理等待事件
        if (cpu->unlink_on_signal) {
            qemu_unlink_thread_cond();
        }

        // 执行 TCG 代码
        ret = cpu_exec_step(cpu);

        // 处理返回值
        switch (ret) {
        case EXCP_DEBUG:                // 调试事件
            cpu_handle_debug_exception(cpu);
            break;
        case EXCP_HLT:                 // 停机
            cpu->stopped = true;
            break;
        case EXCP_YIELD:               // 让出
            break;
        default:
            cpu_handle_exception(cpu, ret);
            break;
        }
    }
}
```

## TranslationBlock

```c
struct TranslationBlock {
    target_ulong pc;                    // 起始 PC
    target_ulong cs_base;              // 代码段基址
    uint32_t flags;                    // 标志
    uint16_t size;                     // 代码大小
    uint16_t icache;
    uint32_t cflags;                   // 编译标志
    uint32_t invalidated_flag;

    // 代码指针
    void *tc.ptr;

    // 跳转目标
    uintptr_t jmp_target[2];

    // 原始 PC (用于 icache 失效)
    target_ulong pc_orig;
};
```

## TCG 翻译流程

```
tb_gen_code()
  → tcg_func_create()
  → tcg_reg_alloc_start()
  → temp_alloc()
  → tcg_out_op()
  → patch_reloc()
  → tb_link_page()
  → tb_hash_set()
```

## 加速器接口

### AccelClass

```c
struct AccelClass {
    ObjectClass parent_class;

    const char *name;
    int (*init_machine)(MachineState *machine);
    void (*setup_sigsegv)(void);
};
```

### AccelCPUClass

```c
struct AccelCPUClass {
    CPUClass parent_class;

    void (*cpu_exec_enable)(CPUState *cpu);
    void (*cpu_exec_interrupt)(CPUState *cpu, int interrupt_request);
};
```

## KVM 集成

```c
// accel/kvm/kvm-all.c
int kvm_init_vcpu(CPUState *cpu)
{
    KVMState *s = KVM_STATE(current_machine);
    long mmap_size;

    // 创建 VCPU
    ret = kvm_vm_ioctl(s, KVM_CREATE_VCPU, cpu->cpu_index);
    cpu->kvm_fd = ret;

    // 初始化 KVM 运行
    ret = kvm_vcpu_init(cpu);
}
```

## 设计模式

1. **解释器模式**: TCG 将 guest 代码解释为 host 代码
2. **缓存模式**: TB hash 缓存加速翻译
3. **策略模式**: AccelClass 支持多种加速器
4. **模板方法**: cpu_exec 提供主循环框架
