# net/dsa - 分布式交换机架构

## 1. 模块架构

### 1.1 功能概述

DSA (Distributed Switch Architecture) 是一种框架，允许在多个物理端口之间共享单个网络设备驱动程序。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/dsa/dsa.c` | DSA 核心 |
| `net/dsa/slave.c` | 从设备 |
| `net/dsa/tag_dsa.c` | DSA 标签 |
| `include/net/dsa.h` | DSA 定义 |

## 2. 核心数据结构

### 2.1 struct dsa_chip_data

```c
// include/net/dsa.h:60
struct dsa_chip_data {
    struct device *master_dev;        // 主设备 (CPU 端口)
    int num_ports;                   // 端口数量
    struct dsa_port_data *port_data; // 端口数据
    struct device *pd;               // 平台数据
    char **port_names;               // 端口名称
};
```

### 2.2 struct dsa_port_data

```c
// include/net/dsa.h:80
struct dsa_port_data {
    const char *name;               // 端口名称
    struct device *dev;             // 端口设备
    struct dsa_switch *dst;         // 所属 switch
    int index;                      // 端口索引
    struct net_device *slave;       // 从设备
};
```

### 2.3 struct dsa_switch

```c
// include/net/dsa.h:100
struct dsa_switch {
    struct device *dev;
    struct dsa_chip_data *pd;
    const struct dsa_switch_ops *ops;

    int num_ports;                  // 端口数
    unsigned long port_bitmap;      // 端口位图
    unsigned long enabled_ports;    // 启用端口

    struct dsa_port_data *ports;
    struct dsa_switch_driver *drv;
};
```

### 2.4 struct dsa_switch_ops

```c
// include/net/dsa.h:150
struct dsa_switch_ops {
    const char *name;

    // 交换机配置
    int (*setup)(struct dsa_switch *ds);
    int (*set_addr)(struct dsa_switch *ds, u8 *addr);

    // 端口配置
    int (*port_enable)(struct dsa_switch *ds, int port);
    void (*port_disable)(struct dsa_switch *ds, int port);

    // 标签
    int (*tag_protocol)(struct dsa_switch *ds);

    // FDB
    int (*fdb_add)(struct dsa_switch *ds, int port,
                   const unsigned char *addr);
    int (*fdb_del)(struct dsa_switch *ds, int port,
                   const unsigned char *addr);
    int (*fdb_getnext)(struct dsa_switch *ds, int port,
                        unsigned char *addr);
};
```

## 3. 从设备 (slave)

### 3.1 dsa_slave_create()

```c
// net/dsa/slave.c:200
static int dsa_slave_create(struct dsa_switch *ds, struct device *parent,
                            int port)
{
    struct net_device *slave_dev;

    // 分配网络设备
    slave_dev = alloc_netdev(sizeof(struct dsa_slave_priv),
                              ds->ports[port].name, NET_NAME_UNKNOWN,
                              ether_setup);

    // 设置从设备操作
    slave_dev->netdev_ops = &dsa_slave_netdev_ops;
    slave_dev->ethtool_ops = &dsa_slave_ethtool_ops;

    // 设置 MAC 地址
    memcpy(slave_dev->dev_addr, ds->ops->get_addr(ds), ETH_ALEN);

    // 注册
    register_netdev(slave_dev);

    ds->ports[port].slave = slave_dev;
    return 0;
}
```

### 3.2 dsa_slave_xmit()

```c
// net/dsa/slave.c:400
netdev_tx_t dsa_slave_xmit(struct sk_buff *skb, struct net_device *dev)
{
    struct dsa_slave_priv *p = netdev_priv(dev);
    struct sk_buff *nskb;

    // 添加 DSA 标签
    nskb = p->dst->ops->tag_xmit(skb, p->port);
    if (!nskb)
        return NETDEV_TX_OK;

    // 发送到主设备
    dev->master->netdev_ops->ndo_start_xmit(nskb, dev->master);

    return NETDEV_TX_OK;
}
```

### 3.3 dsa_slave_rcv()

```c
// net/dsa/slave.c:500
rx_handler_result_t dsa_slave_rcv(struct sk_buff **pskb)
{
    struct dsa_slave_priv *p;
    struct sk_buff *skb = *pskb;
    int port;

    // 解析 DSA 标签
    port = dsa_slave_parse_tag(skb);
    if (port < 0)
        return RX_HANDLER_PASS;

    // 获取从设备
    p = dsa_slave_dev_get(port);

    // 推送标签
    skb_push(skb, ETH_HLEN);

    // 传递到协议栈
    netif_receive_skb(skb);

    return RX_HANDLER_CONSUMED;
}
```

## 4. 标签协议

### 4.1 DSA 标签格式

```
+---------+--------+--------+--------+--------+--------+
|  DA (6) |  SA (6)| EtherType | Payload |  FCS  |
+---------+--------+--------+--------+--------+--------+
                          ^
                          |
            +-------------+-------------+
            |   DSA Tag (4 bytes)     |
            +---------+----+----------+
            |   Source   |  EtherType |
            |   Port     |            |
            +---------+----+----------+
```

### 4.2 tag_dsa_xmit()

```c
// net/dsa/tag_dsa.c:50
struct sk_buff *tag_dsa_xmit(struct sk_buff *skb, int port)
{
    struct dsa_ethertype_tag *tag;

    // 添加 DSA 标签
    skb_push(skb, sizeof(*tag));

    tag = (struct dsa_ethertype_tag *)skb->data;
    tag->proto = htons(ETH_P_DSA);
    tag->port = port;

    return skb;
}
```

## 5. FDB (Forwarding Database)

### 5.1 dsa_fdb_add()

```c
// net/dsa/slave.c:600
int dsa_fdb_add(struct dsa_switch *ds, int port,
                const unsigned char *addr)
{
    if (!ds->ops->fdb_add)
        return -EOPNOTSUPP;

    return ds->ops->fdb_add(ds, port, addr);
}
```

### 5.2 老化

```c
// 定期检查 FDB 条目
// 移除过期的条目
```

## 6. 配置示例

### 6.1 Device Tree

```dts
switch@0 {
    compatible = "marvell,mv88e6085";
    reg = <0>;

    dsa,member = <0 0>;

    ports {
        #address-cells = <1>;
        #size-cells = <0>;

        cpu@0 {
            reg = <0>;
            label = "cpu";
            ethernet = <&gmac0>;
        };

        swp0@1 {
            reg = <1>;
            label = "wan";
        };

        swp1@2 {
            reg = <2>;
            label = "lan0";
        };
    };
};
```

### 6.2 命令行

```bash
# 查看 DSA 端口
ip link

# 配置端口 VLAN
bridge vlan add dev swp0 vid 100
```
