# 第五章：编码与演化

## 编码基础

内存与字节序列转换。

## 格式类型

JSON、XML、CSV 及二进制变体。

## Protocol Buffers

Google 的基于模式的二进制编码，带字段标签。

## Avro

动态模式方法，使用 writer/reader 模式。

## 向后/向前兼容性

### Protocol Buffers

- 添加新标签字段
- 不要重用或更改现有标签

### Avro

- 仅添加/删除有默认值的字段
- 更改字段类型需要小心处理

## 数据流模式

- 数据库存储
- REST/RPC API
- 消息代理和 Actor 框架

## 图片

![](/fig/ddia_0501.png)

![](/fig/ddia_0502.png)

![](/fig/ddia_0503.png)

![](/fig/ddia_0504.png)

![](/fig/ddia_0505.png)

![](/fig/ddia_0506.png)

![](/fig/ddia_0507.png)
