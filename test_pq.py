from pq_crypto import kyber_generate_keypair, pq_encrypt, pq_decrypt


def main():
    public_key, private_key = kyber_generate_keypair()
    print("Clé publique Kyber :", public_key.hex()[:60], "…")
    print("Clé privée Kyber  :", private_key.hex()[:60], "…")

    message = b"test chiffrement PQ"
    print("\nMessage original :", message)

    encrypted = pq_encrypt(message, public_key)
    print("\nMessage chiffré (hex, tronqué) :", encrypted.hex()[:80], "…")

    decrypted = pq_decrypt(encrypted, private_key)
    print("\nMessage déchiffré :", decrypted)

    if decrypted == message:
        print("\nSuccès : le message a été correctement déchiffré !")
    else:
        print("\nErreur : le message déchiffré ne correspond pas à l'original.")


if __name__ == "__main__":
    main()
