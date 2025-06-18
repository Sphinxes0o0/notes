# pip install cryptography==36.0.1
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh

# 1. 双方协商使用两个独特的正整数 g 与 p
## generator => 即基数 g，通常使用 2, 有时也使用 5
## key_size => 模数 p 的长度，通常使用 2048-3072 位（2048 位的安全性正在减弱）
params = dh.generate_parameters(generator=2, key_size=2048)
param_numbers = params.parameter_numbers()
g = param_numbers.g  # => 肯定是 2
p = param_numbers.p  # => 一个 2048 位的整数
print(f"{g=}, {p=}")

# 2. Alice 生成自己的秘密整数 a 与公开整数 A
alice_priv_key = params.generate_private_key()
a = alice_priv_key.private_numbers().x
A = alice_priv_key.private_numbers().public_numbers.y
print(f"{a=}")
print(f"{A=}")

# 3. Bob 生成自己的秘密整数 b 与公开整数 B
bob_priv_key = params.generate_private_key()
b = bob_priv_key.private_numbers().x
B = bob_priv_key.private_numbers().public_numbers.y
print(f"{b=}")
print(f"{B=}")

# 4. Alice 与 Bob 公开交换整数 A 跟 B（即各自的公钥）

# 5. Alice 使用 a B 与 p 计算出共享密钥
## 首先使用 B p g 构造出 bob 的公钥对象（实际上 g 不参与计算）
bob_pub_numbers = dh.DHPublicNumbers(B, param_numbers)
bob_pub_key = bob_pub_numbers.public_key()
## 计算共享密钥
alice_shared_key = alice_priv_key.exchange(bob_pub_key)

# 6. Bob 使用 b A 与 p 计算出共享密钥
## 首先使用 A p g 构造出 alice 的公钥对象（实际上 g 不参与计算）
alice_pub_numbers = dh.DHPublicNumbers(A, param_numbers)
alice_pub_key = alice_pub_numbers.public_key()
## 计算共享密钥
bob_shared_key = bob_priv_key.exchange(alice_pub_key)

# 两者应该完全相等， Alice 与 Bob 完成第一次密钥交换
alice_shared_key == bob_shared_key

# 7. Alice 与 Bob 使用 shared_key 进行对称加密通讯