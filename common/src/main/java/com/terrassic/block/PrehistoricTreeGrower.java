package com.terrassic.block;

import com.terrassic.Terrassic;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.grower.AbstractTreeGrower;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;

/**
 * Grows a sapling into the tree data/terrassic/worldgen/configured_feature/&lt;tree&gt;.json (written by
 * tools/javagen/gen_blocks.py, the same feature the world generates).
 */
public class PrehistoricTreeGrower extends AbstractTreeGrower {
    private final ResourceKey<ConfiguredFeature<?, ?>> tree;

    public PrehistoricTreeGrower(String tree) {
        this.tree = ResourceKey.create(Registries.CONFIGURED_FEATURE, Terrassic.id(tree));
    }

    @Override
    protected ResourceKey<ConfiguredFeature<?, ?>> getConfiguredFeature(RandomSource random, boolean hasFlowers) {
        return tree;
    }
}
