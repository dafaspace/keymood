#!/usr/bin/env node
// Keymood in the portfolio's languages (root CLAUDE.md, "Languages"; index.html, "Languages").
//
// English is the source and stays inside index.html, so the default load fetches nothing:
//   - the I18N_EN block: every text the code writes, one key a line. A line `//: ...` just
//     above a key is a note for the translator; it is copied into en.json as "note".
//   - data-t="key" (an element's inner HTML) and data-t-attr="attr:key,attr:key" on the
//     static markup, the dafaspace convention. The same key twice must have the same English.
//   - the library and the moods in their own data: lib.<id>.name and lib.<id>.why from
//     PROG_LIB (written by tools/progs.py), mood.<name>.name and mood.<name>.traj from
//     EMOTIONS (the names are _portfolio/shared/moods.json's).
//
// A translation is i18n/<code>.json, shaped { "key": { "text": "...", "from": "<hash>" } },
// "from" being the hash in i18n/en.json of the English it was made from. A plural is one key
// per form the language uses, as Intl.PluralRules names them (key.one, key.few, key.many,
// key.other; ar also key.zero and key.two); English writes .one and .other, and every form of
// a plural takes the same hash, the plural's. {placeholders} and HTML tags must survive.
// Song titles in a library entry's example are not translated, and neither are app names.
//
//   node tools/i18n.mjs build         writes i18n/en.json and the I18N_READY list in index.html
//                                     (the languages that have a file: only these are offered)
//   node tools/i18n.mjs check         one line per problem, exit 1 if there is any: a missing
//                                     key, a stale "from", a lost or added {placeholder} or tag,
//                                     a key the English no longer has, en.json or I18N_READY
//                                     behind index.html
//   node tools/i18n.mjs check --all   the same, and a language with no file yet is a problem too
//                                     (before a store submission: all thirteen)

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const rel = f => path.join(ROOT, f);
export const hash = s => crypto.createHash('sha1').update(s).digest('hex').slice(0, 10);
const between = (s, a, b) => {
  const i = s.indexOf(a);
  if (i < 0) throw new Error(`index.html has no ${a}`);
  const j = s.indexOf(b, i + a.length);
  if (j < 0) throw new Error(`index.html has no ${b}`);
  return s.slice(i + a.length, j);
};

// Every keyed text in the markup, in document order (dafaspace's tools/i18n.mjs). Tags inside
// <script> or a comment are not keys; spans may not overlap.
function spans(html) {
  const out = [], skip = [...html.matchAll(/<script\b[\s\S]*?<\/script>|<!--[\s\S]*?-->/g)].map(m => [m.index, m.index + m[0].length]);
  for (const m of html.matchAll(/<([a-zA-Z][a-zA-Z0-9]*)\b(?:[^>"']|"[^"]*"|'[^']*')*>/g)) {
    if (!/\sdata-t(?:-attr)?="/.test(m[0]) || skip.some(([a, b]) => m.index > a && m.index < b)) continue;
    const [tag, name] = m, open = m.index;
    const attrs = /\sdata-t-attr="([^"]*)"/.exec(tag), own = /\sdata-t="([^"]*)"/.exec(tag);
    for (const pair of attrs ? attrs[1].split(',') : []) {
      const [attr, key] = pair.split(':');
      const a = new RegExp(`\\s${attr}="([^"]*)"`).exec(tag);
      if (!a) throw new Error(`${key}: no ${attr}="" on ${tag}`);
      out.push({ key, text: a[1], start: open + a.index });
    }
    if (!own) continue;
    let depth = 1, close;
    const re = new RegExp(`<(/?)${name}\\b[^>]*>`, 'g');
    re.lastIndex = open + tag.length;
    while ((close = re.exec(html))) { depth += close[1] ? -1 : 1; if (!depth) break; }
    if (!close) throw new Error(`${own[1]}: no closing </${name}>`);
    out.push({ key: own[1], text: html.slice(open + tag.length, close.index), start: open + tag.length, end: close.index });
  }
  out.sort((a, b) => a.start - b.start);
  for (let i = 1; i < out.length; i++) if (out[i].end && out[i - 1].end && out[i].start < out[i - 1].end) throw new Error(`key ${out[i].key} sits inside key ${out[i - 1].key}`);
  return out;
}

const evalJs = (src, what) => { try { return vm.runInNewContext('(' + src + ')'); } catch (e) { throw new Error(`cannot read ${what}: ${e.message}`); } };

// The I18N_EN block: strict JSON once the comment lines are out; `//:` lines are notes.
function englishBlock(html) {
  const body = between(html, '/* I18N_EN:start */', '/* I18N_EN:end */');
  const lines = body.slice(body.indexOf('{')).split('\n'), notes = {}, keep = [];
  let note = null;
  for (const l of lines) {
    const st = l.trim();
    if (st.startsWith('//:')) { note = (note ? note + ' ' : '') + st.slice(3).trim(); continue; }
    if (st.startsWith('//')) continue;
    const k = /^"([^"]+)"\s*:/.exec(st);
    if (k && note) { notes[k[1]] = note; note = null; }
    keep.push(l);
  }
  const text = keep.join('\n').replace(/;\s*$/, '');
  let en;
  try { en = JSON.parse(text); } catch (e) { throw new Error(`the I18N_EN block is not strict JSON: ${e.message}`); }
  return { en, notes };
}

// Everything the English is made of, keyed, in order: markup, code, moods, library.
export function sources(html = fs.readFileSync(rel('index.html'), 'utf8')) {
  const en = {}, notes = {}, area = {};
  const add = (key, text, a, where) => {
    if (typeof text !== 'string') throw new Error(`${key}: no English text (${where})`);
    if (key in en && en[key] !== text) throw new Error(`key ${key} has two different English texts (${where})`);
    en[key] = text; area[key] = area[key] || a;
  };
  for (const s of spans(html)) add(s.key, s.text, 'ui', 'markup');
  const block = englishBlock(html);
  for (const [k, v] of Object.entries(block.en)) add(k, v, k.startsWith('tw.') ? 'twist' : 'ui', 'I18N_EN');
  Object.assign(notes, block.notes);
  const emo = evalJs(/var EMOTIONS = (\[[\s\S]*?\n\]);/.exec(html)?.[1] ?? 'x', 'EMOTIONS');
  for (const e of emo) {
    const k = 'mood.' + e.name.toLowerCase();
    add(k + '.name', e.name, 'moods', 'EMOTIONS');
    add(k + '.traj', e.traj, 'moods', 'EMOTIONS');
  }
  notes['mood.action.traj'] = 'A mood\'s .traj is the arc its music takes, shown under the mode in Assist.';
  const lib = JSON.parse(between(html, '/* PROG_LIB:start */', '/* PROG_LIB:end */').trim().replace(/^var PROG_LIB = /, '').replace(/;\s*$/, ''));
  for (const p of lib) {
    add('lib.' + p.id + '.name', p.name, 'library', 'PROG_LIB');
    add('lib.' + p.id + '.why', p.why, 'library', 'PROG_LIB');
  }
  if (lib.length) {
    notes['lib.' + lib[0].id + '.name'] = 'A library name that starts with its numerals keeps them in front with the name in brackets ("I-IV-V (three-chord song)"); the app shows only what is in the brackets.';
  }
  const LANGS = evalJs(/var LANGS = (\{[\s\S]*?\});/.exec(html)?.[1] ?? 'x', 'LANGS');
  const ready = JSON.parse(between(html, '/* I18N_READY:start */', '/* I18N_READY:end */').trim().replace(/^var I18N_READY = /, '').replace(/;\s*$/, ''));
  // Plurals: a key whose English has .one and .other.
  const plural = new Set();
  for (const k of Object.keys(en)) {
    const m = /^(.+)\.(one|other)$/.exec(k);
    if (m && (m[1] + '.one') in en && (m[1] + '.other') in en) plural.add(m[1]);
  }
  return { en, notes, area, plural, langs: Object.keys(LANGS), names: LANGS, ready, lib };
}

const pluralBase = (src, k) => { const m = /^(.+)\.(zero|one|two|few|many|other)$/.exec(k); return m && src.plural.has(m[1]) ? m[1] : null; };
// Every form of a plural takes one hash: the plural's English, all its forms together.
const hashOf = (src, k) => { const b = pluralBase(src, k); return b ? hash(JSON.stringify([src.en[b + '.one'], src.en[b + '.other']])) : hash(src.en[k]); };

export function enJsonText(src) {
  const out = {};
  for (const k of Object.keys(src.en)) {
    out[k] = { text: src.en[k], hash: hashOf(src, k) };
    if (src.notes[k]) out[k].note = src.notes[k];
    if (pluralBase(src, k)) out[k].plural = true;
  }
  return JSON.stringify(out, null, 2) + '\n';
}

const translated = src => src.langs.filter(c => c !== 'en' && fs.existsSync(rel(`i18n/${c}.json`)));
const readyBlock = list => `\nvar I18N_READY = ${JSON.stringify(list)};\n`;

export function build() {
  const html = fs.readFileSync(rel('index.html'), 'utf8'), src = sources(html);
  fs.mkdirSync(rel('i18n'), { recursive: true });
  fs.writeFileSync(rel('i18n/en.json'), enJsonText(src));
  const ready = ['en', ...translated(src)];
  const a = '/* I18N_READY:start */', b = '/* I18N_READY:end */', i = html.indexOf(a), j = html.indexOf(b);
  const next = html.slice(0, i + a.length) + readyBlock(ready) + html.slice(j);
  if (next !== html) fs.writeFileSync(rel('index.html'), next);
  return { keys: Object.keys(src.en).length, ready };
}

const vars = s => (s.match(/\{\w+\}/g) || []).sort();
const tags = s => (s.match(/<\/?[a-zA-Z][a-zA-Z0-9]*/g) || []).map(x => x.toLowerCase()).sort();
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

export function check({ all = false } = {}) {
  const html = fs.readFileSync(rel('index.html'), 'utf8'), src = sources(html), problems = [];
  if (!fs.existsSync(rel('i18n/en.json')) || fs.readFileSync(rel('i18n/en.json'), 'utf8') !== enJsonText(src))
    problems.push('i18n/en.json is behind index.html: run node tools/i18n.mjs build');
  const have = translated(src);
  if (!same(src.ready, ['en', ...have])) problems.push(`I18N_READY in index.html is ${JSON.stringify(src.ready)}, the files say ${JSON.stringify(['en', ...have])}: run node tools/i18n.mjs build`);
  for (const f of fs.existsSync(rel('i18n')) ? fs.readdirSync(rel('i18n')) : []) {
    const c = f.replace(/\.json$/, '');
    if (f.endsWith('.json') && !src.langs.includes(c)) problems.push(`i18n/${f}: ${c} is not one of the languages in LANGS`);
  }
  for (const c of have) {
    let dict;
    try { dict = JSON.parse(fs.readFileSync(rel(`i18n/${c}.json`), 'utf8')); }
    catch (e) { problems.push(`${c}: cannot read i18n/${c}.json: ${e.message}`); continue; }
    const cats = new Intl.PluralRules(c).resolvedOptions().pluralCategories;
    // What this language must have: every plain key, and each plural in its own forms.
    const want = new Map();
    for (const k of Object.keys(src.en)) {
      const b = pluralBase(src, k);
      if (!b) want.set(k, src.en[k]);
      else for (const cat of cats) want.set(b + '.' + cat, src.en[b + '.other']);
    }
    for (const [k, enText] of want) {
      const e = dict[k];
      if (!e) { problems.push(`${c}: ${k} missing`); continue; }
      if (typeof e.text !== 'string' || typeof e.from !== 'string') { problems.push(`${c}: ${k} is not { "text", "from" }`); continue; }
      if (!e.text.trim()) problems.push(`${c}: ${k} is empty`);
      if (e.from !== hashOf(src, pluralBase(src, k) ? pluralBase(src, k) + '.other' : k)) problems.push(`${c}: ${k} is stale (the English changed since it was translated)`);
      const b = pluralBase(src, k), cat = b && k.slice(b.length + 1);
      let ev = vars(enText), tv = vars(e.text);
      // A singular form may spell its number out ("одна"), so {n} is optional there.
      if (b && /^(zero|one|two)$/.test(cat)) { ev = ev.filter(v => v !== '{n}'); tv = tv.filter(v => v !== '{n}'); }
      if (!same(ev, tv)) problems.push(`${c}: ${k} has ${tv.join(' ') || 'no placeholders'}, the English ${ev.join(' ') || 'none'}`);
      if (!same(tags(enText), tags(e.text))) problems.push(`${c}: ${k} has other HTML tags than the English (${tags(enText).join(' ') || 'none'})`);
    }
    for (const k of Object.keys(dict)) {
      if (want.has(k)) continue;
      const b = pluralBase(src, k);
      problems.push(b ? `${c}: ${k} is not a plural form ${c} uses (${cats.join(' ')})` : `${c}: ${k} is no longer in the English`);
    }
  }
  const missing = src.langs.filter(c => c !== 'en' && !have.includes(c));
  if (all) for (const c of missing) problems.push(`${c}: not translated yet (i18n/${c}.json)`);
  const count = a => Object.values(src.area).filter(x => x === a).length;
  const line = `Keymood i18n: ${Object.keys(src.en).length} English keys (UI ${count('ui')}, library ${count('library')}, moods ${count('moods')}, Twist ${count('twist')}); ` +
    `${have.length} of ${src.langs.length - 1} languages translated` + (missing.length ? ` (not yet: ${missing.join(' ')})` : '') +
    (problems.length ? `; ${problems.length} problem${problems.length === 1 ? '' : 's'}` : '; OK');
  return { problems, line, src };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === fs.realpathSync(process.argv[1])) {
  const cmd = process.argv[2];
  if (cmd === 'build') { const r = build(); console.log(`built: i18n/en.json (${r.keys} keys), I18N_READY ${r.ready.join(' ')}`); }
  else if (cmd === 'check') {
    const r = check({ all: process.argv.includes('--all') });
    for (const p of r.problems) console.log(p);
    console.log(r.line);
    process.exit(r.problems.length ? 1 : 0);
  } else { console.log('usage: node tools/i18n.mjs build | check [--all]'); process.exit(2); }
}
