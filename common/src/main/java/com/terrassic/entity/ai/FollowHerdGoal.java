package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Loose herds: follow a lower-id neighbour with a size-aware stopping distance, or yield if another animal is
 * too close. A one-way following relationship prevents pairs endlessly chasing one another in circles.
 */
public class FollowHerdGoal extends Goal {
    private static final double SEARCH = 24.0D;
    private static final double TOO_FAR = 7.0D;
    private static final double CLOSE = 4.0D;
    private final DinosaurEntity mob;
    private DinosaurEntity neighbour;
    private int repathTimer;
    private Vec3 offset;
    private boolean separating;

    private boolean available() {
        return !this.mob.isTame() && !this.mob.isBaby() && !this.mob.isVehicle() && !this.mob.isPassenger()
                && !this.mob.isSleeping() && !this.mob.isKnockedOut() && !this.mob.isOrderedToSit()
                && this.mob.getTarget() == null;
    }

    private double spacing(DinosaurEntity other) {
        return Math.max(CLOSE, (this.mob.getBbWidth() + other.getBbWidth()) * 0.75D + 1.0D);
    }

    public FollowHerdGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (!this.available()
                || this.mob.getRandom().nextInt(reducedTickDelay(30)) != 0) {
            return false;
        }
        DinosaurEntity best = null;
        double bestDist = Double.MAX_VALUE;
        for (DinosaurEntity other : this.mob.level().getEntitiesOfClass(this.mob.getClass(), this.mob.getBoundingBox().inflate(SEARCH),
                e -> e != this.mob && e.isAlive() && !e.isTame() && !e.isBaby())) {
            double d = this.mob.distanceToSqr(other);
            // Higher-id animals yield, so the pair does not push in opposite directions every tick.
            if (other.getId() >= this.mob.getId()) continue;
            if (d < bestDist) {
                best = other;
                bestDist = d;
            }
        }
        this.neighbour = best;
        if (best == null) return false;
        double gap = this.spacing(best);
        this.separating = bestDist < gap * gap * 0.55D;
        return this.separating || bestDist > Math.max(TOO_FAR, gap + 3.0D) * Math.max(TOO_FAR, gap + 3.0D);
    }

    @Override
    public boolean canContinueToUse() {
        if (!this.available() || this.neighbour == null || !this.neighbour.isAlive() || this.neighbour.isTame()) {
            return false;
        }
        double d = this.mob.distanceToSqr(this.neighbour);
        double gap = this.spacing(this.neighbour);
        return (this.separating ? d < gap * gap : d > (gap + 1.0D) * (gap + 1.0D)) && d < SEARCH * SEARCH * 2;
    }

    @Override
    public void start() {
        this.repathTimer = 0;
        Vec3 away = this.mob.position().subtract(this.neighbour.position()).multiply(1, 0, 1);
        if (away.lengthSqr() < 0.01D) {
            away = Vec3.directionFromRotation(0, (this.mob.getUUID().getLeastSignificantBits() & 255) * 360.0F / 256);
        }
        this.offset = away.normalize().scale(this.spacing(this.neighbour) + 1.5D);
    }

    @Override
    public void stop() {
        this.neighbour = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        if (--this.repathTimer <= 0) {
            this.repathTimer = adjustedTickDelay(20);
            Vec3 target = this.neighbour.position().add(this.offset);
            this.mob.getNavigation().moveTo(target.x, target.y, target.z, 0.85D);
        }
    }
}
