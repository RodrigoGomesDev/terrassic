# Baixar e aplicar os sons gravados (roda no Mac)

A rede da nuvem bloqueia os sites de som, então o download roda no Mac. Tudo é automático: um script baixa, confere a licença e o gerador corta, muda o tom e mistura as gravações. Aprovado pelo Rodrigo (24/10/2026): "pode baixar sim, pode commitar".

Fontes: só **domínio público** (gravações do National Park Service e do US Fish and Wildlife Service) e **CC0** (OpenGameArt). Nenhuma pede login. A lista completa, com links e licenças, está em `tools/soundgen/sources.py` e vira `docs/LICENSES-SOUNDS.md`.

## Passos (na raiz do repositório)

1. Pré-requisitos (uma vez):
   ```bash
   command -v ffmpeg || brew install ffmpeg          # precisa do encoder libvorbis (o do brew tem)
   python3 -c "import numpy" || python3 -m pip install --user numpy
   ```
2. Baixar as fontes para `art/sounds/src/<id>/` (pula o que já existe; Wikimedia é conferida na API e pulada se não for PD/CC0):
   ```bash
   python3 tools/soundgen/fetch.py
   ```
   A saída lista cada fonte como `downloaded`, `ok`, `SKIPPED` ou `FAILED`, e o tamanho total. Um link morto não para o resto.
3. Gerar os sons (as receitas trocam o som sintético pela gravação onde ela existir):
   ```bash
   python3 tools/soundgen/build.py
   ```
   A última linha diz quantos arquivos vieram de gravações (o esperado com tudo baixado é `20 from recordings` de 22; os 2 passos do T. rex continuam sintéticos).
4. Conferir: `./gradlew build` e `./gradlew :fabric:runClient`; num mundo, chegar perto de um Tiranossauro, um Parassaurolofo e um Pteranodonte (ovo gerador) e ouvir.
5. Commit (nome do Rodrigo), só estes caminhos:
   ```bash
   git add art/sounds/src docs/LICENSES-SOUNDS.md common/src/main/resources/assets/terrassic/sounds
   git commit -m "Sons gravados: fontes em domínio público e CC0 no piloto" -m "Baixadas por tools/soundgen/fetch.py (National Park Service, US Fish and Wildlife Service, OpenGameArt CC0) e aplicadas pelas receitas do piloto: Tiranossauro, Parassaurolofo e Pteranodonte. Licenças em docs/LICENSES-SOUNDS.md."
   git push origin main
   ```
6. Mandar de volta para a nuvem a saída do passo 2 e do passo 3. Se houver como, mandar também a pasta `art/sounds/src/` (ou um .tar.gz dela): sem ela a nuvem não consegue ajustar as receitas nem criar conjuntos de voz novos com gravações.

## Se algo falhar
- `FAILED` em uma fonte: siga com as outras; o som dela fica no sintético. Me mande a linha.
- `SKIPPED` (licença): correto, a fonte não entra.
- Erro do ffmpeg sobre `libvorbis`: `brew reinstall ffmpeg`.
