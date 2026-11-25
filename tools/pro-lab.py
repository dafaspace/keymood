#!/usr/bin/env python3
"""Mock-up: how a stranger finds Keymood Pro (Dafa, 25 Nov: "a button to go Pro, then a
code or a purchase"). Two screens on a 402x874 iPhone: the entry points, and the Pro
sheet. Writes pro-lab.html next to layout-lab.html."""
import os
import layout_lab_shared as L

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = L.W, L.H


def tabs_with_lock():
    s = '<rect x="16" y="586" width="370" height="44" rx="22" fill="%s"/>' % L.BG2
    s += L.pill(18, 588, 120, 40, 'Dice', pri=True) + L.text(196, 608, 'Metronome', 13, L.SUB)
    # Progressions shown to everyone, with a small lock: the value is where people look.
    s += L.text(300, 608, 'Progressions', 13, L.SUB)
    s += ('<g transform="translate(352 600)" fill="none" stroke="%s" stroke-width="1.4"><rect x="0" y="5" width="11" height="8" rx="1.5"/>'
          '<path d="M2.5 5V3.5a3 3 0 0 1 6 0V5"/></g>' % L.SUB)
    return s


def pro_pill():
    # A small "Pro" pill in the app bar, beside the settings gear; gone once Pro is on.
    return ('<rect x="236" y="62" width="52" height="30" rx="15" fill="none" stroke="#e8c26a" stroke-width="1.5"/>'
            + L.text(262, 77, 'Pro', 13, '#e8c26a', 600))


def entry():
    return (L.header() + pro_pill() + L.wheel(False) + tabs_with_lock()
            + L.text(20, 660, 'CHANGE ON ROLL', 10, L.SUB, 500, 'start'))


def sheet():
    s = L.header() + L.wheel(False) + '<rect width="%d" height="%d" fill="rgba(0,0,0,.55)"/>' % (W, H)
    y0 = 300
    s += '<rect x="0" y="%d" width="%d" height="%d" rx="18" fill="%s"/>' % (y0, W, H - y0, L.BG2)
    s += '<rect x="181" y="%d" width="40" height="5" rx="2.5" fill="#55544f"/>' % (y0 + 8)
    s += L.text(24, y0 + 44, 'Keymood Pro', 22, L.INK, 600, 'start')
    s += L.text(24, y0 + 72, 'Practice that does not go stale.', 13, L.SUB, 400, 'start')
    items = [('177 progressions in any key', 'jazz, baroque, blues, flamenco, film, folk and more'),
             ('Loop and Click', 'play along at your tempo, as long as you like'),
             ('Twist', 'the same progression again, with a surprising turn')]
    y = y0 + 108
    for t, sub in items:
        s += '<circle cx="34" cy="%d" r="4" fill="#e8c26a"/>' % (y + 1)
        s += L.text(48, y, t, 14, L.INK, 500, 'start') + L.text(48, y + 20, sub, 11.5, L.SUB, 400, 'start')
        y += 52
    # No price until Pro can be bought (Dafa, 25 Nov).
    s += L.text(201, y + 4, 'Not on sale yet.', 13, L.SUB)
    s += L.pill(24, y + 18, 354, 48, 'Tell me when it is', pri=True, size=14)
    s += L.text(201, y + 84, 'Opens an email to hello@dafaspace.com.', 11.5, L.SUB)
    s += L.text(24, y + 112, 'HAVE A CODE?', 10, L.SUB, 500, 'start')
    s += '<rect x="24" y="%d" width="270" height="44" rx="10" fill="%s" stroke="rgba(255,255,255,.15)"/>' % (y + 124, L.BG)
    s += L.text(38, y + 146, 'Paste a code', 14, '#6a6964', 400, 'start')
    s += L.pill(302, y + 124, 76, 44, 'Use')
    return s


html = ('<!doctype html><html><head><meta charset="utf-8"><title>Keymood Pro</title><style>'
        'body{margin:0;padding:20px;background:#6b6b6b;font:13px/1.35 -apple-system,sans-serif;color:#fff}'
        '.row{display:flex;gap:26px;align-items:flex-start}figure{margin:0;width:300px}svg{width:300px;height:auto;display:block}'
        'figcaption{margin-top:8px}figcaption b{display:block;font-size:14px;margin-bottom:3px}figcaption span{color:#e9e6de}'
        '</style></head><body><div class="row">'
        + L.phone(entry(), '1 - where Pro is found',
                  'A gold Pro pill in the app bar, and the Progressions tab shown to everyone with a lock. '
                  'Both open the same sheet. Once Pro is on, the pill goes and the lock goes.')
        + L.phone(sheet(), '2 - the Pro sheet',
                  'What Pro gives and a code field. Until a shop exists it says so plainly, shows '
                  'no price, and an email button counts who wants it.')
        + '</div></body></html>')
open(os.path.join(HERE, 'pro-lab.html'), 'w').write(html)
print('ok')
