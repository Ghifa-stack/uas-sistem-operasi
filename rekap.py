import csv
import statistics as st
from collections import defaultdict

data = defaultdict(list)
with open('hasil/ringkasan.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        data[int(r['batas_mib'])].append(r)


def sd(x):
    return round(st.stdev(x), 2) if len(x) > 1 else 0.0


kolom = ['batas_mib', 'n_ulangan', 'langkah_min', 'langkah_maks', 'langkah_rata',
         'langkah_sd', 'alokasi_rata_mib', 'rss_rata_mib', 'cgroup_rata_mib',
         'sisa_ruang_rata_mib', 'mati', 'oom_true', 'exit_137']
hasil = []
for batas in sorted(data):
    rs = data[batas]
    lang = [int(r['langkah_terakhir']) for r in rs]
    alok = [float(r['alokasi_terakhir_mib']) for r in rs]
    rss = [float(r['rss_terakhir_mib']) for r in rs]
    cg = [float(r['cgroup_terakhir_mib']) for r in rs]
    hasil.append({
        'batas_mib': batas,
        'n_ulangan': len(rs),
        'langkah_min': min(lang),
        'langkah_maks': max(lang),
        'langkah_rata': round(st.mean(lang), 2),
        'langkah_sd': sd(lang),
        'alokasi_rata_mib': round(st.mean(alok), 2),
        'rss_rata_mib': round(st.mean(rss), 2),
        'cgroup_rata_mib': round(st.mean(cg), 2),
        'sisa_ruang_rata_mib': round(batas - st.mean(cg), 2),
        'mati': sum(r['status'] == 'mati' for r in rs),
        'oom_true': sum(r['oom_killed'] == 'true' for r in rs),
        'exit_137': sum(r['exit_code'] == '137' for r in rs),
    })

with open('hasil/rekap_per_batas.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=kolom)
    w.writeheader()
    w.writerows(hasil)

print('\t'.join(kolom))
for h in hasil:
    print('\t'.join(str(h[k]) for k in kolom))
print('Tersimpan: hasil/rekap_per_batas.csv')
