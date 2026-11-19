# TTY、Shell 与 Console 详解

## 一、Tty 的前世今生

### 1.1 起源：电传打字机时代

**TeleTYpewriter (TTY)** 诞生于 19 世纪末，最初用于电报传输。1960 年代被引入计算机领域作为人机交互界面。

```
┌─────────────────────────────────────┐
│         电传打字机 (TTY)              │
│                                     │
│   键盘 ──────────────────────► 主机  │
│   纸带 ◄────────────────────── 输出  │
└─────────────────────────────────────┘
```

用户通过键盘向主机发送命令，主机的输出被打印在纸带上。整个过程是**串行的、同步的、一对一**的——一台打字机对应一台计算机。

### 1.2 Unix 中的 TTY 设备

在 Unix 哲学中，**一切皆文件**。每个终端设备都对应一个设备文件：

| 设备文件 | 说明 |
|---------|------|
| `/dev/tty` | 当前进程的控制终端（快捷方式） |
| `/dev/tty0` | 第一个虚拟终端（文本模式） |
| `/dev/tty1` | 第二个虚拟终端 |
| `/dev/console` | 系统主控制台 |
| `/dev/ttys000` | 第一个伪终端（slave side） |
| `/dev/ttys002` | 第三个伪终端 |

### 1.3 伪终端 (PTY) 的诞生

随着时代发展，出现了"终端模拟器"——软件模拟老式终端的行为。这些模拟器需要在内核中创建**一对**相互连接的虚拟设备：

```
┌─────────────────────────────────────────────────────────────┐
│                        Kernel (内核)                         │
│                                                              │
│   ┌─────────────┐           ┌─────────────┐                 │
│   │  /dev/ptmx  │◄─────────►│  /dev/pts/X │                 │
│   │  (master)   │    管道    │  (slave)    │                 │
│   └─────────────┘           └─────────────┘                 │
│          ▲                           ▲                        │
└──────────┼───────────────────────────┼──────────────────────┘
           │                           │
      终端模拟器                    Shell/进程
   (Terminal.app,                  (zsh, bash)
    iTerm2, SSH)
```

- **Master (ptmx)** — 由终端模拟器持有，模拟器向 master 写入用户输入，内核将数据转发给 slave
- **Slave (pts/X)** — 由 Shell 持有，Shell 以为自己在一个真实的硬件终端上工作
- **ptmx** — "pseudo-terminal multiplexor"，所有伪终端的 master 端

### 1.4 编号为什么不是连续的

```
ttys000 → 系统进程（sshd、launchd 子进程等）
ttys001 → SSH 会话 #1 或其他系统会话
ttys002 → 你打开的第一个 Terminal 窗口
ttys003 → 第二个 Terminal 窗口
ttys004 → SSH 会话 #2
...
```

内核的 pty 分配算法是：**找到当前最大的已分配编号，加 1**。所以当系统进程占用了 000、001 后，你的第一窗口就会拿到 002。

### 1.5 常用命令

```bash
# 列出所有伪终端
ls -la /dev/ttys*

# 查看哪些 ttys 正被使用
who

# 查看特定 ttys 被谁占用
lsof | grep ttys000
```

---

## 二、Shell 详解

### 2.1 Shell 是什么

Shell 是运行在用户态的命令行解释器，是用户与操作系统内核之间的桥梁：

```
┌──────────────────────────────────────────┐
│                Shell                       │
│                                           │
│  1. 命令行解释   whoami, ls, cd ...       │
│  2. 变量管理     PATH, HOME, USER         │
│  3. 流程控制     if, for, while           │
│  4. 输入/输出重定向   >, <, |             │
│  5. 管道连接     cmd1 | cmd2              │
│  6. 命令替换     $(cmd), `cmd`            │
│  7. 环境控制     export, env              │
│  8. 作业控制     jobs, fg, bg, Ctrl+Z     │
└──────────────────────────────────────────┘
```

### 2.2 常见的 Shell 类型

| Shell | 由来 | 特点 |
|-------|------|------|
| `sh` | Bourne Shell (1977) | 最原始，POSIX 标准参考实现 |
| `bash` | GNU Bourne Again Shell | Linux 默认，功能丰富 |
| `zsh` | Z Shell | macOS 默认，插件生态强大 |
| `fish` | Friendly Interactive Shell | 开箱即用的用户体验 |

macOS Catalina (10.15) 之前默认使用 `bash`，之后改为 `zsh`。

### 2.3 Shell 会话的生命周期

当你打开一个终端窗口时：

```
1. Terminal.app 启动
         ↓
2. 请求内核分配一个新的 ptmx/pts 对
         ↓
3. fork() → 创建子进程
         ↓
4. 子进程执行 execve("/bin/zsh")
         ↓
5. Shell 初始化：加载配置文件 (~/.zshrc, /etc/zshrc)
         ↓
6. 显示提示符 (prompt)，等待输入
         ↓
7. 用户输入命令 → Shell 解析 → fork + exec 执行
         ↓
8. 命令结束 → 返回提示符
         ↓
9. 用户退出 (exit / Ctrl+D) → Shell 进程结束
         ↓
10. 终端模拟器检测到 Shell 退出，关闭窗口
```

### 2.4 交互式 vs 非交互式、登录 vs 非登录

```bash
# 交互式：用户手动输入命令
$ zsh
sphinx@macbook ~ % echo "hello"

# 非交互式：执行脚本
$ zsh script.sh

# 登录 shell：ssh 登录、开机后第一个 shell
# 读取 /etc/profile, ~/.profile, ~/.zprofile

# 非登录 shell：打开新终端窗口
# 读取 ~/.zshrc
```

---

## 三、Console 详解

### 3.1 Console 的原始含义

**Console** 一词来自拉丁语 `consolāre`（安慰、抚慰）。在机械时代，console 是控制台——大型设备（如火车、轮船、收音机）中供操作员坐着控制机器的台子。

在计算机领域，**Console = 直接连接在主机上的主控制终端**：

```
┌────────────────────────────────────────┐
│              服务器主机                  │
│                                        │
│   ┌──────────────────────────┐         │
│   │       系统主机             │         │
│   └──────────┬───────────────┘         │
│              │                          │
│   [键盘+显示器] ← Console (物理连接)     │
│                                        │
└────────────────────────────────────────┘
```

这是你与机器之间**最近、最直接**的连接——没有网络、没有模拟器，是机器"亲生的"终端。

### 3.2 macOS / Linux 中的 Console

| 系统 | Console 含义 |
|------|-------------|
| **macOS** | 桌面登录界面 (Console.app 日志查看器) |
| **Linux** | 物理键盘+显示器，或 Virtual Console (tty1~tty6) |

#### macOS 的 Console

```
┌─────────────────────────────────────────────────┐
│                 macOS 系统                       │
│                                                  │
│  ┌─────────────┐                                 │
│  │  Console    │  ← 日志查看工具                   │
│  │  (日志查看器) │    /Applications/Utilities/      │
│  └─────────────┘                                 │
│                                                  │
│  /dev/console   ← 内核消息输出设备                 │
│                                                  │
│  桌面登录界面 ← macOS 的主控制台                   │
└─────────────────────────────────────────────────┘
```

#### Linux Virtual Console

Linux 系统提供多个**虚拟控制台**，通过 `Ctrl+Alt+F1` ~ `F6` 切换：

| 快捷键 | 对应 | 用途 |
|--------|------|------|
| `Ctrl+Alt+F1` | tty1 | 第一个虚拟控制台 |
| `Ctrl+Alt+F2` | tty2 | 第二个虚拟控制台 |
| ... | ... | ... |
| `Ctrl+Alt+F7` | tty7 | X11 图形会话 |

### 3.3 TTY vs Console 关键区别

| 维度 | TTY (伪终端) | Console |
|------|-------------|---------|
| **连接方式** | 软件模拟（终端模拟器、SSH） | 物理直连（本地键盘+显示器） |
| **访问权限** | 普通用户可任意创建 | 系统管理员或内核专用 |
| **数量** | 可创建多个（ptmx 池） | 通常只有 1 个 |
| **用途** | 用户交互式 shell、SSH | 系统维护、紧急修复、kernel 输出 |
| **macOS** | Terminal.app、SSH 会话 | 本地 GUI 桌面登录 |

---

## 四、整体架构关系图

```
                        用户视角
                          │
        ┌─────────────────┼─────────────────┐
        │                  │                  │
   本地桌面              远程                 物理
   (Terminal.app)    (SSH / 远程桌面)        (Console)
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────────────────────────────────────┐
   │           /dev/ptmx (Master)              │
   │      内核伪终端多路复用器                  │
   └────────┬──────────────┬──────────────────┘
            │              │
     ┌──────┴──────┐  ┌────┴────┐
     │ pts/0       │  │ pts/1   │  ...
     │ (slave)     │  │ (slave) │
     └──────┬──────┘  └────┬────┘
            │              │
            ▼              ▼
        zsh/bash        sshd
       (Shell进程)    (远程Shell)
            │              │
            └──────┬───────┘
                   ▼
            命令执行 + 输出
```

---

## 五、相关命令速查

### 查看终端信息

```bash
# 查看当前终端设备
tty

# 查看所有已登录的终端会话
who
w

# 查看当前 shell 类型
echo $SHELL
ps -p $$ -o comm=
```

### 查看进程 TTY

```bash
# 查看进程的 TTY
ps aux | grep zsh

# lsof 查看 ttys 占用
lsof | grep ttys002
```

### 伪终端设备

```bash
# 查看伪终端设备
ls -la /dev/pts/
ls -la /dev/ttys*
```

### Linux Virtual Console

```bash
# 切换虚拟控制台 (Linux)
Ctrl+Alt+F1   # 切换到 tty1
```

### macOS Console

```bash
# 查看控制台日志
log show --predicate 'process == "kernel"' --last 5m

# 或使用 Console.app
open -a Console
```

---

## 六、参考资料

- [Wikipedia: TTY](https://en.wikipedia.org/wiki/Teleprinter)
- [Linux Kernel Documentation: ptmx](https://www.kernel.org/doc/html/latest/tty driver/pty.html)
- [GNU Bash Manual](https://www.gnu.org/software/bash/manual/)
- [Apple Developer: Kernel I/O Kit](https://developer.apple.com/)
