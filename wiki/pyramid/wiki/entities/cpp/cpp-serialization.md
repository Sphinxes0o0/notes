---
type: entity
tags: [cpp, serialization, data-format]
created: 2026-05-22
sources: [notes-ccpp]
---

# C++ 序列化 (Serialization)

## 定义

序列化是将程序数据结构转换为可存储或传输的格式的过程；反序列化是逆过程，从字节流/文本恢复原始对象。C++ 生态中主流方案包括 JSON（文本）、Protocol Buffers（二进制）、Boost.Serialization（库级）和 MessagePack（轻量二进制）。

## 关键要点

- **核心目的**：持久化存储（写磁盘）和网络传输（跨进程/跨机器通信）
- **方案选择矩阵**：文本格式（JSON/XML）人类可读但体积大；二进制格式（Protobuf/MessagePack/FlatBuffers）高效紧凑但不可读
- **JSON 库**：nlohmann/json（header-only，易用）、RapidJSON（高性能，SAX/DOM 双模式）
- **XML 库**：TinyXML-2（轻量级 DOM 解析）
- **Protocol Buffers**：Google 出品，.proto IDL 定义消息，自动生成序列化代码，比 XML 小 3-10 倍、解析快 20-100 倍，支持字段级向后兼容
- **Boost.Serialization**：非入侵式设计，不需修改类定义，支持文本/二进制/XML 三种归档格式，深度指针保存与恢复
- **MessagePack**：介于 JSON 和 Protobuf 之间，类 JSON 数据结构 + 二进制编码
- **版本控制**：通过版本号字段实现向前/向后兼容，反序列化时按版本号分支处理
- **安全实践**：验证输入长度与格式、限制递归深度（防栈溢出）、加密敏感序列化数据

## 方案对比

| 方案 | 格式 | 优点 | 缺点 |
|------|------|------|------|
| JSON | 文本 | 人类可读、跨语言广泛 | 体积大、无二进制支持 |
| XML | 文本 | Schema 验证、命名空间 | 体积更大、解析慢 |
| Protocol Buffers | 二进制 | 高效、跨语言、向后兼容 | 需 IDL、不可读 |
| MessagePack | 二进制 | 高效、类 JSON 简单 | 不支持复杂类型 |
| FlatBuffers | 二进制 | 零拷贝解析、极致性能 | 复杂、库体积大 |
| Boost.Serialization | 文本/二进制/XML | 非入侵式、深度指针 | 依赖 Boost、归档格式不标准 |

## 代码示例

```cpp
// nlohmann/json: 序列化/反序列化自定义类型
struct Person { std::string name; int age; std::vector<std::string> hobbies; };

void to_json(json& j, const Person& p) {
    j = json{{"name", p.name}, {"age", p.age}, {"hobbies", p.hobbies}};
}
void from_json(const json& j, Person& p) {
    p.name = j.at("name").get<std::string>();
    p.age = j.at("age").get<int>();
    p.hobbies = j.at("hobbies").get<std::vector<std::string>>();
}

// Protocol Buffers: 序列化到文件
Person person;
person.set_name("Zhang San");
person.set_id(1);
std::ofstream output("person.pb", std::ios::binary);
person.SerializeToOstream(&output);

// Boost.Serialization: 非入侵式序列化
template<class Archive>
void serialize(Archive& ar, const unsigned int version) {
    ar & name; ar & age; ar & hobbies;
}
```

## 性能优化

- 预分配内存减少 reallocation
- 零拷贝解析（FlatBuffers 在序列化数据上直接访问，无需复制）
- 高性能场景选二进制格式（Protobuf / MessagePack）
- 批量序列化：合并多个对象为一批

## 相关概念
- [[entities/cpp/cpp-object-lifetime]] — 对象生命周期管理影响序列化/反序列化策略
- [[entities/cpp/smart-pointers]] — 序列化包含指针的对象需要特殊处理（如 Boost 深度指针）
- [[entities/cpp/raii]] — 序列化资源（文件流、网络连接）应使用 RAII 管理
- [[entities/cpp/move-semantics]] — 移动语义可优化序列化中间对象的传递

## 来源详情
- [[sources/notes-ccpp]] — serialization.md：JSON/XML/Protobuf/Boost/MessagePack 全方案覆盖
