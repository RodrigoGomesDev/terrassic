package com.terrassic.mixin.client;

import com.terrassic.client.compat.HatsCompat;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.LivingEntity;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Hats Renewed (optional): a dinosaur's hat sits on its skull as drawn, scale included (client.compat.HatsCompat).
 *  Without Hats the target class is missing and this mixin is skipped. */
@Pseudo
@Mixin(targets = "me.guivnf.mods.hats.client.compat.GeckoLibCompat", remap = false)
public abstract class HatsHeadMixin {
    @Inject(method = "getHeadMatrix", at = @At("HEAD"), cancellable = true, remap = false, require = 0)
    private static void terrassic$dinosaurSkull(LivingEntity entity, CallbackInfoReturnable<Matrix4f> cir) {
        if (entity instanceof DinosaurEntity) {
            Matrix4f anchor = HatsCompat.anchor(entity);
            if (anchor != null) {
                cir.setReturnValue(anchor);
            }
        }
    }
}
