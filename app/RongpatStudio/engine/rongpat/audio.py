"""Rongpat Studio sound: offline synthesized music moods, a sound-effects library, voice loading and the final mix."""
import math, os, subprocess, wave
import numpy as np
from scipy.signal import resample_poly, butter, lfilter

SR = 48000
rng = np.random.default_rng(7)


# ------------------------------------------------------------------ basics
def ffmpeg_exe():
    import glob, sys, imageio_ffmpeg
    if sys.platform == 'win32':
        found = glob.glob(os.path.join(os.path.dirname(imageio_ffmpeg.__file__), 'binaries', 'ffmpeg*.exe'))
        if found:
            return found[0]
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_audio(path):
    """Decode any audio file (wav, mp3, m4a, ogg...) to mono float at 48 kHz using the bundled ffmpeg."""
    cmd = [ffmpeg_exe(), '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    out = subprocess.run(cmd, capture_output=True, **_noconsole())
    if out.returncode != 0:
        raise RuntimeError(f'Could not read audio file {path}: {out.stderr.decode(errors="ignore")[:300]}')
    return np.frombuffer(out.stdout, dtype=np.float32).astype(np.float64)


def _noconsole():
    import sys
    if sys.platform == 'win32':
        return {'creationflags': 0x08000000}
    return {}


def write_wav(path, x):
    y = np.clip(x, -1, 1)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype('<i2').tobytes())


def at(buf, sig, t):
    i = int(t * SR)
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[:j - i]


def envelope(x, fps):
    """Per-frame mouth-opening values 0..1 from a voice clip."""
    hop = SR // fps
    n = max(1, len(x) // hop)
    e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    e = np.convolve(e, [0.25, 0.5, 0.25], 'same')
    ref = np.percentile(e, 97) if len(e) > 3 else (e.max() + 1e-9)
    return np.clip(e / (ref + 1e-9), 0, 1)


def lp(x, fc):
    b, a = butter(2, fc / (SR / 2))
    return lfilter(b, a, x)


def hp(x, fc):
    b, a = butter(2, fc / (SR / 2), 'high')
    return lfilter(b, a, x)


def bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return lfilter(b, a, x)


def noise(d):
    return rng.normal(0, 1, int(d * SR))


def decay(d, tau):
    return np.exp(-np.arange(int(d * SR)) / SR / tau)


# ------------------------------------------------------------------ instruments
_pc = {}


def pluck(freq, dur=1.0, amp=0.5):
    k = (round(freq, 1), dur)
    if k not in _pc:
        n = int(dur * SR)
        p = max(2, int(SR / freq))
        buf = rng.uniform(-1, 1, p)
        out = np.zeros(n)
        for i in range(n):
            out[i] = buf[i % p]
            buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.9965
        _pc[k] = out * np.exp(-np.arange(n) / SR / (dur * 0.6))
    return _pc[k] * amp


def flute(freq, dur, amp=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.4)
    ph = 2 * np.pi * np.cumsum(freq * vib) / SR
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    s += 0.05 * bp(rng.normal(0, 1, n), freq * 0.8, min(freq * 2.5, SR / 2 - 100))
    e = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12)
    return s * e * amp


def bell(freq, dur=2.5, amp=0.3):
    t = np.arange(int(dur * SR)) / SR
    return sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / (dur * d)) for r, a, d in ((1, 1, 0.5), (2.76, 0.5, 0.25), (5.4, 0.25, 0.12), (8.9, 0.12, 0.08))) * amp


def tabla(kind, amp=0.5):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    if kind == 'na':
        f = 420 * (1 + 0.15 * np.exp(-t / 0.02))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
        s += 0.3 * hp(rng.normal(0, 1, n), 2000) * np.exp(-t / 0.01)
    else:
        f = 80 + 70 * np.exp(-t / 0.08)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    return s * amp


def drone(dur, freqs=(65.4, 98.0, 130.8), amp=0.18):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * t + i) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t + i)) for i, f in enumerate(freqs))
    s += 0.3 * lp(rng.normal(0, 1, len(t)), 300)
    return s * amp * np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.0 + 1e-9)


C4 = 261.63
BH = [1, 16 / 15, 5 / 4, 4 / 3, 3 / 2, 8 / 5, 15 / 8]      # raga Bhairav: dusky, mysterious
BU = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3]                     # raga Bhupali: sweet, happy


def note(scale, deg, octv=0):
    o, d = divmod(deg, len(scale))
    return C4 * scale[d] * 2 ** (o + octv)


# ------------------------------------------------------------------ music moods
MOODS = {
    'calm': 'Soft drone with slow dotara plucks (raga Bhairav). Openers, mystery, night.',
    'spooky': 'Low drone, slow bells and a heartbeat. Ghost scenes, horror build-up.',
    'comic': 'Tabla at 160 bpm with a plucked bass. Chases, silly moments.',
    'tense': 'Fast low tremolo. Danger, getting caught, suspense.',
    'sweet': 'Bansuri flute melody with dotara (raga Bhupali). Kindness, friendship, endings.',
    'happy': 'Bouncy dotara with light tabla (Bhupali). Celebrations, fun.',
    'none': 'Silence.',
}


def music(mood, dur):
    n = int(dur * SR) + SR
    m = np.zeros(n)
    if mood == 'calm':
        at(m, drone(dur + 1), 0)
        motif = [(0, 0), (1, 1), (2, 2), (1, 1), (0, 0), (6, -1), (5, -1)]
        t = 0.6
        while t < dur:
            for deg, o in motif:
                at(m, pluck(note(BH, deg, o - 1), 1.4, 0.35), t)
                t += 0.62
            t += 1.2
    elif mood == 'spooky':
        at(m, drone(dur + 1, (55.0, 58.3, 82.4), 0.2), 0)
        t = 0.8
        k = 0
        while t < dur:
            at(m, bell(note(BH, [0, 1, 5][k % 3], 0), 3.0, 0.16), t)
            t += 2.4
            k += 1
        t = 1.5
        while t < dur:
            hb = np.sin(2 * np.pi * (55 + 30 * np.exp(-np.arange(int(0.5 * SR)) / SR / 0.03)) * np.arange(int(0.5 * SR)) / SR) * decay(0.5, 0.08)
            at(m, hb * 0.5, t)
            at(m, hb * 0.35, t + 0.16)
            t += 1.1
    elif mood == 'comic':
        beat = 60 / 160
        pat = ['ge', 'na', 'na', 'ge', 'na', 'ge', 'na', 'na']
        bass = [0, 0, 4, 4, 5, 5, 4, 2]
        t, i = 0.05, 0
        while t < dur:
            at(m, tabla(pat[i % 8], 0.45), t)
            if i % 2 == 0:
                at(m, pluck(note(BH, bass[(i // 2) % 8], -2), 0.5, 0.5), t)
            if i % 4 == 2:
                at(m, pluck(note(BH, [4, 5, 6, 7][(i // 4) % 4], 0), 0.35, 0.35), t + beat / 2)
            t += beat / 2
            i += 1
    elif mood == 'tense':
        at(m, drone(dur + 1, (65.4, 69.3), 0.16), 0)
        t, k = 0.05, 0
        while t < dur:
            at(m, pluck(note(BH, [0, 1][k % 2], -2), 0.4, 0.35), t)
            t += 0.18
            k += 1
    elif mood == 'sweet':
        mel = [(0, 0.8), (1, 0.4), (2, 1.2), (3, 0.8), (2, 0.4), (1, 0.8), (2, 1.6), (3, 0.6), (4, 0.6), (5, 1.2), (4, 0.6), (3, 0.6), (2, 1.6)]
        t = 0.3
        while t < dur:
            for deg, d in mel:
                if t >= dur:
                    break
                at(m, flute(note(BU, deg, 1), d * 1.05, 0.22), t)
                t += d
            t += 0.8
        t = 0.3
        while t < dur:
            for deg in (0, 2, 3, 2):
                at(m, pluck(note(BU, deg, -1), 1.0, 0.3), t)
                t += 0.5
    elif mood == 'happy':
        beat = 60 / 132
        t, i = 0.05, 0
        while t < dur:
            at(m, pluck(note(BU, [0, 2, 4, 2, 3, 1, 2, 0][i % 8], 0), 0.6, 0.35), t)
            if i % 2 == 0:
                at(m, tabla('ge' if i % 4 == 0 else 'na', 0.3), t)
                at(m, pluck(note(BU, [0, 3][(i // 4) % 2], -2), 0.6, 0.35), t)
            t += beat / 2
            i += 1
    return m[:int(dur * SR)]


# ------------------------------------------------------------------ sound effects
def _creak(dur, amp=0.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 90 + 40 * np.sin(2 * np.pi * 1.3 * t) + 25 * rng.normal(0, 1, n).cumsum() / np.sqrt(n)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 23 * t)))
    return bp(x, 300, 2500) * amp * np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.2)


def _sweep(d, lo, hi, a):
    return bp(noise(d), lo, hi) * a * np.sin(np.linspace(0, np.pi, int(d * SR)))


def _heartbeat(amp=0.6):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (55 + 30 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.08)
    return (s + np.roll(s, int(0.16 * SR)) * 0.7) * amp


def _steps(k=6, gap=0.28):
    out = np.zeros(int((k * gap + 0.2) * SR))
    for i in range(k):
        at(out, lp(noise(0.06), 400) * 0.4 * decay(0.06, 0.02), i * gap)
    return out


def _whistle():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(1900 + 500 * t / 0.6) / SR) * 0.35 + bp(rng.normal(0, 1, n), 2000, 6000) * 0.2) * np.minimum(1, t / 0.05)


def _slide_whistle(up=True):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    f = (500 + 1400 * t / 0.7) if up else (1900 - 1400 * t / 0.7)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 * np.minimum(1, t / 0.05) * np.minimum(1, (0.7 - t) / 0.05)


def _pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(900 - 600 * t / 0.12) / SR) * np.exp(-t / 0.03) * 0.6


def _clang():
    t = np.arange(SR) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.25) for f in (523, 1187, 1899, 2650)) * 0.12


def _gong():
    t = np.arange(int(3 * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 2 * t) * a) * np.exp(-t / d) for f, a, d in ((196, 1, 1.4), (247, 0.6, 1.0), (393, 0.4, 0.6), (588, 0.2, 0.4))) * 0.22


def _thunder():
    x = lp(noise(3.0), 120) * 1.6
    e = np.concatenate([np.linspace(0, 1, int(0.05 * SR)), np.exp(-np.arange(int(2.95 * SR)) / SR / 0.8)])
    return x * e


def _rain(d=6.0):
    return bp(noise(d), 800, 7000) * 0.15 * np.minimum(1, np.arange(int(d * SR)) / SR / 0.5)


def _splash():
    return bp(noise(0.7), 300, 5000) * 0.6 * decay(0.7, 0.18)


def _chew():
    out = np.zeros(int(1.1 * SR))
    for k in range(8):
        at(out, bp(noise(0.07), 300, 1200) * 0.3 * decay(0.07, 0.02), k * 0.12)
    return out


def _sparkle():
    out = np.zeros(int(1.6 * SR))
    for k in range(8):
        at(out, bell(1600 + 300 * k, 0.8, 0.05), k * 0.08)
    return out


def _ticks(k=8):
    out = np.zeros(int((k * 0.5 + 0.1) * SR))
    for i in range(k):
        at(out, hp(noise(0.02), 3000) * 0.3 * decay(0.02, 0.004), i * 0.5)
    return out


SFX = {
    'whoosh': ('A fast swish (moves, entrances).', lambda: _sweep(0.6, 400, 3000, 0.4)),
    'rise': ('A slow ghostly rising swish.', lambda: _sweep(1.4, 200, 1500, 0.35)),
    'thud': ('A heavy bump or fall.', lambda: lp(noise(0.4), 150) * 0.9 * decay(0.4, 0.08)),
    'slap': ('A wet slap (fish hits the floor).', lambda: bp(noise(0.15), 300, 3000) * 0.5 * decay(0.15, 0.025)),
    'creak': ('A creaking door or floorboard.', lambda: _creak(1.2, 0.35)),
    'bell': ('A temple-style bell.', lambda: bell(C4 * 2, 3.0, 0.35)),
    'gong': ('The school gong: dhong!', _gong),
    'sparkle': ('Magic twinkles.', _sparkle),
    'heartbeat': ('Six heartbeats speeding up.', lambda: _seq([_heartbeat(0.55 + 0.08 * k) for k in range(6)], [0.55 - 0.04 * k for k in range(6)])),
    'clock': ('Clock ticking (4 s).', _ticks),
    'steps': ('Six footsteps.', _steps),
    'paws': ('Quick soft paw steps.', lambda: _steps(8, 0.16)),
    'whistle': ('A guard’s whistle: pheeep!', _whistle),
    'slide-up': ('Cartoon slide whistle going up.', lambda: _slide_whistle(True)),
    'slide-down': ('Cartoon slide whistle going down.', lambda: _slide_whistle(False)),
    'pop': ('A small pop (emote, appear).', _pop),
    'clang': ('Metal pot clang.', _clang),
    'thunder': ('Thunder rumble.', _thunder),
    'rain': ('Rain (6 s).', _rain),
    'wind': ('Night wind (6 s).', lambda: bp(noise(6), 80, 600) * 0.15 * (0.7 + 0.3 * np.sin(np.linspace(0, 8, int(6 * SR))))),
    'splash': ('Water splash.', _splash),
    'chew': ('Munching.', _chew),
    'room-tone': ('Quiet room hum (6 s).', lambda: lp(noise(6), 200) * 0.12),
}


def _seq(sigs, gaps):
    total = sum(gaps) + max(len(s) for s in sigs) / SR + 0.1
    out = np.zeros(int(total * SR))
    t = 0
    for s, g in zip(sigs, gaps):
        at(out, s, t)
        t += g
    return out


def gated_rms(x, thr_db=-40):
    hop = int(0.05 * SR)
    if len(x) < hop * 2:
        return 1e-9
    fr = np.sqrt(np.mean(x[:len(x) // hop * hop].reshape(-1, hop) ** 2, axis=1))
    lv = 20 * np.log10(fr + 1e-12)
    keep = fr[lv > lv.max() + thr_db]
    return float(np.sqrt(np.mean(keep ** 2))) if len(keep) else 1e-9


def mix(total, voices, music_segs, sfx_events, music_db=-7.0):
    """voices: [(start, samples)]; music_segs: [(start, end, mood)]; sfx_events: [(time, name, gain)]."""
    n = int(total * SR) + SR
    v = np.zeros(n)
    for t, x in voices:
        at(v, x, t)
    vr = gated_rms(v) if np.any(v) else 0.1
    m = np.zeros(n)
    for a, b, mood in music_segs:
        if mood == 'none' or b - a < 0.2:
            continue
        seg = music(mood, b - a + 0.5)
        fade = np.ones(len(seg))
        k = int(0.4 * SR)
        fade[:k] = np.linspace(0, 1, k)
        fade[-k:] = np.linspace(1, 0, k)
        at(m, seg * fade, a)
    if np.any(m):
        m *= (vr * 10 ** (music_db / 20)) / gated_rms(m)
        if np.any(v):
            k2 = int(0.12 * SR)
            ve = np.sqrt(np.convolve(v ** 2, np.ones(k2) / k2, mode='same'))
            act = np.clip(ve / (vr * 0.25), 0, 1)
            act = np.convolve(act, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
            m *= 1 - 0.55 * np.clip(act * 1.5, 0, 1)
    fx = np.zeros(n)
    for t, name, gain in sfx_events:
        if name in SFX:
            at(fx, SFX[name][1]() * gain, t)
    if np.any(fx):
        fx *= (vr * 0.45) / gated_rms(fx)
        vp = np.abs(v).max() if np.any(v) else 0.5
        if np.abs(fx).max() > 0.8 * vp:
            fx *= 0.8 * vp / np.abs(fx).max()
    out = v + m + fx
    out = out[:int(total * SR)]
    pk = np.abs(out).max()
    if pk > 0:
        out = out / pk * 0.5
    return out
