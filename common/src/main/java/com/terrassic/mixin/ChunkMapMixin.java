package com.terrassic.mixin;

import com.llamalad7.mixinextras.sugar.Local;
import com.terrassic.world.continent.ContinentBiomeSource;
import com.terrassic.world.continent.ContinentRouter;
import net.minecraft.server.level.ChunkMap;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/**
 * The Terrassic continent (docs/MUNDO.md, section 10): when a level whose biome source is a
 * {@link ContinentBiomeSource} starts, its noise router gets the continent ({@link ContinentRouter}) right before
 * RandomState wires it to the seed. Everything that shapes the world reads that RandomState: terrain, biomes,
 * structures, the spawn point.
 */
@Mixin(ChunkMap.class)
public abstract class ChunkMapMixin {
    @ModifyArg(method = "<init>", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/level/levelgen/RandomState;create(Lnet/minecraft/world/level/levelgen/NoiseGeneratorSettings;Lnet/minecraft/core/HolderGetter;J)Lnet/minecraft/world/level/levelgen/RandomState;"), index = 0)
    private NoiseGeneratorSettings terrassic$continent(NoiseGeneratorSettings settings, @Local(argsOnly = true) ChunkGenerator generator) {
        if (generator != null && generator.getBiomeSource() instanceof ContinentBiomeSource continent) {
            return ContinentRouter.apply(settings, continent.radius());
        }
        return settings;
    }
}
