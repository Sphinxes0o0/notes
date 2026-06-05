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

## Review 清单 (2026-06-05)

> 对内容和 VitePress 配置的全面 Review 结果。525 个 md，458 个无 frontmatter (87%)，320/321 sidebar 链接有效。

### P0 - 必修 ✓ (2026-06-05 完成)

#### 1. `readingTime` 插件是空壳 ✓
- [x] 修复 `.vitepress/plugins/readingTime.mjs` —— 重写为在 `transform` 阶段注入 `readingTime: N` 到 frontmatter，并在 `transformPageData` 挂到 `pageData.readingTime`
- [x] 选择注入方式：写入 frontmatter 的 `readingTime` 字段（template / 自定义组件可直接读取）
- [x] 验证：单测覆盖无 fm / 有 fm / 已存在 readingTime / 非 .md / 大文档估算 5 种场景

#### 2. `/sys/` sidebar 重复块 ✓
- [x] 删除 `'/sys/'` sidebar 中重复的 "系统编程" 块
- [x] 修正第二份中 "ELF 文件格式" 缩进异常

#### 3. `/kernel/` sidebar 混入 `/network/` 路径 ✓
- [x] 决策：在 sidebar 中加 `↗` 后缀标识交叉引用
- [x] "网络子系统" → "网络子系统 ↗"，"Netfilter" → "Netfilter ↗"
- [x] 同步更新 `kernel/index.md` 的"子系统列表"表格说明

### P1 - 重要 ✓ (2026-06-05 完成)

#### 4. `security/network-traffic-analysis/` 99 个文件无导航 ✓
- [x] 在 `/security/` sidebar 增加"网络流量分析 (论文集)"分类节点（默认折叠）
- [x] 包含根文件 6 个（README / 文献综述 / 方法对比 / 快速参考 / 时间线 / 研究笔记）
- [x] 6 个论文子分类各展示 2-3 篇代表性论文，标注文档数量

#### 5. ccpp 多处游离文件接入 sidebar ✓
- [x] `ccpp/codewar_notes/{c,cpp}/` 4 个文件（新增 "CodeWars 刷题笔记" 分组）
- [x] `ccpp/concurrency/{future,memory_order,mpmc_ringbuffer,multithreads,yield}/` 5 个子目录（为每个创建 `index.md`，新增 "C++ 并发" 分组）
- [x] `ccpp/cpp/` 8 个独立 md（新增 "C++ 高级主题" 分组）
- [x] `ccpp/test-ingest.md` 1 个文件
- [x] `network/core/` 3 个文件（合并入 "Linux 网络核心" 分组，保留可访问性）
- [x] `network/rfc/` 1 个文件（在 "协议" 分组中）
- [x] `network/osi_phy_mac.md`、`network/lwip-bridge-implementation.md`、`network/plantegg-three-from-one.md`（新增 "其他网络笔记" 分组）
- [x] `network/protocols/arp-table-aging.md`（在 "协议" 分组中）
- [x] `network/performance/tcp-bypass-notes.md`（在 "网络性能" 分组中）

#### 6. frontmatter 覆盖率提升 ✓（脚本就绪，未实际 apply）
- [x] 编写脚本：`.github/scripts/audit-frontmatter.js`（`--audit` / `--apply` 两种模式）
- [x] 推断 title（优先 H1，回退文件名）
- [x] 推断 description（首段截断 200 字符）
- [x] 创建 GH Actions workflow：`.github/workflows/audit-frontmatter.yml`
- [ ] **待用户决定**：是否运行 `node .github/scripts/audit-frontmatter.js --apply` 一次性补全 455 个无 frontmatter 文件

#### 7. `midware/` 独立 sidebar ✓
- [x] 从 `/network/` sidebar 中提取 "中间件" 块
- [x] 在 `themeConfig.sidebar` 中新增独立 `'/midware/'` 键

#### 8. `/network/` 重复分组 ✓
- [x] 合并 "网络核心" (3 项) 和 "Linux 网络核心" (13 项) 为单一 "Linux 网络核心" 分组
- [x] 用注释标明 `/network/core/` 来源的三项

### 额外修复

- [x] `/coding_agent/` sidebar 块前缺逗号的语法错误（预存在，修复后 config.mjs 通过 node --check）

### 验证

- [x] config.mjs 语法检查：✓
- [x] 367 个 sidebar 链接全部有效（除 `/` 是首页特殊处理）
- [x] readingTime 插件 5 个单测场景全通过
- [x] audit-frontmatter.js 脚本 dry-run 报告：455 个无 fm、0 个无 title、55 个无 description

### P2 - 建议

#### 9. dead link 审计脚本
- [ ] 编写 `.github/scripts/audit-deaddlinks.js`
- [ ] 检查站内 markdown 中的相对链接
- [ ] 检查 sidebar 配置中的所有 link
- [ ] 可选：检查站外链接（HEAD 请求）
- [ ] 新增 `.github/workflows/audit-deaddlinks.yml`

#### 10. 清理 `ignoreMissing` 列表
- [ ] 删除 `file_api/file_config.h`（不是语言标识符）
- [ ] 验证 `snort`、`haproxy`、`conf` 是否需要 ignore
- [ ] 改用 `text` 兜底更安全

#### 11. sitemap 配置去重
- [ ] 删除 `themeConfig` 外的 `sitemap:` 顶层配置（不是 VitePress 原生字段）
- [ ] 统一 `lastmodDateOnly` 值（plugin: true, sitemap: false 矛盾）

#### 12. 格式清理
- [ ] 修复 `/tools/` sidebar 尾部多余空格（行 470-471）
- [ ] 修正 `/coding_agent/` sidebar 缩进（行 451 顶格应为 6 空格）
- [ ] 修复 `audit-codeblocks.js` 中过时的 `CONTENT_DIRS`（包含不存在的 os/net/netfilter/mm/io_uring/ipc/locking/lib/crypto/block/sched/rcu/time/vfs/sound/virt/openbmc）

#### 13. interview credits 补全
- [ ] 在 `interview/index.md` 或 `interview/credits.md` 顶部加 License 声明
- [ ] 内容：`License: CC BY-NC 4.0 - 原始作者 jwasham`
- [ ] 与现有 jwasham 引用合并

### P3 - 锦上添花

#### 14. 文件命名风格统一
- [ ] 决策：全小写 vs 小写下划线 vs PascalCase
- [ ] 当前混用：`security/masscan/ARCHITECTURE`（全大写）、`kernel/mm/mm_allocator`（下划线）、`qemu/01_qom`（数字前缀 + 下划线）
- [ ] 建议：统一为全小写 + 下划线（URL 友好）

#### 15. `os_fundamentals/` 缺失章节
- [ ] 确认 37、38 章是否真的不存在还是有别的原因（直接从 36 跳到 39）
- [ ] 如确实缺失，sidebar 中加 TODO 注释

#### 16. 可疑 AI 生成内容标注
- [ ] `ccpp/hermes_memory_design.md`、`ccpp/hermes_memory_research_2026h1.md` 风格与手写笔记不同
- [ ] 决策：保留并标注 / 移除 / 归到独立子目录

#### 17. 长中文 URL 优化
- [ ] `os_fundamentals/02_程序的执行_相比_32_位_64_位的优势是什么(上)` 等超长路径
- [ ] 决策：保持现状（保留原貌） / 简化为短 slug + 别名
- [ ] 涉及：os_fundamentals (47)、datastructure (26)、network_fundamentals (27)、design_patterns (29)

#### 18. CLAUDE.md 更新
- [ ] 同步最新目录结构（加入 `coding_agent/`、`security/network-traffic-analysis/`）
- [ ] 更新 srcExclude 说明（courses/、wiki/、android/）
- [ ] 移除已删除的 misc 引用

---

*Review 时间: 2026-06-05*
*最后更新: 2026-06-05*
