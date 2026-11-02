#!/usr/bin/env python3
"""Descrições próprias para TikTok/Instagram sem publicar automaticamente."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'build'
s=json.loads((B/'roteiro.json').read_text(encoding='utf8'))
meta=json.loads((B/'metadata.json').read_text(encoding='utf8'))
no=meta['episodio'];title=s['titulo'];hook=s['gancho'];demo=' [TESTE - NÃO PUBLICAR]' if meta['tipo']=='demo' else ''
out=f'''# TikTok{demo}
🎭 Nina & Zuleide — Episódio {no:02d}: {title}\n\n{hook}\n\nNo prédio da Nina, a fofoca nunca acaba como começou! Assista até a revelação. 😂\n\n#NinaEZuleide #TaSabendoZuleide #Humor #Comedia #Novelinha #Historias\n\n---\n\n# Instagram Reels{demo}\n🎬 Episódio {no:02d} — {title}\n\n{hook}\n\nNina inventa uma história, Zuleide investiga e o condomínio inteiro ganha uma novidade. Qual seria sua reação?\n\n#NinaEZuleide #ReelsBrasil #HumorBrasileiro #Fofoca #Novelinha\n'''
(B/'legendas_tiktok_instagram.md').write_text(out,encoding='utf8');print('Descrições criadas, não publicadas')
