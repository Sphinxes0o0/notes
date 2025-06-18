# CPP STL

## STL 容器

|        容器        |    底层数据结构   |                         时间复杂度                        | 有无序 | 可不可重复 |                                     其他                                       |
|:------------------:|:-----------------:|:---------------------------------------------------------:|:------:|:----------:|:----------------------------------------------------------------------------:|
| array              | 数组              | 随机读改 O(1)                                             | 无序   | 可重复     | 支持随机访问                                                                 |
| vector             | 数组              | 随机读改、尾部插入、尾部删除 O(1) 头部插入、头部删除 O(n) | 无序   | 可重复     | 支持随机访问                                                                    |
| deque              | 双端队列          | 头尾插入、头尾删除 O(1)                                   | 无序   | 可重复     | 一个中央控制器 + 多个缓冲区，支持首尾快速增删，支持随机访问                       |
| forward_list       | 单向链表          | 插入、删除 O(1)                                           | 无序   | 可重复     | 不支持随机访问                                                               |
| list               | 双向链表          | 插入、删除 O(1)                                           | 无序   | 可重复     | 不支持随机访问                                                               |
| stack              | deque / list      | 顶部插入、顶部删除 O(1)                                   | 无序   | 可重复     | deque 或 list 封闭头端开口，不用 vector 的原因应该是容量大小有限制，扩容耗时     |
| queue              | deque / list      | 尾部插入、头部删除 O(1)                                   | 无序   | 可重复     | deque 或 list 封闭头端开口，不用 vector 的原因应该是容量大小有限制，扩容耗时     |
| priority_queue     | vector + max-heap | 插入、删除 O(log2n)                                       | 有序   | 可重复     | vector容器+heap处理规则                                                      |
| set                | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 不可重复   |                                                                              |
| multiset           | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 可重复     |                                                                              |
| map                | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 不可重复   |                                                                              |
| multimap           | 红黑树            | 插入、删除、查找 O(log2n)                                 | 有序   | 可重复     |                                                                              |
| unordered_set      | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 不可重复   |                                                                              |
| unordered_multiset | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 可重复     |                                                                              |
| unordered_map      | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 不可重复   |                                                                              |
| unordered_multimap | 哈希表            | 插入、删除、查找 O(1) 最差 O(n)                           | 无序   | 可重复     |                                                                              |


### array

#### 函数一览： 

|             方法             |     分类   |                                      含义                                       |
|:----------------------------:|:---------:|:------------------------------------------------------------------------------:|
| begin                        | iterators |  返回指向数组容器中第一个元素的迭代器                                               |
| end                          | iterators |  返回指向数组容器中最后一个元素之后的理论元素的迭代器                                 |
| rbegin                       | iterators |  返回指向数组容器中最后一个元素的反向迭代器                                          |
| rend                         | iterators |  返回一个反向迭代器，指向数组中第一个元素之前的理论元素                               |
| cbegin                       | iterators |  返回指向数组容器中第一个元素的常量迭代器(const_iterator)                          |
| cend                         | iterators |  返回指向数组容器中最后一个元素之后的理论元素的常量迭代器(const_iterator)           |
| crbegin                      | iterators |  返回指向数组容器中最后一个元素的常量反向迭代器(const_reverse_iterator)            |
| crend                        | iterators |  返回指向数组中第一个元素之前的理论元素的常量反向迭代器(const_reverse_iterator)     |
| size                         | capacity  |  返回数组容器中元素的数量                                                          |
| max_size                     | capacity  |  返回数组容器可容纳的最大元素数                                                    |
| empty                        | capacity  |  返回一个布尔值，指示数组容器是否为空                                               |
| operator[]                   | element access |  返回容器中第 n(参数)个位置的元素的引用                                      |
| at                           | element access |  返回容器中第 n(参数)个位置的元素的引用                                      |
| front                        | element access |  返回对容器中第一个元素的引用                                                 |
| back                         | element access |  返回对容器中最后一个元素的引用                                               |
| data                         | element access |  返回指向容器中第一个元素的指针                                               |
| fill                         | element access |  用 val(参数)填充数组所有元素                                                |
| swap                         | element access |  通过 x (参数)的内容交换数组的内容                                            |
| get(array)                   | element access |  形如 std::get<0>(myarray)；传入一个数组容器，返回指定位置元素的引用           |
| relational operators (array) | element access |  形如 arrayA > arrayB；依此比较数组每个元素的大小关系                         |

#### 源码实现

```cpp
Class template std::array
namespace std
{
    template<class T, size_t N>
    struct array
    {
        // types
        using value_type             = T;
        using pointer                = T*;
        using const_pointer          = const T*;
        using reference              = T&;
        using const_reference        = const T&;
        using size_type              = size_t;
        using difference_type        = ptrdiff_t;
        using iterator               = /* implementation-defined */;
        using const_iterator         = /* implementation-defined */;
        using reverse_iterator       = std::reverse_iterator<iterator>;
        using const_reverse_iterator = std::reverse_iterator<const_iterator>;
 
        // no explicit construct/copy/destroy for aggregate type
 
        constexpr void fill(const T& u);
        constexpr void swap(array&) noexcept(is_nothrow_swappable_v<T>);
 
        // iterators
        constexpr iterator               begin() noexcept;
        constexpr const_iterator         begin() const noexcept;
        constexpr iterator               end() noexcept;
        constexpr const_iterator         end() const noexcept;
 
        constexpr reverse_iterator       rbegin() noexcept;
        constexpr const_reverse_iterator rbegin() const noexcept;
        constexpr reverse_iterator       rend() noexcept;
        constexpr const_reverse_iterator rend() const noexcept;
 
        constexpr const_iterator         cbegin() const noexcept;
        constexpr const_iterator         cend() const noexcept;
        constexpr const_reverse_iterator crbegin() const noexcept;
        constexpr const_reverse_iterator crend() const noexcept;
 
        // capacity
        [[nodiscard]] constexpr bool empty() const noexcept;
        constexpr size_type size() const noexcept;
        constexpr size_type max_size() const noexcept;
 
        // element access
        constexpr reference       operator[](size_type n);
        constexpr const_reference operator[](size_type n) const;
        constexpr reference       at(size_type n);
        constexpr const_reference at(size_type n) const;
        constexpr reference       front();
        constexpr const_reference front() const;
        constexpr reference       back();
        constexpr const_reference back() const;
 
        constexpr T*       data() noexcept;
        constexpr const T* data() const noexcept;
    };
 
    template<class T, class... U>
        array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```


