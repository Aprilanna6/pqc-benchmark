import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Import Classic McEliece KEMs from pqcrypto
from pqcrypto.kem.mceliece348864 import (
    generate_keypair as mc348864_gen,
    encrypt as mc348864_enc,
    decrypt as mc348864_dec,
)

from pqcrypto.kem.mceliece6688128 import (
    generate_keypair as mc6688128_gen,
    encrypt as mc6688128_enc,
    decrypt as mc6688128_dec,
)

from pqcrypto.kem.mceliece8192128 import (
    generate_keypair as mc8192128_gen,
    encrypt as mc8192128_enc,
    decrypt as mc8192128_dec,
)

# Get profile from environment variable (Mobile, Laptop, Server)
profile = os.environ.get("PROFILE", "default")

# Make directory for results if it doesn't exist
os.makedirs(profile, exist_ok=True)

# Store benchmark results
results = []

# -------------------------------
# Benchmark function (IDENTICAL to HQC / ML-KEM)
# -------------------------------
def benchmark_kem(name, gen, enc_func, dec_func):
    # Key generation
    t0 = time.perf_counter()
    public_key, secret_key = gen()
    t1 = time.perf_counter()

    # Encapsulation
    t2 = time.perf_counter()
    ciphertext, shared_key_enc = enc_func(public_key)
    t3 = time.perf_counter()

    # Decapsulation
    t4 = time.perf_counter()
    shared_key_dec = dec_func(secret_key, ciphertext)
    t5 = time.perf_counter()

    # Sanity check
    assert shared_key_enc == shared_key_dec

    results.append({
        "Algorithm": name,
        "PublicKeyBytes": len(public_key),
        "SecretKeyBytes": len(secret_key),
        "CiphertextBytes": len(ciphertext),
        "SharedKeyBytes": len(shared_key_enc),
        "KeyGen_ms": (t1 - t0) * 1000,
        "Encaps_ms": (t3 - t2) * 1000,
        "Decaps_ms": (t5 - t4) * 1000,
    })

    print(f"{name} KEM done")

# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":

    # Run benchmarks (one per NIST level)
    benchmark_kem("McEliece-348864", mc348864_gen, mc348864_enc, mc348864_dec)
    benchmark_kem("McEliece-6688128", mc6688128_gen, mc6688128_enc, mc6688128_dec)
    benchmark_kem("McEliece-8192128", mc8192128_gen, mc8192128_enc, mc8192128_dec)

    # -------------------------------
    # Save results to CSV
    # -------------------------------
    df = pd.DataFrame(results)
    csv_path = os.path.join(profile, "pqc_mceliece_benchmark.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV saved: {csv_path}")

    # -------------------------------
    # Plot measured values (lines + markers)
    # -------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(df['PublicKeyBytes'], df['Encaps_ms'], 'o-', label='Encapsulation (measured)')
    plt.plot(df['PublicKeyBytes'], df['Decaps_ms'], 's-', label='Decapsulation (measured)')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title('Classic McEliece: Key Size vs Encapsulation/Decapsulation Time (Measured)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    measured_plot = os.path.join(profile, "mceliece_keysize_vs_time_measured.png")
    plt.savefig(measured_plot, dpi=300)
    plt.show()
    print(f"Measured plot saved: {measured_plot}")

    # -------------------------------
    # Extrapolation (same model as HQC)
    # -------------------------------
    real_keys = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    # Power-law fit: t ~ key_size^b
    a_enc, b_enc = np.polyfit(np.log(real_keys), np.log(enc_times), 1)
    a_dec, b_dec = np.polyfit(np.log(real_keys), np.log(dec_times), 1)

    # Hypothetical larger keys
    keys_sim = np.array([200_000, 400_000, 800_000, 1_600_000])
    enc_sim = np.exp(a_enc * np.log(keys_sim) + b_enc)
    dec_sim = np.exp(a_dec * np.log(keys_sim) + b_dec)

    # -------------------------------
    # Plot extrapolated values
    # -------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(real_keys, enc_times, 'o', label='Encapsulation (measured)')
    plt.plot(real_keys, dec_times, 's', label='Decapsulation (measured)')
    plt.plot(keys_sim, enc_sim, '--', label='Encapsulation (extrapolated)')
    plt.plot(keys_sim, dec_sim, '--', label='Decapsulation (extrapolated)')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title('Classic McEliece: Key Size vs Encapsulation/Decapsulation Time (Extrapolated)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    extrapolated_plot = os.path.join(profile, "mceliece_keysize_vs_time_extrapolated.png")
    plt.savefig(extrapolated_plot, dpi=300)
    plt.show()
    print(f"Extrapolated plot saved: {extrapolated_plot}")

