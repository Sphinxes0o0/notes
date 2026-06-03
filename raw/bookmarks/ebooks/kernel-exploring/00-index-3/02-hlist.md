# 哈希表

内核中的哈希表采用的是链式冲突解决方法。

## 整体的样子

```
  hlist_head
  +--------+
  |        | -> hlist_node -> hlist_node -> hlist_node
  +--------+
  |        | -> hlist_node -> hlist_node -> hlist_node
  +--------+
  |        | -> hlist_node -> hlist_node -> hlist_node
  +--------+
```

一个hash table是由多个hlist_head组成的，根据hash算法，会计算出对应的key到哪个bucket。

而每个bucket是一个以hlist_head为首，hlist_node为元素的链表。

## hlist_head链表

```

  hlist_head    hlist_node      hlist_node
  +--------+    +----------+    +----------+
  |        | +--|--pprev   | +--|--pprev   |
  |        | |  |          | |  |          |
  |  +-----|-+  |  +-------|-+  |          |
  |  |     |    |  |       |    |          |
  |  v     |    |  v       |    |          |
  |first --|--> |  next  --|--> |  next    |
  +--------+    +----------+    +----------+

```

仔细一看也算是个双向链表，不过pprev是指针的指针。

## 常用API

---

# Agent Instructions: Querying This Documentation

If you need additional information that is not directly available in this page, you can query the documentation dynamically by asking a question.

Perform an HTTP GET request on the current page URL with the `ask` query parameter:

```
GET https://richardweiyang-2.gitbook.io/kernel-exploring/00-index-3/02-hlist.md?ask=<question>
```

The question should be specific, self-contained, and written in natural language.
The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.