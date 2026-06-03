# 4.1 负载均衡与代理

This section covers load balancing and proxy concepts from the book "Deep Dive into High Availability System Principles and Design."

**Overview**

When discussing load balancing, "Load Balancer" and "Proxy" are often used interchangeably. The high-level architecture shows clients sending requests through a load balancer to backend servers. Key responsibilities include service discovery, health checks, and load distribution.

**Benefits of Load Balancing**

Load balancing provides three main advantages: naming abstraction (clients connect through unified access without knowing backend topology), fault tolerance (health checks ensure only healthy servers receive traffic), and cost/performance gains (requests can stay within the same network region).

**Layer 4 Load Balancing**

Layer 4 load balancing isn't strictly limited to the transport layer. It operates across multiple network layers: L2 uses MAC address modification, L3 uses IP address routing, and L4 uses TCP/UDP port modification with NAT. These layers maintain transport protocol connection characteristics.

**Connection Persistence Problem**

A known issue called "impedance mismatch" occurs when clients with different request frequencies share persistent connections to the same backend server. One solution is adding a secondary dispatcher (Layer 7 load balancer) above Layer 4.

**Layer 7 Load Balancing**

Layer 7 load balancers work at the application layer, establishing new transport connections to backends. They can inspect and route based on TLS, HTTP versions (1, 2, 3), HTTP headers/body, and message protocols like gRPC and RESTful APIs.
