"""Vertical sets in Rongpat style. Each returns SVG strings in scene coordinates."""
import math
from .puppets import tint, ids, fish, lerp, clamp

S = '<g stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'

# ------------------------------------------------------------------ KITCHEN (620 x 1000)
KW, KH = 620, 1000


def kitchen_room(night=0.62):
    s = ('<defs><pattern id="kt@" width="40" height="40" patternUnits="userSpaceOnUse"><rect width="40" height="40" fill="#9CC7C9"/>'
         '<rect width="20" height="20" fill="#7FB0AE"/><rect x="20" y="20" width="20" height="20" fill="#7FB0AE"/></pattern>'
         '<pattern id="kg@" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="#22305F"/><path d="M9 0 L9 18 M0 9 L18 9" stroke="#1C1410" stroke-width="3"/></pattern>'
         '<pattern id="kf@" width="80" height="40" patternUnits="userSpaceOnUse"><rect width="80" height="40" fill="#8C7A6A"/><path d="M0 39 L80 39 M40 0 L40 40" stroke="#6E5E50" stroke-width="2"/></pattern></defs>')
    s += '<rect x="-200" y="-200" width="1020" height="1400" fill="#E8D9B5"/>'
    s += '<rect x="-200" y="480" width="1020" height="170" fill="url(#kt@)"/>'
    s += '<rect x="-200" y="820" width="1020" height="380" fill="url(#kf@)"/>'
    s += S
    s += '<rect x="60" y="110" width="150" height="180" fill="url(#kg@)"/><rect x="50" y="288" width="170" height="12" fill="#F3E6C8"/>'
    s += '<path d="M232 120 L352 120" stroke-width="5"/>'
    for x, h in ((252, 70), (292, 84), (332, 64)):
        s += f'<path d="M{x} 120 L{x} {120 + h}" stroke="#8C8C9A" stroke-width="4"/><ellipse cx="{x}" cy="{128 + h}" rx="10" ry="8" fill="#8C8C9A" stroke-width="3"/>'
    s += '<rect x="20" y="380" width="290" height="12" fill="#6B3A1F"/>'
    for x in (50, 92, 134):
        s += f'<circle cx="{x}" cy="356" r="22" fill="#C9D1D6" stroke-width="3"/>'
    s += '<rect x="-200" y="640" width="530" height="180" fill="#6B3A1F"/>'
    s += '<rect x="-200" y="628" width="530" height="16" fill="#D9C8A8"/>'
    s += '<path d="M-200 700 L330 700 M-200 760 L330 760" stroke="#5A2E18" stroke-width="2"/>'
    s += '<rect x="80" y="604" width="140" height="26" rx="4" fill="#1C1410"/>'
    for x in (232, 262, 292):
        s += f'<rect x="{x}" y="590" width="24" height="38" rx="4" fill="#E3A92B" stroke-width="3"/>'
    s += '</g>'
    return ids(tint(s, night))


def cooker(x=150, y=604, steam=0.0, t=0.0, night=0.55, shake=0.0):
    dx = shake * math.sin(t * 60)
    s = S + f'<g transform="translate({x + dx:.1f},{y})">'
    s += '<path d="M-34 -64 L-34 -8 Q-34 0 -24 0 L24 0 Q34 0 34 -8 L34 -64Z" fill="#C9D1D6"/>'
    s += '<rect x="-40" y="-74" width="80" height="14" rx="5" fill="#8C8C9A"/><path d="M40 -68 L84 -76" stroke-width="8"/>'
    s += '<rect x="-7" y="-92" width="14" height="18" fill="#1C1410"/></g></g>'
    out = tint(s, night)
    if steam > 0:
        for i in range(5):
            k = (t * 1.6 + i / 5) % 1
            r = 10 + 30 * k
            out += f'<circle cx="{x + dx + 20 * math.sin(i * 2 + k * 4):.1f}" cy="{y - 100 - 160 * k:.1f}" r="{r:.1f}" fill="#FBF5E9" opacity="{steam * (1 - k) * 0.85:.2f}"/>'
    return out


def fridge(open_=0.0, fish_in=True, sweets='full', night=0.6, light=1.0, t=0.0):
    """Fridge at x 360..590, y 250..820. open_ 0..1. Returns (body, light_spill)."""
    s = S
    s += '<rect x="356" y="246" width="238" height="578" rx="18" fill="#1F7A78"/>'
    out = tint(s + '</g>', night)
    # interior (lit)
    inner = ''
    if open_ > 0.02:
        L = clamp(open_ * 1.3) * light
        inner += S + '<rect x="372" y="262" width="206" height="546" rx="8" fill="#FFE7A0"/>'
        inner += '<path d="M372 420 L578 420 M372 580 L578 580 M372 700 L578 700" stroke-width="5"/>'
        inner += '<rect x="386" y="360" width="34" height="58" rx="5" fill="#DCEFF4"/><rect x="430" y="374" width="30" height="44" rx="5" fill="#E58BA0"/><rect x="470" y="386" width="40" height="32" rx="4" fill="#3E7A3A"/>'
        inner += '</g>'
        if fish_in:
            inner += S + fish(470, 556, 1.0) + '</g>'
        # sweet box
        inner += S + '<rect x="400" y="640" width="130" height="58" rx="6" fill="#E58BA0"/>'
        if sweets == 'full':
            inner += '<g fill="#FBF5E9" stroke-width="2.5">' + ''.join(f'<circle cx="{420 + i * 22}" cy="652" r="10"/>' for i in range(5)) + '</g>'
            inner += '<rect x="400" y="660" width="130" height="38" rx="6" fill="#E58BA0"/>'
        elif sweets == 'one':
            inner += '<path d="M400 640 L380 600 L510 600 L530 640" fill="#F3B6C4"/>'
            inner += '<g fill="#FBF5E9" stroke-width="2.5"><circle cx="464" cy="652" r="10"/></g>'
            inner += '<rect x="400" y="660" width="130" height="38" rx="6" fill="#E58BA0"/>'
        else:
            inner += '<path d="M400 640 L380 600 L510 600 L530 640" fill="#F3B6C4"/>'
            inner += '<path d="M416 656 Q466 664 514 656" fill="none" stroke="#E3C27A" stroke-width="4"/>'
        inner += '</g>'
        inner = tint(inner, (1 - L) * 0.5, 0.0)
        out += inner
        out += f'<text x="465" y="688" text-anchor="middle" font-family="Hind Siliguri" font-weight="700" font-size="20" fill="#7A1F1F" opacity="{min(1, L):.2f}">মিষ্টি</text>'
    # door: hinged at right edge, swings toward camera. closed covers interior.
    w = lerp(230, 70, open_)
    x0 = 594 - w if open_ < 0.5 else 594
    door = S
    if open_ < 0.5:
        door += f'<rect x="{594 - w:.1f}" y="250" width="{w:.1f}" height="570" rx="16" fill="#1F7A78"/>'
        door += f'<rect x="{max(600 - w, 594 - w + 14):.1f}" y="300" width="8" height="160" rx="3" fill="#C9D1D6" stroke-width="2"/>'
        door += f'<path d="M{594 - w:.1f} 470 L594 470" stroke-width="3"/>'
    else:
        ww = lerp(0, 90, (open_ - 0.5) * 2)
        door += f'<path d="M594 250 L{594 + ww:.1f} {230 - ww * 0.2:.1f} L{594 + ww:.1f} {840 + ww * 0.2:.1f} L594 820Z" fill="#14514F"/>'
    door += '</g>'
    out += tint(door, night)
    # spill light
    spill = ''
    if open_ > 0.02:
        a = clamp(open_ * 1.2) * light
        spill += f'<path d="M372 262 L578 262 L578 808 L640 1000 L-120 1000 L372 808Z" fill="#FFC94A" opacity="{0.22 * a:.2f}"/>'
        spill += f'<ellipse cx="300" cy="900" rx="320" ry="90" fill="#FFC94A" opacity="{0.18 * a:.2f}"/>'
    return out, spill


def dust(t, x0, y0, x1, y1, n=14, amt=1.0, seed=1):
    s = ''
    for i in range(n):
        r = (math.sin(i * 12.9898 + seed) * 43758.5453) % 1
        r2 = (math.sin(i * 78.233 + seed) * 12345.6789) % 1
        x = x0 + (x1 - x0) * ((r + t * 0.02 * (1 + r2)) % 1)
        y = y0 + (y1 - y0) * ((r2 + t * 0.03 * (0.5 + r)) % 1)
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.5 + 1.5 * r:.1f}" fill="#FFF3C4" opacity="{amt * (0.35 + 0.4 * r2):.2f}"/>'
    return s


# ------------------------------------------------------------------ STAIRWELL: low steps rising left->right to a roof door
SX0, SY0, SR, SH, SN = -260, 1500, 54, 36, 17        # start x/y, run, rise, number of steps
LAND_X = SX0 + SN * SR                                  # 658: landing starts
LAND_Y = SY0 - SN * SH                                  # 888: landing level
DOOR_X0, DOOR_X1 = 770, 880                             # roof door on the landing


def tread(i):
    return SY0 - (i + 1) * SH


def stair_line(x):
    """Smooth line along the nosings (for things that float above the steps)."""
    if x >= LAND_X:
        return LAND_Y
    return SY0 - (x - SX0) / SR * SH


def stair_y(x):
    i = int((x - SX0) // SR)
    if i >= SN:
        return LAND_Y
    return tread(max(i, 0))


def stairs_bg(night=0.55, door_open=1.0, t=0.0):
    s = ('<defs><pattern id="sw@" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="#B8D4C6"/>'
         '<circle cx="30" cy="30" r="3" fill="#9CBCAD"/></pattern></defs>')
    s += '<rect x="-600" y="-200" width="1800" height="2000" fill="url(#sw@)"/>'
    s += S
    s += '<rect x="20" y="900" width="70" height="90" fill="#FBF5E9"/><rect x="20" y="900" width="70" height="22" fill="#C8341F"/>'
    s += '<rect x="360" y="760" width="64" height="80" fill="#8C8C9A"/><circle cx="392" cy="792" r="14" fill="#FBF5E9"/>'
    s += '<path d="M520 -200 L520 600" stroke-width="2"/><circle cx="520" cy="620" r="16" fill="#FFC94A"/>'
    # roof door on the landing: open, showing the night sky outside
    s += f'<rect x="{DOOR_X0 - 16}" y="{LAND_Y - 250}" width="{DOOR_X1 - DOOR_X0 + 32}" height="250" fill="#D9C8A8"/>'
    s += f'<rect x="{DOOR_X0}" y="{LAND_Y - 234}" width="{DOOR_X1 - DOOR_X0}" height="234" fill="#22305F"/>'
    s += f'<path d="M{DOOR_X0 + 70} {LAND_Y - 200} A22 22 0 1 0 {DOOR_X0 + 92} {LAND_Y - 166} A17 17 0 1 1 {DOOR_X0 + 70} {LAND_Y - 200}Z" fill="#F3E6C8" stroke-width="3"/>'
    s += f'<g fill="#F3E6C8" stroke="none"><circle cx="{DOOR_X0 + 24}" cy="{LAND_Y - 180}" r="2.5"/><circle cx="{DOOR_X0 + 40}" cy="{LAND_Y - 120}" r="2"/><circle cx="{DOOR_X0 + 90}" cy="{LAND_Y - 100}" r="2.5"/></g>'
    s += f'<rect x="{DOOR_X0}" y="{LAND_Y - 234}" width="{DOOR_X1 - DOOR_X0}" height="234" fill="none"/>'
    dw = (DOOR_X1 - DOOR_X0) * (1 - 0.82 * door_open)
    s += f'<rect x="{DOOR_X1 - dw:.1f}" y="{LAND_Y - 234}" width="{dw:.1f}" height="234" fill="#6B3A1F"/>'
    s += '</g>'
    out = tint(s, night)
    out += f'<path d="M{DOOR_X0} {LAND_Y} L{DOOR_X1} {LAND_Y} L{DOOR_X1 - 40} {LAND_Y - 10} L{DOOR_X0 + 20} {LAND_Y - 10}Z" fill="#9CC7C9" opacity="0.25"/>'
    return ids(out)


def stairs_steps(night=0.5):
    s = S
    pts = f'{SX0},{SY0}'
    for i in range(SN):
        x = SX0 + i * SR
        pts += f' {x},{tread(i)} {x + SR},{tread(i)}'
    pts += f' 1300,{LAND_Y} 1300,1800 {SX0 - 200},1800 {SX0 - 200},{SY0}'
    s += f'<polygon points="{pts}" fill="#9E3B2A"/>'
    for i in range(SN):
        x = SX0 + i * SR
        s += f'<path d="M{x} {tread(i)} L{x + SR + 4} {tread(i)}" stroke="#C98B5E" stroke-width="5"/>'
    s += f'<path d="M{LAND_X} {LAND_Y} L1300 {LAND_Y}" stroke="#C98B5E" stroke-width="5"/>'
    s += '</g>'
    return tint(s, night)


RAIL_H = 150


def stairs_rail(night=0.6):
    """Hand-rail with one baluster on every step and along the landing (drawn in front of the stairs)."""
    s = S
    x0, x1 = SX0 + SR / 2, LAND_X
    y0, y1 = stair_line(x0) - RAIL_H, LAND_Y - RAIL_H
    for i in range(SN):
        x = SX0 + i * SR + SR / 2
        top = stair_line(x) - RAIL_H
        s += f'<path d="M{x:.0f} {tread(i)} L{x:.0f} {top:.0f}" stroke-width="9"/><path d="M{x:.0f} {tread(i)} L{x:.0f} {top:.0f}" stroke="#2F2A2A" stroke-width="4"/>'
    for x in range(int(LAND_X + SR / 2), DOOR_X0 - 20, SR):
        s += f'<path d="M{x} {LAND_Y} L{x} {LAND_Y - RAIL_H}" stroke-width="9"/><path d="M{x} {LAND_Y} L{x} {LAND_Y - RAIL_H}" stroke="#2F2A2A" stroke-width="4"/>'
    rail = f'M{x0 - 20:.0f} {y0 + 13:.0f} L{x1:.0f} {y1:.0f} L{DOOR_X0 - 24} {y1:.0f}'
    s += f'<path d="{rail}" fill="none" stroke-width="16"/><path d="{rail}" fill="none" stroke="#6B3A1F" stroke-width="9"/>'
    s += '</g>'
    return tint(s, night)


# ------------------------------------------------------------------ ROOFTOP (600 x 1000)
def roof_sky():
    s = '<rect x="-300" y="-300" width="1200" height="1000" fill="#22305F"/>'
    s += '<g fill="#F3E6C8">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in ((40, 60, 2.5), (150, 140, 2), (250, 40, 2.5), (520, 90, 2), (560, 300, 2), (90, 300, 2), (330, 200, 1.6))) + '</g>'
    s += '<path d="M430 120 A62 62 0 1 0 492 222 A50 50 0 1 1 430 120Z" fill="#F3E6C8" stroke="#1C1410" stroke-width="4"/>'
    return s


def roof_city():
    s = '<g fill="#2C3E8C" stroke="#1C1410" stroke-width="3">'
    blocks = ((-200, 470, 120), (-80, 430, 90), (10, 480, 110), (120, 450, 80), (200, 500, 120), (320, 440, 70), (390, 470, 130), (520, 430, 90), (610, 480, 160))
    for x, y, w in blocks:
        s += f'<rect x="{x}" y="{y}" width="{w}" height="300"/>'
    s += '</g><g fill="#FFC94A">'
    for x, y, w in blocks:
        for j in range(3):
            if (x + j * 7) % 3 != 0:
                s += f'<rect x="{x + 14 + j * 26}" y="{y + 26 + (j % 2) * 40}" width="12" height="10"/>'
    s += '</g>'
    return s


def roof_set(door=0.0, night=0.0, sari_t=0.0):
    s = S
    # stair room (chilekotha) left
    s += '<rect x="-200" y="390" width="380" height="310" fill="#B8A88E"/><rect x="-210" y="374" width="400" height="20" fill="#D9C8A8"/>'
    s += '<rect x="40" y="520" width="96" height="180" fill="#1C1410"/>'
    if door > 0:
        s += f'<rect x="44" y="524" width="88" height="176" fill="#FFC94A" opacity="{door:.2f}" stroke="none"/>'
    dw = lerp(96, 18, door)
    s += f'<rect x="40" y="520" width="{dw:.1f}" height="180" fill="#6B3A1F"/>'
    # clothesline + sari
    s += '<path d="M190 440 L190 700 M520 440 L520 700" stroke-width="5"/>'
    s += '<path d="M190 446 Q355 476 520 446" fill="none" stroke-width="2"/>'
    sw = 6 * math.sin(sari_t * 1.7)
    s += f'<path d="M232 452 L300 458 L{298 + sw:.1f} 560 L{236 + sw:.1f} 556Z" fill="#C8341F" stroke-width="3"/>'
    s += f'<path d="M380 458 L420 456 L{422 + sw * 0.6:.1f} 506 L{380 + sw * 0.6:.1f} 506Z" fill="#E3A92B" stroke-width="3"/>'
    # aerial with kite
    s += '<path d="M330 640 L330 330 M312 360 L348 360 M316 384 L344 384" stroke="#8C8C9A" stroke-width="5"/>'
    s += '<path d="M352 300 L380 330 L352 360 L324 330Z" fill="#E58BA0" stroke-width="3"/>'
    # water tanks right
    s += '<rect x="580" y="520" width="90" height="120" rx="12" fill="#3B4466"/><rect x="680" y="540" width="80" height="100" rx="12" fill="#3B4466"/>'
    s += '<path d="M580 560 L670 560 M680 576 L760 576" stroke-width="3"/>'
    # parapet + floor
    s += '<rect x="-200" y="640" width="1000" height="40" fill="#B8A88E"/>'
    s += '<rect x="-200" y="680" width="1000" height="400" fill="#6E6258"/>'
    s += '<path d="M-200 760 L800 760 M-200 860 L800 860" stroke="#5A4E46" stroke-width="2"/>'
    s += '<path d="M150 640 L160 616 L196 616 L206 640Z" fill="#B5482A"/><circle cx="170" cy="606" r="12" fill="#3E7A3A" stroke-width="2"/><circle cx="188" cy="600" r="13" fill="#3E7A3A" stroke-width="2"/>'
    s += '</g>'
    out = tint(s, night)
    if door > 0:
        out += f'<path d="M44 524 L132 524 L240 1000 L-80 1000Z" fill="#FFC94A" opacity="{0.16 * door:.2f}"/>'
    return out
