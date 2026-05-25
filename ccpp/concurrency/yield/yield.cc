// cxx functions managing the current thread
// defined in <thread>
//    std::this_thread::yield
//
// std::this_thread::yield() 提示调度器让出当前线程的时间片，
// 但这是一个非绑定性的提示。在线程数量很少或者没有其他线程竞争CPU时，
// 调度器可能立即重新调度当前线程继续执行。
// 因此，在单线程或低竞争环境中，yield的效果可能不明显。

#include <cstdint>
#include <iostream>
#include <thread>
#include <chrono>

void little_sleep(std::chrono::milliseconds ms) {
    auto start = std::chrono::high_resolution_clock::now();
    auto end = start + ms;
    uint64_t count = 0;
    std::cout << "yield to sleep : " << count << std::endl;
    do {
        count++;
        if (count % 10000 == 0) {
            std::cout << "yield to sleep : " << count << std::endl;
        }
        std::this_thread::yield();
    } while (std::chrono::high_resolution_clock::now() < end);
    std::cout << "yield to sleep done : " << count << std::endl;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    std::cout << "Start yielding..." << std::endl;
    little_sleep(std::chrono::milliseconds(10));
    std::cout << "Finished yielding." << std::endl;
    auto elapsed = std::chrono::high_resolution_clock::now() - start;
    std::cout << "Elapsed time: "
              << std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count()
              << " ms" << std::endl;

    return 0;
}