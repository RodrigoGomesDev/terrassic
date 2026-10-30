# HUD "Âmbar" (v0.14)

Pedido do Rodrigo em 30/10/2026: o HUD antigo estava "muito IA e muito chapado", e ele queria algo único. O estudo
(três direções, comparação com o Vanilla+ e uma segunda versão com texturas) terminou com a escolha da **versão 1 do
Âmbar**, com o fundo das peças em escuro chapado (18:06Z). Prévia aprovada: https://claude.ai/artifact/A8gmsTnR4hExM16C4XD7Bs.
Os geradores das imagens (`dirF.py`, `dirB.py`) ficam fora da árvore, em `/mnt/project-files/hud-estudo/scripts/`; o
código do jogo segue as mesmas medidas, pixel a pixel.

Regras do estudo:

- Vida, fome, XP e barra de pulo **do jogador** ficam como no Minecraft. O Âmbar só vale para as peças do mod.
- Nada no alto do meio nem no alto à direita da tela.
- Cada peça liga e desliga em `config/terrassic-client.json` (a tela de opções vem na v0.14.2).
- Sem barra do bando: o jogador pode ter vinte dinos. Os avisos à direita ocupam o lugar dela.

## O visual

Código: `client/ui/AmberHud.java`.

- **Placa de basalto**: polígono com quinas lascadas, contorno de 1 px `#0E0B0E`, fundo chapado `#1C181E`, borda clara no
  alto e à esquerda, escura embaixo e à direita. Cada peça tem a sua forma; a textura é feita uma vez e guardada.
- **Sulco**: a barra é cortada na pedra (fundo preto, lábio de baixo claro), com o preenchimento em três tons e um
  menisco claro na ponta. Vida em vermelho, fome em âmbar, torpor em lilás, doma em verde, stamina em azul.
- **Gota de âmbar**: o bicho de verdade, ao vivo, preso numa gota de resina e tingido de âmbar escuro, com bolhas e
  um brilho por cima.
- **Letras**: a Sedimento do mod, com sombra dura de 1 px.

## Parte 1 (v0.14): placa da montaria, avisos e modo compacto

### Placa da montaria

No canto superior esquerdo, montado num dino seu:

- A gota de âmbar com o bicho, pendurada na borda esquerda da placa.
- "Tiranossauro · Nv 23" (o nível em âmbar). A placa alarga quando o nome é longo.
- Vida e fome em sulcos. A vida aparece em números por 3 segundos quando muda (opção para deixar sempre).
- O **encaixe do especial**: o âmbar enche de baixo para cima enquanto o especial recarrega e acende quando está
  pronto. Hoje só os grandes terópodes têm um (o rugido forte, clique direito com a mão vazia). O encaixe mostra um
  mouse quando o especial é um botão do mouse e a letra quando é uma tecla.
- A terceira linha da prévia, a stamina, entra junto com a stamina da montaria. Até lá a placa tem duas linhas.

### Avisos

No meio da borda direita, até quatro de cada vez. Entram deslizando, ficam 6 segundos e saem. Valem para qualquer
bicho seu, perto ou longe:

| Aviso | Cor | Linha de baixo |
|---|---|---|
| Subiu de nível | âmbar | "Tiranossauro · Nv 24" |
| Domesticado | âmbar | nome e sexo |
| Nasceu um filhote (ovo chocado perto de você) | verde | nome e sexo |
| Com fome / Com fome, longe de você | laranja | nome (uma vez a cada 2 minutos por bicho) |
| Acordou bravo (o bicho que você nocauteou) | laranja | nome |
| Tricerátops morreu | vermelho | "X 214  Y 71  Z -880" |

Eles substituem as mensagens da barra de ação. Com `"hud_notices": false`, voltam para a barra de ação.

### Modo compacto

`"hud_style": "compact"`. Sem placas. A vida da montaria vira dez corações vanilla de montaria acima da barra de fome,
cada um valendo 10%. O especial vira uma linha de texto acima da hotbar ("Rugido forte pronto", "Rugido forte em 12 s").
Os avisos aparecem sem placa: o bicho e duas linhas de texto, alinhados à direita.

### Opções (`config/terrassic-client.json`)

| Opção | Padrão | O que faz |
|---|---|---|
| `hud_style` | `"amber"` | `"amber"` ou `"compact"` |
| `hud_mount` | `true` | Placa da montaria |
| `hud_notices` | `true` | Avisos à direita (`false` = barra de ação) |
| `hud_numbers_always` | `false` | A vida da montaria em números o tempo todo |

A opção antiga `hud_pack` sai do arquivo sozinha.

## Parte 2 (v0.14.1): placa de nome, barras de doma e cartão da Lupa

Código: `client/DinoNameplate.java`, `client/LensOverlay.java`.

### Placa de nome

Olhando para um dino a até 24 blocos (sem a Lupa na mão e fora o que você monta), aparece sobre a cabeça dele uma
placa pequena, do mesmo tamanho a qualquer distância:

- uma gotinha na cor do temperamento: verde para domado, vermelho para predador selvagem, âmbar para os outros selvagens;
- "Tiranossauro · Nv 23", com o nível em âmbar;
- a vida num sulco.

A posição na tela vem da câmera do quadro (`mixin/client/LevelRendererMixin`). Some 0,5 s depois que você desvia o olhar.

### Barras de doma

Num bicho desmaiado, à esquerda da placa de nome: "Desmaiado" com o tempo até acordar, o torpor (lilás) e a doma
(verde). Os números vêm do servidor pelo mesmo pedido da Lupa, que agora responde também para um bicho desmaiado
sem a Lupa na mão.

### Cartão da Lupa

O mesmo cartão de antes, no visual Âmbar: a gota de âmbar com o bicho, nome e nível, ♀ ou ♂, idade e tamanho,
selvagem ou de quem; as barras em sulcos (vida, fome, torpor, doma) com o número à direita; depois a eficiência, como
domar, a carga, os pontos e "Come:" com os itens. Tem no mínimo 172 de largura e alarga para a linha mais longa.

### Opções novas

| Opção | Padrão | O que faz |
|---|---|---|
| `hud_nameplate` | `true` | Placa de nome sobre o bicho que você olha |
| `hud_taming` | `true` | Barras de doma no bicho desmaiado |

No modo compacto, a placa de nome e as barras de doma aparecem sem a placa de pedra.

## Parte 3 (v0.14.2): título da era, tela do dino e opções do HUD

### Título da era

Um corte nas camadas de rocha de lado a lado da tela: solo, argila e cinza por cima, uma faixa grossa de âmbar com o
nome da era entalhado (letras escuras com o lábio de baixo claro), giz e basalto embaixo, as pontas se desfazendo. Uma
amonite no giz, um osso na argila e a data embaixo ("68 milhões de anos atrás"). Mesmo tempo de antes: entra em 0,5 s,
fica 3,5 s e sai em 1 s, uma vez por jogador e mundo.

### Tela do dino

O mesmo conteúdo da v0.13 no visual Âmbar, com 372 x 196: o bicho de verdade sobre uma rocha quebrada com um veio de
âmbar; o nome em letras grandes e âmbar, ♀ ou ♂, idade, o que está fazendo, sela e carga; vida e fome em sulcos;
montado num grande terópode, "Teclas da montaria" com o encaixe do rugido forte. Na coluna da direita, "NÍVEL N", a XP
num sulco com "Próximo: x/y XP" escrito embaixo, os pontos e os status com o "+" em âmbar. As ordens embaixo.

### Opções do HUD

Botão "HUD" ao lado de "Regras do Terrassic" no menu de pausa (a tela de título fica a do Minecraft, v0.14.3). Estilo (Âmbar ou Compacto) e um
interruptor por peça: placa da montaria, placa de nome, barras de doma, avisos à direita, espécie nova, título da era
e números nas barras sempre. Cada mudança vai na hora para `config/terrassic-client.json`.

## Tamanho (v0.14.4)

O Rodrigo achou a placa da montaria e os avisos grandes demais na escala da GUI (30/10, 18:41Z) e aprovou a versão
menor (18:44Z, prévia https://claude.ai/artifact/AyVUwoTYBrB8GHFQrGXE6j). Os dois continuam com todo o conteúdo, mas são
desenhados um passo abaixo da escala da GUI: GUI 3 vira HUD 2 e GUI 4 vira HUD 3, sempre inteiro e no mínimo 1. Fica
com 2/3 do tamanho, texto incluído.

`"hud_scale": "auto"` em `config/terrassic-client.json`; um número de 1 a 4 fixa a escala, que nunca passa da escala
da GUI. Na tela de opções do HUD, o botão "Tamanho" troca entre automático, 1, 2, 3 e 4.

Os corações do modo compacto, a placa de nome, a Lupa, a tela do dino e o título da era ficam na escala da GUI.

## Fica para uma versão própria: a roda do apito

A roda do apito da prévia (segurar H: seguir, esperar, vagar por perto, atacar meu alvo, juntar o bando, ficar
passivo, com "N dinos ouvem o apito") não é só HUD: quatro dessas ordens ainda não existem no jogo. Ela entra como uma
versão própria, depois que o Rodrigo aprovar como cada ordem funciona.

## v0.14.5: F3 e Lupa

Do teste no Mac (30/10): com o F3 aberto a placa da montaria some (ela cobria as primeiras linhas). Enquanto o cartão
da Lupa está na tela, os avisos da direita esperam escondidos, sem contar o tempo, e voltam quando o cartão fecha (os
dois ficam no meio do lado direito).
