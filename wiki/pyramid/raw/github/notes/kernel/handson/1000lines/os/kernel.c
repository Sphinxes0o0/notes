#include "kernel.h"
#include "common.h"

#define PROCS_MAX       8 // 最大进程数量
#define PROC_UNUSED     0 // 未使用的进程控制结构
#define PROC_RUNNABLE   1 // 可运行的进程
#define SSTATUS_SPIE    (1 << 5)
#define SCAUSE_ECALL    8

// 应用程序镜像的基础虚拟地址。这需要与 `user.ld` 中定义的起始地址匹配。
#define USER_BASE 0x1000000

extern char __bss[], __bss_end[], __stack_top[];
extern char __free_ram[], __free_ram_end[];
extern char __kernel_base[];
extern char _binary_shell_bin_start[], _binary_shell_bin_size[];

struct process {
  int pid;    // 进程 ID
  int state;  // 进程状态: PROC_UNUSED 或 PROC_RUNNABLE
  vaddr_t sp; // 栈指针
  uint32_t *page_table;
  uint8_t stack[8192]; // 内核栈
};

struct process procs[PROCS_MAX];
struct process *current_proc;
struct process *idle_proc;

struct virtio_virtq *blk_request_vq;
struct virtio_blk_req *blk_req;
paddr_t blk_req_paddr;
uint64_t blk_capacity;

struct file files[FILES_MAX];
uint8_t disk[DISK_MAX_SIZE];

void fs_flush(void);

__attribute__((naked)) void user_entry(void) {
  __asm__ __volatile__(
      "csrw sepc, %[sepc]        \n"
      "csrw sstatus, %[sstatus]  \n"
      "sret                      \n"
      :
      : [sepc] "r"(USER_BASE), 
        [sstatus] "r"(SSTATUS_SPIE | SSTATUS_SUM));
}

int oct2int(char *oct, int len) {
    int dec = 0;
    for (int i = 0; i < len; i++) {
        if (oct[i] < '0' || oct[i] > '7')
        break;

        dec = dec * 8 + (oct[i] - '0');
    }
    return dec;
}

struct file *fs_lookup(const char *filename) {
    for (int i = 0; i < FILES_MAX; i++) {
        struct file *file = &files[i];
        if (!strcmp(file->name, filename)) return file;
    }

    return NULL;
}

paddr_t alloc_pages(uint32_t size) {
    static paddr_t next_paddr = (paddr_t)__free_ram;
    paddr_t paddr = next_paddr;
    next_paddr += size * PAGE_SIZE;

    if (next_paddr > (paddr_t)__free_ram_end) PANIC("out of memory\n");

    memset((void *)paddr, 0, size * PAGE_SIZE);
    return paddr;
}

void map_page(uint32_t *table1, uint32_t vaddr, paddr_t paddr, uint32_t flags) {
    if (!is_aligned(vaddr, PAGE_SIZE)) PANIC("vaddr not aligned %x", vaddr);
    if (!is_aligned(paddr, PAGE_SIZE)) PANIC("paddr not aligned %x", paddr);

    uint32_t vpn1 = (vaddr >> 22) & 0x3ff;
    if ((table1[vpn1] & PAGE_V) == 0) {
        uint32_t pt_paddr = alloc_pages(1);
        table1[vpn1] = ((pt_paddr / PAGE_SIZE) << 10) | PAGE_V;
    }

    // 设置二级页表项以映射物理页面
    uint32_t vpn0 = (vaddr >> 12) & 0x3ff;
    uint32_t *table0 = (uint32_t *)((table1[vpn1] >> 10) * PAGE_SIZE);
    table0[vpn0] = ((paddr / PAGE_SIZE) << 10) | flags | PAGE_V;
}

struct sbiret sbi_call(long arg0, long arg1, long arg2, long arg3, long arg4,
                       long arg5, long fid, long eid) {
    register long a0 __asm__("a0") = arg0;
    register long a1 __asm__("a1") = arg1;
    register long a2 __asm__("a2") = arg2;
    register long a3 __asm__("a3") = arg3;
    register long a4 __asm__("a4") = arg4;
    register long a5 __asm__("a5") = arg5;
    register long a6 __asm__("a6") = fid;
    register long a7 __asm__("a7") = eid;

    __asm__ __volatile__(
        "ecall"
        : "+r"(a0), "+r"(a1)
        : "r"(a0), "r"(a1), "r"(a2), "r"(a3),
          "r"(a4), "r"(a5), "r"(a6), "r"(a7)
        : "memory"
    );

    return (struct sbiret){.error = a0, .value = a1};
}

void putchar(char ch) {
    sbi_call(ch, 0, 0, 0, 0, 0, 0, 1 /* Console Putchar */);
}

__attribute__((naked))
__attribute__((aligned(4)))
void kernel_entry(void) {
  __asm__ __volatile__(
        // 从sscratch中获取运行进程的内核栈
        "csrrw sp, sscratch, sp\n"

        "addi sp, sp, -4 * 31\n"
        "sw ra,  4 * 0(sp)\n"
        "sw gp,  4 * 1(sp)\n"
        "sw tp,  4 * 2(sp)\n"
        "sw t0,  4 * 3(sp)\n"
        "sw t1,  4 * 4(sp)\n"
        "sw t2,  4 * 5(sp)\n"
        "sw t3,  4 * 6(sp)\n"
        "sw t4,  4 * 7(sp)\n"
        "sw t5,  4 * 8(sp)\n"
        "sw t6,  4 * 9(sp)\n"
        "sw a0,  4 * 10(sp)\n"
        "sw a1,  4 * 11(sp)\n"
        "sw a2,  4 * 12(sp)\n"
        "sw a3,  4 * 13(sp)\n"
        "sw a4,  4 * 14(sp)\n"
        "sw a5,  4 * 15(sp)\n"
        "sw a6,  4 * 16(sp)\n"
        "sw a7,  4 * 17(sp)\n"
        "sw s0,  4 * 18(sp)\n"
        "sw s1,  4 * 19(sp)\n"
        "sw s2,  4 * 20(sp)\n"
        "sw s3,  4 * 21(sp)\n"
        "sw s4,  4 * 22(sp)\n"
        "sw s5,  4 * 23(sp)\n"
        "sw s6,  4 * 24(sp)\n"
        "sw s7,  4 * 25(sp)\n"
        "sw s8,  4 * 26(sp)\n"
        "sw s9,  4 * 27(sp)\n"
        "sw s10, 4 * 28(sp)\n"
        "sw s11, 4 * 29(sp)\n"

        // 获取并保存异常发生时的sp
        "csrr a0, sscratch\n"
        "sw a0, 4 * 30(sp)\n"

        // 重置内核栈
        "addi a0, sp, 4 * 31\n"
        "csrw sscratch, a0\n"

        "mv a0, sp\n"
        "call handle_trap\n"

        "lw ra,  4 * 0(sp)\n"
        "lw gp,  4 * 1(sp)\n"
        "lw tp,  4 * 2(sp)\n"
        "lw t0,  4 * 3(sp)\n"
        "lw t1,  4 * 4(sp)\n"
        "lw t2,  4 * 5(sp)\n"
        "lw t3,  4 * 6(sp)\n"
        "lw t4,  4 * 7(sp)\n"
        "lw t5,  4 * 8(sp)\n"
        "lw t6,  4 * 9(sp)\n"
        "lw a0,  4 * 10(sp)\n"
        "lw a1,  4 * 11(sp)\n"
        "lw a2,  4 * 12(sp)\n"
        "lw a3,  4 * 13(sp)\n"
        "lw a4,  4 * 14(sp)\n"
        "lw a5,  4 * 15(sp)\n"
        "lw a6,  4 * 16(sp)\n"
        "lw a7,  4 * 17(sp)\n"
        "lw s0,  4 * 18(sp)\n"
        "lw s1,  4 * 19(sp)\n"
        "lw s2,  4 * 20(sp)\n"
        "lw s3,  4 * 21(sp)\n"
        "lw s4,  4 * 22(sp)\n"
        "lw s5,  4 * 23(sp)\n"
        "lw s6,  4 * 24(sp)\n"
        "lw s7,  4 * 25(sp)\n"
        "lw s8,  4 * 26(sp)\n"
        "lw s9,  4 * 27(sp)\n"
        "lw s10, 4 * 28(sp)\n"
        "lw s11, 4 * 29(sp)\n"
        "lw sp,  4 * 30(sp)\n"
        "sret\n"
    );
}

__attribute__((section(".text.boot"))) 
__attribute__((naked)) 
void boot(void) {
    __asm__ __volatile__(
        "mv sp, %[stack_top]\n" // 设置栈指针
        "j kernel_main\n"       // 跳转到内核主函数
        :
        : [stack_top] "r"(__stack_top) // 将栈顶地址作为 %[stack_top] 传递
    );
}

__attribute__((naked))
void switch_context(uint32_t *prev_sp, uint32_t *next_sp) {
  /*
  switch_context将被调用者保存的寄存器保存到栈上，切换栈指针，然后从栈中恢复被调用者保存的寄存器。
  换句话说，执行上下文作为临时局部变量存储在栈上。
    或者，也可以将上下文保存在`struct process`中.

  被调用者保存的寄存器是被调用函数在返回前必须恢复的寄存器。
  在 RISC-V中，s0到s11是被调用者保存的寄存器。
    其他像a0这样的寄存器是调用者保存的寄存器，已经由调用者保存在栈上。
        这就是为什么switch_context只处理部分寄存器。

  naked属性告诉编译器不要生成除内联汇编以外的任何代码。
  没有这个属性也应该能工作，但手动修改栈指针时使用它是个好习惯，可以避免意外行为。
  */
  __asm__ __volatile__(
        // 将被调用者保存寄存器保存到当前进程的栈上
        "addi sp, sp, -13 * 4\n" // 为13个4字节寄存器分配栈空间
        "sw ra,  0  * 4(sp)\n"   // 仅保存被调用者保存的寄存器
        "sw s0,  1  * 4(sp)\n"
        "sw s1,  2  * 4(sp)\n"
        "sw s2,  3  * 4(sp)\n"
        "sw s3,  4  * 4(sp)\n"
        "sw s4,  5  * 4(sp)\n"
        "sw s5,  6  * 4(sp)\n"
        "sw s6,  7  * 4(sp)\n"
        "sw s7,  8  * 4(sp)\n"
        "sw s8,  9  * 4(sp)\n"
        "sw s9,  10 * 4(sp)\n"
        "sw s10, 11 * 4(sp)\n"
        "sw s11, 12 * 4(sp)\n"

        // 切换栈指针
        "sw sp, (a0)\n" // *prev_sp = sp;
        "lw sp, (a1)\n" // 在这里切换栈指针(sp)

        // 从下一个进程的栈中恢复被调用者保存的寄存器
        "lw ra,  0  * 4(sp)\n" // 仅恢复被调用者保存的寄存器
        "lw s0,  1  * 4(sp)\n"
        "lw s1,  2  * 4(sp)\n"
        "lw s2,  3  * 4(sp)\n"
        "lw s3,  4  * 4(sp)\n"
        "lw s4,  5  * 4(sp)\n"
        "lw s5,  6  * 4(sp)\n"
        "lw s6,  7  * 4(sp)\n"
        "lw s7,  8  * 4(sp)\n"
        "lw s8,  9  * 4(sp)\n"
        "lw s9,  10 * 4(sp)\n"
        "lw s10, 11 * 4(sp)\n"
        "lw s11, 12 * 4(sp)\n"
        "addi sp, sp, 13 * 4\n" // 我们已从栈中弹出13个4字节寄存器
        "ret\n"
    );
}

struct process *create_process(const void *image, size_t image_size) {
    struct process *proc = NULL;
    int i;

    for (i = 0; i < PROCS_MAX; i++) {
        if (procs[i].state == PROC_UNUSED) {
        proc = &procs[i];
        break;
        }
    }

    if (!proc)
        PANIC("No more process slot");

    // 设置被调用者保存的寄存器。
    // 这些寄存器值将在 `switch_context` 中的第一次上下文切换时被恢复。
    uint32_t *sp = (uint32_t *)&proc->stack[sizeof(proc->stack)];
    *--sp = 0;                    // s11
    *--sp = 0;                    // s10
    *--sp = 0;                    // s9
    *--sp = 0;                    // s8
    *--sp = 0;                    // s7
    *--sp = 0;                    // s6
    *--sp = 0;                    // s5
    *--sp = 0;                    // s4
    *--sp = 0;                    // s3
    *--sp = 0;                    // s2
    *--sp = 0;                    // s1
    *--sp = 0;                    // s0
    *--sp = (uint32_t)user_entry; // ra

    // 映射内核页面。
    uint32_t *page_table = (uint32_t *)alloc_pages(1);
    for (paddr_t paddr = (paddr_t)__kernel_base; paddr < (paddr_t)__free_ram_end; paddr += PAGE_SIZE)
        map_page(page_table, paddr, paddr, PAGE_R | PAGE_W | PAGE_X);

    // virtio_blk mmio区域映射
    map_page(page_table, VIRTIO_BLK_PADDR, VIRTIO_BLK_PADDR, PAGE_R | PAGE_W);

    // 映射用户页。
    for (uint32_t off = 0; off < image_size; off += PAGE_SIZE) {
        paddr_t page = alloc_pages(1);

        // 处理要复制的数据小于页面大小的情况。
        size_t remaining = image_size - off;
        size_t copy_size = PAGE_SIZE <= remaining ? PAGE_SIZE : remaining;

        // 填充并映射页面。
        memcpy((void *)page, image + off, copy_size);
        map_page(page_table, USER_BASE + off, page,
                PAGE_U | PAGE_R | PAGE_W | PAGE_X);
    }

    proc->pid = i + 1;
    proc->state = PROC_RUNNABLE;
    proc->sp = (uint32_t)sp;
    proc->page_table = page_table;
    return proc;
}

void delay(void) {
    for (int i = 0; i < 30000000; i++)
        __asm__ __volatile__("nop");
}

void yield(void) {
    struct process *next = idle_proc;

    // 搜索可运行的进程
    for (int i = 0; i < PROCS_MAX; i++) {
        struct process *proc = &procs[(current_proc->pid + i) % PROCS_MAX];
        if (proc->state == PROC_RUNNABLE && proc->pid > 0) {
        next = proc;
        break;
        }
    }

    // 如果除了当前进程外没有可运行的进程，返回并继续处理
    if (next == current_proc) return;

    __asm__ __volatile__(
        "sfence.vma\n"
        "csrw satp, %[satp]\n"
        "sfence.vma\n"
        "csrw sscratch, %[sscratch]\n"
        :
        // 不要忘记尾随逗号！
        : [satp] "r"(SATP_SV32 | ((uint32_t)next->page_table / PAGE_SIZE)),
          [sscratch] "r"((uint32_t)&next->stack[sizeof(next->stack)])
    );

    // 上下文切换
    struct process *prev = current_proc;
    current_proc = next;
    switch_context(&prev->sp, &next->sp);
}

void proc_a_entry(void) {
    printf("starting process A\n");
    while (1) {
        putchar('A');
        yield();
    }
}

void proc_b_entry(void) {
    printf("starting process B\n");
    while (1) {
        putchar('B');
        yield();
    }
}

long getchar(void) {
    struct sbiret ret = sbi_call(0, 0, 0, 0, 0, 0, 0, 2);
    return ret.error;
}


void handle_syscall(struct trap_frame *f) {
  // 通过检查 a3 寄存器的值来确定系统调用的类型
    switch (f->a3) {
    case SYS_PUTCHAR:
        putchar(f->a0);
        break;
    case SYS_GETCHAR:
        while (1) {
        long ch = getchar();
        if (ch >= 0) {
            f->a0 = ch;
            break;
        }
        yield();
        }
        break;
    case SYS_READFILE:
    case SYS_WRITEFILE: {
        const char *filename = (const char *)f->a0;
        char *buf = (char *)f->a1;
        int len = f->a2;
        struct file *file = fs_lookup(filename);
        if (!file) {
            printf("file not found: %s\n", filename);
            f->a0 = -1;
            break;
        }

        if (len > (int)sizeof(file->data)) len = file->size;

        if (f->a3 == SYS_WRITEFILE) {
            memcpy(file->data, buf, len);
            file->size = len;
            fs_flush();
        } else {
            memcpy(buf, file->data, len);
        }

        f->a0 = len;
        break;
    }
    default:
        PANIC("unexpected syscall a3=%x\n", f->a3);
    }
}

/*
    是否调用了 ecall 指令可以通过检查 scause 的值来确定。
    除了调用 handle_syscall函数外，还将 4（ecall 指令的大小）加到 sepc 的值上。
    这是因为 sepc指向导致异常的程序计数器，它指向 ecall指令。
    如果不改变它，内核会返回到同一个位置，并且 ecall 指令会被重复执行。
*/
void handle_trap(struct trap_frame *trap_frame) {
    uint32_t scause = READ_CSR(scause);
    uint32_t stval = READ_CSR(stval);
    uint32_t user_pc = READ_CSR(sepc);

    if (scause == SCAUSE_ECALL) {
        handle_syscall(trap_frame);
        user_pc += 4;
    } else {
        PANIC("unexpected trap scause=%x, stval=%x, sepc=%x\n", 
            scause, stval, user_pc);
    }

    WRITE_CSR(sepc, user_pc);
}

uint32_t virtio_reg_read32(unsigned offset) {
    return *((volatile uint32_t *)(VIRTIO_BLK_PADDR + offset));
}

uint64_t virtio_reg_read64(unsigned offset) {
    return *((volatile uint64_t *)(VIRTIO_BLK_PADDR + offset));
}

void virtio_reg_write32(unsigned offset, uint32_t value) {
    *((volatile uint32_t *)(VIRTIO_BLK_PADDR + offset)) = value;
}

bool virtq_is_busy(struct virtio_virtq *vq) {
    return vq->last_used_index != *vq->used_index;
}

void virtq_kick(struct virtio_virtq *vq, int desc_index) {
    vq->avail.ring[vq->avail.index % VIRTQ_ENTRY_NUM] = desc_index;
    vq->avail.index++;
    __sync_synchronize();
    virtio_reg_write32(VIRTIO_REG_QUEUE_NOTIFY, vq->queue_index);
    vq->last_used_index = *vq->used_index;
}

// 从 virtio-blk 设备读取/写入。
void read_write_disk(void *buf, unsigned sector, int is_write) {
    if (sector >= blk_capacity / SECTOR_SIZE) {
        printf("virtio: tried to read/write sector=%d, but capacity is %d\n",
            sector, blk_capacity / SECTOR_SIZE);
        return;
    }

    // // 根据 virtio-blk 规范构造请求。
    blk_req->sector = sector;
    blk_req->type = is_write ? VIRTIO_BLK_T_OUT : VIRTIO_BLK_T_IN;
    if (is_write)
        memcpy(blk_req->data, buf, SECTOR_SIZE);

    // 构造 virtqueue 描述符(使用 3 个描述符)
    struct virtio_virtq *vq = blk_request_vq;
    vq->descs[0].addr = blk_req_paddr;
    vq->descs[0].len = sizeof(uint32_t) * 2 + sizeof(uint64_t);
    vq->descs[0].flags = VIRTQ_DESC_F_NEXT;
    vq->descs[0].next = 1;

    vq->descs[1].addr = blk_req_paddr + offsetof(struct virtio_blk_req, data);
    vq->descs[1].len = SECTOR_SIZE;
    vq->descs[1].flags = VIRTQ_DESC_F_NEXT | (is_write ? 0 : VIRTQ_DESC_F_WRITE);
    vq->descs[1].next = 2;

    vq->descs[2].addr = blk_req_paddr + offsetof(struct virtio_blk_req, status);
    vq->descs[2].len = sizeof(uint8_t);
    vq->descs[2].flags = VIRTQ_DESC_F_WRITE;

    // 通知设备有新的请求。
    virtq_kick(vq, 0);

    // 等待设备完成处理。
    while (virtq_is_busy(vq))
        ;

    // virtio-blk：如果返回非零值，则表示错误。
    if (blk_req->status != 0) {
        printf("virtio: warn: failed to read/write sector=%d status=%d\n", sector,
            blk_req->status);
        return;
    }

    // 对于读操作，将数据复制到缓冲区。
    if (!is_write)
        memcpy(buf, blk_req->data, SECTOR_SIZE);

  /*
      发送请求按以下步骤进行：
      在 blk_req 中构造请求。指定要访问的扇区号和读/写类型。
      构造指向 blk_req 各个区域的描述符链(见下文)。
      将描述符链的头描述符索引添加到 Available Ring。
      通知设备有新的待处理请求。
      等待设备完成处理(又称忙等待或轮询)。
      检查设备的响应。
  */
}

void virtio_reg_fetch_and_or32(unsigned offset, uint32_t value) {
    virtio_reg_write32(offset, virtio_reg_read32(offset) | value);
}

struct virtio_virtq *virtq_init(unsigned index) {
    // 为 virtqueue 分配一个区域。
    paddr_t virtq_paddr =
        alloc_pages(align_up(sizeof(struct virtio_virtq), PAGE_SIZE) / PAGE_SIZE);
    struct virtio_virtq *vq = (struct virtio_virtq *)virtq_paddr;
    vq->queue_index = index;
    vq->used_index = (volatile uint16_t *)&vq->used.index;
    // 1. 通过写入队列的索引(第一个队列为 0)到 QueueSel 来选择队列。
    virtio_reg_write32(VIRTIO_REG_QUEUE_SEL, index);
    // 5. 通过写入大小到 QueueNum 来通知设备队列大小。
    virtio_reg_write32(VIRTIO_REG_QUEUE_NUM, VIRTQ_ENTRY_NUM);
    // 6. 通过写入其字节值到 QueueAlign 来通知设备已使用的对齐方式。
    virtio_reg_write32(VIRTIO_REG_QUEUE_ALIGN, 0);
    // 7. 将队列第一页的物理编号写入 QueuePFN 寄存器。
    virtio_reg_write32(VIRTIO_REG_QUEUE_PFN, virtq_paddr);
    return vq;
}

void virtio_blk_init(void) {
    if (virtio_reg_read32(VIRTIO_REG_MAGIC) != 0x74726976)
        PANIC("virtio: invalid magic value");
    if (virtio_reg_read32(VIRTIO_REG_VERSION) != 1)
        PANIC("virtio: invalid version");
    if (virtio_reg_read32(VIRTIO_REG_DEVICE_ID) != VIRTIO_DEVICE_BLK)
        PANIC("virtio: invalid device id");

    // 1. 重置设备。
    virtio_reg_write32(VIRTIO_REG_DEVICE_STATUS, 0);
    // 2. 设置 ACKNOWLEDGE 状态位：表示客户操作系统已注意到该设备。
    virtio_reg_fetch_and_or32(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_ACK);
    // 3. 设置 DRIVER 状态位。
    virtio_reg_fetch_and_or32(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_DRIVER);
    // 5. 设置 FEATURES_OK 状态位。
    virtio_reg_fetch_and_or32(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_FEAT_OK);
    // 7. 执行设备特定的设置，包括发现设备的 virtqueues
    blk_request_vq = virtq_init(0);
    // 8. 设置 DRIVER_OK 状态位。
    virtio_reg_write32(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_DRIVER_OK);

    // 获取磁盘容量。
    blk_capacity = virtio_reg_read64(VIRTIO_REG_DEVICE_CONFIG + 0) * SECTOR_SIZE;
    printf("virtio-blk: capacity is %d bytes\n", blk_capacity);

    // 分配一个区域来存储对设备的请求。
    blk_req_paddr =
        alloc_pages(align_up(sizeof(*blk_req), PAGE_SIZE) / PAGE_SIZE);
    blk_req = (struct virtio_blk_req *)blk_req_paddr;
}

void fs_init(void) {
    for (unsigned sector = 0; sector < sizeof(disk) / SECTOR_SIZE; sector++)
        read_write_disk(&disk[sector * SECTOR_SIZE], sector, false);

    unsigned off = 0;
    for (int i = 0; i < FILES_MAX; i++) {
        struct tar_header *header = (struct tar_header *)&disk[off];

        if (header->name[0] == '\0') break;

        if (strcmp(header->magic, "ustar") != 0)
        PANIC("invalid tar header: magic=\"%s\"", header->magic);

        int filesz = oct2int(header->size, sizeof(header->size));
        struct file *file = &files[i];
        file->in_use = true;
        strcpy(file->name, header->name);
        memcpy(file->data, header->data, filesz);
        file->size = filesz;
        printf("file: %s, size=%d\n", file->name, file->size);

        off += align_up(sizeof(struct tar_header) + filesz, SECTOR_SIZE);
    }
}

void fs_flush(void) {
    // 将所有文件内容复制到 `disk` 缓冲区
    memset(disk, 0, sizeof(disk));
    unsigned off = 0;
    for (int file_i = 0; file_i < FILES_MAX; file_i++) {
        struct file *file = &files[file_i];
        if (!file->in_use)
        continue;

        struct tar_header *header = (struct tar_header *)&disk[off];
        memset(header, 0, sizeof(*header));
        strcpy(header->name, file->name);
        strcpy(header->mode, "000644");
        strcpy(header->magic, "ustar");
        strcpy(header->version, "00");
        header->type = '0';

        // 将文件大小转换为八进制字符串
        int filesz = file->size;
        for (int i = sizeof(header->size); i > 0; i--) {
            header->size[i - 1] = (filesz % 8) + '0';
            filesz /= 8;
        }

        // 计算校验和
        int checksum = ' ' * sizeof(header->checksum);
        for (unsigned i = 0; i < sizeof(struct tar_header); i++)
            checksum += (unsigned char)disk[off + i];

        for (int i = 5; i >= 0; i--) {
            header->checksum[i] = (checksum % 8) + '0';
            checksum /= 8;
        }

        // 复制文件数据
        memcpy(header->data, file->data, file->size);
        off += align_up(sizeof(struct tar_header) + file->size, SECTOR_SIZE);
    }

    // 将 `disk` 缓冲区写入 virtio-blk
    for (unsigned sector = 0; sector < sizeof(disk) / SECTOR_SIZE; sector++)
        read_write_disk(&disk[sector * SECTOR_SIZE], sector, true);

    printf("wrote %d bytes to disk\n", sizeof(disk));
}

void test_virt_blk(void) {
    char buf[SECTOR_SIZE];
    read_write_disk(buf, 0, false /* 从磁盘读取 */);
    printf("first sector: %s\n", buf);

    strcpy(buf, "hello from kernel!!!\n");
    read_write_disk(buf, 0, true /* 写入磁盘 */);
}

void kernel_main(void) {
    memset(__bss, 0, (size_t)__bss_end - (size_t)__bss);
    printf("\n\n");
    WRITE_CSR(stvec, (uint32_t)kernel_entry);

    virtio_blk_init();

    fs_init();

    idle_proc = create_process(NULL, 0);
    idle_proc->pid = 0;                  // idle
    current_proc = idle_proc;

    create_process(_binary_shell_bin_start, (size_t)_binary_shell_bin_size);

    yield();
    PANIC("switched to idle process");
}