package com.primalera.block;

import com.primalera.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.function.Supplier;

/**
 * A dinosaur egg. Laid when two dinosaurs breed (or placed by a player) and hatches by itself after a few
 * minutes: it cracks twice (hatch = 0, 1, 2) and then a baby comes out. The baby imprints on the closest
 * player within 12 blocks and is born tame.
 */
public class DinoEggBlock extends Block {
    public static final IntegerProperty HATCH = BlockStateProperties.HATCH;
    private static final VoxelShape SMALL = Block.box(5.0D, 0.0D, 5.0D, 11.0D, 9.0D, 11.0D);
    private static final VoxelShape LARGE = Block.box(4.0D, 0.0D, 4.0D, 12.0D, 13.0D, 12.0D);

    private final Supplier<? extends EntityType<? extends DinosaurEntity>> species;
    private final boolean large;

    public DinoEggBlock(Supplier<? extends EntityType<? extends DinosaurEntity>> species, boolean large, Properties properties) {
        super(properties);
        this.species = species;
        this.large = large;
        this.registerDefaultState(this.stateDefinition.any().setValue(HATCH, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(HATCH);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return this.large ? LARGE : SMALL;
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (random.nextInt(2) != 0) {
            return;
        }
        int hatch = state.getValue(HATCH);
        if (hatch < 2) {
            level.playSound(null, pos, SoundEvents.TURTLE_EGG_CRACK, SoundSource.BLOCKS, 0.7F, 0.9F + random.nextFloat() * 0.2F);
            level.setBlock(pos, state.setValue(HATCH, hatch + 1), Block.UPDATE_CLIENTS);
        } else {
            hatchEgg(level, pos, random);
        }
    }

    private void hatchEgg(ServerLevel level, BlockPos pos, RandomSource random) {
        level.playSound(null, pos, SoundEvents.TURTLE_EGG_HATCH, SoundSource.BLOCKS, 0.8F, 0.9F + random.nextFloat() * 0.2F);
        level.removeBlock(pos, false);
        level.levelEvent(2001, pos, Block.getId(this.defaultBlockState()));
        DinosaurEntity baby = this.species.get().create(level);
        if (baby == null) {
            return;
        }
        baby.setAge(-24000);
        baby.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, random.nextFloat() * 360.0F, 0.0F);
        Player player = level.getNearestPlayer(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, 12.0D, false);
        if (player != null) {
            baby.tameBy(player);
            baby.setOrderedToSit(false);
        }
        level.addFreshEntity(baby);
    }
}
