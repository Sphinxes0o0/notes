---
type: entity
tags: [math, set-theory, algorithms, foundation]
created: 2026-05-23
sources: [pdf-algo-ds-books]
---

# Set Theory Basics

## Definition

Set theory is the mathematical foundation of computer science. Sets are unordered collections of distinct elements, and set operations underpin everything from relational databases to type theory.

## Key Concepts

### Basic Operations
- **Union** (A ∪ B): Elements in A or B
- **Intersection** (A ∩ B): Elements in both A and B
- **Difference** (A \ B): Elements in A but not B
- **Cartesian Product** (A × B): All ordered pairs (a, b)
- **Power Set** (P(A)): Set of all subsets of A

### Relations & Functions
- **Binary Relation**: Subset of A × B
- **Equivalence Relation**: Reflexive + symmetric + transitive → partitions
- **Partial Order**: Reflexive + antisymmetric + transitive
- **Function**: Relation where each input maps to exactly one output

### Cardinality
- **Finite Sets**: Countable by natural numbers
- **Countably Infinite**: ℵ₀ (natural numbers, integers, rationals)
- **Uncountably Infinite**: ℝ (real numbers), Cantor's diagonal argument

## Relevance to CS

| CS Domain | Set Theory Foundation |
|-----------|----------------------|
| Database Theory | Relational algebra (union, join, projection, selection) |
| Type Theory | Set as type, element as value |
| Algorithm Analysis | Combinatorics, counting arguments |
| Formal Languages | Alphabets as sets, strings as sequences |
| Automata Theory | States as sets, transitions as relations |

## Related Pages

- [[entities/datastructure/algorithm-complexity]] — Mathematical analysis of algorithms
- [[entities/datastructure/hash-table]] — Hash functions rely on set mapping properties
- [[datastructure-index]] — DSA module index

## Source Details

- [[sources/pdf-algo-ds-books]] — 基础集合论
