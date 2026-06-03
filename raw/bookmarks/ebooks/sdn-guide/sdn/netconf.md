# NETCONF

## 概述

NETCONF是一种基于XML的交换机配置接口，用于替代CLI、SNMP和其他配置交换机的方法。

## 协议结构

NETCONF通过RPC与交换机通信，包含四层：

### Layer 1 - Secure Transport

提供与交换机的安全通信。NETCONF不指定使用哪种传输协议，因此可以采用SSH、TLS、HTTP和其他协议。

### Layer 2 - Messages

提供传输无关的消息封装格式用于RPC通信，包括`<rpc>`、`<rpc-reply>`和`<notification>`元素。

### Layer 3 - Operations

定义一系列RPC调用方法，可通过Capabilities扩展，例如`<edit-config>`。

### Layer 4 - Content

定义RPC调用的数据内容，包括配置数据和通知数据。

## 参考

- RFC6241
