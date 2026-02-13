import os
import base64
import zlib

from kyber_py.kyber import Kyber512
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def kyber_generate_keypair():
    public_key, private_key = Kyber512.keygen()
    return public_key, private_key

def kyber_save_key(key: bytes, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(base64.b64encode(key).decode("ascii"))
        
def kyber_load_key(filename: str) -> bytes:
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip()
    return base64.b64decode(data)

def kyber_encapsulate(public_key: bytes):
    shared_secret, ciphertext = Kyber512.encaps(public_key)
    return ciphertext, shared_secret

def kyber_decapsulate(ciphertext: bytes, private_key: bytes):
    shared_secret = Kyber512.decaps(private_key, ciphertext)
    return shared_secret

_tmp_pk, _tmp_sk = Kyber512.keygen()
_tmp_ss, _tmp_ct = Kyber512.encaps(_tmp_pk)
KYBER_CT_LEN = len(_tmp_ct)
del _tmp_pk, _tmp_sk, _tmp_ss, _tmp_ct

def derive_aes_key(shared_secret: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"SecCW-Kyber-AES256GCM",
    )
    return hkdf.derive(shared_secret)

def pq_encrypt(message: bytes, public_key: bytes) -> bytes:
    kyber_ct, shared_secret = kyber_encapsulate(public_key)
    aes_key = derive_aes_key(shared_secret)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    aes_ct = aesgcm.encrypt(nonce, message, None)
    
    return kyber_ct + nonce + aes_ct

def pq_decrypt(data: bytes, private_key: bytes) -> bytes:
    kyber_ct = data[:KYBER_CT_LEN]
    nonce = data[KYBER_CT_LEN:KYBER_CT_LEN + 12]
    aes_ct = data[KYBER_CT_LEN + 12:]

    shared_secret = kyber_decapsulate(kyber_ct, private_key)
    aes_key = derive_aes_key(shared_secret)
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, aes_ct, None)

def pq_encrypt_compressed(message: bytes, public_key: bytes) -> bytes:
    compressed = zlib.compress(message)
    return pq_encrypt(compressed, public_key)

def pq_decrypt_compressed(data: bytes, private_key: bytes) -> bytes:
    compressed = pq_decrypt(data, private_key)
    return zlib.decompress(compressed)

def pq_encrypt_compressed_b64(message: bytes, public_key: bytes) -> bytes:
    data = pq_encrypt_compressed(message, public_key)
    return base64.b64encode(data).decode("ascii")

def pq_decrypt_compressed_b64(cipher_b64: bytes, private_key: bytes) -> bytes:
    data = base64.b64decode(cipher_b64.encode("ascii"))
    return pq_decrypt_compressed(data, private_key)

if __name__ == "__main__":
    pk, sk = kyber_generate_keypair()
    msg = b"Hello, post-quantum Morse world!"
    
    ct = pq_encrypt(msg, pk)
    pt = pq_decrypt(ct, sk)
    print("TEST simple", pt.decode())
    ct_c = pq_encrypt_compressed(msg, pk)
    pt_c = pq_decrypt_compressed(ct_c, sk)
    print("TEST compression", pt_c.decode())
    
    ct_b64 = pq_encrypt_compressed_b64(msg, pk)
    print("TEST B64 cipher (start)", ct_b64[:60], "...")
    pt_b64 = pq_decrypt_compressed_b64(ct_b64, sk)
    print("TEST B64 -> clear", pt_b64.decode())
