import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------
# Import ML-KEMs aus pqcrypto
# -------------------------------
from pqcrypto.kem.ml_kem_512 import generate_keypair as ml512_gen, encrypt as ml512_enc, decrypt as ml512_dec
from pqcrypto.kem.ml_kem_768 import generate_keypair as ml768_gen, encrypt as ml768_enc, decrypt as ml768_dec
from pqcrypto.kem.ml_kem_1024 import generate_keypair as ml1024_gen, encrypt as ml1024_enc, decrypt as ml1024_dec

# -------------------------------
# Profil / Arbeitsverzeichnis
# -------------------------------
profile = os.environ.get("PROFILE", "default")
os.makedirs(profile, exist_ok=True)
results = []

# -------------------------------
# Benchmark-Funktion
# -------------------------------
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

    # Prüfen, dass beide Shared Keys übereinstimmen
    assert shared_key_enc == shared_key_dec

    # Ergebnisse speichern
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

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    benchmark_kem("ML-KEM-512", ml512_gen, ml512_enc, ml512_dec)
    benchmark_kem("ML-KEM-768", ml768_gen, ml768_enc, ml768_dec)
    benchmark_kem("ML-KEM-1024", ml1024_gen, ml1024_enc, ml1024_dec)
    
    # -------------------------------
    # Save results to CSV
    # -------------------------------
    df = pd.DataFrame(results)
    csv_path = os.path.join(profile, "pqc_mlkem_benchmark.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV saved: {csv_path}")

    # -------------------------------
    # Plot measured values
    # -------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(df["PublicKeyBytes"], df["Encaps_ms"], "o-", color="green", label="Encapsulation (measured)")
    plt.plot(df["PublicKeyBytes"], df["Decaps_ms"], "s-", color="red", label="Decapsulation (measured)")
    plt.xlabel("Public Key Size (Bytes)")
    plt.ylabel("Time (ms)")
    plt.title("ML-KEM: Key Size vs Encapsulation/Decapsulation Time (Measured)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    measured_plot = os.path.join(profile, "mlkem_keysize_vs_time_measured.png")
    plt.savefig(measured_plot, dpi=300)
    plt.show()
    print(f"Measured plot saved: {measured_plot}")

    # -------------------------------
    # Extrapolation for larger keys
    # -------------------------------
    real_keys = np.array(df["PublicKeyBytes"])
    enc_times = np.array(df["Encaps_ms"])
    dec_times = np.array(df["Decaps_ms"])

    # Fit power-law: t ~ key_size^b
    a_enc, b_enc = np.polyfit(np.log(real_keys), np.log(enc_times), 1)
    a_dec, b_dec = np.polyfit(np.log(real_keys), np.log(dec_times), 1)

    keys_sim = np.array([2249, 4522, 7245, 10240, 14000])
    enc_sim = np.exp(a_enc * np.log(keys_sim) + b_enc)
    dec_sim = np.exp(a_dec * np.log(keys_sim) + b_dec)

    # -------------------------------
    # Plot extrapolated values (Messpunkte + Linie)
    # -------------------------------
    plt.figure(figsize=(10, 6))

    # Messpunkte
    plt.plot(real_keys, enc_times, "o", color="green", label="Encapsulation (measured)")
    plt.plot(real_keys, dec_times, "s", color="red", label="Decapsulation (measured)")

    # Kombiniere Messpunkte und extrapolierte Punkte für Linie
    all_keys_enc = np.concatenate([real_keys, keys_sim])
    all_enc = np.concatenate([enc_times, enc_sim])
    all_keys_dec = np.concatenate([real_keys, keys_sim])
    all_dec = np.concatenate([dec_times, dec_sim])

    plt.plot(all_keys_enc, all_enc, "--", color="green", label="Encapsulation (extrapolated)")
    plt.plot(all_keys_dec, all_dec, "--", color="red", label="Decapsulation (extrapolated)")

    plt.xlabel("Public Key Size (Bytes)")
    plt.ylabel("Time (ms)")
    plt.title("ML-KEM: Key Size vs Encapsulation/Decapsulation Time (Extrapolated)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    extrapolated_plot = os.path.join(profile, "mlkem_keysize_vs_time_extrapolated.png")
    plt.savefig(extrapolated_plot, dpi=300)
    plt.show()
    print(f"Extrapolated plot saved: {extrapolated_plot}")

