package com.terrassic.entity.ai;

import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.PathNavigationRegion;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.level.pathfinder.WalkNodeEvaluator;

/**
 * 1.11 (docs/DESEMPENHO_1_11.md): vanilla's walking node evaluator, with the type of each single block remembered for
 * the length of one search. For an animal wider than a block, vanilla reads the type of every block its body covers at
 * each node it tries (and each of those looks at its 26 neighbours for fire or a cactus), so the same block is worked
 * out again for every node whose footprint covers it: a 4-block-wide predator reads each block up to ~80 times in a
 * search. The answer cannot change inside one search (it runs on a snapshot region in one go), so remembering it gives
 * exactly vanilla's path, only cheaper. The memory is dropped when the search ends.
 */
public class MemoWalkNodeEvaluator extends WalkNodeEvaluator {
    private final Long2ObjectOpenHashMap<BlockPathTypes> single = new Long2ObjectOpenHashMap<>();
    private BlockGetter searching;

    @Override
    public void prepare(PathNavigationRegion region, Mob mob) {
        super.prepare(region, mob);
        this.single.clear();
        this.searching = region;
    }

    @Override
    public void done() {
        super.done();
        this.single.clear();
        this.searching = null;
    }

    @Override
    public BlockPathTypes getBlockPathType(BlockGetter level, int x, int y, int z) {
        if (level != this.searching || level == null) {
            return super.getBlockPathType(level, x, y, z);
        }
        long key = BlockPos.asLong(x, y, z);
        BlockPathTypes type = this.single.get(key);
        if (type == null) {
            type = super.getBlockPathType(level, x, y, z);
            this.single.put(key, type);
        }
        return type;
    }
}
