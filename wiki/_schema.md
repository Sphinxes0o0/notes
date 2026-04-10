# LLM Wiki Schema

This file instructs the LLM on how to maintain the wiki. Read this before every ingest, query, or lint operation.

## Core Principles

1. **Incremental Compilation**: Never regenerate all pages from raw sources. Always work incrementally.
2. **Immutable Raw**: Never modify files in `raw/` or `sources/`. All synthesis happens in entities/, concepts/, etc.
3. **Cross-Reference**: Every page should link to related pages. Wiki is a graph, not a list.
4. **Append-Only Log**: All operations are logged to `log.md` with timestamp.

## Three Core Operations

### Ingest
When a new source document is added to `raw/`:
1. Read the document
2. Create a summary page in `sources/` named after the document
3. Extract entities and create/update pages in `entities/`
4. Extract concepts and create/update pages in `concepts/`
5. Add cross-links between related pages
6. Update `index.md` with new entries
7. Append operation to `log.md`

### Query
When asked a question:
1. Search the wiki for relevant pages
2. Synthesize an answer from compiled knowledge
3. If answer is incomplete, note what is missing
4. Optionally create a new page in `explorations/` with the full research
5. Append the query and answer to `log.md`

### Lint
Periodically:
1. Check for orphan pages (no incoming links)
2. Check for stale content (sources updated but wiki not)
3. Check for broken links
4. Check for contradictions between pages
5. Report issues but do not auto-delete — flag for human review
6. Append lint results to `log.md`

## Page Structure

### Source Summary Pages (sources/)
```markdown
---
title: Document Title
source: original filename
date: YYYY-MM-DD
tags: [tag1, tag2]
---

## Summary

One paragraph summary of the document.

## Key Points

- Point 1
- Point 2

## Related

- [[../entities/Entity Name]]
- [[../concepts/Concept Name]]
```

### Entity Pages (entities/)
```markdown
---
title: Entity Name
type: person | company | project | tool | other
tags: [tag1, tag2]
---

## Definition

Brief definition.

## Notes

## Related

- [[../entities/Other Entity]]
- [[../concepts/Related Concept]]
```

### Concept Pages (concepts/)
```markdown
---
title: Concept Name
tags: [tag1, tag2]
---

## Definition

## Key Points

## Examples

## Related

- [[../entities/Related Entity]]
- [[../concepts/Parent Concept]]
```

## Naming Conventions

- Files: kebab-case.md (e.g., `tcp-protocol.md`)
- Links: Use wikilinks [[../path/name]] for internal references
- Tags: lowercase, hyphen-separated

## Index

`index.md` is the catalog of all wiki pages. Keep it updated with:
- All entity pages (grouped by type)
- All concept pages (grouped by theme)
- All source summaries (grouped by topic)
- All explorations

## Log Format

All operations append to `log.md`:

```
## YYYY-MM-DD HH:MM

### Ingest
- Source: filename
- Action: created/updated pages
- Notes:

### Query
- Question: ...
- Answer: ...
- Pages consulted: ...

### Lint
- Orphans found: ...
- Stale content: ...
- Issues: ...
```
