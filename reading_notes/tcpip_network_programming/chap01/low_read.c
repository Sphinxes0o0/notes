/*
#include <unistd.h>

ssize_t read(int fd, void *buf, size_t count);


*/
#include <fcntl.h> // open()
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUF_SIZE 1024

int main(int argc, char *argv[]) {

    int fd;
    char buf[BUF_SIZE];
    
    fd = open("data.txt", O_RDWR);
    if (fd == -1) {
        perror("open()");
        exit(1);
    }

    printf("file descriptor: %d \n", fd);

    if (read(fd, buf, sizeof(buf)) == -1) {
        perror("read()");
        exit(1);
    }
    
    printf("file data: %s", buf);

    close(fd);

    return 0;
}