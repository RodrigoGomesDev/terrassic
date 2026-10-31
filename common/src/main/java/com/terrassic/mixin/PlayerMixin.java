package com.terrassic.mixin;

import com.terrassic.entity.FlyingDinosaur;
import com.terrassic.item.AmberLensItem;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The Amber Lens counts as scoping, so it gets the vanilla spyglass zoom, overlay and slower mouse.
 * Riding a flyer in the air, sneak brings it down (client/DinoControls) instead of dropping the rider off mid-air, and
 * the rider stays seated rather than crouching in the saddle; on the ground sneak gets off as usual.
 */
@Mixin(Player.class)
public abstract class PlayerMixin {
    @Inject(method = "isScoping", at = @At("RETURN"), cancellable = true)
    private void terrassic$amberLensScoping(CallbackInfoReturnable<Boolean> cir) {
        Player self = (Player) (Object) this;
        if (!cir.getReturnValueZ() && self.isUsingItem() && self.getUseItem().getItem() instanceof AmberLensItem) {
            cir.setReturnValue(true);
        }
    }

    @Inject(method = "wantsToStopRiding", at = @At("HEAD"), cancellable = true)
    private void terrassic$stayOnFlyer(CallbackInfoReturnable<Boolean> cir) {
        if (terrassic$inFlight()) {
            cir.setReturnValue(false);
        }
    }

    @Inject(method = "updatePlayerPose", at = @At("HEAD"), cancellable = true)
    private void terrassic$seatedInFlight(CallbackInfo ci) {
        Player self = (Player) (Object) this;
        if (terrassic$inFlight()) {
            self.setPose(Pose.STANDING);
            ci.cancel();
        }
    }

    private boolean terrassic$inFlight() {
        Player self = (Player) (Object) this;
        return self.getVehicle() instanceof FlyingDinosaur flyer && flyer.isFlying();
    }
}
