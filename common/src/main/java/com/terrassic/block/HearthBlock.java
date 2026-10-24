package com.terrassic.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Stone ring hearth: an open fire that never goes out. Burns what stands in it, crackles, gives smoke and sparks.
 */
public class HearthBlock extends FacingBlock {
    public HearthBlock(Properties properties, double[][] northBoxes) {
        super(properties, northBoxes);
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (entity instanceof LivingEntity && !entity.fireImmune()) {
            entity.hurt(level.damageSources().inFire(), 1.0F);
        }
        super.entityInside(state, level, pos, entity);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        double x = pos.getX() + 0.5D, y = pos.getY(), z = pos.getZ() + 0.5D;
        if (random.nextInt(10) == 0) {
            level.playLocalSound(x, y + 0.5D, z, SoundEvents.CAMPFIRE_CRACKLE, SoundSource.BLOCKS,
                    0.5F + random.nextFloat(), random.nextFloat() * 0.7F + 0.6F, false);
        }
        level.addParticle(ParticleTypes.SMOKE, x + (random.nextDouble() - 0.5D) * 0.3D, y + 0.9D,
                z + (random.nextDouble() - 0.5D) * 0.3D, 0.0D, 0.04D, 0.0D);
        if (random.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.FLAME, x + (random.nextDouble() - 0.5D) * 0.4D, y + 0.3D,
                    z + (random.nextDouble() - 0.5D) * 0.4D, 0.0D, 0.02D, 0.0D);
        }
        if (random.nextInt(8) == 0) {
            level.addParticle(ParticleTypes.LAVA, x, y + 0.4D, z, 0.0D, 0.0D, 0.0D);
        }
    }
}
