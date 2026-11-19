---
type: source
source-type: web
title: "Tip of the Week #42: Prefer Factory Functions to Initializer Methods"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/42
summary: "abseil C++ Tips of the Week #42: Prefer Factory Functions to Initializer Methods."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: ee196de264146117e83b0529d59c7446
---

> 原文：<https://abseil.io/tips/42> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#42: Prefer Factory Functions to Initializer Methods

\
\

Originally posted as totw/42 on 2013-05-10

By Geoffrey Romer [(<span class="__cf_email__" cfemail="dabda8b5b7bfa89abdb5b5bdb6bff4b9b5b7">\[email protected\]</span>)](/cdn-cgi/l/email-protection#4126332e2c243301262e2e262d246f222e2c)

Revised 2017-12-21

*“The man who builds a factory builds a temple; the man who works there worships there, and to each is due, not scorn and blame, but reverence and praise.” – Calvin Coolidge*

In environments where exceptions are disallowed (such as within Google), C++ constructors effectively must succeed, because they have no way to report failure to the caller. You can use an `abort()`, of course, but doing so crashes the whole program, which is often unacceptable in production code.

If your class’s initialization logic can’t avoid the possibility of failure, one common approach is to give the class an initializer method (also called an “init method”), which performs any initialization work that might fail, and signals that failure via its return value. The assumption is usually that the user will call this method immediately after construction, and if it fails the user will immediately destroy the object. However, these assumptions are not always documented, nor always obeyed. It’s all too easy for users to start calling other methods before initialization, or after initialization has failed. Sometimes the class actually encourages this behavior, e.g. by providing methods to configure the object before initializing it, or to read errors out of it after initialization fails.

This design commits you to maintaining a class with at least two distinct user-visible states, and often three: initialized, uninitialized, and initialization-failed. Making such a design work requires a lot of discipline: every method of the class has to specify what states it can be called in, and users have to comply with these rules. If this discipline lapses, client developers will tend to write whatever code happens to work, regardless of what you intended to support. When that starts to happen, maintainability nosedives, because your implementation has to support whatever combinations of pre-initialization method calls your clients have started to depend on. In effect, your implementation has become your interface. (See [Hyrum’s Law](https://www.hyrumslaw.com).)

Fortunately, there’s a simple alternative that lacks these drawbacks: provide a *factory function* which creates and initializes instances of your class, and returns them by pointer or as `absl::optional` (see [TotW \#123](123)), using null to indicate failure. Here’s a toy example using `unique_ptr<>`:

<div class="language-c++ highlighter-rouge">

<div class="highlight">

```cpp
// foo.h
class Foo {
 public:
  // Factory method: creates and returns a Foo.
  // May return null on failure.
  static std::unique_ptr<Foo> Create();

  // Foo is not copyable.
  Foo(const Foo&) = delete;
  Foo& operator=(const Foo&) = delete;

 private:
  // Clients can't invoke the constructor directly.
  Foo();
};

// foo.c
std::unique_ptr<Foo> Foo::Create() {
  // Note that since Foo's constructor is private, we have to use new.
  return absl::WrapUnique(new Foo());
}
```

</div>

</div>

In many cases, this pattern gives you the best of both worlds: the factory function `Foo::Create()` exposes only fully-initialized objects like a constructor, but it can indicate failure like an initializer method. Another advantage of factory functions is that they can return instances of any subclass of the return type (though this is not possible if using `absl::optional` as the return type). This allows you to swap in a different implementation without updating user code, or even choose the implementation class dynamically, based on user input.

The primary drawback of this approach is that it returns a pointer to a heap-allocated object, so it’s not well-suited for “value-like” classes designed to work on the stack. However, such classes usually don’t require complex initialization in the first place. Factory functions also can’t be used when a derived class constructor needs to initialize its base, so initializer methods are sometimes necessary in the protected API of a base class. The public API can still use factory functions, though.


