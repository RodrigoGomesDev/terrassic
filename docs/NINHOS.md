# Ninhos selvagens e procriação de selvagens (v0.6, fase 68)

Até aqui só os domados punham ovos (com a comida certa). Agora a fauna se reproduz sozinha, com teto por área, e
os ninhos selvagens são a forma de ter um predador antes do nocaute (v0.7): roubar o ovo.

| Regra | Como |
|---|---|
| Ovo selvagem | Propriedade `wild=true` do `DinoEggBlock` (a aparência é a mesma). Choca um filhote **selvagem**, que segue os adultos da espécie (`FollowParentGoal`) e cresce com a manada. Sem imprinting. |
| Roubar | Quebrar o ovo fresco (`hatch=0`) solta o item do ovo, como antes. Colocado de novo pelo jogador é um ovo comum (`wild=false`) e choca domado, imprintado em quem estiver a 12 blocos. |
| Defesa do ninho | Começar a quebrar um ovo selvagem (ou quebrá-lo) avisa os adultos selvagens da espécie a 20 blocos: acordam e tomam o jogador como agressor. Quem briga (ceratopsídeos, anquilossauros, titãs, predadores) ataca; quem foge debanda. Criativo não acorda ninguém. |
| Procriação selvagem | `wildBreedingTick` a cada 10 s, 1 chance em 12: adulto selvagem, bem alimentado (fome ≥ 80), acordado, sem alvo, sem montaria e fora do tempo de espera procura um par do sexo oposto nas mesmas condições a 16 blocos; os dois entram em "amor" e o `BreedGoal` vanilla faz o resto. Depois os dois gastam 15 de fome e esperam 5 min (`setAge(6000)`). |
| Teto por área | `wildPopulationCap()`: selvagens da espécie a 32 blocos (adultos e filhotes). Por largura da hitbox: ≥ 4 blocos (titãs, T. rex) 3; ≥ 2 (Triceratops, Edmontosaurus) 5; ≥ 1 (Velociraptor, Gallimimus) 8; menores (Compsognathus, Protoceratops) 12. Quem passa o teto não procria. |
| Ninhada | `clutchSize()` ovos selvagens ao lado da mãe: ≥ 3 de largura 1 ovo; ≥ 1,2 dois; menores três. Vaga ao redor (`findEggSpot`, raio 3). |
| Ninho de nascença | Uma manada em cinco nasce (spawn natural ou geração de chunk) com um ovo selvagem já posto ao lado de uma fêmea adulta. É o que se acha explorando. |
| Mar | `SwimmingDinosaur.wildNests()` = false: praia de desova do Archelon e nascimentos vivos no mar ficam para a v0.8. Pterossauros entram (o ovo fica onde houver chão a 3 blocos). |

Nada muda para os domados: um casal domado alimentado põe um ovo comum, como antes.

## O dom do ladrão de ovos (Oviraptor, fase 79)

Flag `egg_boost` do gerador. Um **Oviraptor** domado, adulto e acordado, a cada 5 s, tira mais 5 s do descanso de
procriação (`getAge() > 0`) de todo dinossauro domado adulto a 16 blocos: o casal alimentado volta a aceitar
comida em metade do tempo e põe ovos com o dobro da frequência. As galinhas no mesmo raio têm o `eggTime`
encurtado no mesmo ritmo. Não mexe nos selvagens nem nos filhotes. Por ter `customServerAiStep`, a flag é
incompatível com `roar`, `display`, `scoop`, `forage` e `night_guard` na mesma espécie.

Teste humano: dois dinos domados + um Oviraptor domado perto; o intervalo entre ovos deve cair pela metade;
galinhas perto botam visivelmente mais.

## O chocador (Citipati, fase 82)

Flag `brooder` do gerador (`DinosaurEntity.brooder()`), primeira espécie o **Citipati**.

- **Selvagem** (`entity/ai/BroodGoal`, prioridade 7): adulto sem alvo, de vez em quando (1/200 por tick) procura
  um bloco de ovo de dinossauro a 6 blocos (`nearestEgg`), anda até ele e senta ao lado por 2 a 4 minutos.
- **Pose de choco**: sentado (ou dormindo) com um ovo a 2 blocos, a animação de descanso passa de `sit` para
  `brood` (asas abertas sobre a ninhada); recalculada a cada 10 ticks (`isBrooding()`). Vale para domados: mande
  sentar junto do ninho.
- **Choco rápido** (`broodEggs`): a cada 160 ticks cada bloco de ovo a 2 blocos de um chocador sentado recebe um
  `randomTick` extra (metade avança um estágio). Os três estágios saem em ~1 minuto em vez de ~7 a 10.

Teste humano: Citipati selvagem perto de um ninho selvagem deve sentar e abrir as asas; ovo domado com um Citipati
domado sentado ao lado choca em cerca de um minuto; longe dele, no tempo normal.

## O que falta

- Conquista "Ladrão de ninhos" (roubar um ovo selvagem) na aba Caderno de Campo: espera a thread de conquistas.
- Fêmea choca sentada sobre a ninhada / modelo de ninho de gravetos (v0.8, com as colônias de Maiasaura).
- Balanço do teto por tipo de mundo (v0.8).
