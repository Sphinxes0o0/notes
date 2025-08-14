CC      = cc
CFLAGS  = -Wall -std=c99
LDFLAGS = -lpthread

all: shm_write_once shm_reader

shm_write_once: shm_write_once.c shm_common.h
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

shm_reader: shm_reader.c shm_common.h
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f shm_write_once shm_reader