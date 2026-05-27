---
type: entity
tags: [compiler, mlir, fuzzing, llvm, testing]
created: 2026-05-27
sources: [pdf-mlir-fuzzing, pdf-cpp-slides]
---

# MLIR Compiler Fuzzing

## Definition

MLIR compiler fuzzing is the application of coverage-guided fuzzing to MLIR-based compilers. Rather than generating C/C++ programs and translating to MLIR (low diversity), MLIRSmith directly generates valid MLIR programs from dialect op definitions, discovering semantic bugs in passes and cross-dialect transformations.

## Key Concepts

### Traditional vs. MLIR Fuzzing

| 方法 | 输入 | 问题 |
|------|------|------|
| Csmith→C→MLIR | C programs | Low MLIR structural diversity |
| MLIRSmith | Valid MLIR programs | Direct coverage of MLIR semantics |

### MLIRSmith Approach (ASE'23)

1. **Program Templates**: parameterized op sequences from dialect definitions
2. **Syntactic Validity**: generated from actual op semantics (types, regions)
3. **Semantic Validity**: op preconditions checked during generation
4. **Cross-Pass Testing**: random pass pipelines discover inter-pass bugs

### Bug Categories Found

- **Intra-pass**: invalid canonicalization producing UB
- **Inter-pass**: ordering dependencies between bufferize and loop conversion
- **Dialect boundary**: incomplete type conversion across dialect interfaces
- **Verifier bypass**: subtle IR that passes verifier but causes runtime crash

### Fuzzing Infrastructure

```
libFuzzer (coverage-guided)
    ↓
MLIR IR Generator (dialect ops + type constraints)
    ↓
Pass Pipeline (random pass combinations)
    ↓
Verifier → Execution → Crash Detection
```

## Related Pages

- [[entities/ai-mlir-compilation]] — MLIR编译基础设施（dialects/passes/ lowering）
- [[entities/cpp/mlir-fuzzing]] — MLIR模糊测试entity（已存在）
- [[entities/cpp/compiler-ai-software-stack]] — AI编译器软件栈
- [[cpp-index]] — C++编译器生态

## Source Details

- [[sources/pdf-mlir-fuzzing]] — MLIR编译器基础设施模糊测试（赵英全，2024）