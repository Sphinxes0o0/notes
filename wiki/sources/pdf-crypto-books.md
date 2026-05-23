---
type: source
tags: [crypto, openssl, tls, security]
source-type: pdf
created: 2026-05-23
sources: [pdf-crypto-books]
title: "OpenSSL Cookbook 中文版 / 图解密码技术 第三版"
author: "Ivan Ristić; 结城浩"
date: 2024
size: medium
path: raw/github/notes/resources/docs/cpp/openssl-cookbook-中文版.pdf, raw/github/notes/resources/docs/cpp/图解密码技术 第三版.pdf
summary: "两册密码学书籍：OpenSSL Cookbook（密钥生成、证书管理、服务器安全测试）和 图解密码技术 第三版（公钥加密、数字签名、证书、TLS/SSL 图解）"
---

# OpenSSL Cookbook & 密码学

## OpenSSL Cookbook

### 核心内容

OpenSSL 是最重要、最广泛使用的开源加密库之一，几乎所有互联网基础设施的安全都依赖它。

**第 1 章：常规任务**
- 密钥与证书生成
- CA 创建与管理（开发/内网环境）
- 为依赖 SSL/TLS 的程序配置 OpenSSL

**第 2 章：服务器安全测试**
- 使用 OpenSSL 测试服务器安全配置
- 密码套件评估
- TLS 版本兼容性测试

## 图解密码技术 第三版

> 注意：此 PDF 为图片扫描版，以下为基于主题的推断。

涵盖对称加密（AES）、公钥加密（RSA/ECC）、哈希函数（SHA）、数字签名、证书（PKI/X.509）、TLS/SSL 协议的图解化说明。

## 相关页面

- [[kernel-subsystems-index]] — 内核密码学子系统
- [[entities/cpp/raii]] — RAII 资源管理
- [[entities/security/commercial-cryptography]] — 国密算法 SM2/SM3/SM4 与商用密码评估
- [[sys-prog-index]] — 系统编程导航
