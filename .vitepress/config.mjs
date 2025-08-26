import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Sphinx's Notes",
  description: "技术学习笔记和总结",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: 'C/C++', link: '/notes/ccpp/' },
      { text: '网络', link: '/notes/network/' },
      { text: '操作系统', link: '/notes/os/' },
      { text: '系统编程', link: '/notes/sys/' },
      { text: '中间件', link: '/notes/midware/' },
      { text: '工具', link: '/notes/tools/' }
    ],

    sidebar: {
      '/notes/ccpp/': [
        {
          text: 'C/C++ 学习笔记',
          items: [
            { text: '概述', link: '/notes/ccpp/' },
            {
              text: 'C 语言',
              items: [
                { text: 'C 语言基础', link: '/notes/ccpp/c/c' },
                { text: '内存管理', link: '/notes/ccpp/c/memory_management' },
                { text: '内存相关', link: '/notes/ccpp/c/memory' }
              ]
            },
            {
              text: 'C++',
              items: [
                { text: 'C++ 基础', link: '/notes/ccpp/cpp/cpp' },
                { text: '对象创建', link: '/notes/ccpp/cpp/object_creation_heap_or_stack' },
                {
                  text: '容器',
                  items: [
                    { text: '容器概览', link: '/notes/ccpp/cpp/containers/containers_overview_guide' },
                    { text: 'vector', link: '/notes/ccpp/cpp/containers/vector' },
                    { text: 'array', link: '/notes/ccpp/cpp/containers/array' },
                    { text: 'list', link: '/notes/ccpp/cpp/containers/list' },
                    { text: 'deque', link: '/notes/ccpp/cpp/containers/deque' },
                    { text: 'stack', link: '/notes/ccpp/cpp/containers/stack' },
                    { text: 'map', link: '/notes/ccpp/cpp/containers/map' },
                    { text: 'unordered_map', link: '/notes/ccpp/cpp/containers/unordered_map' }
                  ]
                }
              ]
            },
            { text: '位操作', link: '/notes/ccpp/common_bit_operations' },
            { text: '编译过程', link: '/notes/ccpp/compilation_process' },
            { text: '序列化', link: '/notes/ccpp/serialization' }
          ]
        }
      ],
      '/notes/network/': [
        {
          text: '网络学习笔记',
          items: [
            { text: '概述', link: '/notes/network/' },
            {
              text: 'TCP/IP',
              items: [
                { text: 'IP 协议', link: '/notes/network/tcpip/ip' },
                { text: 'TCP 协议', link: '/notes/network/tcpip/tcp' }
              ]
            },
            {
              text: 'Linux Netfilter',
              items: [
                { text: '连接跟踪', link: '/notes/network/linux_netfilter/conntrack' },
                { text: '连接跟踪垃圾回收', link: '/notes/network/linux_netfilter/conntrack_gc' }
              ]
            }
          ]
        }
      ],
      '/notes/os/': [
        {
          text: '操作系统学习笔记',
          items: [
            { text: '概述', link: '/notes/os/' },
            { text: 'Linux 内核开发指南', link: '/notes/os/linux_kernel_development_guide' }
          ]
        }
      ],
      '/notes/sys/': [
        {
          text: '系统编程学习笔记',
          items: [
            { text: '概述', link: '/notes/sys/' },
            { text: '计算机架构介绍', link: '/notes/sys/computer_architecture_intro' },
            {
              text: '设计模式',
              items: [
                { text: '单例模式', link: '/notes/sys/design_pattern/singleton' }
              ]
            },
            {
              text: '基础',
              items: [
                { text: 'ELF 文件格式', link: '/notes/sys/fundamentals/elf' },
                { text: 'Linux 系统编程', link: '/notes/sys/fundamentals/linux_system_programming' }
              ]
            },
            {
              text: '进程间通信',
              items: [
                { text: 'Linux IPC', link: '/notes/sys/ipc/linux_ipc' },
                { text: '共享内存', link: '/notes/sys/ipc/shm/shm' },
                { text: '邮箱机制', link: '/notes/sys/ipc/mailbox/lwip_mailbox' }
              ]
            }
          ]
        }
      ],
      '/notes/midware/': [
        {
          text: '中间件学习笔记',
          items: [
            { text: '概述', link: '/notes/midware/' },
            { text: 'DoIP', link: '/notes/midware/doip' },
            {
              text: 'SOME/IP',
              items: [
                { text: 'vSOME/IP', link: '/notes/midware/someip/vsomeip' },
                { text: 'SOME/IP 安全', link: '/notes/midware/someip/security' }
              ]
            }
          ]
        }
      ],
      '/notes/tools/': [
        {
          text: '工具使用笔记',
          items: [
            { text: '概述', link: '/notes/tools/' },
            { text: 'Manjaro 交换分区', link: '/notes/tools/manjaro_swap' },
            { text: 'Netcat 使用', link: '/notes/tools/netcat' },
            { text: '移除 Snap', link: '/notes/tools/remove_snap' },
            { text: 'Vim 配置', link: '/notes/tools/vim_config.rc' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Sphinxes0o0' }
    ]
  }
})
