import os
from kyber_py.kyber import Kyber512 
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def kyber_generate_keypair():
    public_key, private_key = Kyber512.keygen()  
    return public_key, private_key

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
