#!/usr/bin/env python3
"""Deterministic English brain-puzzle Reel creator (original graphics and audio).

Requires Pillow and ffmpeg. No generative-API key and no third-party assets.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import wave
from datetime import date

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG_TOP = (9, 16, 39)
BG_BOTTOM = (27, 20, 62)
WHITE = (245, 249, 255)
MUTED = (169, 183, 215)
CYAN = (66, 235, 232)
PURPLE = (173, 124, 255)
YELLOW = (255, 214, 95)
DARK_CARD = (23, 34, 65)

FONTS = [
    ("/usr/share/fonts/truetype/lato/Lato-Heavy.ttf", "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
for heavy, regular in FONTS:
    if os.path.exists(heavy) and os.path.exists(regular):
        FONT_BOLD, FONT_REGULAR = heavy, regular
        break
else:
    raise RuntimeError("Install fonts-lato or fonts-dejavu-core")


def font(size: int, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def symbol_font(size: int):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def seed_for(day: str):
    return int.from_bytes(hashlib.sha256(("blinkpuzz-v2:" + day).encode()).digest()[:8], "big")


def build_puzzle(day: str):
    rd = random.Random(seed_for(day))
    kind = (date.fromisoformat(day).toordinal()) % 5
    if kind in (0, 1, 2):
        rows, cols = 7, 7
        ix = rd.randrange(2, rows * cols - 2)
        row, col = divmod(ix, cols)
        if kind == 0:
            normal, odd = rd.choice([("→", "←"), ("↑", "↓"), ("↗", "↖")])
            tag, title, sub = "ODD ONE OUT", "ONE ARROW IS DIFFERENT", "Find the reversed arrow."
        elif kind == 1:
            normal, odd = rd.choice([("6", "9"), ("8", "3"), ("5", "6"), ("2", "7")])
            tag, title, sub = "ODD ONE OUT", "FIND THE WRONG DIGIT", "One digit breaks the pattern."
        else:
            normal, odd = rd.choice([("●", "◆"), ("■", "◆"), ("◆", "●")])
            tag, title, sub = "VISUAL CHALLENGE", "SPOT THE ODD SHAPE", "Only one shape is different."
        grid = [[normal for _ in range(cols)] for _ in range(rows)]
        grid[row][col] = odd
        assert sum(v == odd for line in grid for v in line) == 1
        ans = f"{chr(65 + col)}{row+1}"
        return dict(kind="grid", title=title, tag=tag, subtitle=sub, grid=grid,
                    answer=ans, reveal=f"THE ODD ONE: {ans}", cell=(row, col),
                    detail="Look for the highlighted symbol.", normal=normal, odd=odd)
    if kind == 3:
        a, d, e = rd.randint(2, 12), rd.randint(2, 7), rd.randint(1, 4)
        nums = [a, a+d, a+2*d+e, a+3*d+3*e]
        assert nums[1]-nums[0] == d and nums[2]-nums[1] == d+e
        return dict(kind="sequence", title="WHAT NUMBER COMES NEXT?", tag="NUMBER PATTERN",
                    subtitle="Find the next number in the series.", items=[*nums[:3], "?"],
                    answer=str(nums[3]), reveal=f"ANSWER: {nums[3]}",
                    detail=f"The gaps grow: +{d}, +{d+e}, +{d+2*e}.")
    x, y, z = rd.sample(range(3, 12), 3)
    return dict(kind="equations", title="UNLOCK THE FINAL NUMBER", tag="MINI LOGIC TEST",
                subtitle="Each symbol has one value.", values=[2*x, x+y, y+z],
                x=x, y=y, z=z, answer=str(z), reveal=f"TRIANGLE = {z}",
                detail=f"Circle={x}, square={y}, triangle={z}.")


def gradient():
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(a*(1-t)+b*t) for a, b in zip(BG_TOP, BG_BOTTOM))
        d.line([(0, y), (W, y)], fill=c, width=1)
    d.ellipse((-250, 160, 320, 730), outline=(32, 53, 94), width=6)
    d.ellipse((840, 1200, 1400, 1800), outline=(48, 45, 93), width=6)
    return im


def center_text(draw, text, x, y, fnt, fill=WHITE, anchor="mm"):
    draw.text((x, y), text, font=fnt, fill=fill, anchor=anchor, stroke_width=0)


def rounded(draw, xy, fill=DARK_CARD, outline=None, width=1, rad=34):
    draw.rounded_rectangle(xy, radius=rad, fill=fill, outline=outline, width=width)


def draw_grid(draw, p, show_answer):
    rows, cols = len(p['grid']), len(p['grid'][0])
    left, top, step = 135, 670, 116
    for col in range(cols):
        center_text(draw, chr(65+col), left+col*step+48, top-66, font(30, True), MUTED)
    for row in range(rows):
        center_text(draw, str(row+1), left-60, top+row*step+48, font(30, True), MUTED)
        for col in range(cols):
            x = left+col*step
            y = top+row*step
            selected = show_answer and p['cell'] == (row, col)
            rounded(draw, (x, y, x+96, y+96),
                    fill=(35, 88, 112) if selected else (37, 47, 84),
                    outline=CYAN if selected else (51, 65, 108), width=5 if selected else 2,
                    rad=20)
            ch = p['grid'][row][col]
            center_text(draw, ch, x+48, y+46, symbol_font(56), YELLOW if selected else WHITE)
    if show_answer:
        r, c = p['cell']
        x, y = left+c*step, top+r*step
        draw.ellipse((x-12, y-12, x+108, y+108), outline=YELLOW, width=7)


def draw_sequence(draw, p, show_answer):
    x0, top, step = 142, 835, 208
    for i, v in enumerate(p['items']):
        x = x0+i*step
        selected = show_answer and i == 3
        rounded(draw, (x, top, x+172, top+180), fill=(30, 98, 107) if selected else (37, 47, 84),
                outline=CYAN if selected else (61, 71, 112), width=5 if selected else 2, rad=30)
        center_text(draw, str(p['answer'] if selected else v), x+86, top+88, font(87, True), YELLOW if selected else WHITE)
    center_text(draw, "Every gap follows a pattern", W//2, 1150, font(37), MUTED)


def draw_equations(draw, p, show_answer):
    rows = [("● + ●", p['values'][0]), ("● + ■", p['values'][1]), ("■ + ▲", p['values'][2]), ("▲", p['answer'] if show_answer else "?")]
    for i,(left,right) in enumerate(rows):
        y = 645 + 205*i
        selected = show_answer and i == 3
        rounded(draw, (155, y, 925, y+155), fill=(30, 98, 107) if selected else (37, 47, 84),
                outline=CYAN if selected else (58, 70, 112), width=5 if selected else 2,rad=30)
        draw.text((250, y+75), left, font=symbol_font(74), fill=YELLOW if selected else WHITE, anchor="lm")
        draw.text((865, y+75), "= " + str(right), font=font(69, True), fill=YELLOW if selected else CYAN, anchor="rm")


def frame(background, puzzle, seconds_remaining, show_answer):
    im = background.copy()
    d = ImageDraw.Draw(im)
    rounded(d, (75, 125, 1005, 184), fill=(35, 45, 81), rad=26)
    center_text(d, "BLINKPUZZ  /  DAILY BRAIN GAMES", W//2, 154, font(34, True), CYAN)
    center_text(d, puzzle['tag'], W//2, 286, font(34, True), PURPLE)
    headline = puzzle['title']
    if len(headline) > 24:
        words = headline.split()
        lines, current = [], ""
        for word in words:
            if len(current + " " + word) > 18 and current:
                lines.append(current)
                current = word
            else:
                current = (current + " " + word).strip()
        if current: lines.append(current)
        for i,line in enumerate(lines[:2]):
            center_text(d, line, W//2, 369+i*70, font(53, True), WHITE)
    else:
        center_text(d, headline, W//2, 398, font(56, True), WHITE)
    center_text(d, puzzle['subtitle'], W//2, 523, font(38), MUTED)
    if puzzle['kind'] == 'grid':
        draw_grid(d, puzzle, show_answer)
    elif puzzle['kind'] == 'sequence':
        draw_sequence(d, puzzle, show_answer)
    else:
        draw_equations(d, puzzle, show_answer)
    if show_answer:
        rounded(d, (96, 1516, 984, 1660), fill=(26, 92, 101), outline=CYAN, width=3, rad=30)
        center_text(d, puzzle['reveal'], W//2, 1577, font(54, True), CYAN)
        center_text(d, puzzle['detail'], W//2, 1632, font(27), WHITE)
    else:
        d.rounded_rectangle((116, 1540, 964, 1558), radius=9, fill=(60, 67, 103))
        fraction = seconds_remaining / 6
        d.rounded_rectangle((116, 1540, 116 + int(848 * fraction), 1558), radius=9, fill=CYAN)
        center_text(d, f"{seconds_remaining}", W//2, 1654, font(91, True), CYAN)
    center_text(d, "COMMENT YOUR ANSWER BEFORE THE REVEAL", W//2, 1727, font(30, True), MUTED)
    center_text(d, "@blinkpuzz  •  NEW CHALLENGE EVERY DAY", W//2, 1782, font(26), MUTED)
    return im


def audio_file(path: Path, seconds=8):
    sr = 24000
    total = int(seconds * sr)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        block = bytearray()
        for i in range(total):
            t = i/sr
            s = 0.0
            local = t % 1.0
            if t < 6 and local < 0.06:
                s += 0.075 * (1-local/0.06) * math.sin(2*math.pi*850*t)
            if 6 <= t < 6.5:
                s += 0.060 * (1-(t-6)/0.5) * (
                    math.sin(2*math.pi*659.25*t) + 0.5*math.sin(2*math.pi*987.77*t))
            block.extend(struct.pack('<h', round(max(-1,min(1,s))*32767)))
        w.writeframes(block)


def make_reel(day: str, output_dir: Path, quick=False):
    date.fromisoformat(day)
    puzzle = build_puzzle(day)
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / f'{day}.mp4'
    poster = output_dir / f'{day}.jpg'
    metadata = output_dir / f'{day}.json'
    bg = gradient()
    frame(bg, puzzle, 6, False).save(poster, quality=91, optimize=True)
    with tempfile.TemporaryDirectory(prefix='blinkpuzz-') as tmp:
        tmp = Path(tmp)
        duration = 8
        rows=[]
        for n in range(duration):
            pic = tmp / f'frame_{n:02d}.jpg'
            show = n >= 6
            pic_im = frame(bg, puzzle, max(1, 6-n), show)
            if quick:
                pic_im = pic_im.resize((540, 960))
            pic_im.save(pic, quality=87, optimize=True)
            rows.append(f"file '{pic.as_posix()}'\nduration 1")
        rows.append(f"file '{(tmp / 'frame_07.jpg').as_posix()}'")
        playlist = tmp/'concat.txt'
        playlist.write_text('\n'.join(rows)+'\n', encoding='utf-8')
        audio = tmp/'sound.wav'
        audio_file(audio)
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-safe", "0", "-f", "concat", "-i", str(playlist),
                   "-i", str(audio), "-t", "8", "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(dest)]
        subprocess.run(command, check=True)
    caption = (f"{puzzle['title']} 👀\n\n"
               f"Can you solve this before the timer runs out? Drop your answer below! 🧠\n\n"
               f"Follow @blinkpuzz for a fresh daily challenge.\n\n"
               f"#BrainTeaser #PuzzleChallenge #DailyPuzzle #MindGames #BlinkPuzz\n\n"
               f"Challenge ID: BP{day.replace('-', '')}")
    info = {
        "id": f"blinkpuzz-{day}", "date": day, "type": puzzle['kind'],
        "title": puzzle['title'], "answer": puzzle['answer'], "solution": puzzle['detail'],
        "caption": caption, "video": dest.name, "poster": poster.name,
        "duration_seconds": 8, "width": 540 if quick else W, "height": 960 if quick else H,
        "format": "vertical 9:16", "published": False
    }
    metadata.write_text(json.dumps(info, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    return info


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--date', default=date.today().isoformat(), help='YYYY-MM-DD')
    parser.add_argument('--out', type=Path, default=Path('docs/media'))
    parser.add_argument('--quick', action='store_true', help='Half-resolution smoke-test mode')
    args=parser.parse_args()
    data=make_reel(args.date, args.out, args.quick)
    print(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    main()
