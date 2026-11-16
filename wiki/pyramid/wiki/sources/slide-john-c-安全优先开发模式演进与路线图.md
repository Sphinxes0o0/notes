---
type: source
source-type: slide
title: "John_C++ “安全优先”开发模式演进与路线图"
path: slides/John_C++ “安全优先”开发模式演进与路线图.pdf
source-md5: a0ef16b62f0aa5b288ca642cdcbd1aee
size: 5699 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# John_C++ “安全优先”开发模式演进与路线图

> Ingested from `slides/John_C++ “安全优先”开发模式演进与路线图.pdf` via `lit parse` on 2026-06-04.
> Source file: 5.57 MB.

## Page 1

_(no text content on this page)_

## Page 2

_(no text content on this page)_

## Page 3

_(no text content on this page)_

## Page 4

_(no text content on this page)_

## Page 5

_(no text content on this page)_

## Page 6

What C++ Needs to be Safe?
C++需要些什么才能安全？
C++     Summit’25
December 12-13, 2025
Modified Monday, Dec 1st, 2025
John Lakos
Senior Architect, Office of the CTO
首席技术官办公室高级架构师
 © 2025 Bloomberg Finance L.P. All rights reserved.

## Page 7

What C++ Needs to be Safe?
John Lakos
Bloomberg, CTO
Revised December 1, 2025

    7

## Page 8

        Abstract
        摘要
The world runs on C++. For more than two decades, C++ has served as the workhorse of high-performance, low-power, and low-latency software across
industries. Its raw speed and unconstrained flexibility have made C++ the go-to language for and backbone of large-scale software development.
C++ 是驱动世界运转的核心语言。二十多年来，它始终是各行业高性能、低功耗、低延迟软件的主力担当。凭借其极致速度与无拘无束的灵
活性，C++ 已成为大规模软件开发的首选语言和核心支柱。
Recently, however, software engineering priorities have shifted significantly toward safety. While C++ enables the creation of secure and correct
programs, its traditional focus has favored performance over safety guarantees. As the software landscape evolves, C++ faces a crucial inflection point. To
maintain its unparalleled stature, C++ must embrace various safety mechanisms along with safety-by-default principles to support a broader developer
ecosystem while preserving the performance capabilities that experts will continue to demand.
然而近年来，软件工程的重心已显著向安全性倾斜。尽管 C++ 语言能够开发出安全可靠的程序，但其传统定位始终更侧重性能而非安全保障。
随着软件生态的持续演进，C++ 正面临关键转折点。为保持其无可替代的地位，C++ 必须拥抱多种安全机制与默认安全原则，既要维护开发
者生态系统的广泛性，又要确保满足技术专家持续追求的性能表现。
This talk will examine C++'s evolution toward safety-first development, analyzing functional, language, memory, lifetime, and data-race safety
considerations. We survey existing safety techniques, identify current limitations, and explore potential solutions for remaining security challenges.
Finally, we present a comprehensive roadmap for achieving robust safety guarantees in C++26 and beyond, while continuing to enable all the language’s
performance advantages.
本次演讲将深入探讨 C++ 向安全优先开发模式的演进历程，系统解析函数式、语言、内存、生存期及数据竞争安全等核心议题。我们将全面
梳理现有安全技术，识别现存局限，并探索应对遗留安全挑战的创新方案。最终，我们将提出一套完整的路线图，旨在确保 C++26 及后续版
本实现可靠的安全保障，同时持续释放该语言的性能优势。

        8

## Page 9

Introduction and Motivation
引言与动机
Introduction
and
Motivation      9

## Page 10

        Motivation
        动机
C++ has come under sharp criticism.
C++已经受到了尖锐的批评。
§ Proponents of potential successor languages: Rust 潜在的继任语言支持者：Rust
§ Regulatory agencies: European Union 监管机构：欧盟
§ Governments & Cybersecurity Organizations 政府与网络安全组织
Major companies are backing away from C++. 多家大型企业正逐步退出
C++。
§ Google: Leaving C++, openly moving to Rust 谷歌：正离开 C++，公开迈向 Rust
§ Microsoft: No longer uniformly supports WG21/C++ 微软不再统一支持 WG21/C++
§ Adobe: Quietly moving new development over to Rust Adobe 悄然将新开发项目迁移
  至 Rust 10

## Page 11

    Our Top-Level Strategy
    顶层战略

by making it more 是通过让它更加
 Safe, Healthy, and Efficient
   安全、健康、且高效 11

## Page 12

       Our Top-Level     Strategy
三个首要聚焦区域
Three Primary Areas of Focus
1. Safety 安全
§  Correctness — Easy to get programs right
正确性——易于使程序正确
§  Security — Hard to create security vulnerabilities
保险——难以制造安全漏洞
2. Health 健康
§ Ecosystem — Support for Clang, GCC, MSVC, etc.
  生态——支持 Clang、GCC、 MSVC 等
3. Efficiency 高效
§  Machine — Run Time, Compile Time, Link Time
   机——运行时、编译时、链接时
§  Human — Development Time, Maintenance Time
   人——开发时间、维护时间        12

## Page 13

Making C++ Safer
更安全
Correct 正确
Ø The essential behavior is as intended.
基本行为符合预期。
— Support for detecting/preventing defects
缺陷检测/预防

Secure 保险
Ø Defects cannot be easily exploited.
缺陷不易被利用。
— Inherently resistant to malicious attacks
本有的抗恶意攻击能力        13

## Page 14

     Making C++ Healthier
     更健康
Ecosystem 生态
 Ø Compilers, Libraries, and Supporting Tools 编译器、库以
 及支持工具
 GCC, Clang, MSVC, EDG, …
 — Standard-Library Implementations 标准库实现
 — Sanitizers, Static Analyzers, Debuggers 净化器、静态分析、
 调试器
 — Testing Frameworks, Fuzzers, Documenters 测试框架、模糊
 器、文档

     14

## Page 15

 Making C++ more Efficient
 更高效
Machine 机
 Ø Programs and supporting tools run quickly.
 程序和支持工具运行快
 — Executables, Compilers, Linkers, Static Analyzers
 可执行文件、编译器、链接器、静态分析器

Human 人
 Ø Developer efficiency is maximized. 开发者效率最大化
 — Design, Develop, Document, Test, Maintain
 设计、开发、记录、测试、维护        15

## Page 16

     Safe, Healthy, and Efficient
     安全、健康、且高效
What we aim to achieve:
中长期目标
q Make C++ easier to use securely and correctly. 使 C++ 更易于安全、正确地使用
q Close the gap with other “Safe” languages.    缩小与其他“安全”语言的差距。
q Blunt any desire to migrate away from C++.   打消任何想离开C++的念头。
q Improve the typical C++ user’s experience.   改善典型C++用户的使用体验。
q Set an example for other C++ organizations.   为其他C++组织树立榜样。



                                                16

## Page 17

From WG21 Proposal To Production
    从WG21提案到生产
 From WG21
ToProposal
   Production 17

## Page 18

        History of Contracts Proposals for C++
        C++契约提案的历史
        第三次提案（“合并提案”，
        “类属性”，“C++2a 契约）

        标准化C++契约的20年                          提案投票进入 C++20 工作草案    2025
        替换提案开发中                                                     You
                                                                    are
Herb Sutter gave                          自 C++20 工作草案移除           here
an excellent talk                                                  2025你
 on Contracts at              SG21 诞生     第四次提案（”契约MVP")            在这
    CppCon’25        探索性论文
  Herb Sutter在       提案放弃    提案在 WG21 全会失败
  CppCon'25上关于
     契约的精彩演讲      第一次提案，类D                      提案转交 EWG/LEWG  提案投票进入 C++20 工作草案
                              第二次提案（“BDE 契约”，   设计评审
                              “基于宏”）


                                                18
    Slide courtesy of Timur Doumler (ACCU 2025: Tuesday, 2-APR-25, 14:00 BST): “Contracts for C++”

## Page 19

                                                                                                                   2022 彭博赞助 Clang 中的 C++202x 功能 Jabot
                                                                                                                   2023 彭博赞助 契约 MVP 的倡导 Doumler
                                                                                                                   2024 彭博赞助 Clang 和 GCC 中的 MVP Fiselier, Ranns, Sandoe
                           History of Contracts                                                                    2025 彭博安排了有录制的安全小组会议，由 Phil Nash 组织：Azman,
                                                                                           Proposals
                                                                                                                   Berne, Doumler, Gill, Lakos, Lippincott, Wong
                                                    2009                    C++ 契约提案的历史                            2025 “彭博社持续支持在 Clang 和 GCC 中对 C++26 契约 MVP 及后续
                                                    BDE 契约产品化                                  2017                版本进行原型开发与产品化。”Edwards (彭博首席技术官）
                                                    Lakos                   2015               BDE 契约支持评审                   2022
                                                            2009            “Uniform”          Berne                        Bloomberg sponsors
                                                            BDE                                                             C++202X featuresin Clang
                                                            Contracts       contracts                                       Jabot
                                                            productized     problematic                                     2023
                        2004       2004                     Lakos                          2017                             Bloomberg sponsors
                        BDE 契约     BDE Contracts                                           BDE                              Contracts MVP advocate
                        在彭博广       in wide use                                             Contracts                        Doumler
                        泛使用        throughout                                              Support                          2024
                                   Bloomberg                                               Berne                            Bloomberg sponsors
                                                                                                                            MVP in Clang and GCC
                                                                           2017 --         2017 –        2020 –             Fiselier, Ranns, Sandoe
    2003                                                                   许多论文            Many papers   Much Reflector     2025
    Bloomberg’s BDE                                                        Berne, Lakos                  Lakos, Berne       Bloomberg arranges for
                                                    2012                                                                    recorded safety panel
    team invents what                                                                                                       Organized by Phil Nash:
    (a subset of which)                             BDE open-sourced                                                        Azman,Berne,Doumler,Gill,
    will evolve into                                                                                                        Lakos, Lippincott, Wong
    today’s C++26 MVP                               2012                                       2020                         2025
    Lakos                                           BDE 开源                                     许多反思                         “Bloomberg continuesto
    2003                                                                                       Lakos，Berne                  support prototyping and
    彭博BDE团队发明了什么                                                                                                            productizing the C++26
                                                                                                                            beyondinClangandGCC.”
    （其中一部分）将演变为                                                                                                             Contracts MVP and
    现今的 C++26 MVP                                                                                                           Edwards(Bloomberg’sCTO)

Slide courtesy of Timur Doumler (ACCU 2025: Tuesday, 2-APR-25, 14:00 BST): “Contracts for C++”                                  19
                                      幻灯片由Timur Doumler提供

## Page 20

 Creative Thinking        从 WG21 提案到生产        实际
 创造性思维     From WG21 Proposal To Production
 ISO C++ Proposals     X     X
 ISO C++ 提案
 Compiler Prototypes        5 years
编译器原型
        C++11 C++14 C++17 C++20 C++23 C++26 C++29 C++32
 ISO C++ Standards        X
 ISO C++ 标准                               1 yr
   2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032
 Annual Compiler Versions                     4 years
 年度编译器版本
   2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032
 Production Compiler Use        10 years        20
 编译器投入生产使用

## Page 21

Creative Thinking        从WG21提案到生产        规范的
创造性思维     From WG21 Proposal To Production
ISO C++ Proposals
ISO C++ 提案
Compiler Prototypes
编译器原型        2 years
       C++11 C++14 C++17 C++20 C++23 C++26 C++29 C++32
ISO C++ Standards                      1 yr
ISO C++ 标准
  2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032
Annual Compiler Versions                   1 yr
年度编译器版本
  2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032
Production Compiler Use        4 years        21
编译器投入生产使用

## Page 22

Creative Thinking        理想的
创造性思维     From WG21 Proposal To Production
ISO C++ Proposals
ISO C++ 提案
Compiler Prototypes
编译器原型        2 years
       C++11 C++14 C++17 C++20 C++23 C++26 C++29 C++32
ISO C++ Standards        1 yr
ISO C++ 标准
  2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032
Annual Compiler Versions
年度编译器版本
  2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032
Production Compiler Use    3 years        22
编译器投入生产使用

## Page 23

What does it mean to be “Safe”?
     “安全”意味着什么？
 What does
  it mean to
 be “Safe”? 23

## Page 24

What does it mean to be “Safe”?
    “安全”意味着什么？
Safety means different things to different people:
安全对不同的人意味着不同的东西
q Secure 保险
— Doesn’t admit security vulnerabilities. 不允许安全漏洞
q Well-defined 定义清楚
— Doesn’t admit undefined behavior. 不允许未定义行为
q Correct Behavior 正确的行为
— Does what it is intended to do. 按意图行动
— Surprisingly, correctnessisn’t typically considered part ofsafety. 令人意外的是，
正确性通常不被视为安全的一部分。
    24

## Page 25

 Any access
must be type What does it     mean to     be “Safe”?
 safe. 任何访问
  务必类型安全     “安全”意味着什么？ A language could, of course, allow write-only
                        access to uninitialized allocated memory and
                                        still be M.S.
        Memory Safety 内存安全         当然，语言可以允许对未初始化的已分配内存进行
                                       只写访问，同时仍能保持内存安全
    A language is memory safe if it does NOT permit access to unallocated or uninitialized
    memory.
    如果某种语言不允许访问未分配或未初始化的内存 ，则该语言是内存安全的

    q Garbage Collected Language: 垃圾收集语言        “one or more readers
    — Java, Python, JavaScript, Go              or just one writer”                   “一个
    q Functional Languages: 函数式语言               或多个读者，或者只有一个写
    — Scala, OCaml, Haskell, PHP    者”
    q Languages that Enforce the Law of Exclusivity (LoE): 实施独占性原则的语言
    — Rust (lifetime via Borrow Checking), Swift 6.0 (lifetime via Reference Counting)
        Rust(以借用检查实现的生存期），Swift 6.0(以引用计数实现的生存期）

                                                                                          25

## Page 26

        What does it mean to be “Safe”?
        “安全”意味着什么？
What Memory Safety Isn’t:
内存安全不是什么？
  Memory safety does not necessarily imply an absence of all
  undefined behavior: 内存安全并不意味着不存在任何的未定义行为 Guaranteed UB!
      twice(int x) { return x + x; } 保证是未定义行为！
  int main() { return twice (1’500’000’000); }
Signed integer overflow is UB, but it’s NOT a violation of
memory safety, per se. 有符号整数溢出是UB，但严格来说它并不违反
内存安全性。 26

## Page 27

 What does it mean to be “Safe”?
“安全”意味着什么？                     Plain-language
                                contracts are
What we’re trying to achieve:    for humans!
                                   自然语言契约
我们试图实现什么？                          是给人看的！
q Security: Every C++ program can be built such that no (core-language)
UB is ever executed. 安全性：每个 C++ 程序均可构建为确保（核心语言）
UB 永不被执行。
q Correctness: User-defined functions can be written such that their
plain-language contracts — preconditions and postconditions — are
optionally checked (redundantly), typically at runtime. 正确性：         用户定义
函数的契约（前置条件与后置条件）用日常语言写出，并且一般在运行时被可
选（冗余）地检查。                                                            Caller holds a *
*Notallplain-languagepreconditions canbecheckedatruntime: ???????    valid license.
并非所有日常语言的前置条件都能在运行时检查：？？？？                                                调用者持有      27
                                                                          有效许可

## Page 28

What does it mean to be “Safe”?
“安全”意味着什么？
What we’re trying to achieve:
我们试图实现什么？
q Security: Every C++ program can be built such that no (core-
language) UB is ever executed.安全性：每个 C++ 程序均可构建为确保（核心语
言）UB 永不被执行。
without changing any source code,
relink our code using an ISO-C++-compliant compiler, we can be sure
no core-language UB will ever be executed!
即，无需修改任何源代码，只是简单用符合 ISO-C++ 标准的编译器重新编译
链接，就能确保核心语言中的未定义行为永不被执行

    28

## Page 29

      What does it mean to be “Safe”?
        “安全”意味着什么？
What we’re trying to achieve:
我们试图实现什么？
That is, those who choose to check the contracts of their own (user-
defined) functions have the tools to do so.即，选择自行检查（用户定
义）函数契约的人员具备相应的工具。
q Correctness: User-defined functions can be written such that their plain-
 language contracts — preconditions and postconditions — are optionally
 checked (redundantly), typically at runtime.正确性：用户定义函数的契约（前
 置条件与后置条件）用自然语言写出，并且一般在运行时被可选（冗余）地
 检查。 29

## Page 30

                                    3rd-party
   What does it mean to be “Safe”?  libraries
                                      too!
   “安全”意味着什么？                       第三方库也一样！
What we’re trying to     achieve:
“安全”意味着什么？
(Conforming) Standard Library implementations can detect,report, and/or avoidUB
withnochange toclient code.
（符合的）标准库实现可在不修改客户端代码的情况下检测、报告和/或避免未声明，且无需修改客
Security: Every C++ program can be built such hat
户代码
q Correctness: User-defined functions can be written such that their plain-
language contracts — preconditions and postconditions — are optionally
checked (redundantly), typically at runtime.正确性：用户定义函数的日常语言契约
（前置条件与后置条件）一般在运行时被可选（冗余）地检查。
                                                                           30

## Page 31

Tools That Address UB In C++
  C++ 中解决 UB 的工具
 Tools That
Address UB
    In C++  31

## Page 32

        Tools That Address UB In C++
        C++ 中解决 UB 的工具
There is no one tool that addresses all of C++’s UB:
目前尚无单一工具能全面解决C++的未定义行为问题。
1. Runtime Contract Checking 运行期契约检查
2. Erroneous Behavior (EB) 错误行为
3. Symbolic Contract Assertions 符号契约断言
4. Source-Code Subsetting (part of “Profiles”) 源代码子集（“规格
    配置”的一部分）
5. Compile-Time-Enforced Exclusivity 编译期实施的独占性
6. Runtime-Enforced Reference Counting 运行期实施的引用计数
        32

## Page 33

1. Runtime Contract Checking
运行期契约检查
Runtime
Contract
Checking      33

## Page 34

Safe — Contracts
安全—契约
What is a contract? 什么是契约？
ØPlain-language contract: 日常语言契约
— A natural-language description of the agreement
between client and library 客户和库的协议的自然语言描述
ØContract assertion: 契约断言
— A C++ code construct that identifies something that
must be true in a correct program 标记正确的程序中必然
为真的东西的一种 C++ 代码构造
    34

## Page 35

   Safe — Contracts
   安全—契约
C++26 Contracts MVP Features: C++26 契约 MVP 特性
§  Preconditions and postconditions directly on
   declaration 直接声明前置和后置条件
§ Standard way to set contract-violation handler 设置契约违反处理程序的标准方式
§  Four standard semantics for contract violations: 处理契约违反的四种标准语义
   , enforce, observe, quick
       _enforce     _enforce
§ A fifth semantic is anticipated: 预计还有第五种
   •assume    Status quo for both the core-language
                 and standard-library functions.
                         核心语言和标准库函数的现状.
       35

## Page 36

Function Declaration
Safe — Contracts
安全—契约 函数声明
A Simple Use Case: 简单用例
double sqrt(double x);
       Return a value whose representation is
       as close as possible to the positive
       square root of the specified `x` value.
    // 返回一个值，它的表示要离指定的 `x ` 值的平方根尽可能接近
        Essential Behavior
        基本行为
        36

## Page 37

        Safe — Contracts
        安全—契约
A Simple Use Case: 简单用例
double sqrt(double x);
       Return a value whose representation is
       as close as possible to the positive
       square root of the specified `x` value.
       The behavior is undefined unless `x >= 0`.
    // 除非 `x >= 0`，否则行为未定义 Undefined Behavior
        未定义行为
        37

## Page 38

Safe — Contracts
安全—契约
    A Simple Use Case: Plain-Language Contract
        日常语言契约
double sqrt(double x);
       Return a value whose representation is
       as close as possible to the positive
       square root of the specified `x` value.
    // The behavior is undefined unless `x >= 0`.

38

## Page 39

    Safe — Contracts
    安全—契约
A Simple Use Case 简单用例
double sqrt(double x)
pre( x >= 0 );



39

## Page 40

        Safe — Contracts
        安全—契约
    A Simple   Use Case 简单用例
    double sqrt(double x)
    pre(     x >= 0 )     Recall: 回想
    post(r : r >= 0);     double std::nextafter(double value,
                          // Return the next  double northStar);
                          // specified     `double` after the
                                     `value` in the direction of
Might we do               // the specified `NorthStar`. …  ?
  better?                 // 返回指定”value”在指定“方向”上的下一个
   也许我们能                  //“double”
   做得更好？
                              40

## Page 41

        Safe     — Contracts
              Implies Implementation must not modify
                      this parameter’s value
    A Simple Use Case    意味着实施方不得修改该参数的数值
    double (const     double x)
    pre( x >= 0 ) Is this post condition good enough?!    Parameter used
                                                         in postcondition
                                                              后置条件中用
    post(r : r >= 0)           这种后置条件够好了吗？                      的参数
post( r : (x == 0 r == 0) What exactly are we missing?!
    || (r * r <= x &&        漏掉了什么？                        *
    || (r * r >= x &&    std::nextafter(r,INFINITY) >= x)
        std::nextafter(r,0)                               *
                                                          <= x) ); 41

## Page 42

                 Safe                                              FYI:
        — Contracts Comparing squared results (previous approach)
        fails miserably for most subnormal
        values. 供您参考：对于大多数次正规值，比较平
        方结果（先前方法）是惨遭失败

double sqr(const double x) { return x * x; } // helper function 辅助函数
    double sqrt(const double x)        Realize that, if — in either case below — the assumption isn’t true, the nexttoward
         pre( x >= 0 )                 difference will be negative, the inequality will not hold, and the overall assertion will be
         post( r : r >= 0 )            false, as is appropriate. 需明确，若以下任一情形中假设不成立，则差值将为负值，不等式
    {                                  将不成立，整体结论亦将不成立，此为合理处理方式
         double output = std::sqrt(x); // `sqrt` demonstrates runtime testing of `std::sqrt`.
         contract_assert(        // `sqrt` 用于展示 `std::sqrt` 的运行期测试
             ( sqr(output) == x )      Assume (for now) the next double above `output` squared is above `x`.
                                           假设（暂且）高于 output 的平方的下一个 double 高于 x。
         ||  ( sqr(output) < x &&
             x - sqr(output) <= sqr(std::nexttoward(output,INFINITY)) – x )
         ||  (sqr(output)    > x &&
         );  x - sqr(std::nexttoward(output,0)) >= sqr(output) – x )
         return output;        Assume (for now) the next double below `output` squared is below `x`.
    }                                      假设（暂且）低于 output 平方的下一个 double 小于 x。
             https://godbolt.org/z/31vn4xend                       42

## Page 43

        Safe     — Contracts
Most Important Usage 最重要的用途
namespace std {
template <class T, class Allocator = allocator<T>>
class vector {
    // ...
    constexpr     T& operator[](size_type n);
    constexpr const T& operator[](size_type n) const;
};  // ...

        43

## Page 44

        Safe     — Contracts                          Would
                               catch >65%
                            of STL’s security
Most Important     Usage    vulnerabilities!
                                HELLO!!!
                             可抓住 >65 % 的 STL
namespace std {                   安全漏洞
template <class T, class Allocator = allocator<T>>
class vector {
    // ...
    constexpr     T& operator[](size                 pre(n < size());
    constexpr const T& operator[](size_type n) const pre(n < size());
};  // ...
    We sometimes call contract assertions “Ghost Code” — why?
        我们有时将契约断言称为“幽灵代码”——为什么？                       44

## Page 45

     Safe —     Contracts
Teaching safe contract-assertion predicates:
契约断言谓词的教学
Basic: A contract-assertion predicate should have no side effects.
基础：契约断言谓词不应该有副作用
Advanced: A contract-assertion predicate MUST have NO destructive side
effects.
高级：契约断言谓词必须没有破坏性副作用
Ø A destructive side effect alters essential behavior.
 破坏性副作用改变本质行为
Ø Behavioris essential ifit’simplied by the plain-language contract.
 日常语言契约所隐含的是本质行为
     45

## Page 46

        Safe    —     Contracts
Coming in C++29 — the ability to…
C++29 带来的新能力…
1.  require that a contract assertion always be enforced
    要求契约断言总能施行
2.  mark a contract assertion as “expensive” (audit)
    标记某契约断言为“昂贵”（audit）
3.  capture input values and use them in postconditions
    捕获输入值并用于后置条件
4.  employ requires clauses on contract assertions to ease use with templates
    在契约断言中使用 requires 子句，方便同模板配合

        46

## Page 47

    Safe     — Contracts
Future Example
未来的例子                     1. Ability to require a
                          contract assertion always
template <typename T>     be enforced
T sqrt(T x)               要求契约断言总被执行
pre<enforced>  ( x >= 0 )

                              47

## Page 48

        Safe     — Contracts
    Future Example                2. Ability to mark a
    template <typename T>         contract assertion
                                  将契约断言标记为昂贵
    T sqrt(T x)                   as expensive (audit)
    pre<enforced>  ( x >= 0 )     （audit）
post<audit> // expensive assertion 昂贵的断言

  (r : abs(arg - r * r) < sqrt_accuracy(arg) ); 48

## Page 49

      Safe     — Contracts
  Future Example                3. Ability to capture
  template <typename T>         input values and use
  T sqrt(T x)                   them in postconditions
                                捕获输入值并用于后置条
  pre<enforced>  ( x >= 0 )     件
  post<audit>    expensive     assertion 昂贵的断言
[arg=x] // capture value of x 捕捉 x 值
(r : abs(arg - r * r) < sqrt_accuracy(arg) ); 49

## Page 50

      Safe — Contracts 4. Ability to employ
  Future Example                          requires clauses on
                                          contract assertions
  template <typename T>                   to ease use with
  T sqrt(T x)                             templates
  pre<enforced>  ( x >= 0 )               在契约断言中使用
  post<audit>    expensive     assertion  requires 子句，方
[arg=x] // capture value of x 便同模板配合
requires has_sqrt_accuracy<T> // concept 概念
(r : abs(arg - r * r) < sqrt_accuracy(arg) ); 50

## Page 51

        Safe                            —     Contracts
    Coming soon—Assertionsin the core language!    Core-language assertions could be
                                                   available much sooner than C++29!
    即将来临--核心语言中的断言！                                        核心语言中的断言可能比 C++29
                                                                 还要早实现
    Ø Implicit precondition checks                 The C++ Standard doesn’t need to
隐式前置条件检查                                          change because implicit assertions
    — C-style array-bounds checks                             replace UB.
    C风格的数组边界检查                                             C++ 标准无需改变因为隐式断言
    e.g., int a[32];     a[32]          = 5;                    会替代 UB
    — Signed integer-overflow checks                          Today we could manually
    有符号整数溢出检查                                                 check for overflow and, if
    e.g., int x = INT_MAX;              ++x;                  so, throw an exception.
    — Null-pointer checks:            With core-language      今天我们手动检查溢出
    空指针检查                            contract assertions,     并抛出异常
    e.g., int *p = 0;     *p = 5;    we get that for free!
                                           核心语言契约让我们
                                           免费拥有这种检查               51

## Page 52

2. Erroneous Behavior (EB)
错误行为
Erroneous
Behavior
(EB)      52

## Page 53

Safe — Erroneous Behavior (EB)
Erroneous Behavior (EB) 错误行为
Ø Defining undefined behavior to guard
against security vulnerabilities when
contract violations are not enforced.
在契约违犯未执行时，通过定义未定义行为来防范安全漏洞。
Ø EB is nonetheless still “guarded” by a
“precondition” — even if uncheckable.
尽管无法验证，EB 仍受制于一个前置条件。
Ø Importantly, incorrect use remains objectively and
observably incorrect!
重要的是，显然，错误使用仍属错误！        53

## Page 54

        Safe — Erroneous Behavior (EB)
Uninitialized Reads 未初始化的读取
§ Reading an uninitialized automatic variable now produces an erroneous value, which
  constitutes erroneous behavior.
  读取未初始化的自动变量会产生错误值 ，构成错误行为。
§ No more surreptitiously reading private data from program stack.
  不再偷偷读取程序堆栈中的私有数据。
void g(int& k); // function taking a modifiable `int` ref 函数接受可修改 int 引用
void f()
    {   int i;   // Uninitialized value! 未初始化的值！
    int j = i; // Error: EB (trap or unspecified value). 错误：EB(陷阱或未定义值）
    }   g(j);    // Possible EB — i.e., if `g` first reads `j`. 可能 EB - 当 g 先读取 j 54

## Page 55

    2. Erroneous Behavior vs. 1. Runtime Checking
        错误行为 vs. 运行期检查
                                 1. Runtime Contract Checking
    2. Erroneous Behavior        运行期检查
        错误行为
                                        Array
Uninitialized                Signed    Bounds
   Memory                    Integer    Error
    Read             Overflow          数组边界错误
   未初始化内存            有符号数溢出
     读取

Unreachable                                 Errors due to
                                             Raw-Pointer
  Pointer    Unallocated                     Arithmetic
   Error       Memory            Data Races    原始指针算术
  不可达指针错       Access            数据竞争           引起的错误
     误          未分配内存
                 错误              55

## Page 56

3. Symbolic Contract Assertions
符号契约断言
Symbolic
Contract
Assertions      56

## Page 57

          3. Symbolic Contract Assertions  Symbolic
                                           contract predicate
    Core-Language Example: 核心语言例子          (declaration-only)
                                           符号（仅声明）契
    void f(int *begin, int *end);          约谓词
         pre<symbolic>(is_reachable(begin, end));
    void g()
    {     int a[15],  b[15];  Local static analysis
          f(a, b);        identifies a
              局部静态分析发现前置条件违规
    }         precondition violation
57

## Page 58

            3. Symbolic Contract Assertions
    Prospective Standard-Container Example  Symbolic
                                       (declaration-only)
        前瞻性的标准容器例子                     contract predicate
                                             符号（仅声明）
    template <typename Iter, typename T>      契约谓词
Iter find(Iter first, Iter last, const T& value);
    pre<symbolic>(is_reachable(first, last));
int f(const std::vector<int>& a, const std::vector<int>& b, int value)
{ // ...
    bool found = (find(a.begin(), b.end(), value) != b.end());
         // ...        Error, caught at compile time via local static analysis.
    }        错误，编译期通过局部静态分析捕获 58

## Page 59

         3. Symbolic Contract Assertions
Harder, Standard-Iterator Example
    更难，标准容器的例子                                     Symbolic
                                              (declaration-only)
                                              contract predicate
template <typename Iter, typename T>                符号（仅声明）
Iter  find(Iter first, Iter last, const T& value)    契约谓词
      pre<symbolic>(is_reachable(first, last));    Inherently a runtime
int   f(std::vector<int>& vec, int value)               operation.
{     int* a = vec.begin();                              本来就是运行期操作
vec.push_back(17); // Might invalidate `a`. 有可能使 `a` 无效
int* b = vec.end();
bool found = (find(a, b, value)!= b.end());
}     // ...        Defect, but hard to catch via (compile-time) static analysis.
          缺陷，但是难以通过（编译期）静态分析捕获                           )59

## Page 60

4. Source-Code Subsetting (was “Profiles”)
源码取子集（曾经是“规格配置”）

Profiles

    60

## Page 61

      4. Source-Code Subsetting     Profiles
        subset     the
    Disallowing C-Style Casts        Language
        规格配置取语言子
      禁止 C 风格转型        集
    [[profiles::enforce(std::type)]];     *orthogonal     to
        contracts
    void f(int i)        与契约正交
    { (unsigned*)&i;// Error, type-unsafe cast // 错误，     转型类
        型不安全
* The parts of profiles that subset the language are orthogonal to contracts.
                              对语言取子集的规格配置与契约正交        61

## Page 62

5. Exclusivity Enforced at Compile Time
    编译期施行独占性
  Exclusivity
  Enforceds at
Compile Time 62

## Page 63

5. Exclusivity Enforced at Compile Time

                            Law of Exclusivity
                                   独占性原则

“If a storage reference expression evaluates to a storage reference that is
 implemented by a variable, then the formal access duration of that access
   may not overlap the formal access duration of any other access to the
              same variable unless both accesses are reads.”
                      "如果某存储引用表达式求值为由某个变量实现的存储引用，那么该
                      访问的形式访问期不得与对同一变量的任何其他访问的形式访问期重
                              叠，除非两次访问都是读取操作”
    — Apple/Swift 6.0

        63

## Page 64

        5. Exclusivity Enforced at Compile Time
Exclusivity during iteration 迭代中的独占性
#include <std2.h> // From P3390R0, by Sean Baxter

    int main() safe {
     std2::vector<int> vec { 11, 15, 20 };    Ensure Ample Space?!
     vec.reserve(1`000`000);        确保空间充足?!      Ill-formed:
     for (int x : vec) {        Cannot acquire mutable reference
      if (x % 2) {        during iteration
          mut vec.push_back(x);        非合式的：不能在迭代中获取可变引
      }        用
      std2::println(x);     // Observe something to preserve code. 观察点什么，让代码不被优化掉
     }
    }



      64

## Page 65

 6. Reference Counting Enforced at Run Time
      运行期的引用计数
Reference Counting
    Enforced at
    Run Time 65

## Page 66

6. Reference Counting Enforced at Run Time

Box Data
装箱数据
Essential (i.e., non-optional) information required by the
runtime system used to ensure proper program execution.
是运行时系统为确保程序正确执行所需的关键信息。

    66

## Page 67

 6. Reference Counting Enforced at Run Time
Reference counting during iteration
  迭代中的引用计数
    #include <vector>        “
                   Box Data” tracks iterator
    int main() safe                              validity
    {                                           装箱数据追踪迭代器有效
         std::vector<int> vec { 11, 15, 20 };        性
         vec.reserve(1`000`000);
         for (int x : vec)
         {
               if (x % 2)                  Runtime check remains
               {                             because vec might
                   vec.push_back(x);    reallocate (leading to UB).
               }                              保留运行期检查， 因为 vec
         }     std::println(x);                可能重新分配（引起UB)
    }              67

## Page 68

    6. Reference Counting Enforced at Run Time
    Iterator Invalidation (simplified)    Inherently NOT
    迭代器失效（简化后）               Compile-Time
    #include <vector>            Checkable!
                                 本来就不是编译期可以
    void f(std::vector<int>& vec)    检查的
{ int *b = vec.begin();
    vec.push_back(17); // might invalidate `b` 可能使 `b` 无效
    int *e = vec.end();
} std::sort(b, e); // error if `b` is invalid 如 `b` 无效则出错

                             68

## Page 69

    6. Reference Counting Enforced at Run Time
Iterator Invalidation + preconditions
    迭代器失效 + 前置条件        Precondition guards
#include <vector>        UB!
void f(std::vector<int>& vec)        前置条件防止UB!
{     pre(vec.size() < vec.capacity())
      int *b = vec.begin();        Cannot invalidate b
      vec.push_back(17);        不能让 b 失效
      int *e = vec.end();
}     std::sort(b, e);        b cannot be invalid
          b 不能无效

          69

## Page 70

        Exclusivity Enforced at Run Time
 Why do we call  运行期施行的独占性
it “Ghost” Data?
     为什么称之为
     “幽灵”数据                           Ghost Data
                                         幽灵数据

    Optional information made available to multiple contract assertions at various
granularities (e.g., all assertions within a particular function invocation) that would
                 not otherwise be represented in the abstract machine.
                          幽灵数据是提供给多个契约断言的可选信息，可在不同粒度级别（例如特定函数
                           调用中的所有断言）上使用，这些信息在抽象机器中不会以其他方式表示。


    70

## Page 71

   Exclusivity Enforced at Run Time

Important essential properties of Ghost Data.
幽灵数据的重要基本特性。
Ø With Ghost Data… 有了幽灵数据
—  Assertions can express any requirement whose violation
   could alter program behavior.
   断言可表达任何违反后可能改变程序行为的要求。
—  Many assertions will require core-language interfaces to update them.
   许多断言需要通过核心语言接口进行更新。
Ø Ghost Data has zero runtime overhead when…
幽灵数据在以下情况是0运行期开销。
—  Contract-assertion checks are disabled.
  契约断言检查已禁止。
—  Local analysis can prove that the assertions will not be
   violated.
   局部分析可以证明断言不会被违反。
       71

## Page 72

Exclusivity Enforced at Run Time Join Us?
Ghost Data      加入我们？
幽灵数据
Active Research Project:
正在研究中的项目
Tanium: Lisa Lippincott
Bloomberg: Joshua Berne
Citadel: Gasper Azman
The C++ Foundation: Mungo Gill
    72

## Page 73

Current Safety-Project Priorities
当前安全项目的优先级
Current
Safety-Project
Priorities      73

## Page 74

Safety — Contracts, EB, Memory Safety




              Contract
             Violations    Data Races
Vector Array    违反契约       数据竞争     Other
   Bounds        20%       2%      其他
 vector 数组边         1%
      界
     65%    Lifetime Isssues
                  生存期问题
                   2%
Erroneous Behavior
       错误行为
        10%

                    74

## Page 75

Safety — Contracts, EB, Memory Safety




              Contract
             Violations    Data Races
Vector Array    违反契约       数据竞争     Other
   Bounds        20%       2%      其他
 vector 数组边         1%
      界
     65%    Lifetime Isssues
                  生存期问题
                   2%
Erroneous Behavior
       错误行为
        10%

                    75

## Page 76

Safety — Contracts, EB, Memory Safety




              Contract
             Violations    Data Races
Vector Array    违反契约       数据竞争     Other
   Bounds        20%       2%      其他
 vector 数组边         1%
      界
     65%    Lifetime Isssues
                  生存期问题
                   2%
Erroneous Behavior
       错误行为
        10%

                    76

## Page 77

Safety — Contracts, EB, Memory Safety




              Contract
             Violations    Data Races
Vector Array    违反契约       数据竞争     Other
   Bounds        20%       2%      其他
 vector 数组边         1%
      界
     65%    Lifetime Isssues
                  生存期问题
                   2%
Erroneous Behavior
       错误行为
        10%

                    77

## Page 78

        Interaction of Various Techniques
                          各种技术的互动
        Ghost Data            幽灵数据
                              “Profiles” 规格配置
        Runtime Reference Counting 运行期引用计数       Bad Reinterpret
        Compile-Time Exclusivity 编译期独占性               Cast
                                                     不良重解释转型
Runtime Contract Checking
         运行期契约检查                                  Errors due to
Uninitialized             Signed        Array      Raw-Pointer
   Memory                 Integer        Bounds    Arithmetic
    Read        Overflow        Error               原始指针算术引起
  未初始化的内存读     有符号数溢出         数组边界错误                   的错误
      取                                             Symbolic
    Erroneous Behavior                          Contract Checking
  错误行为                                               符号契约检查
                                                   Unreachable
Unallocated                                          Pointer
  Memory                      Data Races              Error
                              数据竞争                      误
  Access                                             不可达指针错
  访问未分配内存
78

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/John_C++ “安全优先”开发模式演进与路线图.pdf]]`
