#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>


void* thread_summation(void *arg);
int sum = 0;

int main(int argc, char* argv[]) {

    pthread_t id_t1, id_t2;
    int range1[] = {1, 5};
    int range2[] = {6, 10};

    if (pthread_create(&id_t1, NULL, thread_summation, (void *)&range1) != 0) {
        printf("pthread_create() error");
        exit(1);
    }

    if (pthread_create(&id_t2, NULL, thread_summation, (void *)&range2) != 0) {
        printf("pthread_create() error");
        exit(1);
    }

    if (pthread_join(id_t1, NULL) != 0) {
        printf("pthread_join() error \n");
        exit(1);
    }

    if (pthread_join(id_t2, NULL) != 0) {
        printf("pthread_join() error \n");
        exit(1);
    }

    printf("result: %d \n", sum);

    return 0;
}


void* thread_summation(void *arg) {

    int start = ((int *) arg)[0];
    int end = ((int *) arg)[1];

    while (start <= end) {
        sum += start;
        start++;
    }

    return NULL;
}