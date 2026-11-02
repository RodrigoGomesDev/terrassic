package com.terrassic.entity;

import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.control.MoveControl;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The Carnotaurus rig (tools/modelgen/handmade/carnotaurus, made for it from its own study: 34 animations of its own).
 * The life of an {@link ApexTheropod}, with what this animal does differently:
 * <ul>
 *   <li><b>No loud roar</b>: its roar is short and low. At a rival, over big prey and at a target already close it
 *       locks on instead ("lock_on": it stops, drops the head and stares with both forward eyes, the warning before
 *       the sprint); the plain roar is for what it sees from afar.</li>
 *   <li><b>A weak jaw</b>: mostly quick snaps; the heavy bite rips back with the whole body; now and then the head
 *       turns on its side and a horn flicks the target away ("hook"), which is also the blow at small things at its
 *       feet (the jaws cannot reach down there).</li>
 *   <li><b>Built for the straight line</b>: the fastest of the big predators, but a long rigid tail and long legs
 *       turn badly. A sharp turn at a sprint ends in a skid (skid_turn, or skid_turn_r to the right) that bleeds the
 *       speed off, and a sprint that ends at once in a brake with the body thrown back (brake), both kicking up the
 *       ground. Both are read from how it really moves; the brake also when a rider lets go of the run, the skid only
 *       on its own (a ridden one goes where the rider's client steers it, at up to 0.7 blocks a tick: braced legs
 *       over a 12-block slide the server cannot slow down, and every glance of the rider's camera would be a turn).</li>
 *   <li><b>Horns for rivals</b>: two wild adult males that meet do not settle it by size alone. They square up
 *       (threat: horns shown from the front, a foot scraping), walk in and shove horn to horn (shove); the weaker,
 *       most of the time the smaller, slides back and gives way for a minute, and the winner roars after it.</li>
 *   <li><b>Its own idle gestures</b>: besides the common ones, it rubs a horn on a trunk and its tiny arms twitch.</li>
 * </ul>
 */
public abstract class Abelisaur extends ApexTheropod {
    /** The cycles: pixels of ground each one covers (the stride) and its length in ticks (carnoanims.py WALK, RUN,
     *  stalk = the walk at 0.7 of the stride and 1.6 times as long). */
    private static final double WALK_PX = 70.0D;
    private static final double WALK_TICKS = 30.0D;
    private static final double RUN_PX = 128.0D;
    private static final double RUN_TICKS = 12.0D;
    private static final double STALK_PX = 49.0D;
    private static final double STALK_TICKS = 48.0D;
    private static final int LOCK_ON_TICKS = 44;
    /** Closer than this (blocks, size 1.0) a new target gets the stare instead of the roar. */
    private static final double LOCK_RANGE = 12.0D;
    private static final Strike SNAP = new Strike("attack_quick", 4, 19, false);
    private static final Strike BITE_PULL = new Strike("attack", 9, 36, false);
    private static final Strike HOOK = new Strike("hook", 9, 24, false);
    /** The feet blow plays "stomp", which this rig maps onto its hook (actionAnimation). */
    private static final Strike HOOK_LOW = new Strike("stomp", 9, 24, true);
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch", "horn_rub", "arm_twitch"};

    // ---- skid and brake (blocks per tick of real ground speed at size 1.0; a juvenile's are scaled down)
    /** A sprint: the chase runs at about 0.3 blocks a tick, the run cycle starts at 0.14 (runThresholdSqr 0.02) and a
     *  wild stroll stays under 0.17. Above 0.2 it is really running. */
    private static final double SPRINT = 0.2D;
    /** Turned this much (degrees) over the last {@link #TURN_TICKS} ticks, every one of them at a sprint: a path that
     *  bends goes a few degrees a tick, a sharp corner or a target that dodged swings the heading at once. */
    private static final float SKID_TURN = 40.0F;
    private static final int TURN_TICKS = 4;
    /** In a chase the heading hardly swings: inside 6 blocks ApexBiteGoal runs at the target only while it is within
     *  40 degrees of the nose and otherwise stops and turns on the spot (5 degrees a tick), and further out the path is
     *  re-aimed every 8 ticks; from 20 degrees off it already eases to 0.6 of its pace, so the sprint is gone within two
     *  ticks. A chase skids on the bearing instead: prey that cut across it, 20 degrees or more off the nose (where the
     *  goal gives up running straight at it) while it was at a sprint the two ticks before, and close (10 blocks at size
     *  1.0, where the goal steers it straight). Simulated on the goal's own rules: a player sprinting or walking fast
     *  across its path 6 to 12 blocks ahead makes it skid within a second or two; a straight chase never does.
     *  Through the skid it swings round at {@link #SKID_SWING} degrees a tick instead of stopping dead to turn. */
    private static final float SKID_BEARING = 20.0F;
    private static final double SKID_CHASE_RANGE = 10.0D;
    private static final float SKID_SWING = 9.0F;
    /** The brake: at least this many ticks of sprint, then under {@link #STOPPED} within {@link #BRAKE_WINDOW} ticks
     *  of the last one (letting go of the run, the ground friction takes 0.3 to under 0.07 in three ticks). */
    private static final int SPRINT_TICKS = 10;
    private static final double STOPPED = 0.07D;
    private static final int BRAKE_WINDOW = 6;
    /** Both clips are 0.9 s; the wait before the next one of either. */
    private static final int SKID_TICKS = 18;
    private static final int SKID_COOLDOWN = 40;
    private static final int BRAKE_COOLDOWN = 60;

    // ---- rival males
    /** How far it notices another male, where the horns meet (centre to centre: the foreheads sit 2.9 blocks ahead
     *  of the centre at size 1.0) and how long the squaring up may take before it gives up. */
    private static final double RIVAL_RANGE = 16.0D;
    private static final double SHOVE_GAP = 5.8D;
    private static final int THREAT_TICKS = 56;
    private static final int SQUARE_UP_LIMIT = 400;
    /** The shove clip (2.7 s): the pushing pulses run from 0.4 s to 2.2 s at 1.2 a second. */
    private static final int SHOVE_TICKS = 54;
    private static final int PUSH_FROM = 8;
    private static final int PUSH_TO = 44;
    /** The loser keeps out of the winner's way this long; neither starts another contest before the cooldown. */
    private static final int GIVE_WAY_TICKS = 1200;
    private static final int RIVAL_COOLDOWN = 2400;

    /** Ground speed and heading of the last ticks (newest first), measured on its own position: a mob moves after its
     *  AI step, and a ridden one is moved by its rider's client, so getDeltaMovement() would miss either. */
    private final double[] speeds = new double[SPRINT_TICKS + BRAKE_WINDOW];
    private final float[] turns = new float[TURN_TICKS];
    private double lastX = Double.NaN;
    private double lastZ;
    private float lastYaw;
    /** Game tick until which the action clip under way should be left alone (a blow, the rider's bite, ours). */
    private int busyUntil;
    private int skidCooldown;
    private int brakeCooldown;
    /** Ticks into the skid under way (0 = none). */
    private int skidding;
    private boolean skidRight;
    /** The skid under way came from prey cutting across it (it swings round to it). */
    private boolean skidAtTarget;
    /** Ticks into the brake under way (0 = none). */
    private int braking;

    /** The male it is squaring up to (-1 = none), ticks since it began, ticks into the shove (-1 = not yet). */
    private int rivalId = -1;
    private int rivalTicks;
    private int shoveTick = -1;
    /** Decided by the pair's leader (lower id) when the shove starts: who slides back. */
    private boolean losing;
    private int rivalCooldown = 600;
    private int lostTo = -1;
    private int lostUntil;

    protected Abelisaur(EntityType<? extends Abelisaur> type, Level level) {
        super(type, level);
    }

    @Override
    protected String[] extraActions() {
        return new String[]{"roar", "attack_quick", "call", "threat", "drink", "sniff", "look_back", "shake", "yawn", "stretch",
                "stomp", "hook", "lock_on", "shove", "horn_rub", "arm_twitch", "skid_turn", "skid_turn_r", "brake"};
    }

    @Override
    protected String actionAnimation(String trigger) {
        return "stomp".equals(trigger) ? "hook" : trigger;
    }

    @Override
    protected String[] gestures() {
        return GESTURES;
    }

    @Override
    protected double walkCycleSpeed() {
        return WALK_PX / 16.0D / WALK_TICKS * this.modelScale();
    }

    @Override
    protected double runCycleSpeed() {
        return RUN_PX / 16.0D / RUN_TICKS * this.modelScale();
    }

    @Override
    protected double stalkCycleSpeed() {
        return STALK_PX / 16.0D / STALK_TICKS * this.modelScale();
    }

    @Override
    protected String loudAnim() {
        return "lock_on";
    }

    @Override
    protected int loudTicks() {
        return LOCK_ON_TICKS;
    }

    @Override
    protected boolean loudShakesAir() {
        return false;
    }

    /** A target already close gets the stare; the roar is for what it sees from afar. */
    @Override
    public void roar() {
        LivingEntity target = this.getTarget();
        double range = LOCK_RANGE * this.getScale();
        if (target != null && !this.isTame() && this.distanceToSqr(target) < range * range) {
            this.roarLoud();
        } else {
            super.roar();
        }
    }

    /** Its bite tip stops 4.3 blocks ahead (attack), the T. rex's 6.5 blocks: the same rig units at 16 / 24. */
    @Override
    public double reachScale() {
        return 0.667D;
    }

    @Override
    public Strike feetStrike() {
        this.busy(HOOK_LOW.total());
        return HOOK_LOW;
    }

    /** Asked once per blow, when it starts (ApexBiteGoal): the clip it picks is left to play out. */
    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        Strike strike = r < 0.55F ? SNAP : (r < 0.85F ? BITE_PULL : HOOK);
        this.busy(strike.total());
        return strike;
    }

    @Override
    protected void startRiderAttack(LivingEntity target) {
        super.startRiderAttack(target);
        this.busy(HOOK.total());
    }

    private void busy(int ticks) {
        this.busyUntil = Math.max(this.busyUntil, this.tickCount + ticks);
    }

    /** Nothing else on the action clip: no blow, roar or rider bite under way. */
    private boolean actionFree() {
        return this.tickCount >= this.busyUntil && !this.isRoaring();
    }

    // ------------------------------------------------------------------ the day

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        ServerLevel level = (ServerLevel) this.level();
        this.measure();
        this.skidAndBrake(level);
        if (this.rivalCooldown > 0) {
            this.rivalCooldown--;
        }
        if (this.rivalId >= 0) {
            this.rivalTick(level);
        } else if ((this.tickCount + this.getId()) % 20 == 0 && this.rivalCooldown <= 0) {
            this.lookForRival(level);
        }
    }

    /** Ground speed and turn of this tick, pushed in front of the last ones. */
    private void measure() {
        double x = this.getX();
        double z = this.getZ();
        float yaw = this.getYRot();
        double speed = 0.0D;
        float turn = 0.0F;
        if (!Double.isNaN(this.lastX)) {
            double dx = x - this.lastX;
            double dz = z - this.lastZ;
            // a jump of more than a block and a half in one tick is a teleport, not a run (ridden flat out is 0.7)
            speed = Math.sqrt(dx * dx + dz * dz);
            if (speed > 1.5D) {
                speed = 0.0D;
            }
            turn = Mth.wrapDegrees(yaw - this.lastYaw);
        }
        System.arraycopy(this.speeds, 0, this.speeds, 1, this.speeds.length - 1);
        System.arraycopy(this.turns, 0, this.turns, 1, this.turns.length - 1);
        this.speeds[0] = speed;
        this.turns[0] = turn;
        this.lastX = x;
        this.lastZ = z;
        this.lastYaw = yaw;
    }

    /** Up on its feet on firm ground, free to play a clip of its own. */
    private boolean footing() {
        return this.isAlive() && this.onGround() && !this.isInWater() && !this.isSleeping() && !this.isKnockedOut()
                && !this.isInSittingPose() && !this.isPassenger();
    }

    private void skidAndBrake(ServerLevel level) {
        if (this.skidCooldown > 0) {
            this.skidCooldown--;
        }
        if (this.brakeCooldown > 0) {
            this.brakeCooldown--;
        }
        if (this.skidding > 0) {
            this.skidTick(level);
        }
        if (this.braking > 0) {
            this.brakeTick(level);
        }
        if (!this.footing() || !this.actionFree() || this.shoveTick >= 0) {
            return;
        }
        // a juvenile runs slower: the same thresholds at its size (half at most)
        double sprint = SPRINT * Mth.clamp(this.getScale(), 0.5D, 1.0D);
        float turned = 0.0F;
        boolean fast = true;
        for (int i = 0; i < TURN_TICKS; i++) {
            turned += this.turns[i];
            fast &= this.speeds[i] >= sprint;
        }
        if (this.skidCooldown <= 0 && !this.isVehicle()) {
            // a heading that grows turns it to the right (south to west): the clip that leans that way
            if (fast && Math.abs(turned) >= SKID_TURN) {
                this.skid(turned > 0.0F, false);
                return;
            }
            float bearing = this.chaseBearing();
            if (Math.abs(bearing) >= SKID_BEARING && this.speeds[0] >= sprint * 0.75D && this.speeds[1] >= sprint
                    && this.speeds[2] >= sprint) {
                this.skid(bearing > 0.0F, true);
                return;
            }
        }
        if (this.brakeCooldown <= 0 && this.speeds[0] < STOPPED && !this.horizontalCollision && this.sprintedThenStopped(sprint)) {
            this.triggerAnim(ACTION_CONTROLLER, "brake");
            this.busy(SKID_TICKS);
            this.braking = 1;
            this.brakeCooldown = BRAKE_COOLDOWN;
            // the turn-in that came with the stop is not a skid as well
            this.skidCooldown = Math.max(this.skidCooldown, SKID_TICKS);
        }
    }

    private void skid(boolean right, boolean atTarget) {
        this.skidRight = right;
        this.skidAtTarget = atTarget;
        this.triggerAnim(ACTION_CONTROLLER, right ? "skid_turn_r" : "skid_turn");
        this.busy(SKID_TICKS);
        this.skidding = 1;
        this.skidCooldown = SKID_COOLDOWN;
    }

    /** How far off the nose the prey it chases is (degrees, + to its right), 0 when it is not chasing anything close. */
    private float chaseBearing() {
        LivingEntity target = this.getTarget();
        if (target == null || !target.isAlive() || !this.isAggressive()) {
            return 0.0F;
        }
        double dx = target.getX() - this.getX();
        double dz = target.getZ() - this.getZ();
        double range = SKID_CHASE_RANGE * this.getScale();
        if (dx * dx + dz * dz > range * range) {
            return 0.0F;
        }
        return Mth.wrapDegrees((float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F - this.getYRot());
    }

    /** The last tick at a sprint was a few ticks ago, after a run of at least {@link #SPRINT_TICKS} of them. A stop
     *  that eased off over a longer stretch (pace 0.5 near the prey, a path ending) is a plain stop. */
    private boolean sprintedThenStopped(double sprint) {
        int last = -1;
        for (int i = 1; i <= BRAKE_WINDOW; i++) {
            if (this.speeds[i] >= sprint) {
                last = i;
                break;
            }
        }
        if (last < 0) {
            return false;
        }
        for (int i = last; i < last + SPRINT_TICKS && i < this.speeds.length; i++) {
            if (this.speeds[i] < sprint * 0.8D) {
                return false;
            }
        }
        return last + SPRINT_TICKS <= this.speeds.length;
    }

    /** The skid: the feet are planted (the clip holds them from 0.15 s to 0.6 s), so the run is held back meanwhile
     *  and the body slides a block or two on its speed, the outer foot throwing up the ground; then it runs on. */
    private void skidTick(ServerLevel level) {
        int t = this.skidding++;
        if (t >= SKID_TICKS || this.isVehicle()) {
            this.skidding = 0;
            return;
        }
        if (t >= 2 && t <= 12) {
            // half the pull of the legs (a quarter of the push: the ground speed goes with its square) and the
            // slide eats the rest: about 0.3 to under 0.1 blocks a tick in four ticks
            MoveControl move = this.getMoveControl();
            if (move.hasWanted()) {
                move.setWantedPosition(move.getWantedX(), move.getWantedY(), move.getWantedZ(), move.getSpeedModifier() * 0.5D);
            }
            this.setDeltaMovement(this.getDeltaMovement().multiply(0.8D, 1.0D, 0.8D));
            LivingEntity target = this.getTarget();
            if (this.skidAtTarget && target != null) {
                // swinging round on the slide, faster than the goal's turn on the spot
                float yaw = Mth.approachDegrees(this.getYRot(), this.getYRot() + this.chaseBearing(), SKID_SWING);
                this.setYRot(yaw);
                this.setYBodyRot(yaw);
            }
            // the outer side of the curve: the left foot on a right turn
            this.kickUp(level, this.skidRight ? -1.0D : 1.0D, 0.0D, 2);
        }
    }

    /** The brake: both feet pushed forward dig in, dust in front of them for the first half of the clip. */
    private void brakeTick(ServerLevel level) {
        int t = this.braking++;
        if (t >= SKID_TICKS) {
            this.braking = 0;
            return;
        }
        if (t <= 9) {
            this.kickUp(level, -1.0D, 0.6D, 1);
            this.kickUp(level, 1.0D, 0.6D, 1);
        }
    }

    /** Ground dust at one foot: side -1 = its left, +1 = its right, forward in blocks at size 1.0. */
    private void kickUp(ServerLevel level, double side, double forward, int count) {
        BlockState ground = level.getBlockState(this.getBlockPosBelowThatAffectsMyMovement());
        if (ground.isAir()) {
            return;
        }
        double k = this.modelScale() * this.getScale() * 1.5D;
        float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
        // facing (-sin, cos); its right hand is (-cos, -sin)
        double fx = -Mth.sin(yaw);
        double fz = Mth.cos(yaw);
        double x = this.getX() + fx * forward * k - fz * side * 0.6D * k;
        double z = this.getZ() + fz * forward * k + fx * side * 0.6D * k;
        level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), x, this.getY() + 0.1D, z, count,
                0.15D, 0.05D, 0.15D, 0.12D);
    }

    // ------------------------------------------------------------------ rival males

    /** A wild grown male, free to take on another: no prey in mind, no rider, awake, not just beaten. */
    private boolean canSquareUp() {
        return this.footing() && !this.isBaby() && !this.isTame() && !this.isFemale() && this.getTarget() == null
                && !this.isVehicle() && !this.isLeashed() && !this.isRoaring() && this.tickCount >= this.lostUntil;
    }

    private void lookForRival(ServerLevel level) {
        if (!this.canSquareUp() || !this.getNavigation().isDone() && this.speeds[0] >= SPRINT) {
            return;
        }
        double range = RIVAL_RANGE * this.getScale();
        Abelisaur best = null;
        double bestD = range * range;
        for (Abelisaur other : level.getEntitiesOfClass(Abelisaur.class, this.getBoundingBox().inflate(range),
                e -> e != this && e.getClass() == this.getClass() && e.rivalId < 0 && e.rivalCooldown <= 0 && e.canSquareUp())) {
            double d = this.distanceToSqr(other);
            if (d < bestD) {
                bestD = d;
                best = other;
            }
        }
        if (best != null) {
            this.squareUp(best);
            best.squareUp(this);
        }
    }

    /** The challenge: it turns to the other, shows the horns from the front and scrapes a foot, with a low growl. */
    private void squareUp(Abelisaur other) {
        this.rivalId = other.getId();
        this.rivalTicks = 0;
        this.shoveTick = -1;
        this.losing = false;
        this.getNavigation().stop();
        this.triggerAnim(ACTION_CONTROLLER, "threat");
        this.busy(THREAT_TICKS);
        this.playSound(this.roarSound(), 1.4F, 0.7F * this.getVoicePitch());
    }

    private void endRivalry(int cooldown) {
        this.rivalId = -1;
        this.shoveTick = -1;
        this.rivalTicks = 0;
        this.losing = false;
        this.rivalCooldown = cooldown;
    }

    private void rivalTick(ServerLevel level) {
        Entity e = level.getEntity(this.rivalId);
        if (!(e instanceof Abelisaur other) || !other.isAlive() || other.rivalId != this.getId()) {
            this.endRivalry(600);
            return;
        }
        double dist = Math.sqrt(this.distanceToSqr(other));
        boolean shoving = this.shoveTick >= 0;
        // anything else that comes up (prey, a hit, a rider, sleep) or one that wandered off ends it
        boolean fit = shoving ? this.isAlive() && this.getTarget() == null && !this.isVehicle() && !this.isKnockedOut()
                : this.canSquareUp() || !this.onGround() && this.isAlive() && this.getTarget() == null;
        if (!fit || dist > RIVAL_RANGE * this.getScale() * 1.5D || ++this.rivalTicks > SQUARE_UP_LIMIT + SHOVE_TICKS) {
            this.endRivalry(600);
            other.endRivalry(600);
            return;
        }
        // face it the whole time, body and head
        double dx = other.getX() - this.getX();
        double dz = other.getZ() - this.getZ();
        float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        float yaw = Mth.approachDegrees(this.getYRot(), yawTo, shoving ? 3.0F : 8.0F);
        this.setYRot(yaw);
        this.setYBodyRot(yaw);
        this.getLookControl().setLookAt(other, 30.0F, 30.0F);
        this.getNavigation().stop();
        double gap = SHOVE_GAP * (this.getScale() + other.getScale()) / 2.0D;
        if (shoving) {
            this.shoveTick(level, other, dx / Math.max(dist, 1.0E-3D), dz / Math.max(dist, 1.0E-3D));
            return;
        }
        if (this.rivalTicks <= THREAT_TICKS) {
            return;
        }
        if (dist > gap + 0.3D) {
            // walking in head on (the stroll's pace), slowing for the last two blocks so it stops where the horns meet
            float off = Math.abs(Mth.wrapDegrees(yawTo - this.getYRot()));
            if (off < 30.0F) {
                double pace = dist < gap + 2.0D ? 0.45D : 0.8D;
                this.getMoveControl().setWantedPosition(other.getX(), other.getY(), other.getZ(), pace);
            }
        } else if (this.getId() < other.getId() && other.rivalTicks > THREAT_TICKS && other.shoveTick < 0
                && Math.abs(Mth.wrapDegrees(yawTo - this.getYRot())) < 25.0F && other.facing(this, 25.0F)) {
            // the pair's leader starts the shove for both and decides it: size counts most, then how hurt each is
            double a = this.strength();
            double b = other.strength();
            boolean thisLoses = this.getRandom().nextDouble() * (a + b) >= a;
            this.startShove(thisLoses);
            other.startShove(!thisLoses);
            this.playSound(SoundEvents.GOAT_RAM_IMPACT, 1.2F, 0.55F);
        }
    }

    private boolean facing(Entity other, float within) {
        double dx = other.getX() - this.getX();
        double dz = other.getZ() - this.getZ();
        float yawTo = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        return Math.abs(Mth.wrapDegrees(yawTo - this.getYRot())) < within;
    }

    /** Size to the fourth power (a 10% bigger male wins about 6 times in 10), weighed by health. */
    private double strength() {
        double s = this.getAdultSize();
        return s * s * s * s * (0.4D + 0.6D * this.getHealth() / this.getMaxHealth());
    }

    private void startShove(boolean loses) {
        this.shoveTick = 0;
        this.losing = loses;
        this.triggerAnim(ACTION_CONTROLLER, "shove");
        this.busy(SHOVE_TICKS);
    }

    /** Horn to horn: the loser slides back with each pulse of the push; at the end it gives way, the winner keeps the
     *  ground (ApexTheropod's rival roar goes after the one that gives way). */
    private void shoveTick(ServerLevel level, Abelisaur other, double nx, double nz) {
        int t = this.shoveTick++;
        if (this.losing && t >= PUSH_FROM && t <= PUSH_TO) {
            double push = Math.max(0.0D, Math.sin(2.0D * Math.PI * 1.2D * (t - PUSH_FROM) / 20.0D));
            // away from the winner, along the line between them
            this.setDeltaMovement(this.getDeltaMovement().add(-nx * 0.05D * push, 0.0D, -nz * 0.05D * push));
            if (t % 4 == 0) {
                this.kickUp(level, -1.0D, 0.0D, 1);
                this.kickUp(level, 1.0D, 0.0D, 1);
            }
        }
        if (t >= SHOVE_TICKS) {
            if (this.losing) {
                this.lostTo = other.getId();
                this.lostUntil = this.tickCount + GIVE_WAY_TICKS;
            }
            this.endRivalry(RIVAL_COOLDOWN + this.getRandom().nextInt(RIVAL_COOLDOWN / 2));
        }
    }

    /** Two males settle it with the horns, not by size alone: after a shove the loser gives way to the winner for a
     *  while; any other pair goes by the usual rule (the smaller wild adult steps out of the bigger one's way). */
    @Override
    protected boolean givesWayTo(ApexTheropod rival) {
        if (rival instanceof Abelisaur male && rival.getClass() == this.getClass() && !this.isFemale() && !male.isFemale()
                && !this.isTame() && !rival.isTame() && !this.isBaby() && !rival.isBaby()) {
            return male.getId() == this.lostTo && this.tickCount < this.lostUntil && this.getTarget() == null;
        }
        return super.givesWayTo(rival);
    }
}
