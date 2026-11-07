"""Builds the scenes.xlsx template: a Scenes sheet with dropdowns plus reference lists."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from . import engine as E
from . import audio as A

INK = '1C1410'
HEAD = PatternFill('solid', fgColor='1C1410')
PAPER = PatternFill('solid', fgColor='F3E6C8')
EX = PatternFill('solid', fgColor='FBF5E9')
COLS = [('Shot', 6, 'Number of the shot (just for you).'),
        ('Place', 24, 'Where it happens. Pick from the list (Places sheet), or an image file name from the images folder.'),
        ('View', 9, 'Which part of the place to show: left, center, right (or 0–100).'),
        ('Time', 9, 'day, evening or night. Night tints everything blue.'),
        ('Camera', 11, 'auto, wide, medium, close, push-in, pull-out, pan-left, pan-right, follow. Add "shake" for a shaky camera.'),
        ('Focus', 12, 'Who the camera looks at (default: the speaker).'),
        ('Cast', 30, 'Who is in the shot and where: "mishti left, tutul right". Positions: far-left, left, center, right, far-right or -100..100. Add back / front / flip / hidden. Leave empty to keep the same cast as the shot before.'),
        ('Actions', 30, 'What they do: "tutul: jump; mishti: enter-left". Add @seconds for timing: "mechho: scared @1.5". See the Actions sheet.'),
        ('Speaker', 11, 'Who talks (their mouth moves). For two voices: "tutul; mishti".'),
        ('Voice', 16, 'The recording file in the voice folder, e.g. 01_mishti.wav. Two clips: "a.wav; b.wav @2.5".'),
        ('Subtitle', 34, 'The caption. Use | to split a long line into two captions. Start with ^ to put it at the top. For a title card this is the title.'),
        ('Emote', 14, 'A symbol over someone’s head: "tutul: !", "mishti: heart @1". See the Actions sheet.'),
        ('SFX', 18, 'Sound effects: "whoosh @0.5, thud @1.2". Built-in names are on the Sounds sheet, or use a file from the sounds folder.'),
        ('Music', 9, 'calm, spooky, comic, tense, sweet, happy, none. Empty = keep the previous music.'),
        ('Duration', 9, 'Seconds. Empty = automatic (fits the voice).'),
        ('Transition', 10, 'cut or fade (dip to black) into this shot.'),
        ('Notes', 24, 'Anything for yourself. Ignored.'),
        ('Expression', 22, 'Optional. Faces change automatically with the situation; set one here to choose it yourself: "pupu: angry @1.2, mitul: smug". See the Actions sheet.')]

EXAMPLE = [
    [1, 'title', '', 'night', '', '', '', '', '', '', 'মেছো ভূত | The Fish-Thief Ghost', '', 'bell', 'calm', 3, '', 'Title card'],
    [2, 'sen-kitchen-night', 'center', 'night', 'push-in', 'mishti', 'mishti left', '', 'mishti', '01_mishti.wav', 'Every night, fish goes missing in this house. | The thief isn’t human.', '', 'clock', 'spooky', '', 'fade', ''],
    [3, 'sen-kitchen-night', '', '', 'wide', '', 'mishti far-left, mechho right hidden', 'mechho: appear @0.3, hold-fish; mishti: hiss @1.2', '', '', '', 'mishti: ! @1.0', 'rise @0.2', '', 3, '', 'Mechho appears with a fish'],
    [4, 'sen-kitchen-night', '', '', 'close', 'mechho', '', 'mechho: scared', 'mechho', '06_mechho.wav', 'Help! A cat!', 'mechho: sweat @0.4', 'whoosh @0.2', 'comic', '', '', ''],
    [5, 'rooftop-at-night', 'center', 'night', 'medium', 'tutul', 'tutul left, mechho right', 'mechho: cry', 'tutul', '09_tutul.wav', 'Uncle, why are you crying?', '', 'wind', 'calm', '', 'fade', ''],
    [6, 'rooftop-at-night', '', '', 'medium', 'tutul', '', 'tutul: offer', 'tutul', '10_tutul.wav', 'There’s no fish. | Want a sweet?', 'mechho: ? @1.0', '', 'sweet', '', '', ''],
    [7, 'rooftop-at-night', '', '', 'push-in', 'mechho', '', 'mechho: glow, hold-sweet, happy @1.0', 'mechho', '11_mechho.wav', 'This is… better than fish!', 'mechho: heart @1.2', 'sparkle', '', '', '', ''],
]


def make_template(path, lib, example=False):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Scenes'
    ws.sheet_properties.tabColor = 'C8341F'
    for i, (h, w, tip) in enumerate(COLS, start=1):
        c = ws.cell(row=1, column=i, value=h)
        c.font = Font(bold=True, color='FBF5E9')
        c.fill = HEAD
        c.alignment = Alignment(horizontal='center', vertical='center')
        ws.column_dimensions[c.column_letter].width = w
        t = ws.cell(row=2, column=i, value=tip)
        t.font = Font(italic=True, size=8, color='8A3B12')
        t.alignment = Alignment(wrap_text=True, vertical='top')
        t.fill = PAPER
    ws.row_dimensions[2].height = 92
    ws.freeze_panes = 'C3'
    rows = EXAMPLE if example else [[i] + [''] * (len(COLS) - 1) for i in range(1, 31)]
    for r, row in enumerate(rows, start=3):
        for c, v in enumerate(row, start=1):
            cell = ws.cell(row=r, column=c, value=(v if v != '' else None))
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            if example:
                cell.fill = EX
    add_reference_sheets(wb, lib)
    # dropdowns
    n_pl = len(lib.places) + 1
    dv = DataValidation(type='list', formula1=f"=Places!$A$2:$A${n_pl}", allow_blank=True, showErrorMessage=False)
    ws.add_data_validation(dv)
    dv.add('B3:B400')
    for col, opts in (('C', 'left,center,right'), ('D', 'day,evening,night'), ('E', 'auto,wide,medium,close,push-in,pull-out,pan-left,pan-right,follow'),
                      ('N', ','.join(A.MOODS)), ('P', 'cut,fade')):
        d = DataValidation(type='list', formula1=f'"{opts}"', allow_blank=True, showErrorMessage=False)
        ws.add_data_validation(d)
        d.add(f'{col}3:{col}400')
    n_ch = len(lib.chars) + 1
    for col in ('F',):
        d = DataValidation(type='list', formula1=f"=Characters!$A$2:$A${n_ch}", allow_blank=True, showErrorMessage=False)
        ws.add_data_validation(d)
        d.add(f'{col}3:{col}400')
    wb.save(path)


def add_reference_sheets(wb, lib):
    cs = wb.create_sheet('Characters')
    cs.append(['Name to type', 'Character', 'Bangla', 'Role', 'What they look like'])
    for slug in ['mishti', 'mechho', 'tutul'] + sorted(s for s in lib.chars if s not in ('mishti', 'mechho', 'tutul')):
        c = lib.chars[slug]
        cs.append([slug, c['name'], c.get('bn', ''), c.get('role', ''), c.get('desc', '')])
    ps = wb.create_sheet('Places')
    ps.append(['Name to type', 'Place', 'Bangla', 'What it shows'])
    for slug, p in lib.places.items():
        ps.append([slug, p['name'], p.get('bn', ''), p.get('desc', '')])
    acs = wb.create_sheet('Actions')
    acs.append(['Action', 'What it does'])
    for k, v in E.ACTIONS.items():
        acs.append([k, v])
    acs.append([])
    acs.append(['Body move (rigged characters)', 'What it does - works on: ' + ', '.join(sorted(E.RIG.RIGS))])
    for k, v in E.RIG.POSES.items():
        acs.append([k, v[2]])
    acs.append([])
    acs.append(['Expression', 'Faces change on their own; use the Expression column to choose one'])
    from . import expressions as X
    for k in X.EXPR:
        acs.append([k, ''])
    acs.append([])
    acs.append(['Object action', 'For the ball, bat, stumps or any object in library\\props (e.g. "ball: bowl mitul pupu")'])
    for k, v in E.BALL_ACTIONS.items():
        acs.append([k, v])
    acs.append([])
    acs.append(['Emote', 'Meaning'])
    for k, v in E.EMOTES.items():
        acs.append([k, v])
    acs.append([])
    acs.append(['Camera', 'What it does'])
    for k, v in (('auto', 'Wide shot, or medium on the speaker when two or more people are in the shot.'), ('wide', 'The whole scene.'),
                 ('medium', 'Waist-up on the focus character.'), ('close', 'Face close-up on the focus character.'),
                 ('push-in', 'Slowly moves in from wide to medium.'), ('pull-out', 'Slowly moves out from medium to wide.'),
                 ('pan-left', 'Slides across the place to the left.'), ('pan-right', 'Slides across to the right.'),
                 ('follow', 'Stays on the focus character as they move.'), ('ball', 'Follows the cricket ball.')):
        acs.append([k, v])
    ss = wb.create_sheet('Sounds')
    ss.append(['Sound effect', 'What it is'])
    for k, (d, _) in A.SFX.items():
        ss.append([k, d])
    ss.append([])
    ss.append(['Music mood', 'What it sounds like'])
    for k, v in A.MOODS.items():
        ss.append([k, v])
    for sh in (cs, ps, acs, ss):
        for c in sh[1]:
            c.font = Font(bold=True, color='FBF5E9')
            c.fill = HEAD
        for col, w in zip('ABCDE', (18, 30, 16, 26, 90)):
            sh.column_dimensions[col].width = w
        for row in sh.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical='top')


def refresh_lists(path, lib):
    from openpyxl import load_workbook
    wb = load_workbook(path)
    for name in ('Characters', 'Places', 'Actions', 'Sounds'):
        if name in wb.sheetnames:
            del wb[name]
    add_reference_sheets(wb, lib)
    wb.save(path)
