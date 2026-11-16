---
type: source
source-type: pdf
title: "<% tp.system.prompt('PDF 标题') %>"
author: "<% tp.system.prompt('作者') %>"
date: <% tp.system.prompt('日期 (YYYY-MM-DD)', '2026-01-01') %>
category: <% tp.system.prompt('分类 (books/papers/slides)', 'papers') %>
tags: []
size-mb: 0
path: "raw/PDFs/<% tp.system.prompt('分类路径', 'papers') %>/<% tp.system.prompt('文件名') %>"
summary: ""
---

# <% tp.frontmatter.title %>

**作者:** <% tp.frontmatter.author %>
**日期:** <% tp.frontmatter.date %>
**分类:** <% tp.frontmatter.category %>
**路径:** `<% tp.frontmatter.path %>`

## 核心内容

<!-- LLM ingest 后填充 -->

## 关键要点

-

## 相关页面

-
