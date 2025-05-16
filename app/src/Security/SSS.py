# Shamir 分片算法：
# 实现或集成现有的 Shamir 阈值分片库（如 secretsharing）。
# 将私钥通过分片算法拆分为 N 个分片，要求至少 K 个分片恢复（用户自定义阈值）。
# 分片可能需要附加元数据（如分片编号、哈希校验值）。
# 分片恢复逻辑：验证分片有效性后重组私钥。

import hashlib
import secrets
import json


def split_secret(secret_bytes, n, k, p):
    """
    Splits a secret into n shares using Shamir's Secret Sharing algorithm.
    Requires at least k shares to recover the secret.

    :param secret_bytes: The secret as bytes.
    :param n: Number of shares to generate.
    :param k: Threshold of shares required for recovery.
    :param p: Prime number defining the finite field.
    :return: List of share dictionaries with index, share, and hash.
    """
    if k < 1:
        raise ValueError("k must be at least 1.")
    if n < k:
        raise ValueError("n must be >= k.")

    s = int.from_bytes(secret_bytes, byteorder='big')
    if s >= p:
        raise ValueError("Secret is too large for the given prime p.")

    coefficients = [s] + [secrets.randbelow(p) for _ in range(k - 1)]
    shares = []

    for x in range(1, n + 1):
        y = 0
        for coeff in reversed(coefficients):
            y = (y * x + coeff) % p

        data = f"{x}:{y}".encode('utf-8')
        hash_digest = hashlib.sha256(data).hexdigest()
        shares.append({
            'index': x,
            'share': y,
            'hash': hash_digest
        })

    return shares


def recover_secret(shares, p, byte_length, k):
    """
    Recovers the secret from a list of shares using Shamir's Secret Sharing.

    :param shares: List of share dictionaries.
    :param p: Prime number used in splitting.
    :param byte_length: Expected byte length of the secret.
    :param k: Required number of shares.
    :return: Recovered secret as bytes.
    """
    valid_shares = []
    for share in shares:
        x = share['index']
        y = share['share']
        data = f"{x}:{y}".encode('utf-8')
        computed_hash = hashlib.sha256(data).hexdigest()
        if computed_hash == share['hash']:
            valid_shares.append((x, y))

    if len(valid_shares) < k:
        raise ValueError(f"Not enough valid shares. Required: {k}, Found: {len(valid_shares)}")

    secret = 0
    for i in range(len(valid_shares)):
        xi, yi = valid_shares[i]
        numerator = 1
        denominator = 1
        for j in range(len(valid_shares)):
            if j == i:
                continue
            xj, _ = valid_shares[j]
            numerator = (numerator * (-xj)) % p
            denominator = (denominator * (xi - xj)) % p

        inv_denominator = pow(denominator, p - 2, p)
        lagrange = (numerator * inv_denominator) % p
        secret = (secret + yi * lagrange) % p

    return secret.to_bytes(byte_length, byteorder='big')


# 示例用法
if __name__ == "__main__":
    # 使用 secp256k1 的阶作为素数 p
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    secret = b"this_is_a_32_byte_secret_key____"
    n = 5
    k = 3
    byte_length = 32

    # 分片生成
    shares = split_secret(secret, n, k, p)
    print("Generated shares:")
    for share in shares:
        print(json.dumps(share, indent=2))

    # 模拟恢复（使用前3个分片）
    recovered_secret = recover_secret(shares[:3], p, byte_length, k)
    print("\nRecovered secret:", recovered_secret)
    assert recovered_secret == secret, "Recovery failed!"
    print("Successfully recovered the secret.")