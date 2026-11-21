# Pyramid 迁入 Notes

## 布局与维护

`wiki/pyramid/` 保留完整的 Pyramid 知识包布局。Obsidian Vault 为 `wiki/pyramid/wiki/`，原始资料为 `wiki/pyramid/raw/`，辅助工具为 `wiki/pyramid/scripts/`。导入、查询和知识库质量要求仍按 [AGENT.md](pyramid/AGENT.md) 执行。日常技术笔记继续维护在 Notes 原有主题目录。

在仓库根目录运行：

```bash
python3 wiki/pyramid/scripts/lint_okf.py --check
python3 wiki/pyramid/scripts/lint_wiki.py
```

知识包继续使用 Obsidian 双向链接，不直接参与 VitePress 构建。网站通过 `/tools/pyramid` 提供阅读入口，原有页面路径和 `/notes/` 发布地址保持不变。

## 来源和历史

- Notes 基线：`5116b869ad076d9e8591def5e67b99e2ebf73700`。
- Pyramid 来源：`dbbf49e925aca5cdb5c97574d00919af119fba60`，包含远程 main `42ff5fa0e117d81ce53b6e648be08ce0a688072b` 及本地移除旧配置的提交。
- 采用双父合并，保留两条 main 历史。其他分支、Issues、Discussions 和仓库设置不在本次文件合并范围内。
- 来源有 1905 个非依赖 Git 条目；除下述有意变化外，按原路径及内容保留。当前已删除的源码不从旧历史自动恢复。

## 依赖、附件和来源快照

- 排除原仓库跟踪的 2,210 个 `scripts/node_modules/` 文件；保留 package 文件，按需在知识包的 `scripts/` 下运行 `npm ci`。
- 当前来源中的 223 个 LFS 文件（11,999,465 字节）逐一校验 SHA-256 后转成普通 Git 文件，调整包内 `.gitattributes`。当前知识包无需向 Pyramid 的 LFS 服务取文件。
- 历史提交仍有 LFS 指针。原 Pyramid 远端已删除，恢复旧附件需要使用本地备份中的 LFS 对象。
- Notes 原先位于 `resources/docs/` 的 16 份 PDF 已迁入 [ebooks](https://github.com/Sphinxes0o0/ebooks)。知识库来源页里的原路径用于记录采集位置。
- 保留两处上游仓库的固定 gitlink，并在根目录补充 `.gitmodules`。需要原始上游源码时，运行 `git submodule update --init --recursive`。
- Obsidian 配置、插件和主题由个人在本地维护，仓库忽略 `.obsidian/`。知识库的 Markdown 正文与双向链接继续保留。
- 两份 Notes 来源快照共比较 636 个文件：124 个与当前 Notes 字节相同，274 个同路径版本不同，238 个未找到同路径文件或相同内容。全部保留在原始资料层，不覆盖当前 Notes。逐文件结果见 `.github/pyramid-notes-comparison.json`。
- 导入资料中既有的 105 组重复图片/PDF 按完整哈希和精确路径集合记录于 `.github/pyramid-asset-baseline.json`。新增路径或不同内容的重复仍会导致资产审计失败。

## 验证边界

迁移前的知识库检查结果为 950 个 Markdown 页面、6 处失效双向链接、350 个孤立页、280 个 frontmatter 问题；OKF 检查无错误、18 条警告。迁移保留这些既有内容问题，不把它们描述为本次修复。

`.github/pyramid-wiki-baseline.json` 保存迁移前检查结果。`npm run check:pyramid` 是迁移时的逐文件和历史核验命令；日后有意编辑知识库后，不应把与旧来源不同误判为内容丢失。网站构建和审计仍使用 Notes 原有命令。
