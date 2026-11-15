---
title: "The importance of thinking about performance"
---

# The importance of thinking about performance {#chapter}

[返回总目录](../abseil-hints)

## The importance of thinking about performance {#the-importance-of-thinking-about-performance}

Knuth is often quoted out of context as saying *premature optimization is the root of all evil*. The [full quote](https://dl.acm.org/doi/pdf/10.1145/356635.356640) reads: *“We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. Yet we should not pass up our opportunities in that critical 3%.”* This document is about that critical 3%, and a more compelling quote, again from Knuth, reads:

> The improvement in speed from Example 2 to Example 2a is only about 12%, and many people would pronounce that insignificant. The conventional wisdom shared by many of today’s software engineers calls for ignoring efficiency in the small; but I believe this is simply an overreaction to the abuses they see being practiced by penny-wise-and-pound-foolish programmers, who can’t debug or maintain their “optimized” programs. In established engineering disciplines a 12% improvement, easily obtained, is never considered marginal; and I believe the same viewpoint should prevail in software engineering. Of course I wouldn’t bother making such optimizations on a one-shot job, but when it’s a question of preparing quality programs, I don’t want to restrict myself to tools that deny me such efficiencies.

Many people will say “let’s write down the code in as simple a way as possible and deal with performance later when we can profile”. However, this approach is often wrong:

1.  If you disregard all performance concerns when developing a large system, you will end up with a flat profile where there are no obvious hotspots because performance is lost all over the place. It will be difficult to figure out how to get started on performance improvements.
2.  If you are developing a library that will be used by other people, the people who will run into performance problems will be likely to be people who cannot easily make performance improvements (they will have to understand the details of code written by other people/teams, and have to negotiate with them about the importance of performance optimizations).
3.  It is harder to make significant changes to a system when it is in heavy use.
4.  It is also hard to tell if there are performance problems that can be solved easily and so we end up with potentially expensive solutions like over-replication or severe overprovisioning of a service to handle load problems.

Instead, we suggest that when writing code, try to choose the faster alternative if it does not impact readability/complexity of the code significantly.

## Estimation {#estimation}

If you can develop an intuition for how much performance might matter in the code you are writing, you can make a more informed decision (e.g., how much extra complexity is warranted in the name of performance). Some tips on estimating performance while you are writing code:

- Is it test code? If so, you need to worry mostly about the asymptotic complexity of your algorithms and data structures. (Aside: development cycle time matters, so avoid writing tests that take a long time to run.)
- Is it code specific to an application? If so, try to figure out how much performance matters for this piece of code. This is typically not very hard: just figuring out whether code is initialization/setup code vs. code that will end up on hot paths (e.g., processing every request in a service) is often sufficient
- Is it library code that will be used by many applications? In this case it is hard to tell how sensitive it might become. This is where it becomes especially important to follow some of the simple techniques described in this document. For example, if you need to store a vector that usually has a small number of elements, use an absl::InlinedVector instead of std::vector. Such techniques are not very hard to follow and don’t add any non-local complexity to the system. And if it turns out that the code you are writing does end up using significant resources, it will be higher performance from the start. And it will be easier to find the next thing to focus on when looking at a profile.

You can do a slightly deeper analysis when picking between options with potentially different performance characteristics by relying on [back of the envelope calculations](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation). Such calculations can quickly give a very rough estimate of the performance of different alternatives, and the results can be used to discard some of the alternatives without having to implement them.

Here is how such an estimation might work:

1.  Estimate how many low-level operations of various kinds are required, e.g., number of disk seeks, number of network round-trips, bytes transmitted etc.
2.  Multiply each kind of expensive operation with its rough cost, and add the results together.
3.  The preceding gives the *cost* of the system in terms of resource usage. If you are interested in latency, and if the system has any concurrency, some of the costs may overlap and you may have to do slightly more complicated analysis to estimate the latency.

The following table, which is an updated version of a table from a [2007 talk at Stanford University](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/stanford-295-talk.pdf) (video of the 2007 talk no longer exists, but there is a [video of a related 2011 Stanford talk that covers some of the same content](https://www.youtube.com/watch?v=modXC5IWTJI)) may be useful since it lists the types of operations to consider, and their rough cost:

<div class="language-plaintext highlighter-rouge">

<div class="highlight">

```cpp
L1 cache reference                             0.5 ns
L2 cache reference                             3 ns
Branch mispredict                              5 ns
Mutex lock/unlock (uncontended)               15 ns
Main memory reference                         50 ns
Compress 1K bytes with Snappy              1,000 ns
Read 4KB from SSD                         20,000 ns
Round trip within same datacenter         50,000 ns
Read 1MB sequentially from memory         64,000 ns
Read 1MB over 100 Gbps network           100,000 ns
Read 1MB from SSD                      1,000,000 ns
Disk seek                              5,000,000 ns
Read 1MB sequentially from disk       10,000,000 ns
Send packet CA->Netherlands->CA      150,000,000 ns
```

</div>

</div>

The preceding table contains rough costs for some basic low-level operations. You may find it useful to also track estimated costs for higher-level operations relevant to your system. E.g., you might want to know the rough cost of a point read from your SQL database, the latency of interacting with a Cloud service, or the time to render a simple HTML page. If you don’t know the relevant cost of different operations, you can’t do decent back-of-the-envelope calculations!

### Example: Time to quicksort a billion 4 byte numbers {#example-time-to-quicksort-a-billion-4-byte-numbers}

As a rough approximation, a good quicksort algorithm makes log(N) passes over an array of size N. On each pass, the array contents will be streamed from memory into the processor cache, and the partition code will compare each element once to a pivot element. Let’s add up the dominant costs:

1.  Memory bandwidth: the array occupies 4 GB (4 bytes per number times a billion numbers). Let’s assume ~16GB/s of memory bandwidth per core. That means each pass will take ~0.25s. N is ~2^30, so we will make ~30 passes, so the total cost of memory transfer will be ~7.5 seconds.
2.  Branch mispredictions: we will do a total of N\*log(N) comparisons, i.e., ~30 billion comparisons. Let’s assume that half of them (i.e., 15 billion) are mispredicted. Multiplying by 5 ns per misprediction, we get a misprediction cost of 75 seconds. We assume for this analysis that correctly predicted branches are free.
3.  Adding up the previous numbers, we get an estimate of ~82.5 seconds.

If necessary, we could refine our analysis to account for processor caches. This refinement is probably not needed since branch mispredictions are the dominant cost according to the analysis above, but we include it here anyway as another example. Let’s assume we have a 32MB L3 cache, and that the cost of transferring data from L3 cache to the processor is negligible. The L3 cache can hold 2^23 numbers, and therefore the last 22 passes can operate on the data resident in the L3 cache (the 23rd last pass brings data into the L3 cache and the remaining passes operate on that data.) That cuts down the memory transfer cost to 2.5 seconds (10 memory transfers of 4GB at 16GB/s) instead of 7.5 seconds (30 memory transfers).

### Example: Time to generate a web page with 30 image thumbnails {#example-time-to-generate-a-web-page-with-30-image-thumbnails}

Let’s compare two potential designs where the original images are stored on disk, and each image is approximately 1MB in size.

1.  Read the contents of the 30 images serially and generate a thumbnail for each one. Each read takes one seek + one transfer, which adds up to 5ms for the seek, and 10ms for the transfer, which adds up to 30 images times 15ms per image, i.e., 450ms.
2.  Read in parallel, assuming the images are spread evenly across K disks. The previous resource usage estimate still holds, but latency will drop by roughly a factor of K, ignoring variance (e.g, we will sometimes get unlucky and one disk will have more than 1/Kth of the images we are reading). Therefore if we are running on a distributed filesystem with hundreds of disks, the expected latency will drop to ~15ms.
3.  Let’s consider a variant where all images are on a single SSD. This changes the sequential read performance to 20µs + 1ms per image, which adds up to ~30 ms overall.

## Measurement {#measurement}

The preceding section gives some tips about how to think about performance when writing code without worrying too much about how to measure the performance impact of your choices. However, before you actually start making improvements, or run into a tradeoff involving various things like performance, simplicity, etc. you will want to measure or estimate potential performance benefits. Being able to measure things effectively is the number one tool you’ll want to have in your arsenal when doing performance-related work.

As an aside, it’s worth pointing out that profiling code that you’re unfamiliar with can also be a good way of getting a general sense of the structure of the codebase and how it operates. Examining the source code of heavily involved routines in the dynamic call graph of a program can give you a high level sense of “what happens” when running the code, which can then build your own confidence in making performance-improving changes in slightly unfamiliar code.

### Profiling tools and tips {#profiling-tools-and-tips}

Many useful profiling tools are available. A useful tool to reach for first is [pprof](https://github.com/google/pprof/blob/main/doc/README.md) since it gives good high level performance information and is easy to use both locally and for code running in production. Also try [perf](https://perf.wiki.kernel.org/index.php/Main_Page) if you want more detailed insight into performance.

Some tips for profiling:

- Build production binaries with appropriate debugging information and optimization flags.

- If you can, write a [microbenchmark](https://abseil.io/fast/75) that covers the code you are improving. Microbenchmarks improve turnaround time when making performance improvements, help verify the impact of performance improvements, and can help prevent future performance regressions. However microbenchmarks can have [pitfalls](https://abseil.io/fast/39) that make them non-representative of full system performance. Useful libraries for writing microbenchmarks: [C++](https://github.com/google/benchmark/blob/main/README.md) [Go](https://pkg.go.dev/testing#hdr-Benchmarks) [Java](https://github.com/openjdk/jmh).

- Use a benchmark library to [emit performance counter readings](https://abseil.io/fast/53) both for better precision, and to get more insight into program behavior.

- Lock contention can often artificially lower CPU usage. Some mutex implementations provide support for profiling lock contention.

- Use [ML profilers](https://www.tensorflow.org/tensorboard/tensorboard_profiling_keras#debug_performance_bottlenecks) for machine learning performance work .

### What to do when profiles are flat {#what-to-do-when-profiles-are-flat}

You will often run into situations where your CPU profile is flat (there is no obvious big contributor to slowness). This can often happen when all low-hanging fruit has been picked. Here are some tips to consider if you find yourself in this situation:

- Don’t discount the value of many small optimizations! Making twenty separate 1% improvements in some subsystem is often eminently possible and collectively mean a pretty sizable improvement (work of this flavor often relies on having stable and high quality microbenchmarks). Some examples of these sorts of changes are in the [changes that demonstrate multiple techniques](/ccpp/cpp/abseil-hints/11-sections#cls-that-demonstrate-multiple-techniques) section.
- Find loops closer to the top of call stacks (flame graph view of a CPU profile can be helpful here). Potentially, the loop or the code it calls could be restructured to be more efficient. Some code that initially built a complicated graph structure incrementally by looping over nodes and edges of the input was changed to build the graph structure in one shot by passing it the entire input. This removed a bunch of internal checks that were happening per edge in the initial code.
- Take a step back and look for structural changes higher up in the call stacks instead of concentrating on micro-optimizations. The techniques listed under [algorithmic improvements](/ccpp/cpp/abseil-hints/02-sections#algorithmic-improvements) can be useful when doing this.
- Look for overly general code. Replace it with a customized or lower-level implementation. E.g., if an application is repeatedly using a regular expression match where a simple prefix match would suffice, consider dropping the use of the regular expression.
- Attempt to reduce the number of allocations: [get an allocation profile](https://gperftools.github.io/gperftools/heapprofile.html), and pick away at the highest contributor to the number of allocations. This will have two effects: (1) It will provide a direct reduction of the amount of time spent in the allocator (and garbage collector for GC-ed languages) (2) There will often be a reduction in cache misses since in a long running program using tcmalloc, every allocation tends to go to a different cache line.
- Gather other types of profiles, specially ones based on hardware performance counters. Such profiles may point out functions that are encountering a high cache miss rate. Techniques described in the [profiling tools and tips](/ccpp/cpp/abseil-hints/01-sections#profiling-tools-and-tips) section can be helpful.

## API considerations {#api-considerations}

Some of the techniques suggested below require changing data structures and function signatures, which may be disruptive to callers. Try to organize code so that the suggested performance improvements can be made inside an encapsulation boundary without affecting public interfaces. This will be easier if your [modules are deep](https://web.stanford.edu/~ouster/cgi-bin/book.php) (significant functionality accessed via a narrow interface).

Widely used APIs come under heavy pressure to add features. Be careful when adding new features since these will constrain future implementations and increase cost unnecessarily for users who don’t need the new features. E.g., many C++ standard library containers promise iterator stability, which in typical implementations increases the number of allocations significantly, even though many users do not need pointer stability.

Some specific techniques are listed below. Consider carefully the performance benefits vs. any API usability issues introduced by such changes.

### Bulk APIs {#bulk-apis}

Provide bulk ops to reduce expensive API boundary crossings or to take advantage of algorithmic improvements.

Add bulk MemoryManager::LookupMany interface.

In addition to adding a bulk interface, this also simplified the signature for the new bulk variant: it turns out clients only needed to know if all the keys were found, so we can return a bool rather than a Status object.

memory_manager.h

<div class="old">

```cpp
class MemoryManager {
 public:
  ...
  util::StatusOr<LiveTensor> Lookup(const TensorIdProto& id);
```

</div>

<div class="new">

```cpp
class MemoryManager {
 public:
  ...
  util::StatusOr<LiveTensor> Lookup(const TensorIdProto& id);

  // Lookup the identified tensors
  struct LookupKey {
    ClientHandle client;
    uint64 local_id;
  };
  bool LookupMany(absl::Span<const LookupKey> keys,
                  absl::Span<tensorflow::Tensor> tensors);
```

</div>

Add bulk ObjectStore::DeleteRefs API to amortize locking overhead.

object_store.h

<div class="old">

```cpp
template <typename T>
class ObjectStore {
 public:
  ...
  absl::Status DeleteRef(Ref);
```

</div>

<div class="new">

```cpp
template <typename T>
class ObjectStore {
 public:
  ...
  absl::Status DeleteRef(Ref);

  // Delete many references.  For each ref, if no other Refs point to the same
  // object, the object will be deleted.  Returns non-OK on any error.
  absl::Status DeleteRefs(absl::Span<const Ref> refs);
  ...
template <typename T>
absl::Status ObjectStore<T>::DeleteRefs(absl::Span<const Ref> refs) {
  util::Status result;
  absl::MutexLock l(&mu_);
  for (auto ref : refs) {
    result.Update(DeleteRefLocked(ref));
  }
  return result;
}
```

</div>

memory_tracking.cc

<div class="old">

```cpp
void HandleBatch(int, const plaque::Batch& input) override {
  for (const auto& t : input) {
    auto in = In(t);
    PLAQUE_OP_ASSIGN_OR_RETURN(const auto& handles, in.handles());
    for (const auto handle : handles.value->handles()) {
      PLAQUE_OP_RETURN_IF_ERROR(in_buffer_store_
                                    ? bstore_->DeleteRef(handle)
                                    : tstore_->DeleteRef(handle));
    }
  }
}
```

</div>

<div class="new">

```cpp
void HandleBatch(int, const plaque::Batch& input) override {
  for (const auto& t : input) {
    auto in = In(t);
    PLAQUE_OP_ASSIGN_OR_RETURN(const auto& handles, in.handles());
    if (in_buffer_store_) {
      PLAQUE_OP_RETURN_IF_ERROR(
          bstore_->DeleteRefs(handles.value->handles()));
    } else {
      PLAQUE_OP_RETURN_IF_ERROR(
          tstore_->DeleteRefs(handles.value->handles()));
    }
  }
}
```

</div>

Use [Floyd's heap construction](https://en.wikipedia.org/wiki/Heapsort#Variations) for efficient initialization.

Bulk initialization of a heap can be done in O(N) time, whereas adding one element at a time and updating the heap property after each addition requires O(N lg(N)) time.

Sometimes it is hard to change callers to use a new bulk API directly. In that case it might be beneficial to use a bulk API internally and cache the results for use in future non-bulk API calls:

Cache block decode results for use in future calls.

Each lookup needs to decode a whole block of K entries. Store the decoded entries in a cache and consult the cache on future lookups.

lexicon.cc

<div class="old">

```cpp
void GetTokenString(int pos, std::string* out) const {
  ...
  absl::FixedArray<LexiconEntry, 32> entries(pos + 1);

  // Decode all lexicon entries up to and including pos.
  for (int i = 0; i <= pos; ++i) {
    p = util::coding::TwoValuesVarint::Decode32(p, &entries[i].remaining,
                                                &entries[i].shared);
    entries[i].remaining_str = p;
    p += entries[i].remaining;  // remaining bytes trail each entry.
  }
```

</div>

<div class="new">

```cpp
mutable std::vector<absl::InlinedVector<std::string, 16>> cache_;
...
void GetTokenString(int pos, std::string* out) const {
  ...
  DCHECK_LT(skentry, cache_.size());
  if (!cache_[skentry].empty()) {
    *out = cache_[skentry][pos];
    return;
  }
  ...
  // Init cache.
  ...
  const char* prev = p;
  for (int i = 0; i < block_sz; ++i) {
    uint32 shared, remaining;
    p = TwoValuesVarint::Decode32(p, &remaining, &shared);
    auto& cur = cache_[skentry].emplace_back();
    gtl::STLStringResizeUninitialized(&cur, remaining + shared);

    std::memcpy(cur.data(), prev, shared);
    std::memcpy(cur.data() + shared, p, remaining);
    prev = cur.data();
    p += remaining;
  }
  *out = cache_[skentry][pos];
```

</div>

### View types {#view-types}

Prefer view types (e.g., `std::string_view`, `std::Span<T>`, `absl::FunctionRef<R(Args...)>`) for function arguments (unless ownership of the data is being transferred). These types reduce copying, and allow callers to pick their own container types (e.g., one caller might use `std::vector` whereas another one uses `absl::InlinedVector`).

### Pre-allocated/pre-computed arguments {#pre-allocatedpre-computed-arguments}

For frequently called routines, sometimes it is useful to allow higher-level callers to pass in a data structure that they own or information that the called routine needs that the client already has. This can avoid the low-level routine being forced to allocate its own temporary data structure or recompute already-available information.

Add RPC_Stats::RecordRPC variant allowing client to pass in already available WallTime value.

rpc-stats.h

<div class="old">

```cpp
static void RecordRPC(const Name &name, const RPC_Stats_Measurement& m);
```

</div>

<div class="new">

```cpp
static void RecordRPC(const Name &name, const RPC_Stats_Measurement& m,
                      WallTime now);
```

</div>

clientchannel.cc

<div class="old">

```cpp
const WallTime now = WallTime_Now();
...
RPC_Stats::RecordRPC(stats_name, m);
```

</div>

<div class="new">

```cpp
const WallTime now = WallTime_Now();
...
RPC_Stats::RecordRPC(stats_name, m, now);
```

</div>

### Thread-compatible vs. Thread-safe types {#thread-compatible-vs-thread-safe-types}

A type may be either thread-compatible (synchronized externally) or thread-safe (synchronized internally). Most generally used types should be thread-compatible. This way callers who do not need thread-safety don’t pay for it.

Make a class thread-compatible since callers are already synchronized.

hitless-transfer-phase.cc

<div class="old">

```cpp
TransferPhase HitlessTransferPhase::get() const {
  static CallsiteMetrics cm("HitlessTransferPhase::get");
  MonitoredMutexLock l(&cm, &mutex_);
  return phase_;
}
```

</div>

<div class="new">

```cpp
TransferPhase HitlessTransferPhase::get() const { return phase_; }
```

</div>

hitless-transfer-phase.cc

<div class="old">

```cpp
bool HitlessTransferPhase::AllowAllocate() const {
  static CallsiteMetrics cm("HitlessTransferPhase::AllowAllocate");
  MonitoredMutexLock l(&cm, &mutex_);
  return phase_ == TransferPhase::kNormal || phase_ == TransferPhase::kBrownout;
}
```

</div>

<div class="new">

```cpp
bool HitlessTransferPhase::AllowAllocate() const {
  return phase_ == TransferPhase::kNormal || phase_ == TransferPhase::kBrownout;
}
```

</div>

However if the typical use of a type needs synchronization, prefer to move the synchronization inside the type. This allows the synchronization mechanism to be tweaked as necessary to improve performance (e.g., sharding to reduce contention) without affecting callers.
