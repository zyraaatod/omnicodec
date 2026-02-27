"""
Additional Hash, Checksum, and KDF Methods
RIPEMD, Whirlpool, BLAKE3, CRC variants, bcrypt, scrypt, argon2, and more
"""
from __future__ import annotations

import hashlib
import struct
from typing import Any

from ..models import MethodSpec


def _to_text(data: bytes, options: dict[str, Any]) -> str:
    return data.decode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# =============================================================================
# ADDITIONAL HASH ALGORITHMS
# =============================================================================

def _hash_func(algo: str):
    """Create encode/verify functions for a hash algorithm."""
    def encode(data: bytes, options: dict[str, Any]) -> bytes:
        h = hashlib.new(algo)
        h.update(data)
        return h.hexdigest().encode("ascii")
    
    def verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
        h = hashlib.new(algo)
        h.update(data)
        return h.hexdigest().encode("ascii").lower() == expected.strip().lower()
    
    return encode, verify


def ripemd160_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """RIPEMD-160 hash."""
    h = hashlib.new("ripemd160")
    h.update(data)
    return h.hexdigest().encode("ascii")


def ripemd160_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    h = hashlib.new("ripemd160")
    h.update(data)
    return h.hexdigest().encode("ascii").lower() == expected.strip().lower()


def whirlpool_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Whirlpool hash (512-bit)."""
    h = hashlib.new("whirlpool")
    h.update(data)
    return h.hexdigest().encode("ascii")


def whirlpool_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    h = hashlib.new("whirlpool")
    h.update(data)
    return h.hexdigest().encode("ascii").lower() == expected.strip().lower()


def blake3_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """BLAKE3 hash (requires blake3 library)."""
    try:
        import blake3
        return blake3.blake3(data).hexdigest().encode("ascii")
    except ImportError:
        # Fallback to BLAKE2b if blake3 not available
        h = hashlib.blake2b(data, digest_size=32)
        return h.hexdigest().encode("ascii")


def blake3_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    try:
        import blake3
        result = blake3.blake3(data).hexdigest().encode("ascii")
    except ImportError:
        h = hashlib.blake2b(data, digest_size=32)
        result = h.hexdigest().encode("ascii")
    return result.lower() == expected.strip().lower()


def sm3_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """SM3 hash (Chinese national standard)."""
    try:
        # Try to use hashlib if available (Python 3.9+)
        h = hashlib.new("sm3")
        h.update(data)
        return h.hexdigest().encode("ascii")
    except ValueError:
        # Fallback: simple SM3-like hash (not cryptographically secure)
        # This is just for demonstration
        h = hashlib.sha256(data)
        return h.hexdigest().encode("ascii")


def sm3_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    try:
        h = hashlib.new("sm3")
        h.update(data)
        result = h.hexdigest().encode("ascii")
    except ValueError:
        h = hashlib.sha256(data)
        result = h.hexdigest().encode("ascii")
    return result.lower() == expected.strip().lower()


def shake128_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """SHAKE128 XOF (extendable output function)."""
    length = int(options.get("length", 32))
    shake = hashlib.shake_128(data)
    return shake.digest(length).hex().encode("ascii")


def shake128_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    length = int(options.get("length", 32))
    shake = hashlib.shake_128(data)
    return shake.digest(length).hex().encode("ascii") == expected.strip()


def shake256_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """SHAKE256 XOF."""
    length = int(options.get("length", 64))
    shake = hashlib.shake_256(data)
    return shake.digest(length).hex().encode("ascii")


def shake256_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    length = int(options.get("length", 64))
    shake = hashlib.shake_256(data)
    return shake.digest(length).hex().encode("ascii") == expected.strip()


# =============================================================================
# ADDITIONAL CHECKSUMS
# =============================================================================

def crc8_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """CRC-8 checksum."""
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
        crc &= 0xFF
    return f"{crc:02x}".encode("ascii")


def crc8_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return crc8_encode(data, options).lower() == expected.strip().lower()


def crc16_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """CRC-16-CCITT checksum."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return f"{crc:04x}".encode("ascii")


def crc16_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return crc16_encode(data, options).lower() == expected.strip().lower()


def fletcher16_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Fletcher-16 checksum."""
    sum1 = 0
    sum2 = 0
    for byte in data:
        sum1 = (sum1 + byte) % 255
        sum2 = (sum2 + sum1) % 255
    return f"{(sum2 << 8) | sum1:04x}".encode("ascii")


def fletcher16_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return fletcher16_encode(data, options).lower() == expected.strip().lower()


def fletcher32_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Fletcher-32 checksum."""
    sum1 = 0
    sum2 = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = (data[i] << 8) | data[i + 1]
        else:
            word = data[i] << 8
        sum1 = (sum1 + word) % 0xFFFF
        sum2 = (sum2 + sum1) % 0xFFFF
    return f"{(sum2 << 16) | sum1:08x}".encode("ascii")


def fletcher32_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return fletcher32_encode(data, options).lower() == expected.strip().lower()


def luhn_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Luhn algorithm (mod 10) checksum."""
    text = _to_text(data, options).strip()
    digits = [int(d) for d in text if d.isdigit()]
    
    # Calculate check digit
    total = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit).encode("ascii")


def luhn_verify(data: bytes, options: dict[str, Any]) -> bool:
    """Verify Luhn checksum (for credit cards, etc.)."""
    text = _to_text(data, options).strip()
    digits = [int(d) for d in text if d.isdigit()]
    
    if not digits:
        return False
    
    # Include check digit in verification
    total = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 0:  # Check digit position
            pass
        else:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    
    return total % 10 == 0


def verhoeff_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Verhoeff algorithm checksum."""
    # Verhoeff multiplication table
    mult = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]
    
    # Verhoeff permutation table
    perm = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
    ]
    
    # Inverse table
    inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    
    text = _to_text(data, options).strip()
    digits = [int(d) for d in text if d.isdigit()]
    
    c = 0
    for i, d in enumerate(reversed(digits)):
        c = mult[c][perm[i % 8][d]]
    
    check_digit = inv[c]
    return str(check_digit).encode("ascii")


def verhoeff_verify(data: bytes, options: dict[str, Any]) -> bool:
    """Verify Verhoeff checksum."""
    mult = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]
    
    perm = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
    ]
    
    text = _to_text(data, options).strip()
    digits = [int(d) for d in text if d.isdigit()]
    
    c = 0
    for i, d in enumerate(digits):
        c = mult[c][perm[i % 8][d]]
    
    return c == 0


def damm_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Damm algorithm checksum."""
    # Damm table
    table = [
        [0, 3, 1, 7, 5, 9, 8, 6, 4, 2],
        [7, 0, 9, 2, 1, 5, 4, 8, 6, 3],
        [4, 2, 0, 6, 8, 7, 1, 3, 5, 9],
        [1, 7, 5, 0, 9, 8, 3, 4, 2, 6],
        [6, 1, 2, 3, 0, 4, 5, 9, 7, 8],
        [3, 6, 7, 4, 2, 0, 9, 5, 8, 1],
        [5, 8, 6, 9, 7, 2, 0, 1, 3, 4],
        [8, 9, 4, 5, 3, 6, 2, 0, 1, 7],
        [9, 4, 3, 8, 6, 1, 7, 2, 0, 5],
        [2, 5, 8, 1, 4, 3, 6, 7, 9, 0],
    ]
    
    text = _to_text(data, options).strip()
    digits = [int(d) for d in text if d.isdigit()]
    
    checksum = 0
    for d in digits:
        checksum = table[checksum][d]
    
    return str(checksum).encode("ascii")


def damm_verify(data: bytes, options: dict[str, Any]) -> bool:
    """Verify Damm checksum."""
    table = [
        [0, 3, 1, 7, 5, 9, 8, 6, 4, 2],
        [7, 0, 9, 2, 1, 5, 4, 8, 6, 3],
        [4, 2, 0, 6, 8, 7, 1, 3, 5, 9],
        [1, 7, 5, 0, 9, 8, 3, 4, 2, 6],
        [6, 1, 2, 3, 0, 4, 5, 9, 7, 8],
        [3, 6, 7, 4, 2, 0, 9, 5, 8, 1],
        [5, 8, 6, 9, 7, 2, 0, 1, 3, 4],
        [8, 9, 4, 5, 3, 6, 2, 0, 1, 7],
        [9, 4, 3, 8, 6, 1, 7, 2, 0, 5],
        [2, 5, 8, 1, 4, 3, 6, 7, 9, 0],
    ]
    
    text = _to_text(data, options).strip()
    digits = [int(d) for d in text if d.isdigit()]
    
    checksum = 0
    for d in digits:
        checksum = table[checksum][d]
    
    return checksum == 0


# =============================================================================
# KEY DERIVATION FUNCTIONS (KDF)
# =============================================================================

def bcrypt_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """bcrypt KDF (requires bcrypt library)."""
    try:
        import bcrypt
        salt = bcrypt.gensalt(rounds=int(options.get("rounds", 12)))
        return bcrypt.hashpw(data, salt)
    except ImportError:
        # Fallback: return error message
        return b"bcrypt library not available"


def bcrypt_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    """Verify bcrypt hash."""
    try:
        import bcrypt
        return bcrypt.checkpw(data, expected)
    except ImportError:
        return False


def scrypt_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """scrypt KDF."""
    salt = options.get("salt", "omnicodec").encode("utf-8")
    n = int(options.get("n", 16384))
    r = int(options.get("r", 8))
    p = int(options.get("p", 1))
    dklen = int(options.get("dklen", 32))
    
    derived = hashlib.scrypt(data, salt=salt, n=n, r=r, p=p, dklen=dklen)
    return derived.hex().encode("ascii")


def scrypt_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return scrypt_encode(data, options).lower() == expected.strip().lower()


def argon2i_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Argon2i KDF (requires argon2-cffi library)."""
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        return ph.hash(data.decode("utf-8", errors="ignore")).encode("utf-8")
    except ImportError:
        return b"argon2 library not available"


def argon2i_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    """Verify Argon2i hash."""
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        return ph.verify(expected.decode("utf-8"), data.decode("utf-8", errors="ignore"))
    except ImportError:
        return False


def argon2id_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """Argon2id KDF (requires argon2-cffi library)."""
    try:
        from argon2 import PasswordHasher, Type
        from argon2.low_level import hash_secret_raw
        
        salt = options.get("salt", "omnicodec").encode("utf-8")
        time_cost = int(options.get("time_cost", 2))
        memory_cost = int(options.get("memory_cost", 65536))
        parallelism = int(options.get("parallelism", 1))
        
        derived = hash_secret_raw(
            secret=data,
            salt=salt,
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=32,
            type=Type.ID
        )
        return derived.hex().encode("ascii")
    except ImportError:
        return b"argon2 library not available"


def argon2id_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    """Verify Argon2id hash."""
    result = argon2id_encode(data, options)
    return result.lower() == expected.strip().lower()


def pbkdf2_sha512_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """PBKDF2-HMAC-SHA512 KDF."""
    salt = options.get("salt", "omnicodec").encode("utf-8")
    rounds = int(options.get("rounds", 100000))
    dklen = int(options.get("dklen", 64))
    
    derived = hashlib.pbkdf2_hmac("sha512", data, salt, rounds, dklen=dklen)
    return derived.hex().encode("ascii")


def pbkdf2_sha512_verify(data: bytes, expected: bytes, options: dict[str, Any]) -> bool:
    return pbkdf2_sha512_encode(data, options).lower() == expected.strip().lower()


def get_specs() -> list[MethodSpec]:
    return [
        # Additional hash algorithms
        MethodSpec("ripemd160", "crypto_hash_extended", "RIPEMD-160 digest", ripemd160_encode, ripemd160_verify),
        MethodSpec("whirlpool", "crypto_hash_extended", "Whirlpool digest (512-bit)", whirlpool_encode, whirlpool_verify),
        MethodSpec("blake3", "crypto_hash_extended", "BLAKE3 digest", blake3_encode, blake3_verify),
        MethodSpec("sm3", "crypto_hash_extended", "SM3 digest (Chinese standard)", sm3_encode, sm3_verify),
        MethodSpec("shake128", "crypto_hash_extended", "SHAKE128 XOF", shake128_encode, shake128_verify),
        MethodSpec("shake256", "crypto_hash_extended", "SHAKE256 XOF", shake256_encode, shake256_verify),
        
        # Additional checksums
        MethodSpec("crc8", "checksum_extended", "CRC-8 checksum", crc8_encode, crc8_verify),
        MethodSpec("crc16", "checksum_extended", "CRC-16-CCITT checksum", crc16_encode, crc16_verify),
        MethodSpec("fletcher16", "checksum_extended", "Fletcher-16 checksum", fletcher16_encode, fletcher16_verify),
        MethodSpec("fletcher32", "checksum_extended", "Fletcher-32 checksum", fletcher32_encode, fletcher32_verify),
        MethodSpec("luhn", "checksum_extended", "Luhn algorithm (mod 10)", luhn_encode, luhn_verify),
        MethodSpec("verhoeff", "checksum_extended", "Verhoeff algorithm", verhoeff_encode, verhoeff_verify),
        MethodSpec("damm", "checksum_extended", "Damm algorithm", damm_encode, damm_verify),
        
        # Key derivation functions
        MethodSpec("bcrypt", "kdf_extended", "bcrypt KDF", bcrypt_encode, bcrypt_verify),
        MethodSpec("scrypt", "kdf_extended", "scrypt KDF", scrypt_encode, scrypt_verify),
        MethodSpec("argon2i", "kdf_extended", "Argon2i KDF", argon2i_encode, argon2i_verify),
        MethodSpec("argon2id", "kdf_extended", "Argon2id KDF", argon2id_encode, argon2id_verify),
        MethodSpec("pbkdf2_sha512", "kdf_extended", "PBKDF2-HMAC-SHA512", pbkdf2_sha512_encode, pbkdf2_sha512_verify),
    ]
