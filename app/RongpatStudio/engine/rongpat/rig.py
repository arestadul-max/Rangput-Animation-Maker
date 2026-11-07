"""Rigged characters: bible characters rebuilt from moving parts (head, torso, two-joint arms and legs) plus hand props.

Coordinates are the bible's head/body space (the card art space before the card transform). A pose is a dict of
hand and foot targets; arms and legs bend with simple two-bone IK, elbows and knees pointing outward.
"""
import math, re

INK = '#1C1410'
CONCH = '#FBF5E9'


def _head_from_card(card_svg):
    """Pull the head group (clip-path group) and all defs out of a bible card file."""
    i = card_svg.index('<g clip-path=')
    d, j = 0, i
    for m in re.finditer(r'<g\b|</g>', card_svg[i:]):
        d += 1 if m.group(0) == '<g' else -1
        if d == 0:
            j = i + m.end()
            break
    defs = ''.join(re.findall(r'<defs>.*?</defs>', card_svg, re.S))
    return defs, card_svg[i:j]


def ik(S, T, L1, L2, out):
    """Two-bone IK: returns (elbow, hand). out = -1 bends the joint toward -x, +1 toward +x."""
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = math.hypot(dx, dy)
    d = max(abs(L1 - L2) + 1, min(L1 + L2 - 0.5, d))
    a = math.atan2(dy, dx)
    c = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
    th = math.acos(max(-1, min(1, c)))
    e1 = (S[0] + L1 * math.cos(a + th), S[1] + L1 * math.sin(a + th))
    e2 = (S[0] + L1 * math.cos(a - th), S[1] + L1 * math.sin(a - th))
    E = e1 if (e1[0] - e2[0]) * out > 0 else e2
    H = (S[0] + d * math.cos(a), S[1] + d * math.sin(a))
    return E, H


def P(p):
    return f'{p[0]:.1f} {p[1]:.1f}'


def limb(a, b, c, color, w, low=None, low_frac=0.45):
    s = f'<path d="M{P(a)} L{P(b)} L{P(c)}" fill="none" stroke="{INK}" stroke-width="{w + 8}"/>'
    s += f'<path d="M{P(a)} L{P(b)} L{P(c)}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    if low:
        k = (c[0] + (b[0] - c[0]) * low_frac, c[1] + (b[1] - c[1]) * low_frac)
        s += f'<path d="M{P(k)} L{P(c)}" fill="none" stroke="{INK}" stroke-width="{w + 8}"/><path d="M{P(k)} L{P(c)}" fill="none" stroke="{low}" stroke-width="{w}"/>'
    return s


# ------------------------------------------------------------------ props held in a hand (origin = grip, pointing down at 0 deg)
def bat_svg():
    return ('<rect x="-6" y="-34" width="12" height="46" rx="4" fill="#8A3B12"/>'
            '<path d="M-18 10 L18 10 L17 178 Q0 190 -17 178Z" fill="#E3C27A"/><path d="M0 22 L0 168" stroke="#C49A4A" stroke-width="3"/>')


def ball_svg(r=13):
    return (f'<circle cx="0" cy="0" r="{r}" fill="#B5282A"/>'
            f'<path d="M{-r * 0.55:.1f} {-r * 0.8:.1f} Q{-r * 0.15:.1f} 0 {-r * 0.55:.1f} {r * 0.8:.1f} M{r * 0.55:.1f} {-r * 0.8:.1f} Q{r * 0.15:.1f} 0 {r * 0.55:.1f} {r * 0.8:.1f}" fill="none" stroke="{CONCH}" stroke-width="1.6"/>')


def cone_svg():
    return ('<path d="M-30 -12 L30 -12 L0 50Z" fill="#F3E6C8"/><path d="M-22 0 L20 0 M-14 14 L14 14" stroke="#8C8C9A" stroke-width="2"/>'
            '<path d="M-34 -10 Q-26 -30 -10 -24 Q0 -38 14 -26 Q28 -32 34 -10Z" fill="#F3D9A0"/>')


def ruler_svg():
    ticks = ''.join(f'<path d="M-6 {20 + k * 20} L2 {20 + k * 20}" stroke-width="2"/>' for k in range(9))
    return f'<rect x="-8" y="-20" width="16" height="210" fill="#E3A92B"/>{ticks}'


def chalk_svg():
    return f'<rect x="-10" y="-4" width="20" height="8" rx="2" fill="{CONCH}" stroke-width="2.5"/>'


def magnifier_svg():
    return (f'<path d="M0 0 L0 -60" stroke="{INK}" stroke-width="14"/><path d="M0 0 L0 -60" stroke="#8A3B12" stroke-width="8"/>'
            f'<circle cx="0" cy="-100" r="40" fill="#DCEFF4" opacity="0.55"/><circle cx="0" cy="-100" r="40" fill="none" stroke="#E3A92B" stroke-width="7"/>'
            f'<circle cx="0" cy="-100" r="45" fill="none" stroke-width="3"/>')


PROPS = {'bat': bat_svg, 'ball': ball_svg, 'cone': cone_svg, 'ruler': ruler_svg, 'chalk': chalk_svg, 'magnifier': magnifier_svg}


def prop_at(name, hand, angle):
    return f'<g transform="translate({P(hand).replace(" ", ",")}) rotate({angle:.1f})"><g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{PROPS[name]()}</g></g>'


# ------------------------------------------------------------------ rig specs
def _kid(slug, skin, chin, sleeve, legs, socks, shoe, shorts, torso, behind='', front='', shoulders=(148, 244), props=None,
         head_strip=(), head_add='', eyes=None, mouth=None, arm_w=16):
    sy = chin + 12
    return dict(slug=slug, skin=skin, chin=chin, sy=sy, hip=sy + 130, feet=sy + 300, sleeve=sleeve, short=True,
                legcol=legs, socks=socks, shoe=shoe, lower=shorts, torso=torso, behind=behind, front=front,
                sh=((shoulders[0], sy + 14), (shoulders[1], sy + 14)), L1=66, L2=64, arm_w=arm_w,
                hipx=(180, 212), props=props or {}, head_strip=head_strip, head_add=head_add, eyes=eyes, mouth=mouth)


def _shorts(top, bottom, fill, w):
    return (f'<path d="M{196 - w - 4} {top} L{196 - w - 8} {bottom} L194 {bottom} L196 {top + 20} L198 {bottom} '
            f'L{196 + w + 8} {bottom} L{196 + w + 4} {top}Z" fill="{fill}"/>')


def _tunic(sy, length, fill, flare=8, half=60, belly=0):
    L = sy + length
    return (f'<path d="M{196 - half + 6} {sy} Q196 {sy - 8} {196 + half - 6} {sy} Q{196 + half + 8} {sy + 12} {196 + half + 4} {sy + 52} '
            f'Q{196 + half + 8 + belly} {sy + length * 0.55} {196 + half + flare} {L} Q196 {L + 8} {196 - half - flare} {L} '
            f'Q{196 - half - 8 - belly} {sy + length * 0.55} {196 - half - 4} {sy + 52} Q{196 - half - 8} {sy + 12} {196 - half + 6} {sy}Z" fill="{fill}"/>')


def specs():
    S = {}
    sy = 254
    S['pupu'] = _kid('pupu', '#C48A5A', 242, '#1F7A78', '#C48A5A', CONCH, '#C8341F', _shorts(sy + 110, sy + 182, '#B59A62', 38),
                     _tunic(sy, 140, 'url(#pupu--h1-dots)', flare=2, half=52)
                     + f'<path d="M156 {sy + 2} L150 {sy + 120} M236 {sy + 2} L242 {sy + 120}" stroke-width="18"/><path d="M156 {sy + 2} L150 {sy + 120} M236 {sy + 2} L242 {sy + 120}" stroke="#2C3E8C" stroke-width="10"/>',
                     behind=f'<rect x="124" y="{sy + 8}" width="144" height="150" rx="16" fill="#2C3E8C"/>')
    sy = 252
    S['mitul'] = _kid('mitul', '#B07548', 240, '#E3A92B', '#B07548', CONCH, CONCH, _shorts(sy + 110, sy + 182, '#2C3E8C', 38),
                      _tunic(sy, 140, 'url(#mitul--k-stripe)', flare=2, half=52))
    sy = 260
    S['babai'] = _kid('babai', '#C48A5A', 248, '#E07A2E', '#C48A5A', None, '#2C3E8C', _shorts(sy + 110, sy + 182, '#6B5A3A', 44),
                      _tunic(sy, 146, 'url(#babai--k-tri)', flare=4, half=60, belly=18), shoulders=(140, 252))
    sy = 254
    lens = [r'<path d="M252 204 L298 268" stroke-width="16"/><path d="M252 204 L298 268" stroke="#8A3B12" stroke-width="9"/>',
            r'<circle cx="228" cy="178" r="42" fill="#DCEFF4"/>', r'<path d="M196 178 Q228 144 260 178 Q228 200 196 178Z" fill="#FBF5E9" stroke-width="4"/>',
            r'<circle cx="228" cy="176" r="15" fill="#1C1410" stroke="none"/>', r'<path d="M190 176 Q228 136 266 176" fill="none" stroke-width="8"/>',
            r'<circle cx="228" cy="178" r="42" fill="none" stroke="#E3A92B" stroke-width="7"/>', r'<circle cx="228" cy="178" r="47" fill="none" stroke-width="3"/>',
            r'<circle cx="233" cy="170" r="4.5" fill="#FBF5E9"/>']
    S['jhumpa'] = _kid('jhumpa', '#A86F48', 242, '#2C3E8C', '#A86F48', None, '#E3A92B', '',
                       _tunic(sy, 200, 'url(#jhumpa--k-star)', flare=22, half=50) + f'<path d="M160 {sy} Q196 {sy + 28} 232 {sy}" fill="none" stroke="#FBF5E9" stroke-width="6"/>',
                       shoulders=(146, 246), head_strip=lens,
                       head_add=('<g stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
                                 '<path d="M210 178 Q224 166 238 178 Q224 186 210 178Z" fill="#FBF5E9" stroke-width="3"/><circle cx="226" cy="177" r="5.5" fill="#1C1410" stroke="none"/>'
                                 '<path d="M206 176 Q224 162 242 176" fill="none" stroke-width="5"/><path d="M210 160 Q224 150 240 158" fill="none" stroke-width="5"/></g>'
                                 '<circle cx="228" cy="175" r="1.8" fill="#FBF5E9"/>'),
                       eyes=[(154, 182, 178, 166), (210, 238, 178, 166)], mouth=(192, 226))
    # Anko Sir (adult)
    sy = 250
    S['anko-sir'] = dict(slug='anko-sir', skin='#C29068', chin=238, sy=sy, hip=sy + 190, feet=sy + 440, sleeve=CONCH, short=False,
                         legcol=CONCH, socks=None, shoe=INK, lower='', torso=_tunic(sy, 262, 'url(#anko-sir--n-math)', flare=10)
                         + f'<path d="M196 {sy + 6} L196 {sy + 96}" stroke-width="3"/>'
                         + ''.join(f'<circle cx="196" cy="{sy + 30 + k * 24}" r="3" fill="#1C1410" stroke="none"/>' for k in range(3))
                         + f'<path d="M224 {sy + 56} L226 {sy + 30}" stroke-width="9"/><path d="M224 {sy + 56} L226 {sy + 30}" stroke="#C8341F" stroke-width="4"/>'
                         + f'<rect x="212" y="{sy + 52}" width="32" height="32" fill="{CONCH}" stroke-width="3"/>',
                         behind='', front='', sh=((140, sy + 14), (252, sy + 14)), L1=80, L2=76, arm_w=16, hipx=(176, 216),
                         props={}, head_strip=(), head_add='', eyes=None, mouth=None, adult=True)
    return S


RIGS = specs()
DEFAULT_PROPS = {'babai': {'l': 'cone'}, 'jhumpa': {'r': 'magnifier'}, 'anko-sir': {'l': 'ruler', 'r': 'chalk'}}


# ------------------------------------------------------------------ poses
def _idle(R, t):
    (lx, ly), (rx, ry) = R['sh']
    L = R['L1'] + R['L2']
    sw = 3 * math.sin(t * 1.7)
    return dict(lh=(lx - 14 + sw, ly + L - 10), rh=(rx + 14 - sw, ry + L - 10), lf=None, rf=None, dy=1.5 * math.sin(t * 2.0), lean=0.0,
                head=1.5 * math.sin(t * 0.9), lp=0.0, rp=0.0)


def _mix(a, b, w):
    out = dict(a)
    for k, v in b.items():
        if k not in a or a[k] is None or v is None:
            out[k] = v if w > 0.5 else a.get(k)
        elif isinstance(v, tuple) and isinstance(v[0], str):
            out[k] = (v[0], a[k][1] + (v[1] - a[k][1]) * w) if a[k][0] == v[0] else (v if w > 0.5 else a[k])
        elif isinstance(v, tuple):
            out[k] = tuple(x + (y - x) * w for x, y in zip(a[k], v))
        elif isinstance(v, (int, float)):
            out[k] = a[k] + (v - a[k]) * w
        else:
            out[k] = v if w > 0.5 else a[k]
    return out


def _ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# each pose function: (R, u seconds since start, t absolute) -> partial pose dict. Durations: None = held until another pose.
def p_bat_ready(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(lh=(rx - 10, ly + 96), rh=(rx + 2, ly + 104), bat=('r', 200 + 4 * math.sin(t * 3)), dy=10, lean=-4, head=-4)


def p_swing(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    cx, cy = (lx + rx) / 2, ly + 30
    k = _ease(u / 0.38)
    ang = -40 + 260 * k      # degrees around the chest: from back-up to across-up
    rr = R['L1'] + R['L2'] - 20
    hx, hy = cx + rr * math.cos(math.radians(ang + 90)) * 0.9, cy + rr * math.sin(math.radians(ang + 90)) * 0.55
    return dict(lh=(hx - 6, hy), rh=(hx + 6, hy + 4), bat=('r', 160 - 300 * k), dy=8 - 10 * k, lean=-8 + 18 * k, head=-6 + 10 * k)


def p_bowl(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    k = _ease(u / 0.55)
    ang = math.radians(90 + 360 * k)            # windmill from straight down, over the top
    L = R['L1'] + R['L2'] - 4
    return dict(rh=(rx + L * math.cos(ang) * 0.6, ry + L * math.sin(ang)), lh=(lx - 40, ly + 40 - 30 * math.sin(k * math.pi)),
                lean=10 * math.sin(k * math.pi), head=6 * math.sin(k * math.pi), dy=-6 * math.sin(k * math.pi))


def p_catch(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    c = (lx + rx) / 2
    k = _ease(u / 0.2)
    return dict(lh=(rx + 8, ly - 62 * k + 20), rh=(rx + 40, ly - 58 * k + 20), head=8 * k, dy=-4)


def p_cheer(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    w = 14 * math.sin(u * 9)
    return dict(lh=(lx - 74 + w, ly - 92), rh=(rx + 74 - w, ly - 92), head=4 * math.sin(u * 6), dy=-3 * abs(math.sin(u * 6)))


def p_six(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(lh=(lx - 26, ly - 124), rh=(rx + 26, ly - 124), head=0)


def p_out(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(rx + 26, ry - 124), head=-3)


def p_point(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(rx + R['L1'] + R['L2'] - 6, ry + 6), head=6)


def p_point_left(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(lh=(lx - R['L1'] - R['L2'] + 6, ly + 6), head=-6)


def p_clap(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    c = (lx + rx) / 2
    g = 8 + 26 * abs(math.sin(u * 8))
    return dict(lh=(c - g, ly + 60), rh=(c + g, ly + 60))


def p_shrug(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(lh=(lx - 60, ly + 60), rh=(rx + 60, ry + 60), dy=-6, head=8)


def p_facepalm(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(214, R['chin'] - 40), head=10, lean=4)


def p_hips(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(lh=(lx - 8, R['hip'] - 6), rh=(rx + 8, R['hip'] - 6), head=-3)


def p_scared(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    j = 3 * math.sin(u * 50)
    return dict(lh=(lx + 10 + j, R['chin'] - 20), rh=(rx - 10 - j, R['chin'] - 20), dy=6, head=-6 + j)


def p_wave(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(rx + 50 + 20 * math.sin(u * 10), ry - 80), head=5)


def p_think(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(206, R['chin'] + 6), lh=(rx - 20, ly + 70), head=-10)


def p_eat(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    k = abs(math.sin(u * 3.2))
    return dict(lh=(lx + 20, ly + 70), rh=(rx - 20 - 30 * k, ry + 60 - 90 * k))


def p_magnify(R, u, t):
    return dict(rh=(232, R['sy'] + 120), head=-4)


def p_carry_bat(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(rx + 10, ry + 70), bat=('r', 160))


def p_hold_ball(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(rh=(rx + 18, ry + 80), ball=True)


def p_dance(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    a = math.sin(u * 6)
    return dict(lh=(lx - 40, ly - 60 * a + 10), rh=(rx + 40, ry + 60 * a - 30), lean=8 * a, dy=-6 * abs(a), head=6 * a)


def p_crouch(R, u, t):
    (lx, ly), (rx, ry) = R['sh']
    return dict(lh=(lx + 6, ly + 90), rh=(rx - 6, ry + 90), dy=26, lean=0)


POSES = {
    'bat-ready': (p_bat_ready, None, 'Batting stance with the bat.'), 'swing': (p_swing, 0.6, 'Swings the bat (then back to the stance).'),
    'bowl': (p_bowl, 0.7, 'Bowls: arm windmills over the top.'), 'throw': (p_bowl, 0.6, 'Throws.'),
    'catch': (p_catch, None, 'Both hands up above the head to catch.'), 'cheer': (p_cheer, 2.0, 'Arms up, waving.'),
    'six': (p_six, None, 'Umpire signal: both arms straight up.'), 'out': (p_out, None, 'Umpire signal: one finger up.'),
    'point': (p_point, 1.6, 'Points to the right.'), 'point-left': (p_point_left, 1.6, 'Points to the left.'),
    'clap': (p_clap, 1.4, 'Claps.'), 'shrug': (p_shrug, 1.2, 'Shrugs.'), 'facepalm': (p_facepalm, 1.6, 'Hand on face.'),
    'hands-on-hips': (p_hips, None, 'Hands on hips (strict).'), 'cover-face': (p_scared, 1.5, 'Hands up to the face in fright.'),
    'wave': (p_wave, 1.5, 'Waves.'), 'think': (p_think, None, 'Hand on chin.'), 'eat': (p_eat, None, 'Keeps eating from the hand.'),
    'magnify': (p_magnify, None, 'Jhumpa: magnifying glass up to her eye.'), 'carry-bat': (p_carry_bat, None, 'Holds a bat at the side.'),
    'hold-ball': (p_hold_ball, None, 'Holds the ball up.'), 'arm-dance': (p_dance, None, 'Dances with the arms.'),
    'keeper': (p_crouch, None, 'Crouches like a wicketkeeper.'), 'relax': (None, None, 'Back to standing normally.'),
}


def pose_at(R, slug, acts, t, moving=None, talk=0.0):
    """acts: list of (name, start) for pose actions, sorted. Returns final pose dict."""
    base = idle_auto(R, t) if R.get('auto') else _idle(R, t)
    hold = None
    cur = None
    for name, st in acts:
        if st > t:
            break
        fn, dur, _ = POSES[name]
        if dur is None:
            hold = (name, st)
            cur = None
        elif t - st < dur:
            cur = (name, st)
        if name == 'relax':
            hold = None
    pose = base
    if hold and POSES[hold[0]][0]:
        w = _ease((t - hold[1]) / 0.25)
        pose = _mix(pose, POSES[hold[0]][0](R, t - hold[1], t), w)
    if cur:
        fn, dur, _ = POSES[cur[0]]
        u = t - cur[1]
        w = _ease(u / 0.12) * _ease((dur - u) / 0.15)
        pose = _mix(pose, fn(R, u, t), w)
    if talk > 0.1 and not cur and not (hold and hold[0] not in ('hands-on-hips', 'keeper')):
        (rx, ry) = R['sh'][1]
        g = 0.5 + 0.5 * math.sin(t * 4.2)
        pose = _mix(pose, dict(rh=(rx + 40 + 16 * g, ry + 50 - 40 * g)), 0.8)
        pose['head'] = pose.get('head', 0) + 3 * math.sin(t * 7) * talk
    if moving:
        run, ph = moving
        sw = math.sin(ph * math.pi * 2)
        (lx, ly), (rx, ry) = R['sh']
        L = R['L1'] + R['L2']
        if not cur and not hold and not R.get('props'):
            pose['lh'] = (lx - 20, ly + L - 30 + (22 if run else 14) * sw)
            pose['rh'] = (rx + 20, ry + L - 30 - (22 if run else 14) * sw)
        lift = 22 if run else 14
        pose['lf_lift'] = max(0, sw) * lift
        pose['rf_lift'] = max(0, -sw) * lift
        pose['lean'] = pose.get('lean', 0) + (6 if run else 0)
    return pose


def draw(R, head_defs, head_svg, pose, props, blink=0.0, talk=0.0, face=None):
    """Returns (svg in body space, hand points dict)."""
    sy, hip, feet = R['sy'], R['hip'], R['feet']
    dy = pose.get('dy', 0.0)
    lean = pose.get('lean', 0.0)
    hx0, hx1 = R['hipx']
    LT = (feet - 6 - (hip + 34)) / 2 + 3
    out = ''
    # legs (IK from hip to foot, knees bend outward)
    legs = ''
    for side, hx, lift_k, sgn in (('l', hx0, 'lf_lift', -1), ('r', hx1, 'rf_lift', 1)):
        Hj = (hx, hip + 34 + dy)
        lift = pose.get(lift_k, 0.0)
        F = (hx - sgn * lift * 0.25, feet - 6 - lift)
        K, F2 = ik(Hj, F, LT, LT, sgn)
        legs += limb(Hj, K, F2, R['legcol'], 22, R['socks'], 0.55)
        shoe = R['shoe']
        legs += f'<ellipse cx="{F2[0] + sgn * 4:.1f}" cy="{F2[1] + 4:.1f}" rx="20" ry="10" fill="{shoe}"/>'
    # upper body group, leaning around the hip centre and moved by dy
    up_tf = f'translate(0,{dy:.1f}) rotate({lean:.1f} 196 {hip:.1f})'
    torso = R['torso']
    head = f'<g transform="rotate({pose.get("head", 0):.1f} 196 {R["chin"]:.1f})">{_head(R, head_svg, blink, talk, face)}</g>'
    arms, hands, prop_layer = '', {}, ''
    (lx, ly), (rx, ry) = R['sh']
    bat = pose.get('bat')
    for side, S, key, sgn in (('l', (lx, ly), 'lh', -1), ('r', (rx, ry), 'rh', 1)):
        T = pose.get(key) or (S[0] + sgn * 14, S[1] + R['L1'] + R['L2'] - 10)
        E, Hd = ik(S, T, R['L1'], R['L2'], sgn)
        if R['short']:
            arms += f'<path d="M{P(S)} L{P(E)} L{P(Hd)}" fill="none" stroke="{INK}" stroke-width="{R["arm_w"] + 8}"/>'
            arms += f'<path d="M{P(E)} L{P(Hd)}" fill="none" stroke="{R["skin"]}" stroke-width="{R["arm_w"]}"/>'
            mid = ((S[0] + E[0]) / 2, (S[1] + E[1]) / 2)
            arms += f'<path d="M{P(S)} L{P(E)}" fill="none" stroke="{R["sleeve"]}" stroke-width="{R["arm_w"] + 2}"/>'
        else:
            arms += limb(S, E, Hd, R['sleeve'], R['arm_w'])
        hands[side] = (Hd, math.degrees(math.atan2(Hd[1] - E[1], Hd[0] - E[0])) - 90)
    hand_circles = ''
    for side in ('l', 'r'):
        Hd, ang = hands[side]
        p = props.get(side)
        if bat and bat[0] == side:
            prop_layer += prop_at('bat', Hd, bat[1])
        elif p:
            a = {'cone': 0, 'magnifier': 0, 'ruler': 168 if side == 'l' else 0, 'chalk': 0}.get(p, ang)
            prop_layer += prop_at(p, (Hd[0], Hd[1] + (14 if p == 'cone' else 0)), a)
        if pose.get('ball') and side == 'r':
            prop_layer += prop_at('ball', (Hd[0], Hd[1] - 10), 0)
        hand_circles += f'<circle cx="{Hd[0]:.1f}" cy="{Hd[1] + 4:.1f}" r="11" fill="{R["skin"]}" stroke="{INK}" stroke-width="4"/>'
    upper = (f'<g transform="{up_tf}">{R["behind"]}'
             f'<path d="M{196 - 14} {R["chin"] - 18} L{196 - 14} {R["chin"] + 16} Q196 {R["chin"] + 22} {196 + 14} {R["chin"] + 16} L{196 + 14} {R["chin"] - 18}Z" fill="{R["skin"]}"/>'
             f'{torso}{head}{arms}{prop_layer}{hand_circles}</g>')
    lower = R['lower']
    body = (f'<g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{legs}'
            f'<g transform="translate(0,{dy:.1f})">{lower}</g>{upper}</g>')
    # hand points after the upper-body transform
    out_hands = {}
    a = math.radians(lean)
    for side, (Hd, ang) in hands.items():
        x, y = Hd[0], Hd[1] + dy
        cx, cy = 196, hip + dy
        rx_ = cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a)
        ry_ = cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)
        out_hands[side] = (rx_, ry_)
    return head_defs + body, out_hands


def _head(R, head_svg, blink, talk, face):
    s = head_svg
    for pat in R.get('head_strip', ()):
        s = s.replace(pat, '')
    if R.get('head_add'):
        s = s[:s.rfind('</g>')] + R['head_add'] + '</g>'
    if isinstance(face, str):
        return s + face
    ov = ''
    if face:
        if blink > 0.5:
            for (x0, x1, y, yt) in face['eyes']:
                cx = (x0 + x1) / 2
                ov += (f'<path d="M{x0 - 3} {y + 1} Q{cx} {yt - 6} {x1 + 3} {y + 1} Q{cx} {y + 6} {x0 - 3} {y + 1}Z" fill="{face["skin"]}"/>'
                       f'<path d="M{x0 - 3} {y + 1} Q{cx} {y + 6} {x1 + 3} {y + 1}" fill="none" stroke="{INK}" stroke-width="4"/>')
        if talk > 0.12:
            mx, my = face['mouth']
            ov += f'<ellipse cx="{mx}" cy="{my}" rx="{11 + 3 * talk:.1f}" ry="{2.5 + 9 * talk:.1f}" fill="#5A1A10" stroke="{INK}" stroke-width="3"/>'
            if talk > 0.45:
                ov += f'<ellipse cx="{mx}" cy="{my + 4 + 3 * talk:.1f}" rx="7" ry="{2 + 2 * talk:.1f}" fill="#C8341F"/>'
    return s + ov


def stumps_svg():
    s = '<g stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    for x in (-16, 0, 16):
        s += f'<rect x="{x - 6}" y="-130" width="12" height="130" rx="4" fill="#F0D9A0"/>'
    s += '<rect x="-22" y="-136" width="20" height="6" rx="3" fill="#E3C27A"/><rect x="2" y="-136" width="20" height="6" rx="3" fill="#E3C27A"/></g>'
    return s


# ================================================================== auto-rigged characters (assets/rigs/*.json)
import json as _json, os as _os
_RIG_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'assets', 'rigs')


def _rig_dirs():
    lib = _os.environ.get('RONGPAT_LIBRARY') or _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), 'library')
    return [_RIG_DIR, _os.path.join(lib, 'rigs')]


def _load_auto():
    out = {}
    files = []
    for dd in _rig_dirs():
        if _os.path.isdir(dd):
            files += [_os.path.join(dd, f) for f in sorted(_os.listdir(dd)) if f.endswith('.json')]
    for fp in files:
        d = _json.load(open(fp, encoding='utf-8'))
        arms = {a['side']: a for a in d['arms']}
        if 'l' not in arms or 'r' not in arms:
            continue
        L1 = sum(math.dist(a['sh'], a['el']) for a in arms.values()) / 2
        L2 = sum(math.dist(a['el'], a['ha']) for a in arms.values()) / 2
        d['sh'] = (tuple(arms['l']['sh']), tuple(arms['r']['sh']))
        d['L1'], d['L2'] = L1, L2
        d['armd'] = arms
        d['auto'] = True
        out[d['slug']] = d
    return out


AUTO = _load_auto()
for _k, _v in AUTO.items():
    if _k not in RIGS:
        RIGS[_k] = _v


def _shoe(x, y, kind, color, skin, sgn):
    if kind == 'boot':
        return f'<path d="M{x - 16:.1f} {y + 6:.1f} L{x - 14:.1f} {y - 30:.1f} L{x + 12:.1f} {y - 30:.1f} L{x + 12:.1f} {y - 8:.1f} Q{x + 22 * sgn + (0 if sgn > 0 else 0):.1f} {y - 4:.1f} {x + 24 * sgn:.1f} {y + 6:.1f}Z" fill="{color}"/>'
    if kind in ('bare', None):
        return f'<ellipse cx="{x + 2 * sgn:.1f}" cy="{y + 2:.1f}" rx="20" ry="9" fill="{skin}"/>'
    if kind == 'chappal':
        return (f'<ellipse cx="{x + 2 * sgn:.1f}" cy="{y + 2:.1f}" rx="20" ry="9" fill="{skin}"/>'
                f'<path d="M{x - 22:.1f} {y + 10:.1f} L{x + 24:.1f} {y + 10:.1f}" stroke="{color}" stroke-width="6"/>')
    return f'<path d="M{x - 20:.1f} {y + 8:.1f} Q{x - 18:.1f} {y - 10:.1f} {x:.1f} {y - 10:.1f} Q{x + 22 * sgn:.1f} {y - 6:.1f} {x + 24 * sgn:.1f} {y + 8:.1f}Z" fill="{color}"/>'


def idle_auto(R, t):
    a = R['armd']
    sw = 3 * math.sin(t * 1.7)
    return dict(lh=(a['l']['ha'][0] + sw, a['l']['ha'][1]), rh=(a['r']['ha'][0] - sw, a['r']['ha'][1]), dy=1.5 * math.sin(t * 2.0), lean=0.0,
                head=1.5 * math.sin(t * 0.9))


def draw_auto(R, head_defs, head_svg, pose, blink=0.0, talk=0.0, face=None):
    sy, hip, feet = R['sy'], R['hip'], R['feet']
    dy, lean = pose.get('dy', 0.0), pose.get('lean', 0.0)
    legs = ''
    lg = R.get('legs')
    if lg:
        w, gap = lg['w'], lg['gap']
        top = lg['top']
        fo = R.get('foot') or {}
        LT = (feet - 8 - (top + 10)) / 2 + 3
        for sgn, lift_k in ((-1, 'lf_lift'), (1, 'rf_lift')):
            hx = 196 + sgn * (gap + w / 2)
            Hj = (hx, top + 10 + dy)
            lift = pose.get(lift_k, 0.0)
            F = (hx + sgn * 2 - sgn * lift * 0.25, feet - 8 - lift)
            K, F2 = ik(Hj, F, LT, LT, sgn)
            legs += limb(Hj, K, F2, lg['fill'], max(18, w * 0.8))
            spread = fo.get('spread', 24)
            legs += _shoe(F2[0], F2[1] + 6, fo.get('kind'), fo.get('color', INK), fo.get('skin', R['skin']), sgn)
    arms, hands, props_layer, circles = '', {}, '', ''
    for side, key, sgn in (('l', 'lh', -1), ('r', 'rh', 1)):
        a = R['armd'][side]
        S = tuple(a['sh'])
        T = pose.get(key) or tuple(a['ha'])
        E, Hd = ik(S, T, R['L1'], R['L2'], sgn)
        w = a.get('w', 16)
        if a['short']:
            arms += f'<path d="M{P(S)} L{P(E)} L{P(Hd)}" fill="none" stroke="{INK}" stroke-width="{w + 8}"/>'
            arms += f'<path d="M{P(E)} L{P(Hd)}" fill="none" stroke="{R["skin"]}" stroke-width="{w}"/>'
            arms += f'<path d="M{P(S)} L{P(E)}" fill="none" stroke="{a["sleeve"]}" stroke-width="{w + 2}"/>'
        else:
            arms += limb(S, E, Hd, a['sleeve'], w)
        ang = math.degrees(math.atan2(Hd[1] - E[1], Hd[0] - E[0])) - 90
        hands[side] = (Hd, ang)
        pr = R['props'].get(side)
        bat = pose.get('bat')
        if bat and bat[0] == side:
            props_layer += prop_at('bat', Hd, bat[1])
        elif pr:
            d_ang = ang - pr['rest_angle']
            hx0, hy0 = pr['hand']
            props_layer += (f'<g transform="translate({Hd[0]:.1f},{Hd[1]:.1f}) rotate({d_ang:.1f}) translate({-hx0:.1f},{-hy0:.1f})">{pr["svg"]}</g>')
        if pose.get('ball') and side == 'r':
            props_layer += prop_at('ball', (Hd[0], Hd[1] - 10), 0)
        if a.get('hand', True):
            circles += f'<circle cx="{Hd[0]:.1f}" cy="{Hd[1] + 4:.1f}" r="11" fill="{R["skin"]}" stroke="{INK}" stroke-width="4"/>'
    head = f'<g transform="rotate({pose.get("head", 0):.1f} 196 {R["chin"]:.1f})">{_head(R, head_svg, blink, talk, face)}</g>'
    neck = (f'<path d="M{196 - 14} {R["chin"] - 18} L{196 - 14} {R["chin"] + 16} Q196 {R["chin"] + 22} {196 + 14} {R["chin"] + 16} '
            f'L{196 + 14} {R["chin"] - 18}Z" fill="{R["skin"]}"/>')
    up_tf = f'translate(0,{dy:.1f}) rotate({lean:.1f} 196 {hip:.1f})'
    body = (f'<g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{R.get("behind", "")}{legs}'
            f'<g transform="translate(0,{dy * 0.4:.1f})">{R.get("static_feet", "")}</g>'
            f'<g transform="{up_tf}">{neck}{R["torso"]}{head}{arms}{props_layer}{circles}{R.get("front", "")}</g></g>')
    out_hands = {}
    ar = math.radians(lean)
    for side, (Hd, ang) in hands.items():
        x, y = Hd[0], Hd[1] + dy
        cx, cy = 196, hip + dy
        out_hands[side] = (cx + (x - cx) * math.cos(ar) - (y - cy) * math.sin(ar), cy + (x - cx) * math.sin(ar) + (y - cy) * math.cos(ar))
    return head_defs + body, out_hands
