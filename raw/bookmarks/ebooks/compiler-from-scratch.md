# Build a Compiler from Scratch, Part 0: Introduction

**Author:** Geoffrey Copin (Sylver)
**Updated:** June 26, 2025
**Read time:** 3 min
**Series:** Build a Compiler from Scratch
**URL:** https://blog.sylver.dev/build-a-compiler-from-scratch-part-0-introduction

---

Compilers are frustrating.

Two decades ago, during a boring afternoon in my teenage room, I set out to discover how the software and games I spent so many hours with were made. I plunged into a Google Search rabbit hole that would yield a puzzling answer: to build a piece of software, you need... a piece of software. A compiler or an interpreter, to be precise.

It took me an embarrassingly long time to understand what seemed to me like a paradox. But the journey of understanding how high-level code is transformed into machine code and interacts with the OS was fascinating.

In this series, we'll go through this journey together, one tiny iteration at a time. We'll build a program to compile a minimalistic language inspired by Python into x86 assembly code. Along the way, we'll learn many things, including how to write a lexer, a parser, a type checker, a garbage collector, and of course we'll discover the basics of x86 assembly as we implement our code generator. We'll also cover more advanced topics, such as code optimization, intermediate representations, and rich error messages.

## The mile-high view

Before we dive into the implementation, let's take a moment to briefly discuss the high-level architecture of our compiler. In its simplest form, a compiler is a program that takes source code as an input, and translates it into another language, typically assembly code or bytecode for a virtual machine. In our case, the source language will be `Pylite`, a minimalistic language designed specifically for this series, and the target language will be assembly code for the x86 family of processors.

One might think that this translation process is done in a single pass, emitting assembly code as we read the input source code. And indeed, this is how many early compilers worked. However, modern compilers are often implemented as a pipeline of stages, with each stage taking the output of the previous stages as input to transform or enrich it in some way. Our compilation pipeline will be quite typical, consisting of the following stages:

```
     ┌────────┐     ┌──────────┐     ┌─────────────┐
     │ PARSER │────▶│ SEMANTIC │────▶│     IR      │
     └────────┘     │ ANALYZER │     │  GENERATOR  │
                    └──────────┘     └─────────────┘
                                              │
                                              ▼
                    ┌─────────────┐     ┌─────────┐
                    │    CODE     │◀────│OPTIMIZER│
                    │  GENERATOR  │     └─────────┘
                    └─────────────┘
```

The parser's input is the raw source code, and the code generator produces the final assembly code. Here is a quick breakdown of each stage:

- **parser**: this stage reads the source code and produces a parse tree, which is a structured in-memory representation of the source code.
- **semantic analyzer**: this stage extracts semantic information from the parse tree. It performs type checking and name resolution, which is the process of associating names with their matching declarations.
- **IR generator**: for reasons that we'll explore later in the series, the parse tree is not the ideal representation for low-level optimizations and code generation. For this reason, it is transformed (or "lowered") into an intermediate representation (IR) by the IR generator before the optimizer and code generator stages.
- **optimizer**: this stage performs various optimizations on the IR to improve the performance of the generated code.
- **code generator**: generates the final assembly code from the optimized IR

Most modern compilers use some variation of this pipeline, often with additional stages with their own intermediate representations. The first three stages, the parser, the semantic analyzer and the IR generator, are often referred to as the front-end of the compiler, while the later stages are called the backend. Generally speaking, the front-end is responsible for analyzing the source code and producing an intermediate representation, while the backend is responsible for IR optimization and code generation.

With this overview in mind, let's move on to the next part, where we'll build a complete compiler for a tiny subset of the `Pylite` language!

**Tags:** #rust #compiler #tutorial

---

## Series Contents

This is **Part 0 (Introduction)** of the "Build a Compiler from Scratch" blog series.

**Series Links:**
- Part 1.1: [Build a Compiler from Scratch, Part 1.1: A Hello World of sorts](https://blog.sylver.dev/build-a-compiler-from-scratch-part-11-a-hello-world-of-sorts)
- Part 1.2: [Build a Compiler from Scratch, Part 1.2: Intermediate Representation and Code Generation](https://blog.sylver.dev/build-a-compiler-from-scratch-part-12-intermediate-representation-and-code-generation)

**Note:** This series has additional parts beyond 1.2. Check the blog for the complete series.
