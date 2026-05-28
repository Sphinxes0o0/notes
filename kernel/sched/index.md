# Linux 调度器子系统 (kernel/sched/) 文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [sched_core.md](sched_core.md) | 调度器核心: schedule(), __schedule(), pick_next_task() | kernel/sched/core.c |
| [sched_cfs.md](sched_cfs.md) | CFS 完全公平调度器 | kernel/sched/fair.c |
| [sched_rt.md](sched_rt.md) | RT 实时调度器 + Deadline 调度器 | kernel/sched/rt.c, deadline.c |
| [sched_class.md](sched_class.md) | 调度类框架 | kernel/sched/sched.h |
| [sched_context_switch.md](sched_context_switch.md) | 上下文切换机制 | kernel/sched/core.c, arch/x86/ |
| [sched_load_balance.md](sched_load_balance.md) | 负载均衡 | kernel/sched/fair.c, topology.c |

---

## 1. 调度器核心 (sched_core.md)

### 关键内容
- `schedule()` → `__schedule_loop()` → `__schedule()`
- `pick_next_task()` → `__pick_next_task()` → `pick_next_task_fair()`
- `struct task_struct`: __state, prio, static_prio, normal_prio, policy
- `struct sched_entity`: load, run_node, vruntime, cfs_rq
- `struct cfs_rq`: tasks_timeline, nr_queued, curr

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| schedule | kernel/sched/core.c:6998 |
| __schedule | kernel/sched/core.c:6764 |
| __pick_next_task | kernel/sched/core.c:5909 |
| pick_next_task_fair | kernel/sched/fair.c:8978 |

---

## 2. CFS 调度器 (sched_cfs.md)

### 关键内容
- `calc_delta_fair()`: vruntime 计算
- `update_curr()`: vruntime 更新
- `place_entity()`: 新任务/睡眠唤醒处理
- `__enqueue_entity()` / `__dequeue_entity()`: 红黑树操作
- `pick_eevdf()`: EEVDF 选择算法
- `entity_eligible()`: 实体合格性检查

### 关键概念
- **vruntime**: CFS 公平性核心，按实际时间 × (NICE_0_LOAD / weight) 计算
- **lag**: `w_i * (V - v_i)`，lag >= 0 的实体才能被选中
- **EEVDF**: Earliest Eligible Virtual Deadline First
- **PICK_BUDDY**: 优化策略，优先选择 next buddy

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| calc_delta_fair | kernel/sched/fair.c:290 |
| update_curr | kernel/sched/fair.c:1286 |
| place_entity | kernel/sched/fair.c:5165 |
| __enqueue_entity | kernel/sched/fair.c:914 |
| __dequeue_entity | kernel/sched/fair.c:923 |
| pick_eevdf | kernel/sched/fair.c:1010 |
| entity_eligible | kernel/sched/fair.c:813 |

---

## 3. RT 调度器 (sched_rt.md)

### 关键内容
- `struct rt_rq`: active (优先级数组), rt_nr_running
- `struct rt_prio_array`: bitmap + queue[]，O(1) 选择
- `enqueue_task_rt()`: 入队到优先级链表
- `pick_next_task_rt()`: `sched_find_first_bit()` O(1) 找到最高优先级
- `push_rt_task()` / `pull_rt_task()`: 多 CPU 间迁移
- RT-throttling: `sched_rt_runtime_exceeded()`

### RT vs CFS 对比
| 特性 | RT | CFS |
|------|-----|-----|
| 调度目标 | 优先级保证 | 公平性 |
| 数据结构 | 优先级位图+链表 | 红黑树(vruntime) |
| 选择算法 | O(1) | O(log n) |
| 饥饿问题 | 可能 | 不可能 |

### Deadline 调度器
- `struct sched_dl_entity`: dl_runtime, dl_deadline, dl_period
- `CBS` 算法: Constant Bandwidth Server
- replenishment 定时器补充 runtime

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| enqueue_task_rt | kernel/sched/rt.c:1431 |
| pick_next_task_rt | kernel/sched/rt.c:1671 |
| push_rt_task | kernel/sched/rt.c:1939 |
| pull_rt_task | kernel/sched/rt.c:2240 |
| sched_rt_runtime_exceeded | kernel/sched/rt.c:863 |

---

## 4. 调度类框架 (sched_class.md)

### 关键内容
- `struct sched_class`: 函数指针接口定义
- 调度类优先级顺序 (链接脚本保证):
  ```
  stop > dl > rt > fair > ext > idle
  ```
- `DEFINE_SCHED_CLASS()`: 链接段属性
- `for_each_active_class()`: 遍历调度类

### sched_class 函数指针
| 类型 | 函数指针 | 用途 |
|------|----------|------|
| 任务队列 | `enqueue_task`, `dequeue_task` | 入队/出队 |
| 选取任务 | `pick_task`, `pick_next_task` | 核心调度决策 |
| 任务切换 | `put_prev_task`, `set_next_task` | 上下文切换支持 |
| 负载均衡 | `balance`, `find_lock_rq` | 多 CPU 负载均衡 |
| 事件处理 | `task_tick`, `task_woken` | 各种调度事件 |

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| struct sched_class | kernel/sched/sched.h:2500 |
| DEFINE_SCHED_CLASS | kernel/sched/sched.h:2709 |
| __pick_next_task | kernel/sched/core.c:5909 |
| __setscheduler_class | kernel/sched/core.c:7254 |

---

## 5. 上下文切换 (sched_context_switch.md)

### 关键内容
- `context_switch()`: MM 切换 + `switch_to()`
- `prepare_task_switch()`: 切换前准备
- `finish_task_switch()`: 切换后清理
- `__schedule()`: 调度器主体
- `switch_to()`: 汇编层面寄存器/栈切换
- `__switch_to()`: FPU, TLS, 段寄存器切换

### 切换流程
```
__schedule()
  └─> context_switch()
       ├─> prepare_task_switch()
       ├─> MM 切换: enter_lazy_tlb() / switch_mm_irqs_off()
       ├─> switch_to(prev, next, prev)
       │     ├─> __switch_to_asm(): 寄存器, 栈指针
       │     └─> __switch_to(): FPU, TLS, 段寄存器
       └─> finish_task_switch()
```

### 状态保存/恢复
| 状态类型 | 保存位置 |
|---------|---------|
| 通用寄存器 (rbx, rbp, r12-r15) | __switch_to_asm 栈帧 |
| 栈指针 (rsp) | task_struct->thread.sp |
| FPU/SSE/AVX | task_struct->thread.fpu |
| TLS | GDT/LDT via load_TLS() |

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| context_switch | kernel/sched/core.c:5239 |
| prepare_task_switch | kernel/sched/core.c:5080 |
| finish_task_switch | kernel/sched/core.c:5112 |
| __schedule | kernel/sched/core.c:6764 |
| switch_to | arch/x86/include/asm/switch_to.h:49 |
| __switch_to_asm | arch/x86/entry/entry_64.S:177 |

---

## 6. 负载均衡 (sched_load_balance.md)

### 关键内容
- `struct sched_domain`: 层次结构定义
- `struct sched_group`: 组容量, cpumask
- `detach_tasks()`: 从源 CPU 分离任务
- `attach_tasks()`: 附加到目标 CPU
- `sched_balance_rq()`: 核心均衡函数
- `sched_balance_newidle()`: CPU idle 时触发
- 调度域层次: SMT → CLS → MC → PKG → NUMA

### 组类型 (group_type)
- `group_has_spare`: 有备用容量
- `group_fully_busy`: 完全使用
- `group_misfit_task`: 任务不适合当前 CPU
- `group_overloaded`: CPU 过载

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| detach_tasks | kernel/sched/fair.c:9648 |
| attach_tasks | kernel/sched/fair.c:9813 |
| sched_balance_rq | kernel/sched/fair.c:11865 |
| sched_balance_newidle | kernel/sched/fair.c:12922 |
| sched_balance_domains | kernel/sched/fair.c:12331 |
| struct sched_domain | include/linux/sched/topology.h:73 |

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │         用户空间进程                     │
                    └─────────────────┬───────────────────────┘
                                      │
                                      │ sched_submit_work()
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │      schedule() / __schedule()           │
                    │  ┌─────────────────────────────────────┐│
                    │  │ pick_next_task()                    ││
                    │  │   for_each_active_class(class) {    ││
                    │  │     class->pick_next_task()         ││
                    │  │   }                                 ││
                    │  └─────────────────────────────────────┘│
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │  context_switch()      │               │   调度类实现          │
        │  ├─> MM 切换           │               │  ├─> stop_sched_class │
        │  ├─> switch_to()      │               │  ├─> dl_sched_class   │
        │  └─> finish_task()   │               │  ├─> rt_sched_class   │
        └───────────────────────┘               │  ├─> fair_sched_class │
                                                │  └─> idle_sched_class │
        ┌───────────────────────┐               └───────────────────────┘
        │  struct rq            │
        │  ├─> cfs_rq          │
        │  ├─> rt_rq           │
        │  ├─> dl_rq           │
        │  └─> nr_running      │
        └───────────────────────┘

调度域层次 (负载均衡):
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  SMT    │ → │  CLS    │ → │  MC     │ → │  PKG    │ → NUMA
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## 深度分析

- [sched_deep_dive_r1.md](sched_deep_dive_r1.md) - 深度分析 R1: CFS/EEVDF, RT调度器, Load Balancing, sched_domain, pick_next_task
- [sched_deep_dive_r2.md](sched_deep_dive_r2.md) - 深度分析 R2: pick_eevdf, calc_delta_fair, update_curr, enqueue_entity, dequeue_entity, task_numa_placement (待完善)
