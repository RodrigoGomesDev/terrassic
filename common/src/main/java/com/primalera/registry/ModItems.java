package com.primalera.registry;

import com.primalera.PrimalEra;
import dev.architectury.core.item.ArchitecturySpawnEggItem;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;

public final class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(PrimalEra.MOD_ID, Registries.ITEM);

    public static final RegistrySupplier<Item> TYRANNOSAURUS_SPAWN_EGG = egg("tyrannosaurus", ModEntities.TYRANNOSAURUS, 0x4B3F30, 0xCDB994);
    public static final RegistrySupplier<Item> TRICERATOPS_SPAWN_EGG = egg("triceratops", ModEntities.TRICERATOPS, 0x7B6E57, 0x9A4E2E);
    public static final RegistrySupplier<Item> STEGOSAURUS_SPAWN_EGG = egg("stegosaurus", ModEntities.STEGOSAURUS, 0x727C49, 0xE09A44);
    public static final RegistrySupplier<Item> VELOCIRAPTOR_SPAWN_EGG = egg("velociraptor", ModEntities.VELOCIRAPTOR, 0x9C7149, 0x3E2C1D);
    public static final RegistrySupplier<Item> COMPSOGNATHUS_SPAWN_EGG = egg("compsognathus", ModEntities.COMPSOGNATHUS, 0x8C874A, 0x57562C);

    private ModItems() {
    }

    private static RegistrySupplier<Item> egg(String name, RegistrySupplier<? extends EntityType<? extends Mob>> type,
                                              int background, int highlight) {
        return ITEMS.register(name + "_spawn_egg",
                () -> new ArchitecturySpawnEggItem(type, background, highlight, new Item.Properties().arch$tab(ModTabs.MAIN)));
    }
}
