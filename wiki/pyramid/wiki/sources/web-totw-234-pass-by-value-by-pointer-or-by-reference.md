---
type: source
source-type: web
title: "Tip of the Week #234: Pass by Value, by Pointer, or by Reference?"
author: "Steve Wang"
date: 2012
url: https://abseil.io/tips/234
summary: "abseil C++ Tips of the Week #234: Pass by Value, by Pointer, or by Reference?."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 410810e7a3877fe9ac9a76a1f2718f45
---

> 原文：<https://abseil.io/tips/234> · 作者：Steve Wang · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#234: Pass by Value, by Pointer, or by Reference?

\
\

Originally posted as TotW \#234 on August 29, 2024

*By [Steve Wang](/cdn-cgi/l/email-protection#6b1c0a050c181f0e1d0e2b0c04040c070e45080406)*

Updated 2024-09-30

Quicklink: [abseil.io/tips/234](https://abseil.io/tips/234)

## Overview

Many programming languages, such as Java and Python, always access objects via references, and functions that accept objects get their own reference to the caller’s object. Others, such as C and Go, allow you to explicitly specify pointers to objects. C++ further allows you to choose whether to pass by value, giving the called function a copy of the argument, or to pass by reference, giving the called function access to the caller’s object. This tip will illustrate the various ways input-only function parameters are passed in C++ and provide recommendations and caveats.

When we talk about passing by value, we explicitly mean that the language ensures that the scope of the function call has an exclusive copy of its argument\[^elision\]. Reassigning a new value to this variable does not mutate the corresponding object in the caller’s scope. However, invoking the argument’s methods may still mutate its underlying state.

Meanwhile, when we talk about passing by reference, we effectively bring the object from the caller’s scope into the current function’s scope, and reassignment will mutate the underlying object.

Passing by pointer has some similarities to passing by reference, yet is technically a special case of pass-by-value, as the pointer itself is a value that corresponds to the address of the underlying object (or a null pointer, which refers to no object at all).

Consider the following:

```cpp

void AddOneToValue(int x) {
  ++x;
}

void AddOneToReference(int& x) {
  ++x;
}

// Here, the pointer points at a "pointee"; we're adding one to the
// pointed-at object.
void AddOneToPointee(int* x) {
  ++*x;
}

...

int x = 5;
AddOneToValue(x);
// x is still 5.
AddOneToReference(x);
// x is now 6.
AddOneToPointee(&x);
// x is now 7.
```

As a result, when writing functions in C++, the language makes us consider how to pass parameters – should we pass by value, by pointer, by reference (if so, which kind)?

## Why Do We Care About Passing by Value?

The astute reader might wonder what the issues are with always passing by reference. First off, having unnecessary `const T&` (e.g., `Add(const int& a, const int& b)`) adds visual clutter.

Second, in C++, as mentioned above, a reference is largely syntactic sugar for a pointer\[^const_ref\], with the associated overhead of a memory lookup when we want to use it unless the compiler is able to optimize that away. By passing small types by value, we can pass them in registers instead of needing to store them on the stack.

```cpp

// Passing a small value by value, the compiler can avoid a stack allocation and
// pass it in a register.
int foo = 5;
Bar(foo);

// However, passing a small value by reference requires `foo` to be copied
// ("spilled") to the stack since you can't take the address of a register.
int foo = 5;
Bar(&foo);
```

Of course, if the variable is already on the stack or heap (e.g., it’s part of an array) then this concern is irrelevant, but we should still prefer to pass by value to avoid some cache misses and memory pressure if it’s already loaded in a register.

Regardless, references can further introduce concerns regarding *aliasing*\[^aliasing\] – since the function does not have an exclusive copy of the object, we have no guarantees that the object will remain unchanged throughout the lifetime of the function, even if we have a reference-to-const (which is only a promise that we will not mutate it *through that particular parameter*).

## Why Do We Care About Passing by Reference?

On the opposite end of the spectrum, one might wonder why we don’t just pass all input parameters by value.

In C++, if you pass a variable by value, depending on how the function is called the variable’s value may be copied or moved (or neither)\[^names\]. On the other hand, passing by reference (or pointer) allows you to refer to an existing object and therefore avoid a copy entirely. So, in general, the larger an object, the more you should prefer passing by reference.

Passing by value can have benefits as well as drawbacks from the perspective of memory safety. On one hand, if you have the only copy of an object, then you don’t have to worry about other threads stomping over its state. On the other hand, if you retain a reference to this object, once it goes out of scope, then you have a use-after-free bug (just as for any other local variable).

## Guidelines

All of these rules apply equally. If none of them apply, a safe option is to pass by reference-to-const for required parameters, and by pointer for optional ones.

### Pass by Value

Passing by value can be more *efficient* in some cases (when the relevant types are small enough that moving or copying them is more efficient than working via pointers), and is helpful for conveying ownership (typically when the called function wants to own the value, to move from it, or to otherwise modify its own copy).

Specifically, the types listed below should usually be passed by value:

- Numeric and enumeration types (including protobuf enums).
- Smart pointers, when the called function takes ownership unconditionally.

Some additional types can be efficiently passed by value, as an optimization:

- Types that provide an efficient move constructor, **only if the called function needs its own copy of the value**. Examples include `std::vector<T>`, `std::string`, `absl::flat_hash_map<T>` and other containers that don’t store their contents inline\[^proto_move\].

  In these cases, you should pass by value, and `std::move` at the callsite when needed (or pass in a temporary which is subject to mandatory copy elision per [Tip \#166](/tips/166)). See [Tip \#117](/tips/117) for supplemental reading on copy elision and pass-by-value.

  Passing by value is especially common in a constructor that stores one of these types in a member variable.

  ``` cpp

  class Foo {
    public:
      // Here, we pass bar by reference and copy it into bar_.
      Foo(const std::vector<int>& bar) : bar_(bar) {}

      // But, we can instead use std::vector's move constructor to avoid
      // the expensive copy entirely, in some cases.
      Foo(std::vector<int> bar) : bar_(std::move(bar)) {}
    private:
      std::vector<int> bar_;
  };
  ```

- `T`, where `sizeof(T) <= 16`<sup><a href="#fn:abi" class="footnote" rel="footnote">1</a></sup> and `T` is either a scalar type such as an integer or a pointer type, or a class\[^calls\] such that:

  - It has a non-deleted copy constructor or move constructor.
  - All copy and move operations are trivial – one requirement is that they must either be omitted or explicitly defaulted ([Tip \#131](/tips/131)).
  - The destructor is trivial and non-deleted.

  For types that your team does not own\[^hyrum\], you should only rely on this behavior if they explicitly document that they should be passed by value, such as `spanner::Database` and `absl::Duration`.

- `std::optional<T>`, where passing `T` by value applies.

  `std::optional<T>` adds some size overhead compared to `T`, which further limits the types that can be passed by value efficiently. So, for instance, `std::optional<std::span<U>>` and `std::optional<absl::string_view>` are too big, as each of these wrapped types is 16 bytes before accounting for `std::optional`’s overhead.

  If `sizeof(std::optional<T>) > 16`, or if `T` has a nontrivial copy constructor, then prefer passing `absl::Nullable<const T*>` ([Tip \#163](/tips/163)), and use a null pointer to represent the case that would otherwise be captured by `std::nullopt`.

  Note that [Tip \#163](/tips/163) applies here – if all callers will always have a `std::optional<T>`, then you may pass by `const&`.

  Do not use this idiom with smart pointers or other types that have a representation for “no value”. For instance, do not write `std::optional<std::unique_ptr<U>>`; instead, prefer to use `std::unique_ptr<U>` directly, and pass a null pointer to represent “no value”.

### Pass by Reference or by Pointer

Note: If an argument `x` in a call `f(x)` is required to outlive the function call, [do not pass it by reference](https://google.github.io/styleguide/cppguide.html#Inputs_and_Outputs).

The types listed below should usually be passed by reference (for required parameters) or by pointer (for optional parameters).

- Smart pointers (e.g., `std::unique_ptr<T>`) where you don’t want to transfer ownership: dereference the smart pointer to pass `const T&` if the pointed-at value is always known (and required) to be non-null; else pass `absl::Nullable<const T*>` ([Tip \#188](/tips/188)).

  In cases of shared ownership\[^shared_ptr\] where you only *sometimes* want to take ownership, you may want to pass a reference to the `std::shared_ptr` to avoid the slight overhead of updating reference counts.

- Containers that store their contents inline, e.g., `std::array<T, N>` and `absl::InlinedVector<T, N>`.

  While `std::array<T, N>` can be efficient to pass by value if `sizeof(T) * N <= 16`, `absl::InlinedVector<T, N>` has a non-trivial copy constructor and thus will never be passed in a register.

- Types with non-trivial copy constructors, where you don’t intend to use move semantics.

- Protocol buffers.

  You might think that the `Duration` type defined by

  ``` cpp

  edition = "2023";

  message Duration {
    int64 seconds = 1;
    int32 nanos = 2;
  }
  ```

  only contains an `int64` (8 bytes) and an `int32` (4 bytes) and is therefore 12 bytes (padded out to 16 bytes), but that’s not correct because protobufs may have a vtable pointer (8 bytes) or other metadata. Additionally, you shouldn’t pass protos by value by default (even if they don’t have many fields) because they do not promise that they can be trivially copied (and in practice they usually cannot).

### Pass a View (by Value)

For some types, a corresponding *view* type – a type that gives read-only access to the underlying data, and might support various different underlying types – can be a good way to accept inputs to a function that does not need its own copy of those inputs.

- For functions accepting a string argument, whether as `std::string`, `absl::string_view`, or `const char*`, defining the parameter as an `absl::string_view` is efficient and supports all of these inputs types (see [Tip \#179](/tips/179)).

- For functions accepting a `std::vector<T>`, defining the parameter as an `absl::Span<const T>` is more efficient and more flexible (see [Tip \#93](/tips/93)), though using `const std::vector<T>&` can be a reasonable choice if constraints make `absl::Span` impractical.

- For functions that accept a callable object, such as a lambda, we can choose between defining a function parameter as `const Fn&` (where `Fn` is a template parameter) or as a type-erased callable such as `absl::FunctionRef` (see [Tip \#145](/tips/145)).

## Closing Words

While passing function parameters by `const&` is a good default choice, there are plenty of cases where it’s not the best option. The guidelines in this tip can help to weigh the relevant factors and design safe and efficient APIs.

We want to emphasize that they are just guidelines, though, and if you have good reason to deviate from these (e.g., benchmarking or profiling identifies potential performance gains), we encourage you to do so (and to document your rationale for the next reader).


