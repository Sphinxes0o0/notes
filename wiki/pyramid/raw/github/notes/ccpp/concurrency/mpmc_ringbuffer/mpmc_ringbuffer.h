#pragma once
#include <atomic>
#include <cstddef>
#include <optional>
#include <type_traits>

template <typename T, size_t N>
class MPMCRingBuffer {
    static_assert(N > 1, "capacity must be greater than 1");
    static_assert(std::is_trivially_destructible_v<T>, 
        "T must be trivially destructible");
    
    alignas(64) std::atomic<size_t> head_ {0};
    alignas(64) std::atomic<size_t> tail_ {0};
    alignas(64) T buffer_[N];

    static constexpr size_t mask_ = N - 1;
    static_assert((N & mask_) == 0, "N must be power of two for fast mod");

public:
    MPMCRingBuffer() = default;
    MPMCRingBuffer(const MPMCRingBuffer&) = delete;
    MPMCRingBuffer& operator=(const MPMCRingBuffer &) = delete;

    bool push(const T& item) {
        size_t tail = head_.load(std::memory_order_relaxed);
        while (true) {

            // 读 head 用 acquire 防重排
            size_t head = head_.load(std::memory_order_acquire);
            size_t next_tail = (tail + 1) & mask_;

            if (next_tail == head) {
                return false;
            }

             // 尝试 CAS tail → next_tail
            if (tail_.compare_exchange_weak(tail, next_tail, 
                std::memory_order_release,// 成功：release 保证 buffer_[tail]=value 对消费者可见
                std::memory_order_relaxed)) { // 失败：只需 relaxed 重试
                buffer_[tail & mask_] = item;
                return true;
            }
        }
    }

    std::optional<T> pop() { 
        size_t head = head_.load(std::memory_order_relaxed);
        while (true) {
            size_t tail = tail_.load(std::memory_order_acquire);
            if (head == tail) {
                return std::nullopt;
            }

            size_t next_head = (head + 1) & mask_;
            if (head_.compare_exchange_weak(head, next_head, 
                std::memory_order_acquire,// 成功：acquire 保证后续读 buffer_[head] 看到最新值
                std::memory_order_relaxed)) {// 失败：retry
                T value = buffer_[head & mask_];
                return value;
            }
        }
    }

    size_t size_approx() const {
        size_t tail = tail_.load(std::memory_order_acquire);
        size_t head = head_.load(std::memory_order_acquire);
        return (tail >= head) ? (tail - head) : (tail - head + N);
    }

    bool empty() const {
        return head_.load() == tail_.load();
    }

    bool full() const {
        size_t h = head_.load(std::memory_order_relaxed);
        size_t t = tail_.load(std::memory_order_relaxed);
        return ((t + 1) & mask_) == h;
    }

};