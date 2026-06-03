# 2.5 HTTPS 加密原理与优化实践

## HTTPS 加密原理

HTTPS 是 HTTP over TLS/SSL 的缩写，通过 TLS/SSL 协议对传输数据进行加密。TLS/SSL 使用非对称加密进行密钥交换，对称加密进行数据传输。

## HTTPS 优化实践

### 1. TLS 1.3 升级

TLS 1.3 相比 TLS 1.2 有以下优势：
- 握手过程从 2-RTT 减少到 1-RTT
- 移除不安全的加密算法
- 前向保密（Forward Secrecy）成为必须

### 2. 证书优化

- 使用 ECC 证书替代 RSA 证书（更小、更快）
- 启用 OCSP Stapling 避免客户端额外查询
- 合理设置证书链深度

### 3. 会话复用

- Session ID：服务端保存会话状态
- Session Ticket：客户端保存会话状态
- 减少握手次数，降低延迟

### 4. HTTP/2 和 HTTP/3

- HTTP/2：多路复用，头部压缩
- HTTP/3：基于 QUIC，更低的连接延迟
