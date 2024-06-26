# TCP

## 三次握手与四次挥手

### 三次握手
* 第一次握手：
client首先向server的TCP发送一个连接请求报文，这个特殊的报文不含应用层数据，其首部中同步位SYN被设置为1；
另外，会随机产生一个起始序号seq=x(连接请求报文不携带数据，但要消耗一个序号).

* 第二次握手：
server的收到TCP连接请求报文后，如果同意建立连接，就向client发回确认，并为该TCP连接分配TCP缓存和变量；
在回复报文中，SYN和ACK位都被设置为1，确认号字段值为ack=x+1,并且server随机产生起始序号seq=y. 确认包同样不包含应用层数据。

* 第三次握手：
当client收到确认报文后，向server给出确认，同时在自己的系统上为该连接分配缓存和变量；
这个报文的确认为ACK被设置为1，序号段被设置为seq=x+1,确认号字段ack=y+1. 该报文可以携带数据，如果不携带数据则不消耗序号。 
理想状态下，TCP连接一旦建立，在通信双方中的任何一方主动关闭连接之前，TCP 连接都将被一直保持下去。
因为TCP提供全双工通信，因此双方任何时候都可以发送数据。

### 四次挥手

* 第一次挥手：
client准备关闭连接，就向其TCP发送一个连接释放报文，并停止再发送数据，主动关闭TCP连接。
该报文的FIN标志位被设置为1，seq=u,它等于前面已经发送过的数据的最后一个字节的序号加1。

* 第二次挥手：
server收到连接释放报文后即发出确认，确认号是ack=u+1,序号为v,等于它前面已经发送过的数据的最后一个字节序号加1.
此时client到server这个方向的连接就释放了，TCP处于半关闭状态。ACK=1，seq=v,ack=u+1

* 第三次挥手：
若server已经没有要向client发送的数据，就通知TCP释放连接，此时发出FIN=1，确认号ack= u+1,序号seq =w,已经发送过的数据最后一个字节加1。
确认为ACK=1. (FIN = 1, ACK=1,seq = w, ack =u+1) 第四次挥手：client收到连接释放报文后，必须发出确认。
在确认报文中，确认位ACK=1，序号seq=u+1,确认号ack=w+1. 此时连接还没有释放掉，必须经过实践等待计时器设置的时间2MSL(Max Segment Lifetime)后，
client才进入连接关闭状态。


## Q & A

### 二次握手可以吗？

采用三次握手是为了防止失效的连接请求报文再次传到server，可能因此产生错误。

当网络波动时，假设客户端发送的连接请求正常达服务方，服务方建立连接的应答未能到达客户端：
则客户方要重新发送连接请求，若采用二次握手，服务方收到客服端重传的请求连接后，会以为是新的请求，就会发送同意连接报文，并新开进程提供服务，这样会造成服务方资源的无谓浪费。 
如果只采用一次的话，客户端不知道服务端是否已经收到自己发送的数据，则会不断地发送数据。
为了保证服务端能收接受到客户端的信息并能做出正确的应答而进行前两次(第一次和第二次)握手，
为了保证客户端能够接收到服务端的信息并能做出正确的应答而进行后两次(第二次和第三次)握手

### 主动方要等待２MSL后才关闭连接?
保证TCP协议的全双工连接能够可靠关闭． 
主要为了确保对方能收到ACK, 如果client直接CLOSED了，那么由于IP协议的不可靠性或其它网络原因，导致server没有收到client最后回复的ACK。
server在超时之后继续发送FIN，此时由于client已经CLOSED了，就找不到与重发的FIN对应的连接，server此时就会收到RST（而不是期待的ACK），系统会认为是连接错误把问题报告给上层。
所以，client不能直接进入CLOSED，而是保持2MSL的状态,如果这个时间内又收到了server的关闭请求时则马上重传，否则说明server已经受到确认包则可以关闭.

## TCP 拥塞控制

TODO
### 滑动窗口

TODO

### Q: 可靠性如何保证 ?
在TCP的连接中，数据流必须以正确的顺序送达对方。
TCP的可靠性是通过顺序编号和确认（ACK）来实现的。TCP在开始传送一个段时，为准备重传而首先将该段插入到发送队列之中，同时启动时钟。
其后，如果收到了接受端对该段的ACK信息，就将该段从队列中删去。如果在时钟规定的时间内，ACK未返回，那么就从发送队列中再次送出这个段。
TCP在协议中就对数据可靠传输做了保障，握手与断开都需要通讯双方确认，数据传输也需要双方确认成功，
在协议中还规定了：分包、重组、重传等规则；
而UDP主要是面向不可靠连接的，不能保证数据正确到达目的地。

