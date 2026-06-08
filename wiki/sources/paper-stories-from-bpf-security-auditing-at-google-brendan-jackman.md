---
type: source
source-type: paper
title: "Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman"
path: papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf
source-md5: c2a7a7d5af16c050502d4f17353e569b
size: 748 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
created: 2026-06-04
tags: []

---

# Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman

> Ingested from `papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf` via `lit parse` on 2026-06-04.
> Source file: 0.73 MB.

## Page 1

Proprietary + Confidential



Stories from BPF security
auditing at Google




Brendan Jackman

## Page 2

Agenda    Proprietary + Confidential




●  History/refresher: KRSI

●  BPF Atomics

●  Ringbuffers

●  What’s next?

## Page 3

Proprietary + Confidential




Refresher: KRSI

## Page 4

    Detection & Response w/ Telemetry    Proprietary + Confidential



    Security
    telemetry
    agent



         Various      Clever      Clever
          Linux      Software    Security
        Computers    Pipeline    Engineers
(Google’s machines - not
    your Chromebook!)

## Page 5

Security telemetry on Linux: our journey    Proprietary + Confidential





●   Audit is not flexible or fast enough

●   Kernel module was awful to maintain

●   Turned to BPF, but we often struggled to find simple places to attach our programs

●   The BPF LSM was born.

●   LSMs get a semantic (internal) API for security information

●   Designed for enforcement, and now we use them for audit too.

## Page 6

Proprietary + Confidential




BPF Atomics

## Page 7

Proprietary + Confidential

BPF programs are
concurrent

## Page 8

     Proprietary + Confidential
So how do you
generate a     per-CPU arrays…
globally-unique
integer?      bpf_spin_lock…

## Page 9

At the BPF office hours…        Proprietary + Confidential

                     Atomics
drake_no.png        helpers?
    Atomics
drake_yes.png      instructions!

## Page 10

Proprietary + Confidential

## Page 11

Proprietary + Confidential





struct bpf_insn {
  __u8 code;       /* opcode */
  __u8 dst_reg:4;  /* dest register */
  __u8 src_reg:4;  /* source register */
  __s16 off;       /* signed offset */
  __s32 imm;       /* signed immediate constant */
};

## Page 12

         Old                                              New              Proprietary + Confidential
                                                                           Proprietary + Confidential

     representation                                   representation

struct bpf_insn i = {                                struct bpf_insn i = {
     .code = BPF_STX | BPF_XADD | BPF_DW,             .code = BPF_STX | BPF_ATOMIC | BPF_DW,
     .imm = 0, // otherwise verifier rejects insn     .imm = BPF_ADD,
     .dst_reg = BPF_REG_0,                            .dst_reg = BPF_REG_0,
     .src_reg = BPF_REG_1,                            .src_reg = BPF_REG_1,
}                                                    }

         Same bit-representation!

         New instructions


struct bpf_insn i = {                        struct bpf_insn i = {                        struct bpf_insn i = {
     .code = BPF_STX | BPF_ATOMIC | BPF_DW,       .code = BPF_STX | BPF_ATOMIC | BPF_DW,   .code = BPF_STX | BPF_ATOMIC | BPF_DW,
     .imm = BPF_ADD | BPF_FETCH,                  .imm = BPF_OR,                           .imm = BPF_XOR | BPF_FETCH,
     .dst_reg = BPF_REG_0,                        .dst_reg = BPF_REG_0,                    .dst_reg = BPF_REG_0,
     .src_reg = BPF_REG_1,                        .src_reg = BPF_REG_1,                    .src_reg = BPF_REG_1,
}                                            }                                            }

## Page 13

Proprietary + Confidential




Ringbuffers

## Page 14

Ring buffers: perf buffer vs BPF ringbuf    Proprietary + Confidential




Userspace agent

Userspace agent

Reordering!


                        Shallow    Deep
                        (memory    (memory
                   inefficient)    efficient)

CPU0 CPU1 CPU2 CPU3
                       (lock-free)



                   CPU0 CPU0 CPU0 CPU0



Perf Buffer enforces one-ring-per-CPU    BPF ringbuf gives flexibility to make these tradeoffs as you desire

## Page 15

    Ring buffers: promises    Proprietary + Confidential



execution
  argv

    env
execution     Outputting all data at once means that all is lost if the
  argv
   env        ringbuf is full

execution
  argv

    env

## Page 16

Ring buffers: promises    Proprietary + Confidential



execution

argv        Promise system:
env

execution    ● Don’t lose the whole event if ringbuf is full

argv
env          ● This also lets us defer producing data until later


execution

argv


env

## Page 17

Ring buffers: chunking               Proprietary + Confidential

execution
argv chunk     small,
0              fixed-size
               chunks         ●  Verifier likes to know buffer sizes in advance
argv chunk1     large,
                variable-sized
argv chunk2     data          ●  But allocating max-possible size is bad
(padding)

                              ●  Break down large data into fixed-size chunks

## Page 18

    Proprietary + Confidential

BPF Across
Multiple Kernel
Versions

## Page 19

Kernel Diversity    Proprietary + Confidential


Various kernel versions… only one userspace binary.

 How do we do “feature negotiation?”

## Page 20

    Proprietary + Confidential
If your program
uses unsupported
features, the
verifier rejects it.

## Page 21

    Linear program fallback    Proprietary + Confidential










Most feature-complete version    Most widely-supported version
         of the prog                      of the prog

## Page 22

    Top tip: field renames                             Proprietary + Confidential

                    SEC("lsm/something")           SEC("lsm/something")
                    int BPF_PROG(something *s)     int BPF_PROG(something *s)
                    {                              {
                         if (s->new_field > 3)    if (s->old_field > 3)
return 1;                                               return 1;
    drake_no.png         return 0;                  return 0;
                    }                              }


                     SEC("lsm/something")
                     int BPF_PROG(something *s)
                     {
                          int field = 0;

                          if (bpf_core_field_exists(s->new_field))
                              field = s->new_field;
                          else
    drake_yes.png             field = s->old_field;

                          if (s->new_field > 3)
                              return 1;
                          return 0;
                         }

## Page 23

Proprietary + Confidential




What’s next?

## Page 24

What’s next?    Proprietary + Confidential



 ●  DNS auditing

 ●  Enforcement with KRSI

 ●  Less kernel implementation details

## Page 25

Proprietary + Confidential









Thank You







The Google

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[papers/Stories_from_BPF_Security_Auditing_at_Google_-_Brendan_Jackman.pdf]]`
