#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define BUF_SIZE 30

int main(int argc, char *argv[]) {
    int sockfd;
    struct sockaddr_in servaddr;
    char buf[BUF_SIZE];

    if (argc != 3) {
        printf("Usage: %s <ip> <port> \n", argv[0]);
        exit(1);
    }


    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(atoi(argv[2]));
    servaddr.sin_addr.s_addr = inet_addr(argv[1]);

    int ret = connect(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr));
    if (ret == -1) {
        perror("conntect() ");
        exit(1);
    }

    write(sockfd, "123", strlen("123"));
    send(sockfd, "4", strlen("4"), MSG_OOB);
    write(sockfd, "567", strlen("567"));
    send(sockfd, "890", strlen("890"), MSG_OOB);


    close(sockfd);


    return 0;
}
