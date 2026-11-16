#include <atomic>
#include <thread>
#include <cassert>
#include <iostream>
#include <chrono>

std::atomic<bool> ready {false};
int data = 0;

void consumer() {
    while (!ready.load(std::memory_order_relaxed)) {
        // 等待生产者准备好数据
        std::this_thread::yield();
    }

    assert(data == 42);
    std::cout << "Consumer: " << data << std::endl;
}

void producer() {
    std::this_thread::sleep_for(std::chrono::milliseconds(500)); // 模拟一些工作
    data = 42;
    ready.store(true, std::memory_order_relaxed);
    std::cout << "Producer: " << data << std::endl;
}

int main() {
    std::thread t1(consumer);
    std::thread t2(producer);
    t1.join();
    t2.join();

    return 0;
}