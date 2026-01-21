import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

profiles = ["Mobile", "Laptop", "Server"]
marker_map = {"Mobile": "o", "Laptop": "^", "Server": "s"}  # Marker per profile
linestyles = {"Mobile": "-", "Laptop": "--", "Server": "-."}  # Line styles for extrapolated

color_enc = "green"
color_dec = "red"

# -------------------------------
# 1. Measured values (lines + markers, all profiles combined)
# -------------------------------
plt.figure(figsize=(10, 6))

for profile in profiles:
    csv_path = os.path.join(profile, "pqc_hqc_benchmark.csv")
    if not os.path.exists(csv_path):
        print(f"CSV for {profile} not found, skipping...")
        continue

    df = pd.read_csv(csv_path)
    keys = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    plt.plot(keys, enc_times,
             marker=marker_map[profile],
             linestyle='-',
             color=color_enc,
             label=f'{profile} Encapsulation')

    plt.plot(keys, dec_times,
             marker=marker_map[profile],
             linestyle='-',
             color=color_dec,
             label=f'{profile} Decapsulation')

plt.xlabel('Public Key Size (Bytes)')
plt.ylabel('Time (ms)')
plt.title('HQC KEM: All Profiles (Measured Values)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("combined_hqc_measured.png", dpi=300)
plt.show()
print("Measured values plot saved: combined_hqc_measured.png")

# -------------------------------
# 2. Extrapolated values (lines + markers, all profiles combined)
# -------------------------------
plt.figure(figsize=(10, 6))

for profile in profiles:
    csv_path = os.path.join(profile, "pqc_hqc_benchmark.csv")
    if not os.path.exists(csv_path):
        continue

    df = pd.read_csv(csv_path)
    keys_real = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    a_enc, b_enc = np.polyfit(np.log(keys_real), np.log(enc_times), 1)
    a_dec, b_dec = np.polyfit(np.log(keys_real), np.log(dec_times), 1)

    keys_sim = np.array([2249, 4522, 7245, 10240, 14000])
    enc_sim = np.exp(a_enc * np.log(keys_sim) + b_enc)
    dec_sim = np.exp(a_dec * np.log(keys_sim) + b_dec)

    plt.plot(keys_sim, enc_sim,
             linestyle=linestyles[profile],
             color=color_enc,
             marker=marker_map[profile],
             label=f'{profile} Encapsulation')

    plt.plot(keys_sim, dec_sim,
             linestyle=linestyles[profile],
             color=color_dec,
             marker=marker_map[profile],
             label=f'{profile} Decapsulation')

plt.xlabel('Public Key Size (Bytes)')
plt.ylabel('Time (ms)')
plt.title('HQC KEM: All Profiles (Extrapolated Values)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("combined_hqc_extrapolated.png", dpi=300)
plt.show()
print("Extrapolated values plot saved: combined_hqc_extrapolated.png")

# -------------------------------
# 3. Measured values per profile (subplots under each other)
# -------------------------------
fig, axes = plt.subplots(len(profiles), 1, figsize=(10, 6*len(profiles)), sharex=True, sharey=True)

for i, profile in enumerate(profiles):
    csv_path = os.path.join(profile, "pqc_hqc_benchmark.csv")
    if not os.path.exists(csv_path):
        print(f"CSV for {profile} not found, skipping...")
        continue

    df = pd.read_csv(csv_path)
    keys = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    ax = axes[i]
    ax.plot(keys, enc_times,
            marker=marker_map[profile],
            linestyle='-',
            color=color_enc,
            label='Encapsulation')
    ax.plot(keys, dec_times,
            marker=marker_map[profile],
            linestyle='-',
            color=color_dec,
            label='Decapsulation')
    ax.set_title(f'{profile} (Measured Values)')
    ax.set_ylabel('Time (ms)')
    ax.grid(True)
    ax.legend()

axes[-1].set_xlabel('Public Key Size (Bytes)')
plt.tight_layout()
plt.savefig("measured_per_profile.png", dpi=300)
plt.show()
print("Measured values per profile plot saved: measured_per_profile.png")

# -------------------------------
# 4. Extrapolated values per profile (subplots under each other)
# -------------------------------
fig, axes = plt.subplots(len(profiles), 1, figsize=(10, 6*len(profiles)), sharex=True, sharey=True)

for i, profile in enumerate(profiles):
    csv_path = os.path.join(profile, "pqc_hqc_benchmark.csv")
    if not os.path.exists(csv_path):
        continue

    df = pd.read_csv(csv_path)
    keys_real = np.array(df['PublicKeyBytes'])
    enc_times = np.array(df['Encaps_ms'])
    dec_times = np.array(df['Decaps_ms'])

    a_enc, b_enc = np.polyfit(np.log(keys_real), np.log(enc_times), 1)
    a_dec, b_dec = np.polyfit(np.log(keys_real), np.log(dec_times), 1)

    keys_sim = np.array([2249, 4522, 7245, 10240, 14000])
    enc_sim = np.exp(a_enc * np.log(keys_sim) + b_enc)
    dec_sim = np.exp(a_dec * np.log(keys_sim) + b_dec)

    ax = axes[i]
    ax.plot(keys_sim, enc_sim,
            linestyle=linestyles[profile],
            marker=marker_map[profile],
            color=color_enc,
            label='Encapsulation')
    ax.plot(keys_sim, dec_sim,
            linestyle=linestyles[profile],
            marker=marker_map[profile],
            color=color_dec,
            label='Decapsulation')
    ax.set_title(f'{profile} (Extrapolated Values)')
    ax.set_ylabel('Time (ms)')
    ax.grid(True)
    ax.legend()

axes[-1].set_xlabel('Public Key Size (Bytes)')
plt.tight_layout()
plt.savefig("extrapolated_per_profile.png", dpi=300)
plt.show()
print("Extrapolated values per profile plot saved: extrapolated_per_profile.png")

