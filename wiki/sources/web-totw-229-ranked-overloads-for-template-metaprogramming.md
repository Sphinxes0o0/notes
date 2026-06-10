---
type: source
source-type: web
title: "Tip of the Week #229: Ranked Overloads for Template Metaprogramming"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/229
summary: "abseil C++ Tips of the Week #229: Ranked Overloads for Template Metaprogramming."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 54f7d85b0c34586e253e9b2d27c67785
---

> 原文：<https://abseil.io/tips/229> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#229: Ranked Overloads for Template Metaprogramming

\
\

Originally posted as TotW \#229 on February 5, 2024

*By [Miguel Young de la Sota](/cdn-cgi/l/email-protection#8ce1eff5e3f9e2ebcce1e5f8a2e9e8f9) and [Matt Kulukundis](/cdn-cgi/l/email-protection#412a272c01262e2e262d246f222e2c)*

Updated 2024-02-20

Quicklink: [abseil.io/tips/229](https://abseil.io/tips/229)

Warning: This is an advanced tip for folks doing template metaprogramming. In general, avoid template metaprogramming unless you have a very, very good reason. If you are reading this, it’s because you need to do some template metaprogramming or just want to learn something nifty.

## One Cool Trick

Ordinarily, C++ requires every function invocation to resolve to a single “best” function or it produces an ambiguity error. The exact definition of “best” is more complex than we want to go into, but involves things like implicit conversions and type qualifiers.

In situations that would produce ambiguity errors, we can use explicit class hierarchies to force the definition of “best” to be what we prefer. This “ranked overloads” technique uses structures with a class hierarchy so they have a priority ordering and the compiler will select the highest priority method first. We’ll define a family of empty [tag types](/tips/198) `Rank0`, `Rank1`, etc., that are related by inheritance, and use those to guide the overload resolution process.<sup><a href="#fn:rank" class="footnote" rel="footnote">1</a></sup>

```cpp

// Public API with good comments.
template <typename T>
size_t Size(const T& t);

// Everything below here is a working example of ranked overloads, that
// you can copy and paste to get you started!
namespace internal_size {

// Use [Tip #229](/tips/229) for dispatching.
struct Rank0 {};
struct Rank1 : Rank0 {};
struct Rank2 : Rank1 {};
struct Rank3 : Rank2 {};

template <typename T>
size_t SizeImpl(Rank3, const std::optional<T>& x) {
  return x.has_value() ? Size(*x) : 0;
}

template <typename T>
size_t SizeImpl(Rank3, const std::vector<T>& v) {
  size_t res = 0;
  for (const auto& e : v) res += Size(e);
  return res;
}

template <typename T>
size_t SizeImpl(Rank3, const T& t)
  requires std::convertible_to<T, absl::string_view>
{
  return absl::string_view{t}.size();
}

template <typename T>
size_t SizeImpl(Rank2, const T& x)
  requires requires { x.length(); }
{
  return x.length();
}

template <typename T>
size_t SizeImpl(Rank1, const T& x)
  requires requires { x.size(); }
{
  return x.size();
}

template <typename T>
size_t SizeImpl(Rank0, const T& x) { return 1; }

}  // namespace internal_size

template <typename T>
size_t Size(const T& t) {
  // Start with the highest rank, Rank3.
  return internal_size::SizeImpl(internal_size::Rank3{}, t);
}

auto i = Size("foo");                      // hits the string_view overload
auto j = Size(std::vector<int>{1, 2, 3});  // hits the vector overload
auto k = Size(17);                         // hits the lowest rank "catch all"
```

Note that the `absl::string_view`, `std::optional`, and `std::vector` overloads use `Rank3`. When overloads are mutually incompatible (the call *can’t* be ambiguous by construction), the same rank type can be used. You can think of all overloads with the same rank as being tried in parallel.

NOTE: The astute reader may wonder why the `absl::string_view` overload is declared as a template. Doing so ensures that no implicit conversions will take place in the signature other than the one for the rank structs. If this overload were declared with an `absl::string_view` parameter then the call would be ambiguous: `Rank2{}` -\> `Rank0{}` would count as a conversion but `const char[]` to `absl::string_view` would also and the call would become [ambiguous again](https://godbolt.org/#z:OYLghAFBqd5QCxAYwPYBMCmBRdBLAF1QCcAaPECAMzwBtMA7AQwFtMQByARg9KtQYEAysib0QXACx8BBAKoBnTAAUAHpwAMvAFYTStJg1DIApACYAQuYukl9ZATwDKjdAGFUtAK4sGe1wAyeAyYAHI%2BAEaYxCBmAJykAA6oCoRODB7evnrJqY4CQSHhLFEx8baY9vkMQgRMxASZPn5cFVXptfUEhWGR0bEJCnUNTdmtQ109xaUDAJS2qF7EyOwc5gDMwcjeWADUJuseidViB9gmGgCCG1s7mPuHQ8TBwAD6AG54mADuZxfXZk2DG2Xj2BzcTxefyuN2BdwebgIAE9EphXgRiExCApoQCgSCwYd3pgHCRcf8APQU3bKLwRWh4ZC7S7KACSu2%2BhAQu2AqAwuzQLDYggUADp/gRMCxEgZJQjkajmGxdgAVXGpABeaIIuyEeC1EDQDCGqvMADZdgRZgcrDCrkrMApEkwVrtgpLiMxaK9NfcTAB2W2XKm7RT3XkUzEMADWmHQAFpUMTiLRUEx0ApdvxiLt8E6mARkAgXuKrk8vA5dgAlQzRjT7QMBgAiNv%2B5crNZjXF2IGrtfrAas/pb6yD7Z1nejZh7fa7DaHI7HGIrE9r6xnk%2B7g%2Bbrbtl0l0tlfsOCsYrHuavW5zL%2Bu1utvrMPEEn61IAoEJqG6BAIFQx3SpyHJe5xmBaqizPO/y7LsxCYAQSwMLsqiiggTAKB8YheJgEAQQcABi94GgAVOBM4aLu1zDv8EpSjKBbHoiKJnsqwFtre6KEZgj4ys%2Ba5vkan4EN%2BIDEqSxDgqxoG7O8uGNlc0G%2BhxsGZgcTa7ORo5QVmJC7IaH46kwXhEOauz3L2MkwY6%2ByWKpnEQJg1qafJlnwZ6lk4k5lEtnuik6nqWrcbQvExq%2Buxfj%2BkJGB8XzfJaslBtBsGuYhBCir6OEUTue4HnRcrgqeDqmlebFahx/lcU%2Bk5mPx%2BmmlJ4FabBACOXh4MplktW1VmDkhor0EYBAIBlo4Nt5lEJS5CG9f1wCDcNQZZdcVw5Ue8pMYVrE3qVfkPpVtatO%2Bxo6mq9XWs5zWte1F1dSpga9eljkWKN1FyZciVwVNyEPZlVHZbRq35et55Fdely%2BZxgXBXWNVHXVYHxZNblcDaz17s20Ehg6%2Bauu60Rej6t7Uct/30WtirA5tYPsTtBoCcdJlWpBzkhp0DQclyloIPcxbAFzJpRtGjUfW5uOemIBNaj%2B5WQ6L%2BO%2Bj%2BL7bsOb5Wj9Y3/IZRBug8anlRA5hmPwqAG490Fm%2BbFuWxj1LFgQmaDfckVvJ8Py7Em0SpumGtGaguzaDrdnhSJJJEOJhzun8gYHdVuzrM2pu7CGtv21z0khzp7spmm6De1r0YB3rXD%2BgnVul6XSfYpz9ypt8jo6gL1lmKIhbcmItAGxw8y0JwACsvB%2BBwWikKgnBuNY1hhYsyx%2BoCPCkAQmid/M0YgD3XCimYPc9/EAAc6zrP6XAH2Y/r6Jwkj94vw%2BcLwCggBo8%2BL/McCwDAiAoKg0p0NE5CUIKiTfxiNsQwbxlwxj4HQD0d8IARCvhEYI9QkScDnvA5gxAkQAHkIjaBDsg3ggphQEAwQwWgSDB68CwBELwwA3BtzvtwChUoQHiAYaQfAsEHB4GJPQoemBVAkiMqsOeuNu7kP0HgCImJ0EeCwFfDEeAWB4PmFQAwwAFAADUYoYMVHgmQggRBiHYFIPR8glBqCvroVoBgjAoHHpYcREQ76wAdCAJgjjMB0FIMmEAYDoyzHmH%2Bao9D4xflUqYGylgzD1l4JnZ4WAnE4TaCHdILgGDuE8M0fwaSph9BiK0XIaQBCjBaEkFIhSGA5JKP0cYlRkkCFZo0DJYwkmcPqcMbowRehVLybYdpxS9ATAaJUmYXB5gKCnisCQXde6XzESPDgSEd5mnjGaSQAprHAF0r4iCEBcCEB0hsUZvAF7kP8aQFePcH6iIvqQRRlzSADyHvM2%2B99H6nNIC/d%2BiwCCJCMr/PSX96DEFCOeTgqglkrLWcAowWziBeBjLMXgcZ9lxL0PwfRohxDGPRaYlQ6gxGWNIN8TEiQlFnw4H3B5V95kYKMr8nUqAqCLOWas9ZIDYXwr8bpDwgLojWXWEct5Wgzlc3TP0RJ1zeB3Ifo8mJN9bCvJOcK5eIBJA71FP6SQkh/QaC4GaM0Zglkn1fKI9YsynnyqVUvclZhzVyo4Mcp%2B8xkypGcJIIAA%3D%3D).

## Detailed Example

Let’s suppose we want `Size(x)` to return `x.length()`, `x.size()`, or `1` depending on what the passed type `x` implements. The naive approach does not work:

```cpp

template <typename T>
size_t Size(const T& x)
  requires requires { x.length(); }
{
  return x.length();
}

template <typename T>
size_t Size(const T& x)
  requires requires { x.size(); }
{
  return x.size();
}

template <typename T>
size_t Size(const T& x) { return 1; }

auto i = Size(std::string("foo"));  // Ambiguous.
```

Because the size and length overloads are of equal rank, they are equally good matches for the call. Because overload resolution does not eliminate all but one candidate, the compiler declares the callsite ambiguous. There are clever tricks using variadic functions or `int`/`long` promotion to create an ordering for two options, but these do not scale to having N descending ranks of overloads.

Using ranked overloads as we’ve suggested attaches *explicit ranks* in the form of inheritance to specific overloads. This rank is based on the following rule: overloads with more derived classes have higher rank than overloads with less specific ones. That is, if two overloads differ by a single argument’s type, and both are bases of the argument, the type closest in the inheritance hierarchy has higher rank and is a better match.

This means we can build a tower of empty structs, each deriving from the previous, to put an *explicit, numeric rank* on each overload. Using this trick, we would write `Size` like this:

```cpp

// Public API with good comments.
template <typename T>
size_t Size(const T& t);

namespace internal_size {

// Use go/ranked-overloads for dispatching.
struct Rank0 {};
struct Rank1 : Rank0 {};
struct Rank2 : Rank1 {};

template <typename T>
size_t SizeImpl(Rank2, const T& x)
  requires requires { x.length(); }
{
  return x.length();
}

template <typename T>
size_t SizeImpl(Rank1, const T& x)
  requires requires { x.size(); }
{
  return x.size();
}

template <typename T>
size_t SizeImpl(Rank0, const T& x) { return 1; }

}  // namespace internal_size

template <typename T>
size_t Size(const T& t) {
  // Start with the highest rank
  return internal_size::SizeImpl(internal_size::Rank2{}, t);
}

auto i = Size(std::string("foo"));  // 3
```

The overloads can now be read as an `if`/`else` chain. First we try the `Rank2` overload; if substitution fails, we fall back to the next rank, `Rank1`, and then `Rank0`. Of course, this particular method will treat `Size(std::string("foo"))` differently from `Size("foo")`. This highlights some of the dangers of generic programming, though the fix is relatively straightforward: add an explicit rank to handle strings, as below.

```cpp

// Public API with good comments.
template <typename T>
size_t Size(const T& t);

namespace internal_size {
// Use go/ranked-overloads for dispatching.
struct Rank0 {};
struct Rank1 : Rank0 {};
struct Rank2 : Rank1 {};
struct Rank3 : Rank2 {};

template <typename T>
size_t SizeImpl(Rank3, const T& t)
  requires std::convertible_to<T, absl::string_view>
{
  return absl::string_view{t}.size();
}

template <typename T>
size_t SizeImpl(Rank2, const T& x)
  requires requires { x.length(); }
{
  return x.length();
}

template <typename T>
size_t SizeImpl(Rank1, const T& x)
  requires requires { x.size(); }
{
  return x.size();
}

template <typename T>
size_t SizeImpl(Rank0, const T& x) { return 1; }

}  // namespace internal_size

template <typename T>
size_t Size(const T& t) {
  // Start with the highest rank
  return internal_size::SizeImpl(internal_size::Rank3{}, t);
}

auto i = Size("foo");  // 3
```

Now extending this to `vector` and `optional` is quite straightforward!

```cpp

// Public API with good comments.
template <typename T>
size_t Size(const T& t);

namespace internal_size {
// Use go/ranked-overloads for dispatching.
struct Rank0 {};
struct Rank1 : Rank0 {};
struct Rank2 : Rank1 {};
struct Rank3 : Rank2 {};

template <typename T>
size_t SizeImpl(Rank3, const std::optional<T>& x) {
  return x.has_value() ? Size(*x) : 0;
}

template <typename T>
size_t SizeImpl(Rank3, const std::vector<T>& v) {
  size_t res = 0;
  for (const auto& e : v) res += Size(e);
  return res;
}

template <typename T>
size_t SizeImpl(Rank3, const T& t)
  requires std::convertible_to<T, absl::string_view>
{
  return absl::string_view{t}.size();
}

template <typename T>
size_t SizeImpl(Rank2, const T& x)
  requires requires { x.length(); }
{
  return x.length();
}

template <typename T>
size_t SizeImpl(Rank1, const T& x)
  requires requires { x.size(); }
{
  return x.size();
}

template <typename T>
size_t SizeImpl(Rank0, const T& x) { return 1; }

}  // namespace internal_size

template <typename T>
size_t Size(const T& t) {
  // Start with the highest rank
  return internal_size::SizeImpl(internal_size::Rank3{}, t);
}

auto i = Size("foo");                      // hits the string_view overload
auto j = Size(std::vector<int>{1, 2, 3});  // hits the vector overload
auto k = Size(17);                         // hits the lowest rank "catch all"
```

## Parting Thoughts

Now that you have learned this awesome power, please remember to use it sparingly. As we saw with the `absl::string_view` overload, generic programming is subtle and can lead to unexpected results.


