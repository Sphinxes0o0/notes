#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

#define BUF_SIZE 30

int main(int argc, char* argv[]) {

    int fd1[2], fd2[2];
    char str1[] = "String1: Hello \n";
    char str2[] = "String2: World \n";
    char buf[BUF_SIZE];

    pid_t pid;
    pipe(fd1);
    pipe(fd2);
    pid = fork();

    if (pid == 0) {
        write(fd1[1], str1, sizeof(str1));
        read(fd2[0], buf, BUF_SIZE);
        printf("child proc output: %s \n", buf);
    } else {
        read(fd1[0], buf, BUF_SIZE);
        printf("parent proc output: %s \n", buf);
        write(fd2[1], str2, sizeof(str2));
        sleep(3);
    }

    return 0;
}