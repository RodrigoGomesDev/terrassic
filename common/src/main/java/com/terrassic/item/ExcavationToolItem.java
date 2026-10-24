package com.terrassic.item;

import com.terrassic.registry.ModBlocks;
import com.terrassic.registry.ModItems;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;

/**
 * Hair Brush and Flint Chisel: hold right click on fossil rock to dig a fossil out, like the vanilla brush on
 * suspicious sand. The brush is slow and never breaks the fossil; the chisel is fast but sometimes the fossil
 * cracks and only a bone comes out. The rock turns into stone either way.
 */
public class ExcavationToolItem extends Item {
    private static final int USE_DURATION = 200;

    private final int workTicks;
    private final float breakChance;

    public ExcavationToolItem(int workTicks, float breakChance, Properties properties) {
        super(properties);
        this.workTicks = workTicks;
        this.breakChance = breakChance;
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Player player = context.getPlayer();
        if (player != null && context.getLevel().getBlockState(context.getClickedPos()).is(ModBlocks.FOSSIL_ROCK.get())) {
            player.startUsingItem(context.getHand());
            return InteractionResult.CONSUME;
        }
        return InteractionResult.PASS;
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
        if (!(user instanceof Player player)) {
            user.releaseUsingItem();
            return;
        }
        HitResult hit = player.pick(5.0D, 0.0F, false);
        if (!(hit instanceof BlockHitResult blockHit) || hit.getType() != HitResult.Type.BLOCK) {
            user.releaseUsingItem();
            return;
        }
        BlockPos pos = blockHit.getBlockPos();
        BlockState state = level.getBlockState(pos);
        if (!state.is(ModBlocks.FOSSIL_ROCK.get())) {
            user.releaseUsingItem();
            return;
        }
        int used = USE_DURATION - remainingTicks + 1;
        if (level.isClientSide()) {
            return;
        }
        if (used % 5 == 0) {
            level.playSound(null, pos, SoundEvents.BRUSH_GRAVEL, SoundSource.BLOCKS, 0.8F, 1.0F);
            ((ServerLevel) level).sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state),
                    blockHit.getLocation().x, blockHit.getLocation().y, blockHit.getLocation().z, 4, 0.1D, 0.1D, 0.1D, 0.0D);
        }
        if (used >= this.workTicks) {
            excavate(level, pos, player);
            stack.hurtAndBreak(1, player, p -> p.broadcastBreakEvent(p.getUsedItemHand()));
            user.releaseUsingItem();
        }
    }

    private void excavate(Level level, BlockPos pos, Player player) {
        level.setBlock(pos, Blocks.STONE.defaultBlockState(), Block.UPDATE_ALL);
        level.playSound(null, pos, SoundEvents.BRUSH_GRAVEL_COMPLETED, SoundSource.BLOCKS, 1.0F, 1.0F);
        if (level.random.nextFloat() < this.breakChance) {
            Block.popResource(level, pos, new ItemStack(Items.BONE));
            player.displayClientMessage(Component.translatable("message.terrassic.fossil_broke"), true);
            return;
        }
        Block.popResource(level, pos, new ItemStack(ModItems.randomFossil(level.random)));
        if (player instanceof ServerPlayer sp) {
            Research.objective(sp, Objective.FIRST_FOSSIL);
        }
    }
}
