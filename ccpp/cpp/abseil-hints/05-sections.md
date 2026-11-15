---
title: "Precompute expensive information once"
---

# Precompute expensive information once {#chapter}

[返回总目录](../abseil-hints)

### Precompute expensive information once {#precompute-expensive-information-once}

Precompute a TensorFlow graph execution node property that allows us to quickly rule out certain unusual cases.

executor.cc

<div class="old">

```cpp
struct NodeItem {
  ...
  bool kernel_is_expensive = false;  // True iff kernel->IsExpensive()
  bool kernel_is_async = false;      // True iff kernel->AsAsync() != nullptr
  bool is_merge = false;             // True iff IsMerge(node)
  ...
  if (IsEnter(node)) {
  ...
  } else if (IsExit(node)) {
  ...
  } else if (IsNextIteration(node)) {
  ...
  } else {
    // Normal path for most nodes
    ...
  }
```

</div>

<div class="new">

```cpp
struct NodeItem {
  ...
  bool kernel_is_expensive : 1;  // True iff kernel->IsExpensive()
  bool kernel_is_async : 1;      // True iff kernel->AsAsync() != nullptr
  bool is_merge : 1;             // True iff IsMerge(node)
  bool is_enter : 1;             // True iff IsEnter(node)
  bool is_exit : 1;              // True iff IsExit(node)
  bool is_control_trigger : 1;   // True iff IsControlTrigger(node)
  bool is_sink : 1;              // True iff IsSink(node)
  // True iff IsEnter(node) || IsExit(node) || IsNextIteration(node)
  bool is_enter_exit_or_next_iter : 1;
  ...
  if (!item->is_enter_exit_or_next_iter) {
    // Fast path for nodes types that don't need special handling
    DCHECK_EQ(input_frame, output_frame);
    ...
  } else if (item->is_enter) {
  ...
  } else if (item->is_exit) {
  ...
  } else {
    DCHECK(IsNextIteration(node));
    ...
  }
```

</div>

Precompute 256 element array and use during trigram initialization.

byte_trigram_classifier.cc

<div class="old">

```cpp
void ByteTrigramClassifier::VerifyModel(void) const {
  ProbT class_sums[num_classes_];
  for (int cls = 0; cls < num_classes_; cls++) {
    class_sums[cls] = 0;
  }
  for (ByteNgramId id = 0; id < trigrams_.num_trigrams(); id++) {
    for (int cls = 0; cls < num_classes_; ++cls) {
      class_sums[cls] += Prob(trigram_probs_[id].log_probs[cls]);
    }
  }
  ...
}                         
```

</div>

<div class="new">

```cpp
void ByteTrigramClassifier::VerifyModel(void) const {
  CHECK_EQ(sizeof(ByteLogProbT), 1);
  ProbT fast_prob[256];
  for (int b = 0; b < 256; b++) {
    fast_prob[b] = Prob(static_cast<ByteLogProbT>(b));
  }

  ProbT class_sums[num_classes_];
  for (int cls = 0; cls < num_classes_; cls++) {
    class_sums[cls] = 0;
  }
  for (ByteNgramId id = 0; id < trigrams_.num_trigrams(); id++) {
    for (int cls = 0; cls < num_classes_; ++cls) {
      class_sums[cls] += fast_prob[trigram_probs_[id].log_probs[cls]];
    }
  }
  ...
}                         
```

</div>

General advice: check for malformed inputs at module boundaries instead of repeating checks internally.

### Move expensive computations outside loops {#move-expensive-computations-outside-loops}

Move bounds computation outside loop.

literal_linearizer.cc

<div class="old">

```cpp
for (int64 i = 0; i < src_shape.dimensions(dimension_numbers.front());
     ++i) {
```

</div>

<div class="new">

```cpp
int64 dim_front = src_shape.dimensions(dimension_numbers.front());
const uint8* src_buffer_data = src_buffer.data();
uint8* dst_buffer_data = dst_buffer.data();
for (int64 i = 0; i < dim_front; ++i) {
```

</div>

### Defer expensive computation {#defer-expensive-computation}

Defer GetSubSharding call until needed, which reduces 43 seconds of CPU time to 2 seconds.

sharding_propagation.cc

<div class="old">

```cpp
HloSharding alternative_sub_sharding =
    user.sharding().GetSubSharding(user.shape(), {i});
if (user.operand(i) == &instruction &&
    hlo_sharding_util::IsShardingMoreSpecific(alternative_sub_sharding,
                                              sub_sharding)) {
  sub_sharding = alternative_sub_sharding;
}
```

</div>

<div class="new">

```cpp
if (user.operand(i) == &instruction) {
  // Only evaluate GetSubSharding if this operand is of interest,
  // as it is relatively expensive.
  HloSharding alternative_sub_sharding =
      user.sharding().GetSubSharding(user.shape(), {i});
  if (hlo_sharding_util::IsShardingMoreSpecific(
          alternative_sub_sharding, sub_sharding)) {
    sub_sharding = alternative_sub_sharding;
  }
}
```

</div>

Don't update stats eagerly; compute them on demand.

Do not update stats on the very frequent allocation/deallocation calls. Instead, compute stats on demand when the much less frequently called Stats() method is invoked.

Preallocate 10 nodes not 200 for query handling in Google's web server.

A simple change that reduced web server's CPU usage by 7.5%.

querytree.h

<div class="old">

```cpp
static const int kInitParseTreeSize = 200;   // initial size of querynode pool
```

</div>

<div class="new">

```cpp
static const int kInitParseTreeSize = 10;   // initial size of querynode pool
```

</div>

Change search order for 19% throughput improvement.

An old search system (circa 2000) had two tiers: one contained a full-text index, and the other tier contained just the index for the title and anchor terms. We used to search the smaller title/anchor tier first. Counter-intuitively, we found that it is cheaper to search the larger full-text index tier first since if we reach the end of the full-text tier, we can entirely skip searching the title/anchor tier (a subset of the full-text tier). This happened reasonably often and allowed us to reduce the average number of disk seeks to process a query.

See discussion of title and anchor text handling in [The Anatomy of a Large-Scale Hypertextual Web Search Engine](https://research.google/pubs/the-anatomy-of-a-large-scale-hypertextual-web-search-engine/) for background information.

### Specialize code {#specialize-code}

A particular performance-sensitive call-site may not need the full generality provided by a general-purpose library. Consider writing specialized code in such cases instead of calling the general-purpose code if it provides a performance improvement.

Custom printing code for Histogram class is 4x as fast as sprintf.

This code is performance sensitive because it is invoked when monitoring systems gather statistics from various servers.

histogram_export.cc

<div class="old">

```cpp
void Histogram::PopulateBuckets(const string &prefix,
                                expvar::MapProto *const var) const {
                                ...
  for (int i = min_bucket; i <= max_bucket; ++i) {
    const double count = BucketCount(i);
    if (!export_empty_buckets && count == 0.0) continue;
    acc += count;
    // The label format of exported buckets for discrete histograms
    // specifies an inclusive upper bound, which is the same as in
    // the original Histogram implementation.  This format is not
    // applicable to non-discrete histograms, so a half-open interval
    // is used for them, with "_" instead of "-" as a separator to
    // make possible to distinguish the formats.
    string key =
        options_.export_cumulative_counts() ?
            StringPrintf("%.12g", boundaries_->BucketLimit(i)) :
        options_.discrete() ?
            StringPrintf("%.0f-%.0f",
                         ceil(boundaries_->BucketStart(i)),
                         ceil(boundaries_->BucketLimit(i)) - 1.0) :
            StringPrintf("%.12g_%.12g",
                         boundaries_->BucketStart(i),
                         boundaries_->BucketLimit(i));
    EscapeMapKey(&key);
    const double value = options_.export_cumulative_counts() ? acc : count;
    expvar::AddMapFloat(StrCat(prefix,
                               options_.export_bucket_key_prefix(),
                               key),
                        value * count_mult,
                        var);
  }
```

</div>

<div class="new">

```cpp
// Format "val" according to format.  If "need_escape" is true, then the
// format can produce output with a '.' in it, and the result will be escaped.
// If "need_escape" is false, then the caller guarantees that format is
// such that the resulting number will not have any '.' characters and
// therefore we can avoid calling EscapeKey.
// The function is free to use "*scratch" for scratch space if necessary,
// and the resulting StringPiece may point into "*scratch".
static StringPiece FormatNumber(const char* format,
                                bool need_escape,
                                double val, string* scratch) {
  // This routine is specialized to work with only a limited number of formats
  DCHECK(StringPiece(format) == "%.0f" || StringPiece(format) == "%.12g");

  scratch->clear();
  if (val == trunc(val) && val >= kint32min && val <= kint32max) {
    // An integer for which we can just use StrAppend
    StrAppend(scratch, static_cast<int32>(val));
    return StringPiece(*scratch);
  } else if (isinf(val)) {
    // Infinity, represent as just 'inf'.
    return StringPiece("inf", 3);
  } else {
    // Format according to "format", and possibly escape.
    StringAppendF(scratch, format, val);
    if (need_escape) {
      EscapeMapKey(scratch);
    } else {
      DCHECK(!StringPiece(*scratch).contains("."));
    }
    return StringPiece(*scratch);
  }
}
...
void Histogram::PopulateBuckets(const string &prefix,
                                expvar::MapProto *const var) const {
                                ...
  const string full_key_prefix = StrCat(prefix,
                                        options_.export_bucket_key_prefix());
  string key = full_key_prefix;  // Keys will start with "full_key_prefix".
  string start_scratch;
  string limit_scratch;
  const bool cumul_counts = options_.export_cumulative_counts();
  const bool discrete = options_.discrete();
  for (int i = min_bucket; i <= max_bucket; ++i) {
    const double count = BucketCount(i);
    if (!export_empty_buckets && count == 0.0) continue;
    acc += count;
    // The label format of exported buckets for discrete histograms
    // specifies an inclusive upper bound, which is the same as in
    // the original Histogram implementation.  This format is not
    // applicable to non-discrete histograms, so a half-open interval
    // is used for them, with "_" instead of "-" as a separator to
    // make possible to distinguish the formats.
    key.resize(full_key_prefix.size());  // Start with full_key_prefix.
    DCHECK_EQ(key, full_key_prefix);

    const double limit = boundaries_->BucketLimit(i);
    if (cumul_counts) {
      StrAppend(&key, FormatNumber("%.12g", true, limit, &limit_scratch));
    } else {
      const double start = boundaries_->BucketStart(i);
      if (discrete) {
        StrAppend(&key,
                  FormatNumber("%.0f", false, ceil(start), &start_scratch),
                  "-",
                  FormatNumber("%.0f", false, ceil(limit) - 1.0,
                               &limit_scratch));
      } else {
        StrAppend(&key,
                  FormatNumber("%.12g", true, start, &start_scratch),
                  "_",
                  FormatNumber("%.12g", true, limit, &limit_scratch));
      }
    }
    const double value = cumul_counts ? acc : count;

    // Add to map var
    expvar::AddMapFloat(key, value * count_mult, var);
  }
}
```

</div>

Add specializations for VLOG(1), VLOG(2), … for speed and smaller code size.

`VLOG` is a heavily used macro throughout the code base. This change avoids passing an extra integer constant at nearly every call site (if the log level is constant at the call site, as it almost always is, as in `VLOG(1) << ...`), which saves code space.

vlog_is_on.h

<div class="old">

```cpp
class VLogSite final {
 public:
  ...
  bool IsEnabled(int level) {
    int stale_v = v_.load(std::memory_order_relaxed);
    if (ABSL_PREDICT_TRUE(level > stale_v)) {
      return false;
    }

    // We put everything other than the fast path, i.e. vlogging is initialized
    // but not on, behind an out-of-line function to reduce code size.
    return SlowIsEnabled(stale_v, level);
  }
  ...
 private:
  ...
  ABSL_ATTRIBUTE_NOINLINE
  bool SlowIsEnabled(int stale_v, int level);
  ...
};
```

</div>

<div class="new">

```cpp
class VLogSite final {
 public:
  ...
  bool IsEnabled(int level) {
    int stale_v = v_.load(std::memory_order_relaxed);
    if (ABSL_PREDICT_TRUE(level > stale_v)) {
      return false;
    }

    // We put everything other than the fast path, i.e. vlogging is initialized
    // but not on, behind an out-of-line function to reduce code size.
    // "level" is almost always a call-site constant, so we can save a bit
    // of code space by special-casing for levels 1, 2, and 3.
#if defined(__has_builtin) && __has_builtin(__builtin_constant_p)
    if (__builtin_constant_p(level)) {
      if (level == 0) return SlowIsEnabled0(stale_v);
      if (level == 1) return SlowIsEnabled1(stale_v);
      if (level == 2) return SlowIsEnabled2(stale_v);
      if (level == 3) return SlowIsEnabled3(stale_v);
      if (level == 4) return SlowIsEnabled4(stale_v);
      if (level == 5) return SlowIsEnabled5(stale_v);
    }
#endif
    return SlowIsEnabled(stale_v, level);
    ...
 private:
  ...
  ABSL_ATTRIBUTE_NOINLINE
  bool SlowIsEnabled(int stale_v, int level);
  ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled0(int stale_v);
  ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled1(int stale_v);
  ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled2(int stale_v);
  ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled3(int stale_v);
  ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled4(int stale_v);
  ABSL_ATTRIBUTE_NOINLINE bool SlowIsEnabled5(int stale_v);
  ...
};
```

</div>

vlog_is_on.cc

<div class="new">

```cpp
bool VLogSite::SlowIsEnabled0(int stale_v) { return SlowIsEnabled(stale_v, 0); }
bool VLogSite::SlowIsEnabled1(int stale_v) { return SlowIsEnabled(stale_v, 1); }
bool VLogSite::SlowIsEnabled2(int stale_v) { return SlowIsEnabled(stale_v, 2); }
bool VLogSite::SlowIsEnabled3(int stale_v) { return SlowIsEnabled(stale_v, 3); }
bool VLogSite::SlowIsEnabled4(int stale_v) { return SlowIsEnabled(stale_v, 4); }
bool VLogSite::SlowIsEnabled5(int stale_v) { return SlowIsEnabled(stale_v, 5); }
```

</div>

Replace RE2 call with a simple prefix match when possible.

read_matcher.cc

<div class="old">

```cpp
enum MatchItemType {
  MATCH_TYPE_INVALID,
  MATCH_TYPE_RANGE,
  MATCH_TYPE_EXACT,
  MATCH_TYPE_REGEXP,
};
```

</div>

<div class="new">

```cpp
enum MatchItemType {
  MATCH_TYPE_INVALID,
  MATCH_TYPE_RANGE,
  MATCH_TYPE_EXACT,
  MATCH_TYPE_REGEXP,
  MATCH_TYPE_PREFIX,   // Special type for regexp ".*"
};
```

</div>

read_matcher.cc

<div class="old">

```cpp
p->type = MATCH_TYPE_REGEXP;
```

</div>

<div class="new">

```cpp
term.NonMetaPrefix().CopyToString(&p->prefix);
if (term.RegexpSuffix() == ".*") {
  // Special case for a regexp that matches anything, so we can
  // bypass RE2::FullMatch
  p->type = MATCH_TYPE_PREFIX;
} else {
  p->type = MATCH_TYPE_REGEXP;
```

</div>

Use StrCat rather than StringPrintf to format IP addresses.

ipaddress.cc

<div class="old">

```cpp
string IPAddress::ToString() const {
  char buf[INET6_ADDRSTRLEN];

  switch (address_family_) {
    case AF_INET:
      CHECK(inet_ntop(AF_INET, &addr_.addr4, buf, INET6_ADDRSTRLEN) != NULL);
      return buf;
    case AF_INET6:
      CHECK(inet_ntop(AF_INET6, &addr_.addr6, buf, INET6_ADDRSTRLEN) != NULL);
      return buf;
    case AF_UNSPEC:
      LOG(DFATAL) << "Calling ToString() on an empty IPAddress";
      return "";
    default:
      LOG(FATAL) << "Unknown address family " << address_family_;
  }
}
...
string IPAddressToURIString(const IPAddress& ip) {
  switch (ip.address_family()) {
    case AF_INET6:
      return StringPrintf("[%s]", ip.ToString().c_str());
    default:
      return ip.ToString();
  }
}
...
string SocketAddress::ToString() const {
  return IPAddressToURIString(host_) + StringPrintf(":%u", port_);
}
```

</div>

<div class="new">

```cpp
string IPAddress::ToString() const {
  char buf[INET6_ADDRSTRLEN];

  switch (address_family_) {
    case AF_INET: {
      uint32 addr = gntohl(addr_.addr4.s_addr);
      int a1 = static_cast<int>((addr >> 24) & 0xff);
      int a2 = static_cast<int>((addr >> 16) & 0xff);
      int a3 = static_cast<int>((addr >> 8) & 0xff);
      int a4 = static_cast<int>(addr & 0xff);
      return StrCat(a1, ".", a2, ".", a3, ".", a4);
    }
    case AF_INET6:
      CHECK(inet_ntop(AF_INET6, &addr_.addr6, buf, INET6_ADDRSTRLEN) != NULL);
      return buf;
    case AF_UNSPEC:
      LOG(DFATAL) << "Calling ToString() on an empty IPAddress";
      return "";
    default:
      LOG(FATAL) << "Unknown address family " << address_family_;
  }
}
...
string IPAddressToURIString(const IPAddress& ip) {
  switch (ip.address_family()) {
    case AF_INET6:
      return StrCat("[", ip.ToString(), "]");
    default:
      return ip.ToString();
  }
}
...
string SocketAddress::ToString() const {
  return StrCat(IPAddressToURIString(host_), ":", port_);
}
```

</div>
