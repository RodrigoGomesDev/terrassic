package com.terrassic.item;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * The hunting bow (docs/ARMAS.md): a sinew-backed recurve. Same hands and pose as the vanilla bow, but a heavier
 * draw: 25 ticks to full, and a full draw flies faster (3.3) and hits harder (+1 damage). Takes any arrow; the
 * narcotic arrow is its reason to exist. Draw frames come from the "pull"/"pulling" properties (client/WeaponPoses).
 */
public class HuntingBowItem extends BowItem {
    public static final int FULL_DRAW = 25;

    public HuntingBowItem(Properties properties) {
        super(properties);
    }

    /** 0..1 like BowItem.getPowerForTime, over the longer draw. */
    public static float power(int ticksUsed) {
        float f = (float) ticksUsed / FULL_DRAW;
        f = (f * f + f * 2.0F) / 3.0F;
        return Math.min(f, 1.0F);
    }

    @Override
    public void releaseUsing(ItemStack bow, Level level, LivingEntity user, int remaining) {
        if (!(user instanceof Player player)) {
            return;
        }
        ItemStack ammo = player.getProjectile(bow);
        if (ammo.isEmpty()) {
            return;
        }
        float power = power(this.getUseDuration(bow, user) - remaining);
        if (power < 0.1F) {
            return;
        }
        List<ItemStack> shots = draw(bow, ammo, player);
        if (level instanceof ServerLevel server && !shots.isEmpty()) {
            this.shoot(server, player, player.getUsedItemHand(), bow, shots, power * 3.3F, 0.8F, power == 1.0F, null);
        }
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.ARROW_SHOOT, SoundSource.PLAYERS,
                1.0F, 0.75F / (level.getRandom().nextFloat() * 0.4F + 1.2F) + power * 0.5F);
        player.awardStat(Stats.ITEM_USED.get(this));
    }

    @Override
    protected Projectile createProjectile(Level level, LivingEntity shooter, ItemStack bow, ItemStack ammo, boolean crit) {
        Projectile shot = super.createProjectile(level, shooter, bow, ammo, crit);
        if (shot instanceof AbstractArrow arrow) {
            arrow.setBaseDamage(arrow.getBaseDamage() + 1.0D);
        }
        return shot;
    }

    @Override
    public int getDefaultProjectileRange() {
        return 18;
    }
}
