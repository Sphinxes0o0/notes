/*
 * TAP Device Test Program
 * 用于验证TAP设备功能的用户空间测试程序
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <getopt.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/if.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <netinet/udp.h>

#define TAP_DEVICE "/dev/tap0"
#define BUFFER_SIZE 2048

// 创建测试以太网帧
int create_test_frame(char *buffer, const char *src_mac, const char *dst_mac, 
                     const char *src_ip, const char *dst_ip, 
                     const char *data, int data_len)
{
    struct ethhdr *eth = (struct ethhdr *)buffer;
    struct iphdr *ip = (struct iphdr *)(buffer + sizeof(struct ethhdr));
    char *payload = buffer + sizeof(struct ethhdr) + sizeof(struct iphdr);
    
    // 解析MAC地址
    sscanf(dst_mac, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
           &eth->h_dest[0], &eth->h_dest[1], &eth->h_dest[2],
           &eth->h_dest[3], &eth->h_dest[4], &eth->h_dest[5]);
    
    sscanf(src_mac, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
           &eth->h_source[0], &eth->h_source[1], &eth->h_source[2],
           &eth->h_source[3], &eth->h_source[4], &eth->h_source[5]);
    
    eth->h_proto = htons(ETH_P_IP);
    
    // 构建IP头
    ip->version = 4;
    ip->ihl = 5;
    ip->tos = 0;
    ip->tot_len = htons(sizeof(struct iphdr) + data_len);
    ip->id = htons(12345);
    ip->frag_off = 0;
    ip->ttl = 64;
    ip->protocol = IPPROTO_UDP;
    ip->check = 0;
    inet_pton(AF_INET, src_ip, &ip->saddr);
    inet_pton(AF_INET, dst_ip, &ip->daddr);
    
    // 复制数据
    memcpy(payload, data, data_len);
    
    return sizeof(struct ethhdr) + sizeof(struct iphdr) + data_len;
}

// 测试基本读写功能
int test_basic_rw(void)
{
    int fd;
    char write_buffer[BUFFER_SIZE];
    char read_buffer[BUFFER_SIZE];
    int frame_len;
    ssize_t bytes_written, bytes_read;
    
    printf("=== 测试基本读写功能 ===\n");
    
    // 打开TAP设备
    fd = open(TAP_DEVICE, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("打开TAP设备失败");
        return -1;
    }
    
    printf("成功打开TAP设备: %s\n", TAP_DEVICE);
    
    // 创建测试数据帧
    const char *test_data = "Hello TAP Device!";
    frame_len = create_test_frame(write_buffer,
                                 "aa:bb:cc:dd:ee:ff",  // 源MAC
                                 "11:22:33:44:55:66",  // 目标MAC
                                 "192.168.1.1",        // 源IP
                                 "192.168.1.2",        // 目标IP
                                 test_data, strlen(test_data));
    
    // 写入测试数据
    bytes_written = write(fd, write_buffer, frame_len);
    if (bytes_written < 0) {
        perror("写入TAP设备失败");
        close(fd);
        return -1;
    }
    
    printf("成功写入 %zd 字节数据到TAP设备\n", bytes_written);
    
    // 尝试读取数据 (可能没有数据返回)
    bytes_read = read(fd, read_buffer, sizeof(read_buffer));
    if (bytes_read < 0) {
        if (errno == EAGAIN) {
            printf("没有数据可读 (正常现象)\n");
        } else {
            perror("读取TAP设备失败");
        }
    } else {
        printf("从TAP设备读取到 %zd 字节数据\n", bytes_read);
    }
    
    close(fd);
    printf("基本读写测试完成\n\n");
    return 0;
}

// 测试网络接口状态
int test_network_interface(void)
{
    int sock;
    struct ifreq ifr;
    
    printf("=== 测试网络接口状态 ===\n");
    
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("创建socket失败");
        return -1;
    }
    
    strcpy(ifr.ifr_name, "tap0");
    
    // 获取接口标志
    if (ioctl(sock, SIOCGIFFLAGS, &ifr) < 0) {
        perror("获取接口标志失败");
        close(sock);
        return -1;
    }
    
    printf("接口 tap0 状态:\n");
    printf("  UP: %s\n", (ifr.ifr_flags & IFF_UP) ? "是" : "否");
    printf("  RUNNING: %s\n", (ifr.ifr_flags & IFF_RUNNING) ? "是" : "否");
    printf("  BROADCAST: %s\n", (ifr.ifr_flags & IFF_BROADCAST) ? "是" : "否");
    printf("  MULTICAST: %s\n", (ifr.ifr_flags & IFF_MULTICAST) ? "是" : "否");
    
    // 获取MAC地址
    if (ioctl(sock, SIOCGIFHWADDR, &ifr) >= 0) {
        unsigned char *mac = (unsigned char*)ifr.ifr_hwaddr.sa_data;
        printf("  MAC地址: %02x:%02x:%02x:%02x:%02x:%02x\n",
               mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    }
    
    // 获取MTU
    if (ioctl(sock, SIOCGIFMTU, &ifr) >= 0) {
        printf("  MTU: %d\n", ifr.ifr_mtu);
    }
    
    close(sock);
    printf("网络接口测试完成\n\n");
    return 0;
}

// 持续数据包测试
int test_continuous_packets(int count)
{
    int fd;
    char buffer[BUFFER_SIZE];
    int frame_len;
    ssize_t bytes_written;
    int i;
    
    printf("=== 持续数据包测试 (发送 %d 个包) ===\n", count);
    
    fd = open(TAP_DEVICE, O_RDWR);
    if (fd < 0) {
        perror("打开TAP设备失败");
        return -1;
    }
    
    for (i = 0; i < count; i++) {
        char test_data[64];
        snprintf(test_data, sizeof(test_data), "Test packet #%d", i + 1);
        
        frame_len = create_test_frame(buffer,
                                     "aa:bb:cc:dd:ee:ff",
                                     "11:22:33:44:55:66",
                                     "192.168.1.1",
                                     "192.168.1.2",
                                     test_data, strlen(test_data));
        
        bytes_written = write(fd, buffer, frame_len);
        if (bytes_written < 0) {
            perror("写入失败");
            break;
        }
        
        if ((i + 1) % 10 == 0) {
            printf("已发送 %d 个数据包\n", i + 1);
        }
        
        usleep(1000); // 1ms延迟
    }
    
    close(fd);
    printf("持续数据包测试完成\n\n");
    return 0;
}

// 性能测试
int test_performance(void)
{
    int fd;
    char buffer[BUFFER_SIZE];
    int frame_len;
    ssize_t bytes_written;
    int packets = 1000;
    int i;
    struct timeval start, end;
    double elapsed;
    
    printf("=== 性能测试 (发送 %d 个包) ===\n", packets);
    
    fd = open(TAP_DEVICE, O_RDWR);
    if (fd < 0) {
        perror("打开TAP设备失败");
        return -1;
    }
    
    // 准备测试数据
    const char *test_data = "Performance test data for TAP device";
    frame_len = create_test_frame(buffer,
                                 "aa:bb:cc:dd:ee:ff",
                                 "11:22:33:44:55:66",
                                 "192.168.1.1",
                                 "192.168.1.2",
                                 test_data, strlen(test_data));
    
    // 开始计时
    gettimeofday(&start, NULL);
    
    for (i = 0; i < packets; i++) {
        bytes_written = write(fd, buffer, frame_len);
        if (bytes_written < 0) {
            perror("写入失败");
            break;
        }
    }
    
    // 结束计时
    gettimeofday(&end, NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
    
    printf("发送 %d 个数据包用时: %.3f 秒\n", packets, elapsed);
    printf("平均速率: %.0f 包/秒\n", packets / elapsed);
    printf("吞吐量: %.2f KB/s\n", (packets * frame_len) / (elapsed * 1024));
    
    close(fd);
    printf("性能测试完成\n\n");
    return 0;
}

void print_usage(const char *prog_name)
{
    printf("用法: %s [选项]\n", prog_name);
    printf("选项:\n");
    printf("  -b         基本读写测试\n");
    printf("  -i         网络接口测试\n");
    printf("  -c <count> 持续数据包测试 (指定包数量)\n");
    printf("  -p         性能测试\n");
    printf("  -a         运行所有测试\n");
    printf("  -h         显示帮助信息\n");
}

int main(int argc, char *argv[])
{
    int opt;
    int run_all = 0;
    int packet_count = 100;
    
    printf("TAP设备测试程序\n");
    printf("================\n\n");
    
    if (argc == 1) {
        print_usage(argv[0]);
        return 1;
    }
    
    while ((opt = getopt(argc, argv, "bic:pah")) != -1) {
        switch (opt) {
            case 'b':
                test_basic_rw();
                break;
            case 'i':
                test_network_interface();
                break;
            case 'c':
                packet_count = atoi(optarg);
                test_continuous_packets(packet_count);
                break;
            case 'p':
                test_performance();
                break;
            case 'a':
                run_all = 1;
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    if (run_all) {
        test_basic_rw();
        test_network_interface();
        test_continuous_packets(50);
        test_performance();
    }
    
    printf("所有测试完成！\n");
    return 0;
} 