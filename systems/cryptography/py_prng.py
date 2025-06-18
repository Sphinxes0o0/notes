import hmac, hashlib
def random_number_generator(seed: bytes, max_num: int):
  state = seed
  counter = 0

  while True:
    state = hmac.new(state, bytes(counter), hashlib.sha1).digest()
    counter += 1

    # 这里取余实际上是压缩了信息，某种程度上说，这可以保证内部的真实状态 state 不被逆向出来
    yield int.from_bytes(state, byteorder="big") % max_num

# 测试下，计算 20 个 100 以内的随机数
gen = random_number_generator(b"abc", 100)
print([next(gen) for _ in range(20)])
# => [71, 41, 52, 18, 51, 14, 58, 30, 70, 20, 59, 93, 3, 10, 81, 63, 48, 67, 18, 36]