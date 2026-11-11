#!/usr/bin/env python3
"""Check that each output file meets expected publication format."""
import json
import subprocess
from pathlib import Path
import sys


def validate(folder):
    paths=sorted(Path(folder).glob('*.json'))
    if not paths:
        raise AssertionError('No media manifests found')
    for path in paths:
        data=json.loads(path.read_text(encoding='utf8'))
        video=path.parent/data['video']
        poster=path.parent/data['poster']
        assert video.is_file() and video.stat().st_size > 20_000, video
        assert poster.is_file() and poster.stat().st_size > 10_000, poster
        assert data['answer'] and data['solution']
        assert 'Challenge ID: BP' in data['caption']
        assert data['caption'].count('#') <= 5
        proc=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],
                            check=True,capture_output=True,text=True)
        p=json.loads(proc.stdout)
        streams=p['streams']
        v=next(s for s in streams if s['codec_type']=='video')
        assert (v['width'],v['height'])==(1080,1920),video
        assert v['codec_name']=='h264'
        assert any(s['codec_type']=='audio' and s['codec_name']=='aac' for s in streams)
        assert abs(float(p['format']['duration'])-float(data.get('duration_seconds',8)))<0.15
        print(f"PASS {data['date']} ({data['type']}, answer={data['answer']})")
    return len(paths)

if __name__=='__main__':
    print(f'{validate(sys.argv[1] if len(sys.argv)>1 else "docs/media")} reels validated')
