#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>


int main(int argc, char *argv[]) {

    int sock;
    char buf[1024];
    struct sockaddr_in serv_addr;

    FILE *readfp;
    FILE *writefp;

    sock = socket(AF_INET, SOCK_STREAM, 0);
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[2]));
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);

    if (connect(sock, (const struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("connect ");
        exit(1);
    }

    readfp = fdopen(sock, "r");
    writefp = fdopen(sock, "w");

    while (1) {
        if (fgets(buf, sizeof(buf), readfp) == NULL)
            break;
        fputs(buf, stdout);
        fflush(stdout);
    }

    fputs("FROM Client: thanks !", writefp);
    fflush(writefp);
    fclose(writefp);
    fclose(readfp);


    return 0;
}
