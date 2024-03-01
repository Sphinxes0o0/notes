# DoIP

Diagnostic On IP---ISO 13400

1. 将IP技术应用到车载网络中，需满足车规需求；
2. 在诊断范畴，DoIP协议定义了从物理层（Physical Layer）到应用层（Application Layer）搭建“通信桥梁”的规则（此处可类似CAN总线的TP层协议ISO 15765-2）

DoIP所在的位置位于七层模型中第三层和第四层, 其中运用到的IP协议：TCP/IP协议、UDP协议。
整个ISO 13400-2协议中定义的内容是规定了搭建“通信渠道”（Tester与ECU之间的通信渠道）的规则。

> TLS是2020版DoIP协议新增添的内容，主要目的是为了保证通信数据的安全性。

DoIP 大致流程:

1) 物理连接（Physically connection）

2) 车辆声明（Vehicle Discovery）

3) 通信建立（Connection Establishment）

4) 诊断通信（Diagnostic Communication）


## 物理连接

车外客户端（Test equipment）用相应的接口卡（IP-Based Network）连接车身边缘节点（DoIP Edge Node GW）。
在 ISO 13400 协议中规定外部诊断设备连接边缘节点，且需用激活线来激活边缘节点的DoIP功能。
物理连接后，通过相应手段获取IP地址，建立通信。


## 车辆声明：

物理连接后，车辆会议广播的形式发送三次车辆声明，声明的信息可以包括：
- VIN
- EID
- GID

如果诊断设备没有获取车辆信息，也可以主动请求（Vehicle Identification request）来获取相应信息

## 通信建立

在DoIP协议中，有Socket概念：Socket一端连接着IP地址，一端连接着Port端口。
并且Socket对于芯片而言是一种资源。因此有激活失效之分。  
在协议中定义了Payload Type （0005/0006）用于激活Socket。
激活后，Socket使能，接下来就可以进行诊断通信。


## 诊断通信
Socket激活后，进行诊断通信.
```bash
  external test equipment                DoIP  Gateway                            ECU
      ===========                           ========                         ==============
 	|                                   |                                  |
 	|                                   |                                  |
 	|                                   |                                  |
 	|         Diag Message request      |                                  |
 ---------  | --------------------------------> |                                  |
 /| A Doip	|                                   |                                  |
  |  Diag	|                                   |                                  |
  |/ Msg	|          Diag Message Ack         |                                  |
 ---------  |  <------------------------------- |                                  |
 	|                                   |                                  |
 	|                                   |                                  |
 	|                                   |        Diag Message request      |
 	|                                   | -------------------------------> |
 	|                                   |                                  |
 	|                                   |        Diag Message Reponse      |
 	|                                   | <------------------------------- |
 	|                                   |                                  |
 	|       Diag Message Reponse        |                                  |
 	| <-------------------------------  |                                  |
 	|                                   |                                  |
 	|                                   |                                  |

```
外部Tester发送诊断请求，网关收到诊断请求后，会给与一个收到答复（Acknowledgement）,用意是告诉Tester，
网关此时已收到诊断请求，与此同时网关将诊断请求（Diagnostic Request）发送至Target ECU。
ECU收到诊断请求，并基于这个请求给与响应。

因此对于Tester而言，一共收到两个响应。
- Diagnostic Message Acknowledgement；
- Diagnostic Message Response；

在DoIP协议中，通过PayLoad Type区分报文帧类型，用于实现不同的具体功能。
但是其具体发送方式都是基于TCP/UDP协议。

上述整个过程，报文的发送方式都是以TCP/IP协议（当然是将传统的TCP/IP协议做了车规级应用），
定义不同的阶段模型、不同的Payload Type应用报文类型，定义合理的机制，来保证Tester与ECU稳健进行诊断通信。


