# Menu principal Terrassic

> **Desligado desde a v0.14.3 (30/10/2026):** por enquanto o mod não muda o menu do Minecraft. A tela de título, o
> panorama, o logo e as telas de carregamento do Terrassic estão desligados no código (`ClientConfig.titleScreen()`),
> e o botão "Regras do Terrassic" saiu da tela de título (continua no menu de pausa). Nada foi apagado.

> Aprovado pelo Rodrigo em 24/10/2026 ("pra mim está perfeito esse modelo para o menu"). A tipografia (letreiro e
> slogan) ainda vai mudar depois do estudo de tipografia da capa. Cores, texto em caixa normal, divisor e ícones seguem a
> identidade "Âmbar e Basalto" (`docs/IDENTIDADE.md`, `client/ui/TerrassicPalette` e `TerrassicUi`).

## O que é

O menu principal do Minecraft é trocado por uma tela própria (`client/title/TerrassicMenuScreen.java`), igual no
Fabric e no Forge:

- **Fundo:** três ilustrações aprovadas pelo Rodrigo em 25/10/2026 (`art/menu_ia/v3/`):
  confronto T. rex × Triceratops, Espinossauro no rio e Pteranodonte nas falésias. PNGs originais
  de 1672×941 copiados sem alteração; são ilustrações por IA, não capturas ou renders exatos dos modelos.
  Uma cena é sorteada por inicialização do jogo, com movimento lateral lento. O jogo aplica um
  sombreado à esquerda e no rodapé para preservar a leitura sem modificar os arquivos aprovados.
- **No alto, à esquerda:** o letreiro de pedra **TERRASSIC** da capa, um traço âmbar e o slogan **"The past has awoken."**
  (em inglês em todos os idiomas, como na capa).
- **Opções**, alinhadas ao letreiro, cada uma com um ícone próprio de 16×16 no mesmo estilo:
  pegada de terópode (Um jogador), duas pegadas (Multijogador), controles com o fragmento de âmbar (Regras do
  Terrassic), amonite (Mods), martelo de geólogo (Opções) e arco de pedra (Sair do jogo, depois do divisor da
  TerrassicUi). Ícones em pedra com contorno de basalto; a opção destacada (mouse ou teclado) acende em âmbar, com uma
  faixa e uma dica curta embaixo ("Seus mundos, ou um novo salto"...). Em telas baixas (escala de interface 3 ou 4)
  as opções ficam um pouco mais juntas.
- **Regras do Terrassic** abre a tela de Regras com os padrões dos mundos novos (o mesmo botão que o `ClientHooks`
  põe na tela de título do Minecraft, que este menu substitui).
- **No alto, à direita:** ícones de Idioma e Acessibilidade, com dica ao passar o mouse.
- **Embaixo, à direita:** a plaquinha de museu do animal da cena (nome científico, idade, tamanho e onde viveu).
- **Rodapé:** versão do Terrassic à esquerda; o copyright da Mojang à direita abre os créditos, como no vanilla.
- Entra com um fade na primeira vez que o jogo abre.
- **Mods** abre a lista de mods do Forge, ou a do Mod Menu no Fabric quando ele está instalado (sem ele, a opção some).
- **Realms** não aparece (o Realms não roda mods). Sem a frase amarela (splash).
- `"title_screen": false` em `config/terrassic-client.json` volta ao menu do Minecraft.

## Telas de carregamento

Criar ou abrir um mundo e "Carregando terreno..." (entrar num servidor, trocar de dimensão) mostram uma cena da
galeria no lugar da terra do Minecraft, parada e escurecida com basalto para o mapa de chunks e a porcentagem do
vanilla ficarem legíveis (`TerrassicMenuScreen.renderBackdrop`, chamado por `LevelLoadingScreenMixin` e
`ReceivingLevelScreenMixin`). A cena é sorteada de novo a cada volta ao menu. A dica "Você sabia?" fica numa laje de
basalto da identidade (`TerrassicTitle.renderTip` com `TerrassicUi.slab`). Com `"title_screen": false` volta a terra
do vanilla; `"loading_tips": false` tira só a dica.

## Guia de Campo: dioramas de habitat

Aprovado pelo Rodrigo em 25/10/2026. Na página de cada espécie do Guia de Campo, atrás do modelo 3D vivo, fica um
diorama do habitat dela: uma cena de blocos sem animal, renderizada no Blender e impressa como gravura em tinta sobre
o papel do Caderno, com as bordas sumindo no papel, bem clara para o modelo colorido ler primeiro.

- Seis habitats (`textures/gui/notebook/habitat_<nome>.png`, 744×288, quatro vezes a caixa da figura): **floresta**
  (metassequoias na neblina), **planície** (samambaias e araucárias), **rio** (margens com palmeiras), **seco**
  (areia e laterita com cicadáceas), **litoral** (falésias de giz) e **mar** (mar aberto).
- `client/GuideHabitats.java` diz o habitat de cada espécie (sem entrada, a espécie fica na planície);
  `NotebookScreen` desenha o diorama antes do modelo.
- Gerador: `tools/menugen/habitats.py` (`BACKEND=cycles SAMPLES=64 python3 -B habitats.py ../capagen <saída>`), que
  usa as cenas e as luzes de `menu_cenas.py` e aplica a gravura com as cores `INK`, `INK_SOFT` e `PAPER` da paleta.

## Arquivos

- Tela: `common/src/main/java/com/terrassic/client/title/TerrassicMenuScreen.java` (registrada em `TerrassicClient`).
- Texturas: `assets/terrassic/textures/gui/title/menu/` (`fundo_confronto.png`, `fundo_espinossauro.png`, `fundo_pteranodonte.png` 1672×941, `titulo.png`, `icones.png` com
  uma coluna por ícone e as linhas normal/destacado/apagado).
- Geradores (`tools/menugen/`): `menu_cenas.py` monta e renderiza as cenas com o `tools/capagen` (gl.py para prévia
  rápida, `BACKEND=cycles` para a imagem final), `icones.py` desenha os ícones, `menu_assets.py` grava as texturas.
- Textos: `tools/javagen/menu_texts.py` (`menu.terrassic.slogan`, `menu.terrassic.<opção>.hint`,
  `menu.terrassic.scene.<cena>.*`), em pt_br, en_us e es_es.

Para reinstalar os fundos aprovados, sem regenerar marca ou ícones:

```sh
build/menu-render-venv/bin/python -B tools/menugen/menu_assets.py --approved
```

A fonte canônica é `art/menu_ia/v3/`. O instalador verifica o tamanho e copia os três PNGs
sem alterar seus bytes. Os geradores Blender antigos permanecem como histórico; sua saída
não deve sobrescrever automaticamente as escolhas aprovadas. Para adicionar cenas, manter
`APPROVED`, `TerrassicMenuScreen.SCENES`, dimensões e textos de plaquinha em concordância.

Validação de 25/10: integridade e orçamento passaram; build Fabric/Forge passou em 36 s.
Revisão da tela dentro do jogo, em diferentes resoluções e escalas, permanece pendente.

## Testes no jogo (para o Rodrigo)

- [ ] Fabric e Forge abrem direto no menu novo, com o fade, a cena e o letreiro.
- [ ] Passar o mouse e usar Tab/setas: a opção acende em âmbar com a dica; Enter abre.
- [ ] Um jogador, Multijogador (com o aviso de segurança na primeira vez), Regras do Terrassic (volta para o menu ao
      fechar), Opções e Sair funcionam.
- [ ] Forge: Mods abre a lista de mods. Fabric com Mod Menu: abre a lista; sem Mod Menu, a opção não aparece.
- [ ] Idioma: trocar para English e Español muda as opções, as dicas e a plaquinha (o slogan fica em inglês).
- [ ] Acessibilidade abre; o copyright abre os créditos.
- [ ] Sair de um mundo volta para este menu (não para o do Minecraft).
- [ ] Janela pequena (854×480), escala de interface 3 e 4, e tela cheia em 1080p e 1440p: nada se sobrepõe (opções
      abaixo do slogan, acima do rodapé), a cena cobre a tela toda.
- [ ] `"title_screen": false` em `config/terrassic-client.json` traz o menu do Minecraft de volta.
- [ ] Criar um mundo novo e abrir um existente: a cena aparece atrás do mapa de chunks, a porcentagem lê bem e a dica
      fica na laje de basalto, sem cortar o texto em janela pequena.
- [ ] Entrar num servidor e passar por um portal do Nether: "Carregando terreno..." também mostra a cena.
- [ ] Guia de Campo: espécies de floresta, planície, rio, seco, litoral e mar mostram o diorama certo atrás do modelo;
      o modelo continua girando com o mouse e o texto embaixo não muda de lugar; nada aparece para espécie desconhecida.
