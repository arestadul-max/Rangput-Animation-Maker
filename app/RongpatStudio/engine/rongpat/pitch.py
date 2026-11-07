"""The cricket pitch: a real batting/bowling scene seen down the pitch, like cricket on TV.

Two camera views (the View column):
  batting  camera behind the bowler, looking at the batter: batter facing us with stumps and keeper behind, fielders
           far away; the ball comes in from the bottom of the frame, bounces and is hit (or goes to the keeper).
  bowling  camera behind the batter, looking at the bowler: the bowler runs in towards us, jumps and bowls; the
           ball comes at the camera (or, after a big hit, flies back over the bowler's head).

Everything lives in pitch coordinates: p = metres along the pitch (batter's stumps at 0, bowler's stumps at 20),
X = metres sideways, H = metres up. A simple telephoto camera projects them to the 540 x 960 frame.
"""
import math

INK = '#1C1410'
KID_UNITS = 158.0    # drawing units per metre for a character at scale 1 (a kid is ~1.4 m = 221 units)


def _cam(pc, d, z_main, mult, feet_y, h=10.0):
    """A high telephoto camera like cricket on TV. z_main: distance to the main player, drawn at scale `mult`
    with feet at `feet_y`."""
    F = mult * KID_UNITS * z_main
    return dict(pc=pc, d=d, F=F, h=h, yh=feet_y - F * h / z_main)


VIEWS = {
    'batting': _cam(pc=101.0, d=-1, z_main=100.0, mult=0.95, feet_y=690.0),   # batter at p=1
    'bowling': _cam(pc=-80.0, d=+1, z_main=100.0, mult=0.95, feet_y=700.0),   # bowler at the crease, p=20
}
Y_H = 0.0
ALIASES = {'batting': 'batting', 'batter': 'batting', 'batsman': 'batting', 'center': 'batting', 'centre': 'batting',
           'bowling': 'bowling', 'bowler': 'bowling', 'run-up': 'bowling'}


def view_of(s):
    return ALIASES.get((s.view or 'batting').split()[0], 'batting')


def depth(view, p):
    v = VIEWS[view]
    return (p - v['pc']) * v['d']


def project(view, p, X=0.0, H=0.0):
    """-> (x, y, scale) in frame units; scale = how big a character of scale 1 is drawn there. None if behind us."""
    z = depth(view, p)
    if z < 1.5:
        return None
    v = VIEWS[view]
    return (270 + v['F'] * X / z, v['yh'] + v['F'] * (v['h'] - H) / z, v['F'] / (z * KID_UNITS))


# ------------------------------------------------------------------ who is who
def roles(s, lib):
    bat = bowl = keep = None
    ball = None
    for c in s.cast:
        kind = lib.chars[c['slug']]['kind']
        names = [g.get('name') for g in c.get('segs', [])]
        if kind == 'prop':
            if c['slug'] == 'ball' or any(n in ('bowl', 'throw') for n in names):
                ball = c
                for g in c.get('segs', []):
                    if g.get('name') == 'bowl' and len(g.get('arg', [])) >= 2:
                        bowl = bowl or g['arg'][0]
                        bat = bat or g['arg'][1]
            continue
        if any(n in ('bat-ready', 'swing') for n in names):
            bat = bat or c['slug']
        if 'keeper' in names:
            keep = keep or c['slug']
        if any(n in ('bowl',) for n in names):
            bowl = bowl or c['slug']
    return bat, bowl, keep, ball


def ball_plan(ball):
    """Release time, arrival time at the bat, and what happens after (hit-up/left/right or None)."""
    t_r, hit, t_h = None, None, None
    for g in (ball or {}).get('segs', []):
        if g.get('name') == 'bowl' and t_r is None:
            t_r = g['t0']
        if g.get('name') in ('hit-up', 'hit-left', 'hit-right') and hit is None:
            hit, t_h = g['name'], g['t0']
    if t_r is None:
        return None
    t_arr = t_h if (t_h is not None and t_h > t_r + 0.3) else t_r + 0.7
    return dict(t_r=t_r, t_arr=t_arr, hit=hit)


REL = (19.4, -0.25, 1.85)      # release point (p, X, H)
ARR = (1.35, 0.28, 0.50)       # where the ball meets the bat (batter stands at p=1, in front of the stumps)
BOUNCE_P = 4.2


def ball_3d(plan, t):
    """Ball position (p, X, H) at shot time t, or None before release."""
    if not plan or t < plan['t_r']:
        return None
    t_r, t_a = plan['t_r'], plan['t_arr']
    if t <= t_a:
        k = (t - t_r) / max(0.05, t_a - t_r)
        kb = (REL[0] - BOUNCE_P) / (REL[0] - ARR[0])        # fraction of the flight before the bounce
        p = REL[0] + (ARR[0] - REL[0]) * k
        X = REL[1] + (ARR[1] - REL[1]) * k
        if k < kb:
            q = k / kb
            H = max(0.0, REL[2] * (1 - q * q))
        else:
            q = (k - kb) / (1 - kb)
            H = ARR[2] * math.sin(q * math.pi / 2) + 0.05
        return (p, X, H)
    u = t - t_a
    hit = plan['hit']
    if hit == 'hit-up':                                     # lofted: back over the bowler's head for six
        return (ARR[0] + 18 * u, ARR[1] + 1.8 * u, ARR[2] + 10 * u - 3 * u * u)
    if hit in ('hit-left', 'hit-right'):                    # along the ground to the side
        d = -1 if hit == 'hit-left' else 1
        return (ARR[0] + 6 * u, ARR[1] + d * 22 * u, max(0.04, 0.4 * abs(math.sin(u * 7)) * max(0, 1 - u)))
    k = min(1.0, u / 0.3)                                   # missed: past the bat into the keeper's gloves
    return (ARR[0] + (-2.8 - ARR[0]) * k, ARR[1] + (-0.6 - ARR[1]) * k, ARR[2] + 0.15 * k)


# ------------------------------------------------------------------ where everyone stands
# fielders: (p, where across the frame from -1 left edge to +1 right edge)
FIELD_BAT = [(-12.0, -0.82), (-10.0, 0.7), (-18.0, -0.3), (-22.0, 0.35), (-28.0, -0.75), (-26.0, 0.8), (-33.0, 0.05), (-31.0, -0.5)]
FIELD_BOWL = [(28.0, -0.66), (33.0, 0.6), (44.0, -0.28), (40.0, 0.82), (50.0, 0.3), (54.0, -0.8), (30.0, 0.9), (58.0, 0.0)]


def place_cast(s, t, lib, view):
    """-> list of (slug, p, X, extra) for the people drawn in this view; extra may hold run-up info."""
    bat, bowl, keep, ball = roles(s, lib)
    plan = ball_plan(ball)
    out = []
    fi = 0
    for c in s.cast:
        slug = c['slug']
        if lib.chars[slug]['kind'] == 'prop':
            continue
        if slug == bat:
            if view == 'batting':
                out.append((slug, 1.0, 0.0, {}))
            continue
        if slug == keep:
            if view == 'batting':
                out.append((slug, -3.0, -0.85, {}))
            continue
        if slug == bowl:
            if view == 'bowling':
                p, run, ph = 20.8, False, 0.0
                if plan:
                    t_r = plan['t_r']
                    a, b = max(0.0, t_r - 1.7), t_r - 0.35
                    if t < b:
                        k = max(0.0, (t - a) / max(0.2, b - a))
                        p = 34.0 + (21.0 - 34.0) * k
                        run, ph = True, (t - a) * 2.2
                    elif t < t_r:
                        p = 21.0 - 0.6 * (t - b) / 0.35
                    else:
                        p = 20.4 - 2.8 * min(1.0, (t - t_r) / 0.7)
                out.append((slug, p, -0.35, {'run': run, 'phase': ph}))
            continue
        spots = FIELD_BAT if view == 'batting' else FIELD_BOWL
        p, fr = spots[fi % len(spots)]
        X = fr * 270 * depth(view, p) / VIEWS[view]['F']
        fi += 1
        out.append((slug, p, X, {}))
    return out, plan, (bat, bowl, keep, ball)


def auto_poses(c_slug, roles_, plan, poses):
    """Add the obvious cricket poses if the sheet did not: stance, swing at the ball, the bowling action, keeper."""
    bat, bowl, keep, _ = roles_
    names = [n for n, _ in poses]
    out = list(poses)
    if c_slug == bat:
        if 'bat-ready' not in names:
            out.insert(0, ('bat-ready', 0.0))
        if plan and plan['hit'] and 'swing' not in names:
            out.append(('swing', plan['t_arr'] - 0.2))
    if c_slug == bowl and plan and 'bowl' not in names:
        out.append(('bowl', plan['t_r'] - 0.35))
    if c_slug == keep and 'keeper' not in names:
        out.insert(0, ('keeper', 0.0))
    return sorted(out, key=lambda a: a[1])


# ------------------------------------------------------------------ drawing
def _quad(view, pts, fill, extra=''):
    q = [project(view, p, X) for p, X in pts]
    if any(v is None for v in q):
        return ''
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y, _ in q) + 'Z'
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def _line(view, a, b, col, w):
    pa, pb = project(view, *a), project(view, *b)
    if not pa or not pb:
        return ''
    return f'<path d="M{pa[0]:.1f} {pa[1]:.1f} L{pb[0]:.1f} {pb[1]:.1f}" stroke="{col}" stroke-width="{w}" fill="none"/>'


def stumps(view, p, X=0.0):
    pr = project(view, p, X)
    if not pr:
        return ''
    x, y, k = pr
    u = KID_UNITS * k                                     # units per metre here
    h, gap, w = 0.71 * u, 0.11 * u, max(3.0, 0.045 * u)
    g = f'<g stroke="{INK}" stroke-width="3" stroke-linejoin="round">'
    for i in (-1, 0, 1):
        g += f'<rect x="{x + i * gap - w / 2:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w * 0.3:.1f}" fill="#F0D9A0"/>'
    g += (f'<rect x="{x - gap * 1.1:.1f}" y="{y - h - w * 0.6:.1f}" width="{gap * 1.05:.1f}" height="{w * 0.6:.1f}" fill="#E3C27A"/>'
          f'<rect x="{x + gap * 0.05:.1f}" y="{y - h - w * 0.6:.1f}" width="{gap * 1.05:.1f}" height="{w * 0.6:.1f}" fill="#E3C27A"/></g>')
    g += f'<ellipse cx="{x:.1f}" cy="{y + 2:.1f}" rx="{gap * 2.2:.1f}" ry="{gap * 0.35:.1f}" fill="{INK}" opacity="0.18"/>'
    return g


def background(view):
    """Seen from high up: the field with mowing stripes, the narrow gully pitch with creases, and the boundary wall
    with trees and the school far away at the top."""
    far_p = -38.0 if view == 'batting' else 62.0
    wall = project(view, far_p, 0, 0)
    wy = wall[1] if wall else 80
    g = '<rect x="-400" y="-400" width="1340" height="1760" fill="#7FA65A"/>'
    # mowing stripes
    ps = ([-60, -40, -30, -22, -15, -9, -4, 1, 6, 11, 16, 21, 26, 31, 36, 42, 50]
          if view == 'batting' else [90, 70, 60, 52, 45, 38, 32, 26, 20, 14, 8, 2, -4, -10, -16, -22, -30, -40])
    for i in range(len(ps) - 1):
        if i % 2 == 0:
            g += _quad(view, [(ps[i], -80), (ps[i], 80), (ps[i + 1], 80), (ps[i + 1], -80)], '#8DB466')
    # boundary: trees, the school and a painted wall
    g += (f'<g stroke="{INK}" stroke-width="3" stroke-linejoin="round">'
          f'<rect x="-400" y="-400" width="1340" height="{wy + 380:.0f}" fill="#3E7A3A"/>'
          f'<rect x="300" y="{wy - 120:.0f}" width="190" height="104" fill="#E3A92B"/><rect x="292" y="{wy - 132:.0f}" width="206" height="16" fill="#B5462A"/>'
          + ''.join(f'<rect x="{320 + i * 42}" y="{wy - 100:.0f}" width="22" height="34" rx="10" fill="#2E6B3A"/>' for i in range(4))
          + ''.join(f'<path d="M{x} {wy:.0f} Q{x - 40} {wy - 50:.0f} {x - 8} {wy - 92:.0f} Q{x + 22} {wy - 126:.0f} {x + 48} {wy - 90:.0f} '
                    f'Q{x + 78} {wy - 50:.0f} {x + 40} {wy:.0f}Z" fill="{c}"/>'
                    for x, c in ((-20, '#4A8A42'), (70, '#2E6B3A'), (160, '#4A8A42'), (240, '#2E6B3A'), (500, '#4A8A42')))
          + f'<rect x="-20" y="{wy - 24:.0f}" width="580" height="28" fill="#FBF5E9"/>'
          + ''.join(f'<path d="M{x} {wy - 10:.0f} q9 -7 18 0 q-9 7 -18 0Z M{x + 18} {wy - 10:.0f} l7 -6 l0 12Z" fill="#E07A2E" stroke-width="1.5"/>'
                    for x in range(6, 540, 48))
          + '</g>')
    # the pitch (a narrow gully pitch), worn ends and creases
    W = 0.85
    g += _quad(view, [(-3.0, -W), (-3.0, W), (23.0, W), (23.0, -W)], '#D8BD84', 'stroke="#B89A62" stroke-width="2"')
    for pe in (0.0, 20.0):
        g += _quad(view, [(pe - 1.4, -0.7), (pe - 1.4, 0.7), (pe + 1.9, 0.7), (pe + 1.9, -0.7)] if pe == 0 else
                   [(pe - 1.9, -0.7), (pe - 1.9, 0.7), (pe + 1.4, 0.7), (pe + 1.4, -0.7)], '#C9A86C', 'opacity="0.75"')
    for pe, sgn in ((0.0, 1), (20.0, -1)):
        g += _line(view, (pe + sgn * 1.22, -W), (pe + sgn * 1.22, W), '#FBF5E9', 3)     # popping crease
        g += _line(view, (pe, -0.9), (pe, 0.9), '#FBF5E9', 2)                          # bowling crease
        for X in (-0.9, 0.9):
            g += _line(view, (pe - sgn * 0.8, X), (pe + sgn * 1.22, X), '#FBF5E9', 2)  # return creases
    return g


_PLAN = [None]


def _lerp_x(plan):
    k = (REL[0] - BOUNCE_P) / (REL[0] - ARR[0])
    return (REL[1] + (ARR[1] - REL[1]) * k, 0.0)


def ball_svg(view, b, t, plan=None):
    """The ball and its shadow on the grass."""
    _PLAN[0] = plan
    if not b:
        return '', None
    p, X, H = b
    if view == 'batting' and plan and p > BOUNCE_P and t < plan['t_arr']:
        # the bowler is behind this camera: the ball comes in from the bottom of the frame down to the bounce
        bp = project(view, BOUNCE_P, *_lerp_x(plan))
        k = (REL[0] - p) / (REL[0] - BOUNCE_P)
        x0, y0 = 240.0, 1010.0
        x, y = x0 + (bp[0] - x0) * k, y0 + (bp[1] - y0) * k
        r = max(4.0, 0.036 * KID_UNITS * 3.0 * (1.9 - 0.85 * k))
        return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({(t * 900) % 360:.0f})"><circle r="{r:.1f}" fill="#B3261E" stroke="{INK}" stroke-width="3"/>'
                f'<path d="M{-r * 0.35:.1f} {-r * 0.85:.1f} Q{r * 0.1:.1f} 0 {-r * 0.35:.1f} {r * 0.85:.1f}" fill="none" stroke="#FBF5E9" stroke-width="2"/></g>'), depth(view, p)
    pr = project(view, p, X, H)
    sh = project(view, p, X, 0.0)
    if not pr or not sh:
        return '', None
    x, y, k = pr
    r = max(4.0, 0.036 * KID_UNITS * k * 3.0)     # drawn bigger than life so it reads on a phone
    if r > 140 or y < -200 or y > 1200:
        return '', None
    sw = (t * 900) % 360
    trail = ''
    for i, dt in enumerate((0.05, 0.1)):
        pb = ball_3d(_PLAN[0], t - dt) if _PLAN[0] else None
        q = project(view, *pb) if pb else None
        if q:
            trail += f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{r * (0.8 - 0.2 * i):.1f}" fill="#FBF5E9" opacity="{0.35 - 0.12 * i:.2f}"/>'
    shadow = f'<ellipse cx="{sh[0]:.1f}" cy="{sh[1]:.1f}" rx="{r * 1.1:.1f}" ry="{r * 0.35:.1f}" fill="{INK}" opacity="{0.25 / (1 + H):.2f}"/>'
    ball = (f'<g transform="translate({x:.1f},{y:.1f}) rotate({sw:.0f})"><circle r="{r:.1f}" fill="#B3261E" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M{-r * 0.35:.1f} {-r * 0.85:.1f} Q{r * 0.1:.1f} 0 {-r * 0.35:.1f} {r * 0.85:.1f}" fill="none" stroke="#FBF5E9" stroke-width="2"/>'
            f'<path d="M{r * 0.35:.1f} {-r * 0.85:.1f} Q{-r * 0.1:.1f} 0 {r * 0.35:.1f} {r * 0.85:.1f}" fill="none" stroke="#FBF5E9" stroke-width="2"/></g>')
    return shadow + trail + ball, depth(view, p)
