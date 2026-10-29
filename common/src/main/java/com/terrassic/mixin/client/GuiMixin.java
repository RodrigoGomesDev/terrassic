package com.terrassic.mixin.client;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.client.gui.Gui;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** A ridden dinosaur's health is on the mount panel (client/TerrassicHud): the vanilla Gui counts no vehicle hearts for
 *  it, so it draws no mount hearts and keeps the player's own food bar. Horses and other vanilla mounts are untouched.
 *  (Forge draws these through its own overlays: forge/MountHudForge.) */
@Mixin(Gui.class)
public abstract class GuiMixin {
    @Inject(method = "getVehicleMaxHearts", at = @At("HEAD"), cancellable = true, require = 0)
    private void terrassic$noDinoHearts(LivingEntity vehicle, CallbackInfoReturnable<Integer> cir) {
        if (vehicle instanceof DinosaurEntity) {
            cir.setReturnValue(0);
        }
    }
}
