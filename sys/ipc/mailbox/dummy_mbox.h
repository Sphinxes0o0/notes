#pragma once

#include <pthread.h>

// 定义错误码
#define ERR_OK 0
#define ERR_MEM -1
#define SYS_MBOX_EMPTY -2
#define SYS_ARCH_TIMEOUT -3

// 定义邮箱大小
#define DUMMY_MBOX_SIZE 128

typedef struct dummy_mbox dummy_mbox_t;

typedef struct {
  int count;
  pthread_mutex_t mutex;
  pthread_cond_t cond;
} dummy_sem_t;

struct dummy_mbox {
  int first, last;
  void *msgs[DUMMY_MBOX_SIZE];
  dummy_sem_t *not_empty;
  dummy_sem_t *not_full;
  dummy_sem_t *mutex;
  int wait_send;
};

// 函数声明
int dummy_mbox_new(dummy_mbox_t **mb);
void dummy_mbox_free(dummy_mbox_t **mb);
void dummy_mbox_post(dummy_mbox_t **mb, void *msg);
int dummy_mbox_trypost(dummy_mbox_t **mb, void *msg);
void *dummy_mbox_fetch(dummy_mbox_t **mb);
int dummy_mbox_tryfetch(dummy_mbox_t **mb, void **msg);
