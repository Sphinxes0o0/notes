# 端口扫描器：masscan 与 nmap 使用手册

本文档涵盖 masscan 和 nmap 的完整使用方法、场景化命令和实战技巧。

---

## 一、masscan

masscan 是异步高速端口扫描器，特点是非常快，但精度略低于 nmap。

### 1.1 安装

```bash
# macOS
brew install masscan

# Ubuntu/Debian
sudo apt install masscan

# 源码编译
git clone https://github.com/robertdavidgraham/masscan
cd masscan && make -j4 && sudo make install
```

### 1.2 核心参数

| 参数 | 说明 |
|------|------|
| `<IP>/<CIDR>` | 目标 IP 或网段 |
| `-p <ports>` | 指定端口，支持单个、范围、列表 |
| `--rate=<N>` | 发包速率，默认 100，常用 1000~100000 |
| `--banners` | 获取 banner 信息 |
| `-oJ <file>` | JSON 格式输出（推荐） |
| `-oL <file>` | 列表格式输出 |
| `-oB <file>` | 二进制输出 |
| `-oG <file>` | Grepable 格式输出 |
| `-iL <file>` | 从文件读取目标列表 |
| `-iR <N>` | 随机扫描 N 个 IP |
| `--excludefile <file>` | 排除文件 |
| `--source-ip <IP>` | 指定源 IP |
| `--adapter <name>` | 指定网卡（需 root） |
| `--wait <N>` | 设置等待时间（默认 10 秒） |
| `--resume <file>` | 恢复暂停的扫描 |
| `--echo` | 输出当前配置到 stdout |

### 1.3 场景化命令

#### 场景 1：内网快速资产梳理

```bash
# 扫描整个内网网段的常用端口，5 万并发速率
sudo masscan 192.168.0.0/16 -p22,80,443,445,3306,3389,5432,6379,8080,8443 \
    --rate=50000 -oJ lan_assets.json

# 查看结果
cat lan_assets.json | jq -r '.[] | select(.ports | length > 0) |
    "\(.ip):\(.ports[].port)"' | sort -V
```

#### 场景 2：公网资产快速测绘

```bash
# 对单个 IP 全端口扫描
sudo masscan 1.2.3.4 -p1-65535 --rate=100000 -oJ single_full.json

# 对 IP 段扫描常见端口
sudo masscan 1.2.3.0/24 -p22,80,443,1080,3306,3389,5432,8080,8443,8888 \
    --rate=100000 -oJ subnet_scan.json

# 随机抽样互联网扫描（测绘用）
sudo masscan -iR 100000 -p22,80,443 --rate=100000 -oJ random_scan.json
```

#### 场景 3：批量目标文件扫描

```bash
# 准备目标文件（每行一个 IP 或 CIDR）
cat > targets.txt << 'EOF'
10.0.0.0/24
192.168.1.1
172.16.0.0/28
8.8.8.8
EOF

# 扫描
sudo masscan -iL targets.txt -p22,80,443,3306,8080 \
    --rate=50000 -oJ batch.json
```

#### 场景 4：获取服务 Banner

```bash
# 获取 HTTP banner（Web 服务器信息）
sudo masscan 10.0.0.1 -p80,443,8080,8443 --banners --rate=1000 \
    -oJ banner_scan.json

# 查看 banner
cat banner_scan.json | jq -r '.[] | .ports[].banner' | head -20
```

#### 场景 5：恢复中断的扫描

```bash
# Ctrl+C 暂停后，当前目录会生成 pause.conf
# 重启扫描
sudo masscan --resume pause.conf

# 导出配置并重启
sudo masscan --echo > masscan.conf
# 编辑 masscan.conf 后
sudo masscan -c masscan.conf
```

### 1.4 性能与网络注意事项

```bash
# 绕过限速（需管理员权限）
sudo masscan 10.0.0.0/24 -p80 --rate=1000000 --adapter eth0

# 指定网卡和源 IP
masscan 10.0.0.0/24 -p80 --rate=10000 --adapter eth0 --source-ip 10.0.0.100

# 设置 TTL
masscan 10.0.0.0/24 -p80 --ttl 64

# 小带宽限速（假设 2Mbps）
masscan 10.0.0.0/24 -p80 --rate=200 --wait 0
```

### 1.5 常见错误处理

| 问题 | 原因 | 解决 |
|------|------|------|
| `FAILED` | 需要 root 权限 | `sudo masscan ...` |
| 丢包严重 | 速率过高 | 降低 `--rate` |
| 扫描不到目标 | 网卡/路由问题 | 加 `--adapter` 指定网卡 |
| 端口全部 missed | 网段不对或防火墙拦截 | 确认目标和网络可达性 |

---

## 二、nmap

nmap 是功能最全面的端口扫描器，支持服务检测、操作系统指纹、脚本扫描等。

### 2.1 安装

```bash
# macOS（预装）
nmap --version

# Ubuntu/Debian
sudo apt install nmap

# 源码编译
wget https://nmap.org/dist/nmap-7.95.tar.bz2
bzip2 -cd nmap-7.95.tar.bz2 | tar xvf -
cd nmap-7.95 && ./configure && make -j4 && sudo make install
```

### 2.2 目标指定

| 格式 | 示例 |
|------|------|
| 单个 IP | `nmap 192.168.1.1` |
| IP 列表 | `nmap 192.168.1.1 192.168.1.2` |
| CIDR | `nmap 192.168.1.0/24` |
| 范围 | `nmap 192.168.1.1-254` |
| 主机名 | `nmap scanme.nmap.org` |
| 文件 | `nmap -iL targets.txt` |
| 排除 | `nmap 192.168.1.0/24 --exclude 192.168.1.1` |

### 2.3 扫描类型

| 参数 | 类型 | 说明 |
|------|------|------|
| `-sS` | TCP SYN 扫描 | 半开放扫描，速度快，需 root，**最常用** |
| `-sT` | TCP connect 扫描 | 全连接扫描，无需 root，命中率更高但更慢 |
| `-sU` | UDP 扫描 | 扫描 UDP 端口，慢但必要 |
| `-sN` | TCP Null 扫描 | 绕过防火墙 |
| `-sF` | TCP FIN 扫描 | 绕过防火墙 |
| `-sX` | TCP Xmas 扫描 | 绕过防火墙 |
| `-sA` | ACK 扫描 | 仅检测防火墙过滤规则 |
| `-sI` | 空闲扫描 | 隐藏真实来源 |
| `-sP` | Ping 扫描 | 等同于 `-sn`，只发现主机不扫端口 |
| `-sV` | 版本检测 | 检测服务版本，**最常用** |
| `-sC` | 脚本扫描 | 运行默认脚本，**最常用** |

### 2.4 端口规格

| 参数 | 说明 |
|------|------|
| `-p <port>` | 扫描指定端口，如 `-p 22` 或 `-p 22,80,443` |
| `-p <range>` | 端口范围，如 `-p 1-1000` |
| `-p-` | 所有端口（1-65535） |
| `-p <proto>` | 指定协议，如 `-p udp:53` |
| `-F` | 快速扫描（Top 100 端口） |
| `--top-ports <N>` | 扫描最常见的 N 个端口 |
| `-r` | 顺序扫描（不随机） |

### 2.5 输出格式

| 参数 | 说明 |
|------|------|
| `-oN <file>` | 标准输出（可读文本），**最常用** |
| `-oX <file>` | XML 格式输出 |
| `-oG <file>` | Grepable 格式输出 |
| `-oJ <file>` | JSON 格式输出（nmap 7.80+） |
| `-oA <base>` | 输出所有格式 |
| `-v` / `-vv` | 详细输出 |
| `-d` / `-dd` | 调试信息 |

### 2.6 场景化命令

#### 主机发现

```bash
# 快速发现内网存活主机（不扫端口，速度快）
nmap -sn 192.168.1.0/24

# 不发送 ping，直接假设主机在线
nmap -Pn 192.168.1.0/24

# ARP 发现（同一广播域内最准确）
sudo nmap -PR 192.168.1.0/24
```

#### 端口扫描

```bash
# SYN 扫描常见端口（快，推荐）
sudo nmap -sS -F 192.168.1.1

# TCP connect 扫描（无需 root）
nmap -sT -F 192.168.1.1

# 全端口 SYN 扫描
sudo nmap -sS -p- 192.168.1.1

# 指定端口范围
sudo nmap -sS -p 1-1000,3306,5432,6379,8080,8443 192.168.1.1

# UDP 端口扫描
sudo nmap -sU -p 53,67,68,123,161,500,514,1194 192.168.1.1
```

#### 服务版本检测

```bash
# 轻量版本检测（快）
nmap -sV --version-intensity 1 192.168.1.1

# 标准版本检测（推荐）
nmap -sV 192.168.1.1

# 深度版本检测（慢但最全）
nmap -sV --version-intensity 9 192.168.1.1
```

#### 操作系统检测

```bash
# 基本 OS 检测
sudo nmap -O 192.168.1.1

# 激进 OS 检测（猜测）
sudo nmap -O --osscan-guess 192.168.1.1

# 综合检测
sudo nmap -A -T4 192.168.1.1
```

#### 漏洞评估

```bash
# 使用所有漏洞脚本扫描
nmap --script vuln 192.168.1.1

# 排除 DoS 类漏洞脚本
nmap --script "vuln and not dos" -p- 192.168.1.1

# 常见高危漏洞检测
nmap --script "smb-vuln* and not intrusive" -p 139,445 192.168.1.1
nmap --script "ssl-heartbleed,ssl-poodle,sslv2-drown" -p 443 192.168.1.1
nmap --script "http-csrf,http-sql-injection,http-xss*" -p 80,8080 192.168.1.1

# 心脏滴血漏洞
nmap -p 443 --script ssl-heartbleed 192.168.1.1

# SMB 永恒之蓝
nmap --script smb-vuln-ms17-010 -p 445 192.168.1.1
```

#### Web 服务专项

```bash
# HTTP 服务深度探测
nmap -sV -sC -p 80,443,8080,8443 \
    --script http-enum,http-title,http-headers,http-methods,http-robots.txt \
    192.168.1.1

# 检测 HTTPS 配置问题
nmap -sV -p 443 \
    --script ssl-enum-ciphers,ssl-cert,ssl-heartbleed,ssl-poodle \
    192.168.1.1
```

#### 数据库服务

```bash
# MySQL
nmap -sV -sC -p 3306 \
    --script mysql-info,mysql-enum,mysql-empty-password,mysql-brute \
    192.168.1.1

# PostgreSQL
nmap -sV -sC -p 5432 \
    --script pgsql-info,postgres-brute \
    192.168.1.1

# MongoDB
nmap -sV -sC -p 27017 \
    --script mongodb-info,mongodb-brute \
    192.168.1.1

# Redis
nmap -sV -sC -p 6379 \
    --script redis-info,redis-brute \
    192.168.1.1
```

#### 绕过防火墙

```bash
# 分片包扫描
sudo nmap -f -sS 192.168.1.1

# 诱饵扫描（-D 后面跟诱饵 IP，ME 是你的真实 IP）
nmap -D 192.168.1.100,192.168.1.101,ME -sS -p 80 192.168.1.1

# 空闲扫描（利用第三方空闲主机）
nmap -sI zombie_host 192.168.1.1

# 伪造源端口
sudo nmap -sS -g 53 192.168.1.1

# Null/FIN/Xmas 扫描（绕过某些防火墙）
sudo nmap -sN -p 80 192.168.1.1
sudo nmap -sF -p 80 192.168.1.1
sudo nmap -sX -p 80 192.168.1.1
```

#### 防火墙/IDS 检测

```bash
# ACK 扫描（检测防火墙规则）
sudo nmap -sA -p 80 192.168.1.1
# open      = 无防火墙，端口直接可达
# filtered  = 有防火墙过滤

# 检测是否有防火墙
nmap --script firewalk --traceroute 192.168.1.1

# 路径追踪
sudo nmap --traceroute -p 80 192.168.1.1
```

#### 性能调优

```bash
# 极限速度（可能丢包）
sudo nmap -T5 -sS -p- --max-parallelism 500 --max-rate 100000 192.168.1.1

# 稳定快速（推荐日常使用）
nmap -T4 -sV -sC -p- -oA scan 192.168.1.1

# 低带宽限速
nmap -T2 --max-rate 10k -sS 192.168.1.1

# 长超时（高延迟网络）
sudo nmap -sS --max-scan-delay 30s -p- 192.168.1.1
```

#### 报告生成

```bash
# 同时输出所有格式
nmap -sV -sC -p- -A -oA full_report 192.168.1.1

# 生成 HTML 报告
nmap -sV -oX scan.xml 192.168.1.1
xsltproc scan.xml -o scan.html
```

### 2.7 时间模板

| 模板 | 名称 | 场景 |
|------|------|------|
| `-T0` | 偏执（Paranoid） | IDS 规避，每 5 分钟一个包 |
| `-T1` | 鬼祟（Sneaky） | IDS 规避，每 15 秒一个包 |
| `-T2` | 礼貌（Polite） | 降低资源消耗 |
| `-T3` | 正常（Normal） | **默认** |
| `-T4` | 激进（Aggressive） | **常用**，适合快速扫描 |
| `-T5` | 疯狂（Insane） | 极限速度，可能丢包 |

### 2.8 NSE 脚本分类

| 类别 | 说明 |
|------|------|
| `auth` | 认证绕过测试 |
| `broadcast` | 广播发现 |
| `brute` | 暴力破解 |
| `default` | 默认脚本（-sC 使用） |
| `discovery` | 服务发现 |
| `dos` | 拒绝服务测试（慎用） |
| `exploit` | 利用漏洞测试 |
| `fuzzer` | 模糊测试 |
| `intrusive` | 侵入性脚本 |
| `malware` | 恶意软件检测 |
| `safe` | 安全脚本 |
| `vuln` | 漏洞检测 |

> [!tip]
> 查看所有脚本：`ls /usr/share/nmap/scripts/`  
> 搜索脚本：`nmap --script-help "keyword"`

---

## 三、实战组合技

### 3.1 快速资产梳理 → 精细探测

```bash
# 第一步：masscan 快速发现开放端口
sudo masscan -p1-10000 10.0.0.0/24 --rate=100000 -oJ masscan.json

# 第二步：提取端口列表给 nmap
ports=$(cat masscan.json | jq -r '.[].ports[].port' | sort -u | paste -sd,)
nmap -sV -sC -p $ports 10.0.0.0/24 -oA detail_scan
```

### 3.2 全端口版本 + 漏洞检测

```bash
# 一键综合扫描（适用于单目标）
nmap -sV -sC -O -p- -A --script vuln -oA full_vuln 10.0.0.1
```

### 3.3 批量目标处理

```bash
# 对多个目标同时扫描
nmap -sV -sC -iL targets.txt -oA batch_scan

# Grepable 格式快速筛选
nmap -sV -oG - 192.168.1.0/24 | grep "22/open" | cut -d' ' -f2
```

---

## 四、场景对照表

| 场景 | 推荐命令 |
|------|---------|
| **内网快速发现存活主机** | `nmap -sn 192.168.1.0/24` |
| **内网资产端口梳理（快）** | `sudo masscan 192.168.1.0/24 -p1-10000 --rate=50000 -oJ scan.json` |
| **内网资产详细服务探测** | `nmap -sV -sC -p- -A -T4 -oA result 192.168.1.0/24` |
| **公网单 IP 全端口** | `sudo masscan 1.2.3.4 -p1-65535 --rate=100000 -oJ full.json` |
| **公网单服务深度检测** | `nmap -sV -sC -p 80,443 -A -T4 target` |
| **批量目标快速扫描** | `sudo masscan -iL targets.txt -p22,80,443 --rate=50000 -oJ batch.json` |
| **批量目标深度扫描** | `nmap -sV -sC -iL targets.txt -oA batch` |
| **漏洞评估（单目标）** | `nmap --script vuln -p- -A -oA vulnscan target` |
| **Web 应用专项** | `nmap -sV -sC -p 80,443,8080 --script http-enum,http-title,http-vuln* target` |
| **数据库服务检测** | `nmap -sV -sC -p 3306,5432,27017 --script mysql*,postgres*,mongodb* target` |
| **绕过防火墙扫描** | `sudo nmap -sS -f -D ME,1.2.3.4 -g 53 -p- target` |
| **内网横向渗透** | `nmap -sS -sC -p 139,445,3389,5985 -A -T4 -oA lateral 192.168.1.0/24` |
| **互联网测绘抽样** | `sudo masscan -iR 10000 -p80,443 --rate=100000 -oJ random.json` |

---

## 五、输出格式解析

### masscan JSON

```bash
# 提取 IP 和端口
cat scan.json | jq -r '.[] | .ip + ":" + (.ports | map(.port) | join(","))'

# 统计开放端口 Top N
cat scan.json | jq -r '.[].ports[].port' | sort | uniq -c | sort -rn | head -10

# 导出为端口列表（给 nmap 用）
cat scan.json | jq -r '.[].ports[].port' | sort -u | paste -sd,
```

### nmap Grepable

```bash
# 提取开放端口的主机
grep "Open" result.gnmap | cut -d' ' -f2

# 提取 SSH 开放的主机
grep "22/open" result.gnmap | cut -d' ' -f2
```

---

## 六、常见服务端口速查表

| 服务 | 端口 |
|------|------|
| SSH | 22 |
| HTTP | 80 |
| HTTPS | 443 |
| FTP | 21 |
| SMB | 139, 445 |
| MySQL | 3306 |
| MSSQL | 1433 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| MongoDB | 27017 |
| RDP | 3389 |
| VNC | 5900 |
| DNS | 53 |
| SNMP | 161 |
| SMTP | 25, 465, 587 |
| IMAP | 143, 993 |
| LDAP | 389, 636 |
| Docker | 2375, 2376 |
| Kubernetes | 6443, 10250 |
| ZooKeeper | 2181 |
| Kafka | 9092 |
| Consul | 8500 |

---

## 七、黄金组合

> [!tip]
> **日常使用中记住两个黄金组合即可**：
> - 快速发现：`masscan --rate=100000 -oJ scan.json <targets>`
> - 深度探测：`nmap -sV -sC -p <open_ports> -oA result <target>`

---

## 八、安全与法律声明

> [!warning]
> **务必确保扫描行为已获得授权**。未经授权的端口扫描在大多数国家和地区属于违法行为。互联网测绘类扫描尤其需要明确授权范围。
