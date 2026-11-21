# Sphinx's Notes

技术学习笔记与实践示例，涵盖 C/C++、Linux 内核、网络协议、系统编程、安全及 AI Agent。

在线阅读：[GitHub Pages](https://sphinxes0o0.github.io/notes/)。各主题的 `index.md` 提供阅读入口。

## 技术知识库

Pyramid 的概念页、来源摘要和综合分析统一在本仓库维护。浏览[知识库首页](https://github.com/Sphinxes0o0/notes/blob/main/wiki/pyramid/wiki/home.md)，或在 Obsidian 中打开 `wiki/pyramid/wiki/`。网站的[知识库入口](https://sphinxes0o0.github.io/notes/tools/pyramid)提供在线阅读导航；[迁移记录](https://github.com/Sphinxes0o0/notes/blob/main/wiki/MIGRATION.md)说明历史、来源快照和附件的处理方式。

## 本地开发

使用 Node.js 22（最低 22.12）和 npm。本地与 GitHub Actions 均通过 `.nvmrc` 指定 Node 主版本。

```bash
nvm install
nvm use
npm ci
npm run docs:dev
```

未安装 nvm 时，可自行安装符合 `package.json` 中 `engines` 要求的 Node.js。

```bash
npm run docs:build    # 构建到 .vitepress/dist/，Node 堆内存上限为 8 GB
npm run docs:preview  # 预览已构建的站点
```

## 项目结构

- `ccpp/`、`kernel/`、`sys/`、`qemu/`：语言、内核与系统实践。
- `network/`、`midware/`、`security/`：网络协议、中间件与安全。
- `coding_agent/`、`a2a/`、`research/`：AI Agent、A2A 协议与专题研究。
- `datastructure/`、`design_patterns/`、`network_fundamentals/`、`os_fundamentals/`、`interview/`：基础课程与面试笔记。
- `tools/`、`android/`：工具与 Android 笔记；`android/` 当前不参与站点构建。
- `.vitepress/config.mjs`：站点配置；`.vitepress/sidebar/`：按主题拆分的侧边栏。
- `public/`：直接发布的静态文件；`resources/` 和主题内的图片目录：文档附件。PDF 原件集中存放在 [ebooks](https://github.com/Sphinxes0o0/ebooks)。
- `scripts/`、`.github/scripts/`：内容及链接审计；`.github/workflows/`：检查与发布流程。

## 内容维护与检查

新页面沿用相邻文档的命名和语言风格，添加 YAML `title` 与清晰的一级标题。按需要更新主题 `index.md`、对应侧边栏及跨主题引用。代码块注明语言，图片与附件使用可解析的链接。

```bash
npm run check:links        # 检查正文中的内部链接，需要 Python 3
npm run check:navigation   # 检查顶部导航、侧边栏及其入口
npm run check:search       # 构建后检查搜索索引和实际查询
npm run check:frontmatter  # 只读检查已跟踪文档的 title/description，缺失则失败
npm run check:codeblocks   # 检查代码围栏和语言标记
npm run audit:content      # 已跟踪内容审计；未复核候选会失败，需要 Python 3
npm run check:assets       # 检查已跟踪图片/PDF 的字节级重复
python3 scripts/link_check.py --external  # 可选：探测外部链接，需要网络
```

审计脚本的扫描范围不完全相同，结果需结合原文判断。短文、TODO 和超长页面属于人工复核候选，不应自动删除或拆分。`.github/content-review.json` 保存逐项复核结论与文件指纹，正文变化后需重新复核。frontmatter 和内容检查用于 PR 门禁；`--apply` 会写入文件，使用前先检查改动范围。

提交前的 Husky hook 执行代码块、导航和正文内部链接检查，需要 Python 3。完整构建在 PR 检查中执行，本地提交前可按需运行 `npm run docs:build`。搜索渲染回归测试通过 `node --test .github/scripts/test-search.mjs` 运行。链接检查器的回归测试通过 `python3 -m unittest discover -s scripts -p 'test_*.py'` 运行；可执行示例仍按所在目录的工具链验证。构建配置启用了 `ignoreDeadLinks`，因此构建成功后仍需检查链接，并在本地预览修改过的页面。

## 持续集成与发布

推送及 PR 会触发内部链接、frontmatter 和代码块检查；外部链接另有定期检查。推送到 `main` 或手动触发 `deploy.yml` 会安装锁定依赖、构建站点并发布至 GitHub Pages。`docs-build.yml` 在 PR 和手动触发时验证导航、正文内部链接、链接与搜索回归测试及全站构建。

提交信息沿用 `docs(kernel): 描述`、`refactor(structure): 描述` 或 `chore: 描述`。PR 说明改动主题和验证结果；修改页面布局或导航时附截图。

本地搜索保留全文与代码索引，按需下载 gzip 数据并在浏览器解压，避免解析大段 JavaScript 字符串；不支持解压或请求失败时回退至 JSON。索引通过异步分批恢复，减少打开搜索时对输入的阻塞。VitePress 升级改变搜索组件时，兼容检查会要求复核适配器。

发布后地址检查：启动预览后运行 `python3 scripts/check_built_site.py`，检查页面、静态资源和实际发布的内部链接。构建会将并发与 A2A 示例源码导出至原相对路径，避免源码在仓库存在、下载链接却返回 404。
