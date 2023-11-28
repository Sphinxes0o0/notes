#include <bits/types/struct_timeval.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define BUF_SIZE 30

int main(int argc, char* argv[]) {

    int serv_sock, clnt_sock;
    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t clnt_addr_size, adr_sz;

    struct timeval timeout;

    char buf[BUF_SIZE];
    fd_set read_fds, copy_reads;
    int fd_max, str_len, fd_num, i;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (struct sockaddr*) &serv_addr, sizeof(serv_addr)) == -1){
        perror("bind failed");
        exit(1);
    }

    if (listen(serv_sock, 10) == -1) {
        perror("listen failed");
        exit(1);
    }

    FD_ZERO(&read_fds);
    FD_SET(serv_sock, &read_fds);
    fd_max = serv_sock;

    while (true) {
        copy_reads = read_fds;
        timeout.tv_sec = 5;
        timeout.tv_usec = 5000;
        if (select(fd_max + 1, &copy_reads, NULL, NULL, &timeout) == -1) 
            break;
        if (fd_num == 0)
            continue;

        for (i = 0; i <= fd_max + 1; i++) {
            if (FD_ISSET(i, &copy_reads)) {
                if (i == serv_sock) { // contection reques 
                    clnt_addr_size = sizeof(clnt_addr);
                    clnt_sock = accept(serv_sock, (struct sockaddr*) &clnt_addr, &clnt_addr_size);
                    FD_SET(clnt_sock, &read_fds);
                    if (clnt_sock > fd_max)
                        fd_max = clnt_sock;
                    printf("connected client: %d \n", clnt_sock);
                } else { //read message
                    str_len = read(i, buf, BUF_SIZE);
                    if (str_len == 0) { // close request
                        FD_CLR(i, &read_fds);
                        close(i);
                        printf("close client: %d \n", i);
                    } else {
                        write(i, buf, str_len); // echo
                    }
                }
            }
        }
    }
    close(serv_sock);

    return 0;
}

