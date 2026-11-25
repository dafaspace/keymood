#!/usr/bin/env python3
"""Mock-up: how a selected key could look on the app's wheel - today's outline against a
sector raised toward the viewer (Dafa, 25 Nov). Draws the wheel roughly as the app does
(dark theme, Itten, major ring outside, minor inside) and writes selection-lab.html."""
import math, os
import icon as I

HERE = os.path.dirname(os.path.abspath(__file__))
S = 460
CX = CY = S / 2
R = S * 0.46
MAJ = ['C', 'G', 'D', 'A', 'E', 'B', 'F♯', 'D♭', 'A♭', 'E♭', 'B♭', 'F']
MIN = ['Am', 'Em', 'Bm', 'F♯m', 'C♯m', 'G♯m', 'D♯m', 'B♭m', 'Fm', 'Cm', 'Gm', 'Dm']
OUT_C = [I.lighten(c, 0.16) for c in I.ITTEN]
IN_C = [I.lighten(c, 0.02) for c in I.ITTEN]


def label(text, i, r, size, col_bg, weight=500):
    a = -math.pi / 2 + i * 2 * math.pi / 12
    x, y = CX + r * math.cos(a), CY + r * math.sin(a)
    ink = '#1c1c1a' if I.lum(col_bg) > 0.40 else '#ffffff'
    return ('<text x="%.1f" y="%.1f" fill="%s" font-family="-apple-system, Helvetica Neue, sans-serif" '
            'font-size="%.1f" font-weight="%d" text-anchor="middle" dominant-baseline="central">%s</text>'
            % (x, y, ink, size, weight, text))


def wheel(sel=None, mode='none'):
    """sel = (index, inner?) ; mode = 'outline' | 'raise'."""
    parts = [I.ring(CX, CY, R, R * 0.70, OUT_C, 0.4), I.ring(CX, CY, R * 0.70, R * 0.42, IN_C, 0.4),
             '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#1c1c1a"/>' % (CX, CY, R * 0.42)]
    for i in range(12):
        if sel and mode == 'raise' and sel == (i, False):
            continue
        parts.append(label(MAJ[i], i, R * 0.85, R * 0.085, OUT_C[i]))
    for i in range(12):
        if sel and mode == 'raise' and sel == (i, True):
            continue
        parts.append(label(MIN[i], i, R * 0.56, R * 0.062, IN_C[i]))
    if sel:
        i, inner = sel
        ro, ri = (R * 0.70, R * 0.42) if inner else (R, R * 0.70)
        d = I.seg_path(CX, CY, ro, ri, i, 0.4)
        if mode == 'outline':
            parts.append('<path d="%s" fill="none" stroke="#1c1c1a" stroke-width="7" stroke-linejoin="round"/>'
                         '<path d="%s" fill="none" stroke="#fff" stroke-width="2.6" stroke-linejoin="round"/>' % (d, d))
        else:
            col = I.lighten((IN_C if inner else OUT_C)[i], 0.12)
            a = -math.pi / 2 + i * 2 * math.pi / 12
            rm = (ro + ri) / 2
            mx, my = CX + rm * math.cos(a), CY + rm * math.sin(a)
            txt = label(MIN[i] if inner else MAJ[i], i, R * (0.56 if inner else 0.85),
                        R * (0.062 if inner else 0.085), col, 600)
            parts.append('<g transform="translate(%.2f %.2f) scale(1.09) translate(%.2f %.2f)" filter="url(#lift)">'
                         '<path d="%s" fill="%s"/>%s</g>' % (mx, my, -mx, -my, d, col, txt))
    defs = ('<defs><filter id="lift" x="-40%" y="-40%" width="180%" height="180%">'
            '<feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#000" flood-opacity="0.6"/></filter></defs>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s'
            '<rect width="100%%" height="100%%" fill="#1c1c1a"/>%s</svg>' % (S, S, S, S, defs, ''.join(parts)))


states = {
    'now-c': (wheel((0, False), 'outline'), 'Now: C selected (outline)'),
    'raise-c': (wheel((0, False), 'raise'), 'Raised: C selected'),
    'now-am': (wheel((0, True), 'outline'), 'Now: Am selected (outline)'),
    'raise-am': (wheel((0, True), 'raise'), 'Raised: Am selected'),
}
for k, (v, _) in states.items():
    open(os.path.join(HERE, 'sel-%s.svg' % k), 'w').write(v)
figs = ''.join('<figure><img src="sel-%s.svg" width="300" height="300" alt=""><figcaption>%s</figcaption></figure>'
               % (k, cap) for k, (_, cap) in states.items())
open(os.path.join(HERE, 'selection-lab.html'), 'w').write(
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Keymood selection</title><style>body{margin:0;padding:20px 16px;background:#111110;color:#e8e6e0;'
    'font:14px/1.4 -apple-system,system-ui,sans-serif}.row{display:flex;flex-wrap:wrap;gap:22px}'
    'figure{margin:0;text-align:center}figcaption{margin-top:6px;font-weight:600}</style></head><body>'
    '<div class="row">%s</div></body></html>' % figs)
print('wrote', ', '.join(states))
