# Menu principal Terrassic

> Aprovado pelo Rodrigo em 24/10/2026 ("pra mim está perfeito esse modelo para o menu"). A tipografia (letreiro e
> slogan) ainda vai mudar depois do estudo de tipografia da capa. Cores, texto em caixa normal, divisor e ícones seguem a
> identidade "Âmbar e Basalto" (`docs/IDENTIDADE.md`, `client/ui/TerrassicPalette` e `TerrassicUi`).

## O que é

O menu principal do Minecraft é trocado por uma tela própria (`client/title/TerrassicMenuScreen.java`), igual no
Fabric e no Forge:

- **Fundo:** uma cena do Cretáceo Superior feita com os blocos e os modelos do próprio mod e renderizada no Blender
  (Cycles), com sombras, luz rebatendo e névoa de verdade. A primeira é **"Névoa"**: o T. rex saindo da neblina da manhã
  entre metassequoias gigantes. A cena preenche a tela e desliza devagar para os lados (2 minutos ida e volta). O lado
  esquerdo e a parte de baixo já vêm escurecidos na imagem, para o texto ficar legível.
- **No alto, à esquerda:** o letreiro de pedra **TERRASSIC** da capa, um traço âmbar e o slogan **"O passado acordou."**
  (traduzido).
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

## Arquivos

- Tela: `common/src/main/java/com/terrassic/client/title/TerrassicMenuScreen.java` (registrada em `TerrassicClient`).
- Texturas: `assets/terrassic/textures/gui/title/menu/` (`fundo_nevoa.png` 1920×1080, `titulo.png`, `icones.png` com
  uma coluna por ícone e as linhas normal/destacado/apagado).
- Geradores (`tools/menugen/`): `menu_cenas.py` monta e renderiza as cenas com o `tools/capagen` (gl.py para prévia
  rápida, `BACKEND=cycles` para a imagem final), `icones.py` desenha os ícones, `menu_assets.py` grava as texturas.
- Textos: `tools/javagen/menu_texts.py` (`menu.terrassic.slogan`, `menu.terrassic.<opção>.hint`,
  `menu.terrassic.scene.<cena>.*`), em pt_br, en_us e es_es.

Para pôr outra cena: uma função nova em `menu_cenas.py`, o id em `SCENES` de `menu_assets.py` e de
`TerrassicMenuScreen`, e as três linhas da plaquinha em `menu_texts.py`. O jogo sorteia uma cena por abertura.

## Testes no jogo (para o Rodrigo)

- [ ] Fabric e Forge abrem direto no menu novo, com o fade, a cena e o letreiro.
- [ ] Passar o mouse e usar Tab/setas: a opção acende em âmbar com a dica; Enter abre.
- [ ] Um jogador, Multijogador (com o aviso de segurança na primeira vez), Regras do Terrassic (volta para o menu ao
      fechar), Opções e Sair funcionam.
- [ ] Forge: Mods abre a lista de mods. Fabric com Mod Menu: abre a lista; sem Mod Menu, a opção não aparece.
- [ ] Idioma: trocar para English e Español muda as opções, as dicas, o slogan e a plaquinha.
- [ ] Acessibilidade abre; o copyright abre os créditos.
- [ ] Sair de um mundo volta para este menu (não para o do Minecraft).
- [ ] Janela pequena (854×480), escala de interface 3 e 4, e tela cheia em 1080p e 1440p: nada se sobrepõe (opções
      abaixo do slogan, acima do rodapé), a cena cobre a tela toda.
- [ ] `"title_screen": false` em `config/terrassic-client.json` traz o menu do Minecraft de volta.
