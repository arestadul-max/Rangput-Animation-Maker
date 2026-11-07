import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fullbody
from specs import *

CHECK = lambda pid, c1, c2: (f'<pattern id="{pid}" width="22" height="22" patternUnits="userSpaceOnUse"><rect width="22" height="22" fill="{c1}"/>'
                             f'<path d="M0 6 L22 6 M0 16 L22 16 M6 0 L6 22 M16 0 L16 22" stroke="{c2}" stroke-width="3" opacity="0.8"/></pattern>')

TUTUL_STRING_FIX = None

SPEC = {
    'Tuli:': dict(chin=236, skin='#C98B5E', disc='#1F7A78', P=dict(body=tuli, front=TULI_FRONT),
                  removes=['<circle cx="196" cy="190" r="168" fill="none" stroke="#1F7A78" stroke-width="4" stroke-dasharray="2 9"/>',
                           '<g fill="#1C1410"><ellipse cx="258" cy="252" rx="17" ry="22"/><ellipse cx="266" cy="290" rx="16" ry="21"/><ellipse cx="272" cy="328" rx="15" ry="20"/><ellipse cx="276" cy="366" rx="14" ry="20"/></g>']),
    'Ronju:': dict(chin=238, skin='#B87A4B', disc='#E3A92B', P=dict(body=ronju),
                   removes=['<path d="M40 400 L94 140" stroke-width="11"/><path d="M40 400 L94 140" stroke="#8C8C9A" stroke-width="5"/>',
                            're:<g transform="rotate\\(-12 92 92\\)">.*?</g>']),
    'Khema Dida:': dict(chin=242, skin='#B98258', disc='#22305F', P=dict(body=dida),
                        removes=['<circle cx="300" cy="340" r="70" fill="#FFC94A" opacity="0.28"/>', 're:<g transform="rotate\\(-8 300 350\\)">.*?</g>'],
                        keep_stars=True),
    'Pupu:': dict(chin=242, skin='#C48A5A', disc='#E58BA0', P=dict(body=pupu, kid=True),
                  removes=['<path d="M90 400 L92 352 L74 316 M92 352 L112 318" fill="none" stroke-width="13"/><path d="M90 400 L92 352 L74 316 M92 352 L112 318" fill="none" stroke="#8A3B12" stroke-width="7"/>',
                           '<path d="M74 316 Q93 330 112 318" fill="none" stroke="#C8341F" stroke-width="2.5"/>']),
    'Inspector Moyna:': dict(chin=240, skin='#B07548', disc='#3E7A3A', P=dict(body=moyna), removes=[]),
    'Professor Ghontu:': dict(chin=246, skin='#C29068', disc='#B5482A', P=dict(body=ghontu, defs=CHECK('gh-check', '#2C3E8C', '#9CC7C9')), removes=[]),
    'Bhombol:': dict(chin=244, skin='#C79066', disc='#C8341F', P=dict(body=bhombol, behind=BHOMBOL_BEHIND),
                     removes=['<circle cx="196" cy="168" r="104" fill="none" stroke="#1C1410" stroke-width="24"/>', '<circle cx="196" cy="168" r="104" fill="none" stroke="#FBF5E9" stroke-width="16"/>']),
    'Kalo Megh:': dict(chin=244, skin='#A86F48', disc='#3A2A3E', P=dict(body=kalo, tall=30), removes=[]),
    'Shubho:': dict(chin=238, skin='#B98258', disc='#2C3E8C', P=dict(body=shubho, defs=CHECK('sb-check', '#FBF5E9', '#2C3E8C')), removes=['re:<g transform="rotate\\(-10 100 370\\)">.*?</g>']),
    'Rini:': dict(chin=238, skin='#C48A5A', disc='#E58BA0', P=dict(body=rini), removes=[]),
    'Baba:': dict(chin=244, skin='#B98258', disc='#3E7A3A', P=dict(body=haripada), removes=['re:<g transform="rotate\\(-14 96 350\\)">.*?</g>']),
    'Ma:': dict(chin=242, skin='#B07548', disc='#1F7A78', P=dict(body=mallika), removes=[]),
    'Mitul:': dict(chin=240, skin='#B07548', disc='#2C3E8C', P=dict(body=mitul, kid=True), removes=['re:<g transform="rotate\\(22 300 240\\)">.*?</g>']),
    'Babai:': dict(chin=248, skin='#C48A5A', disc='#3E7A3A', P=dict(body=babai, kid=True), removes=[]),
    'Jhumpa:': dict(chin=242, skin='#A86F48', disc='#E58BA0', P=dict(body=jhumpa, kid=True), removes=[]),
    'Tutul:': dict(chin=252, skin='#C29068', disc='#1F7A78', P=dict(body=tutul, kid=True), removes=['<path d="M114 330 Q190 210 300 112" fill="none" stroke="#1C1410" stroke-width="1.5"/>']),
}


bb, bf = bagha_body()
db, _ = dhol_body()
kb, kf = kumir_body()
SPEC.update({
    'Bagha:': dict(chin=272, skin='#E58A2E', disc='#3E7A3A', P=dict(custom=(bb, bf, 562), scale=0.95), removes=[]),
    'Shiyal Pandit:': dict(chin=262, skin='#E07A2E', disc='#E3A92B', P=dict(body=shiyal, scale=0.72), removes=[]),
    'Dhol:': dict(chin=368, skin='#8E8A93', disc='#C8341F', P=dict(custom=(db, '', 584), scale=0.9),
                  removes=['re:<path d="M96 334 L300 334[^>]*/>', 're:<path d="M110 340 L130 398[^>]*/>', 're:<ellipse cx="96" cy="369"[^>]*/>']),
    'Kumir Babu:': dict(chin=290, skin='#3E7A3A', disc='#1F7A78', P=dict(custom=(kb, kf, 568), scale=0.95),
                        removes=['re:<path d="M226 270 Q246 330 236 404[^>]*/>', 're:<path d="M248 270 L276 320 L296 262Z"[^>]*/>',
                                 're:<path d="M58 304 L178 304 L178 392 L58 392Z"[^>]*/>', 're:<path d="M72 304 L72 392"[^>]*/>',
                                 're:<path d="M86 326 L162 326[^>]*/>', 're:<g fill="#E3A92B"><ellipse cx="208".*?</g>']),
    'Jol-Konya:': dict(chin=234, skin='#7FC4C0', disc='#2C3E8C', P=dict(body=jol, clip_pad=30),
                       removes=['<path d="M176 232 L176 300 L216 300 L216 232Z" fill="#7FC4C0"/>']),
})
FULL_ALREADY = ('Mishti:', 'Gyani:', 'Chhotu:', 'Rupoli:', 'Mechho Bhoot:', 'Petni Pori:', 'Bot-Dadu:')


def reframe(svg):
    m = re.match(r'<svg class="art"[^>]*aria-label="([^"]*)"[^>]*>(.*)</svg>', svg, re.S)
    aria, inner = m.group(1), m.group(2)
    dm = re.search(r'<circle cx="196" cy="190" r="150" fill="(#[0-9A-Fa-f]{6})"/>', inner)
    disc = dm.group(1) if dm else '#2C3E8C'
    defs = ''.join(re.findall(r'<defs>.*?</defs>', inner, re.S))
    rest = re.sub(r'<defs>.*?</defs>', '', inner, flags=re.S)
    rest = re.sub(r'<rect width="392" height="400"[^>]*/>', '', rest)
    rest = re.sub(r'<circle cx="196" cy="190" r="150"[^>]*/>', '', rest)
    backdrop = (f'<rect width="392" height="640" fill="#F3E6C8"/>'
                f'<path d="M46 640 L46 210 A150 150 0 0 1 346 210 L346 640Z" fill="{disc}"/>'
                f'<ellipse cx="196" cy="608" rx="110" ry="14" fill="#1C1410" opacity="0.18"/>')
    return (f'<svg class="art" viewBox="0 0 392 640" role="img" aria-label="{aria}">{defs}{backdrop}'
            f'<g transform="translate(-19.6,165) scale(1.1)">{rest}</g></svg>')


def convert_card(svg):
    aria = re.search(r'aria-label="([^"]*)"', svg).group(1)
    if aria.startswith(FULL_ALREADY):
        return reframe(svg)
    key = next((k for k in SPEC if aria.startswith(k)), None)
    if key is None:
        return None
    sp = SPEC[key]
    removes = []
    s2 = svg
    for r in sp['removes']:
        if r.startswith('re:'):
            s2, n = re.subn(r[3:], '', s2, count=1, flags=re.S)
            if n == 0:
                raise SystemExit(f'{key} regex not found {r}')
        else:
            removes.append(r)
    P = dict(sp['P'])
    out = fullbody.card(key, s2, sp['chin'], sp['skin'], P, removes, disc=sp['disc'])
    if P.get('defs'):
        out = out.replace('<defs>', '<defs>' + P['defs'], 1)
    new_aria = aria.rstrip('.') + ' — full body, standing'
    out = out.replace(f'aria-label="{aria}"', f'aria-label="{new_aria}"', 1)
    return out


def convert_file(path, height_from=1320, height_to=1560):
    s = open(path).read()
    count = 0

    def rep(m):
        nonlocal count
        r = convert_card(m.group(0))
        if r is None:
            return m.group(0)
        count += 1
        return r
    s = re.sub(r'<svg class="art".*?</svg>', rep, s, flags=re.S)
    s = s.replace('.art{display:block;width:100%;height:400px;border-bottom:3px solid #1C1410}',
                  '.art{display:block;width:100%;height:auto;border-bottom:3px solid #1C1410}')
    s = s.replace(f'height: {height_from}px; box-sizing', f'height: {height_to}px; box-sizing')
    s = s.replace(f'"height":{height_from}}}', f'"height":{height_to}}}')
    open(path, 'w').write(s)
    return count


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, convert_file(p))
