---
title: "Avoid unnecessary work"
description: "Avoid unnecessary work：Avoid unnecessary work。"
---

# Avoid unnecessary work {#chapter}

[返回总目录](../abseil-hints)

## Avoid unnecessary work {#avoid-unnecessary-work}

Perhaps one of the most effective categories of improving performance is avoiding work you don’t have to do. This can take many forms, including creating specialized paths through code for common cases that avoid more general expensive computation, precomputation, deferring work until it is really needed, hoisting work into less-frequently executed pieces of code, and other similar approaches. Below are many examples of this general approach, categorized into a few representative categories.

### Fast paths for common cases {#fast-paths-for-common-cases}

Often, code is written to cover all cases, but some subset of the cases are much simpler and more common than others. E.g., `vector::push_back` usually has enough space for the new element, but contains code to resize the underlying storage when it does not. Some attention paid to the structure of code can help make the common simple case faster without hurting uncommon case performance significantly.

Make fast path cover more common cases.

Add handling of trailing single ASCII bytes, rather than only handling multiples of four bytes with this routine. This avoids calling the slower generic routine for all-ASCII strings that are, for example, 5 bytes.

utf8statetable.cc

<div class="old">

```cpp
// Scan a UTF-8 stringpiece based on state table.
// Always scan complete UTF-8 characters
// Set number of bytes scanned. Return reason for exiting
// OPTIMIZED for case of 7-bit ASCII 0000..007f all valid
int UTF8GenericScanFastAscii(const UTF8ScanObj* st, absl::string_view str,
                             int* bytes_consumed) {
                             ...
  int exit_reason;
  do {
    //  Skip 8 bytes of ASCII at a whack; no endianness issue
    while ((src_limit - src >= 8) &&
           (((UNALIGNED_LOAD32(src + 0) | UNALIGNED_LOAD32(src + 4)) &
             0x80808080) == 0)) {
      src += 8;
    }
    //  Run state table on the rest
    int rest_consumed;
    exit_reason = UTF8GenericScan(
        st, absl::ClippedSubstr(str, src - initial_src), &rest_consumed);
    src += rest_consumed;
  } while (exit_reason == kExitDoAgain);

  *bytes_consumed = src - initial_src;
  return exit_reason;
}
```

</div>

<div class="new">

```cpp
// Scan a UTF-8 stringpiece based on state table.
// Always scan complete UTF-8 characters
// Set number of bytes scanned. Return reason for exiting
// OPTIMIZED for case of 7-bit ASCII 0000..007f all valid
int UTF8GenericScanFastAscii(const UTF8ScanObj* st, absl::string_view str,
                             int* bytes_consumed) {
                             ...
  int exit_reason = kExitOK;
  do {
    //  Skip 8 bytes of ASCII at a whack; no endianness issue
    while ((src_limit - src >= 8) &&
           (((UNALIGNED_LOAD32(src + 0) | UNALIGNED_LOAD32(src + 4)) &
             0x80808080) == 0)) {
      src += 8;
    }
    while (src < src_limit && Is7BitAscii(*src)) { // Skip ASCII bytes
      src++;
    }
    if (src < src_limit) {
      //  Run state table on the rest
      int rest_consumed;
      exit_reason = UTF8GenericScan(
          st, absl::ClippedSubstr(str, src - initial_src), &rest_consumed);
      src += rest_consumed;
    }
  } while (exit_reason == kExitDoAgain);

  *bytes_consumed = src - initial_src;
  return exit_reason;
}
```

</div>

Simpler fast paths for InlinedVector.

inlined_vector.h

<div class="old">

```cpp
auto Storage<T, N, A>::Resize(ValueAdapter values, size_type new_size) -> void {
  StorageView storage_view = MakeStorageView();

  IteratorValueAdapter<MoveIterator> move_values(
      MoveIterator(storage_view.data));

  AllocationTransaction allocation_tx(GetAllocPtr());
  ConstructionTransaction construction_tx(GetAllocPtr());

  absl::Span<value_type> construct_loop;
  absl::Span<value_type> move_construct_loop;
  absl::Span<value_type> destroy_loop;

  if (new_size > storage_view.capacity) {
  ...
  } else if (new_size > storage_view.size) {
    construct_loop = {storage_view.data + storage_view.size,
                      new_size - storage_view.size};
  } else {
    destroy_loop = {storage_view.data + new_size, storage_view.size - new_size};
  }
```

</div>

<div class="new">

```cpp
auto Storage<T, N, A>::Resize(ValueAdapter values, size_type new_size) -> void {
  StorageView storage_view = MakeStorageView();
  auto* const base = storage_view.data;
  const size_type size = storage_view.size;
  auto* alloc = GetAllocPtr();
  if (new_size <= size) {
    // Destroy extra old elements.
    inlined_vector_internal::DestroyElements(alloc, base + new_size,
                                             size - new_size);
  } else if (new_size <= storage_view.capacity) {
    // Construct new elements in place.
    inlined_vector_internal::ConstructElements(alloc, base + size, &values,
                                               new_size - size);
  } else {
  ...
  }
```

</div>

Fast path for common cases of initializing 1-D to 4-D tensors.

tensor_shape.cc

<div class="old">

```cpp
template <class Shape>
TensorShapeBase<Shape>::TensorShapeBase(gtl::ArraySlice<int64> dim_sizes) {
  set_tag(REP16);
  set_data_type(DT_INVALID);
  set_ndims_byte(0);
  set_num_elements(1);
  for (int64 s : dim_sizes) {
    AddDim(internal::SubtleMustCopy(s));
  }
}
```

</div>

<div class="new">

```cpp
template <class Shape>
void TensorShapeBase<Shape>::InitDims(gtl::ArraySlice<int64> dim_sizes) {
  DCHECK_EQ(tag(), REP16);

  // Allow sizes that are under kint64max^0.25 so that 4-way multiplication
  // below cannot overflow.
  static const uint64 kMaxSmall = 0xd744;
  static_assert(kMaxSmall * kMaxSmall * kMaxSmall * kMaxSmall <= kint64max,
                "bad overflow check");
  bool large_size = false;
  for (auto s : dim_sizes) {
    if (s > kMaxSmall) {
      large_size = true;
      break;
    }
  }

  if (!large_size) {
    // Every size fits in 16 bits; use fast-paths for dims in {1,2,3,4}.
    uint16* dst = as16()->dims_;
    switch (dim_sizes.size()) {
      case 1: {
        set_ndims_byte(1);
        const int64 size = dim_sizes[0];
        const bool neg = Set16(kIsPartial, dst, 0, size);
        set_num_elements(neg ? -1 : size);
        return;
      }
      case 2: {
        set_ndims_byte(2);
        const int64 size0 = dim_sizes[0];
        const int64 size1 = dim_sizes[1];
        bool neg = Set16(kIsPartial, dst, 0, size0);
        neg |= Set16(kIsPartial, dst, 1, size1);
        set_num_elements(neg ? -1 : (size0 * size1));
        return;
      }
      case 3: {
      ...
      }
      case 4: {
      ...
      }
    }
  }

  set_ndims_byte(0);
  set_num_elements(1);
  for (int64 s : dim_sizes) {
    AddDim(internal::SubtleMustCopy(s));
  }
}
```

</div>

Make varint parser fast path cover just the 1-byte case, instead of covering 1-byte and 2-byte cases.

Reducing the size of the (inlined) fast path reduces code size and icache pressure, which leads to improved performance.

parse_context.h

<div class="old">

```cpp
template <typename T>
PROTOBUF_NODISCARD const char* VarintParse(const char* p, T* out) {
  auto ptr = reinterpret_cast<const uint8_t*>(p);
  uint32_t res = ptr[0];
  if (!(res & 0x80)) {
    *out = res;
    return p + 1;
  }
  uint32_t byte = ptr[1];
  res += (byte - 1) << 7;
  if (!(byte & 0x80)) {
    *out = res;
    return p + 2;
  }
  return VarintParseSlow(p, res, out);
}
```

</div>

<div class="new">

```cpp
template <typename T>
PROTOBUF_NODISCARD const char* VarintParse(const char* p, T* out) {
  auto ptr = reinterpret_cast<const uint8_t*>(p);
  uint32_t res = ptr[0];
  if (!(res & 0x80)) {
    *out = res;
    return p + 1;
  }
  return VarintParseSlow(p, res, out);
}
```

</div>

parse_context.cc

<div class="old">

```cpp
std::pair<const char*, uint32_t> VarintParseSlow32(const char* p,
                                                   uint32_t res) {
  for (std::uint32_t i = 2; i < 5; i++) {
  ...
}
...
std::pair<const char*, uint64_t> VarintParseSlow64(const char* p,
                                                   uint32_t res32) {
  uint64_t res = res32;
  for (std::uint32_t i = 2; i < 10; i++) {
  ...
}
```

</div>

<div class="new">

```cpp
std::pair<const char*, uint32_t> VarintParseSlow32(const char* p,
                                                   uint32_t res) {
  for (std::uint32_t i = 1; i < 5; i++) {
  ...
}
...
std::pair<const char*, uint64_t> VarintParseSlow64(const char* p,
                                                   uint32_t res32) {
  uint64_t res = res32;
  for (std::uint32_t i = 1; i < 10; i++) {
  ...
}
```

</div>

Skip significant work in RPC_Stats_Measurement addition if no errors have occurred.

rpc-stats.h

<div class="old">

```cpp
struct RPC_Stats_Measurement {
  ...
  double errors[RPC::NUM_ERRORS];
```

</div>

<div class="new">

```cpp
struct RPC_Stats_Measurement {
  ...
  double get_errors(int index) const { return errors[index]; }
  void set_errors(int index, double value) {
    errors[index] = value;
    any_errors_set = true;
  }
 private:
  ...
  // We make this private so that we can keep track of whether any of
  // these values have been set to non-zero values.
  double errors[RPC::NUM_ERRORS];
  bool any_errors_set;  // True iff any of the errors[i] values are non-zero
```

</div>

rpc-stats.cc

<div class="old">

```cpp
void RPC_Stats_Measurement::operator+=(const RPC_Stats_Measurement& x) {
  ...
  for (int i = 0; i < RPC::NUM_ERRORS; ++i) {
    errors[i] += x.errors[i];
  }
}
```

</div>

<div class="new">

```cpp
void RPC_Stats_Measurement::operator+=(const RPC_Stats_Measurement& x) {
  ...
  if (x.any_errors_set) {
    for (int i = 0; i < RPC::NUM_ERRORS; ++i) {
      errors[i] += x.errors[i];
    }
    any_errors_set = true;
  }
}
```

</div>

Do array lookup on first byte of string to often avoid fingerprinting full string.

soft-tokens-helper.cc

<div class="old">

```cpp
bool SoftTokensHelper::IsSoftToken(const StringPiece& token) const {
  return soft_tokens_.find(Fingerprint(token.data(), token.size())) !=
      soft_tokens_.end();
}
```

</div>

soft-tokens-helper.h

<div class="new">

```cpp
class SoftTokensHelper {
 ...
 private:
  ...
  // Since soft tokens are mostly punctuation-related, for performance
  // purposes, we keep an array filter_.  filter_[i] is true iff any
  // of the soft tokens start with the byte value 'i'.  This avoids
  // fingerprinting a term in the common case, since we can just do an array
  // lookup based on the first byte, and if filter_[b] is false, then
  // we can return false immediately.
  bool          filter_[256];
  ...
};

inline bool SoftTokensHelper::IsSoftToken(const StringPiece& token) const {
  if (token.size() >= 1) {
    char first_char = token.data()[0];
    if (!filter_[first_char]) {
      return false;
    }
  }
  return IsSoftTokenFallback(token);
}
```

</div>

soft-tokens-helper.cc

<div class="new">

```cpp
bool SoftTokensHelper::IsSoftTokenFallback(const StringPiece& token) const {
  return soft_tokens_.find(Fingerprint(token.data(), token.size())) !=
      soft_tokens_.end();
}
```

</div>
