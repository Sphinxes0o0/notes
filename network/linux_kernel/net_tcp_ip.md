# Linux 内核 TCP/IP 协议栈分析

## 1. net/ipv4/tcp.c 核心结构与函数

### 1.1 struct tcp_sock 结构体

**文件**: `include/linux/tcp.h:197-520`

`tcp_sock` 是 TCP 协议的核心数据结构，继承自 `inet_connection_sock`:

```c
// 行 197-204
struct tcp_sock {
	/* inet_connection_sock has to be the first member of tcp_sock */
	struct inet_connection_sock	inet_conn;
    ...
```

**关键字段分组（按缓存行优化）**:

**TX 读取热点** (行 206-218):
```c
__cacheline_group_begin(tcp_sock_read_tx);
u32	max_window;		/* Maximal window ever seen from peer	*/
u32	rcv_ssthresh;		/* Current window clamp			*/
u32	reordering;		/* Packet reordering metric.		*/
u32	notsent_lowat;		/* TCP_NOTSENT_LOWAT */
u16	gso_segs;		/* Max number of segs per GSO packet	*/
struct sk_buff *retransmit_skb_hint;  /* from STCP, retrans queue hinting */
__cacheline_group_end(tcp_sock_read_tx);
```

**TXRX 读取热点** (行 220-237):
```c
__cacheline_group_begin(tcp_sock_read_txrx);
u32	tsoffset;		/* timestamp offset */
u32	snd_wnd;		/* The window we expect to receive	*/
u32	mss_cache;		/* Cached effective mss, not including SACKS */
u32	snd_cwnd;		/* Sending congestion window		*/
u32	prr_out;		/* Total number of pkts sent during Recovery. */
u32	lost_out;		/* Lost packets			*/
u32	sacked_out;		/* SACK'd packets			*/
u8	nonagle     : 4,	/* Disable Nagle algorithm?             */
    rate_app_limited:1;  /* rate limited? */
__cacheline_group_end(tcp_sock_read_txrx);
```

**RX 读取热点** (行 239-253):
```c
__cacheline_group_begin(tcp_sock_read_rx);
u32	copied_seq;		/* Head of yet unread data */
u32	snd_wl1;		/* Sequence for window update		*/
u32	tlp_high_seq;		/* snd_nxt at the time of TLP */
u32	rttvar_us;		/* smoothed mdev_max			*/
u32	retrans_out;		/* Retransmitted packets out		*/
struct rb_root	out_of_order_queue;  /* OOO segments rbtree */
__cacheline_group_end(tcp_sock_read_rx);
```

**TX 读写热点** (行 255-283):
```c
__cacheline_group_begin(tcp_sock_write_tx) ____cacheline_aligned;
u32	segs_out;		/* RFC4898 tcpEStatsPerfSegsOut */
u64	bytes_sent;		/* RFC4898 tcpEStatsPerfHCDataOctetsOut */
u32	write_seq;		/* Tail(+1) of data held in tcp send buffer */
u32	pushed_seq;		/* Last pushed seq, required to talk to windows */
u32	lsndtime;		/* timestamp of last sent data packet */
u32	mdev_us;		/* medium deviation			*/
struct list_head tsorted_sent_queue; /* time-sorted sent but un-SACKed skbs */
struct sk_buff *highest_sack;   /* skb just after the highest sack */
__cacheline_group_end(tcp_sock_write_tx);
```

### 1.2 struct tcp_md5sig 结构体

**文件**: `include/uapi/linux/tcp.h:389-396`

```c
struct tcp_md5sig {
	struct __kernel_sock_addr_storage tcpm_addr;	/* address associated */
	__u8	tcpm_flags;				/* extension flags */
	__u8	tcpm_prefixlen;				/* address prefix */
	__u16	tcpm_keylen;				/* key length */
	int	tcpm_ifindex;				/* device index for scope */
	__u8	tcpm_key[TCP_MD5SIG_MAXKEYLEN];		/* key (binary) */
};
```

### 1.3 tcp_sendmsg() 函数

**文件**: `net/ipv4/tcp.c:1460-1469`

```c
int tcp_sendmsg(struct sock *sk, struct msghdr *msg, size_t size)
{
	int ret;

	lock_sock(sk);
	ret = tcp_sendmsg_locked(sk, msg, size);
	release_sock(sk);

	return ret;
}
```

**实际发送逻辑 tcp_sendmsg_locked()**: 行 1130-1458

关键发送路径 (行 1241-1334):
```c
restart:
	mss_now = tcp_send_mss(sk, &size_goal, flags);

	while (msg_data_left(msg)) {
		int copy = 0;

		skb = tcp_write_queue_tail(sk);
		if (skb)
			copy = size_goal - skb->len;

		if (copy <= 0 || !tcp_skb_can_collapse_to(skb)) {
new_segment:
			if (!sk_stream_memory_free(sk))
				goto wait_for_space;
            ...
			skb = tcp_stream_alloc_skb(sk, sk->sk_allocation,
						   first_skb);
            ...
			tcp_skb_entail(sk, skb);
			copy = size_goal;
		}
        // 数据复制和合并
		copy = min_t(int, copy, msg_data_left(msg));
		err = skb_copy_to_page_nocache(sk, &msg->msg_iter, skb,
					       pfrag->page,
					       pfrag->offset, copy);
```

### 1.4 tcp_recvmsg() 函数

**文件**: `net/ipv4/tcp.c:2965-2980`

```c
int tcp_recvmsg(struct sock *sk, struct msghdr *msg, size_t len, int flags,
		int *addr_len)
{
	int ret;
	ret = tcp_recvmsg_locked(sk, msg, len, flags, &tss, &cmsg_flags);
    ...
}
```

**实际接收逻辑 tcp_recvmsg_locked()**: 行 2687-2900

关键接收循环 (行 2740-2834):
```c
do {
	u32 offset;

	/* Check for urgent data */
	if (unlikely(tp->urg_data) && tp->urg_seq == *seq) {
		if (copied)
			break;
		if (signal_pending(current)) {
			copied = timeo ? sock_intr_errno(timeo) : -EAGAIN;
			break;
		}
	}

	/* Get buffer from receive queue */
	skb_queue_walk(&sk->sk_receive_queue, skb) {
		offset = *seq - TCP_SKB_CB(skb)->seq;
		if (TCP_SKB_CB(skb)->tcp_flags & TCPHDR_FIN)
			goto found_fin_ok;
		if (offset < skb->len)
			goto found_ok_skb;
	}
    ...
} while (copied < target);
```

### 1.5 TCP 连接建立

#### tcp_v4_connect()

**文件**: `net/ipv4/tcp_ipv4.c:222-364`

```c
int tcp_v4_connect(struct sock *sk, struct sockaddr_unsized *uaddr, int addr_len)
{
	struct sockaddr_in *usin = (struct sockaddr_in *)uaddr;
    ...
	/* Set state to SYN-SENT */
	tcp_set_state(sk, TCP_SYN_SENT);  // 行 306
	err = inet_hash_connect(tcp_death_row, sk);  // 行 307
    ...
	err = tcp_connect(sk);  // 行 346
    ...
failure:
	tcp_set_state(sk, TCP_CLOSE);  // 行 358
    ...
}
```

#### tcp_connect()

**文件**: `net/ipv4/tcp_output.c:4296-4395`

```c
int tcp_connect(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct sk_buff *buff;
	int err;

	tcp_connect_init(sk);  // 行 4354

	buff = tcp_stream_alloc_skb(sk, sk->sk_allocation, true);  // 行 4361
	if (unlikely(!buff))
		return -ENOBUFS;

	/* SYN eats a sequence byte */
	tcp_init_nondata_skb(buff, sk, tp->write_seq, TCPHDR_SYN);  // 行 4368
	tcp_connect_queue_skb(sk, buff);
	tcp_ecn_send_syn(sk, buff);
	tcp_rbtree_insert(&sk->tcp_rtx_queue, buff);

	/* Send off SYN; include data in Fast Open */
	err = tp->fastopen_req ? tcp_send_syn_data(sk, buff) :
	      tcp_transmit_skb(sk, buff, 1, sk->sk_allocation);  // 行 4377

	WRITE_ONCE(tp->snd_nxt, tp->write_seq);
	tp->pushed_seq = tp->write_seq;

	/* Timer for repeating the SYN until an answer. */
	tcp_reset_xmit_timer(sk, ICSK_TIME_RETRANS,
			     inet_csk(sk)->icsk_rto, false);  // 行 4394
    ...
}
```

#### tcp_connect_init()

**文件**: `net/ipv4/tcp_output.c:4104-4177`

```c
static void tcp_connect_init(struct sock *sk)
{
	const struct dst_entry *dst = __sk_dst_get(sk);
	struct tcp_sock *tp = tcp_sk(sk);
    ...
	tp->tcp_header_len = sizeof(struct tcphdr);
	if (READ_ONCE(sock_net(sk)->ipv4.sysctl_tcp_timestamps))
		tp->tcp_header_len += TCPOLEN_TSTAMP_ALIGNED;
    ...
	tcp_sync_mss(sk, dst_mtu(dst));  // 行 4127
    ...
	tp->snd_una = tp->write_seq;  // 行 4162
	WRITE_ONCE(tp->snd_nxt, tp->write_seq);  // 行 4165
	tp->rcv_nxt = 0;  // 行 4168
	tp->rcv_wup = tp->rcv_nxt;  // 行 4171
	inet_csk(sk)->icsk_rto = tcp_timeout_init(sk);  // 行 4174
    ...
}
```

### 1.6 TCP 状态机

#### TCP 状态定义

**文件**: `include/net/tcp_states.h:12-28`

```c
enum {
	TCP_ESTABLISHED = 1,
	TCP_SYN_SENT,
	TCP_SYN_RECV,
	TCP_FIN_WAIT1,
	TCP_FIN_WAIT2,
	TCP_TIME_WAIT,
	TCP_CLOSE,
	TCP_CLOSE_WAIT,
	TCP_LAST_ACK,
	TCP_LISTEN,
	TCP_CLOSING,	/* Now a valid state */
	TCP_NEW_SYN_RECV,
	TCP_BOUND_INACTIVE, /* Pseudo-state for inet_diag */
	TCP_MAX_STATES	/* Leave at the end! */
};
```

#### tcp_set_state()

**文件**: `net/ipv4/tcp.c:2997-3065`

```c
void tcp_set_state(struct sock *sk, int state)
{
	int oldstate = sk->sk_state;
    ...
	switch (state) {
	case TCP_ESTABLISHED:
		if (oldstate != TCP_ESTABLISHED)
			TCP_INC_STATS(sock_net(sk), TCP_MIB_CURRESTAB);
		break;
	case TCP_CLOSE_WAIT:
		if (oldstate == TCP_SYN_RECV)
			TCP_INC_STATS(sock_net(sk), TCP_MIB_CURRESTAB);
		break;
	case TCP_CLOSE:
		if (oldstate == TCP_CLOSE_WAIT || oldstate == TCP_ESTABLISHED)
			TCP_INC_STATS(sock_net(sk), TCP_MIB_ESTABRESETS);
		sk->sk_prot->unhash(sk);
		...
	default:
		if (oldstate == TCP_ESTABLISHED || oldstate == TCP_CLOSE_WAIT)
			TCP_DEC_STATS(sock_net(sk), TCP_MIB_CURRESTAB);
	}
	inet_sk_state_store(sk, state);  // 行 3064
}
```

#### 状态转换表

**文件**: `net/ipv4/tcp.c:3075-3100`

```c
static const unsigned char new_state[16] = {
  /* current state:        new state:      action:	*/
  [TCPF_ESTABLISHED]	= TCP_FIN_WAIT1 | TCP_ACTION_FIN,
  [TCPF_CLOSE_WAIT]	= TCP_LAST_ACK | TCP_ACTION_FIN,
  [TCPF_FIN_WAIT1]	= TCP_CLOSING | TCP_ACTION_FIN,
  [TCPF_FIN_WAIT2]	= TCP_TIME_WAIT | TCP_ACTION_FIN,
  [TCPF_CLOSING]	= TCP_TIME_WAIT | TCP_ACTION_FIN,
  [TCPF_LAST_ACK]	= TCP_CLOSE | TCP_ACTION_FIN,
};
```

#### tcp_close_state()

**文件**: `net/ipv4/tcp.c:3092-3100`

```c
static int tcp_close_state(struct sock *sk)
{
	int next = (int)new_state[sk->sk_state];
	int ns = next & TCP_STATE_MASK;

	tcp_set_state(sk, ns);

	return next & TCP_ACTION_FIN;
}
```

### 1.7 tcp_close() 和 tcp_disconnect()

#### tcp_close()

**文件**: `net/ipv4/tcp.c:3347-3356`

```c
void tcp_close(struct sock *sk, long timeout)
{
	lock_sock(sk);
	__tcp_close(sk, timeout);
	release_sock(sk);
	if (!sk->sk_net_refcnt)
		inet_csk_clear_xmit_timers_sync(sk);
	sock_put(sk);
}
```

#### __tcp_close()

**文件**: `net/ipv4/tcp.c:3175-3255`

```c
void __tcp_close(struct sock *sk, long timeout)
{
	bool data_was_unread = false;
	struct sk_buff *skb;
	int state;

	WRITE_ONCE(sk->sk_shutdown, SHUTDOWN_MASK);

	if (sk->sk_state == TCP_LISTEN) {
		tcp_set_state(sk, TCP_CLOSE);
		inet_csk_listen_stop(sk);
		goto adjudge_to_death;
	}

	/* Flush receive buffers */
	while ((skb = skb_peek(&sk->sk_receive_queue)) != NULL) {
		u32 end_seq = TCP_SKB_CB(skb)->end_seq;
		if (TCP_SKB_CB(skb)->tcp_flags & TCPHDR_FIN)
			end_seq--;
		if (after(end_seq, tcp_sk(sk)->copied_seq))
			data_was_unread = true;
		tcp_eat_recv_skb(sk, skb);
	}

	if (sk->sk_state == TCP_CLOSE)
		goto adjudge_to_death;

	/* ABORT logic per RFC2525 */
	if (unlikely(tcp_sk(sk)->repair)) {
		sk->sk_prot->disconnect(sk, 0);
	} else if (data_was_unread) {
		/* Unread data was tossed, zap the connection. */
		tcp_set_state(sk, TCP_CLOSE);
		tcp_send_active_reset(sk, sk->sk_allocation,
				      SK_RST_REASON_TCP_ABORT_ON_CLOSE);
	} else if (tcp_close_state(sk)) {
		/* Send FIN if needed */
		tcp_send_fin(sk);
	}
    ...
}
```

#### tcp_disconnect()

**文件**: `net/ipv4/tcp.c:3400-3430`

```c
int tcp_disconnect(struct sock *sk, int flags)
{
	struct inet_sock *inet = inet_sk(sk);
	struct inet_connection_sock *icsk = inet_csk(sk);
	struct tcp_sock *tp = tcp_sk(sk);
	int old_state = sk->sk_state;
    ...
	if (old_state != TCP_CLOSE)
		tcp_set_state(sk, TCP_CLOSE);

	/* ABORT function of RFC793 */
	if (old_state == TCP_LISTEN) {
		inet_csk_listen_stop(sk);
	} else if (unlikely(tp->repair)) {
		WRITE_ONCE(sk->sk_err, ECONNABORTED);
	} else if (tcp_need_reset(old_state)) {
		tcp_send_active_reset(sk, gfp_any(), SK_RST_REASON_TCP_STATE);
		WRITE_ONCE(sk->sk_err, ECONNRESET);
	}
    ...
}
```

## 2. net/ipv4/tcp_input.c 核心函数

### 2.1 tcp_rcv_established()

**文件**: `net/ipv4/tcp_input.c:6519-6712`

快速路径（头部预测） (行 6559-6616):
```c
void tcp_rcv_established(struct sock *sk, struct sk_buff *skb)
{
	const struct tcphdr *th = (const struct tcphdr *)skb->data;
	struct tcp_sock *tp = tcp_sk(sk);
	unsigned int len = skb->len;
    ...
	/* Header prediction check:
	 * pred_flags is 0xS?10 << 16 + snd_wnd
	 * if header_prediction is to be made
	 */
	if ((tcp_flag_word(th) & TCP_HP_BITS) == tp->pred_flags &&
	    TCP_SKB_CB(skb)->seq == tp->rcv_nxt &&
	    !after(TCP_SKB_CB(skb)->ack_seq, tp->snd_nxt)) {
        ...
		if (tcp_header_len == sizeof(struct tcphdr) + TCPOLEN_TSTAMP_ALIGNED) {
			if (!tcp_parse_aligned_timestamp(tp, th))
				goto slow_path;
			delta = tp->rx_opt.rcv_tsval - tp->rx_opt.ts_recent;
		}

		if (len <= tcp_header_len) {
			if (len == tcp_header_len) {
				/* Pure ACK */
				tcp_ecn_received_counters(sk, skb, 0);
				tcp_ack(sk, skb, flag);  // 行 6608
				__kfree_skb(skb);
				tcp_data_snd_check(sk);  // 行 6610
				return;
			}
		} else {
			/* Bulk data transfer */
			tcp_cleanup_skb(skb);
			__skb_pull(skb, tcp_header_len);
			eaten = tcp_queue_rcv(sk, skb, &fragstolen);  // 行 6655
			tcp_event_data_recv(sk, skb);
			if (TCP_SKB_CB(skb)->ack_seq != tp->snd_una) {
				tcp_ack(sk, skb, flag | FLAG_DATA);  // 行 6661
				tcp_data_snd_check(sk);  // 行 6662
			}
			__tcp_ack_snd_check(sk, 0);
			return;
		}
	}
slow_path:
	/* Standard slow path */
	if (!tcp_validate_incoming(sk, skb, th, 1))
		return;
    ...
	reason = tcp_ack(sk, skb, FLAG_SLOWPATH | FLAG_UPDATE_TS_RECENT);  // 行 6697
    ...
	tcp_data_queue(sk, skb);  // 行 6708
	tcp_data_snd_check(sk);  // 行 6710
}
```

### 2.2 tcp_data_snd_check()

**文件**: `net/ipv4/tcp_input.c:6125-6129`

```c
static inline void tcp_data_snd_check(struct sock *sk)
{
	tcp_push_pending_frames(sk);
	tcp_check_space(sk);
}
```

### 2.3 tcp_ack()

**文件**: `net/ipv4/tcp_input.c:4246-4395`

```c
static int tcp_ack(struct sock *sk, const struct sk_buff *skb, int flag)
{
	struct inet_connection_sock *icsk = inet_csk(sk);
	struct tcp_sock *tp = tcp_sk(sk);
	struct tcp_sacktag_state sack_state;
	struct rate_sample rs = { .prior_delivered = 0 };
	u32 prior_snd_una = tp->snd_una;
    ...
	/* If the ack is older than previous acks then we can probably ignore it. */
	if (before(ack, prior_snd_una)) {
		if (before(ack, prior_snd_una - max_window)) {
			if (!(flag & FLAG_NO_CHALLENGE_ACK))
				tcp_send_challenge_ack(sk, false);
			return -SKB_DROP_REASON_TCP_TOO_OLD_ACK;
		}
		goto old_ack;
	}

	/* If the ack includes data we haven't sent yet, discard this segment */
	if (after(ack, tp->snd_nxt))
		return -SKB_DROP_REASON_TCP_ACK_UNSENT_DATA;

	if (after(ack, prior_snd_una)) {
		flag |= FLAG_SND_UNA_ADVANCED;
		WRITE_ONCE(icsk->icsk_retransmits, 0);
	}
    ...
	/* Window update check */
	if ((flag & (FLAG_SLOWPATH | FLAG_SND_UNA_ADVANCED)) ==
	    FLAG_SND_UNA_ADVANCED) {
		/* Window is constant, pure forward advance */
		tcp_update_wl(tp, ack_seq);
		tcp_snd_una_update(tp, ack);
		flag |= FLAG_WIN_UPDATE;
	} else {
		/* Slow path processing */
		flag |= tcp_ack_update_window(sk, skb, ack, ack_seq);
		if (TCP_SKB_CB(skb)->sacked)
			flag |= tcp_sacktag_write_queue(sk, skb, prior_snd_una,
							&sack_state);
	}
    ...
	/* Clean retransmit queue */
	flag |= tcp_clean_rtx_queue(sk, skb, prior_fack, prior_snd_una,
				    &sack_state, flag & FLAG_ECE);
    ...
	if (tcp_ack_is_dubious(sk, flag)) {
		tcp_fastretrans_alert(sk, prior_snd_una, num_dupack, &flag,
				      &rexmit);  // 行 4391
	}
    ...
}
```

### 2.4 tcp_rcv_state_process()

**文件**: `net/ipv4/tcp_input.c:7170-7250`

```c
tcp_rcv_state_process(struct sock *sk, struct sk_buff *skb)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct inet_connection_sock *icsk = inet_csk(sk);
	const struct tcphdr *th = tcp_hdr(skb);
    ...
	switch (sk->sk_state) {
	case TCP_CLOSE:
		goto discard;

	case TCP_LISTEN:
		if (th->ack) return SKB_DROP_REASON_TCP_FLAGS;
		if (th->syn) {
			rcu_read_lock();
			local_bh_disable();
			icsk->icsk_af_ops->conn_request(sk, skb);
			local_bh_enable();
			rcu_read_unlock();
			consume_skb(skb);
			return 0;
		}
		goto discard;

	case TCP_SYN_SENT:
		tp->rx_opt.saw_tstamp = 0;
		tcp_mstamp_refresh(tp);
		queued = tcp_rcv_synsent_state_process(sk, skb, th);  // 行 7215
		if (queued >= 0)
			return queued;
		tcp_urg(sk, skb, th);
		__kfree_skb(skb);
		tcp_data_snd_check(sk);
		return 0;
	}
    ...
}
```

## 3. TCP 套接字操作与通用套接字的不同

### 3.1 tcp_prot 结构体

**文件**: `net/ipv4/tcp_ipv4.c:3416-3466`

```c
struct proto tcp_prot = {
	.name			= "TCP",
	.owner			= THIS_MODULE,
	.close			= tcp_close,
	.pre_connect		= tcp_v4_pre_connect,
	.connect		= tcp_v4_connect,
	.disconnect		= tcp_disconnect,
	.accept			= inet_csk_accept,
	.ioctl			= tcp_ioctl,
	.init			= tcp_v4_init_sock,
	.destroy		= tcp_v4_destroy_sock,
	.shutdown		= tcp_shutdown,
	.setsockopt		= tcp_setsockopt,
	.getsockopt		= tcp_getsockopt,
	.recvmsg		= tcp_recvmsg,
	.sendmsg		= tcp_sendmsg,
	.splice_eof		= tcp_splice_eof,
	.backlog_rcv		= tcp_v4_do_rcv,
	.release_cb		= tcp_release_cb,
	.hash			= inet_hash,
	.unhash			= inet_unhash,
	.get_port		= inet_csk_get_port,
	.freeptr_offset		= offsetof(struct tcp_sock,
					   inet_conn.icsk_inet.sk.sk_freeptr),
	.obj_size		= sizeof(struct tcp_sock),  // 行 3457
	...
};
```

**关键差异**:
- `obj_size = sizeof(struct tcp_sock)` - TCP 使用更大的结构体
- `backlog_rcv = tcp_v4_do_rcv` - TCP 特定的 backlog 处理
- `sendmsg/recvmsg` 使用 TCP 特定的实现

### 3.2 inet_connection_sock 结构体

**文件**: `include/net/inet_connection_sock.h:82-144`

```c
struct inet_connection_sock {
	/* inet_sock has to be the first member! */
	struct inet_sock	  icsk_inet;
	struct request_sock_queue icsk_accept_queue;
	struct inet_bind_bucket	  *icsk_bind_hash;
	struct timer_list	  icsk_delack_timer;  // 延迟 ACK 定时器
	union {
		struct timer_list icsk_keepalive_timer;
		struct timer_list mptcp_tout_timer;
	};
	__u32			  icsk_rto;           // 重传超时
	__u32			  icsk_rto_min;
	__u32			  icsk_rto_max;
	__u32			  icsk_delack_max;
	const struct tcp_congestion_ops *icsk_ca_ops;  // 拥塞控制
	const struct inet_connection_sock_af_ops *icsk_af_ops;
	...
	struct {
		__u8		  pending;	 /* ACK is pending */
		__u8		  quick;	 /* Scheduled number of quick acks */
		__u8		  pingpong;	 /* The session is interactive */
		__u8		  retry;
		__u32		  ato:ATO_BITS,	 /* Predicted tick of soft clock */
				  rcv_mss;	 /* MSS used for delayed ACK decisions */
	} icsk_ack;
	...
};
```

## 4. 发送/接收路径的 Copybreak 和合并

### 4.1 Copybreak 优化

**文件**: `net/ipv4/tcp.c:740-749`

```c
static bool tcp_should_autocork(struct sock *sk, struct sk_buff *skb,
				int size_goal)
{
	return skb->len < size_goal &&
	       READ_ONCE(sock_net(sk)->ipv4.sysctl_tcp_autocorking) &&
	       !tcp_rtx_queue_empty(sk) &&
	       refcount_read(&sk->sk_wmem_alloc) > skb->truesize &&
	       tcp_skb_can_collapse_to(skb);
}
```

### 4.2 SKB 合并条件

**文件**: `net/ipv4/tcp.c:1257-1278`

```c
if (copy <= 0 || !tcp_skb_can_collapse_to(skb)) {
new_segment:
	if (!sk_stream_memory_free(sk))
		goto wait_for_space;
	first_skb = tcp_rtx_and_write_queues_empty(sk);
	skb = tcp_stream_alloc_skb(sk, sk->sk_allocation,
				   first_skb);
	if (!skb)
		goto wait_for_space;
	tcp_skb_entail(sk, skb);
	copy = size_goal;
}
```

### 4.3 数据复制和合并

**文件**: `net/ipv4/tcp.c:1291-1334`

```c
/* Try to append data to the end of skb. */
if (copy > msg_data_left(msg))
	copy = msg_data_left(msg);

if (zc == 0) {
	bool merge = true;
	int i = skb_shinfo(skb)->nr_frags;
	struct page_frag *pfrag = sk_page_frag(sk);

	if (!sk_page_frag_refill(sk, pfrag))
		goto wait_for_space;

	if (!skb_can_coalesce(skb, i, pfrag->page,
			      pfrag->offset)) {
		if (i >= READ_ONCE(net_hotdata.sysctl_max_skb_frags)) {
			tcp_mark_push(tp, skb);
			goto new_segment;
		}
		merge = false;
	}

	copy = min_t(int, copy, pfrag->size - pfrag->offset);
    ...
	err = skb_copy_to_page_nocache(sk, &msg->msg_iter, skb,
				       pfrag->page,
				       pfrag->offset,
				       copy);
	if (err)
		goto do_error;

	/* Update the skb. */
	if (merge) {
		skb_frag_size_add(&skb_shinfo(skb)->frags[i - 1], copy);
	} else {
		skb_fill_page_desc(skb, i, pfrag->page, pfrag->offset, copy);
	}
    ...
}
```

## 5. 连接状态转换

### 5.1 三次握手状态转换

```
客户端                              服务器
  |                                   |
  |  --- SYN (seq=x) ------------->   |  TCP_SYN_SENT → TCP_SYN_RECV
  |                                   |
  |  <-- SYN+ACK (seq=y, ack=x+1) --  |  TCP_SYN_RECV
  |                                   |
  |  --- ACK (ack=y+1) ------------>  |  TCP_SYN_RECV → TCP_ESTABLISHED
  |                                   |
  v                                   v
```

**SYN_SENT 处理** (`tcp_rcv_synsent_state_process`):
- 文件: `net/ipv4/tcp_input.c:6994` → `tcp_finish_connect(sk, skb)` → `tcp_set_state(sk, TCP_ESTABLISHED)`

**SYN_RECV 处理**:
- 文件: `net/ipv4/tcp_input.c:7058` → `tcp_set_state(sk, TCP_SYN_RECV)`
- 文件: `net/ipv4/tcp_input.c:7288` → `tcp_set_state(sk, TCP_ESTABLISHED)`

### 5.2 四次挥手状态转换

```
主动关闭                            被动关闭
  |                                   |
  |  --- FIN (seq=u) ------------->  |  TCP_ESTABLISHED → TCP_FIN_WAIT1
  |                                   |  TCP_ESTABLISHED → TCP_CLOSE_WAIT
  |                                   |
  |  <-- ACK (ack=u+1) -------------  |  TCP_FIN_WAIT1 → TCP_FIN_WAIT2
  |                                   |
  |  <-- FIN (seq=w) ---------------- |  TCP_CLOSE_WAIT → TCP_LAST_ACK
  |                                   |
  |  --- ACK (ack=w+1) ------------->  |  TCP_LAST_ACK → TCP_CLOSE
  |                                   |
  v                                   v
```

## 6. 定时器管理

### 6.1 tcp_init_xmit_timers()

**文件**: `net/ipv4/tcp_timer.c:896-905`

```c
void tcp_init_xmit_timers(struct sock *sk)
{
	inet_csk_init_xmit_timers(sk, &tcp_write_timer, &tcp_delack_timer,
				  &tcp_keepalive_timer);
	hrtimer_setup(&tcp_sk(sk)->pacing_timer, tcp_pace_kick, CLOCK_MONOTONIC,
		      HRTIMER_MODE_ABS_PINNED_SOFT);
	hrtimer_setup(&tcp_sk(sk)->compressed_ack_timer, tcp_compressed_ack_kick,
		      CLOCK_MONOTONIC, HRTIMER_MODE_REL_PINNED_SOFT);
}
```

### 6.2 TCP 定时器类型

**文件**: `include/net/inet_connection_sock.h:146-150`

```c
#define ICSK_TIME_RETRANS	1	/* Retransmit timer */
#define ICSK_TIME_DACK		2	/* Delayed ack timer */
#define ICSK_TIME_PROBE0	3	/* Zero window probe timer */
#define ICSK_TIME_LOSS_PROBE	5	/* Tail loss probe timer */
#define ICSK_TIME_REO_TIMEOUT	6	/* Reordering timer */
```

### 6.3 tcp_retransmit_timer()

**文件**: `net/ipv4/tcp_timer.c:534-603`

```c
void tcp_retransmit_timer(struct sock *sk)
{
	struct tcp_sock *tp = tcp_sk(sk);
	struct inet_connection_sock *icsk = inet_csk(sk);
    ...
	if (!tp->packets_out)
		return;

	if (!tp->snd_wnd && !sock_flag(sk, SOCK_DEAD) &&
	    !((1 << sk->sk_state) & (TCPF_SYN_SENT | TCPF_SYN_RECV))) {
		/* Zero window probe handling */
		if (tcp_rtx_probe0_timed_out(sk, skb, rtx_delta)) {
			tcp_write_err(sk);
			goto out;
		}
		tcp_enter_loss(sk);
		tcp_retransmit_skb(sk, skb, 1);
		goto out_reset_timer;
	}
    ...
	__NET_INC_STATS(sock_net(sk), LINUX_MIB_TCPTIMEOUTS);
	if (tcp_write_timeout(sk))
		goto out;
    ...
}
```

### 6.4 SYN-SENT 定时器

SYN-SENT 状态使用 `ICSK_TIME_RETRANS` 定时器，在 `tcp_connect()` 中设置:

**文件**: `net/ipv4/tcp_output.c:4393-4395`

```c
/* Timer for repeating the SYN until an answer. */
tcp_reset_xmit_timer(sk, ICSK_TIME_RETRANS,
		     inet_csk(sk)->icsk_rto, false);
```

---

## 7. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| struct tcp_sock | include/linux/tcp.h | 197-520 |
| tcp_sendmsg | net/ipv4/tcp.c | 1460-1469 |
| tcp_sendmsg_locked | net/ipv4/tcp.c | 1130-1458 |
| tcp_recvmsg | net/ipv4/tcp.c | 2965-2980 |
| tcp_recvmsg_locked | net/ipv4/tcp.c | 2687-2900 |
| tcp_v4_connect | net/ipv4/tcp_ipv4.c | 222-364 |
| tcp_connect | net/ipv4/tcp_output.c | 4296-4395 |
| tcp_connect_init | net/ipv4/tcp_output.c | 4104-4177 |
| tcp_set_state | net/ipv4/tcp.c | 2997-3065 |
| tcp_close | net/ipv4/tcp.c | 3347-3356 |
| __tcp_close | net/ipv4/tcp.c | 3175-3255 |
| tcp_rcv_established | net/ipv4/tcp_input.c | 6519-6712 |
| tcp_ack | net/ipv4/tcp_input.c | 4246-4395 |
| tcp_rcv_state_process | net/ipv4/tcp_input.c | 7170-7250 |
| tcp_prot | net/ipv4/tcp_ipv4.c | 3416-3466 |
| tcp_init_xmit_timers | net/ipv4/tcp_timer.c | 896-905 |
| tcp_retransmit_timer | net/ipv4/tcp_timer.c | 534-603 |
