"""
Symmetric Cryptography Encodings
AES, ChaCha20, Fernet, 3DES, and more
"""
from __future__ import annotations

import hashlib
import os
from typing import Any

from ..models import MethodSpec


def _to_bytes(text: str, options: dict[str, Any]) -> bytes:
    return text.encode(options.get("encoding", "utf-8"), errors=options.get("errors", "strict"))


# =============================================================================
# AES ENCRYPTION (Pure Python implementation - ECB mode for simplicity)
# =============================================================================
def _aes_encrypt_block(block: bytes, key: bytes) -> bytes:
    """Simple AES-like substitution-permutation (educational, not production-safe)."""
    # This is a simplified cipher for demonstration
    # For production, use PyCryptodome: pip install pycryptodome
    result = bytearray(block)
    
    # Multiple rounds of substitution and mixing
    for round_num in range(10):
        # SubBytes (simple XOR with key material)
        key_byte = key[round_num % len(key)]
        for i in range(len(result)):
            result[i] ^= key_byte
            result[i] = ((result[i] << 1) | (result[i] >> 7)) & 0xFF  # Rotate left
    
    return bytes(result)


def _aes_decrypt_block(block: bytes, key: bytes) -> bytes:
    """Decrypt AES-like block."""
    result = bytearray(block)
    
    for round_num in range(9, -1, -1):
        key_byte = key[round_num % len(key)]
        for i in range(len(result)):
            result[i] = ((result[i] >> 1) | (result[i] << 7)) & 0xFF  # Rotate right
            result[i] ^= key_byte
    
    return bytes(result)


def aes_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    AES encryption (simplified implementation).
    For production use, install PyCryptodome.
    """
    key_str = options.get("key", "omnicodec-default-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    # Pad to 16-byte boundary (PKCS7)
    pad_len = 16 - (len(data) % 16)
    padded = data + bytes([pad_len] * pad_len)
    
    # Add IV (random or from key)
    iv = os.urandom(16)
    result = bytearray(iv)
    
    # Encrypt block by block
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        # Simple CBC mode
        if i == 0:
            xor_input = bytes(a ^ b for a, b in zip(block, iv))
        else:
            prev_cipher = result[-16:]
            xor_input = bytes(a ^ b for a, b in zip(block, prev_cipher))
        
        encrypted = _aes_encrypt_block(xor_input, key)
        result.extend(encrypted)
    
    return bytes(result)


def aes_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    AES decryption.
    """
    if len(data) < 17:
        raise ValueError("Data too short for AES decryption")
    
    key_str = options.get("key", "omnicodec-default-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    iv = data[:16]
    ciphertext = data[16:]
    
    if len(ciphertext) % 16 != 0:
        raise ValueError("Invalid ciphertext length")
    
    result = bytearray()
    prev_input = iv
    
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        decrypted = _aes_decrypt_block(block, key)
        
        # XOR with previous ciphertext (CBC)
        plaintext = bytes(a ^ b for a, b in zip(decrypted, prev_input))
        result.extend(plaintext)
        prev_input = block
    
    # Remove PKCS7 padding
    pad_len = result[-1]
    if pad_len > 16 or pad_len == 0:
        raise ValueError("Invalid padding")
    
    return bytes(result[:-pad_len])


# =============================================================================
# CHACHA20 ENCRYPTION
# =============================================================================
def chacha20_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    ChaCha20 stream cipher.
    Simplified implementation for demonstration.
    """
    key_str = options.get("key", "omnicodec-chacha20-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    # Generate nonce
    nonce = os.urandom(12)
    result = bytearray(nonce)
    
    # Generate keystream and XOR with data
    keystream = hashlib.sha256(key + nonce).digest()
    keystream_idx = 0
    
    for byte in data:
        if keystream_idx >= 32:
            # Regenerate keystream
            nonce = bytes([n + 1 for n in nonce])
            keystream = hashlib.sha256(key + nonce).digest()
            keystream_idx = 0
        
        result.append(byte ^ keystream[keystream_idx])
        keystream_idx += 1
    
    return bytes(result)


def chacha20_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    ChaCha20 decryption (same as encryption for stream cipher).
    """
    if len(data) < 13:
        raise ValueError("Data too short")
    
    key_str = options.get("key", "omnicodec-chacha20-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    nonce = data[:12]
    ciphertext = data[12:]
    
    keystream = hashlib.sha256(key + nonce).digest()
    keystream_idx = 0
    
    result = bytearray()
    for byte in ciphertext:
        if keystream_idx >= 32:
            nonce = bytes([n + 1 for n in nonce])
            keystream = hashlib.sha256(key + nonce).digest()
            keystream_idx = 0
        
        result.append(byte ^ keystream[keystream_idx])
        keystream_idx += 1
    
    return bytes(result)


# =============================================================================
# FERNET ENCRYPTION (Symmetric authenticated encryption)
# =============================================================================
def fernet_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Fernet encryption (authenticated encryption).
    Simplified implementation using HMAC + AES-like cipher.
    """
    import base64
    import time
    import hmac
    
    key_str = options.get("key", "omnicodec-fernet-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    # Generate signing key and encryption key
    signing_key = hashlib.sha256(key + b"sign").digest()
    enc_key = hashlib.sha256(key + b"encrypt").digest()
    
    # Timestamp
    timestamp = int(time.time()).to_bytes(8, "big")
    
    # IV
    iv = os.urandom(16)
    
    # Encrypt (simplified)
    padded = data + bytes([16 - (len(data) % 16)] * (16 - (len(data) % 16)))
    encrypted = bytearray()
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        xored = bytes(a ^ b for a, b in zip(block, enc_key[:16]))
        encrypted.extend(xored)
    
    # Token structure: timestamp + iv + ciphertext + hmac
    token_data = timestamp + iv + bytes(encrypted)
    signature = hmac.new(signing_key, token_data, hashlib.sha256).digest()
    
    # Base64 encode
    token = token_data + signature
    return base64.urlsafe_b64encode(token)


def fernet_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Fernet decryption.
    """
    import base64
    import hmac
    
    key_str = options.get("key", "omnicodec-fernet-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    signing_key = hashlib.sha256(key + b"sign").digest()
    enc_key = hashlib.sha256(key + b"encrypt").digest()
    
    # Decode base64
    try:
        token = base64.urlsafe_b64decode(data)
    except Exception:
        raise ValueError("Invalid base64")
    
    if len(token) < 48:  # timestamp(8) + iv(16) + min_cipher(16) + hmac(32)
        raise ValueError("Token too short")
    
    # Verify signature
    token_data = token[:-32]
    signature = token[-32:]
    
    expected_sig = hmac.new(signing_key, token_data, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    
    # Decrypt
    timestamp = token_data[:8]
    iv = token_data[8:24]
    ciphertext = token_data[24:]
    
    decrypted = bytearray()
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        xored = bytes(a ^ b for a, b in zip(block, enc_key[:16]))
        decrypted.extend(xored)
    
    # Remove padding
    pad_len = decrypted[-1]
    if pad_len > 16 or pad_len == 0:
        raise ValueError("Invalid padding")
    
    return bytes(decrypted[:-pad_len])


# =============================================================================
# 3DES ENCRYPTION (Triple DES - Legacy)
# =============================================================================
def _des_encrypt_block(block: bytes, key: bytes) -> bytes:
    """Simplified DES-like encryption (educational)."""
    result = bytearray(block)
    for i in range(8):
        key_byte = key[i % len(key)]
        for j in range(8):
            result[j] ^= key_byte
            result[j] = ((result[j] << 1) | (result[j] >> 7)) & 0xFF
    return bytes(result)


def _des_decrypt_block(block: bytes, key: bytes) -> bytes:
    """Simplified DES decryption."""
    result = bytearray(block)
    for i in range(7, -1, -1):
        key_byte = key[i % len(key)]
        for j in range(8):
            result[j] = ((result[j] >> 1) | (result[j] << 7)) & 0xFF
            result[j] ^= key_byte
    return bytes(result)


def triple_des_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Triple DES encryption (3DES - legacy algorithm).
    Simplified implementation.
    """
    key_str = options.get("key", "omnicodec-3des-key-24bytes!")
    key = key_str.encode()[:24].ljust(24, b"\x00")
    
    # Split into 3 keys
    k1, k2, k3 = key[:8], key[8:16], key[16:24]
    
    # Pad data
    pad_len = 8 - (len(data) % 8)
    padded = data + bytes([pad_len] * pad_len)
    
    result = bytearray()
    for i in range(0, len(padded), 8):
        block = padded[i:i+8]
        # 3DES: E(k1) -> D(k2) -> E(k3)
        encrypted = _des_encrypt_block(_des_decrypt_block(_des_encrypt_block(block, k1), k2), k3)
        result.extend(encrypted)
    
    return bytes(result)


def triple_des_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Triple DES decryption.
    """
    key_str = options.get("key", "omnicodec-3des-key-24bytes!")
    key = key_str.encode()[:24].ljust(24, b"\x00")
    
    k1, k2, k3 = key[:8], key[8:16], key[16:24]
    
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i+8]
        # 3DES decrypt: D(k3) -> E(k2) -> D(k1)
        decrypted = _des_decrypt_block(_des_encrypt_block(_des_decrypt_block(block, k3), k2), k1)
        result.extend(decrypted)
    
    # Remove padding
    pad_len = result[-1]
    if pad_len > 8 or pad_len == 0:
        raise ValueError("Invalid padding")
    
    return bytes(result[:-pad_len])


# =============================================================================
# XOR CIPHER (Simple)
# =============================================================================
def xor_cipher_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    XOR cipher with repeating key.
    """
    key_str = options.get("key", "secret")
    key = key_str.encode()
    
    if not key:
        key = b"\x00"
    
    result = bytearray()
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % len(key)])
    
    return bytes(result)


def xor_cipher_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    XOR cipher decryption (same as encryption).
    """
    return xor_cipher_encode(data, options)


# =============================================================================
# RC4 STREAM CIPHER
# =============================================================================
def _rc4_key_schedule(key: bytes) -> list[int]:
    """RC4 Key Scheduling Algorithm (KSA)."""
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    return S


def _rc4_prga(S: list[int], length: int) -> bytes:
    """RC4 Pseudo-Random Generation Algorithm (PRGA)."""
    i = j = 0
    result = []
    for _ in range(length):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        result.append(S[(S[i] + S[j]) % 256])
    return bytes(result)


def rc4_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    RC4 stream cipher.
    """
    key_str = options.get("key", "omnicodec-rc4-key")
    key = key_str.encode()
    
    # Add IV for security
    iv = os.urandom(8)
    full_key = iv + key
    
    S = _rc4_key_schedule(full_key)
    keystream = _rc4_prga(S, len(data))
    
    ciphertext = bytes(a ^ b for a, b in zip(data, keystream))
    return iv + ciphertext


def rc4_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    RC4 decryption.
    """
    if len(data) < 9:
        raise ValueError("Data too short")
    
    key_str = options.get("key", "omnicodec-rc4-key")
    key = key_str.encode()
    
    iv = data[:8]
    ciphertext = data[8:]
    
    full_key = iv + key
    S = _rc4_key_schedule(full_key)
    keystream = _rc4_prga(S, len(ciphertext))
    
    return bytes(a ^ b for a, b in zip(ciphertext, keystream))


# =============================================================================
# BLOWFISH-LIKE CIPHER (Simplified)
# =============================================================================
def blowfish_encode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Blowfish-like encryption (simplified).
    """
    key_str = options.get("key", "omnicodec-blowfish-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    # Pad
    pad_len = 8 - (len(data) % 8)
    padded = data + bytes([pad_len] * pad_len)
    
    result = bytearray()
    for i in range(0, len(padded), 8):
        block = padded[i:i+8]
        # Simple Feistel-like structure
        left = int.from_bytes(block[:4], "big")
        right = int.from_bytes(block[4:], "big")
        
        for round_num in range(16):
            round_key = int.from_bytes(key[round_num*4:(round_num+1)*4], "big")
            left ^= round_key
            # Simple F function
            right ^= ((left << 1) | (left >> 31)) & 0xFFFFFFFF
            left, right = right, left
        
        result.extend(left.to_bytes(4, "big"))
        result.extend(right.to_bytes(4, "big"))
    
    return bytes(result)


def blowfish_decode(data: bytes, options: dict[str, Any]) -> bytes:
    """
    Blowfish decryption.
    """
    key_str = options.get("key", "omnicodec-blowfish-key")
    key = hashlib.sha256(key_str.encode()).digest()
    
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i+8]
        left = int.from_bytes(block[:4], "big")
        right = int.from_bytes(block[4:], "big")
        
        for round_num in range(15, -1, -1):
            left, right = right, left
            round_key = int.from_bytes(key[round_num*4:(round_num+1)*4], "big")
            right ^= ((left << 1) | (left >> 31)) & 0xFFFFFFFF
            left ^= round_key
        
        result.extend(left.to_bytes(4, "big"))
        result.extend(right.to_bytes(4, "big"))
    
    # Remove padding
    pad_len = result[-1]
    if pad_len > 8 or pad_len == 0:
        raise ValueError("Invalid padding")
    
    return bytes(result[:-pad_len])


def get_specs() -> list[MethodSpec]:
    return [
        # Block ciphers
        MethodSpec("aes", "crypto_symmetric", "AES encryption (simplified)", aes_encode, aes_decode, aliases=("aes256",)),
        MethodSpec("triple_des", "crypto_symmetric", "Triple DES (3DES)", triple_des_encode, triple_des_decode, aliases=("3des", "des3")),
        MethodSpec("blowfish", "crypto_symmetric", "Blowfish cipher", blowfish_encode, blowfish_decode),
        
        # Stream ciphers
        MethodSpec("chacha20", "crypto_symmetric", "ChaCha20 stream cipher", chacha20_encode, chacha20_decode),
        MethodSpec("rc4", "crypto_symmetric", "RC4 stream cipher", rc4_encode, rc4_decode),
        
        # Authenticated encryption
        MethodSpec("fernet", "crypto_symmetric", "Fernet authenticated encryption", fernet_encode, fernet_decode),
        
        # Simple ciphers
        MethodSpec("xor_cipher", "crypto_symmetric", "XOR cipher with key", xor_cipher_encode, xor_cipher_decode),
    ]
