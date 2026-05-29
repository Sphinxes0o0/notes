---
type: entity
tags: [linux, ebpf, ecosystem, libraries, tooling, bcc, libbpf, go, rust, python]
created: 2026-05-22
sources: [pdf-ebpf-books, pdf-ebpf-papers]
---

# eBPF Ecosystem

## 定义

eBPF 生态包含用于编写、加载、管理 eBPF 程序的用户态库，以及配套的调试/观测工具。核心生态围绕 BCC、libbpf、cilium/ebpf 三大开源项目展开，支持 Go/Rust/Python/C 等多语言开发。

## 核心开发框架

### BCC (BPF Compiler Collection)

- **定位**：面向追踪的工具箱，最流行、最友好的 eBPF 库
- **特点**：Python/Lua 前端，运行时调用 LLVM 动态编译 BPF C 源码
- **优点**：容易上手，大量示例和工具，活跃社区
- **缺点**：需要部署 LLVM/Clang 环境，运行时编译消耗资源，无法在目标机器缺少内核头文件时工作
- **GitHub**：[iovisor/bcc](https://github.com/iovisor/bcc)

**支持程序类型**：Tracing (kprobe/kretprobe/tracepoint/perf)、XDP、TC、Socket Filter、LSM

### libbpf (官方 BPF 库)

- **定位**：Linux 内核官方维护的 C 库（位于内核源码 `tools/lib/bpf`）
- **特点**：专注可复用 BPF 程序（CO-RE），无 I/O 和编译器抽象
- **优点**：内核官方支持，最底层接口，无外部依赖，支持 CO-RE 一次编译到处运行
- **缺点**：低层次接口，需要较多样板代码
- **GitHub**：[libbpf/libbpf](https://github.com/libbpf/libbpf)

**支持程序类型**：Tracing、XDP、LSM（显式 attach 支持）

**libbpf-bootstrap**：基于 libbpf 的 starter 项目，提供多种语言绑定的模板，地址 [libbpf/libbpf-bootstrap](https://github.com/libbpf/libbpf-bootstrap)

### cilium/ebpf (Pure Go)

- **定位**：纯 Go 实现的 eBPF 库（由 Cilium 团队维护）
- **特点**：无 CGO 依赖，通过 `bpf2go` 嵌入编译后的 BPF 程序
- **优点**：Go 生态友好，编译简单，支持 CO-RE
- **缺点**：设计较独特（Collections/Specs API），部分网络程序类型需要自己实现 attach
- **GitHub**：[cilium/ebpf](https://github.com/cilium/ebpf)

**核心 API**：`asm` 包（低级指令）、`bpf2go`（嵌入编译产物）、`Collections`（程序集合管理）

### 其他 Go 库

| 库 | 特点 |
|----|------|
| **iovisor/gobpf** | BCC 官方 Go wrapper，支持 tracing 和 XDP |
| **dropbox/goebpf** | 纯 Go，专注网络，干净简洁 |
| **aquasecurity/libbpfgo** | libbpf Go wrapper，聚焦 tracing 和安全用例 |

### Python 库

| 库 | 特点 |
|----|------|
| **bcc** | BCC 官方 Python wrapper，最广泛使用 |
| **pyebpf** | BCC wrapper + extras，仅支持 kprobe tracing |

### Rust 库

| 库 | 特点 |
|----|------|
| **libbpf-rs** | libbpf Rust wrapper，safe API |
| **aya** | 纯 Rust，功能完整（async 支持） |
| **redbpf** | Rust BPF 框架 |

## 工具生态

### bpftool

内核提供的 BPF introspection 和调试工具：

```bash
# 列出所有 BPF 程序
bpftool prog show

# 列出所有 Maps
bpftool map show

# 查看程序详情（JSON 输出）
bpftool --json --pretty prog show

# 查看 Map 内容
bpftool map dump id <id>

# 查看 JIT 编译后的汇编
bpftool prog dump jited

# 生成 BPF skeleton
bpftool gen skeleton <bpf.o> > <skel.h>

# dump BTF 信息
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
```

### iproute2

加载 BPF 网络程序到内核：
- `ip link set dev eth0 xdp obj prog.o` — 加载 XDP 程序
- `tc qdisc add dev eth0 clsact` — 启用 clsact qdisc
- `tc filter add dev eth0 ingress bpf da obj prog.o` — 加载 TC 程序

### bpftrace

DTrace for Linux，单行命令和短工具的高级跟踪语言：
```bash
# 跟踪 sys_open 调用
bpftrace -e 'kprobe:do_sys_open { printf("%s: %s\n", comm, str(arg1)) }'

# 内置工具示例：tcpconnect, opensnoop, biolatency
```

底层调用 BCC (`libbcc.so`)。

### perf

Linux 内核性能分析工具，也可加载 BPF 追踪程序到内核：
```bash
perf list
perf stat -e cycles:u,instructions:u ./program
```

## CO-RE 工作流

```
1. Clang 编译 C 代码 → BPF object (ELF)
   $ clang -O2 -target bpf -c prog.c -o prog.o

2. bpftool 生成 skeleton（包含类型安全的程序加载辅助）
   $ bpftool gen skeleton prog.o > prog.skel.h

3. 用户态 Go/C 程序 include skeleton.h
   - 打开/加载/attach 程序
   - 创建/操作 Maps
   - 与 BPF 程序交互

4. libbpf/cilium-ebpf 根据目标内核 BTF 调整字节码（CO-RE 重定位）
```

## 内核配置要求

```bash
CONFIG_BPF=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_CGROUP_BPF=y
CONFIG_NET_SCH_INGRESS=m
CONFIG_NET_CLS_BPF=m
CONFIG_NET_CLS_ACT=y
CONFIG_BPF_EVENTS=y
CONFIG_DEBUG_INFO_BTF=y  # CO-RE 需要
CONFIG_TEST_BPF=m        # BPF 自我测试
```

## sysctl 调优参数

| 参数 | 说明 |
|------|------|
| `net.core.bpf_jit_enable` | 0=解释器，1=JIT，2=JIT+调试日志 |
| `net.core.bpf_jit_harden` | 0=关闭，1=非特权用户，2=全部用户 |
| `net.core.bpf_jit_kallsyms` | 导出 JIT 符号到 /proc/kallsyms |
| `kernel.unprivileged_bpf_disabled` | 禁止非特权用户调用 bpf syscall |

## Coolbpf（中文生态）

浪潮/阿里云等国内厂商贡献的 Coolbpf 项目：
- **CO-RE + BCC 混合**：低资源占用、高可移植性 + 动态编译特性
- **多语言支持**：Python/Rust/Go/C/lwcb
- **远程编译服务**：用户只需 `pip install coolbpf`，自动远程编译 bpf.c
- **低版本内核支持**：提供 eBPF 驱动兼容老内核

## 相关概念

- [[entities/linux/ebpf/ebpf-overview]] — eBPF 核心架构
- [[entities/linux/ebpf/ebpf-xdp]] — XDP 网络处理
- [[entities/linux/kernel/index]] — Linux 内核子系统
- [[tools-index]] — 工具索引

## 来源详情

- [[sources/pdf-ebpf-books]] — 《eBPF基础》第2.2节开发框架（BCC/bpftrace/libbpf/libbpf-bootstrap/cilium-ebpf/Coolbpf）
- [[sources/pdf-ebpf-papers]] — eBPF Library Ecosystem Overview in Go Rust Python C and More (Kyle Quest)
