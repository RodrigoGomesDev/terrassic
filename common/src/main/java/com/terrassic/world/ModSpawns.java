package com.terrassic.world;

import com.terrassic.config.SpawnConfig;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.entity.SwimmingDinosaur;
import com.terrassic.registry.ModEntities;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.hooks.level.biome.BiomeProperties;
import dev.architectury.registry.level.biome.BiomeModifications;
import dev.architectury.registry.level.entity.SpawnPlacementsRegistry;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * Natural spawning. Dinosaurs are CREATURE category, so (like cows and sheep) they mostly appear when chunks
 * are generated and then persist.
 *
 *  BEGIN GENERATED table (tools/javagen/gen_species.py, table WORLD)
 *  Species             Biomes                          weight  group
 *  Tyrannosaurus       savanna, jungle                 1       1
 *  Spinosaurus         river, swamp, mangrove          2       1
 *  Dilophosaurus       forest, jungle                  3       1-2
 *  Velociraptor        savanna, badlands, desert*      6       2-4
 *  Compsognathus       forest, jungle                  8       3-6
 *  Triceratops         savanna, plains                 6       2-4
 *  Stegosaurus         forest, plains                  4       1-3
 *  Ankylosaurus        forest, plains, badlands        3       1-2
 *  Brachiosaurus       savanna, plains                 1       1-2
 *  Parasaurolophus     plains, forest                  5       2-5
 *  Pachycephalosaurus  taiga, hills                    4       2-3
 *  Gallimimus          savanna, plains, desert*        6       3-6
 *  Maiasaura           plains, savanna                 4       3-6
 *  Pteranodon          beach, stony shore              8       2-4
 *  Quetzalcoatlus      plains, savanna, badlands       3       1-2
 *  Hatzegopteryx       hills, forest                   2       1
 *  Mosasaurus          deep ocean (not frozen)         2       1
 *  END GENERATED table
 *  (*desert only where there is sand to stand on)
 * Weights can be scaled or turned off per species in config/terrassic.json (SpawnConfig).
 */
public final class ModSpawns {
    private ModSpawns() {
    }

    public static void init() {
        // BEGIN GENERATED placements
        placement(ModEntities.TYRANNOSAURUS);
        placement(ModEntities.SPINOSAURUS);
        placement(ModEntities.DILOPHOSAURUS);
        placement(ModEntities.VELOCIRAPTOR);
        placement(ModEntities.COMPSOGNATHUS);
        placement(ModEntities.TRICERATOPS);
        placement(ModEntities.STEGOSAURUS);
        placement(ModEntities.ANKYLOSAURUS);
        placement(ModEntities.BRACHIOSAURUS);
        placement(ModEntities.PARASAUROLOPHUS);
        placement(ModEntities.PACHYCEPHALOSAURUS);
        placement(ModEntities.GALLIMIMUS);
        placement(ModEntities.MAIASAURA);
        SpawnPlacementsRegistry.register(ModEntities.PTERANODON, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, FlyingDinosaur::checkFlyerSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.QUETZALCOATLUS, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, FlyingDinosaur::checkFlyerSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.HATZEGOPTERYX, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, FlyingDinosaur::checkFlyerSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.MOSASAURUS, SpawnPlacements.Type.IN_WATER,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, SwimmingDinosaur::checkSeaSpawnRules);
        // END GENERATED placements

        LifecycleEvent.SETUP.register(() -> BiomeModifications.addProperties((ctx, props) -> {
            String key = ctx.getKey().map(k -> k.toString()).orElse("");
            // BEGIN GENERATED biomes
            boolean forest = ctx.hasTag(BiomeTags.IS_FOREST);
            boolean jungle = ctx.hasTag(BiomeTags.IS_JUNGLE);
            boolean savanna = ctx.hasTag(BiomeTags.IS_SAVANNA);
            boolean badlands = ctx.hasTag(BiomeTags.IS_BADLANDS);
            boolean taiga = ctx.hasTag(BiomeTags.IS_TAIGA);
            boolean hill = ctx.hasTag(BiomeTags.IS_HILL);
            boolean river = ctx.hasTag(BiomeTags.IS_RIVER);
            boolean plains = key.equals("minecraft:plains") || key.equals("minecraft:sunflower_plains");
            boolean desert = key.equals("minecraft:desert");
            boolean swamp = key.equals("minecraft:swamp") || key.equals("minecraft:mangrove_swamp");
            boolean coast = ctx.hasTag(BiomeTags.IS_BEACH) || key.equals("minecraft:stony_shore");
            boolean deepSea = ctx.hasTag(BiomeTags.IS_DEEP_OCEAN) && !key.contains("frozen");

            if (savanna || jungle) {
                add(props, ModEntities.TYRANNOSAURUS.get(), 1, 1, 1);
            }
            if (river || swamp) {
                add(props, ModEntities.SPINOSAURUS.get(), 2, 1, 1);
            }
            if (forest || jungle) {
                add(props, ModEntities.DILOPHOSAURUS.get(), 3, 1, 2);
            }
            if (savanna || badlands || desert) {
                add(props, ModEntities.VELOCIRAPTOR.get(), 6, 2, 4);
            }
            if (forest || jungle) {
                add(props, ModEntities.COMPSOGNATHUS.get(), 8, 3, 6);
            }
            if (savanna || plains) {
                add(props, ModEntities.TRICERATOPS.get(), 6, 2, 4);
            }
            if (forest || plains) {
                add(props, ModEntities.STEGOSAURUS.get(), 4, 1, 3);
            }
            if (forest || plains || badlands) {
                add(props, ModEntities.ANKYLOSAURUS.get(), 3, 1, 2);
            }
            if (savanna || plains) {
                add(props, ModEntities.BRACHIOSAURUS.get(), 1, 1, 2);
            }
            if (plains || forest) {
                add(props, ModEntities.PARASAUROLOPHUS.get(), 5, 2, 5);
            }
            if (taiga || hill) {
                add(props, ModEntities.PACHYCEPHALOSAURUS.get(), 4, 2, 3);
            }
            if (savanna || plains || desert) {
                add(props, ModEntities.GALLIMIMUS.get(), 6, 3, 6);
            }
            if (plains || savanna) {
                add(props, ModEntities.MAIASAURA.get(), 4, 3, 6);
            }
            if (coast) {
                add(props, ModEntities.PTERANODON.get(), 8, 2, 4);
            }
            if (plains || savanna || badlands) {
                add(props, ModEntities.QUETZALCOATLUS.get(), 3, 1, 2);
            }
            if (hill || forest) {
                add(props, ModEntities.HATZEGOPTERYX.get(), 2, 1, 1);
            }
            if (deepSea) {
                add(props, MobCategory.WATER_CREATURE, ModEntities.MOSASAURUS.get(), 2, 1, 1);
            }
            // END GENERATED biomes
        }));
    }

    private static <T extends DinosaurEntity> void placement(RegistrySupplier<EntityType<T>> type) {
        SpawnPlacementsRegistry.register(type, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, DinosaurEntity::checkDinoSpawnRules);
    }

    private static void add(BiomeProperties.Mutable props, EntityType<?> type, int weight, int min, int max) {
        add(props, MobCategory.CREATURE, type, weight, min, max);
    }

    /** Adds the spawn with the weight from config/terrassic.json (see {@link SpawnConfig}); skipped when it is 0. */
    private static void add(BiomeProperties.Mutable props, MobCategory category, EntityType<?> type, int weight, int min, int max) {
        int w = SpawnConfig.weight(BuiltInRegistries.ENTITY_TYPE.getKey(type).getPath(), weight);
        if (w > 0) {
            props.getSpawnProperties().addSpawn(category, new MobSpawnSettings.SpawnerData(type, w, min, max));
        }
    }
}
