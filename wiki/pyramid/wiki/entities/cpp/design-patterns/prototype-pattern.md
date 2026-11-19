---
type: entity
tags: [cpp, design-patterns, creational]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Prototype Pattern (原型模式)

## GoF 定义

通过复制已有对象来创建新对象，而无需让客户端依赖对象的具体类。

## C++ 实现

### 深拷贝（拷贝构造函数）

```cpp
struct Address {
    string street, city;
    int suite;
    Address(const string& s, const string& c, int s_) : street{s}, city{c}, suite{s_} {}
};

struct Contact {
    string name;
    Address* address;
    Contact(const string& n, Address* a) : name{n}, address{new Address{*a}} {}
    Contact(const Contact& other) : name{other.name}, address{new Address{*other.address}} {}
};
```

### 原型工厂

```cpp
struct EmployeeFactory {
    static Contact main, aux;
    static unique_ptr<Contact> NewMainOfficeEmployee(string name, int suite) {
        auto result = make_unique<Contact>(main);
        result->name = name;
        result->address->suite = suite;
        return result;
    }
};
```

### 序列化（Boost）

```cpp
auto clone = [](const Contact& c) {
    ostringstream oss;
    boost::archive::text_oarchive oa(oss);
    oa << c;
    istringstream iss(oss.str());
    Contact result;
    boost::archive::text_iarchive ia(iss);
    ia >> result;
    return result;
};
```

## 关键点

- 深拷贝 vs 浅拷贝：含指针成员时必须深拷贝
- `Cloneable<T>` 接口：`virtual T clone() const = 0`
- 序列化方式可复用来完成拷贝，但有额外性能开销

## 相关模式

- [[factory-pattern]]
- [[memento-pattern]]
