---
type: source
created: 2026-05-23
source-type: pdf
tags: [cpp, engineering, practices]
title: "Engineering Practices Slides (2025)"
author: "Various (Baidu, Meituan, CSDN, Xiaomi, Parasoft, Tencent, Qoder, Bloomberg, Agibot)"
date: 2025-12-13
size: large
path: raw/PDFs/slides/
summary: "10 slides covering AI coding agents in enterprise, AI-native maturity models, C++ in IoT, AI-powered testing, CLI coding tools, software engineering maturity, object lifetime, and robotics build systems"
---

# Engineering Practices — C++ Slides Collection

> Group source page for engineering practice slides spanning AI coding, testing, IoT, maturity models, and build systems.

---

## 邢俊威 — Coding Agent 重塑软件开发工作

**Speaker:** 邢俊威 (Baidu Engineering Efficiency Department)
**File:** `邢俊威_Coding Agent 重塑软件开发工作.pdf` (25 pages, 4.0K chars)

Baidu's Comate coding agent journey.

**Key takeaways:**
- **AI coding evolution:** Completion (2022) → Chat & RAG (2023) → Agent (2024-2025); AI code generation ratio climbing 5%→80%+
- **Baidu Comate results (2024-2025):**
  - 85%+ engineers using it; 52%+ AI code generation ratio
  - 73%+ agent active users; 90%+ user satisfaction
  - 12% overall Baidu-wide efficiency improvement
- **Comate agent features:**
  - Understanding intent, decomposing tasks, calling tools, auto-execution, self-correction
  - Context engine design for project-level understanding
  - Zulu: full-auto coding agent (2025); Zulu CLI; AI IDE
- **Key insight:** Product form shifting from IDE plugin to autonomous agent

---

## 马良焰 — AI Coding在企业内的实践分享

**Speaker:** 马良焰 (Meituan, R&D Quality and Efficiency)
**File:** `马良焰_AI Coding在企业内的实践分享.pdf` (27 pages, 3.6K chars)

Meituan's enterprise AI coding adoption practices.

**Key takeaways:**
- **Industry trends (2025 data):**
  - Microsoft: 20-30% of code by AI
  - Google: 30%+ of new code AI-generated (up 5% in 6 months)
  - Meta/Zuckerberg: predicts 50% of coding by AI in 2026
  - Anthropic: predicts 90% code touched by AI within months
- **Meituan MCopilot → CatPaw evolution:**
  - Started with IDE plugin (code completion, unit test generation, chat)
  - Evolved to: Code Agent, Next Edit, context engineering
  - Covers: JetBrains, Xcode, VSCode IDEs
- **Enterprise adoption challenges:** Security (code privacy), integration with existing toolchains, developer training

---

## 李建忠 — AI原生软件研发成熟度模型与演进

**Speaker:** 李建忠 (Singularity Intelligence Research Institute / CSDN)
**File:** `李建忠_AI原生软件研发成熟度模型与演进.pdf` (42 pages, 6.5K chars)

A maturity model for AI-native software development and the paradigm shift to Agent-based software.

**Key takeaways:**
- **Paradigm shifts in software:**
  - Application form: Desktop → Web → App → Agent
  - Development form: Waterfall → Agile → Cloud-Native → AI-Native
- **Agent capability maturity ladder:**
  1. Action (bit/atom)
  2. Memory (long-term memory)
  3. Reasoning (reinforcement learning)
  4. Tools (MCP protocol)
  5. Collaboration (A2A — Agent-to-Agent)
  6. Planning
- **Training model → Reasoning model shift:**
  - Training: pre-train (knowledge) → post-train (manners)
  - Inference: fast thinking → slow thinking (chain-of-thought)
- AI-native maturity model provides a framework for organizations to assess their AI adoption level

---

## 董俊杰 — C++语言在Xiaomi Vela中的应用、体验及前景

**Speaker:** 董俊杰 (Xiaomi Vela)
**File:** `董俊杰_C++语言在Xiaomi Vela中的应用、体验及前景.pdf` (37 pages, 5.6K chars)

C++ usage in Xiaomi Vela IoT/embedded operating system.

**Key takeaways:**
- **Xiaomi Vela architecture:**
  - Vela IoT OS (lightweight OS)
  - Vela Safety OS (functional safety)
  - Vela Hybrid OS (fusion system)
  - Based on NuttX kernel + Linux kernel
- **C++ in embedded/IoT:**
  - Practical, everyday C++ patterns for constrained environments
  - Memory-efficient object models for IoT devices
  - Real-world C++ usage on resource-constrained hardware
- Focus on pragmatic, immediately applicable techniques rather than cutting-edge features

---

## 李彦博 — 从自动化到智能化：AI重塑C++软件测试未来

**Speaker:** 李彦博 (Roche Li, Parasoft)
**File:** `李彦博_从自动化到智能化 AI重塑C++软件测试未来.pdf` (36 pages, 5.7K chars)

How AI is transforming C++ software testing.

**Key takeaways:**
- **Traditional testing bottlenecks:** Slow defect localization, difficult test case design, insufficient complex scenarios, high maintenance costs, functional safety challenges
- **AI opportunities in testing:**
  - AI-powered unit test generation for C++ code
  - Automated defect localization using ML
  - Smart test scenario coverage analysis
- **Parasoft approach (since 1987):**
  - AEP (Automatic Error Prevention) theory
  - Complete quality suite: code analysis, unit testing, Selenium Web UI, API testing, service virtualization
- **AI integration:** LLMs for test code generation, automated assertion generation, intelligent test maintenance

---

## 汪晟杰 — 从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站

**Speaker:** 汪晟杰 (Tencent, CodeBuddy Product Lead)
**File:** `汪晟杰_从上下文工程到AI Spec Coding：C++在无图形终端时代的下一站.pdf` (38 pages, 8.4K chars)

CodeBuddy CLI — bringing AI coding to the terminal for C++ developers working in headless environments.

**Key takeaways:**
- **The terminal as C++'s natural habitat:** SSH + Shell is the only reliable entry point during production incidents; IDE doesn't work in Docker/K8s pods, cross-compile chains, or remote servers
- **CLI advantages over IDE:** Zero context switching, composability (AI orchestrates existing toolchains), cross-environment consistency
- **C++ developer + AI gap:** Remote/Docker scenarios lack GUI IDE; traditional Copilot-style completion fails without real build context
- **CodeBuddy CLI features:**
  - Agentic Coding: understands entire codebase, runs commands, edits files
  - Background Agent mode: long-running async execution
  - Command, Subagent, MCP, Hook, Skills extensibility
  - Spec-Coding: plan-first approach before code generation
- **Key insight:** "True productivity isn't adding another interface — it's removing one Alt-Tab"

---

## 徐亮亮 — Qoder CLI：终端里的智能伙伴

**Speaker:** 徐亮亮 (Qoder Technical Expert)
**File:** `徐亮亮_Qoder CLI - 终端里的智能伙伴.pdf` (22 pages, 8.8K chars)

Qoder CLI — an AI-powered command-line development companion.

**Key takeaways:**
- **Three core design challenges:**
  1. Reduce cognitive burden (simple, usable)
  2. Seamless integration (low integration barrier)
  3. Improve development efficiency
- **Two interaction modes:**
  - TUI (Interactive): natural language, visual interface compatible with terminal keyboard habits
  - Headless: traditional CLI with pipe support and scripting
- **Product form comparison:** TUI offers the best balance of flexibility, usage barrier, and integration difficulty vs SDK and GUI
- **Qoder CLI capabilities:** Code generation, understanding developer intent, autonomous completion of complex programming tasks

---

## Pete Muldoon — 软件工程进阶金字塔 (The Pyramid of Software Engineering Mastery)

**Speaker:** Pete Muldoon (Bloomberg, Senior Engineering Lead, Ticker Plant)
**File:** `Pete_软件工程进阶金字塔.pdf` (56 pages, 21.7K chars)

A career maturity model for software engineers — progressing through levels of technical and organizational mastery.

**Key takeaways:**
- **What does "Done" mean?** Moving beyond code completion to systems thinking
- **Pyramid levels (bottom to top):**
  1. Code mastery: writing correct, efficient code
  2. Design and architecture: system-level thinking, patterns
  3. Process and collaboration: team dynamics, code review, CI/CD
  4. Business and domain understanding: connecting engineering to business value
  5. Leadership and mentoring: growing others, technical strategy
- **Practical advice:** Focus on continuous growth across all dimensions; technical skill alone is insufficient for senior roles
- Pete has been using C++ professionally since 1991; based on decades of industry experience

---

## 吴咏炜 — To Be or Not to Be: On Object Lifetime

**Speaker:** 吴咏炜
**File:** `吴咏炜To Be or Not to Be - On Object Lifetime.pdf` (49 pages, 8.7K chars)

C++ object lifetime analysis — when objects are constructed, destroyed, and how to manage memory safely.

**Key takeaways:**
- **Object lifetime fundamentals:** Constructor → valid state → use → destructor
- **Special cases:**
  - Objects created via `mmap` or placement `new`
  - Objects with `.init()` / `.cleanup()` pattern (two-phase construction)
  - Lifetime of subobjects, temporaries, and moved-from objects
- **Tools for lifetime analysis:** Compiler warnings, static analyzers, sanitizers
- Relationship to [[entities/cpp/cpp-object-lifetime]] — overlaps with existing entity content

---

## 田文鑫 — 具身机器人多仓源码构建体系

**Speaker:** 田文鑫 (Agibot / 智元机器人)
**File:** `田文鑫_具身机器人多仓源码构建体系.pdf` (15 pages, 1.0K chars)

Multi-repository source code build system for embodied robotics.

**Key takeaways:**
- **Agibot software architecture:** Brain (interaction, task planning) + Cerebellum (motion, passive safety); control algorithms need 500-1000Hz motor control frequency
- **Multi-repo management:**
  - Integration repo: aggregates all module versions, manages third-party dependencies, implements build toolchain, deployment
  - Module repos: independent implementations with autonomous versioning
  - Integration repo directly references module git commits → precise version alignment
- **Branch management:** Same-name branches across repos enable multi-repo MR pipelines; all repos merge synchronously
- **Build system:** Bazel-based; CI/CD automation via GitLab
- Open-source plan for the build framework

---

## Related Pages

- [[entities/cpp/cpp-object-lifetime]] — Object lifetime control in C++
- [[entities/cpp/cpp-safety]] — Safety-first C++ development
- [[sources/pdf-cpp-slides]] — Previously ingested C++ slides
- [[sources/pdf-cpp-safety-standards]] — Safety/standardization slides
- [[sources/pdf-cpp-ai-inference]] — AI/ML inference slides
