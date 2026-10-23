package com.primalera.registry;

import com.primalera.PrimalEra;
import com.primalera.item.ClubItem;
import com.primalera.item.FlintHatchetItem;
import com.primalera.item.ModTiers;
import com.primalera.item.SpearItem;
import dev.architectury.core.item.ArchitecturySpawnEggItem;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.level.block.Block;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(PrimalEra.MOD_ID, Registries.ITEM);

    /** Every spawn egg, in creative-tab order. */
    public static final List<RegistrySupplier<Item>> SPAWN_EGGS = new ArrayList<>();

    // ---- spawn eggs (each has its own sprite, so the tint colours are plain white)
    public static final RegistrySupplier<Item> TYRANNOSAURUS_SPAWN_EGG = egg("tyrannosaurus", ModEntities.TYRANNOSAURUS);
    public static final RegistrySupplier<Item> SPINOSAURUS_SPAWN_EGG = egg("spinosaurus", ModEntities.SPINOSAURUS);
    public static final RegistrySupplier<Item> DILOPHOSAURUS_SPAWN_EGG = egg("dilophosaurus", ModEntities.DILOPHOSAURUS);
    public static final RegistrySupplier<Item> VELOCIRAPTOR_SPAWN_EGG = egg("velociraptor", ModEntities.VELOCIRAPTOR);
    public static final RegistrySupplier<Item> COMPSOGNATHUS_SPAWN_EGG = egg("compsognathus", ModEntities.COMPSOGNATHUS);
    public static final RegistrySupplier<Item> TRICERATOPS_SPAWN_EGG = egg("triceratops", ModEntities.TRICERATOPS);
    public static final RegistrySupplier<Item> STEGOSAURUS_SPAWN_EGG = egg("stegosaurus", ModEntities.STEGOSAURUS);
    public static final RegistrySupplier<Item> ANKYLOSAURUS_SPAWN_EGG = egg("ankylosaurus", ModEntities.ANKYLOSAURUS);
    public static final RegistrySupplier<Item> BRACHIOSAURUS_SPAWN_EGG = egg("brachiosaurus", ModEntities.BRACHIOSAURUS);
    public static final RegistrySupplier<Item> PARASAUROLOPHUS_SPAWN_EGG = egg("parasaurolophus", ModEntities.PARASAUROLOPHUS);
    public static final RegistrySupplier<Item> PACHYCEPHALOSAURUS_SPAWN_EGG = egg("pachycephalosaurus", ModEntities.PACHYCEPHALOSAURUS);
    public static final RegistrySupplier<Item> GALLIMIMUS_SPAWN_EGG = egg("gallimimus", ModEntities.GALLIMIMUS);

    // ---- materials dropped by dinosaurs
    public static final RegistrySupplier<Item> REX_TOOTH = ITEMS.register("rex_tooth",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> TRICERATOPS_HORN = ITEMS.register("triceratops_horn",
            () -> new Item(new Item.Properties().arch$tab(ModTabs.MAIN)));
    public static final RegistrySupplier<Item> ANKYLOSAURUS_CLUB = ITEMS.register("ankylosaurus_club",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).arch$tab(ModTabs.MAIN)));

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

    // ---- dinosaur egg block items
    static {
        for (Map.Entry<String, RegistrySupplier<Block>> e : ModBlocks.EGGS.entrySet()) {
            RegistrySupplier<Block> block = e.getValue();
            ITEMS.register(e.getKey() + "_egg", () -> new BlockItem(block.get(), new Item.Properties().stacksTo(16).arch$tab(ModTabs.MAIN)));
        }
    }

    private ModItems() {
    }

    private static RegistrySupplier<Item> egg(String name, RegistrySupplier<? extends EntityType<? extends Mob>> type) {
        RegistrySupplier<Item> egg = ITEMS.register(name + "_spawn_egg",
                () -> new ArchitecturySpawnEggItem(type, 0xFFFFFF, 0xFFFFFF, new Item.Properties().arch$tab(ModTabs.MAIN)));
        SPAWN_EGGS.add(egg);
        return egg;
    }
}
