# FAQ

## 如何定位丢包问题

- 检查哪个NIC在丢包: `netstat -i`
- 确定丢包时间: `perf record -g -a -e skb:kfree_skb`
- 找到丢包位置: https://github.com/pavel-odintsov/drop_watch

## 如何查看Linux系统带宽/流量

- 按NIC查看流量: `ifstat`, `dstat -nf`, 或 `sar -n DEV 1 2`
- 按进程查看流量: `nethogs`
- 按连接查看流量: `iptraf`, `iftop`, 或 `tcptrack`
- 查看流量最多的进程: `sysdig -c topprocs_net`
- 查看流量最多的端口: `sysdig -c topports_server`
- 查看最多连接的服务器端口: `sysdig -c fdbytes_by fd.sport`

## 参考文档

- "Monitoring and Tuning the Linux Networking Stack: Receiving Data"
- "Monitoring and Tuning the Linux Networking Stack: Sending Data"
