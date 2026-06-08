---
type: source
source-type: slide
title: "吴咏炜To Be or Not to Be - On Object Lifetime"
path: slides/吴咏炜To Be or Not to Be - On Object Lifetime.pdf
source-md5: 5fc588555481435c83c28cc7589cad93
size: 9931 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 吴咏炜To Be or Not to Be - On Object Lifetime

> Ingested from `slides/吴咏炜To Be or Not to Be - On Object Lifetime.pdf` via `lit parse` on 2026-06-04.
> Source file: 9.7 MB.

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

or

对象生存期和相关工具

    吴咏炜

## Page 7

To be, or not to be,—that is the question.
William Shakespeare, Hamlet, Act III, Scene i

## Page 8

一点代码


class Obj   {        Obj* ptr = (Obj*)mmap(…);
public:              ptr->init();
  Obj();             // 开始使⽤    *ptr
  ~Obj();
  void     init();
  void     cleanup();

private:
  // 数据成员
};

## Page 9

目 录 CONTENTS

    1. 存储期和生存期
    2. 临时对象的生存期
    3. 隐式生存期对象和可平凡复制对象
    4. 工具

## Page 10

_(no text content on this page)_

## Page 11

— What is the answer to Life, the Universe, and
Everything?

## Page 12

— What is the answer to Life, the Universe, and
Everything?
— 42.

## Page 13

— What is the answer to Life, the Universe, and
Everything?
— 42.
— Is 42 an object?

     *Inspired	by	Douglas	Adams,	The	Hitchhiker’s	Guide	to	the	Galaxy

## Page 14

_(no text content on this page)_

## Page 15

_(no text content on this page)_

## Page 16

存储期和生存期

存储期                      生存期
●  定义：为对象预留的内存空间所持续的     ●  定义：对象从构造完成到析构开始的这
   时间                       段时间
●  分类                    ●  生存期不会超出存储期
  •      静态（static）      ●  在生存期之外访问对象是未定义行为
  •      线程（thread）      ●  子对象的生存期
  •      自动（automatic）
  •      动态（dynamic）

## Page 17

静态存储期对象

全局变量和函数外的     static     变量     函数内的     static 变量
●  构造通常在进入 main 之前执行            ●  第一次执行到变量定义时进行构造
  •   同一翻译单元内按定义的顺序                • 并发初始化也是线程安全的
  •   不同翻译单元之间没有确定的顺序           ●  程序退出时按与构造相反的顺序析构
  •   “静态初始化顺序陷阱”               ● Meyers 单例（Meyers’ singleton）可帮助解
●  析构在 main 返回之后执行，顺序与析构相反         决静态初始化陷阱

## Page 18

Meyers     单例解决静态初始化顺序问题

/* A.h        */                         /* B.h */
class        A {                         class B   {
public:                                  public:
     static A& instance();                static B& instance();
     A(const A&) = delete;                B(const B&) = delete;
     A& operator=(const A&) = delete;     B& operator=(const B&) =   delete;
private:                                 private:
     A();                                 B();
     ~A();                                ~B();
};                                       };

/* A.cpp     */                          /* B.cpp   */
A& A::instance()                         B& B::instance()
{                                        {
     static A     a;                      static B   b;
     return a;                            return b;
}                                        }
A::A()                                   B::B()
{                                        {
     //  …                                auto&   a  = A::instance();
}                                         //      使⽤ a
                                         }

## Page 19

线程存储期对象

● 跟静态存储期对象相似，但存储期和生存期跟线程（而非程序）绑定
● 每个线程都拥有变量的一个独立副本
● 函数内的  thread_local 变量会在当前线程首次执行到定义处进行构造（跟静态存储期相似）
● 函数外的  thread_local 变量的构造时机依实现而定（GCC/Clang 的行为跟 MSVC 有区别）
● 析构函数在线程退出时被调用，顺序跟构造顺序相反

## Page 20

自动存储期对象

● 存储期和生存期紧密关联，都由编译器负责管理
● 代码执行到变量定义处（含参数声明处）进行构造，离开所在的作用域时析构
  ● 先构造的后析构
  ● 异常抛出时也会析构（stack unwinding）
● 返回局部变量的引用或指针通常是一个错误…… https://godbolt.org/z/fjG5dMPr3

## Page 21

“动态”对象

● （我的）定义：生存期由程序员手工管理的对象
● 生存期跟存储期绑定的情况
  ● ptr = new  Obj();
  ● delete ptr;
● 生存期跟存储期脱钩的情况
  ●  std::byte buffer[sizeof(Obj)]; 或 auto buffer = mmap(…);
  ● ptr =  new (buffer) Obj();
  ● ptr->~Obj();

## Page 22

    处理“动态”对象需要小心

    ● 需确保对象的内存对齐要求得到满足
● C++17 之前连 new Obj(…) 都不能确保这一点
    ● 确保调用析构函数是在存储被释放或被重用之前
    ● 确保析构函数被调用
    ● 确保析构函数只被调用一次
    ● 确保在析构之后对象不会再被访问

## Page 23

目 录 CONTENTS

    1. 存储期和生存期
    2. 临时对象的生存期
    3. 隐式生存期对象和可平凡复制对象
    4. 工具

## Page 24

什么是临时对象？

● 示例
  ●  x + x
  ●  x++（但 ++x 不是）
  ●  getObj()
●  定义：临时对象是由纯右值（prvalue）实体化（materialize）所产生的无名对象，其生存期由
   语言规则隐式管理，而非由程序员显式控制。
●  生存期结束点：在创建它的完整表达式（full-expression）结束时销毁（通常情况）

## Page 25

    完整表达式（full-expression）示例

    // 语句⼀定会结束⼀个完整表达式
    int x = 5;                          //
    x++;                                //
    x = (a++,   b++, c);                //
    func(a   + b, foo(),    x++);       // ⼀个完整表达式
    // 控制结构
    if (x > 0) { … }                    // "x > 0" 是完整表达式
for (int i = 0; i < n; ++i) { … } // 分号隔开了三个独⽴的完整表达式
// 初始化表达式
    int arr[]       = {1, 2, func()};   // "1"、"2" 和 "func()"   是三个完整表达式
    int a = f1(),       b = f2() + 3;   // "f1()" 和 "f2() + 3"  是完整表达式
    Obj::Obj() : p_(…),     d_(…) {}    // 两个初始化器是完整表达式

## Page 26

安全使用场景

// 完整表达式规则
std::string getName();                  // 假设的函数原型声明
puts(getName().c_str());                // OK：临时 string 在整个语句结束时才销毁

// 临时对象的⽣存期延⻓规则
const std::string& ref    = getName();  //    临时对象⽣存期延⻓⾄ ref 的⽣存期
std::cout << ref << std::endl;          //   OK：临时对象仍然存在

## Page 27

    不安全的使用场景

    std::string getName();   // 假设的函数原型声明
auto ptr = getName().c_str(); // 没意义的语句：指针获得后即失效
    puts(ptr);               // 错误：未定义⾏为


const char& getFirstChar(const std::string& s) { return s[0]; }
const char& c = getFirstChar(getName()); // 危险！
// 此时临时 string 已被销毁，c 是悬空引⽤

    for (auto  x : getVector()) { ... }     // OK：临时 vector ⽣存期延⻓⾄循环结束
for (auto x : getWrapper().getVec()) { ... } // C++23 前危险！Wrapper 的⽣存期未延⻓

## Page 28

那临时对象的存储期到底是哪种？

## Page 29

那临时对象的存储期到底是哪种？





CWG 365 CWG 1634

## Page 30

目 录 CONTENTS

    1. 存储期和生存期
    2. 临时对象的生存期
    3. 隐式生存期对象和可平凡复制对象
    4. 工具

## Page 31

开头的代码


class Obj   {        Obj* ptr = (Obj*)mmap(…);
public:              ptr->init();
  Obj();             // 开始使⽤    *ptr
  ~Obj();
  void     init();
  void     cleanup();

private:
  // 数据成员
};

## Page 32

开头的代码

Obj* ptr = (Obj*)mmap(…);
ptr->init();

## Page 33

    正确做法

    void* addr  =  mmap(…);
    Obj* ptr =  new (addr) Obj(); // 布置 new，在已有内存上构造对象
ptr->init(); // 如果初始化可能失败⼜不允许抛异常，init 是合理的
// 使⽤ *ptr
// 最后应当使⽤ ptr->~Obj() 来清理
//（跟 init 不同，使⽤ cleanup 成员函数基本没有意义。）

## Page 34

但某些类型不要求显式的构造

## Page 35

隐式生存期类型

●标量类型
●数组类型
●不具有用户提供析构函数的聚合类型
  ● 聚合意味着没有构造函数
●具有平凡默认构造函数和平凡析构函数的类类型
  ● 构造和析构不需要编译器生成任何代码

## Page 36

隐式生存期类型分配内存即会创建对象

## Page 37

示例

//        标量类型
auto ptr     = static_cast<int*>(malloc(sizeof(int)));
*ptr = 42;                          // 合法

// 数组类型
auto ap  =    static_cast<Obj*>(malloc(sizeof(Obj[2])));
auto ip  =    new (&ap[0]) Obj();   // 对  ap[0]    进⼀步操作
ip = new   (&ap[1]) Obj();          // 对  ap[1]    进⼀步操作

## Page 38

隐式生存期的理由

● 标量：不需要构造或析构动作
● 数组：不需要构造或析构动作（虽然其中的元素可能需要）
● 无用户析构函数的聚合类型：不需要构造或析构动作（虽然其中的元素可能需要）
● 具有平凡的构造函数和析构函数的类类型：构造或析构动作不需要执行代码

## Page 39

start_lifetime_as…（C++23）

● start_lifetime_as：明确开始隐式生存期对象的生存期
● start_lifetime_as_array：明确开始隐式生存期对象数组的生存期



alignas(float) unsigned char data[sizeof(float)]{0x00, 0x00, 0x40, 0x40};
auto& f = *start_lifetime_as<float>(data);

## Page 40

可平凡复制类型

● 至少有一个未删除的拷贝/移动构造函数或拷贝/移动赋值运算符
● 每个拷贝/移动构造函数都是平凡的或被删除的
● 每个拷贝/移动赋值运算符都是平凡的或被删除的
● 析构函数是平凡的且未删除

## Page 41

一个不具有隐式生存期的可平凡复制类


class Obj  {               protected:
public:                      int x_{};
explicit Obj(int     value)
: y_(value)        {}      private:
int getX()      const        int y_;
{ return x_;    }          };
int getY()      const
{ return y_;    }              https://godbolt.org/z/e7cq1M7ax

## Page 42

    对象创建示例

    // 使⽤ memcpy 创建对象
unsigned char data[sizeof(float)]{0x00, 0x00, 0x40, 0x40};
alignas(float) unsigned char g[sizeof(float)];
memcpy(&g, data, sizeof(float));
auto& f = *reinterpret_cast<float*>(g);
// 使⽤ memcpy 修改对象
unsigned char data[sizeof(float)]{0x00, 0x00, 0x40, 0x40};
float f;
memcpy(&f, data, sizeof(float));
// 使⽤ bit_cast 创建对象（C++20）
unsigned char data[sizeof(float)]{0x00, 0x00, 0x40, 0x40};
auto f = bit_cast<float>(data);

## Page 43

    C++20   之前的手工 bit_cast

template <class To, class From>
enable_if_t<sizeof(To) == sizeof(From) &&
        is_trivially_copyable_v<From> &&
        is_trivially_copyable_v<To>,
        To>
bit_cast(const From& src) noexcept
{
    static_assert(is_trivially_constructible_v<To>,
        "This implementation additionally requires destination "
        "type to be trivially constructible");
    To dst;
    memcpy(&dst, &src, sizeof(To));
     return dst;
    }

## Page 44

代码的问题


class Obj   {            Obj* ptr = (Obj*)mmap(…);
public:                  ptr->init();
  Obj();                 // 开始使⽤    *ptr
  ~Obj();
  void     init();
  void     cleanup();    不是隐式生
private:                 存期对象
  // 数据成员
};

## Page 45

“这些只是理论问题！”

## Page 46

   也许……不过

● 如果数据成员中有任何一个不是可平凡默认构造或可平凡析构，问题就会出现。
● 编译器将来可能针对生存期做出优化。
● 不产生未定义行为是 C++ 程序员的基本美德和责任。

## Page 47

严格别名规则

● 不能用指针访问不兼容类型的对象


int  foo(int*  p1, float* p2)     int n = 0;
{                                 printf("%x\n", foo(&n, (float*)&n));
     *p1  =  1;
     *p2  =  3.0;
     return  *p1;
}

## Page 48

目 录 CONTENTS

    1. 存储期和生存期
    2. 临时对象的生存期
    3. 隐式生存期对象和可平凡复制对象
    4. 工具

## Page 49

编译器告警

●  建议选项： -Wall -Wextra     –Werror
●  考虑日常使用最新版本的编译器来调试和单元测试（即使生产环境使用统一的较老版本）
●  使用 Clang（即使生产环境使用 GCC）

   const char* get_string()       <source>:6:12: warning: address of stack
   {                              memory associated with  local variable 's'
        string s{"Hello"};        returned [-Wreturn-stack-address]
        return s.c_str();         6      return s.c_str();
   }                                 |        ^
                                      https://godbolt.org/z/9qoGfP863

## Page 50

Clang-Tidy

● 静态分析工具，支持多项生存期相关的检查：
  ● bugprone-dangling-handle：检测可能的悬空句柄（如 string_view）
  ● bugprone-use-after-move：检测移动后使用的问题
  ● clang-analyzer-core.StackAddressEscape：检测栈地址逃逸
  ● cppcoreguidelines-owning-memory：检测所有权管理问题
  ● cppcoreguidelines-pro-* 系列：多个与指针安全相关的检查
● 建议在 CI/CD       中进行集成

## Page 51

      （ASan）
AddressSanitizer

● 运行时检测工具，用于发现内存错误，如：
  ● 使用已释放的内存
  ● 堆缓冲区溢出
  ● 栈缓冲区溢出
  ● 使用已返回的栈内存
  ● 使用已离开作用域的栈变量
● 需要在构建时启用（-fsanitize=address）
● 建议在开发和测试阶段使用（有性能开销，不适合生产环境）

## Page 52

    Valgrind

● 动态分析工具，用于发现内存和线程错误。MemCheck 工具可检测：
  ● 非法读写
  ● 使用未初始化的值
  ● 内存泄漏
  ● 错误的内存释放动作
● 无需重新构建，但性能开销巨大（数十倍）
● 支持平台种类不如 ASan

## Page 53

其他辅助工具

● clangd
  ● C/C++/Objective-C      语言服务器
  ● 可识别        Clang-Tidy  配置文件，在编辑时执行轻量级的静态检查
  ●    支持  Visual Studio   Code、Vim、Emacs 等环境
● cppsafe
  ●    基于  LLVM/Clang 的生存期检查工具，使用 lifetime safety profile（生存期安全规格配置）
● MemorySanitizer（MSan）
  ● 专门检测对未初始化内存的读取
  ● 仅支持    Linux Clang

## Page 54

   工具最佳实践

● 开发阶段：使用高告警级别编译，配合 clangd 进行实时检查
● 测试阶段：在 CI 中运行 Clang-Tidy，并在运行单元测试和集成测试时启用 ASan
● 调试阶段：按需使用 Valgrind 或 ASan 诊断问题
● 代码审查：关注涉及裸指针、引用返回、临时对象的代码

## Page 55

To be, or not to be. . . .

## Page 56

https://github.com/adah1972/cpp_summit_2025

## Page 57

THANKS

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/吴咏炜To Be or Not to Be - On Object Lifetime.pdf]]`
