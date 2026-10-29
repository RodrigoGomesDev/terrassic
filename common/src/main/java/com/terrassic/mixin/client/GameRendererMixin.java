package com.terrassic.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.client.RoarShake;
import net.minecraft.client.renderer.GameRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** The loud roar's camera shake (client/RoarShake), applied where the game tilts the view of a hurt player.
 *  Optional: without it the roar just does not shake the camera. */
@Mixin(GameRenderer.class)
public abstract class GameRendererMixin {
    @Inject(method = "bobHurt", at = @At("HEAD"), require = 0)
    private void terrassic$roarShake(PoseStack poseStack, float partialTick, CallbackInfo ci) {
        RoarShake.apply(poseStack, partialTick);
    }
}
