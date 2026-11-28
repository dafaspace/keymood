// Keymood's languages, the way Spotanote's tests/i18n.cjs checks its own:
//   1. the build output is current (i18n/en.json, I18N_READY);
//   2. every key the code asks for exists in English, and every English key is asked for;
//   3. the thirteen languages, their note names and right-to-left set are whole;
//   4. the note naming, the plural fallback and the pseudo-locale behave.
//   node tests/i18n.mjs        (exit 1 on any failure, one line each)
import fs from 'node:fs';
import vm from 'node:vm';
import { ROOT, sources, enJsonText, check } from '../tools/i18n.mjs';

const html = fs.readFileSync(ROOT + '/index.html', 'utf8');
const src = sources(html);
const bad = [];
const fail = m => bad.push(m);
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
const en = src.en, has = k => k in en, plural = b => src.plural.has(b);

// 1. Build output.
if (!fs.existsSync(ROOT + '/i18n/en.json') || fs.readFileSync(ROOT + '/i18n/en.json', 'utf8') !== enJsonText(src))
  fail('i18n/en.json is behind index.html: run node tools/i18n.mjs build');
const r = check();
for (const p of r.problems) fail('check: ' + p);

// 2. Keys in code. The first argument of every t(), ta(), tn() and tx() call is read up to
// its comma: each literal in it shaped like a key must exist (tn: as a plural), and one
// that ends in a dot is a prefix the code completes, so some key must start with it.
const asked = new Set(), prefixes = new Set();
const keyShape = /^[a-z][A-Za-z0-9]*(\.[A-Za-z0-9-]*)+$/;
for (const m of script.matchAll(/(?<![\w.$])(t|ta|tn|tx)\(/g)) {
  let i = m.index + m[0].length, depth = 0, q = null, lit = '', lits = [];
  for (; i < script.length; i++) {
    const ch = script[i];
    if (q) { if (ch === '\\') { lit += script[++i]; continue; } if (ch === q) { lits.push(lit); q = null; lit = ''; } else lit += ch; continue; }
    if (ch === "'" || ch === '"') { q = ch; continue; }
    if ('([{'.includes(ch)) depth++;
    else if (')]}'.includes(ch)) { if (!depth--) break; }
    else if (ch === ',' && !depth) break;
  }
  for (const k of lits) {
    if (!keyShape.test(k)) continue;
    const line = script.slice(0, m.index).split('\n').length;
    if (k.endsWith('.')) { prefixes.add(k); if (!Object.keys(en).some(x => x.startsWith(k))) fail(`script line ${line}: no English key starts with ${k}`); continue; }
    if (m[1] === 'tn') { asked.add(k); if (!plural(k)) fail(`script line ${line}: ${k} is not a plural (${k}.one and ${k}.other)`); }
    else if (m[1] !== 'tx') { asked.add(k); if (!has(k)) fail(`script line ${line}: no English for ${k}`); }
  }
}
// The keys the code completes from its data: each family must be whole.
const grab = (rx, s = script) => [...s.matchAll(rx)].map(m => m[1]);
const block = (a, b) => script.slice(script.indexOf(a), script.indexOf(b, script.indexOf(a)));
const family = [];
for (const id of grab(/\{ id:'(\w+)',\s+type:/g)) family.push('mode.' + id, 'mode.' + id + '.mood');
for (const p of src.lib) family.push('pmode.' + p.tonic);
for (const id of grab(/\['(\w+)', \[/g, block('var PROG_FAMILIES', '\n];'))) family.push('pg.fam.' + id);
for (const id of grab(/'(\w+)'/g, block('var ALL_REL_KEYS', ';'))) family.push('rel.' + id, 'rel.' + id + '.text');
for (const id of grab(/\{id:'(\w+)'/g, block('var DJMOVES', '\n];'))) family.push('dj.' + id, 'dj.' + id + '.sub');
for (let i = 0; i <= 5; i++) family.push('hard.' + i);
for (const d of [1, 2, 4, 8, 16, 32, 64]) family.push('metro.counts.' + d, 'metro.dotted.' + d);
const devs = grab(/\{ id: '(\w+)', L: \d, needs:/g);
if (devs.length < 20) fail(`Twist: only ${devs.length} devices found in TWIST_DEVS`);
for (const id of devs) family.push('tw.' + id, 'tw.' + id + '.in', 'tw.' + id + '.tag');
const forms = new Set([...grab(/tx: '(\w+)'/g), ...grab(/\d, '(\w+)'\]/g, block('var TW_BORROW', '};')),
  ...grab(/'(\w+)'/g, (/return \[('it6', 'ger6', 'fr6')\]\.map/.exec(script) || ['', ''])[1])]);
for (const tx of forms) family.push('tw.' + tx, 'tw.' + tx + '.in');
for (const k of family) { asked.add(k); if (!has(k)) fail(`no English for ${k}`); }
// Tags a form has of its own are optional (twTag falls back to its device's).
for (const tx of forms) if (has('tw.' + tx + '.tag')) asked.add('tw.' + tx + '.tag');
// And the other way: an English key nobody asks for is a translation nobody needs. Asked
// means: in a t() call, completed from a prefix in one, made from the data above, or held as
// a literal the code passes on (CT_NAME's 'panel.roleTonic', the dice chips' 'dice.key').
for (const m of script.matchAll(/'([a-z][A-Za-z0-9]*(?:\.[A-Za-z0-9-]+)+)'/g)) if (has(m[1])) asked.add(m[1]);
for (const p of prefixes) for (const k of Object.keys(en)) if (k.startsWith(p)) asked.add(k);
const htmlKeys = new Set([...html.matchAll(/data-t="([^"]+)"/g)].map(m => m[1]).concat(
  [...html.matchAll(/data-t-attr="([^"]+)"/g)].flatMap(m => m[1].split(',').map(p => p.split(':')[1]))));
for (const k of Object.keys(en)) {
  if (src.area[k] === 'library' || src.area[k] === 'moods' || htmlKeys.has(k)) continue;
  const b = /^(.+)\.(one|other)$/.exec(k);
  if (asked.has(k) || (b && asked.has(b[1]))) continue;
  fail(`${k}: in I18N_EN but nothing asks for it`);
}
// The data-sourced texts are reached through progName/progWhy and moodName/moodTraj.
for (const f of ["tx('lib.' + p.id + '.name'", "tx('lib.' + p.id + '.why'", "tx('mood.' + e.name.toLowerCase() + '.name'", "tx('mood.' + e.name.toLowerCase() + '.traj'"])
  if (!script.includes(f)) fail('the library or the moods are no longer read through ' + f);

// 3. The thirteen.
const SET = ['en', 'ru', 'uk', 'ka', 'es', 'fr', 'de', 'it', 'pt-BR', 'tr', 'ja', 'he', 'ar'];
const core = between('/* I18N_CORE:start */', '/* I18N_CORE:end */');
function between(a, b) { return script.slice(script.indexOf(a) + a.length, script.indexOf(b)); }
const enBlock = JSON.parse(between('/* I18N_EN:start */', '/* I18N_EN:end */').replace(/^\s*var I18N_EN = /, '')
  .split('\n').filter(l => !/^\s*\/\//.test(l)).join('\n').replace(/;\s*$/, ''));
const ctx = { window: {}, console: { warn() {}, log() {} }, Intl, I18N_EN: enBlock, navigator: { languages: ['en'] }, localStorage: { getItem() { return null; }, setItem() {} },
  MODES: grab(/\{ id:'(\w+)',\s+type:'(\w+)'/g).map(id => ({ id, type: /dorian|aeolian|phrygian/.test(id) ? 'min' : id === 'locrian' ? 'dim' : 'maj' })),
  qName: s => s.replace(/♯/g, '#').replace(/♭/g, 'b'), loadPref: (k, d) => d, savePref() {} };
vm.createContext(ctx);
vm.runInContext(core + ';this.X={LANGS,LANG_ORDER,RTL_LANGS,NOTE_SYSTEMS,LANG_MUSIC,_sysName,_pseudo,t,tn,tx,chordName,keyName,keyShort,noteName,' +
  'set:function(o){for(var k in o){if(k==="LANG")LANG=o[k];if(k==="LANG_PSEUDO")LANG_PSEUDO=o[k];if(k==="_tr")_tr=o[k];if(k==="_noteSys")_noteSys=o[k];}_pcache={};}}', ctx);
const X = ctx.X;
if (JSON.stringify(Object.keys(X.LANGS)) !== JSON.stringify(SET)) fail('LANGS is not the portfolio set: ' + Object.keys(X.LANGS).join(' '));
if (JSON.stringify(X.LANG_ORDER) !== JSON.stringify(SET)) fail('LANG_ORDER is not the portfolio set');
if (Object.keys(X.RTL_LANGS).sort().join() !== 'ar,he') fail('RTL set is not he and ar');
for (const c of SET) {
  const m = X.LANG_MUSIC[c];
  if (!m) { fail(`${c}: no LANG_MUSIC entry`); continue; }
  if (!X.NOTE_SYSTEMS[m.notes] || X.NOTE_SYSTEMS[m.notes].picker === false) fail(`${c}: note names ${m.notes} is not a system in the picker`);
  const kn = m.keys.notes, titles = !kn ? [] : typeof kn === 'string' ? [kn] : Object.entries(kn).flat();
  for (const id of titles) if (!X.NOTE_SYSTEMS[id]) fail(`${c}: key titles name ${id}, not a note system`);
  if (m.keys.minor !== null && m.keys.minor !== 'lower') fail(`${c}: keys.minor must be null or lower`);
  if (m.chords !== 'letters' && m.chords !== 'notes') fail(`${c}: chords must be letters or notes`);
}
for (const [id, S] of Object.entries(X.NOTE_SYSTEMS)) if (S.base.length !== 7) fail(`note system ${id} has ${S.base.length} names, not 7`);

// 4. Behaviour.
const eq = (got, want, what) => { if (got !== want) fail(`${what}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`); };
const de = { 'C': 'C', 'C♯': 'Cis', 'C𝄪': 'Cisis', 'D♭': 'Des', 'E♭': 'Es', 'E𝄫': 'Eses', 'F♯♯': 'Fisis', 'A♭': 'As', 'A𝄫': 'Ases',
  'B': 'H', 'B♭': 'B', 'B𝄫': 'Heses', 'B♯': 'His', 'C♭': 'Ces', 'G♭': 'Ges', 'F♭': 'Fes', 'E♯': 'Eis' };
for (const [k, v] of Object.entries(de)) eq(X._sysName('german', k), v, 'German ' + k);
const la = { 'B♭': 'Si♭', 'C♯': 'Do♯', 'F𝄪': 'Fa𝄪', 'D♭♭': 'Re𝄫', 'G': 'Sol' };
for (const [k, v] of Object.entries(la)) eq(X._sysName('latin', k), v, 'solfège ' + k);
eq(X._sysName('french', 'E♭'), 'Mi♭', 'French E♭');
eq(X._sysName('portuguese', 'F♯'), 'Fá♯', 'Portuguese F♯');
eq(X._sysName('iroha', 'F♯'), '嬰ヘ', 'iroha F♯');
eq(X._sysName('iroha', 'B♭'), '変ロ', 'iroha B♭');
eq(X._sysName('ukrainian', 'B♭'), 'сі♭', 'Ukrainian B♭');
eq(X._sysName('cyrillicWords', 'F♯'), 'фа-диез', 'Russian key-title F♯');
eq(X._sysName('cyrillicWords', 'B♭'), 'си-бемоль', 'Russian key-title B♭');
for (const k of ['C', 'F♯♯', 'B𝄫', 'E♭']) eq(X._sysName('letters', k), k, 'letters keep ' + k);
X.set({ LANG: 'en', LANG_PSEUDO: false, _tr: null, _noteSys: 'letters' });
eq(X.keyName('C♯', 'major'), 'C♯ major', 'English key title');
eq(X.keyName('F♯', 4, true), 'F# Aeolian', 'quiz key title');
eq(X.keyShort('A', true), 'Am', 'English short minor');
eq(X.chordName('B♭', 'm7', 'D'), 'B♭m7/D', 'chord in letters');
X.set({ _noteSys: 'latin' });
eq(X.chordName('B♭', 'm7'), 'B♭m7', 'chords stay letters while (c) is letters');
eq(X.keyName('B♭', 'minor'), 'Si♭ minor', 'key title in the chosen names');
X.set({ _noteSys: 'letters' });
eq(X.t('no.such.key'), '', 'a missing key never shows its name');
X.set({ LANG: 'de', _noteSys: 'german', _tr: { 'key.minor': '{note}-Moll', 'key.major': '{note}-Dur', 'key.shortMinor': '{note}' } });
eq(X.keyName('F♯', 'minor'), 'fis-Moll', 'German minor key title');
eq(X.keyName('B♭', 'major'), 'B-Dur', 'German major key title');
eq(X.keyShort('E♭', true), 'es', 'German short minor');
X.set({ LANG: 'ru', _noteSys: 'cyrillic', _tr: { 'key.major': '{note} мажор' } });
eq(X.keyName('F♯', 'major'), 'фа-диез мажор', 'Russian key title in words');
eq(X.noteName('F♯'), 'фа♯', 'Russian note name with a sign');
X.set({ LANG: 'en', _noteSys: 'letters', _tr: null });
X.set({ LANG: 'ru', _tr: { 'pro.count.few': '{n} прогрессии' } });
eq(X.tn('pro.count', 3), '3 прогрессии', 'ru plural few');
eq(X.tn('pro.count', 5), '5 progressions in any key', 'a missing form falls back to English');
X.set({ LANG: 'he', _tr: null });
eq(X.noteName('C♯'), '⁨C♯⁩', 'a name in right-to-left text is isolated');
X.set({ LANG: 'xx', LANG_PSEUDO: true, _tr: null });
const ps = X.t('panel.modeOf', { num: 'II', key: 'G major' });
if (!/^\[.*<strong>G major<\/strong>\]$/.test(ps) || !ps.includes('II')) fail('pseudo-locale lost a tag or a placeholder: ' + ps);
const plain = 'Diatonic chords', pp = X._pseudo(plain);
if (pp.length < plain.length * 1.4 || !/^\[.*\]$/.test(pp) || /[a-z]{2}/.test(pp.replace(/ẋ/g, ''))) fail('pseudo-locale is not 40% longer and accented: ' + pp);
eq(X.keyShort('A', true), 'Am', 'pseudo leaves short key names alone');

// 5. The store build carries the languages.
const sync = fs.readFileSync(ROOT + '/mobile/sync-web.sh', 'utf8');
if (!/i18n/.test(sync)) fail('mobile/sync-web.sh does not copy i18n/');

if (bad.length) { console.error(bad.join('\n')); process.exit(1); }
console.log(`i18n: ${Object.keys(en).length} English keys, every key the code asks for exists and every one is asked for; ` +
  `13 languages with note names; naming, plurals and the pseudo-locale: OK (${r.line})`);
