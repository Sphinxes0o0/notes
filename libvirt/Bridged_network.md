# Bridged network
A bridged network shares a real Ethernet device with virtual machines (VMs).
Each VM can bind directly to any available IPv4 or IPv6 addresses on the LAN, 
just like a physical computer. 

Bridging offers the best performance and the least headache out of the libvirt network types.

## Limitations
The libvirt server must be connected to the LAN via Ethernet. 
If it is connected wirelessly, a Routed network or NAT-based network are the only options.

### Limitations for dedicated servers

A bridge is only possible when there are enough IP addresses to allocate one per VM. 
This is not a problem for IPv6, as hosting providers usually provide many free IPv6 addresses.However, extra IPv4 addresses are rarely free. 
If you only have one public IPv4 address (and need to serve clients over IPv4), 
either buy more IPv4 addresses or create a NAT-based network.

Hosting providers often only allow the MAC address of the server to bind to IP addresses on the LAN, which prevents bridging. 
Your provider may let you rent a private VLAN that allows VMs to bind directly to IP addresses, 
but if this is too costly then consider a Routed network.

## Initial steps

In this example:

- The server has an Ethernet device called `eth0`.
- VMs share `eth0`, which is enslaved into a bridge called `br0`.
- The hosting provider has allocated two address blocks (see CIDR notation):
    - one public IPv4 address block (`203.0.113.160/29`)
    - one public IPv6 address block (`2001:db8::/64`)
    
- The server binds statically to `203.0.113.166` and `2001:db8::1`.
- VMs can bind to any available IPv4 and IPv6 addresses in the allocated blocks.

Identify the MAC address of the Ethernet device for later.

```bash
# ip address show dev eth0 | awk '$1=="link/ether" {print $2}'
19:7c:3b:92:ec:ee
```

For performance and security reasons, disable netfilter for bridges. Create /etc/sysctl.d/bridge.conf with these contents:
```conf
net.bridge.bridge-nf-call-ip6tables=0
net.bridge.bridge-nf-call-iptables=0
net.bridge.bridge-nf-call-arptables=0
```

Create `/etc/udev/rules.d/99-bridge.rules` with the following contents. 
This udev rule applies the sysctl settings above when the bridge module is loaded.
(If using Linux kernel 3.18 or later, change `KERNEL=="bridge"` to `KERNEL=="br_netfilter"`.)

```bash
ACTION=="add", SUBSYSTEM=="module", KERNEL=="bridge", RUN+="/sbin/sysctl -p /etc/sysctl.d/bridge.conf"
```











