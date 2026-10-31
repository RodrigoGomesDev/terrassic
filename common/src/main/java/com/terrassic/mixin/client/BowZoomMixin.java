package com.terrassic.mixin.client;

import com.terrassic.client.WeaponPoses;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The vanilla bow's draw zoom for the hunting bow (the game checks for the vanilla bow by item).
 *  Optional: without it the hunting bow just does not zoom. */
@Mixin(AbstractClientPlayer.class)
public abstract class BowZoomMixin {
    @Inject(method = "getFieldOfViewModifier", at = @At("RETURN"), cancellable = true, require = 0)
    private void terrassic$bowZoom(CallbackInfoReturnable<Float> cir) {
        float zoom = WeaponPoses.bowZoom((AbstractClientPlayer) (Object) this);
        if (zoom > 0.0F) {
            float scale = Minecraft.getInstance().options.fovEffectScale().get().floatValue();
            cir.setReturnValue(cir.getReturnValue() * (1.0F - 0.15F * zoom * scale));
        }
    }
}
