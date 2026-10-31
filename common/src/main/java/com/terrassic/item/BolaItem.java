package com.terrassic.item;

import com.terrassic.entity.ThrownBola;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

/**
 * The bola (v1.1, docs/ARMAS.md): hold use to swing it over the head (the trident's raised pose, a whoosh per turn),
 * release to throw. A full second of swinging throws it about 20 blocks; a short swing drops it a few blocks ahead.
 * What it does to the animal it hits is in {@link ThrownBola}.
 */
public class BolaItem extends Item {
    /** Ticks of swinging for a full-strength throw. */
    public static final int FULL_SWING = 20;
    /** Below this a release is a fumble: nothing is thrown. */
    private static final int MIN_SWING = 4;

    public BolaItem(Properties properties) {
        super(properties);
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.SPEAR;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return 72000;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(player.getItemInHand(hand));
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
        int used = this.getUseDuration(stack) - remaining;
        // one whoosh per turn of the thongs, quicker and higher as the swing builds
        if (!level.isClientSide() && used > 0 && used % (used < FULL_SWING ? 8 : 6) == 0) {
            float swing = Mth.clamp((float) used / FULL_SWING, 0.0F, 1.0F);
            level.playSound(null, user.getX(), user.getEyeY(), user.getZ(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS,
                    0.25F, 1.4F + 0.4F * swing);
        }
    }

    @Override
    public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int remaining) {
        if (!(user instanceof Player player)) {
            return;
        }
        int used = this.getUseDuration(stack) - remaining;
        if (used < MIN_SWING) {
            return;
        }
        float swing = Mth.clamp((float) used / FULL_SWING, 0.0F, 1.0F);
        if (!level.isClientSide()) {
            ThrownBola bola = new ThrownBola(level, player);
            ItemStack one = stack.copy();
            one.setCount(1);
            bola.setItem(one);
            bola.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 0.9F + 0.9F * swing, 1.0F);
            level.addFreshEntity(bola);
        }
        level.playSound(null, player.getX(), player.getEyeY(), player.getZ(), SoundEvents.TRIDENT_THROW, SoundSource.PLAYERS,
                0.6F, 1.3F);
        if (!player.getAbilities().instabuild) {
            stack.shrink(1);
        }
        player.getCooldowns().addCooldown(this, 20);
        player.awardStat(Stats.ITEM_USED.get(this));
    }
}
