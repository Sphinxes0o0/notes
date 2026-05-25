## DESCRIPTION
Create a function that takes an integer as an argument and returns "Even" for even numbers or "Odd" for odd numbers.

## Sulotion

最简单的方法：
使用%（取模）运算符来检查数字除以2的余数。如果余数为0，那么这个数是偶数；如果余数不为0（实际上会是1），
那么这个数是奇数。
```c
const char* even_or_odd(int number)
{
  // return a statically allocated string,
  if(number%2 == 0) return "Even";
  else return "Odd";
}
```
### Best Practice
```c
const char * even_or_odd(int n)
{
  return (n & 1)?("Odd"):("Even");
}
```
使用了位运算符&来判断整数n的奇偶性。
在这里，`n & 1`是一个位运算表达式，它计算n与1的按位与（AND）结果。

当一个整数与1进行按位与操作时，
- 如果该整数的最低位（二进制位）是1，则结果是1，表示这是一个奇数；
- 如果最低位是0，则结果是0，表示这是一个偶数。

函数返回值是一个指向常量字符的指针，根据n & 1的结果返回"Odd"或"Even"字符串。

这里是函数的详细解释：

- n & 1：计算n的最低位
    - 如果n是奇数，最低位将是1，所以n & 1将返回1
    - 如果n是偶数，最低位将是0，所以n & 1将返回0

- (n & 1) ? ("Odd") : ("Even")：这是一个条件表达式（也称为三元操作符）
    - 如果(n & 1)的结果是true（C语言中任何非零值都被视为true），它将返回"Odd"；
    - 如果结果是false（即0），它将返回"Even"

> (C语言中负数也适用)，它的最低位将是0，所以`-22 & 1`的结果将是0，

这种方法是有效且高效的，因为它直接在位级别上进行操作，避免了除法或模运算的开销。