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
- [x] `.github/scripts/audit-codeblocks.js` - 审计脚本

---

## 待处理

### 1. CI 验证
- [ ] 验证 GitHub Actions workflow 是否正常工作
- [ ] 首次 CI 运行后根据结果修复问题

### 2. 内容质量
- [ ] 外部链接检查 - 验证外部 URL 是否有效
- [ ] 考虑将 `file_api/file_config.h` 改为 `c` 或 `cpp`

### 3. Sidebar 优化（可选）
- [ ] 添加 tools 子目录内容到 sidebar
- [ ] 统一 collapsed 行为
- [ ] 考虑为 os/ 子目录添加更多内容

### 4. 其他
- [ ] 添加 .gitignore（如果需要）
- [ ] 考虑添加依赖版本锁定（package-lock.json 或 yarn.lock）

---

## 无需处理（已确认）

- 图片链接：所有现有图片引用有效 ✓
- Sidebar 链接：全部 283 个链接都指向存在的文件 ✓
- VitePress 配置：manualChunks 和 ignoreMissing 已优化 ✓
- TODO 标记：用户选择保留 ✓

---

*最后更新: 2026-05-10*
