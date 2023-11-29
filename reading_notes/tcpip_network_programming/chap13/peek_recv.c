#include <netinet/in.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/socket.h>

#define BUF_SIZE 30

int main(int argc, char *argv[]) {
    int acpt_sock, recv_sock;
    struct sockaddr_in acpt_addr, recv_addr;
    int str_len, state;
    socklen_t recv_addr_sz;
    char buf[BUF_SIZE];

    if (argc != 2) {
        printf("Usage: %s <port>\n", argv[0]);
        exit(1);
    }

    acpt_sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&acpt_addr, 0, sizeof(acpt_addr));
    acpt_addr.sin_family = AF_INET;
    acpt_addr.sin_port = htons(atoi(argv[1]));
    acpt_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(acpt_sock, (const struct sockaddr *)&acpt_addr, sizeof(acpt_addr)) == -1) {
        perror("bind");
        exit(1);
    }

    if (listen(acpt_sock, 5) == -1) {
        perror("listen");
        exit(1);
    }

    recv_addr_sz = sizeof(recv_addr);
    recv_sock = accept(acpt_sock, (struct sockaddr *)&recv_addr, &recv_addr_sz);
    if (recv_sock == -1) {
        perror("accept");
        exit(1);
    }

    while (true) {
        str_len = recv(recv_sock, buf, sizeof(buf) - 1, MSG_PEEK|MSG_DONTWAIT);
        if (str_len > 0) 
            break;
    }

    buf[str_len] = 0;
    printf("Buffering %d bytes %s\n", str_len, buf);

    str_len = recv(recv_sock, buf, sizeof(buf) - 1, 0);
    buf[str_len] = 0;
    printf("READ Again: %s \n", buf);

    close(recv_sock);
    close(acpt_sock);

    return 0;
}
