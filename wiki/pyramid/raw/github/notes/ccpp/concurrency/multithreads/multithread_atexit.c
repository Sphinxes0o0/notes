#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>

// 全局变量用于标识不同的atexit函数
int main_thread_id;
int child_thread_id;

// 主线程的atexit回调函数
void main_thread_exit_handler() {
    printf("主线程的atexit函数被调用 - 程序即将退出\n");
    printf("主线程ID: %d\n", main_thread_id);
}

// 子线程的atexit回调函数
void child_thread_exit_handler() {
    printf("子线程的atexit函数被调用 - 程序即将退出\n");
    printf("子线程ID: %d\n", child_thread_id);
}

// 第二个主线程atexit函数，演示执行顺序
void main_thread_exit_handler2() {
    printf("主线程的第二个atexit函数被调用\n");
}

// 子线程函数
void* child_thread_function(void* arg) {
    int thread_num = *(int*)arg;
    child_thread_id = thread_num;
    
    printf("子线程 %d 开始执行\n", thread_num);
    
    // 子线程注册atexit函数
    if (atexit(child_thread_exit_handler) != 0) {
        fprintf(stderr, "子线程注册atexit函数失败\n");
        return NULL;
    }
    printf("子线程 %d 注册了atexit函数\n", thread_num);
    
    // 子线程做一些工作
    printf("子线程 %d 正在工作...\n", thread_num);
    sleep(2);
    
    printf("子线程 %d 即将结束\n", thread_num);
    return NULL;
}

int main() {
    printf("=== 多线程atexit演示程序 ===\n\n");
    
    main_thread_id = 1;
    
    // 主线程注册atexit函数
    if (atexit(main_thread_exit_handler) != 0) {
        fprintf(stderr, "主线程注册第一个atexit函数失败\n");
        exit(1);
    }
    printf("主线程注册了第一个atexit函数\n");
    
    // 主线程注册第二个atexit函数（演示LIFO顺序）
    if (atexit(main_thread_exit_handler2) != 0) {
        fprintf(stderr, "主线程注册第二个atexit函数失败\n");
        exit(1);
    }
    printf("主线程注册了第二个atexit函数\n");
    
    // 创建子线程
    pthread_t threads[2];
    int thread_nums[2] = {1, 2};
    
    printf("\n--- 创建子线程 ---\n");
    for (int i = 0; i < 2; i++) {
        if (pthread_create(&threads[i], NULL, child_thread_function, &thread_nums[i]) != 0) {
            fprintf(stderr, "创建线程 %d 失败\n", i + 1);
            exit(1);
        }
        printf("创建了子线程 %d\n", i + 1);
    }
    
    // 主线程做一些工作
    printf("\n--- 主线程工作 ---\n");
    printf("主线程正在工作...\n");
    sleep(1);
    
    // 等待所有子线程完成
    printf("\n--- 等待子线程完成 ---\n");
    for (int i = 0; i < 2; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            fprintf(stderr, "等待线程 %d 失败\n", i + 1);
            exit(1);
        }
        printf("子线程 %d 已完成\n", i + 1);
    }
    
    printf("\n--- 主线程即将退出 ---\n");
    printf("注意：atexit函数将按照LIFO（后进先出）的顺序被调用\n");
    printf("程序即将退出，atexit函数将被调用...\n\n");
    
    return 0; // 程序正常结束，atexit函数将被调用
} 