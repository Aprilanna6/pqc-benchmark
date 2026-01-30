import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# Profile und CSV-Dateien
# -------------------------------
profiles = ["Mobile", "Laptop", "Server"]
kem_files = {
    "HQC": "pqc_hqc_benchmark.csv",
    "ML-KEM": "mlkem_benchmark.csv",
    "McEliece": "pqc_mceliece_benchmark.csv"
}

# Farben, Marker und Linienstile so gewählt, dass auch bei SW-Druck unterscheidbar
kem_styles = {
    "HQC": {"color": "green", "marker": "o", "linestyle": "-"},
    "ML-KEM": {"color": "blue", "marker": "s", "linestyle": "--"},
    "McEliece": {"color": "red", "marker": "D", "linestyle": "-."}
}

# -------------------------------
# Figure mit 3 Subplots
# -------------------------------
fig, axes = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

for i, profile in enumerate(profiles):
    ax = axes[i]

    for kem_name, csv_file in kem_files.items():
        csv_path = os.path.join(profile, csv_file)
        if not os.path.exists(csv_path):
            print(f"[WARN] {csv_path} nicht gefunden, überspringe {kem_name}")
            continue

        df = pd.read_csv(csv_path)
        style = kem_styles[kem_name]

        # Messpunkte sortieren nach KeySize
        df_sorted = df.sort_values("PublicKeyBytes")

        # Linien verbinden die Messpunkte, Marker zeigen Punkte
        ax.plot(df_sorted['PublicKeyBytes'], df_sorted['Encaps_ms'],
                color=style["color"], marker=style["marker"],
                linestyle=style["linestyle"], label=f"{kem_name} Encaps")
        ax.plot(df_sorted['PublicKeyBytes'], df_sorted['Decaps_ms'],
                color=style["color"], marker=style["marker"],
                linestyle=style["linestyle"], label=f"{kem_name} Decaps")

    ax.set_title(f"{profile} Profile: Key Size vs Encapsulation/Decapsulation Time")
    ax.set_ylabel("Time (ms)")
    ax.grid(True)
    ax.legend(fontsize=9)

axes[-1].set_xlabel("Public Key Size (Bytes)")

plt.tight_layout()
output_png = "comparison_all_profiles.png"  # <- Neuer Dateiname
plt.savefig(output_png, dpi=300)
plt.show()
print(f"Vergleichsplot gespeichert: {output_png}")

