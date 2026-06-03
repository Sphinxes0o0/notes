# 第三章：数据模型与查询语言

> 语言的边界就是世界的边界。 — 维特根斯坦

## 数据模型层次

1. 应用程序层：对象和数据结构
2. 数据库层：JSON/XML/关系/图
3. 存储引擎层：字节表示
4. 硬件层：电流/光脉冲/磁场

## 关系模型与文档模型

### 对象关系不匹配

ORM 框架的优缺点。

### 文档数据模型

JSON 文档表示一对多关系更自然。

![](/fig/ddia_0301.png)

**图 3-1: 使用关系模式表示 LinkedIn 个人资料**

```json
{
    "user_id": 251,
    "first_name": "Barack",
    "last_name": "Obama",
    "positions": [
        {"job_title": "President", "organization": "United States of America"}
    ]
}
```

![](/fig/ddia_0302.png)

**图 3-2: 一对多关系形成树状结构**

### 规范化与反规范化

- 规范化：写入更快，查询需连接
- 反规范化：读取更快，写入更昂贵

## 图数据模型

### 属性图

```sql
CREATE TABLE vertices (
    vertex_id integer PRIMARY KEY,
    label text,
    properties jsonb
);

CREATE TABLE edges (
    edge_id integer PRIMARY KEY,
    tail_vertex integer REFERENCES vertices,
    head_vertex integer REFERENCES vertices,
    label text,
    properties jsonb
);
```

### Cypher 查询语言

```cypher
MATCH
    (person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (:Location {name:'United States'}),
    (person) -[:LIVES_IN]-> () -[:WITHIN*0..]-> (:Location {name:'Europe'})
RETURN person.name
```

![](/fig/ddia_0306.png)

**图 3-6: 图结构数据示例**

## 事件溯源与 CQRS

- **事件溯源**: 将状态变化表达为不可变事件
- **CQRS**: 命令查询责任分离

![](/fig/ddia_0308.png)

**图 3-8: 使用不可变事件日志作为真相来源**

## 总结

- **关系模型**: 适合分析、数据仓库
- **文档模型**: 适合独立 JSON 文档
- **图数据模型**: 适合多对多关系
- **事件溯源**: 适合复杂业务领域

## 图片

![](/fig/ddia_0303.png)

![](/fig/ddia_0304.png)

![](/fig/ddia_0305.png)

![](/fig/ddia_0307.png)

![](/fig/ddia_0309.png)
