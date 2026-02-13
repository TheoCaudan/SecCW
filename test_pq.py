#!/usr/bin/env python
import os
from pq_crypto import (
    kyber_generate_keypair,
    pq_encrypt,
    pq_decrypt,
    pq_encrypt_compressed,
    pq_decrypt_compressed,
    pq_encrypt_compressed_b64,
    pq_decrypt_compressed_b64,
    )

def test_basic():
    pk, sk = kyber_generate_keypair()
    message = b"Test PQ crypto Kyber512 + AES-GCM (basic mode)"
    
    ciphertext = pq_encrypt(message, pk)
    decrypted = pq_decrypt(ciphertext, sk)
    
    assert decrypted == message
    print("[OK] test_basic : simple encrypt/decrypt")
    
def test_compressed():
    pk, sk = kyber_generate_keypair()
    message = b"Test PQ crypto Kyber512 + AES-GCM (compressed mode)"
    
    cipher_comp = pq_encrypt_compressed(message, pk)
    decrypted = pq_decrypt_compressed(cipher_comp, sk)
    
    assert decrypted == message
    print("[OK] test_compressed : compressed encrypt/decrypt")
    
def test_compressed_b64():
    pk, sk = kyber_generate_keypair()
    message = b"Test PQ crypto Kyber512 + AES-GCM (compressed + base64 mode)"
    
    cipher_b64 = pq_encrypt_compressed_b64(message, pk)
    decrypted = pq_decrypt_compressed_b64(cipher_b64, sk)
    
    assert decrypted == message
    print("[OK] test_compressed_b64 : compressed Base64 encrypt/decrypt")
    
def test_random_messages(iterations=10):
    pk, sk = kyber_generate_keypair()
    for i in range(iterations):
        msg_len = os.urandom(1)[0]
        message = os.urandom(msg_len)
        
        ct = pq_encrypt(message, pk)
        pt = pq_decrypt(ct, sk)
        assert pt == message
        
        ct_c = pq_encrypt_compressed(message, pk)
        pt_c = pq_decrypt_compressed(ct_c, sk)
        assert pt_c == message
        
    print(f"[OK] test_random_messages : {iterations} simple and compressed random messages")
    
if __name__ == "__main__":
    test_basic()
    test_compressed()
    test_compressed_b64()
    test_random_messages()
    print("[OUT] All the tests have been a success")
