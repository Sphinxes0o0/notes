---
type: source
source-type: github
title: "Linux Kernel Crypto Subsystem Notes"
author: "notes repo"
date: 2026-05-20
size: small
path: raw/github/notes/crypto/linux_kernel/
summary: "Linux内核密码学子系统：crypto_alg注册、skcipher、aead、ahash、模板机制"
tags: [linux-kernel, cryptography]
created: 2026-05-20
---

# Linux Kernel Crypto Subsystem Notes

## 来源信息

- **路径**: raw/github/notes/crypto/linux_kernel/
- **文件数**: 5个文档（index + 4个分析文档）
- **类型**: 内核源码分析笔记

## 核心内容

- **crypto_core.md**: 核心框架、crypto_alg结构、crypto_tfm、算法注册
- **crypto_skcipher.md**: 同步加密接口、ablkcipher、AES/DES
- **crypto_async.md**: 异步加密、AEAD、AHASH、SHA/GCM
- **crypto_infra.md**: algapi、cryptd、随机数、压缩

## 关键概念

- crypto_larval: 幼虫状态延迟自测机制
- Template模板: cbc(aes)等组合算法
- 同步/异步: blocking vs callback

## 相关页面
- [[entities/linux/kernel/crypto/linux-kernel-crypto-core]]
