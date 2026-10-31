package com.terrassic.entity.ai;

import com.terrassic.entity.ApexTheropod;
import com.terrassic.entity.DinosaurEntity;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The fight of a big theropod (in place of the vanilla melee, which paths to the target's exact block):
 * <ul>
 *   <li>Far away it paths to the target: running at a player or after it roared, stalking slowly up to prey.</li>
 *   <li>Within {@link #DIRECT} body-lengths it stops pathing and closes in on a straight line, turning on the spot
 *       when the target is off to the side (the turn rate of a wide animal made it circle the waypoint before, the
 *       "bites, walks away and comes back" of the 29/10 test).</li>
 *   <li>It stops with its head over the target ({@link #STAND}), never on top of it, and steps back when the target
 *       gets under its belly.</li>
 *   <li>The reach is measured from the head: a bite starts only in front of it and within the neck's reach. The
 *       animation plays first and the hit lands on the frame the jaws close (attack_quick most of the time, the
 *       heavy bite with the shake now and then, a stomp for small things at its feet).</li>
 * </ul>
 * Distances are in blocks for an animal of size 1.0 and scale with {@link DinosaurEntity#getScale()}.
 */
public class ApexBiteGoal extends Goal {
    /** Inside this distance (centre to centre) it moves on its own, no path. */
    private static final double DIRECT = 9.0D;
    /** Where it stops: the snout is then just short of the target (closer, the head swings through a player's
     *  camera: the inside of the mouth filled the screen in the 29/10 rc1 test). It slows down in the last stretch. */
    private static final double STAND = 5.3D;
    private static final double SLOW = 1.5D;
    /** Closer than this it steps back before it bites; much closer the target is under the belly. */
    private static final double BITE_MIN = 4.2D;
    /** Small targets: where it stops and how far from its centre the stomping foot comes down. */
    private static final double STOMP_STAND = 2.4D;
    private static final double STOMP_REACH = 3.6D;
    /** Bite reach from the centre (the neck stretches) and how far off the snout's line the target may be. */
    private static final double REACH = 6.8D;
    private static final float REACH_ANGLE = 35.0F;
    /** Turning on the spot, degrees per tick. */
    private static final float TURN = 5.0F;

    private final ApexTheropod mob;
    private final double speed;
    private int repath;
    private int cooldown;
    /** Ticks until the hit of the bite under way lands (0 = none under way). */
    private int pending;
    private boolean stomping;
    /** Stuck check: where it stood 40 ticks ago, and the ticks left of backing off. */
    private Vec3 lastSpot;
    private int unstick;
    private float side;

    public ApexBiteGoal(ApexTheropod mob, double speed) {
        this.mob = mob;
        this.speed = speed;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity target = this.mob.getTarget();
        return target != null && target.isAlive() && this.mob.canAttack(target) && !this.mob.isVehicle();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity target = this.mob.getTarget();
        if (target == null || !target.isAlive() || this.mob.isVehicle() || !this.mob.isWithinRestriction(target.blockPosition())) {
            return false;
        }
        return !(target instanceof Player player) || (!player.isSpectator() && !player.isCreative());
    }

    @Override
    public void start() {
        this.mob.setAggressive(true);
        this.repath = 0;
        this.pending = 0;
    }

    @Override
    public void stop() {
        this.mob.setAggressive(false);
        this.mob.getNavigation().stop();
        this.pending = 0;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        LivingEntity target = this.mob.getTarget();
        if (target == null) {
            return;
        }
        double s = this.mob.getScale();
        double dx = target.getX() - this.mob.getX();
        double dz = target.getZ() - this.mob.getZ();
        double dist = Math.sqrt(dx * dx + dz * dz);
        float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        float off = Math.abs(Mth.wrapDegrees(yawTo - this.mob.getYRot()));
        this.mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
        // small things (a chicken, a compy) are stomped: it walks right up to them instead of biting from afar
        boolean small = this.mob.strikesAtFeet(target);
        double stand = (small ? STOMP_STAND : STAND) * s;
        double biteMin = (small ? 0.0D : BITE_MIN) * s;
        if (this.cooldown > 0) {
            this.cooldown--;
        }

        // a bite under way: stand, keep the head on the target, land the hit when the jaws close
        if (this.pending > 0) {
            this.mob.getNavigation().stop();
            this.turn(yawTo, TURN * 0.6F);
            if (--this.pending == 0) {
                double reach = (this.stomping ? 4.0D : REACH + 1.0D) * s + target.getBbWidth() / 2.0D;
                if (target.isAlive() && dist <= reach && off < 60.0F && Math.abs(target.getY() - this.mob.getY()) < 5.0D * s) {
                    this.mob.doHurtTarget(target);
                }
            }
            return;
        }
        // roaring at it first: stand and face it
        if (this.mob.isRoaring()) {
            this.mob.getNavigation().stop();
            this.turn(yawTo, TURN);
            return;
        }

        if (dist > DIRECT * s || this.mob.horizontalCollision || Math.abs(target.getY() - this.mob.getY()) > 2.0D) {
            // far, blocked, or up / down a slope: the path finder knows the way
            if (this.unstick > 0) {
                // pinned against a block corner: back off a little, then a fresh path
                this.unstick--;
                this.mob.getNavigation().stop();
                this.mob.getMoveControl().strafe(-0.6F, this.side);
                return;
            }
            if (this.mob.tickCount % 40 == 0) {
                if (this.lastSpot != null && this.mob.position().distanceToSqr(this.lastSpot) < 0.09D && !this.mob.getNavigation().isDone()) {
                    this.unstick = 12;
                    this.side = this.mob.getRandom().nextBoolean() ? 0.4F : -0.4F;
                    this.repath = 0;
                }
                this.lastSpot = this.mob.position();
            }
            if (--this.repath <= 0) {
                this.repath = dist > 32.0D ? 15 : 8;
                boolean stalk = target instanceof Animal && dist > 14.0D * s && !this.mob.hasRoaredAt(target);
                if (!this.mob.getNavigation().moveTo(target, stalk ? this.speed * 0.52D : this.speed)) {
                    this.repath += 10;
                }
            }
        } else {
            this.mob.getNavigation().stop();
            if (dist > stand) {
                if (off < 40.0F) {
                    double pace = dist < stand + SLOW * s ? 0.5D : off < 20.0F ? 1.0D : 0.6D;
                    this.mob.getMoveControl().setWantedPosition(target.getX(), target.getY(), target.getZ(), this.speed * pace);
                } else {
                    this.turn(yawTo, TURN);
                }
            } else if (dist < biteMin) {
                this.turn(yawTo, TURN);
                this.mob.getMoveControl().strafe(-0.5F, 0.0F);
            } else {
                this.turn(yawTo, TURN);
            }
        }

        if (this.cooldown <= 0 && off < REACH_ANGLE && Math.abs(target.getY() - this.mob.getY()) < 4.5D * s) {
            if (small) {
                if (dist < STOMP_REACH * s + target.getBbWidth() / 2.0D) {
                    this.begin(this.mob.feetStrike());
                }
            } else if (dist <= REACH * s + target.getBbWidth() / 2.0D && dist >= biteMin) {
                this.begin(this.mob.biteFor(target));
            }
        }
    }

    /** Starts a blow: the animation now, the hit when it lands, the next one once it is over. */
    private void begin(ApexTheropod.Strike strike) {
        this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, strike.anim());
        this.pending = strike.hit();
        this.cooldown = strike.total();
        this.stomping = strike.atFeet();
        this.mob.getNavigation().stop();
    }

    private void turn(float yaw, float max) {
        float y = Mth.approachDegrees(this.mob.getYRot(), yaw, max);
        this.mob.setYRot(y);
        this.mob.setYBodyRot(y);
    }
}
