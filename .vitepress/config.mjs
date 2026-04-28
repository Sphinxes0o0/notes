import { defineConfig } from 'vitepress'
import { VitePWA } from 'vite-plugin-pwa'
import { sitemapPlugin } from '@vuepress/plugin-sitemap'
import { readingTimePlugin } from './plugins/readingTime.mjs'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  plugins: [
    readingTimePlugin(),
    sitemapPlugin({
      hostname: 'https://Sphinxes0o0.github.io/notes',
      lastmodDateOnly: true
    })
  ],

  title: "Sphinx's Notes",
  description: "技术学习笔记和总结",

  // Content source directory
  srcDir: '.',

  // Clean URLs without .html
  cleanUrls: true,

  // Show last updated timestamp
  lastUpdated: true,

  // Smooth scroll navigation
  smoothScroll: true,

  // Exclude courses and wiki directories from VitePress processing
  srcExclude: ['courses/**', 'wiki/**', 'misc/**'],

  // Ignore dead links for excluded content
  ignoreDeadLinks: true,

  // Markdown configuration
  markdown: {
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    },
    lineNumbers: true,
    container: {
      tipLabel: '💡 提示',
      warningLabel: '⚠️ 注意',
      dangerLabel: '🚨 危险',
      infoLabel: 'ℹ️ 信息',
      detailsLabel: '详情'
    },
    // Gracefully handle unrecognized languages
    ignoreMissing: ['dts', 'haproxy', 'snort', 'conf', 'pam', 'file_api/file_config.h']
  },

  // PWA configuration
  pwa: {
    base: '/',
    includeAssets: ['favicon.ico', 'robots.txt'],
    manifest: {
      name: "Sphinx's Notes",
      short_name: 'Sphinx笔记',
      description: '技术学习笔记和总结',
      theme_color: '#3c8772',
      background_color: '#ffffff',
      display: 'standalone',
      icons: [
        {
          src: '/pwa-192x192.svg',
          sizes: '192x192',
          type: 'image/svg+xml'
        },
        {
          src: '/pwa-512x512.svg',
          sizes: '512x512',
          type: 'image/svg+xml'
        }
      ]
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-cache',
            expiration: {
              maxEntries: 10,
              maxAgeSeconds: 60 * 60 * 24 * 365
            },
            cacheableResponse: {
              statuses: [0, 200]
            }
          }
        },
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'gstatic-fonts-cache',
            expiration: {
              maxEntries: 10,
              maxAgeSeconds: 60 * 60 * 24 * 365
            },
            cacheableResponse: {
              statuses: [0, 200]
            }
          }
        }
      ]
    }
  },

  // Sitemap
  sitemap: {
    hostname: 'https://Sphinxes0o0.github.io/notes',
    lastmodDateOnly: false
  },

  // Head meta tags for SEO
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#3c8772' }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:title', content: "Sphinx's Notes" }],
    ['meta', { name: 'og:description', content: '技术学习笔记和总结' }],
    ['meta', { name: 'author', content: 'Sphinx' }],
    ['meta', { name: 'robots', content: 'index, follow' }]
  ],

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config

    // Search configuration (local search)
    search: {
      provider: 'local',
      options: {
        detailedView: true
      }
    },

    // Outline (table of contents)
    outline: {
      level: [2, 3],
      label: '目录'
    },

    // Edit link - allow users to edit page on GitHub
    editLink: {
      pattern: 'https://github.com/Sphinxes0o0/notes/edit/main/:path',
      text: '在 GitHub 上编辑此页'
    },

    // Doc footer (prev/next navigation)
    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    // Social links
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Sphinxes0o0' }
    ],

    // Footer
    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2024-present Sphinx'
    },

    // Last updated text
    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'short'
      }
    },

    // Nav
    nav: [
      { text: '首页', link: '/' },
      { text: 'C/C++', link: '/ccpp/' },
      { text: '系统', link: '/sys/' },
      { text: '内核', link: '/kernel/' },
      { text: '网络/协议', link: '/network/' },
      { text: '安全', link: '/security/' },
      { text: '工具', link: '/tools/' },
      {
        text: '课程',
        items: [
          { text: '数据结构', link: '/datastructure/' },
          { text: '设计模式', link: '/design_patterns/' },
          { text: '网络基础', link: '/network_fundamentals/' },
          { text: '操作系统基础', link: '/os_fundamentals/' }
        ]
      },
      { text: 'QEMU', link: '/qemu/' }
    ],

    sidebar: {
      '/ccpp/': [
        {
          text: 'C/C++ 学习笔记',
          items: [
            { text: '概述', link: '/ccpp/' },
            {
              text: 'C 语言',
              items: [
                { text: 'C 语言基础', link: '/ccpp/c/c' },
                { text: '内存管理', link: '/ccpp/c/memory_management' },
                { text: '内存相关', link: '/ccpp/c/memory' }
              ]
            },
            {
              text: 'C++',
              items: [
                { text: 'C++ 基础', link: '/ccpp/cpp/cpp' },
                { text: '对象创建', link: '/ccpp/cpp/object_creation_heap_or_stack' },
                {
                  text: '容器',
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
                }
              ]
            },
            { text: '位操作', link: '/ccpp/common_bit_operations' },
            { text: '编译过程', link: '/ccpp/compilation_process' },
            { text: '序列化', link: '/ccpp/serialization' }
          ]
        }
      ],
      '/sys/': [
        {
          text: '系统',
          items: [
            {
              text: '操作系统',
              items: [
                { text: '概述', link: '/os/' },
                { text: 'Linux 内核开发指南', link: '/os/linux_kernel_development_guide' },
                { text: 'Linux 101', link: '/os/linux_101' },
                {
                  text: '内核深度分析',
                  items: [
                    { text: '调度器', link: '/os/scheduler_deep_dive' },
                    { text: '内存管理/SLUB', link: '/os/slub_allocator_deep_dive' },
                    { text: '虚拟文件系统/VFS', link: '/os/vfs_deep_dive' },
                    { text: '块 I/O', link: '/os/block_io_deep_dive' },
                    { text: '同步机制', link: '/os/synchronization_deep_dive' },
                    { text: '时间管理', link: '/os/timekeeping_deep_dive' },
                    { text: 'Cgroups', link: '/os/cgroups_deep_dive' }
                  ]
                }
              ]
            },
            {
              text: '系统编程',
              items: [
                { text: '概述', link: '/sys/' },
                                { text: 'ELF 文件格式', link: '/sys/fundamentals/elf' },
                { text: 'Linux 系统编程', link: '/sys/fundamentals/linux_system_programming' },
                { text: 'TTY / Shell / Console', link: '/sys/tty_shell_console' }
              ]
            },
            {
              text: '设计模式',
              items: [
                { text: '单例模式', link: '/sys/design_pattern/singleton' }
              ]
            },
            {
              text: '进程间通信',
              items: [
                { text: 'Linux IPC', link: '/sys/ipc/linux_ipc' },
                { text: '共享内存', link: '/sys/ipc/shm/shm' },
                { text: '邮箱机制', link: '/sys/ipc/mailbox/lwip_mailbox' }
              ]
            }
          ]
        }
      ],
      '/network/': [
        {
          text: '网络/协议',
          items: [
            {
              text: '网络',
              items: [
                { text: '概述', link: '/network/' },
                { text: '网络栈深度分析', link: '/network/network_stack_deep_dive' },
                {
                  text: 'TCP/IP',
                  items: [
                    { text: 'IP 协议', link: '/network/tcpip/ip' },
                    { text: 'TCP 协议', link: '/network/tcpip/tcp' },
                    { text: 'TCP/IP 子系统', link: '/network/tcpip/net_subsystem_tcpip' },
                    { text: '拥塞控制', link: '/network/tcpip/net_subsystem_congestion' }
                  ]
                },
                {
                  text: 'Linux Netfilter',
                  items: [
                    { text: 'Netfilter 子系统', link: '/network/linux_netfilter/net_subsystem_netfilter' },
                    { text: 'Netfilter TCP 深度分析', link: '/network/linux_netfilter/netfilter_tcp_deep_dive' },
                    { text: '连接跟踪', link: '/network/linux_netfilter/conntrack' },
                    { text: '连接跟踪垃圾回收', link: '/network/linux_netfilter/conntrack_gc' },
                    { text: 'nftables', link: '/network/linux_netfilter/nftables' }
                  ]
                },
                {
                  text: '网络核心',
                  items: [
                    { text: 'Socket 子系统', link: '/network/core/net_subsystem_socket' },
                    { text: '连接跟踪', link: '/network/core/net_subsystem_conntrack' },
                    { text: '路由', link: '/network/core/net_subsystem_routing' }
                  ]
                },
                {
                  text: '网络性能',
                  items: [
                    { text: '内核技巧', link: '/network/performance/net_subsystem_kernel_tricks' },
                    { text: '热路径', link: '/network/performance/net_subsystem_hotpath' },
                    { text: '高级特性', link: '/network/performance/net_subsystem_advanced' },
                    { text: '定时器', link: '/network/performance/net_subsystem_timers' }
                  ]
                },
                {
                  text: '协议',
                  items: [
                    { text: 'BPF Hooks', link: '/network/protocols/net_subsystem_bpf_hooks' },
                    { text: 'Netlink', link: '/network/protocols/net_subsystem_netlink' },
                    { text: 'RFC 实现', link: '/network/rfc/net_subsystem_rfc_impl' }
                  ]
                }
              ]
            },
            {
              text: '中间件',
              items: [
                { text: '概述', link: '/midware/' },
                { text: 'DoIP', link: '/midware/doip' },
                {
                  text: 'SOME/IP',
                  items: [
                    { text: 'vSOME/IP', link: '/midware/someip/vsomeip' },
                    { text: 'SOME/IP 安全', link: '/midware/someip/security' }
                  ]
                }
              ]
            }
          ]
        }
      ],
      '/security/': [
        {
          text: '安全工具笔记',
          items: [
            { text: '概述', link: '/security/' },
            {
              text: '网络扫描',
              items: [
                { text: '架构分析', link: '/security/masscan/ARCHITECTURE' },
                { text: '报文特征与识别', link: '/security/masscan/PACKET_FEATURES' },
                { text: '检测方法与引擎', link: '/security/masscan/DETECTION' }
              ]
            },
            {
              text: '安全监控',
              items: [
                { text: 'Falco', link: '/security/falco/ARCHITECTURE' }
              ]
            },
            {
              text: '入侵检测',
              items: [
                { text: 'Snort 3 架构分析', link: '/security/nids/snort3_architecture_analysis' }
              ]
            }
          ]
        }
      ],
      '/tools/': [
        {
          text: '工具使用笔记',
          items: [
            { text: '概述', link: '/tools/' },
            { text: 'Manjaro 交换分区', link: '/tools/manjaro_swap' },
            { text: 'Netcat 使用', link: '/tools/netcat' },
            { text: '端口扫描器', link: '/tools/port_scanner' },
            { text: '移除 Snap', link: '/tools/remove_snap' },
                      ]
        }
      ],
      '/datastructure/': [
        {
          text: '数据结构',
          items: [
            { text: '概述', link: '/datastructure/' },
            { text: '01_复杂度', link: '/datastructure/01_复杂度_如何衡量程序运行的效率' },
            { text: '02_数据结构', link: '/datastructure/02_数据结构_将昂贵的时间复杂度转换成廉价的空间复杂度' },
            { text: '03_增删查', link: '/datastructure/03_增删查_掌握数据处理的基本操作_以不变应万变' },
            { text: '04_线性表', link: '/datastructure/04_如何完成线性表结构下的增删查' },
            { text: '05_栈', link: '/datastructure/05_栈_后进先出的线性表_如何实现增删查' },
            { text: '06_队列', link: '/datastructure/06_队列_先进先出的线性表_如何实现增删查' },
            { text: '07_数组', link: '/datastructure/07_数组_如何实现基于索引的查找' },
            { text: '08_字符串', link: '/datastructure/08_字符串_如何正确回答面试中高频考察的字符串匹配算法' },
            { text: '09_树和二叉树', link: '/datastructure/09_树和二叉树_分支关系与层次结构下_如何有效实现增删查' },
            { text: '10_哈希表', link: '/datastructure/10_哈希表_如何利用好高效率查找的利器' },
            { text: '11_递归', link: '/datastructure/11_递归_如何利用递归求解汉诺塔问题' },
            { text: '12_分治', link: '/datastructure/12_分治_如何利用分治法完成数据查找' },
            { text: '13_排序', link: '/datastructure/13_排序_经典排序算法原理解析与优劣对比' },
            { text: '14_动态规划', link: '/datastructure/14_动态规划_如何通过最优子结构_完成复杂问题求解' },
            { text: '15_复杂度分析', link: '/datastructure/15_定位问题才能更好地解决问题_开发前的复杂度分析与技术选型' },
            { text: '16_真题案例1', link: '/datastructure/16_真题案例1_算法思维训练' },
            { text: '17_真题案例2', link: '/datastructure/17_真题案例2_数据结构训练' },
            { text: '18_真题案例3', link: '/datastructure/18_真题案例3_力扣真题训练' },
            { text: '19_真题案例4', link: '/datastructure/19_真题案例4_大厂真题实战演练' }
          ]
        }
      ],
      '/design_patterns/': [
        {
          text: '设计模式',
          items: [
            { text: '概述', link: '/design_patterns/' },
            { text: '13_反转原则', link: '/design_patterns/13-反转原则如何减少代码间的相互影响' },
            { text: '14_惯例原则', link: '/design_patterns/14-惯例原则如何提升编程中的沟通效率' },
            { text: '15_分离原则', link: '/design_patterns/15-分离原则如何将复杂问题拆分成小问题' },
            { text: '16_契约原则', link: '/design_patterns/16-契约原则如何做好-API-接口设计' },
            { text: '17_单例模式', link: '/design_patterns/17-单例模式如何有效进行程序初始化' },
            { text: '18_建造者模式', link: '/design_patterns/18-建造者模式如何创建不同形式的复杂对象' },
            { text: '19_抽象工厂模式', link: '/design_patterns/19-抽象工厂模式如何统一不同代码风格下的代码级别' },
            { text: '20_工厂方法模式', link: '/design_patterns/20-工厂方法模式如何解决生成对象时的不确定性' },
            { text: '21_原型模式', link: '/design_patterns/21-原型模式什么场景下需要用到对象拷贝' },
            { text: '22_适配器模式', link: '/design_patterns/22-适配器模式如何处理不同-API-接口的兼容性' },
            { text: '23_桥接模式', link: '/design_patterns/23-桥接模式如何实现抽象协议与不同实现的绑定' },
            { text: '24_组合模式', link: '/design_patterns/24-组合模式如何用树形结构处理对象之间的复杂关系' },
            { text: '25_装饰模式', link: '/design_patterns/25-装饰模式如何在基础组件上扩展新功能' },
            { text: '26_门面模式', link: '/design_patterns/26-门面模式如何实现-API-网关的高可用性' },
            { text: '27_享元模式', link: '/design_patterns/27-享元模式如何通过共享对象减少内存加载消耗' },
            { text: '28_代理模式', link: '/design_patterns/28-代理模式如何控制和管理对象的访问' },
            { text: '29_访问者模式', link: '/design_patterns/29-访问者模式如何实现对象级别的矩阵结构' },
            { text: '30_模板方法模式', link: '/design_patterns/30-模板方法模式如何实现同一模板框架下的算法扩展' },
            { text: '31_策略模式', link: '/design_patterns/31-策略模式如何解决不同活动策略的营销推荐场景' },
            { text: '32_状态模式', link: '/design_patterns/32-状态模式如何通过有限状态机监控功能的“状态变化”' },
            { text: '33_观察者模式', link: '/design_patterns/33-观察者模式如何发送消息变化的通知' },
            { text: '34_备忘录模式', link: '/design_patterns/34-备忘录模式如何在聊天会话中记录历史消息' },
            { text: '35_中介者模式', link: '/design_patterns/35-中介者模式如何通过中间层来解决耦合过多的问题' },
            { text: '36_迭代器模式', link: '/design_patterns/36-迭代器模式如何实现遍历数据时的职责分离' },
            { text: '37_解释器模式', link: '/design_patterns/37-解释器模式如何实现一个自定义配置规则功能' },
            { text: '38_命令模式', link: '/design_patterns/38-命令模式如何在一次请求中封装多个参数' },
            { text: '39_责任链模式', link: '/design_patterns/39-责任链模式如何解决审核、过滤场景问题' }
          ]
        }
      ],
      '/network_fundamentals/': [
        {
          text: '网络基础',
          items: [
            { text: '概述', link: '/network_fundamentals/' },
            { text: '01_漫游互联网', link: '/network_fundamentals/01_漫游互联网_什么是蜂窝移动网络' },
            { text: '02_TCP握手挥手', link: '/network_fundamentals/02_传输层协议_TCP_TCP_为什么握手是_3_次_挥手是_4_次' },
            { text: '03_TCP粘包', link: '/network_fundamentals/03_TCP_的封包格式_TCP_为什么要粘包和拆包' },
            { text: '04_TCP滑动窗口', link: '/network_fundamentals/04_TCP_的稳定性_滑动窗口和流速控制是怎么回事' },
            { text: '05_UDP协议', link: '/network_fundamentals/05_UDP_协议_TCP_协议和_UDP_协议的优势和劣势' },
            { text: '06_IPv4', link: '/network_fundamentals/06_IPv4_协议_路由和寻址的区别是什么' },
            { text: '07_IPv6', link: '/network_fundamentals/07_IPv6_协议_Tunnel_技术是什么' },
            { text: '08_NAT', link: '/network_fundamentals/08_局域网_NAT_是如何工作的' },
            { text: '09_TCP抓包', link: '/network_fundamentals/09_TCP_实战_如何进行_TCP_抓包调试' },
            { text: '10_Socket与epoll', link: '/network_fundamentals/10_Socket_编程_epoll_为什么用红黑树' },
            { text: '11_缓冲区flip', link: '/network_fundamentals/11_流和缓冲区_缓冲区的_flip_是怎么回事' },
            { text: '12_BIO_NIO_AIO', link: '/network_fundamentals/12_网络_IO_模型_BIO_NIO_和_AIO_有什么区别' },
            { text: '13_RPC框架', link: '/network_fundamentals/13_面试中如何回答“怎样实现_RPC_框架”的问题' },
            { text: '14_DNS', link: '/network_fundamentals/14_DNS_域名解析系统_CNAME_记录的作用是' },
            { text: '15_CDN', link: '/network_fundamentals/15_内容分发网络_请简述_CDN_回源如何工作' },
            { text: '16_HTTP缓存', link: '/network_fundamentals/16_HTTP_协议面试通关_强制缓存和协商缓存的区别是' },
            { text: '17_流媒体', link: '/network_fundamentals/17_流媒体技术_直播网站是如何实现的' },
            { text: '18_爬虫与反爬虫', link: '/network_fundamentals/18_爬虫和反爬虫_如何防止黑产爬取我的数据' },
            { text: '19_网络安全', link: '/network_fundamentals/19_网络安全概述_对称_非对称加密的区别是' },
            { text: '20_HTTPS', link: '/network_fundamentals/20_信任链_为什么可以相信一个_HTTPS_网站' },
            { text: '21_DDoS防护', link: '/network_fundamentals/21_攻防手段介绍_如何抵御_SYN_拒绝攻击' }
          ]
        }
      ],
      '/os_fundamentals/': [
        {
          text: '操作系统基础',
          items: [
            { text: '概述', link: '/os_fundamentals/' },
            { text: '01_计算机是什么', link: '/os_fundamentals/01_计算机是什么' },
            { text: '02_32位与64位', link: '/os_fundamentals/02_程序的执行_相比_32_位_64_位的优势是什么(上)' },
            { text: '03_程序执行64位下', link: '/os_fundamentals/03_程序的执行_相比_32_位_64_位的优势是什么(下)' },
            { text: '04_递归转非递归', link: '/os_fundamentals/04_构造复杂的程序_将一个递归函数转成非递归函数的通用方法' },
            { text: '05_存储器分级', link: '/os_fundamentals/05_存储器分级_L1_Cache_比内存和_SSD_快多少倍' },
            { text: '06_文件管理', link: '/os_fundamentals/06_目录结构和文件管理指令_rm_rf_指令的作用是' },
            { text: '07_进程与管道', link: '/os_fundamentals/07_进程_重定向和管道指令_xarg_指令的作用是' },
            { text: '08_用户权限', link: '/os_fundamentals/08_用户和权限管理指令_请简述_Linux_权限划分的原则' },
            { text: '09_Linux网络指令', link: '/os_fundamentals/09_Linux_中的网络指令_如何查看一个域名有哪些_NS_记录' },
            { text: '10_软件安装', link: '/os_fundamentals/10_软件的安装_编译安装和包管理器安装有什么优势和劣势' },
            { text: '11_日志分析', link: '/os_fundamentals/11_高级技巧之日志分析_利用_Linux_指令分析_Web_日志' },
            { text: '12_集群部署', link: '/os_fundamentals/12_高级技巧之集群部署_利用_Linux_指令同时在多台机器部署程序' },
            { text: '13_Linux内核', link: '/os_fundamentals/13_操作系统内核_Linux_内核和_Window_内核有什么区别' },
            { text: '14_用户态内核态', link: '/os_fundamentals/14_用户态和内核态_用户态线程和内核态线程有什么区别' },
            { text: '15_中断', link: '/os_fundamentals/15_中断和中断向量_Javaj_等语言为什么可以捕获到键盘输入' },
            { text: '16_OS对比', link: '/os_fundamentals/16_WinMacUnixLinux_的区别和联系_为什么_Debian_漏洞排名第一还这么多人用' },
            { text: '17_进程与线程', link: '/os_fundamentals/17_进程和线程_进程的开销比线程大在了哪里' },
            { text: '18_锁', link: '/os_fundamentals/18_锁_信号量和分布式锁_如何控制同一时间只有_2_个线程运行' },
            { text: '19_乐观锁', link: '/os_fundamentals/19_乐观锁_区块链_除了上锁还有哪些并发控制方法' },
            { text: '20_线程调度', link: '/os_fundamentals/20_线程的调度_线程调度都有哪些方法' },
            { text: '21_哲学家就餐', link: '/os_fundamentals/21_哲学家就餐问题_什么情况下会触发饥饿和死锁' },
            { text: '22_进程间通信', link: '/os_fundamentals/22_进程间通信_进程间通信都有哪些方法' },
            { text: '23_服务进程线程', link: '/os_fundamentals/23_分析服务的特性_我的服务应该开多少个进程_多少个线程' },
            { text: '24_虚拟内存', link: '/os_fundamentals/24_虚拟内存_一个程序最多能使用多少内存' },
            { text: '25_内存管理单元', link: '/os_fundamentals/25_内存管理单元_什么情况下使用大内存分页' },
            { text: '26_LRU缓存', link: '/os_fundamentals/26_缓存置换算法_LRU_用什么数据结构实现更合理' },
            { text: '27_内存回收上', link: '/os_fundamentals/27_内存回收上篇_如何解决内存的循环引用问题' },
            { text: '28_内存回收下', link: '/os_fundamentals/28_内存回收下篇_三色标记_清除算法是怎么回事' },
            { text: '29_Linux目录', link: '/os_fundamentals/29_Linux_下的各个目录有什么作用' },
            { text: '30_文件系统', link: '/os_fundamentals/30_文件系统的底层实现_FAT_NTFS_和_Ext3_有什么区别' },
            { text: '31_B树与B+树', link: '/os_fundamentals/31_数据库文件系统实例_MySQL_中_B_树和_B+_树有什么区别' },
            { text: '32_HDFS', link: '/os_fundamentals/32_HDFS_介绍_分布式文件系统是怎么回事' },
            { text: '33_TCPIP多路复用', link: '/os_fundamentals/33_互联网协议群(TCPIP)_多路复用是怎么回事' },
            { text: '34_UDP协议', link: '/os_fundamentals/34_UDP_协议_UDP_和_TCP_相比快在哪里' },
            { text: '35_IO模式', link: '/os_fundamentals/35_Linux_的_IO_模式_electpollepoll_有什么区别' },
            { text: '36_公私钥体系', link: '/os_fundamentals/36_公私钥体系和网络安全_什么是中间人攻击' },
            { text: '39_Linux架构', link: '/os_fundamentals/39_Linux_架构优秀在哪里' }
          ]
        }
      ],
      '/qemu/': [
        {
          text: 'QEMU 架构分析',
          items: [
            { text: '概述', link: '/qemu/' },
            {
              text: 'Phase 1-3: 核心子系统',
              items: [
                { text: 'QOM (对象模型)', link: '/qemu/01_qom' },
                { text: '内存管理', link: '/qemu/02_memory' },
                { text: 'CPU 执行', link: '/qemu/03_cpu' }
              ]
            },
            {
              text: 'Phase 4: 块设备层',
              items: [
                { text: 'BlockDriverState 图结构', link: '/qemu/04_block_bs_graph' },
                { text: 'QCOW2 格式实现', link: '/qemu/04_qcow2' },
                { text: 'Coroutine 和 I/O 线程', link: '/qemu/04_coroutine_io' },
                { text: '块任务与实时迁移', link: '/qemu/04_block_job' }
              ]
            },
            {
              text: 'Phase 5: 迁移',
              items: [
                { text: '迁移框架', link: '/qemu/05_migration_framework' },
                { text: 'RAM 迁移', link: '/qemu/05_ram_migration' },
                { text: 'Multifd 和压缩', link: '/qemu/05_multifd_compression' }
              ]
            },
            {
              text: 'Phase 6: 网络',
              items: [
                { text: '网络核心架构', link: '/qemu/06_network_core' },
                { text: 'VLAN 和 Hub', link: '/qemu/06_vlan_hub' }
              ]
            },
            {
              text: 'Phase 7: 用户模式',
              items: [
                { text: '系统调用模拟', link: '/qemu/07_syscall' },
                { text: '信号处理', link: '/qemu/07_signal' }
              ]
            },
            {
              text: 'Phase 8: QAPI',
              items: [
                { text: 'QAPI Schema 和代码生成', link: '/qemu/08_qapi' }
              ]
            },
            {
              text: 'Phase 9: UI',
              items: [
                { text: 'VNC 服务器架构', link: '/qemu/09_vnc' }
              ]
            }
          ]
        }
      ],
      '/kernel/': [
        {
          text: 'Linux 内核深度分析',
          items: [
            { text: '概述', link: '/kernel/' },
            {
              text: '内存管理 (mm)',
              items: [
                { text: '概述', link: '/mm/linux_kernel/' },
                { text: '分配器', link: '/mm/linux_kernel/mm_allocator' },
                { text: '核心结构', link: '/mm/linux_kernel/mm_core_structs' },
                { text: '内存映射', link: '/mm/linux_kernel/mm_mmap' },
                { text: '页错误处理', link: '/mm/linux_kernel/mm_page_fault' },
                { text: '页面回收', link: '/mm/linux_kernel/mm_page_reclaim' },
                { text: 'OOM 处理', link: '/mm/linux_kernel/mm_oom' },
                { text: 'Swap', link: '/mm/linux_kernel/mm_swap' },
                { text: 'Cgroup 内存', link: '/mm/linux_kernel/mm_memory_cgroup' }
              ]
            },
            {
              text: '虚拟文件系统 (VFS)',
              items: [
                { text: '概述', link: '/vfs/linux_kernel/' },
                { text: '索引节点', link: '/vfs/linux_kernel/inode' },
                { text: '目录项缓存', link: '/vfs/linux_kernel/dcache' },
                { text: '超级块', link: '/vfs/linux_kernel/superblock' },
                { text: '文件操作', link: '/vfs/linux_kernel/file_operations' },
                { text: '缓冲区缓存', link: '/vfs/linux_kernel/buffer_cache' },
                { text: '路径查找', link: '/vfs/linux_kernel/path_lookup' },
                { text: '挂载命名空间', link: '/vfs/linux_kernel/mount_namespace' },
                { text: '可执行格式', link: '/vfs/linux_kernel/exec_binfmt' }
              ]
            },
            {
              text: '块设备层 (block)',
              items: [
                { text: '概述', link: '/block/linux_kernel/' },
                { text: '通用块层', link: '/block/linux_kernel/block_core' },
                { text: '请求处理', link: '/block/linux_kernel/block_request' },
                { text: '调度器', link: '/block/linux_kernel/block_scheduler' },
                { text: '多队列', link: '/block/linux_kernel/block_mq' },
                { text: ' gendisk', link: '/block/linux_kernel/block_genhd' }
              ]
            },
            {
              text: '网络子系统',
              items: [
                { text: '概述', link: '/net/linux_kernel/' },
                { text: 'Socket 核心', link: '/net/linux_kernel/net_socket_core' },
                { text: 'TCP/IP 协议栈', link: '/net/linux_kernel/net_tcp_ip' },
                { text: 'Netfilter', link: '/net/linux_kernel/net_netfilter' },
                { text: '路由', link: '/net/linux_kernel/net_routing' },
                { text: 'sk_buff', link: '/net/linux_kernel/net_skbuff' }
              ]
            },
            {
              text: 'Netfilter',
              items: [
                { text: '概述', link: '/netfilter/linux_kernel/' },
                { text: '子系统架构', link: '/netfilter/linux_kernel/netfilter_subsystem' }
              ]
            },
            {
              text: '调度器 (sched)',
              items: [
                { text: '概述', link: '/sched/linux_kernel/' },
                { text: '核心结构', link: '/sched/linux_kernel/sched_core' },
                { text: 'CFS 调度器', link: '/sched/linux_kernel/sched_cfs' },
                { text: '实时调度', link: '/sched/linux_kernel/sched_rt' },
                { text: '上下文切换', link: '/sched/linux_kernel/sched_context_switch' },
                { text: '负载均衡', link: '/sched/linux_kernel/sched_load_balance' }
              ]
            },
            {
              text: '同步机制 (locking)',
              items: [
                { text: '概述', link: '/locking/linux_kernel/' },
                { text: '子系统架构', link: '/locking/linux_kernel/locking_subsystem' }
              ]
            },
            {
              text: 'RCU',
              items: [
                { text: '概述', link: '/rcu/linux_kernel/' },
                { text: '子系统架构', link: '/rcu/linux_kernel/rcu_subsystem' }
              ]
            },
            {
              text: '时间管理 (time)',
              items: [
                { text: '概述', link: '/time/linux_kernel/' },
                { text: '子系统架构', link: '/time/linux_kernel/time_subsystem' }
              ]
            },
            {
              text: '进程间通信 (ipc)',
              items: [
                { text: '概述', link: '/ipc/linux_kernel/' },
                { text: '子系统架构', link: '/ipc/linux_kernel/ipc_subsystem' }
              ]
            },
            {
              text: 'I/O uring',
              items: [
                { text: '概述', link: '/io_uring/linux_kernel/' },
                { text: '核心架构', link: '/io_uring/linux_kernel/io_uring_core' },
                { text: '内存管理', link: '/io_uring/linux_kernel/io_uring_memory' },
                { text: '操作机制', link: '/io_uring/linux_kernel/io_uring_operations' },
                { text: '特性', link: '/io_uring/linux_kernel/io_uring_features' }
              ]
            },
            {
              text: '加密子系统 (crypto)',
              items: [
                { text: '概述', link: '/crypto/linux_kernel/' },
                { text: '核心架构', link: '/crypto/linux_kernel/crypto_core' },
                { text: '异步加密', link: '/crypto/linux_kernel/crypto_async' },
                { text: '基础设施', link: '/crypto/linux_kernel/crypto_infra' },
                { text: 'SKCIPHER', link: '/crypto/linux_kernel/crypto_skcipher' }
              ]
            },
            {
              text: '通用库 (lib)',
              items: [
                { text: '概述', link: '/lib/linux_kernel/' },
                { text: '子系统架构', link: '/lib/linux_kernel/lib_subsystem' }
              ]
            },
            {
              text: '音频子系统 (sound)',
              items: [
                { text: '概述', link: '/sound/linux_kernel/' },
                { text: '子系统架构', link: '/sound/linux_kernel/sound_subsystem' }
              ]
            },
            {
              text: '虚拟化 (virt)',
              items: [
                { text: '概述', link: '/virt/linux_kernel/' },
                { text: 'KVM 核心', link: '/virt/linux_kernel/kvm_core' },
                { text: 'KVM 内存', link: '/virt/linux_kernel/kvm_memory' },
                { text: 'KVM vCPU', link: '/virt/linux_kernel/kvm_vcpu' },
                { text: 'KVM 中断', link: '/virt/linux_kernel/kvm_interrupt' },
                { text: 'KVM MMU', link: '/virt/linux_kernel/kvm_mmu' },
                { text: 'Virtio 框架', link: '/virt/linux_kernel/virtio_framework' },
                { text: 'Virtio 设备驱动', link: '/virt/linux_kernel/virtio_drivers' },
                { text: 'Virtio 传输', link: '/virt/linux_kernel/virtio_transport' }
              ]
            },
            {
              text: 'OpenBMC',
              items: [
                { text: '概述', link: '/openbmc/linux_kernel/' },
                { text: 'IPMI 协议栈', link: '/openbmc/linux_kernel/ipmi_protocol_stack' },
                { text: 'Redfish 接口', link: '/openbmc/linux_kernel/redfish_interface' },
                { text: 'D-Bus 服务', link: '/openbmc/linux_kernel/phosphor_dbus_services' },
                { text: '网络安全', link: '/openbmc/linux_kernel/security_subsystem' },
                { text: '硬件控制', link: '/openbmc/linux_kernel/hardware_control' },
                { text: '网络通信服务', link: '/openbmc/linux_kernel/network_comm_services' },
                { text: '固件更新', link: '/openbmc/linux_kernel/boot_firmware_update' }
              ]
            }
          ]
        }
      ]
    }
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-runtime': ['vue/runtime-core', 'vue/runtime-dom'],
          'vue-compiler': ['vue/compiler-core', 'vue/compiler-dom', 'vue/compiler-sfc'],
          'vitepress': ['vitepress']
        }
      }
    },
    chunkSizeWarningLimit: 600
  }
})
