---
type: entity
tags: [cpp, stl, allocators]
created: 2026-05-21
sources: [sources/pdf-cpp-effective-stl]
---

# STL Allocators

## 定义

分配器是 STL 中负责封装内存分配和释放的抽象机制。容器通过分配器获取存储元素所需的内存空间。

## 关键要点

### 标准 Allocator 接口

```cpp
template<typename T>
class Allocator {
public:
    using value_type = T;
    using pointer = T*;
    using const_pointer = const T*;
    using reference = T&;
    using const_reference = const T&;
    using size_type = std::size_t;
    using difference_type = std::ptrdiff_t;

    pointer allocate(size_type n);           // 分配 n * sizeof(T) 字节
    void deallocate(pointer p, size_type n); // 释放
    void construct(pointer p, const T& val); // 构造对象 (C++11 前)
    void destroy(pointer p);                 // 析构对象 (C++11 前)
};
```

### C++11 后的变化

- `construct/destroy` 被废弃，由 `std::make_shared`/`std::allocate_shared` 替代
- `allocator_traits` 提供默认实现
- 状态化分配器得到更好的支持

### 状态化分配器

分配器可以保存状态，实现内存池、自定义策略等：

```cpp
template<typename T>
class PoolAllocator {
    MemoryPool<> pool_;  // 私有内存池
public:
    T* allocate(std::size_t n) {
        return static_cast<T*>(pool_.allocate(n * sizeof(T)));
    }
    void deallocate(T* p, std::size_t n) {
        pool_.deallocate(p, n * sizeof(T));
    }
};
```

### 分配器特质 (allocator_traits)

```cpp
template<typename Alloc>
struct allocator_traits {
    using allocator_type = Alloc;
    using pointer = typename Alloc::pointer;

    static pointer allocate(Alloc& a, size_type n);
    static void deallocate(Alloc& a, pointer p, size_type n);
    // ... 其他默认实现
};
```

### 自定义分配器的设计考虑

1. **一致性** — 同一个分配器实例应对所有类型一致
2. **有状态 vs 无状态** — 有状态分配器需注意拷贝语义
3. **rebind** — 用于在内部容器中分配不同类型
4. **propagate_on_container_move_assignment** — 移动时是否移动分配器

## Effective STL 要点 (Items 44-50)

- Item 44: 自定义分配器的通用指导原则
- Item 45: 用 allocator_traits 替代 allocator 成员函数
- Item 46: 不要在分配器中实现非标准功能
- Item 47: 优先使用分配器而非 new/delete
- Item 48: 用 is_standard_layout 简化特化检测
- Item 49: 理解 unordered_* 容器的哈希函数要求
- Item 50: 用 shared_ptr 管理共享资源

## 相关概念
- [[entities/cpp/cpp-stl-containers]] — 容器使用分配器获取内存
- [[entities/cpp/cpp-stl-string]] — string 通过分配器管理字符存储
- [[entities/cpp/cpp-stl-algorithms]] — 算法操作容器内存
- [[entities/cpp/smart-pointers]] — 智能指针也使用分配器
- [[sources/bookmark-stl-source-analysis]] — SGI STL 3.0 源码分析，深入剖析配置器实现
