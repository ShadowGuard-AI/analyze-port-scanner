#!/usr/bin/env python3
"""analyze-port-scanner wordmark banner: the Donner Pass in hard winter, snow standing in vertical walls taller
than the train in the cuts, the rotary plow leading from the left with its rotor turning and a long plume of snow
arcing off to the right in late afternoon light, the locomotive behind it only diesel green bulk and exhaust,
mileposts passing at counted intervals with tops clear, spikes and plates glinting along the near rail where the
plow has cleared to bare steel, cleared dark track behind, drift closing over the rails ahead, and the project
name painted in B612 in dust white on the diesel green flank board of the plow housing, half scoured by blown
snow, one board only and no other readable mark."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(19)
A = sys.argv[1] if len(sys.argv) > 1 else ""
W, H = 1200, 420
GREEN = (38, 84, 52); GREY = (128, 130, 126); RED = (196, 44, 40); DUST = (232, 228, 214)
img = Image.new("RGB", (W, H), (206, 210, 204)); d = ImageDraw.Draw(img, "RGBA")
d.polygon([(0, 96), (300, 52), (640, 84), (960, 44), (1200, 80), (1200, 130), (0, 130)], fill=(224, 226, 220))  # ridge
d.rectangle([0, 120, W, H], fill=(238, 239, 235))  # snow field
# vertical snow walls taller than the train, either side of the cut
d.polygon([(0, 150), (470, 168), (470, 330), (0, 356)], fill=(247, 248, 245))
d.polygon([(0, 150), (470, 168), (470, 186), (0, 172)], fill=(216, 219, 214))
d.polygon([(880, 176), (1200, 158), (1200, 340), (880, 326)], fill=(247, 248, 245))
d.polygon([(880, 176), (1200, 158), (1200, 176), (880, 194)], fill=(216, 219, 214))
# ahead, the drift closes over the rails completely at the right
d.polygon([(880, 240), (1200, 226), (1200, 326), (880, 326)], fill=(251, 251, 248))
# cleared track behind and under the train, dark through white country
d.polygon([(0, 316), (1200, 296), (1200, 330), (0, 356)], fill=(52, 50, 46))
d.line([(0, 322), (1200, 302)], fill=(156, 158, 154), width=4)  # near rail, bare steel glinting
d.line([(0, 348), (1200, 326)], fill=(140, 142, 138), width=4)
for x in range(6, 1200, 44):
    d.line([(x, 330), (x + 22, 328)], fill=(88, 80, 68), width=5)  # sleepers
    if x % 132 == 6:  # spikes and plates glinting where the plow has just cleared
        d.rectangle([x + 4, 318, x + 34, 328], fill=(108, 110, 106), outline=(72, 72, 70))
        d.ellipse([x + 10, 320, x + 16, 326], fill=(210, 212, 206)); d.ellipse([x + 24, 320, x + 30, 326], fill=(210, 212, 206))
# mileposts down the line at counted intervals, faces turned three quarters away
for (x, y, s) in [(520, 224, 1.0), (700, 216, .84), (862, 210, .7)]:
    d.rectangle([x, y, x + 10 * s, y + 56 * s], fill=GREY)
    d.rectangle([x - 3 * s, y - 13 * s, x + 13 * s, y], fill=(104, 106, 102))
    d.rectangle([x - 3 * s, y - 17 * s, x + 13 * s, y - 13 * s], fill=(250, 250, 247))
# exhaust in the cold above the locomotive
for (x, y, r) in [(210, 148, 52), (300, 134, 68), (396, 146, 48)]:
    d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(120, 122, 118, 70))
# locomotive bulk pushing, diesel green, behind the plow
d.rectangle([96, 176, 330, 322], fill=GREEN)
d.rectangle([96, 176, 330, 196], fill=(30, 66, 42))
d.rectangle([150, 140, 182, 178], fill=(44, 46, 44))  # stack
# the rotary plow leading from the left: housing front three quarter, rotor, flank board on its side
px, py = 408, 252
d.ellipse([px - 86, py - 86, px + 86, py + 86], fill=GREEN, outline=(24, 54, 34), width=5)
for i in range(9):
    a = math.radians(i * 40 + 20); x1, y1 = px + math.cos(a) * 21, py + math.sin(a) * 21; x2, y2 = px + math.cos(a) * 70, py + math.sin(a) * 70
    d.line([(x1, y1), (x2, y2)], fill=GREY, width=13); d.line([(x1, y1), (x2, y2)], fill=RED, width=3)
for (a, ln) in [(150, 62), (185, 66), (218, 54)]:
    r = math.radians(a); x, y = px + math.cos(r) * ln, py + math.sin(r) * ln
    d.ellipse([x - 12, y - 8, x + 12, y + 8], fill=(252, 252, 249))
d.ellipse([px - 18, py - 18, px + 18, py + 18], fill=(26, 28, 26))
d.rectangle([px - 7, py - 112, px + 7, py - 86], fill=(44, 46, 44))
d.ellipse([px - 12, py - 134, px + 12, py - 110], fill=(196, 186, 160), outline=(44, 46, 44), width=3)  # unlit lamp
# flank board on the plow housing side, between locomotive and rotor
d.rectangle([196, 226, 330, 286], fill=(22, 54, 32), outline=DUST, width=2)
try:
    f = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/B612.ttf", 15)
except Exception:
    f = ImageFont.load_default()
name = "analyze-port-scanner"
if A == "--v1":  # v1 flaw: name lettered on a station style board planted beside the track, not on the machine
    d.rectangle([900, 96, 1150, 140], fill=GREEN, outline=(24, 54, 34), width=3)
    d.rectangle([1018, 140, 1032, 190], fill=GREY)
    d.text((1025, 118), name, font=f, fill=DUST, anchor="mm")
elif A == "--v2":  # v2 flaw: board lettering crisp and unscoured, fresh paint in a working pass
    d.multiline_text((200, 232), "analyze-\nport-\nscanner", font=f, fill=DUST, spacing=3)
else:
    lines = ["analyze-", "port-", "scanner"]
    for i, lt in enumerate(lines):
        d.text((202, 230 + i * 19), lt, font=f, fill=DUST)
    # blown snow scouring the lettering: white streaks eating the paint from the right edge only
    for _ in range(20):
        x, y = random.uniform(288, 326), random.uniform(228, 284)
        d.line([(x, y), (x + random.uniform(5, 16), y)], fill=(238, 239, 235), width=2)
    for _ in range(12):
        x, y = random.uniform(260, 326), random.uniform(228, 284)
        d.line([(x, y), (x + 4, y)], fill=(238, 239, 235), width=1)
# the plume: a long white arc thrown off to the right, hanging in the late light
for i in range(44):
    t = i / 44; x = px + 84 + t * 560 + random.uniform(-10, 10); y = py - 52 - math.sin(t * 2.4) * 104 + t * 84
    r = random.uniform(6, 17); d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(250, 250, 247, 210))
for _ in range(30):  # blown snow streaming off the upwind wall top
    x, y = random.uniform(0, 460), random.uniform(138, 166)
    d.line([(x, y), (x + random.uniform(14, 40), y - 3)], fill=(252, 252, 250), width=2)
img = img.filter(ImageFilter.GaussianBlur(0.5))
out = {"--v1": "scratch/banner-v1.png", "--v2": "scratch/banner-v2.png"}.get(A, "banner.png")
img.save(__file__.rsplit("/", 1)[0] + "/" + out); print("saved", out)
