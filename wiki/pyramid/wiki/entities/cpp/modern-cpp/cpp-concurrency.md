---
type: entity
tags: [cpp11, cpp14, cpp17, cpp20, concurrency, thread, atomic, mutex, memory-model]
created: 2026-05-27
sources: [github-modern-cpp-features]
---

# C++ Concurrency & Threading

## Definition

C++11 introduced the first standardized threading model: `std::thread`, `std::mutex`, atomic operations, and a **memory model** guaranteeing visibility across threads. C++20 added `std::jthread` with automatic join and stop-token support.

## Key Concepts

### Memory Model (C++11)

C++11 guarantees:
- **Atomic operations** — lock-free where possible
- **Memory order** — controls visibility (`seq_cst`, `acq_rel`, `acquire`, `release`, `relaxed`)
- **Happens-before** — inter-thread ordering guarantee

```c++
std::atomic<int> counter{0};
// Release sequence synchronizes with acquire
counter.store(1, std::memory_order_release);
```

### std::thread (C++11)

Spawn and manage threads:

```c++
std::vector<std::thread> threads;
threads.emplace_back([]() { /* work */ });
threads.emplace_back(foo, true);  // foo(true)

for (auto& t : threads) t.join();  // wait for all
```

Thread is **non-joinable** after `join()` or `detach()`.

### std::jthread (C++20)

Auto-joining thread with **stop token**:

```c++
std::jthread t([](std::stop_token stoken) {
  while (!stoken.stop_requested()) {
    std::this_thread::sleep_for(1s);
  }
});
t.request_stop();  // signal stop — thread will exit loop
// automatically joins in destructor
```

Benefits over `std::thread`:
1. Destructor calls `request_stop()` then `join()`
2. No manual join required
3. `stop_token` for cooperative cancellation

### Atomic Operations (C++11)

Lock-free thread-safe primitives:

```c++
std::atomic<int> n{0};
n.fetch_add(1);             // atomic increment
n.load();                   // atomic read
n.store(42);                // atomic write

// Compare-and-swap loop
int expected = 0;
while (!n.compare_exchange_weak(expected, 1)) {
  // expected is updated with current value on failure
}
```

### Memory Order

| Order | Description | Use case |
|-------|-------------|----------|
| `seq_cst` | Sequential consistency (default) | Strongest — total order |
| `acq_rel` | Acquire + release | CAS operations |
| `acquire` | Synchronizes with release | Reader side |
| `release` | Synchronizes with acquire | Writer side |
| `relaxed` | No ordering guarantee | Simple counters |

### Mutex & Locks (C++11)

```c++
std::mutex mtx;
std::lock_guard<std::mutex> lk(mtx);   // RAII lock
// Critical section
// lk unlocked on destruction
```

Lock helpers:
- `std::scoped_lock` (C++17) — lock multiple mutexes without deadlock
- `std::unique_lock` — deferred locking, timed locking
- `std::shared_lock` — reader-writer lock (C++14)

### Condition Variables (C++11)

Signal/wait for state changes:

```c++
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void worker() {
  std::unique_lock<std::mutex> lk(mtx);
  cv.wait(lk, [] { return ready; });  // spurious wake guard
  // proceed
}

{
  std::lock_guard<std::mutex> lk(mtx);
  ready = true;
  cv.notify_one();  // wake worker
}
```

### std::async & std::future (C++11)

Asynchronous execution with result retrieval:

```c++
auto handle = std::async(std::launch::async, []() { return 42; });
auto result = handle.get();  // blocks until ready

// Lazy evaluation
auto handle2 = std::async(std::launch::deferred, foo);
```

Launch policies:
- `std::launch::async` — new thread
- `std::launch::deferred` — lazy evaluation on `.get()`/`.wait()`

### Parallel Algorithms (C++17)

STL algorithms with execution policies:

```c++
std::vector<int> v{1, 2, 3, 4, 5};

auto it = std::find(std::execution::par, v.begin(), v.end(), 3);
std::sort(std::execution::par_unseq, v.begin(), v.end());

// Reduction
std::reduce(std::execution::par, v.begin(), v.end(), 0, std::plus<>{});
```

Policies: `seq` (sequential), `par` (parallel), `par_unseq` (parallel + vectorized).

### std::atomic_shared_ptr (C++20)

Thread-safe `shared_ptr` operations:
```c++
std::atomic<std::shared_ptr<int>> ptr = std::make_shared<int>(42);
```

## Related Concepts

- [[cpp-memory-model]] — deeper memory ordering
- [[cpp-smart-pointers]] — shared_ptr + atomic (atomic_shared_ptr)
- [[cpp-lambda-expressions]] — lambdas in thread/async
- [[cpp-move-semantics]] — moving thread ownership
