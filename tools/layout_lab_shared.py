"""Drawing helpers shared by the phone mock-up labs (layout-lab, pro-lab)."""
import math
import icon as I

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


