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
- **Excluded content**: The `courses/` directory is excluded from VitePress processing but remains in the repo

## Content Structure

```
notes/
├── ccpp/       # C/C++ notes (C language, C++ containers, memory management)
├── network/    # Network notes (TCP/IP, Linux Netfilter/nftables)
├── os/         # Operating system notes (Linux kernel development)
├── sys/        # System programming (IPC, ELF, design patterns)
├── midware/    # Middleware (DoIP, SOME/IP, vSOME/IP)
└── tools/      # Tool usage notes (Vim, Netcat, etc.)
```

## GitHub Actions

Auto-deploy is configured in `.github/workflows/deploy.yml` - pushes to `main` trigger automatic deployment to GitHub Pages.
