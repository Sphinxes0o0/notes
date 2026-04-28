# net/bluetooth - 蓝牙协议栈

## 1. 模块架构

### 1.1 功能概述

Linux 蓝牙协议栈 (BlueZ) 实现了 Bluetooth 核心协议和蓝牙适配器管理。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/bluetooth/hci_core.c` | HCI 核心 |
| `net/bluetooth/hci_conn.c` | 连接管理 |
| `net/bluetooth/l2cap_core.c` | L2CAP |
| `net/bluetooth/sco.c` | SCO 音频 |
| `net/bluetooth/rfcomm.c` | RFCOMM |
| `net/bluetooth/sdp.c` | SDP 服务发现 |

## 2. 核心数据结构

### 2.1 struct hci_dev

```c
// include/net/bluetooth/hci.h:500
struct hci_dev {
    struct list_head list;
    char name[8];
    unsigned long flags;
    __u16 id;

    struct hci_dev_stats stat;
    struct rfkill *rfkill;

    struct delayed_work_le scan_le; // LE 扫描
    struct work_struct_le rx_work;  // 接收工作
    struct work_struct_le cmd_work; // 命令工作

    struct sk_buff_head rx_q;       // 接收队列
    struct sk_buff_head cmd_q;      // 命令队列

    struct hci_conn_hash *conn_hash; // 连接哈希表
    struct list_head adv_list;      // 广播列表

    const struct hci_dev_ops *ops;
};
```

### 2.2 struct hci_conn

```c
// include/net/bluetooth/hci.h:600
struct hci_conn {
    struct list_head list;
    __u16 handle;                   // 连接句柄
    __u8 type;                     // 连接类型
    __u8 dst_type;                 // 目的地址类型
    bdaddr_t dst;                  // 目的地址

    __u8 state;                    // 连接状态
    __u8 mode;                     // 模式

    struct hci_conn_params *param;

    __u16 interval;                // 连接间隔
    __u16 latency;
    __u16 supervision_timeout;

    struct delayed_work_discov_work;
    struct timer_list conn_timer;   // 连接定时器
};
```

### 2.3 struct l2cap_conn

```c
// net/bluetooth/l2cap_core.h:100
struct l2cap_conn {
    struct hci_conn *hcon;
    struct list_head conn_list;

    __u16mtu;
    __u16 fcs;

    struct list_head channels;      // L2CAP 信道
    struct sk_buff_head tx_q;       // 发送队列
    struct sk_buff_head srej_q;     // 选择性重发队列

    struct work_struct tx_work;
    struct work_struct rx_work;
};
```

## 3. HCI (主机控制器接口)

### 3.1 HCI 事件处理

```c
// net/bluetooth/hci_event.c:500
static void hci_event(struct hci_dev *hdev, struct sk_buff *skb)
{
    struct hci_event_hdr *hdr = (void *)skb->data;
    __u8 event = hdr->evt;

    skb_pull(skb, sizeof(*hdr));

    switch (event) {
    case HCI_EV_CONN_COMPLETE:
        hci_conn_complete_evt(hdev, skb);
        break;
    case HCI_EV_CONN_REQUEST:
        hci_conn_request_evt(hdev, skb);
        break;
    case HCI_EV_DISCONN_COMPLETE:
        hci_disconn_complete_evt(hdev, skb);
        break;
    case HCI_EV_LE_META:
        hci_le_meta_evt(hdev, skb);
        break;
    }
}
```

### 3.2 HCI 命令发送

```c
// net/bluetooth/hci_cmd.c:100
int hci_send_cmd(struct hci_dev *hdev, __u16 ogf, __u16 ocf, __u8 plen,
                 void *param)
{
    struct sk_buff *skb;

    // 分配 skb
    skb = bt_skb_alloc(HCI_COMMAND_HDR_SIZE + plen, GFP_ATOMIC);
    if (!skb)
        return -ENOMEM;

    // 构建命令头
    struct hci_command_hdr *hdr = skb_put(skb, HCI_COMMAND_HDR_SIZE);
    hdr->opcode = cpu_to_le16(hci_opcode(ogf, ocf));
    hdr->plen = plen;

    // 添加参数
    memcpy(skb_put(skb, plen), param, plen);

    // 加入命令队列
    skb_queue_tail(&hdev->cmd_q, skb);

    // 调度发送
    hci_sched_cmd(hdev);

    return 0;
}
```

## 4. L2CAP (逻辑链路控制与适配协议)

### 4.1 L2CAP 连接建立

```c
// net/bluetooth/l2cap_core.c:800
static void l2cap_connect_req(struct l2cap_conn *conn,
                               struct l2cap_cmd_hdr *cmd)
{
    struct l2cap_conn_req *req = (void *)cmd->data;
    struct l2cap_channel *chan;

    // 创建信道
    chan = l2cap_channel_create(conn, req->psm);
    if (!chan)
        return;

    // 发送响应
    l2cap_send_cmd(conn, L2CAP_CONN_RSP, sizeof(rsp), &rsp);

    // 用户接受后发送 L2CAP_ConnectCnf
}
```

### 4.2 L2CAP 数据传输

```c
// net/bluetooth/l2cap_core.c:1200
void l2cap_recv_frame(struct l2cap_conn *conn, struct sk_buff *skb)
{
    struct l2cap_hdr *hdr = (void *)skb->data;

    // 解析 L2CAP 头
    __u16 len = le16_to_cpu(hdr->len);
    __u16 cid = le16_to_cpu(hdr->cid);

    skb_pull(skb, L2CAP_HDR_SIZE);

    // 查找信道
    chan = l2cap_get_channel(conn, cid);
    if (!chan)
        return;

    // 传递给信道
    chan->ops->recv(chan, skb);
}
```

## 5. SCO (同步面向连接)

### 5.1 SCO 连接

```c
// net/bluetooth/sco.c:200
static int sco_connect(struct sock *sk)
{
    bdaddr_t *src = &bt_sk(sk)->src;
    bdaddr_t *dst = &bt_sk(sk)->dst;

    // 创建 SCO 连接
    hci = hci_get_route(dst, src);
    if (!hci)
        return -ENOTCONN;

    // 发送连接请求
    err = hci_setup_sco(hci, &sk->sk_socket->type, dst);

    return err;
}
```

## 6. 安全管理

### 6.1 配对

```c
// net/bluetooth/hci_conn.c:300
static void hci_conn_auth(struct hci_conn *conn)
{
    struct hci_cp_auth_requested cp;

    // 设置链接密钥
    cp.handle = cpu_to_le16(conn->handle);

    // 发送认证请求
    hci_send_cmd(conn->hdev, OGF_LINK_CTL,
                 OCF_AUTH_REQUESTED, sizeof(cp), &cp);

    conn->auth_state = BT_AUTH;
}
```

### 6.2 加密

```c
// net/bluetooth/hci_conn.c:400
static void hci_conn_encrypt(struct hci_conn *conn)
{
    struct hci_cp_set_conn_encrypt cp;

    cp.handle = cpu_to_le16(conn->handle);
    cp.encrypt = 1;

    // 发送加密请求
    hci_send_cmd(conn->hdev, OGF_LINK_CTL,
                 OCF_SET_CONN_ENCRYPT, sizeof(cp), &cp);

    conn->encrypt = BT_ENCRYPT;
}
```

## 7. BLE (低功耗蓝牙)

### 7.1 GATT 服务器

```c
// net/bluetooth/gatt.c:500
struct bt_att_req *gatt_send(struct bt_att *att, void *buf, size_t len,
                             bt_att_callback_t callback, void *callback_data)
{
    struct bt_att_req *req;

    req = kzalloc(sizeof(*req), GFP_ATOMIC);

    // 添加到请求队列
    list_add_tail(&req->list, &att->req_list);

    // 发送
    hci_send_acl(att->conn->hcon, buf, len);

    return req;
}
```

### 7.2 广告

```c
// net/bluetooth/hci_core.c:1500
int hci_le_start_advertising(struct hci_dev *hdev)
{
    struct hci_cp_le_set_adv_param cp;

    memset(&cp, 0, sizeof(cp));
    cp.type = LE_ADV_IND;
    cp.own_address_type = ADDR_LE_DEV_PUBLIC;
    cp.dir_addr_type = 0;
    cp.channel_map = LE_CHAN_ALL;

    // 发送广告参数
    hci_send_cmd(hdev, OGF_LE_CTL,
                 OCF_LE_SET_ADV_PARAM, sizeof(cp), &cp);

    // 启动广告
    hci_send_cmd(hdev, OGF_LE_CTL, OCF_LE_SET_ADV_ENABLE, 1, ...);
}
```
