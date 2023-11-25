
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>



#define BUF_SIZE 30

int main(int argc, char *argv[]) {

    int sock;
    char message1[] = "hi";
    char message2[] = "I'm another UDP host";
    char message3[] = "Nice to meet you";

    struct sockaddr_in your_addr;
    socklen_t addr_sz;

    if (argc != 3) {
        printf("Usage: %s <IP> <port> \n", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("socket()");
        exit(1);
    }

    memset(&your_addr, 0, sizeof(your_addr));
    your_addr.sin_family = AF_INET;
    your_addr.sin_addr.s_addr = inet_addr(argv[1]);
    your_addr.sin_port = htons(atoi(argv[2]));

    sendto(sock, message1, sizeof(message1), 0, 
        (const struct sockaddr *)&your_addr, 
        sizeof(your_addr)
        );
    sendto(sock, message2, sizeof(message2), 0,
        (const struct sockaddr*)&your_addr,
        sizeof(your_addr)
        );
    sendto(sock, message3, sizeof(message3), 0, 
        (const struct sockaddr *)&your_addr, 
        sizeof(your_addr)
        );

    close(sock);
    
    return 0;
}

