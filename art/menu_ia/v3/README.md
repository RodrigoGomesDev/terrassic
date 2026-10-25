# Fundos — revisão geométrica, 25/10/2026

Propostas editadas com a ferramenta integrada image_gen. Originais v2 preservados.
Rodrigo aprovou a aplicação ao menu em 25/10/2026; os três PNGs agora são os fundos ativos. Prompts integrais em `PROMPTS.md`; arquivos,
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

Aprovação visual recebida; integração ao menu compilada nos dois loaders. A reprovação posterior das
imagens dos períodos não inclui estes três fundos (Rodrigo confirmou explicitamente).
Teste visual da interface dentro do jogo permanece pendente.
