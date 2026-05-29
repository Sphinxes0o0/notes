---
type: source
source-type: bookmark
title: "Bevy Engine Guide (序言)"
author: "ailrid.github.io"
date: 2026-05-29
size: medium
path: https://ailrid.github.io/Bevy-Engine-Guide/
summary: "Systematic introduction to Bevy game engine (Rust ECS), covering architecture, plugin development, reflection, and rendering pipeline."
---

# Bevy Engine Guide

## Core Content

Systematic guide to Bevy game engine — a Rust-based engine built around Entity Component System (ECS) architecture.

### Key Topics
- **ECS Architecture**: Entity Component System pattern in Rust — composition over inheritance
- **Bevy Architecture**: Plugin system, app builder pattern, schedule/executor model
- **Reflection System**: Rust trait-based reflection for dynamic entity queries
- **Parallel Graph Construction**: DAG-based parallel task scheduling
- **Rendering Pipeline**: WGPU-based rendering, render graph architecture
- **Plugin Development**: Writing reusable Bevy plugins

### Book Structure (3 Volumes)
1. **Upper (Fundamentals)**: ECS basics, app structure
2. **Middle (Reflection & Parallel Graphs)**: Internal mechanics
3. **Lower (Rendering Pipeline)**: WGPU rendering system

## Why This Matters for Pyramid Wiki

- Rust ECS is a modern design pattern relevant to [[rust-language]] and game engine architecture
- Bevy exemplifies actor-like concurrency models applicable to broader systems programming
- Novel parallel execution model — relevant to [[concurrency]] and parallel computing discussions

## Related Pages
- [[rust-language]] - Rust fundamentals
- [[concurrency]] - concurrency patterns
