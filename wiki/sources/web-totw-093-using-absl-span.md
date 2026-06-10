---
type: source
source-type: web
title: "Tip of the Week #93: using absl::Span"
author: "Samuel Benzaquen"
date: 2012
url: https://abseil.io/tips/93
summary: "abseil C++ Tips of the Week #93: using absl::Span."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 654541b6b57566c30501de5ab7f49a48
---

> 原文：<https://abseil.io/tips/93> · 作者：Samuel Benzaquen · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#93: using absl::Span

\
\

Originally posted as TotW \#93 on April 23, 2015

*By [Samuel Benzaquen](/cdn-cgi/l/email-protection#2b58494e45514a6b4c44444c474e05484446)*

Updated 2023-05-08

Quicklink: [abseil.io/tips/93](https://abseil.io/tips/93)

At Google we are accustomed to using `string_view` as function parameters and return types when we want to deal with unowned strings. It can make the API more flexible and it can improve performance by avoiding unneeded conversions to `string`. ([Tip \#1](/tips/1))

`string_view` has a more generic cousin called `absl::Span` (google3/third_party/absl/types/span.h). Note that though `absl::Span` is similar in utility to `std::span`, available in C++ 20, the two types are not exchangeable.

`Span<const T>` is to `std::vector<T>` what `string_view` is to `string`. It provides a read-only interface to the elements of the vector, but it can also be constructed from non-vector types (like arrays and initializer lists) without incurring the cost of copying the elements.

The `const` can be dropped, so where `Span<const T>` is a view into an array whose elements can’t be mutated, `Span<T>` allows non-const access to the elements. Unlike spans of const, however, these require explicit construction.

## As Function Parameters

Some of the benefits of using `Span` as a function parameter are similar to those of using `string_view`.

The caller can pass a slice of the original vector, or pass a plain array. It is also compatible with other array-like containers, like `absl::InlinedVector`, `absl::FixedArray`, `google::protobuf::RepeatedField`, etc.

As with `string_view`, it is usually better to pass `Span` by value when used as a function parameter - this form is slightly faster, and produces smaller code.

Example:

```cpp

void TakesVector(const std::vector<int>& ints);
void TakesSpan(absl::Span<const int> ints);

void PassOnlyFirst3Elements() {
  std::vector<int> ints = MakeInts();
  // We need to create a temporary vector, and incur an allocation and a copy.
  TakesVector(std::vector<int>(ints.begin(), ints.begin() + 3));
  // No copy or allocations are made when using Span.
  TakesSpan(absl::Span<const int>(ints.data(), 3));
}

void PassALiteral() {
  // This creates a temporary std::vector<int>.
  TakesVector({1, 2, 3});
  // Span does not need a temporary allocation and copy, so it is faster.
  TakesSpan({1, 2, 3});
}
void IHaveAnArray() {
  int values[10] = ...;
  // Once more, a temporary std::vector<int> is created.
  TakesVector(std::vector<int>(std::begin(values), std::end(values)));
  // Just pass the array. Span detects the size automatically.
  // No copy was made.
  TakesSpan(values);
}
```

## Const Correctness for Vector of Pointers

A big problem with passing around `std::vector<T*>` is that you can’t make the pointees const without changing the type of the container.

Any function taking a `const std::vector<T*>&` will not be able to modify the vector, but it can modify the `T`s. This also applies to accessors that return a `const std::vector<T*>&`. You can’t prevent the caller from modifying the `T`s.

Common “solutions” include copying or casting the vector into the right type. These solutions are slow (for the copy) or undefined behavior (for the cast) and should be avoided. Instead, use `Span`.

### Example: Function Parameter

Consider these `Frob` variants:

```cpp

void FrobFastWeak(const std::vector<Foo*>& v);
void FrobSlowStrong(const std::vector<const Foo*>& v);
void FrobFastStrong(absl::Span<const Foo* const> v);
```

Starting with a `const std::vector<Foo*>& v` that needs frobbing, you have two imperfect options and one good one.

```cpp

// fast and easy to type but not const-safe
FrobFastWeak(v);
// slow and noisy, but safe.
FrobSlowStrong(std::vector<const Foo*>(v.begin(), v.end()));
// fast, safe, and clear!
FrobFastStrong(v);
```

### Example: Accessor

```cpp

class MyClass {
 public:
  // This is supposed to be const.
  // Don’t modify my Foos, pretty please.
  const std::vector<Foo*>& shallow_foos() const { return foos_; }
  // Really deep const.
  absl::Span<const Foo* const> deep_foos() const { return foos_; }

 private:
  std::vector<Foo*> foos_;
};
void Caller(const MyClass* my_class) {
  // Accidental violation of MyClass::shallow_foos() contract.
  my_class->shallow_foos()[0]->SomeNonConstOp();
  // This one doesn't compile.
  // my_class->deep_foos()[0]->SomeNonConstOp();
}
```

## Conclusion

When used appropriately, `absl::Span` can provide decoupling, const correctness and a performance benefit.

It is important to note that `Span` behaves much like `string_view` by being a reference to some externally owned data. All the same warnings apply. In particular, a `Span` must not outlive the data it refers to.


