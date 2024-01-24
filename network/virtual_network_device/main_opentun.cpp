#include<unistd.h>

#include <fcntl.h>  /* O_RDWR */
#include <string.h> /* memset(), memcpy() */
#include <stdio.h> /* perror(), printf(), fprintf() */
#include <stdlib.h> /* exit(), malloc(), free() */
#include <sys/ioctl.h> /* ioctl() */

/* includes for struct ifreq, etc */
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/if.h>
#include <linux/if_tun.h>


#include<thread>


int tun_open(char *devname) {
    struct ifreq ifr;
    int fd, err;

    if ( (fd = open("/dev/net/tun", O_RDWR)) == -1 ) {
        perror("open /dev/net/tun");exit(1);
    }
    memset(&ifr, 0, sizeof(ifr));
    ifr.ifr_flags = IFF_TUN;
    strncpy(ifr.ifr_name, devname, IFNAMSIZ); // devname = "tun0" or "tun1", etc 

    /* ioctl will use ifr.if_name as the name of TUN 
    * interface to open: "tun0", etc. */
    if ( (err = ioctl(fd, TUNSETIFF, (void *) &ifr)) == -1 ) {
        perror("ioctl TUNSETIFF");close(fd);exit(1);
    }

    /* After the ioctl call the fd is "connected" to tun device specified
    * by devname ("tun0", "tun1", etc)*/

    return fd;
}


void tun2eth(int tunFD) {
    int nbytes;
    char buf[1600];

    while(1) {
        nbytes = read(tunFD, buf, sizeof(buf));
        printf("Read %d bytes from tun0\n", nbytes);
    }
}


int main(int argc, char *argv[]) {
    int tunFD = tun_open("tun");
    printf("Device tun0 opened\n");

    std::thread t1(tun2eth,tunFD);
    std::thread t2(tun2eth,tunFD);

    t1.join();
    return 0;
}
