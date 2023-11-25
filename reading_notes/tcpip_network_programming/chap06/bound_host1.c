
#include <netinet/in.h>
#include <sys/socket.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>



#define BUF_SIZE 30

int main(int argc, char *argv[]) {

    int sock;
    char message[BUF_SIZE];
    int str_len;
    struct sockaddr_in my_addr, your_addr;
    socklen_t addr_sz;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) {
        perror("socket()");
        exit(1);
    }

    memset(&my_addr, 0, sizeof(my_addr));
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    my_addr.sin_port = htons(atoi(argv[1]));

    if (bind(sock, (const struct sockaddr *)&my_addr, sizeof(my_addr)) == -1) {
        perror("bind()");
        exit(1);
    }

    printf("bond! \n");

    for (int i = 0; i < 3; i++) {

        printf("sleeping times: %d \n", i+1);

        sleep(5);
        addr_sz = sizeof(your_addr);
        str_len = recvfrom(sock, message, BUF_SIZE, 0, 
                            (struct sockaddr *)&your_addr, 
                            &addr_sz
                        );
        printf("Message %d: %s \n", i+1, message);
    }
    close(sock);

    return 0;
}

