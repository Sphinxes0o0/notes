---
type: entity
tags: [cpp, object-lifetime, storage-duration, temporary-objects, ub]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# 吴咏炜 — To Be or Not to Be: On Object Lifetime

## 定义
吴咏炜的演讲深入讲解C++对象生存期（Object Lifetime）：存储期（Storage Duration）、生存期（Lifetime）、临时对象、隐式生存期对象、可平凡复制对象，以及相关调试工具。

## 关键要点

### 存储期 vs 生存期
- **存储期（Storage Duration）**：为对象预留的内存空间所持续的时间
  - 静态（static）：程序启动前构造，main返回后析构
  - 线程（thread）：与绑定线程同周期
  - 自动（automatic）：代码执行到定义处构造，离开作用域析构
  - 动态（dynamic）：手工管理（new/delete或placement new）
- **生存期（Lifetime）**：对象从构造完成到析构开始
- 生存期不会超出存储期；在生存期之外访问对象是未定义行为

### 静态存储期对象
- 构造：进入main之前（同一翻译单元按定义顺序，不同翻译单元无确定顺序 — "静态初始化顺序陷阱"）
- 析构：main返回之后，顺序与构造相反
- **Meyers单例**：`static T instance()` 解决静态初始化顺序问题

### 线程存储期对象
- 每个线程拥有独立副本
- 函数内thread_local变量在当前线程首次执行到定义处构造
- 析构函数在线程退出时被调用

### 自动存储期对象
- 代码执行到变量定义处构造，离开作用域析构
- 先构造的后析构
- 异常抛出时也会析构（stack unwinding）
- 返回局部变量的引用或指针通常是一个错误

### "动态"对象的处理
- 需确保内存对齐（C++17之前连`new Obj(...)`都不能确保）
- 需确保调用析构函数在存储被释放或重用之前
- placement new：`std::byte buffer[sizeof(Obj)]; ptr = new (buffer) Obj(); ptr->~Obj();`

### 临时对象
- **定义**：由纯右值（prvalue）实体化产生的无名对象
- **生存期结束点**：创建它的完整表达式（full-expression）结束时销毁
- 示例：`x + x`, `x++`（但`++x`不是）, `getObj()`

### 隐式生存期对象与可平凡复制对象
- 隐式生存期对象：构造由编译器隐式触发
- 可平凡复制对象（Trivially Copyable）：memcpy安全的类型

### 相关工具
- AddressSanitizer (ASan)：检测use-after-free、double-free
- Valgrind：内存调试
- Compiler warnings：未初始化变量、析构函数检查

## 相关概念
- [[entities/cpp/cpp-object-lifetime]] — 已有entity，交叉引用
- [[entities/cpp/raii]] — 构造/析构与资源管理
- [[entities/cpp/smart-pointers]] — 动态生存期管理
- [[entities/cpp/cpp-stl-containers]] — 容器与对象生存期

## 来源详情
- [[sources/pdf-cpp-slides]] — 吴咏炜, 对象生存期, C++技术演讲 2025
