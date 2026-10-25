package com.terrassic.item;

import com.terrassic.entity.TranqDart;
import com.terrassic.registry.ModItems;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ProjectileWeaponItem;
import net.minecraft.world.level.Level;

import java.util.function.Predicate;

/**
 * The reed blowgun (knockout taming, docs/DOMESTICACAO.md): one puff, one narcotic dart, no draw time. Takes
 * darts from the off hand first, then from the inventory, like the bow takes arrows; creative players shoot for free.
 */
public class BlowgunItem extends ProjectileWeaponItem {
    private static final Predicate<ItemStack> DARTS = stack -> stack.is(ModItems.TRANQ_DART.get());

    public BlowgunItem(Properties properties) {
        super(properties);
    }

    @Override
    public Predicate<ItemStack> getAllSupportedProjectiles() {
        return DARTS;
    }

    @Override
    public int getDefaultProjectileRange() {
        return 20;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack blowgun = player.getItemInHand(hand);
        ItemStack dart = player.getProjectile(blowgun);
        boolean free = player.getAbilities().instabuild;
        if (dart.isEmpty() && !free) {
            return InteractionResultHolder.fail(blowgun);
        }
        if (!level.isClientSide()) {
            TranqDart shot = new TranqDart(level, player);
            shot.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 2.4F, 0.8F);
            shot.pickup = free ? AbstractArrow.Pickup.CREATIVE_ONLY : AbstractArrow.Pickup.ALLOWED;
            level.addFreshEntity(shot);
            blowgun.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(hand));
        }
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.LLAMA_SPIT, SoundSource.PLAYERS,
                0.7F, 1.6F + level.getRandom().nextFloat() * 0.2F);
        if (!free) {
            dart.shrink(1);
            if (dart.isEmpty()) {
                player.getInventory().removeItem(dart);
            }
        }
        player.getCooldowns().addCooldown(this, 16);
        player.awardStat(Stats.ITEM_USED.get(this));
        return InteractionResultHolder.sidedSuccess(blowgun, level.isClientSide());
    }
}
