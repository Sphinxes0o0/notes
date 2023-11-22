#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>

int calculate(int opnum, int opnds[], char op)
{
	int result=opnds[0], i;
	
	switch(op)
	{
	case '+':
		for(i=1; i<opnum; i++) result+=opnds[i];
		break;
	case '-':
		for(i=1; i<opnum; i++) result-=opnds[i];
		break;
	case '*':
		for(i=1; i<opnum; i++) result*=opnds[i];
		break;
	}
	return result;
}

int main(int argc, char *argv[]) {

    int serv_sock, clnt_sock;
    char opinfo[1024];
    int result, opnd_cnt;
    int recv_cnt, recv_len;
    struct sockaddr_in serv_addr, clnt_addr;
    socklen_t clnt_adr_sz;

    if (argc != 2) {
        printf("Usage: %s <port> \n", argv[0]);
        exit(1);
    }

    serv_sock = socket(PF_INET, SOCK_STREAM, 0);
    if (serv_sock == -1) {
        perror("socket()");
        exit(1);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(atoi(argv[1]));

    if (bind(serv_sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("bind()");
        exit(1);
    }
    printf("binding: \naddr %d \n \nprot %d \n", serv_addr.sin_addr.s_addr, serv_addr.sin_port);


    if (listen(serv_sock, 5) == -1) {
        perror("listen()");
        exit(1);
    }
    printf("listening......");

    clnt_adr_sz = sizeof(clnt_addr);

    for (int i=0; i < 5; i++) {
        opnd_cnt = 0;
        clnt_sock = accept(serv_sock, (struct sockaddr*)&clnt_addr, &clnt_adr_sz);
        if (clnt_sock == -1) {
            printf("accept error time: %d", i);
            perror("accept()");
            break;
        }
        read(clnt_sock, &opnd_cnt, 1);

        recv_len = 0;
        while ((opnd_cnt*4 + 1) > recv_len) {
            recv_cnt = read(clnt_sock, &opinfo[recv_len], 1024 - 1);
            recv_len += recv_cnt;
        }
        printf("calculating ......");

        result = calculate(opnd_cnt, (int*)opinfo, opinfo[recv_len - 1]);
        write(clnt_sock, (char*)&result, sizeof(result));
        close(clnt_sock);
    }

    close(serv_sock);

    return 0;
}