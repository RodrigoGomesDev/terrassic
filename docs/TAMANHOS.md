# Tamanhos dos dinossauros

Regra: **1 bloco = 1 metro**. O jogador tem 1,8 bloco, então ele é uma pessoa de 1,8 m ao lado do bicho.
Tudo sai da tabela `SIZES` em `tools/javagen/gen_species.py` (rode `python3 gen_species.py` depois de mudar).
Comparação visual: `art/tamanhos/comparacao_tamanhos.png` (cor = novo, sombra cinza = antigo).

| Espécie | Real | Antes no jogo (compr. x alt.) | Agora no jogo (compr. x alt.) | Hitbox (larg. x alt.) | Filhote |
|---|---|---|---|---|---|
| Brachiosaurus | 18-22 m, cabeça a 9-13 m | 6,8 x 5,2 | **15,5 x 11,9** | 3,5 x 7,0 | 15% |
| Spinosaurus | 14 m | 7,6 x 3,1 | **14,0 x 5,7** (vela) | 2,5 x 4,6 | 25% |
| Tyrannosaurus | 12,3 m | 6,6 x 2,7 | **12,3 x 4,9** | 2,5 x 4,5 | 25% |
| Parasaurolophus | 9,5 m | 6,3 x 2,5 | **9,5 x 3,8** | 2,0 x 3,2 | 30% |
| Triceratops | 9 m | 5,5 x 2,3 | **9,0 x 3,7** | 2,4 x 3,0 | 30% |
| Stegosaurus | 9 m | 5,8 x 2,3 | **9,0 x 3,5** | 2,2 x 3,2 | 30% |
| Ankylosaurus | 6-8 m | 4,4 x 1,3 | **7,0 x 2,0** | 2,4 x 1,9 | 30% |
| Dilophosaurus | 7 m | 4,6 x 2,0 | **7,0 x 3,0** | 1,2 x 2,6 | 35% |
| Gallimimus | 6 m | 3,9 x 2,0 | **6,0 x 3,0** | 1,2 x 2,6 | 35% |
| Pachycephalosaurus | 4,5 m | 3,1 x 1,5 | **4,5 x 2,2** | 1,0 x 1,9 | 40% |
| Velociraptor | 2 m | 2,1 x 0,8 | 2,1 x 0,8 (igual) | 0,7 x 0,9 | 50% |
| Compsognathus | 1-1,25 m | 1,2 x 0,4 | 1,2 x 0,4 (igual) | 0,4 x 0,5 | 50% |

## Escolhas

- Antes quase todos estavam com uns 55-65% do tamanho real. Agora estão no tamanho real.
- O Brachiosaurus foi medido pela altura, não pelo comprimento: o nosso modelo segura o pescoço bem
  em pé, e com 22 blocos de comprimento a cabeça ficaria a 17 blocos do chão. Com 12 blocos de altura ele
  já passa por cima das árvores normais.
- A hitbox (caixa de colisão) é menor que o modelo de propósito. No Minecraft ela é quadrada, e bichos com mais
  de uns 2,5 blocos de largura ficam presos entre árvores. A cauda e o pescoço passam um pouco por dentro dos
  blocos, como acontece em outros mods de dinossauro.
- O Velociraptor continua com o tamanho real (2 m, do tamanho de um peru grande). O "raptor de filme" do
  Jurassic Park é do tamanho de um Deinonychus/Utahraptor; se você preferir, dá para colocar um desses no roster.
- Filhotes agora têm tamanho por espécie: um T. rex recém-nascido tem 3 m, e não mais metade do adulto.
- Altura da sela, culling e sombra foram recalculados automaticamente a partir da escala.

## O que testar no Mac

1. `./gradlew :fabric:runClient` compila (a nuvem não consegue baixar as dependências).
2. Montar T. rex, Triceratops, Brachiosaurus, Parasaurolophus e Gallimimus: o jogador fica sentado na sela?
3. T. rex na selva e Stegosaurus/Ankylosaurus na floresta: eles andam ou ficam presos nas árvores?
4. Gigantes andando: os pés escorregam (parece "moonwalk")? Se sim, aumento a velocidade da animação de passo.
5. Chocar um ovo: o filhote nasce pequeno e cresce para o tamanho adulto sem travar no chão?
6. O Brachiosaurus some da tela quando você olha só para a cabeça dele? (culling)
