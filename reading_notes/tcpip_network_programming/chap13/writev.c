#include <stdio.h>
#include <string.h>
#include <sys/uio.h>

int main(int argc, char *argv[]) {

    struct iovec iov[2];
    char buf1[] = "ABCDEFG";
    char buf2[] = "1234567";

    int str_len;

    iov[0].iov_base = buf1;
    iov[0].iov_len = 3;//strlen(buf1);
    iov[1].iov_base = buf2;
    iov[1].iov_len = 4;//strlen(buf2);

    str_len = writev(1, iov, 2);
    puts("");
    printf("Write bytes: %d \n", str_len);

    return 0;
}
