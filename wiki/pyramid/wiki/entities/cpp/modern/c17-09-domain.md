---
type: entity
tags: [cpp, cpp17, domain-driven-design, ddd, value-object, entity]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Domain-Driven Design (DDD)

## 定义

DDD 在 C++17 中使用類型系統明確表達領域概念。核心問題：**這個類型代表身份還是值？**

| 方面 | Value Object | Entity |
|------|--------------|--------|
| 身份 | 無（由屬性定義） | 有（固定身份） |
| 不變性 | 通常不可變 | 可變 |
| 相等性 | 按屬性值 | 按身份 |
| 示例 | `Money`、`Address`、`Point` | `User`、`Order`、`Account` |

## 關鍵要點

- **Value Object**: 不可變，按值相等，如 `Money`、`Point`
- **Entity**: 有身份，可變，相等性由身份確定
- **Aggregate**: 事務邊界，強制不變量
- **Repository**: 持久化抽象
- **Domain Event**: 解耦通知

## 代碼示例

```cpp
// Value Object: Money
struct Money {
    int64_t amount;
    std::string currency;
    Money(int64_t amt, std::string cur)
        : amount(amt), currency(std::move(cur)) {}
    Money operator+(const Money& rhs) const {
        if (currency != rhs.currency)
            throw std::domain_error("cannot add different currencies");
        return Money(amount + rhs.amount, currency);
    }
    bool operator==(const Money& rhs) const {
        return amount == rhs.amount && currency == rhs.currency;
    }
};

// Entity with Identity
class User {
    UserId id_;
    std::string name_;
public:
    User(UserId id, std::string name) : id_(std::move(id)), name_(std::move(name)) {}
    const UserId& id() const { return id_; }
    void rename(std::string new_name) { name_ = std::move(new_name); }
};
bool operator==(const User& a, const User& b) { return a.id() == b.id(); }

// Aggregate Root
class Order {
    OrderId id_;
    std::vector<OrderLine> lines_;
    OrderStatus status_;
public:
    void add_line(ProductId p, int qty, Money price) {
        if (status_ != OrderStatus::Draft)
            throw std::logic_error("cannot modify finalized order");
        lines_.emplace_back(std::move(p), qty, std::move(price));
    }
    void submit() {
        if (lines_.empty()) throw std::logic_error("empty order");
        status_ = OrderStatus::Submitted;
    }
};
```

## 常見陷阱

- **Entity vs Value Object 混淆**: `Address` 不應有 ID，它是 Value Object
- **Anemic Domain Model**: 只有數據無行為的類 → 應包含領域邏輯
- **對象切片**: 傳遞多態 Entity 時按值傳遞 → 應傳遞引用或指針

## 相關概念

- [[entities/cpp/modern/c17-05-type-driven]] - Type-Driven Design: newtypes、strong typing
- [[entities/cpp/modern/c17-04-templates]] - 模板支持 DDD 模式實現
- [[entities/cpp/modern/m09-domain]] - Master: Domain Modeling（Entity、Value Object、Aggregate）
- [[entities/cpp/modern/c17-09-domain]] - 自身交叉引用

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-09-domain: Value Objects, Entities, Aggregates, Domain Events
