package com.terrassic.entity;

import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;

/**
 * A narcotic dart shot from the blowgun (knockout taming, docs/DOMESTICACAO.md). It barely wounds: what it carries
 * is torpor. A wild creature fills its torpor gauge until it collapses; one already knocked out is kept asleep
 * without being hurt (darts do not spoil the taming effectiveness). A full breath gives it more potency. Drawn as a
 * small arrow (client/PrimitiveArrowRenderer) and picked up again like one; in a creature it stays stuck for a while
 * (v1.1.4, client/StuckProjectilesLayer).
 */
public class TranqDart extends AbstractArrow {
    /** Torpor a dart adds: a flat dose plus a share of the target's gauge, so the giants still need a volley. */
    public static final float TORPOR_FLAT = 16.0F;
    public static final float TORPOR_SHARE = 0.06F;
    private static final ColorParticleOption SWIRL = ColorParticleOption.create(ParticleTypes.ENTITY_EFFECT, 0.62F, 0.42F, 0.92F);

    /** Dose multiplier: 1 for a quick puff, up to 1.5 for a full breath (item/BlowgunItem). */
    private float potency = 1.0F;

    public TranqDart(EntityType<? extends TranqDart> type, Level level) {
        super(type, level);
        this.setBaseDamage(0.5D);
    }

    public TranqDart(Level level, LivingEntity shooter) {
        this(ModEntities.TRANQ_DART.get(), level, shooter, new ItemStack(ModItems.TRANQ_DART.get()), null);
    }

    protected TranqDart(EntityType<? extends TranqDart> type, Level level, LivingEntity shooter, ItemStack pickup, ItemStack weapon) {
        super(type, shooter, level, pickup, weapon);
        this.setBaseDamage(0.5D);
    }

    public void setPotency(float potency) {
        this.potency = potency;
    }

    /** The dose this dart gives a creature with the given torpor gauge. */
    public float dose(float maxTorpor) {
        return (TORPOR_FLAT + maxTorpor * TORPOR_SHARE) * this.potency;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        Entity target = result.getEntity();
        if (target instanceof DinosaurEntity dino && dino.isKnockedOut()) {
            // keeps it asleep without a wound
            if (!this.level().isClientSide()) {
                dino.addTorpor(this.dose(dino.maxTorpor()) * dino.narcoticEffect(), this.getOwner());
                this.dosed(dino);
                if (this.pickup == Pickup.ALLOWED) {
                    this.spawnAtLocation(this.getPickupItem(), 0.1F);
                }
                this.discard();
            }
            return;
        }
        // Awake targets receive the dose in DinosaurEntity.hurt, after the engine accepts the hit.
        super.onHitEntity(result);
    }

    @Override
    protected void doPostHurtEffects(LivingEntity target) {
        super.doPostHurtEffects(target);
        if (target instanceof DinosaurEntity dino && !this.level().isClientSide()) {
            if (this.getPierceLevel() <= 0 && target.getArrowCount() > 0) {
                // the engine counted it as an arrow; a dart is drawn as a dart (client/StuckProjectilesLayer)
                target.setArrowCount(target.getArrowCount() - 1);
                this.stickInto(dino);
            }
            if (!dino.isTame()) {
                this.dosed(dino);
            }
        }
    }

    /** Hit a creature while it was still invulnerable from the last blow: DinosaurEntity#hurt gave the dose anyway,
     *  and the dart stays in instead of bouncing off (v1.1.4). */
    public void dosedThroughInvulnerability(DinosaurEntity dino) {
        this.dosed(dino);
        this.stickInto(dino);
        this.pickup = Pickup.DISALLOWED;
        this.discard();
    }

    /** Leaves the dart visibly stuck in the hide (v1.1.4): a dart as a dart; the narcotic arrow as an arrow. */
    protected void stickInto(DinosaurEntity dino) {
        dino.addStuckDart();
    }

    /** Lets the shooter see and hear that the narcotic went in: a puff of drowsy swirls and a soft tick. */
    private void dosed(DinosaurEntity dino) {
        if (this.level() instanceof ServerLevel server) {
            // v1.1.4: twice as many swirls, a little brighter, and a few witch sparkles, so the hit reads at range
            int swirls = 16 + (int) Math.min(16.0F, dino.getBbWidth() * 4.0F);
            for (int i = 0; i < swirls; i++) {
                double x = dino.getX() + (this.random.nextDouble() - 0.5D) * dino.getBbWidth() * 1.2D;
                double y = dino.getY() + dino.getBbHeight() * (0.5D + this.random.nextDouble() * 0.7D);
                double z = dino.getZ() + (this.random.nextDouble() - 0.5D) * dino.getBbWidth() * 1.2D;
                // the swirl's colour is a dusky violet, the sleep herb's
                server.sendParticles(SWIRL, x, y, z, 1, 0.0D, 0.0D, 0.0D, 1.0D);
            }
            server.sendParticles(ParticleTypes.WITCH, dino.getX(), dino.getY() + dino.getBbHeight() * 0.9D, dino.getZ(),
                    6 + (int) Math.min(6.0F, dino.getBbWidth() * 2.0F), dino.getBbWidth() * 0.35D, dino.getBbHeight() * 0.2D,
                    dino.getBbWidth() * 0.35D, 0.05D);
        }
        this.playSound(SoundEvents.ARROW_HIT, 0.6F, 1.6F);
        if (this.getOwner() instanceof Player shooter) {
            this.level().playSound(null, shooter.getX(), shooter.getEyeY(), shooter.getZ(), SoundEvents.AMETHYST_BLOCK_HIT,
                    SoundSource.PLAYERS, 0.5F, 1.4F + 0.6F * dino.getTorpor() / dino.maxTorpor());
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putFloat("Potency", this.potency);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Potency")) {
            this.potency = tag.getFloat("Potency");
        }
    }

    @Override
    protected SoundEvent getDefaultHitGroundSoundEvent() {
        return SoundEvents.ARROW_HIT;
    }

    @Override
    protected ItemStack getDefaultPickupItem() {
        return new ItemStack(ModItems.TRANQ_DART.get());
    }
}
