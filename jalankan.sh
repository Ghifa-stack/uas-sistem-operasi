#!/bin/bash
# Eksperimen utama: batas memori 64/128/256 MiB x 3 ulangan, urutan diacak
cd ~/proyek-oom || exit 1
mkdir -p hasil
OUT=hasil/ringkasan.csv
echo "urutan,batas_mib,ulangan,status,langkah_terakhir,alokasi_terakhir_mib,rss_terakhir_mib,cgroup_terakhir_mib,waktu_s,exit_code,oom_killed" > "$OUT"
urutan=0
for kombinasi in $(printf '%s\n' 64-1 64-2 64-3 128-1 128-2 128-3 256-1 256-2 256-3 | shuf); do
  b=${kombinasi%-*}
  u=${kombinasi#*-}
  urutan=$((urutan+1))
  nama="run_${b}_${u}"
  csv="hasil/run_${b}m_u${u}.csv"
  docker run --name "$nama" --memory=${b}m --memory-swap=${b}m -v "$PWD":/app -w /app python:3.12-slim python oom_test.py --output "$csv" > "hasil/log_${b}m_u${u}.txt" 2>&1
  kode=$(docker inspect "$nama" --format '{{.State.ExitCode}}')
  oom=$(docker inspect "$nama" --format '{{.State.OOMKilled}}')
  docker rm "$nama" > /dev/null
  if [ "$kode" = "0" ]; then status=selesai; else status=mati; fi
  baris=$(tail -n 1 "$csv" | tr -d '\r')
  echo "$urutan,$b,$u,$status,$baris,$kode,$oom" >> "$OUT"
  echo "[$urutan/9] batas=${b}m ulangan=$u status=$status exit=$kode oom=$oom"
  sleep 3
done
echo "Selesai. Ringkasan: $OUT"
cat "$OUT"
