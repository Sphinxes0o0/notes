#include <stdio.h>
#include <arpa/inet.h>

int main() {
    struct in_addr binaryIP;
    binaryIP.s_addr = inet_addr("192.168.0.1");
    printf("binary ip:  %#x \n", binaryIP.s_addr);
    char *ipAddress = inet_ntoa(binaryIP);
    if (ipAddress != NULL) {
        printf("IP Address: %s\n", ipAddress);
    } else {
        printf("Invalid IP address\n");
    }
    return 0;
}