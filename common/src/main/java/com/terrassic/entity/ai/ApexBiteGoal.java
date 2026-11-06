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
 *   <li>A rig may pause after a blow ({@link ApexTheropod#pauseAfter}): the Giganotosaurus cuts, steps back, stands
 *       watching with one eye and circles before it comes in again.</li>
 *   <li>The reach is measured from the head: a bite starts only in front of it and within the neck's reach. The
 *       animation plays first and the hit lands on the frame the jaws close (attack_quick most of the time, the
 *       heavy bite with the shake now and then, a stomp for small things at its feet).</li>
 * </ul>
 * Distances are in blocks for a T. rex of size 1.0 and scale with {@link ApexTheropod#reachScale()} and
 * {@link DinosaurEntity#getScale()}.
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
    /** How far from its centre the shoulder reaches what stands beside or behind it. */
    private static final double SIDE_REACH = 4.5D;
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
    /** The blow under way, and the pause after the last one: ticks left of the blow's own animation, stepping back,
     *  standing, circling. */
    private ApexTheropod.Strike strike;
    private ApexTheropod.Pause pause;
    private int holdLeft;
    private int backLeft;
    private int stareLeft;
    private int circleLeft;
    private float circleSide;
    /** The duel (06/11/2026, a big rival or a horned herbivore that fights): 0 none, 1 squaring up, 2 circling,
     *  3 going in for a blow; the ticks left of the phase. */
    private int duel;
    private int duelLeft;
    private float duelSide = 1.0F;
    /** Distance it circles at (blocks for a T. rex of size 1.0). */
    private static final double RING = 8.0D;
    private static final ApexTheropod.Strike SHOVE = new ApexTheropod.Strike("shove", 13, 28, false, true);

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
        this.endPause();
    }

    @Override
    public void stop() {
        this.mob.setDueling(false);
        this.duel = 0;
        this.mob.setAggressive(false);
        this.mob.getNavigation().stop();
        this.pending = 0;
        this.endPause();
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
        double s = this.mob.reachScale() * this.mob.getScale();
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
                boolean side = this.strike != null && this.strike.side();
                if (target.isAlive() && dist <= reach && (off < 60.0F || side) && Math.abs(target.getY() - this.mob.getY()) < 5.0D * s) {
                    if (this.mob.doHurtTarget(target)) {
                        this.mob.struck(target, this.strike);
                        if (this.strike == SHOVE) {
                            target.knockback(1.1D, this.mob.getX() - target.getX(), this.mob.getZ() - target.getZ());
                        }
                    }
                }
                this.startPause(this.strike == null ? null : this.mob.pauseAfter(this.strike));
            }
            return;
        }
        // the pause after a blow: back off facing it, stand and watch, circle; then in again. Cut short when the
        // target gets away
        if (this.holdLeft + this.backLeft + this.stareLeft + this.circleLeft > 0) {
            if (dist > DIRECT * s * 1.3D) {
                this.endPause();
            } else {
                this.pauseTick(yawTo, dist, stand);
                return;
            }
        }
        // reeling: its bite was blocked
        if (this.mob.stagger > 0) {
            this.mob.stagger--;
            this.mob.getNavigation().stop();
            this.mob.getMoveControl().strafe(-0.4F, 0.0F);
            return;
        }
        if (this.mob.duels(target) && this.duelTick(target, dist, yawTo, s)) {
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
                this.begin(this.mob.strikeFor(target));
            }
        } else if (this.cooldown <= 0 && !small && off >= 70.0F && dist <= SIDE_REACH * s + target.getBbWidth() / 2.0D
                && Math.abs(target.getY() - this.mob.getY()) < 3.0D * s) {
            // beside or behind it, out of the head's reach: an alpha shoulders it away
            ApexTheropod.Strike side = this.mob.sideStrike(target);
            if (side != null) {
                this.begin(side);
            }
        }
    }

    private void startPause(ApexTheropod.Pause p) {
        this.pause = p;
        if (p == null) {
            return;
        }
        // the blow's animation plays to its end on planted feet before the first step back
        this.holdLeft = Math.max(0, this.strike.total() - this.strike.hit());
        this.backLeft = p.back();
        this.stareLeft = p.stare() == null ? 0 : p.stareTicks();
        this.circleLeft = p.circle();
        this.circleSide = this.mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
    }

    private void endPause() {
        this.pause = null;
        this.holdLeft = 0;
        this.backLeft = 0;
        this.stareLeft = 0;
        this.circleLeft = 0;
    }

    private void pauseTick(float yawTo, double dist, double stand) {
        this.mob.getNavigation().stop();
        if (this.holdLeft > 0) {
            this.turn(yawTo, TURN * 0.6F);
            this.holdLeft--;
        } else if (this.backLeft > 0) {
            this.turn(yawTo, TURN);
            this.mob.getMoveControl().strafe(-0.55F, 0.0F);
            if (--this.backLeft == 0 && this.stareLeft > 0) {
                this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, this.pause.stare());
            }
        } else if (this.stareLeft > 0) {
            this.turn(yawTo, TURN * 0.6F);
            this.stareLeft--;
        } else {
            // sideways round it, drifting back to the distance it bites from
            this.turn(yawTo, TURN);
            float in = dist > stand + 1.5D * this.mob.getScale() ? 0.25F : dist < stand ? -0.2F : 0.0F;
            this.mob.getMoveControl().strafe(in, 0.5F * this.circleSide);
            this.circleLeft--;
        }
    }

    /**
     * The duel: square up at the ring, then circle it sideways while patience runs out, then go in: against its own
     * kind a feint or a real bite (and a shoulder shove when they are chest to chest); against horns it waits for the
     * flank and feints while the horns face it. Returns true while it handles the movement itself.
     */
    private boolean duelTick(LivingEntity target, double dist, float yawTo, double s) {
        double ring = RING * s;
        if (this.duel == 0) {
            if (dist > ring * 1.4D) {
                return false;
            }
            this.duel = 1;
            this.duelLeft = 30;
            this.duelSide = this.mob.getRandom().nextBoolean() ? 1.0F : -1.0F;
            this.mob.setDueling(true);
            if (!this.mob.hasRoaredAt(target)) {
                this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "threat");
            }
        }
        boolean rival = target instanceof ApexTheropod;
        if (this.duel == 1) {
            this.mob.getNavigation().stop();
            this.turn(yawTo, TURN);
            if (--this.duelLeft <= 0) {
                this.duel = 2;
                this.duelLeft = this.patience();
            }
            return true;
        }
        if (this.duel == 2) {
            this.mob.getNavigation().stop();
            this.turn(yawTo, TURN);
            float in = dist > ring + 1.5D * s ? 0.35F : dist < ring - 1.5D * s ? -0.35F : 0.0F;
            this.mob.getMoveControl().strafe(in, 0.42F * this.duelSide);
            if (this.mob.getRandom().nextInt(90) == 0 || this.mob.horizontalCollision) {
                this.duelSide = -this.duelSide;
            }
            // chest to chest with its own kind: the shoulder
            if (rival && dist < 4.6D * s && this.cooldown <= 0) {
                this.begin(SHOVE);
                return true;
            }
            // the other comes in (a charge, a lunge): no more circling, it fights back
            if (dist < STAND * s * 1.15D + target.getBbWidth() * 0.5D) {
                this.duel = 3;
                return false;
            }
            if (--this.duelLeft > 0) {
                return true;
            }
            boolean horns = !rival && this.faces(target, this.mob, 50.0F);
            float r = this.mob.getRandom().nextFloat();
            if ((rival && r < 0.3F) || (horns && r < 0.5F)) {
                this.mob.triggerAnim(DinosaurEntity.ACTION_CONTROLLER, "feint");
                this.duelLeft = this.patience() / 2;
            } else if (horns && r < 0.8F) {
                this.duelLeft = 20 + this.mob.getRandom().nextInt(30);   // keep circling for the flank
            } else {
                this.duel = 3;
            }
            return true;
        }
        // 3: in for a blow (the normal approach and bite); back to circling once it has struck
        return false;
    }

    private int patience() {
        return 35 + this.mob.getRandom().nextInt(45);
    }

    /** Whether {@code who} faces {@code at} within {@code angle} degrees. */
    private boolean faces(LivingEntity who, LivingEntity at, float angle) {
        double dx = at.getX() - who.getX();
        double dz = at.getZ() - who.getZ();
        float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        return Math.abs(Mth.wrapDegrees(yawTo - who.yBodyRot)) < angle;
    }

    /** Starts a blow: the animation now, the hit when it lands, the next one once it is over. */
    private void begin(ApexTheropod.Strike strike) {
        if (this.duel == 3 || strike == SHOVE) {
            this.duel = 2;
            this.duelLeft = this.patience();
        }
        this.strike = strike;
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
