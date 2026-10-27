# Animações do Terrassic: diagnóstico e plano de revisão

Estudo de 27/10/2026, solicitado por Rodrigo. Base examinada: `94d8014b`, main.
Este documento complementa o estudo 02 com uma auditoria das **59 espécies atuais**.
Não altera modelos, recursos, IA, domesticação ou loot. As propostas abaixo ainda precisam de protótipo
e aprovação visual; medidas de prévia não equivalem a teste dentro do Minecraft.

## O que está prejudicando o resultado

O problema principal é a falta de uma sequência convincente de apoio e transferência de peso.
Hoje várias poses são calculadas para encostar no chão em um instante, mas a passagem entre elas
é feita girando e deslocando o animal inteiro. Mais suavização não resolve uma trajetória errada.

Há três trabalhos diferentes: **pose** (anatomia e silhueta), **animação** (como o peso passa de um apoio
para outro) e **controle** (quando tocar e interromper cada movimento). Precisamos dos três.

### Constatações no código e nos recursos

| Achado | Evidência atual | Efeito esperado / limite da conclusão |
|---|---|---|
| A carcaça toca nocaute em loop | `CarcassEntity.registerControllers`: `thenLoop(...knocked_out)`; as 59 animações têm alguma trilha variável | A carcaça reaproveita movimento de respiração. O comentário do renderer diz “frozen”, mas não há congelamento nesse controlador |
| Não existem clips próprios de morte e cadáver | 0/59 `death`, 0/59 `dead` nos exports | A morte não tem uma queda autoral distinta do nocaute |
| Sono, sentar e pouso compartilham pose | `DinosaurEntity.movementAnimation`: `isPerched`, `isSleeping`, `isInSittingPose` → `sit` (exceto incubação) | Não há leitura corporal própria de sono; pousar no ombro também usa esse caminho |
| Não há entrada/saída autoral do descanso | 0/59 `lie_down`, `stand_up`; nocaute não tem clip `knockout` | O controlador interpola diretamente entre loops. Isso não organiza apoios |
| Levantar é genérico | `rig.add_wake`: mesma duração de 1,8 s; root deitado até 0,4 s, zera até 1,2 s; sacode cabeça no final | Pterossauro, crocodilo e titanossauro recuperam equilíbrio pelo mesmo mecanismo básico |
| Acordar libera o comportamento imediatamente | `wakeUp` limpa o estado de nocaute e pode atribuir o jogador como alvo antes do término de `wake` | Risco de andar/atacar enquanto ainda levanta. Exige confirmação visual e teste de estado no jogo |
| Ações disputam ossos com a locomoção | `movement` e `action` separados; o segundo inclui `wake`, `eat`, `attack`; relatório lista ossos em comum | Sobreposição não é erro por si só, mas ações de corpo inteiro precisam de exclusividade explícita |
| Olhar automático não considera descanso/nocaute | `DinoGeoModel` chama `DefaultedEntityGeoModel.setCustomAnimations` sem filtrar o estado | A biblioteca 4.8.4 escreve pitch/yaw de `head`; pode contrariar uma pose relaxada. Não é prova de que o olhar muda em todo nocaute |
| Locomoção não acompanha a distância percorrida | Seleção `walk`/`run` por movimento/agressividade; sem ajuste de fase pela distância no controlador atual | Risco de pé deslizando, sobretudo acelerando, parando e virando; não foi quantificado nesta auditoria |
| Voo troca por limiar e janela de tempo | `FlyingDinosaur.movementAnimation`: velocidade vertical/horizontal e janela de 100 ticks | A troca entre bater asas e planar não garante uma fase compatível de asa; decolagem/pouso precisam de tratamento próprio |

O GeckoLib 4.8.4 local também aplica a rotação de morte padrão, até 90°, no renderer de entidades vivas.
`DinosaurRenderer` não a substitui. Ao mesmo tempo, `dropAllDeathLoot` cria uma `CarcassEntity` imediatamente.
Isso oferece um caminho para **dois corpos visuais durante a morte**, com poses diferentes. A existência dos
dois caminhos está confirmada no código; a duração, o efeito percebido e eventuais diferenças entre loaders
precisam ser gravados no cliente. Não foi feito esse teste nesta entrega.

## Auditoria reproduzível

Comando no ambiente de render já existente:

```sh
build/menu-render-venv/bin/python -B tools/validation/audit_animations.py --render
```

O script usa NumPy/Pillow e o avaliador do próprio `modelgen`. Não chama `build_all.run`, não exporta
assets para o jogo e verifica hashes de entrada antes/depois. `--out` permite outro diretório de saída.
O Python do sistema desta máquina não possui NumPy; o ambiente de render acima possui.

Saídas em `art/estudos/animacoes/v1/`:

- `auditoria.json`: cobertura de clips, comparação fonte/export, hashes, interseção de ossos entre ações
  e caminhada, e medidas de contato por espécie.
- `poses_atuais.png`: seis espécies, mesma câmera entre os quadros de cada linha; descanso, nocaute,
  pior amostra do levantar e fim do levantar. **Mostra o estado atual, não uma proposta melhorada.**
- `tyrannosaurus_wake_atual.gif`: sequência atual de levantar, com câmera fixa.

Cobertura encontrada: todas as 59 espécies têm `sit`, `knocked_out` e `wake`; nenhuma tem `sleep`,
`death`, `dead`, `lie_down`, `stand_up` ou `knockout`. As 59 fontes de animação correspondem aos JSONs
do jogo. Os ossos/cubos/UVs das 59 geometrias também correspondem aos exports. Foram conferidos 438
arquivos de entrada por hash antes/depois, sem alteração.

### O movimento falha mesmo quando a pose inicial encosta

Medição de `knocked_out` e `sit` em nove instantes e de `wake` em 37 instantes, incluindo extremos.
Referência: plano horizontal em y=0, macho, sem sela. A tolerância diagnóstica usada abaixo é -0,5 pixel
de **autoria**; não é meio bloco e não se converte igualmente para todas as espécies.

| Clip | Espécies com algum ponto abaixo de -0,5 px | Interpretação |
|---|---:|---|
| Nocaute parado | 0/59 | O ajuste do ponto mais baixo funciona nas amostras; não prova distribuição de peso correta |
| Levantar | 55/59 | A transição atravessa o plano em muitas espécies, apesar da pose inicial ajustada |
| Descanso | 3/59 | Brachiosaurus, Elasmosaurus e Archelon; os dois últimos exigem interpretação aquática |

Exemplos do menor y durante `wake`:

| Espécie | Menor y (px de autoria) | Instante |
|---|---:|---:|
| Tyrannosaurus | -3,968 | 1,40 s |
| Triceratops | -3,753 | 1,40 s |
| Velociraptor | -0,970 | 1,40 s |
| Argentinosaurus | -0,737 | 1,25 s |
| Pteranodon | -54,462 | 1,00 s |
| Quetzalcoatlus | -31,446 | 1,00 s |

Nos pterossauros, a recuperação genérica libera grandes rotações das asas enquanto o corpo ainda gira.
Além disso, o nocaute aplica `membranes_folded`, mas `add_wake` não recebe essa trilha específica.
Isso precisa de uma sequência própria de recolhimento e apoio; compensar tudo levantando o root
durante a passagem faria o animal levitar.

Há também **overshoot de interpolação**, não só poses mal escolhidas. Na prévia do Tyrannosaurus,
o root chega a 0° em 1,2 s, passa para **-6,074° em 1,4 s** e volta a 0° em 1,8 s; nesse meio tempo
a posição vertical do root chega a -1,225 px. As chaves não pedem esse tombamento oposto: ele nasce
da curva Catmull-Rom entre as chaves. Curvas com tangentes controladas ou trechos lineares/monotônicos
devem ser usados em apoios e paradas. Não trocar todas as curvas do mod por linear indiscriminadamente.

O Pteranodon termina `wake` com rotação animada zero nas três articulações da asa, enquanto `idle`
começa com a asa dobrada. A pose final precisa mirar o repouso real, não simplesmente zerar o rig.
Esses valores foram conferidos no avaliador da fonte; a mistura efetiva no jogo continua pendente.

**Limites:** o avaliador de prévia usa Catmull-Rom; não reproduz a mistura de controladores, rotação
extra do renderer, olhar do jogo ou a física. Mede cantos dos cubos, não malha de colisão nem anatomia.
Nove/37 amostras podem perder extremos entre amostras. O plano não representa ladeiras, lajes ou água.
Espécies aquáticas podem atravessar esse plano legitimamente durante o nado: seus números não são uma
reprovação do comportamento aquático. A carcaça encalhada é um cenário separado. Não mede clipping entre
membros ou apoio de barriga: uma ponta de asa no chão não garante que o tórax esteja apoiado.

## Direção de movimento

Manter os modelos blocados e o estilo Minecraft. A melhora deve vir de poses legíveis, apoios e ritmo.
Nada depende de aumentar cubos, instalar outra biblioteca ou substituir as texturas.

### Separar quatro situações que hoje se confundem

| Situação | Como deve ser lida |
|---|---|
| Descanso acordado | Corpo acomodado, cabeça ainda atenta; respiração discreta, pequenas mudanças ocasionais de atenção |
| Sono | Cabeça apoiada/recolhida conforme o grupo, pálpebras quando o rig permitir, sem seguir o jogador |
| Inconsciência | Assimetria relaxada, pescoço e membros cedidos, respiração lenta; asas recolhidas com articulações coerentes |
| Morte | Perda de sustentação, impacto e acomodação; depois imobilidade sem respiração, olhar ou gestos de recuperação |

Não usar a postura de um fóssil como filme exato de como o animal caiu. Evidência fóssil, analogia com
animais vivos e decisão artística são níveis diferentes de certeza.

### Morte e levantar: encenar apoios

**Morte:** reação curta → membro cede → massa desce com rotação → contato do corpo → acomodação de
pescoço/cauda → `dead` imóvel. O peso chega antes das partes soltas terminarem de acomodar.
Sem quique exagerado, sangramento ou gestos cartunescos. Duas variantes de lado podem vir depois que uma
estiver aprovada. Escolher variante uma vez; não sortear por frame ou trocar após recarregar a carcaça.

**Levantar do nocaute:** recuperar cabeça/apoio → trazer membros para uma base útil → levar o peso sobre
os apoios → elevar quadril/tórax → estabilizar → liberar caminhada. Cauda contrabalança, não vira manivela.
Não basta inverter o filme da morte. Levantar do descanso também precisa de clip próprio.

O root atual fica no chão: girá-lo sozinho tomba todo o animal como uma peça rígida em uma dobradiça.
Precisamos de pivôs e deslocamentos por fase, ancorados aos pontos de apoio. O torso não pode atravessar
um pé plantado nem subir por causa de uma ponta de chifre. Marcar apoios no rig é mais útil nesta fase
do que acrescentar várias curvas seno ao corpo.

Durações iniciais para o protótipo, **hipóteses artísticas, não medidas paleontológicas**:
pequenos bípedes levantando em 0,8–1,4 s; grandes terópodes/ceratopsianos em 1,8–3 s;
saurópodes em 3–5 s. Pterossauros precisam primeiro de coreografia própria, sem impor o tempo de ave.
Decidir o tempo final vendo o protótipo em velocidade normal, inclusive quando há ameaça próxima.

### Cada grupo precisa de uma solução

| Grupo / piloto | Revisão principal |
|---|---|
| Grandes terópodes — Tyrannosaurus | Apoio das pernas, massa sobre o quadril, cabeça e cauda como contrapesos; braços pequenos não sustentam o corpo |
| Pequenos terópodes — Velociraptor | Agachamento compacto, recuperação rápida com pés sob o corpo; descanso não precisa imitar queda de morte |
| Ceratopsianos — Triceratops | Cabeça pesada apoiada, quatro membros com fases distintas; evitar que chifres sejam o único contato que calibra a pose |
| Hadrossauros — Parasaurolophus | Descanso com membros dobrados e passagem coerente entre quatro e duas patas quando aplicável |
| Anquilossauros/estegossauros | Evitar placas/clava atravessando o chão e testar largura do corpo; não compartilhar todos os ajustes com ceratopsianos |
| Saurópodes — Argentinosaurus | Levantar em etapas, apoios largos, pescoço acompanhado por atraso pequeno; não transformar o corpo em gangorra |
| Pterossauros — Pteranodon | Asas recolhidas até o corpo estar sustentado, caminhada quadrúpede, transições de decolagem e pouso próprias |
| Aves — Ichthyornis | Apoio dos pés, pescoço recolhido no descanso, asas junto ao corpo; separar recuperação do sono, do nocaute e pouso no ombro |
| Crocodiliformes — Deinosuchus | Corpo baixo, patas laterais, pouco deslocamento vertical; elevar o tórax com os membros antes de andar |
| Marinhos — Mosasaurus/Elasmosaurus | Inconsciência e morte na água sem exigir apoio de chão; equilíbrio por cauda/nadadeiras; encalhado tratado à parte |
| Quelônios e peixes | Rig próprio: casco e nadadeiras não podem receber a mecânica de pernas de mamífero; peixe não “levanta” como terrestre |

## Caminhada, voo e ações

**Caminhada:** desenhar primeiro contato, apoio, saída e balanço. Durante o apoio, o pé deve ficar
aproximadamente parado em relação ao mundo. Usar distância horizontal real para acumular fase,
com comprimento de passada e duração de referência por grupo. Incluir partida, frenagem e mudança
de direção; não reiniciar o ciclo em cada oscilação do limiar de velocidade. Usar histerese entre andar/correr.
Quatro patas exigem ordem de contato definida; gigantes não devem apenas executar uma caminhada acelerada
com grande balanço do tórax. Agressividade pode influenciar postura, sem obrigar corrida quando quase parado.

**Curvas:** limitar e amortecer torso/cabeça, deslocar o peso para o apoio interno e dar atraso moderado à
cauda. Para uma mudança muito fechada e lenta, usar passos de reposicionamento em vez de girar os pés
plantados. Resolver primeiro o caso plano; depois o terreno.

**Voo:** ciclo com batida descendente legível, recuperação de asa e pontas com atraso. Planeio mantém
sustentação visual e ajustes pequenos, sem parecer congelamento. Transitar em uma pose compatível de asa,
com inclinação proporcional à curva. Decolagem tem preparação/impulso; pouso tem aproximação/freio/contato/
recolhimento. Sincronizar com o estado físico existente: melhorar a animação não corrige sozinho um animal
que permanece parado no ar. Distinguir a revisão da IA/velocidade da revisão das asas.

**Ações:** ataque com preparação, contato e recuperação; mandíbula e som de mordida/rugido alinhados à
fase útil. Só escrever ossos necessários na camada de ações. Algumas ações podem acompanhar a caminhada;
queda e levantar precisam de corpo inteiro exclusivo. Não deslocar o corpo por animação para alcançar
um alvo que o servidor considera fora de alcance. Não alterar dano/cooldown só para combinar com o clip
sem revisar combate junto.

**Vida em repouso:** respiração no tórax, sem levantar o corpo inteiro do chão; olhar distribuído por pescoço
e cabeça, com limites por estado; dois ou três gestos curtos por grupo, com intervalos e fase individual.
Não aplicar aleatoriedade contínua a todos os ossos. O animal deve conseguir ficar quieto.

## Controle e integração propostos

Manter GeckoLib **4.8.4** nesta entrega. Não há necessidade demonstrada de migrar biblioteca para corrigir
esses defeitos. A documentação oficial descreve transições e prioridade por ordem de controladores;
isso não fornece automaticamente biomecânica ou composição aditiva independente por osso.

1. Definir estados visuais exclusivos: morrer/morto, entrar em nocaute/inconsciente, levantar, entrar em
   descanso/descansar/dormir/sair do descanso, locomoção. Morte interrompe todos; dano pode acordar sono;
   nocaute não pode ser cancelado por um gesto aleatório. Sono e torpor continuam mecânicas diferentes.
2. Manter o servidor dono do estado e das transições que afetam movimento/combate. Sincronizar início,
   variante e estado, sem enviar transformações dos ossos por tick. O cliente calcula a pose.
3. Reservar a camada de ações para gestos compatíveis; bloquear ações incompatíveis durante corpo inteiro.
   Desligar o olhar procedural durante morte/nocaute e ajustar durante sono. Restaurar os ossos ao sair
   do estado para não contaminar a próxima entidade renderizada pelo mesmo modelo.
4. Resolver a passagem vivo → carcaça com **um corpo visível** e pose final igual à inicial do cadáver.
   Preservar loot, UUID/sexo/escala, tempo de apodrecimento e recarga. Não adiar a coleta de loot nem duplicá-lo
   para obter um efeito visual. Comparar um atraso somente visual da carcaça com uma queda encenada nela;
   escolher após protótipo, incluindo caso de cliente que recebe a entidade atrasado.
5. Cliente que entra depois da queda ou recarrega o mundo deve ver `dead`, sem repetir a morte nem acordar
   o cadáver. Reload de inconsciente mostra repouso; reload de sono não reinicia uma longa animação de entrada.
6. Metadados dos clips: apoios, passada, fases úteis, duração, posição final e compatibilidade de interrupção.
   Exportar da fonte em `tools/modelgen`; não editar apenas JSONs gerados. Usar nomes estáveis no contrato do rig.

Evitar ragdoll físico como primeira solução. Acrescentaria física, colisões, persistência e sincronização
que este problema não exige. Uma boa queda autoral com carcaça estável resolve o principal com escopo menor.
IK de pés e ajuste limitado do corpo ao terreno vêm depois das poses e do controle corretos. Não usar
correção global do menor canto por frame: asa, cauda ou chifre podem ser o ponto mais baixo e levantar tudo.

## Ordem de implementação e coordenação

| Pacote | Entrega revisável | Arquivos a reservar antes de começar |
|---|---|---|
| 1 — Piloto terrestre | Tyrannosaurus e Triceratops: repouso, queda, cadáver e levantar; vídeo antes/depois no mesmo cenário | `rig.py`, arquétipos envolvidos, `DinosaurEntity`, `DinosaurRenderer`, `DinoGeoModel`, `CarcassEntity`/renderer; conferir geradores de testes |
| 2 — Controle | Exclusividade, acordar sem deslizar, entrega à carcaça, recarga e multiplayer | Classes-base acima e roteiros reais de nocaute/carcaças; manter regressões de domesticação |
| 3 — Voo | Pteranodon e Ichthyornis: asas, recuperação, decolagem/pouso; comparar navegação com animação | Arquétipos pterosaur/bird, `FlyingDinosaur`, metas/controlador apenas se o problema for físico |
| 4 — Passada | Pilotos andando/virando/parando com pé apoiado; piloto gigante Argentinosaurus | Arquétipos e controlador de locomoção; metadados de passada |
| 5 — Expandir famílias | Aplicar somente o piloto aprovado, com ajustes de proporção, casco/placas/cauda/asas | Uma família por vez; sem regeneração geral sobre trabalho de outra frente |
| 6 — Terreno e acabamento | Ajustes de apoio no terreno, olhar, respiração, ociosos, sons e LOD de animação | Cliente/modelo e metadados; medir desempenho antes de aumentar custo |

Responsabilidade proposta: Codex cuida do controle, auditoria e regressões; a frente de modelos cuida de
key poses e curvas por arquétipo; Rodrigo aprova a sensação do movimento nos pilotos. Isso é uma divisão
proposta, não uma tarefa já enviada a outro agente. Reservar arquivos no quadro antes de implementar.

Um piloto convincente exige várias iterações visuais. O custo maior é acertar apoios e recuperação por família;
replicar curvas antes da aprovação multiplicaria o retrabalho. Não prometer uma revisão das 59 espécies
em um único passe automático. O pacote 1 deve ser pequeno o suficiente para comparar lado a lado.

## Critérios para aprovar

- Descanso, sono, nocaute e morte reconhecíveis sem ler a interface. Cadáver sem respiração ou olhar.
- Sem salto de posição entre estados, sem asa abrindo através do chão, sem pés deslizando no levantar.
- Após contato, cabeça/tórax apoiados de forma coerente; não basta um único cubo tocar y=0.
- Próxima animação começa na mesma pose útil da anterior; avaliar também velocidade/continuidade na emenda.
- Filhote, macho/fêmea, sela, encalhado, pousado e diferentes escalas revisados separadamente.
- No jogo: plano, ladeiras, borda de bloco, laje/escada, água rasa/profunda; lateral, frente e 3/4; velocidade
  normal e câmera lenta. Guardar gravações no mesmo enquadramento antes/depois, sem shader primeiro.
- Fabric e Forge: servidor dedicado com dois observadores; entrar durante a queda, sair/voltar, descarregar
  chunk, reiniciar servidor, matar durante nocaute/levantar e verificar loot uma única vez.
- Distância/FPS: verificar fase sem reiniciar ao sair do frustum; tempo de estado não pode depender do FPS.
  IK futuro só onde a criatura é visível/próxima, com amostragem de terreno orçada e fallback estável.
- Integridade, orçamento e build dos dois loaders após mudança de produção, além das regressões de
  nocaute, alimentação e persistência. Esses testes não aprovam a estética sozinhos.

## Referências consultadas

Fontes primárias consultadas em 27/10/2026; a aplicação artística ao Terrassic é uma proposta deste estudo.

- [GeckoLib 4 — Defining Animations in Code](https://github.com/bernie-g/geckolib/wiki/Defining-Animations-in-Code-%28Geckolib4%29):
  transições, ossos compartilhados e precedência. Também foi lido o source JAR 4.8.4 local de
  `GeoEntityRenderer` e `DefaultedEntityGeoModel`, usado pelo projeto.
- [GeckoLib 4 — The Animation Controller](https://github.com/bernie-g/geckolib/wiki/The-Animation-Controller-%28Geckolib4%29):
  controladores concorrentes, ordem de avaliação e duração de transição. Não confundir com a API da versão 5.
- [Xu & Norell, 2004 — Mei long, postura de sono](https://ivpp.cas.cn/sourcedb/zw/rck/yszj/202311/P020140314310256430525.pdf):
  postura compacta em um pequeno terópode; não prova que todos os grupos dormiam igual.
- [Milner et al., 2009 — rastro de repouso de terópode](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0004591):
  evidência de agachamento e orientação das mãos; referência anatômica, não receita de queda.
- [Witton & Habib, 2010 — mecânica de pterossauros](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0013982):
  anatomia e lançamento diferem das aves; usar coreografia própria e distinguir pterossauros entre si.
- [Naturalis — modelo de caminhada do T. rex, 2021](https://www.naturalis.nl/persberichten/nieuw-model-laat-tyrannosaurus-rex-lopen-met-een-swingende-staart):
  referência dos pesquisadores para relacionar cauda, ritmo e passo. Não fornece a velocidade exata de toda
  espécie nem obriga o balanceamento do jogo a copiar uma estimativa biomecânica.

O estudo 02 já apontava passada, camadas e terreno, mas era amplo e usava uma base de 53 modelos.
Esta auditoria localiza o defeito atual das poses/transições e propõe começar por ele.

## Validação desta entrega

- Auditoria executada duas vezes; a segunda incluiu comparação de geometria e gerou as prévias finais.
- `check_project.py`: 59 espécies, 4.341 JSONs e 1.848 chaves em três idiomas, sem erros.
- `check_spawn_budget.py`: 1.000 cenários de escalonamento e 10.000 de orçamento passaram.
- Prancha final inspecionada. Não foi executada build nem revisão visual no jogo, pois esta entrega
  contém estudo/ferramenta/evidências e não muda código Java ou recursos de produção.
