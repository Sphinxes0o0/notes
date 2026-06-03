# 版本控制

Leveldb每次新生成sstable文件，或者删除sstable文件，都会从一个版本升级成另外一个版本。版本控制对于leveldb来说至关重要，是保障数据正确性的重要机制。

## Manifest

manifest文件专用于记录版本信息。leveldb采用了增量式的存储方式，记录每一个版本相较于上一个版本的变化情况。一个Manifest文件中，包含了多条Session Record。一个Session Record记录了从上一个版本至该版本的变化情况。

## Commit

每当完成一次major compaction或者通过minor compaction新生成0层文件，都会触发leveldb进行版本升级。

## Recover

数据库每次启动时，都会利用Manifest信息重新构建最新的version。

## Current

current文件用于指示当前系统使用的manifest文件名。

## 异常处理

当leveldb的manifest文件丢失时，leveldb提供了Repairer接口供用户进行版本信息恢复。

## 多版本并发控制

leveldb采用MVCC避免读写冲突，确保读写操作可以针对相应版本文件进行。

## 图片

- ![Manifest详情](https://leveldb-handbook.readthedocs.io/zh/latest/_images/manifest_detail.jpeg)
- ![版本更新](https://leveldb-handbook.readthedocs.io/zh/latest/_images/version_update.jpeg)
- ![版本恢复](https://leveldb-handbook.readthedocs.io/zh/latest/_images/version_recover.jpeg)
