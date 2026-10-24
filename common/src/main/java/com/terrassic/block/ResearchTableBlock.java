package com.terrassic.block;

import com.terrassic.client.ClientHooks;
import com.terrassic.item.BloodSampleItem;
import com.terrassic.item.FossilItem;
import com.terrassic.item.SketchItem;
import com.terrassic.registry.ModItems;
import com.terrassic.research.Research;
import dev.architectury.utils.Env;
import dev.architectury.utils.EnvExecutor;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Research Table (stone, bone and leather). Right click with a fossil or a sketch to study it: it turns into
 * Field Guide knowledge (see Research) and the fossil leaves a bone behind. Right click with an empty hand opens
 * the Field Guide.
 */
public class ResearchTableBlock extends HorizontalDirectionalBlock {
    private static final VoxelShape SHAPE = Shapes.join(Block.box(0.0D, 12.0D, 0.0D, 16.0D, 16.0D, 16.0D),
            Shapes.or(Block.box(1.0D, 0.0D, 1.0D, 4.0D, 12.0D, 4.0D), Block.box(12.0D, 0.0D, 1.0D, 15.0D, 12.0D, 4.0D),
                    Block.box(1.0D, 0.0D, 12.0D, 4.0D, 12.0D, 15.0D), Block.box(12.0D, 0.0D, 12.0D, 15.0D, 12.0D, 15.0D)),
            BooleanOp.OR);

    public ResearchTableBlock(Properties properties) {
        super(properties);
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
        return SHAPE;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        ItemStack stack = player.getItemInHand(hand);
        boolean client = level.isClientSide();
        if (stack.getItem() instanceof FossilItem fossil) {
            if (!client && player instanceof ServerPlayer sp) {
                Research.studyFossil(sp, fossil.species());
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
                ItemStack bone = new ItemStack(Items.BONE);
                if (!player.getInventory().add(bone)) {
                    player.drop(bone, false);
                }
                studied(level, pos);
            }
            return InteractionResult.sidedSuccess(client);
        }
        String sampled = SketchItem.species(stack);
        if (stack.getItem() instanceof BloodSampleItem && sampled != null) {
            if (!client && player instanceof ServerPlayer sp) {
                Research.studySample(sp, sampled);
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
                ItemStack jar = new ItemStack(ModItems.CLAY_JAR.get());
                if (!player.getInventory().add(jar)) {
                    player.drop(jar, false);
                }
                studied(level, pos);
            }
            return InteractionResult.sidedSuccess(client);
        }
        String sketched = SketchItem.species(stack);
        if (stack.getItem() instanceof SketchItem && sketched != null) {
            if (!client && player instanceof ServerPlayer sp) {
                Research.studySketch(sp, sketched);
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
                studied(level, pos);
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (stack.isEmpty() && hand == InteractionHand.MAIN_HAND) {
            if (client) {
                EnvExecutor.runInEnv(Env.CLIENT, () -> () -> ClientHooks.openNotebook("guide"));
            }
            return InteractionResult.sidedSuccess(client);
        }
        return InteractionResult.PASS;
    }

    private static void studied(Level level, BlockPos pos) {
        level.playSound(null, pos, SoundEvents.UI_CARTOGRAPHY_TABLE_TAKE_RESULT, SoundSource.BLOCKS, 1.0F, 1.0F);
        ((ServerLevel) level).sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5D, pos.getY() + 1.1D, pos.getZ() + 0.5D,
                20, 0.3D, 0.2D, 0.3D, 0.5D);
    }
}
