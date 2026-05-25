---
type: entity
tags: [cpp, skill-creation, llm, documentation]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++ Skill Creator (AI-Driven)

## 定义

C++ Skill Creator 是用於從 cppreference、遠程文檔或本地頭文件動態生成 C++ 技能的模式。

## 核心問題

**如何為 C++20 標準庫組件、遠程第三方庫和本地 C++ 項目創建可執行的技能定義？**

## 技能創建模式

| 用戶請求 | 目標類型 | 輸入模式 |
|----------|----------|----------|
| "create ranges skill" | C++20 std feature | cppreference URL |
| "create skill from ./libs/mynetwork" | Local third-party lib | 本地文件系統路徑 |
| "create skill from https://fmt.dev" | Remote third-party lib | 用戶提供的 URL |

## 技能創建流程

1. **識別目標**: C++20 標準庫功能 / 遠程第三方庫 / 本地庫
2. **執行命令**: `/create-llms-for-skills <URL 或路徑>`
3. **生成技能**: `/create-skills-via-llms <name> <llms.txt-path> <version>`
4. **保存位置**: `~/.agent/skills/`

## 常見 C++20 技能 URL

| 功能 | URL Path |
|------|----------|
| `std::ranges::sort` | `/w/cpp/ranges/sort` |
| `std::integral` | `/w/cpp/concepts/integral` |
| `std::coroutine_handle` | `/w/cpp/coroutine/coroutine_handle` |
| `std::format` | `/w/cpp/utility/format/format` |
| `consteval`, `requires` | `/w/cpp/language/consteval` |

## 代碼示例

```bash
# C++20 ranges
/create-llms-for-skills https://en.cppreference.com/w/cpp/ranges

# Concept
/create-llms-for-skills https://en.cppreference.com/w/cpp/concepts/same_as

# 本地庫
/create-llms-for-skills --local ./libs/async_net "Focus on TCP client API"

# 生成技能
/create-skills-via-llms ranges ~/tmp/ranges-llms.txt c++20
/create-skills-via-llms mycrypto ~/tmp/crypto-llms.txt local
```

## 限制與注意事項

- 本地模式僅支持一個路徑
- 本地庫質量取決於頭文件清晰度和 Doxygen 註釋
- C++17 和 C++20 特性不要混淆（如 structured bindings 是 C++17，ranges 是 C++20）

## 相關概念

- [[entities/cpp/modern/c17-04-templates]] - C++20 Concepts 比 SFINAE 更清晰
- [[entities/cpp/modern/c17-05-type-driven]] - 類型系統技能
- [[entities/cpp/cpp20-features]] - C++20 新特性綜合頁面
- [[entities/cpp/modern/cpp-skill-creator]] - 自身交叉引用

## 來源詳情

- [[sources/cpp-modern-skills]] - cpp-skill-creator: AI-driven skill generation for C++ from docs/headers
