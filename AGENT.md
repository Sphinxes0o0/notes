# AGENT.md — LLM Wiki Maintenance Manual

> 这是你的个人 LLM Wiki 维护手册。当 LLM agent 读到这个文件，它就知道如何维护这个 wiki。

---

## 核心理念

这个 wiki 是一个**持久化、可累积的知识库**。LLM 负责所有的维护工作（总结、交叉引用、更新），你负责筛选来源、提出问题、思考意义。

**两种核心操作：**
- **Ingest** — 添加新来源，LLM 更新相关页面
- **Query** — 提问，LLM 从 wiki 合成答案
- **Lint** — 定期健康检查

---

## 目录结构

```
pyramid/
├── raw/                      # Source Layer（只读，LLM 不修改）
│   ├── github/<owner>/<repo>/.meta.md   # GitHub 仓库元数据
│   ├── PDFs/{papers,books,slides}/       # PDF 文件（论文/书籍/演讲slides）
│   ├── bookmarks/            # 浏览器书签（markdown）
│   └── web/                  # Web clips
│
├── wiki/                     # Generated Layer（LLM 写 = Obsidian Vault）
│   ├── attachments/           # 图片/附件
│   ├── entities/             # 概念页面
│   ├── sources/              # 源文档摘要页
│   ├── synthesis/            # 综合分析、对比
│   └── temporal/journal/     # 日记
│
├── scripts/                  # 辅助脚本
├── AGENT.md                  # 本文件
├── index.md                  # 全局导航
└── log.md                    # 操作日志
```

---

## 来源类型与处理方式

### GitHub 仓库
- 路径：`raw/github/<owner>/<repo>/.meta.md`
- LLM 通过 `gh` CLI 或 GitHub MCP 获取仓库信息
- 不强制 clone，只在需要时读取
- `.meta.md` 包含：仓库描述、主要语言、最后更新时间、关键文件列表

### PDF 文件
- 路径：`raw/PDFs/{papers,books,slides}/`
- LLM 读取 PDF 内容，提取关键信息
- 生成摘要页：`wiki/sources/pdf-<slug>.md`
- 大文件（>50MB）标记到 frontmatter 的 `size: large`

### 浏览器书签
- 路径：`raw/bookmarks/*.md`
- 每组书签一个文件，按主题分类
- LLM 处理后生成：`wiki/sources/bookmark-<slug>.md`

### Web Clips
- 路径：`raw/web/`
- 通过 Obsidian Web Clipper 或其他工具保存
- 图片统一下载到 `wiki/attachments/`

---

## 页面类型规范

### 1. Entity 页面（概念）
```markdown
---
type: entity
tags: [概念, 机器学习]
created: 2026-01-15
sources: [pdf-attention-is-all-you-need, bookmark-ml-resources]
---

# 概念名

## 定义
一句话定义。

## 关键要点
- ...

## 相关概念
- [[另一概念]]

## 来源详情
- [[pdf-attention-is-all-you-need]]
- [[bookmark-ml-resources]]
```

### 2. Source 页面（来源摘要）
```markdown
---
type: source
source-type: pdf | github | bookmark | web
title: "标题"
author: "作者"
date: 2026-01-10
size: small | medium | large
path: raw/PDFs/papers/xxx.pdf
summary: "一句话总结"
---

# 来源标题

## 核心内容
...

## 关键引用
...

## 相关页面
- [[entity-xxx]]
- [[topic-xxx]]
```

### 3. Synthesis 页面（综合分析）
```markdown
---
type: synthesis
tags: [主题, 对比]
created: 2026-01-20
---

# 综合标题

## 背景
...

## 主要发现
...

## 对比分析
| 方面 | A | B |
|------|---|---|
| ... | ... | ... |

## 结论
...
```

### 4. Journal 页面（月度日记）
```markdown
---
type: journal
month: 2026-01
---

# 2026 年 1月

## 本月重点

## 关键进展

## 待续
```

---

## Ingest 工作流

1. 你把新来源放入 `raw/` 对应目录
2. 告诉 LLM："请 ingest [来源路径]"
3. LLM 执行：
   - 读取来源内容
   - 生成摘要，讨论要点
   - 在 `wiki/sources/` 创建摘要页
   - 更新 `wiki/entities/` 相关概念
   - 更新 `index.md`
   - 在 `log.md` 追加 ingest 记录
   - 交叉引用相关现有页面

---

## Query 工作流

1. 你提问
2. LLM 读取 `index.md` 了解 wiki 结构
3. LLM 找到相关页面
4. 合成答案，可选输出格式：
   - markdown 页面 → 可存回 wiki
   - 对比表格
   - Marp 幻灯片
   - 图表

---

## Lint 工作流

定期（每月或每季度）告诉 LLM："请 lint wiki"

检查项：
- 页面间矛盾
- 过时信息（被新来源 supersede）
- 孤立页面（无 inbound links）
- 缺失交叉引用
- 重要概念但无专属页面

---

## 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| Entity | `<slug>.md` | `attention-mechanism.md` |
| Source (PDF) | `pdf-<slug>.md` | `pdf-attention-is-all-you-need.md` |
| Source (GitHub) | `github-<owner>-<repo>.md` | `github-karpathy-makemore.md` |
| Source (Bookmark) | `bookmark-<slug>.md` | `bookmark-ml-resources.md` |
| Synthesis | `topic-<subject>.md` | `topic-llm-agents.md` |
| Comparison | `comparison-<a>-vs-<b>.md` | `comparison-rwkv-vs-transformer.md` |
| Journal | `<YYYY-MM>.md` | `2026-01.md` |

---

## frontmatter 规范

所有 wiki/ 下的页面必须包含：

```yaml
---
type: entity | source | synthesis | journal
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD   # 可选，首次创建时省略
sources: []           # 仅 entity 和 synthesis
---
```

---

## 特殊文件

### index.md
- 每次 ingest 后更新
- 按 category（entities/sources/synthesis/journal）组织
- 每项：链接 + 一句话描述 + 元数据

### log.md
- Append-only 操作日志
- 格式：`## [YYYY-MM-DD] ingest | query | lint | <source-name>`
- 示例：`## [2026-01-15] ingest | pdf-attention-is-all-you-need`

---

## Obsidian 配套

- Vault 根目录：`wiki/`
- 附件文件夹：`attachments/`
- 模板文件夹：`.templates/`（Templater 插件）
- 插件推荐：Templater, Dataview, QuickAdd, Marp, Image Toolkit

---

## 理念

> "LLM 的工作是把所有繁琐的维护工作做好——总结、交叉引用、保持一致。人的工作是筛选来源、提出好问题、思考意义。"
>
> 参考：Karpathy LLM Wiki, Vannevar Bush's Memex (1945)

---

## Quality Gates

> 所有 agent 必须遵守。Ingest 后 Reviewer 逐项验证。

### Cross-Link Quality Gate

- 每个 entity 页面 ≥2 条指向其他 entity 的 [[wikilinks]]（index/dashboard/source 不计）
- 每对相关 entity 应该互链
- 禁止仅靠 index/dashboard 串联的星形结构

### Agent Behavior Gate

来自 Karpathy Claude Code Guidelines：

1. **Think Before Coding** — 不确定就问，不要默默猜测
2. **Simplicity First** — 最少代码，不过度抽象
3. **Surgical Changes** — 只改该改的，不动无关代码
4. **Goal-Driven Execution** — 先定验收标准，再写代码
