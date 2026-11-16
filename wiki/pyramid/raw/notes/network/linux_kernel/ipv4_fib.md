# IPv4 FIB 路由结构

## 1. 模块架构

### 1.1 功能概述

FIB (Forwarding Information Base) 是内核用于快速查找路由的数据结构。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `net/ipv4/fib_frontend.c` | FIB 前端 |
| `net/ipv4/fib_semantics.c` | FIB 语义 |
| `net/ipv4/fib_lookup.h` | FIB 查找接口 |
| `net/ipv4/fib_trie.c` | FIB Trie 实现 |

## 2. 核心数据结构

### 2.1 struct fib_table

```c
// include/net/ip_fib.h:180
struct fib_table {
    struct hlist_node tb_hlist;      // 哈希链表
    u32             tb_id;          // 表 ID (AS number)
    unsigned int    tb_data_size;    // 数据大小
    unsigned char   tb_stamp;        // 时间戳
    int             (*tb_lookup)(struct fib_table *, const struct flowi4 *,
                                 struct fib_result *);
    int             (*tb_insert)(struct fib_table *, struct fib_result *,
                                 struct fib_info *, int);
    int             (*tb_delete)(struct fib_table *, struct fib_result *,
                                 struct fib_info *);
    void            (*tb_flush)(struct fib_table *);
    void            (*tb_select_default)(struct fib_table *,
                                        const struct flowi4 *,
                                        struct fib_result *);
    void            *tb_data;
};
```

### 2.2 struct fib_result

```c
// include/net/ip_fib.h:150
struct fib_result {
    __be32          prefix;          // 前缀
    unsigned char   prefixlen;       // 前缀长度
    unsigned char   nh_sel;          // 下一跳选择
    unsigned char   type;            // 路由类型
    unsigned char   scope;           // 范围
    struct fib_info *fi;             // 路由信息
    struct fib_info *fib_info;
};
```

### 2.3 struct fib_info

```c
// include/net/ip_fib.h:80
struct fib_info {
    struct hlist_node   fib_hash;     // 哈希链表
    struct list_head    fib_list;     // 路由信息链表
    struct net_device   *fib_dev;     // 关联设备
    struct fib_nh_common fib_nhc;

    unsigned int        fib_priority; // 优先级
    unsigned int        fib_prefsrc;  // 优选源地址
    unsigned int        fib_metrics[RTAX_MAX];

    u32                 fib_nh_genid;  // 代际号
};
```

### 2.4 struct fib_nh

```c
// include/net/ip_fib.h:50
struct fib_nh {
    struct net_device   *nh_device;    // 下一跳设备
    __be32              nh_gw;        // 下一跳地址
    unsigned int        nh_oif;       // 输出接口索引
    unsigned int        nh_weight;    // 权重
    int                 nh_parent;    // 父结构
};
```

## 3. Trie 结构

### 3.1 struct trie

```c
// net/ipv4/fib_trie.c:100
struct trie {
    struct node *trie;                // Trie 根节点
    size_t size;                       // Trie 大小
    struct rcu_head rcu;
};
```

### 3.2 struct key_vector

```c
// net/ipv4/fib_trie.c:80
struct key_vector {
    unsigned long bits;               // 关键位
    struct rcu_head rcu;

    // 子节点
    struct key_vector *children[0];
};
```

## 4. 查找流程

### 4.1 fib_lookup()

```c
// net/ipv4/fib_frontend.c:120
int fib_lookup(struct net *net, const struct flowi4 *flp,
               struct fib_result *res)
{
    struct fib_table *table;

    // 获取主表
    table = fib_get_table(net, RT_TABLE_MAIN);
    if (!table)
        return -ENETUNREACH;

    // 调用表特定查找
    return table->tb_lookup(table, flp, res);
}
```

### 4.2 fib_table_lookup()

```c
// net/ipv4/fib_trie.c:400
static int fib_table_lookup(struct fib_table *tb,
                           struct flowi4 *flp,
                           struct fib_result *res)
{
    struct key_vector *n, *pn;
    struct trie *t = (struct trie *)tb->tb_data;

    // 从根节点开始
    n = rcu_dereference(t->trie);

    // 按位遍历
    while (n) {
        int bit = key_extract(n->key, flp->daddr);

        // 精确匹配
        if (tkey_equals(n->key, flp->daddr))
            break;

        // 移动到子节点
        pn = n;
        n = rcu_dereference(n->children[bit]);
    }

    // 返回结果
    return fib_result_assign(res, n);
}
```

## 5. 路由优先级

### 5.1 多路径路由

```c
// fib_trie.c:500
static int fib_select_multipath(struct fib_result *res, int w)
{
    struct fib_info *fi = res->fi;
    int n, k;

    // 基于权重选择
    for (n = 0, k = 0; n < fi->fib_nhs; n++) {
        k += fi->fib_nh[n].nh_weight;
        if (k >= w)
            return n;
    }
}
```

### 5.2 最短路径优先

```c
// 基于协议优先级选择
// 1. RTN_UNICAST (单播)
// 2. RTN_LOCAL (本地)
// 3. RTN_BROADCAST (广播)
// ...
```

## 6. FIB 维护

### 6.1 fib_add()

```c
// net/ipv4/fib_semantics.c:300
int fib_add(struct fib_table *table, struct fib_config *cfg)
{
    struct fib_info *fi;

    // 1. 创建 fib_info
    fi = fib_create_info(cfg);

    // 2. 插入 trie
    hlist_del_rcu(&fi->fib_hash);
    insertbia insert_update(&table->tb_gc, fi);

    // 3. 发送变更通知
    fib_notify(FIB_EVENT_ENTRY_ADD, net, ...);
}
```

### 6.2 fib_sync_up()

```c
// net/ipv4/fib_semantics.c:600
void fib_sync_up(struct net_device *dev)
{
    // 同步设备状态到路由
    struct fib_nh *fib_nh;

    // 更新所有受影响路由的设备
}
```
