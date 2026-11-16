---
type: source
source-type: web
title: "Tip of the Week #45: Avoid Flags, Especially in Library Code"
author: "Abseil Team"
date: 2012
url: https://abseil.io/tips/45
summary: "abseil C++ Tips of the Week #45: Avoid Flags, Especially in Library Code."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: 2dd847c7b00bddd6a110248406eedc95
---

> 原文：<https://abseil.io/tips/45> · 作者：Abseil Team · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#45: Avoid Flags, Especially in Library Code

\
\

Originally posted as TotW \#45 on June 3, 2013

\*by [Titus Winters](/cdn-cgi/l/email-protection#64100d10111724030b0b0308014a070b09)

*“What I really want is the behavior of my code to be controlled by a global variable that cannot be statically predicted, whose usage is incompletely logged, and which can only be removed from my code with great difficulty.” – Nobody, Ever*

The common use of flags in production code, especially within libraries, is a mistake. Don’t use flags unless it is truly necessary. There, we said it.

Flags are global variables, only worse: you can’t know the value of that variable by reading the code. A flag may not only be set at startup, but could potentially be changed later through arbitrary means. If you run a server in your binary, there is usually no guarantee that the value of your flag will remain unchanged from cycle to cycle, nor any notification if it were to change, nor any means for looking for such a change.

If your production environment logs the invocation of every binary directly, and stores those logs, great. Most environments don’t work that way. For library code, this uncertainty is especially nefarious: how can you tell when use of a particular feature is actually dead? The simple answer is: you can’t.

Flags also make it challenging to put the final stake in dead code. During migrations to new backends, you’d *think* that removing legacy code would simply be a matter of removing unnecessary build dependencies and issuing history’s most satisfying `git rm`. You’d be wrong. If your legacy binary has hundreds of flags defined and referenced by production code, simply removing the dead code would cause massive problems for your release engineers: almost no jobs would start up after such a change.

The worst part of all of this? An analysis that was done at Google during early 2012 found that the majority of C++ flags had never actually varied, as far as we can tell within the data retention limits described above.

Flags are appropriate in certain use cases, however: debugging without flag-enabled backtraces just wouldn’t be the same. Feature flags, when handled properly (and cleaned up afterward), are perfectly justified. Knobs that genuinely need to be tweaked by heroic SREs are a handy safety net. More broadly, flags used to pass name/value inputs to a binary, and used only in `main()`, are much more maintainable than positional parameters.

Even given those caveats, it’s time that we all take a good hard look at our usage of flags. The next time you’re tempted to add a flag to your library, spend a while looking for a better way. Pass configuration explicitly: this is almost always easier to reason about properly, and is certainly easier to maintain. Consider making numeric flags into compile-time constants. If you encounter new flags in code reviews, push back. Every flag introduction should be justified.


