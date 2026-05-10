# TODO - Notes 项目优化清单

## 已完成

- [x] os_fundamentals 内容审计与修复
- [x] os_fundamentals sidebar 修复
- [x] CLAUDE.md 内容结构更新
- [x] ccpp 目录审计与修复
- [x] sys 目录审计与修复
- [x] network 目录审计与修复
- [x] kernel 目录审计与修复
- [x] security 目录审计（无问题）
- [x] midware/tools/datastructure/qemu 目录审计与修复
- [x] design_patterns 目录审计与修复
- [x] network_fundamentals 目录审计与修复

## 待处理

### 1. 目录清理与迁移
- [ ] 删除空目录 `courses/`、`wiki/`
- [ ] 迁移 `misc/osi_phy_mac.md` 到 `notes/network/`
- [ ] 从 `.vitepress/config.mjs` 的 `srcExclude` 移除 `misc/**`
- [ ] 添加 `osi_phy_mac.md` 到 network sidebar

### 2. CI/CD
- [x] 创建 CI 代码块审计流程 (`.github/workflows/audit-codeblocks.yml`)
- [x] 创建审计脚本 (`.github/scripts/audit-codeblocks.js`)
- [ ] 提交 CI 文件到 GitHub

### 3. 代码块语言标记
- [ ] 修复 `file_api/file_config.h` → `c` 或 `cpp`（位于 security/nids/snort3_architecture_analysis.md:4103）
- [ ] 考虑将 `conf` → `ini`，`dts` → `typescript` 等作为近似高亮

## 无需处理（已确认）

### Sidebar 配置
- [x] 所有 283 个 sidebar 链接都指向存在的文件 ✓
- [x] 111 个未列入 sidebar 的文件是故意的（deep-dive r1/r2 版本等）

### VitePress 配置
- [x] `manualChunks` 已优化，无需修改
- [x] `ignoreMissing` 正确（这些语言 Shiki 不支持）

### kernel/index.md
- [x] 已修复 16 个链接指向正确的 `linux_kernel/` 子目录

---

*最后更新: 2026-05-10*
