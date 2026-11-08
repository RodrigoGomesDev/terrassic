package com.terrassic.entity.ai;

import com.terrassic.entity.Albertosaurine;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * The other half of the drive (PackDriveGoal): while a juvenile of its pack drives its prey, a grown
 * {@link Albertosaurine} does not run at it. It waits crouched ("ambush_crouch"), facing it, and strikes when the
 * prey comes close (the bite goal takes over), or when the wait has gone on too long.
 */
public class PackAmbushGoal extends Goal {
    /** The prey this close (blocks past the two half widths, at size 1): the strike. */
    private static final double STRIKE = 7.0D;
    private static final int MAX_WAIT = 300;

    private final Albertosaurine mob;
    private LivingEntity prey;
    private int ticks;
    private boolean struck;

    public PackAmbushGoal(Albertosaurine mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity t = this.mob.getTarget();
        if (t == null || this.mob.isBaby() || this.mob.isTame() || this.mob.isVehicle() || this.mob.isDueling()
                || this.mob.isSpent() || this.close(t) || !this.driven(t)) {
            return false;
        }
        this.prey = t;
        return true;
    }

    /** A juvenile of its kind driving this prey right now. */
    private boolean driven(LivingEntity t) {
        return !this.mob.level().getEntitiesOfClass(Albertosaurine.class, t.getBoundingBox().inflate(48.0D),
                e -> e.isAlive() && e.drivePrey == t && e.mode() == Albertosaurine.MODE_DRIVE
                        && e.getType() == this.mob.getType()).isEmpty();
    }

    private boolean close(LivingEntity t) {
        double gap = Math.sqrt(this.mob.distanceToSqr(t)) - this.mob.getBbWidth() * 0.5D - t.getBbWidth() * 0.5D;
        return gap < STRIKE * Math.max(0.6D, this.mob.getScale());
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity t = this.mob.getTarget();
        if (t == null || t != this.prey || !t.isAlive() || this.ticks >= MAX_WAIT || this.mob.isDueling() || this.mob.isVehicle()) {
            return false;
        }
        if (this.close(t)) {
            this.struck = true;
            return false;
        }
        return this.driven(t) || this.ticks < 40;
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.struck = false;
        this.mob.getNavigation().stop();
        this.mob.setMode(Albertosaurine.MODE_AMBUSH);
        this.mob.logAct("ambush: waits crouched for the " + this.prey.getType().toShortString());
    }

    @Override
    public void stop() {
        this.mob.setMode(Albertosaurine.MODE_NONE);
        if (this.struck) {
            this.mob.logAct("ambush: the " + (this.prey == null ? "prey" : this.prey.getType().toShortString())
                    + " comes in reach, it strikes (" + this.ticks / 20 + " s)");
        } else {
            this.mob.logAct("ambush: ends without the prey (" + this.ticks / 20 + " s)");
        }
        this.prey = null;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        this.ticks++;
        this.mob.getNavigation().stop();
        this.mob.getLookControl().setLookAt(this.prey, 20.0F, 20.0F);
        double dx = this.prey.getX() - this.mob.getX();
        double dz = this.prey.getZ() - this.mob.getZ();
        float yaw = Mth.approachDegrees(this.mob.getYRot(), (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F, 5.0F);
        this.mob.setYRot(yaw);
        this.mob.setYBodyRot(yaw);
    }
}
