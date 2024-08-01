import secrets
import string

chars = string.digits + "your_custom_-content" +  string.ascii_letters
def random_string(length: int):
    """生成随机字符串"""
    # 注意，这里不应该使用 random 库！而应该使用 secrets
    code = "".join(secrets.choice(chars) for _ in range(length))
    return code

random_string(24)
# => _rebBfgYs4OtkrPbYtnGmc4n