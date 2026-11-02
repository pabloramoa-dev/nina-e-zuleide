# Nina e Zuleide — Tá Sabendo, Zuleide?

**Projeto independente preparado para importar em um repositório exclusivo** `pabloramoa-dev/nina-e-zuleide`. Não altera nem publica nos projetos existentes.

## Personagens

- **Nina:** adulta, atrevida, paqueradora, coleciona pretendentes, namoros que nunca dão certo e pequenos constrangimentos amorosos no condomínio. Humor malicioso leve, sem cenas explícitas.
- **Zuleide:** amiga confidente, fofoqueira e irônica, a voz da realidade que escuta, aconselha e participa das confusões.
- Animação **original em Manim**, importada dos repositórios `nina-me-contou` e `previsao-sul-fluminense` sem redesenhar os personagens. **Não usar Kugutu.**
- Câmera **tipo retrato 3x4**: rosto e ombros, sem corpo inteiro; Nina mantém seu tamanho aproximado, Zuleide com close maior.

## Regras do episódio

1. Cerca de **três minutos**, parte única, começo, meio, virada e fim. A primeira fala da Nina **obrigatoriamente é o gancho de antecipação** registrado em `data/50_episodios.json`.
2. **Duas imagens de apoio diferentes em cada cena**, uma no quadro de Nina e **outra no quadro de Zuleide**. Nunca repetir a mesma imagem simultaneamente; se os hashes forem iguais, a produção falha.
3. Antes de solicitar qualquer imagem à API paga, **gerar o roteiro completo**, definir cenas, prompts separados e salvar `build/prompts_imagens.json`.
4. SiliconFlow `black-forest-labs/FLUX.1-schnell` com **10 ilustrações por painel** (20 por vídeo). URLs do provedor devem ser baixadas imediatamente. Na ausência de API, falhar com aviso em vez de gerar quadros vazios. O modo demonstração usa imagens claramente marcadas como teste.
5. Voz original Kokoro; risos naturais gerados com a voz, reações e legendas embaixo do painel ativo.
6. Render CPU GitHub Actions, saída MP4 real **H.264 + AAC 540×960**, faststart, sem publicação automática em TikTok/Instagram.
7. Os personagens do episódio são fictícios; referências de vídeos virais fornecem **apenas situações e mecanismos narrativos**, não cenas, áudios nem diálogos de terceiros.

## Os 50 episódios

`data/50_episodios.json` contém 50 pautas originais **com gancho, situação e reviravolta**. `data/fontes_pesquisadas.json` registra 10 referências de vídeos/histórias divulgados e 3 fontes de tendências. **Não são 50 vídeos virais individuais verificados**; as pautas restantes são adaptações originais de padrões culturais dessas fontes.

## Configuração necessária

1. Crie um repositório vazio com o nome `nina-e-zuleide` em `https://github.com/new` e envie os arquivos deste pacote para a raiz.
2. Em **Settings → Secrets and variables → Actions**, configure `SILICONFLOW_API_KEY` (roteiros originais e imagens ilustrativas dos dois quadros). Secrets já salvos em outros repositórios não são automaticamente compartilhados.
3. Em **Actions → Nina e Zuleide - gerar episodio → Run workflow**, informe um número de 1 a 50. O checkbox `modo_teste` gera apenas demonstrações para QA, não material para publicação.
4. Depois da execução, baixe o artifact `nina-zuleide-ep-XX`, que inclui MP4 real, roteiro, timeline e imagens.

**Importante:** a integração final de um novo repositório depende de criá-lo no GitHub. A conexão de GitHub disponível no chat permite gravar arquivos em repositórios existentes, mas não possui ação de criar repositórios.

## Fonte principal da API de imagens

Documentação SiliconFlow: https://siliconflow.readme.io/reference/imagegeneration — endpoint `POST https://api.siliconflow.com/v1/images/generations`, formato `768x1024` e modelo `black-forest-labs/FLUX.1-schnell`. Configurar limite de gastos na conta do provedor. **Nunca gravar chaves em código ou artefatos.**

## Custo aproximado das imagens

20 imagens por episódio × US$ 0,0014 por imagem (preço público consultado) = **US$ 0,028/episódio**; 50 episódios, **US$ 1,40**, sem contar API de texto, armazenamento, impostos ou variação de preço. Preço pode mudar. Não há cobrança quando os workflows não são executados.

## Validação rápida

```bash
python -m unittest discover -s tests -v
python scripts/gerar_roteiro.py --episode 1 --demo
python scripts/gerar_imagens.py --demo
```

Os arquivos de demonstração não contêm falas produzidas e portanto não são um episódio final. Para uma produção, configure a chave SiliconFlow.


## Verificações adicionadas
Prompts completos são gravados antes de qualquer imagem paga. Roteiros usam Qwen3 na mesma conta SiliconFlow; imagens usam FLUX.1 Schnell no endpoint internacional api.siliconflow.com. O MP4 é decodificado integralmente e validado para H.264/AAC, yuv420p, 540x960, sincronismo e duração 135–225 segundos. Nenhuma publicação social é executada. Os 50 itens do catálogo são pautas: diálogos completos são produzidos na execução.
