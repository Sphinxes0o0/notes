---
title: "Snort 3 · 附录 HH–HQ"
description: "附录HH： 位操作工具 — 附录HQ： 信号处理"
---

# Snort 3 · 附录 HH–HQ

[返回总目录](../snort3_architecture_analysis)

## 附录HH： 位操作工具 {#附录hh-位操作工具}

### HH.1 位操作 {#hh-1-位操作}

```cpp
// utils/bit_ops.h

class BitOps {
public:
    // 计算比特数
    static int popcount(uint32_t x) {
        return __builtin_popcount(x);
    }
    
    static int popcount(uint64_t x) {
        return __builtin_popcountll(x);
    }
    
    // 计算前导零
    static int clz(uint32_t x) {
        return __builtin_clz(x);
    }
    
    static int clz(uint64_t x) {
        return __builtin_clzll(x);
    }
    
    // 计算尾随零
    static int ctz(uint32_t x) {
        return __builtin_ctz(x);
    }
    
    // 循环左移
    static uint32_t rotl(uint32_t x, int8_t r) {
        return (x << r) | (x >> (32 - r));
    }
    
    static uint64_t rotl(uint64_t x, int8_t r) {
        return (x << r) | (x >> (64 - r));
    }
    
    // 字节序转换
    static uint16_t bswap16(uint16_t x) {
        return __builtin_bswap16(x);
    }
    
    static uint32_t bswap32(uint32_t x) {
        return __builtin_bswap32(x);
    }
    
    static uint64_t bswap64(uint64_t x) {
        return __builtin_bswap64(x);
    }
    
    // 网络字节序转换
    static uint16_t htons(uint16_t x) { return bswap16(x); }
    static uint32_t htonl(uint32_t x) { return bswap32(x); }
    static uint64_t htonll(uint64_t x) { return bswap64(x); }
    
    // 获取字段
    static uint32_t get_field(uint32_t value, uint8_t pos, uint8_t width) {
        uint32_t mask = ((1 << width) - 1) << pos;
        return (value & mask) >> pos;
    }
    
    // 设置字段
    static uint32_t set_field(uint32_t value, uint8_t pos, uint8_t width, uint32_t field) {
        uint32_t mask = ((1 << width) - 1) << pos;
        return (value & ~mask) | ((field << pos) & mask);
    }
};
```

---

## 附录HI： 文件操作 {#附录hi-文件操作}

### HI.1 文件工具 {#hi-1-文件工具}

```cpp
// utils/file_utils.h

class FileUtils {
public:
    // 读取整个文件
    static std::string read_file(const char* path) {
        std::ifstream file(path, std::ios::binary);
        if (!file)
            return "";
        
        std::string content((std::istreambuf_iterator<char>(file)),
                            std::istreambuf_iterator<char>());
        return content;
    }
    
    // 写入文件
    static bool write_file(const char* path, const std::string& content) {
        std::ofstream file(path, std::ios::binary);
        if (!file)
            return false;
        
        file.write(content.data(), content.size());
        return file.good();
    }
    
    // 追加文件
    static bool append_file(const char* path, const std::string& content) {
        std::ofstream file(path, std::ios::app | std::ios::binary);
        if (!file)
            return false;
        
        file.write(content.data(), content.size());
        return file.good();
    }
    
    // 文件大小
    static size_t file_size(const char* path) {
        struct stat st;
        if (stat(path, &st) < 0)
            return 0;
        return st.st_size;
    }
    
    // 文件存在
    static bool exists(const char* path) {
        return access(path, F_OK) == 0;
    }
    
    // 创建目录
    static bool mkdir(const char* path, mode_t mode = 0755) {
        return ::mkdir(path, mode) == 0 || errno == EEXIST;
    }
    
    // 递归创建目录
    static bool mkdir_p(const char* path) {
        std::string p = path;
        for (size_t i = 1; i < p.size(); i++) {
            if (p[i] == '/') {
                p[i] = '\0';
                mkdir(p.c_str());
                p[i] = '/';
            }
        }
        return mkdir(p.c_str());
    }
    
    // 目录列表
    static std::vector<std::string> list_dir(const char* path) {
        std::vector<std::string> files;
        DIR* dir = opendir(path);
        
        if (!dir)
            return files;
        
        struct dirent* entry;
        while ((entry = readdir(dir)) != nullptr) {
            if (strcmp(entry->d_name, ".") != 0 && 
                strcmp(entry->d_name, "..") != 0) {
                files.push_back(entry->d_name);
            }
        }
        
        closedir(dir);
        return files;
    }
};
```

---

## 附录HJ： 并发工具 {#附录hj-并发工具}

### HJ.1 线程池 {#hj-1-线程池}

```cpp
// utils/thread_pool.h

class ThreadPool {
public:
    explicit ThreadPool(size_t num_threads) : stop_(false) {
        for (size_t i = 0; i < num_threads; i++) {
            workers_.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    
                    {
                        std::unique_lock<std::mutex> lock(this->mutex_);
                        this->condition_.wait(lock,
                            [this] { 
                                return this->stop_ || !this->tasks_.empty(); 
                            });
                        
                        if (this->stop_ && this->tasks_.empty())
                            return;
                        
                        task = std::move(this->tasks_.front());
                        this->tasks_.pop();
                    }
                    
                    task();
                }
            });
        }
    }
    
    template<typename F>
    auto enqueue(F&& f) -> std::future<typename std::result_of<F()>::type> {
        using return_type = typename std::result_of<F()>::type;
        
        auto task = std::make_shared<std::packaged_task<return_type()>>(std::forward<F>(f));
        std::future<return_type> res = task->get_future();
        
        {
            std::unique_lock<std::mutex> lock(mutex_);
            
            if (stop_)
                throw std::runtime_error("enqueue on stopped ThreadPool");
            
            tasks_.emplace([task]() { (*task)(); });
        }
        
        condition_.notify_one();
        return res;
    }
    
    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            stop_ = true;
        }
        
        condition_.notify_all();
        for (std::thread& worker : workers_)
            worker.join();
    }
    
private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex mutex_;
    std::condition_variable condition_;
    bool stop_;
};
```

### HJ.2 无锁队列 {#hj-2-无锁队列}

```cpp
// utils/lock_free_queue.h

template<typename T>
class LockFreeQueue {
public:
    struct Node {
        T* data;
        std::atomic<Node*> next;
    };
    
    LockFreeQueue() {
        Node* dummy = new Node();
        dummy->data = nullptr;
        dummy->next.store(nullptr);
        head_.store(dummy);
        tail_.store(dummy);
    }
    
    void enqueue(T* item) {
        Node* node = new Node();
        node->data = item;
        node->next.store(nullptr);
        
        Node* prev = head_.exchange(node);
        prev->next.store(node);
    }
    
    T* dequeue() {
        Node* tail = tail_.load();
        Node* next = tail->next.load();
        
        if (next == nullptr)
            return nullptr;
        
        tail_.store(next);
        delete tail;
        
        return next->data;
    }
    
private:
    std::atomic<Node*> head_;
    std::atomic<Node*> tail_;
};
```

---

## 附录HK： 错误处理 {#附录hk-错误处理}

### HK.1 错误码和异常 {#hk-1-错误码和异常}

```cpp
// utils/errors.h

// 错误码枚举
enum class ErrorCode : int {
    SUCCESS = 0,
    
    // 通用错误
    INVALID_ARGUMENT = -1,
    NULL_POINTER = -2,
    OUT_OF_RANGE = -3,
    OVERFLOW = -4,
    UNDERFLOW = -5,
    NOT_FOUND = -6,
    ALREADY_EXISTS = -7,
    PERMISSION_DENIED = -8,
    TIMEOUT = -9,
    
    // I/O错误
    IO_ERROR = -100,
    FILE_NOT_FOUND = -101,
    READ_ERROR = -102,
    WRITE_ERROR = -103,
    
    // 协议错误
    PROTOCOL_ERROR = -200,
    DECODE_ERROR = -201,
    ENCODE_ERROR = -202,
    
    // 内存错误
    OUT_OF_MEMORY = -300,
    MEMORY_CORRUPTION = -301
};

// 异常类
class SnortException : public std::exception {
public:
    SnortException(ErrorCode code, const char* msg) 
        : code_(code), message_(msg) {}
    
    const char* what() const noexcept override {
        return message_.c_str();
    }
    
    ErrorCode code() const { return code_; }
    
private:
    ErrorCode code_;
    std::string message_;
};

// 错误宏
#define THROW(code, msg) throw SnortException(code, msg)

#define TRY_BLOCK try {

#define CATCH_ERRORS } \
    catch (const SnortException& e) { \
        handle_error(e.code(), e.what()); \
    } \
    catch (const std::exception& e) { \
        handle_error(ErrorCode::PROTOCOL_ERROR, e.what()); \
    }
```

---

## 附录HL： 日志系统 {#附录hl-日志系统}

### HL.1 日志接口 {#hl-1-日志接口}

```cpp
// loggers/logger.h

class Logger {
public:
    enum class Level : uint8_t {
        TRACE = 0,
        DEBUG = 1,
        INFO = 2,
        WARN = 3,
        ERROR = 4,
        FATAL = 5
    };
    
    virtual ~Logger() = default;
    
    virtual void log(Level level, const char* file, int line,
                    const char* func, const char* fmt, ...) = 0;
    
    void trace(const char* file, int line, const char* func, const char* fmt, ...) {
        va_list args;
        va_start(args, fmt);
        log(Level::TRACE, file, line, func, fmt, args);
        va_end(args);
    }
    
    void debug(const char* file, int line, const char* func, const char* fmt, ...) {
        va_list args;
        va_start(args, fmt);
        log(Level::DEBUG, file, line, func, fmt, args);
        va_end(args);
    }
    
    void info(const char* fmt, ...) {
        va_list args;
        va_start(args, fmt);
        log(Level::INFO, nullptr, 0, nullptr, fmt, args);
        va_end(args);
    }
    
    void warn(const char* fmt, ...) {
        va_list args;
        va_start(args, fmt);
        log(Level::WARN, nullptr, 0, nullptr, fmt, args);
        va_end(args);
    }
    
    void error(const char* fmt, ...) {
        va_list args;
        va_start(args, fmt);
        log(Level::ERROR, nullptr, 0, nullptr, fmt, args);
        va_end(args);
    }
};

// 日志宏
#define LOG_TRACE(fmt, ...) \
    Logger::get_instance()->trace(__FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

#define LOG_DEBUG(fmt, ...) \
    Logger::get_instance()->debug(__FILE__, __LINE__, __func__, fmt, ##__VA_ARGS__)

#define LOG_INFO(fmt, ...) \
    Logger::get_instance()->info(fmt, ##__VA_ARGS__)

#define LOG_WARN(fmt, ...) \
    Logger::get_instance()->warn(fmt, ##__VA_ARGS__)

#define LOG_ERROR(fmt, ...) \
    Logger::get_instance()->error(fmt, ##__VA_ARGS__)
```

---

## 附录HM： 配置解析器 {#附录hm-配置解析器}

### HM.1 JSON配置 {#hm-1-json配置}

```cpp
// config/json_config.h

class JSONConfig {
public:
    bool load(const char* path) {
        std::string content = FileUtils::read_file(path);
        if (content.empty())
            return false;
        
        return parse(content);
    }
    
    bool parse(const std::string& json_str) {
        return json::parse(json_str, root_);
    }
    
    // 获取值
    template<typename T>
    T get(const char* key, const T& default_value) const {
        try {
            return root_.at(key).get<T>();
        } catch (...) {
            return default_value;
        }
    }
    
    // 获取嵌套值
    template<typename T>
    T get_path(const char* path, const T& default_value) const {
        std::vector<std::string> keys = StringUtils::split(path, '.');
        const json* current = &root_;
        
        for (const auto& key : keys) {
            try {
                current = &current->at(key);
            } catch (...) {
                return default_value;
            }
        }
        
        try {
            return current->get<T>();
        } catch (...) {
            return default_value;
        }
    }
    
    // 检查键存在
    bool has(const char* key) const {
        return root_.contains(key);
    }
    
    // 获取所有键
    std::vector<std::string> keys() const {
        std::vector<std::string> result;
        for (const auto& [key, _] : root_.items())
            result.push_back(key);
        return result;
    }
    
private:
    json root_;
};
```

---

## 附录HN： 事件驱动框架 {#附录hn-事件驱动框架}

### HN.1 事件循环 {#hn-1-事件循环}

```cpp
// framework/event_loop.h

class EventLoop {
public:
    EventLoop() : running_(false) {}
    
    // 添加文件描述符事件
    void add_fd(int fd, uint32_t events, std::function<void(uint32_t)> callback) {
        struct epoll_event ev;
        ev.events = events;
        ev.data.fd = fd;
        
        epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd, &ev);
        
        callbacks_[fd] = callback;
    }
    
    // 修改文件描述符事件
    void mod_fd(int fd, uint32_t events) {
        struct epoll_event ev;
        ev.events = events;
        ev.data.fd = fd;
        
        epoll_ctl(epoll_fd_, EPOLL_CTL_MOD, fd, &ev);
    }
    
    // 删除文件描述符
    void del_fd(int fd) {
        epoll_ctl(epoll_fd_, EPOLL_CTL_DEL, fd, nullptr);
        callbacks_.erase(fd);
    }
    
    // 添加定时器
    void add_timer(uint64_t interval_ms, std::function<void()> callback, bool recurring = false) {
        Timer timer;
        timer.interval = interval_ms;
        timer.callback = callback;
        timer.recurring = recurring;
        timer.next_fire = get_time_ms() + interval_ms;
        
        timers_.push_back(timer);
    }
    
    // 运行事件循环
    void run() {
        running_ = true;
        
        while (running_) {
            // 处理定时器
            uint64_t now = get_time_ms();
            for (auto& timer : timers_) {
                if (now >= timer.next_fire) {
                    timer.callback();
                    if (timer.recurring) {
                        timer.next_fire = now + timer.interval;
                    } else {
                        timer.active = false;
                    }
                }
            }
            
            // 移除非活跃定时器
            timers_.erase(
                std::remove_if(timers_.begin(), timers_.end(), 
                    [](const Timer& t) { return !t.active; }),
                timers_.end()
            );
            
            // Epoll等待
            int n = epoll_wait(epoll_fd_, events_, MAX_EVENTS, 100);
            
            for (int i = 0; i < n; i++) {
                uint32_t revents = events_[i].events;
                int fd = events_[i].data.fd;
                
                if (callbacks_.find(fd) != callbacks_.end()) {
                    callbacks_[fd](revents);
                }
            }
        }
    }
    
    // 停止事件循环
    void stop() { running_ = false; }
    
private:
    static constexpr int MAX_EVENTS = 1024;
    static constexpr int MAX_TIMER = 64;
    
    int epoll_fd_;
    struct epoll_event events_[MAX_EVENTS];
    
    bool running_;
    std::map<int, std::function<void(uint32_t)>> callbacks_;
    
    struct Timer {
        uint64_t interval;
        uint64_t next_fire;
        bool recurring;
        bool active = true;
        std::function<void()> callback;
    };
    
    std::vector<Timer> timers_;
};
```

---

## 附录HO： 状态机框架 {#附录ho-状态机框架}

### HO.1 通用状态机 {#ho-1-通用状态机}

```cpp
// framework/state_machine.h

template<typename State, typename Event>
class StateMachine {
public:
    using Transition = std::pair<State, Event>;
    using Handler = std::function<bool(State&, Event)>;
    
    StateMachine(State initial) : current_(initial) {}
    
    // 设置转换
    void set_handler(State state, Event event, Handler handler) {
        handlers_[{state, event}] = handler;
    }
    
    // 设置默认转换
    void set_default_handler(Handler handler) {
        default_handler_ = handler;
    }
    
    // 设置入口/出口动作
    void set_entry_action(State state, std::function<void()> action) {
        entry_actions_[state] = action;
    }
    
    void set_exit_action(State state, std::function<void()> action) {
        exit_actions_[state] = action;
    }
    
    // 处理事件
    bool dispatch(Event event) {
        auto it = handlers_.find({current_, event});
        
        Handler handler;
        if (it != handlers_.end()) {
            handler = it->second;
        } else if (default_handler_) {
            handler = default_handler_;
        } else {
            return false;
        }
        
        // 执行退出动作
        if (exit_actions_.count(current_) > 0)
            exit_actions_[current_]();
        
        // 执行转换
        bool result = handler(current_, event);
        
        // 执行进入动作
        if (result && entry_actions_.count(current_) > 0)
            entry_actions_[current_]();
        
        return result;
    }
    
    // 获取当前状态
    State current() const { return current_; }
    
private:
    State current_;
    std::map<Transition, Handler> handlers_;
    std::function<bool(State&, Event)> default_handler_;
    std::map<State, std::function<void()>> entry_actions_;
    std::map<State, std::function<void()>> exit_actions_;
};

// 使用示例
/*
enum class TcpState { CLOSED, LISTEN, SYN_SENT, ESTABLISHED };
enum class TcpEvent { SYN, SYN_ACK, ACK, FIN, RST };

StateMachine<TcpState, TcpEvent> sm(TcpState::CLOSED);

sm.set_handler(TcpState::CLOSED, TcpEvent::SYN, 
    [](TcpState& s, TcpEvent& e) { 
        s = TcpState::LISTEN; 
        return true; 
    });

sm.set_handler(TcpState::LISTEN, TcpEvent::SYN,
    [](TcpState& s, TcpEvent& e) {
        s = TcpState::SYN_SENT;
        return true;
    });

sm.dispatch(TcpEvent::SYN);  // CLOSED -> LISTEN
*/
```

---

## 附录HP： 观察者模式 {#附录hp-观察者模式}

### HP.1 主题/观察者 {#hp-1-主题-观察者}

```cpp
// framework/observer.h

template<typename... Args>
class Observer {
public:
    virtual ~Observer() = default;
    virtual void update(Args... args) = 0;
};

template<typename... Args>
class Subject {
public:
    void attach(Observer<Args...>* observer) {
        observers_.push_back(observer);
    }
    
    void detach(Observer<Args...>* observer) {
        observers_.erase(
            std::remove(observers_.begin(), observers_.end(), observer),
            observers_.end()
        );
    }
    
    void notify(Args... args) {
        for (auto* observer : observers_)
            observer->update(args...);
    }
    
private:
    std::vector<Observer<Args...>*> observers_;
};

// 使用示例
class FlowObserver : public Observer<Flow*, const char*> {
public:
    void update(Flow* flow, const char* event) override {
        printf("Flow %p: %s\n", flow, event);
    }
};

class FlowManager : public Subject<Flow*, const char*> {
public:
    void create_flow(Flow* flow) {
        notify(flow, "created");
    }
    
    void delete_flow(Flow* flow) {
        notify(flow, "deleted");
    }
};
```

---

## 附录HQ： 信号处理 {#附录hq-信号处理}

### HQ.1 Unix信号处理 {#hq-1-unix信号处理}

```cpp
// utils/signal_handler.h

class SignalHandler {
public:
    using Handler = std::function<void(int)>;
    
    static SignalHandler& instance() {
        static SignalHandler instance;
        return instance;
    }
    
    // 注册信号处理器
    void register_handler(int sig, Handler handler) {
        struct sigaction sa;
        sa.sa_handler = [](int signum) {
            instance().handle_signal(signum);
        };
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;
        
        sigaction(sig, &sa, &old_actions_[sig]);
        handlers_[sig] = handler;
    }
    
    // 恢复默认处理器
    void restore_default(int sig) {
        if (old_actions_[sig]) {
            sigaction(sig, &old_actions_[sig], nullptr);
            handlers_.erase(sig);
        }
    }
    
    // 恢复所有
    void restore_all() {
        for (auto& [sig, _] : handlers_)
            restore_default(sig);
    }
    
private:
    SignalHandler() = default;
    
    void handle_signal(int sig) {
        auto it = handlers_.find(sig);
        if (it != handlers_.end())
            it->second(sig);
    }
    
    std::map<int, Handler> handlers_;
    std::map<int, struct sigaction> old_actions_;
};

// 使用
SignalHandler::instance().register_handler(SIGINT, [](int sig) {
    printf("Caught SIGINT, shutting down...\n");
    // 优雅关闭
});

SignalHandler::instance().register_handler(SIGTERM, [](int sig) {
    printf("Caught SIGTERM, shutting down...\n");
    // 优雅关闭
});

SignalHandler::instance().register_handler(SIGHUP, [](int sig) {
    printf("Caught SIGHUP, reloading config...\n");
    // 重新加载配置
});
```

---
