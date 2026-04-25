---
title: QOM (QEMU 对象模型)
---

# QOM (QEMU 对象模型) 架构分析

## 概述

QOM 是 QEMU 的核心对象模型系统，提供动态类型注册、继承、接口实现等面向对象特性。

## 核心结构

### TypeInfo 和 TypeImpl

```c
// include/qom/object.h
struct TypeInfo {
    const char *name;                    // 类型名称
    size_t instance_size;                // 实例大小
    size_t instance_align;               // 实例对齐
    void (*instance_init)(Object *);    // 实例初始化
    void (*instance_post_init)(Object *);
    void (*instance_finalize)(Object *);
    bool (*abstract);                    // 是否抽象类
    const char *parent;                  // 父类型
    class_init;
    object_finalize;
    property;
};
```

### Object 和 ObjectClass

```c
struct ObjectClass {
    Type type;                          // 类型指针
    ObjectClass *parent;                 // 父类
    GHashTable *properties;              // 属性表
};

struct Object {
    ObjectClass *class;                  // 类指针
    Object *parent;                      // 父对象
    gchar *free_path;                    // 释放路径
    QTAILQ_HEAD(, ObjectProperty) properties;
};
```

## 类层次结构

```
Type
├── OBJECT
├── OBJECT_CLASS
│   ├── TYPE_OBJECT
│   ├── TYPE_DEVICE
│   │   ├── TYPE_SYSTEM_DEVICE
│   │   └── TYPE_PCI_DEVICE
│   ├── TYPE_BUS
│   └── TYPE_MEMORY_REGION
├── INTERFACE
│   ├── TYPE_USER_CREATABLE
│   └── TYPE_vmstate_info
└── ... (其他类型)
```

## 核心机制

### 类型注册

```c
// 静态注册宏
type_register_static(&info)
type_register_static_array(info, n)
```

### 对象创建流程

```
object_new_with_class()
  → object_initialize_with_class()
    → object_init()
      → instance_init()  // 用户回调
```

### 属性系统

- `object_property_add_*()` 系列函数添加属性
- `object_property_get/set()` 访问属性
- `object_property_find_err()` 查找属性

## 接口实现

```c
#define INTERFACE check_type

static const TypeInfo interface_info = {
    .name = TYPE_INTERFACE,
    .parent = TYPE_OBJECT,
};

InterfaceInfo interface_cast;
```

## 设计模式

1. **原型模式**: 对象通过 `object_new` 原型克隆
2. **工厂模式**: `type_create_object` 工厂方法
3. **注册表模式**: 全局 `type_table` 存储所有类型
4. **组合模式**: 对象通过 `parent` 形成树结构
