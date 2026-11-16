# 轮转数组

给定一个整数数组 nums，将数组中的元素向右轮转 k 个位置，其中 k 是非负数。

示例 1:

输入: nums = [1,2,3,4,5,6,7], k = 3
输出: [5,6,7,1,2,3,4]
解释:
旋转 1 步: [7,1,2,3,4,5,6]
旋转 2 步: [6,7,1,2,3,4,5]
旋转 3 步: [5,6,7,1,2,3,4]


示例 2:

输入: nums = [-1,-100,3,99], k = 2  
输出: [3,99,-1,-100]  
解释:  
向右轮转 1 步: [99,-1,-100,3]
向右轮转 2 步: [3,99,-1,-100]


说明:
* 1 <= nums.length <= 10^ 5
* -2^31 <= nums[i] <= 2^31 - 1
* 0 <= k <= 10^5


进阶:
* 尽可能想出更多的解决方案，至少有三种不同的方法可以解决这个问题。
* 你可以使用空间复杂度为 O(1) 的 原地 算法解决这个问题吗？


## Sulution

### 1. 额外数组

```cpp
class Solution {
public:
    void rotate(vector<int>& nums, int k) {
        vector<int> tmp(nums.size());
        for (int i = 0; i < nums.size(); ++i) {
            tmp[(i + k) % nums.size()] = nums[i];
        }
        nums = temp;
    }
};

```

### 2. 3次反转
先反转整个数组，然后反转前 k 个元素，最后反转剩余的 n - k 个元素

```cpp
class Solution {
public:
    void rotate(vector<int>& nums, int k) {
        k = k % nums.size(); // In case k is larger than n
        reverse(nums, 0, nums.size() - 1);
        reverse(nums, 0, k - 1);
        reverse(nums, k, nums.size() - 1);
    }

    void reverse(vector<int>& nums, int start, int end) {
        while (start < end) {
            swap(nums[start], nums[end]);
            start++;
            end--;
        }
    }
};
```

### 3. 环状替换
通过环状替换，在每次替换过程中将元素移动到其最终位置。
```cpp
class Solution {
    
public:
    void rotate(vector<int>& nums, int k) {
        k = k % nums.size();
        int count = 0;
        for (int start = 0; count < nums.size(); start++) {
            int current = start;
            int prev = nums[start];
            do {
                int next = (current + k) % nums.size();
                swap(nums[next], prev);
                current = next; 
                count++;
            } while (start != current);
        }
    }
}
```
`k = k % nums.size();`
为了处理当 k 大于数组长度 nums.size() 的情形：
由于数组是一个循环的结构，当移动的次数等于数组的长度时，数组会回到原始状态。
因此，任何多于数组长度的移动都可以通过取模运算 `k % nums.size()` 来简化，这样可以得到一个等效的、但不超过数组长度的移动次数。

## 总结：
每种方法都有自己的优势：

* 方法 1 很直观，但是它使用了额外的空间。
* 方法 2 是一个很好的原地算法，空间复杂度是 O(1)。
* 方法 3 也是原地算法，并且对于某些特定情况下会更加高效。

在实际情况中，如果允许使用额外的空间，方法 1 更容易理解和实现。但是，如果需要原地算法，方法 2 和方法 3 都是很好的选择。