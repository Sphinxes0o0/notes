# 单例模式 (Singleton Pattern) - C/C++ 实现详解

## 1. 什么是单例模式

单例模式(Singleton Pattern)是一种创建型设计模式，它确保一个类只有一个实例，并提供一个全局访问点来获取这个实例。

### 核心特点：
- **唯一性**：整个程序生命周期中只能存在一个实例
- **全局访问**：提供全局访问点
- **延迟初始化**：通常在第一次使用时才创建实例
- **自我管理**：类自己负责创建和管理自己的唯一实例

## 2. 应用场景

- **配置管理器**：全局配置信息管理
- **日志记录器**：统一的日志管理
- **数据库连接池**：管理数据库连接
- **线程池**：管理线程资源
- **设备驱动管理**：硬件设备的唯一访问接口
- **缓存管理**：全局缓存系统

## 3. C语言实现

### 3.1 基础实现

```c
#include <stdio.h>
#include <stdlib.h>

// 单例结构体
typedef struct {
    int data;
    char name[50];
} Singleton;

// 静态实例指针
static Singleton* instance = NULL;

// 获取单例实例
Singleton* getInstance() {
    if (instance == NULL) {
        instance = (Singleton*)malloc(sizeof(Singleton));
        if (instance != NULL) {
            instance->data = 0;
            snprintf(instance->name, sizeof(instance->name), "Singleton Instance");
        }
    }
    return instance;
}

// 销毁单例
void destroySingleton() {
    if (instance != NULL) {
        free(instance);
        instance = NULL;
    }
}

// 使用示例
int main() {
    Singleton* s1 = getInstance();
    Singleton* s2 = getInstance();
    
    printf("s1 address: %p\n", (void*)s1);
    printf("s2 address: %p\n", (void*)s2);
    printf("Same instance: %s\n", (s1 == s2) ? "Yes" : "No");
    
    destroySingleton();
    return 0;
}
```

### 3.2 线程安全的C实现

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

typedef struct {
    int data;
    char name[50];
} Singleton;

static Singleton* instance = NULL;
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// 线程安全的获取实例
Singleton* getInstance() {
    if (instance == NULL) {
        pthread_mutex_lock(&mutex);
        if (instance == NULL) {  // 双重检查锁定
            instance = (Singleton*)malloc(sizeof(Singleton));
            if (instance != NULL) {
                instance->data = 0;
                snprintf(instance->name, sizeof(instance->name), "Thread-Safe Singleton");
            }
        }
        pthread_mutex_unlock(&mutex);
    }
    return instance;
}

void destroySingleton() {
    pthread_mutex_lock(&mutex);
    if (instance != NULL) {
        free(instance);
        instance = NULL;
    }
    pthread_mutex_unlock(&mutex);
}
```

## 4. C++实现

### 4.1 经典饿汉式 (Eager Initialization)

```cpp
#include <iostream>
#include <string>

class Singleton {
private:
    static Singleton* instance;
    int data;
    std::string name;
    
    // 私有构造函数
    Singleton() : data(0), name("Singleton Instance") {
        std::cout << "Singleton instance created" << std::endl;
    }
    
    // 防止拷贝构造和赋值
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;

public:
    static Singleton* getInstance() {
        return instance;
    }
    
    void setData(int value) { data = value; }
    int getData() const { return data; }
    const std::string& getName() const { return name; }
    
    ~Singleton() {
        std::cout << "Singleton instance destroyed" << std::endl;
    }
};

// 静态成员初始化
Singleton* Singleton::instance = new Singleton();
```

### 4.2 懒汉式 (Lazy Initialization)

```cpp
#include <iostream>
#include <mutex>

class LazySingleton {
private:
    static LazySingleton* instance;
    static std::mutex mtx;
    int data;
    
    LazySingleton() : data(0) {
        std::cout << "LazySingleton instance created" << std::endl;
    }
    
    LazySingleton(const LazySingleton&) = delete;
    LazySingleton& operator=(const LazySingleton&) = delete;

public:
    static LazySingleton* getInstance() {
        if (instance == nullptr) {
            std::lock_guard<std::mutex> lock(mtx);
            if (instance == nullptr) {  // 双重检查锁定
                instance = new LazySingleton();
            }
        }
        return instance;
    }
    
    void setData(int value) { data = value; }
    int getData() const { return data; }
    
    static void destroy() {
        std::lock_guard<std::mutex> lock(mtx);
        delete instance;
        instance = nullptr;
    }
};

// 静态成员初始化
LazySingleton* LazySingleton::instance = nullptr;
std::mutex LazySingleton::mtx;
```

### 4.3 Meyer's Singleton (推荐)

```cpp
#include <iostream>

class MeyersSingleton {
private:
    int data;
    
    MeyersSingleton() : data(0) {
        std::cout << "MeyersSingleton instance created" << std::endl;
    }
    
    MeyersSingleton(const MeyersSingleton&) = delete;
    MeyersSingleton& operator=(const MeyersSingleton&) = delete;

public:
    static MeyersSingleton& getInstance() {
        static MeyersSingleton instance;  // C++11保证线程安全
        return instance;
    }
    
    void setData(int value) { data = value; }
    int getData() const { return data; }
    
    ~MeyersSingleton() {
        std::cout << "MeyersSingleton instance destroyed" << std::endl;
    }
};
```

### 4.4 模板化单例基类

```cpp
#include <iostream>
#include <mutex>

template<typename T>
class SingletonBase {
protected:
    SingletonBase() = default;
    virtual ~SingletonBase() = default;
    
    SingletonBase(const SingletonBase&) = delete;
    SingletonBase& operator=(const SingletonBase&) = delete;

public:
    static T& getInstance() {
        static T instance;
        return instance;
    }
};

// 使用示例
class Logger : public SingletonBase<Logger> {
    friend class SingletonBase<Logger>;
    
private:
    Logger() = default;
    
public:
    void log(const std::string& message) {
        std::cout << "[LOG]: " << message << std::endl;
    }
};

class ConfigManager : public SingletonBase<ConfigManager> {
    friend class SingletonBase<ConfigManager>;
    
private:
    std::string configPath;
    ConfigManager() : configPath("/etc/config.ini") {}
    
public:
    void setConfigPath(const std::string& path) {
        configPath = path;
    }
    
    const std::string& getConfigPath() const {
        return configPath;
    }
};
```

## 5. 线程安全分析

### 5.1 问题场景
```cpp
// 非线程安全的懒汉式实现
class UnsafeSingleton {
private:
    static UnsafeSingleton* instance;
    UnsafeSingleton() {}

public:
    static UnsafeSingleton* getInstance() {
        if (instance == nullptr) {           // 检查点1
            instance = new UnsafeSingleton(); // 创建点
        }
        return instance;                     // 返回点
    }
};
```

**问题**：多线程环境下，可能创建多个实例。

### 5.2 解决方案对比

| 方案 | 优点 | 缺点 | 线程安全 |
|------|------|------|----------|
| 饿汉式 | 简单，天然线程安全 | 程序启动时就创建，可能浪费内存 | ✅ |
| 懒汉式+互斥锁 | 延迟创建，线程安全 | 性能开销，每次访问都要检查锁 | ✅ |
| 双重检查锁定 | 性能较好的线程安全 | 实现复杂，需要注意内存序 | ✅ |
| Meyer's Singleton | 简洁，C++11保证线程安全 | 依赖编译器实现 | ✅ |

## 6. 内存管理注意事项

### 6.1 资源释放
```cpp
class ResourceManagedSingleton {
private:
    static ResourceManagedSingleton* instance;
    static std::once_flag initFlag;
    
    ResourceManagedSingleton() {
        // 初始化资源
    }
    
    ~ResourceManagedSingleton() {
        // 清理资源
    }

public:
    static ResourceManagedSingleton* getInstance() {
        std::call_once(initFlag, []() {
            instance = new ResourceManagedSingleton();
            // 注册程序退出时的清理函数
            std::atexit(cleanup);
        });
        return instance;
    }
    
private:
    static void cleanup() {
        delete instance;
        instance = nullptr;
    }
};

ResourceManagedSingleton* ResourceManagedSingleton::instance = nullptr;
std::once_flag ResourceManagedSingleton::initFlag;
```

### 6.2 RAII管理
```cpp
#include <memory>

class SmartSingleton {
private:
    static std::unique_ptr<SmartSingleton> instance;
    static std::once_flag initFlag;
    
    SmartSingleton() = default;

public:
    static SmartSingleton* getInstance() {
        std::call_once(initFlag, []() {
            instance = std::make_unique<SmartSingleton>();
        });
        return instance.get();
    }
    
    SmartSingleton(const SmartSingleton&) = delete;
    SmartSingleton& operator=(const SmartSingleton&) = delete;
};

std::unique_ptr<SmartSingleton> SmartSingleton::instance = nullptr;
std::once_flag SmartSingleton::initFlag;
```

## 7. 实际应用示例

### 7.1 日志管理器
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <mutex>
#include <chrono>
#include <iomanip>

class Logger {
private:
    std::ofstream logFile;
    std::mutex logMutex;
    
    Logger() {
        logFile.open("application.log", std::ios::app);
    }
    
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

public:
    static Logger& getInstance() {
        static Logger instance;
        return instance;
    }
    
    void log(const std::string& level, const std::string& message) {
        std::lock_guard<std::mutex> lock(logMutex);
        
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        
        logFile << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
                << " [" << level << "] " << message << std::endl;
        logFile.flush();
    }
    
    void info(const std::string& message) { log("INFO", message); }
    void warning(const std::string& message) { log("WARNING", message); }
    void error(const std::string& message) { log("ERROR", message); }
    
    ~Logger() {
        if (logFile.is_open()) {
            logFile.close();
        }
    }
};
```

### 7.2 配置管理器
```cpp
#include <unordered_map>
#include <string>
#include <fstream>
#include <sstream>

class ConfigManager {
private:
    std::unordered_map<std::string, std::string> configs;
    
    ConfigManager() {
        loadConfig("config.ini");
    }
    
    void loadConfig(const std::string& filename) {
        std::ifstream file(filename);
        std::string line;
        
        while (std::getline(file, line)) {
            if (line.empty() || line[0] == '#') continue;
            
            size_t pos = line.find('=');
            if (pos != std::string::npos) {
                std::string key = line.substr(0, pos);
                std::string value = line.substr(pos + 1);
                configs[key] = value;
            }
        }
    }

public:
    static ConfigManager& getInstance() {
        static ConfigManager instance;
        return instance;
    }
    
    std::string get(const std::string& key, const std::string& defaultValue = "") const {
        auto it = configs.find(key);
        return (it != configs.end()) ? it->second : defaultValue;
    }
    
    void set(const std::string& key, const std::string& value) {
        configs[key] = value;
    }
    
    int getInt(const std::string& key, int defaultValue = 0) const {
        std::string value = get(key);
        return value.empty() ? defaultValue : std::stoi(value);
    }
    
    ConfigManager(const ConfigManager&) = delete;
    ConfigManager& operator=(const ConfigManager&) = delete;
};
```

## 8. 优缺点分析

### 优点
- **全局唯一性**：确保系统中只有一个实例
- **全局访问点**：提供统一的访问接口
- **资源控制**：有效控制共享资源的访问
- **延迟初始化**：可以推迟昂贵对象的创建

### 缺点
- **违反单一职责原则**：类既要管理自己的业务逻辑，又要管理实例创建
- **隐藏依赖关系**：使用全局访问点可能隐藏类之间的依赖
- **测试困难**：难以进行单元测试，特别是mock和stub
- **并发问题**：需要特别注意线程安全
- **内存泄漏风险**：如果不正确管理，可能导致内存泄漏

## 9. 最佳实践

### 9.1 选择合适的实现方式
```cpp
// 推荐：使用Meyer's Singleton
class RecommendedSingleton {
public:
    static RecommendedSingleton& getInstance() {
        static RecommendedSingleton instance;
        return instance;
    }
    
    // 业务方法
    void doSomething() { /* ... */ }
    
private:
    RecommendedSingleton() = default;
    RecommendedSingleton(const RecommendedSingleton&) = delete;
    RecommendedSingleton& operator=(const RecommendedSingleton&) = delete;
};
```

### 9.2 考虑依赖注入替代方案
```cpp
// 考虑使用依赖注入而不是单例
class Service {
private:
    Logger& logger;
    ConfigManager& config;

public:
    Service(Logger& l, ConfigManager& c) : logger(l), config(c) {}
    
    void doWork() {
        std::string setting = config.get("some_setting");
        logger.info("Doing work with setting: " + setting);
    }
};
```

### 9.3 总结建议

1. **优先考虑依赖注入**：在可能的情况下，优先使用依赖注入而不是单例模式
2. **使用Meyer's Singleton**：在C++中推荐使用Meyer's Singleton实现
3. **明确生命周期**：确保单例对象的生命周期管理正确
4. **避免过度使用**：不要将单例模式用作全局变量的替代品
5. **考虑线程安全**：在多线程环境中务必考虑线程安全性
6. **提供清理机制**：为单例对象提供适当的资源清理机制

单例模式是一个强大但需要谨慎使用的设计模式。正确实现可以有效管理全局资源，但过度使用可能导致代码耦合度过高和测试困难。在使用时应该仔细权衡其优缺点，选择最适合具体场景的实现方式。
