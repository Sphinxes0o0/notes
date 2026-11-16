---
type: entity
tags: [cpp20, coroutines, co-await, co-yield, co-return, async]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Coroutines

## Definition

**Coroutines** are functions whose execution can be **suspended** and **resumed**. C++20 coroutines are **stackless** — state is heap-allocated. Defined by presence of `co_await`, `co_yield`, or `co_return`.

## Key Concepts

### co_yield — Generator Pattern

Yields a value and suspends; resumes on next call:

```c++
generator<int> range(int start, int end) {
  while (start < end) {
    co_yield start;      // yield value, suspend
    ++start;
  }
  // implicit co_return at end
}

for (int n : range(0, 5)) {
  std::cout << n << " ";  // 0 1 2 3 4
}
```

`co_yield` internally uses `co_await` — suspends the coroutine and returns the value.

### co_await — Suspension

Suspends until expression is ready:

```c++
task<void> echo(socket s) {
  for (;;) {
    auto data = co_await s.async_read();  // suspend until data ready
    co_await async_write(s, data);         // suspend until write complete
  }
}
```

When `co_await expr` is called:
1. If not ready → suspend coroutine, register continuation
2. When ready → resume coroutine

### co_return — Early Return

```c++
task<int> calculate_mol() {
  co_return 42;
}

auto task = calculate_mol();
// ...
co_await task;  // == 42
```

Implicit `co_return` at function end.

### Stackless Nature

C++20 coroutines are **stackless** — cannot suspend from within a nested call. State includes:
- Local variables live across suspension
- Program counter (resumption point)
- Parameters (copied/cloned)
- If not optimized out by compiler → **heap allocation** for coroutine frame

### std::jthread (C++20)

`std::jthread` auto-joins on destruction and supports stop requests:

```c++
std::jthread t([](std::stop_token stoken) {
  while (!stoken.stop_requested()) {
    std::this_thread::sleep_for(1s);
  }
});

t.request_stop();  // signal stop
// or: std::stop_source ss = t.get_stop_source(); ss.request_stop();
```

## Relationship with std::async

| Feature | Coroutines | std::async |
|---------|-----------|-----------|
| Execution | Suspend/resume | Runs on thread |
| Stack | Stackless (heap frame) | Full thread stack |
| Control | Cooperative | Preemptive |
| Standard lib support | No `task`/`generator` in std | `std::async` + `std::future` |

## Key Constraints

- Coroutine functions **cannot** use variadic args, `throw`, `noexcept` (well-formed in C++20)
- Cannot use `return` — must use `co_return`
- `main()` cannot be a coroutine
- Destructors cannot be coroutines

## Related Concepts

- [[cpp-concurrency]] — coroutines interact with threads
- [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] — return type deduction with coroutines
- [[cpp-stl-functional]] — std::bind_front for binding coroutine callable
