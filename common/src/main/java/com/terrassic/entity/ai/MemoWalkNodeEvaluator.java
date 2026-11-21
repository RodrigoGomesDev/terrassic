package com.terrassic.entity.ai;

import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.PathNavigationRegion;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.level.pathfinder.PathfindingContext;
import net.minecraft.world.level.pathfinder.WalkNodeEvaluator;

/**
 * 1.11 (docs/DESEMPENHO_1_11.md): vanilla's walking node evaluator, with the type of each single block remembered for
 * the length of one search. For an animal wider than a block, vanilla reads the type of every block its body covers at
 * each node it tries (and each of those looks at its 26 neighbours for fire or a cactus), so the same block is worked
 * out again for every node whose footprint covers it: a 4-block-wide predator reads each block up to ~80 times in a
 * search. The answer cannot change inside one search (it runs on a snapshot region in one go), so remembering it gives
 * exactly vanilla's path, only cheaper. (1.21.1: vanilla already caches the block's own type in the level's
 * PathTypeCache; what is remembered here is the whole answer, the 26 neighbours for fire or a cactus included.) The memory is dropped when the search ends.
 */
public class MemoWalkNodeEvaluator extends WalkNodeEvaluator {
    private final Long2ObjectOpenHashMap<PathType> single = new Long2ObjectOpenHashMap<>();
    private PathfindingContext searching;

    @Override
    public void prepare(PathNavigationRegion region, Mob mob) {
        super.prepare(region, mob);
        this.single.clear();
        this.searching = this.currentContext;
    }

    @Override
    public void done() {
        super.done();
        this.single.clear();
        this.searching = null;
    }

    @Override
    public PathType getPathType(PathfindingContext context, int x, int y, int z) {
        if (context != this.searching || context == null) {
            return super.getPathType(context, x, y, z);
        }
        long key = BlockPos.asLong(x, y, z);
        PathType type = this.single.get(key);
        if (type == null) {
            type = super.getPathType(context, x, y, z);
            this.single.put(key, type);
        }
        return type;
    }
}
