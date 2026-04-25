---
title: QAPI Schema 和代码生成
---

# QAPI Schema 和代码生成分析

## 概述

QAPI (QEMU API) 是一个模式驱动的代码生成系统，从 JSON schema 定义生成 QMP 命令、事件和数据类型的 C 代码。

## 架构组件

### Schema 文件

- 主 schema: `qapi/qapi-schema.json` - 通过 `include` 指令聚合所有子 schema
- 40+ 专业 schema 文件 (block.json, crypto.json, machine.json 等)
- 定义: enums, structs, unions, alternates, commands, events

### 代码生成管道

| 文件 | 功能 |
|------|------|
| `parser.py` | JSON 类 schema 语法的词法分析器/解析器 |
| `expr.py` | 根据 QAPI 语法验证和规范化表达式 |
| `schema.py` | 从验证的表达式构建内存中 schema 模型 |
| `gen.py` | 生成代码的基类 (`QAPIGen*`) |
| `types.py` | 生成 C 类型定义 (结构体, enums, 数组) |
| `visit.py` | 为序列化生成访问者模式代码 |
| `commands.py` | 生成命令 marshaller (QMP 处理程序) |
| `events.py` | 生成事件发送代码 |
| `introspect.py` | 生成内省 schema |
| `backend.py` | 编排生成管道 |

## 访问者模式实现

### 核心模式

```python
# scripts/qapi/schema.py
class QAPISchemaVisitor:
    def visit_begin(self, schema: QAPISchema) -> None
    def visit_end(self) -> None
    def visit_module(self, name: str) -> None
    def visit_builtin_type(self, name, info, json_type) -> None
    def visit_enum_type(self, name, info, ifcond, features, members, prefix) -> None
    def visit_array_type(self, name, info, ifcond, element_type) -> None
    def visit_object_type(self, name, info, ifcond, features, base, members, branches) -> None
    def visit_command(self, name, info, ifcond, features, arg_type, ret_type, ...) -> None
    def visit_event(self, name, info, ifcond, features, arg_type, boxed) -> None
```

### Schema 实体层次

```
QAPISchemaEntity              # 所有 schema 对象的基类
├── QAPISchemaDefinition      # 有名称/文档的实体
├── QAPISchemaType (ABC)     # 数据类型
│   ├── QAPISchemaBuiltinType # int, str, bool 等
│   ├── QAPISchemaEnumType   # 枚举类型
│   ├── QAPISchemaArrayType   # 数组类型
│   ├── QAPISchemaObjectType  # 结构体/联合
│   └── QAPISchemaAlternateType # 标签联合
├── QAPISchemaCommand        # QMP 命令
└── QAPISchemaEvent          # QMP 事件
```

## 关键设计模式

### 模块化代码生成

```python
# scripts/qapi/gen.py
class QAPISchemaModularCVisitor
# 生成独立的 .c/.h 文件对
# 使用 ifcontext() 上下文管理器包装条件代码
```

### 条件编译

```python
# scripts/qapi/schema.py
class QAPISchemaIfCond
# 为 schema 实体附加 C 预处理器条件
```

### 隐式类型

- 命令参数: `q_obj_<name>-arg` 结构体
- 联合基类: `q_obj_<name>-base` 结构体
- 数组元素: `<type>List` 命名约定

## 代码生成流程

```
1. Parse      → QAPISchemaParser 标记化和解析 JSON schema
2. Normalize  → check_exprs() 验证和规范化表达式
3. Build      → QAPISchema 构造 Python 对象模型
4. Visit      → 每个生成器访问者遍历 schema 树
5. Write      → 生成代码写入输出目录
```

## 生成输出文件

每个 schema 模块生成:
- `qapi-types.h/.c` - C 结构体/enum 定义
- `qapi-visit.h/.c` - 序列化访问者函数
- `qapi-commands.h/.c` - 命令 marshaller
- `qapi-events.h/.c` - 事件发送函数
- `qapi-introspect.h/.c` - 内省数据

## 入口点

```python
# scripts/qapi/main.py
def main() -> int:
    schema = QAPISchema(args.schema)
    backend = create_backend(args.backend)
    backend.generate(schema, output_dir=args.output_dir, ...)
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `qapi/*.json` | Schema 定义 |
| `scripts/qapi/*.py` | 代码生成器 |
| `qapi/*.c` | 生成的代码 |
