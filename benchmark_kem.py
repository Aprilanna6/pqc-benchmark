import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# importierbare KEMs aus pqcrypto
from pqcrypto.kem.hqc_128 import generate_keypair as hqc128_gen, encrypt as hqc128_enc, decrypt as hqc128_dec
from pqcrypto.kem.hqc_192 import generate_keypair as hqc192_gen, encrypt as hqc192_enc, decrypt as hqc192_dec
from pqcrypto.kem.hqc_256 import generate_keypair as hqc256_gen, encrypt as hqc256_enc, decrypt as hqc256_dec

# Profil aus Umgebungsvariable (z.B. Handy, Laptop, Server)
profile = os.environ.get("PROFILE", "default")
os.makedirs(profile, exist_ok=True)

results = []

def benchmark_kem(name, gen, enc_func, dec_func):
    t0 = time.perf_counter()
    public_key, secret_key = gen()
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    ciphertext, shared_key_enc = enc_func(public_key)
    t3 = time.perf_counter()

    t4 = time.perf_counter()
    shared_key_dec = dec_func(secret_key, ciphertext)
    t5 = time.perf_counter()

    assert shared_key_enc == shared_key_dec

    results.append({
        "Algorithm": name,
        "PublicKeyBytes": len(public_key),
        "SecretKeyBytes": len(secret_key),
        "CiphertextBytes": len(ciphertext),
        "SharedKeyBytes": len(shared_key_enc),
        "KeyGen_ms": (t1 - t0) * 1000,
        "Encaps_ms": (t3 - t2) * 1000,
        "Decaps_ms": (t5 - t4) * 1000
    })
    print(f"{name} KEM done")

if __name__ == "__main__":
    # Benchmarks ausführen
    benchmark_kem("HQC-128", hqc128_gen, hqc128_enc, hqc128_dec)
    benchmark_kem("HQC-192", hqc192_gen, hqc192_enc, hqc192_dec)
    benchmark_kem("HQC-256", hqc256_gen, hqc256_enc, hqc256_dec)

    # CSV speichern
    df = pd.DataFrame(results)
    csv_path = os.path.join(profile, "pqc_hqc_benchmark.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV gespeichert: {csv_path}")

    # --- Plot der echten Werte ---
    plt.figure(figsize=(8, 6))
    plt.plot(df['PublicKeyBytes'], df['Encaps_ms'], marker='o', linestyle='-', color='blue',
             label='Encapsulation (gemessen)')
    plt.plot(df['PublicKeyBytes'], df['Decaps_ms'], marker='s', linestyle='-', color='red',
             label='Decapsulation (gemessen)')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title('HQC KEM: Key Size vs Encapsulation/Decapsulation Time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(profile, "hqc_keysize_vs_time.png"), dpi=300)
    plt.show()
    print(f"Plot gespeichert: {os.path.join(profile, 'hqc_keysize_vs_time.png')}")

    # --- Extrapolation für höhere Sicherheitslevel ---
    real_keys = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    # Fit Potenzfunktion: t ~ key^b
    a_enc, b_enc = np.polyfit(np.log(real_keys), np.log(enc_times), 1)
    a_dec, b_dec = np.polyfit(np.log(real_keys), np.log(dec_times), 1)

    # Neue hypothetische Keys für Zukunftsszenarien
    keys_sim = np.array([2249, 4522, 7245, 10240, 14000])
    enc_sim = np.exp(a_enc * np.log(keys_sim) + b_enc)
    dec_sim = np.exp(a_dec * np.log(keys_sim) + b_dec)

    # --- Plot extrapolierte Werte ---
    plt.figure(figsize=(8, 6))
    plt.plot(real_keys, enc_times, 'o', color='blue', label='Encapsulation (gemessen)')
    plt.plot(real_keys, dec_times, 's', color='red', label='Decapsulation (gemessen)')
    plt.plot(keys_sim, enc_sim, '--', color='blue', label='Encapsulation (extrapoliert)')
    plt.plot(keys_sim, dec_sim, '--', color='red', label='Decapsulation (extrapoliert)')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title('HQC KEM: Key Size vs Encapsulation/Decapsulation Time (extrapolated)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(profile, "hqc_keysize_vs_time_extrapolated.png"), dpi=300)
    plt.show()
    print(f"Extrapolierter Plot gespeichert: {os.path.join(profile, 'hqc_keysize_vs_time_extrapolated.png')}")

