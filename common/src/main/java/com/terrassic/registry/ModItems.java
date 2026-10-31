package com.terrassic.registry;

import com.terrassic.Terrassic;
import com.terrassic.config.Eras;
import com.terrassic.config.Story;
import com.terrassic.item.ClubItem;
import com.terrassic.item.ExcavationToolItem;
import com.terrassic.item.FieldNotebookItem;
import com.terrassic.item.FlintHatchetItem;
import com.terrassic.item.FossilItem;
import com.terrassic.item.LoosePageItem;
import com.terrassic.item.ModTiers;
import com.terrassic.item.AmberLensItem;
import com.terrassic.item.BloodSampleItem;
import com.terrassic.item.ClayJarItem;
import com.terrassic.item.SketchCharcoalItem;
import com.terrassic.item.SketchItem;
import com.terrassic.item.SpearItem;
import com.terrassic.item.BlowgunItem;
import com.terrassic.research.GuideSpecies;
import dev.architectury.core.item.ArchitecturySpawnEggItem;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.level.block.Block;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Terrassic.MOD_ID, Registries.ITEM);

    /** Every spawn egg, in creative-tab order. */
    public static final List<RegistrySupplier<Item>> SPAWN_EGGS = new ArrayList<>();

    // ---- spawn eggs (each has its own sprite, so the tint colours are plain white)
    // BEGIN GENERATED spawn eggs (tools/javagen/gen_species.py)
    public static final RegistrySupplier<Item> TYRANNOSAURUS_SPAWN_EGG = egg("tyrannosaurus", ModEntities.TYRANNOSAURUS);
    public static final RegistrySupplier<Item> SPINOSAURUS_SPAWN_EGG = egg("spinosaurus", ModEntities.SPINOSAURUS);
    public static final RegistrySupplier<Item> DILOPHOSAURUS_SPAWN_EGG = egg("dilophosaurus", ModEntities.DILOPHOSAURUS);
    public static final RegistrySupplier<Item> VELOCIRAPTOR_SPAWN_EGG = egg("velociraptor", ModEntities.VELOCIRAPTOR);
    public static final RegistrySupplier<Item> COMPSOGNATHUS_SPAWN_EGG = egg("compsognathus", ModEntities.COMPSOGNATHUS);
    public static final RegistrySupplier<Item> TRICERATOPS_SPAWN_EGG = egg("triceratops", ModEntities.TRICERATOPS);
    public static final RegistrySupplier<Item> STYRACOSAURUS_SPAWN_EGG = egg("styracosaurus", ModEntities.STYRACOSAURUS);
    public static final RegistrySupplier<Item> PACHYRHINOSAURUS_SPAWN_EGG = egg("pachyrhinosaurus", ModEntities.PACHYRHINOSAURUS);
    public static final RegistrySupplier<Item> PROTOCERATOPS_SPAWN_EGG = egg("protoceratops", ModEntities.PROTOCERATOPS);
    public static final RegistrySupplier<Item> LEPTOCERATOPS_SPAWN_EGG = egg("leptoceratops", ModEntities.LEPTOCERATOPS);
    public static final RegistrySupplier<Item> STEGOSAURUS_SPAWN_EGG = egg("stegosaurus", ModEntities.STEGOSAURUS);
    public static final RegistrySupplier<Item> ANKYLOSAURUS_SPAWN_EGG = egg("ankylosaurus", ModEntities.ANKYLOSAURUS);
    public static final RegistrySupplier<Item> EUOPLOCEPHALUS_SPAWN_EGG = egg("euoplocephalus", ModEntities.EUOPLOCEPHALUS);
    public static final RegistrySupplier<Item> THERIZINOSAURUS_SPAWN_EGG = egg("therizinosaurus", ModEntities.THERIZINOSAURUS);
    public static final RegistrySupplier<Item> DEINOCHEIRUS_SPAWN_EGG = egg("deinocheirus", ModEntities.DEINOCHEIRUS);
    public static final RegistrySupplier<Item> BRACHIOSAURUS_SPAWN_EGG = egg("brachiosaurus", ModEntities.BRACHIOSAURUS);
    public static final RegistrySupplier<Item> ALAMOSAURUS_SPAWN_EGG = egg("alamosaurus", ModEntities.ALAMOSAURUS);
    public static final RegistrySupplier<Item> SALTASAURUS_SPAWN_EGG = egg("saltasaurus", ModEntities.SALTASAURUS);
    public static final RegistrySupplier<Item> ARGENTINOSAURUS_SPAWN_EGG = egg("argentinosaurus", ModEntities.ARGENTINOSAURUS);
    public static final RegistrySupplier<Item> OPISTHOCOELICAUDIA_SPAWN_EGG = egg("opisthocoelicaudia", ModEntities.OPISTHOCOELICAUDIA);
    public static final RegistrySupplier<Item> DREADNOUGHTUS_SPAWN_EGG = egg("dreadnoughtus", ModEntities.DREADNOUGHTUS);
    public static final RegistrySupplier<Item> GIGANOTOSAURUS_SPAWN_EGG = egg("giganotosaurus", ModEntities.GIGANOTOSAURUS);
    public static final RegistrySupplier<Item> CARCHARODONTOSAURUS_SPAWN_EGG = egg("carcharodontosaurus", ModEntities.CARCHARODONTOSAURUS);
    public static final RegistrySupplier<Item> CARNOTAURUS_SPAWN_EGG = egg("carnotaurus", ModEntities.CARNOTAURUS);
    public static final RegistrySupplier<Item> TARBOSAURUS_SPAWN_EGG = egg("tarbosaurus", ModEntities.TARBOSAURUS);
    public static final RegistrySupplier<Item> DASPLETOSAURUS_SPAWN_EGG = egg("daspletosaurus", ModEntities.DASPLETOSAURUS);
    public static final RegistrySupplier<Item> ALBERTOSAURUS_SPAWN_EGG = egg("albertosaurus", ModEntities.ALBERTOSAURUS);
    public static final RegistrySupplier<Item> MAJUNGASAURUS_SPAWN_EGG = egg("majungasaurus", ModEntities.MAJUNGASAURUS);
    public static final RegistrySupplier<Item> DAKOTARAPTOR_SPAWN_EGG = egg("dakotaraptor", ModEntities.DAKOTARAPTOR);
    public static final RegistrySupplier<Item> TROODON_SPAWN_EGG = egg("troodon", ModEntities.TROODON);
    public static final RegistrySupplier<Item> OVIRAPTOR_SPAWN_EGG = egg("oviraptor", ModEntities.OVIRAPTOR);
    public static final RegistrySupplier<Item> CITIPATI_SPAWN_EGG = egg("citipati", ModEntities.CITIPATI);
    public static final RegistrySupplier<Item> MONONYKUS_SPAWN_EGG = egg("mononykus", ModEntities.MONONYKUS);
    public static final RegistrySupplier<Item> DIDELPHODON_SPAWN_EGG = egg("didelphodon", ModEntities.DIDELPHODON);
    public static final RegistrySupplier<Item> MESODMA_SPAWN_EGG = egg("mesodma", ModEntities.MESODMA);
    public static final RegistrySupplier<Item> BASILEMYS_SPAWN_EGG = egg("basilemys", ModEntities.BASILEMYS);
    public static final RegistrySupplier<Item> ENCHODUS_SPAWN_EGG = egg("enchodus", ModEntities.ENCHODUS);
    public static final RegistrySupplier<Item> LEPISOSTEUS_SPAWN_EGG = egg("lepisosteus", ModEntities.LEPISOSTEUS);
    public static final RegistrySupplier<Item> PARASAUROLOPHUS_SPAWN_EGG = egg("parasaurolophus", ModEntities.PARASAUROLOPHUS);
    public static final RegistrySupplier<Item> PACHYCEPHALOSAURUS_SPAWN_EGG = egg("pachycephalosaurus", ModEntities.PACHYCEPHALOSAURUS);
    public static final RegistrySupplier<Item> THESCELOSAURUS_SPAWN_EGG = egg("thescelosaurus", ModEntities.THESCELOSAURUS);
    public static final RegistrySupplier<Item> GALLIMIMUS_SPAWN_EGG = egg("gallimimus", ModEntities.GALLIMIMUS);
    public static final RegistrySupplier<Item> STRUTHIOMIMUS_SPAWN_EGG = egg("struthiomimus", ModEntities.STRUTHIOMIMUS);
    public static final RegistrySupplier<Item> MAIASAURA_SPAWN_EGG = egg("maiasaura", ModEntities.MAIASAURA);
    public static final RegistrySupplier<Item> EDMONTOSAURUS_SPAWN_EGG = egg("edmontosaurus", ModEntities.EDMONTOSAURUS);
    public static final RegistrySupplier<Item> CORYTHOSAURUS_SPAWN_EGG = egg("corythosaurus", ModEntities.CORYTHOSAURUS);
    public static final RegistrySupplier<Item> PTERANODON_SPAWN_EGG = egg("pteranodon", ModEntities.PTERANODON);
    public static final RegistrySupplier<Item> QUETZALCOATLUS_SPAWN_EGG = egg("quetzalcoatlus", ModEntities.QUETZALCOATLUS);
    public static final RegistrySupplier<Item> HATZEGOPTERYX_SPAWN_EGG = egg("hatzegopteryx", ModEntities.HATZEGOPTERYX);
    public static final RegistrySupplier<Item> ICHTHYORNIS_SPAWN_EGG = egg("ichthyornis", ModEntities.ICHTHYORNIS);
    public static final RegistrySupplier<Item> VEGAVIS_SPAWN_EGG = egg("vegavis", ModEntities.VEGAVIS);
    public static final RegistrySupplier<Item> MOSASAURUS_SPAWN_EGG = egg("mosasaurus", ModEntities.MOSASAURUS);
    public static final RegistrySupplier<Item> TYLOSAURUS_SPAWN_EGG = egg("tylosaurus", ModEntities.TYLOSAURUS);
    public static final RegistrySupplier<Item> ELASMOSAURUS_SPAWN_EGG = egg("elasmosaurus", ModEntities.ELASMOSAURUS);
    public static final RegistrySupplier<Item> XIPHACTINUS_SPAWN_EGG = egg("xiphactinus", ModEntities.XIPHACTINUS);
    public static final RegistrySupplier<Item> ARCHELON_SPAWN_EGG = egg("archelon", ModEntities.ARCHELON);
    public static final RegistrySupplier<Item> HESPERORNIS_SPAWN_EGG = egg("hesperornis", ModEntities.HESPERORNIS);
    public static final RegistrySupplier<Item> DEINOSUCHUS_SPAWN_EGG = egg("deinosuchus", ModEntities.DEINOSUCHUS);
    public static final RegistrySupplier<Item> BAURUSUCHUS_SPAWN_EGG = egg("baurusuchus", ModEntities.BAURUSUCHUS);
    // END GENERATED spawn eggs

    // ---- hides: one per species, dropped by the animal (1-3, more with Looting); raw material for hide blocks
    // BEGIN GENERATED hides (tools/javagen/gen_species.py)
    public static final RegistrySupplier<Item> TYRANNOSAURUS_HIDE = hide("tyrannosaurus");
    public static final RegistrySupplier<Item> SPINOSAURUS_HIDE = hide("spinosaurus");
    public static final RegistrySupplier<Item> DILOPHOSAURUS_HIDE = hide("dilophosaurus");
    public static final RegistrySupplier<Item> VELOCIRAPTOR_HIDE = hide("velociraptor");
    public static final RegistrySupplier<Item> COMPSOGNATHUS_HIDE = hide("compsognathus");
    public static final RegistrySupplier<Item> TRICERATOPS_HIDE = hide("triceratops");
    public static final RegistrySupplier<Item> STYRACOSAURUS_HIDE = hide("styracosaurus");
    public static final RegistrySupplier<Item> PACHYRHINOSAURUS_HIDE = hide("pachyrhinosaurus");
    public static final RegistrySupplier<Item> PROTOCERATOPS_HIDE = hide("protoceratops");
    public static final RegistrySupplier<Item> LEPTOCERATOPS_HIDE = hide("leptoceratops");
    public static final RegistrySupplier<Item> STEGOSAURUS_HIDE = hide("stegosaurus");
    public static final RegistrySupplier<Item> ANKYLOSAURUS_HIDE = hide("ankylosaurus");
    public static final RegistrySupplier<Item> EUOPLOCEPHALUS_HIDE = hide("euoplocephalus");
    public static final RegistrySupplier<Item> THERIZINOSAURUS_HIDE = hide("therizinosaurus");
    public static final RegistrySupplier<Item> DEINOCHEIRUS_HIDE = hide("deinocheirus");
    public static final RegistrySupplier<Item> BRACHIOSAURUS_HIDE = hide("brachiosaurus");
    public static final RegistrySupplier<Item> ALAMOSAURUS_HIDE = hide("alamosaurus");
    public static final RegistrySupplier<Item> SALTASAURUS_HIDE = hide("saltasaurus");
    public static final RegistrySupplier<Item> ARGENTINOSAURUS_HIDE = hide("argentinosaurus");
    public static final RegistrySupplier<Item> OPISTHOCOELICAUDIA_HIDE = hide("opisthocoelicaudia");
    public static final RegistrySupplier<Item> DREADNOUGHTUS_HIDE = hide("dreadnoughtus");
    public static final RegistrySupplier<Item> GIGANOTOSAURUS_HIDE = hide("giganotosaurus");
    public static final RegistrySupplier<Item> CARCHARODONTOSAURUS_HIDE = hide("carcharodontosaurus");
    public static final RegistrySupplier<Item> CARNOTAURUS_HIDE = hide("carnotaurus");
    public static final RegistrySupplier<Item> TARBOSAURUS_HIDE = hide("tarbosaurus");
    public static final RegistrySupplier<Item> DASPLETOSAURUS_HIDE = hide("daspletosaurus");
    public static final RegistrySupplier<Item> ALBERTOSAURUS_HIDE = hide("albertosaurus");
    public static final RegistrySupplier<Item> MAJUNGASAURUS_HIDE = hide("majungasaurus");
    public static final RegistrySupplier<Item> DAKOTARAPTOR_HIDE = hide("dakotaraptor");
    public static final RegistrySupplier<Item> TROODON_HIDE = hide("troodon");
    public static final RegistrySupplier<Item> OVIRAPTOR_HIDE = hide("oviraptor");
    public static final RegistrySupplier<Item> CITIPATI_HIDE = hide("citipati");
    public static final RegistrySupplier<Item> MONONYKUS_HIDE = hide("mononykus");
    public static final RegistrySupplier<Item> DIDELPHODON_HIDE = hide("didelphodon");
    public static final RegistrySupplier<Item> MESODMA_HIDE = hide("mesodma");
    public static final RegistrySupplier<Item> BASILEMYS_HIDE = hide("basilemys");
    public static final RegistrySupplier<Item> ENCHODUS_HIDE = hide("enchodus");
    public static final RegistrySupplier<Item> LEPISOSTEUS_HIDE = hide("lepisosteus");
    public static final RegistrySupplier<Item> PARASAUROLOPHUS_HIDE = hide("parasaurolophus");
    public static final RegistrySupplier<Item> PACHYCEPHALOSAURUS_HIDE = hide("pachycephalosaurus");
    public static final RegistrySupplier<Item> THESCELOSAURUS_HIDE = hide("thescelosaurus");
    public static final RegistrySupplier<Item> GALLIMIMUS_HIDE = hide("gallimimus");
    public static final RegistrySupplier<Item> STRUTHIOMIMUS_HIDE = hide("struthiomimus");
    public static final RegistrySupplier<Item> MAIASAURA_HIDE = hide("maiasaura");
    public static final RegistrySupplier<Item> EDMONTOSAURUS_HIDE = hide("edmontosaurus");
    public static final RegistrySupplier<Item> CORYTHOSAURUS_HIDE = hide("corythosaurus");
    public static final RegistrySupplier<Item> PTERANODON_HIDE = hide("pteranodon");
    public static final RegistrySupplier<Item> QUETZALCOATLUS_HIDE = hide("quetzalcoatlus");
    public static final RegistrySupplier<Item> HATZEGOPTERYX_HIDE = hide("hatzegopteryx");
    public static final RegistrySupplier<Item> ICHTHYORNIS_HIDE = hide("ichthyornis");
    public static final RegistrySupplier<Item> VEGAVIS_HIDE = hide("vegavis");
    public static final RegistrySupplier<Item> MOSASAURUS_HIDE = hide("mosasaurus");
    public static final RegistrySupplier<Item> TYLOSAURUS_HIDE = hide("tylosaurus");
    public static final RegistrySupplier<Item> ELASMOSAURUS_HIDE = hide("elasmosaurus");
    public static final RegistrySupplier<Item> XIPHACTINUS_HIDE = hide("xiphactinus");
    public static final RegistrySupplier<Item> ARCHELON_HIDE = hide("archelon");
    public static final RegistrySupplier<Item> HESPERORNIS_HIDE = hide("hesperornis");
    public static final RegistrySupplier<Item> DEINOSUCHUS_HIDE = hide("deinosuchus");
    public static final RegistrySupplier<Item> BAURUSUCHUS_HIDE = hide("baurusuchus");
    // END GENERATED hides

    // ---- materials dropped by dinosaurs
    public static final RegistrySupplier<Item> REX_TOOTH = ITEMS.register("rex_tooth",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> MOSASAURUS_TOOTH = ITEMS.register("mosasaurus_tooth",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> TRICERATOPS_HORN = ITEMS.register("triceratops_horn",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> ANKYLOSAURUS_CLUB = ITEMS.register("ankylosaurus_club",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));

    // ---- Cretaceous food (docs/FAUNA.md): what the animals drop instead of vanilla beef, mutton and chicken.
    // Dino meat cooks like beef; prime cuts come from the big species and, cooked, heal a little.
    public static final RegistrySupplier<Item> RAW_DINO_MEAT = ITEMS.register("raw_dino_meat",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(3).saturationMod(0.3F).meat().build())));
    public static final RegistrySupplier<Item> COOKED_DINO_MEAT = ITEMS.register("cooked_dino_meat",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(8).saturationMod(0.8F).meat().build())));
    public static final RegistrySupplier<Item> RAW_PRIME_MEAT = ITEMS.register("raw_prime_meat",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(4).saturationMod(0.3F).meat().build())));
    public static final RegistrySupplier<Item> COOKED_PRIME_MEAT = ITEMS.register("cooked_prime_meat",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(10).saturationMod(0.9F).meat()
                            .effect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0), 1.0F).build())));
    // The fish of the Cretaceous waters: Enchodus in the sea (the cod's seat; raw and cooked like cod).
    public static final RegistrySupplier<Item> ENCHODUS = ITEMS.register("enchodus",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(2).saturationMod(0.1F).build())));
    public static final RegistrySupplier<Item> COOKED_ENCHODUS = ITEMS.register("cooked_enchodus",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(5).saturationMod(0.6F).build())));
    // Lepisosteus, the gar, in the rivers (the salmon's seat; raw and cooked like salmon).
    public static final RegistrySupplier<Item> LEPISOSTEUS = ITEMS.register("lepisosteus",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(2).saturationMod(0.1F).build())));
    public static final RegistrySupplier<Item> COOKED_LEPISOSTEUS = ITEMS.register("cooked_lepisosteus",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)
                    .food(new FoodProperties.Builder().nutrition(6).saturationMod(0.8F).build())));

    // ---- archaic weapons
    public static final RegistrySupplier<Item> FLINT_KNIFE = ITEMS.register("flint_knife",
            () -> new SwordItem(ModTiers.FLINT, 2, -1.4F, new Item.Properties().arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> FLINT_HATCHET = ITEMS.register("flint_hatchet",
            () -> new FlintHatchetItem(ModTiers.FLINT, 5.0F, -3.1F, new Item.Properties().arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> BONE_CLUB = ITEMS.register("bone_club",
            () -> new ClubItem(ModTiers.BONE, 5, -3.2F, 0.6F, new Item.Properties().arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> FLINT_SPEAR = ITEMS.register("flint_spear",
            () -> new SpearItem(6.0F, -2.8F, 7.0F, new Item.Properties().durability(180).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> HORN_SPEAR = ITEMS.register("horn_spear",
            () -> new SpearItem(8.0F, -2.9F, 10.0F, new Item.Properties().durability(520).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> REX_TOOTH_DAGGER = ITEMS.register("rex_tooth_dagger",
            () -> new SwordItem(ModTiers.REX_TOOTH, 3, -1.8F, new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> TAIL_CLUB = ITEMS.register("tail_club",
            () -> new ClubItem(ModTiers.ANKYLO_CLUB, 6, -3.4F, 1.2F, new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    // knockout taming (docs/DOMESTICACAO.md): the reed blowgun, its narcotic darts and the sleep herb
    public static final RegistrySupplier<Item> BLOWGUN = ITEMS.register("blowgun",
            () -> new BlowgunItem(new Item.Properties().durability(96).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> TRANQ_DART = ITEMS.register("tranq_dart",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> SLEEP_HERB = ITEMS.register("sleep_herb",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)));

    // ---- riding gear: the platform saddle of the titans (docs/CARGA.md): four aboard, anyone may climb on
    public static final RegistrySupplier<Item> PLATFORM_SADDLE = ITEMS.register("platform_saddle",
            () -> new Item(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    /** The Field Lens: look at a dinosaur through it for its card, taming state included (item/FieldLensItem). */
    public static final RegistrySupplier<Item> FIELD_LENS = ITEMS.register("field_lens",
            () -> new com.terrassic.item.FieldLensItem(new Item.Properties().stacksTo(1).arch$tab(ModTabs.MAIN)));
    /** The T. rex's own saddle (only it saddles a T. rex), with saddlebags: a saddled T. rex carries its cargo. */
    public static final RegistrySupplier<Item> TYRANNOSAURUS_SADDLE = ITEMS.register("tyrannosaurus_saddle",
            () -> new Item(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    /** The Pteranodon's own saddle (only it saddles a Pteranodon), with saddlebags like the T. rex's. */
    public static final RegistrySupplier<Item> PTERANODON_SADDLE = ITEMS.register("pteranodon_saddle",
            () -> new Item(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    /** The Velociraptor's hunting harness: its "saddle" for the armour it gives; it can never be ridden. */
    public static final RegistrySupplier<Item> VELOCIRAPTOR_HARNESS = ITEMS.register("velociraptor_harness",
            () -> new Item(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));

    // ---- science: notebook, field tools, fossils (docs/HISTORIA.md, section 4)
    public static final RegistrySupplier<Item> FIELD_NOTEBOOK = ITEMS.register("field_notebook",
            () -> new FieldNotebookItem(new Item.Properties().stacksTo(1).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> LOOSE_PAGE = ITEMS.register("loose_page",
            () -> new LoosePageItem(story(new Item.Properties().rarity(Rarity.UNCOMMON), ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> HAIR_BRUSH = ITEMS.register("hair_brush",
            () -> new ExcavationToolItem(60, 0.0F, new Item.Properties().durability(48).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> FLINT_CHISEL = ITEMS.register("flint_chisel",
            () -> new ExcavationToolItem(20, 0.35F, new Item.Properties().durability(32).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> AMBER_LENS = ITEMS.register("amber_lens",
            () -> new AmberLensItem(new Item.Properties().stacksTo(1).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> CLAY_JAR = ITEMS.register("clay_jar",
            () -> new ClayJarItem(new Item.Properties().stacksTo(16).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> RESIN_JAR = ITEMS.register("resin_jar",
            () -> new Item(new Item.Properties().stacksTo(16).craftRemainder(CLAY_JAR.get()).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> BLOOD_SAMPLE = ITEMS.register("blood_sample",
            () -> new BloodSampleItem(new Item.Properties().stacksTo(16)));
    public static final RegistrySupplier<Item> RAW_AMBER = ITEMS.register("raw_amber",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> SKETCHING_CHARCOAL = ITEMS.register("sketching_charcoal",
            () -> new SketchCharcoalItem(new Item.Properties().durability(16).arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> SKETCH = ITEMS.register("sketch",
            () -> new SketchItem(new Item.Properties().stacksTo(16)));
    public static final RegistrySupplier<Item> FOSSIL_ROCK = ITEMS.register("fossil_rock",
            () -> new BlockItem(ModBlocks.FOSSIL_ROCK.get(), new Item.Properties().arch$tab(ModTabs.SCIENCE)));
    public static final RegistrySupplier<Item> RESEARCH_TABLE = ITEMS.register("research_table",
            () -> new BlockItem(ModBlocks.RESEARCH_TABLE.get(), new Item.Properties().arch$tab(ModTabs.SCIENCE)));

    /** species id -> fossil ("&lt;species&gt;_fossil"), in Field Guide order. */
    public static final Map<String, RegistrySupplier<Item>> FOSSILS = new LinkedHashMap<>();

    static {
        for (GuideSpecies species : GuideSpecies.ALL) {
            String id = species.id();
            FOSSILS.put(id, ITEMS.register(id + "_fossil",
                    () -> new FossilItem(id, listed(new Item.Properties(), id, ModTabs.SCIENCE))));
        }
    }

    // ---- dinosaur egg block items
    static {
        for (Map.Entry<String, RegistrySupplier<Block>> e : ModBlocks.EGGS.entrySet()) {
            RegistrySupplier<Block> block = e.getValue();
            ITEMS.register(e.getKey() + "_egg", () -> new BlockItem(block.get(), listed(new Item.Properties().stacksTo(16), e.getKey(), ModTabs.MAIN)));
        }
    }

    // ---- primitive building block items (own creative tab)
    static {
        java.util.Set<String> onWater = java.util.Set.of(BuildingBlocks.ON_WATER);
        Map<String, String> wallTorches = new java.util.HashMap<>();  // torch -> wall torch
        for (String[] pair : BuildingBlocks.WALL_TORCHES) {
            wallTorches.put(pair[0], pair[1]);
        }
        for (Map.Entry<String, RegistrySupplier<Block>> e : ModBlocks.BUILDING.entrySet()) {
            RegistrySupplier<Block> block = e.getValue();
            if (wallTorches.containsValue(e.getKey())) {
                continue;  // placed by the torch's item
            }
            if (wallTorches.containsKey(e.getKey())) {
                RegistrySupplier<Block> wall = ModBlocks.BUILDING.get(wallTorches.get(e.getKey()));
                ITEMS.register(e.getKey(), () -> new net.minecraft.world.item.StandingAndWallBlockItem(block.get(),
                        wall.get(), listed(new Item.Properties(), e.getKey(), ModTabs.BUILDING), net.minecraft.core.Direction.DOWN));
            } else if (onWater.contains(e.getKey())) {
                ITEMS.register(e.getKey(), () -> new net.minecraft.world.item.PlaceOnWaterBlockItem(block.get(),
                        listed(new Item.Properties(), e.getKey(), ModTabs.BUILDING)));
            } else {
                ITEMS.register(e.getKey(), () -> new BlockItem(block.get(), listed(new Item.Properties(), e.getKey(), ModTabs.BUILDING)));
            }
        }
    }

    private ModItems() {
    }

    /**
     * A random fossil of a species of the active eras (config/Eras), weighted by how common each species' fossils are
     * (GuideSpecies.fossilWeight).
     */
    public static Item randomFossil(RandomSource random) {
        int total = 0;
        for (GuideSpecies s : GuideSpecies.ALL) {
            total += Eras.active(s) ? s.fossilWeight() : 0;
        }
        int roll = random.nextInt(total);
        for (GuideSpecies s : GuideSpecies.ALL) {
            roll -= Eras.active(s) ? s.fossilWeight() : 0;
            if (roll < 0) {
                return FOSSILS.get(s.id()).get();
            }
        }
        return FOSSILS.values().iterator().next().get();
    }

    private static RegistrySupplier<Item> hide(String species) {
        return ITEMS.register(species + "_hide", () -> new Item(listed(new Item.Properties(), species, ModTabs.MAIN)));
    }

    /**
     * Puts the item in its creative tab, unless it is named after a species of an era that is switched off
     * (config/Eras): such items stay registered, so saved worlds keep them, but are not listed.
     */
    public static Item.Properties listed(Item.Properties props, String id, RegistrySupplier<CreativeModeTab> tab) {
        return Eras.activeName(id) ? props.arch$tab(tab) : props;
    }

    /** Puts a story item (config/Story) in its creative tab only while the story mode is on. */
    public static Item.Properties story(Item.Properties props, RegistrySupplier<CreativeModeTab> tab) {
        return Story.enabled() ? props.arch$tab(tab) : props;
    }

    private static RegistrySupplier<Item> egg(String name, RegistrySupplier<? extends EntityType<? extends Mob>> type) {
        RegistrySupplier<Item> egg = ITEMS.register(name + "_spawn_egg",
                () -> new ArchitecturySpawnEggItem(type, 0xFFFFFF, 0xFFFFFF, listed(new Item.Properties(), name, ModTabs.MAIN)));
        SPAWN_EGGS.add(egg);
        return egg;
    }
}
