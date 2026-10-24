package com.terrassic.item;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.registry.ModItems;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Sketching Charcoal: hold right click while looking at a dinosaur (up to {@link #RANGE} blocks away) for
 * {@link #SKETCH_TICKS} ticks to draw it. Gives a Sketch of that species, studied at the Research Table.
 */
public class SketchCharcoalItem extends Item {
    public static final double RANGE = 16.0D;
    public static final int SKETCH_TICKS = 60;
    private static final int USE_DURATION = 72000;

    public SketchCharcoalItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (lookedAt(player) == null) {
            return InteractionResultHolder.pass(stack);
        }
        player.startUsingItem(hand);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.BRUSH;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return USE_DURATION;
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remainingTicks) {
        if (!(user instanceof Player player) || level.isClientSide()) {
            return;
        }
        int used = USE_DURATION - remainingTicks + 1;
        if (used % 10 != 0) {
            return;
        }
        DinosaurEntity target = lookedAt(player);
        if (target == null) {
            player.displayClientMessage(Component.translatable("message.terrassic.sketch_lost"), true);
            user.releaseUsingItem();
            return;
        }
        level.playSound(null, player.blockPosition(), SoundEvents.VILLAGER_WORK_CARTOGRAPHER, SoundSource.PLAYERS, 0.5F, 1.4F);
        if (used >= SKETCH_TICKS) {
            ItemStack sketch = SketchItem.of(ModItems.SKETCH.get(), target.speciesId());
            if (!player.getInventory().add(sketch)) {
                player.drop(sketch, false);
            }
            player.displayClientMessage(Component.translatable("message.terrassic.sketch_done", target.getType().getDescription()), true);
            stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(p.getUsedItemHand()));
            user.releaseUsingItem();
        }
    }

    /** The dinosaur the player is looking at, within range, or null. */
    private static DinosaurEntity lookedAt(Player player) {
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getViewVector(1.0F).scale(RANGE));
        AABB box = player.getBoundingBox().expandTowards(player.getViewVector(1.0F).scale(RANGE)).inflate(1.0D);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, box,
                e -> e instanceof DinosaurEntity && !e.isSpectator(), RANGE * RANGE);
        return hit != null && hit.getEntity() instanceof DinosaurEntity dino && player.hasLineOfSight(dino) ? dino : null;
    }
}
