#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#define BUF_SIZE 40


int main(int argc, char *argv[]) {

    int fds[2];
    
    char str[] = "hello, world!";
    char str2[] = "Got message!, feedback !";
    char buf[BUF_SIZE];
    pid_t pid;

    pipe(fds);
    pid = fork();

    if (pid == 0) {
        write(fds[1], str, sizeof(str));
        sleep(2);
        read(fds[0], buf, BUF_SIZE);
        printf("child proc output: %s \n", buf);
    } else {
        read(fds[0], buf, BUF_SIZE);
        printf("parent proc output: %s \n", buf);
        write(fds[1], str2, sizeof(str2));
        sleep(3);
    }

    return 0;
}