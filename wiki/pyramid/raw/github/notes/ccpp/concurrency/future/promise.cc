#include <chrono>
#include <future>
#include <iostream>
#include <numeric>
#include <thread>
#include <vector>

void accumulate(std::vector<int>::iterator first,
                std::vector<int>::iterator last,
                std::promise<int> result) {

    int sum = std::accumulate(first, last, 0);
    result.set_value(sum); // 设置结果
}

void do_work(std::promise<void> barrier) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    barrier.set_value();
}

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    std::promise<int> result;
    std::future<int> future_result = result.get_future();
    std::thread work_thread(accumulate, numbers.begin(), numbers.end(),
                            std::move(result));

    std::cout << "Result of accumulation: " << future_result.get() << std::endl;
    work_thread.join();

    std::promise<void> barrier;
    std::future<void> barrier_future = barrier.get_future();
    std::thread barrier_thread(do_work, std::move(barrier));
    std::cout << "Waiting for work to complete..." << std::endl;
    barrier_future.wait();
    barrier_thread.join();
    std::cout << "Work completed." << std::endl;

    return 0;
}
