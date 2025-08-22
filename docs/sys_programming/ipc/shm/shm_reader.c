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
