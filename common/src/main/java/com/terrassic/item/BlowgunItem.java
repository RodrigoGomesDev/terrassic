package com.terrassic.item;

import com.terrassic.entity.TranqDart;
import com.terrassic.registry.ModItems;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ProjectileWeaponItem;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

import java.util.function.Predicate;

/**
 * The reed blowgun (knockout taming, docs/DOMESTICACAO.md). Hold use to raise it to the lips and fill the lungs
 * (the goat horn pose; the first-person tube swings to the centre through the "terrassic:blowing" model override),
 * release to blow. A full breath (one second) shoots straighter, farther and with half again the dart's dose; a
 * quick puff still works at short range. Takes darts from the off hand first, then from the inventory, like the
 * bow takes arrows; creative players shoot for free.
 */
public class BlowgunItem extends ProjectileWeaponItem {
    private static final Predicate<ItemStack> DARTS = stack -> stack.is(ModItems.TRANQ_DART.get());
    /** Ticks of held breath for a full-strength shot. */
    public static final int FULL_BREATH = 20;
    /** Below this a release is a fumble: nothing is shot. */
    private static final int MIN_BREATH = 3;

    public BlowgunItem(Properties properties) {
        super(properties);
    }

    @Override
    public Predicate<ItemStack> getAllSupportedProjectiles() {
        return DARTS;
    }

    @Override
    public int getDefaultProjectileRange() {
        return 24;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.TOOT_HORN;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return 72000;
    }

    /** 0..1: how full the lungs are after the given ticks of use. */
    public static float breath(int ticksUsed) {
        return Mth.clamp((float) ticksUsed / FULL_BREATH, 0.0F, 1.0F);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack blowgun = player.getItemInHand(hand);
        if (player.getProjectile(blowgun).isEmpty() && !player.getAbilities().instabuild) {
            return InteractionResultHolder.fail(blowgun);
        }
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(blowgun);
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
        // a soft cue when the lungs are full
        if (this.getUseDuration(stack) - remaining == FULL_BREATH && !level.isClientSide()) {
            level.playSound(null, user.getX(), user.getEyeY(), user.getZ(), SoundEvents.CROSSBOW_LOADING_END, SoundSource.PLAYERS,
                    0.35F, 1.7F);
        }
    }

    @Override
    public void releaseUsing(ItemStack blowgun, Level level, LivingEntity user, int remaining) {
        if (!(user instanceof Player player)) {
            return;
        }
        int used = this.getUseDuration(blowgun) - remaining;
        if (used < MIN_BREATH) {
            return;
        }
        ItemStack dart = player.getProjectile(blowgun);
        boolean free = player.getAbilities().instabuild;
        if (dart.isEmpty() && !free) {
            return;
        }
        float breath = breath(used);
        if (!level.isClientSide()) {
            TranqDart shot = new TranqDart(level, player);
            shot.setPotency(1.0F + 0.5F * breath);
            shot.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 1.4F + 1.6F * breath, 1.2F - 1.0F * breath);
            shot.pickup = free ? AbstractArrow.Pickup.CREATIVE_ONLY : AbstractArrow.Pickup.ALLOWED;
            level.addFreshEntity(shot);
            blowgun.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(player.getUsedItemHand()));
        }
        level.playSound(null, player.getX(), player.getEyeY(), player.getZ(), SoundEvents.LLAMA_SPIT, SoundSource.PLAYERS,
                0.4F + 0.5F * breath, 1.9F - 0.4F * breath + level.getRandom().nextFloat() * 0.1F);
        if (!free) {
            dart.shrink(1);
            if (dart.isEmpty()) {
                player.getInventory().removeItem(dart);
            }
        }
        player.getCooldowns().addCooldown(this, 8);
        player.awardStat(Stats.ITEM_USED.get(this));
    }
}
