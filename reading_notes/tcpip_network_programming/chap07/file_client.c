
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    int sock;
    FILE *fp;
    char buf[30];
    int read_cnt;
    struct sockaddr_in serv_addr;


    if (argc != 3) {
        printf("Usage: %s <ip> <port> \n", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        exit(1);
    }

    fp = fopen("recvive.data", "wb");
    if (fp == NULL) {
        printf("fopen()");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_port = htons(atoi(argv[2]));

    if ( connect(sock, (const struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        printf("connect() error");
        exit(1);
    }


    while ((read_cnt = read(sock, buf, 30)) != 0)
        fwrite((void *)buf, 1, read_cnt, fp); 

    puts("Received file data");
    write(sock, "Thank you", 10);

    fclose(fp);
    close(sock);

    return 0;
}

