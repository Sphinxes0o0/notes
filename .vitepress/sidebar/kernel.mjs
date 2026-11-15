export default [
  {
    text: 'Linux 内核深度分析',
    items: [
      { text: '概述', link: '/kernel/' },
      {
        text: '内存管理 (mm)',
        collapsed: true,
        items: [
          { text: '概述', link: '/kernel/mm/' },
          { text: '分配器', link: '/kernel/mm/mm_allocator' },
          { text: '核心结构', link: '/kernel/mm/mm_core_structs' },
          { text: '内存映射', link: '/kernel/mm/mm_mmap' },
          { text: '页错误处理', link: '/kernel/mm/mm_page_fault' },
          { text: '页面回收', link: '/kernel/mm/mm_page_reclaim' },
          { text: 'OOM 处理', link: '/kernel/mm/mm_oom' },
          { text: 'Swap', link: '/kernel/mm/mm_swap' },
          { text: 'Cgroup 内存', link: '/kernel/mm/mm_memory_cgroup' }
        ]
      },
      {
        text: '虚拟文件系统 (VFS)',
        collapsed: true,
        items: [
          { text: '概述', link: '/kernel/vfs/' },
          { text: '索引节点', link: '/kernel/vfs/inode' },
          { text: '目录项缓存', link: '/kernel/vfs/dcache' },
          { text: '超级块', link: '/kernel/vfs/superblock' },
          { text: '文件操作', link: '/kernel/vfs/file_operations' },
          { text: '缓冲区缓存', link: '/kernel/vfs/buffer_cache' },
          { text: '路径查找', link: '/kernel/vfs/path_lookup' },
          { text: '挂载命名空间', link: '/kernel/vfs/mount_namespace' },
          { text: '可执行格式', link: '/kernel/vfs/exec_binfmt' }
        ]
      },
      {
        text: '块设备层 (block)',
        collapsed: true,
        items: [
          { text: '概述', link: '/kernel/block/' },
          { text: '通用块层', link: '/kernel/block/block_core' },
          { text: '请求处理', link: '/kernel/block/block_request' },
          { text: '调度器', link: '/kernel/block/block_scheduler' },
          { text: '多队列', link: '/kernel/block/block_mq' },
          { text: 'gendisk', link: '/kernel/block/block_genhd' }
        ]
      },
      {
        // 交叉引用：网络子系统内容位于 /network/linux_kernel/，保留入口便于在 kernel 导航中跳转
        text: '网络子系统 ↗',
        items: [
          { text: '概述', link: '/network/linux_kernel/' },
          { text: 'Socket 核心', link: '/network/linux_kernel/net_socket_core' },
          { text: 'TCP/IP 协议栈', link: '/network/linux_kernel/net_tcp_ip' },
          { text: 'Netfilter', link: '/network/linux_kernel/net_netfilter' },
          { text: '路由', link: '/network/linux_kernel/net_routing' },
          { text: 'sk_buff', link: '/network/linux_kernel/net_skbuff' }
        ]
      },
      {
        // 交叉引用：Netfilter 内容位于 /network/linux_netfilter/
        text: 'Netfilter ↗',
        items: [
          { text: '概述', link: '/network/linux_netfilter/' },
          { text: '子系统架构', link: '/network/linux_netfilter/netfilter_subsystem' }
        ]
      },
      {
        text: '调度器 (sched)',
        collapsed: true,
        items: [
          { text: '概述', link: '/kernel/sched/' },
          { text: '核心结构', link: '/kernel/sched/sched_core' },
          { text: 'CFS 调度器', link: '/kernel/sched/sched_cfs' },
          { text: '实时调度', link: '/kernel/sched/sched_rt' },
          { text: '上下文切换', link: '/kernel/sched/sched_context_switch' },
          { text: '负载均衡', link: '/kernel/sched/sched_load_balance' }
        ]
      },
      {
        text: '同步机制 (locking)',
        items: [
          { text: '概述', link: '/kernel/locking/' },
          { text: '子系统架构', link: '/kernel/locking/locking_subsystem' }
        ]
      },
      {
        text: 'RCU',
        items: [
          { text: '概述', link: '/kernel/rcu/' },
          { text: '子系统架构', link: '/kernel/rcu/rcu_subsystem' }
        ]
      },
      {
        text: '时间管理 (time)',
        items: [
          { text: '概述', link: '/kernel/time/' },
          { text: '子系统架构', link: '/kernel/time/time_subsystem' }
        ]
      },
      {
        text: '进程间通信 (ipc)',
        items: [
          { text: '概述', link: '/kernel/ipc/' },
          { text: '子系统架构', link: '/kernel/ipc/ipc_subsystem' }
        ]
      },
      {
        text: 'I/O uring',
        items: [
          { text: '概述', link: '/kernel/io_uring/' },
          { text: '核心架构', link: '/kernel/io_uring/io_uring_core' },
          { text: '内存管理', link: '/kernel/io_uring/io_uring_memory' },
          { text: '操作机制', link: '/kernel/io_uring/io_uring_operations' },
          { text: '特性', link: '/kernel/io_uring/io_uring_features' }
        ]
      },
      {
        text: '加密子系统 (crypto)',
        items: [
          { text: '概述', link: '/kernel/crypto/' },
          { text: '核心架构', link: '/kernel/crypto/crypto_core' },
          { text: '异步加密', link: '/kernel/crypto/crypto_async' },
          { text: '基础设施', link: '/kernel/crypto/crypto_infra' },
          { text: 'SKCIPHER', link: '/kernel/crypto/crypto_skcipher' }
        ]
      },
      {
        text: '通用库 (lib)',
        items: [
          { text: '概述', link: '/kernel/lib/' },
          { text: '子系统架构', link: '/kernel/lib/lib_subsystem' }
        ]
      },
      {
        text: '音频子系统 (sound)',
        items: [
          { text: '概述', link: '/kernel/sound/' },
          { text: '子系统架构', link: '/kernel/sound/sound_subsystem' }
        ]
      },
      {
        text: '虚拟化 (virt)',
        collapsed: true,
        items: [
          { text: '概述', link: '/kernel/virt/' },
          { text: 'KVM 核心', link: '/kernel/virt/kvm_core' },
          { text: 'KVM 内存', link: '/kernel/virt/kvm_memory' },
          { text: 'KVM vCPU', link: '/kernel/virt/kvm_vcpu' },
          { text: 'KVM 中断', link: '/kernel/virt/kvm_interrupt' },
          { text: 'KVM MMU', link: '/kernel/virt/kvm_mmu' },
          { text: 'Virtio 框架', link: '/kernel/virt/virtio_framework' },
          { text: 'Virtio 设备驱动', link: '/kernel/virt/virtio_drivers' },
          { text: 'Virtio 传输', link: '/kernel/virt/virtio_transport' }
        ]
      },
      {
        text: 'eBPF',
        items: [
          { text: '概述', link: '/kernel/ebpf/ebpf' },
          { text: 'eBPF 工作原理', link: '/kernel/ebpf/ebpf-how-ebpf-work' },
          { text: 'AF_XDP 技术', link: '/kernel/ebpf/af-xdp-technical' },
          { text: 'Android 网络', link: '/kernel/ebpf/ebpf-android-network' }
        ]
      },
      {
        text: 'OpenBMC',
        collapsed: true,
        items: [
          { text: '概述', link: '/kernel/openbmc/' },
          { text: 'IPMI 协议栈', link: '/kernel/openbmc/ipmi_protocol_stack' },
          { text: 'Redfish 接口', link: '/kernel/openbmc/redfish_interface' },
          { text: 'D-Bus 服务', link: '/kernel/openbmc/phosphor_dbus_services' },
          { text: '网络安全', link: '/kernel/openbmc/security_subsystem' },
          { text: '硬件控制', link: '/kernel/openbmc/hardware_control' },
          { text: '网络通信服务', link: '/kernel/openbmc/network_comm_services' },
          { text: '固件更新', link: '/kernel/openbmc/boot_firmware_update' }
        ]
      }
    ]
  }
]
