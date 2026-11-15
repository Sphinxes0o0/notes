---
title: "plantegg: 举三反一 (Deriving One from Three)"
description: "Two learning approaches:"
---
# plantegg: 举三反一 (Deriving One from Three)

## Core Method
Two learning approaches:
- **Knowledge efficiency**: Theoretical understanding → intuitive application
- **Engineering efficiency**: Repeated practice + case studies to reinforce theory

Most people need concrete examples to deeply understand theoretical concepts.

## TCP CLOSE_WAIT Diagnosis Example

### Problem
Server showed CLOSE_WAIT count equal to `somaxconn`. Adjusting somaxconn changed the count accordingly.

### Theory Application
CLOSE_WAIT means the passive closer (server) is waiting for application to call `close()`. The fact that CLOSE_WAIT = somaxconn suggested no `accept()` calls were being made either.

### Root Cause
OS `open files` limit was 1024, preventing new connections. TCP handshakes completed (ESTABLISHED) without application involvement, but applications couldn't `accept()` → `close()`.

## Key Insight
> "三次握手成功就变成 ESTABLISHED 了，不需要用户态来accept"

TCP handshakes are processed by the kernel before the application accepts the connection. `accept()` retrieves an established connection from the accept queue. Application shutdown does affect TCP state: a graceful close can send FIN, and a connection in CLOSE_WAIT proceeds toward LAST-ACK when its sending side is closed. See [RFC 9293, connection closing](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.6). The case above illustrates a resource-limit diagnosis; CLOSE_WAIT counts alone do not prove that the accept queue is full.
