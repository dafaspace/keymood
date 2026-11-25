#!/usr/bin/env node
// Makes a Keymood Pro tester code: a link that turns Pro on in one browser until a date.
//
//   node tools/pro-code.mjs <label> <days>        e.g.  node tools/pro-code.mjs T03 30
//
// The code is "<payload>.<signature>": the payload is "label|YYYYMMDD" (the last day it
// works), base64url; the signature is ECDSA P-256 over the payload text, made with the
// private key in ../private/keymood-pro-signing.json - outside this public repo, never
// committed. The app holds only the public key, so it can check a code but not make one.
// Use a short label (a tester number), not a name: it is stored in the tester's browser.
// A code cannot be withdrawn before its date without a release; keep the days short.
import { readFileSync } from 'node:fs';
import { createPrivateKey, sign } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const [label, daysArg] = process.argv.slice(2);
const days = Number(daysArg);
if (!label || !/^[A-Za-z0-9-]{1,16}$/.test(label) || !Number.isInteger(days) || days < 1 || days > 366) {
  console.error('usage: node tools/pro-code.mjs <label: letters, digits, -; up to 16> <days: 1-366>');
  process.exit(1);
}
const keyFile = join(here, '..', '..', 'private', 'keymood-pro-signing.json');
const key = createPrivateKey({ key: JSON.parse(readFileSync(keyFile, 'utf8')).private, format: 'jwk' });
const end = new Date(Date.now() + days * 864e5);
const ymd = end.getUTCFullYear() + String(end.getUTCMonth() + 1).padStart(2, '0') + String(end.getUTCDate()).padStart(2, '0');
const b64u = (b) => Buffer.from(b).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const payload = b64u(label + '|' + ymd);
const sig = sign('sha256', Buffer.from(payload, 'ascii'), { key, dsaEncoding: 'ieee-p1363' });
const code = payload + '.' + b64u(sig);
console.log('label:   ' + label);
console.log('works to: ' + ymd.slice(0, 4) + '-' + ymd.slice(4, 6) + '-' + ymd.slice(6) + ' (inclusive)');
console.log('code:    ' + code);
console.log('link:    https://keymood.app/?pro=' + code);
