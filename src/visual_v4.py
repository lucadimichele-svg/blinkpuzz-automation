#!/usr/bin/env python3
"""BlinkPuzz V4: six genuinely different first-frame designs and separate covers.

Fully original procedural artwork, FFmpeg/Pillow, no third-party asset or API keys.
The content remains a quick English brain challenge; this changes visual hierarchy,
not the publishing strategy. New video names prevent overwriting queued assets.
"""
import hashlib
import json
import math
import random
import subprocess
import tempfile
import wave
import struct
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H=1080,1920
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
KINDS=('math','sequence','odd','logic','compare','arcade')
WHITE=(253,253,250)

def f(size,b=True): return ImageFont.truetype(BOLD if b else REG,size)
def txt(d,text,x,y,size,color,weight=True):
    d.text((x,y),str(text),font=f(size,weight),anchor='mm',fill=color)
def rect(d,coords,fill,r=30,outline=None,width=3):
    d.rounded_rectangle(coords,radius=r,fill=fill,outline=outline,width=width)
def seed(day,variant):
    return int.from_bytes(hashlib.sha256(f'blinkpuzz-v4::{day}::{variant}'.encode()).digest()[:8],'big')

def build(day,variant=''):
    date.fromisoformat(day)
    if variant not in ('','B1','B2','B3','N1'): raise ValueError('Invalid variant')
    r=random.Random(seed(day,variant))
    # Multiple active slots on one day should not all be the same kind.
    offset={'':0,'B1':1,'B2':2,'B3':3,'N1':4}[variant]
    kind=KINDS[(date.fromisoformat(day).toordinal()+offset)%len(KINDS)]
    p={'date':day,'variant':variant,'kind':kind,'creative_version':'v4','style':kind}
    if kind=='math':
        a,b,c=r.randint(7,21),r.randint(2,8),r.randint(2,7)
        p.update(title='DON\'T RUSH',tag='MATH TRAP',expression=f'{a} + {b} × {c}',a=a,b=b,c=c,
                 answer=str(a+b*c),solution=f'{b} × {c} = {b*c}; then + {a} = {a+b*c}')
    elif kind=='sequence':
        base=r.randint(2,14); step=r.randint(3,7);grow=r.randint(1,2)
        numbers=[base]
        for i in range(4):numbers.append(numbers[-1]+step+i*grow)
        p.update(title='FIND THE PATTERN',tag='NUMBER SERIES',numbers=numbers[:4],step=step,grow=grow,
                 answer=str(numbers[4]),solution=f'Gaps: +{step}, +{step+grow}, +{step+2*grow}, +{step+3*grow}')
    elif kind=='odd':
        symbols=[('◆','■'),('▲','▼'),('●','◆'),('↗','↖')]
        normal,odd=r.choice(symbols);index=r.randrange(36)
        p.update(title='ONE DOES NOT BELONG',tag='VISUAL TEST',normal=normal,odd=odd,index=index,
                 answer=chr(65+index%6)+str(1+index//6),solution='Different symbol at '+chr(65+index%6)+str(1+index//6))
    elif kind=='logic':
        circle=r.randint(3,9);triangle=r.randint(4,12)
        p.update(title='CRACK THE CODE',tag='LOGIC PUZZLE',circle=circle,triangle=triangle,
                 answer=str(triangle),solution=f'● = {circle}; ▲ = {triangle}')
    elif kind=='compare':
        a,b,c,e=r.randint(8,21),r.randint(3,11),r.randint(3,9),r.randint(3,9)
        left=a+b; right=c*e
        if left==right: b+=1;left+=1
        p.update(title='A OR B?',tag='QUICK DUEL',left=f'{a} + {b}',right=f'{c} × {e}',left_value=left,right_value=right,
                 answer=('A' if left>right else 'B'),solution=f'A = {left}; B = {right}')
    else:
        factor=r.choice([3,4,5,6,7]);right=factor*r.randint(4,9)
        others=[]
        while len(others)<3:
            x=r.randint(17,78)
            if x%factor and x not in others:others.append(x)
        nums=others+[right];r.shuffle(nums)
        p.update(title='PICK ONE',tag='THE ARCADE',factor=factor,doors=nums,
                 answer='ABCD'[nums.index(right)],solution=f'{right} is divisible by {factor}')
    validate(p)
    return p

def validate(p):
    k=p['kind']; ans=p['answer']
    if k=='math': assert int(ans)==p['a']+p['b']*p['c']
    if k=='sequence': assert int(ans)==p['numbers'][-1]+p['step']+3*p['grow']
    if k=='odd': assert ans==chr(65+p['index']%6)+str(1+p['index']//6) and p['normal']!=p['odd']
    if k=='logic': assert int(ans)==p['triangle']
    if k=='compare': assert p['left_value']!=p['right_value'] and ans==('A' if p['left_value']>p['right_value'] else 'B')
    if k=='arcade': assert sum(x%p['factor']==0 for x in p['doors'])==1 and p['doors']['ABCD'.index(ans)]%p['factor']==0
    assert len(ans)>0
    return True

def identity(d,ink,color):
    # Small consistent BP signature, not a repeated giant header.
    rect(d,(72,90,198,185),ink,20)
    txt(d,'BP',135,137,45,color)

def wallpaper(p):
    k=p['kind']
    backgrounds={'math':(255,239,194),'sequence':(14,24,54),'odd':(12,28,22),'logic':(16,42,36),'compare':(20,31,60),'arcade':(45,18,69)}
    return Image.new('RGB',(W,H),backgrounds[k])

def body(d,p,cover=False,answer=False):
    k=p['kind']
    if k=='math':
        ink=(29,30,33);hot=(242,82,47);shade=(255,247,226)
        identity(d,ink,WHITE)
        txt(d,'01  /  THINK FAST',820,140,37,hot)
        txt(d,p['title'],W//2,335,104,ink)
        d.line((110,430,970,430),fill=ink,width=13)
        rect(d,(68,605,1012,1260),shade,32,ink,6)
        txt(d,p['expression'],540,870,103,ink)
        txt(d,'= '+(p['answer'] if answer else '?'),540,1120,113,hot)
        txt(d,'ORDER OF OPERATIONS',540,1380,45,ink)
        d.rectangle((0,1540,W,1570),fill=hot)
    elif k=='sequence':
        ink=(220,236,255);accent=(84,191,252);neon=(250,246,132)
        identity(d,(25,92,142),WHITE)
        txt(d,'THE NUMBER LAB',790,145,42,accent)
        txt(d,'WHAT COMES',540,378,96,WHITE)
        txt(d,'NEXT?',540,502,139,neon)
        d.line((140,600,940,600),fill=accent,width=7)
        for i,val in enumerate(p['numbers']+[p['answer'] if answer else '?']):
            x=55+i*201
            d.ellipse((x,811,x+174,985),fill=neon if i==4 else (43,67,108),outline=accent,width=5)
            txt(d,val,x+87,898,68,(24,31,52) if i==4 else ink)
        for i in range(4):d.line((140+i*201,1021,210+i*201,1021),fill=accent,width=8)
        txt(d,'FIND THE HIDDEN RULE',540,1210,53,accent)
        for j in range(12):d.line((0,1430+j*24,1080,1430+j*24),fill=(24,47,83),width=2)
    elif k=='odd':
        accent=(201,255,72);ink=(230,255,222)
        identity(d,accent,(12,28,22))
        txt(d,'EAGLE EYES',810,140,48,accent)
        txt(d,'FIND THE',540,310,112,WHITE)
        txt(d,'ODD ONE',540,430,123,accent)
        for i in range(36):
            x=94+i%6*153; y=594+i//6*143
            selected=answer and i==p['index']
            rect(d,(x,y,x+127,y+119),(24,65,44) if not selected else (55,102,45),13,accent if selected else (59,104,62),5 if selected else 2)
            txt(d,p['odd'] if i==p['index'] else p['normal'],x+64,y+60,67,accent if selected else ink)
        txt(d,'LOOK CLOSELY',540,1544,51,accent)
    elif k=='logic':
        accent=(166,253,197);paper=(225,248,227);ink=(15,39,33)
        identity(d,accent,ink)
        txt(d,'CASE FILE  /  004',795,142,43,accent)
        txt(d,'CRACK THE',540,350,106,paper)
        txt(d,'CODE',540,482,143,accent)
        for i,(left,right) in enumerate([('● + ●',str(2*p['circle'])),('● + ▲',str(p['circle']+p['triangle'])),('▲',p['answer'] if answer else '?')]):
            y=669+i*234
            rect(d,(105,y,975,y+189),(31,71,62),12,accent,4)
            txt(d,left,318,y+94,94,paper)
            txt(d,'=',582,y+94,80,accent)
            txt(d,right,797,y+94,87,accent)
        txt(d,'ONE SYMBOL. ONE VALUE.',540,1482,39,accent)
    elif k=='compare':
        red=(255,109,105);blue=(111,187,255);ink=(20,31,60)
        d.rectangle((0,0,540,H),fill=(31,72,137))
        d.rectangle((540,0,W,H),fill=(138,45,75))
        identity(d,(240,246,255),ink)
        txt(d,'WHICH SIDE WINS?',540,346,80,WHITE)
        txt(d,'A',270,649,170,blue)
        txt(d,'B',810,649,170,red)
        txt(d,'VS',540,896,76,WHITE)
        rect(d,(42,1000,500,1260),(13,38,90),24,blue,5)
        rect(d,(580,1000,1038,1260),(101,27,50),24,red,5)
        txt(d,p['left'],271,1130,84,WHITE)
        txt(d,p['right'],809,1130,84,WHITE)
        txt(d,'BIGGER RESULT WINS',540,1420,48,WHITE)
        if answer:
            txt(d,'WINNER '+p['answer'],540,1555,86,(245,234,101))
    else:
        accent=(255,219,96);ink=(249,228,255)
        identity(d,accent,(45,18,69))
        txt(d,'ARCADE  /  LEVEL 01',770,142,43,accent)
        txt(d,'PICK',540,346,153,WHITE)
        txt(d,'ONE!',540,500,159,accent)
        txt(d,f'WHICH NUMBER IS DIVISIBLE BY {p["factor"]}?',540,695,42,ink)
        for i,n in enumerate(p['doors']):
            x=48+i*254
            rect(d,(x,825,x+225,1250),(92,41,127),24,accent,6)
            txt(d,'ABCD'[i],x+113,899,69,accent)
            txt(d,n,x+113,1065,91,WHITE)
            if answer and 'ABCD'[i]==p['answer']:
                rect(d,(x+10,1200,x+215,1250),accent,9)
        txt(d,'THERE IS ONLY ONE',540,1440,58,accent)

def draw_reel(p,second):
    ans=second>=6
    im=wallpaper(p)
    d=ImageDraw.Draw(im)
    body(d,p,cover=False,answer=ans)
    # Animated overlay only; no timer on the independently generated cover.
    if p['kind']=='math':bar=(242,82,47);caption=(29,30,33)
    else:bar=(246,224,118);caption=WHITE
    rect(d,(145,1631,935,1697),(18,34,49) if p['kind']!='math' else (247,226,181),22)
    txt(d,'ANSWER: '+p['answer'] if ans else 'YOU HAVE '+str(6-second)+' SECONDS',540,1661,46,bar if ans else caption)
    d.rounded_rectangle((150,1740,930,1757),radius=9,fill=(68,75,84))
    d.rounded_rectangle((150,1740,150+int(780*(1 if ans else (6-second)/6)),1757),radius=9,fill=bar)
    txt(d,'COMMENT YOUR ANSWER',540,1827,35,caption)
    return im

def draw_cover(p):
    im=wallpaper(p);d=ImageDraw.Draw(im)
    body(d,p,cover=True,answer=False)
    if p['kind']=='math':fg=(29,30,33);label='CAN YOU SOLVE IT?'
    else:fg=WHITE;label='CAN YOU SOLVE IT?'
    # Clean independent thumbnail: no countdown, no progress bar and no text behind IG stats.
    rect(d,(135,1660,945,1750),(22,36,52) if p['kind']!='math' else (40,42,46),22)
    txt(d,label,540,1705,48,(250,243,143))
    txt(d,'@BLINKPUZZ',540,1817,30,fg)
    return im

def audio_file(path):
    sr=24000
    with wave.open(str(path),'wb') as a:
        a.setnchannels(1);a.setsampwidth(2);a.setframerate(sr)
        out=bytearray()
        for i in range(sr*8):
            t=i/sr;s=0
            mod=t%1
            if t<6 and mod<.06:s+=.06*(1-mod/.06)*math.sin(2*math.pi*780*t)
            if 6<=t<6.4:s+=.08*(1-(t-6)/.4)*math.sin(2*math.pi*659*t)
            out+=struct.pack('<h',int(max(-1,min(1,s))*32767))
        a.writeframes(out)

def make_reel(day,output_dir,quick=False,variant='',asset_label='V4'):
    if asset_label != 'V4':raise ValueError('Only separate V4 assets, never overwrite original video names')
    p=build(day,variant)
    path=Path(output_dir);path.mkdir(parents=True,exist_ok=True)
    stem=day+('-'+variant if variant else '')+'-V4'
    video=path/(stem+'.mp4');poster=path/(stem+'.jpg');meta=path/(stem+'.json')
    if any(o.exists() for o in (video,poster,meta)):
        if all(o.exists() and o.stat().st_size>100 for o in (video,poster,meta)):
            return json.loads(meta.read_text())
        raise RuntimeError(f'Incomplete assets for {stem}: refusing to overwrite')
    draw_cover(p).save(poster,quality=91,optimize=True)
    with tempfile.TemporaryDirectory(prefix='blinkpuzz-v4-') as td:
        tmp=Path(td)
        contents=[]
        for second in range(8):
            im=draw_reel(p,second)
            if quick:im=im.resize((540,960))
            jpeg=tmp/(f'frame_{second:02d}.jpg')
            im.save(jpeg,quality=87,optimize=True)
            contents.append(f"file '{jpeg.as_posix()}'\nduration 1")
        contents.append(f"file '{(tmp/'frame_07.jpg').as_posix()}'")
        (tmp/'frames.txt').write_text('\n'.join(contents)+'\n')
        audio_file(tmp/'audio.wav')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-safe','0','-f','concat','-i',str(tmp/'frames.txt'),'-i',str(tmp/'audio.wav'),
            '-t','8','-r','24','-c:v','libx264','-preset','veryfast','-crf','24',
            '-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(video)],check=True)
    marker='BP'+day.replace('-','')+variant
    captions={'math':'Did you do the multiplication first?',
              'sequence':'Spot the rule? Show us your method!',
              'odd':'Where is the odd symbol? Give us its position!',
              'logic':'Can you crack the symbols?',
              'compare':'Team A or Team B? Tell us why!',
              'arcade':'Which door is the only correct one?'}
    caption=(f'{p["title"]} 🧠\n\n{captions[p["kind"]]} Comment your answer!\n\n'
             'Follow @blinkpuzz for daily brain puzzles.\n\n'
             '#BrainTeaser #PuzzleChallenge #DailyPuzzle #LogicPuzzle #BlinkPuzz\n\n'
             f'Challenge ID: {marker}')
    result={'id':'blinkpuzz-'+stem,'date':day,'slot':variant or 'base',
            'creative_version':'v4','visual_style':p['style'],'type':p['kind'],
            'title':p['title'],'answer':p['answer'],'solution':p['solution'],
            'caption':caption,'video':video.name,'poster':poster.name,
            'duration_seconds':8,'width':540 if quick else W,'height':960 if quick else H,
            'format':'vertical 9:16','published':False}
    meta.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    return result

if __name__=='__main__':
    import argparse
    arg=argparse.ArgumentParser();arg.add_argument('--date',required=True);arg.add_argument('--variant',default='');arg.add_argument('--out',default='docs/media');arg.add_argument('--quick',action='store_true')
    a=arg.parse_args();print(json.dumps(make_reel(a.date,a.out,a.quick,a.variant)))