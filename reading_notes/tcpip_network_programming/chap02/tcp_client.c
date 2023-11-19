#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <arpa/inet.h>

void error_handling(char *msg) {
    fputs(msg, stderr);
    fputc('\n', stderr);
    exit(1);
}


int main(int argc, char* argv[]) {
    int sock;
    struct sockaddr_in serv_addr;
    char message[30];

    int str_len = 0, read_len = 0, idx = 0;

    if (argc != 3) {
        printf("Usage: %s <IP> <port> \n", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
        error_handling("socket() ");

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_port = htons(atoi(argv[2]));

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(message) - 1) == -1)
        error_handling("connect()");

    // str_len = read(sock, message, sizeof(message) - 1);
    // if (str_len == -1)
    //     error_handling("read()");
    while ( (read_len = read(sock, &message[idx++], 1)) ) {
        // printf("read_len %d", read_len);
        if (read_len == -1) 
            error_handling("read()");
        
        str_len += read_len;
    }

    printf("message from server: %s , call count: %d", message, str_len);
    close(sock);

    return 0;
}
