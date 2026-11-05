package com.terrassic.mixin.parts;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Hit parts (1.7): an arrow that hits a part has its after-effects (a dart's dose and sticking) on the creature. */
@Mixin(AbstractArrow.class)
public interface AbstractArrowInvoker {
    @Invoker("doPostHurtEffects")
    void terrassic$doPostHurtEffects(LivingEntity target);
}
