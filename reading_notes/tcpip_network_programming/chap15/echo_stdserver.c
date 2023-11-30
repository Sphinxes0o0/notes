#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define BUF_SIZE 30

int main(int argc, char * argv[]) {

    int serv_sock, clnt_sock;
    char message[BUF_SIZE];
    int len;

    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t addr_size;

    FILE *readfp, *writefp;
    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[1]));
    serv_addr.sin_addr.s_addr =  htonl(INADDR_ANY);

    if (bind(serv_sock, (const struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind");
        exit(1);
    }

    if (listen(serv_sock, 5) == -1) {
        perror("listen");
        exit(1);
    }

    addr_size = sizeof(clnt_addr);
    for( int i = 0; i < 5; i++) {
        clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &addr_size);
        if (clnt_sock == -1) {
            perror("accept()");
            exit(1);
        } else 
            printf("Connected client %d \n", i+1);

        readfp = fdopen(clnt_sock, "r");
        writefp = fdopen(clnt_sock, "w");
        while (!feof(readfp)) {
            fgets(message, BUF_SIZE, readfp);
            fputs(message, writefp);
            fflush(writefp);
        }

    }
    close(serv_sock);

    return 0;
}
