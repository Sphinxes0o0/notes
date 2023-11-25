
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>


int main(int argc, char* argv[]) {

    struct hostent *host;
    struct sockaddr_in addr;

    if (argc != 2) {
        printf("Usage: %s <ip addr> \n", argv[0]);
        exit(1);
    }

    if (!host) {
        perror("gethostbyname()");
        exit(1);
    }

    memset(&addr, 0, sizeof(addr));
    addr.sin_addr.s_addr = inet_addr(argv[1]);

    printf("gethostbyaddr \n");

    host = gethostbyaddr((char *)&addr.sin_addr, 4, AF_INET);
    if (!host) {
        printf("host empty!");
        exit(1);
    }

    printf("Offcial Name: %s \n", host->h_name);

    for (int i=0; host->h_aliases[i]; i++) 
        printf("aliases %d : %s \n", i+1, host->h_aliases[i]);

    printf("Address type: %s \n", (host->h_addrtype == AF_INET) ? "AF_INET" : "AF_INET6");

    for (int i=0; host->h_addr_list[i]; i++) 
        printf("IP addr %d:%s \n", i+1, inet_ntoa(*(struct in_addr*)host->h_addr_list[i]));
    
    return 0;
}
