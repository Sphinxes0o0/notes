#include <stdio.h>
#include <sys/time.h>

#define BUF_SIZE 3


int main(int argc, char* argv[]) {

    FILE * fp1;
    FILE * fp2;
    char buf[BUF_SIZE];
    struct timeval start, end;

    gettimeofday(&start, NULL);

    fp1 = fopen("../TCPIP_Src.zip", "r");
    fp2 = fopen("cpy.zip", "w");

    while (fgets(buf, BUF_SIZE, fp1) != NULL) 
        fputs(buf, fp2);
    
    gettimeofday(&end, NULL);
    double elapsed = end.tv_sec - start.tv_sec + 
        (end.tv_usec - start.tv_usec) / 1e6;
    printf("run time: %.6f s \n", elapsed);

    fclose(fp1);
    fclose(fp2);

    return 0;
}