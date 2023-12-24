#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>


void* thread_main(void *arg);

int main(int argc, char* argv[]) {

    pthread_t t_id;
    int thread_param = 5;

    if (pthread_create(&t_id, NULL, thread_main, (void *)&thread_param) != 0) {
        printf("pthread_create() error");
        exit(1);
    }
    sleep(2);
    printf("end of main");

    return 0;
}


void* thread_main(void *arg) {

    int i;

    int cnt =* ((int *)arg);
    for (i = 0; i < cnt; i++) {
        sleep(1);
        printf("runing thread \n");
    }

    return NULL;
}