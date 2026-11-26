#!/bin/bash
# Copy the web app into the native bundle, and check what was copied.
#
# The product is ../index.html and the files it loads. This folder only delivers it:
# the web app is the product, Capacitor is the delivery shell. Never edit www/ by hand;
# it is regenerated on every run and is not committed.
#
#   ./mobile/sync-web.sh     copy into www/, run `cap sync`, verify
#
# Taken from AstroVarium's (mobile/sync-web.sh), which learnt it from Cinemail: what goes
# in is a list, and a list is how files go missing (Cinemail shipped a bundle that 404'd
# on ./qr.js at launch). So after copying, the script re-reads index.html, works out
# every local file it loads, and stops if any is absent.

set -euo pipefail
cd "$(dirname "$0")"

SRC=".."
DST="./www"

# What the app loads at runtime. The piano samples are fetched by name (PIANO_FILES), so
# they are listed here and checked below against that list in index.html. Not the
# service worker, the manifest or the web icons: the store build never registers the
# worker (index.html, NATIVE), and its icon lives in Assets.xcassets.
ASSETS=(index.html)
PIANO=$(grep -o "var PIANO_FILES *= *\[[^]]*\]" "$SRC/index.html" | grep -o "'[A-Za-z0-9]*'" | tr -d "'")
[ -n "$PIANO" ] || { echo "[sync] FAIL: no PIANO_FILES list in index.html" >&2; exit 1; }

rm -rf "$DST"; mkdir -p "$DST/piano"
for f in "${ASSETS[@]}"; do
  [ -f "$SRC/$f" ] || { echo "[sync] FAIL: $SRC/$f is missing" >&2; exit 1; }
  cp "$SRC/$f" "$DST/"
done
n=0
for p in $PIANO; do
  [ -f "$SRC/piano/$p.mp3" ] || { echo "[sync] FAIL: piano/$p.mp3 is missing" >&2; exit 1; }
  cp "$SRC/piano/$p.mp3" "$DST/piano/"; n=$((n+1))
done
echo "[sync] copied ${#ASSETS[@]} page and $n piano samples into $DST"

# sync, not copy: copy moves the web files only, and a plugin added to package.json
# would then be missing from the native project until somebody remembered update.
node_modules/.bin/cap sync ios >/dev/null
echo "[sync] cap sync ios: done"

# Verify the bundle Xcode will actually use, not only www/.
node - "$DST" "ios/App/App/public" <<'CHECK'
const fs=require('fs'), path=require('path');
const dirs=process.argv.slice(2).filter(d=>fs.existsSync(d));
const html=fs.readFileSync(path.join(dirs[0],'index.html'),'utf8');
const refs=new Set();
const add=p=>{ p=String(p).split('?')[0].split('#')[0].replace(/^\.\//,'');
  if(p && !/^(https?:|data:|blob:|mailto:|capacitor:|#)/.test(p) && !p.includes('${')) refs.add(p); };
for(const m of html.matchAll(/\b(?:src|href)\s*=\s*"([^"]+)"/g)) add(m[1]);
const pf=html.match(/var PIANO_FILES *= *\[([^\]]*)\]/);
for(const m of pf[1].matchAll(/'([A-Za-z0-9]+)'/g)) add('piano/'+m[1]+'.mp3');
// Loaded only by the web build, guarded by NATIVE in index.html.
for(const webOnly of ['sw.js','manifest.json','icon.png','icon-192.png','apple-touch-icon.png']) refs.delete(webOnly);
let bad=0;
for(const dir of dirs){
  const missing=[...refs].filter(p=>!fs.existsSync(path.join(dir,p)));
  if(missing.length){ bad=1; console.error(`[verify] FAIL: ${dir} lacks ${missing.join(', ')}`); }
  else console.log(`[verify] ok: ${dir} has all ${refs.size} files the app loads`);
}
// Nothing from development or the web-only shell.
const forbidden=['DEV.md','tools','sw.js','wrangler.jsonc','.assetsignore','manifest.json'];
for(const dir of dirs){
  const present=forbidden.filter(f=>fs.existsSync(path.join(dir,f)));
  if(present.length){ bad=1; console.error(`[verify] FAIL: ${dir} carries ${present.join(', ')}`); }
}
// The store build sells Pro in the store: no tester-code field may reach it (App Store
// 3.1.1). index.html hides it under NATIVE; this checks the guard is still there.
if(!/NATIVE/.test(html)){ bad=1; console.error('[verify] FAIL: index.html has no NATIVE guard'); }
if(!bad) console.log('[verify] ok: nothing from development in the bundle');
process.exit(bad);
CHECK
echo "[sync] done"
