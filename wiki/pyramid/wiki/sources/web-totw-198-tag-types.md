---
type: source
source-type: web
title: "Tip of the Week #198: Tag Types"
author: "Alex Konradi"
date: 2012
url: https://abseil.io/tips/198
summary: "abseil C++ Tips of the Week #198: Tag Types."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: b0aa9269c5c7846e68bfe1f8bb77799f
---

> 原文：<https://abseil.io/tips/198> · 作者：Alex Konradi · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#198: Tag Types

\
\

Originally posted as TotW \#198 on August 12, 2021

*By [Alex Konradi](/cdn-cgi/l/email-protection#e5848e8a8b9784818ca5828a8a828980cb868a88)*

Updated 2022-01-24

Quicklink: [abseil.io/tips/198](https://abseil.io/tips/198)

Suppose we have a class `Foo`:

```cpp

class Foo {
 public:
  explicit Foo(int x, int y);
  Foo& operator=(const Foo&) = delete;
  Foo(const Foo&) = delete;
};
```

`Foo` is neither movable nor copyable, but it is constructible, e.g. `Foo f(1, 2);`. Since it has a public constructor, we can easily make an instance wrapped in a `std::optional`:

```cpp

std::optional<Foo> maybe_foo;
maybe_foo.emplace(5, 10);
```

That’s great, but what if the `std::optional` is declared `const`, so we can’t call `emplace()`? Luckily for us, `std::optional` has a constructor for this:

```cpp

// Pass std::in_place as the first argument, followed by the arguments for Foo's
// constructor.
const std::optional<Foo> maybe_foo(std::in_place, 5, 10);
```

Wait, what’s going on with `std::in_place`? If we look at [the documentation](https://en.cppreference.com/w/cpp/utility/optional/optional) for `std::optional` construction, we can see that one of the overloads takes a `std::in_place_t` as the first argument, along with a list of additional arguments. Since [`std::in_place`](https://en.cppreference.com/w/cpp/utility/in_place) is an instance of `std::in_place_t`, the compiler chooses the *emplacing constructor*, which instantiates `Foo` within the `std::optional` by forwarding the rest of the arguments to `Foo`’s constructor.

If we look a little closer at the documentation for `std::in_place_t`, we see that it’s… an empty struct. No special qualifiers or magic declarations. The only thing even mildly special about it is that the standard library includes a named instance of it, `std::in_place`.

## Overload Resolution Via Tag Types

`std::in_place_t` is a member of a loose category of classes sometimes referred to as “tag types”. The function of these classes is to pass information to the compiler by “tagging” specific overloads in an overload set. By providing an instance of an appropriate tag class to an overloaded function (often a constructor), we can use the compiler’s ordinary resolution rules to make it select the desired overload. In the case of our `std::optional` construction, the compiler sees that the first argument is of type `std::in_place_t` and so chooses the matching emplacing constructor.

Though `std::in_place_t` was introduced in C++17, the use of empty classes for tagging overloads in the standard library has been prevalent since [`std::piecewise_construct_t`](https://en.cppreference.com/w/cpp/utility/piecewise_construct_t), was introduced in C++11 to select the emplacing constructor for `std::pair`. C++17 significantly expanded the set of tag types in the standard library.

## Templates, of Course

Besides disambiguating overloads, another common use case for tag types is to pass type information to templated constructors. Consider these two structs:

```cpp

struct A { A(); /* internal members */ };
struct B { B(); /* internal members */ };
```

Let’s try to construct an instance of [`std::variant<A, B>`](https://en.cppreference.com/w/cpp/utility/variant) with each:

```cpp

// These work if A and B are copy- or move-constructible, but incur the
// performance cost of an extra copy or move construction.
std::variant<A, B> with_a{A()};
std::variant<A, B> with_b{B()};

// These aren't valid C++; the language doesn't support providing constructor
// template parameters explicitly.
std::variant<A, B> try_templating_a<A>{};
std::variant<A, B><B> try_templating_b{};
```

What we need is a way to tell the `std::variant` constructor that we want to instantiate `A` or `B` without actually providing an instance of either. For that, we can use [`std::in_place_type`](https://en.cppreference.com/w/cpp/utility/in_place)!

```cpp

std::variant<A, B> with_a{std::in_place_type<A>};
std::variant<A, B> with_b{std::in_place_type<B>};
```

`std::in_place_type<T>` is an instance of the class template `std::in_place_type_t<T>`, which is (unsurprisingly, at this point) empty. By passing a value of type `std::in_place_type_t<A>` to `std::variant`’s constructor, the compiler can deduce that the constructor template parameter is our class `A`.

## Usage

Tag types show up occasionally when interacting with generic class templates, especially ones from the standard library. One of the shortcomings of tag types is that other techniques, such as factory functions, often result in more readable code. Take the following example:

```cpp

// This tag spelling requires the reader to know how std::optional interacts
// with std::in_place.
std::optional<Foo> with_tag(std::in_place, 5, 10);

// Here the intent is clearer: make an optional Foo by providing these arguments.
std::optional<Foo> with_factory = std::make_optional<Foo>(5, 10);
```

These two `std::optional<Foo>` objects are guaranteed to be constructed identically thanks to C++17’s [mandatory copy elision](/tips/166).

So why use tags? Because factory functions don’t always work:

```cpp

// This doesn't work because Foo isn't move-constructible.
std::optional<std::optional<Foo>> foo(std::make_optional<Foo>(5, 10));
```

The above example doesn’t compile because `Foo`’s move constructor is deleted. To make this work, we use `std::in_place` to select the `std::optional` constructor that forwards the remaining arguments.

```cpp

// This constructs everything in place, resulting in a single call to Foo's
// constructor.
std::optional<std::optional<Foo>> foo(std::in_place, std::in_place, 5, 10);
```

In addition to working in places where factory functions don’t, tag types have some other nice properties:

- they are [literal types](https://en.cppreference.com/w/cpp/named_req/LiteralType) which means we can declare `constexpr` instances, even in header files, like `std::in_place`;
- because they are empty, the compiler can optimize them out, resulting in zero runtime overhead.

Though they’re used in the standard library, encountering empty tag types in the wild is relatively uncommon. If you find yourself using one, consider adding a comment to help your readers:

```cpp

std::unordered_map<int, Foo> int_to_foo;
// std::piecewise_construct is a tag for overload resolution of std::pair's
// constructor. Emplaces 100 -> Foo(5, 10) in the map.
int_to_foo.emplace(std::piecewise_construct,
                   std::forward_as_tuple(100),
                   std::forward_as_tuple(5, 10));
```

## Conclusion

Tag types are a powerful way to give additional information to the compiler. While at first glance they might seem magical, they use the same overload resolution and template type deduction rules as the rest of C++. The standard library uses class tags for disambiguating constructor calls, and you can use the same mechanisms to define tags for your own needs.

## See Also

- [std::integer_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence) for compile-time indexing of tuples
- [passkey for std::make_shared](/tips/134#what-about-stdshared-ptr) uses tags to control access


