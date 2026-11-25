#!/usr/bin/env python3
"""Writes the progression library into index.html between the PROG_LIB markers.

tools/progressions.json is the researched library, every entry with the sources it was
checked against (25 Nov 2026, 163 entries from 18 sites). The app carries only what it
shows and plays: id, name, family, tonic, chords, meter, bpm, why and one example. The
sources stay here, in the repo, out of the deployed page.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'progressions.json')
APP = os.path.join(HERE, '..', 'index.html')
RX = re.compile(r'^[b#]?(I|II|III|IV|V|VI|VII|i|ii|iii|iv|v|vi|vii)(°7|ø7|maj7|maj9|7sus4|7b9|sus4|sus2|add9|It6|'
                r'm\(maj7\)|°|\+|7|6|9)?(/[b#]?[1-7])?(:[0-9]+(\.[0-9]+)?)?$')

lib = json.load(open(SRC))
bad = [(p['id'], c) for p in lib for c in p['chords'] if not RX.match(c)]
assert not bad, bad
ids = [p['id'] for p in lib]
assert len(ids) == len(set(ids)), 'duplicate ids'
slim = [{'id': p['id'], 'name': p['name'], 'family': p['family'], 'tonic': p['tonic'],
         'chords': p['chords'], 'meter': p['meter'], 'bpm': p['bpm'], 'why': p['why'],
         'ex': (p.get('examples') or [''])[0]} for p in lib]
js = json.dumps(slim, ensure_ascii=False, separators=(',', ':'))
js = js.replace('},{', '},\n{')          # one entry a line, so diffs stay readable

app = open(APP, encoding='utf-8').read()
start, end = '/* PROG_LIB:start */', '/* PROG_LIB:end */'
i, j = app.index(start), app.index(end)
app = app[:i + len(start)] + '\nvar PROG_LIB = ' + js + ';\n' + app[j:]
open(APP, 'w', encoding='utf-8').write(app)
print('wrote %d progressions, %d bytes' % (len(slim), len(js.encode())))
