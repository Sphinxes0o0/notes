#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdbool.h>

#define BUF_SIZE 30

void read_childproc(int sig) {
    pid_t pid;
    int status;
    pid = waitpid(-1, &status, WNOHANG);
    printf("removed proc id: %d \n", pid);
}

int main(int argc, char *argv[]) {

    int serv_sock, clnt_sock;
    struct sockaddr_in serv_addr, clnt_addr;
    pid_t pid;
    socklen_t adr_sz;
    int str_len, state;
    char buf[BUF_SIZE];
    struct sigaction act;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    act.sa_handler = read_childproc;
    act.sa_flags = 0;
    sigemptyset(&act.sa_mask);

    state = sigaction(SIGCHLD, &act, 0);
    serv_sock = socket(AF_INET, SOCK_STREAM, 0);

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (const struct sockaddr *)&serv_addr, 
        sizeof(serv_addr)) == -1) {
        perror("bind()");
        exit(1);
    }

    if (listen(serv_sock, 5) == -1) {
        perror("listen");
        exit(1);
    }

    while (true) {
        adr_sz = sizeof(clnt_addr);
        clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &adr_sz);
        if (clnt_sock == -1)
            continue;
        else
            puts("new client connected ...");
        
        pid = fork();
        if (pid == -1) {
            close(clnt_sock);
            continue;
        }

        if (pid == 0) {
            close(serv_sock);
            while ((str_len = read(clnt_sock, buf, BUF_SIZE)) != 0) {
                write(clnt_sock, buf, str_len);
            }

            close(clnt_sock);
            puts("client disconnected ...\n");
        } else {
            close(clnt_sock);
        }

    }
    close(serv_sock);
    return 0;
}