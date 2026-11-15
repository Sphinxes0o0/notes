export default [
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
]
