import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Sphinx's Notes",
  description: "个人整理记录的操作系统、网络、系统编程、编程语言等学习笔记和资料",
  base: '/notes/', // GitHub repository name
  
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Programming', link: '/languages/' },
      { text: 'Systems', link: '/os/' },
      { text: 'Network', link: '/network/' },
      { text: 'Tools', link: '/tools/' },
      { text: 'Courses', link: '/courses/' }
    ],

    sidebar: {
      '/languages/': [
        {
          text: '📚 Programming',
          items: [
            {
              text: 'C',
              collapsed: false,
              items: [
                { text: 'C Programming', link: '/languages/c/c' },
                { text: 'Memory Management', link: '/languages/c/memory_management' }
              ]
            },
            {
              text: 'C++',
              collapsed: false,
              items: [
                { text: 'C++ Programming', link: '/languages/cpp/cpp' },
                {
                  text: 'STL Containers',
                  collapsed: true,
                  items: [
                    { text: 'array', link: '/languages/cpp/containers/array' },
                    { text: 'vector', link: '/languages/cpp/containers/vector' },
                    { text: 'deque', link: '/languages/cpp/containers/deque' },
                    { text: 'list', link: '/languages/cpp/containers/list' },
                    { text: 'map', link: '/languages/cpp/containers/map' },
                    { text: 'stack', link: '/languages/cpp/containers/stack' },
                    { text: 'unordered_map', link: '/languages/cpp/containers/unordered_map' }
                  ]
                },
                { text: 'Object Creation', link: '/languages/cpp/object_creation_heap_or_stack' }
              ]
            },
            {
              text: 'Misc',
              collapsed: false,
              items: [
                { text: 'Bit Operations', link: '/languages/common_bit_operations' },
                { text: 'Compilation Process', link: '/languages/compilation_process' },
                { text: 'Serialization', link: '/languages/serialization' }
              ]
            }
          ]
        }
      ],
      '/os/': [
        {
          text: '🖥️ Systems & Infrastructure',
          items: [
            {
              text: 'Operating Systems',
              items: [
                {
                  text: 'Linux',
                  items: [
                    { text: 'Kernel Development Guide', link: '/os/linux_kernel_development_guide' }
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/network/': [
        {
          text: '🌐 Network',
          items: [
            {
              text: 'eBPF',
              items: [
                { text: 'eBPF Basics', link: '/network/ebpf/basic' }
              ]
            },
            {
              text: 'TCP/IP',
              items: [
                { text: 'TCP Protocol', link: '/network/tcp' },
                { text: 'UDP Protocol', link: '/network/udp' },
                { text: 'IP Protocol', link: '/network/ip' },
                { text: 'HTTP Protocol', link: '/network/http' },
                { text: 'Congestion Control', link: '/network/congestion_control' }
              ]
            },
            {
              text: 'Network Programming',
              items: [
                { text: 'epoll', link: '/network/epoll' },
                { text: 'io_uring', link: '/network/io_uring' }
              ]
            }
          ]
        }
      ],
      '/sys_programming/': [
        {
          text: '⚙️ System Programming',
          items: [
            {
              text: 'Process & Thread',
              items: [
                { text: 'Process', link: '/sys_programming/process' },
                { text: 'Thread', link: '/sys_programming/thread' },
                { text: 'IPC', link: '/sys_programming/ipc' }
              ]
            },
            {
              text: 'Memory',
              items: [
                { text: 'Memory Management', link: '/sys_programming/memory' },
                { text: 'Huge Pages', link: '/sys_programming/huge_pages' }
              ]
            },
            {
              text: 'I/O',
              items: [
                { text: 'File System', link: '/sys_programming/file_system' },
                { text: 'Disk I/O', link: '/sys_programming/disk_io' }
              ]
            }
          ]
        }
      ],
      '/tools/': [
        {
          text: '🛠️ Tools',
          items: [
            {
              text: 'Development Tools',
              items: [
                { text: 'Git', link: '/tools/git' },
                { text: 'GDB', link: '/tools/gdb' },
                { text: 'Valgrind', link: '/tools/valgrind' },
                { text: 'CMake', link: '/tools/cmake' },
                { text: 'Makefile', link: '/tools/makefile' },
                { text: 'Bazel', link: '/tools/bazel' }
              ]
            },
            {
              text: 'System Tools',
              items: [
                { text: 'perf', link: '/tools/perf' },
                { text: 'strace', link: '/tools/strace' },
                { text: 'tcpdump', link: '/tools/tcpdump' },
                { text: 'Wireshark', link: '/tools/wireshark' }
              ]
            }
          ]
        }
      ],
      '/courses/': [
        {
          text: '📖 Courses',
          items: [
            { text: 'MIT 6.828', link: '/courses/mit_6.828' },
            { text: 'CMU 15-213', link: '/courses/cmu_15-213' },
            { text: 'CS144', link: '/courses/cs144' }
          ]
        }
      ],
      '/resources/': [
        {
          text: '📦 Resources',
          items: [
            { text: 'Books', link: '/resources/books' },
            { text: 'Papers', link: '/resources/papers' },
            { text: 'Blogs', link: '/resources/blogs' },
            { text: 'Videos', link: '/resources/videos' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Sphinxes0o0/notes' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present Sphinx'
    }
  }
})