# 2.6 Network Congestion Control Principles and Practice

## 2.6.1 Network Congestion Control Principles

This section analyzes congestion control algorithms across internet development stages and discusses optimizing network throughput in high-bandwidth, high-delay environments.

Network throughput closely relates to RTT and bandwidth. Key terms include RTprop (minimum delay between nodes), BtlBw (bottleneck bandwidth), BDP (bandwidth-delay product), and inflight data (sent but unacknowledged packets).

Three operational zones exist: application-limited (below BDP), bandwidth-limited (BDP to buffer capacity), and buffer-limited (exceeding buffer capacity causing packet loss).

Congestion occurs when inflight data persistently deviates from the BDP line. Effective congestion control maintains inflight data in the appropriate range.

## 2.6.2 Early Congestion Control Aimed at Convergence

Early internet congestion control used packet loss as the control signal. Senders maintain a congestion window (cwnd), starting with slow start, increasing until packet loss triggers congestion avoidance. This approach suited early low-bandwidth, shallow-buffer networks but became inadequate as networks evolved with deeper buffers and longer paths.

## 2.6.3 Modern Congestion Control Aimed at Maximizing Efficiency

Modern algorithms like BBR aim to maximize network efficiency by fully utilizing link bandwidth and router buffers rather than merely avoiding collapse. The optimal operating point balances minimum RTT (buffers unfilled) against maximum bandwidth (buffers utilized). These conditions cannot be measured simultaneously.

## 2.6.4 BBR Design Principles

BBR abandons packet loss as a congestion signal, instead alternating between bandwidth and delay measurement. The state machine has four states:

- **STARTUP**: Exponential rate increase to find maximum bandwidth
- **DRAIN**: Exponential decrease to empty excess buffer
- **PROBE_BW**: Primary operating state maintaining steady rate while occasionally probing for bandwidth changes
- **PROBE_RTT**: Window reduced to 4 MSS to measure true RTT

## 2.6.5 BBR Performance

Since Linux 4.9, BBR is built into the kernel. Testing under various conditions shows BBR significantly outperforms traditional algorithms (Cubic, Reno, Westwood) in lossy network environments, achieving 160 Mb/s versus under 3 Mb/s for competitors at 1.5% packet loss.
