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


// magic number 2³² / φ ≈ 2654435761
static inline size_t hash_idx(uint32_t key) { return (key * 2654435761u) >> (32 - BUCKET_SHIFT); }