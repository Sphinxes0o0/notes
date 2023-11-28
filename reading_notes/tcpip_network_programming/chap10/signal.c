#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

void timeout(int sig) {
    if (sig == SIGALRM)
        puts("Time out");
    alarm(2);
}

void keycontrol(int sig) {
    if (sig == SIGINT)
        puts("CTRL+C pressed");
}

int main(int argc, char *argv[]) {

    int i;
    signal(SIGALRM, timeout);
    signal(SIGINT, keycontrol);

    for (i = 0; i < 3; i++) {
        puts("wait ...");
        sleep(100);
    }

    return 0;
}