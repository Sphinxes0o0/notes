#include <future>
#include <thread>
#include <iostream>

void worker(std::promise<int> p) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    p.set_value(42);
}

int main() {
    std::promise<int> promise;
    auto future = promise.get_future();
    std::thread t(worker, std::move(promise));

    int value = future.get(); // get only once
    std::cout << "future value = " << value << std::endl;

    t.join();
    return 0;
}