package com.terrassic.entity.ai;

import com.terrassic.entity.Raptor;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * The fight of a raptor, hit and run (in place of the vanilla melee):
 * <ul>
 *   <li>It creeps up on a target it has not hit yet ("stalk"), for a moment, then runs in.</li>
 *   <li>In range it leaps ("leap"): off the ground 0.26 s in, 0.56 s in the air. The leap opens at 1.5x damage. Prey narrower
 *       than the raptor is pinned for a second ("pounce", slowness on the prey), bitten at 0.7, 1.3 and 1.9 s
 *       while it stays in reach.</li>
 *   <li>Otherwise it bites ("attack", the jaws close at 0.3 s), a sickle-claw kick ("kick", lands at 0.5 s) every third hit,
 *       hops back about 1.5 blocks and comes in again after 16 ticks. It does not trade blow for blow.</li>
 * </ul>
 */
public class RaptorStrikeGoal extends Goal {
    private enum Phase { CLOSE, WIND_UP, AIR, STRIKE, POUNCE, RECOVER }

    private static final int BITE_HIT = 6;
    private static final int KICK_HIT = 10;
    private static final int RECOVER_TICKS = 16;
    private static final int LEAP_WIND_UP = 5;
    /** Ticks in the air before it gives up on landing. */
    private static final int LEAP_LIMIT = 24;
    private static final int LEAP_COOLDOWN = 120;
    private static final double LEAP_MIN = 2.5D;
    private static final double LEAP_MAX = 6.0D;
    /** Sum of the air drag over the ticks of the leap: launch speed = distance / this. */
    private static final double LEAP_GLIDE = 6.4D;
    private static final double LEAP_LIFT = 0.42D;
    private static final double LEAP_FACTOR = 1.5D;
    private static final int[] POUNCE_BITES = {14, 26, 38};
    private static final int POUNCE_TICKS = 56;
    private static final int PIN_TICKS = 20;
    /** It creeps from this distance in, for this long at most. */
    private static final double STALK_FROM = 10.0D;
    private static final int STALK_LIMIT = 50;
    private static final double STALK_SPEED = 0.35D;
    /** Blocks it slides for each block per tick of speed once it stops pushing. */
    private static final double BRAKE = 2.0D;
    private static final double STAND_OFF = 0.8D;
    private static final int LUNGE_TICKS = 2;
    private static final double LUNGE_SPEED = 0.5D;
    /** Where it holds on to pinned prey, centre to centre, for size 1.0. */
    private static final double PIN_GAP = 1.2D;
    private static final double HOP_SPEED = 0.26D;
    private static final double HOP_DISTANCE = 1.5D;
    private static final float TURN = 25.0F;

    private final Raptor mob;
    private final double speed;
    private Phase phase = Phase.CLOSE;
    private LivingEntity lastTarget;
    /** Countdown of the phase under way (ticks up in POUNCE). */
    private int timer;
    private int repath;
    private int hits;
    private int stalkLeft;
    private int leapCooldown;
    private boolean struck;
    private boolean kicking;
    private double factor = 1.0D;

    public RaptorStrikeGoal(Raptor mob, double speed) {
        this.mob = mob;
        this.speed = speed;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        LivingEntity target = this.mob.getTarget();
        return target != null && target.isAlive() && this.mob.canAttack(target) && !this.mob.isRetreating();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity target = this.mob.getTarget();
        return target != null && target.isAlive() && !this.mob.isRetreating() && this.mob.isWithinRestriction(target.blockPosition())
                && !(target instanceof Player player && (player.isCreative() || player.isSpectator()));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        LivingEntity target = this.mob.getTarget();
        if (target != this.lastTarget) {
            this.lastTarget = target;
            this.struck = false;
            this.stalkLeft = STALK_LIMIT;
        }
        this.mob.setAggressive(true);
        this.phase = Phase.CLOSE;
        this.repath = 0;
    }

    @Override
    public void stop() {
        if (this.phase == Phase.POUNCE) {
            this.mob.stopPlaying("pounce");
        }
        this.phase = Phase.CLOSE;
        this.mob.setAggressive(false);
        this.mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        LivingEntity target = this.mob.getTarget();
        if (target == null) {
            return;
        }
        if (this.leapCooldown > 0) {
            this.leapCooldown--;
        }
        this.mob.getLookControl().setLookAt(target, 40.0F, 40.0F);
        double distance = Math.sqrt(this.mob.distanceToSqr(target));
        switch (this.phase) {
            case CLOSE -> this.close(target, distance);
            case WIND_UP -> this.windUp(target, distance);
            case AIR -> this.air(target, distance);
            case STRIKE -> this.strike(target, distance);
            case POUNCE -> this.pounce(target, distance);
            case RECOVER -> {
                this.face(target);
                this.mob.getNavigation().stop();
                if (--this.timer <= 0) {
                    this.phase = Phase.CLOSE;
                    this.repath = 0;
                }
            }
        }
    }

    private double reach(LivingEntity target) {
        return 1.35D * this.mob.getScale() + 0.6D + target.getBbWidth() / 2.0D;
    }

    private void face(LivingEntity target) {
        float yaw = (float) (Mth.atan2(target.getZ() - this.mob.getZ(), target.getX() - this.mob.getX()) * Mth.RAD_TO_DEG) - 90.0F;
        yaw = Mth.approachDegrees(this.mob.getYRot(), yaw, TURN);
        this.mob.setYRot(yaw);
        this.mob.setYBodyRot(yaw);
    }

    private void close(LivingEntity target, double distance) {
        if (this.mob.isScreeching()) {
            this.face(target);
            return;
        }
        // it stands off while the blow winds up (the target walks into its own reach meanwhile: a zombie hit first every
        // time) and allows for the braking; the lunge of strike() closes the gap as the blow lands
        if (distance <= this.reach(target) + STAND_OFF + this.mob.getDeltaMovement().horizontalDistance() * BRAKE) {
            this.beginStrike(target, 1.0D);
            return;
        }
        if (this.leapCooldown <= 0 && this.mob.onGround() && distance >= LEAP_MIN && distance <= LEAP_MAX
                && Math.abs(target.getY() - this.mob.getY()) <= 2.0D && this.mob.hasLineOfSight(target)) {
            this.leapCooldown = LEAP_COOLDOWN;
            this.mob.getNavigation().stop();
            this.mob.play("leap");
            this.phase = Phase.WIND_UP;
            this.timer = LEAP_WIND_UP;
            return;
        }
        boolean creeping = !this.struck && this.stalkLeft > 0 && distance <= STALK_FROM;
        if (creeping) {
            this.stalkLeft--;
        }
        if (--this.repath <= 0) {
            this.repath = 8;
            this.mob.getNavigation().moveTo(target, creeping ? STALK_SPEED : this.speed);
        }
    }

    private void windUp(LivingEntity target, double distance) {
        this.face(target);
        this.mob.getNavigation().stop();
        if (--this.timer > 0) {
            return;
        }
        Vec3 flat = new Vec3(target.getX() - this.mob.getX(), 0.0D, target.getZ() - this.mob.getZ());
        double run = Math.min(flat.length() - this.reach(target) * 0.6D, LEAP_MAX);
        Vec3 push = flat.lengthSqr() < 1.0E-4D ? Vec3.ZERO : flat.normalize().scale(Math.max(run, 0.5D) / LEAP_GLIDE);
        this.mob.setDeltaMovement(push.x, LEAP_LIFT, push.z);
        this.mob.hasImpulse = true;
        this.phase = Phase.AIR;
        this.timer = 0;
    }

    private void air(LivingEntity target, double distance) {
        this.timer++;
        boolean landed = this.timer > 3 && (this.mob.onGround() || this.mob.isInWater());
        if (!landed && this.timer < LEAP_LIMIT) {
            return;
        }
        if (distance > this.reach(target) + 0.5D) {
            this.phase = Phase.CLOSE;
            this.repath = 0;
        } else if (target.getBbWidth() < this.mob.getBbWidth()) {
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, PIN_TICKS, 3), this.mob);
            this.mob.play("pounce");
            this.phase = Phase.POUNCE;
            this.timer = 0;
            this.factor = LEAP_FACTOR;
        } else {
            this.beginStrike(target, LEAP_FACTOR);
        }
    }

    private void beginStrike(LivingEntity target, double hitFactor) {
        this.mob.getNavigation().stop();
        this.kicking = hitFactor == 1.0D && this.hits % 3 == 2;
        this.factor = hitFactor;
        this.mob.play(this.kicking ? "kick" : "attack");
        this.phase = Phase.STRIKE;
        this.timer = this.kicking ? KICK_HIT : BITE_HIT;
    }

    private void strike(LivingEntity target, double distance) {
        this.face(target);
        this.mob.getNavigation().stop();
        if (--this.timer > 0) {
            double gap = distance - this.reach(target) + 0.2D;
            if (this.timer == LUNGE_TICKS && gap > 0.0D && this.mob.onGround()) {
                Vec3 in = target.position().subtract(this.mob.position()).multiply(1.0D, 0.0D, 1.0D).normalize();
                this.mob.setDeltaMovement(in.scale(Math.min(gap, LUNGE_SPEED)).add(0.0D, this.mob.getDeltaMovement().y, 0.0D));
                this.mob.hasImpulse = true;
            }
            return;
        }
        if (distance <= this.reach(target) + 0.5D && this.mob.strike(target, this.factor)) {
            this.struck = true;
        }
        this.hits++;
        this.hopBack(target);
        this.phase = Phase.RECOVER;
        this.timer = RECOVER_TICKS;
    }

    private void pounce(LivingEntity target, double distance) {
        this.face(target);
        this.mob.getNavigation().stop();
        this.timer++;
        double gap = PIN_GAP * this.mob.getScale();
        if (distance > gap && this.mob.onGround() && this.timer < POUNCE_BITES[0]) {
            Vec3 in = target.position().subtract(this.mob.position()).multiply(1.0D, 0.0D, 1.0D).normalize();
            this.mob.setDeltaMovement(in.scale(Math.min(distance - gap, 0.3D)).add(0.0D, this.mob.getDeltaMovement().y, 0.0D));
        }
        for (int bite : POUNCE_BITES) {
            if (this.timer != bite) {
                continue;
            }
            if (distance > this.reach(target) + 0.5D) {
                // the prey got away: off it, back into the fight
                this.mob.stopPlaying("pounce");
                this.phase = Phase.CLOSE;
                this.repath = 0;
                return;
            }
            this.mob.strike(target, this.factor);
            this.factor = 1.0D;
            this.struck = true;
            this.hits++;
        }
        if (this.timer >= POUNCE_TICKS) {
            this.hopBack(target);
            this.phase = Phase.RECOVER;
            this.timer = RECOVER_TICKS;
        }
    }

    /** About 1.5 blocks straight back, unless that lands in a hole or in a fluid. */
    private void hopBack(LivingEntity target) {
        Vec3 back = new Vec3(this.mob.getX() - target.getX(), 0.0D, this.mob.getZ() - target.getZ());
        if (back.lengthSqr() < 1.0E-4D) {
            return;
        }
        back = back.normalize();
        Level level = this.mob.level();
        BlockPos landing = BlockPos.containing(this.mob.position().add(back.scale(HOP_DISTANCE)));
        if (!level.getFluidState(landing).isEmpty() || !level.getFluidState(landing.below()).isEmpty()
                || level.getBlockState(landing.below()).isAir() && level.getBlockState(landing.below(2)).isAir()) {
            return;
        }
        this.mob.setDeltaMovement(back.x * HOP_SPEED, HOP_SPEED, back.z * HOP_SPEED);
        this.mob.hasImpulse = true;
    }
}
