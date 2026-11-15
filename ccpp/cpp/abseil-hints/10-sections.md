---
title: "absl::btree_map/absl::btree_set"
description: "absl::btree_map/absl::btree_set的内容说明与阅读参考。"
---

# absl::btree_map/absl::btree_set {#chapter}

[返回总目录](../abseil-hints)

### absl::btree_map/absl::btree_set {#abslbtree_mapabslbtree_set}

absl::btree_map and absl::btree_set store multiple entries per tree node. This has a number of advantages over ordered C++ standard library containers such as `std::map`. First, the pointer overhead of pointing to child tree nodes is often significantly reduced. Second, because the entries or key/values are stored consecutively in memory for a given btree tree node, cache efficiency is often significantly better.

Use btree_set instead of std::set to represent a very heavily used work-queue.

register_allocator.h

```cpp
using container_type = std::set<WorklistItem>;
```

```cpp
using container_type = absl::btree_set<WorklistItem>;
```

### util::bitmap::InlinedBitVector {#utilbitmapinlinedbitvector}

`util::bitmap::InlinedBitvector` can store short bit-vectors inline, and therefore can often be a better choice than `std::vector<bool>` or other bitmap types.

Use InlinedBitVector instead of std::vector\<bool\>, and then use FindNextBitSet to find the next item of interest.

block_encoder.cc

<div class="old">

```cpp
vector<bool> live_reads(nreads);
...
for (int offset = 0; offset < b_.block_width(); offset++) {
  ...
  for (int r = 0; r < nreads; r++) {
    if (live_reads[r]) {
```

</div>

<div class="new">

```cpp
util::bitmap::InlinedBitVector<4096> live_reads(nreads);
...
for (int offset = 0; offset < b_.block_width(); offset++) {
  ...
  for (size_t r = 0; live_reads.FindNextSetBit(&r); r++) {
    DCHECK(live_reads[r]);
```

</div>

### absl::InlinedVector {#abslinlinedvector}

absl::InlinedVector stores a small number of elements inline (configurable via the second template argument). This enables small vectors up to this number of elements to generally have better cache efficiency and also to avoid allocating a backing store array at all when the number of elements is small.

Use InlinedVector instead of std::vector in various places.

bundle.h

```cpp
class Bundle {
 public:
 ...
 private:
  // Sequence of (slotted instruction, unslotted immediate operands).
  std::vector<InstructionRecord> instructions_;
  ...
};
```

```cpp
class Bundle {
 public:
 ...
 private:
  // Sequence of (slotted instruction, unslotted immediate operands).
  absl::InlinedVector<InstructionRecord, 2> instructions_;
  ...
};
```

### gtl::vector32 {#gtlvector32}

Saves space by using a customized vector type that only supports sizes that fit in 32 bits.

Simple type change saves ~8TiB of memory in Spanner.

table_ply.h

<div class="old">

```cpp
class TablePly {
    ...
    // Returns the set of data columns stored in this file for this table.
    const std::vector<FamilyId>& modified_data_columns() const {
      return modified_data_columns_;
    }
    ...
   private:
    ...
    std::vector<FamilyId> modified_data_columns_;  // Data columns in the table.
```

</div>

<div class="new">

```cpp
#include "util/gtl/vector32.h"
    ...
    // Returns the set of data columns stored in this file for this table.
    absl::Span<const FamilyId> modified_data_columns() const {
      return modified_data_columns_;
    }
    ...

    ...
    // Data columns in the table.
    gtl::vector32<FamilyId> modified_data_columns_;
```

</div>

### gtl::small_map {#gtlsmall_map}

gtl::small_map uses an inline array to store up to a certain number of unique key-value-pair elements, but upgrades itself automatically to be backed by a user-specified map type when it runs out of space.

Use gtl::small_map in tflite_model.

tflite_model.cc

<div class="old">

```cpp
using ChoiceIdToContextMap = gtl::flat_hash_map<int, TFLiteContext*>;
```

</div>

<div class="new">

```cpp
using ChoiceIdToContextMap =
    gtl::small_map<gtl::flat_hash_map<int, TFLiteContext*>>;
```

</div>

### gtl::small_ordered_set {#gtlsmall_ordered_set}

gtl::small_ordered_set is an optimization for associative containers (such as std::set or absl::btree_multiset). It uses a fixed array to store a certain number of elements, then reverts to using a set or multiset when it runs out of space. For sets that are typically small, this can be considerably faster than using something like set directly, as set is optimized for large data sets. This change shrinks cache footprint and reduces critical section length.

Use gtl::small_ordered_set to hold set of listeners.

broadcast_stream.h

<div class="old">

```cpp
class BroadcastStream : public ParsedRtpTransport {
 ...
 private:
  ...
  std::set<ParsedRtpTransport*> listeners_ ABSL_GUARDED_BY(listeners_mutex_);
};
```

</div>

<div class="new">

```cpp
class BroadcastStream : public ParsedRtpTransport {
 ...
 private:
  ...
  using ListenersSet =
      gtl::small_ordered_set<std::set<ParsedRtpTransport*>, 10>;
  ListenersSet listeners_ ABSL_GUARDED_BY(listeners_mutex_);
```

</div>

### gtl::intrusive_list {#gtl-intrusive_list}

`gtl::intrusive_list<T>` is a doubly-linked list where the link pointers are embedded in the elements of type T. It saves one cache line+indirection per element when compared to `std::list<T*>`.

Use intrusive_list to keep track of inflight requests for each index row update.

row-update-sender-inflight-set.h

<div class="old">

```cpp
std::set<int64> inflight_requests_ GUARDED_BY(mu_);
```

</div>

<div class="new">

```cpp
class SeqNum : public gtl::intrusive_link<SeqNum> {
  ...
  int64 val_ = -1;
  ...
};
...
gtl::intrusive_list<SeqNum> inflight_requests_ GUARDED_BY(mu_);
```

</div>

### Limit absl::Status and absl::StatusOr usage {#limit-abslstatus-and-abslstatusor-usage}

Even though `absl::Status` and `absl::StatusOr` types are fairly efficient, they have a non-zero overhead even in the success path and should therefore be avoided for hot routines that don’t need to return any meaningful error details (or perhaps never even fail!):

Avoid StatusOr\<int64\> return type for RoundUpToAlignment() function.

best_fit_allocator.cc

<div class="old">

```cpp
absl::StatusOr<int64> BestFitAllocator::RoundUpToAlignment(int64 bytes) const {
  TPU_RET_CHECK_GE(bytes, 0);

  const int64 max_aligned = MathUtil::RoundDownTo<int64>(
      std::numeric_limits<int64>::max(), alignment_in_bytes_);
  if (bytes > max_aligned) {
    return util::ResourceExhaustedErrorBuilder(ABSL_LOC)
           << "Attempted to allocate "
           << strings::HumanReadableNumBytes::ToString(bytes)
           << " which after aligning to "
           << strings::HumanReadableNumBytes::ToString(alignment_in_bytes_)
           << " cannot be expressed as an int64.";
  }

  return MathUtil::RoundUpTo<int64>(bytes, alignment_in_bytes_);
}
```

</div>

best_fit_allocator.h

<div class="new">

```cpp
// Rounds bytes up to nearest multiple of alignment_.
// REQUIRES: bytes >= 0.
// REQUIRES: result does not overflow int64.
// REQUIRES: alignment_in_bytes_ is a power of 2 (checked in constructor).
int64 RoundUpToAlignment(int64 bytes) const {
  DCHECK_GE(bytes, 0);
  DCHECK_LE(bytes, max_aligned_bytes_);
  int64 result =
      ((bytes + (alignment_in_bytes_ - 1)) & ~(alignment_in_bytes_ - 1));
  DCHECK_EQ(result, MathUtil::RoundUpTo<int64>(bytes, alignment_in_bytes_));
  return result;
}
```

</div>

Add ShapeUtil::ForEachIndexNoStatus to avoid creating a Status return object for every element of a tensor.

shape_util.h

<div class="old">

```cpp
using ForEachVisitorFunction =
    absl::FunctionRef<StatusOr<bool>(absl::Span<const int64_t>)>;
    ...
static void ForEachIndex(const Shape& shape, absl::Span<const int64_t> base,
                         absl::Span<const int64_t> count,
                         absl::Span<const int64_t> incr,
                         const ForEachVisitorFunction& visitor_function);
```

</div>

<div class="new">

```cpp
using ForEachVisitorFunctionNoStatus =
    absl::FunctionRef<bool(absl::Span<const int64_t>)>;
    ...
static void ForEachIndexNoStatus(
    const Shape& shape, absl::Span<const int64_t> base,
    absl::Span<const int64_t> count, absl::Span<const int64_t> incr,
    const ForEachVisitorFunctionNoStatus& visitor_function);
```

</div>

literal.cc

<div class="old">

```cpp
ShapeUtil::ForEachIndex(
    result_shape, [&](absl::Span<const int64_t> output_index) {
      for (int64_t i = 0, end = dimensions.size(); i < end; ++i) {
        scratch_source_index[i] = output_index[dimensions[i]];
      }
      int64_t dest_index = IndexUtil::MultidimensionalIndexToLinearIndex(
          result_shape, output_index);
      int64_t source_index = IndexUtil::MultidimensionalIndexToLinearIndex(
          shape(), scratch_source_index);
      memcpy(dest_data + primitive_size * dest_index,
             source_data + primitive_size * source_index, primitive_size);
      return true;
    });
```

</div>

<div class="new">

```cpp
ShapeUtil::ForEachIndexNoStatus(
    result_shape, [&](absl::Span<const int64_t> output_index) {
      // Compute dest_index
      int64_t dest_index = IndexUtil::MultidimensionalIndexToLinearIndex(
          result_shape, result_minor_to_major, output_index);

      // Compute source_index
      int64_t source_index;
      for (int64_t i = 0, end = dimensions.size(); i < end; ++i) {
        scratch_source_array[i] = output_index[dimensions[i]];
      }
      if (src_shape_dims == 1) {
        // Fast path for this case
        source_index = scratch_source_array[0];
        DCHECK_EQ(source_index,
                  IndexUtil::MultidimensionalIndexToLinearIndex(
                      src_shape, src_minor_to_major, scratch_source_span));
      } else {
        source_index = IndexUtil::MultidimensionalIndexToLinearIndex(
            src_shape, src_minor_to_major, scratch_source_span);
      }
      // Move one element from source_index in source to dest_index in dest
      memcpy(dest_data + PRIMITIVE_SIZE * dest_index,
             source_data + PRIMITIVE_SIZE * source_index, PRIMITIVE_SIZE);
      return true;
    });
```

</div>

In TF_CHECK_OK, avoid creating Ok object in order to test for ok().

status.h

<div class="old">

```cpp
#define TF_CHECK_OK(val) CHECK_EQ(::tensorflow::Status::OK(), (val))
#define TF_QCHECK_OK(val) QCHECK_EQ(::tensorflow::Status::OK(), (val))
```

</div>

<div class="new">

```cpp
extern tensorflow::string* TfCheckOpHelperOutOfLine(
    const ::tensorflow::Status& v, const char* msg);
inline tensorflow::string* TfCheckOpHelper(::tensorflow::Status v,
                                           const char* msg) {
  if (v.ok()) return nullptr;
  return TfCheckOpHelperOutOfLine(v, msg);
}
#define TF_CHECK_OK(val)                                           \
  while (tensorflow::string* _result = TfCheckOpHelper(val, #val)) \
  LOG(FATAL) << *(_result)
#define TF_QCHECK_OK(val)                                          \
  while (tensorflow::string* _result = TfCheckOpHelper(val, #val)) \
  LOG(QFATAL) << *(_result)
```

</div>

Remove StatusOr from the hot path of remote procedure calls (RPCs).

Removal of StatusOr from a hot path eliminated a 14% CPU regression in RPC benchmarks caused by an earlier change.

privacy_context.h

<div class="old">

```cpp
absl::StatusOr<privacy::context::PrivacyContext> GetRawPrivacyContext(
    const CensusHandle& h);
```

</div>

privacy_context_statusfree.h

<div class="new">

```cpp
enum class Result {
  kSuccess,
  kNoRootScopedData,
  kNoPrivacyContext,
  kNoDDTContext,
  kDeclassified,
  kNoPrequestContext
};
...
Result GetRawPrivacyContext(const CensusHandle& h,
                            PrivacyContext* privacy_context);
```

</div>
