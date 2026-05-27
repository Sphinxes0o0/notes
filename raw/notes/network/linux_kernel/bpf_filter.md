# BPF 过滤器核心

## 1. 模块架构

### 1.1 功能概述

BPF (Berkeley Packet Filter) 是 Linux 内核提供的高性能数据包过滤框架，支持用户定义的程序来过滤和处理网络数据包。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/core/filter.c` | BPF 核心实现 (约 11000 行) |
| `include/linux/filter.h` | BPF 头定义 |
| `include/linux/bpf.h` | BPF 类型定义 |
| `kernel/bpf/verifier.c` | BPF 验证器 |

## 2. BPF 程序类型

### 2.1 BPF_PROG_TYPE

```c
// include/linux/bpf.h:1775
struct bpf_prog {
    u16 pages;              // 分配页面数
    u16 jited:1;           // JIT 编译标志
    enum bpf_prog_type type;  // 程序类型
    u32 len;               // 指令数
    u32 jited_len;         // JIT 代码长度
    unsigned int (*bpf_func)(const void *ctx, const struct bpf_insn *insn);
    struct bpf_prog_aux *aux;  // 辅助数据
    union {
        struct sock_filter *insns;    // 经典 BPF
        struct bpf_insn *insnsi;      // eBPF
    };
};
```

### 2.2 程序类型

| 类型 | 上下文 | 用途 |
|-----|-------|-----|
| `SOCKET_FILTER` | sk_buff | 套接字过滤 |
| `SCHED_CLS` | sk_buff | 流量分类 |
| `SCHED_ACT` | sk_buff | 流量动作 |
| `XDP` | xdp_buff | 快速数据路径 |
| `CGROUP_SKB` | sk_buff | Cgroup 包过滤 |
| `CGROUP_SOCK` | sock | Cgroup 套接字 |
| `SK_MSG` | sk_msg | 套接字消息 |
| `SK_LOOKUP` | sock | 套接字查找 |
| `NETFILTER` | sk_buff | Netfilter 钩子 |

## 3. BPF 指令

### 3.1 struct bpf_insn

```c
// include/linux/filter.h:12
struct bpf_insn {
    __u8  code;     // 操作码
    __u8  dst_reg:4;  // 目标寄存器
    __u8  src_reg:4;  // 源寄存器
    __s16 off;       // 偏移
    __s32 imm;       // 立即数
};
```

### 3.2 操作码分类

```c
// 加载/存储
BPF_LD   // 加载
BPF_LDX  // 加载扩展
BPF_ST   // 存储
BPF_STX  // 存储扩展

// ALU 操作
BPF_ADD  // 加法
BPF_SUB  // 减法
BPF_MUL  // 乘法
BPF_DIV  // 除法
BPF_MOD  // 取模
BPF_AND  // 与
BPF_OR   // 或
BPF_XOR  // 异或
BPF_LSH  // 左移
BPF_RSH  // 右移

// 跳转
BPF_JMP  // 跳转
BPF_JEQ  // 等于跳转
BPF_JNE  // 不等跳转
BPF_JGT  // 大于跳转
BPF_JLT  // 小于跳转

// 返回
BPF_EXIT // 退出
```

## 4. BPF 验证器

### 4.1 验证流程

```c
// kernel/bpf/verifier.c
int bpf_check(struct bpf_prog **prog, union bpf_attr *attr, unsigned int size)
{
    // 1. 重复检测
    // 2. 模拟执行
    // 3. 类型检查
    // 4. 内存访问验证
    // 5. 返回值验证
}
```

### 4.2 状态跟踪

```c
struct bpf_verifier_state {
    struct bpf_func_state *func[BPF_MAX_CALL_FRAMES];
    struct stack_slot stack[BPF_MAX_STACK];
};
```

## 5. BPF Maps

### 5.1 Map 类型

```c
// include/linux/bpf.h:806
enum bpf_map_type {
    BPF_MAP_TYPE_UNSPEC,
    BPF_MAP_TYPE_HASH,
    BPF_MAP_TYPE_ARRAY,
    BPF_MAP_TYPE_PROG_ARRAY,
    BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    BPF_MAP_TYPE_PERCPU_HASH,
    BPF_MAP_TYPE_PERCPU_ARRAY,
    BPF_MAP_TYPE_STACK_TRACE,
    BPF_MAP_TYPE_CGROUP_ARRAY,
    BPF_MAP_TYPE_LRU_HASH,
    BPF_MAP_TYPE_LRU_PERCPU_HASH,
    BPF_MAP_TYPE_LPM_TRIE,
    BPF_MAP_TYPE_ARRAY_OF_MAPS,
    BPF_MAP_TYPE_HASH_OF_MAPS,
    BPF_MAP_TYPE_DEVMAP,
    BPF_MAP_TYPE_SOCKMAP,
    BPF_MAP_TYPE_CPUMAP,
    BPF_MAP_TYPE_XSKMAP,
};
```

### 5.2 Map 操作

```c
// Map 创建
int map_create(union bpf_attr *attr) {
    // 1. 分配 map 结构
    // 2. 初始化
    // 3. 返回 fd
}

// Map 查找
void *map_lookup_elem(int fd, void *key) {
    // 1. 获取 map
    // 2. 哈希查找
    // 3. 返回值
}

// Map 更新
int map_update_elem(int fd, void *key, void *value, __u64 flags) {
    // 1. 获取 map
    // 2. 哈希插入/更新
    // 3. 返回结果
}

// Map 删除
int map_delete_elem(int fd, void *key) {
    // 1. 获取 map
    // 2. 哈希删除
    // 3. 返回结果
}
```

## 6. Socket 过滤

### 6.1 sk_filter

```c
// net/core/filter.c
int sk_filter(struct sock *sk, struct sk_buff *skb, unsigned int res)
{
    struct sk_filter *fp;

    // 1. 检查 socket
    if (!skb) return res;

    rcu_read_lock();
    fp = rcu_dereference(sk->sk_filter);
    if (fp) {
        // 运行 BPF 程序
        res = BPF_PROG_RUN(fp, skb);
    }
    rcu_read_unlock();

    return res;
}
```

### 6.2 运行 BPF

```c
// net/core/filter.c:3450
static inline u32 __bpf_prog_run(const struct bpf_prog *prog,
                                  const struct sk_buff *skb,
                                  u64 *drun_ctx)
{
    return prog->bpf_func(skb, prog->insnsi);
}
```

## 7. JIT 编译

### 7.1 JIT 架构

```c
// arch/x86/net/bpf_jit_comp.c
struct bpf_binary_header {
    u32 pages;           // 页数
    u32 size;           // 代码大小
    u32 id;             // ID
    u32 jited_len;      // JIT 后长度
};

// JIT 编译入口
struct bpf_binary_header *
bpf_jit_binary_header(void)
{
    // 为 JIT 代码分配内存
    // 标记为可执行
}
```

### 7.2 x86_64 JIT

```c
// arch/x86/net/bpf_jit.S
/* BPF 指令到 x86_64 指令的映射 */
static const u8 jmp_table[] = {
    [BPF_JEQ + 0xf0] = 0x0f, /* je */
    [BPF_JEQ + 0x0f] = 0x0f, /* je */
    [BPF_JNE] = 0x75,         /* jne */
    [BPF_JGT] = 0x77,         /* ja */
    [BPF_JLT] = 0x72,         /* jb */
    ...
};
```

## 8. tc BPF (Traffic Control)

### 8.1 SCHED_CLS

```c
// net/sched/cls_bpf.c
static int cls_bpf_classify(struct sk_buff *skb, const struct tcf_proto *tp,
                            struct tcf_result *res)
{
    struct cls_bpf_head *head = rcu_dereference(tp->root);
    struct cls_bpf_prog *prog;

    // 运行 BPF 程序
    if (prog->bpf_ops->run)
        return prog->bpf_ops->run(skb, prog->bpf_prog, &res->classid);
}
```

## 9. XDP (Express Data Path)

### 9.1 XDP 程序

```c
// net/core/filter.c
int xdp_set_prog(struct net_device *dev, struct bpf_prog *prog)
{
    struct bpf_prog *old;

    // 设置 XDP 程序
    old = xchg(&dev->xdp_prog, prog);
    if (old)
        bpf_prog_put(old);

    return 0;
}
```

### 9.2 XDP 运行

```c
// net/core/filter.c:4509
static u32 bpf_prog_run_xdp(const struct bpf_prog *prog, struct xdp_buff *xdp)
{
    return __bpf_prog_run(prog, xdp, BPF_DISPATCHER_FUNC(xdp));
}
```

## 10. BPF Syscall

### 10.1 Syscall 命令

```c
// kernel/bpf/syscall.c
enum bpf_cmd {
    BPF_MAP_CREATE,
    BPF_MAP_LOOKUP_ELEM,
    BPF_MAP_UPDATE_ELEM,
    BPF_MAP_DELETE_ELEM,
    BPF_MAP_GET_NEXT_KEY,
    BPF_PROG_LOAD,
    BPF_OBJ_GET_INFO_BY_FD,
    BPF_OBJ_PIN,
    BPF_OBJ_GET,
};
```

### 10.2 Prog Load

```c
// kernel/bpf/syscall.c:2871
int bpf_prog_load(union bpf_attr *attr, unsigned int size)
{
    // 1. 验证属性
    // 2. 分配程序
    // 3. 验证
    // 4. JIT 编译
    // 5. 返回 fd
}
```
