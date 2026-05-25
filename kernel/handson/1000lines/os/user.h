#pragma once
#include "common.h"

__attribute__((noreturn)) void exit(void);

void putchar(char ch);

int getchar(void);

int readfile(const char *filename, char *buf, int len);

int writefile(const char *filename, const char *buf, int len);
