// mem_order_demo.cc
#include <atomic>
#include <thread>
#include <cassert>
#include <iostream>
#include <chrono>

enum class Mode { RELAXED, SEQ_CST, ACQ_REL };

std::atomic<bool> ready{false};
int data = 0;
Mode mode = Mode::ACQ_REL; // ← 可改：RELAXED / SEQ_CST / ACQ_REL

void consumer() {
    std::memory_order mo;
    switch (mode) {
        case Mode::RELAXED: mo = std::memory_order_relaxed; break;
        case Mode::SEQ_CST: mo = std::memory_order_seq_cst; break;
        case Mode::ACQ_REL: mo = std::memory_order_acquire; break;
    }

    while (!ready.load(mo)) {
        std::this_thread::yield();
    }
    assert(data == 42); // 可能失败（仅当 mode==RELAXED 时）
    std::cout << "[OK] data = " << data << std::endl;
}

void producer() {
    data = 42;

    std::memory_order mo;
    switch (mode) {
        case Mode::RELAXED: mo = std::memory_order_relaxed; break;
        case Mode::SEQ_CST: mo = std::memory_order_seq_cst; break;
        case Mode::ACQ_REL: mo = std::memory_order_release; break;
    }

    ready.store(true, mo);
}

int main() {
    std::cout << "Mode: ";
    switch (mode) {
        case Mode::RELAXED: std::cout << "relaxed\n"; break;
        case Mode::SEQ_CST: std::cout << "seq_cst\n"; break;
        case Mode::ACQ_REL: std::cout << "acquire-release\n"; break;
    }

    std::thread t1(producer), t2(consumer);
    t1.join(); t2.join();
    return 0;
}