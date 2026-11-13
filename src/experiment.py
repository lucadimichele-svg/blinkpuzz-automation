#!/usr/bin/env python3
"""BlinkPuzz v4 small-scale 4-arm experiment: comparable original 12-second Reels.

12 slots, Nov 15-20 2026. Three distinct challenge families in every arm.
No prior generated assets or Buffer posts are modified.
"""
from __future__ import annotations
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
LENGTH = 12
REVEAL_AT = 10
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NORMAL = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COLORS = {
    'sequence': ((16, 25, 63), (35, 29, 88), (130, 213, 255), (255, 210, 105)),
    'math': ((42, 25, 22), (87, 39, 48), (255, 180, 115), (126, 241, 225)),
    'logic': ((24, 44, 38), (21, 85, 69), (152, 247, 178), (255, 229, 140)),
}
# Within each day, group assignment is unique. Every arm is tested on all
# three puzzle families, eliminating a major content-category confound.
TEST = (
    ('2026-11-15', 'B1', 'A', 'sequence'),
    ('2026-11-15', 'B2', 'B', 'math'),
    ('2026-11-19', 'N1', 'C', 'logic'),
    ('2026-11-15', 'B3', 'D', 'sequence'),
    ('2026-11-16', 'B1', 'D', 'math'),
    ('2026-11-16', 'B2', 'C', 'sequence'),
    ('2026-11-20', 'N1', 'B', 'logic'),
    ('2026-11-16', 'B3', 'A', 'math'),
    ('2026-11-17', 'N1', 'B', 'sequence'),
    ('2026-11-17', 'base', 'D', 'logic'),
    ('2026-11-18', 'N1', 'A', 'logic'),
    ('2026-11-18', 'base', 'C', 'math'),
)
ARMS = {
    'A': {'difficulty':'easy','in_video_reveal':True,'choices':False,'label':'Easy + reveal'},
    'B': {'difficulty':'medium','in_video_reveal':True,'choices':False,'label':'Medium + reveal'},
    'C': {'difficulty':'medium','in_video_reveal':False,'choices':False,'label':'Medium + caption spoiler'},
    'D': {'difficulty':'medium','in_video_reveal':False,'choices':True,'label':'Medium + options + caption spoiler'},
}


def _font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else NORMAL, size)


def _text(draw, value, cx, cy, size, color=(250, 253, 255), bold=True):
    draw.text((cx, cy), str(value), font=_font(size,bold), fill=color, anchor='mm')


def _pill(draw, coords, fill, outline=None, r=28, width=3):
    draw.rounded_rectangle(coords, radius=r, fill=fill, outline=outline, width=width)


def _seed(day, slot):
    raw = f'blinkpuzz-test-v1:{day}:{slot}'.encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big')


def slot_stem(day, slot):
    return day + ('' if slot=='base' else '-'+slot)


def assignment(day, slot):
    row = next((x for x in TEST if x[:2] == (day, slot)), None)
    return None if row is None else (row[2],row[3])


def build(day, slot):
    result=assignment(day,slot)
    if result is None: raise ValueError(f'Not in experiment: {day} {slot}')
    arm, family=result
    cfg=ARMS[arm]
    rng=random.Random(_seed(day,slot))
    easy=cfg['difficulty']=='easy'
    p={'day':day,'slot':slot,'arm':arm,'family':family,'easy':easy, 'in_video_reveal':cfg['in_video_reveal'],
       'choices_enabled':cfg['choices'], 'creative_version':'experiment-v1', 'duration_seconds':LENGTH}
    if family=='sequence':
        start=rng.randint(3,11)+date.fromisoformat(day).toordinal()%4
        delta=rng.randint(3,6)
        grow=0 if easy else rng.randint(2,3)
        values=[start]
        for i in range(4): values.append(values[-1]+delta+i*grow)
        p.update(display=values[:4],answer=values[4],
                 solution=(f'Add {delta} each time' if easy else f'Gaps: +{delta}, +{delta+grow}, +{delta+2*grow}, +{delta+3*grow}'),
                 options_candidates=[values[4]-grow or values[4]-2,values[4]+grow or values[4]+2])
    elif family=='math':
        a=rng.randint(6,16)
        b=rng.randint(3,7)
        c=rng.randint(3,6)
        d=rng.randint(2,6)
        if easy:
            p.update(display=f'{a} + {b} + {c}',operands=[a,b,c],answer=a+b+c,
                     solution=f'{a} + {b} + {c} = {a+b+c}',options_candidates=[a+b+c+2,a+b+c-2])
        else:
            correct=a+b*c-d
            alt1=(a+b)*c-d
            alt2=a+b*(c-d)
            p.update(display=f'{a} + {b} × {c} − {d}', operands=[a,b,c,d],answer=correct,
                     solution=f'Multiply first: {b} × {c} = {b*c}; then {a} + {b*c} − {d} = {correct}',
                     options_candidates=[alt1,alt2])
    else:
        circle=rng.randint(4,9)
        triangle=rng.randint(6,13)
        if easy:
            question='▲ = ?'
            answer=triangle
            solution=f'● = {circle}; ▲ = {circle+triangle} − {circle} = {triangle}'
        else:
            question='2 × ▲ − ● = ?'
            answer=2*triangle-circle
            solution=f'● = {circle}; ▲ = {circle+triangle} − {circle} = {triangle}; 2 × {triangle} − {circle} = {answer}'
        p.update(display=[f'● + ● = {2*circle}',f'● + ▲ = {circle+triangle}',question], circle=circle, triangle=triangle,
                 answer=answer, solution=solution,
                 options_candidates=[answer+circle,answer+triangle])
    p['answer']=int(p['answer'])
    options=[p['answer'],*p['options_candidates']]
    if len(set(options))<3:
        options=[p['answer'],p['answer']+2,p['answer']-2]
    if p['choices_enabled']:
        rng.shuffle(options)
        p['options']={'ABC'[i]:v for i,v in enumerate(options)}
        p['correct_letter']=next(k for k,v in p['options'].items() if v==p['answer'])
    else:
        p['options']={}
        p['correct_letter']=None
    validate(p)
    return p


def validate(p):
    assert p['answer'] == int(p['answer'])
    assert p['arm'] in ARMS
    if p['family']=='sequence':
        nums=p['display']
        gaps=[nums[i+1]-nums[i] for i in range(3)]
        if p['easy']: assert gaps[0]==gaps[1]==gaps[2]
        else: assert gaps[1]-gaps[0]==gaps[2]-gaps[1] and gaps[1]>gaps[0]
        assert p['answer']==nums[-1]+gaps[-1]+(0 if p['easy'] else gaps[-1]-gaps[-2])
    if p['family']=='math':
        nums=p['operands']
        expect = nums[0]+nums[1]+nums[2] if p['easy'] else nums[0]+nums[1]*nums[2]-nums[3]
        assert p['answer']==expect and p['answer']>0
    if p['family']=='logic':
        assert len(p['display'])==3
        expect=p['triangle'] if p['easy'] else 2*p['triangle']-p['circle']
        assert p['answer']==expect
        assert p['display'][0] == f"● + ● = {2*p['circle']}"
        assert p['display'][1] == f"● + ▲ = {p['circle']+p['triangle']}"
    if p['choices_enabled']:
        assert len(p['options'])==3 and len(set(p['options'].values()))==3
        assert p['options'][p['correct_letter']]==p['answer']
    return True


def render(p,second):
    assert 0<=second<LENGTH
    base, bottom, accent, yellow=COLORS[p['family']]
    im=Image.new('RGB',(W,H))
    draw=ImageDraw.Draw(im)
    for y in range(H):
        ratio=y/H
        draw.line((0,y,W,y),fill=tuple(int(base[i]*(1-ratio)+bottom[i]*ratio) for i in range(3)))
    draw.ellipse((-250,1300,210,1760),outline=(48,89,92),width=5)
    draw.arc((740,-180,1330,460),50,300,fill=accent,width=7)
    _pill(draw,(85,125,995,200),(13,25,38),accent,r=30,width=2)
    _text(draw,'BLINKPUZZ',291,162,42)
    _text(draw,'BRAIN CHALLENGE',767,162,27,accent)
    _text(draw,'THINK TWICE' if not p['easy'] else 'QUICK WARM-UP',W//2,340,53,accent)
    _text(draw,{'sequence':'WHAT COMES NEXT?','math':'WHAT IS THE ANSWER?','logic':'CRACK THE CODE'}[p['family']],W//2,443,63)
    _text(draw,'DON’T RUSH YOUR ANSWER',W//2,535,35,(210,223,231),False)
    if p['family']=='sequence':
        numbers=list(p['display'])+['?']
        for idx,n in enumerate(numbers):
            x=65+idx*193
            _pill(draw,(x,805,x+175,1010),(31,47,71),yellow if idx==4 else accent,r=28,width=4 if idx==4 else 2)
            _text(draw,n,x+87,907,68,yellow if idx==4 else (255,255,255))
        _text(draw,'FIND THE RULE',W//2,1118,40,accent)
    elif p['family']=='math':
        _pill(draw,(95,775,985,1140),(31,44,68),accent,r=45,width=5)
        size=72 if len(p['display'])>14 else 89
        _text(draw,p['display'],W//2,930,size)
        _text(draw,'= ?',W//2,1174,83,yellow)
    else:
        for idx,line in enumerate(p['display']):
            y=696+idx*202
            _pill(draw,(143,y,937,y+168),(25,55,62),yellow if idx==2 else accent,r=30,width=4 if idx==2 else 2)
            _text(draw,line,W//2,y+84,62,yellow if idx==2 else (255,255,255))
    # Choices are an intentionally isolated experimental factor.
    if p['choices_enabled']:
        _text(draw,'CHOOSE A, B OR C',W//2,1295,36,accent)
        for i,(letter,value) in enumerate(p['options'].items()):
            x=107+i*294
            _pill(draw,(x,1340,x+274,1465),(22,42,56),accent,r=21,width=3)
            _text(draw,f'{letter}: {value}',x+137,1402,45,yellow)
    # Identical experiment durations; arms differ only in difficulty/reveal/choices.
    if second>=REVEAL_AT and p['in_video_reveal']:
        _pill(draw,(98,1535,982,1683),(17,65,65),yellow,r=31,width=4)
        _text(draw,f'ANSWER: {p["answer"]}',W//2,1597,54,yellow)
        _text(draw,'CHECK THE CAPTION FOR THE METHOD',W//2,1650,27,(243,244,229),False)
    elif second>=REVEAL_AT:
        _pill(draw,(98,1535,982,1683),(26,57,67),accent,r=31,width=4)
        _text(draw,'WHAT DID YOU GET?',W//2,1608,54,yellow)
        _text(draw,'EXPLAIN YOUR ANSWER BELOW',W//2,1651,27,(243,244,229),False)
    else:
        _pill(draw,(98,1535,982,1683),(25,41,60),accent,r=31,width=2)
        _text(draw,'YOUR ANSWER?',385,1606,39)
        _text(draw,str(REVEAL_AT-second),802,1606,79,accent)
    _pill(draw,(152,1728,928,1748),(34,57,68),r=7)
    progress=(max(0,REVEAL_AT-second)/REVEAL_AT) if second<REVEAL_AT else 0
    if progress>0:
        _pill(draw,(152,1728,152+int(776*progress),1748),accent,r=7)
    _text(draw,'COMMENT BEFORE YOU CHECK THE SOLUTION',W//2,1805,29,(232,239,247))
    _text(draw,'@blinkpuzz',W//2,1859,29,accent)
    return im


def synth_audio(path, duration=LENGTH, reveal_at=REVEAL_AT):
    sr=24000
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        chunk=bytearray()
        for i in range(sr*duration):
            t=i/sr
            pulse=t%1
            signal=0.0
            if t<reveal_at and pulse<.045:
                signal+=.055*(1-pulse/.045)*math.sin(2*math.pi*740*t)
            if reveal_at<=t<reveal_at+.32:
                signal+=.038*(1-(t-reveal_at)/.32)*math.sin(2*math.pi*660*t)
            chunk+=struct.pack('<h',int(max(-1,min(1,signal))*32767))
        w.writeframes(chunk)


def make_reel(day, slot, out_dir, quick=False):
    p=build(day,slot)
    dest=Path(out_dir)
    dest.mkdir(parents=True,exist_ok=True)
    stem=slot_stem(day,slot)+'-EXP'
    mp4=dest/(stem+'.mp4')
    poster=dest/(stem+'.jpg')
    manifest=dest/(stem+'.json')
    render(p,0).save(poster,quality=91,optimize=True)
    with tempfile.TemporaryDirectory(prefix='blinkpuzz-exp-') as temp:
        folder=Path(temp)
        lines=[]
        for second in range(LENGTH):
            frame=render(p,second)
            if quick: frame=frame.resize((540,960))
            name=folder/(f'{second:02d}.jpg')
            frame.save(name,quality=86,optimize=True)
            lines.append(f"file '{name.as_posix()}'\nduration 1")
        lines.append(f"file '{(folder/'11.jpg').as_posix()}'")
        (folder/'frames.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        synth_audio(folder/'sound.wav')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-safe','0','-f','concat','-i',str(folder/'frames.txt'),
            '-i',str(folder/'sound.wav'),'-t',str(LENGTH),'-r','24',
            '-c:v','libx264','-preset','veryfast','-crf','24',
            '-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(mp4)],check=True)
    config=ARMS[p['arm']]
    if p['choices_enabled']:
        intro='Which option is right — A, B or C? Explain your pick in the comments.'
    else:
        intro='What answer did you get? Explain how you solved it in the comments.'
    challenge='BP'+day.replace('-','')+('' if slot=='base' else slot)
    caption=(f'{p["family"].upper()} CHALLENGE 🧠\n\n{intro}\n\n'
             f'Follow @blinkpuzz for daily original brain games.\n\n'
             f'#BrainTeaser #PuzzleChallenge #BrainGames #LogicPuzzle #BlinkPuzz\n\n'
             f'Challenge ID: {challenge}\n\n\n\n'
             f'SPOILER — SOLUTION BELOW ⬇️\n'
             f'Answer: {p["answer"]}. {p["solution"]}')
    meta={'id':'blinkpuzz-'+stem,'date':day,'slot':slot,
          'experiment_id':'BP-2026-11-ABCD', 'experiment_arm':p['arm'],
          'experiment_label':config['label'],'difficulty':config['difficulty'],
          'in_video_reveal':config['in_video_reveal'],'choices_enabled':config['choices'],
          'creative_version':p['creative_version'],'type':p['family'],
          'title':{'sequence':'WHAT COMES NEXT?','math':'WHAT IS THE ANSWER?','logic':'CRACK THE CODE'}[p['family']],
          'answer':str(p['answer']),'solution':p['solution'],'caption':caption,
          'video':mp4.name,'poster':poster.name,'duration_seconds':LENGTH,
          'width':540 if quick else W,'height':960 if quick else H,
          'format':'vertical 9:16','published':False}
    manifest.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return meta


def plan():
    return {'experiment_id':'BP-2026-11-ABCD','start_date':'2026-11-15',
            'end_date':'2026-11-20','timezone':'Europe/Berlin',
            'design':'4 arms x 3 Reels each; 12s every Reel; each arm contains sequence, math, logic once',
            'primary_metrics':['comments_per_100_views','average_watch_seconds'],
            'secondary_metrics':['views_48h','likes_per_100_views','shares_per_100_views','follows_48h'],
            'note':'Exploratory only: n=3/arm, not statistically conclusive. Buffer queue status is not Instagram performance.',
            'arms':{key:dict(value) for key,value in ARMS.items()},
            'slots':[{'date':day,'slot':slot,'arm':arm,'type':family,
                      'challenge_id':'BP'+day.replace('-','')+('' if slot=='base' else slot)}
                     for day,slot,arm,family in TEST]}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--date',required=True)
    parser.add_argument('--slot',required=True)
    parser.add_argument('--out',default='docs/media')
    parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    print(json.dumps(make_reel(args.date,args.slot,args.out,args.quick)))