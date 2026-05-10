# TODO - Notes 项目优化清单

## 已完成 ✓

### 审计与修复
- [x] os_fundamentals 内容审计与修复
- [x] ccpp 目录审计与修复
- [x] sys 目录审计与修复
- [x] network 目录审计与修复
- [x] kernel 目录审计与修复
- [x] security 目录审计
- [x] midware/tools/datastructure/qemu 目录审计与修复
- [x] design_patterns 目录审计与修复
- [x] network_fundamentals 目录审计与修复

### 配置与结构
- [x] CLAUDE.md 内容结构更新
- [x] os_fundamentals sidebar 修复
- [x] kernel/index.md 修复（16 个链接）
- [x] index.md frontmatter 修复
- [x] Sidebar 扩展（security/linux_kernel + network/linux_kernel）
- [x] srcExclude 更新（移除 misc）

### 目录清理
- [x] 删除空目录 courses/, wiki/
- [x] 迁移 misc/osi_phy_mac.md 到 network/

### CI/CD
- [x] `.github/workflows/audit-codeblocks.yml` - 代码块审计流程
- [x] `.github/scripts/audit-codeblocks.js` - 审计脚本（已优化）

### Sidebar 优化
- [x] tools 目录加入 sidebar（tcpdump）
- [x] 统一 collapsed 行为（>5 项的子菜单折叠）

---

## 待处理

### 1. 内容修复 (152 个问题)
- [ ] datastructure 目录：约 80+ 行需要修复
- [ ] os_fundamentals 目录：约 50+ 行需要修复
- [ ] network_fundamentals 目录：约 10+ 行需要修复
- [ ] 其他目录：零星问题

**问题类型**：课程讲解文本混入代码块（CONTENT_BLEEDING）
**建议**：分批修复，每次 1-2 个文件

### 2. 外部链接修复 (6 个失效)
| 文件 | URL |
|------|-----|
| network_fundamentals/模块四思考题解答.md:9 | bind9.readthedocs.io - 404 |
| security/nids/snort3_architecture_analysis.md:15935 | snort.org - 404 |
| security/nids/snort3_architecture_analysis.md:15948 | ettercap.github.io - 连接错误 |
| openbmc/linux_kernel/kvm_virtualmedia.md:1045 | kernel.org - 404 |
| openbmc/linux_kernel/kvm_virtualmedia.md:1046 | kernel.org - 404 |
| network/linux_netfilter/conntrack.md:562 | kernel.org - 404 |

---

*最后更新: 2026-05-10*
