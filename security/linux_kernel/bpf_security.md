# Linux 内核 BPF (Berkeley Packet Filter) 安全机制详细分析

## 目录

1. [BPF 系统调用](#1-bpf-系统调用)
2. [BPF 验证器](#2-bpf-验证器)
3. [BPF 沙箱机制](#3-bpf-沙箱机制)
4. [BPF 映射 (Map)](#4-bpf-映射-map)
5. [BPF 程序类型](#5-bpf-程序类型)
6. [JIT 编译](#6-jit-编译)
7. [安全机制总结](#7-安全机制总结)

---

## 1. BPF 系统调用

### 1.1 系统调用入口

BPF 系统调用的入口定义在 `/Users/sphinx/github/linux/kernel/bpf/syscall.c:6360`:

```c
SYSCALL_DEFINE3(bpf, int, cmd, union bpf_attr __user *, uattr, unsigned int, size)
{
    return __sys_bpf(cmd, USER_BPFPTR(uattr), size);
}
```

### 1.2 BPF 命令 (enum bpf_cmd)

定义在 `/Users/sphinx/github/linux/include/uapi/linux/bpf.h:955-997`:

```c
enum bpf_cmd {
    BPF_MAP_CREATE,           // 创建 BPF 映射
    BPF_MAP_LOOKUP_ELEM,     // 查找映射元素
    BPF_MAP_UPDATE_ELEM,     // 更新映射元素
    BPF_MAP_DELETE_ELEM,     // 删除映射元素
    BPF_MAP_GET_NEXT_KEY,    // 获取下一个键
    BPF_PROG_LOAD,           // 加载 BPF 程序
    BPF_OBJ_PIN,             // 将对象固定到文件系统
    BPF_OBJ_GET,             // 获取固定的对象
    BPF_PROG_ATTACH,         // 附加 BPF 程序
    BPF_PROG_DETACH,         // 分离 BPF 程序
    BPF_PROG_TEST_RUN,       // 测试运行 BPF 程序
    BPF_PROG_GET_NEXT_ID,    // 获取下一个程序 ID
    BPF_MAP_GET_NEXT_ID,     // 获取下一个映射 ID
    // ... 更多命令
    BPF_TOKEN_CREATE,        // 创建 BPF Token (用于细粒度权限控制)
    // ...
};
```

### 1.3 BPF_PROG_LOAD 流程

`bpf_prog_load()` 函数 (`/Users/sphinx/github/linux/kernel/bpf/syscall.c:2871`) 是加载 BPF 程序的核心:

```c
static int bpf_prog_load(union bpf_attr *attr, bpfptr_t uattr, u32 uattr_size)
{
    // 1. 权限检查
    bpf_cap = bpf_token_capable(token, CAP_BPF);

    // 2. 指令数量限制
    if (attr->insn_cnt == 0 ||
        attr->insn_cnt > (bpf_cap ? BPF_COMPLEXITY_LIMIT_INSNS : BPF_MAXINSNS)) {
        err = -E2BIG;
        goto put_token;
    }

    // 3. 非特权用户限制
    if (type != BPF_PROG_TYPE_SOCKET_FILTER &&
        type != BPF_PROG_TYPE_CGROUP_SKB &&
        !bpf_cap)
        goto put_token;

    // 4. 网络管理权限检查
    if (is_net_admin_prog_type(type) && !bpf_token_capable(token, CAP_NET_ADMIN))
        goto put_token;

    // 5. 性能监控权限检查
    if (is_perfmon_prog_type(type) && !bpf_token_capable(token, CAP_PERFMON))
        goto put_token;

    // 6. 安全模块检查 (SELinux/AppArmor)
    err = security_bpf_prog_load(prog, attr, token, uattr.is_kernel);

    // 7. 运行 BPF 验证器
    err = bpf_check(&prog, attr, uattr, uattr_size);

    // 8. 选择运行时 (JIT 或解释器)
    prog = bpf_prog_select_runtime(prog, &err);
}
```

### 1.4 权限分类

定义在 `/Users/sphinx/github/linux/kernel/bpf/syscall.c:2759-2798`:

```c
// 需要 CAP_NET_ADMIN 权限的程序类型
static bool is_net_admin_prog_type(enum bpf_prog_type prog_type)
{
    switch (prog_type) {
    case BPF_PROG_TYPE_SCHED_CLS:  // 调度分类器
    case BPF_PROG_TYPE_SCHED_ACT:  // 调度动作
    case BPF_PROG_TYPE_XDP:        // 快速数据包处理
    case BPF_PROG_TYPE_LWT_IN:
    case BPF_PROG_TYPE_LWT_OUT:
    case BPF_PROG_TYPE_LWT_XMIT:
    // ... 更多网络相关类型
    return true;
    }
}

// 需要 CAP_PERFMON 权限的程序类型
static bool is_perfmon_prog_type(enum bpf_prog_type prog_type)
{
    switch (prog_type) {
    case BPF_PROG_TYPE_KPROBE:      // 内核探针
    case BPF_PROG_TYPE_TRACEPOINT:  // 跟踪点
    case BPF_PROG_TYPE_PERF_EVENT: // 性能事件
    case BPF_PROG_TYPE_RAW_TRACEPOINT:
    // ...
    return true;
    }
}

// 无特权用户可加载的程序类型 (仅需 CAP_BPF)
static bool is_unprivileged_allow(enum bpf_prog_type prog_type)
{
    switch (prog_type) {
    case BPF_PROG_TYPE_CGROUP_SKB:  // 始终允许
    case BPF_PROG_TYPE_SK_REUSEPORT: // 相当于 SOCKET_FILTER
    default:
        return false;
    }
}
```

---

## 2. BPF 验证器

### 2.1 验证器概述

BPF 验证器 (`/Users/sphinx/github/linux/kernel/bpf/verifier.c`) 是 BPF 安全的核心组件。它通过静态分析确保 BPF 程序不会危害系统。

**验证器文档注释** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:56-70`):

```c
/* bpf_check() is a static code analyzer that walks eBPF program
 * instruction by instruction and updates register/stack state.
 * All paths of conditional branches are analyzed until 'bpf_exit' insn.
 *
 * The first pass is depth-first-search to check that the program is a DAG.
 * It rejects the following programs:
 * - larger than BPF_MAXINSNS insns
 * - if loop is present (detected via back-edge)
 * - unreachable insns exist (shouldn't be a forest. program = one function)
 * - out of bounds or malformed jumps
 * The second pass is all possible path descent from the 1st insn.
 * Since it's analyzing all paths through the program, the length of the
 * analysis is limited to 64k insn, which may be hit even if total number of
 * insn is less then 4K, but there are too many branches that change stack/regs.
 * Number of 'branches to be analyzed' is limited to 1k
 */
```

### 2.2 BPF 指令结构

定义在 `/Users/sphinx/github/linux/include/uapi/linux/bpf.h:80-86`:

```c
struct bpf_insn {
    __u8    code;       /* 操作码 */
    __u8    dst_reg:4;  /* 目标寄存器 (0-9) */
    __u8    src_reg:4;  /* 源寄存器 (0-9) */
    __s16   off;        /* 有符号偏移量 */
    __s32   imm;        /* 有符号立即数 */
};
```

### 2.3 寄存器类型 (enum bpf_reg_type)

BPF 验证器使用多种寄存器类型来跟踪值:

```c
enum bpf_reg_type {
    NOT_INIT = 0,           // 未初始化
    SCALAR_VALUE,           // 标量值 (不是指针)
    PTR_TO_CTX,             // 指向上下文的指针 (如 sk_buff)
    PTR_TO_MAP_KEY,         // 指向映射键的指针
    PTR_TO_MAP_VALUE,       // 指向映射值的指针
    PTR_TO_STACK,           // 指向栈的指针
    PTR_TO_SOCKET,          // 指向套接字的指针
    PTR_TO_SOCK_COMMON,     // 指向 sock_common 的指针
    // ... 更多指针类型
};
```

### 2.4 验证器环境结构

定义在 `/Users/sphinx/github/linux/include/linux/bpf_verifier.h:748-789`:

```c
struct bpf_verifier_env {
    u32 insn_idx;              // 当前指令索引
    u32 prev_insn_idx;
    struct bpf_prog *prog;    // 被验证的 BPF 程序
    const struct bpf_verifier_ops *ops;
    struct bpf_verifier_stack_elem *head; // 验证状态栈
    int stack_size;           // 待处理状态数
    bool strict_alignment;    // 执行严格指针对齐检查
    bool test_state_freq;     // 使用不同修剪频率测试验证器
    struct bpf_verifier_state *cur_state; // 当前验证状态
    struct list_head *explored_states; // 搜索修剪优化
    struct bpf_map *used_maps[MAX_USED_MAPS]; // 程序使用的映射
    u32 used_map_cnt;
    u32 id_gen;               // 生成唯一寄存器 ID
    bool allow_ptr_leaks;     // 允许指针泄漏 (仅特权)
    bool allow_uninit_stack;  // 允许访问未初始化栈内存
    bool bpf_capable;         // 是否具有 CAP_BPF 权限
    bool bypass_spec_v1;       // 绕过安全检查 v1
    bool bypass_spec_v4;      // 绕过安全检查 v4
    struct bpf_insn_aux_data *insn_aux_data; // 每条指令的辅助状态
    // ...
};
```

### 2.5 check_cfg() - 控制流图检查

定义在 `/Users/sphinx/github/linux/kernel/bpf/verifier.c:18953-19039`:

```c
static int check_cfg(struct bpf_verifier_env *env)
{
    int insn_cnt = env->prog->len;
    int *insn_stack, *insn_state;

    // 分配状态和栈数组
    insn_state = env->cfg.insn_state = kvzalloc_objs(int, insn_cnt, GFP_KERNEL_ACCOUNT);
    insn_stack = env->cfg.insn_stack = kvzalloc_objs(int, insn_cnt, GFP_KERNEL_ACCOUNT);

    insn_state[0] = DISCOVERED;
    insn_stack[0] = 0;
    env->cfg.cur_stack = 1;

walk_cfg:
    while (env->cfg.cur_stack > 0) {
        int t = insn_stack[env->cfg.cur_stack - 1];
        ret = visit_insn(t, env);
        // 处理 DONE_EXPLORING, KEEP_EXPLORING 或错误
    }

    // 检查是否有未到达的指令
    for (i = 0; i < insn_cnt; i++) {
        if (insn_state[i] != EXPLORED) {
            verbose(env, "unreachable insn %d\n", i);
            ret = -EINVAL;
            goto err_free;
        }
        // 检查 ldimm64 指令完整性
        if (bpf_is_ldimm64(insn)) {
            if (insn_state[i + 1] != 0) {
                verbose(env, "jump into the middle of ldimm64 insn %d\n", i);
                ret = -EINVAL;
                goto err_free;
            }
            i++;
        }
    }
}
```

**check_cfg() 安全检查**:
- 检测循环 (通过回边检测)
- 检测不可达指令
- 检测跳转到 ldimm64 指令中间
- 确保程序是一个单一函数 (非森林)

### 2.6 check_subprogs() - 子程序检查

定义在 `/Users/sphinx/github/linux/kernel/bpf/verifier.c:3686-3684`:

```c
static int check_subprogs(struct bpf_verifier_env *env)
{
    // 检查所有跳转都在同一子程序内
    for (i = 0; i < insn_cnt; i++) {
        // 验证跳转目标在当前子程序范围内
        if (跳转目标不在当前子程序) {
            verbose(env, "jump out of subprog %d\n", cur_subprog);
            return -EINVAL;
        }
    }
}
```

### 2.7 do_check() - 主验证循环

定义在 `/Users/sphinx/github/linux/kernel/bpf/verifier.c:21244-21365`:

```c
static int do_check(struct bpf_verifier_env *env)
{
    for (;;) {
        struct bpf_insn *insn = &insns[env->insn_idx];

        // 检查指令处理数量限制
        if (++env->insn_processed > BPF_COMPLEXITY_LIMIT_INSNS) {
            verbose(env, "BPF program is too large. Processed %d insn\n",
                    env->insn_processed);
            return -E2BIG;
        }

        // 检查是否需要剪枝
        if (is_prune_point(env, env->insn_idx)) {
            err = is_state_visited(env, env->insn_idx);
            if (err == 1) {
                // 发现等价状态，可以剪枝搜索
                goto process_bpf_exit;
            }
        }

        // 处理每条指令
        err = do_check_insn(env, &do_print_state);
        if (err >= 0) {
            marks_err = bpf_commit_stack_write_marks(env);
        }

        env->insn_idx++;
    }
}
```

### 2.8 check_helper_call() - 辅助函数调用检查

定义在 `/Users/sphinx/github/linux/kernel/bpf/verifier.c:11640-11750`:

```c
static int check_helper_call(struct bpf_verifier_env *env, struct bpf_insn *insn, int *insn_idx_p)
{
    enum bpf_prog_type prog_type = resolve_prog_type(env->prog);
    const struct bpf_func_proto *fn = NULL;

    // 1. 获取函数原型
    func_id = insn->imm;
    err = get_helper_proto(env, insn->imm, &fn);

    // 2. 检查上下文
    err = check_context_access(env, insn, off, size, type, info);

    // 3. 检查参数类型
    for (i = 0; i < 5; i++) {
        err = check_func_arg(env, reg, arg_type, &meta);
    }

    // 4. 记录参考对象
    if (fn->ret_type == RET_PTR_TO_MEM ||
        fn->ret_type == RET_PTR_TO_MAP_VALUE_OR_NULL) {
        err = acquire_reference(env, insn_idx);
    }
}
```

---

## 3. BPF 沙箱机制

### 3.1 指令限制

**最大指令数限制** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:21271`):

```c
// 复杂程序限制
if (++env->insn_processed > BPF_COMPLEXITY_LIMIT_INSNS) {
    return -E2BIG;
}

// 非特权用户限制更严格
if (attr->insn_cnt > (bpf_cap ? BPF_COMPLEXITY_LIMIT_INSNS : BPF_MAXINSNS)) {
    return -E2BIG;
}
```

**复杂度限制常量** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:195-196`):

```c
#define BPF_COMPLEXITY_LIMIT_JMP_SEQ  8192   // 最大跳转序列复杂度
#define BPF_COMPLEXITY_LIMIT_STATES   64     // 每个指令的最大状态数
```

### 3.2 内存访问限制

**栈大小限制** (`/Users/sphinx/github/linux/include/linux/filter.h:99`):

```c
/* BPF program can access up to 512 bytes of stack space. */
#define MAX_BPF_STACK  512
```

**栈边界检查** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:7604-7617`):

```c
static int check_stack_slot_within_bounds(struct bpf_verifier_env *env,
                                          s64 off, struct bpf_func_state *state,
                                          enum bpf_access_type t)
{
    int min_valid_off;

    if (t == BPF_WRITE || env->allow_uninit_stack)
        min_valid_off = -MAX_BPF_STACK;  // -512
    else
        min_valid_off = -state->allocated_stack;

    if (off < min_valid_off || off > -1)
        return -EACCES;
}
```

**内存访问检查** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:5854-5880`):

```c
static int __check_mem_access(struct bpf_verifier_env *env, int regno,
                              int off, int size, u32 mem_size,
                              bool zero_size_allowed)
{
    bool size_ok = size > 0 || (size == 0 && zero_size_allowed);

    // 基本边界检查
    if (off >= 0 && size_ok && (u64)off + size <= mem_size)
        return 0;

    // 根据寄存器类型给出具体错误信息
    switch (reg->type) {
    case PTR_TO_MAP_KEY:
        verbose(env, "invalid access to map key, key_size=%d off=%d size=%d\n", ...);
        break;
    case PTR_TO_MAP_VALUE:
        verbose(env, "invalid access to map value, value_size=%d off=%d size=%d\n", ...);
        break;
    // ...
    }
    return -EACCES;
}
```

**变量偏移量限制** (`/Users/sphinx/github/linux/include/linux/bpf_verifier.h:16`):

```c
#define BPF_MAX_VAR_OFF (1 << 29)  // 约 512MB
```

### 3.3 辅助函数白名单

**BPF 辅助函数 ID 枚举** (`/Users/sphinx/github/linux/include/uapi/linux/bpf.h:6130-6134`):

```c
enum bpf_func_id {
    BPF_FUNC_map_lookup_elem = 1,
    BPF_FUNC_map_update_elem = 2,
    BPF_FUNC_map_delete_elem = 3,
    BPF_FUNC_probe_read = 4,
    BPF_FUNC_ktime_get_ns = 5,
    // ... 更多函数 (共 211 个)
    __BPF_FUNC_MAX_ID,
};
```

**辅助函数调用检查** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:11620-11628`):

```c
static int get_helper_proto(struct bpf_verifier_env *env, int func_id,
                           const struct bpf_func_proto **ptr)
{
    if (func_id < 0 || func_id >= __BPF_FUNC_MAX_ID)
        return -ERANGE;

    if (!env->ops->get_func_proto)
        return -EINVAL;

    *ptr = env->ops->get_func_proto(func_id, env->prog);
    return *ptr && (*ptr)->func ? 0 : -EINVAL;
}
```

**每个程序类型有其自己的辅助函数集合**:

```c
// sched_cls、xdp 等程序类型允许的辅助函数
case BPF_PROG_TYPE_SCHED_CLS:
case BPF_PROG_TYPE_SCHED_ACT:
case BPF_PROG_TYPE_XDP:
case BPF_PROG_TYPE_SK_SKB:
case BPF_PROG_TYPE_SK_MSG:
    // 允许访问网络数据包和映射
```

### 3.4 指针操作限制

**指针算术限制** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:14510-14535`):

```c
if (known && (val >= BPF_MAX_VAR_OFF || val <= -BPF_MAX_VAR_OFF)) {
    verbose(env, "math between %s pointer and %lld is not allowed\n", ...);
    return false;
}

if (reg->off >= BPF_MAX_VAR_OFF || reg->off <= -BPF_MAX_VAR_OFF) {
    verbose(env, "%s pointer offset %d is not allowed\n", ...);
    return false;
}

if (smin >= BPF_MAX_VAR_OFF || smin <= -BPF_MAX_VAR_OFF) {
    verbose(env, "value %lld makes %s pointer be out of bounds\n", ...);
    return false;
}
```

**禁止指针到标量值转换** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:8243-8246`):

```c
if (!env->allow_ptr_leaks && reg->type == SCALAR_VALUE &&
    is_spillable_regtype(ptr_reg->type)) {
    verbose(env, "R%d variable offset stack access prohibited for !root\n", ...);
    return -EACCES;
}
```

### 3.5 特殊安全标志

```c
struct bpf_verifier_env {
    bool bypass_spec_v1;    // 绕过推测执行检查 v1 (Spectre v1)
    bool bypass_spec_v4;   // 绕过推测执行检查 v4 (Spectre v4)
    bool allow_ptr_leaks;  // 允许指针泄漏 (仅调试用)
    bool allow_uninit_stack; // 允许访问未初始化栈
};
```

---

## 4. BPF 映射 (Map)

### 4.1 bpf_map 结构

定义在 `/Users/sphinx/github/linux/include/linux/bpf.h:296-339`:

```c
struct bpf_map {
    u8 sha[SHA256_DIGEST_SIZE];           // 映射内容的哈希
    const struct bpf_map_ops *ops;       // 映射操作函数集
    struct bpf_map *inner_map_meta;       // 内部映射元数据
#ifdef CONFIG_SECURITY
    void *security;                       // 安全模块数据
#endif
    enum bpf_map_type map_type;           // 映射类型
    u32 key_size;                         // 键大小
    u32 value_size;                       // 值大小
    u32 max_entries;                      // 最大条目数
    u64 map_extra;                         // 特定类型额外数据
    u32 map_flags;                         // 映射标志
    u32 id;                                // 映射 ID
    struct btf_record *record;             // BTF 记录
    int numa_node;                         // NUMA 节点
    struct btf *btf;                        // BTF 数据
    char name[BPF_OBJ_NAME_LEN];           // 映射名称
    atomic64_t refcnt;                     // 引用计数
    atomic64_t usercnt;                    // 用户计数
    bool frozen;                           // 是否冻结 (只读)
    // ...
};
```

### 4.2 映射类型 (enum bpf_map_type)

定义在 `/Users/sphinx/github/linux/include/uapi/linux/bpf.h:999-1049`:

| 类型 | 说明 | 权限要求 |
|------|------|----------|
| BPF_MAP_TYPE_HASH | 哈希映射 | CAP_BPF |
| BPF_MAP_TYPE_ARRAY | 数组映射 | CAP_BPF |
| BPF_MAP_TYPE_PROG_ARRAY | 程序数组 | CAP_BPF |
| BPF_MAP_TYPE_PERF_EVENT_ARRAY | 性能事件数组 | CAP_BPF |
| BPF_MAP_TYPE_PERCPU_HASH | 每 CPU 哈希 | CAP_BPF |
| BPF_MAP_TYPE_LRU_HASH | LRU 哈希 | CAP_BPF |
| BPF_MAP_TYPE_SOCKMAP | 套接字映射 | CAP_NET_ADMIN |
| BPF_MAP_TYPE_DEVMAP | 设备映射 | CAP_NET_ADMIN |
| BPF_MAP_TYPE_XSKMAP | XDP 套接字映射 | CAP_NET_ADMIN |
| BPF_MAP_TYPE_CGROUP_ARRAY | Cgroup 数组 | CAP_BPF |
| BPF_MAP_TYPE_RINGBUF | 环形缓冲区 | CAP_BPF |
| BPF_MAP_TYPE_ARENA | BPF 内存区域 | CAP_BPF |

### 4.3 映射操作函数集

定义在 `/Users/sphinx/github/linux/include/linux/bpf.h:83-187`:

```c
struct bpf_map_ops {
    /* 用户空间可调用的函数 (通过系统调用) */
    int (*map_alloc_check)(union bpf_attr *attr);
    struct bpf_map *(*map_alloc)(union bpf_attr *attr);
    void (*map_free)(struct bpf_map *map);
    int (*map_get_next_key)(struct bpf_map *map, void *key, void *next_key);

    /* 用户空间和 eBPF 程序都可调用的函数 */
    void *(*map_lookup_elem)(struct bpf_map *map, void *key);
    long (*map_update_elem)(struct bpf_map *map, void *key, void *value, u64 flags);
    long (*map_delete_elem)(struct bpf_map *map, void *key);
    long (*map_push_elem)(struct bpf_map *map, void *value, u64 flags);
    long (*map_pop_elem)(struct bpf_map *map, void *value);

    /* 直接值访问 */
    int (*map_direct_value_addr)(const struct bpf_map *map, u64 *imm, u32 off);
    int (*map_direct_value_meta)(const struct bpf_map *map, u64 imm, u32 *off);
    // ...
};
```

### 4.4 映射创建权限检查

定义在 `/Users/sphinx/github/linux/kernel/bpf/syscall.c:1447-1505`:

```c
// 检查 unprivileged_bpf_disabled 设置
if (sysctl_unprivileged_bpf_disabled && !bpf_token_capable(token, CAP_BPF))
    goto put_token;

// 根据映射类型检查权限
switch (map_type) {
case BPF_MAP_TYPE_ARRAY:
case BPF_MAP_TYPE_PERCPU_ARRAY:
case BPF_MAP_TYPE_PROG_ARRAY:
    // ... 基本类型
    if (!bpf_token_capable(token, CAP_BPF))
        goto put_token;
    break;

case BPF_MAP_TYPE_SOCKMAP:
case BPF_MAP_TYPE_SOCKHASH:
case BPF_MAP_TYPE_DEVMAP:
case BPF_MAP_TYPE_XSKMAP:
    // 网络相关类型需要 CAP_NET_ADMIN
    if (!bpf_token_capable(token, CAP_NET_ADMIN))
        goto put_token;
    break;
}
```

---

## 5. BPF 程序类型

### 5.1 程序类型枚举 (enum bpf_prog_type)

定义在 `/Users/sphinx/github/linux/include/uapi/linux/bpf.h:1060-1094`:

```c
enum bpf_prog_type {
    BPF_PROG_TYPE_UNSPEC,
    BPF_PROG_TYPE_SOCKET_FILTER,     // 套接字过滤器 (非特权)
    BPF_PROG_TYPE_KPROBE,            // KPROBE 探针
    BPF_PROG_TYPE_SCHED_CLS,         // 调度分类器 (网络)
    BPF_PROG_TYPE_SCHED_ACT,         // 调度动作
    BPF_PROG_TYPE_TRACEPOINT,        // 跟踪点
    BPF_PROG_TYPE_XDP,              // 快速数据包处理
    BPF_PROG_TYPE_PERF_EVENT,       // 性能事件
    BPF_PROG_TYPE_CGROUP_SKB,       // Cgroup 套接字过滤 (非特权)
    BPF_PROG_TYPE_CGROUP_SOCK,      // Cgroup 套接字
    BPF_PROG_TYPE_LWT_IN,           // LWT 入口
    BPF_PROG_TYPE_LWT_OUT,          // LWT 出口
    BPF_PROG_TYPE_LWT_XMIT,         // LWT 传输
    BPF_PROG_TYPE_SOCK_OPS,         // 套接字选项
    BPF_PROG_TYPE_SK_SKB,           // 套接字 SKB
    BPF_PROG_TYPE_CGROUP_DEVICE,   // Cgroup 设备
    BPF_PROG_TYPE_SK_MSG,           // 套接字消息
    BPF_PROG_TYPE_RAW_TRACEPOINT,   // 原始跟踪点
    BPF_PROG_TYPE_CGROUP_SOCK_ADDR, // Cgroup 套接字地址
    BPF_PROG_TYPE_LWT_SEG6LOCAL,    // SEG6 本地
    BPF_PROG_TYPE_LIRC_MODE2,       // LIRC 模式 2
    BPF_PROG_TYPE_SK_REUSEPORT,     // 套接字重用端口
    BPF_PROG_TYPE_FLOW_DISSECTOR,   // 流解析器
    BPF_PROG_TYPE_CGROUP_SYSCTL,    // Cgroup 系统控制
    BPF_PROG_TYPE_RAW_TRACEPOINT_WRITABLE, // 可写原始跟踪点
    BPF_PROG_TYPE_CGROUP_SOCKOPT,   // Cgroup 套接字选项
    BPF_PROG_TYPE_TRACING,          // 跟踪 (fentry/fexit/modify_return)
    BPF_PROG_TYPE_STRUCT_OPS,       // 结构操作
    BPF_PROG_TYPE_EXT,              // 扩展程序
    BPF_PROG_TYPE_LSM,             // Linux 安全模块
    BPF_PROG_TYPE_SK_LOOKUP,       // 套接字查找
    BPF_PROG_TYPE_SYSCALL,         // 系统调用程序
    BPF_PROG_TYPE_NETFILTER,       // 网络过滤器
};
```

### 5.2 各程序类型的辅助函数权限

**SCHED_CLS (调度分类器)** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:6322-6327`):

```c
case BPF_PROG_TYPE_SCHED_CLS:
case BPF_PROG_TYPE_SCHED_ACT:
case BPF_PROG_TYPE_XDP:
case BPF_PROG_TYPE_LWT_XMIT:
case BPF_PROG_TYPE_SK_SKB:
case BPF_PROG_TYPE_SK_MSG:
    // 允许直接读取和写入数据包
    return true;
```

**KPROBE 类型** (`/Users/sphinx/github/linux/kernel/bpf/verifier.c:6705-6709`):

```c
case BPF_PROG_TYPE_KPROBE:
case BPF_PROG_TYPE_TRACEPOINT:
case BPF_PROG_TYPE_PERF_EVENT:
case BPF_PROG_TYPE_RAW_TRACEPOINT:
    return PRIV_STACK_ADAPTIVE;
```

### 5.3 程序查找类型

定义在 `/Users/sphinx/github/linux/kernel/bpf/syscall.c:2268-2296`:

```c
static const struct bpf_prog_ops * const bpf_prog_types[] = {
#define BPF_PROG_TYPE(_id, _name, prog_ctx_type, kern_ctx_type) \
    [_id] = & _name ## _prog_ops,
#define BPF_MAP_TYPE(_id, _ops)
#define BPF_LINK_TYPE(_id, _name)
#include <linux/bpf_types.h>
};

static int find_prog_type(enum bpf_prog_type type, struct bpf_prog *prog)
{
    if (type >= ARRAY_SIZE(bpf_prog_types))
        return -EINVAL;

    type = array_index_nospec(type, ARRAY_SIZE(bpf_prog_types));
    ops = bpf_prog_types[type];
    if (!ops)
        return -EINVAL;

    prog->aux->ops = ops;
    prog->type = type;
    return 0;
}
```

---

## 6. JIT 编译

### 6.1 JIT 编译概述

BPF 程序可以通过 JIT 编译器编译为本机机器码以提高性能。

**JIT 入口点** (`/Users/sphinx/github/linux/kernel/bpf/core.c:3087-3090`):

```c
/* Stub for JITs that only support cBPF. eBPF programs are interpreted. */
struct bpf_prog * __weak bpf_int_jit_compile(struct bpf_prog *prog)
{
    return prog;
}

/* Stub for JITs that support eBPF. */
void __weak bpf_jit_compile(struct bpf_prog *prog)
{
}
```

### 6.2 bpf_prog_select_runtime()

定义在 `/Users/sphinx/github/linux/kernel/bpf/core.c:2546-2599`:

```c
struct bpf_prog *bpf_prog_select_runtime(struct bpf_prog *fp, int *err)
{
    bool jit_needed = false;

    // 如果已有函数指针，说明已完成
    if (fp->bpf_func)
        goto finalize;

    // 检查是否需要 JIT
    if (IS_ENABLED(CONFIG_BPF_JIT_ALWAYS_ON) ||
        bpf_prog_has_kfunc_call(fp))
        jit_needed = true;

    if (!bpf_prog_select_interpreter(fp))
        jit_needed = true;

    // JIT 编译
    if (jit_needed)
        fp = bpf_int_jit_compile(fp);

finalize:
    *err = bpf_prog_lock_ro(fp);  // 锁定只读
    *err = bpf_check_tail_call(fp);  // 尾调用兼容性检查

    return fp;
}
```

### 6.3 x86_64 JIT 编译器

位置: `/Users/sphinx/github/linux/arch/x86/net/bpf_jit_comp.c`

**关键函数**:

```c
struct bpf_binary_header {
    u32 size;              // 整个人员的大小
    u8  image[];          // JIT 编码的指令
};

static int bpf_jit_blind_constants(struct bpf_prog *fp)
// 混淆常量以防止信息泄漏

static int bpf_jit_emit_body(struct bpf_jit_comp *ctx)
// 发出 JIT 编译的指令

int bpf_int_jit_compile(struct bpf_prog *fp)
// 主 JIT 编译入口
```

### 6.4 JIT 安全措施

**1. 代码锁定只读** (`/Users/sphinx/github/linux/kernel/bpf/core.c:2587`):

```c
*err = bpf_prog_lock_ro(fp);  // 防止代码被修改
```

**2. 常量盲化** (`/Users/sphinx/github/linux/arch/x86/net/bpf_jit_comp.c`):

```c
static int bpf_jit_blind_constants(struct bpf_prog *fp)
{
    // 将敏感常量替换为随机数，计算时再恢复
    // 防止 JIT 代码泄漏敏感值
}
```

**3. ENDBR 指令** (间接分支目标标记):

```c
#ifdef CONFIG_X86_KERNEL_IBT
#define EMIT_ENDBR() EMIT(gen_endbr(), 4)
#else
#define EMIT_ENDBR()
#endif
```

---

## 7. 安全机制总结

### 7.1 BPF 安全机制层次图

```
+----------------------------------------------------------+
|                    用户空间                                |
|  bpf() syscall                                           |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    Capability 检查                         |
|  CAP_BPF, CAP_NET_ADMIN, CAP_PERFMON                     |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    程序类型检查                            |
|  is_net_admin_prog_type(), is_perfmon_prog_type()        |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    BPF 验证器 (核心)                       |
|  +----------------------------------------------------+  |
|  | check_cfg()     - 控制流图检查 (检测循环)            |  |
|  | check_subprogs() - 子程序检查                       |  |
|  | do_check()     - 指令逐条验证                        |  |
|  | check_helper_call() - 辅助函数调用检查               |  |
|  | check_mem_access() - 内存访问边界检查                |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    运行时安全                             |
|  +----------------------------------------------------+  |
|  | JIT 编译 + 常量盲化                                 |  |
|  |推测执行缓解 (Spectre)                               |  |
|  | 锁定只读内存                                        |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
                          |
                          v
+----------------------------------------------------------+
|                    执行环境                               |
|  +----------------------------------------------------+  |
|  | 栈大小限制: 512 字节                               |  |
|  | 指令数量限制: 100万条 (特权) / 4096条 (非特权)     |  |
|  | 跳转序列复杂度限制: 8192                           |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
```

### 7.2 安全检查点汇总

| 检查点 | 位置 | 说明 |
|--------|------|------|
| 指令数量限制 | `syscall.c:2932` | 非特权用户最多 4096 条 |
| 复杂度限制 | `verifier.c:21271` | 最多处理 100 万条 |
| 跳转序列限制 | `verifier.c:3023` | 最多 8192 层 |
| 栈大小限制 | `filter.h:99` | 最多 512 字节 |
| 变量偏移限制 | `bpf_verifier.h:16` | 最大 512MB |
| 辅助函数白名单 | `verifier.c:11620` | 每个程序类型不同 |
| 指针算术限制 | `verifier.c:14510` | 禁止越界指针运算 |
| 内存访问边界 | `verifier.c:5854` | 严格边界检查 |
| 控制流完整性 | `verifier.c:18953` | 检测循环和不可达代码 |

### 7.3 权限要求矩阵

| 程序/映射类型 | CAP_BPF | CAP_NET_ADMIN | CAP_PERFMON |
|--------------|---------|--------------|-------------|
| SOCKET_FILTER | * | - | - |
| CGROUP_SKB | * | - | - |
| SCHED_CLS | - | * | - |
| XDP | - | * | - |
| KPROBE | - | - | * |
| TRACEPOINT | - | - | * |
| MAP (基本) | * | - | - |
| MAP (网络) | - | * | - |
| MAP (追踪) | * | - | - |

### 7.4 BPF Token 机制

BPF Token (Linux 5.15+) 提供了更细粒度的权限控制:

```c
BPF_TOKEN_CREATE  // 创建 Token
BPF_TOKEN_FD      // Token 关联到文件描述符
```

Token 允许:
- 限制可以执行的 BPF 命令
- 限制可以加载的程序类型
- 限制可以创建的映射类型
- 用户命名空间感知的权限检查

---

## 附录: 关键源码位置

| 组件 | 路径 | 说明 |
|------|------|------|
| 系统调用 | `kernel/bpf/syscall.c` | BPF syscall 实现 |
| 验证器 | `kernel/bpf/verifier.c` | 安全验证核心 |
| 核心 | `kernel/bpf/core.c` | JIT 和运行时 |
| 辅助函数 | `kernel/bpf/helpers.c` | BPF 辅助函数实现 |
| 头文件 | `include/linux/bpf.h` | 核心数据结构 |
| UAPI 头 | `include/uapi/linux/bpf.h` | 用户空间 API |
| x86 JIT | `arch/x86/net/bpf_jit_comp.c` | x86_64 JIT 编译器 |
| arm64 JIT | `arch/arm64/net/bpf_jit_comp.c` | ARM64 JIT 编译器 |
| 哈希映射 | `kernel/bpf/hashtab.c` | 哈希表映射实现 |
| 数组映射 | `kernel/bpf/arraymap.c` | 数组映射实现 |
