#include <stdio.h>
#include <fcntl.h>

int main(void) {
    FILE *fp;
    int fd = open("data.dat", O_WRONLY|O_CREAT|O_TRUNC);

    printf("first file descriptor: %d \n",fd );
    fp = fdopen(fd, "w");
    fputs("TCP/IP SOCKET PROGRAMMING \n", fp);
    printf("second file descriptor:%d \n", fileno(fp));
    fclose(fp);

    return 0;
}