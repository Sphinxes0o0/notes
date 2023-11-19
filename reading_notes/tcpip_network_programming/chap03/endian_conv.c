#include <netinet/in.h>
#include <stdio.h>
#include <arpa/inet.h>


int main(int argc, char* argv[]) {

    unsigned short host_port = 0x1234;
    unsigned short net_port;
    unsigned long host_addr = 0x12345678;
    unsigned long net_addr;

    net_port = htons(host_port);
    net_addr = htonl(host_addr);

    printf("Host ordered port: %#x \n", host_port);
    printf("Network ordered port: %#x \n", host_port);

    printf("Host ordered addr: %#lx \n", host_addr);
    printf("Network ordered addr: %#lx \n", net_addr);


    return 0;
}