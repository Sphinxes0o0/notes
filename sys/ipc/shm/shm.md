# 共享内存 (Shared Memory)

## 📋 目录
- [概述](#概述)
- [工作原理](#工作原理)
- [系统调用](#系统调用)
- [实践示例](#实践示例)
- [最佳实践](#最佳实践)
- [调试与优化](#调试与优化)
- [总结](#总结)

## 概述

共享内存是最高效的进程间通信（IPC）机制，它允许多个进程直接访问同一块物理内存，从而实现零拷贝的数据共享。

### 核心优势
- **零拷贝**: 数据直接在共享内存中，无需在进程间复制
- **低延迟**: 访问速度接近本地内存访问
- **高吞吐**: 适合大量数据交换场景

## 工作原理

### 基本概念

共享内存的核心思想是：
内核在物理内存中开辟一块区域，然后将这块物理内存同时映射到多个进程的虚拟地址空间中。
这样，一个进程向这块内存中写入数据，其他进程可以立刻看到，就像操作自己的内存一样，速度非常快。

### 内核数据结构

为了管理这些共享内存段，内核使用一个名为 `shmid_ds` 的结构体来维护每一个共享内存段的信息：

```C
struct shmid_ds {
    struct ipc_perm shm_perm;   // 操作权限，类似文件权限
    size_t          shm_segsz;  // 共享内存段的大小（字节）
    pid_t           shm_lpid;   // 最后一个操作此内存段的进程ID
    pid_t           shm_cpid;   // 创建此内存段的进程ID
    shmatt_t        shm_nattch; // 当前附加到此内存段的进程数量
    time_t          shm_atime;  // 最后一次附加(attach)时间
    time_t          shm_dtime;  // 最后一次分离(detach)时间
    time_t          shm_ctime;  // 最后一次改变(change)时间
};
```

## 系统调用

### POSIX 共享内存 (推荐)

POSIX 共享内存是现代 Linux 系统推荐的方式，基于文件系统接口：

```C
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>

// 创建或打开共享内存对象
int shm_open(const char *name, int oflag, mode_t mode);

// 调整共享内存对象大小
int ftruncate(int fd, off_t length);

// 内存映射
void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);

// 取消内存映射
int munmap(void *addr, size_t length);

// 删除共享内存对象
int shm_unlink(const char *name);
```

### System V 共享内存 (传统方式)

System V 共享内存是传统的 IPC 机制：

```C
#include <sys/ipc.h>
#include <sys/shm.h>

// 创建或获取共享内存段
int shmget(key_t key, size_t size, int shmflg);

// 附加共享内存段到进程地址空间
void *shmat(int shmid, const void *shmaddr, int shmflg);

// 分离共享内存段
int shmdt(const void *shmaddr);

// 控制共享内存段
int shmctl(int shmid, int cmd, struct shmid_ds *buf);
```

## 实践示例

### 基于 POSIX 共享内存的哈希表实现

这个示例实现了一个基于共享内存的哈希表，支持多进程间的键值对存储。

#### 数据结构定义 (`shm_common.h`)

```C
#pragma once

#include <stdint.h>
#include <semaphore.h>

#define SHM_NAME "/test_shm"
#define SEM_NAME "/test_sem"

#define BUCKET_SHIFT    10
#define BUCKETS         (1 << BUCKET_SHIFT)
#define MAX_SLOTS       64

typedef struct KV {
    uint32_t key;
    uint32_t value;
} KV;

typedef struct Bucket {
    uint32_t size;
    KV kv[MAX_SLOTS];
} Bucket;

typedef struct HashMap {
    sem_t sem;
    Bucket buckets[BUCKETS];
} HashMap;

// 哈希函数：使用黄金比例
static inline size_t hash_idx(uint32_t key) { 
    return (key * 2654435761u) >> (32 - BUCKET_SHIFT); 
}
```

#### 写入进程 (`shm_write_once.c`)

```C
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <semaphore.h>
#include <unistd.h>
#include <errno.h>
#include <stdbool.h>

#include "shm_common.h"

static HashMap *open_or_create(void) {
    int fd = shm_open(SHM_NAME, O_RDWR, 0);
    bool first = false;

    if (fd == -1 && errno == ENOENT) {
        /* 第一次：创建并初始化 */
        fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
        if (fd == -1) { perror("shm_open(create)"); exit(EXIT_FAILURE); }

        if (ftruncate(fd, sizeof(HashMap)) == -1) {
            perror("ftruncate"); exit(EXIT_FAILURE);
        }
        first = true;
    } else if (fd == -1) {
        perror("shm_open"); exit(EXIT_FAILURE);
    }

    HashMap *map = mmap(NULL, sizeof(HashMap),
                        PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) { perror("mmap"); exit(EXIT_FAILURE); }
    close(fd);

    if (first) {
        sem_init(&map->sem, 1, 1);
        for (size_t i = 0; i < BUCKETS; ++i) map->buckets[i].size = 0;
    }
    return map;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <key> <value>\n", argv[0]);
        return EXIT_FAILURE;
    }
    uint32_t key = (uint32_t)atoi(argv[1]);
    uint32_t val = (uint32_t)atoi(argv[2]);

    HashMap *map = open_or_create();

    sem_wait(&map->sem);
    Bucket *b = &map->buckets[hash_idx(key)];
    if (b->size < MAX_SLOTS) {
        b->kv[b->size].key   = key;
        b->kv[b->size].value = val;
        b->size++;
        printf("Inserted %u => %u\n", key, val);
    } else {
        printf("Bucket full! key=%u dropped\n", key);
    }
    sem_post(&map->sem);

    munmap(map, sizeof(HashMap));
    return 0;
}
```

#### 读取进程 (`shm_reader.c`)

```C
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include "shm_common.h"

int main() {
    int fd = shm_open(SHM_NAME, O_RDONLY, 0);
    if (fd < 0) {
        perror("shm_open");
        return 1;
    }

    HashMap *shm = mmap(NULL, sizeof(HashMap), PROT_READ, MAP_SHARED, fd, 0);
    if (shm == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    uint32_t total = 0;
    for (uint32_t i = 0; i < BUCKETS; i++) {
        Bucket *bkt = &shm->buckets[i];
        for (uint32_t j = 0; j < bkt->size; j++) {
            printf("bucket[%u]  key=%u  value=%u\n", i, bkt->kv[j].key, bkt->kv[j].value);
            total++;
        }
    }

    printf("Total records: %u\n", total);
    munmap(shm, sizeof(HashMap));

    return 0;
}
```

#### 编译和运行

```bash
# 编译
make

# 写入数据
./shm_write_once 100 200
./shm_write_once 200 300
./shm_write_once 300 400

# 读取数据
./shm_reader

# 清理
make clean
```

## 最佳实践

### 同步机制

#### 1. 信号量同步
```C
// 使用信号量保护共享数据
sem_wait(&map->sem);
map->data = value;
sem_post(&map->sem);
```

#### 2. 原子操作
```C
// 对于简单数据类型，使用原子操作
__atomic_store_n(&shared_counter, new_value, __ATOMIC_RELEASE);
```

#### 3. 锁机制
```C
// 复杂数据结构需要额外的锁保护
pthread_mutex_lock(&shared_mutex);
// 操作共享数据
pthread_mutex_unlock(&shared_mutex);
```

### 内存管理

#### 1. 内存对齐
```C
// 确保结构体在共享内存中正确对齐
typedef struct __attribute__((packed)) SharedData {
    uint32_t magic;
    uint32_t data;
} SharedData;
```

#### 2. 生命周期管理
- **创建**: 第一个进程创建共享内存对象
- **附加**: 进程通过 `mmap` 将共享内存映射到地址空间
- **分离**: 进程通过 `munmap` 分离共享内存
- **销毁**: 最后一个进程分离后，可以删除共享内存对象

### 错误处理

#### 1. 检查共享内存存在性
```C
// 检查共享内存是否已存在
int fd = shm_open(name, O_RDWR, 0);
if (fd == -1 && errno == ENOENT) {
    // 创建新的共享内存对象
    fd = shm_open(name, O_CREAT | O_RDWR, 0666);
}
```

#### 2. 资源清理
```C
// 确保在进程退出时清理资源
void cleanup() {
    munmap(shared_mem, size);
    shm_unlink(SHM_NAME);
}
atexit(cleanup);
```

### 常见陷阱

#### 1. 同步问题
```C
// ❌ 错误：没有同步保护
map->data = value;  // 可能导致数据竞争

// ✅ 正确：使用信号量保护
sem_wait(&map->sem);
map->data = value;
sem_post(&map->sem);
```

#### 2. 内存泄漏
```C
// ❌ 错误：忘记分离共享内存
// 进程退出时没有调用 munmap

// ✅ 正确：确保分离
munmap(shared_mem, size);
```

## 调试与优化

### 调试技巧

#### 1. 查看共享内存状态
```bash
# 查看系统中的共享内存对象
ls -la /dev/shm/

# 查看共享内存统计信息
cat /proc/sysvipc/shm
```

#### 2. 使用 strace 调试
```bash
strace -e trace=shm_open,mmap,munmap ./shm_write_once 100 200
```

#### 3. 内存映射调试
```bash
# 查看进程的内存映射
cat /proc/$$/maps | grep shm
```

### 性能优化

#### 1. 批量操作
```C
// 减少同步开销，批量处理数据
sem_wait(&sem);
for (int i = 0; i < batch_size; i++) {
    process_data(&data[i]);
}
sem_post(&sem);
```

#### 2. 内存池
```C
// 预分配内存池，避免频繁分配/释放
typedef struct {
    void *pool;
    size_t used;
    size_t capacity;
} MemoryPool;
```

#### 3. 缓存友好设计
```C
// 设计数据结构时考虑缓存行对齐
typedef struct __attribute__((aligned(64))) CacheAlignedData {
    uint64_t data[8];  // 64字节，一个缓存行
} CacheAlignedData;
```

#### 4. 无锁设计
```C
// 对于简单场景，考虑无锁数据结构
typedef struct {
    atomic_uint64_t counter;
    atomic_uint64_t data;
} LockFreeStruct;
```

### 性能监控

#### 1. 内存使用监控
```bash
# 监控共享内存使用情况
watch -n 1 'ls -la /dev/shm/ | wc -l'
```

#### 2. 性能分析
```bash
# 使用 perf 分析性能
perf record -g ./shm_benchmark
perf report
```

## 总结

### 与其他 IPC 机制对比

| 机制 | 性能 | 复杂度 | 适用场景 | 同步需求 |
|------|------|--------|----------|----------|
| 共享内存 | 最高 | 高 | 大数据量、高频访问 | 需要手动同步 |
| 管道 | 中等 | 低 | 父子进程通信 | 自动同步 |
| 消息队列 | 中等 | 中等 | 结构化消息传递 | 自动同步 |
| Socket | 较低 | 中等 | 网络通信、跨机器 | 自动同步 |
| 信号 | 高 | 低 | 异步通知 | 无同步 |

### 使用建议

1. **选择场景**: 共享内存适合需要高性能数据交换的场景
2. **同步设计**: 必须仔细设计同步机制，避免数据竞争
3. **错误处理**: 完善的错误处理和资源清理是必须的
4. **性能优化**: 考虑批量操作、内存池等优化技术
5. **调试工具**: 善用系统工具进行调试和性能分析

共享内存是最高效的 IPC 机制，但需要开发者自己处理同步问题。在需要高性能数据交换的场景下，它是首选方案。通过合理的设计和优化，可以充分发挥其性能优势。

