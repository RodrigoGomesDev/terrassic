package com.terrassic.entity;

import com.terrassic.entity.ai.PackAmbushGoal;
import com.terrassic.entity.ai.PackDriveGoal;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

import java.util.UUID;

/**
 * The Albertosaurus rig (tools/modelgen/handmade/albertosaurus, made for it from its own study,
 * docs/estudos/13_PREDADORES_1_10.md, in the 1.10.1 standard of the Daspletosaurus pilot). The life of an
 * {@link ApexTheropod}, with what the runner of the tyrannosaurids does differently:
 * <ul>
 *   <li><b>The pack of mixed ages</b> (Dry Island, Currie 1998; a hypothesis the Guide says is one): a natural group
 *       of two to four, the first two grown, the others juveniles at about 0.55 to 0.65 of the adult size. Packmates
 *       never make each other give way.</li>
 *   <li><b>The call and the answer</b>: a wild adult that takes a target calls the pack ("call_pack", head up); the
 *       others within 24 blocks answer ("answer") and come onto the same target.</li>
 *   <li><b>The drive</b> ({@link PackDriveGoal}, {@link PackAmbushGoal}): the faster juveniles run round the prey in a
 *       wide arc ("drive") and come at it from the far side, so it bolts toward the adults, who wait crouched
 *       ("ambush_crouch") and strike when it arrives.</li>
 *   <li><b>The long chase</b>: the one big predator that does not give up at 48 blocks; it keeps on for 72 blocks or
 *       30 s without landing a blow ("sprint"), and only then gives up, stands panting ("pant") and walks spent for
 *       a while ("walk_tired", "idle_tired"), not hunting.</li>
 *   <li><b>The runner's duel</b>: of the tyrannosaurids it dodges most and blocks least (ai/DuelStyle); its dodge is a
 *       hop aside ("sidestep") and its counter and signature blow bite the rival's neck while going past
 *       ("pass_bite"). Its own bite is light: it shuts and lets go ("attack"), and it snaps on the run ("snap_bite").</li>
 * </ul>
 * DinosaurEntity gives a chase up 48 blocks from where it began or after 20 s without a blow (behaviourTick, private).
 * The longer chase is made here with existing overridable methods only: while its own chase is within 72 blocks and
 * 30 s, {@link #getTarget()} reads null for one tick now and then inside the AI step, which restarts the base count,
 * and the run does not wear it out ({@link #runThresholdSqr()} on the server); it gives up by its own rule.
 */
public abstract class Albertosaurine extends ApexTheropod {
    /** One short line when a behaviour of its own fires ("[alberto] ..."), for the playtests in a generated world. */
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    /** The cycles (albertoanims.py WALK, RUN, SPRINT, STALK): pixels of ground per cycle (stride x K = 0.8) and ticks. */
    private static final double WALK_PX = 67.2D;
    private static final double WALK_TICKS = 36.0D;
    private static final double RUN_PX = 112.0D;
    private static final double RUN_TICKS = 16.0D;
    private static final double SPRINT_PX = 132.8D;
    private static final double SPRINT_TICKS = 14.0D;
    private static final double STALK_PX = 47.04D;
    private static final double STALK_TICKS = 54.0D;
    /** The blows, timed to the jaws in albertoanims.py / albertofight.py (tick the hit lands, ticks to the next). */
    private static final Strike BITE = new Strike("attack", 10, 28, false);
    private static final Strike SNAP = new Strike("snap_bite", 5, 14, false);
    private static final Strike QUICK = new Strike("attack_quick", 6, 18, false);
    private static final Strike LOW = new Strike("bite_low", 8, 24, false);
    private static final Strike SIDE = new Strike("bite_side", 9, 26, false);
    private static final Strike PASS_BITE = new Strike("pass_bite", 9, 26, false);
    /** The long chase: blocks from where it began, and ticks without landing a blow. */
    private static final double CHASE_BLOCKS = 72.0D;
    private static final int CHASE_TICKS = 600;
    /** Spent after it: ticks it walks tired and does not hunt, and how much slower. */
    private static final int SPENT_TICKS = 500;
    private static final UUID SPENT_SLOW = UUID.fromString("5a0c7e2b-41d9-4c6f-8e13-2b9d7f60a1c4");
    /** The call reaches the pack this far (blocks); the next call after this many ticks. */
    public static final double CALL_REACH = 24.0D;
    private static final int CALL_COOLDOWN = 600;
    /** The juveniles of a natural pack: ages for 0.55 .. 0.65 of the adult size (a 0.28 hatchling at -24000). */
    private static final int JUVENILE_AGE_MIN = -15000;
    private static final int JUVENILE_AGE_MAX = -12000;
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch", "snort", "settle",
            "settle", "scan", "scan", "scan"};
    private static final String[] OWN = {"call_pack", "answer", "pant", "snap_bite", "sidestep", "pass_bite"};

    /** What the movement loop shows: 0 nothing of its own, 1 crouched in ambush, 2 driving prey, 3 the long chase's
     *  sprint, 4 spent. */
    public static final byte MODE_NONE = 0;
    public static final byte MODE_AMBUSH = 1;
    public static final byte MODE_DRIVE = 2;
    public static final byte MODE_SPRINT = 3;
    public static final byte MODE_SPENT = 4;
    private static final EntityDataAccessor<Byte> DATA_MODE = SynchedEntityData.defineId(Albertosaurine.class, EntityDataSerializers.BYTE);

    private RawAnimation ambushAnim;
    private RawAnimation driveAnim;
    private RawAnimation sprintAnim;
    private RawAnimation spentWalkAnim;
    private RawAnimation spentIdleAnim;

    // server: the long chase
    private UUID chaseOf;
    private Vec3 chaseStart;
    private int chaseTick;
    private Vec3 baseStart;
    private int baseTick;
    private boolean hideTarget;
    private UUID gaveUpOn;
    private int gaveUpUntil;
    private int spentLeft;
    private boolean longChaseLogged;
    // server: the pack call and the answer
    private int callCooldown = 100;
    private boolean packCalling;
    private boolean answering;
    private int answerIn;
    private LivingEntity answerTarget;
    private Albertosaurine answerTo;
    /** Server, for a juvenile: the prey the pack hunts and the adult that called (PackDriveGoal reads them). */
    public LivingEntity drivePrey;
    public Albertosaurine driveLeader;
    public int driveSince;

    protected Albertosaurine(EntityType<? extends Albertosaurine> type, Level level) {
        super(type, level);
    }

    /** Logs one behaviour line: "[alberto] what (#id x y z)". */
    public void logAct(String what) {
        LOG.info("[alberto] {} (#{} {} {} {})", what, this.getId(), this.getBlockX(), this.getBlockY(), this.getBlockZ());
    }

    /** ai/DuelGoal: a duel move started; its own ones (the pass bite, the parry that ends in one) are logged. */
    public static void duelMove(DinosaurEntity mob, String anim) {
        if (mob instanceof Albertosaurine a && ("pass_bite".equals(anim) || "parry".equals(anim))) {
            a.logAct("parry".equals(anim) ? "pass bite (parry counter)" : "pass bite");
        }
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_MODE, MODE_NONE);
    }

    public byte mode() {
        return this.entityData.get(DATA_MODE);
    }

    public void setMode(byte mode) {
        if (this.mode() != mode) {
            this.entityData.set(DATA_MODE, mode);
        }
    }

    // ------------------------------------------------------------------ the sets it has (its own class: no shared list)

    @Override
    public boolean hasDuelMoves() {
        return true;
    }

    @Override
    public boolean hasLivelySet() {
        return true;
    }

    @Override
    protected String[] extraActions() {
        String[] common = super.extraActions();
        String[] all = java.util.Arrays.copyOf(common, common.length + OWN.length);
        System.arraycopy(OWN, 0, all, common.length, OWN.length);
        return all;
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

    /** Its bite tip, against the T. rex's the distances were measured on: a long low head on a smaller rig. */
    @Override
    public double reachScale() {
        return 0.82D;
    }

    // ------------------------------------------------------------------ blows and the duel

    /** A light biter: quick snaps and the bite that lets go; the low sweep for small things. */
    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        if (target.getBbHeight() < 1.4F && r < 0.45F) {
            return LOW;
        }
        return r < 0.3F ? SNAP : r < 0.65F ? BITE : r < 0.85F ? SIDE : QUICK;
    }

    /** After a bite it is already stepping back out of reach (it bites and goes). */
    @Override
    public Pause pauseAfter(Strike strike) {
        Pause alpha = super.pauseAfter(strike);
        if (alpha != null) {
            return alpha;
        }
        return strike == BITE || strike == SIDE ? new Pause(10, null, 0, 8) : null;
    }

    /** Chest to chest with a rival: it steps out and bites the neck going past. */
    @Override
    public Strike closeStrike() {
        return PASS_BITE;
    }

    /** The duel brain's sidestep: the hop aside. */
    @Override
    public void incomingDodge(int ticks) {
        super.incomingDodge(ticks);
        this.triggerAnim(ACTION_CONTROLLER, "sidestep");
        this.logAct("sidestep");
    }

    // ------------------------------------------------------------------ the pack

    /** It lives in a pack: packmates keep near and never make each other give way. */
    @Override
    protected boolean solitary() {
        return false;
    }

    @Override
    protected boolean givesWayTo(ApexTheropod rival) {
        return false;
    }

    /** A natural pack: the first two grown, the third and fourth juveniles. The group data is ours from the first one
     *  on (the spawners pass it from one to the next), so ApexTheropod's own juveniles stay out of it. */
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        SpawnGroupData spawnData, CompoundTag tag) {
        boolean natural = reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION;
        if (natural && spawnData == null) {
            spawnData = new Pack();
        }
        if (spawnData instanceof Pack pack && pack.getGroupSize() >= 2 && !this.isTame() && this.getAge() == 0) {
            this.setAge(JUVENILE_AGE_MIN + this.random.nextInt(JUVENILE_AGE_MAX - JUVENILE_AGE_MIN + 1));
            this.logAct("pack: a juvenile (" + (pack.getGroupSize() + 1) + "th of the pack)");
        } else if (spawnData instanceof Pack pack) {
            this.logAct("pack: an adult (" + (pack.getGroupSize() + 1) + (pack.getGroupSize() == 0 ? "st" : "nd") + " of the pack)");
        }
        return super.finalizeSpawn(level, difficulty, reason, spawnData, tag);
    }

    /** The group data of a natural pack (no random babies: only the third and the fourth are young). */
    public static final class Pack extends AgeableMob.AgeableMobGroupData {
        public Pack() {
            super(false);
        }
    }

    /** A juvenile of the pack old enough to drive prey (not a hatchling). */
    public boolean isDriver() {
        return this.isBaby() && this.getAge() >= -17000 && !this.isTame();
    }

    @Override
    protected void addExtraGoals() {
        super.addExtraGoals();
        this.goalSelector.addGoal(2, new PackDriveGoal(this));
        this.goalSelector.addGoal(2, new PackAmbushGoal(this));
    }

    /** A wild adult taking a target calls the pack (instead of the roar), and the others answer and come onto it. */
    @Override
    public void setTarget(LivingEntity target) {
        LivingEntity previous = this.getTarget();
        boolean call = !this.level().isClientSide() && target != null && previous == null && !this.answering && !this.isTame()
                && !this.isBaby() && !this.isVehicle() && this.isAlive() && this.callCooldown <= 0
                && !(target instanceof Albertosaurine) && !this.packAround().isEmpty();
        if (call) {
            this.packCalling = true;
        }
        super.setTarget(target);
        if (!call) {
            return;
        }
        this.callCooldown = CALL_COOLDOWN;
        if (!this.isRoaring()) {
            this.roar();
        }
        int n = 0;
        for (Albertosaurine other : this.packAround()) {
            if (other.getTarget() == null && other.answerIn <= 0) {
                other.answerTo = this;
                other.answerTarget = target;
                other.answerIn = 14 + n * 8 + this.random.nextInt(10);
                n++;
            }
        }
        this.logAct("pack call: " + n + " answer, on a " + target.getType().toShortString());
    }

    /** The wild packmates within the call's reach (the juveniles too). */
    public java.util.List<Albertosaurine> packAround() {
        return this.level().getEntitiesOfClass(Albertosaurine.class, this.getBoundingBox().inflate(CALL_REACH),
                e -> e != this && e.isAlive() && !e.isTame() && e.getType() == this.getType() && !e.isKnockedOut());
    }

    /** The roar on a new target becomes the pack call while it calls; an answer has no roar of its own. */
    @Override
    public void roar() {
        if (this.answering) {
            return;
        }
        super.roar();
        if (this.packCalling && this.isRoaring()) {
            this.triggerAnim(ACTION_CONTROLLER, "call_pack");
        }
    }

    // ------------------------------------------------------------------ the long chase

    /** While its own chase runs, the run does not wear it out (the base fatigue): it tires by its own rule. */
    @Override
    protected double runThresholdSqr() {
        if (!this.level().isClientSide() && this.chaseOf != null) {
            return 1.0E9D;
        }
        return 0.02D;
    }

    /** One tick now and then inside the AI step, the target reads null: DinosaurEntity's count starts over. */
    @Override
    public LivingEntity getTarget() {
        return this.hideTarget ? null : super.getTarget();
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (target != null && !this.isTame() && target.getUUID().equals(this.gaveUpOn) && this.tickCount < this.gaveUpUntil) {
            return false;
        }
        return super.canAttack(target);
    }

    /** Spent after the long chase, it does not hunt. */
    @Override
    protected boolean canHunt() {
        return super.canHunt() && this.spentLeft <= 0;
    }

    @Override
    protected void customServerAiStep() {
        this.hideTarget = this.hidesTargetNow();
        try {
            super.customServerAiStep();
        } finally {
            this.hideTarget = false;
        }
        if (this.callCooldown > 0) {
            this.callCooldown--;
        }
        if (this.packCalling && !this.isRoaring()) {
            this.packCalling = false;
        }
        this.answerTick();
        this.chaseTick();
        this.spentTick();
        this.modeTick();
    }

    /** Whether to blank the target for this tick: its own chase is on, within its 72 blocks and 30 s, and the base
     *  count is near its own 48 blocks or 20 s. Never on the ticks the base or the pack read the target. */
    private boolean hidesTargetNow() {
        LivingEntity t = super.getTarget();
        if (t == null || this.chaseOf == null || this.isTame() || this.isDueling() || !t.isAlive()
                || !t.getUUID().equals(this.chaseOf) || this.tickCount % 20 != 7 || (this.tickCount + this.getId()) % 20 == 0) {
            return false;
        }
        boolean baseNear = (this.baseStart != null && this.position().distanceToSqr(this.baseStart) > 34.0D * 34.0D)
                || this.tickCount - Math.max(this.baseTick, this.getLastHurtMobTimestamp()) > 300;
        if (baseNear) {
            this.baseStart = this.position();
            this.baseTick = this.tickCount;
            if (!this.longChaseLogged && this.chaseStart != null && this.position().distanceToSqr(this.chaseStart) > 46.0D * 46.0D) {
                this.longChaseLogged = true;
                this.logAct(String.format(java.util.Locale.ROOT, "long chase: still on past 48 blocks (%.0f)",
                        Math.sqrt(this.position().distanceToSqr(this.chaseStart))));
            }
            return true;
        }
        return false;
    }

    private void chaseTick() {
        LivingEntity t = super.getTarget();
        if (t == null || this.isTame() || this.isDueling() || this.isVehicle() || !t.isAlive()) {
            this.chaseOf = null;
            return;
        }
        if (!t.getUUID().equals(this.chaseOf)) {
            this.chaseOf = t.getUUID();
            this.chaseStart = this.position();
            this.chaseTick = this.tickCount;
            this.baseStart = this.position();
            this.baseTick = this.tickCount;
            this.longChaseLogged = false;
            return;
        }
        if (this.tickCount % 20 != 3) {
            return;
        }
        int sinceHit = this.tickCount - Math.max(this.chaseTick, this.getLastHurtMobTimestamp());
        double gone = Math.sqrt(this.position().distanceToSqr(this.chaseStart));
        if (gone > CHASE_BLOCKS || sinceHit > CHASE_TICKS) {
            this.logAct(String.format(java.util.Locale.ROOT, "long chase: gives up after %.0f blocks, %d s without a blow; spent",
                    gone, sinceHit / 20));
            this.gaveUpOn = t.getUUID();
            this.gaveUpUntil = this.tickCount + 600;
            this.chaseOf = null;
            this.setTarget(null);
            this.startSpent();
        }
    }

    private void startSpent() {
        this.spentLeft = SPENT_TICKS;
        this.getNavigation().stop();
        this.triggerAnim(ACTION_CONTROLLER, "pant");
        AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(SPENT_SLOW);
            speed.addTransientModifier(new AttributeModifier(SPENT_SLOW, "spent", -0.35D, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
    }

    private void spentTick() {
        if (this.spentLeft <= 0) {
            return;
        }
        if (--this.spentLeft == 0 || this.isTame()) {
            this.spentLeft = 0;
            AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
            if (speed != null) {
                speed.removeModifier(SPENT_SLOW);
            }
            this.logAct("spent: has its breath back");
        }
    }

    public boolean isSpent() {
        return this.spentLeft > 0;
    }

    // ------------------------------------------------------------------ the answer

    private void answerTick() {
        if (this.answerIn <= 0) {
            return;
        }
        if (--this.answerIn > 0) {
            return;
        }
        LivingEntity target = this.answerTarget;
        Albertosaurine caller = this.answerTo;
        this.answerTarget = null;
        this.answerTo = null;
        if (target == null || !target.isAlive() || caller == null || !caller.isAlive() || this.getTarget() != null
                || this.isSleeping() || this.isKnockedOut() || this.isInSittingPose()) {
            return;
        }
        this.getLookControl().setLookAt(caller, 30.0F, 30.0F);
        this.triggerAnim(ACTION_CONTROLLER, "answer");
        this.playSound(this.getAmbientSound(), 1.4F, 1.08F * this.getVoicePitch());
        if (this.isDriver()) {
            this.drivePrey = target;
            this.driveLeader = caller;
            this.driveSince = this.tickCount;
            this.logAct("answers the call: a juvenile, it drives the " + target.getType().toShortString());
        } else if (!this.isBaby() && this.spentLeft <= 0) {
            this.answering = true;
            try {
                this.setTarget(target);
            } finally {
                this.answering = false;
            }
            this.logAct("answers the call: joins the hunt");
        }
    }

    // ------------------------------------------------------------------ what the movement loop shows

    private void modeTick() {
        byte mode = MODE_NONE;
        if (this.spentLeft > 0) {
            mode = MODE_SPENT;
        } else if (this.mode() == MODE_AMBUSH || this.mode() == MODE_DRIVE) {
            return;                              // the goals set and clear those two
        } else if (this.chaseOf != null && this.isAggressive() && super.getTarget() != null
                && this.distanceToSqr(super.getTarget()) > 12.0D * 12.0D * this.getScale() * this.getScale()) {
            mode = MODE_SPRINT;
        }
        this.setMode(mode);
    }

    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        byte mode = this.mode();
        if (mode != MODE_NONE && !this.isVehicle() && !this.isSleeping() && !this.isInSittingPose() && !this.isSwimmingDeep()
                && !this.isKnockedOut() && !this.isDueling()) {
            boolean moving = state.isMoving();
            if (mode == MODE_AMBUSH && !moving) {
                if (this.ambushAnim == null) {
                    this.ambushAnim = RawAnimation.begin().thenLoop(anim("ambush_crouch"));
                }
                return state.setAndContinue(this.ambushAnim);
            }
            if (mode == MODE_DRIVE && moving) {
                if (this.driveAnim == null) {
                    this.driveAnim = RawAnimation.begin().thenLoop(anim("drive"));
                }
                this.cycleSpeed = this.gaitSpeed(this.runCycleSpeed());
                return state.setAndContinue(this.driveAnim);
            }
            if (mode == MODE_SPRINT && moving) {
                if (this.sprintAnim == null) {
                    this.sprintAnim = RawAnimation.begin().thenLoop(anim("sprint"));
                }
                this.cycleSpeed = this.gaitSpeed(SPRINT_PX / 16.0D / SPRINT_TICKS * this.modelScale());
                return state.setAndContinue(this.sprintAnim);
            }
            if (mode == MODE_SPENT) {
                if (this.spentWalkAnim == null) {
                    this.spentWalkAnim = RawAnimation.begin().thenLoop(anim("walk_tired"));
                    this.spentIdleAnim = RawAnimation.begin().thenLoop(anim("idle_tired"));
                }
                if (!moving) {
                    return state.setAndContinue(this.spentIdleAnim);
                }
                this.cycleSpeed = this.gaitSpeed(56.0D / 16.0D / 48.0D * this.modelScale());
                return state.setAndContinue(this.spentWalkAnim);
            }
        }
        return super.movementAnimation(state);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (this.spentLeft > 0) {
            tag.putInt("Spent", this.spentLeft);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.getInt("Spent") > 0) {
            this.spentLeft = tag.getInt("Spent");
            AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
            if (speed != null) {
                speed.removeModifier(SPENT_SLOW);
                speed.addTransientModifier(new AttributeModifier(SPENT_SLOW, "spent", -0.35D, AttributeModifier.Operation.MULTIPLY_TOTAL));
            }
        }
    }
}
