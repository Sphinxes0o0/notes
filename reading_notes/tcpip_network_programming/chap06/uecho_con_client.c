
#include <arpa/inet.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>



int main(int argc, char *argv[]) {

    int sock, str_len;
    char message[BUFSIZ];

    struct sockaddr_in serv_addr;

    if (argc != 3) {
        printf("Usage: %s <IP> <PORT> \n", argv[0]);
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

    // 指定收发对象之后， 不仅可以使用sendto, recvfrom, 还可以使用 write, read
    int ret = connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
    if (ret == -1) {
        perror("connect(), errno");
        exit(1);
    }

    while (true) {
        fputs("Input Message(Q to Quit):  ", stdout);
        fgets(message, sizeof(message), stdin);

        if (!strcmp(message, "q\n")) break;

        write(sock, message, strlen(message));
        str_len = read(sock, message, sizeof(message) - 1);
        message[str_len] = 0;
        printf("Message from server: %s \n", message);
    }
    close(sock);

    return 0;
}