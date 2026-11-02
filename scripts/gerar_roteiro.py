#!/usr/bin/env python3
"""Transforma PAUTA (que nunca copia vídeo alheio) em diálogo original de ~3min.
Requer OPENAI_API_KEY para a produção. --demo escreve rascunho para QA, não produção.
"""
from __future__ import annotations
import argparse,json,os,re,urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
CAT=BASE/'data'/'50_episodios.json'
OUT=BASE/'build'
STYLE='''Duas personagens adultas: Nina, paqueradora atrevida, impulsiva e dona de namoros que sempre acabam em situações hilárias; Zuleide, confidente e amiga fofoqueira, cética, sarcástica, acolhedora. Português brasileiro coloquial. Tom ousado apenas em duplos sentidos leves, nunca conteúdo explícito. Originalidade: não copiar falas, pessoas nem sequências específicas de vídeos reais. Uma parte única, início/meio/fim, revelação antes do final. Gancho no PRIMEIRO turno que antecipa uma reviravolta sem entregá-la. Cerca de 460-510 palavras, 45-55 falas, 7-12 cenas, média de 165-195 segundos de fala. Cada fala breve. Alternância dinâmica, nenhuma imagem idêntica entre painéis. Risadas ocasionais naturais. Sem cliffhanger e sem título parte 1. Formato JSON puro.'''

def prompt(item):
    return (STYLE+'\nPAUTA ORIGINAL: '+json.dumps(item,ensure_ascii=False)+'\n'
        'Retorne objeto JSON: {"titulo":string,"gancho":string,"scenes":[{"id":0..9,"resumo":string,"nina_prompt":string,"zuleide_prompt":string}],"lines":[{"speaker":"nina"|"zuleide","text":string,"scene_id":int,"laugh_after":boolean}]}. '
        '10 cenas com 2 prompts cada, visual estilo revistinha moderna, pictórico sem letras, sem personagens Nina ou Zuleide nas imagens de apoio (elas já aparecem à esquerda), Nina POV AÇÃO e Zuleide POV PISTA/REAÇÃO; contextos visuais realmente diferentes. '
        'Cada scene id referenciado pelas falas. Pelo menos 46 falas. A primeira fala idêntica ao gancho fornecido. A última é piada final completa. '
        'Quase 3 minutos com fala natural, não completar texto com repetição.')

def generate_paid(item):
    key=os.getenv('SILICONFLOW_API_KEY')
    if not key:raise RuntimeError('SILICONFLOW_API_KEY ausente. Configure no GitHub Secrets para gerar histórias na produção. Use --demo apenas para teste técnico.')
    body={'model':os.getenv('NINA_SCRIPT_MODEL','Qwen/Qwen3-30B-A3B-Instruct-2507'),'messages':[{'role':'system','content':'Você escreve roteiros originais de comédia brasileira, adequados a todas as idades. Responda somente JSON válido.'},{'role':'user','content':prompt(item)}], 'response_format':{'type':'json_object'},'temperature':0.85,'max_tokens':7000}
    req=urllib.request.Request('https://api.siliconflow.com/v1/chat/completions', data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=100) as r: payload=json.load(r)
    return json.loads(payload['choices'][0]['message']['content'])

def demo(item):
    # Demonstração técnica não substitui um roteiro original final.
    beats=[item['situacao'], 'Nina inventa duas explicações para o ocorrido.', 'Zuleide pede provas do que aconteceu.', 'Uma mensagem faz a confusão crescer.', 'Nina tenta organizar um encontro por conta própria.', 'Os moradores começam a comentar no grupo.', 'Zuleide encontra uma pista no corredor.', 'A pista contradiz a teoria de Nina.', 'A verdade aparece quando alguém explica tudo.',item['virada_final']]
    lines=[];scenes=[]
    for k,beat in enumerate(beats):
        scenes.append({'id':k,'resumo':beat,'nina_prompt':f'Quadrinho A {k}: {beat}. Objetos e ação no corredor; cores rosa e coral, câmera frontal, zero texto.', 'zuleide_prompt':f'Quadrinho B {k}: pista diferente sobre {beat}. Papel, tela de celular, documento ou objeto relevante, paleta azul e amarelo, câmera macro, sem texto.'})
        for j in range(5):
            speaker='nina' if j%2==0 else 'zuleide'
            variants=([f'Zuleide, escuta essa: {beat}',f'Eu tenho uma teoria que vai explicar esse mistério.',f'Não está vendo? Essa história tem outra coisa por trás!'] if speaker=='nina' else [f'Minha filha, de onde você tirou isso?',f'Prova primeiro, fofoca depois!'])
            text=variants[j//2]
            lines.append({'speaker':speaker,'text':text,'scene_id':k,'laugh_after':j==4 and k in (2,5,8)})
    lines[0]['text']=item['gancho_antecipacao']
    lines[-1]['text']='Se for verdade, até o elevador vai precisar de terapeuta!'
    return {'titulo':item['titulo'],'gancho':item['gancho_antecipacao'],'scenes':scenes,'lines':lines,'demo':True}

def validate(doc,item,production):
    assert isinstance(doc['lines'],list) and 42<=len(doc['lines'])<=65,'Roteiro com número de falas incorreto'
    assert len(doc['scenes'])==10,'Exatamente dez cenas por episódio'
    assert doc['lines'][0]['speaker']=='nina','Gancho deve ser da Nina'
    assert doc['lines'][0]['text'].strip().rstrip('.!')==item['gancho_antecipacao'].strip().rstrip('.!'),'Gancho de antecipação não corresponde ao planejado'
    ids={s['id'] for s in doc['scenes']}
    assert ids==set(range(10)),'IDs de cena inválidos'
    for scene in doc['scenes']:
        assert scene['nina_prompt']!=scene['zuleide_prompt'],'Imagens de Nina e Zuleide não podem ter prompts idênticos'
        assert len(scene['nina_prompt'])>25 and len(scene['zuleide_prompt'])>25
    for line in doc['lines']:
        assert line['speaker'] in ('nina','zuleide') and line['scene_id'] in ids and len(line['text'].strip())>=3
    words=sum(len(re.findall(r'\w+',x['text'])) for x in doc['lines'])
    if production:
        assert 400<=words<=590,f'Roteiro fora da duração aproximada: {words} palavras'
        assert not doc.get('demo')
    return words

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episode',type=int,required=True);ap.add_argument('--demo',action='store_true');args=ap.parse_args()
    all_items=json.loads(CAT.read_text(encoding='utf8'))
    item=next(x for x in all_items if x['numero']==args.episode)
    doc=demo(item) if args.demo else generate_paid(item)
    words=validate(doc,item,production=not args.demo)
    OUT.mkdir(exist_ok=True)
    (OUT/'roteiro.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'metadata.json').write_text(json.dumps({'episodio':args.episode,'titulo':item['titulo'],'tipo':'demo' if args.demo else 'producao','source_id':item['inspiracao_id'],'words':words},ensure_ascii=False,indent=2),encoding='utf8')
    print('Roteiro validado:',args.episode,'falas:',len(doc['lines']),'palavras:',words)
