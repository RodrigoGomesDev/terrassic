package com.terrassic.mixin.client;

import com.terrassic.client.LeapClient;
import com.terrassic.client.RiftStormClient;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Amber sky and clouds during a Rift Storm (v0.8, phase M4), red during the ritual of the meteors (v0.9). Optional: without it the storm just has no tint. */
@Mixin(ClientLevel.class)
public abstract class ClientLevelMixin {
    @Inject(method = "getSkyColor", at = @At("RETURN"), cancellable = true, require = 0)
    private void terrassic$stormSky(Vec3 pos, float partialTick, CallbackInfoReturnable<Vec3> cir) {
        cir.setReturnValue(LeapClient.tintSky(RiftStormClient.tintSky(cir.getReturnValue(), partialTick), partialTick));
    }

    @Inject(method = "getCloudColor", at = @At("RETURN"), cancellable = true, require = 0)
    private void terrassic$stormClouds(float partialTick, CallbackInfoReturnable<Vec3> cir) {
        cir.setReturnValue(LeapClient.tintSky(RiftStormClient.tintSky(cir.getReturnValue(), partialTick), partialTick));
    }
}
