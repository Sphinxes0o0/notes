export default [
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
          {
            text: 'Snort 3 架构分析',
            collapsed: true,
            items: [
              { text: '总目录', link: '/security/nids/snort3_architecture_analysis' },
              { text: '数据包处理流水线与模块', link: '/security/nids/snort3/' },
              { text: "架构与数据包流程", link: '/security/nids/snort3/01-architecture' },
              { text: "数据结构与插件开发", link: '/security/nids/snort3/02-core-details' },
              { text: "附录 C–L", link: '/security/nids/snort3/03-appendices-c-l' },
              { text: "附录 M–Z", link: '/security/nids/snort3/04-appendices-m-z' },
              { text: "附录 AA–AN", link: '/security/nids/snort3/05-appendices-aa-an' },
              { text: "附录 AO–BH", link: '/security/nids/snort3/06-appendices-ao-bh' },
              { text: "附录 BI–BY", link: '/security/nids/snort3/07-appendices-bi-by' },
              { text: "附录 BZ–CQ", link: '/security/nids/snort3/08-appendices-bz-cq' },
              { text: "附录 CR–DK", link: '/security/nids/snort3/09-appendices-cr-dk' },
              { text: "附录 DL–EE", link: '/security/nids/snort3/10-appendices-dl-ee' },
              { text: "附录 EF–EW", link: '/security/nids/snort3/11-appendices-ef-ew' },
              { text: "附录 EX–FH", link: '/security/nids/snort3/12-appendices-ex-fh' },
              { text: "附录 FI–FX", link: '/security/nids/snort3/13-appendices-fi-fx' },
              { text: "附录 FY–GK", link: '/security/nids/snort3/14-appendices-fy-gk' },
              { text: "附录 GL–GV", link: '/security/nids/snort3/15-appendices-gl-gv' },
              { text: "附录 GW–HG", link: '/security/nids/snort3/16-appendices-gw-hg' },
              { text: "附录 HH–HQ", link: '/security/nids/snort3/17-appendices-hh-hq' },
              { text: "附录 HR–ID", link: '/security/nids/snort3/18-appendices-hr-id' },
              { text: "附录 IE–IN", link: '/security/nids/snort3/19-appendices-ie-in' },
              { text: "附录 IO–IY", link: '/security/nids/snort3/20-appendices-io-iy' },
              { text: "附录 IZ–JL", link: '/security/nids/snort3/21-appendices-iz-jl' },
              { text: "附录 JM–JX", link: '/security/nids/snort3/22-appendices-jm-jx' },
              { text: "附录 JY–KJ", link: '/security/nids/snort3/23-appendices-jy-kj' },
              { text: "附录 KK–LB", link: '/security/nids/snort3/24-appendices-kk-lb' },
              { text: "附录 LC–LW", link: '/security/nids/snort3/25-appendices-lc-lw' },
              { text: "Codec、TCP 重组与流管理", link: '/security/nids/snort3/26-codecs-tcp-and-flow' },
              { text: "Inspector、协议与规则解析", link: '/security/nids/snort3/27-inspectors-and-rules' },
              { text: "协议检测与参考索引", link: '/security/nids/snort3/28-protocols-and-reference' }
            ]
          }
        ]
      },
      {
        text: 'LLM Agent 防御',
        collapsed: true,
        items: [
          { text: '分层防御方案（IAM + 规则 + Content Guard + NSFA + 沙箱）', link: '/security/llm_agent_defense/layered_defense' },
          { text: 'IAM 认证架构（身份 / 认证 / 凭据管理）', link: '/security/llm_agent_defense/iam_auth_architecture' },
          { text: 'IAM 详细架构与模块流程（启动 / 状态机 / 时序 / 故障 / demo）', link: '/security/llm_agent_defense/detailed_architecture' },
          { text: 'A2A 协议（车载三域 + IAM 集成 + 安全威胁）', link: '/security/llm_agent_defense/a2a_vehicle_protocol' },
          { text: 'A2A + IAM 融合架构（Token 模型 / Sidecar 中间件 / 多跳链路）', link: '/security/llm_agent_defense/a2a_iam_integration_arch' },
          { text: 'A2A + IAM 深度分析与 gRPC 扩展演进', link: '/security/llm_agent_defense/a2a_iam_grpc_deep_dive' },
          { text: 'IAM 对 A2A 的零侵入设计（AgentCard 签名 / Bearer / Server-Side Policy）', link: '/security/llm_agent_defense/a2a_iam_nonintrusive' }
        ]
      },
      {
        // 与 /security/network-traffic-analysis/ 同性质（外部资料综述）
        // 原位于 /research/llm-agent-security-reports/,2026-08 重组到 security/
        text: 'LLM Agent 安全研报',
        collapsed: true,
        items: [
          { text: '概述', link: '/security/llm-agent-security-reports/' },
          { text: 'OWASP LLM Top 10 防御', link: '/security/llm-agent-security-reports/owasp-llm-top10-defenses' },
          { text: 'LLM 应用安全架构', link: '/security/llm-agent-security-reports/llm-app-security-architecture' },
          { text: 'AI Agent 安全 IAM', link: '/security/llm-agent-security-reports/ai-agent-security-iam' },
          { text: 'Constitutional Classifiers (arxiv)', link: '/security/llm-agent-security-reports/arxiv-2601-04603-constitutional-classifiers-pp' },
          { text: 'Three Labs 2026', link: '/security/llm-agent-security-reports/llm-agent-security-three-labs-2026' },
          { text: 'METR 2026 Frontier Risk', link: '/security/llm-agent-security-reports/metr-2026-frontier-risk-report' }
        ]
      },
      {
        text: 'Linux 内核安全',
        collapsed: true,
        items: [
          { text: 'LSM Framework', link: '/security/linux_kernel/lsm_framework' },
          { text: 'SELinux', link: '/security/linux_kernel/selinux_detailed' },
          { text: 'AppArmor', link: '/security/linux_kernel/apparmor_detailed' },
          { text: 'BPF Security', link: '/security/linux_kernel/bpf_security' },
          { text: 'Landlock', link: '/security/linux_kernel/landlock_detailed' },
          { text: 'Integrity Keys', link: '/security/linux_kernel/integrity_keys' },
          { text: 'Lockdown LoadPin', link: '/security/linux_kernel/lockdown_loadpin' },
          { text: 'Security Deep Dive R1', link: '/security/linux_kernel/security_deep_dive_r1' },
          { text: 'Security Deep Dive R2', link: '/security/linux_kernel/security_deep_dive_r2' }
        ]
      },
      {
        text: '网络流量分析 (论文集)',
        collapsed: true,
        items: [
          { text: '研究概述 (README)', link: '/security/network-traffic-analysis/README' },
          { text: '2023-2026 文献综述', link: '/security/network-traffic-analysis/literature-review-2023-2026' },
          { text: '方法对比', link: '/security/network-traffic-analysis/method-comparison' },
          { text: '快速参考', link: '/security/network-traffic-analysis/quick-reference' },
          { text: '研究时间线', link: '/security/network-traffic-analysis/research-timeline' },
          { text: '研究笔记', link: '/security/network-traffic-analysis/research-notes' },
          {
            text: '论文分类 (共 62 篇)',
            collapsed: true,
            items: [
              {
                text: '01. 入侵检测 (21)',
                items: [
                  { text: 'NIDS 类不平衡问题', link: '/security/network-traffic-analysis/papers/01-IDS/paper-01-class-imbalance-deep-learning' },
                  { text: 'SVM 恶意流量检测', link: '/security/network-traffic-analysis/papers/01-IDS/paper-02-SVM-malicious-traffic' },
                  { text: '特征选择 + 集成学习', link: '/security/network-traffic-analysis/papers/01-IDS/paper-03-feature-selection-ensemble' }
                ]
              },
              {
                text: '02. 加密流量 (13)',
                items: [
                  { text: 'TLS 特征 + 集成 (94.85%)', link: '/security/network-traffic-analysis/papers/02-Encrypted/paper-21-TLS-ensemble-94.85' },
                  { text: 'BiLSTM + 自注意力 (96.71%)', link: '/security/network-traffic-analysis/papers/02-Encrypted/paper-22-TLS-BiLSTM-96.71' },
                  { text: 'TLS + 随机森林恶意软件检测', link: '/security/network-traffic-analysis/papers/02-Encrypted/paper-23-TLS-RF-malware' }
                ]
              },
              {
                text: '03. 深度学习 (14)',
                items: [
                  { text: 'CNN-LSTM 混合网络', link: '/security/network-traffic-analysis/papers/03-DeepLearning/paper-35-CNN-LSTM-hybrid-traffic' },
                  { text: 'IoT 恶意软件可视化', link: '/security/network-traffic-analysis/papers/03-DeepLearning/paper-36-IoT-malware-visual' },
                  { text: 'CNN+SE-Net 恶意流量识别', link: '/security/network-traffic-analysis/papers/03-DeepLearning/paper-37-CNN-SE-Net-malware' }
                ]
              },
              {
                text: '04. IoT / 5G (8)',
                items: [
                  { text: '机器学习与 IoT 安全', link: '/security/network-traffic-analysis/papers/04-IoT-5G/paper-49-ML-IoT-security' },
                  { text: 'N-BaIoT 数据集 DDOS 检测', link: '/security/network-traffic-analysis/papers/04-IoT-5G/paper-50-N-BaIoT-DDOS' },
                  { text: '移动恶意软件流量检测', link: '/security/network-traffic-analysis/papers/04-IoT-5G/paper-51-mobile-malware-detection' }
                ]
              },
              {
                text: '05. 对抗样本 (4)',
                items: [
                  { text: 'TAD - 多对抗检测', link: '/security/network-traffic-analysis/papers/05-Adversarial/paper-57-TAD-multi-adversarial' },
                  { text: 'IDS 鲁棒性评估', link: '/security/network-traffic-analysis/papers/05-Adversarial/paper-58-IDS-robustness' },
                  { text: 'GAN 突变流量检测', link: '/security/network-traffic-analysis/papers/05-Adversarial/paper-59-mutated-traffic-GAN' }
                ]
              },
              {
                text: '06. SDN (2)',
                items: [
                  { text: 'SDN 动态扩散', link: '/security/network-traffic-analysis/papers/06-SDN/paper-61-SDN-dynamics-diffusion' },
                  { text: 'SDN 5G/IoT 安全架构', link: '/security/network-traffic-analysis/papers/06-SDN/paper-62-SDN-security-architecture' }
                ]
              }
            ]
          }
        ]
      },
      {
        text: 'SPIFFE 翻译',
        collapsed: true,
        items: [
          { text: '概述', link: '/security/spiffe-book/' },
          { text: '01 - 历史与动机', link: '/security/spiffe-book/ch01-history-and-motivation' },
          { text: '02 - 收益', link: '/security/spiffe-book/ch02-benefits' },
          { text: '03 - 身份背后的一般概念', link: '/security/spiffe-book/ch03-general-concepts-behind-identity' },
          { text: '04 - SPIFFE 与 SPIRE 介绍', link: '/security/spiffe-book/ch04-introduction-to-spiffe-and-spire' },
          { text: '05 - 入门前准备', link: '/security/spiffe-book/ch05-before-you-start' },
          { text: '06 - 设计 SPIRE 部署', link: '/security/spiffe-book/ch06-designing-a-spire-deployment' },
          { text: '07 - 与其他系统集成', link: '/security/spiffe-book/ch07-integrating-with-others' },
          { text: '08 - 用 SPIFFE 身份驱动授权', link: '/security/spiffe-book/ch08-using-spiffe-identities-to-inform-authorization' },
          { text: '09 - 与其他安全技术对比', link: '/security/spiffe-book/ch09-comparing-spiffe-to-other-security-technologies' },
          { text: '10 - 实践者故事', link: '/security/spiffe-book/ch10-practitioners-stories' },
          { text: '术语表', link: '/security/spiffe-book/11-glossary' },
          { text: '译注', link: '/security/spiffe-book/12-notes' },
          { text: '尾声', link: '/security/spiffe-book/13-epilogue' }
        ]
      }
    ]
  }
]
