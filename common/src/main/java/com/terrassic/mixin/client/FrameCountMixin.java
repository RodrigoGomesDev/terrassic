package com.terrassic.mixin.client;

import com.terrassic.client.dev.FrameCount;
import net.minecraft.client.gui.components.DebugScreenOverlay;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 1.21.1: counts the frames for dev/PerfTest and dev/DrawBench (the 1.20.1 FrameTimer ring is gone; every frame
 *  still logs its length here). */
@Mixin(DebugScreenOverlay.class)
public abstract class FrameCountMixin {
    @Inject(method = "logFrameDuration", at = @At("HEAD"))
    private void terrassic$countFrame(long nanos, CallbackInfo ci) {
        FrameCount.frames++;
    }
}
