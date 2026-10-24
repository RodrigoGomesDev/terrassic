# Tamanhos dos dinossauros

Regra: **1 bloco = 1 metro**. O jogador tem 1,8 bloco, então ele é uma pessoa de 1,8 m ao lado do bicho.
Tudo sai da tabela `SIZES` em `tools/javagen/gen_species.py` (rode `python3 gen_species.py` depois de mudar).
Comparação visual: `art/tamanhos/comparacao_tamanhos.png` (cor = novo, sombra cinza = antigo).

| Espécie | Real | Antes no jogo (compr. x alt.) | Agora no jogo (compr. x alt.) | Hitbox (larg. x alt.) | Filhote |
|---|---|---|---|---|---|
| Brachiosaurus | 18-22 m, cabeça a ~13 m | 6,8 x 5,2 | **22,0 x 16,8** | 4,0 x 9,0 | 12% |
| Spinosaurus | 14 m | 7,6 x 3,1 | **14,0 x 5,7** (vela) | 2,5 x 4,6 | 25% |
| Tyrannosaurus | 12-13 m (Sue 12,3; Scotty ~13) | 6,6 x 2,7 | **13,0 x 5,2** | 2,6 x 4,8 | 25% |
| Parasaurolophus | 9,5 m | 6,3 x 2,5 | **9,5 x 3,8** | 2,0 x 3,2 | 30% |
| Triceratops | 9 m | 5,5 x 2,3 | **9,0 x 3,7** | 2,4 x 3,0 | 30% |
| Stegosaurus | 9 m | 5,8 x 2,3 | **9,0 x 3,5** | 2,2 x 3,2 | 30% |
| Ankylosaurus | 6-8 m | 4,4 x 1,3 | **8,0 x 2,3** | 2,6 x 2,1 | 30% |
| Dilophosaurus | 7 m | 4,6 x 2,0 | **7,0 x 3,0** | 1,2 x 2,6 | 35% |
| Gallimimus | 6 m | 3,9 x 2,0 | **6,0 x 3,0** | 1,2 x 2,6 | 35% |
| Pachycephalosaurus | 4,5 m | 3,1 x 1,5 | **4,5 x 2,2** | 1,0 x 1,9 | 40% |
| Velociraptor | 1,5-2,07 m, quadril ~0,5 m, 15-20 kg | 2,1 x 0,8 | 2,1 x 0,8 (igual) | 0,7 x 0,9 | 50% |
| Compsognathus | 1-1,25 m | 1,2 x 0,4 | 1,3 x 0,4 | 0,4 x 0,5 | 50% |
| Mosasaurus (v0.3) | 11-17 m (M. hoffmannii; estimativa máxima ~17 m, Grigoriev 2014) | novo | **17,0 x 3,0** | 3,0 x 2,0 | 20% |
| Maiasaura (v0.3) | 7-9 m, ~3 t | novo | **9,0 x 2,8** | 2,0 x 2,8 | 20% |
| Pteranodon (v0.3) | envergadura 5,6-7,25 m nos machos (Bennett 2001), corpo pequeno | novo | **7,25 de envergadura** x 1,9 | 1,3 x 1,7 | 30% |

## Escolhas

- **Regra para toda espécie nova (Rodrigo, 24/10/2026):** tamanho real pelo maior espécime bem documentado,
  1 bloco = 1 metro, com a fonte anotada nesta tabela.

- Antes quase todos estavam com uns 55-65% do tamanho real. Agora estão no tamanho real, usando o **topo das
  estimativas publicadas** (os maiores adultos conhecidos), por pedido do Rodrigo em 24/10/2026.
- O Brachiosaurus usa os 22 m de comprimento. O nosso modelo segura o pescoço mais em pé que as
  reconstruções (o esqueleto montado do Giraffatitan em Berlim tem 13,3 m de altura), então a cabeça fica a
  ~17 blocos. Dá para baixar o pescoço no tools/modelgen se quiser ficar exato.
- A hitbox (caixa de colisão) é menor que o modelo de propósito. No Minecraft ela é quadrada, e bichos com mais
  de uns 2,5 blocos de largura ficam presos entre árvores. A cauda e o pescoço passam um pouco por dentro dos
  blocos, como acontece em outros mods de dinossauro.
- O Velociraptor continua com o tamanho real: os fósseis da Mongólia dão 1,5-2,07 m de comprimento (quase tudo
  cauda), ~0,5 m de altura no quadril e 15-20 kg, do tamanho de um peru. O raptor de Jurassic Park foi
  baseado no Deinonychus (3,4 m). O raptor maior que um humano é o Utahraptor (5,5-7 m, quadril ~1,5 m,
  280-500 kg), que pode entrar no roster como espécie nova.
- Filhotes agora têm tamanho por espécie: um T. rex recém-nascido tem 3 m, e não mais metade do adulto.
- Altura da sela, culling e sombra foram recalculados automaticamente a partir da escala.

## O que testar no Mac

1. `./gradlew :fabric:runClient` compila (a nuvem não consegue baixar as dependências).
2. Montar T. rex, Triceratops, Brachiosaurus, Parasaurolophus e Gallimimus: o jogador fica sentado na sela?
3. T. rex na selva e Stegosaurus/Ankylosaurus na floresta: eles andam ou ficam presos nas árvores?
4. Gigantes andando: os pés escorregam (parece "moonwalk")? Se sim, aumento a velocidade da animação de passo.
5. Chocar um ovo: o filhote nasce pequeno e cresce para o tamanho adulto sem travar no chão?
6. O Brachiosaurus some da tela quando você olha só para a cabeça dele? (culling)

## Fontes das medidas

- Velociraptor: Turner, Makovicky & Norell (2007); resumo em [Live Science](https://www.livescience.com/23922-velociraptor-facts.html).
- Brachiosaurus: Taylor (2009) e [SV-POW, "How big was Brachiosaurus altithorax? I mean, really?"](https://svpow.com/2014/06/02/how-big-was-brachiosaurus-altithorax-i-mean-really/).
- T. rex: Persons et al. (2019), espécime "Scotty"; Spinosaurus: Ibrahim et al. (2020).
- Ankylosaurus: Arbour & Mallon (2017). Demais: verbetes da Wikipedia de cada espécie.
