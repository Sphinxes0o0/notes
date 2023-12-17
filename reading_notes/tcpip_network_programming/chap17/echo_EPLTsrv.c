
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include <sys/epoll.h>

#define BUF_SIZE 30
#define EPOLL_SIZE 50

int main(int argc, char* argv[]) {

    int serv_sock, clnt_sock;
    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t adr_sz;
    int str_len, i;
    char  buf[BUF_SIZE];

    struct epoll_event event;
    struct epoll_event *ep_event;
    int epfd, event_cnt;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (struct sockaddr*) &serv_addr, sizeof(serv_addr)) == -1){
        perror("bind failed");
        exit(1);
    }

    if (listen(serv_sock, 10) == -1) {
        perror("listen failed");
        exit(1);
    }

    epfd = epoll_create(EPOLL_SIZE);
    ep_event = malloc(sizeof(struct epoll_event) * EPOLL_SIZE);

    event.events = EPOLLIN;
    event.data.fd = serv_sock;
    epoll_ctl(epfd, EPOLL_CTL_ADD, serv_sock, &event);

    while (true) {
        event_cnt = epoll_wait(epfd, ep_event, EPOLL_SIZE, -1);
        if (event_cnt == -1) {
            perror("epoll_wait");
            exit(1);
        }
        puts("return epoll_wait");
        for ( i = 0; i < event_cnt; i++) {
            if (ep_event[i].data.fd == serv_sock) {
                adr_sz = sizeof(clnt_addr);
                clnt_sock = accept(serv_sock, (struct sockaddr*) &clnt_addr, &adr_sz);
                event.events = EPOLLIN;
                event.data.fd = clnt_sock;
                epoll_ctl(epfd, EPOLL_CTL_ADD, clnt_sock, &event);
                printf("connect client: %d", clnt_sock);
            } else {
                str_len = read(ep_event[i].data.fd, buf, 4);
                if (str_len == 0) { // close request
                    epoll_ctl(epfd, EPOLL_CTL_DEL, ep_event[i].data.fd, NULL);
                    close(ep_event[i].data.fd);
                    printf("client: %d closed \n", ep_event[i].data.fd);
                } else {
                    write(ep_event[i].data.fd, buf, str_len); // ehco !
                }
            }
        }
        
    }

    
    close(serv_sock);
    close(epfd);
    
    return 0;
}

