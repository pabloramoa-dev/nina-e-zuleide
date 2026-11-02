#!/usr/bin/env python3
"""Vozes originais Kokoro dos repositórios do usuário; trilha e timeline reais."""
import json,os,subprocess,sys,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'build';SR=44100

def run(*args):subprocess.run(list(map(str,args)),check=True)
def wav_read(path):
    with wave.open(str(path),'rb') as w:
        if w.getframerate()!=SR or w.getnchannels()!=1 or w.getsampwidth()!=2:raise RuntimeError('WAV precisa ser PCM mono 44100Hz s16')
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768

def write_wav(path, samples):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((np.clip(samples,-1,1)*32767).astype('<i2').tobytes())

def prepare():
    s=json.loads((BUILD/'roteiro.json').read_text(encoding='utf8'));lines=s['lines'];parts={};laugh={}
    for who in ('nina','zuleide'):
        selected=[ln['text'] for ln in lines if ln['speaker']==who]
        path=BUILD/f'{who}.txt';path.write_text('\n'.join(selected+['Ha, ha, ha!'])+'\n',encoding='utf8')
        src=ROOT/'nina_source/motor/gerar_voz_kokoro.py' if who=='nina' else ROOT/'reels/gerar_voz_kokoro.py'
        if not src.exists():raise FileNotFoundError('Modelo original de voz ausente: '+str(src))
        base=BUILD/f'{who}_base.wav';segs=BUILD/f'{who}_segments.json'
        run(sys.executable,src,path,'--voz','pf_dora','--speed','1.02' if who=='nina' else '0.95','--gap','0.22','--out',base,'--seg-json',segs)
        if who=='zuleide':
            pitch=.94;out=BUILD/f'{who}_voice.wav'
            flt=f'asetrate=44100*{pitch},aresample=44100,atempo={1/pitch:.5f},vibrato=f=5.5:d=0.09,highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=8:release=180,volume=1.15'
            run('ffmpeg','-y','-v','error','-i',base,'-af',flt,'-ar',SR,'-ac',1,'-c:a','pcm_s16le',out)
            base=out
        audio=wav_read(base);data=json.loads(segs.read_text())
        slices=[]
        for seg in data:
            start=int(seg['ini']*SR);end=int(seg.get('fim_fala',seg['fim']-0.22)*SR)
            slices.append(audio[start:end].copy())
        if len(slices)<len(selected)+1:raise RuntimeError('Modelo gerou menos trechos que as falas')
        parts[who]=slices[:len(selected)]
        laugh[who]=slices[-1][:int(.85*SR)]
    cursor=0;counts={'nina':0,'zuleide':0};timeline=[];chunks=[];risadas=[]
    def add(a):
        nonlocal cursor
        chunks.append(a);cursor+=len(a)
    for i,ln in enumerate(lines):
        who=ln['speaker'];frag=parts[who][counts[who]];counts[who]+=1
        st=cursor/SR;add(frag);en=cursor/SR
        timeline.append({'speaker':who,'text':ln['text'],'scene_id':int(ln['scene_id']),'start':st,'end':en})
        if ln.get('laugh_after'):
            add(np.zeros(int(.10*SR),dtype=np.float32))
            rs=cursor/SR;add(laugh[who]);risadas.append({'who':who,'start':rs,'end':cursor/SR})
        add(np.zeros(int(.20*SR),dtype=np.float32))
    output=np.concatenate(chunks)
    duration=len(output)/SR
    # Gera WAV original; em produção o pipeline avalia se a duração está próxima da meta.
    write_wav(BUILD/'audio_completo.wav',output)
    run(sys.executable,ROOT/'reels/lipsync_amplitude.py',BUILD/'audio_completo.wav',BUILD/'mouth.json','--fps',20)
    cues=json.loads((BUILD/'mouth.json').read_text())['mouthCues']
    (BUILD/'timeline.json').write_text(json.dumps({'title':s['titulo'],'duration':duration,'timeline':timeline,'risadas':risadas,'mouthCues':cues},ensure_ascii=False,indent=2),encoding='utf8')
    print('Áudio original Kokoro:',round(duration,1),'s e',len(timeline),'falas')
    if not 135<=duration<=225: raise ValueError(f'Duração fora do intervalo 3min ±45s: {duration:.1f}s; ajustar texto ou velocidade, sem cortar a história')
if __name__=='__main__':prepare()
