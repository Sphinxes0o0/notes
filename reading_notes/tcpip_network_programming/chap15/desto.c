#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>

int main(void) {

    FILE *fp;
    int fd = open("data.dat", O_WRONLY|O_CREAT|O_TRUNC);
    if (fd == -1) {
        perror("open");
        exit(EXIT_SUCCESS);
    }

    fp = fdopen(fd, "w");
    fputs("Networking C Programming \n", fp);
    fclose(fp);
  
    return 0;
}