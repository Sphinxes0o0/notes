# Linux Kernel BSD Socket Layer Analysis

## Table of Contents
1. [Core Socket Structures](#1-core-socket-structures)
2. [Socket Creation](#2-socket-creation)
3. [inet_create()](#3-inet_create)
4. [inet_bind()](#4-inet_bind)
5. [inet_listen()](#5-inet_listen)
6. [inet_accept()](#6-inet_accept)
7. [inet_connect()](#7-inet_connect)
8. [Send/Receive Paths](#8-sendreceive-paths)
9. [Socket File Operations](#9-socket-file-operations)
10. [Socket Timeout and Blocking](#10-socket-timeout-and-blocking)
11. [Memory Management](#11-memory-management)

---

## 1. Core Socket Structures

### 1.1 `struct socket` (VFS Socket Representation)

**Location:** `/Users/sphinx/github/linux/include/linux/net.h:116-128`

```c
struct socket {
    socket_state    state;      /* Socket state (SS_*) */
    short           type;      /* Socket type (SOCK_STREAM, SOCK_DGRAM, etc.) */
    unsigned long   flags;     /* Socket flags (SOCK_NOSPACE, etc.) */
    struct file    *file;      /* File back pointer for garbage collection */
    struct sock    *sk;        /* Internal networking protocol socket */
    const struct proto_ops *ops; /* Protocol-specific socket operations */
    struct socket_wq wq;       /* Wait queue for several uses */
};
```

**Socket States** (`/Users/sphinx/github/linux/include/uapi/linux/net.h:48-54`):
```c
typedef enum {
    SS_FREE = 0,           /* not allocated */
    SS_UNCONNECTED,        /* unconnected to any socket */
    SS_CONNECTING,         /* in process of connecting */
    SS_CONNECTED,          /* connected to socket */
    SS_DISCONNECTING       /* in process of disconnecting */
} socket_state;
```

**Socket Types** (`/Users/sphinx/github/linux/include/linux/net.h:63-71`):
```c
enum sock_type {
    SOCK_STREAM    = 1,    /* stream (connection) socket */
    SOCK_DGRAM     = 2,    /* datagram (conn.less) socket */
    SOCK_RAW      = 3,    /* raw socket */
    SOCK_RDM      = 4,    /* reliably-delivered message */
    SOCK_SEQPACKET = 5,   /* sequential packet socket */
    SOCK_DCCP     = 6,    /* Datagram Congestion Control Protocol */
    SOCK_PACKET   = 10,   /* linux specific way of getting packets */
};
```

### 1.2 `struct socket_wq`

**Location:** `/Users/sphinx/github/linux/include/linux/net.h:98-104`

```c
struct socket_wq {
    wait_queue_head_t    wait;      /* Note: wait MUST be first field */
    struct fasync_struct *fasync_list;
    unsigned long        flags;     /* SOCKWQ_ASYNC_NOSPACE, etc */
    struct rcu_head      rcu;
};
```

### 1.3 `struct sock_common` (Kernel Internal Socket - Part 1)

**Location:** `/Users/sphinx/github/linux/include/net/sock.h:151-212`

```c
struct sock_common {
    /* Address pair */
    union {
        __addrpair skc_addrpair;
        struct {
            __be32 skc_daddr;      /* Destination address (remote) */
            __be32 skc_rcv_saddr;  /* Receive source address (local) */
        };
    };

    /* Hash (for socket lookup) */
    union {
        unsigned int skc_hash;
        __u16 skc_u16hashes[2];
    };

    /* Port pair - skc_dport && skc_num must be grouped */
    union {
        __portpair skc_portpair;
        struct {
            __be16 skc_dport;      /* Destination port (remote) */
            __u16  skc_num;        /* Local port number */
        };
    };

    unsigned short   skc_family;      /* Address family (AF_INET, etc.) */
    volatile unsigned char skc_state; /* TCP state (TCPF_*) */
    unsigned char    skc_reuse:4;    /* Reuse port mode */
    unsigned char    skc_reuseport:1;
    unsigned char    skc_ipv6only:1;
    unsigned char    skc_net_refcnt:1;
    unsigned char    skc_bypass_prot_mem:1;
    int              skc_bound_dev_if; /* Bound device interface index */

    union {
        struct hlist_node skc_bind_node;    /* Bind hash node */
        struct hlist_node skc_portaddr_node;
    };

    struct proto *skc_prot;           /* Protocol callbacks */
    possible_net_t skc_net;

    /* IPv6 addresses (if CONFIG_IPV6) */
#if IS_ENABLED(CONFIG_IPV6)
    struct in6_addr skc_v6_daddr;
    struct in6_addr skc_v6_rcv_saddr;
#endif

    atomic64_t skc_cookie;            /* Syncookie magic */

    union {
        unsigned long skc_flags;
        struct sock *skc_listener;    /* request_sock listener */
        struct inet_timewait_death_row *skc_tw_dr;
    };
};
```

### 1.4 `struct sock` (Kernel Internal Socket - Full)

**Location:** `/Users/sphinx/github/linux/include/net/sock.h:360-510` (key fields)

```c
struct sock {
    struct sock_common __sk_common;  /* MUST be first - shared with request_sock */

#define sk_node         __sk_common.skc_node
#define sk_nulls_node   __sk_common.skc_nulls_node
#define sk_refcnt       __sk_common.skc_refcnt
#define sk_tx_queue_mapping __sk_common.skc_tx_queue_mapping
#define sk_hash         __sk_common.skc_hash
#define sk_portpair     __sk_common.skc_portpair
#define sk_num          __sk_common.skc_num
#define sk_dport        __sk_common.skc_dport
#define sk_addrpair     __sk_common.skc_addrpair
#define sk_daddr        __sk_common.skc_daddr
#define sk_rcv_saddr    __sk_common.skc_rcv_saddr
#define sk_family       __sk_common.skc_family
#define sk_state        __sk_common.skc_state
#define sk_reuse        __sk_common.skc_reuse
#define sk_reuseport    __sk_common.skc_reuseport
#define sk_ipv6only     __sk_common.skc_ipv6only
#define sk_bound_dev_if __sk_common.skc_bound_dev_if
#define sk_bind_node    __sk_common.skc_bind_node
#define sk_prot         __sk_common.skc_prot
    /* ... more accessors ... */

    /* Cache line group: sock_write_rx */
    atomic_t          sk_drops;           /* Drop count */
    __s32            sk_peek_off;         /* Peek offset */
    struct sk_buff_head sk_error_queue;  /* Error queue */
    struct sk_buff_head sk_receive_queue; /* Receive queue (incoming data) */
    struct {
        atomic_t rmem_alloc;              /* Received memory allocated */
        int     len;
        struct sk_buff *head;
        struct sk_buff *tail;
    } sk_backlog;

    /* Cache line group: sock_read_rx */
    struct dst_entry __rcu *sk_rx_dst;
    int               sk_rx_dst_ifindex;
    u32               sk_rx_dst_cookie;

    u8               sk_userlocks;       /* SOCK_BINDPORT_LOCK, etc */
    int               sk_rcvbuf;          /* Receive buffer size */
    struct sk_filter __rcu *sk_filter;    /* BPF socket filter */
    union {
        struct socket_wq __rcu *sk_wq;
        struct socket_wq *sk_wq_raw;
    };

    void (*sk_data_ready)(struct sock *sk); /* Callback when data arrives */
    long              sk_rcvtimeo;       /* Receive timeout */
    int               sk_rcvlowat;       /* Receive low watermark */

    /* Cache line group: sock_read_rxtx */
    int               sk_err;             /* Last error */
    struct socket     *sk_socket;         /* Back pointer to socket */
    struct mem_cgroup *sk_memcg;          /* Memory cgroup */
    struct xfrm_policy __rcu *sk_policy[2]; /* IPsec policies */

    /* Cache line group: sock_write_rxtx */
    socket_lock_t     sk_lock;             /* Synchronization lock */
    u32               sk_reserved_mem;     /* Reserved memory */
    int               sk_forward_alloc;     /* Forward allocated memory */
    u32               sk_tsflags;          /* Timestamp flags */

    /* Cache line group: sock_write_tx */
    int               sk_write_pending;     /* Write pending counter */
    atomic_t          sk_omem_alloc;        /* Outgoing memory allocation */
    int               sk_err_soft;          /* Soft error */
    int               sk_wmem_queued;       /* Queued write memory */
    refcount_t        sk_wmem_alloc;        /* Write memory allocation */
    unsigned long     sk_tsq_flags;         /* TCP send queue flags */
    union {
        struct sk_buff *sk_send_head;      /* Send queue head */
        struct rb_root  tcp_rtx_queue;      /* TCP retransmit queue */
    };
    struct sk_buff_head sk_write_queue;     /* Write queue */
    struct page_frag  sk_frag;              /* Page fragment */
    union {
        struct timer_list sk_timer;         /* Generic timer */
        struct timer_list tcp_retransmit_timer;
        struct timer_list mptcp_retransmit_timer;
    };
    unsigned long     sk_pacing_rate;        /* Pacing rate (bytes/sec) */
    atomic_t          sk_zckey;
    atomic_t          sk_tskey;

    /* Cache line group: sock_read_tx */
    u32               sk_dst_pending_confirm;
    u32               sk_pacing_status;
    unsigned long     sk_max_pacing_rate;
    long              sk_sndtimeo;           /* Send timeout */
    u32               sk_priority;           /* Priority */
    u32               sk_mark;              /* Skb mark */
    kuid_t            sk_uid;                /* User ID */
    u16               sk_protocol;           /* Protocol (IPPROTO_*) */
    u16               sk_type;               /* Socket type */
    struct dst_entry __rcu *sk_dst_cache;    /* Destination cache */
    netdev_features_t sk_route_caps;        /* Route capabilities */
};
```

### 1.5 `struct sk_buff` (Socket Buffer)

**Location:** `/Users/sphinx/github/linux/include/linux/skbuff.h:885-1103`

```c
struct sk_buff {
    /* First two members: must be first to match sk_buff_head */
    union {
        struct {
            struct sk_buff *next;           /* Next buffer in queue */
            struct sk_buff *prev;           /* Previous buffer in queue */
            union {
                struct net_device *dev;     /* Device (receiving or sending) */
                unsigned long dev_scratch;  /* Scratch area for protocols */
            };
        };
        struct rb_node  rbnode;             /* RB tree node (defrag, TCP) */
        struct list_head list;              /* List node */
        struct llist_node ll_node;          /* Lockless list node */
    };

    struct sock *sk;                        /* Socket this belongs to */

    union {
        ktime_t  tstamp;                   /* Timestamp */
        u64      skb_mstamp_ns;            /* Earliest departure time */
    };

    char cb[48] __aligned(8);              /* Control buffer (per-layer private) */

    union {
        struct {
            unsigned long _skb_refdst;      /* Destination reference */
            void (*destructor)(struct sk_buff *skb); /* Destructor */
        };
        struct list_head tcp_tsorted_anchor; /* TCP TSORT queue */
    };

    /* Packet length info */
    unsigned int len;                       /* Total length (includes data_len) */
    unsigned int data_len;                  /* Data length (fragments) */
    __u16        mac_len;                  /* MAC header length */
    __u16        hdr_len;                  /* Header length (clone) */

    __u16        queue_mapping;            /* Queue mapping */

    /* Cloning flags */
    __u8 __cloned_offset[0];
    __u8  cloned:1;                       /* Cloned flag */
    __u8  nohdr:1;                        /* No headers */
    __u8  fclone:2;                       /* Clone type */
    __u8  peeked:1;                        /* Peeked flag */
    __u8  head_frag:1;                     /* Head from page pool */
    __u8  pfmemalloc:1;                    /* PFMEMALLOC page */
    __u8  pp_recycle:1;                    /* Page pool recycle */

    /* Group: headers (copied with single memcpy) */
    struct_group(headers,
        __u8 __pkt_type_offset[0];
        __u8  pkt_type:3;                  /* PACKET_* type */
        __u8  ignore_df:1;
        __u8  dst_pending_confirm:1;
        __u8  ip_summed:2;                  /* CHECKSUM_* */
        __u8  ooo_okay:1;

        __u8  tstamp_type:2;               /* Timestamp type */
        __u8  tc_at_ingress:1;
        __u8  tc_skip_classify:1;
        __u8  remcsum_offload:1;
        __u8  csum_complete_sw:1;
        __u8  csum_level:2;
        __u8  inner_protocol_type:1;

        __u8  l4_hash:1;
        __u8  sw_hash:1;
        __u8  wifi_acked_valid:1;
        __u8  wifi_acked:1;
        __u8  no_fcs:1;
        __u8  encapsulation:1;
        __u8  encap_hdr_csum:1;
        __u8  csum_valid:1;

        __u8  ndisc_nodetype:2;
        __u8  ipvs_property:1;
        __u8  nf_trace:1;
        __u8  offload_fwd_mark:1;
        __u8  offload_l3_fwd_mark:1;
        __u8  redirected:1;
        __u8  from_ingress:1;
        __u8  nf_skip_egress:1;
        __u8  decrypted:1;
        __u8  slow_gro:1;
        __u8  csum_not_inet:1;
        __u8  unreadable:1;

        __u16 tc_index;
    );

    u16  alloc_cpu;

    /* Checksum */
    union {
        __wsum csum;
        struct {
            __u16 csum_start;
            __u16 csum_offset;
        };
    };

    __u32 priority;                         /* Packet priority */
    int   skb_iif;                         /* Receive interface index */
    __u32 hash;                             /* Hash value */

    /* VLAN */
    union {
        __u32 vlan_all;
        struct {
            __be16 vlan_proto;
            __u16 vlan_tci;
        };
    };

    union {
        unsigned int napi_id;
        unsigned int sender_cpu;
    };

    __u32 secmark;                         /* Security mark */

    union {
        __u32 mark;
        __u32 reserved_tailroom;
    };

    /* Inner protocol (tunnels) */
    union {
        __be16 inner_protocol;
        __u8   inner_ipproto;
    };

    /* Header offsets */
    __u16 inner_transport_header;
    __u16 inner_network_header;
    __u16 inner_mac_header;

    __be16 protocol;                        /* Protocol (ETH_P_*) */
    __u16 transport_header;                 /* Transport layer header offset */
    __u16 network_header;                  /* Network layer header offset */
    __u16 mac_header;                      /* MAC layer header offset */

    /* These elements must be at the end - see alloc_skb() */
    sk_buff_data_t tail;                   /* Tail pointer */
    sk_buff_data_t end;                    /* End pointer */
    unsigned char *head;                   /* Head pointer */
    unsigned char *data;                   /* Data pointer */
    unsigned int truesize;                 /* True size (including sk_buff) */
    refcount_t    users;                   /* Reference count */

#ifdef CONFIG_SKB_EXTENSIONS
    struct skb_ext *extensions;            /* Extensions */
#endif
};
```

### 1.6 `struct proto_ops` (Protocol Operations)

**Location:** `/Users/sphinx/github/linux/include/linux/net.h:160-226`

```c
struct proto_ops {
    int   family;                          /* AF_INET, AF_INET6, etc. */
    struct module *owner;

    /* Core operations */
    int (*release)(struct socket *sock);
    int (*bind)(struct socket *sock, struct sockaddr_unsized *myaddr, int sockaddr_len);
    int (*connect)(struct socket *sock, struct sockaddr_unsized *vaddr, int sockaddr_len, int flags);
    int (*socketpair)(struct socket *sock1, struct socket *sock2);
    int (*accept)(struct socket *sock, struct socket *newsock, struct proto_accept_arg *arg);
    int (*getname)(struct socket *sock, struct sockaddr *addr, int peer);

    /* Polling and I/O */
    __poll_t (*poll)(struct file *file, struct socket *sock, struct poll_table_struct *wait);
    int (*ioctl)(struct socket *sock, unsigned int cmd, unsigned long arg);
    int (*compat_ioctl)(struct socket *sock, unsigned int cmd, unsigned long arg);
    int (*gettstamp)(struct socket *sock, void __user *userstamp, bool timeval, bool time32);

    /* Listening and shutdown */
    int (*listen)(struct socket *sock, int len);
    int (*shutdown)(struct socket *sock, int flags);

    /* Socket options */
    int (*setsockopt)(struct socket *sock, int level, int optname, sockptr_t optval, unsigned int optlen);
    int (*getsockopt)(struct socket *sock, int level, int optname, char __user *optval, int __user *optlen);

    /* Messaging */
    int (*sendmsg)(struct socket *sock, struct msghdr *m, size_t total_len);
    int (*recvmsg)(struct socket *sock, struct msghdr *m, size_t total_len, int flags);

    /* Memory mapping and splicing */
    int (*mmap)(struct file *file, struct socket *sock, struct vm_area_struct *vma);
    ssize_t (*splice_read)(struct socket *sock, loff_t *ppos, struct pipe_inode_info *pipe, size_t len, unsigned int flags);
    void (*splice_eof)(struct socket *sock);

    /* Peek and state */
    int (*set_peek_off)(struct sock *sk, int val);
    int (*peek_len)(struct socket *sock);

    /* Internal kernel callbacks (sock lock held) */
    int (*read_sock)(struct sock *sk, read_descriptor_t *desc, sk_read_actor_t recv_actor);
    int (*read_skb)(struct sock *sk, skb_read_actor_t recv_actor);
    int (*sendmsg_locked)(struct sock *sk, struct msghdr *msg, size_t size);
    int (*set_rcvlowat)(struct sock *sk, int val);
};
```

### 1.7 `struct proto` (Protocol Structure)

**Location:** `/Users/sphinx/github/linux/include/net/sock.h:1286-1360` (key fields)

```c
struct proto {
    /* Close and destroy */
    void (*close)(struct sock *sk, long timeout);

    /* Connection */
    int (*pre_connect)(struct sock *sk, struct sockaddr_unsized *uaddr, int addr_len);
    int (*connect)(struct sock *sk, struct sockaddr_unsized *uaddr, int addr_len);
    int (*disconnect)(struct sock *sk, int flags);
    struct sock *(*accept)(struct sock *sk, struct proto_accept_arg *arg);

    /* I/O */
    int (*ioctl)(struct sock *sk, int cmd, int *karg);
    int (*init)(struct sock *sk);
    void (*destroy)(struct sock *sk);
    void (*shutdown)(struct sock *sk, int how);

    /* Socket options */
    int (*setsockopt)(struct sock *sk, int level, int optname, sockptr_t optval, unsigned int optlen);
    int (*getsockopt)(struct sock *sk, int level, int optname, char __user *optval, int __user *option);
    void (*keepalive)(struct sock *sk, int valbool);

    /* Messaging */
    int (*sendmsg)(struct sock *sk, struct msghdr *msg, size_t len);
    int (*recvmsg)(struct sock *sk, struct msghdr *msg, size_t len, int flags, int *addr_len);
    void (*splice_eof)(struct socket *sock);

    /* Binding */
    int (*bind)(struct sock *sk, struct sockaddr_unsized *addr, int addr_len);
    int (*bind_add)(struct sock *sk, struct sockaddr_unsized *addr, int addr_len);

    /* Backlog processing */
    int (*backlog_rcv)(struct sock *sk, struct sk_buff *skb);

    /* Hashing and port management */
    int (*hash)(struct sock *sk);
    void (*unhash)(struct sock *sk);
    void (*rehash)(struct sock *sk);
    int (*get_port)(struct sock *sk, unsigned short snum);
    void (*put_port)(struct sock *sk);

    /* Memory */
    void (*release_cb)(struct sock *sk);
    int (*sk_mem_schedule)(struct sock *sk, int size, int type);
    void (*sk_mem_reclaim)(struct sock *sk);
};
```

### 1.8 `struct inet_sock` (INET Socket Extension)

**Location:** `/Users/sphinx/github/linux/include/net/inet_sock.h:218-251`

```c
struct inet_sock {
    struct sock sk;                        /* MUST be first */
#if IS_ENABLED(CONFIG_IPV6)
    struct ipv6_pinfo *pinet6;
    struct ipv6_fl_socklist __rcu *ipv6_fl_list;
#endif

    /* Address accessors (macros) */
#define inet_daddr       sk.__sk_common.skc_daddr
#define inet_rcv_saddr   sk.__sk_common.skc_rcv_saddr
#define inet_dport       sk.__sk_common.skc_dport
#define inet_num         sk.__sk_common.skc_num

    unsigned long    inet_flags;          /* INET_FLAGS_PKTINFO, etc. */
    __be32           inet_saddr;          /* Source address */
    __s16            uc_ttl;              /* Unicast TTL */
    __be16           inet_sport;          /* Source port (host byte order) */
    struct ip_options_rcu __rcu *inet_opt; /* IP options */
    atomic_t         inet_id;             /* ID counter */

    __u8             tos;                   /* Type of service */
    __u8             min_ttl;              /* Minimum TTL */
    __u8             mc_ttl;               /* Multicast TTL */
    __u8             pmtudisc;             /* Path MTU discovery mode */
    __u8             rcv_tos;              /* Receive TOS */
    __u8             convert_csum;         /* Convert checksums */
    int              uc_index;             /* Unicast interface index */
    int              mc_index;             /* Multicast interface index */
    __be32           mc_addr;              /* Multicast address */
    u32              local_port_range;     /* High << 16 | Low for port range */

    struct ip_mc_socklist __rcu *mc_list;  /* Multicast group memberships */
    struct inet_cork_full cork;             /* IP cork info */
};
```

### 1.9 `struct inet_protosw` (Protocol Registration)

**Location:** `/Users/sphinx/github/linux/include/net/protocol.h:79-93`

```c
struct inet_protosw {
    struct list_head list;

    /* Lookup key */
    unsigned short type;                   /* SOCK_STREAM, SOCK_DGRAM, etc. */
    unsigned short protocol;               /* L4 protocol (IPPROTO_TCP, etc.) */

    struct proto *prot;                    /* Protocol callbacks */
    const struct proto_ops *ops;           /* Socket operations */

    unsigned char flags;                   /* INET_PROTOSW_* flags */
};
#define INET_PROTOSW_REUSE    0x01         /* Ports automatically reusable */
#define INET_PROTOSW_PERMANENT 0x02       /* Permanent (unremovable) */
#define INET_PROTOSW_ICSK     0x04        /* Is inet_connection_sock */
```

### 1.10 `struct request_sock` (Incoming Connection Request)

**Location:** `/Users/sphinx/github/linux/include/net/request_sock.h:50-75`

```c
struct request_sock {
    struct sock_common __req_common;

#define rsk_refcnt       __req_common.skc_refcnt
#define rsk_hash         __req_common.skc_hash
#define rsk_listener     __req_common.skc_listener
#define rsk_window_clamp __req_common.skc_window_clamp
#define rsk_rcv_wnd      __req_common.skc_rcv_wnd

    struct request_sock *dl_next;
    u16  mss;                              /* Maximum segment size */
    u8   num_retrans;                      /* Number of retransmits */
    u8   syncookie:1;                      /* SYN cookie enabled */
    u8   num_timeout:7;                    /* Number of timeouts */
    u32  ts_recent;                        /* Timestamp recent */
    struct timer_list rsk_timer;           /* Request timer */
    const struct request_sock_ops *rsk_ops; /* Request operations */
    struct sock *sk;                        /* Established socket */
    struct saved_syn *saved_syn;            /* Saved SYN data */
    u32  secid;                            /* Security ID */
    u32  peer_secid;
    u32  timeout;
};
```

### 1.11 `struct request_sock_queue` (Accept Queue)

**Location:** `/Users/sphinx/github/linux/include/net/request_sock.h:177-190`

```c
struct request_sock_queue {
    spinlock_t rskq_lock;
    u8  rskq_defer_accept;                 /* User waits for data after accept */
    u8  synflood_warned;

    atomic_t qlen;                         /* Queue length */
    atomic_t young;                        /* Young connections count */

    struct request_sock *rskq_accept_head;  /* FIFO head of established */
    struct request_sock *rskq_accept_tail; /* FIFO tail of established */
    struct fastopen_queue fastopenq;       /* TCP Fast Open queue */
};
```

### 1.12 `struct inet_connection_sock` (Connection-Oriented INET Socket)

**Location:** `/Users/sphinx/github/linux/include/net/inet_connection_sock.h:79-120`

```c
struct inet_connection_sock {
    struct inet_sock icsk_inet;

    /* Connection management */
    struct request_sock_queue icsk_accept_queue; /* Accept queue */
    struct inet_bind_bucket *icsk_bind_hash;
    struct inet_bind2_bucket *icsk_bind2_hash;

    /* Timers */
    struct timer_list icsk_delack_timer;   /* Delayed ack timer */
    union {
        struct timer_list icsk_keepalive_timer;
        struct timer_list mptcp_tout_timer;
    };

    /* Retransmission */
    __u32 icsk_rto;                        /* Retransmission timeout */
    __u32 icsk_rto_min;
    __u32 icsk_rto_max;
    __u32 icsk_delack_max;

    /* Congestion control */
    const struct tcp_congestion_ops *icsk_ca_ops;

    /* Address family operations */
    const struct inet_connection_sock_af_ops *icsk_af_ops;

    /* Upper layer protocol */
    const struct tcp_ulp_ops *icsk_ulp_ops;
    void __rcu *icsk_ulp_data;

    unsigned int (*icsk_sync_mss)(struct sock *sk, u32 pmtu);

    /* State */
    __u8 icsk_ca_state:5;
    __u8 icsk_ca_initialized:1;
    __u8 icsk_ca_setsockopt:1;
    __u8 icsk_ca_dst_locked:1;
};
```

### 1.13 `struct tcp_sock` (TCP Socket Extension)

**Location:** `/Users/sphinx/github/linux/include/linux/tcp.h:197-230` (key fields)

```c
struct tcp_sock {
    struct inet_connection_sock inet_conn;  /* MUST be first */

    /* TX read-mostly hotpath */
    u32 max_window;                        /* Max window seen from peer */
    u32 rcv_ssthresh;                      /* Current window clamp */
    u32 reordering;                        /* Packet reordering metric */
    u32 notsent_lowat;                     /* TCP_NOTSENT_LOWAT */
    u16 gso_segs;                          /* GSO segments per packet */
    struct sk_buff *retransmit_skb_hint;   /* Retransmit queue hint */

    /* TXRX read-mostly hotpath */
    u32 tsoffset;                          /* Timestamp offset */
    u32 snd_wnd;                           /* The window we expect to receive */
    u32 mss_cache;                         /* Cached effective MSS */
    u32 snd_cwnd;                          /* Sending congestion window */
    u32 prr_out;                            /* Pkts sent during Recovery */
    u32 lost_out;                           /* Lost packets */
};
```

### 1.14 `struct udp_sock` (UDP Socket Extension)

**Location:** `/Users/sphinx/github/linux/include/linux/udp.h:53-85`

```c
struct udp_sock {
    struct inet_sock inet;                 /* MUST be first */

#define udp_port_hash      inet.sk.__sk_common.skc_u16hashes[0]
#define udp_portaddr_hash  inet.sk.__sk_common.skc_u16hashes[1]
#define udp_portaddr_node  inet.sk.__sk_common.skc_portaddr_node

    unsigned long udp_flags;
    int pending;                            /* Any pending frames? */
    __u8 encap_type;                      /* Encapsulation type */

    __u16 len;                             /* Total length of pending frames */
    __u16 gso_size;                        /* GSO size */

    /* UDP-Lite specific */
    __u16 pcslen;
    __u16 pcrlen;
};
```

---

## 2. Socket Creation

### 2.1 `sock_alloc()` - Allocate a Socket

**Location:** `/Users/sphinx/github/linux/net/socket.c:632-650`

```c
struct socket *sock_alloc(void)
{
    struct inode *inode;
    struct socket *sock;

    inode = new_inode_pseudo(sock_mnt->mnt_sb);
    if (!inode)
        return NULL;

    sock = SOCKET_I(inode);

    inode->i_ino = get_next_ino();
    inode->i_mode = S_IFSOCK | S_IRWXUGO;
    inode->i_uid = current_fsuid();
    inode->i_gid = current_fsgid();
    inode->i_op = &sockfs_inode_ops;

    return sock;
}
```

### 2.2 `__sock_create()` - Create a Socket (Full)

**Location:** `/Users/sphinx/github/linux/net/socket.c:1534-1647`

```c
int __sock_create(struct net *net, int family, int type, int protocol,
                 struct socket **res, int kern)
{
    int err;
    struct socket *sock;
    const struct net_proto_family *pf;

    /* Validate inputs */
    if (family < 0 || family >= NPROTO)
        return -EAFNOSUPPORT;
    if (type < 0 || type >= SOCK_MAX)
        return -EINVAL;

    /* Handle obsolete SOCK_PACKET */
    if (family == PF_INET && type == SOCK_PACKET)
        family = PF_PACKET;

    /* LSM hook */
    err = security_socket_create(family, type, protocol, kern);
    if (err)
        return err;

    /* Allocate socket */
    sock = sock_alloc();
    if (!sock)
        return -ENFILE;

    sock->type = type;

    /* Try loading protocol module if not found */
    if (rcu_access_pointer(net_families[family]) == NULL)
        request_module("net-pf-%d", family);

    /* Get protocol family handler */
    rcu_read_lock();
    pf = rcu_dereference(net_families[family]);
    if (!pf) {
        err = -EAFNOSUPPORT;
        goto out_release;
    }

    if (!try_module_get(pf->owner))
        goto out_release;
    rcu_read_unlock();

    /* Call protocol-specific create */
    err = pf->create(net, sock, protocol, kern);
    if (err < 0)
        goto out_module_put;

    /* Bump module refcnt for socket ops owner */
    if (!try_module_get(sock->ops->owner))
        goto out_module_busy;

    module_put(pf->owner);

    err = security_socket_post_create(sock, family, type, protocol, kern);
    if (err)
        goto out_sock_release;

    *res = sock;
    return 0;
}
```

**Flow:**
```
socket() syscall
      |
      v
__sys_socket()
      |
      v
__sys_socket_create()
      |
      v
sock_create() --> __sock_create()
      |
      +-> security_socket_create()     [LSM hook]
      +-> sock_alloc()                [Allocate socket + inode]
      +-> request_module()             [Load protocol module if needed]
      +-> pf->create()                [Call PF_INET's inet_create()]
      +-> security_socket_post_create() [LSM hook]
```

---

## 3. inet_create()

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:260-411`

```c
static int inet_create(struct net *net, struct socket *sock, int protocol, int kern)
{
    struct sock *sk;
    struct inet_protosw *answer;
    struct inet_sock *inet;
    struct proto *answer_prot;
    unsigned char answer_flags;
    int try_loading_module = 0;
    int err;

    if (protocol < 0 || protocol >= IPPROTO_MAX)
        return -EINVAL;

    sock->state = SS_UNCONNECTED;

lookup_protocol:
    err = -ESOCKTNOSUPPORT;
    rcu_read_lock();

    /* Search inetsw[] for matching type/protocol */
    list_for_each_entry_rcu(answer, &inetsw[sock->type], list) {
        err = 0;

        /* Check non-wild match */
        if (protocol == answer->protocol) {
            if (protocol != IPPROTO_IP)
                break;
        } else {
            /* Check wild cases */
            if (IPPROTO_IP == protocol) {
                protocol = answer->protocol;
                break;
            }
            if (IPPROTO_IP == answer->protocol)
                break;
        }
        err = -EPROTONOSUPPORT;
    }
    // ... error handling and module loading ...

    sock->ops = answer->ops;
    answer_prot = answer->prot;
    answer_flags = answer->flags;
    rcu_read_unlock();

    /* Allocate sock structure */
    err = -ENOMEM;
    sk = sk_alloc(net, PF_INET, GFP_KERNEL, answer_prot, kern);
    if (!sk)
        goto out;

    /* Initialize socket from VFS perspective */
    sock_init_data(sock, sk);

    sk->sk_destruct    = inet_sock_destruct;
    sk->sk_protocol    = protocol;
    sk->sk_backlog_rcv = sk->sk_prot->backlog_rcv;

    /* INET-specific initialization */
    inet = inet_sk(sk);
    inet->uc_ttl = -1;
    inet_set_bit(MC_LOOP, sk);
    inet->mc_ttl = 1;
    inet_set_bit(MC_ALL, sk);
    inet->mc_index = 0;
    inet->rcv_tos = 0;

    /* Hash the socket if port was pre-assigned */
    if (inet->inet_num) {
        inet->inet_sport = htons(inet->inet_num);
        err = sk->sk_prot->hash(sk);
        if (err)
            goto out_sk_release;
    }

    /* Protocol-specific initialization */
    if (sk->sk_prot->init) {
        err = sk->sk_prot->init(sk);
        if (err)
            goto out_sk_release;
    }

    return 0;
}
```

### 3.1 inetsw Array and Registration

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:1167-1201`

```c
static struct inet_protosw inetsw_array[] = {
    {
        .type =       SOCK_STREAM,
        .protocol =   IPPROTO_TCP,
        .prot =       &tcp_prot,
        .ops =        &inet_stream_ops,
        .flags =      INET_PROTOSW_PERMANENT | INET_PROTOSW_ICSK,
    },
    {
        .type =       SOCK_DGRAM,
        .protocol =   IPPROTO_UDP,
        .prot =       &udp_prot,
        .ops =        &inet_dgram_ops,
        .flags =      INET_PROTOSW_PERMANENT,
    },
    {
        .type =       SOCK_RAW,
        .protocol =   IPPROTO_IP,          /* wild card */
        .prot =       &raw_prot,
        .ops =        &inet_sockraw_ops,
        .flags =      INET_PROTOSW_REUSE,
    }
};
```

---

## 4. inet_bind()

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:473-574`

```c
int inet_bind(struct socket *sock, struct sockaddr_unsized *uaddr, int addr_len)
{
    return inet_bind_sk(sock->sk, uaddr, addr_len);
}

int inet_bind_sk(struct sock *sk, struct sockaddr_unsized *uaddr, int addr_len)
{
    u32 flags = BIND_WITH_LOCK;
    int err;

    if (sk->sk_prot->bind)
        return sk->sk_prot->bind(sk, uaddr, addr_len);

    if (addr_len < sizeof(struct sockaddr_in))
        return -EINVAL;

    err = BPF_CGROUP_RUN_PROG_INET_BIND_LOCK(sk, uaddr, &addr_len,
                        CGROUP_INET4_BIND, &flags);
    if (err)
        return err;

    return __inet_bind(sk, uaddr, addr_len, flags);
}

int __inet_bind(struct sock *sk, struct sockaddr_unsized *uaddr, int addr_len,
                u32 flags)
{
    struct sockaddr_in *addr = (struct sockaddr_in *)uaddr;
    struct inet_sock *inet = inet_sk(sk);
    struct net *net = sock_net(sk);
    unsigned short snum;
    int chk_addr_ret;
    u32 tb_id = RT_TABLE_LOCAL;
    int err;

    /* Check address family */
    if (addr->sin_family != AF_INET) {
        if (addr->sin_family != AF_UNSPEC ||
            addr->sin_addr.s_addr != htonl(INADDR_ANY))
            return -EAFNOSUPPORT;
    }

    snum = ntohs(addr->sin_port);

    /* Check bind service capability */
    err = -EACCES;
    if (!(flags & BIND_NO_CAP_NET_BIND_SERVICE) &&
        snum && inet_port_requires_bind_service(net, snum) &&
        !ns_capable(net->user_ns, CAP_NET_BIND_SERVICE))
        goto out;

    inet->inet_rcv_saddr = inet->inet_saddr = addr->sin_addr.s_addr;

    /* Acquire lock if needed */
    if (flags & BIND_WITH_LOCK)
        lock_sock(sk);

    /* Allocate port if needed */
    if (snum || !(inet_test_bit(BIND_ADDRESS_NO_PORT, sk) ||
                  (flags & BIND_FORCE_ADDRESS_NO_PORT))) {
        err = sk->sk_prot->get_port(sk, snum);
        if (err) {
            inet->inet_saddr = inet->inet_rcv_saddr = 0;
            goto out_release_sock;
        }
    }

    inet->inet_sport = htons(inet->inet_num);
    inet->inet_daddr = 0;
    inet->inet_dport = 0;
    sk_dst_reset(sk);
    err = 0;

out_release_sock:
    if (flags & BIND_WITH_LOCK)
        release_sock(sk);
out:
    return err;
}
```

---

## 5. inet_listen()

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:238-253`

```c
int inet_listen(struct socket *sock, int backlog)
{
    struct sock *sk = sock->sk;
    int err = -EINVAL;

    lock_sock(sk);

    if (sock->state != SS_UNCONNECTED || sock->type != SOCK_STREAM)
        goto out;

    err = __inet_listen_sk(sk, backlog);

out:
    release_sock(sk);
    return err;
}

int __inet_listen_sk(struct sock *sk, int backlog)
{
    unsigned char old_state = sk->sk_state;
    int err, tcp_fastopen;

    if (!((1 << old_state) & (TCPF_CLOSE | TCPF_LISTEN)))
        return -EINVAL;

    WRITE_ONCE(sk->sk_max_ack_backlog, backlog);

    if (old_state != TCP_LISTEN) {
        tcp_fastopen = READ_ONCE(sock_net(sk)->ipv4.sysctl_tcp_fastopen);
        if ((tcp_fastopen & TFO_SERVER_WO_SOCKOPT1) &&
            (tcp_fastopen & TFO_SERVER_ENABLE) &&
            !inet_csk(sk)->icsk_accept_queue.fastopenq.max_qlen) {
            fastopen_queue_tune(sk, backlog);
            tcp_fastopen_init_key_once(sock_net(sk));
        }

        err = inet_csk_listen_start(sk);
        if (err)
            return err;

        tcp_call_bpf(sk, BPF_SOCK_OPS_TCP_LISTEN_CB, 0, NULL);
    }
    return 0;
}
```

---

## 6. inet_accept()

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:788-803`

```c
int inet_accept(struct socket *sock, struct socket *newsock, struct proto_accept_arg *arg)
{
    struct sock *sk1 = sock->sk, *sk2;

    arg->err = -EINVAL;
    sk2 = READ_ONCE(sk1->sk_prot)->accept(sk1, arg);
    if (!sk2)
        return arg->err;

    lock_sock(sk2);
    __inet_accept(sock, newsock, sk2);
    release_sock(sk2);
    return 0;
}
```

### 6.1 inet_csk_accept() - TCP Accept

**Location:** `/Users/sphinx/github/linux/net/ipv4/inet_connection_sock.c:650-712`

```c
struct sock *inet_csk_accept(struct sock *sk, struct proto_accept_arg *arg)
{
    struct inet_connection_sock *icsk = inet_csk(sk);
    struct request_sock_queue *queue = &icsk->icsk_accept_queue;
    struct request_sock *req;
    struct sock *newsk;
    int error;

    lock_sock(sk);

    /* Verify socket is listening */
    error = -EINVAL;
    if (sk->sk_state != TCP_LISTEN)
        goto out_err;

    /* Find established connection */
    if (reqsk_queue_empty(queue)) {
        long timeo = sock_rcvtimeo(sk, arg->flags & O_NONBLOCK);

        error = -EAGAIN;
        if (!timeo)
            goto out_err;

        error = inet_csk_wait_for_connect(sk, timeo);
        if (error)
            goto out_err;
    }

    /* Remove from accept queue */
    req = reqsk_queue_remove(queue, sk);

    /* Convert request_sock to established sock */
    newsk = req->sk;

    sock_rps_record_flow(newsk);
    sock_graft(newsk, newsock);
    newsock->state = SS_CONNECTED;

    return newsk;

out_err:
    return ERR_PTR(error);
}
```

---

## 7. inet_connect()

### 7.1 inet_stream_connect() - TCP Connect

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:750-759`

```c
int inet_stream_connect(struct socket *sock, struct sockaddr_unsized *uaddr,
                       int addr_len, int flags)
{
    int err;

    lock_sock(sock->sk);
    err = __inet_stream_connect(sock, uaddr, addr_len, flags, 0);
    release_sock(sock->sk);
    return err;
}
```

### 7.2 `__inet_stream_connect()` - Full TCP Connection Logic

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:632-747`

```c
int __inet_stream_connect(struct socket *sock, struct sockaddr_unsized *uaddr,
                          int addr_len, int flags, int is_sendmsg)
{
    struct sock *sk = sock->sk;
    int err;
    long timeo;

    if (uaddr) {
        if (addr_len < sizeof(uaddr->sa_family))
            return -EINVAL;

        if (uaddr->sa_family == AF_UNSPEC) {
            sk->sk_disconnects++;
            err = sk->sk_prot->disconnect(sk, flags);
            sock->state = err ? SS_DISCONNECTING : SS_UNCONNECTED;
            goto out;
        }
    }

    switch (sock->state) {
    default:
        err = -EINVAL;
        goto out;
    case SS_CONNECTED:
        err = -EISCONN;
        goto out;
    case SS_CONNECTING:
        if (inet_test_bit(DEFER_CONNECT, sk))
            err = is_sendmsg ? -EINPROGRESS : -EISCONN;
        else
            err = -EALREADY;
        break;
    case SS_UNCONNECTED:
        err = -EISCONN;
        if (sk->sk_state != TCP_CLOSE)
            goto out;

        if (BPF_CGROUP_PRE_CONNECT_ENABLED(sk)) {
            err = sk->sk_prot->pre_connect(sk, uaddr, addr_len);
            if (err)
                goto out;
        }

        err = sk->sk_prot->connect(sk, uaddr, addr_len);
        if (err < 0)
            goto out;

        sock->state = SS_CONNECTING;

        if (!err && inet_test_bit(DEFER_CONNECT, sk))
            goto out;

        err = -EINPROGRESS;
        break;
    }

    timeo = sock_sndtimeo(sk, flags & O_NONBLOCK);

    if ((1 << sk->sk_state) & (TCPF_SYN_SENT | TCPF_SYN_RECV)) {
        int writebias = /* TCP Fast Open bias calculation */;
        int dis = sk->sk_disconnects;

        if (!timeo || !inet_wait_for_connect(sk, timeo, writebias))
            goto out;

        err = sock_intr_errno(timeo);
        if (signal_pending(current))
            goto out;

        if (dis != sk->sk_disconnects) {
            err = -EPIPE;
            goto out;
        }
    }

    if (sk->sk_state == TCP_CLOSE)
        goto sock_error;

    sock->state = SS_CONNECTED;
    err = 0;

out:
    return err;

sock_error:
    err = sock_error(sk) ? : -ECONNABORTED;
    sock->state = SS_UNCONNECTED;
    sk->sk_disconnects++;
    if (sk->sk_prot->disconnect(sk, flags))
        sock->state = SS_DISCONNECTING;
    goto out;
}
```

---

## 8. Send/Receive Paths

### 8.1 inet_sendmsg()

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:858-867`

```c
int inet_sendmsg(struct socket *sock, struct msghdr *msg, size_t size)
{
    struct sock *sk = sock->sk;

    if (unlikely(inet_send_prepare(sk)))
        return -EAGAIN;

    return INDIRECT_CALL_2(sk->sk_prot->sendmsg, tcp_sendmsg, udp_sendmsg,
                          sk, msg, size);
}
```

### 8.2 inet_recvmsg()

**Location:** `/Users/sphinx/github/linux/net/ipv4/af_inet.c:887-902`

```c
int inet_recvmsg(struct socket *sock, struct msghdr *msg, size_t size, int flags)
{
    struct sock *sk = sock->sk;
    int addr_len = 0;
    int err;

    if (likely(!(flags & MSG_ERRQUEUE)))
        sock_rps_record_flow(sk);

    err = INDIRECT_CALL_2(sk->sk_prot->recvmsg, tcp_recvmsg, udp_recvmsg,
                         sk, msg, size, flags, &addr_len);
    if (err >= 0)
        msg->msg_namelen = addr_len;
    return err;
}
```

---

## 9. Socket File Operations

### 9.1 socket_file_ops

**Location:** `/Users/sphinx/github/linux/net/socket.c:156-173`

```c
static const struct file_operations socket_file_ops = {
    .owner =     THIS_MODULE,
    .read_iter = sock_read_iter,
    .write_iter = sock_write_iter,
    .poll =      sock_poll,
    .unlocked_ioctl = sock_ioctl,
#ifdef CONFIG_COMPAT
    .compat_ioctl = compat_sock_ioctl,
#endif
    .uring_cmd = io_uring_cmd_sock,
    .mmap =      sock_mmap,
    .release =   sock_close,
    .fasync =    sock_fasync,
    .splice_write = splice_to_socket,
    .splice_read =  sock_splice_read,
    .splice_eof =  sock_splice_eof,
    .show_fdinfo = sock_show_fdinfo,
};
```

---

## 10. Socket Timeout and Blocking

### 10.1 sock_rcvtimeo()

**Location:** `/Users/sphinx/github/linux/include/net/sock.h:2701-2704`

```c
static inline long sock_rcvtimeo(const struct sock *sk, bool noblock)
{
    return noblock ? 0 : READ_ONCE(sk->sk_rcvtimeo);
}
```

### 10.2 sk_wait_data()

**Location:** `/Users/sphinx/github/linux/net/core/sock.c:3247-3268`

```c
int sk_wait_data(struct sock *sk, long *timeo, const struct sk_buff *skb)
{
    DEFINE_WAIT_FUNC(wait, woken_wake_function);
    int rc;

    add_wait_queue(sk_sleep(sk), &wait);
    sk_set_bit(SOCKWQ_ASYNC_WAITDATA, sk);
    rc = sk_wait_event(sk, timeo,
                       skb_peek_tail(&sk->sk_receive_queue) != skb,
                       &wait);
    sk_clear_bit(SOCKWQ_ASYNC_WAITDATA, sk);
    remove_wait_queue(sk_sleep(sk), &wait);
    return rc;
}
```

---

## 11. Memory Management

### 11.1 sk_wmem_schedule() - Write Memory Scheduling

Ensures memory is allocated for outgoing data before sending.

**Typical usage pattern:**
```c
if (!sk_wmem_schedule(sk, skb->truesize)) {
    return -ENOMEM;
}
sk_mem_charge(sk, skb->truesize);
atomic_add(skb->truesize, &sk->sk_wmem_alloc);
```

### 11.2 sk_rmem_schedule() - Read Memory Scheduling

Ensures memory is reserved for incoming data.

### 11.3 SKB Allocation

**alloc_skb()** - General SKB allocation from kernel memory:
```c
struct sk_buff *alloc_skb(size_t size, gfp_t priority);
```

**dev_alloc_skb()** - SKB allocation optimized for device receive:
```c
struct sk_buff *dev_alloc_skb(unsigned int length);
```

---

## Socket Creation/Connection Flow Diagram

```
User Application
      |
      | socket()
      v
+-------------+
| sock_alloc()|  <-- Allocate socket + VFS inode
+-------------+
      |
      | pf->create() -> inet_create()
      v
+------------------+     +------------------+     +------------------+
| inetsw lookup    | --> | sk_alloc()       | --> | sock_init_data() |
| (type/protocol)  |     | (allocate sock) |     | (link socket/sock) |
+------------------+     +------------------+     +------------------+

================================================================================

CONNECT FLOW (TCP):
      |
      | connect()
      v
+------------------+
| inet_stream_conn |
+------------------+
      |
      | __inet_stream_connect()
      v
+--------------------+     +--------------------+
| tcp_v4_connect()   | --> | Send SYN           |
| (lookup route)     |     | (sk->sk_prot->conn)|
+--------------------+     +--------------------+
      |                        |
      | Wait for SYN+ACK       |
      v                        v
+------------------+     +------------------+
| inet_wait_for_   |     | tcp_rcv_synsent()|
| connect()         |     | Complete 3-way    |
+------------------+     +------------------+
      |                        |
      v                        v
+------------------+     +------------------+
| sock->state =    |     | tcp_done()      |
| SS_CONNECTED     |     | sk->sk_state =   |
+------------------+     | TCP_ESTABLISHED  |
                         +------------------+

================================================================================

ACCEPT FLOW (TCP):
      |
      | listen()
      v
+------------------+
| inet_listen()    |
+------------------+
      |
      | __inet_listen_sk() -> inet_csk_listen_start()
      v
+------------------+
| sk->sk_state =   |
| TCP_LISTEN       |
+------------------+
      |
      | accept()
      v
+------------------+     +------------------+
| inet_accept()    | --> | sk->sk_prot->   |
|                  |     | accept()        |
+------------------+     +------------------+
      |                        |
      v                        v
+------------------+     +------------------+
| newsock->state = |     | Establish conn   |
| SS_CONNECTED     |     | (request_sock->  |
+------------------+     |  sock)           |
                         +------------------+
```

---

## Data Flow: User to Wire and Back

### Send Path (User to Wire)

```
User Application (write())
      |
      | [File descriptor]
      v
sock_write_iter() / sock_sendmsg()
      |
      | [msghdr with iovec]
      v
inet_sendmsg() -> sk->sk_prot->sendmsg()
      |
      | [tcp_sendmsg() or udp_sendmsg()]
      v
+-----------------------------+
| Protocol-specific handling   |
| - Route lookup              |
| - Header construction       |
| - Checksum calculation      |
+-----------------------------+
      |
      | [sk_buff with headers]
      v
ip_queue_xmit() / ip6_xmit()
      |
      v
      [NIC transmits packet]
```

### Receive Path (Wire to User)

```
NIC receives packet
      |
      v
+-----------------------------+
| netif_receive_skb()          |
+-----------------------------+
      |
      v
+-----------------------------+
| IP layer (ip_rcv)             |
+-----------------------------+
      |
      v
+-----------------------------+
| Transport layer              |
| (tcp_v4_rcv / udp_rcv)       |
+-----------------------------+
      |
      v
sk->sk_receive_queue (sk_buff list)
      |
      v
sock_recvmsg() -> copy_to_user()
      |
      v
User Application (read())
```

---

## File Reference Summary

| File | Purpose |
|------|---------|
| `/Users/sphinx/github/linux/net/socket.c` | BSD socket layer, VFS integration |
| `/Users/sphinx/github/linux/net/ipv4/af_inet.c` | INET socket creation, bind, listen, connect, accept |
| `/Users/sphinx/github/linux/net/ipv4/inet_connection_sock.c` | TCP connection socket (icsk) operations |
| `/Users/sphinx/github/linux/include/linux/net.h` | struct socket, proto_ops |
| `/Users/sphinx/github/linux/include/net/sock.h` | struct sock, sock_common |
| `/Users/sphinx/github/linux/include/linux/skbuff.h` | struct sk_buff |
| `/Users/sphinx/github/linux/include/net/inet_sock.h` | struct inet_sock |
| `/Users/sphinx/github/include/linux/tcp.h` | struct tcp_sock |
| `/Users/sphinx/github/linux/include/linux/udp.h` | struct udp_sock |
| `/Users/sphinx/github/linux/include/net/request_sock.h` | struct request_sock, request_sock_queue |
| `/Users/sphinx/github/linux/include/net/inet_connection_sock.h` | struct inet_connection_sock |
