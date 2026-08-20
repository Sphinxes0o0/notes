---
title: "Solving the Bottom Turtle · 中文翻译"
description: "按你的要求，对每张图的处理策略是："
---
# Solving the Bottom Turtle · 中文翻译

> **原书**：*Solving the Bottom Turtle — a SPIFFE Way to Establish Trust in Your Infrastructure via Universal Identity*（2020）
> **作者**：Daniel Feldman、Emily Fox、Evan Gilman、Ian Haken、Frederick Kautz、Umair Khan、Max Lambrecht、Brandon Lum、Agustín Martínez Fayó、Eli Nesterov、Andres Vega、Michael Wardrop
> **许可**：本翻译基于 [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/legalcode) 公开。**请保留原作者署名与协议说明**。
> **翻译策略**：技术直译 + 段落重排；**专有项目名、协议名、API 名、CLI 命令、配置字段、证书/加密术语一律保留英文**；首次出现的关键概念以"中文（English）"形式给出，后续沿用英文。

## 目录

| 顺序 | 文件 | 原书章节 | 原书页码 |
|---:|---|---|---:|
| 0 | **00-frontmatter.md** | 扉页、致谢、About the book、About Zero the Turtle | p.1–5 |
| 1 | **ch01-history-and-motivation.md** | 第 1 章　SPIFFE 的历史与动机 | p.9–22 |
| 2 | **ch02-benefits.md** | 第 2 章　收益 | p.23–37 |
| 3 | **ch03-general-concepts-behind-identity.md** | 第 3 章　身份背后的通用概念 | p.38–51 |
| 4 | **ch04-introduction-to-spiffe-and-spire.md** | 第 4 章　SPIFFE 与 SPIRE 概念入门 | p.52–77 |
| 5 | **ch05-before-you-start.md** | 第 5 章　动手之前 | p.78–103 |
| 6 | **ch06-designing-a-spire-deployment.md** | 第 6 章　设计一个 SPIRE 部署 | p.104–132 |
| 7 | **ch07-integrating-with-others.md** | 第 7 章　与外部集成 | p.133–145 |
| 8 | **ch08-using-spiffe-identities-to-inform-authorization.md** | 第 8 章　用 SPIFFE 身份驱动授权 | p.146–158 |
| 9 | **ch09-comparing-spiffe-to-other-security-technologies.md** | 第 9 章　与其他安全技术的对比 | p.159–167 |
| 10 | **ch10-practitioners-stories.md** | 第 10 章　从业者故事 | p.168–178 |
| A | **11-glossary.md** | 附录 A　术语表（Glossary） | p.179–189 |
| B | **12-notes.md** | 附录 B　注释（Notes） | p.190–191 |
| C | **13-epilogue.md** | 附录 C　后记（Epilogue） | p.192 |
| — | **TERMS.md** | 翻译术语对照表 | — |

## 工程资产

- `assets/pages/page-XXX.png`：原 PDF 全部 194 页 raster（150 DPI 级别），按需引用——对那些 mermaid 难以还原、或者原图本身信息密度高的图（如复杂概念图、3D 示意、零信任架构图），md 内已用 `见 assets/pages/page-XXX.png` 形式标注。

## 翻译约定的几个细节

- **数字 + 单位**：遵循英文原版的"数字 + 半角空格 + 单位"格式（如 `128 kB`、`12-17 mS`）。这种格式在英文里可读性更好，也更贴合原版。
- **代码 / 命令 / 路径 / URL**：全部保留英文原样，不译。
- **章节顺序号**：以"第 X 章"开头，便于目录检索和交叉引用。
- **重要陈述**：用引用块（`>`）凸显关键洞察。
- **图引用**：用引用块 + 路径引用形式，既不破坏阅读节奏，又方便后续你切图替换。
- **结构图、流程图、序列图**：当前以"文字描述 + 原图引用"为主；**如果要把图换成 mermaid**，可作为后续工作——所有图意都已经在 md 中做了完整描述。
- **章节内所有小标题、要点列表、表格、代码块**都按原版结构 1:1 复刻。

## 关于"复杂图如何处理"

按你的要求，对每张图的处理策略是：

1. **结构 / 流程 / 序列图**：将来可换成 mermaid；当前先用 `见 assets/pages/page-XXX.png` 引用。
2. **复杂示意图 / 概念图 / 插画**：直接引用 `assets/pages/page-XXX.png` 整页 PNG（已经在第一章起按页提取）。
3. **mermaid 表达不了的图**：文字描述 + 占位标注。

> **建议**：等你扫完一遍翻译后，告诉我哪些图你想替换成 mermaid，我再针对性重画。

## 翻译与原书对应页码

| md 文件 | 起始原书页 | 结束原书页 |
|---|---:|---:|
| ch01 | p.9 | p.22 |
| ch02 | p.23 | p.37 |
| ch03 | p.38 | p.51 |
| ch04 | p.52 | p.77 |
| ch05 | p.78 | p.103 |
| ch06 | p.104 | p.132 |
| ch07 | p.133 | p.145 |
| ch08 | p.146 | p.158 |
| ch09 | p.159 | p.167 |
| ch10 | p.168 | p.178 |
| 11-glossary | p.179 | p.189 |
| 12-notes | p.190 | p.191 |
| 13-epilogue | p.192 | p.192 |

## 致谢

- 感谢原书作者团队把这么硬核的工作方法论写出来，**并以 CC BY 4.0 开放**。
- 翻译过程中用到的工具链：`pypdfium2`（PDF 渲染）、`pdfplumber`（PDF 文本提取）、`pypdf`（PDF outline 解析）。所有图按页 raster 出来作为原图资产，**未做任何形式的篡改**。

---

**Trust in Zero.** 🐢
