#!/usr/bin/env python3
"""analyze-port-scanner intro: Donner Pass in hard winter, scenery only, nothing readable. Near rail diagonal
from the lower corner with spikes and fishplates sharp, ballast grey stones between snow dusted sleepers, the
lower arc of the rotary housing entering the top of the foreground with snow packed between its blades, the plow
at work midground in a deep cut with sheer snow walls and its thrown plume drifting right, mileposts clear topped
in a receding row with faces turned away, cleared dark track behind running straight, white slopes to a ridge in
dust pale light, exhaust low over the train, unbroken drift ahead to the top of the frame."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
random.seed(67)
A = sys.argv[1] if len(sys.argv) > 1 else ""
W, H = 1200, 520
GREEN = (38, 84, 52); GREY = (128, 130, 126); RED = (196, 44, 40); DUST = (232, 228, 214)
img = Image.new("RGB", (W, H), (206, 210, 204)); d = ImageDraw.Draw(img, "RGBA")
# dust pale sky and ridge
d.rectangle([0, 0, W, 150], fill=(198, 204, 200))
d.polygon([(0, 150), (260, 88), (520, 132), (820, 76), (1200, 128), (1200, 190), (0, 190)], fill=(222, 224, 218))
d.polygon([(0, 168), (320, 112), (700, 150), (1200, 118), (1200, 200), (0, 200)], fill=(234, 235, 230))
# snow field
d.rectangle([0, 190, W, H], fill=(238, 239, 235))
# the cut: sheer snow walls either side of the line running to the right horizon
d.polygon([(430, 236), (1200, 236), (1200, 300), (470, 330)], fill=(248, 249, 246))  # far wall face
d.polygon([(430, 236), (1200, 236), (1200, 252), (470, 272)], fill=(214, 218, 212))  # far wall top edge shadow
d.polygon([(0, 470), (560, 330), (1200, 330), (1200, H), (0, H)], fill=(246, 247, 243))  # near wall mass
d.polygon([(0, 470), (560, 330), (700, 330), (80, 486)], fill=(226, 229, 223))  # near wall face shading
# cleared dark track behind the train, running straight from left to the plow
d.polygon([(0, 356), (520, 318), (560, 344), (0, 402)], fill=(52, 50, 46))
for x in range(8, 540, 34):  # sleepers on the cleared stretch
    t = x / 540; y = 372 - t * 42
    d.line([(x, y + 14), (x + 26, y + 8)], fill=(86, 78, 66), width=5)
d.line([(0, 362), (548, 322)], fill=(150, 152, 148), width=4)
d.line([(0, 394), (556, 340)], fill=(150, 152, 148), width=4)
# ahead of the plow the drift closes over the rails: unbroken snow to the top right
d.polygon([(860, 236), (1200, 236), (1200, 330), (900, 330)], fill=(250, 250, 247))
# mileposts in a receding row, faces turned away (backs only, nothing to read)
for (x, y, s) in [(640, 262, 1.0), (760, 252, .82), (880, 246, .66), (990, 241, .54)]:
    d.rectangle([x, y, x + 10 * s, y + 52 * s], fill=GREY)
    d.rectangle([x - 3 * s, y - 12 * s, x + 13 * s, y], fill=(104, 106, 102))  # back of the face plate
    d.rectangle([x - 3 * s, y - 16 * s, x + 13 * s, y - 12 * s], fill=(250, 250, 247))  # tops clear of the drifts
# exhaust hanging low over the train
for (x, y, r) in [(300, 236, 60), (390, 222, 76), (480, 232, 54)]:
    d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(120, 122, 118, 70))
# the plow at work midground: housing, rotor ring, locomotive bulk behind, plume thrown right
px, py = 600, 300
d.rectangle([330, 238, 520, 318], fill=GREEN)  # locomotive bulk pushing, diesel green
d.rectangle([330, 238, 520, 256], fill=(30, 66, 42))
d.rectangle([452, 206, 486, 240], fill=(44, 46, 44))  # exhaust stack
d.ellipse([px - 88, py - 88, px + 88, py + 88], fill=GREEN, outline=(24, 54, 34), width=5)  # circular housing
for i in range(9):  # rotor blades around a dark hub, snow packed unevenly
    a = math.radians(i * 40 + 12); x1, y1 = px + math.cos(a) * 22, py + math.sin(a) * 22; x2, y2 = px + math.cos(a) * 74, py + math.sin(a) * 74
    d.line([(x1, y1), (x2, y2)], fill=GREY, width=15)
    d.line([(x1, y1), (x2, y2)], fill=RED, width=3)
for (a, ln) in [(150, 66), (190, 70), (230, 58)]:  # snow wedged thick at the lower left
    r = math.radians(a); x, y = px + math.cos(r) * ln, py + math.sin(r) * ln
    d.ellipse([x - 13, y - 9, x + 13, y + 9], fill=(252, 252, 249))
d.ellipse([px - 20, py - 20, px + 20, py + 20], fill=(26, 28, 26))
d.rectangle([px - 8, py - 116, px + 8, py - 88], fill=(44, 46, 44))  # headlamp bracket, lamp unlit
d.ellipse([px - 13, py - 138, px + 13, py - 112], fill=(196, 186, 160), outline=(44, 46, 44), width=3)
for i in range(26):  # the thrown plume rising and drifting rightward
    t = i / 26; x = px + 90 + t * 330 + random.uniform(-9, 9); y = py - 60 - math.sin(t * 2.6) * 92 + t * 66
    r = random.uniform(5, 15); d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(250, 250, 247, 205))
# foreground: near rail diagonal out of the lower corner, spikes, fishplates, ballast between dusted sleepers
d.polygon([(0, 520), (330, 388), (392, 388), (90, 520)], fill=(238, 239, 235))
for i in range(6):
    t = i / 6; x = 30 + t * 300; y = 500 - t * 96; wdt = 120 - t * 62
    d.line([(x - wdt // 2, y), (x + wdt // 2, y - 12)], fill=(96, 88, 76), width=8)  # sleeper
    for _ in range(6):  # ballast grey stones
        bx, by = x + random.uniform(-wdt / 2, wdt / 2), y + random.uniform(-4, 10)
        d.ellipse([bx - 5, by - 3, bx + 5, by + 3], fill=GREY)
d.line([(24, 506), (344, 392)], fill=(158, 160, 156), width=7)  # the near rail itself, bare steel
d.line([(70, 520), (392, 404)], fill=(140, 142, 138), width=5)
for (x, y) in [(120, 478), (214, 444), (300, 416)]:  # spikes and a fishplate, sharp
    d.rectangle([x - 5, y - 5, x + 5, y + 5], fill=(70, 70, 68))
d.rectangle([238, 428, 286, 442], fill=(104, 106, 102), outline=(70, 70, 68), width=2)
for (x, y) in [(248, 435), (276, 435)]:
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(52, 52, 50))
if A != "--v1":  # v1 flaw: rotary housing arc absent from the top of the foreground, the machine never enters the near frame
    # lower arc of the rotary housing entering shallowly across the top of the foreground, packed snow between blades
    d.arc([-100, -560, 500, 40], 52, 128, fill=GREEN, width=38)
    for a in range(62, 122, 15):
        r = math.radians(a); x, y = 200 + math.cos(r) * 282, -260 + math.sin(r) * 282
        d.line([(200 + math.cos(r) * 252, -260 + math.sin(r) * 252), (x, y)], fill=GREY, width=10)
        d.ellipse([x - 13, y - 8, x + 13, y + 8], fill=(252, 252, 249))
if A == "--v2":  # v2 flaw: figures painted on the nearest milepost back, a readable mark in a frame that allows none
    d.rectangle([630, 238, 662, 254], fill=DUST); d.line([(634, 250), (658, 250)], fill=(30, 30, 30), width=3); d.line([(646, 242), (646, 250)], fill=(30, 30, 30), width=3)
# long late afternoon shadows from posts and rails
for (x, y, ln) in [(640, 314, 90), (760, 300, 70), (880, 288, 54)]:
    d.line([(x + 8, y), (x + 8 + ln, y + 12)], fill=(206, 209, 203), width=6)
img = img.filter(ImageFilter.GaussianBlur(0.5))
out = {"--v1": "scratch/intro-v1.png", "--v2": "scratch/intro-v2.png"}.get(A, "intro-banner.png")
img.save(__file__.rsplit("/", 1)[0] + "/" + out); print("saved", out)
