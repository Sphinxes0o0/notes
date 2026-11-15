export default [
  {
    text: 'C/C++ 学习笔记',
    items: [
      { text: '概述', link: '/ccpp/' },
      {
        text: 'C 语言',
        items: [
          { text: 'C 语言基础', link: '/ccpp/c/c' },
          { text: '内存管理', link: '/ccpp/c/memory_management' }
        ]
      },
      {
        text: 'C++',
        items: [
          { text: 'C++ 基础', link: '/ccpp/cpp/cpp' },
          { text: '对象创建', link: '/ccpp/cpp/object_creation_heap_or_stack' },
          {
            text: '容器',
            collapsed: true,
            items: [
              { text: '容器概览', link: '/ccpp/cpp/containers/overview' },
              { text: 'vector', link: '/ccpp/cpp/containers/vector' },
              { text: 'array', link: '/ccpp/cpp/containers/array' },
              { text: 'list', link: '/ccpp/cpp/containers/list' },
              { text: 'deque', link: '/ccpp/cpp/containers/deque' },
              { text: 'stack', link: '/ccpp/cpp/containers/stack' },
              { text: 'map', link: '/ccpp/cpp/containers/map' },
              { text: 'unordered_map', link: '/ccpp/cpp/containers/unordered_map' }
            ]
          },
          {
            text: 'C++23/26 新特性',
            collapsed: true,
            items: [
              { text: 'std::expected 错误处理', link: '/ccpp/cpp/cpp23/expected_error_handling' },
              { text: 'C++20 协程 + C++26 sender/receiver 异步 I/O', link: '/ccpp/concurrency/cpp20_26_async_io' }
            ]
          }
        ]
      },
      {
        text: 'Rust',
        collapsed: true,
        items: [
          { text: 'Async / Tokio 实战指南', link: '/ccpp/rust/async_tokio_guide' }
        ]
      },
      { text: '位操作', link: '/ccpp/common_bit_operations' },
      { text: '编译过程', link: '/ccpp/compilation_process' },
      { text: '序列化', link: '/ccpp/serialization' },
      {
        text: 'C++ 高级主题',
        collapsed: true,
        items: [
          { text: '原子操作与内存序', link: '/ccpp/cpp/atomic' },
          { text: '智能指针', link: '/ccpp/cpp/smart_pointers' },
          { text: '虚函数原理', link: '/ccpp/cpp/virtual_functions' },
          { text: 'RAII 资源管理', link: '/ccpp/cpp/raii' },
          { text: '类型转换', link: '/ccpp/cpp/type_casting' },
          { text: '拷贝语义', link: '/ccpp/cpp/copy_semantics' },
          { text: '现代 C++（移动语义 / 完美转发）', link: '/ccpp/cpp/cpp_modern' },
          { text: '内存池设计', link: '/ccpp/cpp/memory_pool' },
          { text: 'abseil-hints', collapsed: true, items: [
{ text: '概述与目录', link: '/ccpp/cpp/abseil-hints' },
{ text: "The importance of thinking about performance", link: '/ccpp/cpp/abseil-hints/01-sections' },
{ text: "Algorithmic improvements", link: '/ccpp/cpp/abseil-hints/02-sections' },
{ text: "Bit vectors instead of sets", link: '/ccpp/cpp/abseil-hints/03-sections' },
{ text: "Avoid unnecessary work", link: '/ccpp/cpp/abseil-hints/04-sections' },
{ text: "Precompute expensive information once", link: '/ccpp/cpp/abseil-hints/05-sections' },
{ text: "Use caching to avoid repeated work", link: '/ccpp/cpp/abseil-hints/06-sections' },
{ text: "Avoid logging on hot code paths", link: '/ccpp/cpp/abseil-hints/07-sections' },
{ text: "Reduce template instantiations", link: '/ccpp/cpp/abseil-hints/08-sections' },
{ text: "SIMD Instructions", link: '/ccpp/cpp/abseil-hints/09-sections' },
{ text: "absl::btree_map/absl::btree_set", link: '/ccpp/cpp/abseil-hints/10-sections' },
{ text: "Bulk operations", link: '/ccpp/cpp/abseil-hints/11-sections' },
{ text: "Suggested citation", link: '/ccpp/cpp/abseil-hints/12-sections' }
] }
        ]
      },
      {
        text: 'C++ 并发',
        collapsed: true,
        items: [
          { text: 'C++20 协程 + C++26 sender/receiver 异步 I/O', link: '/ccpp/concurrency/cpp20_26_async_io' },
          { text: 'future / promise / shared_future / async（源码示例）', link: '/ccpp/concurrency/future' },
          { text: 'memory_order 演示（源码示例）', link: '/ccpp/concurrency/memory_order' },
          { text: 'MPMC ring buffer（源码示例）', link: '/ccpp/concurrency/mpmc_ringbuffer' },
          { text: '多线程 atexit（源码示例）', link: '/ccpp/concurrency/multithreads' },
          { text: 'std::this_thread::yield（源码示例）', link: '/ccpp/concurrency/yield' }
        ]
      },
      {
        text: 'CodeWars 刷题笔记',
        collapsed: true,
        items: [
          { text: 'C - Even or Odd', link: '/ccpp/codewar_notes/c/EvenorOdd' },
          { text: 'C - Rock Paper Scissors', link: '/ccpp/codewar_notes/c/RockPaperScissors' },
          { text: 'C++ - 240401', link: '/ccpp/codewar_notes/cpp/240401' },
          { text: 'C++ - 轮转数组', link: '/ccpp/codewar_notes/cpp/rotate_array' }
        ]
      },
      { text: 'Agent Memory 专题 ↗', link: '/coding_agent/hermes_memory_design' }
    ]
  }
]
