package com.terrassic.block;

import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Bone wind chimes: now and then the wind knocks the bones together (a soft, random xylophone note).
 */
public class ChimesBlock extends FacingBlock {
    public ChimesBlock(Properties properties, double[][] northBoxes) {
        super(properties, northBoxes);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(level.isRaining() ? 15 : 45) == 0) {
            level.playLocalSound(pos.getX() + 0.5D, pos.getY() + 0.5D, pos.getZ() + 0.5D,
                    SoundEvents.NOTE_BLOCK_XYLOPHONE.value(), SoundSource.BLOCKS, 0.35F, 0.5F + random.nextFloat() * 1.5F,
                    false);
        }
    }
}
