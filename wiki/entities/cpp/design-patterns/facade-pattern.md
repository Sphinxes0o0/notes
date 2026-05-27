---
type: entity
tags: [cpp, design-patterns, structural]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Facade Pattern (门面模式)

## GoF 定义

为子系统中的一组接口提供一个统一的高层接口，使子系统更易使用。

## C++ 实现

```cpp
struct Console {
    vector<ViewPort*> viewPorts;
    Size charSize, gridSize;
};

struct ConsoleCreationParameters {
    optional<Size> client_size;
    int character_width{10};
    int character_height{14};
    int width{20};
    int height{30};
    bool fullscreen{false};
    bool create_default_view_and_buffer{true};
};

Console::Console(const ConsoleCreationParameters& ccp) {
    // 创建缓冲和视窗
    // 结合缓冲和视图放入合适集合
    // 生成图像纹理
    // 计算网格大小（全屏模式相关）
}
```

## 关键点

- 门面隐藏子系统的复杂性，提供简化的 API
- 典型场景：终端（控制台 = 门面，缓冲区 + 视窗 = 内部组件）
- 不阻止客户端直接访问底层组件

## 相关模式

- [[mediator-pattern]]
- [[adapter-pattern]]
