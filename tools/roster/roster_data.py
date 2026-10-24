"""Bestiário completo do Terrassic, por era (dados brutos).

Cada linha:  Nome | grupo | dieta | tamanho |marcas| nota
- grupo: código de GROUPS em gen_roster.py (define o rótulo e o ambiente padrão).
- dieta: H herbívoro, C carnívoro, P piscívoro, O onívoro, I insetívoro, F filtrador.
- tamanho em metros, topo das estimativas publicadas (1 bloco = 1 m). Comprimento do corpo; envergadura nos
  voadores; sufixo "a" = altura (mamíferos grandes e aves que não voam). Valor de PLANEJAMENTO: a fonte exata
  entra em docs/TAMANHOS.md quando a espécie for implementada.
- marcas (opcional): @T @V @A @F troca o ambiente (terrestre, voador, aquático, anfíbio); VIVO = paria
  filhotes vivos (sem ovo).
- nota (opcional): o que a criatura faz de especial no jogo.

Rode `python3 gen_roster.py` depois de editar: ele escreve docs/bestiario/.
"""

ERAS = [
    ("cretaceo_superior", "Cretáceo Superior", "Capítulo 1: Ecos do Fim (Overworld)", "100 a 66 milhões de anos"),
    ("cretaceo_inferior", "Cretáceo Inferior", "Capítulo 2: Penas e Cinzas", "145 a 100 milhões de anos"),
    ("jurassico", "Jurássico", "Capítulo 3: O Reino dos Gigantes", "201 a 145 milhões de anos"),
    ("triassico", "Triássico", "Capítulo 4: A Origem", "252 a 201 milhões de anos"),
    ("era_do_gelo", "Era do Gelo", "Epílogo: O Caminho de Volta", "2,6 milhões a 11 mil anos (Pleistoceno)"),
]

DATA = {}

DATA["cretaceo_superior"] = """
# Tiranossauros
Tyrannosaurus|TIR|C|13
Tarbosaurus|TIR|C|12
Zhuchengtyrannus|TIR|C|11
Daspletosaurus|TIR|C|9
Albertosaurus|TIR|C|9
Gorgosaurus|TIR|C|9
Bistahieversor|TIR|C|9
Thanatotheristes|TIR|C|8
Lythronax|TIR|C|8
Dryptosaurus|TIR|C|7.5
Appalachiosaurus|TIR|C|7
Teratophoneus|TIR|C|6
Alioramus|TIR|C|6||focinho longo, caça presas rápidas
Qianzhousaurus|TIR|C|6
Nanuqsaurus|TIR|C|6||vive na neve do norte
Timurlengia|TIR|C|4
Moros|TIR|C|3
Suskityrannus|TIR|C|3
# Abelissauros e noassauros
Carnotaurus|ABE|C|8
Majungasaurus|ABE|C|8
Rajasaurus|ABE|C|8
Abelisaurus|ABE|C|9
Pycnonemosaurus|ABE|C|9
Skorpiovenator|ABE|C|7
Ekrixinatosaurus|ABE|C|7
Rugops|ABE|C|6||carniceiro, segue carcaças
Aucasaurus|ABE|C|6
Arcovenator|ABE|C|6
Viavenator|ABE|C|6
Llukalkan|ABE|C|5
Chenanisaurus|ABE|C|8
Quilmesaurus|ABE|C|5
Masiakasaurus|ABE|C|2||dentes para frente, pesca e caça lagartos
Noasaurus|ABE|C|1.5
Vespersaurus|ABE|C|1.5||anda sobre um dedo só, vive no deserto
Velocisaurus|ABE|C|1
# Carcarodontossauros e megaraptores
Giganotosaurus|CAR|C|13
Carcharodontosaurus|CAR|C|12
Mapusaurus|CAR|C|12||caça titanossauros em bando
Meraxes|CAR|C|11
Chilantaisaurus|CAR|C|11
Siats|CAR|C|11
Bahariasaurus|CAR|C|11
Maip|CAR|C|10
Aerosteon|CAR|C|9
Megaraptor|CAR|C|8||garra gigante no polegar
Deltadromeus|CAR|C|8
Shaochilong|CAR|C|6
Orkoraptor|CAR|C|6
Australovenator|CAR|C|6
Murusraptor|CAR|C|6
# Espinossauros
Spinosaurus|ESP|P|14
Oxalaia|ESP|P|12
# Raptores e parentes
Achillobator|RAP|C|6
Austroraptor|RAP|P|6||pesca nos rios da Patagônia
Dakotaraptor|RAP|C|5.5
Unenlagia|RAP|C|3.5
Acheroraptor|RAP|C|2.5
Pyroraptor|RAP|C|2.5
Velociraptor|RAP|C|2.07
Dromaeosaurus|RAP|C|2
Atrociraptor|RAP|C|2
Adasaurus|RAP|C|2
Tsaagan|RAP|C|2
Linheraptor|RAP|C|2
Balaur|RAP|C|2||duas garras em cada pé
Saurornitholestes|RAP|C|1.8
Buitreraptor|RAP|C|1.5
Bambiraptor|RAP|C|1
Mahakala|RAP|C|0.7
Hesperonychus|RAP|C|0.5
Halszkaraptor|RAP|P|0.6|@F|nada como um pato e pesca
Rahonavis|PAR|C|0.7
# Troodontídeos
Latenivenatrix|TRO|C|3.5
Troodon|TRO|C|2.4
Zanabazar|TRO|C|2.3
Saurornithoides|TRO|C|2
Talos|TRO|C|2
Byronosaurus|TRO|C|1.5
Gobivenator|TRO|C|1
# Ornitomimossauros
Deinocheirus|ORN|O|11
Gallimimus|ORN|O|6
Struthiomimus|ORN|O|4.3
Qiupalong|ORN|O|4
Ornithomimus|ORN|O|3.8
Garudimimus|ORN|O|3.5
Archaeornithomimus|ORN|O|3.4
Anserimimus|ORN|O|3
# Oviraptorossauros
Gigantoraptor|OVI|O|8||o maior oviraptor; montaria rápida
Anzu|OVI|O|3.5
Citipati|OVI|O|3
Chirostenotes|OVI|O|2.5
Oviraptor|OVI|O|2
Rinchenia|OVI|O|2
Nemegtomaia|OVI|O|2
Corythoraptor|OVI|O|1.6
Khaan|OVI|O|1.5
Conchoraptor|OVI|O|1.5||quebra conchas de moluscos
Heyuannia|OVI|O|1.5
Huanansaurus|OVI|O|1.5
Avimimus|OVI|O|1.5
# Terizinossauros
Therizinosaurus|TZN|H|10
Segnosaurus|TZN|H|7
Nothronychus|TZN|H|5.3
Erlikosaurus|TZN|H|3.5
# Alvarezssauros
Patagonykus|ALV|I|2
Alvarezsaurus|ALV|I|1.4
Mononykus|ALV|I|1
Albertonykus|ALV|I|0.7
Shuvuuia|ALV|I|0.6
Kol|ALV|I|1.5
# Aves
Gargantuavis|AVE|H|2||ave grande que não voa
Hesperornis|AVE|P|1.5|@A
Baptornis|AVE|P|1|@A
Ichthyornis|AVE|P|0.6|@V
Vegavis|AVE|O|0.6|@F|parente dos patos
Patagopteryx|AVE|O|0.5
Asteriornis|AVE|O|0.4|@V|o "frango do fim do mundo"
# Titanossauros e saurópodes
Patagotitan|TIT|H|37
Argentinosaurus|TIT|H|35
Alamosaurus|TIT|H|30
Puertasaurus|TIT|H|30
Notocolossus|TIT|H|28
Dreadnoughtus|TIT|H|26
Futalognkosaurus|TIT|H|26
Paralititan|TIT|H|26
Uberabatitan|TIT|H|26
Austroposeidon|TIT|H|25
Isisaurus|TIT|H|18
Ampelosaurus|TIT|H|16
Rapetosaurus|TIT|H|15
Jainosaurus|TIT|H|18
Diamantinasaurus|TIT|H|16
Savannasaurus|TIT|H|15
Wintonotitan|TIT|H|15
Lohuecotitan|TIT|H|9
Atsinganosaurus|TIT|H|9
Lirainosaurus|TIT|H|4
Aeolosaurus|TIT|H|15
Maxakalisaurus|TIT|H|13
Saltasaurus|TIT|H|12
Nemegtosaurus|TIT|H|12
Opisthocoelicaudia|TIT|H|12
Sarmientosaurus|TIT|H|12
Rinconsaurus|TIT|H|11
Mansourasaurus|TIT|H|10
Neuquensaurus|TIT|H|7
Magyarosaurus|TIT|H|6||titanossauro anão das ilhas
# Ceratopsianos
Triceratops|CER|H|9
Torosaurus|CER|H|9
Pachyrhinosaurus|CER|H|8
Sinoceratops|CER|H|7
Pentaceratops|CER|H|7
Utahceratops|CER|H|7
Coahuilaceratops|CER|H|6.7
Centrosaurus|CER|H|6
Achelousaurus|CER|H|6
Medusaceratops|CER|H|6
Anchiceratops|CER|H|6
Wendiceratops|CER|H|6
Styracosaurus|CER|H|5.5
Diabloceratops|CER|H|5.5
Chasmosaurus|CER|H|5
Kosmoceratops|CER|H|5||o mais enfeitado de todos, 15 chifres
Regaliceratops|CER|H|5
Albertaceratops|CER|H|6
Xenoceratops|CER|H|6
Mercuriceratops|CER|H|6
Avaceratops|CER|H|4.5
Vagaceratops|CER|H|4.5
Spiclypeus|CER|H|4.5
Ajkaceratops|CER|H|1
Einiosaurus|CER|H|4.5
Nasutoceratops|CER|H|4.5
Zuniceratops|CER|H|3.5
Montanoceratops|CER|H|3
Protoceratops|CER|H|2
Leptoceratops|CER|H|2
Bagaceratops|CER|H|1
# Anquilossauros e nodossauros
Ankylosaurus|ANQ|H|8
Tarchia|ANQ|H|8
Saichania|ANQ|H|6.6
Euoplocephalus|ANQ|H|6
Talarurus|ANQ|H|6
Scolosaurus|ANQ|H|6
Anodontosaurus|ANQ|H|6
Zuul|ANQ|H|6
Pinacosaurus|ANQ|H|5
Dyoplosaurus|ANQ|H|4
Akainacephalus|ANQ|H|5
Nodocephalosaurus|ANQ|H|4.5
Panoplosaurus|NOD|H|7
Edmontonia|NOD|H|6.6
Denversaurus|NOD|H|6
Nodosaurus|NOD|H|6
Hungarosaurus|NOD|H|4.5
Silvisaurus|NOD|H|4
Antarctopelta|NOD|H|4||vive no frio do sul
Struthiosaurus|NOD|H|3
# Hadrossauros
Shantungosaurus|HAD|H|16.6||o maior hadrossauro
Magnapaulia|HAD|H|15
Charonosaurus|HAD|H|13
Edmontosaurus|HAD|H|12
Saurolophus|HAD|H|12
Brachylophosaurus|HAD|H|11
Tsintaosaurus|HAD|H|10
Parasaurolophus|HAD|H|9.5
Lambeosaurus|HAD|H|9.4
Maiasaura|HAD|H|9
Corythosaurus|HAD|H|9
Hypacrosaurus|HAD|H|9
Gryposaurus|HAD|H|9
Kritosaurus|HAD|H|9
Prosaurolophus|HAD|H|8.5
Olorotitan|HAD|H|8
Hadrosaurus|HAD|H|8
Amurosaurus|HAD|H|8
Kamuysaurus|HAD|H|8
Acristavus|HAD|H|8
Bactrosaurus|HAD|H|6
Secernosaurus|HAD|H|3
Telmatosaurus|HAD|H|5||hadrossauro anão das ilhas
Tethyshadros|HAD|H|4
# Ornitópodes pequenos
Thescelosaurus|ORP|H|4
Rhabdodon|ORP|H|4
Talenkauen|ORP|H|4
Orodromeus|ORP|H|2.5
Zalmoxes|ORP|H|2.5
Parksosaurus|ORP|H|2.5
Oryctodromeus|ORP|H|2.1||cava tocas e se esconde nelas
Mochlodon|ORP|H|2
Gasparinisaura|ORP|H|1
# Paquicefalossauros
Pachycephalosaurus|PAQ|H|4.5
Stegoceras|PAQ|H|2.5
Prenocephale|PAQ|H|2.4
Sphaerotholus|PAQ|H|2
Tylocephale|PAQ|H|2
Homalocephale|PAQ|H|1.8
Acrotholus|PAQ|H|1.8
# Pterossauros
Hatzegopteryx|PTE|C|12
Quetzalcoatlus|PTE|C|11
Arambourgiania|PTE|C|10
Cryodrakon|PTE|C|10
Pteranodon|PTE|P|7.25
Azhdarcho|PTE|C|4.5
Zhejiangopterus|PTE|C|3.5
Bakonydraco|PTE|C|3.5
Caiuajara|PTE|H|2.4||vive em colônias no deserto
Nyctosaurus|PTE|P|2||crista gigante em forma de antena
# Mosassauros
Mosasaurus|MOS|C|17
Tylosaurus|MOS|C|13
Prognathodon|MOS|C|12
Plotosaurus|MOS|C|10
Kaikaifilu|MOS|C|10
Taniwhasaurus|MOS|C|9
Platecarpus|MOS|P|7
Clidastes|MOS|P|6
Globidens|MOS|C|6||dentes redondos que quebram conchas
Plioplatecarpus|MOS|P|6
Pannoniasaurus|MOS|C|6|@F|mosassauro de rio
Halisaurus|MOS|P|4
Phosphorosaurus|MOS|P|3
Dallasaurus|MOS|C|1|@F|anda na praia e nada
# Plesiossauros e pliossauros
Thalassomedon|PLE|P|12
Albertonectes|PLE|P|11.6
Styxosaurus|PLE|P|11
Elasmosaurus|PLE|P|10
Aristonectes|PLE|F|10||filtra crustáceos como uma baleia
Futabasaurus|PLE|P|9
Hydrotherosaurus|PLE|P|8
Tuarangisaurus|PLE|P|8
Libonectes|PLE|P|7
Kaiwhekea|PLE|P|7
Polycotylus|PLI|P|5
Dolichorhynchops|PLI|P|5
Brachauchenius|PLI|C|10
Megacephalosaurus|PLI|C|9
# Peixes e tubarões
Ptychodus|TUB|C|10||tubarão que esmaga conchas
Cretoxyrhina|TUB|C|8
Onchopristis|TUB|P|8||peixe-serra gigante de rio
Squalicorax|TUB|C|5
Scapanorhynchus|TUB|C|3
Bonnerichthys|PEI|F|6
Xiphactinus|PEI|C|5
Protosphyraena|PEI|C|3
Ichthyodectes|PEI|C|3
Gillicus|PEI|P|2
Enchodus|PEI|P|1.5||o "arenque dente-de-sabre"
# Crocodilos
Deinosuchus|CRO|C|12
Kaprosuchus|CRT|C|6||crocodilo javali, com presas
Laganosuchus|CRO|P|6
Mahajangasuchus|CRO|C|4
Baurusuchus|CRT|C|3.5
Leidyosuchus|CRO|C|3
Borealosuchus|CRO|C|3
Brachychampsa|CRO|C|2.5
Shamosuchus|CRO|C|2
Armadillosuchus|CRT|O|2||crocodilo blindado que cava como tatu
Mariliasuchus|CRT|O|1||cava tocas
Simosuchus|CRT|H|0.75||crocodilo herbívoro de focinho curto
# Tartarugas
Archelon|TAM|O|4.6
Protostega|TAM|O|3
Desmatochelys|TAM|O|2
Toxochelys|TAM|O|1.5
Basilemys|TAR|H|1.5|@T
# Lagartos, serpentes e anfíbios
Madtsoia|LAG|C|6||serpente constritora gigante
Sanajeh|LAG|C|3.5||serpente que come ovos e filhotes de dinossauro
Dinilysia|LAG|C|2
Najash|LAG|C|2||serpente que ainda tinha patas traseiras
Polyglyphanodon|LAG|H|1.3
Estesia|LAG|C|1||lagarto de mordida venenosa
Pachyrhachis|LAG|P|1|@A
Beelzebufo|ANF|C|0.4||sapo-diabo, come filhotes
# Mamíferos
Didelphodon|MAM|O|0.8
Adalatherium|MAM|O|0.5
Vintana|MAM|H|0.5
Cimolestes|MAM|I|0.3
Alphadon|MAM|O|0.3
Zalambdalestes|MAM|I|0.2
Deltatheridium|MAM|C|0.15
Kryptobaatar|MAM|H|0.1
Mesodma|MAM|H|0.1
# Invertebrados
Parapuzosia|INV|C|2.5||amonite gigante
Baculites|INV|C|2||amonite reta
Inoceramus|INV|F|1.8||marisco gigante
Placenticeras|INV|C|1
Scaphites|INV|C|0.2
"""

DATA["cretaceo_inferior"] = """
# Grandes predadores
Tyrannotitan|CAR|C|12
Acrocanthosaurus|CAR|C|11.5
Neovenator|CAR|C|7.5
Eocarcharia|CAR|C|7
Concavenator|CAR|C|6
Fukuiraptor|CAR|C|4.2
Suchomimus|ESP|P|11
Baryonyx|ESP|P|10
Ichthyovenator|ESP|P|9
Riparovenator|ESP|P|9
Siamosaurus|ESP|P|9
Ceratosuchops|ESP|P|8
Irritator|ESP|P|8
Kryptops|ABE|C|6
Yutyrannus|TIR|C|9
Siamotyrannus|TIR|C|6
Eotyrannus|TIR|C|4
Iberospinus|ESP|P|8
Dilong|TIR|C|1.6
Xiongguanlong|TIR|C|4
# Raptores, troodontídeos e pequenos terópodes
Utahraptor|RAP|C|7
Deinonychus|RAP|C|3.4
Zhenyuanlong|RAP|C|1.65
Tianyuraptor|RAP|C|1.6
Changyuraptor|RAP|C|1.3
Sinornithosaurus|RAP|C|1||mordida venenosa (hipótese)
Microraptor|PAR|C|0.8
Sinornithoides|TRO|C|1.1
Jianianhualong|TRO|C|1.1
Sinovenator|TRO|C|1
Sinusonasus|TRO|C|1
Graciliraptor|RAP|C|0.9
Yurgovuchia|RAP|C|2.5
Geminiraptor|TRO|C|2
Jinfengopteryx|TRO|C|0.55
Mei|TRO|C|0.5||dorme enrolado como pássaro
Sinocalliopteryx|CEL|C|2.4
Mirischia|CEL|C|2
Huaxiagnathus|CEL|C|1.8
Santanaraptor|CEL|C|1.5
Sinosauropteryx|CEL|C|1
Nedcolbertia|CEL|C|3
Fukuivenator|TER|O|2.5
# Ornitomimossauros, oviraptorossauros e terizinossauros
Pelecanimimus|ORN|O|2.5||mais de 200 dentes; pesca
Harpymimus|ORN|O|2
Nqwebasaurus|ORN|O|1
Shenzhousaurus|ORN|O|1.6
Microvenator|OVI|O|1.2
Caudipteryx|OVI|O|1
Incisivosaurus|OVI|H|1
Protarchaeopteryx|OVI|O|0.7
Falcarius|TZN|H|4
Alxasaurus|TZN|H|4
Beipiaosaurus|TZN|H|2.2
# Aves
Jeholornis|AVE|O|0.8|@V
Confuciusornis|AVE|O|0.7|@V
Sapeornis|AVE|H|0.5|@V
Gansus|AVE|P|0.4|@V|ave mergulhadora
Longipteryx|AVE|P|0.3|@V
Iberomesornis|AVE|I|0.2|@V
# Saurópodes
Sauroposeidon|SAU|H|30
Ruyangosaurus|TIT|H|30
Daxiatitan|TIT|H|25
Chubutisaurus|TIT|H|23
Fusuisaurus|TIT|H|22
Rebbachisaurus|SAU|H|20
Phuwiangosaurus|TIT|H|19
Abydosaurus|SAU|H|18
Aragosaurus|SAU|H|18
Andesaurus|TIT|H|18
Malawisaurus|TIT|H|16
Tastavinsaurus|SAU|H|16
Cedarosaurus|SAU|H|15
Limaysaurus|SAU|H|15
Agustinia|SAU|H|15||saurópode com espinhos nas costas
Brontomerus|SAU|H|14||coxa enorme, chuta predadores
Tapuiasaurus|TIT|H|13
Venenosaurus|SAU|H|12
Euhelopus|SAU|H|11
Amargasaurus|SAU|H|10
Demandasaurus|SAU|H|10
Nigersaurus|SAU|H|9
Bajadasaurus|SAU|H|9
Leinkupal|SAU|H|9
Ligabuesaurus|TIT|H|20
Mierasaurus|SAU|H|15
Moabosaurus|SAU|H|10
Fukuititan|TIT|H|10
Zapalasaurus|SAU|H|9
# Iguanodontes e ornitópodes
Iguanodon|IGU|H|13
Lurdusaurus|IGU|H|9
Eolambia|IGU|H|9
Ouranosaurus|IGU|H|8.3
Muttaburrasaurus|IGU|H|8
Barilium|IGU|H|8
Altirhinus|IGU|H|8
Mantellisaurus|IGU|H|7
Tenontosaurus|IGU|H|7
Equijubus|IGU|H|7
Jinzhousaurus|IGU|H|7
Probactrosaurus|IGU|H|6
Hypselospinus|IGU|H|6
Proa|IGU|H|6
Lanzhousaurus|IGU|H|10
Iguanacolossus|IGU|H|9
Bayannurosaurus|IGU|H|9
Hippodraco|IGU|H|4.5
Planicoxa|IGU|H|4.5
Morelladon|IGU|H|6||pequena vela nas costas
Fukuisaurus|IGU|H|4.7
Valdosaurus|ORP|H|4
Atlascopcosaurus|ORP|H|3
Bolong|IGU|H|3
Hypsilophodon|ORP|H|2
Leaellynasaura|ORP|H|2||vive nas florestas polares, enxerga no escuro
Zephyrosaurus|ORP|H|1.8
Diluvicursor|ORP|H|2.3
Qantassaurus|ORP|H|1.8
Elrhazosaurus|ORP|H|1.5
Changchunsaurus|ORP|H|1.5
Jeholosaurus|ORP|H|1.4
Echinodon|HET|O|0.6
# Ceratopsianos
Psittacosaurus|CER|H|2
Koreaceratops|CER|H|1.7
Auroraceratops|CER|H|1.3
Archaeoceratops|CER|H|1
Aquilops|CER|H|0.6
Liaoceratops|CER|H|0.5
Yamaceratops|CER|H|0.5
# Anquilossauros, nodossauros e estegossauros
Cedarpelta|ANQ|H|7.5
Gobisaurus|ANQ|H|6
Shamosaurus|ANQ|H|5
Chuanqilong|ANQ|H|4.5
Minmi|ANQ|H|3
Kunbarrasaurus|ANQ|H|2.5
Borealopelta|NOD|H|5.5||armadura tão bem preservada que se sabe a cor
Peloroplites|NOD|H|5.5
Sauropelta|NOD|H|5
Gastonia|NOD|H|5
Polacanthus|NOD|H|5
Hylaeosaurus|NOD|H|5
Europelta|NOD|H|4.5
Animantarx|NOD|H|3
Liaoningosaurus|NOD|O|0.34|@F|anquilossauro minúsculo que pode ter pescado
Wuerhosaurus|EST|H|7
# Pterossauros
Tropeognathus|PTE|P|8.7
Moganopterus|PTE|P|7
Coloborhynchus|PTE|P|7
Tupuxuara|PTE|O|5.4
Ornithocheirus|PTE|P|5
Caulkicephalus|PTE|P|5
Tupandactylus|PTE|H|5
Anhanguera|PTE|P|4.5
Thalassodromeus|PTE|P|4.5||crista gigante; pesca roçando a água
Istiodactylus|PTE|C|4.3||carniceiro, come carcaças
Zhenyuanopterus|PTE|P|4
Guidraco|PTE|P|4
Tapejara|PTE|O|3.5
Hamipterus|PTE|P|3.5||colônias enormes de ninhos
Dsungaripterus|PTE|O|3||bico curvo que quebra conchas
Pterodaustro|PTE|F|3||filtra a água como um flamingo
Nurhachius|PTE|P|2.5
Ikrandraco|PTE|P|1.5
Sinopterus|PTE|O|1.2
# Répteis marinhos
Kronosaurus|PLI|C|10
Sachicasaurus|PLI|C|10
Callawayasaurus|PLE|P|8
Eromangasaurus|PLE|P|7
Opallionectes|PLE|P|6
Brancasaurus|PLE|P|3.5
Leptocleidus|PLE|P|3
Umoonasaurus|PLE|P|2.5
Platypterygius|ICT|P|7
Malawania|ICT|P|4
Acamptonectes|ICT|P|4
Sveltonectes|ICT|P|4
# Crocodilos e coristoderos
Sarcosuchus|CRO|C|9.5
Pholidosaurus|CRO|P|3
Isisfordia|CRO|C|1.1
Hylaeochampsa|CRO|C|1
Araripesuchus|CRT|C|1
Anatosuchus|CRT|I|0.7||crocodilo de focinho de pato
Bernissartia|CRO|O|0.6
Ikechosaurus|COR|P|1.5
Monjurosuchus|COR|P|1
Hyphalosaurus|COR|P|0.8||pescoço comprido, vive nos lagos
# Tartarugas, lagartos e anfíbios
Araripemys|TAR|C|0.25
Santanachelys|TAM|O|0.2||uma das primeiras tartarugas marinhas
Sinemys|TAR|O|0.3
Manchurochelys|TAR|O|0.3
Yabeinosaurus|LAG|C|0.4
Dalinghosaurus|LAG|I|0.3
Callobatrachus|ANF|I|0.1
Liaobatrachus|ANF|I|0.1
# Peixes
Mawsonia|PEI|C|6||celacanto gigante
Axelrodichthys|PEI|C|2
Cladocyclus|PEI|C|1.2
Peipiaosteus|PEI|C|1
Protopsephurus|PEI|F|1
Vinctifer|PEI|P|1
Lycoptera|PEI|P|0.1
# Mamíferos
Repenomamus|MAM|C|1
Gobiconodon|MAM|C|0.5
Steropodon|MAM|O|0.4||monotremado, parente do ornitorrinco
Vincelestes|MAM|O|0.3
Spinolestes|MAM|I|0.24||tinha espinhos como um ouriço
Zhangheotherium|MAM|I|0.15
Jeholodens|MAM|I|0.15
Sinodelphys|MAM|I|0.15
Eomaia|MAM|I|0.1
Teinolophos|MAM|O|0.1
"""

DATA["jurassico"] = """
# Grandes predadores
Saurophaganax|CAR|C|11
Yangchuanosaurus|CAR|C|11
Torvosaurus|MEG|C|10
Allosaurus|CAR|C|9.7
Megalosaurus|MEG|C|9
Metriacanthosaurus|CAR|C|8
Afrovenator|MEG|C|8
Wiehenvenator|MEG|C|8
Asfaltovenator|CAR|C|8
Sinraptor|CAR|C|7.6
Ceratosaurus|ABE|C|7
Dilophosaurus|TER|C|7
Eoabelisaurus|ABE|C|6.5
Cryolophosaurus|TER|C|6.5
Elaphrosaurus|ABE|O|6
Eustreptospondylus|MEG|C|6
Duriavenator|MEG|C|6
Leshansaurus|MEG|C|6
Sinosaurus|TER|C|5.6
Dracovenator|TER|C|5.5
Monolophosaurus|MEG|C|5
Marshosaurus|MEG|C|5
Condorraptor|MEG|C|5
Dubreuillosaurus|MEG|P|5
Berberosaurus|ABE|C|5
Juratyrant|TIR|C|5
Lourinhanosaurus|CAR|C|4.5
Xuanhanosaurus|MEG|C|4.5
Piatnitzkysaurus|MEG|C|4.3
Gasosaurus|MEG|C|4
Magnosaurus|MEG|C|4
Stokesosaurus|TIR|C|4
# Pequenos terópodes e paravianos
Tanycolagreus|CEL|C|3.3
Guanlong|TIR|C|3
Proceratosaurus|TIR|C|3
Coelurus|CEL|C|2.5
Ornitholestes|CEL|C|2
Limusaurus|ABE|H|1.7||perde os dentes ao crescer
Kileskus|TIR|C|1.5
Compsognathus|CEL|C|1.25
Juravenator|CEL|P|0.8
Xiaotingia|PAR|C|0.6
Yi|PAR|I|0.6||asas de morcego; plana entre árvores
Archaeopteryx|PAR|C|0.5
Aurornis|PAR|C|0.5
Anchiornis|PAR|C|0.4
Eosinopteryx|PAR|I|0.3
Ambopteryx|PAR|I|0.3
Epidexipteryx|PAR|I|0.25|@T|penas de enfeite na cauda
# Saurópodes
Mamenchisaurus|SAU|H|35
Supersaurus|SAU|H|34
Diplodocus|SAU|H|32||D. hallorum, o maior
Turiasaurus|SAU|H|30
Xinjiangtitan|SAU|H|30
Barosaurus|SAU|H|26
Lusotitan|SAU|H|25
Dinheirosaurus|SAU|H|25
Apatosaurus|SAU|H|23
Camarasaurus|SAU|H|23
Giraffatitan|SAU|H|23
Brachiosaurus|SAU|H|22
Brontosaurus|SAU|H|22
Omeisaurus|SAU|H|20
Barapasaurus|SAU|H|18
Klamelisaurus|SAU|H|17
Lingwulong|SAU|H|17
Janenschia|SAU|H|17
Cetiosaurus|SAU|H|16
Patagosaurus|SAU|H|16
Galeamopus|SAU|H|15
Suuwassea|SAU|H|15
Haplocanthosaurus|SAU|H|15
Atlasaurus|SAU|H|15
Tehuelchesaurus|SAU|H|15
Datousaurus|SAU|H|15
Bagualia|SAU|H|15
Kaatedocus|SAU|H|14
Gongxianosaurus|SAU|H|14
Ledumahadi|SPM|H|14
Dicraeosaurus|SAU|H|13
Spinophorosaurus|SAU|H|13
Vulcanodon|SAU|H|11
Brachytrachelopan|SAU|H|10||saurópode de pescoço curto
Shunosaurus|SAU|H|9.5||cauda com clava
Tazoudasaurus|SAU|H|9
Europasaurus|SAU|H|6.2
# Sauropodomorfos do Jurássico Inferior
Lufengosaurus|SPM|H|9
Jingshanosaurus|SPM|H|9
Pulanesaura|SPM|H|9
Yunnanosaurus|SPM|H|7
Aardonyx|SPM|H|7
Massospondylus|SPM|H|6
Xingxiulong|SPM|H|6
Sarahsaurus|SPM|H|4
Seitaad|SPM|H|3.5
Anchisaurus|SPM|H|2.5
# Estegossauros e anquilossauros
Stegosaurus|EST|H|9
Dacentrurus|EST|H|8
Tuojiangosaurus|EST|H|7
Miragaia|EST|H|6.5||pescoço longo como de saurópode
Hesperosaurus|EST|H|6.5
Loricatosaurus|EST|H|6
Jiangjunosaurus|EST|H|6
Kentrosaurus|EST|H|4.5
Huayangosaurus|EST|H|4.5
Gigantspinosaurus|EST|H|4.2||espinhos gigantes nos ombros
Chungkingosaurus|EST|H|4
Chialingosaurus|EST|H|4
Gargoyleosaurus|ANQ|H|4
Scelidosaurus|ANQ|H|4
Mymoorapelta|ANQ|H|3
Emausaurus|ANQ|H|2.5
Scutellosaurus|ANQ|H|1.3
# Ornitópodes e outros ornitísquios
Camptosaurus|IGU|H|7.9
Cumnoria|IGU|H|5
Dryosaurus|ORP|H|4.3
Dysalotosaurus|ORP|H|4
Draconyx|IGU|H|3
Nanosaurus|ORP|H|2
Lesothosaurus|ORP|H|2
Hexinlusaurus|ORP|H|1.8
Agilisaurus|ORP|H|1.7
Heterodontosaurus|HET|O|1.75||presas como um javali
Yandusaurus|ORP|H|1.5
Kulindadromeus|ORP|H|1.5||ornitísquio com penas
Abrictosaurus|HET|O|1.2
Yinlong|CER|H|1.2||o primeiro ceratopsiano
Chaoyangsaurus|CER|H|1
Laquintasaura|ORP|H|1
Fruitadens|HET|O|0.7
Tianyulong|HET|O|0.7
Manidens|HET|O|0.6
Pegomastax|HET|O|0.6
# Pterossauros
Dearc|PTE|P|2.5||o maior pterossauro do Jurássico
Harpactognathus|PTE|C|2.5
Rhamphorhynchus|PTE|P|1.8
Campylognathoides|PTE|C|1.8
Dorygnathus|PTE|P|1.7
Gnathosaurus|PTE|F|1.7
Angustinaripterus|PTE|P|1.6
Kryptodrakon|PTE|C|1.5
Dimorphodon|PTE|C|1.45
Cycnorhamphus|PTE|P|1.3
Ctenochasma|PTE|F|1.2||dentes de pente; filtra a água
Pterodactylus|PTE|C|1.04
Germanodactylus|PTE|P|1
Scaphognathus|PTE|C|0.9
Jeholopterus|PTE|I|0.9
Darwinopterus|PTE|C|0.9
Aerodactylus|PTE|C|0.8
Wukongopterus|PTE|C|0.7
Kunpengopterus|PTE|C|0.7
Sordes|PTE|I|0.6||pterossauro peludo
Anurognathus|PTE|I|0.5||caça insetos no escuro
Batrachognathus|PTE|I|0.5
# Répteis marinhos
Leedsichthys|PEI|F|16.5
Pliosaurus|PLI|C|12
Temnodontosaurus|ICT|C|12||olhos do tamanho de pratos
Liopleurodon|PLI|C|7
Rhomaleosaurus|PLI|C|7
Excalibosaurus|ICT|P|7||focinho de espadarte
Ophthalmosaurus|ICT|P|6
Eurhinosaurus|ICT|P|6
Undorosaurus|ICT|P|6
Muraenosaurus|PLE|P|6
Simolestes|PLI|C|5
Attenborosaurus|PLI|C|5
Microcleidus|PLE|P|5
Stenopterygius|ICT|P|4
Leptonectes|ICT|P|4
Suevoleviathan|ICT|P|4
Brachypterygius|ICT|P|4
Aegirosaurus|ICT|P|4
Cryptoclidus|PLE|P|4
Hauffiosaurus|PLI|C|4
Peloneustes|PLI|P|3.5
Plesiosaurus|PLE|P|3.5
Ichthyosaurus|ICT|P|3.3
Hauffiopteryx|ICT|P|3
Thalassiodracon|PLE|P|2
# Crocodilos
Machimosaurus|CRM|C|7||teleossauro gigante de dentes rombos
Plesiosuchus|CRM|C|7
Dakosaurus|CRM|C|5
Steneosaurus|CRM|P|4
Torvoneustes|CRM|C|4
Metriorhynchus|CRM|C|3
Geosaurus|CRM|C|3
Cricosaurus|CRM|P|3
Teleosaurus|CRM|P|3
Goniopholis|CRO|C|3
Pelagosaurus|CRM|P|1
Protosuchus|CRT|C|1
Junggarsuchus|CRT|C|1
Fruitachampsa|CRT|C|0.5
# Peixes
Asteracanthus|TUB|C|3
Hybodus|TUB|C|2
Lepidotes|PEI|O|2
Pachycormus|PEI|C|1
Caturus|PEI|C|1
Aspidorhynchus|PEI|P|0.6
Gyrodus|PEI|O|0.5
Dapedium|PEI|O|0.4
Leptolepis|PEI|P|0.2
# Tartarugas, lagartos e anfíbios
Plesiochelys|TAR|O|0.5
Eileanchelys|TAR|O|0.5
Kayentachelys|TAR|O|0.3
Pleurosaurus|ESF|P|1.5|@A|esfenodonte nadador
Homoeosaurus|ESF|I|0.2
Eichstaettisaurus|LAG|I|0.2
Ardeosaurus|LAG|I|0.2
Bavarisaurus|LAG|I|0.15
Cteniogenys|COR|P|0.3
Karaurus|ANF|I|0.2||uma das primeiras salamandras
Prosalirus|ANF|I|0.1||um dos primeiros sapos que pulavam
Vieraella|ANF|I|0.03
# Mamíferos e parentes
Kayentatherium|CIN|H|1
Bienotherium|CIN|H|0.8
Tritylodon|CIN|H|0.6
Oligokyphus|CIN|H|0.5
Castorocauda|MAM|P|0.45|@F|nadava como um castor
Maiopatagium|MAM|H|0.25|@V|planador
Fruitafossor|MAM|I|0.15
Agilodocodon|MAM|I|0.15
Volaticotherium|MAM|I|0.13|@V|planador
Docofossor|MAM|I|0.1||cava como uma toupeira
Juramaia|MAM|I|0.1
Morganucodon|MAM|I|0.1
Megazostrodon|MAM|I|0.1
Hadrocodium|MAM|I|0.03
# Invertebrados
Seirocrinus|INV|F|20||lírio-do-mar gigante preso a troncos flutuantes
Megateuthis|INV|C|3||belemnite gigante
Perisphinctes|INV|C|0.5
Mesolimulus|INV|O|0.2||caranguejo-ferradura
Dactylioceras|INV|C|0.1
Kalligramma|INS|O|0.15||"borboleta" do Jurássico (crisopídeo)
"""

DATA["triassico"] = """
# Primeiros dinossauros e parentes
Plateosaurus|SPM|H|10
Riojasaurus|SPM|H|10
Ingentia|SPM|H|10
Lessemsaurus|SPM|H|9
Camelotia|SPM|H|9
Isanosaurus|SAU|H|13
Mussaurus|SPM|H|8
Melanorosaurus|SPM|H|8
Antetonitrus|SPM|H|8
Ruehleia|SPM|H|8
Efraasia|SPM|H|6
Herrerasaurus|DIN|C|6
Liliensternus|TER|C|5.2
Zupaysaurus|TER|C|5
Coloradisaurus|SPM|H|4
Macrocollum|SPM|H|3.5
Coelophysis|TER|C|3
Gnathovorax|DIN|C|3
Sanjuansaurus|DIN|C|3
Unaysaurus|SPM|H|2.5
Thecodontosaurus|SPM|H|2.5
Tawa|TER|C|2.5
Staurikosaurus|DIN|C|2.25
Chindesaurus|DIN|C|2
Chromogisaurus|SPM|O|2
Pantydraco|SPM|O|2
Silesaurus|DIN|H|2.3||dinossauriforme de bico
Eoraptor|DIN|O|1.7
Saturnalia|SPM|O|1.5
Buriolestes|SPM|C|1.5
Daemonosaurus|TER|C|1.5
Asilisaurus|DIN|H|1.5
Pampadromaeus|SPM|O|1.4
Panphagia|SPM|O|1.3
Eodromaeus|DIN|C|1.2
Procompsognathus|TER|C|1
Eocursor|ORP|H|1
Pisanosaurus|DIN|H|1
Dromomeron|DIN|C|1
Lagerpeton|DIN|C|0.7
Marasuchus|DIN|C|0.5
Scleromochlus|DIN|I|0.2||parente minúsculo dos pterossauros, pula como sapo
Kongonaphon|DIN|I|0.1
# Parentes dos crocodilos (pseudossúquios)
Saurosuchus|PSE|C|9
Fasolasuchus|PSE|C|9
Sillosuchus|PSE|O|9
Prestosuchus|PSE|C|7
Batrachotomus|PSE|C|6
Smok|PSE|C|6
Teratosaurus|PSE|C|6
Polonosuchus|PSE|C|6
Postosuchus|PSE|C|5
Longosuchus|PSE|H|5
Desmatosuchus|PSE|H|4.5
Poposaurus|PSE|C|4
Ornithosuchus|PSE|C|4
Ticinosuchus|PSE|C|3
Arizonasaurus|PSE|C|3||vela nas costas
Shuvosaurus|PSE|O|3
Effigia|PSE|O|3
Stagonolepis|PSE|H|3
Typothorax|PSE|H|3
Paratypothorax|PSE|H|3
Aetosauroides|PSE|H|3
Qianosuchus|PSE|C|3|@F|nada e caça no mar raso
Lotosaurus|PSE|H|2.5||vela nas costas, sem dentes
Neoaetosauroides|PSE|H|2
Riojasuchus|PSE|C|2
Aetosaurus|PSE|H|1.5
Hesperosuchus|PSE|C|1.2
Revueltosaurus|PSE|H|1
Dromicosuchus|PSE|C|1
Saltoposuchus|PSE|C|1
Terrestrisuchus|PSE|C|0.6
Erpetosuchus|PSE|C|0.5
Gracilisuchus|PSE|C|0.3
# Fitossauros e outros arcossauriformes
Smilosuchus|FIT|C|12
Rutiodon|FIT|P|8
Machaeroprosopus|FIT|C|7
Angistorhinus|FIT|C|7
Redondasaurus|FIT|C|6.5
Nicrosaurus|FIT|C|6
Mystriosuchus|FIT|P|6|@A|fitossauro marinho
Parasuchus|FIT|P|3
Erythrosuchus|ARC|C|5
Garjainia|ARC|C|2.5
Proterochampsa|ARC|P|2.5
Proterosuchus|ARC|C|2
Doswellia|ARC|C|2||coberto de placas
Chanaresuchus|ARC|P|1.5
Vancleavea|ARC|P|1.2|@F|blindado, nada como enguia
Euparkeria|ARC|C|0.6
# Rincossauros, alocotossauros e outros répteis
Shringasaurus|REP|H|4||chifres na cabeça
Azendohsaurus|REP|H|3
Trilophosaurus|REP|H|2.5
Isalorhynchus|RIN|H|2
Stenaulorhynchus|RIN|H|1.5
Hyperodapedon|RIN|H|1.5
Mesosuchus|RIN|O|1
Rhynchosaurus|RIN|H|1
Tanystropheus|REP|P|6|@F
Dinocephalosaurus|REP|P|6|@A|pescoço longo; paria filhotes vivos
Drepanosaurus|REP|I|0.5||vive nas árvores, garra no dedo
Megalancosaurus|REP|I|0.3
Hypuronector|REP|I|0.12
Longisquama|REP|I|0.15
Kuehneosaurus|REP|I|0.7|@V|lagarto planador
Mecistotrachelos|REP|I|0.2|@V
Icarosaurus|REP|I|0.1|@V
Sharovipteryx|REP|I|0.3|@V
Procolophon|REP|H|0.35
Hypsognathus|REP|H|0.3
Clevosaurus|ESF|O|0.3
Megachirella|LAG|I|0.2
Diphydontosaurus|ESF|I|0.1
# Tartarugas
Eorhynchochelys|TAR|O|1.8
Proganochelys|TAR|H|1|@T
Palaeochersis|TAR|O|0.5
Proterochersis|TAR|O|0.5
Odontochelys|TAR|O|0.4
Pappochelys|TAR|O|0.2
# Pterossauros
Caelestiventus|PTE|C|1.5
Raeticodactylus|PTE|P|1.35
Caviramus|PTE|P|1.35
Austriadactylus|PTE|C|1.2
Eudimorphodon|PTE|P|1
Seazzadactylus|PTE|P|1
Carniadactylus|PTE|I|0.7
Peteinosaurus|PTE|I|0.6
Preondactylus|PTE|I|0.45
# Ictiossauros
Ichthyotitan|ICT|C|25||o maior animal marinho do Triássico
Shastasaurus|ICT|F|21||ictiossauro gigante sem dentes, suga a comida
Cymbospondylus|ICT|C|17
Shonisaurus|ICT|P|15
Guizhouichthyosaurus|ICT|C|10
Thalattoarchon|ICT|C|8.6
Besanosaurus|ICT|P|8
Californosaurus|ICT|P|3
Utatsusaurus|ICT|P|3
Phalarodon|ICT|P|3
Grippia|ICT|P|1
Mixosaurus|ICT|P|1
Chaohusaurus|ICT|P|1
Cartorhynchus|ICT|O|0.4|@F|anda na praia como uma foca
# Notossauros, placodontes e outros marinhos
Nothosaurus|SAP|P|7
Ceresiosaurus|SAP|P|4
Simosaurus|SAP|C|4
Yunguisaurus|SAP|P|4
Pistosaurus|SAP|P|3
Augustasaurus|SAP|P|3
Placodus|SAP|O|3||esmaga conchas
Psephoderma|SAP|O|1.8
Cyamodus|SAP|O|1.3
Paraplacodus|SAP|O|1.3
Lariosaurus|SAP|P|1
Henodus|SAP|F|1||placodonte que parece tartaruga
Placochelys|SAP|O|0.9
Pachypleurosaurus|SAP|P|0.4
Keichousaurus|SAP|P|0.3|@F
Neusticosaurus|SAP|P|0.3
Atopodentatus|REP|H|3|@A|boca de martelo; raspa algas
Helveticosaurus|REP|C|3.6|@A
Anshunsaurus|TAL|P|3
Askeptosaurus|TAL|P|2
Thalattosaurus|TAL|P|2
Xinpusaurus|TAL|P|2
Clarazia|TAL|P|1
Largocephalosaurus|REP|O|2|@A
Hupehsuchus|REP|P|1|@A
Nanchangosaurus|REP|P|1|@A
Eretmorhipis|REP|I|0.7|@A|parecido com ornitorrinco
# Dicinodontes, cinodontes e parentes dos mamíferos
Lisowicia|DIC|H|4.5||dicinodonte do tamanho de um elefante
Placerias|DIC|H|3.5
Ischigualastia|DIC|H|3.5
Stahleckeria|DIC|H|3
Jachaleria|DIC|H|3
Kannemeyeria|DIC|H|3
Dinodontosaurus|DIC|H|2.4
Lystrosaurus|DIC|H|2.5||sobreviveu à maior extinção da Terra
Sinokannemeyeria|DIC|H|2
Cynognathus|CIN|C|2
Diademodon|CIN|H|2
Exaeretodon|CIN|H|1.8
Moschorhinus|CIN|C|1.5
Trucidocynodon|CIN|C|1.2
Chiniquodon|CIN|C|1
Thrinaxodon|CIN|C|0.5||vive em tocas
Massetognathus|CIN|H|0.5
Euchambersia|CIN|C|0.5||mordida venenosa
Trirachodon|CIN|O|0.4
Probainognathus|CIN|I|0.15
Brasilodon|CIN|I|0.15||parente muito próximo dos mamíferos
# Anfíbios
Mastodonsaurus|ANF|C|6||anfíbio gigante com presas
Koskinonodon|ANF|C|3
Cyclotosaurus|ANF|C|3
Eryosuchus|ANF|C|3
Benthosuchus|ANF|C|2.5
Parotosuchus|ANF|C|2.5
Paracyclotosaurus|ANF|C|2.3
Metoposaurus|ANF|C|2
Trematosaurus|ANF|P|2|@A
Plagiosaurus|ANF|C|2
Wetlugasaurus|ANF|C|2
Aphaneramma|ANF|P|1.5|@A
Gerrothorax|ANF|C|1||cabeça larga, emboscada no fundo
Sclerothorax|ANF|C|1
Apachesaurus|ANF|C|0.6
Triadobatrachus|ANF|I|0.1||o avô dos sapos
# Peixes
Birgeria|PEI|C|2
Acrodus|TUB|O|2.5
Saurichthys|PEI|C|1.5||parece uma agulha com dentes
Chinlea|PEI|C|1.5
Ceratodus|PEI|O|1||peixe pulmonado
Bobasatrania|PEI|O|0.6
Colobodus|PEI|O|0.5
Whiteia|PEI|C|0.3
Lissodus|TUB|O|0.3
Ptycholepis|PEI|P|0.3
Perleidus|PEI|P|0.15
# Invertebrados
Gigatitan|INS|C|0.4||inseto parecido com louva-deus gigante que canta
Clatrotitan|INS|C|0.2
Encrinus|INV|F|0.5||lírio-do-mar
Ceratites|INV|C|0.1||amonite
"""

DATA["era_do_gelo"] = """
# Proboscídeos
Mamute-da-estepe (Mammuthus trogontherii)|PRB|H|4.5a
Palaeoloxodon namadicus|PRB|H|4.5a||talvez o maior mamífero terrestre de todos
Mamute-lanoso (Mammuthus primigenius)|PRB|H|4a
Mamute-columbiano (Mammuthus columbi)|PRB|H|4a
Elefante-de-presas-retas (Palaeoloxodon antiquus)|PRB|H|4a
Elefante-de-Recki (Palaeoloxodon recki)|PRB|H|4a
Deinotério (Deinotherium bozasi)|PRB|H|4a||presas curvadas para baixo
Stegodon|PRB|H|3.8a
Mastodonte-americano (Mammut americanum)|PRB|H|3a
Cuvieronius|PRB|H|2.8a
Notiomastodon|PRB|H|2.5a
Mamute-anão (Mammuthus exilis)|PRB|H|2a||das ilhas da Califórnia
Elefante-anão-da-Sicília (Palaeoloxodon falconeri)|PRB|H|1a||do tamanho de um porco
# Rinocerontes, cavalos e antas
Elasmotério (Elasmotherium)|UNG|H|4.5||o "unicórnio siberiano"
Rinoceronte-lanoso (Coelodonta)|UNG|H|3.8
Rinoceronte-de-Merck (Stephanorhinus kirchbergensis)|UNG|H|3.5
Rinoceronte-da-estepe (Stephanorhinus hemitoechus)|UNG|H|3.2
Megatapirus|UNG|H|3||anta gigante da China
Equus scotti|UNG|H|2.3
Cavalo-selvagem (Equus ferus)|UNG|H|2.2
Hidruntino (Equus hydruntinus)|UNG|H|2
Cavalo-de-Yukon (Equus lambei)|UNG|H|2
Haringtonhippus|UNG|H|2
Hippidion|UNG|H|2
Equus neogeus|UNG|H|2
Anta (Tapirus)|UNG|H|2
# Cervídeos, bovídeos e camelídeos
Megaloceros|UNG|H|2.1a
Cervalces latifrons|UNG|H|3||alce gigante de testa larga
Alce (Alces)|UNG|H|3
Sinomegaceros|UNG|H|2.5
Cervalces scotti|UNG|H|2.5
Cervo-vermelho (Cervus elaphus)|UNG|H|2.4
Rena (Rangifer)|UNG|H|2
Antifer|UNG|H|2
Navahoceros|UNG|H|2
Candiacervus|UNG|H|1||cervo anão de Creta
Bison latifrons|UNG|H|4.5||chifres de mais de 2 m
Bisão-da-estepe (Bison priscus)|UNG|H|3.5
Bison antiquus|UNG|H|3.5
Iaque-selvagem (Bos mutus)|UNG|H|3.3
Auroque (Bos primigenius)|UNG|H|3.2
Pelorovis|UNG|H|3
Megalotragus|UNG|H|3
Bootherium|UNG|H|2.5
Euceratherium|UNG|H|2.5
Boi-almiscarado (Ovibos)|UNG|H|2.3
Íbex (Capra ibex)|UNG|H|1.6
Spirocerus|UNG|H|1.5
Tetrameryx|UNG|H|1.5
Saiga|UNG|H|1.4
Antilocapra|UNG|H|1.4
Capromeryx|UNG|H|0.9
Myotragus|UNG|H|1||cabra anã das Baleares
Camelops|UNG|H|3.5
Hemiauchenia|UNG|H|2.5
Palaeolama|UNG|H|2
Guanaco (Lama guanicoe)|UNG|H|2
Sivatherium|UNG|H|3||girafa de pescoço curto com chifres em leque
# Porcos e hipopótamos
Hippopotamus gorgops|UNG|H|4.3|@F
Hipopótamo-europeu (Hippopotamus antiquus)|UNG|H|5|@F
Hipopótamo-de-Madagascar (Hippopotamus lemerlei)|UNG|H|2|@F
Hipopótamo-anão-de-Chipre (Hippopotamus minor)|UNG|H|1|@F
Javali (Sus scrofa)|UNG|O|1.8
Kolpochoerus|UNG|O|1.5
Metridiochoerus|UNG|O|1.5
Platygonus|UNG|O|1
Mylohyus|UNG|O|1
# Preguiças, tatus e gliptodontes
Megatério (Megatherium)|XEN|H|6
Eremotherium|XEN|H|6
Lestodon|XEN|H|4.6
Glossotherium|XEN|H|4
Mylodon|XEN|H|3
Paramylodon|XEN|H|3
Megalonyx|XEN|H|3
Nothrotheriops|XEN|H|2.7
Catonyx|XEN|H|2.5
Scelidotherium|XEN|H|2.5
Valgipes|XEN|H|2
Nothrotherium|XEN|H|1.5
Megalocnus|XEN|H|1.5||preguiça-gigante de Cuba
Doedicurus|XEN|H|4||cauda com clava cheia de espinhos
Gliptodonte (Glyptodon)|XEN|H|3.3
Panochthus|XEN|H|3
Neosclerocalyptus|XEN|H|2.5
Glyptotherium|XEN|H|2.5
Hoplophorus|XEN|H|2
Holmesina|XEN|O|2
Pampatherium|XEN|O|2
Eutatus|XEN|O|1.5
Propraopus|XEN|I|1
# Notoungulados e litopternas
Toxodon|UNG|H|2.7
Mixotoxodon|UNG|H|3
Macrauchenia|UNG|H|3||tromba curta, corre em zigue-zague
Xenorhinotherium|UNG|H|3
# Felinos
Tigre-de-Ngandong (Panthera tigris soloensis)|FEL|C|2.8
Leão-americano (Panthera atrox)|FEL|C|2.5
Leão-das-cavernas (Panthera spelaea)|FEL|C|2.1
Tigre-dentes-de-sabre (Smilodon populator)|FEL|C|2
Smilodon fatalis|FEL|C|1.75
Homotherium|FEL|C|2.2||dentes-de-cimitarra, corre longe
Panthera gombaszoegensis|FEL|C|2
Onça-gigante (Panthera onca augusta)|FEL|C|2
Dinofelis|FEL|C|2
Xenosmilus|FEL|C|1.8
Puma (Puma concolor)|FEL|C|1.6
Miracinonyx|FEL|C|1.6||o "guepardo americano"
Guepardo-gigante (Acinonyx pardinensis)|FEL|C|1.5
Megantereon|FEL|C|1.5
Lince-eurasiático (Lynx lynx)|FEL|C|1
# Canídeos, hienas e mustelídeos
Lobo-terrível (Aenocyon dirus)|CAN|C|1.7
Lobo-cinzento (Canis lupus)|CAN|C|1.6
Xenocyon|CAN|C|1.3
Protocyon|CAN|C|1.2
Cuon (Cuon alpinus)|CAN|C|1.1
Raposa-do-ártico (Vulpes lagopus)|CAN|C|0.7
Hiena-das-cavernas (Crocuta spelaea)|HIE|C|1.6
Hiena-gigante (Pachycrocuta)|HIE|C|1.6
Chasmaporthetes|HIE|C|1.2||hiena corredora
Glutão (Gulo gulo)|CAN|C|1
# Ursos
Arctotherium|URS|O|3.4||o maior urso que já existiu
Urso-de-cara-curta (Arctodus simus)|URS|C|3.4
Urso-das-cavernas (Ursus spelaeus)|URS|O|3
Urso-pardo (Ursus arctos)|URS|O|2.5
Urso-polar (Ursus maritimus)|URS|C|2.5|@F
Panda-gigante-antigo (Ailuropoda baconi)|URS|H|2
# Primatas
Gigantopithecus|PRI|H|3a||o maior primata de todos
Megaladapis|PRI|H|1.5||lêmure do tamanho de um gorila
Archaeoindris|PRI|H|1.5
Theropithecus oswaldi|PRI|H|1.5||babuíno gigante
Palaeopropithecus|PRI|H|1.3||lêmure-preguiça
Protopithecus|PRI|O|1
Caipora|PRI|O|1
# Roedores e pequenos mamíferos
Castor-gigante (Castoroides)|ROE|H|2.2
Capivara-gigante (Neochoerus)|ROE|H|2|@F
Castor-europeu (Castor fiber)|ROE|H|1|@F
Lebre-da-montanha (Lepus timidus)|ROE|H|0.6
Marmota|ROE|H|0.6
Pika (Ochotona)|ROE|H|0.2
Lemingue (Lemmus)|ROE|H|0.15
# Marsupiais e monotremados
Diprotodon|MAR|H|3.8||o maior marsupial de todos
Palorchestes|MAR|H|2.5
Zygomaturus|MAR|H|2.5
Procoptodon|MAR|H|2.7a||canguru gigante de cara curta
Phascolonus|MAR|H|1.9
Protemnodon|MAR|H|2
Sthenurus|MAR|H|2
Thylacoleo|MAR|C|1.5||leão-marsupial, a mordida mais forte
Propleopus|MAR|C|1.5||canguru carnívoro
Tilacino (Thylacinus)|MAR|C|1.3
Diabo-gigante (Sarcophilus laniarius)|MAR|C|1
Megalibgwilia|MAR|I|1||equidna gigante
Zaglossus hacketti|MAR|I|1
# Aves
Argentavis|AVV|C|7||na verdade é do Mioceno; fica como vazamento da Fenda
Aiolornis|AVV|C|5
Teratornis|AVV|C|3.8
Águia-de-Haast (Hieraaetus moorei)|AVV|C|3||caçava moas
Condor-andino (Vultur gryphus)|AVV|C|3
Condor-da-Califórnia (Gymnogyps)|AVV|C|3
Breagyps|AVV|C|3
Abutre-barbudo (Gypaetus)|AVV|C|2.8
Águia-real (Aquila chrysaetos)|AVV|C|2.2
Coruja-das-neves (Bubo scandiacus)|AVV|C|1.5
Corvo (Corvus corax)|AVV|O|1.2
Moa-gigante (Dinornis)|AVE|H|3.6a
Pássaro-elefante (Aepyornis)|AVE|H|3a
Vorombe|AVE|H|3a
Titanis|AVE|C|2.5a||ave-do-terror
Genyornis|AVE|H|2.1a
Pachyornis|AVE|H|1.8a
Emeus|AVE|H|1.8a
Sylviornis|AVE|O|1.7a
Euryapteryx|AVE|H|1.5a
Mullerornis|AVE|H|1.5a
Megalapteryx|AVE|H|1.3a
Anomalopteryx|AVE|H|1.3a
Ornimegalonyx|AVE|C|1.1a||coruja gigante de Cuba que corria
Dodô (Raphus)|AVE|H|1a
Cnemiornis|AVE|H|1a||ganso gigante da Nova Zelândia
Solitário-de-Rodrigues (Pezophaps)|AVE|H|0.9a
Tetraz-grande (Tetrao urogallus)|AVE|H|0.9
Arau-gigante (Pinguinus impennis)|AVE|P|0.85|@F
Psilopterus|AVE|C|0.8a||ave-do-terror pequena
Chendytes|AVE|P|0.8|@F|pato mergulhador que não voava
Lagópode (Lagopus)|AVE|H|0.4
# Répteis
Megalania (Varanus priscus)|LAG|C|7
Crocodylus thorbjarnarsoni|CRO|C|7
Wonambi|LAG|C|5||serpente constritora da Austrália
Voay|CRO|C|5
Dragão-de-komodo (Varanus komodoensis)|LAG|C|3
Quinkana|CRT|C|3
Meiolania|TAR|H|2.5|@T|tartaruga com chifres e cauda de clava
Mekosuchus|CRT|C|2
Hesperotestudo|TAR|H|1.5|@T
# Mamíferos marinhos e peixes
Baleia-da-Groenlândia (Balaena mysticetus)|MMA|F|18
Vaca-marinha-de-Steller (Hydrodamalis)|MMA|H|9
Orca (Orcinus orca)|MMA|C|9
Narval (Monodon)|MMA|C|5
Beluga (Delphinapterus)|MMA|C|5
Morsa (Odobenus)|MMA|C|3.5|@F
Leão-marinho-de-Steller (Eumetopias)|MMA|C|3.3|@F
Foca-anelada (Pusa hispida)|MMA|P|1.5|@F
Esturjão (Huso huso)|PEI|C|7
Tubarão-branco (Carcharodon carcharias)|TUB|C|6
Salmão-do-atlântico (Salmo salar)|PEI|C|1.5
Lúcio (Esox lucius)|PEI|C|1.5
"""

# Criaturas fora das 5 eras: aparecem em qualquer era como "vazamentos" da Fenda.
DATA["anomalias"] = """
Megalodon (Otodus megalodon)|TUB|C|20||Mioceno a Plioceno
Dunkleosteus|PEI|C|8||Devoniano, peixe blindado
"""
