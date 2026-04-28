---
title: 内存池设计
date: 2024-01-20 20:30:00
tags:
    - cpp
    - memory-pool
---

## 1. 内存池简介

### 1.1 为什么需要内存池

内存池（Memory Pool）是一种预分配和管理内存的技术，旨在解决以下问题：

- **频繁的小内存分配释放**：每次 `new`/`delete` 调用都需要系统调用，开销巨大
- **内存碎片化**：大量的小对象分配和释放会导致堆碎片化
- **内存分配不确定性**：实时系统需要确定性的内存分配时间

```cpp
// 传统方式的性能问题
void process() {
    for (int i = 0; i < 100000; ++i) {
        // 每次分配都涉及系统调用
        auto* ptr = new SmallObject();
        // ... 使用 ptr
        delete ptr;  // 每次释放也涉及系统调用
    }
}

// 使用内存池的方式
void process_with_pool(MemoryPool& pool) {
    for (int i = 0; i < 100000; ++i) {
        auto* ptr = pool.allocate<SmallObject>();
        // ... 使用 ptr
        pool.deallocate(ptr);
    }
}
```

### 1.2 减少内存碎片

内存碎片分为两种：

- **外部碎片**：空闲内存被分割成不连续的小块，无法满足大内存分配
- **内部碎片**：分配的实际内存大于请求的内存，造成浪费

内存池通过预先分配大块内存，然后在内部进行分配，可以有效控制碎片。

```cpp
// 固定大小内存池示意图
/*
┌─────────────────────────────────────┐
│           Memory Pool               │
│  ┌─────┬─────┬─────┬─────┬─────┐   │
│  │ obj │ obj │ obj │ obj │ ... │   │
│  └─────┴─────┴─────┴─────┴─────┘   │
│   ↑                           ↑    │
│   └────── 空闲链表管理 ────────┘    │
└─────────────────────────────────────┘
*/
```

### 1.3 提高分配效率

内存池的分配效率远高于传统的堆分配：

| 操作 | 传统 new/delete | 内存池 |
|------|-----------------|--------|
| 系统调用 | 每次都需要 | 仅初始时需要 |
| 分配复杂度 | O(log n) 或更差 | O(1) |
| 缓存友好性 | 差 | 好（连续分配） |

## 2. 固定大小内存池

### 2.1 空闲链表实现

空闲链表是最简单的内存池实现方式，每个空闲块都包含一个指向下一个空闲块的指针。

```cpp
class FixedSizePool {
private:
    struct FreeNode {
        FreeNode* next;
    };

    FreeNode* free_list_ = nullptr;
    void* memory_block_ = nullptr;
    size_t block_size_;
    size_t object_size_;

public:
    FixedSizePool(size_t object_size, size_t pool_size) {
        object_size_ = std::max(object_size, sizeof(FreeNode*));
        block_size_ = object_size_ * pool_size;

        // 一次性分配整块内存
        memory_block_ = std::malloc(block_size_);

        // 初始化空闲链表
        free_list_ = static_cast<FreeNode*>(memory_block_);
        FreeNode* current = free_list_;
        for (size_t i = 1; i < pool_size; ++i) {
            current->next = reinterpret_cast<FreeNode*>(
                reinterpret_cast<char*>(current) + object_size_);
            current = current->next;
        }
        current->next = nullptr;
    }

    ~FixedSizePool() {
        std::free(memory_block_);
    }

    void* allocate() {
        if (!free_list_) {
            return nullptr;  // 池已耗尽
        }
        FreeNode* node = free_list_;
        free_list_ = free_list_->next;
        return node;
    }

    void deallocate(void* ptr) {
        FreeNode* node = static_cast<FreeNode*>(ptr);
        node->next = free_list_;
        free_list_ = node;
    }
};
```

### 2.2 对象池模式

对象池模式是对空闲链表的高层封装，提供了更面向对象的接口。

```cpp
template<typename T>
class ObjectPool {
private:
    struct Node {
        Node* next;
        char data[sizeof(T)];
    };

    Node* free_list_ = nullptr;
    size_t pool_size_;

public:
    ObjectPool(size_t initial_size = 128) : pool_size_(initial_size) {
        expand_pool(initial_size);
    }

    ~ObjectPool() {
        while (free_list_) {
            Node* node = free_list_;
            free_list_ = free_list_->next;
            std::free(node);
        }
    }

    template<typename... Args>
    T* acquire(Args&&... args) {
        if (!free_list_) {
            expand_pool(pool_size_);  // 扩容
        }

        Node* node = free_list_;
        free_list_ = free_list_->next;

        // 在预分配的内存上构造对象
        return new (node->data) T(std::forward<Args>(args)...);
    }

    void release(T* obj) {
        obj->~T();  // 调用析构函数

        Node* node = reinterpret_cast<Node*>(obj);
        node->next = free_list_;
        free_list_ = node;
    }

private:
    void expand_pool(size_t count) {
        for (size_t i = 0; i < count; ++i) {
            Node* node = static_cast<Node*>(std::malloc(sizeof(Node)));
            node->next = free_list_;
            free_list_ = node;
        }
        pool_size_ = count;
    }
};
```

### 2.3 简单实现示例

一个简单但实用的固定大小内存池实现：

```cpp
#include <cstddef>
#include <cstdlib>
#include <new>

template<typename T, size_t BlockSize = 4096>
class SimplePool {
    union Slot {
        char data[sizeof(T)];
        Slot* next;
    };

    Slot* free_list_ = nullptr;
    Slot* current_block_ = nullptr;
    Slot** current_block_end_ = nullptr;

public:
    SimplePool() = default;
    ~SimplePool() {
        while (current_block_) {
            Slot* block = current_block_;
            current_block_ = *reinterpret_cast<Slot**>(block);
            std::free(block);
        }
    }

    T* allocate() {
        if (!free_list_) {
            allocate_block();
        }

        Slot* slot = free_list_;
        free_list_ = free_list_->next;
        return new (slot) T;
    }

    void deallocate(T* ptr) {
        ptr->~T();
        Slot* slot = reinterpret_cast<Slot*>(ptr);
        slot->next = free_list_;
        free_list_ = slot;
    }

private:
    void allocate_block() {
        // 分配新的内存块
        char* block = static_cast<char*>(std::malloc(BlockSize));
        *reinterpret_cast<Slot**>(block) = current_block_;
        current_block_ = reinterpret_cast<Slot*>(block);

        // 计算可用 slot 的起始位置
        Slot* slots = reinterpret_cast<Slot*>(block + sizeof(Slot*));
        current_block_end_ = reinterpret_cast<Slot**>(block + BlockSize);

        // 将新分配的 slots 加入空闲链表
        free_list_ = slots;
        Slot* current = slots;
        while (current + 1 < reinterpret_cast<Slot*>(current_block_end_)) {
            current->next = current + 1;
            current = current->next;
        }
        current->next = nullptr;
    }
};
```

## 3. 可变大小内存池

### 3.1 伙伴系统

伙伴系统（Buddy System）是一种经典的可变大小内存分配算法，它将内存按 2 的幂次方进行划分。

```cpp
class BuddyAllocator {
private:
    static const size_t MIN_ORDER = 5;  // 32 bytes
    static const size_t MAX_ORDER = 20; // 1 MB
    static const size_t POOL_SIZE = 1 << MAX_ORDER;

    struct FreeNode {
        FreeNode* next;
    };

    FreeNode* free_lists_[MAX_ORDER - MIN_ORDER + 1];
    void* memory_pool_;

    size_t order(size_t size) {
        size_t order = MIN_ORDER;
        while ((1 << order) < size) {
            ++order;
        }
        return order;
    }

public:
    BuddyAllocator() {
        memory_pool_ = std::malloc(POOL_SIZE);
        for (int i = 0; i <= MAX_ORDER - MIN_ORDER; ++i) {
            free_lists_[i] = nullptr;
        }
    }

    ~BuddyAllocator() {
        std::free(memory_pool_);
    }

    void* allocate(size_t size) {
        size_t req_order = order(size);
        size_t alloc_order = req_order;

        // 寻找合适的阶
        while (alloc_order <= MAX_ORDER - MIN_ORDER &&
               free_lists_[alloc_order] == nullptr) {
            ++alloc_order;
        }

        if (alloc_order > MAX_ORDER - MIN_ORDER) {
            return nullptr;  // 分配失败
        }

        // 移除空闲块
        FreeNode* block = free_lists_[alloc_order];
        free_lists_[alloc_order] = block->next;

        // 分割成更小的块
        while (alloc_order > req_order) {
            --alloc_order;
            size_t block_size = 1 << (alloc_order + MIN_ORDER);
            FreeNode* buddy = reinterpret_cast<FreeNode*>(
                reinterpret_cast<char*>(block) + block_size);
            buddy->next = free_lists_[alloc_order];
            free_lists_[alloc_order] = buddy;
        }

        return block;
    }

    void deallocate(void* ptr, size_t size) {
        size_t req_order = order(size);
        FreeNode* block = static_cast<FreeNode*>(ptr);

        // 合并伙伴块
        while (req_order < MAX_ORDER - MIN_ORDER) {
            size_t block_size = 1 << (req_order + MIN_ORDER);
            uintptr_t address = reinterpret_cast<uintptr_t>(ptr);
            uintptr_t buddy_address = address ^ block_size;

            // 检查伙伴是否空闲
            FreeNode** list = &free_lists_[req_order];
            FreeNode** prev = nullptr;

            for (FreeNode* current = *list; current; current = current->next) {
                if (reinterpret_cast<uintptr_t>(current) == buddy_address) {
                    // 找到伙伴，合并
                    if (prev) {
                        prev = current->next;
                    } else {
                        *list = current->next;
                    }

                    ptr = std::min(ptr, static_cast<void*>(current));
                    ++req_order;
                    block = static_cast<FreeNode*>(ptr);
                    break;
                }
                prev = &current->next;
            }

            if (prev == nullptr) {
                break;  // 伙伴忙，无法合并
            }
        }

        // 插入到空闲链表
        block->next = free_lists_[req_order];
        free_lists_[req_order] = block;
    }
};
```

### 3.2 Slab 分配器

Slab 分配器是介于对象池和完整内存分配器之间的方案，特别适合分配大量相同大小的对象。

```cpp
class SlabAllocator {
private:
    struct Slab {
        Slab* next;
        char* free_ptr;
        char* end;
    };

    size_t object_size_;
    Slab* partial_slab_ = nullptr;
    Slab* full_slab_ = nullptr;
    Slab* empty_slab_ = nullptr;

    Slab* allocate_slab() {
        const size_t SLAB_SIZE = 4096;
        Slab* slab = static_cast<Slab*>(std::malloc(SLAB_SIZE));
        slab->next = nullptr;
        slab->free_ptr = reinterpret_cast<char*>(slab + 1);
        slab->end = reinterpret_cast<char*>(slab) + SLAB_SIZE;
        return slab;
    }

public:
    SlabAllocator(size_t object_size) : object_size_(object_size) {}

    ~SlabAllocator() {
        Slab* slab = partial_slab_;
        while (slab) {
            Slab* next = slab->next;
            std::free(slab);
            slab = next;
        }
        slab = full_slab_;
        while (slab) {
            Slab* next = slab->next;
            std::free(slab);
            slab = next;
        }
        slab = empty_slab_;
        while (slab) {
            Slab* next = slab->next;
            std::free(slab);
            slab = next;
        }
    }

    void* allocate() {
        // 优先从 partial slab 分配
        if (partial_slab_) {
            void* ptr = partial_slab_->free_ptr;
            partial_slab_->free_ptr += object_size_;

            if (partial_slab_->free_ptr >= partial_slab_->end) {
                // slab 已满，移到 full 列表
                Slab* slab = partial_slab_;
                partial_slab_ = partial_slab_->next;
                slab->next = full_slab_;
                full_slab_ = slab;
            }
            return ptr;
        }

        // 从 empty slab 分配
        if (empty_slab_) {
            partial_slab_ = empty_slab_;
            empty_slab_ = empty_slab_->next;
            partial_slab_->next = nullptr;
            return allocate();  // 重新分配
        }

        // 创建新的 slab
        empty_slab_ = allocate_slab();
        return allocate();
    }

    void deallocate(void* ptr, Slab* slab) {
        // 简单实现：将 slab 标记为非满
        if (slab == full_slab_) {
            // 从 full 列表移到 partial 列表
            // 实际实现需要找到并移除 slab
        }
    }
};
```

### 3.3 Linux 内核中的 slab

Linux 内核使用 slab 分配器来管理对象缓存，其核心思想包括：

- **缓存着色**（Cache Coloring）：将对象在 CPU 缓存行上错开，减少缓存冲突
- **持久化对象**：对象不被释放，只是归还到缓存
- **热对象**：保持对象在 CPU 缓存中

```c
// Linux 内核 slab API 概念示例
struct kmem_cache* obj_cache;

// 创建缓存
obj_cache = kmem_cache_create(
    "my_object",           // 名称
    sizeof(struct my_obj), // 对象大小
    alignof(struct my_obj), // 对齐要求
    SLAB_HWCACHE_ALIGN,    // 标志：CPU 缓存对齐
    NULL                   // 构造函数
);

// 从缓存分配
struct my_obj* obj = kmem_cache_alloc(obj_cache, GFP_KERNEL);

// 释放到缓存
kmem_cache_free(obj_cache, obj);

// 销毁缓存
kmem_cache_destroy(obj_cache);
```

## 4. 内存池的应用场景

### 4.1 高性能服务器

在高性能服务器中，内存池用于：

- **高频请求处理**：Web 服务器、游戏服务器每秒处理数万请求
- **连接池管理**：数据库连接、网络连接的重用
- **日志缓冲**：高并发写入日志的缓冲区

```cpp
// HTTP 服务器中的请求对象池
class HttpRequestPool {
    ObjectPool<HttpRequest> pool_;
public:
    HttpRequest* acquire_request() {
        return pool_.acquire();
    }

    void release_request(HttpRequest* req) {
        req->reset();  // 重置状态
        pool_.release(req);
    }
};
```

### 4.2 游戏开发

游戏开发中的内存池应用：

- **实体管理**：游戏中的子弹、粒子、特效等高频创建销毁的对象
- **纹理和模型数据**：大型资源的缓存管理
- **帧内存分配**：每帧的临时分配，帧结束时统一释放

```cpp
// 游戏粒子系统内存池
class ParticlePool {
    struct Particle {
        Vector3 position;
        Vector3 velocity;
        float lifetime;
        bool active;
    };

    ObjectPool<Particle> pool_;
    static const size_t MAX_PARTICLES = 10000;

public:
    Particle* emit(const Vector3& pos, const Vector3& vel) {
        Particle* p = pool_.acquire();
        p->position = pos;
        p->velocity = vel;
        p->lifetime = 2.0f;
        p->active = true;
        return p;
    }

    void update(float dt) {
        // 每帧更新所有活跃粒子
        // 死去的粒子归还池中
    }
};
```

### 4.3 嵌入式系统

嵌入式系统的内存池特点：

- **确定性分配**：实时系统的内存分配必须可预测
- **资源受限**：内存有限，必须避免碎片
- **无垃圾回收**：嵌入式环境通常没有 GC

```cpp
// 嵌入式实时系统的固定内存池
template<typename T, size_t PoolSize>
class RTMemoryPool {
    static_assert((PoolSize & (PoolSize - 1)) == 0,
                  "PoolSize must be power of 2");

    T* pool_[PoolSize];
    size_t free_count_ = PoolSize;

public:
    RTMemoryPool() {
        for (size_t i = 0; i < PoolSize; ++i) {
            pool_[i] = nullptr;
        }
    }

    // O(1) 时间复杂度的分配
    T* allocate() {
        if (free_count_ == 0) {
            return nullptr;
        }
        --free_count_;
        return pool_[free_count_];
    }

    // O(1) 时间复杂度的释放
    void deallocate(T* obj) {
        pool_[free_count_] = obj;
        ++free_count_;
    }

    size_t available() const { return free_count_; }
};
```

## 5. C++ 内存池实现

### 5.1 简单内存池类

一个完整的固定大小内存池实现：

```cpp
#include <cstddef>
#include <cstdlib>
#include <memory>
#include <stdexcept>

template<typename T>
class MemoryPool {
public:
    MemoryPool(size_t initial_capacity = 128) {
        expand_capacity(initial_capacity);
    }

    ~MemoryPool() {
        while (blocks_) {
            Block* block = blocks_;
            blocks_ = blocks_->next;
            std::free(block);
        }
    }

    // 分配一个对象
    template<typename... Args>
    T* allocate(Args&&... args) {
        if (!free_list_) {
            expand_capacity(capacity_);
        }

        T* obj = free_list_;
        free_list_ = free_list_->next;

        try {
            new (obj) T(std::forward<Args>(args)...);
        } catch (...) {
            // 构造失败，归还内存
            reinterpret_cast<FreeNode*>(obj)->next = free_list_;
            free_list_ = reinterpret_cast<FreeNode*>(obj);
            throw;
        }

        ++allocated_;
        return obj;
    }

    // 释放一个对象
    void deallocate(T* obj) {
        obj->~T();
        reinterpret_cast<FreeNode*>(obj)->next = free_list_;
        free_list_ = reinterpret_cast<FreeNode*>(obj);
        --allocated_;
    }

    size_t allocated() const { return allocated_; }
    size_t capacity() const { return capacity_; }

private:
    union FreeNode {
        FreeNode* next;
        char data[sizeof(T)];
    };

    struct Block {
        Block* next;
    };

    FreeNode* free_list_ = nullptr;
    Block* blocks_ = nullptr;
    size_t capacity_ = 0;
    size_t allocated_ = 0;

    void expand_capacity(size_t new_capacity) {
        Block* block = static_cast<Block*>(std::malloc(
            sizeof(Block) + new_capacity * sizeof(T)));

        if (!block) {
            throw std::bad_alloc();
        }

        block->next = blocks_;
        blocks_ = block;

        // 添加到空闲链表
        FreeNode* node = reinterpret_cast<FreeNode*>(block + 1);
        free_list_ = node;

        for (size_t i = 1; i < new_capacity; ++i) {
            node->next = reinterpret_cast<FreeNode*>(
                reinterpret_cast<char*>(node) + sizeof(T));
            node = node->next;
        }
        node->next = nullptr;

        capacity_ += new_capacity;
    }
};
```

### 5.2 对象池实现

支持对象构造和析构的通用对象池：

```cpp
#include <functional>
#include <queue>
#include <mutex>

template<typename T>
class ObjectPool {
public:
    using Constructor = std::function<void(T*)>;
    using Destructor = std::function<void(T*)>;

    ObjectPool(size_t initial_size = 64,
               Constructor constructor = nullptr,
               Destructor destructor = nullptr)
        : constructor_(constructor), destructor_(destructor) {
        for (size_t i = 0; i < initial_size; ++i) {
            pool_.push(new T());
        }
    }

    ~ObjectPool() {
        while (!pool_.empty()) {
            delete pool_.front();
            pool_.pop();
        }
    }

    std::shared_ptr<T> acquire() {
        std::lock_guard<std::mutex> lock(mutex_);

        if (pool_.empty()) {
            pool_.push(new T());
        }

        T* obj = pool_.front();
        pool_.pop();

        return std::shared_ptr<T>(obj, [this](T* p) {
            std::lock_guard<std::mutex> lock(mutex_);
            if (destructor_) {
                destructor_(p);
            }
            pool_.push(p);
        });
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return pool_.size();
    }

private:
    std::queue<T*> pool_;
    std::mutex mutex_;
    Constructor constructor_;
    Destructor destructor_;
};
```

### 5.3 线程安全问题

在多线程环境中使用内存池需要考虑线程安全：

```cpp
#include <mutex>
#include <atomic>

template<typename T>
class ThreadSafePool {
private:
    struct FreeNode {
        FreeNode* next;
    };

    FreeNode* free_list_ = nullptr;
    std::atomic<size_t> free_count_{0};
    std::mutex mutex_;

    void expand(size_t count) {
        for (size_t i = 0; i < count; ++i) {
            FreeNode* node = static_cast<FreeNode*>(std::malloc(sizeof(T)));
            node->next = free_list_;
            free_list_ = node;
            ++free_count_;
        }
    }

public:
    ThreadSafePool(size_t initial_size = 128) {
        expand(initial_size);
    }

    T* allocate() {
        // 快速路径：无锁
        FreeNode* node = free_list_;
        if (!node || !free_list_.load(std::memory_order_relaxed)) {
            std::lock_guard<std::mutex> lock(mutex_);
            node = free_list_;
            if (!node) {
                expand(128);
                node = free_list_;
            }
            free_list_ = free_list_.load(std::memory_order_relaxed);
        }

        free_list_ = node->next;
        --free_count_;

        return new (node) T;
    }

    void deallocate(T* obj) {
        obj->~T();
        FreeNode* node = static_cast<FreeNode*>(obj);
        node->next = free_list_;
        free_list_ = node;
        ++free_count_;
    }

    size_t available() const {
        return free_count_.load(std::memory_order_relaxed);
    }
};

// 使用示例
ThreadSafePool<Connection> connection_pool;

void handle_request() {
    Connection* conn = connection_pool.allocate();
    // 使用连接...
    connection_pool.deallocate(conn);
}
```

## 总结

内存池是高性能内存管理的关键技术：

- **固定大小内存池**：实现简单，适用于对象大小固定的场景
- **可变大小内存池**：灵活性更高，但实现更复杂
- **对象池**：封装了构造和析构逻辑，使用更方便
- **线程安全**：多线程环境需要额外的同步机制

选择合适的内存池策略需要考虑：
- 对象的生命周期和大小
- 分配和释放的频率
- 对内存碎片的要求
- 实时性和确定性的需求
