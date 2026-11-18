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
 * them). A creature turning fast no longer leaves its tail outside its boxes for a frame. 1.11: only the creatures
 * within {@link #NEAR} blocks of the camera, farther than any reach or weapon (docs/DESEMPENHO_1_11.md); the rest keep
 * the parts placed on their tick.
 */
@Mixin(GameRenderer.class)
public abstract class PartFrameMixin {
    @org.spongepowered.asm.mixin.Unique
    private static final double NEAR = 32.0D;

    @Inject(method = "pick", at = @At("HEAD"))
    private void terrassic$placeParts(float partialTick, CallbackInfo ci) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        net.minecraft.world.phys.Vec3 eye = mc.gameRenderer.getMainCamera().getPosition();
        for (DinosaurEntity owner : ((PartOwners) mc.level).terrassic$partOwners()) {
            if (!owner.isRemoved() && owner.partsActive() && owner.distanceToSqr(eye) < NEAR * NEAR) {
                owner.placeParts(partialTick);
            }
        }
    }
}
