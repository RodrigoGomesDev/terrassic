package com.terrassic.mixin.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.terrassic.client.RiftStormClient;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Amber fog (and clear colour) during a Rift Storm (v0.8, phase M4). Optional. */
@Mixin(FogRenderer.class)
public abstract class FogRendererMixin {
    @Shadow
    private static float fogRed;
    @Shadow
    private static float fogGreen;
    @Shadow
    private static float fogBlue;

    @Inject(method = "setupColor", at = @At("TAIL"), require = 0)
    private static void terrassic$stormFog(Camera camera, float partialTick, ClientLevel level, int renderDistance,
                                           float bossColor, CallbackInfo ci) {
        if (RiftStormClient.intensity(partialTick) <= 0.0F) {
            return;
        }
        Vec3 c = RiftStormClient.tintFog(new Vec3(fogRed, fogGreen, fogBlue), partialTick);
        fogRed = (float) c.x;
        fogGreen = (float) c.y;
        fogBlue = (float) c.z;
        RenderSystem.clearColor(fogRed, fogGreen, fogBlue, 0.0F);
    }
}
