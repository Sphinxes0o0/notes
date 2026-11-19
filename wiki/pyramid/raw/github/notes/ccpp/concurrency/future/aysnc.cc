#include <algorithm>
#include <future>
#include <iostream>
#include <mutex>
#include <numeric>
#include <string>
#include <vector>

std::mutex mutex;

struct X {
    void foo(int i, const std::string& s) {
        std::lock_guard<std::mutex> lk(mutex);
        std::cout << "X::foo(" << i << ", " << s << ")\n";
    }

    void bar(const std::string& s) {
        std::lock_guard<std::mutex> lk(mutex);
        std::cout << "X::bar(" << s << ")\n";
    }

    int operator()(int i) {
        std::lock_guard<std::mutex> lk(mutex);
        std::cout << i << "\n";
        return i + 10;
    }
};

template <typename RandomIt>
int parallel_sum(RandomIt beg, RandomIt end) {
    auto len = end - beg;
    if (len < 1000)
        return std::accumulate(beg, end, 0);

    RandomIt mid = beg + len / 2;
    auto handle = std::async(std::launch::async, parallel_sum<RandomIt>, mid, end);
    int sum = parallel_sum(beg, mid);
    return sum + handle.get();
}

int main() {
    std::vector<int> v(10000, 1);
    std::cout << "Sum: " << parallel_sum(v.begin(), v.end()) << "\n";

    X x;
    auto a1 = std::async(&X::foo, &x, 42, "hello");
    auto a2 = std::async(std::launch::deferred, &X::bar, &x, "world");
    auto a3 = std::async(std::launch::async, X(), 42);
    a2.wait();
    std::cout << "a1: " << a1.get() << "\n";
    std::cout << "a3: " << a3.get() << "\n";

    return 0;   
}
