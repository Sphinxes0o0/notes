---
type: entity
tags: [software-engineering, project-management, programming]
created: 2026-05-23
sources: [pdf-misc-books]
---

# The Mythical Man-Month

## Definition

"The Mythical Man-Month" (Frederick P. Brooks Jr., 1975/1995) is a seminal book on software engineering based on Brooks' experience managing IBM's OS/360 project. Its central thesis is that **adding manpower to a late software project makes it later** — known as Brooks' Law.

## Key Concepts

### Brooks' Law
> "Adding manpower to a late software project makes it later."
- **Why**: New workers require training O(n) from existing workers
- **Communication overhead**: n(n-1)/2 communication paths
- **Partitioning limits**: Some tasks are inherently sequential

### The Second-System Effect
The second system a designer builds tends to be over-engineered — incorporating every feature that was left out of the first version. The solution is **conceptual integrity**: a single architect vision.

### No Silver Bullet (1986)
> "There is no single development, in either technology or management technique, which by itself promises even one order-of-magnitude improvement in productivity, reliability, or simplicity."
- **Essential difficulties**: Complexity, conformity, changeability, invisibility
- **Accidental difficulties**: Tools, languages, processes (these can be improved)

### The Surgical Team
Brooks advocates for a **chief programmer team** structure:
- **Surgeon** (chief programmer): Architect + implementer
- **Copilot**: Backup, research, performance
- **Administrator**: Personnel, budget, space
- **Toolsmith**: Build system, library support
- **Language lawyer**: Expert consultant

## Related Pages

- [[entities/software-engineering/mythical-man-month]] — (this page)
- [[sys-prog-index]] — System programming project management
- [[os-index]] — OS design as an example of large-scale software

## Source Details

- [[sources/pdf-misc-books]] — 人月神话 40周年纪念版
