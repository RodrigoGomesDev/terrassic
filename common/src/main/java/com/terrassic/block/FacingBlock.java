package com.terrassic.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A building block turned towards the player who placed it: cave paintings (full block, picture on the front) and
 * roof eaves (a tilted sheet of thatch, see gen_blocks.py gen_eave).
 */
public class FacingBlock extends HorizontalDirectionalBlock {
    /** The tilted eave sheet, roughly: the top half of the block. */
    public static final VoxelShape EAVE = Block.box(0.0D, 9.0D, 0.0D, 16.0D, 16.0D, 16.0D);

    private final VoxelShape shape;

    /** shape = null for a full block. */
    public FacingBlock(Properties properties, VoxelShape shape) {
        super(properties);
        this.shape = shape == null ? Shapes.block() : shape;
        this.registerDefaultState(this.stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return this.defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return this.shape;
    }
}
