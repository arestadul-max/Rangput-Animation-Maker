"""Situation-driven facial expressions drawn over a character's face (head coordinates).

A face is described by its anchors: skin colour, two eyes (x0, x1, y, yt) and the mouth point. Expressions are
parameter sets that blend smoothly; `auto_expression` picks one from what is happening in the shot.
"""
import math, re

INK = '#1C1410'
CONCH = '#FBF5E9'

# brow: (inner lift, outer lift, angle bias); lid: top lid closure 0..1; low: lower lid raise; eye: eye size;
# pupil: pupil size; mouth: smile curve (-1 frown .. 1 big smile), open: base mouth opening 0..1, wide: width factor
BASE = dict(brow_in=0.0, brow_out=0.0, lid=0.0, low=0.0, eye=1.1, pupil=1.0, smile=0.15, open=0.0, wide=1.0,
            teeth=0.0, blush=0.0, sweat=0.0, tears=0.0, vein=0.0, wobble=0.0, tilt=0.0, ghoul=0.0)
EXPR = {
    'neutral': {},
    'happy': dict(smile=0.8, low=0.25, brow_in=2, brow_out=2, blush=0.3),
    'excited': dict(smile=0.9, open=0.55, eye=1.15, brow_in=6, brow_out=6, pupil=1.1),
    'laughing': dict(smile=1.0, open=0.8, lid=0.9, low=0.5, brow_in=4, brow_out=4, blush=0.5),
    'sad': dict(smile=-0.6, brow_in=7, brow_out=-4, lid=0.3, pupil=1.1),
    'crying': dict(smile=-0.8, open=0.35, brow_in=9, brow_out=-5, lid=0.55, tears=1.0, wobble=0.6),
    'angry': dict(smile=-0.5, brow_in=-8, brow_out=4, lid=0.35, teeth=1.0, open=0.25, wide=1.2, vein=1.0),
    'scared': dict(smile=-0.4, open=0.45, eye=1.25, pupil=0.6, brow_in=9, brow_out=2, sweat=1.0, wobble=1.0),
    'surprised': dict(smile=0.0, open=0.6, eye=1.3, pupil=0.75, brow_in=10, brow_out=10),
    'shocked': dict(smile=-0.2, open=0.9, eye=1.35, pupil=0.55, brow_in=12, brow_out=12, sweat=0.6),
    'confused': dict(smile=-0.15, brow_in=6, brow_out=-2, tilt=1.0, wobble=0.3),
    'thinking': dict(smile=-0.05, lid=0.25, brow_in=-2, brow_out=5, tilt=0.6),
    'nervous': dict(smile=0.1, wobble=1.0, brow_in=6, brow_out=-2, sweat=1.0, pupil=0.85),
    'embarrassed': dict(smile=0.35, wobble=0.5, lid=0.3, brow_in=5, brow_out=-1, blush=1.0, sweat=0.4),
    'smug': dict(smile=0.55, lid=0.45, brow_in=-2, brow_out=4, tilt=0.8),
    'sleepy': dict(lid=0.75, smile=0.0, brow_in=-1, brow_out=-3),
    'disgusted': dict(smile=-0.7, lid=0.4, low=0.4, brow_in=-6, brow_out=2, tilt=0.5),
    'love': dict(smile=0.7, lid=0.3, low=0.3, blush=1.0, brow_in=4, brow_out=3),
    'stern': dict(smile=-0.25, lid=0.25, brow_in=-6, brow_out=2),
    # horror: black eyes with burning pupils, no blush
    'evil': dict(smile=0.4, lid=0.3, brow_in=-10, brow_out=7, pupil=0.7, ghoul=1.0, tilt=0.4),
    'haunting': dict(smile=-0.1, eye=1.25, pupil=0.55, brow_in=-4, brow_out=4, ghoul=1.0),
}
GHOSTS = {'petni', 'jol-konya', 'kalo-megh', 'bot-dadu'}

EMOTE_EXPR = {'!': 'surprised', '?': 'confused', 'heart': 'love', 'zzz': 'sleepy', 'sweat': 'nervous', 'anger': 'angry',
              'idea': 'excited', 'music': 'happy', 'sparkle': 'excited', 'shock': 'shocked'}
ACTION_EXPR = {'cheer': 'excited', 'six': 'excited', 'clap': 'happy', 'arm-dance': 'happy', 'dance': 'happy', 'happy': 'happy',
               'cover-face': 'scared', 'scared': 'scared', 'shake': 'scared', 'fall': 'shocked', 'facepalm': 'embarrassed',
               'hands-on-hips': 'stern', 'think': 'thinking', 'shrug': 'confused', 'cry': 'crying', 'catch': 'surprised',
               'swing': 'excited', 'bowl': 'stern', 'eat': 'happy', 'sleep': 'sleepy', 'point': 'stern', 'wave': 'happy',
               'magnify': 'thinking', 'bat-ready': 'stern', 'keeper': 'thinking', 'glow': 'love', 'spin': 'excited', 'jump': 'excited'}
HOLD_ACTIONS = {'hands-on-hips', 'think', 'magnify', 'bat-ready', 'keeper', 'sleep', 'glow', 'eat'}


def mix(names_weights):
    out = dict(BASE)
    tot = sum(w for _, w in names_weights) or 1
    for k in BASE:
        out[k] = sum(EXPR.get(n, {}).get(k, BASE[k]) * w for n, w in names_weights) / tot
    return out


def text_mood(text, loud):
    t = text.strip()
    if not t:
        return None
    if re.search(r'[!！]\s*[\?？]|[\?？]\s*[!！]', t):
        return 'shocked'
    if t.endswith(('!', '!”', '!"', '?!')) or t.count('!') >= 2:
        return 'excited' if loud < 0.85 else 'angry' if re.search(r'(কে |কেন|WHO|Who|NO|না!)', t) else 'excited'
    if t.endswith(('?', '?”', '?"')):
        return 'confused'
    if '…' in t or '...' in t:
        return 'nervous'
    return None


def auto_expression(s, slug, t, talk, lib_kind=None):
    """Returns [(expression, weight)] for this character at shot time t."""
    # 1. explicit Expression column
    exp = [e for e in getattr(s, 'expressions', []) if e['slug'] == slug and e['t'] <= t]
    if exp:
        e = exp[-1]
        prev = exp[-2]['kind'] if len(exp) > 1 else 'neutral'
        w = min(1.0, (t - e['t']) / 0.3)
        return [(e['kind'], w), (prev, 1 - w)]
    picks = []
    # 2. emotes
    for e in getattr(s, 'emotes', []):
        if e['slug'] == slug and 0 <= t - e['t'] <= 2.2:
            u = t - e['t']
            picks.append((EMOTE_EXPR.get(e['kind'], 'neutral'), min(1, u / 0.15) * min(1, (2.2 - u) / 0.4)))
    # 3. actions
    for a in getattr(s, 'actions', {}).get(slug, []):
        st = a['t'] if a['t'] is not None else 0.0
        name = a['name']
        if name in ACTION_EXPR and t >= st:
            u = t - st
            dur = 99 if name in HOLD_ACTIONS else (1.8 if name != 'catch' else 0.7)
            if u <= dur:
                w = min(1, u / 0.2) * min(1, (dur - u) / 0.4)
                picks.append((ACTION_EXPR[name], w * (0.6 if name in HOLD_ACTIONS else 1.0)))
            if name == 'catch' and 0.7 < u < 2.5:
                picks.append(('happy', min(1, (u - 0.7) / 0.3)))
    # 4. what they are saying
    for v in getattr(s, 'voices', []):
        if v['speaker'] != slug or not v.get('len'):
            continue
        if v['start'] - 0.2 <= t <= v['start'] + v['len'] + 0.6:
            loud = max(v['env']) if v.get('env') is not None and len(v['env']) else 0.5
            part = _caption_part(s, v)
            m = text_mood(part, loud)
            if m:
                picks.append((m, 0.8))
    # 5. listeners react to someone else's strong line
    if not picks:
        for v in getattr(s, 'voices', []):
            if v['speaker'] and v['speaker'] != slug and v.get('len') and v['start'] <= t <= v['start'] + v['len'] + 0.8:
                m = text_mood(_caption_part(s, v), 0.5)
                if m in ('angry', 'shocked'):
                    picks.append(('nervous', 0.5))
                elif m == 'excited':
                    picks.append(('happy', 0.4))
    if not picks:
        return [('neutral', 1.0)]
    tot = sum(w for _, w in picks)
    if tot < 1:
        picks.append(('neutral', 1 - tot))
    return picks


def _caption_part(s, v):
    parts = [p.strip() for p in s.subtitle.lstrip('^').split('|') if p.strip()] if s.subtitle else []
    if not parts:
        return ''
    i = s.voices.index(v) if v in s.voices else 0
    return parts[min(i, len(parts) - 1)]


def gaze_for(s, slug, t, positions):
    """Pupil offset (dx, dy) in eye units: look at the current speaker, else drift."""
    me = positions.get(slug)
    for v in getattr(s, 'voices', []):
        if v['speaker'] and v['speaker'] != slug and v.get('len') and v['start'] <= t <= v['start'] + v['len'] + 0.3:
            other = positions.get(v['speaker'])
            if me and other:
                d = other[0] - me[0]
                return (max(-1, min(1, d / 120)) * 4.5, -1.0)
    ph = (hash(slug) % 100) / 17
    k = math.sin(t * 0.7 + ph)
    return (2.5 * (1 if k > 0.6 else -1 if k < -0.75 else 0), 0.0)


def draw_face(face, e, blink, talk, gaze=(0, 0), t=0.0):
    """Overlay in head coordinates. e = expression params (from mix)."""
    skin = face['skin']
    out = ''
    eyes = [e_ for e_ in (face.get('eyes') or []) if len(e_) == 4]
    if len(eyes) == 1:
        eyes = []          # one visible eye (e.g. behind a magnifier): leave the eyes as drawn
    lid = max(e['lid'], blink)
    closed = bool(face.get('closed'))
    for i, (x0, x1, y, yt) in enumerate(eyes):
        cx = (x0 + x1) / 2
        w = (x1 - x0) / 2 * e['eye']
        up = (y - yt) * e['eye'] + 2
        dn = 7 * e['eye']
        sgn = -1 if i == 0 else 1
        # redraw the eye so the pupils can look around and change size
        almond = f'M{cx - w:.1f} {y:.1f} Q{cx:.1f} {y - up * 1.9:.1f} {cx + w:.1f} {y:.1f} Q{cx:.1f} {y + dn * 1.6:.1f} {cx - w:.1f} {y:.1f}Z'
        # hide the eye (and brow) painted on the card, so the redrawn one never doubles up into a dark "mask"
        top = yt - (22 if closed else 12)
        out += (f'<ellipse cx="{cx:.1f}" cy="{(top + y + 11) / 2:.1f}" rx="{(x1 - x0) / 2 + 9:.1f}" ry="{(y + 11 - top) / 2:.1f}" '
                f'fill="{skin}" stroke="none"/>')
        g = e.get('ghoul', 0.0)
        out += f'<path d="{almond}" fill="{CONCH if g < 0.5 else "#0B0708"}" stroke="{INK}" stroke-width="3"/>'
        pr = 5.5 * e['pupil']
        px, py = cx + gaze[0] + e['tilt'] * 0.0, y - up * 0.25 + gaze[1]
        if g >= 0.5:      # burning pupils in black eyes
            fl = 0.75 + 0.25 * math.sin(t * 13 + i)
            out += (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr * 2.4:.1f}" fill="#FF2A1A" opacity="{0.25 * fl:.2f}" stroke="none"/>'
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr * 1.05:.1f}" fill="#FF3B22" stroke="none"/>'
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr * 0.45:.1f}" fill="#FFE9C8" opacity="{fl:.2f}" stroke="none"/>')
        else:
            out += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{pr:.1f}" fill="{INK}" stroke="none"/><circle cx="{px + pr * 0.4:.1f}" cy="{py - pr * 0.45:.1f}" r="1.8" fill="{CONCH}" stroke="none"/>'
        if lid > 0.02:
            ly = (y - up * 1.0) + (up * 1.0 + 2) * lid
            out += (f'<path d="M{cx - w - 3:.1f} {y + 1:.1f} Q{cx:.1f} {y - up * 2.1:.1f} {cx + w + 3:.1f} {y + 1:.1f} L{cx + w + 3:.1f} {ly - 2:.1f} '
                    f'Q{cx:.1f} {ly + 4 * (1 - lid):.1f} {cx - w - 3:.1f} {ly - 2:.1f}Z" fill="{skin}" stroke="none"/>'
                    f'<path d="M{cx - w - 3:.1f} {ly - 2:.1f} Q{cx:.1f} {ly + 4 * (1 - lid):.1f} {cx + w + 3:.1f} {ly - 2:.1f}" fill="none" stroke="{INK}" stroke-width="{4.5 if lid < 0.9 else 4:.1f}"/>')
        else:
            out += f'<path d="M{cx - w - 3:.1f} {y - 1:.1f} Q{cx:.1f} {y - up * 2.0:.1f} {cx + w + 3:.1f} {y - 1:.1f}" fill="none" stroke="{INK}" stroke-width="4.5"/>'
        if e['low'] > 0.05:
            out += f'<path d="M{cx - w:.1f} {y + 3:.1f} Q{cx:.1f} {y - 4 * e["low"]:.1f} {cx + w:.1f} {y + 3:.1f}" fill="none" stroke="{INK}" stroke-width="2.5"/>'
        # brow: inner end near the nose, outer end away from it
        bi, bo = e['brow_in'], e['brow_out']
        by = yt - (16 if closed else 14)
        inner_x, outer_x = (x1, x0) if i == 0 else (x0, x1)
        tilt = e['tilt'] * (6 if i == 1 else -1)
        out += (f'<path d="M{outer_x + sgn * 2:.1f} {by - bo - tilt:.1f} Q{cx:.1f} {by - (bi + bo) / 2 - 4 - tilt:.1f} {inner_x - sgn * 2:.1f} {by - bi - tilt:.1f}" '
                f'fill="none" stroke="{INK}" stroke-width="5.5" stroke-linecap="round"/>')
        if e['tears'] > 0.1:
            k = (t * 1.3 + i * 0.5) % 1
            out += f'<path d="M{cx + sgn * w * 0.6:.1f} {y + 6 + 30 * k:.1f} q-5 9 0 13 q5 -4 0 -13Z" fill="#9CC7C9" stroke="{INK}" stroke-width="1.5" opacity="{e["tears"] * (1 - k):.2f}"/>'
    if e.get('ghoul', 0) >= 0.5:      # wipe painted blush off a ghost's cheeks, add hollow shadows
        for (x0, x1, y, yt) in eyes:
            c_ = (x0 + x1) / 2
            out += (f'<ellipse cx="{c_:.1f}" cy="{y + 21:.1f}" rx="16" ry="11" fill="{skin}" stroke="none"/>'
                    f'<path d="M{c_ - 12:.1f} {y + 10:.1f} Q{c_:.1f} {y + 18:.1f} {c_ + 12:.1f} {y + 10:.1f}" fill="none" stroke="#3A3F55" stroke-width="3" opacity="0.6"/>')
    if e['blush'] > 0.05 and e.get('ghoul', 0) < 0.5:
        for (x0, x1, y, yt) in eyes:
            out += f'<ellipse cx="{(x0 + x1) / 2:.1f}" cy="{y + 20:.1f}" rx="11" ry="6" fill="#E58BA0" opacity="{0.6 * e["blush"]:.2f}" stroke="none"/>'
    # mouth
    mx, my = face['mouth']
    open_ = max(e['open'] * 0.6, 0) + talk * (0.8 + 0.4 * max(e['open'], 0))
    w = 13 * e['wide'] * (1 + 0.2 * max(e['smile'], 0))
    sm = e['smile']
    wob = e['wobble'] * 2.5 * math.sin(t * 18)
    out += f'<ellipse cx="{mx}" cy="{my + 1}" rx="{w + 7:.1f}" ry="11" fill="{skin}" stroke="none"/>'
    if open_ < 0.12:
        out += (f'<path d="M{mx - w:.1f} {my - sm * 4:.1f} Q{mx - w / 2:.1f} {my + sm * 7 + wob:.1f} {mx:.1f} {my + sm * 7 - wob:.1f} '
                f'Q{mx + w / 2:.1f} {my + sm * 7 + wob:.1f} {mx + w:.1f} {my - sm * 4 + e["tilt"] * -4:.1f}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>')
    else:
        h = 4 + 16 * min(1.2, open_)
        top = my - 3 - sm * 3
        bot_c = top + h * (1.2 + 0.4 * sm)
        out += (f'<path d="M{mx - w:.1f} {top:.1f} Q{mx:.1f} {top + sm * 5 - (2 if sm < 0 else 0) + wob:.1f} {mx + w:.1f} {top:.1f} '
                f'Q{mx + w * 0.7:.1f} {bot_c:.1f} {mx:.1f} {bot_c:.1f} Q{mx - w * 0.7:.1f} {bot_c:.1f} {mx - w:.1f} {top:.1f}Z" fill="#5A1A10" stroke="{INK}" stroke-width="3.5"/>')
        if e['teeth'] > 0.3 or sm > 0.6:
            out += f'<path d="M{mx - w * 0.8:.1f} {top + 1:.1f} L{mx + w * 0.8:.1f} {top + 1:.1f} L{mx + w * 0.7:.1f} {top + 5:.1f} L{mx - w * 0.7:.1f} {top + 5:.1f}Z" fill="{CONCH}" stroke="none"/>'
        if h > 9:
            out += f'<ellipse cx="{mx:.1f}" cy="{bot_c - 4:.1f}" rx="{w * 0.5:.1f}" ry="{min(5, h * 0.25):.1f}" fill="#C8341F" stroke="none"/>'
    # sweat drops and anger marks are drawn by the scene on the head itself (engine.draw_emote)
    return out
