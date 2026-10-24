package com.terrassic.item;

import com.terrassic.registry.ModSounds;
import com.terrassic.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.Map;

/**
 * Clay Jar: the scientist's sample flask.
 * <ul>
 *   <li>Used on a spruce or jungle log (the resin trees), it taps the resin: the jar becomes a Jar of Resin and the
 *       log is left stripped, so each log gives resin once. A Jar of Resin is crafted into Raw Amber (the jar comes
 *       back).</li>
 *   <li>Carried in the inventory, an empty jar is filled with a Blood Sample when its owner defeats a dinosaur
 *       (see Research). Samples are studied at the Research Table.</li>
 * </ul>
 */
public class ClayJarItem extends Item {
    /** Resin trees: conifers (spruce) and the tropical trees that made Dominican amber (jungle). */
    private static final Map<Block, Block> TAPPED = Map.of(
            Blocks.SPRUCE_LOG, Blocks.STRIPPED_SPRUCE_LOG, Blocks.SPRUCE_WOOD, Blocks.STRIPPED_SPRUCE_WOOD,
            Blocks.JUNGLE_LOG, Blocks.STRIPPED_JUNGLE_LOG, Blocks.JUNGLE_WOOD, Blocks.STRIPPED_JUNGLE_WOOD);

    public ClayJarItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos();
        BlockState state = level.getBlockState(pos);
        Player player = context.getPlayer();
        Block tapped = TAPPED.get(state.getBlock());
        if (tapped == null) {
            if (player != null && !level.isClientSide() && state.is(net.minecraft.tags.BlockTags.LOGS)) {
                player.displayClientMessage(Component.translatable("message.terrassic.no_resin"), true);
            }
            return InteractionResult.PASS;
        }
        if (!level.isClientSide()) {
            BlockState stripped = tapped.defaultBlockState();
            if (state.hasProperty(RotatedPillarBlock.AXIS)) {
                stripped = stripped.setValue(RotatedPillarBlock.AXIS, state.getValue(RotatedPillarBlock.AXIS));
            }
            level.setBlock(pos, stripped, Block.UPDATE_ALL_IMMEDIATE);
            level.playSound(null, pos, ModSounds.SFX_CLAY_JAR.get(), SoundSource.BLOCKS, 1.0F, 0.8F);
            ItemStack stack = context.getItemInHand();
            ItemStack resin = new ItemStack(ModItems.RESIN_JAR.get());
            if (player == null || !player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            if (player != null && !player.getInventory().add(resin)) {
                player.drop(resin, false);
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }
}
