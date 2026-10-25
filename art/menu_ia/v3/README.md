# Fundos — revisão geométrica, 25/10/2026

Propostas editadas com a ferramenta integrada image_gen. Originais v2 preservados.
Nenhum fundo ativo do jogo foi substituído. Prompts integrais em `PROMPTS.md`; arquivos,
dimensões e hashes em `manifest.json`.

## Auditoria visual

Rodrigo identificou degraus de grama achatados na floresta v2. A revisão anterior conferiu
composição e iluminação, mas não identificou corretamente esses problemas estruturais.
Também foram observadas margens com alturas inconsistentes e falésias com fragmentos
estreitos, incompatíveis com uma grade uniforme de blocos.

| Imagem | Resultado observado na revisão |
|---|---|
| `floresta_confronto.png` | Removido o pequeno degrau achatado ao lado da face de terra; primeiro plano reconstruído com faces maiores e cantos mais claros. Confronto, enquadramento e luz mantidos visualmente. |
| `rio_espinossauro.png` | Margens e leito com volumes mais definidos; preservados água, reflexos e posição do animal. |
| `falesias_pteranodonte.png` | Reduzidos os fragmentos estreitos das paredes; estratos e degraus mais regulares. Preservados voo, costa e iluminação. |

## Limites e pendências

As três saídas foram inspecionadas visualmente e comparadas à v2. São melhorias de imagens
raster, não renders de uma malha de blocos verificada. A escala das texturas ainda varia;
alinhamento tridimensional de todos os blocos e fidelidade exata dos animais aos modelos
originais não estão certificados. Não anunciar como capturas do jogo ou como assets finais
validados. Para garantia estrutural, reconstruir os cenários em uma grade real e renderizar
os modelos do projeto, usando estas imagens como referência de composição e iluminação.

Pendente: revisão do Rodrigo em tamanho integral e escolha antes de aplicação ao menu.
Não houve build nem teste no jogo: esta entrega modifica apenas propostas de arte e documentação.
