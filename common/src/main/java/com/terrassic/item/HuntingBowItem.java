package com.terrassic.item;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ArrowItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.Level;

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
        boolean infinite = player.getAbilities().instabuild || EnchantmentHelper.getItemEnchantmentLevel(Enchantments.INFINITY_ARROWS, bow) > 0;
        ItemStack ammo = player.getProjectile(bow);
        if (ammo.isEmpty() && !infinite) {
            return;
        }
        if (ammo.isEmpty()) {
            ammo = new ItemStack(Items.ARROW);
        }
        float power = power(this.getUseDuration(bow) - remaining);
        if (power < 0.1F) {
            return;
        }
        boolean free = infinite && ammo.is(Items.ARROW);
        if (!level.isClientSide()) {
            ArrowItem arrowItem = (ArrowItem) (ammo.getItem() instanceof ArrowItem ? ammo.getItem() : Items.ARROW);
            AbstractArrow arrow = arrowItem.createArrow(level, ammo, player);
            arrow.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, power * 3.3F, 0.8F);
            arrow.setBaseDamage(arrow.getBaseDamage() + 1.0D);
            if (power == 1.0F) {
                arrow.setCritArrow(true);
            }
            int powerLevel = EnchantmentHelper.getItemEnchantmentLevel(Enchantments.POWER_ARROWS, bow);
            if (powerLevel > 0) {
                arrow.setBaseDamage(arrow.getBaseDamage() + powerLevel * 0.5D + 0.5D);
            }
            int punch = EnchantmentHelper.getItemEnchantmentLevel(Enchantments.PUNCH_ARROWS, bow);
            if (punch > 0) {
                arrow.setKnockback(punch);
            }
            if (EnchantmentHelper.getItemEnchantmentLevel(Enchantments.FLAMING_ARROWS, bow) > 0) {
                arrow.setSecondsOnFire(100);
            }
            bow.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(player.getUsedItemHand()));
            if (free || player.getAbilities().instabuild && (ammo.is(Items.SPECTRAL_ARROW) || ammo.is(Items.TIPPED_ARROW))) {
                arrow.pickup = AbstractArrow.Pickup.CREATIVE_ONLY;
            }
            level.addFreshEntity(arrow);
        }
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.ARROW_SHOOT, SoundSource.PLAYERS,
                1.0F, 0.75F / (level.getRandom().nextFloat() * 0.4F + 1.2F) + power * 0.5F);
        if (!free && !player.getAbilities().instabuild) {
            ammo.shrink(1);
            if (ammo.isEmpty()) {
                player.getInventory().removeItem(ammo);
            }
        }
        player.awardStat(Stats.ITEM_USED.get(this));
    }

    @Override
    public int getDefaultProjectileRange() {
        return 18;
    }
}
