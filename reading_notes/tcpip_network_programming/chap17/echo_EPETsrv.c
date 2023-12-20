#include <asm-generic/errno-base.h>
#include <fcntl.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <unistd.h>

#define BUF_SIZE 4
#define EPOLL_SIZE 50


int main(int argc, char *argv[]) {

    int serv_sock, clnt_sock;
    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t addr_size;
    int str_len, i;
    char buf[BUF_SIZE];

    struct epoll_event *epoll_events;
    struct epoll_event epoll_ev;
    int epfd, event_count;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(PF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (const struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind() ");
        exit(EXIT_FAILURE);
    }



    if (listen(serv_sock, 5) == -1) {
        perror("listen() ");
        exit(EXIT_FAILURE);
    }

    epfd = epoll_create(EPOLL_SIZE);
    epoll_events = malloc(sizeof(struct epoll_event) * EPOLL_SIZE);

    int flag = fcntl(serv_sock, F_GETFL, 0);
    fcntl(serv_sock, F_SETFL, flag | O_NONBLOCK);
    epoll_ev.events = EPOLLIN;
    epoll_ev.data.fd = serv_sock;
    epoll_ctl(epfd, EPOLL_CTL_ADD, serv_sock, &epoll_ev);


    while (1) {
        event_count = epoll_wait(epfd, epoll_events, EPOLL_SIZE, -1);
        if (event_count == -1) {
            perror("epoll_wait() ");
            break;
        }

        puts("return epoll_wait");
        for (i=0; i < event_count; i++) {
            if (epoll_events[i].data.fd == serv_sock) {
                addr_size = sizeof(clnt_addr);
                clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &addr_size);
                if (clnt_sock == -1) {
                    perror("accept() ");
                    break;
                }

                int flag = fcntl(clnt_sock, F_GETFL, 0);
                fcntl(clnt_sock, F_SETFL, flag | O_NONBLOCK);

                epoll_ev.events = EPOLLIN | EPOLLET;
                epoll_ev.data.fd = clnt_sock;
                epoll_ctl(epfd, EPOLL_CTL_ADD, clnt_sock, &epoll_ev);
                printf("connected client: %d \n", clnt_sock);
            } else {
                while(1) {
                    str_len = read(epoll_events[i].data.fd, buf, BUF_SIZE);
                    if (str_len < 0) {
                        if (errno == EAGAIN) 
                            break;
                        else
                            printf("errno %d: %s", errno, strerror(errno));
                    } else if (str_len == 0) {
                        epoll_ctl(epfd, EPOLL_CTL_DEL, epoll_events[i].data.fd, NULL);
                        close(epoll_events[i].data.fd);

                        printf("closed client:%d \n", epoll_events[i].data.fd);
                        break;
                    } else {
                        write(epoll_events[i].data.fd, buf, str_len);
                    }
                }
            }
        }
    }
    close(serv_sock);
    close(epfd);

    return 0;
}

