---
title: C++ 类型转换
date: 2026-04-28 12:00:00
tags:
    - cpp
    - type-casting
---

## 1. C 风格类型转换

### 1.1 (type)value 语法

C 风格类型转换使用括号将目标类型放在变量前：

```cpp
double d = 3.14159;
int i = (int)d;           // 截断小数部分，结果为 3
int* p = (int*)0x1234;    // 将地址值强制转换为指针
```

### 1.2 存在的问题

C 风格类型转换存在以下缺陷：

- **隐蔽性**：转换语法简单，不易在代码审查中发现
- **危险性**：可以随意转换任何类型，缺乏类型检查
- **行为未定义**：在某些不兼容类型之间转换会导致未定义行为
- **难以追踪**：无法区分不同目的的转换操作

```cpp
// 危险示例：const 指针被轻易去除 const 属性
const int* pc = &i;
int* p = (int*)pc;  // 虽然能编译，但导致未定义行为
```

## 2. 四种 C++ 类型转换

### 2.1 static_cast：编译期转换

`static_cast` 用于编译期能够确定的类型转换，具有编译时类型检查：

```cpp
// 基本类型之间的转换
double d = 3.14159;
int i = static_cast<int>(d);  // 安全的基本类型转换

// 有转换构造函数的类类型转换
class A {
public:
    A(int x) {}
};

A a = static_cast<A>(10);  // 调用 A(int) 构造函数

// 父子类之间的上行转换（安全）
class Base {};
class Derived : public Base {};
Derived d;
Base* bp = static_cast<Base*>(&d);  // 上行转换，安全
```

### 2.2 dynamic_cast：运行时多态转换

`dynamic_cast` 用于运行时类型识别和安全的多态类型转换：

```cpp
class Base {
public:
    virtual ~Base() {}  // 必须有虚函数才能使用 dynamic_cast
};

class Derived : public Base {
public:
    void specific() {}
};

Base* bp = new Derived();

// 下行转换：安全，如果类型不匹配返回 nullptr
Derived* dp = dynamic_cast<Derived*>(bp);
if (dp) {
    dp->specific();
}

// 引用类型的下行转换：失败时抛出 bad_cast 异常
try {
    Derived& dr = dynamic_cast<Derived&>(*bp);
} catch (const std::bad_cast& e) {
    // 转换失败
}
```

### 2.3 const_cast：const 属性移除

`const_cast` 是唯一能去除 const 限定符的转换运算符：

```cpp
const int c = 100;
// int* p = &c;              // 错误：不能从 const int* 赋值给 int*
int* p = const_cast<int*>(&c);  // 去除 const 属性

// 也可用于去除 volatile 限定符
volatile int v = 200;
int* pv = const_cast<int*>(&v);
```

### 2.4 reinterpret_cast：位 reinterpretation

`reinterpret_cast` 将位模式重新解释为另一种类型，用于低层次内存操作：

```cpp
// 指针类型之间的转换
int* ip = new int(42);
char* cp = reinterpret_cast<char*>(ip);

// 将指针转换为整数
uintptr_t addr = reinterpret_cast<uintptr_t>(ip);

// 函数指针类型转换（不可移植）
typedef void (*FuncPtr)();
FuncPtr fp = reinterpret_cast<FuncPtr>(ip);
```

## 3. 各转换的使用场景

### 3.1 何时使用 static_cast

- **基本类型之间的数值转换**：如 double 转 int
- **类层次结构中的上行转换**（派生类到基类）
- **具有明确转换构造函数的类型转换**
- **void* 与其他指针类型之间的转换**
- **枚举与整数之间的转换**

```cpp
int i = static_cast<int>(3.14);           // 数值转换
char c = static_cast<char>(65);           // 整数到字符
void* vp = static_cast<void*>(ip);        // 指针转 void*
int* ip2 = static_cast<int*>(vp);         // void* 转具体指针
```

### 3.2 何时使用 dynamic_cast

- **类层次结构中的下行转换**（基类到派生类）
- **需要安全检查的多态类型转换**
- **在运行时需要判断对象实际类型时**

```cpp
Base* bp = getObject();  // 返回基类指针，不知道实际类型
if (Derived* dp = dynamic_cast<Derived*>(bp)) {
    // 只有当 bp 实际指向 Derived 对象时才进入此分支
    dp->derivedMethod();
}
```

### 3.3 何时使用 const_cast

- **修改 non-const 版本的函数参数**（调用 const 版本的成员函数后）
- **与不支持 const 的旧 API 交互**
- **实现缓存或备忘录功能时修改 const 对象**

```cpp
class Cache {
    std::string find(const std::string& key) const {
        // 在 const 成员函数中访问非 const 的内部缓存
        return const_cast<Cache*>(this)->cache[key];
    }
    std::map<std::string, std::string> cache;
};
```

### 3.4 何时使用 reinterpret_cast

- **与硬件或底层系统交互**
- **网络协议解析**
- **序列化/反序列化操作**
- **指针与整数之间的转换**（应谨慎使用）

```cpp
// 网络协议解析
struct Packet {
    char data[4];
};

char buffer[4] = {0x01, 0x02, 0x03, 0x04};
Packet* pkt = reinterpret_cast<Packet*>(buffer);

// 指针与地址转换
uintptr_t addr = reinterpret_cast<uintptr_t>(pointer);
void* ptr = reinterpret_cast<void*>(addr);
```

## 4. 转换安全注意事项

### 4.1 类型安全

遵循以下原则确保类型转换安全：

- **优先使用 static_cast 和 dynamic_cast**，避免使用 C 风格转换
- **dynamic_cast 适用于多态类型**，确保类中有虚函数
- **const_cast 只用于去除 const 属性**，不要用于修改实际上为 const 的对象
- **reinterpret_cast 仅用于低层次操作**，确保了解底层表示

### 4.2 危险的转换示例

```cpp
// 危险 1：去除 const 后修改 const 对象
const int constVal = 100;
int* p = const_cast<int*>(&constVal);
*p = 200;  // 未定义行为！constVal 可能存储在只读内存

// 危险 2：错误的 reinterpret_cast
double d = 3.14;
int* ip = reinterpret_cast<int*>(&d);  // 未定义行为
// 在不同平台上 double 和 int 可能有不同大小和对齐要求

// 危险 3：类型别名导致的未定义行为
alignas(8) char buffer[16];
auto* p1 = reinterpret_cast<double*>(buffer);
auto* p2 = reinterpret_cast<int*>(buffer);  // 别名规则违规

// 危险 4：C 风格转换绕过类型检查
class Base {};
class Derived1 : public Base {};
class Derived2 : public Base {};

Derived1 d1;
Base* bp = &d1;
// Derived2* d2p = (Derived2*)bp;  // 未定义行为
Derived2* d2p = dynamic_cast<Derived2*>(bp);  // 安全，返回 nullptr
```

### 4.3 安全建议

- **优先使用 C++ 类型转换运算符**，它们具有更好的可读性和可追踪性
- **使用 static_cast** 替代大多数 C 风格转换
- **使用 dynamic_cast** 进行多态类型向下转换，并检查返回值
- **谨慎使用 const_cast**，确保不会修改真正的 const 对象
- **避免使用 reinterpret_cast**，或者将其封装在明确意图的函数中
- **启用编译器警告**（如 `-Wold-style-cast`），检测潜在的 unsafe 转换
