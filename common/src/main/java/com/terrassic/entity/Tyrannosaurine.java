package com.terrassic.entity;

import com.terrassic.entity.ai.CarcassStealGoal;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.animation.PlayState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The Daspletosaurus rig (tools/modelgen/handmade/daspletosaurus, made for it from its own study,
 * docs/estudos/13_PREDADORES_1_10.md; the pilot of the 1.10.1 visual standard). The life of an {@link ApexTheropod},
 * with what this tyrannosaurine does differently:
 * <ul>
 *   <li><b>The crushing bite</b>: its heavy bite holds and gives two short shakes ("attack"); at big prey it uses it
 *       more, at small things the low sweep, at the side the arcing bite.</li>
 *   <li><b>The face bite</b>: in a duel the most patient of the tyrannosaurids (it blocks a lot with the heavy skull
 *       and hardly dodges, ai/DuelStyle); its counter and its signature blow bite the rival's face ("parry",
 *       "face_bite": the bitten skulls of Tanke &amp; Currie 1998). It opens a duel showing its teeth ("jaw_test").</li>
 *   <li><b>The carcass thief</b> ({@link CarcassStealGoal}): hungry, it walks in on another predator's kill and roars
 *       at it ("steal_roar"); one under half its size leaves the carcass, an equal or a bigger one has to fight for
 *       it. Over a carcass it crouches with the head low ("carcass_guard") and growls at whoever comes near.</li>
 *   <li><b>Family</b>: a pair, and sometimes a juvenile at about 0.6 of the adult size with them (the bonebed of
 *       Currie et al. 2005; a hypothesis): the third of a natural group is born a juvenile, and mates never make
 *       each other give way.</li>
 *   <li><b>Its own gestures</b>: besides the lively set it rubs its face on the ground after eating ("face_rub").</li>
 * </ul>
 * It has the duel and the lively sets of the remade apex predators (hasDuelMoves, hasLivelySet) by its own class, so
 * the shared lists in DinosaurEntity stay untouched.
 */
public abstract class Tyrannosaurine extends ApexTheropod {
    /** One short line when a behaviour of its own fires ("[dasp] ..."), for the playtests in a generated world. */
    private static final Logger LOG = LoggerFactory.getLogger("terrassic");
    /** The cycles (daspleanims.py WALK, RUN, STALK): pixels of ground per cycle (stride x K = 0.72) and ticks. */
    private static final double WALK_PX = 50.4D;
    private static final double WALK_TICKS = 40.0D;
    private static final double RUN_PX = 83.5D;
    private static final double RUN_TICKS = 20.0D;
    private static final double STALK_PX = 35.3D;
    private static final double STALK_TICKS = 60.0D;
    /** The blows, timed to the jaws in daspleanims.py / dasplefight.py (tick the hit lands, ticks to the next). */
    private static final Strike CRUSH = new Strike("attack", 10, 40, false);
    private static final Strike SNAP = new Strike("attack_quick", 6, 18, false);
    private static final Strike LOW = new Strike("bite_low", 8, 24, false);
    private static final Strike SIDE = new Strike("bite_side", 9, 26, false);
    private static final Strike FACE_BITE = new Strike("face_bite", 11, 28, false);
    /** Big prey (blocks wide): the crushing bite more often (Russell 1970: the ceratopsian hunter). */
    private static final float BIG = 1.8F;
    /** The third of a natural group is a juvenile of about 0.6 of the adult size (growth 0.44 of a 0.28 hatchling). */
    private static final int JUVENILE_AGE = -13300;
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch", "snort", "snort",
            "settle", "settle", "scan", "scan"};
    private static final String[] OWN = {"steal_roar", "jaw_test", "face_rub", "face_bite", "carcass_guard"};
    /** Client: how close a carcass must be for the guard crouch (blocks past the two half widths). */
    private static final double GUARD_REACH = 2.0D;

    private RawAnimation guardCarcassAnim;
    /** Client: a carcass with meat at its jaws, looked up every ten ticks. */
    private boolean atCarcass;
    /** Server: ticks the steal goal or the carcass guard leave the next carcass act alone. */
    private int carcassActCooldown;
    /** Server: a carcass with meat in sight (looked up every second): it goes for that before it hunts. */
    private boolean carcassInSight;

    protected Tyrannosaurine(EntityType<? extends Tyrannosaurine> type, Level level) {
        super(type, level);
    }

    /** Logs one behaviour line: "[dasp] what (id, x y z)". */
    public void logAct(String what) {
        LOG.info("[dasp] {} (#{} {} {} {})", what, this.getId(), this.getBlockX(), this.getBlockY(), this.getBlockZ());
    }

    /** ai/DuelGoal: a duel move started; its own ones (the face bite, the parry that ends in one) are logged. */
    public static void duelMove(DinosaurEntity mob, String anim) {
        if (mob instanceof Tyrannosaurine t && ("face_bite".equals(anim) || "parry".equals(anim))) {
            t.logAct("parry".equals(anim) ? "face bite (parry counter)" : "face bite");
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

    /** Its bite tip, against the T. rex's the distances were measured on: a shorter head and neck on a smaller rig. */
    @Override
    public double reachScale() {
        return 0.78D;
    }

    // ------------------------------------------------------------------ blows and the duel

    @Override
    public Strike biteFor(LivingEntity target) {
        float r = this.getRandom().nextFloat();
        if (target.getBbWidth() >= BIG) {
            return r < 0.55F ? CRUSH : r < 0.8F ? SIDE : SNAP;
        }
        if (target.getBbHeight() < 1.4F && r < 0.45F) {
            return LOW;
        }
        return r < 0.35F ? SNAP : r < 0.65F ? CRUSH : r < 0.85F ? SIDE : SNAP;
    }

    /** After the crushing bite it steps back a little, the jaws still working. */
    @Override
    public Pause pauseAfter(Strike strike) {
        Pause alpha = super.pauseAfter(strike);
        if (alpha != null) {
            return alpha;
        }
        return strike == CRUSH ? new Pause(8, null, 0, 0) : null;
    }

    /** Chest to chest with a rival: it bites the face. */
    @Override
    public Strike closeStrike() {
        return FACE_BITE;
    }

    /** It opens a duel by showing its teeth, the jaws opened slowly. */
    @Override
    public String duelOpener() {
        return "jaw_test";
    }

    // ------------------------------------------------------------------ family

    /** It lives in a pair (and the juvenile with them): its mate keeps near and never makes it give way. */
    @Override
    protected boolean solitary() {
        return false;
    }

    @Override
    protected boolean givesWayTo(ApexTheropod rival) {
        return super.givesWayTo(rival) && rival.isFemale() == this.isFemale();
    }

    /** A natural group: the pair, and the third one a juvenile. The group data is ours from the first one on (the
     *  spawners pass it from one to the next), so ApexTheropod's own juveniles stay out of it. */
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        SpawnGroupData spawnData) {
        boolean natural = reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION;
        if (natural && spawnData == null) {
            spawnData = new Family();
        }
        if (spawnData instanceof Family family && family.getGroupSize() >= 2 && !this.isTame() && this.getAge() == 0) {
            this.setAge(JUVENILE_AGE);
            this.logAct("family: the juvenile of the pair");
        } else if (spawnData instanceof Family family) {
            this.logAct("family: " + (family.getGroupSize() == 0 ? "first of the pair" : "its mate"));
        }
        return super.finalizeSpawn(level, difficulty, reason, spawnData);
    }

    /** The group data of a natural family (no random babies: only the third is young). */
    public static final class Family extends AgeableMob.AgeableMobGroupData {
        public Family() {
            super(false);
        }
    }

    // ------------------------------------------------------------------ the carcass

    @Override
    protected void addExtraGoals() {
        super.addExtraGoals();
        this.goalSelector.addGoal(1, new CarcassStealGoal(this));
    }

    /** CarcassStealGoal: the roar at the rival on the carcass, the sound when the jaws open (0.85 s). */
    public void stealRoar(LivingEntity rival) {
        this.triggerAnim(ACTION_CONTROLLER, "steal_roar");
        this.getLookControl().setLookAt(rival, 30.0F, 30.0F);
    }

    public void stealRoarSound() {
        this.playSound(this.roarSound(), 3.0F, 0.9F * this.getVoicePitch());
    }

    /** A scavenger first (Hone &amp; Tanke 2015): with meat lying in sight it goes for the carcass (to eat it, or to
     *  take it from whoever holds it) instead of starting a hunt. */
    @Override
    protected boolean canHunt() {
        return super.canHunt() && !this.carcassInSight;
    }

    /** Over a carcass, a growl at a meat eater that comes too near; after eating, the face rubbed on the ground. */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if ((this.tickCount + this.getId()) % 20 == 5) {
            this.carcassInSight = !this.isTame() && !this.isSated() && !this.level().getEntitiesOfClass(CarcassEntity.class,
                    this.getBoundingBox().inflate(24.0D), CarcassEntity::hasMeat).isEmpty();
        }
        if (this.carcassActCooldown > 0) {
            this.carcassActCooldown--;
            return;
        }
        if ((this.tickCount + this.getId()) % 20 != 0 || this.isTame() || this.isBaby() || this.getTarget() != null
                || this.isRoaring() || !this.onGround()) {
            return;
        }
        CarcassEntity carcass = this.carcassAtJaws();
        if (carcass == null) {
            return;
        }
        double r = 10.0D * this.getScale();
        for (DinosaurEntity other : this.level().getEntitiesOfClass(DinosaurEntity.class, this.getBoundingBox().inflate(r),
                e -> e != this && e.isAlive() && !e.isBaby() && !(e instanceof Tyrannosaurine) && CarcassStealGoal.eatsMeat(e))) {
            this.getLookControl().setLookAt(other, 30.0F, 30.0F);
            this.triggerAnim(ACTION_CONTROLLER, "threat");
            this.logAct("carcass guard: growls at " + other.speciesId());
            this.playSound(this.roarSound(), 1.4F, 0.7F * this.getVoicePitch());
            this.carcassActCooldown = 160 + this.getRandom().nextInt(120);
            return;
        }
    }

    @Override
    public void onAteCarrion() {
        super.onAteCarrion();
        if (this.isSated() && this.getRandom().nextInt(2) == 0) {
            this.carcassActCooldown = 70;
            this.triggerAnim(ACTION_CONTROLLER, "face_rub");
            this.logAct("face rub after eating");
        }
    }

    /** The nearest carcass with meat right at its jaws, or null. */
    public CarcassEntity carcassAtJaws() {
        double reach = this.getBbWidth() * 0.5D + GUARD_REACH + 2.0D * this.getScale();
        CarcassEntity best = null;
        double bestD = Double.MAX_VALUE;
        for (CarcassEntity c : this.level().getEntitiesOfClass(CarcassEntity.class, this.getBoundingBox().inflate(reach + 2.0D),
                CarcassEntity::hasMeat)) {
            double d = Math.sqrt(this.distanceToSqr(c)) - c.getBbWidth() * 0.5D;
            if (d <= reach && d < bestD) {
                bestD = d;
                best = c;
            }
        }
        return best;
    }

    /** Standing at a carcass (not hunting, not resting): the crouch over it, head low. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (this.tickCount % 10 == 0) {
            this.atCarcass = !this.isBaby() && this.carcassAtJaws() != null;
        }
        if (this.atCarcass && !state.isMoving() && !this.isAggressive() && !this.isVehicle() && !this.isSleeping()
                && !this.isInSittingPose() && !this.isSwimmingDeep() && !this.isKnockedOut()) {
            if (this.guardCarcassAnim == null) {
                this.guardCarcassAnim = RawAnimation.begin().thenLoop(anim("carcass_guard"));
            }
            return state.setAndContinue(this.guardCarcassAnim);
        }
        return super.movementAnimation(state);
    }

    /** Whether this one can take a carcass from that one by the roar alone (it is under half its size). */
    public boolean frightens(LivingEntity rival) {
        return linearSize(rival) < 0.5D * linearSize(this);
    }

    /** The hitbox's linear size (the cube root of its volume): a 9 m tyrannosaur against a 3 m raptor reads ~0.35. */
    public static double linearSize(LivingEntity e) {
        return Math.cbrt(e.getBbWidth() * e.getBbWidth() * e.getBbHeight());
    }

    /** CarcassStealGoal: the carcass act just played; leave the next one alone for a while. */
    public void carcassActDone(int ticks) {
        this.carcassActCooldown = Math.max(this.carcassActCooldown, ticks);
    }

    /** Whether it is free to go after a carcass someone else holds (wild, grown, hungry, nothing else on). */
    public boolean wantsToSteal() {
        return !this.isTame() && !this.isBaby() && !this.isSated() && this.getHunger() < HUNTS_BELOW && this.getTarget() == null
                && !this.isVehicle() && !this.isSleeping() && !this.isInSittingPose() && !this.isKnockedOut()
                && this.getHealth() > this.getMaxHealth() * 0.5F && this.carcassActCooldown <= 0;
    }
}
