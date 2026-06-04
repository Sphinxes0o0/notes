---
type: source
source-type: pdf
title: "Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF"
path: papers/Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf
size: 1854 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF

> Ingested from `papers/Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf` via `lit parse` on 2026-06-04.
> Source file: 1.81 MB.

## Page 1

Warping    Reality
Creating and countering
the next generation of
Linux rootkits using eBPF

Pat Hogan
@PathToFile

## Page 2

Overview @pathtofile

  ● What are Linux kernel rootkits
  ● Why writing and using rootkits is hard
  ● How eBPF solves these problems and more
  ● How to detect and prevent malicious eBPF usage

## Page 3

What are kernel rootkits?

## Page 4

Kernel Rootkits - Advantages    @pathtofile




 ● Attackers want to maintain access to
   compromised machines
   ○ Credentials change, vulnerabilities get
     patched, etc.


 ● Hooking syscall table = visibility and control
   ○ See all network traffic
   ○ Hide files and processes
   ○ Create root processes

## Page 5

  Kernel Rootkits - Risks    @pathtofile



   ● Small bugs can cause major problems
     ○ Crashing the kernel means crashing the
       system


   ● Any update to the kernel risks disaster

   ● Some environments block arbitrary kernel
modules (e.g. Amazon EKS)

## Page 6

 “How about we add
JavaScript-like capabilities to the
 Linux Kernel?”
 - Thomas Graf, Isovalent, 2020

## Page 7

What is eBPF?

## Page 8

eBPF    @pathtofile




 ●   eBPF (extended Berkeley Packet Filtering)

 ●   Experienced rapid growth in last ~2 years

 ●   eBPF allows you to create programmable trace
     points in the kernel

 ●   Programs can be attached to:
    ○  Network Interfaces
    ○  Kernel functions
    ○  User mode functions

 ●   eBPF programs are guaranteed to be:
    ○  Safe
    ○  Efficient
    ○   Portable

## Page 9

eBPF - Safe and Efficient    @pathtofile



                                                                  int handle_execve_enter(struct
 ●   Programs typically written in C or Rust                      trace_event_raw_sys_enter * ctx):
     ●    Has variables, loops, conditionals                      ; bpf_probe_read_user(&c, sizeof(c), ctx->args[0]);
                                                                    0: (79) r3 = *(u64 *)(r1 +16)
     ●    Can call a small number of helper functions               1: (bf) r6 = r10
                                                                    2: (07) r6 += -16
                                                                  ; bpf_probe_read_user(&c, sizeof(c), ctx->args[0]);
 ●   Compiled by LLVM or GCC into bpf bytecode                      3: (bf) r1 = r6
                                                                    4: (b7) r2 = 16
     ●    Architecture agnostic                                     5: (85) call bpf_probe_read_user#-66336
     ●      Kernel version agnostic                                 6: (b7) r1 = 29477
                                                                  ; bpf_printk("Execve: %s", c);
                                                                    7: (6b) *(u16 *)(r10 -24) = r1
                                                                    8: (18) r1 = 0x203a657663657845
SEC("tp/syscalls/sys_enter_execve")                                  10: (7b) *(u64 *)(r10 -32) = r1
int handle_execve_enter(struct trace_event_raw_sys_enter *ctx)       11: (b7) r1 = 0
                                                                     12: (73) *(u8 *)(r10 -22) = r1
{                                                                    13: (bf) r1 = r10
     char prog[TASK_COMM_LEN];                                    ;  14: (07) r1 += -32
     bpf_probe_read_user(&prog, sizeof(prog), ctx->args[0]);      ; bpf_printk("Execve: %s", c);
     bpf_printk("Execve: %s", prog);                                 15: (b7) r2 = 11
                                                                     16: (bf) r3 = r6
                                                                     17: (85) call bpf_trace_printk#-61248
     return 0;                                                    ; return 0;
}                                                                    18: (b7) r0 = 0
                                                                     19: (95) exit

## Page 10

eBPF - Safe and Efficient                                              @pathtofile

 ●     Sent to kernel via a user space loader           int main(int argc, char **argv) {
                                                            struct example_bpf *skel;
      ○  Only CAP_ADMIN or CAP_BPF*                         int err;
                                                            /* Open BPF application */
 ●     Kernel eBPF Verifier checks code isn’t:              skel = example_bpf__open();
                                                            if (!skel) {
      ○  Too big                                                   fprintf(stderr, "Failed to open BPF skeleton\n");
      ○  Too complex                                        }      return 1;
      ○  Reading invalid memory                             /* Load & verify BPF programs */
                                                            err = example_bpf__load(skel);
                                                            if (err) {
 ●     If code passes, it is compiled to native                    fprintf(stderr, "Failed to load and verify BPF skeleton\n");
       instructions using a JIT compiler                    }      goto cleanup;
      ○  Patches locations of helper functions and fields   /* Attach tracepoint handler */
                                                            err = example_bpf__attach(skel);
      ○  Enables portability across kernels                 if (err) {
                                                                   fprintf(stderr, "Failed to attach BPF skeleton\n");
 ●     Program is then attached to network or function      }      goto cleanup;
      ○  Run once per packer/function call                  printf("Successfully started!\n");
                                                            read_trace_pipe();
      ○  Stateless, but can use Maps to store data         cleanup:
                                                            example_bpf__destroy(skel);
                                                            return -err;
                                                           }

## Page 11

Using eBPF to
Warp Network Reality

## Page 12

eBPF - Warping Network Reality    @pathtofile

## Page 13

eBPF - Warping Network Reality    @pathtofile










     eBPF enables:                              Security observes:
  ●  Read and write packets pre-firewall     ●  Connection from internal IP to ssh
  ●  Routing packets across networks         ●  No active internet-facing connections
  ●  Altering source and destination
     IP and Ports

## Page 14

eBPF - Warping Network Reality    @pathtofile










     eBPF enables:                            Security observes:
  ●  Reading C2 packets then discarding    ●  Normal web connections
  ●  Hijacking existing connections        ●  Nothing unusual in netstat or tcpdump
  ●  Cloning packets to create new traffic
  ●  Can use UProbe to hook OpenSSL
     functions, read and write TLS

## Page 15

Using eBPF to
Warp Data Reality

## Page 16

eBPF - Warping Data Reality    @pathtofile

## Page 17

eBPF - Warping Data Reality    @pathtofile

## Page 18

eBPF - Warping Data Reality    @pathtofile

## Page 19

 eBPF - Warping Data Reality                              @pathtofile

     User space program                                   eBPF Program

int main() {                                         SEC("fexit/__x64_sys_read")
     // Open File                                    int BPF_PROG(read_exit, struct pt_regs *regs, long ret) {
     char filename[100] = "read_me";                  // 1. Read in data returned from kernel
     int fd = openat(AT_FDCWD, filename, O_RDWR);     char buffer[100];
                                                      bpf_probe_read_user(
     // Read data from file                                       &buffer, sizeof(buffer), PT_REGS_PARM2(regs)
     char buffer[100];                                );
     read(fd, buffer, sizeof(buffer));                // 2. Change data
     printf("Data: %s\n", buffer);                    const char *fake_data = "fake_data";
                                                      for (int i=0; i<sizeof(replace); i++) {
     // Close file                                      buffer[i] = fake_data[i];
     close(fd);                                       }
     return 0;                                        // 3. Overwrite
}                                                     bpf_probe_write_user(
                                                        PT_REGS_PARM2(regs), &buffer, sizeof(buffer)
                                                      );
                                                      return 0;
                                                     }

## Page 20

 eBPF - Warping Data Reality                              @pathtofile

     User space program                                   eBPF Program

int main() {                                         SEC("fexit/__x64_sys_read")
     // Open File                                    int BPF_PROG(read_exit, struct pt_regs *regs, long ret) {
     char filename[100] = "read_me";                  // 1. Read in data returned from kernel
     int fd = openat(AT_FDCWD, filename, O_RDWR);     char buffer[100];
                                                      bpf_probe_read_user(
     // Read data from file                                       &buffer, sizeof(buffer), PT_REGS_PARM2(regs)
     char buffer[100];                                );
     read(fd, buffer, sizeof(buffer));                // 2. Change data
     printf("Data: %s\n", buffer);                    const char *fake_data = "fake_data";
                                                      for (int i=0; i<sizeof(replace); i++) {
     // Close file                                      buffer[i] = fake_data[i];
     close(fd);                                       }
     return 0;                                        // 3. Overwrite
}                                                     bpf_probe_write_user(
                                                        PT_REGS_PARM2(regs), &buffer, sizeof(buffer)
                                                      );
                                                      return 0;
                                                     }

## Page 21

 eBPF - Warping Data Reality                              @pathtofile

     User space program                                   eBPF Program

int main() {                                         SEC("fexit/__x64_sys_read")
     // Open File                                    int BPF_PROG(read_exit, struct pt_regs *regs, long ret) {
     char filename[100] = "read_me";                  // 1. Read in data returned from kernel
     int fd = openat(AT_FDCWD, filename, O_RDWR);     char buffer[100];
                                                      bpf_probe_read_user(
     // Read data from file                                       &buffer, sizeof(buffer), PT_REGS_PARM2(regs)
     char buffer[100];                                );
     read(fd, buffer, sizeof(buffer));                // 2. Change data
     printf("Data: %s\n", buffer);                    const char *fake_data = "fake_data";
                                                      for (int i=0; i<sizeof(replace); i++) {
     // Close file                                      buffer[i] = fake_data[i];
     close(fd);                                       }
     return 0;                                        // 3. Overwrite
}                                                     bpf_probe_write_user(
                                                        PT_REGS_PARM2(regs), &buffer, sizeof(buffer)
                                                      );
                                                      return 0;
                                                     }

## Page 22

eBPF - Warping Data Reality                                                @pathtofile

bpf_probe_write_user                                                  SEC("fmod_ret/__x64_sys_write")
                                                                      int BPF_PROG(fake_write, struct pt_regs *regs)
 ●     Any user space buffer, pointer, or string can be overwritten   {
 ●     E.g. execve, connect, netlink data, etc.                        // Get expected write amount
                                                                       u32 count = PT_REGS_PARM3(regs);
fmod_ret programs
 ●     Special type of eBPF programs to override function calls        // Overwrite return
 ●     Only some kernel functions, all syscalls                        return count;
 ●     Doesn’t call function, instead return error or fake result     }
 ●     Most software silently fails (sshd, rsyslogd, etc.)

bpf_send_signal                                                       SEC("fentry/__x64_sys_openat")
                                                                      int BPF_PROG(bpf_dos, struct pt_regs *regs)
 ●     eBPF helper function                                           {
 ●     Raises a signal on current thread                               // Kill any program that attempts to open a file
 ●     Signal SIGKILL unstoppable, kills entire process                bpf_send_signal(SIGKILL);

                                                                       return 0;
                                                                      }

## Page 23

eBPF - Warping Data Reality                    @pathtofile

                                           SEC("fexit/__x64_sys_read")
 ●   Can programmatically determine when   int BPF_PROG(read_exit, struct pt_regs *regs, long ret) {
     to affect calls                       // Check Process ID
 ●   Can filter based on:                  int pid = bpf_get_current_pid_tgid() >> 32;
    ●   Process ID                         // Check Program name
    ●   Process name                       char comm[TASK_COMM_LEN];
    ●   User ID                            bpf_get_current_comm(&comm, sizeof(comm);
    ●   Function arguments                 // Check user ID
    ●   Function return                    int uid = (int)bpf_get_current_uid_gid();
    ●   Time since boot
    ●   Previous activity                  // Check function argument
    ●   ...                                char data[100];
                                           bpf_probe_read_user(&data, sizeof(data), PT_REGS_PARM2(regs));

                                           // Check return Value
                                           if (ret != 0) { /* ...     */ };

                                           return 0;
                                          }

## Page 24

eBPF - Warping Data Reality    @pathtofile


 eBPF enables
  ●  Bypassing MFA by faking pam.d files
  ●  Enabling access using fake
     credentials


 Security observes
  ●  cat, vim, etc. only see real data without
     fake user

## Page 25

Demo Time

## Page 26

Other features,
Limitations

## Page 27

eBPF - Other features    @pathtofile


Running on network hardware
 ● eBPF can run outside the OS on the network card
 ● Dependent on card model
 ● Able to alter packets after auditing from OS


Programs can persist after loader exit
 ●   Some programs can be pinned to
     /sys/fs/bpf/
 ●   Fentry, Fexit programs
 ●   If pinned, loader not longer required
 ●   Otherwise loader needs to continue to run
 ●   Reduces detectable footprint


Chaining eBPF programs together
 ●   bpf_tail_call
 ●   Increases complexity
 ●   eBPF Maps used to store state between calls

## Page 28

eBPF - Limitations    @pathtofile



Race conditions
 ●  If usermode process runs too quickly, tampering fails
 ●  Process could race on another thread to discover/defeat tampering

No persistence across reboots
 ●  Programs need to be re-loaded after every reboot

Cannot write to kernel memory
 ●  Not able to alter kernel memory
 ●  Kernel security products (e.g. AuditD) unaffected
 ●  Kernel raises warning when ‘bpf_probe_write_user’ is used
 ●  However, can tamper with user mode controllers, log readers, network traffic, etc.

## Page 29

Detections and
Preventions

## Page 30

eBPF - File Detections    @pathtofile



 ●  Look for files that contain eBPF
    programs



 ●  Easy if programs compiled using
    LLVM + LibBPF
    ○  But not the only way to load
       eBPF Programs



 ●  If using bpftool + libbpf,
    ELF baked into loader .rodata

## Page 31

eBPF - File Detections    @pathtofile



 ●  Look for files that contain eBPF
    programs



 ●  Easy if programs compiled using
    LLVM + LibBPF
    ○  But not the only way to load
       eBPF Programs



 ●  If using bpftool + libbpf,
    ELF baked into loader .rodata

## Page 32

eBPF - File Detections    @pathtofile


  ●  Look for programs calling bpf_probe_write_user
  ●  BPF Bytecode:
    On Disk:        85 00 00 00 24 00 00 00
    In kernel:      85 00 00 00 40 FE FE FF

  ● Native bytecode:

    In Kernel:      callq 0xffff....

## Page 33

eBPF - Process Detections    @pathtofile



 Process Monitoring                                  SEC("tp/syscalls/sys_enter_bpf")
 ●  Monitor all ‘bpf’ syscalls                       int bpf_dos(struct trace_event_raw_sys_enter *ctx)
                                                     {
   ○  Only trusted programs should be using eBPF      // Get current program filename
   ○  Can use eBPF to monitor itself                  char comm[TASK_COMM_LEN];
                                                      bpf_get_current_comm(&comm, sizeof(comm));

 ●  Can use eBPF to extract program bytecode during   // Check program name
    loading                                           char comm_check[TASK_COMM_LEN] = "bpftool";
                                                      for (int i = 0; i < TASK_COMM_LEN; i++) {
                                                       if (prog_name[i] != comm_check[i]) {
                                                        // Program name doesn't match
                                                        // kill process
                                                        bpf_send_signal(SIGKILL);
                                                        return 0;
                                                       }
                                                      }
                                                      // bpftool is ok to run
                                                      return 0;
                                                     }

## Page 34

eBPF - Memory Detections    @pathtofile



 ●  Volatility planning to release new memory scanning plugins
 ●  Volatility works on live and offline memory dumps

## Page 35

eBPF - Preventions    @pathtofile



 ● eBPF can be disabled
   ○  Requires re-building kernel
   ○  Not always an option (e.g. managed environments)



 ● eBPF community is discussing how to sign eBPF programs
   ○  Signing can prevent unauthorised eBPF usage
   ○  Difficult due to JIT compilation
   ○  When implemented, it impact how eBPF can be used

## Page 36

What else can eBPF do?

## Page 37

eBPF - Windows    @pathtofile



 ●  eBPF is on Windows now

 ●  Currently only network routing

 ●  Future plans for function hooks

 ●  Writing to user memory not discussed

 ●  But the future is interesting!








    https://cloudblogs.microsoft.com/opensource/2021/05/10/making-ebpf-work-on-windows/

## Page 38

eBPF - Anti-Anti-Sandboxing    @pathtofile



 ● eBPF a great tool to defeat Anti-Sandbox and Anti-RE
 ● Doesn’t require attaching to processes
 ● Can fake uptime, file contents, MAC Address, DNS responses, etc.
 ● Examples of Anti-Sandbox techniques:










  https://www.trustedsec.com/blog/enumerating-anti-sandboxing-techniques/

## Page 39

eBPF - Bad-BPF    @pathtofile


  ●  https://github.com/pathtofile/bad-bpf
  ●  Collection of eBPF programs and loaders
  ●  Lots of comments and details on how they work
  ●  Examples of filtering based on PID and process name

    Bpf-Dos:                                                  Sudo-Add:
    Kills any program trying to use eBPF                      Adds a user to sudoers list

    Exec-Hijack:                                              TCP-Reroute:
    Hijacks calls to execve to launch a different program     Route TCP traffic from magic source port across NICs

    Pid-Hide:                                                 Text-Replace:
    Hides processes from tools like ‘ps’                      Replaces arbitrary text in arbitrary files.
                                                             - Add users to /etc/passwd
                                                             - Hide kernel modules from ‘lsmod’
                                                             - Fake MAC Address, etc.

## Page 40

Conclusion

## Page 41

 eBPF - Conclusion    @pathtofile




   ●   Using Kernel Rootkits can be super risky for an attacker
   ●   eBPF removes this risk, making it possible to run safe, portable, rootkits
   ●   Detection and prevention can be difficult without kernel mode security

Links:
   ●   Code Samples:             https://github.com/pathtofile/bad-bpf
   ●   Docs and blogs:           https://blog.tofile.dev/categories/#ebpf

   ●   eBPF Community Website:   https://ebpf.io
   ●   eBPF Community Slack:     https://ebpf.io/slack
   ●   eBPF Technical Guides:    https://docs.cilium.io/en/v1.9/bpf/#bpf-guide
                                 https://github.com/iovisor/bpf-docs/blob/master/eBPF.md
   ●   Other eBPF talks:         DEF CON 27: Jeff Dileo - Evil eBPF
                                 DEF CON 29: Guillaume Fournier - eBPF, I thought we were friends!
                                 InfoQ 2020:Thomas Graf - Rethinking the Linux Kernel
   ●   Mega thanks               Cory, Maybe, family

## Page 42

     @pathtofile

Questions?

Website:
https://path.tofile.dev

GitHub, Slack, Twitter:
@PathToFile

Email:
path[at]tofile[dot]dev

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[papers/Creating_and_countering_the_next_generation_of_Linux_rootkits_using_eBPF.pdf]]`
