package com.terrassic.entity.ai;

import com.terrassic.entity.DinosaurEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * 1.10.1 (docs/estudos/12, section 6): a herd follower goes to where its leader is going, plus a place of its own in the
 * group: a fixed angle from its UUID and a distance from the herd's spacing. All of them heading for the same spot from
 * their own places is the cohesion and the alignment; FollowHerdGoal (a higher priority) still keeps them apart.
 */
public class HerdMoveGoal extends Goal {
    private final DinosaurEntity mob;
    private Vec3 spot;
    private int repath;

    public HerdMoveGoal(DinosaurEntity mob) {
        this.mob = mob;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean free() {
        return !this.mob.isVehicle() && !this.mob.isPassenger() && !this.mob.isSleeping() && !this.mob.isKnockedOut()
                && !this.mob.isOrderedToSit() && this.mob.getTarget() == null && this.mob.fleeLeft <= 0 && this.mob.herdFollower();
    }

    /** Where the leader is going (or where it stands), with this one's own place round it. */
    private Vec3 spot() {
        DinosaurEntity leader = this.mob.herdLeader();
        if (leader == null) {
            return null;
        }
        BlockPos to = leader.getNavigation().isInProgress() ? leader.getNavigation().getTargetPos() : null;
        Vec3 base = to == null ? leader.position() : Vec3.atBottomCenterOf(to);
        long bits = this.mob.getUUID().getLeastSignificantBits();
        double angle = (bits & 0xFFFF) / 65536.0D * Math.PI * 2.0D;
        double gap = Math.max(4.0D, (this.mob.getBbWidth() + leader.getBbWidth()) * 0.75D + 1.0D);
        double dist = gap * (1.0D + ((bits >>> 16) & 3) * 0.5D);
        return base.add(Math.cos(angle) * dist, 0.0D, Math.sin(angle) * dist);
    }

    @Override
    public boolean canUse() {
        if ((this.mob.tickCount + this.mob.getId()) % 20 != 0 || !this.free()) {
            return false;
        }
        this.spot = this.spot();
        return this.spot != null && this.mob.position().distanceToSqr(this.spot.x, this.mob.getY(), this.spot.z) > 9.0D;
    }

    @Override
    public boolean canContinueToUse() {
        return this.free() && this.spot != null && this.mob.position().distanceToSqr(this.spot.x, this.mob.getY(), this.spot.z) > 4.0D
                && !(this.mob.getNavigation().isDone() && this.repath > 0);
    }

    @Override
    public void start() {
        this.repath = 0;
    }

    @Override
    public void stop() {
        this.spot = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        if (--this.repath > 0) {
            return;
        }
        this.repath = adjustedTickDelay(20);
        Vec3 s = this.spot();
        if (s == null) {
            return;
        }
        this.spot = s;
        DinosaurEntity leader = this.mob.herdLeader();
        double far = this.mob.position().distanceTo(s);
        double speed = leader != null && leader.getNavigation().isInProgress() ? (far > 12.0D ? 1.15D : 0.95D) : 0.8D;
        this.mob.getNavigation().moveTo(s.x, s.y, s.z, speed);
    }
}
