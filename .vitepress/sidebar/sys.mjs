export default [
  {
    text: '系统',
    items: [
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
]
