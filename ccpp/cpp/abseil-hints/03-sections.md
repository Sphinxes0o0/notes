---
title: "Bit vectors instead of sets"
---

# Bit vectors instead of sets {#chapter}

[返回总目录](../abseil-hints)

### Bit vectors instead of sets {#bit-vectors-instead-of-sets}

If the domain of a set can be represented by a small integer, the set can be replaced with a bit vector (InlinedBitVector is often a good choice). Set operations can also be nicely efficient on these representations using bitwise boolean operations (OR for union, AND for intersection, etc.).

Spanner placement system. Replace dense_hash_set\<ZoneId\> with a bit-vector with one bit per zone.

zone_set.h

<div class="old">

```cpp
class ZoneSet: public dense_hash_set<ZoneId> {
 public:
  ...
  bool Contains(ZoneId zone) const {
    return count(zone) > 0;
  }
```

</div>

<div class="new">

```cpp
class ZoneSet {
  ...
  // Returns true iff "zone" is contained in the set
  bool ContainsZone(ZoneId zone) const {
    return zone < b_.size() && b_.get_bit(zone);
  }
  ...
 private:
  int size_;          // Number of zones inserted
  util::bitmap::InlinedBitVector<256> b_;
```

</div>

Benchmark results:

```cpp
CPU: AMD Opteron (4 cores) dL1:64KB dL2:1024KB
Benchmark                          Base (ns)  New (ns) Improvement
------------------------------------------------------------------
BM_Evaluate/1                            960       676    +29.6%
BM_Evaluate/2                           1661      1138    +31.5%
BM_Evaluate/3                           2305      1640    +28.9%
BM_Evaluate/4                           3053      2135    +30.1%
BM_Evaluate/5                           3780      2665    +29.5%
BM_Evaluate/10                          7819      5739    +26.6%
BM_Evaluate/20                         17922     12338    +31.2%
BM_Evaluate/40                         36836     26430    +28.2%
```

Use bit matrix to keep track of reachability properties between operands instead of hash table.

hlo_computation.h

<div class="old">

```cpp
using TransitiveOperandMap =
    std::unordered_map<const HloInstruction*,
                       std::unordered_set<const HloInstruction*>>;
```

</div>

<div class="new">

```cpp
class HloComputation::ReachabilityMap {
  ...
  // dense id assignment from HloInstruction* to number
  tensorflow::gtl::FlatMap<const HloInstruction*, int> ids_;
  // matrix_(a,b) is true iff b is reachable from a
  tensorflow::core::Bitmap matrix_;
};
```

</div>

## Reduce allocations {#reduce-allocations}

Memory allocation adds costs:

1.  It increases the time spent in the allocator.
2.  Newly-allocated objects may require expensive initialization and sometimes corresponding expensive destruction when no longer needed.
3.  Every allocation tends to be on a new cache line and therefore data spread across many independent allocations will have a larger cache footprint than data spread across fewer allocations.

Garbage-collection runtimes sometimes obviate issue \#3 by placing consecutive allocations sequentially in memory.

### Avoid unnecessary allocations {#avoid-unnecessary-allocations}

Reducing allocations increases benchmark throughput by 21%.

memory_manager.cc

<div class="old">

```cpp
LiveTensor::LiveTensor(tf::Tensor t, std::shared_ptr<const DeviceInfo> dinfo,
                       bool is_batched)
    : tensor(std::move(t)),
      device_info(dinfo ? std::move(dinfo) : std::make_shared<DeviceInfo>()),
      is_batched(is_batched) {
```

</div>

<div class="new">

```cpp
static const std::shared_ptr<DeviceInfo>& empty_device_info() {
  static std::shared_ptr<DeviceInfo>* result =
      new std::shared_ptr<DeviceInfo>(new DeviceInfo);
  return *result;
}

LiveTensor::LiveTensor(tf::Tensor t, std::shared_ptr<const DeviceInfo> dinfo,
                       bool is_batched)
    : tensor(std::move(t)), is_batched(is_batched) {
  if (dinfo) {
    device_info = std::move(dinfo);
  } else {
    device_info = empty_device_info();
  }
```

</div>

Use statically-allocated zero vector when possible rather than allocating a vector and filling it with zeroes.

embedding_executor_8bit.cc

```cpp
// The actual implementation of the EmbeddingLookUpT using template parameters
// instead of object members to improve the performance.
template <bool Mean, bool SymmetricInputRange>
static tensorflow::Status EmbeddingLookUpT(...) {
    ...
  std::unique_ptr<tensorflow::quint8[]> zero_data(
      new tensorflow::quint8[max_embedding_width]);
  memset(zero_data.get(), 0, sizeof(tensorflow::quint8) * max_embedding_width);
```

```cpp
// A size large enough to handle most embedding widths
static const int kTypicalMaxEmbedding = 256;
static tensorflow::quint8 static_zero_data[kTypicalMaxEmbedding];  // All zeroes
...
// The actual implementation of the EmbeddingLookUpT using template parameters
// instead of object members to improve the performance.
template <bool Mean, bool SymmetricInputRange>
static tensorflow::Status EmbeddingLookUpT(...) {
    ...
  std::unique_ptr<tensorflow::quint8[]> zero_data_backing(nullptr);

  // Get a pointer to a memory area with at least
  // "max_embedding_width" quint8 zero values.
  tensorflow::quint8* zero_data;
  if (max_embedding_width <= ARRAYSIZE(static_zero_data)) {
    // static_zero_data is big enough so we don't need to allocate zero data
    zero_data = &static_zero_data[0];
  } else {
    // static_zero_data is not big enough: we need to allocate zero data
    zero_data_backing =
        absl::make_unique<tensorflow::quint8[]>(max_embedding_width);
    memset(zero_data_backing.get(), 0,
           sizeof(tensorflow::quint8) * max_embedding_width);
    zero_data = zero_data_backing.get();
  }
```

Also, prefer stack allocation over heap allocation when object lifetime is bounded by the scope (although be careful with stack frame sizes for large objects).

### Resize or reserve containers {#resize-or-reserve-containers}

When the maximum or expected maximum size of a vector (or some other container types) is known in advance, pre-size the container’s backing store (e.g., using `resize` or `reserve` in C++).

Pre-size a vector and fill it in, rather than N push_back operations.

indexblockdecoder.cc

<div class="old">

```cpp
for (int i = 0; i < ndocs-1; i++) {
  uint32 delta;
  ERRORCHECK(b->GetRice(rice_base, &delta));
  docs_.push_back(DocId(my_shard_ + (base + delta) * num_shards_));
  base = base + delta + 1;
}
docs_.push_back(last_docid_);
```

</div>

<div class="new">

```cpp
docs_.resize(ndocs);
DocId* docptr = &docs_[0];
for (int i = 0; i < ndocs-1; i++) {
  uint32 delta;
  ERRORCHECK(b.GetRice(rice_base, &delta));
  *docptr = DocId(my_shard_ + (base + delta) * num_shards_);
  docptr++;
  base = base + delta + 1;
}
*docptr = last_docid_;
```

</div>

Caveat: Do not use `resize` or `reserve` to grow one element at a time since that may lead to quadratic behavior. Also, if element construction is expensive, prefer an initial `reserve` call followed by several `push_back` or `emplace_back` calls instead of an initial `resize` since that will double the number of constructor calls.

### Avoid copying when possible {#avoid-copying-when-possible}

- Prefer moving to copying data structures when possible.
- If lifetime is not an issue, store pointers or indices instead of copies of objects in transient data structures. E.g., if a local map is used to select a set of protos from an incoming list of protos, we can make the map store just pointers to the incoming protos instead of copying potentially deeply nested data. Another common example is sorting a vector of indices rather than sorting a vector of large objects directly since the latter would incur significant copying/moving costs.

Avoid an extra copy when receiving a tensor via gRPC.

A benchmark that sends around 400KB tensors speeds up by ~10-15%:

```cpp
Benchmark              Time(ns)    CPU(ns) Iterations
-----------------------------------------------------
BM_RPC/30/98k_mean    148764691 1369998944       1000
```

```cpp
Benchmark              Time(ns)    CPU(ns) Iterations
-----------------------------------------------------
BM_RPC/30/98k_mean    131595940 1216998084       1000
```

Move large options structure rather than copying it.

index.cc

<div class="old">

```cpp
return search_iterators::DocPLIteratorFactory::Create(opts);
```

</div>

<div class="new">

```cpp
return search_iterators::DocPLIteratorFactory::Create(std::move(opts));
```

</div>

Use std::sort instead of std::stable_sort, which avoids an internal copy inside the stable sort implementation.

encoded-vector-hits.h

<div class="old">

```cpp
std::stable_sort(hits_.begin(), hits_.end(),
                 gtl::OrderByField(&HitWithPayloadOffset::docid));
```

</div>

<div class="new">

```cpp
struct HitWithPayloadOffset {
  search_iterators::LocalDocId64 docid;
  int first_payload_offset;  // offset into the payload vector.
  int num_payloads;

  bool operator<(const HitWithPayloadOffset& other) const {
    return (docid < other.docid) ||
           (docid == other.docid &&
            first_payload_offset < other.first_payload_offset);
  }
};
    ...
    std::sort(hits_.begin(), hits_.end());
```

</div>

### Reuse temporary objects {#reuse-temporary-objects}

A container or an object declared inside a loop will be recreated on every loop iteration. This can lead to expensive construction, destruction, and resizing. Hoisting the declaration outside the loop enables reuse and can provide a significant performance boost. (Compilers are often unable to do such hoisting on their own due to language semantics or their inability to ensure program equivalence.)

Hoist variable definition outside of loop iteration.

autofdo_profile_utils.h

<div class="old">

```cpp
auto iterator = absl::WrapUnique(sstable->GetIterator());
while (!iterator->done()) {
  T profile;
  if (!profile.ParseFromString(iterator->value_view())) {
    return absl::InternalError(
        "Failed to parse mem_block to specified profile type.");
  }
  ...
  iterator->Next();
}
```

</div>

<div class="new">

```cpp
auto iterator = absl::WrapUnique(sstable->GetIterator());
T profile;
while (!iterator->done()) {
  if (!profile.ParseFromString(iterator->value_view())) {
    return absl::InternalError(
        "Failed to parse mem_block to specified profile type.");
  }
  ...
  iterator->Next();
}
```

</div>

Define a protobuf variable outside a loop so that its allocated storage can be reused across loop iterations.

stats-router.cc

<div class="old">

```cpp
for (auto& r : routers_to_update) {
  ...
  ResourceRecord record;
  {
    MutexLock agg_lock(r.agg->mutex());
    r.agg->AddResourceRecordUsages(measure_indices, &record);
  }
  ...
}
```

</div>

<div class="new">

```cpp
ResourceRecord record;
for (auto& r : routers_to_update) {
  ...
  record.Clear();
  {
    MutexLock agg_lock(r.agg->mutex());
    r.agg->AddResourceRecordUsages(measure_indices, &record);
  }
  ...
}
```

</div>

Serialize to same std::string repeatedly.

program_rep.cc

<div class="old">

```cpp
std::string DeterministicSerialization(const proto2::Message& m) {
  std::string result;
  proto2::io::StringOutputStream sink(&result);
  proto2::io::CodedOutputStream out(&sink);
  out.SetSerializationDeterministic(true);
  m.SerializePartialToCodedStream(&out);
  return result;
}
```

</div>

<div class="new">

```cpp
absl::string_view DeterministicSerializationTo(const proto2::Message& m,
                                               std::string* scratch) {
  scratch->clear();
  proto2::io::StringOutputStream sink(scratch);
  proto2::io::CodedOutputStream out(&sink);
  out.SetSerializationDeterministic(true);
  m.SerializePartialToCodedStream(&out);
  return absl::string_view(*scratch);
}
```

</div>

Caveat: protobuf, string, vector, containers etc. tend to grow to the size of the largest value ever stored in them. Therefore reconstructing them periodically (e.g., after every N uses) can help reduce memory requirements and reinitialization costs.
