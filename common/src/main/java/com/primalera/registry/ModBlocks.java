package com.primalera.registry;

import com.primalera.PrimalEra;
import com.primalera.block.DinoEggBlock;
import com.primalera.entity.DinosaurEntity;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

import java.util.LinkedHashMap;
import java.util.Map;

/** Dinosaur egg blocks, one per species ("&lt;species&gt;_egg"). */
public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(PrimalEra.MOD_ID, Registries.BLOCK);

    /** species id -> egg block, in registration order (also used for the creative tab). */
    public static final Map<String, RegistrySupplier<Block>> EGGS = new LinkedHashMap<>();

    static {
        egg("tyrannosaurus", ModEntities.TYRANNOSAURUS, true);
        egg("spinosaurus", ModEntities.SPINOSAURUS, true);
        egg("dilophosaurus", ModEntities.DILOPHOSAURUS, false);
        egg("velociraptor", ModEntities.VELOCIRAPTOR, false);
        egg("compsognathus", ModEntities.COMPSOGNATHUS, false);
        egg("triceratops", ModEntities.TRICERATOPS, true);
        egg("stegosaurus", ModEntities.STEGOSAURUS, true);
        egg("ankylosaurus", ModEntities.ANKYLOSAURUS, true);
        egg("brachiosaurus", ModEntities.BRACHIOSAURUS, true);
        egg("parasaurolophus", ModEntities.PARASAUROLOPHUS, true);
        egg("pachycephalosaurus", ModEntities.PACHYCEPHALOSAURUS, false);
        egg("gallimimus", ModEntities.GALLIMIMUS, false);
    }

    private ModBlocks() {
    }

    private static void egg(String species, RegistrySupplier<? extends EntityType<? extends DinosaurEntity>> type, boolean large) {
        EGGS.put(species, BLOCKS.register(species + "_egg", () -> new DinoEggBlock(type, large,
                BlockBehaviour.Properties.of().mapColor(MapColor.SAND).strength(0.5F).sound(SoundType.METAL)
                        .randomTicks().noOcclusion())));
    }

    /** The egg block of a species, or null if the registry is not ready / unknown species. */
    public static Block eggFor(String species) {
        RegistrySupplier<Block> egg = EGGS.get(species);
        return egg != null && egg.isPresent() ? egg.get() : null;
    }
}
