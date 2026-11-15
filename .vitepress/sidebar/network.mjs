export default [
  {
    text: '网络/协议',
    items: [
      {
        text: '网络',
        items: [
          { text: '概述', link: '/network/' },
          { text: '网络栈深度分析', link: '/network/stack_deep_dive' },
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
              // 双语并存：中文版偏概念综述，英文版偏源码分析
              // 见 network/index.md「三个易混目录的快速区分」段
              { text: 'Netfilter 子系统分析（英 · 源码）', link: '/network/linux_netfilter/net_subsystem_netfilter' },
              { text: 'Netfilter 子系统分析（中 · 概念）', link: '/network/linux_netfilter/netfilter_subsystem' },
              { text: 'Netfilter TCP 深度分析', link: '/network/linux_netfilter/netfilter_tcp_deep_dive' },
              { text: '连接跟踪', link: '/network/linux_netfilter/conntrack' },
              { text: '连接跟踪垃圾回收', link: '/network/linux_netfilter/conntrack_gc' },
              { text: 'nftables', link: '/network/linux_netfilter/nftables' }
            ]
          },
          {
            // 合并：原“网络核心”（/network/core/）与“Linux 网络核心”（/network/linux_kernel/）
            text: 'Linux 网络核心',
            collapsed: true,
            items: [
              // —— 核心架构（来源 /network/core/）——
              { text: 'Socket 子系统', link: '/network/linux_kernel/socket_bsd_layer' },
              { text: '连接跟踪（核心架构）', link: '/network/linux_kernel/nf_conntrack_subsystem' },
              { text: '路由（核心架构）', link: '/network/linux_kernel/net_routing_subsystem' },
              // —— 详解与实现（来源 /network/linux_kernel/）——
              { text: 'Socket', link: '/network/linux_kernel/socket' },
              { text: 'Socket Syscall', link: '/network/linux_kernel/socket_syscall' },
              { text: 'TCP', link: '/network/linux_kernel/ipv4_tcp' },
              { text: 'UDP', link: '/network/linux_kernel/ipv4_udp' },
              { text: 'Netfilter', link: '/network/linux_kernel/netfilter' },
              { text: 'XDP', link: '/network/linux_kernel/xdp' },
              { text: 'AF Packet', link: '/network/linux_kernel/af_packet' },
              { text: 'Net Device', link: '/network/linux_kernel/net_device' },
              { text: 'NAPI', link: '/network/linux_kernel/napi' },
              { text: 'SK Buff', link: '/network/linux_kernel/sk_buff' },
              { text: 'Bridge', link: '/network/linux_kernel/bridge' },
              { text: 'DSA', link: '/network/linux_kernel/dsa' },
              { text: 'Routing', link: '/network/linux_kernel/routing' }
            ]
          },
          {
            text: '网络性能',
            items: [
              { text: '内核技巧', link: '/network/performance/net_subsystem_kernel_tricks' },
              { text: '热路径', link: '/network/performance/net_subsystem_hotpath' },
              { text: '高级特性', link: '/network/performance/net_subsystem_advanced' },
              { text: '定时器', link: '/network/performance/net_subsystem_timers' },
              { text: 'TCP Bypass Notes', link: '/network/performance/tcp-bypass-notes' }
            ]
          },
          {
            text: '协议',
            items: [
              { text: 'BPF Hooks', link: '/network/protocols/net_subsystem_bpf_hooks' },
              { text: 'Netlink', link: '/network/protocols/net_subsystem_netlink' },
              { text: 'ARP 表老化机制', link: '/network/protocols/arp-table-aging' },
              { text: 'RFC 实现', link: '/network/rfc/net_subsystem_rfc_impl' }
            ]
          },
          {
            text: '其他网络笔记',
            collapsed: true,
            items: [
              { text: 'OSI: PHY & MAC 层', link: '/network/osi_phy_mac' },
              { text: 'LwIP 网桥实现', link: '/network/lwip-bridge-implementation' },
              { text: 'plantegg - 举三反一', link: '/network/plantegg-three-from-one' }
            ]
          },
          {
            // 翻译文章集：arthurchiao.art / plantegg / lsgxeva
            // 原始目录 /network/linux_net-stack/
            text: '网络栈译文集',
            collapsed: true,
            items: [
              { text: 'plantegg - Linux Network Stack 概览', link: '/network/linux_net-stack/linux-network-stack-plantegg' },
              { text: 'Linux 网络栈原理、监控与调优：前言 (2022)', link: '/network/linux_net-stack/linux-网络栈原理监控与调优前言2022' },
              { text: 'Linux 网络栈 RX：原理及内核实现 (2022)', link: '/network/linux_net-stack/linux-网络栈接收数据rx原理及内核实现2022' },
              { text: 'Linux 网络栈 RX：配置调优 (2022)', link: '/network/linux_net-stack/linux-网络栈接收数据rx配置调优2022' },
              { text: 'Linux 中 ARP 表老化机制 (lsgxeva)', link: '/network/linux_net-stack/linux中arp表的老化机制-lsgxeva-博客园' },
              { text: '[译] 现代网络负载均衡与代理导论 (2017)', link: '/network/linux_net-stack/译-现代网络负载均衡与代理导论2017' }
            ]
          }
        ]
      }
    ]
  }
]
