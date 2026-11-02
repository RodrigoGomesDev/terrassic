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

## Colisões que ainda existem (02/11/2026)

- Pteranodon × Velociraptor: 8,6, as duas já refeitas. Uma das duas muda de cor.
- Giganotosaurus × Dreadnoughtus 4,9, Pachyrhinosaurus 6,2, Brachiosaurus 7,1, Mosasaurus 7,5: as antigas mudam.
- Protoceratops × Mononykus 6,9, Compsognathus 8,1, Styracosaurus 8,3: as antigas mudam.
- Carnotaurus × Majungasaurus 9,2: o Majungasaurus muda.
- Triceratops: a mais perto é o Pachyrhinosaurus (antigo, 13,4); o Mosasaurus, do mesmo pacote 1.5, não pode usar ameixa.
- Gallimimus × Hesperornis 6,4, Citipati 7,5, Tylosaurus 7,5, Mosasaurus 8,0: as antigas mudam. O Mosasaurus, último
  do pacote 1.5, sai do azul-escuro quando for refeito. Nenhuma colisão com refeitos (Giganotosaurus e Pteranodon
  ficaram acima de 10 depois de o macho ir para o grafite-azulado).
- Pachycephalosaurus: a mais perto é o Compsognathus (antigo, 12,9); nenhuma abaixo de 10. O castanho foi testado e
  descartado (5,9 do Carnotaurus), e a fêmea sépia ficava a 7,8 do Protoceratops. O Parasaurolophus, próximo do pacote
  1.5, não pode usar mel nem ocre.
- Uns 45 dos 59 bichos do mod estão na faixa marrom, bege e oliva. Cada um que for refeito escolhe uma cor livre
  nesta tabela antes de pintar.
