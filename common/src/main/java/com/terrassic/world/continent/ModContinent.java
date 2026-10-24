package com.terrassic.world.continent;

import com.mojang.serialization.Codec;
import com.terrassic.Terrassic;
import com.terrassic.config.WorldConfig;
import dev.architectury.event.events.common.LifecycleEvent;
import dev.architectury.registry.registries.DeferredRegister;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.border.WorldBorder;
import net.minecraft.world.level.levelgen.DensityFunction;
import net.minecraft.world.level.levelgen.presets.WorldPreset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The Terrassic continent (docs/MUNDO.md, section 10): a world much smaller than vanilla, one Pangaea-like continent
 * with the sea all around and a world border that closes it.
 * <ul>
 *   <li>{@link ContinentBiomeSource} ({@code terrassic:continente} biome source) marks a world type as a continent
 *       and carries its radius; the three "Terrassic" world types use it (tools/javagen/gen_world.py).</li>
 *   <li>{@link ContinentRouter} and ChunkMapMixin swap the vanilla continentalness for {@link ContinentDensity}
 *       when such a level starts.</li>
 *   <li>WorldCreationUiStateMixin (client) opens "Criar novo mundo" on {@link #DEFAULT_PRESET}.</li>
 *   <li>{@link #closeTheSea}: the world border of a new continent world.</li>
 * </ul>
 */
public final class ModContinent {
    private static final Logger LOG = LoggerFactory.getLogger(Terrassic.MOD_ID);

    public static final DeferredRegister<Codec<? extends BiomeSource>> BIOME_SOURCES =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.BIOME_SOURCE);
    public static final DeferredRegister<Codec<? extends DensityFunction>> DENSITY_FUNCTION_TYPES =
            DeferredRegister.create(Terrassic.MOD_ID, Registries.DENSITY_FUNCTION_TYPE);

    /** World type selected by default in "Criar novo mundo" (the medium continent). */
    public static final ResourceKey<WorldPreset> DEFAULT_PRESET =
            ResourceKey.create(Registries.WORLD_PRESET, Terrassic.id("terrassic"));

    /** Vanilla's default border is 59 999 968 blocks wide; anything that big has not been set by anyone. */
    private static final double UNSET_BORDER = 5.0E7D;

    private ModContinent() {
    }

    public static void init() {
        BIOME_SOURCES.register("continente", () -> ContinentBiomeSource.CODEC);
        BIOME_SOURCES.register();
        DENSITY_FUNCTION_TYPES.register("continente", ContinentDensity.CODEC::codec);
        DENSITY_FUNCTION_TYPES.register();
        LifecycleEvent.SERVER_STARTED.register(ModContinent::closeTheSea);
    }

    /** Radius in blocks of the continent this level is built on, or 0 for any other world. */
    public static int radius(ServerLevel level) {
        return level.getChunkSource().getGenerator().getBiomeSource() instanceof ContinentBiomeSource c ? c.radius() : 0;
    }

    /**
     * A new continent world gets a square border centred on the continent, {@code borda_em_raios} radii from the
     * middle (2 by default: the continent plus about one radius of open sea). A border someone already set, or
     * {@code "borda": false} in config/terrassic-world.json, is left alone; /worldborder still works as usual.
     */
    private static void closeTheSea(MinecraftServer server) {
        ServerLevel overworld = server.overworld();
        int radius = radius(overworld);
        if (radius <= 0 || !WorldConfig.continentBorder()) {
            return;
        }
        WorldBorder border = overworld.getWorldBorder();
        if (border.getSize() < UNSET_BORDER) {
            return;
        }
        double size = 2.0D * radius * WorldConfig.continentBorderRadii();
        border.setCenter(0.0D, 0.0D);
        border.setSize(size);
        LOG.info("Terrassic continent of radius {}: world border set to {} blocks", radius, (int) size);
    }
}
