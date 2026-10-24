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

import java.util.EnumMap;
import java.util.Map;

/**
 * A building block turned towards the player who placed it: cave paintings and skull fossils (full block, picture on
 * the front), roof eaves, skull trophies and rib arches. The shape is given as boxes for the north facing (pixels,
 * like Block.box) and turned with the block, the same way the blockstate turns the model (gen_blocks.py).
 */
public class FacingBlock extends HorizontalDirectionalBlock {
    public static final double[][] FULL = {{0, 0, 0, 16, 16, 16}};
    /** The tilted eave sheet, roughly: the top half of the block. */
    public static final double[][] EAVE = {{0, 9, 0, 16, 16, 16}};
    /** Plaque and skull against the wall at the back (south side when facing north). */
    public static final double[][] TROPHY = {{0, 0, 13, 16, 16, 16}};
    /** Two posts and the lintel; the opening between them can be walked through. */
    public static final double[][] ARCH = {{0, 0, 6, 3, 16, 10}, {13, 0, 6, 16, 16, 10}, {3, 13, 6, 13, 16, 10}};

    private final Map<Direction, VoxelShape> shapes = new EnumMap<>(Direction.class);

    public FacingBlock(Properties properties, double[][] northBoxes) {
        super(properties);
        for (Direction d : Direction.Plane.HORIZONTAL) {
            VoxelShape shape = Shapes.empty();
            for (double[] b : northBoxes) {
                shape = Shapes.or(shape, turned(b, d));
            }
            this.shapes.put(d, shape.optimize());
        }
        this.registerDefaultState(this.stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    /** A north box turned to face d: y rotation 90 (east) maps (x, z) to (16 - z, x). */
    private static VoxelShape turned(double[] b, Direction d) {
        return switch (d) {
            case EAST -> Block.box(16 - b[5], b[1], b[0], 16 - b[2], b[4], b[3]);
            case SOUTH -> Block.box(16 - b[3], b[1], 16 - b[5], 16 - b[0], b[4], 16 - b[2]);
            case WEST -> Block.box(b[2], b[1], 16 - b[3], b[5], b[4], 16 - b[0]);
            default -> Block.box(b[0], b[1], b[2], b[3], b[4], b[5]);
        };
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
        return this.shapes.get(state.getValue(FACING));
    }
}
