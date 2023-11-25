
#include <netinet/in.h>
#include <sys/socket.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
// #include <unistd.h>
// #include <sys/stat.h>
// #include <fcntl.h>



int main(int argc, char *argv[]) {

    int serv_sd, clnt_sd;
    FILE *fp;
    char buf[30];
    int read_cnt;

    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t clnt_addr_sz;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sd = socket(AF_INET, SOCK_STREAM, 0);
    if (serv_sd == -1) {
        perror("socket");
        exit(1);
    }
    fp = fopen("file_server.c", "rb");
    if (fp == NULL) {
        printf("fopen() %d %s", errno, strerror(errno));
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sd, (const struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        printf("bind() %d %s", errno, strerror(errno));
        exit(1);
    }

    listen(serv_sd, 5);

    clnt_addr_sz = sizeof(clnt_addr);
    clnt_sd = accept(serv_sd, (struct sockaddr *)&clnt_addr, &clnt_addr_sz);

    while (1) {
        read_cnt = fread((void*)buf, 1, 30, fp);
        if (read_cnt < 30) {
            write(clnt_sd, buf, read_cnt);
            break;
        }
        write(clnt_sd, buf, 30);
    }

    shutdown(clnt_sd, SHUT_WR);
    read(clnt_sd, buf, 30);
    printf("Message from client: %s \n", buf);

    fclose(fp);
    close(clnt_sd);
    close(serv_sd);

    return 0;
}

