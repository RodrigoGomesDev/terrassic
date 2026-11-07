package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.EnumSet;

/**
 * 1.9.5, behaviour (docs/estudos/12): a wild animal brought low (DinosaurEntity.fleeBelow) runs from what hurt it. Of
 * eight headings 24-32 blocks out it takes the one that leaves it furthest from the attacker, never into deep water
 * (unless it swims) nor up or down a cliff (the two traps ARK's fleeing creatures fell into), and runs there; it keeps
 * running while the flight lasts, then heals (DinosaurEntity.behaviourTick) and may come back.
 */
public class FleeHurtGoal extends Goal {
    private final DinosaurEntity mob;
    private int repath;

    public FleeHurtGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        return this.mob.fleeLeft > 0 && this.mob.fleeFrom != null && !this.mob.isVehicle() && !this.mob.isTame();
    }

    @Override
    public boolean canContinueToUse() {
        return this.canUse();
    }

    @Override
    public void start() {
        this.repath = 0;
    }

    @Override
    public void stop() {
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        if (--this.repath > 0 && !this.mob.getNavigation().isDone()) {
            return;
        }
        this.repath = 40;
        BlockPos best = null;
        double bestScore = -1.0D;
        double ax = this.mob.fleeFrom.getX(), az = this.mob.fleeFrom.getZ();
        int y0 = this.mob.blockPosition().getY();
        for (int i = 0; i < 8; i++) {
            double a = (i + this.mob.getRandom().nextDouble() * 0.5D) * Math.PI / 4.0D;
            double r = 24.0D + this.mob.getRandom().nextDouble() * 8.0D;
            int x = (int) Math.floor(this.mob.getX() + Math.cos(a) * r);
            int z = (int) Math.floor(this.mob.getZ() + Math.sin(a) * r);
            if (!this.mob.level().hasChunkAt(new BlockPos(x, y0, z))) {
                continue;
            }
            BlockPos top = this.mob.level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, new BlockPos(x, y0, z));
            boolean water = this.mob.level().getFluidState(top.below()).is(FluidTags.WATER)
                    && this.mob.level().getFluidState(top.below(2)).is(FluidTags.WATER);
            if (water && !this.mob.isInWater()) {
                continue;                       // not into deep water
            }
            if (Math.abs(top.getY() - y0) > 6) {
                continue;                       // nor up or down a cliff
            }
            double score = (x - ax) * (x - ax) + (z - az) * (z - az);
            if (score > bestScore) {
                bestScore = score;
                best = top;
            }
        }
        if (best != null) {
            this.mob.getNavigation().moveTo(best.getX() + 0.5D, best.getY(), best.getZ() + 0.5D, 1.5D);
        }
    }
}
