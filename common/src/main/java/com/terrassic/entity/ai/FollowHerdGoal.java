package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Herds and packs (docs/BANDOS.md): a wild adult that has strayed more than seven blocks from the nearest wild adult
 * of its species walks back to it. No leader, no bookkeeping: cohesion comes from everyone keeping a neighbour
 * close, and the herd drifts together as its members wander.
 */
public class FollowHerdGoal extends Goal {
    private static final double SEARCH = 24.0D;
    private static final double TOO_FAR = 7.0D;
    private static final double CLOSE = 4.0D;
    private final DinosaurEntity mob;
    private DinosaurEntity neighbour;
    private int repathTimer;

    public FollowHerdGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (this.mob.isTame() || this.mob.isBaby() || this.mob.isVehicle() || this.mob.isSleeping() || this.mob.getTarget() != null
                || this.mob.getRandom().nextInt(reducedTickDelay(30)) != 0) {
            return false;
        }
        DinosaurEntity best = null;
        double bestDist = Double.MAX_VALUE;
        for (DinosaurEntity other : this.mob.level().getEntitiesOfClass(this.mob.getClass(), this.mob.getBoundingBox().inflate(SEARCH),
                e -> e != this.mob && e.isAlive() && !e.isTame() && !e.isBaby())) {
            double d = this.mob.distanceToSqr(other);
            if (d < bestDist) {
                best = other;
                bestDist = d;
            }
        }
        this.neighbour = best;
        return best != null && bestDist > TOO_FAR * TOO_FAR;
    }

    @Override
    public boolean canContinueToUse() {
        if (this.neighbour == null || !this.neighbour.isAlive() || this.neighbour.isTame() || this.mob.getTarget() != null) {
            return false;
        }
        double d = this.mob.distanceToSqr(this.neighbour);
        return d > CLOSE * CLOSE && d < SEARCH * SEARCH * 2;
    }

    @Override
    public void start() {
        this.repathTimer = 0;
    }

    @Override
    public void stop() {
        this.neighbour = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        if (--this.repathTimer <= 0) {
            this.repathTimer = adjustedTickDelay(10);
            this.mob.getNavigation().moveTo(this.neighbour, 1.05D);
        }
    }
}
