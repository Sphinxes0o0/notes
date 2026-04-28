# Linux Security 子系统文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [lsm_framework.md](lsm_framework.md) | LSM 框架: 钩子机制, 核心结构, 初始化 | security/security.c |
| [selinux_detailed.md](selinux_detailed.md) | SELinux 详细: TE/RBAC/MLS, AVC, 策略 | security/selinux/ |
| [apparmor_detailed.md](apparmor_detailed.md) | AppArmor 详细: 路径 MAC, 策略, 域转换 | security/apparmor/ |
| [landlock_detailed.md](landlock_detailed.md) | Landlock 详细: 规则集, FS/网络控制, 层级 | security/landlock/ |
| [lockdown_loadpin.md](lockdown_loadpin.md) | Lockdown/LoadPin: 内核锁定, 模块固定, Capabilities | security/lockdown/, loadpin/ |
| [bpf_security.md](bpf_security.md) | BPF 安全: 验证器, 沙箱, JIT, 程序类型 | kernel/bpf/ |
| [integrity_keys.md](integrity_keys.md) | 完整性+密钥: IMA/EVM, 密钥管理, 密钥环 | security/integrity/, keys/ |
| [security_deep_dive_r1.md](security_deep_dive_r1.md) | 深度分析 R1: LSM框架, SELinux, AppArmor, Landlock | security/ |
| [security_deep_dive_r2.md](security_deep_dive_r2.md) | 深度分析 R2: SELinux AVC, 策略加载, domain转移, AppArmor 策略抽象, Landlock 规则遍历 | security/ |

---

## 1. LSM 框架 (lsm_framework.md)

### 关键内容
- LSM 设计目标与架构
- struct security_hook_list: 钩子链表
- call_int_hook / call_void_hook 宏
- 钩子类型: inode, file, task, bprm

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| security_add_hooks | security/security.c |
| call_int_hook | security/lsm_hooks.h |

---

## 2. SELinux (selinux_detailed.md)

### 关键内容
- TE (Type Enforcement) 类型强制
- MLS (Multi-Level Security)
- RBAC (Role-Based Access Control)
- struct context: 安全上下文
- AVC (Access Vector Cache)

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| security_compute_sid | security/selinux/ss/services.c |
| avc_has_perm | security/selinux/avc.c |
| inode_has_perm | security/selinux/hooks.c |

---

## 3. AppArmor (apparmor_detailed.md)

### 关键内容
- 基于路径的 MAC
- aa_policydb: 策略匹配引擎
- aa_profile: 配置文件结构
- profile_transition(): 域转换

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| aa_file_permission | security/apparmor/file.c |
| aa_bprm_set_creds | security/apparmor/domain.c |

---

## 4. Landlock (landlock_detailed.md)

### 关键内容
- 用户空间安全模块
- landlock_ruleset: 规则集
- FS/网络访问控制
- 层级继承 (最多 16 层)

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| landlock_create_ruleset | security/landlock/ruleset.c |
| landlock_insert_rule | security/landlock/ruleset.c |

---

## 5. Lockdown / LoadPin (lockdown_loadpin.md)

### 关键内容
- LOCKDOWN_INTEGRITY / LOCKDOWN_CONFIDENTIALITY
- LoadPin: 模块/固件加载固定
- Capabilities: 5 种能力集

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| lockdown_is_locked_down | security/lockdown/lockdown.c |
| cap_capable | security/commoncap.c |

---

## 6. BPF 安全 (bpf_security.md)

### 关键内容
- BPF 验证器: check_cfg, do_check
- 沙箱: 指令限制, 内存边界
- JIT 编译安全措施
- 34 种程序类型

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| bpf_prog_load | kernel/bpf/syscall.c |
| check_cfg | kernel/bpf/verifier.c |

---

## 7. 完整性与密钥 (integrity_keys.md)

### 关键内容
- IMA: 文件完整性测量
- EVM: 扩展属性验证
- 密钥管理: key, key_type
- 密钥环: keyring_search

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| ima_file_hash | security/integrity/ima/ima_main.c |
| key_alloc | security/keys/key.c |

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │         用户空间                        │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │   BPF Program       │               │   SELinux Policy   │
        │   (加载验证)        │               │   (TE/RBAC/MLS)   │
        └──────────┬──────────┘               └──────────┬──────────┘
                   │                                     │
                   ▼                                     ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │   BPF Verifier       │               │   AVC (Access       │
        │   (安全验证)        │               │   Vector Cache)     │
        └──────────┬──────────┘               └──────────┬──────────┘
                   │                                     │
                   └───────────────┬─────────────────────┘
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │         LSM Hooks                      │
                    │   inode_permission / file_permission     │
                    │   bprm_check_security / cap_capable    │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │   Landlock           │               │   AppArmor           │
        │   (规则集限制)      │               │   (路径控制)        │
        └─────────────────────┘               └─────────────────────┘
```

---

## 源码位置索引

| 组件 | 路径 |
|------|------|
| LSM 核心 | security/security.c |
| SELinux | security/selinux/ |
| AppArmor | security/apparmor/ |
| Landlock | security/landlock/ |
| Lockdown | security/lockdown/ |
| LoadPin | security/loadpin/ |
| Capabilities | security/commoncap.c |
| BPF 验证器 | kernel/bpf/verifier.c |
| BPF syscall | kernel/bpf/syscall.c |
| IMA | security/integrity/ima/ |
| EVM | security/integrity/evm/ |
| 密钥管理 | security/keys/ |
