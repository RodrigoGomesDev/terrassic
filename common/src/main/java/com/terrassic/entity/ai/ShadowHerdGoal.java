package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.HerbivoreDinosaur;
import com.terrassic.entity.PredatorDinosaur;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Following the herds (06/11/2026, the ecosystem): a wild grown predator that is not hunting, with a migrating herd
 * within 64 blocks, shadows it: it keeps 24 to 32 blocks off the herd's side and walks with it. When hunger comes back
 * its target goals find the herd right there, and the weak first (a calf, a wounded one; PredatorDinosaur). Lions do
 * this with the wildebeest; the herds of the Cretaceous had theirs.
 */
public class ShadowHerdGoal extends Goal {
    private static final double SEE = 64.0D;
    private final PredatorDinosaur mob;
    private HerbivoreDinosaur herd;
    private int repath;
    private int ticks;
    private float side;

    public ShadowHerdGoal(PredatorDinosaur mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean available() {
        return !this.mob.isTame() && !this.mob.isBaby() && !this.mob.isVehicle() && !this.mob.isSleeping() && !this.mob.isKnockedOut()
                && this.mob.getTarget() == null;
    }

    @Override
    public boolean canUse() {
        if (!this.available() || this.mob.getRandom().nextInt(reducedTickDelay(200)) != 0) {
            return false;
        }
        // big enough to take what it follows (a little predator does not shadow a herd of giants)
        this.herd = null;
        double best = SEE * SEE;
        for (HerbivoreDinosaur h : this.mob.level().getEntitiesOfClass(HerbivoreDinosaur.class, this.mob.getBoundingBox().inflate(SEE),
                e -> e.isAlive() && !e.isTame() && e.getMigrationTarget() != null && e.getBbWidth() <= this.mob.getBbWidth() * 1.6F)) {
            double d = this.mob.distanceToSqr(h);
            if (d < best) {
                best = d;
                this.herd = h;
            }
        }
        this.side = this.mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
        return this.herd != null;
    }

    @Override
    public boolean canContinueToUse() {
        return this.available() && this.herd != null && this.herd.isAlive() && this.herd.getMigrationTarget() != null && this.ticks < 2400;
    }

    @Override
    public void start() {
        this.ticks = 0;
        this.repath = 0;
    }

    @Override
    public void stop() {
        this.herd = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        this.ticks++;
        if (--this.repath > 0) {
            return;
        }
        this.repath = adjustedTickDelay(30);
        Vec3 dest = Vec3.atBottomCenterOf(this.herd.getMigrationTarget());
        Vec3 way = dest.subtract(this.herd.position()).multiply(1.0D, 0.0D, 1.0D).normalize();
        // off the herd's flank, a little behind its leader
        Vec3 flank = new Vec3(-way.z, 0.0D, way.x).scale(28.0D * this.side).add(way.scale(-6.0D));
        Vec3 at = this.herd.position().add(flank);
        double far = this.mob.distanceToSqr(at);
        this.mob.getNavigation().moveTo(at.x, at.y, at.z, far > 30.0D * 30.0D ? 1.0D : 0.8D);
    }
}
