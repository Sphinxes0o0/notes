# VFS Exec 与 Binfmt

## 1. 模块架构

### 1.1 功能概述

Exec 是 Linux 执行新程序的核心机制。Binfmt (Binary Format) 是可执行文件格式的注册框架，支持多种可执行格式如 ELF、script 等。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/exec.c` | 程序加载核心 |
| `fs/binfmt_script.c` | 脚本解释器 |
| `fs/binfmt_elf.c` | ELF 格式 |
| `fs/binfmt_aout.c` | a.out 格式 |
| `include/linux/binfmts.h` | binfmt 接口 |

## 2. 核心数据结构

### 2.1 struct linux_binprm

```c
// include/linux/binfmts.h:100
struct linux_binprm {
    struct file *file;                 // 可执行文件
    const char *filename;              // 文件名
    const char *interp;                // 解释器
    struct page **page;                // 参数页面
    unsigned long p;                   // 栈指针
    unsigned long shdr0;               // section header 0
    unsigned long header0;             // ELF header
    unsigned long interp_flags;
    unsigned long vma_pages;           // VMA 页面数
    unsigned long min_copied;          // 复制的最小长度
    unsigned long cred_prepared:1;     // 凭证已准备
    unsigned long executable_stack:1;   // 可执行栈
    unsigned long entry:2;
    struct mm_struct *mm;              // 内存描述符
    struct cred *cred;                 // 凭证
    int argc, envc;                   // 参数数量
    const char *const *argv;           // 参数向量
    const char *const *envp;           // 环境变量
    struct rlimit saved_rlim[ RLIM_NLIMITS ];
    unsigned long rlim_stack_max;
    // ...
};
```

### 2.2 struct linux_binfmt

```c
// include/linux/binfmts.h:80
struct linux_binfmt {
    struct list_head lh;
    struct module *module;
    int (*load_binary)(struct linux_binprm *);
    int (*load_shlib)(struct file *);
    int (*core_dump)(struct coredump_params *cprm);
    unsigned long min_coredump;
    int hasvdso;
};
```

## 3. Exec 流程

### 3.1 sys_execve()

```c
// fs/exec.c:2000
int do_execve(struct user_arg_ptr *argv, struct user_arg_ptr *envp)
{
    return do_execveat(AT_FDCWD, "/proc/self/exe", argv, envp, 0);
}
```

### 3.2 do_execveat()

```c
// fs/exec.c:1900
int do_execveat(int dfd, const char *filename,
                struct user_arg_ptr argv,
                struct user_arg_ptr envp,
                int flags)
{
    struct linux_binprm *bprm;

    // 分配 binprm
    bprm = kzalloc(sizeof(*bprm), GFP_KERNEL);
    if (!bprm)
        return -ENOMEM;

    // 打开可执行文件
    ret = open_exec(filename);

    // 准备参数
    ret = prepare_binprm(bprm);

    // 检查权限
    ret = security_bprm_check(bprm);

    // 执行
    ret = exec_binprm(bprm);

    // 释放
    free_bprm(bprm);

    return ret;
}
```

### 3.3 exec_binprm()

```c
// fs/exec.c:1850
static int exec_binprm(struct linux_binprm *bprm)
{
    struct file *file = bprm->file;
    struct linux_binfmt *fmt;

    // 搜索并调用二进制格式的 load_binary
    list_for_each_entry(fmt, &formats, lh) {
        if (!try_module_get(fmt->module))
            continue;

        // 调用格式特定的加载函数
        bprm->recursion_depth++;
        ret = fmt->load_binary(bprm);
        bprm->recursion_depth--;

        module_put(fmt->module);
        if (ret >= 0)
            return ret;
    }

    return -ENOEXEC;
}
```

## 4. ELF 加载

### 4.1 load_elf_binary()

```c
// fs/binfmt_elf.c:600
static int load_elf_binary(struct linux_binprm *bprm)
{
    struct file *file = bprm->file;
    struct elf_phdr *elf_ppnt, *elf_phdata;
    struct elf_hdr *elf_ex = (struct elf_hdr *)bprm->buf;
    unsigned long elf_bss, elf_brk;
    int retval;

    // 检查 ELF magic
    if (memcmp(elf_ex->e_ident, ELFMAG, SELFMAG) != 0)
        return -ENOEXEC;

    // 读取程序头
    elf_phdata = load_phdrs(file, elf_ex);
    if (IS_ERR(elf_phdata))
        return PTR_ERR(elf_phdata);

    // 查找解释器
    for (elf_ppnt = elf_phdata; elf_ppnt++ < ...; ) {
        if (elf_ppnt->p_type == PT_INTERP) {
            // 加载解释器
            load_elf_interp(...);
        }
    }

    // 设置 brk
    elf_brk = ELF_PAGESTART(elf_bss + ELF_MIN_ALIGN - 1);

    // 创建 VMA
    for (elf_ppnt = elf_phdata; elf_ppnt++ < ...; ) {
        if (elf_ppnt->p_type != PT_LOAD)
            continue;

        // 映射段
        elf_map(file, elf_ppnt, ...);
    }

    // 设置入口点
    current->start_code = elf_entry;

    // 准备栈
    retval = setup_arg_pages(bprm, ...);

    // 复制环境和参数
    retval = copy_strings(bprm->envc, bprm->envp, bprm);
    retval = copy_strings(bprm->argc, bprm->argv, bprm);

    // 清除当前地址空间
    flush_old_exec(bprm);

    // 设置新的地址空间
    install_exec_creds(bprm);

    // 启动新程序
    start_thread(regs, elf_entry, bprm->p);

    return 0;
}
```

### 4.2 elf_map()

```c
// fs/binfmt_elf.c:400
static unsigned long elf_map(struct file *file, struct elf_phdr *elf_ppnt,
                            int executable, unsigned long *interp_map_addr)
{
    unsigned long page, offset;
    unsigned long map_addr;
    unsigned long prot = PROT_READ | PROT_EXEC;

    // 计算偏移和地址
    offset = elf_ppnt->p_offset;
    map_addr = *interp_map_addr;

    // mmap 映射
    map_addr = do_mmap(file, map_addr, elf_ppnt->p_filesz, prot,
                       MAP_FIXED | MAP_PRIVATE, offset);

    return map_addr;
}
```

## 5. 脚本解释器

### 5.1 load_script()

```c
// fs/binfmt_script.c:100
static int load_script(struct linux_binprm *bprm)
{
    const char *i_arg, *i_name;
    char *cp;
    struct file *file;
    int retval;

    // 检查 #! 标志
    if ((bprm->buf[0] != '#') || (bprm->buf[1] != '!'))
        return -ENOEXEC;

    // 解析解释器路径和参数
    bprm->buf[255] = '\0';
    cp = strchr(bprm->buf, '\n');

    // 提取解释器
    i_name = cp + 1;
    for (cp = i_name; *cp && (*cp == ' '); cp++)
        ;

    // 查找参数
    i_arg = strchr(cp, ' ');
    if (i_arg) {
        *i_arg = '\0';
        i_arg++;
    }

    // 打开解释器
    file = open_exec(i_name);
    if (IS_ERR(file))
        return PTR_ERR(file);

    // 替换 bprm 中的文件名
    bprm->file = file;
    bprm->filename = i_name;

    // 递归调用 exec_binprm
    return search_binary_handler(bprm);
}
```

## 6. 参数页面管理

### 6.1 prepare_binprm()

```c
// fs/exec.c:200
int prepare_binprm(struct linux_binprm *bprm)
{
    struct file *file = bprm->file;
    umode_t mode;
    struct inode *inode = file_inode(file);
    int retval;

    // 检查权限
    mode = inode->i_mode;
    if (IS_SUID(mode)) {
        bprm->per_clear |= PER_CLEAR_ON_SETID;
        bprm->cred->euid = inode->i_uid;
    }

    if (IS_SGID(mode)) {
        bprm->per_clear |= PER_CLEAR_ON_SETID;
        bprm->cred->egid = inode->i_gid;
    }

    // 读取文件头
    memset(bprm->buf, 0, sizeof(bprm->buf));
    retval = kernel_read(file, 0, bprm->buf, sizeof(bprm->buf));

    return retval;
}
```

### 6.2 setup_arg_pages()

```c
// fs/exec.c:400
int setup_arg_pages(struct linux_binprm *bprm, unsigned long page_size)
{
    unsigned long stack_base;
    struct vm_area_struct *vma;
    struct mm_struct *mm = current->mm;

    // 计算栈基址
    stack_base = STACK_TOP;
    stack_base -= (page_size - 1);
    stack_base &= ~(page_size - 1);

    // 映射参数页面
    for (i = 0; i < MAX_ARG_PAGES; i++) {
        struct page *page = bprm->page[i];
        if (page) {
            vma = vm_area_alloc(mm);
            vm_map_range(vma, stack_base, page, PAGE_SIZE);
            stack_base += PAGE_SIZE;
        }
    }

    // 设置栈指针
    bprm->p = stack_base;

    return 0;
}
```

## 7. 凭证管理

### 7.1 install_exec_creds()

```c
// fs/exec.c:500
void install_exec_creds(struct linux_binprm *bprm)
{
    // 安装新的凭证
    commit_creds(bprm->cred);

    // 清除 setuid 标志
    current->pdeath_signal = 0;

    // 设置执行域
    call_int_hook(bprm, BINPRM_HOOK);
}
```

### 7.2 compute_creds()

```c
// fs/exec.c:300
void compute_creds(struct linux_binprm *bprm)
{
    const struct cred *old = current_cred();

    // 复制凭证
    bprm->cred = prepare_creds();
    if (!bprm->cred)
        return;

    // 应用 SUID/SGID
    if (bprm->file->f_path.mnt->mnt_flags & MNT_NOSUID)
        return;

    // 检查 inode 的 suid/sgid
    if (mode & S_ISUID) {
        bprm->cred->euid = inode->i_uid;
        bprm->per_clear |= PER_CLEAR_ON_SETID;
    }

    if (mode & S_ISGID) {
        bprm->cred->egid = inode->i_gid;
        bprm->per_clear |= PER_CLEAR_ON_SETID;
    }
}
```

## 8. 线程启动

### 8.1 start_thread()

```c
// fs/binfmt_elf.c:200
void start_thread(struct pt_regs *regs, unsigned long entry,
                  unsigned long stack)
{
    // 设置指令指针
    regs->ip = entry;
    // 设置栈指针
    regs->sp = stack;
    // 清除标志
    regs->flags = 0;
    // 设置 CS/SS
    regs->cs = __USER_CS;
    regs->ss = __USER_DS;
}
```

## 9. Core Dump

### 9.1 do_coredump()

```c
// fs/coredump.c:200
int do_coredump(long signr, struct pt_regs *regs)
{
    struct linux_binfmt *fmt;
    struct core_state *core_state;
    struct core_dump_params cprm = {
        .regs = regs,
        .signr = signr,
        .limit = rlimit(RLIMIT_CORE),
    };

    // 检查 limit
    if (cprm.limit == 0)
        return 0;

    // 获取二进制格式
    fmt = current->binfmt;
    if (!fmt || !fmt->core_dump)
        return 0;

    // 创建 core 文件
    cprm.file = filp_open("core", O_CREAT | O_RDWR, 0600);

    // 调用格式特定的 core_dump
    fmt->core_dump(&cprm);

    return 0;
}
```

## 10. Binfmt 注册

### 10.1 register_binfmt()

```c
// fs/exec.c:1800
int register_binfmt(struct linux_binfmt *fmt)
{
    if (!fmt)
        return -EINVAL;
    fmt->module = NULL;
    list_add(&fmt->lh, &formats);
    return 0;
}
```

### 10.2 unregister_binfmt()

```c
// fs/exec.c:1820
void unregister_binfmt(struct linux_binfmt *fmt)
{
    list_del(&fmt->lh);
}
```

## 11. Exec 执行流程图

```
用户: execve("/bin/ls", ["ls", "-l"], envp)

内核路径:
1. do_execveat()
   |
2. open_exec()
   |  打开可执行文件
   |
3. prepare_binprm()
   |  检查权限，读取文件头
   |
4. search_binary_handler()
   |  遍历注册的 binfmt
   |
5. ELF 格式:
   load_elf_binary()
   |
   +---> 检查 magic
   +---> 读取 program headers
   +---> 映射 segments (elf_map)
   +---> 设置入口点
   +---> setup_arg_pages()
   +---> flush_old_exec()
   +---> start_thread()

6. 脚本格式:
   load_script()
   |
   +---> 检查 #!
   +---> 提取解释器路径
   +---> open_exec(解释器)
   +---> search_binary_handler()
         (递归)
```

## 12. 常用 binfmt 格式

| 格式 | 文件 | 说明 |
|------|------|------|
| ELF | binfmt_elf.c | Executable and Linkable Format |
| Script | binfmt_script.c | #! 解释器脚本 |
| a.out | binfmt_aout.c | 早期 Unix 格式 |
| flat | binfmt_flat.c | 嵌入式格式 |
| FDPIC | binfmt_elf_fdpic.c | FDPIC ELF |
