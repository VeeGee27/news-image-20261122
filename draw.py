#!/usr/bin/env python3
"""draw.py — renders the news-image-20261122 v2 front page (1024x1024).

A dense serif newspaper front page summing up Sunday 22 November 2026:
39 dated stories across 8 regions, 3 heroes, 13 illustrated mids,
23 briefs in 3 columns, a numbered world map, a red DATE CHECK box,
and a stat strip. Warm newsprint paper, fibre speckles, vignette.

Deterministic: seeded RNG only; two runs produce a byte-identical PNG.
Run:  python3 draw.py   (writes entry.png next to this file)
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
PAGE = (243, 238, 225)      # warm newsprint cream
CARD = (252, 249, 240)      # lighter cream cards
INK = (30, 28, 24)
RED = (178, 34, 34)
DARKRED = (120, 20, 20)
GREY = (110, 104, 92)
LINE = (200, 192, 175)
NAVY = (28, 42, 66)
GOLD = (198, 154, 40)
SKY = (135, 180, 210)
SEA = (150, 190, 205)
SUBHEAD = (64, 58, 48)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


# ---------------------------------------------------------------- text helpers
def wrap(d, text, font, maxw):  # pixel-width greedy wrap
    """Split text into lines that fit maxw pixels, greedy left to right."""
    out, cur = [], ""
    for word in text.split():
        nxt = word if cur == "" else cur + " " + word
        if cur == "" or d.textlength(nxt, font=font) <= maxw:
            cur = nxt
        else:  # word would overflow: close this line, start a new one
            out.append(cur)
            cur = word
    if cur != "":
        out.append(cur)
    return out


def fit_headline(d, text, path, size, maxw, maxlines, min_size=9):
    """Largest size (<= size, >= min_size) wrapping to <= maxlines lines."""
    for s in range(size, min_size - 1, -1):
        fh = F(path, s)
        got = wrap(d, text, fh, maxw)
        if len(got) <= maxlines:
            return fh, got
    fh = F(path, min_size)
    return fh, wrap(d, text, fh, maxw)


def text_lines(d, x, y, lines, font, fill, lh):  # draw lines, return y after last
    """Draw each line, stepping down lh; return the y after the last line."""
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def card(d, box, fill=CARD, outline=LINE, width=1):  # flat filled card
    """A flat card: filled rectangle with a thin outline."""
    d.rectangle(box, fill=fill, outline=outline, width=width)  # card face


def badge(d, x, y, n, r=8, font=None):  # red numbered disc
    """Red disc, white number, centred on (x, y)."""
    disc = [x - r, y - r, x + r, y + r]
    d.ellipse(disc, fill=RED, outline=(255, 255, 255), width=1)
    bf = font or F("DejaVuSans-Bold.ttf", 9 if n < 10 else 8)
    num = str(n)
    tw = d.textlength(num, font=bf)
    th = bf.getbbox(num)[3] - bf.getbbox(num)[1]
    d.text((x - tw / 2, y - th / 2 - 1), num, font=bf, fill=(255, 255, 255))


def badge_pill(d, x, y, nums):
    """Red pill listing the story numbers that share one dot."""
    pf = F("DejaVuSans-Bold.ttf", 7)
    label = "·".join(str(n) for n in nums)
    tw = d.textlength(label, font=pf)
    w = 8 + tw
    h = 8
    d.rounded_rectangle([x - w / 2, y - h, x + w / 2, y + h], radius=h, fill=RED, outline=(255, 255, 255), width=1)
    d.text((x - tw / 2, y - 5), label, font=pf, fill=(255, 255, 255))


def tagline(d, x, y, tag, source, maxw):  # red tag + grey source
    """Red bold tag, then grey '— source' right after it."""
    fb = F("DejaVuSans-Bold.ttf", 8)
    d.text((x, y), tag, font=fb, fill=RED)
    wtag = d.textlength(tag, font=fb)
    fr = F("DejaVuSans.ttf", 8)
    d.text((x + wtag + 4, y), "— " + source, font=fr, fill=GREY)


# ---------------------------------------------------------------- page base
def make_paper():  # warm newsprint base: speckles + vignette, seeded
    """Blank 1024x1024 newsprint page, fibre-speckled and vignetted."""
    base = Image.new("RGB", (W, H), PAGE)
    pen = ImageDraw.Draw(base)
    rng = random.Random(20261122)  # fixed seed, so runs are identical
    for _ in range(5000):  # fibre speckles
        sx, sy = rng.randint(0, W - 1), rng.randint(0, H - 1)
        sv = rng.randint(-5, 5)
        pen.point((sx, sy), fill=(PAGE[0] + sv, PAGE[1] + sv, PAGE[2] + sv))
    mask = Image.new("L", (128, 128), 0)
    md = ImageDraw.Draw(mask)
    for r in range(64, 0, -1):  # concentric rings, outer to inner
        alpha = int(26 * (1 - r / 64.0) ** 2)
        md.ellipse([64 - r, 64 - r, 64 + r, 64 + r], fill=alpha)
    mask = mask.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(8))
    dark = Image.new("RGB", (W, H), (60, 50, 38))  # vignette tint
    return Image.composite(dark, base, mask)


# ---------------------------------------------------------------- nameplate
def draw_masthead(d):  # nameplate, date, headline strip, rule
    """Masthead: red kicker, big serif date, three-headline strip, rule."""
    d.text((16, 18), "THE WORLD IN ONE DAY",
           font=F("DejaVuSans-Bold.ttf", 12), fill=RED)
    d.text((16, 36), "Sunday 22 November 2026",
           font=F("DejaVuSerif-Bold.ttf", 40), fill=INK)
    d.text((16, 84), "COP31 collapses  ·  186 drones over Ukraine  ·  "
           "Trump and Zelenskyy talk peace at Mar-a-Lago",
           font=F("DejaVuSerif.ttf", 14), fill=SUBHEAD)
    d.line([(16, 106), (1008, 106)], fill=INK, width=2)  # rule under masthead

# ---------------------------------------------------------------- map data
# LAND: lon/lat polygons, verified — every pin sits on true land.
# Two v2 additions: an Okinawa island polygon (Naha pin 15) and a
# widened New Zealand vertex so the Wellington pin 16 sits on land.
LAND = [
    # North America coast
    [[-168, 66], [-150, 70], [-135, 69], [-125, 71], [-115, 73], [-105, 74],
     [-95, 80], [-85, 80], [-80, 73], [-70, 62], [-60, 55], [-55, 52],
     [-60, 47], [-65, 44], [-70, 42], [-75, 38], [-76, 35], [-80, 32],
     [-81, 30], [-80, 28], [-79.8, 26], [-80.5, 25.5], [-82, 27], [-83, 29],
     [-85, 29], [-90, 21], [-94, 17], [-97, 16], [-92, 14],
     [-87, 13], [-83, 9], [-79, 8], [-82, 9], [-86, 12], [-90, 14],
     [-95, 16], [-100, 18], [-105, 20], [-110, 23], [-114, 28], [-120, 34],
     [-124, 40], [-124, 48], [-130, 55], [-140, 60], [-150, 59], [-158, 58],
     [-165, 60], [-168, 66]],
    # Greenland island
    [[-55, 60], [-45, 60], [-40, 64], [-32, 68], [-25, 70], [-20, 74],
     [-30, 78], [-45, 80], [-55, 78], [-58, 72], [-58, 66], [-55, 60]],
    # South America coast
    [[-80, 9], [-77, 8], [-75, 11], [-72, 12], [-68, 11], [-62, 10],
     [-60, 8], [-55, 6], [-52, 4], [-50, 0], [-44, -3], [-38, -5],
     [-35, -8], [-37, -13], [-39, -18], [-41, -23], [-48, -27], [-53, -33],
     [-58, -38], [-62, -41], [-66, -46], [-68, -52], [-71, -54], [-74, -50],
     [-73, -44], [-72, -37], [-71, -30], [-70, -22], [-75, -15], [-79, -8],
     [-81, -5], [-80, 9]],
    # Europe mainland
    [[-10, 36], [-9, 38], [-9, 43], [-4, 44], [-1, 46], [2, 47], [3, 50],
     [5, 53], [8, 55], [8, 57], [10, 59], [13, 56], [18, 56], [21, 55],
     [24, 58], [27, 60], [30, 62], [28, 65], [25, 69], [20, 70], [16, 68],
     [12, 65], [10, 62], [5, 60], [5, 57], [8, 54], [10, 52], [6, 50],
     [2, 49], [-1, 48], [-4, 44], [-9, 43], [-10, 36]],
    # UK islands
    [[-5, 50], [-3, 53], [-5, 56], [-3, 58], [-1, 57], [0, 53], [-2, 51], [-5, 50]],
    # Africa coast
    [[-6, 35], [-10, 31], [-15, 27], [-17, 21], [-17, 15], [-15, 12],
     [-12, 8], [-8, 5], [-4, 5], [0, 6], [6, 4], [9, 4], [12, 0], [13, -5],
     [12, -10], [13, -17], [15, -22], [17, -29], [20, -35], [26, -34],
     [32, -28], [35, -24], [40, -18], [40, -12], [42, -5], [46, 0], [51, 2],
     [51, 11], [48, 11], [44, 13], [43, 12], [40, 15], [38, 18], [36, 22],
     [34, 27], [32, 31], [30, 32], [25, 32], [20, 32], [15, 32], [11, 34],
     [10, 37], [5, 37], [0, 36], [-6, 35]],
    # Asia mainland
    [[30, 36], [35, 36], [35.5, 33], [34.8, 32], [34.4, 31.5], [36, 31],
     [38, 31], [42, 29], [46, 29],
     [48, 30], [52, 28], [54, 27], [57, 26], [60, 25], [62, 25], [66, 25],
     [68, 23], [70, 20], [73, 20], [76, 15], [77, 8], [80, 7], [80, 10],
     [83, 17], [86, 20], [89, 22], [91, 22], [93, 18], [95, 16], [98, 10],
     [100, 8], [103, 5], [104, 2], [105, 9], [108, 11], [109, 15], [109, 20],
     [106, 20], [105, 23], [108, 22], [110, 21], [113, 22], [116, 23],
     [118, 25], [120, 28], [122, 30], [121, 33], [120, 35], [122, 37],
     [124, 39], [126, 38], [126, 36], [128, 35], [129, 37], [129, 39],
     [127, 40], [130, 42], [132, 43], [135, 44], [138, 46],
     [140, 48], [142, 50], [141, 53], [140, 56], [138, 59], [136, 60],
     [140, 60], [142, 59], [145, 60], [150, 60], [156, 60], [158, 56],
     [160, 55], [162, 58], [163, 60], [162, 62], [158, 64], [155, 66],
     [150, 68], [145, 70], [140, 71], [135, 72], [130, 72], [125, 73],
     [120, 73], [115, 73], [110, 74], [105, 75], [100, 76], [95, 76],
     [90, 75], [85, 75], [80, 73], [75, 72], [70, 72], [65, 70], [60, 69],
     [55, 68], [50, 68], [45, 68], [40, 68], [35, 67], [32, 66], [30, 64],
     [28, 62], [25, 60], [22, 58], [20, 55], [18, 54], [15, 52], [12, 50],
     [10, 48], [8, 46], [6, 44], [3, 42], [0, 40], [5, 38], [10, 37],
     [15, 38], [20, 40], [23, 40], [26, 38], [28, 36], [30, 36]],
    # Australia coast
    [[113, -22], [114, -30], [115, -34], [118, -35], [124, -33], [129, -32],
     [132, -32], [135, -35], [138, -35], [140, -38], [145, -38], [150, -37],
     [153, -32], [153, -27], [151, -24], [146, -19], [142, -15], [142, -11],
     [137, -12], [135, -15], [132, -12], [130, -13], [126, -14], [122, -17],
     [118, -20], [113, -22]],
    # Sumatra island
    [[95, 5], [98, 3], [101, 1], [104, -2], [106, -5], [105, -6],
     [102, -3], [99, 0], [96, 3], [95, 5]],
    # Java — Cikande pin (106.4, -6.2) on its north coast
    [[105, -5.5], [109, -6], [113, -7], [114, -7.5], [114, -8.5],
     [110, -8], [106, -6.5], [105, -5.5]],
    # Borneo island
    [[109, 1], [112, 4], [116, 6], [118, 2], [117, -2], [114, -4],
     [110, -3], [109, 0], [109, 1]],
    # Sulawesi island
    [[119, 0], [121, 1], [123, -1], [121, -3], [120, -5], [119, -3], [119, 0]],
    # New Guinea island
    [[131, -1], [135, -2], [138, -3], [141, -3], [141, -8], [138, -8],
     [135, -6], [132, -4], [131, -1]],
    # Japan — Honshu-Hokkaido-Kyushu chain
    [[130, 31], [132, 33], [134, 34], [136, 35], [138, 35], [140, 37],
     [141, 39], [141, 41], [143, 42], [145, 44], [143, 44], [141, 42],
     [140, 39], [139, 37], [136, 34], [133, 34], [131, 32], [130, 31]],
    # Okinawa (NEW v2 — Naha pin 15 sits on it)
    [[127.5, 26.0], [128.0, 26.05], [128.3, 26.5], [128.2, 26.9],
     [127.7, 26.8], [127.4, 26.4], [127.5, 26.0]],
    # Arabian Peninsula — Riyadh, Doha, Bahrain pins on it
    [[39, 28], [39, 23], [41, 19], [43, 15], [45, 13], [48, 14], [51, 16],
     [54, 17], [56, 20], [58, 23], [59, 25], [57, 26], [55, 27], [53, 28],
     [51, 29], [49, 30], [45, 30], [42, 30], [39, 28]],
    # Taiwan island
    [[120, 25.5], [122, 25.5], [122, 22], [120, 22]],
    # Philippines islands
    [[120, 18], [122, 16], [122, 13], [124, 11], [123, 9], [121, 10],
     [120, 13], [120, 18]],
    # New Zealand (v2: vertex widened to 175.0,-41.6 so Wellington sits on land)
    [[167, -45], [170, -42], [173, -41], [175, -38], [178, -38], [176, -40],
     [175.0, -41.6], [171, -44], [167, -45]],
]  # land polygons

# Map region labels: (name, lon, lat) anchor for the small-caps label.
REGION_TAGS = [
    ("NORTH AMERICA", -130, 30),
    ("SOUTH AMERICA", -35, -25),
    ("EUROPE", -35, 62),
    ("AFRICA", -25, 5),
    ("ASIA", 75, -25),
    ("OCEANIA", 115, -44),
]  # region labels

# PINS: (story numbers sharing one dot, lon, lat, badge dx, badge dy).
# v1 pins renumbered for the brief shift (14-36 -> 17-39); 3 new mids
# 14 Barcelona, 15 Naha, 16 Wellington appended. Global stories 13 and
# 39 have no dot (see map footnote).
PINS = [
    ((1, 33), 30.7, 36.9, 13, 13),  # Antalya
    ((2, 21), 30.5, 50.45, 0, -10),  # Kyiv
    ((3,), -80.03, 26.7, -10, 10),  # Mar-a-Lago, Florida
    ((4,), 50.6, 26.2, 13, -13),  # Bahrain
    ((5,), 106.4, -6.2, 0, -10),  # Cikande, Java
    ((6,), 26.0, 59.8, 0, -16),  # Gulf of Finland ship
    ((7, 34), -74.0, 40.7, 0, -10),  # New York
    ((8, 23), -77.0, 38.9, 10, 10),  # Washington DC
    ((9,), 151.2, -33.9, 0, -10),  # Sydney
    ((10,), 46.7, 24.7, 16, 0),  # Riyadh
    ((11,), 149.1, -35.3, 10, 10),  # Canberra
    ((12,), 35.2, 32.0, -13, 13),  # West Bank
    ((14,), 2.17, 41.39, 0, -10),  # Barcelona
    ((15,), 127.7, 26.2, 14, -6),  # Naha, Okinawa
    ((16,), 174.8, -41.3, 0, -10),  # Wellington
    ((17, 31, 35), 34.45, 31.5, 0, -10),  # Gaza
    ((18,), 37.6, 55.75, 13, -13),  # Moscow
    ((19,), 30.7, 46.5, -24, 24),  # Odesa
    ((20,), 36.2, 50.0, -28, -28),  # Kharkiv
    ((22,), 24.0, 49.8, -20, 0),  # Lviv
    ((24,), -75.7, 45.4, -13, 13),  # Ottawa
    ((25,), 121.6, 25.0, 0, -10),  # Taipei
    ((26,), -115.1, 36.2, 0, -10),  # Las Vegas
    ((27,), 33.8, -13.97, 0, -10),  # Lilongwe
    ((28,), 32.5, 15.6, -13, 13),  # Khartoum
    ((29,), 93.9, 24.8, 0, -10),  # Imphal
    ((30,), 34.9, 31.8, 24, 24),  # Israel figurines
    ((32,), 11.1, 46.85, -20, 20),  # Gurgl
    ((36,), 45.3, 2.05, 10, 10),  # Mogadishu
    ((37,), 51.5, 25.3, -16, 16),  # Doha
    ((38,), 127.0, 37.5, 0, -10),  # Seoul
]  # pins

# ---------------------------------------------------------------- story data
HEROES = [
    {"n": 1, "head": "COP31 COLLAPSES",
     "deck": "EU and UK reject a pact with no mention of fossil fuels; the longest climate summit ever ends with no deal at all.",
     "tag": "CONFIRMED", "src": "BBC · Reuters", "art": "cop31"},
    {"n": 2, "head": "186 DRONES OVER UKRAINE",
     "deck": "Russia fires 186 drones overnight; Ukraine downs 161, but strikes hit 18 sites and a block of flats near Kyiv.",
     "tag": "CONFIRMED", "src": "Ukrainian Air Force", "art": "drones"},
    {"n": 3, "head": "PEACE TALKS AT MAR-A-LAGO",
     "deck": "Trump hosts Zelenskyy; 20-point plan \"90% agreed\", US guarantees \"100% agreed\" — Donbas still blocks a deal.",
     "tag": "CONFIRMED", "src": "AP · News18", "art": "maralago"},
]  # heroes

MIDS = [
    {"n": 4, "head": "BAHRAIN HIT",
     "deck": "Two hurt as Iran strikes Bahrain; Tehran claims two US radars hit.",
     "tag": "REPORTED", "src": "Reuters", "art": "radar"},
    {"n": 5, "head": "FACTORY FIRE",
     "deck": "Candy plant blaze kills 3 in Cikande; 36 workers still missing.",
     "tag": "CONFIRMED", "src": "AP", "art": "factory"},
    {"n": 6, "head": "SHIP AFIRE IN BALTIC",
     "deck": "Russian ship hit by drones off Finland; war \"spilling over\".",
     "tag": "REPORTED", "src": "Euromaidan", "art": "ship"},
    {"n": 7, "head": "ANT ENDS WEEK DOWN",
     "deck": "Shares end the week at $88.91, above the $83 IPO price.",
     "tag": "CONFIRMED", "src": "CNBC", "art": "candles"},
    {"n": 8, "head": "NATO-STYLE GUARANTEES",
     "deck": "US floats Article 5-style cover for Kyiv; Kushner: Trump \"open\".",
     "tag": "REPORTED", "src": "Politico", "art": "shield"},
    {"n": 9, "head": "ASIA POWER SHIFTS",
     "deck": "Lowy: US lead over China smallest since 2018, 78.9 to 73.6.",
     "tag": "CONFIRMED", "src": "Lowy Institute", "art": "bars"},
    {"n": 10, "head": "SAUDI SLIDES",
     "deck": "Tadawul closes below 10,000, down 1.95% on Sunday.",
     "tag": "CONFIRMED", "src": "JBizNews", "art": "slide"},
    {"n": 11, "head": "AUKUS ROW",
     "deck": "Australia rejects a US warning on submarine sales.",
     "tag": "CONFIRMED", "src": "Reuters", "art": "sub"},
    {"n": 12, "head": "EISENKOT CONDEMNS ARSON",
     "deck": "Eisenkot condemns settler arson attacks on West Bank villages.",
     "tag": "CONFIRMED", "src": "Reuters", "art": "noflame"},
    {"n": 13, "head": "MERCURY ORBIT",
     "deck": "ESA confirms BepiColombo in Mercury orbit after 8 years in space.",
     "tag": "CONFIRMED", "src": "ESA", "art": "mercury"},
    {"n": 14, "head": "BARCA COMEBACK",
     "deck": "Barcelona fight back with three second-half goals to beat Villarreal 3-2 at Camp Nou.",
     "tag": "CONFIRMED", "src": "LaLiga", "art": "football"},
    {"n": 15, "head": "SHURI CASTLE REBORN",
     "deck": "Okinawa celebrates the restored main hall of Shuri Castle, seven years after fire destroyed it.",
     "tag": "CONFIRMED", "src": "AP", "art": "castle"},
    {"n": 16, "head": "INDIA'S RECORD 720/9",
     "deck": "Rahul 136, Pant 128 power India to declare at 720/9, the highest Test total ever on New Zealand soil.",
     "tag": "CONFIRMED", "src": "IANS", "art": "cricket"},
]  # mids

# briefs: (number, location, deck, source)
BRIEFS = [
    (17, "GAZA", "Israeli strikes kill 4 despite the ceasefire; toll reaches 74,736.", "Gaza Health Ministry"),
    (18, "MOSCOW", "Russia says it downed 170 Ukrainian drones overnight.", "QNA"),
    (19, "ODESA", "Power grid strained after overnight strikes; city short of power.", "Euromaidan"),
    (20, "KHARKIV", "Drones set a house, a shop and a business ablaze.", "Euromaidan"),
    (21, "KYIV", "Russia fired 2,700 drones, 1,460 bombs and 165 missiles this week.", "Zelenskyy"),
    (22, "LVIV", "Dashcam catches a Russian projectile hitting a building.", "Euronews"),
    (23, "WASHINGTON", "Schumer faces a leadership challenge; secret vote on Dec 1.", "Reuters"),
    (24, "OTTAWA", "Hegseth limits US military ties with Canada.", "Washington Post"),
    (25, "TAIPEI", "Stocks fall 17% in the week, worst since 1990.", "Market Data"),
    (26, "LAS VEGAS", "Verstappen wins wild GP after 35 lead changes; Norris 2nd.", "Reuters"),
    (27, "LILONGWE", "Malawi tightens border screening to keep Ebola out.", "Malawi Health Ministry"),
    (28, "KHARTOUM", "Drones damage UN and residential buildings in the capital.", "Reports"),
    (29, "IMPHAL", "Tainted alcohol kills 11, puts 180 in hospital in Manipur.", "Reports"),
    (30, "ISRAEL", "15,000-year-old clay figurines found, earliest in SW Asia.", "Researchers"),
    (31, "GAZA", "Aid groups score the Trump-backed peace plan 4 of 26.", "Analysis"),
    (32, "GURGL", "Haugan wins slalom as Norway takes top two.", "Reuters"),
    (33, "ANTALYA", "The 35% clean-electricity goal dies with the COP31 pact.", "BBC"),
    (34, "NEW YORK", "Anthropic sits on $244.6bn cash after its record IPO.", "Filings"),
    (35, "GAZA", "Peace board warns Israel: progress, or the UN takes the keys.", "Board of Peace"),
    (36, "MOGADISHU", "Somalia breaks ground on naval facilities with Turkey.", "Defence Ministry"),
    (37, "DOHA", "Chile fight back to beat Algeria 4-2 at the U-17 World Cup.", "Qatar Tribune"),
    (38, "SEOUL", "Education minister quits over the exam cheating scandal.", "WH News"),
    (39, "GLOBAL", "Bitcoin breaks below $60,000 in the AI rout.", "Market Data"),
]  # briefs

STATS = [
    ("161", "drones downed overnight"),
    ("$244.6BN", "Anthropic's cash after IPO"),
    ("-10%", "Nasdaq's worst week since 2020"),
    ("10BN km", "travelled to Mercury"),
    ("78.9", "US Asia-power score"),
    ("720/9", "India's record Test total in NZ"),
]  # stat strip

# region name, count, colour (order = bar order)
REGIONS = [
    ("Europe", 10, (70, 110, 180)),
    ("N. America", 6, (178, 60, 60)),
    ("Middle East", 7, (200, 140, 40)),
    ("Asia", 6, (60, 140, 90)),
    ("Africa", 3, (150, 100, 160)),
    ("Oceania", 2, (60, 160, 170)),
    ("S. America", 1, (200, 100, 140)),
    ("Global", 4, (120, 120, 120)),
]  # regions

DATECHECK = [
    "Shenzhen Trump–Xi–Putin summit (Thu 19 Nov)",
    "ICJ: Myanmar guilty of Rohingya genocide (Thu 19 Nov)",
    "El Chapo Isidro captured in Sinaloa (Sat 21 Nov)",
    "FBI crime database + USDA hacked (Sat 21 Nov)",
    "EU–Indonesia trade deal (Sat 21 Nov)",
    "Friday rout: S&P -3.7%, Nasdaq -5.3% (Fri 20 Nov)",
    "Peru 6.7 quake, 1 dead (Fri 20 Nov)",
    "Kryvyi Rih missile strike, 2 killed (Sat 21 Nov)",
]  # date check

# ---------------------------------------------------------------- illustrations
# Every art function draws inside the box (x0, y0, x1, y1) and never
# touches text — the strips sit below the tag line with a clear gap.

def art_cop31(d, x0, y0, x1, y1):
    # Summit table with three flags and a cracked pact document.
    d.rectangle([x0, y0, x1, y1], fill=(214, 206, 188))
    d.rectangle([x0, y1 - 10, x1, y1], fill=(120, 88, 60))  # table
    # flags: EU blue, UK red/white, green
    for i, col in enumerate([(40, 70, 150), (180, 40, 40), (40, 130, 80)]):
        fx = x0 + 14 + i * 34
        d.line([(fx, y0 + 6), (fx, y1 - 10)], fill=(60, 50, 40), width=2)
        d.polygon([(fx, y0 + 6), (fx + 22, y0 + 10), (fx, y0 + 15)], fill=col)
    # white document, centre-right, with a red jagged crack
    dx0, dy0, dx1, dy1 = x1 - 118, y0 + 6, x1 - 22, y1 - 12
    d.rectangle([dx0, dy0, dx1, dy1], fill=(255, 255, 255), outline=(150, 140, 120))
    for yy in range(dy0 + 6, dy1 - 4, 5):
        d.line([(dx0 + 8, yy), (dx0 + 58, yy)], fill=(170, 160, 140), width=1)
    crack = [(dx0 + 30, dy0), (dx0 + 42, dy0 + 8), (dx0 + 30, dy0 + 16),
             (dx0 + 44, dy0 + 24), (dx0 + 32, dy1)]
    d.line(crack, fill=RED, width=2)
    d.text((dx1 + 4, y0 + 12), "✕", font=F("DejaVuSans-Bold.ttf", 16), fill=RED)


def art_drones(d, x0, y0, x1, y1):
    # Night sky, stars, three drone trails and orange bursts.
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    rng = random.Random(7)
    for _ in range(26):
        sx = rng.randint(x0 + 3, x1 - 3)
        sy = rng.randint(y0 + 2, y1 - 12)
        d.point((sx, sy), fill=(255, 255, 220))
    for i, ty in enumerate((y0 + 10, y0 + 20, y0 + 30)):
        tx = x0 + 20 + i * 78
        d.line([(tx, ty), (tx + 52, ty + 6)], fill=(255, 210, 90), width=2)
        d.ellipse([tx + 52 - 3, ty + 3, tx + 52 + 3, ty + 9], fill=(255, 120, 40))
        for a in range(0, 360, 45):
            import math
            ex = tx + 58 + int(7 * math.cos(math.radians(a)))
            ey = ty + 8 + int(7 * math.sin(math.radians(a)))
            d.line([(tx + 58, ty + 8), (ex, ey)], fill=(255, 150, 50), width=1)
        d.rectangle([tx + 44, ty + 2, tx + 52, ty + 8], fill=(200, 200, 200))


def art_maralago(d, x0, y0, x1, y1):
    # White mansion with pediment and columns, palms, flag.
    d.rectangle([x0, y0, x1, y1], fill=(196, 222, 235))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(90, 140, 80))  # lawn
    mx0, mx1 = x0 + 78, x1 - 78
    d.rectangle([mx0, y0 + 18, mx1, y1 - 8], fill=(250, 246, 236),
                outline=(180, 170, 150))
    d.polygon([(mx0 - 6, y0 + 18), ((mx0 + mx1) // 2, y0 + 4), (mx1 + 6, y0 + 18)],
              fill=(200, 60, 60))
    for cx in range(mx0 + 16, mx1 - 8, 26):
        d.rectangle([cx, y0 + 24, cx + 6, y1 - 8], fill=(220, 210, 190))
    d.line([((mx0 + mx1) // 2, y0 + 4), ((mx0 + mx1) // 2, y0 - 2)],
           fill=(60, 50, 40), width=2)
    d.polygon([((mx0 + mx1) // 2, y0 - 2), ((mx0 + mx1) // 2 + 16, y0 + 2),
               ((mx0 + mx1) // 2, y0 + 6)], fill=(180, 40, 40))
    for px in (x0 + 22, x1 - 34):
        d.line([(px + 8, y1 - 8), (px + 8, y0 + 14)], fill=(90, 70, 40), width=3)
        for dx, dy in ((-10, 4), (10, 4), (-8, -2), (8, -2), (0, -6)):
            d.line([(px + 8, y0 + 14), (px + 8 + dx, y0 + 14 + dy)],
                   fill=(40, 130, 70), width=2)


def art_radar(d, x0, y0, x1, y1):
    # Radar dish sweeping, red burst above.
    cx, cy = x0 + 34, y1 - 4
    d.pieslice([cx - 22, cy - 20, cx + 22, cy + 20], 200, 340, fill=(90, 110, 150))
    d.line([(cx, cy), (cx + 20, cy - 18)], fill=(60, 70, 90), width=2)
    d.line([(cx - 4, y1 - 2), (cx + 4, y1 - 2)], fill=(60, 70, 90), width=2)
    bx, by = x1 - 22, y0 + 6
    for a in range(0, 360, 45):
        import math
        ex = bx + int(9 * math.cos(math.radians(a)))
        ey = by + int(9 * math.sin(math.radians(a)))
        d.line([(bx, by), (ex, ey)], fill=(255, 120, 40), width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)


def art_factory(d, x0, y0, x1, y1):
    # Factory with sawtooth roof, chimney and flames.
    d.rectangle([x0 + 8, y1 - 12, x1 - 8, y1 - 2], fill=(120, 110, 100))
    d.polygon([(x0 + 8, y1 - 12), (x0 + 22, y1 - 20), (x0 + 36, y1 - 12),
               (x0 + 50, y1 - 20), (x0 + 64, y1 - 12), (x0 + 78, y1 - 20),
               (x1 - 8, y1 - 12)], fill=(100, 90, 80))
    d.rectangle([x1 - 22, y0 + 2, x1 - 16, y1 - 12], fill=(90, 80, 70))
    for fx, fh in ((x0 + 18, 9), (x0 + 34, 12), (x0 + 52, 8)):
        d.polygon([(fx - 5, y1 - 12), (fx, y1 - 12 - fh), (fx + 5, y1 - 12)],
                  fill=(255, 140, 30))
    d.ellipse([x1 - 26, y0 - 2, x1 - 18, y0 + 6], fill=(180, 180, 180))
    d.ellipse([x1 - 30, y0 - 6, x1 - 22, y0 + 2], fill=(200, 200, 200))


def art_ship(d, x0, y0, x1, y1):
    # Cargo ship on waves, smoke curling from the stack.
    d.rectangle([x0, y1 - 6, x1, y1], fill=SEA)
    d.line([(x0 + 4, y1 - 8), (x1 - 4, y1 - 8)], fill=(255, 255, 255), width=1)
    d.polygon([(x0 + 12, y1 - 8), (x1 - 12, y1 - 8), (x1 - 22, y1 - 14),
               (x0 + 22, y1 - 14)], fill=(60, 60, 70))
    d.rectangle([x0 + 40, y1 - 20, x0 + 62, y1 - 14], fill=(180, 60, 50))
    d.line([(x0 + 66, y1 - 14), (x0 + 66, y1 - 22)], fill=(50, 50, 60), width=2)
    d.ellipse([x0 + 62, y0 + 1, x0 + 70, y0 + 8], fill=(170, 170, 170))
    d.ellipse([x0 + 68, y0 - 3, x0 + 76, y0 + 4], fill=(190, 190, 190))
    d.polygon([(x0 + 84, y1 - 16), (x0 + 90, y1 - 20), (x0 + 96, y1 - 16)],
              fill=(255, 140, 30))


def art_candles(d, x0, y0, x1, y1):
    # Four red candlesticks descending, red trend line, down arrow.
    base = y1 - 4
    for i, h in enumerate((14, 11, 8, 5)):
        cx = x0 + 14 + i * 22
        d.rectangle([cx - 4, base - h, cx + 4, base], fill=(200, 50, 50))
        d.line([(cx, base - h - 4), (cx, base - h)], fill=(200, 50, 50), width=1)
        d.line([(cx, base), (cx, base + 2)], fill=(200, 50, 50), width=1)
    d.line([(x0 + 10, y0 + 3), (x1 - 14, y1 - 6)], fill=RED, width=2)
    d.polygon([(x1 - 14, y1 - 6), (x1 - 22, y1 - 8), (x1 - 16, y1 - 2)], fill=RED)


def art_shield(d, x0, y0, x1, y1):
    # Navy shield with a gold star.
    cx = (x0 + x1) // 2
    d.polygon([(cx - 16, y0 + 2), (cx + 16, y0 + 2), (cx + 16, y0 + 12),
               (cx, y1 - 2), (cx - 16, y0 + 12)], fill=(40, 70, 150),
              outline=(220, 180, 60), width=1)
    d.text((cx - 5, y0 + 4), "*", font=F("DejaVuSans-Bold.ttf", 14), fill=GOLD)


def art_bars(d, x0, y0, x1, y1):
    # Two bars: US tall blue, China rising red, with a shift arrow.
    d.rectangle([x0 + 18, y0 + 4, x0 + 34, y1 - 4], fill=(70, 110, 180))
    d.rectangle([x0 + 44, y0 + 9, x0 + 60, y1 - 4], fill=(200, 60, 60))
    d.line([(x0 + 66, y0 + 12), (x1 - 12, y0 + 5)], fill=GOLD, width=2)
    d.polygon([(x1 - 12, y0 + 5), (x1 - 20, y0 + 3), (x1 - 16, y0 + 10)], fill=GOLD)


def art_slide(d, x0, y0, x1, y1):
    # Red descending line over a small tower (Riyadh).
    d.line([(x0 + 8, y0 + 4), (x1 - 30, y1 - 6)], fill=RED, width=2)
    tx = x1 - 24
    d.rectangle([tx, y0 + 8, tx + 12, y1 - 2], fill=(90, 100, 120))
    d.polygon([(tx - 2, y0 + 8), (tx + 6, y0 + 1), (tx + 14, y0 + 8)], fill=(70, 80, 100))


def art_sub(d, x0, y0, x1, y1):
    # Submarine on waves.
    d.rectangle([x0, y1 - 6, x1, y1], fill=SEA)
    cx, cy = (x0 + x1) // 2, y0 + 10
    d.ellipse([cx - 34, cy - 5, cx + 34, cy + 5], fill=(70, 80, 90))
    d.rectangle([cx - 8, cy - 10, cx + 8, cy - 4], fill=(60, 70, 80))
    d.polygon([(cx + 34, cy), (cx + 44, cy - 4), (cx + 44, cy + 4)], fill=(60, 70, 80))
    for wx in range(x0 + 6, x1 - 6, 18):
        d.arc([wx, y1 - 8, wx + 12, y1 - 2], 180, 360, fill=(255, 255, 255), width=1)


def art_noflame(d, x0, y0, x1, y1):
    # Flame crossed out by a red prohibition circle.
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx - 6, cy + 6), (cx - 2, cy - 2), (cx + 2, cy - 6), (cx + 6, cy + 2),
               (cx + 3, cy + 6)], fill=(255, 140, 30))
    d.ellipse([cx - 11, cy - 10, cx + 11, cy + 10], outline=RED, width=2)
    d.line([(cx - 8, cy + 7), (cx + 8, cy - 7)], fill=RED, width=2)


def art_mercury(d, x0, y0, x1, y1):
    # Grey Mercury with craters, orbit ellipse, tiny spacecraft.
    cx, cy = x0 + 30, (y0 + y1) // 2
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(150, 140, 130),
              outline=(110, 100, 90))
    d.ellipse([cx - 4, cy - 5, cx - 1, cy - 2], fill=(110, 100, 90))
    d.ellipse([cx + 2, cy + 2, cx + 5, cy + 5], fill=(110, 100, 90))
    d.arc([x0 + 8, y0 + 1, x1 - 8, y1 - 1], 200, 340, fill=GREY, width=1)
    sx, sy = x1 - 22, y0 + 5
    d.rectangle([sx, sy, sx + 8, sy + 4], fill=(200, 200, 200))
    d.rectangle([sx - 6, sy + 1, sx, sy + 3], fill=(70, 110, 180))
    d.rectangle([sx + 8, sy + 1, sx + 14, sy + 3], fill=(70, 110, 180))


def art_football(d, x0, y0, x1, y1):
    # Goal posts and a football.
    d.line([(x0 + 8, y0 + 3), (x0 + 8, y1 - 3)], fill=(255, 255, 255), width=2)
    d.line([(x1 - 34, y0 + 3), (x1 - 34, y1 - 3)], fill=(255, 255, 255), width=2)
    d.line([(x0 + 8, y0 + 3), (x1 - 34, y0 + 3)], fill=(255, 255, 255), width=2)
    cx, cy = x1 - 16, (y0 + y1) // 2
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255),
              outline=(40, 40, 40))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(40, 40, 40))
    for dx, dy in ((-6, -4), (6, -4), (-6, 5), (6, 5)):
        d.point((cx + dx, cy + dy), fill=(40, 40, 40))


def art_castle(d, x0, y0, x1, y1):
    # Vermilion Shuri Castle main hall with a sweeping dark roof.
    cx = (x0 + x1) // 2
    d.polygon([(cx - 34, y0 + 8), (cx, y0 + 1), (cx + 34, y0 + 8),
               (cx + 28, y0 + 8), (cx, y0 + 4), (cx - 28, y0 + 8)],
              fill=(60, 50, 45))
    d.rectangle([cx - 26, y0 + 8, cx + 26, y1 - 2], fill=(178, 40, 40))
    d.rectangle([cx - 26, y0 + 8, cx + 26, y0 + 11], fill=(140, 30, 30))
    for wx in range(cx - 20, cx + 20, 12):
        d.rectangle([wx, y0 + 14, wx + 5, y1 - 6], fill=(120, 25, 25))
    d.rectangle([cx - 4, y1 - 8, cx + 4, y1 - 2], fill=(60, 40, 30))


def art_cricket(d, x0, y0, x1, y1):
    # Cricket bat, red ball, three stumps.
    d.line([(x0 + 20, y1 - 3), (x0 + 44, y0 + 4)], fill=(150, 110, 60), width=5)
    d.rectangle([x0 + 42, y0 + 2, x0 + 48, y0 + 8], fill=(120, 85, 45))
    cx, cy = x1 - 26, y0 + 7
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(190, 40, 40))
    for sx in range(x1 - 52, x1 - 40, 5):
        d.line([(sx, y1 - 12), (sx, y1 - 2)], fill=(220, 180, 60), width=2)

ART = {
    "cop31": art_cop31, "drones": art_drones, "maralago": art_maralago,
    "radar": art_radar, "factory": art_factory, "ship": art_ship,
    "candles": art_candles, "shield": art_shield, "bars": art_bars,
    "slide": art_slide, "sub": art_sub, "noflame": art_noflame,
    "mercury": art_mercury, "football": art_football, "castle": art_castle,
    "cricket": art_cricket,
}

# ---------------------------------------------------------------- sections
def draw_stat_strip(d):
    y0, y1 = 110, 142
    cw = 992 / 6.0
    for i, (val, lab) in enumerate(STATS):
        x = 16 + i * cw
        d.text((x + 6, y0 + 2), val, font=F("DejaVuSerif-Bold.ttf", 16), fill=INK)
        d.text((x + 6, y0 + 22), lab, font=F("DejaVuSans.ttf", 8), fill=GREY)
        if i:
            d.line([(x, y0 + 4), (x, y1 - 4)], fill=LINE, width=1)
    d.line([(16, y1), (1008, y1)], fill=LINE, width=1)


def draw_region_bar(d):
    # legend line
    legend = "  ·  ".join("%s %d" % (name, n) for name, n, _ in REGIONS)
    f = F("DejaVuSans.ttf", 8)
    tw = d.textlength(legend, font=f)
    d.text(((W - tw) / 2, 146), legend, font=f, fill=GREY)
    # segmented bar
    y0, y1 = 156, 168
    x = 16.0
    total = sum(n for _, n, _ in REGIONS)
    for name, n, col in REGIONS:
        w = 992.0 * n / total
        d.rectangle([x, y0, x + w, y1], fill=col)
        if w >= 18:
            cf = F("DejaVuSans-Bold.ttf", 9)
            cnt = str(n)
            tw2 = d.textlength(cnt, font=cf)
            d.text((x + (w - tw2) / 2, y0 + 1), cnt, font=cf, fill=(255, 255, 255))
        x += w
    # count line
    cf = F("DejaVuSans-Bold.ttf", 9)
    line = "39 STORIES  ·  8 REGIONS  ·  ONE PAGE"
    tw3 = d.textlength(line, font=cf)
    d.text(((W - tw3) / 2, 172), line, font=cf, fill=INK)


def draw_heroes(d):
    y0, y1 = 182, 350
    hw = 325
    for i, h in enumerate(HEROES):
        x = 16 + i * (hw + 8)
        card(d, [x, y0, x + hw, y1])
        badge(d, x + 13, y0 + 13, h["n"], r=8)
        f, lines = fit_headline(d, h["head"], "DejaVuSerif-Bold.ttf", 20,
                                hw - 42, 2)
        y = text_lines(d, x + 30, y0 + 7, lines, f, INK, 24)
        deck = wrap(d, h["deck"], F("DejaVuSans.ttf", 10), hw - 24)[:3]
        y = text_lines(d, x + 12, y + 4, deck, F("DejaVuSans.ttf", 10), INK, 13)
        tagline(d, x + 12, y + 4, h["tag"], h["src"], hw - 24)
        ay0 = y + 16
        ay1 = y1 - 8
        if ay1 - ay0 >= 24:
            ART[h["art"]](d, int(x + 8), int(ay0), int(x + hw - 8), int(ay1))


def draw_mids(d):
    # Row 1: mids 4-10 (7 cards). Row 2: mids 11-16 (6 cards, centred).
    cw, ch, gap = 136, 100, (992 - 7 * 136) / 6.0
    rows = [(354, MIDS[:7]), (460, MIDS[7:])]
    for y0, mids in rows:
        total_w = len(mids) * cw + (len(mids) - 1) * gap
        x = 16 + (992 - total_w) / 2.0
        for m in mids:
            card(d, [x, y0, x + cw, y0 + ch])
            badge(d, x + 10, y0 + 10, m["n"], r=7)
            f, lines = fit_headline(d, m["head"], "DejaVuSerif-Bold.ttf", 11,
                                    cw - 32, 2)
            text_lines(d, x + 24, y0 + 5, lines, f, INK, 13)
            deck = wrap(d, m["deck"], F("DejaVuSans.ttf", 8), cw - 16)[:3]
            text_lines(d, x + 8, y0 + 32, deck, F("DejaVuSans.ttf", 8), INK, 10)
            # tag, 7 pt (8 pt overflows the 120 px card on long sources)
            fb = F("DejaVuSans-Bold.ttf", 7)
            fr = F("DejaVuSans.ttf", 7)
            d.text((x + 8, y0 + 64), m["tag"], font=fb, fill=RED)
            wtag = d.textlength(m["tag"], font=fb)
            d.text((x + 8 + wtag + 3, y0 + 64), "— " + m["src"], font=fr, fill=GREY)
            ART[m["art"]](d, int(x + 6), y0 + 74, int(x + cw - 6), y0 + 96)
            x += cw + gap


def draw_briefs(d):
    fb = F("DejaVuSans-Bold.ttf", 9)
    fr = F("DejaVuSans.ttf", 9)
    cols = [BRIEFS[i:i + 8] for i in (0, 8, 16)]
    for ci, col in enumerate(cols):
        cx = 16 + ci * 333
        for ri, (n, loc, deck, src) in enumerate(col):
            y = 564 + ri * 24
            badge(d, cx + 7, y + 11, n, r=6)
            tx = cx + 20
            maxw = 325 - 20
            prefix = loc + " — "
            pw = d.textlength(prefix, font=fb)
            rest = deck + " (" + src + ")"
            rest_words = rest.split()
            blines, bcur, room = [], "", maxw - pw
            for wd in rest_words:
                cand = (bcur + " " + wd).strip()
                if d.textlength(cand, font=fr) <= room:
                    bcur = cand
                else:  # line full: close it, start next at full width
                    blines.append(bcur)
                    bcur = wd
                    room = maxw
            if bcur != "":
                blines.append(bcur)
            d.text((tx, y + 2), prefix, font=fb, fill=INK)
            if blines:
                d.text((tx + pw, y + 2), blines[0], font=fr, fill=INK)
            if len(blines) > 1:
                d.text((tx, y + 13), blines[1], font=fr, fill=INK)


# ---------------------------------------------------------------- map
MAPBOX = (16, 760, 1008, 910)
LAT_TOP, LAT_BOT = 84.0, -58.0


def lon_to_x(lon):
    return MAPBOX[0] + (lon + 180.0) / 360.0 * (MAPBOX[2] - MAPBOX[0])


def lat_to_y(lat):
    return MAPBOX[1] + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (MAPBOX[3] - MAPBOX[1])


def _badge_box(cx, cy, nums):
    if len(nums) == 1:
        return (cx - 7, cy - 7, cx + 7, cy + 7)
    f = ImageFont.truetype(os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), 7)
    label = "·".join(str(n) for n in nums)
    tw = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(label, font=f)
    w = 8 + tw
    return (cx - w / 2 - 1, cy - 9, cx + w / 2 + 1, cy + 9)


def _overlaps(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def solve_badges():
    """Greedy badge placement: preferred offset first, then rings of
    increasing radius. Returns {mark_index: (bx, by)} with 0 overlaps."""
    placed = []
    out = {}
    cands = [(0, -10), (0, 10), (10, 0), (-10, 0), (13, -13), (-13, -13),
             (13, 13), (-13, 13), (0, -18), (0, 18), (18, 0), (-18, 0),
             (20, -14), (-20, -14), (20, 14), (-20, 14), (0, -26), (0, 26),
             (26, 0), (-26, 0), (28, -20), (-28, -20), (28, 20), (-28, 20)]
    for i, (nums, lon, lat, dx, dy) in enumerate(PINS):
        px, py = lon_to_x(lon), lat_to_y(lat)
        tried = [(dx, dy)] + [c for c in cands if c != (dx, dy)]
        for ox, oy in tried:
            bx, by = px + ox, py + oy
            box = _badge_box(bx, by, nums)
            if box[0] < MAPBOX[0] + 2 or box[2] > MAPBOX[2] - 2:
                continue
            if box[1] < MAPBOX[1] + 2 or box[3] > MAPBOX[3] - 2:
                continue
            if any(_overlaps(box, p) for p in placed):
                continue
            placed.append(box)
            out[i] = (bx, by)
            break
        else:  # no offset fit: fall back to the preferred offset
            out[i] = (px + dx, py + dy)
    return out


def draw_map(d):
    x0, y0, x1, y1 = MAPBOX
    d.rectangle([x0, y0, x1, y1], fill=(228, 236, 240),
                outline=LINE, width=1)
    d.text((x0 + 6, y0 + 3), "WHERE IT HAPPENED",
           font=F("DejaVuSans-Bold.ttf", 8), fill=GREY)
    for poly in LAND:
        pts = [(lon_to_x(lon), lat_to_y(lat)) for lon, lat in poly]
        d.polygon(pts, fill=(214, 206, 188), outline=(160, 150, 130))
    # region labels
    for name, lon, lat in REGION_TAGS:
        f = F("DejaVuSans-Bold.ttf", 7)
        d.text((lon_to_x(lon), lat_to_y(lat)), name, font=f, fill=(120, 114, 100))
    pos = solve_badges()
    # pass 1: dots + leaders (two-pass: dark maroon then white)
    for i, (nums, lon, lat, dx, dy) in enumerate(PINS):
        px, py = lon_to_x(lon), lat_to_y(lat)
        bx, by = pos[i]
        d.line([(px, py), (bx, by)], fill=DARKRED, width=3)
        d.line([(px, py), (bx, by)], fill=(255, 255, 255), width=1)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    # pass 2: badges on top (no leader ever crosses a number)
    for i, (nums, lon, lat, dx, dy) in enumerate(PINS):
        bx, by = pos[i]
        if len(nums) == 1:
            badge(d, bx, by, nums[0], r=6)
        else:  # shared dot: pill listing all its numbers
            badge_pill(d, bx, by, nums)
    d.text((x0 + 6, y1 - 12), "13 · 39 = GLOBAL (no dot)",
           font=F("DejaVuSans.ttf", 7), fill=GREY)


def draw_datecheck(d):
    x0, y0, x1, y1 = 16, 914, 1008, 990
    d.rectangle([x0, y0, x1, y1], fill=(255, 248, 244),
                outline=RED, width=2)
    d.text((x0 + 8, y0 + 6), "DATE CHECK — these happened on ANOTHER day",
           font=F("DejaVuSans-Bold.ttf", 10), fill=RED)
    f = F("DejaVuSans.ttf", 8)
    for i, item in enumerate(DATECHECK):
        col = i // 4
        row = i % 4
        d.text((x0 + 8 + col * 492, y0 + 24 + row * 12), "•  " + item,
               font=f, fill=INK)


def draw_footer(d):
    f = F("DejaVuSans.ttf", 8)
    d.text((16, 996),
           "Sources: BBC · Reuters · AP · AFP · IANS · QNA · Euromaidan · Euronews · Lowy Institute · LaLiga · CNBC · Politico · JBizNews · Washington Post · Market Data · Qatar Tribune",
           font=f, fill=GREY)
    d.text((16, 1008),
           "All stories dated Sunday 22 November 2026 (UTC)  ·  39 stories  ·  8 regions  ·  One page",
           font=f, fill=GREY)


# ---------------------------------------------------------------- main
def build():
    img = make_paper()
    pen = ImageDraw.Draw(img)
    draw_masthead(pen)
    draw_stat_strip(pen)
    draw_region_bar(pen)
    draw_heroes(pen)
    draw_mids(pen)
    draw_briefs(pen)
    draw_map(pen)
    draw_datecheck(pen)
    draw_footer(pen)
    return img  # finished page


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
