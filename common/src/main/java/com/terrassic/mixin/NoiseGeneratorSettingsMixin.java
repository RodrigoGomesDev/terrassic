package com.terrassic.mixin;

import com.terrassic.world.CretaceousSurface;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import net.minecraft.world.level.levelgen.SurfaceRules;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Puts the surface rules of the Cretaceous biomes ({@link CretaceousSurface}) in front of every surface rule. They
 * only match Cretaceous biomes, so worlds without them generate exactly as before.
 */
@Mixin(NoiseGeneratorSettings.class)
public abstract class NoiseGeneratorSettingsMixin {
    @Inject(method = "surfaceRule", at = @At("RETURN"), cancellable = true)
    private void terrassic$cretaceousSurface(CallbackInfoReturnable<SurfaceRules.RuleSource> cir) {
        cir.setReturnValue(CretaceousSurface.wrap(cir.getReturnValue()));
    }
}
