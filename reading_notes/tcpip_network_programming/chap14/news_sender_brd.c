#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define TTL 64
#define BUF_SIZE 32

int main(int argc, char *argv[]) {
    int send_sock;
    struct sockaddr_in broad_addr;
    int so_brd = 1;
    char buf[BUF_SIZE];
    FILE *fp;

    if (argc != 3) {
        printf("Usage: %s <BoradCast IP> <port> \n", argv[0]);
        exit(EXIT_SUCCESS);
    }

    send_sock = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&broad_addr, 0, sizeof(broad_addr));
    broad_addr.sin_family = AF_INET;
    broad_addr.sin_addr.s_addr = inet_addr(argv[1]);
    broad_addr.sin_port = htons(atoi(argv[2]));

    setsockopt(send_sock, SOL_SOCKET, SO_BROADCAST,
         (void *)&so_brd, sizeof(so_brd));

    if ((fp = fopen(/*"news.txt"*/"news_sender.c", "r")) == NULL) {
        perror("fopen");
        exit(EXIT_SUCCESS);
    }

    while (!feof(fp)) {
        fgets(buf, BUF_SIZE, fp);
        sendto(send_sock, buf, strlen(buf), 0,
         (const struct sockaddr *)&broad_addr, sizeof(broad_addr));
        sleep(1);
    }
    fclose(fp);
    close(send_sock);

    return 0;
}
