---
type: source
tags: [security, crypto, tls, pki, trustzone, mbedtls, books]
source-type: pdf
created: 2026-05-23
sources: [pdf-security-crypto-books]
title: "安全与密码学书籍合集（6册）"
author: "Ivan Ristić, 徐凯/崔红鹏, 帅峰云/黄腾/宋洋, 结城浩, etc."
date: 2026-05
size: large
path: raw/PDFs/books/
summary: "6册安全与密码学专业书籍：Bulletproof TLS & PKI 2nd Ed、图解密码技术 第三版、密码技术与物联网安全mbedtls、商用密码应用安全性评估考核题、手机安全与TrustZone/OP-TEE、OpenSSL Cookbook"
---

# 安全与密码学书籍合集

## 书目一览

### 1. Bulletproof TLS and PKI, 2nd Edition
- **作者**: Ivan Ristić (Feisty Duck)
- **出版**: 2022, 2nd Ed (build 1121)
- **ISBN**: 978-1907117091
- **页数**: 504
- **内容**: SSL/TLS和PKI权威指南
  - **第1章**: SSL/TLS与密码学基础（协议历史、密码学构建块、主动/被动网络攻击）
  - **第2章**: TLS 1.3深度解析（Record协议、Handshake、0-RTT、Key Schedule、Session Resumption）
  - **第3章**: TLS 1.2详解（Handshake、Key Exchange、RSA/ECDH、Renegotiation）
  - 后续章节：PKI体系、证书管理、服务器配置、攻击与防护
- **特点**: 最权威的TLS/PKI实践参考书之一
- **状态**: PDF完整文本

### 2. 图解密码技术 第三版
- **作者**: 结城浩
- **出版**: 第三版
- **页数**: 426
- **内容**: 图解化讲解对称加密（AES）、公钥加密（RSA/ECC）、哈希函数（SHA）、数字签名、证书（PKI/X.509）、TLS/SSL协议
- **特点**: 以大量插图和通俗语言讲解密码学原理，适合入门
- **状态**: 图片扫描版，无可提取文本（已在旧源 pdf-crypto-books 中引用）

### 3. 密码技术与物联网安全：mbedtls开发实战
- **作者**: 徐凯, 崔红鹏
- **出版**: 机械工业出版社, 2019
- **ISBN**: 978-7-111-62001-3
- **页数**: 707
- **内容**: 
  - **第1章**: 物联网安全概述（mbedtls简介、OpenSSL简介）
  - **第2章**: mbedtls入门（体系结构、CMake安装、Zephyr OS示例）
  - **第3章**: 数论基础（素数、模运算、群、域、欧拉函数）
  - 后续章节：对称加密、公钥加密、哈希、TLS/DTLS协议、X.509证书、安全实践
- **特点**: 理论与实践结合，基于mbedtls库的物联网安全开发实战
- **状态**: PDF完整文本

### 4. 商用密码应用安全性评估考核题
- **出版**: 中国商用密码检测中心
- **页数**: 622
- **内容**: 商用密码应用安全性评估从业人员考核题库（含党的二十大相关时政题）
- **题型**: 单项选择题、多项选择题，覆盖密码算法、密钥管理、密码产品测评等
- **用途**: 商用密码应用安全性评估（密评）从业人员考试备考
- **状态**: PDF完整文本

### 5. 手机安全和可信应用开发指南：TrustZone与OP-TEE技术详解
- **作者**: 帅峰云, 黄腾, 宋洋
- **出版**: 机械工业出版社, 2018
- **ISBN**: 978-7-111-60956-8
- **页数**: 786
- **内容**: 
  - **第一篇 基础技术篇**: TEE概念、ARM TrustZone技术（ARMv7/v8架构、AXI安全扩展、TZASC/TZMA/TZPC）、ARM可信固件ATF
  - **第二篇 系统集成篇**: QEMU运行OP-TEE启动过程、安全引导与ATF启动（bl1/bl2/bl31/bl32）
- **特点**: 全面讲解TrustZone硬件安全扩展和OP-TEE开源TEE实现
- **状态**: PDF完整文本

### 6. OpenSSL Cookbook 中文版
- **作者**: Ivan Ristić（李振宇译）
- **出版**: 人民邮电出版社
- **页数**: 72
- **内容**: 
  - **第1章**: OpenSSL常规任务（密钥生成、CSR、自签名证书、私有CA搭建、密码套件选择）
  - **第2章**: 使用OpenSSL进行测试（SSL连接测试、协议版本检测、密码套件测试、OCSP/CRL检查、BEAST/Heartbleed漏洞测试）
- **特点**: 精炼实用的OpenSSL操作手册
- **状态**: PDF完整文本

## 相关页面

- [[sources/pdf-crypto-books]] — 旧源（已合并至此新源）
- [[kernel-subsystems-index]] — 内核密码学子系统
- [[entities/security]] — 安全工具
- [[entities/cpp/raii]] — RAII资源管理
- [[sys-prog-index]] — 系统编程导航
