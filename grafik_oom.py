import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = defaultdict(list)
with open("hasil/ringkasan.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        data[int(r["batas_mib"])].append(r)
batas = sorted(data)

def rata(b, kolom):
    nilai = [float(r[kolom]) for r in data[b]]
    return sum(nilai) / len(nilai)

# Grafik 1: langkah terakhir vs batas memori
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=200)
for b in batas:
    ys = [int(r["langkah_terakhir"]) for r in data[b]]
    ax.scatter([b] * len(ys), ys, color="#D85A30", zorder=3)
rt = [rata(b, "langkah_terakhir") for b in batas]
ax.plot(batas, rt, marker="o", color="#D85A30", label="Rata-rata 3 ulangan")
for b, y in zip(batas, rt):
    ax.annotate(f"{y:g}", (b, y), textcoords="offset points", xytext=(0, 9), ha="center")
ax.set_xticks(batas)
ax.set_xlabel("Batas memori --memory (MiB)")
ax.set_ylabel("Langkah terakhir (1 langkah = 5 MiB)")
ax.set_title("Langkah terakhir sebelum container dihentikan (OOMKilled)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig("hasil/grafik1_langkah_terakhir.png")
plt.close(fig)

# Grafik 2: batas vs memori cgroup saat dihentikan
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=200)
x = range(len(batas))
lebar = 0.27
ax.bar([i - lebar for i in x], batas, lebar, label="Batas --memory", color="#888780")
ax.bar(list(x), [rata(b, "cgroup_terakhir_mib") for b in batas], lebar,
       label="Memori cgroup terakhir", color="#D85A30")
ax.bar([i + lebar for i in x], [rata(b, "alokasi_terakhir_mib") for b in batas], lebar,
       label="Alokasi terakhir", color="#1D9E75")
ax.set_xticks(list(x))
ax.set_xticklabels([f"{b} MiB" for b in batas])
ax.set_ylabel("Memori (MiB)")
ax.set_title("Batas memori vs memori terpakai saat dihentikan")
ax.legend()
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("hasil/grafik2_batas_vs_cgroup.png")
plt.close(fig)
print("Grafik tersimpan di folder hasil/")
