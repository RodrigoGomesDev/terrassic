package com.terrassic.entity;

import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** A flint-tipped arrow (docs/ARMAS.md): a little more bite than the vanilla arrow, picked up as itself. */
public class FlintArrow extends AbstractArrow {
    public FlintArrow(EntityType<? extends FlintArrow> type, Level level) {
        super(type, level);
        this.setBaseDamage(2.5D);
    }

    public FlintArrow(Level level, LivingEntity shooter) {
        super(ModEntities.FLINT_ARROW.get(), shooter, level);
        this.setBaseDamage(2.5D);
    }

    @Override
    protected ItemStack getPickupItem() {
        return new ItemStack(ModItems.FLINT_ARROW.get());
    }
}
