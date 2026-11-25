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

# Something in the middle of B (Dafa, 25 Nov: "maybe add something in the centre?").
CREAM = '#f3efe6'
wheel = ring(C, C, R, R * 0.70, lifted, 0.6) + '\n  ' + ring(C, C, R * 0.70, R * 0.42, ITTEN, 0.6)
HUB = R * 0.42


def c_outline(i=0):
    """The app's own selection mark: sector i's outer segment lifted, in a dark halo and a white
    line (0 = C, 2 = D)."""
    sl = 2 * math.pi / 12
    a0, a1 = -math.pi / 2 + i * sl - sl / 2, -math.pi / 2 + i * sl + sl / 2
    p = lambda r, a: '%.3f %.3f' % (C + r * math.cos(a), C + r * math.sin(a))
    ro, ri = R * 1.035, R * 0.70
    d = ('M %s A %.3f %.3f 0 0 1 %s L %s A %.3f %.3f 0 0 0 %s Z'
         % (p(ro, a0), ro, ro, p(ro, a1), p(ri, a1), ri, ri, p(ri, a0)))
    return ('<path d="%s" fill="%s"/><path d="%s" fill="none" stroke="#1c1c1a" stroke-width="22" '
            'stroke-linejoin="round"/><path d="%s" fill="none" stroke="#ffffff" stroke-width="9" '
            'stroke-linejoin="round"/>' % (d, lighten(ITTEN[i], 0.30), d, d))


def eighth_note(cx, cy, s, col):
    """An eighth note, head low-left, stem up, one flag; s = head width."""
    hx, hy = cx - s * 0.28, cy + s * 0.55
    stem_x = hx + s * 0.47
    top = cy - s * 0.95
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" transform="rotate(-22 %.1f %.1f)" fill="%s"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
            '<path d="M %.1f %.1f c %.1f %.1f %.1f %.1f %.1f %.1f c %.1f %.1f %.1f %.1f %.1f %.1f Z" fill="%s"/>'
            % (hx, hy, s * 0.5, s * 0.36, hx, hy, col,
               stem_x - s * 0.08, top, s * 0.08, hy - top, col,
               stem_x, top, s * 0.05, s * 0.35, s * 0.62, s * 0.42, s * 0.48, s * 1.05,
               s * 0.02, s * -0.42, s * -0.38, s * -0.55, s * -0.48, s * -0.62, col))


variants.update({
    # B1: a cream hub, as the first icon had, so the colours sit on light at the middle.
    'b1': svg(wheel + '\n  <circle cx="%d" cy="%d" r="%.1f" fill="%s"/>' % (C, C, HUB * 0.92, CREAM), BG_DARK),
    # B2: an eighth note in the hub - says "music" before "colour".
    'b2': svg(wheel + '\n  ' + eighth_note(C, C, HUB * 0.62, CREAM), BG_DARK),
    # B3: the app's selection on C - the gesture the app is used by.
    'b3': svg(wheel + '\n  ' + c_outline(), BG_DARK),
    # B4: B3 and the note together.
    'b4': svg(wheel + '\n  ' + c_outline() + '\n  ' + eighth_note(C, C, HUB * 0.62, CREAM), BG_DARK),
})

def lum(hex_):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def word(radius, colours, size):
    """KEYMOOD, a letter per sector over the top half: K on Eb (9 o'clock) to D on A
    (3 o'clock), M on C at the top, each letter upright to the circle, white on every
    sector."""
    out = []
    for k, ch in enumerate('KEYMOOD'):
        i = (9 + k) % 12
        a = -90 + i * 30
        x, y = C + radius * math.cos(math.radians(a)), C + radius * math.sin(math.radians(a))
        # One ink for the whole word: switching to dark on the amber sectors split the
        # name in two (seen 25 Nov). White with a thin dark edge reads on every sector.
        out.append('<text x="%.1f" y="%.1f" transform="rotate(%.1f %.1f %.1f)" fill="#ffffff" '
                   'stroke="#1c1c1a" stroke-width="%.1f" stroke-linejoin="round" paint-order="stroke" '
                   'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-weight="700" '
                   'font-size="%.1f" text-anchor="middle" dominant-baseline="central">%s</text>'
                   % (x, y, a + 90, x, y, size * 0.14, size, ch))
    return '\n  '.join(out)


variants.update({
    # K1: KEYMOOD across the outer ring's top half (Dafa, 25 Nov).
    'k1': svg(wheel + '\n  ' + word(R * 0.85, lifted, R * 0.21), BG_DARK),
    # K2: the same in the inner ring, closer to the hub.
    'k2': svg(wheel + '\n  ' + word(R * 0.56, ITTEN, R * 0.17), BG_DARK),
})
# B3 with D selected (Dafa, 25 Nov: "b3 D selected").
variants['b3d'] = svg(wheel + '\n  ' + c_outline(2), BG_DARK)

def wheel_exploded(i, push, both_rings, lift):
    """The wheel with sector i moved outward along its own bisector by `push` (a share of R),
    instead of outlined: the outer segment alone, or the whole wedge with its minor."""
    sl = 2 * math.pi / 12
    mid = -math.pi / 2 + i * sl
    dx, dy = R * push * math.cos(mid), R * push * math.sin(mid)
    outer = [c if k != i else lighten(c, lift) for k, c in enumerate(lifted)]
    inner = list(ITTEN)
    # Draw the rings without sector i, then sector i on top, moved.
    def only(colours, keep):
        return [c if k == keep else 'none' for k, c in enumerate(colours)]
    def without(colours, drop):
        return [c if k != drop else 'none' for k, c in enumerate(colours)]
    base = (ring(C, C, R, R * 0.70, without(outer, i), 0.6) + '\n  ' +
            ring(C, C, R * 0.70, R * 0.42, without(inner, i) if both_rings else inner, 0.6))
    moved = ring(C, C, R, R * 0.70, only(outer, i), 0.6)
    if both_rings:
        moved += '\n  ' + ring(C, C, R * 0.70, R * 0.42, only(inner, i), 0.6)
    return base + '\n  <g transform="translate(%.2f %.2f)">%s</g>' % (dx, dy, moved)


# D pushed out instead of outlined (Dafa, 25 Nov: "reads better small").
variants['x1'] = svg(wheel_exploded(2, 0.08, False, 0.0), BG_DARK)   # the outer segment, same colour
variants['x2'] = svg(wheel_exploded(2, 0.08, True, 0.0), BG_DARK)    # the whole wedge, same colour
variants['x3'] = svg(wheel_exploded(2, 0.08, False, 0.22), BG_DARK)  # the outer segment, lighter

SHADOW = ('<defs><filter id="lift" x="-30%%" y="-30%%" width="160%%" height="160%%">'
          '<feDropShadow dx="0" dy="%.1f" stdDeviation="%.1f" flood-color="#000" flood-opacity="0.55"/>'
          '</filter></defs>')


def seg_path(cx, cy, r_out, r_in, i, gap_deg=0.6):
    sl = 2 * math.pi / 12
    gap = math.radians(gap_deg) / 2
    a0 = -math.pi / 2 + i * sl - sl / 2 + gap
    a1 = a0 + sl - 2 * gap
    p = lambda r, a: '%.3f %.3f' % (cx + r * math.cos(a), cy + r * math.sin(a))
    return ('M %s A %.3f %.3f 0 0 1 %s L %s A %.3f %.3f 0 0 0 %s Z'
            % (p(r_out, a0), r_out, r_out, p(r_out, a1), p(r_in, a1), r_in, r_in, p(r_in, a0)))


def wheel_lifted(i, inner_ring=False, scale=1.08, lift=0.10, cx=C, cy=C, r=None):
    """Sector i raised off the wheel toward the viewer: drawn again on top, a little larger
    about its own middle, a shade lighter, over a soft shadow - instead of an outline. Works
    the same on the inner ring, since nothing has to move outward."""
    r = r or R
    outer_c, inner_c = lifted, ITTEN
    body = ring(cx, cy, r, r * 0.70, outer_c, 0.6) + '\n  ' + ring(cx, cy, r * 0.70, r * 0.42, inner_c, 0.6)
    ro, ri = (r * 0.70, r * 0.42) if inner_ring else (r, r * 0.70)
    col = lighten((inner_c if inner_ring else outer_c)[i], lift)
    sl = 2 * math.pi / 12
    mid = -math.pi / 2 + i * sl
    rm = (ro + ri) / 2
    mx, my = cx + rm * math.cos(mid), cy + rm * math.sin(mid)
    d = seg_path(cx, cy, ro, ri, i)
    return (SHADOW % (r * 0.035, r * 0.045) + '\n  ' + body +
            '\n  <g transform="translate(%.2f %.2f) scale(%.3f) translate(%.2f %.2f)" filter="url(#lift)">'
            '<path d="%s" fill="%s"/></g>' % (mx, my, scale, -mx, -my, d, col))


variants['u1'] = svg(wheel_lifted(2), BG_DARK)                         # D raised
variants['u2'] = svg(wheel_lifted(2, scale=1.12, lift=0.16), BG_DARK)  # D raised more

def ring_gap(cx, cy, r_out, r_in, colours, g):
    """Like ring(), but the gaps between segments have a constant width g (in px of the
    1024 grid) instead of a constant angle, so they do not widen toward the rim."""
    sl = 2 * math.pi / 12
    out = []
    for i, col in enumerate(colours):
        if col == 'none':
            continue
        out.append('<path d="%s" fill="%s"/>' % (seg_gap(cx, cy, r_out, r_in, i, g), col))
    return '\n  '.join(out)


def seg_gap(cx, cy, r_out, r_in, i, g):
    sl = 2 * math.pi / 12
    a0, a1 = -math.pi / 2 + i * sl - sl / 2, -math.pi / 2 + i * sl + sl / 2
    do, di = math.asin(g / 2 / r_out), math.asin(min(0.99, g / 2 / r_in))
    p = lambda r, a: '%.3f %.3f' % (cx + r * math.cos(a), cy + r * math.sin(a))
    return ('M %s A %.3f %.3f 0 0 1 %s L %s A %.3f %.3f 0 0 0 %s Z'
            % (p(r_out, a0 + do), r_out, r_out, p(r_out, a1 - do), p(r_in, a1 - di), r_in, r_in, p(r_in, a0 + di)))


def wheel_gap_raised(i, g, scale=1.12, lift=0.16):
    """Icon G (D raised more) with gaps of width g between all segments and between the rings."""
    ro, rm, ri = R, R * 0.70, R * 0.42
    body = (ring_gap(C, C, ro, rm + g / 2, lifted, g) + '\n  ' + ring_gap(C, C, rm - g / 2, ri, ITTEN, g))
    col = lighten(lifted[i], lift)
    sl = 2 * math.pi / 12
    mid = -math.pi / 2 + i * sl
    rmid = (ro + rm) / 2
    mx, my = C + rmid * math.cos(mid), C + rmid * math.sin(mid)
    d = seg_gap(C, C, ro, rm + g / 2, i, g)
    return (SHADOW % (R * 0.035, R * 0.045) + '\n  ' + body +
            '\n  <g transform="translate(%.2f %.2f) scale(%.3f) translate(%.2f %.2f)" filter="url(#lift)">'
            '<path d="%s" fill="%s"/></g>' % (mx, my, scale, -mx, -my, d, col))


# Wider gaps between the segments (Dafa, 25 Nov), on G (D raised more).
for g in (12, 22, 34):
    variants['g%d' % g] = svg(wheel_gap_raised(2, g), BG_DARK)

def wheel_gap_raised_on(i, g, outer_cols, inner_cols, scale=1.12, lift=0.16, shadow=0.55):
    ro, rm, ri = R, R * 0.70, R * 0.42
    body = (ring_gap(C, C, ro, rm + g / 2, outer_cols, g) + '\n  ' + ring_gap(C, C, rm - g / 2, ri, inner_cols, g))
    col = lighten(outer_cols[i], lift)
    sl = 2 * math.pi / 12
    mid = -math.pi / 2 + i * sl
    rmid = (ro + rm) / 2
    mx, my = C + rmid * math.cos(mid), C + rmid * math.sin(mid)
    d = seg_gap(C, C, ro, rm + g / 2, i, g)
    sh = SHADOW.replace('flood-opacity="0.55"', 'flood-opacity="%.2f"' % shadow)
    return (sh % (R * 0.035, R * 0.045) + '\n  ' + body +
            '\n  <g transform="translate(%.2f %.2f) scale(%.3f) translate(%.2f %.2f)" filter="url(#lift)">'
            '<path d="%s" fill="%s"/></g>' % (mx, my, scale, -mx, -my, d, col))


# Gap 28, between 22 and 34 (Dafa, 25 Nov), on dark and on white.
variants['w28d'] = svg(wheel_gap_raised(2, 28), BG_DARK)
# On white the light theme's colours: the palette as it is, a deeper minor ring, a softer shadow.
deeper = ['#%02x%02x%02x' % tuple(max(0, int(int(c[k:k + 2], 16) * 0.82)) for k in (1, 3, 5)) for c in ITTEN]
variants['w28w'] = svg(wheel_gap_raised_on(2, 28, ITTEN, deeper, lift=0.25, shadow=0.35), '#ffffff')
variants['w28c'] = svg(wheel_gap_raised_on(2, 28, ITTEN, deeper, lift=0.25, shadow=0.35), '#f3efe6')

# Gap 28 with nothing raised (Dafa, 25 Nov: "try the icon without the raise").
def plain_gap(outer_cols, inner_cols, g=28):
    return ring_gap(C, C, R, R * 0.70 + g / 2, outer_cols, g) + '\n  ' + ring_gap(C, C, R * 0.70 - g / 2, R * 0.42, inner_cols, g)
variants['p28d'] = svg(plain_gap(lifted, ITTEN), BG_DARK)
variants['p28w'] = svg(plain_gap(ITTEN, deeper), '#ffffff')
variants['p28c'] = svg(plain_gap(ITTEN, deeper), '#f3efe6')

def blend(hex_, alpha, bg):
    """A colour drawn at `alpha` over `bg`, as the app's canvas draws its rings."""
    f = [int(hex_[k:k + 2], 16) for k in (1, 3, 5)]
    b = [int(bg[k:k + 2], 16) for k in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(x * alpha + y * (1 - alpha)) for x, y in zip(f, b))


# The rings in the app's own colours, measured on its canvas on 25 Nov: the outer ring at
# alpha 0.95 and the inner at 0.82 over the ground, in Itten as it is (light theme) or
# lifted by 0.16 (dark theme). The first white icon darkened the inner ring instead
# (x 0.82), which turned it muddy - Dafa: "dirty, not the app's colours".
def app_rings(bg, dark):
    base = lifted if dark else ITTEN
    return [blend(c, 0.95, bg) for c in base], [blend(c, 0.82, bg) for c in base]

o, i_ = app_rings('#ffffff', False)
variants['q28w'] = svg(plain_gap(o, i_), '#ffffff')
o, i_ = app_rings(BG_DARK, True)
variants['q28d'] = svg(plain_gap(o, i_), BG_DARK)
for k, v in variants.items():
    with open(os.path.join(HERE, 'icon-%s.svg' % k), 'w') as f:
        f.write(v)
print('wrote', ', '.join('icon-%s.svg' % k for k in variants))
