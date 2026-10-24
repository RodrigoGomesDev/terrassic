package com.terrassic.leap;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.joml.Vector3f;

/**
 * The Leap Altar (docs/SALTO.md): a plinth of stacked stone, a drum of bone wrapped in hide and the amber on top.
 * It does nothing by itself (Rule 0): it only shows what it can do, and acts when a player asks.
 * <ul>
 *   <li>Use: what the altar needs (posts of the ring, fragments) and what you can do with it.</li>
 *   <li>Sneak + use with raw amber: offer the amber and start the ritual of the meteors (or, with only 2-3
 *       fragments in the Normal mode, the Unstable Leap, confirmed with a second offering).</li>
 *   <li>Sneak + use with an empty hand: leap, once the altar is open for you.</li>
 * </ul>
 * {@link #STAGE}: 0 cold (ring incomplete), 1 ring complete, 2 ritual, 3 open (the Rift Tyrant was beaten here).
 */
public class LeapAltarBlock extends BaseEntityBlock {
    public static final IntegerProperty STAGE = IntegerProperty.create("stage", 0, 3);
    public static final int COLD = 0;
    public static final int RING = 1;
    public static final int RITUAL = 2;
    public static final int OPEN = 3;
    public static final int[] LIGHT = {3, 8, 15, 12};
    private static final VoxelShape SHAPE = Shapes.or(Block.box(0, 0, 0, 16, 4, 16), Block.box(3, 4, 3, 13, 9, 13),
            Block.box(4, 9, 4, 12, 16, 12));
    private static final DustParticleOptions AMBER = new DustParticleOptions(new Vector3f(1.0F, 0.66F, 0.2F), 1.0F);

    public LeapAltarBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(STAGE, COLD));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(STAGE);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new LeapAltarBlockEntity(pos, state);
    }

    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide() ? null
                : createTickerHelper(type, LeapRegistry.LEAP_ALTAR_ENTITY.get(), LeapAltarBlockEntity::serverTick);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (hand != InteractionHand.MAIN_HAND) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide() && level.getBlockEntity(pos) instanceof LeapAltarBlockEntity altar) {
            altar.use(player);
        }
        return InteractionResult.sidedSuccess(level.isClientSide());
    }

    @Override
    public void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof LeapAltarBlockEntity altar) {
            altar.cancelRitual(true);
        }
        super.onRemove(state, level, pos, newState, moved);
    }

    /** Client: the amber glows and drifts, stronger with each stage; during the ritual it spits fire. */
    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        int stage = state.getValue(STAGE);
        double x = pos.getX() + 0.5D;
        double y = pos.getY() + 1.05D;
        double z = pos.getZ() + 0.5D;
        if (stage == COLD) {
            if (random.nextInt(4) == 0) {
                level.addParticle(AMBER, x + (random.nextDouble() - 0.5D) * 0.4D, y, z + (random.nextDouble() - 0.5D) * 0.4D, 0, 0, 0);
            }
            return;
        }
        for (int i = 0; i < stage; i++) {
            double a = random.nextDouble() * Math.PI * 2.0D;
            double r = 0.3D + random.nextDouble() * (stage == OPEN ? 2.8D : 0.6D);
            level.addParticle(AMBER, x + Math.cos(a) * r, y - 0.4D + random.nextDouble() * 0.8D, z + Math.sin(a) * r, 0.0D, 0.02D, 0.0D);
        }
        if (stage == RITUAL) {
            level.addParticle(ParticleTypes.FLAME, x, y, z, (random.nextDouble() - 0.5D) * 0.05D, 0.12D, (random.nextDouble() - 0.5D) * 0.05D);
            if (random.nextInt(3) == 0) {
                level.addParticle(ParticleTypes.LAVA, x, y, z, 0.0D, 0.0D, 0.0D);
            }
        } else if (stage == OPEN && random.nextInt(2) == 0) {
            level.addParticle(ParticleTypes.END_ROD, x, y + 0.2D, z, 0.0D, 0.04D, 0.0D);
        }
    }
}
