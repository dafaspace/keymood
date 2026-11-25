#!/usr/bin/env python3
"""Keymood's app icon, drawn from the app's own numbers so it matches the wheel.

The colours are the default palette (Itten, `PALETTES.itten` in index.html), lifted for
the dark theme exactly as the wheel and the header mark lift them (`lightenHex(c, .16)`).
The geometry is the header mark's (`paintWordmark`): twelve ring segments, C centred at
the top, inner radius 0.6 of the outer.

Writes SVGs next to this file; tools/icon-lab.html shows them side by side. A chosen
variant is rasterised to icon.png with headless Chrome (see DEV.md, Icon).
"""
import math, os

ITTEN = ['#E3000F', '#EF4E1C', '#F47E1B', '#FBB034', '#F6E500', '#8DC63F',
         '#1FA64A', '#00A99D', '#0061A8', '#2E3192', '#662D91', '#A21D6B']
BG_DARK, BG_LIGHT = '#1c1c1a', '#e7e3da'
HERE = os.path.dirname(os.path.abspath(__file__))


def lighten(hex_, t):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    up = lambda v: round(v + (255 - v) * t)
    return '#%02x%02x%02x' % (up(r), up(g), up(b))


def ring(cx, cy, r_out, r_in, colours, gap_deg=0.0):
    """Twelve annular segments, C (index 0) centred at the top, clockwise in fifths."""
    sl = 2 * math.pi / 12
    gap = math.radians(gap_deg) / 2
    out = []
    for i, col in enumerate(colours):
        a0 = -math.pi / 2 + i * sl - sl / 2 + gap
        # Touching segments get a hair of overlap: anti-aliasing on two edges that meet
        # exactly lets the ground show through as a thin seam.
        a1 = a0 + sl - 2 * gap + (math.radians(0.4) if not gap else 0)
        p = lambda r, a: '%.3f %.3f' % (cx + r * math.cos(a), cy + r * math.sin(a))
        d = ('M %s A %.3f %.3f 0 0 1 %s L %s A %.3f %.3f 0 0 0 %s Z'
             % (p(r_out, a0), r_out, r_out, p(r_out, a1), p(r_in, a1), r_in, r_in, p(r_in, a0)))
        out.append('<path d="%s" fill="%s"/>' % (d, col))
    return '\n  '.join(out)


def svg(body, bg, size=1024):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '  <rect width="%d" height="%d" fill="%s"/>\n  %s\n</svg>\n'
            % (size, size, size, size, size, size, bg, body))


S, C = 1024, 512
# Outer radius 0.38 of the side: inside the 0.40 safe circle of a maskable Android icon
# and clear of iOS's rounded corners.
R = S * 0.38
lifted = [lighten(c, 0.16) for c in ITTEN]

variants = {
    # A: the header mark, as the wheel draws it in the dark theme.
    'a': svg(ring(C, C, R, R * 0.60, lifted), BG_DARK),
    # B: the wheel itself, major ring outside, minor ring inside (the same colours a
    # little deeper, as the inner ring reads in the app), with the dark hub.
    'b': svg(ring(C, C, R, R * 0.70, lifted, 0.6) + '\n  ' +
             ring(C, C, R * 0.70, R * 0.42, ITTEN, 0.6), BG_DARK),
    # C: the header mark in the light theme, raw palette on the light ground.
    'c': svg(ring(C, C, R, R * 0.60, ITTEN), BG_LIGHT),
}
for k, v in variants.items():
    with open(os.path.join(HERE, 'icon-%s.svg' % k), 'w') as f:
        f.write(v)
print('wrote', ', '.join('icon-%s.svg' % k for k in variants))
