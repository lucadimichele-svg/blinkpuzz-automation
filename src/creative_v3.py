#!/usr/bin/env python3
"""BlinkPuzz Creative v3: independent, original puzzle formats and visual styles.

No external stock images, AI API, branded assets, lyrics or copyrighted audio.
Each challenge uses a deterministic seed and an independently checked answer.
"""
import hashlib
import json
import math
import random
import struct
import subprocess
import tempfile
import wave
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
KINDS = ('odd', 'sequence', 'math', 'missing', 'code', 'compare', 'memory', 'door')
OFFSETS = {'': 0, 'B1': 1, 'B2': 3, 'B3': 5, 'N1': 2}
THEMES = {
    'odd':      ((7, 31, 44),  (5, 64, 73),   (72, 247, 204), (249, 222, 84)),
    'sequence': ((39, 16, 44), (85, 31, 58),  (255, 134, 136), (255, 219, 151)),
    'math':     ((29, 24, 12), (78, 56, 16),  (255, 203, 75), (255, 244, 191)),
    'missing':  ((17, 19, 55), (43, 38, 102), (174, 148, 255), (118, 241, 239)),
    'code':     ((38, 15, 40), (78, 17, 84),  (255, 118, 209), (146, 244, 237)),
    'compare':  ((11, 24, 59), (16, 56, 109), (95, 175, 255), (252, 155, 123)),
    'memory':   ((10, 38, 31), (15, 83, 66),  (121, 252, 181), (248, 238, 128)),
    'door':     ((44, 19, 19), (101, 38, 21), (255, 155, 94), (244, 226, 164)),
}
WHITE = (248, 250, 255)
MUTED = (202, 210, 230)
HEAVY = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for path in (HEAVY, REGULAR):
    if not Path(path).is_file():
        raise RuntimeError('Install fonts-dejavu-core')


def ft(px, bold=False):
    return ImageFont.truetype(HEAVY if bold else REGULAR, px)


def tint(color, amount):
    return tuple(max(0, min(255, int(c*amount))) for c in color)


def seed(day, variant):
    s = 'blinkpuzz-creative-v3:' + day + ':' + variant
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], 'big')


def build_puzzle(day, variant=''):
    date.fromisoformat(day)
    if variant not in OFFSETS:
        raise ValueError('Unknown variant ' + variant)
    rng = random.Random(seed(day, variant))
    kind = KINDS[(date.fromisoformat(day).toordinal()*3 + OFFSETS[variant]) % len(KINDS)]
    p = {'kind': kind, 'creative_version': 'v3', 'day': day, 'slot': variant or 'base'}
    if kind == 'odd':
        normal, odd = rng.choice([('●', '◆'), ('▲', '▼'), ('◆', '■'), ('↑', '↗')])
        index = rng.randrange(25)
        p.update(title='SPOT THE ONE THAT CHANGED', subtitle='One tile is different. Where?',
                 tag='EAGLE EYES', normal=normal, odd=odd, index=index,
                 answer=f'{chr(65+index%5)}{index//5+1}',
                 detail='Different symbol at ' + f'{chr(65+index%5)}{index//5+1}')
    elif kind == 'sequence':
        first, step = rng.randint(2, 14), rng.randint(3, 9)
        nums = [first+step*i for i in range(5)]
        p.update(title='WHAT COMES NEXT?', subtitle='Follow the number pattern',
                 tag='NUMBER RUSH', numbers=nums[:4], step=step, answer=str(nums[4]),
                 detail=f'Add {step} each time')
    elif kind == 'math':
        a, b, c = rng.randint(4, 19), rng.randint(2, 9), rng.randint(2, 7)
        p.update(title='DON’T FALL FOR THIS', subtitle='Do multiplication first',
                 tag='MATH TRAP', a=a, b=b, c=c, answer=str(a+b*c),
                 detail=f'{b} × {c} = {b*c}, then + {a}')
    elif kind == 'missing':
        pairs = [[rng.randint(2, 11),rng.randint(2, 11)] for _ in range(3)]
        grid = [[a,b,a+b] for a,b in pairs]
        p.update(title='COMPLETE THE LAST ROW', subtitle='The same rule works for each row',
                 tag='MISSING NUMBER', matrix=grid, answer=str(grid[2][2]),
                 detail=f'{grid[2][0]} + {grid[2][1]} = {grid[2][2]}')
    elif kind == 'code':
        circle, triangle = rng.sample(range(3, 12), 2)
        p.update(title='UNLOCK THE SHAPE', subtitle='What is the triangle worth?',
                 tag='LOGIC LOCK', circle=circle, triangle=triangle,
                 answer=str(triangle), detail=f'● = {circle}; ▲ = {triangle}')
    elif kind == 'compare':
        while True:
            a,b,c,d = [rng.randint(3, 12) for _ in range(4)]
            left, right = a+b, c*d
            if left != right and abs(left-right) <= 20:
                break
        p.update(title='WHICH SIDE WINS?', subtitle='Choose A or B before the reveal',
                 tag='FAST COMPARISON', left=f'{a} + {b}', right=f'{c} × {d}',
                 left_value=left, right_value=right,
                 answer='A' if left>right else 'B', detail=f'A = {left}  |  B = {right}')
    elif kind == 'memory':
        digits = rng.sample(range(1, 10), 5)
        target_index = rng.randint(1, 3)
        p.update(title='REMEMBER THIS ORDER', subtitle='Memorize the five digits',
                 tag='MEMORY FLASH', digits=digits, target_index=target_index,
                 answer=str(digits[target_index]),
                 detail=f'Position {target_index+1} was {digits[target_index]}')
    else:
        factor = rng.choice([3, 4, 5, 7])
        correct = factor*rng.randint(3, 9)
        others = []
        while len(others)<3:
            n = rng.randint(13, 69)
            if n % factor and n not in others and n != correct:
                others.append(n)
        values = others + [correct]
        rng.shuffle(values)
        pos = values.index(correct)
        p.update(title='PICK THE RIGHT DOOR', subtitle=f'Which number is divisible by {factor}?',
                 tag='ONE RIGHT ANSWER', factor=factor, doors=values, index=pos,
                 answer='ABCD'[pos], detail=f'{correct} ÷ {factor} = {correct//factor}')
    validate_puzzle(p)
    return p


def validate_puzzle(p):
    kind, a = p['kind'], p['answer']
    if kind == 'odd':
        assert p['normal'] != p['odd'] and 0 <= p['index'] < 25
        assert a == chr(65+p['index']%5)+str(p['index']//5+1)
    elif kind == 'sequence':
        nums = p['numbers']; assert len(nums)==4
        assert all(nums[i+1]-nums[i] == p['step'] for i in range(3))
        assert int(a) == nums[-1]+p['step']
    elif kind == 'math':
        assert int(a)==p['a']+p['b']*p['c']
    elif kind == 'missing':
        assert len(p['matrix'])==3
        assert all(x+y==z for x,y,z in p['matrix'])
        assert int(a)==p['matrix'][-1][-1]
    elif kind == 'code':
        assert 2*p['circle'] > 0
        assert (p['circle']+p['triangle'])-p['circle']==int(a)
    elif kind == 'compare':
        assert p['left_value']!=p['right_value']
        assert a==('A' if p['left_value']>p['right_value'] else 'B')
    elif kind == 'memory':
        assert len(set(p['digits']))==5
        assert a==str(p['digits'][p['target_index']])
    elif kind == 'door':
        assert sum(x%p['factor']==0 for x in p['doors'])==1
        assert p['doors']['ABCD'.index(a)]%p['factor']==0
    else:
        raise AssertionError('Unsupported puzzle kind')
    return True


def text(d, label, x, y, size, color=WHITE, bold=False):
    d.text((x,y), str(label), font=ft(size,bold), fill=color, anchor='mm')


def card(d, coords, fill, outline=None, radius=32, width=3):
    d.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def background(kind):
    base, bottom, accent, secondary = THEMES[kind]
    img = Image.new('RGB',(W,H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        f=y/H
        rgb=tuple(int(base[k]*(1-f)+bottom[k]*f) for k in range(3))
        d.line((0,y,W,y),fill=rgb)
    # Abstract original motifs: no stock/vector artwork.
    for step in range(4):
        d.arc((780-step*40,-210-step*40,1280+step*40,320+step*40),
              start=30,end=170,fill=tint(accent,0.20),width=4)
    for step in range(4):
        d.arc((-310-step*40,1230-step*40,160+step*40,1770+step*40),
              start=210,end=345,fill=tint(secondary,0.25),width=4)
    return img


def heading(d,p,accent,secondary):
    card(d,(75,128,1005,202),fill=(18,25,48),outline=tint(accent,0.65),radius=22,width=2)
    text(d,'BLINKPUZZ',265,166,38,WHITE,True)
    text(d,'DAILY BRAIN GAMES',785,166,26,accent,True)
    card(d,(285,265,795,324),fill=tint(accent,0.26),outline=accent,radius=26,width=2)
    text(d,p['tag'],540,293,28,WHITE,True)
    title=p['title']
    if len(title)>23:
        words=title.split(); lines=[]; chunk=''
        for word in words:
            candidate=(chunk+' '+word).strip()
            if len(candidate)>20 and chunk:
                lines.append(chunk);chunk=word
            else:
                chunk=candidate
        if chunk:lines.append(chunk)
        for i,line in enumerate(lines[:2]):
            text(d,line,540,407+i*79,57,WHITE,True)
    else:
        text(d,title,540,435,62,WHITE,True)
    text(d,p['subtitle'],540,558,34,MUTED,False)
    # Identity stripe for a visible thumbnail difference.
    d.rounded_rectangle((190,611,890,625),radius=7,fill=accent)


def puzzle_visual(d,p,phase,accent,secondary):
    k=p['kind']
    showing=phase=='reveal'
    if k=='odd':
        for i in range(25):
            x=162+(i%5)*154; y=678+(i//5)*146
            chosen=showing and i==p['index']
            card(d,(x,y,x+132,y+126),fill=tint(accent,0.45) if chosen else (30,44,64),
                 outline=secondary if chosen else tint(accent,0.64),radius=18,width=5 if chosen else 2)
            text(d,p['odd'] if i==p['index'] else p['normal'],x+66,y+63,69,secondary if chosen else WHITE,True)
        for i in range(5):
            text(d,'ABCDE'[i],229+i*154,645,26,accent,True)
            text(d,str(i+1),120,742+i*146,26,accent,True)
    elif k=='sequence':
        for i,val in enumerate(p['numbers']+[p['answer'] if showing else '?']):
            x=64+i*194
            card(d,(x,825,x+179,1018),fill=tint(accent,0.41) if i==4 else (35,35,59),
                 outline=accent if i==4 else tint(accent,0.63),radius=29,width=4)
            text(d,val,x+89,916,69 if len(str(val))<=2 else 56,WHITE if i<4 else secondary,True)
        text(d,'FIND THE RULE',540,1170,48,accent,True)
    elif k=='math':
        card(d,(96,785,984,1160),fill=(39,37,46),outline=accent,radius=40,width=4)
        expression=f"{p['a']} + {p['b']} × {p['c']}"
        text(d,expression,540,968,111,WHITE,True)
        text(d,'= ' + (p['answer'] if showing else '?'),540,1291,89,secondary,True)
    elif k=='missing':
        for row in range(3):
            for col in range(3):
                x=230+col*220;y=687+row*223
                target=row==2 and col==2
                val='?' if target and not showing else str(p['matrix'][row][col])
                card(d,(x,y,x+190,y+186),fill=tint(accent,.37) if target else (32,35,73),
                     outline=accent if target else tint(accent,.63),radius=28,width=4)
                text(d,val,x+95,y+90,79,secondary if target else WHITE,True)
    elif k=='code':
        rows=[('● + ●',str(2*p['circle'])),('● + ▲',str(p['circle']+p['triangle'])),
              ('▲',p['answer'] if showing else '?')]
        for i,(left,right) in enumerate(rows):
            y=720+i*221
            card(d,(130,y,950,y+172),fill=tint(accent,.35) if i==2 else (55,29,64),
                 outline=accent if i==2 else tint(secondary,.6),radius=32)
            text(d,left,372,y+83,78,WHITE,True)
            text(d,'= '+right,769,y+83,77,secondary,True)
    elif k=='compare':
        for i,(lbl,val) in enumerate((('A',p['left']),('B',p['right']))):
            x=90+475*i
            chosen=showing and p['answer']==lbl
            card(d,(x,776,x+425,1229),fill=tint(accent,.34) if chosen else (23,53,86),
                 outline=secondary if chosen else accent,radius=37,width=6 if chosen else 3)
            text(d,lbl,x+212,857,100,secondary if chosen else accent,True)
            text(d,val,x+212,1022,69,WHITE,True)
        text(d,'BIGGER RESULT WINS',540,1345,38,secondary,True)
    elif k=='memory':
        if phase=='memorize':
            digits=[str(v) for v in p['digits']]
            title='MEMORIZE THESE FIVE DIGITS'
        elif phase=='ask':
            digits=['?' for _ in p['digits']]
            title=f"WHAT WAS POSITION {p['target_index']+1}?"
        else:
            digits=['·' for _ in p['digits']]
            digits[p['target_index']]=p['answer']
            title='THIS WAS THE NUMBER'
        text(d,title,540,758,43,accent,True)
        for i,val in enumerate(digits):
            x=70+i*194
            chosen=showing and i==p['target_index']
            card(d,(x,861,x+176,1126),fill=tint(accent,.40) if chosen else (26,62,57),
                 outline=secondary if chosen else accent,radius=29,width=5)
            text(d,val,x+88,983,87,secondary if chosen else WHITE,True)
            text(d,str(i+1),x+88,1164,35,MUTED,True)
    elif k=='door':
        for i,n in enumerate(p['doors']):
            x=77+i*241
            chosen=showing and i==p['index']
            card(d,(x,778,x+204,1209),fill=tint(accent,.36) if chosen else (72,37,35),
                 outline=secondary if chosen else accent,radius=35,width=5 if chosen else 3)
            card(d,(x+28,805,x+176,875),fill=tint(accent,.33),radius=20)
            text(d,'ABCD'[i],x+102,839,42,WHITE,True)
            text(d,str(n),x+102,1030,78,secondary if chosen else WHITE,True)
        text(d,'ONLY ONE MATCHES',540,1323,42,secondary,True)


def render(p,second):
    kind=p['kind']
    _,_,accent,secondary=THEMES[kind]
    img=background(kind)
    d=ImageDraw.Draw(img)
    heading(d,p,accent,secondary)
    phase='reveal' if second>=6 else ('memorize' if kind=='memory' and second<3 else 'ask')
    puzzle_visual(d,p,phase,accent,secondary)
    if phase=='reveal':
        card(d,(106,1452,974,1619),fill=(17,35,50),outline=secondary,radius=37,width=4)
        text(d,'ANSWER: '+p['answer'],540,1505,55,secondary,True)
        text(d,p['detail'],540,1572,31,WHITE)
    else:
        card(d,(113,1464,967,1606),fill=(20,31,52),outline=tint(accent,.7),radius=34,width=3)
        text(d,('MEMORIZE' if kind=='memory' and phase=='memorize' else 'YOUR ANSWER?'),340,1530,40,WHITE,True)
        text(d,str(max(1,6-second)),785,1530,91,accent,True)
    d.rounded_rectangle((154,1664,926,1683),radius=9,fill=tint(accent,.22))
    if second<6:
        d.rounded_rectangle((154,1664,154+int(772*(6-second)/6),1683),radius=9,fill=accent)
    else:
        d.rounded_rectangle((154,1664,926,1683),radius=9,fill=secondary)
    text(d,'DROP YOUR ANSWER BELOW',540,1760,33,WHITE,True)
    text(d,'@blinkpuzz  •  NEW CHALLENGES DAILY',540,1820,27,MUTED)
    return img


def synth_audio(path):
    sr=24000
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        out=bytearray()
        for i in range(sr*8):
            t=i/sr
            s=0.0
            phase=t%1
            if t<6 and phase<0.08:
                s+=.05*(1-phase/.08)*math.sin(2*math.pi*820*t)
            if 6<=t<6.5:
                s+=.06*(1-(t-6)/.5)*(math.sin(2*math.pi*660*t)+.5*math.sin(2*math.pi*990*t))
            out+=struct.pack('<h',int(max(-1,min(1,s))*32767))
        w.writeframes(out)


def make_reel(day, output_dir, quick=False, variant='', asset_label=''):
    if asset_label and (not asset_label.isalnum() or len(asset_label)>8):
        raise ValueError('Invalid asset label')
    p=build_puzzle(day,variant)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    stem=day+('-'+variant if variant else '')+('-'+asset_label if asset_label else '')
    mp4=output_dir/(stem+'.mp4')
    cover=output_dir/(stem+'.jpg')
    manifest=output_dir/(stem+'.json')
    render(p,0).save(cover,quality=88,optimize=True)
    with tempfile.TemporaryDirectory(prefix='blinkpuzz-v3-') as temp:
        folder=Path(temp)
        items=[]
        for second in range(8):
            img=render(p,second)
            if quick:
                img=img.resize((540,960))
            path=folder/(f'{second:02d}.jpg')
            img.save(path,quality=87,optimize=True)
            items.append(f"file '{path.as_posix()}'\nduration 1")
        items.append(f"file '{(folder/'07.jpg').as_posix()}'")
        (folder/'frames.txt').write_text('\n'.join(items)+'\n',encoding='utf-8')
        synth_audio(folder/'audio.wav')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
                        '-safe','0','-f','concat','-i',str(folder/'frames.txt'),
                        '-i',str(folder/'audio.wav'),'-t','8','-r','24',
                        '-c:v','libx264','-preset','veryfast','-crf','24',
                        '-pix_fmt','yuv420p','-c:a','aac','-b:a','96k',
                        '-movflags','+faststart',str(mp4)],check=True)
    marker='BP'+day.replace('-','')+variant
    caption=(f"{p['title']} 🧠\n\n{p['subtitle']} — what did you get? "
             f"Comment before the reveal!\n\n"
             f"Follow @blinkpuzz for original bite-size brain challenges.\n\n"
             f"#BrainTeaser #PuzzleChallenge #MindGames #DailyPuzzle #BlinkPuzz\n\n"
             f"Challenge ID: {marker}")
    info={'id':'blinkpuzz-'+stem,'date':day,'slot':variant or 'base',
          'type':p['kind'],'creative_version':'v3','title':p['title'],
          'answer':p['answer'],'solution':p['detail'],'caption':caption,
          'video':mp4.name,'poster':cover.name,'duration_seconds':8,
          'width':540 if quick else W,'height':960 if quick else H,
          'format':'vertical 9:16','published':False}
    manifest.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return info


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--date',default=date.today().isoformat())
    parser.add_argument('--variant',default='',choices=list(OFFSETS))
    parser.add_argument('--out',type=Path,default=Path('docs/media'))
    parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    print(json.dumps(make_reel(args.date,args.out,args.quick,args.variant),ensure_ascii=False))