#include "dummy_mbox.h"
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

dummy_mbox_t *mbox;

// 生产者线程函数
void *producer_thread(void *arg) {
  int id = *(int *)arg;
  char *messages[] = {"Hello", "World", "From", "Producer"};

  for (int i = 0; i < 4; i++) {
    char *msg = malloc(32);
    snprintf(msg, 32, "%s %d-%d", messages[i], id, i);

    printf("Producer %d: Sending message '%s'\n", id, msg);
    dummy_mbox_post(&mbox, msg);
    sleep(1);
  }

  return NULL;
}

// 消费者线程函数
void *consumer_thread(void *arg) {
  int id = *(int *)arg;

  for (int i = 0; i < 8; i++) {
    char *msg = (char *)dummy_mbox_fetch(&mbox);
    printf("Consumer %d: Received message '%s'\n", id, msg);
    free(msg);
    sleep(1);
  }

  return NULL;
}

int main() {
  pthread_t producers[4];
  pthread_t consumers[5];
  int producer_ids[4] = {1, 2, 3, 4};
  int consumer_ids[5] = {1, 2, 3, 4, 5};

  // 创建邮箱
  if (dummy_mbox_new(&mbox) != ERR_OK) {
    printf("Failed to create mailbox\n");
    return -1;
  }

  printf("Creating producer and consumer threads...\n");

  // 创建生产者线程
  for (int i = 0; i < 4; i++) {
    pthread_create(&producers[i], NULL, producer_thread, &producer_ids[i]);
  }

  // 创建消费者线程
  for (int i = 0; i < 5; i++) {
    pthread_create(&consumers[i], NULL, consumer_thread, &consumer_ids[i]);
  }

  // 等待所有线程完成
  for (int i = 0; i < 4; i++) {
    pthread_join(producers[i], NULL);
  }

  for (int i = 0; i < 5; i++) {
    pthread_join(consumers[i], NULL);
  }

  // 释放邮箱
  dummy_mbox_free(&mbox);

  printf("All threads finished, mailbox test completed.\n");
  return 0;
}