# 序列化

## 什么是序列化

在编写应用程序的时候往往需要将程序的某些数据存储在内存中，
然后将其写入某个文件或是将它传输到网络中的另一台计算机上以实现通讯。
这个将 程序数据转化成能被存储并传输的格式的过程被称为"序列化"（Serialization），
而它的逆过程则可被称为"反序列化" （Deserialization）。

简单来说，序列化就是将对象实例的状态转换为可保持或传输的格式的过程。
与序列化相对的是反序列化，它根据流重构对象。这两个过程结合起来，可以轻 松地存储和传输数据。
例如，可以序列化一个对象，然后使用 HTTP 通过 Internet 在客户端和服务器之间传输该对象。


## 总结

* 序列化：将对象变成字节流的形式传出去。
* 反序列化：从字节流恢复成原来的对象。


## 为什么要序列化

对象序列化通常用于两个目的：

1. 将对象存储于硬盘上 ，便于以后反序列化使用

2. 在网络上传送对象的字节序列


网络传输方面的便捷性、灵活性;
这里举个可能发生的需求：
有一个数据结构，里面存储的数据是经过很多其它数据通过非常复杂的算法生成的，由于数据量很大，算法又复杂，
因此生成该数据结构所用数据的时间可能要很久（也许几个小时，甚至几天），生成该数据结构后又要用作其他的计算，
那么你在调试阶段，每次运行个程序，就光生成数据结构就要花上这么长的时间，无疑代价是非常大的。
如果你确定生成数据结构的算法不会变或不常变，那么就可以通过序列化技术生成数据结构数据存储到磁盘上，
下次重新运行程序时只需要从磁盘上读 取该对象数据即可，所花费时间也就读一个文件的时间，可想而知是多么的快，节省了开发时间。

## 序列化方案对比

常见的序列化方案可以分为以下几类：

| 方案 | 格式 | 优点 | 缺点 |
|------|------|------|------|
| JSON | 文本 | 人类可读、跨语言支持广泛 | 占用空间大、解析速度慢 |
| XML | 文本 | 人类可读、支持 schema 验证 | 占用空间更大、解析速度慢 |
| Protocol Buffers | 二进制 | 高效、跨语言、向后兼容 | 需要定义 IDL、不可读 |
| MessagePack | 二进制 | 高效、跨语言、简单 | 不支持复杂类型 |
| FlatBuffers | 二进制 | 零拷贝解析、效率极高 | 复杂、库体积大 |
| Thrift | 二进制 | 高效、跨语言、功能全面 | 需要定义 IDL |
| ASN.1 | 二进制/文本 | 标准成熟、安全性好 | 复杂、学习曲线陡峭 |

## JSON 序列化

### JSON 格式特点

JSON（JavaScript Object Notation）是一种轻量级的数据交换格式，具有以下特点：

- 人类可读
- 跨语言支持广泛
- 支持多种数据类型：字符串、数字、布尔值、数组、对象、null
- 无法表示二进制数据（需要 Base64 编码）

### C++ JSON 库

#### nlohmann/json

nlohmann/json 是 C++ 中最流行的 JSON 库之一，header-only 设计，使用方便：

```cpp
#include <iostream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct Person {
    std::string name;
    int age;
    std::vector<std::string> hobbies;
};

void to_json(json& j, const Person& p) {
    j = json{{"name", p.name}, {"age", p.age}, {"hobbies", p.hobbies}};
}

void from_json(const json& j, Person& p) {
    p.name = j.at("name").get<std::string>();
    p.age = j.at("age").get<int>();
    p.hobbies = j.at("hobbies").get<std::vector<std::string>>();
}

int main() {
    Person person{"张三", 30, {"读书", "游泳", "编程"}};

    // 序列化
    json j = person;
    std::string json_str = j.dump(4);  // 格式化输出，缩进 4 空格
    std::cout << json_str << std::endl;

    // 反序列化
    json j2 = json::parse(json_str);
    Person p2 = j2.get<Person>();
    std::cout << "Name: " << p2.name << std::endl;

    // 直接构建
    json j3 = {
        {"product", "Widget"},
        {"quantity", 100},
        {"price", 9.99},
        {"in_stock", true}
    };

    return 0;
}
```

#### RapidJSON

RapidJSON 是一个高性能的 JSON 解析/生成库，支持 SAX 和 DOM 两种解析模式：

```cpp
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

int main() {
    // 解析 JSON
    const char* json = R"({"name":"李四","age":25})";
    rapidjson::Document d;
    d.Parse(json);

    std::cout << "Name: " << d["name"].GetString() << std::endl;
    std::cout << "Age: " << d["age"].GetInt() << std::endl;

    // 生成 JSON
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);

    buffer.Clear();
    writer.Reset(buffer);

    writer.StartObject();
    writer.Key("name");
    writer.String("王五");
    writer.Key("age");
    writer.Int(35);
    writer.Key("city");
    writer.String("北京");
    writer.EndObject();

    std::cout << buffer.GetString() << std::endl;

    return 0;
}
```

## XML 序列化

### XML 格式特点

XML（eXtensible Markup Language）是一种标记语言，具有以下特点：

- 人类可读
- 支持属性和元素
- 支持命名空间，避免命名冲突
- 支持 Schema 和 DTD 验证
- 占用空间较大，解析速度较慢

### C++ XML 库

#### TinyXML-2

TinyXML-2 是一个轻量级的 XML 解析库：

```cpp
#include <tinyxml2.h>
#include <iostream>

using namespace tinyxml2;

int main() {
    XMLDocument doc;

    // 创建 XML 文档
    XMLElement* root = doc.NewElement("People");
    doc.InsertFirstChild(root);

    XMLElement* person = doc.NewElement("Person");
    person->SetAttribute("id", "1");
    root->InsertEndChild(person);

    XMLElement* name = doc.NewElement("Name");
    name->SetText("张三");
    person->InsertEndChild(name);

    XMLElement* age = doc.NewElement("Age");
    age->SetText("30");
    person->InsertEndChild(age);

    // 保存到文件
    doc.SaveFile("people.xml");

    // 从文件加载
    XMLDocument doc2;
    doc2.LoadFile("people.xml");

    XMLElement* root2 = doc2.FirstChildElement("People");
    XMLElement* person2 = root2->FirstChildElement("Person");

    const char* name_str = person2->FirstChildElement("Name")->GetText();
    int age_val = person2->FirstChildElement("Age")->IntText();

    std::cout << "Name: " << name_str << std::endl;
    std::cout << "Age: " << age_val << std::endl;

    return 0;
}
```

## Protocol Buffers

### 什么是 Protocol Buffers

Google Protocol Buffers（GPB）是 Google 内部使用的数据编码方式，旨在用来代替 XML 进行数据交换。可用于数据序列化与反序列化。主要特性有：

- 高效：二进制格式，体积小、解析快
- 语言中立(Cpp, Java, Python, Go, etc.)
- 可扩展：支持字段添加和变更，保持向后兼容
- 自动生成序列化代码
- 官方文档完善

### 定义 .proto 文件

```protobuf
syntax = "proto3";

package addressbook;

message Person {
    string name = 1;
    int32 id = 2;
    string email = 3;

    enum PhoneType {
        MOBILE = 0;
        HOME = 1;
        WORK = 2;
    }

    message PhoneNumber {
        string number = 1;
        PhoneType type = 2;
    }

    repeated PhoneNumber phones = 4;
}

message AddressBook {
    repeated Person people = 1;
}
```

### C++ 使用 Protocol Buffers

```cpp
#include <iostream>
#include <fstream>
#include "addressbook.pb.h"

int main() {
    // 初始化 protobuf 库
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    // 创建 Person
    Person person;
    person.set_name("张三");
    person.set_id(1);
    person.set_email("zhangsan@example.com");

    Person::PhoneNumber* phone = person.add_phones();
    phone->set_number("13800138000");
    phone->set_type(Person::MOBILE);

    // 序列化到文件
    std::ofstream output("person.pb", std::ios::binary);
    if (!person.SerializeToOstream(&output)) {
        std::cerr << "Failed to serialize." << std::endl;
        return -1;
    }
    output.close();

    // 从文件反序列化
    std::ifstream input("person.pb", std::ios::binary);
    Person person2;
    if (!person2.ParseFromIstream(&input)) {
        std::cerr << "Failed to parse." << std::endl;
        return -1;
    }
    input.close();

    std::cout << "Name: " << person2.name() << std::endl;
    std::cout << "Email: " << person2.email() << std::endl;
    std::cout << "Phones: " << person2.phones_size() << std::endl;

    // 清理
    google::protobuf::ShutdownProtobufLibrary();

    return 0;
}
```

### Protocol Buffers 的优势

1. **紧凑的数据格式**：二进制格式，比 XML/JSON 小 3-10 倍
2. **快速的解析速度**：解析速度比 XML 快 20-100 倍
3. **跨语言支持**：支持 C++、Java、Python、Go 等多种语言
4. **良好的扩展性**：可以添加新字段，旧的代码可以读取新格式
5. **自动代码生成**：根据 .proto 文件自动生成序列化代码

## Boost.Serialization

### Boost.Serialization 特点

Boost.Serialization 可以创建或重建程序中的等效结构，并保存为二进制数据、文本数据、XML 或者有用户自定义的其他文件。该库具有以下吸引人的特性：

- 代码可移植（实现仅依赖于 ANSI C++）。
- 深度指针保存与恢复。
- 可以序列化 STL 容器和其他常用模版库。
- 数据可移植（跨平台）。
- 非入侵性（不需要修改类的定义）。

### 基本使用

```cpp
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <iostream>
#include <fstream>
#include <sstream>

class Person {
private:
    friend class boost::serialization::access;

    template<class Archive>
    void serialize(Archive& ar, const unsigned int version) {
        ar & name;
        ar & age;
        ar & hobbies;
    }

public:
    std::string name;
    int age;
    std::vector<std::string> hobbies;

    Person() {}  // 必须有默认构造函数
    Person(const std::string& n, int a, const std::vector<std::string>& h)
        : name(n), age(a), hobbies(h) {}
};

int main() {
    // 序列化到文本
    Person p1("李四", 28, {"读书", "运动"});

    std::ostringstream oss;
    boost::archive::text_oarchive oa(oss);
    oa << p1;
    std::string text = oss.str();

    std::cout << "Serialized:\n" << text << std::endl;

    // 反序列化
    std::istringstream iss(text);
    boost::archive::text_iarchive ia(iss);
    Person p2;
    ia >> p2;

    std::cout << "Deserialized - Name: " << p2.name
              << ", Age: " << p2.age << std::endl;

    return 0;
}
```

### 二进制序列化

```cpp
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <fstream>

void save_binary(const Person& p, const std::string& filename) {
    std::ofstream ofs(filename, std::ios::binary);
    boost::archive::binary_oarchive oa(ofs);
    oa << p;
}

void load_binary(Person& p, const std::string& filename) {
    std::ifstream ifs(filename, std::ios::binary);
    boost::archive::binary_iarchive ia(ifs);
    ia >> p;
}
```

## 序列化最佳实践

### 版本控制与兼容性

在设计序列化格式时，需要考虑版本演进：

```cpp
// 使用版本号处理兼容性
message Config {
    int32 version = 1;
    string name = 2;

    // 新版本添加的字段
    string description = 3;  // version >= 2
    int32 timeout_ms = 4;    // version >= 3
}

// 反序列化时检查版本
void load_config(const Config& cfg) {
    if (cfg.version() > CURRENT_VERSION) {
        throw std::runtime_error("Unknown version");
    }

    // 根据版本处理不同字段
    if (cfg.has_name()) {
        // 处理 name
    }

    if (cfg.version() >= 2 && cfg.has_description()) {
        // 处理 description
    }
}
```

### 性能优化建议

1. **预分配内存**：对于动态容器，预分配可以减少内存重新分配
2. **使用零拷贝解析**：如 FlatBuffers，避免数据复制
3. **选择合适的序列化格式**：高性能场景使用二进制格式
4. **批量序列化**：将多个对象合并成一个批次序列化

### 安全性考虑

1. **验证输入**：反序列化前验证数据长度和格式
2. **防止注入攻击**：文本格式需要转义特殊字符
3. **限制递归深度**：XML/JSON 解析限制嵌套深度
4. **加密敏感数据**：序列化后加密重要数据

## MessagePack 简介

MessagePack 是一个高效的二进制序列化格式，介于 JSON 和 Protocol Buffers 之间：

```cpp
#include <msgpack.hpp>
#include <iostream>
#include <vector>

int main() {
    // 序列化
    std::vector<std::string> data = {"hello", "world"};
    msgpack::sbuffer buffer;
    msgpack::pack(buffer, data);

    // 反序列化
    msgpack::object_handle result = msgpack::unpack(buffer.data(), buffer.size());
    std::vector<std::string> unpacked;
    result.get().convert(unpacked);

    std::cout << unpacked[0] << " " << unpacked[1] << std::endl;

    return 0;
}
```
