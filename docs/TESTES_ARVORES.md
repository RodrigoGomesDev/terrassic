# Copas das árvores — 26/10/2026

Rodrigo identificou pontas de tronco vertical visíveis acima da copa das magnólias.
A configuração combinava `fancy_trunk_placer` (galhos que sobem) com `blob_foliage_placer`
de offset 0. A copa ficava abaixo das pontas. O offset foi alterado para **2**, preservando
raio 3, altura 3, formato arredondado, flores, tronco e demais parâmetros da árvore.

Fonte: `tools/javagen/gen_blocks.py`, entrada `WOODS["magnolia"]`.
Recurso: `data/terrassic/worldgen/configured_feature/magnolia.json`.
Não foi executado o gerador de blocos em massa. A feature é compartilhada pela geração natural
e pelo crescimento da muda (`PrehistoricTreeGrower`).

## Reprodução e comparação

O harness usa `/place feature` no Minecraft real, em parcelas separadas de um mundo descartável.
Depois de salvar e encerrar o servidor, decodifica as paletas/estados dos blocos dos arquivos MCA.
Uma ponta vertical é considerada exposta se o tronco termina e não há folhas da própria árvore
na coluna acima dele. Troncos laterais e cascas aparentes sob a copa não são classificados como erro.

Comparação Fabric em `build/tree-regression/fabric-axilsg0o/`:

| Magnólia | Árvores afetadas | Pontas expostas |
|---|---:|---:|
| Original, offset 0 | 5/5 | 5 |
| Blob, offset 1 | 3/5 | 3 |
| Blob, offset 2 | 0/5 | 0 |
| Fancy foliage, offset 4 | 0/5 | 0 |

A correção escolhida foi a menor elevação que passou nas amostras, mantendo a copa original.
As oito outras famílias tiveram cinco árvores cada na comparação, sem o mesmo defeito:
araucária, ginkgo, metassequoia, taxódio, samambaia-arbórea, sabal, podocarpo e plátano.

## Regressão da configuração entregue

- Fabric: 72 árvores (8 de cada família), `build/tree-regression/fabric-x1gzqwft/`.
  Nenhuma ponta vertical descoberta nas nove famílias. A análise dos estados de folhas também confirmou
  cobertura por folhas com `distance < 7`, que não dependem de folhagem sem suporte para ocultar o tronco.
- Forge: 72 árvores (8 de cada família), `build/tree-regression/forge-d20qkau0/`.
  Nenhuma ponta vertical descoberta nas nove famílias.
- Hashes das nove configurações testadas conferidos contra a entrega; definição no gerador confere
  com os JSONs nas nove famílias. Recurso de magnólia comparado byte a byte aos JARs finais dos dois loaders.
- Build Fabric/Forge com regressões de movimento e dados passou em 51 s.
- Integridade: 59 espécies, 4.341 JSONs, 1.848 chaves; orçamento de spawn passou.

```sh
python3 -B tools/validation/tree_regression.py --loader fabric --eula-file /caminho/eula.txt --compare
python3 -B tools/validation/tree_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/tree_regression.py --loader forge --eula-file /caminho/eula.txt
```

## Limites

A configuração corrige árvores novas e cultivadas, sem reescrever árvores/construções já salvas.
Não houve edição de mundo do Rodrigo. As amostras são árvores isoladas em terreno plano: não validam
todos os seeds, sobreposição de copas em floresta densa, interação com construções ou remoção de folhas
por animais/jogadores. A revisão visual dessas situações continua separada da auditoria estrutural.
