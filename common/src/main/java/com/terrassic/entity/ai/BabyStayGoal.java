package com.terrassic.entity.ai;

import com.terrassic.entity.Behaviour;
import com.terrassic.entity.DinosaurEntity;
import com.terrassic.entity.PredatorDinosaur;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * 1.10.1 (docs/estudos/12, section 6): a wild baby keeps within 6 blocks of the nearest grown one of its species (its
 * mother) and runs from any predator of another species or player that comes within 8, to the far side of its mother
 * when she is there. A player holding its food is let come (that is how a baby is tamed).
 */
public class BabyStayGoal extends Goal {
    private static final double STAY = 6.0D;
    private static final double THREAT = 8.0D;
    private final DinosaurEntity mob;
    private LivingEntity threat;
    private DinosaurEntity mother;
    private int repath;
    /** Which side of its mother it goes round, and a check that it is getting anywhere (else the other side). */
    private double sideSign = 1.0D;
    private Vec3 lastPos;
    private int stuckCheck;
    private int stuck;

    public BabyStayGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean free() {
        return !Behaviour.oldBaby && this.mob.isBaby() && !this.mob.isTame() && !this.mob.isVehicle() && !this.mob.isPassenger()
                && !this.mob.isSleeping() && !this.mob.isKnockedOut() && this.mob.fleeLeft <= 0;
    }

    private void look() {
        this.threat = null;
        double best = THREAT * THREAT;
        for (LivingEntity e : this.mob.level().getEntitiesOfClass(LivingEntity.class, this.mob.getBoundingBox().inflate(THREAT),
                e -> e != this.mob && e.isAlive() && this.threatens(e))) {
            double d = e.distanceToSqr(this.mob);
            if (d < best) {
                best = d;
                this.threat = e;
            }
        }
        this.mother = null;
        best = 32.0D * 32.0D;
        for (DinosaurEntity d : this.mob.level().getEntitiesOfClass(DinosaurEntity.class, this.mob.getBoundingBox().inflate(32.0D, 8.0D, 32.0D),
                e -> e != this.mob && e.getType() == this.mob.getType() && e.isAlive() && !e.isBaby() && !e.isTame())) {
            double dd = d.distanceToSqr(this.mob);
            if (dd < best) {
                best = dd;
                this.mother = d;
            }
        }
    }

    private boolean threatens(LivingEntity e) {
        if (e instanceof Player p) {
            return !p.isCreative() && !p.isSpectator() && !this.mob.isFood(p.getMainHandItem()) && !this.mob.isFood(p.getOffhandItem());
        }
        return e instanceof PredatorDinosaur p && !p.isTame() && !p.isBaby() && p.getType() != this.mob.getType();
    }

    private boolean wants() {
        return this.threat != null || (this.mother != null && this.mother.distanceToSqr(this.mob) > STAY * STAY);
    }

    @Override
    public boolean canUse() {
        if ((this.mob.tickCount + this.mob.getId()) % 10 != 0 || !this.free()) {
            return false;
        }
        this.look();
        return this.wants();
    }

    @Override
    public boolean canContinueToUse() {
        if (!this.free()) {
            return false;
        }
        if ((this.mob.tickCount + this.mob.getId()) % 10 == 0) {
            this.look();
        }
        if (this.threat != null) {
            if (this.stuck == 0 && this.sideSign == 0.0D && (this.mob.tickCount + this.mob.getId()) % 10 == 0) {
                Behaviour.log("baby flee: " + this.mob.speciesId() + " #" + this.mob.getId() + " from " + this.threat.getType().toShortString());
            }
            return true;
        }
        return this.mother != null && this.mother.distanceToSqr(this.mob) > 2.5D * 2.5D;
    }

    @Override
    public void start() {
        this.repath = 0;
        this.lastPos = this.mob.position();
        this.stuckCheck = 20;
        this.sideSign = 0.0D;
        this.stuck = 0;
        if (this.threat != null) {
            Behaviour.log("baby flee: " + this.mob.speciesId() + " #" + this.mob.getId() + " from " + this.threat.getType().toShortString());
        }
    }

    @Override
    public void stop() {
        this.mob.getNavigation().stop();
        this.threat = null;
    }

    @Override
    public void tick() {
        if (--this.stuckCheck <= 0) {
            this.stuckCheck = 20;
            if (this.threat != null && this.lastPos != null && this.mob.position().distanceToSqr(this.lastPos) < 0.3D * 0.3D) {
                this.sideSign = this.sideSign == 0.0D ? -1.0D : -this.sideSign;      // wedged against her: round the other side
                this.stuck++;
                this.repath = 0;
            }
            this.lastPos = this.mob.position();
        }
        if (--this.repath > 0) {
            return;
        }
        this.repath = 10;
        Vec3 to;
        double speed;
        if (this.threat != null) {
            Vec3 away = this.mob.position().subtract(this.threat.position()).multiply(1.0D, 0.0D, 1.0D);
            if (away.lengthSqr() < 0.01D) {
                away = new Vec3(1.0D, 0.0D, 0.0D);
            }
            away = away.normalize();
            if (this.mother != null) {
                // behind its mother, on the far side from the threat (or just away when she is nearer the threat than 3)
                Vec3 m = this.mother.position();
                Vec3 off = m.subtract(this.threat.position()).multiply(1.0D, 0.0D, 1.0D);
                off = off.lengthSqr() < 0.01D ? away : off.normalize();
                // far enough that the threat is past 8 blocks, still within 6 of her
                double back = Mth.clamp(10.0D - this.mother.distanceTo(this.threat), this.mother.getBbWidth() * 0.5D + 2.0D, 6.0D);
                // round her side, the side it is already on, so the way does not run into her body
                Vec3 side = new Vec3(-off.z, 0.0D, off.x);
                if (this.sideSign == 0.0D) {
                    this.sideSign = this.mob.position().subtract(m).dot(side) < 0.0D ? -1.0D : 1.0D;
                }
                double on = this.sideSign;
                Vec3 dir = off.scale(0.77D).add(side.scale(0.64D * on));
                to = m.add(dir.scale(back));
                if (to.distanceToSqr(this.threat.position()) < this.mob.distanceToSqr(this.threat)) {
                    to = this.mob.position().add(away.scale(12.0D));
                }
            } else {
                to = this.mob.position().add(away.scale(12.0D));
            }
            speed = 1.6D;
        } else if (this.mother != null) {
            to = this.mother.position();
            speed = 1.2D;
        } else {
            return;
        }
        boolean going = this.stuck < 2 && this.mob.getNavigation().moveTo(to.x, to.y, to.z, speed);
        if (!going && this.threat != null) {
            // no way round her (or none found twice): straight away from the threat
            Vec3 away = this.mob.position().subtract(this.threat.position()).multiply(1.0D, 0.0D, 1.0D);
            away = away.lengthSqr() < 0.01D ? new Vec3(1.0D, 0.0D, 0.0D) : away.normalize();
            Vec3 run = this.mob.position().add(away.scale(10.0D));
            this.mob.getNavigation().moveTo(run.x, run.y, run.z, speed);
        }
    }
}
