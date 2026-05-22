---
type: entity
tags: [security, port-scanning, masscan, nmap, network-reconnaissance, vulnerability-assessment, tools]
created: 2026-05-22
sources: [notes-tools]
---

# Port Scanning（端口扫描）

## 定义

端口扫描是网络侦察的核心技术，用于发现目标主机上开放的网络端口和服务。masscan 提供极致速度（互联网规模），nmap 提供全面深度（服务指纹、漏洞检测）。

## 关键要点

### masscan — 高速异步端口扫描器

**设计理念**：无状态、异步、用户态 TCP/IP 栈，单机可达千万 pps。

**核心参数**：

| 参数 | 说明 |
|------|------|
| `-p ports` | 端口规格：单个/范围/列表 |
| `--rate=N` | 发包速率（默认 100，常用 1000~100000） |
| `--banners` | 获取服务 banner 信息 |
| `-oJ file` | JSON 格式输出（推荐） |
| `-oL file` | 列表格式输出 |
| `--resume file` | 从 pause.conf 恢复中断扫描 |
| `-iL file` | 从文件读取目标列表 |

**典型场景**：

```
# 内网快速资产梳理（5 万 pps）
masscan 192.168.0.0/16 -p22,80,443,445,3306,3389 --rate=50000 -oJ lan.json

# 公网单 IP 全端口
masscan 1.2.3.4 -p1-65535 --rate=100000 -oJ full.json

# 批量目标
masscan -iL targets.txt -p22,80,443 --rate=50000 -oJ batch.json
```

**性能注意事项**：高 `--rate` 可能丢包；需 root 权限；`--adapter` 指定网卡避免路由问题。

### nmap — 全面端口扫描与安全审计

**扫描类型对照**：

| 类型 | 参数 | 特点 | 权限 |
|------|------|------|------|
| TCP SYN | `-sS` | 半开放（最常用），快 | root |
| TCP Connect | `-sT` | 全连接，无需 root | 普通用户 |
| UDP | `-sU` | 慢但必要 | root |
| 版本检测 | `-sV` | 服务指纹识别 | — |
| 脚本扫描 | `-sC` | 默认 NSE 脚本 | — |
| OS 检测 | `-O` | 操作系统指纹 | root |
| 综合扫描 | `-A` | -sV + -sC + -O + traceroute | root |

**NSE 脚本引擎**：13 个类别（auth/brute/default/discovery/exploit/vuln 等），可组合使用。

```
# 漏洞检测
nmap --script vuln -p- target

# 心脏滴血
nmap --script ssl-heartbleed -p 443 target

# 永恒之蓝
nmap --script smb-vuln-ms17-010 -p 445 target
```

**时间模板**：T0（偏执/规避 IDS）→ T3（默认）→ T5（疯狂/可能丢包），日常推荐 T4。

**输出格式**：`-oN` 文本 / `-oX` XML / `-oG` Grepable / `-oJ` JSON / `-oA` 全格式。

### 实战组合技

**两步法（推荐工作流）**：

1. **masscan 快速发现**：在大网段上以高并发发现所有开放端口
2. **nmap 精细探测**：对发现的端口做服务版本检测 + 漏洞脚本

```bash
# Step 1: masscan 发现
sudo masscan 10.0.0.0/24 -p1-10000 --rate=100000 -oJ masscan.json

# Step 2: 提取端口 → nmap 精细扫
ports=$(cat masscan.json | jq -r '.[].ports[].port' | sort -u | paste -sd,)
nmap -sV -sC -p $ports 10.0.0.0/24 -oA detail_scan
```

**场景速查**：

| 场景 | 推荐命令 |
|------|---------|
| 存活主机发现 | `nmap -sn 192.168.1.0/24` |
| 内网资产端口 | `masscan 192.168.1.0/24 -p1-10000 --rate=50000` |
| 内网详细探测 | `nmap -sV -sC -p- -A -T4 -oA result target` |
| 漏洞评估 | `nmap --script vuln -p- -A -oA vulnscan target` |
| 绕过防火墙 | `nmap -sS -f -D ME,... -g 53 -p- target` |
| Web 专项 | `nmap -sV -sC -p 80,443,8080 --script http-enum,http-title target` |
| 数据库检测 | `nmap -sV -sC -p 3306,5432,6379 --script mysql*,postgres*,redis* target` |

## 相关概念

- [[entities/tools/linux-network-tools]] — tcpdump 抓包 + netcat 连接与端口扫描互补
- [[entities/security]] — Masscan 架构深度分析（无状态扫描、BlackRock 随机化、SYN Cookie）
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 端口扫描依赖内核 Socket/sk_buff 层和 TCP 协议栈
- [[entities/os/os-io-model]] — nmap 多种扫描类型涉及不同 I/O 模型和 socket 操作

## 来源详情

- [[sources/notes-tools]] — masscan 与 nmap 使用手册（场景化命令 + 组合技）
