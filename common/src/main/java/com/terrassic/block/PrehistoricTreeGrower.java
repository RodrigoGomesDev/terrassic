package com.terrassic.block;

import com.terrassic.Terrassic;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.block.grower.TreeGrower;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;

import java.util.Optional;

/**
 * Grows a sapling into the tree data/terrassic/worldgen/configured_feature/&lt;tree&gt;.json (written by
 * tools/javagen/gen_blocks.py, the same feature the world generates).
 */
public final class PrehistoricTreeGrower {
    private PrehistoricTreeGrower() {
    }

    public static TreeGrower of(String tree) {
        ResourceKey<ConfiguredFeature<?, ?>> feature = ResourceKey.create(Registries.CONFIGURED_FEATURE, Terrassic.id(tree));
        return new TreeGrower(Terrassic.MOD_ID + ":" + tree, Optional.empty(), Optional.of(feature), Optional.empty());
    }
}
