# T. rex — primeiro piloto de modelo e animação

27/10/2026. Pedido do Rodrigo: melhorar primeiro o T. rex, comparar com o trabalho de criaturas de
Alex's Caves e preparar uma apresentação semelhante à imagem enviada. Evolução do estudo 06.

## Entrega

Piloto separado em `art/pilotos/trex/v1/`, com fonte em `tools/modelgen/pilots/`.
**Não substitui o T. rex instalado no mod.** A aprovação visual do piloto precede sua integração nos
controladores; as outras 58 espécies também não foram regeneradas. É uma entrega de arte/rig/curvas
editável, não uma alegação de teste no Minecraft.

Arquivos para revisar:

- `trex_death.gif`: perda de apoio, agachamento, queda lateral e acomodação.
- `trex_wake.gif`: recuperar posição de apoio e depois estender as pernas.
- `trex_antes_depois.gif`: recuperação atual à esquerda e piloto à direita, na mesma escala e câmera.
  Os dois começam juntos em tempo real; o antigo termina antes. Não foi inventado um clip antigo de morte:
  o mod não tinha esse clip autoral.
- `trex_lie_down.gif`, `trex_poses.png`: repouso e comparação de poses.
- `tyrannosaurus.bbmodel`: projeto do Blockbench, com macho/fêmea e os novos clips.
- `tyrannosaurus.geo.json`, `tyrannosaurus.animation.json`, texturas: export isolado para futura integração.
- `trex_diorama.png`: apresentação com iluminação de estúdio, modelo do piloto, blocos e logo do Terrassic.
- `trex_diorama.blend`: cena editável com texturas empacotadas.
- `validacao.json`: medidas, hashes e confirmação de recursos de produção intactos.

## O que aprendemos com Alex's Caves

Foi consultado o código oficial, não um vídeo promocional isolado. No
[TremorsaurusModel](https://github.com/AlexModGuy/AlexsCaves/blob/main/src/main/java/com/github/alexmodguy/alexscaves/client/model/TremorsaurusModel.java),
as ações coordenam várias articulações. O movimento das pernas compensa parte do deslocamento do corpo;
cauda e pescoço têm ritmos diferentes; o olhar é distribuído e há ajuste de pernas conforme o terreno.
O modelo retorna à pose base antes de compor movimentos, evitando acumulação entre quadros.

A consequência para o Terrassic é separar **massa principal, apoio e movimento secundário**. Mais cubos
não resolvem uma pata sem sustentação. Não copiamos medidas, geometria, textura, keyframes nem trechos
de implementação. O projeto consultado usa Citadel; nosso piloto continua em formato compatível com GeckoLib.

No [AtlatitanModel](https://github.com/AlexModGuy/AlexsCaves/blob/main/src/main/java/com/github/alexmodguy/alexscaves/client/model/AtlatitanModel.java),
formas adicionais e elementos rotacionados são ligados a uma estrutura comum de saurópode. A lição é usar
camadas para mudar volumes e silhueta, mantendo articulações coerentes. Isso não significa transferir
proporções do saurópode ou o visual fantástico dessas criaturas para o nosso T. rex.

A imagem enviada é referência de **composição**: criatura em destaque, base pequena, luz dirigida e fundo
escuro. O diorama produzido usa a identidade e os assets do Terrassic. Não contém a logo ou criaturas da referência.

## Mudanças de modelo

- 139 → **147 cubos**, 24 → **26 ossos**. Sem subdivisão geral nem centenas de detalhes pequenos.
- Novo osso `chest`: pescoço, braços e parte anterior do tórax articulam juntos, separados de quadril/cauda.
- Raízes das pernas ligadas ao corpo: a articulação acompanha o quadril durante a queda. Isso exige revisar
  as caminhadas herdadas antes de instalar o novo rig no jogo.
- Oito cubos adicionais: dois volumes escapulares, duas dobras laterais, dois volumes de bochecha e duas
  pálpebras no osso `eyelids`. Macho/fêmea mantêm suas cores; texturas foram repintadas no export isolado.
- O ganho procurado é volume em regiões grandes, não ruído. Mais camadas futuras devem ter papel claro:
  musculatura do pescoço, mandíbula/bochecha, articulação da coxa. Escamas pequenas ficam principalmente na textura.

## Mudanças de animação

**Queda (2,6 s):** uma perna cede antes da outra; o corpo agacha antes de tombar. O tórax acompanha com
pequena defasagem, enquanto mandíbula, pescoço e cauda acomodam depois. A rotação principal acontece
no corpo, junto ao quadril, em vez de simplesmente girar o root inteiro no chão.

**Recuperação (2,8 s):** passa primeiro da posição lateral para apoio esternal e só depois estende as pernas.
Não é a queda reproduzida ao contrário. Foram criados também `lie_down` e `stand_up` (2 s).

**Repouso:** `sit` acordado e `sleep` com pálpebras; respiração discreta por expansão do tórax.
**Cadáver:** `dead` sem respiração, distinto de `knocked_out`. A queda de nocaute compartilha neste primeiro
passe a coreografia da morte; o loop final continua respirando. Separar mais essas quedas pode ser uma próxima iteração.

As trajetórias usam smoothstep entre fases, amostradas a 20 Hz e exportadas como segmentos lineares.
Isso impede o overshoot grande de Catmull-Rom nas chaves de apoio. O avaliador do piloto respeita essa
interpolação; os clips herdados continuam usando o avaliador antigo. Não houve troca global de interpolação.

## Limites reais deste passe

O contato foi corrigido **offline contra um plano**, não com IK de patas nem física do terreno. O relatório
registra a faixa de correção do root. Essa compensação evita afundamento grosseiro, mas um único canto
no chão ainda não prova que o peso está bem apoiado. Pés podem deslocar durante as passagens; isso deve
ser corrigido com marcadores de apoio e IK offline/local na próxima iteração, antes de declarar locomoção pronta.

As caminhadas/corridas e ações herdadas não receberam um passe completo para o novo parentesco das pernas.
As pálpebras precisam ser conferidas em mais ângulos e na fêmea. Sono ainda parte da mesma postura esternal
do descanso; falta um ajuste próprio de cabeça mais acomodada. As formas laterais do torso também devem
ser aprovadas na silhueta, não só sob a luz bonita do diorama.

**Nada disso muda os controladores atuais do jogo:** eles ainda precisam selecionar `death`/`dead`, bloquear
ações durante recuperação e resolver a passagem vivo → carcaça. Não basta copiar os JSONs desta pasta para
os recursos. Integração exige o pacote de controle do estudo 06, com regressões de nocaute e loot.

## Próximo passe do T. rex

1. Validar queda, tempo e silhueta nos GIFs, sem efeitos de imagem escondendo articulações.
2. Ajustar apoios dos pés e a cabeça em repouso. Conferir clipping entre coxa, barriga e pescoço.
3. Reautorizar caminhada/partida/frenagem para o rig novo; depois ataque e rugido exclusivos da espécie.
4. Integrar somente o T. rex no jogo: queda/cadáver sem dois corpos, bloqueio durante recuperação,
   olhar limitado por estado e fallback para entidades recebidas depois do início da animação.
5. Testar Fabric/Forge, filhote/fêmea/sela, reload, servidor dedicado e observadores com latência.
6. Só então transformar a solução aprovada em ferramentas para as outras famílias, com ajustes próprios.

## Reprodução e validação

```sh
build/menu-render-venv/bin/python -B tools/modelgen/pilots/preview_trex.py
build/menu-render-venv/bin/python -B tools/modelgen/pilots/hero_trex.py
```

O segundo comando usa Blender/Cycles 5.0.1 do ambiente de render, com acesso aos recursos de render da
máquina. Não requer abrir uma conta nem enviar o modelo a um serviço externo. O diorama não é screenshot.

O gerador de prévias verifica hashes dos recursos de produção antes/depois, o piso em amostras de 40 Hz,
a igualdade entre final de `death` e começo de `dead` e a imobilidade do cadáver. O piso admite erro de
interpolação de até 0,5 pixel de autoria; não é tolerância de meio bloco. O JSON registra os valores reais.
Esses critérios não medem qualidade artística, apoio físico ou integração de runtime.

Integridade do projeto passou com 59 espécies, 4.341 JSONs e 1.848 chaves em três idiomas. Não foi necessária
build de Java: este pacote não muda fontes Java, classes geradas nem recursos instalados. Revisão visual
foi feita nas imagens renderizadas; revisão no Minecraft continua pendente.
