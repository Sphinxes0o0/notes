# libvirt Networking Handbook

This guide demonstrates the most common aspects of libvirt networking, \
whether running virtual machines (VMs) on a dedicated server or within a home lab.

## How to choose a network type

On a dedicated server — where VMs often need to be publicly accessible — 
a `Bridged network` is ideal and allows each VM to bind to its own public IPv4 and IPv6 addresses.

If bridging is not possible, create a `Routed network`. 
If the server has limited public IPv4 addresses, a `NAT-based network` 
that forwards incoming connections may be the only option.

Inside an intranet or home lab, a `NAT-based network` gives VMs outbound network access. 
If VMs are running services that must be accessible from other systems on the LAN, 
create a `Bridged network` (for an Ethernet connected libvirt host) or a `Routed network` (for a wirelessly connected libvirt host).

If you want to prevent libvirt from automatically inserting iptables rules,
create a `Bridged network`, Custom routed network, or Custom `NAT-based network`.