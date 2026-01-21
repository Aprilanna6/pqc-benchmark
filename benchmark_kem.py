import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Import HQC KEMs from pqcrypto library
from pqcrypto.kem.hqc_128 import generate_keypair as hqc128_gen, encrypt as hqc128_enc, decrypt as hqc128_dec
from pqcrypto.kem.hqc_192 import generate_keypair as hqc192_gen, encrypt as hqc192_enc, decrypt as hqc192_dec
from pqcrypto.kem.hqc_256 import generate_keypair as hqc256_gen, encrypt as hqc256_enc, decrypt as hqc256_dec

# Get profile from environment variable (Mobile, Laptop, Server)
profile = os.environ.get("PROFILE", "default")

# Make directory for results if it doesn't exist
os.makedirs(profile, exist_ok=True)

# List to store benchmark results
results = []

# -------------------------------
# Benchmark function for a single KEM
# -------------------------------
def benchmark_kem(name, gen, enc_func, dec_func):
    # Measure key generation
    t0 = time.perf_counter()
    public_key, secret_key = gen()
    t1 = time.perf_counter()

    # Measure encapsulation
    t2 = time.perf_counter()
    ciphertext, shared_key_enc = enc_func(public_key)
    t3 = time.perf_counter()

    # Measure decapsulation
    t4 = time.perf_counter()
    shared_key_dec = dec_func(secret_key, ciphertext)
    t5 = time.perf_counter()

    # Ensure shared keys match
    assert shared_key_enc == shared_key_dec

    # Save results
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
# Main execution
# -------------------------------
if __name__ == "__main__":
    # Run benchmarks for each KEM (128, 192, 256) in the current profile
    benchmark_kem("HQC-128", hqc128_gen, hqc128_enc, hqc128_dec)
    benchmark_kem("HQC-192", hqc192_gen, hqc192_enc, hqc192_dec)
    benchmark_kem("HQC-256", hqc256_gen, hqc256_enc, hqc256_dec)

    # -------------------------------
    # Save results to CSV
    # -------------------------------
    df = pd.DataFrame(results)
    csv_path = os.path.join(profile, "pqc_hqc_benchmark.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV saved: {csv_path}")

    # -------------------------------
    # Plot measured values (lines + markers)
    # -------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(df['PublicKeyBytes'], df['Encaps_ms'], 'o-', color='green', label='Encapsulation (measured)')
    plt.plot(df['PublicKeyBytes'], df['Decaps_ms'], 's-', color='red', label='Decapsulation (measured)')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title('HQC KEM: Key Size vs Encapsulation/Decapsulation Time (Measured)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    measured_plot = os.path.join(profile, "hqc_keysize_vs_time_measured.png")
    plt.savefig(measured_plot, dpi=300)
    plt.show()
    print(f"Measured plot saved: {measured_plot}")

    # -------------------------------
    # Extrapolation for larger keys
    # -------------------------------
    real_keys = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    # Fit power-law: t ~ key_size^b
    a_enc, b_enc = np.polyfit(np.log(real_keys), np.log(enc_times), 1)
    a_dec, b_dec = np.polyfit(np.log(real_keys), np.log(dec_times), 1)

    # Hypothetical future keys (larger sizes)
    keys_sim = np.array([2249, 4522, 7245, 10240, 14000])
    enc_sim = np.exp(a_enc * np.log(keys_sim) + b_enc)
    dec_sim = np.exp(a_dec * np.log(keys_sim) + b_dec)

    # -------------------------------
    # Plot extrapolated values (lines + markers)
    # -------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(real_keys, enc_times, 'o', color='green', label='Encapsulation (measured)')
    plt.plot(real_keys, dec_times, 's', color='red', label='Decapsulation (measured)')
    plt.plot(keys_sim, enc_sim, '--', color='green', label='Encapsulation (extrapolated)')
    plt.plot(keys_sim, dec_sim, '--', color='red', label='Decapsulation (extrapolated)')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title('HQC KEM: Key Size vs Encapsulation/Decapsulation Time (Extrapolated)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    extrapolated_plot = os.path.join(profile, "hqc_keysize_vs_time_extrapolated.png")
    plt.savefig(extrapolated_plot, dpi=300)
    plt.show()
    print(f"Extrapolated plot saved: {extrapolated_plot}")

