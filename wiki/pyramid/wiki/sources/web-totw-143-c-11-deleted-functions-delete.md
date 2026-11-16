---
type: source
source-type: web
title: "Tip of the Week #143: C++11 Deleted Functions (`= delete`)"
author: "Leonard Mosescu"
date: 2012
url: https://abseil.io/tips/143
summary: "abseil C++ Tips of the Week #143: C++11 Deleted Functions (`= delete`)."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: b25c725c2623f8395cc7ac5f857014a9
---

> 原文：<https://abseil.io/tips/143> · 作者：Leonard Mosescu · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#143: C++11 Deleted Functions (`= delete`)

\
\

Originally posted as TotW \#143 on March 2, 2018

*By [Leonard Mosescu](/cdn-cgi/l/email-protection#9ef3f1edfbedfdebdef9f1f1f9f2fbb0fdf1f3)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/143](https://abseil.io/tips/143)

## Introduction

Interfaces, in a general sense, normally define the set of operations which can be invoked. Yet sometimes we may want to express the opposite: explicitly define a set of operations which should *not* be used. For example, disabling the copy constructor and copy assignment operator is a common way to restrict copy semantics for a particular type.

The language offers multiple options to effect such restrictions (and we’ll explore each one shortly):

1.  Provide a dummy definition consisting solely of a *runtime* check.
2.  Use accessibility controls (protected/private) to make the function inaccessible.
3.  Declare the function, but intentionally omit the definition.
4.  Since C++11: Explicitly define the function as “deleted”.

The pre-C++11 techniques range from runtime checks (#1) to compile-time (#2) or link time (#3) diagnostics. While battle-proven, these techniques are far from perfect: a runtime check is not ideal for the majority of situations where the constraint is static, and the link-time check delays the diagnostic to very late in the build process. Moreover, link time diagnostics are not guaranteed (missing a definition for an ODR-used function is an ODR violation) and the actual diagnostic messages are rarely developer-friendly.

A compile time check is better, but still flawed. It only works for member functions and is based on accessibility constraints, which are verbose, error-prone and susceptible to loopholes. Moreover, the errors that result from referencing such functions can be misleading, referring as they do to access restrictions rather than interface misuse.

The application of \#2 and \#3 to disable copying would look like this:

```cpp

class MyType {
 private:
  MyType(const MyType&);  // Not defined anywhere.
  MyType& operator=(const MyType&);  // Not defined anywhere.
  // ...
};
```

Manually applying this for every class gets old really fast, so developers commonly package them in one of these ways:

**The “mixin” approach** ([boost::noncopyable](http://www.boost.org/doc/libs/master/libs/core/doc/html/core/noncopyable.html), [non-copyable mixin](https://en.wikibooks.org/wiki/More_C%2B%2B_Idioms/Non-copyable_Mixin))

```cpp

class MyType : private NoCopySemantics {
  ...
};
```

**The macros approach**

```cpp

class MyType {
 private:
  DISALLOW_COPY_AND_ASSIGN(MyType);
};
```

## C++11 Deleted Definitions

C++11 addressed the need for a better solution through a new language feature: deleted definitions \[*dcl.fct.def.delete*\]. (See “deleted definitions” in the [C++ standard draft](http://eel.is/c++draft/dcl.fct.def.delete).) Any function can be explicitly *defined as deleted:*

```cpp

void foo() = delete;
```

The syntax is straightforward, resembling [defaulted functions](131), although with a couple of notable differences:

1.  Any function can be deleted, including non-member functions (in contrast to `=default`, which works only with special member functions).
2.  Functions must be deleted on the first declaration only (unlike `=default`).

The key thing to keep in mind is that `=delete` is a function *definition* (it does not remove or hide the declaration). The deleted function is thus defined and participates in name lookup and overload resolution as any other function. It’s a special kind of *“radioactive”* definition which says *“don’t touch!”*.

Attempts to use a deleted function result in a *compile time* error with a clear diagnostic, which is one of the key benefits over the pre-C++11 techniques.

```cpp

class MyType {
 public:
  // Disable default constructor.
  MyType() = delete;

  // Disable copy (and move) semantics.
  MyType(const MyType&) = delete;
  MyType& operator=(const MyType&) = delete;

  //...
};
```

```cpp

// error: call to deleted constructor of 'MyType'
// note: 'MyType' has been explicitly marked deleted here
//   MyType() = delete;
MyType x;

void foo(const MyType& val) {
  // error: call to deleted constructor of 'MyType'
  // note: 'MyType' has been explicitly marked deleted here
  //   MyType(const MyType&) = delete;
  MyType copy = val;
}
```

**Note**: by explicitly defining the copy operations as deleted we also suppress the move operations (having user-declared copy operations inhibits the implicit declaration of the move operations). If the intention is to define a move-only type using the implicit move operations, [`=default`](131) can be used to “bring them back”, for example:

```cpp

MyType(MyType&&) = default;
MyType& operator=(MyType&&) = default;
```

## Other Uses

While the examples above are centered on copy semantics (which is likely the most common case), any function (member or not) can be deleted.

Since deleted functions participate in overload resolution they can help catch unintended uses. Let’s say we have the following overloaded `print` function:

```cpp

void print(int value);
void print(absl::string_view str);
```

Calling `print('x')` will print the integer value of ‘x’, when the developer likely intended `print("x")`. We can catch this:

```cpp

void print(int value);
void print(const char* str);
// Use string literals ":" instead of character literals ':'.
void print(char) = delete;
```

Note that `=delete` doesn’t affect just function calls. Attempting to take the address of a deleted function will also result in a compilation error:

```cpp

void (*pfn1)(int) = &print  // ok
void (*pfn2)(char) = &print // error: attempt to use a deleted function
```

This example is extracted from a real world application: [absl::StrCat()](https://github.com/abseil/abseil-cpp/blob/092ed9793a1ad0e7e418f32c057bf3159a71cd04/absl/strings/str_cat.h#L257). Deleted functions are valuable any time a particular part of an interface must be restricted.

Defining destructors as deleted is stricter than making them private (although this is a big hammer and it may introduce more limitations than intended)

```cpp

// A _very_ limited type:
//   1. Dynamic storage only.
//   2. Lives forever (can't be destructed).
//   3. Can't be a member or base class.
class ImmortalHeap {
 public:
  ~ImmortalHeap() = delete;
  //...
};
```

Yet another example, this time we want to only allow the allocation of non-array objects (\[real world example\]\[crashpad\]):

```cpp

// Don't allow new T[].
class NoHeapArraysPlease {
 public:
  void* operator new[](std::size_t) = delete;
  void operator delete[](void*) = delete;
};

auto p = new NoHeapArraysPlease;  // OK

// error: call to deleted function 'operator new[]'
// note: candidate function has been explicitly deleted
//   void* operator new[](std::size_t) = delete;
auto pa = new NoHeapArraysPlease[10];
```

## Summary

`=delete` offers an explicit way to express parts of an interface which should not be referenced, also enabling better diagnostics than the pre-C++11 idioms. No piece of code, including compiler generated code, can reference a deleted function. For nuanced access control, the access specifiers or more elaborate techniques (for example, the passkey idiom as discussed in [Tip \#134](134)) are more appropriate.

**Important**: Since the deleted definitions are part of the interface they should have the same access specifier as the other parts of the interface. Concretely, this means they should usually be public. In practice this also results in the best diagnostics (private and =delete doesn’t make much sense).

**Credits**: This tip includes key contributions and feedback from many people, special thanks to: Mark Mentovai, James Dennett, Bruce Dawson and Yitzhak Mandelbaum.

### References

- [TotW \#131: Special member functions and =default](131)
- [TotW \#134: make_unique and private constructors](134)
- [`delete`d functions](http://en.cppreference.com/w/cpp/language/function#Deleted_functions)
- [access specifiers](http://en.cppreference.com/w/cpp/language/access)
- [C++ Core Guidelines: C.81](https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md#c81-use-delete-when-you-want-to-disable-default-behavior-without-wanting-an-alternative)
- [Google C++ style guide: Copyable and Movable Types](https://google.github.io/styleguide/cppguide.html#Copyable_Movable_Types)


