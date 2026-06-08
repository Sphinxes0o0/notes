---
type: source
source-type: slide
title: "董俊杰_C++语言在Xiaomi Vela中的应用、体验及前景"
path: slides/董俊杰_C++语言在Xiaomi Vela中的应用、体验及前景.pdf
source-md5: b405f11db109e94ebe37f953dc8d56bb
size: 6480 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# 董俊杰_C++语言在Xiaomi Vela中的应用、体验及前景

> Ingested from `slides/董俊杰_C++语言在Xiaomi Vela中的应用、体验及前景.pdf` via `lit parse` on 2026-06-04.
> Source file: 6.33 MB.

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

    C++语言在Xiaomi Vela中的应
    用

     分享人：
Xiaomi Vela董俊杰

## Page 7

RPC  Android
Vela  Windows
    Linux
Vela FrameworkKernel    融合系统    Vela Safety OS
Kernel     T标准系统     Vela Hybrid OS  功能安全系统
    IO        S

    轻量操作系统

## Page 8

Xiaomi Vela系统架构图

## Page 9

讲点什么？




 没有高大上的

 讲点一听就懂的，听懂就能用的

 都是日常中常见的，容易忽略的东西

## Page 10

第 一 P  P T










第 一 P  P T










第    一    P    P    T

## Page 11

01 C++ In Xiaomi Vela

## Page 12

   C++在Vela中的核心定位




       系统模块
核心开发语言              提供核心基础库 应用层主要开发语言

       通信中间件     •   Base库：消息循环、
       应用框架          线程管理、时间管理、 音视频管理
   •   服务框架          WeakPtr、 应用服务
                     LazyInstance等 • 系统应用能力扩展
                 •   重要组件封装：JS引
                     擎封装、图形库封装
                     等

## Page 13

C++在Vela中的使用细节——支持版本及库

        需要关闭RTTI和EXCEPTION， 可以使用STL，
        可以减少运行时的开销 以及基于STL的开源软件，
        谨慎使用boost


  基于clang的版本，
目前可以支持C++17/20。    可以支持多种STL库
 不过由于鉴于不同设备需求，
    不宜升的过高。

## Page 14

   C++在Xiaomi Vela中的使用挑战

                        对codesize要求非常高，（可以
 RTOS flat模式下，全局变量和     通过宏控制代码的codesize大小；
 静态变量的构造和析构与linux       编译选项 –os –lto链接优化）
 不同，某些情况存在一次构造、
 多次析构问题






TLS本地变量的使用，鉴于
Nuttx内核的使用不同Slot不同                      个别STL接口支持不全，
（默认8个），过多使用可能存                          (如
在问题 std::thread_local变量不能               filesystem 中删除文件等接
使用，另外TLS也存在内存泄漏     小有瑕疵，但是99%以上运行无障碍   口支持不全）
等问题。

## Page 15

02C++：改进模块化设
       计

## Page 16

    避免让代码变成混乱的毛线团


 导入       常见大力出奇迹，风格以刚猛为主，
 常见误区
 具体示例
&&解决方案    缺乏优雅精巧的设计方案；
        日复一日的代码累积，代码飞线成混乱的毛线团；

## Page 17

    常见误区



  导入

  常见误区

 具体示例
&&解决方案

   模块                 接口               类内
  交叉引用                设计不合理           无关内容多
      模块A引用B的内容，     因需求/实现设置接口，    一个类里面放入太多
      B引用A的内容        不考虑其合理性和必要     无关内容
                     性

## Page 18

   示例1：交叉引用是万恶之源





  导入

 常见误区
 具体示例
&&经验分享







   问题剖析




   这种情况我称为 依赖外溢。

## Page 19

    解决经验1：分层设计




   导入

  常见误区
  具体示例
 &&经验分享






解决经验：分层设计
 上层依赖下层，
下层不能依赖上层

## Page 20

   经验2：Delegate/Client解决反向依赖



   导入

 常见误区
 具体示例
&&解决方案





   解决经验：Delegate/Client

   通过Delegate，将底层依赖做成接口，通过继承方法
   来解决反向依赖的问题

## Page 21

        经验3：避免因实现/需求定接口

        IApplication
  导入

 常见误区
 具体示例    Application
&&解决方案

接口是模块对外的郑重承诺，
   不可随意对待
        问题剖析           解决经验
   一个接口只有一个实现时，        果断删除接口，只对外提供API
    最容易出现这种状况：         严格按照API规则管理对外接口，
    后续的维护者容易的因为        对添加接口的必要性进行评估
将Application加一个功能，
再给IApplication添加接口     从模块中拆分非核心逻辑，保证
                       模块的灵活性

## Page 22

   经验3：用Inner实现代替接口继承


  导入     可以编写一个Inner类，负责具体实现，对
         外开放外部接口：
 常见误区    1.  达到隐藏内部实现细节；
 具体示例    2.  防止接口被继承和替换
&&解决方案   3.  不用额外的创建接口，可以直接使用









             代码来自V8

## Page 23

    经验4：避免超级类存在，化整为零，分割功能



  导入

 常见误区
 具体示例
&&解决方案




        代码来自flutter

     将一个大功能拆分成若干类，每个类完成一个任务。
    每个类都是独立的，对外依赖全部通过抽象接口隔离。
通过大的Shell/Manager程序将其合并在一起（中间者模式）

## Page 24

经验4：避免超级类的存在，化整为零，分割功能

以快应用的安装程序为例，原来安装程序大约1700行代码，放在一
  导入 个文件中，我们将其拆解为10+文件，并合理安排他们的关系
 常见误区
 具体示例
&&解决方案

## Page 25

             总结：做好设计的真正难题

  导入      1.  解决好模块问题，要从一个类、一个函数做
 常见误区         起；
 具体示例     2.  谨防代码维护和演进过程中的代码变味：
&&解决方案
             1.  平常加强对团队的教育；
             2.  代码Review要到位；
             3.  时常发起微重构，不断清理代码

## Page 26

03 C++安全简单讨论

## Page 27

智能指针的安全性


       主要包括两种：
      * unique_ptr 独享指针
      * shared_ptr 共享指针 （指针计数线程安全，指针所指向
智能指针   的内容不安全）


* 异步编程中对象管理难题
* 循环引用
* 裸指针的生命周期完全不可控    安全挑战

## Page 28

跨线程指针安全性:MessageLoop & TaskRunner










大家想想，this指针会发生什么事情？    代码来自flutter

## Page 29

异步调用安全性










通过延长生命周期，或者延长生命周期的引用
来防止指针悬空。
思考：如果需要跨线程访问，哪些是不安全的？
注意：必须通过make_shared来创建对象

## Page 30

    对指针深度思考


   std::shared_ptr / std::weak_ptr 可以组成强弱引用，可以做到多线程安全。
 • std::unique_ptr 没有类似的weak_ptr可以使用，虽然可以模拟一个，但是线程
   安全是保障不了的。

来自flutter引擎的WeakPtrFactory/WeakPtr的逻辑
       •   weak_ptr无法阻止unique_ptr删除对
           象，从而无法安全的获取到对象。
       •   这个用法只能是同线程安全 对象 对象ptr
flag
    •     Rust的 Rc/Arc/Box/Weak + Sync/Send标
          记 较好的解决了该问题； weak_ptr
    •     C++对跨线程语义缺乏标记和约束， 只 unique_ptr
          能依靠程序员的经验和细心。
Flutter中，增加了一个ThreadCheck，保障同线程安全

## Page 31

04 C++封装C接口

## Page 32

为了ABI兼容，C++通常要封装为C API



需要二进制集成软件时，需要将C++接口转为C接口。
1）不同C++编译器对类的内存布局不完全一致；2）不同版本和实现的STL存在差异，会造成二级制不兼容；3）C++的mangling机制可能不相同



对于C++类，封装成Handle 透明指针，提供Create/Destroy方法，并对类函数进行封装，完全隔离C++代码。



对于纯虚抽象类，需要用C Struct组成的回调函数，让外部开发者来实现其接口


对于std::function一类的函数对象，需要做成callback + userdata指针的模式，允许用户传递带有上下文的
接口

## Page 33

封装C++类为C API （以Android API为例）

        定义结构体但不定义具体内容，只能以指针的形式使用；
        可防止编译器随意和void*转换指针。（C编译器会给warning）



    将C++类用 <类名>_<函数名> 方式封装。



    思考问题：
    1. 函数命命名方式采用什么合适？
    2. 类对象的生命周期，希望如何管理？
    3. 希望把类的所有接口都暴露吗？

## Page 34

    使用C为C++提供抽象接口





   这里我们模拟了C++纯虚类，定义了
   一个C版本的Vtable。
   实际上，大多数纯虚类的Vtable表的
   第一项就是析构函数。



这里，我们并没有明确，将QuickAppClient指针，是独占方式还是共享方式交给使用者的。具体方式取
决于具体业务。
以独占方式交接的话， free接口应该直接释放资源；
如果以共享方式交接的话，free接口相当于释放引用计数。
通常以独占方式交接，多线程情况下不会发生竞态；如果以共享方式，至少引用计数需要保证原子化。
结论：少用C，多用C++。

## Page 35

相对std::function, C回调容易忽略User Data的释放

        该Android NDK的API，没有说明 data 如何释放，何时释放的问题。
        实际上，开发者需要考虑移除callback后再释放 data。
        如果程序非正常退出，或者遗忘了，很容易造成内存泄漏问题。


    很多场合下（如单次回调），不能确保回调一定被调
    用，也不能确保 user_data一定被释放。
    此时，调用者需确保给回调者释放user_data的机会



  思考： Callback的Free动作发生在哪个线程？
  答案是取决于Callback的调用者。它可能发生在任意线程。
  如果，你希望Callback发生在你指定的线程，该如何处理？这只能由Callback的实现者自己做线程间通讯了。

## Page 36

05 如何写出好的C++代码

## Page 37

C++在Vela中的代码风格的一些感想



工具优于规范：使用现成的代码风格规范，如Webkit, Google, Chromium, 优先使用clang-format工具；
风格至少局部统一：每个人的编码习惯不一样，不要试图统一系统内所有风格，但是至少要保证一个模块一个风格；




好的代码应该让人望文生义，即让人看到后，就能明白你的意图。
代码应简单、直白；既要做模块抽象，也需要保持克制。



文件命名最好和内容对应，就像java语言那样，能让人通过文件名能大体了解文件的内容；
要警惕不要include太多的头文件。Include的越多，说明你的模块依赖越严重。



多看一些优秀开源软件的代码，有助于能力提升；
可以有一些代码审美。干净、整洁的代码，犹如一个人穿着朴素，但是非常干净整洁；


推荐看一看https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines

## Page 38

写好C++，也是一种修行



内存！内存！
尽量使用C++的智能指针：实践证明，内存泄漏或者崩溃问题往往来自裸指针，很少出现在智能指针中；



保持代码无异味：
时常对代码进行微重构，不断的改进和规范代码；


能够复用的尽量复用：
如果代码中存在两处非常相似的逻辑，应该将它提取出来，做成公共的模块；
一个常见的错误，喜欢到处加宏，将代码搞得支离破碎。

不追求银弹，保持克制，架构设计做到刚刚好：
1. 不为未来不确定的需求买单，不追求一次性解决所有问题；
2. 搞清楚模块的边界，一个模块解决一个问题；

身似菩提树，心如明镜台，时时勤拂拭，     莫使惹尘埃。

## Page 39

06 C++未来之我见

## Page 40

C++新标准中看好的功能



    协程               模块

C++20标准中的协程及其关联
库，在目前的异步编程中非常        C++20标准中的模块，提供了
有用。                  一种比include更好的导入导出
但是相对Rust来说，C++的协     的机制。编译速度更快，封
程还缺失一个类似Tokio这样的     装的更加完整。
广泛使用的协程库，是目前很
大的障碍。

## Page 41

C++未来发展的一些思考




安全？        简单？

内存安全与线程安全，是      让缺乏经验的程序员更加
两个很难解决的问题。       容易的写出安全、高效的
1) 缺乏足够的意识；    C++代码？
2) 缺乏通用的方案；    1.  包管理、编译管理？
3) 缺乏强制的约束。    2.  好的库，很重要；

## Page 42

C++是我见过最古老又最年轻的语言，也是一个值得我学习和追随一生的语言。

Thank You!

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/董俊杰_C++语言在Xiaomi Vela中的应用、体验及前景.pdf]]`
