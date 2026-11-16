---
type: entity
tags: [hyperscan, intel, pattern-matching, regex, nids]
created: 2026-05-29
sources: [github-snort3-parser-search]
---

# Intel Hyperscan

## Definition

Intel Hyperscan is a high-performance multiple pattern matching library developed by Intel, used in network security applications (like Snort) to match packet payloads against thousands of regex patterns simultaneously using SIMD (SSE/AVX) instructions.

## Key Characteristics

- **Software-based**: Runs on commodity CPU with SIMD instructions
- **Hybrid matching**: Combines NFA/DFA/Aho-Corasick algorithms
- **Pattern format**: PCRE-compatible regular expressions
- **Use case**: Deep packet inspection (DPI), intrusion detection, data exfiltration detection

## How It Works in Snort3

Snort3 uses Hyperscan for:
1. **Rule matching**: Thousands of signatures checked simultaneously
2. **Stream reassembly**: Pattern matching on reassembled TCP streams
3. **HTTP inspect**: Regex matching on HTTP headers/URIs

## Related Concepts

- [[snort3-parser-search]] — Snort3 parser and search engine
- [[snort3-stream]] — TCP stream processing
- [[linux-intrusion-detection]] — Linux IDS ecosystem

## Sources
- [[github-snort3-parser-search]]
