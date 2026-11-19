---
type: source
source-type: web
title: "Tip of the Week #124: `absl::StrFormat()`"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/124
summary: "abseil C++ Tips of the Week #124: absl::StrFormat()."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 79d96159473b17447c23e65a14ac422f
---

> 原文：<https://abseil.io/tips/124> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#124: `absl::StrFormat()`

\
\

Originally posted as TotW \#124 on October 11, 2016

Updated 2022-11-16

Quicklink: [abseil.io/tips/124](https://abseil.io/tips/124)

## The `str_format` Library and `absl::StrFormat()`

After a long testing and development period, we’re pleased to announce that the `str_format` library is now generally available. The `str_format` library is a very efficient, typesafe, and extensible library that implements all `printf` formatting syntax. Nearly all `printf`-style conversions can be trivially upgraded to `absl::StrFormat()`. For more detailed documentation, see https://abseil.io/docs/cpp/guides/format. It’s the best option for printf-style formatting, but no position is taken here on where printf-style is or isn’t appropriate.

Usage is simple. Add a BUILD dependency on `//third_party/absl/strings:str_format`, and include the header:

```cpp

#include "absl/strings/str_format.h"
```

Most users will interact with the `str_format` library simply by calling `absl::StrFormat()` just as they’d call `StringPrintf()` or `util::format::StringF()` in the past. There are also `StrAppendFormat()` and `StreamFormat()` variants.

```cpp

std::string s = absl::StrFormat("%d %s\n", 123, "hello");
```

Unlike the C library’s `printf()`, the correctness of `absl::StrFormat()` conversions doesn’t rely on callers encoding the exact types of arguments into the format string. With `printf()` this must be carefully done with length modifiers and conversion specifiers, such as `%llu` encoding the type `unsigned long long`. But `absl::StrFormat()` is written in C++, so it uses templates and overloading to safely work directly with types in the caller’s argument list. In `absl::StrFormat()`, a format conversion specifies a broader C++ conceptual category instead of an exact type. For example, `%s` binds to any string-like argument, so `std::string`, `absl::string_view`, `Cord`, and `const char*` are all accepted. Likewise, `%d` accepts an integer-like argument, etc. It can be further extended for basic user-defined types (though we’d like to manage the extensions for now). It ignores length modifiers like `ll` and formats any usable value. For example, clients do not have to unnecessarily hardcode the types of the data members of `x` here:

```cpp

  X x = project_x::GetStats();
  LOG(INFO) << absl::StreamFormat("%s:%08x", x.name, x.size);
```

The `name` can be anything string-like, and `size` can be any integer-like type. This decoupling is great for the maintainers of `project_x`.

We can also control the destination much more smoothly with the `str_format` library. In the `printf()` family, there was `fprintf()` for `FILE*` output, `sprintf()` for writing to a buffer, `asprintf()` for writing to allocated memory, or the (now deprecated) usage of `StringPrintf()` (with wasteful multiple calls to `vsnprintf()`). The `str_format` library uses an abstract sink, so the destination can be customized without loss of efficiency. As built-ins, we have `absl::StrFormat()` to produce a new `std::string`, `absl::StrAppendFormat()` to append to a `std::string`, and `absl::StreamFormat()` to write to a `std::ostream` (such as for logging).

Under the clang compiler, compile-time checking is performed on literal format strings. In the uncommon case of format strings determined at runtime, the format string must be parsed and checked against an argument list specification for compatibility before it can be used. This eliminates a danger of traditional `printf()` when using runtime formats. This ability to produce parsed format specifiers (similar to how regular expressions can be compiled into `RE` objects) can yield a performance boost, so in performance-sensitive code it may be used even with statically-determined format strings.

There are a few notable differences from `printf()` (see https://abseil.io/docs/cpp/guides/format). We try in the `str_format` library to be flexible without information loss. If a signed argument is formatted with an unsigned conversion like `%u` or `%x`, we convert the argument to the corresponding unsigned integer type before formatting, so printing negatives with `%u` may work differently from one’s expectations on this previously undefined behavior.

Best of all, it is highly optimized and much faster than `sprintf()` or the deprecated `StringPrintf()` (see [format-shootout](https://docs.google.com/a/google.com/spreadsheets/d/1-pEDOge3DzXiyEoO9xC2JJxL4Ybf-XdPu1nXzBiUsAM "Format shootout results")). Please give this library a try anywhere you’d use printf-style formatting.

### Examples

I’ll close with a few examples.

```cpp

#include "absl/strings/str_format.h"

absl::StrAppendFormat(&s, "Also, %s\n", epilogue);

// Logs something like: "billydonahue         12345.67"
// When formatting streamed output, prefer `absl::StreamFormat()` instead of
// stream I/O manipulators like `std::setw`.
// See https://google.github.io/styleguide/cppguide.html#Streams for more information.
for (const auto& g : hard_workers)
  LOG(INFO) << absl::StreamFormat("%-20s %8.2f", g.username, g.bonus);

// POSIX positional specifiers (yields "veni, vidi, vici!").
summary = absl::StrFormat("%2$s, %3$s, %1$s!", "vici", "veni", "vidi");

std::string letter = response.format_string();  // known only at runtime
// Reject unacceptable form letters.
auto format = absl::ParsedFormat<'d', 's', 's'>::New(letter);
if (!format) {
  // ... error case ...
  return;
}
letter = StringF(*format, vacation_days, from, to);

// Precompile for performance. Yields, e.g., rows like:
//   "<tr><td>alice</td><td>00000123</td></tr>\n"
//   "<tr><td>bob</td><td>00004567</td></tr>\n"
static const auto* const pfmt = new absl::ParsedFormat<'s','d'>(
    "<tr><td>%s</td><td>%08d</td></tr>\n");
for (const auto& joe : folks) {
  absl::StrAppendFormat(&output, *pfmt, joe.name, joe.id);
}
// The 'FormatStreamed' adaptor can be used to format any ostream-formattable
// 'x'.
s = absl::StrFormat("[%-12s]", absl::FormatStreamed(x));
```


