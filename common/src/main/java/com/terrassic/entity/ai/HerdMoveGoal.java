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
    /** Stuck: where it was two seconds ago, and a rest after giving up (it pushed in place against a neighbour). */
    private Vec3 lastPos;
    private int stuckCheck;
    private int restUntil;

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
        double dist = gap * (0.8D + ((bits >>> 16) & 3) * 0.35D);
        return base.add(Math.cos(angle) * dist, 0.0D, Math.sin(angle) * dist);
    }

    // canUse/canContinueToUse run only on the mob's even ticks (Mob.serverAiStep): the stagger counts those
    // (tickCount / 2), or every animal with an odd id never started (half the calves and herd followers, 08/11)
    @Override
    public boolean canUse() {
        if ((this.mob.tickCount / 2 + this.mob.getId()) % 20 != 0 || this.mob.tickCount < this.restUntil || !this.free()) {
            return false;
        }
        this.spot = this.spot();
        return this.spot != null && this.mob.position().distanceToSqr(this.spot.x, this.mob.getY(), this.spot.z) > 9.0D && !this.taken(this.spot);
    }

    /** Another of the herd already stands on that place: it is as good as there (pushing into it is walking in place). */
    private boolean taken(Vec3 at) {
        double r = Math.max(1.5D, this.mob.getBbWidth() * 0.9D);
        return !this.mob.level().getEntitiesOfClass(this.mob.getClass(), new net.minecraft.world.phys.AABB(at, at).inflate(r, 3.0D, r),
                e -> e != this.mob && e.isAlive()).isEmpty();
    }

    @Override
    public boolean canContinueToUse() {
        return this.free() && this.spot != null && this.mob.tickCount >= this.restUntil && !this.taken(this.spot) && this.mob.position().distanceToSqr(this.spot.x, this.mob.getY(), this.spot.z) > 4.0D
                && !(this.mob.getNavigation().isDone() && this.repath > 0);
    }

    @Override
    public void start() {
        this.repath = 0;
        this.lastPos = this.mob.position();
        this.stuckCheck = 20;
    }

    @Override
    public void stop() {
        this.spot = null;
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        // walking without getting anywhere (the place is taken, a neighbour in the way): give it up for a while
        if (--this.stuckCheck <= 0) {
            this.stuckCheck = 20;
            if (this.lastPos != null && this.mob.position().distanceToSqr(this.lastPos) < 0.3D * 0.3D) {
                this.restUntil = this.mob.tickCount + 200;
                this.spot = null;
                return;
            }
            this.lastPos = this.mob.position();
        }
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
        // its own place set on the ground; when no path gets there (a bank, a drop), beside the leader; else rest
        if (!Reach.walkOr(this.mob, s, leader == null ? null : leader.position(), speed)) {
            this.restUntil = this.mob.tickCount + 200;
            this.spot = null;
        }
    }
}
