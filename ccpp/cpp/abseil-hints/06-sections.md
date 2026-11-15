---
title: "Use caching to avoid repeated work"
description: "Use caching to avoid repeated work的内容说明与阅读参考。"
---

# Use caching to avoid repeated work {#chapter}

[返回总目录](../abseil-hints)

### Use caching to avoid repeated work {#use-caching-to-avoid-repeated-work}

Cache based on precomputed fingerprint of large serialized proto.

dp_ops.cc

<div class="old">

```cpp
InputOutputMappingProto mapping_proto;
PLAQUE_OP_REQUIRES(
    mapping_proto.ParseFromStringPiece(GetAttrMappingProto(state)),
    absl::InternalError("Failed to parse InputOutputMappingProto"));
ParseMapping(mapping_proto);
```

</div>

<div class="new">

```cpp
uint64 mapping_proto_fp = GetAttrMappingProtoFp(state);
{
  absl::MutexLock l(&fp_to_iometa_mu);
  if (fp_to_iometa == nullptr) {
    fp_to_iometa =
        new absl::flat_hash_map<uint64, std::unique_ptr<ProgramIOMetadata>>;
  }
  auto it = fp_to_iometa->find(mapping_proto_fp);
  if (it != fp_to_iometa->end()) {
    io_metadata_ = it->second.get();
  } else {
    auto serial_proto = GetAttrMappingProto(state);
    DCHECK_EQ(mapping_proto_fp, Fingerprint(serial_proto));
    InputOutputMappingProto mapping_proto;
    PLAQUE_OP_REQUIRES(
        mapping_proto.ParseFromStringPiece(GetAttrMappingProto(state)),
        absl::InternalError("Failed to parse InputOutputMappingProto"));
    auto io_meta = ParseMapping(mapping_proto);
    io_metadata_ = io_meta.get();
    (*fp_to_iometa)[mapping_proto_fp] = std::move(io_meta);
  }
}
```

</div>

### Make the compiler’s job easier {#make-the-compilers-job-easier}

The compiler may have trouble optimizing through layers of abstractions because it must make conservative assumptions about the overall behavior of the code, or may not make the right speed vs. size tradeoffs. The application programmer will often know more about the behavior of the system and can aid the compiler by rewriting the code to operate at a lower level. However, only do this when profiles show an issue since compilers will often get things right on their own. Looking at the generated assembly code for performance critical routines can help you understand if the compiler is “getting it right”. Pprof provides a very helpful [display of source code interleaved with disassembly](https://github.com/google/pprof/blob/main/doc/README.md#annotated-source-code) and annotated with performance data.

Some techniques that may be useful:

1.  Avoid functions calls in hot functions (allows the compiler to avoid frame setup costs).
2.  Move slow-path code into a separate tail-called function.
3.  Copy small amounts of data into local variables before heavy use. This can let the compiler assume there is no aliasing with other data, which may improve auto-vectorization and register allocation.
4.  Hand-unroll very hot loops.

Speed up ShapeUtil::ForEachState by replacing absl::Span with raw pointers to the underlying arrays.

shape_util.h

<div class="old">

```cpp
struct ForEachState {
  ForEachState(const Shape& s, absl::Span<const int64_t> b,
               absl::Span<const int64_t> c, absl::Span<const int64_t> i);
  ~ForEachState();

  const Shape& shape;
  const absl::Span<const int64_t> base;
  const absl::Span<const int64_t> count;
  const absl::Span<const int64_t> incr;
```

</div>

<div class="new">

```cpp
struct ForEachState {
  ForEachState(const Shape& s, absl::Span<const int64_t> b,
               absl::Span<const int64_t> c, absl::Span<const int64_t> i);
  inline ~ForEachState() = default;

  const Shape& shape;
  // Pointers to arrays of the passed-in spans
  const int64_t* const base;
  const int64_t* const count;
  const int64_t* const incr;
```

</div>

Hand unroll [cyclic redundancy check](https://en.wikipedia.org/wiki/Cyclic_redundancy_check) (CRC) computation loop.

crc.cc

<div class="old">

```cpp
void CRC32::Extend(uint64 *lo, uint64 *hi, const void *bytes, size_t length)
                      const {
                      ...
  // Process bytes 4 at a time
  while ((p + 4) <= e) {
    uint32 c = l ^ WORD(p);
    p += 4;
    l = this->table3_[c & 0xff] ^
        this->table2_[(c >> 8) & 0xff] ^
        this->table1_[(c >> 16) & 0xff] ^
        this->table0_[c >> 24];
  }

  // Process the last few bytes
  while (p != e) {
    int c = (l & 0xff) ^ *p++;
    l = this->table0_[c] ^ (l >> 8);
  }
  *lo = l;
}
```

</div>

<div class="new">

```cpp
void CRC32::Extend(uint64 *lo, uint64 *hi, const void *bytes, size_t length)
                      const {
                      ...
#define STEP {                                  \
    uint32 c = l ^ WORD(p);                     \
    p += 4;                                     \
    l = this->table3_[c & 0xff] ^               \
        this->table2_[(c >> 8) & 0xff] ^        \
        this->table1_[(c >> 16) & 0xff] ^       \
        this->table0_[c >> 24];                 \
}

  // Process bytes 16 at a time
  while ((e-p) >= 16) {
    STEP;
    STEP;
    STEP;
    STEP;
  }

  // Process bytes 4 at a time
  while ((p + 4) <= e) {
    STEP;
  }
#undef STEP

  // Process the last few bytes
  while (p != e) {
    int c = (l & 0xff) ^ *p++;
    l = this->table0_[c] ^ (l >> 8);
  }
  *lo = l;
}
```

</div>

Handle four characters at a time when parsing Spanner keys.

1.  Hand unroll loop to deal with four characters at a time rather than using memchr

2.  Manually unroll loop for finding separated sections of name

3.  Go backwards to find separated portions of a name with '#' separators (rather than forwards) since the first part is likely the longest in the name.

key.cc

<div class="old">

```cpp
void Key::InitSeps(const char* start) {
  const char* base = &rep_[0];
  const char* limit = base + rep_.size();
  const char* s = start;

  DCHECK_GE(s, base);
  DCHECK_LT(s, limit);

  for (int i = 0; i < 3; i++) {
    s = (const char*)memchr(s, '#', limit - s);
    DCHECK(s != NULL);
    seps_[i] = s - base;
    s++;
  }
}
```

</div>

<div class="new">

```cpp
inline const char* ScanBackwardsForSep(const char* base, const char* p) {
  while (p >= base + 4) {
    if (p[0] == '#') return p;
    if (p[-1] == '#') return p-1;
    if (p[-2] == '#') return p-2;
    if (p[-3] == '#') return p-3;
    p -= 4;
  }
  while (p >= base && *p != '#') p--;
  return p;
}

void Key::InitSeps(const char* start) {
  const char* base = &rep_[0];
  const char* limit = base + rep_.size();
  const char* s = start;

  DCHECK_GE(s, base);
  DCHECK_LT(s, limit);

  // We go backwards from the end of the string, rather than forwards,
  // since the directory name might be long and definitely doesn't contain
  // any '#' characters.
  const char* p = ScanBackwardsForSep(s, limit - 1);
  DCHECK(*p == '#');
  seps_[2] = p - base;
  p--;

  p = ScanBackwardsForSep(s, p);
  DCHECK(*p == '#');
  seps_[1] = p - base;
  p--;

  p = ScanBackwardsForSep(s, p);
  DCHECK(*p == '#');
  seps_[0] = p - base;
}
```

</div>

Avoid frame setup costs by converting ABSL_LOG(FATAL) to ABSL_DCHECK(false).

arena_cleanup.h

<div class="old">

```cpp
inline ABSL_ATTRIBUTE_ALWAYS_INLINE size_t Size(Tag tag) {
  if (!EnableSpecializedTags()) return sizeof(DynamicNode);

  switch (tag) {
    case Tag::kDynamic:
      return sizeof(DynamicNode);
    case Tag::kString:
      return sizeof(TaggedNode);
    case Tag::kCord:
      return sizeof(TaggedNode);
    default:
      ABSL_LOG(FATAL) << "Corrupted cleanup tag: " << static_cast<int>(tag);
      return sizeof(DynamicNode);
  }
}
```

</div>

<div class="new">

```cpp
inline ABSL_ATTRIBUTE_ALWAYS_INLINE size_t Size(Tag tag) {
  if (!EnableSpecializedTags()) return sizeof(DynamicNode);

  switch (tag) {
    case Tag::kDynamic:
      return sizeof(DynamicNode);
    case Tag::kString:
      return sizeof(TaggedNode);
    case Tag::kCord:
      return sizeof(TaggedNode);
    default:
      ABSL_DCHECK(false) << "Corrupted cleanup tag: " << static_cast<int>(tag);
      return sizeof(DynamicNode);
  }
}
```

</div>

### Reduce stats collection costs {#reduce-stats-collection-costs}

Balance the utility of stats and other behavioral information about a system against the cost of maintaining that information. The extra information can often help people to understand and improve high-level behavior, but can also be costly to maintain.

Stats that are not useful can be dropped altogether.

Stop maintaining expensive stats about number of alarms and closures in SelectServer.

Part of changes that reduce time for setting an alarm from 771 ns to 271 ns.

selectserver.h

<div class="old">

```cpp
class SelectServer {
 public:
 ...
 protected:
  ...
  scoped_ptr<MinuteTenMinuteHourStat> num_alarms_stat_;
  ...
  scoped_ptr<MinuteTenMinuteHourStat> num_closures_stat_;
  ...
};
```

</div>

<div class="new">

```cpp
// Selectserver class
class SelectServer {
 ...
 protected:
 ...
};
```

</div>

/selectserver.cc

<div class="old">

```cpp
void SelectServer::AddAlarmInternal(Alarmer* alarmer,
                                    int offset_in_ms,
                                    int id,
                                    bool is_periodic) {
                                    ...
  alarms_->insert(alarm);
  num_alarms_stat_->IncBy(1);
  ...
}
```

</div>

<div class="new">

```cpp
void SelectServer::AddAlarmInternal(Alarmer* alarmer,
                                    int offset_in_ms,
                                    int id,
                                    bool is_periodic) {
                                    ...
  alarms_->Add(alarm);
  ...
}
```

</div>

/selectserver.cc

<div class="old">

```cpp
void SelectServer::RemoveAlarm(Alarmer* alarmer, int id) {
      ...
      alarms_->erase(alarm);
      num_alarms_stat_->IncBy(-1);
      ...
}
```

</div>

<div class="new">

```cpp
void SelectServer::RemoveAlarm(Alarmer* alarmer, int id) {
      ...
      alarms_->Remove(alarm);
      ...
}
```

</div>

Often, stats or other properties can be maintained for a sample of the elements handled by the system (e.g., RPC requests, input records, users). Many subsystems use this approach (tcmalloc allocation tracking, /requestz status pages, Dapper samples).

When sampling, consider reducing the sampling rate when appropriate.

Maintain stats for just a sample of doc info requests.

Sampling allows us to avoid touching 39 histograms and MinuteTenMinuteHour stats for most requests.

generic-leaf-stats.cc

```cpp
... code that touches 39 histograms to update various stats on every request ...
```

```cpp
// Add to the histograms periodically
if (TryLockToUpdateHistogramsDocInfo(docinfo_stats, bucket)) {
  // Returns true and grabs bucket->lock only if we should sample this
  // request for maintaining stats
  ... code that touches 39 histograms to update various stats ...
  bucket->lock.Unlock();
}
```

Reduce sampling rate and make faster sampling decisions.

This change reduces the sampling rate from 1 in 10 to 1 in 32. Furthermore, we now keep execution time stats just for the sampled events and speed up sampling decisions by using a power of two modulus. This code is called on every packet in the Google Meet video conferencing system and needed performance work to keep up with capacity demands during the first part of the COVID outbreak as users rapidly migrated to doing more online meetings.

packet_executor.cc

<div class="old">

```cpp
class ScopedPerformanceMeasurement {
 public:
  explicit ScopedPerformanceMeasurement(PacketExecutor* packet_executor)
      : packet_executor_(packet_executor),
        tracer_(packet_executor->packet_executor_trace_threshold_,
                kClosureTraceName) {
    // ThreadCPUUsage is an expensive call. At the time of writing,
    // it takes over 400ns, or roughly 30 times slower than absl::Now,
    // so we sample only 10% of closures to keep the cost down.
    if (packet_executor->closures_executed_ % 10 == 0) {
      thread_cpu_usage_start_ = base::ThreadCPUUsage();
    }

    // Sample start time after potentially making the above expensive call,
    // so as not to pollute wall time measurements.
    run_start_time_ = absl::Now();
  }

  ~ScopedPerformanceMeasurement() {
```

</div>

<div class="new">

```cpp
ScopedPerformanceMeasurement::ScopedPerformanceMeasurement(
    PacketExecutor* packet_executor)
    : packet_executor_(packet_executor),
      tracer_(packet_executor->packet_executor_trace_threshold_,
              kClosureTraceName) {
  // ThreadCPUUsage is an expensive call. At the time of writing,
  // it takes over 400ns, or roughly 30 times slower than absl::Now,
  // so we sample only 1 in 32 closures to keep the cost down.
  if (packet_executor->closures_executed_ % 32 == 0) {
    thread_cpu_usage_start_ = base::ThreadCPUUsage();
  }

  // Sample start time after potentially making the above expensive call,
  // so as not to pollute wall time measurements.
  run_start_time_ = absl::Now();
}
```

</div>

packet_executor.cc

<div class="old">

```cpp
~ScopedPerformanceMeasurement() {
  auto run_end_time = absl::Now();
  auto run_duration = run_end_time - run_start_time_;

  if (thread_cpu_usage_start_.has_value()) {
  ...
  }

  closure_execution_time->Record(absl::ToInt64Microseconds(run_duration));
```

</div>

<div class="new">

```cpp
ScopedPerformanceMeasurement::~ScopedPerformanceMeasurement() {
  auto run_end_time = absl::Now();
  auto run_duration = run_end_time - run_start_time_;

  if (thread_cpu_usage_start_.has_value()) {
    ...
    closure_execution_time->Record(absl::ToInt64Microseconds(run_duration));
  }
```

</div>

Benchmark results:

```cpp
Run on (40 X 2793 MHz CPUs); 2020-03-24T20:08:19.991412535-07:00
CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_PacketOverhead_mean                               224          85    +62.0%
```
