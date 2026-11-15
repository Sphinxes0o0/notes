---
search: false
title: "Pi Agent"
description: "**PI Agent** (π Agent) is a minimal, extensible terminal coding harness that adapts to your workflows rather than forcing you to change them. Originally created by Mario Zechner, it has grown into a…"
---
# Pi Agent

**PI Agent** (π Agent) is a minimal, extensible terminal coding harness that adapts to your workflows rather than forcing you to change them. Originally created by Mario Zechner, it has grown into a full-featured AI agent framework with multiple implementations and a rich ecosystem.

The core philosophy is to stay small at its core while being extensible through TypeScript extensions, skills, prompt templates, themes, and pi packages.

> **Note:** "PI" or "π" refers to multiple related but distinct projects — the original TypeScript/Node.js implementation and several forks/ports (notably a Rust version and oh-my-pi). This document covers the main implementations.

---


## 分篇阅读

正文按原章节顺序分篇，旧章节链接仍可跳转。

- [Implementations](./pi-agent/01-sections)
- [2. pi-ai 统一 API：40+ Provider 的抽象](./pi-agent/02-sections)
- [2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors）](./pi-agent/03-sections)
- [5. 关键文件索引](./pi-agent/04-sections)
- [4. Subagent Task Fan-out 机制](./pi-agent/05-sections)

<script setup>
import LegacyAnchorRedirect from "../.vitepress/components/LegacyAnchorRedirect.vue"
import targets from "./pi-agent/legacy-anchors.json"
</script>

<LegacyAnchorRedirect :targets="targets" />
