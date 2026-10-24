# Terrassic: escopo do produto

> **Status: aprovado pelo Rodrigo em 24/10/2026** ("pode continuar os próximos passos"). A história e as eras estão em `docs/HISTORIA.md`; as criaturas, em `docs/ROSTER.md`. O tamanho dos dinossauros é tratado à parte.

## A visão

O Terrassic é **um mod só, grande e completo, 100% autoral**. Não é modpack e não depende de mods de conteúdo de outras pessoas. No futuro ele ganha **mods complementares do próprio Rodrigo** (roupinhas para os dinos e outros extras) e pode ter um **pacote de texturas próprio**.

Regra para decidir onde cada coisa entra:
- **No mod principal:** tudo o que é preciso para jogar a história do começo ao fim e para o mundo parecer pré-histórico.
- **Num mod complementar:** extras opcionais que alguém pode querer desligar, e que não mudam a história.
- **No pacote de texturas:** mudanças na aparência do Minecraft vanilla (blocos, menus, sons do vanilla), que não precisam de código.

## Dependências: só bibliotecas, embutidas

O mod hoje usa duas **bibliotecas** (código de base, não conteúdo): **GeckoLib** (modelos e animações dos dinos) e **Architectury API** (o mesmo código rodar no Fabric e no Forge). Elas não adicionam nada ao jogo sozinhas, e trocar por código próprio significaria refazer todo o sistema de animação. Recomendação:
- **Manter as duas**, e **embutir dentro do arquivo do Terrassic** (o "jar-in-jar" que o Fabric e o Forge aceitam; as licenças das duas permitem). O jogador instala um arquivo só.
- **Não usar o Patchouli** para os livros: o Caderno de Campo é uma tela própria do mod (atualizado na `HISTORIA.md`).
- Nenhuma outra dependência. Compatibilidade com mods famosos (JEI/REI para receitas, mapas) pode vir depois, sempre opcional.

## O que fica em cada lugar

### Mod principal: Terrassic
| Área | Conteúdo |
|---|---|
| História | Tela de abertura, Caderno de Campo (Diário, Guia, Katarina, Relatório), páginas, a Katarina, os finais e os créditos |
| Eras | As 4 eras + o epílogo, com dimensões, biomas, plantas, materiais, estruturas e eventos; tipo de mundo "Terrassic" e suporte ao mundo normal |
| Criaturas | Todas as ~140 do ecossistema, com sexo, ninhos, bandos, cadeia alimentar e carcaças |
| Domesticar e montar | Domesticação (comida, ovo, nocaute), montar, **voar** (pterossauros), **nadar** (répteis marinhos), selas por espécie, sela de plataforma, carga, criaturas de ombro. É o coração do estilo ARK, então fica no principal |
| Cientista | Lente de Âmbar, Carvão de Esboço, pincel e cinzel, Frasco de Argila, Mesa de Pesquisa, fósseis |
| Sobrevivência primitiva | Armas e ferramentas de pedra, osso e sílex, blocos de construção primitivos, roupas de pele, frio e calor |
| Chefes | Tirano da Fenda, Rei do Rio, Leviatã da Fenda, Coração da Fenda |
| Visual e som | HUD próprio, tela de título, céu, névoa, partículas, sons e músicas de cada era (ver abaixo) |
| Idiomas | pt_br, en_us e es_es em tudo |

### Mods complementares (futuro, do Rodrigo)
Cada um depende do Terrassic e pode ser instalado ou não:
- **Terrassic: Guarda-Roupa:** roupinhas, chapéus, pinturas de guerra, armaduras decorativas e variantes de cor para os dinos domesticados.
- **Terrassic: Decoração:** esqueletos montados para exibir, troféus, quadros dos dinos, móveis primitivos extras.
- **Terrassic: Desafios:** modos mais difíceis (hardcore pré-histórico, dinos mais agressivos, sem HUD).
- Outros que surgirem, sempre opcionais.

Os pedidos de "subir nos dinos" e "subir no pterodáctilo e voar" ficam **no principal**, porque já estão planejados no roadmap (montaria v0.2, voo v0.3–v0.4) e sem eles o mod não fica completo. Se a ideia for **escalar** o corpo de um dino gigante (andar em cima de um Brachiosaurus em movimento), isso entra junto com a sela de plataforma (v0.6).

Para os complementares funcionarem, o principal precisa de um **jeito público de outros mods se ligarem nele** (por exemplo, "espaço de roupa" nos dinos e um registro de cosméticos). Vale pensar nisso desde já, mesmo antes de o primeiro complementar existir.

### Pacote de texturas próprio (opcional)
Recomendação: em vez de um download separado, ele vem **embutido no mod como pacote opcional** (os dois loaders permitem isso). Aparece no menu de Pacotes de Recursos já ligado, e quem não gostar desliga.
- Blocos vanilla com cara mais rústica (madeira rachada, pedra mais natural).
- Menus e botões em couro, osso e pedra.
- Fonte e cores combinando com o Caderno de Campo.
Tudo feito pelos geradores em `tools/` como o resto da arte, sem copiar texturas de terceiros.

## HUD próprio

Feito com imagens dos **nossos** dinos: retratos renderizados dos próprios modelos `.bbmodel` pelo `tools/modelgen`, então tudo continua autoral.

| Elemento | Quando aparece | O que mostra |
|---|---|---|
| **Painel de montaria** | Montado em um dino | Retrato do dino, vida, stamina (correr, voar, mergulhar), fome (v0.6) e peso da carga |
| **Barra do bando** | Com dinos seguindo o jogador | Até 6 retratos pequenos com vida e um ícone de estado (seguindo, sentado, lutando), no estilo da equipe do Cobblemon |
| **Aviso de nova espécie** | Primeira vez que avista ou estuda uma espécie | Retrato (ou a silhueta "???"), nome e o nível novo no Guia |
| **Nome da era** | Ao chegar numa era | O nome do capítulo e da era em letras grandes, com uma linha da Katarina |
| **Temperatura** | No Triássico e na Era do Gelo | Termômetro pequeno, que fica vermelho ou azul no perigo |
| **Alerta da Fenda** | Quando uma Tempestade da Fenda vai começar | Ícone de âmbar rachado pulsando; o Compsognathus no ombro também avisa de predadores |
| **Objetivos** | Ao completar um objetivo | Aviso no estilo das conquistas, com moldura de osso e âmbar |

Tudo configurável: dá para mover, diminuir ou desligar cada parte, e o F1 esconde tudo.

**Tela de título:** um panorama com dinos do mod, o logo do Terrassic e dicas de carregamento com curiosidades reais dos dinossauros (nos três idiomas).

## Ambientação

O que faz cada era parecer um lugar de verdade:
- **Céu e névoa por era:** amarelado e quente no Triássico, úmido e verde no Jurássico, cinzento no Cretáceo Inferior com cinza, céu de meteoros no fim do Cretáceo, branco na Era do Gelo.
- **Partículas:** pólen e insetos nas florestas, esporos nos samambaiais, cinza caindo, neve soprando, poeira vermelha no deserto.
- **Sons de fundo:** insetos, sapos, água, vento, e rugidos distantes de criaturas que o jogador ainda não viu. Cada espécie com os seus sons (já planejado para a v0.3).
- **Música própria por era**, tocando como a do vanilla (de vez em quando, não o tempo todo).
- **Plantas certas:** cada era com a sua flora (sem grama nem flores antes do Cretáceo), arbustos, cipós e folhagem baixa para o chão não parecer o do Minecraft.
- **Eventos de clima:** monções, nevascas, chuva de cinza, Episódio Pluvial, migrações.

## Tamanho do trabalho e ordem

É um projeto grande: ~140 criaturas, 5 dimensões, 4 chefes, HUD, música. Para ele não virar algo que nunca fica pronto, a recomendação é **fechar uma era por vez, jogável do começo ao fim**:
- **Até a v1.0, "Ecos do Fim":** o Capítulo 1 completo no Overworld (todas as criaturas do Cretáceo Superior, cientista, Caderno de Campo, HUD, ambientação, chefe e o salto). Já é um mod completo por si só.
- **v2.0 Araripe, v3.0 Jurássico, v4.0 Triássico com o final, v5.0 Era do Gelo.**
- Os sistemas de montaria do ROSTER (voo, nado, carga, nocaute) entram na era em que a primeira criatura que precisa deles aparece.

Essa ordem precisa ser refletida no `docs/ROSTER.md`, que hoje organiza as versões por sistema (céus, mares, trabalhadores). Fica para depois que esta proposta for aprovada.
