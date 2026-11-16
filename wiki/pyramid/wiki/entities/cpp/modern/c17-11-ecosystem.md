---
type: entity
tags: [cpp, cpp17, ecosystem, cmake, build-tooling, sanitizers]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++ Ecosystem & Tooling

## 定义

C++ 生態系統工具用於構建、測試和維護項目。核心問題：**如何構建、測試和維護這個項目？**

## 關鍵工具

| 工具 | 用途 |
|------|------|
| **CMake** | 構建系統生成器 |
| **vcpkg / Conan** | 包管理器 |
| **clang-tidy** | 靜態分析 / Linter |
| **AddressSanitizer** | 內存錯誤檢測 |
| **ThreadSanitizer** | 數據競爭檢測 |
| **UBSan** | 未定義行為檢測 |
| **GTest** | 單元測試 |

## 關鍵要點

- **CMake**: 始終設置 `CMAKE_CXX_STANDARD_REQUIRED ON`
- **vcpkg**: 源代碼包管理，通過 manifest (vcpkg.json) 聲明依賴
- **clang-tidy**: 需要 `compile_commands.json`（`CMAKE_EXPORT_COMPILE_COMMANDS=ON`）
- **ASan**: 檢測 use-after-free、buffer overflow、double-free、stack overflow
- **TSan**: 檢測數據競爭
- **UBSan**: 檢測未定義行為（有符號整數溢出等）

## 代碼示例

```cmake
# Modern CMake: Target-Based
cmake_minimum_required(VERSION 3.14)
project(MyProject VERSION 1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(mylib STATIC src/lib.cpp src/lib.h)
target_compile_features(mylib PRIVATE cxx_std_17)
target_include_directories(mylib PUBLIC include)

add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE mylib)
```

```bash
# clang-tidy
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON .
clang-tidy src/*.cpp

# AddressSanitizer
g++ -std=c++17 -fsanitize=address -g widget.cpp -o widget

# Combined sanitizers
g++ -std=c++17 -fsanitize=address,undefined,signed-integer-overflow -g widget.cpp -o widget
```

## 常見陷阱

- **無 CMAKE_CXX_STANDARD_REQUIRED**: 標準只是請求，不強制
- **忘記 compile_commands.json**: clang-tidy 需要
- **開發時不使用 sanitizer**: ASan 應在開發時使用

## 相關概念

- [[entities/cpp/modern/m11-ecosystem]] - Master: C++ Ecosystem
- [[entities/cpp/cpp-safety]] - AddressSanitizer、UBSan 是安全工具的一部分
- [[entities/cpp/modern/c17-11-ecosystem]] - 自身交叉引用

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-11-ecosystem: CMake, vcpkg, clang-tidy, sanitizers, GTest
