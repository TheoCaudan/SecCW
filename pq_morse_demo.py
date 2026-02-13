#!/usr/bin/env python
import sys
from pq_crypto import(
    kyber_generate_keypair,
    kyber_save_key,
    kyber_load_key,
    pq_encrypt_compressed_b64,
)
from CWToCS8 import convert_to_CW, write_toCS8

PUBLIC_KEY_FILE = "kyber_pk.b64"
PRIVATE_KEY_FILE = "kyber_sk.b64"

def get_or_create_keypair():
    try:
        pk = kyber_load_key(PUBLIC_KEY_FILE)
        sk = kyber_load_key(PRIVATE_KEY_FILE)
        print("[i] Existing keys loaded")
    except FileNotFoundError:
        print("[i] No pre-generated keys found, generating new keys")
        pk, sk = kyber_generate_keypair()
        kyber_save_key(pk, PUBLIC_KEY_FILE)
        kyber_save_key(sk, PRIVATE_KEY_FILE)
        print(f"[OUT] Generated keys in {PUBLIC_KEY_FILE} / {PRIVATE_KEY_FILE}")
    return pk, sk

def demo_enc(plaintext: str, output_file: str, modulation: str):
    pk, sk = get_or_create_keypair()
    
    msg_bytes = plaintext.encode("utf-8")
    cipher_b64 = pq_encrypt_compressed_b64(msg_bytes, pk)
    print("[OUT] Ciphertext Base64 (start) :", cipher_b64[:80], "...")
    
    IQ = convert_to_CW(cipher_b64, modulation)
    write_toCS8(IQ, output_file)
    
    print(f"[OUT] CS8 file generated : {output_file}")
    print(f"[OUT] Modulation         : {modulation}")
    print("[i] Encryption chain demo has ended")
    
def usage():
    print("Usage :")
    print("  Encoding demo :")
    print("    python pq_morse_demo.py enc \"<message_text>\" <output_file.cs8> <AM|FM>")
    print("")
    print("E.g.:")
    print("  python pq_morse_demo.py enc \"Hello RF world\" out.cs8 AM")
    
def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "enc":
        if len(sys.argv) != 5:
            usage()
            sys.exit(1)
        message_clair = sys.argv[2]
        output_file = sys.argv[3]
        modulation = sys.argv[4].upper()
        demo_enc(message_clair, output_file, modulation)

    else:
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
