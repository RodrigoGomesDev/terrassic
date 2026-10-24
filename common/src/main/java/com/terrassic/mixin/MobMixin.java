package com.terrassic.mixin;

import com.terrassic.world.CretaceousBiomes;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.LevelAccessor;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Keeps the vanilla night monsters that do not belong to the Late Cretaceous off the surface of the Cretaceous biomes
 * ({@link CretaceousBiomes#blocksSpawn}). Mob.checkSpawnRules is asked for every natural and world-generation spawn.
 */
@Mixin(Mob.class)
public abstract class MobMixin {
    @Inject(method = "checkSpawnRules", at = @At("HEAD"), cancellable = true)
    private void terrassic$cretaceousNights(LevelAccessor level, MobSpawnType reason, CallbackInfoReturnable<Boolean> cir) {
        if (CretaceousBiomes.blocksSpawn((Mob) (Object) this, level, reason)) {
            cir.setReturnValue(false);
        }
    }
}
