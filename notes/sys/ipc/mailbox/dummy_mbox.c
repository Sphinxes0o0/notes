#include "dummy_mbox.h"
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

// 创建信号量
static dummy_sem_t *dummy_sem_new(int count) {
  dummy_sem_t *sem = (dummy_sem_t *)malloc(sizeof(dummy_sem_t));
  if (sem != NULL) {
    sem->count = count;
    pthread_mutex_init(&sem->mutex, NULL);
    pthread_cond_init(&sem->cond, NULL);
  }
  return sem;
}

// 释放信号量
static void dummy_sem_free(dummy_sem_t *sem) {
  if (sem != NULL) {
    pthread_cond_destroy(&sem->cond);
    pthread_mutex_destroy(&sem->mutex);
    free(sem);
  }
}

// 等待信号量
static void dummy_sem_wait(dummy_sem_t *sem) {
  pthread_mutex_lock(&sem->mutex);
  while (sem->count <= 0) {
    pthread_cond_wait(&sem->cond, &sem->mutex);
  }
  sem->count--;
  pthread_mutex_unlock(&sem->mutex);
}

// 信号量增加（通知）
static void dummy_sem_signal(dummy_sem_t *sem) {
  pthread_mutex_lock(&sem->mutex);
  sem->count++;
  pthread_cond_signal(&sem->cond);
  pthread_mutex_unlock(&sem->mutex);
}

// 创建邮箱
int dummy_mbox_new(dummy_mbox_t **mb) {
  dummy_mbox_t *mbox;

  mbox = (dummy_mbox_t *)malloc(sizeof(dummy_mbox_t));
  if (mbox == NULL) {
    return ERR_MEM;
  }

  mbox->first = mbox->last = 0;
  mbox->not_empty = dummy_sem_new(0); // 初始为空
  mbox->not_full = dummy_sem_new(0);  // 初始为满
  mbox->mutex = dummy_sem_new(1);     // 初始可访问
  mbox->wait_send = 0;

  *mb = mbox;
  return ERR_OK;
}

// 释放邮箱
void dummy_mbox_free(dummy_mbox_t **mb) {
  if (mb != NULL && *mb != NULL) {
    dummy_mbox_t *mbox = *mb;
    dummy_sem_free(mbox->not_empty);
    dummy_sem_free(mbox->not_full);
    dummy_sem_free(mbox->mutex);
    free(mbox);
    *mb = NULL;
  }
}

// 阻塞式发送消息
void dummy_mbox_post(dummy_mbox_t **mb, void *msg) {
  dummy_mbox_t *mbox;
  int first;

  if (mb == NULL || *mb == NULL)
    return;
  mbox = *mb;

  dummy_sem_wait(mbox->mutex); // 获取互斥锁

  // 如果队列满了，则等待
  while ((mbox->last + 1) >= (mbox->first + DUMMY_MBOX_SIZE)) {
    mbox->wait_send++;
    dummy_sem_signal(mbox->mutex);
    dummy_sem_wait(mbox->not_full);
    dummy_sem_wait(mbox->mutex);
    mbox->wait_send--;
  }

  // 将消息放入队列
  mbox->msgs[mbox->last % DUMMY_MBOX_SIZE] = msg;

  first = (mbox->last == mbox->first) ? 1 : 0;
  mbox->last++;

  // 如果这是队列中的第一条消息，通知等待的读取者
  if (first) {
    dummy_sem_signal(mbox->not_empty);
  }

  dummy_sem_signal(mbox->mutex); // 释放互斥锁
}

// 非阻塞式发送消息
int dummy_mbox_trypost(dummy_mbox_t **mb, void *msg) {
  dummy_mbox_t *mbox;
  int first;

  if (mb == NULL || *mb == NULL)
    return ERR_MEM;
  mbox = *mb;

  dummy_sem_wait(mbox->mutex); // 获取互斥锁

  // 如果队列满了，直接返回错误
  if ((mbox->last + 1) >= (mbox->first + DUMMY_MBOX_SIZE)) {
    dummy_sem_signal(mbox->mutex);
    return ERR_MEM;
  }

  // 将消息放入队列
  mbox->msgs[mbox->last % DUMMY_MBOX_SIZE] = msg;

  first = (mbox->last == mbox->first) ? 1 : 0;
  mbox->last++;

  // 如果这是队列中的第一条消息，通知等待的读取者
  if (first) {
    dummy_sem_signal(mbox->not_empty);
  }

  dummy_sem_signal(mbox->mutex); // 释放互斥锁
  return ERR_OK;
}

// 阻塞式接收消息
void *dummy_mbox_fetch(dummy_mbox_t **mb) {
  dummy_mbox_t *mbox;
  void *msg = NULL;

  if (mb == NULL || *mb == NULL)
    return NULL;
  mbox = *mb;

  dummy_sem_wait(mbox->mutex); // 获取互斥锁

  // 如果队列为空，则等待
  while (mbox->first == mbox->last) {
    dummy_sem_signal(mbox->mutex);
    dummy_sem_wait(mbox->not_empty);
    dummy_sem_wait(mbox->mutex);
  }

  // 从队列中取出消息
  msg = mbox->msgs[mbox->first % DUMMY_MBOX_SIZE];
  mbox->first++;

  // 如果有线程在等待发送消息，通知它们
  if (mbox->wait_send) {
    dummy_sem_signal(mbox->not_full);
  }

  dummy_sem_signal(mbox->mutex); // 释放互斥锁
  return msg;
}

// 非阻塞式接收消息
int dummy_mbox_tryfetch(dummy_mbox_t **mb, void **msg) {
  dummy_mbox_t *mbox;

  if (mb == NULL || *mb == NULL)
    return SYS_MBOX_EMPTY;
  mbox = *mb;

  dummy_sem_wait(mbox->mutex); // 获取互斥锁

  // 如果队列为空，直接返回
  if (mbox->first == mbox->last) {
    dummy_sem_signal(mbox->mutex);
    return SYS_MBOX_EMPTY;
  }

  // 从队列中取出消息
  if (msg != NULL) {
    *msg = mbox->msgs[mbox->first % DUMMY_MBOX_SIZE];
  }

  mbox->first++;

  // 如果有线程在等待发送消息，通知它们
  if (mbox->wait_send) {
    dummy_sem_signal(mbox->not_full);
  }

  dummy_sem_signal(mbox->mutex); // 释放互斥锁
  return ERR_OK;
}
