# std::stack 详解

## 概述

`std::stack` 是一个容器适配器，它提供了后进先出（LIFO - Last In First Out）的数据结构。stack 不是一个真正的容器，而是基于其他容器（默认是deque）的包装器。

## 特性

- **底层数据结构**：默认使用 deque，也可以使用 vector 或 list
- **时间复杂度**：
  - 顶部插入、删除：O(1)
  - 不支持遍历和随机访问
- **访问限制**：只能访问栈顶元素
- **大小**：运行时可变

## 主要函数

|             方法             |     分类       |                                      含义                                       |
|:----------------------------:|:-------------:|:------------------------------------------------------------------------------:|
| top                         | element access| 返回栈顶元素的引用                                                              |
| empty                       | capacity      | 检查栈是否为空                                                                  |
| size                        | capacity      | 返回栈中元素的数量                                                              |
| push                        | modifiers     | 将元素压入栈顶                                                                  |
| emplace                     | modifiers     | 在栈顶原地构造元素                                                              |
| pop                         | modifiers     | 弹出栈顶元素（不返回值）                                                        |
| swap                        | modifiers     | 与另一个stack交换内容                                                           |

## 使用示例

```cpp
#include <stack>
#include <iostream>
#include <vector>
#include <list>

int main() {
    // 1. 基本操作
    std::stack<int> st;
    
    // 压入元素
    st.push(10);
    st.push(20);
    st.push(30);
    
    std::cout << "Stack size: " << st.size() << std::endl;
    std::cout << "Top element: " << st.top() << std::endl;
    
    // 2. 弹出元素
    while (!st.empty()) {
        std::cout << "Popping: " << st.top() << std::endl;
        st.pop();  // 注意：pop()不返回值
    }
    
    // 3. 使用不同的底层容器
    std::stack<int, std::vector<int>> stack_with_vector;
    std::stack<int, std::list<int>> stack_with_list;
    
    // 向不同底层容器的stack添加元素
    for (int i = 1; i <= 5; ++i) {
        stack_with_vector.push(i);
        stack_with_list.push(i * 10);
    }
    
    std::cout << "Vector-based stack size: " << stack_with_vector.size() << std::endl;
    std::cout << "List-based stack size: " << stack_with_list.size() << std::endl;
    
    // 4. emplace操作（C++11）
    std::stack<std::pair<int, std::string>> pair_stack;
    pair_stack.emplace(1, "first");   // 直接构造pair
    pair_stack.push({2, "second"});   // 使用临时对象
    
    while (!pair_stack.empty()) {
        auto& top_pair = pair_stack.top();
        std::cout << "(" << top_pair.first << ", " << top_pair.second << ")" << std::endl;
        pair_stack.pop();
    }
    
    // 5. 实际应用：括号匹配
    auto isValidParentheses = [](const std::string& s) {
        std::stack<char> stack;
        for (char c : s) {
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c);
            } else if (c == ')' || c == ']' || c == '}') {
                if (stack.empty()) return false;
                char top = stack.top();
                stack.pop();
                if ((c == ')' && top != '(') ||
                    (c == ']' && top != '[') ||
                    (c == '}' && top != '{')) {
                    return false;
                }
            }
        }
        return stack.empty();
    };
    
    std::string test1 = "()[]{}";
    std::string test2 = "([{}])";
    std::string test3 = "([)]";
    
    std::cout << test1 << " is " << (isValidParentheses(test1) ? "valid" : "invalid") << std::endl;
    std::cout << test2 << " is " << (isValidParentheses(test2) ? "valid" : "invalid") << std::endl;
    std::cout << test3 << " is " << (isValidParentheses(test3) ? "valid" : "invalid") << std::endl;
    
    return 0;
}
```

## 模板声明

```cpp
template<
    class T,
    class Container = std::deque<T>
> class stack;
```

### 底层容器要求

底层容器必须支持以下操作：
- `back()` - 访问最后一个元素
- `push_back()` - 在末尾添加元素
- `pop_back()` - 移除最后一个元素
- `empty()` - 检查是否为空
- `size()` - 获取大小

常用的底层容器：
- `std::deque`（默认）- 双端队列
- `std::vector` - 动态数组
- `std::list` - 双向链表

## 不同底层容器的特性比较

| 底层容器 | 内存布局 | 扩容策略 | 性能特点 |
|----------|----------|----------|----------|
| deque | 分段连续 | 按需分配新段 | 平衡的性能 |
| vector | 连续 | 倍数增长 | 缓存友好，但可能重分配 |
| list | 链表 | 逐个节点分配 | 无重分配，但缓存不友好 |

## 实际应用场景

### 1. 表达式求值

```cpp
#include <stack>
#include <string>

int evaluatePostfix(const std::vector<std::string>& tokens) {
    std::stack<int> stack;
    
    for (const std::string& token : tokens) {
        if (token == "+" || token == "-" || token == "*" || token == "/") {
            int b = stack.top(); stack.pop();
            int a = stack.top(); stack.pop();
            
            if (token == "+") stack.push(a + b);
            else if (token == "-") stack.push(a - b);
            else if (token == "*") stack.push(a * b);
            else if (token == "/") stack.push(a / b);
        } else {
            stack.push(std::stoi(token));
        }
    }
    
    return stack.top();
}
```

### 2. 函数调用栈模拟

```cpp
#include <stack>
#include <iostream>

struct CallFrame {
    std::string function_name;
    int line_number;
    std::string local_vars;
};

class CallStack {
private:
    std::stack<CallFrame> stack;
    
public:
    void pushFrame(const std::string& func, int line, const std::string& vars = "") {
        stack.push({func, line, vars});
        std::cout << "Entering " << func << " at line " << line << std::endl;
    }
    
    void popFrame() {
        if (!stack.empty()) {
            std::cout << "Exiting " << stack.top().function_name << std::endl;
            stack.pop();
        }
    }
    
    void printStackTrace() {
        std::stack<CallFrame> temp_stack = stack;  // 复制栈
        std::cout << "Stack trace:" << std::endl;
        while (!temp_stack.empty()) {
            const auto& frame = temp_stack.top();
            std::cout << "  " << frame.function_name 
                      << " (line " << frame.line_number << ")" << std::endl;
            temp_stack.pop();
        }
    }
};
```

## 性能考虑

### 选择底层容器的建议

1. **默认选择 deque**：
   - 平衡的性能特征
   - 无需重新分配整个容器
   - 适合大多数场景

2. **选择 vector**：
   - 需要更好的缓存性能
   - 元素较小且数量可预估
   - 不在意偶尔的重分配开销

3. **选择 list**：
   - 元素较大，移动成本高
   - 严格避免重分配
   - 不关心缓存性能

## 注意事项

1. **pop() 不返回值**：这是为了异常安全，需要先用 top() 获取值，再 pop()
2. **访问空栈**：对空栈调用 top() 或 pop() 是未定义行为
3. **没有迭代器**：stack 不提供迭代器接口，无法遍历
4. **非标准容器**：stack 是适配器，不是真正的容器类

## 与其他容器的比较

| 特性 | stack | vector | deque | list |
|------|-------|--------|-------|------|
| 后端访问 | 仅栈顶 | 支持 | 支持 | 支持 |
| 随机访问 | 不支持 | 支持 | 支持 | 不支持 |
| 插入位置 | 仅栈顶 | 任意 | 两端优化 | 任意 |
| 迭代器 | 无 | 随机访问 | 随机访问 | 双向 |
| 用途 | LIFO操作 | 通用容器 | 双端操作 | 频繁插入删除 | 