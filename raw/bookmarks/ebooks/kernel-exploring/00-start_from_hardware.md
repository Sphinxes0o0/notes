# 中断和异常

学习、适用内核，中断和异常是不能绕过的一大知识点。只可惜出道这么多年，一直都没有认真地潜心研究这部分的内容。那这次就从硬件开始。

## 从硬件开始 -- IDT

中断和异常的处理需要硬件的支持，知道了硬件可以说就是了解了一大半。而这部分的硬件在x86平台上就是熟知的IDT了。

[从IDT开始](/kernel-exploring/00-start_from_hardware/01-idt.md)

## 中断和异常的区别

中断和异常这两个词我想大家经常听到，但是这两者之间有什么区别呢？你能想到啥？那就听我慢慢道来吧～

[中断？异常？有什么区别](/kernel-exploring/00-start_from_hardware/02-difference.md)

## 插播--系统调用的实现

学习过程中突然想到以前学习的时候说系统调用是通过**int 0x80**来实现的，那就干脆找找系统调用是怎么处理的呗。

这不看不打紧，一看发现现在的系统调用实现采用了新的方式。所以在这里插播一下～

[系统调用的实现](/kernel-exploring/00-start_from_hardware/03-syscall.md)

## 异常处理

书归正传，看过了系统调用，现在继续回来看异常处理。

在这里我们只看看异常向量表是如何初始化，并关联到异常处理函数的。

[异常向量表的设置](/kernel-exploring/00-start_from_hardware/04-exception_vector_setup.md)

## 中断函数

接着我们来看看中断。当然我们同样暂时不看很多具体的细节，只是把中断向量表和中断函数串起来。能够对系统架构有一个大致的理解。

[中断向量和中断函数](/kernel-exploring/00-start_from_hardware/05-interrupt_handler.md)

## APIC

随着硬件的进步，中断控制器也从原始的8259A进化到了APCI。在这里我们也粗略的了解一下。

[APIC](/kernel-exploring/00-start_from_hardware/06-apic.md)

## 重要的中断处理

系统中有些中断处理比较特殊，我们也尝试了解一下。

### 时钟中断

时钟中断对整个系统有特殊的意义。比如调度和RCU，都和时钟中断有关联。

[时钟中断](/kernel-exploring/00-start_from_hardware/07-timer_interrupt.md)

### 软中断

本质来讲这部分已经不是中断了，而且和硬件没有耦合。之所以放在这里，是因为一来暂时没有别的地方放。二来在某些方面和中断还有关系，比如中断上下文。

嗯，那就先放在这里吧。如果那一天觉得不合适了，再移动。

[软中断](/kernel-exploring/00-start_from_hardware/08-softirq.md)

## 中断、软中断、抢占和多处理器

这也是一个无处安放的章节，因为这个topic其实有点大。Paul老人家还专门写过一本这方面的书--《并行编程》。

暂时我只看了点皮毛，不过有些概念觉得实在是太重要了。必须找个地方记录一下，否则下次来看又忘记了。

[中断、软中断、抢占和多处理器](/kernel-exploring/00-start_from_hardware/09-irq_softirq_preempt_and_smp.md)