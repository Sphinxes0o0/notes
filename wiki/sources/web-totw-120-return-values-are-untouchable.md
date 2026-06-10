---
type: source
source-type: web
title: "Tip of the Week #120: Return Values are Untouchable"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/120
summary: "abseil C++ Tips of the Week #120: Return Values are Untouchable."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 8afe5b9e9633294f62a77d125ea31d3a
---

> 原文：<https://abseil.io/tips/120> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#120: Return Values are Untouchable

\
\

Originally posted as TotW \#120 on August 16, 2012

*by Samuel Benzaquen, [(<span class="__cf_email__" cfemail="f88b9a9d968299b89f97979f949dd69b9795">\[email protected\]</span>)](/cdn-cgi/l/email-protection#1f6c7d7a71657e5f78707078737a317c7072)*

Let’s suppose you have this code snippet, which seems to be working as expected:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
absl::Status DoSomething() {
  absl::Status status;
  absl::Cleanup log_on_error = [&status] {
    if (!status.ok()) LOG(ERROR) << status;
  };
  status = DoA();
  if (!status.ok()) return status;
  status = DoB();
  if (!status.ok()) return status;
  status = DoC();
  if (!status.ok()) return status;
  return status;
}
```

</div>

</div>

A refactor changes the last line from `return status;` to `return absl::OkStatus();` and suddenly the code stopped logging the errors.

What is going on?

## Summary

Never access (read or write) the return variable after the return statement has run. Unless you take great care to do it correctly, the behavior is unspecified.

Return variables are implicitly accessed by destructors after they have been copied or moved (\[stmt.return\]), which is how this unexpected access occurs, but the copy/move may be elided, which is why behavior is unspecified.

This tip only applies when you are returning a non-reference local variable. Returning any other expression will not trigger this problem.

## The Problem

There are 2 different optimizations on return statements that can modify the behavior of that code snippet: the named return value optimization (NRVO) and implicit moves.

The *before* code was working because NRVO is being performed and the `return` statement is not actually doing any work. The variable `status` is already constructed in the return address and the cleanup object is seeing this unique instance of the `Status` object *after* the return statement.

In the *after* code, NRVO is not being performed and the returned variable is being moved into the return value. The cleanup object is being run after the move operation is done and it is seeing a moved-from `Status`.

Note that the *before* code was not correct either, as it relies on NRVO for correctness. We encourage you to rely on NRVO for performance (See TotW \#24), but not correctness. After all, NRVO is an *optional* optimization and compiler options or quality of implementation of the compiler can affect whether or not it happens.

## Solution

Do not touch the return variable after the return statement. Be careful of destructors of local variables doing so implicitly.

The simplest solution is to separate the function in two. One that does all the processing, and one that calls the first one and does the post-processing (ie logging on error). Eg:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
absl::Status DoSomething() {
  absl::Status status;
  status = DoA();
  if (!status.ok()) return status;
  status = DoB();
  if (!status.ok()) return status;
  status = DoC();
  if (!status.ok()) return status;
  return status;
}

absl::Status DoSomethingAndLog() {
  absl::Status status = DoSomething();
  if (!status.ok()) LOG(ERROR) << status;
  return status;
}
```

</div>

</div>

If you are only reading the value, you could also make sure to disable the optimizations instead. That would force a copy to be made all the time and the post-processing will not see a moved-from value. Eg:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
absl::Status DoSomething() {
  absl::Status status_no_nrvo;
  // 'status' is a reference so NRVO and all associated optimizations
  // will be disabled.
  // The 'return status;' statements will always copy the object and Logger
  // will always see the correct value.
  absl::Status& status = status_no_nrvo;
  absl::Cleanup log_on_error = [&status] {
    if (!status.ok()) LOG(ERROR) << status;
  };
  status = DoA();
  if (!status.ok()) return status;
  status = DoB();
  if (!status.ok()) return status;
  status = DoC();
  if (!status.ok()) return status;
  return status;
}
```

</div>

</div>

## Another Real Life Example

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::string EncodeVarInt(int i) {
  std::string out;
  proto2::io::StringOutputStream string_output(&out);
  proto2::io::CodedOutputStream coded_output(&string_output);
  coded_output.WriteVarint32(i);
  return out;
}
```

</div>

</div>

`CodedOutputStream` does some work on the destructor to trim unused trailing bytes. This function can leave garbage bytes on the string if NRVO does not happen.

Note that in this case you can’t force NRVO to happen and the trick to disable it won’t help. We must modify the return value before the return statement runs.

A good solution is to add a block and restrict the function to only return after the block is finished. Like this:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
std::string EncodeVarInt(int i) {
  std::string out;
  {
    proto2::io::StringOutputStream string_output(&out);
    proto2::io::CodedOutputStream coded_output(&string_output);
    coded_output.WriteVarint32(i);
  }
  // At this point the streams are destroyed and they already flushed.
  // We can safely return 'out'.
  return out;
}
```

</div>

</div>

## Conclusion

Don’t hold on to references to variables that are being returned.

You can’t control whether NRVO happens or not. Compiler versions and options can change this from underneath you. Do not depend on it for correctness.

You can’t control whether returning a local variable triggers an implicit move or not. The type you use might be updated in the future to support move operations. Moreover, future language standards will apply implicit moves on even more situations so you can’t assume that just because it is not happening now it won’t happen in the future.


