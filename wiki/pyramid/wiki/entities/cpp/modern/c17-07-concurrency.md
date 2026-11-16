---
type: entity
tags: [cpp, cpp17, concurrency, threads, atomics, mutex]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Concurrency

## 定义

C++17 提供線程通信和數據競爭預防的核心原語。核心問題：**線程如何通信，如何防止數據競爭？**

| 需求 | 工具 | C++ 版本 |
|------|------|----------|
| 後台運行任務 | `std::async` | C++11 |
| 多個共享讀者 | `std::shared_mutex` | C++17 |
| 保護共享數據 | `std::mutex` | C++11 |
| 多 mutex 鎖（避免死鎖） | `std::lock` / `std::scoped_lock` | C++17 |
| 線程間信號 | `std::condition_variable` | C++11 |
| 無鎖計數器 | `std::atomic<T>` | C++11 |
| 緩存線衝突 | `std::hardware_destructive_interference_size` | C++17 |

> **注意**: `std::jthread` (自動 join) 是 C++20。C++17 使用 `std::thread` 並顯式 `join()` 或 `detach()`。

## 關鍵要點

- **std::thread**: 始終在銷毀前 `join()` 或 `detach()`，否則 `std::terminate`
- **lock_guard**: RAII 模式，構造時獲取，析構時釋放
- **std::scoped_lock**: C++17，死鎖free 多 mutex 鎖
- **std::atomic**: 無鎖操作，需選擇 memory_order
- **std::shared_mutex**: C++17，讀者-寫者鎖（shared_lock vs unique_lock）

## 代碼示例

```cpp
// scoped_lock — C++17，死鎖free 多鎖
std::mutex m1, m2;
void safe_multiple() {
    std::scoped_lock lock(m1, m2);  // C++17
}

// atomic + memory ordering
std::atomic<int> data{0};
std::atomic<bool> ready{false};

void producer() {
    data.store(42, std::memory_order_release);
    ready.store(true, std::memory_order_release);
}

void consumer() {
    while (!ready.load(std::memory_order_acquire)) {
        std::this_thread::yield();
    }
    assert(data.load(std::memory_order_acquire) == 42);
}

// shared_mutex — C++17 讀者-寫者鎖
class RWList {
    mutable std::shared_mutex mtx_;
public:
    int read(size_t idx) const {
        std::shared_lock lock(mtx_);  // 多讀者可並發
        return data_.at(idx);
    }
    void write(size_t idx, int val) {
        std::unique_lock lock(mtx_);  // 獨占寫
        data_.at(idx) = val;
    }
};

// 避免 false sharing
struct PaddedCounter {
    std::atomic<int> a{0};
    char pad[std::hardware_destructive_interference_size - sizeof(int)];
};
```

## 常見陷阱

- **Joinable thread destructor**: 可連接線程銷毀時調用 `std::terminate`
- **數據競爭**: `int counter = 0; ++counter` → 應用 `std::atomic<int>`
- **死鎖**: 不同線程以不同順序獲取鎖 → 使用 `std::scoped_lock`
- **False sharing**: 獨立 atomic 在同一緩存線上

## 相關概念

- [[entities/cpp/concurrency]] - 現有並發 entity（std::thread、mutex、atomic、future）
- [[entities/cpp/cpp-memory-model]] - C++ Memory Model: Sequential Consistency、Acquire/Release
- [[entities/cpp/modern/c17-03-mutability]] - mutable 關鍵字在多線程中的安全性
- [[entities/cpp/modern/m07-concurrency]] - Master: Concurrency 思維模型

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-07-concurrency: std::thread, mutex, atomic, condition_variable, async
