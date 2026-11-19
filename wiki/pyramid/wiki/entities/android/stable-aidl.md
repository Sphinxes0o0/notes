---
type: entity
tags: [android, AIDL, IPC, Treble]
created: 2026-05-25
sources: [notes-android]
---

# Stable AIDL — 稳定的 AIDL 接口

## 定义

Android 10 引入的稳定 AIDL 是替代 HIDL 的新 IPC 机制。相比 HIDL，Stable AIDL **仅支持结构化数据**（parcelable），不允许非结构化接口，并内置版本控制机制。

## 与 HIDL 的主要区别

| 特性 | HIDL | Stable AIDL |
|------|------|-------------|
| 接口定义语言 | 自定义 .hal 文件 | AIDL (.aidl 文件) |
| 数据类型 | .hal struct + 自定义类型 | 只能是 parcelable（结构化数据）|
| 版本控制 | 包级别版本 (`@1.0`, `@2.0`) | 接口级别版本（aidl_interface + versions）|
| 默认实现 | 不支持 | 支持 `IFooDefault` 默认实现 |
| 引入版本 | Android 8.0 (O) | Android 10 (Q) |

## 版本控制机制

```protobuf
aidl_interface {
    name: "my-module-name",
    srcs: ["tests_1/some/package/IFoo.aidl"],
    versions: ["1", "2"],  // 已冻结版本
}
```

- 冻结版本在 `api/` 目录追踪 API 定义
- `foo-freeze-api` 在构建时冻结新版本
- 向后兼容：只允许在接口末尾添加新方法，不允许修改/删除已有方法

## 默认实现（处理旧接口）

```cpp
class MyDefault : public IFooDefault {
    Status anAddedMethod(...) override {
        // 旧版本服务器不实现此方法时调用默认实现
    }
};
IFoo::setDefaultImpl(std::unique_ptr<IFoo>(MyDefault));
```

## 相关概念

- [[hidl]] — HIDL 是 Android 8.0 的方案，Stable AIDL 是其演进
- [[treble-architecture]] — 两者都是 Treble 架构的 IPC 基础设施
- [[vintf]] — Stable AIDL 接口通过 VINTF 设备清单管理
- [[hal]] — HAL 接口仍可使用 HIDL（尤其对 SP-HAL）

## 来源详情

- [[notes-android]] — 13_stable-aidl.md
