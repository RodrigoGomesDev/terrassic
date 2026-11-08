package com.terrassic.entity.ai;

import com.terrassic.entity.CarcassEntity;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;
import java.util.List;

/**
 * Scavenging (docs/CARCACAS.md): a hungry meat eater with no target walks to the nearest carcass within 24 blocks
 * and bites it every second and a half until it has had its fill; then it is sated for a few minutes (a sated
 * wild predator does not hunt).
 */
public class EatCarcassGoal extends Goal {
    private static final double RANGE = 24.0D;
    private final DinosaurEntity mob;
    private CarcassEntity carcass;
    private int eatTimer;
    private int bites;
    private int repathTimer;
    /** 1.10.1 (found playing a real world, 08/11): a Dakotaraptor swam 60 s under a carcass on a bank it could not
     *  climb. Best distance so far and the ticks since it last got 1 block nearer; at 10 s it gives up that carcass
     *  for a minute. */
    private double bestDist;
    private int noProgress;
    private int skipId = -1;
    private long skipUntil;

    public EatCarcassGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (this.mob.isSated() || this.mob.isInSittingPose() || this.mob.isVehicle()
                || this.mob.getTarget() != null || this.mob.isPassenger()) {
            return false;
        }
        if (this.mob.getRandom().nextInt(reducedTickDelay(40)) != 0) {
            return false;
        }
        List<CarcassEntity> near = this.mob.level().getEntitiesOfClass(CarcassEntity.class,
                this.mob.getBoundingBox().inflate(RANGE), CarcassEntity::hasMeat);
        CarcassEntity best = null;
        double bestDist = Double.MAX_VALUE;
        for (CarcassEntity c : near) {
            if (c.getId() == this.skipId && this.mob.level().getGameTime() < this.skipUntil) {
                continue;
            }
            double d = this.mob.distanceToSqr(c);
            if (d < bestDist) {
                best = c;
                bestDist = d;
            }
        }
        this.carcass = best;
        return best != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.carcass != null && this.noProgress < 200 && this.carcass.isAlive() && this.carcass.hasMeat() && !this.mob.isSated()
                && this.mob.getTarget() == null && !this.mob.isInSittingPose() && !this.mob.isVehicle();
    }

    @Override
    public void start() {
        this.bites = 0;
        this.eatTimer = 10;
        this.repathTimer = 0;
        this.bestDist = this.mob.distanceTo(this.carcass);
        this.noProgress = 0;
        this.mob.getNavigation().moveTo(this.carcass, 1.1D);
    }

    private void giveUp() {
        this.skipId = this.carcass.getId();
        this.skipUntil = this.mob.level().getGameTime() + 1200L;
        this.carcass = null;
    }

    @Override
    public void stop() {
        if (this.carcass != null && this.noProgress >= 200) {
            this.giveUp();
        }
        this.carcass = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        // the goal selector re-checks canContinueToUse only every other tick: after giveUp() the carcass is gone
        // while tick() still runs once (a server crash in the 1.10.1 regression, 08/11)
        if (this.carcass == null || !this.carcass.isAlive()) {
            return;
        }
        this.mob.getLookControl().setLookAt(this.carcass, 30.0F, 30.0F);
        double reach = this.mob.getBbWidth() * 0.5D + this.carcass.getBbWidth() * 0.5D + 1.5D;
        if (this.mob.distanceToSqr(this.carcass) > reach * reach) {
            double d = this.mob.distanceTo(this.carcass);
            if (d < this.bestDist - 1.0D) {
                this.bestDist = d;
                this.noProgress = 0;
            } else if (++this.noProgress >= 200) {
                this.giveUp();
                return;
            }
            if (--this.repathTimer <= 0) {
                this.repathTimer = 20;
                this.mob.getNavigation().moveTo(this.carcass, 1.1D);
            }
            return;
        }
        this.mob.getNavigation().stop();
        if (--this.eatTimer <= 0) {
            this.eatTimer = 30;
            this.carcass.bite(this.mob);
            if (++this.bites >= this.mob.carcassFill()) {
                this.mob.setSated(6000 + this.mob.getRandom().nextInt(2400));
            }
        }
    }
}
