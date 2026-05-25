#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>

// 使用原子变量来协调两个线程
std::atomic<bool> thread1_finished{false};
std::atomic<bool> thread2_finished{false};

void worker_thread(const std::string& name, std::atomic<bool>& finished_flag) {
    std::cout << name << " started\n";
    
    // 模拟一些工作
    for (int i = 0; i < 10; ++i) {
        std::cout << name << " working... " << i << "\n";
        // 不调用 yield，线程尽可能长时间地持有 CPU
    }
    
    std::cout << name << " finished\n";
    finished_flag = true;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    
    // 创建两个工作线程
    std::thread t1(worker_thread, "Thread-1", std::ref(thread1_finished));
    std::thread t2(worker_thread, "Thread-2", std::ref(thread2_finished));
    
    // 等待两个线程完成
    t1.join();
    t2.join();
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::cout << "Total execution time: " << duration.count() << " ms\n";

    return 0;
}