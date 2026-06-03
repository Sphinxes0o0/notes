# 第十一章：批处理

> 带有太强个人色彩的系统无法成功。

## 使用 Unix 工具的批处理

```bash
cat /var/log/nginx/access.log |
  awk '{print $7}' |
  sort |
  uniq -c |
  sort -r -n |
  head -n 5
```

## 分布式系统中的批处理

### 分布式文件系统

HDFS 等将文件分成块，分散到多台机器。

### MapReduce

1. 读取输入文件并切分为记录
2. 调用 mapper 提取键和值
3. 按键排序
4. 调用 reducer

### 数据流引擎

Spark 和 Flink 解决了 MapReduce 的局限性。

## 批处理用例

### ETL

批处理天然适合数据转换。

### 分析

OLAP 查询扫描大量记录并做分组聚合。

### 机器学习

特征工程、模型训练、批量推理。

## 图片

![](/fig/ddia_1101.png)

![](/fig/ddia_1102.png)

![](/fig/ddia_1103.png)
