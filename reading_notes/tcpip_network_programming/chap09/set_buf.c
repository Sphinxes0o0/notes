#include <asm-generic/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>

int main(int argc, char* argv[]) {

    int sock;
    int snd_buf = 1024 * 10 , recv_buf = 1024 * 10, state;
    socklen_t len;

    sock = socket(AF_INET, SOCK_STREAM, 0);
    len =sizeof(snd_buf);

    state = getsockopt(sock, SOL_SOCKET, SO_SNDBUF, (void *)&snd_buf, &len);
    len = sizeof(recv_buf);

    state = getsockopt(sock, SOL_SOCKET, SO_SNDBUF, (void *)&recv_buf, &len);
    
    printf("input buffer size :%d \n", recv_buf);
    printf("output buf size: %d \n", snd_buf);

    state =setsockopt(sock, SOL_SOCKET, SO_SNDBUF,
         (void *)&snd_buf, sizeof(snd_buf));
    state =setsockopt(sock, SOL_SOCKET, SO_RCVBUF,
         (void *)&recv_buf, sizeof(recv_buf));

    len =sizeof(snd_buf);

    state = getsockopt(sock, SOL_SOCKET, SO_SNDBUF, (void *)&snd_buf, &len);
    len = sizeof(recv_buf);

    state = getsockopt(sock, SOL_SOCKET, SO_SNDBUF, (void *)&recv_buf, &len);
    
    printf("input buffer size :%d \n", recv_buf);
    printf("output buf size: %d \n", snd_buf);

    
    return 0;
}