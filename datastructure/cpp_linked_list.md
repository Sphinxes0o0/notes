---
title: C++ 实现单向链表
---

# C++ 实现单向链表

链表是最常用的基础数据结构之一，与数组相比，链表在插入和删除操作上具有天然的优势，因为只需要修改指针指向，无需移动大量元素。本文详细介绍如何在 C++ 中实现一个完整的单向链表，包含哨兵节点设计、核心操作封装以及复杂度分析。

## 1. 链表结构设计

### 1.1 节点结构体定义

单向链表的基本单元是节点（Node），每个节点包含两个部分：

- **数据域（val）**：存储节点的值
- **指针域（next）**：指向下一个节点的指针

```cpp
struct ListNode {
    int val;                // 节点存储的值
    ListNode* next;         // 指向下一个节点的指针

    ListNode(int x) : val(x), next(nullptr) {}  // 构造函数
};
```

示意图：

```
+-----+     +-----+     +-----+     +-----+
|  1  | --> |  2  | --> |  3  | --> |  4  | --> NULL
+-----+     +-----+     +-----+     +-----+
  val=1       val=2       val=3       val=4
  next        next        next        next
```

### 1.2 哨兵节点的作用

哨兵节点（Sentinel Node）是一种特殊的 dummy 节点，不存储实际数据，仅作为链表的起始标记。其作用包括：

- **简化边界处理**：无需对空链表或插入到头部/尾部的情况做特殊判断
- **统一操作逻辑**：所有插入、删除操作都针对某个真实节点的前驱进行
- **避免空指针异常**：确保 head 指针始终指向一个有效节点

```cpp
class MyLinkedList {
private:
    int size;           // 链表长度
    ListNode* dummy;    // 哨兵节点

public:
    MyLinkedList() {
        size = 0;
        dummy = new ListNode(0);  // 创建哨兵节点
    }
};
```

带哨兵节点的链表结构：

```
+-----+     +-----+     +-----+     +-----+
| dummy| --> |  1  | --> |  2  | --> |  3  | --> NULL
+-----+     +-----+     +-----+     +-----+
  (sentinel)   val=1       val=2       val=3
```

## 2. 完整实现代码

下面是一个完整的单向链表实现，支持常见的增删改查操作。

### 2.1 类的完整定义

```cpp
#include <iostream>

struct ListNode {
    int val;
    ListNode* next;

    ListNode(int x) : val(x), next(nullptr) {}
};

class MyLinkedList {
private:
    int size;
    ListNode* dummy;  // 哨兵节点，简化边界处理

public:
    // 构造函数：初始化哨兵节点和大小
    MyLinkedList() {
        size = 0;
        dummy = new ListNode(0);  // 哨兵节点不存储数据
    }

    // 析构函数：释放所有节点内存
    ~MyLinkedList() {
        ListNode* cur = dummy;
        while (cur) {
            ListNode* next = cur->next;
            delete cur;
            cur = next;
        }
    }

    // 获取第 index 个节点的值，index 从 0 开始
    int get(int index) {
        if (index < 0 || index >= size) {
            return -1;  // 无效索引
        }
        ListNode* cur = dummy->next;  // 从第一个真实节点开始
        for (int i = 0; i < index; i++) {
            cur = cur->next;
        }
        return cur->val;
    }

    // 在头部插入节点 - O(1)
    void addAtHead(int val) {
        ListNode* newNode = new ListNode(val);
        newNode->next = dummy->next;
        dummy->next = newNode;
        size++;
    }

    // 在尾部插入节点 - O(n)
    void addAtTail(int val) {
        ListNode* newNode = new ListNode(val);
        ListNode* cur = dummy;
        while (cur->next != nullptr) {
            cur = cur->next;
        }
        cur->next = newNode;
        size++;
    }

    // 在第 index 个位置插入节点 - O(n)
    void addAtIndex(int index, int val) {
        if (index < 0 || index > size) {
            return;  // 无效索引（注意：index == size 允许在尾部插入）
        }
        ListNode* newNode = new ListNode(val);
        ListNode* cur = dummy;
        for (int i = 0; i < index; i++) {
            cur = cur->next;
        }
        newNode->next = cur->next;
        cur->next = newNode;
        size++;
    }

    // 删除第 index 个节点 - O(n)
    void deleteAtIndex(int index) {
        if (index < 0 || index >= size) {
            return;  // 无效索引
        }
        ListNode* cur = dummy;
        for (int i = 0; i < index; i++) {
            cur = cur->next;
        }
        ListNode* toDelete = cur->next;
        cur->next = toDelete->next;
        delete toDelete;
        size--;
    }

    // 打印链表
    void printList() {
        ListNode* cur = dummy->next;
        std::cout << "LinkedList: ";
        while (cur != nullptr) {
            std::cout << cur->val;
            if (cur->next) std::cout << " -> ";
            cur = cur->next;
        }
        std::cout << " -> NULL" << std::endl;
    }

    // 获取链表大小
    int getSize() {
        return size;
    }
};
```

### 2.2 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|------|-----------|-----------|------|
| `addAtHead(val)` | **O(1)** | O(1) | 直接在头部插入，无需遍历 |
| `addAtTail(val)` | **O(n)** | O(1) | 需要遍历到尾部 |
| `get(index)` | **O(n)** | O(1) | 需要遍历到指定位置 |
| `addAtIndex(index, val)` | **O(n)** | O(1) | 需要遍历到指定位置 |
| `deleteAtIndex(index)` | **O(n)** | O(1) | 需要遍历到指定位置 |

### 2.3 关键实现细节

**头部插入（addAtHead）**：

```cpp
void addAtHead(int val) {
    ListNode* newNode = new ListNode(val);
    newNode->next = dummy->next;  // 新节点指向原头部
    dummy->next = newNode;        // 哨兵节点指向新节点
    size++;
}
```

**尾部插入（addAtTail）**：

```cpp
void addAtTail(int val) {
    ListNode* newNode = new ListNode(val);
    ListNode* cur = dummy;
    while (cur->next != nullptr) {  // 遍历到尾节点
        cur = cur->next;
    }
    cur->next = newNode;  // 尾节点指向新节点
    size++;
}
```

**指定位置删除（deleteAtIndex）**：

```cpp
void deleteAtIndex(int index) {
    ListNode* cur = dummy;
    for (int i = 0; i < index; i++) {  // 遍历到待删除节点的前驱
        cur = cur->next;
    }
    ListNode* toDelete = cur->next;
    cur->next = toDelete->next;  // 前驱节点跨过待删除节点
    delete toDelete;             // 释放内存
    size--;
}
```

## 3. 使用示例

### 3.1 基本操作演示

```cpp
int main() {
    MyLinkedList* obj = new MyLinkedList();

    // 添加元素
    obj->addAtHead(1);     // 链表: 1 -> NULL
    obj->addAtTail(3);     // 链表: 1 -> 3 -> NULL
    obj->addAtIndex(1, 2); // 链表: 1 -> 2 -> 3 -> NULL

    // 获取元素
    std::cout << "get(0) = " << obj->get(0) << std::endl;  // 输出 1
    std::cout << "get(1) = " << obj->get(1) << std::endl;  // 输出 2
    std::cout << "get(2) = " << obj->get(2) << std::endl;  // 输出 3

    obj->printList();  // 输出: LinkedList: 1 -> 2 -> 3 -> NULL

    // 删除元素
    obj->deleteAtIndex(1);  // 删除位置 1 的节点（值为 2）
    obj->printList();       // 输出: LinkedList: 1 -> 3 -> NULL

    // 再次获取验证
    std::cout << "get(1) after delete = " << obj->get(1) << std::endl;  // 输出 3

    delete obj;
    return 0;
}
```

运行结果：

```
get(0) = 1
get(1) = 2
get(2) = 3
LinkedList: 1 -> 2 -> 3 -> NULL
LinkedList: 1 -> 3 -> NULL
get(1) after delete = 3
```

### 3.2 完整测试用例

```cpp
#include <cassert>
#include <iostream>

int main() {
    // 测试空链表
    MyLinkedList* list = new MyLinkedList();
    assert(list->get(0) == -1);  // 空链表访问无效
    assert(list->getSize() == 0);

    // 测试 addAtHead
    list->addAtHead(1);
    list->addAtHead(2);
    list->addAtHead(3);
    assert(list->get(0) == 3);   // 头部是最新插入的 3
    assert(list->get(1) == 2);
    assert(list->get(2) == 1);
    assert(list->getSize() == 3);

    // 测试 addAtTail
    list->addAtTail(4);
    assert(list->get(3) == 4);
    assert(list->getSize() == 4);

    // 测试 addAtIndex
    list->addAtIndex(2, 5);  // 在位置 2 插入 5
    assert(list->get(2) == 5);
    assert(list->get(3) == 1);  // 原位置 2 的节点被挤到位置 3

    // 测试 deleteAtIndex
    list->deleteAtIndex(2);  // 删除位置 2 的节点（值为 5）
    assert(list->get(2) == 1);
    assert(list->getSize() == 4);

    // 测试越界操作
    list->deleteAtIndex(10);  // 无效删除，不应崩溃
    list->addAtIndex(100, 999);  // 无效插入，不应崩溃

    list->printList();

    delete list;
    std::cout << "All tests passed!" << std::endl;
    return 0;
}
```

## 4. 双向链表 vs 单向链表

### 4.1 复杂度对比

| 操作 | 单向链表 | 双向链表 |
|------|---------|---------|
| 头部插入 | O(1) | O(1) |
| 尾部插入 | O(n) | O(1) |
| 头部删除 | O(1) | O(1) |
| 尾部删除 | O(n) | O(1) |
| 指定位置插入 | O(n) | O(n) |
| 指定位置删除 | O(n) | O(n) |
| 搜索 | O(n) | O(n) |

### 4.2 实现差异

**单向链表节点**：

```cpp
struct ListNode {
    int val;
    ListNode* next;
};
```

**双向链表节点**：

```cpp
struct DListNode {
    int val;
    DListNode* prev;
    DListNode* next;
};
```

双向链表的哨兵节点设计：

```
+--------+     +-----+     +-----+     +-----+
|  dummy | <-> |  1  | <-> |  2  | <-> |  3  | <-> NULL
+--------+     +-----+     +-----+     +-----+
              (head)               (tail)
```

双向链表的尾部操作优势：

```cpp
// 单向链表尾部删除 - O(n)
void deleteAtTail(ListNode*& head) {
    if (head == nullptr) return;
    if (head->next == nullptr) { delete head; head = nullptr; return; }
    ListNode* cur = head;
    while (cur->next->next != nullptr) {
        cur = cur->next;
    }
    delete cur->next;
    cur->next = nullptr;
}

// 双向链表尾部删除 - O(1)
void deleteAtTail(DListNode* tail) {
    if (tail == nullptr) return;
    DListNode* prev = tail->prev;
    prev->next = nullptr;
    delete tail;
}
```

### 4.3 如何选择

- **单向链表适用场景**：内存敏感、只需单向遍历（如栈的实现、链表翻转）
- **双向链表适用场景**：需要双向遍历、频繁在头部和尾部操作（如 LRU Cache、浏览器历史记录）

## 5. LeetCode 题目推荐

### 5.1 #707 Design Linked List

设计链表是 LeetCode 中的经典题目，要求实现一个支持以下操作的链表：

- `get(index)` - 获取链表中第 index 个节点的值
- `addAtHead(val)` - 在链表头部插入值为 val 的节点
- `addAtTail(val)` - 在链表尾部插入值为 val 的节点
- `addAtIndex(index, val)` - 在链表第 index 个位置插入值为 val 的节点
- `deleteAtIndex(index)` - 删除链表中第 index 个节点

本题的核心考察点：

- 哨兵节点的使用
- 边界条件处理（空链表、头部、尾部）
- 内存管理（new/delete）

### 5.2 #206 Reverse Linked List

链表的翻转是另一道经典题目，要求将链表反转：

```
输入: 1 -> 2 -> 3 -> 4 -> 5 -> NULL
输出: 5 -> 4 -> 3 -> 2 -> 1 -> NULL
```

**迭代解法 - O(n) 时间，O(1) 空间**：

```cpp
ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    ListNode* curr = head;
    while (curr != nullptr) {
        ListNode* next = curr->next;  // 保存下一个节点
        curr->next = prev;             // 反转指向
        prev = curr;                   // prev 前移
        curr = next;                   // curr 前移
    }
    return prev;  // 新的头节点
}
```

**递归解法 - O(n) 时间，O(n) 空间（调用栈）**：

```cpp
ListNode* reverseListRecursive(ListNode* head) {
    if (head == nullptr || head->next == nullptr) {
        return head;
    }
    ListNode* newHead = reverseListRecursive(head->next);
    head->next->next = head;
    head->next = nullptr;
    return newHead;
}
```

翻转链表的核心思想是：遍历过程中反转每个节点的 next 指针，使原本指向后继的指针指向前驱，最终链表方向完全反转。

---
