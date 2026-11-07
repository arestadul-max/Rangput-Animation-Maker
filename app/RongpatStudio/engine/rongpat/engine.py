"""Rongpat Studio engine: turns a scene sheet into frames (SVG) and a sound mix."""
import json, math, os, random, re, difflib
from . import puppets as P
from . import sets as SETS
from . import rig as RIG
from . import expressions as X

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
USER_LIB = os.environ.get('RONGPAT_LIBRARY') or os.path.join(os.path.dirname(ROOT), 'library')
FPS = 30
W, H = 540, 960
INK = '#1C1410'
K = 1.9   # authored stroke width -> output px (same as the Short)


class SheetError(Exception):
    pass


# =================================================================== library
class Library:
    def __init__(self):
        self.chars = {c['slug']: c for c in json.load(open(os.path.join(ASSETS, 'characters', 'index.json'), encoding='utf-8'))}
        for slug, name, bn, role, desc, h in (
                ('mishti', 'Mishti (animated)', 'মিষ্টি', 'Ginger cat', 'Fully animated cat: sits, runs, leaps, meows, hisses.', 330),
                ('mechho', 'Mechho Bhoot (animated)', 'মেছো ভূত', 'Fish-loving ghost', 'Fully animated ghost: floats, gets scared, glows, holds a fish or sweet.', 290),
                ('tutul', 'Tutul (animated)', 'টুটুল', 'Little kid', 'Fully animated kid: talks, smiles, yawns, offers a sweet, walks.', 510)):
            self.chars[slug] = dict(slug=slug, name=name, bn=bn, role=role, desc=desc, kind='puppet', height=h)
        self.places = {p['slug']: p for p in json.load(open(os.path.join(ASSETS, 'places', 'index.json'), encoding='utf-8'))}
        self._svg = {}
        from .library import scan_user_library
        uc, up = scan_user_library(USER_LIB)
        self.user_chars, self.user_places = sorted(uc), sorted(up)
        self.chars.update(uc)
        self.places.update(up)
        for slug in RIG.RIGS:
            if slug in self.chars and slug not in uc:
                self.chars[slug] = dict(self.chars[slug], kind='rig')
        self.chars['ball'] = dict(slug='ball', name='Cricket ball (object)', bn='বল', role='Object', kind='prop', height=17, native_h=17,
                                  svg=RIG.ball_svg(8.5), grip=(0, 0), rest_dy=8.5, desc='A cricket ball.')
        self.chars['bat'] = dict(slug='bat', name='Cricket bat (object)', bn='ব্যাট', role='Object', kind='prop', height=115, native_h=224,
                                 svg=f'<g stroke="#1C1410" stroke-width="4" stroke-linejoin="round">{RIG.bat_svg()}</g>', grip=(0, 0), rest_dy=190,
                                 desc='A cricket bat (held at the handle).')
        self.chars['stumps'] = dict(slug='stumps', name='Cricket stumps (object)', bn='স্টাম্প', role='Object', kind='prop', height=115, native_h=136,
                                    svg=RIG.stumps_svg(), grip=(0, 0), rest_dy=0, desc='Three stumps with bails.')
        from .library import scan_user_props
        self.user_props = scan_user_props(USER_LIB)
        self.chars.update(self.user_props)
        self._rig_head = {}

    def rig_head(self, slug):
        if slug not in self._rig_head:
            self._rig_head[slug] = RIG._head_from_card(self.char_svg(slug))
        return self._rig_head[slug]

    def char_svg(self, slug):
        if slug not in self._svg:
            c = self.chars[slug]
            if 'svg' in c:
                self._svg[slug] = c['svg']
            else:
                self._svg[slug] = open(c.get('file') or os.path.join(ASSETS, 'characters', slug + '.svg'), encoding='utf-8').read()
        return self._svg[slug]

    def place_svg(self, slug):
        k = 'place:' + slug
        if k not in self._svg:
            p = self.places[slug]
            if 'svg' in p:
                self._svg[k] = p['svg']
            else:
                self._svg[k] = open(p.get('file') or os.path.join(ASSETS, 'places', slug + '.svg'), encoding='utf-8').read()
        return self._svg[k]

    def find(self, word, table, what):
        w = word.strip().lower().replace(' ', '-').replace('_', '-')
        tbl = self.chars if table == 'chars' else self.places
        if w in tbl:
            return w
        alias = {'mechho-bhoot': 'mechho', 'mishti-cat': 'mishti', 'cat': 'mishti', 'ghost': 'mechho', 'khema-dida': 'dida', 'grandma': 'dida',
                 'anko': 'anko-sir', 'ruksana': 'dr-ruksana', 'doctor': 'dr-ruksana', 'nurse': 'shefali', 'postman': 'haridas', 'guard': 'robin',
                 'kitchen': 'sen-kitchen-night', 'stairs': 'stairwell', 'rooftop': 'rooftop-at-night', 'roof': 'rooftop-at-night',
                 'classroom': 'school-classroom', 'school': 'school-gate', 'hospital': 'hospital-outside', 'thana': 'police-station-outside',
                 'police-station': 'police-station-outside', 'lab': 'school-science-lab'}
        if w in alias and alias[w] in tbl:
            return alias[w]
        for s, c in tbl.items():
            if w == c['name'].lower().replace(' ', '-') or w == c.get('bn', ''):
                return s
        sug = difflib.get_close_matches(w, list(tbl), n=3, cutoff=0.5)
        hint = f' Did you mean: {", ".join(sug)}?' if sug else f' See the {"Characters" if table == "chars" else "Places"} sheet for the list.'
        raise SheetError(f'Unknown {what} "{word}".{hint}')


# =================================================================== sheet parsing
POS = {'far-left': -190, 'left': -105, 'center': 0, 'centre': 0, 'middle': 0, 'mid': 0, 'right': 105, 'far-right': 190}
CAMERAS = ['auto', 'wide', 'medium', 'close', 'push-in', 'pull-out', 'pan-left', 'pan-right', 'follow', 'ball']
ACTIONS = {
    'enter-left': 'Walks in from the left to their spot.', 'enter-right': 'Walks in from the right.',
    'exit-left': 'Walks out to the left (near the end of the shot unless you give @time).', 'exit-right': 'Walks out to the right.',
    'walk-to': 'Walks to a new spot, e.g. "walk-to right".', 'run-to': 'Runs to a new spot.',
    'jump': 'Jumps (add x2, x3 for more).', 'hop': 'A small hop.', 'shake': 'Trembles with fear.', 'scared': 'Jumps back and trembles.',
    'happy': 'Bounces happily.', 'dance': 'Sways and bounces.', 'spin': 'Spins round once.', 'fall': 'Faints and falls over.',
    'sleep': 'Eyes shut, with Zzz.', 'float': 'Hovers up and down (ghosts do this anyway).', 'glow': 'A warm golden glow around them.',
    'appear': 'Fades in.', 'vanish': 'Fades out.', 'turn': 'Turns to face the other way.', 'grow': 'Grows bigger.', 'shrink': 'Shrinks smaller.',
    'sit': 'Mishti only: sits.', 'leap': 'Mishti only: leaps.', 'hiss': 'Mishti only: hisses.', 'offer': 'Tutul only: holds out a sweet.',
    'hold-fish': 'Mechho only: holds a fish.', 'hold-sweet': 'Mechho only: holds a sweet.', 'cry': 'Mechho only: tears.',
}
BALL_ACTIONS = {'in-hand': 'In someone’s hand: "ball: in-hand mitul" (add left or right).',
                'bowl': 'Bowled or thrown from one person to another: "ball: bowl mitul pupu @1.2".',
                'throw': 'Thrown to someone’s hands: "umbrella: throw haridas tuli @1".',
                'hit-up': 'Hit high into the sky and out of the frame.', 'hit-left': 'Hit hard along the ground to the left.',
                'hit-right': 'Hit hard along the ground to the right.',
                'fly-in': 'Flies in from above into someone’s hands: "ball: fly-in anko-sir @0.5".', 'drop': 'Falls to the ground.',
                'spin': 'Spins on the spot.', 'bounce': 'Bounces up and down.', 'swing': 'Swings back and forth (a door, a sign).',
                'appear': 'Pops in.', 'vanish': 'Disappears.'}
EMOTES = {'!': 'Surprise', '?': 'Confused', 'heart': 'Love', 'zzz': 'Sleepy', 'sweat': 'Nervous', 'anger': 'Angry', 'idea': 'Idea bulb',
          'music': 'Singing / music', 'sparkle': 'Delighted', 'shock': 'Shock lines'}
HEADERS = ['shot', 'place', 'view', 'time', 'camera', 'focus', 'cast', 'actions', 'speaker', 'voice', 'subtitle', 'emote', 'sfx', 'music', 'duration', 'transition', 'notes', 'expression']


def _norm_header(h):
    h = str(h or '').strip().lower()
    for k in HEADERS:
        if h.startswith(k):
            return k
    return h


def read_sheet(path):
    rows = []
    if path.lower().endswith('.csv'):
        import csv
        with open(path, encoding='utf-8-sig') as f:
            r = list(csv.reader(f))
    else:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb['Scenes'] if 'Scenes' in wb.sheetnames else wb.worksheets[0]
        r = [[c for c in row] for row in ws.iter_rows(values_only=True)]
    hdr_i = next((i for i, row in enumerate(r) if row and any(_norm_header(c) == 'place' for c in row)), None)
    if hdr_i is None:
        raise SheetError('The scene sheet needs a header row with at least a "Place" column.')
    hdr = [_norm_header(c) for c in r[hdr_i]]
    for n, row in enumerate(r[hdr_i + 1:], start=hdr_i + 2):
        d = {hdr[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(row) if i < len(hdr)}
        if not any(d.get(k) for k in ('place', 'cast', 'subtitle', 'voice', 'actions', 'sfx', 'duration', 'emote', 'camera')):
            continue
        if d.get('shot', '').startswith('Number of the shot'):
            continue
        d['_row'] = n
        rows.append(d)
    if not rows:
        raise SheetError('The scene sheet has no shots yet. Fill in at least one row under the header.')
    return rows


def _pos(word, row):
    w = word.lower()
    if w in POS:
        return POS[w]
    try:
        return max(-100, min(100, float(w.rstrip('%')))) * 2.4
    except ValueError:
        raise SheetError(f'Row {row}: unknown position "{word}". Use far-left, left, center, right, far-right or a number from -100 to 100.')


def _split(s, seps=';,\n'):
    return [x.strip() for x in re.split('[' + re.escape(seps) + ']', s) if x.strip()]


def _at_time(s):
    m = re.search(r'@\s*([0-9.]+)', s)
    return (re.sub(r'@\s*[0-9.]+', '', s).strip(), float(m.group(1)) if m else None)


class Shot:
    pass


def build_plan(rows, lib, project_dir, audio_mod=None):
    shots = []
    prev = None
    t = 0.0
    for d in rows:
        rn = d['_row']
        s = Shot()
        s.row = rn
        place = d.get('place') or (prev.place if prev else '')
        if not place:
            raise SheetError(f'Row {rn}: no Place given.')
        img = os.path.join(project_dir, 'images', place)
        if os.path.splitext(place)[1].lower() in ('.svg', '.png', '.jpg', '.jpeg') and os.path.exists(img):
            s.place = place
            s.place_kind = 'image'
            s.image = img
        else:
            s.place = lib.find(place, 'places', 'place')
            s.place_kind = lib.places[s.place]['kind']
        s.view = (d.get('view') or (prev.view if prev and prev.place == s.place else 'center')).lower()
        s.time = (d.get('time') or (prev.time if prev else 'day')).lower()
        if s.time not in ('day', 'evening', 'night'):
            raise SheetError(f'Row {rn}: Time must be day, evening or night (got "{s.time}").')
        cam = (d.get('camera') or 'auto').lower().split()
        s.camera = cam[0] if cam else 'auto'
        s.cam_shake = 'shake' in cam
        if s.camera not in CAMERAS:
            raise SheetError(f'Row {rn}: unknown camera "{s.camera}". Use one of: {", ".join(CAMERAS)}.')
        # cast
        cast_txt = d.get('cast', '')
        s.cast = []
        if cast_txt:
            for item in _split(cast_txt, ',;\n'):
                words = item.split()
                slug = lib.find(words[0], 'chars', 'character')
                c = dict(slug=slug, x=0.0, back=False, front=False, flip=False, hidden=False)
                for w in words[1:]:
                    lw = w.lower()
                    if lw in ('back', 'front', 'flip', 'hidden'):
                        c[lw] = True
                    else:
                        c['x'] = _pos(lw, rn)
                s.cast.append(c)
        elif prev and prev.place == s.place:
            s.cast = [dict(c) for c in prev.cast_end]
        
        # voices
        s.voices = []
        speakers = [lib.find(w, 'chars', 'character') for w in _split(d.get('speaker', ''), ',;\n')] if d.get('speaker') else []
        vt = 0.35
        for i, item in enumerate(_split(d.get('voice', ''), ';\n')):
            name, at = _at_time(item)
            fn = os.path.join(project_dir, 'voice', name)
            if not os.path.exists(fn):
                cand = [f for f in os.listdir(os.path.join(project_dir, 'voice')) if os.path.splitext(f)[0].lower() == os.path.splitext(name)[0].lower()] if os.path.isdir(os.path.join(project_dir, 'voice')) else []
                if cand:
                    fn = os.path.join(project_dir, 'voice', cand[0])
                else:
                    raise SheetError(f'Row {rn}: voice file "{name}" is not in the voice folder.')
            x = audio_mod.load_audio(fn)
            spk = speakers[i] if i < len(speakers) else (speakers[-1] if speakers else None)
            start = at if at is not None else vt
            s.voices.append(dict(file=fn, start=start, len=len(x) / audio_mod.SR, samples=x, env=audio_mod.envelope(x, FPS), speaker=spk))
            vt = start + len(x) / audio_mod.SR + 0.25
        if speakers and not s.voices:
            s.voices.append(dict(file=None, start=0.3, len=None, samples=None, env=None, speaker=speakers[0]))
        s.subtitle = d.get('subtitle', '')
        # duration
        dur = d.get('duration', '')
        if dur:
            try:
                s.dur = float(dur)
            except ValueError:
                raise SheetError(f'Row {rn}: Duration must be a number of seconds (got "{dur}").')
        else:
            vend = max([v['start'] + v['len'] for v in s.voices if v['len']] + [0])
            words = len(s.subtitle.split())
            s.dur = max(2.5, vend + 0.6 if vend else 1.2 + words * 0.38) if s.place_kind != 'title' else max(3.0, vend + 0.6)
        for v in s.voices:
            if v['len'] is None:
                v['len'] = s.dur - 0.6
        # focus
        f = d.get('focus', '')
        s.focus = lib.find(f, 'chars', 'character') if f else (speakers[0] if speakers else (s.cast[0]['slug'] if s.cast else None))
        # actions
        s.actions = {}
        for item in _split(d.get('actions', ''), ';\n'):
            if ':' not in item:
                raise SheetError(f'Row {rn}: actions need "who: what", e.g. "mishti: jump" (got "{item}").')
            who, what = item.split(':', 1)
            slug = lib.find(who, 'chars', 'character')
            for a in _split(what, ',+'):
                a, at = _at_time(a)
                parts = a.lower().split()
                if not parts:
                    continue
                name, arg = parts[0], parts[1:]
                isprop = lib.chars[slug]['kind'] == 'prop'
                allowed = BALL_ACTIONS if isprop else {**ACTIONS, **{k: v[2] for k, v in RIG.POSES.items()}}
                if name not in allowed:
                    sug = difflib.get_close_matches(name, list(allowed), n=2)
                    raise SheetError(f'Row {rn}: unknown action "{name}"' + (' for an object' if isprop else '') + '.' + (f' Did you mean {", ".join(sug)}?' if sug else ''))
                if isprop and name in ('in-hand', 'bowl', 'throw', 'fly-in'):
                    side = [w for w in arg if w in ('left', 'right')]
                    arg = [lib.find(w, 'chars', 'character') for w in arg if w not in ('left', 'right')] + side
                    need = 2 if name in ('bowl', 'throw') else 1
                    if len(arg) < need:
                        raise SheetError(f'Row {rn}: "ball: {name}" needs {"who bowls and who bats" if need == 2 else "whose hand"}, e.g. "ball: bowl mitul pupu".')
                s.actions.setdefault(slug, []).append(dict(name=name, arg=arg, t=at))
        # emotes
        s.emotes = []
        for item in _split(d.get('emote', ''), ';,\n'):
            if ':' not in item:
                raise SheetError(f'Row {rn}: emotes need "who: emote", e.g. "tutul: !".')
            who, what = item.split(':', 1)
            what, at = _at_time(what)
            what = what.strip().lower()
            if what not in EMOTES:
                raise SheetError(f'Row {rn}: unknown emote "{what}". Use one of: {" ".join(EMOTES)}.')
            s.emotes.append(dict(slug=lib.find(who, 'chars', 'character'), kind=what, t=at if at is not None else 0.2))
        # expressions (optional; otherwise automatic)
        s.expressions = []
        for item in _split(d.get('expression', ''), ';,\n'):
            if ':' not in item:
                raise SheetError(f'Row {rn}: expressions need "who: expression", e.g. "pupu: angry".')
            who, what = item.split(':', 1)
            what, at = _at_time(what)
            what = what.strip().lower()
            if what not in X.EXPR:
                sug = difflib.get_close_matches(what, list(X.EXPR), n=2)
                raise SheetError(f'Row {rn}: unknown expression "{what}".' + (f' Did you mean {", ".join(sug)}?' if sug else f' Use one of: {", ".join(X.EXPR)}.'))
            s.expressions.append(dict(slug=lib.find(who, 'chars', 'character'), kind=what, t=at if at is not None else 0.0))
        s.expressions.sort(key=lambda e: e['t'])
        # sfx
        s.sfx = []
        for item in _split(d.get('sfx', ''), ',;\n'):
            name, at = _at_time(item)
            s.sfx.append(dict(name=name.lower(), t=at if at is not None else 0.0))
        s.music = (d.get('music') or (prev.music if prev else 'calm')).lower()
        s.transition = (d.get('transition') or 'cut').lower()
        s.start = t
        t += s.dur
        for pslug in list(s.actions):
            if lib.chars[pslug]['kind'] == 'prop' and not any(c['slug'] == pslug for c in s.cast):
                s.cast.append(dict(slug=pslug, x=0.0, back=False, front=False, flip=False, hidden=False))
        _resolve_actions(s, lib)
        shots.append(s)
        prev = s
    return shots


# =================================================================== actions -> motion
def _resolve_actions(s, lib):
    """Turn each character's action list into timed segments and work out where they end up."""
    s.cast_end = []
    for c in s.cast:
        acts = s.actions.get(c['slug'], [])
        segs = []
        x = c['x']
        for a in acts:
            n, arg, t0 = a['name'], a['arg'], a['t']
            if n in ('enter-left', 'enter-right'):
                segs.append(dict(kind='move', t0=t0 or 0.0, dur=1.1, x0=(-460 if n == 'enter-left' else 460), x1=x, run=False))
            elif n in ('exit-left', 'exit-right'):
                st = t0 if t0 is not None else max(0.0, s.dur - 1.3)
                segs.append(dict(kind='move', t0=st, dur=1.1, x0=x, x1=(-460 if n == 'exit-left' else 460), run=False))
                x = -460 if n == 'exit-left' else 460
            elif n in ('walk-to', 'run-to'):
                if not arg:
                    raise SheetError(f'Row {s.row}: "{n}" needs a place to go, e.g. "{n} right".')
                tx = _pos(arg[0], s.row)
                run = n == 'run-to'
                segs.append(dict(kind='move', t0=t0 or 0.0, dur=0.6 if run else 1.3, x0=x, x1=tx, run=run))
                x = tx
            elif lib.chars[c['slug']]['kind'] == 'prop':
                segs.append(dict(kind='ball', name=n, arg=arg, t0=t0 if t0 is not None else 0.0))
            elif n in RIG.POSES:
                segs.append(dict(kind='pose', name=n, t0=t0 if t0 is not None else 0.0))
            else:
                reps = 1
                for w in arg:
                    if w.startswith('x') and w[1:].isdigit():
                        reps = int(w[1:])
                segs.append(dict(kind=n, t0=t0 if t0 is not None else 0.0, reps=reps))
        # chain moves so later moves start from earlier targets
        c['segs'] = sorted(segs, key=lambda g: g['t0'])
        end = dict(c)
        end['x'] = x
        end.pop('segs', None)
        names = [a['name'] for a in acts]
        if 'appear' in names:
            end['hidden'] = False
        if 'vanish' in names:
            end['hidden'] = True
        if abs(x) >= 400:
            continue
        s.cast_end.append(end)


def char_state(s, c, t, lib):
    """Position and pose of one cast member at shot time t."""
    st = dict(x=c['x'], y=0.0, rot=0.0, sc=1.0, sy=1.0, alpha=0.0 if c.get('hidden') else 1.0, flip=c['flip'],
              moving=False, run=False, dirx=0, shake=0.0, glow=0.0, sleep=False, mood=None, pose=None, offer=0.0,
              hold=None, cry=0.0, hiss=False, poses=[], walk=None)
    moves = [g for g in c.get('segs', []) if g['kind'] == 'move']
    if moves and moves[0]['x0'] in (-460, 460):
        st['x'] = moves[0]['x0']
    for g in moves:
        u = t - g['t0']
        if u < 0:
            break
        p = min(1.0, u / g['dur'])
        st['x'] = P.lerp(g['x0'], g['x1'], P.ss(p) if not g['run'] else p)
        if p < 1:
            st['moving'] = True
            st['run'] = g['run']
            st['dirx'] = 1 if g['x1'] > g['x0'] else -1
            ph = u * (4.5 if g['run'] else 2.6)
            if lib.chars[c['slug']]['kind'] in ('rig', 'layered'):
                st['walk'] = (g['run'], ph / 2)
                st['y'] -= abs(math.sin(ph * math.pi)) * 5
            else:
                st['y'] -= abs(math.sin(ph * math.pi)) * (14 if g['run'] else 9)
                st['rot'] += 3 * math.sin(ph * math.pi)
    for g in c.get('segs', []):
        k = g['kind']
        u = (t - g['t0'])
        if k == 'move':
            continue
        if k == 'pose':
            if lib.chars[c['slug']]['kind'] in ('rig', 'layered'):
                st['poses'].append((g['name'], g['t0']))
            elif u >= 0 and g['name'] in ('cheer', 'six', 'clap', 'arm-dance', 'wave') and u < 2.0:
                st['y'] -= abs(math.sin(u * math.pi * 2.2)) * 16
            continue
        if k == 'ball':
            continue
        if u < 0:
            continue
        if k in ('jump', 'hop'):
            d = 0.62 if k == 'jump' else 0.4
            hgt = 95 if k == 'jump' else 40
            if u < d * g['reps']:
                q = (u % d) / d
                st['y'] -= math.sin(math.pi * q) * hgt
                st['sy'] *= 1 + 0.06 * math.sin(math.pi * q)
                st['pose'] = 'leap'
        elif k in ('shake', 'scared'):
            dd = 1.2 * g['reps'] if g['reps'] > 1 else 1.4
            if u < dd:
                st['shake'] = 1.0 - max(0, u - dd + 0.3) / 0.3
                st['mood'] = 'scared'
                if k == 'scared' and u < 0.35:
                    st['y'] -= math.sin(math.pi * u / 0.35) * 40
        elif k == 'happy':
            st['y'] -= abs(math.sin(u * math.pi * 2.2)) * 18
            st['mood'] = 'happy'
        elif k == 'dance':
            st['y'] -= abs(math.sin(u * math.pi * 2.4)) * 16
            st['rot'] += 7 * math.sin(u * math.pi * 1.2)
            st['mood'] = 'happy'
        elif k == 'spin':
            if u < 0.8 * g['reps']:
                st['sc'] *= math.cos(2 * math.pi * (u % 0.8) / 0.8) if True else 1
        elif k == 'fall':
            q = min(1.0, u / 0.45)
            st['rot'] += 88 * P.ss(q)
            st['y'] += 0
        elif k == 'sleep':
            st['sleep'] = True
        elif k == 'float':
            st['y'] -= 20 + 12 * math.sin(u * 2.4)
        elif k == 'glow':
            st['glow'] = min(1.0, u / 0.5)
        elif k == 'appear':
            st['alpha'] = min(1.0, u / 0.5)
        elif k == 'vanish':
            st['alpha'] = max(0.0, 1 - u / 0.5)
        elif k == 'turn':
            st['flip'] = not st['flip']
        elif k == 'grow':
            st['sc'] *= 1 + 0.5 * P.ss(min(1, u / 0.6))
        elif k == 'shrink':
            st['sc'] *= 1 - 0.5 * P.ss(min(1, u / 0.6))
        elif k in ('sit', 'leap'):
            st['pose'] = k
        elif k == 'hiss':
            st['hiss'] = True
        elif k == 'offer':
            st['offer'] = P.ss(min(1, u / 0.7))
        elif k == 'hold-fish':
            st['hold'] = 'fish'
        elif k == 'hold-sweet':
            st['hold'] = 'sweet'
        elif k == 'cry':
            st['cry'] = min(1, u / 0.5)
    if c['slug'] == 'mechho':
        st['y'] -= 26 + 10 * math.sin(t * 2.2)
    if st['shake']:
        st['x'] += 4 * st['shake'] * math.sin(t * 55)
        st['rot'] += 2 * st['shake'] * math.sin(t * 41)
    return st


# =================================================================== drawing
SIZE = {'rupoli': 0.45, 'chhotu': 0.5, 'gyani': 0.6, 'mishti-card': 0.6, 'bot-dadu': 1.45, 'dhol': 1.05}


def base_scale(c):
    if c['kind'] in ('card', 'rig', 'layered'):
        return 0.64 * SIZE.get(c['slug'], c.get('size_mult', 1.0))
    if c['kind'] == 'prop':
        return 1.0
    return {'mishti': 0.36, 'mechho': 0.82, 'tutul': 0.46}[c['slug']]


def char_height(c):
    if c['kind'] in ('card', 'rig', 'layered'):
        return (605 - c['bbox'][1])
    return c['height']


def _blinks(seed, dur):
    r = random.Random(seed)
    t, out = r.uniform(0.4, 2.0), []
    while t < dur:
        out.append(t)
        t += r.uniform(2.4, 4.8)
    return out


def talk_amount(s, slug, t):
    for v in s.voices:
        if v['speaker'] != slug:
            continue
        u = t - v['start']
        if v['env'] is None:
            if 0 <= u <= v['len']:
                return 0.35 + 0.35 * abs(math.sin(u * 11)) * abs(math.sin(u * 3.3))
            continue
        i = u * FPS
        e = v['env']
        if 0 <= i < len(e) - 1:
            j = int(i)
            val = e[j] * (1 - (i - j)) + e[j + 1] * (i - j)
            return P.clamp((val - 0.08) * 1.5)
    return 0.0


def face_overlay(s, c, t, face, talk, bl):
    e = X.mix(X.auto_expression(s, c['slug'], t, talk))
    gaze = X.gaze_for(s, c['slug'], t, getattr(s, '_positions', {}))
    return X.draw_face(face, e, bl, talk, gaze, t)


def draw_character(lib, s, c, st, t, night):
    info = lib.chars[c['slug']]
    sc = base_scale(info) * st['sc'] * (0.82 if c.get('back') else 1.12 if c.get('front') else 1.0)
    talk = talk_amount(s, c['slug'], t)
    bl = 1.0 if st['sleep'] else P.blinkv(t, _blinks(hash((c['slug'], s.row)) & 0xffff, s.dur + 1), 0.14)
    flip = -1 if st['flip'] else 1
    tn = night * 0.55
    hands = {}
    if info['kind'] == 'prop':
        return '', info['height'], {}
    if info['kind'] == 'rig':
        R_ = RIG.RIGS[c['slug']]
        hdefs, hsvg = lib.rig_head(c['slug'])
        face = info.get('face') or None
        if R_.get('eyes'):
            face = dict(skin=R_['skin'], eyes=R_['eyes'], mouth=list(R_['mouth']))
        pose = RIG.pose_at(R_, c['slug'], st['poses'], t, st['walk'], talk)
        if face:
            face = face_overlay(s, c, t, face, talk, bl)
        if R_.get('auto'):
            body, hl = RIG.draw_auto(R_, hdefs, hsvg, pose, bl, talk, face)
        else:
            body, hl = RIG.draw(R_, hdefs, hsvg, pose, RIG.DEFAULT_PROPS.get(c['slug'], {}), bl, talk, face)
        tx, ty, csc = info['tx'], info['ty'], info['sc']
        body = f'<g transform="translate(-196,-605)"><g transform="translate({tx},{ty}) scale({csc})">{body}</g></g>'
        for side, (hx, hy) in hl.items():
            px, py = tx + hx * csc - 196, ty + hy * csc - 605
            hands[side] = (st['x'] + px * sc * flip, st['y'] + py * sc)
    if info['kind'] == 'card':
        inner = lib.char_svg(c['slug'])
        ov = ''
        f = info.get('face')
        ov_on = False
        if f and len(f.get('eyes', [])) == 2:
            ov = face_overlay(s, c, t, f, talk, bl)
            ov = f'<g transform="translate({info["tx"]},{info["ty"]}) scale({info["sc"]})">{ov}</g>'
        else:
            st['sy'] *= 1 + 0.035 * talk
        body = soft_rig(info, inner + ov, st, t, talk, c, s)
        ov = 'x'
        body = f'<g transform="translate(-196,-605)">{body}</g>'
    elif info['kind'] == 'layered':
        body, hl = draw_layered(info, st, t, talk, c, s)
        for side, (hx, hy) in hl.items():
            hands[side] = (st['x'] + (hx - 196) * sc * flip, st['y'] + (hy - 605) * sc)
        body = f'<g transform="translate(-196,-605)">{body}</g>'
    elif info['kind'] == 'puppet':
        body = P.ids(_puppet(c['slug'], st, t, talk, bl))
    if tn > 0:
        key = (body if info['kind'] != 'card' else None)
        if info['kind'] == 'card' and not ov:
            ck = ('tint', c['slug'], round(tn, 3))
            if ck not in lib._svg:
                lib._svg[ck] = P.tint(body, tn, 0)
            body = lib._svg[ck]
        else:
            body = P.tint(body, tn, 0)
    h = char_height(info) * sc
    x = st['x']
    y = st['y']
    shadow = f'<ellipse cx="0" cy="2" rx="{70 * sc / 0.7:.1f}" ry="{9 * sc / 0.7:.1f}" fill="#1C1410" opacity="{0.22 * st["alpha"]:.2f}" stroke="none"/>' if c['slug'] != 'mechho' else ''
    glow = ''
    if st['glow'] > 0:
        glow = (f'<defs><radialGradient id="gl{id(c)}"><stop offset="0" stop-color="#FFC94A" stop-opacity="0.75"/><stop offset="1" stop-color="#FFC94A" stop-opacity="0"/></radialGradient></defs>'
                f'<ellipse cx="0" cy="{-h * 0.5:.1f}" rx="{h * 0.55:.1f}" ry="{h * 0.62:.1f}" fill="url(#gl{id(c)})" opacity="{st["glow"]:.2f}" stroke="none"/>')
    return (f'<g transform="translate({x:.1f},0)">{shadow}</g>'
            f'<g transform="translate({x:.1f},{y:.1f})" opacity="{st["alpha"]:.2f}">{glow}'
            f'<g transform="rotate({st["rot"]:.2f}) scale({sc * flip:.3f},{sc * st["sy"]:.3f})">{body}</g></g>'), h, hands


def _puppet(slug, st, t, talk, bl):
    if slug == 'mishti':
        pose = 'run' if st['moving'] else (st['pose'] if st['pose'] in ('leap', 'sit') else 'sit')
        if st['pose'] == 'leap':
            pose = 'leap'
        mouth = 'hiss' if st['hiss'] else ('meow' if talk > 0.1 else 'none')
        eo = 0.0 if st['sleep'] else (1.0 if st['mood'] == 'scared' else 0.45) * (1 - bl)
        g = P.mishti(t, eo, (0, 0), 3.0, 0, mouth, talk, 8 * math.sin(t * 2), t * 20, pose, t * 3)
        if pose != 'sit' and st['dirx'] > 0:
            g = f'<g transform="scale(-1,1)">{g}</g>'
        return g
    if slug == 'mechho':
        mood = 'scared' if st['mood'] == 'scared' else ('happy' if st['mood'] == 'happy' else 'hungry')
        mouth = 'talk' if talk > 0.1 else ('scream' if mood == 'scared' else 'grin')
        g = P.mechho(t, mood, (0, 0), mouth, talk, rattle=3.0 if st['shake'] else 0.6, holding=st['hold'] or 'none',
                     sweet_p=1.0, tears=st['cry'], glow=st['glow'], eye_o=0.0 if st['sleep'] else 1.0 - bl)
        return f'<g transform="translate(0,-150)">{g}</g>'
    if slug == 'tutul':
        mouth = 'talk' if talk > 0.1 else ('smile' if st['mood'] == 'happy' else 'o' if st['mood'] == 'scared' else 'smile')
        eo = 0.0 if st['sleep'] else 0.6 * (1 - bl)
        return P.tutul_full(t, eo, (0, -4), mouth, talk, offer=st['offer'], step=t * 2.6 if st['moving'] else 0)
    return ''


EMOTE_SVG = {
    '!': '<circle cx="0" cy="-36" r="26" fill="#FBF5E9"/><path d="M-5 -54 L5 -54 L3 -30 L-3 -30Z" fill="#C8341F" stroke-width="2"/><circle cx="0" cy="-20" r="4" fill="#C8341F" stroke="none"/>',
    '?': '<circle cx="0" cy="-36" r="26" fill="#FBF5E9"/><path d="M-8 -44 Q-8 -54 0 -54 Q9 -54 9 -46 Q9 -38 1 -35 L1 -27" fill="none" stroke="#2C3E8C" stroke-width="5"/><circle cx="1" cy="-17" r="3.5" fill="#2C3E8C"/>',
    'heart': '<path d="M0 -8 Q-30 -30 -18 -48 Q-6 -60 0 -44 Q6 -60 18 -48 Q30 -30 0 -8Z" fill="#E58BA0"/>',
    'zzz': '<text x="-6" y="-20" font-family="Rozha One" font-size="30" fill="#FBF5E9" stroke="#1C1410" stroke-width="2" paint-order="stroke">z</text><text x="12" y="-44" font-family="Rozha One" font-size="22" fill="#FBF5E9" stroke="#1C1410" stroke-width="2" paint-order="stroke">z</text><text x="26" y="-62" font-family="Rozha One" font-size="16" fill="#FBF5E9" stroke="#1C1410" stroke-width="2" paint-order="stroke">z</text>',
    'sweat': '<path d="M28 -40 Q40 -20 32 -12 Q22 -8 22 -20 Q22 -30 28 -40Z" fill="#BFE3EE"/>',
    'anger': '<path d="M-14 -40 Q-4 -36 -6 -26 M14 -40 Q4 -36 6 -26 M-14 -14 Q-4 -18 -6 -28 M14 -14 Q4 -18 6 -28" fill="none" stroke="#C8341F" stroke-width="6"/>',
    'idea': '<circle cx="0" cy="-40" r="18" fill="#FFC94A"/><rect x="-8" y="-24" width="16" height="10" fill="#8C8C9A"/><path d="M-30 -40 L-38 -40 M30 -40 L38 -40 M0 -66 L0 -74 M-22 -60 L-28 -66 M22 -60 L28 -66" stroke="#FFC94A" stroke-width="4"/>',
    'music': '<path d="M-14 -16 L-14 -50 L12 -56 L12 -22" fill="none" stroke-width="4"/><ellipse cx="-19" cy="-16" rx="7" ry="5" fill="#1C1410"/><ellipse cx="7" cy="-22" rx="7" ry="5" fill="#1C1410"/>',
    'sparkle': '<path d="M0 -60 L5 -42 L22 -36 L5 -30 L0 -12 L-5 -30 L-22 -36 L-5 -42Z" fill="#FFC94A"/><path d="M26 -62 L28 -56 L34 -54 L28 -52 L26 -46 L24 -52 L18 -54 L24 -56Z" fill="#FBF5E9"/>',
    'shock': '<path d="M-34 -10 L-50 -26 M-38 -36 L-58 -44 M34 -10 L50 -26 M38 -36 L58 -44 M0 -50 L0 -70" fill="none" stroke="#1C1410" stroke-width="5"/>',
}


def draw_emote(kind, x, y, u):
    if u < 0 or u > 1.8:
        return ''
    a = P.clamp(u / 0.15)
    pop = 1 + 0.25 * math.sin(math.pi * P.clamp(u / 0.3)) if u < 0.3 else 1.0
    fade = 1 - P.clamp((u - 1.5) / 0.3)
    bob = -4 * math.sin(u * 5)
    return (f'<g transform="translate({x:.1f},{y + bob:.1f}) scale({a * pop:.2f})" opacity="{fade:.2f}">'
            f'<g stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{EMOTE_SVG[kind]}</g></g>')


# ---------------------------------------------------------------- places
def place_world(lib, s):
    """Returns (svg_back, svg_front, xmin, xmax, floor_y) in world units (height 960)."""
    night = {'day': 0.0, 'evening': 0.25, 'night': 0.55}[s.time]
    warm = 0.12 if s.time == 'evening' else 0.0
    if s.place_kind == 'image':
        ext = os.path.splitext(s.image)[1].lower()
        if ext == '.svg':
            raw = open(s.image, encoding='utf-8').read()
            vb = re.search(r'viewBox="([-0-9. ]+)"', raw)
            w, h = (float(v) for v in vb.group(1).split()[2:4]) if vb else (1600.0, 900.0)
            inner = re.sub(r'^.*?<svg[^>]*>', '', raw, flags=re.S)
            inner = inner[:inner.rfind('</svg>')]
        else:
            from PIL import Image
            import base64
            im = Image.open(s.image)
            w, h = im.size
            data = base64.b64encode(open(s.image, 'rb').read()).decode()
            mime = 'image/png' if ext == '.png' else 'image/jpeg'
            inner = f'<image width="{w}" height="{h}" href="data:{mime};base64,{data}"/>'
        k = H / h
        back = f'<g transform="scale({k:.4f})">{inner}</g>'
        return P.tint(back, night * 0.6, warm), '', 0, w * k, H * 0.9
    p = lib.places[s.place]
    kind = p['kind']
    if kind == 'tile':
        k = H / p['h']
        back = f'<g transform="scale({k:.4f})">{lib.place_svg(s.place)}</g>'
        return P.tint(back, night, warm), '', 0, p['w'] * k, H * p['floor']
    if kind == 'set' and s.place == 'sen-kitchen-night':
        n = max(night, 0.5)
        bg = SETS.kitchen_room(n)
        fr, spill = SETS.fridge(0.0, True, 'full', night=n, light=1.0, t=0)
        ck = SETS.cooker(150, 604, 0, 0, night=n * 0.9)
        return bg + ck + fr + spill, '', -200, 820, H * p['floor']
    if kind == 'set' and s.place == 'stairwell':
        return SETS.stairs_bg(max(night, 0.45), 1.0, 0) + SETS.stairs_steps(), SETS.stairs_rail(), -260, 900, SETS.LAND_Y
    return '', '', 0, W, H * 0.9


def title_card(s, t):
    parts = [p.strip() for p in s.subtitle.split('|')]
    a = P.clamp(t / 0.6)
    out = ('<defs><pattern id="tt-pat" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="#22305F"/>'
           '<path d="M30 8 Q42 22 30 36 Q18 22 30 8Z" fill="none" stroke="#2C3E8C" stroke-width="3"/><circle cx="30" cy="48" r="3" fill="#2C3E8C"/></pattern></defs>'
           '<rect width="540" height="960" fill="url(#tt-pat)"/>'
           '<circle cx="270" cy="440" r="220" fill="#FFC94A" opacity="0.10"/>')
    y = 430
    for i, p in enumerate(parts[:3]):
        bn = bool(re.search('[ঀ-৿]', p))
        fs = 58 if i == 0 else 30
        fam = 'Hind Siliguri' if bn else 'Rozha One'
        col = '#FBF5E9' if i == 0 else '#E3A92B'
        lines = wrap(p, 14 if i == 0 else 26)
        for ln in lines:
            out += (f'<text x="270" y="{y}" text-anchor="middle" font-family="{fam}" font-weight="700" font-size="{fs}" fill="{col}" '
                    f'stroke="#1C1410" stroke-width="2.4" paint-order="stroke" opacity="{a:.2f}">{esc(ln)}</text>')
            y += fs * 1.15
        y += 12
    return out


# ---------------------------------------------------------------- captions
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def wrap(text, n):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines


def caption(s, t):
    if not s.subtitle or s.place_kind == 'title':
        return ''
    text = s.subtitle
    top = text.startswith('^')
    text = text.lstrip('^').strip()
    parts = [p.strip() for p in text.split('|') if p.strip()]
    if s.voices and s.voices[0]['len']:
        a = s.voices[0]['start']
        b = s.voices[-1]['start'] + s.voices[-1]['len'] + 0.25
    else:
        a, b = 0.15, s.dur - 0.1
    if not (a <= t <= b):
        return ''
    tot = sum(len(p) for p in parts) or 1
    acc = a
    cur = parts[-1]
    for p in parts:
        span = (b - a) * len(p) / tot
        if t < acc + span:
            cur = p
            break
        acc += span
    bn = bool(re.search('[ঀ-৿]', cur))
    fam = 'Hind Siliguri' if bn else 'Inter'
    lines = wrap(cur, 22 if bn else 24)[:3]
    fs = 32
    y0 = 820 - (len(lines) - 1) * fs * 1.15 if top else 250
    out = ''
    for i, ln in enumerate(lines):
        out += (f'<text x="270" y="{y0 + i * fs * 1.15:.1f}" text-anchor="middle" font-family="{fam}" font-weight="700" font-size="{fs}" '
                f'fill="#FFFFFF" stroke="#101010" stroke-width="2.6" stroke-linejoin="round" paint-order="stroke">{esc(ln)}</text>')
    return out


# ---------------------------------------------------------------- camera
def camera(s, t, lib, world, positions):
    _, _, xmin, xmax, floor = world
    span = xmax - xmin
    v = s.view
    if v in ('left', 'center', 'centre', 'right'):
        x0 = {'left': xmin + 270, 'center': (xmin + xmax) / 2, 'centre': (xmin + xmax) / 2, 'right': xmax - 270}[v]
    else:
        try:
            x0 = P.lerp(xmin + 270, xmax - 270, P.clamp(float(v.rstrip('%')) / 100))
        except ValueError:
            x0 = (xmin + xmax) / 2
    if s.place_kind == 'set':
        x0 = 270 if v == 'center' else x0
    s.x0 = x0
    fx, fy, fh = x0, floor, 360
    if s.focus and s.focus in positions:
        fx, fy, fh = positions[s.focus]
    u = P.ss(t / max(s.dur, 0.01))
    mode = s.camera
    if mode == 'auto':
        mode = 'medium' if (s.voices and s.voices[0]['speaker'] and len(s.cast) > 1) else 'wide'
    gx = sum(p[0] for p in positions.values()) / len(positions) if positions else fx
    hmax = max([p[2] for p in positions.values()] + [300])
    wz = max(1.0, min(1.45, 960 * 0.5 / max(hmax, 1)))
    wide = (x0, floor - (0.86 - 0.5) * 960 / wz, wz)
    xs = [p[0] for p in positions.values()]
    spread = (max(xs) - min(xs)) if xs else 0
    zm = 1.32 if spread * 1.32 < 380 else max(1.0, 380 / max(spread, 1))
    med = ((gx if spread * zm < 380 else P.lerp(gx, fx, 0.55)), fy - fh * 0.5, zm)
    close = (fx, fy - fh * 0.8, 2.2)
    if mode == 'wide':
        c = wide
    elif mode == 'medium':
        c = med
    elif mode == 'close':
        c = close
    elif mode == 'follow':
        c = (fx, fy - fh * 0.55, 1.3)
    elif mode == 'ball':
        bx, by, _ = positions.get('ball') or positions.get(s.focus) or (fx, fy, 0)
        c = (bx, by - 200, 1.1)
    elif mode == 'push-in':
        c = tuple(P.lerp(a, b, u) for a, b in zip(wide, med))
    elif mode == 'pull-out':
        c = tuple(P.lerp(a, b, u) for a, b in zip(med, wide))
    elif mode == 'pan-left':
        c = (P.lerp(x0 + 170, x0 - 170, u), 480, 1.0)
    elif mode == 'pan-right':
        c = (P.lerp(x0 - 170, x0 + 170, u), 480, 1.0)
    else:
        c = wide
    cx, cy, z = c
    hw, hh = 270 / z, 480 / z
    cx = min(max(cx, xmin + hw), xmax - hw) if xmax - xmin > 2 * hw else (xmin + xmax) / 2
    cy = min(max(cy, hh), H - hh)
    if s.cam_shake:
        cx += 5 * math.sin(t * 47) / z
        cy += 5 * math.cos(t * 39) / z
    return cx, cy, z


def vignette(strength=0.55):
    return ('<defs><radialGradient id="vg" cx="50%" cy="45%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="100%" stop-color="#05070F" stop-opacity="{strength:.2f}"/></radialGradient></defs>'
            '<rect width="540" height="960" fill="url(#vg)"/>')


def _sw(m):
    return f'stroke-width="{float(m.group(1)) * K:.1f}"'


def finalize(body, px_w=1080, px_h=1920):
    body = re.sub(r'stroke-width="([0-9.]+)"', _sw, body)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px_w}" height="{px_h}" viewBox="0 0 540 960">'
            f'<style>.k path,.k circle,.k ellipse,.k rect,.k line,.k polygon{{vector-effect:non-scaling-stroke}}</style>'
            f'<rect width="540" height="960" fill="#0E1226"/><g class="k">{body}</g></svg>')


# =================================================================== frames
class Movie:
    def __init__(self, shots, lib):
        self.shots = shots
        self.lib = lib
        self.total = sum(s.dur for s in shots)
        self.nframes = int(round(self.total * FPS))
        self._world = {}

    def shot_at(self, T):
        for i, s in enumerate(self.shots):
            if T < s.start + s.dur or i == len(self.shots) - 1:
                return i, s
        return len(self.shots) - 1, self.shots[-1]

    def world(self, s):
        if s.row not in self._world:
            self._world[s.row] = place_world(self.lib, s)
        return self._world[s.row]

    def frame_svg(self, f, px_w=1080, px_h=1920):
        P.reset_uid()
        T = f / FPS
        i, s = self.shot_at(T)
        t = T - s.start
        if s.place_kind == 'title':
            body = title_card(s, t)
        else:
            body = self.scene(s, t)
        body += vignette(0.55)
        body += caption(s, t)
        fade = 0.0
        if s.transition in ('fade', 'dip') and t < 0.35:
            fade = 1 - t / 0.35
        if i + 1 < len(self.shots) and self.shots[i + 1].transition in ('fade', 'dip') and s.dur - t < 0.35:
            fade = max(fade, 1 - (s.dur - t) / 0.35)
        if i == 0 and t < 0.3:
            fade = max(fade, 1 - t / 0.3)
        if i == len(self.shots) - 1 and s.dur - t < 0.5:
            fade = max(fade, 1 - (s.dur - t) / 0.5)
        if fade > 0:
            body += f'<rect width="540" height="960" fill="#000" opacity="{fade:.3f}"/>'
        return finalize(body, px_w, px_h)

    def scene(self, s, t):
        lib = self.lib
        world = self.world(s)
        back, front, xmin, xmax, floor = world
        night = {'day': 0.0, 'evening': 0.15, 'night': 0.5}[s.time]
        # first pass: positions for camera focus
        states, positions = [], {}
        cam0x = None
        for c in s.cast:
            st = char_state(s, c, t, lib)
            states.append((c, st))
        cx0 = None
        # characters stand relative to the view centre
        tmp = camera(s, 0, lib, world, {})
        base_x = s.x0
        for c, st in states:
            info = lib.chars[c['slug']]
            sc = base_scale(info) * (0.82 if c.get('back') else 1.12 if c.get('front') else 1.0)
            positions[c['slug']] = (base_x + st['x'], self._feet(s, c, floor), char_height(info) * sc)
        s._positions = positions
        stage = ''
        emotes = ''
        all_hands = {}
        order = sorted(states, key=lambda cs: (0 if cs[0].get('back') else 2 if cs[0].get('front') else 1))
        for c, st in order:
            fx, fy, _ = positions[c['slug']]
            if s.place == 'stairwell':
                fy = SETS.stair_y(base_x + st['x'])
            if lib.chars[c['slug']]['kind'] == 'prop':
                continue
            g, h, hands = draw_character(lib, s, c, st, t, night)
            stage += f'<g transform="translate({base_x:.1f},{fy:.1f})">{g}</g>'
            all_hands[c['slug']] = {k: (base_x + v[0], fy + v[1]) for k, v in hands.items()}
            all_hands[c['slug']]['_body'] = (base_x + st['x'], fy + st['y'] - h * 0.55, h)
            for e in s.emotes:
                if e['slug'] == c['slug']:
                    emotes += draw_emote(e['kind'], base_x + st['x'] + h * 0.22, fy + st['y'] - h * 0.98, t - e['t'])
            if st['sleep']:
                emotes += draw_emote('zzz', base_x + st['x'] + h * 0.2, fy + st['y'] - h * 0.95, 0.5 + (t % 1.0) * 0.0)
        ball = ''
        props_back = ''
        for c, st in states:
            info = lib.chars[c['slug']]
            if info['kind'] == 'prop':
                fy = self._feet(s, c, floor)
                bp = ball_pos(s, c, t, all_hands, base_x, fy, info)
                if bp:
                    positions[c['slug']] = (bp[0], bp[1] + 200, 400)
                    g = draw_ball(s, c, t, all_hands, base_x, fy, info, night)
                    if any(x['kind'] == 'ball' for x in c.get('segs', [])) and not c.get('back'):
                        ball += g
                    else:
                        props_back += g
        cx, cy, z = camera(s, t, lib, world, positions)
        cam = f'translate(270,480) scale({z:.4f}) translate({-cx:.2f},{-cy:.2f})'
        return f'<g transform="{cam}">{back}{props_back}{stage}{ball}{front}{emotes}</g>'

    def _feet(self, s, c, floor):
        y = floor
        if c.get('back'):
            y -= 40
        if c.get('front'):
            y += 30
        if s.place == 'stairwell':
            y = SETS.LAND_Y
        return y


# =================================================================== objects (ball, bat, stumps, anything in library/props)
def _hand(all_hands, who, floor, base_x, side='r'):
    h = all_hands.get(who, {})
    if side in h:
        return h[side]
    if 'r' in h:
        return h['r']
    if '_body' in h:
        return (h['_body'][0] + 20, h['_body'][1])
    return (base_x, floor - 120)


def _rest(info, floor, x):
    k = info['height'] / info['native_h']
    return (x, floor - info.get('rest_dy', info['native_h'] / 2) * k)


def _ball_seg_pos(segs, i, t, all_hands, base_x, floor, x_rest, info):
    g = segs[i]
    u = t - g['t0']

    def start():
        return _ball_seg_pos(segs, i - 1, g['t0'], all_hands, base_x, floor, x_rest, info) if i > 0 else _rest(info, floor, x_rest)
    n = g['name']
    side = 'l' if 'left' in g['arg'] else 'r'
    if n == 'in-hand':
        x, y = _hand(all_hands, g['arg'][0], floor, base_x, side)
        return (x, y - 4)
    if n in ('bowl', 'throw'):
        a = _hand(all_hands, g['arg'][0], floor, base_x)
        bh = all_hands.get(g['arg'][1], {}).get('_body', (base_x, floor - 120, 200))
        if n == 'throw':
            tgt = _hand(all_hands, g['arg'][1], floor, base_x)
            k = min(1.0, u / 0.7)
            q = k
            return (a[0] + (tgt[0] - a[0]) * q, a[1] + (tgt[1] - a[1]) * q - 160 * math.sin(math.pi * q))
        tgt = (bh[0] + 14, floor - bh[2] * 0.32)
        bounce = (a[0] + (tgt[0] - a[0]) * 0.72, floor - 4)
        k = min(1.0, u / 0.62)
        if k < 0.72:
            q = k / 0.72
            return (a[0] + (bounce[0] - a[0]) * q, a[1] + (bounce[1] - a[1]) * q * q - 30 * math.sin(math.pi * q) * (1 - q))
        q = (k - 0.72) / 0.28
        return (bounce[0] + (tgt[0] - bounce[0]) * q, bounce[1] + (tgt[1] - bounce[1]) * q - 20 * math.sin(math.pi * q))
    if n in ('hit-up', 'hit-left', 'hit-right'):
        p0 = start()
        k = min(1.4, u / 1.0)
        if n == 'hit-up':
            return (p0[0] + 300 * k, p0[1] - 1600 * k + 300 * k * k)
        d = -1 if n == 'hit-left' else 1
        return (p0[0] + d * 900 * k, min(floor - 6, p0[1] + (floor - 6 - p0[1]) * min(1, k * 3)) - 30 * abs(math.sin(k * 9)) * (1 - k))
    if n == 'fly-in':
        tgt = _hand(all_hands, g['arg'][0], floor, base_x, side)
        k = min(1.0, u / 0.7)
        p0 = (tgt[0] - 320, -260)
        q = k * k * (3 - 2 * k)
        return (p0[0] + (tgt[0] - p0[0]) * q, p0[1] + (tgt[1] - 6 - p0[1]) * q - 120 * math.sin(math.pi * q))
    if n == 'drop':
        p0 = start()
        rest = _rest(info, floor, p0[0] + 30)
        k = min(1.0, u / 0.6)
        return (p0[0] + 30 * k, p0[1] + (rest[1] - p0[1]) * k * k)
    if n == 'bounce':
        p0 = start()
        return (p0[0], p0[1] - abs(math.sin(u * 5)) * 40 * max(0, 1 - u / 3))
    return start()


def ball_pos(s, c, t, all_hands, base_x, floor, info):
    segs = sorted([g for g in c.get('segs', []) if g['kind'] == 'ball' and g['name'] not in ('spin', 'swing', 'appear', 'vanish')], key=lambda g: g['t0'])
    idx = [i for i, g in enumerate(segs) if g['t0'] <= t]
    x_rest = base_x + c['x']
    if not idx:
        if segs and segs[0]['name'] == 'in-hand':
            return _ball_seg_pos(segs, 0, segs[0]['t0'], all_hands, base_x, floor, x_rest, info)
        if segs and segs[0]['name'] in ('bowl', 'throw'):
            return _hand(all_hands, segs[0]['arg'][0], floor, base_x)
        if segs and segs[0]['name'] == 'fly-in':
            return None
        return _rest(info, floor, x_rest)
    return _ball_seg_pos(segs, idx[-1], t, all_hands, base_x, floor, x_rest, info)


def _prop_extra(c, t):
    rot, alpha = 0.0, 0.0 if c.get('hidden') else 1.0
    flying = False
    for g in c.get('segs', []):
        u = t - g['t0']
        if g['kind'] != 'ball' or u < 0:
            continue
        if g['name'] == 'spin':
            rot = u * 540
        elif g['name'] == 'swing':
            rot = 22 * math.sin(u * 3.5)
        elif g['name'] == 'appear':
            alpha = min(1.0, u / 0.3)
        elif g['name'] == 'vanish':
            alpha = max(0.0, 1 - u / 0.3)
        elif g['name'] in ('bowl', 'throw', 'hit-up', 'hit-left', 'hit-right', 'fly-in'):
            flying = u < 1.2
    return rot, alpha, flying


def draw_ball(s, c, t, all_hands, base_x, floor, info, night=0.0):
    p = ball_pos(s, c, t, all_hands, base_x, floor, info)
    if not p:
        return ''
    rot, alpha, flying = _prop_extra(c, t)
    k = info['height'] / info['native_h'] * (0.82 if c.get('back') else 1.0)
    gx, gy = info.get('grip', (0, 0))
    body = info['svg'] if not night else P.tint(info['svg'], night * 0.55, 0)
    if flying:
        rot += t * 900
    out = ''
    if flying:
        for j in (3, 2, 1):
            q = ball_pos(s, c, t - 0.025 * j, all_hands, base_x, floor, info)
            if q and math.hypot(q[0] - p[0], q[1] - p[1]) > 6:
                out += (f'<g transform="translate({q[0]:.1f},{q[1]:.1f}) scale({k:.4f}) translate({-gx:.1f},{-gy:.1f})" opacity="{0.3 - 0.07 * j:.2f}">{body}</g>')
    if c['slug'] == 'ball':
        out += f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="13" fill="#FFF3C4" opacity="{0.35 * alpha:.2f}" stroke="none"/>'
    out += (f'<g transform="translate({p[0]:.1f},{p[1]:.1f}) rotate({rot % 360:.1f}) scale({k:.4f}) translate({-gx:.1f},{-gy:.1f})" opacity="{alpha:.2f}">'
            f'<g stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">{body}</g></g>')
    return out


# =================================================================== automatic rigs for art without separate limbs
NECK = {'mishti-card': 0.45, 'bagha': 0.44, 'gyani': 0.42, 'chhotu': 0.5, 'dhol': 0.44, 'kumir': 0.34, 'petni': 0.3, 'tutul-card': 0.4}
SWAY_ONLY = {'rupoli', 'bot-dadu', 'jol-konya'}
_sid = [0]


def soft_rig(info, body, st, t, talk, c, s):
    """Flat picture: split at the neck so the head nods, tilts and talks; the body breathes and leans."""
    slug = c['slug']
    top = info['bbox'][1]
    hgt = 605 - top
    nod = 2.5 * math.sin(t * 1.1 + len(slug)) + 5 * talk * math.sin(t * 9)
    pose_names = [p[0] for p in st.get('poses', [])]
    e = X.mix(X.auto_expression(s, slug, t, talk))
    nod += 6 * e.get('tilt', 0)
    if st.get('mood') == 'happy' or any(n in ('cheer', 'six', 'clap', 'arm-dance') for n in pose_names):
        nod += 4 * math.sin(t * 7)
    breathe = 1 + 0.012 * math.sin(t * 2.0)
    if slug in SWAY_ONLY or info.get('neck') == 'none':
        sk = 4 * math.sin(t * (3.2 if slug == 'rupoli' else 1.3))
        return f'<g transform="translate(196,605) skewX({sk:.2f}) scale(1,{breathe:.4f}) translate(-196,-605)">{body}</g>'
    if info.get('face'):
        neck = info['ty'] + info['face']['chin'] * info['sc'] + 4
    else:
        frac = info.get('neck') if isinstance(info.get('neck'), (int, float)) else NECK.get(slug, 0.3)
        neck = top + hgt * frac
    _sid[0] += 1
    cb, ch = f'sb{_sid[0]}', f'sh{_sid[0]}'
    cx = (info['bbox'][0] + info['bbox'][2]) / 2
    clip = (f'<defs><clipPath id="{cb}"><rect x="-600" y="{neck - 3:.1f}" width="1600" height="2000"/></clipPath>'
            f'<clipPath id="{ch}"><rect x="-600" y="-1400" width="1600" height="{neck + 1408:.1f}"/></clipPath></defs>')
    return (clip + f'<g transform="translate(196,605) scale(1,{breathe:.4f}) translate(-196,-605)"><g clip-path="url(#{cb})">{body}</g></g>'
            f'<g transform="translate(0,{(1 - breathe) * (605 - neck):.2f}) rotate({nod:.2f} {cx:.1f} {neck:.1f})"><g clip-path="url(#{ch})">{body}</g></g>')


def draw_layered(info, st, t, talk, c, s):
    """A character drawn in named parts: arms and legs turn at their joints, the head turns at the neck."""
    L = info['layered']
    W = info['wrap']
    k, wcx, wby = W['k'], W['cx'], W['by']

    def to_card(p):
        return (196 + (p[0] - wcx) * k, 605 + (p[1] - wby) * k)
    parts = L['parts']
    al, ar = parts.get('arm-left'), parts.get('arm-right')
    head = parts.get('head')
    R_ = dict(chin=to_card(head['pivot'])[1] if head else 300, sy=(to_card(head['pivot'])[1] + 12) if head else 312)
    lp = to_card(al['pivot']) if al else (160, 330)
    rp = to_card(ar['pivot']) if ar else (232, 330)
    alen = (math.dist(al['pivot'], al['tip']) * k) if al else 130
    R_['sh'] = (lp, rp)
    R_['L1'] = R_['L2'] = alen / 2
    legs = [parts.get('leg-left'), parts.get('leg-right')]
    R_['hip'] = to_card(legs[0]['pivot'])[1] if legs[0] else 440
    R_['feet'] = 605
    pose = RIG.pose_at(R_, c['slug'], st.get('poses', []), t, st.get('walk'), talk)
    e = X.mix(X.auto_expression(s, c['slug'], t, talk))
    out = {}
    hands = {}
    for name, p in parts.items():
        piv = p['pivot']
        ang = 0.0
        if name in ('arm-left', 'arm-right'):
            key = 'lh' if name == 'arm-left' else 'rh'
            tgt = pose.get(key)
            pc = to_card(piv)
            tip = to_card(p['tip'])
            rest_a = math.atan2(tip[1] - pc[1], tip[0] - pc[0])
            if tgt:
                ang = math.degrees(math.atan2(tgt[1] - pc[1], tgt[0] - pc[0]) - rest_a)
                ang = (ang + 180) % 360 - 180
            a = rest_a + math.radians(ang)
            hands['l' if name == 'arm-left' else 'r'] = (pc[0] + alen * math.cos(a), pc[1] + alen * math.sin(a))
        elif name in ('leg-left', 'leg-right'):
            lift = pose.get('lf_lift' if name == 'leg-left' else 'rf_lift', 0.0)
            ang = (1 if name == 'leg-left' else -1) * lift * 0.9
        elif name == 'head':
            ang = pose.get('head', 0.0) + 6 * e.get('tilt', 0) + 4 * talk * math.sin(t * 9)
        out[name] = f'<g transform="rotate({ang:.2f} {piv[0]:.1f} {piv[1]:.1f})">{p["svg"]}</g>'
    order = ['leg-left', 'leg-right', 'arm-left', 'body', 'torso', 'head', 'arm-right']
    inner = L['rest'] + ''.join(out.get(n, '') for n in order)
    dy = pose.get('dy', 0.0)
    svg = f'<g transform="translate(0,{dy:.1f}) translate(196,605) scale({k:.5f}) translate({-wcx:.2f},{-wby:.2f})">{inner}</g>'
    return svg, hands
