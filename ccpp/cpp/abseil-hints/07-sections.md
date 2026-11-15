---
title: "Avoid logging on hot code paths"
description: "Avoid logging on hot code paths：Code size considerations。"
---

# Avoid logging on hot code paths {#chapter}

[返回总目录](../abseil-hints)

### Avoid logging on hot code paths {#avoid-logging-on-hot-code-paths}

Logging statements can be costly, even if the logging-level for the statement doesn’t actually log anything. E.g., `ABSL_VLOG`’s implementation requires at least a load and a comparison, which may be a problem in hot code paths. In addition, the presence of the logging code may inhibit compiler optimizations. Consider dropping logging entirely from hot code paths.

Remove logging from guts of memory allocator.

This was a small part of a larger change.

gpu_bfc_allocator.cc

```cpp
void GPUBFCAllocator::SplitChunk(...) {
  ...
  VLOG(6) << "Adding to chunk map: " << new_chunk->ptr;
  ...
}
...
void GPUBFCAllocator::DeallocateRawInternal(void* ptr) {
  ...
  VLOG(6) << "Chunk at " << c->ptr << " no longer in use";
  ...
}
```

```cpp
void GPUBFCAllocator::SplitChunk(...) {
...
}
...
void GPUBFCAllocator::DeallocateRawInternal(void* ptr) {
...
}
```

Precompute whether or not logging is enabled outside a nested loop.

image_similarity.cc

<div class="old">

```cpp
for (int j = 0; j < output_subimage_size_y; j++) {
  int j1 = j - rad + output_to_integral_subimage_y;
  int j2 = j1 + 2 * rad + 1;
  // Create a pointer for this row's output, taking into account the offset
  // to the full image.
  double *image_diff_ptr = &(*image_diff)(j + min_j, min_i);

  for (int i = 0; i < output_subimage_size_x; i++) {
    ...
    if (VLOG_IS_ON(3)) {
    ...
    }
    ...
  }
}
```

</div>

<div class="new">

```cpp
const bool vlog_3 = DEBUG_MODE ? VLOG_IS_ON(3) : false;

for (int j = 0; j < output_subimage_size_y; j++) {
  int j1 = j - rad + output_to_integral_subimage_y;
  int j2 = j1 + 2 * rad + 1;
  // Create a pointer for this row's output, taking into account the offset
  // to the full image.
  double *image_diff_ptr = &(*image_diff)(j + min_j, min_i);

  for (int i = 0; i < output_subimage_size_x; i++) {
    ...
    if (vlog_3) {
    ...
    }
  }
}
```

</div>

```cpp
Run on (40 X 2801 MHz CPUs); 2016-05-16T15:55:32.250633072-07:00
CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                          Base (ns)  New (ns) Improvement
------------------------------------------------------------------
BM_NCCPerformance/16                   29104     26372     +9.4%
BM_NCCPerformance/64                  473235    425281    +10.1%
BM_NCCPerformance/512               30246238  27622009     +8.7%
BM_NCCPerformance/1k              125651445  113361991     +9.8%
BM_NCCLimitedBoundsPerformance/16       8314      7498     +9.8%
BM_NCCLimitedBoundsPerformance/64     143508    132202     +7.9%
BM_NCCLimitedBoundsPerformance/512   9335684   8477567     +9.2%
BM_NCCLimitedBoundsPerformance/1k   37223897  34201739     +8.1%
```

Precompute whether logging is enabled and use the result in helper routines.

periodic_call.cc

<div class="old">

```cpp
  VLOG(1) << Logid()
          << "MaybeScheduleAlarmAtNextTick. Time until next real time: "
          << time_until_next_real_time;
          ...
  uint64 next_virtual_time_ms =
      next_virtual_time_ms_ - num_ticks * kResolutionMs;
  CHECK_GE(next_virtual_time_ms, 0);
  ScheduleAlarm(now, delay, next_virtual_time_ms);
}

void ScheduleNextAlarm(uint64 current_virtual_time_ms)
    ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
  if (calls_.empty()) {
    VLOG(1) << Logid() << "No calls left, entering idle mode";
    next_real_time_ = absl::InfiniteFuture();
    return;
  }
  uint64 next_virtual_time_ms = FindNextVirtualTime(current_virtual_time_ms);
  auto delay =
      absl::Milliseconds(next_virtual_time_ms - current_virtual_time_ms);
  ScheduleAlarm(GetClock().TimeNow(), delay, next_virtual_time_ms);
}

// An alarm scheduled by this function supersedes all previously scheduled
// alarms. This is ensured through `scheduling_sequence_number_`.
void ScheduleAlarm(absl::Time now, absl::Duration delay,
                   uint64 virtual_time_ms)
    ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
  next_real_time_ = now + delay;
  next_virtual_time_ms_ = virtual_time_ms;
  ++ref_count_;  // The Alarm holds a reference.
  ++scheduling_sequence_number_;
  VLOG(1) << Logid() << "ScheduleAlarm. Time : "
          << absl::FormatTime("%M:%S.%E3f", now, absl::UTCTimeZone())
          << ", delay: " << delay << ", virtual time: " << virtual_time_ms
          << ", refs: " << ref_count_
          << ", seq: " << scheduling_sequence_number_
          << ", executor: " << executor_;

  executor_->AddAfter(
      delay, new Alarm(this, virtual_time_ms, scheduling_sequence_number_));
}
```

</div>

<div class="new">

```cpp
  const bool vlog_1 = VLOG_IS_ON(1);

  if (vlog_1) {
    VLOG(1) << Logid()
            << "MaybeScheduleAlarmAtNextTick. Time until next real time: "
            << time_until_next_real_time;
  }
  ...
  uint64 next_virtual_time_ms =
      next_virtual_time_ms_ - num_ticks * kResolutionMs;
  CHECK_GE(next_virtual_time_ms, 0);
  ScheduleAlarm(now, delay, next_virtual_time_ms, vlog_1);
}

void ScheduleNextAlarm(uint64 current_virtual_time_ms, bool vlog_1)
    ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
  if (calls_.empty()) {
    if (vlog_1) {
      VLOG(1) << Logid() << "No calls left, entering idle mode";
    }
    next_real_time_ = absl::InfiniteFuture();
    return;
  }
  uint64 next_virtual_time_ms = FindNextVirtualTime(current_virtual_time_ms);
  auto delay =
      absl::Milliseconds(next_virtual_time_ms - current_virtual_time_ms);
  ScheduleAlarm(GetClock().TimeNow(), delay, next_virtual_time_ms, vlog_1);
}

// An alarm scheduled by this function supersedes all previously scheduled
// alarms. This is ensured through `scheduling_sequence_number_`.
void ScheduleAlarm(absl::Time now, absl::Duration delay,
                   uint64 virtual_time_ms,
                   bool vlog_1)
    ABSL_EXCLUSIVE_LOCKS_REQUIRED(mutex_) {
  next_real_time_ = now + delay;
  next_virtual_time_ms_ = virtual_time_ms;
  ++ref_count_;  // The Alarm holds a reference.
  ++scheduling_sequence_number_;
  if (vlog_1) {
    VLOG(1) << Logid() << "ScheduleAlarm. Time : "
            << absl::FormatTime("%M:%S.%E3f", now, absl::UTCTimeZone())
            << ", delay: " << delay << ", virtual time: " << virtual_time_ms
            << ", refs: " << ref_count_
            << ", seq: " << scheduling_sequence_number_
            << ", executor: " << executor_;
  }

  executor_->AddAfter(
      delay, new Alarm(this, virtual_time_ms, scheduling_sequence_number_));
}
```

</div>

## Code size considerations {#code-size-considerations}

Performance encompasses more than just runtime speed. Sometimes it is worth considering the effects of software choices on the size of generated code. Large code size means longer compile and link times, bloated binaries, more memory usage, more icache pressure, and other sometimes negative effects on microarchitectural structures like branch predictors, etc. Thinking about these issues is especially important when writing low-level library code that will be used in many places, or when writing templated code that you expect will be instantiated for many different types.

The techniques that are useful for reducing code size vary significantly across programming languages. Here are some techniques that we have found useful for C++ code (which can suffer from an over-use of templates and inlining).

### Trim commonly inlined code {#trim-commonly-inlined-code}

Widely called functions combined with inlining can have a dramatic effect on code size.

Speed up TF_CHECK_OK.

Avoid creating Ok object, and save code space by doing complex formatting of fatal error message out of line instead of at every call site.

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

status.cc

<div class="new">

```cpp
string* TfCheckOpHelperOutOfLine(const ::tensorflow::Status& v,
                                 const char* msg) {
  string r("Non-OK-status: ");
  r += msg;
  r += " status: ";
  r += v.ToString();
  // Leaks string but this is only to be used in a fatal error message
  return new string(r);
}
```

</div>

Shrink each RETURN_IF_ERROR call site by 79 bytes of code.

1.  Added special adaptor class for use by just RETURN_IF_ERROR.
2.  Do not construct/destruct StatusBuilder on fast path of RETURN_IF_ERROR.
3.  Do not inline some StatusBuilder methods since they are now no longer needed on the fast path.
4.  Avoid unnecessary ~Status call.

Improve performance of CHECK_GE by 4.5X and shrink code size from 125 bytes to 77 bytes.

logging.h

<div class="old">

```cpp
struct CheckOpString {
  CheckOpString(string* str) : str_(str) { }
  ~CheckOpString() { delete str_; }
  operator bool() const { return str_ == NULL; }
  string* str_;
};
...
#define DEFINE_CHECK_OP_IMPL(name, op) \
  template <class t1, class t2> \
  inline string* Check##name##Impl(const t1& v1, const t2& v2, \
                                   const char* names) { \
    if (v1 op v2) return NULL; \
    else return MakeCheckOpString(v1, v2, names); \
  } \
  string* Check##name##Impl(int v1, int v2, const char* names);
DEFINE_CHECK_OP_IMPL(EQ, ==)
DEFINE_CHECK_OP_IMPL(NE, !=)
DEFINE_CHECK_OP_IMPL(LE, <=)
DEFINE_CHECK_OP_IMPL(LT, < )
DEFINE_CHECK_OP_IMPL(GE, >=)
DEFINE_CHECK_OP_IMPL(GT, > )
#undef DEFINE_CHECK_OP_IMPL
```

</div>

<div class="new">

```cpp
struct CheckOpString {
  CheckOpString(string* str) : str_(str) { }
  // No destructor: if str_ is non-NULL, we're about to LOG(FATAL),
  // so there's no point in cleaning up str_.
  operator bool() const { return str_ == NULL; }
  string* str_;
};
...
extern string* MakeCheckOpStringIntInt(int v1, int v2, const char* names);

template<int, int>
string* MakeCheckOpString(const int& v1, const int& v2, const char* names) {
  return MakeCheckOpStringIntInt(v1, v2, names);
}
...
#define DEFINE_CHECK_OP_IMPL(name, op) \
  template <class t1, class t2> \
  inline string* Check##name##Impl(const t1& v1, const t2& v2, \
                                   const char* names) { \
    if (v1 op v2) return NULL; \
    else return MakeCheckOpString(v1, v2, names); \
  } \
  inline string* Check##name##Impl(int v1, int v2, const char* names) { \
    if (v1 op v2) return NULL; \
    else return MakeCheckOpString(v1, v2, names); \
  }
DEFINE_CHECK_OP_IMPL(EQ, ==)
DEFINE_CHECK_OP_IMPL(NE, !=)
DEFINE_CHECK_OP_IMPL(LE, <=)
DEFINE_CHECK_OP_IMPL(LT, < )
DEFINE_CHECK_OP_IMPL(GE, >=)
DEFINE_CHECK_OP_IMPL(GT, > )
#undef DEFINE_CHECK_OP_IMPL
```

</div>

logging.cc

<div class="new">

```cpp
string* MakeCheckOpStringIntInt(int v1, int v2, const char* names) {
  strstream ss;
  ss << names << " (" << v1 << " vs. " << v2 << ")";
  return new string(ss.str(), ss.pcount());
}
```

</div>

### Inline with care {#inline-with-care}

Inlining can often improve performance, but sometimes it can increase code size without a corresponding performance payoff (and in some case even a performance loss due to increased instruction cache pressure).

Reduce inlining in TensorFlow.

The change stops inlining many non-performance-sensitive functions (e.g., error paths and op registration code). Furthermore, slow paths of some performance-sensitive functions are moved into non-inlined functions.

These changes reduces the size of tensorflow symbols in a typical binary by 12.2% (8814545 bytes down to 7740233 bytes)

Protocol buffer library change. Avoid expensive inlined code space for encoding message length for messages ≥ 128 bytes and instead do a procedure call to a shared out-of-line routine.

Not only makes important large binaries smaller but also faster.

Bytes of generated code per line of a heavily inlined routine in one large binary. First number represents the total bytes generated for a particular source line including all locations where that code has been inlined.

Before:

```cpp
.           0   1825 template <typename MessageType>
.           0   1826 inline uint8* WireFormatLite::InternalWriteMessage(
.           0   1827     int field_number, const MessageType& value, uint8* target,
.           0   1828     io::EpsCopyOutputStream* stream) {
>>>    389246   1829   target = WriteTagToArray(field_number, WIRETYPE_LENGTH_DELIMITED, target);
>>>   5454640   1830   target = io::CodedOutputStream::WriteVarint32ToArray(
>>>    337837   1831       static_cast<uint32>(value.GetCachedSize()), target);
>>>   1285539   1832   return value._InternalSerialize(target, stream);
.           0   1833 }
```

The new codesize output with this change looks like:

```cpp
.           0   1825 template <typename MessageType>
.           0   1826 inline uint8* WireFormatLite::InternalWriteMessage(
.           0   1827     int field_number, const MessageType& value, uint8* target,
.           0   1828     io::EpsCopyOutputStream* stream) {
>>>    450612   1829   target = WriteTagToArray(field_number, WIRETYPE_LENGTH_DELIMITED, target);
>>       9609   1830   target = io::CodedOutputStream::WriteVarint32ToArrayOutOfLine(
>>>    434668   1831       static_cast<uint32>(value.GetCachedSize()), target);
>>>   1597394   1832   return value._InternalSerialize(target, stream);
.           0   1833 }
```

coded_stream.h

<div class="new">

```cpp
class PROTOBUF_EXPORT CodedOutputStream {
  ...
  // Like WriteVarint32()  but writing directly to the target array, and with the
  // less common-case paths being out of line rather than inlined.
  static uint8* WriteVarint32ToArrayOutOfLine(uint32 value, uint8* target);
  ...
};
...
inline uint8* CodedOutputStream::WriteVarint32ToArrayOutOfLine(uint32 value,
                                                               uint8* target) {
  target[0] = static_cast<uint8>(value);
  if (value < 0x80) {
    return target + 1;
  } else {
    return WriteVarint32ToArrayOutOfLineHelper(value, target);
  }
}
```

</div>

coded_stream.cc

<div class="new">

```cpp
uint8* CodedOutputStream::WriteVarint32ToArrayOutOfLineHelper(uint32 value,
                                                              uint8* target) {
  DCHECK_GE(value, 0x80);
  target[0] |= static_cast<uint8>(0x80);
  value >>= 7;
  target[1] = static_cast<uint8>(value);
  if (value < 0x80) {
    return target + 2;
  }
  target += 2;
  do {
    // Turn on continuation bit in the byte we just wrote.
    target[-1] |= static_cast<uint8>(0x80);
    value >>= 7;
    *target = static_cast<uint8>(value);
    ++target;
  } while (value >= 0x80);
  return target;
}
```

</div>

Reduce absl::flat_hash_set and absl::flat_hash_map code size.

1.  Extract code that does not depend on the specific hash table type into common (non-inlined) functions.
2.  Place ABSL_ATTRIBUTE_NOINLINE directives judiciously.
3.  Out-of-line some slow paths.

Reduces sizes of some large binaries by ~0.5%.

Do not inline string allocation and deallocation when not using protobuf arenas.

public/arenastring.h

<div class="old">

```cpp
  if (IsDefault(default_value)) {
    std::string* new_string = new std::string();
    tagged_ptr_.Set(new_string);
    return new_string;
  } else {
    return UnsafeMutablePointer();
  }
}
```

</div>

<div class="new">

```cpp
  if (IsDefault(default_value)) {
    return SetAndReturnNewString();
  } else {
    return UnsafeMutablePointer();
  }
}
```

</div>

internal/arenastring.cc

<div class="new">

```cpp
std::string* ArenaStringPtr::SetAndReturnNewString() {
  std::string* new_string = new std::string();
  tagged_ptr_.Set(new_string);
  return new_string;
}
```

</div>

Avoid inlining some routines. Create variants of routines that take 'const char\*' rather than 'const std::string&' to avoid std::string construction code at every call site.

op.h

<div class="old">

```cpp
class OpDefBuilderWrapper {
 public:
  explicit OpDefBuilderWrapper(const char name[]) : builder_(name) {}
  OpDefBuilderWrapper& Attr(std::string spec) {
    builder_.Attr(std::move(spec));
    return *this;
  }
  OpDefBuilderWrapper& Input(std::string spec) {
    builder_.Input(std::move(spec));
    return *this;
  }
  OpDefBuilderWrapper& Output(std::string spec) {
    builder_.Output(std::move(spec));
    return *this;
  }
```

</div>

<div class="new">

```cpp
class OpDefBuilderWrapper {
 public:
  explicit OpDefBuilderWrapper(const char name[]) : builder_(name) {}
  OpDefBuilderWrapper& Attr(std::string spec) {
    builder_.Attr(std::move(spec));
    return *this;
  }
  OpDefBuilderWrapper& Attr(const char* spec) TF_ATTRIBUTE_NOINLINE {
    return Attr(std::string(spec));
  }
  OpDefBuilderWrapper& Input(std::string spec) {
    builder_.Input(std::move(spec));
    return *this;
  }
  OpDefBuilderWrapper& Input(const char* spec) TF_ATTRIBUTE_NOINLINE {
    return Input(std::string(spec));
  }
  OpDefBuilderWrapper& Output(std::string spec) {
    builder_.Output(std::move(spec));
    return *this;
  }
  OpDefBuilderWrapper& Output(const char* spec) TF_ATTRIBUTE_NOINLINE {
    return Output(std::string(spec));
  }
```

</div>
