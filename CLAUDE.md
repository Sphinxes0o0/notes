# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Sphinx's technical notes repository - a personal knowledge base built with VitePress and deployed to GitHub Pages. Content is organized into:

- **`notes/`** - Main technical notes (C/C++, network, OS, system programming, middleware, tools)
- **`courses/`** - Course materials (excluded from VitePress builds via `srcExclude`)
- **`resources/`** - Resource files

## Commands

```bash
npm install           # Install dependencies
npm run docs:dev      # Start VitePress dev server
npm run docs:build     # Build for production
npm run docs:preview   # Preview production build
```

## Architecture

- **Framework**: VitePress v2 (static documentation site generator)
- **Base path**: `/notes/` (configured for GitHub Pages deployment)
- **VitePress config**: `.vitepress/config.mjs` - contains all navigation and sidebar configuration
- **Build output**: `.vitepress/dist` (uploaded to GitHub Pages artifact)
- **Custom plugins**: `.vitepress/plugins/readingTime.mjs` (reading time calculation)
- **Excluded content**: `courses/`, `wiki/` directories are excluded from VitePress processing via `srcExclude`

## Content Structure

```
notes/
├── ccpp/              # C/C++ notes (C language, C++ containers, memory management)
├── network/           # Network notes (TCP/IP, Linux Netfilter/nftables)
├── os/                # Operating system notes
├── sys/               # System programming (IPC, ELF, design patterns)
├── midware/           # Middleware (DoIP, SOME/IP, vSOME/IP)
├── tools/             # Tool usage notes (Vim, Netcat, etc.)
├── kernel/            # Linux kernel deep-dive (mm, VFS, block, net, sched, etc.)
├── security/          # Security tools (masscan, falco, snort)
├── qemu/              # QEMU architecture analysis
├── datastructure/     # Data structures course
├── design_patterns/   # Design patterns course
├── network_fundamentals/  # Network fundamentals course
├── os_fundamentals/   # Operating system fundamentals course
└── resources/        # Resource files
```

## GitHub Actions

Auto-deploy is configured in `.github/workflows/deploy.yml` - pushes to `main` trigger automatic deployment to GitHub Pages.

## CI/CD

- `.github/workflows/audit-codeblocks.yml` - Automatically audits markdown code blocks on push/PR
  - Checks for unclosed code blocks, invalid language markers, and content bleeding
  - Script: `.github/scripts/audit-codeblocks.js`

## Agent Parallelism

This project supports **up to 10 concurrent agents** for parallel tasks:
- Content auditing across multiple directories simultaneously
- Batch fixing of code block issues
- Independent file processing (each agent can work on different files/directories)

Typical parallel workflow: Launch multiple agents with non-overlapping file scopes.
