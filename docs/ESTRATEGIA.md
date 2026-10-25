# Terrassic: plano mestre

> 24/10/2026. Pedido do Rodrigo: o Terrassic tem de ser **superior a qualquer mod de dinossauro que já existiu**, uma
> **marca** (site, Discord, redes), jogável por **muitos jogadores** e integrável em modpacks. Antes de construir mais,
> estudar. Este documento junta os cinco estudos (`docs/estudos/`) em decisões e num plano. Serve ao Rodrigo e a toda
> sessão do Claude que pegar o projeto: **leia antes de começar uma fase nova**.
>
> | Estudo | Arquivo |
> |---|---|
> | 01 Mercado e concorrência | `docs/estudos/01_MERCADO.md` |
> | 02 Modelos 3D, animação e pipeline | `docs/estudos/02_3D_ANIMACAO.md` |
> | 03 Multiplayer grande e modpacks (com auditoria do código) | `docs/estudos/03_MULTIPLAYER_INTEGRACAO.md` |
> | 04 Versões do Minecraft, loaders e Bedrock | `docs/estudos/04_VERSOES_PLATAFORMAS.md` |
> | 05 Marca, comunidade e limites legais | `docs/estudos/05_MARCA_COMUNIDADE.md` |
> | Identidade visual (paleta e componentes) | `docs/IDENTIDADE.md` |
>
> Os números dos estudos foram lidos em 24/10/2026 nas APIs do Modrinth, CurseForge, GitHub e nas fontes oficiais; a
> busca geral na web e o Reddit estavam bloqueados naquele ambiente, então a "voz do jogador" veio de issues e addons.
> Vale uma rodada manual no Reddit e no YouTube antes de fechar o posicionamento público.

---

## 1. Onde estamos no mercado

1. **Não existe hoje um mod de dinossauro de referência ativo.** O maior da história, JurassiCraft (8,1M de downloads),
   parou em 2021 no 1.12.2; o sucessor morreu antes de lançar.
2. **O concorrente direto é o Fossils and Archeology: Revival** (9,8M CF + 590k Modrinth, 60+ espécies), com **a mesma
   stack do Terrassic** (Architectury + GeckoLib, Fabric e Forge, 1.20.1), um programador só e bugs graves (dinos que
   perdem a domesticação ao recarregar, bichos pequenos demais). Os outros: Jurassic Reborn (usa a marca do filme),
   Unusual Prehistory 2 (remake só NeoForge 1.21.1), Jurassic Saga e Jurassic Revived (novos, pequenos).
3. **O teto do tema é dez vezes maior que o nicho atual.** Alex's Mobs 159M, Mowzie's 115M, Ice and Fire 109M,
   Cobblemon ~66M, contra menos de 10M do melhor mod de dinossauro. Há demanda que ninguém atendeu.
4. **Os jogadores consertam sozinhos o que falta**, e os addons mostram o quê: spawn natural (621k), domesticação,
   escala real ("os dinos do F&A são pequenos demais?") e desempenho (Ice and Fire Patcher, 7,3M). Também montam
   modpacks inteiros para ter a experiência completa (Prehistoric World, 1M, pedindo 7 GB de RAM).
5. **Os mods morrem pelos mesmos motivos:** escopo maior que a equipe, reescritas, autor único, presos a uma versão,
   licença fechada que impede a comunidade de continuar.

**Conclusão:** a vaga de "o mod de dinossauro" está aberta, e os pilares do Terrassic já miram exatamente as lacunas.
O risco não é falta de ideia; é **executar com qualidade, desempenho e continuidade**, que é onde todos falharam.

## 2. O norte: o que "superior a qualquer mod de dinossauro" quer dizer, medido

| Eixo | Meta | Como se mede |
|---|---|---|
| Qualidade de criatura | Toda espécie lançada passa o **checklist de modelo** (estudo 02 §7): tamanho real com fonte, densidade de texel na faixa, pé sem escorregar, olhar no pescoço, cauda com inércia, conjunto completo de animações | CI do `tools/modelgen` + revisão |
| Mundo vivo | Nenhum addon de "spawn natural" ou "domesticação" é necessário; manadas, caça, ninhos e migração visíveis em 10 minutos de jogo | roteiros de teste `TESTES_Vxx.md` |
| Desempenho | **100 jogadores por servidor** (backend) com MSPT médio < 35 ms; 150 animais na tela sem travar com Sodium + shaders (≤ 400 mil vértices de entidade por frame) | perfil do **spark** anexado a cada versão, mundo de teste com bots |
| Integração | Modpack não precisa de código para ajustar: dietas por tag, espécies e spawns por datapack, Jade e EMI/JEI, licença que permite modpack | lista de integração (estudo 03 §6) |
| Narrativa e ciência | Campanha por eras no nível do Twilight Forest e Guia de Campo no nível da Pokédex/Ponder | conquistas e Caderno completos por era |
| Continuidade | Mais de uma pessoa com acesso a tudo; licença que deixa a comunidade portar se o projeto parar | README, licença, GitHub da organização |
| Marca | Identidade própria completa (paleta, fontes, logo); no fim do roadmap, domínios, redes, Discord, site com bestiário gerado dos dados e trailer em cada versão grande | §5 |

## 3. Os pilares de diferenciação e onde o Terrassic está

| Lacuna do mercado (estudo 01 §5) | No Terrassic hoje | Falta |
|---|---|---|
| Escala real (1 bloco = 1 m) | ✅ regra fixa, 53 modelos | hitbox multiparte acima de 8 m, navegação de gigantes, densidade de texel unificada |
| Domesticação estilo ARK | 🔄 comida, ovo, montaria, carga, plataforma | nocaute completo (v0.7), persistência à prova de recarga |
| Ecossistema vivo | ✅ manadas, caça, carcaças, fome, sono, ninhos, migração, spawner próprio | orçamento por jogador, LOD de IA |
| Campanha por eras com chefes | ✅ Capítulo 1 com Altar, ritual e Tirano (v0.9, frente paralela) | dimensões das eras seguintes (v2.0+) |
| Guia de Campo científico | ✅ Caderno, níveis do Guia, fósseis | fichas por espécie no nível Pokédex, escala comparada |
| Tipo de mundo próprio | ✅ 11 biomas do Cretáceo | mundo-ilha (thread de mundo) |
| Desempenho em servidor | ○ | §6 item 3 (o maior risco técnico hoje) |
| API e datapacks | ○ | dietas por tag, espécies em JSON, eventos |
| Marca original sem IP alheio | ✅ história e nomes autorais | revisar o ícone (anel + T. rex lembra o logo do filme) |
| Fabric e Forge com paridade | ✅ Architectury | levar para 1.21.1 NeoForge + Fabric |

## 4. Decisões

O Rodrigo deixou a frente decidir (24/10/2026). Ficam valendo até alguém registrar outra decisão aqui.

| # | Decisão | Por quê (estudo) |
|---|---|---|
| D1 | **Plataforma:** alphas em 1.20.1 Forge + Fabric (como está). **Port para 1.21.1 NeoForge + Fabric entre fev e abr/2027**; a v1.0 sai em 1.21.1 (principal) e 1.20.1 (manutenção). **Forge só na 1.20.1.** A versão 26.x-alvo se escolhe no 2º tri/2027, olhando para onde ATM, Cobblemon e Create forem. Bedrock só como projeto separado, não antes de 2028 | 04: 1.21.1 é o "LTS de fato" (ATM10, Cobblemon, Create, GeckoLib 4.9 vivo); Architectury API não tem Forge da 1.21 em diante; 26.x é port pesado (Java 25, GeckoLib 5) |
| D2 | **Qualidade antes de quantidade.** Nenhuma espécie nova entra no jogo sem passar o checklist do estudo 02 §7. Antes da v1.0, as espécies que já existem passam pelo **Passe de Qualidade** (densidade de texel, passo casado com a velocidade, camada procedural, animações que faltam). O núcleo da v1.0 são as espécies que passarem, não um número | 01: Mowzie's (11 mobs) > mods de 100 espécies medianas; 02: hoje a densidade varia 13x e os pés escorregam |
| D3 | **Densidade de texel: 16 px por metro** como padrão, piso de 8 acima de 15 m, teto de 32 abaixo de 1 m; filhote com geometria própria (`ontogeny`) | 02 §5.1 e §5.4 |
| D4 | **Escala:** spawner com cota por jogador e rodízio justo, errantes efêmeros (não vão para o disco), LOD de IA por distância, tracking range 8 / 10-12, dados por jogador em arquivo próprio; meta de 100 jogadores por backend e rede Velocity para mais | 03 §7-8 (21 riscos auditados) |
| D5 | **Dados abertos para modpacks:** dietas por tag já; espécies (números, dieta, habitat, loot) em JSON de datapack antes do port 1.21.1 (o `gen_species.py` passa a emitir); estado de item como record + Codec (nada de NBT cru), para o port virar data components sem dor | 03 §6, 04 §6.3 |
| D6 | **Integrações opcionais** (nunca dependência obrigatória): Jade/WTHIT, EMI (+ JEI/REI), tags `c:`, FTB Quests (documentar os IDs das conquistas), claims (FTB Chunks / OPAC), permissões (fabric-permissions-api / PermissionAPI) | 03 §5-6, ESCOPO "um mod só" |
| D7 | **Identidade visual "Âmbar e Basalto"** (`docs/IDENTIDADE.md`): basalto, pedra, osso, âmbar como único acento, papel do caderno; nada de ciano/vidro/hexágono (ARK) nem vermelho-amarelo-preto (filme) | pedido do Rodrigo; 05 §4.3 |
| D8 | **Posicionamento:** "o mod de dinossauros para quem leva dinossauros a sério" (ciência e escala real) como guarda-chuva; a aventura da Katarina nos trailers. Slogan: **"Atravesse a Fenda." / "Cross the Rift." / "Cruza la Grieta."** Ciência como padrão, silhuetas icônicas preservadas, variantes de pele e pena por resource pack | 01 §4.6, 05 §4.1-4.2 |
| D9 | **Nome: manter "Terrassic"** (já está em tudo; projetos criados no Modrinth e no CurseForge), com a ressalva legal do §4. Reservas se um advogado vetar: **Paleorift** ou **Mesorift** | 05 §3 |
| D10 | **Nomes de versão:** capítulo nas grandes (v1.0 "Ecos do Fim"...), tema nas médias, **"Leva"** nas expansões de bestiário depois da v1.0, builds de teste **"Ensaio"** (`1.0.0-ensaio.3`), revelação de espécie como **"Ficha nº 027"**. Mascote: **Sílex**, um Compsognathus curioso (já no mod) | 05 §4.4-4.5 |
| D11 | **Desempenho é requisito de produto:** cada versão sai com um perfil do spark num mundo de teste e um número de MSPT por jogadores, publicado no changelog | 01 §5.2 item 1, 03 §2 |

**Decisões do Rodrigo (24/10/2026)** (o plano recebido, `PLANO_MESTRE.md`, e `COORDENACAO.md` registram o que veio depois):
1. **Titular: Rodrigo Gomes, pessoa física.** O projeto é pessoal e **não pode ser vinculado a empresa nenhuma** (nem
   em código, créditos, licença, site ou redes).
2. **Licença (aplicada):** código **LGPL-3.0** (`LICENSE` + `COPYING`) e todos os assets **All Rights Reserved** com
   permissões explícitas (`LICENSE-ASSETS.md`: modpacks livres baixando do Modrinth/CurseForge, vídeos livres com
   monetização, addons livres sem usar o logo nem parecer oficial, ports não oficiais proibidos) e um CLA a favor do
   titular (`CLA.md`). O `fabric.mod.json` e o `mods.toml` já dizem isso.
3. **Projetos criados no Modrinth e no CurseForge** (o slug já está garantido).
4. **Ficam para depois, quando houver produto entregável** (fim do roadmap, marco "Lançamento"): registro no INPI,
   advogado sobre a marca "TERRASSIC" registrada nos EUA para produtos de terrário (fora do ramo de jogos), domínios e
   perfis nas redes sociais.

## 5. Antes do primeiro post público (quando houver produto entregável)

Nada disto é urgente: o Rodrigo deixou marca, domínios e redes para o fim do roadmap. Feito agora: titular definido,
licença aplicada, projetos no Modrinth e no CurseForge.

1. Disclaimer obrigatório da Mojang no README (já está), nas páginas do Modrinth e do CurseForge e no site: *"NOT AN
   OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT."*, com o responsável e um e-mail.
2. Revisar o ícone (sem T. rex de perfil dentro do anel) e adotar o monograma para avatar (`IDENTIDADE.md`).
3. Press kit (logo, monograma, paleta, as fontes próprias, textos do `RESUMO.md`) e storyboard do trailer a partir das
   9 cenas do `CAPA.md`.
4. Ir gravando clipes curtos de cada animação nova: viram o estoque do primeiro mês público.
5. **Na reta final (marco "Lançamento"):** domínios, perfis nas redes, Discord aberto, INPI e consulta sobre a marca
   americana.

## 6. Briefing para a sessão principal (o que fazer, em ordem)

Cada item aponta o estudo com os detalhes. Os de **qualidade de criatura** importam também para a thread de remodelagem
("Remodelar todos os dinos com mais detalhe"): se ela está refazendo modelos, **D3 (densidade de texel) e o contrato de
rig** devem entrar agora, antes de refazer os 53.

| # | Ação | Estudo | Arquivos principais | Esforço |
|---|---|---|---|---|
| 1 | **Errantes efêmeros:** `shouldBeSaved()` falso para errante selvagem sem nome; despawn ligado à simulation distance; errante não põe ninho; filhote de ovo selvagem nasce errante | 03 §3.2, riscos 2-3 | `DinosaurEntity`, `DinoEggBlock`, `EcoSpawner` | baixo |
| 2 | **Spawner orçado e justo:** cota por jogador (sugestão 12 terra / 5 céu / 7 mar), teto proporcional, rodízio, jogadores escalonados por hash, caixa limitada em Y, disjuntor por MSPT | 03 §3.1, riscos 1 e 5 | `EcoSpawner`, `gen_rules.py` | médio |
| 3 | **Metas baratas:** `AvoidEntityGoal` dos herbívoros com saída cedo (`fightsBack`, domado) e intervalo maior; predador testa `canHunt()` antes de varrer; `(tickCount + id) % N`; temporizadores por `gameTime` | 03 riscos 4, 7, 11 | `HerbivoreDinosaur`, `PredatorDinosaur`, `DinosaurEntity` | baixo |
| 4 | **Densidade de texel unificada** e re-autoria dos extremos (saurópodes, mosassauro, os menores de 2 m) | 02 §5.1 | `tools/modelgen`, `gen_species.py` (SIZES) | médio |
| 5 | **Passo casado com a velocidade:** o pipeline exporta `stride_m`/`cycle_s`; controlador que acumula a fase pela distância; passadas com som e poeira | 02 §2.4 | `tools/modelgen`, `DinosaurEntity` (controladores) | médio |
| 6 | **Camada procedural compartilhada:** olhar distribuído pelo pescoço, cauda e pescoço com inércia (ChainBuffer), IK de pé (bípede e quadrúpede), respiração, ociosos aleatórios; escrita como função pura (pronta para o GeckoLib 5) | 02 §2, §7 | `client/DinoGeoModel`, contrato de rig | alto |
| 7 | **Animações parciais e as que faltam:** roar/eat/call/attack só no corpo de cima; sleep, hatch, swim, hurt, death, turn, drink | 02 §6 item 4 | `tools/modelgen` | médio |
| 8 | **Dietas por tag** `terrassic:diet/<especie>` com `#c:foods/raw_meat` opcional; carnes do mod nas tags `c:` | 03 §6 | `gen_species.py`, entidades | baixo |
| 9 | **Tracking range** 8 (pequenos e médios) / 10-12 (gigantes), configurável; `Rules.of` sem lock | 03 riscos 9 e 12 | `ModEntities`, `Rules` | baixo |
| 10 | **Hitbox multiparte acima de 8 m** calculada no servidor (mixin no Fabric), câmera de montaria pela altura, navegação de gigantes (caixa ≤ 3, quebra de folhas respeitando claims) | 02 §3, 03 §5.3 | entidades grandes, mixins | alto |
| 11 | **Dados por jogador em arquivo por UUID** (`ResearchData`, `LeapProgress`) e sincronização delta do Conhecimento | 03 riscos 6 e 14 | `research/`, `leap/` | médio |
| 12 | **Claims e permissões:** quebra de bloco montada como do jogador, `getMobGriefingEvent` no Forge, nós de permissão, confiança de equipe para pets, limite de domados por jogador, `/terrassic pets` | 03 §5.2-5.4 | entidades de carga, comandos | médio |
| 13 | **Camada de plataforma e itens com Codec** antes do port 1.21.1: interface `Services` por loader, registro centralizado, payloads tipados, renderers que leem a entidade num ponto só | 04 §6.3 | `registry/`, `network/`, `client/` | médio |
| 14 | **Integrações leves:** Jade/WTHIT (sexo, fome, dono, crescimento), EMI/JEI (Mesa, escavação, chocar, dietas), página dos IDs de conquista para FTB Quests | 03 §6 | `compat/` novo (soft-dependencies) | baixo-médio |
| 15 | **Passar as telas restantes pela paleta** (`IDENTIDADE.md` §5) | IDENTIDADE | `client/` | baixo |

Itens 1 a 3 e 8 a 9 são baratos e destravam multiplayer: dá para fazer numa fase só. Itens 4 a 7 são o "Passe de
Qualidade" das criaturas e devem andar junto com a remodelagem.

## 7. Calendário (estimativas; a ordem importa mais que o mês)

| Período | Mod | Marca e comunidade |
|---|---|---|
| Nov/2026 | Passe de escala (itens 1-3, 8-9); testes da v0.3-v0.9 no jogo | identidade visual completa (paleta, fontes, kit de marca) |
| Dez/2026 - Jan/2027 | Passe de Qualidade das criaturas (itens 4-7) junto com a remodelagem; nocaute (v0.7); camada de plataforma (item 13) | testadores convidados direto pelo Rodrigo |
| Fev - Abr/2027 | **Port para 1.21.1 NeoForge + Fabric**; dados por jogador, claims, integrações (itens 11-14) | **Alpha fechada** ("Ensaio") com testadores convidados |
| Mai - Jun/2027 | Polimento do Capítulo 1 completo; perfis de spark públicos | **Early Access gratuito** nas páginas que já existem no Modrinth e no CurseForge (1.21.1 + 1.20.1) |
| Jul - Set/2027 | Hitbox multiparte e navegação de gigantes (item 10); balanceamento | **Lançamento da marca:** domínios, redes, Discord aberto, site com bestiário, INPI; modpack oficial; produção do trailer |
| Out/2027 (alvo) | **v1.0 "Ecos do Fim"** | lançamento coordenado: trailer em pt/en/es, site, Reddit, lives |
| 2º semestre/2027 | Escolha e port para a 26.x-alvo (GeckoLib 5) | — |
| 2028+ | v2.0 "Penas e Cinzas"; avaliar Bedrock via publishing partner | — |

## 8. Armadilhas (o que matou os outros)

- **Escopo de Prehistoric Nature:** cinco eras antes da v1.0. O Terrassic entrega **uma era excelente** primeiro (já é a regra).
- **Reescrever em vez de evoluir** (JurassiCraft → Project Nublar; Unusual Prehistory 1 → 2 zerou os downloads).
- **Perseguir versões:** ficar numa versão "LTS" por muito tempo, como Cobblemon e Create.
- **Bibliotecas próprias frágeis e dependências demais** (Dawn Era, F&A com quatro dependências).
- **Visual destoante do vanilla** (o "Visual Rework" do Ice and Fire tem 440k downloads): detalhe sim, com paleta e
  densidade de pixel do Minecraft.
- **Bugs de persistência em multiplayer** (domesticação perdida, dinos invisíveis para quem entra no servidor).
- **Moderação tóxica** no Discord oficial e **autor único** sem ninguém para continuar.
- **Clones falsos e malware** com o nome do mod: registrar o nome em todas as plataformas e manter uma página oficial
  de downloads.
- **Qualquer coisa que lembre Jurassic Park/World:** nome, logo de dinossauro em círculo vermelho e amarelo, InGen,
  híbridos, "life finds a way".
