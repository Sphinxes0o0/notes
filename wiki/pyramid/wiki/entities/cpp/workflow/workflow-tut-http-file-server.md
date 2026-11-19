---
type: entity
tags: [C++异步框架, 文件IO, 异步文件, Linux aio]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 09: http_file_server 异步文件 IO

## 定义
展示如何使用异步文件 IO 任务创建 HTTP 文件服务器。

## 读文件任务
~~~cpp
int fd = open(path, O_RDONLY);
size_t size = lseek(fd, 0, SEEK_END);
void *buf = malloc(size);

WFFileIOTask *pread_task = WFTaskFactory::create_pread_task(
    fd, buf, size, 0, pread_callback);
series_of(server_task)->push_back(pread_task);
~~~

## 文件 IO 接口
| 接口 | 说明 |
|------|------|
| create_pread_task | 读文件（fd 或路径） |
| create_pwrite_task | 写文件 |
| create_preadv_task | 分散读 |
| create_pwritev_task | 聚集写 |
| create_fsync_task | fsync |
| create_fdatasync_task | fdatasync |

## 处理读文件结果
~~~cpp
void pread_callback(WFFileIOTask *task) {
    FileIOArgs *args = task->get_args();
    long ret = task->get_retval();  // 读取字节数或 -1
    close(args->fd);
    resp->append_output_body_nocopy(args->buf, ret);
}
~~~

## 异步 IO 实现
- Linux：使用 Linux aio，CPU 占用少
- 其他 Unix/macOS：使用多线程模拟
- 不适合传输大文件（需全部读入内存）

## Repeater 循环输入
~~~cpp
WFRepeaterTask *repeater = WFTaskFactory::create_repeater_task(create, callback);
// create 返回 NULL 时循环结束
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-http-server]] — HTTP 服务器
- [[entities/cpp/workflow/workflow-compute-tasks]] — 计算任务