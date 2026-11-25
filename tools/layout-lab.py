#!/usr/bin/env python3
"""Phone layout mock-ups for Keymood's controls (Dafa, 25 Nov: important controls must not
scroll away, but must not crowd the scrolling part). Three options from the music-app
survey (scratchpad ux-music-apps.md), drawn to scale on a 402x874 pt screen:
A - transport on the wheel (hub and corners), B - a dock at the bottom with the list in a
sheet, C - A plus a tall sheet for the progression list only. Writes layout-lab.html."""
import math, os
import icon as I

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 402, 874
BG, BG2, BG3, INK, SUB = '#1c1c1a', '#252522', '#2e2e2a', '#e8e6e0', '#9a9890'
CX, CY, R = W / 2, 150 + 200, 196
OUT = [I.blend(I.lighten(c, .16), .95, BG) for c in I.ITTEN]
INN = [I.blend(I.lighten(c, .16), .82, BG) for c in I.ITTEN]
MAJ = ['C', 'G', 'D', 'A', 'E', 'B', 'F♯', 'D♭', 'A♭', 'E♭', 'B♭', 'F']


def text(x, y, s, size=13, col=INK, w=400, anchor='middle'):
    return ('<text x="%.1f" y="%.1f" fill="%s" font-family="-apple-system,Helvetica Neue,sans-serif" '
            'font-size="%.1f" font-weight="%d" text-anchor="%s" dominant-baseline="central">%s</text>'
            % (x, y, col, size, w, anchor, s))


def pill(x, y, w, h, label, on=False, pri=False, size=12):
    fill = INK if pri else (BG3 if not on else BG2)
    stroke = ' stroke="%s" stroke-width="1.5"' % INK if on and not pri else ''
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"%s/>' % (x, y, w, h, h / 2, fill, stroke)
            + text(x + w / 2, y + h / 2, label, size, BG if pri else INK, 600 if (on or pri) else 400))


def wheel(hub_play=False):
    s = [I.ring(CX, CY, R, R * .70, OUT, .4), I.ring(CX, CY, R * .70, R * .40, INN, .4),
         '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#1f1f1d" stroke="rgba(255,255,255,.14)"/>' % (CX, CY, R * .40)]
    for i, n in enumerate(MAJ):
        a = -math.pi / 2 + i * math.pi / 6
        s.append(text(CX + R * .85 * math.cos(a), CY + R * .85 * math.sin(a), n, 15, '#fff', 500))
    if hub_play:
        s.append(text(CX, CY - 30, 'ii7', 26, INK, 500))
        s.append(text(CX, CY + 2, 'Em7', 15, SUB))
        s.append('<circle cx="%.1f" cy="%.1f" r="17" fill="%s"/>' % (CX, CY + 40, INK))
        s.append('<rect x="%.1f" y="%.1f" width="11" height="11" rx="1.5" fill="%s"/>' % (CX - 5.5, CY + 34.5, BG))
    return ''.join(s)


def header():
    return (text(20, 78, 'KEYMOOD', 15, SUB, 600, 'start')
            + '<rect x="16" y="104" width="205" height="34" rx="17" fill="%s"/>' % BG2
            + pill(18, 106, 66, 30, 'Tonal', pri=True) + text(124, 121, 'Modal', 13, SUB) + text(185, 121, 'Assist', 13, SUB))


def rows(y0, y1, start=0):
    names = ['Axis progression', 'Fifties', 'Royal road', 'Andalusian cadence', 'ii-V-I', 'Rhythm changes A',
             'Pachelbel', 'La Folia', 'Mario cadence', 'Creep', 'Coltrane changes', 'Backdoor', 'Lament bass']
    s, y, k = [], y0, start
    while y + 46 <= y1 and k < len(names):
        on = names[k] == 'ii-V-I'
        s.append('<rect x="16" y="%.1f" width="370" height="42" rx="10" fill="%s"%s/>'
                 % (y, BG2, ' stroke="%s" stroke-width="1.5"' % INK if on else ''))
        s.append(text(28, y + 15, names[k], 13, INK, 500, 'start'))
        s.append(text(28, y + 30, 'I  V  vi  IV' if k % 2 else 'ii7  V7  Imaj7', 10.5, SUB, 400, 'start'))
        y += 46; k += 1
    return ''.join(s)


def corners():
    c = []
    spots = [(8, 158, 'Loop', True), (W - 52, 158, 'Click', False), (8, 498, '−', False), (W - 52, 498, '+', False)]
    for x, y, lab, on in spots:
        c.append('<rect x="%d" y="%d" width="44" height="44" rx="22" fill="%s"%s/>' % (x, y, BG2, ' stroke="%s" stroke-width="1.5"' % INK if on else ''))
        c.append(text(x + 22, y + 22, lab, 11 if len(lab) > 1 else 20, INK, 600 if on else 400))
    c.append(text(CX, 556 - 8, '92 bpm', 11, SUB))
    return ''.join(c)


def phone(body, title, note):
    return ('<figure><svg viewBox="0 0 %d %d" width="%d" height="%d"><rect width="%d" height="%d" rx="44" fill="%s"/>%s'
            '<rect x="150" y="12" width="102" height="30" rx="15" fill="#000"/>'
            '<rect x="136" y="860" width="130" height="5" rx="2.5" fill="#888"/></svg>'
            '<figcaption><b>%s</b><span>%s</span></figcaption></figure>' % (W, H, W, H, W, H, BG, body, title, note))


# A: transport on the wheel - hub is Play/Stop and shows the chord, four corner buttons.
a = (header() + wheel(True) + corners()
     + '<rect x="0" y="566" width="%d" height="308" fill="%s"/>' % (W, BG)
     + text(20, 584, 'PROGRESSIONS · JAZZ', 10, SUB, 500, 'start') + rows(598, 850, 2))
# B: dock at the bottom (58 + home indicator), the list in a sheet over the column.
b = (header() + wheel(True)
     + '<rect x="0" y="560" width="%d" height="222" rx="14" fill="%s"/>' % (W, BG2)
     + '<rect x="181" y="567" width="40" height="5" rx="2.5" fill="#55544f"/>'
     + text(20, 590, 'PROGRESSIONS · JAZZ', 10, SUB, 500, 'start')
     + rows(604, 780, 3).replace('fill="%s"' % BG2, 'fill="%s"' % BG3)
     + '<rect x="0" y="782" width="%d" height="92" fill="#161614"/>' % W
     + pill(16, 792, 96, 44, 'Stop', pri=True) + pill(120, 792, 84, 44, 'Loop', on=True)
     + pill(212, 792, 44, 44, '−') + text(284, 814, '92', 17, INK, 500) + pill(312, 792, 44, 44, '+')
     + text(370, 814, 'bpm', 10, SUB))
# C: A, and the list in a tall sheet that stops below the hub - the wheel's top half and
# its hub stay in view, with the corner controls.
c = (header() + wheel(True) + corners().split('<rect x="8" y="498"')[0]
     + '<rect x="0" y="430" width="%d" height="444" rx="16" fill="%s"/>' % (W, BG2)
     + '<rect x="181" y="437" width="40" height="5" rx="2.5" fill="#55544f"/>'
     + text(20, 460, 'PROGRESSIONS · JAZZ', 10, SUB, 500, 'start')
     # The sheet covers the lower corners, so tempo moves into its header row.
     + pill(252, 446, 36, 30, '−') + text(310, 461, '92', 14, INK, 500) + pill(332, 446, 36, 30, '+')
     + rows(484, 850, 0).replace('fill="%s"' % BG2, 'fill="%s"' % BG3))

html = ('<!doctype html><html><head><meta charset="utf-8"><title>Keymood layouts</title><style>'
        'body{margin:0;padding:20px;background:#6b6b6b;font:13px/1.35 -apple-system,sans-serif;color:#fff}'
        '.row{display:flex;gap:26px;align-items:flex-start}figure{margin:0;width:300px}svg{width:300px;height:auto;display:block}'
        'figcaption{margin-top:8px}figcaption b{display:block;font-size:14px;margin-bottom:3px}figcaption span{color:#e9e6de}'
        '</style></head><body><div class="row">'
        + phone(a, 'A - controls on the wheel',
                'Play/Stop in the hub, which shows the chord. Loop, Click, tempo − and + in the four empty corners. '
                'Nothing added to the fixed part; the list window stays ~320 pt.')
        + phone(b, 'B - a player bar at the bottom',
                'Stop, Loop, − 92 + always under the thumb (92 pt with the home bar). The list lives in a sheet '
                'that can be pulled up over the wheel. Costs 92 pt for good.')
        + phone(c, 'C - A, plus a tall list sheet',
                'Play/Stop in the hub, Loop and Click in the top corners; the list sheet rises to just below the '
                'hub with tempo in its header, so the chord and every control stay in view: ~400 pt for the list.')
        + '</div></body></html>')
open(os.path.join(HERE, 'layout-lab.html'), 'w').write(html)
print('ok')
