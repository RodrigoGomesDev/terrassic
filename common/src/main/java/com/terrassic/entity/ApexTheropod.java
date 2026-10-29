package com.terrassic.entity;

import com.terrassic.entity.ai.ApexBiteGoal;
import com.terrassic.entity.ai.DinosaurMoveControl;
import com.terrassic.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

/**
 * The big tyrant theropods with a full set of their own animations (the T. rex v2 rig,
 * tools/modelgen/handmade/tyrannosaurus/rexanims.py). On top of a {@link PredatorDinosaur}:
 * <ul>
 *   <li><b>The fight</b> ({@link ApexBiteGoal}): stops with the head over the target, bite timed to the jaws, quick
 *       and heavy bites, a stomp for small things.</li>
 *   <li><b>Roar</b> when it locks onto a player or big prey: it stands and roars, the sound when the jaws open.</li>
 *   <li><b>Loud roar</b> (roar_loud, head to the sky), rare: after killing big prey, at a rival of its species that
 *       comes near, and when a tame one goes to defend its owner. Only this one shakes the air: a burst of comic
 *       speed lines at the mouth (particle terrassic:roar_wave), dust off the ground and the camera shaking for
 *       players nearby (client option "roar_shake").</li>
 *   <li><b>Life</b>: idle gestures (sniff, look back, shake, yawn, stretch, drink by the water), a low call with its
 *       ambient voice, a threat at players who come close when it is not hunting, its own sleep, swim, stalk,
 *       flinch and death.</li>
 *   <li><b>Rivals and family</b>: a wild adult gives way to a bigger wild adult of its kind (who roars at it); now and
 *       then an adult comes with one or two juveniles.</li>
 * </ul>
 */
public abstract class ApexTheropod extends PredatorDinosaur {
    /** Mouth of the loud roar's pose (blocks at model scale 1, forward of the centre and above the feet). */
    private static final double LOUD_MOUTH_FORWARD = 4.5D;
    private static final double LOUD_MOUTH_UP = 6.0D;
    /** The loud roar: length, when the sound starts, the three waves (tick, strength) and the dust. */
    private static final int LOUD_TICKS = 88;
    private static final int LOUD_SOUND = 22;
    private static final int[][] LOUD_WAVES = {{24, 100}, {38, 75}, {52, 75}};
    private static final int ROAR_TICKS = 68;
    private static final int ROAR_SOUND = 16;
    /** Share of wild adults that come with juveniles. */
    private static final float FAMILY_CHANCE = 0.18F;
    private static final String[] GESTURES = {"sniff", "look_back", "shake", "yawn", "stretch"};

    /** Ticks left of the roar under way (normal or loud) and how far into it we are. */
    private int roarLeft;
    private int roarAge;
    private boolean loudRoar;
    private int roarCooldown;
    private int loudCooldown = 600;
    private int pendingLoud;
    private int gestureCooldown = 200;
    private int threatCooldown;
    /** Ticks it still counts as wet after deep water (then it shakes itself). */
    private int soaked;
    /** What the roar under way is aimed at (the body turns to it). */
    private LivingEntity roarFacing;
    /** Entity id of what it last roared at (so it charges instead of stalking). */
    private int roaredAt = -1;
    private RawAnimation stalkAnim;

    protected ApexTheropod(EntityType<? extends ApexTheropod> type, Level level) {
        super(type, level);
        this.moveControl = new DinosaurMoveControl(this, true);   // pivots: no circling round a waypoint
    }

    /** Renderer scale of the model (MODEL_SCALE of the species class). */
    protected abstract float modelScale();

    /** The roar (its threat voice). */
    protected abstract SoundEvent roarSound();

    @Override
    protected String[] extraActions() {
        return new String[]{"roar", "roar_loud", "attack_quick", "stomp", "call", "threat", "drink",
                "sniff", "look_back", "shake", "yawn", "stretch"};
    }

    // ------------------------------------------------------------------ the rig's animations

    @Override
    protected double walkCycleSpeed() {
        return 72.0D / 16.0D / 38.0D * this.modelScale();      // 72 px per 1.9 s cycle
    }

    @Override
    protected double runCycleSpeed() {
        return 128.0D / 16.0D / 16.0D * this.modelScale();     // 128 px per 0.8 s cycle
    }

    private double stalkCycleSpeed() {
        return 56.0D / 16.0D / 56.0D * this.modelScale();      // 56 px per 2.8 s cycle
    }

    @Override
    protected int deathAnimTicks() {
        return 60;
    }

    @Override
    protected boolean hasSleepAnim() {
        return true;
    }

    @Override
    protected boolean hasSwimAnim() {
        return true;
    }

    @Override
    protected boolean flinches() {
        return true;
    }

    @Override
    protected boolean animatesHits() {
        return false;
    }

    /** Creeping up on prey (aggressive but slow): the stalk cycle. */
    @Override
    protected PlayState movementAnimation(AnimationState<DinosaurEntity> state) {
        if (state.isMoving() && this.isAggressive() && !this.isVehicle() && !this.isSleeping() && !this.isSwimmingDeep()) {
            double dx = this.getX() - this.xo;
            double dz = this.getZ() - this.zo;
            if (dx * dx + dz * dz < 0.0081D * this.getScale() * this.getScale()) {
                if (this.stalkAnim == null) {
                    this.stalkAnim = RawAnimation.begin().thenLoop(anim("stalk"));
                }
                PlayState play = state.setAndContinue(this.stalkAnim);
                this.cycleSpeed = this.gaitSpeed(this.stalkCycleSpeed());
                return play;
            }
        }
        return super.movementAnimation(state);
    }

    // ------------------------------------------------------------------ goals

    /** Solitary: adults keep no herd (a family is the juveniles following their parent). */
    @Override
    protected boolean solitary() {
        return true;
    }

    // ------------------------------------------------------------------ water

    /** It floats chest-deep, the back and head out, instead of bobbing on top of the water. */
    @Override
    public double getFluidJumpThreshold() {
        return this.getBbHeight() * 0.5D;
    }

    /** The legs paddle: it swims at a walk (about 2 blocks a second) rather than drifting. */
    @Override
    public void travel(Vec3 input) {
        if (this.isControlledByLocalInstance() && this.isInWater() && !this.onGround() && input.z > 0.0D) {
            float yaw = this.getYRot() * Mth.DEG_TO_RAD;
            this.setDeltaMovement(this.getDeltaMovement().add(-Mth.sin(yaw) * 0.018D, 0.0D, Mth.cos(yaw) * 0.018D));
        }
        super.travel(input);
    }

    @Override
    protected Goal createAttackGoal() {
        return new ApexBiteGoal(this, this.attackSpeed());
    }

    @Override
    protected void addExtraGoals() {
        super.addExtraGoals();
        // a wild adult gives way to a bigger wild adult of its kind
        this.goalSelector.addGoal(4, new AvoidEntityGoal<>(this, ApexTheropod.class, 20.0F, 0.9D, 1.1D,
                e -> e instanceof ApexTheropod rival && this.givesWayTo(rival)));
    }

    private boolean givesWayTo(ApexTheropod rival) {
        return rival != this && rival.getClass() == this.getClass() && !this.isTame() && !rival.isTame()
                && !this.isBaby() && !rival.isBaby() && this.getTarget() == null
                && rival.getAdultSize() > this.getAdultSize() + 0.005F;
    }

    // ------------------------------------------------------------------ roars

    public boolean isRoaring() {
        return this.roarLeft > 0;
    }

    /** Whether it roared at this target (then it charges rather than stalks). */
    public boolean hasRoaredAt(LivingEntity target) {
        return target != null && target.getId() == this.roaredAt;
    }

    /** The roar when it locks onto a target: it stands for it; the sound comes as the jaws open. */
    public void roar() {
        if (this.isRoaring() || this.level().isClientSide()) {
            return;
        }
        this.startRoar(false);
    }

    /** The loud roar, head to the sky, with the wave in the air. */
    public void roarLoud() {
        if (this.isRoaring() || this.level().isClientSide()) {
            return;
        }
        this.loudCooldown = 900 + this.random.nextInt(600);
        this.startRoar(true);
    }

    private void startRoar(boolean loud) {
        this.loudRoar = loud;
        this.roarLeft = loud ? LOUD_TICKS : ROAR_TICKS;
        this.roarAge = 0;
        this.getNavigation().stop();
        triggerAnim(ACTION_CONTROLLER, loud ? "roar_loud" : "roar");
    }

    private void roarTick(ServerLevel level) {
        this.roarAge++;
        this.roarLeft--;
        if (this.roarAge == (this.loudRoar ? LOUD_SOUND : ROAR_SOUND)) {
            this.playSound(this.roarSound(), this.loudRoar ? 5.0F : 3.0F, (this.loudRoar ? 0.85F : 1.0F) * this.getVoicePitch());
        }
        if (!this.loudRoar) {
            return;
        }
        for (int[] wave : LOUD_WAVES) {
            if (this.roarAge == wave[0]) {
                this.airWave(level, wave[1] / 100.0F);
            }
        }
        if (this.roarAge >= LOUD_WAVES[0][0] && this.roarAge <= 60 && this.roarAge % 6 == 0) {
            this.dust(level);
        }
    }

    /** One wave of the loud roar: sent to every player within 96 blocks (it is big; far away it is just a speck). */
    private void airWave(ServerLevel level, float strength) {
        double k = this.modelScale() * this.getScale();
        float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
        double x = this.getX() - Mth.sin(yaw) * LOUD_MOUTH_FORWARD * k;
        double y = this.getY() + LOUD_MOUTH_UP * k;
        double z = this.getZ() + Mth.cos(yaw) * LOUD_MOUTH_FORWARD * k;
        // count 0: the "speed" values reach the particle as its velocity; x carries the wave's size and strength
        for (ServerPlayer player : level.players()) {
            if (player.distanceToSqr(x, y, z) < 96.0D * 96.0D) {
                level.sendParticles(player, ModParticles.ROAR_WAVE.get(), true, x, y, z, 0, strength * k, 0.0D, 0.0D, 1.0D);
            }
        }
    }

    /** Dust kicked off the ground around the feet. */
    private void dust(ServerLevel level) {
        BlockPos below = this.getBlockPosBelowThatAffectsMyMovement();
        BlockState ground = level.getBlockState(below);
        if (ground.isAir()) {
            return;
        }
        double r = this.getBbWidth() * 1.2D;
        for (int i = 0; i < 10; i++) {
            double a = this.random.nextDouble() * Math.PI * 2.0D;
            double d = r * (0.6D + this.random.nextDouble() * 0.8D);
            level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), this.getX() + Math.cos(a) * d,
                    this.getY() + 0.1D, this.getZ() + Math.sin(a) * d, 2, 0.2D, 0.05D, 0.2D, 0.15D);
        }
    }

    @Override
    public void setTarget(LivingEntity target) {
        LivingEntity previous = this.getTarget();
        super.setTarget(target);
        if (this.level().isClientSide() || target == null || previous != null || this.isVehicle() || !this.isAlive()) {
            return;
        }
        if (this.isTame()) {
            // going to defend its owner: the loud roar, now and then
            if (this.loudCooldown <= 0 && !this.isBaby()) {
                this.roarLoud();
                this.roaredAt = target.getId();
            }
        } else if (this.roarCooldown <= 0 && (target instanceof Player || target.getBbWidth() >= 1.2F)) {
            this.roarCooldown = 400;
            this.roar();
            this.roarFacing = target;
            this.roaredAt = target.getId();
        }
    }

    /** Big prey brought down: the loud roar over it. */
    @Override
    public boolean killedEntity(ServerLevel level, LivingEntity killed) {
        boolean result = super.killedEntity(level, killed);
        if (!this.isBaby() && (killed.getBbWidth() >= 1.5F || killed.getMaxHealth() >= 60.0F) && this.loudCooldown <= 200) {
            this.pendingLoud = 30;
        }
        return result;
    }

    // ------------------------------------------------------------------ the day

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        ServerLevel level = (ServerLevel) this.level();
        if (this.roarLeft > 0) {
            this.roarTick(level);
            // it stands for the whole roar (no walking on to a carcass), body turned to what it roars at
            this.getNavigation().stop();
            if (this.roarFacing != null && this.roarFacing.isAlive()) {
                double dx = this.roarFacing.getX() - this.getX();
                double dz = this.roarFacing.getZ() - this.getZ();
                float yaw = Mth.approachDegrees(this.getYRot(), (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F, 4.0F);
                this.setYRot(yaw);
                this.setYBodyRot(yaw);
                this.getLookControl().setLookAt(this.roarFacing, 30.0F, 30.0F);
            }
        } else {
            this.roarFacing = null;
        }
        if (this.roarCooldown > 0) {
            this.roarCooldown--;
        }
        if (this.loudCooldown > 0) {
            this.loudCooldown--;
        }
        if (this.threatCooldown > 0) {
            this.threatCooldown--;
        }
        if (this.pendingLoud > 0 && --this.pendingLoud == 0) {
            this.roarLoud();
        }
        // out of deep water and back on its feet: it shakes the water off (within ten seconds, once it is calm)
        if (this.isInWater()) {
            if (this.getFluidHeight(FluidTags.WATER) > this.getBbHeight() * 0.3D) {
                this.soaked = 200;
            }
        } else if (this.soaked > 0) {
            this.soaked--;
            if (this.onGround() && this.getTarget() == null && !this.isVehicle() && !this.isRoaring()) {
                triggerAnim(ACTION_CONTROLLER, "shake");
                this.soaked = 0;
                this.gestureCooldown = Math.max(this.gestureCooldown, 100);
            }
        }
        // afloat chest-deep its feet are more than a block under the path's nodes (laid on the water surface), so vanilla
        // never counts one as reached and it paddled round the first: here a node counts when it is over it
        Path path = this.getNavigation().getPath();
        // a fresh path starts at the block it stands on; on a stair or a slab edge that block can be behind it, and
        // going back to it (a pivot, a step up, a pivot, the step down) it rocked on the bottom step (rc3c stairs
        // test): a first node it is already past is skipped, as vanilla does for small mobs within 2 blocks
        if (path != null && !path.isDone() && path.getNextNodeIndex() == 0 && path.getNodeCount() > 1) {
            Vec3 first = path.getEntityPosAtNode(this, 0);
            Vec3 second = path.getEntityPosAtNode(this, 1);
            if (Mth.square(second.x - this.getX()) + Mth.square(second.z - this.getZ())
                    < Mth.square(second.x - first.x) + Mth.square(second.z - first.z)) {
                path.advance();
            }
        }
        if (path != null && !path.isDone() && this.isInWater() && !this.onGround()) {
            Vec3 node = path.getNextEntityPos(this);
            double r = this.getBbWidth() / 2.0D + 0.5D;
            if (Mth.square(node.x - this.getX()) + Mth.square(node.z - this.getZ()) < r * r) {
                path.advance();
            }
        }
        if ((this.tickCount + this.getId()) % 40 == 0) {
            this.rivalTick(level);
            this.threatTick(level);
        }
        if (this.calm() && --this.gestureCooldown <= 0) {
            this.gestureCooldown = 300 + this.random.nextInt(500);
            this.gesture(level);
        }
    }

    /** Up and about with nothing to do: standing, awake, wild or tame, no rider. */
    private boolean calm() {
        return this.isAlive() && !this.isRoaring() && this.getTarget() == null && !this.isAggressive() && !this.isSleeping()
                && !this.isKnockedOut() && !this.isInSittingPose() && !this.isVehicle() && !this.isPassenger()
                && this.onGround() && !this.isInWater() && this.getNavigation().isDone()
                && this.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4D;
    }

    private void gesture(ServerLevel level) {
        if (this.waterAhead(level)) {
            triggerAnim(ACTION_CONTROLLER, "drink");
            return;
        }
        String g = GESTURES[this.random.nextInt(GESTURES.length)];
        if (!level.isDay() && this.random.nextInt(3) == 0) {
            g = "yawn";
        }
        triggerAnim(ACTION_CONTROLLER, g);
    }

    /** Water at its feet a few steps in front of it (the snout reaches down to drink). */
    private boolean waterAhead(ServerLevel level) {
        float yaw = this.yBodyRot * Mth.DEG_TO_RAD;
        double k = this.modelScale() * this.getScale();
        for (double d = 3.0D; d <= 5.5D; d += 1.25D) {
            BlockPos at = BlockPos.containing(this.getX() - Mth.sin(yaw) * d * k, this.getY() - 0.5D, this.getZ() + Mth.cos(yaw) * d * k);
            if (level.getFluidState(at).is(FluidTags.WATER) || level.getFluidState(at.below()).is(FluidTags.WATER)) {
                return true;
            }
        }
        return false;
    }

    /** A bigger wild adult of its kind close by: the bigger one roars loud at it (the smaller gives way, see goals). */
    private void rivalTick(ServerLevel level) {
        if (this.isTame() || this.isBaby() || this.getTarget() != null || this.isSleeping() || this.isRoaring()
                || (this.loudCooldown > 0 && this.roarCooldown > 0)) {
            return;
        }
        for (ApexTheropod other : level.getEntitiesOfClass(this.getClass(), this.getBoundingBox().inflate(24.0D),
                e -> e != this && e.isAlive() && !e.isTame() && !e.isBaby())) {
            if (other.givesWayTo(this)) {
                // the loud one when it has it in it, else the plain roar (the smaller one is gone before long)
                if (this.loudCooldown <= 0) {
                    this.roarLoud();
                } else {
                    this.roarCooldown = 400;
                    this.roar();
                }
                this.roarFacing = other;
                return;
            }
        }
    }

    /** Not hunting (full, or tame) but a player walks up close: it lowers the head and growls first. */
    private void threatTick(ServerLevel level) {
        if (this.threatCooldown > 0 || this.isTame() || this.isBaby() || this.canHunt() || !this.calm()) {
            return;
        }
        Player near = level.getNearestPlayer(this, 8.0D * this.getScale());
        if (near != null && !near.isCreative() && !near.isSpectator()) {
            this.threatCooldown = 300 + this.random.nextInt(200);
            this.getLookControl().setLookAt(near, 30.0F, 30.0F);
            triggerAnim(ACTION_CONTROLLER, "threat");
            this.playSound(this.roarSound(), 1.6F, 0.75F * this.getVoicePitch());
        }
    }

    /** Its low call goes with the ambient voice now and then. */
    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!this.level().isClientSide() && this.calm() && !this.isBaby() && this.random.nextInt(5) < 2) {
            triggerAnim(ACTION_CONTROLLER, "call");
        }
    }

    // ------------------------------------------------------------------ family

    /** Now and then a wild adult comes with one or two juveniles of different ages. */
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        SpawnGroupData spawnData, CompoundTag tag) {
        SpawnGroupData data = super.finalizeSpawn(level, difficulty, reason, spawnData, tag);
        if ((reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) && spawnData == null && !this.isBaby()
                && !this.isTame() && !this.isRift() && this.random.nextFloat() < FAMILY_CHANCE) {
            int young = 1 + this.random.nextInt(2);
            for (int i = 0; i < young; i++) {
                if (!(this.getType().create(level.getLevel()) instanceof ApexTheropod juvenile)) {
                    break;
                }
                double a = this.random.nextDouble() * Math.PI * 2.0D;
                juvenile.setRoamer(this.isRoamer());
                juvenile.moveTo(this.getX() + Math.cos(a) * 3.0D, this.getY(), this.getZ() + Math.sin(a) * 3.0D,
                        this.random.nextFloat() * 360.0F, 0.0F);
                if (!level.noCollision(juvenile)) {
                    juvenile.moveTo(this.getX(), this.getY(), this.getZ());
                }
                juvenile.setAge(-8000 - this.random.nextInt(14000));   // a juvenile before finalizeSpawn: no nest of its own
                juvenile.finalizeSpawn(level, difficulty, reason, new AgeableMob.AgeableMobGroupData(false), null);
                level.addFreshEntity(juvenile);
            }
        }
        return data;
    }
}
