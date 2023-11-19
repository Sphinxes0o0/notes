#include <stdio.h>
#include <arpa/inet.h>

int main() {
    const char *ipAddress = "192.168.0.1";
    struct in_addr binaryIP;
    if (inet_aton(ipAddress, &binaryIP)) {
        printf("Binary IP: %u\n", binaryIP.s_addr);
    } else {
        printf("Invalid IP address\n");
    }

    char *addr = "127.232.124.79";
    struct sockaddr_in addr_in;

    inet_aton(addr, &addr_in.sin_addr);

    printf(
        "Network ordered interger addr: %#x \n",
        addr_in.sin_addr.s_addr
    );


    return 0;
}
