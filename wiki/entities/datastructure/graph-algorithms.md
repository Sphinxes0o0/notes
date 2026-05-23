---
type: entity
tags: [algorithms, graph, data-structures]
created: 2026-05-23
sources: [pdf-algo-ds-books]
---

# Graph Algorithms

## Definition

Graph algorithms study the traversal and optimization of graph structures (vertices + edges). They are fundamental to network routing, social network analysis, constraint satisfaction, and many other domains.

## Key Concepts

### Graph Representations
- **Adjacency Matrix**: O(V²) space, O(1) edge lookup
- **Adjacency List**: O(V+E) space, O(deg(v)) edge lookup
- **Edge List**: Simple list of (u, v, w) tuples

### Core Algorithms

| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| DFS | O(V+E) | O(V) | Connectivity, cycle detection, topological sort |
| BFS | O(V+E) | O(V) | Shortest path (unweighted), bipartite check |
| Dijkstra | O((V+E)logV) | O(V) | Single-source shortest path (non-negative weights) |
| Bellman-Ford | O(VE) | O(V) | SSSP with negative weights |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs shortest path |
| Prim's MST | O((V+E)logV) | O(V) | Minimum spanning tree |
| Kruskal's MST | O(E log E) | O(V) | Minimum spanning tree (union-find) |
| Ford-Fulkerson | O(E·max_f) | O(V) | Maximum flow |

### Advanced Topics
- **Strongly Connected Components**: Tarjan's algorithm, Kosaraju's algorithm
- **Topological Ordering**: Kahn's algorithm (BFS-based)
- **Bipartite Matching**: Hungarian algorithm, Hopcroft-Karp
- **Network Flow**: Dinic's algorithm, Push-relabel
- **Planar Graphs**: Kuratowski's theorem, planar embedding

## Related Pages

- [[entities/datastructure/trees-and-graphs]] — Tree & graph data structures
- [[entities/datastructure/dynamic-programming]] — DP on graphs (shortest path)
- [[entities/datastructure/algorithm-complexity]] — Time/space complexity analysis
- [[datastructure-index]] — DSA module index

## Source Details

- [[sources/pdf-algo-ds-books]] — Algorithms in C, Part 5: Graph Algorithms (Sedgewick)
