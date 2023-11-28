#include <bits/types/struct_timeval.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/select.h>
#include <sys/time.h>


int main(int argc, char *argv[]) {

    fd_set read_fds, temps;

    int ret, str_len;
    char buf[BUFSIZ];
    struct timeval timeout;
    FD_ZERO(&read_fds);
    FD_SET(0, &read_fds);// 监视标准输入的变化

    while (1) {
        temps = read_fds;
        timeout.tv_sec = 5;
        timeout.tv_usec = 0;
        ret = select(1, &temps, NULL, NULL, &timeout);
        if (ret == -1) {
            perror("select");
            exit(EXIT_FAILURE);
        } else if (ret == 0) {
            puts("Time-out");
        } else {
            if (FD_ISSET(0, &temps)) {
                str_len = read(0, buf, BUFSIZ);
                if (str_len == -1) {
                    perror("read");
                    exit(EXIT_FAILURE);
                }
                buf[str_len] = 0;
                printf("message from console: %s", buf);
            }
        }
    }

    return 0;
}
