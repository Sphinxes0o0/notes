# TODO - Notes 项目优化清单

## 已完成 ✓

### 审计与修复 (2026-05-10)
- [x] 所有目录内容审计（ccpp, sys, network, kernel, security, midware, tools, datastructure, design_patterns, network_fundamentals, os_fundamentals）
- [x] 修复 152+ 个代码块 bleeding 问题
- [x] 修复 6 个失效外部链接

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

## 待规划/潜在优化

### 1. 内容增强
- [ ] 添加缺失的 index.md 文件描述（如 security/linux_kernel/index.md）
- [ ] 统一各目录的 frontmatter 格式（author, date, tags 等）
- [ ] 检查是否有重复内容可以合并

### 2. SEO 优化
- [ ] 检查 meta description 是否完整
- [ ] 添加 Open Graph 图片
- [ ] 验证 sitemap 生成正确

### 3. 性能优化
- [ ] 图片压缩和优化
- [ ] 考虑使用 CDN 加速外部资源
- [ ] 评估 chunk size 进一步拆分可能

### 4. 开发者体验
- [ ] 添加 pre-commit hooks（lint, format）
- [ ] 添加贡献指南 CONTRIBUTING.md
- [ ] 考虑添加自动图片压缩 CI

### 5. 内容扩展
- [ ] 添加缺失的设计模式章节（如 观察者、装饰器等已存在于 content 但需确认 sidebar）
- [ ] 统一复习题格式

---

*最后更新: 2026-05-11*
