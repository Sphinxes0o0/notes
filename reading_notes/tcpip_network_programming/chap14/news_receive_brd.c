#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define BUF_SIZE 32

int main(int argc, char *argv[]) {

    int recv_sock, str_len;
    char buf[BUF_SIZE];
    struct sockaddr_in addr;
    // struct ip_mreq join_addr;

    if (argc != 2) {
        printf("Usage: %s <PORT> \n", argv[0]);
        exit(EXIT_SUCCESS);
    }

    recv_sock = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(atoi(argv[1]));

    if (bind(recv_sock, (const struct sockaddr *)&addr, sizeof(addr)) == -1) {
        perror("bind");
        exit(EXIT_FAILURE);
    }

    while (1) {
        str_len = recvfrom(recv_sock, buf, BUF_SIZE-1, 0, NULL, NULL);
        if (str_len < 0)
            break;
        buf[str_len] = 0;
        fputs(buf, stdout);
    }
    close(recv_sock);

    return 0;
}