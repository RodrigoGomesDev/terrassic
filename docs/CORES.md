# Cores das espécies

Regra universal (Rodrigo, 02/11/2026): **cada espécie tem modelo e cor só dela.** Nenhuma espécie divide corpo ou
paleta com outra, nem com um parente próximo.

Como medir: `python3 -B tools/modelgen/handmade/_engine/colourcheck.py <espécie>` compara a pele do macho com todas as
outras do mod (média CIELAB das partes escura, média e clara). Abaixo de 10 as duas parecem a mesma cor no jogo.
Contra uma espécie já refeita à mão isso é erro (a cor dela está tomada); contra uma antiga é aviso, e a antiga ganha
uma cor livre quando for refeita.

## Cores tomadas (espécies refeitas à mão)

| Espécie | Cor | Família |
|---|---|---|
| Tyrannosaurus | verde-musgo escuro, faixas ferrugem diagonais | verde |
| Spinosaurus | oliva-acinzentado escuro | oliva |
| Velociraptor | marrom-café com marcas azul-petróleo | marrom escuro |
| Pteranodon | marrom escuro (colide com o Velociraptor: 8,6) | marrom escuro |
| Carnotaurus | vermelho-tijolo escuro, chifres pretos | vermelho |
| Giganotosaurus | cinza-ardósia azulado | azul-cinza |
| Protoceratops | areia quente com selas ferrugem | areia |
| Triceratops | ameixa: cinza-arroxeado, babado com faixa terracota no macho | roxo-acinzentado |
| Gallimimus | grafite-azulado (macho) ou canela (fêmea), barriga e garganta giz, canelas rosadas | azul-preto |
| Pachycephalosaurus | mel listrado (macho), mel escuro (fêmea), listras creme inclinadas, coroa clara na cúpula do macho | mel/ocre |
| Parasaurolophus | ruivo de impala (macho) ou pardo-rosado (fêmea), barriga creme, bandeira preta de alarme na cauda, crista escurecendo até a ponta no macho | ruivo/laranja |
| Ankylosaurus | jade escuro: pele cinza-azulada (petróleo acinzentado) sob placas de chifre escuro, quilhas claras, barriga cinza-esverdeada clara; fêmea com a pele um pouco mais cinza e o chifre mais quente | cinza-petróleo |
| Mosasaurus | verde-garrafa: dorso verde-garrafa fundo sobre barriga marfim, contrassombreado com linha nítida e ondulada; o macho com cicatrizes de mordida na cabeça, a fêmea lisa e um pouco mais cinza; olho dourado | verde-garrafa |

## Colisões que ainda existem (02/11/2026)

- Pteranodon × Velociraptor: 8,6, as duas já refeitas. Uma das duas muda de cor.
- Giganotosaurus × Dreadnoughtus 4,9, Pachyrhinosaurus 6,2, Brachiosaurus 7,1: as antigas mudam (o Mosasaurus saiu, refeito em verde-garrafa).
- Protoceratops × Mononykus 6,9, Compsognathus 8,1, Styracosaurus 8,3: as antigas mudam.
- Carnotaurus × Majungasaurus 9,2: o Majungasaurus muda.
- Triceratops: a mais perto é o Pachyrhinosaurus (antigo, 13,4); o Mosasaurus, do mesmo pacote 1.5, não pode usar ameixa.
- Gallimimus × Hesperornis 6,4, Citipati 7,5, Tylosaurus 7,5: as antigas mudam. O Mosasaurus saiu do azul-escuro
  (refeito em verde-garrafa). Nenhuma colisão com refeitos (Giganotosaurus e Pteranodon
  ficaram acima de 10 depois de o macho ir para o grafite-azulado).
- Pachycephalosaurus: a mais perto é o Compsognathus (antigo, 12,9); nenhuma abaixo de 10. O castanho foi testado e
  descartado (5,9 do Carnotaurus), e a fêmea sépia ficava a 7,8 do Protoceratops. O Parasaurolophus, próximo do pacote
  1.5, não pode usar mel nem ocre.
- Parasaurolophus: o macho ruivo fica a 14,6 do Pachycephalosaurus e a 14,7 do Carnotaurus (machos); contra a fêmea
  mel-escuro do Pachycephalosaurus, 12,3. O primeiro ruivo, mais escuro, ficava a 7,6 do Carnotaurus, e o segundo a
  7,7 da fêmea do Pachycephalosaurus: os dois foram descartados. A fêmea pardo-rosada fica a 10,3 do Carnotaurus e
  acima de 10 de todos os refeitos (a cinza-parda ficava a 9,6 da fêmea do Spinosaurus e 9,9 da do Pteranodon). Das
  antigas, a mais perto é o Majungasaurus (9,3, aviso; ele já muda por causa do Carnotaurus).
- Ankylosaurus: macho e fêmea medidos contra machos e fêmeas de todos. O refeito mais perto é o Spinosaurus (macho:
  11,1 do nosso macho, 10,9 da nossa fêmea); das antigas, o Hatzegopteryx (10,3 a 10,7, sem colisão). Testados e
  descartados: "líquen" (cinza-esverdeado sob chifre sálvia, 9,4 da fêmea do Spinosaurus), "musgo claro" (7,6 do
  Euoplocephalus antigo) e o mesmo jade com placas cor de marfim (lia como as placas claras do modelo antigo). O
  contrassombreamento (dorso escuro, barriga clara) vem do nodossauro Borealopelta (Brown et al. 2017); o ruivo dele
  já está tomado pelo Parasaurolophus, então a pele ficou no cinza-petróleo. O Mosasaurus, último do pacote 1.5, não
  pode usar cinza-petróleo nem azul-escuro.
- Mosasaurus: macho e fêmea medidos contra machos e fêmeas de todos (colourcheck.check com against=("male","female")).
  Nenhum abaixo de 10: o mais perto é o Deinosuchus antigo (10,7 do macho, 10,4 da fêmea); dos refeitos, o
  Velociraptor fica a 12,0 da fêmea. O primeiro tom, "breu" (preto-sépia sobre marfim), foi descartado: 3,4 do
  Velociraptor e 4,4 do Pteranodon. Sobrava pouco escuro livre (azul-escuro do Galimimo, cinza-petróleo do
  Anquilossauro, ameixa do Tricerátops); o verde-garrafa saiu de uma busca em Lab pelo ponto mais longe de todos. O
  pigmento escuro no dorso e a barriga clara vêm da pele fóssil de mosassauro com eumelanina (Lindgren et al. 2014).
- O colourcheck compara só os machos. No Parasaurolophus as duas cores foram medidas também contra as fêmeas dos
  refeitos; vale fazer o mesmo nos próximos (a fêmea do Pachycephalosaurus quase pegou o macho ruivo).
- Uns 45 dos 59 bichos do mod estão na faixa marrom, bege e oliva. Cada um que for refeito escolhe uma cor livre
  nesta tabela antes de pintar.
