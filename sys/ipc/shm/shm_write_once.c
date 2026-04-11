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