# Summary: Layer 4 Load Balancing Technology (四层负载均衡技术)

This chapter covers LVS (Linux Virtual Server), developed by Zhang Wensong in 1998 and integrated into Linux kernel 2.4 in 2004.

**Key Working Modes:**

1. **Direct Routing Mode (DR Mode)** - Modifies MAC addresses at data link layer. Requires VIP binding to loopback interface. Enables "triangle routing" where responses bypass the load balancer. Ideal for asymmetric traffic (10% requests, 90% responses). Limitations include limited monitoring and subnet constraints.

2. **Tunnel Mode** - Encapsulates original IP packets within new IP packets. Supports cross-subnet communication. Requires backend servers to support tunnel protocols like IPIP or GRE. Also inherits triangle routing benefits.

3. **NAT Mode** - Directly modifies destination IP addresses. Load balancer performs DNAT (destination translation) and SNAT (source translation). Both requests and responses pass through the load balancer, making it a potential bottleneck under heavy traffic.

4. **Active-Standby Mode** - Uses Keepalived with VRRP protocol. VIP normally on master node; backup monitors and takes over on failure. Suffers from 50% idle resources and single point of failure risk.

5. **Cluster-Based Mode with Consistent Hashing** - Modern approach using BGP Anycast, distributed consistent hashing, and general-purpose hardware. Allows dynamic scaling without service interruption and better resource utilization.

The chapter concludes that traditional architectures are transitioning from vendor-specific hardware to software-defined solutions on standard servers.
