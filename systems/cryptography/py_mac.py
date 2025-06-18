import hashlib, hmac, binascii

key = b"key"
msg = b"some msg"

mac = hmac.new(key, msg, hashlib.sha256).digest()

print(f"HMAC-SHA256({key}, {msg})", binascii.hexlify(mac).decode('utf8'))

def xor_bytes(b1, b2):
  return bytes(a ^ c for a, c in zip(b1, b2))

def my_hmac(key, msg, hash_name):
  # hash => (block_size, output_size)
  # 单位是 bytes，数据来源于 https://en.wikipedia.org/wiki/HMAC
  hash_size_dict = {
    "md5": (64, 16),
    "sha1": (64, 20),
    "sha224": (64, 28),
    "sha256": (64, 32),
    # "sha512/224": (128, 28),  # 这俩算法暂时不清楚在 hashlib 里叫啥名
    # "sha512/256": (128, 32),
    "sha_384": (128, 48),
    "sha_512": (128, 64),
    "sha3_224": (144, 28),
    "sha3_256": (136, 32),
    "sha3_384": (104, 48),
    "sha3_512": (72, 64),
  }
  if hash_name not in hash_size_dict:
    raise ValueError("unknown hash_name")

  block_size, output_size = hash_size_dict[hash_name]
  hash_ = getattr(hashlib, hash_name)

  # 确保 key 的长度为 block_size
  block_sized_key = key
  if len(key) > block_size:
    block_sized_key = hash_(key).digest()  # 用 hash 函数进行压缩
  if len(key) < block_size:
    block_sized_key += b'\x00' * (block_size - len(key))  # 末尾补 0

  o_key_pad = xor_bytes(block_sized_key, (b"\x5c" * block_size))  # Outer padded key
  i_key_pad = xor_bytes(block_sized_key, (b"\x36" * block_size))  # Inner padded key

  return hash_(o_key_pad + hash_(i_key_pad + msg).digest()).digest()


# 下面验证下
key = b"key"
msg = b"some msg"

mac_ = my_hmac(key, msg, "sha256")
print(f"HMAC-SHA256({key}, {msg})", binascii.hexlify(mac_).decode('utf8'))