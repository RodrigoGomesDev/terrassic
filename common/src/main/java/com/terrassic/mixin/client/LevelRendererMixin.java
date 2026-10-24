package com.terrassic.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.terrassic.client.LeapClient;
import net.minecraft.client.Camera;
import net.minecraft.client.renderer.LevelRenderer;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Shooting stars (v0.9), drawn after the vanilla sky. Optional: without it there are just no shooting stars. */
@Mixin(LevelRenderer.class)
public abstract class LevelRendererMixin {
    @Inject(method = "renderSky", at = @At("TAIL"), require = 0)
    private void terrassic$shootingStars(PoseStack poseStack, Matrix4f projection, float partialTick, Camera camera,
                                         boolean foggy, Runnable fogSetup, CallbackInfo ci) {
        if (!foggy) {
            LeapClient.renderStreaks(poseStack, partialTick);
        }
    }
}
