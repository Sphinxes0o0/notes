#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define BUF_SIZE 30


int main(int argc, char *argv[]) {

    int sock;
    char message[BUF_SIZE];
    int len;
    struct sockaddr_in serv_addr;

    if (argc != 3) {
        printf("Usage: %s <ip> <port> \n", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket ");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[2]));
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);

    if (connect(sock, (const struct sockaddr *)&serv_addr, 
        sizeof(serv_addr)) == -1) {
        perror("connect");
        exit(1);
    } else {
        puts("Connected .....");
    }

    FILE* readfp = fdopen(sock, "r");
    FILE* writefp = fdopen(sock, "w");
    while (1) {
        fputs("input message(q to quit): ", stdout);
        fgets(message, BUF_SIZE, stdin);
        if (!strcmp(message, "q\n") || !strcmp(message, "Q\n")) 
            break;

        fputs(message, writefp);
        fflush(writefp);
        fgets(message, BUF_SIZE, readfp);
        printf("Message from server: %s", message);
    } 
    fclose(writefp);
    fclose(readfp);
    close(sock);

    return 0;
}