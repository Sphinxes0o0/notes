---
type: source
source-type: web
title: "Tip of the Week #1: `string_view`"
author: "Michael Chastain"
date: 2012
url: https://abseil.io/tips/1
summary: "abseil C++ Tips of the Week #1: string_view."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 6454742b4f3ed0d527f530a14a0b474d
---

> 原文：<https://abseil.io/tips/1> · 作者：Michael Chastain · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#1: `string_view`

\
\

Originally posted as TotW \#1 on April 20, 2012

*By [Michael Chastain](/cdn-cgi/l/email-protection#9ff2fafcb1fbfaecf4ebf0efdff8f2fef6f3b1fcf0f2)*

Updated 2020-08-18

Quicklink: [abseil.io/tips/1](https://abseil.io/tips/1)

## What’s a `string_view`, and Why Should You Care?

When creating a function to take a (constant) string as an argument, you have three common alternatives: two that you already know, and one of which you might not be aware:

```cpp

// C Convention
void TakesCharStar(const char* s);

// Old Standard C++ convention
void TakesString(const std::string& s);

// string_view C++ conventions
void TakesStringView(absl::string_view s);    // Abseil
void TakesStringView(std::string_view s);     // C++17
```

The first two cases work best when a caller has the string in the format already provided, but what happens when a conversion is needed (either from `const char*` to `std::string` or `std::string` to `const char*`)?

Callers needing to convert a `std::string` to a `const char*` need to use the (efficient but inconvenient) `c_str()` function:

```cpp

void AlreadyHasString(const std::string& s) {
  TakesCharStar(s.c_str());               // explicit conversion
}
```

Callers needing to convert a `const char*` to a `std::string` don’t need to do anything additional (the good news) but will invoke the creation of a (convenient but inefficient) temporary string, copying the contents of that string (the bad news):

```cpp

void AlreadyHasCharStar(const char* s) {
  TakesString(s); // compiler will make a copy
}
```

## What to Do?

Google’s preferred option for accepting such string parameters is through a `string_view`. This is a “pre-adopted” type from C++17 - for now, use `absl::string_view` even if `std::string_view` is available.

An instance of the `string_view` class can be thought of as a “view” into an existing character buffer. Specifically, a `string_view` consists of only a pointer and a length, identifying a section of character data that is not owned by the `string_view` and cannot be modified by the view. Consequently, making a copy of a `string_view` is a shallow operation: no string data is copied.

`string_view` has implicit conversion constructors from both `const char*` and `const std::string&`, and since `string_view` doesn’t copy, there is no O(n) memory penalty for making a hidden copy. In the case where a `const std::string&` is passed, the constructor runs in O(1) time. In the case where a `const char*` is passed, the constructor invokes a `strlen()` automatically (or you can use the two-parameter `string_view` constructor).

```cpp

void AlreadyHasString(const std::string& s) {
  TakesStringView(s); // no explicit conversion; convenient!
}

void AlreadyHasCharStar(const char* s) {
  TakesStringView(s); // no copy; efficient!
}
```

Because the `string_view` does not own its data, any strings pointed to by the `string_view` (just like a `const char*`) must have a known lifespan, and must outlast the `string_view` itself.

This means that using `string_view` for storage is often questionable: you need some proof that the underlying data will outlive the `string_view`. For example, the following struct probably doesn’t make sense if it might be stored beyond the result of a function call that accepts it as a parameter:

```cpp

struct TestScore {
  absl::string_view username;  // Probably should be a `std::string`
  double score;
};
```

If your API only needs to reference the string data during a single call, and doesn’t need to modify the data, accepting a `string_view` is sufficient.

If you need to use the data later or modify the data, you can explicitly convert to a C++ string object using `std::string(my_string_view)`. Another option, discussed in [Tip \#117](/tips/117), is to pass a `std::string` by value and use `std::move` in callers when applicable.

Adding `string_view` into an existing codebase is not always the right answer: changing parameters to pass by `string_view` can be inefficient if those are then passed to a function requiring a `std::string` or a NUL-terminated `const char*`. It is best to adopt `string_view` starting at the utility code and working upward, or with complete consistency when starting a new project.

## A Few Additional Notes

- Unlike other string types, you should pass `string_view` by value just like you would pass an int or a double because `string_view` is a small value.

- Marking a `string_view` as `const` only affects whether the `string_view` object itself can be modified, and not whether it can be used to modify the underlying chars – it never can. This is exactly analogous to how a `const char*` can never be used to modify the chars, even if the pointer itself can be modified.

- For function parameters, don’t qualify `string_view` with `const` in function declarations (see [Tip \#109](/tips/109)). You may use `const` to qualify `string_view` in function definitions at your (or your team’s) discretion, e.g., to be consistent with the surrounding code ([Tip \#109](/tips/109)). For other local variables, using `const` is neither encouraged nor discouraged (https://google.github.io/styleguide/cppguide.html#Use_of_const).

- `string_view` is not necessarily NUL-terminated. Thus, it’s not safe to write:

  ``` cpp

      printf("%s\n", sv.data()); // DON’T DO THIS
  ```

  Prefer this instead (see [Tip \#124](/tips/124)):

  ``` cpp

      absl::PrintF("%s\n", sv);
  ```

- You can log a `string_view` just like you would a string or a `const char*` :

  ``` cpp

      LOG(INFO) << "Took '" << sv << "'";
  ```

- You can convert an existing routine that accepts `const std::string&` or NUL-terminated `const char*` to `string_view` safely in most cases. The only danger we have encountered in performing this operation is if the address of the function has been taken, this will result in a build break as the resulting function-pointer type will be different.

- `string_view` has a constexpr constructor and a trivial destructor; keep this in mind when using in static and global variables (see [the style guide](https://google.github.io/styleguide/cppguide.html#Static_and_Global_Variables)) or constants (see [Tip \#140](/tips/140)).

- A `string_view` is an effective reference and may not be the best choice for member variables (also see [Tip \#180](/tips/180)).


