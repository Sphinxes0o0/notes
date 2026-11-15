---
title: "Reduce template instantiations"
description: "Reduce template instantiations：Parallelization and synchronization。"
---

# Reduce template instantiations {#chapter}

[返回总目录](../abseil-hints)

### Reduce template instantiations {#reduce-template-instantiations}

Templated code can be duplicated for every possible combination of template arguments when it is instantiated.

Replace template argument with a regular argument.

Changed a large routine templated on a bool to instead take the bool as an extra argument. (The bool was only being used once to select one of two string constants, so a run-time check was just fine.) This reduced the \# of instantiations of the large routine from 287 to 143.

sharding_util_ops.cc

<div class="old">

```cpp
template <bool Split>
Status GetAndValidateAttributes(OpKernelConstruction* ctx,
                                std::vector<int32>& num_partitions,
                                int& num_slices, std::vector<int32>& paddings,
                                bool& has_paddings) {
  absl::string_view num_partitions_attr_name =
      Split ? kNumSplitsAttrName : kNumConcatsAttrName;
      ...
  return OkStatus();
}
```

</div>

<div class="new">

```cpp
Status GetAndValidateAttributes(bool split, OpKernelConstruction* ctx,
                                std::vector<int32>& num_partitions,
                                int& num_slices, std::vector<int32>& paddings,
                                bool& has_paddings) {
  absl::string_view num_partitions_attr_name =
      split ? kNumSplitsAttrName : kNumConcatsAttrName;
      ...
  return OkStatus();
}
```

</div>

Move bulky code from templated constructor to a non-templated shared base class constructor.

Also reduce number of template instantiations from one for every combination of `<T, Device, Rank>` to one for every `<T>` and every `<Rank>`.

sharding_util_ops.cc

<div class="old">

```cpp
template <typename Device, typename T>
class XlaSplitNDBaseOp : public OpKernel {
 public:
  explicit XlaSplitNDBaseOp(OpKernelConstruction* ctx) : OpKernel(ctx) {
    OP_REQUIRES_OK(
        ctx, GetAndValidateAttributes(/*split=*/true, ctx, num_splits_,
                                      num_slices_, paddings_, has_paddings_));
  }
```

</div>

<div class="new">

```cpp
// Shared base class to save code space
class XlaSplitNDShared : public OpKernel {
 public:
  explicit XlaSplitNDShared(OpKernelConstruction* ctx) TF_ATTRIBUTE_NOINLINE
      : OpKernel(ctx),
        num_slices_(1),
        has_paddings_(false) {
    GetAndValidateAttributes(/*split=*/true, ctx, num_splits_, num_slices_,
                             paddings_, has_paddings_);
  }
```

</div>

Reduce generated code size for absl::flat_hash_set and absl::flat_hash_map.

- Extract code that does not depend on the specific hash table type into common (non-inlined) functions.
- Place ABSL_ATTRIBUTE_NOINLINE directives judiciously.
- Move some slow paths out of line.

### Reduce container operations {#reduce-container-operations}

Consider the impact of map and other container operations since each call to such and operation can produce large amounts of generated code.

Turn many map insertion calls in a row to initialize a hash table of emoji characters into a single bulk insert operation (188KB of text down to 360 bytes in library linked into many binaries). 😊

textfallback_init.h

<div class="old">

```cpp
inline void AddEmojiFallbacks(TextFallbackMap *map) {
  (*map)[0xFE000] = &kFE000;
  (*map)[0xFE001] = &kFE001;
  (*map)[0xFE002] = &kFE002;
  (*map)[0xFE003] = &kFE003;
  (*map)[0xFE004] = &kFE004;
  (*map)[0xFE005] = &kFE005;
  ...
  (*map)[0xFEE7D] = &kFEE7D;
  (*map)[0xFEEA0] = &kFEEA0;
  (*map)[0xFE331] = &kFE331;
};
```

</div>

<div class="new">

```cpp
inline void AddEmojiFallbacks(TextFallbackMap *map) {
#define PAIR(x) {0x##x, &k##x}
  // clang-format off
  map->insert({
    PAIR(FE000),
    PAIR(FE001),
    PAIR(FE002),
    PAIR(FE003),
    PAIR(FE004),
    PAIR(FE005),
    ...
    PAIR(FEE7D),
    PAIR(FEEA0),
    PAIR(FE331)});
  // clang-format on
#undef PAIR
};
```

</div>

Stop inlining a heavy user of InlinedVector operations.

Moved very long routine that was being inlined from .h file to .cc (no real performance benefit from inlining this).

reduction_ops_common.h

```cpp
Status Simplify(const Tensor& data, const Tensor& axis,
                const bool keep_dims) {
  ... Eighty line routine body ...
}
```

```cpp
Status Simplify(const Tensor& data, const Tensor& axis, const bool keep_dims);
```

## Parallelization and synchronization {#parallelization-and-synchronization}

### Exploit parallelism {#exploit-parallelism}

Modern machines have many cores, and they are often underutilized. Expensive work may therefore be completed faster by parallelizing it. The most common approach is to process different items in parallel and combine the results when done. Typically, the items are first partitioned into batches to avoid paying the cost of running something in parallel per item.

Four-way parallelization improves the rate of encoding tokens by ~3.6x.

blocked-token-coder.cc

<div class="new">

```cpp
MutexLock l(&encoder_threads_lock);
if (encoder_threads == NULL) {
  encoder_threads = new ThreadPool(NumCPUs());
  encoder_threads->SetStackSize(262144);
  encoder_threads->StartWorkers();
}
encoder_threads->Add
    (NewCallback(this,
                 &BlockedTokenEncoder::EncodeRegionInThread,
                 region_tokens, N, region,
                 stats,
                 controller_->GetClosureWithCost
                 (NewCallback(&DummyCallback), N)));
```

</div>

Parallelization improves decoding performance by 5x.

coding.cc

```cpp
for (int c = 0; c < clusters->size(); c++) {
  RET_CHECK_OK(DecodeBulkForCluster(...);
}
```

```cpp
struct SubTask {
  absl::Status result;
  absl::Notification done;
};

std::vector<SubTask> tasks(clusters->size());
for (int c = 0; c < clusters->size(); c++) {
  options_.executor->Schedule([&, c] {
    tasks[c].result = DecodeBulkForCluster(...);
    tasks[c].done.Notify();
  });
}
for (int c = 0; c < clusters->size(); c++) {
  tasks[c].done.WaitForNotification();
}
for (int c = 0; c < clusters->size(); c++) {
  RETURN_IF_ERROR(tasks[c].result);
}
```

The effect on system performance should be measured carefully – if spare CPU is not available, or if memory bandwidth is saturated, parallelization may not help, or may even hurt.

### Amortize lock acquisition {#amortize-lock-acquisition}

Avoid fine-grained locking to reduce the cost of Mutex operations in hot paths. Caveat: this should only be done if the change does not increase lock contention.

Acquire lock once to free entire tree of query nodes, rather than reacquiring lock for every node in tree.

mustang-query.cc

<div class="old">

```cpp
// Pool of query nodes
ThreadSafeFreeList<MustangQuery> pool_(256);
...
void MustangQuery::Release(MustangQuery* node) {
  if (node == NULL)
    return;
  for (int i=0; i < node->children_->size(); ++i)
    Release((*node->children_)[i]);
  node->children_->clear();
  pool_.Delete(node);
}
```

</div>

<div class="new">

```cpp
// Pool of query nodes
Mutex pool_lock_;
FreeList<MustangQuery> pool_(256);
...
void MustangQuery::Release(MustangQuery* node) {
  if (node == NULL)
    return;
  MutexLock l(&pool_lock_);
  ReleaseLocked(node);
}

void MustangQuery::ReleaseLocked(MustangQuery* node) {
#ifndef NDEBUG
  pool_lock_.AssertHeld();
#endif
  if (node == NULL)
    return;
  for (int i=0; i < node->children_->size(); ++i)
    ReleaseLocked((*node->children_)[i]);
  node->children_->clear();
  pool_.Delete(node);
}
```

</div>

### Keep critical sections short {#keep-critical-sections-short}

Avoid expensive work inside critical sections. In particular, watch out for innocuous looking code that might be doing RPCs or accessing files.

Reduce number of cache lines touched in critical section.

Careful data structure adjustments reduce the number of cache lines accessed significantly and improve the performance of an ML training run by 3.3%.

1.  Precompute some per-node type properties as bits within the NodeItem data structure, meaning that we can avoid touching the Node\* object for outgoing edges in the critical section.
2.  Change ExecutorState::ActivateNodes to use the NodeItem of the destination node for each outgoing edge, rather than touching fields in the \*item-\>node object. Typically this means that we touch 1 or 2 cache lines total for accessing the needed edge data, rather than `~2 + O(num_outgoing edges)` (and for large graphs with many cores executing them there is also less TLB pressure).

Avoid RPC while holding Mutex.

trainer.cc

<div class="old">

```cpp
{
  // Notify the parameter server that we are starting.
  MutexLock l(&lock_);
  model_ = model;
  MaybeRecordProgress(last_global_step_);
}
```

</div>

<div class="new">

```cpp
bool should_start_record_progress = false;
int64 step_for_progress = -1;
{
  // Notify the parameter server that we are starting.
  MutexLock l(&lock_);
  model_ = model;
  should_start_record_progress = ShouldStartRecordProgress();
  step_for_progress = last_global_step_;
}
if (should_start_record_progress) {
  StartRecordProgress(step_for_progress);
}
```

</div>

Also, be wary of expensive destructors that will run before a Mutex is unlocked (this can often happen when the Mutex unlock is triggered by a `~MutexUnlock`.) Declaring objects with expensive destructors before MutexLock may help (assuming it is thread-safe).

### Reduce contention by sharding {#reduce-contention-by-sharding}

Sometimes a data structure protected by a Mutex that is exhibiting high contention can be safely split into multiple shards, each shard with its own Mutex. (Note: this requires that there are no cross-shard invariants between the different shards.)

Shard a cache 16 ways which improves throughput under a multi-threaded load by ~2x.

cache.cc

<div class="new">

```cpp
class ShardedLRUCache : public Cache {
 private:
  LRUCache shard_[kNumShards];
  port::Mutex id_mutex_;
  uint64_t last_id_;

  static inline uint32_t HashSlice(const Slice& s) {
    return Hash(s.data(), s.size(), 0);
  }

  static uint32_t Shard(uint32_t hash) {
    return hash >> (32 - kNumShardBits);
  }
  ...
  virtual Handle* Lookup(const Slice& key) {
    const uint32_t hash = HashSlice(key);
    return shard_[Shard(hash)].Lookup(key, hash);
  }
```

</div>

Shard spanner data structure for tracking calls.

transaction_manager.cc

<div class="old">

```cpp
absl::MutexLock l(&active_calls_in_mu_);
ActiveCallMap::const_iterator iter = active_calls_in_.find(m->tid());
if (iter != active_calls_in_.end()) {
  iter->second.ExtractElements(&m->tmp_calls_);
}
```

</div>

<div class="new">

```cpp
ActiveCalls::LockedShard shard(active_calls_in_, m->tid());
const ActiveCallMap& active_calls_map = shard.active_calls_map();
ActiveCallMap::const_iterator iter = active_calls_map.find(m->tid());
if (iter != active_calls_map.end()) {
  iter->second.ExtractElements(&m->tmp_calls_);
}
```

</div>

If the data structure in question is a map, consider using a concurrent hash map implementation instead.

Be careful with the information used for shard selection. If, for example, you use some bits of a hash value for shard selection and then those same bits end up being used again later, the latter use may perform poorly since it sees a skewed distribution of hash values.

Fix information used for shard selection to prevent hash table issues.

netmon_map_impl.h

<div class="old">

```cpp
ConnectionBucket* GetBucket(Index index) {
  // Rehash the hash to make sure we are not partitioning the buckets based on
  // the original hash. If num_buckets_ is a power of 2 that would drop the
  // entropy of the buckets.
  size_t original_hash = absl::Hash<Index>()(index);
  int hash = absl::Hash<size_t>()(original_hash) % num_buckets_;
  return &buckets_[hash];
}
```

</div>

<div class="new">

```cpp
ConnectionBucket* GetBucket(Index index) {
  absl::Hash<std::pair<Index, size_t>> hasher{};
  // Combine the hash with 42 to prevent shard selection using the same bits
  // as the underlying hashtable.
  return &buckets_[hasher({index, 42}) % num_buckets_];
}
```

</div>

Shard Spanner data structure used for tracking calls.

This CL partitions the ActiveCallMap into 64 shards. Each shard is protected by a separate mutex. A given transaction will be mapped to exactly one shard. A new interface LockedShard(tid) is added for accessing the ActiveCallMap for a transaction in a thread-safe manner. Example usage:

transaction_manager.cc

<div class="old">

```cpp
{
  absl::MutexLock l(&active_calls_in_mu_);
  delayed_locks_timer_ring_.Add(delayed_locks_flush_time_ms, tid);
}
```

</div>

<div class="new">

```cpp
{
  ActiveCalls::LockedShard shard(active_calls_in_, tid);
  shard.delayed_locks_timer_ring().Add(delayed_locks_flush_time_ms, tid);
}
```

</div>

The results show a 69% reduction in overall wall-clock time when running the benchmark with 8192 fibers

```cpp
Benchmark                   Time(ns)        CPU(ns)     Iterations
------------------------------------------------------------------
BM_ActiveCalls/8k        11854633492     98766564676            10
BM_ActiveCalls/16k       26356203552    217325836709            10
```

```cpp
Benchmark                   Time(ns)        CPU(ns)     Iterations
------------------------------------------------------------------
BM_ActiveCalls/8k         3696794642     39670670110            10
BM_ActiveCalls/16k        7366284437     79435705713            10
```
