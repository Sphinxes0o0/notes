---
title: "SIMD Instructions"
---

# SIMD Instructions {#chapter}

[返回总目录](../abseil-hints)

### SIMD Instructions {#simd-instructions}

Explore whether handling multiple items at once using [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) instructions available on modern CPUs can give speedups (e.g., see `absl::flat_hash_map` discussion below in [Bulk Operations](/ccpp/cpp/abseil-hints/11-sections#bulk-operations) section).

### Reduce false sharing {#reduce-false-sharing}

If different threads access different mutable data, consider placing the different data items on different cache lines, e.g., in C++ using the `alignas` directive. However, these directives are easy to misuse and may increase object sizes significantly, so make sure performance measurements justify their use.

Segregate commonly mutated fields in a different cache line than other fields.

histogram.h

<div class="old">

```cpp
HistogramOptions options_;
...
internal::HistogramBoundaries *boundaries_;
...
std::vector<double> buckets_;

double min_;             // Minimum.
double max_;             // Maximum.
double count_;           // Total count of occurrences.
double sum_;             // Sum of values.
double sum_of_squares_;  // Sum of squares of values.
...
RegisterVariableExporter *exporter_;
```

</div>

<div class="new">

```cpp
  HistogramOptions options_;
  ...
  internal::HistogramBoundaries *boundaries_;
  ...
  RegisterVariableExporter *exporter_;
  ...
  // Place the following fields in a dedicated cacheline as they are frequently
  // mutated, so we can avoid potential false sharing.
  ...
#ifndef SWIG
  alignas(ABSL_CACHELINE_SIZE)
#endif
  std::vector<double> buckets_;

  double min_;             // Minimum.
  double max_;             // Maximum.
  double count_;           // Total count of occurrences.
  double sum_;             // Sum of values.
  double sum_of_squares_;  // Sum of squares of values.
```

</div>

### Reduce frequency of context switches {#reduce-frequency-of-context-switches}

Process small work items inline instead of on device thread pool.

cast_op.cc

<div class="new">

```cpp
template <typename Device, typename Tout, typename Tin>
void CastMaybeInline(const Device& d, typename TTypes<Tout>::Flat o,
                     typename TTypes<Tin>::ConstFlat i) {
  if (o.size() * (sizeof(Tin) + sizeof(Tout)) < 16384) {
    // Small cast on a CPU: do inline
    o = i.template cast<Tout>();
  } else {
    o.device(d) = i.template cast<Tout>();
  }
}
```

</div>

### Use buffered channels for pipelining {#use-buffered-channels-for-pipelining}

Channels can be unbuffered which means that a writer blocks until a reader is ready to pick up an item. Unbuffered channels can be useful when the channel is being used for synchronization, but not when the channel is being used to increase parallelism.

### Consider lock-free approaches {#consider-lock-free-approaches}

Sometimes lock-free data structures can make a difference over more conventional mutex-protected data structures. However, direct atomic variable manipulation can be [dangerous](https://abseil.io/docs/cpp/atomic_danger). Prefer higher-level abstractions.

Use lock-free map to manage a cache of RPC channels.

Entries in an RPC stub cache are read thousands of times a second and modified rarely. Switching to an appropriate lock-free map reduces search latency by 3%-5%.

Use a fixed lexicon+lock-free hash map to speed-up determining IsValidTokenId.

dynamic_token_class_manager.h

<div class="old">

```cpp
mutable Mutex mutex_;

// The density of this hash map is guaranteed by the fact that the
// dynamic lexicon reuses previously allocated TokenIds before trying
// to allocate new ones.
dense_hash_map<TokenId, common::LocalTokenClassId> tid_to_cid_
    GUARDED_BY(mutex_);
```

</div>

<div class="new">

```cpp
// Read accesses to this hash-map should be done using
// 'epoch_gc_'::(EnterFast / LeaveFast). The writers should periodically
// GC the deleted entries, by simply invoking LockFreeHashMap::CreateGC.
typedef util::gtl::LockFreeHashMap<TokenId, common::LocalTokenClassId>
    TokenIdTokenClassIdMap;
TokenIdTokenClassIdMap tid_to_cid_;
```

</div>

## Protocol Buffer advice {#protobuf-advice}

Protobufs are a convenient representation of data, especially if the data will be sent over the wire or stored persistently. However, they can have significant performance costs. For example, a piece of code that fills in a list of 1000 points and then sums up the Y coordinates, speeds up by a **factor of 20** when converted from protobufs to a C++ std::vector of structs!

Benchmark code for both versions.

```protobuf
name                old time/op  new time/op  delta
BenchmarkIteration  17.4µs ± 5%   0.8µs ± 1%  -95.30%  (p=0.000 n=11+12)
```

Protobuf version:

```cpp
message PointProto {
  int32 x = 1;
  int32 y = 2;
}
message PointListProto {
  repeated PointProto points = 1;
}
```

```cpp
void SumProto(const PointListProto& vec) {
  int sum = 0;
  for (const PointProto& p : vec.points()) {
    sum += p.y();
  }
  ABSL_VLOG(1) << sum;
}

void BenchmarkIteration() {
  PointListProto points;
  points.mutable_points()->Reserve(1000);
  for (int i = 0; i < 1000; i++) {
    PointProto* p = points.add_points();
    p->set_x(i);
    p->set_y(i * 2);
  }
  SumProto(points);
}
```

Non-protobuf version:

```protobuf
struct PointStruct {
  int x;
  int y;
};

void SumVector(const std::vector<PointStruct>& vec) {
  int sum = 0;
  for (const PointStruct& p : vec) {
    sum += p.y;
  }
  ABSL_VLOG(1) << sum;
}

void BenchmarkIteration() {
  std::vector<PointStruct> points;
  points.reserve(1000);
  for (int i = 0; i < 1000; i++) {
    points.push_back({i, i * 2});
  }
  SumVector(points);
}
```

In addition, the protobuf version adds a few kilobytes of code and data to the binary, which may not seem like much, but adds up quickly in systems with many protobuf types. This increased size creates performance problems by creating i-cache and d-cache pressure.

Here are some tips related to protobuf performance:

Do not use protobufs unnecessarily.

Given the factor of 20 performance difference described above, if some data is never serialized or parsed, you probably should not put it in a protocol buffer. The purpose of protocol buffers is to make it easy to serialize and deserialize data structures, but they can have significant code-size, memory, and CPU overheads. Do not use them if all you want are some of the other niceties like `DebugString` and copyability.

Avoid unnecessary message hierarchies.

Message hierarchy can be useful to organize information in a more readable fashion. However, the extra level of message hierarchy incurs overheads like memory allocations, function calls, cache misses, larger serialized messages, etc.

E.g., instead of:

```protobuf
message Foo {
  optional Bar bar = 1;
}
message Bar {
  optional Baz baz = 1;
}
message Baz {
  optional int32 count = 1;
}
```

Prefer:

```protobuf
message Foo {
  optional int32 count = 1;
}
```

A protocol buffer message corresponds to a message class in C++ generated code and emits a tag and the length of the payload on the wire. To carry an integer, the old form requires more allocations (and deallocations) and emits a larger amount of generated code. As a result, all protocol buffer operations (parsing, serialization, size, etc.) become more expensive, having to traverse the message tree. The new form does not have such overhead and is more efficient.

Use small field numbers for frequently occurring fields.

Protobufs use a variable length integer representation for the combination of field number and wire format (see the [protobuf encoding documentation](https://protobuf.dev/programming-guides/encoding/)). This representation is 1 byte for field numbers between 1 and 15, and two bytes for field numbers between 16 and 2047. (Field numbers 2048 or greater should typically be avoided.)

Consider pre-reserving some small field numbers for future extension of performance-sensitive protobufs.

Choose carefully between int32, sint32, fixed32, and uint32 (and similarly for the 64 bit variants).

Generally, use `int32` or `int64`, but use `fixed32` or `fixed64` for large values like hash codes and `sint32` or `sint64` for values are that are often negative.

A varint occupies fewer bytes to encode small integers and can save space at the cost of more expensive decoding. However, it can take up more space for negative or large values. In that case, using fixed32 or fixed64 (instead of uint32 or uint64) reduces size with much cheaper encoding and decoding. For small negative integers, use sint32 or sint64 instead of int32 or int64.d

For proto2, pack repeated numeric fields by annotating them with `[packed=true]`.

In proto2, repeated values are serialized as a sequence of (tag, value) pairs by default. This is inefficient because tags have to be decoded for every element.

Packed repeated primitives are serialized with the length of the payload first followed by values without tags. When using fixed-width values, we can avoid reallocations by knowing the final size the moment we start parsing; i.e., no reallocation cost. We still don't know how many varints are in the payload and may have to pay the reallocation cost.

In proto3, repeated fields are packed by default.

Packed works best with fixed-width values like fixed32, fixed64, float, double, etc. since the entire encoded length can be predetermined by multiplying the number of elements by the fixed value size, instead of having to calculate the length of each individual element.

Use `bytes` instead for `string` for binary data and large values.

The `string` type holds UTF8-encoded text, and can sometimes require validation. The `bytes` type can hold an arbitrary sequence of bytes (non-text data) and is often more appropriate as well as more efficient than `string`.

Consider `string_type = VIEW` to avoid copying.

Copying a big string or bytes field during parsing is expensive. Such cost can often be avoided by marking the field with `string_type = VIEW`.

```protobuf
message Image {
  ...
  bytes jpeg_encoding = 4 [features.(pb.cpp).string_type=VIEW];
}
```

Without the `VIEW` annotation, when the protocol buffer is parsed, the potentially large field contents are copied from the serialized protocol buffer to a string object in memory. Depending on the number of string or bytes fields and the size of those fields, the overhead of copying can be significant.

Instead of copying the big binary blobs, routines like `ParseFromStringWithAliasing` use `absl::string_view` to reference the original backing string. Note that the backing string (the serialized protocol buffer) must outlive the protocol buffer instance that contains the alias.

Consider using `Cord` for large fields to reduce copying costs.

Annotating large `bytes` and `string` fields with `[ctype=CORD]` may reduce copying costs. This annotation changes the representation of the field from `std::string` to `absl::Cord`. `absl::Cord` uses reference counting and tree-based storage to reduce copying and appending costs. If a protocol buffer is serialized to a cord, parsing a string or bytes field with `[ctype=CORD]` can avoid copying the field contents.

```protobuf
message Document {
  ...
  bytes html = 4 [ctype = CORD];
}
```

Performance of a Cord field depends on length distribution and access patterns. Use benchmarks to validate such changes.

Use protobuf arenas in C++ code.

Consider using arenas to save allocation and deallocation costs, especially for protobufs containing repeated, string, or message fields.

Message and string fields are heap-allocated (even if the top-level protocol buffer object is stack-allocated). If a protocol buffer message has a lot of sub message fields and string fields, allocation and deallocation cost can be significant. Arenas amortize allocation costs and makes deallocation virtually free. It also improves memory locality by allocating from contiguous chunks of memory.

Keep .proto files small

Do not put too many messages in a single .proto file. Once you rely on anything at all from a .proto file, the entire file will get pulled in by the linker even if it's mostly unused. This increases build times and binary sizes. You can use extensions and `Any` to avoid creating hard dependencies on big .proto files with many message types.

Consider storing protocol buffers in serialized form, even in memory.

In-memory protobuf objects have a large memory footprint (often 5x the wire format size), potentially spread across many cache lines. So if your application is going to keep many protobuf objects live for long periods of time, consider storing them in serialized form.

Avoid protobuf map fields.

Protobuf map fields have performance problems that usually outweigh the small syntactic convenience they provide. Prefer using non-protobuf maps initialized from protobuf contents:

msg.proto

```protobuf
map<string, bytes> env_variables = 5;
```

```protobuf
message Var {
  string key = 1;
  bytes value = 2;
}
repeated Var env_variables = 5;
```

Use protobuf message definition with a subset of the fields.

If you want to access only a few fields of a large message type, consider defining your own protocol buffer message type that mimics the original type, but only defines the fields that you care about. Here's an example:

```protobuf
message FullMessage {
  optional int32 field1 = 1;
  optional BigMessage field2 = 2;
  optional int32 field3 = 3;
  repeater AnotherBigMessage field4 = 4;
  ...
  optional int32 field100 = 100;
}
```

```cpp
message SubsetMessage {
  optional int32 field3 = 3;
  optional int32 field88 = 88;
}
```

By parsing a serialized `FullMessage` into a `SubsetMessage`, only two out of a hundred fields are parsed and others are treated as unknown fields. Consider using APIs that discard unknown fields to improve performance even more when appropriate.

Reuse protobuf objects when possible.

Declare protobuf objects outside loops so that their allocated storage can be reused across loop iterations.

## C++-Specific advice {#c-specific-advice}

### absl::flat_hash_map (and set) {#abslflat_hash_map-and-set}

[Absl hash tables](https://abseil.io/docs/cpp/guides/container) usually out-perform C++ standard library containers such as `std::map` and `std::unordered_map`.

Speed up LanguageFromCode (use absl::flat_hash_map instead of a \_\_gnu_cxx::hash_map).

languages.cc

<div class="old">

```cpp
class CodeToLanguage
    ...
    : public __gnu_cxx::hash_map<absl::string_view, i18n::languages::Language,
                                 CodeHash, CodeCompare> {
```

</div>

<div class="new">

```cpp
class CodeToLanguage
    ...
    : public absl::flat_hash_map<absl::string_view, i18n::languages::Language,
                                 CodeHash, CodeCompare> {
```

</div>

Benchmark results:

```cpp
name               old time/op  new time/op  delta
BM_CodeToLanguage  19.4ns ± 1%  10.2ns ± 3%  -47.47%  (p=0.000 n=8+10)
```

Speed up stats publish/unpublish (an older change, so uses dense_hash_map instead of absl::flat_hash_map, which did not exist at the time).

publish.cc

<div class="old">

```cpp
typedef hash_map<uint64, Publication*> PublicationMap;
static PublicationMap* publications = NULL;
```

</div>

<div class="new">

```cpp
typedef dense_hash_map<uint64, Publication*> PublicationMap;;
static PublicationMap* publications GUARDED_BY(mu) = NULL;
```

</div>

Use dense_hash_map instead of hash_map for keeping track of SelectServer alarms (would use absl::flat_hash_map today).

alarmer.h

<div class="old">

```cpp
typedef hash_map<int, Alarm*> AlarmList;
```

</div>

<div class="new">

```cpp
typedef dense_hash_map<int, Alarm*> AlarmList;
```

</div>
