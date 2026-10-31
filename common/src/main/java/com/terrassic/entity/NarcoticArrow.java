package com.terrassic.entity;

import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * An arrow tipped with the sleep herb (docs/ARMAS.md): a dart for the bow. It works like the blowgun's dart, with a
 * dose that follows the draw: up to 2.2 darts' worth from a full draw (3 for a T. rex instead of 5 darts).
 */
public class NarcoticArrow extends TranqDart {
    /** Potency of a full-strength shot (velocity 3, the vanilla bow's full draw). */
    public static final float FULL_POTENCY = 2.2F;

    public NarcoticArrow(EntityType<? extends NarcoticArrow> type, Level level) {
        super(type, level);
        this.setBaseDamage(1.0D);
    }

    public NarcoticArrow(Level level, LivingEntity shooter) {
        super(ModEntities.NARCOTIC_ARROW.get(), level, shooter);
        this.setBaseDamage(1.0D);
    }

    @Override
    public void shoot(double x, double y, double z, float velocity, float inaccuracy) {
        super.shoot(x, y, z, velocity, inaccuracy);
        this.setPotency(FULL_POTENCY * Mth.clamp(velocity / 3.0F, 0.25F, 1.0F));
    }

    @Override
    protected ItemStack getPickupItem() {
        return new ItemStack(ModItems.NARCOTIC_ARROW.get());
    }
}
