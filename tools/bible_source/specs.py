from fullbody import *

K = INK


def V(sy, fill, trim=None):
    s = f'<path d="M178 {sy - 2} L196 {sy + 30} L214 {sy - 2}Z" fill="{fill}"/>'
    if trim:
        s += f'<path d="M174 {sy} L196 {sy + 34} L218 {sy}" fill="none" stroke="{trim}" stroke-width="6"/>'
    return s


# ======================================================= HUMANS 1
def tuli(sy, hip, feet, skin):
    s = legs(hip, feet, '#6E6A3A')
    s += f'<path d="M150 {hip + 90} L150 {hip + 130} M242 {hip + 90} L242 {hip + 130}" stroke-width="2"/>'
    s += feet_kind(feet, 'sneaker', '#FBF5E9')
    s += tunic(sy, 236, 'url(#h1-ripple)')
    s += V(sy, skin, '#E3A92B')
    s += arm((140, sy + 14), (118, sy + 110), (124, sy + 196), '#2C3E8C', skin)
    s += f'<rect x="88" y="{sy + 168}" width="44" height="58" rx="3" fill="#E58BA0"/><path d="M96 {sy + 186} L124 {sy + 186} M96 {sy + 200} L118 {sy + 200}" stroke-width="2"/>'
    s += arm((252, sy + 14), (274, sy + 110), (270, sy + 196), '#2C3E8C', skin)
    s += f'<path d="M150 {sy + 4} Q196 {sy + 50} 242 {sy + 4}" fill="none" stroke-width="14"/><path d="M150 {sy + 4} Q196 {sy + 50} 242 {sy + 4}" fill="none" stroke="#C8341F" stroke-width="7"/>'
    s += f'<ellipse cx="148" cy="{sy + 4}" rx="14" ry="18" fill="#C8341F"/><ellipse cx="244" cy="{sy + 4}" rx="14" ry="18" fill="#C8341F"/>'
    return s


TULI_FRONT = ('<g fill="#1C1410"><ellipse cx="256" cy="250" rx="15" ry="19"/><ellipse cx="262" cy="282" rx="14" ry="18"/>'
              '<ellipse cx="266" cy="312" rx="13" ry="17"/><ellipse cx="268" cy="340" rx="12" ry="16"/></g>'
              '<path d="M262 356 L256 380 M268 356 L272 380" stroke="#C8341F" stroke-width="5"/>')


def ronju(sy, hip, feet, skin):
    s = legs(hip, feet, '#3A5A8C')
    s += feet_kind(feet, 'chappal', '#8A3B12', skin)
    s += tunic(sy, 216, 'url(#h1-zig)')
    s += V(sy, skin)
    s += arm((140, sy + 14), (120, sy + 108), (132, sy + 186), '#C8341F', skin)
    s += f'<path d="M110 {sy + 186} L160 {sy + 186} L135 {sy + 240}Z" fill="#F3E6C8"/>'
    s += f'<g fill="#F3D9A0" stroke-width="2"><circle cx="122" cy="{sy + 182}" r="6"/><circle cx="136" cy="{sy + 178}" r="6"/><circle cx="150" cy="{sy + 182}" r="6"/></g>'
    s += arm((252, sy + 14), (300, sy - 30), (316, sy - 96), '#C8341F', skin)
    s += f'<path d="M318 {sy - 100} L334 {sy - 210}" stroke-width="11"/><path d="M318 {sy - 100} L334 {sy - 210}" stroke="#8C8C9A" stroke-width="5"/>'
    s += f'<g transform="rotate(10 336 {sy - 250})"><rect x="306" y="{sy - 300}" width="60" height="96" rx="10" fill="#1C1410"/><rect x="314" y="{sy - 290}" width="44" height="76" rx="3" fill="#1F7A78" stroke-width="2"/><circle cx="322" cy="{sy - 282}" r="4" fill="#C8341F" stroke="none"/></g>'
    s += f'<path d="M146 {sy} Q196 {sy + 36} 246 {sy} L250 {sy + 16} Q196 {sy + 52} 142 {sy + 16}Z" fill="url(#h1-check)"/>'
    s += f'<path d="M220 {sy + 26} L246 {sy + 20} L250 {sy + 150} L222 {sy + 150}Z" fill="url(#h1-check)"/>'
    return s


def dida(sy, hip, feet, skin):
    s = sari_skirt(sy + 150, feet, 'url(#h1-kantha)', 'url(#h1-border)')
    s += feet_kind(feet, 'chappal', '#FBF5E9', skin, spread=20)
    s += tunic(sy, 170, 'url(#h1-kantha)', flare=4)
    s += aanchal(sy, 'url(#h1-border)')
    s += arm((140, sy + 14), (122, sy + 110), (168, sy + 150), '#FBF5E9', skin, short=True)
    s += arm((252, sy + 14), (270, sy + 110), (224, sy + 150), '#FBF5E9', skin, short=True)
    s += f'<circle cx="196" cy="{sy + 150}" r="60" fill="#FFC94A" opacity="0.3" stroke="none"/>'
    s += f'<rect x="156" y="{sy + 122}" width="80" height="58" rx="7" fill="#1C1410"/><rect x="163" y="{sy + 129}" width="66" height="44" rx="3" fill="#FFC94A" stroke-width="2"/>'
    return s


def pupu(sy, hip, feet, skin):
    s = f'<rect x="124" y="{sy + 8}" width="144" height="150" rx="16" fill="#2C3E8C"/>'
    s += f'<path d="M168 {hip + 40} L166 {feet - 4} L190 {feet - 4} L192 {hip + 40}Z M200 {hip + 40} L202 {feet - 4} L226 {feet - 4} L224 {hip + 40}Z" fill="{skin}"/>'
    s += f'<path d="M166 {feet - 46} L190 {feet - 46} L190 {feet - 4} L166 {feet - 4}Z M202 {feet - 46} L226 {feet - 46} L226 {feet - 4} L202 {feet - 4}Z" fill="#FBF5E9"/>'
    s += feet_kind(feet, 'sneaker', '#C8341F', spread=18)
    s += shorts(hip - 20, hip + 52, '#B59A62', 38)
    s += tunic(sy, 140, 'url(#h1-dots)', flare=2, half=52)
    s += f'<path d="M156 {sy + 2} L150 {sy + 120} M236 {sy + 2} L242 {sy + 120}" stroke-width="18"/><path d="M156 {sy + 2} L150 {sy + 120} M236 {sy + 2} L242 {sy + 120}" stroke="#2C3E8C" stroke-width="10"/>'
    s += arm((148, sy + 14), (124, sy + 76), (114, sy + 136), '#1F7A78', skin, short=True)
    s += f'<path d="M114 {sy + 150} L114 {sy + 110} L100 {sy + 80} M114 {sy + 110} L128 {sy + 80}" fill="none" stroke-width="11"/><path d="M114 {sy + 150} L114 {sy + 110} L100 {sy + 80} M114 {sy + 110} L128 {sy + 80}" fill="none" stroke="#8A3B12" stroke-width="5"/>'
    s += arm((244, sy + 14), (266, sy + 76), (270, sy + 136), '#1F7A78', skin, short=True)
    return s


# ======================================================= HUMANS 2
def moyna(sy, hip, feet, skin):
    s = legs(hip, feet, '#6B5A3A')
    s += feet_kind(feet, 'boot', '#1C1410')
    s += tunic(sy, 200, 'url(#h2-chev)', flare=0)
    s += f'<rect x="134" y="{sy + 186}" width="124" height="16" fill="#6B3A1F"/><rect x="186" y="{sy + 184}" width="20" height="20" fill="#E3A92B" stroke-width="3"/>'
    s += f'<path d="M172 {sy - 4} L196 {sy + 26} L184 {sy + 40} L164 {sy + 8}Z M220 {sy - 4} L196 {sy + 26} L208 {sy + 40} L228 {sy + 8}Z" fill="#B59A62"/>'
    s += f'<path d="M136 {sy + 14} L160 {sy + 2} L164 {sy + 14} L140 {sy + 26}Z M256 {sy + 14} L232 {sy + 2} L228 {sy + 14} L252 {sy + 26}Z" fill="#2C3E8C"/>'
    s += f'<path d="M156 {sy + 60} L160 {sy + 70} L171 {sy + 70} L163 {sy + 77} L166 {sy + 88} L156 {sy + 81} L146 {sy + 88} L149 {sy + 77} L141 {sy + 70} L152 {sy + 70}Z" fill="#E3A92B" stroke-width="3"/>'
    s += arm((140, sy + 14), (100, sy + 90), (142, sy + 168), '#B59A62', skin)
    s += arm((252, sy + 14), (282, sy + 100), (262, sy + 160), '#B59A62', skin)
    s += f'<path d="M248 {sy + 168} L250 {sy + 146} L276 {sy + 146} L278 {sy + 168}Z" fill="#B5482A"/>'
    s += f'<rect x="232" y="{sy - 2}" width="22" height="36" rx="4" fill="#1C1410"/><path d="M243 {sy - 2} L243 {sy - 16}" stroke-width="3"/>'
    return s


def ghontu(sy, hip, feet, skin):
    s = lungi(hip - 30, feet, 'url(#gh-check)')
    s += feet_kind(feet, 'chappal', '#6B3A1F', skin)
    s += tunic(sy, 300, '#FBF5E9', flare=16)
    s += f'<path d="M168 {sy - 2} L196 {sy + 40} L224 {sy - 2} L224 {sy + 300} L168 {sy + 300}Z" fill="url(#h2-spiral)"/>'
    s += f'<path d="M168 {sy - 2} L182 {sy + 120} L170 {sy + 300} M224 {sy - 2} L210 {sy + 120} L222 {sy + 300}" fill="none"/>'
    s += f'<rect x="232" y="{sy + 70}" width="30" height="36" fill="#FBF5E9"/><path d="M238 {sy + 70} L238 {sy + 56} M248 {sy + 70} L250 {sy + 52}" stroke-width="5"/>'
    s += arm((140, sy + 14), (118, sy + 120), (126, sy + 220), '#FBF5E9', skin)
    s += arm((252, sy + 14), (296, sy + 70), (312, sy + 4), '#FBF5E9', skin)
    s += f'<path d="M312 {sy + 2} L330 {sy - 60}" stroke-width="10"/><path d="M312 {sy + 2} L330 {sy - 60}" stroke="#8C8C9A" stroke-width="5"/><path d="M320 {sy - 66} Q330 {sy - 86} 344 {sy - 70} L338 {sy - 58} L328 {sy - 62}Z" fill="#8C8C9A"/>'
    return s


def bhombol(sy, hip, feet, skin):
    s = legs(hip, feet, '#F3E6C8', w=42)
    s += feet_kind(feet, 'nagra', '#E3A92B')
    s += tunic(sy, 250, '#F3E6C8', flare=18, half=70, belly=22)
    s += f'<path d="M126 {sy - 2} Q196 {sy - 12} 266 {sy - 2} L284 {sy + 40} L272 {sy + 250} L238 {sy + 250} L232 {sy + 60} Q196 {sy + 80} 160 {sy + 60} L154 {sy + 250} L120 {sy + 250} L108 {sy + 40}Z" fill="url(#h2-diam)"/>'
    s += f'<path d="M168 {sy + 2} Q196 {sy + 60} 224 {sy + 2}" fill="none" stroke="#E3A92B" stroke-width="5"/><circle cx="196" cy="{sy + 34}" r="9" fill="#E3A92B" stroke-width="3"/>'
    s += arm((132, sy + 16), (104, sy + 120), (120, sy + 206), '#7A1F1F', skin)
    s += arm((260, sy + 16), (292, sy + 110), (270, sy + 170), '#7A1F1F', skin)
    s += f'<rect x="252" y="{sy + 128}" width="36" height="58" rx="6" fill="#1C1410"/><rect x="257" y="{sy + 134}" width="26" height="44" rx="2" fill="#9CC7C9" stroke-width="2"/>'
    return s


BHOMBOL_BEHIND = ('<circle cx="196" cy="168" r="112" fill="none" stroke="#1C1410" stroke-width="24"/>'
                  '<circle cx="196" cy="168" r="112" fill="none" stroke="#FBF5E9" stroke-width="16"/>')


def kalo(sy, hip, feet, skin):
    s = legs(hip, feet, 'url(#h2-hatch)', w=36)
    s += feet_kind(feet, 'shoe', '#1C1410', spread=22)
    s += tunic(sy, 236, 'url(#h2-hatch)', flare=4, half=58)
    s += f'<path d="M176 {sy - 4} L196 {sy + 56} L216 {sy - 4}Z" fill="#FBF5E9"/>'
    s += f'<path d="M190 {sy + 6} L202 {sy + 6} L207 {sy + 58} L196 {sy + 72} L185 {sy + 58}Z" fill="#C8341F"/>'
    s += f'<path d="M176 {sy - 4} L192 {sy + 80} L152 {sy + 52}Z M216 {sy - 4} L200 {sy + 80} L240 {sy + 52}Z" fill="#1C1410" stroke="#5A5A66"/>'
    s += f'<path d="M142 {sy + 66} Q152 {sy + 38} 174 {sy + 32} Q166 {sy + 58} 142 {sy + 66}Z" fill="#2C3E8C" stroke="#8C8C9A" stroke-width="2.5"/>'
    s += arm((140, sy + 14), (124, sy + 116), (150, sy + 200), '#2A2630', skin, hand=False)
    s += arm((252, sy + 14), (280, sy + 110), (262, sy + 196), '#2A2630', skin)
    s += f'<circle cx="262" cy="{sy + 196}" r="5" fill="#C8341F" stroke-width="2"/>'
    return s


KALO_FRONT_CROW = ''


# ======================================================= FAMILIES
def shubho(sy, hip, feet, skin):
    s = lungi(hip - 20, feet, 'url(#sb-check)')
    s += feet_kind(feet, 'chappal', '#2C3E8C', skin)
    s += tunic(sy, 210, 'url(#f-grid)', flare=2)
    s += f'<path d="M160 {sy - 2} L196 {sy + 14} L186 {sy + 34} L152 {sy + 8}Z M232 {sy - 2} L196 {sy + 14} L206 {sy + 34} L240 {sy + 8}Z" fill="#FBF5E9"/>'
    s += f'<path d="M190 {sy + 14} L202 {sy + 14} L207 {sy + 30} L212 {sy + 110} L196 {sy + 124} L180 {sy + 110} L185 {sy + 30}Z" fill="#E3A92B"/>'
    s += arm((140, sy + 14), (116, sy + 106), (128, sy + 190), '#A9C4DE', skin)
    s += f'<g transform="rotate(-8 140 {sy + 150})"><rect x="96" y="{sy + 120}" width="84" height="58" rx="5" fill="#8C8C9A"/><circle cx="138" cy="{sy + 149}" r="8" fill="#C8341F" stroke-width="2"/></g>'
    s += arm((252, sy + 14), (276, sy + 106), (268, sy + 190), '#A9C4DE', skin)
    return s


def rini(sy, hip, feet, skin):
    s = sari_skirt(sy + 150, feet, '#1F7A78', '#E3A92B')
    s += feet_kind(feet, 'chappal', '#C8341F', skin, spread=20)
    s += tunic(sy, 170, '#1F7A78', flare=2)
    s += aanchal(sy, '#14514F', '#E3A92B')
    s += f'<path d="M156 {sy + 40} L236 {sy + 40} L250 {sy + 330} L142 {sy + 330}Z" fill="url(#f-petal)"/>'
    s += f'<path d="M160 {sy + 42} L172 {sy + 4} M232 {sy + 42} L220 {sy + 4}" stroke-width="10"/><path d="M160 {sy + 42} L172 {sy + 4} M232 {sy + 42} L220 {sy + 4}" stroke="#E3A92B" stroke-width="5"/>'
    s += arm((140, sy + 14), (118, sy + 110), (166, sy + 152), '#1F7A78', skin, short=True)
    s += arm((252, sy + 14), (276, sy + 100), (232, sy + 140), '#1F7A78', skin, short=True)
    s += f'<path d="M150 {sy + 150} Q196 {sy + 200} 242 {sy + 150}Z" fill="#C9D1D6"/><path d="M226 {sy + 150} L262 {sy + 100}" stroke-width="5"/><ellipse cx="266" cy="{sy + 94}" rx="8" ry="12" fill="#C9D1D6" stroke-width="3"/>'
    return s


def haripada(sy, hip, feet, skin):
    s = f'<path d="M138 {hip - 10} L254 {hip - 10} L262 {feet - 50} L214 {feet - 46} L196 {hip + 40} L178 {feet - 46} L130 {feet - 50}Z" fill="#FBF5E9"/>'
    s += f'<path d="M150 {feet - 50} L150 {feet - 6} L176 {feet - 6} L176 {feet - 50}Z M216 {feet - 50} L216 {feet - 6} L242 {feet - 6} L242 {feet - 50}Z" fill="{skin}"/>'
    s += feet_kind(feet, 'chappal', '#6B3A1F', skin, spread=26)
    s += tunic(sy, 220, '#F3E6C8', flare=6)
    s += f'<path d="M128 {sy} Q196 {sy - 10} 264 {sy} L282 {sy + 50} L270 {sy + 230} L236 {sy + 230} L230 {sy + 70} Q196 {sy + 90} 162 {sy + 70} L156 {sy + 230} L122 {sy + 230} L110 {sy + 50}Z" fill="url(#f-plus)"/>'
    s += f'<path d="M150 {sy - 2} Q196 {sy + 30} 242 {sy - 2} L246 {sy + 14} Q196 {sy + 46} 146 {sy + 14}Z" fill="#7A1F1F"/>'
    s += f'<path d="M222 {sy + 24} L244 {sy + 20} L248 {sy + 120} L224 {sy + 120}Z" fill="#7A1F1F"/>'
    s += arm((134, sy + 16), (112, sy + 110), (150, sy + 150), '#F3E6C8', skin)
    s += f'<g transform="rotate(-12 120 {sy + 140})"><rect x="86" y="{sy + 110}" width="76" height="56" fill="#FBF5E9"/><path d="M94 {sy + 124} L152 {sy + 124} M94 {sy + 138} L140 {sy + 138} M94 {sy + 152} L148 {sy + 152}" stroke-width="2"/></g>'
    s += f'<path d="M290 {feet} L290 {sy + 150} Q290 {sy + 120} 270 {sy + 122} Q258 {sy + 128} 264 {sy + 140}" fill="none" stroke-width="12"/><path d="M290 {feet} L290 {sy + 150} Q290 {sy + 120} 270 {sy + 122} Q258 {sy + 128} 264 {sy + 140}" fill="none" stroke="#1C1410" stroke-width="7"/>'
    s += f'<path d="M290 {sy + 150} Q290 {sy + 120} 270 {sy + 122} Q258 {sy + 128} 264 {sy + 140}" fill="none" stroke="#8A3B12" stroke-width="5"/>'
    s += arm((258, sy + 16), (288, sy + 90), (290, sy + 150), '#F3E6C8', skin)
    return s


def mallika(sy, hip, feet, skin):
    s = sari_skirt(sy + 150, feet, 'url(#f-alpana)', '#3E7A3A')
    s += feet_kind(feet, 'chappal', '#C8341F', skin, spread=20)
    s += tunic(sy, 170, '#C8341F', flare=2)
    s += aanchal(sy, 'url(#f-alpana)', '#3E7A3A')
    s += f'<circle cx="140" cy="{sy + 46}" r="8" fill="none" stroke="#E3A92B" stroke-width="4"/><path d="M134 {sy + 54} L130 {sy + 76} M140 {sy + 56} L140 {sy + 80} M146 {sy + 54} L150 {sy + 76}" stroke="#E3A92B" stroke-width="5"/>'
    s += arm((140, sy + 14), (114, sy + 110), (130, sy + 186), '#C8341F', skin, short=True)
    s += arm((252, sy + 14), (282, sy + 100), (252, sy + 140), '#C8341F', skin, short=True)
    s += f'<rect x="240" y="{sy + 98}" width="30" height="50" rx="5" fill="#1C1410"/><rect x="244" y="{sy + 104}" width="22" height="36" rx="2" fill="#BFE3EE" stroke-width="2"/><circle cx="272" cy="{sy + 98}" r="9" fill="#C8341F" stroke-width="2"/>'
    s += f'<g fill="#E3A92B" stroke-width="2"><circle cx="130" cy="{sy + 176}" r="5"/></g>'
    return s


# ======================================================= KIDS
def mitul(sy, hip, feet, skin):
    s = f'<path d="M168 {hip + 40} L166 {feet - 4} L190 {feet - 4} L192 {hip + 40}Z M200 {hip + 40} L202 {feet - 4} L226 {feet - 4} L224 {hip + 40}Z" fill="{skin}"/>'
    s += f'<path d="M166 {feet - 70} L190 {feet - 70} L190 {feet - 4} L166 {feet - 4}Z M202 {feet - 70} L226 {feet - 70} L226 {feet - 4} L202 {feet - 4}Z" fill="#FBF5E9"/>'
    s += f'<path d="M166 {feet - 70} L190 {feet - 70} M202 {feet - 70} L226 {feet - 70}" stroke="#C8341F" stroke-width="5"/>'
    s += feet_kind(feet, 'sneaker', '#FBF5E9', spread=18)
    s += shorts(hip - 20, hip + 52, '#2C3E8C', 38)
    s += tunic(sy, 140, 'url(#k-stripe)', flare=2, half=52)
    s += f'<g transform="rotate(30 262 {sy + 80})"><rect x="248" y="{sy - 120}" width="32" height="190" rx="8" fill="#E3C27A"/><rect x="256" y="{sy + 70}" width="16" height="60" fill="#8A3B12"/></g>'
    s += arm((148, sy + 14), (124, sy + 76), (130, sy + 136), '#E3A92B', skin, short=True)
    s += arm((244, sy + 14), (268, sy + 60), (236, sy + 100), '#E3A92B', skin, short=True)
    return s


def babai(sy, hip, feet, skin):
    s = f'<path d="M168 {hip + 40} L166 {feet - 4} L190 {feet - 4} L192 {hip + 40}Z M200 {hip + 40} L202 {feet - 4} L226 {feet - 4} L224 {hip + 40}Z" fill="{skin}"/>'
    s += feet_kind(feet, 'chappal', '#2C3E8C', skin, spread=18)
    s += shorts(hip - 20, hip + 52, '#6B5A3A', 44)
    s += tunic(sy, 146, 'url(#k-tri)', flare=4, half=60, belly=18)
    s += arm((140, sy + 14), (118, sy + 70), (168, sy + 96), '#E07A2E', skin, short=True)
    s += arm((252, sy + 14), (274, sy + 70), (224, sy + 96), '#E07A2E', skin, short=True)
    s += f'<path d="M150 {sy + 92} L242 {sy + 92} L196 {sy + 168}Z" fill="#F3E6C8"/>'
    s += f'<path d="M146 {sy + 94} Q156 {sy + 70} 176 {sy + 78} Q190 {sy + 62} 210 {sy + 76} Q232 {sy + 68} 246 {sy + 94}Z" fill="#F3D9A0"/>'
    return s


def jhumpa(sy, hip, feet, skin):
    s = f'<path d="M168 {hip + 40} L166 {feet - 4} L190 {feet - 4} L192 {hip + 40}Z M200 {hip + 40} L202 {feet - 4} L226 {feet - 4} L224 {hip + 40}Z" fill="{skin}"/>'
    s += feet_kind(feet, 'chappal', '#E3A92B', skin, spread=18)
    s += tunic(sy, 200, 'url(#k-star)', flare=22, half=50)
    s += f'<path d="M160 {sy} Q196 {sy + 28} 232 {sy}" fill="none" stroke="#FBF5E9" stroke-width="6"/>'
    s += arm((146, sy + 14), (124, sy + 80), (130, sy + 140), '#2C3E8C', skin, short=True)
    s += arm((246, sy + 14), (292, sy + 40), (296, sy - 10), '#2C3E8C', skin, short=True)
    s += f'<path d="M296 {sy - 10} L262 {sy - 34}" stroke-width="14"/><path d="M296 {sy - 10} L262 {sy - 34}" stroke="#8A3B12" stroke-width="8"/>'
    return s


def tutul(sy, hip, feet, skin):
    s = f'<path d="M168 {hip + 30} L166 {feet - 8} L190 {feet - 8} L194 {hip + 30}Z M198 {hip + 30} L202 {feet - 8} L226 {feet - 8} L224 {hip + 30}Z" fill="#F3B6C4"/>'
    s += feet_kind(feet, 'bare', '#C29068', skin, spread=18)
    s += f'<path d="M144 {sy + 2} L248 {sy + 2} Q268 {sy + 40} 272 {sy + 210} Q196 {sy + 226} 120 {sy + 210} Q124 {sy + 40} 144 {sy + 2}Z" fill="url(#k-kite)"/>'
    s += arm((146, sy + 14), (120, sy + 90), (124, sy + 150), '#E58BA0', skin)
    s += f'<rect x="100" y="{sy + 156}" width="46" height="50" rx="4" fill="#8A3B12"/><ellipse cx="123" cy="{sy + 156}" rx="27" ry="7" fill="#E3A92B"/><ellipse cx="123" cy="{sy + 206}" rx="27" ry="7" fill="#E3A92B"/>'
    s += f'<path d="M123 {sy + 150} Q200 {sy - 40} 300 136" fill="none" stroke-width="1.5"/>'
    s += arm((246, sy + 14), (270, sy + 90), (262, sy + 150), '#E58BA0', skin)
    return s


# ======================================================= ANIMALS / SPIRITS (custom bodies)
def bagha_body():
    behind = ('<path d="M268 548 Q344 524 334 430 Q330 398 308 408 Q320 430 314 462 Q302 506 262 512" fill="none" stroke-width="30"/>'
              '<path d="M268 548 Q344 524 334 430 Q330 398 308 408 Q320 430 314 462 Q302 506 262 512" fill="none" stroke="#E58A2E" stroke-width="22"/>'
              '<path d="M326 450 L340 446 M330 478 L344 480 M316 506 L328 516" stroke-width="5"/>'
              '<path d="M118 562 Q96 400 146 270 L246 270 Q296 400 274 562Z" fill="url(#a1-vein)"/>'
              '<path d="M158 320 Q196 410 234 320 Q240 480 196 528 Q152 480 158 320Z" fill="#FBF5E9"/>'
              '<path d="M146 410 L144 556 L186 556 L188 410Z M204 410 L206 556 L248 556 L246 410Z" fill="#E58A2E"/>'
              '<path d="M146 450 L164 446 M146 490 L166 486 M246 450 L228 446 M246 490 L226 486" stroke-width="5"/>'
              '<ellipse cx="164" cy="558" rx="26" ry="12" fill="#E58A2E"/><ellipse cx="226" cy="558" rx="26" ry="12" fill="#E58A2E"/>'
              '<path d="M154 556 L154 566 M164 556 L164 568 M174 556 L174 566 M216 556 L216 566 M226 556 L226 568 M236 556 L236 566" stroke-width="2.5"/>')
    front = ('<path d="M116 262 Q196 304 276 262 L282 286 Q196 330 110 286Z" fill="url(#a1-check)"/>'
             '<path d="M226 296 L252 290 L256 420 L228 420Z" fill="url(#a1-check)"/>')
    return behind, front


def shiyal(sy, hip, feet, skin):
    s = ('<path d="M250 %d Q360 %d 340 %d Q330 %d 300 %d Q320 %d 300 %d Q290 %d 246 %d" fill="#E07A2E"/>' % (hip, hip - 20, hip + 140, hip + 190, hip + 200, hip + 150, hip + 90, hip + 60, hip + 60))
    s += '<path d="M318 %d Q336 %d 330 %d Q312 %d 300 %dZ" fill="#FBF5E9"/>' % (hip + 160, hip + 170, hip + 190, hip + 200, hip + 198)
    s += legs(hip, feet, '#E07A2E', w=34)
    s += f'<path d="M159 {feet - 60} L161 {feet - 6} L191 {feet - 6} L191 {feet - 60}Z M201 {feet - 60} L201 {feet - 6} L231 {feet - 6} L233 {feet - 60}Z" fill="#1C1410"/>'
    s += feet_kind(feet, 'shoe', '#1C1410', spread=22)
    s += tunic(sy, 226, '#FBF5E9', flare=6, half=56)
    s += f'<path d="M140 {sy} L178 {sy + 4} L190 {sy + 150} L136 {sy + 150}Z M252 {sy} L214 {sy + 4} L202 {sy + 150} L256 {sy + 150}Z" fill="url(#a2-flame)"/>'
    s += f'<path d="M180 {sy + 80} Q196 {sy + 98} 216 {sy + 76}" fill="none" stroke="#E3A92B" stroke-width="4"/>'
    s += arm((140, sy + 14), (116, sy + 110), (132, sy + 190), '#FBF5E9', '#1C1410')
    s += arm((252, sy + 14), (290, sy + 80), (300, sy + 20), '#FBF5E9', '#1C1410')
    s += f'<g transform="rotate(-14 304 {sy - 4})"><rect x="282" y="{sy - 26}" width="46" height="28" rx="2" fill="#FBF5E9"/><path d="M288 {sy - 16} L320 {sy - 16} M288 {sy - 8} L310 {sy - 8}" stroke-width="2"/></g>'
    return s


def dhol_body():
    behind = ('<ellipse cx="196" cy="420" rx="128" ry="110" fill="#8E8A93"/>'
              '<path d="M112 450 L112 584 L176 584 L176 450Z M216 450 L216 584 L280 584 L280 450Z" fill="#8E8A93"/>'
              '<g fill="#FBF5E9" stroke-width="2.5"><ellipse cx="128" cy="580" rx="9" ry="6"/><ellipse cx="144" cy="582" rx="9" ry="6"/><ellipse cx="160" cy="580" rx="9" ry="6"/>'
              '<ellipse cx="232" cy="580" rx="9" ry="6"/><ellipse cx="248" cy="582" rx="9" ry="6"/><ellipse cx="264" cy="580" rx="9" ry="6"/></g>'
              '<path d="M150 300 Q196 330 242 300" fill="none" stroke="#C8341F" stroke-width="6"/>'
              '<path d="M108 420 L284 420 L284 496 L108 496Z" fill="#B5482A"/>'
              '<path d="M118 424 L136 492 L154 424 L172 492 L190 424 L208 492 L226 424 L244 492 L262 424 L280 492" fill="none" stroke="#E3A92B" stroke-width="3"/>'
              '<ellipse cx="108" cy="458" rx="16" ry="38" fill="#F3E6C8"/><ellipse cx="284" cy="458" rx="16" ry="38" fill="#F3E6C8"/>')
    return behind, ''


def kumir_body():
    behind = ('<path d="M300 470 Q380 500 372 560 Q366 600 300 598 Q340 580 336 552 Q330 520 290 500Z" fill="url(#a2-croc)"/>'
              '<path d="M226 470 L224 562 L256 562 L258 470Z M270 470 L272 562 L304 562 L302 470Z" fill="url(#a2-croc)"/>'
              '<path d="M214 566 Q214 552 236 552 L262 556 L262 568Z M262 566 Q262 552 284 552 L310 556 L310 568Z" fill="#3E7A3A"/>'
              '<path d="M200 270 L316 250 Q336 300 326 480 Q262 494 200 480 Q190 360 200 270Z" fill="#2C3E8C"/>'
              '<path d="M236 280 L262 340 L288 272Z" fill="#FBF5E9"/>'
              '<path d="M262 340 L262 476" stroke-width="3"/>'
              '<g fill="#E3A92B" stroke-width="2"><circle cx="270" cy="370" r="5"/><circle cx="270" cy="410" r="5"/><circle cx="270" cy="450" r="5"/></g>')
    front = (arm((214, 300), (176, 370), (196, 420), '#2C3E8C', '#3E7A3A') +
             '<g transform="rotate(-8 170 430)"><path d="M118 400 L206 400 L206 470 L118 470Z" fill="#C8341F"/><path d="M128 400 L128 470" stroke-width="3"/>'
             '<path d="M138 418 L196 418 M138 434 L186 434 M138 450 L192 450" stroke="#FBF5E9" stroke-width="3"/></g>'
             + arm((316, 290), (336, 380), (316, 440), '#2C3E8C', '#3E7A3A')
             + '<g fill="#E3A92B" stroke-width="2.5"><ellipse cx="318" cy="470" rx="16" ry="6"/><ellipse cx="318" cy="462" rx="16" ry="6"/><ellipse cx="318" cy="454" rx="16" ry="6"/></g>')
    return behind, front


def jol(sy, hip, feet, skin):
    s = sari_skirt(sy + 150, feet + 10, 'url(#s-wave)', '#14514F', half=54, flare=40)
    s += f'<g fill="none" stroke="#9CC7C9" stroke-width="3"><ellipse cx="196" cy="{feet + 16}" rx="140" ry="14"/><ellipse cx="196" cy="{feet + 16}" rx="100" ry="9"/></g>'
    s += tunic(sy, 170, 'url(#s-wave)', flare=2)
    s += aanchal(sy, '#14514F', '#9CC7C9')
    s += f'<g fill="#FBF5E9" stroke-width="2"><circle cx="172" cy="{sy + 6}" r="5"/><circle cx="184" cy="{sy + 12}" r="5"/><circle cx="196" cy="{sy + 14}" r="5.5"/><circle cx="208" cy="{sy + 12}" r="5"/><circle cx="220" cy="{sy + 6}" r="5"/></g>'
    s += arm((140, sy + 14), (106, sy + 90), (84, sy + 30), '#1F7A78', skin, short=True)
    s += arm((252, sy + 14), (286, sy + 90), (308, sy + 30), '#1F7A78', skin, short=True)
    s += f'<path d="M66 {sy + 60} Q78 {sy + 50} 90 {sy + 60} Q78 {sy + 68} 66 {sy + 60}Z M90 {sy + 60} L98 {sy + 52} L98 {sy + 68}Z" fill="#E07A2E" stroke-width="2.5"/>'
    s += f'<path d="M300 {sy - 20} Q312 {sy - 30} 324 {sy - 20} Q312 {sy - 12} 300 {sy - 20}Z M324 {sy - 20} L332 {sy - 28} L332 {sy - 12}Z" fill="#E3A92B" stroke-width="2.5"/>'
    return s
