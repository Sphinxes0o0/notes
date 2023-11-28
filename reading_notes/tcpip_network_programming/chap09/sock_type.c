#include <asm-generic/socket.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char* argv[]) {
    int tcp_sock, udp_sock, sock_type;
    socklen_t optlen;

    int state;

    tcp_sock = socket(AF_INET, SOCK_STREAM, 0);
    printf("tcp socket: %d  <-- SOCK_STREAM %d \n", tcp_sock, SOCK_STREAM);
    udp_sock = socket(AF_INET, SOCK_DGRAM, 0);
    printf("udp socket: %d  <-- SOCK_STREAM %d \n", tcp_sock, SOCK_DGRAM);

    optlen =sizeof(sock_type);

    state = getsockopt(tcp_sock, SOL_SOCKET, SO_TYPE, (void *)&sock_type,
     &optlen);
    printf("Socket type one : %d \n", sock_type);

    state = getsockopt(udp_sock, SOL_SOCKET, SO_TYPE, (void *)&sock_type,
     &optlen);
    printf("Socket type one : %d \n", sock_type);

    return 0;
}