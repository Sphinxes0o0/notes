# eBPF Tutorial 全教程速览

> 来源：https://haolipeng.github.io/ebpf-tutorial/
> 仓库：https://github.com/haolipeng/libbpf-ebpf-beginer
> 环境：Ubuntu 24.04 (kernel 6.8+)，libbpf + C

---

## 🚀 快速开始

### Lesson 1: Hello World
**目标**：第一个 eBPF 程序 — hook `write()` 系统调用
**内核态**：定义 BPF Map 传 PID → 挂载 `tp/syscalls/sys_enter_write` → 匹配 PID 后 `bpf_printk`
**用户态**：libbpf skeleton 加载 → 将自身 PID 写入 Map → attach → 读 `/sys/kernel/debug/tracing/trace_pipe`
**核心 API**：`bpf_get_current_pid_tgid()`, `bpf_map_lookup_elem()`, `bpf_printk()`
**用户态流程**：`open() → load() → update_map() → attach() → 运行 → destroy()`

---

## 🎯 Hook 机制

### Lesson 2: Kprobe
**目标**：hook 内核函数 `do_unlinkat()`（删除文件时触发）
**核心宏**：
- `BPF_KPROBE(func_name, arg1, arg2, ...)` — 一行定义 kprobe，自动处理 pt_regs 解包
- `BPF_CORE_READ(src, field)` — CO-RE 安全读取内核结构体字段
- `PT_REGS_PARM1(ctx)` — 获取函数参数
**查找函数**：`/sys/kernel/debug/tracing/available_filter_functions` 或 `bpftrace -l 'kfunc:*'`
**关键点**：kprobe 依赖内核内部实现，不同内核版本函数签名可能变化

### Lesson 3: Uprobe
**目标**：hook 用户态程序的函数调用和返回
**场景**：生产环境排查（不能挂 gdb）、监控应用函数入参/出参/返回值
**文件**：`target.c`（被跟踪程序）+ `uprobe.bpf.c`（内核态）+ `uprobe.c`（用户态加载器）
**关键点**：uprobe 可以监控用户态程序的具体函数行为，不需要修改目标程序

### Lesson 8: Tracepoint
**目标**：使用稳定的内核 tracepoint（比 kprobe 更优）
**对比**：

| 特性 | Tracepoint | Kprobe |
|------|-----------|--------|
| 稳定性 | ✅ 稳定内核 API | ⚠️ 依赖内核实现 |
| 性能 | ✅ 开销较小 | ⚠️ 开销较大 |
| 可移植性 | ✅ 跨版本稳定 | ⚠️ 版本可能变化 |
| 灵活性 | ⚠️ 仅预定义位置 | ✅ 任意内核函数 |

**查找 tracepoint**：`cat /sys/kernel/debug/tracing/available_events` 或 `bpftrace -l`
**SEC 格式**：`SEC("tp/<subsys>/<event>")`
**关键**：需要查阅 `/sys/kernel/debug/tracing/events/<subsys>/<event>/format` 确定参数类型

### Lesson 9: Raw Tracepoint
**目标**：比普通 tracepoint 更底层的 hook 方式
**区别**：绕过 tracepoint 的参数格式化层，直接访问原始参数，性能更好

---

## 📊 数据结构

### Lesson 4: 用户态 Map
**目标**：纯用户态操作 BPF Map 的 API
**核心 API**：
- `bpf_map_create()` — 创建 Map（指定类型/key_size/value_size/max_entries）
- `bpf_map_update_elem()` — 创建/更新元素（flags: BPF_ANY/BPF_NOEXIST/BPF_EXIST）
- `bpf_map_lookup_elem()` — 查找元素
- `bpf_map_delete_elem()` — 删除元素
- `bpf_map_get_next_key()` — 遍历 Map

### Lesson 5: 内核态 Map
**目标**：内核态创建 Map 并写入 → 用户态读取遍历
**关键**：内核态用 `SEC(".maps")` 声明 Map，`bpf_map_update_elem` 写入；用户态通过 skeleton 访问
**数据结构**：内核态用 struct 传递事件信息（pid, filename, comm 等），用户态解析显示

### Lesson 7: Ring/Perf Buffer
**目标**：高性能数据传输 — perf event buffer vs ring buffer
**perf buffer**：传统方式，每个 CPU 独立 buffer，需要 `bpf_perf_event_output()`
**ring buffer**：新方式，共享环形缓冲区，`bpf_ringbuf_output()`
**差异**：ring buffer 内存效率更高、API 更简单、支持可变长度数据
**用户态**：`ring_buffer__new()` → `ring_buffer__poll()` → `ring_buffer__free()`

---

## 🌐 网络编程

### Lesson 11: TC Ingress
**目标**：拦截入站网络包（防火墙/流量控制）
**挂载点**：网卡 ingress 方向
**三层解析**：以太网头 → IP 头 → ICMP/TCP/UDP 协议识别
**返回值**：
| 返回值 | 含义 |
|--------|------|
| TC_ACT_OK (0) | 放行 |
| TC_ACT_SHOT (2) | 丢弃 |
| TC_ACT_PIPE (3) | 传递给下一个 filter |
| TC_ACT_STOLEN (4) | 消费掉（不再向上传递） |

**用户态三步**：`if_nametoindex()` → `bpf_tc_hook_create()` → `bpf_tc_attach()`
**示例**：丢弃所有入站 ICMP 包

### Lesson 12: TC Egress
**目标**：拦截出站流量，和 TC Ingress 对称

### Lesson 17 (实际编号 Lesson 14): XDP 过滤
**目标**：在内核最早的数据包处理点（网卡驱动层）拦截
**XDP 返回值**：
| 返回值 | 含义 |
|--------|------|
| XDP_DROP | 丢弃 |
| XDP_PASS | 正常传递到内核栈 |
| XDP_TX | 原路返回 |
| XDP_REDIRECT | 重定向到其他网卡 |
| XDP_ABORTED | 错误丢弃 |

**三种模式**：SKB（通用）< DRV（驱动级）< HW（硬件卸载）
**关键**：必须边界检查 data/data_end，否则 BPF 验证器拒绝加载
**与 TC 区别**：XDP 在网卡驱动层，比 TC 更早，性能更高，适合 DDoS 防护

---

## 🔬 高级主题

### Lesson 6: Go 语言开发
**目标**：用 Go 写 eBPF 用户态程序（cilium/ebpf 库）
**关键**：Go 通过 bpf2go 工具将 .bpf.c 编译为 Go embed 对象，用 `collection.LoadAndAssign()` 加载

### Lesson 10: BTF
**目标**：理解 BPF Type Format — eBPF 程序的类型信息格式
**关键**：BTF 让 eBPF 程序跨内核版本兼容（CO-RE: Compile Once, Run Everywhere）

### Lesson 13: SSL Sniff
⚠️ **404 — 页面不存在，可能尚未完成**

---

## 🐝 实战项目

### Lesson 14: HTTPS 流量监控
（未读取，推测：基于 SSL/TLS 库 hook 解密流量统计）

### Lesson 15: 进程命令监控
**目标**：hook `execve` 系统调用，监控所有进程启动命令

### Lesson 16: Bash 命令监控
**目标**：hook bash 的 `readline()` 函数，捕获所有 bash 命令输入
**原理**：通过 uprobe attach 到 bash 进程的 readline 符号

---

## 🔗 NIDS 相关价值排序

| 优先级 | 课程 | 关联 |
|--------|------|------|
| ⭐⭐⭐ | L11 TC Ingress | 入站流量拦截 — NIDS 的核心拦截点 |
| ⭐⭐⭐ | L17 XDP | 高性能包过滤 — Snort3 可选加速路径 |
| ⭐⭐⭐ | L7 Ring Buffer | NIDS 内核态→用户态事件上报 |
| ⭐⭐ | L8 Tracepoint | 稳定的系统调用追踪 |
| ⭐⭐ | L13 SSL Sniff | 加密流量分析（但目前404） |
| ⭐ | L2 Kprobe | Linux 内核函数 hook |
| ⭐ | L10 BTF | CO-RE 兼容性 |
