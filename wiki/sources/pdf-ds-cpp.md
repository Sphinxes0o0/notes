---
type: source
source-type: pdf
created: 2026-05-23
sources: [pdf-ds-cpp]
title: "Data Structures (C++ Language Edition, 3rd Ed)"
author: "Deng Junhui (邓俊辉, Tsinghua University)"
date: 2026-05-23
size: medium
path: raw/PDFs/books/数据结构C++.pdf
summary: "邓俊辉《数据结构（C++语言版）》第3版：清华985教材，从向量/列表到高级搜索树（Splay/Red-Black/B-Tree）、串匹配（KMP/BM/Karp-Rabin）、图论（DFS/BFS/最短路径/最小生成树）"
tags: [data-structures, cpp, books]
---

# Data Structures (C++ Language Edition, 3rd Ed)

## Core Content

A comprehensive data structures textbook from Tsinghua University (985 funded textbook), covering both classic and advanced data structures with C++ template implementations.

### Part I: Foundational Structures

**1. Introduction:**
- Computational complexity: O-notation, Ω, Θ
- Asymptotic analysis, recursion analysis
- Abstract data types, algorithm design methodology

**2. Vector (Dynamic Array):**
- Array-based vector: resizable array, amortized analysis of dynamic growth
- Insertion/deletion in O(n), random access O(1)
- Ordered vector: binary search, Fibonacci search, interpolation search

**3. List (Linked List):**
- Singly/doubly linked list, circular list
- Sentinel nodes (header/trailer) for simplified boundary handling
- Insertion/deletion O(1) given position, search O(n)

**4. Stack & Queue:**
- Stack: LIFO, array/list implementations, bracket matching, expression evaluation (infix→postfix→result)
- Queue: FIFO, circular queue, array/list implementations

### Part II: Trees & Priority Queues

**5. Binary Tree:**
- Binary tree traversal: pre-order, in-order, post-order, level-order
- Recursive and iterative implementations
- Threaded binary tree (Morris traversal)

**6. Binary Search Tree (BST):**
- BST property, search/insert/delete
- Three-node rotation, balanced BST motivation

**7. Balanced BSTs:**
- AVL tree: balance factor, LL/RR/LR/RL rotations, rebalancing
- Splay tree: self-adjusting, amortized O(log n), splaying operations (zig/zag)
- B-Tree: multi-way balanced tree, (2,4) trees (B+ tree in practice)

**8. Red-Black Tree:**
- 5 properties, insertion (3 cases), deletion (6 cases)
- Equivalence to (2,4) B-tree
- C++ STL set/map implementation based on RB-tree

**9. Priority Queue & Heap:**
- Binary heap: complete binary tree, percolate-up/percolate-down
- Heap sort: O(n log n), in-place, not stable
- Leftist heap and binomial heap for mergeable priority queues

### Part III: Advanced Topics

**10. Dictionary & Hash Table:**
- Hash functions: division, multiplication, mid-square, MAD (multiply-add-divide)
- Collision handling: separate chaining, open addressing (linear/quadratic probing, double hashing)
- Rehashing, perfect hashing, Cuckoo hashing
- Bloom filter: probabilistic data structure for set membership

**11. Sorting:**
- Bubble sort, selection sort, insertion sort: O(n²)
- Shell sort: gap sequence, O(n^1.5)
- Merge sort: divide-and-conquer, O(n log n), stable
- Quick sort: partition strategies (Lomuto/Hoare), random pivot, worst-case O(n²)
- Radix sort & bucket sort: linear time for integers
- Comparison-based sorting lower bound: Ω(n log n)

**12. String Matching:**
- Brute force: O(nm)
- KMP algorithm: prefix function, O(n+m)
- BM algorithm: bad character rule, good suffix rule
- Karp-Rabin: rolling hash (Rabin fingerprint), O(n+m) expected

### Part IV: Graphs

**13. Graph:**
- Graph representations: adjacency matrix, adjacency list, incidence matrix
- BFS (Breadth-First Search): SSSP on unweighted graphs
- DFS (Depth-First Search): edge classification (tree/back/forward/cross), topological sort, SCC (Kosaraju/Tarjan)
- Biconnected components, articulation points

**14. Graph Algorithms:**
- Minimum spanning tree: Prim's algorithm, Kruskal's algorithm (union-find)
- Shortest path: Dijkstra (O(E log V)), Bellman-Ford (negative edges), Floyd-Warshall (APSP)
- Maximum flow: Ford-Fulkerson, Edmonds-Karp, Dinic

### Part V: C++ Implementation Notes

- Extensive use of C++ templates for generic data structures
- RAII for resource management in container classes
- Iterator patterns for traversal abstraction
- Exception safety: basic/strong/no-throw guarantees

## Key Quotes

- "数据结构是计算机科学的核心课程，也是衡量程序员能力的重要标尺" (Data structures are the core of CS and an important measure of programmer ability) — Deng Junhui

## Related Pages

- [[datastructure-index]] — Data structures module index
- [[entities/datastructure/algorithm-complexity]] — Complexity analysis
- [[entities/datastructure/linear-data-structures]] — Linear structures
- [[entities/datastructure/sorting-algorithms]] — Sorting algorithms
- [[entities/datastructure/dynamic-programming]] — Dynamic programming
- [[entities/datastructure/recursion-and-divide-conquer]] — Recursion
- [[entities/datastructure/hash-table]] — Hash table
- [[entities/datastructure/trees-and-graphs]] — Trees and graphs
- [[entities/cpp/cpp-stl-containers]] — STL containers
- [[entities/cpp/cpp-stl-algorithms]] — STL algorithms
- [[entities/cpp/cpp-templates]] — C++ templates
- [[cpp-index]] — Modern C++
