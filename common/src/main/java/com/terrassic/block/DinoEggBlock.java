package com.terrassic.block;

import com.terrassic.registry.ModSounds;
import com.terrassic.config.Rule;
import com.terrassic.config.Rules;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.research.Objective;
import com.terrassic.research.Research;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.function.Supplier;

/**
 * A dinosaur egg. Laid when two dinosaurs breed (or placed by a player) and hatches by itself after a few
 * minutes: it cracks twice (hatch = 0, 1, 2) and then a baby comes out. The baby imprints on the closest
 * player within 12 blocks and is born tame.
 * <p>
 * A <b>wild</b> egg ({@link #WILD}, docs/NINHOS.md) was laid by wild parents or spawned with a herd: its baby is
 * born wild and joins the herd, and whoever starts breaking it alerts the wild adults of the species nearby (the
 * fighters attack, the runners stampede). Breaking a fresh egg drops the egg item; placed again by a player it is
 * an ordinary egg and hatches tame. Stealing eggs is how you get a predator of your own before the knockout.
 */
public class DinoEggBlock extends Block {
    public static final IntegerProperty HATCH = BlockStateProperties.HATCH;
    /** Laid by wild parents: hatches a wild baby and is guarded by the herd. */
    public static final BooleanProperty WILD = BooleanProperty.create("wild");
    private static final VoxelShape SMALL = Block.box(5.0D, 0.0D, 5.0D, 11.0D, 9.0D, 11.0D);
    private static final VoxelShape LARGE = Block.box(4.0D, 0.0D, 4.0D, 12.0D, 13.0D, 12.0D);

    private final Supplier<? extends EntityType<? extends DinosaurEntity>> species;
    private final boolean large;

    public DinoEggBlock(Supplier<? extends EntityType<? extends DinosaurEntity>> species, boolean large, Properties properties) {
        super(properties);
        this.species = species;
        this.large = large;
        this.registerDefaultState(this.stateDefinition.any().setValue(HATCH, 0).setValue(WILD, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(HATCH, WILD);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return this.large ? LARGE : SMALL;
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        // one in two random ticks advances a stage at hatch speed 1; the Hatching speed rule scales that (docs/REGRAS.md)
        int stages = Rules.scaled(random, 0.5D, Rule.HATCH_SPEED, level);
        int hatch = state.getValue(HATCH);
        for (int i = 0; i < stages; i++) {
            if (hatch < 2) {
                hatch++;
            } else {
                hatchEgg(level, pos, random, state.getValue(WILD));
                return;
            }
        }
        if (hatch != state.getValue(HATCH)) {
            level.playSound(null, pos, ModSounds.SFX_EGG_CRACK.get(), SoundSource.BLOCKS, 0.7F, 0.9F + random.nextFloat() * 0.2F);
            level.setBlock(pos, state.setValue(HATCH, hatch), Block.UPDATE_CLIENTS);
        }
    }

    /** The herd defends its nest: whoever starts breaking a wild egg becomes the enemy of the wild adults around. */
    @Override
    public void attack(BlockState state, Level level, BlockPos pos, Player player) {
        super.attack(state, level, pos, player);
        this.alertParents(state, level, pos, player);
    }

    @Override
    public void playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
        super.playerWillDestroy(level, pos, state, player);
        this.alertParents(state, level, pos, player);
    }

    /** Whoever breaks a wild egg (a player, or an egg thief like the Didelphodon) becomes the enemy of the wild
     *  adults of the species within twenty blocks. */
    public void alertParents(BlockState state, Level level, BlockPos pos, LivingEntity culprit) {
        if (level.isClientSide() || !state.getValue(WILD) || (culprit instanceof Player player && player.isCreative())) {
            return;
        }
        EntityType<?> type = this.species.get();
        for (DinosaurEntity parent : level.getEntitiesOfClass(DinosaurEntity.class, new AABB(pos).inflate(20.0D),
                e -> e.getType() == type && !e.isTame() && !e.isBaby() && e.getLastHurtByMob() == null)) {
            parent.setSleeping(false);
            parent.setLastHurtByMob(culprit);
        }
    }

    private void hatchEgg(ServerLevel level, BlockPos pos, RandomSource random, boolean wild) {
        level.playSound(null, pos, ModSounds.SFX_EGG_HATCH.get(), SoundSource.BLOCKS, 0.8F, 0.9F + random.nextFloat() * 0.2F);
        level.removeBlock(pos, false);
        level.levelEvent(2001, pos, Block.getId(this.defaultBlockState()));
        DinosaurEntity baby = this.species.get().create(level);
        if (baby == null) {
            return;
        }
        baby.setAge(-24000);
        // A wild nest must not grow the saved population indefinitely. Stolen/player-placed eggs stay persistent.
        baby.setRoamer(wild);
        baby.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, random.nextFloat() * 360.0F, 0.0F);
        // a wild egg hatches a wild baby: it follows the adults of its species (FollowParentGoal), no imprinting
        Player player = wild ? null : level.getNearestPlayer(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, 12.0D, false);
        if (player != null) {
            baby.tameBy(player);
            baby.setOrderedToSit(false);
            if (player instanceof ServerPlayer sp) {
                Research.objective(sp, Objective.HATCH_EGG);
            }
        }
        level.addFreshEntity(baby);
        baby.playAmbientSound();
    }
}
