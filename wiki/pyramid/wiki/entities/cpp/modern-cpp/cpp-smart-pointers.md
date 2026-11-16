---
type: entity
tags: [cpp11, cpp14, cpp17, smart-pointer, unique-ptr, shared-ptr, resource-management]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Smart Pointers

## Definition

Smart pointers are RAII wrappers for heap-allocated objects. C++11 introduced `std::unique_ptr`, `std::shared_ptr`, `std::weak_ptr`. `std::auto_ptr` was deprecated in C++11 and removed in C++17.

## Key Concepts

### std::unique_ptr (C++11)

Non-copyable, movable exclusive ownership. Zero overhead over raw pointer.

```c++
std::unique_ptr<Foo> p1{new Foo{}};
p1->bar();

// Transfer ownership
std::unique_ptr<Foo> p2 = std::move(p1);  // p2 owns Foo, p1 is empty

// Array specialization
std::unique_ptr<int[]> arr{new int[10]};
```

Custom deleter (type-included in unique_ptr's type):
```c++
auto del = [](FILE* f) { fclose(f); };
std::unique_ptr<FILE, decltype(del)> f{fopen("a.txt", "r"), del};
```

### std::make_unique (C++14)

Exception-safe creation — recommended over direct `new`:

```c++
// Pre C++14:
std::unique_ptr<int> p1{new int(1)};

// C++14+:
auto p2 = std::make_unique<int>(1);           // single object
auto p3 = std::make_unique<int[]>(10);         // array
auto p4 = std::make_unique<std::string>(10, 'x'); // args forwarded to ctor
```

`make_unique` provides exception-safety guarantee — no leak if constructor throws:
```c++
// DANGEROUS: leak if function_that_throws() throws after first new
foo(std::unique_ptr<T>{new T{}}, function_that_throws(), std::unique_ptr<T>{new T{}});

// SAFE: make_unique guarantees no leak
foo(std::make_unique<T>(), function_that_throws(), std::make_unique<T>());
```

### std::shared_ptr (C++11)

Reference-counted shared ownership. Thread-safe reference count, but not thread-safe access to managed object.

```c++
void foo(std::shared_ptr<T> t);
void bar(std::shared_ptr<T> t);

auto p1 = std::make_shared<T>();  // refcount = 1
foo(p1);                          // refcount = 2
bar(p1);                          // refcount = 3
// p1 destroyed: refcount = 2
// bar returns: refcount = 1
```

Control block contains: reference count, weak count, deleter, allocator.

### std::make_shared (C++11)

More efficient than `shared_ptr<T>(new T)` — one allocation for object + control block:

```c++
// Two allocations:
std::shared_ptr<T> p1{new T{}};  // 1. T allocation  2. control block

// One allocation:
auto p2 = std::make_shared<T>();  // Single combined allocation
```

### std::make_shared supports arrays (C++20)

```c++
auto p = std::make_shared<int[]>(5);    // shared_ptr<int[]>
auto q = std::make_shared<int[5]>();     // shared_ptr<int[5]>
```

### std::weak_ptr (C++11)

Non-owning reference to `shared_ptr` — prevents cycles:

```c++
std::shared_ptr<Node> sp = std::make_shared<Node>();
std::weak_ptr<Node> wp = sp;

if (auto locked = wp.lock()) {
  // Use locked shared_ptr safely
}
sp.reset();  // Node destroyed even though wp exists
```

**Cycle example**: `parent -> child -> parent` — both use `shared_ptr` → neither destroyed. Solution: one side uses `weak_ptr`.

## Comparison

| Feature | unique_ptr | shared_ptr | weak_ptr |
|---------|-----------|-----------|---------|
| Ownership | Exclusive | Shared | Non-owning |
| Overhead | Zero (one pointer) | Atomic refcount | One pointer |
| Thread-safe refcount | N/A | Yes | Yes |
| Can form cycles | No | Yes (use weak_ptr) | N/A |

## Related Concepts

- [[cpp-move-semantics]] — unique_ptr is move-only
- [[raii]] — smart pointers are the canonical RAII resource management example
- [[cpp-concurrency]] — shared_ptr thread-safety (refcount safe, object not)
