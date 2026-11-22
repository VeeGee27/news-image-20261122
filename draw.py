#!/usr/bin/env python3
"""news-image-20261122 v1 — draws the 22 November 2026 front page.
Build-time renderer (Pillow). Writes entry.png 1024x1024, deterministic.
All 36 stories verified against original sources on 22 Nov 2026.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
PAGE = (243, 238, 225)      # warm newsprint cream
CARD = (252, 249, 240)      # slightly lighter cream for cards
INK = (28, 26, 22)
NAVY = (24, 38, 64)
NAVY2 = (34, 54, 88)
RED = (176, 32, 28)
GOLD = (184, 138, 42)
GREY = (96, 92, 84)
LINE = (180, 174, 160)
MAPSEA = (36, 52, 84)
MAPLAND = (222, 214, 196)
MAPLINE = (120, 112, 92)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

def F(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

# ---------------------------------------------------------------- stories
# heroes: (number, headline, deck, tag, source)
HEROES = [
    (1, "COP31 COLLAPSES",
     "EU and UK reject a pact with no mention of fossil fuels; the longest "
     "climate summit ever ends with no deal at all.",
     "CONFIRMED", "BBC · REUTERS"),
    (2, "186 DRONES OVER UKRAINE",
     "Russia fires 186 drones overnight; Ukraine downs 161, but strikes hit "
     "18 sites and a block of flats near Kyiv.",
     "CONFIRMED", "UKRAINE AIR FORCE"),
    (3, "PEACE TALKS AT MAR-A-LAGO",
     "Trump hosts Zelenskyy; 20-point plan \u201c90% agreed\u201d, US guarantees "
     "\u201c100% agreed\u201d \u2014 Donbas still blocks a deal.",
     "CONFIRMED", "AP · NEWS18"),
]

# mids: (number, headline, deck, tag, source)
MIDS = [
    (4, "BAHRAIN HIT",
     "Two hurt as Iran strikes Bahrain; Tehran claims two US radars hit.",
     "REPORTED", "REUTERS"),
    (5, "FACTORY FIRE",
     "Candy plant blaze kills 3 in Cikande; 36 workers still missing.",
     "CONFIRMED", "AP"),
    (6, "SHIP AFIRE IN BALTIC",
     "Russian ship hit by drones off Finland; war \u201cspilling over\u201d.",
     "REPORTED", "EUROMAIDAN"),
    (7, "ANT ENDS WEEK DOWN",
     "Shares end the week at $88.91, above the $83 IPO price.",
     "CONFIRMED", "CNBC"),
    (8, "NATO-STYLE GUARANTEES",
     "US floats Article 5-style cover for Kyiv; Kushner: Trump \u201copen\u201d.",
     "REPORTED", "POLITICO"),
    (9, "ASIA POWER SHIFTS",
     "Lowy: US lead over China smallest since 2018, 78.9 to 73.6.",
     "CONFIRMED", "LOWY INSTITUTE"),
    (10, "SAUDI SLIDES",
     "Tadawul closes below 10,000, down 1.95% on Sunday.",
     "CONFIRMED", "JBIZNEWS"),
    (11, "AUKUS ROW",
     "Australia rejects a US warning on submarine sales.",
     "CONFIRMED", "REUTERS"),
    (12, "EISENKOT CONDEMNS ARSON",
     "Eisenkot condemns settler arson attacks on West Bank villages.",
     "CONFIRMED", "REUTERS"),
    (13, "MERCURY ORBIT",
     "ESA confirms BepiColombo in Mercury orbit after 8 years in space.",
     "CONFIRMED", "ESA"),
]

# briefs: (number, label, text, source) — label is the place
BRIEFS = [
    (14, "GAZA", "Israeli strikes kill 4 despite the ceasefire; toll reaches 74,736.", "GAZA HEALTH MINISTRY"),
    (15, "MOSCOW", "Russia says it downed 170 Ukrainian drones overnight.", "QNA"),
    (16, "ODESA", "Power grid strained after overnight strikes; city short of power.", "EUROMAIDAN"),
    (17, "KHARKIV", "Drones set a house, a shop and a business ablaze.", "EUROMAIDAN"),
    (18, "KYIV", "Russia fired 2,700 drones, 1,460 bombs and 165 missiles this week.", "ZELENSKYY"),
    (19, "LVIV", "Dashcam catches a Russian projectile hitting a building.", "EURONEWS"),
    (20, "WASHINGTON", "Schumer faces a leadership challenge; secret vote on Dec 1.", "REUTERS"),
    (21, "OTTAWA", "Hegseth limits US military ties with Canada.", "WASHINGTON POST"),
    (22, "TAIPEI", "Stocks fall 17% in the week, worst since 1990.", "MARKET DATA"),
    (23, "LAS VEGAS", "Verstappen wins wild GP after 35 lead changes; Norris 2nd.", "REUTERS"),
    (24, "LILONGWE", "Malawi tightens border screening to keep Ebola out.", "MALAWI HEALTH MINISTRY"),
    (25, "KHARTOUM", "Drones damage UN and residential buildings in the capital.", "REPORTS"),
    (26, "IMPHAL", "Tainted alcohol kills 11, puts 180 in hospital in Manipur.", "REPORTS"),
    (27, "ISRAEL", "15,000-year-old clay figurines found, earliest in SW Asia.", "RESEARCHERS"),
    (28, "GAZA", "Aid groups score the Trump-backed peace plan 4 of 26.", "ANALYSIS"),
    (29, "GURGL", "Haugan wins slalom as Norway takes top two.", "REUTERS"),
    (30, "ANTALYA", "The 35% clean-electricity goal dies with the COP31 pact.", "BBC"),
    (31, "NEW YORK", "Anthropic sits on $244.6bn cash after its record IPO.", "FILINGS"),
    (32, "GAZA", "Peace board warns Israel: progress, or the UN takes the keys.", "BOARD OF PEACE"),
    (33, "MOGADISHU", "Somalia breaks ground on naval facilities with Turkey.", "DEFENCE MINISTRY"),
    (34, "DOHA", "Chile fight back to beat Algeria 4-2 at the U-17 World Cup.", "QATAR TRIBUNE"),
    (35, "SEOUL", "Education minister quits over the exam cheating scandal.", "WH NEWS"),
    (36, "GLOBAL", "Bitcoin breaks below $60,000 in the AI rout.", "MARKET DATA"),
]

# stat strip: (big, label) — each number tied to a story, none a hero headline figure
STATS = [
    ("161", "drones downed overnight"),
    ("$244.6BN", "Anthropic\u2019s cash after IPO"),
    ("\u221210%", "Nasdaq\u2019s worst week since 2020"),
    ("10BN", "km travelled to Mercury"),
    ("78.9", "US Asia-power score"),
    ("4\u20132", "Chile\u2019s U-17 comeback win"),
]

# region bar: (label, count)
REGIONS = [
    ("EUROPE", 9), ("N. AMERICA", 6), ("MIDDLE EAST", 7), ("ASIA", 5),
    ("AFRICA", 3), ("OCEANIA", 1), ("S. AMERICA", 1), ("GLOBAL", 4),
]

# DATE CHECK — big stories deliberately left out (happened on another day)
DATECHECK = [
    "Shenzhen Trump\u2013Xi\u2013Putin summit (Thu 19 Nov)",
    "ICJ: Myanmar guilty of Rohingya genocide (Thu 19 Nov)",
    "El Chapo Isidro captured in Sinaloa (Sat 21 Nov)",
    "FBI crime database + USDA hacked (Sat 21 Nov)",
    "EU\u2013Indonesia trade deal (Sat 21 Nov)",
    "Friday rout: S&P \u22123.7%, Nasdaq \u22125.3% (Fri 20 Nov)",
    "Peru 6.7 quake, 1 dead (Fri 20 Nov)",
    "Kryvyi Rih missile strike, 2 killed (Sat 21 Nov)",
]

# map markers: number -> (lon, lat, dx, dy)  dx,dy = badge offset in px
MARKS = [
    ((1, 30), 30.7, 36.9, 13, 13),
    ((2, 18), 30.5, 50.45, 0, -10),
    ((3,), -80.03, 26.7, -10, 10),
    ((4,), 50.6, 26.2, 13, -13),
    ((5,), 106.4, -6.2, 0, -10),
    ((6,), 26.0, 59.8, 0, -16),
    ((7, 31), -74.0, 40.7, 0, -10),
    ((8, 20), -77.0, 38.9, 10, 10),
    ((9,), 151.2, -33.9, 0, -10),
    ((10,), 46.7, 24.7, 16, 0),
    ((11,), 149.1, -35.3, 10, 10),
    ((12,), 35.2, 32.0, -13, 13),
    ((14, 28, 32), 34.45, 31.5, 0, -10),
    ((15,), 37.6, 55.75, 13, -13),
    ((16,), 30.7, 46.5, -24, 24),
    ((17,), 36.2, 50.0, -28, -28),
    ((19,), 24.0, 49.8, -20, 0),
    ((21,), -75.7, 45.4, -13, 13),
    ((22,), 121.6, 25.0, 0, -10),
    ((23,), -115.1, 36.2, 0, -10),
    ((24,), 33.8, -13.97, 0, -10),
    ((25,), 32.5, 15.6, -13, 13),
    ((26,), 93.9, 24.8, 0, -10),
    ((27,), 34.9, 31.8, 24, 24),
    ((29,), 11.1, 46.85, -20, 20),
    ((33,), 45.3, 2.05, 10, 10),
    ((34,), 51.5, 25.3, -16, 16),
    ((35,), 127.0, 37.5, 0, -10),
]

# ---------------------------------------------------------------- helpers
def wrap(d, text, font, maxw):
    """Greedy word wrap; returns list of lines that fit maxw."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_headline(d, text, path, size, maxw, maxlines, min_size=10):
    """Shrink font until the headline wraps to <= maxlines lines."""
    s = size
    while s > min_size:
        f = F(path, s)
        if len(wrap(d, text, f, maxw)) <= maxlines:
            return f, wrap(d, text, f, maxw)
        s -= 1
    f = F(path, s)
    return f, wrap(d, text, f, maxw)

def text_lines(d, x, y, lines, font, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y

def card(d, box, fill=CARD, outline=LINE, width=1):
    d.rectangle(box, fill=fill, outline=outline, width=width)

def badge(d, x, y, n, r=8, font=None):
    """Red disc with a white number, centred on (x, y)."""
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255), width=1)
    f = font or F("DejaVuSans-Bold.ttf", 9 if n < 10 else 8)
    t = str(n)
    tw = d.textlength(t, font=f)
    th = f.getbbox(t)[3] - f.getbbox(t)[1]
    d.text((x - tw / 2, y - th / 2 - 1), t, font=f, fill=(255, 255, 255))


def badge_pill(d, x, y, nums, small=False):
    """Wide red pill listing several story numbers sharing one dot."""
    f = F("DejaVuSans-Bold.ttf", 7 if small else 8)
    label = "\u00b7".join(str(n) for n in nums)
    tw = d.textlength(label, font=f)
    w = tw + 8
    h = 7 if small else 8
    d.rounded_rectangle([x - w / 2, y - h, x + w / 2, y + h], radius=h,
                        fill=RED, outline=(255, 255, 255), width=1)
    d.text((x - tw / 2, y - 5), label, font=f, fill=(255, 255, 255))

def tagline(d, x, y, tag, source, maxw):
    f = F("DejaVuSans-Bold.ttf", 8)
    d.text((x, y), tag, font=f, fill=RED)
    w = d.textlength(tag, font=f)
    f2 = F("DejaVuSans.ttf", 8)
    d.text((x + w + 4, y), "\u2014 " + source, font=f2, fill=GREY)

# ---------------------------------------------------------------- paper
def make_paper():
    img = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(img)
    # fibre speckles, seeded (deterministic)
    rng = random.Random(20261122)
    for _ in range(5000):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        v = rng.randint(-5, 5)
        d.point((x, y), fill=(PAGE[0] + v, PAGE[1] + v, PAGE[2] + v))
    # faint radial vignette, max ~10% at corners
    g = Image.new("L", (128, 128), 0)
    gd = ImageDraw.Draw(g)
    for r in range(64, 0, -1):
        a = int(26 * (1 - r / 64.0) ** 2)
        gd.ellipse([64 - r, 64 - r, 64 + r, 64 + r], fill=a)
    g = g.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(8))
    dark = Image.new("RGB", (W, H), (60, 50, 38))
    img = Image.composite(dark, img, g)
    return img

# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    d.text((16, 18), "THE WORLD IN ONE DAY", font=F("DejaVuSans-Bold.ttf", 12),
           fill=RED)
    d.text((16, 36), "Sunday 22 November 2026", font=F("DejaVuSerif-Bold.ttf", 40),
           fill=INK)
    d.text((16, 84),
           "COP31 collapses  \u00b7  186 drones over Ukraine  \u00b7  Trump and Zelenskyy talk peace at Mar-a-Lago",
           font=F("DejaVuSerif.ttf", 14), fill=(64, 58, 48))
    d.line([(16, 106), (1008, 106)], fill=INK, width=2)
    d.text((16, 110), "36 STORIES  \u00b7  8 REGIONS  \u00b7  ONE PAGE",
           font=F("DejaVuSans-Bold.ttf", 10), fill=INK)
    d.text((1008, 110), "All times UTC", font=F("DejaVuSans.ttf", 10), fill=GREY,
           anchor="ra")

def draw_stats(d):
    y0, y1, x0, x1 = 128, 168, 16, 1008
    cw = (x1 - x0) / 6
    d.rectangle([x0, y0, x1, y1], outline=LINE, width=1)
    for i, (big, label) in enumerate(STATS):
        x = x0 + i * cw
        if i:
            d.line([(x, y0 + 4), (x, y1 - 4)], fill=LINE, width=1)
        bf = F("DejaVuSerif-Bold.ttf", 20)
        bw = d.textlength(big, font=bf)
        d.text((x + (cw - bw) / 2, y0 + 3), big, font=bf, fill=NAVY)
        lf = F("DejaVuSans.ttf", 8)
        lw = d.textlength(label, font=lf)
        d.text((x + (cw - lw) / 2, y0 + 28), label, font=lf, fill=GREY)

def draw_regions(d):
    y0, y1, x0, x1 = 174, 194, 16, 1008
    cols = [(24, 38, 64), (176, 32, 28), (184, 138, 42), (46, 110, 70),
            (120, 72, 140), (40, 110, 150), (150, 90, 40), (105, 105, 105)]
    segw = (x1 - x0) / len(REGIONS)
    for i, (name, count) in enumerate(REGIONS):
        sx0 = x0 + i * segw
        sx1 = x0 + (i + 1) * segw
        d.rectangle([sx0, y0, sx1 - 1, y1], fill=cols[i % len(cols)])
        t = "%s %d" % (name, count)
        f = F("DejaVuSans-Bold.ttf", 9)
        tw = d.textlength(t, font=f)
        d.text((sx0 + (segw - tw) / 2, y0 + 4), t, font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- hero art
def art_cop31(d, box):
    """Conference hall: rows of flags and a broken globe."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(42, 58, 92))
    # globe, cracked
    cx, cy, r = x0 + 46, y0 + 32, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(96, 140, 110),
              outline=(220, 220, 200), width=2)
    d.line([(cx - 8, cy - 24), (cx + 2, cy - 6), (cx - 4, cy + 8), (cx + 10, cy + 24)],
           fill=(220, 220, 200), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(220, 220, 200), width=1)
    # flags row
    cols = [(176, 32, 28), (24, 38, 64), (184, 138, 42), (46, 110, 70), (120, 72, 140)]
    for i, c in enumerate(cols):
        fx = x0 + 96 + i * 34
        d.line([(fx, y0 + 8), (fx, y0 + 44)], fill=(220, 220, 200), width=1)
        d.polygon([(fx, y0 + 8), (fx + 26, y0 + 13), (fx, y0 + 18)], fill=c)
    # delegates: small heads + shoulders
    for i in range(6):
        hx = x0 + 100 + i * 32
        d.ellipse([hx, y1 - 22, hx + 12, y1 - 10], fill=(210, 190, 160))
        d.pieslice([hx - 4, y1 - 12, hx + 16, y1 + 6], 180, 360, fill=(90, 90, 100))
    d.text((x1 - 8, y1 - 14), "ANTALYA", font=F("DejaVuSans-Bold.ttf", 9),
           fill=(220, 220, 200), anchor="ra")

def art_drones(d, box):
    """Night sky, drone silhouettes, interception bursts."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 20, 38))
    rng = random.Random(7)
    for _ in range(26):
        sx = rng.randint(x0 + 4, x1 - 4)
        sy = rng.randint(y0 + 4, y0 + 22)
        d.point((sx, sy), fill=(200, 200, 220))
    # city skyline
    for i, bh in enumerate([26, 40, 30, 48, 34, 44, 28]):
        bx = x0 + 8 + i * 42
        d.rectangle([bx, y1 - bh, bx + 34, y1], fill=(30, 34, 52))
        for wy in range(y1 - bh + 5, y1 - 4, 9):
            for wx in (bx + 6, bx + 18):
                d.rectangle([wx, wy, wx + 5, wy + 4], fill=(230, 190, 80))
    # drones: small crosses with red trails
    for dx, dy in [(x0 + 60, y0 + 14), (x0 + 150, y0 + 8), (x0 + 230, y0 + 18),
                   (x0 + 110, y0 + 26), (x0 + 270, y0 + 10)]:
        d.line([(dx - 7, dy), (dx + 7, dy)], fill=(220, 220, 220), width=2)
        d.line([(dx, dy - 3), (dx, dy + 3)], fill=(220, 220, 220), width=2)
        d.line([(dx, dy), (dx + 22, dy + 26)], fill=(176, 32, 28), width=2)
    # bursts
    for bx, by in [(x0 + 84, y0 + 42), (x0 + 254, y0 + 38)]:
        for r, c in [(10, (255, 190, 60)), (6, (255, 230, 140)), (3, (255, 255, 255))]:
            d.ellipse([bx - r, by - r, bx + r, by + r], fill=c)

def art_maralgo(d, box):
    """Palm trees, white resort building, two flags."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(126, 178, 208))
    d.rectangle([x0, y0 + 34, x1, y1], fill=(240, 232, 214))
    # sun
    d.ellipse([x1 - 52, y0 + 6, x1 - 20, y0 + 38], fill=(255, 214, 90))
    # palms
    for px in (x0 + 22, x0 + 62, x1 - 26):
        d.line([(px, y1 - 6), (px + 4, y0 + 30)], fill=(90, 60, 30), width=3)
        for ang in (-50, -20, 10, 40):
            ex = px + 4 + int(20 * math.cos(math.radians(ang - 90)))
            ey = y0 + 30 + int(20 * math.sin(math.radians(ang - 90)))
            d.line([(px + 4, y0 + 30), (ex, ey)], fill=(40, 110, 60), width=2)
    # white building with arches
    bx0, by0 = x0 + 96, y0 + 30
    d.rectangle([bx0, by0, bx0 + 130, y1 - 4], fill=(250, 246, 236),
                outline=(150, 140, 120), width=1)
    for i in range(3):
        ax = bx0 + 14 + i * 42
        d.pieslice([ax, by0 + 12, ax + 26, by0 + 38], 180, 360, fill=(40, 70, 110))
        d.rectangle([ax, by0 + 25, ax + 26, y1 - 4], fill=(40, 70, 110))
    # flags on the roof
    for i, c in enumerate([(176, 32, 28), (40, 90, 160)]):
        fx = bx0 + 30 + i * 60
        d.line([(fx, by0 - 16), (fx, by0)], fill=(60, 50, 40), width=1)
        d.polygon([(fx, by0 - 16), (fx + 22, by0 - 12), (fx, by0 - 8)], fill=c)

def draw_heroes(d):
    y0, y1 = 200, 386
    x0 = 16
    cw = 320
    gap = 8
    arts = [art_cop31, art_drones, art_maralgo]
    for i, (num, head, deck, tag, source) in enumerate(HEROES):
        x = x0 + i * (cw + gap)
        card(d, [x, y0, x + cw, y1])
        tx = x + 10
        # number + headline
        badge(d, tx + 9, y0 + 14, num)
        hf, hlines = fit_headline(d, head, "DejaVuSerif-Bold.ttf", 19, cw - 42, 2)
        y = y0 + 8
        y = text_lines(d, tx + 26, y, hlines, hf, INK, 23)
        # deck
        df = F("DejaVuSans.ttf", 10)
        dlines = wrap(d, deck, df, cw - 20)
        assert len(dlines) <= 3, ("hero deck overflow", num, dlines)
        y = text_lines(d, tx, y + 4, dlines, df, (52, 48, 40), 13)
        # tag
        tagline(d, tx, y + 4, tag, source, cw - 20)
        # illustration strip at the bottom
        arts[i](d, (x + 1, y1 - 66, x + cw - 1, y1 - 1))

# ---------------------------------------------------------------- mid art
def _mid_bg(d, box, fill):
    d.rectangle(box, fill=fill)

def art_radar(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (30, 42, 74))
    # radar screen
    cx, cy, r = x0 + 30, y0 + 15, 12
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 200, 120), width=1)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(120, 200, 120), width=1)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(120, 200, 120))
    d.line([(cx, cy - r), (cx, cy + r)], fill=(120, 200, 120))
    d.line([(cx, cy), (cx + 8, cy - 8)], fill=(160, 230, 160), width=2)
    d.ellipse([cx + 6, cy - 10, cx + 9, cy - 7], fill=(160, 230, 160))
    d.ellipse([cx - 7, cy + 3, cx - 4, cy + 6], fill=(160, 230, 160))
    # incoming missiles
    d.line([(x0 + 58, y0 + 22), (x0 + 104, y0 + 6)], fill=(255, 120, 60), width=2)
    d.line([(x0 + 68, y0 + 24), (x0 + 128, y0 + 10)], fill=(255, 120, 60), width=2)
    d.ellipse([x0 + 102, y0 + 4, x0 + 108, y0 + 10], fill=(255, 190, 60))
    d.ellipse([x0 + 126, y0 + 8, x0 + 132, y0 + 14], fill=(255, 190, 60))

def art_fire(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (52, 34, 30))
    d.rectangle([x0 + 8, y0 + 14, x0 + 60, y1 - 2], fill=(110, 100, 92))
    d.rectangle([x0 + 16, y0 + 20, x0 + 26, y0 + 28], fill=(40, 40, 48))
    d.rectangle([x0 + 40, y0 + 20, x0 + 50, y0 + 28], fill=(40, 40, 48))
    for fx, fh in [(x0 + 70, 18), (x0 + 84, 24), (x0 + 98, 16), (x0 + 112, 20)]:
        d.polygon([(fx, y1 - 2), (fx + 6, y1 - fh), (fx + 12, y1 - 2)],
                  fill=(255, 140, 30))
        d.polygon([(fx + 3, y1 - 2), (fx + 6, y1 - fh + 8), (fx + 9, y1 - 2)],
                  fill=(255, 220, 80))

def art_ship(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (38, 66, 92))
    d.rectangle([x0, y0 + 16, x1, y1], fill=(24, 52, 84))
    d.polygon([(x0 + 14, y0 + 16), (x0 + 118, y0 + 16), (x0 + 106, y1 - 6),
               (x0 + 26, y1 - 6)], fill=(18, 22, 30))
    d.rectangle([x0 + 60, y0 + 6, x0 + 74, y0 + 16], fill=(50, 56, 66))
    for sx, sy, sr in [(x0 + 62, y0 + 10, 3), (x0 + 72, y0 + 9, 3)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 155, 160))
    d.polygon([(x0 + 92, y0 + 16), (x0 + 97, y0 + 6), (x0 + 102, y0 + 16)],
              fill=(255, 120, 60))
    d.polygon([(x0 + 95, y0 + 16), (x0 + 97, y0 + 10), (x0 + 99, y0 + 16)],
              fill=(255, 190, 60))
    d.line([(x0 + 136, y0 + 8), (x0 + 164, y0 + 12)], fill=(255, 120, 60), width=2)
    d.ellipse([x0 + 162, y0 + 8, x0 + 168, y0 + 14], fill=(255, 190, 60))

def art_chart_down(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (246, 240, 228))
    d.line([(x0 + 6, y1 - 6), (x1 - 6, y1 - 6)], fill=GREY, width=1)
    pts = [(x0 + 12, y0 + 6), (x0 + 40, y0 + 10), (x0 + 68, y0 + 16),
           (x0 + 96, y0 + 14), (x0 + 124, y0 + 22)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=RED, width=2)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    d.polygon([(x1 - 16, y0 + 20), (x1 - 6, y0 + 20), (x1 - 11, y1 - 8)], fill=RED)

def art_shield(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (34, 54, 88))
    cx = x0 + (x1 - x0) // 2
    d.polygon([(cx - 26, y0 + 2), (cx + 26, y0 + 2), (cx + 26, y0 + 14),
               (cx, y1 - 4), (cx - 26, y0 + 14)], fill=(220, 220, 210),
              outline=GOLD, width=2)
    for sx, sy in [(cx, y0 + 8), (cx - 12, y0 + 14), (cx + 12, y0 + 14)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)

def art_bars(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (246, 240, 228))
    vals = [("US", 79, NAVY), ("CN", 74, RED), ("IN", 41, GOLD), ("JP", 39, (46, 110, 70))]
    for i, (lab, v, c) in enumerate(vals):
        bx = x0 + 12 + i * 32
        bh = int(v / 80 * (y1 - y0 - 12))
        d.rectangle([bx, y1 - 4 - bh, bx + 20, y1 - 4], fill=c)
        d.text((bx + 2, y1 - 13), lab, font=F("DejaVuSans-Bold.ttf", 7),
               fill=(255, 255, 255))

def art_tadawul(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (246, 240, 228))
    d.line([(x0 + 6, y1 - 6), (x1 - 6, y1 - 6)], fill=GREY, width=1)
    pts = [(x0 + 12, y0 + 8), (x0 + 44, y0 + 12), (x0 + 76, y0 + 10),
           (x0 + 108, y0 + 20), (x0 + 128, y0 + 24)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=RED, width=2)
    d.text((x1 - 6, y0 + 2), "10,000", font=F("DejaVuSans-Bold.ttf", 8), fill=RED,
           anchor="ra")

def art_sub(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (28, 58, 86))
    d.rectangle([x0, y0 + 12, x1, y1], fill=(18, 44, 70))
    d.ellipse([x0 + 20, y0 + 8, x0 + 118, y0 + 24], fill=(96, 126, 156))
    d.rectangle([x0 + 56, y0 + 2, x0 + 72, y0 + 10], fill=(96, 126, 156))
    d.polygon([(x0 + 118, y0 + 12), (x0 + 132, y0 + 16), (x0 + 118, y0 + 20)],
              fill=(96, 126, 156))
    d.line([(x0 + 24, y0 + 16), (x0 + 114, y0 + 16)], fill=(210, 220, 230), width=1)
    for wx in range(x0 + 12, x1 - 8, 22):
        d.ellipse([wx, y0 + 26, wx + 5, y0 + 29], fill=(140, 180, 210))

def art_arson(d, box):
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (52, 34, 30))
    d.polygon([(x0 + 20, y0 + 12), (x0 + 46, y0 + 2), (x0 + 72, y0 + 12)],
              fill=(120, 60, 40))
    d.rectangle([x0 + 24, y0 + 12, x0 + 68, y1 - 2], fill=(200, 180, 150))
    d.rectangle([x0 + 42, y0 + 18, x0 + 50, y1 - 2], fill=(60, 40, 30))
    for fx, fh in [(x0 + 80, 16), (x0 + 92, 22), (x0 + 104, 15)]:
        d.polygon([(fx, y1 - 2), (fx + 6, y1 - fh), (fx + 12, y1 - 2)],
                  fill=(255, 140, 30))

def art_mercury(d, box):
    """Mercury + BepiColombo: cratered grey disc, spacecraft with panels."""
    x0, y0, x1, y1 = box
    _mid_bg(d, box, (16, 20, 38))
    # stars
    for sx, sy in [(x0 + 8, y0 + 5), (x0 + 62, y0 + 4), (x0 + 152, y0 + 6),
                   (x0 + 178, y0 + 12), (x0 + 98, y0 + 24), (x0 + 14, y0 + 24)]:
        d.point((sx, sy), fill=(200, 200, 220))
    # Mercury: cratered grey disc
    cx, cy, r = x0 + 30, y0 + 15, 11
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 145, 135),
              outline=(210, 205, 195), width=1)
    for kx, ky, kr in [(cx - 4, cy - 3, 2), (cx + 3, cy + 2, 3), (cx + 5, cy - 5, 2)]:
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(120, 115, 105))
    # spacecraft: gold body + blue solar panels, orange thruster trail
    bx, by = x0 + 92, y0 + 12
    d.rectangle([bx, by, bx + 14, by + 7], fill=(220, 190, 90),
                outline=(255, 230, 150), width=1)
    d.rectangle([bx - 16, by + 2, bx, by + 5], fill=(60, 110, 180))
    d.rectangle([bx + 14, by + 2, bx + 30, by + 5], fill=(60, 110, 180))
    d.line([(bx + 30, by + 3), (bx + 44, by + 3)], fill=(255, 140, 40), width=2)
    d.ellipse([bx + 44, by + 1, bx + 48, by + 5], fill=(255, 190, 60))

MID_ARTS = [art_radar, art_fire, art_ship, art_chart_down, art_shield,
            art_bars, art_tadawul, art_sub, art_arson, art_mercury]

def draw_mids(d):
    y_rows = [(390, 494), (498, 602)]
    x0 = 16
    cw = 192
    gap = 8
    for r, (y0, y1) in enumerate(y_rows):
        for c in range(5):
            i = r * 5 + c
            num, head, deck, tag, source = MIDS[i]
            x = x0 + c * (cw + gap)
            card(d, [x, y0, x + cw, y1])
            tx = x + 8
            badge(d, tx + 8, y0 + 12, num)
            hf, hlines = fit_headline(d, head, "DejaVuSerif-Bold.ttf", 13, cw - 36, 2)
            y = y0 + 6
            y = text_lines(d, tx + 22, y, hlines, hf, INK, 15)
            df = F("DejaVuSans.ttf", 9)
            dlines = wrap(d, deck, df, cw - 16)
            assert len(dlines) <= 2, ("mid deck overflow", num, dlines)
            y = text_lines(d, tx, y + 2, dlines, df, (52, 48, 40), 11)
            tagline(d, tx, y + 2, tag, source, cw - 16)
            MID_ARTS[i](d, (x + 1, y1 - 30, x + cw - 1, y1 - 1))

# ---------------------------------------------------------------- map
MAPBOX = (16, 606, 420, 876)
MAP_SCALE = 1.12
MAP_CY = 741  # y of latitude 10

def proj(lon, lat):
    x = MAPBOX[0] + (lon + 180) * MAP_SCALE
    y = MAP_CY - (lat - 10) * MAP_SCALE
    return x, y

CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73), (-105, 74),
     (-95, 80), (-85, 80), (-80, 73), (-70, 62), (-60, 55), (-55, 52),
     (-60, 47), (-65, 44), (-70, 42), (-75, 38), (-76, 35), (-80, 32),
     (-81, 30), (-80, 28), (-79.8, 26), (-80.5, 25.5), (-82, 27), (-83, 29),
     (-85, 29), (-90, 21), (-94, 17), (-97, 16), (-92, 14),
     (-87, 13), (-83, 9), (-79, 8), (-82, 9), (-86, 12), (-90, 14),
     (-95, 16), (-100, 18), (-105, 20), (-110, 23), (-114, 28), (-120, 34),
     (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-150, 59), (-158, 58),
     (-165, 60), (-168, 66)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
     (-30, 78), (-45, 80), (-55, 78), (-58, 72), (-58, 66), (-55, 60)],
    # South America
    [(-80, 9), (-77, 8), (-75, 11), (-72, 12), (-68, 11), (-62, 10),
     (-60, 8), (-55, 6), (-52, 4), (-50, 0), (-44, -3), (-38, -5),
     (-35, -8), (-37, -13), (-39, -18), (-41, -23), (-48, -27), (-53, -33),
     (-58, -38), (-62, -41), (-66, -46), (-68, -52), (-71, -54), (-74, -50),
     (-73, -44), (-72, -37), (-71, -30), (-70, -22), (-75, -15), (-79, -8),
     (-81, -5), (-80, 9)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-1, 46), (2, 47), (3, 50),
     (5, 53), (8, 55), (8, 57), (10, 59), (13, 56), (18, 56), (21, 55),
     (24, 58), (27, 60), (30, 62), (28, 65), (25, 69), (20, 70), (16, 68),
     (12, 65), (10, 62), (5, 60), (5, 57), (8, 54), (10, 52), (6, 50),
     (2, 49), (-1, 48), (-4, 44), (-9, 43), (-10, 36)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-2, 51), (-5, 50)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 12),
     (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (12, 0), (13, -5),
     (12, -10), (13, -17), (15, -22), (17, -29), (20, -35), (26, -34),
     (32, -28), (35, -24), (40, -18), (40, -12), (42, -5), (46, 0), (51, 2),
     (51, 11), (48, 11), (44, 13), (43, 12), (40, 15), (38, 18), (36, 22),
     (34, 27), (32, 31), (30, 32), (25, 32), (20, 32), (15, 32), (11, 34),
     (10, 37), (5, 37), (0, 36), (-6, 35)],
    # Asia
    [(30, 36), (35, 36), (35.5, 33), (34.8, 32), (34.4, 31.5), (36, 31),
     (38, 31), (42, 29), (46, 29),
     (48, 30), (52, 28), (54, 27), (57, 26), (60, 25), (62, 25), (66, 25),
     (68, 23), (70, 20), (73, 20), (76, 15), (77, 8), (80, 7), (80, 10),
     (83, 17), (86, 20), (89, 22), (91, 22), (93, 18), (95, 16), (98, 10),
     (100, 8), (103, 5), (104, 2), (105, 9), (108, 11), (109, 15), (109, 20),
     (106, 20), (105, 23), (108, 22), (110, 21), (113, 22), (116, 23),
     (118, 25), (120, 28), (122, 30), (121, 33), (120, 35), (122, 37),
     (124, 39), (126, 38), (126, 36), (128, 35), (129, 37), (129, 39),
     (127, 40), (130, 42), (132, 43), (135, 44), (138, 46),
     (140, 48), (142, 50), (141, 53), (140, 56), (138, 59), (136, 60),
     (140, 60), (142, 59), (145, 60), (150, 60), (156, 60), (158, 56),
     (160, 55), (162, 58), (163, 60), (162, 62), (158, 64), (155, 66),
     (150, 68), (145, 70), (140, 71), (135, 72), (130, 72), (125, 73),
     (120, 73), (115, 73), (110, 74), (105, 75), (100, 76), (95, 76),
     (90, 75), (85, 75), (80, 73), (75, 72), (70, 72), (65, 70), (60, 69),
     (55, 68), (50, 68), (45, 68), (40, 68), (35, 67), (32, 66), (30, 64),
     (28, 62), (25, 60), (22, 58), (20, 55), (18, 54), (15, 52), (12, 50),
     (10, 48), (8, 46), (6, 44), (3, 42), (0, 40), (5, 38), (10, 37),
     (15, 38), (20, 40), (23, 40), (26, 38), (28, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (151, -24), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (113, -22)],
    # Sumatra
    [(95, 5), (98, 3), (101, 1), (104, -2), (106, -5), (105, -6),
     (102, -3), (99, 0), (96, 3), (95, 5)],
    # Java (Cikande pin 106.4, -6.2 sits on its north coast)
    [(105, -5.5), (109, -6), (113, -7), (114, -7.5), (114, -8.5),
     (110, -8), (106, -6.5), (105, -5.5)],
    # Borneo
    [(109, 1), (112, 4), (116, 6), (118, 2), (117, -2), (114, -4),
     (110, -3), (109, 0), (109, 1)],
    # Sulawesi
    [(119, 0), (121, 1), (123, -1), (121, -3), (120, -5), (119, -3), (119, 0)],
    # New Guinea
    [(131, -1), (135, -2), (138, -3), (141, -3), (141, -8), (138, -8),
     (135, -6), (132, -4), (131, -1)],
    # Japan (Honshu-Hokkaido-Kyushu chain)
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (141, 41), (143, 42), (145, 44), (143, 44), (141, 42),
     (140, 39), (139, 37), (136, 34), (133, 34), (131, 32), (130, 31)],
    # Arabian Peninsula (Riyadh, Doha, Bahrain pins sit on it)
    [(39, 28), (39, 23), (41, 19), (43, 15), (45, 13), (48, 14), (51, 16),
     (54, 17), (56, 20), (58, 23), (59, 25), (57, 26), (55, 27), (53, 28),
     (51, 29), (49, 30), (45, 30), (42, 30), (39, 28)],
    # Taiwan
    [(120, 25.5), (122, 25.5), (122, 22), (120, 22)],
    # Philippines
    [(120, 18), (122, 16), (122, 13), (124, 11), (123, 9), (121, 10),
     (120, 13), (120, 18)],
    # New Zealand
    [(167, -45), (170, -42), (173, -41), (175, -38), (178, -38), (176, -40),
     (174, -42), (171, -44), (167, -45)],
]

REGION_LABELS = [
    ("NORTH AMERICA", -130, 30), ("SOUTH AMERICA", -35, -25),
    ("EUROPE", -35, 62), ("AFRICA", -25, 5), ("ASIA", 75, -25),
    ("OCEANIA", 115, -48),
]

def draw_map(d):
    x0, y0, x1, y1 = MAPBOX
    card(d, [x0, y0, x1, y1], fill=MAPSEA, outline=LINE)
    d.text((x0 + 10, y0 + 6), "WHERE IT HAPPENED", font=F("DejaVuSans-Bold.ttf", 11),
           fill=(235, 235, 225))
    d.text((x1 - 10, y0 + 7), "\u25cf = story location", font=F("DejaVuSans.ttf", 8),
           fill=(200, 200, 190), anchor="ra")
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAPLAND, outline=MAPLINE)
    lf = F("DejaVuSans-Bold.ttf", 8)
    for name, lon, lat in REGION_LABELS:
        lx, ly = proj(lon, lat)
        d.text((lx, ly), name, font=lf, fill=(170, 175, 190), anchor="mm")
    # markers: dot at true location (white-ringed so it reads on land and
    # sea), short leader to a nearby badge; the dot never moves.
    # Two passes: all dots + leaders first, then all badges on top, so no
    # leader ever crosses over a number.
    seen = {}
    for nums, lon, lat, dx, dy in MARKS:
        mx, my = proj(lon, lat)
        key = (round(mx), round(my))
        if key not in seen:
            d.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=(255, 255, 255))
            d.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=RED)
            seen[key] = True
        bx, by = mx + dx, my + dy
        if dx or dy:
            d.line([(mx, my), (bx, by)], fill=(90, 20, 20), width=3)
            d.line([(mx, my), (bx, by)], fill=(255, 255, 255), width=1)
    for nums, lon, lat, dx, dy in MARKS:
        mx, my = proj(lon, lat)
        bx, by = mx + dx, my + dy
        if len(nums) == 1:
            badge(d, bx, by, nums[0], r=6)
        else:
            badge_pill(d, bx, by, nums, small=True)
    d.text((x0 + 10, y1 - 22),
           "Pills mark dots shared by several stories",
           font=F("DejaVuSans.ttf", 8), fill=(200, 200, 190))
    d.text((x0 + 10, y1 - 11), "13 \u00b7 36 = GLOBAL (no dot)",
           font=F("DejaVuSans.ttf", 8), fill=(200, 200, 190))

# ---------------------------------------------------------------- briefs
def draw_brief(d, x, y, w, num, label, text, source):
    """One brief item; returns height used. Max 3 lines."""
    bf = F("DejaVuSans-Bold.ttf", 8)
    rf = F("DejaVuSans.ttf", 8)
    prefix = "%d %s" % (num, label)
    pw = d.textlength(prefix, font=bf)
    full = text + " (" + source + ")"
    words = full.split()
    lines, cur = [], ""
    avail = w - pw - 6
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=rf) <= avail:
            cur = t
        else:
            lines.append(cur)
            cur = wd
            avail = w
    if cur:
        lines.append(cur)
    assert len(lines) <= 3, ("brief overflow", num, lines)
    d.text((x, y), prefix, font=bf, fill=INK)
    d.text((x + pw + 4, y), lines[0] if lines else "", font=rf, fill=(52, 48, 40))
    yy = y + 10
    for ln in lines[1:]:
        d.text((x, yy), ln, font=rf, fill=(52, 48, 40))
        yy += 10
    return yy - y + 2

def draw_briefs(d):
    x0, y0 = 432, 606
    d.text((x0, y0), "ALSO ON SUNDAY 22 NOVEMBER",
           font=F("DejaVuSans-Bold.ttf", 11), fill=INK)
    d.line([(x0, y0 + 18), (1008, y0 + 18)], fill=LINE, width=1)
    cols = [(432, 186), (626, 186), (820, 188)]
    groups = [BRIEFS[0:8], BRIEFS[8:16], BRIEFS[16:23]]
    for (cx, cw), group in zip(cols, groups):
        y = y0 + 24
        for num, label, text, source in group:
            h = draw_brief(d, cx, y, cw, num, label, text, source)
            y += h + 3

# ---------------------------------------------------------------- date check + footer
def draw_datecheck(d):
    x0, y0, x1, y1 = 16, 880, 1008, 938
    d.rectangle([x0, y0, x1, y1], outline=RED, width=2)
    d.text((x0 + 8, y0 + 3), "DATE CHECK \u2014 NOT 22 NOVEMBER: left out on purpose",
           font=F("DejaVuSans-Bold.ttf", 10), fill=RED)
    f = F("DejaVuSans.ttf", 8)
    left = DATECHECK[0:4]
    right = DATECHECK[4:8]
    y = y0 + 17
    for i, item in enumerate(left):
        d.text((x0 + 8, y + i * 9), "\u2022  " + item, font=f, fill=(52, 48, 40))
    for i, item in enumerate(right):
        d.text((x0 + 500, y + i * 9), "\u2022  " + item, font=f, fill=(52, 48, 40))

def draw_footer(d):
    d.line([(16, 942), (1008, 942)], fill=LINE, width=1)
    f = F("DejaVuSans.ttf", 8)
    d.text((16, 948),
           "All 36 stories happened or were first reported on Sunday 22 November 2026 (UTC). "
           "Sources named on each story; map markers numbered as the list.",
           font=f, fill=GREY)
    d.text((16, 960),
           "Drawn from live reporting: BBC, Reuters, AP, Politico, Euromaidan Press, "
           "Ukrainian Air Force, Lowy Institute, ESA, CNBC, Finnhub.",
           font=f, fill=GREY)
    d.text((1008, 960), "VeeGee27 \u00b7 make.fun", font=f, fill=GREY, anchor="ra")

# ---------------------------------------------------------------- main
def main():
    img = make_paper()
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_regions(d)
    draw_heroes(d)
    draw_mids(d)
    draw_map(d)
    draw_briefs(d)
    draw_datecheck(d)
    draw_footer(d)
    img.save("entry.png", format="PNG")
    print("wrote entry.png", img.size)

if __name__ == "__main__":
    main()
