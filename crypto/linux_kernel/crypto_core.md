# Linux 内核 Crypto 子系统核心框架分析

## 1. Crypto 子系统概述

Linux 内核 Crypto 子系统是一个统一的密码学算法框架,提供了对称加密、非对称加密、哈希、随机数生成等多种密码学功能的抽象接口。

### 1.1 核心组件位置

| 组件 | 路径 |
|------|------|
| 核心 API | `/Users/sphinx/github/linux/crypto/api.c` |
| 算法注册 | `/Users/sphinx/github/linux/crypto/algapi.c` |
| 算法管理器 | `/Users/sphinx/github/linux/crypto/algboss.c` |
| 头文件 | `/Users/sphinx/github/linux/include/crypto/` |
| 主头文件 | `/Users/sphinx/github/linux/include/linux/crypto.h` |

### 1.2 核心数据结构概览

```
crypto_alg_list (全局算法链表)
     │
     ├── crypto_alg (算法基础结构)
     │     ├── cra_type → crypto_type (算法类型)
     │     └── cra_flags (算法标志)
     │
     ├── crypto_larval (幼虫状态算法,用于延迟测试)
     │
     ├── crypto_template (算法模板)
     │     └── instances (模板实例列表)
     │
     └── crypto_tfm (Transform,算法运行时实例)
```

### 1.3 分配函数体系

Crypto 子系统提供两类分配接口:

**同步分配:**
- `crypto_alloc_base()` - 分配基础 transform (`api.c:469`)
- `crypto_alloc_tfm()` - 分配指定类型的 transform (`internal.h:146`)
- `crypto_create_tfm()` - 从已有算法创建 transform (`algapi.h:132`)

**异步分配:**
- `crypto_alloc_tfm_node()` - 支持 NUMA 节点指定 (`api.c:627`)

### 1.4 注册函数体系

**算法注册:**
- `crypto_register_alg()` - 注册单个算法 (`algapi.c:431`)
- `crypto_register_algs()` - 批量注册 (`algapi.c:510`)
- `crypto_unregister_alg()` - 注销 (`algapi.c:491`)

**模板注册:**
- `crypto_register_template()` - 注册模板 (`algapi.c:535`)
- `crypto_register_templates()` - 批量注册 (`algapi.c:559`)

### 1.5 同步 vs 异步接口

| 特性 | 同步接口 | 异步接口 |
|------|----------|----------|
| 调用方式 | blocking | non-blocking |
| 完成通知 | 立即返回 | 通过 callback |
| 典型函数 | `crypto_cipher_encrypt()` | `crypto_ahash_init()` |
| 等待机制 | 进程睡眠 | `crypto_wait_req()` |
| 适用场景 | 常规加密操作 | 硬件加速,大数据处理 |

---

## 2. 核心数据结构详解

### 2.1 struct crypto_alg - 算法基础结构

**定义位置:** `/Users/sphinx/github/linux/include/linux/crypto.h:332`

```c
struct crypto_alg {
    struct list_head cra_list;       // 全局算法链表节点
    struct list_head cra_users;      // 使用此算法的其他算法

    u32 cra_flags;                  // 算法标志
    unsigned int cra_blocksize;     // 块大小
    unsigned int cra_ctxsize;        // 上下文大小
    unsigned int cra_alignmask;      // 对齐掩码
    unsigned int cra_reqsize;        // 请求上下文大小

    int cra_priority;                // 优先级(同名算法选择)
    refcount_t cra_refcnt;           // 引用计数

    char cra_name[CRYPTO_MAX_ALG_NAME];        // 通用名称
    char cra_driver_name[CRYPTO_MAX_ALG_NAME]; // 驱动名称

    const struct crypto_type *cra_type;         // 算法类型回调

    union {
        struct cipher_alg cipher;    // 分组密码回调
    } cra_u;

    int (*cra_init)(struct crypto_tfm *tfm);    // 初始化回调
    void (*cra_exit)(struct crypto_tfm *tfm);  // 退出回调
    void (*cra_destroy)(struct crypto_alg *alg); // 销毁回调

    struct module *cra_module;       // 所属模块
} CRYPTO_MINALIGN_ATTR;
```

**cra_flags 算法类型标志** (`crypto.h:24-37`):

```c
#define CRYPTO_ALG_TYPE_MASK      0x0000000f  // 类型掩码
#define CRYPTO_ALG_TYPE_CIPHER    0x00000001  // 原始分组密码
#define CRYPTO_ALG_TYPE_AEAD      0x00000003  // 带关联数据的认证加密
#define CRYPTO_ALG_TYPE_SKCIPHER  0x00000005  // 流式分组密码
#define CRYPTO_ALG_TYPE_RNG       0x0000000c  // 随机数生成器
#define CRYPTO_ALG_TYPE_HASH      0x0000000e  // 哈希/摘要
#define CRYPTO_ALG_TYPE_AHASH     0x0000000f  // 异步哈希
```

**cra_flags 状态标志** (`crypto.h:41-140`):

```c
#define CRYPTO_ALG_LARVAL         0x00000010  // 幼虫状态(等待测试)
#define CRYPTO_ALG_DEAD           0x00000020  // 已废弃
#define CRYPTO_ALG_DYING          0x00000040  // 正在消亡
#define CRYPTO_ALG_ASYNC          0x00000080  // 异步算法
#define CRYPTO_ALG_NEED_FALLBACK  0x00000100  // 需要软件回退
#define CRYPTO_ALG_TESTED         0x00000400  // 已通过测试
#define CRYPTO_ALG_INSTANCE       0x00000800  // 模板实例
#define CRYPTO_ALG_KERN_DRIVER_ONLY 0x00001000 // 仅内核驱动使用
#define CRYPTO_ALG_INTERNAL      0x00002000  // 内部算法
```

### 2.2 struct crypto_tfm - Transform 结构

**定义位置:** `/Users/sphinx/github/linux/include/linux/crypto.h:411`

```c
struct crypto_tfm {
    refcount_t refcnt;               // 引用计数

    u32 crt_flags;                   // Transform 标志

    int node;                        // NUMA 节点

    struct crypto_tfm *fb;           // 回退 Transform

    void (*exit)(struct crypto_tfm *tfm); // 退出回调

    struct crypto_alg *__crt_alg;    // 关联的算法

    void *__crt_ctx[] CRYPTO_MINALIGN_ATTR; // 算法特定上下文
};
```

**关键宏/内联函数:**

```c
// 获取 Transform 上下文 (algapi.h:185)
static inline void *crypto_tfm_ctx(struct crypto_tfm *tfm)
{
    return tfm->__crt_ctx;
}

// 获取算法名称 (crypto.h:442)
static inline const char *crypto_tfm_alg_name(struct crypto_tfm *tfm)
{
    return tfm->__crt_alg->cra_name;
}

// 判断是否异步 (crypto.h:488)
static inline bool crypto_tfm_is_async(struct crypto_tfm *tfm)
{
    return tfm->__crt_alg->cra_flags & CRYPTO_ALG_ASYNC;
}
```

### 2.3 struct crypto_type - 算法类型

**定义位置:** `/Users/sphinx/github/linux/crypto/internal.h:36`

```c
struct crypto_type {
    unsigned int (*ctxsize)(struct crypto_alg *alg, u32 type, u32 mask);
    // 计算算法上下文大小

    unsigned int (*extsize)(struct crypto_alg *alg);
    // 计算扩展大小

    int (*init_tfm)(struct crypto_tfm *tfm);
    // 初始化 Transform

    void (*show)(struct seq_file *m, struct crypto_alg *alg);
    // 展示算法信息 (/proc)

    int (*report)(struct sk_buff *skb, struct crypto_alg *alg);
    // 报告算法信息 (netlink)

    void (*free)(struct crypto_instance *inst);
    // 释放算法实例

    void (*destroy)(struct crypto_alg *alg);
    // 销毁算法

    unsigned int type;               // 类型值
    unsigned int maskclear;          // 清除的标志掩码
    unsigned int maskset;            // 设置的标志掩码
    unsigned int tfmsize;           // Transform 大小
    unsigned int algsize;            // 算法结构大小
};
```

### 2.4 struct crypto_template - 模板结构

**定义位置:** `/Users/sphinx/github/linux/include/crypto/algapi.h:74`

```c
struct crypto_template {
    struct list_head list;           // 模板全局链表
    struct hlist_head instances;     // 该模板的实例列表
    struct hlist_head dead;          // 已废弃实例列表
    struct module *module;           // 所属模块

    struct work_struct free_work;    // 延迟释放工作队列

    int (*create)(struct crypto_template *tmpl, struct rtattr **tb);
    // 创建实例回调

    char name[CRYPTO_MAX_ALG_NAME];  // 模板名称
};
```

**模板生命周期:**

1. **创建** - `template->create()` 分配实例
2. **注册** - `crypto_register_instance()` 注册到系统
3. **使用** - 用户通过 `crypto_alloc_xxx()` 发现并使用
4. **销毁** - 引用计数归零时调度 `free_work`

### 2.5 struct crypto_larval - 幼虫状态

**定义位置:** `/Users/sphinx/github/linux/crypto/internal.h:28`

```c
struct crypto_larval {
    struct crypto_alg alg;           // 基础算法结构
    struct crypto_alg *adult;        // 成年(真实)算法
    struct completion completion;     // 测试完成信号
    u32 mask;                        // 搜索掩码
    bool test_started;               // 测试已开始标志
};
```

**幼虫机制流程:**

```
算法注册
    │
    ▼
crypto_register_alg()
    │
    ▼
创建 crypto_larval (cra_flags |= CRYPTO_ALG_LARVAL)
    │
    ▼
调度自测 ─────────────────────────────────────┐
    │                                         │
    ▼                                         │
alg_test() 运行测试                           │
    │                                         │
    ├── 成功: adult 算法标记 TESTED           │
    │         唤醒 completion                 │
    │                                         │
    └── 失败: 标记 DEAD                       │
              唤醒 completion                 │
                                             │
◀────────────────────────────────────────────┘
    │
    ▼
crypto_larval_wait() 返回 adult 算法
```

### 2.6 struct crypto_instance - 算法实例

**定义位置:** `/Users/sphinx/github/linux/include/crypto/algapi.h:59`

```c
struct crypto_instance {
    struct crypto_alg alg;           // 基础算法结构

    struct crypto_template *tmpl;    // 所属模板

    union {
        struct hlist_node list;      // 模板实例链表节点
        struct crypto_spawn *spawns; // 依赖的 spawn 列表
    };

    void *__ctx[] CRYPTO_MINALIGN_ATTR; // 上下文数据
};
```

### 2.7 struct crypto_spawn - 算法依赖

**定义位置:** `/Users/sphinx/github/linux/include/crypto/algapi.h:87`

```c
struct crypto_spawn {
    struct list_head list;           // 链表节点
    struct crypto_alg *alg;          // 依赖的算法
    union {
        struct crypto_instance *inst; // 实例指针(注册后)
        struct crypto_spawn *next;   // 下一个 spawn(注册前)
    };
    const struct crypto_type *frontend; // 前端类型
    u32 mask;                        // 类型掩码
    bool dead;                       // 已废弃标志
    bool registered;                 // 已注册标志
};
```

---

## 3. 算法注册流程详解

### 3.1 核心数据结构关系图

```
                    ┌─────────────────────────────────────────┐
                    │           crypto_alg_list               │
                    │  (全局算法链表, 由 crypto_alg_sem 保护)   │
                    └─────────────────────────────────────────┘
                                      │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         ▼
    ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
    │ crypto_alg  │           │crypto_larval│           │crypto_alg   │
    │  (普通算法) │           │ (幼虫状态)  │           │  (模板实例) │
    └─────────────┘           └─────────────┘           └─────────────┘
           │                         │                         │
           │                         │                         │
           ▼                         │                         ▼
    cra_users (依赖列表)              │              tmpl → crypto_template
           │                         │                         │
           │                         ▼                         ▼
           │                  adult ──────► 算法测试完成后    instances
           │                                    指向真实算法   (实例列表)
           │                                         │
           └─────────────────────────────────────────┘
                         (spawn 依赖关系)

    ┌──────────────────────────────────────────────────────────────┐
    │                    crypto_template_list                      │
    │  (模板列表)                                                   │
    └──────────────────────────────────────────────────────────────┘
```

### 3.2 crypto_register_alg() 详细流程

**位置:** `algapi.c:431-476`

```c
int crypto_register_alg(struct crypto_alg *alg)
{
    struct crypto_larval *larval;
    bool test_started = false;
    LIST_HEAD(algs_to_put);
    int err;

    // Step 1: 清除 DEAD 标志并检查算法有效性
    alg->cra_flags &= ~CRYPTO_ALG_DEAD;
    err = crypto_check_alg(alg);  // 验证名称、对齐、优先级等
    if (err)
        return err;

    // Step 2: 如果需要复制算法(CRYPTO_ALG_DUP_FIRST)
    if (alg->cra_flags & CRYPTO_ALG_DUP_FIRST &&
        !WARN_ON_ONCE(alg->cra_destroy)) {
        // 复制算法结构到 kmalloc 内存
    }

    // Step 3: 获取写锁并注册算法
    down_write(&crypto_alg_sem);
    larval = __crypto_register_alg(alg, &algs_to_put);
    if (!IS_ERR_OR_NULL(larval)) {
        test_started = crypto_boot_test_finished();
        larval->test_started = test_started;
    }
    up_write(&crypto_alg_sem);

    // Step 4: 处理注册结果
    if (IS_ERR(larval)) {
        crypto_alg_put(alg);
        return PTR_ERR(larval);
    }

    // Step 5: 调度自测或清理
    if (test_started)
        crypto_schedule_test(larval);  // 调度到 kthread 运行测试
    else
        crypto_remove_final(&algs_to_put);

    return 0;
}
```

### 3.3 __crypto_register_alg() 内部实现

**位置:** `algapi.c:301-357`

```c
static struct crypto_larval *
__crypto_register_alg(struct crypto_alg *alg, struct list_head *algs_to_put)
{
    struct crypto_alg *q;
    struct crypto_larval *larval;
    int ret = -EAGAIN;

    // Step 1: 检查是否为 DEAD 状态
    if (crypto_is_dead(alg))
        goto err;

    INIT_LIST_HEAD(&alg->cra_users);

    ret = -EEXIST;
    // Step 2: 检查名称冲突
    list_for_each_entry(q, &crypto_alg_list, cra_list) {
        if (q == alg)
            goto err;
        if (crypto_is_moribund(q))  // DYING 或 DEAD
            continue;
        if (crypto_is_larval(q)) {
            // 幼虫状态: 只检查 driver_name 冲突
            if (!strcmp(alg->cra_driver_name, q->cra_driver_name))
                goto err;
            continue;
        }
        // 检查名称冲突
        if (!strcmp(q->cra_driver_name, alg->cra_name) ||
            !strcmp(q->cra_driver_name, alg->cra_driver_name) ||
            !strcmp(q->cra_name, alg->cra_driver_name))
            goto err;
    }

    // Step 3: 分配测试幼虫(如果需要自测)
    larval = crypto_alloc_test_larval(alg);
    if (IS_ERR(larval))
        goto out;

    // Step 4: 加入全局链表
    list_add(&alg->cra_list, &crypto_alg_list);

    if (larval) {
        // 有自测: 添加幼虫,标记为未测试
        alg->cra_flags &= ~CRYPTO_ALG_TESTED;
        list_add(&larval->alg.cra_list, &crypto_alg_list);
    } else {
        // 无自测: 直接标记为已测试
        alg->cra_flags |= CRYPTO_ALG_TESTED;
        crypto_alg_finish_registration(alg, algs_to_put);
    }

out:
    return larval;

err:
    larval = ERR_PTR(ret);
    goto out;
}
```

### 3.4 模板注册流程

**位置:** `algapi.c:535-556`

```c
int crypto_register_template(struct crypto_template *tmpl)
{
    struct crypto_template *q;
    int err = -EEXIST;

    // 初始化延迟释放工作队列
    INIT_WORK(&tmpl->free_work, crypto_destroy_instance_workfn);

    down_write(&crypto_alg_sem);

    // 检查 FIPS 模式模块签名
    crypto_check_module_sig(tmpl->module);

    // 检查是否已注册
    list_for_each_entry(q, &crypto_template_list, list) {
        if (q == tmpl)
            goto out;
    }

    // 加入模板链表
    list_add(&tmpl->list, &crypto_template_list);
    err = 0;
out:
    up_write(&crypto_alg_sem);
    return err;
}
```

### 3.5 模板实例创建流程

模板实例通过 `crypto_lookup_template()` + `template->create()` 创建:

**算法查找流程** (`api.c:338-368`):

```c
struct crypto_alg *crypto_alg_mod_lookup(const char *name, u32 type, u32 mask)
{
    // Step 1: 处理 INTERNAL 标志
    if (!((type | mask) & CRYPTO_ALG_INTERNAL))
        mask |= CRYPTO_ALG_INTERNAL;

    // Step 2: 查找或创建幼虫
    larval = crypto_larval_lookup(name, type, mask);
    if (IS_ERR(larval) || !crypto_is_larval(larval))
        return larval;

    // Step 3: 发送探查通知
    ok = crypto_probing_notify(CRYPTO_MSG_ALG_REQUEST, larval);
    if (ok == NOTIFY_STOP)
        alg = crypto_larval_wait(larval, type, mask);
    else {
        crypto_mod_put(larval);
        alg = ERR_PTR(-ENOENT);
    }

    // 清理幼虫
    crypto_larval_kill(container_of(larval, struct crypto_larval, alg));
    return alg;
}
```

**cryptomgr_probe 探查线程** (`algboss.c:50-73`):

```c
static int cryptomgr_probe(void *data)
{
    struct cryptomgr_param *param = data;
    struct crypto_template *tmpl;
    int err = -ENOENT;

    // 查找模板
    tmpl = crypto_lookup_template(param->template);
    if (!tmpl)
        goto out;

    // 调用模板的 create 函数创建实例
    do {
        err = tmpl->create(tmpl, param->tb);
    } while (err == -EAGAIN && !signal_pending(current));

    crypto_tmpl_put(tmpl);

out:
    // 通知等待者结果
    param->larval->adult = ERR_PTR(err);
    param->larval->alg.cra_flags |= CRYPTO_ALG_DEAD;
    complete_all(&param->larval->completion);
    crypto_alg_put(&param->larval->alg);
    kfree(param);
    module_put_and_kthread_exit(0);
}
```

---

## 4. 请求处理详解

### 4.1 crypto_init_ops() / crypto_exit_ops()

**crypto_exit_ops()** (`api.c:371-377`):

```c
static void crypto_exit_ops(struct crypto_tfm *tfm)
{
    const struct crypto_type *type = tfm->__crt_alg->cra_type;

    // 调用类型特定的 exit 回调
    if (type && tfm->exit)
        tfm->exit(tfm);
}
```

**Transform 初始化流程** (`api.c:408-437`):

```c
struct crypto_tfm *__crypto_alloc_tfmgfp(struct crypto_alg *alg, u32 type,
                                         u32 mask, gfp_t gfp)
{
    struct crypto_tfm *tfm;
    unsigned int tfm_size;
    int err = -ENOMEM;

    // Step 1: 计算 Transform 大小并分配
    tfm_size = sizeof(*tfm) + crypto_ctxsize(alg, type, mask);
    tfm = kzalloc(tfm_size, gfp);
    if (tfm == NULL)
        goto out_err;

    // Step 2: 初始化基础字段
    tfm->__crt_alg = alg;
    refcount_set(&tfm->refcnt, 1);

    // Step 3: 调用算法的 cra_init
    if (!tfm->exit && alg->cra_init && (err = alg->cra_init(tfm)))
        goto cra_init_failed;

    goto out;

cra_init_failed:
    crypto_exit_ops(tfm);
    if (err == -EAGAIN)
        crypto_shoot_alg(alg);  // 标记为失活,避免重复选择
    kfree(tfm);
out_err:
    tfm = ERR_PTR(err);
out:
    return tfm;
}
```

### 4.2 crypto_ctxsize() - 计算上下文大小

**位置:** `api.c:379-398`

```c
static unsigned int crypto_ctxsize(struct crypto_alg *alg, u32 type, u32 mask)
{
    const struct crypto_type *type_obj = alg->cra_type;
    unsigned int len;

    // 计算对齐后的大小
    len = alg->cra_alignmask & ~(crypto_tfm_ctx_alignment() - 1);

    if (type_obj)
        // 类型特定的上下文大小
        return len + type_obj->ctxsize(alg, type, mask);

    switch (alg->cra_flags & CRYPTO_ALG_TYPE_MASK) {
    case CRYPTO_ALG_TYPE_CIPHER:
        len += crypto_cipher_ctxsize(alg);
        break;
    default:
        BUG();
    }

    return len;
}
```

### 4.3 异步请求处理

**crypto_async_request 结构** (`crypto.h:188`):

```c
struct crypto_async_request {
    struct list_head list;        // 队列链表
    crypto_completion_t complete; // 完成回调
    void *data;                  // 回调私有数据
    struct crypto_tfm *tfm;      // 关联的 Transform

    u32 flags;                   // 请求标志
};
```

**crypto_wait 等待机制** (`crypto.h:364-398`):

```c
struct crypto_wait {
    struct completion completion;
    int err;
};

#define DECLARE_CRYPTO_WAIT(_wait) \
    struct crypto_wait _wait = { \
        COMPLETION_INITIALIZER_ONSTACK((_wait).completion), 0 }

static inline int crypto_wait_req(int err, struct crypto_wait *wait)
{
    switch (err) {
    case -EINPROGRESS:
    case -EBUSY:
        // 等待完成
        wait_for_completion(&wait->completion);
        reinit_completion(&wait->completion);
        err = wait->err;
        break;
    }
    return err;
}
```

### 4.4 请求队列操作

**入队** (`algapi.c:948-968`):

```c
int crypto_enqueue_request(struct crypto_queue *queue,
                          struct crypto_async_request *request)
{
    int err = -EINPROGRESS;

    if (unlikely(queue->qlen >= queue->max_qlen)) {
        // 队列满
        if (!(request->flags & CRYPTO_TFM_REQ_MAY_BACKLOG)) {
            err = -ENOSPC;
            goto out;
        }
        err = -EBUSY;
        // 加入 backlog
        if (queue->backlog == &queue->list)
            queue->backlog = &request->list;
    }

    queue->qlen++;
    list_add_tail(&request->list, &queue->list);

out:
    return err;
}
```

**出队** (`algapi.c:982-998`):

```c
struct crypto_async_request *crypto_dequeue_request(struct crypto_queue *queue)
{
    struct list_head *request;

    if (unlikely(!queue->qlen))
        return NULL;

    queue->qlen--;

    // 先处理 backlog
    if (queue->backlog != &queue->list)
        queue->backlog = queue->backlog->next;

    request = queue->list.next;
    list_del_init(request);

    return list_entry(request, struct crypto_async_request, list);
}
```

---

## 5. 模板机制详解

### 5.1 模板结构与实例关系

```
┌─────────────────────────────────────────────────────────────────┐
│                     crypto_template                             │
│  name: "cbc"                                                    │
│  create: cbc_create  ──────────────────────────────────────┐    │
│  module: THIS_MODULE                                         │    │
│  instances ─────────────────────────────────────────────►   │    │
└──────────────────────────────────────────────────────────────│────┘
                                                                   │
                                                                   │ hlist
                                                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     crypto_instance                             │
│  alg.cra_name: "cbc(aes)"                                       │
│  alg.cra_driver_name: "cbc_base"                               │
│  tmpl → crypto_template                                         │
│  __ctx[] ─────────────────────────────────────────────────►    │
└──────────────────────────────────────────────────────────────│────┘
                                                                   │
                                                                   │ 指向
                                                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     crypto_spawn                                │
│  alg → aes 算法                                                  │
│  inst → crypto_instance                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 模板创建示例: CBC

CBC 是一个模板,实现为 `crypto/cbc.c`:

```c
// CBC 模板定义
static struct crypto_template cbc_tmpl = {
    .name = "cbc",
    .create = cbc_create,
    .module = THIS_MODULE,
};

// cbc_create 实现 (简化)
static int cbc_create(struct crypto_template *tmpl, struct rtattr **tb)
{
    struct crypto_instance *inst;
    struct crypto_spawn *spawn;
    // 1. 分配实例上下文
    inst = skcipher_alloc_instance_simple(tmpl, tb);
    // 2. 获取底层算法(如 aes)的 spawn
    spawn = skcipher_instance_ctx(inst);
    // 3. 设置算法属性
    inst->alg.base.cra_blocksize = ...;
    inst->alg.encrypt = cbc_encrypt;
    inst->alg.decrypt = cbc_decrypt;
    // 4. 注册实例
    return crypto_register_instance(tmpl, inst);
}
```

### 5.3 模板实例注册

**crypto_register_instance()** (`algapi.c:643-703`):

```c
int crypto_register_instance(struct crypto_template *tmpl,
                             struct crypto_instance *inst)
{
    struct crypto_larval *larval;
    struct crypto_spawn *spawn;
    u32 fips_internal = 0;
    LIST_HEAD(algs_to_put);
    int err;

    // Step 1: 检查算法有效性
    err = crypto_check_alg(&inst->alg);
    if (err)
        return err;

    // Step 2: 设置模块和标志
    inst->alg.cra_module = tmpl->module;
    inst->alg.cra_flags |= CRYPTO_ALG_INSTANCE;
    inst->alg.cra_destroy = crypto_destroy_instance;

    down_write(&crypto_alg_sem);

    // Step 3: 处理 spawns
    larval = ERR_PTR(-EAGAIN);
    for (spawn = inst->spawns; spawn;) {
        struct crypto_spawn *next;

        if (spawn->dead)
            goto unlock;

        next = spawn->next;
        spawn->inst = inst;
        spawn->registered = true;

        // 继承 FIPS 内部标志
        fips_internal |= spawn->alg->cra_flags;

        crypto_mod_put(spawn->alg);

        spawn = next;
    }

    inst->alg.cra_flags |= (fips_internal & CRYPTO_ALG_FIPS_INTERNAL);

    // Step 4: 注册算法
    larval = __crypto_register_alg(&inst->alg, &algs_to_put);
    if (IS_ERR(larval))
        goto unlock;
    else if (larval)
        larval->test_started = true;

    // Step 5: 加入模板实例列表
    hlist_add_head(&inst->list, &tmpl->instances);
    inst->tmpl = tmpl;

unlock:
    up_write(&crypto_alg_sem);

    if (IS_ERR(larval))
        return PTR_ERR(larval);

    if (larval)
        crypto_schedule_test(larval);
    else
        crypto_remove_final(&algs_to_put);

    return 0;
}
```

### 5.4 模板销毁流程

**crypto_destroy_instance()** (`algapi.c:93-102`):

```c
static void crypto_destroy_instance(struct crypto_alg *alg)
{
    struct crypto_instance *inst = container_of(alg,
                                struct crypto_instance, alg);
    struct crypto_template *tmpl = inst->tmpl;

    // 标记 refcnt 为 -1,表示正在销毁
    refcount_set(&alg->cra_refcnt, -1);
    // 调度延迟释放
    schedule_work(&tmpl->free_work);
}
```

**crypto_destroy_instance_workfn()** (`algapi.c:72-91`):

```c
static void crypto_destroy_instance_workfn(struct work_struct *w)
{
    struct crypto_template *tmpl = container_of(w,
                                struct crypto_template, free_work);
    struct crypto_instance *inst;
    struct hlist_node *n;
    HLIST_HEAD(list);

    down_write(&crypto_alg_sem);

    // 收集 refcnt 为 -1 的实例
    hlist_for_each_entry_safe(inst, n, &tmpl->dead, list) {
        if (refcount_read(&inst->alg.cra_refcnt) != -1)
            continue;
        hlist_del(&inst->list);
        hlist_add_head(&inst->list, &list);
    }
    up_write(&crypto_alg_sem);

    // 释放实例
    hlist_for_each_entry_safe(inst, n, &list, list)
        crypto_free_instance(inst);
}
```

---

## 6. 架构图

### 6.1 Crypto 子系统整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Userspace Applications                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Kernel Crypto API (crypto/)                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     High-Level Interfaces                        │    │
│  │  crypto_alloc_skcipher()  │  crypto_aead_init()  │  crypto_rng  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Template Layer (如 cbc, gcm, pcrypt)         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Core API (api.c)                             │    │
│  │  crypto_register_alg()  │  crypto_alloc_tfm()  │  crypto_has_alg │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  Algorithm Registry (algapi.c)                   │    │
│  │      crypto_alg_list  │  crypto_template_list  │  larval       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Algorithm Implementations                           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │ Software (e.g.,│  │ Hardware (e.g.,│  │ Template (e.g.,│              │
│  │ aes-generic)   │  │ aes-ice)       │  │ cbc(aes))      │              │
│  └────────────────┘  └────────────────┘  └────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 算法查找与分配时序图

```
用户: crypto_alloc_skcipher("cbc(aes)", ...)
          │
          ▼
┌─────────────────────────────────────┐
│ crypto_alg_mod_lookup("cbc(aes)")  │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ crypto_larval_lookup()              │
│   - 解析名称: template="cbc"       │
│     inner_name="aes"                │
│   - 创建 crypto_larval             │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ crypto_probing_notify()             │
│   - 发送 CRYPTO_MSG_ALG_REQUEST    │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ cryptomgr_schedule_probe()          │
│   - 创建 cryptomgr_param          │
│   - 启动 kthread: cryptomgr_probe  │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ cryptomgr_probe() (内核线程)        │
│   - crypto_lookup_template("cbc")  │
│   - tmpl->create(tmpl, tb)        │
│     - 分配 crypto_instance        │
│     - crypto_grab_spawn("aes")     │
│     - crypto_register_instance()   │
│   - 唤醒 larval->completion        │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ crypto_larval_wait() 返回 adult    │
│   = crypto_larval.alg              │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ crypto_create_tfm_node(alg, ...)   │
│   - 分配 crypto_skcipher           │
│   - 调用 init_tfm()               │
│   - 调用 cra_init()                │
└─────────────────────────────────────┘
          │
          ▼
返回 crypto_skcipher 指针给用户
```

---

## 7. 关键文件索引

| 文件 | 作用 | 关键函数 |
|------|------|----------|
| `crypto/api.c` | 核心 Transform API | `crypto_alloc_base()`, `crypto_destroy_tfm()` |
| `crypto/algapi.c` | 算法注册与查找 | `crypto_register_alg()`, `crypto_alg_mod_lookup()` |
| `crypto/algboss.c` | 算法自动加载管理器 | `cryptomgr_probe()`, `cryptomgr_schedule_test()` |
| `crypto/internal.h` | 内部类型定义 | `struct crypto_type`, `struct crypto_larval` |
| `crypto/skcipher.c` | 流式分组密码实现 | `crypto_register_skcipher()` |
| `crypto/aead.c` | AEAD 接口实现 | `crypto_register_aead()` |
| `include/linux/crypto.h` | 用户层头文件 | `struct crypto_alg`, `struct crypto_tfm` |
| `include/crypto/algapi.h` | 算法层头文件 | `struct crypto_template`, `crypto_register_*` |

---

## 8. 总结

Linux 内核 Crypto 子系统的核心设计要点:

1. **分层架构**: 从用户 API 到具体算法实现,层层抽象
2. **延迟测试机制**: 通过 larval 状态实现算法自测而不阻塞注册
3. **模板机制**: 通过模板动态组合算法(如 cbc = cbc_template(cipher))
4. **引用计数管理**: 完善的生命周期管理,防止 Use-After-Free
5. **同步/异步支持**: 统一的接口同时支持阻塞和非阻塞操作
6. **NUMA 支持**: 可指定 NUMA 节点分配 Transform
