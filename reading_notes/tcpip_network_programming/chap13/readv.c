#include <bits/types/struct_iovec.h>
#include <stdio.h>
#include <sys/uio.h>
#include <string.h>

int main(int argc, char **argv) {
    struct iovec vec[2];
    char buf[30] = {0,};
    char buf2[60] = {0,};

    int str_len = 0;

    vec[0].iov_base = buf;
    vec[0].iov_len = 2;
    vec[1].iov_base = buf2;
    vec[1].iov_len = 30;

    str_len = readv(0, vec, 2);
    printf("Read bytes: %d \n", str_len);
    printf("First Message: %s \n", buf);
    printf("Second Message: %s \n", buf2);
 
    return 0;
}

