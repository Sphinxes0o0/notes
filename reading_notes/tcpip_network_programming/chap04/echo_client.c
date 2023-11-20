#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>



int main(int argc, char *argv[]) {

    int sock, str_len;
    char message[1024];
    struct sockaddr_in serv_addr;

    if (argc != 3) {
        printf("Usage: %s<IP> <port> \n", argv[0]);
        exit(1);
    }

    sock  = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket() ");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_port = htons(atoi(argv[2]));

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("connect()");
        exit(0);
    } else {
        puts("Connected ......");
    }

    while(1) {
        fputs("Input Message(Q to Quit):  ", stdout);
        fgets(message, 1024, stdin);

        if ( !strcmp(message, "q\n") || !strcmp(message, "Q\n"))
            break;

        printf("str len: %lu, string: %s", sizeof(message), message);
        write(sock, message, strlen(message));
        str_len = read(sock, message, 1024 - 1);
        printf("str len: %d", str_len);
        message[str_len] = 0;
        printf("Message from server: %s", message);
    }

    close(sock);

    return 0;
}
