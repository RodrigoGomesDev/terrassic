package com.terrassic.block;

import net.minecraft.core.BlockPos;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Straw bed, hide bed and hammock: real beds (sleep, set the spawn point), drawn with a plain block model instead of
 * the vanilla bed's block entity renderer, so they have no block entity.
 */
public class PrimitiveBedBlock extends BedBlock {
    public PrimitiveBedBlock(Properties properties) {
        super(DyeColor.BROWN, properties);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return null;
    }
}
