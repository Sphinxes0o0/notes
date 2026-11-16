---
type: entity
tags: [C++异步框架, MySQL, 异步数据库, 事务]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 12: MySQL CLI

## 概述
`tutorial-12-mysql_cli` 展示如何使用 Workflow 的异步 MySQL 客户端。

## MySQL URL
- `mysql://user:password@host:port/dbname?charset=utf8`
- `mysqls://` 用于 SSL 连接

## 创建任务
~~~cpp
WFMySQLTask *task = WFTaskFactory::create_mysql_task(url, retry_max, callback);
task->get_req()->set_query("SELECT * FROM table1;");
task->start();
~~~

## 结果解析
使用 `MySQLResultCursor` 遍历结果集：
~~~cpp
MySQLResultCursor cursor(task->get_resp());
if (cursor.get_cursor_status() == MYSQL_STATUS_GET_RESULT) {
    const MySQLField *const *fields = cursor.fetch_fields();
    std::vector<std::vector<MySQLCell>> rows;
    cursor.fetch_all(rows);
}
~~~

## 事务连接
`WFMySQLConnection` 保证独占连接：
~~~cpp
WFMySQLConnection conn(1);
conn.init("mysql://root@127.0.0.1/test");
WFMySQLTask *t1 = conn.create_query_task("BEGIN;", callback);
WFMySQLTask *t2 = conn.create_query_task("SELECT * FROM t FOR UPDATE;", callback);
(*t1 > t2 > t3 > t4 > t5).start();  // 任务链自动串行
~~~

## 预处理
~~~cpp
conn.create_prepare_task("SELECT * FROM t WHERE id=?", callback);
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端总览
- [[entities/cpp/workflow/workflow-async-model]] — 异步模型