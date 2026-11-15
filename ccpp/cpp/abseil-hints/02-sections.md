---
title: "Algorithmic improvements"
description: "Algorithmic improvements：Algorithmic improvements、Better memory representation。"
---

# Algorithmic improvements {#chapter}

[返回总目录](../abseil-hints)

## Algorithmic improvements {#algorithmic-improvements}

The most critical opportunities for performance improvements come from algorithmic improvements, e.g., turning an O(N²) algorithm to O(N lg(N)) or O(N), avoiding potentially exponential behavior, etc. These opportunities are rare in stable code, but are worth paying attention to when writing new code. A few examples that show such improvements to pre-existing code:

Add nodes to cycle detection structure in reverse post-order.

We were previously adding graph nodes and edges one at a time to a cycle-detection data structure, which required expensive work per edge. We now add the entire graph in reverse post-order, which makes cycle-detection trivial.

graphcycles.h

<div class="old">

```cpp
class GraphCycles : public util_graph::Graph {
 public:
  GraphCycles();
  ~GraphCycles() override;

  using Node = util_graph::Node;
```

</div>

<div class="new">

```cpp
class GraphCycles : public util_graph::Graph {
 public:
  GraphCycles();
  ~GraphCycles() override;

  using Node = util_graph::Node;

  // InitFrom adds all the nodes and edges from src, returning true if
  // successful, false if a cycle is encountered.
  // REQUIRES: no nodes and edges have been added to GraphCycles yet.
  bool InitFrom(const util_graph::Graph& src);
```

</div>

graphcycles.cc

<div class="new">

```cpp
bool GraphCycles::InitFrom(const util_graph::Graph& src) {
  ...
  // Assign ranks in topological order so we don't need any reordering during
  // initialization. For an acyclic graph, DFS leaves nodes in reverse
  // topological order, so we assign decreasing ranks to nodes as we leave them.
  Rank last_rank = n;
  auto leave = [&](util_graph::Node node) {
    DCHECK(r->rank[node] == kMissingNodeRank);
    NodeInfo* nn = &r->nodes[node];
    nn->in = kNil;
    nn->out = kNil;
    r->rank[node] = --last_rank;
  };
  util_graph::DFSAll(src, std::nullopt, leave);

  // Add all the edges (detect cycles as we go).
  bool have_cycle = false;
  util_graph::PerEdge(src, [&](util_graph::Edge e) {
    DCHECK_NE(r->rank[e.src], kMissingNodeRank);
    DCHECK_NE(r->rank[e.dst], kMissingNodeRank);
    if (r->rank[e.src] >= r->rank[e.dst]) {
      have_cycle = true;
    } else if (!HasEdge(e.src, e.dst)) {
      EdgeListAddNode(r, &r->nodes[e.src].out, e.dst);
      EdgeListAddNode(r, &r->nodes[e.dst].in, e.src);
    }
  });
  if (have_cycle) {
    return false;
  } else {
    DCHECK(CheckInvariants());
    return true;
  }
}
```

</div>

graph_partitioner.cc

<div class="old">

```cpp
absl::Status MergeGraph::Init() {
  const Graph& graph = *compiler_->graph();
  clusters_.resize(graph.NodeLimit());
  graph.PerNode([&](Node node) {
    graph_->AddNode(node);
    NodeList* n = new NodeList;
    n->push_back(node);
    clusters_[node] = n;
  });
  absl::Status s;
  PerEdge(graph, [&](Edge e) {
    if (!s.ok()) return;
    if (graph_->HasEdge(e.src, e.dst)) return;  // already added
    if (!graph_->InsertEdge(e.src, e.dst)) {
      s = absl::InvalidArgumentError("cycle in the original graph");
    }
  });
  return s;
}
```

</div>

<div class="new">

```cpp
absl::Status MergeGraph::Init() {
  const Graph& graph = *compiler_->graph();
  if (!graph_->InitFrom(graph)) {
    return absl::InvalidArgumentError("cycle in the original graph");
  }
  clusters_.resize(graph.NodeLimit());
  graph.PerNode([&](Node node) {
    NodeList* n = new NodeList;
    n->push_back(node);
    clusters_[node] = n;
  });
  return absl::OkStatus();
}
```

</div>

Replace the deadlock detection system built into a mutex implementation with a better algorithm.

Replaced deadlock detection algorithm by one that is ~50x as fast and scales to millions of mutexes without problem (the old algorithm relied on a 2K limit to avoid a performance cliff). The new code is based on the following paper: A dynamic topological sort algorithm for directed acyclic graphs David J. Pearce, Paul H. J. Kelly Journal of Experimental Algorithmics (JEA) JEA Homepage archive Volume 11, 2006, Article No. 1.7

The new algorithm takes O(\|V\|+\|E\|) space (instead of the O(\|V\|^2) bits needed by the older algorithm). Lock-acquisition order graphs are very sparse, so this is much less space. The algorithm is also quite simple: the core of it is ~100 lines of C++. Since the code now scales to much larger number of Mutexes, we were able to relax an artificial 2K limit, which uncovered a number of latent deadlocks in real programs.

Benchmark results: these were run in DEBUG mode since deadlock detection is mainly enabled in debug mode. The benchmark argument (/2k etc.) is the number of tracked nodes. At the default 2k limit of the old algorithm, the new algorithm takes only 0.5 microseconds per InsertEdge compared to 22 microseconds for the old algorithm. The new algorithm also easily scales to much larger graphs without problems whereas the old algorithm keels over quickly.

```cpp
DEBUG: Benchmark            Time(ns)    CPU(ns) Iterations
----------------------------------------------------------
DEBUG: BM_StressTest/2k        23553      23566      29086
DEBUG: BM_StressTest/4k        45879      45909      15287
DEBUG: BM_StressTest/16k      776938     777472        817
```

```cpp
DEBUG: BM_StressTest/2k          392        393   10485760
DEBUG: BM_StressTest/4k          392        393   10485760
DEBUG: BM_StressTest/32k         407        407   10485760
DEBUG: BM_StressTest/256k        456        456   10485760
DEBUG: BM_StressTest/1M          534        534   10485760
```

Replace an IntervalMap (with O(lg N) lookups) with a hash table (O(1) lookups).

The initial code was using IntervalMap because it seemed like the right data structure to support coalescing of adjacent blocks, but a hash table suffices since the adjacent block can be found by a hash table lookup. This (plus other changes in the CL) improve the performance of tpu::BestFitAllocator by ~4X.

best_fit_allocator.h

<div class="old">

```cpp
using Block = gtl::IntervalMap<int64, BlockState>::Entry;
...
// Map of pairs (address range, BlockState) with one entry for each allocation
// covering the range [0, allocatable_range_end_).  Adjacent kFree and
// kReserved blocks are coalesced. Adjacent kAllocated blocks are not
// coalesced.
gtl::IntervalMap<int64, BlockState> block_list_;

// Set of all free blocks sorted according to the allocation policy. Adjacent
// free blocks are coalesced.
std::set<Block, BlockSelector> free_list_;
```

</div>

<div class="new">

```cpp
// A faster hash function for offsets in the BlockTable
struct OffsetHash {
  ABSL_ATTRIBUTE_ALWAYS_INLINE size_t operator()(int64 value) const {
    uint64 m = value;
    m *= uint64_t{0x9ddfea08eb382d69};
    return static_cast<uint64_t>(m ^ (m >> 32));
  }
};

// Hash table maps from block start address to block info.
// We include the length of the previous block in this info so we
// can find the preceding block to coalesce with.
struct HashTableEntry {
  BlockState state;
  int64 my_length;
  int64 prev_length;  // Zero if there is no previous block.
};
using BlockTable = absl::flat_hash_map<int64, HashTableEntry, OffsetHash>;
```

</div>

Replace sorted-list intersection (O(N log N)) with hash table lookups (O(N)).

Old code to detect whether or not two nodes share a common source would get the sources for each node in sorted order and then do a sorted intersection. The new code places the sources for one node in a hash-table and then iterates over the other node's sources checking the hash-table.

```cpp
name             old time/op  new time/op  delta
BM_CompileLarge   28.5s ± 2%   22.4s ± 2%  -21.61%  (p=0.008 n=5+5)
```

Implement good hash function so that things are O(1) instead of O(N).

location.h

<div class="old">

```cpp
// Hasher for Location objects.
struct LocationHash {
  size_t operator()(const Location* key) const {
    return key != nullptr ? util_hash::Hash(key->address()) : 0;
  }
};
```

</div>

<div class="new">

```cpp
size_t HashLocation(const Location& loc);
...
struct LocationHash {
  size_t operator()(const Location* key) const {
    return key != nullptr ? HashLocation(*key) : 0;
  }
};
```

</div>

location.cc

<div class="new">

```cpp
size_t HashLocation(const Location& loc) {
  util_hash::MurmurCat m;

  // Encode some simpler features into a single value.
  m.AppendAligned((loc.dynamic() ? 1 : 0)                    //
                  | (loc.append_shard_to_address() ? 2 : 0)  //
                  | (loc.is_any() ? 4 : 0)                   //
                  | (!loc.any_of().empty() ? 8 : 0)          //
                  | (loc.has_shardmap() ? 16 : 0)            //
                  | (loc.has_sharding() ? 32 : 0));

  if (loc.has_shardmap()) {
    m.AppendAligned(loc.shardmap().output() |
                    static_cast<uint64_t>(loc.shardmap().stmt()) << 20);
  }
  if (loc.has_sharding()) {
    uint64_t num = 0;
    switch (loc.sharding().type_case()) {
      case Sharding::kModShard:
        num = loc.sharding().mod_shard();
        break;
      case Sharding::kRangeSplit:
        num = loc.sharding().range_split();
        break;
      case Sharding::kNumShards:
        num = loc.sharding().num_shards();
        break;
      default:
        num = 0;
        break;
    }
    m.AppendAligned(static_cast<uint64_t>(loc.sharding().type_case()) |
                    (num << 3));
  }

  auto add_string = [&m](absl::string_view s) {
    if (!s.empty()) {
      m.Append(s.data(), s.size());
    }
  };

  add_string(loc.address());
  add_string(loc.lb_policy());

  // We do not include any_of since it is complicated to compute a hash
  // value that is not sensitive to order and duplication.
  return m.GetHash();
}
```

</div>

## Better memory representation {#better-memory-representation}

Careful consideration of memory footprint and cache footprint of important data structures can often yield big savings. The data structures below focus on supporting common operations by touching fewer cache lines. Care taken here can (a) avoid expensive cache misses (b) reduce memory bus traffic, which speeds up both the program in question and anything else running on the same machine. They rely on some common techniques you may find useful when designing your own data structures.

### Compact data structures {#compact-data-structures}

Use compact representations for data that will be accessed often or that comprises a large portion of the application’s memory usage. A compact representation can significantly reduce memory usage and improve performance by touching fewer cache lines and reducing memory bus bandwidth usage. However, watch out for [cache-line contention](/ccpp/cpp/abseil-hints/09-sections#reduce-false-sharing).

### Memory layout {#memory-layout}

Carefully consider the memory layout of types that have a large memory or cache footprint.

- Reorder fields to reduce padding between fields with different alignment requirements (see [class layout discussion](https://stackoverflow.com/questions/9989164/optimizing-memory-layout-of-class-instances-in-c)).
- Use smaller numeric types where the stored data will fit in the smaller type.
- Enum values sometimes take up a whole word unless you’re careful. Consider using a smaller representation (e.g., use `enum class OpType : uint8_t { ... }` instead of `enum class OpType { ... }`).
- Order fields so that fields that are frequently accessed together are closer to each other – this will reduce the number of cache lines touched on common operations.
- Place hot read-only fields away from hot mutable fields so that writes to the mutable fields do not cause the read-only fields to be evicted from nearby caches.
- Move cold data so it does not live next to hot data, either by placing the cold data at the end of the struct, or behind a level of indirection, or in a separate array.
- Consider packing things into fewer bytes by using bit and byte-level encoding. This can be complicated, so only do this when the data under question is encapsulated inside a well-tested module, and the overall reduction of memory usage is significant. Furthermore, watch out for side effects like under-alignment of frequently used data, or more expensive code for accessing packed representations. Validate such changes using benchmarks.

### Indices instead of pointers {#indices-instead-of-pointers}

On modern 64-bit machines, pointers take up 64 bits. If you have a pointer-rich data structure, you can easily chew up lots of memory with indirections of T\*. Instead, consider using integer indices into an array T\[\] or other data structure. Not only will the references be smaller (if the number of indices is small enough to fit in 32 or fewer bits), but the storage for all the T\[\] elements will be contiguous, often leading to better cache locality.

### Batched storage {#batched-storage}

Avoid data structures that allocate a separate object per stored element (e.g., `std::map`, `std::unordered_map` in C++). Instead, consider types that use chunked or flat representations to store multiple elements in close proximity in memory (e.g., `std::vector`, `absl::flat_hash_{map,set}` in C++). Such types tend to have much better cache behavior. Furthermore, they encounter less allocator overhead.

One useful technique is to partition elements into chunks where each chunk can hold a fixed number of elements. This technique can reduce the cache footprint of a data structure significantly while preserving good asymptotic behavior.

For some data structures, a single chunk suffices to hold all elements (e.g., strings and vectors). Other types (e.g., `absl::flat_hash_map`) also use this technique.

### Inlined storage {#inlined-storage}

Some container types are optimized for storing a small number of elements. These types provide space for a small number of elements at the top level and completely avoid allocations when the number of elements is small. This can be very helpful when instances of such types are constructed often (e.g., as stack variables in frequently executed code), or if many instances are live at the same time. If a container will typically contain a small number of elements consider using one of the inlined storage types, e.g., InlinedVector.

Caveat: if `sizeof(T)` is large, inlined storage containers may not be the best choice since the inlined backing store will be large.

### Unnecessarily nested maps {#unnecessarily-nested-maps}

Sometimes a nested map data structure can be replaced with a single-level map with a compound key. This can reduce the cost of lookups and insertions significantly.

Reduce allocations and improve cache footprint by converting btree\<a,btree\<b,c\>\> to btree\<pair\<a,b\>,c\>.

graph_splitter.cc

<div class="old">

```cpp
absl::btree_map<std::string, absl::btree_map<std::string, OpDef>> ops;
```

</div>

<div class="new">

```cpp
// The btree maps from {package_name, op_name} to its const Opdef*.
absl::btree_map<std::pair<absl::string_view, absl::string_view>,
                const OpDef*>
    ops;
```

</div>

Caveat: if the first map key is big, it might be better to stick with nested maps:

Switch to a nested map leads to 76% performance improvement in microbenchmark.

We previously had a single-level hash table where the key consisted of a (string) path and some other numeric sub-keys. Each path occurred in approximately 1000 keys on average. We split the hash table into two levels where the first level was keyed by the path and each second level hash table kept just the sub-key to data mapping for a particular path. This reduced the memory usage for storing paths by a factor of 1000, and also sped up accesses where many sub-keys for the same path were accessed together.

### Arenas {#arenas}

Arenas can help reduce memory allocation cost, but they also have the benefit of packing together independently allocated items next to each other, typically in fewer cache lines, and eliminating most destruction costs. They are likely most effective for complex data structures with many sub-objects. Consider providing an appropriate initial size for the arena since that can help reduce allocations.

Caveat: it is easy to misuse arenas by putting too many short-lived objects in a long-lived arena, which can unnecessarily bloat memory footprint.

### Arrays instead of maps {#arrays-instead-of-maps}

If the domain of a map can be represented by a small integer or is an enum, or if the map will have very few elements, the map can sometimes be replaced by an array or a vector of some form.

Use an array instead of flat_map.

rtp_controller.h

<div class="old">

```cpp
const gtl::flat_map<int, int> payload_type_to_clock_frequency_;
```

</div>

<div class="new">

```cpp
// A map (implemented as a simple array) indexed by payload_type to clock freq
// for that paylaod type (or 0)
struct PayloadTypeToClockRateMap {
  int map[128];
};
...
const PayloadTypeToClockRateMap payload_type_to_clock_frequency_;
```

</div>
