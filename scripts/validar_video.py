"""Bloqueia entrega de MP4 incompleto ou incompatível."""
import json, subprocess, sys
from pathlib import Path

def validate(info):
    streams=info['streams']
    video=next(s for s in streams if s['codec_type']=='video')
    audio=next(s for s in streams if s['codec_type']=='audio')
    assert video['codec_name']=='h264'
    assert audio['codec_name']=='aac'
    assert (video['width'],video['height'])==(540,960)
    assert video['pix_fmt']=='yuv420p'
    assert 135<=float(info['format']['duration'])<=225
    assert abs(float(video['duration'])-float(audio['duration']))<.5

if __name__=='__main__':
    path=Path(sys.argv[1])
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    validate(info)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],check=True)
    path.with_suffix('.qa.json').write_text(json.dumps(info,indent=2))
    print('MP4 decodificado integralmente: H264/AAC, vertical, duração e sincronismo válidos')
