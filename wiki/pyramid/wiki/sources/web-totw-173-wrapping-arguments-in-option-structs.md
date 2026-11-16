---
type: source
source-type: web
title: "Tip of the Week #173: Wrapping Arguments in Option Structs"
author: "John Bandela"
date: 2012
url: https://abseil.io/tips/173
summary: "abseil C++ Tips of the Week #173: Wrapping Arguments in Option Structs."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 7fe5cc66109d0f016b085dd1612e41af
---

> 原文：<https://abseil.io/tips/173> · 作者：John Bandela · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#173: Wrapping Arguments in Option Structs

\
\

Originally posted as TotW \#173 on December 19, 2019

*By [John Bandela](/cdn-cgi/l/email-protection#e38981828d87868f82a3848c8c848f86cd808c8e)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/173](https://abseil.io/tips/173)

*It came without packages, boxes or bags. And he puzzled and puzzled ‘till his puzzler was sore.*

*-Dr. Seuss*

## Designated Initializers

Designated initializers are a C++20 feature that is available in most compilers today. Designated initializers make using option structs easier and safer since we can construct the options object in the call to the function. This results in shorter code and avoids a lot of temporary lifetime issues with option structs.

```cpp

struct PrintDoubleOptions {
  absl::string_view prefix = "";
  int precision = 8;
  char thousands_separator = ',';
  char decimal_separator = '.';
  bool scientific = false;
};

void PrintDouble(double value,
                 const PrintDoubleOptions& options = PrintDoubleOptions{});

std::string name = "my_value";
PrintDouble(5.0, {.prefix = absl::StrCat(name, "="), .scientific = true});
```

For more background on why option structs are helpful and the potential pitfalls in using them that designated initializers help avoid, read on.

## The Problem of Passing Many Arguments

Functions that take many arguments can be confusing. To illustrate, let us consider this function for printing out a floating point value.

```cpp

void PrintDouble(double value, absl::string_view prefix,  int precision,
                 char thousands_separator, char decimal_separator,
                 bool scientific);
```

This function provides us a lot of flexibility because it takes so many options.

```cpp

PrintDouble(5.0, "my_value=", 2, ',', '.', false);
```

The above code will print out: “my_value=5.00”.

However, it is hard to read this code and know to which parameter each argument corresponds. For instance, here we have inadvertently mixed up the order of our `precision` and `thousands_separator`.

```cpp

PrintDouble(5.0, "my_value=", ',', '.', 2, false);
```

Historically, we have used [argument comments](http://clang.llvm.org/extra/clang-tidy/checks/bugprone/argument-comment.html) to clarify argument meanings at call sites to reduce this sort of ambiguity. The addition of argument comments to the above example would allow ClangTidy to detect the error:

```cpp

PrintDouble(5.0, "my_value=",
            /*precision=*/2,
            /*thousands_separator=*/',',
            /*decimal_separator=*/'.',
            /*scientific=*/false);
```

However, argument comments still have several drawbacks:

- No enforcement: ClangTidy warnings are not caught at buildtime. Subtle errors (e.g. a missing `=` sign) can disable the check entirely with no warning, providing a false sense of security.
- Availability: not all projects and platforms support ClangTidy.

No matter whether your arguments are commented or not, specifying lots of options can also be tedious. Many times there are sensible defaults for the options. To address this concern, we can add defaults to the parameters.

```cpp

void PrintDouble(double value, absl::string_view prefix = "", int precision = 8,
                 char thousands_separator = ',', char decimal_separator = '.',
                 bool scientific = false);
```

Now we can call `PrintDouble` with less boilerplate.

```cpp

PrintDouble(5.0, "my_value=");
```

However, if we want to specify a non-default argument for `scientific`, we would still be forced to specify values for all of the parameters that come before it:

```cpp

PrintDouble(5.0, "my_value=",
            /*precision=*/8,              // unchanged from default
            /*thousands_separator=*/',',  // unchanged from default
            /*decimal_separator=*/'.',    // unchanged from default
            /*scientific=*/true);
```

We can address all of these issues by grouping all of the options together in an *option struct*:

```cpp

struct PrintDoubleOptions {
  absl::string_view prefix = "";
  int precision = 8;
  char thousands_separator = ',';
  char decimal_separator = '.';
  bool scientific = false;
};

void PrintDouble(double value,
                 const PrintDoubleOptions& options = PrintDoubleOptions{});
```

Now we can have names for our values, as well as flexibly use defaults.

```cpp

PrintDoubleOptions options;
options.prefix = "my_value=";
PrintDouble(5.0, options);
```

## Caveats

There are some issues with this solution, though. First is that we now have some extra boilerplate in passing options, though that’s often a minor cost compared to the benefits. But there are a few more things to consider.

### Lifetime of Temporaries

For example, when we took all the options as parameters the following code was safe:

```cpp

std::string name = "my_value";
PrintDouble(5.0, absl::StrCat(name, "="));
```

In the code above, we are creating a temporary `string` and binding a `string_view` to that. The temporary lifetime is the duration of the function call so we are safe, but using an options struct in the same manner, results in a dangling `string_view`.

```cpp

std::string name = "my_value";
PrintDoubleOptions options;
options.prefix = absl::StrCat(name, "=");
PrintDouble(5.0, options);
```

There are two ways we can fix this. The first is to simply change the type of `prefix` from `string_view` to `string`. The downside of doing this is that now the option struct is less efficient than directly passing the arguments. The other way that we can fix this is to add setter member functions.

```cpp

class PrintDoubleOptions {
 public:
  PrintDoubleOptions& set_prefix(absl::string_view prefix) {
    prefix_ = prefix;
    return *this;
  }

  absl::string_view prefix() const { return prefix_; }

  // Setters and getters for the other member variables.

 private:
  absl::string_view prefix_ = "";
  int precision_ = 8;
  char thousands_separator_ = ',';
  char decimal_separator_ = '.';
  bool scientific_ = false;
};
```

This can then be used to set the variables in the call.

```cpp

std::string name = "my_value";
PrintDouble(5.0, PrintDoubleOptions{}.set_prefix(absl::StrCat(name, "=")));
```

As you can see, the cost is that our option struct became a more complicated class with a lot more boilerplate.

The simpler alternative is to use [designated initializers](#designated-initializers) as shown at the top.

### Type Deduction

Designated initializers are often used with [copy list initialization](https://en.cppreference.com/w/cpp/language/list_initialization#Copy-list-initialization), where a brace-enclosed list of initializers doesn’t have an explicit type specified nearby.

When directly passing options to a function with the option struct as a parameter, the braced list is immediately turned into an argument of the specific type. So, this works well:

```cpp

PrintDouble(5.0, {.scientific=true})
```

But in a function like `std::make_unique` that uses “perfect forwarding”, where the type of the parameter must be deduced, the braced list’s type cannot be found. So, this does not work:

```cpp

class DoublePrinter {
  explicit DoublePrinter(const PrintDoubleOptions& options);
  ...
};

auto printer1 = std::make_unique<DoublePrinter>({.scientific=true});
```

The caller must name the option struct’s type, or there must be a helper factory function that does so.

```cpp

class DoublePrinter {
  static std::unique_ptr<DoublePrinter> Make(const PrintDoubleOptions& options);
  explicit DoublePrinter(const PrintDoubleOptions& options);
};

auto printer1 = std::make_unique<DoublePrinter>(
    PrintDoubleOptions{.scientific=true});
auto printer2 = DoublePrinter::Make({.scientific=true});
```

### Default Values in a Nested Type

If an option struct is associated with a class, it’s often reasonable to nest the struct within the class.

```cpp

class DoublePrinter {
  struct Options {
    int precision = 8;
    ...
  };

  explicit DoublePrinter(const Options& options);

  static std::unique_ptr<DoublePrinter> Make(const Options& options);
};
```

But then if you need to allow the option struct to be skipped entirely, such as when it’s being added to an existing class, and the nested struct has a default member initializer (the `= 8` after the field name `precision`, for example), you cannot have a [default argument](https://google.github.io/styleguide/cppguide.html#Default_Arguments) whose value leaves the field implicit.

In this case, provide another overload instead of using a default argument.

```cpp

class DoublePrinter {
  struct Options {
    int precision = 8;
    ...
  };

  static std::unique_ptr<DoublePrinter> Make() { return Make({}); }
  static std::unique_ptr<DoublePrinter> Make(const Options& options);

  explicit DoublePrinter() : DoublePrinter({}) {}
  explicit DoublePrinter(const Options& options);

  // Cannot do this:
  //   static std::unique_ptr<DoublePrinter> Make(const Options& options = {});
  //   explicit DoublePrinter(const Options& options = {});
};
```

## Conclusions

1.  For functions which take multiple arguments which may be confused by the caller or where you want to specify default arguments without having to worry about the order, strongly consider using option structs to increase both convenience and code clarity.

2.  When calling functions that take option structs, using designated initializers can result in shorter code as well as potentially avoiding temporary lifetime issues.

3.  Designated initializers by virtue of their conciseness and clarity further tip the balance towards preferring functions that take option structs over those that have many parameters.


