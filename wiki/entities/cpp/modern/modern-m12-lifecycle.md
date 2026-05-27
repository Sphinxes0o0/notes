---
type: entity
tags: [cpp, master, lifecycle, raii, rule-of-5]
created: 2026-05-27
sources: [github-modern-cpp-skills-m12]
---

# modern-m12-lifecycle

## 定義

C++ 對象生命週期的核心思維模型：**這個對象何時死亡？**

## 核心問題

**何時死亡？**

- **Stack**: 到達 `}` 作用域末尾
- **Heap**: 當 `delete`（或智能指針釋放）發生
- **Static**: 程序退出時（反向初始化順序）

## 關鍵要點

- RAII：資源獲取即初始化，析構函數自動釋放資源
- Scope Guard：`std::scope_exit` (C++23) 確保清理回調一定執行
- Rule of 5：如果需要自定義拷貝/移動/析構，幾乎總是需要全部五個
- 靜態初始化順序災難：Meyers Singleton (`instance()` 局部靜態變量) 解決這個問題
- Lambda/線程捕獲局部引用是 Use After Free 的常見原因

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Resource Leak | 是否手動 `open()` 而沒有封裝類？ |
| Use After Free | 是否在 lambda/線程中捕獲了局部變量的引用？ |
| Static Fiasco | 靜態對象是否相互依賴？（用 Meyers Singleton） |

## 思維框架

1. **Does it have a destructor?** Yes → RAII. Good. No → Wrap it.
2. **Does it copy?** `FILE*` cannot copy. Delete copy constructor.
3. **Use after free?** Never capture reference to local in lambda/thread.

## 相關概念

- [[entities/cpp/modern/modern-m01-ownership]] — 所有權決定了誰負責析構
- [[entities/cpp/modern/modern-m07-concurrency]] — 線程中的引用捕獲是生命周期陷阱
- [[entities/cpp/modern/modern-m15-anti-pattern]] — `new`/`delete` 是生命周期問題的根源
- [[entities/cpp/raii]] — RAII 是生命周期的核心慣用法
- [[entities/cpp/cpp-object-lifetime]] — 對象生命周期的完整技術細節
- [[entities/cpp/modern/modern-m14-mental-model]] — 內存視圖幫助理解對象的存儲位置

## Source

- [[sources/github-modern-cpp-skills-m12]]