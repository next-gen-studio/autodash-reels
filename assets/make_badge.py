# usage: python3 make_badge.py "TEXT" [color] [out.png]
# Makes the pop-in badge sticker (replaces the fixed NEW sticker). 420x190 canvas, same style as sticker_new.png.
# Pick TEXT per video topic: e.g. NEW, HOT, TRY THIS, iOS 27, GLOW UP, WOW, MUST TRY, XMAS, TOP PICK, EASY, FREE...
# colors: red orange gold green teal blue purple pink black
import sys
from PIL import Image, ImageDraw, ImageFont
P = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
txt = sys.argv[1].strip()
col = sys.argv[2] if len(sys.argv) > 2 else 'red'
out = sys.argv[3] if len(sys.argv) > 3 else 'badge.png'
C = {'red': (255, 59, 48), 'orange': (255, 149, 0), 'gold': (255, 196, 0), 'green': (40, 200, 90),
     'teal': (0, 190, 200), 'blue': (10, 132, 255), 'purple': (150, 70, 255), 'pink': (255, 55, 140),
     'black': (25, 25, 30)}
fill = C.get(col, C['red'])
txt_col = (20, 20, 20) if col == 'gold' else (255, 255, 255)
W, H = 420, 190
im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
size = 96
while size > 30:
    f = ImageFont.truetype(P, size)
    tw = d.textlength(txt, font=f)
    if tw <= W - 90: break
    size -= 2
bb = d.textbbox((0, 0), txt, font=f)
th = bb[3] - bb[1]
bw = min(W - 10, int(tw + 80)); bh = min(H - 20, max(120, th + 60))
x0 = (W - bw) // 2; y0 = (H - bh) // 2
d.rounded_rectangle((x0 + 4, y0 + 8, x0 + bw + 4, y0 + bh + 8), radius=34, fill=(0, 0, 0, 90))
d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=34, fill=fill + (255,), outline=(255, 255, 255, 255), width=7)
d.text(((W - tw) / 2, y0 + (bh - th) / 2 - bb[1]), txt, font=f, fill=txt_col)
im.save(out)
print(out, txt, col)
