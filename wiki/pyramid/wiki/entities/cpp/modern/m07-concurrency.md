---
type: entity
tags: [cpp, master, concurrency, threads, atomics, deadlock, memory-model]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Concurrency Mental Model

## 核心問題

**線程如何通信？**

- **Shared State**: Mutexes (`std::mutex`) 或 Atomics (`std::atomic`)
- **Coordination**: Condition Variables (`std::condition_variable`) 或 Latches/Semaphores (C++20)
- **Tasks**: `std::async` 或 Coroutines (C++20)

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Data Race** | 兩個線程是否在沒有 Happens-Before 邊緣的情況下訪問內存？ |
| **Deadlock** | 是否線程 A 鎖了 Mutex A 然後 B，而另一個線程鎖了 B 然後 A？ |
| **False Sharing** | 獨立的 atomic 是否在同一緩存線上？ |
| **Live Lock** | 線程是否在無進展地空轉？ |

## Thinking Prompt

1. **我需要線程嗎？**
   - 短期任務？→ `std::async` 或線程池
   - 長期後台？→ `std::jthread`

2. **這是共享狀態嗎？**
   - 是？→ 用 `std::mutex` 保護
   - 小/原始類型？→ `std::atomic`

3. **鎖還是 Atomic？**
   - 需要多步驟的邏輯？→ Mutex（Atomic 僅適用於單一指令）
   - 簡單標誌/計數器？→ Atomic

## Trace Up / Down

- **Trace Up**: "計數器中隨機更新值" → `counter++` 是讀-修改-寫，不是原子性的。數據競爭 → `std::atomic<int>`

## Quick Reference

| 工具 | C++ 版本 | 使用時機 |
|------|----------|----------|
| **`std::jthread`** | C++20 | 標準線程（自動 join）|
| **`std::atomic`** | C++11 | 無鎖計數器/標誌 |
| **`std::mutex`** | C++11 | 鎖定臨界區 |
| **`std::shared_mutex`** | C++17 | 讀重負載 |
| **`std::latch`** | C++20 | 等待 N 個任務開始 |
| **`co_await`** | C++20 | 異步 I/O（需要庫）|

## 相關概念

- [[entities/cpp/concurrency]] - 現有 Concurrency entity
- [[entities/cpp/cpp-memory-model]] - C++ Memory Model
- [[entities/cpp/modern/c17-07-concurrency]] - C++17 Concurrency 技能
- [[entities/cpp/modern/m03-mutability]] - Master: Mutability（mutable + 線程安全）

## 來源詳情

- [[sources/cpp-modern-skills]] - m07-concurrency: std::thread, jthread, atomic, mutex, deadlock, race condition, memory model
