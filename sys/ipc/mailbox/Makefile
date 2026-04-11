CC = gcc
CFLAGS = -Wall -Wextra -pthread -O2 -g

# 源文件
SRCS = dummy_mbox.c test.c
OBJS = $(SRCS:.c=.o)

# 目标文件
TARGET = test_dummy_mbox

# 默认目标
all: $(TARGET)

# 链接目标文件
$(TARGET): dummy_mbox.o test.o
	$(CC) $(CFLAGS) -o $@ $^ -lpthread

# 编译源文件
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# 清理生成的文件
clean:
	rm -f $(OBJS) $(TARGET)

# 伪目标
.PHONY: all clean