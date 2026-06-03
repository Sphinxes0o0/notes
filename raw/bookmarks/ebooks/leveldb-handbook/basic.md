# 基本概念

leveldb是一个写性能十分优秀的存储引擎，是典型的LSM树(Log Structured-Merge Tree)实现。

## 整体架构

leveldb中主要由以下几个重要的部件构成：
- memtable
- immutable memtable
- log(journal)
- sstable
- manifest
- current

### memtable

memtable就是一个在内存中进行数据组织与维护的结构。memtable底层使用了一种跳表数据结构。

### immutable memtable

memtable的容量到达阈值时，便会转换成一个不可修改的memtable。当immutable memtable被创建时，leveldb后台压缩进程会将内容创建sstable。

### log

leveldb在写内存之前会首先将所有的写操作写到日志文件中。日志的写操作都是一次顺序写，因此写效率高。

### sstable

leveldb的数据主要通过sstable进行存储。后台会整合这些sstable文件，该过程也称为compaction。sstable文件在逻辑上被分成若干层。

### manifest

manifest文件用来记录versionEdit信息。当compaction完成时，leveldb会创建一个新的version。

### current

这个文件的内容只有一个信息，就是记载当前的manifest文件名。

## 图片

- ![整体架构](https://leveldb-handbook.readthedocs.io/zh/latest/_images/leveldb_arch.jpeg)
- ![manifest](https://leveldb-handbook.readthedocs.io/zh/latest/_images/manifest.jpeg)
