#include <chrono>
#include <thread>
#include <iostream>

auto now() {
    return std::chrono::high_resolution_clock::now();
}

auto awake_time() {
    using std::chrono::operator""ms;
    return now() + 2000ms;
}

int main() {
    std::cout << "Hello World!" << std::endl;
    const auto start{ now()};
    std::cout << "Start sleeping..." << std::endl;
    std::this_thread::sleep_until(awake_time());
    std::chrono::duration<double, std::milli> elapsed{ now() - start};
    std::cout << "Awake after " << elapsed.count() << "ms" << std::endl;

    return 0;
}
