package com.terrassic.world.continent;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.biome.Climate;

import java.util.List;
import java.util.stream.Stream;

/**
 * Biome source type {@code terrassic:continente}: the world types "Terrassic" (data/terrassic/worldgen/world_preset)
 * wrap their biome map in it to say "this overworld is a continent of radius {@code raio}". The biomes come from
 * {@code biome_source} unchanged; the continent itself is the terrain, put in place by ChunkMapMixin and
 * {@link ContinentRouter} when the level starts. The radius lives here, in the world's own saved settings, so a
 * world keeps its size whatever the config says later.
 */
public final class ContinentBiomeSource extends BiomeSource {
    public static final Codec<ContinentBiomeSource> CODEC = RecordCodecBuilder.create(i -> i.group(
            BiomeSource.CODEC.fieldOf("biome_source").forGetter(ContinentBiomeSource::biomes),
            Codec.intRange(64, 30000).optionalFieldOf("raio", ContinentDensity.DEFAULT_RADIUS).forGetter(ContinentBiomeSource::radius)
    ).apply(i, ContinentBiomeSource::new));

    private final BiomeSource biomes;
    private final int radius;

    public ContinentBiomeSource(BiomeSource biomes, int radius) {
        this.biomes = biomes;
        this.radius = radius;
    }

    public BiomeSource biomes() {
        return biomes;
    }

    /** Radius of the continent in blocks. */
    public int radius() {
        return radius;
    }

    @Override
    protected Codec<? extends BiomeSource> codec() {
        return CODEC;
    }

    @Override
    protected Stream<Holder<Biome>> collectPossibleBiomes() {
        return biomes.possibleBiomes().stream();
    }

    @Override
    public Holder<Biome> getNoiseBiome(int x, int y, int z, Climate.Sampler sampler) {
        return biomes.getNoiseBiome(x, y, z, sampler);
    }

    @Override
    public void addDebugInfo(List<String> info, BlockPos pos, Climate.Sampler sampler) {
        info.add("Terrassic continent, radius " + radius);
        biomes.addDebugInfo(info, pos, sampler);
    }
}
