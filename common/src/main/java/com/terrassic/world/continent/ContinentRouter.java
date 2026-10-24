package com.terrassic.world.continent;

import com.terrassic.Terrassic;
import net.minecraft.world.level.levelgen.DensityFunction;
import net.minecraft.world.level.levelgen.DensityFunctions;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import net.minecraft.world.level.levelgen.NoiseRouter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

/**
 * Puts the Terrassic continent into a vanilla noise router: every read of the vanilla continentalness (the router's
 * own {@code continents}, which the biome choice uses, and every terrain function that reads
 * {@code minecraft:overworld/continents} by name: offset, factor, jaggedness, depth, sloped_cheese...) becomes a
 * {@link ContinentDensity} around it. Nothing of vanilla is copied: the world keeps the vanilla noise settings
 * (surface rules, aquifers, ores, caves) and only the continentalness changes.
 *
 * <p>Called by ChunkMapMixin, once per level, right before the router is wired to the world seed.
 */
public final class ContinentRouter {
    private static final Logger LOG = LoggerFactory.getLogger(Terrassic.MOD_ID);

    private ContinentRouter() {
    }

    /** {@code settings} with the continent of radius {@code radius} in its noise router. */
    public static NoiseGeneratorSettings apply(NoiseGeneratorSettings settings, int radius) {
        NoiseRouter router = settings.noiseRouter();
        // Density functions are records that compare by value, and mapping with a visitor that changes nothing
        // rebuilds the same structure, so the vanilla continentalness mapped that way equals each place the router
        // reads it. Visitors run bottom-up and the root comes last: the root is the reference wrapper (as read by
        // name) and the node just before it is the function itself (as read by spline coordinates, which unwrap the
        // reference). Matching the function itself catches both, since the wrapper is rebuilt around the match.
        List<DensityFunction> seen = new ArrayList<>();
        router.continents().mapAll(f -> {
            seen.add(f);
            return f;
        });
        DensityFunction outer = seen.get(seen.size() - 1);
        DensityFunction inner = seen.size() > 1 ? seen.get(seen.size() - 2) : outer;
        int[] hits = {0};
        NoiseRouter rewritten = router.mapAll(f -> {
            if (f.equals(inner) || f.equals(outer)) {
                hits[0]++;
                return DensityFunctions.flatCache(new ContinentDensity(f, radius));
            }
            return f;
        });
        if (hits[0] == 0) {
            LOG.warn("Terrassic continent: no vanilla continentalness found in the noise router; the world stays vanilla");
            return settings;
        }
        LOG.info("Terrassic continent of radius {} blocks ({} reads of the continentalness replaced)", radius, hits[0]);
        // this copy only feeds RandomState.create (router, noise and sea settings); the chunk generator keeps the
        // original settings for everything else (surface rules, saving the world)
        return new NoiseGeneratorSettings(settings.noiseSettings(), settings.defaultBlock(), settings.defaultFluid(),
                rewritten, settings.surfaceRule(), settings.spawnTarget(), settings.seaLevel(),
                settings.disableMobGeneration(), settings.aquifersEnabled(), settings.oreVeinsEnabled(),
                settings.useLegacyRandomSource());
    }
}
