# Terrassic — piloto do T. rex, v1

Primeiro passe para revisão de Rodrigo, 27/10/2026. Não instalado no mod.

- Comece por `trex_death.gif` e `trex_antes_depois.gif` (recuperação antiga à esquerda, piloto à direita).
- Abra `tyrannosaurus.bbmodel` no Blockbench para editar rig, cubos, texturas e clips.
- `trex_diorama.png` é a imagem de apresentação, renderizada em 3D com a logo original.
- `trex_diorama.blend` contém a cena editável e texturas empacotadas.
- `validacao.json` e `manifesto.json` registram medidas e hashes. O ZIP reúne a entrega.

139→147 cubos; novo tórax articulado, volumes nos ombros/bochechas/laterais e pálpebras.
Queda em fases, recuperação passando pelo apoio esternal, repouso, sono, nocaute com respiração e cadáver imóvel.

Limites: contato ajustado offline para chão plano, sem IK de pés ou validação física; ainda pode haver
deslocamento de pés e clipping entre membros. Caminhada/corrida herdadas precisam ser revistas para o rig novo.
Não copie apenas os JSONs para o jogo: os controladores ainda não usam os novos estados.

O diorama é uma apresentação do piloto, não uma captura do Minecraft. A referência de Alex's Caves foi usada
para estudar composição, articulação e apoio; nenhum modelo, textura ou código externo foi copiado.

Estudo e próximos passos: `docs/estudos/07_TREX_PILOTO.md`. Fontes: `tools/modelgen/pilots/`.
Gerar prévias com `preview_trex.py`, diorama com `hero_trex.py` e pacote com `package_trex.py`, usando
`build/menu-render-venv/bin/python -B`. A cena usa Blender/Cycles; os assets do jogo permanecem intactos.
