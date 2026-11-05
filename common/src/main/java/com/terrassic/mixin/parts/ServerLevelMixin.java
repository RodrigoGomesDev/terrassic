package com.terrassic.mixin.parts;

import com.terrassic.entity.parts.DinoParts;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Hit parts (1.7): a player's attack or use packet names the part it aimed at by id; the server finds it here, next to
 * the Ender Dragon's parts (and Forge's PartEntity).
 */
@Mixin(ServerLevel.class)
public abstract class ServerLevelMixin {
    @Inject(method = "getEntityOrPart", at = @At("RETURN"), cancellable = true)
    private void terrassic$findPart(int id, CallbackInfoReturnable<Entity> cir) {
        if (cir.getReturnValue() == null) {
            Entity part = DinoParts.partById((ServerLevel) (Object) this, id);
            if (part != null) {
                cir.setReturnValue(part);
            }
        }
    }
}
