# MM VMA Merge/Split

## 1. vma_merge 合并

### 1.1 vma_merge
**文件**: `mm/vma.c:1200-1350`

```c
struct vm_area_struct *vma_merge(struct vma_iterator *vmi,
                                  struct mm_struct *mm,
                                  struct vm_area_struct *prev,
                                  unsigned long start, unsigned long end,
                                  unsigned long vm_flags,
                                  struct anon_vma *anon_vma,
                                  struct file *file,
                                  pgoff_t pgoff,
                                  struct mempolicy *policy,
                                  struct vm_userfaultfd_ctx ctx)
{
    struct vm_area_struct *vma;

    // 检查是否可以与前一个 VMA 合并
    if (prev) {
        vma = vma_merge_new_range(vmi, prev, start, end, vm_flags,
                                   anon_vma, file, pgoff, policy, ctx);
        if (vma)
            return vma;
    }

    // 检查是否可以与下一个 VMA 合并
    vma = vma_prev_limit(vmi, start, end);
    if (vma && vma_end(vma) == start)
        return vma_merge_next(vmi, prev, vma, start, end, vm_flags,
                             anon_vma, file, pgoff, policy, ctx);

    return NULL;
}
```

### 1.2 vma_merge_new_range
**文件**: `mm/vma.c:1100-1200`

```c
static struct vm_area_struct *
vma_merge_new_range(struct vma_iterator *vmi, struct vm_area_struct *prev,
                    unsigned long start, unsigned long end,
                    unsigned long vm_flags, struct anon_vma *anon_vma,
                    struct file *file, pgoff_t pgoff,
                    struct mempolicy *policy, struct vm_userfaultfd_ctx ctx)
{
    struct vm_area_struct *vma;
    struct vm_area_struct *next;

    // 获取下一个 VMA
    next = vma_next(vmi);
    if (!next)
        goto nomerge;

    // 检查能否合并的条件
    // 1. 标志兼容
    if (!vmflags_compatible(prev->vm_flags, next->vm_flags, vm_flags))
        goto nomerge;

    // 2. 区域连续
    if (prev && prev->vm_end != start)
        goto nomerge;

    // 3. 匿名/文件映射类型一致
    if ((prev && !vma_adjust_trans_huge(prev, start, end, prev->vm_end - prev->vm_start)) ||
        (next && !vma_adjust_trans_huge(next, start, end, next->vm_end - next->vm_start)))
        goto nomerge;

    // 4. 文件映射：文件相同，偏移连续
    if (file && next->vm_file == file &&
        next->vm_pgoff == pgoff + ((start - next->vm_start) >> PAGE_SHIFT)) {
        // 可以合并
        return vma_expand(next, start, end, prev);
    }

nomerge:
    return NULL;
}
```

### 1.3 vma_expand
**文件**: `mm/vma.c:900-1000`

```c
static struct vm_area_struct *
vma_expand(struct vm_area_struct *vma, unsigned long start,
           unsigned long end, struct vm_area_struct *prev)
{
    struct vm_area_struct *next = vma_next(vmi, vma);

    // 更新 VMA 范围
    vma->vm_start = start;
    vma->vm_end = end;

    // 如果有前后相邻的 VMA，解除链接
    if (prev)
        vma_detach(prev);
    if (next)
        vma_detach(next);

    // 重新链接
    if (prev)
        vma_attach(prev, vma);
    if (next)
        vma_attach(vma, next);

    // 更新 maple tree
    vmi_store(vmi, vma);

    // 更新统计
    vm_stat_account(mm, vma->vm_flags, vma->vm_end - vma->vm_start);

    return vma;
}
```

## 2. split_vma 分割

### 2.1 split_vma
**文件**: `mm/vma.c:1400-1500`

```c
int split_vma(struct vma_iterator *vmi, struct vm_area_struct *vma,
               unsigned long addr, int new_below)
{
    struct vm_area_struct *new;
    unsigned long old_end;

    if (addr < vma->vm_start || addr >= vma->vm_end)
        return -EINVAL;

    // 分配新的 VMA
    new = vm_area_alloc(vma->vm_mm);
    if (!new)
        return -ENOMEM;

    old_end = vma->vm_end;

    // 复制 VMA 属性
    *new = *vma;

    // 调整范围
    if (new_below) {
        new->vm_start = addr;
        new->vm_pgoff += (addr - vma->vm_start) >> PAGE_SHIFT;
    } else {
        new->vm_end = addr;
    }

    // 修改原始 VMA
    if (new_below) {
        vma->vm_end = addr;
    } else {
        vma->vm_start = addr;
        vma->vm_pgoff = new->vm_pgoff +
            (new->vm_end - addr) >> PAGE_SHIFT;
    }

    // 处理 anon_vma
    if (vma->anon_vma) {
        int ret = anon_vma_clone(new, vma, VMA_OP_SPLIT);
        if (ret) {
            vm_area_free(new);
            return ret;
        }
    }

    // 插入 maple tree
    vma_store(vmi, new);

    // 更新 vm_file 引用
    if (new->vm_file)
        get_file(new->vm_file);

    vm_stat_account(mm, new->vm_flags, new->vm_end - new->vm_start);

    return 0;
}
```

### 2.2 __split_vma
**文件**: `mm/vma.c:1350-1400`

```c
static int __split_vma(struct vma_iterator *vmi, struct vm_area_struct *vma,
                        unsigned long addr, int new_below)
{
    struct mm_struct *mm = vma->vm_mm;
    int ret;

    // 分割点必须对齐
    if (addr & ~PAGE_MASK)
        return -EINVAL;

    // 检查是否有足够的锁
    if (vma->vm_file)
        mapping_unmap_writable(vma->vm_file->f_mapping);

    ret = split_vma(vmi, vma, addr, new_below);

    if (vma->vm_file)
        mapping_map_writable(vma->vm_file->f_mapping);

    return ret;
}
```

## 3. vma_adjust 调整

### 3.1 vma_adjust
**文件**: `mm/vma.c:700-850`

```c
int vma_adjust(struct vm_area_struct *vma, unsigned long start,
               unsigned long end, pgoff_t pgoff, struct vm_area_struct *new)
{
    struct mm_struct *mm = vma->vm_mm;
    struct vm_area_struct *prev, *next;
    unsigned long old_end;
    long adjust_next;
    bool remove_next = false;

    // 计算调整量
    adjust_next = (new ? (new->vm_end - new->vm_start) : 0) -
                  (end - start);

    // 获取前后 VMA
    prev = vma_prev(vmi, start);
    next = vma_next(vmi, end);

    // 如果需要移除 next VMA
    if (next && end > next->vm_start) {
        if (end - next->vm_start >= next->vm_end - next->vm_start) {
            // 完全覆盖 next
            remove_next = true;
        } else {
            // 部分重叠
            return -ENOMEM;
        }
    }

    // 更新 VMA
    vma_start_write(vma);

    // 修改范围
    old_end = vma->vm_end;
    vma->vm_start = start;
    vma->vm_end = end;
    vma->vm_pgoff = pgoff;

    // 调整 maple tree
    vma_store(vmi, vma);

    // 处理 anon_vma
    if (vma->anon_vma)
        anon_vma_adjust(vma, start, end, adjust_next);

    // 处理文件映射
    if (vma->vm_file)
        vma_interval_tree_remove(vma, &vma->vm_file->f_mapping->i_mmap);

    // 处理下一个 VMA
    if (adjust_next) {
        next->vm_start += adjust_next;
        next->vm_pgoff += adjust_next >> PAGE_SHIFT;
        vma_store(vmi, next);
    }

    // 移除被覆盖的 VMA
    if (remove_next) {
        vma_remove(next);
        vm_area_free(next);
    }

    // 更新统计
    vm_stat_account(mm, vma->vm_flags, end - start - (old_end - vma->vm_end));

    return 0;
}
```

## 4. VMA 合并条件检查

### 4.1 vmflags_compatible
**文件**: `mm/vma.c:100-150`

```c
static bool vmflags_compatible(vm_flags_t vm1_flags, vm_flags_t vm2_flags,
                              vm_flags_t needed)
{
    // 检查基本标志
    if ((vm1_flags & needed) != (vm2_flags & needed))
        return false;

    // 检查互斥标志
    if ((vm1_flags & VM_SHARED) != (vm2_flags & VM_SHARED))
        return false;

    // 检查特殊标志
    if ((vm1_flags & VM_LOCKED) != (vm2_flags & VM_LOCKED))
        return false;

    if ((vm1_flags & VM_HUGEPAGE) != (vm2_flags & VM_HUGEPAGE))
        return false;

    return true;
}
```

### 4.2 vma_adjust_trans_huge
**文件**: `mm/vma.c:150-200`

```c
static bool vma_adjust_trans_huge(struct vm_area_struct *vma,
                                   unsigned long start, unsigned long end,
                                   unsigned long delta)
{
    unsigned long tokens;
    unsigned long next;

    // 检查是否支持 THP
    if (!vma->vm_file ||
        !vma->vm_file->f_mapping->a_ops->remap_pages)
        return false;

    // 检查地址是否对齐
    if (start & ~HPAGE_PMD_MASK)
        return false;

    next = vma->vm_end;
    if (next & ~HPAGE_PMD_MASK)
        return false;

    tokens = (end - start) >> HPAGE_PMD_SHIFT;
    if (tokens > HPAGE_PMD_NR)
        return false;

    return true;
}
```

## 5. anon_vma 分割/合并

### 5.1 anon_vma_clone
**文件**: `mm/rmap.c:500-550`

```c
int anon_vma_clone(struct vm_area_struct *vma, struct vm_area_struct *pvma,
                   enum vma_op op)
{
    struct anon_vma_chain *avc, *pavc;
    struct anon_vma *anon_vma;

    // 遍历父 VMA 的 anon_vma_chain
    list_for_each_entry(pavc, &pvma->anon_vma_chain, same_vma) {
        avc = anon_vma_chain_alloc(GFP_KERNEL);
        if (!avc)
            goto enomem;

        // 克隆 chain
        avc->vma = vma;
        avc->anon_vma = pavc->anon_vma;
        list_add(&avc->same_vma, &vma->anon_vma_chain);

        // 如果是 fork，更新引用计数
        if (op == VMA_OP_FORK) {
            anon_vma = avc->anon_vma;
            spin_lock(&anon_vma->rwsem);
            anon_vma->num_active_vmas++;
            spin_unlock(&anon_vma->rwsem);
        }
    }

    return 0;

enomem:
    // 清理已分配的 chain
    anon_vma_chain_free(vma);
    return -ENOMEM;
}
```

### 5.2 anon_vma_adjust
**文件**: `mm/rmap.c:550-600`

```c
void anon_vma_adjust(struct vm_area_struct *vma,
                     unsigned long start, unsigned long end,
                     long adjust_next)
{
    struct anon_vma_chain *avc;

    // 遍历所有关联的 anon_vma_chain
    list_for_each_entry(avc, &vma->anon_vma_chain, same_vma) {
        struct anon_vma *anon_vma = avc->anon_vma;
        unsigned long anon_start, anon_end;

        // 计算在此 VMA 范围内的 anon_vma 区间
        anon_start = max(start, vma->vm_start);
        anon_end = min(end, vma->vm_end);

        // 更新 anon_vma 区间树
        anon_vma_interval_tree_remove(avc, &anon_vma->rb_root);
        avc->rb_subtree_last = anon_end;
        anon_vma_interval_tree_insert(avc, &anon_vma->rb_root);
    }
}
```

## 6. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| vma_merge | mm/vma.c | 1200 |
| vma_merge_new_range | mm/vma.c | 1100 |
| vma_expand | mm/vma.c | 900 |
| split_vma | mm/vma.c | 1400 |
| __split_vma | mm/vma.c | 1350 |
| vma_adjust | mm/vma.c | 700 |
| vmflags_compatible | mm/vma.c | 100 |
| vma_adjust_trans_huge | mm/vma.c | 150 |
| anon_vma_clone | mm/rmap.c | 500 |
| anon_vma_adjust | mm/rmap.c | 550 |
