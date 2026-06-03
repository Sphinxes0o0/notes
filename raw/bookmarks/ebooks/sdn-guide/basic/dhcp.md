# DHCP/DNS

## DHCP

DHCP（动态主机配置协议）动态分配IP地址给主机，使用UDP数据包，端口67和68。它使用租约概念，IP地址有效期因用户连接需求而异。DHCP可以分配动态和静态地址，后者适用于需要固定IP的永久设备（如Web服务器）。

## DNS

DNS（域名系统）将域名解析为IP地址并处理电子邮件路由信息，通过递归查询工作。从最近的DNS服务器开始，查询向上传播直到解析。

- 端口：UDP 53
- 功能：通过gethostbyname()和gethostbyaddr()库调用访问

### FQDN（完全限定域名）

包含完整域路径的完整主机名，提供精确的主机位置识别。

### 资源记录

- A: IP地址查询
- PTR: IP到域名的反向查询
- CNAME: 规范名称/别名
- HINFO: 主机CPU和操作系统信息
- MX: 邮件交换记录
- NS: 名称服务器地址

### 缓存

名称服务器维护缓存以减少DNS流量。

### 协议选择

DNS同时支持TCP和UDP的53端口。UDP处理大多数查询，TCP用于数据超过大小限制或主/从服务器区域传输时。

## 示例

k8s.io的正向DNS查询返回A记录：23.236.58.218

23.236.58.218的反向查询返回：218.58.236.23.bc.googleusercontent.com

## FAQ

**dnsmasq "bad DHCP host name"问题：** 由2.67之前版本的数字前缀主机名引起。2.67版本解决，允许数字开头的主机名（RFC-1123）。

## 图片

![DHCP会话图](https://upload.wikimedia.org/wikipedia/commons/2/28/DHCP_session_en.svg)
