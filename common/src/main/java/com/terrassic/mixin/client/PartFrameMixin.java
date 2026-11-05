package com.terrassic.mixin.client;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.parts.PartOwners;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Hit parts (1.7): every frame, before the crosshair is aimed, the parts of the creatures around are put where their
 * models are drawn in this frame (between two ticks: position, body and head turned as the renderer interpolates
 * them). A creature turning fast no longer leaves its tail outside its boxes for a frame.
 */
@Mixin(GameRenderer.class)
public abstract class PartFrameMixin {
    @Inject(method = "pick", at = @At("HEAD"))
    private void terrassic$placeParts(float partialTick, CallbackInfo ci) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        for (DinosaurEntity owner : ((PartOwners) mc.level).terrassic$partOwners()) {
            if (!owner.isRemoved() && owner.partsActive()) {
                owner.placeParts(partialTick);
            }
        }
    }
}
