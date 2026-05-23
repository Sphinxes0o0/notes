---
type: index
tags: [cpp, modern-cpp, stl]
created: 2026-05-22
---

# Modern C++ & STL

> C++11/14/17/20 features and the standard template library

## Modern C++ Features

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/move-semantics]] | Move semantics: rvalue references, std::move, std::forward, value categories | cpp, modern-cpp |
| [[entities/cpp/smart-pointers]] | Smart pointers: shared_ptr, unique_ptr, weak_ptr | cpp, modern-cpp |
| [[entities/cpp/lambda-expressions]] | Lambda expressions: capture, mutable, generic lambdas | cpp, modern-cpp |
| [[entities/cpp/auto-type-deduction]] | Type deduction: auto, decltype, decltype(auto) | cpp, modern-cpp |
| [[entities/cpp/constexpr]] | constexpr: compile-time evaluation, C++11/14/17/20 | cpp, modern-cpp |
| [[entities/cpp/raii]] | RAII: automatic resource management via constructor/destructor | cpp, modern-cpp |
| [[entities/cpp/concurrency]] | Concurrency: std::thread, mutex, atomic, future | cpp, modern-cpp |
| [[entities/cpp/variadic-templates]] | Variadic templates: parameter pack expansion, sizeof..., fold expressions | cpp, modern-cpp |
| [[entities/cpp/if-constexpr]] | if constexpr: compile-time branching, compile-time polymorphism | cpp, modern-cpp |
| [[entities/cpp/cpp20-features]] | C++20: Concepts, Modules, Coroutines, Ranges | cpp, modern-cpp, cpp20 |

## STL Components

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/cpp-stl-containers]] | Containers: vector/deque/list/set/map, unordered containers | cpp, stl |
| [[entities/cpp/cpp-stl-algorithms]] | Algorithms: sort/find/remove/transform, iterator配合 | cpp, stl |
| [[entities/cpp/cpp-stl-iterators]] | Iterators: categories, invalidation rules, adaptors | cpp, stl |
| [[entities/cpp/cpp-stl-functors]] | Function objects: functors, lambdas, function adaptors | cpp, stl |
| [[entities/cpp/cpp-stl-string]] | String: string implementation, string_view, efficient operations | cpp, stl |
| [[entities/cpp/cpp-stl-allocators]] | Allocators: memory management, custom allocators, allocator_traits | cpp, stl |

## Additional Topics

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/cpp-serialization]] | Serialization: JSON/XML/Protobuf/Boost/MessagePack, format comparison, versioning, security | cpp, serialization |
| [[entities/cpp/cpp-object-lifetime]] | Object lifetime control: restricting allocation to heap or stack via access control | cpp, object-lifetime |
| [[entities/cpp/cpp-reflection]] | C++26 compile-time reflection: `^^`, `[: :]` splice, `std::meta::info`, meta functions | cpp, cpp26, reflection |
| [[entities/cpp/cpp-safety]] | Safety-first C++: defense-in-depth (sandbox/harden/detect/prevent), C++26 Contracts | cpp, safety, security |
| [[entities/cpp/cpp-perf-optimization]] | CPU cache optimization, SIMD, branch prediction, profiling tools (perf/eBPF/IPT) | cpp, performance |
| [[entities/cpp/cpp-llm-inference]] | C++ for LLM inference: PD/EPD separation, KV Cache pooling, xLLM architecture | cpp, llm, ai |
| [[entities/cpp/cpp-recsys-optimization]] | C++ for recommendation training: RecIS, Four Walls (Python/CPU/Memory/Compute), GPU HashTable | cpp, recsys, performance |
| [[entities/cpp/cpp-templates]] | C++ Templates: metaprogramming, specialization, SFINAE, CRTP, variadic templates, fold expressions | cpp, templates, metaprogramming |

## Sources

| Source | Description | Date |
|--------|-------------|------|
| [[sources/pdf-cpp-ai-inference]] | AI/ML inference: Mooncake, RTP-LLM, DeepSeek, LazyLLM, FlagScale, on-device LLM, RecIS | 2025-12 |
| [[sources/pdf-cpp-safety-standards]] | C++ safety & standards: Bjarne@40, Michael AI stack, David AI code risks | 2025-12 |
| [[sources/pdf-cpp-compiler-toolchain]] | Compiler/toolchain: MLIR fuzzing, RISC-V AI compiler, FlagOS compiler, heterogeneous architecture | 2025-12 |
| [[sources/pdf-cpp-perf-engineering]] | Performance engineering: kernel bypass, Bcache Btree, distributed caching, RDMA transfer, crash diagnosis | 2025-12 |
| [[sources/pdf-cpp-engineering-practices]] | Engineering practices: AI coding (Baidu/Meituan), testing, maturity model, Xiaomi Vela, CLI tools, object lifetime, robotics build | 2025-12 |
| [[sources/pdf-cpp-templates]] | C++ Templates 2nd Ed: Vandevoorde, Josuttis, Gregor — metaprogramming, SFINAE, CRTP, specialization | 2017 |
| [[sources/pdf-cpp-nginx-module]] | Nginx module dev with C++11 + Boost: Luó Jiànfēng — module architecture, HTTP/stream, Boost integration | 2015 |
| [[sources/pdf-crypto-books]] | OpenSSL Cookbook + Illustrated Cryptography 3rd Ed: key management, TLS testing, crypto basics | 2024 |

## Cross-References

- [[design-patterns-index]] — RAII and smart pointers encode creational patterns in C++; modern C++ idioms embody SOLID
- [[interview-index]] — Modern C++ features (move semantics, constexpr, concurrency) are key interview topics
- [[sys-prog-index]] — [[entities/cpp]] and C/C++ language fundamentals underpin all system programming work
- [[entities/ai-mlir-compilation]] — AI compilation and MLIR infrastructure for model optimization
- [[entities/risc-v-ai-ecosystem]] — RISC-V open ISA + AI software ecosystem
- [[entities/kernel-bypass-dpdk]] — Kernel bypass techniques for high-speed networking
