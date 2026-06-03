# 透明大页的玄机

虚拟内存管理中有个常用，非常有意思，但是知道名字但是不知道是怎么运作的机制--透明大页(Transparent Huge Page)。

之前我对这个东西也不是很理解，而且还经常和另一个概念混淆--hugetlb。这两个都是利用了页表中"大页"表项，减少tlb的失误进而提高内存访问速度。而两者不同的是，相对hugetlb， THP更加灵活，当然也更加复杂。

系统中如何使用，可以参考官方[文档](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/admin-guide/mm/transhuge.rst)。

## 相同之处

THP和hugetlb相同之处，或者说和其他虚拟内存的相同之处在于在缺页中断中的处理流程几乎是一样的。

```
handle_mm_fault()
    hugetlb_fault
    __handle_mm_fault
        create_huge_pmd()
        do_huge_pmd_numa_page
        wp_huge_pmd
```

同样都是从handle\_mm\_fault()进来，hugetlb有专门的处理方法，剩下的就走到\_\_handle\_mm\_fault()。

在\_\_handle\_mm\_fault函数中会逐级查询，并按照不同情况进行处理。比如如果pmd为空，且支持THP，那么就会调用create\_huge\_pmd()来创建。或者是在COW的情况下，就会调用wp\_huge\_pmd()进行处理。

## 不同之处

相同之处平平无奇，关键还是在于不同之处。所谓透明，其实就是比hugetlb多了一些灵活性。在必要的时候可以拆分页表或者拆分大页本身。

目前理解上，THP的特别之处在与：

* [分配](/kernel-exploring/nei-cun-guan-li/00-index/04-thp/12-thp_alloc.md)
* [合并](/kernel-exploring/nei-cun-guan-li/00-index/04-thp/11-khugepaged.md)
* [拆分](/kernel-exploring/nei-cun-guan-li/00-index/04-thp/13-thp_split.md)