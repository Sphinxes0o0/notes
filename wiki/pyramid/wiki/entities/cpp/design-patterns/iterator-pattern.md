---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Iterator Pattern (迭代器模式)

## GoF 定义

提供一种方法顺序访问集合元素，而不暴露底层表示。

## C++ 实现

### 二叉树前序迭代器

```cpp
template <typename T>
struct Node { T value; Node<T>* left, *right, *parent; BinaryTree<T>* tree; };

template <typename T>
struct BinaryTree {
    Node<T>* root = nullptr;
    explicit BinaryTree(Node<T>* r) : root(r) { r->set_tree(this); }
};

template <typename U>
struct PreOrderIterator {
    Node<U>* current;
    explicit PreOrderIterator(Node<U>* n) : current(n) {}
    bool operator!=(const PreOrderIterator& o) const { return current != o.current; }
    Node<U>& operator*() { return *current; }
    PreOrderIterator& operator++() {
        if (current->right) {
            current = current->right;
            while (current->left) current = current->left;
        } else {
            Node<T>* p = current->parent;
            while (p && current == p->right) { current = p; p = p->parent; }
            current = p;
        }
        return *this;
    }
};

template <typename T>
struct Tree {
    using iterator = PreOrderIterator<T>;
    iterator begin() {
        Node<T>* n = root;
        while (n->left) n = n->left;
        return iterator{n};
    }
    iterator end() { return iterator{nullptr}; }
};
```

### 协程版本（后序遍历）

```cpp
generator<Node<T>*> post_order_impl(Node<T>* node) {
    if (node) {
        for (auto x : post_order_impl(node->left)) co_yield x;
        for (auto y : post_order_impl(node->right)) co_yield y;
        co_yield node;
    }
}
generator<Node<T>*> post_order() { return post_order_impl(root); }
```

## 关键点

- 自定义迭代器需实现 `++`, `!=`, `*` 操作符
- C++20 协程使递归遍历无需手动维护栈
- `begin()/end()` 让容器兼容基于范围的 `for` 循环

## 相关模式

- [[composite-pattern]]
- [[visitor-pattern]]
