---
type: entity
tags: [C++异步框架, MySQL客户端, 数据库, 异步]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 12: mysql_cli 异步 MySQL 客户端

## 定义
命令行交互式异步 MySQL 客户端。

## MySQL URL 格式
~~~bash
mysql://username:password@host:port/dbname?character_set=utf8
mysqls://...  # SSL 连接
~~~

## 创建 MySQL 任务
~~~cpp
WFMySQLTask *task = WFTaskFactory::create_mysql_task(url, RETRY_MAX, callback);
task->get_req()->set_query("SELECT * FROM table1;");
task->start();
~~~

## 支持的命令
- COM_QUERY：增删改查、建库建表、预处理、事务
- 多条语句可拼接执行
- 不支持 USE 命令（用 db_name.table_name）

## 结果解析
~~~cpp
MySQLResultCursor cursor(task->get_resp());
do {
    if (cursor.get_cursor_status() == MYSQL_STATUS_GET_RESULT) {
        // SELECT 结果
        const MySQLField *const *fields = cursor.fetch_fields();
        std::vector<std::vector<MySQLCell>> rows;
        cursor.fetch_all(rows);
    } else if (...) {
        // INSERT/UPDATE 结果
        cursor.get_affected_rows();
        cursor.get_insert_id();
    }
} while (cursor.next_result_set());
~~~

## 事务连接（WFMySQLConnection）
~~~cpp
WFMySQLConnection conn(id);
conn.init(url);
WFMySQLTask *t1 = conn.create_query_task("BEGIN;", callback);
WFMySQLTask *t2 = conn.create_query_task("SELECT ... FOR UPDATE;", callback);
(*t1 > t2 > t3 > t4).start();
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-error-handling]] — 错误处理