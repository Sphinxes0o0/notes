---
type: source
source-type: pdf
title: "Design Patterns in C++ (GoF 23 patterns with C++ implementation)"
author: "k_eckel (blog.mscenter.edu.cn)"
date: 2026-05-23
size: small
path: raw/PDFs/books/GoF+23种设计解析附C++实现.pdf
summary: "GoF 23种设计模式精解：创建型5种、结构型7种、行为型11种，每模式附带完整C++实现源码和解析"
---

# Design Patterns in C++ (GoF 23 patterns with C++ implementation)

## Core Content

A Chinese-language deep-dive into the 23 Gang of Four (GoF) design patterns, each with complete C++ implementation code and narrative explaining the rationale, structure, participants, and trade-offs.

### Creational Patterns (5)

**1. Factory (Simple Factory + Factory Method):**
- Simple Factory: centralized object creation with switch/if-else; violates OCP
- Factory Method: virtual constructor pattern, `Product* CreateProduct()` in Creator base class
- C++ implementation: abstract product interface, concrete product classes, factory subclasses

**2. Abstract Factory:**
- Families of related product objects; "factory of factories"
- Product hierarchy: AbstractProductA/AbstractProductB, ConcreteProductA1/ConcreteProductA2
- C++: abstract factory interface, concrete factories, product hierarchies

**3. Singleton:**
- Ensure one instance, global access point
- Lazy initialization vs eager initialization
- Thread-safe singleton: double-checked locking pattern, C++11 magic statics (Meyer's singleton)
- Multi-thread considerations: static local initialization is thread-safe in C++11

**4. Builder:**
- Separate construction from representation; same construction process yields different products
- Director + Builder interface + ConcreteBuilders
- C++: Director calls Builder steps, product assembled incrementally

**5. Prototype:**
- Clone/create objects via copying a prototype instance
- Deep copy vs shallow copy, virtual Clone() pattern
- C++: Cloneable base class with virtual Clone(), prototype registry

### Structural Patterns (7)

**6. Adapter (Wrapper):**
- Convert interface: class adapter (multiple inheritance) vs object adapter (composition)
- Target → Adapter → Adaptee

**7. Bridge (Handle/Body):**
- Decouple abstraction from implementation; compile-time vs run-time binding
- Abstraction + Implementor hierarchy

**8. Composite (Tree Structure):**
- Part-whole hierarchy: Leaf + Composite → Component
- Transparent vs safe composite design

**9. Decorator (Wrapper):**
- Add responsibilities dynamically; alternative to subclassing for extensibility
- Decorator maintains reference to Component, adds behavior before/after

**10. Facade:**
- Unified high-level interface to a subsystem; law of Demeter principle

**11. Flyweight:**
- Fine-grained shared objects for memory efficiency; intrinsic vs extrinsic state separation

**12. Proxy (Surrogate):**
- Control access: virtual proxy, remote proxy, protection proxy, smart reference
- C++: operator->() for smart pointers as proxy

### Behavioral Patterns (11)

**13. Template Method:**
- Skeleton algorithm in base class, defer steps to subclasses; Hollywood principle
- C++: non-virtual interface (NVI) idiom, template method pattern

**14. Strategy (Policy):**
- Encapsulate interchangeable algorithms; composition over inheritance
- C++: function pointers, functors, std::function, strategy as template parameter

**15. State:**
- Object behavior changes with internal state; state machine via state object hierarchy

**16. Observer (Dependents/Publish-Subscribe):**
- One-to-many dependency; subject notifies observers on state change
- C++: signal-slot (Boost.Signals, Qt), observer list, thread-safe notification

**17. Command (Action/Transaction):**
- Encapsulate request as object; undoable operations, macro commands
- C++: functor-based Command, Command queue for undo stack

**18. Chain of Responsibility:**
- Multiple handlers, each decides to handle or pass; event bubbling pattern

**19. Mediator:**
- Centralize complex communication; reduce coupling between colleagues

**20. Memento:**
- Capture & restore object state without breaking encapsulation; snapshot pattern

**21. Iterator:**
- Sequential access to aggregate elements; C++ STL iterators as canonical example
- C++: iterator_traits, input/output/forward/bidirectional/random-access categories

**22. Visitor:**
- New operations on object structure without modifying classes; double dispatch
- C++: accept(Visitor&), visit(ConcreteElement&), cyclic vs acyclic visitor

**23. Interpreter:**
- Grammar representation + interpreter for language sentences; AST pattern
- C++: abstract expression, terminal/non-terminal expressions, context

## Key Quotes

- "懂了设计模式，你就懂了面向对象分析和设计（OOA/D）的精要" (Understanding design patterns means grasping the essence of OOA/D) — k_eckel

## Related Pages

- [[design-patterns-index]] — Design patterns module index
- [[entities/design-patterns/solid-principles]] — SOLID principles
- [[entities/design-patterns/design-principles-advanced]] — Advanced design principles
- [[entities/design-patterns/creational-patterns]] — Creational patterns
- [[entities/design-patterns/structural-patterns]] — Structural patterns
- [[entities/design-patterns/behavioral-patterns]] — Behavioral patterns
- [[entities/cpp/raii]] — RAII idiom
- [[entities/cpp/smart-pointers]] — Smart pointers (proxy pattern example)
- [[entities/cpp/cpp-stl-iterators]] — STL iterators (iterator pattern)
- [[cpp-index]] — Modern C++
- [[sys-prog-index]] — System programming
