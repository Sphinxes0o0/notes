#include <stdio.h>
#include <arpa/inet.h>

int main() {
    const char *ipAddress = "192.168.0.1";
    printf("IP String: %s \n", ipAddress);

    in_addr_t binaryIP = inet_addr(ipAddress);

    if (binaryIP != INADDR_NONE) {
        printf("Binary IP: %u\n", binaryIP);
    } else {
        printf("Invalid IP address\n");
    }
    
    return 0;
}