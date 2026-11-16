---
type: entity
tags: [cpp, cpp17, lifecycle, raii, rule-of-5, rule-of-0]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Lifecycle & RAII

## 定义

C++ 生命周期是確定性的，RAII 將資源清理綁定到對象銷毀。核心問題：**這個對象何時創建，何時銷毀？**

## 關鍵概念

| 規則 | 描述 |
|------|------|
| **Rule of 0** | 偏好 default/delete 所有特殊成員函數 |
| **Rule of 5** | 管理原始資源時定義全部五個 |
| **Rule of 3** | C++11 之前的版本（無移動） |

## 關鍵要點

- **Static Initialization**: 零初始化 → 常量初始化 → 動態初始化（函數局部 static 線程安全）
- **Magic Statics**: C++11+ 函數局部 static 線程安全初始化
- **Constructor Types**: 委託構造函數、繼承構造函數 (C++11)
- **Virtual Destructor**: 多態類必須有虛析構函數
- **=default / =delete**: 顯式請求/禁止編譯器生成

## 代碼示例

```cpp
// Rule of Zero — C++17 偏好
class Widget {
    std::string name_;
    std::vector<int> data_;
public:
    Widget(std::string n, std::vector<int> d)
        : name_(std::move(n)), data_(std::move(d)) {}
    // 所有特殊成員隱式正確
};

// Rule of Five — 管理原始資源
class ManualResource {
    FILE* handle_ = nullptr;
public:
    explicit ManualResource(const char* path) : handle_(fopen(path, "r")) {}
    ~ManualResource() { if (handle_) fclose(handle_); }
    ManualResource(const ManualResource&) = delete;
    ManualResource& operator=(const ManualResource&) = delete;
    ManualResource(ManualResource&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }
    ManualResource& operator=(ManualResource&& other) noexcept {
        if (this != &other) {
            if (handle_) fclose(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }
};

// Scope Guard: Commit/Rollback Pattern
class FileTransaction {
    FILE* file_;
    bool committed_ = false;
public:
    FileTransaction(const char* path) : file_(fopen(path, "w")) {}
    void commit() { committed_ = true; }
    ~FileTransaction() {
        if (!committed_) { /* rollback */ }
        if (file_) fclose(file_);
    }
};

// Magic Statics — 線程安全單例
Widget& get_widget() {
    static Widget instance(42);  // 初始化一次，線程安全
    return instance;
}
```

## 常見陷阱

- **Constructor 拋出後部分構造**: 使用成員初始化列表 + RAII
- **返回 this from constructor**: 構造函數中 `instance = this` 危險
- **拷貝 mutex**: `std::mutex` 不可拷貝

## 相關概念

- [[entities/cpp/raii]] - 現有 RAII entity
- [[entities/cpp/modern/c17-01-ownership]] - 所有權與 RAII
- [[entities/cpp/modern/c17-02-resource]] - Smart Pointers 是 RAII 實現
- [[entities/cpp/modern/m12-lifecycle]] - Master: Lifecycle
- [[entities/cpp/modern/c17-12-lifecycle]] - 自身交叉引用

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-12-lifecycle: RAII, Rule of 5/0, constructor, destructor, static initialization
