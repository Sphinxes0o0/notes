
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>


int main(int argc, char *argv[]) {
    int serv_sock, clnt_sock;
    FILE * readfp;
    FILE * writefp;

    struct sockaddr_in  serv_addr, clnt_addr;
    socklen_t clnt_addr_size;
    char buf[30] = {0, };
    
    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[1]));
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(serv_sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind");
        exit(1);
    }

    if (listen(serv_sock, 5) == -1) {
        perror("listen");
        exit(1);
    }

    clnt_addr_size = sizeof(clnt_addr);
    clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &clnt_addr_size);

    printf("Connected: cfd %d \n", clnt_sock);
    readfp = fdopen(serv_sock, "r");
    writefp = fdopen(clnt_sock, "w");

    fputs("FROM Server: Hi client \n", writefp);
    fputs("I love all of the world \n", writefp);
    fputs("You are awesome", writefp);
    fflush(writefp);

    fclose(writefp); //  这里最终将直接关闭sockfd, 最终的
    fgets(buf, sizeof(buf), readfp);
    fputs(buf, stdout);

    fclose(readfp);

    return 0;
}
