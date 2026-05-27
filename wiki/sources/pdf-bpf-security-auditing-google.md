---
type: source
source-type: pdf
title: "Stories from BPF Security Auditing at Google"
author: "Brendan Jackman (Google)"
date: 2023
size: medium
path: raw/PDFs/papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf
summary: "A practitioner's account of auditing eBPF for security vulnerabilities inside Google — covering the bug classes found, the audit methodology, and the hardening efforts that followed."
created: 2026-05-27
---

# Stories from BPF Security Auditing at Google

## Core Content

Brendan Jackman, a Google engineer, shares first-hand experience of a security audit of the Linux kernel's eBPF subsystem conducted internally. This is a rare practitioner-level look at eBPF security assessment.

### Audit Scope and Methodology

- **Scope**: Kernel eBPF subsystem (verifier, JIT compiler, map operations, program loading, attachment points).
- **Methodology**: Code review + fuzzing + static analysis. Fuzzing targets: verifier input (random eBPF programs), map operations (concurrent access), JIT compiler output (x86/arm64 code generation).
- **Timeline**: Multi-month effort with a team of ~4 kernel/security engineers.

### Bug Classes Found

1. **Verifier Bugs**: Logic flaws that allowed bypassing safety checks — out-of-bounds memory access, null pointer dereference, integer overflow in pointer arithmetic. Several CVEs resulted.
2. **Race Conditions**: Concurrent map access without sufficient locking led to use-after-free and data corruption. The eBPF subsystem's concurrent nature creates subtle race windows.
3. **JIT Compiler Vulnerabilities**: Speculative execution vulnerabilities (Spectre/Meltdown variants) in JIT-generated code. The JIT's optimization passes could be tricked into generating Spectre-gadget code.
4. **Map Leakage**: Incorrect reference counting on map file descriptors could leak kernel memory or allow double-free.
5. **Attachment Point Attacks**: Abuse of newer attach points (LSM, struct_ops) to override security hooks in unexpected ways.

### Mitigations Implemented

- **Verifier Hardening**: Added additional bounds checks, dead code elimination, and loop counting improvements.
- **Lock Annotations**: Added `__acquires`/`__releases` annotations to map functions to enable static analysis tools to catch locking violations.
- **JIT Hardening**: Spectre/Meltdown mitigations in JIT code generation, including retpolines and speculation barriers.
- **Fuzzing Infrastructure**: Integrated libBpfgo and AFL-based fuzzing into the kernel CI pipeline.

### Key Findings

- The eBPF verifier is the most critical security boundary — flaws there have broad implications.
- Fuzzing found more bugs than manual code review (80% vs 20% in this audit).
- Google's internal kernel patch set includes eBPF-specific hardening that eventually made it into mainline.

## Source Details

- **Author**: Brendan Jackman, Google
- **Path**: raw/PDFs/papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf
- **Size**: 748.3 KB
- **Domain**: eBPF security, kernel auditing, vulnerability research, Google