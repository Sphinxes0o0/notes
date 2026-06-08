---
type: source
source-type: slide
title: "Bjarne_C++跨越40载的成功经验与未来演进"
path: slides/Bjarne_C++跨越40载的成功经验与未来演进.pdf
source-md5: 450a3b3b394433511934dd5b431004ec
size: 6520 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# Bjarne_C++跨越40载的成功经验与未来演进

> Ingested from `slides/Bjarne_C++跨越40载的成功经验与未来演进.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.37 MB.

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

C++跨越40载的成功经验
与未来演进

Bjarne Stroustrup
哥伦比亚大学
Bjarne@stroustrup.com

## Page 7

Abstract

• Why did C++ succeed on a massive scale without marketing or a rich
  owner? Its imminent death was frequently predicted even from before it
  was called C++. The reason is that C++ some key C++ features serve
  widespread needs, are manageable by “ordinary developers”, and stable
  over decades.
• Here, I will describe the role of classes with constructors and destructors,
  templates with concepts, and modules in contemporary C++. Also, I will
  briefly explain the plans for “Profiles” to manage the complexity accreted
  over decades of serious use.
• Along the way, I’ll try to put the evolution of C++ in its historical context.

• 70 minutes + Q&A

        Stroustrup - C++ at 40 - China 2025 7

## Page 8

好的设计始于问题

• 我想构建一个分布式 Unix 系统
• 时间回到 1979 年
• 当时没有语言能满足我的所有需求

• 我需要高效的硬件操作
• 像 C 语言那样

• 还需要管理复杂性的抽象能力
• 像 Simula 语言那样
• 以及一个灵活的“强”静态类型系统

    Bjarne Stroustrup, 摄于 1986
    Stroustrup - C++ at 40 - China 2025    8

## Page 9

核心理念：在代码中直接表达思想
• 示例
• 数学：张量，多项式
• 工程：矩阵，傅里叶变换
• 图形学：着色，Gnome，路径
• 生物学：DNA序列，蛋白质
• 电信：缓冲区，通道
• 航空航天：电机，航线
• 汽车：车辆，汽车，行人
• 金融：金融工具，交易
• 计算机科学：映射，任务，图像，文件，边
• …
• 并且要让其代价合理
• 唯一的限制是你的想象力
• 注：大多数优秀的软件都是无形的。
    Stroustrup - evolution - 2024    9

## Page 10

优秀的设计，基于合理的原则

• 灵活的静态类型系统
• 可扩展性
• 零开销
• 最少的显式类型转换
• 资源管理
• 防止泄漏
• 错误处理
• 提供保证
• 灵活的并发支持                                  当代 C++
• 不局限于一种风格                                 能比以往任何早期的 C++
                                           更好地实现这些目标。

    Stroustrup - C++ at 40 - China 2025        10

## Page 11

好的工具随需求而演进
• 为什么要演进？
  • 世界在变
  • 问题在变
  • 我们在变
• 优秀的工程依赖于反馈和改进
  • 例如：泛型编程，编译期编程，模块

• “任何声称拥有完美语言的人，不是推销员就是愚人，或者两者兼有”
  – Bjarne Stroustrup 1980年代起
• “即使是我也能设计出一门更漂亮的语言”
  – Bjarne Stroustrup 1980年代起

      Stroustrup - C++ at 40 - China 2025    11

## Page 12

稳定性与演进

• 稳定性：过去运行良好的代码，现在依然运行良好
• 演进：通常，我们今天可以做得更好
• 现实世界的进步：开发者如何跟上必要的变革？







 Stroustrup - C++ at 40 - China 2025    12

## Page 13

            C++        生来就被设计为持续演进的语言，
            其使用规模也在不断增长
 6000000               展示 C++ 用户数量的粗略估计
 5000000          C++11        C++20
                  concurrency, lambdas, time, range-for, auto, concepts, coroutines, modules,
                  constexpr, shared_ptr, tuple, regex, …       ranges, calendars, span, format, …
 4000000
                   C++98
 3000000           exceptions, templates, the STL,
                   Namespaces, …
 2000000                                                                    C++17
             First commercial release                                       template argument deduction, …
             virtual functions, iostreams, complex,        C++14
 1000000     const, operators, …        variadic templates, generic lambda, …

           0
             1980      1985      1990    1995      2000      2005      2010      2015      2020
C with Classes         ANSI/ISO standardization starts
classes, function declarations,
constructors and destructors,        Stroustrup - C++ at 40 - China 2025        13
coroutines

## Page 14

统计 C++ 用户非常困难

    • 谁是开发者？程序员？
    • 学生算吗？
    • 经理、规划人员、测试人员、文档编写者等算吗？
    • 大多数开发者使用多种语言
    • 并非所有开发者的影响都相同
    • 但在统计时却被一视同仁
    • 企业软件
    • 嵌入式系统
    • 开源或社区项目
    • 个人项目
    • 许多组织不公布其开发者数量
    • 不同的组织使用不同的统计方法
    • 一些用户和组织在网络上制造了很大声量
    • 但许多并没有
Stroustrup - C++ at 40 - China 2025 14

## Page 15

数据来源：
    www.slashdata.co
有多少开发者？





                                                 1200 万
                                                 似乎是一个
                                                 保守的估计

• 许多人信任这个来源
      2025 年有 1630 万 C++ 开发者
      4 年内 C++ 开发者数量增长了 72%（每年近 20%！）
      4 年内新增近 700 万开发者（每年近 200 万！）
  •   与 Java 和 Python 一起，C++ 开发者群体的增长速度明显快于其他语言
          Stroustrup - C++ at 40 - China 2025    15

## Page 16

当代 C++ 不仅仅是新特性

    • 一些关键特性和技术已存在很久，例如：
    • 带构造函数和析构函数的类
    • 异常        不要盲目使用所有新特性
    • 模板
    • std::vector        也不要局限于仅使用新特性
    • 一些是较新的，例如：
    • 模块
    • 概念（用于指定泛型接口）
    • Lambda 表达式（用于生成函数对象）
    • 范围
    • constexpr 和 consteval（用于编译期计算）
    • 并发支持和并行算法        更多关于最新特性和
    • 协程（虽然它们是早期 C++ 的重要部分，但缺失了几十年）    未来发展方向的讨论，
    • std::shared_ptr        请参考YouTube上的
    • 关键在于将这些特性作为一个整体来运用        相关视频
        Stroustrup - C++ at 40 - China 2025    16

## Page 17

编程语言的价值
体现在应用程序的质量之中










Stroustrup - C++ at 40 - China 2025    17

## Page 18

    在这里，我重点关注

    • 资源管理
• 包括生存期控制和错误处理
    • 泛型编程
• 包括概念
    • 模块
• 包括逐步淘汰预处理器
    • 指南及其施行
• 以保证我们编写的是“21世纪的 C++”？

Stroustrup - C++ at 40 - China 2025 18

## Page 19

资源管理

• 资源是你必须获取并随后释放（归还）的任何东西
  显式地或隐式地
• 例如：内存、字符串、锁、文件句柄、套接字、线程句柄、事务、着色器...
• 防止资源泄漏        句柄
• 避免手动释放
• 在应用代码中防止使用 free()、delete 以及类似的资源释放    资源
• 每个资源都由一个句柄表示
• 负责访问和释放
• 在应用代码中防止使用 malloc()、new 以及类似的返回指针的资源获取
• 每个资源句柄都根植于一个作用域中
• 并且句柄可以从一个作用域移动到另一个作用域

    Stroustrup - C++ at 40 - China 2025    19

## Page 20

提升抽象层次
                                   类型参数                              C++ 的基石：
template<typename T>                                                 构造函数/析构函数
class Vector {        // T 类型元素的 vector
public:
       Vector(initializer_list<T>);    // 获取内存；初始化元素 – 构造函数
       ~Vector();        // 销毁元素；释放内存 – 析构函数
       // …
private:        底层
       T* elem;        // 指向元素的指针                                    Vector
};     int sz;       // 元素数量                                             元素
void fct()
{      Vector<double> constants {1, 1.618, 3.14, 2.99e8};
       Vector<string> designers {"Strachey", "Richards", "Ritchie"}; 规则会递归应用
       // …
       Vector<pair<string,jthread>> vp { {"producer",prod}, {"consumer",cons}};
}          Stroustrup - C++ at 40 - China 2025                           20

## Page 21

生存期控制

• 对于简单且高效的资源管理是必要的
• 构造
• 在首次使用前建立不变量（如果有的话）
• 构造函数
• 析构
• 在最后一次使用后释放每一项资源（如果有的话）
• 析构函数
• 拷贝
• 拷贝：a=b 意味着 a==b（规则类型）
• 拷贝构造函数：X(const X&)
• 拷贝赋值：X::operator=(const X&)
• 移动
• 在作用域之间移动资源
• 移动构造函数：X(X&&)
• 移动赋值：X::operator=(X&&)
    Stroustrup - C++ at 40 - China 2025    21

## Page 22

输出按行去重 #1
// 下面的代码替代了AWK中的(!a[$0]++)模式，避免了隐式I/O和循环        无需 显式处理
                                                    内存的分配与释放
                                                    设定容器大小
import std;                                         错误处理
using namespace std;                                类型转换
                                                    指针
                                                •   使用预处理器
int main()     // 从输入打印不重复行                     执行效率高
{                                               •   可调优
     unordered_map<string,int> m;        // 使用哈希表存储
     for (string line; getline(cin,line); )
         if (m[line]++ == 0)
         cout << line << '\n';
}

         Stroustrup - C++ at 40 - China 2025            22

## Page 23

输出按行去重 #2     —— 获取不重复行

import std;
using namespace std;

vector<string> collect_lines(istream& is)     // 从输入获取不重复行
{
     unordered_set<string> s;                 // 哈希表      vector 的元素类型
     for (string line; getline(is,line); )                可被推导出来
         s.insert(line);
     return vector{from_range, s}; // 将集合元素拷贝到 vector 中
}                                                 vector 被移动，而非被拷贝
auto lines = collect_lines(cin);
for (auto& s : lines)
     cout << s << "\n";
         Stroustrup - C++ at 40 - China 2025                  23

## Page 24

输出按行去重 #3     —— 消除拷贝
vector<string> collect_lines(istream& is) // 从输入获取不重复行
{
unordered_set<string> s {from_range,istream_view<Line>{is}}; // 直接从输入构建集合
 return vector{from_range,s};
}

auto lines = collect_lines(cin);

• Use move a constructor for vector
 • Faster and simpler than using new, a pointer, and delete
• Or even better: construct the vector in lines (since 1983)
 • “copy elision”

    Stroustrup - C++ at 40 - China 2025        24

## Page 25

消除拷贝：
    重要细节
• 但标准库没有 Line 类型
• 所以我建立了一个
struct Line : string { };
istream& operator>>(istream& is, Line& ln) { return getline(is, ln); }

• 注：传统的面向对象编程        Kristen Nygaard
• 不要痴迷于只使用新特性
• 许多旧特性仍然必不可少，并且往往是完成其擅长任务的最佳选择



Stroustrup - C++ at 40 - China 2025    25

## Page 26

输出按行去重 #4 —— 消除更多拷贝
• 如果编译器不够智能，无法将 set 元素移动到 vector 中
    我们可以显式地做（重新实现移动到 vector 的逻辑，使用循环或视图）
  • 在性能至关重要的地方，调优（在测量之后）是一项重要的活动
vector<string> collect_lines(istream& is)  // 从输入获取不重复行
{
    unordered_set<string> s {from_range, istream_view<Line>{is}};
    return vector{from_range,std::move(s)};
}
                                               高层级代码
for (auto& s : collect_lines(cin))               可以非常高效
    cout << s << "\n";                         • 可以被调优

        Stroustrup - C++ at 40 - China 2025        26

## Page 27

调优

• 对某些代码来说是必要的
  •  “避免过早优化”
  • 永远在优化前后进行测量
  • 设计接口以允许在需要时进行优化
     • 定义明确
     • 类型丰富
     • 包含足够的信息以启用检查和优化
• 复杂度管理
  •  让简单的事情保持简单！
• 抽象层次
  •    剥得越多，哭得越多
         Stroustrup - C++ at 40 - China 2025    27

## Page 28

资源与错误
• 一般原则
• 杜绝资源泄漏          如果每个资源都有资源句柄，这很容易。
• 不要让资源处于无效状态     如果没有，基本上不可能做到。
• 当错误发生时
• 在退出函数之前
• 将访问过的每个对象置于有效状态
• 释放该函数拥有的每个对象



Stroustrup - C++ at 40 - China 2025    28

## Page 29

资源句柄与指针
• 不要使用内置指针作为资源句柄
•  “不要直接使用 new”
void f(int n, int x)
{   Gadget g {n};     // 一个 Gadget 可能持有资源，如内存、锁和文件句柄
    Gadget* pg = new Gadget{n};    // 显式 new：不要这样做！
    // …
    if (x<100) throw std::runtime_error{"Weird!"} // *pg 泄漏了; g 不会泄漏
    if (x<200) return;        // *pg 泄漏了; g 不会泄漏
}   // …
• 局部对象比显式 new 更简单，且通常更快
        Stroustrup - C++ at 40 - China 2025        29

## Page 30

 制定清晰的错误处理策略

• 对于常见且可在局部处理的失败，使用错误码和测试
  • 确保未检查错误会导致终止或异常，而不是错误的结果
• 对于罕见的（“异常的”）或无法在局部处理的失败，使用异常
  • 用于处理构造函数、运算符和其他没有简单方法返回错误指示器的函数中的错误（例如：
   Matrix x = y+z;）
  • 用于自动将错误沿调用链向上传播给处理程序
  • 替代方案是“错误码地狱”，调用栈上的每个调用者都必须记得测试
  • 不使用指针作为资源句柄 —— 始终使用作用域资源句柄 (RAII)
• 对于某些关键应用而言，绝不允许无条件立即终止。

        Stroustrup - C++ at 40 - China 2025 30

## Page 31

错误处理                                想象一下，如果使用基于错误码的
                                    错误处理，这段代码会是什么样子

• 依赖 RAII
   • 即使在小型系统中，异常也可以比错误码更便宜、更快：C++ Exceptions for Smaller
   Firmware

void fct(jthread& prod, string name)
{
   ifstream in { name };
   if (!in) { /* … */ }      // 预期可能发生错误
   // …
   vector<double> constants {1, 1.618, 3.14, 2.99e8};  // 内存可能耗尽
   vector<string> designers {"Strachey", "Richards", "Ritchie"}; // 嵌套构造
   auto dmr = "Dennis “s + "M. " + designers[2];
   // …
    jthread cons { receiver };
    pair<string,jthread&> pipeline[] = { {"producer", prod}, {"consumer", cons}};
}   // …        Stroustrup - C++ at 40 - China 2025        31

## Page 32

泛型编程

• 当代 C++ 的关键基础
• 更短、更易读的代码
• 更直接的思想表达
• 零开销抽象
• 类型安全
• 在标准库中无处不在
• 容器和算法        Alex Stepanov
• 并发：线程、锁等
• 内存管理：分配器、资源管理指针等
• I/O
• 字符串和正则表达式
• …

    Stroustrup - C++ at 40 - China 2025    32

## Page 33

基于概念的泛型编程
• 编写适用于所有合适实参类型的代码
void sort(Sortable_range auto& r);
vector<string> vs;
// … fill vs …        概念：
sort(vs);        •     明确指定对类型 r 的要求
array<int,128> ai;                隐式：
// … fill ai …                        容器类型
sort(ai);                             元素类型
                                      元素数量
list<int> lsti;                   •   比较准则
// … fill lsti …
sort(lsti);        // 错误：list 不提供随机访问
    Stroustrup - C++ at 40 - China 2025    33

## Page 34

模板

• C++ 对泛型编程的支持基于三个目标
     极其通用/灵活：“它必须能够做比我想象的多得多的事情”
     零开销：像 vector 和 Matrix 这样的抽象可以与 C 数组竞争
     定义明确的接口：意味着类型安全、重载和良好的错误信息

 直到本世纪我们才找到同时实现这三个目标的方法
     Bjarne Stroustrup: Concept-based Generic Programming. October 2025.
     Gabriel Dos Reis and Bjarne Stroustrup: Specifying C++ Concepts. POPL06.
      January 2006.

        Stroustrup - C++ at 40 - China 2025 34

## Page 35

模板 —— 一个经典 (C++98)                              的使用示例
template<typename Random_access_iterator, typename Compare = std::less>
void sort (Random_access_iterator first, Random_access_iterator last, Compare
= Compare{})
{ … }                                           调用时会使用 > 的标准库函数
vector<string> v = { "CPL", "BCPL", "C",        对象
    "C++" };
sort(begin(v), end(v));                         // 对 vector 排序
sort(begin(v), begin(v)+size(v)/2);             // 对 vector 的前半部分排序
sort(begin(v), end(v), greater<string>{});      // 按降序排序字符串
int a[] = { 3,1,4,2,6,9,0,-1};                    一个 lambda 表达
                                                  式，生成一个函数对
sort(begin(a), end(a));             // 对数组排序      象
sort(begin(a), end(a), [](int x, int y) { return abs(x)<abs(y); }); // 按绝对值排序
    Stroustrup - C++ at 40 - China 2025               35

## Page 36

模板 —— 一个经典 (C++98)    的使用示例

• 这种用于 sort() 的泛型编程风格是
• 非常通用、灵活且传统的
• 有点啰嗦
• 直到很晚才进行类型检查（在“模板实例化时”），意味着丑陋的错误信息
• 接近最优效率
• 成功于大规模应用
• 违反了接口应该被精确定义这一基本目标（和一般原则）

    我们必须做得更好
    Stroustrup - C++ at 40 - China 2025    36

## Page 37

用于指定约束的概念
• 概念是一个编译期谓词
• 一个在编译期运行并产生布尔值的函数
• 通常由其他概念构建而成
                            有现成的概念库
• 指定 sort() 的要求             <ranges>: random_access_range 和 sortable
• 第一次尝试

template<typename R>
concept Sortable_range =
random_access_range<R>      // 拥有 begin()/end(), ++, [], +, …
&& sortable<iterator_t<R>>; // 可以比较和交换元素

void sort(sortable auto& r);
    Stroustrup - C++ at 40 - China 2025        37

## Page 38

    概念
    • 那个简单的 Sortable_range 对于基础库来说不够通用
    • 我们需要指定比较准则

    template<typename R, typename Compare = ranges::less>
    concept Sortable_range =
      random_access_range<R>      // has begin()/end(), ++, [], +, …
      && sortable<iterator_t<R>, Compare>; // 使用 Compare 比较元素
    template<Sortable_range R, typename Compare = ranges::less>
    void sort(R& r, Compare cmp = {});

    • 概念可以接受多个参数
• 它们不仅仅是类型的类型
    • 标准库算法和概念非常通用
    • 通常带有许多参数和重载Stroustrup - C++ at 40 - China 2025        38

## Page 39

使用

• 现在我们可以直接表达对容器的排序
  vector v = { 1,5,2,8,-1 };

  sort(v);        // 使用 < 排序
  sort(v, ranges::greater{}); // 使用 > 排序
  list lst = { 1,5,2,8,-1 };
  sort(lst);        // 错误：list 不是 Sortable_range – 无随机访问

                                             兼容性/稳定性
                                             是一个重要的特性

      Stroustrup - C++ at 40 - China 2025        39

## Page 40

使用 —— 但是接受一对迭代器的传统 sort() 怎么办？
• 基于概念的重载
template<typename Iter, typename Compare = ranges::less>
concept Sortable_iterator =
random_access_iterator<Iter>     // 具有 begin()/end(), ++, [], +, ...
 && sortable<Iter, Compare>;     // 使用 Compare 比较元素
template<Sortable_iterator Iter, typename Compare = ranges::less>
void sort(Iter first, Iter last, Compare cmp = {});
• 使用
vector v = { 1,5,2,8,-1 };
sort(v.begin(),v.end()); // 传统方式
sort(v);    // 表达更直接                               兼容性/稳定性
                                                   是一个重要的特性

    Stroustrup - C++ at 40 - China 2025                40

## Page 41

概念

• 我们一直都有概念这一思想。例如：
• C 内置类型：算术类型和浮点类型（大概自 1972 年起）
• STL 概念：迭代器、序列和容器（自 1990 年代初起）
• 数学概念：单子，群，环，域（几个世纪以来）
• 图概念：边，顶点，图，DAG（自 1736 年起）
• 除非程序员脑海中对涉及的概念有清晰的认识，否则任何泛型程序都无法工作。
• 相对较新的是，我们可以定义它们以便在代码中使用。
• C++ 概念是可以接受类型实参的编译期函数（谓词）。
• 简单
• 通用
• 我们必须学会有效地使用概念

    Stroustrup - C++ at 40 - China 2025    41

## Page 42

概念通常由其他概念构建而成

template<typename R, typename Pred = ranges::less>
concept Forward_sortable_range =
       ranges::forward_range<R> // 具有 begin()/end(), ++, ...
       && sortable<ranges::iterator_t<R>, Pred>; // 使用 Pred 比较元素








    Stroustrup - C++ at 40 - China 2025    42

## Page 43

    概念可以由语言基本特性构建

    template<typename T, typename U = T>
    concept equality_comparable = requires(T a, U b) { // 使用模式
     {a==b} -> Boolean;
     {a!=b} -> Boolean;
     {b==a} -> Boolean;
     {b!=a} -> Boolean;
    }

    • 使用模式
    • requires 运算符是一种底层机制，用于检查构造是否为有效的 C++。
     • 它对于表达底层要求至关重要，但在高层级代码中最好避免使用，在那些地方使用命
     名概念（通常使用 requires 构建）更易于理解和维护。

Stroustrup - C++ at 40 - China 2025 43

## Page 44

使用模式

• 概念指定了模板必须能够对其参数做什么
• 确切地说，参数类型不是必须的
• 例如：在 requires(X a, Y b) {a+b;} 中，a+b 中的 + 可以由以下任何一种方式提供
• X operator+(X,Y);                  // 如果 a 是 X 且 b 是 Y
• X X::operator+(const Y&);          // 如果 a 是 X 且 b 是 Y 的派生类
• Y operator+(const X&, const Y&);   // 如果 X 可以由 Y 隐式构造
                                     // 且 Y 可以由 X 隐式构造
• Y operator+(Y,X&);                 // 如果 Y 可以由 X 隐式构造
                                     // 且 b 是 X
• … 还有更多 …
• 这很重要。
• 处理混合模式算术
• 处理隐式转换
• 接口稳定性（随着 + 定义的变化）     Stroustrup - C++ at 40 - China 2025 44

## Page 45

概念的益处
• 支持好的设计
• 就像类所做的那样
• 可读性，可维护性
• 过度使用无约束的类型（auto 和 typename）是问题的来源
• 大幅改进错误信息
• 重载
• 像函数一样，但更简单




Stroustrup - C++ at 40 - China 2025    45

## Page 46

简化设计 —— 示例：    条件属性
• 概念提供了简单、优雅的条件表达方式
template<typename T> class Ptr {
  // ...
  T* operator->() requires is_class_v<T>; // 仅当 T 是类时才提供 -> 运算符
};
template<typename T, typename U> class Pair {
  // ...
  // 构造函数 (仅当类型可转换为成员时)：
  template<convertible_to<T> TT, convertible_to<U> UU>
  Pair(const TT&, const UU&);
};

      Stroustrup - C++ at 40 - China 2025        46

## Page 47

模块                    终于实现了！
                      这一特性在1994年的《D&E》中就已提出
• 头文件包含的顺序依赖问题：            •  相比之下，模块化：
#include "a.h"                    import a;
#include "b.h"                    import b;
• 可能与下面的情况效果不同：       •     与顺序无关：
#include "b.h"
#include "a.h"                    import b;
• #include 是文本包含机制                import a;
• 这种机制导致：                  •  import 不具有传递性
• #include 具有传递性           •  优势：
• 相同的代码被重复编译多次            •     编译工作只需执行一次
• 容易引发宏定义冲突等问题

    Stroustrup - C++ at 40 - China 2025    47

## Page 48

模块

• 提升代码质量: 实现真正的模块化（特别是避免宏的污染）
• => 显著提升编译速度（不是百分比级的提升，而是数量级的提升）
export module map_printer;    // 定义一个倍数
import iostream;        Imports
import containers;        不具有传递性
using namespace std;
export        // 这是模块导出的唯一实体
template<Sequence S>
void print_map(const S& m) {
    for (const auto& [key,val] : m) // 将键值对拆分
}        cout << key << " -> " << val << '\n';
    Stroustrup - C++ at 40 - China 2025       48

## Page 49

    标准库模块化

    • 模块 std 包含了完整的 std 命名空间










        以十分之一的时间提供十倍的信息 - 效率提升 100 倍
参考文档： http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2412r0.pdf
        Stroustrup - C++ at 40 - China 2025 49

## Page 50

   模块 —— 不仅仅用于标准库








• 25 倍的加速        观看这个视频。
       不要指望所有情况下都有这种效果        非常震撼
   •   Daniela Engert: Contemporary C++ in
       Action        Stroustrup - C++ at 40 - China 2025    50

## Page 51

这重要吗？
• 经过基本测试后，我已经很多年没见过资源泄漏了
• 我曾重新设计了一个 1990 年代的设计以提高可靠性
• 不是玩具：它已在生产环境中使用 20 多年
• 关键技术：简化！
• 新设计意外地快了 100 倍
• 我没有使用比本次演讲中你所看到的更高级的东西
• 在生产代码中
• 实验性代码受到的约束较少
• 这些技术非常广泛适用
• 资源管理
• 错误处理
• 泛型编程
• …
    Stroustrup - C++ at 40 - China 2025    51

## Page 52

并发

• 为了效率
• 因此，有许多不同的风格
• 许多优化技术
  • 广泛的支持
• 线程和锁
• 共享
• 并行算法
• 协作取消
• Futures
• 协程
• …          这是一个重要话题，需要专门的
             讲座来详细讨论
    Stroustrup - C++ at 40 - China 2025    52

## Page 53

    不要被困在 20 世纪
    • 现代编程方式的优势
    • 适用于大多数场景
    • 升级代码很难
    • 但可能是最有益的
    • 通常可以循序渐进地完成
    • 新代码无需延续过时的范式

    如何实现？
    • 想避开不够理想的技术并不容易
    • 历史代码的影响
    • 固有习惯的束缚
Stroustrup - C++ at 40 - China 2025 53

## Page 54

指南与其施行
• 我们无法改变语言
• 我们可以改变它的使用方式
• 稳定性/兼容性是一个主要特性
• 逐步采用新特性和技术是至关重要的
• 指南
• 个别规则可以选择使用或不使用
• 施行是不完整的
• 现已可用：C++ Core Guidelines
• 规格配置
• 强制施行的连贯的指南规则集
• WG21 和其他地方正在进行相关工作 —— 尚未可用
• 解决技术债务
• 解决安全性和简单性的问题
• 帮助聚焦教育        Stroustrup - C++ at 40 - China 2025    54

## Page 55

超集的子集      C++     GSL     STL
• 为了取得进步
• 做一些新的事情，停止做一些旧的事情        不使用
• 简单的取子集行不通
• 我们需要低级/棘手/接近硬件/易错/专家专用的特性
• 为了高效地实现高级设施
• 许多低级特性可以用得很好
• 用少量抽象扩展语言
• 使用标准库
• 添加一个微型库 (GSL)
• 没有新的语言特性
• 可以使用混乱/危险/低级的特性来实现 GSL
• 然后取子集
   • 我们想要“增强版 C++”        语义保持不变：
• 简单，安全，灵活，且快速        结果代码是 ISO C++
• 不是一个被阉割的子集     Stroustrup - C++ at 40 - China 2025    55

## Page 56

核心规则

• 有些人无法应用所有规则
• 至少在最初阶段
• 渐进式采用是常见做法
• 许多人需要额外的规则
• 针对特定需求
• 我们最初专注于核心规则
• 那些我们希望每个人最终都能从中受益的规则
• 核心中的核心
• 无未初始化的变量
• 无范围或 nullptr 违规
• 无泄漏
• 防止悬空指针
• 无通过指针的类型违规
• 无失效
    Stroustrup - C++ at 40 - China 2025    56

## Page 57

示例：不要对指针使用下标
•   相反，使用具有足够信息进行范围检查的抽象
    • 需要运行时支持
• 常见风格        • 更好的风格
    void f(int* p, int n);                               void f(span<int> s);
    int a[100];                                          int a[100];
    // …                                                 // …
    f(a,100);     // OK? (取决于 n 的含义)                     f(span<int>{a});  // 详细
    f(a,1000); // 潜在的灾难                                  f(a);
•  “让简单的事情保持简单”                                          f({a,1000});      // 可检查
   • 比“旧风格”更简单
   • 更短
   • 至少一样快        Stroustrup - C++ at 40 - China 2025                        57

## Page 58

示例：失效
• 这必须被阻止
• 需要静态分析（例如，在编译器中）
void f(vector<int>& vi)
{    vi.push_back(9);       // 可能重新分配 vi 的元素                       参加 WG21
}                                                                  •     P3446R0
                                                                         P1179 R1
void g()
{    vector<int> vi { 1,2 };
     auto p = vi.begin();   // 指向 vi 的第一个元素
     f(vi);
}    *p = 7;                // 错误：p 已失效

                            Stroustrup - C++ at 40 - China 2025          58

## Page 59

建议纳入标准的初始规格配置集合

  • 算法规范：全面的区间检查，禁止解引用 end() 迭代器
  • 算术规范：检测上溢和下溢
  • 类型转换规范：全部禁用
  • 并发规范：消除死锁和数据竞争（难点）
  • 初始化规范：所有对象必须初始化
  • 失效规范：禁止通过已失效的指针访问（包括悬空指针）
  • 指针规范：禁止对内置指针使用下标操作（应使用 span、vector、string 等）
  • 区间规范：捕获区间错误                              没有一个会进入 C++26
  • RAII 规范：所有资源必须由句柄管理
  • 类型规范：涵盖初始化、区间、转换、失效和指针规则                 一个巨大的错误 
  • 联合体（union）规范：禁止使用 union（应使用 variant 等）   实现工作正在进行中
      Stroustrup - C++ at 40 - China 2025        59
  • 所有规范可按需启用，也可在必要时禁用

## Page 60

 C++ 模型
• 静态类型系统
 • 对内置类型和用户定义类型提供同等支持
 • 值语义和引用语义
• 系统且通用的资源管理 (RAII)
• 高效的面向对象编程
• 灵活且高效的泛型编程
• 编译期编程
• 直接使用机器和操作系统资源
• 通过库支持并发（借助内部指令）
• 最终消除 C 预处理器

     Stroustrup - C++ at 40 - China 2025    60

## Page 61

编程语言的价值
体现在应用程序的质量之中










Stroustrup - C++ at 40 - China 2025    61

## Page 62

 参考文献
• B. Stroustrup: 21st century C++ Blog@CACM January 2025
• B. Stroustrup: Concept-based Generic programming October 2025
• C++ Core Guidelines GitHub
• Profiles
    • B. Stroustrup: Safety Profiles: Type-and-resource Safe programming in ISO Standard C++
    • B. Stroustrup: Profiles syntax
    • B. Stroustrup: Profile invalidation - eliminating dangling pointers
    • Herb Sutter: Lifetime safety: Preventing common dangling
• Khalil Estell: C++ Exceptions for Smaller Firmware. CppCon 2024.
• Daniela Engert: Contemporary C++ in Action CppCon 2022.
    • A client server application for displaying video frames with timing constraints
• B. Stroustrup: A Tour of C++ (3rd Edition). Addison-Wesley. 2022.
• B. Stroustrup: Programming: Principles and Practice using C++. Addison-Wesley. 2023.
• B. Stroustrup’s HOPL papers
    • A History of C++: 1979-1991. March 1993
    • Evolving a language in and for the real world: C++ 1991-2006. June 2007
    • Thriving in a Crowded and Changing World: C++ 2006–2020. June 2020.
        Stroustrup - C++ at 40 - China 2025 62

## Related pages

- [[cpp20-features]]

## Source

- Local path: `[[slides/Bjarne_C++跨越40载的成功经验与未来演进.pdf]]`
