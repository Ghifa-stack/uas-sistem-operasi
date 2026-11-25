#!/usr/bin/env python3
"""Proyek UAS SO: uji pelampauan batas memori container (mode retain)."""
import argparse
import csv
import time
from pathlib import Path

MIB = 1024 * 1024


def rss_mib():
    for baris in Path('/proc/self/status').read_text().splitlines():
        if baris.startswith('VmRSS:'):
            return round(int(baris.split()[1]) / 1024, 2)
    return 0.0


def cgroup_mib(nama):
    try:
        teks = Path('/sys/fs/cgroup/' + nama).read_text().strip()
        return None if teks == 'max' else round(int(teks) / MIB, 2)
    except (OSError, ValueError):
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    p.add_argument('--steps', type=int, default=60)
    p.add_argument('--chunk-mb', type=int, default=5)
    p.add_argument('--pause', type=float, default=0.1)
    a = p.parse_args()
    total = a.steps * a.chunk_mb
    if not (1 <= a.steps <= 60 and 1 <= a.chunk_mb <= 8 and a.pause >= 0):
        p.error('Batas aman: steps=1..60, chunk-mb=1..8, pause>=0')
    if total > 300:
        p.error('Batas aman: total alokasi (steps x chunk-mb) maksimum 300 MiB')
    batas = cgroup_mib('memory.max')
    if batas is None and total > 100:
        p.error('Tanpa batas memori, total alokasi maksimum 100 MiB. Jalankan lewat docker --memory.')
    print(f'Batas cgroup: {batas} MiB | rencana alokasi: {total} MiB', flush=True)
    retained = []
    mulai = time.time()
    with open(a.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['langkah', 'alokasi_mib', 'rss_mib', 'cgroup_mib', 'waktu_s'])
        f.flush()
        for i in range(1, a.steps + 1):
            retained.append(bytearray(a.chunk_mb * MIB))
            rss = rss_mib()
            cg = cgroup_mib('memory.current')
            waktu = round(time.time() - mulai, 2)
            w.writerow([i, i * a.chunk_mb, rss, cg, waktu])
            f.flush()
            print(f'Langkah {i:02}: alokasi={i * a.chunk_mb} MiB | RSS={rss:.2f} MiB | cgroup={cg} MiB', flush=True)
            time.sleep(a.pause)
    print('Selesai tanpa dihentikan. Data:', a.output)


if __name__ == '__main__':
    main()
