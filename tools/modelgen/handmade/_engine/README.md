# Motor único dos modelos feitos à mão

Criado em 31/10/2026 para acelerar a refação dos modelos antigos (estudo aprovado pelo Rodrigo às 03:44Z).
Antes, cada espécie levava uma cópia do motor na própria pasta e escrevia as ~28 animações do zero.
Agora a pasta da espécie tem só os cubos, a pintura e as animações que são dela.

- `proto.py`: modelo (ossos, cubos, `pair` espelhado), UV por face (1 texel = 1 pixel), pintura, `stamp` de decalques
  e `geo_json` (já inverte o u das faces leste/oeste como o GeckoLib desenha).
- `skin.py`: escamas, placas da barriga, contornos de músculo.
- `geo.py`: lê o geo exportado como o jogo desenha e renderiza as prévias.
- `anim2.py`: animação por poses, IK das pernas, exportação GeckoLib (a versão do Velociraptor, com escala por osso).
- `qa.py`: regras checadas por código antes de qualquer prévia:
  - `separate_coplanar` (zero faces no mesmo plano, nos dois sentidos, porque o GeckoLib não corta a face de trás);
  - `single_face_planes` (plano sem espessura com uma face só);
  - `pixel_bugs`: pixel esticado (face com tamanho que não é inteiro), buraco em face sólida, ponto solto num recorte,
    cubo com menos de 1 px;
  - `clean_orphans` (apaga os pontos soltos dos recortes) e `metrics` (os números do padrão do T. rex);
  - `pinholes` (opcional, precisa de scipy): rachaduras onde o fundo aparece através do animal, para olhar à mão.
- `shots.py`: as prévias padrão (lateral, 3/4, frente, traseira, cabeça). `jsongif.py`: poses lidas do animation.json.
- `plans/theropod.py`: molde do terópode grande. As 26 animações do T. rex v2 escritas sobre um contrato de nomes de
  ossos (root, body, neck..., head, skull, jaw, arm/forearm, thigh/shin/foot/toes, tail1..N). Conferido contra o
  `tyrannosaurus/rexanims.py`: as poses saem iguais.

O T. rex, o Pteranodonte e o Velociraptor continuam com as cópias deles (não foram mexidos). Uma espécie nova
importa daqui. Cada grupo de corpo ganha o seu molde quando a primeira espécie dele for refeita e aprovada.
