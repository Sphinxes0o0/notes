# 现代CPP

验证环境：
```
> clang --version
clang version 13.0.1
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/bin
```

### 被弃用的特性

- `char *`

不再允许字符串字面值常量赋值给一个 char *。
如果需要用字符串字面值常量赋值和初始化一个 char *，应该使用 const char * 或者 auto。

```bash
01.cc:10:17: warning: ISO C++11 does not allow conversion from string literal to 'char *' [-Wwritable-strings]
    char *str = "hello world";
                ^
1 warning generated.

```

#### `unexpected_handler`、`set_unexpected()` --> `noexcept`

`noexcept` 是 C++11 为了替代 `throw()` 而提出的一个新的关键字，在 C++ 中使用函数异常声明列表来查看函数可能抛出的异常。比如：
```cpp
void func() throw (int,double);
```
上例就是一个函数异常声明列表，该声明指出 func 可能抛出int和 double 类型的异常。
但是在实际编程中很少使用这种写法，所以这一特性在 C++11 中被抛弃。另外，如果异常声明列表写成如下形式：
```cpp
void func() throw();
```
这种写法表示函数 `func` 不抛出任何异常，而这种写法在 c++11 中被新的关键字 `noexcept` 异常声明所取代。

语法上 `noexcept` 修饰符有两种形式，一种就是简单地在函数声明后加上 `noexcept` 关键字。比如：
```cpp
void func() noecept;
```
另外一种形式则是接受一个常量表达式（参阅《常量表达式》）作为参数，如下所示：

```cpp
void func() noexcept(常量表达式);
```
常量表达式的结果会被转换成一个 `bool` 类型的值，该值为 `true`，表示函数不会抛出异常，
反之则可能抛出异常。而不带常量表达式的 `noexcept` 相当于声明了 noexcept(true)，即不会抛出异常。

- `auto_ptr`  --> `unique_ptr`

- `register` 关键字被弃用，可以使用但不再具备任何实际含义

- `bool` 类型的 `++` 操作被弃用

- 如果一个类有析构函数，为其生成拷贝构造函数和拷贝赋值运算符的特性被弃用了

- C 语言风格的类型转换被弃用（即在变量前使用 `(convert_type)`），应该使用 `static_cast`、`reinterpret_cast`、`const_cast `来进行类型转换。

- C++17 标准中弃用了一些可以使用的 C 标准库，例如 `<ccomplex>`、`<cstdalign>`、`<cstdbool>` 与 `<ctgmath>` 等

- `std::bind`, `std::function`, `export` 等特性也均被弃用


### 新增的特性

- `nullptr`

`nullptr` 出现的目的是为了替代 `NULL。在某种意义上来说，传统` C++ 会把 `NULL`、`0` 视为同一种东西，这取决于编译器如何定义 `NULL`，有些编译器会将 `NULL` 定义为 `((void*)0)`，有些则会直接将其定义为 `0`。

```cpp
#include <iostream>
#include <type_traits>

void foo(char *);
void foo(int);

int main() {
    if (std::is_same<decltype(NULL), decltype(0)>::value)
        std::cout << "NULL == 0" << std::endl;
    if (std::is_same<decltype(NULL), decltype((void*)0)>::value)
        std::cout << "NULL == (void *)0" << std::endl;
    if (std::is_same<decltype(NULL), std::nullptr_t>::value)
        std::cout << "NULL == nullptr" << std::endl;

    foo(0);          // 调用 foo(int)
    // foo(NULL);    // 该行不能通过编译
    foo(nullptr);    // 调用 foo(char*)
    return 0;
}

void foo(char *) {
    std::cout << "foo(char*) is called" << std::endl;
}
void foo(int i) {
    std::cout << "foo(int) is called" << std::endl;
}
```


- `constexpr`
`constexpr` 让用户显式的声明函数或对象构造函数在编译期会成为常量表达式;
从 C++14 开始，constexpr 函数可以在内部使用局部变量、循环和分支等简单语句，例如下面的代码在 C++11 的标准下是不能够通过编译的：
```cpp
constexpr int fibonacci(const int n) {
    if(n == 1) return 1;
    if(n == 2) return 1;
    return fibonacci(n-1) + fibonacci(n-2);
}
```
为此，可以写出下面这类简化的版本来使得函数从 C++11 开始即可用：
```cpp
constexpr int fibonacci(const int n) {
    return n == 1 || n == 2 ? 1 : fibonacci(n-1) + fibonacci(n-2);
}
```
C++17 将 `constexpr` 这个关键字引入到 if 语句中，允许在代码中声明常量表达式的判断条件，考虑下面的代码：
```cpp
#include <iostream>

template<typename T>
auto print_type_info(const T& t) {
    if constexpr (std::is_integral<T>::value) {
        return t + 1;
    } else {
        return t + 0.001;
    }
}
int main() {
    std::cout << print_type_info(5) << std::endl;
    std::cout << print_type_info(3.14) << std::endl;
}
```
在编译时，实际代码就会表现为如下：

```cpp
int print_type_info(const int& t) {
    return t + 1;
}
double print_type_info(const double& t) {
    return t + 0.001;
}
int main() {
    std::cout << print_type_info(5) << std::endl;
    std::cout << print_type_info(3.14) << std::endl;
}
```

- `if` / `swtich`变量声明强化

C++17 中可以在 if（或 switch）中直接声明临时变量
```cpp
// 将临时变量放到 if 语句内
if (const std::vector<int>::iterator itr = std::find(vec.begin(), vec.end(), 3);
    itr != vec.end()) {
    *itr = 4;
}
```

-  初始化列表

初始化是一个非常重要的语言特性，最常见的就是在对象进行初始化时进行使用。 
在传统 C++ 中，不同的对象有着不同的初始化方法，例如普通数组、 POD （Plain Old Data，
即没有构造、析构和虚函数的类或结构体） 类型都可以使用 {} 进行初始化，
也就是我们所说的初始化列表。 而对于类对象的初始化，要么需要通过拷贝构造、要么就需要使用 () 进行。 
这些不同方法都针对各自对象，不能通用。例如：
```cpp
#include <iostream>
#include <vector>

class Foo {
public:
    int value_a;
    int value_b;
    Foo(int a, int b) : value_a(a), value_b(b) {}
};

int main() {
    // before C++11
    int arr[3] = {1, 2, 3};
    Foo foo(1, 2);
    std::vector<int> vec = {1, 2, 3, 4, 5};

    std::cout << "arr[0]: " << arr[0] << std::endl;
    std::cout << "foo:" << foo.value_a << ", " << foo.value_b << std::endl;
    for (std::vector<int>::iterator it = vec.begin(); it != vec.end(); ++it) {
        std::cout << *it << std::endl;
    }
    return 0;
}
```
为了解决这个问题，C++11 首先把初始化列表的概念绑定到了类型上，并将其称之为 `std::initializer_list`，
允许构造函数或其他函数像参数一样使用初始化列表，这就为类对象的初始化与普通数组和 POD 的初始化方法提供了统一的桥梁，例如：
```cpp
#include <initializer_list>
#include <vector>
class MagicFoo {
public:
    std::vector<int> vec;
    MagicFoo(std::initializer_list<int> list) {
        for (std::initializer_list<int>::iterator it = list.begin();
             it != list.end(); ++it)
            vec.push_back(*it);
    }
};
int main() {
    // after C++11
    MagicFoo magicFoo = {1, 2, 3, 4, 5};

    std::cout << "magicFoo: ";
    for (std::vector<int>::iterator it = magicFoo.vec.begin(); it != magicFoo.vec.end(); ++it) std::cout << *it << std::endl;
}
```
这种构造函数被叫做初始化列表构造函数，具有这种构造函数的类型将在初始化时被特殊关照。

初始化列表除了用在对象构造上，还能将其作为普通函数的形参，例如：
```cpp
public:
    void foo(std::initializer_list<int> list) {
        for (std::initializer_list<int>::iterator it = list.begin();
            it != list.end(); ++it) vec.push_back(*it);
    }

magicFoo.foo({6,7,8,9});
```

其次，C++11 还提供了统一的语法来初始化任意的对象，例如：
```cpp
Foo foo2 {3, 4};
```

- 结构花绑定
```cpp

#include <iostream>
#include <tuple>

std::tuple<int, double, std::string> f() {
    return std::make_tuple(1, 2.3, "456");
}

int main() {
    auto [x, y, z] = f();
    std::cout << x << ", " << y << ", " << z << std::endl;
    return 0;
}
```

- `auto`
`auto` 在很早以前就已经进入了 C++，但是他始终作为一个存储类型的指示符存在，与 `register` 并存。在传统 C++ 中，如果一个变量没有声明为 `register` 变量，将自动被视为一个 `auto` 变量。而随着 `register` 被弃用（在 C++17 中作为保留关键字，以后使用，目前不具备实际意义），对 `auto` 的语义变更也就非常自然了。

使用 `auto` 进行类型推导的一个最为常见而且显著的例子就是迭代器。
```cpp
// 在 C++11 之前
// 由于 cbegin() 将返回 vector<int>::const_iterator
// 所以 itr 也应该是 vector<int>::const_iterator 类型
for(vector<int>::const_iterator it = vec.cbegin(); itr != vec.cend(); ++it)
```
而有了 auto 之后可以：
```cpp
#include <initializer_list>
#include <vector>
#include <iostream>

class MagicFoo {
public:
    std::vector<int> vec;
    MagicFoo(std::initializer_list<int> list) {
        // 从 C++11 起, 使用 auto 关键字进行类型推导
        for (auto it = list.begin(); it != list.end(); ++it) {
            vec.push_back(*it);
        }
    }
};
int main() {
    MagicFoo magicFoo = {1, 2, 3, 4, 5};
    std::cout << "magicFoo: ";
    for (auto it = magicFoo.vec.begin(); it != magicFoo.vec.end(); ++it) {
        std::cout << *it << ", ";
    }
    std::cout << std::endl;
    return 0;
}
```
一些其他的常见用法：
```cpp
auto i = 5;              // i 被推导为 int
auto arr = new auto(10); // arr 被推导为 int *
```

从 C++ 20 起，auto 甚至能用于函数传参，考虑下面的例子：
```cpp
int add(auto x, auto y) {
    return x+y;
}
auto i = 5; // 被推导为 int
auto j = 6; // 被推导为 int
std::cout << add(i, j) << std::endl;
```

- decltype

`decltype` 关键字是为了解决 `auto` 关键字只能对变量进行类型推导的缺陷而出现的。它的用法和 `typeof` 很相似：

```cpp
decltype(表达式)
```

- 尾返回类型推导

- decltype(auto)

`decltype(auto)` 是 C++14 开始提供的一个略微复杂的用法。

要理解它,需要知道 C++ 中参数转发的概念

简单来说，`decltype(auto)` 主要用于对转发函数或封装的返回类型进行推导，它使我们无需显式的指定 `decltype` 的参数表达式。考虑看下面的例子，当对下面两个函数进行封装时：

```cpp
std::string  lookup1();
std::string& lookup2();

// 在 C++11 中，封装实现是如下形式：
std::string look_up_a_string_1() {
    return lookup1();
}
std::string& look_up_a_string_2() {
    return lookup2();
}

// 而有了 decltype(auto)，我们可以让编译器完成这一件烦人的参数转发：
decltype(auto) look_up_a_string_1() {
    return lookup1();
}
decltype(auto) look_up_a_string_2() {
    return lookup2();
}
```

- for 迭代

- 外部模板

传统 C++ 中，模板只有在使用时才会被编译器实例化。换句话说，只要在每个编译单元（文件）中编译的代码中遇到了被完整定义的模板，都会实例化。这就产生了重复实例化而导致的编译时间的增加。并且，我们没有办法通知编译器不要触发模板的实例化。

为此，C++11 引入了外部模板，扩充了原来的强制编译器在特定位置实例化模板的语法，能够显式的通知编译器何时进行模板的实例化：
```cpp
template class std::vector<bool>;          // 强行实例化
extern template class std::vector<double>; // 不在该当前编译文件中实例化模板
```
- 类型模板
使用 using 引入了下面这种形式的写法，并且同时支持对传统 typedef 相同的功效：
```cpp
typedef int (*process)(void *);
using NewProcess = int(*)(void *); // <--
template<typename T>
using TrueDarkMagic = MagicType<std::vector<T>, std::string>;// <--

int main() {
    TrueDarkMagic<bool> you;
}
```

-  变长参数模板
```cpp
template<typename... Ts> class Magic;
```

1. 递归模板函数

递归是非常容易想到的一种手段，也是最经典的处理方法。这种方法不断递归地向函数传递模板参数，进而达到递归遍历所有模板参数的目的：
```cpp
#include <iostream>
template<typename T0>
void printf1(T0 value) {
    std::cout << value << std::endl;
}
template<typename T, typename... Ts>
void printf1(T value, Ts... args) {
    std::cout << value << std::endl;
    printf1(args...);
}
int main() {
    printf1(1, 2, "123", 1.1);
    return 0;
}
```

2. 变参模板展开
在 C++17 中增加了变参模板展开的支持，于是你可以在一个函数中完成 printf 的编写：
```cpp
template<typename T0, typename... T>
void printf2(T0 t0, T... t) {
    std::cout << t0 << std::endl;
    if constexpr (sizeof...(t) > 0) printf2(t...);
}
```

3. 初始化列表展开
递归模板函数是一种标准的做法，但缺点显而易见的在于必须定义一个终止递归的函数。

这里介绍一种使用初始化列表展开的黑魔法：
```cpp
template<typename T, typename... Ts>
auto printf3(T value, Ts... args) {
    std::cout << value << std::endl;
    (void) std::initializer_list<T>{([&args] {
        std::cout << args << std::endl;
    }(), value)...};
}
```
在这个代码中，额外使用了 C++11 中提供的初始化列表以及 Lambda 表达式的特性（下一节中将提到）。

通过初始化列表，`(lambda 表达式, value)... `将会被展开。由于逗号表达式的出现，首先会执行前面的 lambda 表达式，完成参数的输出。 
为了避免编译器警告，我们可以将 `std::initializer_list` 显式的转为 void。

- 折叠表达式
C++ 17 中将变长参数这种特性进一步带给了表达式，考虑下面这个例子：
```cpp
#include <iostream>
template<typename ... T>
auto sum(T ... t) {
    return (t + ...);
}
int main() {
    std::cout << sum(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) << std::endl;
}
```











