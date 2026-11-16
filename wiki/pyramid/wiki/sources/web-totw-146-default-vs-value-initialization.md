---
type: source
source-type: web
title: "Tip of the Week #146: Default vs Value Initialization"
author: "Dominic Hamon"
date: 2012
url: https://abseil.io/tips/146
summary: "abseil C++ Tips of the Week #146: Default vs Value Initialization."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: c8f65380bd7ce3476ab63fde0c4abf10
---

> 原文：<https://abseil.io/tips/146> · 作者：Dominic Hamon · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#146: Default vs Value Initialization

\
\

Originally posted as TotW \#146 on April 19, 2018

*By [Dominic Hamon](/cdn-cgi/l/email-protection#a7c3c8cacec9cec4e7c0c8c8c0cbc289c4c8ca)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/146](https://abseil.io/tips/146)

“The road to success is always under construction.” – [Lily Tomlin](https://en.wikipedia.org/wiki/Lily_Tomlin)

## TL;DR

For safety and readability, you should assume scalar objects are not initialized to a reasonable value until they have been explicitly set to a value. Use of initializers can ensure that scalar values are initialized to safe values.

## Introduction

When objects are created, they may be initialized or uninitialized. Uninitialized objects are not safe to read, but understanding when the object is uninitialized is not trivial.

The first thing to understand is if the type under construction is scalar, aggregate, or some other type. A *scalar* type can be thought of as a simple type: an integral or floating point arithmetic object; a pointer; an enum; a pointer-to-member; `nullptr_t`. An *aggregate* type is an array or a class with nothing virtual, no non-public fields or bases, and no constructor declarations.

Another factor affecting whether an instance has been initialized to a value that is safe to read is whether it has an explicit *initializer*. That is, the object name in the statement is followed by `()`, `{}`, or `= {}`.

As these rules are not intuitive, the easiest rule to remember to ensure an object is initialized is to provide an initializer. This is called *value-initialization* and is distinct from *default-initialization*, which is what the compiler will perform otherwise for scalar and aggregate types.

## User-Provided Constructors

If a type is defined with a user-defined constructor, it is not an aggregate type, and initialization gets much simpler with both value- and default-initialization invoking the constructor:

```cpp

struct Foo {
  Foo() : v() {}

  int v;
  std::string s;
};

int main() {
  Foo default_foo;
  Foo value_foo = {};
  ...
}
```

The `= {}` triggers value-initialization of `value_foo`, which calls `Foo`’s default constructor. After, `v` is safe to read, because the constructor’s initializer list value-initializes it. In fact, as `v` does not have a class type, this is a special case of value-initialization called *zero-initialization* and `value_foo.v` will have the value `0`.

Similarly, while `default_foo` is default-initialized, it calls the same constructor, so `default_foo.v` is also zero-initialized and is safe to read.

Note that `Foo::s` has a user-provided constructor, so it is value-initialized in either case, and safe to read.

## User-Declared vs User-Provided Constructors

It is possible for the user to *declare* a constructor while asking the compiler to *provide* the definition via `=default`. For example:

```cpp

struct Foo {
  Foo() = default; // "User-declared", NOT "user-provided".

  int v;
};

int main() {
  Foo default_foo;
  Foo value_foo = {};
}
```

In this case, `Foo` defines a *user-declared*, but not *user-provided*, constructor. While this type will not be an aggregate, members will be initialized as if for an aggregate. This means that `default_foo.v` will be uninitialized, while `value_foo.v` will be *zero-initialized*. Note that “user-declared” only applies to a default constructor which is defaulted (`= default`) *at its point of declaration*. A defaulted out-of-line *implementation* (`Foo::Foo() = default`) is considered user-provided and will behave equivalently to a definition of `Foo::Foo() {}`.

### Uninitialized Members in User-Provided Constructors

```cpp

struct Foo {
  Foo() {}

  int v;
};

int main() {
  Foo foo = {};
}
```

In this case, although `Foo` has a user-provided constructor, it fails to initialize `v`. In this case, `v` is once more default-initialized, which means its value is undetermined, and it is unsafe to read.

### Explicit Value-Initialization

In general, it is a good idea to replace the initializer with an explicit initialization to a value, even if that value is 0, for the benefit of the reader. This is called *direct-initialization*, which is a more specific form of value-initialization.

```cpp

struct Foo {
  Foo() : v(0) {}

  int v;
};
```

## Default Member Initialization

A simpler solution than defining constructors for classes, while still avoiding the pitfalls of default- vs value-initialization, is to initialize members of classes at declaration, wherever possible:

```cpp

struct Foo {
  int v = 0;
};
```

This ensures that no matter how the instance of `Foo` is constructed, `v` will be initialized to a determinate value.

*Default member initialization* also serves as documentation, especially in the case of booleans, or non-zero initial values, as to what is a safe initial value for the member.

## Pro Tip: Scalar Zero-Initialization

The full set of rules for when scalar values are safe to read after initialization:

- The type is followed by an explicit `()`, `{}`, or `= {}` initializer.
- The instance of the type under construction is an element of an array with an initializer as above. E.g., `new int[10]()`.
- The instance of the type under construction is a member of a class with a disabled default constructor, and the instance of the outer object is value-initialized.
- The instance of the type under construction is static or thread-local.
- The instance of the type under construction is a member of a class with an aggregate type that has an initializer.

### Array Types

It’s easy to forget to add an explicit initializer to array declarations, but this can lead to particularly pernicious initialization issues.

```cpp

int main() {
  int foo[3];
  int bar[3] = {};
  ...
}
```

Every element of `foo` is default-initialized, while every element of `bar` will be zero-initialized.

## A Digression Discerning Defaulted Default Constructor Declarations

Pop quiz: Do these stylistically different declarations affect the behaviour of the code?

```cpp

struct Foo {
  Foo() = default;

  int v;
};

struct Bar {
  Bar();

  int v;
};

Bar::Bar() = default;

int main() {
  Foo f = {};
  Bar b = {};
  ...
}
```

Many developers would reasonably assume that this may affect code generation quality, but otherwise is a style preference. As you might have guessed, because I’m asking, this is not the case.

The reason goes back to the section above on [User-Declared vs User-Provided Constructors](#user-declared-vs-user-provided-constructors). As the constructor for `Foo` is defaulted on declaration, it is not user-provided (but it *is* user-declared). This means that while `Foo` is not an aggregate type, `f.v` is still zero-initialized. However, `Bar` has a user-provided constructor, albeit created by the compiler as a defaulted constructor. As this constructor does not explicitly initialize `Bar::v`, `b.v` will be default-initialized and unsafe to read.

## Recommendations

- Be explicit about the value to which scalar types are being initialized instead of relying on zero-initialization.
- Treat all instances of scalar types as having indeterminate values until you explicitly initialize or assign to them.
- If a member has a sensible default, and the class has multiple constructors, use a default member initializer to ensure it isn’t left uninitialized. Be aware that [a member initializer within a constructor will override the default](http://en.cppreference.com/w/cpp/language/data_members).

## Further Reading

- [Tip \#61](/tips/61): Default Member Initializers
- [Tip \#88](/tips/88): Initialization: `=`, `()`, and `{}`
- [Tip \#131](/tips/131): Special member functions and `=default`
- [CppReference - Initialization](http://en.cppreference.com/w/cpp/language/initialization)


