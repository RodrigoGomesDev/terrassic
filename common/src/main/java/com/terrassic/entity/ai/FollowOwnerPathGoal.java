package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/** Follow an owner using the animal's own navigation, including AmphibiousPathNavigation. */
public class FollowOwnerPathGoal extends Goal {
    private final DinosaurEntity mob;
    private final double speed;
    private final double start;
    private final double stop;
    private LivingEntity owner;
    private int repath;

    public FollowOwnerPathGoal(DinosaurEntity mob, double speed, double start, double stop) {
        this.mob = mob;
        this.speed = speed;
        this.start = start;
        this.stop = stop;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private boolean available() {
        return this.mob.isTame() && !this.mob.isKnockedOut() && !this.mob.isOrderedToSit() && !this.mob.isWandering()
                && !this.mob.isVehicle() && !this.mob.isPassenger() && !this.mob.isLeashed();
    }

    @Override
    public boolean canUse() {
        this.owner = this.mob.getOwner();
        return this.available() && this.owner != null && this.owner.isAlive() && !this.owner.isSpectator()
                && this.mob.distanceToSqr(this.owner) > this.start * this.start;
    }

    @Override
    public boolean canContinueToUse() {
        return this.available() && this.owner != null && this.owner.isAlive() && !this.owner.isSpectator()
                && !this.mob.getNavigation().isDone() && this.mob.distanceToSqr(this.owner) > this.stop * this.stop;
    }

    @Override
    public void start() {
        this.repath = 0;
    }

    @Override
    public void stop() {
        this.owner = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        this.mob.getLookControl().setLookAt(this.owner, 10, this.mob.getMaxHeadXRot());
        if (--this.repath <= 0) {
            this.repath = adjustedTickDelay(10);
            this.mob.getNavigation().moveTo(this.owner, this.speed);
        }
    }
}
