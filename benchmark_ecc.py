import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Get profile from environment variable
profile = os.environ.get("PROFILE", "default")

# Make directory for results if it doesn't exist
os.makedirs(profile, exist_ok=True)

# List to store benchmark results
results = []

# -------------------------------
# Benchmark function for a single ECC curve
# -------------------------------
def benchmark_ecc(name, curve):
    # Generate key
    t0 = time.perf_counter()
    private_key = ec.generate_private_key(curve())
    public_key = private_key.public_key()
    t1 = time.perf_counter()

    # Serialize public key (for size)
    t2 = time.perf_counter()
    pk_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    t3 = time.perf_counter()

    # "Encapsulation": ECDH to derive shared key with itself (for benchmarking)
    t4 = time.perf_counter()
    shared_key_enc = private_key.exchange(ec.ECDH(), public_key)
    t5 = time.perf_counter()

    # "Decapsulation": same operation
    t6 = time.perf_counter()
    shared_key_dec = private_key.exchange(ec.ECDH(), public_key)
    t7 = time.perf_counter()

    assert shared_key_enc == shared_key_dec

    results.append({
        "Algorithm": name,
        "PublicKeyBytes": len(pk_bytes),
        "KeyGen_ms": (t1 - t0) * 1000,
        "Encapsulation_ms": (t5 - t4) * 1000,
        "Decapsulation_ms": (t7 - t6) * 1000
    })

    print(f"{name} done")

# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    curves = [
        ("secp256r1", ec.SECP256R1),
        ("secp384r1", ec.SECP384R1),
        ("secp521r1", ec.SECP521R1)
    ]

    for name, curve in curves:
        benchmark_ecc(name, curve)

    # -------------------------------
    # Save results to CSV
    # -------------------------------
    df = pd.DataFrame(results)
    csv_path = os.path.join(profile, "ecc_benchmark.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV saved: {csv_path}")

    # -------------------------------
    # Plot measured values
    # -------------------------------
    plt.figure(figsize=(10,6))
    plt.plot(df['PublicKeyBytes'], df['Encapsulation_ms'], 'o-', color='green', label='Encapsulation')
    plt.plot(df['PublicKeyBytes'], df['Decapsulation_ms'], 's-', color='red', label='Decapsulation')
    plt.xlabel('Public Key Size (Bytes)')
    plt.ylabel('Time (ms)')
    plt.title(f'ECC: Key Size vs Encapsulation/Decapsulation Time ({profile})')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plot_path = os.path.join(profile, "ecc_keysize_vs_time.png")
    plt.savefig(plot_path, dpi=300)
    plt.show()
    print(f"Plot saved: {plot_path}")

