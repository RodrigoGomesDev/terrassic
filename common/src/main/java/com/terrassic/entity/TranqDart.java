package com.terrassic.entity;

import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.ItemSupplier;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;

/**
 * A narcotic dart shot from the blowgun (knockout taming, docs/DOMESTICACAO.md). It barely wounds: what it carries
 * is torpor. A wild creature fills its torpor gauge until it collapses; one already knocked out is kept asleep
 * without being hurt (darts do not spoil the taming effectiveness). Picked up again like an arrow.
 */
public class TranqDart extends AbstractArrow implements ItemSupplier {
    /** Torpor a dart adds: a flat dose plus a share of the target's gauge, so the giants still need a volley. */
    public static final float TORPOR_FLAT = 14.0F;
    public static final float TORPOR_SHARE = 0.06F;

    public TranqDart(EntityType<? extends TranqDart> type, Level level) {
        super(type, level);
        this.setBaseDamage(0.5D);
    }

    public TranqDart(Level level, LivingEntity shooter) {
        super(ModEntities.TRANQ_DART.get(), shooter, level);
        this.setBaseDamage(0.5D);
    }

    /** The dose this dart gives a creature with the given torpor gauge. */
    public static float dose(float maxTorpor) {
        return TORPOR_FLAT + maxTorpor * TORPOR_SHARE;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        Entity target = result.getEntity();
        if (target instanceof DinosaurEntity dino && dino.isKnockedOut()) {
            // keeps it asleep without a wound
            if (!this.level().isClientSide()) {
                dino.addTorpor(dose(dino.maxTorpor()), this.getOwner());
                this.playSound(SoundEvents.ARROW_HIT, 0.6F, 1.6F);
                if (this.pickup == Pickup.ALLOWED) {
                    this.spawnAtLocation(this.getPickupItem(), 0.1F);
                }
                this.discard();
            }
            return;
        }
        super.onHitEntity(result);
        if (!this.level().isClientSide() && target instanceof DinosaurEntity dino && dino.isAlive()) {
            dino.addTorpor(dose(dino.maxTorpor()), this.getOwner());
        }
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return SoundEvents.ARROW_HIT;
    }

    @Override
    protected ItemStack getPickupItem() {
        return new ItemStack(ModItems.TRANQ_DART.get());
    }

    @Override
    public ItemStack getItem() {
        return new ItemStack(ModItems.TRANQ_DART.get());
    }
}
