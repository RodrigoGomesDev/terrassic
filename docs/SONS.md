# Sons próprios do Terrassic: plano

Status (24/10/2026, tarde): **vozes v2**. Cada uma das 53 espécies tem a sua própria voz, 100% sintetizada por código (nada gravado, nada de terceiros): 20 arquétipos re-vozeados para o corpo de cada espécie, mais um som assinatura por espécie (436 sons). O Rodrigo testou o piloto e achou alguns sons parecidos com aldeão e galinha: eram os sons vanilla que 48 espécies ainda usavam (galinha, papagaio, camelo, cabra, porco, raposa...) e as gravações de aves do piloto. Ver "Vozes v2" no fim. As seções abaixo contam o plano original.

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

## Gravações (automático)
O download não depende do Rodrigo: `tools/soundgen/fetch.py` baixa no Mac gravações em domínio público (National Park Service, US Fish and Wildlife Service) e CC0 (OpenGameArt), sem login, e confere a licença. As receitas usam jacaré e bisão (T. rex), alce e mergulhão mais graves (Parassaurolofo), grou, garça e corvo (Pteranodonte) e asas grandes, com o som sintético por baixo como camada grave e como reserva enquanto a gravação não existe. Passo a passo: `docs/SONS_DOWNLOAD.md`. Licenças: `docs/LICENSES-SOUNDS.md`.

## Vozes v2 (24/10/2026, substitui o piloto)
O Rodrigo ouviu no jogo e alguns sons lembravam **aldeão** ou **galinha**. Os culpados:
- **Sons vanilla** que 48 das 53 espécies ainda usavam com outro tom: galinha (Gallimimus, Struthiomimus, Oviraptor, Citipati, passos do Mononykus), papagaio (Compsognathus, Troodon, Oviraptor, Citipati, Mononykus, Hesperornis), camelo (Maiasaura, Edmontosaurus, Corythosaurus), cabra (Pachycephalosaurus), porco (Thescelosaurus), vaca (Stegosaurus), raposa (Velociraptor, Dakotaraptor, Didelphodon), devastador, hoglin, farejador, golfinho, bacalhau e tartaruga. Os grunhidos de camelo, cabra e porco são os que mais lembram gente.
- **Gravações de aves do piloto**: gansos (ferido do hadrossauro), filhote de pelicano pedindo comida (ferido do pterossauro), cisnes, corvo, garça e grou. Mesmo mais graves, continuam soando como ave de quintal.

O que mudou:
- **Tudo sintetizado** em `tools/soundgen/synth.py` (numpy): uma garganta simulada. Fonte harmônica com jitter, subharmônicos (rosnado), "fry" (a voz quebrando em pulsos = chocalho) e tremor de garganta; filtro de formantes que se movem (boca abrindo e fechando), ressonância de tubo (a crista oca dos lambeossauros, a traqueia longa dos saurópodes), notch nasal, saturação e uma reverberação de ar livre. Animal grande = formantes baixos, que é o que faz o som parecer enorme.
- **Regras contra "gente" e "galinha"**: nenhum zumbido limpo no tom de voz humana com formantes de vogal (o "hmm" do aldeão) e nenhum cacarejo curto e ruidoso (galinha). Os grandes ficam abaixo da voz humana, os médios ganham chocalho, subharmônicos e chiado, os pequenos trinam em vez de cacarejar.
- **Graves audíveis**: um corte suave abaixo de 60 Hz em todos os sons, para a energia ficar onde fone e notebook tocam, sem perder o peso.
- `recipes.py` lista os 20 conjuntos e `SPECIES_VOICE` liga cada espécie a um conjunto e um tom (o Minecraft limita o tom a 0,5 a 2 e o filhote toca 1,5x mais agudo, então cada conjunto é feito para o tamanho dos seus animais).
- `python3 tools/soundgen/preview.py PASTA` gera um mp3 por conjunto (todos os sons em fila) e a folha de espectrogramas, para ouvir fora do jogo.
- As gravações em `art/sounds/src/` e `fetch.py` continuam no repositório como referência, mas nenhum conjunto as usa.

| Conjunto | Espécies | Sons |
|---|---|---|
| `boom_large` | T. rex, Tarbosaurus, Daspletosaurus, Albertosaurus, Giganotosaurus, Carcharodontosaurus, Spinosaurus | estrondo de boca fechada com tremor de crocodilo, rugido rouco (ameaça), latido ferido, gemido, passos |
| `growl_theropod` | Carnotaurus, Majungasaurus, Dilophosaurus | coaxar nasal com chocalho, bufo, estalo de mandíbula, silvo que vira rosnado (ameaça/exibição) |
| `rattle_raptor` | Velociraptor, Dakotaraptor, Troodon | chocalho de garganta, bufadas e estalos de bico, chiado com chocalho, grasnido rouco ferido |
| `trill_small` | Compsognathus, Mononykus | trinados assobiados que deslizam, "tsip", tagarelar |
| `drum_ratite` | Oviraptor, Citipati, Gallimimus, Struthiomimus, Therizinosaurus, Deinocheirus | tamborilar grave de boca fechada (como emu e casuar), arrulho-estrondo, chiado |
| `horn_hadrosaur` | Parasaurolophus, Corythosaurus | trompa da crista (voz deslizando sobre as ressonâncias fixas da crista) |
| `bellow_hadrosaur` | Edmontosaurus, Maiasaura | bramido pelo saco nasal inflado, buzinadas, bufo |
| `snort_ceratopsian` | Triceratops, Styracosaurus, Pachyrhinosaurus, Protoceratops | bufos pelas narinas, bramido-grunhido, respiração e batida de chifre |
| `honk_armored` | Ankylosaurus, Euoplocephalus, Stegosaurus | buzina nasal (passagens nasais em laço), fungadas, gemido rangido |
| `rumble_sauropod` | todos os saurópodes | ronco e gemido muito graves, expiração enorme, passos que tremem o chão |
| `grunt_ornithopod` | Pachycephalosaurus, Thescelosaurus | grunhido oco grave, bufada-grunhido, fungadas |
| `squawk_pterosaur` | Pteranodon, Quetzalcoatlus, Hatzegopteryx | grasnido gutural rouco, matraca de bico, bater de asa de membrana |
| `cry_seabird` | Ichthyornis | grito áspero de ave marinha, tagarelar, asas rápidas |
| `wail_diver` | Hesperornis | lamento longo e risada trêmula (como mergulhões num lago) |
| `blow_mosasaur` | Mosasaurus, Tylosaurus | bufo de respiração na superfície, ronco subaquático com bolhas, estalo de mandíbula |
| `moan_plesiosaur` | Elasmosaurus | gemidos suaves como de baleia, "whoop" subindo |
| `huff_turtle` | Archelon | respirações pesadas, chiado, grunhido |
| `drum_fish` | Xiphactinus | tamborilar de peixe grande (músculo da bexiga natatória), batidas |
| `bellow_croc` | Deinosuchus, Baurusuchus | bramido infrassônico com "dança da água", rosnado, chiado, passos |
| `hiss_mammal` | Didelphodon | chiado, tagarelar rosnado, fungadas |

Espécie nova: escolha um conjunto (ou crie um) em `SPECIES_VOICE`, rode `build.py`, `gen_resources.py` (legendas) e `gen_species.py`.

### Uma voz por espécie (v3)
O Rodrigo pediu que cada dino tenha som único. Os 20 conjuntos viraram **arquétipos** (`ARCHETYPES` em recipes.py) e cada espécie tem o seu conjunto, com o nome dela (`SPECIES`): o arquétipo é re-vozeado para o corpo do animal (`fp` tom, `fk` tamanho da garganta = formantes, `tf` ritmo, `rough` aspereza, sementes próprias) e ganha um **som assinatura** ligado à anatomia: o T. rex tem o estrondo de peito mais longo, o Carnotaurus bufa pelos chifres e buzina, o Dilophosaurus chocalha a crista, o Styracosaurus bate os chifres, o Mononykus zumbe e cava, a Citipati ronrona chocando, o Pachycephalosaurus bate a cúpula, o Tylosaurus bate o rostro, e assim por diante. O tom fica embutido no som (pitch 1.0 em `SPECIES_VOICE`). Espécie nova: uma linha em `SPECIES` com o arquétipo, o perfil e a assinatura.

## Efeitos próprios (fase 2)
Os sons temáticos que ainda vinham do Minecraft viraram 24 efeitos sintetizados (45 variações), em
`sounds/sfx/<nome>_<n>.ogg`, gerados pela mesma `tools/soundgen` (tabela `SFX` em `recipes.py`; legenda
`subtitles.terrassic.sfx.<nome>`; registro `ModSounds.SFX_<NOME>`).

| Efeito | Onde toca | Substituiu |
|---|---|---|
| egg_crack, egg_hatch | ovo racha e eclode (`DinoEggBlock`); o filhote já chama ao nascer | tartaruga |
| egg_lay | fêmea põe ovo (`DinosaurEntity`) | tartaruga |
| egg_break | ladrão de ovos (`EggThiefGoal`) | tartaruga |
| eat | dinossauro come | comer genérico |
| carcass_tear, carcass_squish, carcass_rot, carcass_bones | carcaça (`CarcassEntity`) | comer, slime, compostor |
| saddle_on, saddle_off, cargo | sela e cesto de carga | cavalo, tesoura, baú do burro |
| spear_throw, spear_hit, spear_ground | lança (`SpearItem`, `ThrownSpear`) | tridente |
| charcoal | desenho a carvão | aldeão cartógrafo |
| amber_ping | âmbar do refúgio da Katarina | ametista |
| discover | descoberta (`Research`): registrado, troca pendente (arquivo reservado ao Codex) | ametista |
| drum, chimes, clay_jar | tambor, sinos de osso, jarro de argila | bloco musical, mel |
| rift_pulse, rift_tear, rift_glitch | Fenda (`RiftStorm`, `RiftStormClient`) | ametista, enderman |

Continuam vanilla de propósito, porque o jogador já os reconhece: pegar item, respingo, virar página,
luneta, pincel, fogueira e mesa de cartografia.
