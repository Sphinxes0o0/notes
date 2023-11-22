#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdbool.h>

#include <arpa/inet.h>
#include <netinet/in.h>

#define BUF_SIZE 30

int main(int argc, char *argv[]) {

    int serv_sock, str_len;
    char message[BUF_SIZE];
    socklen_t clnt_addr_sz;

    struct sockaddr_in serv_addr, clnt_addr;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (serv_sock == -1) {
        perror("socket()");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind()");
        exit(1);
    }
    printf("binded: ip %c port %d", serv_addr.sin_addr.s_addr, serv_addr.sin_port);

    while (true) {
        clnt_addr_sz = sizeof(clnt_addr);

        str_len = recvfrom(serv_sock, 
                        message, BUF_SIZE, 0,
                        (struct sockaddr*)&clnt_addr, 
                        &clnt_addr_sz);

        sendto(serv_sock, message, str_len, 0, (struct sockaddr*)&clnt_addr, clnt_addr_sz);
    }
    close(serv_sock);

    return 0;
}