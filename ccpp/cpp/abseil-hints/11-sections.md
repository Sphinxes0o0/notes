---
title: "Bulk operations"
description: "Bulk operations：Bulk operations、CLs that demonstrate multiple techniques、Further reading。"
---

# Bulk operations {#chapter}

[返回总目录](../abseil-hints)

## Bulk operations {#bulk-operations}

If possible, handle many items at once rather than just one at a time.

absl::flat_hash_map compares one hash byte per key from a group of keys using a single SIMD instruction.

See [Swiss Table Design Notes](https://abseil.io/about/design/swisstables) and related [CppCon 2017](https://www.youtube.com/watch?v=ncHmEUmJZf4) and [CppCon 2019](https://www.youtube.com/watch?v=JZE3_0qvrMg) talks by Matt Kulukundis.

raw_hash_set.h

<div class="new">

```cpp
// Returns a bitmask representing the positions of slots that match hash.
BitMask<uint32_t> Match(h2_t hash) const {
  auto ctrl = _mm_loadu_si128(reinterpret_cast<const __m128i*>(pos));
  auto match = _mm_set1_epi8(hash);
  return BitMask<uint32_t>(_mm_movemask_epi8(_mm_cmpeq_epi8(match, ctrl)));
}
```

</div>

Do single operations to deal with many bytes and fix things up, rather than checking every byte what to do.

ordered-code.cc

<div class="old">

```cpp
int len = 0;
while (val > 0) {
  len++;
  buf[9 - len] = (val & 0xff);
  val >>= 8;
}
buf[9 - len - 1] = (unsigned char)len;
len++;
FastStringAppend(dest, reinterpret_cast<const char*>(buf + 9 - len), len);
```

</div>

<div class="new">

```cpp
BigEndian::Store(val, buf + 1);  // buf[0] may be needed for length
const unsigned int length = OrderedNumLength(val);
char* start = buf + 9 - length - 1;
*start = length;
AppendUpto9(dest, start, length + 1);
```

</div>

Improve Reed-Solomon processing speed by handling multiple interleaved input buffers more efficiently in chunks.

```cpp
Run on (12 X 3501 MHz CPUs); 2016-09-27T16:04:55.065995192-04:00
CPU: Intel Haswell with HyperThreading (6 cores) dL1:32KB dL2:256KB dL3:15MB
Benchmark                          Base (ns)  New (ns) Improvement
------------------------------------------------------------------
BM_OneOutput/3/2                      466867    351818    +24.6%
BM_OneOutput/4/2                      563130    474756    +15.7%
BM_OneOutput/5/3                      815393    688820    +15.5%
BM_OneOutput/6/3                      897246    780539    +13.0%
BM_OneOutput/8/4                     1270489   1137149    +10.5%
BM_AllOutputs/3/2                     848772    642942    +24.3%
BM_AllOutputs/4/2                    1067647    638139    +40.2%
BM_AllOutputs/5/3                    1739135   1151369    +33.8%
BM_AllOutputs/6/3                    2045817   1456744    +28.8%
BM_AllOutputs/8/4                    3012958   2484937    +17.5%
BM_AllOutputsSetUpOnce/3/2            717310    493371    +31.2%
BM_AllOutputsSetUpOnce/4/2            833866    600060    +28.0%
BM_AllOutputsSetUpOnce/5/3           1537870   1137357    +26.0%
BM_AllOutputsSetUpOnce/6/3           1802353   1398600    +22.4%
BM_AllOutputsSetUpOnce/8/4           3166930   2455973    +22.4%
```

Decode four integers at a time (circa 2004).

Introduced a [GroupVarInt format](https://static.googleusercontent.com/media/research.google.com/en//people/jeff/WSDM09-keynote.pdf) that encodes/decodes groups of 4 variable-length integers at a time in 5-17 bytes, rather than one integer at a time. Decoding one group of 4 integers in the new format takes ~1/3rd the time of decoding 4 individually varint-encoded integers.

groupvarint.cc

<div class="new">

```cpp
const char* DecodeGroupVar(const char* p, int N, uint32* dest) {
  assert(groupvar_initialized);
  assert(N % 4 == 0);
  while (N) {
    uint8 tag = *p;
    p++;

    uint8* lenptr = &groupvar_table[tag].length[0];

#define GET_NEXT                                        \
    do {                                                \
      uint8 len = *lenptr;                              \
      *dest = UNALIGNED_LOAD32(p) & groupvar_mask[len]; \
      dest++;                                           \
      p += len;                                         \
      lenptr++;                                         \
    } while (0)
    GET_NEXT;
    GET_NEXT;
    GET_NEXT;
    GET_NEXT;
#undef GET_NEXT

    N -= 4;
  }
  return p;
}
```

</div>

Encode groups of 4 k-bit numbers at a time.

Added KBitStreamEncoder and KBitStreamDecoder classes to encode/decode 4 k-bit numbers at a time into a bit stream. Since K is known at compile time, the encoding and decoding can be quite efficient. E.g., since four numbers are encoded at a time, the code can assume that the stream is always byte-aligned (for even k), or nibble-aligned (for odd k).

## CLs that demonstrate multiple techniques {#cls-that-demonstrate-multiple-techniques}

Sometimes a single CL contains a number of performance-improving changes that use many of the preceding techniques. Looking at the kinds of changes in these CLs is sometimes a good way to get in the mindset of making general changes to speed up the performance of some part of a system after that has been identified as a bottleneck.

Speed up GPU memory allocator by ~40%.

36-48% speedup in allocation/deallocation speed for GPUBFCAllocator:

1.  Identify chunks by a handle number, rather than by a pointer to a Chunk. Chunk data structures are now allocated in a `vector<Chunk>`, and a handle is an index into this vector to refer to a particular chunk. This allows the next and prev pointers in Chunk to be ChunkHandle (4 bytes), rather than `Chunk*` (8 bytes).

2.  When a Chunk object is no longer in use, we maintain a free list of Chunk objects, whose head is designated by ChunkHandle `free_chunks_list_`, and with the `Chunk->next` pointing to the next free list entry. Together with (1), this allows us to avoid heap allocation/deallocation of Chunk objects in the allocator, except (rarely) when the `vector<Chunk>` grows. It also makes all the memory for Chunk objects contiguous.

3.  Rather than having the bins\_ data structure be a std::set and using lower_bound to locate the appropriate bin given a byte_size, we instead have an array of bins, indexed by a function that is log₂(byte_size/256). This allows the bin to be located with a few bit operations, rather than a binary search tree lookup. It also allows us to allocate the storage for all the Bin data structures in a contiguous array, rather than in many different cache lines. This reduces the number of cache lines that must be moved around between cores when multiple threads are doing allocations.

4.  Added fast path to GPUBFCAllocator::AllocateRaw that first tries to allocate memory without involving the retry_helper\_. If an initial attempt fails (returns nullptr), then we go through the retry_helper\_, but normally we can avoid several levels of procedure calls as well as the allocation/deallocation of a std::function with several arguments.

5.  Commented out most of the VLOG calls. These can be reenabled selectively when needed for debugging purposes by uncommenting and recompiling.

Added multi-threaded benchmark to test allocation under contention.

Speeds up ptb_word_lm on my desktop machine with a Titan X card from 8036 words per second to 8272 words per second (+2.9%).

```cpp
Run on (40 X 2801 MHz CPUs); 2016/02/16-15:12:49
CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                          Base (ns)  New (ns) Improvement
------------------------------------------------------------------
BM_Allocation                            347       184    +47.0%
BM_AllocationThreaded/1                  351       181    +48.4%
BM_AllocationThreaded/4                 2470      1975    +20.0%
BM_AllocationThreaded/16               11846      9507    +19.7%
BM_AllocationDelayed/1                   392       199    +49.2%
BM_AllocationDelayed/10                  285       169    +40.7%
BM_AllocationDelayed/100                 245       149    +39.2%
BM_AllocationDelayed/1000                238       151    +36.6%
```

Speed up Pathways throughput by ~20% via a set of miscellaneous changes.

- Unified a bunch of special fast descriptor parsing functions into a single ParsedDescriptor class and use this class in more places to avoid expensive full parse calls.

- Change several protocol buffer fields from string to bytes (avoids unnecessary utf-8 checks and associated error handling code).

- DescriptorProto.inlined_contents is now a string, not a Cord (it is expected to be used only for small-ish tensors). This necessitated the addition of a bunch of copying helpers in tensor_util.cc (need to now support both strings and Cords).

- Use flat_hash_map instead of std::unordered_map in a few places.

- Added MemoryManager::LookupMany for use by Stack op instead of calling Lookup per batch element. This change reduces setup overhead like locking.

- Removed some unnecessary string creation in TransferDispatchOp.

- Performance results for transferring a batch of 1000 1KB tensors from one component to another in the same process:

```cpp
Before: 227.01 steps/sec
After:  272.52 steps/sec (+20% throughput)
```

~15% XLA compiler performance improvement through a series of changes.

Some changes to speed up XLA compilation:

1.  In SortComputationsByContent, return false if a == b in comparison function, to avoid serializing and fingerprinting long computation strings.

2.  Turn CHECK into DCHECK to avoid touching an extra cache line in HloComputation::ComputeInstructionPostOrder

3.  Avoid making an expensive copy of the front instruction in CoreSequencer::IsVectorSyncHoldSatisfied().

4.  Rework 2-argument HloComputation::ToString and HloComputation::ToCord routines to do the bulk of the work in terms of appending to std::string, rather than appending to a Cord.

5.  Change PerformanceCounterSet::Increment to just do a single hash table lookup rather than two.

6.  Streamline Scoreboard::Update code

Overall speedup of 14% in XLA compilation time for one important model.

Speed up low level logging in Google Meet application code.

Speed up ScopedLogId, which is on the critical path for each packet.

- Removed the `LOG_EVERY_N(ERROR, ...)` messages that seemed to be there only to see if invariants were violated.
- Inlined the PushLogId and PopLogid() routines (since without the `LOG_EVERY_N_SECONDS(ERROR, ...)` statements, they are now small enough to inline.
- Switched to using a fixed array of size 4 and an 'int size' variable instead of an `InlinedVector<...>` for maintaining the thread local state. Since we never were growing beyond size 4 anyway, the InlinedVector's functionality was more general than needed.

```cpp
Base: Baseline plus the code in scoped_logid_test.cc to add the benchmark
New: This changelist

CPU: Intel Ivybridge with HyperThreading (20 cores) dL1:32KB dL2:256KB dL3:25MB
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_ScopedLogId/threads:1                               8           4    +52.6%
BM_ScopedLogId/threads:2                               8           4    +51.9%
BM_ScopedLogId/threads:4                               8           4    +52.9%
BM_ScopedLogId/threads:8                               8           4    +52.1%
BM_ScopedLogId/threads:16                             11           6    +44.0%
```

Reduce XLA compilation time by ~31% by improving Shape handling.

Several changes to improve XLA compiler performance:

1.  Improved performance of ShapeUtil::ForEachIndex... iteration in a few ways:

    - In ShapeUtil::ForEachState, save just pointers to the arrays represented by the spans, rather than the full span objects.

    - Pre-form a ShapeUtil::ForEachState::indexes_span pointing at the ShapeUtil::ForEachState::indexes vector, rather than constructing this span from the vector on every loop iteration.

    - Save a ShapeUtil::ForEachState::indexes_ptr pointer to the backing store of the ShapeUtil::ForEachState::indexes vector, allowing simple array operations in ShapeUtil::ForEachState::IncrementDim(), rather than more expensive vector::operator\[\] operations.

    - Save a ShapeUtil::ForEachState::minor_to_major array pointer initialized in the constructor by calling shape.layout().minor_to_major().data() rather than calling LayoutUtil::Minor(...) for each dimension for each iteration.

    - Inlined the ShapeUtil::ForEachState constructor and the ShapeUtil::ForEachState::IncrementDim() routines

2.  Improved the performance of ShapeUtil::ForEachIndex iteration for call sites that don't need the functionality of returning a Status in the passed in function. Did this by introducing ShapeUtil::ForEachIndexNoStatus variants, which accept a ForEachVisitorFunctionNoStatus (which returns a plain bool). This is faster than the ShapeUtil::ForEachIndex routines, which accept a ForEachVisitorFunction (which returns a `StatusOr<bool>`, which requires an expensive `StatusOr<bool>` destructor call per element that we iterate over).

    - Used this variant of ShapeUtil::ForEachIndexNoStatus in LiteralBase::Broadcast and GenerateReduceOutputElement.

3.  Improved performance of LiteralBase::Broadcast in several ways:

    - Introduced templated BroadcastHelper routine in literal.cc that is specialized for different primitive byte sizes (without this, primitive_size was a runtime variable and so the compiler couldn't do a very good job of optimizing the memcpy that occurred per element, and would invoke the general memcpy path that assumes the byte count is fairly large, even though in our case it is a tiny power of 2 (typically 1, 2, 4, or 8)).

    - Avoided all but one of ~(5 + num_dimensions + num_result_elements) virtual calls per Broadcast call by making a single call to 'shape()' at the beginning of the LiteralBase::Broadcast routine. The innocuous looking 'shape()' calls that were sprinkled throughout end up boiling down to "root_piece().subshape()", where subshape() is a virtual function.

    - In the BroadcastHelper routine, Special-cased the source dimensions being one and avoided a call to IndexUtil::MultiDimensionalIndexToLinearIndex for this case.

    - In BroadcastHelper, used a scratch_source_array pointer variable that points into the backing store of the scratch_source_index vector, and used that directly to avoid vector::operator\[\] operations inside the per-element code. Also pre-computed a scratch_source_span that points to the scratch_source_index vector outside the per-element loop in BroadcastHelper, to avoid constructing a span from the vector on each element.

    - Introduced new three-argument variant of IndexUtil::MultiDimensionalIndexToLinearIndex where the caller passes in the minor_to_major span associated with the shape argument. Used this in BroadcastHelper to compute this for the src and dst shapes once per Broadcast, rather than once per element copied.

4.  In ShardingPropagation::GetShardingFromUser, for the HloOpcode::kTuple case, only call user.sharding().GetSubSharding(...) if we have found the operand to be of interest. Avoiding calling it eagerly reduces CPU time in this routine for one lengthy compilation from 43.7s to 2.0s.

5.  Added benchmarks for ShapeUtil::ForEachIndex and Literal::Broadcast and for the new ShapeUtil::ForEachIndexNoStatus.

```cpp
Base is with the benchmark additions of
BM_ForEachIndex and BM_BroadcastVectorToMatrix (and BUILD file change to add
benchmark dependency), but no other changes.

New is this cl

Run on (72 X 1357.56 MHz CPU s) CPU Caches: L1 Data 32 KiB (x36)
L1 Instruction 32 KiB (x36) L2 Unified 1024 KiB (x36) L3 Unified 25344 KiB (x2)

Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_MakeShape                                       18.40       18.90     -2.7%
BM_MakeValidatedShape                              35.80       35.60     +0.6%
BM_ForEachIndex/0                                  57.80       55.80     +3.5%
BM_ForEachIndex/1                                  90.90       85.50     +5.9%
BM_ForEachIndex/2                               1973606     1642197     +16.8%
```

The newly added ForEachIndexNoStatus is considerably faster than the ForEachIndex variant (it only exists in this new cl, but the benchmark work that is done by BM_ForEachIndexNoStatus/NUM is comparable to the BM_ForEachIndex/NUM results above).

```cpp
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_ForEachIndexNoStatus/0                             0        46.90    ----
BM_ForEachIndexNoStatus/1                             0        65.60    ----
BM_ForEachIndexNoStatus/2                             0     1001277     ----
```

Broadcast performance improves by ~58%.

```cpp
Benchmark                                      Base (ns)    New (ns) Improvement
----------------------------------------------------------------------------
BM_BroadcastVectorToMatrix/16/16                   5556        2374     +57.3%
BM_BroadcastVectorToMatrix/16/1024               319510      131075     +59.0%
BM_BroadcastVectorToMatrix/1024/1024           20216949     8408188     +58.4%
```

Macro results from doing ahead-of-time compilation of a large language model (program does more than just the XLA compilation, but spends a bit less than half its time in XLA-related code):

Baseline program overall: 573 seconds With this cl program overall: 465 seconds (+19% improvement)

Time spent in compiling the two largest XLA programs in running this program:

Baseline: 141s + 143s = 284s With this CL: 99s + 95s = 194s (+31% improvement)

Reduce compilation time for large programs by ~22% in Plaque (a distributed execution framework).

Small tweaks to speed up compilation by ~22%.

1.  Speed up detection of whether or not two nodes share a common source. Previously, we would get the sources for each node in sorted order and then do a sorted intersection. We now place the sources for one node in a hash-table and then iterate over the other node's sources checking the hash-table.
2.  Reuse the same scratch hash-table in step 1.
3.  When generating compiled proto, keep a single btree keyed by `pair<package, opname>` instead of a btree of btrees.
4.  Store pointer to opdef in the preceding btree instead of copying the opdef into the btree.

Measurement of speed on large programs (~45K ops):

```cpp
name             old time/op  new time/op  delta
BM_CompileLarge   28.5s ± 2%   22.4s ± 2%  -21.61%  (p=0.008 n=5+5)
```

MapReduce improvements (~2X speedup for wordcount benchmark).

Mapreduce speedups:

1.  The combiner data structures for the SafeCombinerMapOutput class have been changed. Rather than using a `hash_multimap<SafeCombinerKey, StringPiece>`, which had a hash table entry for each unique key/value inserted in the table, we instead use a `hash_map<SafeCombinerKey, ValuePtr*>` (where ValuePtr is a linked list of values and repetition counts). This helps in three ways:

    - It significantly reduces memory usage, since we only use "sizeof(ValuePtr) + value_len" bytes for each value, rather than "sizeof(SafeCombinerKey) + sizeof(StringPiece) + value_len + new hash table entry overhead" for each value. This means that we flush the reducer buffer less often.

    - It's significantly faster, since we avoid extra hash table entries when we're inserting a new value for a key that already exists in the table (and instead we just hook the value into the linked list of values for that key).

    - Since we associate a repetition count with each value in the linked list, we can represent this sequence:

      ``` c++
      Output(key, "1");
      Output(key, "1");
      Output(key, "1");
      Output(key, "1");
      Output(key, "1");
      ```

    as a single entry in the linked list for "key" with a repetition count of 5. Internally we yield "1" five times to the user-level combining function. (A similar trick could be applied on the reduce side, perhaps).

2.  (Minor) Added a test for "nshards == 1" to the default MapReductionBase::KeyFingerprintSharding function that avoids fingerprinting the key entirely if we are just using 1 reduce shard (since we can just return 0 directly in that case without examining the key).

3.  Turned some VLOG(3) statements into DVLOG(3) in the code path that is called for each key/value added to the combiner.

Reduces time for one wordcount benchmark from 12.56s to 6.55s.

Rework the alarm handling code in the SelectServer to significantly improve its performance (adding+removing an alarm from 771 ns to 271 ns).

Reworked the alarm handling code in the SelectServer to significantly improve its performance.

Changes:

1.  Switched to using `AdjustablePriorityQueue<Alarm>` instead of a a `set<Alarm*>` for the `AlarmQueue`. This significantly speeds up alarm handling, reducing the time taken to add and remove an alarm from 771 nanoseconds to 281 nanoseconds. This change avoids an allocation/deallocation per alarm setup (for the red-black tree node in the STL set object), and also gives much better cache locality (since the AdjustablePriorityQueue is a heap implemented in a vector, rather than a red-black tree), there are fewer cache lines touched when manipulating the `AlarmQueue` on every trip through the selectserver loop.

2.  Converted AlarmList in Alarmer from a hash_map to a dense_hash_map to avoid another allocation/deallocation per alarm addition/deletion (this also improves cache locality when adding/removing alarms).

3.  Removed the `num_alarms_stat_` and `num_closures_stat_` MinuteTenMinuteHourStat objects, and the corresponding exported variables. Although monitoring these seems nice, in practice they add significant overhead to critical networking code. If I had left these variables in as Atomic32 variables instead of MinuteTenMinuteHourStat, they would have still increased the cost of adding and removing alarms from 281 nanoseconds to 340 nanoseconds.

Benchmark results

```cpp
Benchmark                      Time(ns)  CPU(ns) Iterations
-----------------------------------------------------------
BM_AddAlarm/1                       902      771     777777
```

With this change

```cpp
Benchmark                      Time(ns)  CPU(ns) Iterations
-----------------------------------------------------------
BM_AddAlarm/1                       324      281    2239999
```

3.3X performance in index serving speed!

We found a number of performance issues when planning a switch from on-disk to in-memory index serving in 2001. This change fixed many of these problems and took us from 150 to over 500 in-memory queries per second (for a 2 GB in-memory index on dual processor Pentium III machine).

- Lots of performance improvements to index block decoding speed (8.9 MB/s to 13.1 MB/s for a microbenchmark).
- We now checksum the block during decoding. This allows us to implement all of our getsymbol operations to be done without any bounds checking.
- We have grungy macros that hold the various fields of a BitDecoder in local variables over entire loops, and then store them back at the end of the loops.
- We use inline assembly to get at the 'bsf' instruction on Intel chips for getUnary (finds index of first 1 bit in a word)
- When decoding values into a vector, we resize the vector outside of the loop and just walk a pointer along the vector, rather than doing a bounds-checked access to store every value.
- During docid decoding, we keep the docids in local docid space, to avoid multiplying by num_shards\_. Only when we need the actual docid value do we multiply by num_shards\_ and add my_shard\_.
- The IndexBlockDecoder now exports an interface 'AdvanceToDocid' that returns the index of the first docid ≥ "d". This permits the scanning to be done in terms of local docids, rather than forcing the conversion of each local docid to a global docid when the client calls GetDocid(index) for every index in the block.
- Decoding of position data for documents is now done on demand, rather than being done eagerly for the entire block when the client asked for position data for any document within the block.
- If the index block being decoded ends within 4 bytes of a page boundary, we copy it to a local buffer. This allows us to always load our bit decoding buffer via a 4-byte load, without having to worry about seg faults if we run off the end of a mmapped page.
- We only initialize the first nterms\_ elements of various scoring data structures, rather than initializing all MAX_TERMS of them (in some cases, we were unnecessarily memsetting 20K to 100K of data per document scored).
- Avoid round_to_int and subsequent computation on intermediate scoring values when the value being computed is 0 (the subsequent computation was just writing '0' over the 0 that we had memset in these cases, and this was the most common case).
- Made a bounds check on scoring data structures into a debug-mode assertion.

## Further reading {#further-reading}

In no particular order, a list of performance related books and articles that the authors have found helpful:

- [Optimizing software in C++](https://www.agner.org/optimize/optimizing_cpp.pdf) by Agner Fog. Describes many useful low-level techniques for improving performance.
- [Understanding Software Dynamics](https://www.oreilly.com/library/view/understanding-software-dynamics/9780137589692/) by Richard L. Sites. Covers expert methods and advanced tools for diagnosing and fixing performance problems.
- [Performance tips of the week](https://abseil.io/fast/) - a collection of useful tips.
- [Performance Matters](https://travisdowns.github.io/) - a collection of articles about performance.
- [Daniel Lemire’s blog](https://lemire.me/blog/) - high performance implementations of interesting algorithms.
- [Building Software Systems at Google and Lessons Learned](https://www.youtube.com/watch?v=modXC5IWTJI) - a video that describes system performance issues encountered at Google over a decade.
- [Programming Pearls](https://books.google.com/books/about/Programming_Pearls.html?id=kse_7qbWbjsC) and [More Programming Pearls: Confessions of a Coder](https://books.google.com/books/about/More_Programming_Pearls.html?id=a2AZAQAAIAAJ) by Jon Bentley. Essays on starting with algorithms and ending up with simple and efficient implementations.
- [Hacker’s Delight](https://en.wikipedia.org/wiki/Hacker%27s_Delight) by Henry S. Warren. Bit-level and arithmetic algorithms for solving some common problems.
- [Computer Architecture: A Quantitative Approach](https://books.google.com/books/about/Computer_Architecture.html?id=cM8mDwAAQBAJ) by John L. Hennessy and David A. Patterson - Covers many aspects of computer architecture, including one that performance-minded software developers should be aware of like caches, branch predictors, TLBs, etc.
