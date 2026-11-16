---
type: entity
tags: [cpp, cpp11, modern-cpp, virtual-functions, override-specifier]
created:2026-06-08
sources: [bookmark-effective-modern-cpp]
---

# C++11 Explicit Virtual Overrides

## 定义

C++11引入 `override`关键字，明确标注派生类虚函数覆写（override）基类虚函数。编译器会验证基类中确实存在签名一致的虚函数，否则报错。这是消除"silent override"错误（基类改名后派生类不再覆写，但仍以为是覆写）的关键安全特性。配套的还有 `final`关键字，禁止进一步覆写。

##关键要点

- **`override`关键字**：仅作编译期断言，零运行时开销
- **`final`关键字**：禁止类被继承 /虚函数被进一步覆写
- **编译期检查**：派生类签名不匹配时立即报错
- **零开销**：与不加 `override` 的虚函数机器码完全一致
- **代码可读性**：读者无需翻基类即可看出是覆写

##核心概念

- **虚函数覆写三要素**：相同签名 + `virtual`（隐式或显式）+派生类作用域
- **常见错误**：constness差异、参数默认值不参与覆写（按静态类型解析）
- **override vs overload**：override 是覆写基类同名虚函数；overload 是同作用域同名不同参数
- **与 `final`组合**：`void foo() override final;`禁止再覆写
- **多继承歧义**：override 帮助编译器解析二义性虚函数

## 相关页面

- [[entities/cpp/modern-cpp/cpp-attributes]] — C++11 属性语法
- [[entities/cpp/modern-cpp/cpp-concepts]] — Concepts
- [[entities/cpp/modern-cpp/cpp-attributes]] —虚函数表
- [[sources/bookmark-effective-modern-cpp]] — Effective Modern C++
