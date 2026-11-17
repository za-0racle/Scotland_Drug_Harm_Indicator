"""Render SDHI's code-owned vector identity and bitmap derivatives.

Run manually with Python + Pillow. No frontend/runtime dependency is added.
The motif is abstract branding, not a chart of research data.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
BRAND = PUBLIC / 'brand'
BRAND.mkdir(exist_ok=True)
INK, GOLD, IVORY, MUTED = '#252525', '#C9A227', '#FAF8F2', '#625F55'


def font(size, bold=False):
    candidates = [Path('C:/Windows/Fonts') / ('segoeuib.ttf' if bold else 'segoeui.ttf'),
                  Path('/usr/share/fonts/truetype/dejavu') / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise RuntimeError('Install Segoe UI or DejaVu Sans to render the brand assets.')


MARK = '''<rect width="64" height="64" rx="14" fill="#252525"/>
<path d="M14 47h36" fill="none" stroke="#FAF8F2" stroke-opacity=".35" stroke-width="2"/>
<path d="m14 40 12-11 12 5 12-17" fill="none" stroke="#C9A227" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<g fill="#FAF8F2"><circle cx="14" cy="40" r="3"/><circle cx="26" cy="29" r="3"/><circle cx="38" cy="34" r="3"/><circle cx="50" cy="17" r="3"/></g>'''
icon_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>SDHI analytical line symbol</title>{MARK}</svg>\n'
(PUBLIC / 'favicon.svg').write_text(icon_svg, encoding='utf-8')
(BRAND / 'sdhi-icon.svg').write_text(icon_svg, encoding='utf-8')
logo_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="80" viewBox="0 0 280 80" role="img" aria-labelledby="title">
<title id="title">SDHI — Scotland Drug Harm Intelligence</title>
<g transform="translate(0 8)">{MARK}</g>
<g fill="#252525" font-family="Segoe UI,DejaVu Sans,sans-serif">
<text x="80" y="38" font-size="32" font-weight="700" letter-spacing="2">SDHI</text>
<text x="81" y="57" font-size="12">Scotland Drug Harm</text>
<text x="81" y="73" font-size="12">Intelligence</text></g></svg>\n'''
(BRAND / 'sdhi-logo.svg').write_text(logo_svg, encoding='utf-8')
(BRAND / 'sdhi-logo-dark.svg').write_text(logo_svg.replace('<g fill="#252525" font-family=', '<g fill="#FAF8F2" font-family='), encoding='utf-8')


def mark(size):
    scale = 4
    image = Image.new('RGBA', (size * scale, size * scale))
    draw = ImageDraw.Draw(image)
    unit = size * scale / 64
    point = lambda x, y: (round(x * unit), round(y * unit))
    draw.rounded_rectangle((0, 0, size * scale - 1, size * scale - 1), radius=14 * unit, fill=INK)
    draw.line([point(14, 47), point(50, 47)], fill='#74736E', width=max(1, round(2 * unit)))
    draw.line([point(14, 40), point(26, 29), point(38, 34), point(50, 17)], fill=GOLD, width=max(1, round(4 * unit)), joint='curve')
    for x, y in [(14, 40), (26, 29), (38, 34), (50, 17)]:
        draw.ellipse((point(x - 3, y - 3), point(x + 3, y + 3)), fill=IVORY)
    return image.resize((size, size), Image.Resampling.LANCZOS)


for size in [192, 512]:
    mark(size).save(BRAND / f'sdhi-icon-{size}.png')
apple = Image.new('RGB', (180, 180), IVORY)
apple.paste(mark(148), (16, 16), mark(148))
apple.save(PUBLIC / 'apple-touch-icon.png')
mark(256).save(PUBLIC / 'favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
logo = Image.new('RGBA', (840, 240))
logo.paste(mark(192), (0, 24))
d = ImageDraw.Draw(logo)
d.text((240, 6), 'SDHI', font=font(96, True), fill=INK)
d.text((243, 128), 'Scotland Drug Harm', font=font(36), fill=INK)
d.text((243, 176), 'Intelligence', font=font(36), fill=INK)
logo.save(BRAND / 'sdhi-logo.png')

# Social image: typeset labels and an abstract motif, with no data or agency marks.
scale = 2
social = Image.new('RGB', (1200 * scale, 630 * scale), IVORY)
d = ImageDraw.Draw(social)
d.rectangle((0, 0, 1200 * scale, 12 * scale), fill=GOLD)
social.paste(mark(76 * scale), (72 * scale, 63 * scale), mark(76 * scale))
d.text((169 * scale, 65 * scale), 'SDHI', font=font(48 * scale, True), fill=INK)
d.text((73 * scale, 195 * scale), 'Scotland Drug Harm', font=font(58 * scale, True), fill=INK)
d.text((73 * scale, 273 * scale), 'Intelligence', font=font(64 * scale, True), fill=INK)
d.text((76 * scale, 378 * scale), 'Historical Drug Harm Research Dashboard', font=font(27 * scale), fill=MUTED)
d.line([(76 * scale, 467 * scale), (1124 * scale, 467 * scale)], fill='#E8D9AC', width=2 * scale)
d.text((76 * scale, 510 * scale), 'sdhi.cc', font=font(26 * scale, True), fill=INK)
d.text((765 * scale, 514 * scale), 'Data analytics · MSc research', font=font(21 * scale), fill=MUTED)
# Standalone abstract geometry, separated from the title block.
pts = [(933, 281), (985, 237), (1037, 257), (1119, 148)]
d.line([(x * scale, y * scale) for x, y in pts], fill=GOLD, width=6 * scale, joint='curve')
for x, y in pts:
    d.ellipse(((x - 6) * scale, (y - 6) * scale, (x + 6) * scale, (y + 6) * scale), fill=INK)
social.resize((1200, 630), Image.Resampling.LANCZOS).save(PUBLIC / 'og-image.png')
print('SDHI SVG, PNG, Apple touch and multi-resolution ICO assets generated.')
