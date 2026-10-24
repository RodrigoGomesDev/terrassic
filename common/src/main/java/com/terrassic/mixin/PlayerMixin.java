package com.terrassic.mixin;

import com.terrassic.item.AmberLensItem;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The Amber Lens counts as scoping, so it gets the vanilla spyglass zoom, overlay and slower mouse.
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
}
