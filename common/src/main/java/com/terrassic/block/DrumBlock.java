package com.terrassic.block;

import com.terrassic.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/**
 * Hide drum: right click to beat it (a deep drum note, a little higher or lower each beat).
 */
public class DrumBlock extends FacingBlock {
    public DrumBlock(Properties properties, double[][] northBoxes) {
        super(properties, northBoxes);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        float pitch = 0.6F + level.getRandom().nextFloat() * 0.4F;
        level.playSound(player, pos, ModSounds.SFX_DRUM.get(), SoundSource.RECORDS, 2.0F, pitch);
        if (level.isClientSide()) {
            level.addParticle(ParticleTypes.NOTE, pos.getX() + 0.5D, pos.getY() + 0.9D, pos.getZ() + 0.5D,
                    pitch - 0.6D, 0.0D, 0.0D);
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }
}
