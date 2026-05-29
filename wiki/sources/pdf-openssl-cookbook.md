---
type: source
source-type: pdf
title: OpenSSL Cookbook 中文版
author: Ivan Ristić (李振宇译)
date: 2015
size: small
path: raw/PDFs/books/openssl-cookbook-中文版.pdf
summary: Ivan Ristić OpenSSL Cookbook：密钥生成/证书管理/CA搭建/SSL测试实用手册，72页精炼指南
tags: [security, openssl, tls, pki, certificates, books]
created: 2015
---
# OpenSSL Cookbook 中文版

## 核心内容

**Author:** Ivan Ristić (Feisty Duck) | 译：李振宇 | 人民邮电出版社 | 72页

### OpenSSL的江湖地位

> "OpenSSL虽然有很多缺点，但依旧是最成功、最重要的开源项目之一。大部分互联网基础设施的安全都依赖于它。"

### 第1章：常规任务

**密钥生成：**
```bash
openssl genrsa -out server.key 2048
openssl rsa -in server.key -pubout -out server.pub
```

**证书操作：**
- CSR生成与自签名证书
- 私有CA搭建（创建根CA + 中间CA）
- 密码套件选择与配置

### 第2章：测试

**SSL Labs测试项目：**
- SSL连接测试：`openssl s_client -connect host:443`
- 协议版本检测：`openssl s_server`
- 密码套件枚举
- OCSP/CRL检查
- 漏洞测试：BEAST/Heartbleed/ROBOT

### 与《Bulletproof TLS and PKI》关系

本手册是《Bulletproof TLS and PKI》的精华版，面向需要快速上手的实践者。

## 相关页面
- [[sources/pdf-security-crypto-books]] — 安全密码学书籍合集
- [[entities/linux/kernel/index]] — 内核密码学子系统
- [[entities/linux/security/linux-security-observability-ebpf]] — 安全监控
- [[sys-prog-index]] — 系统编程