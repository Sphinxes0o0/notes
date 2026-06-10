---
type: source
source-type: web
title: "Tip of the Week #64: Raw String Literals"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/64
summary: "abseil C++ Tips of the Week #64: Raw String Literals."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 73e77e186c25166ddafaaaa87afe7de3
---

> 原文：<https://abseil.io/tips/64> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#64: Raw String Literals

\
\

Originally published as totw/64 on 2013-12-09

*By Titus Winters [(<span class="__cf_email__" cfemail="46322f32333506212929212a236825292b">\[email protected\]</span>)](/cdn-cgi/l/email-protection#25514c51505665424a4a4249400b464a48)*

Updated 2017-10-23

Quicklink: [abseil.io/tips/64](https://abseil.io/tips/64)

*`"(?:\"(?:\\\\\"|[^\"])*\"|'(?:\\\\'|[^'])*')";` — A cat walking over the keyboard . . . or maybe what the fox says . . . no, actually just a highly- escaped regexp found in real C++ code.*

Odds are you’ve had trouble getting your regular expression understood properly in C++ due to escaping issues. Similarly, you’ve probably been annoyed with preserving quotes and newlines when embedding a text version of Protobuf or JSON data into your unittests. When you have to use significant escaping (or worse, multi-layer escaping), code clarity drops precipitously.

Luckily, there’s a new C++11 feature that removes this need for escaping: raw string literals.

## The Raw String Literal Format

A raw string literal has the following special syntax:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
R"tag(whatever you want to say)tag"
```

</div>

</div>

`tag` is a sequence of up to 16 characters (and an empty tag is both OK and common). The characters after ‘“tag(‘ and before the first following occurrence of ‘)tag”’ are used literally as the contents of the string literal. ‘tag’ may contain any character but parentheses, backslash, and whitespace.

Examine the difference:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
const char concert_17_raw[] =
    "id: 17\n"
    "artist: \"Beyonce\"\n"
    "date: \"Wed Oct 10 12:39:54 EDT 2012\"\n"
    "price_usd: 200\n";
```

</div>

</div>

versus:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
const char concert_17_raw[] = R"(
    id: 17
    artist: "Beyonce"
    date: "Wed Oct 10 12:39:54 EDT 2012"
    price_usd: 200)";
```

</div>

</div>

## Special Cases

Note that indentation rules, combined with the fact that raw string literals may contain newlines, leave you with an awkward choice on how to indent the first line of your raw string block. Because text protobufs ignore whitespace, this problem can be avoided by throwing in a leading newline (ignored by the parser) in that case, but not all uses of raw strings are so forgiving.

A non-empty tag is useful when the sequence `)"` happens to appear in your string and therefore can’t act as the closing delimiter:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::string my_string = R"foo(This contains quoted parens "()")foo";
```

</div>

</div>

## Conclusion

Raw string literals are certainly not an everyday tool for most of us, but there are times when good use of this new language feature will increase readability. So the next time you’re scratching your head trying to figure out if you need two `\\`s or four, try raw string literals instead. Your readers will thank you for it, even if regular expressions are still hard:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
R"regexp((?:"(?:\\"|[^"])*"|'(?:\\'|[^'])*'))regexp";
```

</div>

</div>


