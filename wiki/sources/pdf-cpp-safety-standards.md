---
type: source
created: 2026-05-23
source-type: pdf
title: "C++ Safety & Standardization Slides (2025)"
author: "Bjarne Stroustrup, Michael Wong, David Sankel"
date: 2025-12-13
size: medium
path: raw/PDFs/slides/
summary: "3 slides covering C++ evolution at 40 (Bjarne Stroustrup), C++ AI stack standardization (Michael Wong), and mitigating risks of AI-generated code (David Sankel)"
---

# C++ Safety & Standardization — Slides Collection

> Group source page for C++ language evolution, standardization, and AI code risk slides.

---

## Bjarne Stroustrup — C++跨越40载的成功经验与未来演进

**Speaker:** Bjarne Stroustrup (Columbia University)
**File:** `Bjarne_C++跨越40载的成功经验与未来演进.pdf` (57 pages, 18.6K chars)

Bjarne Stroustrup reflects on 40 years of C++, its design philosophy, and the path forward including "Profiles" for safety.

**Key takeaways:**
- **Why C++ succeeded:** It serves widespread needs, is manageable by "ordinary developers", and remains stable over decades
- **Core design principles:**
  - Flexible static type system, extensibility, zero-overhead, minimal explicit type conversions, resource management (prevent leaks), error handling (provide guarantees), flexible concurrency support, not limited to one style
- **Key features that mattered:**
  - "C with Classes": classes, constructors/destructors, virtual functions, iostreams, `const`, operators
  - C++98: exceptions, templates, STL, namespaces
  - C++11: concurrency, lambdas, `auto`, `constexpr`, `shared_ptr`
  - C++20: concepts, coroutines, modules, ranges, `span`, `format`
- **Stability vs Evolution:** "Code that worked in the past still works today" — backward compatibility is sacred
- **C++ developer count:** 16.3M in 2025, growing 72% in 4 years (~20%/year); nearly 7M new developers added
- **Future: "Profiles"** — A new mechanism to manage complexity and improve safety without breaking existing code. Profiles allow selective enforcement of safety guarantees (type safety, bounds safety, lifetime safety)
- Quote: "Any language claiming to be perfect is either a salesman or a fool, or both"

---

## Michael Wong — 新的AI使命：面向智能体时代的全栈C++标准化

**Speaker:** Michael Wong (Yetiware AI CTO, WG21 ML group chair)
**File:** `Michael_新的AI使命：面向智能体时代的全栈C++标准化.pdf` (12 pages, 1.5K chars)

Michael Wong presents the three-layer C++ AI stack and the standardization roadmap for C++ in the Agent era.

**Key takeaways:**
- **Three-Layer C++ AI Stack:**
  1. **Foundation (Data Science):** `std::data_frame` — a heterogeneous, column-oriented container to allow Pandas-like data manipulation in C++
  2. **Core Data Structures:** `mdspan` (multi-dimensional arrays), Tensors & Graphs
  3. **Execution (Performance & Parallelism):** Parallel algorithms, executors, SIMD
- **Future: `std::data_frame`** — The "next frontier" after ranges and statistics algorithms; experimental/future standardization
- **Agent Era:** C++ needs to support AI Agents at the language level; ImageNet moment for C++: standardized benchmarks and infrastructure for AI workloads
- The AI software stack is fracturing — C++ standardization aims to provide a unified foundation
- **Building a real Transformer layer:** Abstract device interface for CUDA/ROCm/CANN; INT8 quantization for deployment

---

## David Sankel — 拨开迷雾：规避AI生成代码的真实风险

**Speaker:** David Sankel (Adobe Principal Scientist, WG21 committee)
**File:** `David Sankel_拨开迷雾：规避AI生成代码的真实风险.pdf` (22 pages, 9.4K chars)

Beyond "AI makes mistakes" — a systematic analysis of stability, technical debt, and human debt risks from AI-generated code.

**Key takeaways:**
- **Problem #1 — Stale Knowledge:** AI models have stale training data; the landscape changes daily
- **Problem #2 — Code Churn:** GitClear 2024 study: 26% increase in "Code Churn" since AI assistants; decrease in code reuse → building a mountain of "write-only" code
- **Mitigation #3 — Senior Engineer Intervention:** Stop checking style (tools do that), start checking architecture. Key question: "Could this 50-line AI function be replaced by one `std::algorithm`?"
- **Problem #4 — Architectural Drift:** AI generates "Textbook C++", not "Your Project's C++". Symptoms: reinventing the wheel, paradigm mismatch, inconsistency
- **Mitigation #4 — The Spec Check:** Shift left — review the plan first, not the code. "Before you write code, list the existing classes and patterns you intend to use"
- **Problem #5 — The Death Spiral:** AI fails slightly → you prompt to fix → it breaks something else → repeat ×10 → 1 hour on a 15-minute task
- **Safe Integration Checklist:** 1) Use "plan mode" 2) Senior engineer review before merge 3) Define architectural boundaries 4) Automated integration tests 5) Limit AI scope to well-defined tasks

---

## Related Pages

- [[entities/cpp/cpp-safety]] — Safety-first C++ development, defense-in-depth
- [[entities/cpp/cpp-reflection]] — C++26 compile-time reflection
- [[entities/cpp/cpp-perf-optimization]] — Performance optimization techniques
- [[sources/pdf-cpp-slides]] — Previously ingested C++ slides (reflection, safety, perf, xLLM)
