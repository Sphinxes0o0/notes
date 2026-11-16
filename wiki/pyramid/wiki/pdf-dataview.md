---
type: index
tags: [pdf, dataview]
created: 2026-05-20
---

# PDF 索引（Dataview）

> 当 `wiki/sources/` 下有 PDF source 页时，此查询自动生效。当前为模板。

```dataview
TABLE WITHOUT ID
  file.link AS "文件",
  author AS "作者",
  category AS "分类",
  size-mb AS "大小(MB)"
FROM "sources"
WHERE type = "source" AND source-type = "pdf"
SORT category ASC, file.name ASC
```

---

## 按分类筛选

```dataview
TABLE WITHOUT ID
  file.link AS "书名",
  author AS "作者"
FROM "sources"
WHERE type = "source" AND source-type = "pdf" AND category = "books"
SORT file.name ASC
```

## 按标签筛选

```dataview
TABLE WITHOUT ID
  file.link AS "文件",
  tags AS "标签"
FROM "sources"
WHERE type = "source" AND source-type = "pdf" AND contains(tags, "eBPF")
SORT file.name ASC
```

---

> 提示：创建 PDF source 页的模板在 `wiki/.templates/pdf-source.md`
