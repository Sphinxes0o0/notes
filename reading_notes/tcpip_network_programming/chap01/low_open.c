/*
https://man7.org/linux/man-pages/man2/open.2.html

#include <fcntl.h>

int open(const char *pathname, int flags);
int open(const char *pathname, int flags, mode_t mode);

int creat(const char *pathname, mode_t mode);


general open flags:
O_CREATE
O_TRUNC
O_RDONLY
O_WRONLY
O_APPEND
O_RDWR

===========================================================================

https://man7.org/linux/man-pages/man2/close.2.html
https://man7.org/linux/man-pages/man2/write.2.html

#include <unistd.h>

int close(int fd);
ssize_t write(int fd, const void buf[.count], size_t count);


https://man7.org/linux/man-pages/man3/exit.3.html

#include <stdlib.h>

[[noreturn]] void exit(int status);


https://man7.org/linux/man-pages/man3/perror.3.html
#include <stdio.h>

void perror(const char *s);

*/

#include <fcntl.h> // open()

#include <stdlib.h> //exit()
#include <stdio.h> // perror()
#include <unistd.h> //  wirte()



int main(int argc, char* argv[]) {
    int fd;
    char buf[] = "let's go!\n";

    fd = open("data.txt", O_CREAT | O_RDWR | O_TRUNC | O_APPEND, S_IRUSR | S_IWUSR);
    if (fd == -1) {
        perror("open() ");
        exit(1);
    }

    printf("file descriptor: %d \n", fd);
    if (write(fd, buf, sizeof(buf)) == -1) {
        perror("write() ");
        exit(1);
    }

    close(fd);

    return 0;
}