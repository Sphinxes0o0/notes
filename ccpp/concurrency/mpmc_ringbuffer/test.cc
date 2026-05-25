#include "mpmc_ringbuffer.h"
#include <cstddef>
#include <thread>
#include <vector>
#include <iostream>
#include <chrono>
#include <cassert>

constexpr size_t CAP = 1024;
MPMCRingBuffer<int , CAP> q;

void producer(int id, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        int val = id * 1000 + static_cast<int>(i);
        while (!q.push(val)) {
            std::this_thread::yield(); // busy-wait fallback
        }
    }
}

void consumer(int id, size_t& count, std::atomic<bool>& stop) {
    size_t local_count = 0;
    while (!stop.load(std::memory_order_relaxed)) {
        if (auto val = q.pop()) {
            // std::cout << "C" << id << ": " << *val << "\n";
            ++local_count;
        } else {
            std::this_thread::yield();
        }
    }
    count += local_count;
}

int main() {
    constexpr int NUM_PROD = 4;
    constexpr int NUM_CONS = 4;
    constexpr size_t ITEMS_PER_PROD = 10'000;

    std::vector<std::thread> threads;
    std::vector<size_t> cons_counts(NUM_CONS, 0);
    std::atomic<bool> stop_flag{false};

    // 启动消费者
    for (int i = 0; i < NUM_CONS; ++i) {
        threads.emplace_back(consumer, i, std::ref(cons_counts[i]), std::ref(stop_flag));
    }

    // 启动生产者
    auto start = std::chrono::steady_clock::now();
    for (int i = 0; i < NUM_PROD; ++i) {
        threads.emplace_back(producer, i, ITEMS_PER_PROD);
    }

    // 等待生产者结束
    for (size_t i = NUM_CONS; i < threads.size(); ++i) {
        threads[i].join();
    }

    // 通知消费者结束
    stop_flag.store(true, std::memory_order_release);
    for (int i = 0; i < NUM_CONS; ++i) {
        threads[i].join();
    }
    auto dur = std::chrono::steady_clock::now() - start;

    size_t total = 0;
    for (auto c : cons_counts) total += c;

    std::cout << "Expected: " << NUM_PROD * ITEMS_PER_PROD << "\n";
    std::cout << "Consumed: " << total << "\n";
    std::cout << "Time: " << std::chrono::duration<double>(dur).count() << " s\n";

    assert(total == NUM_PROD * ITEMS_PER_PROD);
    std::cout << "[PASS] All items processed.\n";
    return 0;
}