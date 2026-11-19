---
type: entity
tags: [cpp, master, concurrency, threads, atomic]
created: 2026-05-27
sources: [github-modern-cpp-skills-m07]
---

# modern-m07-concurrency

## 定義

C++ 並發編程的核心思維模型：**線程如何通信？**

## 核心問題

**線程如何通信？**

- **Shared State**: Mutexes (`std::mutex`) 或 Atomics (`std::atomic`)
- **Coordination**: Condition Variables (`std::condition_variable`) 或 Latches/Semaphores (C++20)
- **Tasks**: `std::async` 或 Coroutines (C++20)

## 關鍵要點

- `std::jthread` (C++20)：自動 join，停止令牌支持協作取消
- `std::atomic`：無鎖計數器/標誌，讀-改-寫操作（如 `counter++`）需要特別注意
- `std::shared_mutex` (C++17)：讀者多/寫者少的 workload 首選
- `std::atomic` 只保證單一指令的原子性，`counter++` 是讀-改-寫，非原子
- False Sharing：獨立的 atomic 變量若位於同一緩存線，會相互干擾
- C++20 `co_await`：async I/O 需要庫支持

## 常見錯誤映射

| 問題 | 設計問題 |
|------|----------|
| Data Race | 兩個線程訪問內存是否沒有 Happens-Before 邊？ |
| Deadlock | 是否線程 A 鎖了 mutex B 再鎖 A，而另一線程鎖了 A 再鎖 B？ |
| False Sharing | 獨立的 atomic 是否位於同一緩存線？ |
| Live Lock | 線程是否在空轉而無實質進展？ |

## 思維框架

1. **Do I need a thread?** Short task → `std::async` 或 Thread Pool. Long background → `std::jthread`.
2. **Is it shared state?** Yes → Protect with `std::mutex`. Is it small/primitive? → `std::atomic`.
3. **Locks or Atomics?** Logic requiring multiple steps → Mutex. Simple flag/counter → Atomic.

## 相關概念

- [[entities/cpp/modern/modern-m03-mutability]] — `mutable` + 並發需要 mutex 保護
- [[entities/cpp/modern/modern-m12-lifecycle]] — 線程生命週期中的引用懸空問題
- [[entities/cpp/concurrency]] — C++ 並發完整技術棧
- [[entities/cpp/cpp-memory-model]] — C++ 內存模型的 happens-before 語義
- [[entities/cpp/modern/modern-m14-mental-model]] — 緩存線是 False Sharing 的根源
- [[entities/cpp/modern/modern-m06-error-handling]] — `std::terminate` 在並發出錯時被觸發

## Source

- [[sources/github-modern-cpp-skills-m07]]