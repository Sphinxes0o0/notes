#include <thread>
#include <iostream>
#include <chrono>

using namespace std::chrono_literals;

void foo() {
    std::thread::id this_id = std::this_thread::get_id();
    std::cout << "thread " << this_id << " is sleeping\n";
    std::this_thread::sleep_for(2500ms);
}

int main() {
    std::thread t1(foo);
    std::thread t2(foo);

    using namespace std::chrono_literals;
    std::cout << "\nHello from main thread, id: " 
              << std::this_thread::get_id() << "\n";

    const auto start = std::chrono::high_resolution_clock::now();
    std::this_thread::sleep_for(1000ms);
    const auto end = std::chrono::high_resolution_clock::now();
    const auto elapsed = end - start;
    std::cout << "\nMain thread slept for " << elapsed << " ms\n";

    t1.join();
    t2.join();

    return 0;
}
