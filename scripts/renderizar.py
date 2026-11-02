#!/usr/bin/env python3
"""Dois retratos Manim originais + ilustrações DISTINTAS e realmente visíveis em ambos painéis.
Chamada: manim -ql --fps 20 -r 540,960 scripts/renderizar.py NinaZuleide
"""
import bisect,hashlib,json,math,sys,textwrap
from pathlib import Path
from manim import *
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'build'
sys.path[:0]=[str(ROOT/'nina_source/motor'),str(ROOT/'reels')]
import nina_lib as NL
import previsao_lib as PREV
import dvh_lip as LIP
config.frame_width=8.0
config.frame_height=14.222
config.pixel_width=540
config.pixel_height=960

class NinaZuleide(Scene):
    def construct(self):
        info=json.loads((BUILD/'timeline.json').read_text(encoding='utf8'))
        lines=info['timeline'];starts=[x['start'] for x in lines];duration=info['duration']
        self.camera.background_color='#101725'
        ypanels={'nina':3.30,'zuleide':-3.30}
        x_figure=-2.00;x_art=1.88
        # 10 ilustrações para cada quadro. Não permitir mesma imagem entre personagens.
        imgs={}
        for role in ('nina','zuleide'):
            imgs[role]=[]
            for i in range(10):
                file=BUILD/'images'/role/f'cena_{i:02d}.jpg'
                if not file.is_file():raise FileNotFoundError('Falta ilustração real: '+str(file))
                imgs[role].append(file)
        for i in range(10):
            if hashlib.sha256(imgs['nina'][i].read_bytes()).digest()==hashlib.sha256(imgs['zuleide'][i].read_bytes()).digest():
                raise RuntimeError('Nina e Zuleide possuem a mesma ilustração; render bloqueado na cena '+str(i))
        pictures={r:[ImageMobject(str(path)) for path in files] for r,files in imgs.items()}
        for role in pictures:
            for pic in pictures[role]:
                pic.scale(min(3.08/pic.width,3.76/pic.height))
        # Molduras escuras da dupla
        for role in ('nina','zuleide'):
            cy=ypanels[role]
            base=RoundedRectangle(corner_radius=.16,width=7.82,height=6.33,fill_color='#253548' if role=='nina' else '#333A49',fill_opacity=1,stroke_color='#101725',stroke_width=4).move_to([0,cy,0])
            self.add(base,Line([-3.86,cy+3.04,0],[3.86,cy+3.04,0],color='#DFB77B',stroke_width=6))
            name=Text('NINA' if role=='nina' else 'DONA ZULEIDE',font='DejaVu Sans',font_size=32,color='#FFE6AB',weight='BOLD').move_to([-2.0,cy+2.65,0]);self.add(name)
            frame=RoundedRectangle(corner_radius=.16,width=3.30,height=4.06,fill_color='#1A2636',fill_opacity=1,stroke_color='#C9B18B',stroke_width=3).move_to([x_art,cy-.02,0]);self.add(frame)
        chars={'nina':NL.nina(expr='ironica',cenario='tarde'), 'zuleide':PREV.dona_maria(humor='simpatica')}
        # Zoom de foto 3x4. Nina quase igual à versão aprovada; Zuleide mais aproximada.
        for role,p in chars.items():
            g=p['grupo'];factor=1.18
            g.scale(factor);p['_factor']=factor
            g.shift(np.array([x_figure,ypanels[role]+.48,0])-p['cab'].get_center())
            self.add(g)
        # Cobrir apenas bordas externas para o enquadramento sem corpo inteiro.
        for cy in ypanels.values():
            self.add(Rectangle(width=3.70,height=1.40,fill_color='#253548' if cy>0 else '#333A49',fill_opacity=1,stroke_width=0).move_to([-2.03,cy-2.23,0]))
        # Imagens de apoio SEM imagens iguais entre painéis, com âncoras independentes.
        active_pictures={}
        for role in ('nina','zuleide'):
            frame=pictures[role][0].copy().move_to([x_art,ypanels[role]-.02,0]);self.add(frame);active_pictures[role]=frame
        # Legenda inferior por painel, não por cima da imagem.
        captions={role:Text('...',font='DejaVu Sans',font_size=25,color=WHITE,weight='MEDIUM') for role in chars}
        for role,cap in captions.items():cap.move_to([0,ypanels[role]-2.58,0]);self.add(cap)
        mouths={}
        for role,p in chars.items():
            m=p['rosto'][3] if role=='nina' else p['boca'];extra=VGroup();self.add(extra)
            mouths[role]={'original':m,'extra':extra,'last':None}
        cues=info['mouthCues'];cue_starts=[c['start'] for c in cues]
        state={'index':-1,'scene':-1,'last_y':{'nina':0,'zuleide':0},'last_eyes':{'nina':0,'zuleide':0}}
        times={r:ypanels[r] for r in chars}
        def animate(all_mobj,alpha):
            now=min(duration-.0001,alpha*duration)
            ix=max(0,min(len(lines)-1,bisect.bisect_right(starts,now)-1));line=lines[ix]
            speaker=line['speaker'] if now<line['end'] else None
            for l in info.get('risadas',[]):
                if l['start']<=now<l['end']:speaker=l['who'];break
            if ix!=state['index']:
                state['index']=ix
                for role,cap in captions.items():
                    cap.become(Text(textwrap.fill(line['text'],width=45) if role==line['speaker'] else ' ',font='DejaVu Sans',font_size=26,color=WHITE,weight='MEDIUM'))
                    if cap.width>7.13:cap.scale_to_fit_width(7.13)
                    if cap.height>.78:cap.scale_to_fit_height(.78)
                    cap.move_to([0,times[role]-2.57,0])
                scene=line['scene_id']
                if scene!=state['scene']:
                    state['scene']=scene
                    for role in chars:
                        new=pictures[role][scene].copy().move_to([x_art,times[role]-.02,0])
                        active_pictures[role].become(new)
            ci=max(0,min(len(cues)-1,bisect.bisect_right(cue_starts,now)-1))
            cue=cues[ci]['value'] if cues and cues[ci]['start']<=now<cues[ci]['end'] else 'X'
            for role,p in chars.items():
                active=(speaker==role and cue!='X');target=cue if active else 'X';lip=mouths[role]
                if target!=lip['last']:
                    lip['original'].set_stroke(opacity=0 if active else 1)
                    if active:
                        mouth=(NL.boca_fala('aberta' if cue in ('C','D') else 'meia') if role=='nina' else LIP.boca_visema(cue))
                        mouth.scale(p['_factor']);lip['extra'].become(mouth);lip['extra'].move_to(lip['original'].get_center())
                    else:lip['extra'].become(VGroup())
                    lip['last']=target
                y=.026*math.sin(now*2.2+(0 if role=='nina' else 2.0))
                p['grupo'].shift(UP*(y-state['last_y'][role]));state['last_y'][role]=y
                if active:lip['extra'].move_to(lip['original'].get_center())
                dx=.024*math.sin(now*.9+(1 if role=='nina' else 3))-state['last_eyes'][role]
                if role=='nina':
                    for eye in p['rosto'][0]:
                        for part in (eye[1],eye[2],eye[3]):part.shift(RIGHT*dx)
                    blink=(now+.3)%3.6<.12
                    for lid in p['rosto'][1]:lid[0].set_fill(opacity=1 if blink else 0);lid[1].set_stroke(opacity=1 if blink else 0)
                else:
                    for eye in (p['oe'],p['od']):eye.shift(RIGHT*dx);eye.set_opacity(.06 if (now+.7)%3.6<.12 else 1)
                state['last_eyes'][role]+=dx
        clock=Dot(point=ORIGIN,radius=.001,fill_opacity=0,stroke_opacity=0);self.add(clock)
        self.play(UpdateFromAlphaFunc(Group(*list(self.mobjects)),animate),run_time=duration,rate_func=linear)
