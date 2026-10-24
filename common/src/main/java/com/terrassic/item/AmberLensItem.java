package com.terrassic.item;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.research.Knowledge;
import com.terrassic.research.Research;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUtils;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Amber Lens: a spyglass made of polished amber (zoom and overlay come from the vanilla spyglass, see
 * {@code mixin.PlayerMixin}). Keeping a dinosaur in view for {@link #OBSERVE_TICKS} ticks, up to {@link #RANGE}
 * blocks away, records it as "sighted" in the Field Guide, so far-away or dangerous animals can be logged
 * without walking up to them.
 */
public class AmberLensItem extends Item {
    public static final double RANGE = 64.0D;
    public static final int OBSERVE_TICKS = 40;
    private static final int USE_DURATION = 1200;
    /** Server side: player -> {entity id being observed, ticks}. Kept off the item so its NBT does not change mid-use. */
    private static final Map<UUID, int[]> OBSERVING = new HashMap<>();

    public AmberLensItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        player.playSound(SoundEvents.SPYGLASS_USE, 1.0F, 1.0F);
        player.awardStat(Stats.ITEM_USED.get(this));
        return ItemUtils.startUsingInstantly(level, player, hand);
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.SPYGLASS;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return USE_DURATION;
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remainingTicks) {
        if (!(user instanceof ServerPlayer player)) {
            return;
        }
        DinosaurEntity target = lookedAt(player);
        int[] obs = OBSERVING.computeIfAbsent(player.getUUID(), u -> new int[]{-1, 0});
        if (target == null || target.getId() != obs[0]) {
            obs[0] = target == null ? -1 : target.getId();
            obs[1] = 0;
            return;
        }
        if (++obs[1] == OBSERVE_TICKS) {
            boolean known = Research.level(player, target.speciesId()) >= Knowledge.SIGHTED;
            Research.sighted(player, target);
            Research.award(player, "journal/amber_lens");
            if (known) {
                player.displayClientMessage(Component.translatable("message.terrassic.lens_seen", target.getType().getDescription(),
                        (int) Math.round(player.distanceTo(target))), true);
            }
        }
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity user) {
        this.releaseUsing(stack, level, user, 0);
        return stack;
    }

    @Override
    public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int remainingTicks) {
        user.playSound(SoundEvents.SPYGLASS_STOP_USING, 1.0F, 1.0F);
        OBSERVING.remove(user.getUUID());
    }

    /** The dinosaur in the centre of the view, within range and in line of sight, or null. */
    private static DinosaurEntity lookedAt(Player player) {
        Vec3 eye = player.getEyePosition();
        Vec3 look = player.getViewVector(1.0F);
        Vec3 end = eye.add(look.scale(RANGE));
        AABB box = player.getBoundingBox().expandTowards(look.scale(RANGE)).inflate(1.0D);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, box,
                e -> e instanceof DinosaurEntity && !e.isSpectator(), RANGE * RANGE);
        return hit != null && hit.getEntity() instanceof DinosaurEntity dino && player.hasLineOfSight(dino) ? dino : null;
    }
}
