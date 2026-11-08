package com.terrassic.effect;

import com.terrassic.Terrassic;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;

/**
 * Bleeding (1.10.1, the Carcharodontosaurus' tearing bite; docs/estudos/13, Rodrigo's answer: a real mechanic, simple and
 * fair to players). The blade teeth cut: the victim loses one point of health a second (amplifier 1: one and a half),
 * for as long as the effect lasts (the bite gives a few seconds). Fair to players: it never takes a player below one
 * heart by itself (the bite kills, the bleeding does not), and milk ends it like any effect. Damage type
 * terrassic:bleeding (data/terrassic/damage_type): no knockback, through armour (it is a wound, not a blow).
 */
public class BleedingEffect extends MobEffect {
    public static final ResourceKey<DamageType> DAMAGE = ResourceKey.create(Registries.DAMAGE_TYPE, Terrassic.id("bleeding"));
    /** Ticks between two losses. */
    private static final int EVERY = 20;
    /** A player keeps at least this much health against the bleeding alone (one heart). */
    private static final float PLAYER_FLOOR = 2.0F;

    public BleedingEffect() {
        super(MobEffectCategory.HARMFUL, 0x9a1f1f);
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        return duration % EVERY == 0;
    }

    @Override
    public void applyEffectTick(LivingEntity entity, int amplifier) {
        if (entity.level().isClientSide() || !entity.isAlive()) {
            return;
        }
        float amount = 1.0F + 0.5F * amplifier;
        if (entity instanceof Player) {
            amount = Math.min(amount, entity.getHealth() - PLAYER_FLOOR);
            if (amount <= 0.0F) {
                return;
            }
        }
        // the cut bleeds through the hurt cooldown of the last blow, but leaves the next blow its own cooldown
        int cooldown = entity.invulnerableTime;
        entity.invulnerableTime = 0;
        entity.hurt(source(entity), amount);
        entity.invulnerableTime = Math.min(entity.invulnerableTime, cooldown);
    }

    public static DamageSource source(LivingEntity entity) {
        return new DamageSource(entity.level().registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(DAMAGE));
    }
}
