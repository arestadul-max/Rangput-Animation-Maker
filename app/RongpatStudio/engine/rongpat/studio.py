"""Rongpat Studio: commands used by the Windows launchers.

  python -m rongpat new  "My Story"            create a project folder with a scene sheet
  python -m rongpat make "projects/My Story"   render the final video
  python -m rongpat make "projects/My Story" --preview
  python -m rongpat make "projects/My Story" --shots 3-5
  python -m rongpat still "projects/My Story" 4 [1.5]   one picture of shot 4 at 1.5 s
"""
import os, sys, time, subprocess, pickle, re
from multiprocessing import Pool, cpu_count

from . import engine as E
from . import audio as A

FONTS = os.path.join(E.ASSETS, 'fonts')
_movie = None
_px = (1080, 1920)


def _init(blob, px):
    global _movie, _px
    shots, = pickle.loads(blob)
    _movie = E.Movie(shots, E.Library())
    _px = px


def _render(f):
    import resvg_py
    svg = _movie.frame_svg(f, *_px)
    return bytes(resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS], skip_system_fonts=True))


def find_sheet(project):
    for name in ('scenes.xlsx', 'scenes.csv'):
        p = os.path.join(project, name)
        if os.path.exists(p):
            return p
    for f in os.listdir(project):
        if f.lower().endswith(('.xlsx', '.csv')) and not f.startswith('~$'):
            return os.path.join(project, f)
    raise E.SheetError(f'No scene sheet (scenes.xlsx) found in {project}')


def load(project, shots_sel=None):
    lib = E.Library()
    rows = E.read_sheet(find_sheet(project))
    shots = E.build_plan(rows, lib, project, A)
    if shots_sel:
        a, b = shots_sel
        keep = shots[a - 1:b]
        if not keep:
            raise E.SheetError(f'There is no shot {a} (the sheet has {len(shots)} shots).')
        t = 0.0
        for s in keep:
            s.start = t
            t += s.dur
        shots = keep
    return lib, shots


def build_audio(shots, project, out_wav):
    voices, segs, fx = [], [], []
    custom = {}
    for s in shots:
        for v in s.voices:
            if v.get('samples') is not None:
                voices.append((s.start + v['start'], v['samples']))
        mood = s.music if s.music in A.MOODS else 'calm'
        if segs and segs[-1][2] == mood and abs(segs[-1][1] - s.start) < 1e-6:
            segs[-1] = (segs[-1][0], s.start + s.dur, mood)
        else:
            segs.append((s.start, s.start + s.dur, mood))
        for e in s.sfx:
            name = e['name']
            if name in A.SFX:
                fx.append((s.start + e['t'], name, 1.0))
            else:
                cand = [f for f in os.listdir(os.path.join(project, 'sounds'))] if os.path.isdir(os.path.join(project, 'sounds')) else []
                hit = [f for f in cand if os.path.splitext(f)[0].lower() == os.path.splitext(name)[0].lower()]
                if not hit:
                    raise E.SheetError(f'Row {s.row}: sound "{name}" is not a built-in sound or a file in the sounds folder.')
                key = 'file:' + hit[0]
                if key not in A.SFX:
                    x = A.load_audio(os.path.join(project, 'sounds', hit[0]))
                    A.SFX[key] = ('custom', (lambda x=x: x))
                fx.append((s.start + e['t'], key, 1.0))
    total = sum(s.dur for s in shots)
    mixd = A.mix(total, voices, segs, fx)
    A.write_wav(out_wav, mixd)
    return total


def grain_png(path):
    if os.path.exists(path):
        return
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(3)
    g = np.clip(128 + rng.normal(0, 22, (1920, 1080)), 0, 255).astype('uint8')
    Image.fromarray(g, 'L').convert('RGB').save(path)


def make(project, preview=False, shots_sel=None, jobs=None):
    project = os.path.abspath(project)
    t0 = time.time()
    print(f'Reading the scene sheet in {project} ...')
    lib, shots = load(project, shots_sel)
    movie = E.Movie(shots, lib)
    print(f'  {len(shots)} shots, {movie.total:.1f} seconds, {movie.nframes} frames.')
    out_dir = os.path.join(project, 'output')
    os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(out_dir, '_work')
    os.makedirs(work, exist_ok=True)
    print('Making the sound (voices, music, effects) ...')
    wav = os.path.join(work, 'mix.wav')
    build_audio(shots, project, wav)
    name = os.path.basename(project.rstrip('\\/'))
    suffix = ' (preview)' if preview else ''
    if shots_sel:
        suffix += f' shots {shots_sel[0]}-{shots_sel[1]}'
    out = os.path.join(out_dir, f'{name}{suffix}.mp4')
    px = (540, 960) if preview else (1080, 1920)
    ff = A.ffmpeg_exe()
    grain = os.path.join(E.ASSETS, 'grain.png')
    grain_png(grain)
    if preview:
        cmd = [ff, '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(E.FPS), '-c:v', 'png', '-i', '-', '-i', wav,
               '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26', '-pix_fmt', 'yuv420p',
               '-af', 'loudnorm=I=-13:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out]
    else:
        cmd = [ff, '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(E.FPS), '-c:v', 'png', '-i', '-', '-loop', '1', '-i', grain, '-i', wav,
               '-filter_complex', '[1:v]format=rgb24,scale=1080:1920[g];[0:v]format=rgb24[v];[v][g]blend=all_mode=overlay:all_opacity=0.16:shortest=1,format=yuv420p[o]',
               '-map', '[o]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
               '-af', 'loudnorm=I=-13:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]
    jobs = jobs or max(1, cpu_count() - 1)
    print(f'Drawing {movie.nframes} frames on {jobs} CPU cores ({"preview" if preview else "full HD"}) ...')
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, **A._noconsole())
    blob = pickle.dumps((_strip(shots),))
    t1 = time.time()
    with Pool(jobs, initializer=_init, initargs=(blob, px)) as pool:
        for i, png in enumerate(pool.imap(_render, range(movie.nframes), chunksize=4)):
            proc.stdin.write(png)
            if i % 30 == 0 or i == movie.nframes - 1:
                el = time.time() - t1
                eta = el / (i + 1) * (movie.nframes - i - 1)
                sys.stdout.write(f'\r  frame {i + 1}/{movie.nframes}  ({100 * (i + 1) / movie.nframes:.0f}%)  about {int(eta // 60)}m {int(eta % 60):02d}s left   ')
                sys.stdout.flush()
    proc.stdin.close()
    proc.wait()
    print()
    if proc.returncode != 0:
        raise RuntimeError('ffmpeg could not make the video file.')
    print(f'Done in {int((time.time() - t0) // 60)}m {int((time.time() - t0) % 60):02d}s.')
    print(f'Your video: {out}')
    return out


def _strip(shots):
    import copy
    out = []
    for s in shots:
        c = copy.copy(s)
        c.voices = [dict(v, samples=None) for v in s.voices]
        out.append(c)
    return out


def still(project, shot, at=None):
    import resvg_py
    lib, shots = load(os.path.abspath(project), (shot, shot))
    s = shots[0]
    t = at if at is not None else s.dur / 2
    m = E.Movie(shots, lib)
    svg = m.frame_svg(int(min(t, s.dur - 0.05) * E.FPS))
    out_dir = os.path.join(os.path.abspath(project), 'output')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'shot {shot} at {t:.1f}s.png')
    open(out, 'wb').write(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS], skip_system_fonts=True)))
    print(f'Picture saved: {out}')
    return out


def new(name, base):
    from .template import make_template
    safe = re.sub(r'[<>:"/\\|?*]', '', name).strip() or 'New Story'
    p = os.path.join(base, safe)
    if os.path.exists(p):
        raise E.SheetError(f'A project called "{safe}" already exists.')
    for sub in ('voice', 'images', 'sounds', 'output'):
        os.makedirs(os.path.join(p, sub))
    make_template(os.path.join(p, 'scenes.xlsx'), E.Library())
    print(f'New project created: {p}')
    print('Put your voice recordings in its "voice" folder, then fill in scenes.xlsx.')
    return p


def projects_dir():
    return os.path.join(os.path.dirname(E.ROOT), 'projects')


def ask_project():
    pd = projects_dir()
    os.makedirs(pd, exist_ok=True)
    items = sorted(d for d in os.listdir(pd) if os.path.isdir(os.path.join(pd, d)))
    if not items:
        raise E.SheetError('There are no projects yet. Run "1 - New Project" first.')
    print('Your projects:')
    for i, d in enumerate(items, 1):
        print(f'  {i}. {d}')
    while True:
        a = input('Type the project number and press Enter: ').strip()
        if a.isdigit() and 1 <= int(a) <= len(items):
            return os.path.join(pd, items[int(a) - 1])
        print('  Please type one of the numbers above.')


def open_file(path):
    if sys.platform == 'win32' and not os.environ.get('RONGPAT_NO_OPEN'):
        try:
            os.startfile(path)
        except OSError:
            pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if not argv:
            print(__doc__)
            return 0
        cmd = argv.pop(0)
        if cmd == 'new':
            name = argv[0] if argv and argv[0] != '--ask' else input('Name of your new story: ').strip()
            p = new(name or 'New Story', projects_dir())
            open_file(p)
        elif cmd == 'make':
            preview = '--preview' in argv
            sel = None
            if '--shots' in argv:
                v = argv[argv.index('--shots') + 1]
                a, _, b = v.partition('-')
                sel = (int(a), int(b or a))
            proj = argv[0] if argv and not argv[0].startswith('--') else ask_project()
            if '--ask-shots' in argv:
                a = input('Which shots? (e.g. 3 or 3-5, or just Enter for all): ').strip()
                if a:
                    x, _, y = a.partition('-')
                    sel = (int(x), int(y or x))
            out = make(proj, preview, sel)
            open_file(out)
        elif cmd == 'still':
            if argv and argv[0] == '--ask':
                proj = ask_project()
                shot = int(input('Shot number: ').strip())
                tt = input('At which second of the shot? (Enter = middle): ').strip()
                out = still(proj, shot, float(tt) if tt else None)
            else:
                out = still(argv[0], int(argv[1]), float(argv[2]) if len(argv) > 2 else None)
            open_file(out)
        elif cmd == 'update-library':
            from .library import import_bible
            src = argv[0] if argv else os.path.join(E.USER_LIB, 'bible-import')
            os.makedirs(src, exist_ok=True)
            print(f'Importing bible boards from {src} ...')
            nc, np_ = import_bible(src, E.USER_LIB)
            lib = E.Library()
            print(f'Imported {nc} characters and {np_} places.')
            print(f'Your library now has {len(lib.chars)} characters and {len(lib.places)} places.')
            if lib.user_chars:
                print('  Your own / updated characters: ' + ', '.join(lib.user_chars))
            if lib.user_places:
                print('  Your own / updated places: ' + ', '.join(lib.user_places))
            proj = os.path.join(os.path.dirname(E.ROOT), 'projects')
            if os.path.isdir(proj):
                from .template import refresh_lists
                for d in os.listdir(proj):
                    x = os.path.join(proj, d, 'scenes.xlsx')
                    if os.path.exists(x):
                        try:
                            refresh_lists(x, lib)
                        except PermissionError:
                            print(f'  (close {d}/scenes.xlsx in Excel to update its lists)')
            print('Done. Character and Place lists in your projects are updated.')
        elif cmd == 'list':
            lib = E.Library()
            print('CHARACTERS:')
            for k, c in sorted(lib.chars.items()):
                print(f'  {k:22s} {c["name"]}')
            print('PLACES:')
            for k, p in sorted(lib.places.items()):
                print(f'  {k:28s} {p["name"]}')
        elif cmd == 'template':
            from .template import make_template
            make_template(argv[0], E.Library())
        else:
            print(__doc__)
        return 0
    except E.SheetError as e:
        print('\nPROBLEM IN THE SCENE SHEET:\n  ' + str(e))
        return 2
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('\nSomething went wrong: ' + str(e))
        return 1
