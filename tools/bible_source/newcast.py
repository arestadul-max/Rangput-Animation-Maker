"""New townsfolk characters for the Rongpat bible (boards 21-23). Full body, short necks, shared scale."""
from fullbody import *

INKS = 'stroke="#1C1410" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'
CONCH = '#FBF5E9'
GREY_HAIR = '#D9D2C2'
KHAKI = '#B8A070'
KHAKI_D = '#8A7448'

PATTERNS = {
    'n-math': '<pattern id="n-math" width="26" height="26" patternUnits="userSpaceOnUse"><rect width="26" height="26" fill="#FBF5E9"/><path d="M3 7 L11 7 M7 3 L7 11 M16 16 L22 22 M22 16 L16 22" stroke="#2C3E8C" stroke-width="2"/></pattern>',
    'n-hex': '<pattern id="n-hex" width="30" height="26" patternUnits="userSpaceOnUse"><rect width="30" height="26" fill="#1F7A78"/><path d="M8 4 L16 4 L20 11 L16 18 L8 18 L4 11Z" fill="none" stroke="#E3A92B" stroke-width="2"/><circle cx="12" cy="11" r="2" fill="#FBF5E9"/></pattern>',
    'n-ring': '<pattern id="n-ring" width="28" height="28" patternUnits="userSpaceOnUse"><rect width="28" height="28" fill="#B5482A"/><circle cx="14" cy="14" r="10" fill="none" stroke="#E3A92B" stroke-width="2"/><circle cx="14" cy="14" r="5" fill="none" stroke="#FBF5E9" stroke-width="2"/></pattern>',
    'n-moon': '<pattern id="n-moon" width="26" height="26" patternUnits="userSpaceOnUse"><rect width="26" height="26" fill="#22305F"/><path d="M9 4 Q3 10 9 16 Q4 16 4 10 Q4 5 9 4Z" fill="#FBF5E9"/><circle cx="19" cy="19" r="2.2" fill="#E3A92B"/></pattern>',
    'n-lchk': '<pattern id="n-lchk" width="22" height="22" patternUnits="userSpaceOnUse"><rect width="22" height="22" fill="#3E7A3A"/><path d="M0 6 L22 6 M6 0 L6 22" stroke="#26502A" stroke-width="5"/><path d="M0 16 L22 16 M16 0 L16 22" stroke="#FBF5E9" stroke-width="1.5"/></pattern>',
    'n-gam': '<pattern id="n-gam" width="16" height="16" patternUnits="userSpaceOnUse"><rect width="16" height="16" fill="#FBF5E9"/><path d="M0 4 L16 4 M4 0 L4 16" stroke="#C8341F" stroke-width="3"/><path d="M0 11 L16 11 M11 0 L11 16" stroke="#C8341F" stroke-width="1.5"/></pattern>',
    'n-rick': '<pattern id="n-rick" width="32" height="32" patternUnits="userSpaceOnUse"><rect width="32" height="32" fill="#2C3E8C"/><g transform="translate(16 16)"><path d="M0 -10 Q5 -4 0 0 Q-5 -4 0 -10Z M10 0 Q4 5 0 0 Q4 -5 10 0Z M0 10 Q-5 4 0 0 Q5 4 0 10Z M-10 0 Q-4 -5 0 0 Q-4 5 -10 0Z" fill="#E58BA0" stroke="#1C1410" stroke-width="1"/><circle r="2.6" fill="#E3A92B"/></g><circle cx="2" cy="2" r="2" fill="#FBF5E9"/></pattern>',
    'n-tri': '<pattern id="n-tri" width="24" height="22" patternUnits="userSpaceOnUse"><rect width="24" height="22" fill="#C8341F"/><path d="M2 18 L12 4 L22 18Z" fill="#E3A92B" stroke="#1C1410" stroke-width="1.5"/></pattern>',
    'n-dot': '<pattern id="n-dot" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="20" height="20" fill="#C8341F"/><circle cx="6" cy="6" r="4" fill="#F3D9A0"/><circle cx="16" cy="16" r="3" fill="#E3A92B"/></pattern>',
    'n-beat': '<pattern id="n-beat" width="44" height="22" patternUnits="userSpaceOnUse"><rect width="44" height="22" fill="#FBF5E9"/><path d="M0 12 L12 12 L16 4 L20 19 L24 12 L44 12" fill="none" stroke="#C8341F" stroke-width="2"/></pattern>',
    'n-plus': '<pattern id="n-plus" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="20" height="20" fill="#FBF5E9"/><path d="M10 5 L10 15 M5 10 L15 10" stroke="#1F7A78" stroke-width="2.5"/></pattern>',
    'n-chev': '<pattern id="n-chev" width="20" height="16" patternUnits="userSpaceOnUse"><rect width="20" height="16" fill="#B8A070"/><path d="M2 12 L10 5 L18 12" fill="none" stroke="#8A7448" stroke-width="2.5"/></pattern>',
    'n-env': '<pattern id="n-env" width="26" height="20" patternUnits="userSpaceOnUse"><rect width="26" height="20" fill="#C8341F"/><rect x="4" y="4" width="18" height="12" fill="none" stroke="#FBF5E9" stroke-width="1.5"/><path d="M4 4 L13 11 L22 4" fill="none" stroke="#FBF5E9" stroke-width="1.5"/></pattern>',
}


# ------------------------------------------------------------------ head kit (head space, face centre 196,170)
def ears(skin, rx=56):
    return (f'<ellipse cx="{196 - rx - 2}" cy="174" rx="10" ry="16" fill="{skin}"/>'
            f'<ellipse cx="{196 + rx + 2}" cy="174" rx="10" ry="16" fill="{skin}"/>')


def face(skin, rx=56, ry=68):
    return f'<ellipse cx="196" cy="170" rx="{rx}" ry="{ry}" fill="{skin}"/>', 170 + ry


def eyes(kind='normal', gx=0, gy=0, skin='#B98258'):
    L = 'M156 166 Q171 154 186 166 Q171 174 156 166Z'
    R = 'M206 166 Q221 154 236 166 Q221 174 206 166Z'
    if kind == 'happy':
        return ('<path d="M156 170 Q171 154 186 170" fill="none" stroke-width="6"/>'
                '<path d="M206 170 Q221 154 236 170" fill="none" stroke-width="6"/>'), ''
    s = f'<path d="{L}" fill="{CONCH}" stroke-width="3"/><path d="{R}" fill="{CONCH}" stroke-width="3"/>'
    s += (f'<circle cx="{171 + gx}" cy="{165 + gy}" r="6" fill="#1C1410" stroke="none"/>'
          f'<circle cx="{221 + gx}" cy="{165 + gy}" r="6" fill="#1C1410" stroke="none"/>')
    if kind == 'sleepy':
        s += (f'<path d="M153 167 Q171 151 189 167Z" fill="{skin}" stroke="none"/><path d="M203 167 Q221 151 239 167Z" fill="{skin}" stroke="none"/>'
              '<path d="M153 167 Q171 162 189 167" fill="none" stroke-width="5"/><path d="M203 167 Q221 162 239 167" fill="none" stroke-width="5"/>')
        return s, ''
    s += ('<path d="M152 164 Q171 150 190 164" fill="none" stroke-width="5"/>'
          '<path d="M202 164 Q221 150 240 164" fill="none" stroke-width="5"/>')
    glint = (f'<circle cx="{173 + gx}" cy="{163 + gy}" r="2" fill="{CONCH}"/>'
             f'<circle cx="{223 + gx}" cy="{163 + gy}" r="2" fill="{CONCH}"/>')
    return s, glint


BROWS = {
    'plain': '<path d="M154 142 L186 138" stroke-width="5"/><path d="M206 138 L238 142" stroke-width="5"/>',
    'stern': '<path d="M152 136 L188 146" stroke-width="6"/><path d="M204 146 L240 136" stroke-width="6"/>',
    'up': '<path d="M154 134 Q170 126 186 132" fill="none" stroke-width="5"/><path d="M206 132 Q222 126 238 134" fill="none" stroke-width="5"/>',
    'one_up': '<path d="M154 136 Q170 126 186 132" fill="none" stroke-width="5"/><path d="M206 140 L238 142" stroke-width="5"/>',
    'thick': '<path d="M150 146 L190 143" stroke-width="8"/><path d="M202 143 L242 146" stroke-width="8"/>',
}
NOSE = '<path d="M196 168 L190 202 Q196 208 204 204" fill="none"/>'


def bushy(color):
    return (f'<path d="M150 142 Q170 128 190 142 L186 149 Q170 138 152 148Z" fill="{color}" stroke-width="3"/>'
            f'<path d="M242 142 Q222 128 202 142 L206 149 Q222 138 240 148Z" fill="{color}" stroke-width="3"/>')


def head_svg(aria, parts_behind, skin, hair, eye_kind, gx, gy, brows, mouth, extras='', rx=56, ry=68, after=''):
    e, glint = eyes(eye_kind, gx, gy, skin)
    f, chin = face(skin, rx, ry)
    inner = (f'<g {INKS}>{parts_behind}{ears(skin, rx)}{f}{hair}{e}{brows}{NOSE}{mouth}{extras}</g>{glint}{after}')
    return f'<svg class="art" aria-label="{aria}">{inner}</svg>', chin


# ------------------------------------------------------------------ bodies
def coat_panels(sy, length):
    return (f'<path d="M146 {sy + 2} L130 {sy + length} L174 {sy + length} L180 {sy + 40} L168 {sy + 4}Z" fill="{CONCH}"/>'
            f'<path d="M246 {sy + 2} L262 {sy + length} L218 {sy + length} L212 {sy + 40} L224 {sy + 4}Z" fill="{CONCH}"/>')


def scarf(sy, fill):
    return (f'<path d="M146 {sy} Q196 {sy + 36} 246 {sy} L250 {sy + 16} Q196 {sy + 52} 142 {sy + 16}Z" fill="{fill}"/>'
            f'<path d="M220 {sy + 26} L246 {sy + 20} L250 {sy + 120} L222 {sy + 120}Z" fill="{fill}"/>')


def u_neck(sy, skin):
    return f'<path d="M172 {sy - 2} Q196 {sy + 44} 220 {sy - 2}Z" fill="{skin}"/>'


def b_anko(sy, hip, feet, skin):
    s = legs(hip, feet, CONCH, w=36) + feet_kind(feet, 'nagra', '#1C1410', skin)
    s += tunic(sy, 262, 'url(#n-math)', flare=10)
    s += f'<path d="M196 {sy + 6} L196 {sy + 96}" stroke-width="3"/>'
    s += ''.join(f'<circle cx="196" cy="{sy + 30 + k * 24}" r="3" fill="#1C1410" stroke="none"/>' for k in range(3))
    s += f'<path d="M224 {sy + 56} L226 {sy + 30}" stroke-width="9"/><path d="M224 {sy + 56} L226 {sy + 30}" stroke="#C8341F" stroke-width="4"/>'
    s += f'<rect x="212" y="{sy + 52}" width="32" height="32" fill="{CONCH}" stroke-width="3"/>'
    ticks = ''.join(f'<path d="M84 {sy - 170 + k * 22} L92 {sy - 170 + k * 22}" stroke-width="2.5"/>' for k in range(10))
    s += f'<g transform="rotate(-12 92 {sy + 14})"><rect x="84" y="{sy - 190}" width="18" height="232" fill="#E3A92B"/>{ticks}</g>'
    s += arm((140, sy + 14), (104, sy + 84), (92, sy + 10), CONCH, skin)
    s += arm((252, sy + 14), (282, sy + 104), (272, sy + 186), CONCH, skin)
    s += f'<rect x="262" y="{sy + 194}" width="22" height="9" rx="2" fill="{CONCH}" stroke-width="2.5"/>'
    s += ''.join(f'<circle cx="{262 + dx}" cy="{sy + 214 + dy}" r="2.5" fill="{CONCH}" stroke="none"/>' for dx, dy in ((2, 4), (14, 12), (24, 2), (8, 22), (20, 28)))
    return s


def b_mitali(sy, hip, feet, skin):
    s = sari_skirt(sy + 150, feet, 'url(#n-hex)', '#E3A92B') + feet_kind(feet, 'chappal', '#C8341F', skin, spread=20)
    s += tunic(sy, 170, '#1F7A78', flare=2) + aanchal(sy, 'url(#n-hex)', '#E3A92B')
    s += coat_panels(sy, 300)
    s += f'<rect x="226" y="{sy + 70}" width="26" height="26" fill="{CONCH}" stroke-width="3"/><path d="M232 {sy + 72} L232 {sy + 52} M244 {sy + 72} L246 {sy + 54}" stroke="#2C3E8C" stroke-width="4"/>'
    # flask held by the neck, glowing
    s += f'<circle cx="80" cy="{sy + 134}" r="34" fill="#FFC94A" opacity="0.35" stroke="none"/>'
    s += f'<path d="M72 {sy + 82} L88 {sy + 82} L88 {sy + 108} Q108 {sy + 116} 106 {sy + 138} Q104 {sy + 162} 80 {sy + 162} Q56 {sy + 162} 54 {sy + 138} Q52 {sy + 116} 72 {sy + 108}Z" fill="#E6F2E0"/>'
    s += f'<path d="M57 {sy + 136} Q80 {sy + 128} 103 {sy + 136} Q102 {sy + 158} 80 {sy + 158} Q58 {sy + 158} 57 {sy + 136}Z" fill="#3E7A3A" stroke-width="2.5"/>'
    s += ''.join(f'<circle cx="{x}" cy="{sy + y}" r="{r}" fill="{CONCH}" stroke-width="2.5"/>' for x, y, r in ((84, 64, 6), (72, 42, 8), (88, 16, 10)))
    s += arm((140, sy + 14), (112, sy + 104), (80, sy + 88), CONCH, skin)
    s += arm((252, sy + 14), (290, sy + 92), (252, sy + 150), CONCH, skin)
    return s


def b_jogen(sy, hip, feet, skin):
    s = f'<path d="M150 {feet - 44} L152 {feet - 6} L176 {feet - 6} L176 {feet - 44}Z M216 {feet - 44} L216 {feet - 6} L240 {feet - 6} L242 {feet - 44}Z" fill="{skin}"/>'
    s += f'<path d="M140 {hip - 20} L252 {hip - 20} L262 {feet - 40} L214 {feet - 36} L196 {hip + 70} L178 {feet - 36} L130 {feet - 40}Z" fill="{CONCH}"/>'
    s += f'<path d="M204 {hip} L212 {feet - 40}" fill="none" stroke-width="2.5"/>'
    s += feet_kind(feet, 'chappal', '#5A3A22', skin)
    s += tunic(sy, 205, KHAKI, flare=4, half=56)
    s += f'<path d="M150 {sy - 2} Q196 {sy + 26} 240 {sy - 2} L246 {sy + 14} Q196 {sy + 44} 144 {sy + 14}Z" fill="url(#n-ring)"/>'
    s += f'<path d="M218 {sy + 24} L244 {sy + 16} L250 {sy + 132} L222 {sy + 132}Z" fill="url(#n-ring)"/>'
    # school gong on a cord
    s += f'<path d="M108 {sy + 20} L108 {sy + 70}" stroke-width="3"/>'
    s += f'<circle cx="108" cy="{sy + 116}" r="46" fill="#E3A92B"/><circle cx="108" cy="{sy + 116}" r="30" fill="none" stroke-width="3"/><circle cx="108" cy="{sy + 116}" r="11" fill="#E07A2E"/>'
    s += f'<path d="M48 {sy + 84} Q38 {sy + 116} 48 {sy + 148} M34 {sy + 72} Q20 {sy + 116} 34 {sy + 160}" fill="none" stroke-width="4"/>'
    s += arm((140, sy + 14), (104, sy + 60), (108, sy + 8), KHAKI, skin, short=True)
    s += f'<path d="M300 {sy - 70} L346 {sy - 112}" stroke-width="11"/><path d="M300 {sy - 70} L346 {sy - 112}" stroke="#8A3B12" stroke-width="5"/>'
    s += f'<ellipse cx="352" cy="{sy - 118}" rx="17" ry="13" fill="{CONCH}" transform="rotate(45 352 {sy - 118})"/>'
    s += f'<path d="M330 {sy - 150} Q350 {sy - 160} 372 {sy - 150} M322 {sy - 168} Q350 {sy - 182} 380 {sy - 168}" fill="none" stroke-width="4"/>'
    s += arm((252, sy + 14), (292, sy - 20), (298, sy - 82), KHAKI, skin, short=True)
    return s


def b_robin(sy, hip, feet, skin):
    s = legs(hip, feet, '#22305F') + feet_kind(feet, 'boot', '#1C1410', skin)
    s += tunic(sy, 205, '#2C3E8C', flare=4)
    s += f'<rect x="150" y="{sy + 50}" width="30" height="30" fill="none" stroke-width="3"/><rect x="212" y="{sy + 50}" width="30" height="30" fill="none" stroke-width="3"/>'
    s += f'<path d="M164 {sy + 92} L176 {sy + 92} L176 {sy + 104} L170 {sy + 110} L164 {sy + 104}Z" fill="#E3A92B" stroke-width="2.5"/>'
    s += f'<rect x="132" y="{hip - 26}" width="128" height="18" fill="#1C1410"/><rect x="186" y="{hip - 28}" width="20" height="22" fill="#E3A92B" stroke-width="3"/>'
    s += scarf(sy, 'url(#n-moon)')
    s += f'<path d="M206 {sy + 34} Q214 {sy + 90} 196 {sy + 120}" fill="none" stroke="#E3A92B" stroke-width="3"/><rect x="184" y="{sy + 118}" width="20" height="11" rx="4" fill="#C9D1D6" stroke-width="2.5"/>'
    s += f'<path d="M110 {sy + 40} L112 {feet - 4}" stroke-width="14"/><path d="M110 {sy + 40} L112 {feet - 4}" stroke="#E3A92B" stroke-width="8"/>'
    s += ''.join(f'<path d="M104 {sy + 120 + k * 90} L118 {sy + 120 + k * 90}" stroke-width="3"/>' for k in range(4))
    s += arm((140, sy + 14), (120, sy + 100), (112, sy + 158), '#2C3E8C', skin)
    s += f'<path d="M278 {sy + 216} L296 {sy + 216} L334 {feet} L238 {feet}Z" fill="#FFC94A" opacity="0.55" stroke="none"/>'
    s += f'<rect x="276" y="{sy + 176}" width="22" height="42" rx="4" fill="#8C8C9A"/><rect x="273" y="{sy + 210}" width="28" height="10" rx="3" fill="#FFC94A" stroke-width="2.5"/>'
    s += arm((252, sy + 14), (280, sy + 100), (287, sy + 170), '#2C3E8C', skin)
    return s


def b_montu(sy, hip, feet, skin):
    s = lungi(hip - 20, feet, 'url(#n-lchk)') + feet_kind(feet, 'chappal', '#2C3E8C', skin)
    s += tunic(sy, 210, CONCH, flare=2, half=54) + u_neck(sy, skin)
    s += f'<path d="M136 {sy - 4} L170 {sy - 4} L164 {sy + 186} L132 {sy + 176}Z" fill="url(#n-gam)"/>'
    # kettle with steam swirls
    s += f'<path d="M56 {sy + 150} Q80 {sy + 112} 104 {sy + 150}" fill="none" stroke-width="7"/>'
    s += f'<path d="M54 {sy + 182} L22 {sy + 150} L28 {sy + 144} L60 {sy + 168}Z" fill="#8C8C9A"/>'
    s += f'<path d="M50 {sy + 150} L110 {sy + 150} Q120 {sy + 214} 80 {sy + 218} Q40 {sy + 214} 50 {sy + 150}Z" fill="#8C8C9A"/>'
    s += f'<ellipse cx="80" cy="{sy + 150}" rx="31" ry="7" fill="#C9D1D6"/><circle cx="80" cy="{sy + 140}" r="5" fill="#1C1410" stroke="none"/>'
    for sw in (f'M24 {sy + 140} Q8 {sy + 118} 24 {sy + 100} Q40 {sy + 82} 24 {sy + 62}', f'M40 {sy + 104} Q30 {sy + 90} 42 {sy + 76}'):
        s += f'<path d="{sw}" fill="none" stroke-width="9"/><path d="{sw}" fill="none" stroke="{CONCH}" stroke-width="4"/>'
    s += arm((140, sy + 14), (104, sy + 92), (80, sy + 122), skin, skin, hand=True)
    s += arm((252, sy + 14), (292, sy + 98), (278, sy + 150), skin, skin)
    for k in range(4):
        y0 = sy + 146 - k * 21
        s += f'<path d="M264 {y0} L292 {y0} L289 {y0 - 21} L267 {y0 - 21}Z" fill="#B5482A" stroke-width="3"/>'
    return s


def b_kashem(sy, hip, feet, skin):
    s = legs(hip + 100, feet, skin, w=32) + feet_kind(feet, 'chappal', '#C8341F', skin)
    s += lungi(hip - 20, hip + 158, 'url(#n-rick)')
    s += tunic(sy, 196, CONCH, flare=2, half=52) + u_neck(sy, skin)
    s += f'<path d="M136 {hip - 34} L256 {hip - 34} L258 {hip - 12} L134 {hip - 12}Z" fill="url(#n-gam)"/>'
    s += f'<path d="M98 {sy + 172} L82 {sy + 120} L62 {sy + 92} L88 {sy + 88} L92 {sy + 118} L104 {sy + 170}Z" fill="#E3A92B"/>'
    s += f'<ellipse cx="100" cy="{sy + 194}" rx="15" ry="19" fill="#1C1410"/>'
    s += arm((140, sy + 14), (112, sy + 100), (100, sy + 166), skin, skin)
    s += f'<path d="M322 {sy - 112} Q334 {sy - 92} 326 {sy - 70} M336 {sy - 124} Q352 {sy - 92} 340 {sy - 60}" fill="none" stroke-width="4"/>'
    s += arm((252, sy + 14), (294, sy - 20), (306, sy - 86), skin, skin)
    return s


def b_bablu(sy, hip, feet, skin):
    s = legs(hip, feet, '#5A3A22') + feet_kind(feet, 'shoe', '#1C1410', skin)
    s += tunic(sy, 205, 'url(#n-tri)', belly=26)
    s += f'<path d="M150 {sy - 4} Q196 {sy + 22} 242 {sy - 4} L238 {sy + 124} L218 {sy + 124} L220 {sy + 28} Q196 {sy + 38} 172 {sy + 28} L174 {sy + 124} L154 {sy + 124}Z" fill="{CONCH}"/>'
    s += f'<path d="M156 {sy + 108} L174 {sy + 108} M218 {sy + 108} L238 {sy + 108}" stroke="#2C3E8C" stroke-width="4"/>'
    c = sy + 156
    s += f'<circle cx="196" cy="{c}" r="62" fill="none" stroke-width="20"/><circle cx="196" cy="{c}" r="62" fill="none" stroke="#5A3A22" stroke-width="11"/>'
    s += f'<path d="M196 {c} L140 {c + 22} M196 {c} L252 {c + 22} M196 {c} L196 {c + 60}" stroke-width="9"/><circle cx="196" cy="{c}" r="15" fill="#5A3A22"/><circle cx="196" cy="{c}" r="5" fill="#E3A92B" stroke="none"/>'
    s += arm((140, sy + 14), (118, sy + 96), (140, sy + 122), '#C8341F', skin, short=True)
    s += arm((252, sy + 14), (274, sy + 96), (252, sy + 122), '#C8341F', skin, short=True)
    return s


def b_pintu(sy, hip, feet, skin):
    s = legs(hip, feet, '#2C3E8C', w=34)
    s += f'<rect x="150" y="{feet - 34}" width="40" height="12" fill="#5470B0"/><rect x="200" y="{feet - 34}" width="40" height="12" fill="#5470B0"/>'
    s += feet_kind(feet, 'sneaker', CONCH, skin)
    s += tunic(sy, 190, 'url(#n-dot)', flare=4)
    s += arm((140, sy + 14), (100, sy - 50), (124, sy - 132), '#C8341F', skin, short=True)
    s += arm((252, sy + 14), (292, sy + 86), (288, sy + 34), '#C8341F', skin, short=True)
    s += f'<ellipse cx="290" cy="{sy + 10}" rx="19" ry="15" fill="#F3D9A0"/><ellipse cx="290" cy="{sy + 6}" rx="7" ry="5" fill="#5A3A22"/>'
    s += f'<path d="M300 {sy + 22} Q304 {sy + 40} 300 {sy + 48} Q296 {sy + 40} 300 {sy + 22}Z" fill="#8A3B12" stroke-width="2.5"/>'
    return s


def b_ruksana(sy, hip, feet, skin):
    s = legs(hip, feet, '#E58BA0', w=36) + feet_kind(feet, 'shoe', '#8A3B12', skin)
    s += tunic(sy, 250, 'url(#n-beat)', flare=10)
    s += coat_panels(sy, 306)
    s += f'<path d="M168 {sy + 4} Q158 {sy + 70} 184 {sy + 112} M224 {sy + 4} Q234 {sy + 70} 208 {sy + 112}" fill="none" stroke-width="6"/>'
    s += f'<path d="M184 {sy + 112} Q196 {sy + 132} 208 {sy + 112}" fill="none" stroke-width="6"/><path d="M196 {sy + 128} L196 {sy + 160}" stroke-width="5"/><circle cx="196" cy="{sy + 170}" r="12" fill="#C9D1D6"/>'
    s += f'<g transform="rotate(-10 152 {sy + 150})"><rect x="122" y="{sy + 104}" width="60" height="78" rx="4" fill="#8A3B12"/><rect x="129" y="{sy + 116}" width="46" height="60" fill="{CONCH}" stroke-width="2.5"/>'
    s += f'<path d="M136 {sy + 130} L168 {sy + 130} M136 {sy + 142} L164 {sy + 142} M136 {sy + 154} L160 {sy + 154}" stroke="#2C3E8C" stroke-width="2.5"/><rect x="142" y="{sy + 98}" width="20" height="10" fill="#8C8C9A" stroke-width="2.5"/></g>'
    s += arm((140, sy + 14), (114, sy + 108), (150, sy + 156), CONCH, skin)
    s += arm((252, sy + 14), (278, sy + 110), (268, sy + 190), CONCH, skin)
    s += f'<path d="M274 {sy + 184} L292 {sy + 160}" stroke-width="8"/><path d="M274 {sy + 184} L292 {sy + 160}" stroke="#2C3E8C" stroke-width="4"/>'
    return s


def b_shefali(sy, hip, feet, skin):
    s = sari_skirt(sy + 150, feet, CONCH, '#1F7A78') + feet_kind(feet, 'shoe', CONCH, skin, spread=20)
    s += tunic(sy, 170, CONCH, flare=2) + aanchal(sy, 'url(#n-plus)', '#1F7A78')
    s += f'<circle cx="166" cy="{sy + 56}" r="10" fill="{CONCH}"/><circle cx="166" cy="{sy + 56}" r="6" fill="none" stroke="#1F7A78" stroke-width="2.5"/>'
    s += arm((140, sy + 14), (116, sy + 100), (150, sy + 132), CONCH, skin, short=True)
    s += f'<ellipse cx="128" cy="{sy + 134}" rx="44" ry="9" fill="#C9D1D6"/>'
    s += f'<rect x="102" y="{sy + 98}" width="20" height="34" rx="3" fill="#BFE3EE" stroke-width="3"/>'
    s += ''.join(f'<circle cx="{x}" cy="{sy + 128}" r="5" fill="{c}" stroke-width="2"/>' for x, c in ((136, '#E58BA0'), (148, CONCH), (156, '#E3A92B')))
    s += f'<g transform="rotate(8 256 {sy + 130})"><rect x="230" y="{sy + 96}" width="52" height="68" rx="4" fill="#2C3E8C"/><rect x="236" y="{sy + 106}" width="40" height="52" fill="{CONCH}" stroke-width="2.5"/>'
    s += f'<path d="M242 {sy + 120} L270 {sy + 120} M242 {sy + 132} L266 {sy + 132} M242 {sy + 144} L262 {sy + 144}" stroke="#1F7A78" stroke-width="2.5"/></g>'
    s += arm((252, sy + 14), (278, sy + 100), (248, sy + 146), CONCH, skin, short=True)
    return s


def b_gopal(sy, hip, feet, skin):
    s = legs(hip, feet, KHAKI_D) + feet_kind(feet, 'boot', '#1C1410', skin)
    s += f'<path d="M150 {sy + 150} L58 {sy - 132}" stroke-width="15"/><path d="M150 {sy + 150} L58 {sy - 132}" stroke="#E3A92B" stroke-width="8"/>'
    s += tunic(sy, 205, 'url(#n-chev)', belly=34, half=64)
    s += f'<rect x="128" y="{hip - 26}" width="136" height="18" fill="#1C1410"/><rect x="186" y="{hip - 28}" width="20" height="22" fill="#E3A92B" stroke-width="3"/>'
    s += f'<path d="M228 {sy + 44} L232 {sy + 56} L244 {sy + 56} L234 {sy + 64} L238 {sy + 76} L228 {sy + 68} L218 {sy + 76} L222 {sy + 64} L212 {sy + 56} L224 {sy + 56}Z" fill="#E3A92B" stroke-width="2.5"/>'
    s += f'<path d="M160 {sy + 22} Q166 {sy + 80} 186 {sy + 96}" fill="none" stroke="#C8341F" stroke-width="3"/><rect x="176" y="{sy + 94}" width="20" height="11" rx="4" fill="#C9D1D6" stroke-width="2.5"/>'
    s += arm((136, sy + 14), (108, sy + 100), (146, sy + 146), KHAKI, skin, short=True)
    s += f'<path d="M224 {sy + 108} L266 {sy + 108} L246 {sy + 172}Z" fill="#F3E6C8"/><path d="M232 {sy + 120} L258 {sy + 120} M238 {sy + 136} L254 {sy + 136}" stroke="#8C8C9A" stroke-width="2.5"/>'
    s += ''.join(f'<circle cx="{x}" cy="{sy + y}" r="4.5" fill="{CONCH}" stroke-width="1.8"/>' for x, y in ((232, 104), (242, 100), (252, 103), (260, 106), (247, 94)))
    s += f'<path d="M258 {sy + 98} Q270 {sy + 84} 276 {sy + 70}" fill="none" stroke="#3E7A3A" stroke-width="5"/>'
    s += arm((256, sy + 14), (288, sy + 98), (246, sy + 140), KHAKI, skin, short=True)
    return s


def b_haridas(sy, hip, feet, skin):
    s = legs(hip, feet, KHAKI) + feet_kind(feet, 'shoe', '#5A3A22', skin)
    s += tunic(sy, 205, KHAKI)
    s += f'<rect x="150" y="{sy + 50}" width="30" height="30" fill="none" stroke-width="3"/>'
    s += f'<path d="M150 {sy + 4} L262 {hip - 30}" stroke-width="13"/><path d="M150 {sy + 4} L262 {hip - 30}" stroke="#5A3A22" stroke-width="6"/>'
    s += f'<rect x="236" y="{hip - 66}" width="34" height="26" fill="{CONCH}" transform="rotate(-10 252 {hip - 54})"/><rect x="258" y="{hip - 70}" width="32" height="24" fill="#F3E6C8" transform="rotate(8 274 {hip - 58})"/>'
    s += f'<rect x="226" y="{hip - 52}" width="80" height="78" rx="8" fill="#C8341F"/><path d="M226 {hip - 44} L306 {hip - 44} L306 {hip - 12} Q266 {hip + 6} 226 {hip - 12}Z" fill="url(#n-env)"/>'
    s += f'<path d="M110 {sy + 182} L110 {sy + 166} Q110 {sy + 144} 90 {sy + 150}" fill="none" stroke-width="8"/>'
    s += f'<path d="M102 {sy + 192} L118 {sy + 192} L116 {feet - 50} L110 {feet - 6} L104 {feet - 50}Z" fill="#1C1410"/>'
    s += arm((140, sy + 14), (118, sy + 100), (110, sy + 176), KHAKI, skin, short=True)
    s += f'<g transform="rotate(-8 300 {sy - 96})"><rect x="270" y="{sy - 120}" width="58" height="38" fill="{CONCH}"/><path d="M270 {sy - 120} L299 {sy - 100} L328 {sy - 120}" fill="none" stroke-width="3"/><rect x="312" y="{sy - 114}" width="10" height="12" fill="#C8341F" stroke-width="2"/></g>'
    s += arm((252, sy + 14), (292, sy - 10), (296, sy - 72), KHAKI, skin, short=True)
    return s


# ------------------------------------------------------------------ heads
def H(name, aria, skin, **k):
    return head_svg(aria, k.get('behind', ''), skin, k.get('hair', ''), k.get('eye', 'normal'), k.get('gx', 0), k.get('gy', 0),
                    k.get('brows', BROWS['plain']), k.get('mouth', ''), k.get('extras', ''), k.get('rx', 56), k.get('ry', 68), k.get('after', ''))


def heads():
    out = {}
    sk = '#C29068'
    out['anko'] = H('anko', 'Anko Sir: bald maths teacher with grey side tufts, thick round glasses, bushy grey brows, grey mustache and a frown, panjabi printed with plus and times signs, holding a ruler and chalk — full body, standing', sk,
        hair=(f'<path d="M140 178 Q126 128 152 110 Q146 134 150 160 Q146 172 140 178Z" fill="{GREY_HAIR}"/><path d="M252 178 Q266 128 240 110 Q246 134 242 160 Q246 172 252 178Z" fill="{GREY_HAIR}"/>'
              '<path d="M188 104 Q192 88 200 104" fill="none" stroke-width="3"/><path d="M166 118 Q184 108 202 110" fill="none" stroke="#FBF5E9" stroke-width="5" opacity="0.7"/>'),
        brows=bushy(GREY_HAIR), gx=0,
        mouth=(f'<path d="M176 214 Q196 204 216 214 Q206 221 196 216 Q186 221 176 214Z" fill="{GREY_HAIR}" stroke-width="3"/><path d="M184 230 Q196 223 208 230" fill="none"/>'),
        extras=('<circle cx="171" cy="166" r="19" fill="#FBF5E9" fill-opacity="0.2" stroke-width="5"/><circle cx="221" cy="166" r="19" fill="#FBF5E9" fill-opacity="0.2" stroke-width="5"/>'
                '<path d="M190 164 Q196 158 202 164 M152 162 L142 158 M240 162 L250 158" fill="none"/>'
                '<ellipse cx="238" cy="198" rx="8" ry="5" fill="#FBF5E9" opacity="0.8" stroke="none"/>'))
    sk = '#B98258'
    out['mitali'] = H('mitali', 'Mitali Bose: science teacher with a bun skewered by a pencil, cat-eye glasses, a small red bindi and a big smile, white lab coat over a teal sari printed with hexagons, holding a glowing green flask — full body, standing', sk,
        behind=('<circle cx="196" cy="86" r="26" fill="#1C1410"/><path d="M168 62 L226 108" stroke-width="10"/><path d="M168 62 L226 108" stroke="#E3A92B" stroke-width="5"/><path d="M160 56 L168 62" stroke="#E58BA0" stroke-width="8"/>'),
        hair='<path d="M140 168 Q132 98 196 96 Q260 98 252 168 Q246 126 214 116 Q196 132 176 118 Q146 126 140 168Z" fill="#1C1410"/>',
        gx=2, brows=BROWS['up'],
        mouth='<path d="M176 218 Q196 240 216 218 Q196 226 176 218Z" fill="#1C1410"/><path d="M182 220 L210 220 L208 225 L184 225Z" fill="#FBF5E9" stroke="none"/>',
        extras=('<path d="M150 158 Q150 178 170 179 Q189 177 190 160 Q172 150 150 152 L144 145Z" fill="none" stroke-width="4.5"/>'
                '<path d="M242 158 Q242 178 222 179 Q203 177 202 160 Q220 150 242 152 L248 145Z" fill="none" stroke-width="4.5"/>'
                '<path d="M190 160 Q196 156 202 160" fill="none"/><circle cx="196" cy="138" r="4" fill="#C8341F" stroke="none"/>'
                '<circle cx="140" cy="196" r="5" fill="#E3A92B" stroke-width="2"/><circle cx="252" cy="196" r="5" fill="#E3A92B" stroke-width="2"/>'))
    sk = '#8E5B3A'
    out['jogen'] = H('jogen', 'Ghonta-da: thin old school peon with cropped grey hair, crinkled happy eyes and a gap-toothed grin, khaki shirt, white dhoti and a ring-patterned gamchha, holding the school gong and a mallet — full body, standing', sk,
        hair=f'<path d="M140 160 Q138 100 196 98 Q254 100 252 160 Q246 124 196 118 Q146 124 140 160Z" fill="{GREY_HAIR}"/>',
        eye='happy', brows=f'<path d="M154 140 L186 136" stroke="{GREY_HAIR}" stroke-width="7"/><path d="M206 136 L238 140" stroke="{GREY_HAIR}" stroke-width="7"/>',
        mouth=('<path d="M170 210 Q196 248 222 210Z" fill="#1C1410"/><path d="M176 212 L216 212 L213 221 L179 221Z" fill="#FBF5E9" stroke-width="2"/><rect x="194" y="212" width="7" height="10" fill="#1C1410" stroke="none"/>'
               '<path d="M146 176 L136 172 M146 182 L136 184 M246 176 L256 172 M246 182 L256 184" fill="none" stroke-width="2.5"/>'),
        after='<g fill="#FBF5E9" opacity="0.7">' + ''.join(f'<circle cx="{x}" cy="{y}" r="1.6"/>' for x, y in ((172, 226), (180, 232), (212, 232), (220, 226), (196, 236), (186, 237), (206, 237))) + '</g>')
    sk = '#A87452'
    out['robin'] = H('robin', 'Robin Sardar: sleepy night security guard with a navy peaked cap, heavy-lidded eyes and a thick black mustache, navy uniform, moon-and-star muffler, whistle, bamboo lathi and a torch — full body, standing', sk,
        hair=('<path d="M140 146 L140 178 L148 168Z M252 146 L252 178 L244 168Z" fill="#1C1410"/>'
              '<path d="M138 140 Q136 92 196 88 Q256 92 254 140Z" fill="#22305F"/><path d="M128 140 Q196 126 264 140 Q254 156 196 152 Q138 156 128 140Z" fill="#1C1410"/>'
              '<circle cx="196" cy="114" r="10" fill="#E3A92B" stroke-width="3"/>'),
        eye='sleepy', brows=BROWS['plain'],
        mouth='<path d="M164 210 Q196 194 228 210 Q214 224 196 214 Q178 224 164 210Z" fill="#1C1410"/><path d="M188 228 Q196 232 204 228" fill="none"/>')
    out['montu'] = H('montu', 'Montu-da: tea seller with wavy black hair, a thin mustache and a huge toothy smile, white vest, green checked lungi and a red check gamchha, holding a steaming kettle and a stack of clay cups — full body, standing', sk,
        hair='<path d="M138 166 Q128 110 170 98 Q200 84 236 100 Q262 116 254 166 Q248 132 226 124 Q214 134 196 124 Q178 136 160 126 Q144 136 138 166Z" fill="#1C1410"/>',
        gx=-3, brows=BROWS['up'],
        mouth=('<path d="M180 208 Q196 202 212 208" fill="none" stroke-width="4"/><path d="M172 214 Q196 244 220 214Z" fill="#1C1410"/>'
               '<path d="M177 215 L215 215 Q212 223 196 223 Q180 223 177 215Z" fill="#FBF5E9" stroke-width="2"/>'))
    sk = '#8E5B3A'
    out['kashem'] = H('kashem', 'Kashem Mia: lean rickshaw puller with short hair under a red check gamchha headband, stubble and a friendly smile, white vest, rickshaw-art flower lungi folded to the knee, holding a brass bulb horn and waving — full body, standing', sk,
        rx=52,
        hair=('<path d="M144 150 Q142 100 196 98 Q250 100 248 150Z" fill="#1C1410"/>'
              '<path d="M142 132 Q196 118 250 132 L250 148 Q196 134 142 148Z" fill="url(#n-gam)"/>'
              '<path d="M248 134 L278 122 L272 144Z M248 142 L274 162 L258 168Z" fill="url(#n-gam)"/>'),
        brows=BROWS['plain'],
        mouth='<path d="M178 220 Q196 234 214 220" fill="none" stroke-width="5"/>',
        extras='<path d="M150 192 Q152 236 196 240 Q240 236 242 192 Q234 228 196 231 Q158 228 150 192Z" fill="#3A2A20" opacity="0.55" stroke="none"/>')
    sk = '#B98258'
    out['bablu'] = H('bablu', 'Bablu Ustad: big-bellied bus driver with a comb-over, yellow mirrored aviators, thick brows, a black mustache and paan-red lips, triangle-patterned red shirt and a towel round his neck, gripping a steering wheel — full body, standing', sk,
        rx=60, ry=66,
        hair=('<path d="M136 170 Q130 120 150 106 Q150 140 146 170Z M256 170 Q262 120 242 106 Q242 140 246 170Z" fill="#1C1410"/>'
              '<path d="M150 118 Q196 102 242 116 M158 128 Q196 112 236 124" fill="none" stroke-width="5"/>'),
        brows=BROWS['thick'],
        mouth=('<path d="M166 212 Q196 198 226 212 Q212 222 196 216 Q180 222 166 212Z" fill="#1C1410"/>'
               '<path d="M182 225 Q196 234 210 225 Q196 229 182 225Z" fill="#C8341F" stroke-width="3"/>'),
        extras=('<path d="M148 154 L192 154 Q194 182 172 185 Q148 183 148 154Z" fill="#E3A92B" stroke-width="4.5"/>'
                '<path d="M200 154 L244 154 Q244 183 220 185 Q198 182 200 154Z" fill="#E3A92B" stroke-width="4.5"/>'
                '<path d="M192 157 L200 157" fill="none"/><path d="M156 164 L168 158 M208 164 L220 158" stroke="#FBF5E9" stroke-width="3"/>'))
    sk = '#C29068'
    out['pintu'] = H('pintu', 'Pintu: young fuchka seller with spiky hair and a cheeky lopsided grin, a big basket of golden puris balanced on his head, red polka-dot kurta and rolled jeans, holding up one puri dripping tamarind water — full body, standing', sk,
        hair=('<path d="M142 150 L140 118 L156 124 L160 106 L176 118 L186 102 L198 116 L212 104 L218 120 L236 110 L234 128 L252 128 L250 150 Q196 124 142 150Z" fill="#1C1410"/>'
              '<ellipse cx="196" cy="104" rx="32" ry="9" fill="url(#n-gam)"/>'
              + ''.join(f'<circle cx="{x}" cy="{y}" r="13" fill="#F3D9A0" stroke-width="3"/>' for x, y in ((140, 82), (166, 76), (196, 72), (226, 76), (252, 82), (154, 62), (182, 56), (210, 56), (238, 62), (196, 40)))
              + '<path d="M100 88 Q196 112 292 88 L284 102 Q196 128 108 102Z" fill="#E3A92B"/>'
              '<path d="M124 96 L126 108 M150 101 L151 114 M176 104 L176 117 M216 104 L216 117 M242 101 L241 114 M268 96 L266 108" stroke-width="2.5"/>'),
        gx=4, gy=-2, brows=BROWS['one_up'],
        mouth='<path d="M176 216 Q200 238 220 212" fill="none" stroke-width="5"/><path d="M222 208 Q226 214 222 218" fill="none" stroke-width="3"/>')
    out['ruksana'] = H('ruksana', 'Dr. Ruksana Ahmed: kind doctor with side-swept black hair in a low bun, warm smile and small stud earrings, white coat over a heartbeat-line kameez, stethoscope round her neck, holding a clipboard and pen — full body, standing', sk,
        behind='<circle cx="146" cy="204" r="20" fill="#1C1410"/>',
        hair='<path d="M140 172 Q130 100 196 96 Q262 100 252 172 Q250 130 230 118 Q196 142 150 128 Q142 140 140 172Z" fill="#1C1410"/>',
        brows=BROWS['up'],
        mouth='<path d="M178 220 Q196 236 214 220" fill="none" stroke-width="5"/>',
        extras=('<circle cx="160" cy="196" r="9" fill="#E58BA0" opacity="0.55" stroke="none"/><circle cx="232" cy="196" r="9" fill="#E58BA0" opacity="0.55" stroke="none"/>'
                '<circle cx="140" cy="192" r="3.5" fill="#E3A92B" stroke-width="2"/><circle cx="252" cy="192" r="3.5" fill="#E3A92B" stroke-width="2"/>'))
    sk = '#B98258'
    out['shefali'] = H('shefali', 'Sister Shefali: brisk nurse with neat middle-parted hair, a folded white cap with a teal stripe, one raised eyebrow and a pen behind her ear, white sari with teal border, carrying a medicine tray and a clipboard — full body, standing', sk,
        hair=('<path d="M140 170 Q134 98 196 96 Q258 98 252 170 Q246 120 196 116 Q146 120 140 170Z" fill="#1C1410"/>'
              '<path d="M150 110 L242 110 L232 74 Q196 62 160 74Z" fill="#FBF5E9"/><path d="M155 100 L237 100 L235 92 L157 92Z" fill="#1F7A78" stroke-width="2"/>'
              '<path d="M196 72 L196 86 M189 79 L203 79" stroke="#1F7A78" stroke-width="4"/>'),
        brows=BROWS['one_up'],
        mouth='<path d="M184 222 Q198 229 212 219" fill="none" stroke-width="5"/>',
        extras='<path d="M246 152 L274 128" stroke-width="9"/><path d="M246 152 L274 128" stroke="#2C3E8C" stroke-width="4"/>')
    sk = '#A87452'
    out['gopal'] = H('gopal', 'Havildar Gopal Dhar: round-faced police constable with a khaki-brown beret, small eyes, bushy brows and a droopy mustache with muri crumbs, chevron khaki uniform with a big belly, lathi over his shoulder and a paper cone of jhalmuri — full body, standing', sk,
        rx=64, ry=64,
        hair=('<path d="M134 128 Q128 90 180 84 Q240 80 264 106 Q260 126 250 130 Q196 118 134 128Z" fill="#5A4A2A"/>'
              '<path d="M134 128 Q196 116 256 128 L256 138 Q196 126 134 138Z" fill="#1C1410"/><circle cx="166" cy="110" r="9" fill="#E3A92B" stroke-width="3"/>'),
        gx=-3, brows=bushy('#1C1410'),
        mouth=('<path d="M166 206 Q196 196 226 206 L230 232 Q218 218 196 214 Q174 218 162 232Z" fill="#1C1410"/>'
               '<path d="M190 226 Q196 230 202 226" fill="none"/>'),
        after='<circle cx="184" cy="214" r="2.5" fill="#FBF5E9"/><circle cx="210" cy="212" r="2.5" fill="#FBF5E9"/>')
    sk = '#C29068'
    out['haridas'] = H('haridas', 'Haridas the postman: cheerful old postman with a khaki peaked cap, white hair and a big white mustache, half-moon glasses low on his nose, khaki uniform with a red envelope-print mailbag, closed black umbrella, holding up a letter — full body, standing', sk,
        hair=(f'<path d="M140 140 Q134 162 142 180 L150 150Z M252 140 Q258 162 250 180 L242 150Z" fill="{GREY_HAIR}"/>'
              '<path d="M140 136 Q140 96 196 92 Q252 96 252 136Z" fill="#B8A070"/><path d="M132 136 Q196 126 260 136 Q254 152 196 148 Q138 152 132 136Z" fill="#8A7448"/>'
              '<rect x="186" y="104" width="20" height="14" fill="#C8341F" stroke-width="2.5"/>'),
        gy=-2, brows=bushy('#FBF5E9'),
        mouth='<path d="M168 210 Q196 194 224 210 Q212 223 196 214 Q180 223 168 210Z" fill="#FBF5E9"/><path d="M184 226 Q196 234 208 226" fill="none"/>',
        extras=('<path d="M154 176 L188 176 Q186 191 171 191 Q156 191 154 176Z" fill="none" stroke-width="4"/>'
                '<path d="M204 176 L238 176 Q236 191 221 191 Q206 191 204 176Z" fill="none" stroke-width="4"/><path d="M188 178 Q196 174 204 178" fill="none" stroke-width="3"/>'))
    return out


BODIES = {'anko': b_anko, 'mitali': b_mitali, 'jogen': b_jogen, 'robin': b_robin, 'montu': b_montu, 'kashem': b_kashem,
          'bablu': b_bablu, 'pintu': b_pintu, 'ruksana': b_ruksana, 'shefali': b_shefali, 'gopal': b_gopal, 'haridas': b_haridas}
SKINS = {'anko': '#C29068', 'mitali': '#B98258', 'jogen': '#8E5B3A', 'robin': '#A87452', 'montu': '#A87452', 'kashem': '#8E5B3A',
         'bablu': '#B98258', 'pintu': '#C29068', 'ruksana': '#C29068', 'shefali': '#B98258', 'gopal': '#A87452', 'haridas': '#C29068'}
DISCS = {'anko': '#2C3E8C', 'mitali': '#B5482A', 'jogen': '#E3A92B', 'robin': '#22305F', 'montu': '#E07A2E', 'kashem': '#3E7A3A',
         'bablu': '#C8341F', 'pintu': '#E58BA0', 'ruksana': '#1F7A78', 'shefali': '#E58BA0', 'gopal': '#3E7A3A', 'haridas': '#2C3E8C'}
PATS = {'anko': ['n-math'], 'mitali': ['n-hex'], 'jogen': ['n-ring'], 'robin': ['n-moon'], 'montu': ['n-lchk', 'n-gam'],
        'kashem': ['n-rick', 'n-gam'], 'bablu': ['n-tri'], 'pintu': ['n-dot', 'n-gam'], 'ruksana': ['n-beat'], 'shefali': ['n-plus'],
        'gopal': ['n-chev'], 'haridas': ['n-env']}


def art(key):
    src, chin = heads()[key]
    defs = '<defs>' + ''.join(PATTERNS[p] for p in PATS[key]) + '</defs>'
    src = src.replace('">', '">' + defs, 1) if False else src
    src = src.replace(f'aria-label="', 'aria-label="', 1)
    # put pattern defs inside the head svg so card() carries them
    i = src.index('>') + 1
    src = src[:i] + defs + src[i:]
    skin = SKINS[key]
    s = card(key, src, chin, skin, {'body': BODIES[key], 'clip_pad': 2}, disc=DISCS[key])
    return s.replace(f'id="hc{key}"', f'id="hc-{key}"').replace(f'url(#hc{key})', f'url(#hc-{key})')


if __name__ == '__main__':
    import subprocess
    from PIL import Image
    keys = list(BODIES)
    W = Image.new('RGB', (392 * 6, 640 * 2), 'white')
    for n, k in enumerate(keys):
        svg = art(k).replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" width="392" height="640" ', 1)
        open(f'nb/{k}.svg', 'w').write(svg)
        subprocess.run(['rsvg-convert', '-o', f'nb/{k}.png', f'nb/{k}.svg'], check=True)
        W.paste(Image.open(f'nb/{k}.png').convert('RGB'), ((n % 6) * 392, (n // 6) * 640))
    W.save('nb/sheet.png')
    print('ok')
