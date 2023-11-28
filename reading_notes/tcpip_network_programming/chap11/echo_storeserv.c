
#include <signal.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

#include <sys/wait.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>

#define BUF_SIZE 100

void read_childproc(int sig) {
    pid_t pid;
    int status;
    pid = waitpid(-1, &status, WNOHANG);
    printf("removed proc id: %d \n", pid);
}

int main(int argc, char *argv[]) {

    int serv_sock, clnt_sock;
    struct sockaddr_in serv_addr, clnt_addr;
    int fds[2];
    pid_t pid;

    struct sigaction act;
    socklen_t adr_sz;
    int str_len, state;
    char buf[BUF_SIZE];

    if (argc != 2) {
        fprintf(stderr, "usage: %s <port>\n", argv[0]);
        exit(1);
    }

    if (pipe(fds) == -1) {
        perror("pipe");
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (serv_sock == -1) {
        perror("socket");
        exit(1);
    }

    act.sa_handler = read_childproc;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;
    state = sigaction(SIGCHLD, &act, 0);

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (const struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind()");
        exit(1);
    }

    if (listen(serv_sock, 5) == -1) {
        perror("listen");
    }

    pipe(fds);
    pid = fork();

    if (pid == 0) {
        FILE *fp = fopen("echomsg.txt", "wt");
        char msgbuf[BUF_SIZE];
        int len;

        for (int i = 0; i < 10; i++) {
            len = read(fds[0], msgbuf, sizeof(msgbuf));
            fwrite((void *)msgbuf, 1, len, fp);
        }
        fclose(fp);
        return 0;
    } 

    while (true) {
        adr_sz = sizeof(clnt_addr);
        clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &adr_sz);
        if (clnt_sock == -1)
            continue;
        else
            puts("new clinet connected ..");


        pid = fork();

        if (pid == 0) {

            close(serv_sock);
            while ((str_len = read(clnt_sock, buf, BUF_SIZE)) != 0) {
                write(clnt_sock, buf, str_len);
                write(fds[1], buf, str_len);
            }
            close(clnt_sock);
            puts("client disconnected ...");

            return 0;
        } 
        else
            close(clnt_sock);
    }
    close(serv_sock);

    return 0;
}
