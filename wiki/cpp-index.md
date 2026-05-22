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

## Cross-References

- [[design-patterns-index]] — RAII and smart pointers encode creational patterns in C++; modern C++ idioms embody SOLID
- [[interview-index]] — Modern C++ features (move semantics, constexpr, concurrency) are key interview topics
- [[sys-prog-index]] — [[entities/cpp]] and C/C++ language fundamentals underpin all system programming work
