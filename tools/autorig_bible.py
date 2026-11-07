"""Build-time auto-rigger: re-runs each bible character's body code, separating arms, legs, feet and hand props.

Writes assets/rigs/<slug>.json used by rongpat.rig at run time.
"""
import sys, os, re, json, math
SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bible_source')
sys.path.insert(0, SP)
import fullbody, specs, newcast, apply
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app', 'RongpatStudio', 'engine'))
from rongpat.library import KNOWN_CHARS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app', 'RongpatStudio', 'engine', 'assets', 'rigs') + os.sep
os.makedirs(OUT, exist_ok=True)
DONE_BY_HAND = {'pupu', 'mitul', 'babai', 'jhumpa', 'anko-sir'}

CAP = {}


def cap_arm(sh, el, ha, sleeve, skin, short=False, hand=True, w=16):
    i = len(CAP['arms'])
    CAP['arms'].append(dict(sh=list(sh), el=list(el), ha=list(ha), sleeve=sleeve, short=short, hand=hand, w=w))
    return f'@@ARM{i}@@'


def cap_legs(top, feet, fill, w=38, gap=3):
    CAP['legs'].append(dict(top=top, feet=feet, fill=fill, w=w, gap=gap))
    return '@@LEGS@@'


def cap_feet(feet, kind, color='#FBF5E9', skin='#C29068', spread=24):
    CAP['feet'].append(dict(feet=feet, kind=kind, color=color, skin=skin, spread=spread))
    return '@@FEET@@'


def run(fn, sy, hip, feet, skin):
    CAP.clear()
    CAP.update(arms=[], legs=[], feet=[])
    mod = sys.modules[fn.__module__]
    saved = (mod.arm, mod.legs, mod.feet_kind)
    mod.arm, mod.legs, mod.feet_kind = cap_arm, cap_legs, cap_feet
    try:
        s = fn(sy, hip, feet, skin)
    finally:
        mod.arm, mod.legs, mod.feet_kind = saved
    return s, dict(CAP)


def split_elems(s):
    out, i = [], 0
    tok = re.compile(r'<g\b[^>]*>|</g>|<[a-zA-Z][^>]*/>|<text\b.*?</text>|@@[A-Z0-9]+@@', re.S)
    depth, start = 0, None
    for m in tok.finditer(s):
        t = m.group(0)
        if t.startswith('<g') and not t.endswith('/>'):
            if depth == 0:
                start = m.start()
            depth += 1
        elif t == '</g>':
            depth -= 1
            if depth == 0:
                out.append(s[start:m.end()])
        elif depth == 0:
            out.append(t)
    return out


def bbox(el):
    nums = []
    for attr in re.findall(r'\b(?:d|points)="([^"]*)"', el):
        v = [float(x) for x in re.findall(r'-?\d+\.?\d*', attr)]
        nums += list(zip(v[0::2], v[1::2]))
    for a, b in (('x', 'y'), ('cx', 'cy'), ('x1', 'y1'), ('x2', 'y2')):
        for mx, my in re.findall(rf'\b{a}="(-?[\d.]+)"[^>]*?\b{b}="(-?[\d.]+)"', el):
            nums.append((float(mx), float(my)))
    for mx, mw in re.findall(r'\bx="(-?[\d.]+)"[^>]*?\bwidth="([\d.]+)"', el):
        pass
    if not nums:
        return None
    xs, ys = [p[0] for p in nums], [p[1] for p in nums]
    w = re.search(r'\bwidth="([\d.]+)"', el)
    h = re.search(r'\bheight="([\d.]+)"', el)
    x1, y1 = max(xs) + (float(w.group(1)) if w else 0), max(ys) + (float(h.group(1)) if h else 0)
    return (min(xs), min(ys), x1, y1)


def specs_list():
    out = []
    for aria, d in list(apply.SPEC.items()):
        name = aria.rstrip(':')
        slug = KNOWN_CHARS.get(name)
        P = d['P']
        if not slug or slug in DONE_BY_HAND or 'body' not in P:
            continue
        out.append((slug, P['body'], d['chin'], d['skin'], P.get('kid', False), P.get('tall', 0), P.get('behind', ''), P.get('front', '')))
    hd = newcast.heads()
    names = {'anko': 'anko-sir', 'mitali': 'mitali', 'jogen': 'ghonta-da', 'robin': 'robin', 'montu': 'montu', 'kashem': 'kashem', 'bablu': 'bablu',
             'pintu': 'pintu', 'ruksana': 'dr-ruksana', 'shefali': 'shefali', 'gopal': 'gopal', 'haridas': 'haridas'}
    for k, fn in newcast.BODIES.items():
        slug = names[k]
        if slug in DONE_BY_HAND:
            continue
        out.append((slug, fn, hd[k][1], newcast.SKINS[k], False, 0, '', ''))
    return out


def build(slug, fn, chin, skin, kid, tall, behind, front):
    sy = chin + 12
    feet = sy + (300 if kid else 440 + tall)
    hip = sy + (130 if kid else 190)
    s, cap = run(fn, sy, hip, feet, skin)
    els = split_elems(s)
    arms = cap['arms']
    for a in arms:
        a['side'] = 'l' if a['sh'][0] < 196 else 'r'
    # hand props: small elements near a hand
    props = {'l': [], 'r': []}
    keep = []
    for idx, el in enumerate(els):
        if el.startswith('@@'):
            keep.append(el)
            continue
        bb = bbox(el)
        hit = None
        if bb and arms:
            w, h = bb[2] - bb[0], bb[3] - bb[1]
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
            best = None
            for a in arms:
                if not a['hand']:
                    continue
                hx, hy = a['ha']
                near = (bb[0] - 24 <= hx <= bb[2] + 24 and bb[1] - 24 <= hy <= bb[3] + 24) or math.hypot(cx - hx, cy - hy) < 50
                crosses_mid = bb[0] < 196 < bb[2] and w > 70
                garment = ('url(#' in el and max(w, h) > 90) or el.count('<path') > 6
                if near and max(w, h) < 175 and not crosses_mid and not garment:
                    d = math.hypot(cx - hx, cy - hy)
                    if best is None or d < best[0]:
                        best = (d, a)
            if best:
                hit = best[1]
        if hit:
            props[hit['side']].append(el)
        else:
            keep.append(el)
    torso = ''.join(e for e in keep if not e.startswith('@@'))
    # rest angles for props
    prop_out = {}
    for side, lst in props.items():
        if not lst:
            continue
        a = next(a for a in arms if a['side'] == side)
        ang = math.degrees(math.atan2(a['ha'][1] - a['el'][1], a['ha'][0] - a['el'][0])) - 90
        prop_out[side] = dict(svg=''.join(lst), hand=a['ha'], rest_angle=ang)
    legs = cap['legs'][0] if cap['legs'] else None
    footinfo = cap['feet'][0] if cap['feet'] else None
    static_legs = ''
    if not legs:
        # legs are part of the garment: keep the feet drawn statically
        if footinfo:
            static_legs = fullbody.feet_kind(**footinfo)
        footinfo_dyn = None
    else:
        footinfo_dyn = footinfo
    def ns(x):
        return re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{slug}--{m.group(1)})', x)
    torso = ns(torso)
    behind, front = ns(behind), ns(front)
    for v in prop_out.values():
        v['svg'] = ns(v['svg'])
    static_legs = ns(static_legs)
    rig = dict(slug=slug, chin=chin, skin=skin, sy=sy, hip=hip, feet=feet, kid=kid, arms=arms, legs=legs, foot=footinfo_dyn,
               static_feet=static_legs, torso=torso, behind=behind, front=front, props=prop_out)
    json.dump(rig, open(OUT + slug + '.json', 'w'), ensure_ascii=False)
    return rig


if __name__ == '__main__':
    done = []
    for item in specs_list():
        r = build(*item)
        done.append((r['slug'], len(r['arms']), bool(r['legs']), {k: len(v['svg']) for k, v in r['props'].items()}))
    for d in done:
        print(d)
