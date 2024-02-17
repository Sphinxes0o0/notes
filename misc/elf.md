---
title: elf简介
date: 2022-01-15 18:03:28
tags:
    - linux
    - c
    - elf
---

## 回顾

程序的转换处理过程:

1. C代码 hello.c:

```C
#include <stdio.h>

int main() {
    printf("hello!");
}
```
2. 预处理

```bash
$ gcc -E hello.c -o hello.i
# 0 "hello.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 0 "<command-line>" 2
# 1 "hello.c"
# 1 "/usr/include/stdio.h" 1 3 4
# 27 "/usr/include/stdio.h" 3 4
# 1 "/usr/include/bits/libc-header-start.h" 1 3 4
# 33 "/usr/include/bits/libc-header-start.h" 3 4
# 1 "/usr/include/features.h" 1 3 4
# 473 "/usr/include/features.h" 3 4
# 1 "/usr/include/sys/cdefs.h" 1 3 4
# 462 "/usr/include/sys/cdefs.h" 3 4
# 1 "/usr/include/bits/wordsize.h" 1 3 4
# 463 "/usr/include/sys/cdefs.h" 2 3 4
# 1 "/usr/include/bits/long-double.h" 1 3 4
# 464 "/usr/include/sys/cdefs.h" 2 3 4
# 474 "/usr/include/features.h" 2 3 4
# 497 "/usr/include/features.h" 3 4
# 1 "/usr/include/gnu/stubs.h" 1 3 4
# 10 "/usr/include/gnu/stubs.h" 3 4
# 1 "/usr/include/gnu/stubs-64.h" 1 3 4
# 11 "/usr/include/gnu/stubs.h" 2 3 4
# 498 "/usr/include/features.h" 2 3 4
# 34 "/usr/include/bits/libc-header-start.h" 2 3 4
# 28 "/usr/include/stdio.h" 2 3 4





# 1 "/usr/lib/gcc/x86_64-pc-linux-gnu/11.1.0/include/stddef.h" 1 3 4
# 209 "/usr/lib/gcc/x86_64-pc-linux-gnu/11.1.0/include/stddef.h" 3 4

# 209 "/usr/lib/gcc/x86_64-pc-linux-gnu/11.1.0/include/stddef.h" 3 4
typedef long unsigned int size_t;
# 34 "/usr/include/stdio.h" 2 3 4


# 1 "/usr/lib/gcc/x86_64-pc-linux-gnu/11.1.0/include/stdarg.h" 1 3 4
# 40 "/usr/lib/gcc/x86_64-pc-linux-gnu/11.1.0/include/stdarg.h" 3 4
typedef __builtin_va_list __gnuc_va_list;
# 37 "/usr/include/stdio.h" 2 3 4

# 1 "/usr/include/bits/types.h" 1 3 4
# 27 "/usr/include/bits/types.h" 3 4
# 1 "/usr/include/bits/wordsize.h" 1 3 4
# 28 "/usr/include/bits/types.h" 2 3 4
# 1 "/usr/include/bits/timesize.h" 1 3 4
# 29 "/usr/include/bits/types.h" 2 3 4


typedef unsigned char __u_char;
typedef unsigned short int __u_short;
typedef unsigned int __u_int;
typedef unsigned long int __u_long;


typedef signed char __int8_t;
typedef unsigned char __uint8_t;
typedef signed short int __int16_t;
typedef unsigned short int __uint16_t;
typedef signed int __int32_t;
typedef unsigned int __uint32_t;

typedef signed long int __int64_t;
typedef unsigned long int __uint64_t;






typedef __int8_t __int_least8_t;
typedef __uint8_t __uint_least8_t;
typedef __int16_t __int_least16_t;
typedef __uint16_t __uint_least16_t;
typedef __int32_t __int_least32_t;
typedef __uint32_t __uint_least32_t;
typedef __int64_t __int_least64_t;
typedef __uint64_t __uint_least64_t;



typedef long int __quad_t;
typedef unsigned long int __u_quad_t;







typedef long int __intmax_t;
typedef unsigned long int __uintmax_t;
# 141 "/usr/include/bits/types.h" 3 4
# 1 "/usr/include/bits/typesizes.h" 1 3 4
# 142 "/usr/include/bits/types.h" 2 3 4
# 1 "/usr/include/bits/time64.h" 1 3 4
# 143 "/usr/include/bits/types.h" 2 3 4


typedef unsigned long int __dev_t;
typedef unsigned int __uid_t;
typedef unsigned int __gid_t;
typedef unsigned long int __ino_t;
typedef unsigned long int __ino64_t;
typedef unsigned int __mode_t;
typedef unsigned long int __nlink_t;
typedef long int __off_t;
typedef long int __off64_t;
typedef int __pid_t;
typedef struct { int __val[2]; } __fsid_t;
typedef long int __clock_t;
typedef unsigned long int __rlim_t;
typedef unsigned long int __rlim64_t;
typedef unsigned int __id_t;
typedef long int __time_t;
typedef unsigned int __useconds_t;
typedef long int __suseconds_t;
typedef long int __suseconds64_t;

typedef int __daddr_t;
typedef int __key_t;


typedef int __clockid_t;


typedef void * __timer_t;


typedef long int __blksize_t;




typedef long int __blkcnt_t;
typedef long int __blkcnt64_t;


typedef unsigned long int __fsblkcnt_t;
typedef unsigned long int __fsblkcnt64_t;


typedef unsigned long int __fsfilcnt_t;
typedef unsigned long int __fsfilcnt64_t;


typedef long int __fsword_t;

typedef long int __ssize_t;


typedef long int __syscall_slong_t;

typedef unsigned long int __syscall_ulong_t;



typedef __off64_t __loff_t;
typedef char *__caddr_t;


typedef long int __intptr_t;


typedef unsigned int __socklen_t;




typedef int __sig_atomic_t;
# 39 "/usr/include/stdio.h" 2 3 4
# 1 "/usr/include/bits/types/__fpos_t.h" 1 3 4




# 1 "/usr/include/bits/types/__mbstate_t.h" 1 3 4
# 13 "/usr/include/bits/types/__mbstate_t.h" 3 4
typedef struct
{
  int __count;
  union
  {
    unsigned int __wch;
    char __wchb[4];
  } __value;
} __mbstate_t;
# 6 "/usr/include/bits/types/__fpos_t.h" 2 3 4




typedef struct _G_fpos_t
{
  __off_t __pos;
  __mbstate_t __state;
} __fpos_t;
# 40 "/usr/include/stdio.h" 2 3 4
# 1 "/usr/include/bits/types/__fpos64_t.h" 1 3 4
# 10 "/usr/include/bits/types/__fpos64_t.h" 3 4
typedef struct _G_fpos64_t
{
  __off64_t __pos;
  __mbstate_t __state;
} __fpos64_t;
# 41 "/usr/include/stdio.h" 2 3 4
# 1 "/usr/include/bits/types/__FILE.h" 1 3 4



struct _IO_FILE;
typedef struct _IO_FILE __FILE;
# 42 "/usr/include/stdio.h" 2 3 4
# 1 "/usr/include/bits/types/FILE.h" 1 3 4



struct _IO_FILE;


typedef struct _IO_FILE FILE;
# 43 "/usr/include/stdio.h" 2 3 4
# 1 "/usr/include/bits/types/struct_FILE.h" 1 3 4
# 35 "/usr/include/bits/types/struct_FILE.h" 3 4
struct _IO_FILE;
struct _IO_marker;
struct _IO_codecvt;
struct _IO_wide_data;




typedef void _IO_lock_t;





struct _IO_FILE
{
  int _flags;


  char *_IO_read_ptr;
  char *_IO_read_end;
  char *_IO_read_base;
  char *_IO_write_base;
  char *_IO_write_ptr;
  char *_IO_write_end;
  char *_IO_buf_base;
  char *_IO_buf_end;


  char *_IO_save_base;
  char *_IO_backup_base;
  char *_IO_save_end;

  struct _IO_marker *_markers;

  struct _IO_FILE *_chain;

  int _fileno;
  int _flags2;
  __off_t _old_offset;


  unsigned short _cur_column;
  signed char _vtable_offset;
  char _shortbuf[1];

  _IO_lock_t *_lock;







  __off64_t _offset;

  struct _IO_codecvt *_codecvt;
  struct _IO_wide_data *_wide_data;
  struct _IO_FILE *_freeres_list;
  void *_freeres_buf;
  size_t __pad5;
  int _mode;

  char _unused2[15 * sizeof (int) - 4 * sizeof (void *) - sizeof (size_t)];
};
# 44 "/usr/include/stdio.h" 2 3 4
# 52 "/usr/include/stdio.h" 3 4
typedef __gnuc_va_list va_list;
# 63 "/usr/include/stdio.h" 3 4
typedef __off_t off_t;
# 77 "/usr/include/stdio.h" 3 4
typedef __ssize_t ssize_t;






typedef __fpos_t fpos_t;
# 133 "/usr/include/stdio.h" 3 4
# 1 "/usr/include/bits/stdio_lim.h" 1 3 4
# 134 "/usr/include/stdio.h" 2 3 4



extern FILE *stdin;
extern FILE *stdout;
extern FILE *stderr;






extern int remove (const char *__filename) __attribute__ ((__nothrow__ , __leaf__));

extern int rename (const char *__old, const char *__new) __attribute__ ((__nothrow__ , __leaf__));



extern int renameat (int __oldfd, const char *__old, int __newfd,
       const char *__new) __attribute__ ((__nothrow__ , __leaf__));
# 173 "/usr/include/stdio.h" 3 4
extern FILE *tmpfile (void) ;
# 187 "/usr/include/stdio.h" 3 4
extern char *tmpnam (char *__s) __attribute__ ((__nothrow__ , __leaf__)) ;




extern char *tmpnam_r (char *__s) __attribute__ ((__nothrow__ , __leaf__)) ;
# 204 "/usr/include/stdio.h" 3 4
extern char *tempnam (const char *__dir, const char *__pfx)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__malloc__)) ;







extern int fclose (FILE *__stream);




extern int fflush (FILE *__stream);
# 227 "/usr/include/stdio.h" 3 4
extern int fflush_unlocked (FILE *__stream);
# 246 "/usr/include/stdio.h" 3 4
extern FILE *fopen (const char *__restrict __filename,
      const char *__restrict __modes) ;




extern FILE *freopen (const char *__restrict __filename,
        const char *__restrict __modes,
        FILE *__restrict __stream) ;
# 279 "/usr/include/stdio.h" 3 4
extern FILE *fdopen (int __fd, const char *__modes) __attribute__ ((__nothrow__ , __leaf__)) ;
# 292 "/usr/include/stdio.h" 3 4
extern FILE *fmemopen (void *__s, size_t __len, const char *__modes)
  __attribute__ ((__nothrow__ , __leaf__)) ;




extern FILE *open_memstream (char **__bufloc, size_t *__sizeloc) __attribute__ ((__nothrow__ , __leaf__)) ;





extern void setbuf (FILE *__restrict __stream, char *__restrict __buf) __attribute__ ((__nothrow__ , __leaf__));



extern int setvbuf (FILE *__restrict __stream, char *__restrict __buf,
      int __modes, size_t __n) __attribute__ ((__nothrow__ , __leaf__));




extern void setbuffer (FILE *__restrict __stream, char *__restrict __buf,
         size_t __size) __attribute__ ((__nothrow__ , __leaf__));


extern void setlinebuf (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__));







extern int fprintf (FILE *__restrict __stream,
      const char *__restrict __format, ...);




extern int printf (const char *__restrict __format, ...);

extern int sprintf (char *__restrict __s,
      const char *__restrict __format, ...) __attribute__ ((__nothrow__));





extern int vfprintf (FILE *__restrict __s, const char *__restrict __format,
       __gnuc_va_list __arg);




extern int vprintf (const char *__restrict __format, __gnuc_va_list __arg);

extern int vsprintf (char *__restrict __s, const char *__restrict __format,
       __gnuc_va_list __arg) __attribute__ ((__nothrow__));



extern int snprintf (char *__restrict __s, size_t __maxlen,
       const char *__restrict __format, ...)
     __attribute__ ((__nothrow__)) __attribute__ ((__format__ (__printf__, 3, 4)));

extern int vsnprintf (char *__restrict __s, size_t __maxlen,
        const char *__restrict __format, __gnuc_va_list __arg)
     __attribute__ ((__nothrow__)) __attribute__ ((__format__ (__printf__, 3, 0)));
# 379 "/usr/include/stdio.h" 3 4
extern int vdprintf (int __fd, const char *__restrict __fmt,
       __gnuc_va_list __arg)
     __attribute__ ((__format__ (__printf__, 2, 0)));
extern int dprintf (int __fd, const char *__restrict __fmt, ...)
     __attribute__ ((__format__ (__printf__, 2, 3)));







extern int fscanf (FILE *__restrict __stream,
     const char *__restrict __format, ...) ;




extern int scanf (const char *__restrict __format, ...) ;

extern int sscanf (const char *__restrict __s,
     const char *__restrict __format, ...) __attribute__ ((__nothrow__ , __leaf__));





# 1 "/usr/include/bits/floatn.h" 1 3 4
# 119 "/usr/include/bits/floatn.h" 3 4
# 1 "/usr/include/bits/floatn-common.h" 1 3 4
# 24 "/usr/include/bits/floatn-common.h" 3 4
# 1 "/usr/include/bits/long-double.h" 1 3 4
# 25 "/usr/include/bits/floatn-common.h" 2 3 4
# 120 "/usr/include/bits/floatn.h" 2 3 4
# 407 "/usr/include/stdio.h" 2 3 4



extern int fscanf (FILE *__restrict __stream, const char *__restrict __format, ...) __asm__ ("" "__isoc99_fscanf")

                               ;
extern int scanf (const char *__restrict __format, ...) __asm__ ("" "__isoc99_scanf")
                              ;
extern int sscanf (const char *__restrict __s, const char *__restrict __format, ...) __asm__ ("" "__isoc99_sscanf") __attribute__ ((__nothrow__ , __leaf__))

                      ;
# 435 "/usr/include/stdio.h" 3 4
extern int vfscanf (FILE *__restrict __s, const char *__restrict __format,
      __gnuc_va_list __arg)
     __attribute__ ((__format__ (__scanf__, 2, 0))) ;





extern int vscanf (const char *__restrict __format, __gnuc_va_list __arg)
     __attribute__ ((__format__ (__scanf__, 1, 0))) ;


extern int vsscanf (const char *__restrict __s,
      const char *__restrict __format, __gnuc_va_list __arg)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__format__ (__scanf__, 2, 0)));





extern int vfscanf (FILE *__restrict __s, const char *__restrict __format, __gnuc_va_list __arg) __asm__ ("" "__isoc99_vfscanf")



     __attribute__ ((__format__ (__scanf__, 2, 0))) ;
extern int vscanf (const char *__restrict __format, __gnuc_va_list __arg) __asm__ ("" "__isoc99_vscanf")

     __attribute__ ((__format__ (__scanf__, 1, 0))) ;
extern int vsscanf (const char *__restrict __s, const char *__restrict __format, __gnuc_va_list __arg) __asm__ ("" "__isoc99_vsscanf") __attribute__ ((__nothrow__ , __leaf__))



     __attribute__ ((__format__ (__scanf__, 2, 0)));
# 489 "/usr/include/stdio.h" 3 4
extern int fgetc (FILE *__stream);
extern int getc (FILE *__stream);





extern int getchar (void);






extern int getc_unlocked (FILE *__stream);
extern int getchar_unlocked (void);
# 514 "/usr/include/stdio.h" 3 4
extern int fgetc_unlocked (FILE *__stream);
# 525 "/usr/include/stdio.h" 3 4
extern int fputc (int __c, FILE *__stream);
extern int putc (int __c, FILE *__stream);





extern int putchar (int __c);
# 541 "/usr/include/stdio.h" 3 4
extern int fputc_unlocked (int __c, FILE *__stream);







extern int putc_unlocked (int __c, FILE *__stream);
extern int putchar_unlocked (int __c);






extern int getw (FILE *__stream);


extern int putw (int __w, FILE *__stream);







extern char *fgets (char *__restrict __s, int __n, FILE *__restrict __stream)
     __attribute__ ((__access__ (__write_only__, 1, 2)));
# 608 "/usr/include/stdio.h" 3 4
extern __ssize_t __getdelim (char **__restrict __lineptr,
                             size_t *__restrict __n, int __delimiter,
                             FILE *__restrict __stream) ;
extern __ssize_t getdelim (char **__restrict __lineptr,
                           size_t *__restrict __n, int __delimiter,
                           FILE *__restrict __stream) ;







extern __ssize_t getline (char **__restrict __lineptr,
                          size_t *__restrict __n,
                          FILE *__restrict __stream) ;







extern int fputs (const char *__restrict __s, FILE *__restrict __stream);





extern int puts (const char *__s);






extern int ungetc (int __c, FILE *__stream);






extern size_t fread (void *__restrict __ptr, size_t __size,
       size_t __n, FILE *__restrict __stream) ;




extern size_t fwrite (const void *__restrict __ptr, size_t __size,
        size_t __n, FILE *__restrict __s);
# 678 "/usr/include/stdio.h" 3 4
extern size_t fread_unlocked (void *__restrict __ptr, size_t __size,
         size_t __n, FILE *__restrict __stream) ;
extern size_t fwrite_unlocked (const void *__restrict __ptr, size_t __size,
          size_t __n, FILE *__restrict __stream);







extern int fseek (FILE *__stream, long int __off, int __whence);




extern long int ftell (FILE *__stream) ;




extern void rewind (FILE *__stream);
# 712 "/usr/include/stdio.h" 3 4
extern int fseeko (FILE *__stream, __off_t __off, int __whence);




extern __off_t ftello (FILE *__stream) ;
# 736 "/usr/include/stdio.h" 3 4
extern int fgetpos (FILE *__restrict __stream, fpos_t *__restrict __pos);




extern int fsetpos (FILE *__stream, const fpos_t *__pos);
# 762 "/usr/include/stdio.h" 3 4
extern void clearerr (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__));

extern int feof (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;

extern int ferror (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;



extern void clearerr_unlocked (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__));
extern int feof_unlocked (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;
extern int ferror_unlocked (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;







extern void perror (const char *__s);




extern int fileno (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;




extern int fileno_unlocked (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;
# 799 "/usr/include/stdio.h" 3 4
extern FILE *popen (const char *__command, const char *__modes) ;





extern int pclose (FILE *__stream);





extern char *ctermid (char *__s) __attribute__ ((__nothrow__ , __leaf__));
# 839 "/usr/include/stdio.h" 3 4
extern void flockfile (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__));



extern int ftrylockfile (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__)) ;


extern void funlockfile (FILE *__stream) __attribute__ ((__nothrow__ , __leaf__));
# 857 "/usr/include/stdio.h" 3 4
extern int __uflow (FILE *);
extern int __overflow (FILE *, int);
# 874 "/usr/include/stdio.h" 3 4

# 2 "hello.c" 2


# 3 "hello.c"
int main() {
    printf("hello!");
}

```
3. 汇编
```bash
$ gcc -S hello.
```
查看生成内容

```bash

	.file	"hello.c"
	.text
	.section	.rodata
.LC0:
	.string	"hello!"
	.text
	.globl	main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	leaq	.LC0(%rip), %rax
	movq	%rax, %rdi
	movl	$0, %eax
	call	printf@PLT
	movl	$0, %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	main, .-main
	.ident	"GCC: (GNU) 11.1.0"
	.section	.note.GNU-stack,"",@progbits
```

4. 机器码

```bash
gcc -C hello.s
```
* file 查看
    ```bash
    hello.o: ELF 64-bit LSB relocatable, x86-64, version 1 (SYSV), not stripped
    ```

* objdump 查看
  ```bash
    hello.o:     file format elf64-x86-64
    hello.o
  ```

* nm 查看
  ```bash
                     U _GLOBAL_OFFSET_TABLE_
    0000000000000000 T main
                     U printf

  ```

* readelf
```bash
ELF Header: 
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              REL (Relocatable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x0
  Start of program headers:          0 (bytes into file)
  Start of section headers:          640 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           0 (bytes)
  Number of program headers:         0
  Size of section headers:           64 (bytes)
  Number of section headers:         14
  Section header string table index: 13

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .text             PROGBITS         0000000000000000  00000040
       000000000000001f  0000000000000000  AX       0     0     1
  [ 2] .rela.text        RELA             0000000000000000  000001c0
       0000000000000030  0000000000000018   I      11     1     8
  [ 3] .data             PROGBITS         0000000000000000  0000005f
       0000000000000000  0000000000000000  WA       0     0     1
  [ 4] .bss              NOBITS           0000000000000000  0000005f
       0000000000000000  0000000000000000  WA       0     0     1
  [ 5] .rodata           PROGBITS         0000000000000000  0000005f
       0000000000000007  0000000000000000   A       0     0     1
  [ 6] .comment          PROGBITS         0000000000000000  00000066
       0000000000000013  0000000000000001  MS       0     0     1
  [ 7] .note.GNU-stack   PROGBITS         0000000000000000  00000079
       0000000000000000  0000000000000000           0     0     1
  [ 8] .note.gnu.pr[...] NOTE             0000000000000000  00000080
       0000000000000030  0000000000000000   A       0     0     8
  [ 9] .eh_frame         PROGBITS         0000000000000000  000000b0
       0000000000000038  0000000000000000   A       0     0     8
  [10] .rela.eh_frame    RELA             0000000000000000  000001f0
       0000000000000018  0000000000000018   I      11     9     8
  [11] .symtab           SYMTAB           0000000000000000  000000e8
       00000000000000a8  0000000000000018          12     4     8
  [12] .strtab           STRTAB           0000000000000000  00000190
       000000000000002b  0000000000000000           0     0     1
  [13] .shstrtab         STRTAB           0000000000000000  00000208
       0000000000000074  0000000000000000           0     0     1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  l (large), p (processor specific)

There are no section groups in this file.

There are no program headers in this file.

There is no dynamic section in this file.

Relocation section '.rela.text' at offset 0x1c0 contains 2 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
000000000007  000300000002 R_X86_64_PC32     0000000000000000 .rodata - 4
000000000014  000600000004 R_X86_64_PLT32    0000000000000000 printf - 4

Relocation section '.rela.eh_frame' at offset 0x1f0 contains 1 entry:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
000000000020  000200000002 R_X86_64_PC32     0000000000000000 .text + 0

The decoding of unwind sections for machine type Advanced Micro Devices X86-64 is not currently supported.

Symbol table '.symtab' contains 7 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS hello.c
     2: 0000000000000000     0 SECTION LOCAL  DEFAULT    1 
     3: 0000000000000000     0 SECTION LOCAL  DEFAULT    5 
     4: 0000000000000000    31 FUNC    GLOBAL DEFAULT    1 main
     5: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND _GLOBAL_OFFSET_TABLE_
     6: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND printf

No version information found in this file.

Displaying notes found in: .note.gnu.property
  Owner                Data size 	Description
  GNU                  0x00000020	NT_GNU_PROPERTY_TYPE_0
      Properties: x86 ISA used: 
	x86 feature used: x86

```

5. 链接
```bash
gcc hello.o -o hello
```

* file 查看

```bash
hello: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=92f33896a3687559674a0d0f204f68984bfd8ee3, for GNU/Linux 4.4.0, not stripped
```
* readelf：
    ```bash
    ELF Header:
    Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
    Class:                             ELF64
    Data:                              2's complement, little endian
    Version:                           1 (current)
    OS/ABI:                            UNIX - System V
    ABI Version:                       0
    Type:                              DYN (Shared object file)
    Machine:                           Advanced Micro Devices X86-64
    Version:                           0x1
    Entry point address:               0x1040
    Start of program headers:          64 (bytes into file)
    Start of section headers:          14168 (bytes into file)
    Flags:                             0x0
    Size of this header:               64 (bytes)
    Size of program headers:           56 (bytes)
    Number of program headers:         13
    Size of section headers:           64 (bytes)
    Number of section headers:         30
    Section header string table index: 29

    Section Headers:
    [Nr] Name              Type             Address           Offset
        Size              EntSize          Flags  Link  Info  Align
    [ 0]                   NULL             0000000000000000  00000000
        0000000000000000  0000000000000000           0     0     0
    [ 1] .interp           PROGBITS         0000000000000318  00000318
        000000000000001c  0000000000000000   A       0     0     1
    [ 2] .note.gnu.pr[...] NOTE             0000000000000338  00000338
        0000000000000040  0000000000000000   A       0     0     8
    [ 3] .note.gnu.bu[...] NOTE             0000000000000378  00000378
        0000000000000024  0000000000000000   A       0     0     4
    [ 4] .note.ABI-tag     NOTE             000000000000039c  0000039c
        0000000000000020  0000000000000000   A       0     0     4
    [ 5] .gnu.hash         GNU_HASH         00000000000003c0  000003c0
        000000000000001c  0000000000000000   A       6     0     8
    [ 6] .dynsym           DYNSYM           00000000000003e0  000003e0
        00000000000000a8  0000000000000018   A       7     1     8
    [ 7] .dynstr           STRTAB           0000000000000488  00000488
        0000000000000084  0000000000000000   A       0     0     1
    [ 8] .gnu.version      VERSYM           000000000000050c  0000050c
        000000000000000e  0000000000000002   A       6     0     2
    [ 9] .gnu.version_r    VERNEED          0000000000000520  00000520
        0000000000000020  0000000000000000   A       7     1     8
    [10] .rela.dyn         RELA             0000000000000540  00000540
        00000000000000c0  0000000000000018   A       6     0     8
    [11] .rela.plt         RELA             0000000000000600  00000600
        0000000000000018  0000000000000018  AI       6    23     8
    [12] .init             PROGBITS         0000000000001000  00001000
        000000000000001b  0000000000000000  AX       0     0     4
    [13] .plt              PROGBITS         0000000000001020  00001020
        0000000000000020  0000000000000010  AX       0     0     16
    [14] .text             PROGBITS         0000000000001040  00001040
        0000000000000195  0000000000000000  AX       0     0     16
    [15] .fini             PROGBITS         00000000000011d8  000011d8
        000000000000000d  0000000000000000  AX       0     0     4
    [16] .rodata           PROGBITS         0000000000002000  00002000
        000000000000000b  0000000000000000   A       0     0     4
    [17] .eh_frame_hdr     PROGBITS         000000000000200c  0000200c
        0000000000000034  0000000000000000   A       0     0     4
    [18] .eh_frame         PROGBITS         0000000000002040  00002040
        00000000000000d8  0000000000000000   A       0     0     8
    [19] .init_array       INIT_ARRAY       0000000000003de8  00002de8
        0000000000000008  0000000000000008  WA       0     0     8
    [20] .fini_array       FINI_ARRAY       0000000000003df0  00002df0
        0000000000000008  0000000000000008  WA       0     0     8
    [21] .dynamic          DYNAMIC          0000000000003df8  00002df8
        00000000000001e0  0000000000000010  WA       7     0     8
    [22] .got              PROGBITS         0000000000003fd8  00002fd8
        0000000000000028  0000000000000008  WA       0     0     8
    [23] .got.plt          PROGBITS         0000000000004000  00003000
        0000000000000020  0000000000000008  WA       0     0     8
    [24] .data             PROGBITS         0000000000004020  00003020
        0000000000000010  0000000000000000  WA       0     0     8
    [25] .bss              NOBITS           0000000000004030  00003030
        0000000000000008  0000000000000000  WA       0     0     1
    [26] .comment          PROGBITS         0000000000000000  00003030
        0000000000000012  0000000000000001  MS       0     0     1
    [27] .symtab           SYMTAB           0000000000000000  00003048
        00000000000003d8  0000000000000018          28    22     8
    [28] .strtab           STRTAB           0000000000000000  00003420
        000000000000021b  0000000000000000           0     0     1
    [29] .shstrtab         STRTAB           0000000000000000  0000363b
        0000000000000116  0000000000000000           0     0     1
    Key to Flags:
    W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
    L (link order), O (extra OS processing required), G (group), T (TLS),
    C (compressed), x (unknown), o (OS specific), E (exclude),
    l (large), p (processor specific)

    There are no section groups in this file.

    Program Headers:
    Type           Offset             VirtAddr           PhysAddr
                    FileSiz            MemSiz              Flags  Align
    PHDR           0x0000000000000040 0x0000000000000040 0x0000000000000040
                    0x00000000000002d8 0x00000000000002d8  R      0x8
    INTERP         0x0000000000000318 0x0000000000000318 0x0000000000000318
                    0x000000000000001c 0x000000000000001c  R      0x1
        [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
    LOAD           0x0000000000000000 0x0000000000000000 0x0000000000000000
                    0x0000000000000618 0x0000000000000618  R      0x1000
    LOAD           0x0000000000001000 0x0000000000001000 0x0000000000001000
                    0x00000000000001e5 0x00000000000001e5  R E    0x1000
    LOAD           0x0000000000002000 0x0000000000002000 0x0000000000002000
                    0x0000000000000118 0x0000000000000118  R      0x1000
    LOAD           0x0000000000002de8 0x0000000000003de8 0x0000000000003de8
                    0x0000000000000248 0x0000000000000250  RW     0x1000
    DYNAMIC        0x0000000000002df8 0x0000000000003df8 0x0000000000003df8
                    0x00000000000001e0 0x00000000000001e0  RW     0x8
    NOTE           0x0000000000000338 0x0000000000000338 0x0000000000000338
                    0x0000000000000040 0x0000000000000040  R      0x8
    NOTE           0x0000000000000378 0x0000000000000378 0x0000000000000378
                    0x0000000000000044 0x0000000000000044  R      0x4
    GNU_PROPERTY   0x0000000000000338 0x0000000000000338 0x0000000000000338
                    0x0000000000000040 0x0000000000000040  R      0x8
    GNU_EH_FRAME   0x000000000000200c 0x000000000000200c 0x000000000000200c
                    0x0000000000000034 0x0000000000000034  R      0x4
    GNU_STACK      0x0000000000000000 0x0000000000000000 0x0000000000000000
                    0x0000000000000000 0x0000000000000000  RW     0x10
    GNU_RELRO      0x0000000000002de8 0x0000000000003de8 0x0000000000003de8
                    0x0000000000000218 0x0000000000000218  R      0x1

    Section to Segment mapping:
    Segment Sections...
    00     
    01     .interp 
    02     .interp .note.gnu.property .note.gnu.build-id .note.ABI-tag .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt 
    03     .init .plt .text .fini 
    04     .rodata .eh_frame_hdr .eh_frame 
    05     .init_array .fini_array .dynamic .got .got.plt .data .bss 
    06     .dynamic 
    07     .note.gnu.property 
    08     .note.gnu.build-id .note.ABI-tag 
    09     .note.gnu.property 
    10     .eh_frame_hdr 
    11     
    12     .init_array .fini_array .dynamic .got 

    Dynamic section at offset 0x2df8 contains 26 entries:
    Tag        Type                         Name/Value
    0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
    0x000000000000000c (INIT)               0x1000
    0x000000000000000d (FINI)               0x11d8
    0x0000000000000019 (INIT_ARRAY)         0x3de8
    0x000000000000001b (INIT_ARRAYSZ)       8 (bytes)
    0x000000000000001a (FINI_ARRAY)         0x3df0
    0x000000000000001c (FINI_ARRAYSZ)       8 (bytes)
    0x000000006ffffef5 (GNU_HASH)           0x3c0
    0x0000000000000005 (STRTAB)             0x488
    0x0000000000000006 (SYMTAB)             0x3e0
    0x000000000000000a (STRSZ)              132 (bytes)
    0x000000000000000b (SYMENT)             24 (bytes)
    0x0000000000000015 (DEBUG)              0x0
    0x0000000000000003 (PLTGOT)             0x4000
    0x0000000000000002 (PLTRELSZ)           24 (bytes)
    0x0000000000000014 (PLTREL)             RELA
    0x0000000000000017 (JMPREL)             0x600
    0x0000000000000007 (RELA)               0x540
    0x0000000000000008 (RELASZ)             192 (bytes)
    0x0000000000000009 (RELAENT)            24 (bytes)
    0x000000006ffffffb (FLAGS_1)            Flags: PIE
    0x000000006ffffffe (VERNEED)            0x520
    0x000000006fffffff (VERNEEDNUM)         1
    0x000000006ffffff0 (VERSYM)             0x50c
    0x000000006ffffff9 (RELACOUNT)          3
    0x0000000000000000 (NULL)               0x0

    Relocation section '.rela.dyn' at offset 0x540 contains 8 entries:
    Offset          Info           Type           Sym. Value    Sym. Name + Addend
    000000003de8  000000000008 R_X86_64_RELATIVE                    1130
    000000003df0  000000000008 R_X86_64_RELATIVE                    10e0
    000000004028  000000000008 R_X86_64_RELATIVE                    4028
    000000003fd8  000100000006 R_X86_64_GLOB_DAT 0000000000000000 _ITM_deregisterTM[...] + 0
    000000003fe0  000300000006 R_X86_64_GLOB_DAT 0000000000000000 __libc_start_main@GLIBC_2.2.5 + 0
    000000003fe8  000400000006 R_X86_64_GLOB_DAT 0000000000000000 __gmon_start__ + 0
    000000003ff0  000500000006 R_X86_64_GLOB_DAT 0000000000000000 _ITM_registerTMCl[...] + 0
    000000003ff8  000600000006 R_X86_64_GLOB_DAT 0000000000000000 __cxa_finalize@GLIBC_2.2.5 + 0

    Relocation section '.rela.plt' at offset 0x600 contains 1 entry:
    Offset          Info           Type           Sym. Value    Sym. Name + Addend
    000000004018  000200000007 R_X86_64_JUMP_SLO 0000000000000000 printf@GLIBC_2.2.5 + 0

    The decoding of unwind sections for machine type Advanced Micro Devices X86-64 is not currently supported.

    Symbol table '.dynsym' contains 7 entries:
    Num:    Value          Size Type    Bind   Vis      Ndx Name
        0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
        1: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND _ITM_deregisterT[...]
        2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND [...]@GLIBC_2.2.5 (2)
        3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND [...]@GLIBC_2.2.5 (2)
        4: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
        5: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND _ITM_registerTMC[...]
        6: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND [...]@GLIBC_2.2.5 (2)

    Symbol table '.symtab' contains 41 entries:
    Num:    Value          Size Type    Bind   Vis      Ndx Name
        0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
        1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS abi-note.c
        2: 000000000000039c    32 OBJECT  LOCAL  DEFAULT    4 __abi_tag
        3: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS init.c
        4: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
        5: 0000000000001070     0 FUNC    LOCAL  DEFAULT   14 deregister_tm_clones
        6: 00000000000010a0     0 FUNC    LOCAL  DEFAULT   14 register_tm_clones
        7: 00000000000010e0     0 FUNC    LOCAL  DEFAULT   14 __do_global_dtors_aux
        8: 0000000000004030     1 OBJECT  LOCAL  DEFAULT   25 completed.0
        9: 0000000000003df0     0 OBJECT  LOCAL  DEFAULT   20 __do_global_dtor[...]
        10: 0000000000001130     0 FUNC    LOCAL  DEFAULT   14 frame_dummy
        11: 0000000000003de8     0 OBJECT  LOCAL  DEFAULT   19 __frame_dummy_in[...]
        12: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS hello.c
        13: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
        14: 0000000000002114     0 OBJECT  LOCAL  DEFAULT   18 __FRAME_END__
        15: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS 
        16: 0000000000003df0     0 NOTYPE  LOCAL  DEFAULT   19 __init_array_end
        17: 0000000000003df8     0 OBJECT  LOCAL  DEFAULT   21 _DYNAMIC
        18: 0000000000003de8     0 NOTYPE  LOCAL  DEFAULT   19 __init_array_start
        19: 000000000000200c     0 NOTYPE  LOCAL  DEFAULT   17 __GNU_EH_FRAME_HDR
        20: 0000000000004000     0 OBJECT  LOCAL  DEFAULT   23 _GLOBAL_OFFSET_TABLE_
        21: 0000000000001000     0 FUNC    LOCAL  DEFAULT   12 _init
        22: 00000000000011d0     5 FUNC    GLOBAL DEFAULT   14 __libc_csu_fini
        23: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND _ITM_deregisterT[...]
        24: 0000000000004020     0 NOTYPE  WEAK   DEFAULT   24 data_start
        25: 0000000000004030     0 NOTYPE  GLOBAL DEFAULT   24 _edata
        26: 00000000000011d8     0 FUNC    GLOBAL HIDDEN    15 _fini
        27: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND printf@GLIBC_2.2.5
        28: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_mai[...]
        29: 0000000000004020     0 NOTYPE  GLOBAL DEFAULT   24 __data_start
        30: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
        31: 0000000000004028     0 OBJECT  GLOBAL HIDDEN    24 __dso_handle
        32: 0000000000002000     4 OBJECT  GLOBAL DEFAULT   16 _IO_stdin_used
        33: 0000000000001160   101 FUNC    GLOBAL DEFAULT   14 __libc_csu_init
        34: 0000000000004038     0 NOTYPE  GLOBAL DEFAULT   25 _end
        35: 0000000000001040    47 FUNC    GLOBAL DEFAULT   14 _start
        36: 0000000000004030     0 NOTYPE  GLOBAL DEFAULT   25 __bss_start
        37: 0000000000001139    31 FUNC    GLOBAL DEFAULT   14 main
        38: 0000000000004030     0 OBJECT  GLOBAL HIDDEN    24 __TMC_END__
        39: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND _ITM_registerTMC[...]
        40: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@G[...]

    Version symbols section '.gnu.version' contains 7 entries:
    Addr: 0x000000000000050c  Offset: 0x00050c  Link: 6 (.dynsym)
    000:   0 (*local*)       0 (*local*)       2 (GLIBC_2.2.5)   2 (GLIBC_2.2.5)
    004:   0 (*local*)       0 (*local*)       2 (GLIBC_2.2.5)

    Version needs section '.gnu.version_r' contains 1 entry:
    Addr: 0x0000000000000520  Offset: 0x000520  Link: 7 (.dynstr)
    000000: Version: 1  File: libc.so.6  Cnt: 1
    0x0010:   Name: GLIBC_2.2.5  Flags: none  Version: 2

    Displaying notes found in: .note.gnu.property
    Owner                Data size 	Description
    GNU                  0x00000030	NT_GNU_PROPERTY_TYPE_0
        Properties: x86 ISA needed: x86-64-baseline
        x86 feature used: x86
        x86 ISA used: 

    Displaying notes found in: .note.gnu.build-id
    Owner                Data size 	Description
    GNU                  0x00000014	NT_GNU_BUILD_ID (unique build ID bitstring)
        Build ID: 92f33896a3687559674a0d0f204f68984bfd8ee3

    Displaying notes found in: .note.ABI-tag
    Owner                Data size 	Description
    GNU                  0x00000010	NT_GNU_ABI_TAG (ABI version tag)
        OS: Linux, ABI: 4.4.0

    ```
* nm
    ```bash
    000000000000039c r __abi_tag
    0000000000004030 B __bss_start
    0000000000004030 b completed.0
                    w __cxa_finalize@GLIBC_2.2.5
    0000000000004020 D __data_start
    0000000000004020 W data_start
    0000000000001070 t deregister_tm_clones
    00000000000010e0 t __do_global_dtors_aux
    0000000000003df0 d __do_global_dtors_aux_fini_array_entry
    0000000000004028 D __dso_handle
    0000000000003df8 d _DYNAMIC
    0000000000004030 D _edata
    0000000000004038 B _end
    00000000000011d8 T _fini
    0000000000001130 t frame_dummy
    0000000000003de8 d __frame_dummy_init_array_entry
    0000000000002114 r __FRAME_END__
    0000000000004000 d _GLOBAL_OFFSET_TABLE_
                    w __gmon_start__
    000000000000200c r __GNU_EH_FRAME_HDR
    0000000000001000 t _init
    0000000000003df0 d __init_array_end
    0000000000003de8 d __init_array_start
    0000000000002000 R _IO_stdin_used
                    w _ITM_deregisterTMCloneTable
                    w _ITM_registerTMCloneTable
    00000000000011d0 T __libc_csu_fini
    0000000000001160 T __libc_csu_init
                    U __libc_start_main@GLIBC_2.2.5
    0000000000001139 T main
                    U printf@GLIBC_2.2.5
    00000000000010a0 t register_tm_clones
    0000000000001040 T _start
    0000000000004030 D __TMC_END__
    ```

## 格式简介

> ELF： executable and linkable format

一种用于可执行文件、目标代码、共享库和核心转储（`core dump`）的标准文件格式。
首次发布于一个名为 `System V Release 4（SVR4）`的 `Unix` 操作系统版本中关于应用二进制接口（ABI）的规范中，并且此后不久发布于工具接口标准（Tool Interface Standard），随后很快被不同 `Unix` 发行商所接受。1999 年，这种格式被 `86open` 项目选为 `x86` 架构处理器上的 `Unix` 和 类 Unix 系统的标准二进制文件格式。

按照设计，ELF 格式灵活性高、可扩展，并且跨平台。比如它支持不同的字节序和地址范围，所以它不会不兼容某一特别的 CPU 或指令架构。这也使得 ELF 格式能够被运行于众多不同平台的各种操作系统所广泛采纳。

每个 ELF 文件都由一个 ELF 首部和紧跟其后的文件数据部分组成。数据部分可以包含：

* 程序头表（Program header table）：
  描述 0 个或多个内存段信息
  > 内存段中包含了用于某个 ELF 文件运行时执行所需的信息，而片段中包含了用于链接和重定位的重要数据。
    整个文件中的任何一个字节至多只能属于一个片段，也就是说可能存在不属于任何片段的孤立字节。
* 分段头表（Section header table）：
  描述 0 段或多段链接与重定位需要的数据
* 程序头表与分段头表引用的数据，比如 `.text`, `.data`

程序表中包含指向其他分段的索引， 分段表中也是如此：

```text
----------------------------
|     ELF  header           |
|---------------------------|
|   Program header table    |-------|
|---------------------------|       |
|          .text            |<------|-------|
|---------------------------|       |       |
|          .rodata          |<------|-------|
|---------------------------|       |       |
|           ......          |<------|-------|
|---------------------------|       |       |
|           .data           |<------|-------|
|---------------------------|               |
|  Section header table     |---------------|
|---------------------------|
```

* `Linux-IA32` 下的 ELF 存储和对应到Linux 内核中的情况

```text
  0====>-----------------------------  ---|             --------------------------------------              
        |     ELF  header           |     |             |      Kernel Virtual           |  /| 1GB
        |                           |     |             |                               |   |/  
        |---------------------------|     |             |-------------------------------|<===== 0xC000 00000  
        |   Program header table    |     |             |     User Stack  (dynamic)     |  <-- 栈 
        |                           |     |             |                               |
        |---------------------------|     |             |-------------------------------|<===== %esp
        |          .init            |     | \           |            /|\                |
        |---------------------------|     |  \          |             |                 |
        |          .text            |     |   \         |            \|/                |
        |---------------------------|     |    \        |-------------------------------|
        |          .rodata          |     |     \       |        dynamic libs           | <-- 共享库区域
        |---------------------------|  ---|      |      |-------------------------------|
        |           .data           | ---|       |      |           /|\                 |
        |---------------------------|    |\      |      |            |                  |
        |           .bss            | ---| \     |      |            |                  |
        |---------------------------|       \    |      |-------------------------------|<===== brk
        |           .symtab         |       |    |      |          heap                 | <-- 堆： 由程序主动申请释放(malloc, new)
        |---------------------------|       |     \     |-------------------------------|
        |           .debug          |       |      ---->|        .data ,  .bss          | <-- 读写数据段
        |---------------------------|        \          |-------------------------------|             
        |           .line           |         \---->    |       .init, .text, .rodata   | <-- 只读代码段
        |---------------------------|                   |-------------------------------|<===== 0x0804 8000
        |           .data           |                   |                               |
        |---------------------------|                   |         not used yet          |
        |           .strtab         |                   |                               |
        |---------------------------|                   |-------------------------------|<===== 0 
                ELF 文件(磁盘)                               Linux 虚拟空间
```

#### sections

* header
    包括：我们字节标识信息， 文件类型(.O, exec, .so), 机器类型(IA-32, IA-64, Power-32)

* `.text`
  编译后的代码部分

* `.rodata`
  只读数据

* `.data`
  已初始化的全局变量

* `.bss`
  block started by symbol
  为初始化的全局变量, 仅仅作为占位符, 不占据任何实际磁盘空间。
  > 区分初始化和非初始化是为了提供空间效率

  因为C语言中已经规定: 未初始化的全局变量和局部静态变量的默认值为零。
  所以，将为初始化的变量和已经初始化的变量分开成两个段：
  * `.data` 中存放具体的初始值, 仅占有一定的磁盘空间
  * `.bss` 中仅说明变量将来执行时占用几个字节即可, 几乎不占用磁盘空间， 提高了执行效率

* '.symtab`
  存放函数名和全局变量(符号表)信息

* `.rel.text` & `.rel.data`
  `.text` & `.data`的重定位信息, 用于重新修改代码段中的指令的地址信 & 对被模块使用或定义的全局变量进行重定位的信息。
  在`.o`文件里面是需要的， 而实际的可执行文件里面已经重定位过了， 所以就不存在了。

* `.debug`
  调试符号表

* `strtab`
  包含`symtab` 和 `debug` 中符号和节名

#### 代码对应ELF

```cpp
#include <stdio.h>

int y = 100;                   // .data
int x;                         // .bss

void print() {
    printf("hello!");         // .text
}


int main() {                 // .text
    static int a = 1;        // .data
    static int b;            // .bss
    int c = 200, d;           
    print();
}


```
#### elf.h

通过 `man elf` 就可以获取elf 介绍的详细信息

* elf header

```c
#define EI_NIDENT 16

typedef struct {
    unsigned char e_ident[EI_NIDENT];
    uint16_t      e_type;
    uint16_t      e_machine;
    uint32_t      e_version;
    ElfN_Addr     e_entry;
    ElfN_Off      e_phoff;
    ElfN_Off      e_shoff;
    uint32_t      e_flags;
    uint16_t      e_ehsize;
    uint16_t      e_phentsize;
    uint16_t      e_phnum;
    uint16_t      e_shentsize;
    uint16_t      e_shnum;
    uint16_t      e_shstrndx;
} ElfN_Ehdr;

# N = 32 or 64
```
* Program header (Phdr)

```c
// 32
typedef struct {
    uint32_t   p_type;
    Elf32_Off  p_offset;
    Elf32_Addr p_vaddr;
    Elf32_Addr p_paddr;
    uint32_t   p_filesz;
    uint32_t   p_memsz;
    uint32_t   p_flags;
    uint32_t   p_align;
} Elf32_Phdr;

// 64
typedef struct {
    uint32_t   p_type;
    uint32_t   p_flags;
    Elf64_Off  p_offset;
    Elf64_Addr p_vaddr;
    Elf64_Addr p_paddr;
    uint64_t   p_filesz;
    uint64_t   p_memsz;
    uint64_t   p_align;
} Elf64_Phdr;

```

* Section header (Shdr)
```c
typedef struct {
    uint32_t   sh_name;
    uint32_t   sh_type;
    uint32_t   sh_flags;
    Elf32_Addr sh_addr;
    Elf32_Off  sh_offset;
    uint32_t   sh_size;
    uint32_t   sh_link;
    uint32_t   sh_info;
    uint32_t   sh_addralign;
    uint32_t   sh_entsize;
} Elf32_Shdr;

typedef struct {
    uint32_t   sh_name;
    uint32_t   sh_type;
    uint64_t   sh_flags;
    Elf64_Addr sh_addr;
    Elf64_Off  sh_offset;
    uint64_t   sh_size;
    uint32_t   sh_link;
    uint32_t   sh_info;
    uint64_t   sh_addralign;
    uint64_t   sh_entsize;
} Elf64_Shdr;

```
*  String and symbol tables
```bash
typedef struct {
    uint32_t      st_name;
    Elf32_Addr    st_value;
    uint32_t      st_size;
    unsigned char st_info;
    unsigned char st_other;
    uint16_t      st_shndx;
} Elf32_Sym;

typedef struct {
    uint32_t      st_name;
    unsigned char st_info;
    unsigned char st_other;
    uint16_t      st_shndx;
    Elf64_Addr    st_value;
    uint64_t      st_size;
} Elf64_Sym;

```

### 常用的工具

`GNU Binutils` 是用来处理许多格式的目标文件(包括elf文件)一整套的编程语言工具程序，包括：

* readelf
  显示elf文件

* objdump
  显示elf和object格式文件，解码elf文件中高级语言语句所对应的机器语言语句段落，汇编语言语句段落

* nm
  显示elf文件中变量名和地址 

* strings
  打印文件中的可打印字符的字符串。
  在开发软件的时候，各种文本/ASCII 信息会被添加到其中，比如打印信息、调试信息、帮助信息、错误等。只要这些信息都存在于二进制文件中，就可以用 `strings` 命令将其转储到屏幕上。

* ldd 
  打印共享对象依赖关系。
  对动态链接的二进制文件运行该命令会显示出所有依赖库和它们的路径。


