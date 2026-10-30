package com.terrassic.entity.ai;

import com.terrassic.entity.FlyingDinosaur;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Home for a colonist (world/PteroColonies): a wild one more than {@link #RANGE} blocks from its colony and not out
 * fishing (FishingFlightGoal) flies straight back and drops onto it; at the colony it shuffles about on the rocks a
 * few blocks at a time. At night everyone is home, so the colony is where to find them after dark.
 */
public class ColonyGoal extends Goal {
    private static final double RANGE = 10.0D;
    private final FlyingDinosaur bird;
    private boolean flying;

    public ColonyGoal(FlyingDinosaur bird) {
        this.bird = bird;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean free() {
        return this.bird.isColonist() && !this.bird.isKnockedOut() && !this.bird.isVehicle() && !this.bird.isPassenger()
                && !this.bird.isLeashed() && this.bird.getTarget() == null && !this.bird.isCruising();
    }

    @Override
    public boolean canUse() {
        if (!this.free()) {
            return false;
        }
        if (this.away() > RANGE) {
            return true;
        }
        // a short shuffle on the rocks now and then
        return this.bird.onGround() && this.bird.getRandom().nextInt(reducedTickDelay(240)) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return this.free() && (this.flying || !this.bird.getNavigation().isDone());
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        BlockPos home = this.bird.getColonyHome();
        if (this.away() > RANGE) {
            this.flying = true;
            this.bird.setCruising(true);
            if (this.bird.onGround()) {
                Vec3 v = this.bird.getDeltaMovement();
                this.bird.setDeltaMovement(v.x, 0.6D, v.z);
            }
        } else {
            this.flying = false;
            double a = this.bird.getRandom().nextDouble() * Math.PI * 2.0D;
            double r = 2.0D + this.bird.getRandom().nextDouble() * 4.0D;
            this.bird.getNavigation().moveTo(home.getX() + 0.5D + Math.cos(a) * r, home.getY(), home.getZ() + 0.5D + Math.sin(a) * r, 0.6D);
        }
    }

    @Override
    public void stop() {
        if (this.flying) {
            this.bird.setCruising(false);
            this.bird.setSoarTarget(null);
        }
        this.flying = false;
    }

    @Override
    public void tick() {
        if (!this.flying) {
            return;
        }
        Vec3 roost = Vec3.atBottomCenterOf(this.bird.getColonyHome());
        double flat = Math.sqrt(Mth.square(roost.x - this.bird.getX()) + Mth.square(roost.z - this.bird.getZ()));
        this.bird.setSoarTarget(roost.add(0.0D, flat > 24.0D ? 18.0D : Math.max(2.0D, flat * 0.5D), 0.0D));
        if (flat < 4.0D && this.bird.getY() - roost.y < 7.0D) {
            this.bird.setCruising(false);
            this.bird.setDeltaMovement(0.0D, -0.1D, 0.0D);
            this.flying = false;
        }
    }

    /** Horizontal distance to the colony. */
    private double away() {
        BlockPos home = this.bird.getColonyHome();
        return home == null ? 0.0D : Math.sqrt(Mth.square(home.getX() + 0.5D - this.bird.getX()) + Mth.square(home.getZ() + 0.5D - this.bird.getZ()));
    }
}
