# 2.2 HTTPS 请求优化分析

## 2.2.1 请求阶段分析

A complete HTTPS request without connection reuse requires 5 stages: DNS lookup, TCP handshake, SSL handshake, server processing, and content transfer.

A typical HTTPS request (using TLS 1.2) requires approximately 5 RTTs: 1 RTT for DNS lookup + 1 RTT for TCP handshake + 2 RTTs for SSL handshake + 1 RTT for HTTP content transfer.

RTT (Round-Trip Time) is a key metric for evaluating network latency. For example, if the RTT from Beijing to Los Angeles is 190ms, accessing a service in LA would take approximately: 4 x 190ms + backend processing time. The optimization focus should be on reducing RTT and SSL computational overhead.

## 2.2.2 各阶段耗时分析

You can use curl's -w parameter for detailed latency analysis:

```
time_namelookup:  %{time_namelookup}\n
time_connect:     %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_redirect:    %{time_redirect}\n
time_pretransfer: %{time_pretransfer}\n
time_starttransfer: %{time_starttransfer}\n
time_total:       %{time_total}\n
```

**Table 2-2: curl Internal Latency Variables**

| Variable | Description |
|----------|-------------|
| time_namelookup | DNS resolution time |
| time_connect | TCP handshake completion time |
| time_appconnect | TLS handshake completion time |
| time_redirect | Total redirection time |
| time_starttransfer | Time to first byte |
| time_total | Total request time |

**Table 2-3: HTTPS Request Time Calculation**

| Time | Formula |
|------|---------|
| DNS lookup | time_namelookup |
| TCP handshake | time_connect - time_namelookup |
| SSL handshake | time_appconnect - time_connect |
| Server processing | time_total - time_starttransfer |
| TTFB | time_starttransfer |
| Total | time_total |

## 2.2.3 HTTPS 的优化总结

Key optimization strategies include:

- **DNS optimization**: Pre-fetch DNS resolution to eliminate 1 RTT
- **Content compression**: Reduce transfer size
- **SSL optimization**: Upgrade to TLS 1.3 (reduces SSL RTT from 2 to 1)
- **Transport optimization**: Upgrade congestion control algorithms (e.g., BBR over CUBIC)
- **Network optimization**: Use commercial acceleration services
- **Protocol upgrade**: Move to HTTP/2, then HTTP/3 (QUIC)
