#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <fcntl.h>

#include <arpa/inet.h>

#define BUF_SIZE 30

int acpt_sock, recv_sock;

void urg_handler(int signo) {
    int str_len;

    char buf[BUF_SIZE];
    str_len = recv(recv_sock, buf, sizeof(buf) - 1, MSG_OOB);
    buf[str_len] = '\0';

    printf("URG MSG: %s \n", buf);
}

int main(int argc, char *argv[]) {
    struct sockaddr_in recv_addr, serv_addr;

    int str_len, state;
    socklen_t serv_addr_sz;
    struct sigaction act;

    char buf[BUF_SIZE];

    if (argc != 2) {
        printf("Usage: %s <port>\n", argv[0]);
        exit(1);
    }

    int acpt_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (acpt_sock < 0) {
        perror("socket");
        exit(1);
    }

    memset(&recv_addr, 0, sizeof(serv_addr));
    recv_addr.sin_family = AF_INET;
    recv_addr.sin_port = htons(atoi(argv[1]));
    recv_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    act.sa_handler = urg_handler;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;

    if (state == -1) {
        perror("sigaction");
        exit(1);
    }

    if (bind(acpt_sock, (const struct sockaddr *)&recv_addr, sizeof(recv_addr)) == -1) {
        perror("bind() \n");
        exit(1);
    }
    if (listen(acpt_sock, 5) == -1) {
        perror("listen()");
        exit(1);
    }

    serv_addr_sz = sizeof(serv_addr);

    recv_sock = accept(acpt_sock, (struct sockaddr *)&serv_addr, &serv_addr_sz);
    if (recv_sock == -1) {
        perror("accept()");
        exit(1);
    }
    
    int ret = fcntl(recv_sock, F_SETOWN, getpid());
    if (ret == -1) {
        perror("fcntl \n");
        exit(1);
    }
    state = sigaction(SIGURG, &act, NULL);
    while ((str_len = recv(recv_sock, buf, sizeof(buf) - 1, 0)) != 0) {
        if (str_len == -1)
            continue;
        buf[str_len] = 0;
        puts(buf);
    }

    close(recv_sock);
    close(acpt_sock);

    return 0;
}
