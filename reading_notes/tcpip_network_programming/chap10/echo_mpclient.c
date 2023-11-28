#include <netinet/in.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>


void read_routine(int sock, char * buf) {
    while (true) {
        int str_len = read(sock, buf, 30);
        if (str_len == 0)
            return;
        buf[str_len] = 0;
        printf("Message from server: %s", buf);
    }
}


void write_routine(int sock, char *buf) {
    while (true) {
        fgets(buf, 30, stdin);
        if (!strcmp(buf, "q\n") || !strcmp(buf, "Q\n")) {
            shutdown(sock, SHUT_WR);
            return;
        }
        write(sock, buf, strlen(buf));
    }

}


int main(int argc, char * argv[]) {
    int sock;
    pid_t pid;
    char buf[30];
    struct sockaddr_in serv_addr;

    if (argc != 3) {
        printf("Usage: %s <ip> <port>", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_port = htons(atoi(argv[2]));
    serv_addr.sin_family = AF_INET;

    if (connect(sock, (const struct sockaddr *)&serv_addr,
     sizeof(serv_addr)) == -1) {
        perror("connect");
        exit(1);
    }

    pid = fork();
    if (pid == 0)
        write_routine(sock, buf);
    else
        read_routine(sock, buf);

    close(sock);

    return 0;
}
