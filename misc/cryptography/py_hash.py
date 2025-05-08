import hashlib, binascii

text = 'hello'
data = text.encode("utf8")

sha256hash = hashlib.sha256(data).digest()
print(f"SHA-256({text}) = ", binascii.hexlify(sha256hash).decode("utf8"))

sha384hash = hashlib.sha384(data).digest()
print(f"SHA-384({text}) = ", binascii.hexlify(sha384hash).decode("utf8"))

sha512hash = hashlib.sha512(data).digest()
print(f"SHA-512({text}) = ", binascii.hexlify(sha512hash).decode("utf8"))


sha3_256hash = hashlib.sha3_256(data).digest()
print(f"SHA3-256({text}) = ", binascii.hexlify(sha3_256hash).decode("utf8"))

sha3_512hash = hashlib.sha3_512(data).digest()
print(f"SHA3-512({text}) = ", binascii.hexlify(sha3_512hash).decode("utf8"))

blake2s = hashlib.new('blake2s', data).digest()
print("BLAKE2s({text}) = ", binascii.hexlify(blake2s).decode("utf-8"))

blake2b = hashlib.new('blake2b', data).digest()
print("BLAKE2b({text}) = ", binascii.hexlify(blake2b).decode("utf-8"))

ripemd160 = hashlib.new('ripemd160', data).digest()
print("RIPEMD-160({text}) = ", binascii.hexlify(ripemd160).decode("utf-8"))

