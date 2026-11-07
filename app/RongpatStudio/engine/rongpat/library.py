"""The character and place library.

The app reads its cast and places from folders, never from inside the code, so the bible can grow or change:

  RongpatStudio/engine/assets/        the built-in library (bible as shipped)
  RongpatStudio/library/characters/   YOUR characters: .svg or transparent .png (+ optional .json with name, size, skin)
  RongpatStudio/library/places/       YOUR places: .svg, .png or .jpg (+ optional .json with name, floor)
  RongpatStudio/library/bible-import/ drop bible board files (.dc.html / .html) here and run "Update Library"

Anything in library/ with the same name as a built-in one replaces it.
"""
import io, json, os, re, html

INK = '#1C1410'
CARD_FEET = (196, 605)
EYE = re.compile(r'<path d="M([0-9.]+) ([0-9.]+) Q([0-9.]+) ([0-9.]+) ([0-9.]+) ([0-9.]+) Q[0-9. ]+Z" fill="#FBF5E9" stroke-width="3"/>')
FACE = re.compile(r'<ellipse cx="196" cy="(1[4-9][0-9])" rx="([4-7][0-9])" ry="([5-8][0-9])" fill="(#[0-9A-Fa-f]{6})"/>')
SIZES = {'adult': 475, 'tall': 520, 'kid': 350, 'small-kid': 300, 'big-animal': 470, 'animal': 300, 'small-animal': 180}


KNOWN_CHARS = {'Tuli': 'tuli', 'Ronju': 'ronju', 'Khema Dida': 'dida', 'Pupu': 'pupu', 'Inspector Moyna': 'moyna', 'Professor Ghontu': 'ghontu',
               'Bhombol': 'bhombol', 'Kalo Megh': 'kalo-megh', 'Shubho': 'shubho', 'Rini': 'rini', 'Baba': 'baba', 'Ma': 'ma', 'Mitul': 'mitul',
               'Babai': 'babai', 'Jhumpa': 'jhumpa', 'Tutul': 'tutul-card', 'Mishti': 'mishti-card', 'Bagha': 'bagha', 'Gyani': 'gyani',
               'Chhotu': 'chhotu', 'Rupoli': 'rupoli', 'Shiyal Pandit': 'shiyal', 'Dhol': 'dhol', 'Kumir Babu': 'kumir', 'Mechho Bhoot': 'mechho-card',
               'Petni Pori': 'petni', 'Bot-Dadu': 'bot-dadu', 'Jol-Konya': 'jol-konya', 'Anko Sir': 'anko-sir', 'Mitali Bose': 'mitali',
               'Ghonta-da': 'ghonta-da', 'Robin Sardar': 'robin', 'Montu-da': 'montu', 'Kashem Mia': 'kashem', 'Bablu Ustad': 'bablu', 'Pintu': 'pintu',
               'Dr. Ruksana Ahmed': 'dr-ruksana', 'Sister Shefali': 'shefali', 'Havildar Gopal Dhar': 'gopal', 'Haridas the postman': 'haridas'}
KNOWN_PLACES = {'ma-amp-babas-bedroom': 'parents-bedroom', 'ma-babas-bedroom': 'parents-bedroom', 'river-ghat-amp-pavilion': 'river-ghat',
                'river-ghat-pavilion': 'river-ghat', 'front-gate': 'school-gate', 'playground': 'school-playground', 'classroom': 'school-classroom',
                'corridor': 'school-corridor', 'teachers-room': 'school-teachers-room', 'science-lab': 'school-science-lab',
                'the-classroom': 'old-classroom', 'the-newlyweds-flat': 'newlyweds-flat', 'the-kitchen': 'home-kitchen',
                'the-sen-house': 'sen-house-outside', 'the-living-room': 'living-room', 'the-courtyard': 'courtyard'}
SKIP_CHARS = {'mechho-card'}
EXTRAS = {   # bits of card backdrop art that should not follow a character into a scene
    'mishti-card': [r'<circle cx="300" cy="92" r="28" fill="#F3E6C8"/>', r'<circle cx="314" cy="82" r="25" fill="#22305F"/>'],
    'kalo-megh': [r'<circle cx="290" cy="98" r="36" fill="#C8341F"/>'],
    'chhotu': [r'<path d="M226 64 Q226 30 290 30[^"]*" fill="#FBF5E9" stroke-width="3"/>', r'<text x="290" y="72"[^>]*>[^<]*</text>'],
    'bagha': [r'<g fill="#8C8C9A"><circle cx="302" cy="62" r="18"/><circle cx="324" cy="54" r="22"/><circle cx="346" cy="64" r="16"/></g>',
              r'<path d="M322 78 L310 102 L322 100 L312 124 L334 94 L322 96 L330 78Z" fill="#E3A92B" stroke-width="3"/>'],
}        # the animated Mechho puppet is used instead


def slugify(s):
    s = html.unescape(s).replace('’', '').replace("'", '').lower()
    return re.sub(r'[^a-z0-9ঀ-৿]+', '-', s).strip('-')


def render_alpha_bbox(svg_doc):
    import numpy as np
    from PIL import Image
    import resvg_py
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg_doc, skip_system_fonts=True))
    a = np.array(Image.open(io.BytesIO(png)).convert('RGBA'))[:, :, 3]
    ys, xs = np.where(a > 20)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def namespace_ids(svg, prefix):
    for i in sorted(set(re.findall(r'id="([^"]+)"', svg)), key=len, reverse=True):
        if i.startswith(prefix + '--'):
            continue
        n = prefix + '--' + i
        svg = svg.replace(f'id="{i}"', f'id="{n}"').replace(f'url(#{i})', f'url(#{n})').replace(f'href="#{i}"', f'href="#{n}"')
    return svg


def detect_face(inner, transform):
    """Find eyes, skin and mouth on a Rongpat card head so the app can blink and lip-sync it."""
    clip = inner[inner.find('clip-path='):] if 'clip-path=' in inner else inner
    eyes = [(float(m.group(1)), float(m.group(5)), float(m.group(2)), float(m.group(4))) for m in EYE.finditer(clip)][:2]
    fm = FACE.search(clip)
    if not eyes or not fm:
        return None
    chin = float(fm.group(1)) + float(fm.group(3))
    return dict(skin=fm.group(4), chin=chin, eyes=eyes, mouth=[196, chin - 19])


# ------------------------------------------------------------------ bible boards -> library
def import_bible_file(path, out_dir):
    """Extract every character card and place tile from one bible board file."""
    s = open(path, encoding='utf-8').read()
    chars, places = [], []
    os.makedirs(os.path.join(out_dir, 'characters'), exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'places'), exist_ok=True)
    board = os.path.splitext(os.path.splitext(os.path.basename(path))[0])[0]
    for art, meta in re.findall(r'<div class="card">\s*(<svg class="art".*?</svg>)\s*<div class="meta">(.*?)</div>\s*</div>', s, re.S):
        m = re.search(r'<svg class="art"[^>]*aria-label="([^"]*)"[^>]*>(.*)</svg>', art, re.S)
        if not m:
            continue
        aria, inner = m.group(1), m.group(2)
        inner = re.sub(r'<rect width="392" height="640"[^>]*/>', '', inner, count=1)
        inner = re.sub(r'<path d="M46 640 L46 210 A150 150 0 0 1 346 210 L346 640Z"[^>]*/>', '', inner, count=1)
        inner = re.sub(r'<ellipse cx="196" cy="608" rx="110" ry="14"[^>]*/>', '', inner, count=1)
        nm = re.search(r'<h2 class="nm">(.*?)(?:<span class="bn">(.*?)</span>)?</h2>', meta, re.S)
        name = html.unescape(re.sub('<[^>]+>', '', nm.group(1))).strip() if nm else aria.split(':')[0]
        bn = html.unescape(nm.group(2) or '').strip() if nm else ''
        tag = re.search(r'<div class="tag">(.*?)</div>', meta)
        cname = html.unescape(aria.split(':')[0]).strip()
        slug = KNOWN_CHARS.get(cname) or slugify(cname)
        if slug in SKIP_CHARS:
            continue
        for pat in EXTRAS.get(slug, []):
            inner = re.sub(pat, '', inner)
        inner = namespace_ids(inner, slug)
        tr = re.search(r'<g transform="translate\(([-0-9.]+),([-0-9.]+)\) scale\(([0-9.]+)\)">', inner)
        doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="392" height="640" viewBox="0 0 392 640">{inner}</svg>'
        info = dict(slug=slug, name=name, bn=bn, role=html.unescape(tag.group(1)) if tag else '', board=board,
                    desc=html.unescape(aria.split(':', 1)[-1]).strip(), kind='card', bbox=render_alpha_bbox(doc),
                    tx=float(tr.group(1)) if tr else 0.0, ty=float(tr.group(2)) if tr else 0.0, sc=float(tr.group(3)) if tr else 1.0)
        info['face'] = detect_face(inner, tr) if tr else None
        open(os.path.join(out_dir, 'characters', slug + '.svg'), 'w', encoding='utf-8').write(inner)
        chars.append(info)
    for m in re.finditer(r'<div class="tile">\s*(<svg class="art".*?</svg>)\s*<div class="meta">(.*?)</div>\s*</div>', s, re.S):
        svg, meta = m.group(1), m.group(2)
        nm = re.search(r'<h2 class="nm">(.*?)(?:<span class="bn">(.*?)</span>)?</h2>', meta, re.S)
        name = html.unescape(re.sub('<[^>]+>', '', nm.group(1))).strip()
        bn = html.unescape(nm.group(2) or '').strip()
        vb = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', svg)
        w, h = float(vb.group(1)), float(vb.group(2))
        if w / h < 1.3 or w < 500:      # skip small prop/detail tiles
            continue
        inner = re.sub(r'^<svg[^>]*>', '', svg)
        inner = inner[:inner.rindex('</svg>')]
        slug = slugify(name)
        slug = KNOWN_PLACES.get(slug, slug)
        inner = namespace_ids(inner, 'pl-' + slug)
        aria = re.search(r'aria-label="([^"]*)"', svg)
        open(os.path.join(out_dir, 'places', slug + '.svg'), 'w', encoding='utf-8').write(inner)
        places.append(dict(slug=slug, name=name, bn=bn, board=board, w=w, h=h, desc=html.unescape(aria.group(1)) if aria else '',
                           floor=0.9 if h >= 400 else 0.93, kind='tile'))
    return chars, places


def import_bible(folder, out_dir):
    # rig files that come with an update pack (made when Claude builds new characters)
    import shutil
    rd = os.path.join(out_dir, 'rigs')
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith('.rig.json') or (f.lower().endswith('.json') and 'rig' in f.lower()):
            os.makedirs(rd, exist_ok=True)
            shutil.copy(os.path.join(folder, f), os.path.join(rd, f.replace('.rig.json', '.json')))
            print(f'  rig installed: {f}')
    files = [f for f in sorted(os.listdir(folder)) if f.lower().endswith(('.html', '.htm'))]
    ci, pi = _load_index(out_dir, 'characters'), _load_index(out_dir, 'places')
    nc = np_ = 0
    for f in files:
        c, p = import_bible_file(os.path.join(folder, f), out_dir)
        for x in c:
            ci[x['slug']] = x
        for x in p:
            pi[x['slug']] = x
        nc += len(c)
        np_ += len(p)
        print(f'  {f}: {len(c)} characters, {len(p)} places')
    _save_index(out_dir, 'characters', ci)
    _save_index(out_dir, 'places', pi)
    return nc, np_


def _load_index(d, kind):
    p = os.path.join(d, kind, 'index.json')
    if os.path.exists(p):
        return {x['slug']: x for x in json.load(open(p, encoding='utf-8'))}
    return {}


def _save_index(d, kind, idx):
    os.makedirs(os.path.join(d, kind), exist_ok=True)
    json.dump(list(idx.values()), open(os.path.join(d, kind, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


# ------------------------------------------------------------------ loose files dropped into library/
def _sidecar(path):
    j = os.path.splitext(path)[0] + '.json'
    if os.path.exists(j):
        try:
            return json.load(open(j, encoding='utf-8'))
        except Exception as e:
            print(f'  (could not read {os.path.basename(j)}: {e})')
    return {}


def _svg_parts(raw):
    vb = re.search(r'viewBox="([-0-9. ,]+)"', raw)
    if vb:
        x, y, w, h = (float(v) for v in re.split('[ ,]+', vb.group(1).strip()))
    else:
        w = float(re.search(r'width="([0-9.]+)', raw).group(1))
        h = float(re.search(r'height="([0-9.]+)', raw).group(1))
        x = y = 0.0
    inner = re.sub(r'^.*?<svg[^>]*>', '', raw, count=1, flags=re.S)
    inner = inner[:inner.rfind('</svg>')]
    return x, y, w, h, inner


def loose_character(path, cache):
    """A character file someone drew (SVG or transparent PNG): fit it into the card frame (feet at 196,605)."""
    key = f'{os.path.basename(path)}:{os.path.getmtime(path)}'
    side = _sidecar(path)
    slug = slugify(side.get('slug') or os.path.splitext(os.path.basename(path))[0])
    ext = os.path.splitext(path)[1].lower()
    if key in cache:
        info = dict(cache[key])
    else:
        if ext == '.svg':
            x, y, w, h, inner = _svg_parts(open(path, encoding='utf-8').read())
            inner = namespace_ids(inner, slug)
        else:
            import base64
            from PIL import Image
            w, h = Image.open(path).size
            x = y = 0.0
            inner = f'<image width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(open(path, "rb").read()).decode()}"/>'
        doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{inner}</svg>'
        bb = render_alpha_bbox(doc) or [0, 0, int(w), int(h)]
        info = dict(slug=slug, kind='card', inner_raw=None, vb=[x, y, w, h], src_bbox=bb)
        info['_inner'] = inner
        cache[key] = {k: v for k, v in info.items() if k != '_inner'}
        cache[key]['_inner_file'] = path
    if '_inner' not in info:
        if ext == '.svg':
            x, y, w, h, inner = _svg_parts(open(path, encoding='utf-8').read())
            info['_inner'] = namespace_ids(inner, slug)
        else:
            import base64
            from PIL import Image
            w, h = Image.open(path).size
            info['_inner'] = f'<image width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(open(path, "rb").read()).decode()}"/>'
    x, y, w, h = info['vb']
    bx0, by0, bx1, by1 = info['src_bbox']
    layered = None
    if ext == '.svg':
        defs_all = ''.join(re.findall(r'<defs>.*?</defs>', info['_inner'], re.S))
        layered = layered_info(info['_inner'], (x, y, w, h), defs_all)
    size = side.get('size', 'adult')
    target = SIZES.get(size, size) if not isinstance(size, (int, float)) else size
    try:
        target = float(target)
    except (TypeError, ValueError):
        target = SIZES['adult']
    k = target / max(1.0, (by1 - by0))
    cx = (bx0 + bx1) / 2 + x
    by = by1 + y
    wrapped = f'<g transform="translate(196,605) scale({k:.5f}) translate({-cx:.2f},{-by:.2f})">{info["_inner"]}</g>'
    hw = (bx1 - bx0) * k / 2
    out = dict(slug=slug, kind='card', name=side.get('name', os.path.splitext(os.path.basename(path))[0]), bn=side.get('bn', ''),
               role=side.get('role', 'Your character'), desc=side.get('description', ''), board='library',
               bbox=[int(196 - hw), int(605 - target), int(196 + hw), 605], tx=0, ty=0, sc=1, face=None, svg=wrapped)
    if side.get('flip'):
        out['svg'] = f'<g transform="translate(392,0) scale(-1,1)">{wrapped}</g>'
    out['wrap'] = dict(k=k, cx=cx, by=by)
    out['neck'] = side.get('neck')
    if layered:
        out['kind'] = 'layered'
        out['layered'] = layered
    return out


def loose_place(path):
    side = _sidecar(path)
    slug = slugify(side.get('slug') or os.path.splitext(os.path.basename(path))[0])
    ext = os.path.splitext(path)[1].lower()
    if ext == '.svg':
        x, y, w, h, inner = _svg_parts(open(path, encoding='utf-8').read())
        inner = f'<g transform="translate({-x},{-y})">{namespace_ids(inner, "pl-" + slug)}</g>'
    else:
        import base64
        from PIL import Image
        w, h = Image.open(path).size
        mime = 'image/png' if ext == '.png' else 'image/jpeg'
        inner = f'<image width="{w}" height="{h}" href="data:{mime};base64,{base64.b64encode(open(path, "rb").read()).decode()}"/>'
    return dict(slug=slug, name=side.get('name', os.path.splitext(os.path.basename(path))[0]), bn=side.get('bn', ''), board='library',
                w=float(w), h=float(h), desc=side.get('description', ''), floor=float(side.get('floor', 0.9)), kind='tile', svg=inner)


def scan_user_library(lib_dir):
    """Characters and places the user added. Returns (chars, places) dicts keyed by slug."""
    chars, places = {}, {}
    if not os.path.isdir(lib_dir):
        return chars, places
    cache_p = os.path.join(lib_dir, '.cache.json')
    try:
        cache = json.load(open(cache_p, encoding='utf-8'))
    except Exception:
        cache = {}
    cd = os.path.join(lib_dir, 'characters')
    if os.path.isdir(cd):
        idx = _load_index(lib_dir, 'characters')
        for slug, info in idx.items():
            p = os.path.join(cd, slug + '.svg')
            if os.path.exists(p):
                info = dict(info)
                info['file'] = p
                chars[slug] = info
        for f in sorted(os.listdir(cd)):
            p = os.path.join(cd, f)
            if f.lower().endswith(('.svg', '.png')) and os.path.splitext(f)[0] not in idx:
                try:
                    c = loose_character(p, cache)
                    chars[c['slug']] = c
                except Exception as e:
                    print(f'  (skipped character {f}: {e})')
    pd = os.path.join(lib_dir, 'places')
    if os.path.isdir(pd):
        idx = _load_index(lib_dir, 'places')
        for slug, info in idx.items():
            p = os.path.join(pd, slug + '.svg')
            if os.path.exists(p):
                info = dict(info)
                info['file'] = p
                places[slug] = info
        for f in sorted(os.listdir(pd)):
            p = os.path.join(pd, f)
            if f.lower().endswith(('.svg', '.png', '.jpg', '.jpeg')) and os.path.splitext(f)[0] not in idx:
                try:
                    pl = loose_place(p)
                    places[pl['slug']] = pl
                except Exception as e:
                    print(f'  (skipped place {f}: {e})')
    try:
        json.dump(cache, open(cache_p, 'w', encoding='utf-8'))
    except Exception:
        pass
    return chars, places


# ------------------------------------------------------------------ objects dropped into library/props
PROP_SIZES = {'tiny': 14, 'small': 30, 'medium': 60, 'large': 120, 'huge': 220}


def scan_user_props(lib_dir):
    """Every .svg/.png in library/props becomes an object that can be held, thrown, dropped, spun or placed."""
    out = {}
    pd = os.path.join(lib_dir, 'props')
    if not os.path.isdir(pd):
        return out
    for f in sorted(os.listdir(pd)):
        p = os.path.join(pd, f)
        ext = os.path.splitext(f)[1].lower()
        if ext not in ('.svg', '.png'):
            continue
        try:
            side = _sidecar(p)
            slug = slugify(side.get('slug') or os.path.splitext(f)[0])
            if ext == '.svg':
                x, y, w, h, inner = _svg_parts(open(p, encoding='utf-8').read())
                inner = namespace_ids(inner, 'pr-' + slug)
            else:
                import base64
                from PIL import Image
                w, h = Image.open(p).size
                x = y = 0.0
                inner = f'<image width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(open(p, "rb").read()).decode()}"/>'
            doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{inner}</svg>'
            bb = render_alpha_bbox(doc) or [0, 0, int(w), int(h)]
            bx0, by0, bx1, by1 = bb[0] + x, bb[1] + y, bb[2] + x, bb[3] + y
            grip = side.get('grip', 'center')
            if isinstance(grip, list):
                gx, gy = bx0 + (bx1 - bx0) * grip[0], by0 + (by1 - by0) * grip[1]
            elif grip == 'top':
                gx, gy = (bx0 + bx1) / 2, by0 + (by1 - by0) * 0.08
            elif grip == 'bottom':
                gx, gy = (bx0 + bx1) / 2, by1
            else:
                gx, gy = (bx0 + bx1) / 2, (by0 + by1) / 2
            size = side.get('size', 'medium')
            height = float(PROP_SIZES.get(size, size)) if not isinstance(size, (int, float)) else float(size)
            out[slug] = dict(slug=slug, name=side.get('name', os.path.splitext(f)[0]), bn=side.get('bn', ''), role='Your object', kind='prop',
                             height=height, native_h=max(1.0, by1 - by0), svg=inner, grip=(gx, gy), rest_dy=by1 - gy,
                             desc=side.get('description', 'Your object'))
        except Exception as e:
            print(f'  (skipped object {f}: {e})')
    return out


# ------------------------------------------------------------------ layered characters (parts named head, body, arm-left ...)
PART_NAMES = ('head', 'body', 'torso', 'arm-left', 'arm-right', 'leg-left', 'leg-right')


def _balanced_group(s, start):
    d, j = 0, start
    for m in re.finditer(r'<g\b|</g>', s[start:]):
        tok = m.group(0)
        if tok == '<g':
            d += 1
        else:
            d -= 1
            if d == 0:
                return s[start:start + m.end()]
    return s[start:]


def find_parts(inner):
    parts = {}
    for m in re.finditer(r'<g\b[^>]*?(?:\bid|inkscape:label)="([^"]+)"[^>]*>', inner):
        name = m.group(1).strip().lower().split('--')[-1].replace('_', '-').replace(' ', '-')
        name = {'arm-l': 'arm-left', 'arm-r': 'arm-right', 'leg-l': 'leg-left', 'leg-r': 'leg-right', 'left-arm': 'arm-left',
                'right-arm': 'arm-right', 'left-leg': 'leg-left', 'right-leg': 'leg-right'}.get(name, name)
        if name in PART_NAMES and name not in parts:
            parts[name] = _balanced_group(inner, m.start())
    return parts


def layered_info(inner, vb, defs_all):
    """Pivots (in source coordinates) for each named part, found by rendering the part alone."""
    parts = find_parts(inner)
    if len([p for p in parts if p.startswith(('arm', 'leg', 'head'))]) < 2:
        return None
    x, y, w, h = vb
    rest = inner
    for p in parts.values():
        rest = rest.replace(p, '')
    info = {}
    for name, svg in parts.items():
        doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}">{defs_all}{svg}</svg>'
        bb = render_alpha_bbox(doc)
        if not bb:
            continue
        bx0, by0, bx1, by1 = bb[0] + x, bb[1] + y, bb[2] + x, bb[3] + y
        if name == 'head':
            pivot = ((bx0 + bx1) / 2, by1 - (by1 - by0) * 0.06)
        elif name.startswith(('arm', 'leg')):
            pivot = ((bx0 + bx1) / 2, by0 + min(12, (by1 - by0) * 0.08))
        else:
            pivot = ((bx0 + bx1) / 2, (by0 + by1) / 2)
        info[name] = dict(svg=svg, bbox=[bx0, by0, bx1, by1], pivot=pivot, tip=((bx0 + bx1) / 2, by1))
    return dict(parts=info, rest=rest)
