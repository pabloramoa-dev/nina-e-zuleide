#!/usr/bin/env python3
"""Gera prompts do roteiro ANTES de pedir imagens à SiliconFlow.
Cada cena tem dois prompts semanticamente distintos. Não duplicar imagens entre painéis.
"""
import argparse,hashlib,json,os,time,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'build'
STYLE='Modern Brazilian comic book illustration, lush colors, cinematic 2D, original background art, no text no letters no watermarks, vertical illustration.'

def generated_image(prompt,token,seed):
    payload=json.dumps({'model':'black-forest-labs/FLUX.1-schnell','prompt':prompt,'image_size':'768x1024','seed':seed}).encode()
    req=urllib.request.Request('https://api.siliconflow.com/v1/images/generations',data=payload,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=120) as r: obj=json.load(r)
            url=obj['images'][0]['url']
            if not url.startswith('https://'):raise ValueError('URL de resposta inválida')
            with urllib.request.urlopen(url,timeout=100) as r: return r.read()
        except Exception as e:
            if attempt==3:raise RuntimeError('Falha SiliconFlow, sem substituir por cartão de texto') from e
            time.sleep(3*(attempt+1))

def demo_image(out,idx,role,caption):
    # Aprovação técnica: demonstrações nunca são vendidas como ilustração paga.
    fg=(241,160,171) if role=='nina' else (148,211,227)
    img=Image.new('RGB',(768,1024),(25+idx*3,45+idx*3,76+idx*2));d=ImageDraw.Draw(img)
    d.rounded_rectangle((60,85,710,920),radius=55,fill=fg)
    d.ellipse((120+(idx*19)%260,180,540+(idx*19)%130,580),fill=(255,220,177),outline=(38,41,60),width=16)
    d.rectangle((135,660,635,700),fill=(50,64,79))
    d.polygon([(235,660),(520,620),(450,890)],fill=(255,230,175))
    d.text((135,760),f'PREVIA {role.upper()} / {idx+1:02d}',fill=(25,40,65))
    img.save(out,'JPEG',quality=88)

def run(demo=False):
    script=json.loads((B/'roteiro.json').read_text(encoding='utf8'))
    token=os.getenv('SILICONFLOW_API_KEY')
    if not token and not demo:raise RuntimeError('SILICONFLOW_API_KEY ausente; NÃO serão usados cartões vazios nem imagens iguais nos dois quadros. Configure este GitHub Secret.')
    folder=B/'images';folder.mkdir(parents=True,exist_ok=True)
    prompts=[];hashes=set()
    # Persistir o plano COMPLETO antes da primeira chamada paga.
    for scene in script['scenes']:
        for role in ('nina','zuleide'):
            prompts.append({'scene':scene['id'],'role':role,'prompt':STYLE+' '+scene[role+'_prompt']})
    if len(prompts)!=20 or len({p['prompt'].strip().casefold() for p in prompts})!=20:
        raise ValueError('O plano precisa de 20 prompts distintos antes de gerar imagens')
    (B/'prompts_imagens.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding='utf8')
    for scene in script['scenes']:
        k=scene['id'];pair=[]
        for role in ('nina','zuleide'):
            d=folder/role;d.mkdir(exist_ok=True)
            out=d/f'cena_{k:02d}.jpg'
            prompt=next(p['prompt'] for p in prompts if p['scene']==k and p['role']==role)
            if demo:demo_image(out,k,role,scene['resumo'])
            else:
                raw=generated_image(prompt,token,seed=k*101+(2 if role=='nina' else 89)+85000)
                out.write_bytes(raw)
                with Image.open(out) as im: im.convert('RGB').save(out,'JPEG',quality=88)
            h=hashlib.sha256(out.read_bytes()).hexdigest()
            assert h not in hashes,f'Imagem duplicada detectada no episódio: {out}'
            hashes.add(h);pair.append(out)
        assert pair[0].read_bytes()!=pair[1].read_bytes(),'Pares iguais proibidos'
    (B/'prompts_imagens.json').write_text(json.dumps(prompts,ensure_ascii=False,indent=2),encoding='utf8')
    print('Imagens geradas:',len(prompts),'Nenhuma duplicada; 10 por personagem')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--demo',action='store_true');a=ap.parse_args();run(a.demo)
