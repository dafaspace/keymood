#!/bin/sh
# Rebuild piano/*.mp3 from the Salamander Grand Piano originals.
#
# Source: https://github.com/sfzinstruments/SalamanderGrandPiano (Alexander Holm,
# CC BY 3.0), Samples/<note>v10.flac - 48 kHz / 24-bit, velocity layer 10 of 16.
# Download the 13 files below into one folder and pass it as $1:
#   C3 D#3 F#3 A3 C4 D#4 F#4 A4 C5 D#5 F#5 A5 C6   (each as <note>v10.flac)
#
# Per file: start 2 ms before the first sound (the originals carry a few ms of
# silence, which would delay every note), keep 5 s with a fade over the last 1.4,
# stay at 48 kHz so nothing is resampled, and encode LAME VBR V0.
#
# Levels are EVENED, not left as recorded. Measured K-weighted over each attack, the
# set was ragged: C4 sat 3 dB above its neighbours (and it serves B, C, C#, D - so C
# major's tonic came out accented) while A5 and C6 dropped 4 dB below F#5. A one-
# velocity set has no way to even that out at play time, so each file is gained onto
# a gentle slope instead: -18.5 LUFS at C3 falling 0.25 dB per file, 3 dB over three
# octaves, which is roughly how a real piano's top thins out. The app's PIANO_GAIN
# sets the overall level.
set -e
SRC="${1:?usage: tools/piano.sh <folder with the v10 flacs>}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/piano"
mkdir -p "$OUT"
k=0
for n in C3 D#3 F#3 A3 C4 D#4 F#4 A4 C5 D#5 F#5 A5 C6; do
  in="$SRC/${n}v10.flac"
  on=$(ffmpeg -hide_banner -nostats -i "$in" -t 0.5 -af "silencedetect=n=-60dB:d=0.001" -f null - 2>&1 \
       | grep -o "silence_end: [0-9.]*" | head -1 | awk '{print $2}')
  st=$(awk -v o="${on:-0}" 'BEGIN { s = o - 0.002; if (s < 0) s = 0; printf "%.4f", s }')
  name=$(echo "$n" | sed 's/#/s/')
  lu=$(ffmpeg -hide_banner -nostats -ss "$st" -t 0.6 -i "$in" -af ebur128 -f null - 2>&1 \
       | grep -E "^ +I:" | tail -1 | awk '{print $2}')
  gain=$(awk -v l="$lu" -v k="$k" 'BEGIN { printf "%.2f", (-18.5 - 0.25*k) - l }')
  ffmpeg -hide_banner -loglevel error -y -ss "$st" -i "$in" -t 5 \
    -af "volume=${gain}dB,afade=t=out:st=3.6:d=1.4:curve=exp" -ar 48000 -c:a libmp3lame -q:a 0 "$OUT/$name.mp3"
  echo "$name.mp3  start ${st}s  attack ${lu} LUFS  gain ${gain} dB"
  k=$((k + 1))
done
