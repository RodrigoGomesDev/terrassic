package com.terrassic.entity.ai;

import com.terrassic.entity.Raptor;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/** A tame raptor badly hurt falls back behind its owner, away from whatever hurt it, until {@link Raptor#isRetreating()} ends. */
public class RaptorRetreatGoal extends Goal {
    private static final double BEHIND = 3.0D;
    private static final double SPEED = 1.3D;
    private static final double KEEP_AWAY = 5.0D;

    private final Raptor mob;
    private int repath;

    public RaptorRetreatGoal(Raptor mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        return this.mob.isRetreating() && !this.mob.isInSittingPose();
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
        LivingEntity owner = this.mob.getOwner();
        if (owner == null || --this.repath > 0) {
            return;
        }
        this.repath = 10;
        LivingEntity threat = this.mob.getLastHurtByMob();
        boolean threatened = threat != null && threat.isAlive();
        if (threatened && this.mob.distanceToSqr(threat) < KEEP_AWAY * KEEP_AWAY) {
            // it caught up: keep away from it first, there is no standing still behind the owner
            Vec3 clear = DefaultRandomPos.getPosAway(this.mob, 10, 5, threat.position());
            if (clear != null) {
                this.mob.getNavigation().moveTo(clear.x, clear.y, clear.z, SPEED);
                return;
            }
        }
        Vec3 away = threatened ? owner.position().subtract(threat.position()) : owner.getLookAngle().reverse();
        away = away.multiply(1.0D, 0.0D, 1.0D);
        Vec3 spot = away.lengthSqr() < 1.0E-4D ? owner.position() : owner.position().add(away.normalize().scale(BEHIND));
        this.mob.getNavigation().moveTo(spot.x, spot.y, spot.z, SPEED);
        this.mob.getLookControl().setLookAt(owner, 30.0F, 30.0F);
    }
}
