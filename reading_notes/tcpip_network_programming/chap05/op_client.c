
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    int sock, result, opnd_cnt, i;
    char opmsg[1024];
    struct sockaddr_in serv_addr;

    if (argc != 3) {
        printf("Usage: %s <IP> <PORT> \n", argv[0]);
        exit(1);
    }

    sock = socket(PF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[2]));

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1 ) {
        perror("connect");
        exit(1);
    } else {
        puts("Connected ......");
    }

    fputs("Operand count: ", stdout);
    scanf("%d", &opnd_cnt);
    opmsg[0] = (char)opnd_cnt;

    for (i = 0; i < opnd_cnt; i++) {
        printf("Operand %d: ", i + 1);
        scanf("%d", (int *)&opmsg[i*4 + 1]);
    }

    fgetc(stdin);
    fputs("Operator:", stdout);
    scanf("%c", &opmsg[opnd_cnt*4 + 1]);
    write(sock, opmsg, opnd_cnt*4 + 2);
    printf("writing");


    read(sock, &result, 4);
    printf("reading.");

    printf("Operation result:%d \n", result);
    close(sock);

    return 0;
}