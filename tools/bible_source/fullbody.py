"""Rebuild bible character art as full-body figures with short necks."""
import re, sys

SC = 0.74          # shared figure scale (all humans the same scale)
VB_H = 640
INK = '#1C1410'


def T(x):
    return f'{x:.1f}'


# ---------------------------------------------------------------- body parts (head coordinate space)
def neck(chin, skin, w=28):
    return f'<path d="M{196 - w / 2} {chin - 18} L{196 - w / 2} {chin + 16} Q196 {chin + 22} {196 + w / 2} {chin + 16} L{196 + w / 2} {chin - 18}Z" fill="{skin}"/>'


def arm(sh, el, ha, sleeve, skin, short=False, hand=True, w=16):
    (x0, y0), (x1, y1), (x2, y2) = sh, el, ha
    s = f'<path d="M{x0} {y0} L{x1} {y1} L{x2} {y2}" fill="none" stroke="{INK}" stroke-width="{w + 8}"/>'
    if short:
        s += f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{skin}" stroke-width="{w}"/>'
        s += f'<path d="M{x0} {y0} L{x1} {y1}" fill="none" stroke="{sleeve}" stroke-width="{w + 2}"/>'
    else:
        s += f'<path d="M{x0} {y0} L{x1} {y1} L{x2} {y2}" fill="none" stroke="{sleeve}" stroke-width="{w}"/>'
    if hand:
        s += f'<circle cx="{x2}" cy="{y2 + 4}" r="11" fill="{skin}"/>'
    return s


def tunic(sy, length, fill, flare=8, half=60, belly=0):
    L = sy + length
    return (f'<path d="M{196 - half + 6} {sy} Q196 {sy - 8} {196 + half - 6} {sy} Q{196 + half + 8} {sy + 12} {196 + half + 4} {sy + 52} '
            f'Q{196 + half + 8 + belly} {sy + length * 0.55} {196 + half + flare} {L} Q196 {L + 8} {196 - half - flare} {L} '
            f'Q{196 - half - 8 - belly} {sy + length * 0.55} {196 - half - 4} {sy + 52} Q{196 - half - 8} {sy + 12} {196 - half + 6} {sy}Z" fill="{fill}"/>')


def legs(top, feet, fill, w=38, gap=3):
    a = 196 - gap
    b = 196 + gap
    return (f'<path d="M{a - w} {top} L{a - w + 4} {feet - 6} L{a - 2} {feet - 6} L{a} {top}Z" fill="{fill}"/>'
            f'<path d="M{b} {top} L{b + 2} {feet - 6} L{b + w - 4} {feet - 6} L{b + w} {top}Z" fill="{fill}"/>')


def shorts(top, bottom, fill, w=42):
    return (f'<path d="M{196 - w - 4} {top} L{196 - w - 8} {bottom} L{194} {bottom} L196 {top + 20} L198 {bottom} '
            f'L{196 + w + 8} {bottom} L{196 + w + 4} {top}Z" fill="{fill}"/>')


def lungi(top, feet, fill, half=58):
    return (f'<path d="M{196 - half} {top} L{196 + half} {top} L{196 + half + 6} {feet - 18} L{196 - half - 6} {feet - 18}Z" fill="{fill}"/>'
            f'<path d="M{196 + 10} {top + 4} L{196 + 22} {feet - 20}" fill="none" stroke-width="2.5"/>')


def sari_skirt(top, feet, fill, border, half=56, flare=26):
    s = (f'<path d="M{196 - half} {top} Q{196 - half - 8} {(top + feet) / 2} {196 - half - flare} {feet - 4} '
         f'L{196 + half + flare} {feet - 4} Q{196 + half + 8} {(top + feet) / 2} {196 + half} {top}Z" fill="{fill}"/>')
    s += (f'<path d="M{196 - half - flare + 4} {feet - 30} L{196 + half + flare - 4} {feet - 30} L{196 + half + flare} {feet - 4} '
          f'L{196 - half - flare} {feet - 4}Z" fill="{border}"/>')
    for dx in (-6, 6, 18):
        s += f'<path d="M{196 + dx} {top + 30} L{196 + dx * 1.6} {feet - 32}" fill="none" stroke-width="2.5"/>'
    return s


def aanchal(sy, fill, border=None):
    s = f'<path d="M{196 + 66} {sy + 168} L{196 + 36} {sy + 186} L{196 - 70} {sy + 14} L{196 - 40} {sy - 4}Z" fill="{fill}"/>'
    if border:
        s += f'<path d="M{196 + 66} {sy + 168} L{196 + 56} {sy + 175} L{196 - 52} {sy + 2} L{196 - 40} {sy - 4}Z" fill="{border}"/>'
    return s


def feet_kind(feet, kind, color='#FBF5E9', skin='#C29068', spread=24):
    xl, xr = 196 - spread, 196 + spread
    s = ''
    for x, d in ((xl, -1), (xr, 1)):
        if kind == 'sneaker':
            s += (f'<path d="M{x - 22 * (d > 0) - 6 * (d < 0) - 16} {feet + 4} Q{x - 20} {feet - 16} {x} {feet - 14} Q{x + 22} {feet - 10} {x + 24} {feet + 4}Z" fill="{color}"/>'
                  f'<path d="M{x - 26} {feet + 4} L{x + 24} {feet + 4}" stroke-width="6"/>')
        elif kind == 'shoe':
            s += f'<path d="M{x - 22} {feet + 4} Q{x - 20} {feet - 14} {x} {feet - 12} Q{x + 24} {feet - 8} {x + 26} {feet + 4}Z" fill="{color}"/>'
        elif kind == 'boot':
            s += f'<path d="M{x - 18} {feet + 4} L{x - 16} {feet - 34} L{x + 14} {feet - 34} L{x + 14} {feet - 12} Q{x + 26} {feet - 8} {x + 26} {feet + 4}Z" fill="{color}"/>'
        elif kind == 'nagra':
            s += f'<path d="M{x - 22} {feet + 4} Q{x - 20} {feet - 12} {x} {feet - 12} Q{x + 22} {feet - 10} {x + 34} {feet - 10} Q{x + 26} {feet + 2} {x + 22} {feet + 4}Z" fill="{color}"/>'
        else:  # chappal / bare
            s += f'<ellipse cx="{x + 2 * d}" cy="{feet - 2}" rx="22" ry="10" fill="{skin}"/>'
            if kind == 'chappal':
                s += f'<path d="M{x - 24} {feet + 6} L{x + 26} {feet + 6}" stroke="{color}" stroke-width="6"/><path d="M{x - 8} {feet - 8} L{x + 8} {feet + 2}" stroke="{color}" stroke-width="4"/>'
    return s


# ---------------------------------------------------------------- per-character specs
def build(name, chin, skin, P):
    sy = chin + 12
    kid = P.get('kid', False)
    tall = P.get('tall', 0)
    feet = sy + (300 if kid else 440 + tall)
    hip = sy + (130 if kid else 190)
    s = ''
    s += P.get('behind', '')
    b = P['body']
    s += neck(chin, skin, 24 if kid else 28)
    s += b(sy, hip, feet, skin)
    return s, feet


def card(name, src_svg, chin, skin, P, removes=(), bg='#F3E6C8', disc='#1F7A78', label=None):
    m = re.match(r'<svg class="art"[^>]*aria-label="([^"]*)"[^>]*>(.*)</svg>', src_svg, re.S)
    aria, inner = m.group(1), m.group(2)
    defs = ''.join(re.findall(r'<defs>.*?</defs>', inner, re.S))
    rest = re.sub(r'<defs>.*?</defs>', '', inner, flags=re.S)
    rest = re.sub(r'<rect width="392" height="400"[^>]*/>', '', rest)
    rest = re.sub(r'<circle cx="196" cy="190" r="150"[^>]*/>', '', rest)
    for r in removes:
        if r not in rest:
            raise SystemExit(f'{name}: remove-string not found: {r[:60]}')
        rest = rest.replace(r, '')
    if 'custom' in P:
        behind, frontc, feet = P['custom']
        body = behind
        P = dict(P, front=frontc)
    else:
        body, feet = build(name, chin, skin, P)
    cid = 'hc' + re.sub(r'\W', '', name)
    clip = f'<clipPath id="{cid}"><rect x="-300" y="-300" width="1000" height="{chin + 300 + P.get("clip_pad", 1)}"/></clipPath>'
    # placement: feet at y=605 in the 392x640 card; scale shared
    sc = P.get('scale', SC)
    ty = 605 - feet * sc
    tx = 196 - 196 * sc
    front = P.get('front', '')
    g = (f'<g transform="translate({T(tx)},{T(ty)}) scale({sc})">'
         f'<g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{body}</g>'
         f'<g clip-path="url(#{cid})">{rest}</g>'
         f'<g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{front}</g></g>')
    top_y = max(20, ty + 40 * SC)
    backdrop = (f'<rect width="392" height="{VB_H}" fill="{bg}"/>'
                f'<path d="M46 {VB_H} L46 210 A150 150 0 0 1 346 210 L346 {VB_H}Z" fill="{disc}"/>'
                f'<ellipse cx="196" cy="608" rx="110" ry="14" fill="#1C1410" opacity="0.18"/>')
    a = label or aria
    return (f'<svg class="art" viewBox="0 0 392 {VB_H}" role="img" aria-label="{a}">'
            f'<defs>{clip}</defs>{defs}{backdrop}{P.get("backdrop_extra", "")}{g}</svg>')
