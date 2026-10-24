package com.terrassic.world;

import com.terrassic.Terrassic;
import com.terrassic.registry.ModItems;
import dev.architectury.event.events.common.PlayerEvent;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Container;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * The arrival crater (Cratera de Chegada, HISTORIA.md §8): where the player landed when the machine failed. Dug once
 * per world, the first time anyone joins, 18 to 26 blocks from the world spawn, in any overworld (Terrassic or
 * normal): a shallow scorched bowl of volcanic ash and cracked mud with amber shards at the centre, ash on the rim,
 * and a basket with raw amber and one of Katarina's pages. Only blocks of the mod and vanilla soil are used.
 */
public final class ArrivalCrater {
    private static final int RADIUS = 6;

    private ArrivalCrater() {
    }

    public static void init() {
        PlayerEvent.PLAYER_JOIN.register(ArrivalCrater::onJoin);
    }

    private static void onJoin(ServerPlayer player) {
        ServerLevel level = player.server.overworld();
        Data data = Data.get(level);
        if (data.placed) {
            return;
        }
        data.placed = true;  // even if no spot is found: never try again
        data.setDirty();
        RandomSource rng = RandomSource.create(level.getSeed() ^ 0x5EED_C8A7L);
        BlockPos spawn = level.getSharedSpawnPos();
        for (int attempt = 0; attempt < 12; attempt++) {
            double angle = rng.nextDouble() * Math.PI * 2.0;
            int dist = 18 + rng.nextInt(9);  // beyond the spawn radius (10), so nobody lands inside it
            int x = spawn.getX() + (int) Math.round(Math.cos(angle) * dist);
            int z = spawn.getZ() + (int) Math.round(Math.sin(angle) * dist);
            level.getChunk(x >> 4, z >> 4);
            BlockPos top = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, new BlockPos(x, 0, z)).below();
            if (!level.getFluidState(top).isEmpty() || !level.getFluidState(top.above()).isEmpty()) {
                continue;  // not in water
            }
            dig(level, top, rng);
            data.x = top.getX();
            data.y = top.getY();
            data.z = top.getZ();
            return;
        }
    }

    private static BlockState ours(String id, BlockState fallback) {
        Block b = BuiltInRegistries.BLOCK.get(Terrassic.id(id));
        return b == Blocks.AIR ? fallback : b.defaultBlockState();
    }

    private static void dig(ServerLevel level, BlockPos center, RandomSource rng) {
        BlockState ash = ours("volcanic_ash", Blocks.GRAVEL.defaultBlockState());
        BlockState ashLayer = ours("volcanic_ash_layer", Blocks.AIR.defaultBlockState());
        BlockState mud = ours("cracked_mud", Blocks.COARSE_DIRT.defaultBlockState());
        BlockState amber = ours("amber_block", Blocks.GLOWSTONE.defaultBlockState());
        for (int dx = -RADIUS - 1; dx <= RADIUS + 1; dx++) {
            for (int dz = -RADIUS - 1; dz <= RADIUS + 1; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d > RADIUS + 1.2) {
                    continue;
                }
                int x = center.getX() + dx;
                int z = center.getZ() + dz;
                BlockPos surface = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, new BlockPos(x, 0, z)).below();
                BlockState top = level.getBlockState(surface);
                if (top.is(BlockTags.LOGS) || top.is(BlockTags.LEAVES) || !level.getFluidState(surface).isEmpty()) {
                    continue;  // leave trees and water alone
                }
                // clear plants and snow above the ground of the bowl
                for (int y = 1; y <= 3; y++) {
                    BlockPos p = surface.above(y);
                    if (level.getBlockState(p).canBeReplaced() && level.getFluidState(p).isEmpty()) {
                        level.setBlock(p, Blocks.AIR.defaultBlockState(), Block.UPDATE_CLIENTS);
                    }
                }
                if (d > RADIUS) {  // the rim: a dusting of ash
                    if (rng.nextFloat() < 0.55F && level.getBlockState(surface).isFaceSturdy(level, surface, Direction.UP)) {
                        level.setBlock(surface.above(), ashLayer, Block.UPDATE_CLIENTS);
                    }
                    continue;
                }
                int depth = (int) Math.round(2.2 * (1.0 - (d / RADIUS) * (d / RADIUS)));
                for (int k = 0; k < depth; k++) {
                    level.setBlock(surface.below(k), Blocks.AIR.defaultBlockState(), Block.UPDATE_CLIENTS);
                }
                BlockPos floor = surface.below(depth);
                BlockState f;
                if (d < 1.2) {
                    f = amber;
                } else if (d < 3.0) {
                    f = rng.nextFloat() < 0.15F ? amber : ash;
                } else {
                    f = rng.nextFloat() < 0.6F ? mud : (rng.nextFloat() < 0.5F ? ash : Blocks.COARSE_DIRT.defaultBlockState());
                }
                level.setBlock(floor, f, Block.UPDATE_CLIENTS);
                if (d >= 3.0 && rng.nextFloat() < 0.25F) {
                    level.setBlock(floor.above(), ashLayer, Block.UPDATE_CLIENTS);
                }
            }
        }
        // the basket on the rim, with raw amber and one of Katarina's pages
        BlockPos rim = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                center.offset(RADIUS + 1, 0, 0));
        BlockState basket = ours("wicker_basket", Blocks.AIR.defaultBlockState());
        if (!basket.isAir() && level.getFluidState(rim).is(Fluids.EMPTY)) {
            if (basket.hasProperty(HorizontalDirectionalBlock.FACING)) {
                basket = basket.setValue(HorizontalDirectionalBlock.FACING, Direction.WEST);
            }
            level.setBlock(rim, basket, Block.UPDATE_ALL);
            BlockEntity be = level.getBlockEntity(rim);
            if (be instanceof Container c) {
                c.setItem(0, new ItemStack(ModItems.RAW_AMBER.get(), 3));
                c.setItem(1, new ItemStack(ModItems.LOOSE_PAGE.get()));
                be.setChanged();
            }
        }
    }

    /** Whether (and where) the crater was dug: data/terrassic_crater.dat of the overworld. */
    static final class Data extends SavedData {
        private static final String NAME = "terrassic_crater";
        boolean placed;
        int x;
        int y;
        int z;

        static Data get(ServerLevel level) {
            return level.getServer().getLevel(Level.OVERWORLD).getDataStorage().computeIfAbsent(Data::load, Data::new, NAME);
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            tag.putBoolean("Placed", this.placed);
            tag.putInt("X", this.x);
            tag.putInt("Y", this.y);
            tag.putInt("Z", this.z);
            return tag;
        }

        static Data load(CompoundTag tag) {
            Data d = new Data();
            d.placed = tag.getBoolean("Placed");
            d.x = tag.getInt("X");
            d.y = tag.getInt("Y");
            d.z = tag.getInt("Z");
            return d;
        }
    }
}
