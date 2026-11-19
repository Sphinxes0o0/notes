---
type: source
source-type: web
title: "Tip of the Week #197: Reader Locks Should Be Rare"
author: "Titus Winters"
date: 2012
url: https://abseil.io/tips/197
summary: "abseil C++ Tips of the Week #197: Reader Locks Should Be Rare."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: d26cf6416cbf68d5bdcd0c6b69ff12c1
---

> 原文：<https://abseil.io/tips/197> · 作者：Titus Winters · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#197: Reader Locks Should Be Rare

\
\

Originally posted as TotW \#197 on July 29, 2021

*By [Titus Winters](/cdn-cgi/l/email-protection#07736e7372744764742972647529626372)*

Updated 2024-04-01

Quicklink: [abseil.io/tips/197](https://abseil.io/tips/197)

“Ah, how good it is to be among people who are reading.” - *Rainer Maria Rilke*

The `absl::Mutex` class has supported two styles of locking for many years now:

- Exclusive locks, in which exactly one thread holds the lock.
- Shared locks, which have two modes. If they are held “for writing” they use an exclusive lock, but they also have a different mode in which many threads can hold the lock “for reading.”

How can a shared lock be acceptable? Isn’t the whole point of having a lock to gain exclusive access to an object? The perceived value in shared locks is when we need read-only access to the underlying data/objects. Remember that we get data races and API races when two threads access the same data without synchronization, and at least one of those accesses is a write. If we use a shared-lock when many threads only need to read data, and always use exclusive locks when writing data, we can avoid contention among the readers and still avoid data and API races.

To support this, `absl::Mutex` has both `Mutex::Lock()` (and `Mutex::WriterLock()`, an alternate name for the same exclusive behavior) as well as `Mutex::ReaderLock()`. From reading through those interfaces, you might think that we should prefer `ReaderLock()` when we’re only reading from the data protected by the lock.

In many cases you’d be wrong.

### ReaderLock Is Slow

`ReaderLock` inherently does more bookkeeping and requires more overhead than a standard exclusive lock. As a result, in many cases using the more specialized form (shared locks) is actually a performance loss, as we have to do quite a bit more work in the lock machinery itself. This cost is minor in the absence of contention, but `ReaderLock` underperforms `Lock` under contention for short critical sections. Without contention, the value `ReaderLock` provides is less significant in the first place.

Consider the logic in an exclusive lock vs. a shared lock. A shared lock generally must also have an exclusive lock mode - if there are no writers, no data race can occur, and thus there is no need for locking in the first place. Shared locking is therefore inherently more complex, requiring checks on whether other readers hold locks, or modifications to the (atomic) count of readers, etc.

### When are Shared Locks Useful?

Shared locks are primarily a benefit when the lock is going to be held for a comparatively long time and it’s likely that multiple readers will concurrently obtain the *shared* lock. For example, if you’re going to do a lot of work while holding the lock (e.g. iterating over a large container, not just doing a single lookup), then a shared locking scheme may be valuable. The dominant question is not “am I writing to the data”, it’s “how long do I expect the lock to be held by readers (compared to how long it takes to acquire the lock)?”

```cpp

// This is bad - the amount of work done under the lock is insignificant.
// The added complexity of using reader locks is going to cost more in aggregate
// than the contention saved by having multiple threads able to call this
// function concurrently.
int Foo::GetElementSize() const {
  absl::ReaderMutexLock l(&lock_);
  return element_size_;
}
```

Even when the amount of computation performed under a lock is larger, and reader locks become more useful, we often find we have better special-case interfaces to avoid contention entirely - see https://abseil.io/fast and https://abseil.io/docs/cpp/guides/synchronization for more. RCU (“Read Copy Update”) abstractions provide a particularly common solution here, making the read path essentially free.

### What Should We Do?

Be on the lookout for use of `ReaderLock` - the overwhelming majority of uses of it are actually a pessimization … but we can’t statically determine that definitively to rewrite code to use exclusive locking instead. (Reasoning about concurrency properties in C++ is still too hard for most refactoring work.)

If you spot `ReaderLock`, especially new uses of it, try to ask “Is the computation under this lock often long?” If it’s just looking up a value in a container, an exclusive lock is almost certainly a better solution.

In the end, profiling may be the only way to be sure - contention tracking is particularly valuable here.


