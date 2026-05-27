---
type: entity
tags: [snort3, infrastructure, hash-table, file-processing, decompression, javascript-normalization]
created: 2026-05-27
sources: [github-snort3-infrastructure]
---

# Snort3 Infrastructure

## Overview

Snort3's infrastructure layer provides core utilities used across the entire IDS/IPS engine: hash table implementations, file processing pipeline, decompression framework, JavaScript normalization, and helper utilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Service Inspectors                                │
│              (HTTP, SMTP, POP, IMAP, SMB, FTP...)                       │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          js_norm                                         │
│                  JavaScript Normalizer                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │JSTokenizer  │  │JSIdentifierCtx│ │JSNormalizer │  │PDFJSNorm   │ │
│  │  (Flex)     │  │(var_xxxx alias)│ │ (buffers)   │  │(PDF extrac)│ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └────────────┘ │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          file_api                                        │
│                    File Processing Pipeline                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐            │
│  │FileFlows │  │FileContext│  │FileCache │  │FileCapture │            │
│  │(per-flow)│  │(per-file)│  │(verdict) │  │(disk store)│            │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │FileIdentifier│  │FileMemPool   │  │FileSegments  │                │
│  │(magic trie)   │  │(memory pool) │  │(reassembly)  │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       decompress                                          │
│                    File Decompression                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  PDF Parser │  │  SWF Parser   │  │ ZIP Parser  │  │ OLE Parser │ │
│  │(FlateDecode)│  │(ZLIB/LZMA)   │  │(VBA extract)│  │(VBA RLE)   │ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └────────────┘ │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           hash                                            │
│                     Hash Table Implementations                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐         │
│  │  XHash   │  │  ZHash    │  │  GHash   │  │SegmentedLruCache│      │
│  │(memcap+LRU)│ │(zero-alloc)│ │(simple) │  │(low contention)│      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                                   │
│  │HashLruCache │  │HashKeyOps     │                                   │
│  │(LRU list)   │  │(hash function)│                                   │
│  └──────────────┘  └──────────────┘                                   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         helpers                                           │
│                     Utility Library                                       │
│  Encoding: base64, BER, UTF-16/32    Search: Boyer-Moore, Hyperscan     │
│  Memory: memcap allocator, scratch    Ring: Ring2 (single-prod/consumer)│
│  I/O: stream buffers, JSON formatter  Events: EventGen, Infractions      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Hash Tables (hash/)

### XHash — Extended Hash (memcap + LRU)

Primary hash table for Snort. Enforces memory caps and uses LRU eviction.

```
XHash
├── HashKeyOperations (hash function + key compare)
├── HashLruCache[] (vector of LRU lists, supports multiple data types)
├── MemCapAllocator (enforces memcap)
└── HashNode* (linked list per row)
```

Key features:
- **Memcap enforcement**: Automatic node recovery (ANR) when memory exhausted
- **Multiple LRU caches**: Separate LRU policies for different data types
- **Thread-safe**: Used across packet processing threads

### ZHash — Zero-Allocation Hash

Pre-allocated hash table. Disables runtime allocations for latency-sensitive paths.

### GHash — Generic Hash

Simple non-LRU hash table. Building block for other implementations.

### LruCacheShared / SegmentedLruCache

Thread-safe LRU caches:
- `SegmentedLruCache`: 4 segments (configurable) to reduce lock contention
- Uses XOR-based segment selection for load balancing

### HashKeyOperations

Configurable hash function:
- `do_hash()`: Multiplies by scale, adds each byte, XORs with hardener
- When `SnortConfig::static_hash()`: fixed seed/scale/hardener for reproducibility
- Otherwise: random per-instance (thread-local RNG)

## File Processing (file_api/)

### Three-Stage Pipeline

```
File Flow                    Type Detection              Signature & Capture
─────────────────────────────────────────────────────────────────────────
file_process()        →    FileIdentifier        →    SHA256 calculation
(FileFlows)                 (magic trie)                 (OpenSSL)
                                │                           │
                                ▼                           ▼
                         FilePolicy                  FileCapture
                         (type-based verdict)        (memcap + disk store)
```

### FileIdentifier — Magic-based Type Detection

Trie data structure (256 branches per node) for byte-level pattern matching:
- `find_file_type_id()`: Traverses trie based on file magic bytes
- Supports shared nodes to reduce memory
- Context pointer for incremental scanning across packets

### FileCache — Verdict Caching

Stores file contexts keyed by (src_ip, dst_ip, src_port, file_id, asid):
- `cached_verdict_lookup()`: Check if verdict exists
- `apply_verdict()`: Block/log/reject based on policy
- Multi-process sharing via MPDataBus

### FileCapture — Memory + Disk

Two-tier storage:
1. **Memory**: FileMemPool (circular buffer, 1 writer + 1 reader)
2. **Disk**: Background thread writes to filesystem

Workflow: `process_buffer()` → `reserve_file()` → `store_file_async()`

### FileSegments — Out-of-Order Reassembly

Handles retransmissions and out-of-order file data:
- Maintains queue of segments with offsets
- `process_one()` / `process_all()` for sequential reassembly

## Decompression (decompress/)

### File Decomp Framework

Signature-based dispatcher:

| Signature | File Type | Decompressor |
|-----------|-----------|--------------|
| `%PDF-` | PDF | `file_decomp_pdf.cc` |
| `CWS`/`ZWS`/`FWS` | SWF | `file_decomp_swf.cc` |
| `PK\x03\x04` | ZIP | `file_decomp_zip.cc` |
| ZIP→`vbaProject.bin` | OLE | `file_olefile.cc` |

### PDF Decompression (FlateDecode)

Incremental PDF parser (PDF 32000-1:2008):
- States: `P_START` → `P_IND_OBJ` → `P_DICT_OBJECT` → `P_STREAM`
- `FlateDecode` filter triggers zlib `inflate()`
- Supports UTF-16BE → UTF-8 conversion

### SWF Decompression

- `CWS`: ZLIB compressed
- `ZWS`: LZMA compressed (if `HAVE_LZMA`)
- `FWS`: Uncompressed

### ZIP + VBA Extraction

```
ZIP Parser
├── Detects vbaProject.bin filename
├── Decompresses to OLE data
└── Passes to OLE Parser

OLE Parser (OleFile)
├── Parses header (sector size, FAT location)
├── Walks FAT/Mini-FAT sector chains
├── Directory entry traversal
└── RLE decompression of VBA stream
```

### VBA Extraction Pipeline

```
Office Document (ZIP)
  → vbaProject.bin (OLE Compound File)
      → VBA Stream (RLE compressed)
          → Extracted VBA Macro Code
```

## JavaScript Normalization (js_norm/)

### Purpose

Normalizes JavaScript to remove obfuscation for security analysis:
- Whitespace removal
- Identifier normalization (`var_xxxx` aliases)
- String concatenation
- Escape sequence decoding (`\uXXXX`, `\xXX`, `%XX`)
- Semicolon insertion (ASI)

### Architecture

```
JSNorm (orchestrator)
├── JSNormalizer (buffer management)
│   └── JSTokenizer (Flex lexer, 1260+ rules)
│       └── JSIdentifierCtx (identifier substitution + aliasing)
│
└── PDFJSNorm (PDF-extended)
    └── PDFTokenizer (Flex lexer for PDF structure)
```

### JSTokenizer — Flex Lexer

JavaScript tokenizer (Flex) with:
- **Token types**: IDENTIFIER, KEYWORD, PUNCTUATOR, OPERATOR, LITERAL
- **Scope tracking**: GLOBAL, BRACES {}, PARENTHESES (), BRACKETS []
- **Alias state machine**: ALIAS_NONE → ALIAS_DEFINITION → ALIAS_PREFIX → ALIAS_EQUALS → ALIAS_NEW → ALIAS_VALUE
- **Return codes**: EOS, SCRIPT_ENDED, BAD_TOKEN, IDENTIFIER_OVERFLOW, etc.

### JSIdentifierCtx — Identifier Management

Normalizes identifiers to `var_0000`–`var_ffff` (65536 unique):
- Scope stack (GLOBAL, FUNCTION, BLOCK)
- Alias tracking (e.g., `var a = console.log` → alias `a` → `console.log`)
- Ignore lists for `ident_ignore` / `prop_ignore` config

### PDFJSNorm — PDF JavaScript Extraction

Detects PDF via magic bytes (`%PDF-1.`):
- Extracts `/JS` dictionary entries
- Handles UTF-16BE encoded JavaScript
- Normalizes extracted JS through standard pipeline

### Event Detection

Generates detection events (GID 154) for:
- `EVENT_NEST_UNESCAPE_FUNC`: Nested unescape functions (obfuscation)
- `EVENT_BAD_TOKEN`: Invalid JavaScript syntax
- `EVENT_IDENTIFIER_OVERFLOW`: Too many unique identifiers
- `EVENT_BRACKET_NEST_OVERFLOW`: Excessive bracket nesting
- `EVENT_SCOPE_NEST_OVERFLOW`: Excessive scope nesting
- `EVENT_DATA_LOST`: Data gaps during normalization

## Helpers

### Pattern Matching

- **BoyerMooreSearch**: Classic right-to-left pattern matching, sub-linear in best case
- **LiteralSearch**: Factory that selects Boyer-Moore or Hyperscan based on `HAVE_HYPERSCAN`
- **HyperSearch**: Hardware-accelerated pattern matching via Intel Hyperscan

### Memory Management

- **MemCapAllocator**: Fixed-size block allocator with capacity limit
- **PrimedAllocator**: STL allocator that pools deallocations on freelist
- **ScratchAllocator**: Per-packet-thread scratch memory

### Ring Buffers

- **Ring2**: Single-reader single-writer with length-value records
- **RingLogic**: Lock-free coordination via atomic indices

### Encoding/Decoding

- **Base64Encoder**: 3-byte → 4-byte encoding (libb64)
- **BerReader**: ASN.1/BER parsing (INTEGER, BOOLEAN, BIT_STRING, STRING)
- **UtfDecodeSession**: UTF-16/32 le/be normalization + charset detection

## Related Concepts

- [[snort3-actions]] — Snort3 rule actions
- [[snort3-connectors]] — Service connectors (TCP/UDP/file/popen)
- [[snort3-events-filters]] — Event generation and 3-layer filter architecture
- [[snort3-flow]] — Flow tracking
- [[snort3-ips-options]] — IPS options
- [[snort3-framework]] — Plugin system, lifecycle, pig, shell
- [[snort3-control-startup]] — Control and startup

## Sources

- [[github-snort3-infrastructure]]
