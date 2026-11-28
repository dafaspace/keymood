#!/usr/bin/env python3
"""Writes the progression library into index.html between the PROG_LIB markers.

tools/progressions.json is the researched library, every entry with the sources it was
checked against (25 Nov 2026, 163 entries from 18 sites). The app carries only what it
shows and plays: id, name, family, tonic, chords, meter, bpm, why and one example. The
sources stay here, in the repo, out of the deployed page.

Each entry may also carry "c", a rough commonness: 3 very common, 2 common, 1 rare (Dafa,
27-28 Nov 2026: three steps, no numbers, ranked inside the style). It is read from the corpus
counts in ../../corpus/out/library-evidence.json (the corpus tools and their METHOD.md
live in the project folder, outside this public repo; Dafa, 28 Nov 2026) and ranked against the other
entries of the same family. An entry gets no "c" when:
- its family's own music is not in the corpora (classical, galant and Renaissance are thin;
  film, metal, gospel, flamenco, klezmer, Arabic, Japanese are absent), so a low count there
  says nothing about the style;
- the count measures a common chord frame rather than the progression (frame-only schemata);
- it would be "rare" on a form or schema: those are matched whole and strictly, so variants
  are missed and a low count is not rarity (Rhythm changes A is found in 5 pieces).
A high count is evidence (precision measured at 95%); a low one is evidence only where a
match is loose enough to find the variants. Recall was not measured.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'progressions.json')
EVID = os.path.join(HERE, '..', '..', 'corpus', 'out', 'library-evidence.json')   # outside the repo
COVERED = {'jazz', 'pop-rock', 'blues', 'modal', 'folk-celtic'}
STRICT = {'form', 'schema', 'none'}
APP = os.path.join(HERE, '..', 'index.html')
RX = re.compile(r'^[b#]?(I|II|III|IV|V|VI|VII|i|ii|iii|iv|v|vi|vii)(°7|ø7|maj7|maj9|7sus4|7b9|sus4|sus2|add9|It6|'
                r'm\(maj7\)|°|\+|7|6|9)?(/[b#]?[1-7])?(:[0-9]+(\.[0-9]+)?)?$')

lib = json.load(open(SRC))
bad = [(p['id'], c) for p in lib for c in p['chords'] if not RX.match(c)]
assert not bad, bad
ids = [p['id'] for p in lib]
assert len(ids) == len(set(ids)), 'duplicate ids'

def commonness(lib, ev):
    fams = {}
    for p in lib:
        e = ev.get(p['id'])
        if p['family'] in COVERED and e and e.get('identifiable_at_chord_level'):
            fams.setdefault(p['family'], []).append((e['unique_pieces'], p['id'], e['kind']))
    out = {}
    for xs in fams.values():
        n = len(xs)
        for cnt, i, kind in xs:
            less = sum(1 for c, _, _ in xs if c < cnt)
            same = sum(1 for c, _, _ in xs if c == cnt)
            # midrank in thirds, ties share a step: 3 * (less + (same-1)/2) / (n-1), floored
            step = min(2, 3 * (2 * less + same - 1) // (2 * (n - 1)))
            if step == 0 and kind in STRICT: continue
            out[i] = step + 1
    return out

common = commonness(lib, json.load(open(EVID)))
slim = [{'id': p['id'], 'name': p['name'], 'family': p['family'], 'tonic': p['tonic'],
         'chords': p['chords'], 'meter': p['meter'], 'bpm': p['bpm'], 'why': p['why'],
         'ex': (p.get('examples') or [''])[0]} for p in lib]
for e in slim:
    if e['id'] in common: e['c'] = common[e['id']]
js = json.dumps(slim, ensure_ascii=False, separators=(',', ':'))
js = js.replace('},{', '},\n{')          # one entry a line, so diffs stay readable

app = open(APP, encoding='utf-8').read()
start, end = '/* PROG_LIB:start */', '/* PROG_LIB:end */'
i, j = app.index(start), app.index(end)
app = app[:i + len(start)] + '\nvar PROG_LIB = ' + js + ';\n' + app[j:]
open(APP, 'w', encoding='utf-8').write(app)
print('wrote %d progressions, %d bytes; commonness on %d (%d very common, %d common, %d rare)' % (
    len(slim), len(js.encode()), len(common), *[sum(1 for v in common.values() if v == k) for k in (3, 2, 1)]))
