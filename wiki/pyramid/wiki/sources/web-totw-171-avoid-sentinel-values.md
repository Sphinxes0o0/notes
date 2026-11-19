---
type: source
source-type: web
title: "Tip of the Week #171: Avoid Sentinel Values"
author: "Hyrum Wright"
date: 2012
url: https://abseil.io/tips/171
summary: "abseil C++ Tips of the Week #171: Avoid Sentinel Values."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: e103d2528830b03087407655b94c0196
---

> 原文：<https://abseil.io/tips/171> · 作者：Hyrum Wright · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#171: Avoid Sentinel Values

\
\

Originally posted as TotW \#171 on November 8, 2019

*By [Hyrum Wright](/cdn-cgi/l/email-protection#b2dac5c0dbd5dac6f2d5ddddd5ded79cd1dddf)*

Updated 2020-04-06

Quicklink: [abseil.io/tips/171](https://abseil.io/tips/171)

[Sentinel values](https://en.wikipedia.org/wiki/Sentinel_value) are values that have special meaning in a specific context. For example, consider the following API:

```cpp

// Returns the account balance, or -5 if the account has been closed.
int AccountBalance();
```

Every value of `int` is documented to be a valid return value for `AccountBalance`, except for `-5`. Intuitively, this feels a bit odd: should callers only check against `-5` specifically, or is any negative value a reliable “account closed” signal? What happens when the system supports negative balances and the API needs to be adjusted to return negative values?

Using sentinel values increases the complexity of the calling code. If the caller is rigorous, it explicitly checks against the sentinel value:

```cpp

int balance = AccountBalance();
if (balance == -5) {
  LOG(ERROR) << "account closed";
  return;
}
// use `balance` here
```

Some callers may check against a broader range of values than is specified:

```cpp

int balance = AccountBalance();
if (balance <= 0) {
  LOG(ERROR) << "where is my account?";
  return;
}
// use `balance` here
```

And some callers may just ignore the sentinel value altogether, assuming that it doesn’t actually occur in practice:

```cpp

int balance = AccountBalance();
// use `balance` here
```

## Problems with Sentinel Values

The above example illustrates some of the common problems with using sentinel values. Others include:

- Different systems may use different sentinel values, such as a single negative value, all negative values, an infinite value, or any arbitrary value. The only way to communicate the special value is through documentation.
- The sentinel values are still part of the type’s domain of valid values, so neither the caller nor the callee is forced by the type system to acknowledge that a value may be invalid. When code and comments disagree, both are usually wrong.
- Sentinel values limit interface evolution, as the specific sentinel may someday be a valid value for use in that system.
- One system’s sentinel value is another’s valid value, increasing cognitive overhead and code complexity when interfacing with multiple systems.

Forgetting to check for specified sentinel values is a common bug. In the best case, the use of an unchecked sentinel value will immediately crash the system during runtime. More frequently, an unchecked sentinel value may continue to propagate through the system, producing bad results as it goes.

## Use `std::optional` Instead

Use `std::optional` to indicate unavailable or invalid information instead of using special values.

```cpp

// Returns the account balance, or std::nullopt if the account has been closed.
std::optional<int> AccountBalance();
```

The caller of our new version of `AccountBalance()` now must explicitly look inside the returned value for a potential balance, signalling that the result might be invalid in the process. Barring additional documentation, the caller can assume that any valid `int` value can be returned from this function, without excluding specific sentinel values. This simplification clarifies the intent of calling code.

```cpp

std::optional<int> balance = AccountBalance();

if (!balance.has_value()) {
  LOG(ERROR) << "Account doesn't exist";
  return;
}
// use `*balance` here
```

Next time you are tempted to use a sentinel value within your system, strongly consider using an appropriate `std::optional` instead.

## See Also

- For more information about using `std::optional` to pass values as parameters, see [TotW \#163](163).
- For help deciding when to use `std::optional` instead of `std::unique_ptr`, see [TotW \#123](123).


