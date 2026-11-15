export default [
  {
    text: '研究合集',
    items: [
      { text: '概述', link: '/research/' },
      {
        text: 'Agent-SafetyBench 评测',
        items: [
          { text: '概述', link: '/research/agent-safetybench-singuard-eval/' }
        ]
      },
      {
        text: 'Agentgateway 分析',
        items: [
          { text: '概述', link: '/research/agentgateway-analysis/' },
          { text: 'IAM 认证与 A2A 授权', link: '/research/agentgateway-analysis/iam-authn-authz-a2a' },
          { text: 'AgentTeams 深度分析', link: '/research/agentgateway-analysis/agentteams-deep-dive' }
        ]
      },
      {
        text: 'NIO 车端 AI Agent 安全',
        items: [
          { text: '概述', link: '/research/nio-vehicle-ai-agent-security/' },
          { text: 'IAM LLM Guard 白皮书', link: '/research/nio-vehicle-ai-agent-security/iam-llm-guard-whitepaper' },
          { text: 'Edge AI 安全报告', link: '/research/nio-vehicle-ai-agent-security/edge-ai-security-report' },
          { text: 'Vehicle IAM 集成', link: '/research/nio-vehicle-ai-agent-security/vehicle-iam-integrated' },
          {
            text: 'Framework Design',
            items: [
              { text: '概述', link: '/research/nio-vehicle-ai-agent-security/framework-design/' },
              { text: 'v2 集成版（Framework + ASG 详细设计）', link: '/research/nio-vehicle-ai-agent-security/framework-design/framework-design-v2-integrated' }
            ]
          }
        ]
      },
      {
        text: 'Uber ADR 深度分析',
        items: [
          { text: '概述', link: '/research/uber-adr-analysis/' }
        ]
      }
    ]
  }
]
