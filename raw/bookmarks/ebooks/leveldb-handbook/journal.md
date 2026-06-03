# LevelDB 日志系统

## 概述

LevelDB 在写内存之前会将本次写操作的内容写入日志文件，以防止数据因进程异常或系统掉电而丢失。系统包含两个 memory db 及对应的两份日志文件，当可读写 db 的数据量超过上限时，会转换为不可写的 memory db，与其对应的日志文件变为 frozen log。Immutable memory db 由后台 minor compaction 进程转换为 sstable 文件持久化。

## 日志结构

日志文件按 block 划分，每个 block 大小为 32KiB，包含若干完整 chunk。每条日志记录包含一个或多个 chunk，每个 chunk 包含 7 字节 header：前 4 字节为校验码，接着 2 字节为数据长度，最后 1 字节为 chunk 类型。

**四种 chunk 类型**：full（单条记录）、first（多条记录首部）、middle（中间部分）、last（尾部）。

## 日志内容

日志内容为写入的 batch 编码后的信息，包含 Header（sequence number、put/del 操作个数）和 Data（batch 编码内容）。

## 日志写

LevelDB 内部实现 journal writer。调用 Next 函数获取 singleWriter 写入单条记录。当 buffer 超过 32KiB 时，计算 header 并写入文件，然后 reset buffer 开始新 chunk。大型记录可能跨越多个 block 存储。

## 日志读

日志读取按 32KiB block 进行块读取。Reader 调用 Next 返回 singleReader，每次 Read 返回一个 chunk。读取时检查校验码、数据类型、长度等，若不正确根据用户设置返回错误或丢弃数据。循环读取直至遇到 Last 类型的 chunk。

## 图片

- ![双日志](https://leveldb-handbook.readthedocs.io/zh/latest/_images/two_log.jpeg)
- ![日志结构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/journal.jpeg)
- ![日志内容](https://leveldb-handbook.readthedocs.io/zh/latest/_images/journal_content.jpeg)
- ![日志写](https://leveldb-handbook.readthedocs.io/zh/latest/_images/journal_write.jpeg)
- ![日志读](https://leveldb-handbook.readthedocs.io/zh/latest/_images/journal_read.jpeg)
