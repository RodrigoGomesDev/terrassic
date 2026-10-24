package com.terrassic.mixin.client;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.MultiPlayerGameMode;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Every dinosaur is a HasCustomInventoryScreen (the inventory key opens the cargo while riding), which makes vanilla
 * send OPEN_INVENTORY to the server instead of opening the player's own inventory. Only do that when the mount really
 * carries a chest; otherwise the key opens the rider's inventory as usual.
 */
@Mixin(MultiPlayerGameMode.class)
public abstract class InventoryKeyMixin {
    @Shadow
    @Final
    private Minecraft minecraft;

    @Inject(method = "isServerControlledInventory", at = @At("HEAD"), cancellable = true)
    private void terrassic$inventoryKeyOnlyWithCargo(CallbackInfoReturnable<Boolean> cir) {
        if (this.minecraft.player != null && this.minecraft.player.getVehicle() instanceof DinosaurEntity dino && !dino.isChested()) {
            cir.setReturnValue(false);
        }
    }
}
