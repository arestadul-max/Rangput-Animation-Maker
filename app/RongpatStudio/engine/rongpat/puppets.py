"""Rongpat animation library: colour tinting, easing, characters and sets as SVG strings."""
import math, re

INK = '#1C1410'
NIGHT = (0x1B, 0x25, 0x47)
WARM = (0xFF, 0xB3, 0x47)
_uid = [0]


def uid():
    _uid[0] += 1
    return f"u{_uid[0]}"


def reset_uid():
    _uid[0] = 0


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ss(t):
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


def ramp(t, t0, t1):
    if t1 == t0:
        return 1.0 if t >= t1 else 0.0
    return ss((t - t0) / (t1 - t0))


def keys(t, ks):
    """ks: list of (time, value) where value is float or tuple; smootherstep between keys."""
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            u = ss((t - t0) / (t1 - t0)) if t1 > t0 else 1
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
            return lerp(v0, v1, u)
    return ks[-1][1]


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tohex(c):
    return '#%02X%02X%02X' % tuple(int(clamp(v, 0, 255)) for v in c)


def tint_color(h, n, w):
    c = hx(h)
    if h.upper() == INK:
        return h
    c = tuple(lerp(a, b, n) for a, b in zip(c, NIGHT))
    c = tuple(lerp(a, b, w) for a, b in zip(c, WARM))
    return tohex(c)


_hexre = re.compile(r'#[0-9A-Fa-f]{6}')


def tint(svg, n=0.0, w=0.0):
    if n == 0 and w == 0:
        return svg
    return _hexre.sub(lambda m: tint_color(m.group(0), n, w), svg)


def ids(svg):
    """Replace @ placeholders in ids/urls with a unique suffix."""
    return svg.replace('@', uid())


def blinkv(t, times, dur=0.16):
    """Return lid closure amount 0..1 for blinks at given times."""
    v = 0.0
    for b in times:
        d = t - b
        if 0 <= d <= dur:
            v = max(v, math.sin(math.pi * d / dur))
    return v


# ---------------------------------------------------------------- eyes
def eye(cx, cy, w, up, down, open_, pupil_rx, pupil_ry, gx, gy, iris, lid, lidw=6, glint=True):
    """Almond eye with a lid that lowers as open_ goes 1 -> 0. Coordinates in local units."""
    x0, x1 = cx - w / 2, cx + w / 2
    almond = f"M{x0},{cy} Q{cx},{cy - up} {x1},{cy} Q{cx},{cy + down} {x0},{cy}Z"
    top_mid = cy - up / 2
    bot_mid = cy + down / 2
    Ly = lerp(bot_mid + 1, top_mid - 2, clamp(open_))
    c = 2 * Ly - cy
    lidp = f"M{x0},{cy} Q{cx},{cy - up} {x1},{cy} Q{cx},{c} {x0},{cy}Z"
    s = f'<path d="{almond}" fill="{iris}"/>'
    if pupil_rx > 0:
        s += f'<ellipse cx="{cx + gx:.1f}" cy="{cy + gy:.1f}" rx="{pupil_rx}" ry="{pupil_ry}" fill="#1C1410" stroke="none"/>'
        if glint:
            s += f'<circle cx="{cx + gx + pupil_rx * 0.45:.1f}" cy="{cy + gy - pupil_ry * 0.4:.1f}" r="{max(1.6, pupil_rx * 0.3):.1f}" fill="#FBF5E9" stroke="none"/>'
    s += f'<path d="{lidp}" fill="{lid}" stroke="none"/>'
    s += f'<path d="M{x0 - 4},{cy - 1} Q{cx},{c} {x1 + 2},{cy} L{x1 + 7},{cy - 4}" fill="none" stroke="#1C1410" stroke-width="{lidw}" stroke-linecap="round"/>'
    s += f'<path d="{almond}" fill="none" stroke="#1C1410" stroke-width="2.5"/>'
    return s


# ---------------------------------------------------------------- MISHTI
MISHTI_DEFS = ('<pattern id="mf@" width="20" height="14" patternUnits="userSpaceOnUse" patternTransform="translate({ph},0)">'
               '<rect width="20" height="14" fill="#E07A2E"/><path d="M0 14 Q10 0 20 14" stroke="#8A3B12" stroke-width="2" fill="none"/></pattern>')


def mishti_head(eye_o=0.45, gaze=(0, 0), pupil=3.0, ears=0.0, mouth='none', mouth_a=0.0):
    ear_l = f'<g transform="rotate({-ears:.1f} 160 132)"><path d="M134 150 L140 80 L184 122Z" fill="#E07A2E"/><path d="M146 136 L148 100 L170 122Z" fill="#E58BA0" stroke-width="2"/></g>'
    ear_r = f'<g transform="rotate({ears:.1f} 232 132)"><path d="M208 122 L252 80 L258 150Z" fill="#E07A2E"/><path d="M222 124 L244 100 L246 132Z" fill="#E58BA0" stroke-width="2"/></g>'
    s = ear_l + ear_r
    s += '<ellipse cx="196" cy="176" rx="74" ry="62" fill="#E07A2E"/>'
    s += '<path d="M196 120 L196 136 M182 122 L186 136 M210 122 L206 136" stroke="#8A3B12" stroke-width="5"/>'
    gx, gy = gaze
    for ex in (170, 222):
        s += eye(ex, 170, 46, 26, 18, eye_o, pupil, 10, gx, gy, '#9BD06A', '#E07A2E', lidw=5, glint=pupil > 2.5)
    s += '<ellipse cx="196" cy="206" rx="26" ry="16" fill="#FBF5E9" stroke-width="3"/>'
    s += '<path d="M187 196 L205 196 L196 205Z" fill="#E58BA0" stroke-width="3"/>'
    if mouth == 'meow':
        h = 6 + 18 * mouth_a
        s += f'<path d="M184 208 Q196 {208 + h * 1.6:.1f} 208 208Z" fill="#7A1F1F" stroke-width="3"/>'
    elif mouth == 'hiss':
        s += '<path d="M178 206 Q196 236 214 206Z" fill="#7A1F1F" stroke-width="3"/><path d="M184 207 L188 217 L191 207Z M201 207 L204 217 L208 207Z" fill="#FBF5E9" stroke-width="1.5"/>'
    else:
        s += '<path d="M196 205 Q191 215 180 211 M196 205 Q201 215 212 211" fill="none" stroke-width="3"/>'
    s += '<path d="M164 202 L110 194 M164 208 L112 214 M228 202 L282 194 M228 208 L280 214" stroke-width="2.5"/>'
    s += '<path d="M146 238 Q196 268 246 238" fill="none" stroke-width="12"/><path d="M146 238 Q196 268 246 238" fill="none" stroke="#C8341F" stroke-width="7"/>'
    s += '<circle cx="196" cy="262" r="10" fill="#E3A92B"/>'
    return s


def mishti(t=0.0, eye_o=0.45, gaze=(0, 0), pupil=3.0, ears=0.0, mouth='none', mouth_a=0.0,
           tail=0.0, phase=0.0, pose='sit', step=0.0, head_rot=0.0):
    """Origin = ground under the cat's centre. Sitting cat is ~330 units tall."""
    d = MISHTI_DEFS.replace('{ph}', f'{phase:.1f}')
    s = f'<defs>{d}</defs><g transform="translate(-196,-395)" stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    head = mishti_head(eye_o, gaze, pupil, ears, mouth, mouth_a)
    if pose == 'sit':
        ta = tail
        s += (f'<g transform="rotate({ta:.1f} 262 360)"><path d="M262 372 Q344 352 322 260 Q314 230 296 240 '
              f'Q308 262 302 292 Q292 340 250 346Z" fill="url(#mf@)"/></g>')
        s += '<path d="M118 398 Q96 300 150 236 L242 236 Q296 300 274 398Z" fill="url(#mf@)"/>'
        s += '<path d="M160 244 Q196 312 232 244 Q196 266 160 244Z" fill="#FBF5E9"/>'
        s += '<ellipse cx="172" cy="392" rx="20" ry="9" fill="#E07A2E"/><ellipse cx="220" cy="392" rx="20" ry="9" fill="#E07A2E"/>'
        s += f'<g transform="rotate({head_rot:.1f} 196 240)">{head}</g>'
    else:  # leap / run: horizontal body facing left
        k = math.sin(step * math.pi * 2)
        legs_f = f'M150 318 L{92 + 10 * k:.0f} {330 - 8 * k:.0f} M170 330 L{112 - 10 * k:.0f} {356 + 6 * k:.0f}'
        legs_b = f'M300 330 L{350 + 12 * k:.0f} {372 - 6 * k:.0f} M318 318 L{372 - 10 * k:.0f} {350 + 8 * k:.0f}'
        if pose == 'leap':
            legs_f = 'M150 318 L70 300 M168 330 L84 330'
            legs_b = 'M300 330 L380 362 M318 318 L392 336'
        s += f'<path d="{legs_b}" fill="none" stroke-width="22"/><path d="{legs_b}" fill="none" stroke="#E07A2E" stroke-width="14"/>'
        s += '<path d="M330 296 Q390 270 432 220" fill="none" stroke-width="26"/><path d="M330 296 Q390 270 432 220" fill="none" stroke="#E07A2E" stroke-width="18"/>'
        s += '<ellipse cx="240" cy="306" rx="118" ry="56" fill="url(#mf@)"/>'
        s += f'<path d="{legs_f}" fill="none" stroke-width="22"/><path d="{legs_f}" fill="none" stroke="#E07A2E" stroke-width="14"/>'
        s += f'<g transform="translate(-60,64) rotate(-12 196 176) scale(0.92) translate(17,15)">{head}</g>'
    s += '</g>'
    return s


# ---------------------------------------------------------------- MECHHO BHOOT
MECHHO_DEFS = ('<pattern id="bn@" width="34" height="20" patternUnits="userSpaceOnUse" patternTransform="translate({bx},{by})">'
               '<rect width="34" height="20" fill="#EAF1F2"/><path d="M4 10 L30 10 M10 4 L14 10 L10 16 M18 4 L22 10 L18 16" stroke="#2C3E8C" stroke-width="2" fill="none"/></pattern>'
               '<pattern id="fs@" width="40" height="26" patternUnits="userSpaceOnUse" patternTransform="translate({fx},0)">'
               '<rect width="40" height="26" fill="#EAF1F2"/><path d="M8 13 Q16 5 24 13 Q16 21 8 13Z M24 13 L31 7 L31 19Z" fill="#E07A2E" stroke="#8A3B12" stroke-width="1.5"/>'
               '<circle cx="13" cy="12" r="1.5" fill="#1C1410"/></pattern>')


def mechho_body_path(ph, amp=8.0):
    w = lambda k: amp * math.sin(ph + k)
    return (f"M150 112 Q230 104 240 196 Q246 256 228 300 Q{216 + w(0):.1f} 330 {240 + w(1):.1f} 362 "
            f"Q{206 + w(2):.1f} 352 {194 + w(2.5):.1f} 384 Q{172 + w(3):.1f} 352 {150 + w(3.6):.1f} 374 "
            f"Q{138 + w(4.2):.1f} 342 {112 + w(5):.1f} 352 Q126 300 108 258 Q84 176 150 112Z")


def mechho(t=0.0, mood='hungry', gaze=(0, 0), mouth='grin', mouth_a=0.0, rattle=0.0, fish_t=0.0,
           holding='fish', sweet_p=0.0, tears=0.0, glow=0.0, wave=0.0, eye_o=1.0):
    """Origin = body centre (165,240 in drawing units). Ghost ~280 units tall."""
    bx = rattle * math.sin(t * 50)
    by = rattle * math.cos(t * 43)
    d = MECHHO_DEFS.replace('{bx}', f'{bx:.1f}').replace('{by}', f'{by:.1f}').replace('{fx}', f'{(t * 30) % 40:.1f}')
    ph = t * 4.2
    body = mechho_body_path(ph)
    s = f'<g transform="translate({-165 + bx * 0.8:.1f},{-240 + by * 0.6:.1f})" stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    if glow > 0:
        s += f'<path d="{body}" fill="none" stroke="#FFC94A" stroke-width="22" opacity="{0.45 * glow:.2f}"/>'
    # back arm (wave)
    if holding == 'fish':
        arm = 'M110 230 Q86 260 120 286'
    elif holding == 'sweet':
        arm = 'M112 230 Q92 250 110 272'
    else:
        a = wave
        arm = f'M112 228 Q{80 + 10 * math.sin(a):.0f} {200 - 20 * math.cos(a):.0f} {70 + 20 * math.sin(a):.0f} {170 + 10 * math.cos(a):.0f}'
    s += f'<path d="{arm}" fill="none" stroke-width="16"/><path d="{arm}" fill="none" stroke="#FFFFFF" stroke-width="9"/>'
    s += f'<path d="{body}" fill="#FFFFFF"/>'
    gx, gy = gaze
    if mood == 'happy':
        s += '<path d="M130 174 Q150 154 170 174 M182 174 Q202 154 222 174" fill="none" stroke-width="7"/>'
    else:
        pr = {'hungry': 9, 'scared': 4.5, 'flat': 8}.get(mood, 9)
        up = 30 if mood == 'scared' else 24
        for ex in (150, 202):
            s += eye(ex, 172, 46, up, 16, eye_o, pr, pr, gx, gy, '#FFFFFF', '#FFFFFF', lidw=6)
    if tears > 0:
        for i, (ex, ey) in enumerate(((130, 186), (222, 186))):
            for j in range(3):
                k = (t * 1.3 + j / 3 + i * 0.17) % 1
                yy = ey + k * 70
                s += f'<path d="M{ex} {yy:.1f} q-6 10 0 14 q6 -4 0 -14Z" fill="#9CC7C9" stroke-width="2" opacity="{tears * (1 - k):.2f}"/>'
    if mouth == 'grin':
        s += '<path d="M140 206 Q178 244 216 206 Q178 222 140 206Z" fill="#1C1410"/>'
        drip = 12 + 8 * math.sin(t * 3)
        s += f'<path d="M168 222 L168 {236 + drip:.1f} Q172 {244 + drip:.1f} 176 {236 + drip:.1f} L176 224" fill="#BFE3EE" stroke-width="3"/>'
    elif mouth == 'scream':
        h = 22 + 10 * mouth_a
        s += f'<ellipse cx="178" cy="228" rx="22" ry="{h:.1f}" fill="#1C1410"/><ellipse cx="178" cy="{228 + h * 0.5:.1f}" rx="12" ry="{h * 0.3:.1f}" fill="#C8341F" stroke="none"/>'
    elif mouth == 'talk':
        h = 3 + 20 * mouth_a
        s += f'<path d="M156 214 Q178 {214 + h * 1.8:.1f} 200 214 Q178 {218:.0f} 156 214Z" fill="#1C1410"/>'
    elif mouth == 'smile':
        s += '<path d="M150 212 Q178 236 206 212" fill="none" stroke-width="5"/>'
    elif mouth == 'O':
        s += '<ellipse cx="178" cy="220" rx="10" ry="13" fill="#1C1410"/>'
    elif mouth == 'chew':
        h = 6 + 6 * abs(math.sin(t * 9))
        s += f'<ellipse cx="178" cy="218" rx="12" ry="{h:.1f}" fill="#1C1410"/>'
    elif mouth == 'wobble':
        s += f'<path d="M150 218 Q164 {208 + 4 * math.sin(t * 20):.1f} 178 218 Q192 {228 + 4 * math.sin(t * 20):.1f} 206 218" fill="none" stroke-width="5"/>'
    # front arm + held item
    if holding == 'fish':
        s += '<g transform="rotate(-8 175 270)">' + fish(175, 270, 1.0) + '</g>'
        s += '<path d="M232 236 Q246 270 200 290" fill="none" stroke-width="16"/><path d="M232 236 Q246 270 200 290" fill="none" stroke="#FFFFFF" stroke-width="9"/>'
    elif holding == 'sweet':
        hx_, hy_ = lerp(250, 186, sweet_p), lerp(270, 222, sweet_p)
        s += f'<path d="M232 236 Q{254 - 30 * sweet_p:.0f} {258 - 20 * sweet_p:.0f} {hx_:.0f} {hy_:.0f}" fill="none" stroke-width="16"/>'
        s += f'<path d="M232 236 Q{254 - 30 * sweet_p:.0f} {258 - 20 * sweet_p:.0f} {hx_:.0f} {hy_:.0f}" fill="none" stroke="#FFFFFF" stroke-width="9"/>'
        if sweet_p < 0.98:
            s += rosogolla(hx_, hy_ - 10, 1.0)
    else:
        s += '<path d="M232 236 Q250 262 236 282" fill="none" stroke-width="16"/><path d="M232 236 Q250 262 236 282" fill="none" stroke="#FFFFFF" stroke-width="9"/>'
    s += '</g>'
    return s


def fish(cx, cy, sc=1.0, color='#9AA6AE'):
    return (f'<g transform="translate({cx},{cy}) scale({sc})"><path d="M-46 0 Q-10 -24 30 0 Q-10 22 -46 0Z" fill="{color}" stroke-width="3"/>'
            f'<path d="M30 0 L50 -14 L46 0 L50 14Z" fill="{color}" stroke-width="3"/>'
            f'<path d="M-14 -16 Q-6 -2 -14 16" fill="none" stroke-width="2"/><circle cx="-32" cy="-3" r="3" fill="#1C1410" stroke="none"/></g>')


def rosogolla(cx, cy, sc=1.0):
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({sc})"><circle r="15" fill="#FBF5E9" stroke-width="3"/>'
            f'<path d="M-7 -6 Q-2 -11 4 -9" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
            f'<path d="M-4 15 q-2 6 1 9" fill="none" stroke="#E3C27A" stroke-width="2"/></g>')


GHOST_HAND = ("M-18 -6 Q-26 18 -17 36 Q-12 44 -8 34 L-6 24 Q-4 44 2 48 Q9 46 6 30 L8 22 Q14 40 21 35 "
              "Q27 28 18 6 Q12 -8 0 -10 Q-12 -10 -18 -6Z")


def ghost_hand(hx_, hy_, ax, ay, rattle=0.0, t=0.0, wave=0.0, holding_fish=False, holding_sweet=False):
    """A wispy pure-white arm from (ax,ay) to a three-fingered hand at (hx,hy). Absolute scene coords."""
    mx, my = (ax + hx_) / 2 + 30, (ay + hy_) / 2
    s = '<g stroke="#1C1410" stroke-linejoin="round" stroke-linecap="round">'
    s += f'<path d="M{ax} {ay} Q{mx} {my} {hx_} {hy_ - 4}" fill="none" stroke-width="30"/><path d="M{ax} {ay} Q{mx} {my} {hx_} {hy_ - 4}" fill="none" stroke="#FFFFFF" stroke-width="22"/>'
    s += f'<g transform="translate({hx_},{hy_}) rotate({wave:.1f})"><path d="{GHOST_HAND}" fill="#FFFFFF" stroke-width="4"/></g>'
    if holding_fish:
        s += f'<g transform="translate({hx_ + 4},{hy_ + 44}) rotate(80)">' + fish(0, 0, 0.9) + '</g>'
    if holding_sweet:
        s += rosogolla(hx_ + 2, hy_ + 44, 1.0)
    s += '</g>'
    return s


# ---------------------------------------------------------------- TUTUL
TUTUL_DEFS = ('<pattern id="kk@" width="24" height="28" patternUnits="userSpaceOnUse"><rect width="24" height="28" fill="#E58BA0"/>'
              '<path d="M12 3 L19 12 L12 21 L5 12Z" fill="#E3A92B" stroke="#C8341F" stroke-width="1.5"/></pattern>')


def kite_small(x, y, s=1.0, r=0.0, op=1.0):
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({r:.1f}) scale({s:.2f})" opacity="{op:.2f}">'
            '<path d="M0 -14 L11 0 L0 14 L-11 0Z" fill="#E3A92B" stroke="#C8341F" stroke-width="2"/>'
            '<path d="M0 14 Q4 22 0 30" fill="none" stroke="#C8341F" stroke-width="1.5"/></g>')


def tutul(t=0.0, eye_o=0.6, gaze=(0, -4), mouth='o', mouth_a=0.0, offer=0.0, kites=0.0, spool=True, head_tilt=0.0):
    """Bust. Origin = bottom centre of the bust (196,400)."""
    d = TUTUL_DEFS
    s = f'<defs>{d}</defs><g transform="translate(-196,-400)" stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    s += '<path d="M96 404 Q100 318 158 302 L234 302 Q290 318 296 404Z" fill="url(#kk@)"/>'
    s += '<path d="M180 248 L180 308 Q196 314 212 308 L212 248Z" fill="#C29068"/>'
    s += '<path d="M160 304 Q196 326 232 304" fill="none"/>'
    if spool:
        s += '<g transform="translate(-10,0)"><rect x="96" y="336" width="50" height="56" rx="4" fill="#8A3B12"/><ellipse cx="121" cy="336" rx="29" ry="8" fill="#E3A92B"/><ellipse cx="121" cy="392" rx="29" ry="8" fill="#E3A92B"/></g>'
    s += f'<g transform="rotate({head_tilt:.1f} 196 300)">'
    s += '<circle cx="130" cy="196" r="12" fill="#C29068"/><circle cx="262" cy="196" r="12" fill="#C29068"/>'
    s += '<ellipse cx="196" cy="190" rx="64" ry="62" fill="#C29068"/>'
    s += '<path d="M130 196 Q126 120 196 118 Q266 120 262 196 L254 172 L138 172Z" fill="#1C1410"/>'
    gx, gy = gaze
    for ex in (168, 224):
        s += eye(ex, 192, 38, 30, 18, eye_o, 8, 8, gx, gy, '#FBF5E9', '#C29068', lidw=5)
    s += '<path d="M196 196 L193 214 Q196 218 201 215" fill="none"/>'
    if mouth == 'o' or mouth == 'talk':
        ry = 3 + 9 * mouth_a if mouth == 'talk' else 8
        s += f'<ellipse cx="200" cy="236" rx="7" ry="{ry:.1f}" fill="#1C1410"/>'
    elif mouth == 'smile':
        s += '<path d="M184 232 Q200 246 216 232" fill="none" stroke-width="4"/>'
    elif mouth == 'yawn':
        s += f'<ellipse cx="200" cy="238" rx="10" ry="{6 + 10 * mouth_a:.1f}" fill="#1C1410"/>'
    s += '<g fill="#E58BA0" opacity="0.6" stroke="none"><ellipse cx="156" cy="216" rx="11" ry="6"/><ellipse cx="238" cy="216" rx="11" ry="6"/></g>'
    s += '</g>'
    if offer > 0:
        hx_, hy_ = lerp(262, 372, offer), lerp(340, 268, offer)
        s += f'<path d="M262 318 Q{300 + 40 * offer:.0f} {330 - 10 * offer:.0f} {hx_:.0f} {hy_:.0f}" fill="none" stroke-width="22"/>'
        s += f'<path d="M262 318 Q{300 + 40 * offer:.0f} {330 - 10 * offer:.0f} {hx_:.0f} {hy_:.0f}" fill="none" stroke="#E58BA0" stroke-width="14"/>'
        s += f'<circle cx="{hx_:.0f}" cy="{hy_:.0f}" r="13" fill="#C29068"/>'
    s += '</g>'
    if offer > 0:
        hx_, hy_ = lerp(262, 372, offer), lerp(340, 268, offer)
        s += rosogolla(hx_ - 196, hy_ - 400 - 22, 1.0)
    if kites > 0:
        for i in range(6):
            k = (kites + i / 6) % 1
            x = -80 + i * 32 + 20 * math.sin(k * 6 + i)
            y = -60 - k * 300
            s += kite_small(x, y, 0.9 + 0.3 * k, 20 * math.sin(k * 5 + i), (1 - k) * min(1, kites * 3))
    return s


def rope_halo(cx, cy, rx, ry, grow=1.0):
    if grow <= 0:
        return ''
    sc = lerp(0.85, 1.0, grow)
    op = clamp(grow * 1.4)
    e = f'cx="{cx}" cy="{cy}" rx="{rx * sc:.1f}" ry="{ry * sc:.1f}" fill="none"'
    return (f'<g opacity="{op:.2f}"><ellipse {e} stroke="#FFC94A" stroke-width="30" opacity="0.25"/>'
            f'<ellipse {e} stroke="#1C1410" stroke-width="16"/><ellipse {e} stroke="#FBF5E9" stroke-width="10"/>'
            f'<ellipse {e} stroke="#1C1410" stroke-width="10" stroke-dasharray="2 9"/></g>')


def tutul_full(t=0.0, eye_o=0.6, gaze=(0, -4), mouth='o', mouth_a=0.0, offer=0.0, kites=0.0, step=0.0):
    """Full-body Tutul (5 yrs). Origin = between his feet. ~510 units tall."""
    s = f'<defs>{TUTUL_DEFS}</defs><g transform="translate(-196,-640)" stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    # legs (pyjama pants) + bare feet
    sw = 10 * math.sin(step * math.pi * 2)
    s += f'<path d="M170 520 L{166 - sw:.0f} 612 L188 612 L194 520Z" fill="#F3B6C4"/>'
    s += f'<path d="M198 520 L{204 + sw:.0f} 612 L226 612 L222 520Z" fill="#F3B6C4"/>'
    s += f'<ellipse cx="{170 - sw:.0f}" cy="624" rx="22" ry="11" fill="#C29068"/><ellipse cx="{222 + sw:.0f}" cy="624" rx="22" ry="11" fill="#C29068"/>'
    # back arm holding the kite spool
    s += '<path d="M150 318 Q118 380 124 444" fill="none" stroke-width="24"/><path d="M150 318 Q118 380 124 444" fill="none" stroke="#E58BA0" stroke-width="16"/>'
    s += '<circle cx="124" cy="452" r="13" fill="#C29068"/>'
    s += '<rect x="100" y="456" width="46" height="50" rx="4" fill="#8A3B12"/><ellipse cx="123" cy="456" rx="27" ry="7" fill="#E3A92B"/><ellipse cx="123" cy="506" rx="27" ry="7" fill="#E3A92B"/>'
    # oversized shirt
    s += '<path d="M150 304 L242 304 Q262 340 266 528 Q196 544 126 528 Q130 340 150 304Z" fill="url(#kk@)"/>'
    s += '<path d="M168 304 Q196 322 224 304" fill="none"/>'
    s += '<path d="M184 276 L184 308 Q196 314 208 308 L208 276Z" fill="#C29068"/>'
    # front arm: rests or offers the sweet
    hx_, hy_ = lerp(250, 340, offer), lerp(452, 300, offer)
    ex_, ey_ = lerp(262, 300, offer), lerp(390, 330, offer)
    arm = f'M242 318 Q{ex_:.0f} {ey_:.0f} {hx_:.0f} {hy_:.0f}'
    s += f'<path d="{arm}" fill="none" stroke-width="24"/><path d="{arm}" fill="none" stroke="#E58BA0" stroke-width="16"/>'
    s += f'<circle cx="{hx_:.0f}" cy="{hy_ + 6:.0f}" r="13" fill="#C29068"/>'
    # head (same design as the bible portrait), lowered for a short neck
    s += '<g transform="translate(0,32)">'
    s += '<circle cx="130" cy="196" r="12" fill="#C29068"/><circle cx="262" cy="196" r="12" fill="#C29068"/>'
    s += '<ellipse cx="196" cy="190" rx="64" ry="62" fill="#C29068"/>'
    s += '<path d="M130 196 Q126 120 196 118 Q266 120 262 196 L254 172 L138 172Z" fill="#1C1410"/>'
    gx, gy = gaze
    for ex in (168, 224):
        s += eye(ex, 192, 38, 30, 18, eye_o, 8, 8, gx, gy, '#FBF5E9', '#C29068', lidw=5)
    s += '<path d="M196 196 L193 214 Q196 218 201 215" fill="none"/>'
    if mouth in ('o', 'talk'):
        ry = 3 + 9 * mouth_a if mouth == 'talk' else 8
        s += f'<ellipse cx="200" cy="236" rx="7" ry="{ry:.1f}" fill="#1C1410"/>'
    elif mouth == 'smile':
        s += '<path d="M184 232 Q200 246 216 232" fill="none" stroke-width="4"/>'
    elif mouth == 'yawn':
        s += f'<ellipse cx="200" cy="238" rx="10" ry="{6 + 10 * mouth_a:.1f}" fill="#1C1410"/>'
    s += '<g fill="#E58BA0" opacity="0.6" stroke="none"><ellipse cx="156" cy="216" rx="11" ry="6"/><ellipse cx="238" cy="216" rx="11" ry="6"/></g>'
    s += '</g></g>'
    if offer > 0.05:
        s += rosogolla(hx_ - 196, hy_ - 640 - 14, 1.0)
    if kites > 0:
        for i in range(6):
            k = (kites + i / 6) % 1
            x = 70 + i * 22 + 30 * math.sin(k * 6 + i) + k * 60
            y = -180 - k * 300
            s += kite_small(x, y, 0.9 + 0.3 * k, 20 * math.sin(k * 5 + i), (1 - k) * min(1, kites * 3))
    return s
