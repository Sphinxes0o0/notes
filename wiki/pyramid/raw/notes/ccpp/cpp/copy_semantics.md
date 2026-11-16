---
title: C++ 拷贝语义
date: 2024-01-20 10:00:00
tags:
    - cpp
    - copy-semantics
---

## 1. 浅拷贝 vs 深拷贝

### 1.1 默认拷贝构造函数的问题

C++ 为每个类提供默认的拷贝构造函数和拷贝赋值运算符，它们的行为是成员逐个拷贝（memberwise copy）。对于包含指针成员的类，这可能导致问题。

```cpp
class String {
public:
    String(const char* p) {
        len = strlen(p);
        str = new char[len + 1];
        strcpy(str, p);
    }

    ~String() {
        delete[] str;
    }

private:
    char* str;
    size_t len;
};
```

这个类使用默认的拷贝构造函数，当发生拷贝时：

```cpp
String s1("hello");
String s2 = s1;  // 默认拷贝：逐成员拷贝
```

默认拷贝构造函数只拷贝指针的值（地址），而不是指针指向的数据。

### 1.2 浅拷贝的陷阱

**浅拷贝**（Shallow Copy）只拷贝指针本身，不拷贝指针指向的数据。多个对象可能指向同一块内存，导致：

1. **重复释放**：多个对象析构时对同一块内存释放多次
2. **数据竞争**：一个对象修改数据影响另一个对象
3. **悬空指针**：一个对象析构后，另一个对象的指针指向已释放内存

```cpp
String s1("hello");
String s2 = s1;  // 浅拷贝：s1.str 和 s2.str 指向同一块内存

std::cout << s1.get_str() << std::endl;  // 正常
std::cout << s2.get_str() << std::endl;  // 正常

// 函数结束，s2 先析构，释放了 "hello" 所在的内存
// s1 析构时再次释放同一块内存 → 程序崩溃
```

### 1.3 深拷贝的实现

**深拷贝**（Deep Copy）不仅拷贝指针，还拷贝指针指向的数据。每个对象拥有独立的数据副本。

```cpp
class String {
public:
    String() : str(nullptr), len(0) {}

    String(const char* p) {
        len = strlen(p);
        str = new char[len + 1];
        strcpy(str, p);
    }

    // 拷贝构造函数 - 深拷贝
    String(const String& other) {
        len = other.len;
        str = new char[len + 1];
        strcpy(str, other.str);
    }

    // 拷贝赋值运算符 - 深拷贝
    String& operator=(const String& other) {
        if (this != &other) {  // 自我赋值检查
            delete[] str;
            len = other.len;
            str = new char[len + 1];
            strcpy(str, other.str);
        }
        return *this;
    }

    ~String() {
        delete[] str;
    }

    const char* get_str() const { return str; }

private:
    char* str;
    size_t len;
};
```

## 2. 拷贝构造与拷贝赋值

### 2.1 拷贝构造函数的定义

拷贝构造函数的签名是固定的：

```cpp
ClassName(const ClassName& other);
ClassName(const ClassName& other, Args...);  // 可带其他参数
```

**何时调用拷贝构造函数**：
- 对象作为参数以值传递时
- 对象作为返回值（有些情况会被优化）
- 用一个对象初始化另一个对象

```cpp
class Widget {
public:
    Widget(const Widget& w);  // 拷贝构造函数
};

Widget w1;
Widget w2(w1);        // 调用拷贝构造
Widget w3 = w1;       // 调用拷贝构造（这里是初始化，不是赋值）
```

### 2.2 拷贝赋值运算符 operator=

拷贝赋值运算符的签名也是固定的：

```cpp
ClassName& operator=(const ClassName& other);
```

**何时调用拷贝赋值运算符**：
- 对象已经被构造，需要用另一个对象赋值给它

```cpp
Widget w1;
Widget w2;
w2 = w1;  // 调用拷贝赋值运算符（w2 已经存在）
```

### 2.3 拷贝运算符的自我赋值检查

自我赋值（self-assignment）是指 `obj = obj` 这种情况。如果不处理，可能导致：

```cpp
String& operator=(const String& other) {
    // 错误的实现
    delete[] str;        // 释放了自己的内存
    len = other.len;
    str = new char[len + 1];  // other.str 也被删除了！
    strcpy(str, other.str);
    return *this;
}
```

正确的实现需要先检查自我赋值：

```cpp
String& operator=(const String& other) {
    if (this != &other) {  // 检查自我赋值
        delete[] str;
        len = other.len;
        str = new char[len + 1];
        strcpy(str, other.str);
    }
    return *this;
}
```

**现代 C++ 的替代方案**（更简洁）：

```cpp
String& operator=(const String& other) {
    String temp(other);    // 拷贝构造临时对象
    std::swap(str, temp.str);  // 交换指针
    std::swap(len, temp.len);
    return *this;
}
// 函数结束时，temp（持有旧数据）自动析构，释放旧内存
```

## 3. 移动构造与移动赋值

### 3.1 移动构造 vs 拷贝构造

**拷贝构造**：复制源对象的数据，源对象保持不变
**移动构造**："偷取"源对象的数据，源对象被置于有效但可析构的状态

```cpp
class String {
public:
    // 拷贝构造函数
    String(const String& other)
        : str(new char[other.len + 1]), len(other.len) {
        strcpy(str, other.str);
    }

    // 移动构造函数
    String(String&& other) noexcept
        : str(other.str), len(other.len) {
        other.str = nullptr;  // 源对象被掏空
        other.len = 0;
    }
};
```

**调用移动构造的场景**：
- 用右值初始化对象
- `std::move()` 转换左值为右值

```cpp
String s1("hello");
String s2(std::move(s1));  // 调用移动构造，s2 获得数据，s1 变为空
```

### 3.2 移动赋值 vs 拷贝赋值

移动赋值的逻辑：获取源对象的资源，释放自己原有的资源。

```cpp
class String {
public:
    // 移动赋值运算符
    String& operator=(String&& other) noexcept {
        if (this != &other) {
            delete[] str;       // 先释放自己的资源
            str = other.str;    // 偷取对方的指针
            len = other.len;
            other.str = nullptr;  // 源对象被掏空
            other.len = 0;
        }
        return *this;
    }
};
```

### 3.3 如何实现移动语义

实现移动语义需要：

1. **添加移动构造函数**：`ClassName(ClassName&& other) noexcept`
2. **添加移动赋值运算符**：`ClassName& operator=(ClassName&& other) noexcept`
3. **使用 `noexcept`**：告诉编译器移动操作不会抛出异常，这对容器和算法很重要
4. **将源对象置于可析构状态**：通常设为 `nullptr` 或默认状态

```cpp
class Resource {
public:
    Resource(const std::string& name) : name_(name) {
        std::cout << "Resource acquired: " << name_ << "\n";
    }

    ~Resource() {
        std::cout << "Resource released: " << name_ << "\n";
    }

    // 移动构造函数
    Resource(Resource&& other) noexcept : name_(std::move(other.name_)) {
        std::cout << "Resource moved: " << name_ << "\n";
    }

    // 移动赋值
    Resource& operator=(Resource&& other) noexcept {
        if (this != &other) {
            name_ = std::move(other.name_);
            std::cout << "Resource move-assigned: " << name_ << "\n";
        }
        return *this;
    }

private:
    std::string name_;
};

Resource create() {
    return Resource("temp");  // 优先触发移动
}
```

## 4. 示例：String 类实现

### 4.1 错误版本（浅拷贝）

以下实现使用默认拷贝构造函数，存在严重问题：

```cpp
class BadString {
public:
    BadString(const char* p) {
        len = strlen(p);
        str = new char[len + 1];
        strcpy(str, p);
    }

    // 没有自定义拷贝构造和拷贝赋值
    // 使用编译器生成的默认版本（浅拷贝）

    ~BadString() {
        delete[] str;
    }

    const char* c_str() const { return str; }

private:
    char* str;
    size_t len;
};

// 使用示例
void bad_string_demo() {
    BadString s1("hello");
    BadString s2(s1);  // 浅拷贝：两个对象指向同一内存

    std::cout << s1.c_str() << std::endl;  // 正常
    std::cout << s2.c_str() << std::endl;  // 正常

    // s2 析构时释放内存
    // s1 析构时再次释放同一内存 → 未定义行为/崩溃
}
```

### 4.2 正确版本（深拷贝 + 移动语义）

完整的 String 类实现，同时支持深拷贝和移动语义：

```cpp
class String {
public:
    // 默认构造函数
    String() : str(nullptr), len(0) {}

    // 构造函数
    String(const char* p) {
        len = strlen(p);
        str = new char[len + 1];
        strcpy(str, p);
    }

    // 拷贝构造函数（深拷贝）
    String(const String& other)
        : str(new char[other.len + 1]), len(other.len) {
        strcpy(str, other.str);
    }

    // 移动构造函数
    String(String&& other) noexcept
        : str(other.str), len(other.len) {
        other.str = nullptr;
        other.len = 0;
    }

    // 拷贝赋值运算符（深拷贝 + 自我赋值检查）
    String& operator=(const String& other) {
        if (this != &other) {
            String temp(other);     // 拷贝构造临时对象
            std::swap(str, temp.str);
            std::swap(len, temp.len);
        }
        return *this;
    }

    // 移动赋值运算符
    String& operator=(String&& other) noexcept {
        if (this != &other) {
            delete[] str;
            str = other.str;
            len = other.len;
            other.str = nullptr;
            other.len = 0;
        }
        return *this;
    }

    // 析构函数
    ~String() {
        delete[] str;
    }

    const char* c_str() const { return str; }
    bool empty() const { return len == 0; }

private:
    char* str;
    size_t len;
};

// 使用示例
void good_string_demo() {
    // 构造
    String s1("hello");
    String s2("world");

    // 拷贝构造
    String s3(s1);
    std::cout << s3.c_str() << std::endl;  // "hello"

    // 拷贝赋值
    s2 = s1;
    std::cout << s2.c_str() << std::endl;  // "hello"

    // 移动构造
    String s4(std::move(s1));  // s1 被掏空
    std::cout << s4.c_str() << std::endl;  // "hello"
    std::cout << s1.empty() << std::endl;   // true

    // 移动赋值
    String s5("temp");
    s5 = std::move(s4);  // s5 获得数据，s4 被掏空
    std::cout << s5.c_str() << std::endl;  // "hello"
    std::cout << s4.empty() << std::endl;   // true
}
```

## 5. 拷贝省略 (Copy Elision)

### 5.1 RVO (Return Value Optimization)

RVO 是一种编译器优化技术，允许编译器省略拷贝（或移动）返回值对象。直接在被返回的位置构造对象，避免额外的拷贝或移动操作。

```cpp
class Widget {
public:
    Widget() { std::cout << "Default构造\n"; }
    Widget(const Widget&) { std::cout << "拷贝构造\n"; }
    Widget(Widget&&) { std::cout << "移动构造\n"; }
};

Widget create_widget() {
    return Widget();  // 直接构造在调用者的位置
}

void demo_rvo() {
    Widget w = create_widget();
    // 没有输出拷贝或移动构造
    // Widget 直接在 w 的位置构造
}
```

### 5.2 NRVO (Named RVO)

NRVO 是 RVO 的变体，当返回值是一个命名变量时发生。

```cpp
Widget create_widget_named() {
    Widget w;  // 命名变量
    return w;  // NRVO：直接构造到调用者位置
}

void demo_nrvo() {
    Widget w = create_widget_named();
    // 不会调用拷贝或移动构造
}
```

**注意**：在 C++17 之前，如果 NRVO/RVO 不发生，编译器必须选择拷贝或移动返回值。C++17 起，拷贝省略是强制的（强制 RVO，即使有副作用）。

```cpp
// C++17 起，即使显式使用拷贝，编译器也可能省略
Widget w = std::move(create_widget());
// 在 C++17+ 中，可能仍然不产生移动构造
```

**拷贝省略的触发条件**（C++17）：
- 从返回语句中的局部变量返回
- 从函数返回值初始化对象

---

## 总结

理解 C++ 的拷贝语义对于编写正确、高效的代码至关重要：

- **浅拷贝**：只拷贝指针值，导致多个对象共享同一内存，危险
- **深拷贝**：拷贝整个数据，确保对象间相互独立
- **拷贝构造/赋值**：用于创建对象的完整副本
- **移动构造/赋值**：转移资源所有权，避免不必要的拷贝
- **拷贝省略**：编译器优化，避免不必要的拷贝和移动操作

遵循 Rule of Zero/Three/Five：
- **Rule of Zero**：优先使用智能指针和 RAII，让编译器生成默认的特殊成员函数
- **Rule of Three**：有自定义析构函数时，通常也需要自定义拷贝构造和拷贝赋值
- **Rule of Five**：有移动语义时，需要同时实现所有五个特殊成员函数
