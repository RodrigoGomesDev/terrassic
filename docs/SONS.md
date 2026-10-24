# Sons próprios do Terrassic: plano

Status (24/10/2026): aprovado pelo Rodrigo (linha "boca fechada", sons livres CC0). O gerador está pronto e o **piloto** já está no mod com sons gerados por código, porque a rede da nuvem bloqueia todos os sites de sons livres. Quando os arquivos CC0 chegarem em `art/sounds/src/`, as receitas passam a usá-los.

## Hoje
Cada espécie usa sons vanilla com outro tom (por exemplo, o devastador mais grave para o T. rex). Funciona, mas o jogador reconhece os sons e eles não combinam com a proposta autoral do mod.

## Uma nota científica que muda o estilo
Ninguém sabe como os dinossauros soavam. Os parentes vivos mais próximos (aves e crocodilos) fazem **sons de boca fechada**: estrondos graves, arrulhos, sopros e chiados. O rugido de cinema é invenção. A proposta é seguir essa linha: o T. rex faz um estrondo grave que se sente mais do que se ouve, o Parassaurolofo faz um chamado de trompa (o som da crista dele já foi simulado por cientistas) e o Pteranodonte grasna. Os sons ficam críveis e diferentes de qualquer outro mod.

## Quantos sons
| Evento | Variações | Quem tem |
|---|---|---|
| Ambiente (idle) | 3 | todas |
| Ferido | 2 | todas |
| Morte | 1 | todas |
| Ameaça (roar, crista, chamado) | 1 ou 2 | predadores e quem tem exibição ou chamado |
| Passo | 2 | só as grandes (T. rex, Espinossauro, Braquiossauro, Tricerátops, Estegossauro, Anquilossauro) |
| Ataque (mordida, cabeçada, cauda) | 1 | quem luta |
| Nado ou bater de asas | 2 | Mosassauro, Pteranodonte |

Os filhotes usam os mesmos arquivos com tom mais agudo (já é assim hoje). Com 15 espécies dá **cerca de 120 arquivos curtos**, de 0,5 a 3 s cada, uns 3 MB no total.

## De onde vêm (opções)
1. **Gravações livres CC0 editadas.** Sons de animais reais (jacaré, avestruz, ema, casuar, elefante-marinho, camelo, baleia), cortados, misturados em camadas, mais graves ou mais lentos. Fonte: Freesound, só com licença CC0 (sem obrigação de crédito, uso comercial liberado). A rede da nuvem bloqueia o Freesound, então o Rodrigo baixaria um pacote que eu indicar (lista de links) e colocaria em `art/sounds/src/`. Fica bom e não custa nada.
2. **Gerados por código** em `tools/soundgen/`, com síntese (ruído filtrado, formantes, estrondo grave). Sai na hora e sem licença, mas soa mais artificial. Bom para camadas (o grave do T. rex, passos, bater de asas), fraco como som principal.
3. **Gravados ou comprados pelo Rodrigo.** A melhor qualidade e a mais autoral, mas é o caminho mais lento.

## Formato e pipeline
- **Formato:** OGG Vorbis, **mono** (o Minecraft só posiciona no espaço sons mono), 44,1 kHz, volume normalizado.
- **Fontes** em `art/sounds/src/` com um `CREDITS.md` (arquivo, autor, link, licença), e **receitas** numa tabela Python em `tools/soundgen/recipes.py`: arquivo de origem, corte, mudança de tom, esticar no tempo, camadas, equalização e fade.
- `tools/soundgen/build.py` usa o ffmpeg (já instalado na nuvem) e gera:
  - `assets/terrassic/sounds/<espécie>/<evento>_N.ogg`
  - `assets/terrassic/sounds.json`, com as variações, a distância de alcance (maior para os gigantes) e a legenda
  - `registry/ModSounds.java`, com os SoundEvents registrados pelo Architectury
  - legendas nos 3 idiomas (`subtitles.terrassic.<espécie>.<evento>`)
- O `gen_species.py` passa a apontar cada espécie para `ModSounds` em vez de `SoundEvents.*` vanilla. Quem ainda não tiver som próprio continua no vanilla, então dá para entregar aos poucos.
- Como nos sprites, um arquivo só é regravado quando o som muda, para o git não ver diferença à toa.

## Recomendação
Opção 1 (CC0 editado) para os sons principais, com a opção 2 para camadas graves, passos e asas. Começar com um **piloto de 3 espécies**: T. rex (estrondo), Parassaurolofo (trompa) e Pteranodonte (grasnado). O Rodrigo ouve no jogo, aprova o estilo, e depois as outras 12 seguem o mesmo padrão.

O que preciso do Rodrigo:
1. Aprovar a linha "boca fechada" (sem rugido de cinema).
2. Escolher a origem (1, 2 ou 3).
3. Se for a 1: baixar o pacote CC0 que eu listar e deixar em `art/sounds/src/`.

## Como ficou (piloto)
- Os sons são organizados em **conjuntos de voz** compartilhados (`tools/soundgen/recipes.py`): `boom_large` (terópodes grandes), `horn_hadrosaur` (hadrossauros) e `squawk_pterosaur` (pterossauros). Cada espécie escolhe um conjunto e um tom em `SPECIES_VOICE`, então centenas de espécies precisam de poucas dezenas de conjuntos, não de milhares de arquivos.
- Piloto: Tiranossauro (estrondo, ameaça, passos), Parassaurolofo (chamado de crista) e Pteranodonte (grasnado e bater de asas). As outras espécies continuam com os sons vanilla até ganharem um conjunto.
- `python3 tools/soundgen/build.py` gera os .ogg, o `sounds.json` e o `ModSounds.java`; `gen_resources.py` gera as legendas; `gen_species.py` liga as espécies aos conjuntos.

## O que baixar (Freesound, filtro de licença "Creative Commons 0")
Coloque os arquivos em `art/sounds/src/` com o nome sugerido e preencha `art/sounds/src/CREDITS.md`. 2 ou 3 de cada já bastam.

| Para o conjunto | Buscar no Freesound | Nome sugerido |
|---|---|---|
| boom_large | `alligator bellow`, `crocodile growl`, `ostrich boom` | `boom_jacare_1.wav`, `boom_avestruz_1.wav` |
| boom_large (ameaça) | `cassowary boom`, `elephant seal` | `ameaca_casuar_1.wav` |
| horn_hadrosaur | `didgeridoo low`, `conch shell horn`, `emu drumming` | `trompa_1.wav` |
| squawk_pterosaur | `heron call`, `pelican`, `gannet colony` | `grasnado_garca_1.wav` |
| squawk_pterosaur (asas) | `swan wings flap`, `large bird wings` | `asas_1.wav` |
| passos | `heavy footstep dirt`, `log thud` | `passo_1.wav` |

Depois é só me avisar: eu troco as receitas para usar os arquivos, mantendo o código como camada grave.
