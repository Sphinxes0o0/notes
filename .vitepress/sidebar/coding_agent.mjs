export default [
  {
    text: 'AI 编码 Agent',
    items: [
      { text: '概述', link: '/coding_agent/' },
      { text: 'pi-agent', collapsed: true, items: [
{ text: '概述与目录', link: '/coding_agent/pi-agent' },
{ text: "Implementations", link: '/coding_agent/pi-agent/01-sections' },
{ text: "2. pi-ai 统一 API：40+ Provider 的抽象", link: '/coding_agent/pi-agent/02-sections' },
{ text: "2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors）", link: '/coding_agent/pi-agent/03-sections' },
{ text: "5. 关键文件索引", link: '/coding_agent/pi-agent/04-sections' },
{ text: "4. Subagent Task Fan-out 机制", link: '/coding_agent/pi-agent/05-sections' }
] },
      { text: 'Pi 扩展生态与能力', link: '/coding_agent/pi-agent-ecosystem' },
      { text: 'Pi vs 其他 Agent 框架', link: '/coding_agent/pi-agent-comparison' },
      { text: 'Pi 定制 workflow 实操', link: '/coding_agent/pi-agent-custom-workflow' },
      { text: 'Hermes Agent Memory 系统设计', link: '/coding_agent/hermes_memory_design' },
      { text: 'Hermes Memory 论文与开源项目', link: '/coding_agent/hermes_memory_research_2026h1' },
      { text: 'A2A 协议与实战 ↗', link: '/a2a/' },
      { text: '跨 Agent Session 可移植方案', link: '/coding_agent/session-portability' }
    ]
  }
]
