---
type: source
source-type: slide
title: "David Sankel_大规模安全 C++：纵深防御策略"
path: slides/David Sankel_大规模安全 C++：纵深防御策略.pdf
source-md5: 2d9bcfc7e9aa0a232bbb663dd9074f8d
size: 2109 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# David Sankel_大规模安全 C++：纵深防御策略

> Ingested from `slides/David Sankel_大规模安全 C++：纵深防御策略.pdf` via `lit parse` on 2026-06-04.
> Source file: 2.06 MB.

## Page 1

© 2025 Adobe. All Rights Reserved.

## Page 2

© 2025 Adobe. All Rights Reserved.

## Page 3

© 2025 Adobe. All Rights Reserved.

## Page 4

© 2025 Adobe. All Rights Reserved.

## Page 5

© 2025 Adobe. All Rights Reserved.

## Page 6

Safe C++ at
Scale
A Defense in Depth
Strategy
大规模C++安全实践:纵深防御
策略
David Sankel | Principal Scientist

      Im
      a
      ge
      generated
      with
      A
      d
      o
      be
      Firefly

## Page 7

Secure C++ at
Scale
A Defense in Depth
Strategy
大规模C++安全实践:纵深防御
策略
David Sankel | Principal Scientist

      Im
      a
      ge
      generated
      with
      A
      d
      o
      be
      Firefly

## Page 8

自我介绍
§ Principal Scientist at Adobe/Adobe
首席科学家
§ Leading the Tech Foundations Group
管理一个技术基础团队
§ Also lead Software Technology Lab
以及一个软件技术实验室





为std::variant、std::input_vector、反射和C++语
§ Director, Boost Foundation/Boost
言的许多其他方面做出了贡献

基金会负责人
    © 2024 Adobe. All Rights Reserved. Adobe Confidential.    © 2025 Adobe. All Rights Reserved.

## Page 9

 Current State of
 当前的安全形势

9

## Page 10

Vulnerability Root Causes/缺陷的根本原因
 Other 30%  24%  30%  6%      33%
 Memory Safety 70%  76%  70%  94%  67%
 Microsoft      e      um
     id        al      ties (2021)
     © 2025 Adobe. All Rights Reserved.

## Page 11

Vulnerability Root Causes/缺陷的根本原因
 Other 30%  24%  30%  6%      33%
 Memory Safety 70%  76%  70%  94%  67%
 Microsoft      e      um
     id        al      ties (2021)
     © 2025 Adobe. All Rights Reserved.

## Page 12

Vulnerability Root Causes/缺陷的根本原因
 Other 30%  24%  30%  6%      33%
 Memory Safety 70%  76%  70%  94%  67%
 Microsoft      e      um
     id        al      ties (2021)
     © 2025 Adobe. All Rights Reserved.

## Page 13

Vulnerability Root Causes/缺陷的根本原因
 Other 30%  24%  30%  6%      33%
 Memory Safety 70%  76%  70%  94%  67%
 Microsoft      e      um
     id        al      ties (2021)
     © 2025 Adobe. All Rights Reserved.

## Page 14

Vulnerability Root Causes/缺陷的根本原因
 Other 30%  24%  30%  6%      33%
 Memory Safety 70%  76%  70%  94%  67%
 Microsoft      e      um
     id        al      ties (2021)
     © 2025 Adobe. All Rights Reserved.

## Page 15

关键洞察：我们并非败于逻辑，而是败于内存管理







© 2025 Adobe. All Rights Reserved. 15

## Page 16

Where do vulnerabilities come from?
缺陷一般来自何处？

 Vulnerabilities are found and patched over
 time.
 遗留代码：经过实战考验，依然随时间推移被发现有缺陷并修复
identified vulnerabilities.
新代码：新发现缺陷的主要来源
 density is highest in code written in the last 1-
 数据：研究显示，最近1-2年写的代码中的缺陷
 密度最高

暗示：如果我们停止在新代码中引入 bug，问题最终
就会消失        © 2024 Adobe. All Rights Reserved. Adobe Confidential.
      16        © 2025 Adobe. All Rights Reserved.

## Page 17

Not all C++ code is equally safety / security critical
并非所有 C++ 代码在功能安全与安全防护方面同等重要
§ Widely deployed software
大范围部署的软件
§ Handling untrusted inputs
处理不受信任的输入

§ File format parsers
文件格式解析
§ Network protocol parsing
网络协议解析
插件/脚本接口
    © 2025 Adobe. All Rights Reserved.     17

## Page 18

Recommendation #1: The
“Nuclear” Option
建议#1: 终极方案
Use a Memory-Safe Language (Rust)

逻辑：如果新代码是主要问题，那就用安全的语言写新代
码
证据：Android 在向 Rust 迁移

 代码回滚率低4倍；代码走查效率高 25% © 2024 Adobe. All Rights Reserved. Adobe Confidential.
    18        © 2025 Adobe. All Rights Reserved.

## Page 19

The reality check: Why we can’t always use Rust
务实审查：Rust 并非万能良药
1. Complexity: Introducing a second toolchain and build system.
2.1. 复杂性：引入一个新的工具链和构建系统
3.2. 小片段问题：如果你有一千万行 C++ 代码，但只需要加入 500 行新功能，那么为了这点小功能而引入 Rust 就不值
4. 得
Conclusion: We are stuck with C++ for a long time. We need a strategy for existing
结论：我们会和C++共存很长时间，需要一个策略应对已经存在的代码库 © 2025 Adobe. All Rights Reserved. 19

## Page 20

Defense-in-depth strategy | The ”Swiss Cheese”
model
深度防御策略：“瑞士奶酪”模型
protections. If one layer fails, the next catches the
bug.
一层可以捕捉 bug。
1. Isolate: sandboxing
   隔离：使用沙箱
2. Harden: compiler & library flags
   加强：编译器选项和库的特性
3. Detect: sanitizers & fuzzing
   检测：（内存）消毒器与模糊测试
4. 预防：现代编程实践 & 避免 UB（未定义行为）
        © 2024 Adobe. All Rights Reserved. Adobe Confidential.
20 © 2025 Adobe. All Rights Reserved.

## Page 21

第1层：沙箱隔离-控制爆炸半径
If a parser is exploited, ensure it cannot touch the rest of the system.
如果一个解析器被利用，请确保它不会触及系统的其他部分。

识别关键组件：解析不可信输入（图像、JSON、网络数据包）的代码
§ Solutions
解决方案

WebAssembly (Wasm): 先将C++编译成Wasm，然后在一个轻量级的运行库中运行 (比如 RLBox)
OS 级别: Seccomp-bpf (Linux), AppSandbox (Mac), AppContainer (Windows)
    © 2025 Adobe. All Rights Reserved.     21

## Page 22

Layer 2a: Low Cost Hardening—“Free Lunch” Compiler
Flags
第 2a 层：低成本强化-“实惠”的编译器选项

 § Initializes all stack variables to a recognizable pattern.
 用可识别的模式初始化所有栈变量
 § Prevents uninitialized memory exploits.
 禁止使用未初始化的内存
§ -D_FORTIFY

 § Prevents certain stack overflow exploits at runtime
 在运行期阻止特定的栈溢出攻击
     更多选项请参考开源软件安全基金会(OpenSSF)发布的《C/C++编译器强化选项指南》
     © 2025 Adobe. All Rights Reserved.     22

## Page 23

    Medium Cost Hardening—Libc++ Hardening
第 2b 层：中等开销强化-Libc++ 增强
The Standard Library knows your preconditions. Let it check them.
§ Fast Mode: -D
只要标准库知道你的前置条件，就先检查它们
    _LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST
§ Designed for production
为生产环境而设计
D        _MODE=_LIBCPP_HARDENING_MODE_EXTENSIVE
§ More checks. Higher cost
§ Debug Mode : -D
    更多的检查，更高的开销
    _LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_DEBUG
§ Full internal consistency checks. Development only.
See also -D        _HARDENING for
    启用全部内置一致性检查，仅在开发阶段使用
    _GLIBCXX        _MSVC_STL
    libstdc++ 使用-D     _ASSERTIONS ，MSVC 使用
    _GLIBCXX        _MSVC_STL_HARDENING
    © 2025 Adobe. All Rights Reserved.     23

## Page 24

    第 3 层： Dynamic analysis (development)
    动态分析（开发阶段）
   Sanitizers: You cannot ship these (usually), but you must test with them
   消毒工具：通常不随产品发布，但是必须在测试时使用


 TSan(线程消毒工具)：捕捉数据竞争问题
§ Principle: Your attackers are fuzzing your code. You should fuzz it first.
 工作流程：写一个模糊测试 → 发现 Bug → 修复 Bug © 2025 Adobe. All Rights Reserved. 24

## Page 25

第 4 层：     编程实践
The Root Cause: Undefined Behavior
根本原因：未定义行为
在 C++ 中，UB 不是 Bug，但是是安全缺陷
Example: Signed Integer Overflow / 例子：有符号整数溢出
int main() {
    int i = INT_MAX;
    // This is UB. The compiler can assume this NEVER happens.
    // It might optimize away your security check!
    if (i + 1 < i) {
        // "Security check" - Deleted by compiler optimization
}   }   return error;

关键：
目标：写不含UB的代码        © 2025 Adobe. All Rights Reserved.      25

## Page 26

消除UB：使用现代习语 Utilize modern idioms

    § Higher-level constructs, in general, are safer to use
    一般而言，高级抽象的（代码）构造安全性更佳

    § Avoid shared mutable state. (indices are safer than iterators)
    避免共享可变状态（使用索引比使用迭代器更安全）

   § Prefer “always on” precondition checks
    优先使用那些“总是开启的” 前置条件检查
        © 2025 Adobe. All Rights Reserved.     26

## Page 27

The Future: C++26 Contracts | A standard way to
avoid UB
展望未来：


    断言(contract                  _assert!): Check within function.
    The ! Syntax is for hardened checks that cannot be disabled. Prefer those.
           用于强化检查的！语法不能被禁止，优选使用
    // C++26 Syntax Example
    int safe_divide(int a, int b)
       pre!( b != 0 )          // Hardened precondition
    {  post( r: r == a / b )   // Postcondition
    }  return a / b;               © 2025 Adobe. All Rights Reserved.      27

## Page 28

The Future: Better Rust interop
展望未来：更好的 Rust 互操作性





 目标:增量式迁移：主要用于新增代码。你可以用 Rust 重写危险的解析器，但保持现有的 C++ 代码不变

 © 2025 Adobe. All Rights Reserved.     28

## Page 29

Conclusion: Your action plan
结论：你的行动计划
1.
2.     存量 C++ 代码
   1.   Isolate: Sandbox your parsers.
        隔离：用沙箱隔离解析器
   2.
   3.
   4.   Prevent: Teach your team that Undefined Behavior = Security Vulnerability.
        预防：让你的团队认识到“未定义行为就是安全缺陷”

            © 2025 Adobe. All Rights Reserved.     29

## Page 30

Q & A





© 2025 Adobe. All Rights Reserved. 30

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/David Sankel_大规模安全 C++：纵深防御策略.pdf]]`
