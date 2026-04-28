---
title: C++ 虚函数原理
date: 2022-01-15 20:30:00
tags:
    - cpp
    - oop
---

## 1. 虚函数底层原理

### 1.1 vtable（虚函数表）的结构

虚函数表（vtable）是 C++ 实现运行时多态的核心数据结构。每个包含虚函数的类都有一个对应的 vtable，表中存放着该类所有虚函数的地址。

```
┌─────────────────────────────────────────────────────────────────┐
│                        vtable (虚函数表)                          │
├─────────────────────────────────────────────────────────────────┤
│  Index 0: 指向 RTTI type_info 的指针（编译器添加）               │
├─────────────────────────────────────────────────────────────────┤
│  Index 1: &Base::virtual_function_1()                           │
│  Index 2: &Base::virtual_function_2()                           │
│  Index 3: &Base::virtual_function_3()                           │
│  ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 vptr（虚函数指针）在对象中的位置

每个包含虚函数的对象都隐式包含一个指向 vtable 的指针（vptr）。vptr 通常位于对象内存布局的开始位置（也有些编译器放在末尾）。

```cpp
class Base {
public:
    virtual void func1() {}
    virtual void func2() {}
    int data;
};
```

```
┌──────────────────────────────┐
│   vptr (指向 Base::vtable)   │  ← 隐藏指针，编译器添加
├──────────────────────────────┤
│   int data;                  │
└──────────────────────────────┘
```

当派生类重写基类的虚函数时，派生类的 vtable 中对应位置的函数指针会被替换为派生类的版本。

### 1.3 虚函数调用机制（运行时多态）

虚函数通过以下步骤实现运行时多态：

```
1. 通过对象指针/引用访问虚函数
         │
         ▼
2. 通过对象的 vptr 找到 vtable
         │
         ▼
3. 根据函数在 vtable 中的索引定位函数地址
         │
         ▼
4. 调用找到的函数
```

```cpp
class Base {
public:
    virtual void print() { std::cout << "Base"; }
};

class Derived : public Base {
public:
    void print() override { std::cout << "Derived"; }
};

Base* ptr = new Derived();
ptr->print();  // 运行时调用 Derived::print()
```

**调用过程：**
- `ptr->print()` 被编译器转换为 `(*ptr->vptr[index_of_print])(ptr)`
- 其中 `index_of_print` 是 print 函数在 vtable 中的索引
- 通过 vptr 找到派生类的 vtable，调用派生类的 print 实现

### 1.4 vtable 布局详解

```cpp
class Base {
public:
    virtual void vfunc1() {}
    virtual void vfunc2() {}
    virtual void vfunc3() {}
    int base_data;
};

class Derived : public Base {
public:
    void vfunc2() override {}  // 重写 Base::vfunc2
    virtual void derived_vfunc() {}
    int derived_data;
};
```

```
Base 类内存布局:              Derived 类内存布局:
┌───────────────┐            ┌───────────────┐
│ vptr          │            │ vptr          │
├───────────────┤            ├───────────────┤
│ base_data     │            │ base_data     │
└───────────────┘            ├───────────────┤
                             │ derived_data  │
                             └───────────────┘

Base vtable:                  Derived vtable:
┌─────────────────┐           ┌─────────────────┐
│ type_info*      │           │ type_info*      │
├─────────────────┤           ├─────────────────┤
│ &Base::vfunc1   │◄─────────│ &Base::vfunc1   │
├─────────────────┤           ├─────────────────┤
│ &Base::vfunc2   │           │ &Derived::vfunc2│  ← 被重写
├─────────────────┤           ├─────────────────┤
│ &Base::vfunc3   │           │ &Base::vfunc3   │
└─────────────────┘           ├─────────────────┤
                             │ &Derived::derived_vfunc │
                             └─────────────────┘
```

## 2. 纯虚函数与抽象类

### 2.1 纯虚函数的定义

纯虚函数是在基类中声明但不提供实现的虚函数，要求派生类必须重写。

```cpp
class AbstractBase {
public:
    // 纯虚函数语法
    virtual void pure_virtual() = 0;
    virtual int pure_virtual_with_body() = 0 { return 42; }  // 纯虚函数可以有默认实现
};
```

### 2.2 抽象基类的特点

- 包含至少一个纯虚函数的类称为抽象基类
- 不能直接实例化抽象基类
- 派生类必须重写所有纯虚函数，否则仍然为抽象类

```cpp
class AbstractBase {
public:
    virtual void method() = 0;
};

// 错误：不能实例化抽象类
// AbstractBase obj;

// 正确：派生类可以实例化（如果重写了所有纯虚函数）
class Concrete : public AbstractBase {
public:
    void method() override { /* 实现 */ }
};

Concrete obj;  // OK
```

### 2.3 纯虚函数可以有实现吗？

是的，C++ 允许纯虚函数提供默认实现。这在设计模板方法模式时非常有用。

```cpp
class Base {
public:
    virtual void interface() = 0;

    // 纯虚函数的默认实现
    virtual void default_behavior() = 0 {
        std::cout << "Default implementation\n";
    }
};

class Derived : public Base {
public:
    void interface() override {
        std::cout << "Derived implementation\n";
    }
    // 可以选择是否重写 default_behavior
};

int main() {
    Derived d;
    d.default_behavior();  // 调用 Base 的默认实现
}
```

## 3. 虚继承

### 3.1 为什么需要虚继承

虚继承用于解决菱形继承中基类数据重复拷贝的问题。

```
        A
       / \
      B   C
       \ /
        D
```

非虚继承时，D 对象包含两份 A 的数据成员，造成二义性和空间浪费。

```cpp
class A {
public:
    int data;
};

class B : public A {};  // B::data
class C : public A {};  // C::data

class D : public B, public C {};  // D 包含 B::data 和 C::data，两份 A

D d;
d.B::data = 1;   // 必须指定作用域
d.C::data = 2;   // 否则产生二义性
```

### 3.2 虚基类表（vbptr）

虚继承通过 vbptr（虚基类指针）实现，每个虚继承的派生类对象包含一个指向虚基类表的指针。

```cpp
class A {
public:
    int data;
};

class B : virtual public A {};  // 虚继承
class C : virtual public A {};  // 虚继承

class D : public B, public C {};
```

```
虚继承时的内存布局（常见实现）：

D 对象内存布局：
┌───────────────┐
│ B 部分        │
│   vbptr ──────┼──→ 指向虚基类表
├───────────────┤
│ C 部分        │
│   vbptr ──────┼──→ 指向虚基类表
├───────────────┤
│ D 部分        │
└───────────────┘
       │
       ▼
┌───────────────┐
│ 虚基类表       │
│   偏移量 1: 指向 A::data 的偏移  │
└───────────────┘
```

虚基类表（vbtables）结构：

```
B 的虚基类表:
┌────────────────────┐
│ offset to A in B   │  ← B 对象起始到 A 子对象的偏移
└────────────────────┘

C 的虚基类表:
┌────────────────────┐
│ offset to A in C   │
└────────────────────┘
```

### 3.3 菱形继承问题及解决方案

```cpp
class A {
public:
    A(int v) : value(v) {}
    int value;
};

class B : virtual public A {
public:
    B(int v) : A(v) {}
};

class C : virtual public A {
public:
    C(int v) : A(v) {}
};

class D : public B, public C {
public:
    D(int v) : A(v), B(v), C(v) {}  // 必须显式调用 A 的构造函数
};

int main() {
    D d(10);
    std::cout << d.value << std::endl;  // 直接访问，无二义性
}
```

虚继承的优势：
- 只保留一份基类子对象
- 消除二义性
- 节省内存空间

## 4. 构造函数与析构函数中的虚函数

### 4.1 构造函数调用虚函数会发生什么

在构造函数中调用虚函数，**不会**表现出多态性。构造顺序决定了此时调用的是当前正在构造的类的方法。

**构造顺序：**
1. 基类部分构造
2. 成员对象构造
3. 派生类自身构造

当基类构造函数执行时，只有基类的虚函数表指针被设置，派生类的重写尚未生效。

```cpp
class Base {
public:
    Base() {
        std::cout << "Base constructor\n";
        draw();  // 调用的是 Base::draw()
    }
    virtual void draw() { std::cout << "Base::draw()\n"; }
};

class Derived : public Base {
public:
    Derived() {
        std::cout << "Derived constructor\n";
        draw();  // 调用的是 Derived::draw()
    }
    void draw() override { std::cout << "Derived::draw()\n"; }
};

Derived d;
/*
输出：
Base constructor
Base::draw()    ← 注意：这里调用的是 Base::draw()
Derived constructor
Derived::draw()
*/
```

### 4.2 析构函数中的虚函数行为

析构函数中的虚函数行为与构造函数类似，**不会**表现出多态性。

**析构顺序：**
1. 派生类自身析构
2. 成员对象析构
3. 基类部分析构

当基类析构函数执行时，派生类的部分已经被销毁，此时 vptr 已经指向基类的虚函数表。

```cpp
class Base {
public:
    ~Base() {
        std::cout << "Base destructor\n";
        draw();  // 调用的是 Base::draw()
    }
    virtual void draw() { std::cout << "Base::draw()\n"; }
};

class Derived : public Base {
public:
    ~Derived() {
        std::cout << "Derived destructor\n";
        draw();  // 调用的是 Derived::draw()
    }
    void draw() override { std::cout << "Derived::draw()\n"; }
};

Derived d;
/*
输出：
Derived destructor
Base destructor
Base::draw()    ← 注意：这里调用的是 Base::draw()
*/
```

### 4.3 为什么要这样设计

这种设计是为了**防止访问已销毁的派生类成员**。如果构造/析构函数中调用虚函数表现出多态性，可能会访问已经被销毁的派生类数据成员，导致未定义行为。

## 5. 虚函数与默认参数

### 5.1 默认参数的静态绑定特性

虚函数调用的默认参数遵循**静态绑定**规则，而非动态绑定。这意味着默认参数由对象的**静态类型**决定，而非运行时实际类型。

```cpp
class Base {
public:
    virtual void method(int value = 10) {
        std::cout << "Base: " << value << "\n";
    }
};

class Derived : public Base {
public:
    void method(int value = 20) override {
        std::cout << "Derived: " << value << "\n";
    }
};

int main() {
    Base* b = new Derived();

    b->method();  // 输出: Base: 10
                  // 原因：默认参数静态绑定到 Base

    // 派生类对象直接调用：
    Derived d;
    d.method();   // 输出: Derived: 20

    delete b;
    return 0;
}
```

### 5.2 为什么默认参数不动态绑定

这是 C++ 的设计决策，主要原因：

1. **效率考虑**：动态绑定默认参数需要运行时查询，增加开销
2. **二义性问题**：如果派生类省略默认参数，而基类提供默认值，可能导致调用结果不确定

### 5.3 解决方案：NVI 模式

使用 Non-Virtual Interface（NVI）模式可以优雅地解决这个问题：

```cpp
class Base {
public:
    void method() {  // 非虚接口函数
        do_method();  // 调用实际实现
    }

protected:
    virtual void do_method(int value = 10) {  // 派生类重写这个
        std::cout << "Base: " << value << "\n";
    }
};

class Derived : public Base {
protected:
    void do_method(int value) override {
        std::cout << "Derived: " << value << "\n";
    }
};

int main() {
    Base* b = new Derived();
    b->method();  // 输出: Derived: 10
    delete b;
}
```

### 5.4 默认参数与 override 的注意事项

```cpp
class Base {
public:
    virtual void func(int x = 5) = 0;
};

class Derived : public Base {
public:
    // 如果派生类不写默认参数，使用 Base 的默认值 5
    void func(int x) override {  // 注意：签名必须匹配
        std::cout << x << "\n";
    }
};

Derived d;
d.func();  // 错误：调用时需要传参

Base* b = &d;
b->func();  // 输出: 5（使用 Base 的默认参数）
```

## 总结

| 特性 | 行为 |
|------|------|
| vtable | 每个含虚函数的类一个，表项为函数指针 |
| vptr | 每个对象一个，指向类的 vtable |
| 虚函数调用 | 通过 vptr 索引到 vtable，运行时分派 |
| 纯虚函数 | 可有默认实现，= 0 声明纯虚性 |
| 虚继承 | 通过 vbptr 解决菱形继承，数据唯一性 |
| 构造/析构中虚函数 | 静态绑定，不表现多态 |
| 默认参数 | 静态绑定，由静态类型决定 |
