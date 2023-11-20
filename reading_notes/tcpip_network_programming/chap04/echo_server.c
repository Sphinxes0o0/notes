
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h> //read()


int main(int argc, char* argv[]) {

    int serv_sock, clnt_sock;
    char message[1024];
    int str_len, i;

    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t clnt_addr_sz;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (serv_sock == -1) {
        perror("sockeet()");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind()");
        exit(1);
    }

    if (listen(serv_sock, 5) == -1) {
        perror("listen() ");
        exit(1);
    }

    clnt_addr_sz = sizeof(clnt_addr);

    for (i = 0; i < 5; i++) {
        clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &clnt_addr_sz);
        if (clnt_sock == -1) {
            perror("accept()");
            exit(1);
        } else {
            printf("Connected client %d \n", i + 1);
        }

        while((str_len = read(clnt_sock, message, 1024)) != 0) {
            printf(" got message from client \n: %s \n", message);
            write(clnt_sock, message, str_len);
        }
            
        
        close(clnt_sock);
    }

    close(serv_sock);

    return 0;
}