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

## Próximas partes

- **v0.14.1**: placa de nome sobre o bicho que você olha (nome, nível, cor do temperamento, vida), barras de torpor e
  doma no bicho desmaiado, e o cartão da Lupa no mesmo visual.
- **v0.14.2**: roda do apito (segurar H: seguir, esperar, vagar, atacar, juntar, passivo, com "N dinos ouvem o
  apito"), título da era em camadas de rocha, tela do dino e tela de opções do HUD.
