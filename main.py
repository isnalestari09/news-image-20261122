#!/usr/bin/env python3
"""News Image 22 November 2026 - one-page newspaper, drawn in pure Python.

Writes /output/entry.png (or output/entry.png when /output does not exist):
a 1024x1024 PNG summing up Sunday 22 November 2026 in 36 stories.
Stdlib only, no network, no randomness, no timestamps: two runs produce
byte-identical output.

Every figure was verified against wire/agency reporting of 22 Nov 2026
(AP, Reuters, AFP, BBC, Anadolu, Al Jazeera, UKMTO, PHIVOLCS, HK Govt,
Cricinfo, F1.com, ATP, Sky, Guardian, RNZ, PANA, KWS, ANP). Nothing invented.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 244, 228)      # light cream page
PAPER2 = (241, 234, 210)     # slightly darker cream
INK = (28, 28, 28)
RED = (178, 38, 28)
BLUE = (30, 76, 120)         # deep blue for pins / accents
TEAL = (16, 104, 98)
GOLD = (176, 141, 60)
GREY = (118, 114, 102)
WHITE = (255, 255, 255)
SAND = (226, 208, 164)       # land on the map
SEA = (214, 228, 236)        # pale sea on the map
PINK = (255, 232, 226)       # date-check box
GREEN = (46, 125, 50)

# ---------------------------------------------------------------- 5x7 font
# Glyphs are 7 rows of 5 bits. Written out by hand for this program.
FONT = {
'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
'0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
'1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
'2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
'3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
'4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
'5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
'6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
'7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
'8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
'9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
't': ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
'.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
'!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
'?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
"'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
'"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
'(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
'-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
'\u2013': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
'\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
'/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
'%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
'&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
'+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
'$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
'#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
'@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
'*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
'=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
'<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
'>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
'[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
'_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
'\u00b0': ("00100", "01010", "00100", "00000", "00000", "00000", "00000"),
'\u2022': ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
'\u2019': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
'\u201c': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
'\u201d': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
'\u2192': ("00000", "00100", "00010", "11111", "00010", "00100", "00000"),
'\u00d7': ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
'~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
'^': ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- PNG writer
def _png_chunk(kind, data):
    blob = struct.pack(">I", len(data)) + kind + data
    blob += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return blob


def save_png(path, w, h, rgb):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(rgb[y * w * 3:(y + 1) * w * 3])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- drawing surface
class Page:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hrule(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vrule(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def segment(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            for xx in range(cx - half, cx + half + 1):
                self.dot(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for a in range(360):
            rad = math.radians(a)
            for rr in range(r - t + 1, r + 1):
                self.dot(cx + int(rr * math.cos(rad)),
                         cy + int(rr * math.sin(rad)), c)

    def fill_poly(self, pts, c):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.dot(x, y, c)


# ---------------------------------------------------------------- text
def glyph_w(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def put_text(pg, x, y, s, scale, c):
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            g = FONT.get(ch.upper(), FONT[' '])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '1':
                    pg.fill(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def put_centered(pg, cx, y, s, scale, c):
    put_text(pg, cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap_text(s, width, scale):
    """Greedy word wrap to a pixel width; returns the lines."""
    lines = []
    cur = ''
    for w in s.split(' '):
        trial = (cur + ' ' + w) if cur else w
        if text_w(trial, scale) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def put_wrapped(pg, x, y, s, width, scale, c, pitch=None):
    if pitch is None:
        pitch = 7 * scale + 2
    lines = wrap_text(s, width, scale)
    for i, ln in enumerate(lines):
        put_text(pg, x, y + i * pitch, ln, scale, c)
    return y + len(lines) * pitch

# ---------------------------------------------------------------- the day's news
# 36 stories = 3 heroes + 10 minis (4-13) + 23 ALSO items (14-36).
# Regions: EUROPE 5, MIDDLE EAST 6, ASIA 5, AMERICAS 6, AFRICA 8,
# OCEANIA 3, GLOBAL 3 = 36. Header count = numbered cards = region sum.

MASTHEAD_TITLE = "SUNDAY 22 NOVEMBER 2026"
MASTHEAD_SUB = "THE WORLD IN ONE PAGE"
MASTHEAD_COUNTS = "36 STORIES  -  7 REGIONS  -  11 FIELDS  -  PRESS TIME 23:00 UTC"

KPI = [
    ("186", "DRONES LAUNCHED", "Ukr Air Force"),
    ("161", "DOWNED / JAMMED", "Ukr Air Force"),
    ("35%", "CLEAN POWER 2035", "COP31 draft"),
    ("$120bn", "ADAPTATION DROPPED", "COP31 draft"),
    ("720/9", "INDIA DECLARED", "Cricinfo, Wellington"),
    ("98.79%", "HK TURNOUT, FINAL", "HK Govt"),
]

TIMELINE = [
    ("01:00", "HK POLLS OPEN"),
    ("05:11", "HAMAS SEEKS TALKS"),
    ("06:00", "161 OF 186 DOWNED"),
    ("10:00", "HK POLLS CLOSE"),
    ("15:56", "COP31: NO DEAL"),
    ("18:28", "LIVERPOOL 4-0 UTD"),
    ("21:55", "BAYELSA TOLL 29"),
]

HEROES = [
    {
        "kicker": "1  EUROPE  -  UKRAINE",
        "head": ["186 DRONES RAIN", "ON KYIV"],
        "body": ("Russia launched 186 drones overnight, 72 of them "
                 "jet-powered. Ukraine downed or jammed 161; 18 sites "
                 "were hit. In Dymer a block of flats was struck: "
                 "2 killed, 14 feared trapped."),
        "src": "UKR AIR FORCE / AP",
        "badge": "CONFIRMED",
        "kind": "drones",
    },
    {
        "kicker": "2  GLOBAL  -  CLIMATE",
        "head": ["COP31 COLLAPSES:", "NO DEAL"],
        "body": ("The EU, UK, Norway, Panama and island states rejected "
                 "a final text that never mentions fossil fuels. "
                 "President Kurum conceded no agreement. The draft kept "
                 "35% clean power by 2035 but dropped the $120bn target."),
        "src": "PHYS.ORG / NEWSBASE",
        "badge": "CONFIRMED",
        "kind": "cop",
    },
    {
        "kicker": "3  MIDDLE EAST  -  BAHRAIN",
        "head": ["IRAN CLAIMS", "BAHRAIN STRIKES"],
        "body": ("The Guards claim missile and drone strikes on two US "
                 "Patriot radars at al-Riffa and Awali. Bahrain says its "
                 "defences stopped several; a civilian site on Sitra "
                 "burned, 2 hurt. Washington: no damage to US forces."),
        "src": "SEPAH NEWS / REUTERS",
        "badge": "CLAIM",
        "kind": "gulf",
    },
]

MINIS = [
    ("4", "POLAND: 3 OBJECTS WERE KH-101 MISSILES",
     "Lublin prosecutors say the three objects that fell on Friday were "
     "Russian cruise missiles, made in late 2026. NATO meets Monday.",
     "REUTERS", "CONFIRMED", "shield"),
    ("5", "GAZA: HAMAS SEEKS URGENT TALKS",
     "A strike killed 3 soup-kitchen aid workers in Tel al-Hawa; Hamas "
     "seeks talks. Israel says the van carried militants.",
     "ANADOLU", "REPORTED", "star"),
    ("6", "WEST BANK: SETTLERS TORCH CARS, HOMES",
     "Settlers torched ~12 cars and homes in four villages overnight. "
     "No injuries. Eisenkot: 'Jewish terrorism.'",
     "REUTERS/AP", "REPORTED", "flag"),
    ("7", "LIBYA: BLAST SINKS RUSSIAN CORVETTE",
     "A suspected drone attack hit the Merkury at Benghazi naval base; the "
     "ship mostly sank, bow only. 10 slightly hurt.",
     "REUTERS", "REPORTED", "ship"),
    ("8", "CIKANDE: 24 BODY BAGS FROM FACTORY FIRE",
     "Police removed 24 body bags after Saturday's candy-factory fire. "
     "24 of 65 workers are home; 29 still missing.",
     "REUTERS", "REPORTED", "cross"),
    ("9", "HONG KONG: RECORD 98.79% TURNOUT",
     "Election Committee polls closed at 18:00 HKT with a record final "
     "turnout of 98.79%: 5,640 of 5,709 voters.",
     "HK GOVT", "OFFICIAL", "check"),
    ("10", "MANIPUR: 18 DEAD IN HOOCH TRAGEDY",
     "Spurious liquor in Chandel district killed 18 on Sunday; 228 are in "
     "hospital and 1,130 were screened.",
     "HINDUSTAN TIMES", "REPORTED", "cross"),
    ("11", "SPARTA II TOWED OUT OF FINNISH WATERS",
     "Rescue vessel Murman began towing the drone-hit Sparta II out Sunday; "
     "it left Finland's zone by evening. 16 crew safe.",
     "REUTERS", "REPORTED", "ship"),
    ("12", "IRAQ: POWER STATION FIRE KILLS 4",
     "A fire at the Hartha power station near Basra killed at least 4 and "
     "injured 35 on Saturday, reported Sunday.",
     "AL JAZEERA", "REPORTED", "bolt"),
    ("13", "DEMOCRATS CLINCH 258 HOUSE SEATS",
     "The 258th seat fell Sunday as Chuck Hubbard beat Virginia Foxx in N. "
     "Carolina by 330 votes of 287,000. Largest since 1992.",
     "AP", "CONFIRMED", "flag"),
]

ALSO = [
    ("14", "Verstappen wins Las Vegas GP; 35 lead changes, +0.639s", "F1.COM"),
    ("15", "Liverpool 4-0 Man Utd; Pochettino debut, Yoro off 8'", "SKY"),
    ("16", "Alcaraz beats Zverev 6-2, 7-6(7); first ATP Finals title", "ATP"),
    ("17", "Wembanyama 50 pts, 19 reb, 5 blk, 4 stl; Spurs 114-91", "AP"),
    ("18", "Two tankers hit in Hormuz Saturday; ~25 hit in a week", "UKMTO"),
    ("19", "Bayelsa boat toll rises to 29", "CHANNELS TV"),
    ("20", "S. Sudan: 21 killed in Tonj East cattle camp attack", "EYE RADIO"),
    ("21", "Sudan: drone strikes kill 5 children in Khartoum", "RADIO DABANGA"),
    ("22", "Gambia intercepts 491 would-be irregular migrants", "PANA"),
    ("23", "Philippines M5.3 quake off Sarangani, depth 83 km", "PHIVOLCS"),
    ("24", "Trump: will work with Democrats on 10% card cap", "AP"),
    ("25", "Hamas commander Abu Younis killed in Al-Mawasi strike", "BBC"),
    ("26", "Molly Meldrum dies aged 83", "GUARDIAN"),
    ("27", "UN chief: 'no ambiguity in the science' as COP31 fails", "PANA"),
    ("28", "Newspoll: Taylor leads Albanese 42-41 as preferred PM", "POLL BLUDGER"),
    ("29", "Brazil: Chamber to vote Lula fiscal bill Monday", "PARTICLE"),
    ("30", "Kenya: helicopter + drones join Aberdare hiker search", "KWS"),
    ("31", "Maori word 'kaitiakitanga' greets Berlin airport", "RNZ"),
    ("32", "Next COP: Addis Ababa, 8-19 Nov 2027", "AP"),
    ("33", "Trump: 'I could veto everything for two years'", "FOX NEWS"),
    ("34", "S. Africa honours Mlambo-Ngcuka; state funeral 28 Nov", "PRESIDENCY"),
    ("35", "India 720/9 dec in Wellington, highest Test total in NZ", "CRICINFO"),
    ("36", "Niger: 215 youths return from training in Algeria", "ANP"),
]

DATECHECK = ("DATE CHECK  -  LEFT OUT, FIRST REPORTED BEFORE SUNDAY: "
             "400-drone barrage (20 Nov); Kryvyi Rih double-tap (21 Nov); "
             "'El Chapo Isidro' captured (21 Nov); Nigeria boat capsized "
             "(21 Nov); BepiColombo (21 Nov); Sparta II strike (21 Nov); "
             "Peru M6.7 quake (20 Nov); EU-Indonesia pact (21 Nov); "
             "ICJ Myanmar ruling (19 Nov); FBI NCIC hack (20 Nov).  "
             "NOT YET, AFTER SUNDAY: Estonia border closure (1 Dec); "
             "Belgian strike (Mon 23 Nov); Brazil vote (Mon); Cikande "
             "search resumes (Mon); NATO meets (Mon); India-NZ Test day 5 "
             "(Mon); US Congress returns (30 Nov); NZ result (27 Nov).")

REGION_LINE = ("EUROPE 5  -  MIDDLE EAST 6  -  ASIA 5  -  AMERICAS 6  -  "
               "AFRICA 8  -  OCEANIA 3  -  GLOBAL 3  =  36 STORIES")
LEGEND = ("CONFIRMED on the record  |  OFFICIAL on-the-record  |  REPORTED "
          "one outlet  |  CLAIM one side's claim  |  FORECAST not yet happened")
SOURCES = ("Sources: AP, Reuters, AFP, BBC, Anadolu, Al Jazeera, UKMTO, "
           "PHIVOLCS, HK Govt, Cricinfo, F1.com, ATP, Sky, Guardian, RNZ, "
           "PANA, KWS, ANP  -  Original drawings.")
ATTEST = ("Every story here happened, or was first reported, on Sunday "
          "22 November 2026. Counts are attributed to their sources.")

# ---------------------------------------------------------------- illustrations
def starburst(pg, cx, cy, r, c):
    for a in range(0, 360, 30):
        x2 = cx + int(r * math.cos(math.radians(a)))
        y2 = cy + int(r * math.sin(math.radians(a)))
        pg.segment(cx, cy, x2, y2, c)
    pg.disc(cx, cy, max(2, r // 3), c)


def hero_art(pg, x, y, w, h, kind):
    pg.fill(x, y, w, h, WHITE)
    pg.frame(x, y, w, h, INK, 2)
    if kind == "drones":
        # Night sky over Kyiv: drone dots, arcs, one blast over the city.
        pg.fill(x + 2, y + 2, w - 4, h - 4, (26, 32, 54))
        for i in range(12):
            dx = x + 16 + i * 26
            dy = y + 12 + ((i * 29) % 34)
            pg.disc(dx, dy, 2, (247, 220, 110))
            pg.segment(dx - 5, dy, dx + 5, dy, (247, 220, 110))
        for i in range(9):
            bx = x + 10 + i * 36
            bh = 26 + ((i * 41) % 44)
            pg.fill(bx, y + h - 6 - bh, 28, bh, (52, 58, 86))
            for wy in range(y + h - 6 - bh + 6, y + h - 10, 11):
                pg.fill(bx + 5, wy, 3, 3, (247, 220, 110))
                pg.fill(bx + 18, wy, 3, 3, (247, 220, 110))
        pg.segment(x + 60, y + 8, x + 190, y + 74, RED)
        pg.segment(x + 290, y + 6, x + 215, y + 72, RED)
        starburst(pg, x + 200, y + 78, 18, (255, 150, 50))
        pg.disc(x + 200, y + 78, 4, (255, 210, 90))
        put_text(pg, x + 8, y + 8, "KYIV  -  NIGHT", 1, (247, 220, 110))
        put_text(pg, x + 8, y + h - 18, "DYMER: 2 KILLED, 14 TRAPPED", 1, WHITE)
    elif kind == "cop":
        # Antalya: globe and leaf, the draft's dropped $120bn, NO DEAL stamp.
        pg.fill(x + 2, y + 2, w - 4, h - 4, (233, 240, 228))
        pg.disc(x + 58, y + 52, 34, (120, 180, 140))
        pg.fill_poly([(x + 28, y + 52), (x + 48, y + 28), (x + 68, y + 38),
                      (x + 88, y + 52), (x + 68, y + 78), (x + 44, y + 76)],
                     TEAL)
        put_text(pg, x + 28, y + 94, "ANTALYA", 1, INK)
        bx = x + 138
        pg.fill(bx, y + 20, 66, 13, RED)
        pg.fill(bx + 78, y + 20, 66, 13, GREY)
        put_text(pg, bx, y + 6, "DRAFT 1", 1, INK)
        put_text(pg, bx + 78, y + 6, "FINAL", 1, INK)
        put_text(pg, bx + 8, y + 23, "2", 1, WHITE)
        put_text(pg, bx + 86, y + 23, "0", 1, WHITE)
        put_text(pg, bx, y + 42, "FOSSIL-FUEL", 1, INK)
        put_text(pg, bx, y + 52, "MENTIONS: 2 > 0", 1, RED)
        put_text(pg, bx, y + 70, "$120bn", 2, RED)
        put_text(pg, bx, y + 86, "DROPPED", 2, RED)
        put_text(pg, x + 8, y + h - 18, "LONGEST COP EVER: NO DEAL", 1, RED)
    else:
        # Gulf of Bahrain: sea, coast, island, two claimed strike points.
        pg.fill(x + 2, y + 2, w - 4, h - 4, (183, 214, 232))
        coast = [(x + 20, y + h - 4), (x + 60, y + 88), (x + 90, y + 58),
                 (x + 130, y + 68), (x + 170, y + 38), (x + 210, y + 28),
                 (x + 250, y + 48), (x + w - 4, y + 18), (x + w - 4, y + h - 4)]
        pg.fill_poly(coast, SAND)
        pg.disc(x + 150, y + 52, 8, SAND)
        pg.ring(x + 150, y + 52, 8, INK, 1)
        put_text(pg, x + 164, y + 45, "BAHRAIN", 1, INK)
        pg.disc(x + 118, y + 92, 5, BLUE)
        pg.disc(x + 184, y + 78, 5, BLUE)
        starburst(pg, x + 118, y + 92, 13, BLUE)
        starburst(pg, x + 184, y + 78, 13, BLUE)
        put_text(pg, x + 92, y + 108, "al-Riffa", 1, INK)
        put_text(pg, x + 168, y + 96, "Awali", 1, INK)
        put_text(pg, x + 8, y + 8, "GULF OF BAHRAIN", 1, BLUE)


def mini_icon(pg, x, y, w, h, kind):
    pg.fill(x, y, w, h, PAPER2)
    pg.frame(x, y, w, h, INK, 1)
    cx, cy = x + w // 2, y + h // 2
    if kind == "star":
        starburst(pg, cx, cy, 11, GOLD)
    elif kind == "ship":
        pg.fill_poly([(x + 7, y + 20), (x + w - 7, y + 20), (x + w - 12, y + 29),
                      (x + 12, y + 29)], BLUE)
        pg.fill(cx - 3, y + 9, 6, 11, INK)
        starburst(pg, x + w - 12, y + 11, 7, RED)
        pg.segment(x + 4, y + 32, x + w - 4, y + 32, BLUE)
    elif kind == "quake":
        pg.fill_poly([(x + 4, y + 28), (x + 15, y + 9), (x + 25, y + 28)], GREY)
        pg.fill_poly([(x + 21, y + 28), (x + 34, y + 13), (x + 45, y + 28)],
                     (90, 90, 90))
        pg.segment(x + 4, y + 31, x + w - 4, y + 31, RED)
    elif kind == "chart":
        pg.segment(x + 5, y + 8, x + w - 5, y + 28, RED)
        pg.segment(x + 5, y + 8, x + 14, y + 12, RED)
        pg.segment(x + 14, y + 12, x + 24, y + 10, RED)
        pg.segment(x + 24, y + 10, x + w - 5, y + 28, RED)
        pg.disc(x + w - 5, y + 28, 3, RED)
    elif kind == "cross":
        pg.fill(cx - 3, y + 5, 6, 22, RED)
        pg.fill(cx - 10, y + 12, 20, 6, RED)
    elif kind == "shield":
        pg.fill_poly([(cx - 11, y + 5), (cx + 11, y + 5), (cx + 11, y + 20),
                      (cx, y + 30), (cx - 11, y + 20)], BLUE)
        put_text(pg, cx - 7, y + 11, "PL", 1, WHITE)
    elif kind == "flag":
        pg.fill(x + 7, y + 5, w - 14, h - 10, BLUE)
        pg.fill(cx - 2, y + 5, 4, h - 10, (247, 220, 110))
        pg.fill(x + 7, cy - 2, w - 14, 4, (247, 220, 110))
    elif kind == "ball":
        pg.disc(cx, cy, 11, (200, 100, 40))
        pg.ring(cx, cy, 11, INK, 1)
        pg.segment(cx - 11, cy, cx + 11, cy, INK)
        pg.segment(cx, cy - 11, cx, cy + 11, INK)
    elif kind == "check":
        pg.fill(x + 6, y + 6, w - 12, h - 12, WHITE)
        pg.frame(x + 6, y + 6, w - 12, h - 12, INK, 1)
        pg.segment(x + 11, cy, cx - 2, cy + 7, GREEN)
        pg.segment(cx - 2, cy + 7, x + w - 11, y + 10, GREEN)
    elif kind == "bolt":
        pg.fill_poly([(cx + 2, y + 4), (cx - 8, y + 18), (cx - 1, y + 18),
                      (cx - 4, y + 30), (cx + 8, y + 14), (cx + 1, y + 14)],
                     GOLD)


# ---------------------------------------------------------------- world map
# Coarse continent outlines (lon, lat), drawn on a light-cream sea.
LAND = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 70), (-80, 68), (-60, 60),
     (-55, 47), (-70, 42), (-80, 32), (-90, 20), (-97, 16), (-105, 20),
     (-117, 32), (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-55, 60), (-40, 64), (-30, 68), (-20, 70), (-30, 74), (-45, 76),
     (-58, 74), (-60, 68)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-55, -35), (-65, -40), (-70, -50), (-73, -40), (-75, -25),
     (-80, -15), (-81, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (28, 66), (25, 70),
     (18, 69), (12, 65), (5, 60), (-5, 58), (-10, 50), (-10, 43)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 20), (43, 12), (48, 10), (51, 12), (44, 0), (40, -10), (35, -20),
     (32, -28), (25, -33), (18, -35), (15, -27), (12, -18), (9, -2),
     (9, 4), (-8, 5), (-13, 8)],
    [(30, 62), (40, 68), (60, 70), (80, 72), (100, 72), (120, 73),
     (140, 72), (160, 70), (178, 66), (170, 60), (160, 55), (140, 50),
     (130, 42), (127, 35), (122, 30), (120, 25), (110, 20), (105, 10),
     (100, 8), (98, 15), (95, 20), (90, 22), (85, 20), (80, 15), (77, 8),
     (75, 12), (70, 20), (65, 25), (60, 25), (55, 28), (50, 30), (48, 30),
     (43, 38), (40, 42), (35, 42), (30, 45), (28, 50), (30, 55)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -25),
     (146, -20), (142, -15), (140, -12), (135, -12), (132, -11), (130, -13),
     (126, -14), (122, -17), (118, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (140, 36), (141, 39),
     (141, 42), (143, 44), (140, 43), (138, 38), (135, 34)],
]

# (lon, lat, story number, label dx, label dy)
PINS = [
    (30.5, 50.4, "1", 0, -18),
    (30.7, 36.9, "2", -16, 20),
    (50.6, 26.2, "3", 24, -14),
    (22.5, 51.2, "4", -30, 14),
    (34.5, 31.5, "5", 10, 22),
    (20.1, 32.1, "7", -40, 16),
    (106.3, -6.3, "8", 0, 16),
    (114.2, 22.3, "9", 20, -16),
    (94.0, 24.4, "10", -14, 18),
    (24.0, 59.5, "11", -34, -12),
    (47.8, 30.5, "12", 26, 16),
    (-77.0, 38.9, "13", 18, -14),
    (-115.1, 36.2, "14", -20, 14),
]


def lonlat(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180.0) / 360.0 * w,
            y0 + (80.0 - lat) / 135.0 * h)

# ---------------------------------------------------------------- layout
def draw_masthead(pg):
    put_centered(pg, W // 2, 8, MASTHEAD_TITLE, 5, INK)
    put_centered(pg, W // 2, 50, MASTHEAD_SUB, 2, RED)
    put_centered(pg, W // 2, 68, MASTHEAD_COUNTS, 1, INK)
    pg.hrule(12, 86, W - 24, INK, 3)


def draw_kpi(pg, y):
    cw = (W - 24) // 6
    for i, (num, lab, sub) in enumerate(KPI):
        x = 12 + i * cw
        pg.fill(x + 2, y, cw - 4, 52, WHITE)
        pg.frame(x + 2, y, cw - 4, 52, INK, 1)
        put_centered(pg, x + cw // 2, y + 4, num, 3, RED)
        put_centered(pg, x + cw // 2, y + 30, lab, 1, INK)
        put_centered(pg, x + cw // 2, y + 41, sub, 1, GREY)
    pg.hrule(12, y + 56, W - 24, INK, 1)


def draw_timeline(pg, y):
    put_text(pg, 12, y, "SUNDAY, UTC", 1, GREY)
    x0, x1 = 240, W - 70
    pg.hrule(x0, y + 16, x1 - x0, INK, 2)
    n = len(TIMELINE)
    for i, (t, lab) in enumerate(TIMELINE):
        cx = x0 + (x1 - x0) * i // (n - 1)
        pg.disc(cx, y + 16, 4, RED)
        put_centered(pg, cx, y, t, 2, INK)
        put_centered(pg, cx, y + 24, lab, 1, INK)


def draw_hero(pg, x, y, w, hero):
    put_text(pg, x, y, hero["kicker"], 1, RED)
    yy = y + 12
    for ln in hero["head"]:
        put_text(pg, x, yy, ln, 3, INK)
        yy += 21
    hero_art(pg, x, yy + 4, w, 124, hero["kind"])
    yb = yy + 4 + 124 + 6
    yb = put_wrapped(pg, x, yb, hero["body"], w, 1, INK, pitch=9) + 4
    put_text(pg, x, yb + 2, "Source: " + hero["src"], 1, GREY)
    bw = text_w(hero["badge"], 1) + 8
    bx = x + w - bw
    pg.fill(bx, yb, bw, 10, RED)
    put_text(pg, bx + 4, yb + 1, hero["badge"], 1, WHITE)


def draw_mini(pg, x, y, w, num, head, body, src, status, kind):
    mini_icon(pg, x, y, w, 32, kind)
    put_wrapped(pg, x, y + 36, num + ". " + head, w, 1, INK, pitch=9)
    put_wrapped(pg, x, y + 56, body, w, 1, INK, pitch=9)
    put_text(pg, x, y + 94, src + "  -  " + status, 1, GREY)


def draw_map(pg, y):
    put_text(pg, 12, y, "WHERE IT HAPPENED  -  13 STORIES PINNED", 2, INK)
    mx, my, mw, mh = 12, y + 18, W - 24, 104
    pg.fill(mx, my, mw, mh, SEA)
    pg.frame(mx, my, mw, mh, INK, 1)
    for lon in range(-150, 181, 30):
        gx, _ = lonlat(lon, 0, mx, my, mw, mh)
        pg.vrule(int(gx), my, mh, (198, 214, 226), 1)
    for lat in (-30, 0, 30, 60):
        _, gy = lonlat(0, lat, mx, my, mw, mh)
        pg.hrule(mx, int(gy), mw, (198, 214, 226), 1)
    for poly in LAND:
        pts = [lonlat(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        pg.fill_poly([(int(px), int(py)) for px, py in pts], SAND)
    for lon, lat, lab, dx, dy in PINS:
        px, py = lonlat(lon, lat, mx, my, mw, mh)
        px, py = int(px), int(py)
        qx, qy = px + dx, py + dy
        if dx or dy:
            pg.segment(px, py, qx, qy, INK)
        pg.disc(px, py, 2, BLUE)
        pg.disc(qx, qy, 6, BLUE)
        pg.ring(qx, qy, 6, WHITE, 1)
        tw = text_w(lab, 1)
        put_text(pg, qx - tw // 2, qy - 3, lab, 1, WHITE)
    put_centered(pg, W // 2, my + mh + 4, REGION_LINE, 1, INK)


def draw_also(pg, y):
    put_text(pg, 12, y, "ALSO ON SUNDAY 22 NOVEMBER", 2, RED)
    pg.hrule(12, y + 16, W - 24, INK, 1)
    colw = (W - 24) // 2
    for i, (num, txt, src) in enumerate(ALSO):
        col = i // 12
        row = i % 12
        x = 12 + col * colw
        yy = y + 22 + row * 11
        put_text(pg, x, yy, num + ". " + txt + "  [" + src + "]", 1, INK)


def draw_datecheck(pg, y):
    pg.fill(12, y, W - 24, 48, PINK)
    pg.frame(12, y, W - 24, 48, RED, 2)
    put_wrapped(pg, 20, y + 4, DATECHECK, W - 40, 1, INK, pitch=8)


def draw_footer(pg, y):
    put_centered(pg, W // 2, y, LEGEND, 1, INK)
    put_centered(pg, W // 2, y + 8, SOURCES, 1, GREY)
    put_centered(pg, W // 2, y + 16, ATTEST, 1, GREY)


# ---------------------------------------------------------------- main
def main():
    pg = Page(W, H, PAPER)
    draw_masthead(pg)
    draw_kpi(pg, 94)
    draw_timeline(pg, 156)
    hw = (W - 24 - 2 * 12) // 3
    for i, hero in enumerate(HEROES):
        draw_hero(pg, 12 + i * (hw + 12), 194, hw, hero)
    mw = (W - 24 - 4 * 10) // 5
    for i, (num, head, body, src, status, kind) in enumerate(MINIS):
        col, row = i % 5, i // 5
        draw_mini(pg, 12 + col * (mw + 10), 437 + row * 104, mw,
                  num, head, body, src, status, kind)
    draw_map(pg, 653)
    draw_also(pg, 788)
    draw_datecheck(pg, 944)
    draw_footer(pg, 998)
    outdir = "/output" if os.path.isdir("/output") else "output"
    if outdir == "output":
        os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    save_png(path, W, H, pg.buf)
    print("wrote %s (%d bytes, %dx%d)" % (path, os.path.getsize(path), W, H))


if __name__ == "__main__":
    main()
