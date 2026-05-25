---
type: entity
tags: [cpp, cpp17, performance, cache-locality, string-view, pmr]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Performance Optimization

## 定义

C++17 性能優化關注數據訪問模式和內存管理。核心問題：**數據在哪裡，你多頻繁接觸它？**

| 場景 | 工具 | 為什麼 |
|------|------|--------|
| 循環中多次分配 | `reserve()` | 避免重複重分配 |
| 傳遞字符串 | `std::string_view` | 零拷貝，無分配 |
| 臨時分配 | SSO (Small String Optimization) | 短字符串棧存儲 |
| 自定義內存池 | `std::pmr` | 減少分配開銷 |
| 熱路徑小數據 | Inline / `[[gnu::always_inline]]` | 避免函數調用開銷 |
| 減少拷貝 | 移動語義 | `std::move` 對 rvalue |

## 關鍵要點

- **Cache Locality**: 連續訪問 > 跳躍訪問；AoS vs SoA
- **string_view**: 非擁有視圖（指針 + 長度），生命周期依附原字符串
- **reserve()**: 預分配避免重分配
- **SSO**: 大多數實現將 <=15 字符存儲在對象內部
- **std::pmr**: `monotonic_buffer_resource` 池分配

## 代碼示例

```cpp
// SoA (Structure of Arrays) — 更好的緩存利用
struct Points {
    std::vector<double> x, y, z;
};
// 所有 x 緊密循環 — 緩存友好

// string_view: 零拷貝字符串視圖
void parse(std::string_view sv);  // 接受 string 或 char*
std::string path = "/usr/local/bin";
std::string_view sv = path;  // 共享數據，無拷貝
std::string_view sub = sv.substr(5, 10);  // 零拷貝

// reserve: 避免重分配
std::vector<int> v;
v.reserve(1000);  // 預分配
for (int i = 0; i < 1000; ++i) {
    v.push_back(i);  // 無重分配
}

// std::pmr: monotonic buffer
std::pmr::monotonic_buffer_resource pool{1024};  // 1KB from stack
std::pmr::vector<int> vec{&pool};
vec.push_back(1);  // pool 按需增長
```

## 常見陷阱

- **不必要的字符串拷貝**: `void process(std::string s)` → `void process(std::string_view sv)`
- **Vector of Pointers**: `std::vector<std::unique_ptr<Widget>>` 緩存不友好
- **Premature optimization**: 先 profile，再優化瓶頸

## 相關概念

- [[entities/cpp/cpp-stl-containers]] - STL 容器選擇（vector vs list）
- [[entities/cpp/cpp-stl-string]] - string 實現與 SSO
- [[entities/cpp/cpp-perf-optimization]] - CPU cache、SIMD、profiling 工具
- [[entities/cpp/modern/c17-01-ownership]] - 移動語義避免拷貝
- [[entities/cpp/modern/c17-02-resource]] - Smart Pointers 的性能考慮
- [[entities/cpp/modern/m10-performance]] - Master: Performance

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-10-performance: cache locality, string_view, reserve, PMR
