package com.primalera.world;

import com.primalera.entity.DinosaurEntity;
import com.primalera.registry.ModEntities;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.hooks.level.biome.BiomeProperties;
import dev.architectury.registry.level.biome.BiomeModifications;
import dev.architectury.registry.level.entity.SpawnPlacementsRegistry;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * Natural spawning. Dinosaurs are CREATURE category, so (like cows and sheep)
 * they mostly appear when chunks are generated and then persist.
 *
 *  Compsognathus  forests, jungles               weight 8,  groups of 3-6
 *  Velociraptor   savannas, badlands, deserts*   weight 6,  packs of 2-4
 *  Triceratops    savannas, plains               weight 6,  herds of 2-4
 *  Stegosaurus    forests, plains                weight 4,  groups of 1-3
 *  Tyrannosaurus  savannas, jungles              weight 1,  alone
 *  (*desert only where there is sand to stand on)
 */
public final class ModSpawns {
    private ModSpawns() {
    }

    public static void init() {
        SpawnPlacementsRegistry.register(ModEntities.TYRANNOSAURUS, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, DinosaurEntity::checkDinoSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.TRICERATOPS, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, DinosaurEntity::checkDinoSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.STEGOSAURUS, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, DinosaurEntity::checkDinoSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.VELOCIRAPTOR, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, DinosaurEntity::checkDinoSpawnRules);
        SpawnPlacementsRegistry.register(ModEntities.COMPSOGNATHUS, SpawnPlacements.Type.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, DinosaurEntity::checkDinoSpawnRules);

        LifecycleEvent.SETUP.register(() -> BiomeModifications.addProperties((ctx, props) -> {
            boolean forest = ctx.hasTag(BiomeTags.IS_FOREST);
            boolean jungle = ctx.hasTag(BiomeTags.IS_JUNGLE);
            boolean savanna = ctx.hasTag(BiomeTags.IS_SAVANNA);
            boolean badlands = ctx.hasTag(BiomeTags.IS_BADLANDS);
            String path = ctx.getKey().map(k -> k.getPath()).orElse("");
            boolean plains = path.equals("plains") || path.equals("sunflower_plains");
            boolean desert = path.equals("desert");

            if (forest || jungle) {
                add(props, ModEntities.COMPSOGNATHUS.get(), 8, 3, 6);
            }
            if (savanna || badlands || desert) {
                add(props, ModEntities.VELOCIRAPTOR.get(), 6, 2, 4);
            }
            if (savanna || plains) {
                add(props, ModEntities.TRICERATOPS.get(), 6, 2, 4);
            }
            if (forest || plains) {
                add(props, ModEntities.STEGOSAURUS.get(), 4, 1, 3);
            }
            if (savanna || jungle) {
                add(props, ModEntities.TYRANNOSAURUS.get(), 1, 1, 1);
            }
        }));
    }

    private static void add(BiomeProperties.Mutable props, EntityType<?> type, int weight, int min, int max) {
        props.getSpawnProperties().addSpawn(MobCategory.CREATURE, new MobSpawnSettings.SpawnerData(type, weight, min, max));
    }
}
