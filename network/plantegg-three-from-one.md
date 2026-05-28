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

TCP connection state transitions happen in OS kernel. `accept()` and `close()` don't affect the kernel-level TCP state machine—they only consume resources after connection is established.
