"""The Pocket Guide (v1.1.2, docs/AJUDA.md): the in-game help book. Rodrigo asked for "um livrinho de ajuda" on
31/10/2026 and approved the topics and the Minecraft-book look the same day.

Writes assets/terrassic/pocket_guide.json (topic order, icon, recipes shown on a crafting grid), the advancement and
loot table that give every player one book on their first tick in a world, the recipe (book + flint), and returns
LANG for gen_resources.py. %key:<name>% in a text becomes the key the player has bound (client/PocketGuideScreen).
Keep every text short: the screen flows it over as many pages as it needs. A title must fit its index line: about
82 px of the default font, so 14 letters or so.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "common", "src", "main", "resources")
A = os.path.join(RES, "assets", "terrassic")
D = os.path.join(RES, "data", "terrassic")

# id, icon, recipes on the grid, {lang: (title, body)}; paragraphs separated by \n
TOPICS = [
    ("start", "terrassic:field_lens", ["pocket_guide"], {
        "pt_br": ("Começo",
                  "Os dinossauros vivem no mundo normal, no meio dos outros animais: mais ou menos um a cada quatro bichos, e os carnívoros são bem mais raros que os herbívoros. "
                  "Os grandes andam em bando, os voadores fazem colônias na costa e os répteis marinhos ficam no oceano.\n"
                  "Quase tudo começa com sílex, que sai do cascalho, e com junco, que cresce na beira de rios e pântanos.\n"
                  "O Velociraptor caça de noite: não ande sozinho no escuro no começo."),
        "en_us": ("Getting Started",
                  "Dinosaurs live in the normal world among the other animals: roughly one in every four, and the carnivores are much rarer than the herbivores. "
                  "The big ones roam in herds, the flyers nest in colonies on the coast and the sea reptiles keep to the ocean.\n"
                  "Almost everything starts with flint, from gravel, and rush, which grows along rivers and swamps.\n"
                  "The Velociraptor hunts at night: early on, do not walk alone in the dark."),
        "es_es": ("Primeros pasos",
                  "Los dinosaurios viven en el mundo normal, entre los demás animales: más o menos uno de cada cuatro, y los carnívoros son mucho más raros que los herbívoros. "
                  "Los grandes van en manada, los voladores anidan en colonias en la costa y los reptiles marinos viven en el océano.\n"
                  "Casi todo empieza con sílex, que sale de la grava, y con junco, que crece a orillas de ríos y pantanos.\n"
                  "El Velociraptor caza de noche: al principio, no camines solo a oscuras."),
    }),
    ("dinos", "terrassic:tyrannosaurus_spawn_egg", ["bestiary_carnivores", "bestiary_herbivores", "bestiary_flyers", "bestiary_marine"], {
        "pt_br": ("Os dinossauros",
                  "Cada espécie tem sua página num dos quatro Bestiários: Carnívoros, Herbívoros, Voadores e Marinhos. Em cada página: o que come, o tamanho real, como se doma e quanta comida a doma pede.\n"
                  "Faça os Bestiários com um livro e um pouco do assunto: carne, folhas, uma pena ou um peixe."),
        "en_us": ("The Dinosaurs",
                  "Every species has its page in one of the four Bestiaries: Carnivores, Herbivores, Flyers and Sea Reptiles. On each page: what it eats, its real size, how it is tamed and how much food taming takes.\n"
                  "Make the Bestiaries from a book and a bit of their subject: meat, leaves, a feather or a fish."),
        "es_es": ("Los dinosaurios",
                  "Cada especie tiene su página en uno de los cuatro Bestiarios: Carnívoros, Herbívoros, Voladores y Marinos. En cada página: qué come, su tamaño real, cómo se doma y cuánta comida pide la doma.\n"
                  "Haz los Bestiarios con un libro y un poco de su tema: carne, hojas, una pluma o un pez."),
    }),
    ("weapons", "terrassic:flint_spear", ["flint_spear", "bone_club", "hunting_bow", "flint_arrow"], {
        "pt_br": ("Armas",
                  "Lança: um toque rápido em %key:use% dá uma estocada que alcança uns 4 blocos; segure para arremessar.\n"
                  "Clava: atordoa. Golpe lento que enche o torpor do bicho e fere pouco, boa para o nocaute.\n"
                  "Arco de caça: puxada mais longa e tiro mais forte que o arco comum. Usa qualquer flecha.\n"
                  "Flecha de sílex: um pouco mais de dano que a flecha comum."),
        "en_us": ("Weapons",
                  "Spear: a quick tap of %key:use% thrusts about 4 blocks ahead; hold it to throw.\n"
                  "Club: it stuns. A slow blow that fills the animal's torpor and barely wounds, good for a knockout.\n"
                  "Hunting bow: a longer draw and a stronger shot than the plain bow. Takes any arrow.\n"
                  "Flint arrow: a little more damage than the plain arrow."),
        "es_es": ("Armas",
                  "Lanza: un toque rápido de %key:use% da una estocada de unos 4 bloques; mantén pulsado para lanzarla.\n"
                  "Garrote: aturde. Un golpe lento que llena el letargo del animal y hiere poco, bueno para noquear.\n"
                  "Arco de caza: tensado más largo y tiro más fuerte que el arco normal. Usa cualquier flecha.\n"
                  "Flecha de sílex: un poco más de daño que la flecha normal."),
    }),
    ("blowgun", "terrassic:blowgun", ["blowgun", "tranq_dart", "sleep_herb", "narcotic_arrow"], {
        "pt_br": ("Zarabatana",
                  "Segure %key:use% para levar o tubo à boca e encher o fôlego; solte para soprar. "
                  "Com o fôlego cheio, em um segundo, o dardo vai mais longe, mais reto e com mais narcótico.\n"
                  "Quando o narcótico entra, saem espirais violeta do bicho e você ouve um tic, mais agudo conforme ele fica tonto.\n"
                  "A flecha narcótica faz o mesmo no arco."),
        "en_us": ("Blowgun",
                  "Hold %key:use% to raise the tube to your lips and fill your lungs; let go to blow. "
                  "With a full breath, one second, the dart flies farther and straighter and carries more narcotic.\n"
                  "When the narcotic gets in, violet swirls rise from the animal and you hear a tick, higher as it grows drowsy.\n"
                  "The narcotic arrow does the same from a bow."),
        "es_es": ("Cerbatana",
                  "Mantén %key:use% para llevar el tubo a la boca y llenar los pulmones; suelta para soplar. "
                  "Con el aliento lleno, en un segundo, el dardo va más lejos, más recto y con más narcótico.\n"
                  "Cuando entra el narcótico salen espirales violetas del animal y oyes un tic, más agudo a medida que se adormece.\n"
                  "La flecha narcótica hace lo mismo con el arco."),
    }),
    ("bola", "terrassic:bola", ["bola", "bola_from_hide"], {
        "pt_br": ("Boleadeira",
                  "Segure %key:use% para girar e solte para lançar. Quanto mais girar, até um segundo, mais longe vai.\n"
                  "Derruba um voador no ar, que fica preso no chão por 8 segundos, e prende as pernas de um bicho por 6. "
                  "Os gigantes arrebentam a corda.\n"
                  "Derrube o Pteranodonte e use a zarabatana enquanto ele está preso."),
        "en_us": ("Bola",
                  "Hold %key:use% to swing it and let go to throw. The longer you swing, up to a second, the farther it flies.\n"
                  "It brings a flyer down from the air and holds it on the ground for 8 seconds, and ties an animal's legs for 6. "
                  "Giants snap the cord.\n"
                  "Bring a Pteranodon down and use the blowgun while it is tied."),
        "es_es": ("Boleadoras",
                  "Mantén %key:use% para hacerlas girar y suelta para lanzar. Cuanto más giren, hasta un segundo, más lejos llegan.\n"
                  "Derriban a un volador, que queda atrapado en el suelo 8 segundos, y atan las patas de un animal durante 6. "
                  "Los gigantes rompen la cuerda.\n"
                  "Derriba al Pteranodon y usa la cerbatana mientras está atado."),
    }),
    ("taming", "terrassic:raw_prime_meat", [], {
        "pt_br": ("Domesticação",
                  "Herbívoros e bichos pequenos: dê a comida da espécie na mão. Segure %key:use% em cima dele: cada porção enche a barra de doma, e cheia ele é seu.\n"
                  "Carnívoros: só filhotes, ovos ou por nocaute. Um carnívoro pequeno pede uma pilha de carne (64); os grandes, de duas a cinco pilhas.\n"
                  "Carne nobre vale por duas porções. Estudar a espécie no Caderno de Campo faz cada porção render um quarto a mais.\n"
                  "No nocaute ele dorme uns 20 segundos, mas não acorda enquanto come: tenha a comida toda na mão antes. Erva sonífera e dardos dão mais tempo.\n"
                  "A Lupa de Campo mostra o que ele come e quanto falta. Filhotes pedem um quarto da comida."),
        "en_us": ("Taming",
                  "Herbivores and small animals: hand-feed them their species' food. Hold %key:use% on it: every bite fills the taming bar, and once it is full it is yours.\n"
                  "Carnivores: only as babies, from eggs or by knockout. A small carnivore takes a stack of meat (64); the big ones two to five stacks.\n"
                  "Prime meat counts as two bites. Studying the species in the Field Notebook makes every bite count a quarter more.\n"
                  "Knocked out it sleeps for about 20 seconds, but it does not wake while it eats: have all the food at hand first. Sleep herb and darts add time.\n"
                  "The Field Lens shows what it eats and how much is left. Babies take a quarter of the food."),
        "es_es": ("Domesticación",
                  "Herbívoros y animales pequeños: dales de comer en la mano la comida de su especie. Mantén %key:use% sobre él: cada bocado llena la barra de doma, y llena es tuyo.\n"
                  "Carnívoros: solo crías, huevos o por noqueo. Un carnívoro pequeño pide una pila de carne (64); los grandes, de dos a cinco pilas.\n"
                  "La carne selecta vale por dos bocados. Estudiar la especie en el Cuaderno de Campo hace que cada bocado rinda un cuarto más.\n"
                  "Noqueado duerme unos 20 segundos, pero no despierta mientras come: ten toda la comida a mano antes. La hierba somnífera y los dardos dan más tiempo.\n"
                  "La Lupa de Campo muestra qué come y cuánto falta. Las crías piden un cuarto de la comida."),
    }),
    ("knockout", "terrassic:bone_club", [], {
        "pt_br": ("Nocaute",
                  "Para domar um bicho selvagem, encha o torpor dele até ele desmaiar: clava, soco, dardos e flechas narcóticas.\n"
                  "Desmaiado, clique nele com a comida da espécie até a barra encher. Carne nobre vale por duas.\n"
                  "Cada ferida enquanto ele dorme baixa a eficiência, e eficiência alta dá mais níveis. "
                  "Ele fica uns 20 segundos desacordado, mas não acorda enquanto você estiver dando comida. Se acordar antes, metade do progresso se perde: mais dardos ou erva sonífera o mantêm dormindo."),
        "en_us": ("Knockout",
                  "To tame a wild animal, fill its torpor until it passes out: club, fists, darts and narcotic arrows.\n"
                  "Once it is out, use its species' food on it until the bar is full. Prime meat counts twice.\n"
                  "Every wound while it sleeps lowers the effectiveness, and high effectiveness gives more levels. "
                  "It stays out for about 20 seconds, but it does not wake while you keep feeding it. If it wakes up first, half the progress is lost: more darts or sleep herb keep it asleep."),
        "es_es": ("Noqueo",
                  "Para domar a un animal salvaje, llena su letargo hasta que se desmaye: garrote, puños, dardos y flechas narcóticas.\n"
                  "Desmayado, usa en él la comida de su especie hasta llenar la barra. La carne selecta cuenta doble.\n"
                  "Cada herida mientras duerme baja la eficacia, y una eficacia alta da más niveles. "
                  "Queda inconsciente unos 20 segundos, pero no despierta mientras le sigas dando comida. Si despierta antes, se pierde la mitad del progreso: más dardos o hierba somnífera lo mantienen dormido."),
    }),
    ("eggs", "terrassic:triceratops_egg", [], {
        "pt_br": ("Ovos e filhotes",
                  "Um macho e uma fêmea domados procriam e põem um ovo. O ovo choca em três etapas, e o filhote marca como "
                  "dono o jogador que estiver mais perto.\n"
                  "Predadores só se domam filhotes ou por nocaute. Herbívoros também se domam com comida na mão."),
        "en_us": ("Eggs and Young",
                  "A tamed male and female breed and lay an egg. The egg hatches in three stages, and the hatchling takes the "
                  "nearest player as its owner.\n"
                  "Predators are tamed only as hatchlings or by knockout. Herbivores can also be tamed by hand-feeding."),
        "es_es": ("Huevos y crías",
                  "Un macho y una hembra domados crían y ponen un huevo. El huevo eclosiona en tres etapas, y la cría toma como "
                  "dueño al jugador más cercano.\n"
                  "Los depredadores solo se doman de crías o por noqueo. Los herbívoros también se doman dándoles de comer."),
    }),
    ("riding", "terrassic:tyrannosaurus_saddle", ["tyrannosaurus_saddle", "carnotaurus_saddle", "giganotosaurus_saddle", "pteranodon_saddle", "triceratops_saddle", "gallimimus_saddle", "parasaurolophus_saddle", "ankylosaurus_saddle", "mosasaurus_saddle", "velociraptor_harness"], {
        "pt_br": ("Montaria",
                  "Ponha a sela num dino montável adulto. O T. rex, o Carnotauro, o Giganotossauro, o Tricerátops, o Galimimo, o Parassaurolofo, o Anquilossauro, o Mossassauro, o Pteranodonte e o Velociraptor pedem a sela deles; "
                  "os outros usam a sela comum. Clique com a mão vazia para montar e use tesoura para tirar a sela.\n"
                  "%key:jump% pula (segure para pular mais alto) e %key:attack% ataca.\n"
                  "No Pteranodonte, %key:jump% decola e bate as asas, olhar dirige, e %key:sneak% no ar desce sem desmontar."),
        "en_us": ("Riding",
                  "Put a saddle on a grown rideable dinosaur. The T. rex, the Carnotaurus, the Giganotosaurus, the Triceratops, the Gallimimus, the Parasaurolophus, the Ankylosaurus, the Mosasaurus, the Pteranodon and the Velociraptor need their own; "
                  "the others take the plain saddle. Use it with an empty hand to mount, and shears take the saddle off.\n"
                  "%key:jump% jumps (hold it to jump higher) and %key:attack% attacks.\n"
                  "On the Pteranodon, %key:jump% takes off and flaps, your view steers, and %key:sneak% in the air descends without dismounting."),
        "es_es": ("Montura",
                  "Pon la silla a un dinosaurio montable adulto. El T. rex, el Carnotaurio, el Giganotosaurio, el Triceratops, el Gallimimus, el Parasaurolophus, el Ankylosaurus, el Mosasaurus, el Pteranodon y el Velociraptor necesitan la suya; "
                  "los demás usan la silla normal. Úsalo con la mano vacía para montar, y las tijeras quitan la silla.\n"
                  "%key:jump% salta (mantén para saltar más alto) y %key:attack% ataca.\n"
                  "En el Pteranodon, %key:jump% despega y bate las alas, la mirada dirige y %key:sneak% en el aire desciende sin desmontar."),
    }),
    ("orders", "terrassic:velociraptor_harness", [], {
        "pt_br": ("Ordens",
                  "Agache e use a mão vazia no seu dino para abrir a tela dele; montado, use %key:inventory%.\n"
                  "Seguir, Esperar, Vagar (anda perto de onde você mandou) e Pare (larga a briga por 10 segundos).\n"
                  "Apito: segure %key:whistle%, aponte com o mouse e solte. A ordem vale para todos os seus dinos a até 96 blocos. Agachado + %key:whistle% mostra onde estão todos, mesmo longe, e rastreia um com uma seta. "
                  "Atacar meu alvo manda todos atrás do bicho que você mira.\n"
                  "Modo: Passivo nunca ataca; Neutro defende você e a si, também de bichos de outros mods; Agressivo vai atrás de monstros e dinos selvagens por perto.\n"
                  "Seus dinos nunca atacam outros bichos seus."),
        "en_us": ("Orders",
                  "Sneak and use an empty hand on your dinosaur to open its screen; while riding, press %key:inventory%.\n"
                  "Follow, Wait, Wander (it roams near where you told it) and Stop (it drops the fight for 10 seconds).\n"
                  "Whistle: hold %key:whistle%, point with the mouse and let go. The order goes to all your dinosaurs within 96 blocks. Sneak + %key:whistle% shows where they all are, even far away, and tracks one with an arrow. "
                  "Attack my target sends them all after the creature you aim at.\n"
                  "Stance: Passive never attacks; Neutral defends you and itself, from other mods' creatures too; Aggressive goes after monsters and wild dinosaurs nearby.\n"
                  "Your dinosaurs never attack your other animals."),
        "es_es": ("Órdenes",
                  "Agáchate y usa la mano vacía en tu dinosaurio para abrir su pantalla; montado, pulsa %key:inventory%.\n"
                  "Seguir, Esperar, Deambular (anda cerca de donde lo dejaste) y Alto (deja la pelea durante 10 segundos).\n"
                  "Silbato: mantén %key:whistle%, apunta con el ratón y suelta. La orden vale para todos tus dinosaurios a 96 bloques. Agachado + %key:whistle% muestra dónde están todos, aunque estén lejos, y rastrea uno con una flecha. "
                  "Atacar mi objetivo los manda a todos a por la criatura que apuntas.\n"
                  "Modo: Pasivo nunca ataca; Neutral te defiende a ti y a sí mismo, también de criaturas de otros mods; Agresivo va a por monstruos y dinosaurios salvajes cercanos.\n"
                  "Tus dinosaurios nunca atacan a tus otros animales."),
    }),
    ("levels", "minecraft:experience_bottle", [], {
        "pt_br": ("Níveis",
                  "Cada dino nasce com um nível. Domado, ganha níveis extras pela eficiência da doma e continua subindo com "
                  "experiência: abates, viagens montado e carga levada.\n"
                  "Cada nível dá um ponto para gastar na tela do dino: Vida, Ataque, Velocidade ou Fome."),
        "en_us": ("Levels",
                  "Every dinosaur is born with a level. Tamed, it gains bonus levels from the taming effectiveness and keeps "
                  "rising with experience: kills, rides and cargo carried.\n"
                  "Each level gives a point to spend on its screen: Health, Attack, Speed or Hunger."),
        "es_es": ("Niveles",
                  "Cada dinosaurio nace con un nivel. Domado, gana niveles extra por la eficacia de la doma y sigue subiendo con "
                  "experiencia: presas, viajes montado y carga transportada.\n"
                  "Cada nivel da un punto para gastar en su pantalla: Vida, Ataque, Velocidad o Hambre."),
    }),
    ("hunger", "terrassic:raw_dino_meat", [], {
        "pt_br": ("Fome e sono",
                  "Todo dino sente fome. O domado com fome pede comida: dê a comida dele na mão, ou deixe comida na carga, "
                  "que ele come sozinho. Bem alimentado, ele se cura devagar.\n"
                  "Selvagens dormem de noite (o Velociraptor, de dia), e um predador de barriga cheia não caça."),
        "en_us": ("Hunger & Sleep",
                  "Every dinosaur gets hungry. A hungry tamed one begs: hand it its food, or leave food in its cargo and it eats "
                  "by itself. Well fed, it heals slowly.\n"
                  "Wild ones sleep at night (the Velociraptor by day), and a predator with a full belly does not hunt."),
        "es_es": ("Hambre y sueño",
                  "Todo dinosaurio tiene hambre. El domado hambriento pide comida: dásela en la mano, o deja comida en su carga "
                  "y comerá solo. Bien alimentado, se cura despacio.\n"
                  "Los salvajes duermen de noche (el Velociraptor, de día), y un depredador con la panza llena no caza."),
    }),
    ("cargo", "minecraft:chest", [], {
        "pt_br": ("Carga e ombro",
                  "Use um baú num dino de carga domado e ele passa a levar carga, recolhendo os itens do chão por perto. "
                  "Abra pela tela do dino, botão Carga.\n"
                  "Bichos pequenos sobem no seu ombro pelo botão Ombro; agache para soltá-los."),
        "en_us": ("Cargo, Shoulder",
                  "Use a chest on a tamed pack animal and it carries cargo, picking up the items lying nearby. "
                  "Open it from the dinosaur's screen, Cargo button.\n"
                  "Small animals ride on your shoulder with the Shoulder button; sneak to let them down."),
        "es_es": ("Carga y hombro",
                  "Usa un cofre en un animal de carga domado y llevará carga, recogiendo los objetos del suelo cercanos. "
                  "Ábrela desde la pantalla del dinosaurio, botón Carga.\n"
                  "Los animales pequeños suben a tu hombro con el botón Hombro; agáchate para bajarlos."),
    }),
    ("building", "terrassic:reed_thatch", ["reed_thatch"], {
        "pt_br": ("Construção",
                  "Só materiais da época: palha de junco, pau a pique, paliçada de troncos, pedra empilhada, couro, osso e as "
                  "madeiras pré-históricas. Nada de vidro, tijolo ou metal.\n"
                  "Os blocos ficam na aba de construção do Terrassic, e as receitas aparecem no livro de receitas."),
        "en_us": ("Building",
                  "Materials of the age only: rush thatch, wattle and daub, log palisades, stacked stone, hide, bone and the "
                  "prehistoric woods. No glass, brick or metal.\n"
                  "The blocks are in the Terrassic building tab, and their recipes show in the recipe book."),
        "es_es": ("Construcción",
                  "Solo materiales de la época: paja de junco, bahareque, empalizada de troncos, piedra apilada, cuero, hueso y las "
                  "maderas prehistóricas. Nada de vidrio, ladrillo ni metal.\n"
                  "Los bloques están en la pestaña de construcción de Terrassic, y sus recetas salen en el libro de recetas."),
    }),
    ("rules", "terrassic:sketch", [], {
        "pt_br": ("Regras",
                  "Quem cria o mundo, ou o administrador do servidor, ajusta as regras: quantidade de dinos, dano, velocidade "
                  "de domar, crescimento dos filhotes e outras.\n"
                  "Elas ficam na tela de criação do mundo e no arquivo de configuração do servidor, não dentro do jogo."),
        "en_us": ("World Rules",
                  "Whoever creates the world, or the server admin, sets the rules: how many dinosaurs, damage, taming speed, "
                  "hatchling growth and more.\n"
                  "They are on the world creation screen and in the server's config file, not inside the game."),
        "es_es": ("Reglas",
                  "Quien crea el mundo, o el administrador del servidor, ajusta las reglas: cantidad de dinosaurios, daño, "
                  "velocidad de doma, crecimiento de las crías y más.\n"
                  "Están en la pantalla de creación del mundo y en el archivo de configuración del servidor, no dentro del juego."),
    }),
]

# 1.7: topics followed by a list drawn by the screen (client/PocketGuideScreen): "species" = every active species
# with its egg, diet, size, how it is tamed and the food it takes (player feedback: "a section that shows all the dinos")
LISTS = {}

# 1.7.1 (Rodrigo, 05/11/2026: "vai ter muitos dinos... já já vai ficar com 300 páginas"): the species live in four
# Bestiaries instead of the Pocket Guide, by diet and habitat (client/PocketGuideScreen groups them: flyers and sea
# reptiles by their kind, the rest by diet; omnivores go with the herbivores). Each is made from a book and a bit of
# its subject. id, ingredients (any of), {lang: (item and book title, the line under it, the opening text)}
VOLUMES = [
    ("carnivores", [{"item": "terrassic:raw_dino_meat"}, {"item": "terrassic:raw_prime_meat"}, {"item": "terrassic:rex_tooth"}], {
        "pt_br": ("Bestiário: Carnívoros", "caçadores e comedores de peixe",
                  "Os caçadores de terra. Carnívoros adultos só se domam por nocaute; filhotes e ovos são o caminho mais fácil.\n"
                  "A doma pede pilhas de carne, e carne nobre vale por duas porções."),
        "en_us": ("Bestiary: Carnivores", "hunters and fish-eaters",
                  "The hunters of the land. Adult carnivores are tamed only by knockout; babies and eggs are the easy way.\n"
                  "Taming takes stacks of meat, and prime meat counts as two portions."),
        "es_es": ("Bestiario: Carnívoros", "cazadores y comedores de peces",
                  "Los cazadores de tierra. Los carnívoros adultos solo se doman por noqueo; las crías y los huevos son el camino fácil.\n"
                  "La doma pide pilas de carne, y la carne selecta vale por dos bocados."),
    }),
    ("herbivores", [{"item": "terrassic:cycad"}, {"tag": "minecraft:leaves"}], {
        "pt_br": ("Bestiário: Herbívoros", "e onívoros",
                  "Os que pastam e os que comem de tudo. A maioria se doma com a comida dela na mão; os grandes também por nocaute.\n"
                  "Muitos andam em bando e defendem o grupo."),
        "en_us": ("Bestiary: Herbivores", "and omnivores",
                  "The grazers and the ones that eat anything. Most are tamed with their food in your hand; the big ones also by knockout.\n"
                  "Many roam in herds and defend the group."),
        "es_es": ("Bestiario: Herbívoros", "y omnívoros",
                  "Los que pastan y los que comen de todo. La mayoría se doma con su comida en la mano; los grandes también por noqueo.\n"
                  "Muchos van en manada y defienden al grupo."),
    }),
    ("flyers", [{"item": "minecraft:feather"}], {
        "pt_br": ("Bestiário: Voadores", "pterossauros e aves",
                  "Os donos do céu. Fazem colônias na costa e nos penhascos.\n"
                  "A boleadeira derruba um voador no ar; preso no chão, ele pode ser domado."),
        "en_us": ("Bestiary: Flyers", "pterosaurs and birds",
                  "The masters of the sky. They nest in colonies on coasts and cliffs.\n"
                  "A bola brings a flyer down; held on the ground, it can be tamed."),
        "es_es": ("Bestiario: Voladores", "pterosaurios y aves",
                  "Los dueños del cielo. Anidan en colonias en la costa y los acantilados.\n"
                  "La boleadora derriba a un volador; sujeto en el suelo, se puede domar."),
    }),
    ("marine", [{"tag": "minecraft:fishes"}], {
        "pt_br": ("Bestiário: Marinhos", "répteis e peixes do mar",
                  "Os que vivem na água: répteis marinhos, tartarugas e os peixes do Cretáceo.\n"
                  "Ficam no oceano e nos rios; os grandes atacam quem nada perto."),
        "en_us": ("Bestiary: Sea Reptiles", "and Cretaceous fish",
                  "The ones living in the water: sea reptiles, turtles and the fish of the Cretaceous.\n"
                  "They keep to the ocean and the rivers; the big ones attack swimmers."),
        "es_es": ("Bestiario: Marinos", "reptiles y peces del mar",
                  "Los que viven en el agua: reptiles marinos, tortugas y los peces del Cretácico.\n"
                  "Viven en el océano y los ríos; los grandes atacan a quien nada cerca."),
    }),
]

# the species list's texts (client/PocketGuideScreen)
LIST_TEXT = {
    "pt_br": {"diet.carnivore": "Carnívoro", "diet.herbivore": "Herbívoro", "diet.omnivore": "Onívoro",
              "diet.piscivore": "Come peixe", "size": "%s m", "tame.egg": "Doma: filhote, ovo ou nocaute",
              "tame.feed": "Doma: na mão ou nocaute", "food": "Comida: %s porções", "food.stacks": "Comida: %s pilhas (%s)", "food.stack": "Comida: 1 pilha (64)", "rideable": "Montável",
              "count": "%s espécies", "count.one": "1 espécie"},
    "en_us": {"diet.carnivore": "Carnivore", "diet.herbivore": "Herbivore", "diet.omnivore": "Omnivore",
              "diet.piscivore": "Fish-eater", "size": "%s m", "tame.egg": "Tame: baby, egg or knockout",
              "tame.feed": "Tame: by hand or knockout", "food": "Food: %s bites", "food.stacks": "Food: %s stacks (%s)", "food.stack": "Food: 1 stack (64)", "rideable": "Rideable",
              "count": "%s species", "count.one": "1 species"},
    "es_es": {"diet.carnivore": "Carnívoro", "diet.herbivore": "Herbívoro", "diet.omnivore": "Omnívoro",
              "diet.piscivore": "Come peces", "size": "%s m", "tame.egg": "Doma: cría, huevo o noqueo",
              "tame.feed": "Doma: en la mano o noqueo", "food": "Comida: %s bocados", "food.stacks": "Comida: %s pilas (%s)", "food.stack": "Comida: 1 pila (64)", "rideable": "Montable",
              "count": "%s especies", "count.one": "1 especie"},
}

BOOK = {
    "pt_br": ("Guia de Bolso", "do Terrassic", "Guia de Bolso"),
    "en_us": ("Pocket Guide", "to Terrassic", "Pocket Guide"),
    "es_es": ("Guía de Bolsillo", "de Terrassic", "Guía de Bolsillo"),
}


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def build_lang():
    """The book's texts and the item name, merged into the lang files by gen_resources.py."""
    lang = {code: {} for code in BOOK}
    for code, (title, subtitle, item) in BOOK.items():
        lang[code]["guide.terrassic.pocket.title"] = title
        lang[code]["guide.terrassic.pocket.subtitle"] = subtitle
        lang[code]["item.terrassic.pocket_guide"] = item
    for vid, _, texts in VOLUMES:
        assert set(texts) == set(BOOK), vid
        for code, (title, subtitle, body) in texts.items():
            lang[code][f"item.terrassic.bestiary_{vid}"] = title
            lang[code][f"guide.terrassic.bestiary.{vid}.title"] = title.split(": ")[-1]
            lang[code][f"guide.terrassic.bestiary.{vid}.subtitle"] = subtitle
            lang[code][f"guide.terrassic.bestiary.{vid}.body"] = body
    for code, texts in LIST_TEXT.items():
        for key, text in texts.items():
            lang[code][f"guide.terrassic.pocket.list.{key}"] = text
    for tid, _, _, texts in TOPICS:
        assert set(texts) == set(BOOK), tid
        for code, (title, body) in texts.items():
            lang[code][f"guide.terrassic.pocket.{tid}.title"] = title
            lang[code][f"guide.terrassic.pocket.{tid}.body"] = body
    return lang


def main():
    """The book's files. Run by gen_resources.py after every recipe is written (it checks the ones it shows)."""
    recipes = os.path.join(D, "recipes")
    _write(os.path.join(recipes, "pocket_guide.json"), {
        "type": "minecraft:crafting_shapeless", "category": "misc",
        "ingredients": [{"item": "minecraft:book"}, {"item": "minecraft:flint"}],
        "result": {"item": "terrassic:pocket_guide"}})
    for vid, ingredient, _ in VOLUMES:
        _write(os.path.join(recipes, f"bestiary_{vid}.json"), {
            "type": "minecraft:crafting_shapeless", "category": "misc",
            "ingredients": [{"item": "minecraft:book"}, ingredient],
            "result": {"item": f"terrassic:bestiary_{vid}"}})
        _write(os.path.join(A, "models", "item", f"bestiary_{vid}.json"),
               {"parent": "item/generated", "textures": {"layer0": f"terrassic:item/bestiary_{vid}"}})
    for tid, icon, recs, _ in TOPICS:
        for r in recs:
            assert os.path.exists(os.path.join(recipes, f"{r}.json")), f"{tid}: no recipe {r}"
    _write(os.path.join(A, "pocket_guide.json"), {"topics": [
        dict({"id": tid, "icon": icon, "recipes": [f"terrassic:{r}" for r in recs]},
             **({"list": LISTS[tid]} if tid in LISTS else {})) for tid, icon, recs, _ in TOPICS]})
    _write(os.path.join(A, "models", "item", "pocket_guide.json"),
           {"parent": "item/generated", "textures": {"layer0": "terrassic:item/pocket_guide"}})
    # one book for every player, on the first tick they spend in a world (vanilla advancement rewards are once per player)
    _write(os.path.join(D, "advancements", "pocket_guide.json"), {
        "criteria": {"joined": {"trigger": "minecraft:tick"}},
        "rewards": {"loot": ["terrassic:gameplay/pocket_guide"]},
        "sends_telemetry_event": False})
    _write(os.path.join(D, "loot_tables", "gameplay", "pocket_guide.json"), {
        "type": "minecraft:advancement_reward",
        "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "terrassic:pocket_guide"}]}]})

if __name__ == "__main__":
    main()
