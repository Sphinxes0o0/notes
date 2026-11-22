# Repository Guidelines

## Project Structure & Module Organization

This repository publishes technical learning notes with VitePress. Markdown content lives directly in topic directories such as `kernel/`, `ccpp/`, `network/`, `sys/`, `security/`, and `coding_agent/`. Use nearby `index.md` files as topic entry points. Hands-on examples live alongside notes, including `kernel/handson/` and `ccpp/concurrency/`.

Site configuration and plugins reside in `.vitepress/`; static assets live in `public/`, `resources/`, and topic-local image directories. Maintenance utilities are in `scripts/` and `.github/scripts/`. Deployment is configured in `.github/workflows/deploy.yml`. The site currently excludes `android/` from VitePress processing.

## Build, Test, and Development Commands

- `npm ci`: install dependencies from `package-lock.json` and initialize Husky hooks.
- `npm run docs:dev`: start the local documentation server.
- `npm run docs:build`: generate the site in `.vitepress/dist/`.
- `npm run docs:preview`: preview the generated site locally.
- `node .github/scripts/audit-codeblocks.js`: check configured content directories for malformed Markdown code fences.

The pre-commit hook checks code fences, navigation, and internal links. Local development and GitHub Actions use Node 22 via `.nvmrc`. Run `npm run docs:build` for a full site build.

## Coding Style & Naming Conventions

Match surrounding documentation, including its predominantly Chinese prose and technical English identifiers. Give new topic pages YAML `title` frontmatter and a descriptive H1. Use relative links, language-tagged fenced code blocks, and descriptive lowercase filenames matching adjacent pages, such as `block_scheduler.md`.

Follow local indentation: `.vitepress/config.mjs` uses two spaces. Preserve existing conventions in embedded C, C++, Rust, and scripts. No repository-wide formatter or linter is configured. Update topic indexes and the VitePress sidebar when adding navigable content.

## Testing Guidelines

There is no repository-wide test framework or coverage target. Build the documentation, run the code-block audit, and inspect changed pages in the browser. Run `npm run check:links` and `npm run check:navigation` to verify site links and navigation. For Pyramid wikilinks, run `python3 wiki/pyramid/scripts/lint_wiki.py` and inspect its broken-link report. Validate executable examples using their own local toolchains and instructions.

## Commit & Pull Request Guidelines

Recent commits follow `type(scope): description`, using types such as `docs`, `refactor`, and `chore`; scopes are optional. Example: `docs(kernel): clarify block scheduler notes`.

Keep changes focused. In pull requests, explain affected topics, list validation performed, and link related issues when applicable. Include screenshots for visible layout or navigation changes.
