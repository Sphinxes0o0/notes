# Sphinx's Notes

技术学习笔记与实践示例，涵盖 C/C++、Linux 内核、网络协议、系统编程、安全及 AI Agent。

在线阅读：[GitHub Pages](https://sphinxes0o0.github.io/notes/)。各主题的 `index.md` 提供阅读入口。

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
- `public/`：直接发布的静态文件；`resources/` 和主题内的图片目录：文档附件。
- `scripts/`、`.github/scripts/`：内容及链接审计；`.github/workflows/`：检查与发布流程。

## 内容维护与检查

新页面沿用相邻文档的命名和语言风格，添加 YAML `title` 与清晰的一级标题。按需要更新主题 `index.md`、对应侧边栏及跨主题引用。代码块注明语言，图片与附件使用可解析的链接。

```bash
npm run check:links        # 检查正文中的内部链接，需要 Python 3
npm run check:navigation   # 检查顶部导航、侧边栏及其入口
npm run check:search       # 构建后检查搜索索引和实际查询
npm run check:frontmatter  # 只读报告 frontmatter、title、description 缺失情况
npm run check:codeblocks   # 检查代码围栏和语言标记
npm run audit:content      # 内容复核候选报告，需要 Python 3
python3 scripts/link_check.py --external  # 可选：探测外部链接，需要网络
```

审计脚本的扫描范围不完全相同，结果需结合原文判断。短文、TODO 和超长页面属于人工复核候选，不应自动删除或拆分。frontmatter 检查当前只报告，不阻止提交；`--apply` 会写入文件，使用前先检查改动范围。

提交前的 Husky hook 执行代码块、导航和正文内部链接检查，需要 Python 3。完整构建在 PR 检查中执行，本地提交前可按需运行 `npm run docs:build`。搜索渲染回归测试通过 `node --test .github/scripts/test-search.mjs` 运行。链接检查器的回归测试通过 `python3 -m unittest discover -s scripts -p 'test_*.py'` 运行；可执行示例仍按所在目录的工具链验证。构建配置启用了 `ignoreDeadLinks`，因此构建成功后仍需检查链接，并在本地预览修改过的页面。

## 持续集成与发布

推送及 PR 会触发内部链接、frontmatter 和代码块检查；外部链接另有定期检查。推送到 `main` 或手动触发 `deploy.yml` 会安装锁定依赖、构建站点并发布至 GitHub Pages。`docs-build.yml` 在 PR 和手动触发时验证导航、正文内部链接、链接与搜索回归测试及全站构建。

提交信息沿用 `docs(kernel): 描述`、`refactor(structure): 描述` 或 `chore: 描述`。PR 说明改动主题和验证结果；修改页面布局或导航时附截图。
