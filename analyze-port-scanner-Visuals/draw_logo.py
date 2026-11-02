#!/usr/bin/env python3
"""analyze-port-scanner logo: the front of a rotary plow head on, a great circular housing in diesel green
enameled iron, inside it the rotor as a ring of heavy angled blades in ballast grey around a dark hub, cutting
edges picked out in signal red where paint survives, snow packed unevenly between the blades, thick at the lower
left and dusting the upper right, one unlit headlamp above on a short bracket in dust coloured glass. Name below
in B612 in ballast grey on diesel green, squared capitals evenly spaced as if each letter had its own column."""
import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A = sys.argv[1] if len(sys.argv) > 1 else ""
W, H = 900, 520
GREEN = (38, 84, 52); GREY = (150, 152, 148); RED = (196, 44, 40); DUST = (232, 228, 214)
img = Image.new("RGB", (W, H), GREEN); d = ImageDraw.Draw(img, "RGBA")
cx, cy, R = 450, 208, 148
# headlamp on its short bracket above the housing, unlit
d.rectangle([cx - 7, cy - R - 42, cx + 7, cy - R + 4], fill=(40, 42, 40))
d.ellipse([cx - 17, cy - R - 72, cx + 17, cy - R - 38], fill=(198, 188, 162), outline=(40, 42, 40), width=3)
# the great circular housing
d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(30, 68, 42), outline=(18, 42, 26), width=6)
d.ellipse([cx - R + 16, cy - R + 16, cx + R - 16, cy + R - 16], outline=(52, 104, 64), width=4)
thin = A == "--v1"  # v1 flaw: blades drawn thin and many, merging into a plain fan at small size
n = 18 if thin else 9
for i in range(n):  # rotor: a ring of angled blades around a dark hub
    a = math.radians(i * (360 / n) + 14)
    x1, y1 = cx + math.cos(a) * 34, cy + math.sin(a) * 34; x2, y2 = cx + math.cos(a) * (R - 26), cy + math.sin(a) * (R - 26)
    # heavy blade plate: a thick grey bar pitched along the tangent, its cutting edge in signal red
    tx, ty = -math.sin(a), math.cos(a)
    if thin:
        d.line([(x1, y1), (x2 + tx * 20, y2 + ty * 20)], fill=GREY, width=3)
    else:
        d.line([(x1, y1), (x2 + tx * 18, y2 + ty * 18)], fill=GREY, width=27)
        ex1, ey1 = x1 + tx * 13, y1 + ty * 13; ex2, ey2 = x2 + tx * 31, y2 + ty * 31
        d.line([(ex1, ey1), (ex2, ey2)], fill=RED, width=5)  # cutting edge along the pitched face
# snow packed between the blades: thick wedged at the lower left, barely dusting the upper right
for (a, dist, s) in [(140, 104, 20), (168, 96, 24), (198, 108, 18), (222, 88, 15)]:
    r = math.radians(a); x, y = cx + math.cos(r) * dist, cy + math.sin(r) * dist
    d.ellipse([x - s, y - s * .66, x + s, y + s * .66], fill=(250, 250, 247))
for (a, dist) in [(28, 112), (52, 96), (330, 118)]:
    r = math.radians(a); x, y = cx + math.cos(r) * dist, cy + math.sin(r) * dist
    d.ellipse([x - 6, y - 4, x + 6, y + 4], fill=(250, 250, 247, 170))  # dusting only
d.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=(24, 26, 24), outline=(90, 92, 88), width=3)  # dark hub
d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(70, 72, 70))
# name in B612 squared capitals, ballast grey on the diesel green ground, each letter in its own column
try:
    f = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/B612.ttf", 34)
except Exception:
    f = ImageFont.load_default()
name = "ANALYZE-PORT-SCANNER"
if A == "--v2":  # v2 flaw: ordinary mixed case running text, no timetable columns
    d.text((450, 452), "analyze-port-scanner", font=f, fill=GREY, anchor="mm")
else:
    cell = 40; total = cell * len(name); x = 450 - total / 2
    for c in name:
        d.text((x + cell / 2, 452), c, font=f, fill=(196, 198, 192), anchor="mm"); x += cell
img = img.filter(ImageFilter.GaussianBlur(0.3))
out = {"--v1": "scratch/logo-v1.png", "--v2": "scratch/logo-v2.png"}.get(A, "logo.png")
img.save(__file__.rsplit("/", 1)[0] + "/" + out)
if A == "":
    img.resize((64, 37)).save(__file__.rsplit("/", 1)[0] + "/scratch/logo64-ship.png")
print("saved", out)
