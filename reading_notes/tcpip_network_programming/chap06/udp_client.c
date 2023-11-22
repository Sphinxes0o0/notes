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

    int sock, str_len;
    char message[BUF_SIZE];
    socklen_t addr_sz;

    struct sockaddr_in serv_addr, from_addr;

    if (argc != 3) {
        printf("Usage: %s <IP> <port> \n", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("socket()");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_port = htons(atoi(argv[2]));

    while (true) {
        fputs("input message(q for quit): ", stdout);
        fgets(message, sizeof(message), stdin);

        if (!strcmp(message, "q\n"))
            break;

        sendto(sock, message, strlen(message), 0, (struct sockaddr*)&serv_addr, sizeof(serv_addr));

        addr_sz = sizeof(from_addr);
        str_len = recvfrom(sock, message, BUF_SIZE, 0, (struct sockaddr*)&from_addr, &addr_sz);
        
        printf("%d", str_len);
        message[str_len] = 0;
        printf("Messge from server: %s", message);
    }
    close(sock);

    return 0;
}