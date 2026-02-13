# PQ-CW : Alternative PQ à AVC (Kyber512 + AES-GCM sur Morse)

Ce dépôt montre une chaîne complète :

> message clair --> Kyber512 + AES-GCM (compressé) --> Base64 --> Morse CW --> IQ CS8

avec des outils optimisés pour l'analyse (FFT)

---

## 1. pq_crypto.py

- Chiffrement hybride **Kyber512 + AES-GCM**
- Version compressée:
    - `pq_encrypt_compressed(message, pk)`
    - `pq_decrypt_compressed(data, sk)`
- Version prête pour Morse:
    - `pq_encrypt_compressed_b64(message, pk) -> str`
    - `pq_decrypt_compressed_b64(cipher_b64, sk) -> bytes`
- Gestion des clefs (save/load Base64):
    - `kyber_generate_keypair()`
    - `kyber_save_key(key, filename)`
    - `kyber_load_key(filename)`

Tests :

```bash
python test_pq.py
```

# 2. CWToCS8.py

Convertit du texte ou un cipher Base64 en Morse CW, puis en fichier IQ CS8 (AM/FM)

- Mode PLAINTEXT (message en clair)
- Mode CIPHER_B64 (cipher PQ Base64)
- Mapping Morse enrichi pour Base64 (+, /, =)
- Generation AM/FM en CS8

Usage :

```bash
#Message en clair
python CWToCS8.py PLAINTEXT "hello world" out_plain.cs8 AM

#Cipher PQ en Base64
python CWToCS8.py CIPHER_B64 "<cipher_b64>" out_cipher.cs8 AM
```

# 3. ReadCS8.py

Analyse d'un fichier CS8 :

- Modes: amplitude, fft, iq, all
- FFT optimisée:
    - backend FFTW (pyFFTW)
    - taille puissance de 2
    - limitation --max-fft-samples pour eviter les FFT géantes
- Axes temps/fréquences corrects
- Option --save pour exporter les figures .png au lieu de les afficher

Exemples:

```bash
#Amplitude vs temps
python ReadCS8.py out.cs8 --mode amplitude

#FFT seule (limité à 1M d'échantillons)
python ReadCS8.py out.cs8 --mod fft --max-fft-samples 1048576

#Tout (IQ + amplitude + FFT)
python readCS8.py out.cs8 --mode all
```

# 4. pq_morse_demo.py (demo)

Demonstration du flux complet d'émission:

> message clair --> PQ crypto (compressé + Base64) --> CW --> CS8

Usage:

```bash
python pq_morse_demo.py enc "Hello RF world" out.cs8 AM
```

Ce script charge ou genere une paire de clefs :

- `kyber_pk.b64` (publique)
- `kyber_sk.b64` (privée)

Il chiffre + compresse + encode en Base64 :

- `pq_encrypt_compressed_b64`

Et il convertit le Base64 en CW puis en CS8 :

- `convert_to_CW`, `write_toCS8`

# 5. Notes sur les clefs

- `kyber_pk.b64` : clef publique (souvent utilisée comme clef semi-publique dans notre contexte => publique seulement pour un nombre limitée de personne)
- `kyber_sk.b64` : clef privée, à protéger.
