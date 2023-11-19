 #include <sys/socket.h>

 #include <netinet/in.h>

 #include <stdlib.h>
 #include <stdio.h>
 #include <string.h>
 #include <unistd.h>
 #include <stdbool.h>

void error_handling(char *msg) {
    fputs(msg, stderr);
    fputc('\n', stderr);
    exit(1);
}


int main (int argc, char *argv[]) {

    int serv_sock, clnt_sock;
    
    struct sockaddr_in serv_addr;
    struct sockaddr_in clnt_addr;
    socklen_t clnt_addr_size;

    char message[] = "Hello World!";
    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(AF_INET, SOCK_STREAM, 0);
    //TODO: 确认下 protocol 参数的含义
    // 大部分情况下， 前两个参数就可以确定协议簇， 数据传输方式 ==> 最终的协议(如AF_INET+ SOCK_STREAM => TCP)
    // 但是，考虑到同一个协议中可能存在多个不同的传输方式所以设置第三个参数来具体指定协议信息
    if (serv_sock == -1) 
        error_handling("socket() error");
    
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1 )
        error_handling("bind() error");

    if (listen(serv_sock, 10) == -1)
        error_handling("listen() error");

    clnt_addr_size = sizeof(clnt_addr);
    clnt_sock = accept(serv_sock, (struct sockaddr *)&clnt_addr, &clnt_addr_size);
    if (clnt_sock== -1)
        error_handling("accept() error");

    write(clnt_sock, message, sizeof(message));

    close(serv_sock);
    close(clnt_sock);
    
    return 0;
}
