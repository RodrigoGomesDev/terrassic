package com.terrassic.entity;

import com.terrassic.registry.ModEntities;
import com.terrassic.registry.ModItems;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

/**
 * A thrown bola (v1.1, docs/ARMAS.md, rules approved by Rodrigo on 31/10/2026). It wounds nothing; it ties.
 * <ul>
 *   <li>A flyer in the air has its wings bound: it stops flying and drops, with no fall damage, and stays down
 *       {@link #FLYER_TICKS}. A rider comes down with it.</li>
 *   <li>Any other animal of the mod has its legs bound for {@link #GROUND_TICKS}: it can neither move nor fight.</li>
 *   <li>Giants (table health over 120: T. rex, Spinosaurus, the sauropods...) snap the thongs at once, and a swimmer
 *       in the water slips them.</li>
 *   <li>A player (PvP on) or a vanilla mob is slowed hard for a few seconds.</li>
 *   <li>Never the thrower's own animals, nor another player's while PvP is off.</li>
 * </ul>
 * A bola that misses falls where it lands. One that caught something drops when the animal frees itself, half of the
 * times (the other half the thongs broke).
 */
public class ThrownBola extends ThrowableItemProjectile {
    public static final int FLYER_TICKS = 160;
    public static final int GROUND_TICKS = 120;
    private static final int PLAYER_TICKS = 60;

    public ThrownBola(EntityType<? extends ThrownBola> type, Level level) {
        super(type, level);
    }

    public ThrownBola(Level level, LivingEntity thrower) {
        super(ModEntities.BOLA.get(), thrower, level);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.BOLA.get();
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (this.level().isClientSide()) {
            return;
        }
        Entity target = com.terrassic.entity.parts.DinoParts.owner(result.getEntity());   // 1.7: a hit part's creature
        Entity thrower = this.getOwner();
        if (target instanceof DinosaurEntity dino) {
            if (!mayTie(dino, thrower)) {
                this.dropBola();
            } else if (isGiant(dino)) {
                this.snap(dino);
            } else {
                dino.entangle(dino instanceof FlyingDinosaur flyer && flyer.isFlying() ? FLYER_TICKS : GROUND_TICKS);
                dino.hurt(this.damageSources().thrown(this, thrower), 0.0F);
                this.puff(target);
            }
        } else if (target instanceof Player player) {
            if (thrower instanceof Player p && (p == player || !p.canHarmPlayer(player))) {
                this.dropBola();
                return;
            }
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, PLAYER_TICKS, 4), thrower);
            player.hurt(this.damageSources().thrown(this, thrower), 0.0F);
            this.puff(target);
            this.maybeDrop();
        } else if (target instanceof LivingEntity living) {
            living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, GROUND_TICKS, 4), thrower);
            living.hurt(this.damageSources().thrown(this, thrower), 0.0F);
            this.puff(target);
            this.maybeDrop();
        } else {
            this.dropBola();
        }
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (!this.level().isClientSide()) {
            if (result.getType() == HitResult.Type.BLOCK) {
                this.dropBola();
            }
            this.discard();
        }
    }

    /** Not the thrower's own animals; another player's only with PvP on; nothing already down or in the water. */
    private static boolean mayTie(DinosaurEntity dino, Entity thrower) {
        if (dino.isKnockedOut() || dino.isEntangled() || dino instanceof SwimmingDinosaur && dino.isInWater()) {
            return false;
        }
        if (dino.isTame()) {
            if (thrower != null && thrower.getUUID().equals(dino.getOwnerUUID())) {
                return false;
            }
            return dino.level().getServer() != null && dino.level().getServer().isPvpAllowed();
        }
        return true;
    }

    /** The big ones: table health over 120 (KillXp's giant and colossal classes); their young can still be tied. */
    public static boolean isGiant(DinosaurEntity dino) {
        return !dino.isBaby() && KillXp.size(dino.getType()) >= 50.0F;
    }

    private void snap(DinosaurEntity dino) {
        this.playSound(SoundEvents.LEASH_KNOT_BREAK, 1.0F, 0.8F);
        this.crumbs();
    }

    private void puff(Entity target) {
        target.playSound(SoundEvents.LEASH_KNOT_PLACE, 1.0F, 0.9F);
        if (this.level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.POOF, target.getX(), target.getY() + target.getBbHeight() * 0.4D, target.getZ(),
                    6, target.getBbWidth() * 0.3D, 0.2D, target.getBbWidth() * 0.3D, 0.02D);
        }
    }

    private void crumbs() {
        if (this.level() instanceof ServerLevel server) {
            server.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, this.getItem()), this.getX(), this.getY(), this.getZ(),
                    8, 0.2D, 0.2D, 0.2D, 0.08D);
        }
    }

    private void maybeDrop() {
        if (this.random.nextBoolean()) {
            this.dropBola();
        } else {
            this.crumbs();
        }
    }

    private void dropBola() {
        ItemStack stack = this.getItem().isEmpty() ? new ItemStack(ModItems.BOLA.get()) : this.getItem().copy();
        stack.setCount(1);
        this.spawnAtLocation(stack, 0.1F);
    }
}
