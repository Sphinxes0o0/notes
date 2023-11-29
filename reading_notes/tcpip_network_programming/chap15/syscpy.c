#include <bits/types/struct_timeval.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/time.h>
#include <unistd.h>

#define BUF_SIZE 3

int main(int argc, char *argv[]) {

    int fd1, fd2, len;
    char buf[BUF_SIZE];

    struct timeval start, end;

    gettimeofday(&start, NULL);

    fd1 = open("../TCPIP_Src.zip", O_RDONLY);
    fd2 = open("cpy.zip", O_WRONLY|O_CREAT|O_TRUNC);

    while ((len = read(fd1, buf, sizeof(buf))) > 0) 
        write(fd2, buf, len);
        
    gettimeofday(&end, NULL);

    double elapsed = end.tv_sec - start.tv_sec + 
        (end.tv_usec - start.tv_usec) / 1e6;
    printf("run time: %.6f s \n", elapsed);
    // syscpy: run time: 0.180837 s
    // stdcpy: run time: 0.005476 s
    close(fd1);
    close(fd2);

    return 0;
}

