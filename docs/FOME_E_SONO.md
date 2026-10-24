# Fome e sono (v0.6, fase 66)

Todo dinossauro tem um medidor de fome de 0 a 100 (começa em 70, salvo e sincronizado para o HUD da v0.8). Nada de
barra na tela ainda: o jogador percebe pelo comportamento (o animal pede, pasta, come carniça, para de caçar).

## Fome

| Regra | Como |
|---|---|
| Esvaziar | 1 ponto a cada `hungerInterval()` ticks: 600 (30 s) para um animal de 3 m, mais devagar quanto maior (`600 × (1 + (comprimento - 3)/10)`, arredondado às centenas: T. rex 1200, Alamosaurus 2200). Filhote: o dobro da velocidade. |
| Selvagem fora de cena | Em 1 de 4 batidas o selvagem ganha 1 em vez de perder: a fauna não morre de fome longe do jogador. |
| Herbívoro | Pasta (animação `graze`) 1/700 ticks, 1/150 com fome; se há grama, samambaia, folha, muda ou bloco de grama ao alcance, come de verdade: +8. |
| Carnívoro | Mordida em carcaça: +20 (fase 65). Saciado depois de encher. |
| Domado | Comida na mão: cura 10% **e** +25 (animação `eat`). Com baú, come sozinho a comida que achar na carga quando com fome (+25). |
| Bem alimentado | Fome > 60: cura 1 a cada 20 s. |
| Faminto | Fome 0: 1 de dano a cada 20 s (dano de fome). |
| Pedindo | Domado com fome < 30 e dono a 8 blocos: animação `beg` a cada 10 s e mensagem "%s está com fome" a cada 2 min. |
| Cadeia alimentar | Predador selvagem só caça (jogador ou presa) com fome < 85, acordado e não saciado: um T. rex bem comido passa por você. |

## Sono

| Regra | Como |
|---|---|
| Horas | Diurnos dormem de noite; `nocturnal=True` (Velociraptor, Dilophosaurus) dormem de dia. Ninguém dorme em tempestade. |
| Quem | Só selvagens (o domado obedece ao dono: sentar é o descanso dele). |
| Como | Goal `DinoSleepGoal` (prioridade 1, junto do sentar): deita (pose `sit`), não anda, não pasta, não caça. Acorda ao ser ferido, com alvo, na água, ou quando as horas acabam. |

## O que falta

- Barra de fome e sono no painel de montaria e na barra do bando (v0.8, HUD).
- Pterossauros e répteis marinhos: o medidor existe (base comum) mas eles não pastam, não comem carcaça nem dormem (IA própria); a fome deles só sobe com a comida do dono ou o truque do selvagem fora de cena.
- Animação própria de dormir (hoje é a de sentar).
